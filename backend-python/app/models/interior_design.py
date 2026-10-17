"""
Interior Design Studio Models — Phase 6E.1.
Pydantic schemas for the 32 distinct interior design catalog items,
room-specific selections, finish customizations, and cost impact calculations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class InteriorFinishOption(BaseModel):
    key: str
    name: str
    material: str
    unit: str
    unit_rate: float = Field(ge=0.0)
    is_upgrade: bool = False
    differential_rate: float = 0.0


class InteriorDesignOption(BaseModel):
    id: str = Field(description="Unique stable ID, e.g. int_lr_01")
    name: str = Field(description="Design name")
    category: str = Field(description="living_room | bedroom | kitchen | bathroom | dining_room | ceiling_lighting")
    style: str = Field(description="Modern | Luxury | Minimalist | Warm Wood | Indian Contemporary | Hotel-Inspired | Budget-Friendly | Soft Luxury")
    budget_tier: str = Field(description="Economy | Mid-Range | Premium | Luxury")
    description: str = Field(description="Detailed architectural & aesthetic summary")
    suitable_room_types: List[str] = Field(description="Compatible room types: living_room, bedroom, master_bedroom, kitchen, bathroom, dining_room, all")
    image_path: str = Field(description="Path or URL to distinct visual preview")
    
    # Detailed interior specification concepts
    wall_finish_default: str
    flooring_default: str
    ceiling_concept: str
    lighting_concept: str
    furniture_concept: str
    fixtures_and_materials: List[str] = Field(default_factory=list)
    
    # Structured cost parameters
    cost_parameters: Dict[str, Any] = Field(default_factory=dict)
    limitations_and_assumptions: List[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        if not v.startswith("int_"):
            raise ValueError("Design option ID must start with 'int_'")
        return v


class RoomInteriorSelection(BaseModel):
    room_id: str = Field(description="Unique room ID from floor plan layout")
    room_type: str = Field(description="Room type: living_room, bedroom, master_bedroom, kitchen, etc.")
    room_name: Optional[str] = None
    room_area_sqft: float = Field(ge=0.0, default=0.0)
    design_id: str = Field(description="Selected design catalog ID from the 32 options")
    design_name: Optional[str] = None
    category: Optional[str] = None
    style: Optional[str] = None
    
    # Configurable finishes
    wall_finish_choice: Optional[str] = None
    flooring_choice: Optional[str] = None
    ceiling_option_id: Optional[str] = None
    lighting_points_count: int = Field(ge=0, default=0)
    customizations: Dict[str, Any] = Field(default_factory=dict)
    
    # Cost impact
    additional_cost: float = Field(ge=0.0, default=0.0)
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)
    
    # Personalized generation
    personalized_image_url: Optional[str] = None
    personalized_image_prompt: Optional[str] = None
    preview_mode: Optional[str] = "geometry_grounded"


class ProjectInteriorSelectionsPayload(BaseModel):
    project_id: str
    floor_plan_id: Optional[str] = None
    selections: Dict[str, RoomInteriorSelection] = Field(default_factory=dict)
    total_interior_cost: float = Field(ge=0.0, default=0.0)
    updated_at: Optional[str] = None


class CalculateInteriorCostRequest(BaseModel):
    project_id: str
    floor_plan_id: Optional[str] = None
    layout_data: Optional[Dict[str, Any]] = None
    selections: Dict[str, RoomInteriorSelection]


class RoomImageGenerationRequest(BaseModel):
    project_id: str
    room_id: str
    room_type: str
    room_name: Optional[str] = "Room"
    room_width: float = Field(ge=1.0)
    room_length: float = Field(ge=1.0)
    room_area: Optional[float] = None
    design_id: str
    doors: Optional[List[Dict[str, Any]]] = None
    windows: Optional[List[Dict[str, Any]]] = None
    floor_name: Optional[str] = "Ground Floor"
    customizations: Dict[str, Any] = Field(default_factory=dict)
    force_regenerate: bool = False


class RoomImageGenerationResponse(BaseModel):
    status: str
    image_url: Optional[str] = None
    prompt_used: str
    room_id: str
    design_id: str
    provider: str
    dimensions: Dict[str, Any]
    error_detail: Optional[str] = None
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)
