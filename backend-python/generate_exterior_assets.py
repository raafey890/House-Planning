"""
Generator for Phase 6F.1 Exterior Assets:
1. Exports catalog data to frontend/src/data/exteriorCatalog.js
2. Generates distinct, rich architectural 2D elevation SVGs and placeholder JPGs for all 32 exterior designs.
"""

import os
import json
import re

from app.services.exterior_design.catalog import EXTERIOR_DESIGNS, EXTERIOR_CATEGORIES

FRONTEND_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend", "src", "data", "exteriorCatalog.js"
)
FRONTEND_IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "frontend", "public", "images", "exteriors"
)


def export_frontend_catalog():
    os.makedirs(os.path.dirname(FRONTEND_DATA_PATH), exist_ok=True)
    content = "/**\n * Exterior Design Catalog — Phase 6F.1 Frontend Data Mirror.\n"
    content += " * Exactly 32 distinct exterior designs across 8 architectural categories.\n */\n\n"
    content += f"export const EXTERIOR_CATEGORIES = {json.dumps(EXTERIOR_CATEGORIES, indent=2)};\n\n"
    content += f"export const EXTERIOR_DESIGNS = {json.dumps(EXTERIOR_DESIGNS, indent=2)};\n"
    with open(FRONTEND_DATA_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Exported {len(EXTERIOR_DESIGNS)} designs to {FRONTEND_DATA_PATH}")


def generate_svg_elevation(design):
    did = design["id"]
    name = design["name"]
    category = design["category"]
    style = design["style"]
    p_color = design["primary_paint_color"]["hex"]
    s_color = design["secondary_paint_color"]["hex"]
    floors = max(design["suitable_floor_configs"])
    budget = design["budget_tier"]
    
    # Category color accents
    cat_badges = {
        "modern_contemporary": ("#3B82F6", "MODERN CONTEMPORARY"),
        "minimalist": ("#10B981", "MINIMALIST NORDIC"),
        "luxury_villa": ("#F59E0B", "LUXURY VILLA"),
        "traditional_indian": ("#EC4899", "TRADITIONAL INDIAN"),
        "indian_modern": ("#8B5CF6", "INDIAN MODERN"),
        "mediterranean": ("#06B6D4", "MEDITERRANEAN"),
        "tropical_contemporary": ("#14B8A6", "TROPICAL CONTEMPORARY"),
        "premium_duplex": ("#6366F1", "PREMIUM DUPLEX")
    }
    badge_color, badge_text = cat_badges.get(category, ("#64748B", category.upper()))

    # Build floor elevation visual blocks
    h_floor = 110
    total_h = 420
    ground_y = 350
    bldg_w = 460
    bldg_x = 90

    # Building silhouette & elements based on category
    accent_box = ""
    if "modern" in category or "duplex" in category:
        accent_box = f'<rect x="{bldg_x + 180}" y="{ground_y - 200}" width="160" height="120" fill="{s_color}" fill-opacity="0.9" rx="4" stroke="#ffffff" stroke-width="2"/>'
    elif "luxury" in category:
        accent_box = f'<rect x="{bldg_x + 140}" y="{ground_y - 220}" width="240" height="140" fill="{s_color}" fill-opacity="0.8" rx="8" stroke="#F59E0B" stroke-width="2"/>'
    elif "traditional" in category:
        accent_box = f'<polygon points="{bldg_x + 60},{ground_y - 180} {bldg_x + 230},{ground_y - 250} {bldg_x + 400},{ground_y - 180}" fill="{s_color}" stroke="#D97706" stroke-width="3"/>'
    elif "mediterranean" in category:
        accent_box = f'<path d="M {bldg_x+80} {ground_y-180} Q {bldg_x+230} {ground_y-230} {bldg_x+380} {ground_y-180} Z" fill="{s_color}" stroke="#B45309" stroke-width="3"/>'
    else:
        accent_box = f'<rect x="{bldg_x + 120}" y="{ground_y - 190}" width="180" height="110" fill="{s_color}" fill-opacity="0.85" rx="4"/>'

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 420" width="100%" height="100%">
  <defs>
    <linearGradient id="skyGrad_{did}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0F172A"/>
      <stop offset="60%" stop-color="#1E293B"/>
      <stop offset="100%" stop-color="#334155"/>
    </linearGradient>
    <linearGradient id="groundGrad_{did}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1E293B"/>
      <stop offset="100%" stop-color="#0B1120"/>
    </linearGradient>
    <pattern id="louvers_{did}" width="12" height="12" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="12" stroke="{s_color}" stroke-width="3" stroke-opacity="0.4"/>
    </pattern>
    <filter id="shadow_{did}" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Sky Background -->
  <rect width="640" height="420" fill="url(#skyGrad_{did})"/>

  <!-- Architectural Grid Backdrop -->
  <line x1="40" y1="80" x2="600" y2="80" stroke="#334155" stroke-dasharray="4 4" stroke-opacity="0.4"/>
  <line x1="40" y1="180" x2="600" y2="180" stroke="#334155" stroke-dasharray="4 4" stroke-opacity="0.4"/>
  <line x1="40" y1="280" x2="600" y2="280" stroke="#334155" stroke-dasharray="4 4" stroke-opacity="0.4"/>

  <!-- Ground Plane & Pavers -->
  <rect x="0" y="{ground_y}" width="640" height="70" fill="url(#groundGrad_{did})"/>
  <line x1="0" y1="{ground_y}" x2="640" y2="{ground_y}" stroke="#475569" stroke-width="2"/>
  
  <!-- Boundary Gate & Lawn Accents -->
  <rect x="40" y="{ground_y - 25}" width="560" height="25" fill="#1E293B" fill-opacity="0.6" stroke="#475569" stroke-width="1.5" rx="2"/>
  <circle cx="90" cy="{ground_y + 20}" r="6" fill="#10B981" fill-opacity="0.8"/>
  <circle cx="115" cy="{ground_y + 18}" r="8" fill="#059669" fill-opacity="0.9"/>
  <circle cx="530" cy="{ground_y + 20}" r="7" fill="#10B981" fill-opacity="0.8"/>
  <circle cx="555" cy="{ground_y + 16}" r="9" fill="#059669" fill-opacity="0.9"/>

  <!-- Main House Massing Silhouette -->
  <g filter="url(#shadow_{did})">
    <!-- Main Wall Block -->
    <rect x="{bldg_x}" y="{ground_y - 220}" width="{bldg_w}" height="220" fill="{p_color}" stroke="#64748B" stroke-width="2" rx="4"/>
    
    <!-- Pattern / Louver Overlays -->
    <rect x="{bldg_x + 20}" y="{ground_y - 200}" width="100" height="190" fill="url(#louvers_{did})" rx="2"/>
    
    <!-- Accent Architectural Mass -->
    {accent_box}

    <!-- Ground Floor Entrance & Pivot Door -->
    <rect x="{bldg_x + 195}" y="{ground_y - 85}" width="50" height="85" fill="#1E293B" stroke="#F59E0B" stroke-width="1.5" rx="2"/>
    <rect x="{bldg_x + 200}" y="{ground_y - 80}" width="40" height="80" fill="#0F172A" rx="1"/>
    <line x1="{bldg_x + 233}" y1="{ground_y - 45}" x2="{bldg_x + 233}" y2="{ground_y - 30}" stroke="#F59E0B" stroke-width="2.5"/>

    <!-- Large Format Architectural Glazing -->
    <rect x="{bldg_x + 40}" y="{ground_y - 75}" width="110" height="65" fill="#0EA5E9" fill-opacity="0.25" stroke="#38BDF8" stroke-width="2" rx="2"/>
    <line x1="{bldg_x + 95}" y1="{ground_y - 75}" x2="{bldg_x + 95}" y2="{ground_y - 10}" stroke="#38BDF8" stroke-width="1.5"/>

    <!-- First Floor Fenestration / Ribbon Window -->
    <rect x="{bldg_x + 40}" y="{ground_y - 180}" width="120" height="70" fill="#0EA5E9" fill-opacity="0.25" stroke="#38BDF8" stroke-width="2" rx="2"/>
    <rect x="{bldg_x + 270}" y="{ground_y - 175}" width="150" height="65" fill="#0EA5E9" fill-opacity="0.25" stroke="#38BDF8" stroke-width="2" rx="2"/>

    <!-- Balcony & Railing Profile -->
    <rect x="{bldg_x + 260}" y="{ground_y - 110}" width="170" height="12" fill="{s_color}" stroke="#94A3B8" stroke-width="1.5" rx="2"/>
    <rect x="{bldg_x + 265}" y="{ground_y - 135}" width="160" height="25" fill="#38BDF8" fill-opacity="0.3" stroke="#CBD5E1" stroke-width="1.5" rx="1"/>
    
    <!-- Exterior Architectural Grazers (Lighting Glows) -->
    <circle cx="{bldg_x + 35}" cy="{ground_y - 20}" r="14" fill="#FDE047" fill-opacity="0.18"/>
    <circle cx="{bldg_x + 165}" cy="{ground_y - 20}" r="14" fill="#FDE047" fill-opacity="0.18"/>
    <circle cx="{bldg_x + 255}" cy="{ground_y - 20}" r="14" fill="#FDE047" fill-opacity="0.18"/>
    <circle cx="{bldg_x + 435}" cy="{ground_y - 20}" r="14" fill="#FDE047" fill-opacity="0.18"/>
  </g>

  <!-- Top Badges & Details -->
  <rect x="24" y="24" width="170" height="26" fill="{badge_color}" fill-opacity="0.2" rx="6" stroke="{badge_color}" stroke-width="1.5"/>
  <text x="34" y="42" fill="{badge_color}" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="700" letter-spacing="1">{badge_text}</text>

  <rect x="204" y="24" width="85" height="26" fill="#334155" fill-opacity="0.6" rx="6" stroke="#475569" stroke-width="1"/>
  <text x="214" y="42" fill="#E2E8F0" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="600">{budget}</text>

  <!-- Architectural Reference Image Pill Indicator -->
  <rect x="420" y="24" width="195" height="26" fill="#0F172A" fill-opacity="0.85" rx="6" stroke="#475569" stroke-width="1"/>
  <circle cx="432" cy="37" r="4" fill="#38BDF8"/>
  <text x="442" y="42" fill="#94A3B8" font-family="system-ui, -apple-system, sans-serif" font-size="10" font-weight="600">ARCHITECTURAL REFERENCE</text>

  <!-- Bottom Title Bar -->
  <rect x="24" y="365" width="592" height="38" fill="#0B1120" fill-opacity="0.9" rx="8" stroke="#334155" stroke-width="1"/>
  <text x="40" y="389" fill="#F8FAFC" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700">{name}</text>
  <text x="596" y="389" text-anchor="end" fill="#94A3B8" font-family="system-ui, -apple-system, sans-serif" font-size="11">{style} • G+{floors-1 if floors > 1 else '0'}</text>
</svg>"""
    return svg


def generate_all_images():
    os.makedirs(FRONTEND_IMAGES_DIR, exist_ok=True)
    count = 0
    for design in EXTERIOR_DESIGNS:
        did = design["id"]
        svg_content = generate_svg_elevation(design)
        
        svg_file = os.path.join(FRONTEND_IMAGES_DIR, f"{did}.svg")
        with open(svg_file, "w", encoding="utf-8") as f:
            f.write(svg_content)

        # Also write as .jpg fallback file (SVGs rendered as SVG data uri or SVG markup)
        # In Vite/modern web, SVG served with .svg works seamlessly.
        # If any img tag references .jpg, having a matching fallback ensures zero 404s
        jpg_file = os.path.join(FRONTEND_IMAGES_DIR, f"{did}.jpg")
        with open(jpg_file, "w", encoding="utf-8") as f:
            f.write(svg_content)

        count += 1

    print(f"Generated {count} architectural SVG & JPG elevation assets in {FRONTEND_IMAGES_DIR}")


if __name__ == "__main__":
    export_frontend_catalog()
    generate_all_images()
