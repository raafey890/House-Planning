"""
Exterior Design Catalog — Phase 6F.1.
Contains exactly 32 distinct exterior design options organized into eight categories:
1. Modern Contemporary (ext_mod_01 to ext_mod_04)
2. Minimalist (ext_min_01 to ext_min_04)
3. Luxury Villa (ext_lux_01 to ext_lux_04)
4. Traditional Indian (ext_trad_01 to ext_trad_04)
5. Indian Modern (ext_indmod_01 to ext_indmod_04)
6. Mediterranean (ext_med_01 to ext_med_04)
7. Tropical Contemporary (ext_trop_01 to ext_trop_04)
8. Premium Duplex (ext_dup_01 to ext_dup_04)
"""

from typing import List, Optional, Dict, Any
from app.models.exterior_design import ExteriorDesignOption

EXTERIOR_CATEGORIES = [
    {"id": "modern_contemporary", "name": "Modern Contemporary", "description": "Sleek geometric volumes, cantilevered slabs, and expansive floor-to-ceiling glass."},
    {"id": "minimalist", "name": "Minimalist", "description": "Clean monolithic masses, concealed gutters, pure white stucco, and raw materials."},
    {"id": "luxury_villa", "name": "Luxury Villa", "description": "Opulent travertine cladding, double-height entrance porticos, and champage gold accents."},
    {"id": "traditional_indian", "name": "Traditional Indian", "description": "Sloping Mangalore clay tile roofs, carved teak brackets, Charupadi verandas, and haveli jharokhas."},
    {"id": "indian_modern", "name": "Indian Modern", "description": "Modernist form enriched with exposed terracotta jaali screens, wirecut brick, and brass accents."},
    {"id": "mediterranean", "name": "Mediterranean", "description": "Warm ivory stucco, Spanish barrel clay roof accents, forged iron lanterns, and arched loggias."},
    {"id": "tropical_contemporary", "name": "Tropical Contemporary", "description": "Deep overhanging timber eaves, volcanic basalt stone, slatted screens, and biophilic planter boxes."},
    {"id": "premium_duplex", "name": "Premium Duplex", "description": "Staggered multi-level box projections, corner glass windows, and integrated covered car porches."}
]

