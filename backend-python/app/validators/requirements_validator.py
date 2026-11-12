import logging
from pydantic import BaseModel, field_validator, ValidationInfo, ValidationError
from typing import Optional, Dict, Any

logger = logging.getLogger("validators.requirements_validator")


class PlanningRequirements(BaseModel):
    """Validated planning requirements extracted from project_service.get_planning_context.

    Accepts the *actual* context shape: individual room-count fields
    (bedrooms, bathrooms, …) rather than a generic ``rooms`` list.
    """
    plot_width: float
    plot_length: float
    facing: str
    floors: int = 1
    bedrooms: int = 0
    bathrooms: int = 0
    kitchens: int = 0
    living_rooms: int = 0
    balconies: int = 0
    parking: int = 0
    setbacks: Optional[Dict[str, Any]] = None

    @field_validator("plot_width", "plot_length")
    @classmethod
    def positive_dimensions(cls, v: float, info: ValidationInfo) -> float:
        if v is None or v <= 0:
            raise ValueError(f"{info.field_name} must be a positive number")
        return v

    @field_validator("facing")
    @classmethod
    def valid_facing(cls, v: str) -> str:
        if v is None:
            raise ValueError("facing is required")
        allowed = {"north", "south", "east", "west"}
        if v.lower() not in allowed:
            raise ValueError(f"facing must be one of {allowed}")
        return v.lower()

    @field_validator("floors")
    @classmethod
    def positive_floors(cls, v: int) -> int:
        if v < 1:
            raise ValueError("floors must be at least 1")
        return v


def validate_requirements(context: dict) -> PlanningRequirements:
    """Validate the planning context extracted from the project.

    Raises ``ValidationError`` if any field is missing or malformed.
    Returns a validated ``PlanningRequirements`` instance.
    """
    try:
        req = PlanningRequirements(
            plot_width=context.get("plot_width"),
            plot_length=context.get("plot_length"),
            facing=context.get("facing"),
            floors=context.get("floors", 1),
            bedrooms=context.get("bedrooms", 0),
            bathrooms=context.get("bathrooms", 0),
            kitchens=context.get("kitchens", 0),
            living_rooms=context.get("living_rooms", 0),
            balconies=context.get("balconies", 0),
            parking=context.get("parking", 0),
            setbacks=context.get("setbacks"),
        )
        return req
    except ValidationError as ve:
        logger.error("Planning requirements validation failed: %s", ve)
        raise


def requirements_fingerprint(req: PlanningRequirements) -> Dict[str, Any]:
    """Produce a stable, comparable fingerprint dict from validated requirements.

    Two plans generated from *identical* user requirements will produce
    matching fingerprints. This is used to decide whether a saved fallback
    plan can be reused for the current request.
    """
    return {
        "plot_width": req.plot_width,
        "plot_length": req.plot_length,
        "facing": req.facing,
        "floors": req.floors,
        "bedrooms": req.bedrooms,
        "bathrooms": req.bathrooms,
        "kitchens": req.kitchens,
        "living_rooms": req.living_rooms,
        "balconies": req.balconies,
        "parking": req.parking,
    }


def fingerprints_match(fp_a: Dict[str, Any], fp_b: Dict[str, Any]) -> bool:
    """Return True when two requirement fingerprints represent the same brief.

    Robust against float vs int JSON discrepancies (e.g. 50.0 vs 50)
    and case/whitespace differences in strings.
    """
    if not isinstance(fp_a, dict) or not isinstance(fp_b, dict):
        return False

    keys = [
        "plot_width", "plot_length", "facing", "floors",
        "bedrooms", "bathrooms", "kitchens", "living_rooms",
        "balconies", "parking"
    ]

    for k in keys:
        val_a = fp_a.get(k)
        val_b = fp_b.get(k)

        if k == "facing":
            str_a = str(val_a or "").strip().lower()
            str_b = str(val_b or "").strip().lower()
            if str_a != str_b:
                return False
        else:
            try:
                num_a = float(val_a if val_a is not None else 0)
                num_b = float(val_b if val_b is not None else 0)
                if abs(num_a - num_b) > 0.01:
                    return False
            except (ValueError, TypeError):
                if val_a != val_b:
                    return False

    return True
