#!/usr/bin/env python3
"""
Universal Build Script for TerraForge Studio
Supports: Windows, Linux, macOS, Android
"""

import sys
import os
import argparse
import subprocess
import platform
from pathlib import Path

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_step(text):
    print(f"{Colors.CYAN}▶ {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def run_command(cmd, cwd=None):
    """Run shell command and return result"""
    print_step(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"Command failed: {result.stderr}")
        return False
    return True

def build_windows_portable():
    """Build Windows portable .exe"""
    print_header("Building Windows Portable")
    
    if not run_command("python desktop/build.py"):
        return False
    
    print_success("Windows portable build completed")
    return True

def build_windows_installer():
    """Build Windows installer with Inno Setup"""
    print_header("Building Windows Installer")
    
    # First build portable
    if not build_windows_portable():
        return False
    
    # Check if Inno Setup is installed
    iscc_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not Path(iscc_path).exists():
        print_error("Inno Setup not found. Install from: https://jrsoftware.org/isinfo.php")
        return False
    
    # Run Inno Setup compiler
    if not run_command(f'"{iscc_path}" desktop/installer.iss'):
        return False
    
    print_success("Windows installer build completed")
    return True

def build_linux():
    """Build Linux AppImage"""
    print_header("Building Linux AppImage")
    
    print_step("Installing dependencies...")
    run_command("pip install -r requirements.txt")
    run_command("pip install -r desktop/desktop_requirements.txt")
    
    print_step("Building frontend...")
    run_command("cd frontend-new && npm install && npm run build")
    
    print_step("Creating AppImage...")
    # TODO: Implement AppImage build
    print_error("Linux build not yet implemented")
    return False

def build_macos():
    """Build macOS .app and .dmg"""
    print_header("Building macOS Application")
    
    if platform.system() != 'Darwin':
        print_error("macOS builds must be run on macOS")
        return False
    
    print_step("Installing dependencies...")
    run_command("pip install -r requirements.txt")
    run_command("pip install -r desktop/desktop_requirements.txt")
    run_command("pip install py2app")
    
    print_step("Building frontend...")
    run_command("cd frontend-new && npm install && npm run build")
    
    print_step("Creating .app bundle...")
    # TODO: Implement py2app build
    print_error("macOS build not yet implemented")
    return False

def build_android():
    """Build Android APK"""
    print_header("Building Android APK")
    
    print_step("Checking Android SDK...")
    # TODO: Implement Android build with Buildozer/Kivy
    print_error("Android build not yet implemented")
    return False

def create_release():
    """Create release packages"""
    print_header("Creating Release Packages")
    
    base_path = Path(__file__).parent.parent
    dist_path = base_path / "desktop" / "dist" / "TerraForge Studio"
    
    if not dist_path.exists():
        print_error("Build directory not found. Run build first.")
        return False
    
    # Create ZIP for portable version
    print_step("Creating portable ZIP...")
    zip_name = f"TerraForge-Studio-v1.0.0-{platform.system()}-{platform.machine()}.zip"
    
    if platform.system() == "Windows":
        run_command(f'powershell Compress-Archive -Path "{dist_path}" -DestinationPath "{zip_name}" -Force')
    else:
        run_command(f'cd desktop/dist && zip -r "../../{zip_name}" "TerraForge Studio"')
    
    print_success(f"Created: {zip_name}")
    
    # Calculate checksum
    print_step("Calculating SHA256 checksum...")
    if platform.system() == "Windows":
        run_command(f'powershell Get-FileHash {zip_name} -Algorithm SHA256 | Select-Object Hash | Out-File {zip_name}.sha256')
    else:
        run_command(f'shasum -a 256 {zip_name} > {zip_name}.sha256')
    
    print_success("Release package created")
    return True

def main():
    parser = argparse.ArgumentParser(description='Build TerraForge Studio for multiple platforms')
    parser.add_argument('--platform', choices=['windows', 'linux', 'macos', 'android', 'all'], 
                       default='windows', help='Target platform')
    parser.add_argument('--installer', action='store_true', help='Create installer (Windows only)')
    parser.add_argument('--release', action='store_true', help='Create release package')
    
    args = parser.parse_args()
    
    print_header("TerraForge Studio - Universal Build System")
    print(f"Platform: {args.platform}")
    print(f"Current OS: {platform.system()}")
    
    success = False
    
    if args.platform == 'windows' or args.platform == 'all':
        if args.installer:
            success = build_windows_installer()
        else:
            success = build_windows_portable()
    
    if args.platform == 'linux' or args.platform == 'all':
        success = build_linux()
    
    if args.platform == 'macos' or args.platform == 'all':
        success = build_macos()
    
    if args.platform == 'android' or args.platform == 'all':
        success = build_android()
    
    if args.release and success:
        create_release()
    
    if success:
        print_header("✓ BUILD SUCCESSFUL!")
    else:
        print_header("✗ BUILD FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