EXTERIOR_DESIGNS: List[Dict[str, Any]] = [
    # ── CATEGORY 1: MODERN CONTEMPORARY ────────────────────────────────────────
    {
        "id": "ext_mod_01",
        "name": "Geometric Cubic Modern Elevation",
        "category": "modern_contemporary",
        "style": "Modern Contemporary",
        "budget_tier": "Mid-Range",
        "description": "Crisp interlocking cubic masses with charcoal fluted composite louvers, warm limestone-finish base, and floor-to-ceiling double-glazed black aluminum fenestration.",
        "suitable_house_types": ["Independent House", "Villa", "Duplex", "Bungalow"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 40.0, "min_area_sqft": 1200.0, "max_area_sqft": 4500.0},
        "suitable_floor_configs": [1, 2, 3],
        "material_palette": ["Charcoal composite louvers", "Limestone textured paint", "Black anodized aluminum", "Clear laminated glass"],
        "primary_paint_color": {"name": "Bone White Emulsion", "hex": "#F4F4F0"},
        "secondary_paint_color": {"name": "Charcoal Slate", "hex": "#2B313B"},
        "door_and_window_style": "Floor-to-ceiling slim-profile black thermal-break aluminum windows with acoustic double glazing",
        "facade_treatment": "Interlocking cantilevered cubic projection with concealed LED perimeter channel",
        "lighting_style": "Recessed 3000K warm LED soffit downlights + vertical facade wall grazers",
        "balcony_and_railing_style": "12mm frameless toughened glass railing with recessed aluminum base shoe",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_mod_01.jpg",
        "customization_defaults": {
            "finish_type": "textured_paint",
            "cladding_type": "fluted_composite_louvers",
            "door_material": "teak_aluminum_hybrid",
            "boundary_wall_style": "horizontal_slats"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 18.0,
            "cladding_rate_sqft": 280.0,
            "window_upgrade_rate": 15000.0,
            "lighting_package": 22000.0
        }
    },
    {
        "id": "ext_mod_02",
        "name": "Cantilevered Floating Slab Residence",
        "category": "modern_contemporary",
        "style": "Modern Contemporary",
        "budget_tier": "Premium",
        "description": "Dramatic horizontal white concrete slab projections with warm teakwood soffit cladding, recessed shadow-reveal joints, and corner glass bay windows.",
        "suitable_house_types": ["Villa", "Duplex", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 35.0, "min_length_ft": 45.0, "min_area_sqft": 1500.0, "max_area_sqft": 5500.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Off-form white concrete", "Natural teak soffit battens", "Brushed dark bronze frames", "Laminated low-E glass"],
        "primary_paint_color": {"name": "Titanium Frost", "hex": "#ECEFEF"},
        "secondary_paint_color": {"name": "Teak Amber Accent", "hex": "#8B5A2B"},
        "door_and_window_style": "Concealed-subframe dark bronze structural glazing with pivot front door",
        "facade_treatment": "3.5-ft deep horizontal floating cantilevered slab with concealed drip edge and warm linear LED strip",
        "lighting_style": "Continuous warm 2700K indirect cove light under cantilevered overhangs",
        "balcony_and_railing_style": "Structural glass balustrade with brushed champagne cap profile",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_mod_02.jpg",
        "customization_defaults": {
            "finish_type": "smooth_stucco",
            "cladding_type": "natural_teak_soffit",
            "door_material": "pivot_teak",
            "boundary_wall_style": "floating_concrete"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 24.0,
            "cladding_rate_sqft": 360.0,
            "window_upgrade_rate": 30000.0,
            "lighting_package": 28000.0
        }
    },
    {
        "id": "ext_mod_03",
        "name": "Asymmetrical Metal & Glass Villa",
        "category": "modern_contemporary",
        "style": "Modern Contemporary",
        "budget_tier": "Luxury",
        "description": "Striking architectural elevation featuring a dramatic diagonal roofline prow, weathered Corten steel accent paneling, and a double-height curtain wall.",
        "suitable_house_types": ["Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 40.0, "min_length_ft": 50.0, "min_area_sqft": 2000.0, "max_area_sqft": 7000.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Weathered Corten steel", "Double-height structural glass", "Matte graphite panels", "Polished basalt base"],
        "primary_paint_color": {"name": "Industrial Platinum", "hex": "#D8DCE0"},
        "secondary_paint_color": {"name": "Rust Corten Orange", "hex": "#A24823"},
        "door_and_window_style": "Motorized acoustic sliding curtain wall with 10-ft oversized metal entrance pivot door",
        "facade_treatment": "Angular diagonal prow framing double-height entry void with architectural metal fins",
        "lighting_style": "Narrow-beam 15-degree architectural spot columns accentuating Corten patina",
        "balcony_and_railing_style": "Matte black powder-coated steel flat-bar railing with timber handrail",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_mod_03.jpg",
        "customization_defaults": {
            "finish_type": "metal_cladding",
            "cladding_type": "corten_steel_panels",
            "door_material": "oversized_metal_pivot",
            "boundary_wall_style": "corten_and_stone"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 32.0,
            "cladding_rate_sqft": 480.0,
            "window_upgrade_rate": 55000.0,
            "lighting_package": 42000.0
        }
    },
    {
        "id": "ext_mod_04",
        "name": "Monolithic Quartzite & Steel House",
        "category": "modern_contemporary",
        "style": "Modern Contemporary",
        "budget_tier": "Premium",
        "description": "Monolithic two-story massing cladded in large-format light silver quartzite stone slabs, highlighted by black steel pergolas and a floating entrance canopy.",
        "suitable_house_types": ["Independent House", "Duplex", "Bungalow"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 40.0, "min_area_sqft": 1200.0, "max_area_sqft": 4000.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Silver quartzite stone slabs", "Black structural steel I-beams", "Warm grey acrylic plaster", "Tinted solar glass"],
        "primary_paint_color": {"name": "Pale Pebble Grey", "hex": "#E2E4E6"},
        "secondary_paint_color": {"name": "Black Obsidian", "hex": "#1C1F24"},
        "door_and_window_style": "Black powder-coated aluminum double-casement windows with steel lintel covers",
        "facade_treatment": "Large-format vertical quartzite stone slab feature wall anchored by steel pergola",
        "lighting_style": "Warm LED linear wall-washers integrated beneath stone reveals and pergola rafters",
        "balcony_and_railing_style": "Minimalist black stainless steel cable railing with low-profile stanchions",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_mod_04.jpg",
        "customization_defaults": {
            "finish_type": "stone_cladding",
            "cladding_type": "silver_quartzite_slabs",
            "door_material": "steel_accent_timber",
            "boundary_wall_style": "stone_pillar_steel_slats"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 22.0,
            "cladding_rate_sqft": 340.0,
            "window_upgrade_rate": 28000.0,
            "lighting_package": 26000.0
        }
    },

    # ── CATEGORY 2: MINIMALIST ────────────────────────────────────────────────
    {
        "id": "ext_min_01",
        "name": "Pure White Minimalist Cube",
        "category": "minimalist",
        "style": "Minimalist",
        "budget_tier": "Mid-Range",
        "description": "Ultra-clean seamless white mineral stucco facade, razor-sharp edge profiles, hidden downspouts, and deep-set square fenestrations with black accent frames.",
        "suitable_house_types": ["Independent House", "Bungalow", "Duplex", "Row House"],
        "recommended_plot_size": {"min_width_ft": 25.0, "min_length_ft": 35.0, "min_area_sqft": 900.0, "max_area_sqft": 3500.0},
        "suitable_floor_configs": [1, 2, 3],
        "material_palette": ["Self-cleaning silicone white stucco", "Slim-line black aluminum", "Flush acoustic paneling", "Porcelain paving"],
        "primary_paint_color": {"name": "Pure Arctic White", "hex": "#FAFAFA"},
        "secondary_paint_color": {"name": "Matte Jet Black", "hex": "#18181B"},
        "door_and_window_style": "Deeply recessed black powder-coated aluminum picture windows with frameless sills",
        "facade_treatment": "Crisp geometric parapet with concealed drainage and flush-mounted hidden garage gate",
        "lighting_style": "Concealed micro-aperture soffit downlights creating clean circular pools of 3000K light",
        "balcony_and_railing_style": "Solid white parapet wall with top recess line (no visible railings)",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_min_01.jpg",
        "customization_defaults": {
            "finish_type": "silicone_mineral_stucco",
            "cladding_type": "none",
            "door_material": "flush_white_laminate",
            "boundary_wall_style": "monolithic_white"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 20.0,
            "cladding_rate_sqft": 0.0,
            "window_upgrade_rate": 18000.0,
            "lighting_package": 16000.0
        }
    },
    {
        "id": "ext_min_02",
        "name": "Raw Exposed Concrete Brutalist-Minimal",
        "category": "minimalist",
        "style": "Minimalist",
        "budget_tier": "Premium",
        "description": "Architectural board-marked raw exposed concrete walling with visible tie-rod holes, recessed vertical slit windows, and a warm solid oak entrance door.",
        "suitable_house_types": ["Villa", "Independent House", "Duplex"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 40.0, "min_area_sqft": 1200.0, "max_area_sqft": 5000.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Board-formed architectural concrete", "Solid natural oak", "Blackened steel", "Frosted cast glass"],
        "primary_paint_color": {"name": "Raw Concrete Neutral", "hex": "#D1D5DB"},
        "secondary_paint_color": {"name": "Natural White Oak", "hex": "#C49A6C"},
        "door_and_window_style": "Narrow vertical ribbon fenestrations with thermal-break graphite steel frames",
        "facade_treatment": "Textured horizontal timber board grain imprinted into concrete formwork",
        "lighting_style": "Recessed base step lights and soft graze lighting against concrete texture",
        "balcony_and_railing_style": "Solid cantilevered concrete upstand wall matching the facade",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_min_02.jpg",
        "customization_defaults": {
            "finish_type": "exposed_concrete_finish",
            "cladding_type": "board_marked_panels",
            "door_material": "solid_white_oak",
            "boundary_wall_style": "concrete_board_formed"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 28.0,
            "cladding_rate_sqft": 320.0,
            "window_upgrade_rate": 22000.0,
            "lighting_package": 24000.0
        }
    },
    {
        "id": "ext_min_03",
        "name": "Scandinavian Nordic Slate Minimal",
        "category": "minimalist",
        "style": "Minimalist",
        "budget_tier": "Mid-Range",
        "description": "Calm Nordic aesthetic combining smooth pale limestone plaster with vertical light-ash timber louvers, black standing-seam accents, and slim Nordic doors.",
        "suitable_house_types": ["Independent House", "Row House", "Bungalow"],
        "recommended_plot_size": {"min_width_ft": 25.0, "min_length_ft": 40.0, "min_area_sqft": 1000.0, "max_area_sqft": 3800.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Nordic limestone plaster", "Vertical ash timber battens", "Anthracite zinc panels", "Double-glazed acoustic timber windows"],
        "primary_paint_color": {"name": "Nordic Birch Stucco", "hex": "#EDEBE6"},
        "secondary_paint_color": {"name": "Anthracite Grey", "hex": "#374151"},
        "door_and_window_style": "Triple-glazed timber-aluminum composite windows in anthracite finish",
        "facade_treatment": "Vertical timber batten privacy screen set against smooth limestone surface",
        "lighting_style": "Minimalist black Scandinavian cylinder wall sconces with bi-directional beams",
        "balcony_and_railing_style": "Slender vertical black steel pickets with natural ash handrail",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_min_03.jpg",
        "customization_defaults": {
            "finish_type": "nordic_lime_stucco",
            "cladding_type": "ash_timber_battens",
            "door_material": "anthracite_timber_composite",
            "boundary_wall_style": "ash_slats_anthracite_frame"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 19.0,
            "cladding_rate_sqft": 290.0,
            "window_upgrade_rate": 24000.0,
            "lighting_package": 18000.0
        }
    },
    {
        "id": "ext_min_04",
        "name": "Zen Monochromatic Pavilion",
        "category": "minimalist",
        "style": "Minimalist",
        "budget_tier": "Premium",
        "description": "Japanese modernism with deep charcoal matte base, bone-white upper volume, fine cedar vertical lattice screens, and a minimalist gravel courtyard entry.",
        "suitable_house_types": ["Independent House", "Villa", "Duplex"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 45.0, "min_area_sqft": 1350.0, "max_area_sqft": 4800.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Japanese burnt cedar (shou sugi ban)", "Textured bone white plaster", "Black river stone", "Clear low-iron glass"],
        "primary_paint_color": {"name": "Warm Bone White", "hex": "#F3F1EC"},
        "secondary_paint_color": {"name": "Charcoal Shou Sugi", "hex": "#1E2024"},
        "door_and_window_style": "Concealed sliding glass screens with fine dark cedar exterior privacy lattice",
        "facade_treatment": "Monochromatic split with dark textured lower plinth and weightless white upper volume",
        "lighting_style": "Low-level pathway wash lights and soft diffuse backlit timber lattice illumination",
        "balcony_and_railing_style": "Concealed glass balustrade behind cedar privacy screen",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_min_04.jpg",
        "customization_defaults": {
            "finish_type": "bone_white_plaster",
            "cladding_type": "shou_sugi_ban_cedar",
            "door_material": "japanese_cedar_pivot",
            "boundary_wall_style": "dark_cedar_lattice"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 25.0,
            "cladding_rate_sqft": 380.0,
            "window_upgrade_rate": 32000.0,
            "lighting_package": 30000.0
        }
    },

    # ── CATEGORY 3: LUXURY VILLA ──────────────────────────────────────────────
    {
        "id": "ext_lux_01",
        "name": "Grand Imperial Marble Villa",
        "category": "luxury_villa",
        "style": "Luxury Villa",
        "budget_tier": "Luxury",
        "description": "Opulent Italian Roman Travertine exterior slab cladding with champagne gold PVD metal accents, double-height grand entrance canopy, and water-feature approach.",
        "suitable_house_types": ["Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 45.0, "min_length_ft": 60.0, "min_area_sqft": 2700.0, "max_area_sqft": 10000.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Italian Roman Travertine stone", "Champagne gold PVD trims", "Double-glazed acoustic low-iron glass", "Polished granite entry plinth"],
        "primary_paint_color": {"name": "Travertine Beige", "hex": "#E6DEC8"},
        "secondary_paint_color": {"name": "Champagne Gold Accent", "hex": "#B89758"},
        "door_and_window_style": "Double-height 18-ft structural curtain wall with motorized gold-accented pivot entrance door",
        "facade_treatment": "Mechanical dry-clad Travertine slab walling with 10mm gold metallic reveal shadowlines",
        "lighting_style": "Multi-tier 2700K warm architectural lighting with concealed vertical cove wash along stone slabs",
        "balcony_and_railing_style": "15mm ultra-clear laminated glass with champagne gold PVD handrail channel",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_lux_01.jpg",
        "customization_defaults": {
            "finish_type": "travertine_stone_dry_clad",
            "cladding_type": "italian_roman_travertine",
            "door_material": "champagne_gold_pvd_pivot",
            "boundary_wall_style": "travertine_and_gold_grille"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 35.0,
            "cladding_rate_sqft": 620.0,
            "window_upgrade_rate": 75000.0,
            "lighting_package": 65000.0
        }
    },
    {
        "id": "ext_lux_02",
        "name": "Contemporary Tuscan Luxury Manor",
        "category": "luxury_villa",
        "style": "Luxury Villa",
        "budget_tier": "Luxury",
        "description": "Hand-chiseled golden sandstone masonry combined with contemporary bronze arched windows, terracotta roof coping, and antique brass fixtures.",
        "suitable_house_types": ["Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 40.0, "min_length_ft": 55.0, "min_area_sqft": 2200.0, "max_area_sqft": 8000.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Hand-chiseled Dholpur/Tuscan sandstone", "Antiqued bronze aluminum", "Terracotta roof tile coping", "Reclaimed solid teak"],
        "primary_paint_color": {"name": "Warm Tuscan Cream", "hex": "#EDE5D1"},
        "secondary_paint_color": {"name": "Antique Bronze", "hex": "#4A3B32"},
        "door_and_window_style": "Graceful modern segmented-arch bronze windows with insulated double-glazing",
        "facade_treatment": "Heavy textured dry-stone masonry with smooth limestone lintels and modern bronze portals",
        "lighting_style": "Handcrafted antique brass exterior carriage lanterns and discrete stone-wash uplights",
        "balcony_and_railing_style": "Hand-forged solid iron balustrades with bronze medallions",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_lux_02.jpg",
        "customization_defaults": {
            "finish_type": "hand_chiseled_stone",
            "cladding_type": "golden_sandstone_masonry",
            "door_material": "arched_reclaimed_teak",
            "boundary_wall_style": "chiseled_stone_with_iron_gates"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 28.0,
            "cladding_rate_sqft": 540.0,
            "window_upgrade_rate": 60000.0,
            "lighting_package": 48000.0
        }
    },
    {
        "id": "ext_lux_03",
        "name": "Ultra-Luxury Infinity View Estate",
        "category": "luxury_villa",
        "style": "Luxury Villa",
        "budget_tier": "Luxury",
        "description": "Breathtaking full-width frameless glass cantilevered balconies, illuminated Brazilian quartzite stone feature slab, and motorized cascading water wall.",
        "suitable_house_types": ["Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 45.0, "min_length_ft": 60.0, "min_area_sqft": 2700.0, "max_area_sqft": 9500.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Translucent backlit quartzite", "Brushed titanium-grey frames", "Frameless low-iron glass", "Water-resistant composite teak"],
        "primary_paint_color": {"name": "Platinum Frost White", "hex": "#F0F2F5"},
        "secondary_paint_color": {"name": "Smoked Titanium", "hex": "#3E444E"},
        "door_and_window_style": "Full-height motorized sliding glass panels with recessed floor tracks",
        "facade_treatment": "Bookmatched natural stone feature wall illuminated at night with integrated water sheet",
        "lighting_style": "Dramatic underwater LED projectors + perimeter RGBW warm linear architectural grazing",
        "balcony_and_railing_style": "Seamless full-span frameless structural glass balustrades",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_lux_03.jpg",
        "customization_defaults": {
            "finish_type": "quartzite_water_facade",
            "cladding_type": "backlit_brazilian_quartzite",
            "door_material": "full_glass_motorized",
            "boundary_wall_style": "glass_and_titanium_compound"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 38.0,
            "cladding_rate_sqft": 750.0,
            "window_upgrade_rate": 85000.0,
            "lighting_package": 78000.0
        }
    },
    {
        "id": "ext_lux_04",
        "name": "Palatial Modernist Villa",
        "category": "luxury_villa",
        "style": "Luxury Villa",
        "budget_tier": "Luxury",
        "description": "Symmetrical monumental colonnade framing, fluted Italian marble pilasters, motorized bronze gate portal, and elevated landscaped entry podium.",
        "suitable_house_types": ["Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 50.0, "min_length_ft": 70.0, "min_area_sqft": 3500.0, "max_area_sqft": 12000.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Statuario marble cladding", "Fluted stone pilasters", "Cast bronze gate elements", "Polished black granite podium"],
        "primary_paint_color": {"name": "Royal Imperial Cream", "hex": "#F7F5EE"},
        "secondary_paint_color": {"name": "Dark Statuario Vein Grey", "hex": "#40454D"},
        "door_and_window_style": "Symmetrical double-height bronze mullion windows with bronze crest handles",
        "facade_treatment": "Monumental two-story slender fluted marble colonnade with recessed shadow perimeter",
        "lighting_style": "In-ground architectural uplight wells illuminating each marble column uniformly",
        "balcony_and_railing_style": "Classical bronze balustrades with fluted marble corner newel posts",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_lux_04.jpg",
        "customization_defaults": {
            "finish_type": "statuario_marble_colonnade",
            "cladding_type": "fluted_marble_pilasters",
            "door_material": "monumental_bronze_double_door",
            "boundary_wall_style": "marble_pier_bronze_railings"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 40.0,
            "cladding_rate_sqft": 680.0,
            "window_upgrade_rate": 90000.0,
            "lighting_package": 72000.0
        }
    },

    # ── CATEGORY 4: TRADITIONAL INDIAN ────────────────────────────────────────
    {
        "id": "ext_trad_01",
        "name": "Kerala Nalukettu Heritage Elevation",
        "category": "traditional_indian",
        "style": "Traditional Indian",
        "budget_tier": "Mid-Range",
        "description": "Authentic Kerala architectural elevation with steeply sloping Mangalore clay tile roof, carved teak gables, Charupadi wooden veranda seating, and brass oil lamps.",
        "suitable_house_types": ["Independent House", "Bungalow", "Villa"],
        "recommended_plot_size": {"min_width_ft": 35.0, "min_length_ft": 45.0, "min_area_sqft": 1500.0, "max_area_sqft": 6000.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Mangalore clay roof tiles", "Hand-carved teak timber", "Laterite stone base", "Brass decorative fittings"],
        "primary_paint_color": {"name": "Heritage Clay Terracotta", "hex": "#C85A32"},
        "secondary_paint_color": {"name": "Deep Sheesham Wood", "hex": "#5A3319"},
        "door_and_window_style": "Traditional solid teakwood carved wooden windows with brass latches and slatted louvers",
        "facade_treatment": "Sloping roof with carved wooden gables (Mukhavaram) and front Charupadi seating veranda",
        "lighting_style": "Hanging Kerala brass oil-inspired pendant lamps with 2700K warm incandescent glow",
        "balcony_and_railing_style": "Handcrafted Charupadi slatted wooden banisters with decorative wooden columns",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_trad_01.jpg",
        "customization_defaults": {
            "finish_type": "terracotta_lime_plaster",
            "cladding_type": "laterite_stone_plinth",
            "door_material": "kerala_carved_teak",
            "boundary_wall_style": "laterite_tile_coping"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 16.0,
            "cladding_rate_sqft": 240.0,
            "window_upgrade_rate": 20000.0,
            "lighting_package": 18000.0
        }
    },
    {
        "id": "ext_trad_02",
        "name": "Chettinad Classical Courtyard Home",
        "category": "traditional_indian",
        "style": "Traditional Indian",
        "budget_tier": "Premium",
        "description": "Rich Chettinad heritage facade featuring ornate Burma teak double doors with brass studs, Athangudi-inspired pilasters, and terracotta cornice bands.",
        "suitable_house_types": ["Independent House", "Villa"],
        "recommended_plot_size": {"min_width_ft": 40.0, "min_length_ft": 50.0, "min_area_sqft": 2000.0, "max_area_sqft": 7000.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Polished Burma teak wood", "Egg-white lime plaster finish", "Handmade terracotta tiles", "Brass repousse panels"],
        "primary_paint_color": {"name": "Eggshell Lime White", "hex": "#F5F2EB"},
        "secondary_paint_color": {"name": "Chettinad Ochre Yellow", "hex": "#E0A838"},
        "door_and_window_style": "Double entrance door with brass lion knocker, brass studs, and heavy teak lintel carving",
        "facade_treatment": "Tiered cornice moldings (Pothigai) and ornamental plaster relief panels",
        "lighting_style": "Filigree brass hanging wall lanterns and warm threshold illumination",
        "balcony_and_railing_style": "Ornate cast-iron balustrades with Chettinad floral motifs",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_trad_02.jpg",
        "customization_defaults": {
            "finish_type": "chettinad_egg_plaster",
            "cladding_type": "carved_teak_fascia",
            "door_material": "brass_studded_burma_teak",
            "boundary_wall_style": "decorative_cornice_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 26.0,
            "cladding_rate_sqft": 380.0,
            "window_upgrade_rate": 35000.0,
            "lighting_package": 28000.0
        }
    },
    {
        "id": "ext_trad_03",
        "name": "Rajasthani Havelian Carved Jharokha",
        "category": "traditional_indian",
        "style": "Traditional Indian",
        "budget_tier": "Luxury",
        "description": "Stunning Royal Rajasthani haveli elevation with hand-carved pink sandstone Jharokha overhanging balconies, intricate jaali stone screens, and chhatri roof pavilions.",
        "suitable_house_types": ["Villa", "Independent House", "Duplex"],
        "recommended_plot_size": {"min_width_ft": 35.0, "min_length_ft": 45.0, "min_area_sqft": 1575.0, "max_area_sqft": 6500.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Pink Dholpur sandstone", "Intricate stone jaali", "Wrought iron accents", "Lime-washed walls"],
        "primary_paint_color": {"name": "Jaipur Sandstone Pink", "hex": "#D99B82"},
        "secondary_paint_color": {"name": "Antique Royal Ivory", "hex": "#F4EBD9"},
        "door_and_window_style": "Arch-headed wooden casements enclosed inside projected stone jharokhas",
        "facade_treatment": "Cantilevered stone jharokhas supported by decorative carved elephant and floral stone brackets",
        "lighting_style": "Warm amber uplights concealed beneath stone brackets highlighting intricate jaali shadows",
        "balcony_and_railing_style": "Perforated geometric stone jaali balustrade screen",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_trad_03.jpg",
        "customization_defaults": {
            "finish_type": "hand_carved_sandstone",
            "cladding_type": "dholpur_jharokha_units",
            "door_material": "sheesham_brass_studded",
            "boundary_wall_style": "sandstone_jaali_screen_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 30.0,
            "cladding_rate_sqft": 520.0,
            "window_upgrade_rate": 45000.0,
            "lighting_package": 36000.0
        }
    },
    {
        "id": "ext_trad_04",
        "name": "Goan-Portuguese Colonial Villa",
        "category": "traditional_indian",
        "style": "Traditional Indian",
        "budget_tier": "Mid-Range",
        "description": "Picturesque Indo-Portuguese Goan villa with vibrant golden-ochre facade, crisp white stucco trims, arched louvered wooden shutters, and oyster-shell window panels.",
        "suitable_house_types": ["Independent House", "Bungalow", "Villa"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 40.0, "min_area_sqft": 1200.0, "max_area_sqft": 4500.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Ochre mineral lime wash", "Stucco window architraves", "Teak louvered shutters", "Red clay roof shingles"],
        "primary_paint_color": {"name": "Goan Colonial Ochre", "hex": "#D89A2B"},
        "secondary_paint_color": {"name": "Pure White Stucco Trim", "hex": "#FFFFFF"},
        "door_and_window_style": "High arched double windows with operable exterior louvered timber shutters in emerald green",
        "facade_treatment": "Prominent raised entrance balcão (porch) with built-in stone benches and ornamental pediment",
        "lighting_style": "Classic black forged-iron Goan carriage wall brackets at entrance and corners",
        "balcony_and_railing_style": "Decorative wrought-iron balustrade in Portuguese scrolling pattern",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_trad_04.jpg",
        "customization_defaults": {
            "finish_type": "goan_ochre_stucco",
            "cladding_type": "white_stucco_bands",
            "door_material": "carved_colonial_double_door",
            "boundary_wall_style": "arched_pediment_gate"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 18.0,
            "cladding_rate_sqft": 180.0,
            "window_upgrade_rate": 22000.0,
            "lighting_package": 16000.0
        }
    },

    # ── CATEGORY 5: INDIAN MODERN ─────────────────────────────────────────────
    {
        "id": "ext_indmod_01",
        "name": "Terracotta Jaali Screen Modernist",
        "category": "indian_modern",
        "style": "Indian Modern",
        "budget_tier": "Mid-Range",
        "description": "Contemporary tropical Indian design featuring an expansive terracotta breeze-block (jaali) curtain wall for passive climate cooling, exposed red brick, and concrete frames.",
        "suitable_house_types": ["Independent House", "Duplex", "Row House", "Villa"],
        "recommended_plot_size": {"min_width_ft": 25.0, "min_length_ft": 40.0, "min_area_sqft": 1000.0, "max_area_sqft": 4000.0},
        "suitable_floor_configs": [1, 2, 3],
        "material_palette": ["Clay terracotta breeze blocks", "Wirecut red facing brick", "Board-finish concrete lintels", "Dark bronze aluminum"],
        "primary_paint_color": {"name": "Natural Terracotta Red", "hex": "#B85333"},
        "secondary_paint_color": {"name": "Warm Sand Grey", "hex": "#C2BEB4"},
        "door_and_window_style": "Concealed sliding glass windows placed behind the terracotta jaali envelope",
        "facade_treatment": "Full-height terracotta geometric breeze screen providing dynamic daylight patterns",
        "lighting_style": "Backlit LED strip profiles behind jaali blocks casting intricate shadows outward at night",
        "balcony_and_railing_style": "Continuous low-height brick parapet with recessed metal handrail",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_indmod_01.jpg",
        "customization_defaults": {
            "finish_type": "exposed_wirecut_brick",
            "cladding_type": "terracotta_jaali_blocks",
            "door_material": "teak_brass_minimal",
            "boundary_wall_style": "matching_jaali_brick"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 16.0,
            "cladding_rate_sqft": 260.0,
            "window_upgrade_rate": 20000.0,
            "lighting_package": 22000.0
        }
    },
    {
        "id": "ext_indmod_02",
        "name": "Contemporary Sheesham & Stone Facade",
        "category": "indian_modern",
        "style": "Indian Modern",
        "budget_tier": "Premium",
        "description": "Rich Indian natural teak and sheesham vertical timber battens paired with honed Dholpur beige sandstone wall panels, dark graphite frames, and a floating cantilever porch.",
        "suitable_house_types": ["Villa", "Duplex", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 45.0, "min_area_sqft": 1350.0, "max_area_sqft": 5200.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Natural sheesham timber", "Honed Dholpur sandstone", "Matte graphite frames", "Clear tempered glass"],
        "primary_paint_color": {"name": "Dholpur Sandstone Buff", "hex": "#E0D7C4"},
        "secondary_paint_color": {"name": "Natural Sheesham Brown", "hex": "#613B1F"},
        "door_and_window_style": "Large panoramic picture windows with integrated exterior sheesham vertical sun louvers",
        "facade_treatment": "Alternating panels of warm timber louvers and smooth-honed stone cladding",
        "lighting_style": "Narrow-beam 3000K warm LED grazers accentuating natural woodgrain and stone veining",
        "balcony_and_railing_style": "Smoked glass balustrade with dark sheesham timber top rail",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_indmod_02.jpg",
        "customization_defaults": {
            "finish_type": "honed_sandstone_panels",
            "cladding_type": "sheesham_vertical_battens",
            "door_material": "solid_sheesham_pivot",
            "boundary_wall_style": "sandstone_with_sheesham_slats"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 24.0,
            "cladding_rate_sqft": 390.0,
            "window_upgrade_rate": 32000.0,
            "lighting_package": 28000.0
        }
    },
    {
        "id": "ext_indmod_03",
        "name": "Courtyard-Centric Vastu Fusion",
        "category": "indian_modern",
        "style": "Indian Modern",
        "budget_tier": "Premium",
        "description": "Vastu-compliant contemporary house with auspicious Northeast light openings, brass jaali entryway screen, central courtyard peek through glass, and warm earthen tones.",
        "suitable_house_types": ["Independent House", "Villa", "Bungalow"],
        "recommended_plot_size": {"min_width_ft": 35.0, "min_length_ft": 50.0, "min_area_sqft": 1750.0, "max_area_sqft": 6000.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Laser-cut brass sheet", "Warm earthen terracotta plaster", "White Makrana marble plinth", "Solar control glass"],
        "primary_paint_color": {"name": "Warm Sand Earthen Plaster", "hex": "#DDD4C3"},
        "secondary_paint_color": {"name": "Polished Brass Gold", "hex": "#C5A059"},
        "door_and_window_style": "Solid teak main door with custom brass laser-cut sacred geometry door handle and grill",
        "facade_treatment": "Brass perforated sun-shield box projection on first floor with deep protective overhangs",
        "lighting_style": "Concealed perimeter brass trough lights and warm welcoming entrance downlight wash",
        "balcony_and_railing_style": "Perforated brass jaali panel railing with clean metal perimeter",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_indmod_03.jpg",
        "customization_defaults": {
            "finish_type": "earthen_textured_plaster",
            "cladding_type": "laser_cut_brass_screens",
            "door_material": "teak_with_brass_inlays",
            "boundary_wall_style": "makrana_plinth_brass_grille"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 22.0,
            "cladding_rate_sqft": 420.0,
            "window_upgrade_rate": 34000.0,
            "lighting_package": 32000.0
        }
    },
    {
        "id": "ext_indmod_04",
        "name": "Modern Earth-Tone Vernacular",
        "category": "indian_modern",
        "style": "Indian Modern",
        "budget_tier": "Mid-Range",
        "description": "Eco-sensitive vernacular elevation featuring rammed-earth textured walls, concrete chajjas (sunshades), bamboo privacy louvers, and natural stone foundation.",
        "suitable_house_types": ["Independent House", "Bungalow", "Row House"],
        "recommended_plot_size": {"min_width_ft": 25.0, "min_length_ft": 40.0, "min_area_sqft": 1000.0, "max_area_sqft": 4200.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Stabilized rammed-earth texture", "Treated bamboo louvers", "Cast concrete chajjas", "Basalt stone cobble"],
        "primary_paint_color": {"name": "Rammed Earth Ochre", "hex": "#C19A6B"},
        "secondary_paint_color": {"name": "Raw Concrete Grey", "hex": "#8A8D8F"},
        "door_and_window_style": "Wide window openings with deep 2-ft cast-concrete horizontal shading overhangs (chajjas)",
        "facade_treatment": "Horizontal stratified earth pigment layers with raw cantilevered concrete canopy",
        "lighting_style": "Earthy copper wall-mounted down-sconces highlighting earthen wall strata",
        "balcony_and_railing_style": "Treated bamboo balusters set into concrete upstand curb",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_indmod_04.jpg",
        "customization_defaults": {
            "finish_type": "rammed_earth_textured",
            "cladding_type": "bamboo_louver_screens",
            "door_material": "natural_sal_wood",
            "boundary_wall_style": "basalt_rubble_masonry"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 15.0,
            "cladding_rate_sqft": 210.0,
            "window_upgrade_rate": 18000.0,
            "lighting_package": 15000.0
        }
    },

    # ── CATEGORY 6: MEDITERRANEAN ─────────────────────────────────────────────
    {
        "id": "ext_med_01",
        "name": "Spanish Modern Hacienda",
        "category": "mediterranean",
        "style": "Mediterranean",
        "budget_tier": "Mid-Range",
        "description": "Warm ivory hand-troweled stucco walls, Spanish red barrel clay tile roof accents, graceful arched entryway with hand-forged black iron lanterns.",
        "suitable_house_types": ["Independent House", "Villa", "Bungalow"],
        "recommended_plot_size": {"min_width_ft": 35.0, "min_length_ft": 45.0, "min_area_sqft": 1500.0, "max_area_sqft": 5500.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Hand-troweled mineral stucco", "Spanish barrel clay roof tiles", "Hand-forged wrought iron", "Honed limestone paving"],
        "primary_paint_color": {"name": "Warm Spanish Cream", "hex": "#F3EAD8"},
        "secondary_paint_color": {"name": "Spanish Terracotta Tile", "hex": "#BA4D29"},
        "door_and_window_style": "Segmented arched windows with multi-pane divided lites and dark walnut entrance door",
        "facade_treatment": "Arched loggia porch with exposed timber ceiling beams and clay tile roof copings",
        "lighting_style": "Hand-forged black iron scrollwork lanterns with amber seeded glass globes",
        "balcony_and_railing_style": "Curved wrought-iron Juliet balconies with decorative basket scrollwork",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_med_01.jpg",
        "customization_defaults": {
            "finish_type": "spanish_troweled_stucco",
            "cladding_type": "clay_barrel_tile_roof",
            "door_material": "arched_carved_walnut",
            "boundary_wall_style": "arched_stucco_iron_gate"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 18.0,
            "cladding_rate_sqft": 250.0,
            "window_upgrade_rate": 22000.0,
            "lighting_package": 20000.0
        }
    },
    {
        "id": "ext_med_02",
        "name": "Santorini Coastal White & Cobblestone",
        "category": "mediterranean",
        "style": "Mediterranean",
        "budget_tier": "Premium",
        "description": "Iconic Aegean styling with curved whitewashed organic parapets, Aegean cobalt blue door & window frames, rustic limestone base wall, and bougainvillea trellises.",
        "suitable_house_types": ["Independent House", "Villa", "Bungalow"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 40.0, "min_area_sqft": 1200.0, "max_area_sqft": 4500.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Whitewashed lime plaster", "Aegean blue wood shutters", "Cycladic limestone flagstones", "Rough-cast mortar"],
        "primary_paint_color": {"name": "Aegean Pure White", "hex": "#FFFFFF"},
        "secondary_paint_color": {"name": "Santorini Cobalt Blue", "hex": "#1E5F9E"},
        "door_and_window_style": "Deep-set casement windows with cobalt blue wooden shutters and arched lintels",
        "facade_treatment": "Curved sculpted corners with organic fluid rooflines and white stepped terrace levels",
        "lighting_style": "Recessed niche lighting within curved stucco recesses casting soft blue-tinted evening glow",
        "balcony_and_railing_style": "Solid sculptural white masonry parapet with organic rounded hand-rests",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_med_02.jpg",
        "customization_defaults": {
            "finish_type": "cycladic_lime_wash",
            "cladding_type": "none",
            "door_material": "aegean_blue_solid_timber",
            "boundary_wall_style": "curved_whitewashed_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 22.0,
            "cladding_rate_sqft": 0.0,
            "window_upgrade_rate": 26000.0,
            "lighting_package": 24000.0
        }
    },
    {
        "id": "ext_med_03",
        "name": "Italian Riviera Stone Villa",
        "category": "mediterranean",
        "style": "Mediterranean",
        "budget_tier": "Luxury",
        "description": "Rough-cut dry-stacked limestone walls, olive-green wooden shutters, arched pergola with timber crossbeams, and a terracotta tiled motor court.",
        "suitable_house_types": ["Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 40.0, "min_length_ft": 55.0, "min_area_sqft": 2200.0, "max_area_sqft": 8000.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Dry-stacked rustic limestone", "Olive-green painted cedar", "Terracotta roof tiles", "Wrought iron hardware"],
        "primary_paint_color": {"name": "Riviera Sandstone", "hex": "#DFD7C0"},
        "secondary_paint_color": {"name": "Italian Olive Green", "hex": "#556B2F"},
        "door_and_window_style": "Arched French double doors with operable louvers in soft olive green",
        "facade_treatment": "Full stone masonry facade with cantilevered timber pergola covered in flowering vines",
        "lighting_style": "Aged verdigris copper wall-mounted lanterns and subtle landscape tree downlights",
        "balcony_and_railing_style": "Antique bronze filigree balustrades with continuous limestone capping",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_med_03.jpg",
        "customization_defaults": {
            "finish_type": "stacked_limestone_facade",
            "cladding_type": "dry_stone_masonry",
            "door_material": "arched_olive_french_door",
            "boundary_wall_style": "dry_limestone_retaining"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 30.0,
            "cladding_rate_sqft": 560.0,
            "window_upgrade_rate": 50000.0,
            "lighting_package": 45000.0
        }
    },
    {
        "id": "ext_med_04",
        "name": "Neo-Classical Mediterranean Duplex",
        "category": "mediterranean",
        "style": "Mediterranean",
        "budget_tier": "Premium",
        "description": "Sophisticated cream plaster finish with fluted cornices, decorative iron Juliet balconies, symmetrical arched windows, and an arched carriage portico.",
        "suitable_house_types": ["Duplex", "Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 45.0, "min_area_sqft": 1350.0, "max_area_sqft": 5000.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Fine-finish limestone plaster", "Decorative cast stone moldings", "Black wrought iron", "Charcoal roof shingles"],
        "primary_paint_color": {"name": "Neo-Classical Alabaster", "hex": "#F4F0E8"},
        "secondary_paint_color": {"name": "Charcoal Black Iron", "hex": "#25282A"},
        "door_and_window_style": "Symmetrical double-hung arched windows with decorative keystones and exterior iron railings",
        "facade_treatment": "Fluted Tuscan pilasters with classical entablature band separating floors",
        "lighting_style": "Symmetrical pair of coach lanterns flanking the main entrance portico",
        "balcony_and_railing_style": "Bow-front black wrought-iron Juliet balconies with rosette accents",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_med_04.jpg",
        "customization_defaults": {
            "finish_type": "limestone_fine_plaster",
            "cladding_type": "cast_stone_entablature",
            "door_material": "classical_paneled_teak",
            "boundary_wall_style": "classical_iron_pier_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 24.0,
            "cladding_rate_sqft": 340.0,
            "window_upgrade_rate": 36000.0,
            "lighting_package": 28000.0
        }
    },

    # ── CATEGORY 7: TROPICAL CONTEMPORARY ─────────────────────────────────────
    {
        "id": "ext_trop_01",
        "name": "Balinese Modern Pavilion House",
        "category": "tropical_contemporary",
        "style": "Tropical Contemporary",
        "budget_tier": "Premium",
        "description": "Deep overhanging timber eaves with exposed rafter tails, natural charcoal volcanic slate stone cladding, tropical timber sun louvers, and water court entry.",
        "suitable_house_types": ["Villa", "Independent House", "Bungalow"],
        "recommended_plot_size": {"min_width_ft": 35.0, "min_length_ft": 50.0, "min_area_sqft": 1750.0, "max_area_sqft": 6500.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Charcoal volcanic slate stone", "Oiled teak timber battens", "Dark bronze structural steel", "Water-resistant timber soffits"],
        "primary_paint_color": {"name": "Balinese Volcanic Sand", "hex": "#D6CEC2"},
        "secondary_paint_color": {"name": "Charcoal Basalt Stone", "hex": "#303236"},
        "door_and_window_style": "Floor-to-ceiling folding glass doors opening completely to shaded verandas",
        "facade_treatment": "Extended 4-ft timber roof overhangs with exposed rafters and natural slate feature wall",
        "lighting_style": "Warm 2700K indirect upward soffit illumination and in-water lotus pool spotlights",
        "balcony_and_railing_style": "Fine slatted teak wood balusters set in black aluminum channel",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_trop_01.jpg",
        "customization_defaults": {
            "finish_type": "volcanic_slate_cladding",
            "cladding_type": "natural_slate_and_teak",
            "door_material": "folding_teak_glass_wall",
            "boundary_wall_style": "slate_clad_water_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 25.0,
            "cladding_rate_sqft": 420.0,
            "window_upgrade_rate": 38000.0,
            "lighting_package": 34000.0
        }
    },
    {
        "id": "ext_trop_02",
        "name": "Bio-Tropical Slatted Timber Residence",
        "category": "tropical_contemporary",
        "style": "Tropical Contemporary",
        "budget_tier": "Premium",
        "description": "Vertical bamboo-composite exterior louvers, double-height glass with deep exterior shading fins, cantilevered green planters, and breezeway ventilation.",
        "suitable_house_types": ["Villa", "Duplex", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 45.0, "min_area_sqft": 1350.0, "max_area_sqft": 5500.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Bamboo-polymer composite louvers", "Raw concrete planter boxes", "High-performance solar glass", "Lush cascading creepers"],
        "primary_paint_color": {"name": "Lush Tropical Greige", "hex": "#DAD6CD"},
        "secondary_paint_color": {"name": "Warm Bamboo Caramel", "hex": "#A07144"},
        "door_and_window_style": "Double-height curtain wall with motorized exterior bamboo sun-shading louvers",
        "facade_treatment": "Cantilevered planter boxes on both levels with integrated drip irrigation and weeping foliage",
        "lighting_style": "Subtle green-foliage accent uplights and linear LED channels under planter boxes",
        "balcony_and_railing_style": "Seamless structural glass integrated behind the live green planter edge",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_trop_02.jpg",
        "customization_defaults": {
            "finish_type": "bio_planter_facade",
            "cladding_type": "bamboo_composite_louvers",
            "door_material": "vertical_slatted_bamboo",
            "boundary_wall_style": "green_living_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 24.0,
            "cladding_rate_sqft": 390.0,
            "window_upgrade_rate": 42000.0,
            "lighting_package": 36000.0
        }
    },
    {
        "id": "ext_trop_03",
        "name": "Rainforest Stone & Wood Retreat",
        "category": "tropical_contemporary",
        "style": "Tropical Contemporary",
        "budget_tier": "Luxury",
        "description": "Dark basalt volcanic stone feature wall, natural oiled ipe wood cladding, seamless indoor-outdoor veranda deck, and oversized cantilevered timber canopy.",
        "suitable_house_types": ["Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 40.0, "min_length_ft": 55.0, "min_area_sqft": 2200.0, "max_area_sqft": 8000.0},
        "suitable_floor_configs": [1, 2],
        "material_palette": ["Deep black basalt stone", "Oiled Ipe hardwood", "Matte bronze structural steel", "Water-resistant timber deck"],
        "primary_paint_color": {"name": "Warm Clay Silt", "hex": "#CDC4B5"},
        "secondary_paint_color": {"name": "Deep Ipe Timber", "hex": "#472B1E"},
        "door_and_window_style": "Oversized 9-ft sliding glass walls with insect-screen cavity pockets and bronze hardware",
        "facade_treatment": "Massive monolithic basalt stone anchor wall contrasting with warm horizontal ipe timber siding",
        "lighting_style": "Soft warm 2500K path and garden lanterns casting organic palm frond shadows",
        "balcony_and_railing_style": "Horizontal Ipe timber slat railing with concealed structural steel frame",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_trop_03.jpg",
        "customization_defaults": {
            "finish_type": "basalt_and_ipe_wood",
            "cladding_type": "horizontal_ipe_siding",
            "door_material": "solid_ipe_pivot",
            "boundary_wall_style": "basalt_rubble_timber_gate"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 28.0,
            "cladding_rate_sqft": 580.0,
            "window_upgrade_rate": 55000.0,
            "lighting_package": 46000.0
        }
    },
    {
        "id": "ext_trop_04",
        "name": "Tropical Brutalist Biophilic House",
        "category": "tropical_contemporary",
        "style": "Tropical Contemporary",
        "budget_tier": "Mid-Range",
        "description": "Raw architectural concrete walls with integrated cascading planter boxes, wooden pergola overhang, wide eaves, and natural ventilation slots.",
        "suitable_house_types": ["Independent House", "Duplex", "Villa"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 40.0, "min_area_sqft": 1200.0, "max_area_sqft": 4500.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Architectural exposed concrete", "Local natural hardwood", "Recycled brick aggregates", "Toughened clear glass"],
        "primary_paint_color": {"name": "Architectural Concrete Grey", "hex": "#C9CCD1"},
        "secondary_paint_color": {"name": "Tropical Teak Accent", "hex": "#7A4E2D"},
        "door_and_window_style": "Recessed casement windows set within deep concrete light scoops",
        "facade_treatment": "Tiered brutalist concrete overhangs with built-in cascading hanging gardens",
        "lighting_style": "Subtle in-concrete step and trough lights creating warm ambient indirect washes",
        "balcony_and_railing_style": "Solid board-formed concrete balustrade with recessed plant ledge",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_trop_04.jpg",
        "customization_defaults": {
            "finish_type": "exposed_concrete_finish",
            "cladding_type": "concrete_integrated_planters",
            "door_material": "hardwood_plank_door",
            "boundary_wall_style": "raw_concrete_planter_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 18.0,
            "cladding_rate_sqft": 260.0,
            "window_upgrade_rate": 24000.0,
            "lighting_package": 22000.0
        }
    },

    # ── CATEGORY 8: PREMIUM DUPLEX ────────────────────────────────────────────
    {
        "id": "ext_dup_01",
        "name": "Split-Level Urban Duplex",
        "category": "premium_duplex",
        "style": "Premium Duplex",
        "budget_tier": "Mid-Range",
        "description": "Staggered floor planes, fluted charcoal aluminum box projection, glass corner window, integrated covered car porch, and dynamic multi-level roofline.",
        "suitable_house_types": ["Duplex", "Independent House", "Row House"],
        "recommended_plot_size": {"min_width_ft": 25.0, "min_length_ft": 40.0, "min_area_sqft": 1000.0, "max_area_sqft": 3500.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Charcoal powder-coated aluminum louvers", "Pure white weather-coat emulsion", "Corner butt-glazed glass", "Heavy-duty driveway pavers"],
        "primary_paint_color": {"name": "Crisp White Acrylic", "hex": "#F6F7F9"},
        "secondary_paint_color": {"name": "Graphite Charcoal", "hex": "#2C3138"},
        "door_and_window_style": "Butt-joint glass corner windows on upper floor with black aluminum frames",
        "facade_treatment": "Cantilevered upper floor box frame projecting 3 ft beyond ground-floor garage line",
        "lighting_style": "Recessed magnetic linear tracks beneath upper cantilever and vertical column sconces",
        "balcony_and_railing_style": "12mm laminated glass balustrade with slim black aluminum top rail",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_dup_01.jpg",
        "customization_defaults": {
            "finish_type": "weather_shield_emulsion",
            "cladding_type": "charcoal_aluminum_box",
            "door_material": "flush_graphite_timber",
            "boundary_wall_style": "graphite_perforated_gate"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 18.0,
            "cladding_rate_sqft": 280.0,
            "window_upgrade_rate": 25000.0,
            "lighting_package": 22000.0
        }
    },
    {
        "id": "ext_dup_02",
        "name": "Twin-Slab Contemporary Duplex",
        "category": "premium_duplex",
        "style": "Premium Duplex",
        "budget_tier": "Premium",
        "description": "Distinct ground and upper floor identity with contrasting white stucco and woodgrain HPL composite panels, deep front terrace deck, and LED profile accents.",
        "suitable_house_types": ["Duplex", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 45.0, "min_area_sqft": 1350.0, "max_area_sqft": 4500.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Woodgrain exterior HPL sheets", "High-build white textured plaster", "Black aluminum window systems", "Polished grey granite steps"],
        "primary_paint_color": {"name": "Bright White Stucco", "hex": "#F8F9FA"},
        "secondary_paint_color": {"name": "Teak Woodgrain HPL", "hex": "#84532B"},
        "door_and_window_style": "Full-height sliding terrace door and picture windows with continuous transoms",
        "facade_treatment": "Double horizontal slab reveals separating ground residential suite from upper duplex floor",
        "lighting_style": "Continuous linear LED diffuser embedded into the slab edge profile",
        "balcony_and_railing_style": "Toughened glass railing supported by black stainless steel spigots",
        "estimated_cost_tier": "Premium",
        "image_path": "/images/exteriors/ext_dup_02.jpg",
        "customization_defaults": {
            "finish_type": "hpl_composite_cladding",
            "cladding_type": "woodgrain_hpl_panels",
            "door_material": "teak_aluminum_hybrid",
            "boundary_wall_style": "hpl_accent_wall"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 22.0,
            "cladding_rate_sqft": 340.0,
            "window_upgrade_rate": 30000.0,
            "lighting_package": 26000.0
        }
    },
    {
        "id": "ext_dup_03",
        "name": "Linear Compact Elevation Duplex",
        "category": "premium_duplex",
        "style": "Premium Duplex",
        "budget_tier": "Mid-Range",
        "description": "Optimized specifically for narrow urban plots (20-30ft frontage), featuring a vertical stone-clad tower element, motorized louvered screen, and compact balcony.",
        "suitable_house_types": ["Duplex", "Row House", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 20.0, "min_length_ft": 35.0, "min_area_sqft": 700.0, "max_area_sqft": 2800.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Vertical stacked stone veneer", "Champagne aluminum louvers", "Warm white acrylic paint", "Compact steel canopy"],
        "primary_paint_color": {"name": "Warm City Grey", "hex": "#E5E6E8"},
        "secondary_paint_color": {"name": "Dark Slate Stacked Stone", "hex": "#3D4148"},
        "door_and_window_style": "Narrow vertical strip windows with frosted privacy glass on staircase and wide front bedroom window",
        "facade_treatment": "Vertical stone tower running continuously from ground to roof parapet, visually elongating narrow frontage",
        "lighting_style": "Vertical up-down LED column grazers positioned on the stone tower element",
        "balcony_and_railing_style": "Perforated aluminum safety screen railing matching louver finish",
        "estimated_cost_tier": "Mid-Range",
        "image_path": "/images/exteriors/ext_dup_03.jpg",
        "customization_defaults": {
            "finish_type": "textured_acrylic_emulsion",
            "cladding_type": "vertical_stacked_stone",
            "door_material": "compact_steel_wood_door",
            "boundary_wall_style": "narrow_lot_sliding_gate"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 16.0,
            "cladding_rate_sqft": 270.0,
            "window_upgrade_rate": 20000.0,
            "lighting_package": 18000.0
        }
    },
    {
        "id": "ext_dup_04",
        "name": "Executive Pent-Floor Duplex",
        "category": "premium_duplex",
        "style": "Premium Duplex",
        "budget_tier": "Luxury",
        "description": "Top-tier duplex elevation with upper floor cantilevered master suite, continuous ribbon glass windows, dark bronze aluminum composite panels (ACP), and illuminated entry canopy.",
        "suitable_house_types": ["Duplex", "Villa", "Independent House"],
        "recommended_plot_size": {"min_width_ft": 30.0, "min_length_ft": 45.0, "min_area_sqft": 1350.0, "max_area_sqft": 5000.0},
        "suitable_floor_configs": [2, 3],
        "material_palette": ["Dark bronze metallic ACP", "Travertine accent column", "Structural ribbon glazing", "Perforated steel entry gate"],
        "primary_paint_color": {"name": "Soft Off-White Satin", "hex": "#F2F3F5"},
        "secondary_paint_color": {"name": "Dark Metallic Bronze", "hex": "#3A332B"},
        "door_and_window_style": "Continuous panoramic horizontal ribbon window across the entire upper facade",
        "facade_treatment": "Bold cantilevered upper floor projection clad in metallic bronze panels with integrated mood lighting",
        "lighting_style": "Integrated micro-downlights in cantilever soffit and backlit motorized house nameplate",
        "balcony_and_railing_style": "15mm tempered smoked glass railing with bronze metallic handrail profile",
        "estimated_cost_tier": "Luxury",
        "image_path": "/images/exteriors/ext_dup_04.jpg",
        "customization_defaults": {
            "finish_type": "metallic_acp_cladding",
            "cladding_type": "dark_bronze_acp",
            "door_material": "oversized_bronze_pivot",
            "boundary_wall_style": "bronze_acp_integrated_gate"
        },
        "cost_parameters": {
            "paint_upgrade_rate_sqft": 26.0,
            "cladding_rate_sqft": 460.0,
            "window_upgrade_rate": 45000.0,
            "lighting_package": 38000.0
        }
    }
]


def get_all_exterior_designs() -> List[ExteriorDesignOption]:
    """Returns all 32 distinct exterior design options."""
    return [ExteriorDesignOption(**d) for d in EXTERIOR_DESIGNS]


def get_exterior_design_by_id(design_id: str) -> Optional[ExteriorDesignOption]:
    """Retrieves a single exterior design by its ID."""
    for d in EXTERIOR_DESIGNS:
        if d["id"] == design_id:
            return ExteriorDesignOption(**d)
    return None


def get_designs_by_category(category_id: str) -> List[ExteriorDesignOption]:
    """Returns exterior designs for a specific category."""
    if category_id == "all":
        return get_all_exterior_designs()
    return [ExteriorDesignOption(**d) for d in EXTERIOR_DESIGNS if d["category"] == category_id]
