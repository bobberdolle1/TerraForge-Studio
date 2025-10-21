# API Examples

Complete guide to using RealWorldMapGen-BNG API endpoints.

## Table of Contents
- [Health Check](#health-check)
- [Map Generation](#map-generation)
- [Download Files](#download-files)
- [Batch Processing](#batch-processing)
- [Task Management](#task-management)

---

## Health Check

Check API and Ollama status:

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T14:30:00Z",
  "ollama": {
    "available": true,
    "models": ["qwen3-vl:235b-cloud", "qwen3-coder:480b-cloud"]
  }
}
```

---

## Map Generation

### Basic Generation

Generate a map with default settings:

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "moscow_center",
    "bbox": {
      "north": 55.7558,
      "south": 55.7508,
      "east": 37.6173,
      "west": 37.6123
    },
    "resolution": 2048
  }'
```

### Full-Featured Generation

Enable all features with AI analysis:

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "san_francisco_downtown",
    "bbox": {
      "north": 37.8,
      "south": 37.79,
      "east": -122.4,
      "west": -122.41
    },
    "resolution": 4096,
    "enable_ai_analysis": true,
    "enable_roads": true,
    "enable_traffic_lights": true,
    "enable_parking": true,
    "enable_buildings": true,
    "enable_vegetation": true
  }'
```

Response:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 0.0,
  "current_step": "Initializing",
  "message": "Map generation started"
}
```

---

## Download Files

### Download Complete Mod Package

Ready-to-install .zip for BeamNG.drive:

```bash
curl -O http://localhost:8000/api/maps/moscow_center/download/zip
```

This creates a mod package with proper structure:
```
moscow_center.zip
├── mod.json
└── levels/
    └── moscow_center/
        ├── moscow_center_heightmap.png
        ├── roads.json
        ├── objects.json
        ├── traffic.json
        ├── info.json
        └── main.level.json
```

**Installation:**
1. Download the .zip file
2. Extract to `<BeamNG.drive>/mods/`
3. Launch BeamNG.drive
4. Select your custom map

### Download Individual Files

Download specific components:

```bash
# Heightmap (16-bit PNG)
curl -O http://localhost:8000/api/maps/moscow_center/download/heightmap

# Road network (JSON)
curl -O http://localhost:8000/api/maps/moscow_center/download/roads

# Buildings and vegetation (JSON)
curl -O http://localhost:8000/api/maps/moscow_center/download/objects

# Traffic lights and parking (JSON)
curl -O http://localhost:8000/api/maps/moscow_center/download/traffic

# Level configuration (JSON)
curl -O http://localhost:8000/api/maps/moscow_center/download/level

# Map metadata (JSON)
curl -O http://localhost:8000/api/maps/moscow_center/download/metadata
```

---

## Batch Processing

Generate multiple maps in one request:

```bash
curl -X POST http://localhost:8000/api/batch/generate \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "map_1",
      "bbox": {
        "north": 55.76,
        "south": 55.75,
        "east": 37.62,
        "west": 37.61
      },
      "resolution": 2048
    },
    {
      "name": "map_2",
      "bbox": {
        "north": 55.77,
        "south": 55.76,
        "east": 37.63,
        "west": 37.62
      },
      "resolution": 2048
    }
  ]'
```

Response:
```json
{
  "batch_id": "b7f5d9c0-1234-5678-90ab-cdef12345678",
  "total": 2,
  "tasks": [
    {
      "name": "map_1",
      "task_id": "550e8400-...",
      "status": "processing"
    },
    {
      "name": "map_2",
      "task_id": "660f9501-...",
      "status": "processing"
    }
  ]
}
```

---

## Task Management

### Check Task Status

Monitor generation progress:

```bash
curl http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65.0,
  "current_step": "Generating heightmap",
  "message": "Processing elevation data",
  "result": null
}
```

Status values:
- `processing` - Generation in progress
- `completed` - Successfully completed
- `failed` - Error occurred

### List All Tasks

```bash
curl http://localhost:8000/api/tasks
```

Response:
```json
{
  "count": 3,
  "tasks": {
    "550e8400-...": {
      "task_id": "550e8400-...",
      "status": "completed",
      "progress": 100.0
    },
    "660f9501-...": {
      "task_id": "660f9501-...",
      "status": "processing",
      "progress": 45.0
    }
  }
}
```

### List Generated Maps

View all available maps:

```bash
curl http://localhost:8000/api/maps
```

Response:
```json
{
  "maps": [
    {
      "name": "moscow_center",
      "description": "Real-world map generated from OSM data",
      "version": "1.0.0",
      "area_km2": 0.5,
      "statistics": {
        "roads": 245,
        "buildings": 128,
        "traffic_lights": 15,
        "parking_lots": 8,
        "vegetation_areas": 12
      }
    }
  ]
}
```

---

## Advanced Features

### AI-Enhanced Generation

Enable satellite imagery analysis:

```bash
# Set environment variable for Mapbox (optional, for better imagery)
export MAPBOX_ACCESS_TOKEN=your_token_here

# Generate with AI analysis
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ai_analyzed_map",
    "bbox": {
      "north": 37.8,
      "south": 37.79,
      "east": -122.4,
      "west": -122.41
    },
    "enable_ai_analysis": true
  }'
```

The AI will:
- Download satellite imagery (OSM tiles, Mapbox, or Bing)
- Analyze terrain type and characteristics
- Optimize object placement density
- Generate traffic routes intelligently

### Ollama Model Management

Check available models:

```bash
curl http://localhost:8000/api/ollama/models
```

Pull required models (if not already present):

```bash
curl -X POST http://localhost:8000/api/ollama/setup
```

---

## Error Handling

### Common Errors

**404 - Map not found:**
```json
{
  "detail": "Map not found"
}
```

**400 - Invalid file type:**
```json
{
  "detail": "Invalid file type"
}
```

**500 - Generation failed:**
```json
{
  "task_id": "...",
  "status": "failed",
  "error": "Error message here",
  "message": "Generation failed: ..."
}
```

### Validation

Area size is limited to prevent excessive resource usage:

```bash
# This will fail if area > MAX_AREA_KM2
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "huge_area",
    "bbox": {
      "north": 56.0,
      "south": 55.0,
      "east": 38.0,
      "west": 37.0
    }
  }'
```

Response:
```json
{
  "detail": "Area too large: 123.45 km² (max: 100.0 km²)"
}
```

---

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Use these interfaces to:
- Explore all endpoints
- Test requests directly in browser
- View request/response schemas
- Download OpenAPI specification

---

## Performance Tips

1. **Use appropriate resolution:**
   - 1024: Quick tests, small areas
   - 2048: Standard quality (recommended)
   - 4096: High detail (slower, larger files)

2. **Disable features you don't need:**
   - Set `enable_ai_analysis: false` for faster generation
   - Disable `enable_vegetation` for simpler maps

3. **Batch processing:**
   - Generate multiple small maps instead of one huge map
   - Process them in parallel

4. **Cache:**
   - OSM data is cached automatically
   - Satellite imagery is cached in `cache/imagery/`

---

## Examples by Use Case

### Racing Track
```json
{
  "name": "nurburgring_section",
  "bbox": {
    "north": 50.335,
    "south": 50.330,
    "east": 6.950,
    "west": 6.940
  },
  "resolution": 4096,
  "enable_roads": true,
  "enable_buildings": false,
  "enable_vegetation": true
}
```

### Urban Environment
```json
{
  "name": "city_center",
  "bbox": {
    "north": 55.756,
    "south": 55.751,
    "east": 37.618,
    "west": 37.613
  },
  "resolution": 2048,
  "enable_ai_analysis": true,
  "enable_roads": true,
  "enable_traffic_lights": true,
  "enable_parking": true,
  "enable_buildings": true,
  "enable_vegetation": true
}
```

### Scenic Route
```json
{
  "name": "mountain_road",
  "bbox": {
    "north": 46.55,
    "south": 46.50,
    "east": 7.75,
    "west": 7.70
  },
  "resolution": 4096,
  "enable_roads": true,
  "enable_vegetation": true,
  "enable_buildings": false
}
```
