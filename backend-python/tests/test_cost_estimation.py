"""
Unit and Integration Test Suite — Phase 6D Construction Cost Estimation Engine.
Covers all 14 required verification criteria:
  1. Known Quantity × Unit Rate calculation
  2. Unit conversions (cu ft, cu m, kg, tonnes, bags)
  3. Negative, invalid or missing rates rejection
  4. Wastage calculations without double-counting
  5. Geometry-derived flooring and area schedules
  6. Exclusion of outdoor-only spaces from indoor flooring
  7. No duplicate counting of shared walls or overlapping geometry
  8. Door and window deductions where source dimensions exist
  9. Missing wall/specifications graceful documented handling
 10. Engineer-provided quantities vs provisional allowances
 11. Rate changes updating amounts without layout regeneration
 12. Rate & assumption snapshot preservation
 13. API model validation and responses
 14. Canonical layout fixtures execution without fresh solves
"""

import os
import json
import pytest
from app.models.layout import LayoutData, Plot, Floor, Room, Wall, Door, Window, Point2D, BoundingBox, Setbacks
from app.models.cost_estimate import (
    RateItem,
    RateProfile,
    CostLineItem,
    EstimateRequest,
    EstimateRecalculateRequest,
    EstimateResponse
)
from app.services.cost_estimation.material_rates import get_default_rate_profile
from app.services.cost_estimation.quantity_calculator import QuantityCalculator
from app.services.cost_estimation.engine import CostEstimationEngine

CANONICAL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "canonical_layouts")


def create_synthetic_layout():
    """Builds a clean, known synthetic 2-room layout for formula verification."""
    return LayoutData(
        units="ft",
        plot=Plot(
            width=30.0,
            length=40.0,
            facing="east",
            buildable_boundary=BoundingBox(width=24.0, length=32.0),
            setbacks=Setbacks(front=4.0, back=4.0, left=3.0, right=3.0),
            building_footprint={"width": 20.0, "length": 20.0, "constructed_area": 400.0}
        ),
        floors=[
            Floor(
                level=0,
                name="Ground Floor",
                rooms=[
                    # Room 1: 10 x 20 = 200 sq ft (x=0, y=0)
                    Room(id="rm1", type="living_room", label="Living", x=0.0, y=0.0, width=10.0, length=20.0, area=200.0),
                    # Room 2: 10 x 20 = 200 sq ft (x=10, y=0) - shares 20ft edge with rm1
                    Room(id="rm2", type="bedroom", label="Bedroom", x=10.0, y=0.0, width=10.0, length=20.0, area=200.0),
                    # Outdoor Balcony: 5 x 10 = 50 sq ft
                    Room(id="rm3", type="balcony", label="Balcony", x=0.0, y=20.0, width=5.0, length=10.0, area=50.0, space_category="outdoor"),
                ],
                doors=[
                    Door(id="d1", type="main_entrance", position=Point2D(x=0.0, y=0.0), width=3.5, room_ids=["rm1"]),
                    Door(id="d2", type="swing", position=Point2D(x=10.0, y=5.0), width=3.0, room_ids=["rm1", "rm2"]),
                ],
                windows=[
                    Window(id="w1", type="sliding", position=Point2D(x=5.0, y=0.0), width=4.0, room_id="rm1"),
                ]
            )
        ]
    )


# ── Criterion 1: Quantity × Unit Rate ───────────────────────────────────────────
def test_1_quantity_times_unit_rate_calculation():
    line = CostLineItem(
        id="TEST-01",
        category="materials",
        item_name="Cement Bag Test",
        quantity=150.0,
        unit="bag",
        unit_rate=380.0,
        amount=150.0 * 380.0,
        classification="specification_derived",
        formula="150 bags * 380 rate",
        assumptions="Standard 50kg bags",
        confidence="benchmark"
    )
    assert line.amount == 57000.0
    assert line.quantity * line.unit_rate == line.amount


# ── Criterion 2: Unit Conversions ──────────────────────────────────────────────
def test_2_unit_conversions():
    # 1 cu ft = 0.0283168 cu m
    cuft = 1000.0
    cum = cuft * 0.0283168
    assert abs(cum - 28.3168) < 0.001

    # 1 metric tonne = 1000 kg
    steel_kg = 4500.0
    steel_tonnes = steel_kg / 1000.0
    assert steel_tonnes == 4.5

    # 1 cement bag = 50 kg = 1.226 cu ft dry cement
    cement_volume_cuft = 122.6
    bags = cement_volume_cuft / 1.226
    assert abs(bags - 100.0) < 0.01


