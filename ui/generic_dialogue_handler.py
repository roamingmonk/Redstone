# ui/generic_dialogue_handler.py
"""
Generic Dialogue System - The Holy Grail Implementation
Creates a single, reusable dialogue system that works for ANY NPC

GOAL: Adding new NPC dialogue = Create 1 JSON file, nothing else.

This replaces:
- draw_garrick_dialogue_screen()
- draw_meredith_dialogue_screen() 
- draw_[any_npc]_dialogue_screen()

With:
- draw_generic_dialogue_screen(npc_id, ...)

The NPC ID determines which JSON file to load and which portrait to display.
No more hardcoded NPC-specific functions!
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button
from utils.npc_display import draw_npc_portrait
from utils.party_display import draw_party_status_panel
from utils.dialogue_ui_utils import draw_standard_dialogue_screen, draw_standard_response_screen

def draw_generic_dialogue_screen(surface, npc_id, game_state, fonts, images, controller=None, location_id=None):
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
    
    #print(f"DEBUG: GDH: draw_generic_dialogue_screen called for {npc_id} at location {location_id}")
    
    try: 
        # CRITICAL: Validate location_id is provided - no hardcoding allowed
        if not location_id:
            raise ValueError(f"location_id is REQUIRED for dialogue with {npc_id} - no hardcoded defaults allowed")
        
        # CRITICAL: Store location for dialogue session - this enables the event system to work
        location_attr = f'{npc_id}_current_location'
        setattr(game_state, location_attr, location_id)
        #print(f"✅ DEBUG: Set {location_attr} = {location_id}")
        
        # CRITICAL: Set dialogue in progress flag
        progress_flag = f'{npc_id}_dialogue_in_progress'
        setattr(game_state, progress_flag, True)
        #print(f"DEBUG: Set {progress_flag} = True")

        # Check for response display state first
        response_attr = f'showing_{npc_id}_response'
        if getattr(game_state, response_attr, False):
            #print(f"DEBUG: GDH: Showing response for {npc_id}")
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
        #print(f"DEBUG: GDH: Getting conversation options for {dialogue_file_id}")
        
        # Get current conversation options from DialogueEngine
        conversation_data = dialogue_engine.get_conversation_options(dialogue_file_id, npc_id)
        #print(f"DEBUG: GDH: conversation_data = {conversation_data}")
        
    except Exception as e:
        print(f"ERROR in draw_generic_dialogue_screen: {e}")
        import traceback
        traceback.print_exc()
        return draw_generic_fallback_screen(surface, npc_id, game_state, fonts)

    # Use standardized dialogue UI system
    try:
        result = draw_standard_dialogue_screen(surface, npc_id, conversation_data, game_state, fonts, controller)
        #print(f"DEBUG: GDH: draw_standard_dialogue_screen result type: {result.get('type')}")
        return result
    except Exception as e:
        print(f"DEBUG: GDH: Exception in draw_standard_dialogue_screen: {e}")
        import traceback
        traceback.print_exc()
        return draw_generic_fallback_screen(surface, npc_id, game_state, fonts)

def draw_generic_response_screen(surface, npc_id, game_state, fonts, location_id=None):
    """Universal NPC response screen - works for ANY NPC"""
    surface.fill((0, 0, 0))
    
    # Get location from stored value if not passed (for consistency)
    if not location_id:
        location_id = getattr(game_state, f'{npc_id}_current_location', None)
        if not location_id:
            print(f"WARNING: No location available for {npc_id} response screen")
            # Don't fail here since response is already stored, just log warning
    
    # Get response text from game state automatically
    response_attr = f'{npc_id}_dialogue_response'
    response_lines = getattr(game_state, response_attr, ["Thank you for listening."])
    
    # Use standardized response screen
    return draw_standard_response_screen(surface, npc_id, response_lines, game_state, fonts)

def draw_generic_fallback_screen(surface, npc_id, game_state, fonts):
    """Universal fallback screen if DialogueEngine not available"""
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
    3. Sets response state using npc_id naming convention
    """
    
    dialogue_engine = controller.dialogue_engine
    if not dialogue_engine:
        return None
    
    # Retrieve stored location - REQUIRED
    location_id = getattr(game_state, f'{npc_id}_current_location')
    if not location_id:
        raise ValueError(f"No location stored for {npc_id} dialogue session")

    # Automatically determine dialogue file based on NPC ID  
    dialogue_file_id = f'{location_id}_{npc_id}'
    
    conversation_data = dialogue_engine.get_conversation_options(dialogue_file_id, npc_id)
    
    if choice_index < len(conversation_data['options']):
        selected_option = conversation_data['options'][choice_index]
        choice_id = selected_option['id']
        
        #print(f"DEBUG: GDH: Available options from engine: {[opt.get('id') for opt in conversation_data['options']]}")
        #print(f"DEBUG: GDH: Selected choice_id: {choice_id}")
        #print(f"DEBUG: GDH: Conversation data keys: {conversation_data.keys()}")

        # Process the choice through DialogueEngine
        result = dialogue_engine.process_dialogue_choice(dialogue_file_id, npc_id, choice_id)

        # Normal response handling
        response_attr = f'{npc_id}_dialogue_response'
        showing_attr = f'showing_{npc_id}_response'
        actions_attr = f'{npc_id}_dialogue_response_actions'

        setattr(game_state, response_attr, result['response'])
        setattr(game_state, showing_attr, True)
        setattr(game_state, actions_attr, result.get('actions_available', []))
        if choice_index < len(conversation_data['options']):
            selected_option = conversation_data['options'][choice_index]
            response_actions = selected_option.get('actions', [])
            setattr(game_state, actions_attr, response_actions)

        # Mark conversation flags using standardized naming
        talked_attr = f'{npc_id}_talked'
        if not getattr(game_state, talked_attr, False):
            setattr(game_state, talked_attr, True)
        
        print(f"Processed {npc_id} dialogue choice: {choice_id}")
        return result
    
    return None

