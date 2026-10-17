from typing import List, Optional
from pydantic import BaseModel, Field

class Point2DProvider(BaseModel):
    x: float
    y: float

class SetbacksProvider(BaseModel):
    front: float = 0.0
    back: float = 0.0
    left: float = 0.0
    right: float = 0.0

class BoundingBoxProvider(BaseModel):
    width: float
    length: float

class PlotProvider(BaseModel):
    width: float
    length: float
    facing: str
    origin: Point2DProvider = Field(default_factory=lambda: Point2DProvider(x=0.0, y=0.0))
    buildable_boundary: BoundingBoxProvider
    setbacks: SetbacksProvider

class RoomMetadataProvider(BaseModel):
    is_primary: bool = False
    has_attached_bath: bool = False
    custom_notes: str = ""

class RoomProvider(BaseModel):
    id: str
    type: str
    label: str
    x: float
    y: float
    width: float
    length: float
    area: float
    rotation: float = 0.0
    metadata: RoomMetadataProvider = Field(default_factory=RoomMetadataProvider)

class WallProvider(BaseModel):
    id: str
    start: Point2DProvider
    end: Point2DProvider
    thickness: float
    type: str = "interior"

class DoorProvider(BaseModel):
    id: str
    wall_id: Optional[str] = None
    room_ids: List[str] = Field(default_factory=list)
    position: Point2DProvider
    width: float
    swing_direction: Optional[str] = None
    type: str = "swing"

class WindowProvider(BaseModel):
    id: str
    wall_id: Optional[str] = None
    room_id: Optional[str] = None
    position: Point2DProvider
    width: float
    type: str = "sliding"

class StairProvider(BaseModel):
    id: str
    x: float
    y: float
    width: float
    length: float
    direction: str = "up"
    connects_levels: List[int] = Field(default_factory=list)

class CirculationProvider(BaseModel):
    id: str
    type: str = "corridor"
    geometry: List[Point2DProvider] = Field(default_factory=list)

class OpeningProvider(BaseModel):
    id: str
    wall_id: Optional[str] = None
    position: Point2DProvider
    width: float
    height: float = 0.0

class BalconyProvider(BaseModel):
    id: str
    room_id: Optional[str] = None
    x: float
    y: float
    width: float
    length: float

class ParkingProvider(BaseModel):
    id: str
    x: float
    y: float
    width: float
    length: float
    capacity: int = 1

class FloorProvider(BaseModel):
    level: int
    name: str
    elevation: float = 0.0
    rooms: List[RoomProvider] = Field(default_factory=list)
    walls: List[WallProvider] = Field(default_factory=list)
    doors: List[DoorProvider] = Field(default_factory=list)
    windows: List[WindowProvider] = Field(default_factory=list)
    openings: List[OpeningProvider] = Field(default_factory=list)
    circulation: List[CirculationProvider] = Field(default_factory=list)
    stairs: List[StairProvider] = Field(default_factory=list)
    balconies: List[BalconyProvider] = Field(default_factory=list)
    parking: List[ParkingProvider] = Field(default_factory=list)

class MetricsProvider(BaseModel):
    total_area: float = 0.0
    built_up_area: float = 0.0
    carpet_area: float = 0.0
    coverage_percentage: float = 0.0

class GenerationMetadataProvider(BaseModel):
    optimization_priority: str = "balanced"
    model_used: str = "gemini-3.8-flash"
    generation_time_ms: int = 0

class GeminiLayoutData(BaseModel):
    schema_version: str = "1.0"
    units: str = "ft"
    plot: PlotProvider
    floors: List[FloorProvider] = Field(default_factory=list)
    metrics: MetricsProvider = Field(default_factory=MetricsProvider)
    generation_metadata: GenerationMetadataProvider = Field(default_factory=GenerationMetadataProvider)


