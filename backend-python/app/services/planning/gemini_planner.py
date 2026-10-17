"""
Hybrid Gemini Architectural Planner.

Pipeline:
  1. Build architectural context (plot, setbacks, buildable, requirements)
  2. Call Gemini with structured JSON prompt
  3. Parse response into LayoutData schema
  4. Run deterministic validation (GeometryValidator, circulation)
  5. Run post-processor for walls, doors, windows, site elements
  6. Return validated LayoutData

Falls back to deterministic planner on ANY Gemini failure.
Never logs API keys, JWTs, prompts, or user data.
"""
import logging
import time
import json
import copy
from typing import Dict, Any, List, Optional, Tuple

from app.models.layout import (
    LayoutData, Plot, Floor, Room, Wall, Door, Window, Stair,
    Point2D, Circulation, BoundingBox, Setbacks
)
from app.services.planning.room_catalog import get_room_specs

logger = logging.getLogger("planning.gemini_planner")


class GeminiPlannerError(Exception):
    """Raised when Gemini planning fails and fallback should be used."""
    pass


def _build_gemini_architectural_prompt(context: Dict[str, Any], requirements: List[Dict[str, Any]]) -> str:
    """
    Build a detailed architectural planning prompt for Gemini.
    Instructs Gemini to act as an architectural planner and return strict JSON.
    """
    plot_w = context.get("plot_width", 30)
    plot_l = context.get("plot_length", 40)
    facing = (context.get("facing", "south") or "south").lower()
    num_floors = int(context.get("floors") or context.get("number_of_floors") or 1)
    style = context.get("design_style", "Modern")

    setbacks = context.get("setbacks", {"front": 4, "rear": 4, "left": 3, "right": 3})
    front_sb = int(setbacks.get("front", 4))
    rear_sb = int(setbacks.get("rear", 4))
    left_sb = int(setbacks.get("left", 3))
    right_sb = int(setbacks.get("right", 3))
    build_w = plot_w - left_sb - right_sb
    build_l = plot_l - front_sb - rear_sb

    # Parse requirements into human-readable list
    req_summary = _parse_requirements_summary(requirements, context)

    prompt = f"""You are an expert residential architect. Generate a complete, practical floor plan layout.

PROJECT SPECIFICATIONS:
- Plot: {plot_w} x {plot_l} ft
- Facing: {facing.upper()} (front side / road side)
- Floors: {num_floors} ({"Ground Floor only" if num_floors == 1 else "Ground + " + str(num_floors - 1) + " Upper"})
- Style: {style}
- Setbacks: Front={front_sb}ft, Rear={rear_sb}ft, Left={left_sb}ft, Right={right_sb}ft
- Buildable Area: {build_w} x {build_l} ft = {build_w * build_l} sq ft

ROOM REQUIREMENTS:
{req_summary}

COORDINATE SYSTEM:
- Origin (0,0) is bottom-left of plot
- X increases rightward, Y increases upward
- All rooms must be placed within the buildable boundary:
  x >= {left_sb}, y >= {front_sb}
  x + width <= {plot_w - right_sb}, y + length <= {plot_l - rear_sb}

ARCHITECTURAL PLANNING RULES:
1. HOUSE FIRST: Design the building to fill 55-80% of the buildable area. Do NOT create a tiny house.
2. Place rooms efficiently with minimal wasted space inside the building envelope.
3. Living room and kitchen near the entrance (front side).
4. Bedrooms in private zones (rear of ground floor or upper floors).
5. Kitchen adjacent to dining room.
6. Bathrooms near bedrooms.
7. Staircase centrally located and aligned across all floors (same x,y,width,length).
8. For {facing.upper()}-facing plots: entrance/living room should face the {facing} side.
9. Room aspect ratios must be between 1:1 and 2.2:1.
10. Minimum room sizes: Bedroom 120sqft, Bathroom 35sqft, Kitchen 80sqft, Living 150sqft.
11. Every room must have positive width and length.
12. Rooms must NOT overlap.
13. All rooms must fit within buildable boundary.

WALL RULES:
- Exterior walls: type="exterior", thickness=0.75
- Interior walls: type="interior", thickness=0.5
- Generate walls for every room edge

DOOR RULES:
- One main entrance door: type="main_entrance", width=3.5, on the {facing} side
- Interior doors: type="swing", width=2.5-3.0, between connected rooms
- Door position is the center point of the door on the wall

WINDOW RULES:
- Windows on exterior walls only, type="sliding", width=3.0-4.0
- At least 1 window per bedroom and living room

STAIR RULES (if multi-floor):
- Staircase: width=8ft, length=12ft minimum
- Same position on every floor (vertically aligned)
- Ground floor direction="up", upper floors direction="down"

UPPER FLOOR RULES:
- Upper floor rooms go within the SAME building footprint as ground floor
- Any area within the building footprint not used by rooms becomes "terrace" (type="terrace")
- Terrace is outdoor space on the roof slab

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact structure:
{{
  "schema_version": "1.0",
  "units": "ft",
  "plot": {{
    "width": {plot_w},
    "length": {plot_l},
    "facing": "{facing}",
    "origin": {{"x": 0, "y": 0}},
    "buildable_boundary": {{"width": {build_w}, "length": {build_l}}},
    "setbacks": {{"front": {front_sb}, "back": {rear_sb}, "left": {left_sb}, "right": {right_sb}}}
  }},
  "floors": [
    {{
      "level": 0,
      "name": "Ground Floor",
      "elevation": 0.0,
      "rooms": [
        {{
          "id": "gf_living_room_1",
          "type": "living_room",
          "label": "Living Room",
          "x": <float>,
          "y": <float>,
          "width": <float>,
          "length": <float>,
          "area": <float>,
          "rotation": 0.0,
          "metadata": {{}}
        }}
      ],
      "walls": [
        {{
          "id": "w_ext_south_1",
          "start": {{"x": <float>, "y": <float>}},
          "end": {{"x": <float>, "y": <float>}},
          "thickness": 0.75,
          "type": "exterior"
        }}
      ],
      "doors": [
        {{
          "id": "d_main_entrance",
          "type": "main_entrance",
          "position": {{"x": <float>, "y": <float>}},
          "width": 3.5,
          "room_ids": ["gf_living_room_1"],
          "swing_direction": "inward"
        }}
      ],
      "windows": [
        {{
          "id": "win_gf_1",
          "position": {{"x": <float>, "y": <float>}},
          "width": 4.0,
          "type": "sliding",
          "room_id": "gf_living_room_1"
        }}
      ],
      "stairs": [
        {{
          "id": "stair_gf",
          "x": <float>,
          "y": <float>,
          "width": 8.0,
          "length": 12.0,
          "direction": "up",
          "connects_levels": [0, 1]
        }}
      ],
      "openings": [],
      "circulation": [],
      "balconies": [],
      "parking": []
    }}
  ]
}}

CRITICAL RULES:
- area = width * length for each room
- NO rooms outside the buildable boundary
- NO overlapping rooms
- ALL requested rooms must be present
- Staircase at same (x, y) on every floor
- Do NOT include garden/yard rooms inside the floors array
- Return ONLY the JSON, no markdown, no explanation
"""
    return prompt


