# 🌐 TerraForge Studio - REST API Specification

**Version**: 4.0.0  
**Base URL**: `https://api.terraforge.studio/v1`  
**Protocol**: HTTPS  
**Format**: JSON

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Models](#models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Webhooks](#webhooks)

---

## 🔐 Authentication

All API requests require authentication using API keys.

### API Key Header
```http
Authorization: Bearer YOUR_API_KEY
```

### Get API Key
```http
POST /auth/api-keys
Content-Type: application/json

{
  "name": "My Application",
  "scopes": ["terrain:read", "terrain:write", "export:read"]
}
```

**Response:**
```json
{
  "key": "tfg_live_abc123...",
  "name": "My Application",
  "scopes": ["terrain:read", "terrain:write", "export:read"],
  "created_at": "2025-10-22T19:00:00Z"
}
```

---

## 📍 Endpoints

### **1. Terrain Generation**

#### Generate Terrain
```http
POST /terrain/generate
```

**Request Body:**
```json
{
  "bbox": {
    "north": 48.8566,
    "south": 48.8466,
    "east": 2.3522,
    "west": 2.3422
  },
  "resolution": 30,
  "source": "srtm",
  "options": {
    "apply_smoothing": true,
    "fill_voids": true
  }
}
```

**Response:**
```json
{
  "id": "gen_abc123",
  "status": "processing",
  "progress": 0,
  "bbox": {...},
  "resolution": 30,
  "created_at": "2025-10-22T19:00:00Z",
  "estimated_completion": "2025-10-22T19:02:00Z"
}
```

#### Get Generation Status
```http
GET /terrain/generate/{id}
```

**Response:**
```json
{
  "id": "gen_abc123",
  "status": "completed",
  "progress": 100,
  "result": {
    "heightmap_url": "https://cdn.terraforge.studio/...",
    "metadata": {
      "min_elevation": 30.5,
      "max_elevation": 120.8,
      "area_km2": 1.23
    }
  }
}
```

---

### **2. Export**

#### Export Terrain
```http
POST /export
```

**Request Body:**
```json
{
  "generation_id": "gen_abc123",
  "format": "godot",
  "options": {
    "meshSubdivision": 128,
    "heightScale": 1.0,
    "generateCollision": true
  }
}
```

**Response:**
```json
{
  "id": "exp_xyz789",
  "format": "godot",
  "status": "processing",
  "download_url": null,
  "created_at": "2025-10-22T19:00:00Z"
}
```

#### Get Export Status
```http
GET /export/{id}
```

**Response:**
```json
{
  "id": "exp_xyz789",
  "status": "completed",
  "format": "godot",
  "download_url": "https://cdn.terraforge.studio/exports/exp_xyz789.tres",
  "file_size": 1024000,
  "expires_at": "2025-10-29T19:00:00Z"
}
```

#### List Available Formats
```http
GET /export/formats
```

**Response:**
```json
{
  "formats": [
    {
      "id": "godot",
      "name": "Godot Engine",
      "category": "game-engine",
      "extensions": [".tres", ".res"]
    },
    {
      "id": "unity",
      "name": "Unity Engine",
      "category": "game-engine",
      "extensions": [".raw"]
    },
    {
      "id": "unreal",
      "name": "Unreal Engine 5",
      "category": "game-engine",
      "extensions": [".png"]
    }
  ]
}
```

---

### **3. History**

#### Get Generation History
```http
GET /history?limit=10&offset=0
```

**Response:**
```json
{
  "items": [
    {
      "id": "gen_abc123",
      "bbox": {...},
      "status": "completed",
      "created_at": "2025-10-22T19:00:00Z"
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

---

### **4. Cache**

#### Get Cache Stats
```http
GET /cache/stats
```

**Response:**
```json
{
  "total_entries": 150,
  "total_size_bytes": 52428800,
  "hit_rate": 0.85,
  "avg_generation_time_ms": 2500
}
```

#### Clear Cache
```http
DELETE /cache
```

**Response:**
```json
{
  "success": true,
  "entries_removed": 150,
  "space_freed_bytes": 52428800
}
```

---

### **5. Webhooks**

#### Create Webhook
```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/terraforge",
  "events": ["generation.completed", "export.completed"],
  "secret": "your_webhook_secret"
}
```

**Response:**
```json
{
  "id": "wh_abc123",
  "url": "https://your-app.com/webhooks/terraforge",
  "events": ["generation.completed", "export.completed"],
  "created_at": "2025-10-22T19:00:00Z"
}
```

#### List Webhooks
```http
GET /webhooks
```

#### Delete Webhook
```http
DELETE /webhooks/{id}
```

---

## 📦 Models

### BoundingBox
```json
{
  "north": 48.8566,
  "south": 48.8466,
  "east": 2.3522,
  "west": 2.3422
}
```

### GenerationStatus
```json
{
  "id": "string",
  "status": "pending | processing | completed | failed",
  "progress": 0-100,
  "bbox": "BoundingBox",
  "resolution": "number",
  "source": "srtm | aster | nasadem",
  "created_at": "ISO 8601",
  "completed_at": "ISO 8601 | null",
  "error": "string | null"
}
```

### ExportResult
```json
{
  "id": "string",
  "format": "godot | unity | unreal | ...",
  "status": "pending | processing | completed | failed",
  "download_url": "string | null",
  "file_size": "number | null",
  "created_at": "ISO 8601",
  "expires_at": "ISO 8601"
}
```

---

## ❌ Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_BBOX",
    "message": "The provided bounding box is invalid",
    "details": {
      "field": "bbox.north",
      "reason": "Must be between -90 and 90"
    }
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_BBOX` | 400 | Invalid bounding box |
| `INVALID_FORMAT` | 400 | Unsupported export format |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## ⏱️ Rate Limiting

