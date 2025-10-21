"""
Incremental update manager for existing maps
"""

import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ..models import MapData, BoundingBox
from ..config import settings

logger = logging.getLogger(__name__)


class UpdateManager:
    """Manage incremental updates to existing maps"""
    
    def __init__(self):
        self.output_dir = settings.output_dir
    
    def check_map_exists(self, map_name: str) -> bool:
        """Check if a map already exists"""
        map_dir = self.output_dir / map_name
        return map_dir.exists() and (map_dir / "info.json").exists()
    
    def load_existing_map(self, map_name: str) -> Optional[MapData]:
        """Load existing map data"""
        map_dir = self.output_dir / map_name
        info_file = map_dir / "info.json"
        
        if not info_file.exists():
            logger.warning(f"Map {map_name} does not exist")
            return None
        
        try:
            with open(info_file, 'r') as f:
                info = json.load(f)
            
            # Reconstruct MapData from saved info
            bbox = BoundingBox(
                north=info['bbox']['north'],
                south=info['bbox']['south'],
                east=info['bbox']['east'],
                west=info['bbox']['west']
            )
            
            map_data = MapData(
                name=map_name,
                bbox=bbox
            )
            
            logger.info(f"Loaded existing map: {map_name}")
            return map_data
            
        except Exception as e:
            logger.error(f"Failed to load existing map: {e}")
            return None
    
    def create_backup(self, map_name: str) -> Optional[Path]:
        """Create a backup of existing map before update"""
        import shutil
        from datetime import datetime
        
        map_dir = self.output_dir / map_name
        
        if not map_dir.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.output_dir / f"{map_name}_backup_{timestamp}"
        
        try:
            shutil.copytree(map_dir, backup_dir)
            logger.info(f"Created backup: {backup_dir}")
            return backup_dir
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def merge_updates(
        self,
        existing: MapData,
        updates: MapData
    ) -> MapData:
        """
        Merge updates into existing map data
        
        Args:
            existing: Existing map data
            updates: New updates to merge
            
        Returns:
            Merged MapData
        """
        # Start with existing data
        merged = existing
        
        # Update roads if new roads are provided
        if updates.roads:
            # Simple replacement for now
            # In production, you'd want to merge intelligently
            merged.roads = updates.roads
            logger.info(f"Updated {len(updates.roads)} roads")
        
        # Update buildings
        if updates.buildings:
            merged.buildings = updates.buildings
            logger.info(f"Updated {len(updates.buildings)} buildings")
        
        # Update traffic infrastructure
        if updates.traffic_lights:
            merged.traffic_lights = updates.traffic_lights
        
        if updates.parking_lots:
            merged.parking_lots = updates.parking_lots
        
        # Update vegetation
        if updates.vegetation:
            merged.vegetation = updates.vegetation
        
        # Update AI analysis if provided
        if updates.ai_analysis:
            merged.ai_analysis = updates.ai_analysis
        
        # Update metadata
        merged.metadata['last_updated'] = datetime.now().isoformat()
        merged.metadata['update_count'] = merged.metadata.get('update_count', 0) + 1
        
        return merged
    
    def get_update_history(self, map_name: str) -> list:
        """Get update history for a map"""
        map_dir = self.output_dir / map_name
        history_file = map_dir / "update_history.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load update history: {e}")
            return []
    
    def add_to_history(
        self,
        map_name: str,
        update_info: Dict[str, Any]
    ):
        """Add an entry to update history"""
        map_dir = self.output_dir / map_name
        history_file = map_dir / "update_history.json"
        
        history = self.get_update_history(map_name)
        
        update_entry = {
            'timestamp': datetime.now().isoformat(),
            **update_info
        }
        
        history.append(update_entry)
        
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            logger.info(f"Added update to history: {map_name}")
        except Exception as e:
            logger.error(f"Failed to save update history: {e}")
