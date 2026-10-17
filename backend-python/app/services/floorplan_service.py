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
    async def save_floor_plan(supabase: Client, project_id: str, user_id: str, job_id: str, layout: LayoutData) -> str:
        payload = {
            "project_id": project_id,
            "user_id": user_id,
            "version_name": "AI Generated Option 1",
            "layout_data": layout.model_dump(),
            "ai_generation_id": job_id
        }
        res = supabase.table("floor_plans").insert(payload).execute()
        return res.data[0]["id"]

    @staticmethod
    async def get_latest_successful(supabase: Client, project_id: str) -> Optional[dict]:
        """
        Fetch the most recent valid floor plan for a project.
        Used as a fallback when live generation fails.
        """
        try:
            res = supabase.table("floor_plans") \
                .select("id, layout_data, created_at, version_name") \
                .eq("project_id", project_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
            
            if res.data and len(res.data) > 0:
                logger.info("Found saved fallback plan for project %s", project_id)
                return res.data[0]
            
            return None
        except Exception as e:
            logger.warning("Error fetching saved plan fallback: %s", e)
            return None
