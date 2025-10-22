# TerraForge Studio - Auto-Start Script
# Automatically starts both backend and frontend

Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🌍 TerraForge Studio v1.0.0                ║" -ForegroundColor Cyan
Write-Host "║  Professional 3D Terrain Generator          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Poetry is installed
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Poetry not found. Please install Poetry first:" -ForegroundColor Red
    Write-Host "   https://python-poetry.org/docs/#installation"
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js not found. Please install Node.js 18+:" -ForegroundColor Red
    Write-Host "   https://nodejs.org/"
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green
Write-Host ""

# Check if dependencies are installed
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    poetry install
}

if (-not (Test-Path "frontend-new/node_modules")) {
    Write-Host "📦 Installing Frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend-new
    npm install
    Set-Location ..
}

Write-Host ""
Write-Host "🚀 Starting TerraForge Studio..." -ForegroundColor Green
Write-Host ""

# Start backend in new window
Write-Host "🔧 Starting Backend API..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    poetry run uvicorn realworldmapgen.api.main:app --reload --host 0.0.0.0 --port 8000
}

# Wait for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend in new window
Write-Host "🎨 Starting Frontend..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD/frontend-new
    npm run dev
}

# Wait for frontend to start
Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ TerraForge Studio is Running!           ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔌 Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# Keep script running and show logs
try {
    Write-Host "📊 Monitoring servers (Ctrl+C to stop)..." -ForegroundColor Cyan
    Write-Host ""
    
    while ($true) {
        # Check if jobs are still running
        if ($backendJob.State -eq "Completed" -or $backendJob.State -eq "Failed") {
            Write-Host "❌ Backend stopped unexpectedly!" -ForegroundColor Red
            break
        }
        
        if ($frontendJob.State -eq "Completed" -or $frontendJob.State -eq "Failed") {
            Write-Host "❌ Frontend stopped unexpectedly!" -ForegroundColor Red
            break
        }
        
        Start-Sleep -Seconds 5
    }
}
finally {
    Write-Host ""
    Write-Host "🛑 Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob
    Remove-Job -Job $backendJob, $frontendJob
    Write-Host "✅ Stopped" -ForegroundColor Green
}

