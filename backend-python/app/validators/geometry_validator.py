from typing import List, Dict, Any, Tuple
from shapely.geometry import box, Polygon
from shapely.ops import unary_union
from app.models.layout import LayoutData, Room

class GeometryValidationError(Exception):
    pass

# Allowed space categories (rooms with these don't count as "unclassified")
ALLOWED_SPACE_CATEGORIES = {
    "public", "service", "private", "circulation", "outdoor",
    "foyer", "terrace", "courtyard", "garden", "setback",
    "driveway", "parking", "utility", "balcony",
}

# Room types that implicitly have a category
IMPLICIT_CATEGORY_MAP = {
    "bedroom": "private",
    "bathroom": "private",
    "kitchen": "service",
    "living_room": "public",
    "dining_room": "public",
    "foyer": "public",
    "stairs": "circulation",
    "staircase": "circulation",
    "corridor": "circulation",
    "hallway": "circulation",
    "circulation": "circulation",
    "parking": "outdoor",
    "balcony": "outdoor",
    "terrace": "outdoor",
    "courtyard": "outdoor",
    "garden": "outdoor",
    "utility": "service",
    "pooja": "private",
    "store": "service",
}


class GeometryValidator:
    @staticmethod
    def validate_layout(layout: LayoutData, requested_rooms: Dict[str, int] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates geometric and architectural quality constraints of a layout.
        Returns (passed: bool, results: dict) where results contains per-check verdicts.
        Raises GeometryValidationError on hard failures.
        """
        results: Dict[str, Any] = {}
        errors: List[str] = []

        # ── 1. Positive plot dimensions ──────────────────────────
        if layout.plot.width <= 0 or layout.plot.length <= 0:
            raise GeometryValidationError("Plot dimensions must be positive.")

        buildable_width = layout.plot.buildable_boundary.width
        buildable_length = layout.plot.buildable_boundary.length

        if buildable_width <= 0 or buildable_length <= 0:
            raise GeometryValidationError("Buildable boundary dimensions must be positive.")

        boundary_min_x = layout.plot.setbacks.left
        boundary_min_y = layout.plot.setbacks.front
        boundary_max_x = boundary_min_x + buildable_width
        boundary_max_y = boundary_min_y + buildable_length
        buildable_box = box(boundary_min_x, boundary_min_y, boundary_max_x, boundary_max_y)
        buildable_area = buildable_box.area

        # Determine front side from facing
        facing = (layout.plot.facing or "south").lower()
        front_side = facing

        # Min room size constraints
        min_room_sizes = {
            "bedroom": 80, "bathroom": 30, "kitchen": 60,
            "living_room": 120, "dining_room": 80,
            "stairs": 40, "parking": 120, "balcony": 20,
        }

        seen_ids = set()
        has_stairs = False
        has_main_entrance = False
        has_foyer = False
        all_stair_positions: Dict[int, List[Tuple[float, float]]] = {}  # level -> [(x, y), ...]

        for floor in layout.floors:
            room_boxes = []
            floor_room_counts = {}
            floor_used_area = 0.0

            for room in floor.rooms:
                if room.id in seen_ids:
                    errors.append(f"Duplicate ID found: {room.id}")
                seen_ids.add(room.id)

                if room.width <= 0 or room.length <= 0:
                    errors.append(f"Room {room.id} ('{room.label}') dimensions must be positive.")
                    continue

                # Create Shapely geometry for the room
                if hasattr(room, "polygon") and room.polygon and len(room.polygon) >= 3:
                    room_geom = Polygon([(p.x, p.y) for p in room.polygon])
                    calculated_area = room_geom.area
                else:
                    room_geom = box(room.x, room.y, room.x + room.width, room.y + room.length)
                    calculated_area = room.width * room.length

                if abs(calculated_area - room.area) > max(10.0, 0.1 * room.area):
                    errors.append(f"Room {room.id} area inconsistency. Expected ~{calculated_area:.1f}, got {room.area}")

                if room.type not in ["parking", "garage", "garden", "yard", "driveway", "balcony", "terrace", "stairs", "staircase", "foyer"]:
                    # Preferred sizes are only guidelines now, but minimums apply
                    min_area = min_room_sizes.get(room.type, 20)
                    if calculated_area < min_area:
                        errors.append(f"Room '{room.label}' is too small ({calculated_area:.0f} sq ft). Min for {room.type} is {min_area} sq ft.")

                if not (hasattr(room, "polygon") and room.polygon):
                    aspect_ratio = max(room.width / room.length, room.length / room.width)
                    if aspect_ratio > 4.0 and room.type not in ["circulation", "balcony", "corridor", "stairs", "hallway", "driveway", "yard", "garden"]:
                        errors.append(f"Room '{room.label}' has extreme aspect ratio ({room.width}x{room.length}).")

                plot_box = box(0, 0, layout.plot.width, layout.plot.length)

                if room.type in ["parking", "garage", "garden", "yard", "driveway", "balcony", "terrace"]:
                    if not plot_box.covers(room_geom):
                        errors.append(f"Outdoor space '{room.label}' is outside the plot boundary.")
                else:
                    if not buildable_box.covers(room_geom):
                        errors.append(f"Indoor room '{room.label}' is outside the buildable boundary.")

                for other_room_id, other_label, other_geom in room_boxes:
                    intersection = room_geom.intersection(other_geom)
                    if intersection.area > 0.01:
                        errors.append(f"Room '{room.label}' overlaps with '{other_label}'.")

                room_boxes.append((room.id, room.label, room_geom))
                floor_room_counts[room.type] = floor_room_counts.get(room.type, 0) + 1
                
                # Exclude outdoor spaces from internal utilization check
                if room.type not in ["parking", "garage", "garden", "yard", "driveway", "balcony", "terrace"]:
                    floor_used_area += calculated_area

                if room.type in ["stairs", "staircase"]:
                    has_stairs = True
                if room.type == "foyer":
                    has_foyer = True

            # Validate outdoor areas on this floor (terraces, balconies, yards)
            for out_area in getattr(floor, "outdoor_areas", []):
                if hasattr(out_area, "polygon") and out_area.polygon and len(out_area.polygon) >= 3:
                    out_geom = Polygon([(p.x, p.y) for p in out_area.polygon])
                else:
                    out_geom = box(out_area.x, out_area.y, out_area.x + out_area.width, out_area.y + out_area.length)

                if not plot_box.covers(out_geom):
                    errors.append(f"Outdoor space '{out_area.label}' is outside the plot boundary.")

            # Collect stair positions from floor.stairs list
            for stair in floor.stairs:
                has_stairs = True
                all_stair_positions.setdefault(floor.level, []).append((stair.x, stair.y))

            # Also collect from room-based stairs
            for room in floor.rooms:
                if room.type in ["stairs", "staircase"]:
                    all_stair_positions.setdefault(floor.level, []).append((room.x, room.y))

            # Contiguous rooms check
            if room_boxes:
                shapely_boxes = [rb[2] for rb in room_boxes]
                # Include attached ground parking / garage if present
                for p in getattr(floor, "parking", []):
                    shapely_boxes.append(box(p["x"], p["y"], p["x"] + p["width"], p["y"] + p["length"]))
                for out in getattr(floor, "outdoor_areas", []):
                    if out.type in ["parking", "garage", "carport", "porch"]:
                        shapely_boxes.append(box(out.x, out.y, out.x + out.width, out.y + out.length))
                unified_shape = unary_union([b.buffer(0.05) for b in shapely_boxes])
                if unified_shape.geom_type == 'MultiPolygon':
                    errors.append(f"Floor {floor.level} is disconnected. All rooms must form a contiguous structure.")

            # Check for main entrance door on ground floor
            if floor.level == 0:
                for door in floor.doors:
                    if getattr(door, 'type', 'swing') == "main_entrance":
                        has_main_entrance = True

        # ── Main entrance validation ────────────────────────────
        results["main_entrance"] = has_main_entrance
        if not has_main_entrance:
            ground_doors = []
            for floor in layout.floors:
                if floor.level == 0:
                    ground_doors = floor.doors
            if not ground_doors:
                errors.append("No doors found on the ground floor. At least a main entrance door is required.")

        # ── Gate validation ─────────────────────────────────────
        gates = layout.plot.gates or []
        has_pedestrian_gate = any(g.get("type") == "pedestrian" for g in gates)
        has_vehicle_gate = any(g.get("type") == "vehicle" for g in gates)
        results["pedestrian_gate"] = has_pedestrian_gate
        results["vehicle_gate"] = has_vehicle_gate

        # ── Parking-road connection ─────────────────────────────
        has_parking = False
        for floor in layout.floors:
            if floor.level == 0 and len(floor.parking) > 0:
                has_parking = True
            for room in floor.rooms:
                if room.type == "parking" and floor.level == 0:
                    has_parking = True
            for out in getattr(floor, "outdoor_areas", []):
                if out.type in ["parking", "garage"] and floor.level == 0:
                    has_parking = True
        results["parking_connection"] = has_parking and has_vehicle_gate if has_parking else True

        # ── Stair alignment across floors ───────────────────────
        stair_aligned = True
        levels = sorted(all_stair_positions.keys())
        if len(levels) >= 2:
            ref_positions = all_stair_positions[levels[0]]
            for lvl in levels[1:]:
                lvl_positions = all_stair_positions[lvl]
                aligned = False
                for rx, ry in ref_positions:
                    for sx, sy in lvl_positions:
                        if abs(rx - sx) <= 2.0 and abs(ry - sy) <= 2.0:
                            aligned = True
                            break
                    if aligned:
                        break
                if not aligned:
                    stair_aligned = False
        results["stair_alignment"] = stair_aligned
        if not stair_aligned:
            errors.append("Stairs are not vertically aligned across floors.")

        # ── Multi-floor stair presence ──────────────────────────
        if len(layout.floors) > 1 and not has_stairs:
            errors.append("Staircase missing. Multi-floor plans require a staircase.")
        results["stair_present"] = has_stairs or len(layout.floors) <= 1

        # ── Unclassified area ───────────────────────────────────
        fp = layout.plot.building_footprint
        fp_area = (fp["width"] * fp["length"]) if fp else buildable_area

        for floor in layout.floors:
            indoor_area = sum(r.width * r.length for r in floor.rooms if r.width > 0 and r.length > 0)
            outdoor_floor_area = sum(o.width * o.length for o in getattr(floor, "outdoor_areas", []) if o.type in ["terrace", "roof", "balcony"])
            accounted = indoor_area + outdoor_floor_area
            unclassified = max(0.0, fp_area - accounted)
            
            if unclassified <= 15.0:
                results[f"floor_{floor.level}_unclassified"] = 0.0
            else:
                results[f"floor_{floor.level}_unclassified"] = round(unclassified, 1)

        # ── Room count validation ───────────────────────────────
        if requested_rooms:
            total_counts = {}
            for floor in layout.floors:
                for room in floor.rooms:
                    total_counts[room.type] = total_counts.get(room.type, 0) + 1

            for r_type, expected_count in requested_rooms.items():
                actual_count = total_counts.get(r_type, 0)
                if actual_count < expected_count:
                    errors.append(f"Requested {expected_count} of type '{r_type}', but found {actual_count}.")

        results["foyer"] = has_foyer
        results["errors"] = errors

        # ── Hard fail if critical errors ────────────────────────
        if errors:
            raise GeometryValidationError("\n".join(errors))

        return True, results
