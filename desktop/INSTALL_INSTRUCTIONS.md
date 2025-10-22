# Installation Instructions for Desktop Build

## Issue: pythonnet не совместим с Python 3.14

На Windows 10/11 `pywebview` может работать с Edge WebView2 (встроенный в систему) без `pythonnet`.

## Решение: Установка зависимостей

Выполните команды по порядку:

```powershell
# 1. Установите основные зависимости
pip install pyinstaller pillow

# 2. Установите зависимости pywebview
pip install bottle proxy-tools typing-extensions

# 3. Установите pywebview БЕЗ зависимостей (пропускаем pythonnet)
pip install pywebview --no-deps
```

## Или используйте готовый скрипт:

```powershell
.\desktop\install_deps.ps1
```

## Проверка установки:

```powershell
python -c "import webview; print('pywebview:', webview.__version__)"
python -c "import PyInstaller; print('PyInstaller:', PyInstaller.__version__)"
python -c "from PIL import Image; print('Pillow: OK')"
```

## После установки:

Запустите сборку:
```powershell
python desktop/build.py
```

Или используйте скрипт:
```powershell
.\desktop\build.ps1
```
