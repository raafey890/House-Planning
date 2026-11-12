from supabase import Client
from app.models.layout import LayoutData
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("services.floorplan")


class FloorplanService:
    @staticmethod
    async def create_generation_job(supabase: Client, project_id: str, user_id: str, provider: str, model: str, context: dict) -> str:
        payload = {
            "project_id": project_id,
            "user_id": user_id,
            "generation_type": "floor_plan",
            "provider": provider,
            "model_used": model,
            "prompt_payload": context,
            "status": "Processing"
        }
        
        res = supabase.table("ai_generations").insert(payload).execute()
        return res.data[0]["id"]

    @staticmethod
    async def update_generation_job(supabase: Client, job_id: str, status: str, response_payload: dict = None, error_message: str = None):
        payload = {"status": status}
        if response_payload is not None:
            payload["response_payload"] = response_payload
        if error_message is not None:
            payload["error_message"] = str(error_message)
            
        supabase.table("ai_generations").update(payload).eq("id", job_id).execute()

    @staticmethod
    async def save_floor_plan(
        supabase: Client,
        project_id: str,
        user_id: str,
        job_id: str,
        layout: LayoutData,
        requirements_fingerprint: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save a generated floor plan with its requirements fingerprint.

        The fingerprint is stored in the ``requirements_fingerprint`` column
        so that future fallback lookups can verify that a saved plan matches
        the user's current requirements.
        """
        payload = {
            "project_id": project_id,
            "user_id": user_id,
            "version_name": "AI Generated Option 1",
            "layout_data": layout.model_dump(),
            "ai_generation_id": job_id,
        }
        if requirements_fingerprint is not None:
            payload["requirements_fingerprint"] = requirements_fingerprint

        res = supabase.table("floor_plans").insert(payload).execute()
        return res.data[0]["id"]

    @staticmethod
    async def get_latest_successful(
        supabase: Client,
        project_id: str,
        current_fingerprint: Optional[Dict[str, Any]] = None,
    ) -> Optional[dict]:
        """Fetch the most recent valid floor plan for a project.

        When *current_fingerprint* is provided the method checks whether
        the saved plan was generated from the same requirements.  If they
        don't match a warning is logged and ``None`` is returned so the
        caller does **not** silently serve an outdated plan.
        """
        try:
            res = supabase.table("floor_plans") \
                .select("id, layout_data, created_at, version_name, requirements_fingerprint") \
                .eq("project_id", project_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            
            if not res.data or len(res.data) == 0:
                return None

            saved = res.data[0]

            # ── Fingerprint comparison ────────────────────────────────
            if current_fingerprint is not None:
                saved_fp = saved.get("requirements_fingerprint")

                # Handle potential JSON string deserialization
                if isinstance(saved_fp, str):
                    try:
                        saved_fp = json.loads(saved_fp)
                    except Exception:
                        logger.warning(
                            "Malformed requirements_fingerprint JSON string in plan %s — skipping fallback",
                            saved.get("id")
                        )
                        return None

                if isinstance(saved_fp, dict):
                    from app.validators.requirements_validator import fingerprints_match
                    if not fingerprints_match(current_fingerprint, saved_fp):
                        logger.warning(
                            "Saved plan for project %s has different requirements "
                            "(saved=%s, current=%s) — skipping fallback",
                            project_id, saved_fp, current_fingerprint,
                        )
                        return None
                elif saved_fp is None:
                    # Legacy plan without stored fingerprint.
                    # Inspect layout_data to verify dimensional and floor count compatibility.
                    ld = saved.get("layout_data") or {}
                    plot_dict = ld.get("plot") or {}
                    legacy_w = plot_dict.get("width")
                    legacy_l = plot_dict.get("length")
                    legacy_floors = len(ld.get("floors") or [])

                    curr_w = current_fingerprint.get("plot_width")
                    curr_l = current_fingerprint.get("plot_length")
                    curr_floors = current_fingerprint.get("floors", 1)

                    is_dim_match = (
                        legacy_w is not None and curr_w is not None and abs(float(legacy_w) - float(curr_w)) < 1.0 and
                        legacy_l is not None and curr_l is not None and abs(float(legacy_l) - float(curr_l)) < 1.0 and
                        legacy_floors == int(curr_floors)
                    )

                    if not is_dim_match:
                        logger.warning(
                            "Legacy saved plan for project %s has incompatible geometry "
                            "(saved: %sx%s, %d floor(s); requested: %sx%s, %d floor(s)) — skipping fallback",
                            project_id, legacy_w, legacy_l, legacy_floors, curr_w, curr_l, curr_floors
                        )
                        return None

                    logger.info(
                        "Legacy saved plan for project %s matches plot dimensions (%sx%s, %d floor(s)) — allowing fallback",
                        project_id, curr_w, curr_l, curr_floors
                    )
                else:
                    # Malformed fingerprint type (not dict and not None)
                    logger.warning(
                        "Unrecognized requirements_fingerprint type (%s) in plan %s — skipping fallback",
                        type(saved_fp).__name__, saved.get("id")
                    )
                    return None

            logger.info("Found valid saved fallback plan for project %s", project_id)
            return saved

        except Exception as e:
            logger.warning("Error fetching saved plan fallback: %s", type(e).__name__)
            return None
