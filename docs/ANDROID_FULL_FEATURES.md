# 📱 TerraForge Studio Android - Full Features Guide

## 🎉 Overview

Android версия теперь имеет **ВСЕ функции** desktop версии:

- ✅ **3D Preview** - Полноценный 3D рендеринг с Cesium
- ✅ **Продвинутое редактирование** - Все инструменты редактирования
- ✅ **Реальный процессинг** - FastAPI backend работает локально на устройстве
- ✅ **React Frontend** - Тот же UI что и на desktop/web
- ✅ **Offline Mode** - Работает без интернета (с кэшем)

---

## 🏗️ Архитектура

### Компоненты:

```
Android App
├── Kivy (Native wrapper)
│   └── WebView (Android component)
│       └── React Frontend (http://127.0.0.1:8000)
│
└── FastAPI Backend (Local server)
    ├── Terrain Processing
    ├── Data Sources (OSM, SRTM)
    └── Export Engines
```

### Как работает:

1. **Kivy App** запускается на Android
2. **FastAPI server** стартует на localhost (порт 8000)
3. **WebView** загружает React UI с локального сервера
4. **Frontend** делает API запросы к localhost backend
5. **Backend** обрабатывает данные и генерирует terrain
6. **Результат** отображается в WebView с 3D preview

---

## ⚡ Производительность

### Оптимизации:

- **Локальный сервер** - нет задержек сети
- **Кэширование** - данные сохраняются на устройстве
- **Ленивая загрузка** - модули загружаются по требованию
- **WebGL** - аппаратное ускорение 3D

### Рекомендуемые устройства:

**Минимум:**
- Android 8.0+ (API 26)
- 4GB RAM
- 4 ядра CPU
- 2GB свободного места

**Рекомендуется:**
- Android 11+ (API 30)
- 6GB+ RAM
- 8 ядер CPU (Snapdragon 7xx+)
- 4GB свободного места
- GPU с OpenGL ES 3.0+

---

## 🚀 Сборка

### 1. Установить зависимости (Linux/macOS):

```bash
# Системные пакеты
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk \
    build-essential libssl-dev libffi-dev python3-dev \
    libgdal-dev libproj-dev

# Python пакеты
pip3 install --user buildozer cython
```

### 2. Собрать APK:

```bash
# Использовать main_webview.py как точку входа
cp main_webview.py main.py

# Собрать
buildozer android debug

# Для release
buildozer android release
```

**Время сборки:** 30-60 минут (первый раз)

### 3. Установить на устройство:

```bash
# Через ADB
adb install -r bin/terraforgestudio-*-arm64-v8a-debug.apk

# Или скопировать файл и установить вручную
```

---

## 📦 Размер APK

С полным функционалом:

```
APK Size (compressed):     ~45-60 MB
APK Size (installed):      ~120-150 MB
With cache (after use):    ~200-300 MB
```

**Компоненты:**
- React Frontend: ~6 MB
- Python Runtime: ~15 MB
- FastAPI/Uvicorn: ~5 MB
- NumPy/SciPy: ~20 MB
- Geospatial libs: ~15 MB
- Kivy: ~10 MB

---

## 🎨 UI Features

### Все функции desktop версии:

1. **Map Interface**
   - Поиск локаций
   - Рисование области
   - Точные координаты

2. **3D Preview**
   - Cesium 3D Globe
   - Вращение, масштаб, панорама
   - Режимы отображения
   - Satellite overlay

3. **Advanced Tools**
   - Terrain editing
   - Layer management
   - Export options
   - Project management

4. **Settings**
   - Resolution settings
   - Data sources
   - Quality controls
   - Cache management

---

## 🔧 Конфигурация

### Файл конфигурации на устройстве:

```
/sdcard/Android/data/com.terraforge.terraforgestudio/files/.env
```

```ini
# Data Sources
SRTM_CACHE_DIR=/sdcard/TerraForge/cache/srtm
OSM_CACHE_DIR=/sdcard/TerraForge/cache/osm

# Processing
MAX_RESOLUTION=2048
MAX_AREA_KM2=25
ENABLE_CACHE=true

# Performance
WORKERS=2
MEMORY_LIMIT_MB=1024
```

---

