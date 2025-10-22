# PyInstaller hook for uvicorn
# Ensures all uvicorn submodules are included

from PyInstaller.utils.hooks import collect_all, collect_submodules

datas, binaries, hiddenimports = collect_all('uvicorn')

# Add all uvicorn submodules explicitly
hiddenimports += collect_submodules('uvicorn')
hiddenimports += collect_submodules('uvicorn.protocols')
hiddenimports += collect_submodules('uvicorn.protocols.http')
hiddenimports += collect_submodules('uvicorn.protocols.websockets')
hiddenimports += collect_submodules('uvicorn.loops')
hiddenimports += collect_submodules('uvicorn.lifespan')

# Critical imports
hiddenimports += [
    'uvicorn',
    'uvicorn.main',
    'uvicorn.config',
    'uvicorn.server',
    'uvicorn.importer',
    'uvicorn.supervisors',
    'uvicorn.supervisors.statreload',
    'uvicorn.supervisors.watchfilesreload',
    'uvicorn.logging',
    'uvicorn._handlers',
]
