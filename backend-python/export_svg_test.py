"""
SVG Exporter — Authentic AutoCAD Engineering Blueprint Styling.
Reflects professional Indian architectural working drawing standards matching reference blueprints:
- Structural RCC Columns with Numbered Tags (01), (02), (03)...
- Double-Line Walls with Clean Cutouts at Openings
- Built-in Architectural Fixtures:
    * Kitchen Cooking Counter ('KIT./OTTA 0.60M') with Stainless Steel Sink
    * Bathrooms/Toilets with Water Closet ('W.C.') & Wash Basin ('W.B.')
    * Bedrooms with Built-in Wardrobes ('C.B.') & Louver Slat Lines
    * Store Room Overhead Storage Loft ('LOFT')
- Windows with Exterior RCC Chhajja (Sunshade Projection) & Code Tags (W, W1, V)
- Doors with Architectural Code Tags (D, D1, D2)
- Numbered Dog-Legged Staircase with Individual Tread Numbers 1-17, Landing & UP/DN Arrows
- Entrance Veranda with Steps, Level Marker (+0.60M ROAD LVL) & Stippled Raised Lawn
- Road Element with Double Arrow (<==== ROAD ====>) & 0.0 M ROAD LVL
- Side-by-Side Blueprint Sheet Mode ('both') matching reference CAD drawing
"""
import os
import sys
import json
import math

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.models.layout import LayoutData

ROOM_COLORS = {
    "living_room":    {"fill": "#ffffff", "stroke": "#0f172a"},
    "drawing_room":   {"fill": "#ffffff", "stroke": "#0f172a"},
    "bedroom":        {"fill": "#ffffff", "stroke": "#0f172a"},
    "master_bedroom": {"fill": "#ffffff", "stroke": "#0f172a"},
    "guest_room":     {"fill": "#ffffff", "stroke": "#0f172a"},
    "kitchen":        {"fill": "#ffffff", "stroke": "#0f172a"},
    "dining_room":    {"fill": "#ffffff", "stroke": "#0f172a"},
    "bathroom":       {"fill": "#f8fafc", "stroke": "#0f172a"},
    "toilet":         {"fill": "#f8fafc", "stroke": "#0f172a"},
    "foyer":          {"fill": "#ffffff", "stroke": "#0f172a"},
    "pooja_room":     {"fill": "#ffffff", "stroke": "#0f172a"},
    "pooja":          {"fill": "#ffffff", "stroke": "#0f172a"},
    "study_room":     {"fill": "#ffffff", "stroke": "#0f172a"},
    "study":          {"fill": "#ffffff", "stroke": "#0f172a"},
    "staircase":      {"fill": "#f8fafc", "stroke": "#0f172a"},
    "stairs":         {"fill": "#f8fafc", "stroke": "#0f172a"},
    "corridor":       {"fill": "#ffffff", "stroke": "#334155"},
    "hallway":        {"fill": "#ffffff", "stroke": "#334155"},
    "utility_room":   {"fill": "#f8fafc", "stroke": "#334155"},
    "utility":        {"fill": "#f8fafc", "stroke": "#334155"},
    "store_room":     {"fill": "#f8fafc", "stroke": "#334155"},
    "store":          {"fill": "#f8fafc", "stroke": "#334155"},
    "balcony":        {"fill": "#ffffff", "stroke": "#0f172a"},
    "terrace":        {"fill": "#ffffff", "stroke": "#0f172a"},
    "parking":        {"fill": "#f8fafc", "stroke": "#0f172a"},
    "garage":         {"fill": "#f8fafc", "stroke": "#0f172a"},
    "default":        {"fill": "#ffffff", "stroke": "#0f172a"}
}

def format_ft_in(val: float) -> str:
    if val is None:
        return ""
    rounded = round(val * 10) / 10
    ft = math.floor(rounded)
    inch = round((rounded - ft) * 12)
    return f"{ft}'-{inch}\"" if inch > 0 else f"{ft}'-0\""

def format_meters(val: float) -> str:
    if val is None:
        return ""
    return f"{(val * 0.3048):.2f}"

def render_columns_svg(indoor_rooms, pw: float, pl: float) -> list:
    """Generate structural RCC columns and numbered bubble tags."""
    if not indoor_rooms:
        return []
    pts = []
    for r in indoor_rooms:
        rx, ry, rw, rl = r.x, r.y, r.width, r.length
        pts.extend([(rx, ry), (rx + rw, ry), (rx, ry + rl), (rx + rw, ry + rl)])

    clusters = []
    for p in pts:
        matched = False
        for c in clusters:
            if math.hypot(c[0] - p[0], c[1] - p[1]) < 1.4:
                matched = True
                break
        if not matched:
            clusters.append(p)

    final_cols = list(clusters)
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            c1, c2 = clusters[i], clusters[j]
            if abs(c1[1] - c2[1]) < 0.6 and 16.0 <= abs(c1[0] - c2[0]) <= 24.0:
                mid_x = (c1[0] + c2[0]) / 2
                if not any(math.hypot(c[0] - mid_x, c[1] - c1[1]) < 4.0 for c in final_cols):
                    final_cols.append((mid_x, c1[1]))

    def sort_key(c):
        return (round(c[1] / 2.0) * 2.0, c[0])
    final_cols.sort(key=sort_key)

    out = ['<g class="structural-columns">']
    col_w = 0.85
    col_l = 1.35
    for idx, col in enumerate(final_cols):
        cx, cy = col[0], col[1]
        tag_num = f"{idx + 1:02d}"
        tag_offset = 1.4
        is_left = cx < pw * 0.4
        is_right = cx > pw * 0.6
        is_top = cy < pl * 0.4

        tag_x = cx + (-tag_offset if is_left else tag_offset if is_right else 0)
        tag_y = cy + (-tag_offset if is_top else tag_offset)
        if not is_left and not is_right:
            tag_x += 1.2

        out.append(f'  <rect x="{cx - col_w/2}" y="{cy - col_l/2}" width="{col_w}" height="{col_l}" fill="#0f172a" stroke="#ffffff" stroke-width="0.06"/>')
        out.append(f'  <line x1="{cx}" y1="{cy}" x2="{tag_x}" y2="{tag_y}" stroke="#0f172a" stroke-width="0.05" stroke-dasharray="0.2 0.15"/>')
        out.append(f'  <circle cx="{tag_x}" cy="{tag_y}" r="0.72" fill="#ffffff" stroke="#0f172a" stroke-width="0.09"/>')
        out.append(f'  <text x="{tag_x}" y="{tag_y + 0.05}" text-anchor="middle" dominant-baseline="middle" font-size="0.42" font-weight="bold" fill="#0f172a" font-family="\'JetBrains Mono\', monospace">({tag_num})</text>')
    out.append('</g>')
    return out

