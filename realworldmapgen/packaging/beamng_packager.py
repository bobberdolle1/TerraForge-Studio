"""
BeamNG.drive mod packaging system
"""

import logging
import zipfile
from pathlib import Path
from typing import Optional
import shutil

logger = logging.getLogger(__name__)


class BeamNGPackager:
    """Package BeamNG.drive maps into installable mod archives"""
    
    def __init__(self):
        pass
    
    def create_mod_package(
        self,
        map_dir: Path,
        map_name: str,
        output_dir: Path
    ) -> Path:
        """
        Create a .zip mod package for BeamNG.drive
        
        Args:
            map_dir: Directory containing map files
            map_name: Name of the map
            output_dir: Output directory for the zip file
            
        Returns:
            Path to created zip file
        """
        logger.info(f"Creating BeamNG.drive mod package for '{map_name}'")
        
        if not map_dir.exists():
            raise FileNotFoundError(f"Map directory not found: {map_dir}")
        
        # Create zip file
        zip_path = output_dir / f"{map_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from map directory
            for file_path in map_dir.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path for archive
                    arcname = f"levels/{map_name}/{file_path.relative_to(map_dir)}"
                    zipf.write(file_path, arcname)
                    logger.debug(f"Added to zip: {arcname}")
            
            # Create mod info file
            mod_info = self._create_mod_info(map_name)
            zipf.writestr("mod.json", mod_info)
        
        logger.info(f"Mod package created: {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")
        return zip_path
    
    def _create_mod_info(self, map_name: str) -> str:
        """Create mod.json content for BeamNG.drive"""
        import json
        
        mod_info = {
            "name": map_name,
            "version": "1.0.0",
            "author": "RealWorldMapGen-BNG",
            "description": f"Real-world map '{map_name}' generated from OpenStreetMap data",
            "gameVersion": "0.31",
            "type": "level",
            "files": {
                "levels": [map_name]
            }
        }
        
        return json.dumps(mod_info, indent=2)
    
    def validate_map_structure(self, map_dir: Path) -> bool:
        """
        Validate that map directory has required files
        
        Args:
            map_dir: Map directory to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_files = [
            "info.json",
            "main.level.json"
        ]
        
        for filename in required_files:
            if not (map_dir / filename).exists():
                logger.warning(f"Missing required file: {filename}")
                return False
        
        return True
    
    def create_preview_image(
        self,
        map_dir: Path,
        heightmap_path: Path
    ) -> Optional[Path]:
        """
        Create a preview image for the map
        
        Args:
            map_dir: Map directory
            heightmap_path: Path to heightmap
            
        Returns:
            Path to preview image
        """
        try:
            from PIL import Image
            
            # Load heightmap
            img = Image.open(heightmap_path)
            
            # Create thumbnail
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
            
            # Save as preview
            preview_path = map_dir / "preview.png"
            img.save(preview_path)
            
            logger.info(f"Preview image created: {preview_path}")
            return preview_path
            
        except Exception as e:
            logger.error(f"Failed to create preview image: {e}")
            return None
