import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Test what happens when bedrooms for 2-bed G+1 are placed upstairs
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

# In G+1 with 2 bedrooms and parking, bedrooms are upstairs:
reqs_30x40 = [{
    "bedrooms": 2,
    "bathrooms": 2,
    "kitchens": 1,
    "living_rooms": 1,
    "dining_rooms": 1,
    "parking_spaces": 1,
    "balconies": 1,
}]
