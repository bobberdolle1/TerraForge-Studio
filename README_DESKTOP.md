# 🌍 TerraForge Studio - Desktop Application

<div align="center">

![TerraForge Studio](https://img.shields.io/badge/TerraForge-Studio-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-orange?style=for-the-badge)

**Professional 3D Terrain Generator from Real-World Map Data**

[Features](#-features) • [Download](#-download) • [Build](#-building-from-source) • [Documentation](#-documentation)

</div>

---

## 🎯 Overview

TerraForge Studio is a professional desktop application for generating 3D terrain from real-world map data. Built with modern technologies (FastAPI + React + pywebview), it provides a native Windows experience similar to industry-standard applications like Gyroflow, Blender, or Unity.

### ✨ Key Features

- 🗺️ **Real-World Data** - OpenStreetMap, SRTM elevation, satellite imagery
- 🎮 **Game Engine Export** - Unreal Engine 5, Unity, GLTF, GeoTIFF
- 🌍 **3D Preview** - Built-in Cesium-based 3D viewer
- 🚀 **Portable** - No installation required, runs from folder
- 💻 **Native UI** - Professional Windows application with Edge WebView2
- 🔒 **Offline Mode** - Works without internet (with cached data)

---

## 📥 Download

### Latest Release

Download the latest version from [Releases](https://github.com/yourusername/TerraForge-Studio/releases):

```
TerraForge-Studio-v1.0.0-Windows-x64.zip  (~250 MB)
```

### System Requirements

- **OS:** Windows 10/11 (64-bit)
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 500MB free space
- **Internet:** Required for downloading map data

---

## 🚀 Quick Start

### For End Users

1. **Download** the ZIP from releases
2. **Extract** to any folder (e.g., `C:\TerraForge Studio`)
3. **Run** `TerraForge Studio.exe`
4. **Generate** your first terrain!

### First Run

On first launch, the application will:
- Create `cache/` and `output/` directories
- Start local backend server (port 8000 or auto-detect)
- Open native window with React UI

---

## 🏗️ Building from Source

### Prerequisites

```powershell
# Check versions
python --version  # Python 3.13+ required
node --version    # Node.js 20+ required
```

### Install Dependencies

```powershell
# Option 1: Automatic (recommended)
.\desktop\install_deps.ps1

# Option 2: Manual
pip install pyinstaller pillow
pip install bottle proxy-tools typing-extensions
pip install pywebview --no-deps  # Skip pythonnet (not compatible with Python 3.14)
```

### Build Application

```powershell
# Full automated build
.\desktop\build.ps1

# Or use Python script
python desktop\build.py
```

### Output

```
desktop/dist/TerraForge Studio/
├── TerraForge Studio.exe    # Main executable
├── README.txt               # User guide
├── LICENSE.txt              # MIT License
├── .env.example             # Configuration template
└── _internal/               # Dependencies (don't modify)
```

---

## 📖 Documentation

- 📘 [Desktop Build Guide](DESKTOP_BUILD_GUIDE.md) - Detailed build instructions
- 🚀 [Quick Start Guide](QUICK_START_DESKTOP.md) - Fast setup
- 🔧 [Desktop README](desktop/README.md) - Technical details
- 📝 [API Documentation](docs/API_SPECIFICATION.md) - Backend API
- 🐛 [Troubleshooting](desktop/INSTALL_INSTRUCTIONS.md) - Common issues

---

## 🎨 Features in Detail

### Real-World Data Sources

| Source | Type | Resolution | Cost | Coverage |
|--------|------|------------|------|----------|
| **OpenStreetMap** | Vector | - | Free | Global |
| **SRTM** | Elevation | 30m-90m | Free | Global |
| **Sentinel Hub** | Imagery | 10m-60m | Paid/Trial | Global |
| **OpenTopography** | Elevation | 0.5m-30m | Free w/ API | Regional |

### Export Formats

- **Unreal Engine 5** - Heightmaps, weightmaps, splines, import scripts
- **Unity** - RAW heightmaps, splatmaps, prefabs, C# scripts
- **GLTF/GLB** - Universal 3D mesh format
- **GeoTIFF** - Georeferenced rasters for GIS

### Advanced Features

- ⚡ **Batch Processing** - Generate multiple terrains
- 🤖 **AI Analysis** - Terrain classification (optional, requires Ollama)
- 🌐 **Multi-language** - English, Russian, Chinese (coming soon)
- 📊 **Progress Tracking** - Real-time generation status
- 💾 **Caching** - Intelligent data caching for faster regeneration

---

## ⚙️ Configuration

Create `.env` file next to the executable:

```ini
# Premium Data Sources (Optional)
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret
OPENTOPOGRAPHY_API_KEY=your_api_key
AZURE_MAPS_KEY=your_api_key

# AI Features (Optional, requires Ollama)
OLLAMA_HOST=http://localhost:11434
OLLAMA_VISION_MODEL=llava
OLLAMA_CODER_MODEL=codellama

# Application Settings
MAX_AREA_KM2=100
DEFAULT_RESOLUTION=2048
CACHE_ENABLED=true
```

---

## 🔧 Development

### Project Structure

```
TerraForge-Studio/
├── desktop/              # Desktop application
│   ├── launcher.py       # Main entry point
│   ├── build.py          # Build automation
│   ├── terraforge.spec   # PyInstaller config
│   └── install_deps.ps1  # Dependency installer
├── frontend-new/         # React UI
│   ├── src/
│   └── package.json
├── realworldmapgen/      # Python backend
│   ├── api/              # FastAPI routes
│   ├── core/             # Core logic
│   └── elevation/        # Elevation processing
└── requirements.txt      # Python dependencies
```

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Cesium (3D viewer)
- Leaflet (2D maps)

**Backend:**
- FastAPI (Python 3.13+)
- NumPy, SciPy (scientific computing)
- GeoPandas, Shapely (geospatial)
- OSMnx (OpenStreetMap)

**Desktop:**
- pywebview (native window)
- PyInstaller (executable packaging)
- Edge WebView2 (rendering)

---

## 🐛 Troubleshooting

### Common Issues

**❌ "pythonnet не устанавливается"**

pythonnet несовместим с Python 3.14. Решение:
```powershell
pip install pywebview --no-deps
```

**❌ "Порт 8000 занят"**

Launcher автоматически найдёт свободный порт. Проверьте Task Manager на наличие других процессов.

**❌ "Frontend не собирается"**

```powershell
cd frontend-new
rm -rf node_modules package-lock.json
npm install
npm run build
```

**❌ "Exe не запускается"**

Запустите из командной строки для диагностики:
```powershell
"desktop\dist\TerraForge Studio\TerraForge Studio.exe"
```

---

## 🚢 Creating Releases

### Manual Release

```powershell
# 1. Build application
.\desktop\build.ps1

# 2. Create ZIP
Compress-Archive -Path "desktop\dist\TerraForge Studio" -DestinationPath "TerraForge-Studio-v1.0.0-Windows-x64.zip"

# 3. Calculate checksum
Get-FileHash TerraForge-Studio-v1.0.0-Windows-x64.zip -Algorithm SHA256 > checksum.txt
```

### Automated Release (GitHub Actions)

```bash
# Tag version
git tag v1.0.0
git push origin v1.0.0

# Workflow automatically:
# - Builds frontend
# - Creates executable
# - Generates checksums
# - Creates GitHub Release
# - Uploads artifacts
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```powershell
# 1. Clone repository
git clone https://github.com/yourusername/TerraForge-Studio.git
cd TerraForge-Studio

# 2. Install dependencies
pip install -r requirements.txt
cd frontend-new && npm install && cd ..

# 3. Run development servers
# Terminal 1 - Backend
python -m uvicorn realworldmapgen.api.main:app --reload

# Terminal 2 - Frontend
cd frontend-new && npm run dev
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenStreetMap** - Community-driven map data
- **NASA SRTM** - Global elevation data
- **Cesium** - 3D geospatial visualization
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **pywebview** - Python desktop apps

---

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/TerraForge-Studio/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/TerraForge-Studio/discussions)
- 📧 **Email:** contact@terraforge.dev (placeholder)

---

<div align="center">

**Made with ❤️ by the TerraForge Team**

⭐ **Star us on GitHub if you like this project!** ⭐

</div>
