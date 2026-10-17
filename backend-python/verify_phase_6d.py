"""
Phase 6D Verification Runner.
Executes CostEstimationEngine on both canonical layouts (30x40 and 50x80)
and prints key quantities, cost breakdowns, and area schedules.
"""

import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.models.layout import LayoutData
from app.services.cost_estimation.engine import CostEstimationEngine

CANONICAL_DIR = os.path.join(os.path.dirname(__file__), "canonical_layouts")

def run_verification():
    print("=" * 80)
    print("PHASE 6D: CONSTRUCTION COST ESTIMATION ENGINE VERIFICATION")
    print("=" * 80)

    for case_name, filename in [
        ("30×40 East-Facing G+1", "canonical_30x40_east_g1.json"),
        ("50×80 South-Facing G+1", "canonical_50x80_south_g1.json")
    ]:
        print(f"\nEvaluating: {case_name} ({filename})")
        print("-" * 80)
        filepath = os.path.join(CANONICAL_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            layout = LayoutData.model_validate_json(f.read())

        engine = CostEstimationEngine(layout, project_id=f"VERIFY-{filename[:12]}")
        estimate = engine.calculate_estimate()

        sched = estimate.area_schedule
        summ = estimate.cost_summary
        q = estimate.quantities

        print(f"Area Schedule:")
        print(f"  Plot Area                    : {sched.plot_area:,.1f} sq ft")
        print(f"  Ground Constructed Footprint : {sched.ground_constructed_footprint:,.1f} sq ft")
        print(f"  Total Built-Up Area (BUA)    : {sched.total_built_up_area:,.1f} sq ft")
        print(f"  Net Indoor Room Area         : {sched.total_indoor_room_area:,.1f} sq ft")
        print(f"  Wall Footprint Area          : {sched.wall_footprint_area:,.1f} sq ft")
        print(f"  Outdoor/Terrace Spaces Count : {len(sched.outdoor_areas) + len(sched.terrace_roof_areas)}")

        print(f"\nKey Material Quantities:")
        print(f"  Total Cement Bags (50kg)     : {q['total_cement_bags']:,} bags")
        print(f"  Manufactured Sand (M-Sand)   : {q['total_sand_cuft']:,.1f} cu ft")
        print(f"  Coarse Aggregate (20mm)      : {q['total_coarse_aggregate_cuft']:,.1f} cu ft")
        print(f"  Standard Red Clay Bricks     : {q['total_bricks_count']:,} pieces")
        print(f"  Structural Steel (Fe 550D)   : {q['total_steel_kg']:,.1f} kg ({q['total_steel_tonnes']:.2f} Tonnes)")
        print(f"  Indoor Vitrified Flooring    : {q['indoor_flooring_sqft']:,.1f} sq ft")
        print(f"  Total Plastering Surface     : {q['total_plaster_sqft']:,.1f} sq ft")
        print(f"  Wall Opening Deductions      : {q['door_deductions_sqft'] + q['window_deductions_sqft']:,.1f} sq ft")

        print(f"\nCost Summary Breakdown (Hyderabad Benchmark, INR ₹):")
        print(f"  Materials Cost               : ₹ {summ.materials_cost:,.2f}")
        print(f"  Civil & Finishing Labor Cost : ₹ {summ.labor_cost:,.2f}")
        print(f"  Openings & Fixtures Cost     : ₹ {summ.openings_and_fixtures_cost:,.2f}")
        print(f"  Services (Plumbing/Electric) : ₹ {summ.services_cost:,.2f}")
        print(f"  Subtotal                     : ₹ {summ.subtotal:,.2f}")
        print(f"  Contingency ({summ.contingency_percentage}%)           : ₹ {summ.contingency_cost:,.2f}")
        print(f"  Contractor Overhead ({summ.contractor_overhead_percentage}%): ₹ {summ.contractor_overhead_cost:,.2f}")
        print(f"  GRAND TOTAL ESTIMATED COST   : ₹ {summ.grand_total:,.2f}")
        print(f"  Cost Per Sq Ft               : ₹ {summ.cost_per_sq_ft:,.2f} / sq ft")
        print(f"  Denominator                  : {summ.cost_per_sq_ft_denominator}")

    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE: ALL QUANTITIES DETERMINISTICALLY CALCULATED")
    print("=" * 80)

if __name__ == "__main__":
    run_verification()
