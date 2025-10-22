"""
FastAPI application for RealWorldMapGen-BNG
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path

from ..models import (
    MapGenerationRequest, GenerationStatus, BoundingBox, ExportFormat
)
from ..core.terrain_generator import TerraForgeGenerator
from ..config import settings
from .settings_routes import router as settings_router
from .batch_routes import router as batch_router
from .ai_routes import router as ai_router
from .websocket_routes import router as websocket_router
from .cache_routes import router as cache_router
from .share_routes import router as share_router
from .plugin_routes import router as plugin_router
from .auth_routes import router as auth_router
from .cloud_routes import router as cloud_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TerraForge Studio",
    description="Professional cross-platform 3D terrain and real-world map generator for Unreal Engine 5, Unity, and other game engines",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(settings_router)
app.include_router(batch_router)
app.include_router(ai_router)
app.include_router(websocket_router)
app.include_router(cache_router)
app.include_router(share_router)
app.include_router(plugin_router)
app.include_router(auth_router)
app.include_router(cloud_router)

# Global generator instance
generator = TerraForgeGenerator()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting TerraForge Studio API v1.0.0")
    logger.info("=" * 60)
    
    # Check available data sources
    logger.info("Checking data sources...")
    
    # Check Ollama (optional - for future AI features)
    try:
        logger.info("○ Ollama check: Optional for AI terrain analysis")
    except Exception as e:
        logger.info(f"○ Ollama check failed: {e}")
    
    # Check OpenStreetMap (always available)
    logger.info("✓ OpenStreetMap available (free)")
    
    # Check other sources from config
    logger.info("○ Premium sources: Check .env for API keys")
    logger.info("  - Sentinel Hub: Satellite imagery")
    logger.info("  - OpenTopography: High-res DEMs")
    logger.info("  - Azure Maps: Vector data")
    logger.info("=" * 60)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "TerraForge Studio",
        "version": "1.0.0",
        "description": "Professional cross-platform 3D terrain and real-world map generator",
        "supported_engines": ["Unreal Engine 5", "Unity", "Generic (GLTF/GeoTIFF)"],
        "endpoints": {
            "generate": "/api/generate",
            "status": "/api/status/{task_id}",
            "tasks": "/api/tasks",
            "health": "/api/health",
            "sources": "/api/sources",
            "formats": "/api/formats",
            "docs": "/docs"
        },
        "repository": "https://github.com/yourusername/TerraForge-Studio",
        "documentation": "https://github.com/yourusername/TerraForge-Studio/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    
    # Check available sources
    available_sources = []
    for name, source in generator.sources.items():
        try:
            is_avail = await source.is_available()
            if is_avail:
                available_sources.append(name)
        except:
            pass
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "data_sources": {
            "available": available_sources,
            "total": len(generator.sources)
        },
        "settings": {
            "max_area_km2": getattr(settings, 'max_area_km2', 100.0),
            "default_resolution": getattr(settings, 'default_resolution', 2048),
        }
    }


@app.get("/api/sources")
async def get_data_sources():
    """Get available data sources and their status"""
    return {
        "elevation": {
            "srtm": {
                "name": "SRTM (Shuttle Radar Topography Mission)",
                "resolution": "30m-90m",
                "coverage": "Global",
                "cost": "Free",
                "available": True,
                "requires_api_key": False
            },
            "opentopography": {
                "name": "OpenTopography",
                "resolution": "0.5m-30m (varies by region)",
                "coverage": "Regional (LiDAR) + Global (SRTM/ASTER)",
                "cost": "Free (with API key)",
                "available": bool(getattr(settings, 'opentopography_api_key', None)),
                "requires_api_key": True
            },
            "azure_maps": {
                "name": "Azure Maps Elevation API",
                "resolution": "Varies",
                "coverage": "Global",
                "cost": "Paid (with free tier)",
                "available": bool(getattr(settings, 'azure_maps_key', None)),
                "requires_api_key": True
            }
        },
        "imagery": {
            "sentinelhub": {
                "name": "Sentinel Hub",
                "resolution": "10m-60m",
                "coverage": "Global",
                "cost": "Paid (with trial)",
                "available": bool(getattr(settings, 'sentinelhub_client_id', None)),
                "requires_api_key": True
            }
        },
        "vector": {
            "openstreetmap": {
                "name": "OpenStreetMap",
                "type": "Vector (roads, buildings, POI)",
                "coverage": "Global",
                "cost": "Free",
                "available": True,
                "requires_api_key": False
            },
            "azure_maps": {
                "name": "Azure Maps",
                "type": "Vector + POI",
                "coverage": "Global",
                "cost": "Paid (with free tier)",
                "available": bool(getattr(settings, 'azure_maps_key', None)),
                "requires_api_key": True
            }
        }
    }


@app.get("/api/formats")
async def get_export_formats():
    """Get available export formats"""
    return {
        "formats": {
            "unreal5": {
                "name": "Unreal Engine 5",
                "description": "Landscape heightmaps, weightmaps, and splines",
                "files": ["heightmap.png", "weightmap.png", "metadata.json", "import_script.py"],
                "valid_resolutions": [1009, 2017, 4033, 8129],
                "supports_weightmaps": True,
                "supports_roads": True,
                "supports_buildings": True
            },
            "unity": {
                "name": "Unity Engine",
                "description": "Terrain heightmaps and prefabs",
                "files": ["heightmap.raw", "splatmap.png", "metadata.json", "import_script.cs"],
                "valid_resolutions": [513, 1025, 2049, 4097],
                "supports_weightmaps": True,
                "supports_roads": True,
                "supports_buildings": True
            },
            "gltf": {
                "name": "GLTF/GLB",
                "description": "3D mesh format (universal)",
                "files": ["terrain.glb", "metadata.json"],
                "valid_resolutions": "Any",
                "supports_weightmaps": False,
                "supports_roads": False,
                "supports_buildings": False
            },
            "geotiff": {
                "name": "GeoTIFF",
                "description": "Georeferenced raster for GIS software",
                "files": ["elevation.tif", "metadata.json"],
                "valid_resolutions": "Any",
                "supports_weightmaps": False,
                "supports_roads": False,
                "supports_buildings": False
            }
        }
    }


@app.post("/api/generate", response_model=GenerationStatus)
async def generate_terrain(
    request: MapGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start terrain generation process
    
    Args:
        request: Terrain generation request with bbox and options
        
    Returns:
        Generation status with task_id
    """
    logger.info(f"Received terrain generation request for '{request.name}'")
    logger.info(f"  Export formats: {[f.value for f in request.export_formats]}")
    logger.info(f"  Resolution: {request.resolution}")
    logger.info(f"  Elevation source: {request.elevation_source.value}")
    
    # Validate bbox
    area_km2 = request.bbox.area_km2()
    max_area = getattr(settings, 'max_area_km2', 100.0)
    if area_km2 > max_area:
        raise HTTPException(
            status_code=400,
            detail=f"Area too large: {area_km2:.2f} km² (max: {max_area} km²)"
        )
    
    if area_km2 <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid bounding box"
        )
    
    # Start generation and get task_id
    task_id = str(uuid.uuid4())
    
    # Register task immediately so it's available for status checks
    initial_status = GenerationStatus(
        task_id=task_id,
        status="pending",
        progress=0.0,
        current_step="Queued for processing",
        message=f"Map generation for '{request.name}' has been queued"
    )
    generator.active_tasks[task_id] = initial_status
    
    async def run_generation():
        try:
            logger.info(f"Background task starting for {task_id}")
            await generator.generate_terrain(request, task_id)
            logger.info(f"Background task completed for {task_id}")
        except Exception as e:
            import traceback
            logger.error(f"Background generation failed: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Update task status on error
            if task_id in generator.active_tasks:
                generator.active_tasks[task_id].status = "failed"
                generator.active_tasks[task_id].error = str(e)
    
    background_tasks.add_task(run_generation)
    
    # Return initial status
    return initial_status


@app.get("/api/status/{task_id}", response_model=GenerationStatus)
@app.get("/api/tasks/{task_id}", response_model=GenerationStatus)
async def get_generation_status(task_id: str):
    """
    Get status of a generation task
    
    Args:
        task_id: Task identifier
        
    Returns:
        Current status of the task
    """
    status = generator.get_task_status(task_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )
    
    return status


@app.get("/api/tasks")
async def list_tasks():
    """List all generation tasks"""
    tasks = await generator.list_tasks()
    return {
        "count": len(tasks),
        "tasks": tasks
    }


@app.get("/api/ollama/models")
async def list_ollama_models():
    """List available Ollama models"""
    try:
        models = await generator.list_ollama_models()
        return {
            "available": True,
            "models": models,
            "configured": {
                "vision": settings.ollama_vision_model,
                "coder": settings.ollama_coder_model
            }
        }
    except Exception as e:
        logger.error(f"Failed to list Ollama models: {e}")
        return {
            "available": False,
            "error": str(e)
        }


@app.post("/api/ollama/setup")
async def setup_ollama():
    """Pull required Ollama models"""
    try:
        results = await generator.setup_ollama_models()
        return {
            "success": all(results.values()),
            "results": results
        }
    except Exception as e:
        logger.error(f"Failed to setup Ollama: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to setup Ollama: {e}"
        )


@app.get("/api/maps")
async def list_maps():
    """List generated maps"""
    output_dir = settings.output_dir
    
    if not output_dir.exists():
        return {"maps": []}
    
    maps = []
    for map_dir in output_dir.iterdir():
        if map_dir.is_dir():
            info_file = map_dir / "info.json"
            if info_file.exists():
                import json
                with open(info_file) as f:
                    info = json.load(f)
                    maps.append(info)
    
    return {"maps": maps}


@app.get("/api/maps/{map_name}/download/{file_type}")
async def download_map_file(map_name: str, file_type: str):
    """
    Download a specific file from a generated map
    
    Args:
        map_name: Name of the map
        file_type: Type of file (heightmap, roads, objects, traffic, metadata, level, zip)
    """
    map_dir = settings.output_dir / map_name
    
    if not map_dir.exists():
        raise HTTPException(status_code=404, detail="Map not found")
    
    # Handle zip download
    if file_type == "zip":
        from ..packaging import BeamNGPackager
        
        packager = BeamNGPackager()
        
        # Check if zip already exists
        zip_path = settings.output_dir / f"{map_name}.zip"
        
        if not zip_path.exists():
            # Create zip package
            zip_path = packager.create_mod_package(
                map_dir,
                map_name,
                settings.output_dir
            )
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=zip_path.name
        )
    
    file_map = {
        "heightmap": f"{map_name}_heightmap.png",
        "roads": "roads.json",
        "objects": "objects.json",
        "traffic": "traffic.json",
        "metadata": "info.json",
        "level": "main.level.json"
    }
    
    if file_type not in file_map:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_path = map_dir / file_map[file_type]
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=file_path.name
    )


