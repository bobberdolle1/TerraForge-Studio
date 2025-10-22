#!/bin/bash
# TerraForge Studio - macOS Build Script

set -e

echo "============================================================"
echo "TerraForge Studio - macOS Build"
echo "============================================================"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script must be run on macOS"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install -r desktop/desktop_requirements.txt
pip3 install py2app

# Build frontend
echo "Building frontend..."
cd frontend-new
npm install
npm run build
cd ..

# Build with PyInstaller (works better than py2app for this)
echo "Building with PyInstaller..."
pyinstaller desktop/terraforge.spec --clean --noconfirm

# Move to .app structure
APP_NAME="TerraForge Studio.app"
APP_DIR="desktop/dist/$APP_NAME"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy executable
cp -r "desktop/dist/TerraForge Studio/"* "$MACOS_DIR/"
mv "$MACOS_DIR/TerraForge Studio" "$MACOS_DIR/TerraForge-Studio"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>TerraForge Studio</string>
    <key>CFBundleDisplayName</key>
    <string>TerraForge Studio</string>
    <key>CFBundleIdentifier</key>
    <string>com.terraforge.studio</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>TerraForge-Studio</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Convert icon to icns (requires iconutil)
if [ -f "desktop/icon.png" ]; then
    mkdir -p icon.iconset
    sips -z 16 16     desktop/icon.png --out icon.iconset/icon_16x16.png
    sips -z 32 32     desktop/icon.png --out icon.iconset/icon_16x16@2x.png
    sips -z 32 32     desktop/icon.png --out icon.iconset/icon_32x32.png
    sips -z 64 64     desktop/icon.png --out icon.iconset/icon_32x32@2x.png
    sips -z 128 128   desktop/icon.png --out icon.iconset/icon_128x128.png
    sips -z 256 256   desktop/icon.png --out icon.iconset/icon_128x128@2x.png
    sips -z 256 256   desktop/icon.png --out icon.iconset/icon_256x256.png
    sips -z 512 512   desktop/icon.png --out icon.iconset/icon_256x256@2x.png
    sips -z 512 512   desktop/icon.png --out icon.iconset/icon_512x512.png
    sips -z 1024 1024 desktop/icon.png --out icon.iconset/icon_512x512@2x.png
    iconutil -c icns icon.iconset
    cp icon.icns "$RESOURCES_DIR/"
    rm -rf icon.iconset icon.icns
fi

# Create DMG
echo "Creating DMG..."
hdiutil create -volname "TerraForge Studio" -srcfolder "$APP_DIR" -ov -format UDZO "TerraForge-Studio-v1.0.0-macOS.dmg"

echo "✓ macOS build completed"
echo "App: $APP_DIR"
echo "DMG: TerraForge-Studio-v1.0.0-macOS.dmg"
