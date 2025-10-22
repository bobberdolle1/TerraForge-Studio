# 🌍 TerraForge Studio

> **[English](#english)** | **[Русский](#russian)**

---

<a name="english"></a>

## 🇬🇧 English Version

**Professional Cross-Platform 3D Terrain and Real-World Map Generator**

A comprehensive tool for generating detailed and functional real-world terrain for **Unreal Engine 5**, **Unity**, and other game engines. Automatically creates heightmaps, roads, buildings, and vegetation based on advanced geospatial data sources including Sentinel Hub, OpenTopography, Azure Maps, and OpenStreetMap.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

### ✨ Key Features

**🌐 Advanced Geospatial Data Sources:**
- 🛰️ **Sentinel Hub** - High-resolution satellite imagery (RGB, NIR, NDVI, temporal series)
- 🏔️ **OpenTopography** - Precision DEMs/DSMs from LiDAR, SRTM, ASTER
- 🗺️ **Azure Maps** - Vector data, routing, POI, elevation services
- 🌍 **Google Earth Engine** - Massive geospatial computations, vegetation indices, classification
- 📍 **OpenStreetMap** - Roads, buildings, land use (vector data)

**🎮 Multi-Engine Export:**
- 🎨 **Unreal Engine 5** 
  - 16-bit PNG/RAW heightmaps (Landscape-ready)
  - Material weightmaps (rock, grass, dirt, sand)
  - Road splines (Data Layers compatible)
  - Instanced Static Meshes for buildings/trees
- 🎯 **Unity**
  - RAW 16-bit terrain heightmaps
  - Splatmaps for terrain textures
  - GameObject prefabs with world coordinates
  - Addressable Assets support
- 📦 **Generic Formats**
  - GLTF/GLB - 3D meshes with textures
  - GeoTIFF - Georeferenced raster data
  - OBJ - Universal 3D format
  - USDZ - Apple AR format
  - JSON metadata (coordinates, CRS, scale)

**🎨 Interactive 3D Preview:**
- 🌐 **CesiumJS Integration** - Real-time 3D terrain visualization
- 🗺️ **Satellite Overlays** - Draped imagery on terrain
- 🏗️ **Building Extrusion** - 3D building visualization
- 🔄 **2D/3D Toggle** - Switch between map views
- 📸 **Export Preview** - Screenshot/video generation

**⚡ Professional Workflow:**
- 🔄 **Incremental Updates** - Update only changed regions
- 📊 **Batch Processing** - Generate multiple terrains in parallel
- 🖼️ **Map Preview** - Visual overlays with statistics
- 💾 **Smart Caching** - Efficient data reuse
- 🌍 **Multi-CRS Support** - WGS84, UTM, custom projections

**🌐 Modern Web Interface:**
- ⚛️ **React + TypeScript** - Professional, responsive UI
- 🎨 **Modern Design** - Clean, intuitive interface
- 🗺️ **Advanced Map Tools** - Polygon, rectangle, circle selection
- 🔍 **Global Search** - Find any location worldwide
- 🌓 **Dark/Light Theme** - Customizable appearance
- 🌍 **Localization** - English & Russian support

### 🏗️ Architecture

```
TerraForge-Studio/
├── realworldmapgen/              # Core Python package
│   ├── core/                     # Core generation engine
│   │   ├── sources/              # Data source adapters
│   │   │   ├── sentinel_hub.py  # Sentinel Hub API
│   │   │   ├── opentopography.py # OpenTopography API
│   │   │   ├── azure_maps.py    # Azure Maps API
│   │   │   ├── earth_engine.py  # Google Earth Engine
│   │   │   └── osm_source.py    # OpenStreetMap
│   │   ├── terrain/              # Heightmap generation
│   │   ├── vector/               # Vector data processing
│   │   └── generator.py          # Main orchestrator
│   ├── exporters/                # Export modules
│   │   ├── unreal5/              # Unreal Engine 5
│   │   │   ├── heightmap.py      # UE5 heightmap export
│   │   │   ├── weightmaps.py     # Material layers
│   │   │   └── splines.py        # Road splines
│   │   ├── unity/                # Unity
│   │   │   ├── terrain.py        # Unity terrain export
│   │   │   └── prefabs.py        # GameObject generation
│   │   └── generic/              # Universal formats
│   │       ├── gltf_exporter.py  # GLTF/GLB
│   │       ├── geotiff.py        # GeoTIFF
│   │       └── obj_exporter.py   # OBJ/USDZ
│   ├── preview/                  # 3D preview renderer
│   ├── ai/                       # AI terrain analysis (optional)
│   └── api/                      # FastAPI REST API
├── frontend/                     # React web interface
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── views/                # Page views
│   │   └── services/             # API services
│   └── public/
├── docs/                         # Documentation
└── .env.example                  # Configuration template
```

### 🚀 Quick Start

#### Prerequisites

- **Python 3.13+**
- **Node.js 18+** (for frontend development)
- **Poetry** (Python dependency management)

**Optional:**
- **Ollama** (for AI terrain analysis) - [Download](https://ollama.ai)

#### Installation

**Windows (PowerShell):**
```powershell
git clone https://github.com/yourusername/TerraForge-Studio.git
cd TerraForge-Studio

# Setup and run
.\setup.ps1       # First-time setup
.\run.ps1         # Start application
.\run.ps1 stop    # Stop application
```

**Linux/Mac:**
```bash
git clone https://github.com/yourusername/TerraForge-Studio.git
cd TerraForge-Studio

chmod +x run.sh
./run.sh         # Start (auto-installs dependencies)
./run.sh stop    # Stop
```

**Manual Installation:**
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install Python dependencies
poetry install

# 3. Start backend API
poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000

# 4. Install frontend dependencies (in another terminal)
cd frontend
npm install
npm run dev

# 5. Access application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 📖 Usage

#### Web Interface

1. **Open** browser at `http://localhost:3000`
2. **Configure Data Sources** (Settings):
   - Add API keys for Sentinel Hub, OpenTopography, Azure Maps
   - Or use free OpenStreetMap + SRTM data
3. **Select Area**:
   - 🔍 Search for location
   - 🔲 Draw rectangle, polygon, or circle
   - 📐 View area statistics
4. **Configure Export**:
   - Choose target engine (UE5, Unity, Generic)
   - Set heightmap resolution (512-8192)
   - Enable features (roads, buildings, vegetation)
5. **Generate**:
   - Click "🚀 Generate Terrain"
   - View 3D preview
   - Download ZIP package

#### API Example

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mountain_valley",
    "bbox": {
      "north": 46.5,
      "south": 46.4,
      "east": 8.0,
      "west": 7.9
    },
    "resolution": 4096,
    "export_formats": ["unreal5", "unity"],
    "elevation_source": "opentopography",
    "enable_roads": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

### 🎮 Importing to Game Engines

#### Unreal Engine 5

1. Download the UE5 export package
2. Extract to your project's `Content/` folder
3. Use the included Python script to auto-import:
   ```python
   # Run in UE5 Python console
   import unreal_import_script
   unreal_import_script.import_terrain("path/to/package")
   ```
4. Files included:
   - `heightmap_16bit.png` - Landscape heightmap
   - `weightmap_*.png` - Material layers (R/G/B/A channels)
   - `roads_splines.json` - Road network data
   - `meshes_placement.json` - Building/tree coordinates
   - `metadata.json` - Scale, coordinates, CRS

See `docs/UNREAL_IMPORT.md` for detailed guide.

#### Unity

1. Download the Unity export package
2. Extract to your project's `Assets/Terrains/` folder
3. Use the C# Editor script:
   ```csharp
   // In Unity Editor
   Tools > TerraForge > Import Terrain
   // Select the package folder
   ```
4. Files included:
   - `heightmap.raw` - 16-bit terrain heightmap
   - `splatmap.png` - Terrain texture layers
   - `objects.json` - GameObject placement data
   - `metadata.json` - Scale, coordinates, CRS

See `docs/UNITY_IMPORT.md` for detailed guide.

#### Generic (GLTF/GeoTIFF)

- **GLTF/GLB**: Load in Blender, Three.js, Babylon.js, etc.
- **GeoTIFF**: Use in QGIS, ArcGIS, or other GIS software
- **OBJ**: Universal 3D format for any software

### ⚙️ Configuration

Edit `.env` file:

```env
# Data Sources
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_secret
OPENTOPOGRAPHY_API_KEY=your_api_key
AZURE_MAPS_SUBSCRIPTION_KEY=your_key

# Defaults
DEFAULT_HEIGHTMAP_RESOLUTION=2048
MAX_AREA_KM2=100.0
ELEVATION_SOURCE_PRIORITY=opentopography,srtm,aster

# Unreal Engine 5
UE5_DEFAULT_LANDSCAPE_SIZE=2017  # 1009, 2017, 4033, 8129
UE5_EXPORT_WEIGHTMAPS=true

# Unity
UNITY_DEFAULT_TERRAIN_SIZE=2049  # 513, 1025, 2049, 4097
UNITY_EXPORT_SPLATMAPS=true
```

### 📦 Core Technologies

**Backend:**
- FastAPI - Modern async web framework
- Rasterio - Geospatial raster I/O
- GeoPandas - Vector data processing
- SentinelHub - Satellite imagery API
- Trimesh - 3D mesh processing
- PyGLTF - GLTF export

**Frontend:**
- React 18 + TypeScript
- React-Leaflet - Map interface
- CesiumJS - 3D terrain visualization
- Tailwind CSS - Modern styling
- Vite - Fast build tool

**Infrastructure:**
- Poetry - Python dependencies
- Docker - Optional containerization

### 🗺️ Data Sources Comparison

| Source | Resolution | Coverage | Requires API Key | Free Tier |
|--------|-----------|----------|------------------|-----------|
| **SRTM** | 30m-90m | Global | ❌ No | ✅ Unlimited |
| **Sentinel Hub** | 10m-60m | Global | ✅ Yes | 🟡 Limited |
| **OpenTopography** | 0.5m-30m | Regional (LiDAR) | ✅ Yes | ✅ Generous |
| **Azure Maps** | Varies | Global | ✅ Yes | 🟡 Limited |
| **OpenStreetMap** | Vector | Global | ❌ No | ✅ Unlimited |

### 📝 Roadmap

**Completed ✅:**
- ✅ Multi-source geospatial data integration
- ✅ Unreal Engine 5 export (heightmaps, weightmaps, splines)
- ✅ Unity export (terrain, splatmaps, prefabs)
- ✅ Generic export (GLTF, GeoTIFF, OBJ)
- ✅ Modern React + TypeScript frontend

**In Progress 🚧:**
- 🚧 CesiumJS 3D preview integration
- 🚧 Material classification using AI/ML
- 🚧 Procedural road mesh generation

**Planned 📋:**
- 📋 Unreal Engine 5 plugin (one-click import)
- 📋 Unity package (AssetStore-ready)
- 📋 Real-time collaborative editing
- 📋 Cloud-based processing (serverless)
- 📋 Water body detection and generation
- 📋 Procedural city generation
- 📋 Support for Godot Engine, O3DE

### 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### 📄 License

MIT License - see [LICENSE](LICENSE) file.

### 🙏 Acknowledgments

- Inspired by [unrealheightmap](https://github.com/manticorp/unrealheightmap)
- Built with [osmnx](https://github.com/gboeing/osmnx) by Geoff Boeing
- Map data © [OpenStreetMap](https://www.openstreetmap.org) contributors
- Powered by Sentinel Hub, OpenTopography, and Azure Maps APIs

---

<a name="russian"></a>

## 🇷🇺 Русская версия

**Профессиональный кроссплатформенный генератор 3D-ландшафтов реального мира**

Комплексный инструмент для генерации детализированного реального рельефа для **Unreal Engine 5**, **Unity** и других игровых движков. Автоматически создаёт карты высот, дороги, здания и растительность на основе передовых геопространственных источников данных: Sentinel Hub, OpenTopography, Azure Maps и OpenStreetMap.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

### ✨ Основные возможности

**🌐 Продвинутые геопространственные источники:**
- 🛰️ **Sentinel Hub** - Спутниковые снимки высокого разрешения (RGB, NIR, NDVI, временные ряды)
- 🏔️ **OpenTopography** - Высокоточные DEM/DSM из LiDAR, SRTM, ASTER
- 🗺️ **Azure Maps** - Векторные данные, маршрутизация, POI, высоты
- 🌍 **Google Earth Engine** - Массивные геопространственные вычисления, индексы растительности
- 📍 **OpenStreetMap** - Дороги, здания, землепользование (векторные данные)

**🎮 Мульти-движковый экспорт:**
- 🎨 **Unreal Engine 5**
  - 16-битные PNG/RAW карты высот (готовые для Landscape)
  - Карты весов материалов (камень, трава, земля, песок)
  - Сплайны дорог (совместимые с Data Layers)
  - Instanced Static Meshes для зданий/деревьев
- 🎯 **Unity**
  - RAW 16-битные карты высот terrain
  - Splatmaps для текстур terrain
  - Префабы GameObject с мировыми координатами
  - Поддержка Addressable Assets
- 📦 **Универсальные форматы**
  - GLTF/GLB - 3D-меши с текстурами
  - GeoTIFF - Георефе�енцированные растровые данные
  - OBJ - Универсальный 3D-формат
  - USDZ - Формат Apple AR
  - JSON метаданные (координаты, CRS, масштаб)

**🎨 Интерактивное 3D-превью:**
- 🌐 **Интеграция CesiumJS** - 3D-визуализация рельефа в реальном времени
- 🗺️ **Наложение спутниковых снимков** - Текстуры на рельефе
- 🏗️ **Экструзия зданий** - 3D-визуализация построек
- 🔄 **Переключение 2D/3D** - Смена видов карты
- 📸 **Экспорт превью** - Генерация скриншотов/видео

**⚡ Профессиональный рабочий процесс:**
- 🔄 **Инкрементальные обновления** - Обновление только изменённых регионов
- 📊 **Пакетная обработка** - Генерация нескольких terrain параллельно
- 🖼️ **Превью карт** - Визуальные наложения со статистикой
- 💾 **Умное кэширование** - Эффективное переиспользование данных
- 🌍 **Поддержка Multi-CRS** - WGS84, UTM, пользовательские проекции

**🌐 Современный веб-интерфейс:**
- ⚛️ **React + TypeScript** - Профессиональный, отзывчивый UI
- 🎨 **Современный дизайн** - Чистый, интуитивный интерфейс
- 🗺️ **Продвинутые инструменты карты** - Полигон, прямоугольник, круг
- 🔍 **Глобальный поиск** - Найти любое место в мире
- 🌓 **Тёмная/светлая тема** - Настраиваемый внешний вид
- 🌍 **Локализация** - Поддержка английского и русского

*(Остальной контент аналогичен английской версии)*

### 🚀 Быстрый старт

См. английскую версию выше для инструкций по установке.

### 📄 Лицензия

Лицензия MIT - см. файл [LICENSE](LICENSE).

---

<div align="center">

**Created with ❤️ for the game development community**

⭐ **If you like this project, give it a star on GitHub!** ⭐

[🌟 Star on GitHub](https://github.com/yourusername/TerraForge-Studio) | 
[📖 Documentation](docs/) | 
[🐛 Report Bug](https://github.com/yourusername/TerraForge-Studio/issues) | 
[💡 Request Feature](https://github.com/yourusername/TerraForge-Studio/issues)

</div>
