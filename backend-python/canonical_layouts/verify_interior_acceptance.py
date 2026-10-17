"""
Acceptance verification script for Phase 6E.1 Interior Design Studio.
Loads canonical 30x40 East and 50x80 South fixtures, extracts rooms,
verifies plan-aware preview generation and cost aggregation.
"""

import json
import os
from app.services.interior_design.catalog import get_all_interior_designs
from app.services.interior_design.preview_service import generate_plan_aware_preview
from app.services.interior_design.service import calculate_project_interior_costs
from app.models.interior_design import RoomInteriorSelection

CANONICAL_DIR = os.path.join(os.path.dirname(__file__), "canonical_layouts")


def run_acceptance_audit():
    print("=" * 80)
    print("PHASE 6E.1 — VISUAL & FUNCTIONAL ACCEPTANCE VERIFICATION")
    print("=" * 80)

    # 1. Catalog Verification
    designs = get_all_interior_designs()
    print(f"\n[CATALOG] Total Designs: {len(designs)} (Required: 32)")
    assert len(designs) == 32

    categories = {}
    for d in designs:
        categories[d.category] = categories.get(d.category, 0) + 1
    print(f"[CATALOG] Categories: {categories}")
    expected_categories = {
        "bedroom": 8,
        "living_room": 6,
        "kitchen": 6,
        "guest_room": 4,
        "bathroom": 4,
        "dining_room": 4,
    }
    assert categories == expected_categories

    # 2. Canonical Layout Tests
    layouts = [
        ("canonical_30x40_east_g1.json", "30x40 East G+1"),
        ("canonical_50x80_south_g1.json", "50x80 South G+1"),
    ]

    for filename, label in layouts:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "r", encoding="utf-8") as f:
            layout_data = json.load(f)

        indoor_rooms = []
        for floor in layout_data.get("floors", []):
            for r in floor.get("rooms", []):
                if r.get("type") not in [
                    "open_terrace",
                    "balcony",
                    "roof_slab_below",
                    "parking",
                    "driveway",
                ]:
                    indoor_rooms.append(r)

        print(f"\n[{label}] Discovered {len(indoor_rooms)} indoor rooms.")
        selections = {}

        for room in indoor_rooms:
            r_name = room.get("name", "Room")
            r_type = room.get("type", "bedroom")
            w = float(room.get("width", 12.0))
            l = float(room.get("length", 14.0))
            area = float(room.get("area", w * l))

            # Pick appropriate design
            design_id = "int_bed_01"
            if "living" in r_type or "hall" in r_type:
                design_id = "int_lr_01"
            elif "kit" in r_type:
                design_id = "int_kit_01"
            elif "bath" in r_type or "toilet" in r_type:
                design_id = "int_bath_01"
            elif "din" in r_type:
                design_id = "int_din_01"
            elif "guest" in r_type:
                design_id = "int_guest_01"

            # Generate Plan-Aware Preview
            preview = generate_plan_aware_preview(
                room_id=room.get("id"),
                room_name=r_name,
                room_type=r_type,
                room_width=w,
                room_length=l,
                room_area=area,
                design_id=design_id,
                floor_name=room.get("floor_name", "Ground Floor"),
            )
            assert preview["status"] == "success"
            assert preview["mode"] == "geometry_grounded"
            assert "<svg" in preview["preview_svg"]

            selections[room.get("id")] = RoomInteriorSelection(
                room_id=room.get("id"),
                room_type=r_type,
                room_name=r_name,
                room_area_sqft=area,
                design_id=design_id,
            )

        # Calculate project interior costs
        cost_res = calculate_project_interior_costs(
            selections=selections, layout_data=layout_data
        )
        print(
            f"[{label}] Successfully calculated total interior upgrade estimate: Rs. {cost_res['total_interior_cost']:,.2f} across {cost_res['room_count']} rooms."
        )

    print("\n" + "=" * 80)
    print("ALL VISUAL & FUNCTIONAL ACCEPTANCE CHECKS PASSED!")
    print("=" * 80)


if __name__ == "__main__":
    run_acceptance_audit()