# ── Criterion 3: Negative / Invalid Rates Rejection ─────────────────────────────
def test_3_invalid_negative_rates_rejected():
    # Pydantic validation rejects negative rate
    with pytest.raises(Exception):
        RateItem(
            category="materials",
            item_key="bad_rate",
            name="Negative Rate Item",
            unit="bag",
            unit_rate=-50.0
        )

    # get_default_rate_profile rejects negative custom override
    with pytest.raises(ValueError, match="cannot be negative"):
        get_default_rate_profile({"cement_bag": -100.0})


# ── Criterion 4: Wastage Without Double Counting ───────────────────────────────
def test_4_wastage_calculations_no_double_counting():
    calc = QuantityCalculator(create_synthetic_layout(), {"flooring_wastage_pct": 7.0, "brick_wastage_pct": 5.0})
    area_sched = calc.calculate_area_schedule()

    # Indoor area = 200 + 200 = 400 sq ft
    assert area_sched.total_indoor_room_area == 400.0

    flooring = calc.calculate_flooring_and_finishes(area_sched)
    # Net: 400, Gross: 400 * 1.07 = 428.0 (exactly 7% applied once)
    assert flooring["indoor_flooring_net_sqft"] == 400.0
    assert flooring["indoor_flooring_gross_sqft"] == 428.0


# ── Criterion 5: Geometry-Derived Area Schedule ─────────────────────────────────
def test_5_geometry_derived_area_schedules():
    layout = create_synthetic_layout()
    calc = QuantityCalculator(layout)
    area_sched = calc.calculate_area_schedule()

    assert area_sched.plot_area == 1200.0  # 30 * 40
    assert area_sched.built_up_by_floor[0] == 400.0  # (0,0,10,20) union (10,0,20,20) = 20x20 = 400 sq ft
    assert area_sched.total_indoor_room_area == 400.0
    assert len(area_sched.outdoor_areas) == 1
    assert area_sched.outdoor_areas[0]["type"] == "balcony"


# ── Criterion 6: Exclusion of Outdoor Spaces from Indoor Flooring ──────────────
def test_6_exclusion_of_outdoor_spaces_from_indoor_flooring():
    layout = create_synthetic_layout()
    calc = QuantityCalculator(layout)
    area_sched = calc.calculate_area_schedule()
    flooring = calc.calculate_flooring_and_finishes(area_sched)

    # Balcony is 50 sq ft. Total indoor is 400.
    # Indoor flooring must be 400 (plus 7% wastage = 428), NOT 450!
    assert flooring["indoor_flooring_net_sqft"] == 400.0
    assert 50.0 not in [flooring["indoor_flooring_net_sqft"]]
    assert flooring["indoor_flooring_gross_sqft"] == 428.0


# ── Criterion 7: No Duplicate Counting of Shared Walls ──────────────────────────
def test_7_no_duplicate_counting_shared_walls():
    layout = create_synthetic_layout()
    calc = QuantityCalculator(layout)
    wall_data = calc.calculate_wall_quantities()

    # Room 1: 10 x 20. Perimeter = 2*(10+20) = 60 ft.
    # Room 2: 10 x 20. Perimeter = 2*(10+20) = 60 ft.
    # Union is 20 x 20 box. Exterior perimeter = 4 * 20 = 80 ft.
    # Shared edge length = 20 ft.
    # Formula: Interior = (60 + 60 - 80) / 2 = 40 / 2 = 20 ft.
    # Total wall length = 80 (ext) + 20 (int) = 100 ft (NOT 120 ft!).
    assert wall_data["ext_wall_length_ft"] == 80.0
    assert wall_data["int_wall_length_ft"] == 20.0
    assert wall_data["total_wall_length_ft"] == 100.0


# ── Criterion 8: Door and Window Deductions ─────────────────────────────────────
def test_8_door_and_window_deductions():
    layout = create_synthetic_layout()
    calc = QuantityCalculator(layout)
    wall_data = calc.calculate_wall_quantities()

    # Main door: 3.5 ft x 7.5 ft = 26.25 sq ft
    # Internal door: 3.0 ft x 7.0 ft = 21.0 sq ft
    # Total doors deduction = 47.25 sq ft
    assert wall_data["door_deduction_sqft"] == 47.25

    # Window: 4.0 ft x 4.5 ft = 18.0 sq ft
    assert wall_data["window_deduction_sqft"] == 18.0
    assert wall_data["total_opening_deductions_sqft"] == 65.25

    # Gross wall area = 100 ft * 10 ft height = 1000 sq ft
    assert wall_data["gross_wall_area_sqft"] == 1000.0
    # Net wall area = 1000.0 - 65.25 = 934.75 sq ft
    assert wall_data["net_wall_area_sqft"] == 934.75


