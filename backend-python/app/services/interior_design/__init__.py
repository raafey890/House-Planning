"""
Interior Design Studio Services — Phase 6E.1.
Exposes catalog retrieval, cost calculation, compatibility validation,
plan-aware preview rendering, and persistence helpers.
"""

from app.services.interior_design.catalog import (
    INTERIOR_CATALOG_DATA,
    get_all_interior_designs,
    get_interior_design_by_id,
    get_designs_by_category,
)
from app.services.interior_design.service import (
    validate_design_compatibility,
    calculate_room_interior_cost,
    calculate_project_interior_costs,
    filter_catalog,
    FLOORING_UPGRADE_RATES,
    WALL_TREATMENT_RATES,
    BASELINE_RATES,
)
from app.services.interior_design.preview_service import generate_plan_aware_preview

__all__ = [
    "INTERIOR_CATALOG_DATA",
    "get_all_interior_designs",
    "get_interior_design_by_id",
    "get_designs_by_category",
    "validate_design_compatibility",
    "calculate_room_interior_cost",
    "calculate_project_interior_costs",
    "filter_catalog",
    "FLOORING_UPGRADE_RATES",
    "WALL_TREATMENT_RATES",
    "BASELINE_RATES",
    "generate_plan_aware_preview",
]
