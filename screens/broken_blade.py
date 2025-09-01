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
    if controller and controller.data_manager:
        location_manager = controller.data_manager.get_manager('locations')
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

def draw_garrick_dialogue_screen(surface, game_state, fonts, images, controller=None):
    """
    Garrick dialogue screen using DialogueEngine
    Clean implementation of Baldur's Gate style dialogue
    """
    surface.fill((0, 0, 0))
    
    # Get dialogue engine from controller
    if not controller:
        return draw_garrick_fallback_screen(surface, game_state, fonts)
    
    dialogue_engine = controller.data_manager.get_manager('dialogue')
    if not dialogue_engine:
        print("DialogueEngine not available, using fallback")
        return draw_garrick_fallback_screen(surface, game_state, fonts)
    
    # Check for response display state first
    if getattr(game_state, 'showing_garrick_response', False):
        return draw_garrick_response_screen(surface, game_state, fonts)
    
    # Get current conversation options from DialogueEngine
    conversation_data = dialogue_engine.get_conversation_options('tavern_garrick', 'garrick')
      

    # Draw dialogue area
    dialogue_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, (20, 20, 20), dialogue_area)
    pygame.draw.rect(surface, WHITE, dialogue_area, 2)
    
    # Title
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render(conversation_data['npc_name'].upper(), True, (0, 255, 0))
    title_rect = title_text.get_rect(center=(dialogue_area.centerx, 120))
    surface.blit(title_text, title_rect)
    
    # Introduction text
    intro_font = fonts.get('fantasy_small', fonts['normal'])
    y_pos = 160
    for line in conversation_data['introduction']:
        line_surface = intro_font.render(line, True, WHITE)
        # Word wrap if line is too long
        if line_surface.get_width() > dialogue_area.width - 40:
            # Simple word wrapping (can be enhanced)
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_surface = intro_font.render(test_line, True, WHITE)
                if test_surface.get_width() <= dialogue_area.width - 40:
                    current_line = test_line
                else:
                    if current_line:
                        line_surface = intro_font.render(current_line, True, WHITE)
                        surface.blit(line_surface, (190, y_pos))
                        y_pos += 20
                    current_line = word
            if current_line:
                line_surface = intro_font.render(current_line, True, WHITE)
                surface.blit(line_surface, (190, y_pos))
                y_pos += 20
        else:
            surface.blit(line_surface, (190, y_pos))
            y_pos += 25
    
    # Dialogue options
    option_rects = []
    y_pos += 20
    option_font = fonts.get('fantasy_small', fonts['normal'])
    
    for i, option in enumerate(conversation_data['options']):
        option_text = f"[{i+1}] {option['text']}"
        
        # Create option area
        option_surface = option_font.render(option_text, True, (0, 255, 0))
        option_rect = pygame.Rect(290, y_pos - 5, dialogue_area.width - 40, 25)
        
        # Highlight on hover
        mouse_pos = pygame.mouse.get_pos()
        if option_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, (30, 40, 40), option_rect)
            option_surface = option_font.render(option_text, True, (255, 255, 0))
        
        surface.blit(option_surface, (190, y_pos))
        option_rects.append(option_rect)
        y_pos += 30
    
    # Action buttons
    action_rects = {}
    button_y = 520
    button_font = fonts.get('fantasy_small', fonts['normal'])
    
    button_x = 350
    for action_name in conversation_data.get('default_actions', []):
        if action_name == 'shop':
            button_text = "SHOP"
        elif action_name == 'goodbye':
            button_text = "FAREWELL"
        else:
            continue
            
        button_rect = draw_button(surface, button_x, button_y, 120, 35, button_text, button_font)
        action_rects[action_name] = button_rect
        button_x += 140

    #add NPC picture on panel on left
    draw_npc_portrait(surface, 'garrick')

    #add party status panel on right
    draw_party_status_panel(surface, game_state, fonts) 

    return {
        "type": "garrick_dialogue",
        "option_rects": option_rects,
        "action_rects": action_rects,
        "conversation_data": conversation_data
    }

