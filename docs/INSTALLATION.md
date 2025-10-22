# Installation & Setup Guide

Complete installation guide for RealWorldMapGen-BNG.

## Prerequisites

### Required
- **Python 3.13+** - Programming language runtime
- **Poetry** - Python dependency management
- **Ollama** - AI model runtime (install locally)
- **Git** - For cloning repository

### Optional
- **Mapbox API Key** - For high-quality satellite imagery
- **Bing Maps API Key** - Alternative satellite imagery provider

---

## Quick Start (Recommended)

### Windows

```powershell
# 1. Clone repository
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG

# 2. Run the application (automatically installs dependencies)
.\run.ps1        # Start
.\run.ps1 stop   # Stop
.\run.ps1 status # Check status
```

### Linux/Mac

```bash
# 1. Clone repository
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG

# 2. Run the application (automatically installs dependencies)
chmod +x run.sh
./run.sh         # Start
./run.sh stop    # Stop
./run.sh status  # Check status
```

**What the script does automatically:**
- ✅ Checks Python and Poetry installation
- ✅ Installs Poetry if needed (requires terminal restart)
- ✅ Creates `.env` configuration from template
- ✅ Creates output and cache directories
- ✅ Installs Python dependencies
- ✅ Checks for Ollama
- ✅ Starts backend and frontend services

---

## Manual Installation

### Step 1: Install Ollama

**Windows:**
1. Download from https://ollama.ai
2. Run installer
3. Verify installation:
```powershell
ollama --version
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Mac:**
```bash
brew install ollama
```

### Step 2: Start Ollama

```bash
# Start Ollama server
ollama serve
```

Keep this terminal open. Ollama needs to be running for AI features.

### Step 3: Configure Environment

```bash
# Create .env file from template
cp .env.example .env

# Edit .env (optional)
nano .env
```

**Key settings:**
```env
# Ollama configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_VISION_MODEL=qwen3-vl:235b-cloud
OLLAMA_CODER_MODEL=qwen3-coder:480b-cloud

# Map generation
DEFAULT_RESOLUTION=2048
MAX_AREA_KM2=100.0

# Optional: Satellite imagery providers
MAPBOX_ACCESS_TOKEN=your_token_here
BING_MAPS_KEY=your_key_here
```

### Step 4: Install Dependencies

```bash
# Install project dependencies
poetry install
```

### Step 5: Start Services

**Terminal 1 - Backend API:**
```bash
poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 8080
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8080
```

### Step 6: Verify Installation

**Check services:**
```bash
# API health check
curl http://localhost:8000/api/health

# Expected response:
# {"status":"healthy","ollama":{"available":true}}
```

**Access interfaces:**
- Frontend: http://localhost:8080
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Ollama Model Setup

The app uses cloud models by default, but you can pull them locally:

```bash
# Vision model (for terrain analysis)
ollama pull qwen3-vl:235b-cloud

# Coder model (for traffic optimization)
ollama pull qwen3-coder:480b-cloud
```

**Note:** Cloud models are accessed via API and don't require local download.

---

## Troubleshooting

### Ollama Not Detected

**Symptom:** API shows `ollama.available: false`

**Solutions:**
1. Verify Ollama is running:
   ```bash
   ollama serve
   ```

2. Check connection:
   - Ollama must be accessible at `http://localhost:11434`
   - Check Firewall settings

3. Test manually:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Poetry Installation Issues

**Poetry not found:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Or on Windows (PowerShell):
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Dependency conflicts:**
```bash
# Clear Poetry cache
poetry cache clear pypi --all
poetry install
```

### Port Already in Use

**Change backend port:**
```bash
poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8001
```

**Change frontend port:**
```bash
cd frontend
python -m http.server 8081
```

### OSM Extraction Errors

**Symptom:** Errors when generating maps

**Solutions:**
1. Check internet connection (OSM data download)
2. Verify bbox coordinates are valid
3. Reduce area size (< 100 km²)
4. Check backend terminal output for errors

### Permission Errors (Linux)

```bash
# Fix output directory permissions
sudo chown -R $USER:$USER output/
sudo chmod -R 755 output/
```

---

## Development Setup

### Enable Hot Reload

**Backend with auto-reload:**
```bash
poetry run uvicorn realworldmapgen.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
For frontend changes, just refresh the browser - no build step needed.

### Run Tests

```bash
# Install dev dependencies
poetry install --with dev

# Run tests (when implemented)
poetry run pytest
```

### Update Dependencies

```bash
# Update all packages
poetry update

# Update specific package
poetry update osmnx

# Restart the backend after updates
# Stop with Ctrl+C and run again:
poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000
```

---

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_VISION_MODEL` | `qwen3-vl:235b-cloud` | Vision model for imagery |
| `OLLAMA_CODER_MODEL` | `qwen3-coder:480b-cloud` | Coder model for optimization |
| `DEFAULT_RESOLUTION` | `2048` | Default heightmap resolution |
| `MAX_AREA_KM2` | `100.0` | Maximum allowed area |
| `ENABLE_AI_ANALYSIS` | `true` | Enable AI features |
| `PARALLEL_PROCESSING` | `true` | Enable parallel processing |
| `MAX_WORKERS` | `4` | Number of parallel workers |

---

## Updating

### Pull Latest Changes

```bash
# Get updates
git pull origin main

# Update dependencies
poetry install

# Restart services
# Stop with Ctrl+C in both terminals and start again
```

### Database/Cache Reset

```bash
# Clear all caches
rm -rf cache/*
rm -rf output/*

# Restart services (stop with Ctrl+C and start again)
```

---

## Uninstallation

```bash
# Remove project directory
cd ..
rm -rf RealWorldMapGen-BNG

# Uninstall Ollama (optional)
# Windows: Use "Add or Remove Programs"
# Linux: Follow Ollama uninstall instructions
# Mac: brew uninstall ollama

# Remove Poetry environment (optional)
poetry env remove python
```

---

## Next Steps

After installation:

1. **Test the System:**
   - Open http://localhost:8080
   - Select a small area on the map
   - Click "Generate Map"
   - Download the .zip file

2. **Read Documentation:**
   - [API Examples](API_EXAMPLES.md) - API usage guide
   - [README](README.md) - Project overview

3. **Install Map in BeamNG.drive:**
   - Extract downloaded .zip to `<BeamNG.drive>/mods/`
   - Launch BeamNG.drive
   - Select your custom map

4. **Experiment:**
   - Try different resolutions
   - Enable/disable AI analysis
   - Test different locations
   - Batch generate multiple maps

---

## Support

- **Issues:** https://github.com/bobberdolle1/RealWorldMapGen-BNG/issues
- **Documentation:** https://github.com/bobberdolle1/RealWorldMapGen-BNG/wiki
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)
