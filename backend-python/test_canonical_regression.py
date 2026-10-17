"""
CATEGORY A: CANONICAL REGRESSION TEST SUITE
=============================================
Strictly verifies the canonical, frozen LayoutData JSON records.
Never calls solve_layout() or runs fresh CP-SAT optimizations.
Verifies SHA-256 hashes, exact room schedules, disjointness,
structural cantilevers, slab decomposition, staircase alignment,
and regenerates all 6 architectural SVGs.
"""
import sys
import os
import hashlib
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.models.layout import LayoutData
from export_svg_test import export_all

CANONICAL_DIR = os.path.join(os.path.dirname(__file__), "canonical_layouts")
SVG_DIR = r"C:\Users\DELL\.gemini\antigravity\brain\35ff5483-d119-45be-a407-00f491b2c1fa"

CANONICAL_SPECS = {
    "canonical_30x40_east_g1.json": {
        "run_id": "CANONICAL-30X40-EAST-G1-20261016",
        "sha256": "93fe2d1737efac326161235586c828dbf073b6c396119824a11fc77715e1105d",
        "gf_slab_expected": 767.0,
        "ff_indoor_expected": 743.0,
        "ff_overlap_expected": 734.0,
        "ff_cantilever_expected": 9.0,
        "ff_outdoor_on_slab_expected": 33.0,
        "staircase_box": (19.0, 27.0, 8.0, 10.0),
        "gf_room_count": 6,
        "ff_room_count": 5
    },
    "canonical_50x80_south_g1.json": {
        "run_id": "CANONICAL-50X80-SOUTH-G1-20261016",
        "sha256": "46efc1c4e69fb8617007e120c497bef6fb3cef6034f4469cdca7d13074fd51d7",
        "gf_slab_expected": 1579.0,
        "ff_indoor_expected": 931.0,
        "ff_overlap_expected": 895.0,
        "ff_cantilever_expected": 36.0,
        "ff_outdoor_on_slab_expected": 684.0,
        "staircase_box": (15.0, 49.0, 10.0, 15.0),
        "gf_room_count": 7,
        "ff_room_count": 5
    }
}

