# 🚀 Быстрый старт RealWorldMapGen-BNG

## ⚡ Быстрая установка и запуск

### Вариант 1: Запуск через Docker (Рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG

# 2. Создайте файл .env (ВАЖНО!)
# На Windows:
copy .env.example .env
# На Linux/Mac:
cp .env.example .env

# 3. Отредактируйте .env (укажите корректные модели Ollama)
# Откройте .env в редакторе и измените:
# OLLAMA_VISION_MODEL=llama3.2-vision
# OLLAMA_CODER_MODEL=qwen2.5-coder

# 4. Запустите Ollama (в отдельном терминале)
ollama serve

# 5. Скачайте модели Ollama
ollama pull llama3.2-vision
ollama pull qwen2.5-coder

# 6. Запустите приложение через Docker
docker-compose up --build

# 7. Откройте браузер
# Frontend: http://localhost:8080
# API: http://localhost:8000/docs
```

### Вариант 2: Локальная установка (без Docker)

```bash
# 1. Установите зависимости системы
# На Ubuntu/Debian:
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev libspatialindex-dev python3-pip

# На Windows: установите OSGeo4W
# https://trac.osgeo.org/osgeo4w/

# 2. Установите Poetry
curl -sSL https://install.python-poetry.org | python3 -
# Или на Windows:
# (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# 3. Установите зависимости Python
poetry install

# 4. Создайте .env файл
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# 5. Запустите Ollama
ollama serve

# 6. Скачайте модели
ollama pull llama3.2-vision
ollama pull qwen2.5-coder

# 7. Запустите backend
poetry run uvicorn realworldmapgen.api.main:app --reload --host 0.0.0.0 --port 8000

# 8. В отдельном терминале запустите frontend
cd frontend
python -m http.server 8080
# Или используйте любой другой HTTP сервер

# 9. Откройте браузер
# Frontend: http://localhost:8080
# API: http://localhost:8000/docs
```

## 📋 Содержимое .env файла

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
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
```

## 🎮 Использование

### 1. Выберите область на карте

- Откройте http://localhost:8080
- Используйте поиск для поиска локации
- Выберите инструмент (прямоугольник, полигон или круг)
- Нарисуйте область на карте

### 2. Настройте параметры

- Введите имя карты (только буквы, цифры, _ и -)
- Выберите разрешение heightmap
- Выберите формат экспорта
- Включите/выключите нужные опции

### 3. Сгенерируйте карту

- Нажмите "🚀 Generate Map"
- Дождитесь завершения (прогресс показывается в реальном времени)
- Скачайте готовый .zip мод для BeamNG.drive

### 4. Установите в BeamNG.drive

- Распакуйте скачанный .zip файл
- Скопируйте папку карты в: `BeamNG.drive/mods/`
- Запустите BeamNG.drive
- Ваша карта будет доступна в списке уровней!

## ❌ Решение проблем

### Ollama не подключается

```bash
# Проверьте что Ollama запущен
curl http://localhost:11434/api/tags

# Проверьте модели
ollama list

# Перезапустите Ollama
# Windows: перезапустите сервис Ollama
# Linux/Mac:
killall ollama
ollama serve
```

### Backend не запускается

```bash
# Проверьте что .env файл создан
ls -la .env  # Linux/Mac
dir .env     # Windows

# Проверьте Python версию (должна быть 3.13+)
python --version

# Переустановите зависимости
poetry install --no-cache
```

### OSM запросы падают с ошибкой

```bash
# Увеличьте таймауты в .env
OSM_TIMEOUT=300

# Уменьшите размер области
# Максимум 100 км² по умолчанию
```

### Модели Ollama не найдены

```bash
# Используйте доступные модели
ollama list

# Обновите .env с корректными именами
# Например:
OLLAMA_VISION_MODEL=llava
OLLAMA_CODER_MODEL=codellama
```

## 📚 Дополнительная информация

- **Документация API**: http://localhost:8000/docs
- **GitHub**: https://github.com/bobberdolle1/RealWorldMapGen-BNG
- **Проблемы**: https://github.com/bobberdolle1/RealWorldMapGen-BNG/issues

## 🔧 Разработка

```bash
# Запуск тестов
poetry run pytest

# Форматирование кода
poetry run black .
poetry run ruff check .

# Проверка типов
poetry run mypy realworldmapgen
```

## 📝 Примеры API запросов

### Генерация карты через API

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "moscow_center",
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

### Проверка статуса генерации

```bash
curl "http://localhost:8000/api/status/{task_id}"
```

### Скачивание карты

```bash
curl "http://localhost:8000/api/maps/{map_name}/download/zip" -o map.zip
```

---

**Наслаждайтесь созданием реалистичных карт! 🎮🗺️**