def render_fixtures_svg(room) -> list:
    """Render built-in CAD furniture and fixtures for a room."""
    rx, ry, rw, rl = room.x, room.y, room.width, room.length
    rtype = room.type.lower()
    out = []

    if "kitchen" in rtype:
        c_depth = min(2.0, rl * 0.28)
        c_len = min(rw - 1.0, 10.0)
        sink_w, sink_l = 2.2, 1.4
        sink_x, sink_y = rx + 1.2, ry + 0.3
        out.append(f'<g class="kitchen-fixtures" pointer-events="none">')
        out.append(f'  <rect x="{rx}" y="{ry}" width="{c_len}" height="{c_depth}" fill="#f8fafc" stroke="#334155" stroke-width="0.12"/>')
        out.append(f'  <line x1="{rx}" y1="{ry + c_depth - 0.2}" x2="{rx + c_len}" y2="{ry + c_depth - 0.2}" stroke="#94a3b8" stroke-width="0.06"/>')
        out.append(f'  <rect x="{sink_x}" y="{sink_y}" width="{sink_w}" height="{sink_l}" fill="#ffffff" stroke="#0f172a" stroke-width="0.10" rx="0.2"/>')
        out.append(f'  <rect x="{sink_x + 0.2}" y="{sink_y + 0.2}" width="{sink_w - 0.4}" height="{sink_l - 0.4}" fill="#f1f5f9" stroke="#0284c7" stroke-width="0.08" rx="0.15"/>')
        out.append(f'  <circle cx="{sink_x + sink_w/2}" cy="{sink_y + sink_l/2}" r="0.14" fill="#0f172a"/>')
        out.append(f'  <circle cx="{sink_x + sink_w/2}" cy="{sink_y + 0.25}" r="0.09" fill="#0f172a"/>')
        out.append(f'  <line x1="{sink_x + sink_w/2}" y1="{sink_y + 0.25}" x2="{sink_x + sink_w/2}" y2="{sink_y + 0.55}" stroke="#0f172a" stroke-width="0.08"/>')
        out.append(f'  <text x="{rx + c_len/2 + 1.5}" y="{ry + c_depth/2}" font-size="0.42" font-weight="bold" fill="#475569" font-family="\'JetBrains Mono\', monospace">KIT. / OTTA (0.60M)</text>')
        out.append('</g>')

    elif "bath" in rtype or "toilet" in rtype:
        wc_x = rx + min(1.2, rw * 0.25)
        wc_y = ry + 0.35
        wb_x = rx + rw - 1.8
        wb_y = ry + 0.35
        out.append(f'<g class="bathroom-fixtures" pointer-events="none">')
        # W.C.
        out.append(f'  <g transform="translate({wc_x}, {wc_y})">')
        out.append(f'    <rect x="-0.8" y="0" width="1.6" height="0.65" fill="#ffffff" stroke="#0f172a" stroke-width="0.10" rx="0.1"/>')
        out.append(f'    <ellipse cx="0" cy="1.45" rx="0.58" ry="0.78" fill="#ffffff" stroke="#0f172a" stroke-width="0.10"/>')
        out.append(f'    <ellipse cx="0" cy="1.48" rx="0.38" ry="0.54" fill="#f1f5f9" stroke="#64748b" stroke-width="0.06"/>')
        out.append(f'    <text x="0" y="2.6" font-size="0.42" font-weight="bold" fill="#0f172a" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">W.C.</text>')
        out.append('  </g>')
        # W.B.
        out.append(f'  <g transform="translate({wb_x}, {wb_y})">')
        out.append(f'    <path d="M -0.7 0 L 0.7 0 Q 0.7 1.1 0 1.2 Q -0.7 1.1 -0.7 0 Z" fill="#ffffff" stroke="#0f172a" stroke-width="0.10"/>')
        out.append(f'    <circle cx="0" cy="0.2" r="0.08" fill="#0f172a"/>')
        out.append(f'    <circle cx="0" cy="0.65" r="0.10" fill="#64748b"/>')
        out.append(f'    <text x="0" y="1.7" font-size="0.42" font-weight="bold" fill="#0f172a" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">W.B.</text>')
        out.append('  </g>')
        if rl >= 6.0:
            out.append(f'  <line x1="{rx + 0.3}" y1="{ry + rl - 2.8}" x2="{rx + rw - 0.3}" y2="{ry + rl - 2.8}" stroke="#94a3b8" stroke-width="0.10" stroke-dasharray="0.3 0.2"/>')
        out.append('</g>')

    elif "bedroom" in rtype:
        cb_d = min(2.0, rl * 0.2)
        cb_w = min(5.5, rw * 0.45)
        cb_x = rx + rw - cb_w - 0.4
        cb_y = ry + 0.4
        out.append(f'<g class="bedroom-fixtures" pointer-events="none">')
        out.append(f'  <rect x="{cb_x}" y="{cb_y}" width="{cb_w}" height="{cb_d}" fill="#f8fafc" stroke="#0f172a" stroke-width="0.14"/>')
        sx = cb_x + 0.35
        while sx < cb_x + cb_w - 0.2:
            out.append(f'  <line x1="{sx}" y1="{cb_y}" x2="{sx}" y2="{cb_y + cb_d}" stroke="#94a3b8" stroke-width="0.06"/>')
            sx += 0.35
        out.append(f'  <rect x="{cb_x + cb_w/2 - 0.9}" y="{cb_y + cb_d/2 - 0.32}" width="1.8" height="0.64" fill="#ffffff" stroke="#0f172a" stroke-width="0.08"/>')
        out.append(f'  <text x="{cb_x + cb_w/2}" y="{cb_y + cb_d/2 + 0.04}" font-size="0.42" font-weight="bold" fill="#0f172a" text-anchor="middle" dominant-baseline="middle" font-family="\'JetBrains Mono\', monospace">C.B.</text>')
        out.append('</g>')

    elif "store" in rtype or "utility" in rtype:
        out.append(f'<g class="store-fixtures" pointer-events="none">')
        loft_y = ry + min(2.4, rl * 0.4)
        out.append(f'  <line x1="{rx}" y1="{loft_y}" x2="{rx + rw}" y2="{loft_y}" stroke="#475569" stroke-width="0.12" stroke-dasharray="0.4 0.2"/>')
        out.append(f'  <text x="{rx + rw/2}" y="{ry + 1.2}" font-size="0.45" font-weight="bold" fill="#64748b" text-anchor="middle" dominant-baseline="middle" font-family="\'JetBrains Mono\', monospace">LOFT / POTHMALA</text>')
        out.append('</g>')

    elif "pooja" in rtype:
        pw_m = min(rw - 1.2, 4.0)
        pl_m = min(rl - 1.2, 1.8)
        px_m = rx + (rw - pw_m) / 2
        py_m = ry + 0.4
        out.append(f'<g class="pooja-fixtures" pointer-events="none">')
        out.append(f'  <rect x="{px_m}" y="{py_m}" width="{pw_m}" height="{pl_m}" fill="#fefce8" stroke="#854d0e" stroke-width="0.12" rx="0.2"/>')
        out.append(f'  <rect x="{px_m + 0.3}" y="{py_m + 0.3}" width="{pw_m - 0.6}" height="{pl_m - 0.6}" fill="#ffffff" stroke="#854d0e" stroke-width="0.08"/>')
        out.append(f'  <text x="{px_m + pw_m/2}" y="{py_m + pl_m/2}" font-size="0.42" font-weight="bold" fill="#854d0e" text-anchor="middle" dominant-baseline="middle">MANDIR</text>')
        out.append('</g>')

    return out

