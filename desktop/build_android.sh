#!/bin/bash
# TerraForge Studio - Android APK Build Script

set -e

echo "============================================================"
echo "TerraForge Studio - Android APK Build"
echo "============================================================"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Android builds must be run on Linux or macOS"
    echo "   Windows users: Use WSL2 (Windows Subsystem for Linux)"
    exit 1
fi

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "Installing Buildozer..."
    pip3 install --user buildozer
    pip3 install --user cython
fi

# Check if Android SDK is set up
if [ -z "$ANDROID_HOME" ]; then
    echo "⚠️  ANDROID_HOME not set. Buildozer will download Android SDK automatically."
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf .buildozer bin

# Initialize buildozer if needed
if [ ! -f "buildozer.spec" ]; then
    echo "Initializing buildozer..."
    buildozer init
fi

# Build APK
echo ""
echo "Building APK (this will take 15-30 minutes on first run)..."
echo ""

buildozer android debug

# Check if build succeeded
if [ -f "bin/*.apk" ]; then
    echo ""
    echo "============================================================"
    echo "✓ APK BUILD SUCCESSFUL!"
    echo "============================================================"
    echo ""
    echo "APK location: bin/"
    ls -lh bin/*.apk
    echo ""
    echo "To install on device:"
    echo "  adb install bin/terraforgestudio-*-arm64-v8a-debug.apk"
    echo ""
else
    echo ""
    echo "============================================================"
    echo "✗ APK BUILD FAILED"
    echo "============================================================"
    exit 1
fi
