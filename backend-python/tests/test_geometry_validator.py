import pytest
from app.models.layout import LayoutData
from app.validators.geometry_validator import GeometryValidator, GeometryValidationError

def create_synthetic_layout(rooms_data: list) -> LayoutData:
    payload = {
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
                "rooms": rooms_data,
                "doors": [
                    {"id": "d_main", "type": "main_entrance", "position": {"x": 5.0, "y": 10.0}, "width": 3.0, "room_ids": ["r1"]}
                ]
            }
        ]
    }
    return LayoutData(**payload)

def test_valid_geometry():
    layout = create_synthetic_layout([
        {"id": "r1", "type": "bed", "label": "B1", "x": 5, "y": 10, "width": 10, "length": 10, "area": 100},
        {"id": "r2", "type": "bed", "label": "B2", "x": 15, "y": 10, "width": 10, "length": 10, "area": 100}
    ])
    valid, results = GeometryValidator.validate_layout(layout)
    assert valid is True

def test_room_outside_plot():
    layout = create_synthetic_layout([
        # Setbacks are left:5, front:10. Buildable area is x:5..45, y:10..70
        # Placing room at x=0 violates the left setback
        {"id": "r1", "type": "bed", "label": "B1", "x": 0, "y": 10, "width": 10, "length": 10, "area": 100}
    ])
    with pytest.raises(GeometryValidationError, match="outside the buildable boundary"):
        GeometryValidator.validate_layout(layout)

def test_overlapping_rooms():
    layout = create_synthetic_layout([
        {"id": "r1", "type": "bed", "label": "B1", "x": 5, "y": 10, "width": 10, "length": 10, "area": 100},
        {"id": "r2", "type": "bed", "label": "B2", "x": 10, "y": 10, "width": 10, "length": 10, "area": 100} # Overlaps from x=10..15
    ])
    with pytest.raises(GeometryValidationError, match="overlaps with"):
        GeometryValidator.validate_layout(layout)

def test_negative_dimensions():
    layout = create_synthetic_layout([
        {"id": "r1", "type": "bed", "label": "B1", "x": 5, "y": 10, "width": -5, "length": 10, "area": -50}
    ])
    with pytest.raises(GeometryValidationError, match="dimensions must be positive"):
        GeometryValidator.validate_layout(layout)

def test_area_inconsistency():
    layout = create_synthetic_layout([
        {"id": "r1", "type": "bed", "label": "B1", "x": 5, "y": 10, "width": 10, "length": 10, "area": 150} # 10x10 != 150
    ])
    with pytest.raises(GeometryValidationError, match="area inconsistency"):
        GeometryValidator.validate_layout(layout)
