# 🌍 TerraForge Studio v4.0

<div align="center">

![Version](https://img.shields.io/badge/version-4.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-production%20ready-success.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Professional 3D Terrain & Real-World Map Generator**

Supports Unreal Engine 5, Unity, GLTF, GeoTIFF, and more

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Roadmap](#-roadmap)

</div>

---

## ✨ Features

### 🎨 Modern UI/UX
- ✅ **Toast Notifications** - Beautiful, non-blocking alerts
- ✅ **8 Professional Presets** - Quick start templates
- ✅ **Generation History** - Track all your creations
- ✅ **Keyboard Shortcuts** - Full keyboard navigation
- ✅ **Dark Mode** - Light/Dark/Auto themes
- ✅ **Mobile Responsive** - Works on all devices

### ⚡ Performance & Productivity
- ✅ **WebSocket Live Updates** - Real-time progress
- ✅ **Smart Caching** - 100x faster for repeated requests
- ✅ **Cache Management UI** - Full control over cache
- ✅ **Drag & Drop** - Visual batch processing
- ✅ **Split-View Comparison** - Compare terrains side-by-side

### 🔗 Collaboration
- ✅ **Share Links** - Generate shareable URLs
- ✅ **Access Control** - Expiry dates & max access
- ✅ **Share Manager** - Manage all your links

### 🏗️ Platform Features
- ✅ **Plugin System** - Extensible architecture
- ✅ **Multi-User Support** - Authentication & sessions
- ✅ **Cloud Storage** - S3 & Azure Blob integration
- ✅ **PWA Support** - Installable app

### 📱 Multi-Platform
- ✅ **Desktop** - Full-featured interface
- ✅ **Mobile** - Optimized bottom navigation
- ✅ **Tablet** - Adaptive layout
- ✅ **PWA** - Install as app

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/TerraForge-Studio
cd TerraForge-Studio

# Backend
pip install -r requirements.txt
python -m realworldmapgen.api.main

# Frontend (new terminal)
cd frontend-new
npm install
npm run dev
```

**Access**: http://localhost:3000

### First Generation

1. **Select a Preset** - Click "Load Preset Template"
2. **Choose Area** - Draw on the map
3. **Generate** - Click "Generate Terrain"
4. **Watch Live Progress** - Via WebSocket updates
5. **Download** - Get your terrain files!

---

## 🎯 Use Cases

### 🎮 Game Development
**Presets**: Unreal Engine 5, Unity Terrain

- High-resolution heightmaps
- Material weightmaps
- Road splines
- Building prefabs
- Optimized for game engines

### 🗺️ GIS & Analysis
**Preset**: GIS Analysis

- Accurate GeoTIFF export
- Georeferenced data
- KML/KMZ support
- Professional mapping

### 🏙️ Urban Planning
**Preset**: Urban Planning

- Building footprints
- Road networks
- Infrastructure data
- City modeling

### 🏔️ Simulation & Training
**Preset**: Simulation & Training

- High-fidelity terrain
- Real-world accuracy
- Military/education use
- Training scenarios

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+G` | Quick generation |
| `Ctrl+D` | Toggle theme |
| `Ctrl+2` | 2D Map view |
| `Ctrl+3` | 3D Preview |
| `Ctrl+H` | History |
| `Ctrl+S` | Settings |
| `Ctrl+Shift+C` | Cache Manager |
| `Ctrl+Shift+S` | Share Manager |
| `Escape` | Close dialog |

*Mac: Use `⌘` instead of `Ctrl`*

---

## 📚 Documentation

### User Guides
- **Quick Start**: `docs/QUICKSTART.md`
- **Settings**: `docs/SETTINGS_GUIDE.md`
- **API Examples**: `docs/API_EXAMPLES.md`

### Technical Docs
- **Installation**: `docs/INSTALLATION.md`
- **Deployment**: `DEPLOYMENT_GUIDE_v4.0.md`
- **Contributing**: `docs/CONTRIBUTING.md`

### Changelogs
- **v3.0 - v4.0**: `COMPLETE_CHANGELOG_v3.0-v4.0.md`
- **v3.1**: `CHANGELOG_v3.1.md`
- **Full Roadmap**: `ROADMAP_COMPLETE.md`

---

## 🔌 Plugin Development

### Creating a Plugin

Create `my_plugin.py` in `./plugins/`:

```python
from realworldmapgen.core.plugin_system import TerraForgePlugin

class MyTerrainPlugin(TerraForgePlugin):
    def __init__(self):
        super().__init__()
        self.name = "MyPlugin"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "My custom plugin"
    
    def on_terrain_generated(self, terrain_data, metadata):
        """Process terrain after generation"""
        self.log_info("Processing terrain...")
        # Your logic here
        return terrain_data
    
    def on_export(self, export_data, format, metadata):
        """Modify export data"""
        # Your logic here
        return export_data
```

**Reload plugins**:
```bash
curl -X POST http://localhost:8000/api/plugins/reload
```

### Available Hooks
- `on_terrain_generated` - After terrain generation
- `on_export` - Before export
- `on_preview` - Preview generation
- `on_cache_hit` - Cache hit event
- `on_elevation_acquired` - Elevation data acquired
- `on_vector_acquired` - Vector data acquired
- `pre_process` - Before generation starts
- `post_process` - After generation completes

---

## ☁️ Cloud Storage Setup

### Amazon S3

```env
S3_ENABLED=true
S3_BUCKET_NAME=my-terraforge-bucket
S3_REGION=us-east-1
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
```

**Permissions** (IAM Policy):
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:PutObject",
      "s3:GetObject",
      "s3:DeleteObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::my-terraforge-bucket/*"
    ]
  }]
}
```

### Azure Blob Storage

```env
AZURE_BLOB_ENABLED=true
AZURE_BLOB_CONTAINER=terraforge
AZURE_BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
```

**Or with account key**:
```env
AZURE_BLOB_ACCOUNT_NAME=myaccount
AZURE_BLOB_ACCOUNT_KEY=...
```

---

## 👥 Multi-User Setup

### Enable Authentication

```env
AUTH_ENABLED=true
```

### Create Admin User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure_password"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password"
  }'
```

