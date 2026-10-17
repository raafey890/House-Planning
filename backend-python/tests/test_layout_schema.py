import pytest
from app.models.layout import LayoutData

def test_valid_schema():
    payload = {
        "schema_version": "1.0",
        "units": "ft",
        "plot": {
            "width": 50,
            "length": 80,
            "facing": "North",
            "buildable_boundary": {"width": 40, "length": 60},
            "setbacks": {"front": 10, "back": 10, "left": 5, "right": 5}
        },
        "floors": [
            {
                "level": 0,
                "name": "Ground",
                "rooms": [
                    {
                        "id": "r1",
                        "type": "bedroom",
                        "label": "Master",
                        "x": 10,
                        "y": 10,
                        "width": 12,
                        "length": 14,
                        "area": 168.0
                    }
                ]
            }
        ]
    }
    
    layout = LayoutData(**payload)
    assert layout.plot.width == 50
    assert layout.floors[0].rooms[0].label == "Master"
