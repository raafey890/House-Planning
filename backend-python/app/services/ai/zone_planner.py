from typing import Dict, Any


def generate_zoning_guide(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate rectangular zones (public, service, private, circulation, outdoor)
    based on plot dimensions, setbacks and facing.
    Returns a dict that can be JSON‑encoded and injected into the LLM prompt.
    All coordinates are expressed in feet relative to the plot origin (0,0).
    """
    # Extract buildable footprint
    width = context.get("buildable_boundary", {}).get("width", 0)
    length = context.get("buildable_boundary", {}).get("length", 0)
    setbacks = context.get("setbacks", {})
    front = setbacks.get("front", 0)
    left = setbacks.get("left", 0)

    # Simple proportional split (configurable via percentages)
    # Public zone occupies front 30% of buildable length
    public_len = length * 0.30
    # Service zone next 20%
    service_len = length * 0.20
    # Private zone rear 30%
    private_len = length * 0.30
    # Circulation core occupies middle vertical strip (15% width)
    circulation_width = width * 0.15
    # Outdoor (terrace/garden) = any remaining area not covered by zones

    # Origin of buildable area (bottom‑left after setbacks)
    origin_x = left
    origin_y = front

    zones = {}
    # Public zone rectangle
    zones["public"] = {
        "x": origin_x,
        "y": origin_y,
        "width": width,
        "length": public_len,
    }
    # Service zone rectangle (immediately behind public)
    zones["service"] = {
        "x": origin_x,
        "y": origin_y + public_len,
        "width": width,
        "length": service_len,
    }
    # Private zone rectangle (rear part)
    zones["private"] = {
        "x": origin_x,
        "y": origin_y + public_len + service_len,
        "width": width,
        "length": private_len,
    }
    # Circulation core runs through the full height, centered horizontally
    circ_x = origin_x + (width - circulation_width) / 2
    zones["circulation"] = {
        "x": circ_x,
        "y": origin_y,
        "width": circulation_width,
        "length": length,
    }
    # Outdoor zone is the leftover area around other zones (for simplicity we expose the full buildable rect)
    zones["outdoor"] = {
        "x": origin_x,
        "y": origin_y,
        "width": width,
        "length": length,
    }
    return zones
