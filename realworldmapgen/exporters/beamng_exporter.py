"""
BeamNG.drive format exporter
"""

import logging
import json
from typing import Dict, Any, List
from pathlib import Path
import numpy as np

from ..models import MapData, RoadSegment, Building, VegetationArea
from ..config import settings

logger = logging.getLogger(__name__)


class BeamNGExporter:
    """Export map data to BeamNG.drive format"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_complete_map(self, map_data: MapData) -> Dict[str, Path]:
        """
        Export all map components to BeamNG.drive format
        
        Args:
            map_data: Complete map data
            
        Returns:
            Dictionary of exported file paths
        """
        logger.info(f"Exporting map '{map_data.name}' to BeamNG.drive format")
        
        # output_dir already contains map name, no need to add it again
        map_dir = self.output_dir
        map_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        # Export terrain/heightmap (copy to output dir if not already there)
        if map_data.heightmap_path:
            heightmap_src = Path(map_data.heightmap_path)
            if heightmap_src.parent != map_dir:
                # Copy heightmap to map directory
                import shutil
                heightmap_dest = map_dir / heightmap_src.name
                shutil.copy2(heightmap_src, heightmap_dest)
                exported_files['heightmap'] = heightmap_dest
            else:
                exported_files['heightmap'] = heightmap_src
        
        # Export road network
        exported_files['roads'] = self._export_roads(map_data.roads, map_dir)
        
        # Export objects (buildings, vegetation)
        exported_files['objects'] = self._export_objects(map_data, map_dir)
        
        # Export traffic infrastructure
        exported_files['traffic'] = self._export_traffic(map_data, map_dir)
        
        # Export level metadata
        exported_files['metadata'] = self._export_metadata(map_data, map_dir)
        
        # Create main level JSON
        exported_files['level'] = self._create_level_json(map_data, map_dir)
        
        logger.info(f"Export completed: {len(exported_files)} files created")
        return exported_files
    
    def _export_roads(self, roads: List[RoadSegment], map_dir: Path) -> Path:
        """Export road network to BeamNG format"""
        roads_file = map_dir / "roads.json"
        
        roads_data = {
            "version": 1,
            "roads": []
        }
        
        for road in roads:
            # Convert lat/lon to BeamNG coordinates
            nodes = []
            for lat, lon in road.geometry:
                x, y = self._latlon_to_beamng(lat, lon)
                nodes.append({
                    "pos": [x, y, 0],  # Z will be adjusted to terrain
                    "width": road.width
                })
            
            road_data = {
                "id": road.osm_id,
                "name": road.name or f"Road_{road.osm_id}",
                "type": road.road_type.value,
                "nodes": nodes,
                "lanes": road.lanes,
                "oneWay": road.oneway,
                "material": self._get_road_material(road),
                "profile": self._get_road_profile(road)
            }
            
            if road.max_speed:
                road_data["speedLimit"] = road.max_speed
            
            roads_data["roads"].append(road_data)
        
        with open(roads_file, 'w') as f:
            json.dump(roads_data, f, indent=2)
        
        logger.info(f"Exported {len(roads)} roads to {roads_file}")
        return roads_file
    
    def _export_objects(self, map_data: MapData, map_dir: Path) -> Path:
        """Export buildings and vegetation"""
        objects_file = map_dir / "objects.json"
        
        objects_data = {
            "version": 1,
            "buildings": [],
            "vegetation": []
        }
        
        # Export buildings
        for building in map_data.buildings:
            # Get building centroid for placement
            lats = [coord[0] for coord in building.geometry]
            lons = [coord[1] for coord in building.geometry]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            x, y = self._latlon_to_beamng(center_lat, center_lon)
            
            # Create building footprint
            footprint = []
            for lat, lon in building.geometry:
                bx, by = self._latlon_to_beamng(lat, lon)
                footprint.append([bx - x, by - y])  # Relative to center
            
            building_data = {
                "id": building.osm_id,
                "position": [x, y, 0],
                "footprint": footprint,
                "height": building.height or 10.0,
                "levels": building.levels or 3,
                "type": building.building_type or "generic",
                "prefab": self._select_building_prefab(building)
            }
            
            objects_data["buildings"].append(building_data)
        
        # Export vegetation
        for veg_area in map_data.vegetation:
            # Sample points within vegetation area
            points = self._sample_vegetation_points(veg_area)
            
            for point in points:
                x, y = self._latlon_to_beamng(point[0], point[1])
                objects_data["vegetation"].append({
                    "type": veg_area.vegetation_type,
                    "position": [x, y, 0],
                    "scale": np.random.uniform(0.8, 1.2),
                    "rotation": np.random.uniform(0, 360),
                    "prefab": self._select_vegetation_prefab(veg_area.vegetation_type)
                })
        
        with open(objects_file, 'w') as f:
            json.dump(objects_data, f, indent=2)
        
        logger.info(f"Exported {len(objects_data['buildings'])} buildings "
                   f"and {len(objects_data['vegetation'])} vegetation objects")
        return objects_file
    
    def _export_traffic(self, map_data: MapData, map_dir: Path) -> Path:
        """Export traffic lights and parking"""
        traffic_file = map_dir / "traffic.json"
        
        traffic_data = {
            "version": 1,
            "trafficLights": [],
            "parkingLots": []
        }
        
        # Export traffic lights
        for light in map_data.traffic_lights:
            x, y = self._latlon_to_beamng(light.position[0], light.position[1])
            
            traffic_data["trafficLights"].append({
                "id": light.osm_id,
                "position": [x, y, 0],
                "direction": light.direction or 0,
                "type": "standard",
                "cycleTime": 30.0
            })
        
        # Export parking lots
        for parking in map_data.parking_lots:
            # Get parking lot center
            lats = [coord[0] for coord in parking.geometry]
            lons = [coord[1] for coord in parking.geometry]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            x, y = self._latlon_to_beamng(center_lat, center_lon)
            
            # Create parking boundary
            boundary = []
            for lat, lon in parking.geometry:
                px, py = self._latlon_to_beamng(lat, lon)
                boundary.append([px - x, py - y])
            
            traffic_data["parkingLots"].append({
                "id": parking.osm_id,
                "position": [x, y, 0],
                "boundary": boundary,
                "capacity": parking.capacity or self._estimate_parking_capacity(boundary),
                "type": parking.parking_type,
                "surface": parking.surface or "asphalt"
            })
        
        with open(traffic_file, 'w') as f:
            json.dump(traffic_data, f, indent=2)
        
        logger.info(f"Exported {len(traffic_data['trafficLights'])} traffic lights "
                   f"and {len(traffic_data['parkingLots'])} parking lots")
        return traffic_file
    
    def _export_metadata(self, map_data: MapData, map_dir: Path) -> Path:
        """Export map metadata"""
        metadata_file = map_dir / "info.json"
        
        metadata = {
            "name": map_data.name,
            "description": f"Real-world map generated from OSM data",
            "version": "1.0.0",
            "author": "RealWorldMapGen-BNG",
            "bbox": {
                "north": map_data.bbox.north,
                "south": map_data.bbox.south,
                "east": map_data.bbox.east,
                "west": map_data.bbox.west
            },
            "center": map_data.bbox.center(),
            "area_km2": map_data.bbox.area_km2(),
            "ai_analysis": map_data.ai_analysis.dict() if map_data.ai_analysis else None,
            "statistics": {
                "roads": len(map_data.roads),
                "buildings": len(map_data.buildings),
                "traffic_lights": len(map_data.traffic_lights),
                "parking_lots": len(map_data.parking_lots),
                "vegetation_areas": len(map_data.vegetation)
            }
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_file
    
    def _create_level_json(self, map_data: MapData, map_dir: Path) -> Path:
        """Create main BeamNG level JSON"""
        level_file = map_dir / "main.level.json"
        
        level_data = {
            "version": 1,
            "name": map_data.name,
            "levelObjects": [],
            "terrainSize": settings.beamng_terrain_size,
            "heightScale": settings.beamng_height_scale,
            "files": {
                "heightmap": str(Path(map_data.heightmap_path).name) if map_data.heightmap_path else None,
                "roads": "roads.json",
                "objects": "objects.json",
                "traffic": "traffic.json",
                "metadata": "info.json"
            }
        }
        
        with open(level_file, 'w') as f:
            json.dump(level_data, f, indent=2)
        
        return level_file
    
    def _latlon_to_beamng(self, lat: float, lon: float) -> tuple:
        """
        Convert lat/lon to BeamNG coordinate system
        Simplified transformation - in production, use proper projection
        """
        # Scale factor (approximate meters per degree at mid-latitudes)
        x = lon * 111320 * np.cos(np.radians(lat))
        y = lat * 110540
        return (x, y)
    
    def _get_road_material(self, road: RoadSegment) -> str:
        """Determine road material/texture"""
        if road.surface:
            return road.surface.lower()
        
        material_map = {
            "motorway": "asphalt_smooth",
            "trunk": "asphalt_smooth",
            "primary": "asphalt",
            "secondary": "asphalt",
            "tertiary": "asphalt_rough",
            "residential": "asphalt_rough",
            "service": "concrete",
            "track": "dirt",
            "path": "dirt"
        }
        return material_map.get(road.road_type.value, "asphalt")
    
    def _get_road_profile(self, road: RoadSegment) -> Dict[str, Any]:
        """Get road cross-section profile"""
        return {
            "width": road.width,
            "lanes": road.lanes,
            "shoulderWidth": 1.0 if road.lanes > 1 else 0.5,
            "camber": 0.02  # 2% camber
        }
    
    def _select_building_prefab(self, building: Building) -> str:
        """Select appropriate building prefab"""
        # Map building types to BeamNG prefabs
        prefab_map = {
            "house": "residential_house",
            "residential": "residential_building",
            "commercial": "commercial_building",
            "industrial": "industrial_building",
            "retail": "shop",
            "office": "office_building"
        }
        
        building_type = building.building_type or "yes"
        return prefab_map.get(building_type.lower(), "generic_building")
    
    def _select_vegetation_prefab(self, veg_type: str) -> str:
        """Select vegetation prefab"""
        prefab_map = {
            "tree": "tree_oak",
            "grass": "grass_patch",
            "bush": "bush_generic"
        }
        return prefab_map.get(veg_type, "tree_generic")
    
    def _sample_vegetation_points(
        self,
        veg_area: VegetationArea,
        density_multiplier: float = 1.0
    ) -> List[tuple]:
        """Sample points within vegetation area based on density"""
        # Calculate area
        coords = veg_area.geometry
        if len(coords) < 3:
            return []
        
        # Get bounding box
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Estimate number of objects
        area_deg2 = (max_lat - min_lat) * (max_lon - min_lon)
        num_objects = int(area_deg2 * 1000000 * veg_area.density * density_multiplier)
        num_objects = min(num_objects, 1000)  # Cap at 1000 objects per area
        
        # Random sampling within bounds
        points = []
        for _ in range(num_objects):
            lat = np.random.uniform(min_lat, max_lat)
            lon = np.random.uniform(min_lon, max_lon)
            points.append((lat, lon))
        
        return points
    
    def _estimate_parking_capacity(self, boundary: List[List[float]]) -> int:
        """Estimate parking capacity from boundary"""
        # Calculate area
        if len(boundary) < 3:
            return 10
        
        # Simple polygon area calculation
        area = 0.0
        for i in range(len(boundary)):
            j = (i + 1) % len(boundary)
            area += boundary[i][0] * boundary[j][1]
            area -= boundary[j][0] * boundary[i][1]
        area = abs(area) / 2.0
        
        # Assume ~12.5 m² per parking space
        capacity = int(area / 12.5)
        return max(capacity, 5)
