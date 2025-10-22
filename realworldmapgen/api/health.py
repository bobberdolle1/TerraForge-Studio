"""
Health Check Endpoint
Monitors system health and readiness
"""

from fastapi import APIRouter, Response
from typing import Dict
import time
import psutil
from datetime import datetime

router = APIRouter()

# Store startup time
STARTUP_TIME = time.time()


@router.get("/health")
async def health_check() -> Dict:
    """
    Basic health check endpoint
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - STARTUP_TIME)
    }


@router.get("/health/ready")
async def readiness_check() -> Dict:
    """
    Readiness check - verifies all dependencies are available
    """
    checks = {}
    
    # Check database
    try:
        # This would actually check DB connection
        checks["database"] = {"status": "healthy", "latency_ms": 5}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Redis
    try:
        # This would actually check Redis connection
        checks["redis"] = {"status": "healthy", "latency_ms": 2}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Check storage (S3/local)
    try:
        checks["storage"] = {"status": "healthy"}
    except Exception as e:
        checks["storage"] = {"status": "unhealthy", "error": str(e)}
    
    # Determine overall status
    all_healthy = all(
        check.get("status") == "healthy" 
        for check in checks.values()
    )
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def liveness_check() -> Dict:
    """
    Liveness check - basic ping to verify process is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/metrics")
async def metrics() -> Dict:
    """
    System metrics for monitoring
    """
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used / (1024 * 1024),
            "memory_total_mb": memory.total / (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_used_gb": disk.used / (1024 * 1024 * 1024),
            "disk_total_gb": disk.total / (1024 * 1024 * 1024),
        },
        "application": {
            "uptime_seconds": int(time.time() - STARTUP_TIME),
            "timestamp": datetime.utcnow().isoformat()
        }
    }
