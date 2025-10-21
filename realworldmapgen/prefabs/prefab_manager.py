"""
Custom prefab management system
Supports importing user 3D models for map generation
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

from ..config import settings

logger = logging.getLogger(__name__)


class PrefabManager:
    """Manage custom 3D model prefabs for map generation"""
    
    def __init__(self):
        self.prefab_dir = settings.cache_dir / "prefabs"
        self.prefab_dir.mkdir(parents=True, exist_ok=True)
        
        self.prefab_registry_path = self.prefab_dir / "registry.json"
        self.prefab_registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load prefab registry from disk"""
        if self.prefab_registry_path.exists():
            try:
                with open(self.prefab_registry_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load prefab registry: {e}")
                return {"prefabs": {}, "categories": {}}
        return {"prefabs": {}, "categories": {}}
    
    def _save_registry(self):
        """Save prefab registry to disk"""
        try:
            with open(self.prefab_registry_path, 'w') as f:
                json.dump(self.prefab_registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save prefab registry: {e}")
    
    def import_prefab(
        self,
        file_path: Path,
        prefab_id: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Import a custom prefab model
        
        Args:
            file_path: Path to model file (.jbeam, .fbx, .obj, .dae, etc.)
            prefab_id: Unique identifier for this prefab
            category: Category (building, vegetation, vehicle, decoration, etc.)
            metadata: Additional metadata (dimensions, tags, OSM mapping)
            
        Returns:
            True if successful
        """
        if not file_path.exists():
            logger.error(f"Prefab file not found: {file_path}")
            return False
        
        # Supported formats
        supported_formats = {
            '.jbeam': 'beamng',
            '.fbx': 'universal',
            '.obj': 'universal',
            '.dae': 'universal',
            '.gltf': 'universal',
            '.glb': 'universal',
            '.blend': 'blender'
        }
        
        file_ext = file_path.suffix.lower()
        if file_ext not in supported_formats:
            logger.error(f"Unsupported prefab format: {file_ext}")
            return False
        
        # Create prefab directory
        prefab_storage = self.prefab_dir / category / prefab_id
        prefab_storage.mkdir(parents=True, exist_ok=True)
        
        # Copy model file
        dest_path = prefab_storage / file_path.name
        shutil.copy2(file_path, dest_path)
        
        # Register prefab
        self.prefab_registry["prefabs"][prefab_id] = {
            "id": prefab_id,
            "category": category,
            "file_path": str(dest_path.relative_to(self.prefab_dir)),
            "format": supported_formats[file_ext],
            "original_name": file_path.name,
            "metadata": metadata or {},
            "tags": metadata.get("tags", []) if metadata else [],
            "osm_mapping": metadata.get("osm_mapping", {}) if metadata else {}
        }
        
        # Update category index
        if category not in self.prefab_registry["categories"]:
            self.prefab_registry["categories"][category] = []
        if prefab_id not in self.prefab_registry["categories"][category]:
            self.prefab_registry["categories"][category].append(prefab_id)
        
        self._save_registry()
        logger.info(f"Imported prefab: {prefab_id} ({category})")
        return True
    
    def get_prefab(self, prefab_id: str) -> Optional[Dict[str, Any]]:
        """Get prefab information by ID"""
        return self.prefab_registry["prefabs"].get(prefab_id)
    
    def get_prefabs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all prefabs in a category"""
        prefab_ids = self.prefab_registry["categories"].get(category, [])
        return [
            self.prefab_registry["prefabs"][pid]
            for pid in prefab_ids
            if pid in self.prefab_registry["prefabs"]
        ]
    
    def get_prefabs_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Get prefabs matching any of the given tags"""
        results = []
        for prefab_id, prefab_data in self.prefab_registry["prefabs"].items():
            prefab_tags = set(prefab_data.get("tags", []))
            if prefab_tags.intersection(tags):
                results.append(prefab_data)
        return results
    
    def get_prefab_for_osm(
        self,
        osm_tags: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Find best matching prefab for OSM tags
        
        Args:
            osm_tags: OSM tags (e.g., {"building": "residential", "height": "10"})
            
        Returns:
            Matching prefab or None
        """
        best_match = None
        best_score = 0
        
        for prefab_id, prefab_data in self.prefab_registry["prefabs"].items():
            osm_mapping = prefab_data.get("osm_mapping", {})
            if not osm_mapping:
                continue
            
            # Calculate match score
            score = 0
            for key, value in osm_tags.items():
                if key in osm_mapping:
                    if isinstance(osm_mapping[key], list):
                        if value in osm_mapping[key]:
                            score += 2
                    elif osm_mapping[key] == value:
                        score += 2
                    elif osm_mapping[key] == "*":  # wildcard
                        score += 1
            
            if score > best_score:
                best_score = score
                best_match = prefab_data
        
        return best_match
    
    def list_all_prefabs(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all prefabs grouped by category"""
        result = {}
        for category, prefab_ids in self.prefab_registry["categories"].items():
            result[category] = [
                self.prefab_registry["prefabs"][pid]
                for pid in prefab_ids
                if pid in self.prefab_registry["prefabs"]
            ]
        return result
    
    def delete_prefab(self, prefab_id: str) -> bool:
        """Delete a prefab and its files"""
        prefab = self.get_prefab(prefab_id)
        if not prefab:
            return False
        
        # Delete files
        try:
            file_path = self.prefab_dir / prefab["file_path"]
            if file_path.exists():
                # Delete parent directory if it only contains this file
                parent = file_path.parent
                file_path.unlink()
                if not any(parent.iterdir()):
                    parent.rmdir()
        except Exception as e:
            logger.error(f"Failed to delete prefab files: {e}")
        
        # Remove from registry
        category = prefab["category"]
        del self.prefab_registry["prefabs"][prefab_id]
        
        if category in self.prefab_registry["categories"]:
            self.prefab_registry["categories"][category].remove(prefab_id)
            if not self.prefab_registry["categories"][category]:
                del self.prefab_registry["categories"][category]
        
        self._save_registry()
        logger.info(f"Deleted prefab: {prefab_id}")
        return True
    
    def import_prefab_pack(
        self,
        pack_dir: Path
    ) -> Dict[str, Any]:
        """
        Import multiple prefabs from a directory structure
        
        Expected structure:
        pack_dir/
          manifest.json
          buildings/
            model1.fbx
            model2.obj
          vegetation/
            tree1.fbx
          
        Returns:
            Import results summary
        """
        manifest_path = pack_dir / "manifest.json"
        if not manifest_path.exists():
            logger.error("No manifest.json found in prefab pack")
            return {"success": False, "error": "Missing manifest.json"}
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            return {"success": False, "error": str(e)}
        
        results = {
            "success": True,
            "imported": [],
            "failed": []
        }
        
        for prefab_def in manifest.get("prefabs", []):
            prefab_id = prefab_def["id"]
            category = prefab_def["category"]
            file_name = prefab_def["file"]
            metadata = prefab_def.get("metadata", {})
            
            file_path = pack_dir / category / file_name
            
            if self.import_prefab(file_path, prefab_id, category, metadata):
                results["imported"].append(prefab_id)
            else:
                results["failed"].append(prefab_id)
        
        logger.info(f"Imported {len(results['imported'])} prefabs from pack")
        return results
    
    def export_prefab_info(self) -> Dict[str, Any]:
        """Export prefab registry as JSON for API"""
        return {
            "total_prefabs": len(self.prefab_registry["prefabs"]),
            "categories": {
                cat: len(pids)
                for cat, pids in self.prefab_registry["categories"].items()
            },
            "prefabs": self.prefab_registry["prefabs"]
        }