def render_stair_svg(stair, floor_lvl: int) -> list:
    """Render authentic numbered staircase with flight divisions and UP/DN directional arrows."""
    sx, sy, sw, sl = stair.x, stair.y, stair.width, stair.length
    landing_l = min(3.5, sl * 0.32)
    flight_l = sl - landing_l
    steps = 9
    step_h = flight_l / steps
    half_w = (sw - 0.4) / 2
    is_up = (floor_lvl == 0)

    out = [f'<g class="arch-stair" id="{getattr(stair, "id", "stair")}">' ]
    out.append(f'  <rect x="{sx}" y="{sy}" width="{sw}" height="{sl}" fill="#ffffff" stroke="#0f172a" stroke-width="0.25"/>')
    out.append(f'  <rect x="{sx}" y="{sy}" width="{sw}" height="{landing_l}" fill="#f8fafc" stroke="#0f172a" stroke-width="0.14"/>')
    out.append(f'  <text x="{sx + sw/2}" y="{sy + landing_l/2}" font-size="0.42" font-weight="bold" fill="#475569" text-anchor="middle" dominant-baseline="middle" font-family="\'JetBrains Mono\', monospace">LANDING ({format_ft_in(landing_l)})</text>')

    # Central rail
    out.append(f'  <line x1="{sx + half_w}" y1="{sy + landing_l}" x2="{sx + half_w}" y2="{sy + sl}" stroke="#0f172a" stroke-width="0.16"/>')
    out.append(f'  <line x1="{sx + half_w + 0.4}" y1="{sy + landing_l}" x2="{sx + half_w + 0.4}" y2="{sy + sl}" stroke="#0f172a" stroke-width="0.16"/>')

    # Tread lines and numbers
    for i in range(steps):
        ty = sy + sl - landing_l - i * step_h
        # Flight 1 (1-9)
        out.append(f'  <line x1="{sx}" y1="{ty}" x2="{sx + half_w}" y2="{ty}" stroke="#0f172a" stroke-width="0.10"/>')
        out.append(f'  <text x="{sx + half_w/2}" y="{ty - step_h/2}" font-size="0.34" font-weight="bold" fill="#0f172a" text-anchor="middle" dominant-baseline="middle" font-family="\'JetBrains Mono\', monospace">{i + 1}</text>')
        # Flight 2 (10-18)
        out.append(f'  <line x1="{sx + half_w + 0.4}" y1="{ty}" x2="{sx + sw}" y2="{ty}" stroke="#0f172a" stroke-width="0.10"/>')
        out.append(f'  <text x="{sx + half_w + 0.4 + half_w/2}" y="{ty - step_h/2}" font-size="0.34" font-weight="bold" fill="#0f172a" text-anchor="middle" dominant-baseline="middle" font-family="\'JetBrains Mono\', monospace">{steps + (steps - i)}</text>')

    if is_up:
        out.append(f'  <circle cx="{sx + half_w/2}" cy="{sy + sl - 0.6}" r="0.30" fill="#0f172a"/>')
        out.append(f'  <line x1="{sx + half_w/2}" y1="{sy + sl - 0.6}" x2="{sx + half_w/2}" y2="{sy + landing_l + 0.5}" stroke="#0f172a" stroke-width="0.14"/>')
        out.append(f'  <line x1="{sx + half_w/2}" y1="{sy + landing_l + 0.5}" x2="{sx + half_w + 0.4 + half_w/2}" y2="{sy + landing_l + 0.5}" stroke="#0f172a" stroke-width="0.14"/>')
        out.append(f'  <line x1="{sx + half_w + 0.4 + half_w/2}" y1="{sy + landing_l + 0.5}" x2="{sx + half_w + 0.4 + half_w/2}" y2="{sy + sl - 1.2}" stroke="#0f172a" stroke-width="0.14"/>')
        out.append(f'  <polygon points="{sx + half_w + 0.4 + half_w/2},{sy + sl - 0.4} {sx + half_w + 0.4 + half_w/2 - 0.35},{sy + sl - 1.2} {sx + half_w + 0.4 + half_w/2 + 0.35},{sy + sl - 1.2}" fill="#0f172a"/>')
        out.append(f'  <text x="{sx + half_w/2}" y="{sy + sl + 0.7}" font-size="0.55" font-weight="bold" fill="#0f172a" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">UP</text>')
    else:
        out.append(f'  <circle cx="{sx + half_w + 0.4 + half_w/2}" cy="{sy + sl - 0.6}" r="0.30" fill="#0f172a"/>')
        out.append(f'  <line x1="{sx + half_w + 0.4 + half_w/2}" y1="{sy + sl - 0.6}" x2="{sx + half_w + 0.4 + half_w/2}" y2="{sy + landing_l + 0.5}" stroke="#0f172a" stroke-width="0.14"/>')
        out.append(f'  <line x1="{sx + half_w + 0.4 + half_w/2}" y1="{sy + landing_l + 0.5}" x2="{sx + half_w/2}" y2="{sy + landing_l + 0.5}" stroke="#0f172a" stroke-width="0.14"/>')
        out.append(f'  <line x1="{sx + half_w/2}" y1="{sy + landing_l + 0.5}" x2="{sx + half_w/2}" y2="{sy + sl - 1.2}" stroke="#0f172a" stroke-width="0.14"/>')
        out.append(f'  <polygon points="{sx + half_w/2},{sy + sl - 0.4} {sx + half_w/2 - 0.35},{sy + sl - 1.2} {sx + half_w/2 + 0.35},{sy + sl - 1.2}" fill="#0f172a"/>')
        out.append(f'  <text x="{sx + half_w + 0.4 + half_w/2}" y="{sy + sl + 0.7}" font-size="0.55" font-weight="bold" fill="#0f172a" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">DN</text>')

    out.append('</g>')
    return out

