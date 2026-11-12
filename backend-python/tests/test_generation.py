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
                {"id": "r1", "type": "bedroom", "label": "B1", "x": 10, "y": 10, "width": 10, "length": 10, "area": 100},
                {"id": "r2", "type": "living_room", "label": "Living", "x": 20, "y": 10, "width": 15, "length": 15, "area": 225}
            ],
            "doors": [
                {"id": "d1", "type": "main_entrance", "position": {"x": 20.0, "y": 10.0}, "width": 3.0}
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
@patch("app.services.planning.engine.solve_layout")
async def test_successful_generation(
    mock_solve, mock_save, mock_update, mock_create, mock_context, mock_verify
):
    mock_supabase = MagicMock()
    mock_supabase.table().select().eq().execute.return_value.data = []

    # Setup mock to return valid layout
    mock_solve.return_value = {
        "status": "GEMINI_HYBRID",
        "layout_data": MOCK_LAYOUT_DATA,
        "planner_source": "gemini"
    }
    
    response = await generate_floor_plan("test-project", GenerateRequest(), "user-123", mock_supabase)
    
    assert response.status == "completed"
    assert response.floor_plan_id == "fp-123"
    assert response.validation["valid"] is True
    mock_save.assert_called_once()
    mock_update.assert_called_with(mock_supabase, "job-123", "Completed", MOCK_LAYOUT_DATA.model_dump())

@pytest.mark.asyncio
@patch("app.api.routes.floor_plans.project_service.verify_ownership", return_value=True)
@patch("app.api.routes.floor_plans.project_service.get_planning_context", return_value=MOCK_CONTEXT)
@patch("app.api.routes.floor_plans.FloorplanService.create_generation_job", return_value="job-123")
@patch("app.api.routes.floor_plans.FloorplanService.update_generation_job")
@patch("app.services.planning.engine.solve_layout")
async def test_failed_generation_geometry_error(
    mock_solve, mock_update, mock_create, mock_context, mock_verify
):
    from app.validators.geometry_validator import GeometryValidationError
    import json
    
    mock_supabase = MagicMock()
    mock_supabase.table().select().eq().execute.return_value.data = []

    # Setup mock to raise Geometry Error
    mock_solve.side_effect = GeometryValidationError("Overlap detected")
    
    response = await generate_floor_plan("test-project", GenerateRequest(), "user-123", mock_supabase)
    
    assert response.status_code == 503
    body = json.loads(response.body.decode())
    assert body["code"] == "AI_TEMPORARILY_UNAVAILABLE"
    
    # Check that it retried 3 times (range(3))
    assert mock_solve.call_count == 3
    mock_update.assert_called_with(mock_supabase, "job-123", "Failed", error_message="Geometry Error: Overlap detected")

@pytest.mark.asyncio
@patch("app.api.routes.floor_plans.project_service.verify_ownership", return_value=False)
async def test_unauthorized_project_access(mock_verify):
    mock_supabase = MagicMock()
    with pytest.raises(HTTPException) as excinfo:
        await generate_floor_plan("test-project", GenerateRequest(), "wrong-user", mock_supabase)
    
    assert excinfo.value.status_code == 403
