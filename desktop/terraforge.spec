# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for TerraForge Studio Desktop
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Get base path
block_cipher = None
base_path = Path('.').absolute()

# Collect all data files and submodules
datas = []
binaries = []
hiddenimports = []

# Add frontend build
frontend_dist = base_path / 'frontend-new' / 'dist'
if frontend_dist.exists():
    datas.append((str(frontend_dist), 'frontend-new/dist'))

# Add icon and resources
desktop_path = base_path / 'desktop'
if (desktop_path / 'icon.ico').exists():
    datas.append((str(desktop_path / 'icon.ico'), 'desktop'))
if (desktop_path / 'icon.png').exists():
    datas.append((str(desktop_path / 'icon.png'), 'desktop'))

# Collect FastAPI and dependencies
tmp_ret = collect_all('fastapi')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

tmp_ret = collect_all('uvicorn')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Collect geospatial libraries
for lib in ['rasterio', 'geopandas', 'shapely', 'pyproj', 'fiona']:
    try:
        tmp_ret = collect_all(lib)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except:
        pass

# Collect pywebview
tmp_ret = collect_all('webview')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Critical: Add all required imports explicitly
hiddenimports += [
    # Core web framework
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.config',
    'uvicorn.server',
    'uvicorn.main',
    
    # FastAPI and dependencies
    'fastapi',
    'fastapi.routing',
    'fastapi.responses',
    'pydantic',
    'pydantic.types',
    'pydantic.fields',
    'starlette',
    'starlette.applications',
    'starlette.routing',
    'starlette.middleware',
    'starlette.responses',
    'starlette.staticfiles',
    
    # HTTP libraries
    'click',
    'h11',
    'httptools',
    'websockets',
    'watchfiles',
    'python-multipart',
    'anyio',
    'sniffio',
    
    # Pywebview
    'webview',
    'bottle',
    'proxy_tools',
    
    # Application modules
    'realworldmapgen',
    'realworldmapgen.api',
    'realworldmapgen.api.main',
    'realworldmapgen.config',
    'realworldmapgen.core',
    'realworldmapgen.elevation',
]

a = Analysis(
    ['launcher.py'],
    pathex=[str(base_path)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pytest',
        'notebook',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TerraForge Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(desktop_path / 'icon.ico') if (desktop_path / 'icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TerraForge Studio',
)