def render_floor_content(layout: LayoutData, floor_lvl: int) -> list:
    """Render full CAD content for a specific floor level."""
    plot = layout.plot
    pw, pl = plot.width, plot.length
    target_floor = None
    for fl in layout.floors:
        if fl.level == floor_lvl:
            target_floor = fl
            break
    if not target_floor and layout.floors:
        target_floor = layout.floors[0]

    out = []
    # 1. Site / Outdoor Areas
    if floor_lvl == 0:
        for s in (getattr(plot, "site_areas", []) or []):
            sx = s.get("x", 0) if isinstance(s, dict) else s.x
            sy = s.get("y", 0) if isinstance(s, dict) else s.y
            sw = s.get("width", 0) if isinstance(s, dict) else s.width
            sl = s.get("length", 0) if isinstance(s, dict) else s.length
            stype = (s.get("type", "") if isinstance(s, dict) else s.type).lower()
            slabel = (s.get("label", "") if isinstance(s, dict) else s.label) or stype.replace("_", " ").upper()
            is_gar = "garden" in stype or "lawn" in stype
            poly = s.get("polygon") if isinstance(s, dict) else getattr(s, "polygon", None)
            meta = s.get("metadata", {}) if isinstance(s, dict) else getattr(s, "metadata", {})
            cx = meta.get("center", {}).get("x", sx + sw/2) if isinstance(meta, dict) else sx + sw/2
            cy = meta.get("center", {}).get("y", sy + sl/2) if isinstance(meta, dict) else sy + sl/2

            if poly and len(poly) > 2:
                poly_pts = " ".join([f"{p['x'] if isinstance(p, dict) else p.x},{p['y'] if isinstance(p, dict) else p.y}" for p in poly])
                out.append(f'<polygon points="{poly_pts}" fill="#ffffff" stroke="#0f172a" stroke-width="0.20" stroke-dasharray="0.6 0.3"/>')
                if is_gar:
                    out.append(f'<polygon points="{poly_pts}" fill="url(#cad-lawn-stipple)" />')
            else:
                out.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sl}" fill="#ffffff" stroke="#0f172a" stroke-width="0.20" stroke-dasharray="0.6 0.3"/>')
                if is_gar:
                    out.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sl}" fill="url(#cad-lawn-stipple)" />')

            if sw >= 4 and sl >= 4:
                lbl_text = "RAISED LAWN" if is_gar else slabel
                out.append(f'<text x="{cx}" y="{cy - 0.4}" text-anchor="middle" dominant-baseline="middle" font-size="0.75" font-weight="bold" fill="#0f172a" font-family="\'Segoe UI\', sans-serif">{lbl_text}</text>')
                out.append(f'<text x="{cx}" y="{cy + 0.6}" text-anchor="middle" dominant-baseline="middle" font-size="0.60" font-weight="600" fill="#475569" font-family="\'JetBrains Mono\', monospace">{format_meters(sw)}X{format_meters(sl)} ({format_ft_in(sw)} × {format_ft_in(sl)})</text>')
    else:
        for oa in getattr(target_floor, "outdoor_areas", []):
            ox, oy, ow, ol = oa.x, oa.y, oa.width, oa.length
            otype = oa.type.lower()
            olabel = oa.label or otype.title()
            is_roof = "roof" in otype
            poly = getattr(oa, "polygon", None)
            meta = getattr(oa, "metadata", {}) or {}
            cx = meta.get("center", {}).get("x", ox + ow/2) if isinstance(meta, dict) else ox + ow/2
            cy = meta.get("center", {}).get("y", oy + ol/2) if isinstance(meta, dict) else oy + ol/2
            fill = "#f8fafc" if is_roof else "#ffffff"
            stroke = "#475569" if is_roof else "#0f172a"
            sdash = "0.8 0.4" if is_roof else "0.6 0.3"

            if poly and len(poly) > 2:
                poly_pts = " ".join([f"{p['x'] if isinstance(p, dict) else p.x},{p['y'] if isinstance(p, dict) else p.y}" for p in poly])
                out.append(f'<polygon points="{poly_pts}" fill="{fill}" stroke="{stroke}" stroke-width="0.20" stroke-dasharray="{sdash}"/>')
                if is_roof:
                    out.append(f'<polygon points="{poly_pts}" fill="url(#roof-pattern)"/>')
            else:
                out.append(f'<rect x="{ox}" y="{oy}" width="{ow}" height="{ol}" fill="{fill}" stroke="{stroke}" stroke-width="0.20" stroke-dasharray="{sdash}"/>')
                if is_roof:
                    out.append(f'<rect x="{ox}" y="{oy}" width="{ow}" height="{ol}" fill="url(#roof-pattern)"/>')
            if ow >= 4 and ol >= 4:
                out.append(f'<text x="{cx}" y="{cy - 0.4}" font-size="0.75" font-weight="bold" fill="#0f172a" text-anchor="middle" dominant-baseline="middle" font-family="\'Segoe UI\', sans-serif">{olabel.upper()}</text>')
                out.append(f'<text x="{cx}" y="{cy + 0.6}" font-size="0.60" font-weight="600" fill="#475569" text-anchor="middle" dominant-baseline="middle" font-family="\'JetBrains Mono\', monospace">{format_meters(ow)}X{format_meters(ol)} ({format_ft_in(ow)} × {format_ft_in(ol)})</text>')

    # Veranda & Steps (Ground Floor)
    if floor_lvl == 0 and (plot.facing or "").lower() == "south":
        sb = getattr(plot, "setbacks", {})
        sf = getattr(sb, "front", 5.0) if sb else 5.0
        vw, vl = 6.0, 4.5
        vx = pw / 2 - vw / 2
        vy = pl - sf - vl
        out.append(f'<g class="arch-veranda" pointer-events="none">')
        out.append(f'  <rect x="{vx}" y="{vy + vl}" width="{vw}" height="0.6" fill="#ffffff" stroke="#0f172a" stroke-width="0.10" />')
        out.append(f'  <rect x="{vx + 0.4}" y="{vy + vl + 0.6}" width="{vw - 0.8}" height="0.6" fill="#ffffff" stroke="#0f172a" stroke-width="0.10" />')
        out.append(f'  <rect x="{vx + 0.8}" y="{vy + vl + 1.2}" width="{vw - 1.6}" height="0.6" fill="#ffffff" stroke="#0f172a" stroke-width="0.10" />')
        out.append(f'  <text x="{vx + vw/2}" y="{vy + vl + 1.05}" font-size="0.34" font-weight="bold" fill="#0f172a" text-anchor="middle">UP</text>')
        out.append(f'  <rect x="{vx + vw/2 - 1.5}" y="{vy + vl - 1.0}" width="3.0" height="0.6" fill="#ffffff" stroke="#0f172a" stroke-width="0.08" />')
        out.append(f'  <text x="{vx + vw/2}" y="{vy + vl - 0.6}" font-size="0.32" font-weight="bold" fill="#0f172a" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">+0.60M ROAD LVL</text>')
        out.append('</g>')

    # 2. Indoor Rooms
    indoor_rooms = [r for r in (target_floor.rooms if target_floor else []) if getattr(r, 'space_category', '') != 'outdoor' and r.type not in ['garden', 'yard', 'balcony', 'terrace', 'roof', 'parking', 'garage']]
    for r in indoor_rooms:
        rx, ry, rw, rl = r.x, r.y, r.width, r.length
        rtype = r.type
        rlabel = (r.label or rtype.replace("_", " ")).upper()
        if "LIVING" in rlabel: rlabel = "LIVING HALL"
        if "KITCHEN" in rlabel and "DINING" not in rlabel: rlabel = "KITCHEN"

        col = ROOM_COLORS.get(rtype, ROOM_COLORS["default"])
        out.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rl}" fill="{col["fill"]}" stroke="{col["stroke"]}" stroke-width="0.22"/>')

        # Fixtures
        out.extend(render_fixtures_svg(r))

        # Typography
        cx, cy = rx + rw / 2, ry + rl / 2
        min_dim = min(rw, rl)
        if min_dim >= 12.0:
            t_size, s_size, compact = 1.05, 0.70, False
        elif min_dim >= 8.0:
            t_size, s_size, compact = 0.88, 0.60, False
        elif min_dim >= 5.5:
            t_size, s_size, compact = 0.74, 0.52, False
        else:
            t_size, s_size, compact = 0.58, 0.44, True

        if compact:
            out.append(f'<text x="{cx}" y="{cy - s_size*0.6}" text-anchor="middle" dominant-baseline="middle" font-size="{t_size}" font-weight="bold" fill="#0f172a" font-family="\'Segoe UI\', sans-serif">{rlabel}</text>')
            out.append(f'<text x="{cx}" y="{cy + s_size*0.7}" text-anchor="middle" dominant-baseline="middle" font-size="{s_size}" font-weight="600" fill="#334155" font-family="\'JetBrains Mono\', monospace">{format_meters(rw)}X{format_meters(rl)}</text>')
        else:
            out.append(f'<text x="{cx}" y="{cy - s_size*1.1}" text-anchor="middle" dominant-baseline="middle" font-size="{t_size}" font-weight="bold" fill="#0f172a" letter-spacing="0.04em" font-family="\'Segoe UI\', sans-serif">{rlabel}</text>')
            out.append(f'<text x="{cx}" y="{cy + s_size*0.25}" text-anchor="middle" dominant-baseline="middle" font-size="{s_size}" font-weight="bold" fill="#0f172a" font-family="\'JetBrains Mono\', monospace">{format_meters(rw)}X{format_meters(rl)}</text>')
            out.append(f'<text x="{cx}" y="{cy + s_size*1.55}" text-anchor="middle" dominant-baseline="middle" font-size="{s_size*0.85}" font-weight="500" fill="#475569" font-family="\'JetBrains Mono\', monospace">({format_ft_in(rw)} × {format_ft_in(rl)})</text>')

    # 3. Structural RCC Columns & Tags
    out.extend(render_columns_svg(indoor_rooms, pw, pl))

    # 4. Walls
    for w in (target_floor.walls if target_floor else []):
        is_ext = getattr(w, "type", "") == "exterior"
        w_stroke = "#0f172a"
        w_thick = 0.75 if is_ext else 0.38
        out.append(f'<line x1="{w.start.x}" y1="{w.start.y}" x2="{w.end.x}" y2="{w.end.y}" stroke="{w_stroke}" stroke-width="{w_thick}" stroke-linecap="square"/>')

    # 5. Doors with Tags (D, D1, D2)
    gap_thick = 0.95
    for d in (target_floor.doors if target_floor else []):
        dx, dy = d.position.x, d.position.y
        dw = getattr(d, "width", 3.0)
        is_main = getattr(d, "type", "") == "main_entrance"
        stroke_col = "#dc2626" if is_main else "#0f172a"
        stroke_w = 0.24 if is_main else 0.14

        owner_room = None
        for rm in indoor_rooms:
            if d.room_ids and rm.id in d.room_ids:
                owner_room = rm
                break
        rtype = (owner_room.type.lower() if owner_room else "")
        d_code = "D" if is_main else ("D2" if any(k in rtype for k in ["bath", "toilet", "store", "balcony"]) else "D1")
        d_dim = "1.00X2.10" if is_main else ("0.75X2.10" if d_code == "D2" else "0.90X2.10")

        orient = "south"
        if owner_room:
            eps = 1.0
            if abs(dy - owner_room.y) < eps: orient = "north"
            elif abs(dy - (owner_room.y + owner_room.length)) < eps: orient = "south"
            elif abs(dx - owner_room.x) < eps: orient = "west"
            elif abs(dx - (owner_room.x + owner_room.width)) < eps: orient = "east"

        if orient == "north":
            wy = owner_room.y if owner_room else dy
            out.append(f'<rect x="{dx}" y="{wy - gap_thick/2}" width="{dw}" height="{gap_thick}" fill="#ffffff" />')
            out.append(f'<line x1="{dx}" y1="{wy - 0.4}" x2="{dx}" y2="{wy + 0.4}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{dx + dw}" y1="{wy - 0.4}" x2="{dx + dw}" y2="{wy + 0.4}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{dx}" y1="{wy}" x2="{dx}" y2="{wy + dw}" stroke="{stroke_col}" stroke-width="{stroke_w}" />')
            out.append(f'<path d="M {dx} {wy + dw} A {dw} {dw} 0 0 0 {dx + dw} {wy}" fill="none" stroke="{stroke_col}" stroke-width="{stroke_w * 0.8}" stroke-dasharray="0.3 0.15" />')
            out.append(f'<text x="{dx + dw/2}" y="{wy + dw + 0.55}" font-size="0.38" font-weight="bold" fill="{stroke_col}" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">{d_code} ({d_dim})</text>')
            if is_main:
                out.append(f'<rect x="{dx + dw/2 - 1.4}" y="{wy - 1.3}" width="2.8" height="0.7" fill="#dc2626" rx="0.2" />')
                out.append(f'<text x="{dx + dw/2}" y="{wy - 0.85}" font-size="0.42" font-weight="bold" fill="#ffffff" text-anchor="middle">MAIN ENTRANCE</text>')
        elif orient == "south":
            wy = (owner_room.y + owner_room.length) if owner_room else dy
            out.append(f'<rect x="{dx}" y="{wy - gap_thick/2}" width="{dw}" height="{gap_thick}" fill="#ffffff" />')
            out.append(f'<line x1="{dx}" y1="{wy - 0.4}" x2="{dx}" y2="{wy + 0.4}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{dx + dw}" y1="{wy - 0.4}" x2="{dx + dw}" y2="{wy + 0.4}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{dx}" y1="{wy}" x2="{dx}" y2="{wy - dw}" stroke="{stroke_col}" stroke-width="{stroke_w}" />')
            out.append(f'<path d="M {dx} {wy - dw} A {dw} {dw} 0 0 1 {dx + dw} {wy}" fill="none" stroke="{stroke_col}" stroke-width="{stroke_w * 0.8}" stroke-dasharray="0.3 0.15" />')
            out.append(f'<text x="{dx + dw/2}" y="{wy - dw - 0.3}" font-size="0.38" font-weight="bold" fill="{stroke_col}" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">{d_code} ({d_dim})</text>')
            if is_main:
                out.append(f'<rect x="{dx + dw/2 - 1.4}" y="{wy + 0.6}" width="2.8" height="0.7" fill="#dc2626" rx="0.2" />')
                out.append(f'<text x="{dx + dw/2}" y="{wy + 1.05}" font-size="0.42" font-weight="bold" fill="#ffffff" text-anchor="middle">MAIN ENTRANCE</text>')
        elif orient == "west":
            wx = owner_room.x if owner_room else dx
            out.append(f'<rect x="{wx - gap_thick/2}" y="{dy}" width="{gap_thick}" height="{dw}" fill="#ffffff" />')
            out.append(f'<line x1="{wx - 0.4}" y1="{dy}" x2="{wx + 0.4}" y2="{dy}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{wx - 0.4}" y1="{dy + dw}" x2="{wx + 0.4}" y2="{dy + dw}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{wx}" y1="{dy}" x2="{wx + dw}" y2="{dy}" stroke="{stroke_col}" stroke-width="{stroke_w}" />')
            out.append(f'<path d="M {wx + dw} {dy} A {dw} {dw} 0 0 1 {wx} {dy + dw}" fill="none" stroke="{stroke_col}" stroke-width="{stroke_w * 0.8}" stroke-dasharray="0.3 0.15" />')
            out.append(f'<text x="{wx + dw + 0.8}" y="{dy + dw/2}" font-size="0.38" font-weight="bold" fill="{stroke_col}" text-anchor="middle" transform="rotate(90 {wx + dw + 0.8} {dy + dw/2})" font-family="\'JetBrains Mono\', monospace">{d_code} ({d_dim})</text>')
            if is_main:
                out.append(f'<rect x="{wx - 2.8}" y="{dy + dw/2 - 0.35}" width="2.6" height="0.7" fill="#dc2626" rx="0.2" />')
                out.append(f'<text x="{wx - 1.5}" y="{dy + dw/2 + 0.1}" font-size="0.42" font-weight="bold" fill="#ffffff" text-anchor="middle">MAIN ENTRY</text>')
        else: # east
            wx = (owner_room.x + owner_room.width) if owner_room else dx
            out.append(f'<rect x="{wx - gap_thick/2}" y="{dy}" width="{gap_thick}" height="{dw}" fill="#ffffff" />')
            out.append(f'<line x1="{wx - 0.4}" y1="{dy}" x2="{wx + 0.4}" y2="{dy}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{wx - 0.4}" y1="{dy + dw}" x2="{wx + 0.4}" y2="{dy + dw}" stroke="#0f172a" stroke-width="0.16" />')
            out.append(f'<line x1="{wx}" y1="{dy}" x2="{wx - dw}" y2="{dy}" stroke="{stroke_col}" stroke-width="{stroke_w}" />')
            out.append(f'<path d="M {wx - dw} {dy} A {dw} {dw} 0 0 0 {wx} {dy + dw}" fill="none" stroke="{stroke_col}" stroke-width="{stroke_w * 0.8}" stroke-dasharray="0.3 0.15" />')
            out.append(f'<text x="{wx - dw - 0.8}" y="{dy + dw/2}" font-size="0.38" font-weight="bold" fill="{stroke_col}" text-anchor="middle" transform="rotate(-90 {wx - dw - 0.8} {dy + dw/2})" font-family="\'JetBrains Mono\', monospace">{d_code} ({d_dim})</text>')
            if is_main:
                out.append(f'<rect x="{wx + 0.5}" y="{dy + dw/2 - 0.35}" width="2.6" height="0.7" fill="#dc2626" rx="0.2" />')
                out.append(f'<text x="{wx + 1.8}" y="{dy + dw/2 + 0.1}" font-size="0.42" font-weight="bold" fill="#ffffff" text-anchor="middle">MAIN ENTRY</text>')

    # 6. Windows with Chhajja & Code Tags
    gap_win = 0.9
    sill_thick = 0.42
    chhajja_proj = 1.5
    for win in (target_floor.windows if target_floor else []):
        wx, wy = win.position.x, win.position.y
        ww = getattr(win, "width", 4.0)
        owner_room = None
        win_rid = getattr(win, "room_id", None) or getattr(win, "room_ids", None)
        if win_rid:
            for rm in indoor_rooms:
                if (isinstance(win_rid, list) and rm.id in win_rid) or rm.id == win_rid:
                    owner_room = rm
                    break
        if not owner_room:
            for rm in indoor_rooms:
                if rm.x - 1.5 <= wx <= rm.x + rm.width + 1.5 and rm.y - 1.5 <= wy <= rm.y + rm.length + 1.5:
                    owner_room = rm
                    break
        rtype = (owner_room.type.lower() if owner_room else "")
        is_vent = "bath" in rtype or "toilet" in rtype
        w_code = "V" if is_vent else ("W1" if ww >= 5.5 else ("W3" if "kitchen" in rtype else "W"))
        w_dim = "0.60X0.90" if is_vent else ("1.80X0.90" if w_code == "W1" else ("1.20X1.00" if w_code == "W3" else "1.50X1.50"))

        is_n = wy <= 3.0
        is_s = wy >= pl - 3.0
        is_w = wx <= 3.0
        is_e = wx >= pw - 3.0
        is_horiz = is_n or is_s or (not is_w and not is_e)

        if is_horiz:
            is_top = is_n or wy < pl / 2
            chhajja_y = wy - chhajja_proj if is_top else wy + gap_win / 2
            out.append(f'<rect x="{wx}" y="{wy - gap_win/2}" width="{ww}" height="{gap_win}" fill="#ffffff" />')
            out.append(f'<rect x="{wx}" y="{wy - sill_thick/2}" width="{ww}" height="{sill_thick}" fill="#ffffff" stroke="#0f172a" stroke-width="0.12" />')
            out.append(f'<line x1="{wx}" y1="{wy - 0.08}" x2="{wx + ww}" y2="{wy - 0.08}" stroke="#0f172a" stroke-width="0.08" />')
            out.append(f'<line x1="{wx}" y1="{wy + 0.08}" x2="{wx + ww}" y2="{wy + 0.08}" stroke="#0f172a" stroke-width="0.08" />')
            out.append(f'<rect x="{wx - 0.5}" y="{chhajja_y}" width="{ww + 1.0}" height="{chhajja_proj}" fill="none" stroke="#475569" stroke-width="0.10" stroke-dasharray="0.35 0.15"/>')
            tag_y = chhajja_y - 0.35 if is_top else chhajja_y + chhajja_proj + 0.65
            out.append(f'<text x="{wx + ww/2}" y="{tag_y}" font-size="0.42" font-weight="bold" fill="#0f172a" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">{w_code} ({w_dim})</text>')
        else:
            is_l = is_w or wx < pw / 2
            chhajja_x = wx - chhajja_proj if is_l else wx + gap_win / 2
            out.append(f'<rect x="{wx - gap_win/2}" y="{wy}" width="{gap_win}" height="{ww}" fill="#ffffff" />')
            out.append(f'<rect x="{wx - sill_thick/2}" y="{wy}" width="{sill_thick}" height="{ww}" fill="#ffffff" stroke="#0f172a" stroke-width="0.12" />')
            out.append(f'<line x1="{wx - 0.08}" y1="{wy}" x2="{wx - 0.08}" y2="{wy + ww}" stroke="#0f172a" stroke-width="0.08" />')
            out.append(f'<line x1="{wx + 0.08}" y1="{wy}" x2="{wx + 0.08}" y2="{wy + ww}" stroke="#0f172a" stroke-width="0.08" />')
            out.append(f'<rect x="{chhajja_x}" y="{wy - 0.5}" width="{chhajja_proj}" height="{ww + 1.0}" fill="none" stroke="#475569" stroke-width="0.10" stroke-dasharray="0.35 0.15"/>')
            tag_x = chhajja_x - 0.4 if is_l else chhajja_x + chhajja_proj + 0.6
            rot = -90 if is_l else 90
            out.append(f'<text x="{tag_x}" y="{wy + ww/2}" font-size="0.42" font-weight="bold" fill="#0f172a" text-anchor="middle" dominant-baseline="middle" transform="rotate({rot} {tag_x} {wy + ww/2})" font-family="\'JetBrains Mono\', monospace">{w_code} ({w_dim})</text>')

    # 7. Stairs
    for st in (target_floor.stairs if target_floor else []):
        out.extend(render_stair_svg(st, floor_lvl))

    return out

