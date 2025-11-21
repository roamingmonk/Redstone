# ui/screen_handlers.py
"""
Generic Screen Handlers - Replace hardcoded click detection
"""
import pygame
from screens.title_menu import draw_main_menu
from screens.gambling_dice import (draw_dice_bets_screen, draw_dice_rules_screen,
                                     draw_dice_rolling_screen, draw_dice_results_screen,
                                     draw_dice_rules_screen)

def handle_main_menu_clicks(mouse_pos, game_controller, event_manager):
    """Handle main menu clicks using actual button coordinates"""
    
    # Get the real button rectangles from the drawing function
    temp_surface = pygame.Surface((1024, 768))
    new_game_button, load_game_button, quit_button = draw_main_menu(
        temp_surface, game_controller.game_state, game_controller.fonts
    )
    
    # Check which button was clicked
    if new_game_button and new_game_button.collidepoint(mouse_pos):
        event_manager.emit("NEW_GAME", {"target_screen": "stats"})
        return True
    elif load_game_button and load_game_button.collidepoint(mouse_pos):
        event_manager.emit("LOAD_GAME", {})
        return True
    elif quit_button and quit_button.collidepoint(mouse_pos):
        event_manager.emit("QUIT_GAME", {})
        return True
    
    return True  

def handle_title_screen_clicks(mouse_pos, game_controller, event_manager):
    """Handle title screen clicks - advance to developer splash"""
    event_manager.emit("SCREEN_CHANGE", {
        "target_screen": "developer_splash", 
        "source_screen": "game_title"
    })
    return True

def handle_developer_splash_clicks(mouse_pos, game_controller, event_manager):
    """Handle developer splash clicks - advance to main menu"""
    event_manager.emit("SCREEN_CHANGE", {
        "target_screen": "main_menu",
        "source_screen": "developer_splash" 
    })
    return True


# Add these functions to ui/screen_handlers.py (at the end of the file)

def handle_dice_bets_clicks(mouse_pos, game_controller, event_manager):
    """Handle dice betting screen clicks using event-driven architecture"""
    

    
    temp_surface = pygame.Surface((1024, 768))
    bet_5_btn, bet_10_btn, bet_25_btn, rules_btn, back_btn = draw_dice_bets_screen(
        temp_surface, game_controller.game_state, game_controller.fonts, 
        game_controller.images
    )
    
    if bet_5_btn and bet_5_btn.collidepoint(mouse_pos):
        event_manager.emit("DICE_BET_PLACED", {"bet_amount": 5})
        return True
    elif bet_10_btn and bet_10_btn.collidepoint(mouse_pos):
        event_manager.emit("DICE_BET_PLACED", {"bet_amount": 10})
        return True
    elif bet_25_btn and bet_25_btn.collidepoint(mouse_pos):
        event_manager.emit("DICE_BET_PLACED", {"bet_amount": 25})
        return True
    elif rules_btn and rules_btn.collidepoint(mouse_pos):
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "dice_rules", "source_screen": "dice_bets"
        })
        return True
    elif back_btn and back_btn.collidepoint(mouse_pos):
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "broken_blade_nav", "source_screen": "dice_bets"
        })
        return True
    return False

def handle_dice_rolling_clicks(mouse_pos, game_controller, event_manager):
    """Handle dice rolling screen clicks (skip animation or continue)"""
    
    temp_surface = pygame.Surface((1024, 768))
    clickable_area = draw_dice_rolling_screen(
        temp_surface, game_controller.game_state, game_controller.fonts, 
        game_controller.images
    )
    
    if clickable_area and clickable_area.collidepoint(mouse_pos):
        current_time = pygame.time.get_ticks()
        # Access gambling stats through new structure
        gambling_stats = game_controller.game_state.character.get('gambling_stats', {})
        roll_start_time = gambling_stats.get('roll_start_time', 0)
        is_rolling = (current_time - roll_start_time) < 2000
        
        if is_rolling:
            event_manager.emit("DICE_SKIP_ANIMATION", {})
        else:
            event_manager.emit("SCREEN_CHANGE", {
                "target_screen": "dice_results", "source_screen": "dice_rolling"
            })
        return True
    return False

def handle_dice_results_clicks(mouse_pos, game_controller, event_manager):
    """Handle dice results screen clicks (play again or quit)"""    
    temp_surface = pygame.Surface((1024, 768))
    buttons = draw_dice_results_screen(
        temp_surface, game_controller.game_state, game_controller.fonts, 
        game_controller.images
    )
    
    if isinstance(buttons, tuple) and len(buttons) == 2:
        play_again_btn, quit_btn = buttons
        if play_again_btn and play_again_btn.collidepoint(mouse_pos):
            event_manager.emit("SCREEN_CHANGE", {
                "target_screen": "dice_bets", "source_screen": "dice_results"
            })
            return True
        elif quit_btn and quit_btn.collidepoint(mouse_pos):
            event_manager.emit("SCREEN_CHANGE", {
                "target_screen": "broken_blade_nav", "source_screen": "dice_results"
            })
            return True
    elif buttons and buttons.collidepoint(mouse_pos):  # Single quit button
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "broken_blade_nav", "source_screen": "dice_results"
        })
        return True
    return False

def handle_dice_rules_clicks(mouse_pos, game_controller, event_manager):
    """Handle dice rules screen clicks (back button)"""    
    temp_surface = pygame.Surface((1024, 768))
    back_btn = draw_dice_rules_screen(
        temp_surface, game_controller.game_state, game_controller.fonts, 
        game_controller.images
    )
    
    if back_btn and back_btn.collidepoint(mouse_pos):
        event_manager.emit("SCREEN_CHANGE", {
            "target_screen": "dice_bets", "source_screen": "dice_rules"
        })
        return True
    return False