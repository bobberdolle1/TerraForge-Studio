"""
Satellite imagery downloader supporting multiple providers
"""

import logging
import asyncio
from typing import Optional, Tuple
from pathlib import Path
import io

import requests
import numpy as np
from PIL import Image

from ..models import BoundingBox
from ..config import settings

logger = logging.getLogger(__name__)


class ImageryDownloader:
    """Download satellite imagery from various providers"""
    
    def __init__(self):
        self.cache_dir = settings.cache_dir / "imagery"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_imagery(
        self,
        bbox: BoundingBox,
        zoom: int = 15,
        provider: str = "osm"
    ) -> Optional[Tuple[Image.Image, dict]]:
        """
        Download satellite imagery for the bounding box
        
        Args:
            bbox: Geographic bounding box
            zoom: Zoom level (higher = more detail)
            provider: Imagery provider (osm, mapbox, google, bing)
            
        Returns:
            Tuple of (PIL Image, metadata dict) or None if failed
        """
        logger.info(f"Downloading {provider} imagery for {bbox} at zoom {zoom}")
        
        try:
            if provider == "osm":
                return await self._download_osm_tiles(bbox, zoom)
            elif provider == "mapbox":
                return await self._download_mapbox(bbox, zoom)
            elif provider == "bing":
                return await self._download_bing(bbox, zoom)
            else:
                logger.warning(f"Unknown provider: {provider}, using OSM")
                return await self._download_osm_tiles(bbox, zoom)
                
        except Exception as e:
            logger.error(f"Failed to download imagery: {e}")
            return None
    
    async def _download_osm_tiles(
        self,
        bbox: BoundingBox,
        zoom: int
    ) -> Tuple[Image.Image, dict]:
        """
        Download OpenStreetMap tiles (satellite view not available, uses map tiles)
        For actual satellite, use Mapbox or Bing
        """
        # Calculate tile coordinates
        tiles = self._bbox_to_tiles(bbox, zoom)
        
        if not tiles:
            raise ValueError("No tiles found for bounding box")
        
        # Download tiles
        tile_images = []
        for tile_x, tile_y in tiles:
            tile_url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"
            
            # Add delay to respect OSM usage policy
            await asyncio.sleep(0.1)
            
            try:
                response = await asyncio.to_thread(
                    requests.get,
                    tile_url,
                    headers={'User-Agent': 'RealWorldMapGen-BNG/1.0'},
                    timeout=10
                )
                response.raise_for_status()
                
                img = Image.open(io.BytesIO(response.content))
                tile_images.append((tile_x, tile_y, img))
                
            except Exception as e:
                logger.warning(f"Failed to download tile {tile_x},{tile_y}: {e}")
        
        if not tile_images:
            raise ValueError("Failed to download any tiles")
        
        # Stitch tiles together
        stitched = self._stitch_tiles(tile_images, zoom)
        
        metadata = {
            "provider": "osm",
            "zoom": zoom,
            "tiles_count": len(tile_images),
            "bbox": bbox.dict()
        }
        
        return stitched, metadata
    
    async def _download_mapbox(
        self,
        bbox: BoundingBox,
        zoom: int
    ) -> Tuple[Image.Image, dict]:
        """
        Download Mapbox satellite imagery
        Requires MAPBOX_ACCESS_TOKEN environment variable
        """
        import os
        
        mapbox_token = os.getenv('MAPBOX_ACCESS_TOKEN')
        if not mapbox_token:
            logger.warning("MAPBOX_ACCESS_TOKEN not set, falling back to OSM tiles")
            return await self._download_osm_tiles(bbox, zoom)
        
        # Calculate center and size
        center_lat, center_lon = bbox.center()
        
        # Mapbox Static Images API
        # Format: /styles/v1/{username}/{style_id}/static/{lon},{lat},{zoom}/{width}x{height}
        width, height = 1280, 1280
        
        url = (
            f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
            f"{center_lon},{center_lat},{zoom}/{width}x{height}"
            f"?access_token={mapbox_token}"
        )
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                url,
                timeout=30
            )
            response.raise_for_status()
            
            img = Image.open(io.BytesIO(response.content))
            
            metadata = {
                "provider": "mapbox",
                "zoom": zoom,
                "center": (center_lat, center_lon),
                "bbox": bbox.dict()
            }
            
            return img, metadata
            
        except Exception as e:
            logger.error(f"Mapbox download failed: {e}")
            raise
    
    async def _download_bing(
        self,
        bbox: BoundingBox,
        zoom: int
    ) -> Tuple[Image.Image, dict]:
        """
        Download Bing Maps satellite imagery
        Uses Bing Maps REST API (requires API key)
        """
        import os
        
        bing_key = os.getenv('BING_MAPS_KEY')
        if not bing_key:
            logger.warning("BING_MAPS_KEY not set, falling back to OSM tiles")
            return await self._download_osm_tiles(bbox, zoom)
        
        center_lat, center_lon = bbox.center()
        
        # Bing Maps Imagery API
        url = (
            f"https://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/"
            f"{center_lat},{center_lon}/{zoom}"
            f"?mapSize=1500,1500&key={bing_key}"
        )
        
        try:
            response = await asyncio.to_thread(
                requests.get,
                url,
                timeout=30
            )
            response.raise_for_status()
            
            img = Image.open(io.BytesIO(response.content))
            
            metadata = {
                "provider": "bing",
                "zoom": zoom,
                "center": (center_lat, center_lon),
                "bbox": bbox.dict()
            }
            
            return img, metadata
            
        except Exception as e:
            logger.error(f"Bing download failed: {e}")
            raise
    
    def _bbox_to_tiles(
        self,
        bbox: BoundingBox,
        zoom: int
    ) -> list:
        """Convert bounding box to list of tile coordinates"""
        # Convert lat/lon to tile coordinates
        def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
            lat_rad = np.radians(lat)
            n = 2.0 ** zoom
            x = int((lon + 180.0) / 360.0 * n)
            y = int((1.0 - np.log(np.tan(lat_rad) + (1 / np.cos(lat_rad))) / np.pi) / 2.0 * n)
            return (x, y)
        
        # Get tile range
        x_min, y_max = lat_lon_to_tile(bbox.south, bbox.west, zoom)
        x_max, y_min = lat_lon_to_tile(bbox.north, bbox.east, zoom)
        
        # Generate all tiles in range
        tiles = []
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                tiles.append((x, y))
        
        # Limit number of tiles to prevent excessive downloads
        if len(tiles) > 100:
            logger.warning(f"Too many tiles ({len(tiles)}), limiting to 100")
            tiles = tiles[:100]
        
        return tiles
    
    def _stitch_tiles(
        self,
        tile_images: list,
        zoom: int,
        tile_size: int = 256
    ) -> Image.Image:
        """Stitch downloaded tiles into a single image"""
        if not tile_images:
            raise ValueError("No tiles to stitch")
        
        # Get min/max tile coordinates
        xs = [t[0] for t in tile_images]
        ys = [t[1] for t in tile_images]
        
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        # Create output image
        width = (x_max - x_min + 1) * tile_size
        height = (y_max - y_min + 1) * tile_size
        
        output = Image.new('RGB', (width, height))
        
        # Paste tiles
        for tile_x, tile_y, img in tile_images:
            x_offset = (tile_x - x_min) * tile_size
            y_offset = (tile_y - y_min) * tile_size
            output.paste(img, (x_offset, y_offset))
        
        return output
    
    def save_imagery(
        self,
        image: Image.Image,
        map_name: str,
        suffix: str = "satellite"
    ) -> Path:
        """Save imagery to cache"""
        filename = f"{map_name}_{suffix}.jpg"
        output_path = self.cache_dir / filename
        
        image.save(output_path, 'JPEG', quality=90)
        logger.info(f"Saved imagery to {output_path}")
        
        return output_path
