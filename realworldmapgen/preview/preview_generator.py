"""
Generate map preview images
"""

import logging
from pathlib import Path
from typing import Optional, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..models import MapData, RoadSegment

logger = logging.getLogger(__name__)


class PreviewGenerator:
    """Generate preview images of generated maps"""
    
    def __init__(self):
        pass
    
    def generate_preview(
        self,
        map_data: MapData,
        output_path: Path,
        size: Tuple[int, int] = (1920, 1080)
    ) -> Path:
        """
        Generate a preview image of the map
        
        Args:
            map_data: Complete map data
            output_path: Where to save the preview
            size: Output image size (width, height)
            
        Returns:
            Path to generated preview image
        """
        logger.info(f"Generating preview for map '{map_data.name}'")
        
        width, height = size
        
        # Create base image
        img = Image.new('RGB', (width, height), color='#1a1a1a')
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Load heightmap if available
        if map_data.heightmap_path and Path(map_data.heightmap_path).exists():
            heightmap = self._load_and_resize_heightmap(
                Path(map_data.heightmap_path),
                size
            )
            # Blend heightmap as background
            img = Image.blend(img, heightmap, alpha=0.3)
            draw = ImageDraw.Draw(img, 'RGBA')
        
        # Calculate bounds for coordinate transformation
        bbox = map_data.bbox
        lat_range = bbox.north - bbox.south
        lon_range = bbox.east - bbox.west
        
        def transform_coords(lat: float, lon: float) -> Tuple[int, int]:
            """Transform lat/lon to image coordinates"""
            x = int((lon - bbox.west) / lon_range * width)
            y = int((bbox.north - lat) / lat_range * height)
            return (x, y)
        
        # Draw roads
        if map_data.roads:
            self._draw_roads(draw, map_data.roads, transform_coords)
        
        # Draw buildings
        if map_data.buildings:
            self._draw_buildings(draw, map_data.buildings, transform_coords)
        
        # Draw traffic lights
        if map_data.traffic_lights:
            self._draw_traffic_lights(draw, map_data.traffic_lights, transform_coords)
        
        # Draw vegetation areas
        if map_data.vegetation:
            self._draw_vegetation(draw, map_data.vegetation, transform_coords)
        
        # Add overlay with map info
        self._add_info_overlay(img, map_data)
        
        # Save
        img.save(output_path, 'JPEG', quality=95)
        logger.info(f"Preview saved to {output_path}")
        
        return output_path
    
    def _load_and_resize_heightmap(
        self,
        heightmap_path: Path,
        size: Tuple[int, int]
    ) -> Image.Image:
        """Load and resize heightmap for background"""
        try:
            heightmap = Image.open(heightmap_path)
            
            # Convert to RGB if needed
            if heightmap.mode != 'RGB':
                # Normalize to 0-255 and create grayscale
                heightmap = heightmap.convert('L')
                # Apply colormap (dark blue to light brown)
                colored = Image.new('RGB', heightmap.size)
                pixels = np.array(heightmap)
                
                # Simple height-based coloring
                rgb_pixels = np.zeros((*pixels.shape, 3), dtype=np.uint8)
                rgb_pixels[:, :, 0] = pixels // 3  # R
                rgb_pixels[:, :, 1] = pixels // 2  # G
                rgb_pixels[:, :, 2] = pixels // 4  # B
                
                colored = Image.fromarray(rgb_pixels, 'RGB')
                heightmap = colored
            
            # Resize to target size
            heightmap = heightmap.resize(size, Image.Resampling.LANCZOS)
            
            return heightmap
            
        except Exception as e:
            logger.warning(f"Failed to load heightmap: {e}")
            return Image.new('RGB', size, color='#1a1a1a')
    
    def _draw_roads(
        self,
        draw: ImageDraw.Draw,
        roads: List[RoadSegment],
        transform: callable
    ):
        """Draw road network"""
        for road in roads:
            if len(road.geometry) < 2:
                continue
            
            # Transform coordinates
            points = [transform(lat, lon) for lat, lon in road.geometry]
            
            # Determine color and width based on road type
            color_map = {
                'motorway': '#ff6b6b',
                'trunk': '#ff8787',
                'primary': '#ffa94d',
                'secondary': '#ffd43b',
                'tertiary': '#adb5bd',
                'residential': '#868e96',
                'service': '#495057',
                'track': '#343a40',
                'path': '#212529'
            }
            
            width_map = {
                'motorway': 4,
                'trunk': 3,
                'primary': 3,
                'secondary': 2,
                'tertiary': 2,
                'residential': 1,
                'service': 1,
                'track': 1,
                'path': 1
            }
            
            color = color_map.get(road.road_type.value, '#868e96')
            width = width_map.get(road.road_type.value, 1)
            
            # Draw road
            draw.line(points, fill=color, width=width)
    
    def _draw_buildings(
        self,
        draw: ImageDraw.Draw,
        buildings: list,
        transform: callable
    ):
        """Draw buildings"""
        for building in buildings:
            if len(building.geometry) < 3:
                continue
            
            points = [transform(lat, lon) for lat, lon in building.geometry]
            
            # Draw filled polygon with semi-transparent fill
            draw.polygon(points, fill=(100, 100, 120, 128), outline=(150, 150, 170, 255))
    
    def _draw_traffic_lights(
        self,
        draw: ImageDraw.Draw,
        traffic_lights: list,
        transform: callable
    ):
        """Draw traffic lights as small circles"""
        for light in traffic_lights:
            x, y = transform(light.position[0], light.position[1])
            
            # Draw small circle
            radius = 3
            draw.ellipse(
                [(x - radius, y - radius), (x + radius, y + radius)],
                fill='#ff0000',
                outline='#ffffff'
            )
    
    def _draw_vegetation(
        self,
        draw: ImageDraw.Draw,
        vegetation: list,
        transform: callable
    ):
        """Draw vegetation areas"""
        for veg in vegetation:
            if len(veg.geometry) < 3:
                continue
            
            points = [transform(lat, lon) for lat, lon in veg.geometry]
            
            # Green with transparency
            color = (34, 139, 34, int(128 * veg.density))
            draw.polygon(points, fill=color)
    
    def _add_info_overlay(
        self,
        img: Image.Image,
        map_data: MapData
    ):
        """Add informational overlay to the image"""
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Semi-transparent background for text
        overlay_height = 120
        draw.rectangle(
            [(0, 0), (img.width, overlay_height)],
            fill=(0, 0, 0, 180)
        )
        
        # Try to use a nice font, fallback to default
        try:
            font_large = ImageFont.truetype("arial.ttf", 32)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Map name
        draw.text((20, 20), map_data.name, fill='white', font=font_large)
        
        # Statistics
        stats_text = (
            f"Roads: {len(map_data.roads)} | "
            f"Buildings: {len(map_data.buildings)} | "
            f"Traffic Lights: {len(map_data.traffic_lights)} | "
            f"Vegetation: {len(map_data.vegetation)}"
        )
        draw.text((20, 65), stats_text, fill='#cccccc', font=font_small)
        
        # Area
        area_text = f"Area: {map_data.bbox.area_km2():.2f} km²"
        draw.text((20, 90), area_text, fill='#cccccc', font=font_small)
