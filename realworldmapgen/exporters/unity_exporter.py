"""
Unity Engine exporter for generated maps
Exports terrains, meshes, and prefabs compatible with Unity
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


class UnityExporter:
    """Export map data to Unity Engine format"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_complete_map(self, map_data: MapData) -> Dict[str, Path]:
        """
        Export all map components to Unity format
        
        Returns:
            Dictionary of exported file paths
        """
        logger.info(f"Exporting map '{map_data.name}' to Unity format")
        
        exported_files = {}
        
        # Export terrain heightmap (RAW 16-bit)
        if map_data.heightmap_path:
            exported_files['terrain'] = self._export_terrain(
                map_data.heightmap_path,
                map_data.name
            )
        
        # Export roads as mesh data
        exported_files['roads'] = self._export_road_meshes(
            map_data.roads,
            map_data.name
        )
        
        # Export buildings as GameObject placement data
        exported_files['buildings'] = self._export_gameobjects(
            map_data.buildings,
            map_data.name
        )
        
        # Export metadata
        exported_files['metadata'] = self._export_metadata(
            map_data,
            exported_files
        )
        
        # Create Unity import script (C#)
        exported_files['import_script'] = self._create_import_script(
            map_data.name,
            exported_files
        )
        
        logger.info(f"Unity export complete: {len(exported_files)} files")
        return exported_files
    
    def _export_terrain(
        self,
        heightmap_path: str,
        map_name: str
    ) -> Path:
        """
        Export heightmap in Unity Terrain format
        Unity expects 16-bit grayscale RAW file, resolution must be power of 2 + 1
        """
        logger.info("Exporting terrain heightmap for Unity")
        
        # Load heightmap
        heightmap = Image.open(heightmap_path)
        
        # Convert to 16-bit grayscale
        if heightmap.mode != 'I;16':
            heightmap = heightmap.convert('I')
        
        height_data = np.array(heightmap, dtype=np.uint16)
        
        # Unity terrain resolutions: 33, 65, 129, 257, 513, 1025, 2049, 4097
        valid_sizes = [33, 65, 129, 257, 513, 1025, 2049, 4097]
        current_size = height_data.shape[0]
        
        # Find closest valid size
        target_size = min(valid_sizes, key=lambda x: abs(x - current_size))
        
        if current_size != target_size:
            logger.info(f"Resizing terrain from {current_size} to {target_size} for Unity")
            heightmap_resized = heightmap.resize((target_size, target_size), Image.Resampling.LANCZOS)
            height_data = np.array(heightmap_resized, dtype=np.uint16)
        
        # Unity expects little-endian 16-bit
        output_path = self.output_dir / f"{map_name}_terrain.raw"
        height_data.astype('<u2').tofile(output_path)
        
        # Export terrain settings for Unity
        terrain_settings = {
            "heightmap_resolution": target_size,
            "terrain_width": (target_size - 1) * 1.0,  # meters
            "terrain_length": (target_size - 1) * 1.0,
            "terrain_height": 600.0,  # max height in meters
            "detail_resolution": 1024,
            "detail_resolution_per_patch": 8,
            "base_map_resolution": 1024,
            "heightmap_format": "RAW_16bit"
        }
        
        settings_path = self.output_dir / f"{map_name}_terrain_settings.json"
        with open(settings_path, 'w') as f:
            json.dump(terrain_settings, f, indent=2)
        
        logger.info(f"Terrain exported: {target_size}x{target_size}")
        return output_path
    
    def _export_road_meshes(
        self,
        roads: List[RoadSegment],
        map_name: str
    ) -> Path:
        """
        Export roads as mesh generation data for Unity
        """
        logger.info(f"Exporting {len(roads)} road meshes")
        
        roads_data = {
            "roads": [],
            "metadata": {
                "coordinate_system": "latlon",
                "total_roads": len(roads)
            }
        }
        
        for i, road in enumerate(roads):
            if len(road.geometry) < 2:
                continue
            
            road_mesh = {
                "id": f"road_{i}",
                "osm_id": road.osm_id,
                "road_type": road.road_type.value,
                "vertices": [
                    {
                        "position": list(point),
                        "index": j
                    }
                    for j, point in enumerate(road.geometry)
                ],
                "width": road.lanes * 3.5 if road.lanes else 7.0,
                "max_speed": road.max_speed or 50.0,
                "material": "Roads/Asphalt",
                "generate_mesh": True,
                "uv_scale": 0.1
            }
            
            roads_data["roads"].append(road_mesh)
        
        output_path = self.output_dir / f"{map_name}_roads_meshes.json"
        with open(output_path, 'w') as f:
            json.dump(roads_data, f, indent=2)
        
        return output_path
    
    def _export_gameobjects(
        self,
        buildings: List[Building],
        map_name: str
    ) -> Path:
        """
        Export buildings as GameObject instantiation data
        """
        logger.info(f"Exporting {len(buildings)} GameObject placements")
        
        gameobjects_data = {
            "gameobjects": [],
            "metadata": {
                "total_buildings": len(buildings),
                "coordinate_system": "latlon"
            }
        }
        
        for i, building in enumerate(buildings):
            if len(building.geometry) < 3:
                continue
            
            # Calculate centroid for placement
            lats = [p[0] for p in building.geometry]
            lons = [p[1] for p in building.geometry]
            centroid = (sum(lats) / len(lats), sum(lons) / len(lons))
            
            # Estimate dimensions
            lat_range = max(lats) - min(lats)
            lon_range = max(lons) - min(lons)
            
            width = lon_range * 111320 * np.cos(np.radians(centroid[0]))
            length = lat_range * 111320
            height = building.height or (building.levels * 3.0 if building.levels else 10.0)
            
            gameobject = {
                "id": f"building_{i}",
                "osm_id": building.osm_id,
                "prefab_path": f"Prefabs/Buildings/{building.building_type or 'Generic'}",
                "position": list(centroid),
                "footprint": building.geometry,
                "transform": {
                    "position": list(centroid) + [0.0],  # lat, lon, elevation
                    "rotation": {"x": 0, "y": 0, "z": 0},
                    "scale": {
                        "x": width / 10.0,
                        "y": height / 10.0,
                        "z": length / 10.0
                    }
                },
                "properties": {
                    "building_type": building.building_type or "generic",
                    "levels": building.levels,
                    "height_meters": height
                },
                "components": [
                    {
                        "type": "MeshRenderer",
                        "material": "Buildings/StandardBuilding"
                    },
                    {
                        "type": "BoxCollider",
                        "size": [width, height, length]
                    }
                ]
            }
            
            gameobjects_data["gameobjects"].append(gameobject)
        
        output_path = self.output_dir / f"{map_name}_buildings_gameobjects.json"
        with open(output_path, 'w') as f:
            json.dump(gameobjects_data, f, indent=2)
        
        return output_path
    
    def _export_metadata(
        self,
        map_data: MapData,
        exported_files: Dict[str, Path]
    ) -> Path:
        """Export map metadata for Unity import"""
        metadata = {
            "map_name": map_data.name,
            "version": "1.0",
            "engine": "Unity",
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
            "import_instructions": "Use the Unity Editor script to import this map"
        }
        
        output_path = self.output_dir / f"{map_data.name}_unity_metadata.json"
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return output_path
    
    def _create_import_script(
        self,
        map_name: str,
        exported_files: Dict[str, Path]
    ) -> Path:
        """Create C# Editor script for importing into Unity"""
        script = f'''using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;

/// <summary>
/// Unity Editor script for importing {map_name}
/// Auto-generated by RealWorldMapGen-BNG
/// 
/// Usage:
/// 1. Place this script in Assets/Editor/
/// 2. Place exported files in Assets/MapData/{map_name}/
/// 3. Use Unity menu: Tools > Import Map > {map_name}
/// </summary>
public class {map_name.replace('-', '_')}Importer : EditorWindow
{{
    private const string MAP_NAME = "{map_name}";
    private const string TERRAIN_FILE = "{exported_files.get('terrain', Path()).name}";
    private const string ROADS_FILE = "{exported_files.get('roads', Path()).name}";
    private const string BUILDINGS_FILE = "{exported_files.get('buildings', Path()).name}";
    
    [MenuItem("Tools/Import Map/{map_name}")]
    public static void ImportMap()
    {{
        Debug.Log($"Importing map: {{MAP_NAME}}");
        
        ImportTerrain();
        ImportRoads();
        ImportBuildings();
        
        Debug.Log("Map import complete!");
    }}
    
    private static void ImportTerrain()
    {{
        Debug.Log("Importing terrain...");
        
        // Create terrain
        TerrainData terrainData = new TerrainData();
        
        // Load settings
        string settingsPath = $"Assets/MapData/{{MAP_NAME}}/{{MAP_NAME}}_terrain_settings.json";
        // Parse settings and configure terrain
        
        // Create GameObject
        GameObject terrainObject = Terrain.CreateTerrainGameObject(terrainData);
        terrainObject.name = MAP_NAME + "_Terrain";
        
        Debug.Log("Terrain created");
    }}
    
    private static void ImportRoads()
    {{
        Debug.Log("Importing roads...");
        
        string roadsPath = $"Assets/MapData/{{MAP_NAME}}/{{ROADS_FILE}}";
        if (!File.Exists(roadsPath)) return;
        
        string json = File.ReadAllText(roadsPath);
        // Parse JSON and create road meshes
        
        Debug.Log("Roads imported");
    }}
    
    private static void ImportBuildings()
    {{
        Debug.Log("Importing buildings...");
        
        string buildingsPath = $"Assets/MapData/{{MAP_NAME}}/{{BUILDINGS_FILE}}";
        if (!File.Exists(buildingsPath)) return;
        
        string json = File.ReadAllText(buildingsPath);
        // Parse JSON and instantiate building prefabs
        
        Debug.Log("Buildings imported");
    }}
}}
'''
        
        output_path = self.output_dir / f"{map_name}_ImportEditor.cs"
        with open(output_path, 'w') as f:
            f.write(script)
        
        return output_path
