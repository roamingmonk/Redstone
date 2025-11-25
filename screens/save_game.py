# screens/save_game.py
"""
Save Game Screen - Full screen overlay for save file management
"""

import pygame
from utils.constants import (BLACK, YELLOW, BLUE, WHITE, GRAY, LIGHT_GRAY)
from utils.graphics import draw_border, draw_button, draw_centered_text
from datetime import datetime

def draw_save_game_screen(surface, game_state, fonts, images, save_manager=None):
    """
    Draw the save game screen with save slot selection
    Returns button rectangles and selected save info
    """
    # Fill with black background
    surface.fill(BLACK)
    
    # Draw chunky retro border around entire screen
    draw_border(surface, 20, 20, 1024-40, 768-40)
    
    # Title
    title_y = 60
    draw_centered_text(surface, "Save Game", 
                      fonts.get('fantasy_large', fonts['header']), 
                      title_y, YELLOW)
    
    # Subtitle with decorative tildes
    subtitle_y = title_y + 50
    draw_centered_text(surface, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 
                      fonts.get('fantasy_medium', fonts['normal']), 
                      subtitle_y, YELLOW)
    
    # Save slot display area
    slot_start_y = 150
    slot_height = 40
    slot_spacing = 20
    
    # Get save slots data from SaveManager (same as load_game.py)
    save_slots = []
    if save_manager:
        all_slots = save_manager.populate_save_slot_cache()
        # Filter to only show manual save slots (1, 2, 3, 4, 5)
        save_slots = [slot for slot in all_slots if slot['slot_num'] in [1, 2, 3, 4, 5]]
    else:
        # Fallback - empty slots
        slots_to_check = [
            (1, "1"),
            (2, "2"), 
            (3, "3"),
            (4, "4"),
            (5, "5"),
        ]
        save_slots = [{'slot_num': slot_num, 'slot_name': slot_name, 'save_info': None} 
                     for slot_num, slot_name in slots_to_check]
    
    # Draw save slots (same pattern as load_game.py)
    slot_rects = []
    for i, slot_data in enumerate(save_slots):
        slot_y = slot_start_y + (i * (slot_height + slot_spacing))
        slot_rect = pygame.Rect(80, slot_y, 864, slot_height)
        slot_rects.append((slot_rect, slot_data['slot_num']))  # Format for ScreenManager
        
        # Check if this slot is selected
        selected = (hasattr(game_state, 'save_selected_slot') and 
                   game_state.save_selected_slot == slot_data['slot_num'])
        
        # Draw slot background with selection highlighting
        if selected:
            pygame.draw.rect(surface, BLUE, slot_rect)  # Blue highlight
        else:
            pygame.draw.rect(surface, LIGHT_GRAY, slot_rect)
        
        # Draw slot border
        pygame.draw.rect(surface, WHITE, slot_rect, 2)
        
        # Slot name (left aligned)
        slot_name_x = slot_rect.x + 10
        slot_name_y = slot_rect.y + 12
        slot_surface = fonts.get('fantasy_medium', fonts['normal']).render(
            slot_data['slot_name'], True, YELLOW)
        surface.blit(slot_surface, (slot_name_x, slot_name_y))
        
        # Save information
        if slot_data['save_info']:
            # Character name
            char_name = slot_data['save_info']['character_name']
            char_x = slot_rect.x + 40
            char_surface = fonts.get('fantasy_small', fonts['normal']).render(
                char_name, True, WHITE)
            surface.blit(char_surface, (char_x, slot_name_y))
            
            # Location (make it readable)
            location = slot_data['save_info']['current_screen']
            location_readable = location.replace('_', ' ').title()
            if location == 'tavern_main':
                location_readable = 'Tavern'
            elif location == 'welcome':
                location_readable = 'Town'
            elif location == 'summary':
                location_readable = 'Character Summary'
                
            location_x = char_x + 340
            location_surface = fonts.get('fantasy_small', fonts['normal']).render(
                location_readable, True, WHITE)
            surface.blit(location_surface, (location_x, slot_name_y))
            
            # Timestamp (formatted)
            timestamp = slot_data['save_info']['timestamp']
            if timestamp != 'Unknown':
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%b %d, %I:%M %p')
                except:
                    time_str = 'Unknown'
            else:
                time_str = 'Unknown'
                
            time_x = location_x + 240
            time_surface = fonts.get('fantasy_small', fonts['normal']).render(
                time_str, True, WHITE)
            surface.blit(time_surface, (time_x, slot_name_y))
            
        else:
            # Empty slot
            empty_x = slot_rect.x + 200
            empty_surface = fonts.get('fantasy_small', fonts['normal']).render(
                "[Empty Slot]", True, (GRAY))
            surface.blit(empty_surface, (empty_x, slot_name_y))
    
      # Status message
    status_y = slot_start_y + (len(save_slots) * (slot_height + slot_spacing)) + 20
    status_text = getattr(game_state, 'save_status_message', "Select a slot to save your game")
    draw_centered_text(surface, status_text,
                      fonts.get('fantasy_small', fonts['normal']),
                      status_y, WHITE)
    
    # Buttons at bottom
    button_y = 650
    button_width = 120
    button_height = 50
    button_spacing = 40
    
    # Calculate button positions (centered)
    total_button_width = (3 * button_width) + (2 * button_spacing)  # Save, Save&Quit, Cancel
    start_x = (1024 - total_button_width) // 2
    
    # Determine button states
    has_selection = (hasattr(game_state, 'save_selected_slot') and 
                    game_state.save_selected_slot is not None)
    
    # Save button (only enabled if slot selected)
    save_button = None
    if has_selection:
        save_button = draw_button(surface, start_x, button_y, button_width, button_height,
                                 "SAVE", fonts.get('fantasy_small', fonts['normal']),
                                 selected=True)
    else:
        # Draw disabled save button
        draw_button(surface, start_x, button_y, button_width, button_height,
                   "SAVE", fonts.get('fantasy_small', fonts['normal']),
                   selected=False)
    
    #Save & Quit button (middle position)
    save_quit_x = start_x + button_width + button_spacing
    save_quit_button = None
    if has_selection:
        save_quit_button = draw_button(surface, save_quit_x, button_y, button_width, button_height,
                                     "SAVE&QUIT", fonts.get('fantasy_tiny', fonts['fantasy_small']),
                                     selected=True)
    else:
        # Draw disabled save & quit button
        draw_button(surface, save_quit_x, button_y, button_width, button_height,
                   "SAVE&QUIT", fonts.get('fantasy_tiny', fonts['fantasy_small']),
                   selected=False)
    
    # Cancel button (now rightmost)
    cancel_x = start_x + (2 * button_width) + (2 * button_spacing)
    cancel_button = draw_button(surface, cancel_x, button_y, button_width, button_height,
                               "CANCEL", fonts.get('fantasy_small', fonts['normal']))
    
    return {
        'slot_rects': slot_rects,
        'save_slots': save_slots,
        'save_button': save_button,  # Only returns if enabled
        'save_quit_button': save_quit_button,  # Only returns if enabled
        'cancel_button': cancel_button
    }
