"""
Terror in Redstone - Main Game File
The clean, modular entry point for the entire game
"""

import pygame
import sys
sys.path.append('.')

# Import our modular components
from screens.character_creation import finalize_character_creation
from game_state import GameState
from utils.constants import load_fonts, load_images, SCREEN_WIDTH, SCREEN_HEIGHT
from screens.character_creation import (
    draw_splash_screen, draw_stats_screen, draw_gender_screen,
    draw_name_screen, draw_custom_name_screen, draw_name_confirm_screen,
    draw_gold_screen, draw_trinket_screen, draw_summary_screen,
    draw_welcome_screen, draw_portrait_selection_screen
)
from screens.title_menu import draw_title_screen, draw_company_splash_screen, draw_main_menu
from screens.tavern import (
    draw_tavern_main_screen, draw_npc_selection_screen,
    draw_npc_conversation_screen
)
from screens.shopping import draw_merchant_screen

from screens.inventory import draw_inventory_screen
from screens.quest_log import draw_quest_log_screen
from screens.character_sheet import draw_character_sheet_screen
from screens.help_screen import draw_help_screen, handle_help_screen_click

from game_logic.commerce_engine import get_commerce_engine
from screens.gambling_dice import (
    draw_dice_bet_screen, draw_dice_rolling_screen,
    draw_dice_results_screen, 
    draw_dice_rules_screen
)
from core.game_controller import GameController, ScreenRegistry, GameConfig

