# 🌍 TerraForge Studio

**Professional Cross-Platform 3D Terrain Generator**

Generate real-world terrains for Unreal Engine 5, Unity, and other platforms using satellite imagery and elevation data.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🎮 Multi-Engine Support
- **Unreal Engine 5** - Landscape heightmaps + weightmaps + Python import scripts
- **Unity** - Terrain heightmaps + splatmaps + C# import scripts  
- **GLTF/GLB** - Universal 3D meshes for Blender, Three.js, AR/VR
- **GeoTIFF** - Georeferenced rasters for QGIS, ArcGIS

### 🌍 Data Sources
- **OpenStreetMap** - Roads, buildings, POI (free)
- **SRTM** - Global elevation data 30-90m (free)
- **OpenTopography** - High-resolution DEMs 0.5-30m (free with API key)
- **Sentinel Hub** - Satellite imagery 10-60m (paid)
- **Azure Maps** - Vector data + elevation (paid)
- **Google Earth Engine** - Advanced analysis (free with auth)

### 🎨 Modern Interface
- **React 18 + TypeScript** - Professional UI
- **Interactive Maps** - Leaflet with drawing tools
- **3D Preview** - CesiumJS integration (ready)
- **Settings UI** - Secure API key management
- **Setup Wizard** - 3-step onboarding

### 🔐 Security & Settings
- **Encrypted Storage** - API keys stored securely
- **UI Management** - No manual .env editing
- **Connection Testing** - Validate data sources
- **Import/Export** - Share configurations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Poetry (for Python dependencies)

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd TerraForge-Studio

# 2. Install Python dependencies
poetry install

# 3. Install frontend dependencies
cd frontend-new
npm install
cd ..

# 4. Copy environment template
cp .env.example .env
```

### Running

```bash
# Terminal 1: Start backend
poetry run uvicorn realworldmapgen.api.main:app --reload

# Terminal 2: Start frontend
cd frontend-new
npm run dev

# Open browser: http://localhost:3000
```

### First Use

1. **Setup Wizard** - Complete 3 steps (language, API keys, default engine)
2. **Select Area** - Draw rectangle on map
3. **Configure** - Choose format, resolution, features
4. **Generate** - Wait 2-10 minutes
5. **Download** - Get ZIP with terrain files
6. **Import** - Use auto-import scripts in your game engine

---

## 📖 Documentation

### User Guides
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - 5-minute quick start
- **[docs/RUN_INSTRUCTIONS.md](docs/RUN_INSTRUCTIONS.md)** - Detailed setup guide
- **[docs/SETTINGS_GUIDE.md](docs/SETTINGS_GUIDE.md)** - Configure API keys and settings

### Technical
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Installation guide
- **[docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)** - API usage examples
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Development guide

### API Documentation
- **Swagger UI**: http://localhost:8000/docs (when running)
- **ReDoc**: http://localhost:8000/redoc (when running)

---

## 🎯 Use Cases

### Game Development
- Generate realistic terrains for open-world games
- Import to UE5 or Unity with one click
- Auto-generated material layers
- Road networks included

### Virtual Reality
- Create immersive environments
- Real-world locations
- High-resolution heightmaps
- GLTF for web-based VR

### GIS Analysis
- Export as GeoTIFF
- Analyze in QGIS/ArcGIS
- Georeferenced data
- Proper CRS support

### Architectural Visualization
- Real-world site context
- Accurate elevations
- Building footprints
- Import to visualization software

---

## 🏗️ Architecture

```
TerraForge Studio/
├── realworldmapgen/          # Python backend
│   ├── core/                 # Data sources & generation
│   ├── exporters/            # Multi-format export
│   ├── settings/             # Secure configuration
│   └── api/                  # FastAPI endpoints
├── frontend-new/             # React frontend
│   ├── src/components/        # UI components
│   ├── src/services/         # API clients
│   └── src/types/            # TypeScript definitions
├── docs/                     # Documentation
└── tests/                    # Automated tests
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Data Sources (optional)
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret
OPENTOPOGRAPHY_API_KEY=your_api_key
AZURE_MAPS_SUBSCRIPTION_KEY=your_subscription_key

# Generation Settings
DEFAULT_RESOLUTION=2048
MAX_AREA_KM2=100.0
CACHE_DIR=./cache
OUTPUT_DIR=./output
```

### Settings UI

Configure via web interface:
1. Open http://localhost:3000
2. Click "Settings" (top-right)
3. Configure data sources, generation defaults, export profiles
4. Test connections and save

---

## 📊 Performance

### Generation Time
- **Small area (5 km²)**: ~2 minutes
- **Medium area (25 km²)**: ~10 minutes  
- **Large area (100 km²)**: ~30 minutes

### Supported Scales
- **Minimum**: 1 km² @ 512px
- **Maximum**: 500 km² @ 8192px
- **Recommended**: 10-25 km² @ 2048px

### File Sizes
- **UE5 PNG**: ~8 MB (2048px)
- **Unity RAW**: ~8 MB (2048px)
- **GLTF**: ~20 MB (2048px)
- **GeoTIFF**: ~8 MB (2048px)

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Frontend tests
pytest tests/test_frontend.py -v

# API tests
pytest tests/test_api_integration.py -v
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenStreetMap** community for free vector data
- **NASA** for SRTM elevation data
- **Sentinel Hub** for satellite imagery
- **OpenTopography** for high-resolution DEMs
- **React** and **FastAPI** communities
- **unrealheightmap** project for inspiration

---

## 📞 Support

- **Documentation**: [docs/](docs/) folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **API Docs**: http://localhost:8000/docs

---

<div align="center">

# 🌍 Generate Amazing Terrains!

**Professional 3D Terrain Generation Made Easy**

[Get Started](docs/QUICKSTART.md) • [Documentation](docs/) • [API Reference](http://localhost:8000/docs)

---

*TerraForge Studio v1.0.0*  
*Professional Cross-Platform 3D Terrain Generator*

</div>