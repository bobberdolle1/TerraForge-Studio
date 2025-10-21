"""
Main map generation orchestrator
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import uuid

from .models import (
    MapGenerationRequest, MapData, GenerationStatus,
    AIAnalysisResult, BoundingBox
)
from .config import settings, ensure_directories
from .ai import OllamaClient, TerrainAnalyzer
from .osm import OSMExtractor
from .elevation import HeightmapGenerator
from .exporters import BeamNGExporter

logger = logging.getLogger(__name__)


class MapGenerator:
    """Main orchestrator for map generation"""
    
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.terrain_analyzer = TerrainAnalyzer(self.ollama_client)
        self.osm_extractor = OSMExtractor()
        self.heightmap_generator = HeightmapGenerator()
        
        # Task tracking
        self.active_tasks: Dict[str, GenerationStatus] = {}
        
        ensure_directories()
    
    async def generate_map(
        self,
        request: MapGenerationRequest,
        task_id: Optional[str] = None
    ) -> GenerationStatus:
        """
        Generate a complete map from the request
        
        Args:
            request: Map generation request
            task_id: Optional task ID (will be generated if not provided)
            
        Returns:
            Generation status with result
        """
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        status = GenerationStatus(
            task_id=task_id,
            status="processing",
            progress=0.0,
            current_step="Initializing"
        )
        self.active_tasks[task_id] = status
        
        try:
            logger.info(f"Starting map generation for '{request.name}' (task: {task_id})")
            
            # Validate area size
            area_km2 = request.bbox.area_km2()
            if area_km2 > settings.max_area_km2:
                raise ValueError(
                    f"Area too large: {area_km2:.2f} km² "
                    f"(max: {settings.max_area_km2} km²)"
                )
            
            # Create map data structure
            map_data = MapData(
                name=request.name,
                bbox=request.bbox
            )
            
            # Step 1: Extract OSM data
            status.current_step = "Extracting OpenStreetMap data"
            status.progress = 10.0
            logger.info("Step 1/5: Extracting OSM data")
            
            osm_data = await asyncio.to_thread(
                self.osm_extractor.extract_all_data,
                request.bbox
            )
            
            if request.enable_roads:
                map_data.roads = osm_data["roads"]
            if request.enable_buildings:
                map_data.buildings = osm_data["buildings"]
            map_data.traffic_lights = osm_data["traffic_lights"]
            map_data.parking_lots = osm_data["parking_lots"]
            if request.enable_vegetation:
                map_data.vegetation = osm_data["vegetation"]
            
            status.progress = 30.0
            
            # Step 2: AI terrain analysis (if enabled)
            if request.enable_ai_analysis and settings.enable_ai_analysis:
                status.current_step = "Analyzing terrain with AI"
                status.progress = 35.0
                logger.info("Step 2/5: AI terrain analysis")
                
                # Check if Ollama is available
                ollama_available = await self.ollama_client.check_health()
                
                if ollama_available:
                    # For now, analyze without imagery (can be extended with satellite images)
                    ai_result = await self.terrain_analyzer.analyze_without_imagery(
                        osm_data,
                        request.bbox
                    )
                    map_data.ai_analysis = ai_result
                    logger.info(f"AI analysis: {ai_result.terrain_type} "
                              f"(confidence: {ai_result.confidence:.2f})")
                else:
                    logger.warning("Ollama not available, skipping AI analysis")
                    # Use OSM-based analysis
                    ai_result = await self.terrain_analyzer.analyze_without_imagery(
                        osm_data,
                        request.bbox
                    )
                    map_data.ai_analysis = ai_result
            
            status.progress = 50.0
            
            # Step 3: Generate heightmap
            status.current_step = "Generating heightmap"
            status.progress = 55.0
            logger.info("Step 3/5: Generating heightmap")
            
            resolution = request.resolution or settings.default_resolution
            heightmap_path, elevation_data = await self.heightmap_generator.generate_heightmap(
                request.bbox,
                resolution,
                request.name
            )
            map_data.heightmap_path = str(heightmap_path)
            
            status.progress = 70.0
            
            # Step 4: AI-assisted infrastructure optimization (if enabled)
            if map_data.ai_analysis and settings.enable_ai_analysis:
                status.current_step = "Optimizing infrastructure placement"
                status.progress = 75.0
                logger.info("Step 4/5: AI infrastructure optimization")
                
                ollama_available = await self.ollama_client.check_health()
                if ollama_available:
                    try:
                        optimization_prompt = """
                        Provide recommendations for optimizing object placement density based on terrain.
                        Consider: vehicle spawn points, traffic density, vegetation distribution.
                        Return a brief JSON response with recommendations.
                        """
                        
                        optimization = await self.ollama_client.analyze_osm_data(
                            osm_data,
                            map_data.ai_analysis.dict(),
                            optimization_prompt
                        )
                        
                        map_data.metadata["ai_optimization"] = optimization
                        logger.info("AI optimization completed")
                    except Exception as e:
                        logger.warning(f"AI optimization failed: {e}")
            
            status.progress = 85.0
            
            # Step 5: Export to BeamNG.drive format
            status.current_step = "Exporting to BeamNG.drive format"
            status.progress = 90.0
            logger.info("Step 5/5: Exporting to BeamNG.drive format")
            
            exporter = BeamNGExporter(settings.output_dir / request.name)
            exported_files = exporter.export_complete_map(map_data)
            
            map_data.metadata["exported_files"] = {
                name: str(path) for name, path in exported_files.items()
            }
            
            # Complete
            status.status = "completed"
            status.progress = 100.0
            status.current_step = "Completed"
            status.result = map_data
            status.message = f"Map '{request.name}' generated successfully"
            
            logger.info(f"Map generation completed: {request.name}")
            
        except Exception as e:
            logger.error(f"Error during map generation: {e}", exc_info=True)
            status.status = "failed"
            status.error = str(e)
            status.message = f"Generation failed: {e}"
        
        return status
    
    async def get_status(self, task_id: str) -> Optional[GenerationStatus]:
        """Get status of a generation task"""
        return self.active_tasks.get(task_id)
    
    async def list_tasks(self) -> Dict[str, GenerationStatus]:
        """List all tasks"""
        return self.active_tasks.copy()
    
    async def check_ollama_health(self) -> bool:
        """Check if Ollama is available"""
        return await self.ollama_client.check_health()
    
    async def list_ollama_models(self) -> list:
        """List available Ollama models"""
        return await self.ollama_client.list_models()
    
    async def setup_ollama_models(self) -> Dict[str, bool]:
        """Pull required Ollama models if not present"""
        logger.info("Checking Ollama models...")
        
        available_models = await self.list_ollama_models()
        results = {}
        
        # Check vision model
        vision_model = settings.ollama_vision_model
        if vision_model not in available_models:
            logger.info(f"Pulling vision model: {vision_model}")
            results[vision_model] = await self.ollama_client.pull_model(vision_model)
        else:
            results[vision_model] = True
        
        # Check coder model
        coder_model = settings.ollama_coder_model
        if coder_model not in available_models:
            logger.info(f"Pulling coder model: {coder_model}")
            results[coder_model] = await self.ollama_client.pull_model(coder_model)
        else:
            results[coder_model] = True
        
        return results
