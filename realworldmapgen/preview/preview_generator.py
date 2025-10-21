"""
Preview image generator for maps
"""

import logging
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..models import MapData
from ..config import settings

logger = logging.getLogger(__name__)


class PreviewGenerator:
    """Generate preview images for maps"""
    
    def __init__(self):
        pass
    
    def generate_preview(
        self,
        map_data: MapData,
        output_path: Path,
        size: tuple = (1024, 1024)
    ) -> Optional[Path]:
        """
        Generate a preview image for the map
        
        Args:
            map_data: Map data to visualize
            output_path: Output path for preview image
            size: Image size (width, height)
            
        Returns:
            Path to generated preview image
        """
        logger.info(f"Generating preview for map: {map_data.name}")
        
        try:
            # Create base image
            img = Image.new('RGB', size, color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Calculate scaling factors
            bbox = map_data.bbox
            width, height = size
            
            lon_range = bbox.east - bbox.west
            lat_range = bbox.north - bbox.south
            
            scale_x = width / lon_range
            scale_y = height / lat_range
            
            # Convert lat/lon to pixel coordinates
            def latlon_to_pixel(lat: float, lon: float) -> tuple:
                x = int((lon - bbox.west) * scale_x)
                y = int((bbox.north - lat) * scale_y)  # Flip Y axis
                return (x, y)
            
            # Draw roads
            if map_data.roads:
                for road in map_data.roads:
                    if len(road.geometry) < 2:
                        continue
                    
                    # Convert road geometry to pixels
                    points = [latlon_to_pixel(lat, lon) for lat, lon in road.geometry]
                    
                    # Determine road color and width
                    road_width = max(1, int(road.width / 2))
                    
                    # Draw road
                    draw.line(points, fill='#666666', width=road_width)
            
            # Draw buildings
            if map_data.buildings:
                for building in map_data.buildings:
                    if len(building.geometry) < 3:
                        continue
                    
                    # Convert building geometry to pixels
                    points = [latlon_to_pixel(lat, lon) for lat, lon in building.geometry]
                    
                    # Draw building
                    draw.polygon(points, fill='#cccccc', outline='#888888')
            
            # Draw vegetation (as green areas)
            if map_data.vegetation:
                for veg in map_data.vegetation:
                    if len(veg.geometry) < 3:
                        continue
                    
                    points = [latlon_to_pixel(lat, lon) for lat, lon in veg.geometry]
                    
                    # Draw vegetation
                    alpha = int(veg.density * 200)
                    draw.polygon(points, fill=f'#{alpha:02x}{alpha+55:02x}{alpha:02x}')
            
            # Draw traffic lights
            if map_data.traffic_lights:
                for light in map_data.traffic_lights:
                    x, y = latlon_to_pixel(light.position[0], light.position[1])
                    draw.ellipse([x-3, y-3, x+3, y+3], fill='#ff0000')
            
            # Draw parking lots
            if map_data.parking_lots:
                for parking in map_data.parking_lots:
                    if len(parking.geometry) < 3:
                        continue
                    
                    points = [latlon_to_pixel(lat, lon) for lat, lon in parking.geometry]
                    draw.polygon(points, fill='#9999cc', outline='#6666aa')
            
            # Add map info overlay
            self._add_info_overlay(img, map_data)
            
            # Save preview
            img.save(output_path)
            logger.info(f"Preview saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate preview: {e}")
            return None
    
    def _add_info_overlay(self, img: Image.Image, map_data: MapData):
        """Add information overlay to preview image"""
        draw = ImageDraw.Draw(img)
        
        # Add semi-transparent background
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Info box
        box_height = 120
        overlay_draw.rectangle(
            [(0, img.height - box_height), (img.width, img.height)],
            fill=(0, 0, 0, 180)
        )
        
        # Composite overlay
        img.paste(overlay, (0, 0), overlay)
        
        # Add text (using default font)
        try:
            # Try to use a better font if available
            font = ImageFont.truetype("arial.ttf", 16)
            font_large = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            font_large = ImageFont.load_default()
        
        # Title
        title_y = img.height - box_height + 10
        draw.text((10, title_y), map_data.name, fill='white', font=font_large)
        
        # Statistics
        stats_y = title_y + 35
        stats = [
            f"Roads: {len(map_data.roads)}",
            f"Buildings: {len(map_data.buildings)}",
            f"Area: {map_data.bbox.area_km2():.2f} km²"
        ]
        
        stats_text = " | ".join(stats)
        draw.text((10, stats_y), stats_text, fill='white', font=font)
        
        # Terrain type if available
        if map_data.ai_analysis:
            terrain_y = stats_y + 25
            draw.text(
                (10, terrain_y),
                f"Terrain: {map_data.ai_analysis.terrain_type.value}",
                fill='#88ff88',
                font=font
            )
    
    def generate_heightmap_preview(
        self,
        heightmap_path: Path,
        output_path: Path,
        apply_colormap: bool = True
    ) -> Optional[Path]:
        """
        Generate a preview of heightmap with optional colormap
        
        Args:
            heightmap_path: Path to heightmap file
            output_path: Output path for preview
            apply_colormap: Whether to apply terrain colormap
            
        Returns:
            Path to generated preview
        """
        try:
            # Load heightmap
            img = Image.open(heightmap_path)
            
            if apply_colormap:
                # Convert to numpy array
                data = np.array(img)
                
                # Normalize to 0-255
                data_normalized = ((data - data.min()) / (data.max() - data.min()) * 255).astype(np.uint8)
                
                # Apply simple terrain colormap
                # Low = water/green, mid = brown, high = white
                colored = np.zeros((*data_normalized.shape, 3), dtype=np.uint8)
                
                # Water (0-50)
                mask = data_normalized < 50
                colored[mask] = [100, 150, 200]
                
                # Lowlands (50-100)
                mask = (data_normalized >= 50) & (data_normalized < 100)
                colored[mask] = [120, 180, 100]
                
                # Hills (100-180)
                mask = (data_normalized >= 100) & (data_normalized < 180)
                colored[mask] = [160, 140, 100]
                
                # Mountains (180+)
                mask = data_normalized >= 180
                colored[mask] = [240, 240, 240]
                
                img = Image.fromarray(colored)
            
            # Resize for preview
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Save
            img.save(output_path)
            logger.info(f"Heightmap preview saved to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate heightmap preview: {e}")
            return None
