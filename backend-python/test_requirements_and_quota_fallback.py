"""
Unit and integration tests for:
1. PlanningRequirements validation and fingerprinting (Phase 6M.1)
2. Saved-plan matching fallback
3. Gemini quota exhaustion fast-fail (GeminiQuotaExhaustedError)
4. Deterministic solver fallback execution and post-processor assembly
"""
import pytest
from unittest.mock import patch, MagicMock
from app.validators.requirements_validator import (
    validate_requirements,
    requirements_fingerprint,
    fingerprints_match,
    PlanningRequirements
)
from app.services.planning.gemini_planner import (
    GeminiQuotaExhaustedError,
    GeminiPlannerError,
    plan_with_gemini
)
from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout
from app.services.floorplan_service import FloorplanService
from app.models.layout import LayoutData


# ── 1. Requirements Validation Tests ──────────────────────────────────────────

def test_validate_requirements_valid_g1():
    context = {
        "plot_width": 50,
        "plot_length": 80,
        "facing": "south",
        "floors": 2,
        "bedrooms": 3,
        "bathrooms": 3,
        "kitchens": 1,
        "living_rooms": 1,
        "balconies": 1,
        "parking": 1,
    }
    req = validate_requirements(context)
    assert req.plot_width == 50
    assert req.plot_length == 80
    assert req.facing == "south"
    assert req.floors == 2
    assert req.bedrooms == 3


def test_validate_requirements_invalid_dimensions():
    with pytest.raises(Exception):
        validate_requirements({
            "plot_width": -10,
            "plot_length": 50,
            "facing": "north",
            "floors": 1
        })


def test_validate_requirements_invalid_facing():
    with pytest.raises(Exception):
        validate_requirements({
            "plot_width": 30,
            "plot_length": 50,
            "facing": "north-west-invalid",
            "floors": 1
        })


def test_validate_requirements_invalid_floors():
    with pytest.raises(Exception):
        validate_requirements({
            "plot_width": 30,
            "plot_length": 50,
            "facing": "east",
            "floors": 0
        })


# ── 2. Requirements Fingerprint Tests ─────────────────────────────────────────

def test_requirements_fingerprint_matching():
    context1 = {
        "plot_width": 40,
        "plot_length": 60,
        "facing": "north",
        "floors": 2,
        "bedrooms": 3,
        "bathrooms": 2,
        "kitchens": 1,
        "living_rooms": 1,
        "balconies": 1,
        "parking": 1,
    }
    context2 = dict(context1)

    req1 = validate_requirements(context1)
    req2 = validate_requirements(context2)

    fp1 = requirements_fingerprint(req1)
    fp2 = requirements_fingerprint(req2)

    assert fingerprints_match(fp1, fp2) is True


def test_requirements_fingerprint_mismatch():
    context1 = {
        "plot_width": 50,
        "plot_length": 80,
        "facing": "south",
        "floors": 2,
        "bedrooms": 3,
    }
    context2 = {
        "plot_width": 50,
        "plot_length": 80,
        "facing": "south",
        "floors": 2,
        "bedrooms": 1,  # Different bedroom count
    }
    req1 = validate_requirements(context1)
    req2 = validate_requirements(context2)

    fp1 = requirements_fingerprint(req1)
    fp2 = requirements_fingerprint(req2)

    assert fingerprints_match(fp1, fp2) is False


# ── 3. Saved-Plan Matching Fallback Tests ─────────────────────────────────────

@pytest.mark.asyncio
async def test_saved_plan_matching_success():
    mock_supabase = MagicMock()
    mock_execute = MagicMock()
    matching_fp = {
        "plot_width": 30, "plot_length": 40, "facing": "east",
        "floors": 1, "bedrooms": 2, "bathrooms": 1, "kitchens": 1,
        "living_rooms": 1, "balconies": 0, "parking": 1
    }
    mock_execute.data = [{
        "id": "saved-plan-123",
        "layout_data": {"floors": []},
        "created_at": "2026-10-20T12:00:00Z",
        "version_name": "AI Generated Option 1",
        "requirements_fingerprint": matching_fp
    }]
    mock_supabase.table().select().eq().order().limit().execute.return_value = mock_execute

    plan = await FloorplanService.get_latest_successful(
        mock_supabase, "proj-1", current_fingerprint=matching_fp
    )
    assert plan is not None
    assert plan["id"] == "saved-plan-123"


