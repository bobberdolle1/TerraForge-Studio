#!/usr/bin/env python3
"""
Simple script to create .env file
"""

ENV_CONTENT = """# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_VISION_MODEL=llama3.2-vision
OLLAMA_CODER_MODEL=qwen2.5-coder
OLLAMA_TIMEOUT=300

# Output Configuration
OUTPUT_DIR=output
CACHE_DIR=cache

# Map Generation Settings
DEFAULT_RESOLUTION=2048
DEFAULT_SCALE=1.0
MAX_AREA_KM2=100.0

# OSM Settings
OSM_CACHE_ENABLED=true
OSM_TIMEOUT=180

# Elevation Data
ELEVATION_SOURCE=SRTM3

# BeamNG.drive Export Settings
BEAMNG_TERRAIN_SIZE=2048
BEAMNG_HEIGHT_SCALE=1.0

# Processing Settings
ENABLE_AI_ANALYSIS=true
ENABLE_SATELLITE_IMAGERY=true
PARALLEL_PROCESSING=true
MAX_WORKERS=4
"""

if __name__ == "__main__":
    import os
    import sys
    
    # Check if force flag is provided
    force = "--force" in sys.argv or "-f" in sys.argv
    
    if os.path.exists(".env") and not force:
        print(".env file already exists!")
        print("Use --force or -f to overwrite")
        exit(1)
    
    with open(".env", "w") as f:
        f.write(ENV_CONTENT)
    
    print("[OK] .env file created successfully!")
    print("\nNext steps:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Pull required models:")
    print("   ollama pull llama3.2-vision")
    print("   ollama pull qwen2.5-coder")
    print("3. Start the application:")
    print("   docker-compose up --build")
    print("   OR")
    print("   poetry run uvicorn realworldmapgen.api.main:app --reload")

