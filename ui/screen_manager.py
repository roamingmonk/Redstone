# ui/screen_manager.py
"""
Screen Manager - Enhanced Generic Screen Handling System
BUILDING ON YOUR EXISTING CODE - Enhanced to handle full screen lifecycle
Replaces hardcoded screen logic with data-driven approach + massive draw_current_screen elimination
"""

from typing import Dict, Callable, Any, Optional
import pygame
import os
import traceback
from utils.constants import OVERLAY_RESTRICTED_SCREENS, LAYOUT_IMAGE_Y, LAYOUT_BUTTON_CENTER_Y
from screens.character_creation import draw_summary_screen
from screens.load_game import draw_load_game_screen
from utils.overlay_utils import OverlayState
from screens.help_overlay import draw_help_screen
from screens.statistics_overlay import draw_statistics_screen
from screens.character_overlay import draw_character_sheet_screen
from screens.quest_overlay import draw_quest_overlay
from screens.inventory_overlay import draw_inventory_screen
from screens.save_game import draw_save_game_screen
from screens.combat_loot_overlay import draw_combat_loot_screen
from ui.shopping_overlay import ShoppingOverlay
from game_logic.commerce_engine import get_commerce_engine
from ui.combat_system import CombatEncounter
from ui.shopping_overlay import ShoppingOverlay
from ui.generic_dialogue_handler import draw_generic_dialogue_screen
from ui.death_overlay import create_death_overlay
from screens.intro_scenes import draw_intro_scene_1, draw_intro_scene_2, draw_intro_scene_3
from screens.act_two_transition import (draw_act_two_start, register_act_two_buttons, get_act_two_manager)
from screens.act_three_transition import (draw_act_three_start, register_act_three_buttons, get_act_three_manager)
from screens.victory_screen import draw_victory_screen

from screens.epilogue_slides import (draw_epilogue_slide_1, draw_epilogue_slide_2, draw_epilogue_slide_3,
                                    draw_epilogue_slide_4, draw_epilogue_slide_5, draw_epilogue_slide_6,
                                    draw_epilogue_slide_7)
from screens.credits import CreditsScreen

from screens.exploration_hub import draw_exploration_hub, register_exploration_hub_buttons, get_hub_manager
from screens.swamp_church_exterior_nav import draw_swamp_church_exterior_nav
from screens.swamp_church_interior_nav import draw_swamp_church_interior_nav
from screens.hill_ruins_entrance_nav import draw_hill_ruins_entrance_nav
from screens.hill_ruins_ground_level_nav import draw_hill_ruins_ground_level_nav
from screens.refugee_camp_main_nav import draw_refugee_camp_main_nav 

from screens.red_hollow_mine_pre_entrance_nav import draw_red_hollow_mine_pre_entrance_nav
from screens.red_hollow_mine_level_1_nav import draw_red_hollow_mine_level_1_nav
from screens.red_hollow_mine_level_2_nav import draw_red_hollow_mine_level_2_nav
from screens.red_hollow_mine_level_2b_nav import draw_red_hollow_mine_level_2b_nav
from screens.red_hollow_mine_level_3_nav import draw_red_hollow_mine_level_3_nav

from screens.dungeon_level_1_nav import draw_dungeon_level_1_nav
from screens.dungeon_level_2_nav import draw_dungeon_level_2_nav
from screens.dungeon_level_3_nav import draw_dungeon_level_3_nav
from screens.dungeon_level_4_nav import draw_dungeon_level_4_nav
from screens.dungeon_level_5_nav import draw_dungeon_level_5_nav


from ui.screen_handlers import (handle_main_menu_clicks, handle_dice_bets_clicks,
                                handle_dice_rolling_clicks, handle_dice_results_clicks,
                                handle_dice_rules_clicks)



