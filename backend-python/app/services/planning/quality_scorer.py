"""
Architectural Quality Scorer.
Computes an objective, 100-point Architectural Quality Score across 9 categories:
1. Requirement satisfaction (25)
2. Adjacency quality (15)
3. Circulation & connectivity (15)
4. Room proportions (10)
5. Area program & target compliance (10)
6. Building compactness (10)
7. Parking & site access (5)
8. Privacy zoning (5)
9. Daylight & exterior opportunities (5)
Total = 100.
"""
from typing import Dict, Any, List

def compute_architectural_quality_score(layout_data: Any, target_footprint: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Evaluates layout_data and returns a detailed breakdown and total score (0 - 100).
    """
    scores = {}
    floors = layout_data.floors if hasattr(layout_data, "floors") else []
    plot = layout_data.plot if hasattr(layout_data, "plot") else None

    # Collect rooms by floor
    rooms_by_floor: Dict[int, List[Any]] = {}
    all_rooms = []
    for fl in floors:
        lvl = fl.level
        rooms_by_floor[lvl] = fl.rooms
        all_rooms.extend(fl.rooms)

    indoor_rooms = [r for r in all_rooms if getattr(r, "space_category", "") != "outdoor" and r.type not in ["garden", "yard", "terrace", "balcony"]]

    # 1. Requirement Satisfaction (25 pts)
    types_present = set(r.type for r in all_rooms)
    req_score = 25.0
    essential_types = ["living_room", "kitchen", "staircase" if len(floors) > 1 else "living_room"]
    for et in essential_types:
        if et not in types_present:
            req_score -= 6.0
    has_bed = any("bedroom" in t for t in types_present)
    has_bath = any("bath" in t or "toilet" in t for t in types_present)
    if not has_bed:
        req_score -= 6.0
    if not has_bath:
        req_score -= 5.0
    scores["requirement_satisfaction"] = max(0.0, round(req_score, 1))

    # 2. Adjacency Quality (15 pts)
    adj_score = 0.0
    # Check touch between room pairs on same floor
    def rooms_touch(r1, r2):
        # r1 and r2 touch if horizontal or vertical boundary intersects
        r1_x2, r1_y2 = r1.x + r1.width, r1.y + r1.length
        r2_x2, r2_y2 = r2.x + r2.width, r2.y + r2.length
        h_touch = (abs(r1_x2 - r2.x) < 0.2 or abs(r2_x2 - r1.x) < 0.2) and (min(r1_y2, r2_y2) - max(r1.y, r2.y) >= 2.0)
        v_touch = (abs(r1_y2 - r2.y) < 0.2 or abs(r2_y2 - r1.y) < 0.2) and (min(r1_x2, r2_x2) - max(r1.x, r2.x) >= 2.0)
        return h_touch or v_touch

    # Kitchen - Dining
    kit = next((r for r in all_rooms if r.type == "kitchen"), None)
    din = next((r for r in all_rooms if r.type == "dining_room"), None)
    liv = next((r for r in all_rooms if r.type == "living_room"), None)
    foy = next((r for r in all_rooms if r.type == "foyer"), None)
    stair = next((r for r in all_rooms if r.type == "staircase"), None)
    mbed = next((r for r in all_rooms if r.type == "master_bedroom"), None)

    if kit and din and rooms_touch(kit, din):
        adj_score += 5.0
    elif kit and liv and rooms_touch(kit, liv):
        adj_score += 3.0

    if liv and din and rooms_touch(liv, din):
        adj_score += 3.0

    if foy and liv and rooms_touch(foy, liv):
        adj_score += 2.0
    elif not foy:
        adj_score += 2.0  # N/A

    # Master bed - bath
    mbed_fl = getattr(mbed, "floor_level", 1) if mbed else 1
    mbed_baths = [r for r in all_rooms if ("bath" in r.type or "toilet" in r.type) and getattr(r, "floor_level", 1) == mbed_fl]
    if mbed and any(rooms_touch(mbed, b) for b in mbed_baths):
        adj_score += 3.0
    elif mbed:
        adj_score += 1.5

    # Stair touches hub
    if stair:
        hubs = [r for r in all_rooms if r.type in ["living_room", "dining_room", "corridor", "foyer"]]
        if any(rooms_touch(stair, h) for h in hubs):
            adj_score += 2.0
    else:
        adj_score += 2.0
    scores["adjacency_quality"] = min(15.0, round(adj_score, 1))

    # 3. Circulation & Connectivity (15 pts)
    circ_score = 15.0
    metadata = getattr(layout_data, "metadata", {}) or {}
    if not metadata.get("circulation_valid", True):
        circ_score -= 6.0
    if metadata.get("isolated_rooms"):
        circ_score -= len(metadata.get("isolated_rooms")) * 2.0
    scores["circulation_and_connectivity"] = max(0.0, min(15.0, round(circ_score, 1)))

    # 4. Room Proportions (10 pts)
    prop_score = 10.0
    for r in indoor_rooms:
        if r.width > 0 and r.length > 0:
            ar = max(r.width / r.length, r.length / r.width)
            if ar > 2.2:
                prop_score -= 2.0
            elif ar > 1.8:
                prop_score -= 0.5
    scores["room_proportions"] = max(2.0, min(10.0, round(prop_score, 1)))

    # 5. Area Program & Target Compliance (10 pts)
    target_score = 10.0
    fp = getattr(plot, "building_footprint", None)
    if fp and target_footprint:
        actual_fp_area = fp.get("width", 0) * fp.get("length", 0)
        target_area = target_footprint.get("target_area", 1)
        ratio = actual_fp_area / target_area if target_area > 0 else 1.0
        if 0.85 <= ratio <= 1.25:
            target_score = 10.0
        elif 0.70 <= ratio <= 1.40:
            target_score = 7.5
        elif 0.55 <= ratio <= 1.60:
            target_score = 5.0
        else:
            target_score = 2.0
    scores["area_program_compliance"] = round(target_score, 1)

    # 6. Building Compactness (10 pts)
    comp_score = 8.0
    gf_rooms = rooms_by_floor.get(0, [])
    gf_indoor = [r for r in gf_rooms if getattr(r, "space_category", "") != "outdoor" and r.type not in ["garden", "yard", "terrace", "balcony"]]
    if fp and gf_indoor:
        fp_area = fp.get("width", 0) * fp.get("length", 0)
        gf_used = sum(r.width * r.length for r in gf_indoor)
        if fp_area > 0:
            util = gf_used / fp_area
            if util >= 0.80:
                comp_score = 10.0
            elif util >= 0.72:
                comp_score = 8.5
            elif util >= 0.60:
                comp_score = 6.0
            else:
                comp_score = 3.0
    scores["building_compactness"] = round(comp_score, 1)

    # 7. Parking & Site Access (5 pts)
    park_score = 5.0
    has_parking = any(r.type in ["parking", "garage"] for r in all_rooms)
    gates = getattr(plot, "gates", []) or []
    has_vg = any(g.get("type") == "vehicle" for g in gates)
    if has_parking and not has_vg:
        park_score = 1.0
    scores["parking_and_site_access"] = round(park_score, 1)

    # 8. Privacy Zoning (5 pts)
    priv_score = 5.0
    # Check if bedrooms are separated from main living entrance
    if len(floors) > 1:
        # G+1: having bedrooms upstairs provides natural privacy
        priv_score = 5.0
    else:
        priv_score = 4.5
    scores["privacy_zoning"] = round(priv_score, 1)

    # 9. Daylight & Window Opportunities (5 pts)
    day_score = 4.5
    if len(getattr(floors[0], "windows", [])) >= 3:
        day_score = 5.0
    scores["daylight_opportunities"] = round(day_score, 1)

    total_score = round(sum(scores.values()), 1)
    return {
        "total_score": total_score,
        "max_score": 100.0,
        "percentage": total_score,
        "passed_threshold": total_score >= 70.0,
        "breakdown": scores
    }
