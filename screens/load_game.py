# screens/load_game.py
"""
Load Game Screen - Full screen overlay for save file management
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text
from datetime import datetime

def draw_load_game_screen(surface, game_state, fonts, images, save_manager=None):
    """
    Draw the load game screen with save slot selection
    Returns button rectangles and selected save info
    """
    # Fill with black background
    surface.fill(BLACK)
    
    # Draw chunky retro border around entire screen
    draw_border(surface, 20, 20, 1024-40, 768-40)
    
    # Title
    title_y = 60
    draw_centered_text(surface, "Load Game", 
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
    
    save_slots = []
    slot_rects = []
    
    # Define save slots to check
    slots_to_check = [
        (99, "Quick Save"),
        (1, "Slot 1"),
        (2, "Slot 2"), 
        (3, "Slot 3"),
        (4, "Slot 4"),
        (5, "Slot 5"),
        (0, "Auto-Save")
    ]
    
    # Get save slots data from SaveManager
    save_slots = []
    if save_manager:
        save_slots = save_manager.populate_save_slot_cache()
    else:
        # Fallback - empty slots
        save_slots = [{'slot_num': slot_num, 'slot_name': slot_name, 'save_info': None} 
                     for slot_num, slot_name in slots_to_check]
    
    
    # Draw save slots
    for i, slot_data in enumerate(save_slots):
        slot_y = slot_start_y + (i * (slot_height + slot_spacing))
        slot_rect = pygame.Rect(80, slot_y, 864, slot_height)
        slot_rects.append((slot_rect, slot_data['slot_num'])) 
        
        # Check if this slot is selected
        selected = (hasattr(game_state, 'load_selected_slot') and 
                   game_state.load_selected_slot == slot_data['slot_num'])
        
        # Draw selection highlight
        if selected:
            pygame.draw.rect(surface, BLUE, slot_rect)
        else:
            pygame.draw.rect(surface, (40, 40, 40), slot_rect)
        
        # Draw slot border
        pygame.draw.rect(surface, WHITE, slot_rect, 2)
        
        # Slot name (left aligned)
        slot_name_x = slot_rect.x + 20
        slot_name_y = slot_rect.y + 12
        slot_surface = fonts.get('fantasy_medium', fonts['normal']).render(
            slot_data['slot_name'], True, YELLOW)
       #### print(f"DEBUG: Slot name '{slot_data['slot_name']}' at position ({slot_name_x}, {slot_name_y})")
        surface.blit(slot_surface, (slot_name_x, slot_name_y))

        # Save information
        if slot_data['save_info']:
            # Character name
            char_name = slot_data['save_info']['character_name']
            char_x = slot_rect.x + 120
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
                
            location_x = char_x + 300
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
                
            time_x = location_x + 150
            time_surface = fonts.get('fantasy_small', fonts['normal']).render(
                time_str, True, WHITE)
            surface.blit(time_surface, (time_x, slot_name_y))
            
        else:
            # Empty slot
            empty_x = slot_rect.x + 200
            empty_surface = fonts.get('fantasy_small', fonts['normal']).render(
                "[Empty Slot]", True, (128, 128, 128))
            surface.blit(empty_surface, (empty_x, slot_name_y))
    
    # Status message area
    status_y = slot_start_y + (len(save_slots) * (slot_height + slot_spacing)) + 40
    status_text = "Select a save file to load or delete"
    
    # Check for status messages in game_state
    if hasattr(game_state, 'load_status_message'):
        status_text = game_state.load_status_message
    
    draw_centered_text(surface, status_text,
                      fonts.get('fantasy_small', fonts['normal']),
                      status_y, WHITE)
    
    # Buttons at bottom
    button_y = 650
    button_width = 120
    button_height = 50
    button_spacing = 40
    
    # Calculate button positions (centered)
    total_button_width = (3 * button_width) + (2 * button_spacing)
    start_x = (1024 - total_button_width) // 2
    
    # Determine button states
    has_selection = (hasattr(game_state, 'load_selected_slot') and 
                    game_state.load_selected_slot is not None)
    
    selected_slot_info = None
    if has_selection:
        for slot_data in save_slots:
            if slot_data['slot_num'] == game_state.load_selected_slot:
                selected_slot_info = slot_data['save_info']
                break
    
    can_load = has_selection and selected_slot_info is not None
    
    # Load button
    load_button = draw_button(surface, start_x, button_y, button_width, button_height,
                             "LOAD", fonts.get('fantasy_small', fonts['normal']),
                             selected=can_load)
    
    # Delete button  
    delete_x = start_x + button_width + button_spacing
    delete_button = draw_button(surface, delete_x, button_y, button_width, button_height,
                               "DELETE", fonts.get('fantasy_small', fonts['normal']),
                               selected=has_selection)
    
    # Cancel button
    cancel_x = delete_x + button_width + button_spacing
    cancel_button = draw_button(surface, cancel_x, button_y, button_width, button_height,
                               "CANCEL", fonts.get('fantasy_small', fonts['normal']))
    
    return {
        'slot_rects': slot_rects,
        'save_slots': save_slots,
        'load_button': load_button if can_load else None,
        'delete_button': delete_button if has_selection else None,
        'cancel_button': cancel_button
    }

def handle_load_game_click(mouse_pos, game_state, result, event_manager=None):
    """
    Handle mouse clicks on the load game screen
    Returns True if click was handled, False otherwise
    """
    print(f"🖱️ LOAD CLICK DEBUG: mouse_pos={mouse_pos}, event_manager={event_manager is not None}")
    if not result:
        return False
    
   # Handle slot selection clicks
    for slot_rect, slot_num in result['slot_rects']:
        if slot_rect.collidepoint(mouse_pos):
            event_manager.emit("LOAD_SLOT_SELECTED", {'slot_num': slot_num})
            return True
    
    # Handle button clicks
    if result['load_button'] and result['load_button'].collidepoint(mouse_pos):
        event_manager.emit("LOAD_GAME_CONFIRM", {})
        return True
    
    if result['delete_button'] and result['delete_button'].collidepoint(mouse_pos):
        event_manager.emit("DELETE_SAVE_CONFIRM", {})
        return True
    
    if result['cancel_button'] and result['cancel_button'].collidepoint(mouse_pos):
        event_manager.emit("LOAD_SCREEN_CANCEL", {})
        return True
    
    return False