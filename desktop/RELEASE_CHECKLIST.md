# 📋 Release Checklist for TerraForge Studio Desktop

Используйте этот чеклист перед созданием релиза.

## ✅ Pre-Release Checklist

### 1. Code Quality

- [ ] Все тесты проходят
- [ ] Нет критических ошибок в логах
- [ ] Code review выполнен
- [ ] Changelog обновлён

### 2. Dependencies

```powershell
# Проверить версии
python --version  # 3.13+
node --version    # 20+

# Проверить установку
pip list | findstr "pyinstaller pywebview pillow"
```

- [ ] Все Python зависимости установлены
- [ ] Все Node.js зависимости установлены
- [ ] pywebview установлен без pythonnet

### 3. Frontend Build

```powershell
cd frontend-new
npm run build
```

- [ ] Frontend собирается без ошибок
- [ ] Размер bundle приемлемый (<10MB)
- [ ] Нет критических предупреждений

### 4. Backend

```powershell
python -m uvicorn realworldmapgen.api.main:app --host 0.0.0.0 --port 8000
```

- [ ] API запускается
- [ ] /api/health возвращает OK
- [ ] /api/sources показывает доступные источники
- [ ] Базовая генерация работает

### 5. Desktop Launcher

```powershell
python desktop/launcher.py
```

- [ ] Launcher запускается
- [ ] Окно открывается
- [ ] Frontend загружается
- [ ] API доступен

## 🔨 Build Process

### 1. Clean Build

```powershell
# Очистить старые сборки
rm -rf desktop/dist, desktop/build
rm -rf frontend-new/dist
```

### 2. Build Frontend

```powershell
cd frontend-new
npm install
npm run build
cd ..
```

- [ ] Сборка успешна
- [ ] dist/ создан
- [ ] index.html присутствует

### 3. Build Desktop

```powershell
.\desktop\build.ps1
```

- [ ] Зависимости установлены
- [ ] Иконки созданы
- [ ] PyInstaller выполнен
- [ ] Executable создан

### 4. Test Executable

```powershell
cd "desktop\dist\TerraForge Studio"
.\TerraForge Studio.exe
```

**Тесты:**
- [ ] Приложение запускается
- [ ] UI загружается
- [ ] API работает
- [ ] Можно создать тестовый проект
- [ ] Генерация terrain работает
- [ ] Экспорт файлов работает
- [ ] Закрытие приложения корректно

## 📦 Create Release Package

### 1. Create ZIP

```powershell
Compress-Archive -Path "desktop\dist\TerraForge Studio" -DestinationPath "TerraForge-Studio-v1.0.0-Windows-x64.zip"
```

### 2. Calculate Checksum

```powershell
Get-FileHash TerraForge-Studio-v1.0.0-Windows-x64.zip -Algorithm SHA256 | Select-Object Hash | Out-File "TerraForge-Studio-v1.0.0-Windows-x64.zip.sha256"
```

### 3. Verify Package

- [ ] ZIP размер ~200-300MB
- [ ] SHA256 checksum создан
- [ ] Все файлы в архиве

## 📝 Documentation

- [ ] README_DESKTOP.md обновлён
- [ ] CHANGELOG.md обновлён
- [ ] Version numbers обновлены:
  - [ ] package.json (frontend)
  - [ ] pyproject.toml (backend)
  - [ ] launcher.py
  - [ ] README.md

## 🚀 GitHub Release

### 1. Create Tag

```bash
git tag -a v1.0.0 -m "Release v1.0.0 - Desktop Application"
git push origin v1.0.0
```

### 2. Create Release on GitHub

- [ ] Go to Releases → New Release
- [ ] Choose tag: v1.0.0
- [ ] Release title: "TerraForge Studio v1.0.0 - Desktop"
- [ ] Description from CHANGELOG
- [ ] Upload files:
  - [ ] TerraForge-Studio-v1.0.0-Windows-x64.zip
  - [ ] TerraForge-Studio-v1.0.0-Windows-x64.zip.sha256

### 3. Release Notes Template

```markdown
# TerraForge Studio v1.0.0 - Desktop Application

## 🎉 First Desktop Release!

Professional 3D terrain generator now available as a native Windows application.

## ✨ What's New

- 🖥️ Native Windows desktop application
- 🌍 Built-in 3D preview with Cesium
- 🎮 Export to Unreal Engine 5, Unity, GLTF, GeoTIFF
- 🚀 Portable - no installation required
- 💾 Smart caching for faster regeneration

## 📥 Installation

1. Download `TerraForge-Studio-v1.0.0-Windows-x64.zip`
2. Extract to any folder
3. Run `TerraForge Studio.exe`

## 🔒 Verification

Verify download integrity:
```powershell
certutil -hashfile TerraForge-Studio-v1.0.0-Windows-x64.zip SHA256
```

## 📋 System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 500MB disk space
- Internet for map data

## 📖 Documentation

- [Desktop Build Guide](DESKTOP_BUILD_GUIDE.md)
- [Quick Start](QUICK_START_DESKTOP.md)
- [API Docs](docs/API_SPECIFICATION.md)

## 🐛 Known Issues

- pythonnet not compatible with Python 3.14 (resolved by using Edge WebView2)

## 🙏 Credits

Made with ❤️ by the TerraForge Team
```

## ✅ Post-Release

- [ ] Verify release on GitHub
- [ ] Test download link
- [ ] Announce on social media
- [ ] Update website (if applicable)
- [ ] Close milestone on GitHub

## 🐛 Rollback Plan

If critical issues found:

```bash
# Delete release
gh release delete v1.0.0

# Delete tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

---

## 📊 Metrics to Track

After release, monitor:

- Download count
- Issue reports
- User feedback
- Performance metrics
- Crash reports

---

**Version:** 1.0.0  
**Date:** 2025-10-22  
**Author:** TerraForge Team
