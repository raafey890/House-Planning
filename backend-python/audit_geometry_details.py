import sys
import os
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout
from app.services.metrics import compute_floor_metrics

def audit_case(name, ctx, reqs):
    print("=" * 80)
    print(f"GEOMETRY & AREA AUDIT: {name}")
    print("=" * 80)
    res = solve_layout(ctx, reqs, use_gemini=False)
    layout = post_process_layout(res)

    plot = layout.plot
    print(f"Plot: {plot.width}x{plot.length} ft, Facing: {plot.facing}")
    print(f"Setbacks: {plot.setbacks}")
    print(f"Buildable Boundary: {plot.buildable_boundary}")
    print(f"Building Footprint BBox: {plot.building_footprint['width']}x{plot.building_footprint['length']} ft at ({plot.building_footprint['x']}, {plot.building_footprint['y']}), Area = {plot.building_footprint['constructed_area']} sq ft")

    for fl in layout.floors:
        print(f"\n--- FLOOR {fl.level}: {fl.name} ---")
        indoor_rooms = [r for r in fl.rooms if r.space_category != "outdoor"]
        outdoor_areas = getattr(fl, "outdoor_areas", [])

        # Build indoor geometries
        indoor_geoms = []
        for r in indoor_rooms:
            b = box(r.x, r.y, r.x + r.width, r.y + r.length)
            indoor_geoms.append((r, b))

        indoor_union = unary_union([b for _, b in indoor_geoms]) if indoor_geoms else Polygon()
        sum_indoor = sum(r.width * r.length for r in indoor_rooms)

        print(f"Indoor Rooms ({len(indoor_rooms)}):")
        print(f"  Sum of individual room areas: {sum_indoor:.1f} sq ft")
        print(f"  Unary union of room polygons: {indoor_union.area:.1f} sq ft")
        print(f"  Disjoint check (sum == union): {abs(sum_indoor - indoor_union.area) < 0.01}")

        # Indoor overlaps
        has_indoor_overlap = False
        for i in range(len(indoor_geoms)):
            for j in range(i + 1, len(indoor_geoms)):
                inter = indoor_geoms[i][1].intersection(indoor_geoms[j][1]).area
                if inter > 0.01:
                    print(f"  WARNING: Indoor overlap between {indoor_geoms[i][0].label} and {indoor_geoms[j][0].label}: {inter:.2f} sq ft")
                    has_indoor_overlap = True
        if not has_indoor_overlap:
            print("  Indoor pairwise overlap: NONE (all rooms strictly disjoint)")

        for r in indoor_rooms:
            print(f"    - {r.label:18s} ({r.type:14s}): bbox={r.width:.1f}x{r.length:.1f} ft at ({r.x:.1f},{r.y:.1f}), area={r.width*r.length:.1f} sq ft")

        # Outdoor areas
        print(f"\nOutdoor Areas ({len(outdoor_areas)}):")
        outdoor_geoms = []
        for o in outdoor_areas:
            if o.polygon and len(o.polygon) > 2:
                coords = [(p.x, p.y) for p in o.polygon]
                geom = Polygon(coords)
                geom_type = f"irregular polygon ({len(coords)} vertices)"
            else:
                geom = box(o.x, o.y, o.x + o.width, o.y + o.length)
                geom_type = "rectangle"

            outdoor_geoms.append((o, geom, geom_type))

        sum_outdoor = sum(o.area for o in outdoor_areas)
        print(f"  Sum of reported outdoor areas: {sum_outdoor:.1f} sq ft")

        for o, geom, geom_type in outdoor_geoms:
            minx, miny, maxx, maxy = geom.bounds
            bbox_w = round(maxx - minx, 1)
            bbox_l = round(maxy - miny, 1)
            bbox_area = round(bbox_w * bbox_l, 1)
            actual_poly_area = round(geom.area, 1)
            is_rect = abs(actual_poly_area - bbox_area) < 0.1

            print(f"    - {o.label:18s} ({o.type:10s}):")
            print(f"        Geometry Type     : {geom_type}")
            print(f"        BBox [x,y,w,l]    : ({o.x:.1f}, {o.y:.1f}, {o.width:.1f}, {o.length:.1f}) ft -> bbox area = {o.width*o.length:.1f} sq ft")
            print(f"        Actual Poly Bounds: ({minx:.1f}, {miny:.1f}, {bbox_w:.1f}, {bbox_l:.1f}) ft")
            print(f"        Actual Poly Area  : {actual_poly_area:.1f} sq ft")
            print(f"        Reported Area     : {o.area:.1f} sq ft")
            print(f"        Matches Reported? : {abs(actual_poly_area - o.area) < 0.1}")
            if o.polygon:
                pts_str = ", ".join([f"({p.x},{p.y})" for p in o.polygon])
                print(f"        Polygon Vertices  : [{pts_str}]")

            # Check overlap with indoor rooms on this floor
            inter_indoor = geom.intersection(indoor_union).area
            print(f"        Overlap w/ Indoor : {inter_indoor:.2f} sq ft ({'ZERO OVERLAP' if inter_indoor < 0.01 else 'OVERLAPS!'})")

        # Check pairwise outdoor overlap
        has_out_overlap = False
        for i in range(len(outdoor_geoms)):
            for j in range(i + 1, len(outdoor_geoms)):
                inter = outdoor_geoms[i][1].intersection(outdoor_geoms[j][1]).area
                if inter > 0.01:
                    print(f"  WARNING: Outdoor overlap between {outdoor_geoms[i][0].label} and {outdoor_geoms[j][0].label}: {inter:.2f} sq ft")
                    has_out_overlap = True
        if not has_out_overlap:
            print("  Outdoor pairwise overlap: NONE (all outdoor areas strictly disjoint)")

    # Upper floor vs GF slab analysis
    if len(layout.floors) > 1:
        gf = layout.floors[0]
        ff = layout.floors[1]
        gf_slab = unary_union([box(r.x, r.y, r.x + r.width, r.y + r.length) for r in gf.rooms if r.space_category != "outdoor"])
        ff_in_union = unary_union([box(r.x, r.y, r.x + r.width, r.y + r.length) for r in ff.rooms if r.space_category != "outdoor"])
        
        ff_in_on_gf = gf_slab.intersection(ff_in_union).area
        ff_in_outside_gf = ff_in_union.difference(gf_slab).area
        
        upper_out_geoms = []
        for o in getattr(ff, "outdoor_areas", []):
            if o.polygon and len(o.polygon) > 2:
                upper_out_geoms.append(Polygon([(p.x, p.y) for p in o.polygon]))
            else:
                upper_out_geoms.append(box(o.x, o.y, o.x + o.width, o.y + o.length))
        
        upper_out_union = unary_union(upper_out_geoms) if upper_out_geoms else Polygon()
        upper_out_on_gf = gf_slab.intersection(upper_out_union).area
        
        print("\n--- UPPER FLOOR (FF) SLAB & OVERHANG DECOMPOSITION ---")
        print(f"Ground Floor Slab Area               : {gf_slab.area:.1f} sq ft")
        print(f"First Floor Indoor Total Area        : {ff_in_union.area:.1f} sq ft")
        print(f"  - Overlap with GF Slab             : {ff_in_on_gf:.1f} sq ft ({ff_in_on_gf / gf_slab.area * 100:.1f}% of GF slab)")
        print(f"  - Overhang/Cantilever beyond GF    : {ff_in_outside_gf:.1f} sq ft")
        print(f"First Floor Outdoor Total Area       : {upper_out_union.area:.1f} sq ft")
        print(f"  - Overlap with GF Slab             : {upper_out_on_gf:.1f} sq ft")
        print(f"Sum on GF Slab (Indoor On GF + Out)  : {ff_in_on_gf + upper_out_on_gf:.1f} sq ft")
        print(f"Discrepancy against GF Slab          : {abs(gf_slab.area - (ff_in_on_gf + upper_out_on_gf)):.2f} sq ft")

audit_case(
    "50x80 South-Facing G+1",
    {"plot_width": 50, "plot_length": 80, "facing": "south", "floors": 2, "design_style": "modern", "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}, "parking_spaces": 0},
    [{"bedrooms": 3, "bathrooms": 2, "kitchens": 1, "living_rooms": 1, "parking_spaces": 0}]
)

audit_case(
    "30x40 East-Facing G+1",
    {"plot_width": 30, "plot_length": 40, "facing": "east", "floors": 2, "design_style": "modern", "setbacks": {"front": 4, "rear": 3, "left": 3, "right": 3}, "parking_spaces": 0},
    [{"bedrooms": 3, "bathrooms": 2, "kitchens": 1, "living_rooms": 1, "parking_spaces": 0}]
)
