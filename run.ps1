# RealWorldMapGen-BNG Universal Script for Windows
# Usage: .\run.ps1 [start|stop|restart|status]

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status", "")]
    [string]$Action = "start"
)

function Show-Help {
    Write-Host "???  RealWorldMapGen-BNG Control Script" -ForegroundColor Cyan
    Write-Host "======================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 [action]" -ForegroundColor White
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  start    - Start the application (default)" -ForegroundColor White
    Write-Host "  stop     - Stop the application" -ForegroundColor White
    Write-Host "  restart  - Restart the application" -ForegroundColor White
    Write-Host "  status   - Check if services are running" -ForegroundColor White
    Write-Host ""
}

function Get-ServiceStatus {
    Write-Host "?? Checking service status..." -ForegroundColor Yellow
    Write-Host ""
    
    $backendRunning = $false
    $frontendRunning = $false
    
    # Check backend (port 8000)
    $backendProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($backendProcess) {
        Write-Host "? Backend is running on port 8000" -ForegroundColor Green
        $backendRunning = $true
    } else {
        Write-Host "? Backend is not running" -ForegroundColor Red
    }
    
    # Check frontend (port 8080)
    $frontendProcess = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($frontendProcess) {
        Write-Host "? Frontend is running on port 8080" -ForegroundColor Green
        $frontendRunning = $true
    } else {
        Write-Host "? Frontend is not running" -ForegroundColor Red
    }
    
    # Check Ollama
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "? Ollama is running" -ForegroundColor Green
    } catch {
        Write-Host "? Ollama is not running" -ForegroundColor Red
    }
    
    Write-Host ""
    return ($backendRunning -and $frontendRunning)
}

function Stop-Services {
    Write-Host "?? Stopping services..." -ForegroundColor Yellow
    Write-Host ""
    
    $stopped = $false
    
    # Stop backend
    $backendProcess = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
    if ($backendProcess) {
        Stop-Process -Id $backendProcess -Force -ErrorAction SilentlyContinue
        Write-Host "? Stopped backend" -ForegroundColor Green
        $stopped = $true
    }
    
    # Stop frontend
    $frontendProcess = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -First 1
    if ($frontendProcess) {
        Stop-Process -Id $frontendProcess -Force -ErrorAction SilentlyContinue
        Write-Host "? Stopped frontend" -ForegroundColor Green
        $stopped = $true
    }
    
    if ($stopped) {
        Write-Host ""
        Write-Host "? Services stopped" -ForegroundColor Green
    } else {
        Write-Host "??  No services were running" -ForegroundColor Cyan
    }
}

function Start-Services {
    Write-Host "???  RealWorldMapGen-BNG" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if Python is installed
    Write-Host "?? Checking Python installation..." -ForegroundColor Yellow
    $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonInstalled) {
        Write-Host "? Python is not installed. Please install Python 3.13+ first." -ForegroundColor Red
        Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
    
    $pythonVersion = python --version 2>&1
    Write-Host "? $pythonVersion found" -ForegroundColor Green
    Write-Host ""
    
    # Check if Poetry is installed
    Write-Host "?? Checking Poetry installation..." -ForegroundColor Yellow
    $poetryInstalled = Get-Command poetry -ErrorAction SilentlyContinue
    if (-not $poetryInstalled) {
        Write-Host "? Poetry is not installed. Please run setup first:" -ForegroundColor Yellow
        Write-Host "   .\setup.ps1" -ForegroundColor White
        exit 1
    }
    
    Write-Host "? Poetry found" -ForegroundColor Green
    Write-Host ""
    
    # Check if .env exists
    if (-not (Test-Path .env)) {
        Write-Host "?? Creating .env file from template..." -ForegroundColor Yellow
        if (Test-Path .env.example) {
            Copy-Item .env.example .env
            Write-Host "? .env file created" -ForegroundColor Green
        } else {
            Write-Host "? .env.example not found" -ForegroundColor Red
            exit 1
        }
        Write-Host ""
    }
    
    # Create directories
    if (-not (Test-Path output)) {
        New-Item -ItemType Directory -Force -Path output | Out-Null
    }
    if (-not (Test-Path cache)) {
        New-Item -ItemType Directory -Force -Path cache | Out-Null
    }
    
    # Check dependencies
    Write-Host "?? Checking dependencies..." -ForegroundColor Yellow
    
    # Check if critical packages are installed
    $testImport = poetry run python -c "import fastapi; import uvicorn; import pydantic" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Dependencies not installed" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "??  Please run setup first:" -ForegroundColor Yellow
        Write-Host "   .\setup.ps1" -ForegroundColor White
        Write-Host ""
        exit 1
    } else {
        Write-Host "? Dependencies are installed" -ForegroundColor Green
        Write-Host ""
    }
    
    # Check Ollama
    Write-Host "?? Checking Ollama status..." -ForegroundColor Yellow
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "? Ollama is running" -ForegroundColor Green
    } catch {
        Write-Host "??  Ollama is not running!" -ForegroundColor Yellow
        Write-Host "   Download from: https://ollama.ai" -ForegroundColor White
        Write-Host "   AI features will be limited without Ollama" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "?? Starting services..." -ForegroundColor Cyan
    Write-Host ""
    
    # Start backend
    Write-Host "?? Starting Backend API..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; poetry run uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000"
    Write-Host "   Backend will run on http://localhost:8000" -ForegroundColor White
    
    Start-Sleep -Seconds 2
    
    # Start frontend
    Write-Host "?? Starting Frontend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; python -m http.server 8080"
    Write-Host "   Frontend will run on http://localhost:8080" -ForegroundColor White
    
    Write-Host ""
    Write-Host "? Services starting!" -ForegroundColor Green
    Write-Host ""
    Write-Host "? Please wait a few seconds for services to fully start..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "?? Access the application at:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:8080" -ForegroundColor White
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "?? To stop: .\run.ps1 stop" -ForegroundColor Yellow
    Write-Host ""
}

# Main execution
switch ($Action) {
    "start" {
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Write-Host "?? Restarting services..." -ForegroundColor Cyan
        Write-Host ""
        Stop-Services
        Write-Host ""
        Start-Sleep -Seconds 2
        Start-Services
    }
    "status" {
        Get-ServiceStatus
    }
    default {
        Show-Help
    }
}
