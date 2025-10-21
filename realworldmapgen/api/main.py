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
    MapGenerationRequest, GenerationStatus, BoundingBox
)
from ..generator import MapGenerator
from ..config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RealWorldMapGen-BNG",
    description="AI-powered real-world map generator for BeamNG.drive",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global generator instance
generator = MapGenerator()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting RealWorldMapGen-BNG API")
    
    # Check Ollama health
    ollama_status = await generator.check_ollama_health()
    if ollama_status:
        logger.info("✓ Ollama is available")
        
        # List available models
        models = await generator.list_ollama_models()
        logger.info(f"Available Ollama models: {models}")
    else:
        logger.warning("✗ Ollama is not available - AI features will be limited")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "RealWorldMapGen-BNG",
        "version": "0.1.0",
        "description": "AI-powered real-world map generator for BeamNG.drive",
        "endpoints": {
            "generate": "/api/generate",
            "status": "/api/status/{task_id}",
            "tasks": "/api/tasks",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    ollama_available = await generator.check_ollama_health()
    
    return {
        "status": "healthy",
        "ollama": {
            "available": ollama_available,
            "host": settings.ollama_host
        },
        "settings": {
            "max_area_km2": settings.max_area_km2,
            "default_resolution": settings.default_resolution,
            "ai_enabled": settings.enable_ai_analysis
        }
    }


@app.post("/api/generate", response_model=GenerationStatus)
async def generate_map(
    request: MapGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start map generation process
    
    Args:
        request: Map generation request with bbox and options
        
    Returns:
        Generation status with task_id
    """
    logger.info(f"Received generation request for '{request.name}'")
    
    # Validate bbox
    area_km2 = request.bbox.area_km2()
    if area_km2 > settings.max_area_km2:
        raise HTTPException(
            status_code=400,
            detail=f"Area too large: {area_km2:.2f} km² (max: {settings.max_area_km2} km²)"
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
            await generator.generate_map(request, task_id)
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
    status = await generator.get_status(task_id)
    
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
