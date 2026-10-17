import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from app.services.planning.area_program import build_area_program

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

prog = build_area_program(context_50x80, requirements)
print("=== 50x80 Area Program ===")
print("Buildable:", prog["buildable_width"], "x", prog["buildable_length"])
print("Target Footprint:", prog["target_footprint"])
print("Area Metrics:", prog["area_program_metrics"])
print("Floors Program:")
for fl, r_list in prog["floors_program"].items():
    print(f"  Floor {fl}: {len(r_list)} rooms:")
    for r in r_list:
        sp = r["specs"]
        print(f"    {r['type']:18s} min={sp['min_w']}x{sp['min_h']} ({sp['min_area']}) pref={sp['pref_w']}x{sp['pref_h']} ({sp['pref_area']})")
