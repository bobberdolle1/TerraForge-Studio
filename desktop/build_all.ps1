# TerraForge Studio - Universal Build Script (PowerShell)
# Supports: Windows Portable, Windows Installer, Release Package

param(
    [switch]$Installer,
    [switch]$Release,
    [switch]$All
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TerraForge Studio - Universal Build System" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Build portable version
Write-Host "Building Windows Portable..." -ForegroundColor Yellow
python desktop/build.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Create portable ZIP if requested
if ($Release -or $All) {
    Write-Host ""
    Write-Host "Creating portable ZIP..." -ForegroundColor Yellow
    $version = "v1.0.0"
    $zipName = "TerraForge-Studio-$version-Windows-Portable.zip"
    
    if (Test-Path $zipName) {
        Remove-Item $zipName
    }
    
    Compress-Archive -Path "desktop\dist\TerraForge Studio" -DestinationPath $zipName
    Write-Host "Created: $zipName" -ForegroundColor Green
    
    # Calculate checksum
    Write-Host "Calculating checksum..." -ForegroundColor Yellow
    Get-FileHash $zipName -Algorithm SHA256 | Select-Object Hash | Out-File "$zipName.sha256"
    Write-Host "Created: $zipName.sha256" -ForegroundColor Green
}

# Build installer if requested
if ($Installer -or $All) {
    Write-Host ""
    Write-Host "Building Windows Installer..." -ForegroundColor Yellow
    
    $isccPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if (-not (Test-Path $isccPath)) {
        Write-Host "WARNING: Inno Setup not found!" -ForegroundColor Yellow
        Write-Host "Install from: https://jrsoftware.org/isinfo.php" -ForegroundColor Yellow
    } else {
        & $isccPath "desktop\installer.iss"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Installer created successfully!" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "BUILD COMPLETED!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Outputs:" -ForegroundColor Cyan
Write-Host "  - Portable: desktop\dist\TerraForge Studio\" -ForegroundColor White

if ($Release -or $All) {
    Write-Host "  - ZIP: $zipName" -ForegroundColor White
}

if ($Installer -or $All) {
    Write-Host "  - Installer: desktop\installer_output\TerraForge-Studio-Setup-*.exe" -ForegroundColor White
}
