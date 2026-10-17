import os
os.environ['GEMINI_API_KEY'] = 'test'
import pytest
from unittest.mock import patch, MagicMock
from app.models.layout import LayoutData
from app.api.routes.floor_plans import generate_floor_plan, GenerateRequest
from fastapi import HTTPException

# Mock context
MOCK_CONTEXT = {
    "project_id": "test-project",
    "plot_width": 50,
    "plot_length": 80,
    "facing": "North",
    "floors": 1,
    "budget": 100000,
    "design_style": "Modern",
    "interior_style": "Minimal",
    "bedrooms": 2,
    "bathrooms": 1,
    "kitchens": 1,
    "living_rooms": 1,
    "balconies": 0,
    "custom_notes": ""
}

# Mock LayoutData
MOCK_LAYOUT_DATA = LayoutData(**{
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
                {"id": "r1", "type": "bed", "label": "B1", "x": 10, "y": 10, "width": 10, "length": 10, "area": 100}
            ]
        }
    ]
})

@pytest.mark.asyncio
@patch("app.api.routes.floor_plans.project_service.verify_ownership", return_value=True)
@patch("app.api.routes.floor_plans.project_service.get_planning_context", return_value=MOCK_CONTEXT)
@patch("app.api.routes.floor_plans.FloorplanService.create_generation_job", return_value="job-123")
@patch("app.api.routes.floor_plans.FloorplanService.update_generation_job")
@patch("app.api.routes.floor_plans.FloorplanService.save_floor_plan", return_value="fp-123")
@patch("app.api.routes.floor_plans.GeminiProvider.generate_layout")
async def test_successful_generation(
    mock_generate, mock_save, mock_update, mock_create, mock_context, mock_verify
):
    # Setup mock to return valid layout
    mock_generate.return_value = MOCK_LAYOUT_DATA
    
    response = await generate_floor_plan("test-project", GenerateRequest(), "user-123")
    
    assert response.status == "completed"
    assert response.floor_plan_id == "fp-123"
    assert response.validation["valid"] is True
    mock_save.assert_called_once()
    mock_update.assert_called_with("job-123", "Completed", MOCK_LAYOUT_DATA.model_dump())

@pytest.mark.asyncio
@patch("app.api.routes.floor_plans.project_service.verify_ownership", return_value=True)
@patch("app.api.routes.floor_plans.project_service.get_planning_context", return_value=MOCK_CONTEXT)
@patch("app.api.routes.floor_plans.FloorplanService.create_generation_job", return_value="job-123")
@patch("app.api.routes.floor_plans.FloorplanService.update_generation_job")
@patch("app.api.routes.floor_plans.GeminiProvider.generate_layout")
async def test_failed_generation_geometry_error(
    mock_generate, mock_update, mock_create, mock_context, mock_verify
):
    from app.validators.geometry_validator import GeometryValidationError
    
    # Setup mock to raise Geometry Error
    mock_generate.side_effect = GeometryValidationError("Overlap detected")
    
    response = await generate_floor_plan("test-project", GenerateRequest(), "user-123")
    
    assert response.status == "failed"
    assert response.validation["valid"] is False
    assert "Geometry Error: Overlap detected" in response.validation["errors"]
    
    # Check that it retried 3 times (range(3))
    assert mock_generate.call_count == 3
    mock_update.assert_called_with("job-123", "Failed", error_message="Geometry Error: Overlap detected")

@pytest.mark.asyncio
@patch("app.api.routes.floor_plans.project_service.verify_ownership", return_value=False)
async def test_unauthorized_project_access(mock_verify):
    with pytest.raises(HTTPException) as excinfo:
        await generate_floor_plan("test-project", GenerateRequest(), "wrong-user")
    
    assert excinfo.value.status_code == 403
