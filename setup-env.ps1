# PowerShell script to setup .env file for Windows users

Write-Host "🚀 RealWorldMapGen-BNG Environment Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if .env already exists
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "❌ Setup cancelled" -ForegroundColor Red
        exit
    }
}

# Create .env file
$envContent = @"
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
"@

Set-Content -Path ".env" -Value $envContent

Write-Host "✅ .env file created successfully!`n" -ForegroundColor Green

# Check if Ollama is installed
Write-Host "🔍 Checking Ollama installation..." -ForegroundColor Cyan
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama is installed: $ollamaVersion" -ForegroundColor Green
    
    # Check if Ollama is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2
        Write-Host "✅ Ollama is running" -ForegroundColor Green
        
        # List available models
        Write-Host "`n📦 Checking available models..." -ForegroundColor Cyan
        $models = ollama list
        Write-Host $models
        
        # Check for required models
        $hasVision = $models -match "llama3.2-vision"
        $hasCoder = $models -match "qwen2.5-coder"
        
        if (-not $hasVision) {
            Write-Host "`n⚠️  Vision model not found. Pull it with:" -ForegroundColor Yellow
            Write-Host "   ollama pull llama3.2-vision" -ForegroundColor White
        }
        
        if (-not $hasCoder) {
            Write-Host "`n⚠️  Coder model not found. Pull it with:" -ForegroundColor Yellow
            Write-Host "   ollama pull qwen2.5-coder" -ForegroundColor White
        }
        
        if ($hasVision -and $hasCoder) {
            Write-Host "`n✅ All required models are available!" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️  Ollama is not running. Start it with: ollama serve" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Ollama is not installed!" -ForegroundColor Red
    Write-Host "   Install from: https://ollama.ai" -ForegroundColor White
}

Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure Ollama is running: ollama serve" -ForegroundColor White
Write-Host "2. Pull required models:" -ForegroundColor White
Write-Host "   ollama pull llama3.2-vision" -ForegroundColor Gray
Write-Host "   ollama pull qwen2.5-coder" -ForegroundColor Gray
Write-Host "3. Start the application:" -ForegroundColor White
Write-Host "   docker-compose up --build" -ForegroundColor Gray
Write-Host "   OR" -ForegroundColor Gray
Write-Host "   poetry install; poetry run uvicorn realworldmapgen.api.main:app" -ForegroundColor Gray
Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green

