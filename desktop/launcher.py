"""
TerraForge Studio - Desktop Application Launcher
Professional desktop interface using pywebview
"""

import sys
import os
import logging
import threading
import time
import socket
from pathlib import Path
import webview
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server

# Configure logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if we can import FastAPI (might be in frozen app)
try:
    from realworldmapgen.api.main import app
    from realworldmapgen.config import settings
except ImportError as e:
    logger.error(f"Failed to import application modules: {e}")
    logger.error("Make sure you're running from the correct directory")
    sys.exit(1)


class DesktopServer:
    """FastAPI server wrapper for desktop application"""
    
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.started = False
        
    def find_free_port(self):
        """Find a free port to use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def is_port_in_use(self, port):
        """Check if port is already in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0
    
    def start(self):
        """Start FastAPI server in background thread"""
        # Find free port if default is in use
        if self.is_port_in_use(self.port):
            logger.warning(f"Port {self.port} is in use, finding alternative...")
            self.port = self.find_free_port()
            logger.info(f"Using port {self.port}")
        
        config = Config(
            app=app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=False  # Disable access logs for cleaner UI
        )
        
        self.server = Server(config)
        
        # Start server in separate thread
        self.thread = threading.Thread(target=self.server.run, daemon=True)
        self.thread.start()
        
        # Wait for server to start
        max_retries = 30
        for i in range(max_retries):
            try:
                if self.is_port_in_use(self.port):
                    self.started = True
                    logger.info(f"Server started successfully on {self.host}:{self.port}")
                    break
            except:
                pass
            time.sleep(0.1)
        
        if not self.started:
            raise RuntimeError("Failed to start server")
        
        return f"http://{self.host}:{self.port}"
    
    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.should_exit = True


class TerraForgeApp:
    """Main desktop application class"""
    
    def __init__(self):
        self.server = DesktopServer()
        self.window = None
        
    def on_closing(self):
        """Handle window closing event"""
        logger.info("Application closing...")
        self.server.stop()
        
    def on_loaded(self):
        """Handle window loaded event"""
        logger.info("Application loaded successfully")
        
    def show_splash(self):
        """Show splash screen while loading"""
        splash_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
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
                    color: white;
                }
                .splash-container {
                    text-align: center;
                    animation: fadeIn 0.5s ease-in;
                }
                .logo {
                    font-size: 64px;
                    font-weight: bold;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .title {
                    font-size: 32px;
                    margin-bottom: 10px;
                    font-weight: 600;
                }
                .subtitle {
                    font-size: 18px;
                    opacity: 0.9;
                    margin-bottom: 40px;
                }
                .loader {
                    width: 50px;
                    height: 50px;
                    border: 4px solid rgba(255,255,255,0.3);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto;
                }
                .version {
                    margin-top: 30px;
                    font-size: 14px;
                    opacity: 0.7;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(-20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
        </head>
        <body>
            <div class="splash-container">
                <div class="logo">🌍</div>
                <div class="title">TerraForge Studio</div>
                <div class="subtitle">Professional 3D Terrain Generator</div>
                <div class="loader"></div>
                <div class="version">Version 1.0.0</div>
            </div>
        </body>
        </html>
        """
        return splash_html
    
    def run(self):
        """Run the desktop application"""
        logger.info("Starting TerraForge Studio Desktop...")
        
        # Start backend server
        try:
            url = self.server.start()
            logger.info(f"Backend server running at {url}")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return
        
        # Create main window
        self.window = webview.create_window(
            title="TerraForge Studio",
            url=url,
            width=1400,
            height=900,
            resizable=True,
            fullscreen=False,
            min_size=(1024, 768),
            background_color='#1a1a1a',
            text_select=True
        )
        
        # Set window events
        self.window.events.closing += self.on_closing
        self.window.events.loaded += self.on_loaded
        
        # Start GUI
        webview.start(
            debug=False,  # Set to True for development
            http_server=False  # We use our own FastAPI server
        )


def main():
    """Main entry point"""
    # Check if running as frozen executable
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = Path(sys.executable).parent
    else:
        # Running as script
        application_path = Path(__file__).parent.parent
    
    # Change working directory to application path
    os.chdir(application_path)
    
    # Create necessary directories
    cache_dir = application_path / "cache"
    output_dir = application_path / "output"
    cache_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    # Update settings paths
    settings.cache_dir = cache_dir
    settings.output_dir = output_dir
    
    logger.info(f"Application path: {application_path}")
    logger.info(f"Cache directory: {cache_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    # Run application
    app_instance = TerraForgeApp()
    app_instance.run()


if __name__ == "__main__":
    main()