def verify_canonical_file(filename, spec):
    print("\n" + "=" * 80)
    print(f"VERIFYING CANONICAL RECORD: {filename}")
    print(f"Expected Run ID : {spec['run_id']}")
    print(f"Expected SHA-256: {spec['sha256']}")
    print("=" * 80)

    fpath = os.path.join(CANONICAL_DIR, filename)
    assert os.path.exists(fpath), f"ERROR: Missing canonical file {fpath}"

    with open(fpath, "rb") as f:
        file_bytes = f.read()
    actual_hash = hashlib.sha256(file_bytes).hexdigest()
    assert actual_hash == spec["sha256"], f"FAILED: SHA-256 hash mismatch!\nExpected: {spec['sha256']}\nGot     : {actual_hash}"
    print(f">>> PASS 1: SHA-256 Content Hash verified ({actual_hash[:16]}...)")

    layout = LayoutData.model_validate_json(file_bytes.decode('utf-8'))
    actual_run_id = layout.metadata.get("canonical_run_id")
    assert actual_run_id == spec["run_id"], f"FAILED: Run ID mismatch! Expected {spec['run_id']}, got {actual_run_id}"
    print(f">>> PASS 2: Canonical Run ID verified ({actual_run_id})")

    # 1. Ground Floor Indoor Rooms
    gf = layout.floors[0]
    gf_indoor = [r for r in gf.rooms if getattr(r, 'space_category', '') != 'outdoor']
    assert len(gf_indoor) == spec["gf_room_count"], f"Expected {spec['gf_room_count']} GF rooms, got {len(gf_indoor)}"
    gf_boxes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in gf_indoor]
    gf_slab = unary_union(gf_boxes)
    gf_sum = sum(r.width * r.length for r in gf_indoor)

    assert abs(gf_sum - gf_slab.area) < 0.001, f"GF rooms overlap! Sum={gf_sum}, Union={gf_slab.area}"
    assert abs(gf_slab.area - spec["gf_slab_expected"]) < 0.01, f"Expected GF slab {spec['gf_slab_expected']}, got {gf_slab.area}"
    print(f">>> PASS 3: Ground Floor indoor slab verified ({gf_slab.area:.1f} sq ft, {len(gf_indoor)} rooms, strictly disjoint)")

    # 2. First Floor Indoor Rooms
    ff = layout.floors[1]
    ff_indoor = [r for r in ff.rooms if getattr(r, 'space_category', '') != 'outdoor']
    assert len(ff_indoor) == spec["ff_room_count"], f"Expected {spec['ff_room_count']} FF rooms, got {len(ff_indoor)}"
    ff_boxes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in ff_indoor]
    ff_indoor_poly = unary_union(ff_boxes)
    ff_sum = sum(r.width * r.length for r in ff_indoor)

    assert abs(ff_sum - ff_indoor_poly.area) < 0.001, f"FF rooms overlap! Sum={ff_sum}, Union={ff_indoor_poly.area}"
    assert abs(ff_indoor_poly.area - spec["ff_indoor_expected"]) < 0.01, f"Expected FF indoor {spec['ff_indoor_expected']}, got {ff_indoor_poly.area}"
    print(f">>> PASS 4: First Floor indoor area verified ({ff_indoor_poly.area:.1f} sq ft, {len(ff_indoor)} rooms, strictly disjoint)")

    # 3. Staircase Alignment
    gf_stair = next(r for r in gf_indoor if r.type == "staircase")
    ff_stair = next(r for r in ff_indoor if r.type == "staircase")
    sx, sy, sw, sl = spec["staircase_box"]
    assert (gf_stair.x, gf_stair.y, gf_stair.width, gf_stair.length) == (sx, sy, sw, sl), f"GF stair misaligned: {(gf_stair.x, gf_stair.y, gf_stair.width, gf_stair.length)}"
    assert (ff_stair.x, ff_stair.y, ff_stair.width, ff_stair.length) == (sx, sy, sw, sl), f"FF stair misaligned: {(ff_stair.x, ff_stair.y, ff_stair.width, ff_stair.length)}"
    print(f">>> PASS 5: Staircase vertical alignment verified at ({sx}, {sy}), size {sw}x{sl} ft")

    # 4. Containment, Overlap & Cantilever
    ff_on_gf = gf_slab.intersection(ff_indoor_poly).area
    ff_cantilever = ff_indoor_poly.difference(gf_slab).area

    assert abs(ff_on_gf - spec["ff_overlap_expected"]) < 0.01, f"Expected FF on GF overlap {spec['ff_overlap_expected']}, got {ff_on_gf}"
    assert abs(ff_cantilever - spec["ff_cantilever_expected"]) < 0.01, f"Expected cantilever {spec['ff_cantilever_expected']}, got {ff_cantilever}"
    print(f">>> PASS 6: Overlap ({ff_on_gf:.1f} sq ft) and Cantilever ({ff_cantilever:.1f} sq ft) verified against expected")

    # 5. Upper Outdoor Slab Decomposition & Irregular Polygons
    ff_outdoor = getattr(ff, "outdoor_areas", [])
    ff_out_polys = []
    for o in ff_outdoor:
        if o.polygon and len(o.polygon) > 2:
            coords = [(p.x, p.y) for p in o.polygon]
            g = Polygon(coords)
            assert abs(g.area - o.area) < 0.01, f"Polygon area {g.area} != reported {o.area}"
        else:
            g = box(o.x, o.y, o.x + o.width, o.y + o.length)
            assert abs(g.area - o.area) < 0.01, f"Rect area {g.area} != reported {o.area}"
        # Overlap with indoor
        inter_in = g.intersection(ff_indoor_poly).area
        assert inter_in < 0.001, f"Outdoor area {o.label} overlaps indoor rooms by {inter_in} sq ft!"
        ff_out_polys.append(g)

    # Disjointness between outdoor areas
    for i in range(len(ff_out_polys)):
        for j in range(i + 1, len(ff_out_polys)):
            inter_out = ff_out_polys[i].intersection(ff_out_polys[j]).area
            assert inter_out < 0.001, f"Outdoor areas {ff_outdoor[i].label} and {ff_outdoor[j].label} overlap by {inter_out} sq ft!"

    upper_out_on_gf = sum(gf_slab.intersection(p).area for p in ff_out_polys)
    assert abs(upper_out_on_gf - spec["ff_outdoor_on_slab_expected"]) < 0.01, f"Expected outdoor on slab {spec['ff_outdoor_on_slab_expected']}, got {upper_out_on_gf}"
    print(f">>> PASS 7: Upper outdoor areas verified ({upper_out_on_gf:.1f} sq ft, all disjoint from indoor rooms)")

    # 6. Exact Physical Slab Partition Proof
    reconciled_sum = ff_on_gf + upper_out_on_gf
    discrepancy = abs(gf_slab.area - reconciled_sum)
    assert discrepancy < 0.001, f"Slab discrepancy {discrepancy} exceeds 0.001 sq ft!"
    print(f">>> PASS 8: Exact Physical Slab Partition: GF Slab ({gf_slab.area:.1f}) = Overlap ({ff_on_gf:.1f}) + Outdoor ({upper_out_on_gf:.1f}), Error = {discrepancy:.4f} sq ft")