**Limits:**
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise: Unlimited

**Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1698000000
```

When exceeded:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}
```

---

## 🔔 Webhooks

### Events

#### `generation.started`
```json
{
  "event": "generation.started",
  "data": {
    "id": "gen_abc123",
    "bbox": {...}
  },
  "timestamp": "2025-10-22T19:00:00Z"
}
```

#### `generation.completed`
```json
{
  "event": "generation.completed",
  "data": {
    "id": "gen_abc123",
    "status": "completed",
    "result": {
      "heightmap_url": "https://...",
      "metadata": {...}
    }
  },
  "timestamp": "2025-10-22T19:02:00Z"
}
```

#### `generation.failed`
```json
{
  "event": "generation.failed",
  "data": {
    "id": "gen_abc123",
    "error": "Generation timeout"
  },
  "timestamp": "2025-10-22T19:05:00Z"
}
```

#### `export.completed`
```json
{
  "event": "export.completed",
  "data": {
    "id": "exp_xyz789",
    "format": "godot",
    "download_url": "https://..."
  },
  "timestamp": "2025-10-22T19:03:00Z"
}
```

### Webhook Signature

All webhooks include a signature header:
```http
X-TerraForge-Signature: sha256=abc123...
```

**Verify:**
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 📝 Examples

### Python
```python
import requests

API_KEY = "tfg_live_abc123..."
BASE_URL = "https://api.terraforge.studio/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Generate terrain
response = requests.post(
    f"{BASE_URL}/terrain/generate",
    json={
        "bbox": {
            "north": 48.8566,
            "south": 48.8466,
            "east": 2.3522,
            "west": 2.3422
        },
        "resolution": 30
    },
    headers=headers
)

generation = response.json()
print(f"Generation ID: {generation['id']}")
```

### JavaScript
```javascript
const API_KEY = "tfg_live_abc123...";
const BASE_URL = "https://api.terraforge.studio/v1";

const response = await fetch(`${BASE_URL}/terrain/generate`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${API_KEY}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    bbox: {
      north: 48.8566,
      south: 48.8466,
      east: 2.3522,
      west: 2.3422
    },
    resolution: 30
  })
});

const generation = await response.json();
console.log(`Generation ID: ${generation.id}`);
```

### cURL
```bash
curl -X POST https://api.terraforge.studio/v1/terrain/generate \
  -H "Authorization: Bearer tfg_live_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "bbox": {
      "north": 48.8566,
      "south": 48.8466,
      "east": 2.3522,
      "west": 2.3422
    },
    "resolution": 30
  }'
```

---

**Last Updated**: 22 October 2025  
**Version**: 4.0.0  
**Status**: Draft

<div align="center">

[Back to Docs](../README.md) • [Examples](./API_EXAMPLES.md) • [SDKs](#)

</div>
