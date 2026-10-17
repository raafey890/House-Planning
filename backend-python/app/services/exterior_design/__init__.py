"""
Exterior Design Services Package — Phase 6F.
"""

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
    generate_plan_aware_exterior_svg,
    generate_personalized_exterior_preview
)
from app.services.exterior_design.image_generator_service import (
    build_exterior_geometry_prompt,
    generate_personalized_exterior_image
)

__all__ = [
    "get_all_exterior_designs",
    "get_exterior_design_by_id",
    "get_designs_by_category",
    "validate_exterior_compatibility",
    "calculate_exterior_design_cost",
    "filter_catalog",
    "get_compatible_catalog_for_project",
    "generate_plan_aware_exterior_svg",
    "generate_personalized_exterior_preview",
    "build_exterior_geometry_prompt",
    "generate_personalized_exterior_image"
]
