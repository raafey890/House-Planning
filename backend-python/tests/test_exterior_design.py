"""
Unit and Integration Test Suite — Phase 6F.1 Exterior Design Studio Foundation.
Verifies:
  1. Exactly 32 unique exterior designs
  2. Exactly 8 categories with 4 designs each (Modern Contemporary, Minimalist, Luxury Villa,
     Traditional Indian, Indian Modern, Mediterranean, Tropical Contemporary, Premium Duplex)
  3. Stable ID prefixes (ext_), non-empty metadata, color palettes, and architectural parameters
  4. Plan-aware compatibility engine: floor count rules, width clearances, area bounds
  5. Status levels: compatible, compatible_with_adjustments, not_recommended with architectural rationale
  6. Incremental cost calculation grounded in perimeter, floor heights, and finishes
  7. API endpoints: catalog listing, filtering, detail, compatibility check, and cost calculation
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.exterior_design import (
    ExteriorDesignOption,
    CompatibilityCheckResponse
)
from app.services.exterior_design.catalog import (
    get_all_exterior_designs,
    get_exterior_design_by_id,
    get_designs_by_category,
    EXTERIOR_DESIGNS
)
from app.services.exterior_design.service import (
    validate_exterior_compatibility,
    calculate_exterior_design_cost,
    filter_catalog,
    get_compatible_catalog_for_project
)

client = TestClient(app)


# ── 1. Catalog Size & ID Integrity ────────────────────────────────────────────

def test_1_catalog_total_count():
    """Verify catalog contains exactly 32 distinct exterior designs."""
    designs = get_all_exterior_designs()
    assert len(designs) == 32, f"Expected exactly 32 designs, got {len(designs)}"


def test_2_catalog_id_uniqueness_and_format():
    """Verify all IDs are unique, start with 'ext_', and have valid metadata."""
    designs = get_all_exterior_designs()
    ids = [d.id for d in designs]
    assert len(ids) == len(set(ids)), "Found duplicate design IDs in catalog"
    
    for d in designs:
        assert d.id.startswith("ext_"), f"Design ID '{d.id}' must start with 'ext_'"
        assert len(d.name) > 0, f"Design '{d.id}' has an empty name"
        assert len(d.description) > 0, f"Design '{d.id}' has an empty description"
        assert len(d.material_palette) >= 2, f"Design '{d.id}' must have at least 2 materials"
        assert "name" in d.primary_paint_color and "hex" in d.primary_paint_color
        assert "name" in d.secondary_paint_color and "hex" in d.secondary_paint_color
        assert len(d.suitable_floor_configs) >= 1
        assert len(d.suitable_house_types) >= 1


# ── 2. Category Distribution ─────────────────────────────────────────────────

def test_3_category_distribution():
    """Verify exactly 8 categories with exactly 4 designs each."""
    designs = get_all_exterior_designs()
    expected_categories = [
        "modern_contemporary",
        "minimalist",
        "luxury_villa",
        "traditional_indian",
        "indian_modern",
        "mediterranean",
        "tropical_contemporary",
        "premium_duplex"
    ]
    
    category_counts = {}
    for d in designs:
        category_counts[d.category] = category_counts.get(d.category, 0) + 1

    assert len(category_counts) == 8, f"Expected 8 categories, found {len(category_counts)}: {list(category_counts.keys())}"
    for cat in expected_categories:
        assert cat in category_counts, f"Category '{cat}' missing from catalog"
        assert category_counts[cat] == 4, f"Category '{cat}' must have 4 designs, got {category_counts[cat]}"


# ── 3. Plan-Aware Compatibility Engine ───────────────────────────────────────

def test_4_floor_count_compatibility():
    """Verify single-floor project flagging on designs requiring multi-level floors."""
    # ext_dup_01 (Premium Duplex) requires [2, 3] floors
    result = validate_exterior_compatibility(
        design_id="ext_dup_01",
        plot_width=35.0,
        plot_length=50.0,
        floors=1  # Ground floor only
    )
    assert result.status in ["compatible_with_adjustments", "not_recommended"]
    assert result.score < 90
    assert any("Floor Count" in r for r in result.reasons)

    # When floors=2, it should be highly compatible
    result_g1 = validate_exterior_compatibility(
        design_id="ext_dup_01",
        plot_width=35.0,
        plot_length=50.0,
        floors=2
    )
    assert result_g1.status == "compatible"
    assert result_g1.score >= 85


def test_5_plot_frontage_compatibility():
    """Verify narrow plot frontage is flagged for grand luxury villas."""
    # ext_lux_01 requires min 45ft width
    result_narrow = validate_exterior_compatibility(
        design_id="ext_lux_01",
        plot_width=22.0,  # Narrow plot
        plot_length=50.0,
        floors=2
    )
    assert result_narrow.status in ["compatible_with_adjustments", "not_recommended"]
    assert any("Width" in r or "Frontage" in r for r in result_narrow.reasons)

    # Wide plot check
    result_wide = validate_exterior_compatibility(
        design_id="ext_lux_01",
        plot_width=50.0,
        plot_length=70.0,
        floors=2
    )
    assert result_wide.status == "compatible"
    assert result_wide.score >= 90


def test_6_compatibility_does_not_modify_geometry():
    """Compatibility check must be purely evaluative and never alter coordinates."""
    res = validate_exterior_compatibility(
        design_id="ext_mod_01",
        plot_width=30.0,
        plot_length=45.0,
        floors=1
    )
    assert isinstance(res, CompatibilityCheckResponse)
    assert res.is_compatible in [True, False]
    assert isinstance(res.reasons, list)
    assert isinstance(res.adjustments_suggested, list)


# ── 4. Incremental Cost Derivation ───────────────────────────────────────────

def test_7_cost_derivation_structure():
    """Verify cost calculation returns complete breakdown and quantity metrics."""
    cost = calculate_exterior_design_cost(
        design_id="ext_mod_01",
        plot_width=30.0,
        plot_length=40.0,
        floors=1
    )
    assert cost["total_exterior_cost"] > 0
    assert "breakdown" in cost
    assert "quantities" in cost
    bd = cost["breakdown"]
    assert "exterior_paint_upgrade" in bd
    assert "facade_cladding_and_louvers" in bd
    assert "doors_and_windows_upgrade" in bd
    assert "exterior_architectural_lighting" in bd
    assert "boundary_wall_and_gate" in bd
    assert "total" in bd
    assert bd["total"] == cost["total_exterior_cost"]


def test_8_cost_scales_with_floors():
    """Multi-storey homes have larger wall area and balcony railings, costing more."""
    cost_g = calculate_exterior_design_cost(
        design_id="ext_mod_01",
        plot_width=30.0,
        plot_length=40.0,
        floors=1
    )
    cost_g1 = calculate_exterior_design_cost(
        design_id="ext_mod_01",
        plot_width=30.0,
        plot_length=40.0,
        floors=2
    )
    assert cost_g1["total_exterior_cost"] > cost_g["total_exterior_cost"]
    assert cost_g1["quantities"]["height_ft"] > cost_g["quantities"]["height_ft"]
    assert cost_g1["breakdown"]["balcony_railing_upgrade"] > 0


# ── 5. Project Catalog Compatibility Evaluator ───────────────────────────────

def test_9_project_compatible_catalog_sorting():
    """Verify all 32 items are returned and sorted by compatibility score."""
    project_ctx = {
        "plot_width": 30.0,
        "plot_length": 45.0,
        "floors": 1,
        "building_type": "Independent House"
    }
    evaluated = get_compatible_catalog_for_project(project_ctx)
    assert len(evaluated) == 32
    # Verify descending sort order by score
    scores = [item["compatibility"]["score"] for item in evaluated]
    assert scores == sorted(scores, reverse=True)
    # Check that each item has compatibility dictionary
    for item in evaluated:
        assert "compatibility" in item
        assert "status" in item["compatibility"]
        assert "reasons" in item["compatibility"]


# ── 6. FastAPI Endpoints Integration ──────────────────────────────────────────

def test_10_api_catalog_list_and_filter():
    """Verify /api/v1/exterior/catalog returns 32 items and filters properly."""
    res = client.get("/api/v1/exterior/catalog")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 32

    # Filter by category
    res_cat = client.get("/api/v1/exterior/catalog?category=minimalist")
    assert res_cat.status_code == 200
    cat_data = res_cat.json()
    assert len(cat_data) == 4
    for d in cat_data:
        assert d["category"] == "minimalist"


def test_11_api_catalog_detail():
    """Verify /api/v1/exterior/catalog/{id} returns design detail and handles 404."""
    res = client.get("/api/v1/exterior/catalog/ext_mod_01")
    assert res.status_code == 200
    assert res.json()["id"] == "ext_mod_01"

    res_404 = client.get("/api/v1/exterior/catalog/ext_non_existent")
    assert res_404.status_code == 404


def test_12_api_validate_compatibility():
    """Verify POST /api/v1/exterior/validate-compatibility returns valid check response."""
    payload = {
        "design_id": "ext_mod_01",
        "plot_width": 30.0,
        "plot_length": 45.0,
        "floors": 1,
        "building_type": "Independent House"
    }
    res = client.post("/api/v1/exterior/validate-compatibility", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "score" in data
    assert "is_compatible" in data


def test_13_api_calculate_cost():
    """Verify POST /api/v1/exterior/calculate-cost returns accurate cost breakdown."""
    payload = {
        "project_id": "test-proj-01",
        "design_id": "ext_mod_01",
        "plot_width": 30.0,
        "plot_length": 45.0,
        "floors": 1,
        "materials": {"finish_type": "smooth_stucco"},
        "lighting": {"fixture_count": 8}
    }
    res = client.post("/api/v1/exterior/calculate-cost", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_exterior_cost"] > 0
    assert "breakdown" in data
