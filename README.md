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

- 🌍 **Real-World Data Integration** - Extract geographic data from OpenStreetMap for any location
- 🤖 **AI-Powered Analysis** - Uses Qwen3-VL and Qwen3-Coder via Ollama for intelligent terrain analysis
- 🏔️ **Heightmap Generation** - Creates detailed elevation data from SRTM sources
- 🛣️ **Road Network Generation** - Automatically generates roads with proper types, lanes, and materials
- 🚦 **Traffic Infrastructure** - Places traffic lights and creates parking lots based on OSM data
- 🏢 **Building Placement** - Extracts and positions buildings with height information
- 🌳 **Vegetation Distribution** - Generates trees and vegetation areas based on terrain analysis
- 🎮 **BeamNG.drive Export** - Outputs all data in BeamNG.drive-compatible formats
- 🌐 **Web Interface** - Interactive map selection with Leaflet integration
- 🐳 **Docker Support** - Fully containerized with Docker Compose

### 🏗️ Architecture

```
RealWorldMapGen-BNG/
├── realworldmapgen/              # Core Python package
│   ├── ai/                       # AI integration (Ollama)
│   ├── osm/                      # OpenStreetMap extraction
│   ├── elevation/                # Heightmap generation
│   ├── exporters/                # BeamNG.drive exporters
│   ├── api/                      # FastAPI backend
│   └── generator.py              # Main orchestrator
├── frontend/                     # Web interface
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

1. Open browser at `http://localhost:8080`
2. Use the rectangle tool to select an area on the map
3. Configure generation options:
   - Map name
   - Heightmap resolution (1024/2048/4096)
   - Enable/disable features (AI, roads, traffic, buildings, etc.)
4. Click "Generate Map"
5. Download generated files when complete

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
    "enable_ai_analysis": true,
    "enable_roads": true,
    "enable_traffic_lights": true,
    "enable_parking": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

### 🎮 Importing to BeamNG.drive

1. Locate generated map in `output/<map_name>/` directory
2. Copy files to BeamNG.drive levels directory:
   ```
   <BeamNG.drive>/levels/<map_name>/
   ```
3. Required files:
   - `main.level.json` - Main level configuration
   - `<map_name>_heightmap.png` - Terrain heightmap
   - `roads.json` - Road network data
   - `objects.json` - Buildings and vegetation
   - `traffic.json` - Traffic lights and parking
   - `info.json` - Map metadata
4. Launch BeamNG.drive and load your custom map

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
- Leaflet - Interactive maps
- Leaflet.draw - Drawing tools
- Vanilla JavaScript

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

- [ ] Real satellite imagery download and analysis
- [ ] AI-optimized traffic route generation
- [ ] Support for custom object prefabs
- [ ] Export to other game engines (Unreal, Unity)
- [ ] Map preview generation
- [ ] Batch processing for multiple areas
- [ ] Incremental updates to existing maps

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

- 🌍 **Интеграция реальных данных** - Извлечение географических данных из OpenStreetMap для любой локации
- 🤖 **ИИ-анализ** - Использует Qwen3-VL и Qwen3-Coder через Ollama для интеллектуального анализа местности
- 🏔️ **Генерация heightmap** - Создание детальных данных о высоте из источников SRTM
- 🛣️ **Генерация дорожной сети** - Автоматическое создание дорог с правильными типами, полосами и материалами
- 🚦 **Дорожная инфраструктура** - Размещение светофоров и создание парковок на основе данных OSM
- 🏢 **Размещение зданий** - Извлечение и позиционирование зданий с информацией о высоте
- 🌳 **Распределение растительности** - Генерация деревьев и зон растительности на основе анализа местности
- 🎮 **Экспорт в BeamNG.drive** - Вывод всех данных в форматы, совместимые с BeamNG.drive
- 🌐 **Веб-интерфейс** - Интерактивный выбор области с интеграцией Leaflet
- 🐳 **Поддержка Docker** - Полная контейнеризация с Docker Compose

### 🏗️ Архитектура

```
RealWorldMapGen-BNG/
├── realworldmapgen/              # Основной Python-пакет
│   ├── ai/                       # Модули ИИ-интеграции
│   ├── osm/                      # Извлечение данных OpenStreetMap
│   ├── elevation/                # Генерация heightmap
│   ├── exporters/                # Экспортеры в BeamNG.drive
│   ├── api/                      # FastAPI бэкенд
│   └── generator.py              # Главный оркестратор
├── frontend/                     # Веб-интерфейс
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

1. Откройте браузер: `http://localhost:8080`
2. Используйте инструмент прямоугольника для выбора области на карте
3. Настройте параметры генерации:
   - Название карты
   - Разрешение heightmap (1024/2048/4096)
   - Включение/отключение функций (ИИ, дороги, светофоры, здания и т.д.)
4. Нажмите "Generate Map"
5. Скачайте сгенерированные файлы после завершения

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
    "enable_ai_analysis": true,
    "enable_roads": true,
    "enable_traffic_lights": true,
    "enable_parking": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

### 🎮 Импорт в BeamNG.drive

1. Найдите сгенерированную карту в директории `output/<название_карты>/`
2. Скопируйте файлы в папку уровней BeamNG.drive:
   ```
   <BeamNG.drive>/levels/<название_карты>/
   ```
3. Необходимые файлы:
   - `main.level.json` - Конфигурация уровня
   - `<название_карты>_heightmap.png` - Heightmap ландшафта
   - `roads.json` - Данные дорожной сети
   - `objects.json` - Здания и растительность
   - `traffic.json` - Светофоры и парковки
   - `info.json` - Метаданные карты
4. Запустите BeamNG.drive и загрузите вашу карту

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
- Leaflet - Интерактивные карты
- Leaflet.draw - Инструменты рисования
- Vanilla JavaScript

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

- [ ] Реальная загрузка и анализ спутниковых снимков
- [ ] ИИ-оптимизированная генерация маршрутов трафика
- [ ] Поддержка пользовательских префабов объектов
- [ ] Экспорт в другие игровые движки (Unreal, Unity)
- [ ] Генерация превью карты
- [ ] Пакетная обработка нескольких областей
- [ ] Инкрементальные обновления существующих карт

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
