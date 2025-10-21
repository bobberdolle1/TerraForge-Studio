"""
Terrain analyzer using AI vision models
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio

from .ollama_client import OllamaClient
from ..models import AIAnalysisResult, TerrainType, BoundingBox
from ..imagery import ImageryDownloader

logger = logging.getLogger(__name__)


class TerrainAnalyzer:
    """Analyze terrain using AI models"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.imagery_downloader = ImageryDownloader()
    
    async def analyze_satellite_image_detailed(
        self,
        image_path: Path,
        bbox: BoundingBox
    ) -> Dict[str, Any]:
        """
        Perform detailed analysis of satellite imagery with AI vision model
        Extracts precise road widths, building boundaries, surface types
        
        Args:
            image_path: Path to satellite image
            bbox: Geographic bounding box
            
        Returns:
            Detailed analysis dictionary
        """
        vision_prompt = """
Analyze this satellite/aerial imagery with maximum detail and precision.

ROAD ANALYSIS (critical for accurate generation):
1. For EACH visible road, estimate:
   - Exact width in meters (measure from imagery)
   - Number of lanes (count visible lane markings)
   - Lane markings type (solid, dashed, double, none)
   - Road surface type (asphalt, concrete, gravel, dirt)
   - Road condition (excellent, good, fair, poor)
   - Shoulder width if visible
2. Road network density (0.0-1.0)
3. Dominant road types (highway, arterial, residential, service)

BUILDING ANALYSIS (for precise placement):
1. For buildings, identify:
   - Exact footprint boundaries (describe relative positions)
   - Building height estimate from shadows (meters)
   - Roof type (flat, pitched, complex)
   - Building material appearance (concrete, brick, metal, wood)
   - Building spacing and orientation
2. Building density by area (0.0-1.0)
3. Building types distribution (residential, commercial, industrial)

SURFACE & TERRAIN:
1. Surface types:
   - Paved areas (roads, parking lots, plazas)
   - Vegetated areas (grass, trees, forest)
   - Water bodies (rivers, lakes, ponds)
   - Bare ground/soil
2. Terrain characteristics:
   - Elevation variation (flat, rolling, hilly, mountainous)
   - Slope steepness estimation
   - Natural features (valleys, ridges)

INFRASTRUCTURE:
1. Parking lots: location, size, striping pattern
2. Intersections: type (4-way, T, roundabout), traffic control visible
3. Sidewalks and pedestrian paths
4. Visible landmarks or significant structures

Return detailed JSON format.
"""
        
        try:
            logger.info(f"Starting detailed AI vision analysis: {image_path}")
            response = await self.ollama.generate(
                model=self.ollama.vision_model,
                prompt=vision_prompt,
                images=[str(image_path)],
                format="json"
            )
            
            import json
            detailed_analysis = json.loads(response)
            logger.info("Detailed vision analysis complete")
            return detailed_analysis
            
        except Exception as e:
            logger.error(f"Detailed vision analysis failed: {e}")
            return {}
    
    async def analyze_satellite_image(
        self, 
        image_path: Path,
        bbox: BoundingBox
    ) -> AIAnalysisResult:
        """
        Analyze satellite imagery to determine terrain characteristics
        
        Args:
            image_path: Path to satellite image
            bbox: Geographic bounding box of the image
            
        Returns:
            AIAnalysisResult with terrain analysis
        """
        prompt = """Analyze this satellite image and provide detailed information about:

1. Terrain type (forest, urban, suburban, rural, water, mountain, desert, industrial, or mixed)
2. Dominant geographical features (buildings, roads, water bodies, vegetation, etc.)
3. Building density (0.0 to 1.0, where 0 is none and 1.0 is very dense urban)
4. Vegetation density (0.0 to 1.0)
5. Road density (0.0 to 1.0)
6. Any notable features or recommendations for game level design

Format your response as follows:
TERRAIN_TYPE: [type]
FEATURES: [comma-separated list]
BUILDING_DENSITY: [0.0-1.0]
VEGETATION_DENSITY: [0.0-1.0]
ROAD_DENSITY: [0.0-1.0]
SUGGESTIONS: [comma-separated suggestions]
CONFIDENCE: [0.0-1.0]
"""
        
        try:
            logger.info(f"Starting AI analysis of satellite image: {image_path}")
            response = await self.ollama.analyze_image(image_path, prompt)
            
            # Parse the response
            result = self._parse_analysis_response(response)
            logger.info(f"AI analysis completed: {result.terrain_type} "
                       f"(confidence: {result.confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error during terrain analysis: {e}")
            # Return default result on error
            return AIAnalysisResult(
                terrain_type=TerrainType.MIXED,
                dominant_features=["unknown"],
                building_density=0.3,
                vegetation_density=0.3,
                road_density=0.3,
                suggestions=["AI analysis failed, using default values"],
                confidence=0.0
            )
    
    def _parse_analysis_response(self, response: str) -> AIAnalysisResult:
        """Parse AI response into structured result"""
        lines = response.strip().split('\n')
        data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                data[key] = value
        
        # Extract terrain type
        terrain_str = data.get('terrain_type', 'mixed').lower()
        terrain_type = TerrainType.MIXED
        for tt in TerrainType:
            if tt.value in terrain_str:
                terrain_type = tt
                break
        
        # Extract features
        features_str = data.get('features', 'mixed terrain')
        features = [f.strip() for f in features_str.split(',')]
        
        # Extract densities
        try:
            building_density = float(data.get('building_density', '0.3'))
        except ValueError:
            building_density = 0.3
            
        try:
            vegetation_density = float(data.get('vegetation_density', '0.3'))
        except ValueError:
            vegetation_density = 0.3
            
        try:
            road_density = float(data.get('road_density', '0.3'))
        except ValueError:
            road_density = 0.3
        
        # Extract suggestions
        suggestions_str = data.get('suggestions', '')
        suggestions = [s.strip() for s in suggestions_str.split(',') if s.strip()]
        
        # Extract confidence
        try:
            confidence = float(data.get('confidence', '0.7'))
        except ValueError:
            confidence = 0.7
        
        return AIAnalysisResult(
            terrain_type=terrain_type,
            dominant_features=features,
            building_density=max(0.0, min(1.0, building_density)),
            vegetation_density=max(0.0, min(1.0, vegetation_density)),
            road_density=max(0.0, min(1.0, road_density)),
            suggestions=suggestions,
            confidence=max(0.0, min(1.0, confidence))
        )
    
    async def analyze_without_imagery(
        self,
        osm_data: Dict[str, Any],
        bbox: BoundingBox
    ) -> AIAnalysisResult:
        """
        Analyze terrain based on OSM data when satellite imagery is not available
        
        Args:
            osm_data: OpenStreetMap data
            bbox: Geographic bounding box
            
        Returns:
            AIAnalysisResult based on OSM data
        """
        # Calculate densities from OSM data
        area_km2 = bbox.area_km2()
        
        num_buildings = len(osm_data.get('buildings', []))
        num_roads = len(osm_data.get('roads', []))
        num_vegetation = len(osm_data.get('vegetation', []))
        
        # Estimate densities (normalized values)
        building_density = min(1.0, num_buildings / (area_km2 * 50))
        road_density = min(1.0, num_roads / (area_km2 * 20))
        vegetation_density = min(1.0, num_vegetation / (area_km2 * 10))
        
        # Determine terrain type based on densities
        if building_density > 0.7:
            terrain_type = TerrainType.URBAN
        elif building_density > 0.3:
            terrain_type = TerrainType.SUBURBAN
        elif vegetation_density > 0.6:
            terrain_type = TerrainType.FOREST
        else:
            terrain_type = TerrainType.MIXED
        
        features = []
        if building_density > 0.3:
            features.append("buildings")
        if road_density > 0.3:
            features.append("road network")
        if vegetation_density > 0.3:
            features.append("vegetation")
        
        return AIAnalysisResult(
            terrain_type=terrain_type,
            dominant_features=features or ["mixed terrain"],
            building_density=building_density,
            vegetation_density=vegetation_density,
            road_density=road_density,
            suggestions=["Analysis based on OSM data only"],
            confidence=0.6
        )
