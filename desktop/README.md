# TerraForge Studio - Desktop Application

This directory contains the desktop application version of TerraForge Studio, packaged as a native Windows executable.

## 🚀 Quick Build

### Windows

```powershell
# Using PowerShell (recommended)
.\desktop\build.ps1

# OR using Batch
desktop\build.bat
```

### Manual Build

```bash
# 1. Install dependencies
pip install -r desktop/desktop_requirements.txt

# 2. Run build script
python desktop/build.py
```

## 📋 Requirements

- **Python 3.13+** - Backend runtime
- **Node.js 20+** - Frontend build
- **PyInstaller 6.3+** - Executable packaging
- **pywebview 4.4+** - Native window

## 🏗️ Build Process

The build script (`build.py`) performs the following steps:

1. **Check Requirements** - Verifies all tools are installed
2. **Build Frontend** - Compiles React app (`npm run build`)
3. **Generate Icons** - Creates application icons (PNG/ICO)
4. **Build Executable** - Packages everything with PyInstaller
5. **Create Release Package** - Adds README, LICENSE, .env.example

## 📦 Output Structure

```
desktop/dist/TerraForge Studio/
├── TerraForge Studio.exe    # Main executable
├── README.txt               # User documentation
├── LICENSE.txt              # MIT License
├── .env.example             # Configuration template
├── _internal/               # Python runtime and dependencies
└── frontend-new/dist/       # React frontend (embedded)
```

## 🎨 Architecture

### Components

1. **launcher.py** - Desktop application entry point
   - Starts FastAPI backend server
   - Creates pywebview native window
   - Handles application lifecycle

2. **terraforge.spec** - PyInstaller configuration
   - Collects all dependencies
   - Embeds frontend build
   - Configures executable options

3. **build.py** - Automated build script
   - Orchestrates entire build process
   - Handles errors and logging
   - Creates release package

### Data Flow

```
User clicks .exe
    ↓
launcher.py starts
    ↓
FastAPI server starts (localhost:8000)
    ↓
pywebview window opens
    ↓
Serves React frontend from /
    ↓
API calls to /api/*
```

## 🔧 Development

### Testing Desktop App Locally

```python
# Run desktop launcher without building
cd desktop
python launcher.py
```

### Debugging PyInstaller Issues

```bash
# Build with debug console
pyinstaller terraforge.spec --debug all

# Run with console output
# Edit terraforge.spec: console=True
```

## 📝 Configuration

### Environment Variables

Create `.env` file in the same directory as the executable:

```ini
# Premium data sources (optional)
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret
OPENTOPOGRAPHY_API_KEY=your_api_key
AZURE_MAPS_KEY=your_api_key

# AI features (optional)
OLLAMA_HOST=http://localhost:11434
```

### Application Paths

When running as executable:
- **Cache**: `<exe_dir>/cache/`
- **Output**: `<exe_dir>/output/`
- **Config**: `<exe_dir>/.env`

## 🐛 Troubleshooting

### Build Fails

**Error: PyInstaller not found**
```bash
pip install pyinstaller>=6.3.0
```

**Error: Frontend build failed**
```bash
cd frontend-new
npm install
npm run build
```

### Runtime Issues

**Error: Port 8000 already in use**
- The launcher will automatically find a free port
- Check Task Manager for existing processes

**Error: Missing dependencies**
- Ensure all files in `dist/TerraForge Studio/` are present
- Don't move files out of the `_internal/` folder

## 📊 Size Optimization

Current build size: ~200-300MB (includes Python runtime + dependencies)

To reduce size:
1. Remove unused dependencies from `requirements.txt`
2. Use `--exclude-module` in PyInstaller
3. Enable UPX compression (already enabled)

## 🔒 Code Signing (Optional)

For production releases, sign the executable:

```bash
# Windows (requires certificate)
signtool sign /f certificate.pfx /p password "TerraForge Studio.exe"
```

## 🚢 Distribution

### Create Installer (Inno Setup)

```bash
# Use Inno Setup to create installer
iscc desktop/installer.iss
```

### Create Portable ZIP

```bash
# Compress the entire dist folder
Compress-Archive -Path "desktop/dist/TerraForge Studio" -DestinationPath "TerraForge-Studio-v1.0.0-Windows-x64.zip"
```

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📞 Support

- Issues: https://github.com/yourusername/TerraForge-Studio/issues
- Discussions: https://github.com/yourusername/TerraForge-Studio/discussions