def draw_garrick_response_screen(surface, game_state, fonts):
    """Display Garrick's response to player choice"""
    
    surface.fill((0, 0, 0))
    
    # Response area
    response_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, (20, 20, 20), response_area)
    pygame.draw.rect(surface, WHITE, response_area, 2)

    # Title
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render("GARRICK RESPONDS", True, (0, 255, 0))
    title_rect = title_text.get_rect(center=(512, 120))
    surface.blit(title_text, title_rect)
    
    # Response text
    response_font = fonts.get('fantasy_small', fonts['normal'])
   # y_pos = 180
   # for line in game_state.garrick_dialogue_response:
   #     line_surface = response_font.render(line, True, WHITE)
   #     line_rect = line_surface.get_rect(center=(512, y_pos))
   #     surface.blit(line_surface, line_rect)
   #     y_pos += 25
    
    
    # Get the list of dialogue lines from your game_state
    #dialogue_lines = game_state.garrick_dialogue_response
    
    # 1. COMBINE THE LIST INTO A SINGLE STRING
    # The 'join' method correctly handles the conversion from a list to a string.
    full_dialogue_text = " ".join(game_state.garrick_dialogue_response)

    # Calculate the area where the text should go (between the portraits)
    # Assumes portrait width is 200 based on previous work
    portrait_width = 160
    text_area_width = SCREEN_WIDTH - (portrait_width * 2) - (SPACING['margin'] * 4)
    text_area_x = SPACING['margin'] + portrait_width + (SPACING['margin'] * 2)

    # Use the wrap function to break the text into correctly sized lines
    wrapped_lines = wrap_text(full_dialogue_text, response_font, text_area_width)

    # Calculate the total height of the text block
    line_height = SPACING['line_height']
    total_text_height = len(full_dialogue_text) * line_height

    # Calculate the starting Y position to vertically center the text
    start_y = 130 #LAYOUT_DIALOG_Y + (LAYOUT_DIALOG_HEIGHT - total_text_height) // 2

    # Loop through each line and draw it
    for i, line_surface in enumerate(wrapped_lines):
        line_rect = line_surface.get_rect(centerx=text_area_x + (text_area_width // 2))
        line_rect.top = start_y + (i * line_height)
        surface.blit(line_surface, line_rect)


    #add NPC picture on panel on left
    draw_npc_portrait(surface, 'garrick')

    #add party status panel on right
    draw_party_status_panel(surface, game_state, fonts) 

    # Continue button
    continue_button = draw_button(surface, 452, 480, 120, 40, "CONTINUE", 
                                 fonts.get('fantasy_small', fonts['normal']))
    
    return {
        "type": "garrick_response", 
        "continue_button": continue_button
    }

def draw_garrick_fallback_screen(surface, game_state, fonts):
    """Fallback if DialogueEngine is not available"""
    
    surface.fill((0, 0, 0))
    
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render("GARRICK THE BARKEEP", True, (0, 255, 0))
    title_rect = title_text.get_rect(center=(512, 200))
    surface.blit(title_text, title_rect)
    
    message_font = fonts.get('fantasy_small', fonts['normal'])
    message_text = message_font.render("DialogueEngine not available - using simple interface", True, WHITE)
    message_rect = message_text.get_rect(center=(512, 250))
    surface.blit(message_text, message_rect)
    
    # Simple buttons
    shop_button = draw_button(surface, 312, 350, 100, 40, "SHOP", message_font)
    back_button = draw_button(surface, 412, 350, 100, 40, "BACK", message_font)
    
    return {"type": "fallback", "shop_button": shop_button, "back_button": back_button}

def process_garrick_dialogue_choice(choice_index, game_state, controller):
    """Process player's dialogue choice"""
    
    dialogue_engine = controller.data_manager.get_manager('dialogue')
    if not dialogue_engine:
        return None
    
    conversation_data = dialogue_engine.get_conversation_options('tavern_garrick', 'garrick')
    
    if choice_index < len(conversation_data['options']):
        selected_option = conversation_data['options'][choice_index]
        choice_id = selected_option['id']
        
        # Process the choice through DialogueEngine
        result = dialogue_engine.process_dialogue_choice('tavern_garrick', 'garrick', choice_id)
        
        # Set response display state
        game_state.garrick_dialogue_response = result['response']
        game_state.showing_garrick_response = True
        
        # Mark conversation flags
        if not hasattr(game_state, 'garrick_talked') or not game_state.garrick_talked:
            game_state.garrick_talked = True
        
        return result
    
    return None

def draw_meredith_dialogue_screen(surface, game_state, fonts, images, controller=None):
    """
    Server (Meredith) dialogue using standardized DialogueEngine system
    """
   
    # Check for response display state first
    if getattr(game_state, 'showing_meredith_response', False):
        return draw_meredith_response_screen(surface, game_state, fonts)
    
    # Get dialogue engine from controller
    if not controller:
        return draw_meredith_fallback_screen(surface, game_state, fonts)
    
    dialogue_engine = controller.data_manager.get_manager('dialogue')
    if not dialogue_engine:
        return draw_meredith_fallback_screen(surface, game_state, fonts)
    
    # Get current conversation options from DialogueEngine
    conversation_data = dialogue_engine.get_conversation_options('tavern_meredith', 'meredith')
    
    # Use your standardized dialogue UI system
    try:
        from utils.dialogue_ui_utils import draw_standard_dialogue_screen
        result = draw_standard_dialogue_screen(surface, 'meredith', conversation_data, game_state, fonts, controller)
        return result
    except ImportError as e:
        print(f"❌ DEBUG: Failed to import dialogue_ui_utils: {e}")
        return draw_meredith_fallback_screen(surface, game_state, fonts)
    except Exception as e:
        print(f"❌ DEBUG: Error in draw_standard_dialogue_screen: {e}")
        return draw_meredith_fallback_screen(surface, game_state, fonts)
    
def draw_meredith_response_screen(surface, game_state, fonts):
    """Display Meredith's response to player choice"""
    surface.fill((0, 0, 0))
   
    # Display response text
    response_lines = getattr(game_state, 'meredith_dialogue_response', ["Thank you for listening."])
    
   # Use standardized response screen
    from utils.dialogue_ui_utils import draw_standard_response_screen
    return draw_standard_response_screen(surface, 'meredith', response_lines, game_state, fonts)

def draw_meredith_fallback_screen(surface, game_state, fonts):
    """Fallback if DialogueEngine not available"""
    surface.fill((0, 0, 0))
    
    # Draw NPC portrait
    draw_npc_portrait(surface, 'meredith')
    
    lines = [
        "Meredith Whisperwind",
        "",
        "Well hello there, stranger!",
        "I hear all the best gossip working these tables.",
        "Come back when the dialogue system is ready!"
    ]
    
    y_pos = 120
    for line in lines:
        if line:  # Skip empty lines
            line_text = fonts['normal'].render(line, True, WHITE)
            line_rect = line_text.get_rect(center=(512, y_pos))
            surface.blit(line_text, line_rect)
        y_pos += 30
    
    back_button = draw_button(surface, 450, 400, 120, 35, "BACK", fonts['normal'])
    return {"back_button": back_button}

def process_meredith_dialogue_choice(choice_index, game_state, controller):
    """Process player's dialogue choice with Meredith (Server)"""
    
    dialogue_engine = controller.data_manager.get_manager('dialogue')
    if not dialogue_engine:
        return None
    
    conversation_data = dialogue_engine.get_conversation_options('tavern_meredith', 'meredith')
    
    if choice_index < len(conversation_data['options']):
        selected_option = conversation_data['options'][choice_index]
        choice_id = selected_option['id']
        
        # Process the choice through DialogueEngine
        result = dialogue_engine.process_dialogue_choice('tavern_meredith', 'meredith', choice_id)
        
        # Set response display state
        game_state.meredith_dialogue_response = result['response']
        game_state.showing_meredith_response = True
        
        # Mark conversation flags - IMPORTANT for quest progression
        if not hasattr(game_state, 'meredith_talked') or not game_state.meredith_talked:
            game_state.meredith_talked = True
        
        # Special handling for Swamp Church discovery (critical quest trigger)
        if choice_id == 'swamp_church':
            print("🏛️ Player discovered Swamp Church location through Meredith!")
            # The DialogueEngine already handled the location discovery via effects
            # But we can add any additional game state updates here if needed
        
        return result
    
    return None