def test_canonical_svg_exports():
    print("\n" + "=" * 80)
    print("VERIFYING ARCHITECTURAL SVG EXPORTS FROM CANONICAL RECORDS")
    print("=" * 80)

    # Regenerate all 6 SVGs from canonical files
    export_all()

    expected_files = [
        ("floorplan_30x40_ground.svg", "CANONICAL-30X40-EAST-G1-20261016", "GROUND FLOOR", "ROOMS ON LEVEL: 6"),
        ("floorplan_30x40_first.svg",  "CANONICAL-30X40-EAST-G1-20261016", "FIRST FLOOR",  "ROOMS ON LEVEL: 5"),
        ("floorplan_30x40_site.svg",   "CANONICAL-30X40-EAST-G1-20261016", "SITE PLAN",    "EAST FACING"),
        ("floorplan_50x80_ground.svg", "CANONICAL-50X80-SOUTH-G1-20261016", "GROUND FLOOR", "ROOMS ON LEVEL: 7"),
        ("floorplan_50x80_first.svg",  "CANONICAL-50X80-SOUTH-G1-20261016", "FIRST FLOOR",  "ROOMS ON LEVEL: 5"),
        ("floorplan_50x80_site.svg",   "CANONICAL-50X80-SOUTH-G1-20261016", "SITE PLAN",    "SOUTH FACING"),
    ]

    for fname, expected_run, expected_sheet, expected_feature in expected_files:
        fpath = os.path.join(SVG_DIR, fname)
        assert os.path.exists(fpath), f"Missing SVG export: {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            svg_text = f.read()

        assert len(svg_text) > 1000, f"SVG file {fname} is suspiciously small ({len(svg_text)} bytes)"
        assert expected_run in svg_text, f"Run ID {expected_run} not found in {fname}"
        assert expected_sheet in svg_text, f"Sheet title {expected_sheet} not found in {fname}"
        assert expected_feature in svg_text, f"Feature {expected_feature} not found in {fname}"
        assert "<polygon" in svg_text, f"Expected <polygon> tags for irregular boundaries in {fname}"

        print(f">>> PASS: Verified {fname} (Run ID: {expected_run}, Sheet: {expected_sheet}, Tags: <polygon>)")

if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("STARTING CATEGORY A: CANONICAL REGRESSION TESTS")
    print("#" * 80)

    for filename, spec in CANONICAL_SPECS.items():
        verify_canonical_file(filename, spec)

    test_canonical_svg_exports()

    print("\n" + "=" * 80)
    print("ALL CANONICAL REGRESSION TESTS PASSED WITH 0.00 SQ FT DISCREPANCY!")
    print("=" * 80)
