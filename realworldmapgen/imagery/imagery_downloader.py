"""
Imagery downloader for satellite images
"""

import logging
from typing import Optional
from pathlib import Path
import asyncio
import httpx
from PIL import Image
import io

from ..models import BoundingBox
from ..config import settings

logger = logging.getLogger(__name__)


class ImageryDownloader:
    """Download satellite imagery from various sources"""
    
    def __init__(self):
        self.cache_dir = settings.cache_dir / "imagery"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_satellite_image(
        self,
        bbox: BoundingBox,
        zoom: int = 16,
        source: str = "esri"
    ) -> Optional[Path]:
        """
        Download satellite imagery for a bounding box
        
        Args:
            bbox: Geographic bounding box
            zoom: Zoom level (1-19)
            source: Imagery source (esri, google, bing)
            
        Returns:
            Path to downloaded image or None if failed
        """
        logger.info(f"Downloading satellite imagery for {bbox} at zoom {zoom}")
        
        try:
            # Calculate tile coordinates
            center_lat, center_lon = bbox.center()
            
            # For simplicity, download a single tile at the center
            # In production, you'd stitch multiple tiles together
            
            if source == "esri":
                url = self._get_esri_url(center_lat, center_lon, zoom)
            else:
                logger.warning(f"Unsupported source: {source}, using ESRI")
                url = self._get_esri_url(center_lat, center_lon, zoom)
            
            # Download image
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Save image
                image_data = response.content
                img = Image.open(io.BytesIO(image_data))
                
                # Generate filename
                filename = f"satellite_{bbox.north}_{bbox.west}_{zoom}.png"
                output_path = self.cache_dir / filename
                
                img.save(output_path)
                logger.info(f"Satellite image saved to {output_path}")
                
                return output_path
                
        except Exception as e:
            logger.error(f"Failed to download satellite imagery: {e}")
            return None
    
    def _get_esri_url(self, lat: float, lon: float, zoom: int) -> str:
        """Get ESRI World Imagery tile URL"""
        # Convert lat/lon to tile coordinates
        x, y = self._latlon_to_tile(lat, lon, zoom)
        return f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
    
    def _latlon_to_tile(self, lat: float, lon: float, zoom: int) -> tuple:
        """Convert lat/lon to tile coordinates"""
        import math
        
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        
        return (x, y)
    
    async def download_multiple_tiles(
        self,
        bbox: BoundingBox,
        zoom: int = 16
    ) -> Optional[Path]:
        """
        Download and stitch multiple tiles to cover entire bbox
        
        Args:
            bbox: Geographic bounding box
            zoom: Zoom level
            
        Returns:
            Path to stitched image
        """
        # This is a placeholder for future implementation
        # Would involve downloading multiple tiles and stitching them together
        logger.info("Multi-tile download not yet implemented, using single tile")
        return await self.download_satellite_image(bbox, zoom)