class ScreenManager:
    """
    Enhanced Screen Manager that handles BOTH click routing AND screen rendering
    
    EXISTING FUNCTIONALITY (preserved):
    - Screen click handling registration  
    - Click routing to appropriate handlers
    
    NEW FUNCTIONALITY (added):
    - Full screen rendering lifecycle management
    - Screen registration with render functions
    - Professional screen transitions with history
    - Error handling and fallback systems
    - Replaces the massive 1700-line draw_current_screen() method
    """
    
    def __init__(self, event_manager, screen=None, fonts=None, images=None):
        # Your original click handling system
        self.event_manager = event_manager
        self.screens = {}  # screen_name -> screen_handler (click handlers)
        
        # Full screen rendering system
        self.screen = screen  # pygame display surface
        self.fonts = fonts    # font dictionary
        self.images = images  # image dictionary
        
        # Screen render function registry
        self.render_functions = {}  # screen_name -> render_function
        self.enter_hooks = {}       # screen_name -> enter_function
        self.exit_hooks = {}        # screen_name -> exit_function
        self.floating_text_manager = None

        # Screen state tracking
        self.current_screen = None
        self.previous_screen = None
        self.screen_history = []
        
        #Error handling
        self.fallback_screen = "main_menu"
        self.error_count = 0
        self.max_errors = 3

        self._current_game_controller = None 

        # Initialize - Manager References
        self.act_two_manager = None  
        self.act_three_manager = None  
        self.victory_manager = None
        self.epilogue_manager = None
        self.credits_screen_instance = None
        self.epilogue_manager = None

        # Navigation route map for simple transitions
        self.navigation_routes = {
            'START_GAME': 'developer_splash',
            'CONTINUE': 'main_menu',
            # Future routes can be added here
        }

        print("📺 Enhanced ScreenManager initialized")
        if event_manager:
            event_manager.register("SCREEN_CHANGE", self._handle_screen_change_event)
            event_manager.register("SCREEN_ADVANCE", self._handle_screen_advance_event)
            event_manager.register("DIALOGUE_ENDED", self._handle_dialogue_ended)
            event_manager.register("OPEN_SHOPPING", self._handle_open_shopping)
            event_manager.register("SHOPPING_BACK", self._handle_shopping_back)  ####  TODO REMOVE AFTER OVERLAY ADD
            event_manager.register("SHOPPING_ITEM_CLICK", self._handle_shopping_item_click)  ####  TODO REMOVE AFTER OVERLAY ADD
            self.event_manager.register("COMMERCE_PURCHASE", self._handle_commerce_purchase)
            self.event_manager.register("COMMERCE_RESET_CART", self._handle_commerce_reset)


            # Register direct navigation events
            # This direct system is simple and not the same input system as subsequent screens
            # Plan to use the screen manager route map for more complex flows
            event_manager.register("START_GAME", self._handle_direct_navigation)
            event_manager.register("CONTINUE", self._handle_direct_navigation)
            event_manager.register("LOAD_GAME", self._handle_load_game)
            event_manager.register("SAVE_GAME", self._handle_save_game)
            event_manager.register("NPC_CLICKED", self._handle_npc_clicked)
            event_manager.register("REGISTER_FULL_SCREEN_CLICK", self._handle_full_screen_registration)
            
            print("📺 ScreenManager subscribed to navigation events")

    def register_location_action_handler(self, event_manager):
        """Register LOCATION_ACTION event handler with EventManager"""
        
        def handle_location_action(event_data):
            """Process LOCATION_ACTION events from BaseLocation"""
            
            # 🐛 ADD THIS DEBUG
            print(f"📍 LOCATION_ACTION EVENT RECEIVED:")
            print(f"   action (action_name): {event_data.get('action')}")
            print(f"   location_id: {event_data.get('location_id')}")
            print(f"   area_id: {event_data.get('area_id')}")
            print(f"   action_data type: {event_data.get('action_data', {}).get('type')}")
            print(f"   Full event_data: {event_data}")

            action = event_data.get('action')
            location_id = event_data.get('location_id') 
            area_id = event_data.get('area_id')
            action_data_from_json = event_data.get('action_data', {})
            
            #print(f"🗺️ Processing location action: {action} at {location_id}.{area_id}")
            
            # Get the BaseLocation instance
            if hasattr(self, '_current_game_controller'):
                game_controller = self._current_game_controller
                
                if hasattr(game_controller, 'data_manager'):
                    location_manager = game_controller.data_manager.location_manager
                    location_instance = location_manager.get_location_instance(location_id)
                    
                    if location_instance:
                        # Let BaseLocation handle the action (thin coordination)
                        result = location_instance.handle_action(
                            action_data_from_json if action_data_from_json else {'action_name': action}, 
                            game_controller.game_state, 
                            self.event_manager
                        )
                        
                        if result:
                            print(f"✅ Action {action} processed successfully")
                        else:
                            print(f"⚠️ Action {action} processing failed")
                            
                    else:
                        print(f"❌ Location instance not found: {location_id}")
                else:
                    print(f"❌ DataManager not available")
            else:
                print(f"❌ GameController not available")
        
        # Register the handler using your EventManager's register method
        event_manager.register("LOCATION_ACTION", handle_location_action)
        print("🎯 Registered LOCATION_ACTION event handler")

    def register_exploration_hub_action_handler(self, event_manager):
        """Register EXPLORATION_HUB_ACTION event handler with EventManager"""
        
        def handle_exploration_hub_action(event_data):
            """Process EXPLORATION_HUB_ACTION events from exploration hub"""
            from screens.exploration_hub import get_hub_manager
            
            action = event_data.get('action')
            
            if not hasattr(self, '_current_game_controller'):
                print("❌ GameController not available")
                return
            
            game_controller = self._current_game_controller
            game_state = game_controller.game_state
            hub_manager = get_hub_manager()
            
            if action == 'return':
                # Return to Redstone town
                print("🗺️ Returning to Redstone town")
                self.event_manager.emit("SCREEN_CHANGE", {"target_screen": "redstone_town"})
                
            elif action == 'navigate':
                # Navigate to location
                location_id = event_data.get('location_id')
                if location_id and location_id in REDSTONE_REGION_LOCATIONS:
                    location_data = REDSTONE_REGION_LOCATIONS[location_id]
                    target = location_data['target']
                    print(f"🗺️ Traveling to {location_data['name']} → {target}")
                    self.event_manager.emit("SCREEN_CHANGE", {"target_screen": target})
                else:
                    print(f"❌ Unknown location: {location_id}")
            else:
                print(f"⚠️ Unknown exploration hub action: {action}")
        
        # Import here to avoid circular dependency
        from data.maps.redstone_region import REDSTONE_REGION_LOCATIONS
        
        # Register the handler
        event_manager.register("EXPLORATION_HUB_ACTION", handle_exploration_hub_action)
        print("🗺️ Registered EXPLORATION_HUB_ACTION event handler")

    def get_epilogue_manager(self):
        """Get or create epilogue manager"""
        if not self.epilogue_manager:
            from screens.epilogue_slides import EpilogueSequenceManager
            self.epilogue_manager = EpilogueSequenceManager(
                self.event_manager,
                self._current_game_state
            )
            print("🎬 EpilogueSequenceManager created")
        return self.epilogue_manager
    
    def _handle_full_screen_registration(self, event_data):
        """Handle dynamic full-screen clickable registration"""
        screen = event_data.get("screen")
        event_type = event_data.get("event_type")
        if screen and event_type:
            self.register_full_screen_clickable(screen, event_type)

    def register_full_screen_clickable(self, screen_name, event_type):
        """Dynamically register full-screen clickable"""
        if hasattr(self, 'input_handler') and self.input_handler:
            # Clear existing clickables for this screen
            self.input_handler.clear_clickables(screen_name)
            
            # Register full-screen clickable
            full_screen_rect = pygame.Rect(0, 0, 1024, 768)
            self.input_handler.register_clickable(screen_name, full_screen_rect, event_type, {})
            
            print(f"🖱️ Full-screen clickable registered for {screen_name}")
    
    def register_screen(self, screen_name: str, click_handler: Callable):
        """EXISTING: Register a screen's click handling function"""
        self.screens[screen_name] = {
            'click_handler': click_handler
        }
        print(f"🔗 Registered screen click handler: {screen_name}")

    def _handle_direct_navigation(self, event_data):
        """Handle navigation events that just emit SCREEN_CHANGE"""
        target_screen = event_data.get('target_screen')
        source_screen = event_data.get('source_screen', 'unknown')
        
        if target_screen:
            # Emit the SCREEN_CHANGE event that we already handle
            self.event_manager.emit('SCREEN_CHANGE', {
                'target_screen': target_screen,
                'source_screen': source_screen
            })

    def _handle_load_game(self, event_data):
        """Handle LOAD_GAME - open load overlay via unified state"""
        print("📂 ScreenManager: Opening load screen")
        if hasattr(self, '_current_game_state'):
            # Use unified overlay state system
            if not hasattr(self._current_game_state, 'overlay_state'):
                
                self._current_game_state.overlay_state = OverlayState()
            
            self._current_game_state.overlay_state.open_overlay("load_game")
            print(f"🔍 DEBUG: Overlay state set to: {self._current_game_state.overlay_state.get_active_overlay()}")

    def _handle_save_game(self, event_data):
        """Handle SAVE_GAME - open save overlay via unified state"""
        print("💾 ScreenManager: Opening save screen")
        if hasattr(self, '_current_game_state'):
            # Use unified overlay state system
            if not hasattr(self._current_game_state, 'overlay_state'):
                
                self._current_game_state.overlay_state = OverlayState()
            
            self._current_game_state.overlay_state.open_overlay("save_game")
            print(f"🔍 DEBUG: Overlay state set to: {self._current_game_state.overlay_state.get_active_overlay()}")

    def register_save_screen_clickables(self):
        """Register save screen clickables when save overlay opens"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Get button coordinates from the draw function
            temp_surface = pygame.Surface((1024, 768))
            
            # Get save_manager from game_controller
            save_manager = None
            if hasattr(self, '_current_game_controller') and self._current_game_controller:
                save_manager = getattr(self._current_game_controller, 'save_manager', None)
            
            #print(f"💾 DEBUG: save_manager = {save_manager}")
            #print(f"💾 DEBUG: _current_game_controller = {getattr(self, '_current_game_controller', 'NOT SET')}")

            result = draw_save_game_screen(
                temp_surface, 
                self._current_game_state, 
                self.fonts, 
                self.images,
                save_manager
            )
        
            if result:
                # Register slot selection areas
                for slot_rect, slot_num in result['slot_rects']:
                    self.input_handler.register_clickable(
                        'save_overlay', 
                        slot_rect, 
                        'SAVE_SLOT_SELECTED', 
                        {'slot_num': slot_num}
                    )
                    
                # Register buttons at fixed positions - always register, check state in handlers
                button_y = 650
                button_width = 120
                button_height = 50
                button_spacing = 40
                total_button_width = (3 * button_width) + (2 * button_spacing)  # Save, Save&Quit, Cancel
                start_x = (1024 - total_button_width) // 2

                # Always register all three buttons (Save, Save&Quit, Cancel)
                buttons = [
                    (start_x, 'SAVE_GAME_CONFIRM'),
                    (start_x + button_width + button_spacing, 'SAVE_AND_QUIT_CONFIRM'),
                    (start_x + (2 * button_width) + (2 * button_spacing), 'SAVE_SCREEN_CANCEL')
                ]

                for button_x, event_type in buttons:
                    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                    self.input_handler.register_clickable('save_overlay', button_rect, event_type, {})
                    
            else:
                print("⚠️ Could not get save screen button coordinates")
        else:
            print("⚠️ No InputHandler available for save screen registration")

    def _register_basic_screen_handlers(self):
        """Auto-register basic screen click handlers"""
        
        def handle_title_click(mouse_pos, game_controller, event_manager):
            event_manager.emit("SCREEN_CHANGE", {
                "target_screen": "developer_splash",
                "source_screen": "game_title"
            })
            return True
        
        def handle_developer_splash_click(mouse_pos, game_controller, event_manager):
            event_manager.emit("SCREEN_CHANGE", {
                "target_screen": "main_menu", 
                "source_screen": "developer_splash"
            })
            return True
        
        # Register all basic handlers
        self.register_screen("game_title", handle_title_click)
        self.register_screen("developer_splash", handle_developer_splash_click)
        self.register_screen("main_menu", handle_main_menu_clicks)
        
        # Register dice game handlers
        self.register_screen("dice_bets", handle_dice_bets_clicks)
        self.register_screen("dice_rolling", handle_dice_rolling_clicks)
        self.register_screen("dice_results", handle_dice_results_clicks)
        self.register_screen("dice_rules", handle_dice_rules_clicks)

        print("📺 Basic screen click handlers auto-registered")

    def handle_screen_click(self, screen_name: str, mouse_pos, game_controller):
        """EXISTING: Route click to appropriate screen handler"""
        if screen_name in self.screens:
            handler = self.screens[screen_name]['click_handler']
            return handler(mouse_pos, game_controller, self.event_manager)
        else:
            print(f"⚠️ No click handler registered for screen: {screen_name}")
            return False
    
    def get_registered_screens(self):
        """EXISTING: Get list of all registered screens"""
        return list(self.screens.keys())

    def _handle_npc_clicked(self, event_data):
        """Handle NPC_CLICKED events by navigating to dialogue screen"""
        npc_id = event_data.get('npc_id')
        location = event_data.get('location')
        
        if npc_id:
            # Construct screen name using location_npc pattern
            location = location or 'unknown'
            dialogue_screen = f"{location}_{npc_id}"  # Creates "redstone_town_bernard"
            print(f"📍 ScreenManager: NPC clicked: {npc_id}, navigating to {dialogue_screen}")
            
            # Use existing transition method
            if hasattr(self, '_current_game_state'):
                return self.transition_to(dialogue_screen, self._current_game_state)
        
        return False

    def register_stats_screen_clickables(self):
        """Register stats screen clickables when entering stats screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            # For each clickable region, call register_clickable individually
            
            # ROLL STATS button
            roll_rect = pygame.Rect(350, 320, 160, 50)
            self.input_handler.register_clickable('stats', roll_rect, 'REROLL_STATS', {})
            
            # KEEP STATS button  
            keep_rect = pygame.Rect(550, 320, 160, 50)
            self.input_handler.register_clickable('stats', keep_rect, 'KEEP_STATS', {})
            
            print("📊 Stats screen clickables registered")
        else:
            print("⚠️ No InputHandler available for stats screen registration")

    def register_gender_screen_clickables(self):
        """Register gender screen clickables when entering gender screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # MALE button (exact coordinates from draw_gender_screen)
            male_rect = pygame.Rect(340, 280, 160, 70)
            self.input_handler.register_clickable('gender', male_rect, 'SELECT_MALE', {})
            
            # FEMALE button (exact coordinates from draw_gender_screen)  
            female_rect = pygame.Rect(560, 280, 160, 70)
            self.input_handler.register_clickable('gender', female_rect, 'SELECT_FEMALE', {})
            
            #print("🚹🚺 Gender screen clickables registered")
        else:
            print("⚠️ No InputHandler available for gender screen registration")

    def register_name_screen_clickables(self):
        """Register name screen clickables when entering name screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Use the same dynamic layout logic as draw_name_screen
            button_width = 220
            button_height = 50
            button_y = 200
            
            # Calculate starting position to center all three buttons (from the draw function)
            total_width = 3 * button_width + 2 * 20  # 20px spacing between buttons
            start_x = (1024 - total_width) // 2
            
            # Register the three name option buttons
            for i in range(3):
                x = start_x + i * (button_width + 20)
                name_rect = pygame.Rect(x, button_y, button_width, button_height)
                action_name = f'SELECT_NAME_{i+1}'
                self.input_handler.register_clickable('name', name_rect, action_name, {'action': action_name})
            
            # Action buttons (exact coordinates from draw_name_screen)
            action_button_y = 280
            
            # NEW NAMES button (350, 280, 160, 50)
            new_names_rect = pygame.Rect(350, action_button_y, 160, 50)
            self.input_handler.register_clickable('name', new_names_rect, 'REROLL_NAMES', {'action': 'REROLL_NAMES'})
            
            # CUSTOM NAME button (550, 280, 180, 50) 
            custom_rect = pygame.Rect(550, action_button_y, 180, 50)
            self.input_handler.register_clickable('name', custom_rect, 'CUSTOM_NAME', {'action': 'CUSTOM_NAME'})
            
            print("📝 Name selection screen clickables registered (dynamic layout)")
        else:
            print("⚠️ No InputHandler available for name screen registration")

    def register_custom_name_screen_clickables(self):
        """Register custom name screen clickables when entering custom name screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Button coordinates from draw_custom_name_screen
            button_y = 320
            
            # CONFIRM button (350, 320, 160, 50) - always register, engine will handle logic
            confirm_rect = pygame.Rect(350, button_y, 160, 50)
            self.input_handler.register_clickable('custom_name', confirm_rect, 'CONFIRM_CUSTOM_NAME', {'action': 'CONFIRM_CUSTOM_NAME'})
            
            # BACK button (550, 320, 160, 50)
            back_rect = pygame.Rect(550, button_y, 160, 50)
            self.input_handler.register_clickable('custom_name', back_rect, 'BACK_TO_NAME', {'action': 'BACK_TO_NAME'})
            
            # Input box clickable area for activating text input
            input_box_width = 400
            input_box_height = 50
            input_box_x = (1024 - input_box_width) // 2
            input_box_y = 220
            input_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
            self.input_handler.register_clickable('custom_name', input_rect, 'ACTIVATE_TEXT_INPUT', {'action': 'ACTIVATE_TEXT_INPUT'})
            
            print("✏️ Custom name screen clickables registered")
        else:
            print("⚠️ No InputHandler available for custom name screen registration")

    def register_name_confirm_screen_clickables(self):
        """Register name confirm screen clickables when entering name confirm screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Button coordinates from draw_name_confirm_screen - centered pair
            button_y = 280
            button_width = 160
            button_spacing = 40
            total_width = (button_width * 2) + button_spacing  # 360
            start_x = (1024 - total_width) // 2  # 332
            
            # CONFIRM button (332, 280, 160, 50)
            confirm_rect = pygame.Rect(start_x, button_y, button_width, 50)
            self.input_handler.register_clickable('name_confirm', confirm_rect, 'ACCEPT_NAME', {'action': 'ACCEPT_NAME'})
            
            # BACK button (532, 280, 160, 50)
            back_rect = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, 50)
            self.input_handler.register_clickable('name_confirm', back_rect, 'BACK_TO_NAME_SELECTION', {'action': 'BACK_TO_NAME_SELECTION'})
            
            #print("✅ Name confirm screen clickables registered")
        else:
            print("⚠️ No InputHandler available for name confirm screen registration")
        
    def register_cavia_warning_clickables(self, game_state=None):
        """Register Cavia warning screen clickables"""
        if hasattr(self, 'input_handler') and self.input_handler:
            print("🎮 Registering Cavia warning screen clickables")
            
            # Button coordinates from draw_cavia_warning_screen
            # text_y = 160, button_y = text_y + 230 = 390
            button_y = 390
            
            # BACK button: (280, button_y, 200, 50) - "PICK SOMETHING ELSE"
            back_rect = pygame.Rect(280, button_y, 200, 50)
            self.input_handler.register_clickable('cavia_warning', back_rect,
                                                'CAVIA_WARNING_BACK', {'action': 'CAVIA_WARNING_BACK'})
            
            # CONFIRM button: (520, button_y, 200, 50) - "I'M A GUINEA PIG!"
            confirm_rect = pygame.Rect(520, button_y, 200, 50)
            self.input_handler.register_clickable('cavia_warning', confirm_rect,
                                                'CAVIA_WARNING_CONFIRM', {'action': 'CAVIA_WARNING_CONFIRM'})
            
            print("✅ Cavia warning clickables registered (2 buttons)")
        else:
            print("⚠️ No InputHandler available for Cavia warning screen registration")

    def register_portrait_screen_clickables(self):
        """Register portrait screen clickables when entering portrait screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Use exact coordinates from draw_portrait_selection_screen
            portrait_size = 110
            total_width = 6 * portrait_size + 5 * 20  # 6 portraits + 5 gaps of 20px
            start_x = (1024 - total_width) // 2  # Center the row
            portrait_y = LAYOUT_IMAGE_Y + 120  # Same as draw function
            
            # Register each portrait clickable (1-5)
            for i in range(6):
                portrait_x = start_x + i * (portrait_size + 20)
                portrait_rect = pygame.Rect(portrait_x, portrait_y, portrait_size, portrait_size)
                action_name = f'SELECT_PORTRAIT_{i+1}'  # 1-6 for semantic actions
                self.input_handler.register_clickable('portrait_selection', portrait_rect, 
                                                    action_name, {'action': action_name})
            
            # Register button clickables
            button_y = LAYOUT_BUTTON_CENTER_Y
            
            # BACK button (300, button_y, 120, 40)
            back_rect = pygame.Rect(300, button_y, 120, 40)
            self.input_handler.register_clickable('portrait_selection', back_rect, 
                                                'BACK_FROM_PORTRAIT', {'action': 'BACK_FROM_PORTRAIT'})
            
            # CONTINUE button (600, button_y, 120, 40)
            continue_rect = pygame.Rect(600, button_y, 120, 40)
            self.input_handler.register_clickable('portrait_selection', continue_rect, 
                                                'CONFIRM_PORTRAIT', {'action': 'CONFIRM_PORTRAIT'})
            
            #print("🖼️ Portrait selection screen clickables registered (5 portraits + 2 buttons)")
        else:
            print("⚠️ No InputHandler available for portrait screen registration")

    def register_gold_screen_clickables(self):
        """Register gold screen clickables when entering gold screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
           # Button coordinates from draw_gold_screen - centered at (432, 280, 160, 50)
            button_rect = pygame.Rect(432, 280, 160, 50)
            
            # Register the single button - logic will be handled by CharacterEngine
            self.input_handler.register_clickable('gold', button_rect, 'GOLD_BUTTON_CLICK', {'action': 'GOLD_BUTTON_CLICK'})
            
            print("🪙 Gold screen clickables registered")
        else:
            print("⚠️ No InputHandler available for gold screen registration")

    def register_trinket_screen_clickables(self):
        """Register trinket screen clickables when entering trinket screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Button coordinates from draw_trinket_screen - centered at (432, 280, 160, 50)
            button_rect = pygame.Rect(432, 280, 160, 50)
 
            # Register the button - CharacterEngine will determine if it's ROLL or CONTINUE
            self.input_handler.register_clickable('trinket', button_rect, 'TRINKET_BUTTON_CLICK', {'action': 'TRINKET_BUTTON_CLICK'})
            
            print("🎭 Trinket screen clickables registered")
        else:
            print("⚠️ No InputHandler available for trinket screen registration")

    def register_summary_screen_clickables(self, game_state):
        """Register clickable regions for summary screen using semantic actions"""
        
       # Get the START GAME button coordinates from the draw function
        temp_surface = pygame.Surface((1024, 768))
        
        start_button = draw_summary_screen(
            temp_surface, 
            game_state, 
            self.fonts, 
            self.images
        )
        
        if start_button:
            # Register the START GAME button with semantic action
            self.input_handler.register_clickable(
                "summary", 
                start_button, 
                "START_GAME", 
                {}
            )
            
        else:
            print("⚠️ Could not get START GAME button coordinates")
            
    def register_intro_scene_clickables(self, scene_id):
        """
        Register clickables for intro scene using the established pattern
        This follows your proven semantic action architecture
        """
        if hasattr(self, 'input_handler') and self.input_handler:
            # Get button coordinates by rendering the scene
            temp_surface = pygame.Surface((1024, 768))
            
            # Call the actual registered scene function, not the generic one
            if scene_id == "intro_scene_1":
                scene_result = draw_intro_scene_1(temp_surface, None, self.fonts, self.images)
            elif scene_id == "intro_scene_2":
                scene_result = draw_intro_scene_2(temp_surface, None, self.fonts, self.images)
            elif scene_id == "intro_scene_3":
                scene_result = draw_intro_scene_3(temp_surface, None, self.fonts, self.images)
            else:
                print(f"⚠️ Unknown scene_id: {scene_id}")
                return
            
            if scene_result:
                # Register CONTINUE button
                self.input_handler.register_clickable(
                    scene_id, 
                    scene_result["continue_button"], 
                    "INTRO_NEXT", 
                    {}
                )
                
                # Register SKIP button
                self.input_handler.register_clickable(
                    scene_id, 
                    scene_result["skip_button"], 
                    "INTRO_SKIP", 
                    {}
                )
                
                print(f"🎬 Intro scene clickables registered: {scene_id}")
            else:
                print(f"⚠️ Could not register clickables for {scene_id}")
        else:
            print("⚠️ No InputHandler available for intro scene registration")

    def register_act_two_clickables(self):
        """
        Register clickable buttons for ACT TWO transition screen
        Follows intro_scenes pattern for consistency
        """
        if hasattr(self, 'input_handler') and self.input_handler:
            # Get button coordinates by rendering the scene to temp surface
            temp_surface = pygame.Surface((1024, 768))
            
            # Call the draw function to get button rects
            scene_result = draw_act_two_start(temp_surface, None, self.fonts, self.images)
            
            if scene_result and "continue_button" in scene_result:
                # Register CONTINUE button with semantic action
                self.input_handler.register_clickable(
                    "act_two_start",
                    scene_result["continue_button"],
                    "ACT_TWO_CONTINUE",
                    {}
                )
                
                print(f"🎬 Act II clickables registered")
            else:
                print(f"⚠️ Could not register Act II clickables")
        else:
            print("⚠️ No InputHandler available for Act II registration")

    def register_act_three_clickables(self):
        """
        Register clickable buttons for ACT THREE transition screen
        Follows act_two pattern for consistency
        """
        if hasattr(self, 'input_handler') and self.input_handler:
            # Get button coordinates by rendering the scene to temp surface
            temp_surface = pygame.Surface((1024, 768))
            
            # Call the draw function to get button rects
            scene_result = draw_act_three_start(temp_surface, None, self.fonts, self.images)
            
            if scene_result and "continue_button" in scene_result:
                # Register CONTINUE button with semantic action
                self.input_handler.register_clickable(
                    "act_three_start",
                    scene_result["continue_button"],
                    "ACT_THREE_CONTINUE",
                    {}
                )
                
                print(f"🎬 Act III clickables registered")
            else:
                print(f"⚠️ Could not register Act III clickables")
        else:
            print("⚠️ No InputHandler available for Act III registration")

    def register_victory_screen_clickables(self, game_state):
        """
        Register clickable button for victory screen
        Follows intro_scenes and act_two patterns
        """
        if hasattr(self, 'input_handler') and self.input_handler:
            # Get button coordinates by rendering to temp surface
            temp_surface = pygame.Surface((1024, 768))
            
            # Call the draw function to get button rect
            from screens.victory_screen import draw_victory_screen
            scene_result = draw_victory_screen(temp_surface, self._current_game_state, self.fonts, self.images)
            
            if scene_result and "continue_button" in scene_result:
                # Register CONTINUE button with screen change event
                self.input_handler.register_clickable(
                    "victory_screen",
                    scene_result["continue_button"],
                    "SCREEN_CHANGE",
                    {"target": "dungeon_level_5_nav", "source": "victory_screen"}
                )
                
                print(f"🏆 Victory screen clickables registered")
            else:
                print(f"⚠️ Could not register victory screen clickables")
        else:
            print("⚠️ No InputHandler available for victory screen registration")

    def register_load_screen_clickables(self):
        """Register load screen clickables when load overlay opens"""
        if hasattr(self, 'input_handler') and self.input_handler:
           
           # Clear old clickables first
            self.input_handler.clear_clickables('load_overlay')
            
            # Get button coordinates from the draw function
            temp_surface = pygame.Surface((1024, 768))
           
            
            # Get save_manager from game_controller
            save_manager = None
            if hasattr(self, '_current_game_controller') and self._current_game_controller:
                save_manager = getattr(self._current_game_controller, 'save_manager', None)
            
            #print(f"🔍 DEBUG: save_manager = {save_manager}")
            #print(f"🔍 DEBUG: _current_game_controller = {getattr(self, '_current_game_controller', 'NOT SET')}")

            result = draw_load_game_screen(
                temp_surface, 
                self._current_game_state, 
                self.fonts, 
                self.images,
                save_manager
            )
           
            if result:
                # Get current screen name (where load overlay is displayed)
                #current_screen = getattr(self._current_game_state, 'screen', 'combat')
                
                screen_key = 'load_overlay'
                
                # Register slot selection areas with HIGHER priority than underlying screen
                for slot_rect, slot_num in result['slot_rects']:
                    self.input_handler.register_clickable(
                        screen_key,  
                        slot_rect, 
                        'LOAD_SLOT_SELECTED', 
                        {'slot_num': slot_num},
                        priority=200  # Higher than death overlay (100), higher than combat grid
                    )
                      
            # Register buttons at fixed positions - always register, check state in handlers
            button_y = 650
            button_width = 120
            button_height = 50
            button_spacing = 40
            total_button_width = (3 * button_width) + (2 * button_spacing)
            start_x = (1024 - total_button_width) // 2

            # Always register all three buttons
            buttons = [
                (start_x, 'LOAD_GAME_CONFIRM'),
                (start_x + button_width + button_spacing, 'DELETE_SAVE_CONFIRM'), 
                (start_x + 2 * (button_width + button_spacing), 'LOAD_SCREEN_CANCEL')
            ]

            for button_x, event_type in buttons:
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                self.input_handler.register_clickable(screen_key, button_rect, event_type, {}, priority=200)
                
                #print("🔍 Load screen clickables registered")
            
        else:
            print("⚠️ No InputHandler available for load screen registration")

    def register_exploration_hub_clickables(self):
        """Register clickable areas for exploration hub"""
        register_exploration_hub_buttons(self)
        print("🗺️ Exploration hub clickables registered")

    def register_stats_confirm_low_clickables(self):
        """Register low stats confirmation clickables"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Only register normal warning screen buttons
            reroll_rect = pygame.Rect(300, 280, 160, 50)
            self.input_handler.register_clickable('stats_confirm_low', reroll_rect, 'REROLL_FROM_CONFIRM', {})
            
            proceed_rect = pygame.Rect(500, 280, 160, 50)
            self.input_handler.register_clickable('stats_confirm_low', proceed_rect, 'PROCEED_WITH_LOW_STATS', {})
            
            print("⚠️ Low stats confirmation clickables registered")

    def _handle_open_shopping(self, event_data):
        """Handle OPEN_SHOPPING events from dialogue system"""
        print(f"📺 ScreenManager: _handle_open_shopping called with: {event_data}")
        
        merchant_id = event_data.get('merchant_id')
        source_location = event_data.get('source_location', 'broken_blade')
        
        print(f"🛒 Opening shopping for merchant: {merchant_id}")

        # Get merchant data from ItemManager
        data_manager = self._current_game_controller.data_manager
        if data_manager:
            item_manager = data_manager.get_manager('items')
            if item_manager:
                # Load merchant configuration if not already loaded
                if not hasattr(item_manager, 'merchant_data') or not item_manager.merchant_data:
                    item_manager.load_merchant_data()
                
                # Get the merchant config from merchants.json
                merchant_config = item_manager.merchant_data.get('merchants', {}).get(merchant_id)
                
                if merchant_config:
                    # Get game state early so we can pass it to get_merchant_inventory
                    game_state = self._current_game_controller.game_state

                    # Get merchant inventory using proper ItemManager method (includes player-sold items)
                    merchant_inventory = item_manager.get_merchant_inventory(merchant_id, game_state=game_state)
                    if merchant_inventory:
                        merchant_items = merchant_inventory.get('items', [])
                        merchant_name = merchant_inventory.get('merchant_name', merchant_id)
                    else:
                        print(f"❌ No inventory returned for {merchant_id}")
                        return

                    # Create the merchant data structure
                    merchant_data = {
                        'merchant_id': merchant_id,
                        'merchant_name': merchant_name,
                        'items': merchant_items
                    }
                    
                    # Initialize merchant stock in commerce engine if not already done
                    commerce_engine = self._current_game_controller.commerce_engine
                    if commerce_engine:
                        if not hasattr(game_state, 'merchant_stocks'):
                            game_state.merchant_stocks = {}
                        
                        # Only initialize if this merchant hasn't been stocked yet
                        if merchant_id not in game_state.merchant_stocks:
                            commerce_engine._initialize_merchant_stock(merchant_id)
                            print(f"🛒 First visit to {merchant_id} - stock initialized")


                    # Store merchant data in game state
                    game_state = self._current_game_controller.game_state

                    # # Check if merchant needs refresh (day changed, removes player-sold loot)
                    # commerce_engine = self._current_game_controller.commerce_engine
                    # if commerce_engine and commerce_engine.should_refresh_merchant(merchant_id):
                    #     commerce_engine.refresh_merchant_stock(merchant_id)
                    #     # Reload merchant inventory after refresh
                    #     merchant_inventory = item_manager.get_merchant_inventory(merchant_id)
                    #     if merchant_inventory:
                    #         merchant_items = merchant_inventory.get('items', [])
                    #         merchant_data['items'] = merchant_items
                    #         print(f"✅ Merchant {merchant_id} stock refreshed")

                    setattr(game_state, 'current_merchant_data', merchant_data)
                    setattr(game_state, 'current_merchant_id', merchant_id)
                    setattr(game_state, 'shopping_return_dialogue', f"{source_location}_{merchant_id}")
                    
                    # Use the same event structure as other screen changes
                    self.event_manager.emit("SCREEN_CHANGE", {
                        'target_screen': "merchant_shop",
                        'source_screen': source_location
                    })
                    return
                else:
                    print(f"❌ No merchant config found for {merchant_id}")
            else:
                print("❌ No item_manager found")
        else:
            print("❌ No data_manager found")
        
        print(f"❌ Failed to open shop for {merchant_id}")

