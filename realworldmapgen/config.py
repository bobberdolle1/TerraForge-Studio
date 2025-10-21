"""
Configuration management for RealWorldMapGen-BNG
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Ollama configuration
    ollama_host: str = "http://localhost:11434"
    ollama_vision_model: str = "qwen3-vl:235b-cloud"
    ollama_coder_model: str = "qwen3-coder:480b-cloud"
    ollama_timeout: int = 300  # seconds
    
    # Output configuration
    output_dir: Path = Path("output")
    cache_dir: Path = Path("cache")
    
    # Map generation settings
    default_resolution: int = 2048  # heightmap resolution
    default_scale: float = 1.0  # meters per pixel
    max_area_km2: float = 100.0  # maximum area in square kilometers
    
    # OSM settings
    osm_cache_enabled: bool = True
    osm_timeout: int = 180
    
    # Elevation data
    elevation_source: str = "SRTM3"  # SRTM1, SRTM3, or ASTER
    
    # BeamNG.drive export settings
    beamng_terrain_size: int = 2048
    beamng_height_scale: float = 1.0
    
    # Processing settings
    enable_ai_analysis: bool = True
    enable_satellite_imagery: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def ensure_directories():
    """Create necessary directories if they don't exist"""
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
