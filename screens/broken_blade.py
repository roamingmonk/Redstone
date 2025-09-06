# screens/broken_blade.py
"""
The Broken Blade Tavern - Clean DialogueEngine Implementation
Professional architecture with proper separation of concerns
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button
from utils.npc_display import draw_npc_portrait
from utils.party_display import draw_party_status_panel
from utils.dialogue_ui_utils import draw_standard_dialogue_screen
from utils.dialogue_ui_utils import draw_standard_response_screen

def draw_broken_blade_main_screen(surface, game_state, fonts, images, controller=None):
    """
    Main Broken Blade tavern screen - Clean implementation with LocationManager integration
    Five-button interface matching tavern_main design but with clean architecture
    """
    surface.fill((0, 0, 0))
    
    # Get location data from LocationManager
    location_data = None
    area_data = None
    if controller:
        location_manager = controller.data_manager.location_manager
        if location_manager:
            location_data = location_manager.get_location_data('redstone_broken_blade')
            if location_data:
                area_data = location_data.get('areas', {}).get('main_room')
    
    # Use tavern background image if available
    background_image = images.get('locations', {}).get('broken_blade_main')
    if background_image:
        surface.blit(background_image, (0, LAYOUT_IMAGE_Y))
    else:
        # Draw border for image area
        draw_border(surface, 0, LAYOUT_IMAGE_Y, 1024, LAYOUT_IMAGE_HEIGHT)
    
    # Title and description from LocationManager or fallback
    title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
    if area_data:
        title_text = area_data.get('display_name', 'THE BROKEN BLADE TAVERN')
        atmosphere = area_data.get('description', {}).get('atmosphere', '')
        subtitle = area_data.get('description', {}).get('subtitle', 'Choose your path, adventurer...')
        ambient_details = area_data.get('description', {}).get('ambient_details', '')
        
        desc_lines = [subtitle]
        if atmosphere:
            desc_lines.append("")
            desc_lines.append(atmosphere)
        if ambient_details:
            desc_lines.append(ambient_details)
    else:
        # Fallback if LocationManager data unavailable
        title_text = "THE BROKEN BLADE TAVERN"
        desc_lines = [
            "Choose your path, adventurer...",
            "",
            "The tavern bustles with activity. Adventurers gather around tables,",
            "sharing tales and seeking companions for dangerous quests."
        ]
    
    title_surface = title_font.render(title_text, True, WHITE)
    title_rect = title_surface.get_rect(center=(512, 50))
    surface.blit(title_surface, title_rect)
    
    # Description text
    desc_font = fonts.get('fantasy_medium', fonts.get('medium', fonts['normal']))
    
    y_pos = 570
    for line in desc_lines:
        if line:  # Skip empty lines
            line_surface = desc_font.render(line, True, WHITE)
            line_rect = line_surface.get_rect(center=(512, y_pos))
            surface.blit(line_surface, line_rect)
        y_pos += 25
    
    # Five main buttons - using constants for consistency
    from utils.constants import LAYOUT_BUTTON_CENTER_Y, calculate_button_font

    button_font = calculate_button_font(fonts, "TALK TO BARTENDER", 170)  # Use your width
    button_y = LAYOUT_BUTTON_CENTER_Y  # Use standard button position
    button_width = 170
    button_height = 40

    # Calculate button positions for even spacing
    total_width = 5 * button_width + 4 * 15
    start_x = (1024 - total_width) // 2
    
    # Button 1: Talk to Garrick (Bartender)
    bartender_button = draw_button(surface, start_x, button_y, button_width, button_height,
                                "TALK TO BARTENDER", button_font)
    
    # Button 2: Talk to Server (Meredith)
    server_x = start_x + button_width + 15
    server_button = draw_button(surface, server_x, button_y, button_width, button_height,
                               "TALK TO SERVER", button_font)
    
    # Button 3: Talk to Patrons
    patrons_x = server_x + button_width + 15
    patrons_button = draw_button(surface, patrons_x, button_y, button_width, button_height,
                                "TALK TO PATRONS", button_font)
    
    # Button 4: Gamble
    gamble_x = patrons_x + button_width + 15
    gamble_button = draw_button(surface, gamble_x, button_y, button_width, button_height,
                               "GAMBLE", button_font)
    
    # Button 5: Leave Tavern
    leave_x = gamble_x + button_width + 15
    leave_button = draw_button(surface, leave_x, button_y, button_width, button_height,
                              "LEAVE TAVERN", button_font)
    
    # Help text
    help_font = fonts.get('help_text', fonts['small'])
    help_text = "Press H for help and shortcuts"
    help_surface = help_font.render(help_text, True, WHITE)
    help_x = (1024 - help_surface.get_width()) // 2
    surface.blit(help_surface, (help_x, 790))

    #add party status panel on right
    from utils.party_display import draw_party_status_panel
    draw_party_status_panel(surface, game_state, fonts)
    
    return bartender_button, server_button, patrons_button, gamble_button, leave_button


