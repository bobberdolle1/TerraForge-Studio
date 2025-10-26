# 🌍 TerraForge Studio

**Professional 3D Terrain Generator for Game Engines**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://react.dev)
[![Tauri](https://img.shields.io/badge/tauri-2.0+-FFC131.svg)](https://tauri.app)
[![FastAPI](https://img.shields.io/badge/fastapi-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Создавайте реалистичные 3D ландшафты на основе реальных геоданных для Unreal Engine 5, Unity и других игровых движков.

![TerraForge Studio](docs/images/screenshot.png)

---

## ✨ Возможности

### 🗺️ Картографирование
- **Интерактивная 2D карта** - Leaflet с поддержкой OSM, спутниковых снимков, гибридного режима
- **3D превью** - Cesium для предпросмотра рельефа в реальном времени
- **Выделение областей** - Rectangle/Polygon инструменты с сохранением между сеансами
- **Типы карт** - OpenStreetMap, Satellite, Hybrid (спутник + названия), Topographic

### 🎮 Экспорт для движков
- **Unreal Engine 5** - оптимизированные landscape (1009, 2017, 4033, 8129)
- **Unity** - terrain heightmaps (513, 1025, 2049, 4097)
- **GLTF 2.0** - универсальный 3D формат
- **GeoTIFF** - для GIS и картографических приложений

### 🤖 AI Интеграция (опционально)
- **Qwen3-VL** - анализ местности по спутниковым снимкам
- **Qwen3-Coder** - умная генерация конфигураций
- **Ollama** - локальный запуск моделей через cloud API
- **Автоанализ** - опциональный автоматический анализ при выборе области

### ⚙️ Настройки и управление
- **Data Sources** - интеграция с SentinelHub, OpenTopography, Azure Maps, Google Earth Engine
- **Export Profiles** - настраиваемые профили для разных движков
- **Локализация** - полная поддержка English/Русский
- **Темы** - Light/Dark/Auto режимы  

---

## 🚀 Быстрый старт

### Требования
- Python 3.10+
- Node.js 18+
- Rust (для Tauri)

### 1. Backend (FastAPI)

```powershell
cd TerraForge-Studio
.venv\Scripts\activate  # Windows
python -m uvicorn realworldmapgen.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend (React + Tauri)

```powershell
cd frontend-new
npm install
npm run build
npm run tauri:dev

# Frontend
cd frontend-new && npm install && npm run dev

# Backend
pip install -r requirements.txt
uvicorn realworldmapgen.api.main:app --reload

# Visit http://localhost:5173
```

**Смотрите [Руководство по быстрому старту](docs/QUICK_START.md) для подробных инструкций.**  
**See [Quick Start Guide](docs/QUICK_START.md) for detailed instructions.**

---

## 📚 Документация / Documentation

- **[Быстрый старт / Quick Start](docs/QUICK_START.md)** - Начните работу за 5 минут / Get running in 5 minutes
- **[Руководство по сборке / Build Guide](BUILD.md)** - Сборка .exe и бинарников / Building .exe and binaries
- **[Спецификация API / API Specification](docs/API_SPECIFICATION.md)** - Полная документация REST API / Complete REST API docs
- **[Руководство по развертыванию / Deployment Guide](docs/DEPLOYMENT.md)** - Production развертывание / Production deployment
- **[Руководство по экспортерам / Exporters Guide](docs/EXPORTERS_GUIDE.md)** - Интеграция с игровыми движками / Game engine integration
- **[Полная документация / Full Documentation](docs/README.md)** - Индекс всей документации / Complete documentation index

---

## 🎯 Технологический стек / Technology Stack

**Frontend / Фронтенд**: React 18 + TypeScript + Vite + TailwindCSS  
**Backend / Бэкенд**: FastAPI (Python 3.10+) + Pydantic  
**Maps / Карты**: Leaflet + Cesium  
**Desktop / Десктоп**: Tauri 2.0  
**AI / ИИ**: Ollama + Qwen3 models (опционально / optional)

---

## 🎮 Форматы экспорта / Export Formats

- **Unreal Engine 5** - PNG landscape (1009, 2017, 4033, 8129)
- **Unity** - RAW heightmap (513, 1025, 2049, 4097)
- **GLTF 2.0** - Универсальный 3D формат / Universal 3D format
- **GeoTIFF** - Для GIS приложений / For GIS applications

---

## 🎯 Использование / Usage

### 1. Выбор области / Select Area
1. Откройте 2D Map Selector / Open 2D Map Selector
2. Выберите тип карты (OSM/Satellite/Hybrid) / Choose map type
3. Используйте Rectangle или Polygon / Use Rectangle or Polygon tool
4. Нарисуйте область на карте / Draw area on map
5. Выделение сохраняется автоматически / Selection is saved automatically

### 2. Настройка экспорта / Configure Export
1. Export Configuration → параметры / parameters
2. Выберите формат (UE5/Unity/GLTF) / Choose format
3. Настройте разрешение / Set resolution
4. Включите нужные features / Enable features

### 3. Генерация / Generation
1. Нажмите Generate Terrain / Click Generate Terrain
2. Следите за прогрессом / Monitor progress
3. Скачайте результат / Download result  

---

## 🤖 AI Ассистент / AI Assistant (опционально / optional)

Для использования AI функций / To use AI features:

1. Установите Ollama / Install Ollama: https://ollama.ai
2. Запустите сервер / Start server: `ollama serve`
3. Установите модели / Install models:
   ```bash
   ollama pull qwen3-vl:235b-cloud
   ollama pull qwen3-coder:480b-cloud
   ```
4. Settings → AI Assistant → Enable → Save
5. Страница перезагрузится автоматически / Page will reload automatically

Подробнее / More info: [OLLAMA_SETUP.md](OLLAMA_SETUP.md)

---

## 🤝 Участие в разработке / Contributing

Мы приветствуем вклад в проект! / We welcome contributions!  
Смотрите / See [CONTRIBUTING.md](docs/CONTRIBUTING.md) для руководства / for guidelines.

```bash
git clone https://github.com/your-username/terraforge-studio.git
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
```

---

## 📄 Лицензия / License

MIT License - смотрите / see [LICENSE](LICENSE) для деталей / for details.

---

## 📞 Поддержка / Support

- **Документация / Documentation**: [docs/](docs/README.md)
- **Проблемы / Issues**: https://github.com/terraforge/studio/issues

---

<div align="center">

**Сделано с ❤️ bobberdolle 1**  
**Built with ❤️ by bobberdolle1**

• [Документация / Docs](docs/README.md) • [API](docs/API_SPECIFICATION.md) • 

</div>
