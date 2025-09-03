# ui/screen_manager.py
"""
Screen Manager - Generic Screen Handling System
Replaces hardcoded screen logic with data-driven approach
"""

from typing import Dict, Callable, Any, Optional

class ScreenManager:
    """
    Manages screen registration, transitions, and event routing
    Eliminates hardcoded screen handling from GameController
    """
    
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.screens = {}  # screen_name -> screen_handler
        self.current_screen = None
        
        print("📺 ScreenManager initialized")
    
    def register_screen(self, screen_name: str, click_handler: Callable):
        """Register a screen's click handling function"""
        self.screens[screen_name] = {
            'click_handler': click_handler
        }
        print(f"🔗 Registered screen: {screen_name}")
    
    def handle_screen_click(self, screen_name: str, mouse_pos, game_controller):
        """Route click to appropriate screen handler"""
        if screen_name in self.screens:
            handler = self.screens[screen_name]['click_handler']
            return handler(mouse_pos, game_controller, self.event_manager)
        else:
            print(f"⚠️ No handler registered for screen: {screen_name}")
            return False
    
    def get_registered_screens(self):
        """Get list of all registered screens"""
        return list(self.screens.keys())