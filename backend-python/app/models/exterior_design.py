"""
Exterior Design Studio Models — Phase 6F.1.
Pydantic schemas for the 32 distinct exterior design catalog items,
project-level exterior selections, finish and color customizations,
plan-aware compatibility validation, and cost impact calculations.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class ExteriorColorItem(BaseModel):
    name: str
    hex: str
    code: Optional[str] = None


class ExteriorColorPalette(BaseModel):
    primary_wall_color: Union[str, Dict[str, str]]
    accent_wall_color: Union[str, Dict[str, str]]
    boundary_wall_color: Optional[Union[str, Dict[str, str]]] = None
    door_color: Optional[Union[str, Dict[str, str]]] = None
    window_frame_color: Optional[Union[str, Dict[str, str]]] = None
    railing_color: Optional[Union[str, Dict[str, str]]] = None


class ExteriorMaterials(BaseModel):
    finish_type: str = "standard_paint"
    cladding_type: Optional[str] = "none"
    door_material: Optional[str] = "solid_teak"
    window_frame_material: Optional[str] = "powder_coated_aluminum"
    railing_material: Optional[str] = "toughened_glass"


class ArchitecturalElements(BaseModel):
    entrance_portal: Optional[str] = "canopy"
    door_style: Optional[str] = "pivot"
    window_frame_style: Optional[str] = "floor_to_ceiling"
    balcony_railing: Optional[str] = "glass_railing"
    facade_panels: Optional[str] = "none"
    boundary_wall_style: Optional[str] = "matching_plaster"
    gate_design: Optional[str] = "motorized_sliding"


class LightingConfig(BaseModel):
    style: str = "architectural_grazers"
    fixture_count: int = Field(ge=0, default=6)
    fixture_type: Optional[str] = "3000k_warm_led"


class LandscapingConfig(BaseModel):
    garden_style: Optional[str] = "minimalist_greens"
    pathway_material: Optional[str] = "granite_pavers"
    greenery_level: Optional[str] = "moderate"


class ExteriorDesignOption(BaseModel):
    id: str = Field(description="Unique stable ID starting with ext_")
    name: str = Field(description="Display name of exterior design")
    category: str = Field(description="modern_contemporary | minimalist | luxury_villa | traditional_indian | indian_modern | mediterranean | tropical_contemporary | premium_duplex")
    style: str = Field(description="Architectural style name")
    budget_tier: str = Field(description="Economy | Mid-Range | Premium | Luxury")
    description: str = Field(description="Detailed architectural & aesthetic elevation summary")
    suitable_house_types: List[str] = Field(description="Suitable house types: Villa, Duplex, Bungalow, Independent House, Row House")
    recommended_plot_size: Dict[str, Any] = Field(description="Dict with min_width_ft, min_length_ft, min_area_sqft, max_area_sqft")
    suitable_floor_configs: List[int] = Field(description="Suitable floor counts, e.g. [1, 2] for G and G+1")
    material_palette: List[str] = Field(description="List of core exterior materials")
    primary_paint_color: Dict[str, str] = Field(description="Default primary paint name and hex")
    secondary_paint_color: Dict[str, str] = Field(description="Default secondary accent paint name and hex")
    door_and_window_style: str = Field(description="Exterior fenestration specifications")
    facade_treatment: str = Field(description="Façade architectural articulation")
    lighting_style: str = Field(description="Exterior lighting treatment")
    balcony_and_railing_style: Optional[str] = None
    estimated_cost_tier: str = "Mid-Range"
    image_path: str = Field(description="Path to architectural reference photo in public/images/exteriors/")
    customization_defaults: Dict[str, Any] = Field(default_factory=dict)
    cost_parameters: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        if not v.startswith("ext_"):
            raise ValueError("Exterior design option ID must start with 'ext_'")
        return v


class ProjectExteriorSelection(BaseModel):
    project_id: str
    design_id: str
    design_name: Optional[str] = None
    category: Optional[str] = None
    style: Optional[str] = None
    
    # Customization structures
    colors: Dict[str, Any] = Field(default_factory=dict)
    materials: Dict[str, Any] = Field(default_factory=dict)
    architectural_elements: Dict[str, Any] = Field(default_factory=dict)
    lighting: Dict[str, Any] = Field(default_factory=dict)
    landscaping: Dict[str, Any] = Field(default_factory=dict)
    boundary_wall: Dict[str, Any] = Field(default_factory=dict)

    # Compatibility rating for this specific project
    compatibility_status: str = "compatible"  # compatible | compatible_with_adjustments | not_recommended
    compatibility_notes: List[str] = Field(default_factory=list)

    # Cost tracking
    additional_cost: float = Field(ge=0.0, default=0.0)
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ProjectExteriorSelectionPayload(BaseModel):
    project_id: str
    selection: Optional[ProjectExteriorSelection] = None
    total_exterior_cost: float = Field(ge=0.0, default=0.0)
    updated_at: Optional[str] = None


class CalculateExteriorCostRequest(BaseModel):
    project_id: str
    design_id: str
    plot_width: Optional[float] = 30.0
    plot_length: Optional[float] = 40.0
    floors: Optional[int] = 1
    building_footprint_sqft: Optional[float] = None
    materials: Dict[str, Any] = Field(default_factory=dict)
    lighting: Dict[str, Any] = Field(default_factory=dict)
    architectural_elements: Dict[str, Any] = Field(default_factory=dict)
    landscaping: Dict[str, Any] = Field(default_factory=dict)
    boundary_wall: Dict[str, Any] = Field(default_factory=dict)


class CompatibilityCheckRequest(BaseModel):
    design_id: str
    plot_width: float = Field(ge=1.0)
    plot_length: float = Field(ge=1.0)
    floors: int = Field(ge=1, default=1)
    building_type: Optional[str] = "Independent House"
    building_footprint_sqft: Optional[float] = None


class CompatibilityCheckResponse(BaseModel):
    design_id: str
    status: str  # compatible | compatible_with_adjustments | not_recommended
    score: int   # 0 to 100
    is_compatible: bool
    reasons: List[str] = Field(default_factory=list)
    adjustments_suggested: List[str] = Field(default_factory=list)


# ── Phase 6F.2 Canonical Exterior Visualization Models ──────────────────────

class ExteriorViewAngle(str):
    FRONT = "front"
    FRONT_LEFT = "front_left"
    FRONT_RIGHT = "front_right"


class ExteriorLightingMode(str):
    DAYLIGHT = "daylight"
    NIGHT = "night"


class CanonicalExteriorConfig(BaseModel):
    project_id: str
    plot_width: float = Field(ge=10.0, le=250.0, default=30.0)
    plot_length: float = Field(ge=15.0, le=350.0, default=40.0)
    plot_facing: str = Field(default="North")
    floors: int = Field(ge=1, le=5, default=1)
    building_footprint_sqft: Optional[float] = None
    building_type: Optional[str] = "Independent House"
    design_id: str = Field(description="Must start with ext_")
    design_name: Optional[str] = None
    style: Optional[str] = None

    # Colors dictionary: primary_wall, accent_wall, boundary_wall, door, window_frame, railing
    colors: Dict[str, str] = Field(default_factory=dict)
    materials: Dict[str, str] = Field(default_factory=dict)
    architectural_elements: Dict[str, Any] = Field(default_factory=dict)
    lighting: Dict[str, Any] = Field(default_factory=dict)
    landscaping: Dict[str, Any] = Field(default_factory=dict)
    boundary_wall: Dict[str, Any] = Field(default_factory=dict)
    rendering_preferences: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("design_id")
    @classmethod
    def validate_design_id(cls, v: str) -> str:
        if not v.startswith("ext_"):
            raise ValueError("Exterior design ID must start with 'ext_'")
        return v

    @field_validator("colors")
    @classmethod
    def validate_hex_colors(cls, v: Dict[str, str]) -> Dict[str, str]:
        import re
        hex_pattern = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
        for key, val in v.items():
            if isinstance(val, str):
                if not hex_pattern.match(val):
                    raise ValueError(f"Invalid hex color for '{key}': '{val}'. Must be a valid hex code like #FFFFFF or #FFF")
        return v


class ExteriorVisualizationRequest(BaseModel):
    project_id: str
    design_id: str
    view_angle: str = Field(default="front", description="front | front_left | front_right")
    lighting_mode: str = Field(default="daylight", description="daylight | night")
    plot_width: Optional[float] = 30.0
    plot_length: Optional[float] = 40.0
    floors: Optional[int] = 1
    plot_facing: Optional[str] = "North"
    building_footprint_sqft: Optional[float] = None
    colors: Optional[Dict[str, str]] = None
    materials: Optional[Dict[str, str]] = None
    architectural_elements: Optional[Dict[str, Any]] = None
    lighting: Optional[Dict[str, Any]] = None
    landscaping: Optional[Dict[str, Any]] = None
    boundary_wall: Optional[Dict[str, Any]] = None
    force_regenerate: bool = False

    @field_validator("view_angle")
    @classmethod
    def validate_view_angle(cls, v: str) -> str:
        valid = {"front", "front_left", "front_right"}
        norm = v.lower().strip()
        if norm not in valid:
            raise ValueError(f"Invalid view_angle '{v}'. Must be one of {valid}")
        return norm

    @field_validator("lighting_mode")
    @classmethod
    def validate_lighting_mode(cls, v: str) -> str:
        valid = {"daylight", "night"}
        norm = v.lower().strip()
        if norm not in valid:
            raise ValueError(f"Invalid lighting_mode '{v}'. Must be one of {valid}")
        return norm


class ExteriorVisualizationResponse(BaseModel):
    status: str = Field(description="success | provider_error | error")
    preview_mode: str = Field(default="svg_vector", description="svg_vector | ai_generated")
    svg_content: Optional[str] = None
    image_url: Optional[str] = None
    view_angle: str = "front"
    lighting_mode: str = "daylight"
    project_id: str
    design_id: str
    design_name: Optional[str] = None
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    colors_used: Dict[str, str] = Field(default_factory=dict)
    materials_used: Dict[str, str] = Field(default_factory=dict)
    provider: str = "Architectural Vector Elevation Engine"
    prompt_used: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_detail: Optional[str] = None

