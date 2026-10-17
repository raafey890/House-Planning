import json
from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout

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

print("Solving layout...")
res = solve_layout(context, requirements)
print("Solve status:", res["status"])
layout = post_process_layout(res)

print("Generated layout:")
print(layout.model_dump_json(indent=2))

from app.validators.geometry_validator import GeometryValidator
print("Validating layout...")
passed, results = GeometryValidator.validate_layout(layout)
print("Passed:", passed)
print("Results:", json.dumps(results, indent=2))
