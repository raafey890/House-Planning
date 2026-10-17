"""
Exterior Design API Routes — Phase 6F.1.
Exposes endpoints for the 32-design catalog, real-time plan-aware compatibility,
incremental cost derivation, and project-level exterior selections persistence.
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
from app.models.exterior_design import (
    ExteriorDesignOption,
    ProjectExteriorSelection,
    ProjectExteriorSelectionPayload,
    CalculateExteriorCostRequest,
    CompatibilityCheckRequest,
    CompatibilityCheckResponse,
    CanonicalExteriorConfig,
    ExteriorVisualizationRequest,
    ExteriorVisualizationResponse
)
from app.services.exterior_design.catalog import (
    get_all_exterior_designs,
    get_exterior_design_by_id,
    get_designs_by_category
)
from app.services.exterior_design.service import (
    validate_exterior_compatibility,
    calculate_exterior_design_cost,
    filter_catalog,
    get_compatible_catalog_for_project
)
from app.services.exterior_design.preview_service import (
    generate_personalized_exterior_preview
)
from app.services.exterior_design.image_generator_service import (
    generate_personalized_exterior_image
)

logger = logging.getLogger("api.exterior_designs")

# Router for catalog & general exterior calculations
catalog_router = APIRouter(prefix="/api/v1/exterior", tags=["exterior-catalog"])

# Router for project-specific selections
project_exterior_router = APIRouter(prefix="/api/v1/projects/{project_id}/exterior-selections", tags=["exterior-selections"])

# In-memory/filesystem cache for resilience during migrations & offline tests
LOCAL_EXTERIOR_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "canonical_layouts")


def _get_local_cache_path(project_id: str) -> str:
    return os.path.join(CACHE_DIR, f"exterior_selections_{project_id}.json")


def _read_local_selections(project_id: str) -> Optional[Dict[str, Any]]:
    if project_id in LOCAL_EXTERIOR_CACHE:
        return LOCAL_EXTERIOR_CACHE[project_id]
    cache_file = _get_local_cache_path(project_id)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                LOCAL_EXTERIOR_CACHE[project_id] = data
                return data
        except Exception as e:
            logger.warning(f"Failed to read local exterior selections cache: {e}")
    return None


def _write_local_selections(project_id: str, data: Dict[str, Any]):
    LOCAL_EXTERIOR_CACHE[project_id] = data
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        cache_file = _get_local_cache_path(project_id)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to write local exterior selections cache: {e}")


# ── Catalog Endpoints ────────────────────────────────────────────────────────

@catalog_router.get("/catalog", response_model=List[ExteriorDesignOption])
async def list_catalog(
    category: Optional[str] = Query(None, description="modern_contemporary, minimalist, luxury_villa, traditional_indian, indian_modern, mediterranean, tropical_contemporary, premium_duplex"),
    budget_tier: Optional[str] = Query(None, description="Economy, Mid-Range, Premium, Luxury"),
    style: Optional[str] = Query(None, description="Modern, Luxury, Minimalist, Traditional, etc."),
    house_type: Optional[str] = Query(None, description="Villa, Duplex, Bungalow, Independent House, Row House"),
    search: Optional[str] = Query(None, description="Search keyword in title, style, or materials")
):
    """
    Returns the 32 distinct exterior design catalog options with optional filtering.
    """
    return filter_catalog(category=category, budget_tier=budget_tier, style=style, house_type=house_type, search=search)


@catalog_router.get("/catalog/{design_id}", response_model=ExteriorDesignOption)
async def get_design_detail(design_id: str):
    """
    Returns full details for a specific exterior design option.
    """
    design = get_exterior_design_by_id(design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exterior design option '{design_id}' not found"
        )
    return design


@catalog_router.post("/validate-compatibility", response_model=CompatibilityCheckResponse)
async def check_compatibility(payload: CompatibilityCheckRequest):
    """
    Validates physical dimension clearances, floor counts, and architectural compatibility
    without altering the approved floor plan.
    """
    return validate_exterior_compatibility(
        design_id=payload.design_id,
        plot_width=payload.plot_width,
        plot_length=payload.plot_length,
        floors=payload.floors,
        building_type=payload.building_type,
        building_footprint_sqft=payload.building_footprint_sqft
    )


@catalog_router.post("/calculate-cost")
async def calculate_costs(req: CalculateExteriorCostRequest):
    """
    Calculates the exact exterior cost breakdown derived from perimeter, floor height,
    accent cladding, premium doors/windows, lighting, boundary wall, and landscaping.
    """
    return calculate_exterior_design_cost(
        design_id=req.design_id,
        plot_width=req.plot_width or 30.0,
        plot_length=req.plot_length or 40.0,
        floors=req.floors or 1,
        building_footprint_sqft=req.building_footprint_sqft,
        materials=req.materials,
        lighting=req.lighting,
        architectural_elements=req.architectural_elements,
        landscaping=req.landscaping,
        boundary_wall=req.boundary_wall
    )


@catalog_router.post("/generate-preview", response_model=ExteriorVisualizationResponse)
async def generate_exterior_preview_endpoint(req: ExteriorVisualizationRequest):
    """
    Generates a personalized, dimension-grounded vector elevation preview (SVG)
    tailored to the project's exact plot frontage, floor levels, perspective angle,
    day/night lighting, and user-customized paint/material selections.
    """
    design = get_exterior_design_by_id(req.design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exterior design option '{req.design_id}' not found"
        )
    return generate_personalized_exterior_preview(req)


@catalog_router.post("/generate-image", response_model=ExteriorVisualizationResponse)
async def generate_exterior_image_endpoint(req: ExteriorVisualizationRequest):
    """
    Generates a photorealistic exterior rendering using Google Gemini (gemini-2.5-flash-image)
    grounded in actual project dimensions, selected design DNA, and paint/material finishes.
    Provides honest provider diagnostics (e.g. 429 quota exhaustion) without simulated success.
    """
    design = get_exterior_design_by_id(req.design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exterior design option '{req.design_id}' not found"
        )
    return generate_personalized_exterior_image(req)


@catalog_router.post("/validate-config")
async def validate_canonical_config(config: CanonicalExteriorConfig):
    """
    Validates a canonical exterior configuration model for completeness and physical constraints.
    """
    design = get_exterior_design_by_id(config.design_id)
    if not design:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exterior design option '{config.design_id}' not found"
        )
    return {
        "status": "valid",
        "project_id": config.project_id,
        "design_id": config.design_id,
        "design_name": design.name,
        "floors": config.floors,
        "plot_width": config.plot_width,
        "plot_length": config.plot_length,
        "facing": config.plot_facing
    }


# ── Project Selections Endpoints ──────────────────────────────────────────────

@project_exterior_router.get("", response_model=ProjectExteriorSelectionPayload)
async def get_project_exterior_selection(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Fetches the saved exterior selection and customizations for a given project.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    # Attempt query from Supabase table
    try:
        res = supabase.table("project_exterior_selections").select("*").eq("project_id", project_id).execute()
        if res.data and len(res.data) > 0:
            row = res.data[0]
            sel = ProjectExteriorSelection(
                project_id=row["project_id"],
                design_id=row["design_id"],
                design_name=row.get("design_name"),
                category=row.get("category"),
                style=row.get("style"),
                colors=row.get("colors") or {},
                materials=row.get("materials") or {},
                architectural_elements=row.get("architectural_elements") or {},
                lighting=row.get("lighting") or {},
                landscaping=row.get("landscaping") or {},
                boundary_wall=row.get("boundary_wall") or {},
                compatibility_status=row.get("compatibility_status", "compatible"),
                compatibility_notes=row.get("compatibility_notes") or [],
                additional_cost=float(row.get("additional_cost", 0.0)),
                cost_breakdown=row.get("cost_breakdown") or {},
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at")
            )
            return ProjectExteriorSelectionPayload(
                project_id=project_id,
                selection=sel,
                total_exterior_cost=sel.additional_cost,
                updated_at=sel.updated_at
            )
    except Exception as e:
        logger.warning(f"Supabase query failed, falling back to local cache: {e}")

    # Fallback to local cache
    cached = _read_local_selections(project_id)
    if cached:
        return ProjectExteriorSelectionPayload(**cached)

    return ProjectExteriorSelectionPayload(
        project_id=project_id,
        selection=None,
        total_exterior_cost=0.0
    )


@project_exterior_router.post("", response_model=ProjectExteriorSelectionPayload)
async def save_project_exterior_selection(
    project_id: str,
    payload: ProjectExteriorSelectionPayload,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Saves or updates the exterior design selection and customizations for a project.
    Recalculates costs automatically using dimensional parameters.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    if not payload.selection:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No exterior selection provided")

    sel = payload.selection
    design = get_exterior_design_by_id(sel.design_id)
    if not design:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Design '{sel.design_id}' not found in catalog")

    # Fetch project context for dimensional grounding
    context = {}
    try:
        context = await project_service.get_planning_context(project_id, supabase)
    except Exception as e:
        logger.warning(f"Could not fetch full planning context: {e}")

    plot_w = float(context.get("plot_width", 30.0) or 30.0)
    plot_l = float(context.get("plot_length", 40.0) or 40.0)
    floors = int(context.get("floors", 1) or 1)

    # Recalculate cost with dimensional precision
    cost_calc = calculate_exterior_design_cost(
        design_id=sel.design_id,
        plot_width=plot_w,
        plot_length=plot_l,
        floors=floors,
        materials=sel.materials,
        lighting=sel.lighting,
        architectural_elements=sel.architectural_elements,
        landscaping=sel.landscaping,
        boundary_wall=sel.boundary_wall
    )

    total_cost = cost_calc["total_exterior_cost"]
    breakdown = cost_calc["breakdown"]

    # Re-evaluate compatibility for storage
    compat = validate_exterior_compatibility(
        design_id=sel.design_id,
        plot_width=plot_w,
        plot_length=plot_l,
        floors=floors
    )

    updated_sel = ProjectExteriorSelection(
        project_id=project_id,
        design_id=sel.design_id,
        design_name=design.name,
        category=design.category,
        style=design.style,
        colors=sel.colors or design.customization_defaults.get("colors", {}),
        materials=sel.materials or design.customization_defaults.get("materials", {}),
        architectural_elements=sel.architectural_elements or design.customization_defaults.get("architectural_elements", {}),
        lighting=sel.lighting or design.customization_defaults.get("lighting", {}),
        landscaping=sel.landscaping or design.customization_defaults.get("landscaping", {}),
        boundary_wall=sel.boundary_wall or design.customization_defaults.get("boundary_wall", {}),
        compatibility_status=compat.status,
        compatibility_notes=compat.reasons,
        additional_cost=total_cost,
        cost_breakdown=breakdown,
        updated_at=datetime.utcnow().isoformat()
    )

    # Attempt persistence in Supabase
    try:
        record = {
            "project_id": project_id,
            "design_id": updated_sel.design_id,
            "design_name": updated_sel.design_name,
            "category": updated_sel.category,
            "style": updated_sel.style,
            "colors": updated_sel.colors,
            "materials": updated_sel.materials,
            "architectural_elements": updated_sel.architectural_elements,
            "lighting": updated_sel.lighting,
            "landscaping": updated_sel.landscaping,
            "boundary_wall": updated_sel.boundary_wall,
            "compatibility_status": updated_sel.compatibility_status,
            "compatibility_notes": updated_sel.compatibility_notes,
            "additional_cost": updated_sel.additional_cost,
            "cost_breakdown": updated_sel.cost_breakdown,
            "updated_at": datetime.utcnow().isoformat()
        }
        supabase.table("project_exterior_selections").upsert(
            record, on_conflict="project_id"
        ).execute()
    except Exception as e:
        logger.warning(f"Could not upsert to Supabase table project_exterior_selections: {e}")

    # Always persist to local cache
    result_payload = ProjectExteriorSelectionPayload(
        project_id=project_id,
        selection=updated_sel,
        total_exterior_cost=total_cost,
        updated_at=datetime.utcnow().isoformat()
    )
    _write_local_selections(project_id, result_payload.model_dump())

    return result_payload


@project_exterior_router.delete("", response_model=ProjectExteriorSelectionPayload)
async def delete_project_exterior_selection(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Clears the exterior design selection for a project.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    # Try deleting from Supabase
    try:
        supabase.table("project_exterior_selections").delete().eq("project_id", project_id).execute()
    except Exception as e:
        logger.warning(f"Failed to delete from Supabase: {e}")

    # Update local cache
    cached = {"project_id": project_id, "selection": None, "total_exterior_cost": 0.0, "updated_at": datetime.utcnow().isoformat()}
    _write_local_selections(project_id, cached)

    return ProjectExteriorSelectionPayload(**cached)


@project_exterior_router.get("/options")
async def get_project_exterior_options(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Returns all 32 catalog designs evaluated in real-time against this specific project's
    plot dimensions and floor count, with compatibility badges and clear architectural reasons.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    # Fetch project data
    context = {}
    try:
        context = await project_service.get_planning_context(project_id, supabase)
    except Exception as e:
        logger.warning(f"Could not fetch full planning context: {e}")

    return get_compatible_catalog_for_project(context)
