"""
Unit & Integration Tests — Phase 6F.2 Personalized Exterior Visualization.
Verifies:
  1. Canonical exterior configuration model validation (valid inputs, invalid hex codes, invalid IDs)
  2. Multi-angle vector elevation SVG generation (Front, Front-Left Perspective, Front-Right Perspective)
  3. Day vs Night lighting appearance (sunlight drop shadows vs 2700K window glow, LED grazers, moon/stars)
  4. Floor count scaling (G+0, G+1, G+2) and datum level markers
  5. Exact custom paint color and cladding pattern embedding
  6. Geometry-grounded architectural prompt generation
  7. Honest provider abstraction and error reporting (API key missing / 429 quota exhaustion)
  8. API endpoints (/generate-preview, /generate-image, /validate-config)
"""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.main import app
from app.models.exterior_design import (
    CanonicalExteriorConfig,
    ExteriorVisualizationRequest,
    ExteriorVisualizationResponse
)
from app.services.exterior_design.preview_service import (
    generate_plan_aware_exterior_svg,
    generate_personalized_exterior_preview
)
from app.services.exterior_design.image_generator_service import (
    build_exterior_geometry_prompt,
    generate_personalized_exterior_image
)

client = TestClient(app)


# ── 1. Canonical Exterior Configuration Model Tests ──────────────────────────

def test_canonical_config_valid():
    """Verify valid canonical exterior configuration passes validation."""
    config = CanonicalExteriorConfig(
        project_id="proj_101",
        plot_width=35.0,
        plot_length=45.0,
        plot_facing="North",
        floors=2,
        design_id="ext_mod_01",
        design_name="Minimalist Cuboid Villa",
        colors={
            "primary_wall": "#F4F4F0",
            "accent_wall": "#2B313B",
            "boundary_wall": "#2B313B",
            "door": "#8B5A2B"
        },
        materials={
            "finish_type": "sand_texture_plaster",
            "cladding_type": "wooden_slats"
        }
    )
    assert config.project_id == "proj_101"
    assert config.floors == 2
    assert config.design_id == "ext_mod_01"
    assert config.colors["primary_wall"] == "#F4F4F0"


def test_canonical_config_invalid_design_id():
    """Verify design_id must start with ext_."""
    with pytest.raises(ValidationError):
        CanonicalExteriorConfig(
            project_id="proj_101",
            design_id="invalid_design_id"
        )


def test_canonical_config_invalid_hex_color():
    """Verify invalid hex color raises ValidationError."""
    with pytest.raises(ValidationError):
        CanonicalExteriorConfig(
            project_id="proj_101",
            design_id="ext_mod_01",
            colors={"primary_wall": "not_a_hex_color"}
        )


def test_visualization_request_view_angle_validation():
    """Verify invalid view_angle is rejected."""
    with pytest.raises(ValidationError):
        ExteriorVisualizationRequest(
            project_id="proj_101",
            design_id="ext_mod_01",
            view_angle="invalid_angle"
        )


def test_visualization_request_lighting_mode_validation():
    """Verify invalid lighting_mode is rejected."""
    with pytest.raises(ValidationError):
        ExteriorVisualizationRequest(
            project_id="proj_101",
            design_id="ext_mod_01",
            lighting_mode="afternoon_tea"
        )


# ── 2. Vector Elevation Preview Generator Tests ─────────────────────────────

def test_generate_svg_front_elevation_daylight():
    """Verify front elevation SVG in daylight mode."""
    res = generate_plan_aware_exterior_svg(
        project_id="proj_101",
        design_id="ext_mod_01",
        plot_width=30.0,
        plot_length=40.0,
        floors=2,
        view_angle="front",
        lighting_mode="daylight"
    )
    assert res["status"] == "success"
    assert res["preview_mode"] == "svg_vector"
    assert res["view_angle"] == "front"
    assert res["lighting_mode"] == "daylight"
    svg = res["svg_content"]
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    assert "Front Elevation (Orthographic)" in svg
    assert "Daylight Sun Angle" in svg
    assert "30.0 ft Plot Frontage" in svg
    assert "±0.00m Ground" in svg
    assert "+0.45m Plinth" in svg
    assert "daylightGlass" in svg


def test_generate_svg_front_left_perspective():
    """Verify front-left perspective SVG generates 3D massing and depth."""
    res = generate_plan_aware_exterior_svg(
        project_id="proj_101",
        design_id="ext_lux_01",
        plot_width=40.0,
        plot_length=50.0,
        floors=2,
        view_angle="front_left",
        lighting_mode="daylight"
    )
    assert res["status"] == "success"
    assert res["view_angle"] == "front_left"
    svg = res["svg_content"]
    assert "Front-Left 3/4 Isometric Perspective" in svg
    assert "polygon points=" in svg  # 3D isometric facets


def test_generate_svg_front_right_perspective():
    """Verify front-right perspective SVG generates 3D massing and depth."""
    res = generate_plan_aware_exterior_svg(
        project_id="proj_101",
        design_id="ext_mod_02",
        plot_width=30.0,
        plot_length=40.0,
        floors=1,
        view_angle="front_right",
        lighting_mode="daylight"
    )
    assert res["status"] == "success"
    assert res["view_angle"] == "front_right"
    svg = res["svg_content"]
    assert "Front-Right 3/4 Isometric Perspective" in svg
    assert "polygon points=" in svg


