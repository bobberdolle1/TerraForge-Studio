"""
Prefab management system for buildings and objects
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PrefabManager:
    """Manage prefabs for buildings and objects"""
    
    def __init__(self, prefabs_dir: Optional[Path] = None):
        self.prefabs_dir = prefabs_dir or Path("prefabs")
        self.prefabs_dir.mkdir(parents=True, exist_ok=True)
        
        # Built-in prefab mappings
        self.building_prefabs = {
            "residential": "residential_building_01",
            "commercial": "commercial_building_01",
            "industrial": "industrial_building_01",
            "office": "office_building_01",
            "house": "residential_house_01",
            "apartment": "apartment_building_01",
            "generic": "generic_building_01"
        }
        
        self.vegetation_prefabs = {
            "tree": "tree_oak_01",
            "grass": "grass_patch_01",
            "bush": "bush_generic_01",
            "forest": "forest_pine_01"
        }
    
    def get_building_prefab(
        self,
        building_type: str,
        height: Optional[float] = None
    ) -> str:
        """
        Get appropriate building prefab based on type and height
        
        Args:
            building_type: Type of building
            height: Building height in meters
            
        Returns:
            Prefab identifier
        """
        # Normalize building type
        building_type = building_type.lower() if building_type else "generic"
        
        # Select base prefab
        prefab = self.building_prefabs.get(building_type, "generic_building_01")
        
        # Modify based on height if provided
        if height:
            if height > 50:
                prefab += "_tall"
            elif height > 20:
                prefab += "_medium"
            else:
                prefab += "_low"
        
        return prefab
    
    def get_vegetation_prefab(self, vegetation_type: str) -> str:
        """
        Get vegetation prefab based on type
        
        Args:
            vegetation_type: Type of vegetation
            
        Returns:
            Prefab identifier
        """
        return self.vegetation_prefabs.get(
            vegetation_type.lower(),
            "tree_generic_01"
        )
    
    def load_custom_prefabs(self, prefabs_file: Path) -> bool:
        """
        Load custom prefab mappings from JSON file
        
        Args:
            prefabs_file: Path to prefabs JSON file
            
        Returns:
            True if successful
        """
        try:
            with open(prefabs_file, 'r') as f:
                custom_prefabs = json.load(f)
            
            # Update mappings
            if "buildings" in custom_prefabs:
                self.building_prefabs.update(custom_prefabs["buildings"])
            
            if "vegetation" in custom_prefabs:
                self.vegetation_prefabs.update(custom_prefabs["vegetation"])
            
            logger.info(f"Loaded custom prefabs from {prefabs_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load custom prefabs: {e}")
            return False
    
    def export_prefab_list(self, output_path: Path) -> Path:
        """
        Export list of available prefabs
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        prefab_list = {
            "buildings": self.building_prefabs,
            "vegetation": self.vegetation_prefabs
        }
        
        with open(output_path, 'w') as f:
            json.dump(prefab_list, f, indent=2)
        
        logger.info(f"Prefab list exported to {output_path}")
        return output_path
    
    def get_all_prefabs(self) -> Dict[str, Dict[str, str]]:
        """Get all available prefabs"""
        return {
            "buildings": self.building_prefabs.copy(),
            "vegetation": self.vegetation_prefabs.copy()
        }
