"""
Incremental map update system
Load existing maps, detect changes, update only modified parts
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from ..models import MapData, BoundingBox
from ..config import settings

logger = logging.getLogger(__name__)


class IncrementalUpdateManager:
    """Manage incremental updates to existing maps"""
    
    def __init__(self):
        self.index_file = settings.output_dir / "map_index.json"
        self.map_index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load map index with metadata"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load map index: {e}")
        return {"maps": {}, "last_updated": None}
    
    def _save_index(self):
        """Save map index"""
        self.map_index["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.map_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save map index: {e}")
    
    def register_map(
        self,
        map_name: str,
        bbox: BoundingBox,
        file_hashes: Dict[str, str],
        metadata: Dict[str, Any]
    ):
        """Register a newly generated map"""
        self.map_index["maps"][map_name] = {
            "name": map_name,
            "bbox": {
                "north": bbox.north,
                "south": bbox.south,
                "east": bbox.east,
                "west": bbox.west
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1,
            "file_hashes": file_hashes,
            "metadata": metadata
        }
        self._save_index()
    
    def find_existing_map(
        self,
        bbox: BoundingBox
    ) -> Optional[Dict[str, Any]]:
        """
        Find existing map that overlaps with bounding box
        
        Args:
            bbox: Bounding box to check
            
        Returns:
            Existing map info or None
        """
        for map_name, map_info in self.map_index["maps"].items():
            existing_bbox = map_info["bbox"]
            
            # Check for overlap
            if self._bboxes_overlap(bbox, existing_bbox):
                logger.info(f"Found overlapping map: {map_name}")
                return map_info
        
        return None
    
    def _bboxes_overlap(
        self,
        bbox1: BoundingBox,
        bbox2: Dict[str, float]
    ) -> bool:
        """Check if two bounding boxes overlap"""
        return not (
            bbox1.east < bbox2["west"] or
            bbox1.west > bbox2["east"] or
            bbox1.north < bbox2["south"] or
            bbox1.south > bbox2["north"]
        )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {file_path}: {e}")
            return ""
    
    async def detect_changes(
        self,
        map_name: str,
        new_osm_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect changes between existing map and new OSM data
        
        Args:
            map_name: Name of existing map
            new_osm_data: Newly fetched OSM data
            
        Returns:
            Dictionary of detected changes
        """
        logger.info(f"Detecting changes for map: {map_name}")
        
        map_info = self.map_index["maps"].get(map_name)
        if not map_info:
            return {"has_changes": False, "error": "Map not found"}
        
        map_dir = settings.output_dir / map_name
        
        # Load existing map data
        existing_data = await self._load_existing_data(map_dir)
        if not existing_data:
            return {"has_changes": True, "reason": "Cannot load existing data"}
        
        changes = {
            "has_changes": False,
            "roads": {"added": [], "removed": [], "modified": []},
            "buildings": {"added": [], "removed": [], "modified": []},
            "traffic_lights": {"added": [], "removed": []},
            "parking_lots": {"added": [], "removed": []},
            "vegetation": {"added": [], "removed": []}
        }
        
        # Compare roads
        changes["roads"] = self._compare_roads(
            existing_data.get("roads", []),
            new_osm_data.get("roads", [])
        )
        
        # Compare buildings
        changes["buildings"] = self._compare_buildings(
            existing_data.get("buildings", []),
            new_osm_data.get("buildings", [])
        )
        
        # Compare other elements
        changes["traffic_lights"] = self._compare_simple_elements(
            existing_data.get("traffic_lights", []),
            new_osm_data.get("traffic_lights", [])
        )
        
        # Determine if there are significant changes
        total_changes = sum([
            len(changes["roads"]["added"]),
            len(changes["roads"]["removed"]),
            len(changes["roads"]["modified"]),
            len(changes["buildings"]["added"]),
            len(changes["buildings"]["removed"]),
            len(changes["buildings"]["modified"])
        ])
        
        changes["has_changes"] = total_changes > 0
        changes["total_changes"] = total_changes
        
        logger.info(f"Detected {total_changes} changes")
        return changes
    
    async def _load_existing_data(self, map_dir: Path) -> Optional[Dict[str, Any]]:
        """Load existing map data files"""
        try:
            data = {}
            
            # Load roads
            roads_file = map_dir / "roads.json"
            if roads_file.exists():
                with open(roads_file, 'r') as f:
                    data["roads"] = json.load(f).get("roads", [])
            
            # Load buildings
            objects_file = map_dir / "objects.json"
            if objects_file.exists():
                with open(objects_file, 'r') as f:
                    obj_data = json.load(f)
                    data["buildings"] = obj_data.get("buildings", [])
                    data["vegetation"] = obj_data.get("vegetation", [])
            
            # Load traffic
            traffic_file = map_dir / "traffic.json"
            if traffic_file.exists():
                with open(traffic_file, 'r') as f:
                    traffic_data = json.load(f)
                    data["traffic_lights"] = traffic_data.get("traffic_lights", [])
                    data["parking_lots"] = traffic_data.get("parking_lots", [])
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load existing data: {e}")
            return None
    
    def _compare_roads(
        self,
        existing: List[Dict],
        new: List[Dict]
    ) -> Dict[str, List]:
        """Compare road datasets"""
        existing_ids = {r.get("osm_id"): r for r in existing}
        new_ids = {r.get("osm_id"): r for r in new}
        
        added = [r for rid, r in new_ids.items() if rid not in existing_ids]
        removed = [r for rid, r in existing_ids.items() if rid not in new_ids]
        modified = []
        
        # Check for modifications
        for rid in set(existing_ids.keys()) & set(new_ids.keys()):
            if existing_ids[rid].get("geometry") != new_ids[rid].get("geometry"):
                modified.append({
                    "osm_id": rid,
                    "old": existing_ids[rid],
                    "new": new_ids[rid]
                })
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified
        }
    
    def _compare_buildings(
        self,
        existing: List[Dict],
        new: List[Dict]
    ) -> Dict[str, List]:
        """Compare building datasets"""
        existing_ids = {b.get("osm_id"): b for b in existing}
        new_ids = {b.get("osm_id"): b for b in new}
        
        added = [b for bid, b in new_ids.items() if bid not in existing_ids]
        removed = [b for bid, b in existing_ids.items() if bid not in new_ids]
        modified = []
        
        # Check for modifications
        for bid in set(existing_ids.keys()) & set(new_ids.keys()):
            old_b = existing_ids[bid]
            new_b = new_ids[bid]
            
            if (old_b.get("geometry") != new_b.get("geometry") or
                old_b.get("height") != new_b.get("height") or
                old_b.get("levels") != new_b.get("levels")):
                modified.append({
                    "osm_id": bid,
                    "old": old_b,
                    "new": new_b
                })
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified
        }
    
    def _compare_simple_elements(
        self,
        existing: List[Dict],
        new: List[Dict]
    ) -> Dict[str, List]:
        """Compare simple element lists (traffic lights, parking)"""
        existing_ids = {e.get("osm_id") for e in existing}
        new_ids = {e.get("osm_id") for e in new}
        
        added_ids = new_ids - existing_ids
        removed_ids = existing_ids - new_ids
        
        return {
            "added": [e for e in new if e.get("osm_id") in added_ids],
            "removed": [e for e in existing if e.get("osm_id") in removed_ids]
        }
    
    async def apply_incremental_update(
        self,
        map_name: str,
        changes: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> bool:
        """
        Apply incremental changes to existing map
        
        Args:
            map_name: Map to update
            changes: Detected changes
            new_data: New map data
            
        Returns:
            True if successful
        """
        if not changes.get("has_changes"):
            logger.info("No changes to apply")
            return True
        
        logger.info(f"Applying incremental update to {map_name}")
        
        map_dir = settings.output_dir / map_name
        
        try:
            # Update roads
            if changes["roads"]["added"] or changes["roads"]["modified"] or changes["roads"]["removed"]:
                await self._update_roads(map_dir, changes["roads"], new_data.get("roads", []))
            
            # Update buildings
            if changes["buildings"]["added"] or changes["buildings"]["modified"] or changes["buildings"]["removed"]:
                await self._update_buildings(map_dir, changes["buildings"], new_data.get("buildings", []))
            
            # Update version
            map_info = self.map_index["maps"][map_name]
            map_info["version"] += 1
            map_info["updated_at"] = datetime.now().isoformat()
            self._save_index()
            
            logger.info(f"Incremental update complete (v{map_info['version']})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply incremental update: {e}")
            return False
    
    async def _update_roads(
        self,
        map_dir: Path,
        road_changes: Dict[str, List],
        all_roads: List[Dict]
    ):
        """Update roads file with changes"""
        roads_file = map_dir / "roads.json"
        
        # Save updated roads
        with open(roads_file, 'w') as f:
            json.dump({"roads": all_roads}, f, indent=2)
        
        logger.info(f"Updated roads: +{len(road_changes['added'])} -{len(road_changes['removed'])} ~{len(road_changes['modified'])}")
    
    async def _update_buildings(
        self,
        map_dir: Path,
        building_changes: Dict[str, List],
        all_buildings: List[Dict]
    ):
        """Update buildings file with changes"""
        objects_file = map_dir / "objects.json"
        
        # Load existing objects to preserve vegetation
        existing_data = {}
        if objects_file.exists():
            with open(objects_file, 'r') as f:
                existing_data = json.load(f)
        
        # Update with new buildings
        existing_data["buildings"] = all_buildings
        
        with open(objects_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        logger.info(f"Updated buildings: +{len(building_changes['added'])} -{len(building_changes['removed'])} ~{len(building_changes['modified'])}")
