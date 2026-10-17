from typing import Dict, Any

# Import the zoning helper
try:
    from app.services.ai.zone_planner import generate_zoning_guide
except ImportError:
    # Will be resolved at runtime when the module is available
    generate_zoning_guide = None


def build_prompt(context: Dict[str, Any], feedback: str = None) -> str:
    """Build the LLM prompt with full planning context.

    Includes plot dimensions, setbacks, buildable area, entry sequence,
    zoning guide, and utilization rules. The prompt is designed to guide the
    LLM toward a realistic, professional floor plan.
    """
    # Base project info
    prompt = (
        f"You are an expert AI Architectural Planner.\n"
        f"You must generate a practical, realistic residential layout based on the user's requirements.\n\n"
        f"PROJECT CONTEXT:\n"
        f"- Plot Width: {context.get('plot_width', 0)} ft\n"
        f"- Plot Length: {context.get('plot_length', 0)} ft\n"
        f"- Facing: {context.get('facing', 'Unknown')} (front side)\n"
        f"- Floors requested: {context.get('floors', 1)}\n\n"
        f"ROOM REQUIREMENTS:\n"
        f"- Bedrooms: {context.get('bedrooms', 0)}\n"
        f"- Bathrooms: {context.get('bathrooms', 0)}\n"
        f"- Kitchens: {context.get('kitchens', 0)}\n"
        f"- Living Rooms: {context.get('living_rooms', 0)}\n"
        f"- Balconities: {context.get('balconies', 0)}\n\n"
        f"PREFERENCES:\n"
        f"- Architecture Style: {context.get('design_style', 'Modern')}\n"
        f"- Interior Style: {context.get('interior_style', 'Minimal')}\n"
        f"- Custom Notes: {context.get('custom_notes', 'None')}\n\n"
    )

    # Buildable area and setbacks
    buildable = context.get('buildable_boundary', {})
    setbacks = context.get('setbacks', {})
    prompt += (
        f"BUILDABLE AREA & SETBACKS:\n"
        f"- Buildable Width: {buildable.get('width', 0)} ft\n"
        f"- Buildable Length: {buildable.get('length', 0)} ft\n"
        f"- Setbacks (ft): Front {setbacks.get('front', 0)}, Rear {setbacks.get('rear', 0)}, "
        f"Left {setbacks.get('left', 0)}, Right {setbacks.get('right', 0)}\n"
        f"- Target Utilization: >= 40% of buildable area (prefer 60‑80%).\n\n"
    )

    # Entry sequence – must follow front side determined by facing
    prompt += (
        "ENTRY SEQUENCE (MUST BE FOLLOWED):\n"
        "1. ROAD / FRONT SIDE (determined by facing).\n"
        "2. MAIN GATE (pedestrian) on front side.\n"
        "3. VEHICLE GATE (if parking required) on front side, with driveway.\n"
        "4. DRIVEWAY connecting vehicle gate to parking and main entrance.\n"
        "5. MAIN ENTRANCE DOOR (type \"main_entrance\") on front side, swing outward.\n"
        "6. FOYER (optional) between main door and interior circulation.\n\n"
    )

    # Zoning guide – provide JSON for the model
    if generate_zoning_guide:
        try:
            zones = generate_zoning_guide(context)
            prompt += "ZONING GUIDE (JSON):\n" + f"{zones}\n\n"
        except Exception:
            prompt += "ZONING GUIDE: {}\n\n"
    else:
        prompt += "ZONING GUIDE: {}\n\n"

    # Architectural planning rules (kept from previous version for safety)
    prompt += (
        "ARCHITECTURAL PLANNING RULES:\n"
        "1. All rooms must fit within the buildable plot dimensions.\n"
        "2. Distribute rooms sensibly; avoid clustering in a corner.\n"
        "3. Respect the setback dimensions – no rooms may cross them.\n"
        "4. Living room near entrance/foyer; kitchen near dining; bedrooms in private zones.\n"
        "5. Provide logical circulation paths; every room must be reachable.\n"
        "6. Approximate room size ranges: Bedroom 100‑200 ft², Bathroom 30‑50 ft², Kitchen 80‑150 ft², "
        "Living 150‑300 ft².\n"
        "7. For G+1 or higher, include a staircase (type \"stairs\") aligned across floors.\n"
        "8. Exterior walls type \"exterior\" thickness 0.75 ft; interior walls thickness 0.5 ft.\n"
        "9. Doors must specify wall association, position, width; main entrance door type \"main_entrance\".\n"
        "10. Windows only on exterior walls.\n"
        "11. Strict geometry: no overlapping rooms, positive dimensions, area = width * length.\n"
    )

    if feedback:
        prompt += f"\nPREVIOUS ATTEMPT FAILED WITH THESE ERRORS:\n{feedback}\n"
        prompt += "Analyze the feedback, correct the geometry/planning errors, and provide a completely valid layout.\n"

    prompt += (
        "\nReturn ONLY a structured JSON object exactly matching the requested JSON schema.\n"
        "Do NOT include markdown formatting, explanations, or any other text."
    )
    return prompt