## 📱 Особенности Android

### WebView настройки:

```java
// Включено в коде
webView.getSettings().setJavaScriptEnabled(true);
webView.getSettings().setDomStorageEnabled(true);
webView.getSettings().setAllowFileAccess(true);
webView.setWebContentsDebuggingEnabled(true); // Для отладки
```

### Permissions:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.CAMERA" />
```

---

## 🐛 Отладка

### Chrome DevTools:

1. Подключить устройство по USB
2. Открыть Chrome на desktop
3. Перейти на `chrome://inspect`
4. Выбрать TerraForge WebView
5. Inspect - полный DevTools!

### Логи:

```bash
# Все логи
adb logcat

# Только Python
adb logcat | grep python

# Только TerraForge
adb logcat | grep TerraForge
```

### Проверка сервера:

```bash
# Port forwarding
adb forward tcp:8000 tcp:8000

# Открыть в браузере на desktop
http://localhost:8000
```

---

## 🎯 Оптимизация

### Уменьшить размер APK:

```ini
# В buildozer.spec
android.add_compile_options = android.enableR8=true
android.gradle_dependencies = com.android.tools.build:gradle:7.4.0

# Удалить ненужные архитектуры
android.archs = arm64-v8a  # Только 64-bit
```

### Улучшить производительность:

```python
# В main_webview.py
# Ограничить воркеры
os.environ['WORKERS'] = '2'

# Ограничить память
os.environ['MAX_MEMORY_MB'] = '512'

# Отключить ненужные фичи
os.environ['ENABLE_AI'] = 'false'
os.environ['ENABLE_ANALYTICS'] = 'false'
```

---

## 📊 Тестирование

### Unit Tests:

```bash
# На desktop (быстрее)
python -m pytest tests/

# На устройстве
adb shell "cd /sdcard/TerraForge && python -m pytest"
```

### Performance Tests:

```python
# Тест генерации
import time
start = time.time()
generate_terrain(location="London", resolution=1024)
print(f"Time: {time.time() - start:.2f}s")
```

---

## 🚢 Релиз

### Подпись APK:

```bash
# Создать keystore
keytool -genkey -v -keystore terraforge.keystore \
    -alias terraforge -keyalg RSA -keysize 2048 \
    -validity 10000

# Собрать release
buildozer android release

# Подписать
jarsigner -verbose -sigalg SHA256withRSA \
    -digestalg SHA256 -keystore terraforge.keystore \
    bin/terraforgestudio-*-release-unsigned.apk terraforge

# Выровнять
zipalign -v 4 \
    bin/terraforgestudio-*-release-unsigned.apk \
    bin/terraforgestudio-1.0.2-release.apk
```

### Google Play:

1. Создать listing в Play Console
2. Загрузить signed APK
3. Заполнить метаданные
4. Отправить на ревью

---

## 💡 Best Practices

1. **Оптимизация батареи**
   - Останавливать backend при паузе
   - Очищать кэш старых данных
   - Использовать WiFi для больших загрузок

2. **Управление памятью**
   - Ограничить размер кэша
   - Очищать неиспользуемые данные
   - Мониторить использование RAM

3. **UX на мобильных**
   - Touch-friendly кнопки (min 48dp)
   - Responsive layout
   - Оптимизация для маленьких экранов
   - Landscape/Portrait support

---

## 🎓 Примеры использования

### Генерация terrain:

1. Открыть приложение
2. Ввести "Mount Everest" в поиске
3. Выбрать область на карте
4. Установить resolution 1024x1024
5. Нажать "Generate"
6. Дождаться обработки (1-3 минуты)
7. Просмотреть в 3D preview
8. Экспорт в UE5/Unity

### Offline использование:

1. Загрузить данные с WiFi
2. Включить airplane mode
3. Использовать кэшированные данные
4. Генерировать terrain offline

---

## 📞 Support

- 📖 Документация: [GitHub Wiki](https://github.com/bobberdolle1/TerraForge-Studio/wiki)
- 🐛 Issues: [GitHub Issues](https://github.com/bobberdolle1/TerraForge-Studio/issues)
- 💬 Discord: Coming soon

---

**Android версия теперь полнофункциональная!** 🚀📱
