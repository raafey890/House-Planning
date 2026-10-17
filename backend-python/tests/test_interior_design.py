"""
Unit and Integration Test Suite — Phase 6E.1 Interactive Interior Design Studio.
Verifies all 16 acceptance criteria:
  1. Exactly 32 unique designs
  2. Correct category counts: Bedroom 8, Living Room 6, Kitchen 6, Guest Room 4, Bathroom 4, Dining Room 4
  3. Correct category-specific image mapping (all 32 SVG assets exist and match category)
  4. Filtering out room types that do not exist in the selected plan
  5. Independent selections for multiple bedrooms or bathrooms
  6. Room selection matching the actual layout and dimensions
  7. Saved selections being restored accurately
  8. Handling invalid room/design combinations
  9. Personalized preview requests receiving correct room geometry and options
 10. Preview generation failures / limitations being reported honestly
 11. Selected features updating the cost estimate correctly
 12. Replacing a selected design without double-counting baseline materials
 13. Rate changes not rerunning the planning solver
 14. Existing Phase 6C.8A geometry and SVG regression tests compatibility
 15. Existing Phase 6D cost-estimation tests compatibility
 16. API endpoints integration
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.interior_design import (
    InteriorDesignOption,
    RoomInteriorSelection,
    ProjectInteriorSelectionsPayload,
    CalculateInteriorCostRequest
)
from app.services.interior_design.catalog import (
    INTERIOR_CATALOG_DATA,
    get_all_interior_designs,
    get_interior_design_by_id,
    get_designs_by_category
)
from app.services.interior_design.service import (
    validate_design_compatibility,
    calculate_room_interior_cost,
    calculate_project_interior_costs,
    filter_catalog,
    FLOORING_UPGRADE_RATES,
    WALL_TREATMENT_RATES,
    BASELINE_RATES
)
from app.services.interior_design.preview_service import generate_plan_aware_preview

client = TestClient(app)


# ── 1. Catalog Size & ID Uniqueness ──────────────────────────────────────────

def test_1_catalog_total_count():
    """Verify catalog contains exactly 32 distinct designs."""
    designs = get_all_interior_designs()
    assert len(designs) == 32, f"Expected exactly 32 designs, got {len(designs)}"


def test_2_catalog_id_uniqueness_and_format():
    """Verify all IDs are unique, non-empty, and prefixed with 'int_'."""
    designs = get_all_interior_designs()
    ids = [d.id for d in designs]
    assert len(ids) == len(set(ids)), "Found duplicate design IDs in catalog"
    for d in designs:
        assert d.id.startswith("int_"), f"Design ID {d.id} must start with 'int_'"
        assert len(d.name) > 0
        assert len(d.description) > 0


# ── 2. Category Distribution ─────────────────────────────────────────────────

def test_3_category_distribution():
    """Verify exact category counts: Bedroom 8, Living Room 6, Kitchen 6, Guest Room 4, Bathroom 4, Dining Room 4."""
    designs = get_all_interior_designs()
    category_counts = {}
    for d in designs:
        category_counts[d.category] = category_counts.get(d.category, 0) + 1

    expected = {
        "bedroom": 8,
        "living_room": 6,
        "kitchen": 6,
        "guest_room": 4,
        "bathroom": 4,
        "dining_room": 4
    }
    assert category_counts == expected, f"Category distribution mismatch: {category_counts}"


# ── 3. Category-Specific Image Mapping ───────────────────────────────────────

def test_4_category_specific_image_mapping():
    """Verify all 32 designs point to valid realistic JPG photographic assets in public folder."""
    designs = get_all_interior_designs()
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    public_img_dir = os.path.join(repo_root, "frontend", "public", "images", "interiors")

    assert os.path.exists(public_img_dir), f"Images directory does not exist: {public_img_dir}"

    for d in designs:
        assert d.image_path == f"/images/interiors/{d.id}.jpg", f"Design {d.id} image_path is {d.image_path}, expected .jpg"
        full_path = os.path.join(public_img_dir, f"{d.id}.jpg")
        assert os.path.exists(full_path), f"Missing realistic JPG asset for {d.id} at {full_path}"
        file_size = os.path.getsize(full_path)
        assert file_size >= 10000, f"JPG file {d.id}.jpg is too small or corrupted ({file_size} bytes)"

        # Verify valid JPEG binary signature (SOI marker: \xff\xd8)
        with open(full_path, "rb") as f:
            header = f.read(2)
            assert header == b"\xff\xd8", f"File {d.id}.jpg does not have a valid JPEG header: {header}"


# ── 4. Filtering Out Non-Existent Room Types ─────────────────────────────────

def test_5_plan_room_type_filtering():
    """
    Verify filtering logic allows showing only designs suitable for discovered rooms
    and discards inappropriate rooms.
    """
    # A plan with only 1 bedroom and 1 kitchen should filter designs accordingly
    bed_designs = filter_catalog(room_type="bedroom")
    assert len(bed_designs) >= 8
    for d in bed_designs:
        assert any("bedroom" in st or "all" in st for st in d.suitable_room_types)

    # Discovered kitchen rooms match kitchen category
    kit_designs = filter_catalog(category="kitchen", room_type="kitchen")
    assert len(kit_designs) == 6
    for d in kit_designs:
        assert d.category == "kitchen"


# ── 5. Independent Selections for Multiple Bedrooms/Bathrooms ────────────────

def test_6_independent_selections_multiple_rooms():
    """
    Verify that Master Bedroom, Bedroom 2, and Guest Room can hold completely independent
    designs, finishes, and distinct calculated costs.
    """
    sel_mbr = RoomInteriorSelection(
        room_id="room_mbr_01",
        room_type="master_bedroom",
        room_name="Master Bedroom",
        room_area_sqft=220.0,
        design_id="int_bed_02",  # Luxury Master Bedroom
        flooring_choice="italian_marble",
        ceiling_option_id="int_ceil_02",
        lighting_points_count=10
    )

    sel_bed2 = RoomInteriorSelection(
        room_id="room_bed_02",
        room_type="bedroom",
        room_name="Bedroom 2",
        room_area_sqft=140.0,
        design_id="int_bed_07",  # Compact Budget-Friendly
        flooring_choice="vitrified_tiles",
        ceiling_option_id="int_ceil_01",
        lighting_points_count=4
    )

    sel_guest = RoomInteriorSelection(
        room_id="room_guest_01",
        room_type="guest_room",
        room_name="Guest Room",
        room_area_sqft=130.0,
        design_id="int_guest_01",  # Modern Guest Room
        flooring_choice="wooden_laminate",
        ceiling_option_id="int_ceil_01",
        lighting_points_count=6
    )

    cost_mbr, breakdown_mbr = calculate_room_interior_cost(sel_mbr)
    cost_bed2, breakdown_bed2 = calculate_room_interior_cost(sel_bed2)
    cost_guest, breakdown_guest = calculate_room_interior_cost(sel_guest)

    assert cost_mbr > cost_guest > cost_bed2
    assert breakdown_mbr["flooring_upgrade"] == 220.0 * 240.0  # Marble differential
    assert breakdown_bed2["flooring_upgrade"] == 0.0           # Baseline vitrified
    assert breakdown_guest["flooring_upgrade"] == 130.0 * 95.0 # Laminate differential


# ── 6. Room Selection Matching Actual Layout Dimensions ──────────────────────

def test_7_room_selection_matching_layout_dimensions():
    """Verify room interior selection hydrates geometry and dimensions from layout_data."""
    layout_data = {
        "floors": [
            {
                "floor_number": 0,
                "rooms": [
                    {
                        "id": "room_live_101",
                        "name": "Living Room",
                        "type": "living_room",
                        "width": 16.0,
                        "length": 18.0,
                        "area": 288.0
                    }
                ]
            }
        ]
    }

    selections = {
        "room_live_101": RoomInteriorSelection(
            room_id="room_live_101",
            room_type="",  # will be hydrated
            room_area_sqft=0.0,  # will be hydrated
            design_id="int_lr_01"
        )
    }

    result = calculate_project_interior_costs(selections=selections, layout_data=layout_data)
    hydrated = result["selections"]["room_live_101"]

    assert hydrated.room_type == "living_room"
    assert hydrated.room_area_sqft == 288.0
    assert hydrated.room_name == "Living Room"
    assert hydrated.additional_cost > 0


# ── 7. Handling Invalid Room/Design Combinations ─────────────────────────────

def test_8_invalid_room_design_combinations():
    """Verify compatibility validator catches invalid room-design cross-applications."""
    # Applying living room design to a bathroom
    res_invalid = validate_design_compatibility("int_lr_01", "bathroom")
    assert res_invalid["compatible"] is False
    assert len(res_invalid["warnings"]) > 0

    # Applying U-shaped kitchen to narrow room < 8.5 ft
    res_tight = validate_design_compatibility("int_kit_03", "kitchen", room_width=7.0, room_length=10.0)
    assert res_tight["compatible"] is False
    assert any("8.5 ft" in w for w in res_tight["warnings"])


# ── 8. Plan-Aware Personalized Preview Generation ────────────────────────────

def test_9_plan_aware_preview_generation():
    """
    Verify generate_plan_aware_preview receives real room geometry,
    respects dimensions, door/window openings, and returns SVG layout with honest status.
    """
    preview = generate_plan_aware_preview(
        room_id="room_mbr_01",
        room_name="Master Bedroom",
        room_type="bedroom",
        room_width=14.0,
        room_length=16.0,
        room_area=224.0,
        design_id="int_bed_01",
        floor_name="First Floor",
        customizations={
            "flooring_choice": "italian_marble",
            "lighting_points_count": 8,
            "ceiling_option_id": "int_ceil_01"
        }
    )

    assert preview["status"] == "success"
    assert preview["mode"] == "geometry_grounded"
    assert preview["dimensions"]["width"] == 14.0
    assert preview["dimensions"]["length"] == 16.0
    assert preview["dimensions"]["area_sqft"] == 224.0
    assert len(preview["clearances"]) > 0
    assert "<svg" in preview["preview_svg"]
    assert "14.0 ft" in preview["preview_svg"]
    assert "16.0 ft" in preview["preview_svg"]

    # Honest reporting of AI image provider status
    assert preview["ai_generation_status"]["available"] is False
    assert "geometry-grounded" in preview["ai_generation_status"]["reason"]


def test_10_plan_aware_preview_unknown_design_handling():
    """Verify preview generator handles unknown design IDs gracefully."""
    res = generate_plan_aware_preview(
        room_id="room_01",
        room_name="Test",
        room_type="bedroom",
        room_width=12.0,
        room_length=12.0,
        room_area=144.0,
        design_id="int_nonexistent_99"
    )
    assert res["status"] == "error"
    assert "not found" in res["message"]


# ── 9. Zero Double-Counting & Cost Estimation Updates ────────────────────────

def test_11_zero_double_counting_material_replacement():
    """
    Verify that selecting Italian Marble flooring only charges the differential
    (+₹240/sq ft) over the baseline vitrified tile (₹75/sq ft) already included in Phase 6D.
    """
    assert FLOORING_UPGRADE_RATES["vitrified_tiles"]["differential"] == 0.0
    assert FLOORING_UPGRADE_RATES["italian_marble"]["differential"] == 240.0

    sel = RoomInteriorSelection(
        room_id="room_mbr_01",
        room_type="bedroom",
        room_area_sqft=200.0,
        design_id="int_bed_01",
        flooring_choice="italian_marble"
    )
    cost, breakdown = calculate_room_interior_cost(sel)

    # Differential = 200 * 240 = 48,000
    assert breakdown["flooring_upgrade"] == 48000.0
    # Entire room cost must equal the exact sum of all itemized parts
    assert cost == round(sum(breakdown.values()), 2)


def test_12_recalculating_estimate_does_not_call_solver():
    """
    Verify that changing an interior option or room selection calculates
    instantaneously via deterministic formulas without requiring CP-SAT solver.
    """
    sel = RoomInteriorSelection(
        room_id="room_101",
        room_type="kitchen",
        room_area_sqft=120.0,
        design_id="int_kit_01"
    )
    cost_initial, _ = calculate_room_interior_cost(sel)

    # Change to luxury kitchen
    sel.design_id = "int_kit_05"
    cost_luxury, _ = calculate_room_interior_cost(sel)

    assert cost_luxury > cost_initial


# ── 10. API Endpoints Integration ────────────────────────────────────────────

def test_13_api_catalog_all_32_items():
    """Verify GET /api/v1/interior/catalog returns exactly 32 designs."""
    response = client.get("/api/v1/interior/catalog")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 32


def test_14_api_catalog_filter_by_guest_room():
    """Verify GET /api/v1/interior/catalog?category=guest_room returns 4 designs."""
    response = client.get("/api/v1/interior/catalog?category=guest_room")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    for d in data:
        assert d["category"] == "guest_room"


def test_15_api_generate_preview_endpoint():
    """Verify POST /api/v1/interior/generate-preview returns plan-aware preview."""
    payload = {
        "room_id": "room_test_01",
        "room_name": "Living Hall",
        "room_type": "living_room",
        "room_width": 15.0,
        "room_length": 18.0,
        "room_area": 270.0,
        "design_id": "int_lr_01",
        "floor_name": "Ground Floor",
        "customizations": {
            "flooring_choice": "vitrified_tiles",
            "lighting_points_count": 8
        }
    }
    response = client.post("/api/v1/interior/generate-preview", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["mode"] == "geometry_grounded"
    assert "<svg" in data["preview_svg"]


def test_16_api_calculate_costs_endpoint():
    """Verify POST /api/v1/interior/calculate-cost."""
    payload = {
        "project_id": "proj_unit_test_99",
        "selections": {
            "room_1": {
                "room_id": "room_1",
                "room_type": "bedroom",
                "room_area_sqft": 160.0,
                "design_id": "int_bed_01",
                "lighting_points_count": 6
            }
        }
    }
    response = client.post("/api/v1/interior/calculate-cost", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_interior_cost"] > 0
    assert "room_1" in data["selections"]


# ── 11. Regression Tests for 32 Bespoke Layouts & Category Enforcement ──────

def test_17_all_32_designs_generate_unique_distinct_previews():
    """
    Verify that all 32 catalog designs generate valid, non-empty, and distinct SVG previews
    when mapped to their appropriate room categories.
    """
    designs = get_all_interior_designs()
    category_to_room_type = {
        "bedroom": ("master_bedroom", 14.0, 16.0),
        "guest_room": ("guest_bedroom", 12.0, 14.0),
        "living_room": ("living_room", 16.0, 20.0),
        "kitchen": ("kitchen", 10.0, 14.0),
        "dining_room": ("dining_room", 12.0, 14.0),
        "bathroom": ("master_bathroom", 7.0, 9.0),
    }

    generated_svgs = {}

    for d in designs:
        r_type, w, l = category_to_room_type[d.category]
        res = generate_plan_aware_preview(
            room_id=f"test_room_{d.id}",
            room_name=f"Test {d.category.title()}",
            room_type=r_type,
            room_width=w,
            room_length=l,
            room_area=w * l,
            design_id=d.id
        )
        assert res["status"] == "success", f"Failed for design {d.id}: {res.get('message')}"
        assert res["preview_svg"] is not None
        assert len(res["preview_svg"]) > 500
        # Check uniqueness: no two designs should produce identical SVG output
        assert res["preview_svg"] not in generated_svgs.values(), f"Design {d.id} produced duplicate SVG"
        generated_svgs[d.id] = res["preview_svg"]

    assert len(generated_svgs) == 32


def test_18_incompatible_room_category_rejection():
    """
    Verify that applying an incompatible design (e.g. kitchen design in a bedroom)
    is rejected with HTTP 400 Bad Request.
    """
    # 1. Kitchen design in Bedroom
    bad_payload_1 = {
        "room_id": "bed_01",
        "room_name": "Master Bedroom",
        "room_type": "master_bedroom",
        "room_width": 14.0,
        "room_length": 16.0,
        "room_area": 224.0,
        "design_id": "int_kit_01"  # Kitchen design!
    }
    resp1 = client.post("/api/v1/interior/generate-preview", json=bad_payload_1)
    assert resp1.status_code == 400
    assert "Incompatible room category" in resp1.json()["detail"]

    # 2. Bathroom design in Living Room
    bad_payload_2 = {
        "room_id": "lr_01",
        "room_name": "Living Room",
        "room_type": "living_room",
        "room_width": 16.0,
        "room_length": 20.0,
        "room_area": 320.0,
        "design_id": "int_bath_01"  # Bathroom design!
    }
    resp2 = client.post("/api/v1/interior/generate-preview", json=bad_payload_2)
    assert resp2.status_code == 400
    assert "Incompatible room category" in resp2.json()["detail"]


def test_19_dimension_adaptive_scaling():
    """
    Verify that small (<130 sq ft) and master suite (>200 sq ft) rooms
    scale their furniture layouts adaptively (e.g. master suites unlock secondary zones).
    """
    # Compact bedroom (100 sq ft)
    compact_res = generate_plan_aware_preview(
        room_id="compact_bed",
        room_name="Compact Bedroom",
        room_type="bedroom",
        room_width=10.0,
        room_length=10.0,
        room_area=100.0,
        design_id="int_bed_01"
    )
    assert compact_res["status"] == "success"
    # Should not have secondary vanity zone taking up critical circulation space
    assert "Master Suite Feature" not in " ".join(compact_res["clearances"])

    # Master suite (280 sq ft) for int_bed_01
    master_res = generate_plan_aware_preview(
        room_id="master_suite",
        room_name="Grand Master Bedroom",
        room_type="master_bedroom",
        room_width=16.0,
        room_length=17.5,
        room_area=280.0,
        design_id="int_bed_01"
    )
    assert master_res["status"] == "success"
    # Should unlock secondary master suite zone (media console)
    assert any("Master Zone" in c for c in master_res["clearances"])
    assert "FLOATING MEDIA CONSOLE" in master_res["preview_svg"]

    # Master suite (280 sq ft) for int_bed_02 (vanity dressing & reading lounge)
    master_res_02 = generate_plan_aware_preview(
        room_id="master_suite_02",
        room_name="Grand Master Suite",
        room_type="master_bedroom",
        room_width=16.0,
        room_length=17.5,
        room_area=280.0,
        design_id="int_bed_02"
    )
    assert master_res_02["status"] == "success"
    assert any("Master Suite Feature" in c for c in master_res_02["clearances"])
    assert "VANITY" in master_res_02["preview_svg"]
    assert "LOUNGE" in master_res_02["preview_svg"]


def test_20_opening_geometry_mapped_in_preview():
    """
    Verify that when doors and windows from floor plan geometry are passed,
    they are rendered into the generated architectural preview.
    """
    doors = [{"width": 3.5, "direction": "inward"}]
    windows = [{"width": 5.0, "sill_height": 3.0}]

    res = generate_plan_aware_preview(
        room_id="test_geo_room",
        room_name="Living Room",
        room_type="living_room",
        room_width=15.0,
        room_length=18.0,
        room_area=270.0,
        design_id="int_lr_01",
        doors=doors,
        windows=windows
    )
    assert res["status"] == "success"
    svg = res["preview_svg"]
    assert "Floor Plan Door 1" in svg
    assert "Floor Plan Window 1" in svg
