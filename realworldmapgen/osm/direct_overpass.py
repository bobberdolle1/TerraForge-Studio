"""
Direct Overpass API client - reliable alternative to osmnx
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from ..models import (
    BoundingBox, RoadSegment, RoadType, TrafficLight, 
    ParkingLot, Building, VegetationArea
)

logger = logging.getLogger(__name__)


class DirectOverpassClient:
    """Direct HTTP client for Overpass API"""
    
    # List of Overpass API servers (fallback chain)
    ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.openstreetmap.ru/api/interpreter",
    ]
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RealWorldMapGen-BNG/0.1.0'
        })
    
    def query(self, overpass_ql: str) -> Optional[Dict[str, Any]]:
        """
        Execute Overpass QL query with automatic fallback
        
        Args:
            overpass_ql: Overpass QL query string
            
        Returns:
            Parsed JSON response or None if all endpoints fail
        """
        last_error = None
        
        for endpoint in self.ENDPOINTS:
            try:
                logger.info(f"Querying {endpoint}...")
                
                response = self.session.post(
                    endpoint,
                    data=overpass_ql,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✓ Success from {endpoint}")
                    return data
                elif response.status_code == 504:
                    logger.warning(f"⚠️  Timeout from {endpoint} (504)")
                    last_error = "Gateway timeout"
                    continue
                elif response.status_code == 429:
                    logger.warning(f"⚠️  Rate limited by {endpoint} (429)")
                    last_error = "Rate limited"
                    continue
                else:
                    logger.warning(f"⚠️  HTTP {response.status_code} from {endpoint}")
                    last_error = f"HTTP {response.status_code}"
                    continue
                    
            except requests.Timeout:
                logger.warning(f"⚠️  Timeout connecting to {endpoint}")
                last_error = "Connection timeout"
                continue
            except requests.RequestException as e:
                logger.warning(f"⚠️  Request failed to {endpoint}: {e}")
                last_error = str(e)
                continue
            except Exception as e:
                logger.error(f"⚠️  Unexpected error with {endpoint}: {e}")
                last_error = str(e)
                continue
        
        logger.error(f"✗ All Overpass endpoints failed. Last error: {last_error}")
        return None
    
    def extract_roads(self, bbox: BoundingBox) -> List[RoadSegment]:
        """Extract roads from OSM using Overpass API"""
        
        # Overpass QL query for roads
        query = f"""
[out:json][timeout:{self.timeout}];
(
  way["highway"]
     ["highway"!~"footway|cycleway|path|pedestrian|steps|track|service"]
     ["access"!~"private|no"]
     ({bbox.south},{bbox.west},{bbox.north},{bbox.east});
);
out geom;
"""
        
        logger.info(f"Extracting roads for area: {bbox.area_km2():.3f} km²")
        
        data = self.query(query)
        if not data:
            logger.warning("No data returned from Overpass API for roads")
            return []
        
        elements = data.get("elements", [])
        logger.info(f"Received {len(elements)} road elements from Overpass API")
        
        roads = []
        for elem in elements:
            try:
                if elem.get("type") != "way":
                    continue
                
                # Get geometry
                geometry = elem.get("geometry", [])
                if not geometry or len(geometry) < 2:
                    continue
                
                # Convert to (lat, lon) tuples
                coords = [(point["lat"], point["lon"]) for point in geometry]
                
                # Get tags
                tags = elem.get("tags", {})
                highway = tags.get("highway", "unclassified")
                
                # Map to road type
                road_type = self._map_highway_to_road_type(highway)
                
                # Get lanes
                lanes = tags.get("lanes", "1")
                try:
                    lanes = int(lanes) if isinstance(lanes, str) else lanes
                except (ValueError, TypeError):
                    lanes = 1
                
                # Get max speed
                max_speed = tags.get("maxspeed")
                if max_speed and isinstance(max_speed, str):
                    try:
                        max_speed = int(max_speed.replace("km/h", "").replace("mph", "").strip())
                    except (ValueError, AttributeError):
                        max_speed = None
                
                # Check if oneway
                oneway = tags.get("oneway", "no") in ["yes", "true", "1"]
                
                roads.append(RoadSegment(
                    osm_id=str(elem.get("id")),
                    road_type=road_type,
                    geometry=coords,
                    name=tags.get("name"),
                    lanes=lanes,
                    width=self._estimate_road_width(road_type, lanes),
                    max_speed=max_speed,
                    oneway=oneway,
                    surface=tags.get("surface")
                ))
                
            except Exception as e:
                logger.warning(f"Failed to process road element: {e}")
                continue
        
        logger.info(f"✓ Processed {len(roads)} roads")
        return roads
    
    def extract_buildings(self, bbox: BoundingBox) -> List[Building]:
        """Extract buildings from OSM"""
        
        query = f"""