# #########  TODO Keep as fallback until render shopping overlay is confirmed.  /////Plan to remove ////
#     def _render_merchant_shop(self, surface, game_state, fonts, images, controller):
#         """TEMPORARY: Render tabbed shopping overlay - will be removed once verified"""
#         if not hasattr(self, '_shopping_overlay'):
#             self._shopping_overlay = ShoppingOverlay(screen_manager=self)
        
#         self._shopping_overlay.render(surface, game_state, fonts, images or {})
#         return True
# #########  TODO Keep as fallback until render shopping overlay is confirmed.  /////Plan to remove ////
    def _handle_shopping_back(self, event_data):
        """Handle BACK button - navigation only- TOBE REMOVED AFTER OVERLAY ADD"""
        print("🛒 BACK button clicked!")
        game_state = self._current_game_controller.game_state
        return_dialogue = getattr(game_state, 'shopping_return_dialogue', 'broken_blade_garrick')
        
        self.event_manager.emit("SCREEN_CHANGE", {
            'target_screen': return_dialogue,
            'source_screen': "merchant_shop"
        })

# #########   TODO Keep as fallback until render shopping overlay is confirmed.  /////Plan to remove ////
    def _handle_shopping_item_click(self, event_data):
        """Handle item row clicks - add to cart- TOBE REMOVED AFTER OVERLAY ADD"""
        item_index = event_data.get('item_index')
        print(f"🛒 Item {item_index} clicked!")
        
        # Get current merchant data to find which item was clicked
        game_state = self._current_game_controller.game_state
        merchant_data = getattr(game_state, 'current_merchant_data', None)
        
        if merchant_data and item_index is not None:
            items = merchant_data.get('items', [])
            if 0 <= item_index < len(items):
                clicked_item = items[item_index]
                item_id = clicked_item.get('item_id')
                merchant_id = merchant_data.get('merchant_id')
                
                # Check stock before allowing add to cart
                commerce = get_commerce_engine()
                stock_status = commerce.get_stock_status(item_id, merchant_id)
                
                if stock_status['remaining'] <= 0:
                    print(f"⚠️ {clicked_item.get('name', item_id)} is out of stock!")
                    return  # Don't add to cart   

                # Emit event to CommerceEngine to add item to cart
                self.event_manager.emit("COMMERCE_ADD_TO_CART", {
                    'item_id': item_id,
                    'merchant_id': merchant_id,
                    'action': 'add_to_cart'
                })


    def _handle_shopping_item_click_direct(self, item_index):
        """Handle direct item click in shopping overlay"""
        game_state = self._current_game_controller.game_state
        merchant_data = getattr(game_state, 'current_merchant_data', None)
        
        if merchant_data and merchant_data.get('items'):
            items = merchant_data['items']
            if 0 <= item_index < len(items):
                clicked_item = items[item_index]
                item_id = clicked_item.get('item_id')
                merchant_id = merchant_data.get('merchant_id')
                
                # Check stock
                commerce = get_commerce_engine()
                stock_status = commerce.get_stock_status(item_id, merchant_id)
                
                if stock_status['remaining'] <= 0:
                    print(f"⚠️ {clicked_item.get('name', item_id)} is out of stock!")
                    return
                
                # Add to cart
                commerce.add_to_cart(item_id, merchant_id)
                print(f"🛒 Added {clicked_item.get('name')} to cart")

    def _handle_shopping_close(self):
        """Handle closing the shopping overlay"""
        game_state = self._current_game_controller.game_state
        return_dialogue = getattr(game_state, 'shopping_return_dialogue', 'broken_blade_garrick')
        
        self.event_manager.emit("SCREEN_CHANGE", {
            'target_screen': return_dialogue,
            'source_screen': "merchant_shop"
        })

    def _handle_commerce_purchase(self, event_data):
        """Handle purchase button from shopping overlay"""
        game_state = self._current_game_controller.game_state
        merchant_id = getattr(game_state, 'current_merchant_id', 'garrick')
        commerce = get_commerce_engine()
        success, message = commerce.process_purchase(merchant_id)
        print(f"🛒 {message}")

    def _handle_commerce_reset(self, event_data):
        """Handle reset cart button from shopping overlay"""
        
        commerce = get_commerce_engine()
        commerce.clear_cart()
        print("🛒 Shopping cart cleared")

    def handle_current_screen_input(self, event, game_state):
        """
        Handle input for screens that manage their own input (overlays)
        Returns True if input was handled, False otherwise
        """
        current_screen = game_state.screen
       #TODO these are not active.  is this an orphaned method?  consider removal 
        # Shopping overlay input handling
        if current_screen == "merchant_shop" and hasattr(self, '_shopping_overlay'):
            if event.type == pygame.KEYDOWN:
                # Handle tab switching and shortcuts
                if event.key == pygame.K_b:  # BUY tab
                    return self._shopping_overlay.switch_to_tab(0)
                elif event.key == pygame.K_s:  # SELL tab
                    return self._shopping_overlay.switch_to_tab(1)
                elif event.key == pygame.K_i:  # INFO tab
                    return self._shopping_overlay.switch_to_tab(2)
                elif event.key == pygame.K_ESCAPE:
                    # Close shopping overlay
                    self._handle_shopping_close()
                    return True
                # Let overlay handle other keys
                return self._shopping_overlay.handle_keyboard_input(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Let overlay handle clicks
                click_handled = self._shopping_overlay.handle_mouse_click(event.pos)
                if click_handled:
                    return True
                
                # Handle button clicks within overlay
                if hasattr(self._shopping_overlay, 'button_rects'):
                    for button_name, button_rect in self._shopping_overlay.button_rects.items():
                        if button_rect and button_rect.collidepoint(event.pos):
                            if button_name == 'buy':
                                self._handle_commerce_purchase({})
                            elif button_name == 'reset':
                                self._handle_commerce_reset({})
                            elif button_name == 'close':
                                self._handle_shopping_close()
                            return True
                
                # Handle item clicks in BUY tab
                if self._shopping_overlay.active_tab_index == 0:  # BUY tab
                    for item_rect, item_index in self._shopping_overlay.merchant_item_rects:
                        if item_rect.collidepoint(event.pos):
                            self._handle_shopping_item_click_direct(item_index)
                            return True
        
        return False

    def register_quest_log_screen_clickables(self):
        """Register clickable areas for quest log screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            self.input_handler.clear_clickables('quest_log')
            # For now, just register ESC to close - you can add specific quest buttons later
            print("📋 Quest log screen clickables registered")
        else:
            print("⚠️ No InputHandler available for quest log screen")

    def register_combat_screen_clickables(self):
        """Register clickable areas for combat screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            # Store reference to combat encounter for click handling
            from ui.combat_system import get_combat_encounter
            self._combat_encounter = get_combat_encounter()
            print("⚔️ Combat screen handler registered")
        else:
            print("⚠️ No InputHandler available for combat screen")

    def register_quest_overlay_clickables(self):
        """Register clickable areas for quest overlay"""
        if hasattr(self, 'input_handler') and self.input_handler:
            self.input_handler.clear_clickables('quest_log')
            print("📋 Quest overlay clickables registered")
        else:
            print("⚠️ No InputHandler available for quest overlay")

    def register_character_sheet_screen_clickables(self):
        """Register clickable areas for character sheet screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            self.input_handler.clear_clickables('character_sheet')
            # For now, just register ESC to close - you can add specific character sheet buttons later
            print("👤 Character sheet screen clickables registered")
        else:
            print("⚠️ No InputHandler available for character sheet screen")

    def register_help_screen_clickables(self):
        """Register clickable areas for help screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            self.input_handler.clear_clickables('help')
            # For now, just register ESC to close - you can add specific help buttons later
            print("❓ Help screen clickables registered")
        else:
            print("⚠️ No InputHandler available for help screen")

    def register_shopping_overlay_clickables(self):
        """Register clickable areas for shopping overlay"""
        if hasattr(self, 'input_handler') and self.input_handler:
            self.input_handler.clear_clickables('merchant_shop')
            
            # Register tab clicks if overlay exists
            if hasattr(self, '_shopping_overlay') and self._shopping_overlay:
                # Let the overlay handle its own clicks
                print("🛒 Shopping overlay clickables registered")
            # Register ESC to close (will be handled by overlay)
        else:
            print("⚠️ No InputHandler available for shopping overlay")

    def register_render_function(self, screen_name: str, render_function: Callable,
                                enter_hook: Optional[Callable] = None,
                                exit_hook: Optional[Callable] = None):
        """
        NEW: Register a screen's rendering function and optional lifecycle hooks
        
        Args:
            screen_name: Unique identifier for the screen
            render_function: Function that renders the screen (screen, game_state, fonts, images)
            enter_hook: Optional function called when entering screen
            exit_hook: Optional function called when leaving screen
        """
        self.render_functions[screen_name] = render_function
        
        if enter_hook:
            self.enter_hooks[screen_name] = enter_hook
        if exit_hook:
            self.exit_hooks[screen_name] = exit_hook
            
        print(f"🎨 Screen render function registered: {screen_name}")
    
    def register_all_screen_renders(self):
        """
        NEW: Register all game screen render functions
        This replaces the massive if/elif chain in draw_current_screen()
        """
        
        try:
            # Import all screen drawing functions
            from screens.title_menu import draw_title_screen, draw_company_splash_screen, draw_main_menu
            from screens.character_creation import (
                draw_stats_screen, draw_gender_screen, draw_name_screen,
                draw_custom_name_screen, draw_name_confirm_screen, 
                draw_portrait_selection_screen, draw_cavia_warning_screen,
                draw_gold_screen, draw_trinket_screen, draw_stats_confirm_low_screen,
                draw_summary_screen
            )
            
            from screens.intro_scenes import (
                draw_intro_scene_1, draw_intro_scene_2, draw_intro_scene_3
            )
            from ui.shopping_overlay import draw_shopping_overlay
            from screens.inventory_overlay import draw_inventory_screen
            from screens.quest_overlay import draw_quest_overlay
            from screens.character_overlay import draw_character_sheet_screen
            from screens.help_overlay import draw_help_screen
            from screens.combat_loot_overlay import draw_combat_loot_screen

            from screens.gambling_dice import (
                draw_dice_bets_screen, draw_dice_rolling_screen,
                draw_dice_results_screen, draw_dice_rules_screen
            )
            
            from screens.redstone_town import render_town_navigation
            from ui.combat_system import draw_combat_screen

            # Title and menu screens
            self.register_render_function("game_title", draw_title_screen)
            self.register_render_function("developer_splash", draw_company_splash_screen)
            self.register_render_function("main_menu", draw_main_menu)
            
            # Character creation screens
            self.register_render_function("stats", draw_stats_screen,
                enter_hook=lambda _: self.register_stats_screen_clickables())
            self.register_render_function("gender", draw_gender_screen,
                enter_hook=lambda _: self.register_gender_screen_clickables())
            self.register_render_function("name", draw_name_screen,
                enter_hook=lambda _: self.register_name_screen_clickables())
            self.register_render_function("custom_name", draw_custom_name_screen,
                enter_hook=lambda _: self.register_custom_name_screen_clickables())  
            self.register_render_function("name_confirm", draw_name_confirm_screen,
                enter_hook=lambda _: self.register_name_confirm_screen_clickables()) 
            self.register_render_function("portrait_selection", draw_portrait_selection_screen,
                enter_hook=lambda _: self.register_portrait_screen_clickables())
            self.register_render_function("cavia_warning", draw_cavia_warning_screen,
                enter_hook=lambda game_state: self.register_cavia_warning_clickables(game_state))
            self.register_render_function("gold", draw_gold_screen,
                enter_hook=lambda _: self.register_gold_screen_clickables())
            self.register_render_function("trinket", draw_trinket_screen,
                enter_hook=lambda _: self.register_trinket_screen_clickables())
            self.register_render_function("stats_confirm_low", draw_stats_confirm_low_screen,
                enter_hook=lambda _: self.register_stats_confirm_low_clickables())
            self.register_render_function("summary", draw_summary_screen,
                enter_hook=lambda game_state: self.register_summary_screen_clickables(game_state))
            self.register_render_function("intro_scene_1", draw_intro_scene_1,
                enter_hook=lambda _: self.register_intro_scene_clickables("intro_scene_1"))
            self.register_render_function("intro_scene_2", draw_intro_scene_2,
                enter_hook=lambda _: self.register_intro_scene_clickables("intro_scene_2"))
            self.register_render_function("intro_scene_3", draw_intro_scene_3,
                enter_hook=lambda _: self.register_intro_scene_clickables("intro_scene_3"))



            self.register_render_function("act_two_start", draw_act_two_start,
                enter_hook=lambda _: self.register_act_two_clickables())
            self.register_render_function("act_three_start", draw_act_three_start,
                enter_hook=lambda _: self.register_act_three_clickables())  
            
            # Act II Exploration Hub - Tile-based Regional Map
            self.register_render_function("exploration_hub", draw_exploration_hub,
                enter_hook=lambda _: self.register_exploration_hub_clickables())

        # BaseLocation System
            # Broken Blade Tavern 
            self._auto_register_location("broken_blade")
            self._auto_register_location("patron_selection")

            # Act II Exploration Hub (custom tile-based map - NOT auto-registered)
            # self._auto_register_location("exploration_hub")  # Disabled - using custom renderer

            # Act II Investigation Locations
            self._auto_register_location("swamp_church")
            self._auto_register_location("hill_ruins")
            self._auto_register_location("refugee_camp")  
            self._auto_register_location("red_hollow_mine")  
            # Redstown Town
            self.register_render_function("redstone_town", render_town_navigation)
            # Swamp church navigation
            self.register_render_function("swamp_church_exterior_nav", draw_swamp_church_exterior_nav)
            self.register_render_function("swamp_church_interior_nav", draw_swamp_church_interior_nav)
            # Hill ruins navigation
            self.register_render_function("hill_ruins_entrance_nav", draw_hill_ruins_entrance_nav)
            self.register_render_function("hill_ruins_ground_level_nav", draw_hill_ruins_ground_level_nav)
            # Refugee camp navigation
            self.register_render_function("refugee_camp_main_nav", draw_refugee_camp_main_nav)
            # Red Hollow Mine navigation
            self.register_render_function("red_hollow_mine_pre_entrance_nav", draw_red_hollow_mine_pre_entrance_nav)
            self.register_render_function("red_hollow_mine_level_1_nav", draw_red_hollow_mine_level_1_nav)
            self.register_render_function("red_hollow_mine_level_2_nav", draw_red_hollow_mine_level_2_nav)
            self.register_render_function("red_hollow_mine_level_2b_nav", draw_red_hollow_mine_level_2b_nav)
            self.register_render_function("red_hollow_mine_level_3_nav", draw_red_hollow_mine_level_3_nav)
            #Hill Ruins Dungeon
            self.register_render_function("dungeon_level_1_nav", draw_dungeon_level_1_nav)
            self.register_render_function("dungeon_level_2_nav", draw_dungeon_level_2_nav)
            self.register_render_function("dungeon_level_3_nav", draw_dungeon_level_3_nav)
            self.register_render_function("dungeon_level_4_nav", draw_dungeon_level_4_nav)
            self.register_render_function("dungeon_level_5_nav", draw_dungeon_level_5_nav)

            # Victory screen (post-boss defeat)
            self.register_render_function("victory_screen", draw_victory_screen,
                                        enter_hook=self.register_victory_screen_clickables)
            print("🏆 Victory screen registered")

            # Epilogue slides 
            self.register_render_function("epilogue_slide_1", draw_epilogue_slide_1,
                enter_hook=lambda _: (self.get_epilogue_manager(), self.register_epilogue_slide_clickables("epilogue_slide_1")))

            self.register_render_function("epilogue_slide_2", draw_epilogue_slide_2,
                enter_hook=lambda _: (self.get_epilogue_manager(), self.register_epilogue_slide_clickables("epilogue_slide_2")))

            self.register_render_function("epilogue_slide_3", draw_epilogue_slide_3,
                enter_hook=lambda _: (self.get_epilogue_manager(), self.register_epilogue_slide_clickables("epilogue_slide_3")))
            
            self.register_render_function("epilogue_slide_4", draw_epilogue_slide_4,
                enter_hook=lambda _: (self.get_epilogue_manager(),self.register_epilogue_slide_clickables("epilogue_slide_4")))

            self.register_render_function("epilogue_slide_5", draw_epilogue_slide_5,
                enter_hook=lambda _: (self.get_epilogue_manager(),self.register_epilogue_slide_clickables("epilogue_slide_5")))

            self.register_render_function("epilogue_slide_6", draw_epilogue_slide_6,
                enter_hook=lambda _: (self.get_epilogue_manager(),self.register_epilogue_slide_clickables("epilogue_slide_6")))

            self.register_render_function("epilogue_slide_7", draw_epilogue_slide_7,
                enter_hook=lambda _: (self.get_epilogue_manager(),self.register_epilogue_slide_clickables("epilogue_slide_7")))

            print("🎬 Epilogue slides registered")

            # Credits screen (Session D)
            self.register_render_function("credits", self._render_credits_screen,
                enter_hook=lambda _: self.register_credits_clickables())
            print("🎞️ Credits screen registered")

            # Utility screens
            self.register_render_function("inventory", draw_inventory_screen,
                enter_hook=lambda _: self.register_inventory_screen_clickables())
            self.register_render_function("quest_log", draw_quest_overlay,
                enter_hook=lambda _: self.register_quest_overlay_clickables())
            self.register_render_function("character_sheet", draw_character_sheet_screen,
                enter_hook=lambda _: self.register_character_sheet_screen_clickables())
            self.register_render_function("help", draw_help_screen,
                enter_hook=lambda _: self.register_help_screen_clickables())
            self.register_render_function("merchant_shop", self._render_shopping_overlay,
                enter_hook=lambda _: self.register_shopping_overlay_clickables())

            self._register_npc_dialogue_screens()

            # Gambling mini-game screens
            self.register_render_function("dice_bets", draw_dice_bets_screen)
            self.register_render_function("dice_rolling", draw_dice_rolling_screen)
            self.register_render_function("dice_results", draw_dice_results_screen)
            self.register_render_function("dice_rules", draw_dice_rules_screen)
            
            self.register_render_function("combat", draw_combat_screen,
                enter_hook=lambda _: self.register_combat_screen_clickables())

            print(f"🎨 All screen render functions registered: {len(self.render_functions)} total")
            
            self._register_basic_screen_handlers()
        except ImportError as e:
            print(f"❌ Error importing screen functions: {e}")
            print("📍 Some screen modules may not exist yet - this is normal during development")
    
    def transition_to(self, screen_name: str, game_state, save_history: bool = True) -> bool:
        """
        NEW: Transition to a new screen with proper lifecycle management
        
        Args:
            screen_name: Target screen name
            game_state: Current game state
            save_history: Whether to save current screen in history
            
        Returns:
            True if transition successful, False if failed
        """
        if screen_name not in self.render_functions:
            print(f"❌ ERROR: Unknown render function for screen '{screen_name}'")
            print(f"📍 Registered screens: {list(self.render_functions.keys())}")
            return False

        # Save history for back navigation
        if save_history and self.current_screen:
            self.previous_screen = self.current_screen
            self.screen_history.append(self.current_screen)
            
            # Limit history size to prevent memory bloat
            if len(self.screen_history) > 10:
                self.screen_history.pop(0)
        
        # Call exit hook for current screen
        if self.current_screen and self.current_screen in self.exit_hooks:
            try:
                self.exit_hooks[self.current_screen](game_state)
            except Exception as e:
                print(f"⚠️ Error in exit hook for {self.current_screen}: {e}")
        
        # Update current screen
        old_screen = self.current_screen
        self.current_screen = screen_name
        
        # Update game state (Single Data Authority pattern)
        game_state.screen = screen_name
        
        # Call enter hook for new screen
        if screen_name in self.enter_hooks:
            try:
                self.enter_hooks[screen_name](game_state)
            except Exception as e:
                print(f"⚠️ Error in enter hook for {screen_name}: {e}")
        
        #print(f"🔄 Screen transition: {old_screen} → {screen_name}")
        return True
    
    def _auto_register_location(self, location_id: str):
        """
        Automatically register all areas of a location as screens
        
        Args:
            location_id: Location to register (e.g., 'broken_blade')
        """
        if not (hasattr(self, '_current_game_controller') and 
                self._current_game_controller and 
                hasattr(self._current_game_controller, 'data_manager')):
            print(f"⚠️ Cannot auto-register {location_id}: DataManager not available")
            return
        
        location_manager = self._current_game_controller.data_manager.location_manager
        area_ids = location_manager.get_all_area_ids(location_id)
            
        # Register each area as a screen
        for area_id in area_ids:
            # ALWAYS skip "_main" suffix for main areas for consistency
            if area_id == "main":
                screen_name = location_id  # Just "broken_blade", not "broken_blade_main"
            else:
                screen_name = f"{location_id}_{area_id}"  # "broken_blade_basement_cleared"
            
            self._register_base_location_screen(screen_name, location_id, area_id)
            print(f"📍 Auto-registered: {screen_name}")

    def _register_base_location_screen(self, screen_name: str, location_id: str, area_id: str):
        """Register a BaseLocation screen with proper event integration"""
        
        def location_render_function(surface, game_state, fonts, images, controller=None):
            """BaseLocation rendering function"""
            # Get controller from ScreenManager since it's not passed as parameter
            if not controller:
                controller = getattr(self, '_current_game_controller', None)
                                    
            if controller and hasattr(controller, 'data_manager'):
                location_manager = controller.data_manager.location_manager
                location_instance = location_manager.get_location_instance(location_id)
                
                if location_instance:
                    location_instance.navigate_to_area(area_id)
                    return location_instance.render(surface, game_state, fonts, images, controller)
            
            print(f"❌ FALLBACK: Using black screen because controller check failed")
            # Fallback
            surface.fill((0, 0, 0))
            return {}
                
        def location_enter_hook(game_state):
            """Register BaseLocation buttons when entering screen"""
            if hasattr(self, '_current_game_controller'):
                controller = self._current_game_controller
                if controller and hasattr(controller, 'data_manager'):
                    location_manager = controller.data_manager.location_manager
                    location_instance = location_manager.get_location_instance(location_id)
                    
                    if location_instance:
                        location_instance.navigate_to_area(area_id)
                        location_instance.register_with_input_handler(self, screen_name)
        
        # Register with ScreenManager
        self.register_render_function(screen_name, location_render_function, enter_hook=location_enter_hook)
        #print(f"🗺️ BaseLocation screen registered: {screen_name} -> {location_id}.{area_id}")

    def render_current_screen(self, game_state) -> bool:
        """Render the current screen
        game_state: Current game state
        Returns: True if render successful, False if failed
        """
        # Handle exploration hub mouse hover (if on exploration hub screen)
        if game_state.screen == 'exploration_hub':
            hub_manager = get_hub_manager()
            mouse_pos = pygame.mouse.get_pos()
            hub_manager.handle_mouse_move(mouse_pos)
        
        self._current_game_state = game_state
        
        if not self.current_screen:
            print("⚠️ No current screen set for rendering")
            return False
        
        if self.current_screen not in self.render_functions:
            print(f"❌ Current screen '{self.current_screen}' has no render function")
            return self._handle_render_error(game_state)
        
        try:
            # Call the screen's render function - THIS REPLACES THE ENTIRE MASSIVE METHOD
            render_function = self.render_functions[self.current_screen]
            render_result = None
            try:
               # Try with controller and capture result
                render_result = render_function(self.screen, game_state, self.fonts, self.images, self._current_game_controller)
            except TypeError:
                try:
                    # Fallback to 4 parameters and capture result
                    render_result = render_function(self.screen, game_state, self.fonts, self.images)
                except Exception as e:
                    print(f"⚠️ Error calling render function: {e}")
                    render_result = None

            # Only process combat clickables if we got a valid result
            # if self.current_screen == "combat" and isinstance(render_result, dict) and render_result:
            #     input_handler = getattr(self._current_game_controller, 'input_handler', None)
            #     if input_handler and hasattr(input_handler, 'register_combat_clickables'):
            #         input_handler.register_combat_clickables(self.current_screen, render_result)

            # Reset error count on successful render
            self.error_count = 0

            # Render overlays on top of main screen
            self._render_overlays(game_state)
            
            if self.floating_text_manager:
                try:
                    self.floating_text_manager.draw(self.screen, self.fonts)
                except Exception as floating_text_error:
                    print(f"⚠️ Floating text render error: {floating_text_error}")

            # ===== ADD DEBUG OVERLAY RENDERING HERE =====
            # Always render debug overlay last (if registered and enabled)
            if hasattr(self, 'debug_overlay_renderer') and self.debug_overlay_renderer:
                try:
                    self.debug_overlay_renderer(self.screen, self.fonts)
                except Exception as e:
                    print(f"⚠️ Debug overlay render error: {e}")
            # ===== END DEBUG OVERLAY ADDITION =====

            return True
                    
        except Exception as e:
            print(f"❌ Error rendering screen '{self.current_screen}': {e}")
            print(f"📍 Traceback: {traceback.format_exc()}")
            return self._handle_render_error(game_state)

    def _render_shopping_overlay(self, surface, game_state, fonts, images, controller):
        """Render the new tabbed shopping overlay"""
        
        
        # Create overlay instance if needed
        if not hasattr(self, '_shopping_overlay'):
            self._shopping_overlay = ShoppingOverlay(screen_manager=self)
        
        # Render the overlay
        self._shopping_overlay.render(surface, game_state, fonts, images or {})
        return True

    def sync_with_game_state(self, game_state) -> bool:
        """
        NEW: Ensure ScreenManager is synced with GameState.screen
        Call this from GameController to maintain Single Data Authority
        """
        if self.current_screen != game_state.screen:
            #print(f"🔄 Syncing ScreenManager: {self.current_screen} → {game_state.screen}")
            return self.transition_to(game_state.screen, game_state, save_history=False)
        return True
    
    def go_back(self, game_state) -> bool:
        """
        NEW: Navigate back to previous screen (like browser back button)
        """
        if self.previous_screen:
            return self.transition_to(self.previous_screen, game_state, save_history=False)
        elif self.screen_history:
            previous = self.screen_history.pop()
            return self.transition_to(previous, game_state, save_history=False)
        else:
            print("📍 No previous screen to return to")
            return False
    
    def _handle_render_error(self, game_state) -> bool:
        """
        NEW: Handle rendering errors with fallback and recovery
        """
        self.error_count += 1
        
        if self.error_count >= self.max_errors:
            print(f"💥 Too many render errors ({self.error_count}), emergency fallback")
            if self.screen:
                self.screen.fill((0, 0, 0))  # Black screen
            return False
        
        # Try to fall back to previous screen
        if self.previous_screen and self.previous_screen in self.render_functions:
            print(f"🔄 Falling back to previous screen: {self.previous_screen}")
            return self.transition_to(self.previous_screen, game_state, save_history=False)
        
        # Try fallback screen
        if self.fallback_screen in self.render_functions:
            print(f"🔄 Falling back to safe screen: {self.fallback_screen}")
            return self.transition_to(self.fallback_screen, game_state, save_history=False)
        
        # Last resort: black screen
        print("💥 No fallback available, displaying black screen")
        if self.screen:
            self.screen.fill((0, 0, 0))
        return False

    def _handle_screen_change_event(self, event_data):
        """Handle SCREEN_CHANGE events from the EventManager hub"""
        #print(f"🔄 ScreenManager: Received SCREEN_CHANGE event: {event_data}")
        
        # Support both 'target' and 'target_screen' for compatibility
        target_screen = event_data.get("target_screen") or event_data.get("target")
        source_screen = event_data.get("source_screen") or event_data.get("source")
        
        #print(f"🔄 ScreenManager: Attempting transition to '{target_screen}'")
        
        if target_screen:
            #print(f"📺 ScreenManager handling navigation: {source_screen} → {target_screen}")
            if hasattr(self, '_current_game_state'):
                success = self.transition_to(target_screen, self._current_game_state)
                if success:
                    self.event_manager.emit("SCREEN_CHANGED", {
                        "old_screen": source_screen,
                        "new_screen": target_screen
                    })
                return success
        
        print(f"🔄 ScreenManager: Transition completed")
        return False

    def _handle_screen_advance_event(self, event_data):
        """Handle SCREEN_ADVANCE events for simple navigation"""
        current_screen = event_data.get("current_screen")
        
        # Define simple advancement rules
        advance_map = {
            "game_title": "developer_splash",
            "developer_splash": "main_menu"
        }
        
        target_screen = advance_map.get(current_screen)
        if target_screen:
            #print(f"📺 ScreenManager auto-advancing: {current_screen} → {target_screen}")
            if hasattr(self, '_current_game_state'):
                return self.transition_to(target_screen, self._current_game_state)
        
        return False

    def _handle_dialogue_ended(self, event_data):
        """Handle DIALOGUE_ENDED events by returning to appropriate screen"""
        npc_id = event_data.get('npc_id')
        return_to = event_data.get('return_to', 'location')
        
        # Check if dialogue used navigate effect - if so, skip auto-return
        if hasattr(self, '_current_game_state'):
            if getattr(self._current_game_state, 'skip_dialogue_return', False):
                print(f"⏭️ Skipping auto-return (navigate effect used)")
                self._current_game_state.skip_dialogue_return = False  # Clear flag
                return True
        
        # Get the stored location context for this dialogue session
        if hasattr(self, '_current_game_state'):
            # First try to use the stored return screen (includes area suffix)
            return_screen_attr = f'{npc_id}_return_screen'
            target_screen = getattr(self._current_game_state, return_screen_attr, None)
            
            if not target_screen:
                # Fallback: use location_id (for backward compatibility with single-area locations)
                location_id = getattr(self._current_game_state, f'{npc_id}_current_location', None)
                target_screen = location_id
            
            if target_screen:
                print(f"🔙 Returning to: {target_screen}")
                source_screen = f'{npc_id}_dialogue'
                
                # Use the same event structure as other screen changes
                self.event_manager.emit("SCREEN_CHANGE", {
                    'target_screen': target_screen,
                    'source_screen': source_screen
                })
            else:
                print(f"⚠️ Warning: No stored location or return screen for {npc_id}")
        
        return True

    def _register_npc_dialogue_screens(self):
        """
        Auto-register dialogue screens from filesystem
        Follows location_npc pattern: broken_blade_garrick.json -> "broken_blade_garrick" screen
        """        
        dialogue_path = "data/dialogues/"
        registered_count = 0

        if not os.path.exists(dialogue_path):
            print(f"Warning: Dialogue directory not found: {dialogue_path}")
            return
        
        for filename in os.listdir(dialogue_path):
            if filename.endswith('.json'):
                # Extract screen name from filename
                screen_name = filename[:-5]  # Remove .json extension
                
                # Parse location_npc pattern
                if '_' in screen_name:
                    parts = screen_name.rsplit('_', 1)  # Split on LAST underscore
                    location_id = parts[0]  # "broken_blade"
                    npc_id = parts[1]       # "garrick"
                    
                    # Create render function for this specific dialogue
                    def create_dialogue_render_function(npc_id, location_id):
                        def render_dialogue(surface, game_state, fonts, images, controller=None):
                            # CRITICAL FIX: Get controller from ScreenManager if not provided
                            if not controller:
                                controller = getattr(self, '_current_game_controller', None)
                                if controller:
                                    print(f"🔧 CONTROLLER FIX: Retrieved controller from ScreenManager for {npc_id}")
                                else:
                                    print(f"⚠️ CONTROLLER MISSING: No controller available for {npc_id}")
                            
                            return draw_generic_dialogue_screen(surface, npc_id, game_state, fonts, images, controller, location_id)
                        return render_dialogue
                
                    # Register the screen (keyboard-only, no enter hook needed)
                    dialogue_render_func = create_dialogue_render_function(npc_id, location_id)
                    self.register_render_function(screen_name, dialogue_render_func)         
                            
                    registered_count += 1
                    print(f"✅ Auto-registered dialogue: {screen_name} (location: {location_id}, npc: {npc_id})")
                
                else:
                    print(f"⚠️ Skipping dialogue file with invalid naming: {filename}")
                    print(f"   Expected format: location_npc.json (e.g., broken_blade_garrick.json)")
        
        print(f"🎭 Dialogue system: {registered_count} screens auto-registered from filesystem")
        
        if registered_count == 0:
            print("⚠️ No dialogue screens registered. Check data/dialogues/ directory and file naming.")
        else:
            print("✅ Dialogue system ready - adding new NPCs now requires only JSON file creation!")

    # Method to set the current game controller
    def set_current_controller(self, controller):
        """Store reference to current game controller for dialogue screens"""
        self._current_game_controller = controller
        if controller:
            print(f"🎮 ScreenManager: Controller reference stored")
        else:
            print(f"⚠️ ScreenManager: Controller reference cleared")

    def set_game_state_context(self, game_state):
        """Set the game state context for event handling"""
        self._current_game_state = game_state

    # UTILITY METHODS
    
    def get_current_screen(self) -> Optional[str]:
        """Get the currently active screen name"""
        return self.current_screen
    
    def get_screen_history(self) -> list:
        """Get the screen navigation history"""
        return self.screen_history.copy()
    
    def is_screen_registered_for_render(self, screen_name: str) -> bool:
        """Check if a screen has a render function registered"""
        return screen_name in self.render_functions
    
    def get_registered_render_screens(self) -> list:
        """Get list of all screens with render functions"""
        return list(self.render_functions.keys())
    
    def get_credits_screen(self):
        """Get or create credits screen instance"""
        if not self.credits_screen_instance:
            from screens.credits import CreditsScreen
            self.credits_screen_instance = CreditsScreen(self.event_manager)
            print("🎞️ Credits screen instance created")
        return self.credits_screen_instance

    def get_epilogue_manager(self):
        """Get or create epilogue manager"""
        if not self.epilogue_manager:
            from screens.epilogue_slides import EpilogueSequenceManager
            self.epilogue_manager = EpilogueSequenceManager(
                self.event_manager,
                self._current_game_state
            )
            print("🎬 EpilogueSequenceManager created")
        return self.epilogue_manager
    
    def _render_credits_screen(self, surface, game_state, fonts, images, controller=None):
        """Render credits screen wrapper"""
        credits_screen = self.get_credits_screen()
        
        # Update credits scroll position (16ms = ~60fps)
        credits_screen.update(16)
        
        # Draw credits
        credits_screen.draw(surface, fonts)
        
        return {"credits_screen": credits_screen}

    def register_epilogue_slide_clickables(self, slide_id):
        """Register clickables for epilogue slides (follows intro_scenes pattern)"""
        if hasattr(self, 'input_handler') and self.input_handler:
            # Get button coordinates by rendering the slide to temp surface
            temp_surface = pygame.Surface((1024, 768))
            
            # Import the draw function based on slide_id
            from screens import epilogue_slides
            
            # Call the appropriate draw function
            if slide_id == "epilogue_slide_1":
                slide_result = epilogue_slides.draw_epilogue_slide_1(
                    temp_surface, self._current_game_state, self.fonts, self.images
                )
            elif slide_id == "epilogue_slide_2":
                slide_result = epilogue_slides.draw_epilogue_slide_2(
                    temp_surface, self._current_game_state, self.fonts, self.images
                )
            elif slide_id == "epilogue_slide_3":
                slide_result = epilogue_slides.draw_epilogue_slide_3(
                    temp_surface, self._current_game_state, self.fonts, self.images
                )
            elif slide_id == "epilogue_slide_4":
                slide_result = epilogue_slides.draw_epilogue_slide_4(
                    temp_surface, self._current_game_state, self.fonts, self.images
                )
            elif slide_id == "epilogue_slide_5":
                slide_result = epilogue_slides.draw_epilogue_slide_5(
                    temp_surface, self._current_game_state, self.fonts, self.images
                )
            elif slide_id == "epilogue_slide_6":
                slide_result = epilogue_slides.draw_epilogue_slide_6(
                    temp_surface, self._current_game_state, self.fonts, self.images
                )
            elif slide_id == "epilogue_slide_7":
                slide_result = epilogue_slides.draw_epilogue_slide_7(
                    temp_surface, self._current_game_state, self.fonts, self.images
                )
            else:
                slide_result = None
            
            if slide_result:
                # Register CONTINUE button
                self.input_handler.register_clickable(
                    slide_id, 
                    slide_result["continue_button"], 
                    "EPILOGUE_NEXT", 
                    {}
                )
                
                # Register SKIP button
                self.input_handler.register_clickable(
                    slide_id, 
                    slide_result["skip_button"], 
                    "EPILOGUE_SKIP", 
                    {}
                )
                
                print(f"🎬 Epilogue slide clickables registered: {slide_id}")
            else:
                print(f"⚠️ Could not register clickables for {slide_id}")
        else:
            print("⚠️ No InputHandler available for epilogue slide registration")

    def register_credits_clickables(self):
        """Register credits screen clickables (ESC to skip)"""
        if hasattr(self, 'input_handler') and self.input_handler:
            # Credits screen is mainly auto-scroll, ESC handled by credits screen itself
            # No specific clickables needed
            print("🎞️ Credits screen ready (ESC to skip)")
        else:
            print("⚠️ No InputHandler available for credits registration")
    
    def get_debug_info(self) -> dict:
        """Get debug information about the ScreenManager state"""
        return {
            "current_screen": self.current_screen,
            "previous_screen": self.previous_screen,
            "screen_history": self.screen_history,
            "error_count": self.error_count,
            "click_handlers_registered": len(self.screens),
            "render_functions_registered": len(self.render_functions),
            "total_screens": len(set(self.screens.keys()) | set(self.render_functions.keys()))
        }
    
    def debug_status(self):
        """Temporary debug method to see what's registered"""
        #print(f"🔍 ScreenManager Debug:")
        #print(f"   Click handlers: {len(self.screens)}")
        #print(f"   Render functions: {len(getattr(self, 'render_functions', {}))}")
        print(f"   Current screen: {getattr(self, 'current_screen', 'None')}")
        if hasattr(self, 'render_functions'):
            print(f"   Registered renders: {list(self.render_functions.keys())}")
    
    def set_debug_overlay_renderer(self, renderer_function):
        """Register debug overlay renderer to be called on every screen"""
        self.debug_overlay_renderer = renderer_function
        print("🔧 Debug overlay renderer registered")

    def set_floating_text_manager(self, floating_text_manager):
        """Attach a floating text manager for universal notifications."""
        self.floating_text_manager = floating_text_manager
        
    def register_overlay_events(self):
        """Register ScreenManager as the proper overlay coordinator"""
        if self.event_manager:
            self.event_manager.register("OVERLAY_TOGGLE", self._handle_overlay_toggle)
            #print("📺 ScreenManager registered for overlay management")

    def _handle_overlay_toggle(self, event_data):
        """Handle overlay toggle - Centralized state management"""
        overlay_id = event_data.get("overlay_id")
        
        # Initialize overlay state if not exists
        if not hasattr(self._current_game_state, 'overlay_state'):
            self._current_game_state.overlay_state = OverlayState()
        overlay_state = self._current_game_state.overlay_state
        
        # Special handling for load/save screens (need clickable registration)
        if overlay_id == "load_game":
            if overlay_state.is_open("load_game"):
                overlay_state.close_overlay()
            else:
                overlay_state.open_overlay("load_game")
                self.register_load_screen_clickables()
            return

        if overlay_id == "save_game":
            if overlay_state.is_open("save_game"):
                overlay_state.close_overlay()
            else:
                overlay_state.open_overlay("save_game")
                self.register_save_screen_clickables()
            return
        
        # Universal overlay handling with centralized state
        if overlay_state.is_open(overlay_id):
            overlay_state.close_overlay()
            #print(f"📋 ScreenManager: {overlay_id} closed")
        else:
            overlay_state.open_overlay(overlay_id)
            #print(f"📋 ScreenManager: {overlay_id} opened")

    def _render_overlays(self, game_state):
        """Render any active overlays on top of the main screen"""
        # SELECTIVE OVERLAY RESTRICTIONS  
        if game_state.screen == 'main_menu':
            # Main menu: ONLY allow load_game overlay
            if hasattr(game_state, 'overlay_state'):
                active = game_state.overlay_state.get_active_overlay()
                if active and active != 'load_game':
                    return
                    
        elif game_state.screen in OVERLAY_RESTRICTED_SCREENS:
            # All other restricted screens: Block ALL overlays
            return
        
       # Get active overlay from unified state
        if hasattr(game_state, 'overlay_state'):
            active_overlay_id = game_state.overlay_state.get_active_overlay()
            
            if active_overlay_id:
                # Render based on overlay type
                if active_overlay_id == "load_game":
                    
                    save_manager = None
                    if hasattr(self, '_current_game_controller') and self._current_game_controller:
                        save_manager = getattr(self._current_game_controller, 'save_manager', None)
                    draw_load_game_screen(self.screen, game_state, self.fonts, self.images, save_manager)
                    self.register_load_screen_clickables()
                elif active_overlay_id == "save_game":
                    save_manager = None
                    if hasattr(self, '_current_game_controller') and self._current_game_controller:
                        save_manager = getattr(self._current_game_controller, 'save_manager', None)
                    draw_save_game_screen(self.screen, game_state, self.fonts, self.images, save_manager)
                    self.register_save_screen_clickables()
                elif active_overlay_id == "inventory_key":
                    draw_inventory_screen(self.screen, game_state, self.fonts, self.images)
                elif active_overlay_id == "quest_key":
                    draw_quest_overlay(self.screen, game_state, self.fonts, self.images)
                elif active_overlay_id == "character_key":
                    draw_character_sheet_screen(self.screen, game_state, self.fonts, self.images)
                elif active_overlay_id == "help_key":
                    draw_help_screen(self.screen, game_state, self.fonts, self.images)
                elif active_overlay_id == "statistics_key":
                    draw_statistics_screen(self.screen, game_state, self.fonts, self.images)
                elif active_overlay_id == "statistics_key":
                    draw_statistics_screen(self.screen, game_state, self.fonts, self.images)
                elif active_overlay_id == "combat_loot":
                    draw_combat_loot_screen(self.screen, game_state, self.fonts, self.images)
        
        # DEATH OVERLAY (special - always renders on top if active)
        if getattr(game_state, 'death_overlay_active', False):
            
            
            if not hasattr(self, '_death_overlay'):
                self._death_overlay = create_death_overlay()
            
            # Get the pre-generated quote from game_state
            death_quote = getattr(game_state, 'death_quote', '')
            character_name = game_state.character.get('name', 'Unknown Hero')
            
            # Only show if not already showing
            if not self._death_overlay.active:
                self._death_overlay.show(character_name, death_quote)
            
            death_buttons = self._death_overlay.render(self.screen, self.fonts)
            
            # Register death overlay buttons with correct signature
            if death_buttons and hasattr(self, 'input_handler'):
                # Get current screen name
                current_screen = getattr(game_state, 'screen', 'combat')
                
                for button_name, button_rect in death_buttons.items():
                    # Determine event type based on button
                    if button_name == 'load_game':
                        event_type = "DEATH_ACTION_LOAD_GAME"
                    elif button_name == 'restart_combat':
                        event_type = "DEATH_ACTION_RESTART_COMBAT"
                    elif button_name == 'return_to_title':
                        event_type = "DEATH_ACTION_RETURN_TO_TITLE"
                    else:
                        continue
                    
                    # Register with correct signature
                    self.input_handler.register_clickable(
                        screen_name=current_screen,
                        rect=button_rect,
                        event_type=event_type,
                        event_data={'button': button_name},
                        priority=100  # High priority - overlay on top
                    )
