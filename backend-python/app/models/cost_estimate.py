"""
Construction Cost Estimation Models — Phase 6D.
Pydantic schemas for area schedules, material rates, quantity calculations,
line items, cost summaries, and estimation requests/responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import datetime


class RateItem(BaseModel):
    category: str = Field(description="Category: materials, masonry, finishes, fixtures, labor, allowances")
    item_key: str = Field(description="Unique machine identifier for rate key")
    name: str = Field(description="Human readable item name")
    unit: str = Field(description="Unit of measurement: bag, piece, cu ft, sq ft, kg, metric tonne, liter, unit")
    unit_rate: float = Field(ge=0.0, description="Unit rate in INR (₹). Must be non-negative.")
    description: Optional[str] = None
    is_labor_included: bool = False
    is_wastage_included: bool = False
    confidence: str = Field(default="illustrative", description="illustrative | market_benchmark | engineer_boq | user_specified")
    source: str = Field(default="Hyderabad (Telangana) Benchmark 2026", description="Source of rate data")
    effective_date: str = Field(default="2026-10-16", description="Effective date YYYY-MM-DD")

    @field_validator("unit_rate")
    @classmethod
    def validate_rate(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Unit rate cannot be negative")
        return round(v, 2)


class RateProfile(BaseModel):
    profile_id: str = "hyderabad_telangana_benchmark"
    location_name: str = "Hyderabad, Telangana (INR ₹)"
    currency: str = "INR"
    currency_symbol: str = "₹"
    status: str = "illustrative_benchmark"
    last_updated: str = Field(default_factory=lambda: datetime.date.today().isoformat())
    notes: str = "Benchmark construction rates for residential RCC structure in Hyderabad region. Sourced for planning and budgeting estimates."
    rates: Dict[str, RateItem] = Field(default_factory=dict)


class AreaScheduleSummary(BaseModel):
    plot_area: float = Field(ge=0.0, description="Total plot area in sq ft")
    ground_constructed_footprint: float = Field(ge=0.0, description="Ground floor true constructed slab area in sq ft")
    built_up_by_floor: Dict[int, float] = Field(default_factory=dict, description="Constructed slab built-up area per floor")
    total_built_up_area: float = Field(ge=0.0, description="Total constructed built-up area across all floors in sq ft")
    indoor_room_area_by_floor: Dict[int, float] = Field(default_factory=dict, description="Net usable indoor room area per floor")
    total_indoor_room_area: float = Field(ge=0.0, description="Total usable indoor room area in sq ft")
    outdoor_areas: List[Dict[str, Any]] = Field(default_factory=list, description="Ground & site outdoor areas (gardens, yards, parking)")
    terrace_roof_areas: List[Dict[str, Any]] = Field(default_factory=list, description="Upper outdoor spaces (balconies, open terraces, roof slab below)")
    wall_footprint_area: float = Field(ge=0.0, description="Area occupied by walls = BUA - indoor room area")
    derivation_method: str = "Shapely exact polygon union and disjoint decomposition"


class CostLineItem(BaseModel):
    id: str = Field(description="Unique line item ID")
    category: str = Field(description="masonry | concrete | structural_steel | flooring | finishes | openings | services | labor | overhead")
    item_name: str = Field(description="Line item description")
    quantity: float = Field(ge=0.0, description="Calculated quantity")
    unit: str = Field(description="Unit of measurement")
    unit_rate: float = Field(ge=0.0, description="Unit rate in INR ₹")
    amount: float = Field(ge=0.0, description="Calculated amount = Quantity × Unit Rate")
    classification: str = Field(description="geometry_derived | provisional_allowance | fixture_count | specification_derived")
    formula: str = Field(description="Explicit engineering formula or calculation origin")
    assumptions: str = Field(description="Underlying engineering assumptions or limitations")
    confidence: str = Field(default="benchmark", description="exact | high | benchmark | provisional")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        return round(v, 2)


class EstimateRequest(BaseModel):
    floor_plan_id: Optional[str] = None
    layout_data: Optional[Dict[str, Any]] = None
    custom_rates: Optional[Dict[str, float]] = None
    custom_specifications: Optional[Dict[str, Any]] = None


class EstimateRecalculateRequest(BaseModel):
    current_estimate_id: Optional[str] = None
    floor_plan_id: Optional[str] = None
    layout_data: Optional[Dict[str, Any]] = None
    custom_rates: Dict[str, float]
    custom_specifications: Optional[Dict[str, Any]] = None


class CostSummary(BaseModel):
    materials_cost: float = Field(ge=0.0)
    labor_cost: float = Field(ge=0.0)
    openings_and_fixtures_cost: float = Field(ge=0.0)
    services_cost: float = Field(ge=0.0)
    subtotal: float = Field(ge=0.0)
    contingency_percentage: float = Field(default=5.0)
    contingency_cost: float = Field(ge=0.0)
    contractor_overhead_percentage: float = Field(default=10.0)
    contractor_overhead_cost: float = Field(ge=0.0)
    tax_percentage: float = Field(default=0.0)
    tax_cost: float = Field(ge=0.0)
    grand_total: float = Field(ge=0.0)
    cost_per_sq_ft: float = Field(ge=0.0)
    cost_per_sq_ft_denominator: str = "Total Constructed Built-Up Area (sq ft)"


class EstimateResponse(BaseModel):
    estimate_id: str
    project_id: str
    floor_plan_id: Optional[str] = None
    created_at: str
    currency: str = "INR"
    currency_symbol: str = "₹"
    location_profile: str = "Hyderabad, Telangana (Benchmark)"
    area_schedule: AreaScheduleSummary
    quantities: Dict[str, Any]
    line_items: List[CostLineItem]
    cost_summary: CostSummary
    rates_snapshot: Dict[str, RateItem]
    assumptions_and_limitations: List[str]
    disclaimer: str
