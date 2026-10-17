from app.models.provider_schema import GeminiLayoutData
from app.models.layout import LayoutData
import json

mock_response = {
    "schema_version": "1.0",
    "units": "ft",
    "plot": {
        "width": 30.0,
        "length": 40.0,
        "facing": "East",
        "origin": {"x": 0.0, "y": 0.0},
        "buildable_boundary": {"width": 28.0, "length": 38.0},
        "setbacks": {"front": 1.0, "back": 1.0, "left": 1.0, "right": 1.0}
    },
    "floors": [],
    "metrics": {
        "total_area": 1200.0,
        "built_up_area": 1000.0,
        "carpet_area": 900.0,
        "coverage_percentage": 83.3
    },
    "generation_metadata": {
        "optimization_priority": "balanced",
        "model_used": "gemini-2.5-pro",
        "generation_time_ms": 1200
    }
}

try:
    # 1. Simulate Gemini producing the provider JSON
    provider_data = GeminiLayoutData(**mock_response)
    print("Provider schema validation passed")
    
    # 2. Simulate the backend converting it to the internal Pydantic model
    internal_data = LayoutData(**provider_data.model_dump())
    print("Internal schema validation passed")
    
except Exception as e:
    print("Validation failed:", e)