@pytest.mark.asyncio
async def test_saved_plan_mismatch_rejected():
    mock_supabase = MagicMock()
    mock_execute = MagicMock()
    saved_fp = {
        "plot_width": 30, "plot_length": 40, "facing": "east",
        "floors": 1, "bedrooms": 3, "bathrooms": 2, "kitchens": 1,
        "living_rooms": 1, "balconies": 0, "parking": 1
    }
    current_fp = dict(saved_fp)
    current_fp["bedrooms"] = 1  # User now wants 1 bedroom instead of 3

    mock_execute.data = [{
        "id": "saved-plan-old",
        "layout_data": {"floors": []},
        "created_at": "2026-10-20T12:00:00Z",
        "version_name": "AI Generated Option 1",
        "requirements_fingerprint": saved_fp
    }]
    mock_supabase.table().select().eq().order().limit().execute.return_value = mock_execute

    # Should reject mismatch and return None
    plan = await FloorplanService.get_latest_successful(
        mock_supabase, "proj-1", current_fingerprint=current_fp
    )
    assert plan is None


# ── 4. Gemini Quota Fast-Fail Test ───────────────────────────────────────────

def test_gemini_quota_exhausted_raises_immediately():
    mock_provider = MagicMock()
    # Simulate a 429 quota error from Google GenAI SDK
    mock_provider.client.models.generate_content.side_effect = Exception(
        "429 Resource exhausted: Quota exceeded for quota metric 'GenerateContent requests'"
    )

    with patch('app.services.ai.gemini_provider.GeminiProvider', return_value=mock_provider):
        context = {
            "plot_width": 30,
            "plot_length": 40,
            "facing": "south",
            "floors": 1,
            "bedrooms": 2,
            "bathrooms": 1,
            "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}
        }
        with pytest.raises(GeminiQuotaExhaustedError):
            plan_with_gemini(context, [])


# ── 5. Hybrid Engine Fallback & Deterministic Solver Test ─────────────────────

def test_engine_deterministic_fallback_when_gemini_quota_exhausted():
    context = {
        "plot_width": 40,
        "plot_length": 60,
        "facing": "south",
        "floors": 1,
        "bedrooms": 2,
        "bathrooms": 1,
        "kitchens": 1,
        "living_rooms": 1,
        "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}
    }
    requirements = [
        {"room_type": "living_room", "count": 1},
        {"room_type": "kitchen", "count": 1},
        {"room_type": "bedroom", "count": 2},
        {"room_type": "bathroom", "count": 1},
    ]

    # Mock plan_with_gemini to raise GeminiQuotaExhaustedError
    with patch(
        'app.services.planning.gemini_planner.plan_with_gemini',
        side_effect=GeminiQuotaExhaustedError("429 Quota exhausted")
    ):
        result = solve_layout(context, requirements, use_gemini=True)
        assert result is not None
        assert result["planner_source"] == "deterministic_fallback"
        assert result["ai_fallback_reason"] == "gemini_quota_exhausted"
        assert len(result["floors"]) >= 1

        # Now test that post_processor produces a valid LayoutData
        layout_data = post_process_layout(result)
        assert layout_data is not None
        assert len(layout_data.floors) == 1
        assert len(layout_data.floors[0].rooms) >= 4


# ── 6. Persistence & Legacy Database Tests ────────────────────────────────────

@pytest.mark.asyncio
async def test_saved_plan_persistence_includes_fingerprint():
    mock_supabase = MagicMock()
    mock_execute = MagicMock()
    mock_execute.data = [{"id": "new-plan-uuid"}]
    mock_supabase.table().insert().execute.return_value = mock_execute

    sample_layout = LayoutData(
        plot={
            "width": 30.0, "length": 40.0, "facing": "north",
            "buildable_boundary": {"width": 24.0, "length": 32.0},
            "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}
        },
        floors=[{
            "level": 0, "name": "Ground Floor",
            "rooms": [{"id": "r1", "type": "living_room", "label": "Living", "x": 3, "y": 4, "width": 12, "length": 15, "area": 180}],
            "walls": [], "doors": [], "windows": []
        }]
    )

    test_fp = {
        "plot_width": 30.0, "plot_length": 40.0, "facing": "north",
        "floors": 1, "bedrooms": 1, "bathrooms": 1, "kitchens": 1,
        "living_rooms": 1, "balconies": 0, "parking": 0
    }

    plan_id = await FloorplanService.save_floor_plan(
        mock_supabase, "proj-1", "user-1", "job-1", sample_layout,
        requirements_fingerprint=test_fp
    )

    assert plan_id == "new-plan-uuid"
    # Verify the insert payload contained requirements_fingerprint
    insert_call_args = mock_supabase.table().insert.call_args[0][0]
    assert "requirements_fingerprint" in insert_call_args
    assert insert_call_args["requirements_fingerprint"] == test_fp