**Response**:
```json
{
  "session": {
    "token": "abc123...",
    "expires_at": "2025-10-23T..."
  }
}
```

### Use Token

```bash
curl -H "Authorization: Bearer abc123..." \
  http://localhost:8000/api/auth/me
```

---

## 📊 API Reference

### Core Endpoints

```
GET  /api/health          # Health check
POST /api/generate        # Start generation
GET  /api/status/{id}     # Get status
GET  /api/tasks           # List tasks
```

### Cache

```
GET  /api/cache/stats     # Cache statistics
GET  /api/cache/entries   # List entries
POST /api/cache/clear     # Clear cache
DELETE /api/cache/{key}   # Delete entry
```

### Share

```
POST /api/share/create    # Create share link
GET  /api/share/{id}      # Get share link
GET  /api/share/list      # List links
DELETE /api/share/{id}    # Delete link
```

### Plugins

```
GET  /api/plugins/list    # List plugins
POST /api/plugins/reload  # Reload plugins
POST /api/plugins/{name}/enable   # Enable
POST /api/plugins/{name}/disable  # Disable
```

### Auth

```
POST /api/auth/register   # Register user
POST /api/auth/login      # Login
POST /api/auth/logout     # Logout
GET  /api/auth/me         # Current user
```

### Cloud

```
GET  /api/cloud/providers # List providers
POST /api/cloud/upload    # Upload file
POST /api/cloud/upload-generation/{id}  # Upload generation
```

**Full API Docs**: http://localhost:8000/docs

---

## 🌟 Advanced Features

### Custom Presets

Edit `frontend-new/src/types/presets.ts`:

```typescript
{
  id: 'my-preset',
  name: 'My Custom Preset',
  description: '...',
  icon: '🎨',
  category: 'general',
  config: {
    resolution: 2048,
    exportFormats: ['gltf'],
    elevationSource: 'auto',
    enableRoads: true,
    enableBuildings: true,
    enableWeightmaps: true,
  },
  tags: ['custom'],
}
```

### Custom Themes

Add to `ThemeContext.tsx`:

```typescript
const themes = {
  ocean: { primary: '#0077be', secondary: '#00a8cc' },
  forest: { primary: '#228b22', secondary: '#32cd32' },
  sunset: { primary: '#ff6347', secondary: '#ffa500' },
}
```

---

## 🤝 Contributing

We welcome contributions!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

See `docs/CONTRIBUTING.md` for details.

---

## 📜 License

MIT License - see `LICENSE` file

---

## 🙏 Credits

**Core Team**: TerraForge Studio Development Team

**Libraries**:
- React, TypeScript, TailwindCSS
- FastAPI, Python
- Leaflet, Cesium
- react-hot-toast, framer-motion
- And many more...

---

## 📞 Support

- **Documentation**: `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

<div align="center">

## 🎊 **TerraForge Studio v4.0**

### The Ultimate Terrain Generation Platform

**100% Feature Complete** | **Production Ready** | **15+ Major Features**

---

Made with ❤️ by the TerraForge Studio Team

*October 22, 2025*

</div>

