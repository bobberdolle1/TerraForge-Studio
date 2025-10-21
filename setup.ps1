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
Start-Sleep -Seconds 5

# Check if Ollama is installed locally
Write-Host "🔍 Checking for local Ollama installation..." -ForegroundColor Yellow
$ollamaInstalled = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaInstalled) {
    Write-Host "⚠️  Ollama is not installed locally" -ForegroundColor Yellow
    Write-Host "   Download and install from: https://ollama.ai" -ForegroundColor Cyan
    Write-Host "   Cloud models (qwen3-vl:235b-cloud, qwen3-coder:480b-cloud) will be used automatically" -ForegroundColor White
} else {
    Write-Host "✓ Ollama is installed" -ForegroundColor Green
    
    # Check if Ollama is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "✓ Ollama service is running" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Ollama is not running. Start it with: ollama serve" -ForegroundColor Yellow
    }
}

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