@app.post("/api/batch/generate")
async def batch_generate(requests: List[MapGenerationRequest]):
    """
    Generate multiple maps in batch
    
    Args:
        requests: List of map generation requests
        
    Returns:
        List of task IDs for tracking progress
    """
    logger.info(f"Starting batch generation of {len(requests)} maps")
    
    task_ids = []
    
    for request in requests:
        try:
            status = await generator.generate_map(request)
            task_ids.append({
                "name": request.name,
                "task_id": status.task_id,
                "status": status.status
            })
        except Exception as e:
            logger.error(f"Failed to start generation for {request.name}: {e}")
            task_ids.append({
                "name": request.name,
                "error": str(e)
            })
    
    return {
        "batch_id": str(uuid.uuid4()),
        "total": len(requests),
        "tasks": task_ids
    }


@app.post("/api/test/generate")
async def test_generate():
    """Test endpoint with sample coordinates"""
    # Sample area: small section in San Francisco
    test_request = MapGenerationRequest(
        name="test_map",
        bbox=BoundingBox(
            north=37.8,
            south=37.79,
            east=-122.4,
            west=-122.41
        ),
        resolution=1024,
        export_engine="beamng",
        enable_ai_analysis=True,
        enable_roads=True,
        enable_traffic_lights=True,
        enable_parking=True,
        enable_buildings=True,
        enable_vegetation=True
    )
    
    status = await generator.generate_map(test_request)
    return status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