def process_response_action(npc_id, action_name, game_state, controller, location_id=None):
    """Process action button clicks from response screens"""
    print(f"DEBUG: process_response_action: {npc_id}, {action_name}")
    
    if not controller or not controller.dialogue_engine:
        return None
    
    dialogue_file_id = f'{location_id}_{npc_id}'
    dialogue_engine = controller.dialogue_engine
    
    # Get the action definition from the dialogue file
    dialogue_data = dialogue_engine.dialogues.get(dialogue_file_id, {})
    actions_config = dialogue_data.get('actions', {})
    action_def = actions_config.get(action_name, {})
    
    # If action_def is empty, these are likely terminal response actions
    if not action_def:
        #print(f"DEBUG: PRA: Terminal action '{action_name}' - ending dialogue gracefully")
        # Clear response state and exit to main tavern
        setattr(game_state, f'showing_{npc_id}_response', False)
        setattr(game_state, f'{npc_id}_dialogue_response', [])
        return "back"  # Return to broken_blade_main instead of looping
    
    action_type = action_def.get('type', 'button')
    #print(f"DEBUG: Action {action_name} has type: {action_type}")
    
    if action_type == 'dialogue_branch':
        # Handle dialogue branching
        target_state = action_def.get('target_state')
        target_option = action_def.get('target_option')
        
        if target_state:
            #print(f"DEBUG: Branching to state: {target_state}")
            
            # Set the new dialogue state
            state_attr = f'{npc_id}_dialogue_state'
            setattr(game_state, state_attr, target_state)
            
            # Clear current response state
            response_attr = f'{npc_id}_dialogue_response'
            showing_attr = f'showing_{npc_id}_response'
            setattr(game_state, showing_attr, False)
            setattr(game_state, response_attr, [])
            
            # If target_option specified, process it automatically
            if target_option:
                #print(f"DEBUG: Auto-processing target_option: {target_option}")
                result = dialogue_engine.process_dialogue_choice(dialogue_file_id, npc_id, target_option)
                
                # Set the response for the branched choice
                setattr(game_state, response_attr, result['response'])
                setattr(game_state, f'{npc_id}_dialogue_response_actions', result.get('actions_available', []))
                setattr(game_state, showing_attr, True)
                
            return True
    
    elif action_type == 'quest_update':
        # Handle quest progression
        quest_id = action_def.get('quest_id')
        step = action_def.get('step')
        print(f"DEBUG: Quest update - {quest_id}: {step}")
        
        # Set quest flag in game state
        if quest_id and step:
            setattr(game_state, f'quest_{quest_id}_{step}', True)
        
        # Clear response state and continue dialogue
        setattr(game_state, f'showing_{npc_id}_response', False)
        setattr(game_state, f'{npc_id}_dialogue_response', [])
        return True
        
    elif action_type == 'recruit_npc':
        # Handle NPC recruitment  
        npc_id_to_recruit = action_def.get('npc_id')
        print(f"DEBUG: Recruiting NPC: {npc_id_to_recruit}")
        
        # Add to party
        if not hasattr(game_state, 'party_members'):
            game_state.party_members = []
        if npc_id_to_recruit and npc_id_to_recruit not in game_state.party_members:
            game_state.party_members.append(npc_id_to_recruit)
        
        # Clear response state and continue dialogue
        setattr(game_state, f'showing_{npc_id}_response', False)
        setattr(game_state, f'{npc_id}_dialogue_response', [])
        return True        
  
    elif action_type == 'merchant':
        # Clear response state and go to shop
        setattr(game_state, f'showing_{npc_id}_response', False)
        setattr(game_state, f'{npc_id}_dialogue_response', [])
        return "shop"
        
    elif action_type == 'exit':
        # Clear response state and exit dialogue
        setattr(game_state, f'showing_{npc_id}_response', False)
        setattr(game_state, f'{npc_id}_dialogue_response', [])
        return "back"
    else:
        print(f"DEBUG: PRA: Unknown action_type '{action_type}' for action '{action_name}'")
        print(f"DEBUG: PRA: action_def = {action_def}")
        print(f"DEBUG: PRA: Available action_def keys: {list(action_def.keys())}")
    return None


