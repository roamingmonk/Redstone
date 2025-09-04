# screens/patron_selection.py
"""
Patron Selection Screen - Professional Event-Driven Architecture
Follows the broken_blade_main pattern for consistent event handling
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text
from utils.party_display import draw_party_status_panel

def draw_patron_selection_screen(surface, game_state, fonts, images, controller=None):
    """
    Professional patron selection screen with event-driven architecture
    Returns button rectangles for the screen manager to handle clicks
    """
    surface.fill(BLACK)
    
    # Use standardized 3-zone layout matching broken_blade_main
    from utils.constants import (LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, 
                            LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                            LAYOUT_BUTTON_Y, LAYOUT_DIALOG_TEXT_Y)

    # ===== IMAGE ZONE =====
    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT
    
    # Draw border around image area
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Tavern interior atmosphere (matching broken_blade visual style)
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    # Rich tavern brown background
    pygame.draw.rect(surface, (40, 20, 10), (img_x, img_y, img_width, img_height))
    
    # Professional title
    title = "TAVERN PATRONS"
    draw_centered_text(surface, title, fonts.get('fantasy_large', fonts['header']), 
                    image_y + 240, YELLOW)
    
    # ===== DIALOG ZONE =====
    dialog_y = LAYOUT_DIALOG_Y
    dialog_height = LAYOUT_DIALOG_HEIGHT
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # Description text
    text_y = LAYOUT_DIALOG_TEXT_Y
    intro_text = "You scan the tavern and notice several interesting patrons..."
    prompt_text = "Choose someone to approach:"
    
    draw_centered_text(surface, intro_text, 
                fonts.get('fantasy_small', fonts['normal']), text_y, WHITE)
    
    desc_y = text_y + 30
    draw_centered_text(surface, prompt_text, 
                fonts.get('fantasy_medium', fonts['normal']), desc_y, BRIGHT_GREEN)
    
    # ===== BUTTON ZONE =====
    button_font = fonts.get('fantasy_small', fonts['normal'])
    button_height = 40
    button_spacing = 15
    
    # Calculate dynamic button widths for patron names
    padding = 20
    gareth_width = button_font.size("GARETH")[0] + padding
    elara_width = button_font.size("ELARA")[0] + padding  
    thorman_width = button_font.size("THORMAN")[0] + padding
    lyra_width = button_font.size("LYRA")[0] + padding
    pete_width = button_font.size("OLD PETE")[0] + padding
    back_width = button_font.size("BACK")[0] + padding
    
    # Calculate total width and center positioning
    patron_widths = [gareth_width, elara_width, thorman_width, lyra_width, pete_width, back_width]
    total_width = sum(patron_widths) + (len(patron_widths) - 1) * button_spacing
    start_x = (1024 - total_width) // 2
    button_y = LAYOUT_BUTTON_CENTER_Y
    
    # Draw patron buttons
    current_x = start_x
    
    # Gareth - The Warrior
    gareth_button = draw_button(surface, current_x, button_y, gareth_width, button_height,
                               "GARETH", button_font)
    current_x += gareth_width + button_spacing
    
    # Elara - The Sage  
    elara_button = draw_button(surface, current_x, button_y, elara_width, button_height,
                              "ELARA", button_font)
    current_x += elara_width + button_spacing
    
    # Thorman - The Dwarf
    thorman_button = draw_button(surface, current_x, button_y, thorman_width, button_height,
                                "THORMAN", button_font)
    current_x += thorman_width + button_spacing
    
    # Lyra - The Rogue
    lyra_button = draw_button(surface, current_x, button_y, lyra_width, button_height,
                             "LYRA", button_font)
    current_x += lyra_width + button_spacing
    
    # Pete - The Comic Relief
    pete_button = draw_button(surface, current_x, button_y, pete_width, button_height,
                             "OLD PETE", button_font)
    current_x += pete_width + button_spacing
    
    # Back button
    back_button = draw_button(surface, current_x, button_y, back_width, button_height,
                             "BACK", button_font)
    
    # Help text
    help_font = fonts.get('help_text', fonts['small'])
    help_text = "Press H for help and shortcuts"
    help_surface = help_font.render(help_text, True, WHITE)
    help_x = (1024 - help_surface.get_width()) // 2
    surface.blit(help_surface, (help_x, 720))
    
    # Party status panel
    draw_party_status_panel(surface, game_state, fonts)
    
    # Return button rectangles for event-driven click handling
    return gareth_button, elara_button, thorman_button, lyra_button, pete_button, back_button