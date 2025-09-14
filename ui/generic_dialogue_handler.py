# ui/generic_dialogue_handler.py
"""
Generic Dialogue System - The Holy Grail Implementation
PHASE 1: REMOVE DUAL RENDERER - This is now the ONLY dialogue renderer

GOAL: Adding new NPC dialogue = Create 1 JSON file, nothing else.

This replaces ALL NPC-specific dialogue functions with a single universal system.
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button
from utils.npc_display import draw_npc_portrait
from utils.party_display import draw_party_status_panel

def draw_generic_dialogue_screen(surface, npc_id, game_state, fonts, images, controller=None, location_id=None):
    #print(f"🧭 RENDER GDH: draw_generic_dialogue_screen [{npc_id}] loc={location_id} from {__file__}")
    """
    Universal NPC dialogue screen - works for ANY NPC
    
    Args:
        npc_id: String identifier (e.g., 'garrick', 'meredith', 'town_guard')
        location_id: REQUIRED - location where dialogue is happening
        
    This function:
    1. Loads dialogue from data/dialogues/{location_id}_{npc_id}.json automatically
    2. Uses npc_id to display correct portrait automatically  
    3. Handles all dialogue UI through standardized system
    4. Works identically for any NPC without code changes
    """
    
    try: 
        # CRITICAL: Validate location_id is provided - no hardcoding allowed
        if not location_id:
            raise ValueError(f"location_id is REQUIRED for dialogue with {npc_id} - no hardcoded defaults allowed")
        
        # CRITICAL: Store location for dialogue session - this enables the event system to work
        location_attr = f'{npc_id}_current_location'
        setattr(game_state, location_attr, location_id)
        
        # CRITICAL: Set dialogue in progress flag
        progress_flag = f'{npc_id}_dialogue_in_progress'
        setattr(game_state, progress_flag, True)

        # Check for response display state first
        response_attr = f'showing_{npc_id}_response'
        if getattr(game_state, response_attr, False):
            return draw_generic_response_screen(surface, npc_id, game_state, fonts, location_id)
        
        # Get dialogue engine from controller
        if not controller:
            print(f"DEBUG: GDH: No controller provided")
            return draw_generic_fallback_screen(surface, npc_id, game_state, fonts)

        dialogue_engine = None
        if hasattr(controller, 'event_manager'):
            dialogue_engine = controller.event_manager.get_service('dialogue_engine')

        if not dialogue_engine:
            print(f"DEBUG: GDH: No dialogue engine available")
            return draw_generic_fallback_screen(surface, npc_id, game_state, fonts)
                
        # Automatically determine dialogue file based on location + NPC ID
        dialogue_file_id = f'{location_id}_{npc_id}'
        

        current_state = dialogue_engine.get_current_dialogue_state(npc_id)
        #print(f"🔍 DEBUG: GDH: Current dialogue state for {npc_id}: {current_state}")
        
        # Check for updated conversation data first (from choice processing)
        stored_conversation_attr = f'{npc_id}_conversation_data'
        conversation_data = getattr(game_state, stored_conversation_attr, None)
        if not conversation_data:
            # No stored data, get fresh conversation options from DialogueEngine
            conversation_data = dialogue_engine.get_conversation_options(dialogue_file_id, npc_id)
        #if conversation_data:
            #print(f"RENDER DEBUG: GDH: Got intro: {conversation_data.get('introduction', ['NO INTRO'])[0]}")
        
    except Exception as e:
        print(f"ERROR in draw_generic_dialogue_screen: {e}")
        import traceback
        traceback.print_exc()
        return draw_generic_fallback_screen(surface, npc_id, game_state, fonts)

    # PHASE 1: Render dialogue directly instead of calling DUU
    return render_dialogue_screen_directly(surface, npc_id, conversation_data, game_state, fonts)


def render_dialogue_screen_directly(surface, npc_id, conversation_data, game_state, fonts):
    """
    PHASE 1: Direct dialogue rendering - no more dual renderer conflict
    This replaces the call to draw_standard_dialogue_screen from dialogue_ui_utils
    """
    #print(f"🎨 DIRECT RENDER: Rendering dialogue for {npc_id}")
    
    # Clear screen
    surface.fill((0, 0, 0))
    
    # Draw NPC portrait using existing system
    draw_npc_portrait(surface, npc_id)
    
    # Draw standardized dialogue area
    dialogue_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_area)
    pygame.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_area, 2)
    
    # Title
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render(conversation_data['npc_name'].upper(), True, DIALOGUE_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(dialogue_area.centerx, 120))
    surface.blit(title_text, title_rect)
    
    # Check if we're in response mode
    response_attr = f'showing_{npc_id}_response'
    is_showing_response = getattr(game_state, response_attr, False)
    
    if is_showing_response:
        # Show response instead of choices
        response_attr = f'{npc_id}_dialogue_response'
        response_lines = getattr(game_state, response_attr, ["Thank you for listening."])
        
        # Render response text
        response_font = fonts.get('fantasy_small', fonts['normal'])
        y_pos = 160
        x_pos = 190
        
        for line in response_lines:
            if line.strip():
                # Simple text rendering - we'll improve this later
                text_surface = response_font.render(line, True, DIALOGUE_TEXT_COLOR)
                surface.blit(text_surface, (x_pos, y_pos))
                y_pos += 25
        
        # Draw party status panel
        draw_party_status_panel(surface, game_state, fonts)
        
        return {
            "type": "response_display",
            "action_rects": {}
        }
    
    else:
        # Regular dialogue mode - show introduction and options
        intro_data = conversation_data.get('introduction', "Hello there!")
        options = conversation_data.get('options', [])

        # Render introduction (handle array or string)
        intro_font = fonts.get('fantasy_small', fonts['normal'])
        y_pos = 160

        if isinstance(intro_data, list):
            for line in intro_data:
                intro_surface = intro_font.render(str(line), True, DIALOGUE_TEXT_COLOR)
                surface.blit(intro_surface, (190, y_pos))
                y_pos += 25
        else:
            intro_surface = intro_font.render(str(intro_data), True, DIALOGUE_TEXT_COLOR)
            surface.blit(intro_surface, (190, y_pos))
        
        # Render options
        choice_font = fonts.get('fantasy_small', fonts['normal'])
        y_pos += 20  # Continue from where intro text ended
        
        for i, choice in enumerate(options):
            choice_text = f"{i+1}. {choice.get('text', 'No text')}"
            choice_surface = choice_font.render(choice_text, True, DIALOGUE_OPTION_COLOR)
            surface.blit(choice_surface, (200, y_pos))
            y_pos += 30
        
        # Keyboard hints
        hint_font = fonts.get('fantasy_small', fonts['normal'])
        hint_text = "Choose Number Option  [Enter] First Option  [B/Backspace] Back"
        hint_surface = hint_font.render(hint_text, True, DIALOGUE_OPTION_COLOR)
        surface.blit(hint_surface, (195, dialogue_area.bottom - 40))
        
        # Draw party status panel
        draw_party_status_panel(surface, game_state, fonts)
        
        return {
            "type": "standard_dialogue",
            "conversation_data": conversation_data
        }


def draw_generic_response_screen(surface, npc_id, game_state, fonts, location_id):
    """
    Universal response screen - shows NPC's response to player choice
    PHASE 1: Direct rendering, no DUU dependencies
    """
    print(f"📝 RESPONSE RENDER: Showing response for {npc_id}")
    
    # Get response data
    response_attr = f'{npc_id}_dialogue_response'
    response_lines = getattr(game_state, response_attr, ["Thank you for listening."])
    
    # Clear screen
    surface.fill((0, 0, 0))
    
    # Draw NPC portrait
    draw_npc_portrait(surface, npc_id)
    
    # Draw dialogue area
    dialogue_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_area)
    pygame.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_area, 2)
    
    # Title
    title_font = fonts.get('fantasy_large', fonts['normal'])
    npc_display_name = npc_id.replace('_', ' ').title()
    title_text = title_font.render(npc_display_name.upper(), True, DIALOGUE_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(dialogue_area.centerx, 120))
    surface.blit(title_text, title_rect)
    
    # Response text
    response_font = fonts.get('fantasy_small', fonts['normal'])
    y_pos = 160
    x_pos = 190
    
    for line in response_lines:
        if line.strip():
            text_surface = response_font.render(line, True, DIALOGUE_TEXT_COLOR)
            surface.blit(text_surface, (x_pos, y_pos))
            y_pos += 25
    
    # Draw party status panel
    draw_party_status_panel(surface, game_state, fonts)
    
    return {
        "type": "response_screen",
        "action_rects": {}
    }


def draw_generic_fallback_screen(surface, npc_id, game_state, fonts):
    """Universal fallback screen if DialogueEngine not available"""
    print(f"🧭 RENDER GDH: draw_generic_fallback_screen [{npc_id}] from {__file__}")
    
    surface.fill((0, 0, 0))
    
    # Draw NPC portrait automatically based on npc_id
    draw_npc_portrait(surface, npc_id)
    
    # Get NPC name from ID (capitalize and format)
    npc_name = npc_id.replace('_', ' ').title()
    
    # Standard fallback message
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render(f"{npc_name.upper()}", True, (0, 255, 0))
    title_rect = title_text.get_rect(center=(512, 200))
    surface.blit(title_text, title_rect)
    
    message_font = fonts.get('fantasy_small', fonts['normal'])
    message_text = message_font.render("DialogueEngine not available - using simple interface", True, WHITE)
    message_rect = message_text.get_rect(center=(512, 250))
    surface.blit(message_text, message_rect)
    
    # Generic action buttons
    back_button = draw_button(surface, 412, 350, 100, 40, "BACK", message_font)
    
    return {"type": "fallback", "back_button": back_button}


def process_generic_dialogue_choice(npc_id, choice_index, game_state, controller, location_id=None):
    """
    Universal dialogue choice processor - works for ANY NPC
    
    Args:
        npc_id: String identifier for the NPC
        choice_index: Which dialogue option was selected
        
    This automatically:
    1. Loads correct dialogue file based on npc_id
    2. Processes choice through DialogueEngine
    3. Handles all resulting state changes
    4. Works for any NPC without code changes
    """
    print(f"🔧 PROCESS_GENERIC: GDH: Called for {npc_id}, choice {choice_index}")
    
    if not controller or not hasattr(controller, 'event_manager'):
        print(f"ERROR: No controller or event_manager for {npc_id}")
        return False
        
    dialogue_engine = controller.event_manager.get_service('dialogue_engine')
    if not dialogue_engine:
        print(f"ERROR: No dialogue engine available for {npc_id}")
        return False
    
    # Location_id is required for proper dialogue file loading
    if not location_id:
        # Try to get from game state
        location_attr = f'{npc_id}_current_location'
        location_id = getattr(game_state, location_attr, None)
        if not location_id:
            print(f"ERROR: No location_id available for {npc_id}")
            return False
    
    # Build dialogue file ID
    dialogue_file_id = f'{location_id}_{npc_id}'
    
    # Process the choice through the dialogue engine
    try:
        choice_result = dialogue_engine.process_dialogue_choice(dialogue_file_id, npc_id, str(choice_index))
        print(f"DEBUG: Choice result: {choice_result}")
        
        # CRITICAL: Clear stored conversation data after processing choice
        stored_conversation_attr = f'{npc_id}_conversation_data'
        setattr(game_state, stored_conversation_attr, None)
        print(f"🧹 Cleared stored conversation data for {npc_id}")

        return True
        
    except Exception as e:
        print(f"ERROR processing choice for {npc_id}: {e}")
        import traceback
        traceback.print_exc()
        return False