def render_architectural_svg(layout: LayoutData, mode: str) -> str:
    """
    Renders standalone architectural SVG blueprints:
    - mode == '0': Ground Floor Plan
    - mode == '1': First Floor Plan
    - mode == 'both': Both Ground & First Floor side-by-side (AutoCAD Sheet Mode)
    - mode == 'site': Site Plan & Roof Overview
    """
    plot = layout.plot
    pw = plot.width
    pl = plot.length
    facing = (plot.front_side or plot.facing or "south").lower()
    is_both = (mode == 'both')
    is_site = (mode == 'site')
    floor_lvl = int(mode) if not (is_both or is_site) else 0

    if is_both:
        spacing = 12.0
        total_w = pw * 2 + spacing
        pad_left = 8.0
        pad_right = 10.0
        pad_top = 8.5
        pad_bottom = 18.0
        view_x = -pad_left
        view_y = -pad_top
        view_w = total_w + pad_left + pad_right
        view_h = pl + pad_top + pad_bottom
    else:
        pad_left = 8.0
        pad_right = 10.0
        pad_top = 8.5
        pad_bottom = 16.0
        view_x = -pad_left
        view_y = -pad_top
        view_w = pw + pad_left + pad_right
        view_h = pl + pad_top + pad_bottom

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_x} {view_y} {view_w} {view_h}" '
               f'width="100%" height="100%" style="background:#ffffff; font-family:\'Segoe UI\',system-ui,sans-serif;">')

    # Shared Defs
    svg.append('<defs>')
    svg.append('  <pattern id="arch-grid-pattern" width="5" height="5" patternUnits="userSpaceOnUse">')
    svg.append('    <path d="M 5 0 L 0 0 0 5" fill="none" stroke="#f1f5f9" stroke-width="0.05" />')
    svg.append('  </pattern>')
    svg.append('  <pattern id="cad-lawn-stipple" width="2" height="2" patternUnits="userSpaceOnUse">')
    svg.append('    <line x1="1" y1="0.6" x2="1" y2="1.4" stroke="#0f172a" stroke-width="0.08" />')
    svg.append('    <line x1="0.6" y1="1" x2="1.4" y2="1" stroke="#0f172a" stroke-width="0.08" />')
    svg.append('  </pattern>')
    svg.append('  <pattern id="footprint-hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">')
    svg.append('    <line x1="0" y1="0" x2="0" y2="1.2" stroke="#64748b" stroke-width="0.12" opacity="0.3" />')
    svg.append('  </pattern>')
    svg.append('  <pattern id="roof-pattern" width="1.8" height="1.8" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">')
    svg.append('    <line x1="0" y1="0" x2="0" y2="1.8" stroke="#94a3b8" stroke-width="0.1" stroke-dasharray="0.3 0.2" opacity="0.4" />')
    svg.append('  </pattern>')
    svg.append('</defs>')

    def render_grid(gx_off=0):
        res = [f'<rect x="{gx_off}" y="0" width="{pw}" height="{pl}" fill="url(#arch-grid-pattern)" />']
        for x in range(0, int(pw) + 1, 5):
            is_maj = (x % 10 == 0)
            sw = 0.04 if is_maj else 0.02
            op = 0.6 if is_maj else 0.35
            res.append(f'<line x1="{gx_off + x}" y1="0" x2="{gx_off + x}" y2="{pl}" stroke="#e2e8f0" stroke-width="{sw}" opacity="{op}"/>')
        for y in range(0, int(pl) + 1, 5):
            is_maj = (y % 10 == 0)
            sw = 0.04 if is_maj else 0.02
            op = 0.6 if is_maj else 0.35
            res.append(f'<line x1="{gx_off}" y1="{y}" x2="{gx_off + pw}" y2="{y}" stroke="#e2e8f0" stroke-width="{sw}" opacity="{op}"/>')
        res.append(f'<rect x="{gx_off}" y="0" width="{pw}" height="{pl}" fill="none" stroke="#0f172a" stroke-width="0.55" />')
        return res

    def render_road():
        r_w = 30
        y_pos = pl + 1.5
        r_out = ['<g class="arch-road">']
        r_out.append(f'  <line x1="-6" y1="{y_pos}" x2="{pw + 6}" y2="{y_pos}" stroke="#0f172a" stroke-width="0.5" />')
        r_out.append(f'  <line x1="-6" y1="{y_pos + 2.5}" x2="{pw + 6}" y2="{y_pos + 2.5}" stroke="#94a3b8" stroke-width="0.2" stroke-dasharray="1.5 1.0" />')
        r_out.append(f'  <line x1="-6" y1="{y_pos + 5.0}" x2="{pw + 6}" y2="{y_pos + 5.0}" stroke="#0f172a" stroke-width="0.5" />')
        r_out.append(f'  <rect x="{pw/2 - 2.0}" y="{y_pos + 0.4}" width="4.0" height="0.65" fill="#ffffff" stroke="#0f172a" stroke-width="0.08" />')
        r_out.append(f'  <text x="{pw/2}" y="{y_pos + 0.85}" font-size="0.34" font-weight="bold" fill="#0f172a" text-anchor="middle" font-family="\'JetBrains Mono\', monospace">0.0 M ROAD LVL</text>')
        r_out.append(f'  <text x="{pw/2}" y="{y_pos + 3.0}" font-size="1.1" font-weight="800" fill="#0f172a" text-anchor="middle" dominant-baseline="middle" letter-spacing="0.18em">&lt;==== R O A D ====&gt;</text>')
        r_out.append(f'  <text x="{pw/2}" y="{y_pos + 4.3}" font-size="0.48" font-weight="600" fill="#64748b" text-anchor="middle">{r_w}\'-0" WIDE ACCESS ROAD ({facing.upper()} FACING)</text>')
        r_out.append('</g>')
        return r_out

    def render_ext_dims(gx_off=0):
        tick_sz = 0.65
        offset = 2.4
        f_size = max(0.85, min(1.2, pw * 0.035))
        d_out = ['<g stroke="#0f172a" fill="#0f172a" font-family="\'JetBrains Mono\', monospace">']
        d_out.append(f'<line x1="{gx_off}" y1="{-offset}" x2="{gx_off + pw}" y2="{-offset}" stroke-width="0.12" />')
        d_out.append(f'<line x1="{gx_off}" y1="{-offset - 0.8}" x2="{gx_off}" y2="0" stroke-width="0.08" stroke-dasharray="0.3 0.15" opacity="0.6" />')
        d_out.append(f'<line x1="{gx_off + pw}" y1="{-offset - 0.8}" x2="{gx_off + pw}" y2="0" stroke-width="0.08" stroke-dasharray="0.3 0.15" opacity="0.6" />')
        d_out.append(f'<line x1="{gx_off - tick_sz/2}" y1="{-offset + tick_sz/2}" x2="{gx_off + tick_sz/2}" y2="{-offset - tick_sz/2}" stroke="#0f172a" stroke-width="0.16" />')
        d_out.append(f'<line x1="{gx_off + pw - tick_sz/2}" y1="{-offset + tick_sz/2}" x2="{gx_off + pw + tick_sz/2}" y2="{-offset - tick_sz/2}" stroke="#0f172a" stroke-width="0.16" />')
        d_out.append(f'<text x="{gx_off + pw/2}" y="{-offset - 0.6}" text-anchor="middle" font-size="{f_size}" font-weight="700" stroke="none">PLOT WIDTH: {format_ft_in(pw)} ({format_meters(pw)} M)</text>')
        dim_x = gx_off + pw + offset
        ext_x = gx_off + pw + offset + 0.8
        d_out.append(f'<line x1="{dim_x}" y1="0" x2="{dim_x}" y2="{pl}" stroke-width="0.12" />')
        d_out.append(f'<line x1="{gx_off + pw}" y1="0" x2="{ext_x}" y2="0" stroke-width="0.08" stroke-dasharray="0.3 0.15" opacity="0.6" />')
        d_out.append(f'<line x1="{gx_off + pw}" y1="{pl}" x2="{ext_x}" y2="{pl}" stroke-width="0.08" stroke-dasharray="0.3 0.15" opacity="0.6" />')
        d_out.append(f'<line x1="{dim_x - tick_sz/2}" y1="{tick_sz/2}" x2="{dim_x + tick_sz/2}" y2="{-tick_sz/2}" stroke="#0f172a" stroke-width="0.16" />')
        d_out.append(f'<line x1="{dim_x - tick_sz/2}" y1="{pl + tick_sz/2}" x2="{dim_x + tick_sz/2}" y2="{pl - tick_sz/2}" stroke="#0f172a" stroke-width="0.16" />')
        d_out.append(f'<text x="{ext_x}" y="{pl/2}" text-anchor="middle" dominant-baseline="middle" font-size="{f_size}" font-weight="700" stroke="none" transform="rotate(90 {ext_x} {pl/2})">PLOT LENGTH: {format_ft_in(pl)} ({format_meters(pl)} M)</text>')
        d_out.append('</g>')
        return d_out

    if is_both:
        # ── AUTOCAD BLUEPRINT SHEET MODE: BOTH FLOORS SIDE-BY-SIDE ──
        # Left Pane: Ground Floor
        svg.extend(render_grid(0))
        svg.append('<g transform="translate(0, 0)">')
        svg.extend(render_floor_content(layout, 0))
        svg.extend(render_road())
        svg.extend(render_ext_dims(0))
        svg.append(f'<text x="{pw/2}" y="{pl + 9.5}" text-anchor="middle" font-size="1.3" font-weight="800" fill="#0f172a" letter-spacing="0.08em">EXI. GROUND FLOOR PLAN</text>')
        svg.append('</g>')

        # Right Pane: First Floor
        right_x = pw + spacing
        svg.extend(render_grid(right_x))
        svg.append(f'<g transform="translate({right_x}, 0)">')
        svg.extend(render_floor_content(layout, 1))
        svg.extend(render_ext_dims(right_x))
        svg.append(f'<text x="{pw/2}" y="{pl + 9.5}" text-anchor="middle" font-size="1.3" font-weight="800" fill="#0f172a" letter-spacing="0.08em">FIRST FLOOR PLAN</text>')
        svg.append('</g>')

        # Title Block across both
        ty = pl + 12.0
        svg.append(f'<g transform="translate(0, {ty})" font-family="\'Segoe UI\', sans-serif">')
        svg.append(f'  <rect x="0" y="0" width="{total_w}" height="3.2" fill="#ffffff" stroke="#0f172a" stroke-width="0.2" />')
        svg.append(f'  <line x1="{total_w * 0.45}" y1="0" x2="{total_w * 0.45}" y2="3.2" stroke="#cbd5e1" stroke-width="0.1" />')
        svg.append(f'  <line x1="{total_w * 0.78}" y1="0" x2="{total_w * 0.78}" y2="3.2" stroke="#cbd5e1" stroke-width="0.1" />')
        svg.append(f'  <text x="1.2" y="1.2" font-size="0.95" font-weight="800" fill="#0f172a" letter-spacing="0.04em">RESIDENTIAL WORKING BLUEPRINT (G+1 CAD SHEET)</text>')
        svg.append('  <text x="1.2" y="2.3" font-size="0.55" font-weight="600" fill="#64748b" letter-spacing="0.02em">ARCHITECTURAL DESIGN &amp; RCC STRUCTURAL GRID</text>')
        svg.append(f'  <text x="{total_w * 0.45 + 1.2}" y="1.1" font-size="0.58" font-weight="600" fill="#334155">PLOT: {format_ft_in(pw)} × {format_ft_in(pl)} ({int(pw * pl)} SQ FT / {format_meters(pw)} × {format_meters(pl)} M)</text>')
        svg.append(f'  <text x="{total_w * 0.45 + 1.2}" y="2.2" font-size="0.55" font-weight="500" fill="#64748b">ORIENTATION: {facing.upper()} FACING | CODE-COMPLIANT ARCHITECTURE</text>')
        svg.append(f'  <text x="{total_w * 0.78 + 1.2}" y="1.1" font-size="0.55" font-weight="700" fill="#059669">VALIDATED BLUEPRINT</text>')
        canonical_id = layout.metadata.get("canonical_run_id", "")
        id_lbl = f"RUN: {canonical_id}" if canonical_id else "OR-TOOLS & GEMINI AI"
        svg.append(f'  <text x="{total_w * 0.78 + 1.2}" y="2.2" font-size="0.40" font-weight="600" fill="#64748b">{id_lbl}</text>')
        svg.append('</g>')

        # Compass & Scale
        comp_rot = 0 if facing == 'south' else (180 if facing == 'north' else (270 if facing == 'east' else 90))
        svg.append(f'<g transform="translate(-3.5, -3.5)">')
        svg.append('  <circle cx="0" cy="0" r="1.8" fill="#ffffff" stroke="#0f172a" stroke-width="0.12" />')
        svg.append(f'  <g transform="rotate({comp_rot})">')
        svg.append('    <polygon points="0,-1.4 0.45,0 0,0" fill="#0f172a" />')
        svg.append('    <polygon points="0,-1.4 -0.45,0 0,0" fill="#ffffff" stroke="#0f172a" stroke-width="0.06" />')
        svg.append('    <polygon points="0,1.4 0.45,0 0,0" fill="#94a3b8" />')
        svg.append('    <polygon points="0,1.4 -0.45,0 0,0" fill="#cbd5e1" />')
        svg.append('  </g>')
        svg.append('  <text x="0" y="-2.1" font-size="0.9" font-weight="bold" fill="#0f172a" text-anchor="middle">N</text>')
        svg.append('</g>')

        sy = pl + 16.0
        svg.append(f'<g transform="translate(0, {sy})" font-family="\'JetBrains Mono\', monospace">')
        svg.append('  <rect x="0" y="0" width="5" height="0.5" fill="#0f172a" stroke="#0f172a" stroke-width="0.08" />')
        svg.append('  <rect x="5" y="0" width="5" height="0.5" fill="#ffffff" stroke="#0f172a" stroke-width="0.08" />')
        svg.append('  <rect x="10" y="0" width="10" height="0.5" fill="#0f172a" stroke="#0f172a" stroke-width="0.08" />')
        svg.append('  <text x="0" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">0</text>')
        svg.append('  <text x="5" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">5\'</text>')
        svg.append('  <text x="10" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">10\'</text>')
        svg.append('  <text x="20" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">20\' FT</text>')
        svg.append('  <text x="10" y="1.4" font-size="0.48" font-weight="500" fill="#64748b" text-anchor="middle">GRAPHIC SCALE: 1 UNIT = 1\'-0" (FEET &amp; INCHES)</text>')
        svg.append('</g>')

    else:
        # ── SINGLE FLOOR OR SITE PLAN VIEW ──
        svg.extend(render_grid(0))
        if is_site:
            # Site Plan View
            for s in (getattr(plot, "site_areas", []) or []):
                sx = s.get("x", 0) if isinstance(s, dict) else s.x
                sy = s.get("y", 0) if isinstance(s, dict) else s.y
                sw = s.get("width", 0) if isinstance(s, dict) else s.width
                sl = s.get("length", 0) if isinstance(s, dict) else s.length
                stype = (s.get("type", "") if isinstance(s, dict) else s.type).lower()
                slabel = (s.get("label", "") if isinstance(s, dict) else s.label) or stype.replace("_", " ").upper()
                is_gar = "garden" in stype or "lawn" in stype
                svg.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sl}" fill="#ffffff" stroke="#0f172a" stroke-width="0.16" stroke-dasharray="0.6 0.3"/>')
                if is_gar:
                    svg.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sl}" fill="url(#cad-lawn-stipple)" />')
                if sw >= 4 and sl >= 4:
                    svg.append(f'<text x="{sx + sw/2}" y="{sy + sl/2}" text-anchor="middle" dominant-baseline="middle" font-size="0.75" font-weight="600" fill="#475569">{slabel}</text>')

            fp = getattr(plot, "building_footprint", None)
            if fp:
                fx = fp.get("x", 0) if isinstance(fp, dict) else fp.x
                fy = fp.get("y", 0) if isinstance(fp, dict) else fp.y
                fw = fp.get("width", 0) if isinstance(fp, dict) else fp.width
                fl = fp.get("length", 0) if isinstance(fp, dict) else fp.length
                f_area = round(fw * fl)
                svg.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fl}" fill="#f1f5f9" stroke="#0f172a" stroke-width="0.65" />')
                svg.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fl}" fill="url(#footprint-hatch)" />')
                svg.append(f'<rect x="{fx + fw/2 - 12}" y="{fy + fl/2 - 2.0}" width="24" height="4.0" fill="#ffffff" stroke="#0f172a" stroke-width="0.16" rx="0.3" />')
                svg.append(f'<text x="{fx + fw/2}" y="{fy + fl/2 - 0.6}" font-size="0.88" font-weight="800" fill="#0f172a" text-anchor="middle">PROPOSED BUILDING FOOTPRINT</text>')
                svg.append(f'<text x="{fx + fw/2}" y="{fy + fl/2 + 0.8}" font-size="0.68" font-weight="600" fill="#334155" text-anchor="middle">{format_ft_in(fw)} × {format_ft_in(fl)} ({f_area} SQ FT)</text>')
        else:
            svg.extend(render_floor_content(layout, floor_lvl))

        svg.extend(render_road())
        svg.extend(render_ext_dims(0))

        # Title Block
        ty = pl + 8.0
        target_floor_obj = None
        if not is_site:
            for fl in layout.floors:
                if fl.level == floor_lvl:
                    target_floor_obj = fl
                    break
            if not target_floor_obj and layout.floors:
                target_floor_obj = layout.floors[0]
        indoor_rooms_cnt = [r for r in (target_floor_obj.rooms if target_floor_obj else []) if getattr(r, 'space_category', '') != 'outdoor' and r.type not in ['garden', 'yard', 'terrace', 'balcony', 'parking', 'garage', 'roof', 'driveway']]
        room_cnt = len(indoor_rooms_cnt) if not is_site else 0

        sheet_title = "SITE PLAN & ROOF OVERVIEW" if is_site else ("EXI. GROUND FLOOR PLAN" if floor_lvl == 0 else ("FIRST FLOOR PLAN" if floor_lvl == 1 else f"FLOOR {floor_lvl} PLAN"))
        svg.append(f'<g transform="translate(0, {ty})" font-family="\'Segoe UI\', sans-serif">')
        svg.append(f'  <rect x="0" y="0" width="{pw}" height="3.2" fill="#ffffff" stroke="#0f172a" stroke-width="0.2" />')
        svg.append(f'  <line x1="{pw * 0.45}" y1="0" x2="{pw * 0.45}" y2="3.2" stroke="#cbd5e1" stroke-width="0.1" />')
        svg.append(f'  <line x1="{pw * 0.78}" y1="0" x2="{pw * 0.78}" y2="3.2" stroke="#cbd5e1" stroke-width="0.1" />')
        svg.append(f'  <text x="1.2" y="1.2" font-size="0.95" font-weight="800" fill="#0f172a" letter-spacing="0.04em">{sheet_title}</text>')
        svg.append('  <text x="1.2" y="2.3" font-size="0.55" font-weight="600" fill="#64748b" letter-spacing="0.02em">RESIDENTIAL ARCHITECTURAL WORKING DRAWING</text>')
        svg.append(f'  <text x="{pw * 0.45 + 1.2}" y="1.1" font-size="0.58" font-weight="600" fill="#334155">PLOT: {format_ft_in(pw)} × {format_ft_in(pl)} ({int(pw * pl)} SQ FT / {format_meters(pw)} × {format_meters(pl)} M)</text>')
        svg.append(f'  <text x="{pw * 0.45 + 1.2}" y="2.2" font-size="0.55" font-weight="500" fill="#64748b">ORIENTATION: {facing.upper()} FACING | ROOMS ON LEVEL: {room_cnt}</text>')
        svg.append(f'  <text x="{pw * 0.78 + 1.2}" y="1.1" font-size="0.55" font-weight="700" fill="#059669">VALIDATED BLUEPRINT</text>')
        canonical_id = layout.metadata.get("canonical_run_id", "")
        id_lbl = f"RUN: {canonical_id}" if canonical_id else "OR-TOOLS & GEMINI AI"
        svg.append(f'  <text x="{pw * 0.78 + 1.2}" y="2.2" font-size="0.40" font-weight="600" fill="#64748b">{id_lbl}</text>')
        svg.append('</g>')

        # Compass & Scale
        comp_rot = 0 if facing == 'south' else (180 if facing == 'north' else (270 if facing == 'east' else 90))
        svg.append(f'<g transform="translate(-3.5, -3.5)">')
        svg.append('  <circle cx="0" cy="0" r="1.8" fill="#ffffff" stroke="#0f172a" stroke-width="0.12" />')
        svg.append(f'  <g transform="rotate({comp_rot})">')
        svg.append('    <polygon points="0,-1.4 0.45,0 0,0" fill="#0f172a" />')
        svg.append('    <polygon points="0,-1.4 -0.45,0 0,0" fill="#ffffff" stroke="#0f172a" stroke-width="0.06" />')
        svg.append('    <polygon points="0,1.4 0.45,0 0,0" fill="#94a3b8" />')
        svg.append('    <polygon points="0,1.4 -0.45,0 0,0" fill="#cbd5e1" />')
        svg.append('  </g>')
        svg.append('  <text x="0" y="-2.1" font-size="0.9" font-weight="bold" fill="#0f172a" text-anchor="middle">N</text>')
        svg.append('</g>')

        sy = pl + 12.2
        svg.append(f'<g transform="translate(0, {sy})" font-family="\'JetBrains Mono\', monospace">')
        svg.append('  <rect x="0" y="0" width="5" height="0.5" fill="#0f172a" stroke="#0f172a" stroke-width="0.08" />')
        svg.append('  <rect x="5" y="0" width="5" height="0.5" fill="#ffffff" stroke="#0f172a" stroke-width="0.08" />')
        svg.append('  <rect x="10" y="0" width="10" height="0.5" fill="#0f172a" stroke="#0f172a" stroke-width="0.08" />')
        svg.append('  <text x="0" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">0</text>')
        svg.append('  <text x="5" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">5\'</text>')
        svg.append('  <text x="10" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">10\'</text>')
        svg.append('  <text x="20" y="-0.5" font-size="0.55" font-weight="600" fill="#0f172a" text-anchor="middle">20\' FT</text>')
        svg.append('  <text x="10" y="1.4" font-size="0.48" font-weight="500" fill="#64748b" text-anchor="middle">GRAPHIC SCALE: 1 UNIT = 1\'-0" (FEET &amp; INCHES)</text>')
        svg.append('</g>')

    svg.append('</svg>')
    return "\n".join(svg)

def export_all():
    out_dir = r"C:\Users\DELL\.gemini\antigravity\brain\35ff5483-d119-45be-a407-00f491b2c1fa"
    canonical_dir = os.path.join(os.path.dirname(__file__), "canonical_layouts")
    os.makedirs(out_dir, exist_ok=True)

    # 1. 50x80 South (villa) Canonical
    path_50 = os.path.join(canonical_dir, "canonical_50x80_south_g1.json")
    print(f"Loading Canonical 50x80 Layout from {path_50}...")
    with open(path_50, "r", encoding="utf-8") as f:
        layout_50 = LayoutData.model_validate_json(f.read())

    p_50_g = os.path.join(out_dir, "floorplan_50x80_ground.svg")
    p_50_1 = os.path.join(out_dir, "floorplan_50x80_first.svg")
    p_50_b = os.path.join(out_dir, "floorplan_50x80_both.svg")
    p_50_s = os.path.join(out_dir, "floorplan_50x80_site.svg")

    with open(p_50_g, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_50, '0'))
    with open(p_50_1, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_50, '1'))
    with open(p_50_b, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_50, 'both'))
    with open(p_50_s, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_50, 'site'))

    print(f"Saved: {p_50_g}")
    print(f"Saved: {p_50_1}")
    print(f"Saved: {p_50_b}")
    print(f"Saved: {p_50_s}")

    # 2. 30x40 East (test 1) Canonical
    path_30 = os.path.join(canonical_dir, "canonical_30x40_east_g1.json")
    print(f"\nLoading Canonical 30x40 Layout from {path_30}...")
    with open(path_30, "r", encoding="utf-8") as f:
        layout_30 = LayoutData.model_validate_json(f.read())

    p_30_g = os.path.join(out_dir, "floorplan_30x40_ground.svg")
    p_30_1 = os.path.join(out_dir, "floorplan_30x40_first.svg")
    p_30_b = os.path.join(out_dir, "floorplan_30x40_both.svg")
    p_30_s = os.path.join(out_dir, "floorplan_30x40_site.svg")

    with open(p_30_g, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_30, '0'))
    with open(p_30_1, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_30, '1'))
    with open(p_30_b, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_30, 'both'))
    with open(p_30_s, "w", encoding="utf-8") as f:
        f.write(render_architectural_svg(layout_30, 'site'))

    print(f"Saved: {p_30_g}")
    print(f"Saved: {p_30_1}")
    print(f"Saved: {p_30_b}")
    print(f"Saved: {p_30_s}")

if __name__ == "__main__":
    export_all()
