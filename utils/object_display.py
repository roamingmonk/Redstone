# utils/object_display.py
"""
Object Display System for Object Examination Dialogues
Handles icons for environmental objects, altars, books, containers, etc.
"""

import pygame
import os
from utils.constants import CHARACTER_ICONS_PATH, LAYOUT_IMAGE_Y, SPACING
from utils.graphics import draw_border

# Default icon for all object examinations
DEFAULT_OBJECT_ICON = "object_examination.png"

# Optional: Custom icons for specific object types (extensible)
OBJECT_ICON_MAPPING = {
    'altar': 'object_examination.png',      # Use default for now
    'symbols': 'object_examination.png',    # Use default for now
    'ritual': 'object_examination.png',     # Use default for now
    'book': 'object_examination.png',       # Future: book_icon.png
    'chest': 'object_examination.png',      # Future: chest_icon.png
    'door': 'object_examination.png',       # Future: door_icon.png
}

def get_object_icon_filename(object_id):
    """
    Get the appropriate icon filename for an object type.
    Falls back to default magnifying glass if no custom icon exists.
    
    Args:
        object_id: The object identifier (e.g., 'altar', 'symbols', 'book')
        
    Returns:
        str: Filename of the icon to use
    """
    # Check if custom icon is defined in mapping
    if object_id in OBJECT_ICON_MAPPING:
        return OBJECT_ICON_MAPPING[object_id]
    
    # Default to magnifying glass for unknown objects
    return DEFAULT_OBJECT_ICON

def draw_object_icon(surface, object_id=None):
    """
    Draws an object examination icon for dialogue screens.
    Used when examining objects/environment instead of talking to NPCs.
    
    Position matches NPC portrait location for consistent UI layout.
    
    Args:
        surface: The Pygame surface to draw on
        object_id: The object identifier (e.g., 'altar', 'symbols', 'book')
    """
    ICON_SIZE = (160, 160)
    
    # Get the appropriate icon filename
    icon_filename = get_object_icon_filename(object_id)
    icon_path = os.path.join(CHARACTER_ICONS_PATH, icon_filename)
    
    try:
        if os.path.exists(icon_path):
            # Load and scale icon
            obj_icon = pygame.image.load(icon_path)
            scaled_icon = pygame.transform.scale(obj_icon, ICON_SIZE)
            
            # Position to match NPC portrait (left side of screen)
            icon_x = SPACING['margin'] - 10
            icon_y = 100
            icon_rect = scaled_icon.get_rect(topleft=(icon_x, icon_y))
            
            # Draw icon and border
            surface.blit(scaled_icon, icon_rect)
            draw_border(surface, icon_rect.x, icon_rect.y, 
                       icon_rect.width, icon_rect.height)
            
            return icon_rect
            
        else:
            # Icon file not found - draw fallback
            print(f"⚠️ Object icon not found: {icon_path}")
            return draw_object_fallback(surface, object_id, ICON_SIZE)
            
    except Exception as e:
        print(f"❌ Error loading object icon '{icon_filename}': {e}")
        return draw_object_fallback(surface, object_id, ICON_SIZE)

def draw_object_fallback(surface, object_id, icon_size):
    """
    Draw a fallback gray box when icon cannot be loaded.
    
    Args:
        surface: Pygame surface to draw on
        object_id: Object identifier (for display)
        icon_size: Tuple (width, height) for icon dimensions
        
    Returns:
        pygame.Rect: The drawn rectangle
    """
    icon_x = SPACING['margin'] - 10
    icon_y = 100
    icon_rect = pygame.Rect(icon_x, icon_y, icon_size[0], icon_size[1])
    
    # Draw gray fallback box
    pygame.draw.rect(surface, (80, 80, 80), icon_rect)
    draw_border(surface, icon_rect.x, icon_rect.y, 
               icon_rect.width, icon_rect.height)
    
    # Draw "?" text in center
    try:
        fallback_font = pygame.font.Font(None, 72)
        text_surface = fallback_font.render("?", True, (200, 200, 200))
        text_rect = text_surface.get_rect(center=icon_rect.center)
        surface.blit(text_surface, text_rect)
    except:
        pass
    
    return icon_rect

# Future extension: Add custom icon support
def register_custom_object_icon(object_id, icon_filename):
    """
    Register a custom icon for a specific object type.
    Allows game designers to add unique icons without code changes.
    
    Args:
        object_id: Object type identifier (e.g., 'ancient_book', 'magic_crystal')
        icon_filename: Name of icon file in CHARACTER_ICONS_PATH
        
    Example:
        register_custom_object_icon('ancient_book', 'book_ancient.png')
        register_custom_object_icon('magic_crystal', 'crystal_icon.png')
    """
    OBJECT_ICON_MAPPING[object_id] = icon_filename
    print(f"📦 Registered custom icon for '{object_id}': {icon_filename}")