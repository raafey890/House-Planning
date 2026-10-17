"""
Render SVG for visual inspection
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from test_full_quality_pipeline import res_50x80, res_30x40

def layout_to_svg(layout_data, floor_lvl=0):
    plot = layout_data.plot
    floor = next((f for f in layout_data.floors if f.level == floor_lvl), layout_data.floors[0])
    pw, pl = plot.width, plot.length
    pad = 4.0

    svg = [f'<svg viewBox="{-pad} {-pad-1} {pw+pad*2+1.5} {pl+pad*2+1}" width="800" height="1100" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<rect x="0" y="0" width="{}" height="{}" fill="#e8e4dc" stroke="#5a6a5a" stroke-width="0.3" stroke-dasharray="1.2 0.6"/>'.format(pw, pl))

    # Outdoor areas (yards/gardens)
    for r in floor.rooms:
        if r.space_category == 'outdoor' or r.type in ['garden', 'yard', 'terrace']:
            col = '#d8ecd8' if 'garden' in r.type else '#edf5ed'
            if hasattr(r, 'polygon') and r.polygon:
                pts = " ".join(f"{p.x},{p.y}" for p in r.polygon)
                svg.append(f'<polygon points="{pts}" fill="{col}" stroke="#7a9a7a" stroke-width="0.2"/>')
            else:
                svg.append(f'<rect x="{r.x}" y="{r.y}" width="{r.width}" height="{r.length}" fill="{col}" stroke="#7a9a7a" stroke-width="0.2"/>')
            svg.append(f'<text x="{r.x+r.width/2}" y="{r.y+r.length/2}" font-size="1.2" font-family="sans-serif" text-anchor="middle" fill="#3a6a3a">{r.label}</text>')

    # Building footprint
    fp = plot.building_footprint or {}
    if fp:
        svg.append(f'<rect x="{fp.get("x",0)}" y="{fp.get("y",0)}" width="{fp.get("width",0)}" height="{fp.get("length",0)}" fill="none" stroke="#2c3e50" stroke-width="0.4" stroke-dasharray="0.8 0.4"/>')

    # Indoor rooms
    ROOM_COLORS = {
        "living_room": "#fcfcfc", "bedroom": "#f8f8f8", "master_bedroom": "#f4f4f4",
        "kitchen": "#fafafa", "bathroom": "#f0f0f0", "dining_room": "#fdfdfd",
        "pooja_room": "#fcfcfc", "study_room": "#f5f5f5", "foyer": "#f0f5f0",
        "staircase": "#f0f0f0", "corridor": "#ffffff"
    }

    for r in floor.rooms:
        if r.space_category != 'outdoor' and r.type not in ['garden', 'yard', 'terrace']:
            col = ROOM_COLORS.get(r.type, "#fbfbfb")
            svg.append(f'<rect x="{r.x}" y="{r.y}" width="{r.width}" height="{r.length}" fill="{col}" stroke="#333" stroke-width="0.25"/>')
            svg.append(f'<text x="{r.x+r.width/2}" y="{r.y+r.length/2-0.5}" font-size="1.0" font-family="sans-serif" font-weight="bold" text-anchor="middle" fill="#1a2620">{r.label.upper()}</text>')
            svg.append(f'<text x="{r.x+r.width/2}" y="{r.y+r.length/2+0.8}" font-size="0.8" font-family="sans-serif" text-anchor="middle" fill="#555">{r.width:.0f}′ × {r.length:.0f}′</text>')

    # Walls
    for w in floor.walls:
        svg.append(f'<line x1="{w.start.x}" y1="{w.start.y}" x2="{w.end.x}" y2="{w.end.y}" stroke="#222" stroke-width="0.4"/>')

    # Gates
    for g in plot.gates or []:
        svg.append(f'<rect x="{g["position"]["x"]-g["width"]/2}" y="{g["position"]["y"]-0.5}" width="{g["width"]}" height="1.0" fill="#4a7a5a"/>')

    svg.append('</svg>')
    return "\n".join(svg)

svg_gf = layout_to_svg(res_50x80["layout_data"], floor_lvl=0)
with open("test_50x80_gf.svg", "w", encoding="utf-8") as f:
    f.write(svg_gf)

svg_ff = layout_to_svg(res_50x80["layout_data"], floor_lvl=1)
with open("test_50x80_ff.svg", "w", encoding="utf-8") as f:
    f.write(svg_ff)

print("Saved test_50x80_gf.svg and test_50x80_ff.svg")
