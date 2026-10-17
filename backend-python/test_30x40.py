import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.planning.area_program import build_area_program

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

prog = build_area_program(context_30x40, reqs_30x40)
print("=== 30x40 Area Program ===")
print("Buildable:", prog["buildable_width"], "x", prog["buildable_length"])
print("Target Footprint:", prog["target_footprint"])
print("Floors Program:")
for fl, r_list in prog["floors_program"].items():
    print(f"  Floor {fl}: {len(r_list)} rooms:")
    tot_min = 0
    tot_pref = 0
    for r in r_list:
        sp = r["specs"]
        tot_min += sp["min_area"]
        tot_pref += sp["pref_area"]
        print(f"    {r['type']:18s} min={sp['min_w']}x{sp['min_h']} ({sp['min_area']}) pref={sp['pref_w']}x{sp['pref_h']} ({sp['pref_area']})")
    print(f"  Total min={tot_min}, Total pref={tot_pref}")
