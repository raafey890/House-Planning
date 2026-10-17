"""
Interior Design Service — Phase 6E.1.
Implements room-specific interior selections, dimension & geometry compatibility checks,
cost derivation with baseline differential logic (no double-counting with Phase 6D),
and project-level persistence.
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
from app.models.interior_design import (
    InteriorDesignOption,
    RoomInteriorSelection,
    ProjectInteriorSelectionsPayload,
)
from app.services.interior_design.catalog import (
    get_all_interior_designs,
    get_interior_design_by_id,
)

logger = logging.getLogger("services.interior_design")

# Baseline rates already included in Phase 6D civil / finishes estimate
BASELINE_RATES = {
    "flooring_sqft": 75.0,     # Standard vitrified tile material + laying
    "wall_paint_sqft": 32.0,   # Standard interior acrylic emulsion
    "ceiling_finish_sqft": 22.0 # Standard ceiling plaster & whitewash/distemper
}

# Flooring upgrade rates and differentials
FLOORING_UPGRADE_RATES = {
    "vitrified_tiles": {"rate": 75.0, "differential": 0.0, "name": "Vitrified Tiles (Baseline)"},
    "anti_skid_tiles": {"rate": 85.0, "differential": 10.0, "name": "Anti-Skid Vitrified Tiles"},
    "wooden_laminate": {"rate": 170.0, "differential": 95.0, "name": "Wooden Laminate Flooring"},
    "engineered_hardwood": {"rate": 260.0, "differential": 185.0, "name": "Engineered Oak Hardwood"},
    "italian_marble": {"rate": 315.0, "differential": 240.0, "name": "Imported Italian Marble"},
    "flamed_granite": {"rate": 140.0, "differential": 65.0, "name": "Flamed Granite Flooring"},
    "terrazzo_tiles": {"rate": 135.0, "differential": 60.0, "name": "Custom Terrazzo Flooring"},
}

# Wall treatment options
WALL_TREATMENT_RATES = {
    "standard_emulsion": {"rate": 32.0, "differential": 0.0, "name": "Standard Acrylic Emulsion"},
    "velvet_luxury_emulsion": {"rate": 58.0, "differential": 26.0, "name": "Luxury Velvet Emulsion"},
    "limewash_texture": {"rate": 90.0, "differential": 58.0, "name": "Artisanal Limewash Textured Paint"},
    "fluted_louvers": {"rate": 320.0, "differential": 288.0, "name": "Charcoal/Oak Fluted Acoustic Louvers"},
    "wood_veneer_paneling": {"rate": 380.0, "differential": 348.0, "name": "Natural Teak/Walnut Veneer Paneling"},
    "bookmatched_marble_slab": {"rate": 650.0, "differential": 618.0, "name": "Bookmatched Statuario Marble Feature Slab"},
    "exposed_brick_cladding": {"rate": 180.0, "differential": 148.0, "name": "Reclaimed Terracotta Brick Tile Cladding"},
    "wallpaper_accent": {"rate": 120.0, "differential": 88.0, "name": "Designer Textured Vinyl Wallpaper"},
}


def validate_design_compatibility(
    design_id: str,
    room_type: str,
    room_width: float = 0.0,
    room_length: float = 0.0,
    room_area: float = 0.0
) -> Dict[str, Any]:
    """
    Validates whether a selected interior design is structurally and spatially
    compatible with a specific room's type and dimensions.
    """
    design = get_interior_design_by_id(design_id)
    if not design:
        return {"compatible": False, "warnings": [f"Unknown design ID: {design_id}"], "notes": []}

    warnings: List[str] = []
    notes: List[str] = []
    norm_room_type = room_type.lower().replace(" ", "_")

    # 1. Room type suitability check
    suitable_types = [t.lower().replace(" ", "_") for t in design.suitable_room_types]
    if "all" not in suitable_types:
        # Check direct match or family match
        is_type_match = False
        if norm_room_type in suitable_types:
            is_type_match = True
        elif "bedroom" in norm_room_type and any("bedroom" in st for st in suitable_types):
            is_type_match = True
        elif ("guest" in norm_room_type or "study" in norm_room_type) and any("guest" in st for st in suitable_types or "bedroom" in st for st in suitable_types):
            is_type_match = True
        elif "living" in norm_room_type and any("living" in st for st in suitable_types or "hall" in st for st in suitable_types):
            is_type_match = True
        elif "bath" in norm_room_type and any("bath" in st for st in suitable_types or "toilet" in st for st in suitable_types):
            is_type_match = True
        elif "dining" in norm_room_type and any("dining" in st for st in suitable_types):
            is_type_match = True
        elif "kitchen" in norm_room_type and any("kitchen" in st for st in suitable_types):
            is_type_match = True

        if not is_type_match:
            warnings.append(
                f"Design '{design.name}' is categorized for {design.category.replace('_', ' ').title()} "
                f"but is being applied to '{room_type}'. Verify spatial compatibility."
            )

    # 2. Kitchen layout dimensional clearances
    min_dim = min(room_width, room_length) if room_width > 0 and room_length > 0 else 0.0
    if design_id == "int_kit_03": # U-Shaped Kitchen
        if min_dim > 0 and min_dim < 8.5:
            warnings.append(
                f"U-Shaped Kitchen requires at least 8.5 ft clear width between opposite counters. "
                f"Current narrowest dimension is {min_dim:.1f} ft."
            )
        else:
            notes.append("Ample clearance for continuous U-countertop and corner carousel carousels.")

    elif design_id == "int_kit_04": # Parallel Galley Kitchen
        if min_dim > 0 and min_dim < 7.5:
            warnings.append(
                f"Parallel Galley Kitchen requires at least 7.5 ft clear width (two 2ft counters + 3.5ft walkway). "
                f"Current dimension is {min_dim:.1f} ft."
            )

    # 3. Dining space clearance
    if design_id == "int_din_02": # Luxury 8-seater dining
        area = room_area or (room_width * room_length)
        if area > 0 and area < 115.0:
            warnings.append(
                f"Luxury dining ensemble with credenza requires ~120 sq ft for adequate chair circulation. "
                f"Current room area is {area:.1f} sq ft."
            )

    # 4. Living room TV accent wall clearance
    if design_id in ("int_lr_01", "int_lr_02"):
        max_dim = max(room_width, room_length) if room_width > 0 and room_length > 0 else 0.0
        if max_dim > 0 and max_dim < 10.5:
            warnings.append(
                f"Full-feature TV console and accent wall paneling performs best with wall width >= 11 ft. "
                f"Maximum room dimension is {max_dim:.1f} ft."
            )

    is_compatible = len(warnings) == 0
    return {
        "compatible": is_compatible,
        "warnings": warnings,
        "notes": notes,
        "design_id": design_id,
        "design_name": design.name,
        "category": design.category,
        "style": design.style,
        "budget_tier": design.budget_tier
    }


def calculate_room_interior_cost(
    selection: RoomInteriorSelection,
    room_geom: Optional[Dict[str, Any]] = None
) -> Tuple[float, Dict[str, float]]:
    """
    Computes additional interior cost and an itemized breakdown for a selected room.
    Ensures zero double-counting against baseline civil/finishes estimates.
    """
    design = get_interior_design_by_id(selection.design_id)
    if not design:
        return 0.0, {}

    # Extract room dimensions
    area_sqft = selection.room_area_sqft
    width = 0.0
    length = 0.0
    if room_geom:
        width = float(room_geom.get("width", 0.0))
        length = float(room_geom.get("length", 0.0))
        if area_sqft <= 0:
            area_sqft = float(room_geom.get("area", width * length))
    
    if area_sqft <= 0:
        area_sqft = 120.0 # Conservative default room area in sq ft

    cost_params = design.cost_parameters or {}
    breakdown: Dict[str, float] = {
        "flooring_upgrade": 0.0,
        "wall_treatment": 0.0,
        "false_ceiling": 0.0,
        "lighting_and_electrical": 0.0,
        "modular_cabinetry_and_millwork": 0.0,
        "fixtures_and_accents": 0.0,
    }

    # 1. Flooring Upgrade Differential
    flooring_choice = selection.flooring_choice or ""
    diff_rate = 0.0
    if flooring_choice in FLOORING_UPGRADE_RATES:
        diff_rate = FLOORING_UPGRADE_RATES[flooring_choice]["differential"]
    elif "italian_marble" in design.flooring_default.lower() or "marble" in design.flooring_default.lower():
        diff_rate = 240.0 # Standard marble differential
    elif "wood" in design.flooring_default.lower() or "parquet" in design.flooring_default.lower() or "laminate" in design.flooring_default.lower():
        diff_rate = 95.0
    elif "terrazzo" in design.flooring_default.lower():
        diff_rate = 60.0
    
    breakdown["flooring_upgrade"] = round(diff_rate * area_sqft, 2)

    # 2. Wall Treatment / Accent Paneling
    wall_choice = selection.wall_finish_choice or ""
    if wall_choice in WALL_TREATMENT_RATES:
        panel_rate = WALL_TREATMENT_RATES[wall_choice]["rate"]
        # Default accent wall is ~10ft * 9ft = 90 sq ft or 30% of total wall area
        panel_area = 80.0
        breakdown["wall_treatment"] = round(panel_rate * panel_area, 2)
    elif "wall_paneling_rate_sqft" in cost_params:
        rate = float(cost_params["wall_paneling_rate_sqft"])
        area = float(cost_params.get("wall_paneling_area_sqft", 75.0))
        breakdown["wall_treatment"] = round(rate * area, 2)
    elif "wall_cladding_rate_sqft" in cost_params:
        rate = float(cost_params["wall_cladding_rate_sqft"])
        area = float(cost_params.get("wall_cladding_area_sqft", 80.0))
        breakdown["wall_treatment"] = round(rate * area, 2)
    elif "marble_slab_cost" in cost_params:
        breakdown["wall_treatment"] = float(cost_params["marble_slab_cost"])
    else:
        # Subtle default upgrade for velvet emulsion or wallpaper
        breakdown["wall_treatment"] = round(area_sqft * 35.0, 2) if design.budget_tier in ("Luxury", "Premium") else 0.0

    # 3. False Ceiling
    ceiling_option = selection.ceiling_option_id
    if ceiling_option:
        ceil_design = get_interior_design_by_id(ceiling_option)
        if ceil_design:
            c_params = ceil_design.cost_parameters
            rate = float(c_params.get("gypsum_rate_sqft", c_params.get("tray_ceiling_rate_sqft", 135.0)))
            breakdown["false_ceiling"] = round(rate * area_sqft, 2)
    elif "false_ceiling_rate_sqft" in cost_params:
        rate = float(cost_params["false_ceiling_rate_sqft"])
        breakdown["false_ceiling"] = round(rate * area_sqft, 2)
    elif "gypsum_rate_sqft" in cost_params:
        rate = float(cost_params["gypsum_rate_sqft"])
        breakdown["false_ceiling"] = round(rate * area_sqft, 2)

    # 4. Lighting & Electrical Fixtures
    points_count = selection.lighting_points_count
    point_cost = points_count * 1200.0 # ₹1,200 per specialized fixture/driver/point
    lump_lighting = float(cost_params.get("lighting_lump_sum", cost_params.get("lighting_fixtures_lump_sum", 0.0)))
    if lump_lighting == 0.0:
        if design.budget_tier == "Luxury":
            lump_lighting = 35000.0
        elif design.budget_tier == "Premium":
            lump_lighting = 20000.0
        elif design.budget_tier == "Mid-Range":
            lump_lighting = 12000.0
        else:
            lump_lighting = 5000.0
    breakdown["lighting_and_electrical"] = round(point_cost + lump_lighting, 2)

    # 5. Modular Cabinetry & Millwork
    category = design.category
    if category == "kitchen":
        # Calculate running feet of counter and modular overhead/base cabinets
        rft_rate = float(cost_params.get("modular_cabinets_rate_rft", 2800.0))
        # Estimate RFT from room dimensions: perimeter - opening allowance, or default ~16 RFT
        if width > 0 and length > 0:
            if design.id == "int_kit_03": # U-shaped: 3 sides
                rft = max(14.0, (width * 2 + length) - 4.0)
            elif design.id == "int_kit_04": # Parallel: 2 sides
                rft = max(12.0, (max(width, length) * 2) - 3.0)
            elif design.id == "int_kit_02": # L-shaped: 2 adjacent sides
                rft = max(12.0, (width + length) - 2.0)
            else:
                rft = max(10.0, (width + length) - 3.0)
        else:
            rft = 16.0
        cabinet_cost = rft * rft_rate
        countertop_cost = float(cost_params.get("quartz_countertop_rate_sqft", 380.0)) * (rft * 2.0)
        breakdown["modular_cabinetry_and_millwork"] = round(cabinet_cost + countertop_cost, 2)

    elif category in ("bedroom", "guest_room"):
        wardrobe_rate = float(cost_params.get("wardrobe_rate_sqft", 1650.0))
        wardrobe_width = float(cost_params.get("wardrobe_width_ft", 7.0))
        wardrobe_height = 9.0
        wardrobe_area = wardrobe_width * wardrobe_height
        wardrobe_cost = wardrobe_rate * wardrobe_area
        headboard_cost = float(cost_params.get("headboard_lump_sum", cost_params.get("bed_headboard_lump_sum", 25000.0)))
        study_cost = float(cost_params.get("study_unit_lump_sum", 0.0))
        breakdown["modular_cabinetry_and_millwork"] = round(wardrobe_cost + headboard_cost + study_cost, 2)

    elif category == "living_room":
        tv_unit = float(cost_params.get("tv_unit_lump_sum", cost_params.get("media_unit_lump_sum", 35000.0)))
        partition = float(cost_params.get("partition_lump_sum", cost_params.get("wooden_rafter_partition", 0.0)))
        breakdown["modular_cabinetry_and_millwork"] = round(tv_unit + partition, 2)

    elif category == "bathroom":
        vanity = float(cost_params.get("floating_vanity_lump_sum", cost_params.get("vanity_lump_sum", 28000.0)))
        shower_glass = float(cost_params.get("shower_glass_lump_sum", cost_params.get("glass_partition_lump_sum", 18000.0)))
        breakdown["modular_cabinetry_and_millwork"] = round(vanity + shower_glass, 2)

    elif category == "dining_room":
        crockery_unit = float(cost_params.get("crockery_unit_lump_sum", cost_params.get("credenza_lump_sum", 32000.0)))
        breakdown["modular_cabinetry_and_millwork"] = round(crockery_unit, 2)

    # 6. Fixtures & Accents (Sanitaryware upgrades, designer handles, mirrors, hardware)
    if category == "bathroom":
        breakdown["fixtures_and_accents"] = float(cost_params.get("fittings_differential_lump_sum", 22000.0))
    elif category == "kitchen":
        breakdown["fixtures_and_accents"] = float(cost_params.get("hardware_and_baskets_lump_sum", 28000.0))
    elif category == "living_room":
        breakdown["fixtures_and_accents"] = float(cost_params.get("accents_lump_sum", 15000.0))
    elif category in ("bedroom", "guest_room"):
        breakdown["fixtures_and_accents"] = float(cost_params.get("hardware_lump_sum", 12000.0))
    else:
        breakdown["fixtures_and_accents"] = 8000.0

    total_cost = sum(breakdown.values())
    return round(total_cost, 2), breakdown


def calculate_project_interior_costs(
    selections: Dict[str, RoomInteriorSelection],
    layout_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Computes total interior cost and itemized breakdown across all selected rooms in a project.
    Binds to real layout geometry if provided.
    """
    room_geoms: Dict[str, Dict[str, Any]] = {}
    
    if layout_data and "floors" in layout_data:
        for floor in layout_data["floors"]:
            for room in floor.get("rooms", []):
                r_id = room.get("id") or room.get("name")
                if r_id:
                    room_geoms[str(r_id)] = room

    updated_selections: Dict[str, RoomInteriorSelection] = {}
    total_project_cost = 0.0

    for room_id, sel in selections.items():
        geom = room_geoms.get(str(room_id)) or room_geoms.get(str(sel.room_id))
        
        # Hydrate room details if available
        if geom:
            if not sel.room_name:
                sel.room_name = geom.get("name", room_id)
            if not sel.room_type:
                sel.room_type = geom.get("type", "room")
            if sel.room_area_sqft <= 0:
                w = float(geom.get("width", 0))
                l = float(geom.get("length", 0))
                sel.room_area_sqft = float(geom.get("area", w * l))

        # Lookup design info
        design = get_interior_design_by_id(sel.design_id)
        if design:
            sel.design_name = design.name
            sel.category = design.category
            sel.style = design.style

        # Calculate cost
        add_cost, breakdown = calculate_room_interior_cost(sel, room_geom=geom)
        sel.additional_cost = add_cost
        sel.cost_breakdown = breakdown
        
        total_project_cost += add_cost
        updated_selections[str(room_id)] = sel

    return {
        "selections": updated_selections,
        "total_interior_cost": round(total_project_cost, 2),
        "room_count": len(updated_selections)
    }


def filter_catalog(
    category: Optional[str] = None,
    room_type: Optional[str] = None,
    budget_tier: Optional[str] = None,
    style: Optional[str] = None
) -> List[InteriorDesignOption]:
    """
    Filters the 32-design catalog by category, room type compatibility, budget tier, or style.
    """
    designs = get_all_interior_designs()
    filtered = []

    for d in designs:
        if category and d.category.lower() != category.lower():
            continue
        if budget_tier and d.budget_tier.lower() != budget_tier.lower():
            continue
        if style and style.lower() not in d.style.lower():
            continue
        if room_type:
            rt_norm = room_type.lower().replace(" ", "_")
            st_list = [t.lower().replace(" ", "_") for t in d.suitable_room_types]
            if "all" not in st_list and rt_norm not in st_list:
                # Check partial match (e.g. master_bedroom matches bedroom)
                if not any(st in rt_norm or rt_norm in st for st in st_list):
                    continue
        filtered.append(d)

    return filtered