# ==========================================
# SCREEN INTEGRATION FUNCTIONS
# ==========================================

def register_npc_dialogue_screen(screen_manager, npc_id):
    """
    Register a dialogue screen for any NPC automatically
    
    Args:
        screen_manager: The ScreenManager instance
        npc_id: NPC identifier (e.g., 'garrick', 'meredith', 'town_guard')
        
    This creates screen registration for:
    - Screen name: f"{npc_id}_dialogue"
    - Handler: generic_dialogue_click_handler with npc_id parameter
    """
    
    screen_name = f"{npc_id}_dialogue"
    
    def npc_click_handler(mouse_pos, game_controller, event_manager):
        """Generic click handler for any NPC dialogue screen"""
        
        # Check if we're showing a response first
        showing_attr = f'showing_{npc_id}_response'
        if getattr(game_controller.game_state, showing_attr, False):
            
            # Create temporary surface to get button positions (same pattern as current)
            temp_surface = pygame.Surface((1024, 768))
            response_attr = f'{npc_id}_dialogue_response'
            response_lines = getattr(game_controller.game_state, response_attr, [])
            result = draw_standard_response_screen(temp_surface, npc_id, response_lines, 
                                                game_controller.game_state, game_controller.fonts, 
                                                game_controller)
            
            # Handle action buttons from response screen
            #print(f"DEBUG: Response screen result: {result}")
            #print(f"DEBUG: Action rects: {result.get('action_rects', {})}")
            
            # CRITICAL FIX: Handle ALL action buttons from response screen
            if result.get("action_rects"):
                for action_name, action_rect in result["action_rects"].items():
                    if action_rect.collidepoint(mouse_pos):
                        #print(f"DEBUG: Response action clicked: {action_name}")
                        
                        # Process the action through dialogue engine
                        if action_name == "continue":
                            # Clear response state and return to dialogue
                            setattr(game_controller.game_state, showing_attr, False)
                            setattr(game_controller.game_state, response_attr, [])
                            return True
                            
                        else:
                            # Handle dialogue branch actions
                            result = process_response_action(npc_id, action_name, 
                                                        game_controller.game_state, 
                                                        game_controller)
                            
                            if result == "shop":
                                event_manager.emit("SCREEN_CHANGE", {
                                    "target_screen": "merchant_shop",
                                    "source_screen": f"{npc_id}_dialogue"
                                })
                            elif result == "back":
                                # Use event manager to track where we came from
                                # The screen manager should track the previous screen
                                if hasattr(game_controller, 'screen_manager') and hasattr(game_controller.screen_manager, 'previous_screen'):
                                    target_screen = game_controller.screen_manager.previous_screen
                                else:
                                    target_screen = "patron_selection"  # Sensible default
                                    
                                event_manager.emit("SCREEN_CHANGE", {
                                    "target_screen": target_screen,
                                    "source_screen": f"{npc_id}_dialogue"
                                })
                            elif result:
                                # Stay in dialogue - action processed successfully
                                pass
                                
                            return True
        
        # Normal dialogue handling
        temp_surface = pygame.Surface((1024, 768))
        result = draw_generic_dialogue_screen(temp_surface, npc_id, game_controller.game_state, 
                                            game_controller.fonts, game_controller.images, controller=game_controller)
        print(f"DEBUG: Dialogue result type: {result.get('type')}")
        print(f"DEBUG: Has back_button: {result.get('back_button') is not None}")


        if result.get("type") == "standard_dialogue":
            print(f"DEBUG: Processing standard dialogue")
            # Handle dialogue option clicks
            for i, option_rect in enumerate(result.get("option_rects", [])):
                if option_rect.collidepoint(mouse_pos):
                    process_generic_dialogue_choice(npc_id, i, game_controller.game_state, game_controller)
                    return True
            
            # Handle back button (check both possible locations)
            back_button = result.get("back_button") or result.get("action_rects", {}).get("back")
            if back_button and back_button.collidepoint(mouse_pos):
                print(f"DEBUG: Back button clicked for {npc_id}")
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": "patron_selection",
                    "source_screen": f"{npc_id}_dialogue"
                })
                return True
                
            # Handle any action buttons (shop, etc.)
            for action_name, action_rect in result.get("action_rects", {}).items():
                if action_rect.collidepoint(mouse_pos):
                    if action_name == "shop":
                        event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": f"{npc_id}_shop",
                            "source_screen": f"{npc_id}_dialogue"
                        })
                    elif action_name == "goodbye":
                        event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": "broken_blade_main", 
                            "source_screen": f"{npc_id}_dialogue"
                        })
                    return True

        else:
            print(f"DEBUG: Non-standard dialogue type, checking for back button anyway")
            # Add fallback back button handling here:
            if result.get("back_button") and result["back_button"].collidepoint(mouse_pos):
                print(f"DEBUG: Back button clicked in non-standard dialogue")
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": "patron_selection",
                    "source_screen": f"{npc_id}_dialogue"
                })
                return True 

       
        return False
    
    # Register the screen with the generic handler
    screen_manager.register_screen(screen_name, npc_click_handler)
    print(f"Registered generic dialogue screen: {screen_name}")

