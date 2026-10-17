"""
CATEGORY B: FRESH SOLVER VALIDATION TEST SUITE
==============================================
Explicitly executes fresh CP-SAT optimizations through solve_layout().
Validates programmatic correctness, architectural constraints,
and geometric slab reconciliation on newly generated layouts.
DOES NOT overwrite or modify canonical JSON files or canonical SVGs.
"""
import sys
import os
import copy
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.models.layout import LayoutData, Plot, Floor, Room, Point2D
from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout
from app.services.metrics import compute_floor_metrics

def test_outdoor_spaces_cannot_increase_indoor_room_count():
    print("\n--- TEST B1: Outdoor Space Segregation Regression ---")
    base_rooms = [
        Room(id="r1", type="master_bedroom", label="Master Bedroom", x=10, y=10, width=15, length=15, area=225, space_category="private"),
        Room(id="r2", type="bedroom", label="Bedroom 2", x=25, y=10, width=12, length=14, area=168, space_category="private"),
        Room(id="r3", type="bathroom", label="Bathroom", x=10, y=25, width=6, length=8, area=48, space_category="private")
    ]
    base_indoor_count = len(base_rooms)
    base_indoor_area = sum(r.width * r.length for r in base_rooms)

    layout = LayoutData(
        plot=Plot(
            width=50, length=80, facing="south", front_side="south",
            setbacks={"front": 4, "rear": 4, "left": 3, "right": 3},
            buildable_boundary={"width": 44, "length": 72},
            building_footprint={"x": 10, "y": 10, "width": 27, "length": 23, "constructed_area": base_indoor_area, "bounding_area": 621.0}
        ),
        floors=[
            Floor(level=0, name="Ground Floor", rooms=[], outdoor_areas=[]),
            Floor(level=1, name="First Floor", rooms=copy.deepcopy(base_rooms), outdoor_areas=[])
        ]
    )

    metrics_before = compute_floor_metrics(layout)
    ff_m_before = metrics_before["floors"][1]

    # Inject outdoor spaces
    layout_with_outdoor = copy.deepcopy(layout)
    layout_with_outdoor.floors[1].rooms.append(
        Room(id="terrace_test", type="terrace", label="Open Terrace", x=16, y=25, width=10, length=8, area=80, space_category="outdoor")
    )
    layout_with_outdoor.floors[1].rooms.append(
        Room(id="garden_test", type="garden", label="Roof Garden", x=0, y=0, width=10, length=5, area=50, space_category="outdoor")
    )
    layout_with_outdoor.floors[1].outdoor_areas.append(
        Room(id="balcony_test", type="balcony", label="Balcony", x=26, y=25, width=6, length=4, area=24, space_category="outdoor")
    )

    metrics_after = compute_floor_metrics(layout_with_outdoor)
    ff_m_after = metrics_after["floors"][1]

    assert ff_m_after["indoor_room_count"] == base_indoor_count, "Outdoor room leaked into indoor count!"
    assert ff_m_after["indoor_room_area"] == base_indoor_area, "Outdoor area leaked into indoor area!"
    print(f">>> PASS B1: Adding outdoor spaces CANNOT increase indoor room count or area.")

def test_fresh_solver_50x80():
    print("\n--- TEST B2: Fresh CP-SAT Solver Run [50×80 South-Facing G+1] ---")
    print("NOTE: This runs a live solver optimization. Results are dynamic and separate from frozen canonical records.")
    ctx = {
        "plot_width": 50, "plot_length": 80, "facing": "south", "floors": 2,
        "design_style": "modern", "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3},
        "parking_spaces": 0
    }
    reqs = [{"bedrooms": 3, "bathrooms": 2, "kitchens": 1, "living_rooms": 1, "parking_spaces": 0}]

    res = solve_layout(ctx, reqs, use_gemini=False)
    layout = post_process_layout(res)

    gf = layout.floors[0]
    ff = layout.floors[1]

    gf_indoor = [r for r in gf.rooms if getattr(r, 'space_category', '') != 'outdoor']
    ff_indoor = [r for r in ff.rooms if getattr(r, 'space_category', '') != 'outdoor']
    ff_outdoor = getattr(ff, "outdoor_areas", [])

    total_beds = sum(1 for fl in layout.floors for r in fl.rooms if "bedroom" in r.type)
    total_baths = sum(1 for fl in layout.floors for r in fl.rooms if "bath" in r.type)

    assert total_beds == 3, f"Expected 3 bedrooms, got {total_beds}"
    assert total_baths == 2, f"Expected 2 bathrooms, got {total_baths}"

    gf_boxes = [box(r.x, r.y, r.x+r.width, r.y+r.length) for r in gf_indoor]
    gf_slab = unary_union(gf_boxes)
    gf_sum = sum(r.width * r.length for r in gf_indoor)
    assert abs(gf_sum - gf_slab.area) < 0.01, "GF indoor rooms overlap!"

    ff_boxes = [box(r.x, r.y, r.x+r.width, r.y+r.length) for r in ff_indoor]
    ff_in_poly = unary_union(ff_boxes)
    ff_sum = sum(r.width * r.length for r in ff_indoor)
    assert abs(ff_sum - ff_in_poly.area) < 0.01, "FF indoor rooms overlap!"

    ff_in_on_gf = gf_slab.intersection(ff_in_poly).area
    ff_cantilever = ff_in_poly.difference(gf_slab).area

    ff_out_polys = []
    for o in ff_outdoor:
        if o.polygon and len(o.polygon) > 2:
            ff_out_polys.append(Polygon([(p.x, p.y) for p in o.polygon]))
        else:
            ff_out_polys.append(box(o.x, o.y, o.x+o.width, o.y+o.length))

    upper_out_on_gf = sum(gf_slab.intersection(p).area for p in ff_out_polys)
    reconciled = ff_in_on_gf + upper_out_on_gf
    diff = abs(gf_slab.area - reconciled)

    print(f"  [FRESH SOLVER RUN] GF Slab Area     : {gf_slab.area:.1f} sq ft ({len(gf_indoor)} rooms)")
    print(f"  [FRESH SOLVER RUN] FF Indoor Total  : {ff_in_poly.area:.1f} sq ft ({len(ff_indoor)} rooms)")
    print(f"  [FRESH SOLVER RUN] FF on GF Overlap : {ff_in_on_gf:.1f} sq ft")
    print(f"  [FRESH SOLVER RUN] FF Cantilever    : {ff_cantilever:.1f} sq ft")
    print(f"  [FRESH SOLVER RUN] FF Outdoor on GF : {upper_out_on_gf:.1f} sq ft ({len(ff_outdoor)} outdoor areas)")
    print(f"  [FRESH SOLVER RUN] Slab Discrepancy : {diff:.4f} sq ft")

    assert diff < 0.01, f"Fresh solve slab discrepancy {diff:.4f} exceeds 0.01 sq ft!"
    print(f">>> PASS B2: Fresh 50×80 layout validated with 0.00 sq ft slab discrepancy.")

