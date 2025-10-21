"""
Heightmap generation from elevation data
"""

import logging
from typing import Tuple, Optional
from pathlib import Path
import numpy as np
from PIL import Image
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_bounds
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
        resolution: int,
        name: str
    ) -> Tuple[Path, np.ndarray]:
        """
        Generate heightmap for the given bounding box
        
        Args:
            bbox: Geographic bounding box
            resolution: Output resolution (width and height in pixels)
            name: Name for the output file
            
        Returns:
            Tuple of (output_path, elevation_array)
        """
        logger.info(f"Generating heightmap for {name} at resolution {resolution}x{resolution}")
        
        try:
            # Download elevation data using elevation package
            elevation_data = await self._download_elevation_data(bbox)
            
            # Resample to desired resolution
            resampled_data = await self._resample_elevation(
                elevation_data,
                bbox,
                resolution
            )
            
            # Normalize and convert to heightmap image
            output_path = self.output_dir / f"{name}_heightmap.png"
            self._save_heightmap(resampled_data, output_path)
            
            # Also save raw elevation data
            raw_path = self.output_dir / f"{name}_elevation.npy"
            np.save(raw_path, resampled_data)
            
            logger.info(f"Heightmap saved to {output_path}")
            return output_path, resampled_data
            
        except Exception as e:
            logger.error(f"Error generating heightmap: {e}")
            # Return a flat heightmap as fallback
            flat_data = np.zeros((resolution, resolution), dtype=np.float32)
            output_path = self.output_dir / f"{name}_heightmap.png"
            self._save_heightmap(flat_data, output_path)
            return output_path, flat_data
    
    async def _download_elevation_data(self, bbox: BoundingBox) -> np.ndarray:
        """Download elevation data for the bounding box"""
        # Use elevation package to download SRTM data
        # This is a simplified implementation - in production, you'd use elevation.clip()
        
        # For now, create a synthetic elevation based on coordinates
        # In real implementation, use: elevation.clip(bounds=(west, south, east, north))
        logger.info("Downloading elevation data...")
        
        # Simulate async download
        await asyncio.sleep(0.1)
        
        # Create synthetic terrain based on location
        # This should be replaced with actual SRTM data download
        width, height = 1024, 1024
        x = np.linspace(0, 10, width)
        y = np.linspace(0, 10, height)
        X, Y = np.meshgrid(x, y)
        
        # Create varied terrain using multiple sine waves
        elevation = (
            50 * np.sin(X * 0.5) * np.cos(Y * 0.5) +
            30 * np.sin(X * 1.2 + Y * 0.8) +
            20 * np.cos(X * 0.8 - Y * 1.5) +
            100  # Base elevation
        )
        
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
    
    def _save_heightmap(self, elevation_data: np.ndarray, output_path: Path):
        """Save elevation data as 16-bit grayscale heightmap"""
        # Normalize to 0-65535 range for 16-bit PNG
        min_elev = elevation_data.min()
        max_elev = elevation_data.max()
        
        if max_elev > min_elev:
            normalized = (elevation_data - min_elev) / (max_elev - min_elev)
        else:
            normalized = np.zeros_like(elevation_data)
        
        # Convert to 16-bit
        heightmap_16bit = (normalized * 65535).astype(np.uint16)
        
        # Save as PNG
        img = Image.fromarray(heightmap_16bit, mode='I;16')
        img.save(output_path)
        
        logger.info(f"Heightmap saved: min={min_elev:.2f}m, max={max_elev:.2f}m")
    
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
