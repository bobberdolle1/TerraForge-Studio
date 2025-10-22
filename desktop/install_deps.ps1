# Install desktop dependencies for Windows
# This script handles the pywebview installation without pythonnet

Write-Host "Installing TerraForge Studio Desktop Dependencies..." -ForegroundColor Cyan
Write-Host ""

# Install PyInstaller and Pillow normally
Write-Host "Installing PyInstaller and Pillow..." -ForegroundColor Yellow
pip install pyinstaller pillow
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install PyInstaller/Pillow" -ForegroundColor Red
    exit 1
}

# Install pywebview dependencies first
Write-Host ""
Write-Host "Installing pywebview dependencies..." -ForegroundColor Yellow
pip install bottle proxy-tools typing-extensions
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install pywebview dependencies" -ForegroundColor Red
    exit 1
}

# Install pywebview without dependencies (skip pythonnet)
Write-Host ""
Write-Host "Installing pywebview (without pythonnet)..." -ForegroundColor Yellow
pip install pywebview --no-deps
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install pywebview" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All dependencies installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Note: On Windows 10/11, pywebview will use Edge WebView2 (built-in)" -ForegroundColor Cyan
Write-Host "No additional webview engine installation is required." -ForegroundColor Cyan
