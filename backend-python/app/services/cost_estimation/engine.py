"""
Construction Cost Estimation Engine — Phase 6D.
Coordinates geometry extraction, quantity calculation, rate lookup,
line-item aggregation, cost breakdowns, and CSV export.
"""

import uuid
import datetime
import io
import csv
from typing import Dict, Any, List, Optional
from app.models.layout import LayoutData
from app.models.cost_estimate import (
    EstimateResponse,
    AreaScheduleSummary,
    CostLineItem,
    CostSummary,
    RateItem,
    RateProfile
)
from app.services.cost_estimation.material_rates import get_default_rate_profile
from app.services.cost_estimation.quantity_calculator import QuantityCalculator


class CostEstimationEngine:
    def __init__(
        self,
        layout: LayoutData,
        project_id: str = "default_project",
        floor_plan_id: Optional[str] = None,
        custom_rates: Optional[Dict[str, float]] = None,
        custom_specifications: Optional[Dict[str, Any]] = None
    ):
        self.layout = layout
        self.project_id = project_id
        self.floor_plan_id = floor_plan_id
        self.custom_rates = custom_rates or {}
        self.custom_specs = custom_specifications or {}

        # 1. Initialize calculator
        self.calculator = QuantityCalculator(self.layout, self.custom_specs)

        # 2. Sourced and validated rate profile
        self.rate_profile = get_default_rate_profile(self.custom_rates)

    def calculate_estimate(self) -> EstimateResponse:
        """
        Executes full deterministic cost estimation and returns structured EstimateResponse.
        """
        # A. Geometry-derived area schedule
        area_schedule = self.calculator.calculate_area_schedule()
        total_bua = area_schedule.total_built_up_area

        # Guard against zero built-up area
        if total_bua <= 0:
            total_bua = max(1.0, area_schedule.plot_area * 0.6)

        # B. Wall quantities and opening deductions
        wall_data = self.calculator.calculate_wall_quantities()

        # C. Concrete and steel quantities
        concrete_steel = self.calculator.calculate_concrete_and_steel(total_bua)

        # D. Mortar materials (cement & sand for brickwork and plaster)
        mortar = self.calculator.calculate_mortar_materials(
            wall_data["masonry_volume_cuft"],
            wall_data["total_plaster_area_sqft"]
        )

        # E. Flooring, paving and waterproofing
        flooring = self.calculator.calculate_flooring_and_finishes(area_schedule)

        # F. Fixtures and services
        fixtures = self.calculator.calculate_fixtures_and_services(area_schedule, wall_data)

        # Total combined material quantities
        total_cement_bags = concrete_steel["cement_bags_concrete"] + mortar["total_cement_bags_mortar"]
        total_sand_cuft = round(concrete_steel["sand_cuft_concrete"] + mortar["total_sand_cuft_mortar"], 2)
        total_coarse_agg_cuft = concrete_steel["coarse_aggregate_cuft_concrete"]
        total_steel_kg = concrete_steel["steel_reinforcement_kg"]
        total_bricks = wall_data["bricks_count_pieces"]

        # Snapshot of rates used
        rates = self.rate_profile.rates

        # G. Build explicit CostLineItems
        line_items: List[CostLineItem] = []

        # Helper to safely create a line item
        def add_line(
            line_id: str,
            category: str,
            item_name: str,
            quantity: float,
            unit: str,
            rate_key: str,
            classification: str,
            formula: str,
            assumptions: str
        ):
            rate_obj = rates.get(rate_key)
            unit_rate = rate_obj.unit_rate if rate_obj else 0.0
            amount = round(quantity * unit_rate, 2)
            confidence = rate_obj.confidence if rate_obj else "benchmark"

            line_items.append(CostLineItem(
                id=line_id,
                category=category,
                item_name=item_name,
                quantity=round(quantity, 2),
                unit=unit,
                unit_rate=round(unit_rate, 2),
                amount=amount,
                classification=classification,
                formula=formula,
                assumptions=assumptions,
                confidence=confidence
            ))

        # ── 1. Structural Materials ──────────────────────────────────────
        add_line(
            "MAT-CEM-01", "materials",
            "Cement (PPC / OPC 53 Grade - Total for RCC, Brickwork & Plaster)",
            total_cement_bags, "bag", "cement_bag",
            "specification_derived",
            f"RCC Concrete ({concrete_steel['cement_bags_concrete']} bags) + Brickwork Mortar ({mortar['cement_bags_brickwork']} bags) + Plaster ({mortar['cement_bags_plaster']} bags)",
            "50 kg standard bags. Includes 3% handling and batching wastage."
        )

        add_line(
            "MAT-SND-01", "materials",
            "Manufactured Sand (M-Sand for RCC Concrete & Masonry Plaster)",
            total_sand_cuft, "cu ft", "m_sand",
            "specification_derived",
            f"Concrete Sand ({concrete_steel['sand_cuft_concrete']} cu ft) + Mortar Sand ({mortar['total_sand_cuft_mortar']} cu ft)",
            "Crushed granite sand conforming to IS 383 Zone II. Includes 5% wastage."
        )

        add_line(
            "MAT-AGG-01", "materials",
            "Coarse Aggregate (20mm Blue Metal Granite for RCC Works)",
            total_coarse_agg_cuft, "cu ft", "coarse_aggregate",
            "specification_derived",
            f"M20 Mix Dry Vol {concrete_steel['total_concrete_cuft']} cu ft × 1.54 × (3/5.5)",
            "Machine crushed blue metal aggregate. Includes 5% wastage."
        )

        add_line(
            "MAT-STL-01", "structural_steel",
            f"TMT Fe 550D Steel Reinforcement Rebar ({concrete_steel['steel_reinforcement_tonnes']} Tonnes)",
            total_steel_kg, "kg", "tmt_steel",
            "provisional_allowance",
            f"Total Built-Up Area ({total_bua} sq ft) × {concrete_steel['steel_factor_applied']}",
            "Provisional estimating allowance (4.0 kg/sq ft). Actual structural steel must be verified with certified engineer's structural drawing and bar bending schedule (BBS)."
        )

        add_line(
            "MAT-BRK-01", "masonry",
            "Standard Red Clay Bricks (Wire Cut Kiln Bricks for Superstructure)",
            total_bricks, "piece", "red_brick",
            "geometry_derived",
            f"Net Masonry Volume ({wall_data['masonry_volume_cuft']} cu ft) × 13.5 bricks/cu ft × 1.05 wastage",
            "9\" exterior walls and 4.5\" interior partitions after door and window opening deductions."
        )

        # ── 2. Flooring & Tiling ──────────────────────────────────────────
        add_line(
            "FLR-VIT-01", "flooring",
            "Indoor Vitrified Floor Tiles (Double Charged / GVT 2'x2')",
            flooring["indoor_flooring_gross_sqft"], "sq ft", "indoor_flooring_tile",
            "geometry_derived",
            f"Net Indoor Room Area ({flooring['indoor_flooring_net_sqft']} sq ft) + 7% cutting wastage",
            "Strictly excludes outdoor surfaces, balconies, and parking."
        )

        if flooring["outdoor_paving_gross_sqft"] > 0:
            add_line(
                "FLR-OUT-01", "flooring",
                "Outdoor Anti-Skid Ceramic / Heavy Duty Balcony & Terrace Tiles",
                flooring["outdoor_paving_gross_sqft"], "sq ft", "outdoor_paving_tile",
                "geometry_derived",
                f"Upper Outdoor Areas ({round(flooring['outdoor_paving_gross_sqft']/1.08, 1)} sq ft) + 8% wastage",
                "Anti-skid exterior grade vitrified / ceramic tiles."
            )

        if flooring["staircase_granite_sqft"] > 0:
            add_line(
                "FLR-GRN-01", "flooring",
                "Polished Natural Granite for Staircase (Treads, Risers & Landing)",
                flooring["staircase_granite_sqft"], "sq ft", "staircase_granite",
                "geometry_derived",
                f"Staircase footprint area × 1.35 vertical tread/riser factor",
                "18mm thick pre-polished gangsaw granite with chamfered bull-nosing."
            )

        add_line(
            "FLR-SKR-01", "flooring",
            "Matching Tile Skirting (100mm height)",
            flooring["skirting_running_ft"], "running ft", "skirting_tile",
            "geometry_derived",
            f"Indoor perimeter skirting allowance ({flooring['skirting_running_ft']} RFT)",
            "Installed along all indoor wall bases."
        )

        # ── 3. Plastering, Painting & Waterproofing ───────────────────────
        add_line(
            "FIN-PNT-INT", "finishes",
            "Interior Wall Putty & Premium Acrylic Emulsion Paint",
            wall_data["internal_paint_area_sqft"], "sq ft", "internal_paint_putty",
            "geometry_derived",
            f"Net interior wall faces + Ceiling area ({wall_data['internal_paint_area_sqft']} sq ft)",
            "2 coats putty + 1 coat primer + 2 coats interior emulsion."
        )

        add_line(
            "FIN-PNT-EXT", "finishes",
            "Exterior Weatherproof Anti-Fungal Acrylic Emulsion Paint",
            wall_data["external_paint_area_sqft"], "sq ft", "external_weatherproof_paint",
            "geometry_derived",
            f"Exterior building envelope face area ({wall_data['external_paint_area_sqft']} sq ft)",
            "1 coat exterior primer + 2 coats exterior weather guard paint."
        )

        if flooring["waterproofing_sqft"] > 0:
            add_line(
                "FIN-WTR-01", "finishes",
                "Elastomeric Membrane Waterproofing (Terraces, Balconies & Toilets)",
                flooring["waterproofing_sqft"], "sq ft", "terrace_waterproofing",
                "geometry_derived",
                f"Exposed terrace/roof slab below + wet area toilet floors ({flooring['waterproofing_sqft']} sq ft)",
                "Polymer-modified cementitious coating with fiberglass mesh."
            )

        # ── 4. Openings & Fixtures ─────────────────────────────────────────
        door_counts = wall_data["door_counts"]
        if door_counts["main"] > 0:
            add_line(
                "OPN-DOR-01", "openings",
                "Teak Wood Main Entrance Door Assembly",
                float(door_counts["main"]), "unit", "door_main_entrance",
                "fixture_count",
                f"Counted from floor plan doors: {door_counts['main']} main door(s)",
                "Complete with heavy teak wood frame, brass fittings, handles, and digital/mortise lock."
            )

        if door_counts["internal"] > 0:
            add_line(
                "OPN-DOR-02", "openings",
                "Internal Flush / Laminated Doors with Hardwood Frame",
                float(door_counts["internal"]), "unit", "door_internal",
                "fixture_count",
                f"Counted from floor plan interior doors: {door_counts['internal']} door(s)",
                "Solid core flush door with laminate finish and SS lock set."
            )

        if door_counts["toilet"] > 0:
            add_line(
                "OPN-DOR-03", "openings",
                "Waterproof PVC / FRP Bathroom & Utility Doors",
                float(door_counts["toilet"]), "unit", "door_toilet",
                "fixture_count",
                f"Counted from floor plan wet areas: {door_counts['toilet']} door(s)",
                "100% waterproof molded PVC doors with polymer frames."
            )

        if wall_data["total_window_area_sqft"] > 0:
            add_line(
                "OPN-WIN-01", "openings",
                "UPVC Sliding Windows with Float Glass & Mosquito Mesh",
                wall_data["total_window_area_sqft"], "sq ft", "window_upvc",
                "geometry_derived",
                f"Total window opening area ({wall_data['total_window_area_sqft']} sq ft)",
                "3-track UPVC sliding window with 5mm clear toughened glass and SS insect mesh."
            )

        if fixtures["staircase_railing_rft"] > 0:
            add_line(
                "OPN-RAL-01", "openings",
                "Stainless Steel (SS 304 Grade) Staircase Railing",
                fixtures["staircase_railing_rft"], "running ft", "staircase_railing_ss",
                "specification_derived",
                f"Staircase railing length ({fixtures['staircase_railing_rft']} RFT)",
                "SS 304 balusters and polished handrail."
            )

        # ── 5. Services (Plumbing & Electrical) ───────────────────────────
        add_line(
            "SRV-PLM-01", "services",
            f"Sanitaryware, CP Fittings & Internal Plumbing ({fixtures['wet_areas_count']} Wet Areas)",
            float(fixtures["wet_areas_count"]), "point", "plumbing_sanitary_point",
            "fixture_count",
            f"Allocated per wet room ({fixtures['wet_areas_count']} bathrooms, toilets & kitchens)",
            "Wall-hung EWC, wash basin, diverter, overhead shower, and CPVC/PVC concealed piping."
        )

        add_line(
            "SRV-ELE-01", "services",
            "Electrical Conduits, FRLS Wiring, Modular Switches & Distribution Board",
            float(fixtures["total_electrical_points"]), "point", "electrical_point_allowance",
            "provisional_allowance",
            f"Estimated at 1 point per 22 sq ft + 10 appliance points/floor ({fixtures['total_electrical_points']} points)",
            "Concealed PVC conduit with copper multi-strand fire-retardant low-smoke wiring and modular plates."
        )

        # ── 6. Civil & Workmanship Labor ──────────────────────────────────
        add_line(
            "LBR-CIV-01", "labor",
            "Civil Masonry, Shuttering, Bar Bending & RCC Concreting Labor",
            total_bua, "sq ft", "masonry_rcc_labor",
            "specification_derived",
            f"Total Built-Up Area ({total_bua} sq ft) × labor rate",
            "Includes centering, shuttering, scaffolding, steel tying, concrete pouring and brick masonry labor."
        )

        add_line(
            "LBR-FLR-01", "labor",
            "Flooring Laying, Cutting, Bedding & Tile Grouting Labor",
            flooring["indoor_flooring_gross_sqft"], "sq ft", "flooring_laying_labor",
            "geometry_derived",
            f"Gross Indoor Tile Area ({flooring['indoor_flooring_gross_sqft']} sq ft) × tile labor rate",
            "Skilled tile masons for laser leveling, adhesive/cement bedding, and epoxy grouting."
        )

        add_line(
            "LBR-PNT-01", "labor",
            "Plaster Finishing, Wall Putty & Painting Labor",
            wall_data["total_plaster_area_sqft"], "sq ft", "painting_labor",
            "geometry_derived",
            f"Total plaster & ceiling area ({wall_data['total_plaster_area_sqft']} sq ft) × painting labor",
            "Surface preparation, putty sanding, primer and two finish coats."
        )

        # ── Cost Aggregation ──────────────────────────────────────────────
        materials_cost = 0.0
        labor_cost = 0.0
        openings_fixtures_cost = 0.0
        services_cost = 0.0

        for item in line_items:
            cat = item.category
            if cat in {"materials", "masonry", "structural_steel", "flooring", "finishes"}:
                materials_cost += item.amount
            elif cat == "labor":
                labor_cost += item.amount
            elif cat == "openings":
                openings_fixtures_cost += item.amount
            elif cat == "services":
                services_cost += item.amount
            else:
                materials_cost += item.amount

        materials_cost = round(materials_cost, 2)
        labor_cost = round(labor_cost, 2)
        openings_fixtures_cost = round(openings_fixtures_cost, 2)
        services_cost = round(services_cost, 2)

        subtotal = round(materials_cost + labor_cost + openings_fixtures_cost + services_cost, 2)

        # Contingency allowance: 5% of subtotal
        contingency_pct = float(self.custom_specs.get("contingency_percentage", 5.0))
        contingency_cost = round(subtotal * (contingency_pct / 100.0), 2)

        # Contractor overhead & profit: 10% of subtotal
        overhead_pct = float(self.custom_specs.get("contractor_overhead_percentage", 10.0))
        overhead_cost = round(subtotal * (overhead_pct / 100.0), 2)

        # Tax: Default 0.0% (GST on residential works contract varies by state & client composition)
        tax_pct = float(self.custom_specs.get("tax_percentage", 0.0))
        tax_cost = round((subtotal + contingency_cost + overhead_cost) * (tax_pct / 100.0), 2)

        grand_total = round(subtotal + contingency_cost + overhead_cost + tax_cost, 2)
        cost_per_sq_ft = round(grand_total / total_bua, 2)

        cost_summary = CostSummary(
            materials_cost=materials_cost,
            labor_cost=labor_cost,
            openings_and_fixtures_cost=openings_fixtures_cost,
            services_cost=services_cost,
            subtotal=subtotal,
            contingency_percentage=contingency_pct,
            contingency_cost=contingency_cost,
            contractor_overhead_percentage=overhead_pct,
            contractor_overhead_cost=overhead_cost,
            tax_percentage=tax_pct,
            tax_cost=tax_cost,
            grand_total=grand_total,
            cost_per_sq_ft=cost_per_sq_ft,
            cost_per_sq_ft_denominator=f"Total Constructed Built-Up Area ({total_bua} sq ft)"
        )

        # Assumptions and limitations
        assumptions_list = [
            f"Default Floor Height: {self.calculator.floor_height} ft floor-to-floor assumption.",
            f"Structural Steel: Estimated at provisional rate of {self.calculator.steel_factor_kg_sqft} kg/sq ft of built-up area. Subject to certified structural engineer's RCC design drawings & Bar Bending Schedule (BBS).",
            f"Concrete Mix: M20 grade (1:1.5:3) assumed for slabs, beams, columns, and foundations with standard dry volume conversion factor of 1.54.",
            f"Wall Construction: 9-inch exterior boundary walls and 4.5-inch interior partition walls with modular red clay bricks (13.5 bricks/cu ft with 5% handling wastage).",
            f"Plastering: 12-15mm cement-sand plaster (1:6 on walls, 1:4 on ceilings) across all exposed masonry surfaces.",
            f"Flooring: 7% cutting and edge wastage allowance included on net indoor usable floor area. Outdoor areas (balconies/terraces) calculated separately with 8% wastage.",
            "Soil & Foundation: Assumes standard hard morrum / soil condition with isolated footing depth of 5 ft. Rocky, loose black cotton soil or deep pile foundations will require structural revisions.",
            "Location Rates: Benchmark material & labor rates sourced for Hyderabad, Telangana (2026). Sourced as illustrative planning benchmarks; user editable for local quotations."
        ]

        disclaimer_text = (
            "NOTICE: This Construction Cost Estimate is generated algorithmically from architectural layout geometry "
            "and regional benchmark pricing. It serves as an architectural planning and budgeting guide. "
            "It does not replace a detailed structural engineering Bill of Quantities (BOQ), soil investigation report, "
            "or contractor site quotation. All rates and quantities can be customized by the user."
        )

        quantities_dict = {
            "total_built_up_area_sqft": total_bua,
            "total_indoor_room_area_sqft": area_schedule.total_indoor_room_area,
            "total_cement_bags": total_cement_bags,
            "total_sand_cuft": total_sand_cuft,
            "total_coarse_aggregate_cuft": total_coarse_agg_cuft,
            "total_steel_kg": total_steel_kg,
            "total_steel_tonnes": concrete_steel["steel_reinforcement_tonnes"],
            "total_bricks_count": total_bricks,
            "indoor_flooring_sqft": flooring["indoor_flooring_gross_sqft"],
            "total_plaster_sqft": wall_data["total_plaster_area_sqft"],
            "total_masonry_volume_cuft": wall_data["masonry_volume_cuft"],
            "net_wall_area_sqft": wall_data["net_wall_area_sqft"],
            "door_deductions_sqft": wall_data["door_deduction_sqft"],
            "window_deductions_sqft": wall_data["window_deduction_sqft"],
        }

        return EstimateResponse(
            estimate_id=str(uuid.uuid4()),
            project_id=self.project_id,
            floor_plan_id=self.floor_plan_id,
            created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            currency="INR",
            currency_symbol="₹",
            location_profile=self.rate_profile.location_name,
            area_schedule=area_schedule,
            quantities=quantities_dict,
            line_items=line_items,
            cost_summary=cost_summary,
            rates_snapshot=rates,
            assumptions_and_limitations=assumptions_list,
            disclaimer=disclaimer_text
        )

    @staticmethod
    def export_to_csv(estimate: EstimateResponse) -> str:
        """
        Exports estimate line items and summary to standard CSV text.
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Header info
        writer.writerow(["AI HOUSE PLANNING SYSTEM — CONSTRUCTION COST ESTIMATE"])
        writer.writerow(["Project ID", estimate.project_id])
        writer.writerow(["Floor Plan ID", estimate.floor_plan_id or "N/A"])
        writer.writerow(["Generated At", estimate.created_at])
        writer.writerow(["Location Profile", estimate.location_profile])
        writer.writerow(["Currency", f"{estimate.currency} ({estimate.currency_symbol})"])
        writer.writerow([])

        # Summary Block
        writer.writerow(["COST SUMMARY BREAKDOWN"])
        writer.writerow(["Metric / Category", "Amount (INR ₹)"])
        writer.writerow(["Total Constructed Built-Up Area", f"{estimate.cost_summary.cost_per_sq_ft_denominator}"])
        writer.writerow(["Cost Per Sq Ft", f"₹ {estimate.cost_summary.cost_per_sq_ft}"])
        writer.writerow(["Materials Cost", f"₹ {estimate.cost_summary.materials_cost}"])
        writer.writerow(["Civil & Finishing Labor Cost", f"₹ {estimate.cost_summary.labor_cost}"])
        writer.writerow(["Openings & Fixtures Cost", f"₹ {estimate.cost_summary.openings_and_fixtures_cost}"])
        writer.writerow(["Plumbing & Electrical Services", f"₹ {estimate.cost_summary.services_cost}"])
        writer.writerow(["Subtotal", f"₹ {estimate.cost_summary.subtotal}"])
        writer.writerow([f"Contingency ({estimate.cost_summary.contingency_percentage}%)", f"₹ {estimate.cost_summary.contingency_cost}"])
        writer.writerow([f"Contractor Overhead & Profit ({estimate.cost_summary.contractor_overhead_percentage}%)", f"₹ {estimate.cost_summary.contractor_overhead_cost}"])
        writer.writerow([f"Applicable Taxes ({estimate.cost_summary.tax_percentage}%)", f"₹ {estimate.cost_summary.tax_cost}"])
        writer.writerow(["GRAND TOTAL ESTIMATED COST", f"₹ {estimate.cost_summary.grand_total}"])
        writer.writerow([])

        # Detailed Line Items
        writer.writerow(["DETAILED MATERIAL & WORK QUANTITIES TABLE"])
        writer.writerow([
            "Item ID",
            "Category",
            "Item Description",
            "Quantity",
            "Unit",
            "Unit Rate (₹)",
            "Amount (₹)",
            "Classification",
            "Formula / Origin",
            "Assumptions"
        ])

        for item in estimate.line_items:
            writer.writerow([
                item.id,
                item.category,
                item.item_name,
                item.quantity,
                item.unit,
                item.unit_rate,
                item.amount,
                item.classification,
                item.formula,
                item.assumptions
            ])

        writer.writerow([])
        writer.writerow(["ESTIMATION ASSUMPTIONS & DISCLAIMER"])
        for ass in estimate.assumptions_and_limitations:
            writer.writerow(["Assumption", ass])
        writer.writerow(["Disclaimer", estimate.disclaimer])

        return output.getvalue()