def _parse_requirements_summary(requirements: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
    """Parse requirements into a human-readable summary for the prompt."""
    lines = []
    room_counts = {}

    for req in requirements:
        if not isinstance(req, dict):
            continue

        if "room_type" in req:
            rtype = req.get("room_type", "").lower()
            count = int(req.get("count", 1))
            room_counts[rtype] = room_counts.get(rtype, 0) + count
        else:
            # DB format
            for key, rtype in [
                ("bedrooms", "bedroom"), ("bathrooms", "bathroom"),
                ("kitchens", "kitchen"), ("living_rooms", "living_room"),
                ("dining_rooms", "dining_room"), ("balconies", "balcony"),
                ("parking_spaces", "parking"), ("parking", "parking"),
            ]:
                val = int(req.get(key, 0))
                if val > 0:
                    room_counts[rtype] = room_counts.get(rtype, 0) + val

            for key in ["pooja_room", "study_room", "utility_room", "guest_room"]:
                if req.get(key):
                    room_counts[key] = room_counts.get(key, 0) + 1

    # Also check context for fallback
    if not room_counts:
        for key, rtype in [
            ("bedrooms", "bedroom"), ("bathrooms", "bathroom"),
            ("kitchens", "kitchen"), ("living_rooms", "living_room"),
        ]:
            val = int(context.get(key, 0))
            if val > 0:
                room_counts[rtype] = val

    for rtype, count in room_counts.items():
        label = rtype.replace("_", " ").title()
        lines.append(f"- {label}: {count}")

    # Add staircase note for multi-floor
    num_floors = int(context.get("floors") or context.get("number_of_floors") or 1)
    if num_floors > 1:
        lines.append(f"- Staircase: 1 (required for {num_floors} floors, same position on each floor)")

    return "\n".join(lines) if lines else "- Standard residential requirements"


def _validate_gemini_layout(layout_data: LayoutData, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Quick validation of Gemini-generated layout before full geometric validation.
    Returns (is_acceptable, list_of_issues).
    """
    issues = []

    if not layout_data.floors:
        issues.append("No floors generated")
        return False, issues

    plot_w = context.get("plot_width", 30)
    plot_l = context.get("plot_length", 40)
    setbacks = context.get("setbacks", {"front": 4, "rear": 4, "left": 3, "right": 3})
    build_x_min = int(setbacks.get("left", 3))
    build_y_min = int(setbacks.get("front", 4))
    build_x_max = plot_w - int(setbacks.get("right", 3))
    build_y_max = plot_l - int(setbacks.get("rear", 4))

    total_indoor_rooms = 0
    total_indoor_area = 0.0

    for floor in layout_data.floors:
        for room in floor.rooms:
            if room.type in ["garden", "yard", "terrace", "balcony", "driveway"]:
                continue

            total_indoor_rooms += 1
            total_indoor_area += room.width * room.length

            # Positive dimensions
            if room.width <= 0 or room.length <= 0:
                issues.append(f"Room {room.id} has non-positive dimensions")

            # Boundary check (with 1ft tolerance for walls)
            if room.x < build_x_min - 1:
                issues.append(f"Room {room.id} extends past left boundary")
            if room.y < build_y_min - 1:
                issues.append(f"Room {room.id} extends past front boundary")
            if room.x + room.width > build_x_max + 1:
                issues.append(f"Room {room.id} extends past right boundary")
            if room.y + room.length > build_y_max + 1:
                issues.append(f"Room {room.id} extends past rear boundary")

            # Area consistency
            expected_area = room.width * room.length
            if abs(expected_area - room.area) > max(5.0, 0.15 * expected_area):
                # Fix it in-place
                room.area = round(expected_area, 1)

    if total_indoor_rooms < 3:
        issues.append(f"Only {total_indoor_rooms} indoor rooms generated — too few")

    buildable_area = (build_x_max - build_x_min) * (build_y_max - build_y_min)
    if buildable_area > 0 and total_indoor_area < buildable_area * 0.25:
        issues.append(f"Indoor area {total_indoor_area:.0f} sqft is only {(total_indoor_area/buildable_area*100):.0f}% of buildable — house too small")

    is_acceptable = len(issues) <= 3  # Allow minor fixable issues
    return is_acceptable, issues


def _repair_gemini_layout(layout_data: LayoutData, context: Dict[str, Any]) -> LayoutData:
    """
    Apply deterministic repairs to a Gemini-generated layout:
    - Fix area calculations
    - Clamp rooms to buildable boundary
    - Ensure space_category is set
    - Add missing walls
    - Compute building footprint
    """
    setbacks = context.get("setbacks", {"front": 4, "rear": 4, "left": 3, "right": 3})
    build_x_min = float(setbacks.get("left", 3))
    build_y_min = float(setbacks.get("front", 4))
    plot_w = float(context.get("plot_width", 30))
    plot_l = float(context.get("plot_length", 40))
    build_x_max = plot_w - float(setbacks.get("right", 3))
    build_y_max = plot_l - float(setbacks.get("rear", 4))
    facing = (context.get("facing", "south") or "south").lower()

    for floor in layout_data.floors:
        for room in floor.rooms:
            # Fix area
            room.area = round(room.width * room.length, 1)

            # Clamp to buildable
            if room.type not in ["garden", "yard", "terrace", "balcony", "driveway", "parking"]:
                if room.x < build_x_min:
                    room.width -= (build_x_min - room.x)
                    room.x = build_x_min
                if room.y < build_y_min:
                    room.length -= (build_y_min - room.y)
                    room.y = build_y_min
                if room.x + room.width > build_x_max:
                    room.width = build_x_max - room.x
                if room.y + room.length > build_y_max:
                    room.length = build_y_max - room.y

                room.area = round(room.width * room.length, 1)

            # Set space_category from room_catalog
            if not room.space_category:
                specs = get_room_specs(room.type)
                room.space_category = specs.get("privacy", "private")

        # Strict indoor/outdoor separation:
        clean_indoor = []
        for room in floor.rooms:
            rtype = (room.type or "").lower()
            if rtype in ["garden", "yard", "terrace", "balcony", "parking", "garage", "roof", "driveway"] or room.space_category == "outdoor":
                room.space_category = "outdoor"
                if not any(o.id == room.id for o in floor.outdoor_areas):
                    floor.outdoor_areas.append(room)
            else:
                clean_indoor.append(room)
        floor.rooms = clean_indoor

        # Regenerate walls for indoor rooms if walls are missing/sparse
        if len(floor.walls) < len(floor.rooms) * 2:
            floor.walls = []
            for room in floor.rooms:
                floor.walls.extend([
                    Wall(id=f"wn_{room.id}", type="interior", thickness=0.5,
                         start=Point2D(x=room.x, y=room.y),
                         end=Point2D(x=room.x + room.width, y=room.y)),
                    Wall(id=f"ws_{room.id}", type="interior", thickness=0.5,
                         start=Point2D(x=room.x, y=room.y + room.length),
                         end=Point2D(x=room.x + room.width, y=room.y + room.length)),
                    Wall(id=f"we_{room.id}", type="interior", thickness=0.5,
                         start=Point2D(x=room.x + room.width, y=room.y),
                         end=Point2D(x=room.x + room.width, y=room.y + room.length)),
                    Wall(id=f"ww_{room.id}", type="interior", thickness=0.5,
                         start=Point2D(x=room.x, y=room.y),
                         end=Point2D(x=room.x, y=room.y + room.length)),
                ])

        # Ensure staircase rooms exist alongside stairs without duplicating existing stair/hall rooms
        from shapely.geometry import box
        for stair in floor.stairs:
            stair_box = box(stair.x, stair.y, stair.x + stair.width, stair.y + stair.length)
            matching_room = None
            for r in floor.rooms:
                r_box = box(r.x, r.y, r.x + r.width, r.y + r.length)
                if stair_box.intersection(r_box).area > 0.5:
                    matching_room = r
                    break
                if r.id == stair.id or r.type in ["staircase", "stairs"] or "stair" in r.label.lower():
                    matching_room = r
                    break

            if matching_room:
                matching_room.type = "staircase"
                matching_room.space_category = "circulation"
            else:
                floor.rooms.append(Room(
                    id=stair.id,
                    type="staircase",
                    label="Staircase",
                    x=stair.x, y=stair.y,
                    width=stair.width, length=stair.length,
                    area=round(stair.width * stair.length, 1),
                    space_category="circulation"
                ))

    # Compute building footprint from ground floor constructed rooms
    gf_rooms = layout_data.floors[0].rooms if layout_data.floors else []
    constructed = [r for r in gf_rooms if r.type not in ["garden", "yard", "driveway", "balcony", "terrace", "roof", "parking"]]
    if constructed:
        from shapely.geometry import box
        from shapely.ops import unary_union
        fp_x = min(r.x for r in constructed)
        fp_y = min(r.y for r in constructed)
        fp_w = max(r.x + r.width for r in constructed) - fp_x
        fp_l = max(r.y + r.length for r in constructed) - fp_y
        gf_shapes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in constructed]
        constructed_area = round(unary_union(gf_shapes).area, 1)
        layout_data.plot.building_footprint = {
            "x": round(fp_x, 1),
            "y": round(fp_y, 1),
            "width": round(fp_w, 1),
            "length": round(fp_l, 1),
            "constructed_area": constructed_area,
            "bounding_area": round(fp_w * fp_l, 1)
        }

    # Classify upper terraces / roof slabs strictly over ground floor constructed slab
    from app.services.planning.open_space import classify_upper_terrace
    for fl in layout_data.floors:
        if fl.level > 0:
            fl_rooms_dict = [r.model_dump() for r in fl.rooms] + [o.model_dump() for o in fl.outdoor_areas]
            gf_rooms_dict = [r.model_dump() for r in layout_data.floors[0].rooms]
            terraces = classify_upper_terrace(
                fl_rooms_dict,
                {"x": build_x_min, "y": build_y_min, "w": build_x_max - build_x_min, "l": build_y_max - build_y_min},
                fl.level,
                gf_footprint=layout_data.plot.building_footprint,
                gf_rooms=gf_rooms_dict
            )
            for t in terraces:
                if not any(o.id == t["id"] for o in fl.outdoor_areas):
                    poly_pts = [Point2D(x=p["x"], y=p["y"]) for p in t.get("polygon", [])] if t.get("polygon") else None
                    fl.outdoor_areas.append(Room(
                        id=t["id"],
                        type=t.get("type", "roof"),
                        label=t.get("label", "Roof Slab Below"),
                        x=t["x"], y=t["y"],
                        width=t["width"], length=t["length"],
                        area=t["area"],
                        space_category="outdoor",
                        polygon=poly_pts
                    ))

    # Set front_side
    layout_data.plot.front_side = facing

    # Ensure main entrance door exists on ground floor
    if layout_data.floors:
        gf = layout_data.floors[0]
        has_main_entrance = any(d.type == "main_entrance" for d in gf.doors)
        if not has_main_entrance:
            # Find entry room (foyer or living room)
            entry_room = None
            for r in gf.rooms:
                if r.type == "foyer":
                    entry_room = r
                    break
            if not entry_room:
                for r in gf.rooms:
                    if r.type == "living_room":
                        entry_room = r
                        break
            if not entry_room and gf.rooms:
                entry_room = gf.rooms[0]

            if entry_room:
                if facing == "south":
                    m_pos = Point2D(x=round(entry_room.x + entry_room.width / 2 - 1.75, 1),
                                    y=round(entry_room.y + entry_room.length, 1))
                elif facing == "north":
                    m_pos = Point2D(x=round(entry_room.x + entry_room.width / 2 - 1.75, 1),
                                    y=round(entry_room.y, 1))
                elif facing == "east":
                    m_pos = Point2D(x=round(entry_room.x + entry_room.width, 1),
                                    y=round(entry_room.y + entry_room.length / 2 - 1.75, 1))
                else:  # west
                    m_pos = Point2D(x=round(entry_room.x, 1),
                                    y=round(entry_room.y + entry_room.length / 2 - 1.75, 1))

                gf.doors.insert(0, Door(
                    id="d_main_entrance",
                    type="main_entrance",
                    position=m_pos,
                    width=3.5,
                    room_ids=[entry_room.id]
                ))

    # Generate site elements (gates, driveway)
    _add_site_elements(layout_data, context)

    return layout_data


def _add_site_elements(layout_data: LayoutData, context: Dict[str, Any]):
    """Add gates, driveway, and classify open plot areas."""
    from app.services.planning.open_space import generate_site_elements, classify_ground_plot

    plot_w = float(context.get("plot_width", 30))
    plot_l = float(context.get("plot_length", 40))
    facing = (context.get("facing", "south") or "south").lower()
    setbacks = context.get("setbacks", {"front": 4, "rear": 4, "left": 3, "right": 3})

    # Check for parking
    has_parking = False
    parking_rect = None
    if layout_data.floors:
        for room in layout_data.floors[0].rooms:
            if room.type in ["parking", "garage"]:
                has_parking = True
                parking_rect = {
                    "x": room.x, "y": room.y,
                    "width": room.width, "length": room.length
                }
                break

    try:
        site_elements = generate_site_elements(
            plot_w=plot_w, plot_l=plot_l, facing=facing,
            setbacks=setbacks, has_parking=has_parking, parking_rect=parking_rect
        )
        layout_data.plot.gates = site_elements.get("gates", [])
        layout_data.plot.driveway = site_elements.get("driveway")
    except Exception as e:
        logger.warning("Site element generation failed (non-fatal): %s", e)

    # Classify ground floor open areas (store in plot.site_areas and outdoor_areas)
    if layout_data.floors:
        gf_rooms_data = []
        for r in layout_data.floors[0].rooms:
            gf_rooms_data.append({
                "type": r.type, "x": r.x, "y": r.y,
                "width": r.width, "length": r.length, "area": r.area,
                "id": r.id
            })
        try:
            yards = classify_ground_plot(gf_rooms_data, plot_w, plot_l, facing)
            layout_data.plot.site_areas = yards
            for yard in yards:
                poly_pts = [Point2D(x=p["x"], y=p["y"]) for p in yard.get("polygon", [])] if yard.get("polygon") else None
                layout_data.floors[0].outdoor_areas.append(Room(
                    id=yard["id"],
                    type=yard["type"],
                    label=yard.get("label", yard["type"].replace("_", " ").title()),
                    x=yard["x"], y=yard["y"],
                    width=yard["width"], length=yard["length"],
                    area=yard["area"],
                    space_category="outdoor",
                    polygon=poly_pts
                ))
        except Exception as e:
            logger.warning("Ground plot classification failed (non-fatal): %s", e)


def plan_with_gemini(context: Dict[str, Any], requirements: List[Dict[str, Any]]) -> LayoutData:
    """
    Call Gemini to generate an architectural floor plan, then validate and repair.

    Returns a validated LayoutData instance ready for SVG rendering.
    Raises GeminiPlannerError if Gemini cannot produce an acceptable plan.
    """
    t_start = time.time()

    # 1. Build the prompt
    prompt = _build_gemini_architectural_prompt(context, requirements)
    logger.info("Gemini architectural prompt built (%d chars)", len(prompt))

    # 2. Call Gemini via existing provider
    from app.services.ai.gemini_provider import GeminiProvider

    try:
        provider = GeminiProvider()
    except Exception as e:
        raise GeminiPlannerError(f"Cannot initialize GeminiProvider: {e}")

    # We use the provider's client directly with our custom prompt
    # instead of generate_layout which uses the old prompt_builder
    from google.genai import types
    import json as json_mod

    candidate_models = ["gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-3.5-flash"]
    # Deduplicate while preserving order
    seen_models = set()
    models_to_try = []
    for m in candidate_models:
        if m and m not in seen_models:
            seen_models.add(m)
            models_to_try.append(m)

    layout_data = None
    last_error = None

    for model_name in models_to_try:
        if layout_data is not None:
            break

        # Attempt 1: Standard structured mode or text mode with JSON instruction
        for mode in ["structured", "text"]:
            try:
                logger.info("Calling Gemini model=%s mode=%s", model_name, mode)
                if mode == "structured":
                    config = types.GenerateContentConfig(
                        temperature=0.15,
                        response_mime_type="application/json",
                    )
                else:
                    config = types.GenerateContentConfig(temperature=0.15)

                response = provider.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )

                raw_text = response.text
                if not raw_text or not raw_text.strip():
                    raise GeminiPlannerError("Gemini returned empty response")

                from app.services.ai.gemini_provider import _extract_json_from_text
                json_str = _extract_json_from_text(raw_text)
                parsed = json_mod.loads(json_str)

                # Parse into LayoutData
                layout_data = LayoutData(**parsed)
                logger.info(
                    "Gemini (%s, %s) returned layout: %d floors, %d total indoor rooms",
                    model_name, mode,
                    len(layout_data.floors),
                    sum(len(f.rooms) for f in layout_data.floors)
                )
                break
            except Exception as e:
                last_error = e
                err_str = str(e)
                status_label = "503" if "503" in err_str else "404" if "404" in err_str else type(e).__name__
                logger.warning("Gemini model=%s mode=%s failed: %s (%s)", model_name, mode, status_label, err_str[:100])
                if mode == "structured" and ("503" in err_str or "unavailable" in err_str):
                    # Immediately try text mode for this model
                    continue
                break

    if layout_data is None:
        raise GeminiPlannerError(f"Gemini failed across models {models_to_try}: {last_error}")

    # 3. Quick validation
    is_acceptable, issues = _validate_gemini_layout(layout_data, context)
    logger.info("Gemini layout validation: acceptable=%s, issues=%d: %s",
                is_acceptable, len(issues), "; ".join(issues[:5]))

    if not is_acceptable:
        raise GeminiPlannerError(
            f"Gemini layout failed validation with {len(issues)} issues: {'; '.join(issues[:5])}"
        )

    # 4. Apply deterministic repairs
    layout_data = _repair_gemini_layout(layout_data, context)

    # 5. Set generation metadata
    elapsed = round(time.time() - t_start, 2)
    layout_data.generation_metadata = {
        "planner_source": "gemini_hybrid",
        "generation_engine": "gemini_hybrid",
        "gemini_model": provider.model_name,
        "generation_time_sec": elapsed,
        "issues_found": len(issues),
        "issues_repaired": issues[:5],
    }

    logger.info("Gemini hybrid plan complete in %.2fs", elapsed)
    return layout_data
