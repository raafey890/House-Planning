"""
Interior Design API Routes — Phase 6E.1.
Exposes endpoints for the 32-design catalog, room compatibility checks,
cost derivation, and project-level interior selections persistence.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional, Dict, List, Any
import logging
import json
import os
from datetime import datetime

from app.core.security import get_current_user, get_user_supabase_client
from app.services import project_service
from app.models.interior_design import (
    InteriorDesignOption,
    RoomInteriorSelection,
    ProjectInteriorSelectionsPayload,
    CalculateInteriorCostRequest,
    RoomImageGenerationRequest,
    RoomImageGenerationResponse
)
from app.services.interior_design.catalog import (
    get_all_interior_designs,
    get_interior_design_by_id,
    get_designs_by_category
)
from app.services.interior_design.service import (
    validate_design_compatibility,
    calculate_room_interior_cost,
    calculate_project_interior_costs,
    filter_catalog
)
from app.services.interior_design.preview_service import generate_plan_aware_preview
from app.services.interior_design.image_generator_service import generate_personalized_room_image

logger = logging.getLogger("api.interior_designs")

# Router for catalog & general interior calculations
catalog_router = APIRouter(prefix="/api/v1/interior", tags=["interior-catalog"])

# Router for project-specific selections
project_interior_router = APIRouter(prefix="/api/v1/projects/{project_id}/interior-selections", tags=["interior-selections"])

# In-memory/filesystem cache for resilience during migrations & offline tests
LOCAL_SELECTIONS_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "canonical_layouts")


def _get_local_cache_path(project_id: str) -> str:
    return os.path.join(CACHE_DIR, f"interior_selections_{project_id}.json")


def _read_local_selections(project_id: str) -> Optional[Dict[str, Any]]:
    if project_id in LOCAL_SELECTIONS_CACHE:
        return LOCAL_SELECTIONS_CACHE[project_id]
    cache_file = _get_local_cache_path(project_id)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                LOCAL_SELECTIONS_CACHE[project_id] = data
                return data
        except Exception as e:
            logger.warning(f"Failed to read local selections cache: {e}")
    return None


def _write_local_selections(project_id: str, data: Dict[str, Any]):
    LOCAL_SELECTIONS_CACHE[project_id] = data
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_file = _get_local_cache_path(project_id)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to write local selections cache: {e}")


# ── Catalog Endpoints ────────────────────────────────────────────────────────

@catalog_router.get("/catalog", response_model=List[InteriorDesignOption])
async def list_catalog(
    category: Optional[str] = Query(None, description="living_room, bedroom, kitchen, bathroom, dining_room, ceiling_lighting"),
    room_type: Optional[str] = Query(None, description="living_room, master_bedroom, bedroom, kitchen, bathroom, etc."),
    budget_tier: Optional[str] = Query(None, description="Economy, Mid-Range, Premium, Luxury"),
    style: Optional[str] = Query(None, description="Modern, Luxury, Minimalist, Warm Wood, etc.")
):
    """
    Returns the 32 distinct interior design catalog options with optional filtering.
    """
    return filter_catalog(category=category, room_type=room_type, budget_tier=budget_tier, style=style)


@catalog_router.get("/catalog/{design_id}", response_model=InteriorDesignOption)
async def get_design_detail(design_id: str):
    """
    Returns full details for a specific interior design option.
    """
    design = get_interior_design_by_id(design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interior design option '{design_id}' not found"
        )
    return design


@catalog_router.post("/validate-compatibility")
async def check_compatibility(payload: Dict[str, Any]):
    """
    Validates physical dimension clearances and functional compatibility of a design for a room.
    """
    design_id = payload.get("design_id")
    room_type = payload.get("room_type", "living_room")
    room_width = float(payload.get("room_width", 0.0))
    room_length = float(payload.get("room_length", 0.0))
    room_area = float(payload.get("room_area", room_width * room_length))

    if not design_id:
        raise HTTPException(status_code=400, detail="Missing design_id")

    return validate_design_compatibility(
        design_id=design_id,
        room_type=room_type,
        room_width=room_width,
        room_length=room_length,
        room_area=room_area
    )


@catalog_router.post("/calculate-cost")
async def calculate_costs(req: CalculateInteriorCostRequest):
    """
    Calculates the exact interior cost and breakdown without double-counting base finishes.
    """
    result = calculate_project_interior_costs(
        selections=req.selections,
        layout_data=req.layout_data
    )
    return {
        "project_id": req.project_id,
        "floor_plan_id": req.floor_plan_id,
        "total_interior_cost": result["total_interior_cost"],
        "selections": result["selections"],
        "room_count": result["room_count"]
    }


@catalog_router.post("/generate-preview")
async def create_plan_aware_preview(payload: Dict[str, Any]):
    """
    Generates a personalized, geometry-grounded room layout visualization
    derived from the actual room's width, length, aspect ratio, openings,
    and user-selected interior finishes.
    """
    room_id = payload.get("room_id", "room_01")
    room_name = payload.get("room_name", "Room")
    room_type = payload.get("room_type", "bedroom")
    room_width = float(payload.get("room_width", 12.0))
    room_length = float(payload.get("room_length", 14.0))
    room_area = float(payload.get("room_area", room_width * room_length))
    design_id = payload.get("design_id", "int_bed_01")
    floor_name = payload.get("floor_name", "Ground Floor")
    doors = payload.get("doors")
    windows = payload.get("windows")
    customizations = payload.get("customizations")

    result = generate_plan_aware_preview(
        room_id=room_id,
        room_name=room_name,
        room_type=room_type,
        room_width=room_width,
        room_length=room_length,
        room_area=room_area,
        design_id=design_id,
        floor_name=floor_name,
        doors=doors,
        windows=windows,
        customizations=customizations
    )

    if result.get("status") == "error":
        if result.get("mode") == "rejected_incompatible":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message"))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("message"))

    return result


@catalog_router.post("/generate-image", response_model=RoomImageGenerationResponse)
async def create_personalized_room_image(req: RoomImageGenerationRequest):
    """
    Constructs a geometry-grounded architectural prompt and generates or retrieves
    a personalized photorealistic interior render based on the user's exact room dimensions,
    aspect ratio, fenestration, and selected finish customizations.
    """
    return await generate_personalized_room_image(req)


# ── Project Selections Endpoints ──────────────────────────────────────────────

@project_interior_router.get("", response_model=ProjectInteriorSelectionsPayload)
async def get_project_selections(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Fetches the saved room interior design selections for a given project.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    # Attempt query from Supabase table
    try:
        res = supabase.table("project_interior_selections").select("*").eq("project_id", project_id).execute()
        if res.data:
            selections: Dict[str, RoomInteriorSelection] = {}
            total_cost = 0.0
            for row in res.data:
                sel = RoomInteriorSelection(
                    room_id=row["room_id"],
                    room_type=row.get("room_type", "room"),
                    room_name=row.get("room_name"),
                    room_area_sqft=float(row.get("room_area_sqft", 0.0)),
                    design_id=row["design_id"],
                    design_name=row.get("design_name"),
                    wall_finish_choice=row.get("wall_finish_choice"),
                    flooring_choice=row.get("flooring_choice"),
                    ceiling_option_id=row.get("ceiling_option_id"),
                    lighting_points_count=int(row.get("lighting_points_count", 0)),
                    customizations=row.get("customizations") or {},
                    additional_cost=float(row.get("additional_cost", 0.0)),
                    cost_breakdown=row.get("cost_breakdown") or {}
                )
                selections[sel.room_id] = sel
                total_cost += sel.additional_cost

            return ProjectInteriorSelectionsPayload(
                project_id=project_id,
                selections=selections,
                total_interior_cost=round(total_cost, 2),
                updated_at=datetime.utcnow().isoformat()
            )
    except Exception as e:
        logger.warning(f"Supabase query failed, falling back to local cache: {e}")

    # Fallback to local cache
    cached = _read_local_selections(project_id)
    if cached:
        return ProjectInteriorSelectionsPayload(**cached)

    return ProjectInteriorSelectionsPayload(
        project_id=project_id,
        selections={},
        total_interior_cost=0.0
    )


@project_interior_router.post("", response_model=ProjectInteriorSelectionsPayload)
async def save_project_selections(
    project_id: str,
    payload: ProjectInteriorSelectionsPayload,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Saves or updates room interior selections for a project. Recalculates costs automatically.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    # Re-calculate costs to ensure absolute accuracy and zero double-counting
    calc_result = calculate_project_interior_costs(selections=payload.selections)
    updated_selections = calc_result["selections"]
    total_cost = calc_result["total_interior_cost"]

    # Attempt persistence in Supabase
    try:
        # Upsert each room selection
        for room_id, sel in updated_selections.items():
            record = {
                "project_id": project_id,
                "room_id": str(room_id),
                "room_type": sel.room_type,
                "room_name": sel.room_name or room_id,
                "room_area_sqft": sel.room_area_sqft,
                "design_id": sel.design_id,
                "design_name": sel.design_name,
                "wall_finish_choice": sel.wall_finish_choice,
                "flooring_choice": sel.flooring_choice,
                "ceiling_option_id": sel.ceiling_option_id,
                "lighting_points_count": sel.lighting_points_count,
                "customizations": sel.customizations,
                "additional_cost": sel.additional_cost,
                "cost_breakdown": sel.cost_breakdown,
                "updated_at": datetime.utcnow().isoformat()
            }
            supabase.table("project_interior_selections").upsert(
                record, on_conflict="project_id,room_id"
            ).execute()
    except Exception as e:
        logger.warning(f"Could not upsert to Supabase table project_interior_selections: {e}")

    # Always persist to resilient local cache as well
    result_payload = ProjectInteriorSelectionsPayload(
        project_id=project_id,
        floor_plan_id=payload.floor_plan_id,
        selections=updated_selections,
        total_interior_cost=total_cost,
        updated_at=datetime.utcnow().isoformat()
    )
    _write_local_selections(project_id, result_payload.model_dump())

    return result_payload


@project_interior_router.delete("/{room_id}", response_model=ProjectInteriorSelectionsPayload)
async def delete_room_selection(
    project_id: str,
    room_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Deletes the interior selection for a specific room.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    # Try deleting from Supabase
    try:
        supabase.table("project_interior_selections").delete().eq("project_id", project_id).eq("room_id", room_id).execute()
    except Exception as e:
        logger.warning(f"Failed to delete from Supabase: {e}")

    # Update local cache
    cached = _read_local_selections(project_id) or {"project_id": project_id, "selections": {}, "total_interior_cost": 0.0}
    if "selections" in cached and room_id in cached["selections"]:
        del cached["selections"][room_id]
        # Recalculate
        new_selections = {k: RoomInteriorSelection(**v) for k, v in cached["selections"].items()}
        recalc = calculate_project_interior_costs(new_selections)
        cached["selections"] = {k: v.model_dump() for k, v in recalc["selections"].items()}
        cached["total_interior_cost"] = recalc["total_interior_cost"]
        return await get_project_selections(project_id=project_id, user_id=user_id, supabase=supabase)


# ── Aliases matching /api/v1/interior/projects/{project_id}/selections ────────

@catalog_router.get("/projects/{project_id}/selections", response_model=ProjectInteriorSelectionsPayload)
async def get_project_selections_alias(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    return await get_project_selections(project_id=project_id, user_id=user_id, supabase=supabase)


@catalog_router.post("/projects/{project_id}/selections", response_model=ProjectInteriorSelectionsPayload)
async def save_project_selections_alias(
    project_id: str,
    payload: ProjectInteriorSelectionsPayload,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    return await save_project_selections(project_id=project_id, payload=payload, user_id=user_id, supabase=supabase)

