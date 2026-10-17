"""
Generates 32 distinct, high-quality, architectural interior design preview SVGs
in frontend/public/images/interiors/.
Each SVG has an 800x500 viewBox, rich gradients, specific color palettes,
architectural elevation/perspective geometry, materials (marble, wood slats, tiles, fabrics),
lighting fixtures with glows, and a stylish interior design badge.
Exact categories:
  - Bedroom (8): int_bed_01 .. int_bed_08
  - Living Room (6): int_lr_01 .. int_lr_06
  - Kitchen (6): int_kit_01 .. int_kit_06
  - Guest Room (4): int_guest_01 .. int_guest_04
  - Bathroom (4): int_bath_01 .. int_bath_04
  - Dining Room (4): int_din_01 .. int_din_04
"""

import os
from pathlib import Path

OUTPUT_DIR = Path(r"c:\Users\DELL\OneDrive\Desktop\House plaining\frontend\public\images\interiors")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DESIGNS = [
    # ── 1. Bedrooms (8) ──────────────────────────────────────────────────────
    {
        "id": "int_bed_01",
        "title": "Modern Contemporary Bedroom",
        "category": "Bedroom",
        "tag": "Mid-Range",
        "bg_grad": ("#1a202c", "#0f131a"),
        "wall_color": "#2d3748",
        "floor_grad": ("#744210", "#452406"),
        "accent_type": "channel_headboard",
        "accent_color": "#4a5568",
        "furniture_color": "#e2e8f0",
        "highlight_color": "#ecc94b",
        "brass": True
    },
    {
        "id": "int_bed_02",
        "title": "Luxury Master Bedroom",
        "category": "Bedroom",
        "tag": "Luxury",
        "bg_grad": ("#241b21", "#150e13"),
        "wall_color": "#2b2129",
        "floor_grad": ("#dcd6cd", "#b5aba0"),
        "accent_type": "tufted_velvet",
        "accent_color": "#44337a",
        "furniture_color": "#faf5ff",
        "highlight_color": "#d69e2e",
        "brass": True
    },
    {
        "id": "int_bed_03",
        "title": "Minimalist Neutral Bedroom",
        "category": "Bedroom",
        "tag": "Mid-Range",
        "bg_grad": ("#1f2421", "#121714"),
        "wall_color": "#e6ede8",
        "floor_grad": ("#c4b5a5", "#9e8e7c"),
        "accent_type": "tatami_platform",
        "accent_color": "#819385",
        "furniture_color": "#f7fafc",
        "highlight_color": "#48bb78",
        "brass": False
    },
    {
        "id": "int_bed_04",
        "title": "Warm Wood Bedroom",
        "category": "Bedroom",
        "tag": "Premium",
        "bg_grad": ("#2a1e17", "#170f0a"),
        "wall_color": "#fbf7ee",
        "floor_grad": ("#9c5c2d", "#6e3c19"),
        "accent_type": "cane_rattan",
        "accent_color": "#c07d4b",
        "furniture_color": "#f7fafc",
        "highlight_color": "#dd6b20",
        "brass": False
    },
    {
        "id": "int_bed_05",
        "title": "Elegant Indian Contemporary Bedroom",
        "category": "Bedroom",
        "tag": "Luxury",
        "bg_grad": ("#211524", "#120914"),
        "wall_color": "#2e1e33",
        "floor_grad": ("#e2d9cf", "#beaf9f"),
        "accent_type": "jaali_screen",
        "accent_color": "#b7791f",
        "furniture_color": "#1a365d",
        "highlight_color": "#d69e2e",
        "brass": True
    },
    {
        "id": "int_bed_06",
        "title": "Premium Hotel-Inspired Bedroom",
        "category": "Bedroom",
        "tag": "Luxury",
        "bg_grad": ("#171923", "#0d0e14"),
        "wall_color": "#1a202c",
        "floor_grad": ("#2d3748", "#1a202c"),
        "accent_type": "bronze_mirror",
        "accent_color": "#744210",
        "furniture_color": "#2b6cb0",
        "highlight_color": "#d69e2e",
        "brass": True
    },
    {
        "id": "int_bed_07",
        "title": "Compact Budget-Friendly Bedroom",
        "category": "Bedroom",
        "tag": "Economy",
        "bg_grad": ("#23282e", "#181b20"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "murphy_study",
        "accent_color": "#4299e1",
        "furniture_color": "#ffffff",
        "highlight_color": "#48bb78",
        "brass": False
    },
    {
        "id": "int_bed_08",
        "title": "Space-Saving Bedroom",
        "category": "Bedroom",
        "tag": "Economy",
        "bg_grad": ("#1e252b", "#11161b"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "space_saving_bridge",
        "accent_color": "#3182ce",
        "furniture_color": "#ffffff",
        "highlight_color": "#38bdf8",
        "brass": False
    },

    # ── 2. Living Rooms (6) ──────────────────────────────────────────────────
    {
        "id": "int_lr_01",
        "title": "Modern Contemporary Living Room",
        "category": "Living Room",
        "tag": "Mid-Range",
        "bg_grad": ("#1e222a", "#14171d"),
        "wall_color": "#2c313c",
        "floor_grad": ("#3d4452", "#22262f"),
        "accent_type": "charcoal_slats",
        "accent_color": "#1f232b",
        "furniture_color": "#4a5568",
        "highlight_color": "#63b3ed",
        "brass": False
    },
    {
        "id": "int_lr_02",
        "title": "Luxury Marble Living Room",
        "category": "Living Room",
        "tag": "Luxury",
        "bg_grad": ("#1c1a17", "#0f0e0c"),
        "wall_color": "#262320",
        "floor_grad": ("#dfdcd7", "#b8b2a8"),
        "accent_type": "marble_slab",
        "accent_color": "#f7f7f7",
        "furniture_color": "#24272e",
        "highlight_color": "#ecc94b",
        "brass": True
    },
    {
        "id": "int_lr_03",
        "title": "Minimalist Neutral Living Room",
        "category": "Living Room",
        "tag": "Mid-Range",
        "bg_grad": ("#2a2723", "#1b1916"),
        "wall_color": "#ebe5dc",
        "floor_grad": ("#d4c5b3", "#b09f8c"),
        "accent_type": "japandi_screen",
        "accent_color": "#cbbba6",
        "furniture_color": "#f0ede6",
        "highlight_color": "#dd6b20",
        "brass": False
    },
    {
        "id": "int_lr_04",
        "title": "Warm Wood Living Room",
        "category": "Living Room",
        "tag": "Premium",
        "bg_grad": ("#26190f", "#140c06"),
        "wall_color": "#382315",
        "floor_grad": ("#8a532d", "#593318"),
        "accent_type": "teak_louvers",
        "accent_color": "#a05a2c",
        "furniture_color": "#422817",
        "highlight_color": "#ed8936",
        "brass": True
    },
    {
        "id": "int_lr_05",
        "title": "Elegant Indian Contemporary Living Room",
        "category": "Living Room",
        "tag": "Luxury",
        "bg_grad": ("#211524", "#120914"),
        "wall_color": "#2e1e33",
        "floor_grad": ("#e2d9cf", "#beaf9f"),
        "accent_type": "jaali_screen",
        "accent_color": "#b7791f",
        "furniture_color": "#1a365d",
        "highlight_color": "#d69e2e",
        "brass": True
    },
    {
        "id": "int_lr_06",
        "title": "Compact Budget-Friendly Living Room",
        "category": "Living Room",
        "tag": "Economy",
        "bg_grad": ("#23282e", "#181b20"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "floating_shelves",
        "accent_color": "#e2e8f0",
        "furniture_color": "#718096",
        "highlight_color": "#48bb78",
        "brass": False
    },

    # ── 3. Kitchens (6) ──────────────────────────────────────────────────────
    {
        "id": "int_kit_01",
        "title": "Modern Modular Kitchen",
        "category": "Kitchen",
        "tag": "Premium",
        "bg_grad": ("#1a202c", "#0e121a"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#e2e8f0", "#cbd5e0"),
        "accent_type": "acrylic_cabinets",
        "accent_color": "#2d3748",
        "furniture_color": "#ffffff",
        "highlight_color": "#63b3ed",
        "brass": False
    },
    {
        "id": "int_kit_02",
        "title": "L-Shaped Kitchen",
        "category": "Kitchen",
        "tag": "Mid-Range",
        "bg_grad": ("#1c2420", "#101613"),
        "wall_color": "#f7fafc",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "l_counter",
        "accent_color": "#285e61",
        "furniture_color": "#f0fff4",
        "highlight_color": "#ecc94b",
        "brass": True
    },
    {
        "id": "int_kit_03",
        "title": "U-Shaped Kitchen",
        "category": "Kitchen",
        "tag": "Luxury",
        "bg_grad": ("#161e2e", "#0a111c"),
        "wall_color": "#f7fafc",
        "floor_grad": ("#e2e8f0", "#b8c2cc"),
        "accent_type": "u_counter",
        "accent_color": "#1a365d",
        "furniture_color": "#edf2f7",
        "highlight_color": "#ecc94b",
        "brass": True
    },
    {
        "id": "int_kit_04",
        "title": "Parallel Kitchen",
        "category": "Kitchen",
        "tag": "Mid-Range",
        "bg_grad": ("#20232a", "#121418"),
        "wall_color": "#f7fafc",
        "floor_grad": ("#e2e8f0", "#cbd5e0"),
        "accent_type": "parallel_galley",
        "accent_color": "#4a5568",
        "furniture_color": "#ffffff",
        "highlight_color": "#ed8936",
        "brass": False
    },
    {
        "id": "int_kit_05",
        "title": "Premium Finish Kitchen",
        "category": "Kitchen",
        "tag": "Luxury",
        "bg_grad": ("#1f1c1a", "#110e0d"),
        "wall_color": "#2d2926",
        "floor_grad": ("#1a1816", "#0f0d0c"),
        "accent_type": "waterfall_island",
        "accent_color": "#4a3b32",
        "furniture_color": "#f7fafc",
        "highlight_color": "#d69e2e",
        "brass": True
    },
    {
        "id": "int_kit_06",
        "title": "Budget-Friendly Modular Kitchen",
        "category": "Kitchen",
        "tag": "Economy",
        "bg_grad": ("#22262a", "#14171a"),
        "wall_color": "#f7fafc",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "woodgrain_laminate",
        "accent_color": "#7b5e43",
        "furniture_color": "#edf2f7",
        "highlight_color": "#48bb78",
        "brass": False
    },

    # ── 4. Guest Rooms (4) ───────────────────────────────────────────────────
    {
        "id": "int_guest_01",
        "title": "Modern Guest Room",
        "category": "Guest Room",
        "tag": "Mid-Range",
        "bg_grad": ("#1a202c", "#0f131a"),
        "wall_color": "#2d3748",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "channel_headboard",
        "accent_color": "#4a5568",
        "furniture_color": "#f8fafc",
        "highlight_color": "#63b3ed",
        "brass": True
    },
    {
        "id": "int_guest_02",
        "title": "Minimalist Guest Room",
        "category": "Guest Room",
        "tag": "Mid-Range",
        "bg_grad": ("#1f2421", "#121714"),
        "wall_color": "#f5f0eb",
        "floor_grad": ("#c4b5a5", "#9e8e7c"),
        "accent_type": "tatami_platform",
        "accent_color": "#819385",
        "furniture_color": "#ffffff",
        "highlight_color": "#48bb78",
        "brass": False
    },
    {
        "id": "int_guest_03",
        "title": "Warm Neutral Guest Room",
        "category": "Guest Room",
        "tag": "Premium",
        "bg_grad": ("#242322", "#161514"),
        "wall_color": "#fbf7ee",
        "floor_grad": ("#8a5229", "#573014"),
        "accent_type": "cane_rattan",
        "accent_color": "#cbb8a3",
        "furniture_color": "#ffffff",
        "highlight_color": "#d69e2e",
        "brass": True
    },
    {
        "id": "int_guest_04",
        "title": "Compact Multipurpose Guest Room",
        "category": "Guest Room",
        "tag": "Economy",
        "bg_grad": ("#1e252b", "#11161b"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "murphy_study",
        "accent_color": "#4299e1",
        "furniture_color": "#ffffff",
        "highlight_color": "#3182ce",
        "brass": False
    },

    # ── 5. Bathrooms (4) ─────────────────────────────────────────────────────
    {
        "id": "int_bath_01",
        "title": "Modern Minimalist Bathroom",
        "category": "Bathroom",
        "tag": "Mid-Range",
        "bg_grad": ("#1e252b", "#10161a"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "floating_vanity",
        "accent_color": "#718096",
        "furniture_color": "#ffffff",
        "highlight_color": "#4299e1",
        "brass": False
    },
    {
        "id": "int_bath_02",
        "title": "Premium Stone-Finish Bathroom",
        "category": "Bathroom",
        "tag": "Luxury",
        "bg_grad": ("#1f1e1c", "#100f0e"),
        "wall_color": "#f7f7f7",
        "floor_grad": ("#ded9d0", "#b5aca0"),
        "accent_type": "marble_bath",
        "accent_color": "#e2e8f0",
        "furniture_color": "#ffffff",
        "highlight_color": "#ecc94b",
        "brass": True
    },
    {
        "id": "int_bath_03",
        "title": "Contemporary Shower Bathroom",
        "category": "Bathroom",
        "tag": "Premium",
        "bg_grad": ("#182026", "#0c1217"),
        "wall_color": "#2d3748",
        "floor_grad": ("#1a202c", "#11161d"),
        "accent_type": "glass_shower",
        "accent_color": "#4a5568",
        "furniture_color": "#ffffff",
        "highlight_color": "#63b3ed",
        "brass": False
    },
    {
        "id": "int_bath_04",
        "title": "Compact Functional Bathroom",
        "category": "Bathroom",
        "tag": "Economy",
        "bg_grad": ("#202429", "#13171b"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "compact_toilet",
        "accent_color": "#a0aec0",
        "furniture_color": "#ffffff",
        "highlight_color": "#48bb78",
        "brass": False
    },

    # ── 6. Dining Rooms (4) ──────────────────────────────────────────────────
    {
        "id": "int_din_01",
        "title": "Modern Family Dining Room",
        "category": "Dining Room",
        "tag": "Mid-Range",
        "bg_grad": ("#1e2329", "#121519"),
        "wall_color": "#f7fafc",
        "floor_grad": ("#654321", "#3d2814"),
        "accent_type": "pendant_dining",
        "accent_color": "#4a5568",
        "furniture_color": "#2d3748",
        "highlight_color": "#ecc94b",
        "brass": True
    },
    {
        "id": "int_din_02",
        "title": "Luxury Dining Room",
        "category": "Dining Room",
        "tag": "Luxury",
        "bg_grad": ("#20191f", "#120d12"),
        "wall_color": "#2d232c",
        "floor_grad": ("#e2dcd4", "#b8afa3"),
        "accent_type": "chandelier_dining",
        "accent_color": "#ffffff",
        "furniture_color": "#1a202c",
        "highlight_color": "#d69e2e",
        "brass": True
    },
    {
        "id": "int_din_03",
        "title": "Warm Contemporary Dining Room",
        "category": "Dining Room",
        "tag": "Premium",
        "bg_grad": ("#281d14", "#160e08"),
        "wall_color": "#fdf8ee",
        "floor_grad": ("#8a5229", "#573014"),
        "accent_type": "live_edge_dining",
        "accent_color": "#a46332",
        "furniture_color": "#382315",
        "highlight_color": "#dd6b20",
        "brass": False
    },
    {
        "id": "int_din_04",
        "title": "Compact Dining Room",
        "category": "Dining Room",
        "tag": "Economy",
        "bg_grad": ("#22272d", "#14181d"),
        "wall_color": "#edf2f7",
        "floor_grad": ("#cbd5e0", "#a0aec0"),
        "accent_type": "round_table",
        "accent_color": "#718096",
        "furniture_color": "#ffffff",
        "highlight_color": "#48bb78",
        "brass": False
    },
]


def render_accent_features(d: dict) -> str:
    acc = d["accent_type"]
    brass_color = "#d69e2e" if d["brass"] else "#a0aec0"
    gold_trim = f'<line x1="180" y1="120" x2="180" y2="340" stroke="{brass_color}" stroke-width="2.5" />' if d["brass"] else ""

    if acc == "charcoal_slats":
        slats = "".join([f'<rect x="{180 + i*16}" y="120" width="8" height="220" rx="2" fill="{d["accent_color"]}" />' for i in range(16)])
        return f'''
        <g id="accent-layer">
            <rect x="170" y="110" width="270" height="240" rx="8" fill="#181c24" opacity="0.9" />
            {slats}
            <rect x="200" y="150" width="210" height="120" rx="6" fill="#0b0d12" stroke="#2d3748" stroke-width="3" />
            <rect x="205" y="155" width="200" height="110" rx="4" fill="url(#screenGrad)" />
            <rect x="180" y="300" width="250" height="35" rx="4" fill="#2d3748" stroke="{d["highlight_color"]}" stroke-width="1.5" />
            <ellipse cx="305" cy="210" rx="90" ry="50" fill="{d["highlight_color"]}" opacity="0.18" filter="url(#glow)" />
            <path d="M 460 310 L 680 310 L 680 390 L 590 390 L 590 410 L 460 410 Z" fill="{d["furniture_color"]}" rx="6" />
            <rect x="470" y="270" width="130" height="40" rx="6" fill="#313947" />
            <rect x="610" y="270" width="60" height="40" rx="6" fill="#313947" />
            <circle cx="530" cy="370" r="28" fill="#1a202c" stroke="{brass_color}" stroke-width="2" />
            <circle cx="565" cy="380" r="18" fill="#2d3748" />
        </g>
        '''

    elif acc == "marble_slab":
        return f'''
        <g id="accent-layer">
            <rect x="180" y="110" width="280" height="240" rx="6" fill="url(#marbleGrad)" stroke="{brass_color}" stroke-width="3" />
            <path d="M 190 120 Q 230 180 270 200 T 310 280 T 330 350" stroke="#718096" stroke-width="2.5" fill="none" opacity="0.45" />
            <path d="M 450 120 Q 410 180 370 200 T 330 280 T 310 350" stroke="#718096" stroke-width="2.5" fill="none" opacity="0.45" />
            {gold_trim}
            <line x1="460" y1="120" x2="460" y2="340" stroke="{brass_color}" stroke-width="2.5" />
            <path d="M 480 320 C 520 280, 640 280, 680 320 L 670 400 C 630 380, 530 380, 490 400 Z" fill="#2d3748" stroke="{brass_color}" stroke-width="1.5" />
            <circle cx="400" cy="80" r="45" fill="none" stroke="{brass_color}" stroke-width="4" filter="url(#glow)" />
            <circle cx="400" cy="80" r="30" fill="none" stroke="{brass_color}" stroke-width="2" />
            <circle cx="400" cy="80" r="5" fill="#ffffff" filter="url(#glow)" />
        </g>
        '''

    elif acc == "japandi_screen":
        return f'''
        <g id="accent-layer">
            <rect x="180" y="110" width="260" height="230" rx="4" fill="#dfd7cb" stroke="#8c7a68" stroke-width="2" />
            <line x1="180" y1="180" x2="440" y2="180" stroke="#8c7a68" stroke-width="1.5" />
            <line x1="180" y1="260" x2="440" y2="260" stroke="#8c7a68" stroke-width="1.5" />
            <line x1="260" y1="110" x2="260" y2="340" stroke="#8c7a68" stroke-width="1.5" />
            <line x1="350" y1="110" x2="350" y2="340" stroke="#8c7a68" stroke-width="1.5" />
            <rect x="470" y="320" width="190" height="55" rx="4" fill="#e8e2d8" stroke="#a08e7c" stroke-width="2" />
            <rect x="460" y="365" width="210" height="15" rx="2" fill="#7d6753" />
            <ellipse cx="380" cy="95" rx="28" ry="38" fill="#fffaf0" stroke="#c4b5a5" stroke-width="1.5" filter="url(#glow)" />
            <line x1="380" y1="0" x2="380" y2="57" stroke="#8c7a68" stroke-width="2" />
        </g>
        '''

    elif acc == "teak_louvers":
        louvers = "".join([f'<rect x="{175 + i*18}" y="110" width="10" height="230" rx="3" fill="#8a4d21" />' for i in range(14)])
        return f'''
        <g id="accent-layer">
            <rect x="170" y="105" width="260" height="240" rx="6" fill="#4d2810" />
            {louvers}
            <rect x="190" y="295" width="220" height="40" rx="4" fill="#2d170a" stroke="{brass_color}" stroke-width="2" />
            <rect x="500" y="280" width="110" height="90" rx="16" fill="#8a441a" stroke="{brass_color}" stroke-width="1.5" />
            <rect x="485" y="300" width="22" height="60" rx="8" fill="#5e2b0e" />
            <rect x="603" y="300" width="22" height="60" rx="8" fill="#5e2b0e" />
        </g>
        '''

    elif acc == "jaali_screen":
        return f'''
        <g id="accent-layer">
            <rect x="180" y="110" width="260" height="240" rx="6" fill="#241429" stroke="{brass_color}" stroke-width="2" />
            <!-- Laser Cut Filigree Grid -->
            <circle cx="230" cy="160" r="22" fill="none" stroke="{brass_color}" stroke-width="2" />
            <circle cx="310" cy="160" r="22" fill="none" stroke="{brass_color}" stroke-width="2" />
            <circle cx="390" cy="160" r="22" fill="none" stroke="{brass_color}" stroke-width="2" />
            <circle cx="270" cy="220" r="22" fill="none" stroke="{brass_color}" stroke-width="2" />
            <circle cx="350" cy="220" r="22" fill="none" stroke="{brass_color}" stroke-width="2" />
            <rect x="470" y="290" width="190" height="90" rx="8" fill="#1a365d" stroke="{brass_color}" stroke-width="2" />
            <circle cx="310" cy="80" r="16" fill="{brass_color}" filter="url(#glow)" />
            <line x1="310" y1="0" x2="310" y2="64" stroke="{brass_color}" stroke-width="2" />
        </g>
        '''

    elif acc == "bronze_mirror":
        return f'''
        <g id="accent-layer">
            <rect x="180" y="110" width="260" height="230" rx="4" fill="#3a2414" stroke="{brass_color}" stroke-width="2" />
            <rect x="200" y="125" width="100" height="200" fill="#653d1c" opacity="0.8" stroke="{brass_color}" stroke-width="1.5" />
            <rect x="320" y="125" width="100" height="200" fill="#653d1c" opacity="0.8" stroke="{brass_color}" stroke-width="1.5" />
            <rect x="470" y="280" width="180" height="100" rx="12" fill="#1a202c" stroke="{brass_color}" stroke-width="2" />
            <line x1="470" y1="80" x2="650" y2="80" stroke="{d["highlight_color"]}" stroke-width="3" filter="url(#glow)" />
        </g>
        '''

    elif acc == "acrylic_cabinets" or "counter" in acc or "galley" in acc or "island" in acc or "laminate" in acc:
        return f'''
        <g id="kitchen-cabinetry">
            <rect x="180" y="110" width="460" height="90" rx="4" fill="{d["accent_color"]}" stroke="#4a5568" stroke-width="1.5" />
            <line x1="295" y1="110" x2="295" y2="200" stroke="#1a202c" stroke-width="2" />
            <line x1="410" y1="110" x2="410" y2="200" stroke="#1a202c" stroke-width="2" />
            <line x1="525" y1="110" x2="525" y2="200" stroke="#1a202c" stroke-width="2" />
            <line x1="180" y1="202" x2="640" y2="202" stroke="{d["highlight_color"]}" stroke-width="4" filter="url(#glow)" />
            <rect x="180" y="205" width="460" height="75" fill="#e2e8f0" stroke="#cbd5e0" stroke-width="1" />
            <rect x="170" y="280" width="480" height="20" rx="3" fill="#ffffff" stroke="{brass_color}" stroke-width="1.5" />
            <rect x="175" y="300" width="470" height="100" fill="{d["accent_color"]}" />
            <line x1="295" y1="300" x2="295" y2="400" stroke="#1a202c" stroke-width="2" />
            <line x1="410" y1="300" x2="410" y2="400" stroke="#1a202c" stroke-width="2" />
            <line x1="525" y1="300" x2="525" y2="400" stroke="#1a202c" stroke-width="2" />
            <polygon points="370,110 450,110 435,70 385,70" fill="#a0aec0" stroke="#718096" stroke-width="2" />
            <rect x="365" y="278" width="90" height="6" rx="2" fill="#1a202c" />
        </g>
        '''

    elif "headboard" in acc or "tatami" in acc or "tufted" in acc or "cane" in acc or "murphy" in acc or "taupe" in acc or "space_saving" in acc:
        return f'''
        <g id="bedroom-bed">
            <rect x="220" y="110" width="360" height="180" rx="8" fill="{d["accent_color"]}" stroke="{brass_color}" stroke-width="2" />
            <line x1="280" y1="110" x2="280" y2="290" stroke="{brass_color}" stroke-width="1.5" />
            <line x1="340" y1="110" x2="340" y2="290" stroke="{brass_color}" stroke-width="1.5" />
            <line x1="400" y1="110" x2="400" y2="290" stroke="{brass_color}" stroke-width="1.5" />
            <line x1="460" y1="110" x2="460" y2="290" stroke="{brass_color}" stroke-width="1.5" />
            <line x1="520" y1="110" x2="520" y2="290" stroke="{brass_color}" stroke-width="1.5" />
            <rect x="250" y="280" width="300" height="90" rx="8" fill="{d["furniture_color"]}" stroke="#cbd5e0" stroke-width="2" />
            <rect x="270" y="250" width="110" height="35" rx="6" fill="#f7fafc" stroke="#e2e8f0" stroke-width="1.5" />
            <rect x="420" y="250" width="110" height="35" rx="6" fill="#f7fafc" stroke="#e2e8f0" stroke-width="1.5" />
            <rect x="250" y="330" width="300" height="35" rx="4" fill="{d["highlight_color"]}" opacity="0.8" />
            <rect x="150" y="300" width="60" height="50" rx="4" fill="#2d3748" stroke="{brass_color}" stroke-width="1" />
            <rect x="590" y="300" width="60" height="50" rx="4" fill="#2d3748" stroke="{brass_color}" stroke-width="1" />
            <line x1="180" y1="0" x2="180" y2="220" stroke="{brass_color}" stroke-width="1.5" />
            <circle cx="180" cy="225" r="12" fill="#fff" filter="url(#glow)" />
            <line x1="620" y1="0" x2="620" y2="220" stroke="{brass_color}" stroke-width="1.5" />
            <circle cx="620" cy="225" r="12" fill="#fff" filter="url(#glow)" />
        </g>
        '''

    elif "vanity" in acc or "bath" in acc or "shower" in acc or "toilet" in acc:
        return f'''
        <g id="bathroom-fixtures">
            <circle cx="330" cy="180" r="65" fill="#f7fafc" stroke="{brass_color}" stroke-width="3" filter="url(#glow)" />
            <rect x="230" y="280" width="200" height="55" rx="6" fill="{d["accent_color"]}" stroke="{brass_color}" stroke-width="1.5" />
            <ellipse cx="330" cy="280" rx="45" ry="12" fill="#ffffff" stroke="#cbd5e0" stroke-width="2" />
            <path d="M 330 268 L 330 240 L 320 240" fill="none" stroke="{brass_color}" stroke-width="4" stroke-linecap="round" />
            <rect x="470" y="110" width="180" height="280" fill="url(#glassGrad)" stroke="#4a5568" stroke-width="2.5" />
            <line x1="470" y1="180" x2="650" y2="180" stroke="#718096" stroke-width="1" stroke-dasharray="4" />
            <path d="M 560 110 L 560 135 L 560 145" fill="none" stroke="{brass_color}" stroke-width="5" />
            <ellipse cx="560" cy="148" rx="25" ry="8" fill="{brass_color}" />
            <ellipse cx="560" cy="155" rx="15" ry="4" fill="{d["highlight_color"]}" filter="url(#glow)" opacity="0.6" />
        </g>
        '''

    elif "dining" in acc or "table" in acc:
        return f'''
        <g id="dining-furniture">
            <rect x="180" y="110" width="440" height="200" rx="8" fill="{d["accent_color"]}" opacity="0.85" stroke="{brass_color}" stroke-width="2" />
            <rect x="220" y="290" width="360" height="24" rx="6" fill="#f7fafc" stroke="{brass_color}" stroke-width="2" />
            <polygon points="260,314 280,314 270,390 250,390" fill="#2d3748" />
            <polygon points="540,314 520,314 530,390 550,390" fill="#2d3748" />
            <rect x="240" y="230" width="45" height="60" rx="8" fill="{d["furniture_color"]}" stroke="{brass_color}" stroke-width="1" />
            <rect x="310" y="230" width="45" height="60" rx="8" fill="{d["furniture_color"]}" stroke="{brass_color}" stroke-width="1" />
            <rect x="445" y="230" width="45" height="60" rx="8" fill="{d["furniture_color"]}" stroke="{brass_color}" stroke-width="1" />
            <rect x="515" y="230" width="45" height="60" rx="8" fill="{d["furniture_color"]}" stroke="{brass_color}" stroke-width="1" />
            <line x1="400" y1="0" x2="400" y2="150" stroke="{brass_color}" stroke-width="2" />
            <ellipse cx="400" cy="160" rx="70" ry="18" fill="none" stroke="{brass_color}" stroke-width="3" filter="url(#glow)" />
            <circle cx="360" cy="160" r="8" fill="#ffffff" filter="url(#glow)" />
            <circle cx="400" cy="160" r="10" fill="#ffffff" filter="url(#glow)" />
            <circle cx="440" cy="160" r="8" fill="#ffffff" filter="url(#glow)" />
        </g>
        '''

    else:
        # Floating shelves & compact features
        return f'''
        <g id="compact-shelves">
            <rect x="180" y="140" width="260" height="15" rx="3" fill="#cbd5e0" />
            <rect x="220" y="190" width="220" height="15" rx="3" fill="#cbd5e0" />
            <rect x="470" y="300" width="190" height="70" rx="8" fill="{d["furniture_color"]}" stroke="#cbd5e0" stroke-width="2" />
            <circle cx="310" cy="100" r="24" fill="{d["highlight_color"]}" filter="url(#glow)" opacity="0.4" />
        </g>
        '''


def generate_svg(d: dict) -> str:
    acc_markup = render_accent_features(d)
    
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{d["bg_grad"][0]}" />
      <stop offset="100%" stop-color="{d["bg_grad"][1]}" />
    </linearGradient>

    <linearGradient id="floorGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{d["floor_grad"][0]}" />
      <stop offset="100%" stop-color="{d["floor_grad"][1]}" />
    </linearGradient>

    <linearGradient id="marbleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="40%" stop-color="#f2f2f2" />
      <stop offset="70%" stop-color="#e8e8e8" />
      <stop offset="100%" stop-color="#ffffff" />
    </linearGradient>

    <linearGradient id="glassGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#63b3ed" stop-opacity="0.25" />
      <stop offset="50%" stop-color="#ffffff" stop-opacity="0.15" />
      <stop offset="100%" stop-color="#63b3ed" stop-opacity="0.20" />
    </linearGradient>

    <linearGradient id="screenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1a202c" />
      <stop offset="100%" stop-color="#2d3748" />
    </linearGradient>

    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>

  <!-- Room Shell & Wall Plane -->
  <rect width="800" height="500" fill="url(#bgGrad)" />
  <rect x="80" y="40" width="640" height="340" fill="{d["wall_color"]}" rx="6" opacity="0.95" />
  <line x1="80" y1="40" x2="80" y2="380" stroke="#4a5568" stroke-width="2" />
  <line x1="720" y1="40" x2="720" y2="380" stroke="#4a5568" stroke-width="2" />

  <!-- Floor Plane with Perspective Lines -->
  <polygon points="80,380 720,380 780,480 20,480" fill="url(#floorGrad)" />
  <line x1="80" y1="380" x2="720" y2="380" stroke="#1a202c" stroke-width="2.5" />
  <line x1="240" y1="380" x2="200" y2="480" stroke="#000000" stroke-width="0.8" opacity="0.3" />
  <line x1="400" y1="380" x2="400" y2="480" stroke="#000000" stroke-width="0.8" opacity="0.3" />
  <line x1="560" y1="380" x2="600" y2="480" stroke="#000000" stroke-width="0.8" opacity="0.3" />

  <!-- Distinct Architectural Features -->
  {acc_markup}

  <!-- Studio Header Overlay -->
  <g id="badge" transform="translate(30, 30)">
    <rect width="210" height="42" rx="8" fill="#0f172a" fill-opacity="0.85" stroke="#334155" stroke-width="1.5" />
    <text x="14" y="18" fill="#94a3b8" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="600" letter-spacing="0.5">{d["category"].upper()}</text>
    <text x="14" y="33" fill="#f8fafc" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="700">{d["title"]}</text>
  </g>

  <!-- Budget Tier Pill -->
  <g id="tier-pill" transform="translate(680, 30)">
    <rect width="90" height="28" rx="14" fill="#1e293b" stroke="{d["highlight_color"]}" stroke-width="1.5" />
    <text x="45" y="18" fill="{d["highlight_color"]}" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="700" text-anchor="middle">{d["tag"]}</text>
  </g>

  <!-- Unique Stable ID -->
  <g id="id-tag" transform="translate(710, 460)">
    <text x="0" y="0" fill="#64748b" font-family="monospace" font-size="12" font-weight="600">{d["id"]}</text>
  </g>
</svg>'''

for d in DESIGNS:
    filepath = OUTPUT_DIR / f"{d['id']}.svg"
    svg_content = generate_svg(d)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

print(f"Successfully generated {len(DESIGNS)} SVGs in {OUTPUT_DIR}")
