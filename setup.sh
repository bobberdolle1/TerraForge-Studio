#!/bin/bash

# RealWorldMapGen-BNG Setup Script

echo "🗺️  RealWorldMapGen-BNG Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose found"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created. You can customize it if needed."
else
    echo "✓ .env file already exists"
fi
echo ""

# Create output and cache directories
echo "📁 Creating output and cache directories..."
mkdir -p output cache
echo "✓ Directories created"
echo ""

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if Ollama is running
echo "🔍 Checking Ollama status..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "⚠️  Ollama is not responding yet. It may still be starting up."
fi

echo ""
echo "📥 Pulling required AI models (this may take a while)..."
echo "   Note: Total download size is ~50GB+"
echo ""

# Pull Qwen3-VL model
echo "Pulling qwen3-vl:235b-cloud..."
docker exec realworldmapgen-ollama ollama pull qwen3-vl:235b-cloud

# Pull Qwen3-Coder model
echo "Pulling qwen3-coder:480b-cloud..."
docker exec realworldmapgen-ollama ollama pull qwen3-coder:480b-cloud

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost:8080"
echo "   API:      http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