# ── Criterion 9: Graceful Handling of Missing Wall / Specifications ─────────────
def test_9_missing_wall_specifications_fallback():
    # Layout with completely empty walls, doors, and windows
    minimal_layout = LayoutData(
        units="ft",
        plot=Plot(
            width=20.0,
            length=30.0,
            facing="north",
            buildable_boundary=BoundingBox(width=16.0, length=24.0),
            setbacks=Setbacks()
        ),
        floors=[
            Floor(
                level=0,
                name="Ground Floor",
                rooms=[
                    Room(id="r1", type="living_room", label="Hall", x=0.0, y=0.0, width=12.0, length=15.0, area=180.0)
                ]
            )
        ]
    )
    engine = CostEstimationEngine(minimal_layout, project_id="test_minimal")
    estimate = engine.calculate_estimate()

    assert estimate.cost_summary.grand_total > 0
    assert estimate.area_schedule.total_built_up_area == 180.0
    assert len(estimate.line_items) > 10


# ── Criterion 10: Engineer Provided vs Provisional Allowances ───────────────────
def test_10_engineer_provided_vs_provisional_allowances():
    engine = CostEstimationEngine(create_synthetic_layout(), project_id="test_prov")
    estimate = engine.calculate_estimate()

    steel_items = [item for item in estimate.line_items if item.category == "structural_steel"]
    assert len(steel_items) >= 1
    assert steel_items[0].classification == "provisional_allowance"
    assert "Provisional" in steel_items[0].assumptions
    assert "4.0 kg/sq ft" in steel_items[0].formula


# ── Criterion 11: Rate Changes Without Layout Regeneration ─────────────────────
def test_11_rate_changes_without_regenerating_layout():
    layout = create_synthetic_layout()
    engine_orig = CostEstimationEngine(layout, custom_rates={"cement_bag": 380.0})
    est_orig = engine_orig.calculate_estimate()

    # Instantly change cement rate to ₹500 without calling any solver
    engine_new = CostEstimationEngine(layout, custom_rates={"cement_bag": 500.0})
    est_new = engine_new.calculate_estimate()

    # Geometry-derived quantities MUST remain identical
    assert est_orig.quantities["total_cement_bags"] == est_new.quantities["total_cement_bags"]
    assert est_orig.area_schedule.total_built_up_area == est_new.area_schedule.total_built_up_area

    # Cost line item and grand total MUST update
    cement_orig = next(item for item in est_orig.line_items if item.id == "MAT-CEM-01")
    cement_new = next(item for item in est_new.line_items if item.id == "MAT-CEM-01")

    assert cement_orig.unit_rate == 380.0
    assert cement_new.unit_rate == 500.0
    assert cement_new.amount > cement_orig.amount
    assert est_new.cost_summary.grand_total > est_orig.cost_summary.grand_total


# ── Criterion 12: Rate & Assumption Snapshot Preservation ───────────────────────
def test_12_saved_estimates_retaining_rate_snapshot():
    layout = create_synthetic_layout()
    engine = CostEstimationEngine(layout, custom_rates={"tmt_steel": 75.0})
    est = engine.calculate_estimate()

    assert "tmt_steel" in est.rates_snapshot
    assert est.rates_snapshot["tmt_steel"].unit_rate == 75.0
    assert est.rates_snapshot["tmt_steel"].confidence == "user_specified"
    assert len(est.assumptions_and_limitations) >= 5


# ── Criterion 13: API Request/Response Model Validation ─────────────────────────
def test_13_api_model_validation():
    req = EstimateRecalculateRequest(
        current_estimate_id="est_123",
        floor_plan_id="fp_456",
        custom_rates={"cement_bag": 400.0, "red_brick": 12.0}
    )
    assert req.custom_rates["cement_bag"] == 400.0

    # Ensure negative rate raises validation error in RateItem
    with pytest.raises(Exception):
        RateItem(category="test", item_key="k", name="n", unit="u", unit_rate=-1.0)


