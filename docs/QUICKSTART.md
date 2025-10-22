# 🚀 TerraForge Studio - Quick Start Guide

## ⚡ Quick Installation

### Windows (PowerShell)

```powershell
# 1. Clone repository
git clone https://github.com/yourusername/TerraForge-Studio.git
cd TerraForge-Studio

# 2. Application management
.\run.ps1          # Start (auto-install)
.\run.ps1 stop     # Stop
.\run.ps1 restart  # Restart
.\run.ps1 status   # Check status
```

### Linux/Mac

```bash
# 1. Clone repository
git clone https://github.com/yourusername/TerraForge-Studio.git
cd TerraForge-Studio

# 2. Application management
chmod +x run.sh
./run.sh          # Start (auto-install)
./run.sh stop     # Stop
./run.sh restart  # Restart
./run.sh status   # Check status
```

## 📋 Prerequisites

**Required:**
- **Python 3.13+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)

**Optional (for advanced features):**
- **Ollama** (AI terrain analysis) - [Download](https://ollama.ai)
- **GDAL** (advanced geospatial processing)

## 🔑 API Keys Setup

TerraForge Studio works with free data sources (OpenStreetMap + SRTM) out of the box. For enhanced data quality, configure optional API keys:

### 1. Copy environment file

```bash
cp .env.example .env
```

### 2. Add API keys (optional)

Edit `.env` file:

```env
# Sentinel Hub (Satellite Imagery)
# Sign up: https://www.sentinel-hub.com/
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_secret
SENTINELHUB_ENABLED=true

# OpenTopography (High-res DEMs)
# Sign up: https://opentopography.org/
OPENTOPOGRAPHY_API_KEY=your_api_key
OPENTOPOGRAPHY_ENABLED=true

# Azure Maps (Vector data)
# Sign up: https://azure.microsoft.com/services/azure-maps/
AZURE_MAPS_SUBSCRIPTION_KEY=your_key
AZURE_MAPS_ENABLED=true

# Google Earth Engine (Advanced analysis)
# Setup: https://developers.google.com/earth-engine/
GOOGLE_EARTH_ENGINE_ENABLED=false  # Requires service account
```

**Note:** All API keys are optional. The system will automatically fallback to free OpenStreetMap + SRTM data if premium sources are unavailable.

## 🎮 First Terrain Generation

### Step 1: Start Application

```bash
# Backend + Frontend will start automatically
./run.sh  # or .\run.ps1 on Windows
```

Access:
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Step 2: Select Area

1. Open http://localhost:3000
2. Use search bar to find a location (e.g., "Grand Canyon")
3. Select drawing tool:
   - 🔲 **Rectangle** - Click and drag
   - 🔺 **Polygon** - Click points to draw shape
   - ⭕ **Circle** - Click center and drag radius

### Step 3: Configure Export

Choose your target game engine:

**For Unreal Engine 5:**
```
Engine: Unreal Engine 5
Resolution: 2017 (recommended for UE5)
Format: 16-bit PNG
Export weightmaps: ✅ Yes
Export splines: ✅ Yes
```

**For Unity:**
```
Engine: Unity
Resolution: 2049 (recommended for Unity)
Format: RAW 16-bit
Export splatmaps: ✅ Yes
Export prefabs: ✅ Yes
```

**For Generic/Other:**
```
Engine: Generic
Format: GLTF + GeoTIFF
Resolution: 2048
```

### Step 4: Generate

1. Click **"🚀 Generate Terrain"**
2. View progress in real-time
3. Preview in 3D viewer (if enabled)
4. Download ZIP package when complete

## 📥 Importing to Game Engines

### Unreal Engine 5

1. Extract downloaded ZIP to `YourProject/Content/Terrains/`
2. In Unreal Editor:
   ```
   Landscape Mode → Import from File
   → Select heightmap_16bit.png
   → Section Size: 127x127
   → Sections Per Component: 1
   → Number of Components: 16x16 (for 2017x2017)
   ```
3. Apply material weightmaps:
   ```
   Landscape Material → Weight Blended Layers
   → Import weightmap_R.png (Rock)
   → Import weightmap_G.png (Grass)
   → Import weightmap_B.png (Dirt)
   → Import weightmap_A.png (Sand)
   ```
4. (Optional) Run Python import script for automatic setup:
   ```python
   # In UE5 Python console
   import unreal_import_terraforge
   unreal_import_terraforge.import_all("Content/Terrains/your_terrain")
   ```

**Detailed guide:** [docs/UNREAL_IMPORT.md](docs/UNREAL_IMPORT.md)

### Unity

1. Extract downloaded ZIP to `Assets/Terrains/`
2. In Unity Editor:
   ```
   GameObject → 3D Object → Terrain
   → Terrain Settings → Import Raw
   → Select heightmap.raw
   → Depth: 16 bit
   → Resolution: 2049x2049
   → Terrain Width/Length: 2048m (from metadata.json)
   → Terrain Height: 600m (from metadata.json)
   ```
3. Apply splatmaps:
   ```
   Terrain → Paint Texture → Edit Terrain Layers
   → Import splatmap.png channels to texture layers
   ```
4. (Optional) Run Editor script for automatic setup:
   ```csharp
   // Unity Editor
   Tools → TerraForge → Import Terrain Package
   // Select the extracted folder
   ```

**Detailed guide:** [docs/UNITY_IMPORT.md](docs/UNITY_IMPORT.md)

### Other Software (GLTF/GeoTIFF)

- **Blender:** File → Import → GLTF (.gltf/.glb)
- **QGIS:** Layer → Add Layer → Add Raster Layer (.tif)
- **ArcGIS:** Add Data → GeoTIFF (.tif)
- **Three.js/Babylon.js:** Load GLTF using standard loaders

## 🔧 Advanced Configuration

### Terrain Quality

Edit `.env`:

```env
# High Quality (slower, larger files)
DEFAULT_HEIGHTMAP_RESOLUTION=4096
ELEVATION_SOURCE_PRIORITY=opentopography,srtm

# Balanced (recommended)
DEFAULT_HEIGHTMAP_RESOLUTION=2048
ELEVATION_SOURCE_PRIORITY=srtm,aster

# Fast (quick previews)
DEFAULT_HEIGHTMAP_RESOLUTION=1024
ELEVATION_SOURCE_PRIORITY=srtm
```

### Export Options

```env
# Unreal Engine 5
UE5_DEFAULT_LANDSCAPE_SIZE=2017  # 1009, 2017, 4033, 8129
UE5_EXPORT_WEIGHTMAPS=true
UE5_EXPORT_SPLINES=true

# Unity
UNITY_DEFAULT_TERRAIN_SIZE=2049  # 513, 1025, 2049, 4097
UNITY_EXPORT_SPLATMAPS=true
UNITY_EXPORT_TREES=true

# Generic
GENERIC_EXPORT_GLTF=true
GENERIC_EXPORT_GEOTIFF=true
```

### Performance

```env
# CPU Usage
PARALLEL_PROCESSING=true
MAX_WORKERS=4  # Number of CPU cores

# Memory
CHUNK_SIZE=1024  # Reduce if running out of memory

# Caching
ENABLE_CACHE=true
CACHE_EXPIRY_DAYS=30
```

## ❌ Troubleshooting

### Backend doesn't start

```bash
# Check Python version (must be 3.13+)
python --version

# Reinstall dependencies
poetry install --no-cache

# Check if port 8000 is available
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -i :8000
```

### Frontend doesn't start

```bash
# Check Node.js version (must be 18+)
node --version

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API keys not working

```bash
# Verify .env file exists
ls -la .env  # Linux/Mac
dir .env     # Windows

# Check API key format (no quotes, no spaces)
# ✅ Correct: SENTINELHUB_CLIENT_ID=abc123
# ❌ Wrong: SENTINELHUB_CLIENT_ID="abc123"
# ❌ Wrong: SENTINELHUB_CLIENT_ID = abc123
```

### Out of memory errors

```env
# Reduce resolution
DEFAULT_HEIGHTMAP_RESOLUTION=1024

# Reduce chunk size
CHUNK_SIZE=512

# Disable parallel processing
PARALLEL_PROCESSING=false
```

### Slow generation

```env
# Enable caching
ENABLE_CACHE=true

# Use faster elevation source
ELEVATION_SOURCE_PRIORITY=srtm

# Reduce area size
MAX_AREA_KM2=25.0
```

## 📚 Additional Resources

- **Full Documentation:** [docs/README.md](docs/README.md)
- **API Reference:** [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md)
- **Contributing:** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
- **API Playground:** http://localhost:8000/docs (when running)

## 🆘 Getting Help

- **Issues:** [GitHub Issues](https://github.com/yourusername/TerraForge-Studio/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/TerraForge-Studio/discussions)

## 🎯 Quick Examples

### Example 1: Mountain Terrain for UE5

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "swiss_alps",
    "bbox": {"north": 46.5, "south": 46.4, "east": 8.0, "west": 7.9},
    "resolution": 4033,
    "export_formats": ["unreal5"],
    "elevation_source": "opentopography",
    "enable_roads": true,
    "enable_buildings": false,
    "enable_vegetation": true
  }'
```

### Example 2: Urban Area for Unity

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "city_downtown",
    "bbox": {"north": 40.76, "south": 40.75, "east": -73.98, "west": -73.99},
    "resolution": 2049,
    "export_formats": ["unity"],
    "enable_roads": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

### Example 3: Island for Generic Export

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tropical_island",
    "bbox": {"north": -17.5, "south": -17.6, "east": -149.8, "west": -149.9},
    "resolution": 2048,
    "export_formats": ["gltf", "geotiff"],
    "enable_water_bodies": true
  }'
```

---

**Enjoy creating realistic terrains! 🌍🎮**