def register_dialogue_clickables(screen_name, npc_id, game_state, fonts, controller):
    """Register dialogue screen clickable areas following BaseLocation pattern"""
    print(f"🎭 REGISTRATION: GDH: register_dialogue_clickables called for {screen_name}, npc: {npc_id}")
    
    # Check response state immediately
    showing_response_attr = f'showing_{npc_id}_response'
    is_showing_response = getattr(game_state, showing_response_attr, False)
    print(f"🎭 REGISTRATION: GDH: is_showing_response = {is_showing_response}")
    
    
    print(f"DEBUG: GDH: register_dialogue_clickables called for screen: {screen_name}, npc: {npc_id}")
    
    if not controller or not hasattr(controller, 'screen_manager'):
        return
    
    screen_manager = controller.screen_manager
    if not hasattr(screen_manager, 'input_handler') or not screen_manager.input_handler:
        return
    
    input_handler = screen_manager.input_handler
    input_handler.clear_clickables(screen_name)
    
    # Create temp surface to get button positions (BaseLocation pattern)
    temp_surface = pygame.Surface((1024, 768))
    
    # Get dialogue data and render to find button positions
    dialogue_engine = controller.event_manager.get_service('dialogue_engine')
    if dialogue_engine:
        location_id = getattr(game_state, f'{npc_id}_current_location', 'broken_blade')
        dialogue_file_id = f'{location_id}_{npc_id}'
        conversation_data = dialogue_engine.get_conversation_options(dialogue_file_id, npc_id)
        
        result = draw_standard_dialogue_screen(temp_surface, npc_id, conversation_data, 
                                             game_state, fonts, controller)
        
        # Register dialogue option clicks
        for i, option_rect in enumerate(result.get('option_rects', [])):
            input_handler.register_clickable(
                screen_name, option_rect, 'DIALOGUE_CHOICE', 
                {'npc_id': npc_id, 'choice_index': i}
            )
        
        # Register action button clicks  
        for action_name, action_rect in result.get('action_rects', {}).items():
            input_handler.register_clickable(
                screen_name, action_rect, 'DIALOGUE_ACTION',
                {'npc_id': npc_id, 'action_name': action_name}
            )
        
            # Register dialogue option clicks
        for i, option_rect in enumerate(result.get('option_rects', [])):
            input_handler.register_clickable(
                screen_name, option_rect, 'DIALOGUE_CHOICE', 
                {'npc_id': npc_id, 'choice_index': i}
            )
        
        # Register action button clicks  
        for action_name, action_rect in result.get('action_rects', {}).items():
            input_handler.register_clickable(
                screen_name, action_rect, 'DIALOGUE_ACTION',
                {'npc_id': npc_id, 'action_name': action_name}
            )
        
        registered_count = len(result.get('option_rects', [])) + len(result.get('action_rects', {}))
        print(f"🎭 Unified screen clickables registered for {screen_name}: {registered_count} buttons")
# ==========================================
# GAME CONTROLLER INTEGRATION
# ==========================================

