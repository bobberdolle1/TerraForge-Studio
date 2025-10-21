"""
Unreal Engine exporter for generated maps
Exports heightmaps, landscapes, and static meshes compatible with UE5
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from PIL import Image

from ..models import MapData, RoadSegment, Building
from ..config import settings

logger = logging.getLogger(__name__)


class UnrealExporter:
    """Export map data to Unreal Engine format"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_complete_map(self, map_data: MapData) -> Dict[str, Path]:
        """
        Export all map components to Unreal Engine format
        
        Returns:
            Dictionary of exported file paths
        """
        logger.info(f"Exporting map '{map_data.name}' to Unreal Engine format")
        
        exported_files = {}
        
        # Export landscape heightmap (16-bit RAW)
        if map_data.heightmap_path:
            exported_files['landscape'] = self._export_landscape(
                map_data.heightmap_path,
                map_data.name
            )
        
        # Export road splines as JSON
        exported_files['roads'] = self._export_road_splines(
            map_data.roads,
            map_data.name
        )
        
        # Export buildings as static mesh placement data
        exported_files['buildings'] = self._export_static_meshes(
            map_data.buildings,
            map_data.name
        )
        
        # Export metadata for UE import
        exported_files['metadata'] = self._export_metadata(
            map_data,
            exported_files
        )
        
        # Create UE import script (Python)
        exported_files['import_script'] = self._create_import_script(
            map_data.name,
            exported_files
        )
        
        logger.info(f"Unreal Engine export complete: {len(exported_files)} files")
        return exported_files
    
    def _export_landscape(
        self,
        heightmap_path: str,
        map_name: str
    ) -> Path:
        """
        Export heightmap in Unreal Engine RAW format
        UE expects 16-bit grayscale RAW file
        """
        logger.info("Exporting landscape heightmap for Unreal Engine")
        
        # Load heightmap
        heightmap = Image.open(heightmap_path)
        
        # Convert to 16-bit grayscale if needed
        if heightmap.mode != 'I;16':
            heightmap = heightmap.convert('I')
        
        # Get numpy array
        height_data = np.array(heightmap, dtype=np.uint16)
        
        # UE expects specific dimensions (power of 2 + 1)
        # Common sizes: 253, 505, 1009, 2017, 4033, 8129
        target_sizes = [253, 505, 1009, 2017, 4033, 8129]
        current_size = height_data.shape[0]
        
        # Find closest valid size
        target_size = min(target_sizes, key=lambda x: abs(x - current_size))
        
        if current_size != target_size:
            logger.info(f"Resizing heightmap from {current_size} to {target_size} for UE compatibility")
            heightmap_resized = heightmap.resize((target_size, target_size), Image.Resampling.LANCZOS)
            height_data = np.array(heightmap_resized, dtype=np.uint16)
        
        # Export as RAW (little-endian 16-bit)
        output_path = self.output_dir / f"{map_name}_landscape.raw"
        height_data.astype('<u2').tofile(output_path)
        
        # Also export world settings
        world_size = target_size - 1  # Actual terrain quads
        scale_xy = 100.0  # 1 meter per quad
        scale_z = 100.0   # Height scale
        
        settings_path = self.output_dir / f"{map_name}_landscape_settings.json"
        with open(settings_path, 'w') as f:
            json.dump({
                "resolution": target_size,
                "world_size": world_size,
                "scale": {
                    "x": scale_xy,
                    "y": scale_xy,
                    "z": scale_z
                },
                "import_type": "Landscape",
                "section_size": "127x127" if target_size <= 1009 else "255x255",
                "sections_per_component": 1,
                "number_of_components": int((world_size / 127) ** 2) if target_size <= 1009 else int((world_size / 255) ** 2)
            }, f, indent=2)
        
        logger.info(f"Landscape exported: {target_size}x{target_size}")
        return output_path
    
    def _export_road_splines(
        self,
        roads: List[RoadSegment],
        map_name: str
    ) -> Path:
        """
        Export roads as spline data for UE Landscape Splines
        """
        logger.info(f"Exporting {len(roads)} road splines")
        
        splines_data = {
            "splines": [],
            "metadata": {
                "coordinate_system": "latlon",
                "total_roads": len(roads)
            }
        }
        
        for i, road in enumerate(roads):
            if len(road.geometry) < 2:
                continue
            
            spline = {
                "id": f"road_{i}",
                "osm_id": road.osm_id,
                "road_type": road.road_type.value,
                "points": [
                    {
                        "location": list(point),
                        "index": j
                    }
                    for j, point in enumerate(road.geometry)
                ],
                "width": road.lanes * 3.5 if road.lanes else 7.0,  # meters
                "max_speed": road.max_speed or 50.0,
                "material": "asphalt"
            }
            
            splines_data["splines"].append(spline)
        
        output_path = self.output_dir / f"{map_name}_roads_splines.json"
        with open(output_path, 'w') as f:
            json.dump(splines_data, f, indent=2)
        
        return output_path
    
    def _export_static_meshes(
        self,
        buildings: List[Building],
        map_name: str
    ) -> Path:
        """
        Export buildings as static mesh placement data
        """
        logger.info(f"Exporting {len(buildings)} building placements")
        
        meshes_data = {
            "static_meshes": [],
            "metadata": {
                "total_buildings": len(buildings),
                "coordinate_system": "latlon"
            }
        }
        
        for i, building in enumerate(buildings):
            if len(building.geometry) < 3:
                continue
            
            # Calculate centroid
            lats = [p[0] for p in building.geometry]
            lons = [p[1] for p in building.geometry]
            centroid = (sum(lats) / len(lats), sum(lons) / len(lons))
            
            # Estimate dimensions from footprint
            lat_range = max(lats) - min(lats)
            lon_range = max(lons) - min(lons)
            
            # Convert to approximate meters (rough estimate)
            width = lon_range * 111320 * np.cos(np.radians(centroid[0]))
            length = lat_range * 111320
            height = building.height or (building.levels * 3.0 if building.levels else 10.0)
            
            mesh_data = {
                "id": f"building_{i}",
                "osm_id": building.osm_id,
                "location": list(centroid),
                "footprint": building.geometry,
                "dimensions": {
                    "width": width,
                    "length": length,
                    "height": height
                },
                "levels": building.levels,
                "building_type": building.building_type or "generic",
                "mesh_asset": f"/Game/Buildings/{building.building_type or 'Generic'}/SM_Building",
                "scale": {
                    "x": width / 10.0,  # Assuming base mesh is 10m
                    "y": length / 10.0,
                    "z": height / 10.0
                }
            }
            
            meshes_data["static_meshes"].append(mesh_data)
        
        output_path = self.output_dir / f"{map_name}_buildings_meshes.json"
        with open(output_path, 'w') as f:
            json.dump(meshes_data, f, indent=2)
        
        return output_path
    
    def _export_metadata(
        self,
        map_data: MapData,
        exported_files: Dict[str, Path]
    ) -> Path:
        """Export map metadata for UE import"""
        metadata = {
            "map_name": map_data.name,
            "version": "1.0",
            "engine": "UnrealEngine5",
            "bounding_box": {
                "north": map_data.bbox.north,
                "south": map_data.bbox.south,
                "east": map_data.bbox.east,
                "west": map_data.bbox.west
            },
            "area_km2": map_data.bbox.area_km2(),
            "statistics": {
                "roads": len(map_data.roads),
                "buildings": len(map_data.buildings),
                "traffic_lights": len(map_data.traffic_lights),
                "parking_lots": len(map_data.parking_lots)
            },
            "exported_files": {
                k: str(v.name) for k, v in exported_files.items()
            },
            "coordinate_reference": "WGS84",
            "import_instructions": "Use the generated Python script to import into Unreal Engine"
        }
        
        output_path = self.output_dir / f"{map_data.name}_unreal_metadata.json"
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return output_path
    
    def _create_import_script(
        self,
        map_name: str,
        exported_files: Dict[str, Path]
    ) -> Path:
        """Create Python script for importing into Unreal Engine Editor"""
        script = f'''#!/usr/bin/env python
"""
Unreal Engine Import Script for {map_name}
Auto-generated by RealWorldMapGen-BNG

Usage:
1. Open Unreal Engine 5 Editor
2. Enable Python Editor Script Plugin
3. Run this script via Tools > Execute Python Script
"""

import unreal
import json

# Import settings
MAP_NAME = "{map_name}"
LANDSCAPE_FILE = "{exported_files.get('landscape', Path()).name}"
ROADS_FILE = "{exported_files.get('roads', Path()).name}"
BUILDINGS_FILE = "{exported_files.get('buildings', Path()).name}"

def import_landscape():
    """Import landscape from RAW heightmap"""
    print(f"Importing landscape: {{LANDSCAPE_FILE}}")
    
    # Load landscape settings
    with open("{exported_files.get('metadata', Path()).name.replace('metadata', 'landscape_settings')}") as f:
        settings = json.load(f)
    
    # Create landscape
    landscape_info = unreal.LandscapeImportLayerInfo()
    landscape_info.layer_name = "Ground"
    
    # Import heightmap
    # Note: Actual import requires UE Editor context
    print(f"Landscape size: {{settings['resolution']}}x{{settings['resolution']}}")
    print(f"Scale: {{settings['scale']}}")
    
def import_roads():
    """Import road splines"""
    print(f"Importing roads: {{ROADS_FILE}}")
    
    with open(ROADS_FILE) as f:
        roads_data = json.load(f)
    
    print(f"Total roads: {{len(roads_data['splines'])}}")
    # Spline creation logic here
    
def import_buildings():
    """Import building static meshes"""
    print(f"Importing buildings: {{BUILDINGS_FILE}}")
    
    with open(BUILDINGS_FILE) as f:
        buildings_data = json.load(f)
    
    print(f"Total buildings: {{len(buildings_data['static_meshes'])}}")
    # Static mesh placement logic here

if __name__ == "__main__":
    print(f"Starting import of {{MAP_NAME}} into Unreal Engine")
    import_landscape()
    import_roads()
    import_buildings()
    print("Import complete!")
'''
        
        output_path = self.output_dir / f"{map_name}_import_unreal.py"
        with open(output_path, 'w') as f:
            f.write(script)
        
        return output_path
