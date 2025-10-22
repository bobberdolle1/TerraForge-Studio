@echo off
REM Install desktop dependencies for Windows
REM This script handles the pywebview installation without pythonnet

echo Installing TerraForge Studio Desktop Dependencies...
echo.

REM Install PyInstaller and Pillow normally
echo Installing PyInstaller and Pillow...
pip install pyinstaller pillow
if errorlevel 1 (
    echo Failed to install PyInstaller/Pillow
    pause
    exit /b 1
)

REM Install pywebview dependencies first
echo.
echo Installing pywebview dependencies...
pip install bottle proxy-tools typing-extensions
if errorlevel 1 (
    echo Failed to install pywebview dependencies
    pause
    exit /b 1
)

REM Install pywebview without dependencies (skip pythonnet)
echo.
echo Installing pywebview (without pythonnet)...
pip install pywebview --no-deps
if errorlevel 1 (
    echo Failed to install pywebview
    pause
    exit /b 1
)

echo.
echo All dependencies installed successfully!
echo.
echo Note: On Windows 10/11, pywebview will use Edge WebView2 (built-in)
echo No additional webview engine installation is required.
pause
