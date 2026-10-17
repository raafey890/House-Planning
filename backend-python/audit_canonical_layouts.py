import sys
import os
import json
import hashlib
from shapely.geometry import box, Polygon, MultiPolygon
from shapely.ops import unary_union

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.models.layout import LayoutData

CANONICAL_DIR = os.path.join(os.path.dirname(__file__), "canonical_layouts")

def audit_canonical(file_path):
    print("=" * 80)
    filename = os.path.basename(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    sha256 = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
    layout = LayoutData.model_validate_json(raw_text)

    run_id = layout.metadata.get("canonical_run_id", "UNKNOWN")
    print(f"CANONICAL LAYOUT AUDIT: {filename}")
    print(f"Run ID  : {run_id}")
    print(f"SHA-256 : {sha256}")
    print(f"Plot    : {layout.plot.width} × {layout.plot.length} ft, Facing: {layout.plot.facing.upper()}")
    print(f"Setbacks: {layout.plot.setbacks}")
    print(f"Building Footprint BBox: {layout.plot.building_footprint['width']} × {layout.plot.building_footprint['length']} ft at ({layout.plot.building_footprint['x']}, {layout.plot.building_footprint['y']}), BBox Area = {layout.plot.building_footprint['width']*layout.plot.building_footprint['length']:.1f} sq ft")
    print("=" * 80)

    # 1. Ground floor indoor
    gf = layout.floors[0]
    gf_indoor = [r for r in gf.rooms if getattr(r, 'space_category', '') != 'outdoor']
    gf_indoor_boxes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in gf_indoor]
    gf_slab = unary_union(gf_indoor_boxes)
    gf_sum = sum(r.width * r.length for r in gf_indoor)

    print(f"\n[GROUND FLOOR (Floor 0)]: {len(gf_indoor)} Indoor Rooms")
    print(f"  Sum of individual room areas : {gf_sum:.1f} sq ft")
    print(f"  Unary union of room polygons : {gf_slab.area:.1f} sq ft")
    print(f"  Strictly disjoint check      : {abs(gf_sum - gf_slab.area) < 0.001}")
    for r in gf_indoor:
        print(f"    - {r.label:18s} ({r.type:14s}): {r.width:4.1f} × {r.length:4.1f} ft at ({r.x:4.1f}, {r.y:4.1f}), area = {r.width*r.length:5.1f} sq ft")

    # Ground floor outdoor
    gf_outdoor = getattr(gf, "outdoor_areas", [])
    print(f"\n[GROUND FLOOR OUTDOOR]: {len(gf_outdoor)} Outdoor Areas")
    for o in gf_outdoor:
        if o.polygon and len(o.polygon) > 2:
            coords = [(p.x, p.y) for p in o.polygon]
            g = Polygon(coords)
            g_type = f"irregular polygon ({len(coords)} vertices)"
        else:
            g = box(o.x, o.y, o.x + o.width, o.y + o.length)
            g_type = "rectangle (4 vertices)"
        bbox_area = o.width * o.length
        overlap_gf_in = g.intersection(gf_slab).area
        print(f"    - {o.label:18s} ({o.type:10s}):")
        print(f"        Geometry Type     : {g_type}")
        print(f"        BBox [x,y,w,l]    : ({o.x:.1f}, {o.y:.1f}, {o.width:.1f}, {o.length:.1f}) ft -> bbox area = {bbox_area:.1f} sq ft")
        print(f"        Actual Poly Area  : {g.area:.1f} sq ft (Reported: {o.area:.1f} sq ft)")
        print(f"        Overlap w/ GF In  : {overlap_gf_in:.2f} sq ft ({'ZERO OVERLAP' if overlap_gf_in < 0.01 else 'OVERLAPS!'})")
        if o.polygon and len(o.polygon) > 2:
            pts_str = ", ".join([f"({p.x},{p.y})" for p in o.polygon])
            print(f"        Polygon Vertices  : [{pts_str}]")

    # 2. First floor indoor
    ff = layout.floors[1]
    ff_indoor = [r for r in ff.rooms if getattr(r, 'space_category', '') != 'outdoor']
    ff_indoor_boxes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in ff_indoor]
    ff_indoor_poly = unary_union(ff_indoor_boxes)
    ff_sum = sum(r.width * r.length for r in ff_indoor)

    print(f"\n[FIRST FLOOR (Floor 1)]: {len(ff_indoor)} Indoor Rooms")
    print(f"  Sum of individual room areas : {ff_sum:.1f} sq ft")
    print(f"  Unary union of room polygons : {ff_indoor_poly.area:.1f} sq ft")
    print(f"  Strictly disjoint check      : {abs(ff_sum - ff_indoor_poly.area) < 0.001}")
    for r in ff_indoor:
        print(f"    - {r.label:18s} ({r.type:14s}): {r.width:4.1f} × {r.length:4.1f} ft at ({r.x:4.1f}, {r.y:4.1f}), area = {r.width*r.length:5.1f} sq ft")

    # First floor outdoor
    ff_outdoor = getattr(ff, "outdoor_areas", [])
    print(f"\n[FIRST FLOOR OUTDOOR]: {len(ff_outdoor)} Outdoor Areas")
    ff_out_polys = []
    for o in ff_outdoor:
        if o.polygon and len(o.polygon) > 2:
            coords = [(p.x, p.y) for p in o.polygon]
            g = Polygon(coords)
            g_type = f"irregular polygon ({len(coords)} vertices)"
        else:
            g = box(o.x, o.y, o.x + o.width, o.y + o.length)
            g_type = "rectangle (4 vertices)"
        ff_out_polys.append(g)
        bbox_area = o.width * o.length
        overlap_ff_in = g.intersection(ff_indoor_poly).area
        print(f"    - {o.label:18s} ({o.type:10s}):")
        print(f"        Geometry Type     : {g_type}")
        print(f"        BBox [x,y,w,l]    : ({o.x:.1f}, {o.y:.1f}, {o.width:.1f}, {o.length:.1f}) ft -> bbox area = {bbox_area:.1f} sq ft")
        print(f"        Actual Poly Area  : {g.area:.1f} sq ft (Reported: {o.area:.1f} sq ft)")
        print(f"        Overlap w/ FF In  : {overlap_ff_in:.2f} sq ft ({'ZERO OVERLAP' if overlap_ff_in < 0.01 else 'OVERLAPS!'})")
        if o.polygon and len(o.polygon) > 2:
            pts_str = ", ".join([f"({p.x},{p.y})" for p in o.polygon])
            print(f"        Polygon Vertices  : [{pts_str}]")

    # Pairwise outdoor overlap
    has_out_overlap = False
    for i in range(len(ff_out_polys)):
        for j in range(i + 1, len(ff_out_polys)):
            inter = ff_out_polys[i].intersection(ff_out_polys[j]).area
            if inter > 0.01:
                print(f"  WARNING: Outdoor overlap between {ff_outdoor[i].label} and {ff_outdoor[j].label}: {inter:.2f} sq ft")
                has_out_overlap = True
    if not has_out_overlap:
        print("  Upper outdoor pairwise overlap: NONE (strictly disjoint)")

    # 3. Slab and Containment Decomposition
    ff_in_on_gf = gf_slab.intersection(ff_indoor_poly).area
    ff_in_outside_gf = ff_indoor_poly.difference(gf_slab).area
    uncovered_gf_slab = gf_slab.difference(ff_indoor_poly)
    upper_out_union = unary_union(ff_out_polys) if ff_out_polys else Polygon()
    upper_out_on_gf = gf_slab.intersection(upper_out_union).area

    print("\n" + "=" * 50)
    print("SLAB RECONCILIATION & CONTAINMENT DECOMPOSITION")
    print("=" * 50)
    print(f"1. Ground Floor Slab (Constructed Footprint) : {gf_slab.area:.1f} sq ft")
    print(f"2. First Floor Indoor Total Area             : {ff_indoor_poly.area:.1f} sq ft")
    print(f"   a. FF Indoor on GF Slab (Intersection)    : {ff_in_on_gf:.1f} sq ft ({ff_in_on_gf/gf_slab.area*100:.1f}% of GF slab)")
    print(f"   b. FF Indoor outside GF Slab (Cantilever) : {ff_in_outside_gf:.1f} sq ft")
    print(f"3. Uncovered GF Slab (Actual Open Slab)      : {uncovered_gf_slab.area:.1f} sq ft")
    print(f"4. First Floor Outdoor Total Area            : {upper_out_union.area:.1f} sq ft")
    print(f"   a. FF Outdoor on GF Slab                  : {upper_out_on_gf:.1f} sq ft")
    print(f"5. Total Accounted on GF Slab (2a + 4a)      : {ff_in_on_gf + upper_out_on_gf:.1f} sq ft")
    print(f"6. Discrepancy against GF Slab (1 - 5)       : {abs(gf_slab.area - (ff_in_on_gf + upper_out_on_gf)):.2f} sq ft")
    assert abs(gf_slab.area - (ff_in_on_gf + upper_out_on_gf)) < 0.01, "Slab discrepancy exceeds 0.01 sq ft!"
    print(">>> EXACT RECONCILIATION PASSED: Discrepancy = 0.00 sq ft.")

if __name__ == "__main__":
    audit_canonical(os.path.join(CANONICAL_DIR, "canonical_30x40_east_g1.json"))
    audit_canonical(os.path.join(CANONICAL_DIR, "canonical_50x80_south_g1.json"))
