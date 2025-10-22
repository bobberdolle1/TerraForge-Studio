#!/usr/bin/env python3
"""
Enhanced launcher with splash screen and update checking
"""

import sys
import os
import logging
import threading
import time
from pathlib import Path
import webview

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import auto-update
try:
    from desktop.auto_update import check_for_updates, show_update_notification
except ImportError:
    check_for_updates = None
    show_update_notification = None

from desktop.launcher import DesktopServer


def show_splash_screen():
    """Show splash screen while loading"""
    splash_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            .splash {
                text-align: center;
                color: white;
            }
            .logo {
                font-size: 72px;
                margin-bottom: 20px;
            }
            .title {
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .subtitle {
                font-size: 18px;
                opacity: 0.9;
                margin-bottom: 30px;
            }
            .loader {
                width: 50px;
                height: 50px;
                border: 5px solid rgba(255,255,255,0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .status {
                margin-top: 20px;
                font-size: 14px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="splash">
            <div class="logo">🗺️</div>
            <div class="title">TerraForge Studio</div>
            <div class="subtitle">3D Terrain Generator</div>
            <div class="loader"></div>
            <div class="status" id="status">Starting...</div>
        </div>
        <script>
            const statuses = [
                'Initializing...',
                'Loading modules...',
                'Starting backend server...',
                'Preparing UI...',
                'Almost ready...'
            ];
            let i = 0;
            setInterval(() => {
                document.getElementById('status').textContent = statuses[i % statuses.length];
                i++;
            }, 1000);
        </script>
    </body>
    </html>
    """
    
    splash_window = webview.create_window(
        'TerraForge Studio - Loading',
        html=splash_html,
        width=500,
        height=400,
        frameless=True,
        easy_drag=True
    )
    
    return splash_window


def check_updates_in_background():
    """Check for updates without blocking startup"""
    if not check_for_updates:
        return
    
    def check():
        time.sleep(2)  # Wait for app to start
        try:
            update = check_for_updates()
            if update:
                logger.info(f"Update available: v{update['version']}")
                # Could show notification in app
        except Exception as e:
            logger.error(f"Update check failed: {e}")
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()


def main():
    """Enhanced main entry point"""
    logger.info("TerraForge Studio Desktop - Enhanced Launcher")
    
    # Check for updates in background
    check_updates_in_background()
    
    # Create and start server
    server = DesktopServer()
    port = server.find_free_port()
    server_thread = threading.Thread(target=server.start, args=(port,), daemon=True)
    server_thread.start()
    
    # Wait for server to start
    max_wait = 30
    for i in range(max_wait):
        if server.started:
            break
        time.sleep(1)
        if i == max_wait - 1:
            logger.error("Server failed to start in time")
            sys.exit(1)
    
    # Create main window
    logger.info("Creating application window...")
    
    window = webview.create_window(
        'TerraForge Studio',
        url=f'http://localhost:{port}',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(800, 600)
    )
    
    # Start webview
    logger.info("Starting webview...")
    webview.start(debug=False)
    
    # Cleanup
    logger.info("Application closed")
    server.stop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
