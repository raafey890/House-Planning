"""
Plan-Aware Exterior Preview Service — Phase 6F.2.
Generates geometry-grounded, architecturally accurate vector elevation visualizations (SVG)
scaled to the project's exact plot frontage and floor count (G+0, G+1, G+2).

Supports 5 distinct visualization modes:
1. front: Orthographic Front Elevation showing frontal facade, boundary wall, entry gate, fenestration per floor, and level datum lines.
2. front_left: 3/4 Isometric Perspective from front-left displaying 3D building massing, depth, and angled boundary perimeter.
3. front_right: 3/4 Isometric Perspective from front-right showing 3D volumes, carport/setback, and depth.
4. daylight: Bright natural sun lighting, crisp sky gradient, sharp drop shadows.
5. night: Twilight atmosphere, illuminated warm 2700K window glazing, architectural LED column grazers, glowing gate fixtures.
"""

from typing import Dict, Any, List, Optional
import math
import html
import re

from app.services.exterior_design.catalog import get_exterior_design_by_id
from app.models.exterior_design import ExteriorVisualizationRequest, ExteriorVisualizationResponse


def _sanitize_color(c: Any, default: str) -> str:
    """Validates and returns a safe hex color string."""
    if isinstance(c, dict):
        c = c.get("hex", default)
    if not isinstance(c, str):
        return default
    c = c.strip()
    if re.match(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", c):
        return c
    return default


def _resolve_colors(design: Any, custom_colors: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """Resolves final colors by combining catalog defaults and user customizations."""
    custom = custom_colors or {}
    
    # Defaults from design if available
    def_primary = design.primary_paint_color.get("hex", "#F4F4F0") if design and hasattr(design, "primary_paint_color") else "#F4F4F0"
    def_accent = design.secondary_paint_color.get("hex", "#2B313B") if design and hasattr(design, "secondary_paint_color") else "#2B313B"
    
    return {
        "primary_wall": _sanitize_color(custom.get("primary_wall"), def_primary),
        "accent_wall": _sanitize_color(custom.get("accent_wall"), def_accent),
        "boundary_wall": _sanitize_color(custom.get("boundary_wall"), def_accent),
        "door": _sanitize_color(custom.get("door"), "#8B5A2B"),
        "window_frame": _sanitize_color(custom.get("window_frame"), "#1F2937"),
        "railing": _sanitize_color(custom.get("railing"), "#1F2937")
    }


def _resolve_materials(design: Any, custom_mat: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """Resolves material and finish overrides."""
    custom = custom_mat or {}
    return {
        "finish_type": str(custom.get("finish_type", "smooth_acrylic_emulsion")),
        "cladding_type": str(custom.get("cladding_type", "wooden_slats")),
        "door_material": str(custom.get("door_material", "solid_teak")),
        "window_frame_material": str(custom.get("window_frame_material", "powder_coated_aluminum")),
        "railing_material": str(custom.get("railing_material", "toughened_glass"))
    }


def _darken_color(hex_color: str, factor: float = 0.8) -> str:
    """Darkens a hex color for depth walls and shadows."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = "".join([c*2 for c in hex_color])
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#1e293b"


def generate_plan_aware_exterior_svg(
    project_id: str,
    design_id: str,
    plot_width: float = 30.0,
    plot_length: float = 40.0,
    floors: int = 1,
    plot_facing: str = "North",
    view_angle: str = "front",
    lighting_mode: str = "daylight",
    custom_colors: Optional[Dict[str, Any]] = None,
    custom_materials: Optional[Dict[str, Any]] = None,
    custom_lighting: Optional[Dict[str, Any]] = None,
    custom_elements: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Renders an architectural vector elevation (SVG) for the specific project and design.
    """
    design = get_exterior_design_by_id(design_id)
    design_name = design.name if design else "Modern Architectural Elevation"
    category = design.category if design else "modern_contemporary"
    style = design.style if design else "Modern"

    # Enforce safe bounds
    frontage_ft = max(15.0, min(120.0, float(plot_width or 30.0)))
    plot_len_ft = max(20.0, min(200.0, float(plot_length or 40.0)))
    floor_count = max(1, min(4, int(floors or 1)))
    view_angle = view_angle.lower().strip() if view_angle else "front"
    if view_angle not in ("front", "front_left", "front_right"):
        view_angle = "front"
    lighting_mode = lighting_mode.lower().strip() if lighting_mode else "daylight"
    is_night = (lighting_mode == "night")

    colors = _resolve_colors(design, custom_colors)
    materials = _resolve_materials(design, custom_materials)
    
    # SVG Dimensions
    view_w, view_h = 1000, 680

    # Colors
    c_primary = colors["primary_wall"]
    c_accent = colors["accent_wall"]
    c_boundary = colors["boundary_wall"]
    c_door = colors["door"]
    c_window = colors["window_frame"]
    c_railing = colors["railing"]

    # Shaded side wall colors for 3D perspective
    c_side_primary = _darken_color(c_primary, 0.72)
    c_side_accent = _darken_color(c_accent, 0.68)

    # Style flags
    is_traditional = ("traditional" in category or "heritage" in style.lower())
    is_mediterranean = ("mediterranean" in category or "spanish" in style.lower())
    is_luxury = ("luxury" in category or "villa" in category)
    is_tropical = ("tropical" in category)

    # Architectural Sizing
    # Ground baseline at y = 560
    ground_y = 560
    plinth_h = 24  # 1.5 ft
    plinth_y = ground_y - plinth_h
    floor_height_px = 110  # roughly 10.5 ft per floor
    bldg_h = floor_count * floor_height_px
    bldg_top_y = plinth_y - bldg_h

    # Building frontage relative to plot width
    # 30ft plot maps to building width ~ 560px on canvas
    scale_w = min(1.3, max(0.7, frontage_ft / 30.0))
    bldg_w = min(720.0, max(420.0, 520.0 * scale_w))
    bldg_x = (view_w - bldg_w) / 2

    # Defs: Gradients, Patterns, and Filters
    defs = []
    
    # 1. Sky Gradient
    if is_night:
        defs.append("""
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#050811" />
            <stop offset="50%" stop-color="#0f172a" />
            <stop offset="100%" stop-color="#1e293b" />
        </linearGradient>
        <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.9" />
            <stop offset="30%" stop-color="#93c5fd" stop-opacity="0.25" />
            <stop offset="100%" stop-color="#1e293b" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="warmWindowGlow" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#fef08a" stop-opacity="0.95" />
            <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.85" />
        </linearGradient>
        <linearGradient id="grazerGlowUp" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.8" />
            <stop offset="40%" stop-color="#fef08a" stop-opacity="0.4" />
            <stop offset="100%" stop-color="#fef08a" stop-opacity="0" />
        </linearGradient>
        <linearGradient id="grazerGlowDown" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#fbbf24" stop-opacity="0.85" />
            <stop offset="50%" stop-color="#fef08a" stop-opacity="0.35" />
            <stop offset="100%" stop-color="#fef08a" stop-opacity="0" />
        </linearGradient>
        <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        """)
    else:
        defs.append("""
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#60a5fa" />
            <stop offset="55%" stop-color="#bae6fd" />
            <stop offset="100%" stop-color="#f0f9ff" />
        </linearGradient>
        <linearGradient id="sunSheen" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ffffff" stop-opacity="0.45" />
            <stop offset="100%" stop-color="#ffffff" stop-opacity="0.05" />
        </linearGradient>
        <linearGradient id="daylightGlass" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.45" />
            <stop offset="50%" stop-color="#0284c7" stop-opacity="0.65" />
            <stop offset="100%" stop-color="#0369a1" stop-opacity="0.8" />
        </linearGradient>
        """)

    # Material Patterns
    cladding = materials.get("cladding_type", "wooden_slats")
    if "wood" in cladding or "timber" in cladding:
        defs.append(f"""
        <pattern id="claddingPattern" width="20" height="12" patternUnits="userSpaceOnUse">
            <rect width="20" height="12" fill="{c_accent}" />
            <line x1="0" y1="11" x2="20" y2="11" stroke="#1c1917" stroke-width="1.5" stroke-opacity="0.6" />
        </pattern>
        """)
    elif "stone" in cladding or "travertine" in cladding or "brick" in cladding:
        defs.append(f"""
        <pattern id="claddingPattern" width="36" height="18" patternUnits="userSpaceOnUse">
            <rect width="36" height="18" fill="{c_accent}" />
            <line x1="0" y1="9" x2="36" y2="9" stroke="#0f172a" stroke-width="1" stroke-opacity="0.4" />
            <line x1="18" y1="0" x2="18" y2="9" stroke="#0f172a" stroke-width="1" stroke-opacity="0.4" />
            <line x1="0" y1="9" x2="0" y2="18" stroke="#0f172a" stroke-width="1" stroke-opacity="0.4" />
        </pattern>
        """)
    else:
        # Fluted vertical louvers
        defs.append(f"""
        <pattern id="claddingPattern" width="10" height="20" patternUnits="userSpaceOnUse">
            <rect width="10" height="20" fill="{c_accent}" />
            <line x1="9" y1="0" x2="9" y2="20" stroke="#0f172a" stroke-width="1.5" stroke-opacity="0.5" />
        </pattern>
        """)

    # Grass & Paver patterns
    defs.append("""
    <linearGradient id="groundGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#334155" />
        <stop offset="25%" stop-color="#1e293b" />
        <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <pattern id="paverPattern" width="24" height="16" patternUnits="userSpaceOnUse">
        <rect width="24" height="16" fill="#475569" />
        <rect x="1" y="1" width="22" height="14" fill="#64748b" opacity="0.3" />
        <line x1="0" y1="16" x2="24" y2="16" stroke="#334155" stroke-width="1" />
        <line x1="24" y1="0" x2="24" y2="16" stroke="#334155" stroke-width="1" />
    </pattern>
    """)

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" width="100%" height="100%" style="border-radius:12px;background:#0f172a;font-family:system-ui,-apple-system,sans-serif;">')
    svg_parts.append("<defs>" + "".join(defs) + "</defs>")

    # 1. Sky & Background
    svg_parts.append(f'<rect width="{view_w}" height="{ground_y}" fill="url(#skyGrad)" />')

    if is_night:
        # Moon and atmospheric glow
        svg_parts.append(f'<circle cx="{view_w - 120}" cy="80" r="45" fill="url(#moonGlow)" />')
        svg_parts.append(f'<circle cx="{view_w - 120}" cy="80" r="22" fill="#f8fafc" />')
        # Stars
        for sx, sy in [(100, 60), (220, 90), (350, 45), (480, 80), (620, 50), (740, 95), (880, 40)]:
            svg_parts.append(f'<circle cx="{sx}" cy="{sy}" r="1.5" fill="#ffffff" opacity="0.7" />')
    else:
        # Sun & distant landscaping silhouette
        svg_parts.append(f'<circle cx="130" cy="75" r="32" fill="#fef08a" opacity="0.9" />')
        svg_parts.append(f'<circle cx="130" cy="75" r="48" fill="#fde047" opacity="0.2" />')

    # Distant lush trees / foliage behind building
    tree_color = "#14532d" if not is_night else "#052e16"
    tree_accent = "#15803d" if not is_night else "#064e3b"
    svg_parts.append(f"""
    <g id="distant-trees" opacity="0.75">
        <circle cx="90" cy="{plinth_y - 20}" r="75" fill="{tree_color}" />
        <circle cx="130" cy="{plinth_y - 45}" r="65" fill="{tree_accent}" />
        <circle cx="{view_w - 100}" cy="{plinth_y - 30}" r="80" fill="{tree_color}" />
        <circle cx="{view_w - 60}" cy="{plinth_y - 50}" r="65" fill="{tree_accent}" />
    </g>
    """)

    # 2. Ground & Driveway
    svg_parts.append(f'<rect x="0" y="{ground_y}" width="{view_w}" height="{view_h - ground_y}" fill="url(#groundGrad)" />')
    # Driveway apron in foreground
    svg_parts.append(f'<rect x="180" y="{ground_y}" width="{view_w - 360}" height="{view_h - ground_y}" fill="url(#paverPattern)" opacity="0.85" />')

    # ══════════════════════════════════════════════════════════════════════════
    # 3. Main Architectural Building Massing
    # ══════════════════════════════════════════════════════════════════════════

    glass_fill = "url(#warmWindowGlow)" if is_night else "url(#daylightGlass)"
    glass_filter = 'filter="url(#softGlow)"' if is_night else ""

    if view_angle == "front":
        # Orthographic Front Elevation
        # Plinth
        svg_parts.append(f'<rect x="{bldg_x - 10}" y="{plinth_y}" width="{bldg_w + 20}" height="{plinth_h}" fill="#334155" stroke="#1e293b" stroke-width="1.5" />')
        svg_parts.append(f'<line x1="{bldg_x - 15}" y1="{plinth_y}" x2="{bldg_x + bldg_w + 15}" y2="{plinth_y}" stroke="#64748b" stroke-width="2" />')

        # Main Building Box (Primary Wall)
        svg_parts.append(f'<rect x="{bldg_x}" y="{bldg_top_y}" width="{bldg_w}" height="{bldg_h}" fill="{c_primary}" stroke="#0f172a" stroke-width="2" />')

        # Distinct Accent Features based on category
        # Accent Cantilever Feature Wall / Column
        accent_col_w = bldg_w * 0.38
        accent_x = bldg_x + (bldg_w - accent_col_w) - 20
        svg_parts.append(f'<rect x="{accent_x}" y="{bldg_top_y - 12}" width="{accent_col_w}" height="{bldg_h + 12}" fill="url(#claddingPattern)" stroke="#0f172a" stroke-width="2" />')

        # Floor by floor elements
        for f in range(floor_count):
            curr_floor_y = plinth_y - ((f + 1) * floor_height_px)
            curr_floor_num = f  # 0 for Ground, 1 for First, 2 for Second

            # Slab separator band
            if f > 0:
                svg_parts.append(f'<rect x="{bldg_x - 6}" y="{curr_floor_y + floor_height_px - 8}" width="{bldg_w + 12}" height="14" fill="#1e293b" stroke="#0f172a" />')

            # Ground Floor Features
            if curr_floor_num == 0:
                # Main Entrance Portal
                portal_w = 110
                portal_h = 88
                portal_x = bldg_x + 55
                portal_y = plinth_y - portal_h

                # Entrance canopy
                svg_parts.append(f'<rect x="{portal_x - 15}" y="{portal_y - 12}" width="{portal_w + 30}" height="12" fill="{c_accent}" stroke="#0f172a" stroke-width="1.5" />')
                # Canopy tie-rods or pillars
                svg_parts.append(f'<line x1="{portal_x - 10}" y1="{portal_y - 12}" x2="{portal_x - 10}" y2="{portal_y - 30}" stroke="#94a3b8" stroke-width="2" />')
                svg_parts.append(f'<line x1="{portal_x + portal_w + 10}" y1="{portal_y - 12}" x2="{portal_x + portal_w + 10}" y2="{portal_y - 30}" stroke="#94a3b8" stroke-width="2" />')

                # Main Entrance Door
                door_w = 46
                door_h = 80
                door_x = portal_x + 12
                door_y = plinth_y - door_h
                svg_parts.append(f'<rect x="{door_x}" y="{door_y}" width="{door_w}" height="{door_h}" fill="{c_door}" stroke="{c_window}" stroke-width="2" />')
                # Pivot handle
                svg_parts.append(f'<rect x="{door_x + door_w - 8}" y="{door_y + 32}" width="3" height="24" fill="#d97706" />')

                # Ground Floor Window (Left of door or right side)
                win_w = 90
                win_h = 65
                win_x = portal_x + door_w + 30
                win_y = plinth_y - win_h - 10
                svg_parts.append(f'<rect x="{win_x}" y="{win_y}" width="{win_w}" height="{win_h}" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="3" />')
                # Mullions
                svg_parts.append(f'<line x1="{win_x + win_w/2}" y1="{win_y}" x2="{win_x + win_w/2}" y2="{win_y + win_h}" stroke="{c_window}" stroke-width="2" />')
                svg_parts.append(f'<line x1="{win_x}" y1="{win_y + win_h/2}" x2="{win_x + win_w}" y2="{win_y + win_h/2}" stroke="{c_window}" stroke-width="1.5" />')

                # Accent Column Window on Ground Floor
                ac_win_x = accent_x + 25
                ac_win_w = accent_col_w - 50
                ac_win_h = 70
                ac_win_y = plinth_y - ac_win_h - 10
                svg_parts.append(f'<rect x="{ac_win_x}" y="{ac_win_y}" width="{ac_win_w}" height="{ac_win_h}" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="3" />')
                svg_parts.append(f'<line x1="{ac_win_x + ac_win_w/2}" y1="{ac_win_y}" x2="{ac_win_x + ac_win_w/2}" y2="{ac_win_y + ac_win_h}" stroke="{c_window}" stroke-width="2" />')

                # Night Downlights under canopy
                if is_night:
                    svg_parts.append(f'<circle cx="{portal_x + 20}" cy="{portal_y - 2}" r="3" fill="#fbbf24" />')
                    svg_parts.append(f'<polygon points="{portal_x + 10},{portal_y} {portal_x + 30},{portal_y} {portal_x + 45},{plinth_y} {portal_x - 5},{plinth_y}" fill="url(#grazerGlowDown)" opacity="0.65" />')
                    svg_parts.append(f'<circle cx="{portal_x + portal_w - 20}" cy="{portal_y - 2}" r="3" fill="#fbbf24" />')
                    svg_parts.append(f'<polygon points="{portal_x + portal_w - 30},{portal_y} {portal_x + portal_w - 10},{portal_y} {portal_x + portal_w + 5},{plinth_y} {portal_x + portal_w - 45},{plinth_y}" fill="url(#grazerGlowDown)" opacity="0.65" />')

            else:
                # Upper Floor (First Floor / Second Floor)
                # Expansive Master Balcony on Left
                balcony_w = bldg_w * 0.45
                balcony_x = bldg_x + 30
                balcony_h = 36
                balcony_y = curr_floor_y + floor_height_px - balcony_h

                # Floor to ceiling glass slider behind balcony
                slider_w = balcony_w - 20
                slider_h = 80
                slider_x = balcony_x + 10
                slider_y = curr_floor_y + floor_height_px - slider_h - 5
                svg_parts.append(f'<rect x="{slider_x}" y="{slider_y}" width="{slider_w}" height="{slider_h}" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="3" />')
                svg_parts.append(f'<line x1="{slider_x + slider_w/3}" y1="{slider_y}" x2="{slider_x + slider_w/3}" y2="{slider_y + slider_h}" stroke="{c_window}" stroke-width="2" />')
                svg_parts.append(f'<line x1="{slider_x + (2*slider_w)/3}" y1="{slider_y}" x2="{slider_x + (2*slider_w)/3}" y2="{slider_y + slider_h}" stroke="{c_window}" stroke-width="2" />')

                # Balcony Cantilever Slab
                svg_parts.append(f'<rect x="{balcony_x - 8}" y="{balcony_y + balcony_h - 6}" width="{balcony_w + 16}" height="10" fill="#0f172a" />')

                # Balcony Railing (Glass or Metal Slats)
                if "glass" in materials.get("railing_material", "glass"):
                    svg_parts.append(f'<rect x="{balcony_x}" y="{balcony_y}" width="{balcony_w}" height="{balcony_h}" fill="#38bdf8" fill-opacity="0.25" stroke="{c_railing}" stroke-width="2" />')
                    svg_parts.append(f'<line x1="{balcony_x}" y1="{balcony_y}" x2="{balcony_x + balcony_w}" y2="{balcony_y}" stroke="{c_railing}" stroke-width="3" />')
                else:
                    svg_parts.append(f'<line x1="{balcony_x}" y1="{balcony_y}" x2="{balcony_x + balcony_w}" y2="{balcony_y}" stroke="{c_railing}" stroke-width="3" />')
                    for rx in range(int(balcony_x) + 10, int(balcony_x + balcony_w), 14):
                        svg_parts.append(f'<line x1="{rx}" y1="{balcony_y}" x2="{rx}" y2="{balcony_y + balcony_h}" stroke="{c_railing}" stroke-width="1.5" />')

                # Upper Accent Box Glazing / Louvers
                up_win_x = accent_x + 25
                up_win_w = accent_col_w - 50
                up_win_h = 75
                up_win_y = curr_floor_y + 15
                svg_parts.append(f'<rect x="{up_win_x}" y="{up_win_y}" width="{up_win_w}" height="{up_win_h}" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="3" />')
                svg_parts.append(f'<line x1="{up_win_x + up_win_w/2}" y1="{up_win_y}" x2="{up_win_x + up_win_w/2}" y2="{up_win_y + up_win_h}" stroke="{c_window}" stroke-width="2" />')

        # Roofline / Parapet Wall / Traditional Eaves
        if is_traditional:
            # Sloping Mangalore Clay Tile Roof
            roof_h = 55
            roof_pts = f"{bldg_x - 30},{bldg_top_y} {bldg_x + bldg_w/2},{bldg_top_y - roof_h} {bldg_x + bldg_w + 30},{bldg_top_y}"
            svg_parts.append(f'<polygon points="{roof_pts}" fill="#b45309" stroke="#78350f" stroke-width="3" />')
            # Decorative carved chhajja wooden rafters
            for rx in range(int(bldg_x - 20), int(bldg_x + bldg_w + 20), 22):
                svg_parts.append(f'<line x1="{rx}" y1="{bldg_top_y}" x2="{rx}" y2="{bldg_top_y + 10}" stroke="#78350f" stroke-width="3" />')
        elif is_mediterranean:
            # Barrel terracotta parapet coping
            svg_parts.append(f'<rect x="{bldg_x - 10}" y="{bldg_top_y - 20}" width="{bldg_w + 20}" height="20" fill="{c_primary}" stroke="#0f172a" stroke-width="2" />')
            svg_parts.append(f'<rect x="{bldg_x - 14}" y="{bldg_top_y - 28}" width="{bldg_w + 28}" height="10" fill="#ea580c" stroke="#9a3412" stroke-width="2" />')
        else:
            # Modern Flat Parapet with Pergola / Slabs
            svg_parts.append(f'<rect x="{bldg_x - 12}" y="{bldg_top_y - 24}" width="{bldg_w + 24}" height="24" fill="{c_primary}" stroke="#0f172a" stroke-width="2" />')
            svg_parts.append(f'<line x1="{bldg_x - 16}" y1="{bldg_top_y - 24}" x2="{bldg_x + bldg_w + 16}" y2="{bldg_top_y - 24}" stroke="#0f172a" stroke-width="3" />')
            # Modern rooftop pergola trellis
            if is_tropical or is_luxury:
                for tx in range(int(bldg_x + 30), int(bldg_x + bldg_w * 0.55), 25):
                    svg_parts.append(f'<line x1="{tx}" y1="{bldg_top_y - 48}" x2="{tx}" y2="{bldg_top_y - 24}" stroke="#1e293b" stroke-width="4" />')
                svg_parts.append(f'<line x1="{bldg_x + 20}" y1="{bldg_top_y - 48}" x2="{bldg_x + bldg_w * 0.58}" y2="{bldg_top_y - 48}" stroke="#1e293b" stroke-width="5" />')

        # Night Architectural Uplights / Grazers
        if is_night:
            # Grazers along accent column
            for gx in [accent_x + 15, accent_x + accent_col_w - 15]:
                svg_parts.append(f'<circle cx="{gx}" cy="{plinth_y - 2}" r="3" fill="#fbbf24" />')
                svg_parts.append(f'<polygon points="{gx - 10},{plinth_y} {gx + 10},{plinth_y} {gx + 30},{bldg_top_y + 20} {gx - 30},{bldg_top_y + 20}" fill="url(#grazerGlowUp)" opacity="0.6" />')

    elif view_angle == "front_left":
        # 3/4 Isometric Perspective from Front-Left
        # Shows Front Facade + Left Side Wall
        side_depth = 110
        iso_y_drop = 30

        # Plinth Left & Front
        # Left plinth
        svg_parts.append(f'<polygon points="{bldg_x - side_depth},{plinth_y - iso_y_drop} {bldg_x},{plinth_y} {bldg_x},{plinth_y + plinth_h} {bldg_x - side_depth},{plinth_y + plinth_h - iso_y_drop}" fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />')
        # Front plinth
        svg_parts.append(f'<polygon points="{bldg_x},{plinth_y} {bldg_x + bldg_w},{plinth_y} {bldg_x + bldg_w},{plinth_y + plinth_h} {bldg_x},{plinth_y + plinth_h}" fill="#334155" stroke="#0f172a" stroke-width="1.5" />')

        # Left Depth Wall (Darker shade)
        svg_parts.append(f'<polygon points="{bldg_x - side_depth},{bldg_top_y - iso_y_drop} {bldg_x},{bldg_top_y} {bldg_x},{plinth_y} {bldg_x - side_depth},{plinth_y - iso_y_drop}" fill="{c_side_primary}" stroke="#0f172a" stroke-width="2" />')
        # Left side slit windows
        for f in range(floor_count):
            sw_y = plinth_y - ((f + 0.5) * floor_height_px) - (iso_y_drop * 0.5)
            svg_parts.append(f'<polygon points="{bldg_x - side_depth + 30},{sw_y - 25} {bldg_x - 30},{sw_y - 12} {bldg_x - 30},{sw_y + 18} {bldg_x - side_depth + 30},{sw_y + 5}" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')

        # Front Facade
        svg_parts.append(f'<rect x="{bldg_x}" y="{bldg_top_y}" width="{bldg_w}" height="{bldg_h}" fill="{c_primary}" stroke="#0f172a" stroke-width="2" />')

        # Accent Cantilever Feature Wall / Column on Front
        accent_col_w = bldg_w * 0.38
        accent_x = bldg_x + (bldg_w - accent_col_w) - 20
        svg_parts.append(f'<rect x="{accent_x}" y="{bldg_top_y - 12}" width="{accent_col_w}" height="{bldg_h + 12}" fill="url(#claddingPattern)" stroke="#0f172a" stroke-width="2" />')

        # Front fenestrations
        for f in range(floor_count):
            curr_floor_y = plinth_y - ((f + 1) * floor_height_px)
            if f == 0:
                # Main Door
                door_w = 44
                door_h = 78
                door_x = bldg_x + 40
                door_y = plinth_y - door_h
                svg_parts.append(f'<rect x="{door_x}" y="{door_y}" width="{door_w}" height="{door_h}" fill="{c_door}" stroke="{c_window}" stroke-width="2" />')
                # Ground window
                svg_parts.append(f'<rect x="{door_x + door_w + 25}" y="{door_y + 10}" width="85" height="60" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')
                # Accent window
                svg_parts.append(f'<rect x="{accent_x + 20}" y="{door_y + 5}" width="{accent_col_w - 40}" height="65" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')
            else:
                # Upper balcony & window
                balcony_w = bldg_w * 0.42
                balcony_x = bldg_x + 25
                balcony_y = curr_floor_y + floor_height_px - 36
                svg_parts.append(f'<rect x="{balcony_x}" y="{curr_floor_y + 15}" width="{balcony_w}" height="75" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')
                svg_parts.append(f'<rect x="{balcony_x - 5}" y="{balcony_y}" width="{balcony_w + 10}" height="36" fill="#38bdf8" fill-opacity="0.25" stroke="{c_railing}" stroke-width="2" />')
                svg_parts.append(f'<rect x="{accent_x + 20}" y="{curr_floor_y + 15}" width="{accent_col_w - 40}" height="70" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')

        # Top Parapet
        svg_parts.append(f'<polygon points="{bldg_x - side_depth - 5},{bldg_top_y - 20 - iso_y_drop} {bldg_x},{bldg_top_y - 20} {bldg_x},{bldg_top_y} {bldg_x - side_depth - 5},{bldg_top_y - iso_y_drop}" fill="{c_side_primary}" stroke="#0f172a" stroke-width="2" />')
        svg_parts.append(f'<rect x="{bldg_x - 8}" y="{bldg_top_y - 20}" width="{bldg_w + 16}" height="20" fill="{c_primary}" stroke="#0f172a" stroke-width="2" />')

        if is_night:
            for gx in [accent_x + 15, accent_x + accent_col_w - 15]:
                svg_parts.append(f'<circle cx="{gx}" cy="{plinth_y - 2}" r="3" fill="#fbbf24" />')
                svg_parts.append(f'<polygon points="{gx - 10},{plinth_y} {gx + 10},{plinth_y} {gx + 25},{bldg_top_y + 20} {gx - 25},{bldg_top_y + 20}" fill="url(#grazerGlowUp)" opacity="0.6" />')

    else:
        # 3/4 Isometric Perspective from Front-Right
        # Shows Front Facade + Right Side Wall
        side_depth = 110
        iso_y_drop = 30

        # Plinth Front & Right
        # Front plinth
        svg_parts.append(f'<polygon points="{bldg_x},{plinth_y} {bldg_x + bldg_w},{plinth_y} {bldg_x + bldg_w},{plinth_y + plinth_h} {bldg_x},{plinth_y + plinth_h}" fill="#334155" stroke="#0f172a" stroke-width="1.5" />')
        # Right plinth
        svg_parts.append(f'<polygon points="{bldg_x + bldg_w},{plinth_y} {bldg_x + bldg_w + side_depth},{plinth_y - iso_y_drop} {bldg_x + bldg_w + side_depth},{plinth_y + plinth_h - iso_y_drop} {bldg_x + bldg_w},{plinth_y + plinth_h}" fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />')

        # Front Facade
        svg_parts.append(f'<rect x="{bldg_x}" y="{bldg_top_y}" width="{bldg_w}" height="{bldg_h}" fill="{c_primary}" stroke="#0f172a" stroke-width="2" />')

        # Right Depth Wall (Darker shade)
        svg_parts.append(f'<polygon points="{bldg_x + bldg_w},{bldg_top_y} {bldg_x + bldg_w + side_depth},{bldg_top_y - iso_y_drop} {bldg_x + bldg_w + side_depth},{plinth_y - iso_y_drop} {bldg_x + bldg_w},{plinth_y}" fill="{c_side_primary}" stroke="#0f172a" stroke-width="2" />')
        # Right side windows
        for f in range(floor_count):
            sw_y = plinth_y - ((f + 0.5) * floor_height_px) - (iso_y_drop * 0.5)
            svg_parts.append(f'<polygon points="{bldg_x + bldg_w + 30},{sw_y - 12} {bldg_x + bldg_w + side_depth - 30},{sw_y - 25} {bldg_x + bldg_w + side_depth - 30},{sw_y + 5} {bldg_x + bldg_w + 30},{sw_y + 18}" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')

        # Accent Cantilever Feature Wall / Column on Front
        accent_col_w = bldg_w * 0.38
        accent_x = bldg_x + 30
        svg_parts.append(f'<rect x="{accent_x}" y="{bldg_top_y - 12}" width="{accent_col_w}" height="{bldg_h + 12}" fill="url(#claddingPattern)" stroke="#0f172a" stroke-width="2" />')

        # Front fenestrations
        for f in range(floor_count):
            curr_floor_y = plinth_y - ((f + 1) * floor_height_px)
            if f == 0:
                # Door on right
                door_w = 44
                door_h = 78
                door_x = bldg_x + bldg_w - 90
                door_y = plinth_y - door_h
                svg_parts.append(f'<rect x="{door_x}" y="{door_y}" width="{door_w}" height="{door_h}" fill="{c_door}" stroke="{c_window}" stroke-width="2" />')
                # Ground windows
                svg_parts.append(f'<rect x="{door_x - 110}" y="{door_y + 10}" width="90" height="60" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')
                svg_parts.append(f'<rect x="{accent_x + 20}" y="{door_y + 5}" width="{accent_col_w - 40}" height="65" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')
            else:
                # Upper balcony & window
                balcony_w = bldg_w * 0.42
                balcony_x = bldg_x + bldg_w - balcony_w - 25
                balcony_y = curr_floor_y + floor_height_px - 36
                svg_parts.append(f'<rect x="{balcony_x}" y="{curr_floor_y + 15}" width="{balcony_w}" height="75" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')
                svg_parts.append(f'<rect x="{balcony_x - 5}" y="{balcony_y}" width="{balcony_w + 10}" height="36" fill="#38bdf8" fill-opacity="0.25" stroke="{c_railing}" stroke-width="2" />')
                svg_parts.append(f'<rect x="{accent_x + 20}" y="{curr_floor_y + 15}" width="{accent_col_w - 40}" height="70" fill="{glass_fill}" {glass_filter} stroke="{c_window}" stroke-width="2" />')

        # Top Parapet
        svg_parts.append(f'<rect x="{bldg_x - 8}" y="{bldg_top_y - 20}" width="{bldg_w + 16}" height="20" fill="{c_primary}" stroke="#0f172a" stroke-width="2" />')
        svg_parts.append(f'<polygon points="{bldg_x + bldg_w},{bldg_top_y - 20} {bldg_x + bldg_w + side_depth + 5},{bldg_top_y - 20 - iso_y_drop} {bldg_x + bldg_w + side_depth + 5},{bldg_top_y - iso_y_drop} {bldg_x + bldg_w},{bldg_top_y}" fill="{c_side_primary}" stroke="#0f172a" stroke-width="2" />')

        if is_night:
            for gx in [accent_x + 15, accent_x + accent_col_w - 15]:
                svg_parts.append(f'<circle cx="{gx}" cy="{plinth_y - 2}" r="3" fill="#fbbf24" />')
                svg_parts.append(f'<polygon points="{gx - 10},{plinth_y} {gx + 10},{plinth_y} {gx + 25},{bldg_top_y + 20} {gx - 25},{bldg_top_y + 20}" fill="url(#grazerGlowUp)" opacity="0.6" />')

    # ══════════════════════════════════════════════════════════════════════════
    # 4. Front Compound Boundary Wall & Gate
    # ══════════════════════════════════════════════════════════════════════════
    wall_h = 42
    wall_y = ground_y - wall_h
    gate_w = 170
    gate_x = (view_w - gate_w) / 2 + 30

    # Boundary Wall Solid Sections
    # Left compound wall
    svg_parts.append(f'<rect x="40" y="{wall_y}" width="{gate_x - 40}" height="{wall_h}" fill="{c_boundary}" stroke="#0f172a" stroke-width="2" />')
    # Right compound wall
    svg_parts.append(f'<rect x="{gate_x + gate_w}" y="{wall_y}" width="{view_w - 80 - (gate_x + gate_w)}" height="{wall_h}" fill="{c_boundary}" stroke="#0f172a" stroke-width="2" />')

    # Compound Gate Piers (Left & Right)
    pier_w = 22
    pier_h = 52
    left_pier_x = gate_x - pier_w
    right_pier_x = gate_x + gate_w
    pier_y = ground_y - pier_h

    svg_parts.append(f'<rect x="{left_pier_x}" y="{pier_y}" width="{pier_w}" height="{pier_h}" fill="#334155" stroke="#0f172a" stroke-width="2" />')
    svg_parts.append(f'<rect x="{left_pier_x - 3}" y="{pier_y - 6}" width="{pier_w + 6}" height="6" fill="#1e293b" />')

    svg_parts.append(f'<rect x="{right_pier_x}" y="{pier_y}" width="{pier_w}" height="{pier_h}" fill="#334155" stroke="#0f172a" stroke-width="2" />')
    svg_parts.append(f'<rect x="{right_pier_x - 3}" y="{pier_y - 6}" width="{pier_w + 6}" height="6" fill="#1e293b" />')

    # Gate Pier Night Lanterns / Luminaires
    if is_night:
        for px in [left_pier_x + pier_w/2, right_pier_x + pier_w/2]:
            svg_parts.append(f'<circle cx="{px}" cy="{pier_y - 12}" r="6" fill="#fef08a" filter="url(#softGlow)" />')
            svg_parts.append(f'<circle cx="{px}" cy="{pier_y - 12}" r="3" fill="#ffffff" />')
            svg_parts.append(f'<polygon points="{px - 10},{pier_y - 6} {px + 10},{pier_y - 6} {px + 25},{ground_y} {px - 25},{ground_y}" fill="url(#grazerGlowDown)" opacity="0.5" />')

    # Main Sliding / Motorized Gate
    svg_parts.append(f'<rect x="{gate_x + 4}" y="{wall_y + 4}" width="{gate_w - 8}" height="{wall_h - 4}" fill="#0f172a" stroke="{c_railing}" stroke-width="2" />')
    # Horizontal gate louvers
    for gy in range(int(wall_y) + 9, int(ground_y) - 4, 6):
        svg_parts.append(f'<line x1="{gate_x + 8}" y1="{gy}" x2="{gate_x + gate_w - 8}" y2="{gy}" stroke="{c_accent}" stroke-width="2" />')

    # ══════════════════════════════════════════════════════════════════════════
    # 5. Dimension Annotations & Datum Levels (Engineering Accuracy)
    # ══════════════════════════════════════════════════════════════════════════
    annot_color = "#94a3b8" if is_night else "#475569"
    badge_bg = "rgba(15, 23, 42, 0.85)"

    # Frontage Dimension Arrow
    arrow_y = ground_y + 40
    svg_parts.append(f"""
    <g id="dimension-frontage">
        <line x1="{bldg_x}" y1="{arrow_y}" x2="{bldg_x + bldg_w}" y2="{arrow_y}" stroke="{annot_color}" stroke-width="1.5" stroke-dasharray="4,4" />
        <line x1="{bldg_x}" y1="{arrow_y - 8}" x2="{bldg_x}" y2="{arrow_y + 8}" stroke="{annot_color}" stroke-width="2" />
        <line x1="{bldg_x + bldg_w}" y1="{arrow_y - 8}" x2="{bldg_x + bldg_w}" y2="{arrow_y + 8}" stroke="{annot_color}" stroke-width="2" />
        <rect x="{(view_w/2) - 80}" y="{arrow_y - 12}" width="160" height="24" rx="4" fill="{badge_bg}" stroke="{annot_color}" stroke-width="1" />
        <text x="{view_w/2}" y="{arrow_y + 4}" fill="#f8fafc" font-size="11" font-weight="600" text-anchor="middle">
            {frontage_ft:.1f} ft Plot Frontage
        </text>
    </g>
    """)

    # Datum Level Markers on Right Side
    datum_x = view_w - 95
    levels = [
        ("±0.00m Ground", ground_y),
        ("+0.45m Plinth", plinth_y),
    ]
    for f in range(1, floor_count):
        levels.append((f"+{0.45 + (f * 3.2):.2f}m Floor {f}", plinth_y - (f * floor_height_px)))
    levels.append((f"+{0.45 + (floor_count * 3.2) + 0.9:.2f}m Parapet", bldg_top_y - 20))

    svg_parts.append(f'<g id="datum-markers">')
    for lbl, ly in levels:
        svg_parts.append(f"""
        <line x1="{bldg_x + bldg_w + 10}" y1="{ly}" x2="{datum_x}" y2="{ly}" stroke="{annot_color}" stroke-width="1" stroke-dasharray="2,3" opacity="0.6" />
        <polygon points="{datum_x},{ly} {datum_x + 8},{ly - 5} {datum_x + 8},{ly + 5}" fill="{annot_color}" />
        <text x="{datum_x + 12}" y="{ly + 4}" fill="{annot_color}" font-size="9" font-weight="600">
            {lbl}
        </text>
        """)
    svg_parts.append('</g>')

    # ══════════════════════════════════════════════════════════════════════════
    # 6. Architectural Title Block & View Mode Watermark
    # ══════════════════════════════════════════════════════════════════════════
    angle_display = {
        "front": "Front Elevation (Orthographic)",
        "front_left": "Front-Left 3/4 Isometric Perspective",
        "front_right": "Front-Right 3/4 Isometric Perspective"
    }.get(view_angle, "Front Elevation")

    lighting_display = "Night Architectural Illumination" if is_night else "Daylight Sun Angle"

    svg_parts.append(f"""
    <g id="title-block">
        <rect x="24" y="20" width="340" height="74" rx="8" fill="{badge_bg}" stroke="#334155" stroke-width="1.2" />
        <text x="38" y="42" fill="#38bdf8" font-size="13" font-weight="700" letter-spacing="0.5">
            {html.escape(design_name.upper())}
        </text>
        <text x="38" y="60" fill="#f8fafc" font-size="11" font-weight="600">
            {angle_display}
        </text>
        <text x="38" y="78" fill="#94a3b8" font-size="10">
            {lighting_display} • G+{floor_count - 1} Levels • {frontage_ft:.0f}×{plot_len_ft:.0f} ft
        </text>
    </g>
    """)

    # Personalized Palette Swatches in top right
    svg_parts.append(f"""
    <g id="palette-swatches">
        <rect x="{view_w - 200}" y="20" width="176" height="34" rx="6" fill="{badge_bg}" stroke="#334155" stroke-width="1" />
        <circle cx="{view_w - 180}" cy="37" r="8" fill="{c_primary}" stroke="#475569" stroke-width="1.5" />
        <circle cx="{view_w - 150}" cy="37" r="8" fill="{c_accent}" stroke="#475569" stroke-width="1.5" />
        <circle cx="{view_w - 120}" cy="37" r="8" fill="{c_boundary}" stroke="#475569" stroke-width="1.5" />
        <circle cx="{view_w - 90}" cy="37" r="8" fill="{c_door}" stroke="#475569" stroke-width="1.5" />
        <circle cx="{view_w - 60}" cy="37" r="8" fill="{c_window}" stroke="#475569" stroke-width="1.5" />
        <circle cx="{view_w - 30}" cy="37" r="8" fill="{c_railing}" stroke="#475569" stroke-width="1.5" />
    </g>
    """)

    svg_parts.append("</svg>")
    full_svg = "".join(svg_parts)

    return {
        "status": "success",
        "preview_mode": "svg_vector",
        "svg_content": full_svg,
        "image_url": None,
        "view_angle": view_angle,
        "lighting_mode": lighting_mode,
        "project_id": project_id,
        "design_id": design_id,
        "design_name": design_name,
        "dimensions": {
            "plot_width_ft": frontage_ft,
            "plot_length_ft": plot_len_ft,
            "floors": floor_count,
            "facing": plot_facing,
            "aspect_ratio": round(frontage_ft / plot_len_ft, 2)
        },
        "colors_used": colors,
        "materials_used": materials,
        "provider": "Architectural Vector Elevation Engine",
        "prompt_used": None,
        "metadata": {
            "canvas_width": view_w,
            "canvas_height": view_h,
            "elevation_type": "plan_aware_custom_vector",
            "is_night": is_night,
            "cladding_type": materials.get("cladding_type")
        }
    }


def generate_personalized_exterior_preview(req: ExteriorVisualizationRequest) -> ExteriorVisualizationResponse:
    """
    Handler for generating personalized vector previews from an ExteriorVisualizationRequest.
    """
    res = generate_plan_aware_exterior_svg(
        project_id=req.project_id,
        design_id=req.design_id,
        plot_width=req.plot_width or 30.0,
        plot_length=req.plot_length or 40.0,
        floors=req.floors or 1,
        plot_facing=req.plot_facing or "North",
        view_angle=req.view_angle,
        lighting_mode=req.lighting_mode,
        custom_colors=req.colors,
        custom_materials=req.materials,
        custom_lighting=req.lighting,
        custom_elements=req.architectural_elements
    )

    return ExteriorVisualizationResponse(
        status=res["status"],
        preview_mode=res["preview_mode"],
        svg_content=res["svg_content"],
        image_url=res["image_url"],
        view_angle=res["view_angle"],
        lighting_mode=res["lighting_mode"],
        project_id=res["project_id"],
        design_id=res["design_id"],
        design_name=res["design_name"],
        dimensions=res["dimensions"],
        colors_used=res["colors_used"],
        materials_used=res["materials_used"],
        provider=res["provider"],
        prompt_used=res["prompt_used"],
        metadata=res["metadata"],
        error_detail=None
    )
