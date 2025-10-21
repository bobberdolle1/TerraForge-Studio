"""
OpenStreetMap data extraction using osmnx
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import osmnx as ox
import networkx as nx
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd

from ..models import (
    BoundingBox, RoadSegment, RoadType, TrafficLight, 
    ParkingLot, Building, VegetationArea
)
from ..config import settings

logger = logging.getLogger(__name__)


class OSMExtractor:
    """Extract and process OpenStreetMap data"""
    
    def __init__(self):
        # Configure osmnx
        ox.config(use_cache=settings.osm_cache_enabled,
                  cache_folder=str(settings.cache_dir / "osm"),
                  timeout=settings.osm_timeout,
                  log_console=False)
        
    def extract_all_data(
        self, 
        bbox: BoundingBox
    ) -> Dict[str, Any]:
        """
        Extract all relevant OSM data for the bounding box
        
        Args:
            bbox: Geographic bounding box
            
        Returns:
            Dictionary containing roads, buildings, traffic lights, etc.
        """
        logger.info(f"Extracting OSM data for bbox: {bbox}")
        
        result = {
            "roads": self.extract_roads(bbox),
            "buildings": self.extract_buildings(bbox),
            "traffic_lights": self.extract_traffic_lights(bbox),
            "parking_lots": self.extract_parking(bbox),
            "vegetation": self.extract_vegetation(bbox)
        }
        
        logger.info(f"Extracted: {len(result['roads'])} roads, "
                   f"{len(result['buildings'])} buildings, "
                   f"{len(result['traffic_lights'])} traffic lights, "
                   f"{len(result['parking_lots'])} parking lots, "
                   f"{len(result['vegetation'])} vegetation areas")
        
        return result
    
    def extract_roads(self, bbox: BoundingBox) -> List[RoadSegment]:
        """Extract road network from OSM"""
        try:
            # Get road network using new API
            G = ox.graph.graph_from_bbox(
                north=bbox.north,
                south=bbox.south,
                east=bbox.east,
                west=bbox.west,
                network_type='all',
                simplify=True
            )
            
            roads = []
            for u, v, data in G.edges(data=True):
                # Get geometry
                if 'geometry' in data:
                    coords = [(point[1], point[0]) for point in data['geometry'].coords]
                else:
                    # Use node coordinates
                    u_coords = (G.nodes[u]['y'], G.nodes[u]['x'])
                    v_coords = (G.nodes[v]['y'], G.nodes[v]['x'])
                    coords = [u_coords, v_coords]
                
                # Determine road type
                highway = data.get('highway', 'unclassified')
                if isinstance(highway, list):
                    highway = highway[0]
                
                road_type = self._map_highway_to_road_type(highway)
                
                # Get additional properties
                lanes = data.get('lanes', 1)
                if isinstance(lanes, str):
                    try:
                        lanes = int(lanes)
                    except ValueError:
                        lanes = 1
                
                max_speed = data.get('maxspeed')
                if isinstance(max_speed, str):
                    try:
                        max_speed = int(max_speed.replace('km/h', '').strip())
                    except (ValueError, AttributeError):
                        max_speed = None
                
                oneway = data.get('oneway', False)
                if isinstance(oneway, str):
                    oneway = oneway.lower() in ['yes', 'true', '1']
                
                roads.append(RoadSegment(
                    osm_id=str(data.get('osmid', f"{u}_{v}")),
                    road_type=road_type,
                    geometry=coords,
                    name=data.get('name'),
                    lanes=lanes,
                    width=self._estimate_road_width(road_type, lanes),
                    max_speed=max_speed,
                    oneway=bool(oneway),
                    surface=data.get('surface')
                ))
            
            return roads
            
        except Exception as e:
            logger.error(f"Error extracting roads: {e}")
            return []
    
    def extract_buildings(self, bbox: BoundingBox) -> List[Building]:
        """Extract buildings from OSM"""
        try:
            buildings_gdf = ox.features.features_from_bbox(
                north=bbox.north,
                south=bbox.south,
                east=bbox.east,
                west=bbox.west,
                tags={'building': True}
            )
            
            buildings = []
            for idx, row in buildings_gdf.iterrows():
                geom = row.geometry
                
                # Extract polygon coordinates
                if geom.geom_type == 'Polygon':
                    coords = [(point[1], point[0]) for point in geom.exterior.coords]
                elif geom.geom_type == 'MultiPolygon':
                    # Use the largest polygon
                    largest = max(geom.geoms, key=lambda p: p.area)
                    coords = [(point[1], point[0]) for point in largest.exterior.coords]
                else:
                    continue
                
                # Get building properties
                height = row.get('height')
                if isinstance(height, str):
                    try:
                        height = float(height.replace('m', '').strip())
                    except (ValueError, AttributeError):
                        height = None
                
                levels = row.get('building:levels')
                if isinstance(levels, str):
                    try:
                        levels = int(levels)
                    except ValueError:
                        levels = None
                
                # Estimate height from levels if not provided
                if height is None and levels:
                    height = levels * 3.0  # Assume 3m per level
                
                buildings.append(Building(
                    osm_id=str(idx[1] if isinstance(idx, tuple) else idx),
                    geometry=coords,
                    height=height,
                    levels=levels,
                    building_type=row.get('building')
                ))
            
            return buildings
            
        except Exception as e:
            logger.error(f"Error extracting buildings: {e}")
            return []
    
    def extract_traffic_lights(self, bbox: BoundingBox) -> List[TrafficLight]:
        """Extract traffic lights from OSM"""
        try:
            traffic_gdf = ox.features.features_from_bbox(
                north=bbox.north,
                south=bbox.south,
                east=bbox.east,
                west=bbox.west,
                tags={'highway': 'traffic_signals'}
            )
            
            traffic_lights = []
            for idx, row in traffic_gdf.iterrows():
                geom = row.geometry
                
                if geom.geom_type == 'Point':
                    traffic_lights.append(TrafficLight(
                        position=(geom.y, geom.x),
                        osm_id=str(idx[1] if isinstance(idx, tuple) else idx),
                        direction=row.get('direction')
                    ))
            
            return traffic_lights
            
        except Exception as e:
            logger.error(f"Error extracting traffic lights: {e}")
            return []
    
    def extract_parking(self, bbox: BoundingBox) -> List[ParkingLot]:
        """Extract parking areas from OSM"""
        try:
            parking_gdf = ox.features.features_from_bbox(
                north=bbox.north,
                south=bbox.south,
                east=bbox.east,
                west=bbox.west,
                tags={'amenity': 'parking'}
            )
            
            parking_lots = []
            for idx, row in parking_gdf.iterrows():
                geom = row.geometry
                
                # Extract polygon coordinates
                if geom.geom_type == 'Polygon':
                    coords = [(point[1], point[0]) for point in geom.exterior.coords]
                elif geom.geom_type == 'MultiPolygon':
                    largest = max(geom.geoms, key=lambda p: p.area)
                    coords = [(point[1], point[0]) for point in largest.exterior.coords]
                else:
                    continue
                
                capacity = row.get('capacity')
                if isinstance(capacity, str):
                    try:
                        capacity = int(capacity)
                    except ValueError:
                        capacity = None
                
                parking_lots.append(ParkingLot(
                    osm_id=str(idx[1] if isinstance(idx, tuple) else idx),
                    geometry=coords,
                    capacity=capacity,
                    surface=row.get('surface'),
                    parking_type=row.get('parking', 'surface')
                ))
            
            return parking_lots
            
        except Exception as e:
            logger.error(f"Error extracting parking: {e}")
            return []
    
    def extract_vegetation(self, bbox: BoundingBox) -> List[VegetationArea]:
        """Extract vegetation areas from OSM"""
        try:
            # Extract forests and parks
            vegetation_gdf = ox.features.features_from_bbox(
                north=bbox.north,
                south=bbox.south,
                east=bbox.east,
                west=bbox.west,
                tags={'natural': ['wood', 'tree', 'tree_row'], 
                      'landuse': ['forest', 'grass', 'meadow']}
            )
            
            vegetation_areas = []
            for idx, row in vegetation_gdf.iterrows():
                geom = row.geometry
                
                # Extract polygon coordinates
                if geom.geom_type == 'Polygon':
                    coords = [(point[1], point[0]) for point in geom.exterior.coords]
                elif geom.geom_type == 'MultiPolygon':
                    largest = max(geom.geoms, key=lambda p: p.area)
                    coords = [(point[1], point[0]) for point in largest.exterior.coords]
                elif geom.geom_type == 'LineString':
                    # For tree rows, create a small buffer
                    continue
                else:
                    continue
                
                # Determine vegetation type
                natural_tag = row.get('natural', '')
                landuse_tag = row.get('landuse', '')
                
                if 'tree' in str(natural_tag) or 'forest' in str(landuse_tag) or 'wood' in str(natural_tag):
                    veg_type = 'tree'
                    density = 0.8
                elif 'grass' in str(landuse_tag) or 'meadow' in str(landuse_tag):
                    veg_type = 'grass'
                    density = 0.6
                else:
                    veg_type = 'tree'
                    density = 0.5
                
                vegetation_areas.append(VegetationArea(
                    geometry=coords,
                    vegetation_type=veg_type,
                    density=density
                ))
            
            return vegetation_areas
            
        except Exception as e:
            logger.error(f"Error extracting vegetation: {e}")
            return []
    
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
        """Estimate road width in meters based on type and lanes"""
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
