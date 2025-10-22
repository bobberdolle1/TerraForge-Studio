# Test TerraForge Studio Desktop Application
# Automated testing script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TerraForge Studio - Application Test" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$exePath = "desktop\dist\TerraForge Studio\TerraForge Studio.exe"

# Check if exe exists
if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: Application not found at $exePath" -ForegroundColor Red
    exit 1
}

Write-Host "Testing application..." -ForegroundColor Yellow
Write-Host ""

# Get file info
$exe = Get-Item $exePath
Write-Host "File: $($exe.Name)" -ForegroundColor Green
Write-Host "Size: $([math]::Round($exe.Length / 1MB, 2)) MB" -ForegroundColor Green
Write-Host "Modified: $($exe.LastWriteTime)" -ForegroundColor Green
Write-Host ""

# Check required files
Write-Host "Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "README.txt",
    "LICENSE.txt",
    ".env.example"
)

foreach ($file in $requiredFiles) {
    $path = "desktop\dist\TerraForge Studio\$file"
    if (Test-Path $path) {
        Write-Host "  OK: $file" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $file" -ForegroundColor Red
    }
}

Write-Host ""

# Check _internal directory
$internalPath = "desktop\dist\TerraForge Studio\_internal"
if (Test-Path $internalPath) {
    $internalSize = (Get-ChildItem $internalPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "Dependencies: $([math]::Round($internalSize, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "WARNING: _internal directory not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting application..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
Write-Host ""

# Start the application
$process = Start-Process $exePath -PassThru

# Monitor for 10 seconds
Start-Sleep -Seconds 5

if ($process.HasExited) {
    Write-Host ""
    Write-Host "ERROR: Application crashed!" -ForegroundColor Red
    Write-Host "Exit code: $($process.ExitCode)" -ForegroundColor Red
    exit 1
} else {
    Write-Host ""
    Write-Host "SUCCESS: Application is running!" -ForegroundColor Green
    Write-Host "Process ID: $($process.Id)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To stop: Stop-Process -Id $($process.Id)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "TEST COMPLETED" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
