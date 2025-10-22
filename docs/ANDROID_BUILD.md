# 📱 TerraForge Studio - Android Build Guide

## Overview

Android version is a **simplified mobile companion app** with limited functionality compared to desktop/web versions.

**Features:**
- ✅ Location search
- ✅ Basic terrain generation
- ✅ Resolution selection
- ❌ No 3D preview (limited by mobile)
- ❌ No advanced editing
- ❌ No real-time processing (performance)

**Recommendation:** Use desktop or web version for full experience. Android app is for quick on-the-go terrain generation.

---

## 🔧 Prerequisites

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Install Buildozer
pip3 install --user buildozer cython

# Add to PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 openjdk@17 autoconf automake libtool pkg-config

# Install Buildozer
pip3 install --user buildozer cython
```

### Windows (WSL2)

```powershell
# Install WSL2
wsl --install

# Restart computer, then open Ubuntu terminal and follow Linux instructions above
```

---

## 🚀 Building APK

### Option 1: Automated Script

```bash
# Make script executable
chmod +x desktop/build_android.sh

# Run build
./desktop/build_android.sh
```

### Option 2: Manual Build

```bash
# Clean previous builds
rm -rf .buildozer bin

# Build debug APK
buildozer android debug

# Build release APK (for distribution)
buildozer android release
```

**Build time:**
- First build: 20-40 minutes (downloads Android SDK/NDK)
- Subsequent builds: 5-15 minutes

---

## 📦 Output

**Debug APK:**
```
bin/terraforgestudio-1.0.2-arm64-v8a-debug.apk   (~15-25 MB)
bin/terraforgestudio-1.0.2-armeabi-v7a-debug.apk  (~15-25 MB)
```

**Release APK (signed):**
```
bin/terraforgestudio-1.0.2-arm64-v8a-release.apk
```

---

## 📱 Installation

### Via ADB (USB)

```bash
# Enable USB debugging on Android device

# Install APK
adb install bin/terraforgestudio-*-arm64-v8a-debug.apk

# Or for 32-bit devices
adb install bin/terraforgestudio-*-armeabi-v7a-debug.apk
```

### Via File Transfer

1. Copy APK to device
2. Open file manager on device
3. Tap APK file
4. Allow "Install from unknown sources" if prompted
5. Install

---

## 🔑 Signing APK (for Release)

### Generate Keystore

```bash
# Generate new keystore
keytool -genkey -v -keystore terraforge.keystore \
    -alias terraforge -keyalg RSA -keysize 2048 \
    -validity 10000

# Enter password and details
```

### Sign APK

```bash
# Build unsigned APK
buildozer android release

# Sign with jarsigner
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA256 \
    -keystore terraforge.keystore \
    bin/terraforgestudio-*-release-unsigned.apk terraforge

# Align APK
zipalign -v 4 \
    bin/terraforgestudio-*-release-unsigned.apk \
    bin/terraforgestudio-1.0.2-release.apk
```

---

## 🐛 Troubleshooting

### Build fails with "SDK not found"

Buildozer will download SDK automatically. If it fails:

```bash
# Set Android SDK path manually
export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
export ANDROID_NDK_HOME=$HOME/.buildozer/android/platform/android-ndk-r25b
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

### Build fails with "Java not found"

```bash
# Ubuntu/Debian
sudo apt install openjdk-17-jdk

# macOS
brew install openjdk@17

# Verify
java -version
```

### APK won't install on device

```bash
# Check minimum Android version (API 21 = Android 5.0)
# Ensure device is Android 5.0+

# Check architecture
adb shell getprop ro.product.cpu.abi

# Use matching APK (arm64-v8a or armeabi-v7a)
```

### App crashes on startup

```bash
# View logs
adb logcat | grep python

# Common issues:
# - Missing permissions in AndroidManifest.xml
# - Missing Python dependencies
# - Incompatible library versions
```

---

## 📋 buildozer.spec Configuration

Key settings in `buildozer.spec`:

```ini
# App info
title = TerraForge Studio
package.name = terraforgestudio
package.domain = com.terraforge

# Version
version = 1.0.2

# Requirements (keep minimal for smaller APK)
requirements = python3,kivy,android,requests

# Android API levels
android.api = 33        # Target (latest)
android.minapi = 21     # Minimum (Android 5.0)

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE
```

---

## 🎨 Customization

### Change App Icon

Replace `desktop/icon.png` with your icon (512x512 PNG)

### Change Splash Screen

```ini
# In buildozer.spec
presplash.filename = path/to/splash.png
android.presplash_color = #667EEA
```

### Add Permissions

```ini
# In buildozer.spec
android.permissions = INTERNET,CAMERA,ACCESS_FINE_LOCATION
```

---

## 📊 APK Size Optimization

```bash
# Use ProGuard (minification)
android.add_compile_options = "android.enableR8.fullMode=true"

# Remove debug symbols
android.add_compile_options = "android.enableResourceOptimizations=true"

# Use APK splits (multiple APKs per architecture)
android.archs = arm64-v8a  # Build separately for each arch
```

**Result:** ~15MB → ~8MB per architecture

---

## 🚀 Publishing to Google Play

### 1. Prepare Release

```bash
# Build release APK
buildozer android release

# Sign APK (see "Signing APK" section above)
```

### 2. Create Play Console Account

1. Go to https://play.google.com/console
2. Pay $25 one-time fee
3. Create developer account

### 3. Create App Listing

- App name: TerraForge Studio
- Description: Professional 3D terrain generator
- Screenshots: 2 phone, 1 tablet (required)
- Feature graphic: 1024x500 PNG

### 4. Upload APK

1. Create release
2. Upload signed APK
3. Fill out content rating questionnaire
4. Submit for review

**Review time:** 1-7 days

---

## 🔄 Updates

### Update Version

```ini
# In buildozer.spec
version = 1.0.3

# In main.py
__version__ = '1.0.3'
```

### Rebuild

```bash
# Clean build
buildozer android clean

# Build new version
buildozer android release
```

---

## 📈 Analytics (Optional)

### Add Firebase

```ini
# In buildozer.spec
requirements = python3,kivy,firebase
```

```python
# In main.py
from jnius import autoclass

# Initialize Firebase
FirebaseApp = autoclass('com.google.firebase.FirebaseApp')
FirebaseApp.initializeApp(self.activity)
```

---

## 💡 Tips

1. **Test on real device** - Emulator may not show real performance
2. **Keep APK small** - Remove unused dependencies
3. **Test on multiple devices** - Different screen sizes and Android versions
4. **Use release builds** - Debug builds are larger and slower
5. **Monitor crashes** - Use Firebase Crashlytics

---

## 📞 Support

- 📖 Buildozer docs: https://buildozer.readthedocs.io/
- 📖 Kivy docs: https://kivy.org/doc/stable/
- 🐛 Report issues: https://github.com/bobberdolle1/TerraForge-Studio/issues

---

**Android version is experimental. Use desktop/web for full experience!** 📱→🖥️
