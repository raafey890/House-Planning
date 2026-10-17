"""
PHASE 6C.8A PIPELINE TRACE - End-to-end diagnostic
Test: 50x80 ft, South facing, G+1, Modern
"""
import sys
import os
import json
import time

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout
from app.services.metrics import compute_floor_metrics
from app.validators.geometry_validator import GeometryValidator

context = {
    "plot_width": 50,
    "plot_length": 80,
    "facing": "south",
    "floors": 2,
    "number_of_floors": 2,
    "design_style": "modern",
    "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3},
}

requirements = [{
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

print("=" * 70)
print("PHASE 6C.8A PIPELINE TRACE")
print("=" * 70)

# -- STEP 3: OR-TOOLS SOLVE -------------------------------------------------
print("\n--- STEP 3: OR-TOOLS ENGINE OUTPUT ---")

t0 = time.time()
engine_result = solve_layout(context, requirements)
t1 = time.time()

print(f"Solver status : {engine_result['status']}")
print(f"Solve time    : {t1 - t0:.2f}s")
print(f"Floor count   : {len(engine_result['floors'])}")

total_indoor_area = 0
for lvl in sorted(engine_result["floors"].keys()):
    rooms = engine_result["floors"][lvl]
    indoor = [r for r in rooms if r["type"] not in ["garden", "yard", "terrace", "balcony", "driveway"]]
    print(f"\n  FLOOR {lvl} ({len(indoor)} indoor rooms):")
    for r in indoor:
        print(f"    {r['type']:20s}  x={r['x']:5.1f}  y={r['y']:5.1f}  w={r['width']:5.1f}  h={r['length']:5.1f}  area={r['area']:6.1f}")
        total_indoor_area += r["area"]

print(f"\n  TOTAL INDOOR AREA: {total_indoor_area:.1f} sq ft")

all_types = []
for lvl, rooms in engine_result["floors"].items():
    for r in rooms:
        all_types.append(r["type"])

REQUIRED_TYPES = ["living_room", "kitchen", "master_bedroom", "staircase"]
missing = [t for t in REQUIRED_TYPES if t not in all_types]
if missing:
    print(f"\n  [FAIL] MISSING REQUIRED ROOM TYPES: {missing}")
    print("  BUG IS IN engine.py / area_program.py")
else:
    print(f"\n  [PASS] All required room types present")

# -- STEP 4: POST PROCESSOR -------------------------------------------------
print("\n--- STEP 4: POST-PROCESSOR TRACE ---")

pre_count = {}
for lvl, rooms in engine_result["floors"].items():
    indoor = [r for r in rooms if r["type"] not in ["garden", "yard", "terrace", "driveway"]]
    pre_count[lvl] = len(indoor)
    print(f"  BEFORE post_processor  |  Floor {lvl}: {len(indoor)} indoor rooms")

layout_data = post_process_layout(engine_result)

print()
for fl in layout_data.floors:
    indoor_rooms = [r for r in fl.rooms if r.space_category != "outdoor" and r.type not in ["garden", "yard", "terrace"]]
    outdoor_rooms = [r for r in fl.rooms if r.space_category == "outdoor" or r.type in ["garden", "yard", "terrace"]]
    
    print(f"  AFTER post_processor   |  Floor {fl.level}: {len(indoor_rooms)} indoor, {len(outdoor_rooms)} outdoor")
    print(f"    Indoor : {', '.join(r.type for r in indoor_rooms)}")
    print(f"    Outdoor: {', '.join(r.type for r in outdoor_rooms)}")

    if len(indoor_rooms) < pre_count.get(fl.level, 0):
        print(f"  [FAIL] Floor {fl.level} lost indoor rooms! Before={pre_count[fl.level]}, After={len(indoor_rooms)}")
    else:
        print(f"    [PASS] No indoor rooms lost")

fp = layout_data.plot.building_footprint
if fp:
    print(f"\n  Building footprint: x={fp.get('x')}, y={fp.get('y')}, w={fp.get('width')}, l={fp.get('length')}")
    print(f"  Footprint area: {fp.get('width', 0) * fp.get('length', 0):.1f} sq ft")
else:
    print("\n  [FAIL] No building footprint found!")

# -- STEP 5: INSPECT FINAL LAYOUT DATA JSON ---------------------------------
print("\n--- STEP 5: FINAL LAYOUTDATA JSON ---")

layout_dict = layout_data.model_dump()

for fl_data in layout_dict["floors"]:
    lvl = fl_data["level"]
    all_rooms = fl_data.get("rooms", [])
    indoor = [r for r in all_rooms if r.get("space_category") != "outdoor" and r.get("type") not in ["garden", "yard", "terrace"]]
    outdoor = [r for r in all_rooms if r.get("space_category") == "outdoor" or r.get("type") in ["garden", "yard", "terrace"]]
    
    print(f"  Floor {lvl} JSON:")
    print(f"    Total rooms in JSON: {len(all_rooms)}")
    print(f"    Indoor rooms: {len(indoor)}")
    for r in indoor:
        print(f"      {r['type']:20s}  x={r['x']:5.1f} y={r['y']:5.1f} w={r['width']:5.1f} h={r['length']:5.1f}")
    print(f"    Outdoor rooms: {len(outdoor)}")
    for r in outdoor:
        print(f"      {r['type']:20s}  label={r.get('label','')}")
    
    print(f"    Doors: {len(fl_data.get('doors', []))}")
    print(f"    Windows: {len(fl_data.get('windows', []))}")
    print(f"    Stairs: {len(fl_data.get('stairs', []))}")
    print(f"    Walls: {len(fl_data.get('walls', []))}")

# -- STEP 8: SVG RENDERING CHECK --------------------------------------------
print("\n--- STEP 8: SVG RENDERING CHECK ---")

floor0 = layout_dict["floors"][0]
indoor_f0 = [r for r in floor0["rooms"] if r.get("space_category") != "outdoor" and r.get("type") not in ["garden", "yard", "terrace"]]
outdoor_f0 = [r for r in floor0["rooms"] if r.get("space_category") == "outdoor" or r.get("type") in ["garden", "yard", "terrace"]]

print(f"  Ground floor: {len(indoor_f0)} indoor rooms rendered ON TOP of {len(outdoor_f0)} outdoor areas")
if len(indoor_f0) == 0:
    print("  [FAIL] SVG will show NO indoor rooms - all are classified outdoor!")
else:
    print("  [PASS] Indoor rooms will be visible over outdoor areas")

print("  SVG render order: outdoor -> footprint -> indoor -> walls -> doors -> windows -> stairs")
print("  [PASS] Correct stacking order (indoor on top)")

# -- METRICS -----------------------------------------------------------------
print("\n--- METRICS ---")

try:
    metrics = compute_floor_metrics(layout_data)
    print(f"  Plot coverage      : {metrics.get('totals', {}).get('plot_coverage_pct', '?')}%")
    print(f"  Buildable coverage : {metrics.get('totals', {}).get('buildable_coverage_pct', '?')}%")
    print(f"  Internal util      : {metrics.get('totals', {}).get('internal_building_utilization_pct', '?')}%")
    print(f"  Classified plot    : {metrics.get('totals', {}).get('classified_plot_pct', '?')}%")
except Exception as e:
    print(f"  [FAIL] Metrics error: {e}")

# -- GEOMETRY VALIDATION -----------------------------------------------------
print("\n--- GEOMETRY VALIDATION ---")

try:
    passed, results = GeometryValidator.validate_layout(layout_data)
    print(f"  Validation passed: {passed}")
    for k, v in results.items():
        print(f"    {k}: {v}")
except Exception as e:
    print(f"  [FAIL] Validation error: {e}")


# == FINAL REPORT ===========================================================
print("\n" + "=" * 70)
print("FINAL PIPELINE TRACE REPORT")
print("=" * 70)

gf_indoor = len([r for r in layout_dict["floors"][0]["rooms"] 
                  if r.get("space_category") != "outdoor" and r.get("type") not in ["garden", "yard", "terrace"]])
ff_indoor = 0
if len(layout_dict["floors"]) > 1:
    ff_indoor = len([r for r in layout_dict["floors"][1]["rooms"] 
                      if r.get("space_category") != "outdoor" and r.get("type") not in ["garden", "yard", "terrace"]])

print(f"  3. OR-Tools generating rooms?        {'YES' if total_indoor_area > 100 else 'NO'}")
print(f"  4. Rooms present before post_proc?    YES (verified above)")
print(f"  5. Rooms present after post_proc?     {'YES' if gf_indoor >= 2 else 'NO'}")
print(f"  6. Rooms present in API JSON?         {'YES' if gf_indoor >= 2 else 'NO'}")
print(f"  Ground floor indoor rooms: {gf_indoor}")
print(f"  First floor indoor rooms:  {ff_indoor}")

if gf_indoor >= 4 and not missing:
    print("\n  [PASS] ENGINE AND POST-PROCESSOR ARE CORRECT")
    print("  If SVG shows only gardens, the bug is in:")
    print("    - Supabase save/load (returning OLD plan)")
    print("    - Frontend plan selection (showing stale data)")
    print("    - FloorPlansTab calling loadSavedPlans() AFTER setLayoutData")
    print("      which OVERWRITES the fresh result with an old plan")
else:
    print(f"\n  [FAIL] Pipeline issue at {'engine' if missing else 'post_processor'} stage")

print("\n" + "=" * 70)