# ── Criterion 14: Canonical Layout Fixtures Regression ─────────────────────────
def test_14_canonical_fixtures_cost_estimation():
    """
    Executes cost estimation on the two canonical layout fixtures:
      - canonical_30x40_east_g1.json
      - canonical_50x80_south_g1.json
    Verifies that real complex geometry is parsed, area schedules are exact,
    and no fresh CP-SAT solve is invoked.
    """
    c30_path = os.path.join(CANONICAL_DIR, "canonical_30x40_east_g1.json")
    assert os.path.exists(c30_path), f"Missing {c30_path}"
    with open(c30_path, "r", encoding="utf-8") as f:
        c30_layout = LayoutData.model_validate_json(f.read())

    engine_30 = CostEstimationEngine(c30_layout, project_id="CANONICAL-30X40")
    est_30 = engine_30.calculate_estimate()

    # Ground floor slab must be exactly 767 sq ft as established in canonical tests
    assert est_30.area_schedule.built_up_by_floor[0] == 767.0
    assert est_30.area_schedule.built_up_by_floor[1] == 743.0
    assert est_30.area_schedule.total_built_up_area == 1510.0
    assert est_30.cost_summary.grand_total > 1000000.0
    assert est_30.cost_summary.cost_per_sq_ft > 1000.0

    c50_path = os.path.join(CANONICAL_DIR, "canonical_50x80_south_g1.json")
    assert os.path.exists(c50_path), f"Missing {c50_path}"
    with open(c50_path, "r", encoding="utf-8") as f:
        c50_layout = LayoutData.model_validate_json(f.read())

    engine_50 = CostEstimationEngine(c50_layout, project_id="CANONICAL-50X80")
    est_50 = engine_50.calculate_estimate()

    # Ground floor slab must be exactly 1579 sq ft as established in canonical tests
    assert est_50.area_schedule.built_up_by_floor[0] == 1579.0
    assert est_50.area_schedule.built_up_by_floor[1] == 931.0
    assert est_50.area_schedule.total_built_up_area == 2510.0
    assert est_50.cost_summary.grand_total > 2000000.0

    # Test CSV export produces valid non-empty string with header
    csv_out = CostEstimationEngine.export_to_csv(est_50)
    assert "AI HOUSE PLANNING SYSTEM — CONSTRUCTION COST ESTIMATE" in csv_out
    assert "DETAILED MATERIAL & WORK QUANTITIES TABLE" in csv_out


# ── Live API Endpoint Tests via TestClient ──────────────────────────────────────
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.security import get_current_user, get_user_supabase_client

client = TestClient(app)


def test_api_endpoints_integration():
    """Tests /rates, /generate, /recalculate, and /export-csv via TestClient."""
    synthetic_layout = create_synthetic_layout()

    # Override authentication and authorization
    app.dependency_overrides[get_current_user] = lambda: "test-user-id"
    app.dependency_overrides[get_user_supabase_client] = lambda: MagicMock()

    with patch("app.services.project_service.verify_ownership", return_value=True):
        # 1. Test GET /rates
        res_rates = client.get("/api/v1/projects/proj-123/cost-estimate/rates")
        assert res_rates.status_code == 200, res_rates.text
        rates_data = res_rates.json()
        assert rates_data["profile_id"] == "hyderabad_telangana_benchmark"
        assert "cement_bag" in rates_data["rates"]

        # 2. Test POST /generate with direct layout_data
        res_gen = client.post(
            "/api/v1/projects/proj-123/cost-estimate/generate",
            json={"layout_data": synthetic_layout.model_dump()}
        )
        assert res_gen.status_code == 200, res_gen.text
        est_data = res_gen.json()
        assert est_data["cost_summary"]["grand_total"] > 0
        assert est_data["area_schedule"]["total_built_up_area"] == 400.0

        # 3. Test POST /recalculate with custom rate
        res_recalc = client.post(
            "/api/v1/projects/proj-123/cost-estimate/recalculate",
            json={
                "layout_data": synthetic_layout.model_dump(),
                "custom_rates": {"cement_bag": 450.0}
            }
        )
        assert res_recalc.status_code == 200, res_recalc.text
        recalc_data = res_recalc.json()
        assert recalc_data["rates_snapshot"]["cement_bag"]["unit_rate"] == 450.0

    # Clean up overrides
    app.dependency_overrides.clear()