@pytest.mark.asyncio
async def test_saved_plan_legacy_compatible_allowed():
    mock_supabase = MagicMock()
    mock_execute = MagicMock()
    # Legacy plan: requirements_fingerprint is None, but layout_data matches 30x40 1-floor
    mock_execute.data = [{
        "id": "legacy-plan-compatible",
        "layout_data": {
            "plot": {"width": 30.0, "length": 40.0},
            "floors": [{"level": 0, "rooms": []}]
        },
        "created_at": "2026-10-15T12:00:00Z",
        "version_name": "Legacy V1",
        "requirements_fingerprint": None
    }]
    mock_supabase.table().select().eq().order().limit().execute.return_value = mock_execute

    current_fp = {
        "plot_width": 30.0, "plot_length": 40.0, "facing": "south", "floors": 1
    }

    plan = await FloorplanService.get_latest_successful(
        mock_supabase, "proj-1", current_fingerprint=current_fp
    )
    assert plan is not None
    assert plan["id"] == "legacy-plan-compatible"


@pytest.mark.asyncio
async def test_saved_plan_legacy_incompatible_rejected():
    mock_supabase = MagicMock()
    mock_execute = MagicMock()
    # Legacy plan: requirements_fingerprint is None, but layout_data was for 50x80 2-floor!
    mock_execute.data = [{
        "id": "legacy-plan-50x80",
        "layout_data": {
            "plot": {"width": 50.0, "length": 80.0},
            "floors": [{"level": 0, "rooms": []}, {"level": 1, "rooms": []}]
        },
        "created_at": "2026-10-15T12:00:00Z",
        "version_name": "Legacy 50x80",
        "requirements_fingerprint": None
    }]
    mock_supabase.table().select().eq().order().limit().execute.return_value = mock_execute

    # User currently wants a 30x40 1-floor house
    current_fp = {
        "plot_width": 30.0, "plot_length": 40.0, "facing": "north", "floors": 1
    }

    plan = await FloorplanService.get_latest_successful(
        mock_supabase, "proj-1", current_fingerprint=current_fp
    )
    # Must reject incompatible legacy plan!
    assert plan is None


@pytest.mark.asyncio
async def test_saved_plan_malformed_fingerprint_handled_safely():
    mock_supabase = MagicMock()
    mock_execute = MagicMock()
    # Corrupt string that cannot be parsed
    mock_execute.data = [{
        "id": "corrupt-plan",
        "layout_data": {"plot": {"width": 30, "length": 40}, "floors": []},
        "created_at": "2026-10-15T12:00:00Z",
        "version_name": "Corrupt",
        "requirements_fingerprint": "not-valid-json{{{"
    }]
    mock_supabase.table().select().eq().order().limit().execute.return_value = mock_execute

    current_fp = {"plot_width": 30.0, "plot_length": 40.0, "facing": "north", "floors": 1}

    plan = await FloorplanService.get_latest_successful(
        mock_supabase, "proj-1", current_fingerprint=current_fp
    )
    assert plan is None


# ── 7. Phase 6M.2 Geometry Reliability Tests ─────────────────────────────────

from app.validators.geometry_validator import GeometryValidator, GeometryValidationError

