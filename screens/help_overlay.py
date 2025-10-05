# screens/help_overlay.py
"""
Terror in Redstone - Help Overlay System
First implementation using BaseTabbedOverlay - proves the concept works!

This replaces the old help_screen.py with a modern tabbed overlay implementation.
Single tab for now, but framework ready for expansion.
"""

import pygame
from utils.tabbed_overlay_utils import BaseTabbedOverlay
from utils.overlay_utils import *
from utils.graphics import draw_text

class HelpOverlay(BaseTabbedOverlay):
    """
    Help system overlay - single tab implementation
    
    PROOF OF CONCEPT:
    - Shows BaseTabbedOverlay working with one tab
    - Demonstrates content rendering
    - Tests keyboard/mouse integration
    - Foundation for more complex overlays
    """
    
    def __init__(self, screen_manager=None):
        super().__init__("help_key", "KEYBOARD SHORTCUTS", screen_manager)
        
        # Add single tab for help content
        self.add_tab("help_main", "Help", pygame.K_1)
        
        # Help content sections
        self.shortcuts = [
            ("GAME CONTROLS", [
                ("ESC", "Close overlay / Exit screen"),
                ("F5", "Quick save"),
                ("F7", "Save game menu"),
                ("F10", "Load game menu")
            ]),
            ("CHARACTER & PARTY", [
                ("I", "Inventory"),
                ("Q", "Quest log"),
                ("C", "Character sheet"),
                
            ]),
            ("NAVIGATION", [
                ("H", "Show this help screen")
            ])
        ]
    
    def render_tab_content(self, surface: pygame.Surface, active_tab, game_state, fonts, images):
        """
        Render help content - EXACT SAME LAYOUT as your existing help_screen.py
        
        This proves we can maintain existing functionality while using new architecture!
        """
        content_rect = self.get_content_area_rect()
        
        # Start rendering shortcuts (copied from your help_screen.py logic)
        current_y = content_rect.y + 20  # Start below tab area
        
        for category, keys in self.shortcuts:
            # Category header
            current_y += 15  # Extra space between categories
            draw_text(surface, category, 
                  fonts.get('fantasy_medium', fonts['normal']), 
                  content_rect.x + 60, current_y, CYAN)
            current_y += 35
        
            # Key bindings
            key_width = 30  # Width for the key column
            gap_width = 30
            for key, description in keys:
                key_text = f"{key:3}"
                draw_text(surface, key_text, 
                        fonts.get('fantasy_small', fonts['small']), 
                        content_rect.x + 60, current_y, WHITE)
                
                description_text = description
                draw_text(surface, description_text, 
                        fonts.get('fantasy_small', fonts['small']), 
                        content_rect.x + 60 + key_width + gap_width, current_y, WHITE)
                current_y += 25
            
            current_y += 15  # Extra space between categories
    
    def on_overlay_opened(self, game_state):
        """Called when help overlay opens"""
        super().on_overlay_opened(game_state)
        print("📖 Help overlay opened - tabbed version!")
    
    def on_overlay_closed(self, game_state):
        """Called when help overlay closes"""
        super().on_overlay_closed(game_state)
        print("📖 Help overlay closed")

# ========================================
# COMPATIBILITY LAYER
# ========================================

# Create global instance
help_overlay_instance = None

def get_help_overlay():
    """Get the global help overlay instance"""
    global help_overlay_instance
    if help_overlay_instance is None:
        help_overlay_instance = HelpOverlay()
    return help_overlay_instance

def draw_help_screen(surface, game_state, fonts, images=None):
    """
    REPLACEMENT for old help_screen.py - EXACT SAME FUNCTION SIGNATURE
    """
    
    overlay = get_help_overlay()
    
    # Register with input handler on first render if not already registered  
    if not getattr(overlay, '_input_registered', False):
        try:
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'self' in frame.f_locals:
                screen_manager = frame.f_locals['self']
                if hasattr(screen_manager, 'input_handler'):
                    overlay.screen_manager = screen_manager
                    overlay._register_with_input_handler()
                    overlay._input_registered = True
        except:
            overlay._input_registered = True
    
    overlay.render(surface, game_state, fonts, images)
    return None

def handle_help_screen_click(mouse_pos, result):
    """
    COMPATIBILITY: Handle clicks on help screen
    
    This maintains the exact same interface as your original help_screen.py
    but internally uses the new tabbed overlay system.
    """
    overlay = get_help_overlay()
    
    # Try to handle tab clicks first
    if overlay.handle_mouse_click(mouse_pos):
        return None  # Tab click handled
    
    # No clicks handled - equivalent to your original "close help" behavior
    return 'close_help'

def handle_help_keyboard_input(key, game_state):
    """NEW: Handle keyboard input for help overlay"""
    if getattr(game_state, 'help_screen_open', False):
        overlay = get_help_overlay()
        return overlay.handle_keyboard_input(key)
    return False