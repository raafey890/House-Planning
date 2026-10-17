"""
Full pipeline test for Phase 6C.8A Architectural Planning Quality Fix.
Tests:
1. 50x80 ft, South-facing, G+1, Modern (Target test)
2. 30x40 ft, East-facing, G+1 (Regression test)
"""
import sys
import os
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout
from app.services.planning.quality_scorer import compute_architectural_quality_score
from app.services.metrics import compute_floor_metrics
from app.validators.geometry_validator import GeometryValidator

print("=" * 80)
print("PHASE 6C.8A ARCHITECTURAL PLANNING QUALITY VERIFICATION")
print("=" * 80)

def run_test(name, context, requirements):
    print(f"\n{'='*30} TEST: {name} {'='*30}")
    t0 = time.time()
    engine_res = solve_layout(context, requirements)
    t_solve = time.time() - t0

    if engine_res.get("status") == "GEMINI_HYBRID" and "layout_data" in engine_res:
        layout_data = engine_res["layout_data"]
    else:
        layout_data = post_process_layout(engine_res)

    metrics = compute_floor_metrics(layout_data)
    try:
        valid, val_results = GeometryValidator.validate_layout(layout_data)
    except Exception as e:
        valid = False
        val_results = {"errors": str(e).split("\n")}
    quality = compute_architectural_quality_score(layout_data, engine_res.get("target_footprint"))

    print(f"Solver Status          : {engine_res.get('status')}")
    print(f"Planner Source         : {engine_res.get('planner_source', 'deterministic')}")
    print(f"Solve Time             : {t_solve:.2f}s")
    print(f"Candidates Evaluated   : {engine_res.get('candidates_evaluated', 1)}")
    print(f"Valid Candidates       : {engine_res.get('valid_candidates', 1)}")
    print(f"Selected Variant       : {engine_res.get('variant')} (seed {engine_res.get('seed')})")

    fp = layout_data.plot.building_footprint or {}
    fp_w = fp.get('width', 0)
    fp_l = fp.get('length', 0)
    fp_area = fp_w * fp_l
    plot_area = layout_data.plot.width * layout_data.plot.length
    build_area = layout_data.plot.buildable_boundary.width * layout_data.plot.buildable_boundary.length

    print(f"\nBuilding Footprint     : {fp_w} x {fp_l} ({fp_area} sq ft)")
    print(f"Plot Coverage          : {metrics['totals']['plot_coverage_pct']}% (Target: ~40-55%)")
    print(f"Buildable Coverage     : {metrics['totals']['buildable_coverage_pct']}% (Target: ~55-75%)")
    print(f"Internal Utilization   : {metrics['totals']['internal_building_utilization_pct']}%")

    print("\nFloors Summary:")
    for fl in layout_data.floors:
        indoor = fl.rooms
        outdoor = getattr(fl, "outdoor_areas", [])
        ind_area = sum(r.width * r.length for r in indoor)
        out_area = sum(r.area if r.area > 0 else r.width * r.length for r in outdoor)
        print(f"  Floor {fl.level} ({fl.name}):")
        print(f"    Indoor Rooms ({len(indoor)}, {ind_area:.0f} sq ft):")
        for r in indoor:
            print(f"      {r.type:18s} x={r.x:4.1f} y={r.y:4.1f} w={r.width:4.1f} h={r.length:4.1f} area={r.width*r.length:5.1f}")
        print(f"    Outdoor Spaces ({len(outdoor)}, {out_area:.0f} sq ft):")
        for r in outdoor:
            print(f"      {r.type:18s} {r.label:20s} w={r.width:4.1f} h={r.length:4.1f} area={r.area:5.1f}")
    if getattr(layout_data.plot, "site_areas", None):
        print(f"  Site Areas ({len(layout_data.plot.site_areas)}):")
        for s in layout_data.plot.site_areas:
            print(f"    {s.get('type'):18s} {s.get('label'):20s} w={s.get('width'):4.1f} h={s.get('length'):4.1f} area={s.get('area'):5.1f}")

    print("\nValidation Badges:")
    for k, v in val_results.items():
        if k != "errors":
            is_pass = v is True or (isinstance(v, (int, float)) and v <= 1000)
            print(f"  {'✅' if is_pass else '❌'} {k:22s} : {v}")
    if val_results.get("errors"):
        print("  Errors:", val_results["errors"])

    print(f"\nArchitectural Quality Score : {quality['total_score']} / 100")
    for cat, sc in quality["breakdown"].items():
        print(f"  - {cat:32s}: {sc}")

    return {
        "valid": valid,
        "quality_score": quality["total_score"],
        "plot_coverage": metrics['totals']['plot_coverage_pct'],
        "build_coverage": metrics['totals']['buildable_coverage_pct'],
        "internal_util": metrics['totals']['internal_building_utilization_pct'],
        "footprint": f"{fp_w}x{fp_l} ({fp_area} sq ft)",
        "val_results": val_results,
        "layout_data": layout_data
    }

# 1. TEST CASE 1: 50x80 South G+1 Modern
context_50x80 = {
    "plot_width": 50,
    "plot_length": 80,
    "facing": "south",
    "floors": 2,
    "number_of_floors": 2,
    "design_style": "modern",
    "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3},
    "parking_spaces": 1
}

reqs_50x80 = [{
    "bedrooms": 3,
    "bathrooms": 3,
    "kitchens": 1,
    "living_rooms": 1,
    "dining_rooms": 1,
    "parking_spaces": 1,
    "balconies": 1,
    "pooja_room": True,
    "study_room": True,
}]

res_50x80 = run_test("50x80 South G+1 Modern", context_50x80, reqs_50x80)

# 2. TEST CASE 2: 30x40 East G+1 Regression
context_30x40 = {
    "plot_width": 30,
    "plot_length": 40,
    "facing": "east",
    "floors": 2,
    "number_of_floors": 2,
    "design_style": "modern",
    "setbacks": {"front": 4, "rear": 3, "left": 3, "right": 3},
    "parking_spaces": 1
}

reqs_30x40 = [{
    "bedrooms": 2,
    "bathrooms": 2,
    "kitchens": 1,
    "living_rooms": 1,
    "dining_rooms": 1,
    "parking_spaces": 1,
    "balconies": 1,
}]

res_30x40 = run_test("30x40 East G+1 Modern (Regression)", context_30x40, reqs_30x40)

print("\n" + "=" * 80)
print("SUMMARY RESULTS:")
print(f"50x80 South G+1: Valid={res_50x80['valid']}, Quality={res_50x80['quality_score']}, Coverage={res_50x80['plot_coverage']}%, Footprint={res_50x80['footprint']}")
print(f"30x40 East G+1 : Valid={res_30x40['valid']}, Quality={res_30x40['quality_score']}, Coverage={res_30x40['plot_coverage']}%, Footprint={res_30x40['footprint']}")
print("=" * 80)
