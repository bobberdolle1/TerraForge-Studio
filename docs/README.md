# TerraForge Studio Documentation

Complete documentation for TerraForge Studio - Professional Cross-Platform 3D Terrain Generator.

## 📚 Documentation Index

### Getting Started
- **[Installation Guide](INSTALLATION.md)** - Complete setup instructions for Windows, Linux, and Mac
  - Prerequisites and dependencies
  - Quick start with automated scripts
  - Manual installation steps
  - API keys configuration
  - Troubleshooting common issues

- **[Quick Start Guide](../QUICKSTART.md)** - Get up and running in 5 minutes
  - Fastest path to first terrain
  - Basic usage examples
  - Common workflows

### API Reference
- **[API Examples](API_EXAMPLES.md)** - Comprehensive API usage guide
  - Health check endpoints
  - Terrain generation examples
  - Multi-engine export
  - Batch processing
  - File downloads
  - Task management

### Game Engine Integration
- **[Unreal Engine 5 Import](UNREAL_IMPORT.md)** - UE5 integration guide *(To be created)*
  - Heightmap import
  - Material weightmaps
  - Road splines
  - Automated Python import script

- **[Unity Import](UNITY_IMPORT.md)** - Unity integration guide *(To be created)*
  - Terrain heightmap import
  - Splatmap configuration
  - GameObject prefab placement
  - Automated C# Editor script

- **[Generic Formats](GENERIC_FORMATS.md)** - GLTF, GeoTIFF, OBJ usage *(To be created)*
  - GLTF/GLB for 3D software
  - GeoTIFF for GIS applications
  - OBJ for universal compatibility

### Advanced Topics
- **[Data Sources](DATA_SOURCES.md)** - Geospatial data sources guide *(To be created)*
  - Sentinel Hub configuration
  - OpenTopography setup
  - Azure Maps integration
  - Google Earth Engine (advanced)
  - OpenStreetMap usage

- **[3D Preview](3D_PREVIEW.md)** - Interactive 3D preview features *(To be created)*
  - CesiumJS integration
  - Real-time visualization
  - Export screenshots/videos

### Development
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
  - Development setup
  - Code style guidelines
  - Pull request process
  - Issue reporting

## 🚀 Quick Links

### For Users
1. [Quick Start Guide](../QUICKSTART.md) - **Start here!**
2. [Installation Guide](INSTALLATION.md) - Detailed setup
3. [API Examples](API_EXAMPLES.md) - Learn the API

