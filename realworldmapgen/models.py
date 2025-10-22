"""
Data models for RealWorldMapGen-BNG
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class TerrainType(str, Enum):
    """Types of terrain identified by AI"""
    FOREST = "forest"
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"
    WATER = "water"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    INDUSTRIAL = "industrial"
    MIXED = "mixed"


class RoadType(str, Enum):
    """Types of roads from OSM"""
    MOTORWAY = "motorway"
    TRUNK = "trunk"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    RESIDENTIAL = "residential"
    SERVICE = "service"
    TRACK = "track"
    PATH = "path"
    FOOTWAY = "footway"


class BoundingBox(BaseModel):
    """Geographic bounding box"""
    north: float = Field(..., description="North latitude")
    south: float = Field(..., description="South latitude")
    east: float = Field(..., description="East longitude")
    west: float = Field(..., description="West longitude")
    
    def center(self) -> Tuple[float, float]:
        """Calculate center point"""
        return ((self.north + self.south) / 2, (self.east + self.west) / 2)
    
    def area_km2(self) -> float:
        """Calculate approximate area in square kilometers"""
        from math import cos, radians
        lat_diff = self.north - self.south
        lon_diff = self.east - self.west
        avg_lat = (self.north + self.south) / 2
        area = abs(lat_diff * lon_diff * cos(radians(avg_lat)) * 111.32 * 111.32)
        return area


class ExportFormat(str, Enum):
    """Available export formats"""
    UNREAL5 = "unreal5"
    UNITY = "unity"
    GLTF = "gltf"
    GEOTIFF = "geotiff"
    OBJ = "obj"
    ALL = "all"


class ElevationSource(str, Enum):
    """Available elevation data sources"""
    SRTM = "srtm"
    OPENTOPOGRAPHY = "opentopography"
    SENTINELHUB = "sentinelhub"
    AZURE_MAPS = "azure_maps"
    AUTO = "auto"  # Automatic selection based on availability


class MapGenerationRequest(BaseModel):
    """Request to generate a terrain"""
    bbox: BoundingBox
    name: str = Field(..., description="Terrain name")
    resolution: Optional[int] = Field(2048, description="Heightmap resolution")
    export_formats: List[ExportFormat] = Field(
        [ExportFormat.UNREAL5], 
        description="Export formats (unreal5, unity, gltf, geotiff, all)"
    )
    elevation_source: ElevationSource = Field(
        ElevationSource.AUTO,
        description="Elevation data source"
    )
    enable_ai_analysis: bool = Field(False, description="Enable AI terrain analysis (requires Ollama)")
    enable_roads: bool = Field(True, description="Generate roads")
    enable_buildings: bool = Field(True, description="Generate buildings")
    enable_vegetation: bool = Field(True, description="Generate vegetation")
    enable_water_bodies: bool = Field(True, description="Detect water bodies")
    enable_weightmaps: bool = Field(True, description="Generate material weightmaps (UE5/Unity)")
    enable_3d_preview: bool = Field(False, description="Generate 3D preview")


class AIAnalysisResult(BaseModel):
    """Result from AI terrain analysis"""
    terrain_type: TerrainType
    dominant_features: List[str]
    building_density: float = Field(0.0, ge=0.0, le=1.0)
    vegetation_density: float = Field(0.0, ge=0.0, le=1.0)
    road_density: float = Field(0.0, ge=0.0, le=1.0)
    suggestions: List[str] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)


class RoadSegment(BaseModel):
    """A road segment"""
    osm_id: str
    road_type: RoadType
    geometry: List[Tuple[float, float]]  # List of (lat, lon) points
    name: Optional[str] = None
    lanes: int = 1
    width: float = 3.5  # meters
    max_speed: Optional[int] = None  # km/h
    oneway: bool = False
    surface: Optional[str] = None


class TrafficLight(BaseModel):
    """Traffic light placement"""
    position: Tuple[float, float]  # (lat, lon)
    osm_id: Optional[str] = None
    intersection_id: Optional[str] = None
    direction: Optional[float] = None  # degrees


class ParkingLot(BaseModel):
    """Parking lot"""
    osm_id: str
    geometry: List[Tuple[float, float]]  # Polygon points
    capacity: Optional[int] = None
    surface: Optional[str] = None
    parking_type: str = "surface"  # surface, underground, multi-storey


class Building(BaseModel):
    """Building structure"""
    osm_id: str
    geometry: List[Tuple[float, float]]  # Polygon points
    height: Optional[float] = None  # meters
    levels: Optional[int] = None
    building_type: Optional[str] = None


class VegetationArea(BaseModel):
    """Vegetation area"""
    geometry: List[Tuple[float, float]]  # Polygon points
    vegetation_type: str  # tree, grass, bush
    density: float = 0.5


class TrafficRoute(BaseModel):
    """AI-optimized traffic route"""
    waypoints: List[Tuple[float, float]]
    route_type: str = "primary"  # primary, secondary, local
    total_distance: float = 0.0  # in meters
    avg_speed: float = 50.0  # km/h
    priority: float = 1.0  # 0.0-1.0


class MapData(BaseModel):
    """Complete map data structure"""
    name: str
    bbox: BoundingBox
    ai_analysis: Optional[AIAnalysisResult] = None
    heightmap_path: Optional[str] = None
    roads: List[RoadSegment] = Field(default_factory=list)
    traffic_lights: List[TrafficLight] = Field(default_factory=list)
    parking_lots: List[ParkingLot] = Field(default_factory=list)
    buildings: List[Building] = Field(default_factory=list)
    vegetation: List[VegetationArea] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenerationStatus(BaseModel):
    """Status of map generation"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float = Field(0.0, ge=0.0, le=100.0)
    current_step: str = ""
    message: Optional[str] = None
    result: Optional[MapData] = None
    error: Optional[str] = None
