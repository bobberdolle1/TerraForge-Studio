"""
Build script for TerraForge Studio Desktop Application
Automates the entire build process: frontend build, icon generation, PyInstaller packaging
"""

import subprocess
import sys
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class BuildError(Exception):
    """Custom exception for build errors"""
    pass


def run_command(cmd, cwd=None, shell=True):
    """Run a command and handle errors"""
    logger.info(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            logger.info(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"Error: {e.stderr}")
        raise BuildError(f"Failed to run: {cmd}")


def check_requirements():
    """Check if all required tools are installed"""
    logger.info("Checking requirements...")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        logger.info(f"✓ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        raise BuildError("Node.js not found. Please install Node.js")
    
    # Check npm (use npm.cmd on Windows)
    npm_cmd = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    try:
        result = subprocess.run([npm_cmd, '--version'], capture_output=True, text=True, shell=True)
        logger.info(f"✓ npm: {result.stdout.strip()}")
    except FileNotFoundError:
        raise BuildError("npm not found. Please install npm")
    
    # Check Python
    logger.info(f"✓ Python: {sys.version.split()[0]}")
    
    # Check PyInstaller
    try:
        import PyInstaller
        logger.info(f"✓ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        raise BuildError("PyInstaller not found. Run: pip install pyinstaller")
    
    # Check pywebview
    try:
        import webview
        logger.info("✓ pywebview: installed")
    except ImportError:
        raise BuildError("pywebview not found. Run: pip install pywebview")


def build_frontend(base_path):
    """Build React frontend"""
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Building React Frontend")
    logger.info("="*60)
    
    frontend_path = base_path / 'frontend-new'
    
    if not frontend_path.exists():
        raise BuildError(f"Frontend directory not found: {frontend_path}")
    
    # Check if node_modules exists
    npm_cmd = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    if not (frontend_path / 'node_modules').exists():
        logger.info("Installing npm dependencies...")
        run_command(f'{npm_cmd} install', cwd=frontend_path)
    
    # Build frontend
    npm_cmd = 'npm.cmd' if sys.platform == 'win32' else 'npm'
    logger.info("Building frontend...")
    run_command(f'{npm_cmd} run build', cwd=frontend_path)
    
    # Check if build succeeded
    dist_path = frontend_path / 'dist'
    if not dist_path.exists():
        raise BuildError("Frontend build failed - dist directory not found")
    
    logger.info(f"✓ Frontend built successfully at {dist_path}")


def generate_icons(base_path):
    """Generate application icons"""
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Generating Application Icons")
    logger.info("="*60)
    
    desktop_path = base_path / 'desktop'
    desktop_path.mkdir(exist_ok=True)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple icon (gradient with text)
        size = 512
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background (purple/blue)
        for y in range(size):
            r = int(102 + (118 - 102) * y / size)
            g = int(126 + (75 - 126) * y / size)
            b = int(234 + (162 - 234) * y / size)
            draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b, 255))
        
        # Draw rounded corners
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=80, fill=255)
        img.putalpha(mask)
        
        # Draw Earth emoji or symbol
        try:
            font_size = 300
            font = ImageFont.truetype("seguiemj.ttf", font_size)
            draw.text((size//2, size//2), "🌍", font=font, anchor="mm")
        except:
            # Fallback to simple text
            font_size = 200
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            draw.text((size//2, size//2), "TF", font=font, anchor="mm", fill=(255, 255, 255, 255))
        
        # Save PNG
        png_path = desktop_path / 'icon.png'
        img.save(png_path, 'PNG')
        logger.info(f"✓ Created PNG icon: {png_path}")
        
        # Save ICO (Windows)
        ico_path = desktop_path / 'icon.ico'
        img_ico = img.resize((256, 256), Image.Resampling.LANCZOS)
        img_ico.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        logger.info(f"✓ Created ICO icon: {ico_path}")
        
    except Exception as e:
        logger.warning(f"Failed to generate icons: {e}")
        logger.warning("Continuing without custom icons...")


def build_executable(base_path):
    """Build executable with PyInstaller"""
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Building Executable with PyInstaller")
    logger.info("="*60)
    
    desktop_path = base_path / 'desktop'
    spec_file = desktop_path / 'terraforge.spec'
    
    if not spec_file.exists():
        raise BuildError(f"Spec file not found: {spec_file}")
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        dir_path = desktop_path / dir_name
        if dir_path.exists():
            logger.info(f"Cleaning {dir_name} directory...")
            shutil.rmtree(dir_path)
    
    # Run PyInstaller
    logger.info("Running PyInstaller (this may take several minutes)...")
    run_command(
        f'pyinstaller "{spec_file}" --clean --noconfirm',
        cwd=desktop_path
    )
    
    # Check if build succeeded
    dist_path = desktop_path / 'dist' / 'TerraForge Studio'
    if not dist_path.exists():
        raise BuildError("PyInstaller build failed - dist directory not found")
    
    logger.info(f"✓ Executable built successfully at {dist_path}")
    
    # Find the exe file
    exe_files = list(dist_path.glob('*.exe'))
    if exe_files:
        logger.info(f"✓ Executable: {exe_files[0].name}")
    
    return dist_path


def create_release_package(base_path, dist_path):
    """Create release package with README and resources"""
    logger.info("\n" + "="*60)
    logger.info("STEP 4: Creating Release Package")
    logger.info("="*60)
    
    # Create README for release
    readme_content = """# TerraForge Studio - Desktop Application

## Installation

1. Extract all files from this archive to a folder of your choice
2. Run `TerraForge Studio.exe`
3. The application will start and open in a native window

## Features

- Professional 3D terrain generation
- Real-world map data from OpenStreetMap
- Export to Unreal Engine 5, Unity, GLTF, GeoTIFF
- Built-in 3D preview with Cesium
- No installation required - fully portable

## System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Internet connection for map data

## First Run

On first run, the application will:
- Create cache and output directories
- Check for available data sources
- Start the local server

## Data Sources

- OpenStreetMap (free, no API key required)
- Optional: Configure API keys in .env file for premium sources

## Support

- Documentation: https://github.com/yourusername/TerraForge-Studio/docs
- Issues: https://github.com/yourusername/TerraForge-Studio/issues

## License

MIT License - See LICENSE file for details

---
TerraForge Studio v1.0.0
© 2025 TerraForge Team
"""
    
    readme_path = dist_path / 'README.txt'
    readme_path.write_text(readme_content, encoding='utf-8')
    logger.info(f"✓ Created README: {readme_path}")
    
    # Copy license
    license_src = base_path / 'LICENSE'
    if license_src.exists():
        license_dst = dist_path / 'LICENSE.txt'
        shutil.copy2(license_src, license_dst)
        logger.info(f"✓ Copied LICENSE: {license_dst}")
    
    # Create .env.example
    env_example = """# TerraForge Studio Configuration
# Copy this file to .env and configure your API keys

# Optional: Premium data sources
# SENTINELHUB_CLIENT_ID=your_client_id
# SENTINELHUB_CLIENT_SECRET=your_client_secret
# OPENTOPOGRAPHY_API_KEY=your_api_key
# AZURE_MAPS_KEY=your_api_key

# Optional: AI features (requires Ollama)
# OLLAMA_HOST=http://localhost:11434
# OLLAMA_VISION_MODEL=llava
# OLLAMA_CODER_MODEL=codellama
"""
    env_path = dist_path / '.env.example'
    env_path.write_text(env_example, encoding='utf-8')
    logger.info(f"✓ Created .env.example: {env_path}")


def main():
    """Main build process"""
    try:
        logger.info("="*60)
        logger.info("TerraForge Studio - Desktop Build Script")
        logger.info("="*60)
        
        base_path = Path(__file__).parent.parent
        logger.info(f"Base path: {base_path}")
        
        # Check requirements
        check_requirements()
        
        # Build frontend
        build_frontend(base_path)
        
        # Generate icons
        generate_icons(base_path)
        
        # Build executable
        dist_path = build_executable(base_path)
        
        # Create release package
        create_release_package(base_path, dist_path)
        
        logger.info("\n" + "="*60)
        logger.info("✓ BUILD COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        logger.info(f"\nExecutable location: {dist_path}")
        logger.info(f"\nTo run: {dist_path / 'TerraForge Studio.exe'}")
        logger.info("\nTo create installer or zip for distribution:")
        logger.info(f"  - Zip the entire '{dist_path.name}' folder")
        logger.info(f"  - Or use a tool like Inno Setup to create installer")
        
        return 0
        
    except BuildError as e:
        logger.error(f"\n❌ BUILD FAILED: {e}")
        return 1
    except Exception as e:
        logger.error(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