def test_geometry_validator_detects_overlapping_rooms():
    # Two bedrooms overlapping at (5, 5) with dimensions 12x12 and 12x12
    overlapping_layout = LayoutData(
        plot={
            "width": 50.0, "length": 80.0, "facing": "south",
            "buildable_boundary": {"width": 44.0, "length": 72.0},
            "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}
        },
        floors=[{
            "level": 0, "name": "Ground Floor",
            "rooms": [
                {"id": "r1", "type": "living_room", "label": "Living", "x": 5, "y": 5, "width": 15, "length": 15, "area": 225},
                {"id": "r2", "type": "bedroom", "label": "Bedroom 1", "x": 10, "y": 10, "width": 12, "length": 12, "area": 144},
            ],
            "walls": [], "doors": [{"id": "d1", "type": "main_entrance", "position": {"x": 10, "y": 5}, "width": 3.5}], "windows": []
        }]
    )

    with pytest.raises(GeometryValidationError) as exc_info:
        GeometryValidator.validate_layout(overlapping_layout)
    assert "overlaps" in str(exc_info.value)


def test_geometry_validator_detects_out_of_boundary_room():
    out_of_bounds_layout = LayoutData(
        plot={
            "width": 30.0, "length": 40.0, "facing": "south",
            "buildable_boundary": {"width": 24.0, "length": 32.0},
            "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}
        },
        floors=[{
            "level": 0, "name": "Ground Floor",
            "rooms": [
                # x=25 + width=10 = 35 > buildable_max_x (27)
                {"id": "r1", "type": "living_room", "label": "Living", "x": 25, "y": 5, "width": 10, "length": 15, "area": 150},
            ],
            "walls": [], "doors": [{"id": "d1", "type": "main_entrance", "position": {"x": 25, "y": 5}, "width": 3.5}], "windows": []
        }]
    )

    with pytest.raises(GeometryValidationError) as exc_info:
        GeometryValidator.validate_layout(out_of_bounds_layout)
    assert "outside the buildable boundary" in str(exc_info.value)


def test_geometry_validator_detects_missing_stair_on_upper_floor():
    # Multi-floor plan with stairs only on ground floor
    missing_stairs_layout = LayoutData(
        plot={
            "width": 40.0, "length": 60.0, "facing": "north",
            "buildable_boundary": {"width": 34.0, "length": 52.0},
            "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}
        },
        floors=[
            {
                "level": 0, "name": "Ground Floor",
                "rooms": [
                    {"id": "r1", "type": "living_room", "label": "Living", "x": 5, "y": 5, "width": 15, "length": 15, "area": 225},
                    {"id": "st1", "type": "staircase", "label": "Staircase", "x": 22, "y": 5, "width": 8, "length": 12, "area": 96},
                ],
                "stairs": [{"id": "st1", "x": 22, "y": 5, "width": 8, "length": 12, "direction": "up"}],
                "walls": [], "doors": [{"id": "d1", "type": "main_entrance", "position": {"x": 10, "y": 5}, "width": 3.5}], "windows": []
            },
            {
                "level": 1, "name": "First Floor",
                "rooms": [
                    # Missing staircase on floor 1!
                    {"id": "r2", "type": "bedroom", "label": "Bedroom 1", "x": 5, "y": 5, "width": 15, "length": 15, "area": 225},
                ],
                "stairs": [],
                "walls": [], "doors": [], "windows": []
            }
        ]
    )

    with pytest.raises(GeometryValidationError) as exc_info:
        GeometryValidator.validate_layout(missing_stairs_layout)
    assert "missing a staircase connection" in str(exc_info.value)


def test_geometry_validator_detects_non_sequential_floors():
    non_seq_layout = LayoutData(
        plot={
            "width": 30.0, "length": 40.0, "facing": "south",
            "buildable_boundary": {"width": 24.0, "length": 32.0},
            "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3}
        },
        floors=[
            {
                "level": 0, "name": "Ground Floor",
                "rooms": [{"id": "r1", "type": "living_room", "label": "Living", "x": 5, "y": 5, "width": 12, "length": 15, "area": 180}],
                "walls": [], "doors": [{"id": "d1", "type": "main_entrance", "position": {"x": 10, "y": 5}, "width": 3.5}], "windows": []
            },
            {
                "level": 3, "name": "Third Floor",  # Non-sequential: jumps from 0 to 3
                "rooms": [{"id": "r2", "type": "bedroom", "label": "Bedroom", "x": 5, "y": 5, "width": 12, "length": 15, "area": 180}],
                "walls": [], "doors": [], "windows": []
            }
        ]
    )

    with pytest.raises(GeometryValidationError) as exc_info:
        GeometryValidator.validate_layout(non_seq_layout)
    assert "contiguous starting from 0" in str(exc_info.value)

