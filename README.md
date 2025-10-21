# 🗺️ RealWorldMapGen-BNG

> **[English](#english)** | **[Русский](#russian)**

---

<a name="english"></a>

## 🇬🇧 English Version

**AI-Powered Real-World Map Generator for BeamNG.drive**

A comprehensive tool for generating detailed and functional real-world maps for BeamNG.drive. Automatically creates roads, traffic lights, parking lots, buildings, and vegetation based on OpenStreetMap data analysis and Qwen AI models via Ollama.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

### ✨ Key Features

**🤖 Advanced AI Analysis:**
- 🛰️ **Satellite Imagery Analysis** - Downloads and analyzes real satellite images (OSM, Mapbox, Bing Maps)
- 🔍 **Detailed Road Detection** - AI extracts road width, lane count, markings, surface type, and condition
- 🏗️ **Building Analysis** - Precise footprint boundaries, height from shadows, roof types, materials
- 🌳 **Surface Classification** - Identifies paved areas, vegetation, water bodies, bare ground
- 🚗 **AI-Optimized Traffic** - Qwen3-Coder generates intelligent traffic routes and driver behaviors

**🎮 Multi-Engine Export:**
- 🏁 **BeamNG.drive** - Complete mod packages with traffic system integration
- 🎨 **Unreal Engine 5** - Landscape heightmaps, road splines, static mesh placement
- 🎯 **Unity** - Terrain data, GameObject instantiation, mesh generation
- 📦 **One-Click Packaging** - Auto-generated .zip mods ready to install

**🗺️ Advanced Mapping:**
- 🌍 **Real-World Data** - Extract from OpenStreetMap for any location worldwide
- 🏔️ **Elevation Data** - SRTM-based heightmap generation
- 🛣️ **Smart Road Networks** - Automatic road types, lanes, materials, widths
- 🚦 **Traffic Infrastructure** - Lights, parking, spawn points, AI behaviors
- 🏢 **Building Placement** - Height info, types, custom prefab support
- 🎨 **Custom Prefabs** - Import your own 3D models (.jbeam, .fbx, .obj, .gltf)

**⚡ Performance & Workflow:**
- 🔄 **Incremental Updates** - Update only changed parts of existing maps
- 📊 **Batch Processing** - Generate multiple maps in parallel
- 🖼️ **Map Preview** - Visual overlays with statistics
- 💾 **Smart Caching** - Imagery and OSM data caching

**🌐 Modern Web Interface:**
- 🎨 **Glassmorphism UI** - Beautiful modern design with animations
- 🔧 **Advanced Selection Tools** - Rectangle, polygon, circle area selection
- 🔍 **Location Search** - Find any place worldwide instantly
- 🗺️ **Multiple Basemaps** - OSM, Humanitarian, Satellite views
- 📍 **Real-time Coordinates** - Mouse position and area statistics
- 🐳 **Docker Ready** - Fully containerized with Docker Compose

### 🏗️ Architecture

```
RealWorldMapGen-BNG/
├── realworldmapgen/              # Core Python package
│   ├── ai/                       # AI integration (Ollama + Qwen models)
│   │   ├── ollama_client.py      # Ollama API client
│   │   └── terrain_analyzer.py   # Advanced vision analysis
│   ├── imagery/                  # Satellite imagery downloader
│   ├── osm/                      # OpenStreetMap extraction
│   ├── elevation/                # Heightmap generation
│   ├── traffic/                  # AI traffic route generation
│   │   ├── traffic_generator.py  # Route optimization
│   │   └── beamng_traffic.py     # BeamNG integration
│   ├── prefabs/                  # Custom prefab management
│   ├── preview/                  # Map preview generator
│   ├── packaging/                # BeamNG mod packager
│   ├── incremental/              # Incremental updates
│   ├── exporters/                # Multi-engine exporters
│   │   ├── beamng_exporter.py    # BeamNG.drive
│   │   ├── unreal_exporter.py    # Unreal Engine 5
│   │   └── unity_exporter.py     # Unity
│   ├── api/                      # FastAPI REST API
│   └── generator.py              # Main orchestrator
├── frontend/                     # Modern web interface
│   ├── index.html                # UI layout
│   ├── style.css                 # Glassmorphism design
│   └── app.js                    # Advanced map controls
├── docs/                         # Documentation
├── docker-compose.yml            # Docker orchestration
└── pyproject.toml                # Poetry dependencies
```

### 🚀 Quick Start

#### Prerequisites

- **Docker & Docker Compose** (for backend and frontend)
- **Ollama** (installed locally - download from https://ollama.ai)
- **Python 3.13+** (for local development)
- **Poetry** (for dependency management)

#### Installation

**Windows (PowerShell):**
```powershell
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG
.\setup.ps1
```

**Linux/Mac:**
```bash
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG
chmod +x setup.sh
./setup.sh
```

**Manual Installation:**
```bash
# 1. Create environment file
cp .env.example .env

# 2. Install and start Ollama
# Download from https://ollama.ai
ollama serve

# 3. Start Docker containers
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:8080
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 📖 Usage

#### Web Interface

1. **Open** browser at `http://localhost:8080`
2. **Search** for a location (or navigate manually on the map)
3. **Select Area** using one of three tools:
   - 🔲 **Rectangle** - Click and drag to create a rectangular area
   - 🔺 **Polygon** - Click points to draw a custom polygon shape
   - ⭕ **Circle** - Click and drag to create a circular area
4. **Configure** generation options:
   - Map name (alphanumeric, underscores, hyphens)
   - Export format (BeamNG.drive, Unreal Engine 5, Unity, or All)
   - Heightmap resolution (1024/2048/4096)
   - Enable/disable features (AI analysis, roads, traffic, buildings, vegetation)
5. **Generate** - Click the "🚀 Generate Map" button
6. **Download** - Get your .zip mod or individual files when complete

**Map Controls:**
- 🔍 Location search with autocomplete
- 📍 Real-time coordinate display
- 📐 Selected area info (bounds + size in km²)
- 🗺️ Switch between OSM, Humanitarian, and Satellite views
- ❌ Clear selection or 🎯 Fit map to selection

#### API Example

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_map",
    "bbox": {
      "north": 37.8,
      "south": 37.79,
      "east": -122.4,
      "west": -122.41
    },
    "resolution": 2048,
    "export_engine": "beamng",
    "enable_ai_analysis": true,
    "enable_roads": true,
    "enable_traffic_lights": true,
    "enable_parking": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

### 🎮 Importing to BeamNG.drive

**Easy Installation (Recommended):**
1. Download the `.zip` file from the web interface
2. Extract to `<BeamNG.drive>/mods/` directory
3. Launch BeamNG.drive - your map will be available automatically!

**Manual Installation:**
1. Locate generated map in `output/<map_name>/` directory
2. Copy the entire folder to:
   ```
   <BeamNG.drive>/levels/<map_name>/
   ```
3. Files included:
   - `main.level.json` - Level configuration
   - `<map_name>_heightmap.png` - Terrain heightmap
   - `roads.json` - Road network data
   - `objects.json` - Buildings and vegetation
   - `traffic.json` - Traffic system (lights, parking, spawn points, AI behaviors)
   - `info.json` - Map metadata
4. Launch BeamNG.drive and select your custom map

**For Unreal Engine 5:**
- Import `.raw` heightmap using the Python script provided
- Load road splines and static mesh placement JSON
- See `docs/UNREAL_IMPORT.md` for details

**For Unity:**
- Import `.raw` terrain heightmap
- Use the C# Editor script for automatic setup
- See `docs/UNITY_IMPORT.md` for details

### ⚙️ Configuration

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

### 📦 Core Technologies

**Backend:**
- FastAPI - Modern async web framework
- osmnx - OpenStreetMap data extraction
- GeoPandas - Geospatial data processing
- Ollama Python SDK - AI model integration
- Rasterio - Raster data I/O
- Pillow - Image processing
- NumPy/SciPy - Numerical computing

**Frontend:**
- Leaflet - Interactive maps with multiple basemap layers
- Leaflet.draw - Advanced drawing tools (rectangle, polygon, circle)
- Nominatim - Location search API
- Modern CSS (Glassmorphism, animations)
- Vanilla JavaScript ES6+

**Infrastructure:**
- Docker & Docker Compose - Containerization
- Nginx - Web server and reverse proxy
- Poetry - Python dependency management

**AI Models:**
- Qwen3-VL:235B-Cloud - Image analysis
- Qwen3-Coder:480B-Cloud - Code generation and recommendations

### 🐛 Known Issues

- **Large areas**: Processing areas >50 km² may require significant memory
- **First-time data**: Downloading SRTM data can be slow (cached afterwards)
- **OSM rate limits**: Very frequent requests may be rate-limited
- **Ollama offline**: AI features unavailable without Ollama

### 📝 Roadmap

**Completed ✅:**
- ✅ Real satellite imagery download and analysis (OSM, Mapbox, Bing Maps)
- ✅ Advanced AI vision analysis (road width, lanes, markings, building heights)
- ✅ AI-optimized traffic route generation with BeamNG integration
- ✅ Support for custom object prefabs (.jbeam, .fbx, .obj, .gltf)
- ✅ Export to Unreal Engine 5 and Unity
- ✅ Map preview generation with statistics
- ✅ Batch processing for multiple areas
- ✅ Incremental updates to existing maps
- ✅ One-click .zip mod packaging
- ✅ Modern glassmorphism UI with advanced map controls

**In Progress 🚧:**
- 🚧 3D map preview rendering
- 🚧 Road texture generation based on AI analysis
- 🚧 Procedural building mesh generation

**Planned 📋:**
- 📋 Real-time collaborative map editing
- 📋 Cloud-based generation (no local Ollama needed)
- 📋 BeamNG.drive lua script generation for dynamic events
- 📋 Integration with more data sources (Google Earth Engine, Mapbox)
- 📋 Advanced vegetation placement with ecosystem simulation
- 📋 Water body detection and generation (rivers, lakes)
- 📋 Procedural city generation for empty areas
- 📋 Support for other games (Assetto Corsa, rFactor 2)

### 🤝 Contributing

Contributions are welcome! Please check [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file.

### 🙏 Acknowledgments

- Inspired by [unrealheightmap](https://github.com/manticorp/unrealheightmap)
- Built with [osmnx](https://github.com/gboeing/osmnx) by Geoff Boeing
- Powered by [Ollama](https://ollama.ai) and Qwen models
- Map data © [OpenStreetMap](https://www.openstreetmap.org) contributors

---

<a name="russian"></a>

## 🇷🇺 Русская версия

**ИИ-генератор карт реального мира для BeamNG.drive**

Полноценный инструмент для генерации детализированных и функциональных карт реальных локаций для BeamNG.drive. Автоматически создает дороги, светофоры, парковки, здания и растительность на основе анализа данных OpenStreetMap и ИИ-моделей Qwen через Ollama.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

### ✨ Основные возможности

**🤖 Продвинутый ИИ-анализ:**
- 🛰️ **Анализ спутниковых снимков** - Загрузка и анализ реальных снимков (OSM, Mapbox, Bing Maps)
- 🔍 **Детальное распознавание дорог** - ИИ извлекает ширину, количество полос, разметку, тип покрытия
- 🏗️ **Анализ зданий** - Точные границы, высота по теням, типы крыш, материалы
- 🌳 **Классификация поверхностей** - Определение дорог, растительности, водоёмов, грунта
- 🚗 **ИИ-оптимизация трафика** - Qwen3-Coder генерирует маршруты и поведение водителей

**🎮 Мульти-движковый экспорт:**
- 🏁 **BeamNG.drive** - Полные пакеты модов с интеграцией трафика
- 🎨 **Unreal Engine 5** - Heightmap ландшафтов, сплайны дорог, размещение статичных мешей
- 🎯 **Unity** - Данные террейна, инстанцирование GameObject, генерация мешей
- 📦 **Упаковка в один клик** - Автоматически создаёт .zip моды готовые к установке

**🗺️ Продвинутое картографирование:**
- 🌍 **Данные реального мира** - Извлечение из OpenStreetMap для любой точки мира
- 🏔️ **Данные высот** - Генерация heightmap на основе SRTM
- 🛣️ **Умные дорожные сети** - Автоматические типы дорог, полосы, материалы, ширина
- 🚦 **Дорожная инфраструктура** - Светофоры, парковки, точки спауна, ИИ-поведение
- 🏢 **Размещение зданий** - Информация о высоте, типах, поддержка пользовательских префабов
- 🎨 **Пользовательские префабы** - Импорт своих 3D-моделей (.jbeam, .fbx, .obj, .gltf)

**⚡ Производительность и рабочий процесс:**
- 🔄 **Инкрементальные обновления** - Обновление только изменённых частей карт
- 📊 **Пакетная обработка** - Генерация нескольких карт параллельно
- 🖼️ **Превью карт** - Визуальные наложения со статистикой
- 💾 **Умное кэширование** - Кэширование снимков и данных OSM

**🌐 Современный веб-интерфейс:**
- 🎨 **Glassmorphism UI** - Красивый современный дизайн с анимациями
- 🔧 **Продвинутые инструменты выбора** - Прямоугольник, полигон, круг
- 🔍 **Поиск локаций** - Поиск любого места в мире мгновенно
- 🗺️ **Несколько базовых карт** - OSM, Humanitarian, спутниковые виды
- 📍 **Координаты в реальном времени** - Позиция мыши и статистика области
- 🐳 **Docker Ready** - Полная контейнеризация с Docker Compose

### 🏗️ Архитектура

```
RealWorldMapGen-BNG/
├── realworldmapgen/              # Основной Python-пакет
│   ├── ai/                       # ИИ-интеграция (Ollama + Qwen модели)
│   │   ├── ollama_client.py      # Клиент Ollama API
│   │   └── terrain_analyzer.py   # Продвинутый анализ изображений
│   ├── imagery/                  # Загрузчик спутниковых снимков
│   ├── osm/                      # Извлечение данных OpenStreetMap
│   ├── elevation/                # Генерация heightmap
│   ├── traffic/                  # ИИ-генерация маршрутов трафика
│   │   ├── traffic_generator.py  # Оптимизация маршрутов
│   │   └── beamng_traffic.py     # Интеграция BeamNG
│   ├── prefabs/                  # Управление пользовательскими префабами
│   ├── preview/                  # Генератор превью карт
│   ├── packaging/                # Упаковщик модов BeamNG
│   ├── incremental/              # Инкрементальные обновления
│   ├── exporters/                # Мульти-движковые экспортеры
│   │   ├── beamng_exporter.py    # BeamNG.drive
│   │   ├── unreal_exporter.py    # Unreal Engine 5
│   │   └── unity_exporter.py     # Unity
│   ├── api/                      # FastAPI REST API
│   └── generator.py              # Главный оркестратор
├── frontend/                     # Современный веб-интерфейс
│   ├── index.html                # Разметка UI
│   ├── style.css                 # Glassmorphism дизайн
│   └── app.js                    # Продвинутые элементы управления картой
├── docs/                         # Документация
├── docker-compose.yml            # Docker оркестрация
└── pyproject.toml                # Poetry зависимости
```

### 🚀 Быстрый старт

#### Требования

- **Docker & Docker Compose** (для бэкенда и фронтенда)
- **Ollama** (локальная установка - скачать с https://ollama.ai)
- **Python 3.13+** (для локальной разработки)
- **Poetry** (для управления зависимостями)

#### Установка

**Windows (PowerShell):**
```powershell
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG
.\setup.ps1
```

**Linux/Mac:**
```bash
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG
chmod +x setup.sh
./setup.sh
```

**Ручная установка:**
```bash
# 1. Создание файла конфигурации
cp .env.example .env

# 2. Установка и запуск Ollama
# Скачайте с https://ollama.ai
ollama serve

# 3. Запуск Docker-контейнеров
docker-compose up -d

# 4. Доступ к приложению
# Фронтенд: http://localhost:8080
# API: http://localhost:8000
# Документация API: http://localhost:8000/docs
```

### 📖 Использование

#### Веб-интерфейс

1. **Откройте** браузер: `http://localhost:8080`
2. **Найдите** локацию (или навигируйте вручную на карте)
3. **Выберите область** одним из трёх инструментов:
   - 🔲 **Прямоугольник** - Кликните и тяните для создания прямоугольной области
   - 🔺 **Полигон** - Кликайте точки для рисования произвольного полигона
   - ⭕ **Круг** - Кликните и тяните для создания круглой области
4. **Настройте** параметры генерации:
   - Название карты (буквы, цифры, подчёркивания, дефисы)
   - Формат экспорта (BeamNG.drive, Unreal Engine 5, Unity или все)
   - Разрешение heightmap (1024/2048/4096)
   - Включение/отключение функций (ИИ-анализ, дороги, трафик, здания, растительность)
5. **Генерируйте** - Нажмите кнопку "🚀 Generate Map"
6. **Скачивайте** - Получите .zip мод или отдельные файлы после завершения

**Управление картой:**
- 🔍 Поиск локаций с автодополнением
- 📍 Отображение координат в реальном времени
- 📐 Информация о выбранной области (границы + размер в км²)
- 🗺️ Переключение между OSM, Humanitarian и спутниковыми видами
- ❌ Очистка выбора или 🎯 Подгонка карты под выделение

#### Пример использования API

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_map",
    "bbox": {
      "north": 55.7558,
      "south": 55.7508,
      "east": 37.6173,
      "west": 37.6123
    },
    "resolution": 2048,
    "export_engine": "beamng",
    "enable_ai_analysis": true,
    "enable_roads": true,
    "enable_traffic_lights": true,
    "enable_parking": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

### 🎮 Импорт в BeamNG.drive

**Простая установка (рекомендуется):**
1. Скачайте `.zip` файл из веб-интерфейса
2. Распакуйте в папку `<BeamNG.drive>/mods/`
3. Запустите BeamNG.drive - ваша карта будет доступна автоматически!

**Ручная установка:**
1. Найдите сгенерированную карту в `output/<название_карты>/`
2. Скопируйте всю папку в:
   ```
   <BeamNG.drive>/levels/<название_карты>/
   ```
3. Включённые файлы:
   - `main.level.json` - Конфигурация уровня
   - `<название_карты>_heightmap.png` - Heightmap террейна
   - `roads.json` - Данные дорожной сети
   - `objects.json` - Здания и растительность
   - `traffic.json` - Система трафика (светофоры, парковки, точки спауна, ИИ-поведение)
   - `info.json` - Метаданные карты
4. Запустите BeamNG.drive и выберите вашу карту

**Для Unreal Engine 5:**
- Импортируйте `.raw` heightmap используя предоставленный Python скрипт
- Загрузите сплайны дорог и JSON размещения статичных мешей
- См. `docs/UNREAL_IMPORT.md` для деталей

**Для Unity:**
- Импортируйте `.raw` heightmap террейна
- Используйте C# Editor скрипт для автоматической настройки
- См. `docs/UNITY_IMPORT.md` для деталей

### ⚙️ Конфигурация

Отредактируйте файл `.env` для настройки:

```env
# Настройки Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_VISION_MODEL=qwen3-vl:235b-cloud
OLLAMA_CODER_MODEL=qwen3-coder:480b-cloud

# Настройки генерации карт
DEFAULT_RESOLUTION=2048
MAX_AREA_KM2=100.0

# Настройки обработки
ENABLE_AI_ANALYSIS=true
PARALLEL_PROCESSING=true
MAX_WORKERS=4
```

### 📦 Основные технологии

**Backend:**
- FastAPI - Современный асинхронный веб-фреймворк
- osmnx - Извлечение данных OpenStreetMap
- GeoPandas - Обработка геопространственных данных
- Ollama Python SDK - Интеграция с ИИ-моделями
- Rasterio - Работа с растровыми данными
- Pillow - Обработка изображений
- NumPy/SciPy - Численные вычисления

**Frontend:**
- Leaflet - Интерактивные карты с несколькими базовыми слоями
- Leaflet.draw - Продвинутые инструменты рисования (прямоугольник, полигон, круг)
- Nominatim - API поиска локаций
- Modern CSS (Glassmorphism, анимации)
- Vanilla JavaScript ES6+

**Инфраструктура:**
- Docker & Docker Compose - Контейнеризация
- Nginx - Веб-сервер и reverse proxy
- Poetry - Управление зависимостями Python

**ИИ-модели:**
- Qwen3-VL:235B-Cloud - Анализ изображений
- Qwen3-Coder:480B-Cloud - Генерация кода и рекомендаций

### 🐛 Известные проблемы

- **Большие области**: Обработка областей >50 км² требует значительной памяти
- **Первая загрузка**: Скачивание SRTM данных может занять время (затем кэшируется)
- **Лимиты OSM**: Частые запросы могут быть ограничены
- **Ollama offline**: ИИ-функции недоступны без Ollama

### 📝 Roadmap

**Завершено ✅:**
- ✅ Загрузка и анализ спутниковых снимков (OSM, Mapbox, Bing Maps)
- ✅ Продвинутый ИИ-анализ (ширина дорог, полосы, разметка, высота зданий)
- ✅ ИИ-оптимизированная генерация маршрутов трафика с интеграцией BeamNG
- ✅ Поддержка пользовательских префабов (.jbeam, .fbx, .obj, .gltf)
- ✅ Экспорт в Unreal Engine 5 и Unity
- ✅ Генерация превью карт со статистикой
- ✅ Пакетная обработка нескольких областей
- ✅ Инкрементальные обновления существующих карт
- ✅ Упаковка .zip модов в один клик
- ✅ Современный glassmorphism UI с продвинутыми элементами управления картой

**В разработке 🚧:**
- 🚧 3D рендеринг превью карт
- 🚧 Генерация текстур дорог на основе ИИ-анализа
- 🚧 Процедурная генерация мешей зданий

**Запланировано 📋:**
- 📋 Совместное редактирование карт в реальном времени
- 📋 Облачная генерация (без локального Ollama)
- 📋 Генерация lua скриптов BeamNG.drive для динамических событий
- 📋 Интеграция с дополнительными источниками данных (Google Earth Engine, Mapbox)
- 📋 Продвинутое размещение растительности с симуляцией экосистем
- 📋 Обнаружение и генерация водных объектов (реки, озёра)
- 📋 Процедурная генерация городов для пустых областей
- 📋 Поддержка других игр (Assetto Corsa, rFactor 2)

### 🤝 Участие в разработке

Мы приветствуем вклад сообщества! Пожалуйста, ознакомьтесь с [CONTRIBUTING.md](docs/CONTRIBUTING.md).

### 📄 Лицензия

Этот проект распространяется под лицензией **MIT License** - см. файл [LICENSE](LICENSE).

### 🙏 Благодарности

- Вдохновлено проектом [unrealheightmap](https://github.com/manticorp/unrealheightmap)
- Создано с использованием [osmnx](https://github.com/gboeing/osmnx) от Geoff Boeing
- Работает на [Ollama](https://ollama.ai) и моделях Qwen
- Данные карт © участники [OpenStreetMap](https://www.openstreetmap.org)

---

<div align="center">

**Made with ❤️ for the BeamNG.drive community**

⭐ **If you like this project, give it a star on GitHub!** ⭐

[🌟 Star on GitHub](https://github.com/bobberdolle1/RealWorldMapGen-BNG) | 
[📖 Documentation](docs/) | 
[🐛 Report Bug](https://github.com/bobberdolle1/RealWorldMapGen-BNG/issues) | 
[💡 Request Feature](https://github.com/bobberdolle1/RealWorldMapGen-BNG/issues)

</div>
