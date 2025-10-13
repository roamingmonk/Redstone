"""
Terror in Redstone - Overlay Utilities
Shared functions for popup screens (inventory, quest log, character sheet)
"""

import pygame
from utils.graphics import draw_centered_text
from utils.constants import (BLACK, WHITE, SOFT_YELLOW, CORNFLOWER_BLUE,
                             DARKEST_GRAY, DARK_GRAY, LIGHTEST_GRAY, VERY_DARK_GRAY,
                             BROWN, DARK_BROWN, RECESSED_BROWN, LIGHT_BROWN, BRIGHT_GREEN)

# Colors for popup screens
#BROWN = (101, 67, 33)
#DARK_BROWN = (70, 45, 20)

# Let's try this color for row highlighting - classic RPG blue
SELECTION_COLOR = CORNFLOWER_BLUE  # Light blue

def draw_popup_background(surface):
    """Draw the brown background for popup screens"""
    surface.fill(DARK_BROWN)

def draw_chunky_border(surface, x, y, width, height, thickness=4):
    """Draw chunky retro borders like Gold Box RPGs"""
    # Outer white border
    pygame.draw.rect(surface, WHITE, (x, y, width, height), thickness)
    # Inner dark border for depth
    pygame.draw.rect(surface, DARKEST_GRAY, (x + thickness, y + thickness, 
                    width - 2*thickness, height - 2*thickness), 2)

def draw_tab_button(surface, x, y, width, height, text, font, active=False):
    """Draw a folder-style tab (active or inactive)"""
    if active:
        # Active tab: lighter color, raised appearance
        color = LIGHT_BROWN  # Light brown
        text_color = BLACK
        border_color = WHITE
        # Draw slightly taller to show it's "in front"
        tab_height = height + 2
        tab_y = y - 2
    else:
        # Inactive tab: darker, recessed appearance  
        color = RECESSED_BROWN   # DarkISH brown  
        text_color = LIGHTEST_GRAY  # Light gray text
        border_color = DARKEST_GRAY
        tab_height = height
        tab_y = y
    
    # Draw tab background (rectangular for now, we can make it fancier later)
    pygame.draw.rect(surface, color, (x, tab_y, width, tab_height))
    
    # Draw top and side borders only (no bottom border for folder effect)
    pygame.draw.line(surface, border_color, (x, tab_y), (x + width, tab_y), 2)  # Top
    pygame.draw.line(surface, border_color, (x, tab_y), (x, tab_y + tab_height), 2)  # Left
    pygame.draw.line(surface, border_color, (x + width, tab_y), (x + width, tab_y + tab_height), 2)  # Right
    
    # Draw centered text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, tab_y + tab_height//2))
    surface.blit(text_surface, text_rect)
    
    return pygame.Rect(x, tab_y, width, tab_height)
    


def draw_item_row(surface, x, y, width, height, selected=False):
    """Draw a table row background (selected or normal)"""
    if selected:
        pygame.draw.rect(surface, SELECTION_COLOR, (x, y, width, height))
    else:
        pygame.draw.rect(surface, WHITE, (x, y, width, height))
    
    # Draw row border
    pygame.draw.rect(surface, DARKEST_GRAY, (x, y, width, height), 1)
    
    return pygame.Rect(x, y, width, height)

def draw_button(surface, x, y, width, height, text, font, pressed=False, selected=False, enabled=True):
    """Draw a retro-style button"""
    if not enabled:
        color = DARKEST_GRAY
        border_color = DARKEST_GRAY
        text_color = VERY_DARK_GRAY
    elif selected:
        color = SOFT_YELLOW
        border_color = WHITE
        text_color = BLACK
    else:
        color = DARKEST_GRAY if pressed else DARK_GRAY
        border_color = DARKEST_GRAY if pressed else WHITE
        text_color = BROWN
    
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    surface.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height) if enabled else None

# ========================================
# CENTRALIZED OVERLAY STATE MANAGEMENT
# ========================================

class OverlayState:
    """
    Centralized overlay state manager
    
    Enforces single overlay behavior by design and provides
    extensible state management for overlay-specific data.
    """
    
    def __init__(self):
        self.active_overlay = None  # Only one overlay active at a time
        self.overlay_data = {}      # Per-overlay state data (tabs, selections, etc.)
    
    def open_overlay(self, overlay_id):
        """Open an overlay (closes any other overlay automatically)"""
        self.active_overlay = overlay_id
        
        # Initialize overlay data if not exists
        if overlay_id not in self.overlay_data:
            self.overlay_data[overlay_id] = {}
    
    def close_overlay(self):
        """Close the currently active overlay"""
        self.active_overlay = None
    
    def close_specific_overlay(self, overlay_id):
        """Close a specific overlay if it's active"""
        if self.active_overlay == overlay_id:
            self.active_overlay = None
    
    def is_open(self, overlay_id):
        """Check if a specific overlay is open"""
        return self.active_overlay == overlay_id
    
    def get_active_overlay(self):
        """Get the currently active overlay ID"""
        return self.active_overlay
    
    def has_any_overlay_open(self):
        """Check if any overlay is currently open"""
        return self.active_overlay is not None
    
    def get_overlay_data(self, overlay_id):
        """Get state data for a specific overlay"""
        return self.overlay_data.get(overlay_id, {})
    
    def set_overlay_data(self, overlay_id, key, value):
        """Set state data for a specific overlay"""
        if overlay_id not in self.overlay_data:
            self.overlay_data[overlay_id] = {}
        self.overlay_data[overlay_id][key] = value
    
    def clear_overlay_data(self, overlay_id):
        """Clear all state data for a specific overlay"""
        if overlay_id in self.overlay_data:
            del self.overlay_data[overlay_id]