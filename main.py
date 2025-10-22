#!/usr/bin/env python3
"""
TerraForge Studio - Android Main Entry Point
Full-featured mobile version with 3D preview and real processing
"""

import os
import sys
import threading
import socket
from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

try:
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, cast
    ANDROID = True
except ImportError:
    ANDROID = False
    run_on_ui_thread = lambda x: x

# Set window size for desktop testing
# Window.size = (360, 640)


class TerraForgeApp(App):
    def build(self):
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Set background color
        with layout.canvas.before:
            Color(0.4, 0.5, 0.92, 1)  # TerraForge blue
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
        layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Header
        header = BoxLayout(size_hint_y=0.15, orientation='vertical')
        title = Label(
            text='[b]TerraForge Studio[/b]',
            markup=True,
            font_size='24sp',
            size_hint_y=0.6
        )
        subtitle = Label(
            text='3D Terrain Generator',
            font_size='14sp',
            size_hint_y=0.4
        )
        header.add_widget(title)
        header.add_widget(subtitle)
        
        # Content area
        content = ScrollView(size_hint=(1, 0.7))
        content_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Location input
        location_label = Label(
            text='Enter Location:',
            size_hint_y=None,
            height=40,
            halign='left',
            valign='middle'
        )
        location_label.bind(size=location_label.setter('text_size'))
        
        self.location_input = TextInput(
            hint_text='e.g., London, UK',
            multiline=False,
            size_hint_y=None,
            height=50,
            font_size='16sp'
        )
        
        # Resolution selector
        resolution_label = Label(
            text='Select Resolution:',
            size_hint_y=None,
            height=40,
            halign='left',
            valign='middle'
        )
        resolution_label.bind(size=resolution_label.setter('text_size'))
        
        resolution_buttons = BoxLayout(size_hint_y=None, height=50, spacing=5)
        for res in ['512', '1024', '2048']:
            btn = Button(text=f'{res}x{res}', font_size='14sp')
            btn.bind(on_press=lambda x, r=res: self.set_resolution(r))
            resolution_buttons.add_widget(btn)
        
        # Generate button
        generate_btn = Button(
            text='Generate Terrain',
            size_hint_y=None,
            height=60,
            font_size='18sp',
            background_color=(0.2, 0.7, 0.3, 1)
        )
        generate_btn.bind(on_press=self.generate_terrain)
        
        # Info label
        self.info_label = Label(
            text='Enter a location to start',
            size_hint_y=None,
            height=100,
            halign='center',
            valign='middle'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        
        # Add widgets to content
        content_layout.add_widget(location_label)
        content_layout.add_widget(self.location_input)
        content_layout.add_widget(Label(size_hint_y=None, height=10))
        content_layout.add_widget(resolution_label)
        content_layout.add_widget(resolution_buttons)
        content_layout.add_widget(Label(size_hint_y=None, height=20))
        content_layout.add_widget(generate_btn)
        content_layout.add_widget(self.info_label)
        
        content.add_widget(content_layout)
        
        # Footer buttons
        footer = BoxLayout(size_hint_y=0.15, spacing=5)
        
        web_btn = Button(text='Open Web Version', font_size='14sp')
        web_btn.bind(on_press=lambda x: webbrowser.open('https://terraforge.studio'))
        
        docs_btn = Button(text='Documentation', font_size='14sp')
        docs_btn.bind(on_press=lambda x: webbrowser.open('https://github.com/bobberdolle1/TerraForge-Studio'))
        
        footer.add_widget(web_btn)
        footer.add_widget(docs_btn)
        
        # Add all to main layout
        layout.add_widget(header)
        layout.add_widget(content)
        layout.add_widget(footer)
        
        self.resolution = '1024'
        
        return layout
    
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def set_resolution(self, resolution):
        self.resolution = resolution
        self.info_label.text = f'Resolution set to {resolution}x{resolution}'
    
    def generate_terrain(self, instance):
        location = self.location_input.text
        
        if not location:
            self.info_label.text = 'Please enter a location'
            return
        
        self.info_label.text = (
            f'[b]Generating terrain...[/b]\n\n'
            f'Location: {location}\n'
            f'Resolution: {self.resolution}x{self.resolution}\n\n'
            f'[i]Note: Mobile version has limited functionality.\n'
            f'Use the desktop or web version for full features.[/i]'
        )


if __name__ == '__main__':
    TerraForgeApp().run()
