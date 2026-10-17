import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, r"C:\Users\DELL\OneDrive\Desktop\House plaining\backend-python")

from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout
from app.validators.geometry_validator import GeometryValidator

context = {
    "plot_width": 50,
    "plot_length": 80,
    "facing": "south",
    "floors": 2,
    "setbacks": {"front": 5, "rear": 4, "left": 4, "right": 4}
}
requirements = [
    {"room_type": "living_room", "count": 1, "floor_level": 0},
    {"room_type": "dining_room", "count": 1, "floor_level": 0},
    {"room_type": "kitchen", "count": 1, "floor_level": 0},
    {"room_type": "parking", "count": 1, "floor_level": 0},
    {"room_type": "utility_room", "count": 1, "floor_level": 0},
    {"room_type": "bedroom", "count": 1, "floor_level": 0},
    {"room_type": "bathroom", "count": 1, "floor_level": 0},
    {"room_type": "staircase", "count": 1, "floor_level": 0},
    {"room_type": "staircase", "count": 1, "floor_level": 1},
    {"room_type": "master_bedroom", "count": 1, "floor_level": 1},
    {"room_type": "bedroom", "count": 2, "floor_level": 1},
    {"room_type": "study_room", "count": 1, "floor_level": 1},
    {"room_type": "balcony", "count": 1, "floor_level": 1},
    {"room_type": "bathroom", "count": 2, "floor_level": 1}
]

print("=== 1. SOLVING LAYOUT ===")
engine_res = solve_layout(context, requirements)
print(f"Status: {engine_res['status']}")
print(f"Solve time: {engine_res['solve_time']}s")
for fl, rms in engine_res["floors"].items():
    print(f"Floor {fl}: {len(rms)} rooms")
    for r in rms:
        print(f"  - {r['type']}: pos=({r['x']}, {r['y']}), size={r['width']}x{r['length']}, area={r['area']}")

print("\n=== 2. POST PROCESSING ===")
layout_data = post_process_layout(engine_res)
print(f"Building Footprint: {layout_data.plot.building_footprint}")
for fl in layout_data.floors:
    print(f"Floor {fl.level} ({fl.name}): {len(fl.rooms)} rooms")
    indoor_cnt = sum(1 for r in fl.rooms if r.space_category not in ["outdoor", "circulation"])
    outdoor_cnt = sum(1 for r in fl.rooms if r.space_category == "outdoor")
    print(f"  Indoor: {indoor_cnt}, Outdoor: {outdoor_cnt}")
    for r in fl.rooms:
        print(f"  - [{r.type}] '{r.label}': pos=({r.x}, {r.y}), size={r.width}x{r.length}, area={r.area}, cat={r.space_category}, has_poly={bool(r.polygon)}")

print("\n=== 3. GEOMETRY VALIDATION ===")
passed, res = GeometryValidator.validate_layout(layout_data)
print(f"Passed: {passed}, errors: {res.get('errors')}")
