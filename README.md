# 🗺️ RealWorldMapGen-BNG

**AI-Powered Real-World Map Generator for BeamNG.drive**

A comprehensive tool for generating detailed and functional maps of real-world locations for BeamNG.drive, featuring automated infrastructure generation (roads, traffic lights, parking, buildings, vegetation) powered by AI analysis of satellite imagery and OpenStreetMap data.

## ✨ Features

- 🌍 **Real-World Data Integration**: Extract geographic data from OpenStreetMap for any location
- 🤖 **AI-Powered Analysis**: Uses Qwen3-VL and Qwen3-Coder via Ollama for intelligent terrain analysis
- 🏔️ **Heightmap Generation**: Creates detailed elevation data from SRTM sources
- 🛣️ **Road Network Generation**: Automatically generates roads with proper types, lanes, and materials
- 🚦 **Traffic Infrastructure**: Places traffic lights and creates parking lots based on OSM data
- 🏢 **Building Placement**: Extracts and positions buildings with height information
- 🌳 **Vegetation Distribution**: Generates trees and vegetation areas based on terrain analysis
- 🎮 **BeamNG.drive Export**: Outputs all data in BeamNG.drive-compatible formats
- 🌐 **Web Interface**: Interactive map selection with Leaflet integration
- 🐳 **Docker Support**: Fully containerized with Docker Compose

## 🏗️ Architecture

```
RealWorldMapGen-BNG/
├── realworldmapgen/          # Core Python package
│   ├── ai/                   # AI integration (Ollama)
│   │   ├── ollama_client.py  # Ollama API client
│   │   └── terrain_analyzer.py # AI terrain analysis
│   ├── osm/                  # OpenStreetMap extraction
│   │   └── osm_extractor.py  # OSM data extractor using osmnx
│   ├── elevation/            # Heightmap generation
│   │   └── heightmap_generator.py
│   ├── exporters/            # BeamNG.drive exporters
│   │   └── beamng_exporter.py
│   ├── api/                  # FastAPI backend
│   │   └── main.py           # API endpoints
│   ├── config.py             # Configuration management
│   ├── models.py             # Data models (Pydantic)
│   └── generator.py          # Main orchestrator
├── frontend/                 # Web interface
│   ├── index.html            # Main HTML
│   ├── style.css             # Styling
│   └── app.js                # Frontend logic
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Python backend container
├── pyproject.toml            # Poetry dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.13+** (for local development)
- **Poetry** (for dependency management)
- **Git**

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd RealWorldMapGen-BNG
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - Ollama server (port 11434)
   - Python backend (port 8000)
   - Frontend web interface (port 8080)

3. **Pull required AI models** (first time only):
   ```bash
   docker exec -it realworldmapgen-ollama ollama pull qwen3-vl:235b-cloud
   docker exec -it realworldmapgen-ollama ollama pull qwen3-coder:480b-cloud
   ```

4. **Access the web interface**:
   Open your browser and navigate to: `http://localhost:8080`

### Option 2: Local Development

1. **Install Poetry**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Install and start Ollama** (separate terminal):
   ```bash
   # Download from https://ollama.ai
   ollama serve
   ollama pull qwen3-vl:235b-cloud
   ollama pull qwen3-coder:480b-cloud
   ```

5. **Run the backend**:
   ```bash
   poetry run uvicorn realworldmapgen.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Serve the frontend** (separate terminal):
   ```bash
   cd frontend
   python -m http.server 8080
   ```

## 📖 Usage

### Web Interface

1. **Open the web interface** at `http://localhost:8080`
2. **Select an area** on the map by using the rectangle tool
3. **Configure options**:
   - Map name
   - Heightmap resolution
   - Enable/disable features (AI, roads, traffic, buildings, etc.)
4. **Click "Generate Map"**
5. **Download the generated files** when complete

### API Usage

#### Generate a Map

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_map",
    "bbox": {
      "north": 37.8,
      "south": 37.79,
      "east": -122.4,
      "west": -122.41
    },
    "resolution": 2048,
    "enable_ai_analysis": true,
    "enable_roads": true,
    "enable_traffic_lights": true,
    "enable_parking": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

