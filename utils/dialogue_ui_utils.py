# utils/dialogue_ui_utils.py
"""
UI utility functions that work with the existing DialogueEngine
These functions provide consistent dialogue UI rendering across all NPCs
"""

import pygame
from utils.constants import *
from utils.graphics import draw_button
from utils.npc_display import draw_npc_portrait

print(f"🔎 DUI module path: {__file__}")

def draw_standard_dialogue_screen(surface, npc_name, conversation_data, game_state, fonts, controller=None):
    #print(f"🖼️ DUU: draw_standard_dialogue_screen [{npc_name}] from {__file__}")
    """
    Standardized dialogue screen that works with DialogueEngine data
    This replaces the individual draw_[npc]_dialogue_screen functions
    """
    #print(f"DEBUG: DUU: DSDS: conversation_data keys = {conversation_data.keys()}")
    #print(f"DEBUG: DUU: DSDS: default_actions = {conversation_data.get('default_actions', 'NOT FOUND')}")
    #print(f"DEBUG: DUU: DSDS: actions config = {conversation_data.get('actions', 'NOT FOUND')}")

    response_attr = f'showing_{npc_name}_response'
    #print(f"DEBUG: DUI: DSDS: {response_attr} = {getattr(game_state, response_attr, False)}")

    surface.fill((0, 0, 0))
    
    # Draw NPC portrait using your existing system
    draw_npc_portrait(surface, npc_name.lower())
        
    # Draw standardized dialogue area
    #dialogue_area = pygame.Rect(DIALOGUE_AREA_X, DIALOGUE_AREA_Y, DIALOGUE_AREA_WIDTH, DIALOGUE_AREA_HEIGHT)
    dialogue_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_area)
    pygame.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_area, 2)
    
    # Title
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render(conversation_data['npc_name'].upper(), True, DIALOGUE_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(dialogue_area.centerx, 120)) #DIALOGUE_TITLE_Y))
    surface.blit(title_text, title_rect)
    
    # Check if we're in response mode first
    response_attr = f'showing_{npc_name}_response'
    is_showing_response = getattr(game_state, response_attr, False)
    
    if is_showing_response:
        # RESPONSE MODE - Show response text instead of introduction + choices
        response_attr = f'{npc_name}_dialogue_response'
        response_lines = getattr(game_state, response_attr, ["Thank you for listening."])
        
        # Display response text in the same area as introduction
        intro_font = fonts.get('fantasy_small', fonts['normal'])
        y_pos = 160
        x_pos = 190
        
        for line in response_lines:
            if line.strip():  # Skip empty lines
                wrapped_lines = wrap_text(line, intro_font, DIALOGUE_AREA_WIDTH - 40)
                for wrapped_surface in wrapped_lines:
                    surface.blit(wrapped_surface, (x_pos, y_pos))
                    y_pos += DIALOGUE_TEXT_LINE_HEIGHT
                y_pos += 10  # Extra space between paragraphs
    else:
        # CHOICE MODE - Show normal introduction text
        intro_font = fonts.get('fantasy_small', fonts['normal'])
        y_pos = 160 #DIALOGUE_TEXT_START_Y
        x_pos = 190 #DIALOGUE_AREA_X

        for line in conversation_data['introduction']:
            wrapped_lines = wrap_text(line, intro_font, DIALOGUE_AREA_WIDTH - 40)
            for wrapped_surface in wrapped_lines:
                surface.blit(wrapped_surface, (x_pos, y_pos))#DIALOGUE_AREA_X - 70, y_pos))
                y_pos += DIALOGUE_TEXT_LINE_HEIGHT
       
    if not is_showing_response:
        y_pos += DIALOGUE_OPTIONS_START_Y_OFFSET

        for i, option in enumerate(conversation_data['options']):
            option_text = f"[{i+1}] {option['text']}"
            text_surface = intro_font.render(option_text, True, DIALOGUE_OPTION_COLOR)
            surface.blit(text_surface, (x_pos + 25, y_pos))
            y_pos += DIALOGUE_OPTION_HEIGHT
    
    # Draw party status using your existing system
    from utils.party_display import draw_party_status_panel
    draw_party_status_panel(surface, game_state, fonts)
    
    # No action buttons in keyboard mode - just render choice mode hint
    if not is_showing_response:
        hint_font = fonts.get('fantasy_small', fonts['normal'])
        hint_text = "[1-3] Choose Option  [Enter] First Option  [B/Backspace] Back"
        hint_surface = hint_font.render(hint_text, True, DIALOGUE_OPTION_COLOR)
        surface.blit(hint_surface, (dialogue_area.left + 20, dialogue_area.bottom - 40))

    # Keyboard-only mode - no clickable regions returned
    return {
        "type": "standard_dialogue",
        "conversation_data": conversation_data
    }


