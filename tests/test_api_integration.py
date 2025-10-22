"""
TerraForge Studio - API Integration Tests
Tests for backend API endpoints
"""

import pytest
import httpx


BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_api_root():
    """Test API root endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TerraForge Studio"
        assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_api_health():
    """Test health check endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "data_sources" in data


@pytest.mark.asyncio
async def test_api_sources():
    """Test data sources endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert "elevation" in data
        assert "imagery" in data
        assert "vector" in data


@pytest.mark.asyncio
async def test_api_formats():
    """Test export formats endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/formats")
        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        assert "unreal5" in data["formats"]
        assert "unity" in data["formats"]
        assert "gltf" in data["formats"]
        assert "geotiff" in data["formats"]


@pytest.mark.asyncio
async def test_generate_terrain_missing_bbox():
    """Test terrain generation with missing bbox"""
    async with httpx.AsyncClient() as client:
        payload = {
            "name": "test",
            "resolution": 2048,
            "export_formats": ["unreal5"]
        }
        response = await client.post(f"{BASE_URL}/api/generate", json=payload)
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_generate_terrain_valid():
    """Test terrain generation with valid request"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "name": "test_terrain",
            "bbox": {
                "north": 40.76,
                "south": 40.75,
                "east": -73.98,
                "west": -73.99
            },
            "resolution": 1009,
            "export_formats": ["unreal5"],
            "elevation_source": "auto",
            "enable_roads": True,
            "enable_buildings": True,
            "enable_weightmaps": True
        }
        response = await client.post(f"{BASE_URL}/api/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] in ["pending", "processing"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

