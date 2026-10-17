"""
Open Space and Site Plan Elements Classifier.
Classifies terraces, balconies, gates, driveway, and site boundary annotations.
Architectural improvements:
- Constrains upper floor terraces to realistic architectural sizes over the Ground Floor roof.
- Ensures vehicle gate and driveway access for all standard residential plots.
- Properly partitions site open spaces (front garden, rear yard, side yards).
"""
from typing import Dict, Any, List
from shapely.geometry import box, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union

def generate_site_elements(
    plot_w: float,
    plot_l: float,
    facing: str,
    setbacks: Dict[str, float],
    has_parking: bool,
    parking_rect: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Generates gate positions, driveway, and front road annotations based on facing.
    Ensures both pedestrian and vehicle access gates exist for standard plots.
    """
    facing = facing.lower()
    gates = []
    driveway = None

    if facing == "south":
        road_y = plot_l
        # Pedestrian gate at center-left
        gates.append({
            "type": "pedestrian",
            "position": {"x": round(plot_w * 0.25, 1), "y": road_y},
            "width": 4.0
        })
        # Vehicle gate aligned with parking or on the right side
        if has_parking and parking_rect:
            vg_x = parking_rect["x"] + parking_rect["width"] / 2
        else:
            vg_x = plot_w * 0.75
        vg_x = min(max(vg_x, 6.0), plot_w - 6.0)

        gates.append({
            "type": "vehicle",
            "position": {"x": round(vg_x, 1), "y": road_y},
            "width": 10.0
        })

        if has_parking and parking_rect:
            py = parking_rect["y"] + parking_rect["length"]
        else:
            py = plot_l - setbacks.get("front", 4)
        driveway = {
            "points": [
                {"x": round(vg_x, 1), "y": road_y},
                {"x": round(vg_x, 1), "y": round(py, 1)}
            ]
        }

    elif facing == "north":
        road_y = 0.0
        gates.append({
            "type": "pedestrian",
            "position": {"x": round(plot_w * 0.25, 1), "y": road_y},
            "width": 4.0
        })
        if has_parking and parking_rect:
            vg_x = parking_rect["x"] + parking_rect["width"] / 2
        else:
            vg_x = plot_w * 0.75
        vg_x = min(max(vg_x, 6.0), plot_w - 6.0)

        gates.append({
            "type": "vehicle",
            "position": {"x": round(vg_x, 1), "y": road_y},
            "width": 10.0
        })

        if has_parking and parking_rect:
            py = parking_rect["y"]
        else:
            py = setbacks.get("front", 4)
        driveway = {
            "points": [
                {"x": round(vg_x, 1), "y": road_y},
                {"x": round(vg_x, 1), "y": round(py, 1)}
            ]
        }

    elif facing == "east":
        road_x = plot_w
        gates.append({
            "type": "pedestrian",
            "position": {"x": road_x, "y": round(plot_l * 0.25, 1)},
            "width": 4.0
        })
        if has_parking and parking_rect:
            vg_y = parking_rect["y"] + parking_rect["length"] / 2
        else:
            vg_y = plot_l * 0.75
        vg_y = min(max(vg_y, 6.0), plot_l - 6.0)

        gates.append({
            "type": "vehicle",
            "position": {"x": road_x, "y": round(vg_y, 1)},
            "width": 10.0
        })

        if has_parking and parking_rect:
            px = parking_rect["x"] + parking_rect["width"]
        else:
            px = plot_w - setbacks.get("front", 4)
        driveway = {
            "points": [
                {"x": road_x, "y": round(vg_y, 1)},
                {"x": round(px, 1), "y": round(vg_y, 1)}
            ]
        }

    else:  # west
        road_x = 0.0
        gates.append({
            "type": "pedestrian",
            "position": {"x": road_x, "y": round(plot_l * 0.25, 1)},
            "width": 4.0
        })
        if has_parking and parking_rect:
            vg_y = parking_rect["y"] + parking_rect["length"] / 2
        else:
            vg_y = plot_l * 0.75
        vg_y = min(max(vg_y, 6.0), plot_l - 6.0)

        gates.append({
            "type": "vehicle",
            "position": {"x": road_x, "y": round(vg_y, 1)},
            "width": 10.0
        })

        if has_parking and parking_rect:
            px = parking_rect["x"]
        else:
            px = setbacks.get("front", 4)
        driveway = {
            "points": [
                {"x": road_x, "y": round(vg_y, 1)},
                {"x": round(px, 1), "y": round(vg_y, 1)}
            ]
        }

    return {
        "gates": gates,
        "driveway": driveway,
        "front_side": facing
    }

def classify_upper_terrace(
    floor_rooms: List[Dict[str, Any]],
    build_box: Dict[str, float],
    floor_lvl: int,
    gf_footprint: Dict[str, float] = None,
    gf_rooms: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Classifies intentional open terraces and roof slab regions on upper floors.
    CRITICAL ARCHITECTURAL RULE:
    An upper terrace or roof slab exists strictly over the Ground Floor constructed slab.
    It accounts for the exact difference between the ground floor constructed slab polygon
    and upper floor occupied spaces (indoor rooms + balconies + intentional terraces),
    guaranteeing 100% geometric area reconciliation without double-counting or phantom areas.
    """
    if floor_lvl == 0 or not floor_rooms:
        return []

    # 1. Compute true ground floor constructed slab polygon
    if gf_rooms:
        constructed_gf = [
            r for r in gf_rooms
            if r.get("type") not in ["garden", "yard", "driveway", "balcony", "terrace", "roof", "parking"]
        ]
        gf_shapes = [box(r["x"], r["y"], r["x"] + r["width"], r["y"] + r["length"]) for r in constructed_gf]
        gf_slab = unary_union(gf_shapes) if gf_shapes else None
    elif gf_footprint:
        gf_x1 = gf_footprint["x"]
        gf_y1 = gf_footprint["y"]
        gf_x2 = gf_x1 + gf_footprint["width"]
        gf_y2 = gf_y1 + gf_footprint["length"]
        gf_slab = box(gf_x1, gf_y1, gf_x2, gf_y2)
    else:
        gf_slab = None

    if not gf_slab or gf_slab.is_empty:
        return []

    # 2. All upper floor occupied spaces (indoor rooms + balconies + intentional terraces)
    # These all occupy space over the ground floor slab below!
    ff_occupied_rooms = [
        r for r in floor_rooms
        if r.get("type") not in ["garden", "yard", "driveway", "roof"]
    ]
    if not ff_occupied_rooms:
        return []

    occupied_shapes = [box(r["x"], r["y"], r["x"] + r["width"], r["y"] + r["length"]) for r in ff_occupied_rooms]
    occupied_union = unary_union(occupied_shapes)

    # 3. Calculate unbuilt slab strictly over the ground floor constructed slab
    unbuilt_slab = gf_slab.difference(occupied_union)
    if unbuilt_slab.is_empty or unbuilt_slab.area < 2.0:
        return []

    def extract_poly_list(geom):
        if geom.is_empty:
            return []
        if isinstance(geom, Polygon):
            return [geom]
        if isinstance(geom, MultiPolygon):
            return list(geom.geoms)
        if isinstance(geom, GeometryCollection):
            res = []
            for g in geom.geoms:
                if isinstance(g, Polygon):
                    res.append(g)
                elif isinstance(g, MultiPolygon):
                    res.extend(g.geoms)
            return res
        return []

    polys = extract_poly_list(unbuilt_slab)
    terraces = []
    idx = 0

    for poly in polys:
        if poly.area < 2.0:
            continue

        minx, miny, maxx, maxy = poly.bounds
        w = round(maxx - minx, 1)
        l = round(maxy - miny, 1)
        poly_area = round(poly.area, 1)

        # Polygon coordinates if irregular
        coords = list(poly.exterior.coords)[:-1]
        is_irregular = len(coords) > 4 or abs(poly_area - (w * l)) > 1.0
        pts = [{"x": round(c[0], 1), "y": round(c[1], 1)} for c in coords] if is_irregular else None

        rep = poly.representative_point()
        center_meta = {"center": {"x": round(rep.x, 1), "y": round(rep.y, 1)}}

        # If it's very small (< 25 sq ft), it's a projecting roof slab ledge below
        # If manageable architectural size (25 to 450 sq ft), label Open Terrace
        # Large unbuilt slab areas are Roof Slab Below
        if poly_area < 25.0:
            slab_type = "roof"
            slab_label = "Roof Slab Below"
        elif idx == 0 and poly_area <= 450.0:
            slab_type = "terrace"
            slab_label = "Open Terrace"
        elif poly_area <= 350.0:
            slab_type = "terrace"
            slab_label = "Open Terrace"
        else:
            slab_type = "roof"
            slab_label = "Roof Slab Below"

        terraces.append({
            "id": f"terrace_f{floor_lvl}_{idx}",
            "type": slab_type,
            "label": slab_label,
            "x": round(minx, 1),
            "y": round(miny, 1),
            "width": w,
            "length": l,
            "area": poly_area,
            "space_category": "outdoor",
            "polygon": pts,
            "metadata": center_meta
        })
        idx += 1

    return terraces

def classify_ground_plot(
    floor_rooms: List[Dict[str, Any]],
    plot_w: float,
    plot_l: float,
    facing: str
) -> List[Dict[str, Any]]:
    """
    Classifies the unbuilt ground floor plot area into gardens, courtyards, and yards.
    Uses Shapely to subtract the building envelope and parking from the plot,
    then decomposes the remaining open space into regions for rendering.
    """
    if not floor_rooms:
        return []

    # 1. Enforce that real indoor rooms exist
    indoor_rooms = [r for r in floor_rooms if r["type"] not in ["garden", "yard", "driveway", "balcony", "terrace"]]
    if not indoor_rooms:
        raise ValueError("Cannot classify plot open space: no indoor ground floor rooms exist.")

    plot_poly = box(0, 0, plot_w, plot_l)

    # 2. All constructed or occupied elements that are not yard/garden
    occupied_shapes = []
    for r in floor_rooms:
        if r["type"] not in ["garden", "yard", "driveway"]:
            occupied_shapes.append(box(r["x"], r["y"], r["x"] + r["width"], r["y"] + r["length"]))

    if not occupied_shapes:
        raise ValueError("No constructed shapes found on ground floor.")

    occupied_union = unary_union(occupied_shapes)
    if occupied_union.area < 80.0:
        raise ValueError(
            f"Ground floor constructed area ({occupied_union.area:.1f} sq ft) is too small. "
            "Refusing to generate empty plan consisting only of garden."
        )

    remaining_plot = plot_poly.difference(occupied_union)

    def extract_polygons(geom):
        if geom.is_empty:
            return []
        if isinstance(geom, Polygon):
            return [geom]
        if isinstance(geom, MultiPolygon):
            return list(geom.geoms)
        if isinstance(geom, GeometryCollection):
            polys = []
            for g in geom.geoms:
                if isinstance(g, Polygon):
                    polys.append(g)
                elif isinstance(g, MultiPolygon):
                    polys.extend(g.geoms)
            return polys
        return []

    # 3. Use actual building envelope bounding box
    min_rx = min(r["x"] for r in indoor_rooms)
    max_rx = max(r["x"] + r["width"] for r in indoor_rooms)
    min_ry = min(r["y"] for r in indoor_rooms)
    max_ry = max(r["y"] + r["length"] for r in indoor_rooms)

    zones = [
        ("Front Garden" if facing == "north" else "Rear Yard", "garden" if facing == "north" else "yard", box(0, 0, plot_w, min_ry)),
        ("Front Garden" if facing == "south" else "Rear Yard", "garden" if facing == "south" else "yard", box(0, max_ry, plot_w, plot_l)),
        ("Front Garden" if facing == "west" else "Side Yard", "garden" if facing == "west" else "yard", box(0, min_ry, min_rx, max_ry)),
        ("Front Garden" if facing == "east" else "Side Yard", "garden" if facing == "east" else "yard", box(max_rx, min_ry, plot_w, max_ry))
    ]

    yards = []
    idx = 0
    for label, rtype, zone_box in zones:
        zone_geom = remaining_plot.intersection(zone_box)
        zone_polys = extract_polygons(zone_geom)
        
        for poly in zone_polys:
            poly_clean = poly.difference(occupied_union)
            clean_subpolys = extract_polygons(poly_clean)

            for clean_poly in clean_subpolys:
                if clean_poly.area < 2.0:
                    continue
                    
                bounds = clean_poly.bounds
                minx, miny, maxx, maxy = bounds
                
                # Format polygon points
                exterior_coords = list(clean_poly.exterior.coords)
                points = [{"x": round(p[0], 2), "y": round(p[1], 2)} for p in exterior_coords[:-1]]
                rep_y = clean_poly.representative_point()
                
                yards.append({
                    "id": f"yard_{idx}",
                    "type": rtype,
                    "label": label,
                    "x": round(minx, 2),
                    "y": round(miny, 2),
                    "width": round(maxx - minx, 2),
                    "length": round(maxy - miny, 2),
                    "area": round(clean_poly.area, 2),
                    "space_category": "outdoor",
                    "polygon": points,
                    "metadata": {"center": {"x": round(rep_y.x, 2), "y": round(rep_y.y, 2)}}
                })
                idx += 1

    return yards
