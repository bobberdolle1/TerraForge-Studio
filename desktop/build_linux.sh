#!/bin/bash
# TerraForge Studio - Linux Build Script

set -e

echo "============================================================"
echo "TerraForge Studio - Linux AppImage Build"
echo "============================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip3 install -r requirements.txt
pip3 install -r desktop/desktop_requirements.txt

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
cd frontend-new
npm install
npm run build
cd ..

# Build with PyInstaller
echo -e "${YELLOW}Building with PyInstaller...${NC}"
pyinstaller desktop/terraforge.spec --clean --noconfirm

# Create AppImage (requires appimagetool)
echo -e "${YELLOW}Creating AppImage...${NC}"

APP_DIR="desktop/dist/TerraForge-Studio.AppDir"
mkdir -p "$APP_DIR"

# Copy executable and resources
cp -r "desktop/dist/TerraForge Studio/"* "$APP_DIR/"
mv "$APP_DIR/TerraForge Studio" "$APP_DIR/AppRun"

# Create .desktop file
cat > "$APP_DIR/terraforge-studio.desktop" << EOF
[Desktop Entry]
Type=Application
Name=TerraForge Studio
Comment=3D Terrain Generator from Real-World Data
Exec=AppRun
Icon=terraforge-studio
Categories=Graphics;3DGraphics;
Terminal=false
EOF

# Copy icon
cp desktop/icon.png "$APP_DIR/terraforge-studio.png"

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    wget "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppImage
./appimagetool-x86_64.AppImage "$APP_DIR" "TerraForge-Studio-v1.0.0-Linux-x86_64.AppImage"

echo -e "${GREEN}✓ Linux build completed${NC}"
echo "AppImage: TerraForge-Studio-v1.0.0-Linux-x86_64.AppImage"