def initialize_game():
    """Initialize pygame and set up the game window"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Terror in Redstone")
    clock = pygame.time.Clock()
    
    # Load all fonts and images
    fonts = load_fonts()
    images = load_images()
    
    return screen, clock, fonts, images

def handle_keyboard_events(event, game_state):
    """Handle keyboard input for different screens"""
    # CRITICAL: Skip universal input when in text input mode
    if game_state.screen == "custom_name" and game_state.custom_name_active:
        # Handle text input directly, bypass universal hotkeys
        if event.key == pygame.K_RETURN:
            if game_state.custom_name_text.strip():
                game_state.selected_name = game_state.custom_name_text.strip()
                game_state.screen = "name_confirm"
        elif event.key == pygame.K_BACKSPACE:
            game_state.custom_name_text = game_state.custom_name_text[:-1]
        else:
            # Add character if it's printable and not too long
            if len(game_state.custom_name_text) < 30 and event.unicode.isprintable():
                game_state.custom_name_text += event.unicode
        return True  # Text input handled, skip everything else
    
    
    # NEW: Let GameController handle universal input first
    if hasattr(handle_keyboard_events, 'controller'):
        if handle_keyboard_events.controller.handle_universal_input(event):
            return True  # Event was consumed by controller
   
    # GAME TITLE - Enter to start
    if event.key == pygame.K_RETURN and game_state.screen == "game_title":
        if hasattr(handle_keyboard_events, 'controller'):
            handle_keyboard_events.controller.transition_to("developer_splash")
            game_state.screen = "developer_splash"

    # DEVELOPER SPLASH - any key to continue  
    elif game_state.screen == "developer_splash":
        if hasattr(handle_keyboard_events, 'controller'):
            handle_keyboard_events.controller.transition_to("main_menu")
            game_state.screen = "main_menu"
    
    # Custom name input handling
    elif game_state.screen == "custom_name" and game_state.custom_name_active:
        if event.key == pygame.K_RETURN:
            if game_state.custom_name_text.strip():
                game_state.selected_name = game_state.custom_name_text.strip()
                game_state.screen = "name_confirm"
        elif event.key == pygame.K_BACKSPACE:
            game_state.custom_name_text = game_state.custom_name_text[:-1]
        else:
            # Add character if it's printable and not too long
            if len(game_state.custom_name_text) < 30 and event.unicode.isprintable():
                game_state.custom_name_text += event.unicode
    
    return True  # Continue running

def handle_mouse_events(mouse_pos, game_state, fonts, images, controller=None):
    """Handle mouse clicks for different screens"""
# Character sheet screen handling (check FIRST - it's an overlay)
    if game_state.character_sheet_open:
        temp_surface = pygame.Surface((1024, 768))
        result = draw_character_sheet_screen(temp_surface, game_state, fonts, images)
        
        if result:
            return_rect = result
            
            if return_rect and return_rect.collidepoint(mouse_pos):
                game_state.character_sheet_open = False
        
        return True  # Don't process other clicks when character sheet is open

# Help screen handling (check FIRST - it's an overlay)
    if game_state.help_screen_open:
        temp_surface = pygame.Surface((1024, 768))
        result = draw_help_screen(temp_surface, game_state, fonts, images)
        
        if result:
            return_rect = result
            
            if return_rect and return_rect.collidepoint(mouse_pos):
                game_state.help_screen_open = False
        
        return True  # Don't process other clicks when help is open - toggles with H key only


# Quest log screen handling (check FIRST - it's an overlay)
    if game_state.quest_log_open:
        temp_surface = pygame.Surface((1024, 768))
        result = draw_quest_log_screen(temp_surface, game_state, fonts, images)
        
        if result and len(result) == 2:
            quest_rects, return_rect = result
            
            # Handle quest selection clicks
            for i, quest_rect in enumerate(quest_rects):
                if quest_rect.collidepoint(mouse_pos):
                    # Get the quest ID from the available quests
                    from screens.quest_log import get_available_quests
                    quests = get_available_quests(game_state)
                    if i < len(quests):
                        selected_quest_id = quests[i]['id']
                        # Toggle selection
                        if game_state.selected_quest == selected_quest_id:
                            game_state.selected_quest = None
                        else:
                            game_state.selected_quest = selected_quest_id
                    break
            
            # Handle return button click
            if return_rect and return_rect.collidepoint(mouse_pos):
                game_state.quest_log_open = False
                game_state.selected_quest = None
        
        return True  # Don't process other clicks when quest log is open

   
    # Inventory screen handling (check FIRST - it's an overlay)
    if game_state.inventory_open:
        temp_surface = pygame.Surface((1024, 768))
        result = draw_inventory_screen(temp_surface, game_state, fonts, images)
        
        

        if result and len(result) == 4:
            tab_rects, button_rects, item_rects, item_names_in_order = result
            weapons_tab, armor_tab, items_tab, consumables_tab = tab_rects
            
            # Handle tab clicks
            if weapons_tab.collidepoint(mouse_pos):
                game_state.inventory_tab = "weapons"
                game_state.inventory_selected = None
            elif armor_tab.collidepoint(mouse_pos):
                game_state.inventory_tab = "armor"
                game_state.inventory_selected = None
            elif items_tab.collidepoint(mouse_pos):
                game_state.inventory_tab = "items"
                game_state.inventory_selected = None
            elif consumables_tab.collidepoint(mouse_pos):
                game_state.inventory_tab = "consumables"
                game_state.inventory_selected = None
            
            # Handle item selection clicks
            else:
                for i, item_rect in enumerate(item_rects):
                    if item_rect.collidepoint(mouse_pos):
                        if i < len(item_names_in_order):
                            selected_item = item_names_in_order[i]
                            # Toggle selection
                            if game_state.inventory_selected == selected_item:
                                game_state.inventory_selected = None
                            else:
                                game_state.inventory_selected = selected_item
                            break

            # Handle button clicks
            if game_state.inventory_tab in ["weapons", "armor"]:
                equip_btn, unequip_btn, discard_btn, return_btn = button_rects
                
                if return_btn and return_btn.collidepoint(mouse_pos):
                    game_state.inventory_open = False
                elif equip_btn and equip_btn.collidepoint(mouse_pos):
                    if game_state.inventory_selected:
                        game_state.equip_item(game_state.inventory_selected, game_state.inventory_tab)
                        game_state.inventory_selected = None  # Clear selection after equipping
                elif unequip_btn and unequip_btn.collidepoint(mouse_pos):
                    if game_state.inventory_selected:
                        game_state.unequip_item(game_state.inventory_selected)
                        game_state.inventory_selected = None  # Clear selection after unequipping
                elif discard_btn and discard_btn.collidepoint(mouse_pos):
                    if game_state.inventory_selected:
                        game_state.discard_item(game_state.inventory_selected)
                        game_state.inventory_selected = None
                        return True # exit immediately after discard to prevent invalid button usage.
                    
            elif game_state.inventory_tab == "consumables":
                consume_btn, discard_btn, return_btn, _ = button_rects
                
                if return_btn and return_btn.collidepoint(mouse_pos):
                    game_state.inventory_open = False
                elif consume_btn and consume_btn.collidepoint(mouse_pos):
                    if game_state.inventory_selected:
                        game_state.consume_item(game_state.inventory_selected)
                        game_state.inventory_selected = None
                elif discard_btn and discard_btn.collidepoint(mouse_pos):
                    if game_state.inventory_selected:
                        game_state.discard_item(game_state.inventory_selected)
                        game_state.inventory_selected = None
                        return True

            else:  # items tab
                discard_btn, return_btn, _, _ = button_rects
                
                if return_btn and return_btn.collidepoint(mouse_pos):
                    game_state.inventory_open = False
                elif discard_btn and discard_btn.collidepoint(mouse_pos):
                    if game_state.inventory_selected:
                        game_state.discard_item(game_state.inventory_selected)
                        game_state.inventory_selected = None
        
                    
        return True  # Don't process other clicks when inventory is open

    # Load screen handling (check FIRST - it's an overlay)
    if game_state.load_screen_open:
        from screens.load_game import draw_load_game_screen, handle_load_game_click
        temp_surface = pygame.Surface((1024, 768))
        result = draw_load_game_screen(temp_surface, game_state, fonts, images, controller)
        handle_load_game_click(mouse_pos, game_state, result, controller)
        return True

    # Save screen handling (check SECOND - it's an overlay)
    if game_state.save_screen_open:
        from screens.save_game import draw_save_game_screen, handle_save_game_click
        temp_surface = pygame.Surface((1024, 768))
        result = draw_save_game_screen(temp_surface, game_state, fonts, images, controller)
        handle_save_game_click(mouse_pos, game_state, result, controller)
        return True

    
    # GAME TITLE - click to go to developer splash
    if game_state.screen == "game_title":
        if controller:
            controller.transition_to("developer_splash")
        game_state.screen = "developer_splash"
        return True

    # DEVELOPER SPLASH - click to go to main menu
    elif game_state.screen == "developer_splash":
        if controller:
            controller.transition_to("main_menu")
        game_state.screen = "main_menu"
        return True
    
   
    # Main menu
    elif game_state.screen == "main_menu":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        new_game_btn, load_game_btn, quit_btn = draw_main_menu(temp_surface, game_state, fonts, images)
        
        if new_game_btn.collidepoint(mouse_pos):
            game_state.activate_character_portrait()
            if controller:
                controller.transition_to("stats")  # Start character creation
            game_state.screen = "stats"
        elif load_game_btn.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("load_screen")
            game_state.load_screen_open = True  # Open load overlay
        elif quit_btn.collidepoint(mouse_pos):
            return False  # Quit game

    # Stats screen
    elif game_state.screen == "stats":
        # We need to call the draw function to get button positions
        # This is a bit of a hack, but it works for our simple system
        pygame.Surface((1, 1))  # Dummy surface
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        roll_button, keep_button = draw_stats_screen(temp_surface, game_state, fonts, images)
        
        if roll_button.collidepoint(mouse_pos):
            game_state.roll_stats()
        
        if keep_button and keep_button.collidepoint(mouse_pos):
            game_state.character.update(game_state.temp_stats)
            if controller:
                controller.transition_to("gender")
            game_state.screen = "gender"
    
    # Gender screen
    elif game_state.screen == "gender":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        male_button, female_button = draw_gender_screen(temp_surface, game_state, fonts, images)
        
        if male_button.collidepoint(mouse_pos):
            game_state.character['gender'] = 'male'
            game_state.current_names = game_state.get_random_names('male')
            if controller:
                controller.transition_to("portrait_selection")
            game_state.screen = "portrait_selection"
        
        if female_button.collidepoint(mouse_pos):
            game_state.character['gender'] = 'female'
            game_state.current_names = game_state.get_random_names('female')
            if controller:
                controller.transition_to("portrait_selection")
            game_state.screen = "portrait_selection"
    
    # Portrait selection screen
    elif game_state.screen == "portrait_selection":
        import screens.character_creation
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        portrait_buttons, back_button, continue_button = screens.character_creation.draw_portrait_selection_screen(temp_surface, game_state, fonts, images)
        
        # Check portrait selection
        for i, portrait_rect in enumerate(portrait_buttons):
            if portrait_rect.collidepoint(mouse_pos):
                game_state.selected_portrait_index = i
        
        # Back to gender selection
        if back_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("gender")
            game_state.screen = "gender"
        
        # Continue to name (only if portrait selected)
        elif continue_button.collidepoint(mouse_pos):
            if hasattr(game_state, 'selected_portrait_index'):
                # Store selection in game state for save/load persistence
                gender = game_state.character.get('gender', 'male')
                game_state.set_selected_portrait(gender, game_state.selected_portrait_index)
                
                # Ensure active portrait file is current
                game_state.ensure_active_portrait()
                
               # DEBUG: Print to verify this is working
                print(f"DEBUG: Portrait data stored: {game_state.character.get('selected_portrait_file', 'MISSING')}")

                if controller:
                    controller.transition_to("name")
                game_state.screen = "name"

    # Name screen
    elif game_state.screen == "name":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        name_buttons, new_names_button, custom_name_button = draw_name_screen(temp_surface, game_state, fonts, images)
        
        if new_names_button.collidepoint(mouse_pos):
            game_state.current_names = game_state.get_random_names(game_state.character['gender'])
        
        if custom_name_button.collidepoint(mouse_pos):
            game_state.custom_name_text = ""
            game_state.custom_name_active = True
            if controller:
                controller.transition_to("custom_name")
            game_state.screen = "custom_name"
        
        # Check if any name button was clicked
        for i, button in enumerate(name_buttons):
            if button.collidepoint(mouse_pos):
                game_state.selected_name = game_state.current_names[i]
                if controller:
                    controller.transition_to("name_confirm")
                game_state.screen = "name_confirm"
                break
    
    # Custom name screen
    elif game_state.screen == "custom_name":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        input_box_rect, confirm_button, back_button = draw_custom_name_screen(temp_surface, game_state, fonts, images)
        
        if input_box_rect.collidepoint(mouse_pos):
            game_state.custom_name_active = True
        else:
            game_state.custom_name_active = False
        
        if confirm_button and confirm_button.collidepoint(mouse_pos):
            game_state.selected_name = game_state.custom_name_text.strip()
            if controller:
                controller.transition_to("name_confirm")
            game_state.screen = "name_confirm"
        
        if back_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("name")
            game_state.screen = "name"
            game_state.custom_name_active = False
    
    # Name confirmation screen
    elif game_state.screen == "name_confirm":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        confirm_button, back_button = draw_name_confirm_screen(temp_surface, game_state, fonts, images)
        
        if confirm_button.collidepoint(mouse_pos):
            game_state.character['name'] = game_state.selected_name
            if controller:
                    controller.transition_to("gold")
            game_state.screen = "gold"
        
        if back_button.collidepoint(mouse_pos):
            if game_state.custom_name_text:
                if controller:
                    controller.transition_to("custom_name")
                game_state.screen = "custom_name"
            else:
                game_state.screen = "name"
    
    # Gold screen
    elif game_state.screen == "gold":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        roll_button = draw_gold_screen(temp_surface, game_state, fonts, images)
        
        if roll_button.collidepoint(mouse_pos):
            if 'gold' not in game_state.character:
                game_state.character['gold'] = game_state.roll_starting_gold()
            else:
                if controller:
                    controller.transition_to("trinket")
                game_state.screen = "trinket"
    
    # Trinket screen
    elif game_state.screen == "trinket":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        roll_button = draw_trinket_screen(temp_surface, game_state, fonts, images)
        
        if roll_button.collidepoint(mouse_pos):
            if 'trinket' not in game_state.character:
                game_state.character['trinket'] = game_state.get_random_trinket()
            else:
                # Calculate final character stats
                game_state.character['hit_points'] = game_state.calculate_hp()
                if controller:
                    controller.transition_to("summary")
                game_state.screen = "summary"
    
    # Summary screen
    elif game_state.screen == "summary":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        start_button = draw_summary_screen(temp_surface, game_state, fonts, images)
        
        if start_button.collidepoint(mouse_pos):
            #game_state.finalize_character()  # Add trinket to inventory
            if finalize_character_creation(game_state):
                        if controller:
                            controller.transition_to("welcome")
                        game_state.screen = "welcome"
            else:
                print("❌ Character creation failed - staying on summary screen")

            if controller:
                controller.transition_to("welcome")
            game_state.screen = "welcome"
    
    # Welcome screen
    elif game_state.screen == "welcome":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        continue_button = draw_welcome_screen(temp_surface, game_state, fonts, images)
        
        if continue_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("tavern_main")
            game_state.enter_tavern()  # Go to tavern instead of ending
    
    # Tavern main screen
    elif game_state.screen == "tavern_main":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        talk_button, gamble_button, bartender_button, leave_button = draw_tavern_main_screen(temp_surface, game_state, fonts, images)
        
        if talk_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("tavern_npcs")
            game_state.screen = "tavern_npcs"
        elif gamble_button.collidepoint(mouse_pos):
            if controller:
                    controller.transition_to("dice_bets")
            game_state.screen = "dice_bet"
        elif bartender_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("bartender")
            game_state.current_npc = "bartender"
            if controller:
                controller.transition_to("tavern_conversation")
            game_state.screen = "tavern_conversation"
        elif leave_button.collidepoint(mouse_pos):
            print("Leaving tavern - town exploration coming soon!")
    
    
   # NPC selection screen
    elif game_state.screen == "tavern_npcs":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        npc_buttons = draw_npc_selection_screen(temp_surface, game_state, fonts, images)
        
        # Generic click handler - no hardcoded NPC names
        for npc_key, button in npc_buttons.items():
            if button and button.collidepoint(mouse_pos):
                if npc_key == 'back':
                    if controller:
                        controller.transition_to("tavern_main")
                    game_state.screen = "tavern_main"
                else:
                    game_state.current_npc = npc_key
                    if controller:
                        controller.transition_to("tavern_conversation")
                    game_state.screen = "tavern_conversation"
                break
    
    # NEW: Dice game screen handlers
    elif game_state.screen == "dice_bet":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        bet_5_button, bet_10_button, bet_25_button, rules_button, back_button = draw_dice_bet_screen(temp_surface, game_state, fonts, images)
        
        if bet_5_button and bet_5_button.collidepoint(mouse_pos):
            game_state.dice_game['current_bet'] = 5
            game_state.roll_redstone_dice()
            if controller:
                controller.transition_to("dice_rolling")
            game_state.screen = "dice_rolling"
        elif bet_10_button and bet_10_button.collidepoint(mouse_pos):
            game_state.dice_game['current_bet'] = 10
            game_state.roll_redstone_dice()
            if controller:
                controller.transition_to("dice_rolling")
            game_state.screen = "dice_rolling"
        elif bet_25_button and bet_25_button.collidepoint(mouse_pos):
            game_state.dice_game['current_bet'] = 25
            game_state.roll_redstone_dice()
            if controller:
                controller.transition_to("dice_rolling")
            game_state.screen = "dice_rolling"
        elif rules_button and rules_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("dice_rules")
            game_state.screen = "dice_rules"
        elif back_button and back_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("tavern_main")
            game_state.screen = "tavern_main"

    elif game_state.screen == "dice_rolling":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        clickable_area = draw_dice_rolling_screen(temp_surface, game_state, fonts, images)
              
        
        if clickable_area is not None and clickable_area.collidepoint(mouse_pos):
            # Check if we're in animation phase
            current_time = pygame.time.get_ticks()
            roll_start_time = game_state.dice_game.get('roll_start_time', 0)
            if (current_time - roll_start_time) < 2000:  # Still in 2-second animation
                # Skip animation
                game_state.dice_game['animation_skipped'] = True
            else:
                # Animation done - go to results
                bet_amount = game_state.dice_game['current_bet']
                dice = game_state.dice_game['last_roll']
                payout, combination, description, continues = game_state.calculate_dice_payout(bet_amount, dice)
                
                # Store results for display
                game_state.dice_game['last_result'] = {
                    'combination': combination,
                    'payout': payout,
                    'description': description
                }
                
                # Reset animation state for next roll
                game_state.dice_game['animation_skipped'] = False
                if controller:
                    controller.transition_to("dice_results")
                game_state.screen = "dice_results"

    elif game_state.screen == "dice_results":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        play_again_button, quit_button = draw_dice_results_screen(temp_surface, game_state, fonts, images)
        
        if play_again_button and play_again_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("dice_bet")
            game_state.screen = "dice_bet"
        elif quit_button and quit_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("tavern_main")
            game_state.screen = "tavern_main"

    elif game_state.screen == "dice_rules":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        back_button = draw_dice_rules_screen(temp_surface, game_state, fonts, images)
        
        if back_button and back_button.collidepoint(mouse_pos):
            if controller:
                controller.transition_to("dice_bet")
            game_state.screen = "dice_bet"
####NEW commerce pull 
    elif game_state.screen == "merchant_shop":
        # Get the commerce engine to handle all business logic
        commerce = get_commerce_engine()

        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        merchant_data = game_state.get_garrick_inventory()
        merchant_item_rects, buy_button, reset_button, back_button = draw_merchant_screen(temp_surface, game_state, fonts, merchant_data, images)
        
        # Check item clicks (add to cart)
        for i, item_rect in enumerate(merchant_item_rects):
            if item_rect and item_rect.collidepoint(mouse_pos):
                item_name = merchant_data['items'][i]['name']
                commerce.add_to_cart(item_name) # CORRECTED
                break
        
        # Check button clicks
        if buy_button and buy_button.collidepoint(mouse_pos):
            # Use the commerce engine's process_purchase method for the entire transaction
            success, message = commerce.process_purchase() # REFACTORED
            print(message) # The engine provides a user-friendly message

        elif reset_button and reset_button.collidepoint(mouse_pos):
            commerce.clear_cart() # CORRECTED
            
        elif back_button and back_button.collidepoint(mouse_pos):
            commerce.clear_cart() # CORRECTED
            if controller:
                controller.transition_to("tavern_conversation")
            game_state.screen = "tavern_conversation"
####end new commerece pull

    # Individual NPC conversation
    elif game_state.screen == "tavern_conversation":
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        action_button, back_button = draw_npc_conversation_screen(temp_surface, game_state, fonts, images)


        if action_button and action_button.collidepoint(mouse_pos):
            if game_state.current_npc == 'bartender':
                # Go to shop screen
                if controller:
                    controller.transition_to("merchant_shop")
                game_state.screen = "merchant_shop"
            elif game_state.current_npc == 'pete':
                # Pete's comedy sequence
                game_state.pete_showing_comedy = True
            elif not game_state.is_party_full():
                # Normal recruitment
                success = game_state.recruit_npc(game_state.current_npc)
                if success:
                    print(f"Recruited {game_state.current_npc}! Party size: {game_state.get_party_size()}")
                    if controller:
                        controller.transition_to("tavern_npcs")
                    game_state.screen = "tavern_npcs"
                else:
                    print(f"{game_state.current_npc} is already in your party!")
            else:
                print("Your party is full! (Maximum 4 members)")
            
        elif back_button.collidepoint(mouse_pos):
            # Handle Pete's comedy transition
            if game_state.current_npc == 'pete' and hasattr(game_state, 'pete_showing_comedy') and game_state.pete_showing_comedy:
                game_state.pete_attempted_recruitment = True
                game_state.pete_showing_comedy = False
            
            # Only SERVER and BARTENDER should mention the Mayor
            if game_state.current_npc in ['server', 'bartender']:
                game_state.mention_mayor()
            # Route back to appropriate screen
            if game_state.current_npc == 'bartender':
                if controller:
                    controller.transition_to("tavern_main")
                game_state.screen = "tavern_main"
            else:
                if controller:
                    controller.transition_to("tavern_npcs")
                game_state.screen = "tavern_npcs"

    
   
    return True

def draw_current_screen(screen, game_state, fonts, images, controller=None):
    """Draw the appropriate screen based on game state"""
    
    if game_state.screen == "game_title":
        draw_title_screen(screen, game_state, fonts, images)
    elif game_state.screen == "developer_splash":
        draw_company_splash_screen(screen, game_state, fonts, images) 
    elif game_state.screen == "main_menu":
        draw_main_menu(screen, game_state, fonts, images)
    elif game_state.screen == "stats":
        draw_stats_screen(screen, game_state, fonts, images)
    elif game_state.screen == "gender":
        draw_gender_screen(screen, game_state, fonts, images)
    elif game_state.screen == "portrait_selection":
        draw_portrait_selection_screen(screen, game_state, fonts, images)
    elif game_state.screen == "name":
        draw_name_screen(screen, game_state, fonts, images)
    elif game_state.screen == "custom_name":
        draw_custom_name_screen(screen, game_state, fonts, images)
    elif game_state.screen == "name_confirm":
        draw_name_confirm_screen(screen, game_state, fonts, images)
    elif game_state.screen == "gold":
        draw_gold_screen(screen, game_state, fonts, images)
    elif game_state.screen == "trinket":
        draw_trinket_screen(screen, game_state, fonts, images)
    elif game_state.screen == "summary":
        draw_summary_screen(screen, game_state, fonts, images)
    elif game_state.screen == "welcome":
        draw_welcome_screen(screen, game_state, fonts, images)
    elif game_state.screen == "tavern_main":
        draw_tavern_main_screen(screen, game_state, fonts, images)
    elif game_state.screen == "tavern_npcs":
        draw_npc_selection_screen(screen, game_state, fonts, images)
    elif game_state.screen == "tavern_conversation":
        draw_npc_conversation_screen(screen, game_state, fonts, images)
    elif game_state.screen == "dice_bet":
        draw_dice_bet_screen(screen, game_state, fonts, images)
    elif game_state.screen == "dice_rolling":
        draw_dice_rolling_screen(screen, game_state, fonts, images)
    elif game_state.screen == "dice_results":
        draw_dice_results_screen(screen, game_state, fonts, images)
    elif game_state.screen == "dice_rules":
        draw_dice_rules_screen(screen, game_state, fonts, images)
    elif game_state.screen == "merchant_shop":
        draw_merchant_screen(screen, game_state, fonts, game_state.get_garrick_inventory(), images)

    #elif game_state.screen == "merchant_shop":
        draw_merchant_screen(screen, game_state, fonts, game_state.get_garrick_inventory(), images)

    # Draw character sheet overlay if open
    if game_state.character_sheet_open:
        draw_character_sheet_screen(screen, game_state, fonts, images)

    # Draw quest log overlay if open 
    if game_state.quest_log_open:
        draw_quest_log_screen(screen, game_state, fonts, images)
    
    # Draw inventory overlay if open 
    if game_state.inventory_open:
        draw_inventory_screen(screen, game_state, fonts, images)
    
    # Draw help screen overlay if open
    if game_state.help_screen_open:
        draw_help_screen(screen, game_state, fonts, images)

     # Draw load screen overlay if open
    if game_state.load_screen_open:
        from screens.load_game import draw_load_game_screen
        draw_load_game_screen(screen, game_state, fonts, images, controller=controller)   

    # Draw save screen overlay if open
    if game_state.save_screen_open:
        from screens.save_game import draw_save_game_screen
        draw_save_game_screen(screen, game_state, fonts, images, controller)

def main():
    """Main game loop"""
    
    # Initialize everything
    screen, clock, fonts, images = initialize_game()
    game_state = GameState()
    game_state.screen = "game_title"  # Start with the game title screen


    controller = GameController(screen, game_state, fonts, images)
    GameConfig.apply_to_controller(controller)
    ScreenRegistry.register_all_screens(controller) 
    controller.debug_mode = True  # NEW LINE - enables debug overlay
    
    running = True
    
    print("=== TERROR IN REDSTONE ===")
    print("Modular game system initialized!")
    print("All fonts and images loaded successfully.")
    print("Press ESC to quit at any time.")
    print("==========================")
    
    # Main game loop
    while running:
        # Handle all events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                controller.shutdown()
                
            
            elif event.type == pygame.KEYDOWN:
                handle_keyboard_events.controller = controller  # Pass controller reference
                running = handle_keyboard_events(event, game_state)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                result = handle_mouse_events(mouse_pos, game_state, fonts, images, controller)
                if result is False:
                    running = False
        
        # Draw current screen
        draw_current_screen(screen, game_state, fonts, images, controller)
        
        # Draw debug overlay
        controller.draw_debug_overlay()

        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    # Clean shutdown
    controller.shutdown()
    

if __name__ == "__main__":
    main()