#### Check System Health

```bash
curl http://localhost:8000/api/health
```

#### List Generated Maps

```bash
curl http://localhost:8000/api/maps
```

#### Download Map Files

```bash
curl -O http://localhost:8000/api/maps/my_map/download/heightmap
curl -O http://localhost:8000/api/maps/my_map/download/roads
curl -O http://localhost:8000/api/maps/my_map/download/objects
curl -O http://localhost:8000/api/maps/my_map/download/traffic
```

## 🎮 Importing to BeamNG.drive

1. **Locate your generated map** in the `output/<map_name>/` directory
2. **Copy the files** to your BeamNG.drive levels directory:
   ```
   <BeamNG.drive>/levels/<map_name>/
   ```
3. **Required files**:
   - `main.level.json` - Main level configuration
   - `<map_name>_heightmap.png` - Terrain heightmap
   - `roads.json` - Road network data
   - `objects.json` - Buildings and vegetation
   - `traffic.json` - Traffic lights and parking
   - `info.json` - Map metadata

4. **Launch BeamNG.drive** and load your custom map

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_VISION_MODEL=qwen3-vl:235b-cloud
OLLAMA_CODER_MODEL=qwen3-coder:480b-cloud

# Map Generation Settings
DEFAULT_RESOLUTION=2048
MAX_AREA_KM2=100.0

# Processing Settings
ENABLE_AI_ANALYSIS=true
PARALLEL_PROCESSING=true
MAX_WORKERS=4
```

## 🛠️ Development

### Project Structure

- **AI Module** (`realworldmapgen/ai/`): Handles Ollama integration and terrain analysis
- **OSM Module** (`realworldmapgen/osm/`): Extracts OpenStreetMap data using osmnx
- **Elevation Module** (`realworldmapgen/elevation/`): Generates heightmaps from elevation data
- **Exporters** (`realworldmapgen/exporters/`): Converts data to BeamNG.drive formats
- **API** (`realworldmapgen/api/`): FastAPI backend with REST endpoints
- **Generator** (`realworldmapgen/generator.py`): Main orchestration logic

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black realworldmapgen/
poetry run ruff check realworldmapgen/
```

### Type Checking

```bash
poetry run mypy realworldmapgen/
```

## 📦 Dependencies

### Core Dependencies

- **FastAPI** - Modern web framework
- **osmnx** - OpenStreetMap data extraction
- **ollama** - AI model integration
- **geopandas** - Geospatial data processing
- **numpy** - Numerical computing
- **Pillow** - Image processing
- **rasterio** - Raster data I/O

### AI Models

- **Qwen3-VL:235B-Cloud** - Vision model for satellite image analysis
- **Qwen3-Coder:480B-Cloud** - Code generation and optimization

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 TODO / Roadmap

- [ ] Implement actual satellite imagery download and analysis
- [ ] Add support for custom object prefabs
- [ ] Implement traffic route generation
- [ ] Add support for custom textures and materials
- [ ] Create map preview generation
- [ ] Add batch processing for multiple areas
- [ ] Implement incremental updates to existing maps
- [ ] Add support for other game engines (Unreal, Unity)
- [ ] Create standalone CLI tool
- [ ] Add map quality validation

## 🐛 Known Issues

- **Large areas**: Processing areas >50 km² may require significant memory
- **Ollama models**: Initial model downloads are large (50GB+ total)
- **OSM rate limits**: Very frequent requests may be rate-limited
- **Elevation data**: First-time downloads can be slow

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Inspired by [unrealheightmap](https://github.com/manticorp/unrealheightmap)
- Built with [osmnx](https://github.com/gboeing/osmnx) by Geoff Boeing
- Powered by [Ollama](https://ollama.ai) and Qwen models
- Map data © [OpenStreetMap](https://www.openstreetmap.org) contributors

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for the BeamNG.drive community**