def test_generate_svg_night_lighting_appearance():
    """Verify night mode includes twilight sky, warm window glow, moon/stars, and architectural LED grazers."""
    res = generate_plan_aware_exterior_svg(
        project_id="proj_101",
        design_id="ext_mod_01",
        plot_width=30.0,
        floors=2,
        view_angle="front",
        lighting_mode="night"
    )
    assert res["status"] == "success"
    assert res["lighting_mode"] == "night"
    svg = res["svg_content"]
    assert "Night Architectural Illumination" in svg
    assert "warmWindowGlow" in svg
    assert "grazerGlowUp" in svg
    assert "grazerGlowDown" in svg
    assert "moonGlow" in svg


def test_generate_svg_custom_colors_and_materials_embedded():
    """Verify exact custom colors and cladding patterns are reflected in the SVG."""
    custom_c = {
        "primary_wall": "#E11D48",
        "accent_wall": "#10B981",
        "boundary_wall": "#1E293B",
        "door": "#7C2D12",
        "window_frame": "#0F172A",
        "railing": "#3B82F6"
    }
    custom_m = {
        "cladding_type": "stone_veneer"
    }
    res = generate_plan_aware_exterior_svg(
        project_id="proj_101",
        design_id="ext_mod_01",
        custom_colors=custom_c,
        custom_materials=custom_m
    )
    svg = res["svg_content"]
    assert "#E11D48" in svg
    assert "#10B981" in svg
    assert "#7C2D12" in svg


def test_generate_svg_floor_count_scaling():
    """Verify floor count scales datum markers from G to G+2."""
    res_g0 = generate_plan_aware_exterior_svg(project_id="p1", design_id="ext_mod_01", floors=1)
    res_g2 = generate_plan_aware_exterior_svg(project_id="p2", design_id="ext_mod_01", floors=3)

    svg_g0 = res_g0["svg_content"]
    svg_g2 = res_g2["svg_content"]

    assert "Floor 1" not in svg_g0
    assert "Floor 1" in svg_g2
    assert "Floor 2" in svg_g2
    assert "G+2 Levels" in svg_g2
    assert "Parapet" in svg_g2


# ── 3. Exterior Image Generator & Prompt Construction ────────────────────────

def test_build_exterior_geometry_prompt():
    """Verify architectural prompt embeds plot frontage, floor levels, perspective, and finishes."""
    req = ExteriorVisualizationRequest(
        project_id="proj_test",
        design_id="ext_mod_01",
        plot_width=32.0,
        plot_length=48.0,
        floors=2,
        view_angle="front_left",
        lighting_mode="night",
        colors={
            "primary_wall": "#F8FAFC",
            "accent_wall": "#334155"
        },
        materials={
            "cladding_type": "wooden_slats"
        }
    )
    prompt = build_exterior_geometry_prompt(req)
    assert "32.0 ft wide frontage" in prompt
    assert "48.0 ft depth" in prompt
    assert "G+1 (2 levels)" in prompt
    assert "Front-left three-quarter (3/4) architectural perspective" in prompt
    assert "Dusk/twilight blue hour architectural photography" in prompt
    assert "#F8FAFC" in prompt
    assert "#334155" in prompt
    assert "wooden slats" in prompt


def test_image_generator_honest_provider_diagnostics():
    """Verify image generator reports honest diagnostics when API key is missing or quota is exhausted."""
    req = ExteriorVisualizationRequest(
        project_id="proj_test",
        design_id="ext_mod_01",
        plot_width=30.0,
        floors=1
    )
    res = generate_personalized_exterior_image(req)
    assert res.preview_mode == "ai_generated"
    # Should be either success (if cached/valid key) or provider_error with transparent diagnostic message
    if res.status == "provider_error":
        assert res.error_detail is not None
        assert "GEMINI" in res.error_detail or "429" in res.error_detail or "Google" in res.provider


# ── 4. API Endpoints Integration Tests ────────────────────────────────────────

def test_api_validate_canonical_config_endpoint():
    """Verify /api/v1/exterior/validate-config endpoint."""
    payload = {
        "project_id": "proj_api_1",
        "design_id": "ext_mod_01",
        "plot_width": 30.0,
        "plot_length": 40.0,
        "floors": 2,
        "colors": {
            "primary_wall": "#F4F4F0",
            "accent_wall": "#2B313B"
        }
    }
    resp = client.post("/api/v1/exterior/validate-config", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "valid"
    assert data["design_id"] == "ext_mod_01"


def test_api_generate_preview_endpoint():
    """Verify /api/v1/exterior/generate-preview returns SVG and dimensions metadata."""
    payload = {
        "project_id": "proj_api_1",
        "design_id": "ext_mod_01",
        "plot_width": 30.0,
        "plot_length": 40.0,
        "floors": 2,
        "view_angle": "front",
        "lighting_mode": "daylight"
    }
    resp = client.post("/api/v1/exterior/generate-preview", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["preview_mode"] == "svg_vector"
    assert "<svg" in data["svg_content"]
    assert data["dimensions"]["plot_width_ft"] == 30.0


def test_api_generate_preview_not_found():
    """Verify 404 is returned for non-existent design ID."""
    payload = {
        "project_id": "proj_api_1",
        "design_id": "ext_non_existent",
        "plot_width": 30.0
    }
    resp = client.post("/api/v1/exterior/generate-preview", json=payload)
    assert resp.status_code == 404


def test_api_generate_image_endpoint():
    """Verify /api/v1/exterior/generate-image endpoint returns response structure."""
    payload = {
        "project_id": "proj_api_1",
        "design_id": "ext_mod_01",
        "plot_width": 30.0,
        "floors": 1
    }
    resp = client.post("/api/v1/exterior/generate-image", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert data["preview_mode"] == "ai_generated"
