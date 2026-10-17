"""
Cost Estimation API Routes — Phase 6D.
Endpoints for generating, fetching, recalculating, and exporting construction cost estimates.
Enforces project ownership, non-destructive persistence, and instant recalculation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from supabase import Client
from typing import Optional, Dict, Any
import logging

from app.core.security import get_current_user, get_user_supabase_client
from app.services import project_service
from app.services.floorplan_service import FloorplanService
from app.models.layout import LayoutData
from app.models.cost_estimate import (
    EstimateRequest,
    EstimateRecalculateRequest,
    EstimateResponse,
    RateProfile
)
from app.services.cost_estimation import (
    get_default_rate_profile,
    CostEstimationEngine
)

logger = logging.getLogger("api.cost_estimation")

router = APIRouter(prefix="/api/v1/projects/{project_id}/cost-estimate", tags=["cost-estimation"])


@router.get("/rates", response_model=RateProfile)
async def get_benchmark_rates(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Returns the benchmark material and labor rate profile for Hyderabad, Telangana.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    return get_default_rate_profile()


@router.post("/generate", response_model=EstimateResponse)
async def generate_cost_estimate(
    project_id: str,
    request: EstimateRequest = None,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Generates a construction cost estimate from the project's selected/latest validated floor plan.
    Saves snapshot to Supabase and returns complete structured estimate.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    req_data = request or EstimateRequest()
    raw_layout = req_data.layout_data
    floor_plan_id = req_data.floor_plan_id

    # If layout data was not provided directly in request body, retrieve from database
    if not raw_layout:
        if floor_plan_id:
            res = supabase.table("floor_plans").select("id, layout_data").eq("id", floor_plan_id).execute()
            if res.data and len(res.data) > 0:
                raw_layout = res.data[0]["layout_data"]
        else:
            saved_plan = await FloorplanService.get_latest_successful(supabase, project_id)
            if saved_plan:
                raw_layout = saved_plan["layout_data"]
                floor_plan_id = saved_plan["id"]

    if not raw_layout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No validated floor plan found for this project. Please generate a floor plan first."
        )

    try:
        layout = LayoutData.model_validate(raw_layout)
    except Exception as e:
        logger.error("Failed to parse layout data for cost estimation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid layout geometry schema: {str(e)}"
        )

    # Execute deterministic calculation engine
    try:
        engine = CostEstimationEngine(
            layout=layout,
            project_id=project_id,
            floor_plan_id=floor_plan_id,
            custom_rates=req_data.custom_rates,
            custom_specifications=req_data.custom_specifications
        )
        estimate = engine.calculate_estimate()
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.exception("Cost estimation calculation error: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cost estimation calculation failed")

    # Persist snapshot to database
    try:
        rates_dict = {k: v.model_dump() for k, v in estimate.rates_snapshot.items()}
        line_items_list = [item.model_dump() for item in estimate.line_items]
        area_sched_dict = estimate.area_schedule.model_dump()

        payload = {
            "project_id": project_id,
            "user_id": user_id,
            "floor_plan_id": floor_plan_id,
            "material_cost": estimate.cost_summary.materials_cost,
            "labor_cost": estimate.cost_summary.labor_cost,
            "electrical_cost": estimate.cost_summary.services_cost * 0.5,
            "plumbing_cost": estimate.cost_summary.services_cost * 0.5,
            "interior_cost": estimate.cost_summary.openings_and_fixtures_cost,
            "exterior_cost": 0.0,
            "total_cost": estimate.cost_summary.grand_total,
            "estimated_duration_weeks": max(12, int(estimate.area_schedule.total_built_up_area / 80)),
            "area_schedule": area_sched_dict,
            "quantity_breakdown": estimate.quantities,
            "line_items": line_items_list,
            "rates_snapshot": rates_dict,
            "assumptions": estimate.assumptions_and_limitations,
            "contingency_cost": estimate.cost_summary.contingency_cost,
            "tax_cost": estimate.cost_summary.tax_cost,
            "overhead_cost": estimate.cost_summary.contractor_overhead_cost,
        }

        # Check if existing estimation row exists for this project
        existing = supabase.table("estimations").select("id").eq("project_id", project_id).execute()
        if existing.data and len(existing.data) > 0:
            db_res = supabase.table("estimations").update(payload).eq("id", existing.data[0]["id"]).execute()
            if db_res.data and len(db_res.data) > 0:
                estimate.estimate_id = db_res.data[0]["id"]
        else:
            db_res = supabase.table("estimations").insert(payload).execute()
            if db_res.data and len(db_res.data) > 0:
                estimate.estimate_id = db_res.data[0]["id"]

    except Exception as db_err:
        logger.warning("Database persistence error (returning in-memory calculation): %s", db_err)

    return estimate


@router.post("/recalculate", response_model=EstimateResponse)
async def recalculate_cost_estimate(
    project_id: str,
    request: EstimateRecalculateRequest,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Recalculates an existing estimate with modified unit rates and specifications
    WITHOUT rerunning the CP-SAT layout solver.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    raw_layout = request.layout_data
    floor_plan_id = request.floor_plan_id

    # If layout was not provided in body, load from floor plan or latest estimation
    if not raw_layout:
        if floor_plan_id:
            res = supabase.table("floor_plans").select("id, layout_data").eq("id", floor_plan_id).execute()
            if res.data and len(res.data) > 0:
                raw_layout = res.data[0]["layout_data"]
        else:
            saved_plan = await FloorplanService.get_latest_successful(supabase, project_id)
            if saved_plan:
                raw_layout = saved_plan["layout_data"]
                floor_plan_id = saved_plan["id"]

    if not raw_layout:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot recalculate: No layout data or saved floor plan available."
        )

    try:
        layout = LayoutData.model_validate(raw_layout)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid layout geometry: {str(e)}")

    try:
        engine = CostEstimationEngine(
            layout=layout,
            project_id=project_id,
            floor_plan_id=floor_plan_id,
            custom_rates=request.custom_rates,
            custom_specifications=request.custom_specifications
        )
        estimate = engine.calculate_estimate()
        if request.current_estimate_id:
            estimate.estimate_id = request.current_estimate_id
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.exception("Recalculate estimation failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Recalculation error")

    return estimate


@router.get("", response_model=EstimateResponse)
async def get_latest_estimate(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Retrieves the most recent saved cost estimate for a project.
    If none is found, generates one automatically from the latest floor plan.
    """
    is_owner = await project_service.verify_ownership(project_id, supabase, user_id=user_id)
    if not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")

    # Check for saved estimate
    try:
        res = supabase.table("estimations").select("*").eq("project_id", project_id).order("updated_at", desc=True).limit(1).execute()
        if res.data and len(res.data) > 0:
            row = res.data[0]
            # If full line items snapshot exists, reconstruct response
            if row.get("line_items") and len(row["line_items"]) > 0:
                area_sched = row.get("area_schedule") or {}
                bua = area_sched.get("total_built_up_area", 1000.0)
                subtotal = float(row.get("material_cost", 0)) + float(row.get("labor_cost", 0)) + float(row.get("interior_cost", 0)) + float(row.get("electrical_cost", 0)) + float(row.get("plumbing_cost", 0))
                grand_total = float(row.get("total_cost", subtotal))
                cost_sqft = round(grand_total / bua, 2) if bua > 0 else 0.0

                return EstimateResponse(
                    estimate_id=row["id"],
                    project_id=project_id,
                    floor_plan_id=row.get("floor_plan_id"),
                    created_at=row.get("created_at") or "",
                    currency="INR",
                    currency_symbol="₹",
                    location_profile="Hyderabad, Telangana (Saved Snapshot)",
                    area_schedule=area_sched,
                    quantities=row.get("quantity_breakdown") or {},
                    line_items=row.get("line_items") or [],
                    cost_summary={
                        "materials_cost": float(row.get("material_cost", 0)),
                        "labor_cost": float(row.get("labor_cost", 0)),
                        "openings_and_fixtures_cost": float(row.get("interior_cost", 0)),
                        "services_cost": float(row.get("electrical_cost", 0)) + float(row.get("plumbing_cost", 0)),
                        "subtotal": subtotal,
                        "contingency_percentage": 5.0,
                        "contingency_cost": float(row.get("contingency_cost", 0)),
                        "contractor_overhead_percentage": 10.0,
                        "contractor_overhead_cost": float(row.get("overhead_cost", 0)),
                        "tax_percentage": 0.0,
                        "tax_cost": float(row.get("tax_cost", 0)),
                        "grand_total": grand_total,
                        "cost_per_sq_ft": cost_sqft,
                        "cost_per_sq_ft_denominator": f"Total Constructed Built-Up Area ({bua} sq ft)"
                    },
                    rates_snapshot=row.get("rates_snapshot") or {},
                    assumptions_and_limitations=row.get("assumptions") or [],
                    disclaimer="Saved estimation snapshot."
                )
    except Exception as e:
        logger.warning("Error loading saved estimation from DB: %s", e)

    # Fallback: Generate fresh estimate from latest floor plan
    return await generate_cost_estimate(project_id, EstimateRequest(), user_id, supabase)


@router.get("/export-csv")
async def export_estimate_csv(
    project_id: str,
    user_id: str = Depends(get_current_user),
    supabase: Client = Depends(get_user_supabase_client)
):
    """
    Generates and downloads a CSV spreadsheet of the cost estimate.
    """
    estimate = await get_latest_estimate(project_id, user_id, supabase)
    csv_text = CostEstimationEngine.export_to_csv(estimate)

    filename = f"cost_estimate_{project_id[:8]}.csv"
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
