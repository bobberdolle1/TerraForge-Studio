"""
Heightmap generation from elevation data
"""

import logging
from typing import Tuple, Optional
from pathlib import Path
import numpy as np
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..models import BoundingBox
from ..config import settings

logger = logging.getLogger(__name__)


class HeightmapGenerator:
    """Generate heightmaps from elevation data"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or settings.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def generate_heightmap(
        self,
        bbox: BoundingBox,
        resolution: int = 2048,
        map_name: str = "map"
    ) -> Tuple[Path, np.ndarray]:
        """
        Generate heightmap for the given bounding box
        
        Args:
            bbox: Geographic bounding box
            resolution: Output heightmap resolution
            map_name: Name of the map (for filename)
            
        Returns:
            Tuple of (heightmap file path, elevation data array)
        """
        logger.info(f"Generating heightmap for {bbox} at resolution {resolution}")
        
        # Create output directory for this map
        map_output_dir = settings.output_dir / map_name
        map_output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download elevation data using elevation package
            elevation_data = await self._download_elevation_data(bbox)
            
            # Resample to desired resolution
            resampled_data = await self._resample_elevation(
                elevation_data,
                bbox,
                resolution
            )
            
            # Save as 16-bit PNG to map directory
            output_path = self._save_heightmap(resampled_data, map_name, map_output_dir)
            
            logger.info(f"Heightmap saved to {output_path}")
            return output_path, resampled_data
            
        except Exception as e:
            logger.error(f"Error generating heightmap: {e}")
            # Return a flat heightmap as fallback
            flat_data = np.zeros((resolution, resolution), dtype=np.float32)
            output_path = self._save_heightmap(flat_data, map_name, map_output_dir)
            return output_path, flat_data
    
    async def _download_elevation_data(self, bbox: BoundingBox) -> np.ndarray:
        """Download real elevation data from Terrain RGB tiles"""
        import httpx
        import math
        from io import BytesIO
        
        logger.info("Downloading real elevation data from terrain tiles...")
        
        # Use zoom level 10 for good detail
        zoom = 10
        
        # Calculate tile coordinates for bbox
        def latlon_to_tile(lat, lon, zoom):
            lat_rad = math.radians(lat)
            n = 2.0 ** zoom
            x = int((lon + 180.0) / 360.0 * n)
            y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
            return (x, y)
        
        # Get tile range
        center_lat = (bbox.north + bbox.south) / 2
        center_lon = (bbox.east + bbox.west) / 2
        tile_x, tile_y = latlon_to_tile(center_lat, center_lon, zoom)
        
        # Mapzen Terrain RGB tiles (now available via AWS)
        # Alternative: use Open-Elevation or SRTM directly
        tile_url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{zoom}/{tile_x}/{tile_y}.png"
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                logger.info(f"Fetching terrain tile: {tile_url}")
                response = await client.get(tile_url)
                
                if response.status_code == 200:
                    # Decode terrain RGB tile
                    # Terrarium format: elevation = (R * 256 + G + B / 256) - 32768
                    img = Image.open(BytesIO(response.content))
                    img_array = np.array(img)
                    
                    if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
                        r = img_array[:, :, 0].astype(np.float32)
                        g = img_array[:, :, 1].astype(np.float32)
                        b = img_array[:, :, 2].astype(np.float32)
                        
                        # Decode Terrarium format
                        elevation = (r * 256.0 + g + b / 256.0) - 32768.0
                        
                        logger.info(f"✅ Downloaded real elevation data: {elevation.shape}, range: {elevation.min():.1f}m to {elevation.max():.1f}m")
                        return elevation
                    else:
                        logger.warning("Invalid terrain tile format")
                        raise ValueError("Invalid tile format")
                else:
                    logger.warning(f"Failed to fetch terrain tile: HTTP {response.status_code}")
                    raise ValueError(f"HTTP {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to download real elevation data: {e}")
            logger.warning("Falling back to synthetic elevation data")
            
            # Fallback: create synthetic terrain
            width, height = 512, 512
            x = np.linspace(0, 10, width)
            y = np.linspace(0, 10, height)
            X, Y = np.meshgrid(x, y)
            
            elevation = (
                50 * np.sin(X * 0.5) * np.cos(Y * 0.5) +
                30 * np.sin(X * 1.2 + Y * 0.8) +
                20 * np.cos(X * 0.8 - Y * 1.5) +
                100
            )
            
            logger.info("Using synthetic elevation data as fallback")
            return elevation.astype(np.float32)
    
    async def _resample_elevation(
        self,
        elevation_data: np.ndarray,
        bbox: BoundingBox,
        target_resolution: int
    ) -> np.ndarray:
        """Resample elevation data to target resolution"""
        logger.info(f"Resampling elevation data to {target_resolution}x{target_resolution}")
        
        # Use PIL for high-quality resampling
        img = Image.fromarray(elevation_data)
        resampled = img.resize(
            (target_resolution, target_resolution),
            Image.Resampling.LANCZOS
        )
        
        return np.array(resampled, dtype=np.float32)
    
    def _save_heightmap(self, data: np.ndarray, map_name: str, output_dir: Path) -> Path:
        """Save heightmap as 16-bit PNG"""
        # Normalize to 16-bit range
        min_val = data.min()
        max_val = data.max()
        
        if max_val > min_val:
            normalized = ((data - min_val) / (max_val - min_val) * 65535).astype(np.uint16)
        else:
            normalized = np.zeros_like(data, dtype=np.uint16)
        
        # Save to map directory
        filename = f"{map_name}_heightmap.png"
        output_path = output_dir / filename
        
        from PIL import Image
        img = Image.fromarray(normalized, mode='I;16')
        img.save(output_path)
        
        return output_path
    
    def get_elevation_at_point(
        self,
        elevation_data: np.ndarray,
        lat: float,
        lon: float,
        bbox: BoundingBox
    ) -> float:
        """
        Get elevation at a specific point
        
        Args:
            elevation_data: Elevation array
            lat: Latitude
            lon: Longitude
            bbox: Bounding box of the elevation data
            
        Returns:
            Elevation in meters
        """
        # Normalize coordinates to array indices
        height, width = elevation_data.shape
        
        x = (lon - bbox.west) / (bbox.east - bbox.west) * width
        y = (bbox.north - lat) / (bbox.north - bbox.south) * height
        
        # Clamp to array bounds
        x = max(0, min(width - 1, int(x)))
        y = max(0, min(height - 1, int(y)))
        
        return float(elevation_data[y, x])
    
    def calculate_slope(self, elevation_data: np.ndarray) -> np.ndarray:
        """
        Calculate slope magnitude for each point
        
        Args:
            elevation_data: Elevation array
            
        Returns:
            Slope magnitude array (in degrees)
        """
        # Calculate gradients
        dy, dx = np.gradient(elevation_data)
        
        # Calculate slope magnitude
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope_deg = np.degrees(slope_rad)
        
        return slope_deg
    
    def generate_normal_map(
        self,
        elevation_data: np.ndarray,
        strength: float = 1.0
    ) -> np.ndarray:
        """
        Generate normal map from elevation data
        
        Args:
            elevation_data: Elevation array
            strength: Normal map strength multiplier
            
        Returns:
            RGB normal map array
        """
        # Calculate gradients
        dy, dx = np.gradient(elevation_data * strength)
        
        # Create normal vectors
        normals = np.dstack((
            -dx,
            -dy,
            np.ones_like(elevation_data)
        ))
        
        # Normalize
        magnitude = np.sqrt((normals ** 2).sum(axis=2, keepdims=True))
        normals = normals / magnitude
        
        # Convert to 0-255 range
        normal_map = ((normals + 1) * 127.5).astype(np.uint8)
        
        return normal_map