### For Developers
1. [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines
2. [API Examples](API_EXAMPLES.md) - API development reference
3. [Installation Guide](INSTALLATION.md#development-setup) - Dev environment

### For Game Developers
1. [Unreal Engine 5 Import](UNREAL_IMPORT.md) - UE5 workflow
2. [Unity Import](UNITY_IMPORT.md) - Unity workflow
3. [Generic Formats](GENERIC_FORMATS.md) - Other engines/software

## 📖 Additional Resources

- **[GitHub Repository](https://github.com/yourusername/TerraForge-Studio)** - Source code
- **[Issue Tracker](https://github.com/yourusername/TerraForge-Studio/issues)** - Report bugs
- **[Discussions](https://github.com/yourusername/TerraForge-Studio/discussions)** - Community support
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI (when running)

## 🎯 Common Tasks

### Installing TerraForge Studio
See [Quick Start Guide](../QUICKSTART.md) or [Installation Guide](INSTALLATION.md)

### Generating Your First Terrain
1. Start application: `./run.sh` (or `.\run.ps1` on Windows)
2. Open web UI: http://localhost:3000
3. Select area on map
4. Choose export format (UE5, Unity, Generic)
5. Click "Generate Terrain"
6. Download ZIP package

### Configuring API Keys
See [Data Sources Guide](DATA_SOURCES.md) for:
- Sentinel Hub setup
- OpenTopography API key
- Azure Maps configuration
- Google Earth Engine (advanced)

### Using the API Directly
See [API Examples](API_EXAMPLES.md) for:
- Basic terrain generation
- Multi-engine export
- Batch processing
- File downloads
- Status monitoring

### Importing to Unreal Engine 5
See [UE5 Import Guide](UNREAL_IMPORT.md) for:
- Landscape import
- Material layers
- Road splines
- Automated Python script

### Importing to Unity
See [Unity Import Guide](UNITY_IMPORT.md) for:
- Terrain import
- Texture splatmaps
- GameObject placement
- Automated C# script

### Troubleshooting
Check [Installation Guide - Troubleshooting](INSTALLATION.md#troubleshooting) for:
- API connection issues
- Dependency problems
- Port conflicts
- Memory errors

## 🔧 Configuration

### Environment Variables
Key configuration files:
- `.env` - Main configuration (API keys, settings)
- `pyproject.toml` - Python dependencies
- `frontend/package.json` - Frontend dependencies

See [Installation Guide](INSTALLATION.md#configuration) for all options.

### Data Source Priority
Configure which elevation sources to use:
```env
# In .env file
ELEVATION_SOURCE_PRIORITY=opentopography,srtm,aster
```

See [Data Sources Guide](DATA_SOURCES.md) for detailed comparison.

### Export Defaults
Configure default settings for each game engine:
```env
# Unreal Engine 5
UE5_DEFAULT_LANDSCAPE_SIZE=2017
UE5_EXPORT_WEIGHTMAPS=true

# Unity
UNITY_DEFAULT_TERRAIN_SIZE=2049
UNITY_EXPORT_SPLATMAPS=true
```

## 📊 Comparison Tables

### Supported Export Formats

| Format | Engine | Heightmap | Materials | Roads | Buildings | Trees |
|--------|--------|-----------|-----------|-------|-----------|-------|
| **UE5** | Unreal Engine 5 | ✅ 16-bit PNG/RAW | ✅ Weightmaps | ✅ Splines | ✅ Static Meshes | ✅ Foliage |
| **Unity** | Unity | ✅ RAW 16-bit | ✅ Splatmaps | ✅ Prefabs | ✅ GameObjects | ✅ Terrain Details |
| **GLTF** | Generic | ✅ Mesh | ✅ PBR Materials | ❌ No | ✅ Meshes | ✅ Meshes |
| **GeoTIFF** | GIS Software | ✅ Raster | ❌ No | ❌ No | ❌ No | ❌ No |
| **OBJ** | 3D Software | ✅ Mesh | ❌ No | ❌ No | ✅ Meshes | ✅ Meshes |

### Data Sources

| Source | Type | Resolution | API Key | Free Tier |
|--------|------|------------|---------|-----------|
| OpenStreetMap | Vector | N/A | ❌ No | ✅ Unlimited |
| SRTM | Elevation | 30m-90m | ❌ No | ✅ Unlimited |
| Sentinel Hub | Imagery | 10m-60m | ✅ Yes | 🟡 Limited |
| OpenTopography | Elevation | 0.5m-30m | ✅ Yes | ✅ Generous |
| Azure Maps | Vector | Varies | ✅ Yes | 🟡 Limited |
| Google Earth Engine | Analysis | Varies | ✅ Yes | 🟡 Complex |

## 📝 Documentation Format

All documentation follows these conventions:
- **Headers**: Use `#` for main sections, `##` for subsections
- **Code blocks**: Triple backticks with language specifier
- **Links**: Relative paths for internal docs
- **Examples**: Practical, runnable examples
- **Notes**: Use blockquotes for important info

## 🤝 Contributing to Documentation

Found an error or want to improve the docs?
1. Edit the relevant `.md` file
2. Submit a pull request
3. See [Contributing Guide](CONTRIBUTING.md) for details

## 📋 Documentation TODO

Documents to be created:
- [ ] UNREAL_IMPORT.md - Detailed UE5 import guide
- [ ] UNITY_IMPORT.md - Detailed Unity import guide
- [ ] GENERIC_FORMATS.md - GLTF/GeoTIFF/OBJ usage
- [ ] DATA_SOURCES.md - Data sources configuration
- [ ] 3D_PREVIEW.md - 3D preview features
- [ ] PERFORMANCE.md - Optimization guide
- [ ] CUSTOM_MATERIALS.md - Material customization

---

**[⬅ Back to Main README](../README.md)**
