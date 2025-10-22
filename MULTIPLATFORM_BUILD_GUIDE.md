# 🌍 TerraForge Studio - Multi-Platform Build Guide

Comprehensive guide for building TerraForge Studio on Windows, Linux, macOS, and Android.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Platform-Specific Builds](#platform-specific-builds)
- [Automated Builds](#automated-builds)
- [Release Process](#release-process)

---

## 🚀 Quick Start

### Universal Build Script

```bash
# Build for current platform (portable)
python desktop/build_all.py

# Build with installer
python desktop/build_all.py --installer

# Create release package
python desktop/build_all.py --release

# Build for specific platform
python desktop/build_all.py --platform windows --installer --release
python desktop/build_all.py --platform linux --release
python desktop/build_all.py --platform macos --release
```

---

## 🖥️ Platform-Specific Builds

### Windows

#### Portable Version

```powershell
# Method 1: Build script
python desktop/build.py

# Method 2: PowerShell wrapper
.\desktop\build.ps1

# Output: desktop/dist/TerraForge Studio/TerraForge Studio.exe
```

#### Installer Version

```powershell
# Requires Inno Setup: https://jrsoftware.org/isinfo.php
python desktop/build_all.py --platform windows --installer

# Or manually:
# 1. Build portable version first
python desktop/build.py

# 2. Compile with Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" desktop/installer.iss

# Output: desktop/installer_output/TerraForge-Studio-Setup-v1.0.0.exe
```

**Size:** ~250MB (portable), ~100MB (installer)

---

### Linux

#### AppImage (Universal Linux)

```bash
# Run build script
chmod +x desktop/build_linux.sh
./desktop/build_linux.sh

# Output: TerraForge-Studio-v1.0.0-Linux-x86_64.AppImage
```

**Run:**
```bash
chmod +x TerraForge-Studio-*.AppImage
./TerraForge-Studio-*.AppImage
```

#### Flatpak (Alternative)

```bash
# Install flatpak-builder
sudo apt install flatpak-builder

# Build flatpak
flatpak-builder --force-clean build-dir desktop/flatpak/com.terraforge.studio.yml

# Install locally
flatpak-builder --install build-dir desktop/flatpak/com.terraforge.studio.yml
```

**Size:** ~280MB (AppImage)

---

### macOS

#### DMG Installer

```bash
# Requires macOS
chmod +x desktop/build_macos.sh
./desktop/build_macos.sh

# Output: 
# - TerraForge Studio.app
# - TerraForge-Studio-v1.0.0-macOS.dmg
```

**Installation:**
1. Open DMG
2. Drag `TerraForge Studio.app` to Applications
3. First run: Right-click → Open (to bypass Gatekeeper)

**Size:** ~300MB

---

### Android (Experimental)

#### APK Build

```bash
# Install Buildozer (Linux/macOS only)
pip install buildozer

# Initialize buildozer
buildozer init

# Build APK
buildozer android debug

# Output: bin/TerraForge-Studio-*.apk
```

**Note:** Android version has limited functionality due to platform constraints.

---

## 🤖 Automated Builds

### GitHub Actions

Push a version tag to trigger multi-platform builds:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This automatically builds:
- ✅ Windows Portable (ZIP)
- ✅ Windows Installer (EXE)
- ✅ Linux AppImage
- ✅ macOS DMG
- ✅ Creates GitHub Release with all artifacts

**Workflow:** `.github/workflows/build-multiplatform.yml`

---

## 📦 Release Process

### Manual Release

1. **Build all platforms:**
```bash
# Windows
python desktop/build_all.py --platform windows --installer --release

# Linux (on Linux machine or WSL)
./desktop/build_linux.sh

# macOS (on macOS machine)
./desktop/build_macos.sh
```

2. **Create checksums:**
```bash
# Windows
Get-FileHash *.zip, *.exe -Algorithm SHA256 | Out-File checksums.txt

# Linux/macOS
sha256sum *.AppImage *.dmg *.zip > checksums.txt
```

3. **Upload to GitHub:**
- Go to Releases → New Release
- Create tag (e.g., v1.0.0)
- Upload all build artifacts
- Include checksums in release notes

### Automated Release

```bash
# Tag and push
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# GitHub Actions will:
# - Build all platforms
# - Create checksums
# - Create GitHub Release
# - Upload all artifacts
```

---

## 🛠️ Build Requirements

### All Platforms

- **Python:** 3.13+
- **Node.js:** 20+
- **npm:** 10+

### Windows

- **PyInstaller:** 6.3+
- **Inno Setup:** 6+ (for installer)

### Linux

- **System packages:**
  ```bash
  sudo apt install libgirepository1.0-dev libcairo2-dev python3-gi
  ```
- **appimagetool:** Auto-downloaded by build script

### macOS

- **Xcode Command Line Tools:**
  ```bash
  xcode-select --install
  ```
- **iconutil:** Built-in

### Android

- **Buildozer:** Linux/macOS only
- **Android SDK:** Auto-installed by Buildozer
- **Java JDK 8**

---

## 📊 Build Sizes

| Platform | Portable | Installer | Compressed |
|----------|----------|-----------|------------|
| Windows  | ~250MB   | ~100MB    | ~80MB      |
| Linux    | ~280MB   | N/A       | ~90MB      |
| macOS    | ~300MB   | ~120MB    | ~100MB     |
| Android  | ~50MB    | N/A       | ~50MB      |

---

## 🔧 Customization

### Change App Name

Edit in:
- `desktop/build_all.py` → APP_NAME
- `desktop/installer.iss` → MyAppName
- `.github/workflows/build-multiplatform.yml`

### Change Version

Edit in:
- `desktop/build_all.py` → VERSION
- `package.json` → version
- `desktop/installer.iss` → MyAppVersion

### Add Platforms

Create new build scripts:
- `desktop/build_<platform>.sh`
- Update `desktop/build_all.py`
- Update `.github/workflows/build-multiplatform.yml`

---

## 🐛 Troubleshooting

### Windows Build Fails

**Error:** "pythonnet not found"
```powershell
pip install pywebview --no-deps
```

**Error:** "npm not found"
```powershell
# Restart terminal after Node.js installation
```

### Linux Build Fails

**Error:** "No module named 'gi'"
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### macOS Build Fails

**Error:** "iconutil: command not found"
```bash
xcode-select --install
```

---

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/bobberdolle1/TerraForge-Studio/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/bobberdolle1/TerraForge-Studio/discussions)

---

**Happy Building! 🚀**
