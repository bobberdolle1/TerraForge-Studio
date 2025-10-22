#!/usr/bin/env python3
"""
Auto-update system for TerraForge Studio
Checks for new releases on GitHub and downloads them
"""

import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from packaging import version
import logging

logger = logging.getLogger(__name__)

GITHUB_REPO = "bobberdolle1/TerraForge-Studio"
CURRENT_VERSION = "1.0.2"


def get_latest_release():
    """Get latest release info from GitHub"""
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    try:
        with urllib.request.urlopen(api_url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                'version': data['tag_name'].lstrip('v'),
                'name': data['name'],
                'url': data['html_url'],
                'assets': data['assets'],
                'published_at': data['published_at'],
                'body': data['body']
            }
    except urllib.error.URLError as e:
        logger.error(f"Failed to check for updates: {e}")
        return None


def check_for_updates():
    """Check if a new version is available"""
    latest = get_latest_release()
    
    if not latest:
        return None
    
    latest_version = latest['version']
    
    if version.parse(latest_version) > version.parse(CURRENT_VERSION):
        return latest
    
    return None


def get_download_url_for_platform():
    """Get the correct download URL for current platform"""
    latest = get_latest_release()
    
    if not latest:
        return None
    
    platform_suffix = {
        'win32': 'Windows-Portable.zip',
        'darwin': 'macOS.dmg',
        'linux': 'Linux-x86_64.AppImage'
    }.get(sys.platform)
    
    if not platform_suffix:
        return None
    
    for asset in latest['assets']:
        if asset['name'].endswith(platform_suffix):
            return asset['browser_download_url']
    
    return None


def download_update(url, destination):
    """Download update file with progress"""
    try:
        print(f"Downloading update from {url}...")
        
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                print(f"\rProgress: {percent}%", end='')
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\nDownload complete!")
        return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


def show_update_notification(update_info):
    """Show update notification to user"""
    print("\n" + "="*60)
    print(f"🎉 New version available: v{update_info['version']}")
    print("="*60)
    print(f"\nRelease: {update_info['name']}")
    print(f"Published: {update_info['published_at']}")
    print(f"\nWhat's new:")
    print(update_info['body'][:500] + "..." if len(update_info['body']) > 500 else update_info['body'])
    print(f"\nDownload: {update_info['url']}")
    print("="*60)


if __name__ == '__main__':
    # Test the auto-update system
    print(f"Current version: {CURRENT_VERSION}")
    print("Checking for updates...")
    
    update = check_for_updates()
    
    if update:
        show_update_notification(update)
        
        response = input("\nDownload now? (y/n): ")
        if response.lower() == 'y':
            download_url = get_download_url_for_platform()
            if download_url:
                destination = Path.home() / "Downloads" / f"TerraForge-Studio-{update['version']}.zip"
                if download_update(download_url, destination):
                    print(f"\nSaved to: {destination}")
    else:
        print("✓ You're running the latest version!")
