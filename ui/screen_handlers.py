# ui/screen_handlers.py
"""
Generic Screen Handlers - Replace hardcoded click detection
"""

def handle_broken_blade_clicks(mouse_pos, game_controller, event_manager):
    """Handle broken blade tavern clicks using events"""
    
   #print(f"DEBUG: ScreenHandler: handle_broken_blade_clicks called")
   # print(f"DEBUG: ScreenHandler: game_controller = {game_controller}")
   # print(f"DEBUG: ScreenHandler: event_manager = {event_manager}")
   # print(f"DEBUG: ScreenHandler: event_manager type = {type(event_manager)}")



    # Import the screen drawing function to get button positions
    from screens.broken_blade import draw_broken_blade_main_screen
    import pygame
    
    # Create temporary surface to get button positions
    temp_surface = pygame.Surface((1024, 768))
    
    # Get button positions (this is the current approach)
    bartender_btn, server_btn, patrons_btn, gamble_btn, leave_btn = draw_broken_blade_main_screen(
        temp_surface, game_controller.game_state, game_controller.fonts, 
        game_controller.images, controller=game_controller
    )
    
    # Check clicks and emit appropriate events
    if bartender_btn.collidepoint(mouse_pos):
        #print(f"DEBUG: SH: About to emit NPC_CLICKED event")
        #print(f"DEBUG: SH: Using event_manager: {event_manager}")
        event_manager.emit("NPC_CLICKED", {
            "npc_id": "garrick",
            "location": "broken_blade_tavern"
        })
        return True
        
    elif server_btn.collidepoint(mouse_pos):
        event_manager.emit("NPC_CLICKED", {
            "npc_id": "meredith", 
            "location": "broken_blade_tavern"
        })
        return True
        
    elif patrons_btn.collidepoint(mouse_pos):
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "patron_selection",
            "source_screen": "broken_blade_main"
        })
        return True
        
    elif gamble_btn.collidepoint(mouse_pos):
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "dice_bets",
            "source_screen": "broken_blade_main"
        })
        return True
        
    elif leave_btn.collidepoint(mouse_pos):
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "town_square",
            "source_screen": "broken_blade_main"
        })
        return True
    
    return False  # No click handled

def handle_patron_selection_clicks(mouse_pos, game_controller, event_manager):
    """Handle patron selection clicks using event-driven architecture"""
    
    # Import the screen drawing function to get button positions
    from screens.patron_selection import draw_patron_selection_screen
    import pygame
    
    # Create temporary surface to get button positions (same pattern as broken_blade)
    temp_surface = pygame.Surface((1024, 768))
    
    # Get button positions from screen drawing function
    gareth_btn, elara_btn, thorman_btn, lyra_btn, pete_btn, back_btn = draw_patron_selection_screen(
        temp_surface, game_controller.game_state, game_controller.fonts, 
        game_controller.images, controller=game_controller
    )
    
    # Check clicks and emit appropriate events
    if gareth_btn.collidepoint(mouse_pos):
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "gareth_dialogue",
            "source_screen": "patron_selection"
        })
        return True
        
    elif elara_btn and elara_btn.collidepoint(mouse_pos):  # ADD: elara_btn and
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "elara_dialogue", 
            "source_screen": "patron_selection"
        })
        return True
        
    elif thorman_btn and thorman_btn.collidepoint(mouse_pos):  # ADD: thorman_btn and
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "thorman_dialogue",
            "source_screen": "patron_selection"
        })
        return True
        
    elif lyra_btn and lyra_btn.collidepoint(mouse_pos):  # ADD: lyra_btn and
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "lyra_dialogue",
            "source_screen": "patron_selection"
        })
        return True
        
    elif pete_btn and pete_btn.collidepoint(mouse_pos):  # ADD: pete_btn and
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "pete_dialogue",
            "source_screen": "patron_selection"
        })
        return True
        
    elif back_btn and back_btn.collidepoint(mouse_pos):  # ADD: back_btn and
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "broken_blade_main",
            "source_screen": "patron_selection"
        })
        return True
    
    return False  # No click handled

def handle_main_menu_clicks(mouse_pos, game_controller, event_manager):
    """Handle main menu clicks using events"""
    # We can implement this next
    return False