def test_fresh_solver_30x40():
    print("\n--- TEST B3: Fresh CP-SAT Solver Run [30×40 East-Facing G+1] ---")
    print("NOTE: This runs a live solver optimization. Results are dynamic and separate from frozen canonical records.")
    ctx = {
        "plot_width": 30, "plot_length": 40, "facing": "east", "floors": 2,
        "design_style": "modern", "setbacks": {"front": 4, "rear": 3, "left": 3, "right": 3},
        "parking_spaces": 0
    }
    reqs = [{"bedrooms": 3, "bathrooms": 2, "kitchens": 1, "living_rooms": 1, "parking_spaces": 0}]

    res = solve_layout(ctx, reqs, use_gemini=False)
    layout = post_process_layout(res)

    gf = layout.floors[0]
    ff = layout.floors[1]

    gf_indoor = [r for r in gf.rooms if getattr(r, 'space_category', '') != 'outdoor']
    ff_indoor = [r for r in ff.rooms if getattr(r, 'space_category', '') != 'outdoor']
    ff_outdoor = getattr(ff, "outdoor_areas", [])

    total_beds = sum(1 for fl in layout.floors for r in fl.rooms if "bedroom" in r.type)
    total_baths = sum(1 for fl in layout.floors for r in fl.rooms if "bath" in r.type)

    assert total_beds == 3, f"Expected 3 bedrooms, got {total_beds}"
    assert total_baths == 2, f"Expected 2 bathrooms, got {total_baths}"

    gf_boxes = [box(r.x, r.y, r.x+r.width, r.y+r.length) for r in gf_indoor]
    gf_slab = unary_union(gf_boxes)
    gf_sum = sum(r.width * r.length for r in gf_indoor)
    assert abs(gf_sum - gf_slab.area) < 0.01, "GF indoor rooms overlap!"

    ff_boxes = [box(r.x, r.y, r.x+r.width, r.y+r.length) for r in ff_indoor]
    ff_in_poly = unary_union(ff_boxes)
    ff_sum = sum(r.width * r.length for r in ff_indoor)
    assert abs(ff_sum - ff_in_poly.area) < 0.01, "FF indoor rooms overlap!"

    ff_in_on_gf = gf_slab.intersection(ff_in_poly).area
    ff_cantilever = ff_in_poly.difference(gf_slab).area

    ff_out_polys = []
    for o in ff_outdoor:
        if o.polygon and len(o.polygon) > 2:
            ff_out_polys.append(Polygon([(p.x, p.y) for p in o.polygon]))
        else:
            ff_out_polys.append(box(o.x, o.y, o.x+o.width, o.y+o.length))

    upper_out_on_gf = sum(gf_slab.intersection(p).area for p in ff_out_polys)
    reconciled = ff_in_on_gf + upper_out_on_gf
    diff = abs(gf_slab.area - reconciled)

    print(f"  [FRESH SOLVER RUN] GF Slab Area     : {gf_slab.area:.1f} sq ft ({len(gf_indoor)} rooms)")
    print(f"  [FRESH SOLVER RUN] FF Indoor Total  : {ff_in_poly.area:.1f} sq ft ({len(ff_indoor)} rooms)")
    print(f"  [FRESH SOLVER RUN] FF on GF Overlap : {ff_in_on_gf:.1f} sq ft")
    print(f"  [FRESH SOLVER RUN] FF Cantilever    : {ff_cantilever:.1f} sq ft")
    print(f"  [FRESH SOLVER RUN] FF Outdoor on GF : {upper_out_on_gf:.1f} sq ft ({len(ff_outdoor)} outdoor areas)")
    print(f"  [FRESH SOLVER RUN] Slab Discrepancy : {diff:.4f} sq ft")

    assert diff < 0.01, f"Fresh solve slab discrepancy {diff:.4f} exceeds 0.01 sq ft!"
    print(f">>> PASS B3: Fresh 30×40 layout validated with 0.00 sq ft slab discrepancy.")

if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("STARTING CATEGORY B: FRESH SOLVER VALIDATION TESTS")
    print("#" * 80)

    test_outdoor_spaces_cannot_increase_indoor_room_count()
    test_fresh_solver_50x80()
    test_fresh_solver_30x40()

    print("\n" + "=" * 80)
    print("ALL FRESH SOLVER VALIDATION TESTS PASSED WITH 0.00 SQ FT DISCREPANCY!")
    print("=" * 80)