[out:json][timeout:{self.timeout}];
(
  way["building"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
  relation["building"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
);
out geom;
"""
        
        logger.info("Extracting buildings...")
        data = self.query(query)
        if not data:
            return []
        
        elements = data.get("elements", [])
        logger.info(f"Received {len(elements)} building elements")
        
        buildings = []
        for elem in elements:
            try:
                if elem.get("type") not in ["way", "relation"]:
                    continue
                
                # Get geometry
                if elem.get("type") == "way":
                    geometry = elem.get("geometry", [])
                    if not geometry or len(geometry) < 3:
                        continue
                    coords = [(point["lat"], point["lon"]) for point in geometry]
                elif elem.get("type") == "relation":
                    # For relations, get outer members
                    members = elem.get("members", [])
                    outer = [m for m in members if m.get("role") == "outer"]
                    if not outer or not outer[0].get("geometry"):
                        continue
                    coords = [(point["lat"], point["lon"]) for point in outer[0]["geometry"]]
                else:
                    continue
                
                tags = elem.get("tags", {})
                
                # Get height
                height = tags.get("height")
                if height and isinstance(height, str):
                    try:
                        height = float(height.replace("m", "").strip())
                    except (ValueError, AttributeError):
                        height = None
                
                # Get levels
                levels = tags.get("building:levels")
                if levels and isinstance(levels, str):
                    try:
                        levels = int(levels)
                    except ValueError:
                        levels = None
                
                # Estimate height from levels
                if not height and levels:
                    height = levels * 3.0
                
                buildings.append(Building(
                    osm_id=str(elem.get("id")),
                    geometry=coords,
                    height=height,
                    levels=levels,
                    building_type=tags.get("building", "yes")
                ))
                
            except Exception as e:
                logger.warning(f"Failed to process building: {e}")
                continue
        
        logger.info(f"✓ Processed {len(buildings)} buildings")
        return buildings
    
    def extract_traffic_lights(self, bbox: BoundingBox) -> List[TrafficLight]:
        """Extract traffic lights from OSM"""
        
        query = f"""
[out:json][timeout:{self.timeout}];
(
  node["highway"="traffic_signals"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
);
out;
"""
        
        logger.info("Extracting traffic lights...")
        data = self.query(query)
        if not data:
            return []
        
        elements = data.get("elements", [])
        logger.info(f"Received {len(elements)} traffic light elements")
        
        traffic_lights = []
        for elem in elements:
            try:
                if elem.get("type") != "node":
                    continue
                
                lat = elem.get("lat")
                lon = elem.get("lon")
                if lat is None or lon is None:
                    continue
                
                tags = elem.get("tags", {})
                
                traffic_lights.append(TrafficLight(
                    position=(lat, lon),
                    osm_id=str(elem.get("id")),
                    direction=tags.get("direction")
                ))
                
            except Exception as e:
                logger.warning(f"Failed to process traffic light: {e}")
                continue
        
        logger.info(f"✓ Processed {len(traffic_lights)} traffic lights")
        return traffic_lights
    
    def extract_parking(self, bbox: BoundingBox) -> List[ParkingLot]:
        """Extract parking lots from OSM"""
        
        query = f"""
[out:json][timeout:{self.timeout}];
(
  way["amenity"="parking"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
  relation["amenity"="parking"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
);
out geom;
"""
        
        logger.info("Extracting parking lots...")
        data = self.query(query)
        if not data:
            return []
        
        elements = data.get("elements", [])
        logger.info(f"Received {len(elements)} parking elements")
        
        parking_lots = []
        for elem in elements:
            try:
                # Get geometry similar to buildings
                if elem.get("type") == "way":
                    geometry = elem.get("geometry", [])
                    if not geometry or len(geometry) < 3:
                        continue
                    coords = [(point["lat"], point["lon"]) for point in geometry]
                elif elem.get("type") == "relation":
                    members = elem.get("members", [])
                    outer = [m for m in members if m.get("role") == "outer"]
                    if not outer or not outer[0].get("geometry"):
                        continue
                    coords = [(point["lat"], point["lon"]) for point in outer[0]["geometry"]]
                else:
                    continue
                
                tags = elem.get("tags", {})
                
                capacity = tags.get("capacity")
                if capacity and isinstance(capacity, str):
                    try:
                        capacity = int(capacity)
                    except ValueError:
                        capacity = None
                
                parking_lots.append(ParkingLot(
                    osm_id=str(elem.get("id")),
                    geometry=coords,
                    capacity=capacity,
                    surface=tags.get("surface"),
                    parking_type=tags.get("parking", "surface")
                ))
                
            except Exception as e:
                logger.warning(f"Failed to process parking lot: {e}")
                continue
        
        logger.info(f"✓ Processed {len(parking_lots)} parking lots")
        return parking_lots
    
    def extract_vegetation(self, bbox: BoundingBox) -> List[VegetationArea]:
        """Extract vegetation areas from OSM"""
        
        query = f"""
[out:json][timeout:{self.timeout}];
(
  way["natural"~"wood|tree|tree_row"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
  way["landuse"~"forest|grass|meadow"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
  relation["natural"~"wood|tree"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
  relation["landuse"~"forest|grass|meadow"]({bbox.south},{bbox.west},{bbox.north},{bbox.east});
);
out geom;
"""
        
        logger.info("Extracting vegetation...")
        data = self.query(query)
        if not data:
            return []
        
        elements = data.get("elements", [])
        logger.info(f"Received {len(elements)} vegetation elements")
        
        vegetation_areas = []
        for elem in elements:
            try:
                # Get geometry
                if elem.get("type") == "way":
                    geometry = elem.get("geometry", [])
                    if not geometry or len(geometry) < 3:
                        continue
                    coords = [(point["lat"], point["lon"]) for point in geometry]
                elif elem.get("type") == "relation":
                    members = elem.get("members", [])
                    outer = [m for m in members if m.get("role") == "outer"]
                    if not outer or not outer[0].get("geometry"):
                        continue
                    coords = [(point["lat"], point["lon"]) for point in outer[0]["geometry"]]
                else:
                    continue
                
                tags = elem.get("tags", {})
                natural_tag = tags.get("natural", "")
                landuse_tag = tags.get("landuse", "")
                
                # Determine vegetation type and density
                if "tree" in natural_tag or "forest" in landuse_tag or "wood" in natural_tag:
                    veg_type = "tree"
                    density = 0.8
                elif "grass" in landuse_tag or "meadow" in landuse_tag:
                    veg_type = "grass"
                    density = 0.6
                else:
                    veg_type = "tree"
                    density = 0.5
                
                vegetation_areas.append(VegetationArea(
                    geometry=coords,
                    vegetation_type=veg_type,
                    density=density
                ))
                
            except Exception as e:
                logger.warning(f"Failed to process vegetation: {e}")
                continue
        
        logger.info(f"✓ Processed {len(vegetation_areas)} vegetation areas")
        return vegetation_areas
    
    def _map_highway_to_road_type(self, highway: str) -> RoadType:
        """Map OSM highway tag to RoadType enum"""
        mapping = {
            'motorway': RoadType.MOTORWAY,
            'motorway_link': RoadType.MOTORWAY,
            'trunk': RoadType.TRUNK,
            'trunk_link': RoadType.TRUNK,
            'primary': RoadType.PRIMARY,
            'primary_link': RoadType.PRIMARY,
            'secondary': RoadType.SECONDARY,
            'secondary_link': RoadType.SECONDARY,
            'tertiary': RoadType.TERTIARY,
            'tertiary_link': RoadType.TERTIARY,
            'residential': RoadType.RESIDENTIAL,
            'service': RoadType.SERVICE,
            'track': RoadType.TRACK,
            'path': RoadType.PATH,
            'footway': RoadType.FOOTWAY,
            'pedestrian': RoadType.FOOTWAY,
        }
        return mapping.get(highway.lower(), RoadType.RESIDENTIAL)
    
    def _estimate_road_width(self, road_type: RoadType, lanes: int) -> float:
        """Estimate road width in meters"""
        lane_width = {
            RoadType.MOTORWAY: 3.75,
            RoadType.TRUNK: 3.5,
            RoadType.PRIMARY: 3.5,
            RoadType.SECONDARY: 3.25,
            RoadType.TERTIARY: 3.0,
            RoadType.RESIDENTIAL: 3.0,
            RoadType.SERVICE: 2.5,
            RoadType.TRACK: 2.0,
            RoadType.PATH: 1.5,
            RoadType.FOOTWAY: 1.5,
        }
        return lane_width.get(road_type, 3.0) * lanes

