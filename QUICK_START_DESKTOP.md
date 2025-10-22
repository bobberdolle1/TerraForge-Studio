# 🚀 Quick Start - Desktop Build

## Быстрый старт для сборки десктопного приложения

### Шаг 1: Установка зависимостей

```powershell
# Способ 1: Автоматическая установка
.\desktop\install_deps.ps1

# Способ 2: Вручную
pip install pyinstaller pillow
pip install bottle proxy-tools typing-extensions
pip install pywebview --no-deps
```

### Шаг 2: Сборка приложения

```powershell
# Полная автоматическая сборка
.\desktop\build.ps1

# Или запустить Python скрипт
python desktop/build.py
```

### Шаг 3: Запуск готового приложения

```powershell
cd "desktop\dist\TerraForge Studio"
.\TerraForge Studio.exe
```

---

## Что делает сборка?

1. ✅ Собирает React frontend (`npm run build`)
2. ✅ Генерирует иконки приложения
3. ✅ Упаковывает всё в .exe с PyInstaller
4. ✅ Создаёт README и конфигурационные файлы

## Результат

```
desktop/dist/TerraForge Studio/
├── TerraForge Studio.exe     ← Запускаемый файл
├── README.txt
├── LICENSE.txt
├── .env.example
└── _internal/                ← Зависимости (не трогать)
```

**Размер:** ~200-300 MB (портативное приложение, без установки)

---

## Создание релиза

### ZIP архив

```powershell
Compress-Archive -Path "desktop\dist\TerraForge Studio" -DestinationPath "TerraForge-Studio-v1.0.0-Windows-x64.zip"
```

### GitHub Release

```bash
# 1. Создать тег версии
git tag v1.0.0
git push origin v1.0.0

# 2. GitHub Actions автоматически:
#    - Соберёт приложение
#    - Создаст релиз
#    - Загрузит .zip
```

---

## Troubleshooting

### ❌ "pythonnet не устанавливается"

**Решение:** pythonnet не совместим с Python 3.14. Используйте установку без зависимостей:
```powershell
pip install pywebview --no-deps
```

### ❌ "Frontend build failed"

**Решение:** Переустановите npm зависимости:
```powershell
cd frontend-new
rm -rf node_modules package-lock.json
npm install
npm run build
```

### ❌ "Executable не запускается"

**Решение:** Запустите из командной строки чтобы увидеть ошибку:
```powershell
"desktop\dist\TerraForge Studio\TerraForge Studio.exe"
```

---

## Системные требования

- **Windows 10/11** (64-bit)
- **Python 3.13+** (3.14 поддерживается)
- **Node.js 20+**
- **Edge WebView2** (встроен в Windows 10/11)

---

## Дополнительно

- 📖 [Полная документация](DESKTOP_BUILD_GUIDE.md)
- 🔧 [Desktop README](desktop/README.md)
- 🐛 [Issues](https://github.com/yourusername/TerraForge-Studio/issues)

**Готово! Теперь у вас есть профессиональное десктопное приложение! 🎉**
