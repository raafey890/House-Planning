"""Floor-plan metrics calculator for Phase 6C.5.

Computes per-floor and whole-layout area metrics so the frontend can
display utilization data and the validator can reference concrete numbers.
"""
from typing import Dict, Any, List
from app.models.layout import LayoutData


# Room types that map to each metric bucket
_CIRCULATION_TYPES = {"corridor", "hallway", "circulation", "foyer", "stairs", "staircase"}
_PARKING_TYPES = {"parking", "garage"}
_TERRACE_TYPES = {"terrace", "courtyard", "garden", "balcony", "yard"}
_UTILITY_TYPES = {"utility", "store", "laundry"}
_SETBACK_TYPES = {"setback"}

def compute_floor_metrics(layout: LayoutData) -> Dict[str, Any]:
    plot_area = layout.plot.width * layout.plot.length
    buildable_area = layout.plot.buildable_boundary.width * layout.plot.buildable_boundary.length
    
    footprint_area = 0.0
    constructed_footprint_area = 0.0
    if layout.plot.building_footprint:
        footprint_area = layout.plot.building_footprint["width"] * layout.plot.building_footprint["length"]
        constructed_footprint_area = layout.plot.building_footprint.get("constructed_area", footprint_area)

    floor_metrics: List[Dict[str, Any]] = []
    totals = {
        "room_area": 0.0,
        "circulation_area": 0.0,
        "parking_area": 0.0,
        "terrace_area": 0.0,
        "utility_area": 0.0,
        "setback_area": 0.0,
        "indoor_room_area": 0.0
    }

    for floor in layout.floors:
        fm: Dict[str, Any] = {"level": floor.level}
        circ = 0.0
        park = 0.0
        terr = 0.0
        util = 0.0
        setb = 0.0
        indoor = 0.0

        # Filter strictly genuine indoor rooms
        indoor_rooms = [
            r for r in floor.rooms
            if (r.space_category != "outdoor" and (r.type or "").lower() not in _TERRACE_TYPES and (r.type or "").lower() not in _PARKING_TYPES)
        ]
        outdoor_in_rooms = [
            r for r in floor.rooms
            if (r.space_category == "outdoor" or (r.type or "").lower() in _TERRACE_TYPES or (r.type or "").lower() in _PARKING_TYPES)
        ]

        for room in indoor_rooms:
            area = room.width * room.length
            rtype = (room.type or "").lower()
            if rtype in _CIRCULATION_TYPES:
                circ += area
                indoor += area
            elif rtype in _UTILITY_TYPES:
                util += area
                indoor += area
            else:
                indoor += area

        # Account for outdoor_areas (terraces, balconies, parking, yards)
        all_outdoor = list(getattr(floor, "outdoor_areas", [])) + outdoor_in_rooms
        for out in all_outdoor:
            o_area = out.area if getattr(out, "area", 0) > 0 else (out.width * out.length)
            o_type = (out.type or "").lower()
            if o_type in _PARKING_TYPES:
                park += o_area
            elif o_type in ["terrace", "roof", "balcony"]:
                terr += o_area
            elif o_type in ["yard", "garden"]:
                setb += o_area

        fm["indoor_room_count"] = len(indoor_rooms)
        fm["outdoor_space_count"] = len(all_outdoor)
        fm["total_room_area"] = round(indoor, 1)
        fm["circulation_area"] = round(circ, 1)
        fm["parking_area"] = round(park, 1)
        fm["terrace_area"] = round(terr, 1)
        fm["utility_area"] = round(util, 1)
        fm["indoor_room_area"] = round(indoor, 1)

        totals["room_area"] += indoor
        totals["circulation_area"] += circ
        totals["parking_area"] += park
        totals["terrace_area"] += terr
        totals["utility_area"] += util
        totals["setback_area"] += setb
        totals["indoor_room_area"] += indoor

        floor_metrics.append(fm)

    # Round totals
    for k in totals:
        totals[k] = round(totals[k], 1)

    # Utilization metrics based on constructed footprint
    cov_ref_area = constructed_footprint_area if constructed_footprint_area > 0 else footprint_area
    plot_coverage_pct = (cov_ref_area / plot_area * 100) if plot_area > 0 else 0
    buildable_coverage_pct = (cov_ref_area / buildable_area * 100) if buildable_area > 0 else 0
    bounding_coverage_pct = (footprint_area / plot_area * 100) if plot_area > 0 else 0
    
    num_floors = len(layout.floors) or 1
    total_constructed_mass = cov_ref_area * num_floors
    internal_building_utilization_pct = (totals["indoor_room_area"] / total_constructed_mass * 100) if total_constructed_mass > 0 else 0
    
    # Ground classified plot = constructed footprint + site areas (yards, gardens, parking)
    site_area_sum = sum(y.get("area", 0) for y in getattr(layout.plot, "site_areas", []))
    ground_accounted = cov_ref_area + site_area_sum
    classified_plot_pct = min(100.0, (ground_accounted / plot_area * 100)) if plot_area > 0 else 0

    totals["plot_coverage_pct"] = round(plot_coverage_pct, 1)
    totals["buildable_coverage_pct"] = round(buildable_coverage_pct, 1)
    totals["bounding_coverage_pct"] = round(bounding_coverage_pct, 1)
    totals["internal_building_utilization_pct"] = round(internal_building_utilization_pct, 1)
    totals["classified_plot_pct"] = round(classified_plot_pct, 1)
    totals["utilization_pct"] = round(classified_plot_pct, 1)
    totals["constructed_footprint_area"] = round(cov_ref_area, 1)
    totals["bounding_footprint_area"] = round(footprint_area, 1)

    # Metric sanity checks: ensure plan is not just an empty plot classified as garden
    totals["building_footprint_area"] = round(footprint_area, 1)
    totals["outdoor_site_area"] = round(totals["terrace_area"] + totals["parking_area"], 1)
    totals["is_valid_residential"] = (totals["indoor_room_area"] >= 200.0)

    # Connectivity & Architectural Adjacency metrics
    from app.validators.connectivity_validator import ConnectivityValidator
    conn_report = ConnectivityValidator.validate_connectivity(layout)
    
    # Count rooms with windows
    rooms_with_windows = set()
    for floor in layout.floors:
        for w in floor.windows:
            if getattr(w, "room_id", None):
                rooms_with_windows.add(w.room_id)

    total_indoor_rooms = sum(
        1 for floor in layout.floors for r in floor.rooms
        if r.type not in ["parking", "garage", "terrace", "balcony", "garden"]
    )

    quality_metrics = {
        "circulation_valid": conn_report["circulation_valid"],
        "isolated_room_count": len(conn_report["isolated_rooms"]),
        "isolated_rooms": conn_report["isolated_rooms"],
        "required_adjacencies": conn_report["required_adjacencies"],
        "stair_connectivity": conn_report["stair_connectivity"],
        "main_entrance_valid": conn_report["main_entrance_valid"],
        "rooms_with_external_windows": len(rooms_with_windows),
        "total_indoor_rooms": total_indoor_rooms,
        "adjacency_score": 100.0 if conn_report["circulation_valid"] and not conn_report["isolated_rooms"] else 70.0
    }

    return {
        "buildable_area": round(buildable_area, 1),
        "floors": floor_metrics,
        "totals": totals,
        "quality": quality_metrics
    }
