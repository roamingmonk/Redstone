# ui/screen_manager.py
"""
Screen Manager - Enhanced Generic Screen Handling System
BUILDING ON YOUR EXISTING CODE - Enhanced to handle full screen lifecycle
Replaces hardcoded screen logic with data-driven approach + massive draw_current_screen elimination
"""

from typing import Dict, Callable, Any, Optional
import pygame
import traceback

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
        # EXISTING: Your original click handling system
        self.event_manager = event_manager
        self.screens = {}  # screen_name -> screen_handler (click handlers)
        
        # NEW: Full screen rendering system
        self.screen = screen  # pygame display surface
        self.fonts = fonts    # font dictionary
        self.images = images  # image dictionary
        
        # NEW: Screen render function registry
        self.render_functions = {}  # screen_name -> render_function
        self.enter_hooks = {}       # screen_name -> enter_function
        self.exit_hooks = {}        # screen_name -> exit_function
        
        # NEW: Screen state tracking
        self.current_screen = None
        self.previous_screen = None
        self.screen_history = []
        
        #Error handling
        self.fallback_screen = "main_menu"
        self.error_count = 0
        self.max_errors = 3
                
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
            # Register direct navigation events
            # This direct system is simple and not the same input system as subsequent screens
            # Plan to use the screen manager route map for more complex flows
            event_manager.register("START_GAME", self._handle_direct_navigation)
            event_manager.register("CONTINUE", self._handle_direct_navigation)
            event_manager.register("LOAD_GAME", self._handle_load_game)
            event_manager.register("REGISTER_FULL_SCREEN_CLICK", self._handle_full_screen_registration)
            print("📺 ScreenManager subscribed to navigation events")

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
        """Handle LOAD_GAME - open load overlay and register clickables"""
        print("📂 ScreenManager: Opening load screen")
        if hasattr(self, '_current_game_state'):
            self._current_game_state.load_screen_open = True
            # Register clickables when opening
            self.register_load_screen_clickables()


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
        
        # Import your existing main menu handler
        from ui.screen_handlers import handle_main_menu_clicks
        
        # Register all basic handlers
        self.register_screen("game_title", handle_title_click)
        self.register_screen("developer_splash", handle_developer_splash_click)
        self.register_screen("main_menu", handle_main_menu_clicks)
        
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
    
    # ========================================
    # NEW METHODS - SCREEN RENDERING SYSTEM
    # ========================================

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
            
            print("🚹🚺 Gender screen clickables registered")
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
            
            # Button coordinates from draw_name_confirm_screen  
            button_y = 280
            
            # CONFIRM button (350, 280, 160, 50)
            confirm_rect = pygame.Rect(350, button_y, 160, 50)
            self.input_handler.register_clickable('name_confirm', confirm_rect, 'ACCEPT_NAME', {'action': 'ACCEPT_NAME'})
            
            # BACK button (550, 280, 160, 50)
            back_rect = pygame.Rect(550, button_y, 160, 50)
            self.input_handler.register_clickable('name_confirm', back_rect, 'BACK_TO_NAME_SELECTION', {'action': 'BACK_TO_NAME_SELECTION'})
            
            print("✅ Name confirm screen clickables registered")
        else:
            print("⚠️ No InputHandler available for name confirm screen registration")
    
    def register_portrait_screen_clickables(self):
        """Register portrait screen clickables when entering portrait screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Use exact coordinates from draw_portrait_selection_screen
            from utils.constants import LAYOUT_IMAGE_Y, LAYOUT_BUTTON_CENTER_Y
            
            portrait_size = 110
            total_width = 5 * portrait_size + 4 * 20  # 5 portraits + 4 gaps of 20px
            start_x = (1024 - total_width) // 2  # Center the row
            portrait_y = LAYOUT_IMAGE_Y + 100  # Same as draw function
            
            # Register each portrait clickable (1-5)
            for i in range(5):
                portrait_x = start_x + i * (portrait_size + 20)
                portrait_rect = pygame.Rect(portrait_x, portrait_y, portrait_size, portrait_size)
                action_name = f'SELECT_PORTRAIT_{i+1}'  # 1-5 for semantic actions
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
            
            print("🖼️ Portrait selection screen clickables registered (5 portraits + 2 buttons)")
        else:
            print("⚠️ No InputHandler available for portrait screen registration")

    def register_gold_screen_clickables(self):
        """Register gold screen clickables when entering gold screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Button coordinates from draw_gold_screen (450, 280, 160, 50)
            button_rect = pygame.Rect(450, 280, 160, 50)
            
            # Register the single button - logic will be handled by CharacterEngine
            self.input_handler.register_clickable('gold', button_rect, 'GOLD_BUTTON_CLICK', {'action': 'GOLD_BUTTON_CLICK'})
            
            print("🪙 Gold screen clickables registered")
        else:
            print("⚠️ No InputHandler available for gold screen registration")

    def register_trinket_screen_clickables(self):
        """Register trinket screen clickables when entering trinket screen"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Button coordinates from draw_trinket_screen (450, 280, 160, 50 - same as gold)
            button_rect = pygame.Rect(450, 280, 160, 50)
            
            # Register the button - CharacterEngine will determine if it's ROLL or CONTINUE
            self.input_handler.register_clickable('trinket', button_rect, 'TRINKET_BUTTON_CLICK', {'action': 'TRINKET_BUTTON_CLICK'})
            
            print("🎭 Trinket screen clickables registered")
        else:
            print("⚠️ No InputHandler available for trinket screen registration")

    def register_summary_screen_clickables(self, game_state):
        """Register clickable regions for summary screen using semantic actions"""
        print("🎯 Registering summary screen clickables")
        
       # Get the START GAME button coordinates from the draw function
        temp_surface = pygame.Surface((1024, 768))
        from screens.character_creation import draw_summary_screen
        
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
            print(f"✅ START GAME button registered at {start_button}")
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
                from screens.intro_scenes import draw_intro_scene_1
                scene_result = draw_intro_scene_1(temp_surface, None, self.fonts, self.images)
            elif scene_id == "intro_scene_2":
                from screens.intro_scenes import draw_intro_scene_2
                scene_result = draw_intro_scene_2(temp_surface, None, self.fonts, self.images)
            elif scene_id == "intro_scene_3":
                from screens.intro_scenes import draw_intro_scene_3
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

    def register_load_screen_clickables(self):
        """Register load screen clickables when load overlay opens"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Get button coordinates from the draw function
            temp_surface = pygame.Surface((1024, 768))
            from screens.load_game import draw_load_game_screen
            
            # Get save_manager from game_controller
            save_manager = None
            if hasattr(self, '_current_game_controller') and self._current_game_controller:
                save_manager = getattr(self._current_game_controller, 'save_manager', None)
            
            print(f"🔍 DEBUG: save_manager = {save_manager}")
            print(f"🔍 DEBUG: _current_game_controller = {getattr(self, '_current_game_controller', 'NOT SET')}")

            result = draw_load_game_screen(
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
                        'load_overlay', 
                        slot_rect, 
                        'LOAD_SLOT_SELECTED', 
                        {'slot_num': slot_num}
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
                self.input_handler.register_clickable('load_overlay', button_rect, event_type, {})
                
                print("🔍 Load screen clickables registered")
            else:
                print("⚠️ Could not get load screen button coordinates")
        else:
            print("⚠️ No InputHandler available for load screen registration")

    def register_stats_confirm_low_clickables(self):
        """Register low stats confirmation clickables"""
        if hasattr(self, 'input_handler') and self.input_handler:
            
            # Only register normal warning screen buttons
            reroll_rect = pygame.Rect(300, 280, 160, 50)
            self.input_handler.register_clickable('stats_confirm_low', reroll_rect, 'REROLL_FROM_CONFIRM', {})
            
            proceed_rect = pygame.Rect(500, 280, 160, 50)
            self.input_handler.register_clickable('stats_confirm_low', proceed_rect, 'PROCEED_WITH_LOW_STATS', {})
            
            print("⚠️ Low stats confirmation clickables registered")

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
                draw_stats_screen, draw_gender_screen, draw_portrait_selection_screen,
                draw_name_screen, draw_custom_name_screen, draw_name_confirm_screen,
                draw_gold_screen, draw_trinket_screen, draw_summary_screen, 
                draw_stats_confirm_low_screen
            )
            
            from screens.intro_scenes import (
                draw_intro_scene_1, draw_intro_scene_2, draw_intro_scene_3
            )

            from screens.broken_blade import draw_broken_blade_main_screen
            from screens.patron_selection import draw_patron_selection_screen  
            from screens.shopping import draw_merchant_screen
            from screens.inventory import draw_inventory_screen
            from screens.quest_log import draw_quest_log_screen
            from screens.character_sheet import draw_character_sheet_screen
            from screens.help_screen import draw_help_screen
            from screens.gambling_dice import (
                draw_dice_bets_screen, draw_dice_rolling_screen,
                draw_dice_results_screen, draw_dice_rules_screen
            )
            
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



            

            #Broken Blade Tavern
            self.register_render_function("broken_blade_main", draw_broken_blade_main_screen)
            self.register_render_function("patron_selection", draw_patron_selection_screen)

            # Utility screens
            self.register_render_function("merchant", draw_merchant_screen)
            self.register_render_function("inventory", draw_inventory_screen)
            self.register_render_function("quest_log", draw_quest_log_screen)
            self.register_render_function("character_sheet", draw_character_sheet_screen)
            self.register_render_function("help", draw_help_screen)
            
            # Gambling mini-game screens
            self.register_render_function("dice_bets", draw_dice_bets_screen)
            self.register_render_function("dice_rolling", draw_dice_rolling_screen)
            self.register_render_function("dice_results", draw_dice_results_screen)
            self.register_render_function("dice_rules", draw_dice_rules_screen)
            
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
        
        print(f"🔄 Screen transition: {old_screen} → {screen_name}")
        return True
    
    def render_current_screen(self, game_state) -> bool:
        """
        NEW: Render the current screen
        This REPLACES the massive 1700-line draw_current_screen() method!
        
        Args:
            game_state: Current game state
            
        Returns:
            True if render successful, False if failed
        """
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
            render_function(self.screen, game_state, self.fonts, self.images)
            
            # Reset error count on successful render
            self.error_count = 0

            # NEW: Render overlays on top of main screen
            self._render_overlays(game_state)

            return True
                    
        except Exception as e:
            print(f"❌ Error rendering screen '{self.current_screen}': {e}")
            print(f"📍 Traceback: {traceback.format_exc()}")
            return self._handle_render_error(game_state)
    
    def sync_with_game_state(self, game_state) -> bool:
        """
        NEW: Ensure ScreenManager is synced with GameState.screen
        Call this from GameController to maintain Single Data Authority
        """
        if self.current_screen != game_state.screen:
            print(f"🔄 Syncing ScreenManager: {self.current_screen} → {game_state.screen}")
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
        print(f"🔄 ScreenManager: Received SCREEN_CHANGE event: {event_data}")
        
        # Support both 'target' and 'target_screen' for compatibility
        target_screen = event_data.get("target_screen") or event_data.get("target")
        source_screen = event_data.get("source_screen") or event_data.get("source")
        
        print(f"🔄 ScreenManager: Attempting transition to '{target_screen}'")
        
        if target_screen:
            print(f"📺 ScreenManager handling navigation: {source_screen} → {target_screen}")
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
            print(f"📺 ScreenManager auto-advancing: {current_screen} → {target_screen}")
            if hasattr(self, '_current_game_state'):
                return self.transition_to(target_screen, self._current_game_state)
        
        return False

    def set_game_state_context(self, game_state):
        """Set the game state context for event handling"""
        self._current_game_state = game_state

    # ========================================
    # UTILITY METHODS
    # ========================================
    
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
        print(f"🔍 ScreenManager Debug:")
        print(f"   Click handlers: {len(self.screens)}")
        print(f"   Render functions: {len(getattr(self, 'render_functions', {}))}")
        print(f"   Current screen: {getattr(self, 'current_screen', 'None')}")
        if hasattr(self, 'render_functions'):
            print(f"   Registered renders: {list(self.render_functions.keys())}")

    def register_overlay_events(self):
        """Register ScreenManager as the proper overlay coordinator"""
        if self.event_manager:
            self.event_manager.register("OVERLAY_TOGGLE", self._handle_overlay_toggle)
            print("📺 ScreenManager registered for overlay management")

    def _handle_overlay_toggle(self, event_data):
        """Handle overlay toggle - ScreenManager owns overlay lifecycle"""
        overlay_id = event_data.get("overlay_id")
        
        if overlay_id == "load_game":
            # Toggle load screen state
            current_state = getattr(self._current_game_state, 'load_screen_open', False)
            self._current_game_state.load_screen_open = not current_state
            
            # Register clickables when opening
            if self._current_game_state.load_screen_open:
                self.register_load_screen_clickables()
            
            print(f"📂 ScreenManager: Load screen {'opened' if self._current_game_state.load_screen_open else 'closed'}")
        
        # TODO: Add other overlays (inventory, quest_log, etc.) here as we modernize them

    def _render_overlays(self, game_state):
        """Render any active overlays on top of the main screen"""
        # Load screen overlay
        if getattr(game_state, 'load_screen_open', False):
            from screens.load_game import draw_load_game_screen
            
            # Get save_manager from game_controller
            save_manager = None
            if hasattr(self, '_current_game_controller') and self._current_game_controller:
                save_manager = getattr(self._current_game_controller, 'save_manager', None)
            
            # Use SaveManager's GameState (the one that actually gets updated)
            if save_manager:
                draw_load_game_screen(self.screen, save_manager.game_state, self.fonts, self.images, save_manager)
            else:
                draw_load_game_screen(self.screen, game_state, self.fonts, self.images, save_manager)
        # Add other overlays here as needed
        # if getattr(game_state, 'inventory_open', False):
        #     from screens.inventory import draw_inventory_screen
        #     draw_inventory_screen(self.screen, game_state, self.fonts, self.images)