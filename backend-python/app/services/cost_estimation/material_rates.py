"""
Material Rates and Regional Profiles — Phase 6D.
Default profile: Hyderabad, Telangana (INR ₹).
Tagged as illustrative/benchmark rates.
Supports user-specified overrides with validation.
"""

from typing import Dict, Optional
from app.models.cost_estimate import RateItem, RateProfile


# Default illustrative benchmark rates for Hyderabad, Telangana (2026 Q4)
# Sourced from standard residential construction benchmarks in Telangana region.
_HYDERABAD_BENCHMARK_RATES: Dict[str, Dict] = {
    # ── 1. Basic Structural Materials ──────────────────────────────────────
    "cement_bag": {
        "category": "materials",
        "item_key": "cement_bag",
        "name": "Portland Pozzolana / OPC 53 Grade Cement",
        "unit": "bag",
        "unit_rate": 380.0,
        "description": "50 kg cement bag for RCC & masonry",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "m_sand": {
        "category": "materials",
        "item_key": "m_sand",
        "name": "Manufactured Sand (M-Sand for Concreting & Plastering)",
        "unit": "cu ft",
        "unit_rate": 55.0,
        "description": "Clean graded crushed stone sand",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "coarse_aggregate": {
        "category": "materials",
        "item_key": "coarse_aggregate",
        "name": "Coarse Aggregate (20mm Blue Metal Granite)",
        "unit": "cu ft",
        "unit_rate": 48.0,
        "description": "Granite crushed aggregate for RCC works",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "tmt_steel": {
        "category": "structural_steel",
        "item_key": "tmt_steel",
        "name": "TMT High-Yield Reinforcement Rebar (Fe 550D)",
        "unit": "kg",
        "unit_rate": 68.0,
        "description": "Thermo-Mechanically Treated steel rebar",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "red_brick": {
        "category": "masonry",
        "item_key": "red_brick",
        "name": "Wire-cut / Standard Kiln Red Clay Bricks (9\"x4.25\"x2.75\")",
        "unit": "piece",
        "unit_rate": 10.5,
        "description": "Standard burnt clay brick for superstructure walls",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },

    # ── 2. Flooring & Tiling ──────────────────────────────────────────────
    "indoor_flooring_tile": {
        "category": "flooring",
        "item_key": "indoor_flooring_tile",
        "name": "Vitrified Floor Tiles (Double Charged / GVT 2'x2')",
        "unit": "sq ft",
        "unit_rate": 65.0,
        "description": "Premium anti-skid vitrified floor tiles for rooms",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "outdoor_paving_tile": {
        "category": "flooring",
        "item_key": "outdoor_paving_tile",
        "name": "Outdoor Anti-skid Heavy Duty Pavers / Ceramic Tiles",
        "unit": "sq ft",
        "unit_rate": 50.0,
        "description": "For balconies, terraces and verandahs",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "staircase_granite": {
        "category": "flooring",
        "item_key": "staircase_granite",
        "name": "Polished Natural Granite (Stair Treads & Risers)",
        "unit": "sq ft",
        "unit_rate": 140.0,
        "description": "Pre-cut flame or mirror polished granite slab",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "skirting_tile": {
        "category": "flooring",
        "item_key": "skirting_tile",
        "name": "Tile Skirting (100mm height matching floor)",
        "unit": "running ft",
        "unit_rate": 25.0,
        "description": "Perimeter wall protection skirting",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },

    # ── 3. Plaster, Paint & Waterproofing ──────────────────────────────────
    "wall_plaster_mortar": {
        "category": "finishes",
        "item_key": "wall_plaster_mortar",
        "name": "Internal & External Cement Plaster Mortar (Materials)",
        "unit": "sq ft",
        "unit_rate": 18.0,
        "description": "Cement-sand mortar for 12-15mm smooth plaster",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "internal_paint_putty": {
        "category": "finishes",
        "item_key": "internal_paint_putty",
        "name": "Interior Putty (2 coats) + Premium Acrylic Emulsion (2 coats)",
        "unit": "sq ft",
        "unit_rate": 24.0,
        "description": "Complete interior wall paint finish including primer",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "external_weatherproof_paint": {
        "category": "finishes",
        "item_key": "external_weatherproof_paint",
        "name": "Exterior Weatherproof Anti-Fungal Acrylic Paint",
        "unit": "sq ft",
        "unit_rate": 28.0,
        "description": "Exterior facade primer + 2 coats weatherproof emulsion",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "terrace_waterproofing": {
        "category": "finishes",
        "item_key": "terrace_waterproofing",
        "name": "Elastomeric Membrane Waterproofing for Terrace & Toilets",
        "unit": "sq ft",
        "unit_rate": 45.0,
        "description": "Multi-coat polymer modified cementitious coating",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },

    # ── 4. Openings & Metalwork ───────────────────────────────────────────
    "door_main_entrance": {
        "category": "openings",
        "item_key": "door_main_entrance",
        "name": "Grand Main Entrance Door (Teak Wood Frame & Shutter)",
        "unit": "unit",
        "unit_rate": 28000.0,
        "description": "Carved teak wood entrance door with brass hardware",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "door_internal": {
        "category": "openings",
        "item_key": "door_internal",
        "name": "Internal Flush / Laminated Door with Hardwood Frame",
        "unit": "unit",
        "unit_rate": 7500.0,
        "description": "Factory pressed flush shutter with SS mortise lock",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "door_toilet": {
        "category": "openings",
        "item_key": "door_toilet",
        "name": "Waterproof PVC / FRP Door for Bathrooms & Utility",
        "unit": "unit",
        "unit_rate": 4200.0,
        "description": "Moisture-resistant molded PVC door assembly",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "window_upvc": {
        "category": "openings",
        "item_key": "window_upvc",
        "name": "UPVC Sliding Window with Float Glass & Mesh Shutter",
        "unit": "sq ft",
        "unit_rate": 480.0,
        "description": "Multi-chamber UPVC profile with 5mm toughened/float glass",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "staircase_railing_ss": {
        "category": "openings",
        "item_key": "staircase_railing_ss",
        "name": "Stainless Steel (SS 304 Grade) Staircase Railing",
        "unit": "running ft",
        "unit_rate": 1250.0,
        "description": "SS 304 balusters and top handrail with toughened infill",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },

    # ── 5. Services & Plumbing / Electrical ───────────────────────────────
    "plumbing_sanitary_point": {
        "category": "services",
        "item_key": "plumbing_sanitary_point",
        "name": "Sanitaryware & Internal Plumbing (CPVC/PVC Piping)",
        "unit": "point",
        "unit_rate": 16000.0,
        "description": "Per wet area (WC, washbasin, mixer tap, diverter, lines)",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "electrical_point_allowance": {
        "category": "services",
        "item_key": "electrical_point_allowance",
        "name": "Electrical Conduit, Concealed FRLS Copper Wiring & Modular Switches",
        "unit": "point",
        "unit_rate": 1150.0,
        "description": "Per electrical point (light/fan/plug/AC point)",
        "is_labor_included": False,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },

    # ── 6. Labor Rates ────────────────────────────────────────────────────
    "masonry_rcc_labor": {
        "category": "labor",
        "item_key": "masonry_rcc_labor",
        "name": "Civil Masonry, Shuttering & RCC Concreting Labor",
        "unit": "sq ft",
        "unit_rate": 220.0,
        "description": "Labor rate per sq ft of built-up area for structure & brickwork",
        "is_labor_included": True,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "flooring_laying_labor": {
        "category": "labor",
        "item_key": "flooring_laying_labor",
        "name": "Tile Laying & Skirting Workmanship Labor",
        "unit": "sq ft",
        "unit_rate": 28.0,
        "description": "Labor rate per sq ft for laying and grouting tiles",
        "is_labor_included": True,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
    "painting_labor": {
        "category": "labor",
        "item_key": "painting_labor",
        "name": "Surface Preparation, Putty Application & Painting Labor",
        "unit": "sq ft",
        "unit_rate": 14.0,
        "description": "Per sq ft of wall/ceiling surface area",
        "is_labor_included": True,
        "is_wastage_included": False,
        "confidence": "illustrative",
        "source": "Hyderabad, Telangana Benchmark 2026",
    },
}


def get_default_rate_profile(custom_overrides: Optional[Dict[str, float]] = None) -> RateProfile:
    """
    Returns the baseline Hyderabad, Telangana rate profile, optionally merging
    validated user custom rate overrides.
    """
    rates: Dict[str, RateItem] = {}

    for k, d in _HYDERABAD_BENCHMARK_RATES.items():
        rate_val = d["unit_rate"]
        confidence = d["confidence"]
        source = d["source"]

        # Check if user passed an override
        if custom_overrides and k in custom_overrides:
            override_val = custom_overrides[k]
            if override_val is not None:
                if override_val < 0:
                    raise ValueError(f"Rate for '{k}' cannot be negative ({override_val})")
                rate_val = float(override_val)
                confidence = "user_specified"
                source = "User Customized Rate"

        item = RateItem(
            category=d["category"],
            item_key=k,
            name=d["name"],
            unit=d["unit"],
            unit_rate=rate_val,
            description=d.get("description"),
            is_labor_included=d.get("is_labor_included", False),
            is_wastage_included=d.get("is_wastage_included", False),
            confidence=confidence,
            source=source,
            effective_date="2026-10-16",
        )
        rates[k] = item

    return RateProfile(
        profile_id="hyderabad_telangana_benchmark",
        location_name="Hyderabad, Telangana (INR ₹)",
        currency="INR",
        currency_symbol="₹",
        status="illustrative_benchmark",
        notes="Illustrative benchmark rates for residential RCC framed construction in Hyderabad, Telangana (2026).",
        rates=rates,
    )
