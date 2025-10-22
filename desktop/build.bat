@echo off
REM TerraForge Studio - Build Script for Windows (Batch)

echo ============================================================
echo TerraForge Studio - Desktop Build Script
echo ============================================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo Python OK

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)
echo Node.js OK

REM Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -r desktop\desktop_requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)

REM Run build script
echo.
echo Starting build process...
python desktop\build.py

if errorlevel 0 (
    echo.
    echo ============================================================
    echo BUILD COMPLETED SUCCESSFULLY!
    echo ============================================================
    echo.
    echo Executable location: desktop\dist\TerraForge Studio\
    pause
) else (
    echo.
    echo ============================================================
    echo BUILD FAILED!
    echo ============================================================
    pause
    exit /b 1
)
