# 🪟 Windows Setup Guide - RealWorldMapGen-BNG

## 📋 Quick Start (Recommended)

### Step 1: Install Prerequisites

1. **Python 3.13+**
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Ollama** (Optional, for AI features)
   - Download from: https://ollama.ai
   - Run after installation: `ollama serve`

### Step 2: Run Setup

```powershell
# Clone the repository
git clone https://github.com/bobberdolle1/RealWorldMapGen-BNG.git
cd RealWorldMapGen-BNG

# Run setup (installs Poetry + all dependencies)
.\setup.ps1
```

### Step 3: Start the Application

```powershell
# Start both backend and frontend
.\run.ps1

# Or use individual commands:
.\run.ps1 start   # Start services
.\run.ps1 stop    # Stop services
.\run.ps1 status  # Check status
.\run.ps1 restart # Restart services
```

### Step 4: Access the Application

- **Frontend**: http://localhost:8080
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔧 Manual Installation (Alternative)

If automatic setup doesn't work, follow these steps:

### 1. Install Poetry

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Close and reopen your terminal after installation.

### 2. Install Dependencies

```powershell
# Create virtual environment
poetry install --no-root

# Install core packages (bypasses GDAL issues on Windows)
poetry run pip install fastapi uvicorn pydantic pydantic-settings requests httpx numpy scipy pillow shapely pyproj networkx ollama aiofiles python-multipart osmnx pandas --no-deps

# Install sub-dependencies
poetry run pip install starlette websockets watchfiles httptools python-dotenv colorama
```

### 3. Create Configuration

```powershell
# Copy environment file
Copy-Item .env.example .env

# Create directories
New-Item -ItemType Directory -Force -Path output, cache
```

### 4. Start Services

```powershell
# Terminal 1: Start backend
poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
python -m http.server 8080
```

---

## ⚠️ Common Issues

### Issue: "GDAL_VERSION must be provided"

**Solution**: The setup scripts automatically bypass this by installing packages without GDAL dependencies.

If you still see this error:
```powershell
# Don't use: poetry install
# Instead use: .\setup.ps1
```

### Issue: "uvloop does not support Windows"

**Solution**: uvloop is a Linux-only package. The scripts automatically skip it on Windows.

### Issue: "Poetry not found"

**Solution**: After installing Poetry, close and reopen your terminal.

### Issue: Port already in use

```powershell
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# Kill the process
taskkill /PID <process_id> /F
```

---

## 📝 Notes for Windows Users

1. **GDAL/Rasterio**: Not used in this project anymore. Removed to improve Windows compatibility.

2. **GeoPandas**: Installed without pyogrio dependency to avoid GDAL requirements.

3. **uvloop**: Skipped on Windows (it's Linux-only). Uvicorn uses fallback event loop.

4. **Poetry vs pip**: The project uses Poetry for dependency management, but setup scripts use pip for problematic packages.

---

## 🎯 Next Steps

After setup, check out:
- [Quick Start Guide](QUICKSTART.md) - How to generate your first map
- [API Examples](docs/API_EXAMPLES.md) - Using the REST API
- [Contributing Guide](docs/CONTRIBUTING.md) - How to contribute

---

## 🆘 Need Help?

If you encounter any issues:

1. Check if services are running:
   ```powershell
   .\run.ps1 status
   ```

2. View API health:
   ```powershell
   curl http://localhost:8000/api/health
   ```

3. Check logs in the terminal windows

4. Report issues: https://github.com/bobberdolle1/RealWorldMapGen-BNG/issues

