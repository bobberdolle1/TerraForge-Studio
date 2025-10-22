# 🚀 TerraForge Studio - Running Instructions

## ⚡ Quick Start (5 Minutes)

### Step 1: Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys (optional - works without them)
# Required only for premium data sources:
# - SENTINELHUB_CLIENT_ID
# - OPENTOPOGRAPHY_API_KEY
# - AZURE_MAPS_SUBSCRIPTION_KEY

# For basic usage, OSM + SRTM work without any keys!
```

### Step 2: Install Dependencies

```bash
# Backend
poetry install

# Frontend
cd frontend-new
npm install
cd ..
```

### Step 3: Start Application

**Terminal 1 - Backend:**
```bash
poetry run uvicorn realworldmapgen.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend-new
npm run dev
```

### Step 4: Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📖 First Terrain Generation

### Via Web UI (Recommended)

1. Open http://localhost:3000
2. Use the **2D Map** to select an area:
   - Click the rectangle tool in the top-left
   - Draw a small rectangle (start with <10 km²)
3. Configure export in the right panel:
   - **Name:** `my_first_terrain`
   - **Format:** Unreal Engine 5 (or Unity)
   - **Resolution:** 2017 (UE5) or 2049 (Unity)
   - **Source:** Auto
4. Click **"🚀 Generate Terrain"**
5. Watch progress in real-time
6. Download when complete!

### Via API (Direct)

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_terrain",
    "bbox": {
      "north": 46.5,
      "south": 46.45,
      "east": 8.0,
      "west": 7.95
    },
    "resolution": 2017,
    "export_formats": ["unreal5"],
    "elevation_source": "auto",
    "enable_roads": true,
    "enable_buildings": true,
    "enable_weightmaps": true
  }'
```

---

## 🎮 Importing to Game Engines

### Unreal Engine 5

1. **Locate exported files:**
   ```
   output/my_first_terrain/unreal5/
   ├── my_first_terrain_heightmap.png
   ├── my_first_terrain_weightmap.png
   ├── my_first_terrain_metadata.json
   ├── my_first_terrain_import_script.py
   └── my_first_terrain_README.txt
   ```

2. **Import to UE5:**
   - Open your UE5 project
   - Landscape Mode (Shift + 2)
   - Manage → Import from File
   - Select `my_first_terrain_heightmap.png`
   - Settings: 2017x2017, Section 127x127
   - Import!

3. **Apply weightmaps:**
   - Create Landscape Material with 4 layers
   - Import `my_first_terrain_weightmap.png`
   - Channels: R=Rock, G=Grass, B=Dirt, A=Sand

### Unity

1. **Locate exported files:**
   ```
   output/my_first_terrain/unity/
   ├── my_first_terrain_heightmap.raw
   ├── my_first_terrain_metadata.json
   └── my_first_terrain_import_script.cs
   ```

2. **Import to Unity:**
   - Copy folder to `Assets/Terrains/`
   - GameObject → 3D Object → Terrain
   - Terrain Settings → Import Raw
   - Select `my_first_terrain_heightmap.raw`
   - Settings: 2049x2049, Depth 16-bit

3. **OR use auto-import:**
   - Tools → TerraForge → Import Terrain
   - Select the folder
   - Done!

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio playwright

# Install Playwright browsers
playwright install chromium

# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_frontend.py -v    # Frontend tests
pytest tests/test_api_integration.py -v  # API tests
```

**Note:** Tests require both backend and frontend to be running.

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.13+

# Reinstall dependencies
poetry install --no-cache

# Check port availability
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000
```

### Frontend won't start

```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
cd frontend-new
rm -rf node_modules package-lock.json
npm install

# Check port availability
# Port 3000 should be free
```

### Generation fails

**Check logs:**
```bash
# Backend logs show detailed error messages
# Look for:
# - "Failed to acquire elevation data" → Data source issue
# - "Area too large" → Reduce selected area
# - API key errors → Check .env configuration
```

**Common fixes:**
- Reduce area size (<25 km² for testing)
- Use default elevation source (SRTM - always works)
- Check internet connection for data downloads

### No exported files

```bash
# Check output directory
ls -la output/your_terrain_name/

# Check permissions
chmod -R 755 output/

# Check disk space
df -h
```

---

## 📊 System Requirements

### Minimum:
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Disk:** 10 GB free
- **Internet:** Required for data download

### Recommended:
- **CPU:** 8+ cores
- **RAM:** 16 GB
- **Disk:** 50 GB free (SSD)
- **Internet:** High-speed (for large areas)

---

## 🔧 Advanced Configuration

### Custom API Keys (.env)

```env
# OpenTopography (for high-res DEMs)
OPENTOPOGRAPHY_API_KEY=your_key_here
OPENTOPOGRAPHY_ENABLED=true

# Sentinel Hub (for satellite imagery)
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_secret
SENTINELHUB_ENABLED=true

# Azure Maps (for vector data)
AZURE_MAPS_SUBSCRIPTION_KEY=your_key
AZURE_MAPS_ENABLED=true
```

### Performance Tuning

```env
# Increase workers for faster processing
MAX_WORKERS=8

# Increase max area (be careful!)
MAX_AREA_KM2=200.0

# Enable caching for repeated generations
ENABLE_CACHE=true
CACHE_EXPIRY_DAYS=30
```

---

## 📝 Development Mode

### Backend with auto-reload:
```bash
poetry run uvicorn realworldmapgen.api.main:app --reload --log-level debug
```

### Frontend with HMR:
```bash
cd frontend-new
npm run dev
```

### Watch logs:
```bash
# Backend logs
tail -f logs/terraforge.log

# Or direct output
poetry run uvicorn realworldmapgen.api.main:app --reload
```

---

## 🎓 Example Workflows

### 1. Generate UE5 Landscape
```
1. Select 10 km² area in Swiss Alps
2. Format: Unreal Engine 5
3. Resolution: 4033 (large)
4. Enable: Roads, Buildings, Weightmaps
5. Generate (~5-10 minutes)
6. Import to UE5 via Python script
```

### 2. Generate Unity Terrain
```
1. Select urban area (NYC, 5 km²)
2. Format: Unity
3. Resolution: 2049
4. Enable: Roads, Buildings
5. Generate (~3-5 minutes)
6. Use C# import script
```

### 3. Export to QGIS
```
1. Select any area
2. Format: GeoTIFF
3. Any resolution
4. Generate
5. Open .tif in QGIS
6. Analyze elevation data
```

---

## 🎉 You're Ready!

Your TerraForge Studio instance is now running and ready to generate professional 3D terrains for Unreal Engine 5, Unity, and other platforms.

**Next Steps:**
- Explore different regions
- Try different export formats
- Test with various resolutions
- Integrate into your game project

**Need Help?**
- Check `docs/` for detailed guides
- See API docs at `/docs`
- Report issues on GitHub

**Happy Terrain Generation! 🌍🎮**

