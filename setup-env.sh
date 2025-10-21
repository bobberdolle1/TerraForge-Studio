#!/bin/bash

# Shell script to setup .env file for Linux/Mac users

echo "🚀 RealWorldMapGen-BNG Environment Setup"
echo "========================================"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

# Create .env file
cat > .env << 'EOF'
# Ollama Configuration
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
EOF

echo "✅ .env file created successfully!"
echo ""

# Check if Ollama is installed
echo "🔍 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed: $(ollama --version)"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running"
        
        # List available models
        echo ""
        echo "📦 Checking available models..."
        ollama list
        
        # Check for required models
        if ollama list | grep -q "llama3.2-vision"; then
            echo "✅ Vision model available"
        else
            echo "⚠️  Vision model not found. Pull it with:"
            echo "   ollama pull llama3.2-vision"
        fi
        
        if ollama list | grep -q "qwen2.5-coder"; then
            echo "✅ Coder model available"
        else
            echo "⚠️  Coder model not found. Pull it with:"
            echo "   ollama pull qwen2.5-coder"
        fi
    else
        echo "⚠️  Ollama is not running. Start it with: ollama serve"
    fi
else
    echo "❌ Ollama is not installed!"
    echo "   Install from: https://ollama.ai"
fi

echo ""
echo "📝 Next steps:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Pull required models:"
echo "   ollama pull llama3.2-vision"
echo "   ollama pull qwen2.5-coder"
echo "3. Start the application:"
echo "   docker-compose up --build"
echo "   OR"
echo "   poetry install && poetry run uvicorn realworldmapgen.api.main:app"
echo ""
echo "✨ Setup complete!"

