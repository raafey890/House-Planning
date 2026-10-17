"""
Post-processor for the deterministic planning engine.
Assembles the complete LayoutData schema with doors, windows, stairs, gates, driveway, and classified spaces.
Architectural improvements:
- Computes actual Ground Floor building footprint before classifying upper terraces.
- Constrains upper terraces strictly within the Ground Floor constructed slab.
- Ensures all site access elements (vehicle gate, pedestrian gate, driveway) are attached.
"""
from typing import Dict, Any, List
from app.models.layout import LayoutData, Plot, Room, Door, Window, Stair, Floor, Point2D, Wall
from app.services.planning.room_catalog import get_room_specs
from app.services.planning.circulation import CirculationGraph
from app.services.planning.open_space import generate_site_elements, classify_upper_terrace, classify_ground_plot

import copy

def post_process_layout(engine_result: Dict[str, Any]) -> LayoutData:
    plot_info = engine_result["plot"]
    floors_data = copy.deepcopy(engine_result["floors"])
    facing = plot_info["facing"].lower()
    setbacks = plot_info["setbacks"]

    build_box = {
        "x_start": plot_info["buildable"]["x"],
        "y_start": plot_info["buildable"]["y"],
        "x_end": plot_info["buildable"]["x"] + plot_info["buildable"]["w"],
        "y_end": plot_info["buildable"]["y"] + plot_info["buildable"]["l"],
        "w": plot_info["buildable"]["w"],
        "l": plot_info["buildable"]["l"]
    }

    # 1. Calculate exact ground floor building footprint BEFORE upper floor classification
    ground_rooms = floors_data.get(0, [])
    constructed_gf = [
        r for r in ground_rooms
        if r["type"] not in ["garden", "yard", "driveway", "balcony", "terrace", "roof", "parking"]
    ]
    if constructed_gf:
        from shapely.geometry import box
        from shapely.ops import unary_union
        footprint_x = min(r["x"] for r in constructed_gf)
        footprint_y = min(r["y"] for r in constructed_gf)
        footprint_w = max(r["x"] + r["width"] for r in constructed_gf) - footprint_x
        footprint_l = max(r["y"] + r["length"] for r in constructed_gf) - footprint_y
        gf_constructed_shapes = [box(r["x"], r["y"], r["x"] + r["width"], r["y"] + r["length"]) for r in constructed_gf]
        constructed_area = round(unary_union(gf_constructed_shapes).area, 1)
        building_footprint = {
            "x": round(footprint_x, 1),
            "y": round(footprint_y, 1),
            "width": round(footprint_w, 1),
            "length": round(footprint_l, 1),
            "constructed_area": constructed_area,
            "bounding_area": round(footprint_w * footprint_l, 1)
        }
    else:
        building_footprint = None

    # 2. Classify upper floor terraces strictly over the Ground Floor constructed slab
    upper_terraces_by_floor: Dict[int, List[Dict[str, Any]]] = {}
    for lvl in list(floors_data.keys()):
        if lvl > 0:
            terraces = classify_upper_terrace(
                floors_data[lvl],
                build_box,
                lvl,
                gf_footprint=building_footprint,
                gf_rooms=ground_rooms
            )
            upper_terraces_by_floor[lvl] = terraces

    # 3. Build Circulation Graph & Movement Network
    circ_graph = CirculationGraph(floors_data, facing=facing)
    circ_validation = circ_graph.validate_circulation()
    interior_doors, open_plan_openings = circ_graph.generate_doors_and_openings()
    exterior_windows = circ_graph.generate_exterior_windows(build_box)

    # 4. Find Parking on Ground Floor (if any)
    has_parking = False
    parking_rect = None
    for r in ground_rooms:
        if r["type"] in ["parking", "garage"]:
            has_parking = True
            parking_rect = r
            break

    # 5. Generate Site Elements (Gates, Driveway, Road side)
    site_elements = generate_site_elements(
        plot_w=plot_info["width"],
        plot_l=plot_info["length"],
        facing=facing,
        setbacks=setbacks,
        has_parking=has_parking,
        parking_rect=parking_rect
    )

    # 6. Classify ground floor unbuilt areas (Yards, Gardens)
    # Store in plot.site_areas and floor.outdoor_areas — NEVER mix into floor.rooms!
    yards = classify_ground_plot(ground_rooms, plot_info["width"], plot_info["length"], facing)

    plot = Plot(
        width=plot_info["width"],
        length=plot_info["length"],
        facing=facing,
        front_side=facing,
        setbacks=setbacks,
        buildable_boundary={
            "width": plot_info["buildable"]["w"],
            "length": plot_info["buildable"]["l"]
        },
        gates=site_elements["gates"],
        driveway=site_elements["driveway"],
        building_footprint=building_footprint,
        site_areas=yards
    )

    # 7. Build Floor Objects
    out_floors: List[Floor] = []
    main_door_placed = False

    for lvl, raw_rooms in floors_data.items():
        rooms: List[Room] = []
        outdoor_areas: List[Room] = []
        stairs: List[Stair] = []
        balconies: List[Dict[str, Any]] = []
        parking_list: List[Dict[str, Any]] = []
        floor_doors: List[Door] = []
        floor_windows: List[Window] = []
        floor_openings: List[Dict[str, Any]] = []
        walls: List[Wall] = []

        # Add floor-specific outdoor spaces (terraces for upper floors, yards for ground floor)
        if lvl > 0 and lvl in upper_terraces_by_floor:
            for t in upper_terraces_by_floor[lvl]:
                poly_pts = [Point2D(x=p["x"], y=p["y"]) for p in t.get("polygon", [])] if t.get("polygon") else None
                outdoor_areas.append(Room(
                    id=t["id"],
                    type=t.get("type", "terrace"),
                    label=t.get("label", "Open Terrace"),
                    x=t["x"], y=t["y"],
                    width=t["width"], length=t["length"],
                    area=t["area"],
                    space_category="outdoor",
                    polygon=poly_pts,
                    metadata=t.get("metadata", {})
                ))
        elif lvl == 0:
            for y in yards:
                poly_pts = [Point2D(x=p["x"], y=p["y"]) for p in y.get("polygon", [])] if y.get("polygon") else None
                outdoor_areas.append(Room(
                    id=y["id"],
                    type=y["type"],
                    label=y.get("label", y["type"].replace("_", " ").title()),
                    x=y["x"], y=y["y"],
                    width=y["width"], length=y["length"],
                    area=y["area"],
                    space_category="outdoor",
                    polygon=poly_pts,
                    metadata=y.get("metadata", {})
                ))

        # Segregate indoor rooms and special components
        for r in raw_rooms:
            rtype = r["type"]
            specs = get_room_specs(rtype, plot_info["width"] * plot_info["length"])
            category = r.get("space_category", specs.get("privacy", "private"))

            if rtype == "staircase":
                stairs.append(Stair(
                    id=r["id"],
                    x=r["x"], y=r["y"],
                    width=r["width"], length=r["length"],
                    direction="up" if lvl == 0 else "down"
                ))
                rooms.append(Room(
                    id=r["id"],
                    type="staircase",
                    label="Staircase",
                    x=r["x"], y=r["y"],
                    width=r["width"], length=r["length"],
                    area=r["area"],
                    space_category="circulation"
                ))

            elif rtype in ["parking", "garage"]:
                parking_list.append({
                    "x": r["x"], "y": r["y"],
                    "width": r["width"], "length": r["length"]
                })
                poly_pts = [Point2D(x=p["x"], y=p["y"]) for p in r.get("polygon", [])] if r.get("polygon") else None
                outdoor_areas.append(Room(
                    id=r["id"],
                    type=rtype,
                    label="Parking" if rtype == "parking" else "Garage",
                    x=r["x"], y=r["y"],
                    width=r["width"], length=r["length"],
                    area=r["area"],
                    space_category="outdoor",
                    polygon=poly_pts,
                    metadata=r.get("metadata", {})
                ))

            elif rtype == "balcony":
                balconies.append({
                    "x": r["x"], "y": r["y"],
                    "width": r["width"], "length": r["length"]
                })
                poly_pts = [Point2D(x=p["x"], y=p["y"]) for p in r.get("polygon", [])] if r.get("polygon") else None
                outdoor_areas.append(Room(
                    id=r["id"],
                    type="balcony",
                    label="Balcony",
                    x=r["x"], y=r["y"],
                    width=r["width"], length=r["length"],
                    area=r["area"],
                    space_category="outdoor",
                    polygon=poly_pts,
                    metadata=r.get("metadata", {})
                ))

            elif rtype in ["garden", "yard", "terrace"]:
                # Pure outdoor space — place in outdoor_areas, NOT rooms
                poly_pts = [Point2D(x=p["x"], y=p["y"]) for p in r.get("polygon", [])] if r.get("polygon") else None
                outdoor_areas.append(Room(
                    id=r["id"],
                    type=rtype,
                    label=r.get("label", rtype.replace("_", " ").title()),
                    x=r["x"], y=r["y"],
                    width=r["width"], length=r["length"],
                    area=r["area"],
                    space_category="outdoor",
                    polygon=poly_pts,
                    metadata=r.get("metadata", {})
                ))

            else:
                # Genuine indoor habitable room
                rooms.append(Room(
                    id=r["id"],
                    type=rtype,
                    label=r.get("label", rtype.replace("_", " ").title()),
                    x=r["x"], y=r["y"],
                    width=r["width"], length=r["length"],
                    area=r["area"],
                    space_category=category
                ))

        # Generate standard enclosing walls strictly for indoor rooms
        for r in rooms:
            walls.extend([
                Wall(id=f"wn_{r.id}", type="interior", thickness=0.5, start=Point2D(x=r.x, y=r.y), end=Point2D(x=r.x + r.width, y=r.y)),
                Wall(id=f"ws_{r.id}", type="interior", thickness=0.5, start=Point2D(x=r.x, y=r.y + r.length), end=Point2D(x=r.x + r.width, y=r.y + r.length)),
                Wall(id=f"we_{r.id}", type="interior", thickness=0.5, start=Point2D(x=r.x + r.width, y=r.y), end=Point2D(x=r.x + r.width, y=r.y + r.length)),
                Wall(id=f"ww_{r.id}", type="interior", thickness=0.5, start=Point2D(x=r.x, y=r.y), end=Point2D(x=r.x, y=r.y + r.length)),
            ])

        # Filter doors for this floor level
        floor_room_ids = set(r.id for r in rooms)
        for d in interior_doors:
            if any(rid in floor_room_ids for rid in d.room_ids):
                floor_doors.append(d)

        # Place Main Entrance Door on Ground Floor (prefer foyer, then living_room)
        if lvl == 0 and not main_door_placed:
            entry_room = None
            for r in rooms:
                if r.type == "foyer":
                    entry_room = r
                    break
            if not entry_room:
                for r in rooms:
                    if r.type == "living_room":
                        entry_room = r
                        break
            if not entry_room and rooms:
                entry_room = rooms[0]

            if entry_room:
                if facing == "south":
                    m_pos = Point2D(x=round(entry_room.x + entry_room.width / 2 - 1.75, 1), y=round(entry_room.y + entry_room.length, 1))
                elif facing == "north":
                    m_pos = Point2D(x=round(entry_room.x + entry_room.width / 2 - 1.75, 1), y=round(entry_room.y, 1))
                elif facing == "east":
                    m_pos = Point2D(x=round(entry_room.x + entry_room.width, 1), y=round(entry_room.y + entry_room.length / 2 - 1.75, 1))
                else:  # west
                    m_pos = Point2D(x=round(entry_room.x, 1), y=round(entry_room.y + entry_room.length / 2 - 1.75, 1))

                floor_doors.insert(0, Door(
                    id="d_main_entrance",
                    type="main_entrance",
                    position=m_pos,
                    width=3.5,
                    room_ids=[entry_room.id],
                    floor_level=0
                ))
                main_door_placed = True

        # Filter windows for this floor
        for w in exterior_windows:
            if w.room_id in floor_room_ids:
                floor_windows.append(w)

        # Filter openings for this floor
        for op in open_plan_openings:
            if any(rid in floor_room_ids for rid in op["room_ids"]):
                floor_openings.append(op)

        out_floors.append(Floor(
            level=lvl,
            name="Ground Floor" if lvl == 0 else f"First Floor" if lvl == 1 else f"Floor {lvl}",
            rooms=rooms,
            walls=walls,
            doors=floor_doors,
            windows=floor_windows,
            openings=floor_openings,
            stairs=stairs,
            balconies=balconies,
            parking=parking_list,
            outdoor_areas=outdoor_areas
        ))

    return LayoutData(
        plot=plot,
        floors=out_floors,
        metadata={
            "generation_engine": "deterministic",
            "solver_status": engine_result.get("status"),
            "solve_time_sec": engine_result.get("solve_time"),
            "circulation_valid": circ_validation["valid"],
            "isolated_rooms": circ_validation["isolated_rooms"]
        }
    )
