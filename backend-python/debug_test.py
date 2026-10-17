from ortools.sat.python import cp_model
from app.services.planning.area_program import build_area_program

context = {
    "plot_width": 50,
    "plot_length": 80,
    "facing": "south",
    "setbacks": {"front": 5, "rear": 5, "left": 5, "right": 5}
}

requirements = [
    {"room_type": "living_room", "count": 1, "floor_level": 0},
    {"room_type": "kitchen", "count": 1, "floor_level": 0},
    {"room_type": "bedroom", "count": 1, "floor_level": 0},
    {"room_type": "bathroom", "count": 1, "floor_level": 0},
    {"room_type": "parking", "count": 1, "floor_level": 0},
    {"room_type": "master_bedroom", "count": 1, "floor_level": 1},
    {"room_type": "bedroom", "count": 1, "floor_level": 1},
    {"room_type": "bathroom", "count": 2, "floor_level": 1},
    {"room_type": "staircase", "count": 1, "floor_level": 0},
    {"room_type": "staircase", "count": 1, "floor_level": 1}
]

program = build_area_program(context, requirements)
print("Program built successfully!")
for fl, rms in program["floors_program"].items():
    print(f"Floor {fl}: {[r['type'] for r in rms]}")
