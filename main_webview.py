#!/usr/bin/env python3
"""
TerraForge Studio - Android with WebView
Full React frontend + FastAPI backend in mobile app
"""

import os
import sys
import threading
import socket
import time
from pathlib import Path

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.logger import Logger

# Android-specific imports
try:
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, cast
    ANDROID = True
    
    # Android Java classes
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
    LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')
    LinearLayout = autoclass('android.widget.LinearLayout')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    
except ImportError:
    ANDROID = False
    Logger.warning('Android: Not running on Android, desktop mode')


class BackendServer:
    """FastAPI backend server for Android"""
    
    def __init__(self):
        self.port = self.find_free_port()
        self.server = None
        self.thread = None
        self.started = False
    
    def find_free_port(self):
        """Find free port for backend"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start(self):
        """Start FastAPI backend"""
        Logger.info(f'Backend: Starting on port {self.port}')
        
        # Add app to path
        sys.path.insert(0, str(Path(__file__).parent))
        
        try:
            from realworldmapgen.api.main import app
            import uvicorn
            
            # Run server
            uvicorn.run(
                app,
                host='127.0.0.1',
                port=self.port,
                log_level='info'
            )
        except Exception as e:
            Logger.error(f'Backend: Failed to start: {e}')
            self.started = False
    
    def start_async(self):
        """Start backend in background thread"""
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()
        
        # Wait for server to start
        for _ in range(30):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('127.0.0.1', self.port))
                sock.close()
                
                if result == 0:
                    self.started = True
                    Logger.info('Backend: Server started successfully')
                    return True
            except:
                pass
            
            time.sleep(1)
        
        Logger.error('Backend: Failed to start in time')
        return False


class WebViewWidget(Widget):
    """Kivy widget wrapping Android WebView"""
    
    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.webview = None
        
        if ANDROID:
            self.create_webview()
    
    @run_on_ui_thread
    def create_webview(self):
        """Create Android WebView"""
        activity = PythonActivity.mActivity
        
        # Create WebView
        self.webview = WebView(activity)
        self.webview.getSettings().setJavaScriptEnabled(True)
        self.webview.getSettings().setDomStorageEnabled(True)
        self.webview.getSettings().setAllowFileAccess(True)
        self.webview.getSettings().setAllowContentAccess(True)
        
        # Enable debugging
        if hasattr(WebView, 'setWebContentsDebuggingEnabled'):
            WebView.setWebContentsDebuggingEnabled(True)
        
        # Set WebView client
        self.webview.setWebViewClient(WebViewClient())
        
        # Add to layout
        layout = cast(LinearLayout, activity.findViewById(0x01000000))  # android.R.id.content
        layout.addView(
            self.webview,
            LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT
            )
        )
        
        # Load URL
        Logger.info(f'WebView: Loading {self.url}')
        self.webview.loadUrl(self.url)
    
    @run_on_ui_thread
    def reload(self):
        """Reload WebView"""
        if self.webview:
            self.webview.reload()
    
    @run_on_ui_thread
    def go_back(self):
        """Navigate back"""
        if self.webview and self.webview.canGoBack():
            self.webview.goBack()
            return True
        return False


class TerraForgeApp(App):
    """Main Android app with full features"""
    
    def build(self):
        self.title = 'TerraForge Studio'
        
        # Start backend server
        Logger.info('App: Starting backend server...')
        self.backend = BackendServer()
        
        if ANDROID:
            # Start server in background
            self.backend.start_async()
            
            # Wait a bit for server to start
            Clock.schedule_once(self.load_webview, 3)
            
            # Show loading screen
            return self.create_loading_screen()
        else:
            # Desktop mode - show info
            from kivy.uix.label import Label
            return Label(
                text='Android app - run on Android device\nFor desktop, use: python desktop/launcher.py',
                font_size='18sp'
            )
    
    def create_loading_screen(self):
        """Create loading screen while server starts"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.graphics import Color, Rectangle
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Background
        with layout.canvas.before:
            Color(0.4, 0.5, 0.92, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Logo
        logo = Label(text='🗺️', font_size='80sp')
        title = Label(text='TerraForge Studio', font_size='28sp', bold=True)
        subtitle = Label(text='Loading...', font_size='18sp')
        
        layout.add_widget(Widget())  # Spacer
        layout.add_widget(logo)
        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(Widget())  # Spacer
        
        self.loading_label = subtitle
        return layout
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def load_webview(self, dt):
        """Load WebView with React frontend"""
        if not self.backend.started:
            self.loading_label.text = 'Backend failed to start\nRetrying...'
            Clock.schedule_once(self.load_webview, 2)
            return
        
        Logger.info(f'App: Loading WebView on http://127.0.0.1:{self.backend.port}')
        
        # Replace root widget with WebView
        url = f'http://127.0.0.1:{self.backend.port}'
        self.root = WebViewWidget(url=url)
    
    def on_pause(self):
        """Handle app pause"""
        return True
    
    def on_resume(self):
        """Handle app resume"""
        pass


if __name__ == '__main__':
    TerraForgeApp().run()
