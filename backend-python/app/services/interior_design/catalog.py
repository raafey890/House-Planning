"""
Interior Design Catalog — Phase 6E.1.
Contains exactly 32 distinct interior design options across 6 room categories:
  - Bedroom: 8 designs (int_bed_01 .. int_bed_08)
  - Living Room: 6 designs (int_lr_01 .. int_lr_06)
  - Kitchen: 6 designs (int_kit_01 .. int_kit_06)
  - Guest Room: 4 designs (int_guest_01 .. int_guest_04)
  - Bathroom: 4 designs (int_bath_01 .. int_bath_04)
  - Dining Room: 4 designs (int_din_01 .. int_din_04)

POP/gypsum ceilings, decorative lighting, flooring, paint, wardrobes, cabinetry
and fixtures are configurable features on these room designs.
"""

from typing import Dict, List, Optional
from app.models.interior_design import InteriorDesignOption

INTERIOR_CATALOG_DATA: List[Dict] = [
    # ── 1. BEDROOM (8 Designs) ───────────────────────────────────────────────
    {
        "id": "int_bed_01",
        "name": "Modern Contemporary Bedroom",
        "category": "bedroom",
        "style": "Modern Contemporary",
        "budget_tier": "Mid-Range",
        "description": "Full-height upholstered channel headboard, integrated bedside LED pendants, smoked glass sliding wardrobe, and warm neutral acoustic wall louvers.",
        "suitable_room_types": ["bedroom", "master_bedroom", "guest_room"],
        "image_path": "/images/interiors/int_bed_01.jpg",
        "wall_finish_default": "Warm grey velvet emulsion with fluted acoustic bedside paneling",
        "flooring_default": "Engineered Oak Hardwood Flooring",
        "ceiling_concept": "Perimeter gypsum false ceiling with warm 3000K LED strip profile",
        "lighting_concept": "Recessed anti-glare COB spotlights + dual bedside reading pendants",
        "furniture_concept": "King-size bed with channel-tufted fabric headboard, floating nightstands, and 7-ft sliding wardrobe",
        "fixtures_and_materials": ["Acoustic fabric louvers", "Smoked grey mirror glass", "Brushed aluminum handles"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1650.0,
            "wardrobe_width_ft": 7.0,
            "bed_headboard_lump_sum": 28000.0,
            "false_ceiling_rate_sqft": 135.0,
            "lighting_lump_sum": 16000.0,
            "hardware_lump_sum": 12000.0
        },
        "limitations_and_assumptions": [
            "Requires minimum 10.5 ft wall width for bed + dual nightstand clearances.",
            "Assumes 9.5 to 10 ft ceiling clearance."
        ]
    },
    {
        "id": "int_bed_02",
        "name": "Luxury Master Bedroom",
        "category": "bedroom",
        "style": "Luxury",
        "budget_tier": "Luxury",
        "description": "Opulent master suite with champagne gold PVD trims, plush velvet headboard wall, bronze mirror insets, full-height walk-in wardrobe, and imported Italian marble flooring.",
        "suitable_room_types": ["bedroom", "master_bedroom"],
        "image_path": "/images/interiors/int_bed_02.jpg",
        "wall_finish_default": "Champagne velvet wall panelling with bronze PVD metallic inlays",
        "flooring_default": "Imported Italian Statuario Marble Slabs",
        "ceiling_concept": "Multi-tiered gypsum tray ceiling with concealed perimeter gold cove wash",
        "lighting_concept": "Statement K9 crystal bedside chandeliers + smart dimmable scene spotlights",
        "furniture_concept": "King-size bespoke velvet upholstered wingback bed, marble-top nightstands, vanity console",
        "fixtures_and_materials": ["Italian Statuario marble", "Champagne gold PVD profiles", "Bronze tinted mirror"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 2400.0,
            "wardrobe_width_ft": 9.0,
            "bed_headboard_lump_sum": 52000.0,
            "false_ceiling_rate_sqft": 160.0,
            "lighting_lump_sum": 35000.0,
            "hardware_lump_sum": 22000.0
        },
        "limitations_and_assumptions": [
            "Recommended for master bedrooms with area >= 160 sq ft for adequate walk-around circulation."
        ]
    },
    {
        "id": "int_bed_03",
        "name": "Minimalist Neutral Bedroom",
        "category": "bedroom",
        "style": "Minimalist",
        "budget_tier": "Mid-Range",
        "description": "Serene Japandi aesthetic with low-profile platform bed, natural linen textures, lime-wash accent wall, and concealed soft illumination.",
        "suitable_room_types": ["bedroom", "master_bedroom", "guest_room"],
        "image_path": "/images/interiors/int_bed_03.jpg",
        "wall_finish_default": "Artisanal natural beige limewash texture paint",
        "flooring_default": "Matte light oak wooden laminate flooring",
        "ceiling_concept": "Clean flat ceiling with subtle recessed architectural cove",
        "lighting_concept": "Diffused indirect headboard cove + washi paper pendant light",
        "furniture_concept": "Low platform wooden bed with extended wooden ledge and handleless push-to-open wardrobe",
        "fixtures_and_materials": ["Natural light oak", "Textured linen upholstery", "Washi paper lantern"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1500.0,
            "wardrobe_width_ft": 6.5,
            "bed_headboard_lump_sum": 22000.0,
            "false_ceiling_rate_sqft": 120.0,
            "lighting_lump_sum": 14000.0,
            "hardware_lump_sum": 9000.0
        },
        "limitations_and_assumptions": [
            "Low platform bed height is 14 inches; verify user mobility preferences."
        ]
    },
    {
        "id": "int_bed_04",
        "name": "Warm Wood Bedroom",
        "category": "bedroom",
        "style": "Warm Wood",
        "budget_tier": "Premium",
        "description": "Rich teakwood wall paneling, natural cane/rattan woven headboard accents, earthy terracotta accents, and soft warm ambient glow.",
        "suitable_room_types": ["bedroom", "master_bedroom"],
        "image_path": "/images/interiors/int_bed_04.jpg",
        "wall_finish_default": "Natural teak wood fluted veneer paneling with warm clay emulsion",
        "flooring_default": "Warm teak plank flooring / woodgrain vitrified",
        "ceiling_concept": "Warm perimeter ceiling with wooden trim detail",
        "lighting_concept": "Warm 2700K brass directional spotlights + woven rattan bedside lamps",
        "furniture_concept": "Solid teak wood bed with natural wicker headboard and matching slatted wardrobe doors",
        "fixtures_and_materials": ["Solid teak wood", "Handwoven natural wicker/rattan", "Antique brass hardware"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1950.0,
            "wardrobe_width_ft": 7.5,
            "bed_headboard_lump_sum": 36000.0,
            "false_ceiling_rate_sqft": 145.0,
            "lighting_lump_sum": 20000.0,
            "hardware_lump_sum": 15000.0
        },
        "limitations_and_assumptions": [
            "Natural wood finishes require annual wax/varnish maintenance."
        ]
    },
    {
        "id": "int_bed_05",
        "name": "Elegant Indian Contemporary Bedroom",
        "category": "bedroom",
        "style": "Indian Contemporary",
        "budget_tier": "Luxury",
        "description": "Subtle brass jaali headboard screen, carved wooden accents, raw silk upholstered headboard, and brass inlay details on wardrobe shutters.",
        "suitable_room_types": ["bedroom", "master_bedroom"],
        "image_path": "/images/interiors/int_bed_05.jpg",
        "wall_finish_default": "Royal matte emulsion with precision laser-cut brass jaali paneling",
        "flooring_default": "Polished Indian marble with brass border inlay",
        "ceiling_concept": "Architectural recessed ceiling with ornate corner mouldings",
        "lighting_concept": "Handcrafted filigree brass pendants + warm cove lighting",
        "furniture_concept": "Sheesham wood poster-inspired low bed with raw silk cushions and brass inlay wardrobe",
        "fixtures_and_materials": ["Sheesham & Teak wood", "Solid brass laser-cut jaali", "Raw silk fabrics"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 2200.0,
            "wardrobe_width_ft": 8.0,
            "bed_headboard_lump_sum": 45000.0,
            "false_ceiling_rate_sqft": 155.0,
            "lighting_lump_sum": 28000.0,
            "hardware_lump_sum": 18000.0
        },
        "limitations_and_assumptions": [
            "Handcrafted brass jaali requires custom lead time of 3 weeks."
        ]
    },
    {
        "id": "int_bed_06",
        "name": "Premium Hotel-Inspired Bedroom",
        "category": "bedroom",
        "style": "Hotel-Inspired",
        "budget_tier": "Luxury",
        "description": "Five-star executive suite vibe with acoustic suede fabric wall cladding, integrated LED headboard cove, executive lounge chair, and dark bronze accents.",
        "suitable_room_types": ["bedroom", "master_bedroom"],
        "image_path": "/images/interiors/int_bed_06.jpg",
        "wall_finish_default": "Wall-to-wall acoustic suede fabric wall paneling with vertical brass channels",
        "flooring_default": "Plush acoustic carpet tiles / high-gloss marble",
        "ceiling_concept": "Deep perimeter drop with magnetic spotlight track & curtain pocket recess",
        "lighting_concept": "Dual circuit reading lights, concealed night light wash + statement pendant",
        "furniture_concept": "Oversized upholstered king bed, integrated floating nightstands, and executive lounge armchair",
        "fixtures_and_materials": ["Acoustic suede panelling", "Anodized bronze aluminum", "Black chrome fittings"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 2100.0,
            "wardrobe_width_ft": 8.0,
            "bed_headboard_lump_sum": 42000.0,
            "false_ceiling_rate_sqft": 150.0,
            "lighting_lump_sum": 26000.0,
            "hardware_lump_sum": 16000.0
        },
        "limitations_and_assumptions": [
            "Fabric wall panelling performs best in fully air-conditioned spaces."
        ]
    },
    {
        "id": "int_bed_07",
        "name": "Compact Budget-Friendly Bedroom",
        "category": "bedroom",
        "style": "Budget-Friendly",
        "budget_tier": "Economy",
        "description": "Smart, cost-effective Scandinavian styling with light laminate finishes, clean white walls, minimalist wardrobe, and high-efficiency LED surface lighting.",
        "suitable_room_types": ["bedroom", "guest_room"],
        "image_path": "/images/interiors/int_bed_07.jpg",
        "wall_finish_default": "Washable acrylic emulsion with soft sage/taupe accent paint",
        "flooring_default": "Standard vitrified ceramic tiles (2'x2')",
        "ceiling_concept": "Clean plastered ceiling with perimeter POP border moulding",
        "lighting_concept": "Energy-efficient LED surface downlights + clip-on reading lamps",
        "furniture_concept": "Queen-size laminate box bed with hydraulic under-bed storage and 5-ft 2-door wardrobe",
        "fixtures_and_materials": ["Pre-laminated particle board", "Stainless steel bar handles", "Edge-banded PVC"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1150.0,
            "wardrobe_width_ft": 5.0,
            "bed_headboard_lump_sum": 14000.0,
            "false_ceiling_rate_sqft": 90.0,
            "lighting_lump_sum": 8000.0,
            "hardware_lump_sum": 6000.0
        },
        "limitations_and_assumptions": [
            "Optimized for economical construction; no false ceiling drop required."
        ]
    },
    {
        "id": "int_bed_08",
        "name": "Space-Saving Bedroom",
        "category": "bedroom",
        "style": "Space-Saving",
        "budget_tier": "Economy",
        "description": "Ergonomic multi-functional design featuring hydraulic lift-up storage bed, integrated wall-mounted fold-out study desk, and overhead bridge storage cabinets.",
        "suitable_room_types": ["bedroom", "guest_room"],
        "image_path": "/images/interiors/int_bed_08.jpg",
        "wall_finish_default": "Durable acrylic emulsion with geometric two-tone paint",
        "flooring_default": "Anti-scratch matte vitrified floor tiles",
        "ceiling_concept": "Flat ceiling with modern surface linear lighting",
        "lighting_concept": "Multi-directional surface track spots + integrated study task light",
        "furniture_concept": "Hydraulic storage bed, integrated corner wardrobe, overhead bridge storage, and floating study desk",
        "fixtures_and_materials": ["High-density moisture-resistant (HDMR) boards", "Heavy-duty hydraulic gas lifts"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1350.0,
            "wardrobe_width_ft": 6.0,
            "bed_headboard_lump_sum": 18000.0,
            "study_unit_lump_sum": 15000.0,
            "false_ceiling_rate_sqft": 100.0,
            "lighting_lump_sum": 10000.0,
            "hardware_lump_sum": 8000.0
        },
        "limitations_and_assumptions": [
            "Ideal for compact bedrooms under 120 sq ft to maximize usable floor area."
        ]
    },

    # ── 2. LIVING ROOM (6 Designs) ───────────────────────────────────────────
    {
        "id": "int_lr_01",
        "name": "Modern Contemporary Living Room",
        "category": "living_room",
        "style": "Modern Contemporary",
        "budget_tier": "Mid-Range",
        "description": "Sleek architectural lines with fluted charcoal acoustic paneling, neutral warm grey palette, floating media console with concealed wiring, and magnetic track lights.",
        "suitable_room_types": ["living_room", "hall", "family_room"],
        "image_path": "/images/interiors/int_lr_01.jpg",
        "wall_finish_default": "Warm grey velvet emulsion with fluted charcoal accent paneling",
        "flooring_default": "Double-charged vitrified floor tiles (4'x2' glossy finish)",
        "ceiling_concept": "Perimeter gypsum drop with concealed 3000K warm LED profile lighting",
        "lighting_concept": "Recessed COB anti-glare downlights + magnetic linear track accent",
        "furniture_concept": "L-shaped low-slung fabric sectional sofa with nesting metal coffee tables",
        "fixtures_and_materials": ["Acoustic wall louvers", "Quartz-top floating TV unit", "Black magnetic track lights"],
        "cost_parameters": {
            "wall_paneling_rate_sqft": 320.0,
            "wall_paneling_area_sqft": 75.0,
            "false_ceiling_rate_sqft": 135.0,
            "lighting_lump_sum": 24000.0,
            "tv_unit_lump_sum": 38000.0,
            "furniture_allowance": 125000.0
        },
        "limitations_and_assumptions": [
            "Requires minimum 11 ft living room wall width for balanced TV console scale."
        ]
    },
    {
        "id": "int_lr_02",
        "name": "Luxury Marble Living Room",
        "category": "living_room",
        "style": "Luxury",
        "budget_tier": "Luxury",
        "description": "Opulent Italian Statuario bookmatched marble TV accent wall, champagne gold metallic trims, crystal chandelier ring, and imported polished marble flooring.",
        "suitable_room_types": ["living_room", "hall"],
        "image_path": "/images/interiors/int_lr_02.jpg",
        "wall_finish_default": "Full-height bookmatched Statuario marble slab + gold PVD inlays",
        "flooring_default": "Imported Italian Marble / Onyx Polished Slabs",
        "ceiling_concept": "Tiered architectural cove with champagne gold leafing details",
        "lighting_concept": "Contemporary crystal ring chandelier + peripheral dimmable spotlights",
        "furniture_concept": "Bespoke velvet upholstered curved sofa and gold-brushed marble cocktail table",
        "fixtures_and_materials": ["Italian Statuario marble", "Brass PVD metal profiles", "K9 crystal chandelier"],
        "cost_parameters": {
            "marble_slab_cost": 85000.0,
            "false_ceiling_rate_sqft": 165.0,
            "lighting_lump_sum": 45000.0,
            "tv_unit_lump_sum": 65000.0,
            "furniture_allowance": 250000.0
        },
        "limitations_and_assumptions": [
            "Bookmatched marble slabs require heavy wall structural anchoring."
        ]
    },
    {
        "id": "int_lr_03",
        "name": "Minimalist Neutral Living Room",
        "category": "living_room",
        "style": "Minimalist",
        "budget_tier": "Mid-Range",
        "description": "Understated Japandi serenity with natural ash wood details, textured off-white limewash, low-slung linen sofa, and gentle indirect illumination.",
        "suitable_room_types": ["living_room", "hall", "family_room"],
        "image_path": "/images/interiors/int_lr_03.jpg",
        "wall_finish_default": "Textured off-white limewash paint with light ash wood border",
        "flooring_default": "Matte finish large-format porcelain slabs (light beige)",
        "ceiling_concept": "Seamless flat gypsum with flush recessed architectural perimeter cove",
        "lighting_concept": "Indirect perimeter cove illumination + paper washi feature pendant",
        "furniture_concept": "Natural linen 3-seater sofa, solid oak coffee block, floating minimalist bench",
        "fixtures_and_materials": ["Natural ash wood", "Organic linen fabric", "Artisanal textured plaster"],
        "cost_parameters": {
            "wall_paneling_rate_sqft": 180.0,
            "wall_paneling_area_sqft": 60.0,
            "false_ceiling_rate_sqft": 125.0,
            "lighting_lump_sum": 18000.0,
            "tv_unit_lump_sum": 28000.0,
            "furniture_allowance": 95000.0
        },
        "limitations_and_assumptions": [
            "Prefers abundant natural daylight; ideal for north or east facing living rooms."
        ]
    },
    {
        "id": "int_lr_04",
        "name": "Warm Wood Living Room",
        "category": "living_room",
        "style": "Warm Wood",
        "budget_tier": "Premium",
        "description": "Floor-to-ceiling teakwood louvers, rich walnut media unit, caramel leather chesterfield sofa, and amber warm accent lighting.",
        "suitable_room_types": ["living_room", "hall"],
        "image_path": "/images/interiors/int_lr_04.jpg",
        "wall_finish_default": "Natural walnut wood paneling with warm sand textured paint",
        "flooring_default": "Rich teakwood plank flooring / woodgrain tiles",
        "ceiling_concept": "Exposed faux timber beams with integrated downlight channels",
        "lighting_concept": "Warm 2700K ambient spots + architectural directional picture lights",
        "furniture_concept": "Cognac top-grain leather sofa, reclaimed wood coffee table, accent wingback chair",
        "fixtures_and_materials": ["Natural walnut veneer", "Top-grain leather", "Brushed brass accents"],
        "cost_parameters": {
            "wall_paneling_rate_sqft": 360.0,
            "wall_paneling_area_sqft": 80.0,
            "false_ceiling_rate_sqft": 150.0,
            "lighting_lump_sum": 26000.0,
            "tv_unit_lump_sum": 45000.0,
            "furniture_allowance": 175000.0
        },
        "limitations_and_assumptions": [
            "Wood paneling adds warmth; pairs best with high natural or warm artificial lighting."
        ]
    },
    {
        "id": "int_lr_05",
        "name": "Elegant Indian Contemporary Living Room",
        "category": "living_room",
        "style": "Indian Contemporary",
        "budget_tier": "Luxury",
        "description": "Brass-accented geometric jaali partition, rich jewel-toned raw silk fabrics, carved wooden details, and traditional brass hanging lamps.",
        "suitable_room_types": ["living_room", "hall"],
        "image_path": "/images/interiors/int_lr_05.jpg",
        "wall_finish_default": "Terracotta & brass filigree accent wall with silk emulsion",
        "flooring_default": "Polished Indian marble with brass border inlays",
        "ceiling_concept": "Decorative wooden rafter ceiling insets with warm LED backlighting",
        "lighting_concept": "Traditional brass hanging pendant cluster + modern COB downlights",
        "furniture_concept": "Carved teakwood diwan/sofa with jewel-toned cushions and brass-rimmed center table",
        "fixtures_and_materials": ["Solid teakwood", "Laser-cut solid brass jaali", "Raw silk textiles"],
        "cost_parameters": {
            "wall_paneling_rate_sqft": 390.0,
            "wall_paneling_area_sqft": 80.0,
            "false_ceiling_rate_sqft": 160.0,
            "lighting_lump_sum": 32000.0,
            "tv_unit_lump_sum": 52000.0,
            "furniture_allowance": 190000.0
        },
        "limitations_and_assumptions": [
            "Brass jaali requires periodic anti-tarnish polishing."
        ]
    },
    {
        "id": "int_lr_06",
        "name": "Compact Budget-Friendly Living Room",
        "category": "living_room",
        "style": "Budget-Friendly",
        "budget_tier": "Economy",
        "description": "Clean, light-filled minimalist layout with birchwood laminate wall shelves, compact 3-seater sofa, and smart LED track light illumination.",
        "suitable_room_types": ["living_room", "hall"],
        "image_path": "/images/interiors/int_lr_06.jpg",
        "wall_finish_default": "Warm white premium emulsion with soft grey painted accent niche",
        "flooring_default": "Double-charged vitrified floor tiles (2'x2')",
        "ceiling_concept": "Flat plaster finish with simple perimeter cornice moulding",
        "lighting_concept": "4-point surface mount LED downlights + slender floor lamp",
        "furniture_concept": "Compact 3-seater track-arm fabric sofa with nesting round coffee tables",
        "fixtures_and_materials": ["Engineered pre-laminated wood", "Powder-coated steel", "Linen-blend fabric"],
        "cost_parameters": {
            "wall_paneling_rate_sqft": 120.0,
            "wall_paneling_area_sqft": 40.0,
            "false_ceiling_rate_sqft": 85.0,
            "lighting_lump_sum": 10000.0,
            "tv_unit_lump_sum": 18000.0,
            "furniture_allowance": 60000.0
        },
        "limitations_and_assumptions": [
            "Optimized for living rooms between 140 to 200 sq ft."
        ]
    },

    # ── 3. KITCHEN (6 Designs) ───────────────────────────────────────────────
    {
        "id": "int_kit_01",
        "name": "Modern Modular Kitchen",
        "category": "kitchen",
        "style": "Modern Modular",
        "budget_tier": "Premium",
        "description": "Handleless high-gloss acrylic modular cabinets, pure white quartz countertop with undermount double sink, and continuous under-cabinet LED task light.",
        "suitable_room_types": ["kitchen"],
        "image_path": "/images/interiors/int_kit_01.jpg",
        "wall_finish_default": "Large-format glazed porcelain subway tile backsplash (24'x12')",
        "flooring_default": "Anti-skid matte vitrified floor tiles (2'x2')",
        "ceiling_concept": "Moisture-resistant gypsum false ceiling with recessed anti-glare spots",
        "lighting_concept": "Continuous 4000K neutral white under-cabinet task LED strip + ceiling spots",
        "furniture_concept": "High-gloss acrylic base & wall cabinets with soft-close German tandem drawers",
        "fixtures_and_materials": ["High-gloss acrylic shutters", "Nano-crystallized quartz counter", "Blum tandem box hardware"],
        "cost_parameters": {
            "modular_cabinets_rate_rft": 3200.0,
            "quartz_countertop_rate_sqft": 420.0,
            "false_ceiling_rate_sqft": 140.0,
            "hardware_and_baskets_lump_sum": 35000.0,
            "chimney_hob_allowance": 42000.0
        },
        "limitations_and_assumptions": [
            "Requires moisture-resistant green gypsum board for ceiling."
        ]
    },
    {
        "id": "int_kit_02",
        "name": "L-Shaped Kitchen",
        "category": "kitchen",
        "style": "L-Shaped",
        "budget_tier": "Mid-Range",
        "description": "Ergonomic L-shaped work triangle with sage green matte cabinetry, Calacatta quartz backsplash, fluted glass overhead display, and brushed brass bar pulls.",
        "suitable_room_types": ["kitchen"],
        "image_path": "/images/interiors/int_kit_02.jpg",
        "wall_finish_default": "Calacatta gold quartz continuous slab backsplash",
        "flooring_default": "Anti-slip rectified porcelain tiles (light grey)",
        "ceiling_concept": "Perimeter drop ceiling with centered ceiling flush mount fixture",
        "lighting_concept": "Overhead LED downlights + under-shelf warm strip accents",
        "furniture_concept": "L-shaped base cabinet run with magic corner pull-out carousels and tall pantry unit",
        "fixtures_and_materials": ["Matte PU lacquer finish", "Calacatta engineered quartz", "Brass hardware"],
        "cost_parameters": {
            "modular_cabinets_rate_rft": 2800.0,
            "quartz_countertop_rate_sqft": 380.0,
            "false_ceiling_rate_sqft": 130.0,
            "hardware_and_baskets_lump_sum": 28000.0,
            "chimney_hob_allowance": 35000.0
        },
        "limitations_and_assumptions": [
            "Best suited for corner kitchens with two perpendicular walls >= 8 ft each."
        ]
    },
    {
        "id": "int_kit_03",
        "name": "U-Shaped Kitchen",
        "category": "kitchen",
        "style": "U-Shaped",
        "budget_tier": "Luxury",
        "description": "Gourmet chef's kitchen with continuous U-countertop, deep navy blue shaker cabinets, central breakfast counter, built-in microwave oven tower, and commercial chimney.",
        "suitable_room_types": ["kitchen"],
        "image_path": "/images/interiors/int_kit_03.jpg",
        "wall_finish_default": "Full-height herringbone marble tile backsplash with brass edge trims",
        "flooring_default": "Large format matte stone-finish vitrified tiles",
        "ceiling_concept": "Architectural false ceiling with dedicated kitchen task lighting grids",
        "lighting_concept": "High-CRI 4000K COB downlights + island pendant lighting cluster",
        "furniture_concept": "Tri-wall modular cabinetry, twin corner carousel units, and integrated spice pullouts",
        "fixtures_and_materials": ["Solid wood shaker profiles", "Composite quartz stone", "Heavy-duty pantry larder"],
        "cost_parameters": {
            "modular_cabinets_rate_rft": 3800.0,
            "quartz_countertop_rate_sqft": 450.0,
            "false_ceiling_rate_sqft": 150.0,
            "hardware_and_baskets_lump_sum": 45000.0,
            "chimney_hob_allowance": 55000.0
        },
        "limitations_and_assumptions": [
            "Requires minimum kitchen clear width >= 8.5 ft to avoid cramped movement between opposing counters."
        ]
    },
    {
        "id": "int_kit_04",
        "name": "Parallel Kitchen",
        "category": "kitchen",
        "style": "Parallel Galley",
        "budget_tier": "Mid-Range",
        "description": "Two parallel counter runs separating wet prep and dry cooking zones with two-tone charcoal and white cabinetry, maximizing aisle efficiency.",
        "suitable_room_types": ["kitchen"],
        "image_path": "/images/interiors/int_kit_04.jpg",
        "wall_finish_default": "Vertical stacked white ceramic subway tiles",
        "flooring_default": "Stain-resistant vitrified tiles",
        "ceiling_concept": "Clean moisture-resistant gypsum drop",
        "lighting_concept": "Parallel twin LED magnetic track channels focused on each counter run",
        "furniture_concept": "Two opposing 10-ft counter runs with tall pantry unit and dedicated refrigerator alcove",
        "fixtures_and_materials": ["Anti-fingerprint thermal laminate", "Black granite / quartz", "SS 304 wire baskets"],
        "cost_parameters": {
            "modular_cabinets_rate_rft": 2600.0,
            "quartz_countertop_rate_sqft": 340.0,
            "false_ceiling_rate_sqft": 125.0,
            "hardware_and_baskets_lump_sum": 25000.0,
            "chimney_hob_allowance": 32000.0
        },
        "limitations_and_assumptions": [
            "Requires minimum 7.5 ft clear room width (two 2-ft counters + 3.5-ft central corridor)."
        ]
    },
    {
        "id": "int_kit_05",
        "name": "Premium Finish Kitchen",
        "category": "kitchen",
        "style": "Premium Finish",
        "budget_tier": "Luxury",
        "description": "Smoked walnut veneer lower cabinetry, fluted glass illuminated overheads, waterfall edge Brazilian granite island, and built-in luxury wine chiller niche.",
        "suitable_room_types": ["kitchen"],
        "image_path": "/images/interiors/int_kit_05.jpg",
        "wall_finish_default": "Full slab bookmatched granite / quartz seamless backsplash",
        "flooring_default": "Imported seamless flamed granite / terrazzo slabs",
        "ceiling_concept": "Recessed wooden trim ceiling with concealed micro-linear spots",
        "lighting_concept": "Concealed LED edge profiles inside every glass cabinet + designer pendant",
        "furniture_concept": "Veneer lower cabinets, motorized touch-to-open overheads, waterfall island with bar seating",
        "fixtures_and_materials": ["Smoked walnut veneer", "Italian sintered stone", "Servo-drive motorized hardware"],
        "cost_parameters": {
            "modular_cabinets_rate_rft": 4500.0,
            "quartz_countertop_rate_sqft": 550.0,
            "false_ceiling_rate_sqft": 170.0,
            "hardware_and_baskets_lump_sum": 65000.0,
            "chimney_hob_allowance": 75000.0
        },
        "limitations_and_assumptions": [
            "Recommended for kitchen areas >= 130 sq ft with dedicated dining or island space."
        ]
    },
    {
        "id": "int_kit_06",
        "name": "Budget-Friendly Modular Kitchen",
        "category": "kitchen",
        "style": "Budget-Friendly",
        "budget_tier": "Economy",
        "description": "Sturdy, long-lasting woodgrain laminate shutters, polished black granite countertop with pre-formed edge, and durable stainless steel wire pull-out baskets.",
        "suitable_room_types": ["kitchen"],
        "image_path": "/images/interiors/int_kit_06.jpg",
        "wall_finish_default": "Glazed ceramic dado wall tiles up to 2 ft above counter",
        "flooring_default": "Standard non-skid ceramic floor tiles",
        "ceiling_concept": "Standard plaster and whitewash ceiling",
        "lighting_concept": "Central LED batten + 2 surface-mounted spotlights above sink and hob",
        "furniture_concept": "Modular base and wall storage cabinets with stainless steel bar handles",
        "fixtures_and_materials": ["1mm high-pressure decorative laminate", "Black granite counter", "SS wire baskets"],
        "cost_parameters": {
            "modular_cabinets_rate_rft": 1850.0,
            "quartz_countertop_rate_sqft": 190.0,
            "false_ceiling_rate_sqft": 80.0,
            "hardware_and_baskets_lump_sum": 16000.0,
            "chimney_hob_allowance": 22000.0
        },
        "limitations_and_assumptions": [
            "Highly durable economical finish; uses baseline granite with no false ceiling requirement."
        ]
    },

    # ── 4. GUEST ROOM (4 Designs) ────────────────────────────────────────────
    {
        "id": "int_guest_01",
        "name": "Modern Guest Room",
        "category": "guest_room",
        "style": "Modern",
        "budget_tier": "Mid-Range",
        "description": "Welcoming, clutter-free contemporary guest room with upholstered queen bed, compact 3-door wardrobe, luggage bench, and reading lights.",
        "suitable_room_types": ["guest_room", "bedroom"],
        "image_path": "/images/interiors/int_guest_01.jpg",
        "wall_finish_default": "Warm light grey velvet emulsion with wood trim accent wall",
        "flooring_default": "Double-charged vitrified floor tiles (2'x2')",
        "ceiling_concept": "Perimeter gypsum false ceiling with warm 3000K recessed spots",
        "lighting_concept": "Anti-glare ceiling spotlights + twin flexible bedside reading sconces",
        "furniture_concept": "Queen-size upholstered bed, luggage bench with drawers, and 3-door wardrobe",
        "fixtures_and_materials": ["Textured laminate", "Upholstered fabric", "Matte black hardware"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1450.0,
            "wardrobe_width_ft": 5.5,
            "bed_headboard_lump_sum": 20000.0,
            "false_ceiling_rate_sqft": 125.0,
            "lighting_lump_sum": 12000.0,
            "hardware_lump_sum": 8000.0
        },
        "limitations_and_assumptions": [
            "Compact layout designed for comfortable short to medium term guest stays."
        ]
    },
    {
        "id": "int_guest_02",
        "name": "Minimalist Guest Room",
        "category": "guest_room",
        "style": "Minimalist",
        "budget_tier": "Mid-Range",
        "description": "Zen-like simplicity with low wooden platform bed, soft cream limewash walls, open hanging clothes rail with lower drawers, and tranquil indirect lighting.",
        "suitable_room_types": ["guest_room", "bedroom"],
        "image_path": "/images/interiors/int_guest_02.jpg",
        "wall_finish_default": "Artisanal cream limewash paint finish",
        "flooring_default": "Matte natural woodgrain tiles",
        "ceiling_concept": "Flat clean ceiling with recessed soft cove perimeter",
        "lighting_concept": "Concealed headboard wash + warm paper globe pendant",
        "furniture_concept": "Minimalist solid wood queen bed with integrated side shelves and open wardrobe rail",
        "fixtures_and_materials": ["Solid rubberwood / ash", "Natural linen bedding", "Textured plaster"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1300.0,
            "wardrobe_width_ft": 5.0,
            "bed_headboard_lump_sum": 18000.0,
            "false_ceiling_rate_sqft": 115.0,
            "lighting_lump_sum": 11000.0,
            "hardware_lump_sum": 7000.0
        },
        "limitations_and_assumptions": [
            "Prioritizes open floor area and airy ambiance over extensive enclosed cabinetry."
        ]
    },
    {
        "id": "int_guest_03",
        "name": "Warm Neutral Guest Room",
        "category": "guest_room",
        "style": "Warm Neutral",
        "budget_tier": "Premium",
        "description": "Inviting beige and taupe palette with cushioned fabric headboard, walnut laminate wardrobe, bedside pendant lights, and plush area rug.",
        "suitable_room_types": ["guest_room", "bedroom"],
        "image_path": "/images/interiors/int_guest_03.jpg",
        "wall_finish_default": "Warm taupe royal emulsion with vertical wooden moulding strips",
        "flooring_default": "Warm engineered oak flooring / luxury vitrified tiles",
        "ceiling_concept": "Perimeter drop ceiling with soft diffused indirect cove",
        "lighting_concept": "Dimmable ceiling spotlights + designer cylindrical bedside pendants",
        "furniture_concept": "Queen bed with beige cushioned headboard, built-in wardrobe, and mini vanity desk",
        "fixtures_and_materials": ["Walnut laminate", "Brushed champagne trims", "Woven wool area rug"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1650.0,
            "wardrobe_width_ft": 6.0,
            "bed_headboard_lump_sum": 24000.0,
            "false_ceiling_rate_sqft": 135.0,
            "lighting_lump_sum": 15000.0,
            "hardware_lump_sum": 10000.0
        },
        "limitations_and_assumptions": [
            "Versatile layout adaptable for multi-generational family guests."
        ]
    },
    {
        "id": "int_guest_04",
        "name": "Compact Multipurpose Guest Room",
        "category": "guest_room",
        "style": "Multipurpose",
        "budget_tier": "Economy",
        "description": "Dual-purpose space serving as a dedicated home office that effortlessly converts into a guest bedroom with daybed/sofa-cum-bed and study credenza.",
        "suitable_room_types": ["guest_room", "bedroom", "study_room"],
        "image_path": "/images/interiors/int_guest_04.jpg",
        "wall_finish_default": "Durable acrylic washable paint with geometric accent wall",
        "flooring_default": "Matte vitrified ceramic tiles",
        "ceiling_concept": "Clean flat ceiling with flush LED panel lighting",
        "lighting_concept": "Bright 4000K study desk task light + warm 3000K relaxing evening spots",
        "furniture_concept": "Convertible queen sofa-cum-bed / daybed with storage, plus integrated 4-ft study desk",
        "fixtures_and_materials": ["Engineered pre-laminated boards", "High-density foam mattress", "Powder-coated steel"],
        "cost_parameters": {
            "wardrobe_rate_sqft": 1250.0,
            "wardrobe_width_ft": 5.0,
            "bed_headboard_lump_sum": 16000.0,
            "study_unit_lump_sum": 14000.0,
            "false_ceiling_rate_sqft": 95.0,
            "lighting_lump_sum": 9000.0,
            "hardware_lump_sum": 7000.0
        },
        "limitations_and_assumptions": [
            "Optimal solution for homes requiring occasional guest accommodation and daily home-office utility."
        ]
    },

    # ── 5. BATHROOM (4 Designs) ──────────────────────────────────────────────
    {
        "id": "int_bath_01",
        "name": "Modern Minimalist Bathroom",
        "category": "bathroom",
        "style": "Modern Minimalist",
        "budget_tier": "Mid-Range",
        "description": "Floating oak vanity unit with ceramic basin, round LED backlit mirror, matte black wall-mounted faucets, and concealed dual-flush toilet tank.",
        "suitable_room_types": ["bathroom", "toilet"],
        "image_path": "/images/interiors/int_bath_01.jpg",
        "wall_finish_default": "Large-format light grey concrete-look porcelain wall tiles up to false ceiling",
        "flooring_default": "Matching anti-skid floor tiles with zero-step shower threshold",
        "ceiling_concept": "Moisture-resistant gypsum false ceiling with anti-moisture downlights",
        "lighting_concept": "Round halo LED backlit mirror + IP65 ceiling moisture downlights",
        "furniture_concept": "32-inch floating waterproof vanity unit with dual soft-close drawers",
        "fixtures_and_materials": ["Waterproof marine plywood vanity", "Matte black CP fittings", "Concealed cistern"],
        "cost_parameters": {
            "vanity_lump_sum": 24000.0,
            "shower_glass_lump_sum": 16000.0,
            "false_ceiling_rate_sqft": 135.0,
            "fittings_differential_lump_sum": 18000.0
        },
        "limitations_and_assumptions": [
            "Concealed cistern requires minimum 4.5 inch wall chase or false duct plumbing."
        ]
    },
    {
        "id": "int_bath_02",
        "name": "Premium Stone-Finish Bathroom",
        "category": "bathroom",
        "style": "Premium Stone",
        "budget_tier": "Luxury",
        "description": "Full-height Carrara marble wall tiles, brushed gold thermostatic shower mixer, marble vanity counter, frameless 10mm glass enclosure, and designer niche shelf.",
        "suitable_room_types": ["bathroom", "toilet"],
        "image_path": "/images/interiors/int_bath_02.jpg",
        "wall_finish_default": "Full-height polished Carrara marble glazed porcelain slabs",
        "flooring_default": "Flamed anti-skid granite / textured marble floor tiles",
        "ceiling_concept": "Moisture-resistant gypsum with recessed gold cove lighting wash",
        "lighting_concept": "Warm perimeter ceiling cove wash + embedded LED shower niche strip",
        "furniture_concept": "42-inch marble-topped floating double vanity with brushed gold metal legs",
        "fixtures_and_materials": ["Carrara porcelain slabs", "Brushed gold PVD shower fixtures", "10mm toughened glass"],
        "cost_parameters": {
            "vanity_lump_sum": 38000.0,
            "shower_glass_lump_sum": 24000.0,
            "false_ceiling_rate_sqft": 160.0,
            "fittings_differential_lump_sum": 32000.0
        },
        "limitations_and_assumptions": [
            "Recommended for bathrooms >= 45 sq ft to comfortably accommodate separate wet and dry zones."
        ]
    },
    {
        "id": "int_bath_03",
        "name": "Contemporary Shower Bathroom",
        "category": "bathroom",
        "style": "Contemporary Shower",
        "budget_tier": "Premium",
        "description": "Black crittall-framed glass shower enclosure, oversized ceiling rain shower head, illuminated tile niche, slate grey tiles, and smart anti-fog mirror.",
        "suitable_room_types": ["bathroom", "toilet"],
        "image_path": "/images/interiors/int_bath_03.jpg",
        "wall_finish_default": "Textured charcoal slate tiles with mosaic shower feature wall",
        "flooring_default": "Hexagonal anti-skid charcoal floor tiles",
        "ceiling_concept": "Dark charcoal moisture-resistant gypsum drop",
        "lighting_concept": "Recessed architectural shower spotlights + anti-fog LED mirror",
        "furniture_concept": "Wall-hung vanity with integrated towel shelf and mirror storage cabinet",
        "fixtures_and_materials": ["Crittall grid black aluminum glass", "Rain shower system", "Slate porcelain"],
        "cost_parameters": {
            "vanity_lump_sum": 28000.0,
            "shower_glass_lump_sum": 20000.0,
            "false_ceiling_rate_sqft": 140.0,
            "fittings_differential_lump_sum": 24000.0
        },
        "limitations_and_assumptions": [
            "Rain shower requires minimum 2.5 bar water pressure booster pump."
        ]
    },
    {
        "id": "int_bath_04",
        "name": "Compact Functional Bathroom",
        "category": "bathroom",
        "style": "Compact Functional",
        "budget_tier": "Economy",
        "description": "Smart, highly functional space-saving bathroom layout with corner basin, wall-hung WC, chrome quarter-turn fittings, and full-height white subway tiles.",
        "suitable_room_types": ["bathroom", "toilet"],
        "image_path": "/images/interiors/int_bath_04.jpg",
        "wall_finish_default": "Glossy white ceramic wall tiles up to 7 ft lintel height",
        "flooring_default": "Anti-skid ceramic floor tiles (1'x1')",
        "ceiling_concept": "Plastered ceiling with moisture-resistant paint",
        "lighting_concept": "Overhead vanity light bar + central ceiling moisture dome light",
        "furniture_concept": "Corner floating washbasin with mirrored medicine storage cabinet above",
        "fixtures_and_materials": ["Vitreous china sanitaryware", "Chrome plated brass fittings", "Stainless steel accessories"],
        "cost_parameters": {
            "vanity_lump_sum": 12000.0,
            "shower_glass_lump_sum": 0.0,
            "false_ceiling_rate_sqft": 90.0,
            "fittings_differential_lump_sum": 8000.0
        },
        "limitations_and_assumptions": [
            "Ideal for powder rooms or compact attached bathrooms under 35 sq ft."
        ]
    },

    # ── 6. DINING ROOM (4 Designs) ───────────────────────────────────────────
    {
        "id": "int_din_01",
        "name": "Modern Family Dining Room",
        "category": "dining_room",
        "style": "Modern Family",
        "budget_tier": "Mid-Range",
        "description": "Contemporary 6-seater dining ensemble with solid oak table, upholstered ergonomic dining chairs, trio of smoky glass pendant lights, and built-in crockery unit.",
        "suitable_room_types": ["dining_room", "living_room"],
        "image_path": "/images/interiors/int_din_01.jpg",
        "wall_finish_default": "Neutral eggshell emulsion with framed abstract gallery art wall",
        "flooring_default": "Glazed vitrified tiles with contrasting perimeter border",
        "ceiling_concept": "Recessed ceiling tray centered directly over the dining table",
        "lighting_concept": "Trio of smoky glass linear pendant lamps + warm perimeter spotlights",
        "furniture_concept": "6-seater solid oak dining table, upholstered chairs, and 5-ft low crockery credenza",
        "fixtures_and_materials": ["Solid oak wood", "Smoked glass pendants", "High-density upholstery fabric"],
        "cost_parameters": {
            "crockery_unit_lump_sum": 32000.0,
            "false_ceiling_rate_sqft": 135.0,
            "lighting_lump_sum": 20000.0,
            "furniture_allowance": 85000.0
        },
        "limitations_and_assumptions": [
            "Requires minimum 10 ft x 10 ft space for dining table and 3 ft chair pull-back clearance."
        ]
    },
    {
        "id": "int_din_02",
        "name": "Luxury Dining Room",
        "category": "dining_room",
        "style": "Luxury",
        "budget_tier": "Luxury",
        "description": "Show-stopping Statuario marble dining table with brass pedestal base, 8 velvet dining chairs, multi-ring brass chandelier, and illuminated wine display console.",
        "suitable_room_types": ["dining_room"],
        "image_path": "/images/interiors/int_din_02.jpg",
        "wall_finish_default": "Bookmatched marble feature panel + metallic wallpaper insets",
        "flooring_default": "Imported Italian marble slabs with waterjet medallion",
        "ceiling_concept": "Double-tiered architectural cove with champagne gold leaf accents",
        "lighting_concept": "Designer multi-tier gold ring chandelier with smart dimming circuits",
        "furniture_concept": "8-seater Italian marble top table with brushed brass base, bespoke velvet chairs, tall display bar",
        "fixtures_and_materials": ["Statuario marble slab", "Brushed brass PVD", "Rich velvet fabrics"],
        "cost_parameters": {
            "crockery_unit_lump_sum": 65000.0,
            "false_ceiling_rate_sqft": 170.0,
            "lighting_lump_sum": 45000.0,
            "furniture_allowance": 180000.0
        },
        "limitations_and_assumptions": [
            "Requires minimum 120 sq ft dining room area for proper chair clearance and buffet circulation."
        ]
    },
    {
        "id": "int_din_03",
        "name": "Warm Contemporary Dining Room",
        "category": "dining_room",
        "style": "Warm Contemporary",
        "budget_tier": "Premium",
        "description": "Live-edge natural wood dining table, woven leather strap chairs, acoustic slatted wood feature wall, and warm ceramic pendant fixture.",
        "suitable_room_types": ["dining_room", "living_room"],
        "image_path": "/images/interiors/int_din_03.jpg",
        "wall_finish_default": "Natural walnut wood slatted accent wall with integrated warm backlighting",
        "flooring_default": "Warm hardwood / woodgrain ceramic planks",
        "ceiling_concept": "Gypsum perimeter drop with wooden trim inset",
        "lighting_concept": "Architectural ceramic conical pendant lights + warm 2700K ambient wash",
        "furniture_concept": "Solid acacia live-edge dining table with matte black metal legs and matching bench",
        "fixtures_and_materials": ["Live-edge acacia slab", "Acoustic timber slats", "Natural leather"],
        "cost_parameters": {
            "crockery_unit_lump_sum": 38000.0,
            "false_ceiling_rate_sqft": 145.0,
            "lighting_lump_sum": 24000.0,
            "furniture_allowance": 110000.0
        },
        "limitations_and_assumptions": [
            "Live-edge wooden tables require acclimatization to prevent seasonal moisture warping."
        ]
    },
    {
        "id": "int_din_04",
        "name": "Compact Dining Room",
        "category": "dining_room",
        "style": "Compact",
        "budget_tier": "Economy",
        "description": "Space-saving breakfast/dining nook with 4-seater round pedestal table, space-efficient curved molded chairs, and wall-mounted fold-down buffet shelf.",
        "suitable_room_types": ["dining_room", "kitchen", "living_room"],
        "image_path": "/images/interiors/int_din_04.jpg",
        "wall_finish_default": "Light pastel accent wall with floating display ledges",
        "flooring_default": "Polished vitrified floor tiles",
        "ceiling_concept": "Flat clean ceiling with centered drop pendant",
        "lighting_concept": "Single statement Scandinavian pendant centered over round table",
        "furniture_concept": "42-inch round tulip dining table with 4 ergonomic shell chairs",
        "fixtures_and_materials": ["Molded polypropylene", "Laminated composite top", "Powder-coated aluminum"],
        "cost_parameters": {
            "crockery_unit_lump_sum": 16000.0,
            "false_ceiling_rate_sqft": 90.0,
            "lighting_lump_sum": 10000.0,
            "furniture_allowance": 35000.0
        },
        "limitations_and_assumptions": [
            "Ideal for compact dining corners or open-plan living-dining layouts down to 64 sq ft."
        ]
    }
]


def get_all_interior_designs() -> List[InteriorDesignOption]:
    """Returns all 32 distinct interior design catalog options as validated Pydantic models."""
    return [InteriorDesignOption(**d) for d in INTERIOR_CATALOG_DATA]


def get_interior_design_by_id(design_id: str) -> Optional[InteriorDesignOption]:
    """Looks up a design by its unique ID."""
    for d in INTERIOR_CATALOG_DATA:
        if d["id"] == design_id:
            return InteriorDesignOption(**d)
    return None


def get_designs_by_category(category: str) -> List[InteriorDesignOption]:
    """Filters designs by category."""
    return [InteriorDesignOption(**d) for d in INTERIOR_CATALOG_DATA if d["category"] == category]
