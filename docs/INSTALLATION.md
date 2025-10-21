# Installation & Setup Guide

Complete installation guide for RealWorldMapGen-BNG.

## Prerequisites

### Required
- **Docker Desktop** (Windows/Mac) or **Docker + Docker Compose** (Linux)
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

# 2. Run setup script
.\setup.ps1
```

The script will:
- ✅ Check Docker installation
- ✅ Create `.env` configuration
- ✅ Check for Ollama
- ✅ Start Docker containers
- ✅ Verify services are running

### Linux/Mac

```bash
# 1. Clone repository
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG

# 2. Run setup script
chmod +x setup.sh
./setup.sh
```

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

### Step 4: Start Docker Services

```bash
# Build and start containers
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

You should see:
```
backend    | Application startup complete.
frontend   | Serving on port 8080
```

### Step 5: Verify Installation

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

2. Check connection (Windows with Docker):
   - Ollama must be accessible at `http://host.docker.internal:11434`
   - Check Windows Firewall settings

3. Test manually:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Docker Build Fails

**Poetry errors:**
```bash
# Clear Docker cache
docker-compose down
docker system prune -a
docker-compose up -d --build
```

**Network issues:**
```bash
# Check Docker network
docker network ls
docker network inspect realworldmapgen-bng_mapgen-network
```

### Port Already in Use

**Change ports in `docker-compose.yml`:**
```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Use 8001 instead of 8000
  
  frontend:
    ports:
      - "8081:8080"  # Use 8081 instead of 8080
```

### OSM Extraction Errors

**Symptom:** Errors when generating maps

**Solutions:**
1. Check internet connection (OSM data download)
2. Verify bbox coordinates are valid
3. Reduce area size (< 100 km²)
4. Check logs:
   ```bash
   docker-compose logs backend | grep ERROR
   ```

### Permission Errors (Linux)

```bash
# Fix output directory permissions
sudo chown -R $USER:$USER output/
sudo chmod -R 755 output/
```

---

## Development Setup

### Run Without Docker

**Prerequisites:**
- Python 3.13+
- Poetry

**Setup:**
```bash
# Install dependencies
poetry install

# Run backend
poetry run uvicorn realworldmapgen.api.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, serve frontend
cd frontend
python -m http.server 8080
```

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

# Rebuild Docker
docker-compose up -d --build
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

### Docker Compose Override

Create `docker-compose.override.yml` for custom settings:

```yaml
version: '3.8'

services:
  backend:
    environment:
      - MAX_AREA_KM2=200.0
      - DEFAULT_RESOLUTION=4096
    volumes:
      - /path/to/custom/output:/app/output
```

---

## Updating

### Pull Latest Changes

```bash
# Get updates
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build
```

### Database/Cache Reset

```bash
# Clear all caches
rm -rf cache/*
rm -rf output/*

# Restart services
docker-compose restart
```

---

## Uninstallation

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (optional - deletes cached data)
docker-compose down -v

# Remove images (optional)
docker rmi realworldmapgen-bng-backend realworldmapgen-bng-frontend

# Uninstall Ollama (optional)
# Windows: Use "Add or Remove Programs"
# Linux: Follow Ollama uninstall instructions
# Mac: brew uninstall ollama
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
