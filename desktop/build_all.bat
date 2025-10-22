@echo off
REM TerraForge Studio - Universal Build Script (Batch)

echo ============================================================
echo TerraForge Studio - Universal Build System
echo ============================================================
echo.

REM Parse arguments
set INSTALLER=0
set RELEASE=0

:parse_args
if "%1"=="" goto end_parse
if /i "%1"=="--installer" set INSTALLER=1
if /i "%1"=="--release" set RELEASE=1
shift
goto parse_args
:end_parse

REM Build portable
echo Building Windows Portable...
python desktop\build.py
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

REM Create ZIP if requested
if %RELEASE%==1 (
    echo.
    echo Creating portable ZIP...
    powershell -Command "Compress-Archive -Path 'desktop\dist\TerraForge Studio' -DestinationPath 'TerraForge-Studio-v1.0.0-Windows-Portable.zip' -Force"
    echo Created ZIP
)

REM Build installer if requested
if %INSTALLER%==1 (
    echo.
    echo Building Windows Installer...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" desktop\installer.iss
)

echo.
echo ============================================================
echo BUILD COMPLETED!
echo ============================================================
pause
