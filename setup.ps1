# RealWorldMapGen-BNG Setup Script for Windows
# PowerShell script

Write-Host "🗺️  RealWorldMapGen-BNG Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

$dockerComposeInstalled = Get-Command docker-compose -ErrorAction SilentlyContinue
if (-not $dockerComposeInstalled) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker and Docker Compose found" -ForegroundColor Green
Write-Host ""

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ .env file created. You can customize it if needed." -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}
Write-Host ""

# Create output and cache directories
Write-Host "📁 Creating output and cache directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path output | Out-Null
New-Item -ItemType Directory -Force -Path cache | Out-Null
Write-Host "✓ Directories created" -ForegroundColor Green
Write-Host ""

# Start Docker containers
Write-Host "🐳 Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if Ollama is running
Write-Host "🔍 Checking Ollama status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama is not responding yet. It may still be starting up." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📥 Pulling required AI models (this may take a while)..." -ForegroundColor Cyan
Write-Host "   Note: Total download size is ~50GB+" -ForegroundColor Yellow
Write-Host ""

# Pull Qwen3-VL model
Write-Host "Pulling qwen3-vl:235b-cloud..." -ForegroundColor Yellow
docker exec realworldmapgen-ollama ollama pull qwen3-vl:235b-cloud

# Pull Qwen3-Coder model
Write-Host "Pulling qwen3-coder:480b-cloud..." -ForegroundColor Yellow
docker exec realworldmapgen-ollama ollama pull qwen3-coder:480b-cloud

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8080" -ForegroundColor White
Write-Host "   API:      http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📊 View logs:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Stop services:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host ""
