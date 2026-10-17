"""
Room catalog and configuration for the deterministic planning engine.
Specifies minimums, preferred architectural dimensions, and practical maximums.
Supports scale-aware preferred sizing based on plot footprint.
"""
from typing import Dict, Any

ROOM_CATALOG = {
    "living_room": {
        "min_w": 13, "min_h": 13, "max_w": 22, "max_h": 24,
        "pref_w": 16, "pref_h": 18, "min_area": 180, "pref_area": 288, "max_area": 480,
        "privacy": "public", "wet": False
    },
    "dining_room": {
        "min_w": 10, "min_h": 10, "max_w": 16, "max_h": 18,
        "pref_w": 12, "pref_h": 14, "min_area": 100, "pref_area": 168, "max_area": 260,
        "privacy": "public", "wet": False
    },
    "kitchen": {
        "min_w": 8, "min_h": 9, "max_w": 14, "max_h": 16,
        "pref_w": 10, "pref_h": 13, "min_area": 80, "pref_area": 130, "max_area": 210,
        "privacy": "service", "wet": True
    },
    "master_bedroom": {
        "min_w": 12, "min_h": 13, "max_w": 18, "max_h": 20,
        "pref_w": 14, "pref_h": 16, "min_area": 160, "pref_area": 224, "max_area": 350,
        "privacy": "private", "wet": False
    },
    "bedroom": {
        "min_w": 10, "min_h": 11, "max_w": 15, "max_h": 17,
        "pref_w": 12, "pref_h": 14, "min_area": 120, "pref_area": 168, "max_area": 250,
        "privacy": "private", "wet": False
    },
    "bathroom": {
        "min_w": 5, "min_h": 6, "max_w": 8, "max_h": 11,
        "pref_w": 6, "pref_h": 8, "min_area": 35, "pref_area": 48, "max_area": 85,
        "privacy": "private", "wet": True
    },
    "toilet": {
        "min_w": 4, "min_h": 4, "max_w": 6, "max_h": 7,
        "pref_w": 4, "pref_h": 6, "min_area": 20, "pref_area": 24, "max_area": 40,
        "privacy": "private", "wet": True
    },
    "parking": {
        "min_w": 10, "min_h": 16, "max_w": 15, "max_h": 24,
        "pref_w": 12, "pref_h": 18, "min_area": 160, "pref_area": 216, "max_area": 340,
        "privacy": "outdoor", "wet": False
    },
    "balcony": {
        "min_w": 4, "min_h": 6, "max_w": 8, "max_h": 16,
        "pref_w": 6, "pref_h": 12, "min_area": 30, "pref_area": 72, "max_area": 130,
        "privacy": "outdoor", "wet": False
    },
    "pooja_room": {
        "min_w": 4, "min_h": 4, "max_w": 8, "max_h": 8,
        "pref_w": 5, "pref_h": 6, "min_area": 20, "pref_area": 30, "max_area": 60,
        "privacy": "public", "wet": False
    },
    "study_room": {
        "min_w": 8, "min_h": 9, "max_w": 14, "max_h": 15,
        "pref_w": 10, "pref_h": 12, "min_area": 80, "pref_area": 120, "max_area": 190,
        "privacy": "private", "wet": False
    },
    "utility_room": {
        "min_w": 5, "min_h": 6, "max_w": 8, "max_h": 10,
        "pref_w": 6, "pref_h": 8, "min_area": 35, "pref_area": 48, "max_area": 75,
        "privacy": "service", "wet": True
    },
    "store_room": {
        "min_w": 5, "min_h": 5, "max_w": 8, "max_h": 8,
        "pref_w": 6, "pref_h": 7, "min_area": 30, "pref_area": 42, "max_area": 60,
        "privacy": "service", "wet": False
    },
    "guest_room": {
        "min_w": 10, "min_h": 10, "max_w": 15, "max_h": 16,
        "pref_w": 12, "pref_h": 13, "min_area": 100, "pref_area": 156, "max_area": 230,
        "privacy": "public", "wet": False
    },
    "corridor": {
        "min_w": 4, "min_h": 6, "max_w": 6, "max_h": 20,
        "pref_w": 5, "pref_h": 14, "min_area": 30, "pref_area": 70, "max_area": 120,
        "privacy": "circulation", "wet": False
    },
    "foyer": {
        "min_w": 6, "min_h": 6, "max_w": 10, "max_h": 12,
        "pref_w": 8, "pref_h": 8, "min_area": 36, "pref_area": 64, "max_area": 110,
        "privacy": "circulation", "wet": False
    },
    "sit_out": {
        "min_w": 6, "min_h": 8, "max_w": 10, "max_h": 14,
        "pref_w": 7, "pref_h": 10, "min_area": 48, "pref_area": 70, "max_area": 130,
        "privacy": "outdoor", "wet": False
    },
    "courtyard": {
        "min_w": 8, "min_h": 8, "max_w": 14, "max_h": 16,
        "pref_w": 10, "pref_h": 12, "min_area": 64, "pref_area": 120, "max_area": 200,
        "privacy": "outdoor", "wet": False
    },
    "staircase": {
        "min_w": 7, "min_h": 10, "max_w": 10, "max_h": 15,
        "pref_w": 8, "pref_h": 13, "min_area": 70, "pref_area": 104, "max_area": 140,
        "privacy": "circulation", "wet": False
    },
    "garage": {
        "min_w": 10, "min_h": 18, "max_w": 16, "max_h": 24,
        "pref_w": 12, "pref_h": 20, "min_area": 180, "pref_area": 240, "max_area": 360,
        "privacy": "outdoor", "wet": False
    }
}

def get_room_specs(room_type: str, plot_area: float = 2000.0) -> Dict[str, Any]:
    """
    Returns room specifications tailored to plot scale.
    For generous plots (>= 3000 sq ft, e.g. 50x80), scales preferred dimensions up appropriately.
    For compact plots (<= 1500 sq ft, e.g. 30x40), uses standard compact dimensions.
    """
    base = ROOM_CATALOG.get(room_type.lower(), {
        "min_w": 8, "min_h": 8, "max_w": 15, "max_h": 16,
        "pref_w": 10, "pref_h": 12, "min_area": 80, "pref_area": 120, "max_area": 200,
        "privacy": "private", "wet": False
    }).copy()

    # Scale-aware adaptation for generous plots
    if plot_area >= 3200.0:
        scale = 1.15
        if room_type in ["living_room", "master_bedroom", "dining_room", "parking"]:
            scale = 1.20
        elif room_type in ["bathroom", "toilet", "pooja_room"]:
            scale = 1.05

        base["pref_w"] = min(int(round(base["pref_w"] * scale)), base["max_w"])
        base["pref_h"] = min(int(round(base["pref_h"] * scale)), base["max_h"])
        base["pref_area"] = min(int(round(base["pref_area"] * (scale ** 2))), base.get("max_area", 400))

    return base
