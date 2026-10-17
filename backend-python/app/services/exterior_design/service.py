"""
Exterior Design Service — Phase 6F.1.
Provides plan-aware design compatibility validation, incremental cost derivation
grounded in project dimensions and geometry, and catalog filtering.
"""

from typing import List, Optional, Dict, Any
import math
import logging

from app.models.exterior_design import (
    ExteriorDesignOption,
    ProjectExteriorSelection,
    CompatibilityCheckResponse
)
from app.services.exterior_design.catalog import (
    get_all_exterior_designs,
    get_exterior_design_by_id,
    EXTERIOR_DESIGNS
)

logger = logging.getLogger("services.exterior_design")


def filter_catalog(
    category: Optional[str] = None,
    budget_tier: Optional[str] = None,
    style: Optional[str] = None,
    house_type: Optional[str] = None,
    search: Optional[str] = None
) -> List[ExteriorDesignOption]:
    """Filters the 32 catalog options based on criteria."""
    designs = get_all_exterior_designs()

    filtered = []
    for d in designs:
        if category and category.lower() != "all" and d.category.lower() != category.lower():
            continue
        if budget_tier and budget_tier.lower() != "all" and d.budget_tier.lower() != budget_tier.lower():
            continue
        if style and style.lower() != "all" and d.style.lower() != style.lower():
            continue
        if house_type and house_type.lower() != "all":
            ht_lower = [ht.lower() for ht in d.suitable_house_types]
            if house_type.lower() not in ht_lower and "all" not in ht_lower:
                continue
        if search and search.strip():
            q = search.lower().strip()
            match_name = q in d.name.lower()
            match_desc = q in d.description.lower()
            match_style = q in d.style.lower()
            match_mats = any(q in m.lower() for m in d.material_palette)
            if not (match_name or match_desc or match_style or match_mats):
                continue
        filtered.append(d)

    return filtered


def validate_exterior_compatibility(
    design_id: str,
    plot_width: float,
    plot_length: float,
    floors: int = 1,
    building_type: Optional[str] = "Independent House",
    building_footprint_sqft: Optional[float] = None
) -> CompatibilityCheckResponse:
    """
    Evaluates physical, dimensional, and architectural compatibility of an exterior design
    against the user's actual project configuration. Never modifies floor plans.
    """
    design = get_exterior_design_by_id(design_id)
    if not design:
        return CompatibilityCheckResponse(
            design_id=design_id,
            status="not_recommended",
            score=0,
            is_compatible=False,
            reasons=[f"Design '{design_id}' not found in catalog."]
        )

    score = 100
    reasons = []
    adjustments = []

    plot_area = plot_width * plot_length
    rec_size = design.recommended_plot_size
    min_w = float(rec_size.get("min_width_ft", 25.0))
    min_area = float(rec_size.get("min_area_sqft", 1000.0))
    max_area = float(rec_size.get("max_area_sqft", 10000.0))
    suitable_floors = design.suitable_floor_configs

    # 1. Floor Count Validation
    if floors not in suitable_floors:
        if floors < min(suitable_floors):
            # E.g. Single-storey house selecting a G+1/G+2 duplex or multi-tier villa
            score -= 35
            reasons.append(
                f"Floor Count Mismatch: This design is optimized for {min(suitable_floors)}-floor multi-level elevations "
                f"(G+{min(suitable_floors)-1}), but your project has {floors} floor (Ground only)."
            )
            adjustments.append("Can be adapted by taking the ground-floor facade treatment and capping with an aesthetic parapet.")
        else:
            # E.g. 3-storey building selecting a 1-storey bungalow
            score -= 25
            reasons.append(
                f"Floor Count Warning: Designed primarily for {max(suitable_floors)} floors, whereas your project has {floors} floors."
            )
            adjustments.append("Upper floor will need repeated fenestration matching the first-floor rhythm.")
    else:
        reasons.append(f"Optimal Floor Match: Fully designed for {floors}-floor configuration (G+{floors-1}).")

    # 2. Plot Frontage (Width) Validation
    width_diff = min_w - plot_width
    if width_diff > 5.0:
        # Heavily constrained frontage
        score -= 30
        reasons.append(
            f"Frontage Constraint: Requires minimum {min_w:.0f}ft plot frontage for architectural proportions; "
            f"your plot width is {plot_width:.0f}ft ({width_diff:.0f}ft deficit)."
        )
        adjustments.append("Horizontal elements, car porch, and window spans will need compression to fit frontage.")
    elif width_diff > 0.0:
        score -= 10
        reasons.append(
            f"Frontage Notice: Ideal frontage is {min_w:.0f}ft; your plot is {plot_width:.0f}ft (minor compression needed)."
        )
        adjustments.append("Slight narrowing of lateral louvers or side reveals.")
    else:
        reasons.append(f"Excellent Frontage: Plot width {plot_width:.0f}ft comfortably fits the required {min_w:.0f}ft facade.")

    # 3. Plot Area Validation
    if plot_area < min_area * 0.8:
        score -= 25
        reasons.append(
            f"Area Constraint: Best suited for plots >= {min_area:.0f} sq ft; your plot is {plot_area:.0f} sq ft."
        )
    elif plot_area > max_area * 1.3:
        score -= 10
        reasons.append(
            f"Expansive Plot Notice: Your plot ({plot_area:.0f} sq ft) exceeds typical compact footprint; boundary landscaping recommended."
        )

    # 4. Building Type Validation
    if building_type and building_type.strip():
        bt_clean = building_type.lower()
        suitable_lower = [st.lower() for st in design.suitable_house_types]
        if not any(st in bt_clean or bt_clean in st for st in suitable_lower):
            score -= 15
            reasons.append(f"House Type Adjustment: Styled as {design.style} {', '.join(design.suitable_house_types)}; your type is {building_type}.")

    # Normalize Score & Determine Status
    final_score = max(0, min(100, score))
    if final_score >= 80:
        status = "compatible"
    elif final_score >= 50:
        status = "compatible_with_adjustments"
    else:
        status = "not_recommended"

    return CompatibilityCheckResponse(
        design_id=design_id,
        status=status,
        score=final_score,
        is_compatible=(status != "not_recommended"),
        reasons=reasons,
        adjustments_suggested=adjustments
    )


