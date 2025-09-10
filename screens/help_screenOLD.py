# screens/help_screen.py
"""
Help Screen - Keyboard shortcuts and controls reference
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text, draw_text

def draw_help_screen(surface, game_state, fonts, images=None):
    """
    Draw help overlay showing all keyboard shortcuts
    Returns button rectangles for interaction
    """
    # Fill with semi-transparent dark background
    overlay = pygame.Surface((1024, 768))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    surface.blit(overlay, (0, 0))
    
    # Main help panel
    panel_width = 600
    panel_height = 600
    panel_x = (1024 - panel_width) // 2
    panel_y = (768 - panel_height) // 2
    
    # Draw panel background and border
    pygame.draw.rect(surface, (40, 40, 40), (panel_x, panel_y, panel_width, panel_height))
    draw_border(surface, panel_x, panel_y, panel_width, panel_height)
    
    # Title
    title_y = panel_y + 30
    #title_x = (panel_width - fonts.get('fantasy_large', fonts['header']).size("KEYBOARD SHORTCUTS")[0]) // 2
    #draw_centered_text(surface, "KEYBOARD SHORTCUTS", 
    #                  fonts.get('fantasy_large', fonts['header']), 
    #                  title_y, YELLOW, panel_width)
    
    title_font = fonts.get('fantasy_large', fonts['header'])
    title_text = "KEYBOARD SHORTCUTS"
    title_width = title_font.size(title_text)[0]
    title_x = (panel_width - title_width) // 2
    draw_text(surface, title_text, title_font, panel_x + title_x, title_y, YELLOW)

    # Shortcuts organized by category
    shortcuts = [
        ("GAME CONTROLS", [
            ("ESC", "Close overlay / Exit screen"),
            ("F1", "Toggle debug mode"), 
            ("F5", "Quick save"),
            ("F7", "Save game menu"),
            ("F10", "Load game menu")
            #(" ", " ")
        ]),
        ("CHARACTER & PARTY", [
            ("I", "Toggle inventory"),
            ("Q", "Toggle quest log"),
            ("C", "Character sheet"),
            ("P", "Party management")
            #(" ", " ")
        ]),
        ("NAVIGATION", [
            #("Arrow Keys", "Navigate menus"),
            #("Enter/Space", "Confirm selection"),
            ("H", "Show this help screen")
        ])
    ]
    
    # Draw shortcuts
    current_y = title_y + 60
    
    for category, keys in shortcuts:
        # Category header
        current_y += 15  # Extra space between categories
        draw_text(surface, category, 
              fonts.get('fantasy_medium', fonts['normal']), 
              panel_x + 20, current_y, CYAN)
        current_y += 35
    
        # Key bindings
        key_width = 30  # Adjust the width for the key column
        gap_width = 30
        for key, description in keys:
            key_text = f"{key:3}"
            draw_text(surface, key_text, 
                    fonts.get('fantasy_small', fonts['small']), 
                    panel_x + 20, current_y, WHITE)
            
            description_text = description
            draw_text(surface, description_text, 
                    fonts.get('fantasy_small', fonts['small']), 
                    panel_x + 20 + key_width + gap_width, current_y, WHITE)
            current_y += 25
        
        current_y += 15  # Extra space between categories
    
    return None

def handle_help_screen_click(mouse_pos, result):
    """Handle clicks on help screen"""
    if result and result.collidepoint(mouse_pos):
        return 'close_help'
    return None