def draw_standard_response_screen(surface, npc_name, response_lines, game_state, fonts, controller=None):
    #print(f"🖼️ DUI: draw_standard_response_screen [{npc_name}] from {__file__}")
    """
    Standardized response screen that matches the dialogue layout
    Shows NPC's response using the same visual framework as dialogue options
    """
    surface.fill((0, 0, 0))
    
    y_pos = 160 #DIALOGUE_TEXT_START_Y
    x_pos = 190 #DIALOGUE_AREA_X
       
    # Draw NPC portrait using your existing system
    draw_npc_portrait(surface, npc_name.lower())

    # Draw standardized dialogue area (same as main dialogue)
    dialogue_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_area)
    pygame.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_area, 2)
    
    # Title (same styling as dialogue)
    title_font = fonts.get('fantasy_large', fonts['normal'])
    npc_display_name = npc_name.replace('_', ' ').title()
    title_text = title_font.render(npc_display_name.upper(), True, DIALOGUE_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(dialogue_area.centerx, DIALOGUE_TITLE_Y))
    surface.blit(title_text, title_rect)
    
    # Response text with proper wrapping (centered in dialogue area)
    response_font = fonts.get('fantasy_small', fonts['normal'])
    #y_pos = DIALOGUE_TEXT_START_Y
    
    for line in response_lines:
        if line.strip():  # Skip empty lines
            wrapped_lines = wrap_text(line, response_font, DIALOGUE_AREA_WIDTH - 40)
            for wrapped_surface in wrapped_lines:
                # Center each line in the dialogue area
                line_x = x_pos #DIALOGUE_AREA_X + (DIALOGUE_AREA_WIDTH - wrapped_surface.get_width()) // 2
                surface.blit(wrapped_surface, (line_x, y_pos))
                y_pos += DIALOGUE_TEXT_LINE_HEIGHT
            y_pos += 10  # Extra space between paragraphs
    
    # Draw party status using your existing system
    from utils.party_display import draw_party_status_panel
    draw_party_status_panel(surface, game_state, fonts)
    
    # Process response-level actions from DialogueEngine result
    action_rects = {}
    
    # Get actions from the current dialogue choice result stored in game state
    # This requires getting the actions from the last processed dialogue choice
    response_actions = []
    if controller and controller.dialogue_engine:
        # Get the last dialogue result actions
        response_attr = f'{npc_name}_dialogue_response_actions'
        response_actions = getattr(game_state, response_attr, [])
    
    response_attr = f'{npc_name}_dialogue_response_actions'
    response_actions = getattr(game_state, response_attr, [])
    #print(f"DEBUG: DSRS: Looking for attribute '{response_attr}' on game_state")
    #print(f"DEBUG: DSRS: Found response_actions = {response_actions}")
    #print(f"DEBUG: DSRS: All game_state attributes containing '{npc_name}': {[attr for attr in dir(game_state) if npc_name in attr]}")


    #print(f"DEBUG: DUI: DSRS: Processing {len(response_actions)} response-level action buttons")
    
# Check if dialogue can continue after this response
    can_continue_dialogue = False
    if controller and controller.dialogue_engine:
        # Get location from stored dialogue session data - no hardcoding
        location_id = getattr(game_state, f'{npc_name}_current_location', None)
        if not location_id:
            print(f"❌ No location stored for {npc_name} dialogue session")
            return  # or handle error appropriately
        dialogue_file_id = f'{location_id}_{npc_name}'
        
        dialogue_data = controller.dialogue_engine.dialogues.get(dialogue_file_id, {})
        action_definitions = dialogue_data.get('actions', {})
        
        # Get current dialogue state after processing the response
        current_state = controller.dialogue_engine.get_current_dialogue_state(npc_name)
        conversation_data = controller.dialogue_engine.get_conversation_options(dialogue_file_id, npc_name)
        
        # Check if there are dialogue options available (not just terminal actions)
        available_options = conversation_data.get('options', [])
        can_continue_dialogue = len(available_options) > 0
        
        #print(f"DEBUG: DSRS: Dialogue continuation check - options available: {len(available_options)}")
        #print(f"DEBUG: DSRS: Current dialogue state: {current_state}")
    else:
        action_definitions = {}  # Fallback if no dialogue engine

    # Keyboard hint strip for response mode - moved here to replace buttons
    hint_font = fonts.get('fantasy_small', fonts['normal'])
    hint_text = "[Enter] Continue  [B/Backspace] Back  [S] Shop (when shown)"
    hint_surface = hint_font.render(hint_text, True, DIALOGUE_OPTION_COLOR)
    surface.blit(hint_surface, (dialogue_area.left + 20, dialogue_area.bottom - 40))

    # Keyboard-only mode - no clickable regions returned
    return {
        "type": "standard_response"
    }