def calculate_project_exterior_cost(
    design_id: str,
    plot_width: float = 30.0,
    plot_length: float = 40.0,
    floors: int = 1,
    building_footprint_sqft: Optional[float] = None,
    materials: Optional[Dict[str, Any]] = None,
    lighting: Optional[Dict[str, Any]] = None,
    architectural_elements: Optional[Dict[str, Any]] = None,
    landscaping: Optional[Dict[str, Any]] = None,
    boundary_wall: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes realistic incremental exterior finishing and upgrade costs grounded in actual dimensions.
    Enforces ZERO double-counting with civil construction estimates.
    """
    design = get_exterior_design_by_id(design_id)
    if not design:
        return {"total_exterior_cost": 0.0, "breakdown": {}}

    materials = materials or {}
    lighting = lighting or {}
    arch = architectural_elements or {}
    land = landscaping or {}
    bwall = boundary_wall or {}

    # 1. Geometry-Grounded Dimensions
    # Footprint perimeter based on standard 70-75% building coverage
    eff_w = plot_width * 0.78
    eff_l = plot_length * 0.75
    footprint = building_footprint_sqft or (eff_w * eff_l)
    external_perimeter = 2.0 * (eff_w + eff_l)
    floor_height = 10.5
    total_height = floors * floor_height

    # Gross exterior wall area & net paintable area
    gross_wall_area = external_perimeter * total_height
    window_door_openings = gross_wall_area * 0.18  # 18% fenestration deduction
    net_wall_area = max(200.0, gross_wall_area - window_door_openings)

    # Front Elevation specific area (where premium claddings are applied)
    front_elevation_area = eff_w * total_height
    accent_cladding_area = front_elevation_area * 0.35  # Approx 35% accent walling

    cost_params = design.cost_parameters or {}

    # 2. Paint & Wall Finish Upgrade (Differential over standard acrylic civil paint)
    finish_choice = materials.get("finish_type", design.customization_defaults.get("finish_type", "standard_paint"))
    paint_diff_rate = 0.0
    if finish_choice in ["textured_paint", "silicone_mineral_stucco", "spanish_troweled_stucco", "cycladic_lime_wash"]:
        paint_diff_rate = 18.0
    elif finish_choice in ["smooth_stucco", "nordic_lime_stucco", "earthen_textured_plaster", "rammed_earth_textured"]:
        paint_diff_rate = 22.0
    elif finish_choice in ["exposed_concrete_finish", "travertine_stone_dry_clad", "hand_chiseled_stone"]:
        paint_diff_rate = 28.0
    elif finish_choice in ["metal_cladding", "quartzite_water_facade", "statuario_marble_colonnade"]:
        paint_diff_rate = 34.0
    
    cost_paint_upgrade = round(paint_diff_rate * net_wall_area, 2)

    # 3. Façade Accent Cladding Upgrade
    cladding_choice = materials.get("cladding_type", design.customization_defaults.get("cladding_type", "none"))
    cladding_rate = 0.0
    if cladding_choice in ["fluted_composite_louvers", "charcoal_aluminum_box", "vertical_stacked_stone"]:
        cladding_rate = 280.0
    elif cladding_choice in ["natural_teak_soffit", "ash_timber_battens", "sheesham_vertical_battens", "bamboo_composite_louvers"]:
        cladding_rate = 360.0
    elif cladding_choice in ["silver_quartzite_slabs", "honed_sandstone_panels", "woodgrain_hpl_panels"]:
        cladding_rate = 340.0
    elif cladding_choice in ["terracotta_jaali_blocks", "laterite_stone_plinth", "concrete_integrated_planters"]:
        cladding_rate = 240.0
    elif cladding_choice in ["corten_steel_panels", "dark_bronze_acp", "laser_cut_brass_screens"]:
        cladding_rate = 450.0
    elif cladding_choice in ["italian_roman_travertine", "golden_sandstone_masonry", "dholpur_jharokha_units", "dry_stone_masonry"]:
        cladding_rate = 550.0
    elif cladding_choice in ["backlit_brazilian_quartzite", "fluted_marble_pilasters", "horizontal_ipe_siding"]:
        cladding_rate = 680.0

    cost_cladding = round(cladding_rate * accent_cladding_area, 2) if cladding_choice != "none" else 0.0

    # 4. Premium Doors & Windows Upgrade Differential
    window_upgrade_rate = float(cost_params.get("window_upgrade_rate", 20000.0))
    door_mat = materials.get("door_material", design.customization_defaults.get("door_material", "standard"))
    door_extra = 0.0
    if "pivot" in door_mat or "teak" in door_mat or "brass" in door_mat:
        door_extra = 25000.0
    elif "oversized" in door_mat or "pvd" in door_mat or "bronze" in door_mat or "glass_motorized" in door_mat:
        door_extra = 45000.0
    cost_fenestration = round(window_upgrade_rate + door_extra, 2)

    # 5. Balcony & Railing Upgrade
    cost_railing = 0.0
    if floors >= 2:
        balcony_width = min(eff_w * 0.6, 18.0)
        railing_mat = materials.get("railing_material", "glass_railing")
        railing_rate = 1800.0 if "glass" in railing_mat else 1200.0
        cost_railing = round(balcony_width * railing_rate, 2)

    # 6. Exterior Lighting Package
    fixture_count = int(lighting.get("fixture_count", 6))
    cost_lighting = round(fixture_count * 2400.0 + (12000.0 if design.budget_tier in ["Premium", "Luxury"] else 6000.0), 2)

    # 7. Boundary Wall & Automated Gate
    bwall_style = bwall.get("boundary_wall_style", design.customization_defaults.get("boundary_wall_style", "matching_plaster"))
    cost_boundary = 35000.0
    if "gold" in bwall_style or "marble" in bwall_style or "corten" in bwall_style:
        cost_boundary = 85000.0
    elif "stone" in bwall_style or "jaali" in bwall_style or "hpl" in bwall_style:
        cost_boundary = 55000.0

    # 8. Optional Landscaping & Driveway Pavers
    cost_landscaping = 0.0
    if land.get("greenery_level") == "high":
        cost_landscaping = 45000.0
    elif land.get("greenery_level") == "moderate":
        cost_landscaping = 28000.0
    elif land.get("greenery_level") == "low":
        cost_landscaping = 15000.0

    total_cost = round(
        cost_paint_upgrade + cost_cladding + cost_fenestration + cost_railing +
        cost_lighting + cost_boundary + cost_landscaping,
        2
    )

    breakdown = {
        "exterior_paint_upgrade": cost_paint_upgrade,
        "facade_cladding_and_louvers": cost_cladding,
        "doors_and_windows_upgrade": cost_fenestration,
        "balcony_railing_upgrade": cost_railing,
        "exterior_architectural_lighting": cost_lighting,
        "boundary_wall_and_gate": cost_boundary,
        "landscaping_and_pavers": cost_landscaping,
        "total": total_cost
    }

    return {
        "design_id": design_id,
        "total_exterior_cost": total_cost,
        "breakdown": breakdown,
        "quantities": {
            "net_paintable_wall_area_sqft": round(net_wall_area, 1),
            "accent_cladding_area_sqft": round(accent_cladding_area, 1),
            "perimeter_ft": round(external_perimeter, 1),
            "height_ft": total_height,
            "floors": floors
        }
    }


def get_compatible_catalog_for_project(
    project_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Evaluates all 32 catalog designs against the project's actual plot and floor data,
    attaching real-time compatibility badges, score, and explanation reasons.
    """
    plot_w = float(project_data.get("plot_width", 30.0) or 30.0)
    plot_l = float(project_data.get("plot_length", 40.0) or 40.0)
    floors = int(project_data.get("floors", 1) or 1)
    btype = project_data.get("building_type", "Independent House")
    footprint = project_data.get("building_footprint_sqft")

    catalog = get_all_exterior_designs()
    result = []

    for item in catalog:
        compat = validate_exterior_compatibility(
            design_id=item.id,
            plot_width=plot_w,
            plot_length=plot_l,
            floors=floors,
            building_type=btype,
            building_footprint_sqft=footprint
        )
        item_dict = item.model_dump()
        item_dict["compatibility"] = {
            "status": compat.status,
            "score": compat.score,
            "is_compatible": compat.is_compatible,
            "reasons": compat.reasons,
            "adjustments": compat.adjustments_suggested
        }
        result.append(item_dict)

    # Sort so most compatible styles appear first, maintaining category integrity
    result.sort(key=lambda x: x["compatibility"]["score"], reverse=True)
    return result


calculate_exterior_design_cost = calculate_project_exterior_cost
