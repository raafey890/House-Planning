"""
Architectural Area Program and Pre-Planning Engine for Floor Planning.
Validates requirements against buildable boundaries, computes target footprint,
and distributes spaces across floors based on architectural zoning principles.
"""
import math
from typing import Dict, Any, List, Tuple
from app.services.planning.room_catalog import get_room_specs

class AreaProgramError(Exception):
    pass

def calculate_target_footprint(
    plot_w: float,
    plot_l: float,
    build_w: float,
    build_l: float,
    num_floors: int,
    gf_net_pref_area: float
) -> Dict[str, float]:
    """
    Computes an architectural target footprint (dimensions and area) based on
    the requested room program, circulation & wall allowances, and plot scale.
    Prevents both severe compression (tiny house in huge yard) and 100% over-building.
    """
    plot_area = plot_w * plot_l
    build_area = build_w * build_l

    # Gross factor: 15% circulation + 12% structural walls
    gross_factor = 1.27
    raw_target_area = gf_net_pref_area * gross_factor

    # Recommended coverage range based on plot scale:
    # Large plots (>= 3200 sq ft, like 50x80): 40% - 55% plot coverage
    # Medium plots (2000-3200 sq ft): 48% - 65% plot coverage
    # Compact plots (< 2000 sq ft, like 30x40): 55% - 75% plot coverage
    if plot_area >= 3200.0:
        min_cov = 0.38
        max_cov = 0.55
    elif plot_area >= 2000.0:
        min_cov = 0.45
        max_cov = 0.65
    else:
        min_cov = 0.52
        max_cov = 0.75

    min_footprint_area = max(raw_target_area * 0.9, plot_area * min_cov)
    max_footprint_area = min(build_area * 0.90, plot_area * max_cov)

    target_area = max(min_footprint_area, min(max_footprint_area, raw_target_area))
    target_area = min(target_area, build_area * 0.92)

    # Determine balanced aspect ratio for footprint
    # Buildable aspect ratio
    build_ar = build_w / build_l
    # Standard residential massing aspect ratio: width is typically 0.65 - 0.85 of length
    target_ar = max(0.60, min(0.85, build_ar))

    # Derive target width and length
    raw_w = math.sqrt(target_area * target_ar)
    # Clamp target width to leave sensible side setbacks / driveway
    if plot_w >= 45.0:
        # On wide plots, leave at least 8-10 ft on one side for driveway/passage
        max_allowed_w = build_w - 6.0
    else:
        max_allowed_w = build_w - 2.0

    target_w = max(min(raw_w, max_allowed_w), min(build_w * 0.65, 20.0))
    target_l = target_area / target_w

    # Clamp target length to leave front & rear yards
    if plot_l >= 60.0:
        max_allowed_l = build_l - 12.0  # Leaves at least 12-16 ft for front lawn/driveway & rear yard
    else:
        max_allowed_l = build_l - 3.0

    target_l = max(min(target_l, max_allowed_l), min(build_l * 0.60, 24.0))
    target_w = round(min(target_w, build_w), 1)
    target_l = round(min(target_l, build_l), 1)
    target_area = round(target_w * target_l, 1)

    return {
        "target_width": target_w,
        "target_length": target_l,
        "target_area": target_area,
        "target_plot_coverage_pct": round((target_area / plot_area) * 100, 1),
        "target_build_coverage_pct": round((target_area / build_area) * 100, 1),
    }

