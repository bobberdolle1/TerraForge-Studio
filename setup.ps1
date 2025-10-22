# ===================================================================
# RealWorldMapGen-BNG - First Time Setup Script for Windows
# ===================================================================

Write-Host ""
Write-Host "???  RealWorldMapGen-BNG Setup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "?? [1/5] Checking Python..." -ForegroundColor Yellow
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonInstalled) {
    Write-Host "? Python not found!" -ForegroundColor Red
    Write-Host "   Please install Python 3.13+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "? $pythonVersion found" -ForegroundColor Green
Write-Host ""

# Check Poetry
Write-Host "?? [2/5] Checking Poetry..." -ForegroundColor Yellow
$poetryInstalled = Get-Command poetry -ErrorAction SilentlyContinue
if (-not $poetryInstalled) {
    Write-Host "??  Installing Poetry..." -ForegroundColor Yellow
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    Write-Host ""
    Write-Host "? Poetry installed!" -ForegroundColor Green
    Write-Host "??  Please close this terminal and run setup.ps1 again" -ForegroundColor Yellow
    Write-Host "   (Poetry needs to be in your PATH)" -ForegroundColor Yellow
    exit 0
}
Write-Host "? Poetry found" -ForegroundColor Green
Write-Host ""

# Create .env file
Write-Host "?? [3/5] Setting up configuration..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    if (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "? Created .env file" -ForegroundColor Green
    } else {
        Write-Host "??  .env.example not found, skipping..." -ForegroundColor Yellow
    }
} else {
    Write-Host "? .env already exists" -ForegroundColor Green
}
Write-Host ""

# Create directories
if (-not (Test-Path output)) {
    New-Item -ItemType Directory -Force -Path output | Out-Null
}
if (-not (Test-Path cache)) {
    New-Item -ItemType Directory -Force -Path cache | Out-Null
}

# Install dependencies
Write-Host "?? [4/5] Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes on first run..." -ForegroundColor White
Write-Host ""

# Core packages
Write-Host "   ?? Installing core packages..." -ForegroundColor Cyan
poetry run pip install --quiet fastapi uvicorn pydantic pydantic-settings requests httpx numpy scipy pillow shapely pyproj networkx ollama aiofiles python-multipart osmnx pandas --no-deps

# Sub-dependencies
Write-Host "   ?? Installing sub-dependencies..." -ForegroundColor Cyan
poetry run pip install --quiet starlette websockets watchfiles httptools python-dotenv colorama

Write-Host "? Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check Ollama
Write-Host "?? [5/5] Checking Ollama..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "? Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "??  Ollama not running!" -ForegroundColor Yellow
    Write-Host "   Download and install from: https://ollama.ai" -ForegroundColor White
    Write-Host "   Then run: ollama serve" -ForegroundColor White
}
Write-Host ""

# Done
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" -ForegroundColor Green
Write-Host "? Setup Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "?? To start the application, run:" -ForegroundColor Cyan
Write-Host "   .\run.ps1" -ForegroundColor White
Write-Host ""
Write-Host "?? Then open your browser at:" -ForegroundColor Cyan
Write-Host "   http://localhost:8080" -ForegroundColor White
Write-Host ""

