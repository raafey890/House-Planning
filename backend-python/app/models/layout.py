from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field

class Point2D(BaseModel):
    x: float
    y: float

class Setbacks(BaseModel):
    front: float = 0.0
    back: float = 0.0
    left: float = 0.0
    right: float = 0.0

class BoundingBox(BaseModel):
    width: float
    length: float

class Plot(BaseModel):
    width: float
    length: float
    facing: str
    origin: Point2D = Field(default_factory=lambda: Point2D(x=0.0, y=0.0))
    buildable_boundary: BoundingBox
    setbacks: Setbacks
    # Phase 6C.5 additions — all optional for backward compat
    front_side: Optional[str] = None          # e.g. "south"
    gates: List[Dict[str, Any]] = Field(default_factory=list)
    driveway: Optional[Dict[str, Any]] = None
    building_footprint: Optional[Dict[str, float]] = None
    site_areas: List[Dict[str, Any]] = Field(default_factory=list)

class Room(BaseModel):
    id: str
    type: str
    label: str
    x: float
    y: float
    width: float
    length: float
    area: float
    rotation: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Phase 6C.5: space classification
    space_category: Optional[str] = None  # public/service/private/circulation/outdoor
    polygon: Optional[List[Point2D]] = None # Phase 6C.8A: complex shapes

class Wall(BaseModel):
    id: str
    start: Point2D
    end: Point2D
    thickness: float
    type: str = "interior"

class Door(BaseModel):
    id: str
    wall_id: Optional[str] = None
    room_ids: List[str] = Field(default_factory=list)
    position: Point2D
    width: float
    swing_direction: Optional[str] = None
    type: str = "swing"  # can also be "main_entrance"

class Window(BaseModel):
    id: str
    wall_id: Optional[str] = None
    room_id: Optional[str] = None
    position: Point2D
    width: float
    type: str = "sliding"

class Stair(BaseModel):
    id: str
    x: float
    y: float
    width: float
    length: float
    direction: str = "up"
    connects_levels: List[int] = Field(default_factory=list)

class Circulation(BaseModel):
    id: str
    type: str = "corridor"
    geometry: List[Point2D] = Field(default_factory=list)

class Floor(BaseModel):
    level: int
    name: str
    elevation: float = 0.0
    rooms: List[Room] = Field(default_factory=list)
    walls: List[Wall] = Field(default_factory=list)
    doors: List[Door] = Field(default_factory=list)
    windows: List[Window] = Field(default_factory=list)
    openings: List[Dict[str, Any]] = Field(default_factory=list)
    circulation: List[Circulation] = Field(default_factory=list)
    stairs: List[Stair] = Field(default_factory=list)
    balconies: List[Dict[str, Any]] = Field(default_factory=list)
    parking: List[Dict[str, Any]] = Field(default_factory=list)
    outdoor_areas: List[Room] = Field(default_factory=list)

class LayoutData(BaseModel):
    schema_version: str = "1.0"
    units: str = "ft"
    plot: Plot
    floors: List[Floor] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Phase 6C.5: validation results
    validation_results: Dict[str, Any] = Field(default_factory=dict)
