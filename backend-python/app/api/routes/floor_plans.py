"""
Floor plan generation route — Phase 6C.3 Demo Reliability & AI Fallback.
Updated for Phase 6C.5: metrics, validation results, front_side enrichment.

Returns structured, safe error responses. Never exposes raw provider
exceptions, API keys, or internal stack traces to the frontend.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from supabase import Client
from app.core.config import settings
from app.core.security import get_current_user, get_user_supabase_client
from app.services import project_service
from app.services.floorplan_service import FloorplanService
from app.services.ai.provider_factory import generate_with_fallback
from app.services.metrics import compute_floor_metrics
from app.validators.geometry_validator import GeometryValidator, GeometryValidationError
from pydantic import BaseModel
from typing import Optional
import time
import logging

logger = logging.getLogger("api.floor_plans")

router = APIRouter(prefix="/api/v1/projects/{project_id}/floor-plans", tags=["floor-plans"])


class GenerateRequest(BaseModel):
    optimization_priority: str = "balanced"


class GenerateResponse(BaseModel):
    generation_id: str
    status: str  # "completed" | "fallback_saved" | "failed"
    floor_plan_id: Optional[str] = None
    layout_data: Optional[dict] = None
    validation: dict
    metrics: Optional[dict] = None
    message: Optional[str] = None
    planner_source: Optional[str] = None


# ── Simple in-memory rate limiter ──────────────────────────────────────────────
rate_limits = {}


def check_rate_limit(user_id: str):
    now = time.time()
    user_requests = rate_limits.get(user_id, [])
    user_requests = [t for t in user_requests if now - t < 60]

    if len(user_requests) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in a minute."
        )

    user_requests.append(now)
    rate_limits[user_id] = user_requests


# ── Main generation endpoint ──────────────────────────────────────────────────
@router.post("/generate", response_model=GenerateResponse)
async def generate_floor_plan(
    project_id: str,
    request: GenerateRequest = None,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    check_rate_limit(user_id)
    logger.info("PHASE_6C8A_CURRENT_BACKEND_EXECUTED")
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    context = await project_service.get_planning_context(project_id, supabase)

    job_id = await FloorplanService.create_generation_job(
        supabase, project_id, user_id,
        settings.AI_PRIMARY_PROVIDER,
        "auto",
        context
    )

    max_validation_attempts = 3
    feedback = None
    layout_data = None
    valid = False
    errors = []
    provider_used = "unknown"
    validation_results = {}

    overall_start = time.time()
    OVERALL_TIMEOUT = 120.0  # 2 minutes max for the entire generation flow

    # ── Generation + validation loop ──────────────────────────────────────
    for attempt in range(max_validation_attempts):
        elapsed = time.time() - overall_start
        if elapsed > OVERALL_TIMEOUT:
            logger.warning(
                "Generation timed out after %.1fs  |  project=%s  attempts=%d",
                elapsed, project_id, attempt
            )
            errors.append("Generation timed out.")
            break

        errors = []
        try:
            t0 = time.time()
            from app.services.planning.engine import solve_layout
            from app.services.planning.post_processor import post_process_layout

            # Fetch requirements from the database
            req_res = supabase.table("project_requirements").select("*").eq("project_id", project_id).execute()

            # Use the hybrid engine: Gemini first, deterministic fallback
            # use_gemini=True by default; will skip Gemini if API key not set
            engine_res = solve_layout(context, req_res.data, use_gemini=True)
            provider_used = engine_res.get("planner_source", "deterministic")

            # Check if Gemini returned a pre-built LayoutData
            if engine_res.get("status") == "GEMINI_HYBRID" and "layout_data" in engine_res:
                # Gemini hybrid path: layout_data is already a LayoutData instance
                layout_data = engine_res["layout_data"]
                logger.info("[GEMINI_HYBRID] Using Gemini-planned layout directly")
            else:
                # Deterministic path: needs post-processing
                logger.info("[DETERMINISTIC] Using OR-Tools planner, running post-processor...")

                # --- DIAGNOSTIC STAGE 1: After OR-Tools solve ---
                fl_cnt = len(engine_res["floors"])
                logger.info(f"[DIAGNOSTIC 1] OR-Tools solve complete: {fl_cnt} floor(s)")
                total_indoor_area = 0.0
                for fl_lvl, r_list in engine_res["floors"].items():
                    indoor_r = [r for r in r_list if r["type"] not in ["garden", "yard", "terrace", "balcony"]]
                    fl_area = sum(r["area"] for r in indoor_r)
                    total_indoor_area += fl_area
                    r_desc = ", ".join([f"{r['type']}({r['x']},{r['y']}:{r['width']}x{r['length']})" for r in indoor_r])
                    logger.info(f"[DIAGNOSTIC 1] Floor {fl_lvl}: {len(indoor_r)} indoor room(s), area={fl_area} sq ft: {r_desc}")
                logger.info(f"[DIAGNOSTIC 1] Total indoor area: {total_indoor_area} sq ft")

                layout_data = post_process_layout(engine_res)

                # --- DIAGNOSTIC STAGE 2: After post_processor ---
                tot_indoor = 0
                tot_outdoor = 0
                for fl in layout_data.floors:
                    ind = sum(1 for r in fl.rooms if r.space_category != "outdoor" and r.type not in ["garden", "yard", "terrace"])
                    outd = sum(1 for r in fl.rooms if r.space_category == "outdoor" or r.type in ["garden", "yard", "terrace"])
                    outd += len(getattr(fl, "outdoor_areas", []))
                    tot_indoor += ind
                    tot_outdoor += outd
                fp = layout_data.plot.building_footprint or {}
                fp_area = fp.get("width", 0) * fp.get("length", 0)
                logger.info(f"[DIAGNOSTIC 2] Post-processor complete: indoor={tot_indoor}, outdoor={tot_outdoor}, footprint={fp.get('width')}x{fp.get('length')} ({fp_area} sq ft)")
                
            gen_elapsed = time.time() - t0
            logger.info(
                "Provider '%s' returned layout in %.2fs  |  project=%s  attempt=%d",
                provider_used, gen_elapsed, project_id, attempt + 1
            )

            # ── Enrich layout with front_side from context ────────────
            if layout_data and layout_data.plot:
                layout_data.plot.front_side = (context.get("facing") or "south").lower()

            t1 = time.time()
            _passed, validation_results = GeometryValidator.validate_layout(layout_data)
            val_elapsed = time.time() - t1
            logger.info(
                "Validation passed in %.2fs  |  project=%s",
                val_elapsed, project_id
            )

            valid = True
            break

        except GeometryValidationError as gve:
            # Layout generated but failed quality checks — retry with feedback
            errors.append(f"Geometry Error: {gve}")
            feedback = str(gve)
            logger.info(
                "Geometry validation failed — retrying with feedback  |  %s",
                gve
            )

        except RuntimeError as re:
            # Provider-level failure (all providers exhausted)
            err_str = str(re)
            errors.append(f"Provider Error: {err_str}")
            logger.warning(
                "Provider runtime error  |  project=%s  |  %s",
                project_id, type(re).__name__
            )
            break  # Don't retry provider failures in the validation loop

        except ValueError as ve:
            # Invalid JSON / Pydantic failures
            errors.append(f"AI Output Error: {ve}")
            feedback = str(ve)
            logger.info(
                "Value error — retrying with feedback  |  %s",
                type(ve).__name__
            )

        except Exception as e:
            if type(e).__name__ == "PlannerException":
                err_msg = str(e)
                logger.warning(f"PlannerException: {err_msg}")
                await FloorplanService.update_generation_job(
                    supabase, job_id, "Failed", error_message=err_msg
                )
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content={
                        "code": "NO_VALID_LAYOUT_FOUND",
                        "message": err_msg or "The selected requirements cannot be arranged within this plot using the current constraints.",
                        "suggestions": [
                            "Reduce bedroom count",
                            "Reduce parking requirement",
                            "Increase number of floors",
                            "Increase plot dimensions"
                        ],
                        "generation_id": job_id
                    }
                )
            
            errors.append(f"Unexpected Error: {type(e).__name__}")
            logger.error(
                "Unexpected error  |  project=%s  |  %s: %s",
                project_id, type(e).__name__, e
            )
            break

    total_elapsed = time.time() - overall_start

    # ── SUCCESS: compute metrics, save and return ─────────────────────────
    if valid and layout_data:
        # Compute metrics and attach to layout before saving
        try:
            metrics = compute_floor_metrics(layout_data)
            if "engine_res" in locals() and isinstance(engine_res, dict) and "quality_score" in engine_res:
                metrics["architectural_quality"] = engine_res["quality_score"]
            layout_data.metrics = metrics
        except Exception as me:
            logger.warning("Metrics computation failed: %s", me)
            metrics = {}

        # Attach validation results
        layout_data.validation_results = validation_results

        # --- DIAGNOSTIC STAGE 3: Before Supabase save ---
        fl_summary = []
        for fl in layout_data.floors:
            indoor_names = [r.type for r in fl.rooms if r.space_category != "outdoor" and r.type not in ["garden", "yard", "terrace"]]
            outdoor_names = [r.type for r in fl.rooms if r.space_category == "outdoor" or r.type in ["garden", "yard", "terrace"]]
            fl_summary.append(f"Floor {fl.level}: indoor={len(indoor_names)} ({', '.join(indoor_names)}), outdoor={len(outdoor_names)} ({', '.join(outdoor_names)})")
        logger.info(f"[DIAGNOSTIC 3] Before Supabase save: {len(layout_data.floors)} floor(s) | {' | '.join(fl_summary)}")
        logger.info(f"[DIAGNOSTIC 3] Building footprint: {layout_data.plot.building_footprint}")

        # Requirement preservation assertion: ensure indoor rooms are not lost
        total_indoor_rooms = sum(
            sum(1 for r in fl.rooms if r.space_category != "outdoor" and r.type not in ["garden", "yard", "terrace"])
            for fl in layout_data.floors
        )
        if total_indoor_rooms < 2:
            raise ValueError(f"Requirement preservation check failed: only {total_indoor_rooms} indoor rooms present. Aborting save.")

        floor_plan_id = await FloorplanService.save_floor_plan(
            supabase, project_id, user_id, job_id, layout_data
        )
        await FloorplanService.update_generation_job(
            supabase, job_id, "Completed", layout_data.model_dump()
        )
        logger.info(
            "Generation completed  |  project=%s  provider=%s  elapsed=%.2fs",
            project_id, provider_used, total_elapsed
        )

        return GenerateResponse(
            generation_id=job_id,
            status="completed",
            floor_plan_id=floor_plan_id,
            layout_data=layout_data.model_dump(),
            validation={"valid": True, "errors": [], **validation_results},
            metrics=metrics
        )

    # ── FAILURE: try saved-plan fallback ──────────────────────────────────
    logger.warning(
        "All generation attempts failed  |  project=%s  elapsed=%.2fs  errors=%s",
        project_id, total_elapsed, errors
    )
    await FloorplanService.update_generation_job(
        supabase, job_id, "Failed", error_message=" | ".join(errors)
    )

    # Check for the most recent valid saved plan
    saved_plan = await FloorplanService.get_latest_successful(supabase, project_id)

    if saved_plan:
        logger.info(
            "Returning saved fallback plan  |  project=%s  plan_id=%s",
            project_id, saved_plan["id"]
        )
        return GenerateResponse(
            generation_id=job_id,
            status="fallback_saved",
            floor_plan_id=saved_plan["id"],
            layout_data=saved_plan["layout_data"],
            validation={"valid": True, "errors": []},
            message="Live generation couldn't complete. Showing your most recent saved plan."
        )

    # ── No saved plan — return structured safe error ─────────────────────
    logger.warning(
        "No saved plan fallback available  |  project=%s",
        project_id
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "code": "AI_TEMPORARILY_UNAVAILABLE",
            "message": "Floor plan generation couldn't complete right now. Your project details are safe. Please retry in a moment.",
            "retryable": True,
            "generation_id": job_id
        }
    )
