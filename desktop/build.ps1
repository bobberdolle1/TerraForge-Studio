# TerraForge Studio - Build Script for Windows
# This script builds the desktop application

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TerraForge Studio - Desktop Build Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found!" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Node.js $nodeVersion" -ForegroundColor Green

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "  - Installing PyInstaller and Pillow..." -ForegroundColor Gray
pip install pyinstaller pillow -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install PyInstaller/Pillow!" -ForegroundColor Red
    exit 1
}

Write-Host "  - Installing pywebview dependencies..." -ForegroundColor Gray
pip install bottle proxy-tools typing-extensions -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install pywebview dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "  - Installing pywebview (without pythonnet for Python 3.14)..." -ForegroundColor Gray
pip install pywebview --no-deps -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install pywebview!" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Dependencies installed" -ForegroundColor Green

# Run build script
Write-Host ""
Write-Host "Starting build process..." -ForegroundColor Yellow
python desktop/build.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "BUILD COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable location: desktop/dist/TerraForge Studio/" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    exit 1
}