def build_area_program(context: Dict[str, Any], raw_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalizes requirements, validates capacity against plot buildable area,
    computes target architectural footprint, and returns a structured floor-by-floor room allocation.
    """
    plot_w = int(context.get("plot_width", 30))
    plot_l = int(context.get("plot_length", 40))
    plot_area = plot_w * plot_l

    # Determine number of floors from context or requirements
    max_req_floor = max((r.get("floor_level", 0) for r in raw_requirements if isinstance(r.get("floor_level"), int)), default=0)
    ctx_floors = context.get("floors") or context.get("number_of_floors")
    num_floors = int(ctx_floors) if ctx_floors else max(1, max_req_floor + 1)
    
    facing = (context.get("facing", "south") or "south").lower()
    setbacks = context.get("setbacks", {"front": 4, "rear": 4, "left": 3, "right": 3})

    # Buildable dimensions
    build_w = plot_w - (int(setbacks.get("left", 3)) + int(setbacks.get("right", 3)))
    build_l = plot_l - (int(setbacks.get("front", 4)) + int(setbacks.get("rear", 4)))
    buildable_footprint = build_w * build_l
    total_buildable_capacity = buildable_footprint * num_floors

    if build_w < 12 or build_l < 12:
        raise AreaProgramError(
            f"Plot dimensions ({plot_w}x{plot_l} ft) with setbacks yield a buildable area of only {build_w}x{build_l} ft, which is too small for residential planning."
        )

    # Normalize raw requirements
    normalized_rooms = []
    req_items = raw_requirements if isinstance(raw_requirements, list) else [raw_requirements] if raw_requirements else []

    # Check for parking in requirements or context
    has_parking_req = False

    for req in req_items:
        if not isinstance(req, dict):
            continue

        # Format 1: Explicit {"room_type": "...", "count": 1, "floor_level": ...}
        if "room_type" in req:
            rtype = req.get("room_type", "").lower()
            if not rtype:
                continue
            count = int(req.get("count", 1))
            floor_pref = req.get("floor_level", None)
            specs = get_room_specs(rtype, plot_area)
            if rtype in ["parking", "garage"]:
                has_parking_req = True
            for _ in range(count):
                normalized_rooms.append({
                    "type": rtype,
                    "floor_pref": floor_pref,
                    "specs": specs,
                    "min_area": specs["min_area"],
                    "pref_area": specs["pref_area"]
                })
        else:
            # Format 2: DB columns format (e.g. {"bedrooms": 3, "bathrooms": 2, ...})
            bed_count = int(req.get("bedrooms", 0))
            if bed_count > 0:
                # 1 master bedroom (upper floor for G+1) + remaining normal bedrooms
                master_specs = get_room_specs("master_bedroom", plot_area)
                normalized_rooms.append({
                    "type": "master_bedroom",
                    "floor_pref": 1 if num_floors > 1 else 0,
                    "specs": master_specs,
                    "min_area": master_specs["min_area"],
                    "pref_area": master_specs["pref_area"]
                })
                bed_specs = get_room_specs("bedroom", plot_area)
                for _ in range(bed_count - 1):
                    normalized_rooms.append({
                        "type": "bedroom",
                        "floor_pref": None,
                        "specs": bed_specs,
                        "min_area": bed_specs["min_area"],
                        "pref_area": bed_specs["pref_area"]
                    })

            for _ in range(int(req.get("bathrooms", 0))):
                b_specs = get_room_specs("bathroom", plot_area)
                normalized_rooms.append({
                    "type": "bathroom", "floor_pref": None,
                    "specs": b_specs, "min_area": b_specs["min_area"], "pref_area": b_specs["pref_area"]
                })

            for _ in range(int(req.get("kitchens", 0))):
                k_specs = get_room_specs("kitchen", plot_area)
                normalized_rooms.append({
                    "type": "kitchen", "floor_pref": 0,
                    "specs": k_specs, "min_area": k_specs["min_area"], "pref_area": k_specs["pref_area"]
                })

            for _ in range(int(req.get("living_rooms", 0))):
                l_specs = get_room_specs("living_room", plot_area)
                normalized_rooms.append({
                    "type": "living_room", "floor_pref": 0,
                    "specs": l_specs, "min_area": l_specs["min_area"], "pref_area": l_specs["pref_area"]
                })

            for _ in range(int(req.get("dining_rooms", 0))):
                d_specs = get_room_specs("dining_room", plot_area)
                normalized_rooms.append({
                    "type": "dining_room", "floor_pref": 0,
                    "specs": d_specs, "min_area": d_specs["min_area"], "pref_area": d_specs["pref_area"]
                })

            park_count = int(req.get("parking_spaces") or req.get("parking") or 0)
            if park_count > 0:
                has_parking_req = True
                p_specs = get_room_specs("parking", plot_area)
                for _ in range(park_count):
                    normalized_rooms.append({
                        "type": "parking", "floor_pref": 0,
                        "specs": p_specs, "min_area": p_specs["min_area"], "pref_area": p_specs["pref_area"]
                    })

            for _ in range(int(req.get("balconies", 0))):
                bal_specs = get_room_specs("balcony", plot_area)
                normalized_rooms.append({
                    "type": "balcony", "floor_pref": 1 if num_floors > 1 else 0,
                    "specs": bal_specs, "min_area": bal_specs["min_area"], "pref_area": bal_specs["pref_area"]
                })

            if req.get("pooja_room"):
                pj_specs = get_room_specs("pooja_room", plot_area)
                normalized_rooms.append({
                    "type": "pooja_room", "floor_pref": 0,
                    "specs": pj_specs, "min_area": pj_specs["min_area"], "pref_area": pj_specs["pref_area"]
                })

            if req.get("study_room"):
                st_specs = get_room_specs("study_room", plot_area)
                normalized_rooms.append({
                    "type": "study_room", "floor_pref": 1 if num_floors > 1 else 0,
                    "specs": st_specs, "min_area": st_specs["min_area"], "pref_area": st_specs["pref_area"]
                })

            if req.get("utility_room"):
                ut_specs = get_room_specs("utility_room", plot_area)
                normalized_rooms.append({
                    "type": "utility_room", "floor_pref": 0,
                    "specs": ut_specs, "min_area": ut_specs["min_area"], "pref_area": ut_specs["pref_area"]
                })

            if req.get("guest_room"):
                g_specs = get_room_specs("guest_room", plot_area)
                normalized_rooms.append({
                    "type": "guest_room", "floor_pref": 0,
                    "specs": g_specs, "min_area": g_specs["min_area"], "pref_area": g_specs["pref_area"]
                })

    # Context fallback
    if not normalized_rooms:
        if context.get("bedrooms"):
            bed_count = int(context.get("bedrooms"))
            master_specs = get_room_specs("master_bedroom", plot_area)
            normalized_rooms.append({
                "type": "master_bedroom", "floor_pref": 1 if num_floors > 1 else 0,
                "specs": master_specs, "min_area": master_specs["min_area"], "pref_area": master_specs["pref_area"]
            })
            bed_specs = get_room_specs("bedroom", plot_area)
            for _ in range(bed_count - 1):
                normalized_rooms.append({
                    "type": "bedroom", "floor_pref": None,
                    "specs": bed_specs, "min_area": bed_specs["min_area"], "pref_area": bed_specs["pref_area"]
                })

        if context.get("bathrooms"):
            for _ in range(int(context.get("bathrooms"))):
                b_specs = get_room_specs("bathroom", plot_area)
                normalized_rooms.append({
                    "type": "bathroom", "floor_pref": None,
                    "specs": b_specs, "min_area": b_specs["min_area"], "pref_area": b_specs["pref_area"]
                })

        if context.get("kitchens"):
            for _ in range(int(context.get("kitchens"))):
                k_specs = get_room_specs("kitchen", plot_area)
                normalized_rooms.append({
                    "type": "kitchen", "floor_pref": 0,
                    "specs": k_specs, "min_area": k_specs["min_area"], "pref_area": k_specs["pref_area"]
                })

        if context.get("living_rooms"):
            for _ in range(int(context.get("living_rooms"))):
                l_specs = get_room_specs("living_room", plot_area)
                normalized_rooms.append({
                    "type": "living_room", "floor_pref": 0,
                    "specs": l_specs, "min_area": l_specs["min_area"], "pref_area": l_specs["pref_area"]
                })

    # Also check parking from context if not yet added
    if not has_parking_req and (context.get("parking_spaces") or context.get("parking")):
        p_count = int(context.get("parking_spaces") or context.get("parking") or 1)
        p_specs = get_room_specs("parking", plot_area)
        for _ in range(p_count):
            normalized_rooms.append({
                "type": "parking", "floor_pref": 0,
                "specs": p_specs, "min_area": p_specs["min_area"], "pref_area": p_specs["pref_area"]
            })
            has_parking_req = True

    # Automatic essential living spaces:
    # 1. Living room -> add dining room if missing and plot >= 1000 sq ft
    has_living = any(r["type"] == "living_room" for r in normalized_rooms)
    has_dining = any(r["type"] == "dining_room" for r in normalized_rooms)
    if has_living and not has_dining and plot_area >= 1000:
        d_specs = get_room_specs("dining_room", plot_area)
        normalized_rooms.append({
            "type": "dining_room", "floor_pref": 0,
            "specs": d_specs, "min_area": d_specs["min_area"], "pref_area": d_specs["pref_area"]
        })

    # 2. Entrance Foyer: for generous residential plots (>= 2400 sq ft, like 50x80)
    has_foyer = any(r["type"] == "foyer" for r in normalized_rooms)
    if has_living and not has_foyer and plot_area >= 2400:
        f_specs = get_room_specs("foyer", plot_area)
        normalized_rooms.append({
            "type": "foyer", "floor_pref": 0,
            "specs": f_specs, "min_area": f_specs["min_area"], "pref_area": f_specs["pref_area"]
        })

    # Strict check: ensure habitable rooms exist
    habitable_count = sum(1 for r in normalized_rooms if r["type"] not in ["staircase", "corridor", "foyer"])
    if habitable_count == 0:
        raise AreaProgramError("No habitable rooms were specified in the requirements. Cannot generate an empty floor plan.")

    # Multi-floor staircase allocation
    has_stairs = any(r["type"] == "staircase" for r in normalized_rooms)
    if num_floors > 1 and not has_stairs:
        stair_spec = get_room_specs("staircase", plot_area)
        for fl in range(num_floors):
            normalized_rooms.append({
                "type": "staircase",
                "floor_pref": fl,
                "specs": stair_spec,
                "min_area": stair_spec["min_area"],
                "pref_area": stair_spec["pref_area"]
            })

    # ── ARCHITECTURAL FLOOR DISTRIBUTION ────────────────────────────────
    ground_rooms = []
    upper_rooms = {fl: [] for fl in range(1, num_floors)}

    # Dedicated stairs routing
    stairs = [r for r in normalized_rooms if r["type"] == "staircase"]
    for st in stairs:
        fl = st.get("floor_pref", 0)
        if fl == 0:
            ground_rooms.append(st)
        elif fl in upper_rooms:
            upper_rooms[fl].append(st)
        else:
            ground_rooms.append(st)

    # Distribute non-stair rooms
    for r in normalized_rooms:
        if r["type"] == "staircase":
            continue

        fl = r.get("floor_pref")
        if fl is not None:
            if fl == 0:
                ground_rooms.append(r)
            elif fl in upper_rooms:
                upper_rooms[fl].append(r)
            else:
                ground_rooms.append(r)
        else:
            rtype = r["type"]
            # Ground floor zoning: entrance, public living, dining, kitchen, services, parking
            if rtype in ["living_room", "dining_room", "kitchen", "parking", "garage", "foyer", "pooja_room", "utility_room"]:
                ground_rooms.append(r)
            elif "bedroom" in rtype:
                gf_has_bed = any("bedroom" in x["type"] for x in ground_rooms)
                total_beds = sum(1 for x in normalized_rooms if "bedroom" in x["type"])
                gf_current_min = sum(x["specs"]["min_area"] for x in ground_rooms)
                # On multi-floor houses:
                # If 3+ bedrooms are requested AND ground floor capacity allows, place 1 bedroom on ground floor.
                # If 2 or fewer bedrooms are requested, place bedrooms upstairs to keep ground floor spacious for living/parking.
                can_fit_on_gf = (gf_current_min + r["specs"]["min_area"] <= buildable_footprint * 0.72)
                if not gf_has_bed and num_floors > 1 and total_beds >= 3 and can_fit_on_gf:
                    ground_rooms.append(r)
                elif num_floors > 1:
                    upper_rooms[1].append(r)
                else:
                    ground_rooms.append(r)
            elif "bath" in rtype or "toilet" in rtype:
                # If ground has no bathroom yet, give one to ground
                gf_has_bath = any("bath" in x["type"] or "toilet" in x["type"] for x in ground_rooms)
                if not gf_has_bath:
                    ground_rooms.append(r)
                elif num_floors > 1:
                    upper_rooms[1].append(r)
                else:
                    ground_rooms.append(r)
            else:
                if num_floors > 1 and rtype in ["balcony", "study_room"]:
                    upper_rooms[1].append(r)
                else:
                    ground_rooms.append(r)

    # Ensure corridor / circulation hub exists on upper floors
    for fl in range(1, num_floors):
        upper_bed_count = sum(1 for r in upper_rooms[fl] if "bedroom" in r["type"])
        has_corridor = any(r["type"] == "corridor" for r in upper_rooms[fl])
        if upper_bed_count >= 1 and not has_corridor:
            corridor_spec = get_room_specs("corridor", plot_area)
            upper_rooms[fl].append({
                "type": "corridor",
                "floor_pref": fl,
                "specs": corridor_spec,
                "min_area": corridor_spec["min_area"],
                "pref_area": corridor_spec["pref_area"]
            })

    floors_program = {0: ground_rooms}
    for fl in range(1, num_floors):
        floors_program[fl] = upper_rooms[fl]

    # Calculate net preferred area for Ground Floor
    gf_net_pref_area = sum(r["specs"]["pref_area"] for r in ground_rooms)

    # Compute target footprint metrics
    target_fp = calculate_target_footprint(
        plot_w=plot_w,
        plot_l=plot_l,
        build_w=build_w,
        build_l=build_l,
        num_floors=num_floors,
        gf_net_pref_area=gf_net_pref_area
    )

    # Area program totals
    total_min_required = sum(r["specs"]["min_area"] for r in normalized_rooms)
    total_pref_required = sum(r["specs"]["pref_area"] for r in normalized_rooms)

    return {
        "plot_width": plot_w,
        "plot_length": plot_l,
        "facing": facing,
        "setbacks": setbacks,
        "buildable_width": build_w,
        "buildable_length": build_l,
        "buildable_area": buildable_footprint,
        "floors_program": floors_program,
        "target_footprint": target_fp,
        "area_program_metrics": {
            "total_min_required_sqft": total_min_required,
            "total_pref_required_sqft": total_pref_required,
            "circulation_allowance_gf": round(gf_net_pref_area * 0.15, 1),
            "wall_allowance_gf": round(gf_net_pref_area * 0.12, 1),
            "target_gf_built_area": target_fp["target_area"],
            "target_footprint_width": target_fp["target_width"],
            "target_footprint_length": target_fp["target_length"],
        }
    }