def setup_generic_dialogue_system(game_controller):
    """
    Set up the complete generic dialogue system
    Call this once during GameController initialization
    
    This automatically:
    1. Registers all existing NPC dialogue screens
    2. Sets up event handlers for dialogue management
    3. Enables "create JSON file only" workflow for new NPCs
    """
    
    # List of all NPCs that need dialogue screens
    # To add new NPC: just add their ID to this list!
    npc_list = ['garrick', 'meredith', 'gareth', 'elara', 'thorman']
    
    for npc_id in npc_list:
        register_npc_dialogue_screen(game_controller.screen_manager, npc_id)
    
    print(f"Generic dialogue system ready for {len(npc_list)} NPCs")
    print("To add new NPC: Create data/dialogues/tavern_[npc_id].json file only!")


# ==========================================
# DEVELOPMENT UTILITIES  
# ==========================================

def validate_npc_dialogue_setup(npc_id, game_controller):
    """
    Validate that an NPC dialogue system is properly set up
    Useful for debugging new NPC additions
    """
    
    issues = []
    
    # Check if dialogue file exists
    import os
    dialogue_file = f'data/dialogues/tavern_{npc_id}.json'
    if not os.path.exists(dialogue_file):
        issues.append(f"Missing dialogue file: {dialogue_file}")
    
    # Check if portrait exists
    portrait_file = f'assets/images/npc_portraits/{npc_id}.jpg'
    if not os.path.exists(portrait_file):
        issues.append(f"Missing portrait: {portrait_file} (will use fallback)")
    
    # Check if screen is registered
    screen_name = f"{npc_id}_dialogue"
    if screen_name not in game_controller.screen_manager.get_registered_screens():
        issues.append(f"Screen not registered: {screen_name}")
    
    # Check if game state attributes exist
    required_attrs = [f'{npc_id}_talked', f'{npc_id}_dialogue_response', f'showing_{npc_id}_response']
    for attr in required_attrs:
        if not hasattr(game_controller.game_state, attr):
            issues.append(f"Missing game state attribute: {attr}")
    
    if issues:
        print(f"NPC {npc_id} setup issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"NPC {npc_id} dialogue system: READY")
    
    return len(issues) == 0


class DialogueStateHandler:
    """
    Handles dialogue response state input routing
    This replaces the manual re-registration approach
    """
    
    def __init__(self, npc_id, game_state, fonts, controller):
        self.handler_id = f"dialogue_response_{npc_id}"
        self.npc_id = npc_id
        self.game_state = game_state
        self.fonts = fonts
        self.controller = controller
        
    def handle_mouse_click(self, mouse_pos):
        """Handle clicks when in dialogue response state"""
        print(f"🎭 DEBUG: DialogueStateHandler processing click for {self.npc_id}")
        
        # Check if we're actually in response state
        response_attr = f'showing_{self.npc_id}_response'
        if not getattr(self.game_state, response_attr, False):
            print(f"🎭 DEBUG: Not in response state for {self.npc_id}")
            return False
            
        # Get response data
        response_data_attr = f'{self.npc_id}_dialogue_response'
        response_lines = getattr(self.game_state, response_data_attr, [])
        
        # Create temp surface to get button positions
        temp_surface = pygame.Surface((1024, 768))
        from utils.dialogue_ui_utils import draw_standard_response_screen
        
        result = draw_standard_response_screen(temp_surface, self.npc_id, response_lines, 
                                             self.game_state, self.fonts, self.controller)
        
        # Check action buttons
        for action_name, action_rect in result.get('action_rects', {}).items():
            if action_rect.collidepoint(mouse_pos):
                print(f"🎭 DEBUG: Response action clicked: {action_name}")
                
                # Emit the dialogue action event
                self.controller.event_manager.emit_event('DIALOGUE_ACTION', {
                    'npc_id': self.npc_id,
                    'action_name': action_name
                })
                return True
                
        print(f"🎭 DEBUG: No response action clicked")
        return False

if __name__ == "__main__":
    print("Generic Dialogue System - Professional NPC Management")
    print("=" * 60)
    print("GOAL: Adding new NPC dialogue = Create 1 JSON file only!")
    print("")
    print("Features:")
    print("- Automatic dialogue file loading based on NPC ID")
    print("- Automatic portrait display based on NPC ID") 
    print("- Automatic game state management based on NPC ID")
    print("- Generic click handling for all NPCs")
    print("- Standardized response system")
    print("")
    print("To add new NPC named 'elena':")
    print("1. Create data/dialogues/tavern_elena.json")
    print("2. Add 'elena' to npc_list in setup_generic_dialogue_system()")
    print("3. Done!")
    print("")
    print("No code changes required for new NPCs!")