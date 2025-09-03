# core/game_controller.py
"""
Professional Game Controller Infrastructure
Centralized management for screen transitions, input handling, and game state
"""

import pygame
import sys
import json
import os
from game_logic.data_manager import get_data_manager, initialize_game_data
from game_logic.character_engine import initialize_character_engine 
from game_logic.inventory_engine import initialize_inventory_engine 
from game_logic.commerce_engine import initialize_commerce_engine 
from game_logic.dialogue_engine import initialize_dialogue_engine
from game_logic.event_manager import initialize_event_manager, get_event_manager
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from utils.constants import *

#from utils.graphics import draw_error_screen   will create later

class GameController:
    """
    Master game controller handling screen management, transitions, and universal input
    This is the 'conductor' that orchestrates all game systems
    """
    def __init__(self, screen: pygame.Surface, game_state, fonts: Dict, images: Dict, data_manager):
        self.screen = screen
        self.game_state = game_state
        self.data_manager = data_manager
        self.fonts = fonts
        self.images = images
        self.event_manager = None

        # Screen registry - maps screen names to their functions
        self.screens: Dict[str, Callable] = {}
        
        # Current screen state
        self.previous_screen = None
        self.screen_history = []
        
        # Universal input state
        self.universal_keys_enabled = True
        self.escape_exits_game = True
        
        self._update_universal_keys_state()
        print("🎮 Game Controller initialized - Professional infrastructure ready!")

        # Set initial universal key state
        self._update_universal_keys_state()

        # Error recovery system
        self.last_known_good_screen = "game_title"
        self.error_count = 0
        
        # Debug/development features
        self.debug_mode = False
        self.frame_count = 0
        self.last_fps_time = pygame.time.get_ticks()
        
        # Save/load system state
        self.last_save_time = None
        self.last_load_time = None

    def initialize_data_systems(self) -> bool:
        """
        Initializes and loads all game data and engines.
        Called during GameController startup
        """
        print("🎮 GameController: Initializing data management systems...")
    
        try:
            print("📊 GameController: Beginning core system initialization...")
            
            # Step 1: Load all data first
            self.data_manager.load_all_data()
            
            # Step 2: Initialize all engines directly in GameController
            self.character_engine = initialize_character_engine(self.game_state)
            self.inventory_engine = initialize_inventory_engine(self.game_state, self.data_manager.item_manager)
            self.commerce_engine = initialize_commerce_engine(self.game_state, self.data_manager.item_manager) 
            self.dialogue_engine = initialize_dialogue_engine(self.game_state)
                        
            self.data_manager.dialogue_engine = self.dialogue_engine
            
            # Step 3: Initialize EventManager directly
            self.event_manager = initialize_event_manager()
            
            # Step 4: Set up event listeners now that everything exists
            self.setup_event_listeners()
            
            print("✅ GameController: All systems initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ GameController: Data initialization failed: {e}")
            self.error_count += 1
            return False


    def setup_event_listeners(self):
        """Initialize all event listeners for professional event-driven architecture"""
        print("🎯 GC Setting up event listeners...")
        
        # Use the event manager we initialized directly in GameController
        event_manager = self.event_manager  # Direct access, no DataManager needed
        print(f"DEBUG: GC event_manager = {event_manager}")  # Add this line
        # Register NPC click handler
        event_manager.register("NPC_CLICKED", self.handle_npc_clicked)
        
        # Register screen change handler
        event_manager.register("SCREEN_CHANGE", self.handle_screen_change)
        
        # Initialize Screen Manager
        from ui.screen_manager import ScreenManager
        from ui.screen_handlers import handle_broken_blade_clicks
        #from ui.generic_dialogue_handler import register_npc_dialogue_screen
        #register_npc_dialogue_screen(self.screen_manager, 'garrick')
        
        self.screen_manager = ScreenManager(event_manager)
        print(f"DEBUG: GC screen_manager created with {self.screen_manager.event_manager}")
        self.screen_manager.register_screen("broken_blade_main", handle_broken_blade_clicks)
        
        print("✅ Event listeners registered successfully!")

    def handle_npc_clicked(self, event_data): #data: Dict[str, Any]): 
        """
        Handle NPC click events - replacement for hardcoded click detection
        
        Args:
            event_data: Dictionary with npc_id, location, and other context
        """
        npc_id = event_data.get("npc_id")
        location = event_data.get("location")

        print(f"🎭 EVENT: NPC '{npc_id}' clicked at '{location}'")
        
        # Use screen manager events instead of direct transition_to calls
        screen_name = f"{npc_id}_dialogue"
        self.event_manager.emit("SCREEN_CHANGE", {
            "target_screen": screen_name,
            "source_screen": self.game_state.screen
        })


    def handle_screen_change(self, event_data):
        """Handle screen transition events - SCREEN MANAGER ONLY"""
        target_screen = event_data.get("target_screen")
        source_screen = event_data.get("source_screen")
        
        print(f"🔄 SCREEN_CHANGE: {source_screen} -> {target_screen}")
        
        if target_screen:
            if hasattr(self, 'screen_manager') and target_screen in self.screen_manager.get_registered_screens():
                # Update game state - screen manager will handle drawing
                self.game_state.screen = target_screen
                print(f"✅ Screen registered: {target_screen}")
            else:
                # FORCE the issue - no fallback
                print(f"❌ UNREGISTERED SCREEN: {target_screen}")
                print(f"   Available screens: {self.screen_manager.get_registered_screens()}")
                print("   This screen needs to be registered with the screen manager!")
                # Stay on current screen instead of crashing
                return
        else:
            print("⚠️ SCREEN_CHANGE event without target_screen")

    def is_text_input_active(self) -> bool:
        """NEW METHOD - Check if we're in text input mode"""
        return (self.game_state.screen == "custom_name" and 
                hasattr(self.game_state, 'custom_name_active') and 
                self.game_state.custom_name_active)

    def handle_input(self, event) -> bool:
            """
            ENHANCED VERSION - Master input handler 
            This replaces your current incomplete version
            """
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                return self.handle_keyboard_input_enhanced(event)  # Pass full event
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return self.handle_mouse_input_enhanced(event.pos)  # Enhanced mouse handling
            
            return True

    def handle_text_input(self, event) -> bool:
        """NEW METHOD - Handle custom name text input (from main.py)"""
        if self.game_state.screen == "custom_name" and self.game_state.custom_name_active:
            if event.key == pygame.K_RETURN:
                if self.game_state.custom_name_text.strip():
                    self.game_state.selected_name = self.game_state.custom_name_text.strip()
                    self.transition_to("name_confirm")  # Use your existing transition_to!
                return True
                
            elif event.key == pygame.K_BACKSPACE:
                self.game_state.custom_name_text = self.game_state.custom_name_text[:-1]
                return True
                
            else:
                if len(self.game_state.custom_name_text) < 30 and event.unicode.isprintable():
                    self.game_state.custom_name_text += event.unicode
                return True
        
        return True
 
    def handle_screen_specific_input(self, event) -> bool:
        """NEW METHOD - Handle screen-specific keyboard input (from main.py)"""
        
        # Game title screen
        if event.key == pygame.K_RETURN and self.game_state.screen == "game_title":
            self.transition_to("developer_splash")  # Use your existing transition_to!
            return True
        
        # Developer splash screen
        elif self.game_state.screen == "developer_splash":
            self.transition_to("main_menu")  # Use your existing transition_to!
            return True
        
        return True

    def is_text_input_active(self) -> bool:
        """NEW METHOD - Check if we're in text input mode"""
        return (self.game_state.screen == "custom_name" and 
                hasattr(self.game_state, 'custom_name_active') and 
                self.game_state.custom_name_active)

    def handle_text_input(self, event) -> bool:
        """NEW METHOD - Handle custom name text input (from main.py)"""
        if self.game_state.screen == "custom_name" and self.game_state.custom_name_active:
            if event.key == pygame.K_RETURN:
                if self.game_state.custom_name_text.strip():
                    self.game_state.selected_name = self.game_state.custom_name_text.strip()
                    self.transition_to("name_confirm")  # Use your existing transition_to!
                return True
                
            elif event.key == pygame.K_BACKSPACE:
                self.game_state.custom_name_text = self.game_state.custom_name_text[:-1]
                return True
                
            else:
                if len(self.game_state.custom_name_text) < 30 and event.unicode.isprintable():
                    self.game_state.custom_name_text += event.unicode
                return True
        
        return True

    def handle_screen_specific_input(self, event) -> bool:
        """NEW METHOD - Handle screen-specific keyboard input (from main.py)"""
        
        # Game title screen
        if event.key == pygame.K_RETURN and self.game_state.screen == "game_title":
            self.transition_to("developer_splash")  # Use your existing transition_to!
            return True
        
        # Developer splash screen
        elif self.game_state.screen == "developer_splash":
            self.transition_to("main_menu")  # Use your existing transition_to!
            return True
        
     # Add other screen-specific handlers here as needed

        return True

    def handle_overlay_mouse_clicks(self, mouse_pos) -> bool:
        """NEW METHOD - All overlay click handling (from main.py)"""
        
       
        # Help screen overlay
        if self.game_state.help_screen_open:
            temp_surface = pygame.Surface((1024, 768))
            from screens.help_screen import draw_help_screen
            result = draw_help_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if result:
                return_rect = result
                if return_rect and return_rect.collidepoint(mouse_pos):
                    self.game_state.help_screen_open = False
            
            return True  # Block other clicks

        # Character sheet screen overlay
        if self.game_state.character_sheet_open:
            temp_surface = pygame.Surface((1024, 768))
            from screens.character_sheet import draw_character_sheet_screen
            result = draw_character_sheet_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if result:
                return_rect = result
                if return_rect and return_rect.collidepoint(mouse_pos):
                    self.game_state.character_sheet_open = False
            
            return True  # Block other clicks
  
        # Quest log Screen overlay
        if self.game_state.quest_log_open:
            temp_surface = pygame.Surface((1024, 768))
            from screens.quest_log import draw_quest_log_screen
            result = draw_quest_log_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if result and len(result) == 2:
                quest_rects, return_rect = result
                
                # Handle quest selection clicks
                for i, quest_rect in enumerate(quest_rects):
                    if quest_rect.collidepoint(mouse_pos):
                        # Handle quest selection clicks
                        for i, quest_rect in enumerate(quest_rects):
                            if quest_rect.collidepoint(mouse_pos):
                                # Get the quest ID from the available quests
                                from screens.quest_log import get_available_quests
                                quests = get_available_quests(self.game_state)
                                if i < len(quests):
                                    selected_quest_id = quests[i]['id']
                                    # Toggle selection
                                    if self.game_state.selected_quest == selected_quest_id:
                                        self.game_state.selected_quest = None
                                    else:
                                        self.game_state.selected_quest = selected_quest_id
                                break
                
                # Handle close button
                if return_rect and return_rect.collidepoint(mouse_pos):
                    self.game_state.quest_log_open = False
                    self.game_state.selected_quest = None
            return True  # Block other clicks

        # Inventory screen overlay
        if self.game_state.inventory_open:
            temp_surface = pygame.Surface((1024, 768))
            from screens.inventory import draw_inventory_screen
            result = draw_inventory_screen(temp_surface, self.game_state, self.fonts, self.images)

            if result and len(result) == 4:
                tab_rects, button_rects, item_rects, item_names_in_order = result
                weapons_tab, armor_tab, items_tab, consumables_tab = tab_rects
                
                # Handle tab clicks
                if weapons_tab.collidepoint(mouse_pos):
                    self.game_state.inventory_tab = "weapons"
                    self.game_state.inventory_selected = None
                elif armor_tab.collidepoint(mouse_pos):
                    self.game_state.inventory_tab = "armor"
                    self.game_state.inventory_selected = None
                elif items_tab.collidepoint(mouse_pos):
                    self.game_state.inventory_tab = "items"
                    self.game_state.inventory_selected = None
                elif consumables_tab.collidepoint(mouse_pos):
                    self.game_state.inventory_tab = "consumables"
                    self.game_state.inventory_selected = None
                
                # Handle item selection clicks
                else:
                    for i, item_rect in enumerate(item_rects):
                        if item_rect.collidepoint(mouse_pos):
                            if i < len(item_names_in_order):
                                selected_item = item_names_in_order[i]
                                # Toggle selection
                                if self.game_state.inventory_selected == selected_item:
                                    self.game_state.inventory_selected = None
                                else:
                                    self.game_state.inventory_selected = selected_item
                                break

                # Handle button clicks
                if self.game_state.inventory_tab in ["weapons", "armor"]:
                    equip_btn, unequip_btn, discard_btn, return_btn = button_rects
                    
                    if return_btn and return_btn.collidepoint(mouse_pos):
                        self.game_state.inventory_open = False
                    elif equip_btn and equip_btn.collidepoint(mouse_pos):
                        if self.game_state.inventory_selected:
                            self.game_state.equip_item(self.game_state.inventory_selected, self.game_state.inventory_tab)
                            self.game_state.inventory_selected = None  # Clear selection after equipping
                    elif unequip_btn and unequip_btn.collidepoint(mouse_pos):
                        if self.game_state.inventory_selected:
                            self.game_state.unequip_item(self.game_state.inventory_selected)
                            self.game_state.inventory_selected = None  # Clear selection after unequipping
                    elif discard_btn and discard_btn.collidepoint(mouse_pos):
                        if self.game_state.inventory_selected:
                            self.game_state.discard_item(self.game_state.inventory_selected)
                            self.game_state.inventory_selected = None
                            return True # exit immediately after discard to prevent invalid button usage.
                        
                elif self.game_state.inventory_tab == "consumables":
                    consume_btn, discard_btn, return_btn, _ = button_rects
                    
                    if return_btn and return_btn.collidepoint(mouse_pos):
                        self.game_state.inventory_open = False
                    elif consume_btn and consume_btn.collidepoint(mouse_pos):
                        if self.game_state.inventory_selected:
                            self.game_state.consume_item(self.game_state.inventory_selected)
                            self.game_state.inventory_selected = None
                    elif discard_btn and discard_btn.collidepoint(mouse_pos):
                        if self.game_state.inventory_selected:
                            self.game_state.discard_item(self.game_state.inventory_selected)
                            self.game_state.inventory_selected = None
                            return True

                else:  # items tab
                    discard_btn, return_btn, _, _ = button_rects
                    
                    if return_btn and return_btn.collidepoint(mouse_pos):
                        self.game_state.inventory_open = False
                    elif discard_btn and discard_btn.collidepoint(mouse_pos):
                        if self.game_state.inventory_selected:
                            self.game_state.discard_item(self.game_state.inventory_selected)
                            self.game_state.inventory_selected = None
                        
            return True  # Don't process other clicks when inventory is open

        # Load screen handling overlay
        if self.game_state.load_screen_open:
            from screens.load_game import draw_load_game_screen, handle_load_game_click
            temp_surface = pygame.Surface((1024, 768))
            result = draw_load_game_screen(temp_surface, self.game_state, self.fonts, self.images, controller=self)
            handle_load_game_click(mouse_pos, self.game_state, result, controller=self)
            return True

        # Save screen handling overlay
        if self.game_state.save_screen_open:
            from screens.save_game import draw_save_game_screen, handle_save_game_click
            temp_surface = pygame.Surface((1024, 768))
            result = draw_save_game_screen(temp_surface, self.game_state, self.fonts, self.images, controller=self)
            handle_save_game_click(mouse_pos, self.game_state, result, controller=self)
            return True

        # Character advancement overlay handling 
        if getattr(self.game_state, 'character_advancement_open', False):
            from screens.character_advancement import draw_character_advancement, handle_character_advancement_click
            temp_surface = pygame.Surface((1024, 768))
            result = draw_character_advancement(temp_surface, self.game_state, self.fonts, controller=self)
            if handle_character_advancement_click(mouse_pos, result, self.game_state, controller=self):
                return True

        return False  # No overlays handled

    def handle_screen_mouse_clicks(self, mouse_pos) -> bool:
        """NEW METHOD - Screen-specific mouse handling framework"""
        # This is where screen-specific mouse logic goes

        # GAME TITLE - click to go to developer splash
        if self.game_state.screen == "game_title":
            self.transition_to("developer_splash")
            return True

        # DEVELOPER SPLASH - click to go to main menu
        elif self.game_state.screen == "developer_splash":
            self.transition_to("main_menu")
            return True
    
        # Main menu
        elif self.game_state.screen == "main_menu":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.title_menu import draw_main_menu
            new_game_btn, load_game_btn, quit_btn = draw_main_menu(temp_surface, self.game_state, self.fonts, self.images)
            
            if new_game_btn.collidepoint(mouse_pos):
                self.game_state.activate_character_portrait()
                self.transition_to("stats")  # Start character creation

            elif load_game_btn.collidepoint(mouse_pos):
                 self.game_state.load_screen_open = True
                
            elif quit_btn.collidepoint(mouse_pos):
                return False  # Quit game

        # Stats screen
        elif self.game_state.screen == "stats":
            # We need to call the draw function to get button positions
            # This is a bit of a hack, but it works for our simple system
            pygame.Surface((1, 1))  # Dummy surface
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_stats_screen
            roll_button, keep_button = draw_stats_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if roll_button.collidepoint(mouse_pos):
                from game_logic.character_engine import get_character_engine
                engine = get_character_engine()
                if engine:
                    engine.roll_stats(reroll_ones=True)
                    # Copy engine results to temp_stats for UI display
                    self.game_state.temp_stats = {
                        'strength': self.game_state.character.get('strength', 0),
                        'dexterity': self.game_state.character.get('dexterity', 0), 
                        'constitution': self.game_state.character.get('constitution', 0),
                        'intelligence': self.game_state.character.get('intelligence', 0),
                        'wisdom': self.game_state.character.get('wisdom', 0),
                        'charisma': self.game_state.character.get('charisma', 0)
                    }
                    self.game_state.stats_rolled = True
            
            if keep_button and keep_button.collidepoint(mouse_pos):
                self.game_state.character.update(self.game_state.temp_stats)
                self.transition_to("gender")
        
        # Gender screen
        elif self.game_state.screen == "gender":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_gender_screen
            male_button, female_button = draw_gender_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if male_button.collidepoint(mouse_pos):
                self.game_state.character['gender'] = 'male'
                self.game_state.current_names = self.game_state.get_random_names('male')
                self.transition_to("portrait_selection")
            
            if female_button.collidepoint(mouse_pos):
                self.game_state.character['gender'] = 'female'
                self.game_state.current_names = self.game_state.get_random_names('female')
                self.transition_to("portrait_selection")
        
        # Portrait selection screen
        elif self.game_state.screen == "portrait_selection":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_portrait_selection_screen
            portrait_buttons, back_button, continue_button = draw_portrait_selection_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            # Check portrait selection
            for i, portrait_rect in enumerate(portrait_buttons):
                if portrait_rect.collidepoint(mouse_pos):
                    self.game_state.selected_portrait_index = i
            
            # Back to gender selection
            if back_button.collidepoint(mouse_pos):
                self.transition_to("gender")
            
            # Continue to name (only if portrait selected)
            elif continue_button.collidepoint(mouse_pos):
                if hasattr(self.game_state, 'selected_portrait_index'):
                    # Store selection in game state for save/load persistence
                    gender = self.game_state.character.get('gender', 'male')
                    self.game_state.set_selected_portrait(gender, self.game_state.selected_portrait_index)
                    
                    # Ensure active portrait file is current
                    self.game_state.ensure_active_portrait()
                    
                # DEBUG: Print to verify this is working
                    print(f"DEBUG: Portrait data stored: {self.game_state.character.get('selected_portrait_file', 'MISSING')}")
                    self.transition_to("name")
                    

        # Name screen
        elif self.game_state.screen == "name":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_name_screen
            name_buttons, new_names_button, custom_name_button = draw_name_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if new_names_button.collidepoint(mouse_pos):
                self.game_state.current_names = self.game_state.get_random_names(self.game_state.character['gender'])
            
            if custom_name_button.collidepoint(mouse_pos):
                self.game_state.custom_name_text = ""
                self.game_state.custom_name_active = True
                self.transition_to("custom_name")
            
            # Check if any name button was clicked
            for i, button in enumerate(name_buttons):
                if button.collidepoint(mouse_pos):
                    self.game_state.selected_name = self.game_state.current_names[i]
                    self.transition_to("name_confirm")
                    
                    break
        
        # Custom name screen
        elif self.game_state.screen == "custom_name":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_custom_name_screen
            input_box_rect, confirm_button, back_button = draw_custom_name_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if input_box_rect.collidepoint(mouse_pos):
                self.game_state.custom_name_active = True
            else:
                self.game_state.custom_name_active = False
            
            if confirm_button and confirm_button.collidepoint(mouse_pos):
                self.game_state.selected_name = self.game_state.custom_name_text.strip()
                self.transition_to("name_confirm")
            
            if back_button.collidepoint(mouse_pos):
                self.transition_to("name")
                self.game_state.custom_name_active = False
        
        # Name confirmation screen
        elif self.game_state.screen == "name_confirm":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_name_confirm_screen
            confirm_button, back_button = draw_name_confirm_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if confirm_button.collidepoint(mouse_pos):
                self.game_state.character['name'] = self.game_state.selected_name
                self.transition_to("gold")

            
            if back_button.collidepoint(mouse_pos):
                if self.game_state.custom_name_text:
                    self.transition_to("custom_name")
                else:
                    self.game_state.screen = "name"
        
        # Gold screen
        elif self.game_state.screen == "gold":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_gold_screen
            roll_button = draw_gold_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if roll_button.collidepoint(mouse_pos):
                if 'gold' not in self.game_state.character:
                    character_engine = self.data_manager.character_engine
                    if character_engine:
                        character_engine.roll_starting_gold()
                else:
                        self.transition_to("trinket")

        
        # Trinket screen
        elif self.game_state.screen == "trinket":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_trinket_screen
            roll_button = draw_trinket_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if roll_button.collidepoint(mouse_pos):
                if 'trinket' not in self.game_state.character:

                    character_engine = self.data_manager.character_engine
                    if character_engine:
                        character_engine.roll_trinket()
                else:
                    # Calculate final character stats via engine
                    character_engine = self.data_manager.character_engine
                    if character_engine:
                        character_engine.calculate_hp()
                    self.transition_to("summary")
           
        # Summary screen
        elif self.game_state.screen == "summary":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_summary_screen
            start_button = draw_summary_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if start_button.collidepoint(mouse_pos):
                
                # Use CharacterEngine for finalization
                from game_logic.character_engine import get_character_engine
                engine = get_character_engine()
                if engine:
                    engine.set_character_class('fighter')  # Set class before finalization
                    success = engine.finalize_character_creation()
                else:
                    success = False
                
                if success:
                            self.transition_to("welcome")
                else:
                    print("❌ Character creation failed - staying on summary screen")
                self.transition_to("welcome")
        
        # Welcome screen
        elif self.game_state.screen == "welcome":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.character_creation import draw_welcome_screen
            continue_button = draw_welcome_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if continue_button.collidepoint(mouse_pos):
                #self.transition_to("tavern_main")
                self.transition_to("broken_blade_main")
        
        # Tavern main screen
        elif self.game_state.screen == "tavern_main":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.tavern import draw_tavern_main_screen
            talk_button, gamble_button, bartender_button, leave_button = draw_tavern_main_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if talk_button.collidepoint(mouse_pos):
                self.transition_to("tavern_npcs")
                
            elif gamble_button.collidepoint(mouse_pos):
                self.transition_to("dice_bets")

            elif bartender_button.collidepoint(mouse_pos):
                self.game_state.current_npc = "bartender"
                self.transition_to("tavern_conversation")

            elif leave_button.collidepoint(mouse_pos):
                print("Leaving tavern - town exploration coming soon!")
        
        # NPC selection screen
        elif self.game_state.screen == "tavern_npcs":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.tavern import draw_npc_selection_screen
            npc_buttons = draw_npc_selection_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            # Generic click handler - no hardcoded NPC names
            for npc_key, button in npc_buttons.items():
                if button and button.collidepoint(mouse_pos):
                    if npc_key == 'back':
                            self.transition_to("tavern_main")
                    else:
                        self.game_state.current_npc = npc_key
                        self.transition_to("tavern_conversation")
                    break
        # Tavern conversation screen  
        elif self.game_state.screen == "tavern_conversation":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.tavern import draw_npc_conversation_screen
            action_button, back_button = draw_npc_conversation_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if action_button and action_button.collidepoint(mouse_pos):
                if self.game_state.current_npc == 'bartender':
                    # Go to shop screen
                    self.transition_to("merchant_shop")
                elif self.game_state.current_npc == 'pete':
                    # Pete's comedy sequence
                    self.game_state.pete_showing_comedy = True
                elif not self.game_state.is_party_full():
                    # Normal recruitment
                    success = self.game_state.recruit_npc(self.game_state.current_npc)
                    if success:
                        print(f"Recruited {self.game_state.current_npc}! Party size: {self.game_state.get_party_size()}")
                        self.transition_to("tavern_npcs")
                    else:
                        print(f"{self.game_state.current_npc} is already in your party!")
                else:
                    print("Your party is full!")
                    
            elif back_button and back_button.collidepoint(mouse_pos):
                # Handle different back destinations based on NPC
                if self.game_state.current_npc == 'bartender':
                    self.transition_to("broken_blade_main")  # Bartender goes back to main tavern
                else:
                    self.transition_to("tavern_npcs")  # Other NPCs go back to NPC selection
       
        #Dice betting screen
        elif self.game_state.screen == "dice_bets":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.gambling_dice import draw_dice_bets_screen
            bet_5_button, bet_10_button, bet_25_button, rules_button, back_button = draw_dice_bets_screen(
                temp_surface, self.game_state, self.fonts, self.images)
            
            if bet_5_button and bet_5_button.collidepoint(mouse_pos):
                self.game_state.dice_game['current_bet'] = 5
                self.game_state.roll_redstone_dice()
                self.transition_to("dice_rolling")
            elif bet_10_button and bet_10_button.collidepoint(mouse_pos):
                self.game_state.dice_game['current_bet'] = 10
                self.game_state.roll_redstone_dice()
                self.transition_to("dice_rolling")
            elif bet_25_button and bet_25_button.collidepoint(mouse_pos):
                self.game_state.dice_game['current_bet'] = 25
                self.game_state.roll_redstone_dice()
                self.transition_to("dice_rolling")
            elif rules_button and rules_button.collidepoint(mouse_pos):
                self.transition_to("dice_rules")
            elif back_button and back_button.collidepoint(mouse_pos):
                self.transition_to("broken_blade_main")
                
        # Dice rolling screen
        elif self.game_state.screen == "dice_rolling":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.gambling_dice import draw_dice_rolling_screen
            skip_area = draw_dice_rolling_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if skip_area and skip_area.collidepoint(mouse_pos):
                # Check if we're in animation phase or done
                current_time = pygame.time.get_ticks()
                roll_start_time = self.game_state.dice_game.get('roll_start_time', 0)
                if (current_time - roll_start_time) < 2000:  # Still in animation
                    # Skip animation
                    self.game_state.dice_game['animation_skipped'] = True
                
                # Always calculate results before transitioning
                bet_amount = self.game_state.dice_game['current_bet']
                dice = self.game_state.dice_game['last_roll']
                payout, combination, description, continues = self.game_state.calculate_dice_payout(bet_amount, dice)
                
                # Store results for display - THIS IS THE MISSING PIECE!
                self.game_state.dice_game['last_result'] = {
                    'combination': combination,
                    'payout': payout,
                    'description': description
                }
                
                # Reset animation state
                self.game_state.dice_game['animation_skipped'] = False
                self.transition_to("dice_results")
                
        # Dice results screen  
        elif self.game_state.screen == "dice_results":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.gambling_dice import draw_dice_results_screen
            continue_button, back_button = draw_dice_results_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if continue_button and continue_button.collidepoint(mouse_pos):
                self.transition_to("dice_bets")
            elif back_button and back_button.collidepoint(mouse_pos):
                self.transition_to("broken_blade_main")
                
        # Dice rules screen
        elif self.game_state.screen == "dice_rules":
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            from screens.gambling_dice import draw_dice_rules_screen
            back_button = draw_dice_rules_screen(temp_surface, self.game_state, self.fonts, self.images)
            
            if back_button and back_button.collidepoint(mouse_pos):
                self.transition_to("dice_bets")

        # Broken Blade Main Screen NEW 

        #where old button clicks lived broken_blade

  
        elif self.game_state.screen == "broken_blade_main":
            # Use generic screen manager instead of hardcoded logic
            handled = self.screen_manager.handle_screen_click(
                "broken_blade_main", mouse_pos, self
            )
            if handled:
                return True

        elif self.game_state.screen == "garrick_dialogue":
            handled = self.screen_manager.handle_screen_click("garrick_dialogue", mouse_pos, self)
            if handled:
                return True

        elif self.game_state.screen == "meredith_dialogue":
            handled = self.screen_manager.handle_screen_click("meredith_dialogue", mouse_pos, self)
            if handled:
                return True

        
        return True




    def run_current_screen(self):
        """
        NEW METHOD - Master screen renderer (from main.py draw_current_screen)
        This is the missing piece your GameController needs
        """
        try:
            self.draw_current_screen()
            self.frame_count += 1
            
        except Exception as e:
            self.handle_screen_error(e)  # Use your existing error handling!

    def draw_current_screen(self):
        """
        NEW METHOD - Complete screen drawing system (from main.py)
        This contains all the screen rendering logic
        """
        
        # All the imports and screen drawing logic from main.py goes here
        # (This is the massive screen rendering function from main.py)
        
        # Import all screen drawing functions
        from screens.character_creation import (
            draw_stats_screen, draw_gender_screen,
            draw_name_screen, draw_custom_name_screen, draw_name_confirm_screen,
            draw_gold_screen, draw_trinket_screen, draw_summary_screen,
            draw_welcome_screen, draw_portrait_selection_screen
        )
                       # ... all other imports from main.py ...
        from screens.character_creation import finalize_character_creation
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
        from screens.gambling_dice import (
            draw_dice_bets_screen, draw_dice_rolling_screen,
            draw_dice_results_screen, 
            draw_dice_rules_screen
        )

        from screens.broken_blade import draw_broken_blade_main_screen
        #from screens.broken_blade import draw_garrick_dialogue_screen
        #from screens.broken_blade import draw_meredith_dialogue_screen
        
        # Main screen drawing logic
        screen = self.screen
        game_state = self.game_state
        fonts = self.fonts
        images = self.images
        controller = self
    
        # All the screen drawing logic from main.py draw_current_screen()
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
        elif game_state.screen == "dice_bets":
            draw_dice_bets_screen(screen, game_state, fonts, images)
        elif game_state.screen == "dice_rolling":
            draw_dice_rolling_screen(screen, game_state, fonts, images)
        elif game_state.screen == "dice_results":
            draw_dice_results_screen(screen, game_state, fonts, images)
        elif game_state.screen == "dice_rules":
            draw_dice_rules_screen(screen, game_state, fonts, images)
        elif game_state.screen == "merchant_shop":
            draw_merchant_screen(screen, game_state, fonts, game_state.get_garrick_inventory(), images)
        elif game_state.screen == "broken_blade_main":
            draw_broken_blade_main_screen(screen, game_state, fonts, images, controller)
       # elif game_state.screen == "meredith_dialogue":
       #     draw_meredith_dialogue_screen(screen, game_state, fonts, images, controller)

#        elif game_state.screen == "garrick_dialogue":
#            draw_garrick_dialogue_screen(screen, game_state, fonts, images, controller)

        elif game_state.screen == "garrick_dialogue":
            from ui.generic_dialogue_handler import draw_generic_dialogue_screen
            draw_generic_dialogue_screen(screen, 'garrick', game_state, fonts, images, controller=self)

        elif game_state.screen == "meredith_dialogue":
            from ui.generic_dialogue_handler import draw_generic_dialogue_screen
            draw_generic_dialogue_screen(screen, 'meredith', game_state, fonts, images, controller=self)



        elif game_state.screen == "merchant_shop":
            draw_merchant_screen(screen, game_state, fonts, game_state.get_garrick_inventory(), images)
        
        # Draw character sheet overlay if open
        if game_state.character_sheet_open:
            #print("DEBUG: Drawing character sheet overlay")
            draw_character_sheet_screen(screen, game_state, fonts, images)

        # Draw quest log overlay if open 
        if game_state.quest_log_open:
            draw_quest_log_screen(screen, game_state, fonts, images)
        
        # Draw inventory overlay if open 
        if game_state.inventory_open:
            #print("DEBUG: Drawing inventory overlay")
            draw_inventory_screen(screen, game_state, fonts, images)
        
        # Draw help screen overlay if open
        if game_state.help_screen_open:
            #print("DEBUG: Drawing help screen overlay")
            draw_help_screen(screen, game_state, fonts, images)

        # Draw load screen overlay if open
        if game_state.load_screen_open:
            from screens.load_game import draw_load_game_screen
            draw_load_game_screen(screen, game_state, fonts, images, controller=controller)   

        # Draw save screen overlay if open
        if game_state.save_screen_open:
            from screens.save_game import draw_save_game_screen
            draw_save_game_screen(screen, game_state, fonts, images, controller)
        
        #Draw Character advancement overlay
        if getattr(game_state, 'character_advancement_open', False):
                from screens.character_advancement import draw_character_advancement
                draw_character_advancement(screen, game_state, fonts, controller)

    def register_screen(self, screen_name: str, screen_function: Callable):
        """
        Register a screen function with the controller
        This allows clean separation - screens don't need to know about each other
        """
        self.screens[screen_name] = screen_function
        print(f"📺 Screen registered: {screen_name}")
    
    def transition_to(self, new_screen: str, save_history: bool = True) -> bool:
        """
        Professional screen transition with error handling and history tracking
        Returns True if transition successful, False if failed
        """
        if new_screen not in self.screens:
            print(f"❌ ERROR: Unknown screen '{new_screen}'")
            return False
        
        # Save previous screen for back navigation
        if save_history and self.game_state.screen:
            self.previous_screen = self.game_state.screen
            self.screen_history.append(self.game_state.screen)
            
            # Limit history size to prevent memory bloat
            if len(self.screen_history) > 10:
                self.screen_history.pop(0)
        
        # SINGLE DATA AUTHORITY: Only update GameState.screen
        old_screen = self.game_state.screen
        self.game_state.screen = new_screen
        self.last_known_good_screen = new_screen
        
        # Update universal key state based on new screen
        self._update_universal_keys_state()

        print(f"🔄 Screen transition: {old_screen} → {new_screen}")
        return True
    
    def go_back(self) -> bool:
        """
        Navigate back to previous screen (like browser back button)
        """
        if self.previous_screen:
            return self.transition_to(self.previous_screen, save_history=False)
        elif self.screen_history:
            previous = self.screen_history.pop()
            return self.transition_to(previous, save_history=False)
        else:
            print("📍 No previous screen to return to")
            return False

    def handle_keyboard_input_enhanced(self, event) -> bool:
        """
        Enhanced keyboard handling - preserves existing logic + adds main.py functionality
        This replaces your current handle_keyboard_input(key) method
        """
        
        # PRIORITY 1: Text input gets absolute priority (NEW - from main.py)
        # This MUST come first to prevent hotkey conflicts during typing
        if self.is_text_input_active():
            return self.handle_text_input(event)
        
        # PRIORITY 2: Universal hotkeys (PRESERVE your existing system)
        # Your existing handle_universal_input() already handles I/Q/C/H/F7/F10/ESC
        if self.handle_universal_input(event):
            return True
        
        # PRIORITY 3: Screen-specific keyboard input (NEW - from main.py)
        # This handles Enter key on title screen, developer splash progression, etc.
        if self.handle_screen_specific_input(event):
            return True
        
        # PRIORITY 4: Screen handler delegation (PRESERVE your existing logic)
        # Keep your existing screen delegation system for individual screen handlers
        current_screen_handler = self.screens.get(self.game_state.screen)
        if current_screen_handler and hasattr(current_screen_handler, 'handle_keyboard_input'):
            # Note: This might need adjustment if screen handlers expect different parameters
            current_screen_handler.handle_keyboard_input(event.key)  # or event, depending on implementation
    
        return True

    def handle_keyboard_input(self, key):
        """
        Handles keyboard events delegated from the main game loop.
        All universal hotkey logic is contained here.
        """
        # Universal keys (always checked regardless of screen)
        if self.universal_keys_enabled:
            if key == pygame.K_h:
                # Toggle the help screen
                if self.is_overlay_active('help_overlay'):
                    self.hide_overlay('help_overlay')
                else:
                    self.show_overlay('help_overlay', 'help_screen')
            
            # All other overlay toggles
            elif key == pygame.K_F1:  # Inventory
                self.toggle_overlay('inventory_overlay', 'inventory_screen')
            elif key == pygame.K_F2:  # Character sheet
                self.toggle_overlay('character_sheet_overlay', 'character_sheet_screen')
            elif key == pygame.K_F3:  # Quest log
                self.toggle_overlay('quest_log_overlay', 'quest_log_screen')
            elif key == pygame.K_F4:  # Map
                self.toggle_overlay('map_overlay', 'world_map_screen')
            elif key == pygame.K_F5:  # Options
                self.toggle_overlay('options_overlay', 'options_screen')
            elif key == pygame.K_F6:  # Lore book
                self.toggle_overlay('lore_book_overlay', 'lore_book_screen')

            # Save/load hotkeys
            elif key == pygame.K_F7:  # Save
                self.save_game()
            elif key == pygame.K_F10:  # Load
                self.load_game()

        # Delegate event to the current screen's handler
        current_screen_handler = self.screens.get(self.current_screen)
        if current_screen_handler and hasattr(current_screen_handler, 'handle_keyboard_input'):
            current_screen_handler.handle_keyboard_input(key)
        
        return True

    def handle_mouse_input_enhanced(self, mouse_pos) -> bool:
        """
        ENHANCED VERSION - Complete mouse handling with all overlay logic
        This enhances your current handle_mouse_click method
        """
        
        # Use the complete overlay mouse handling from main.py
        if self.handle_overlay_mouse_clicks(mouse_pos):
            return True
        
        # Delegate to screen-specific handlers
        return self.handle_screen_mouse_clicks(mouse_pos)

    def handle_mouse_click(self, mouse_pos):
        #old
        """
        Handles mouse click events.
        Delegates the click to the active overlay or the current screen.
        """
        # 1. Handle Overlays First
        # This ensures that if an overlay is active, clicks are processed there
        # before reaching the main screen underneath.
        if self.game_state.character_sheet_open:
            # Delegate click to the character sheet
            character_sheet_screen = self.screens.get("character_sheet_screen")
            if character_sheet_screen:
                character_sheet_screen.handle_mouse_click(mouse_pos, self.game_state, self.fonts, self.images, self)
            return

        if self.game_state.help_screen_open:
            # Delegate click to the help screen
            help_screen = self.screens.get("help_screen")
            if help_screen:
                help_screen.handle_mouse_click(mouse_pos, self.game_state, self.fonts, self.images, self)
            return
            
        # Add other overlays here (e.g., inventory, quest log)
        # This can be done with a more robust loop later.
        
        # 2. Delegate to Current Screen
        # If no overlay is active, pass the event to the current screen's handler.
        current_screen_handler = self.screens.get(self.current_screen)
        if current_screen_handler and hasattr(current_screen_handler, 'handle_mouse_click'):
            current_screen_handler.handle_mouse_click(mouse_pos)

        # Note: If the screen handler needs more than just mouse_pos, you can adjust
        # this call accordingly (e.g., current_screen_handler.handle_mouse_click(mouse_pos, self.game_state, ...))

    def handle_universal_input(self, event: pygame.event.Event) -> bool:
        """
        Handle universal keyboard shortcuts that work across all screens
        Returns True if event was consumed, False if screen should handle it
        """
        #if not self.universal_keys_enabled:
        #    return False
        
        if event.type == pygame.KEYDOWN:
            print(f"🔍 DEBUG: Controller screen={self.game_state.screen}, Key pressed={pygame.key.name(event.key)}")
            print(f"🔍 DEBUG: universal_keys_enabled = {self.universal_keys_enabled}")

            # ===== HELP KEY - ALWAYS WORKS (except during text input) =====
            if event.key == pygame.K_h:
                is_text_input_active = (self.game_state.screen == 'custom_name' and 
                                    getattr(self.game_state, 'custom_name_active', False))
                if not is_text_input_active:
                    if not self.game_state.help_screen_open:
                        self.close_all_overlays()
                    self.game_state.toggle_help()
                    print(f"✅ Help screen toggled: {self.game_state.help_screen_open}")
                    return True

            # ESC key - close overlays first, never exit game
            if event.key == pygame.K_ESCAPE:
                # Check if any overlays are open and close them
                if (self.game_state.help_screen_open or 
                    self.game_state.inventory_open or 
                    self.game_state.quest_log_open or 
                    self.game_state.character_sheet_open or
                    getattr(self.game_state, 'character_advancement_open', False) or
                    getattr(self.game_state, 'save_screen_open', False) or
                    getattr(self.game_state, 'load_screen_open', False)):
                    
                    self.close_all_overlays()
                    if hasattr(self.game_state, 'save_screen_open'):
                        self.game_state.save_screen_open = False
                    if hasattr(self.game_state, 'load_screen_open'):
                        self.game_state.load_screen_open = False
                    print("🔄 ESC: Closed all overlays")
                    return True
                else:
                    # No overlays open - ESC does nothing (could add main menu logic here later)
                    print("🔄 ESC: No overlays to close")
                    return True
            
            # F1 always works (to toggle debug on/off)
            if event.key == pygame.K_F1:
                self.toggle_debug_info()
                return True

            # Other debug shortcuts (only in debug mode)
            if self.debug_mode:
                if event.key == pygame.K_F2:
                    self.print_game_state()
                    return True
                elif event.key == pygame.K_F3:
                    self.screenshot()
                    return True
                # F4 - Reload data systems (development shortcut)
                elif event.key == pygame.K_F4:
                    print("🔄 F4 pressed - Reloading data systems...")
                    self.reload_data_systems()
                    return True

            # ===== CHECK FOR BLOCKED SCREENS =====
            
            if not self.universal_keys_enabled:
                print(f"🚫 Universal keys disabled, skipping key: {pygame.key.name(event.key)}")
                return False

            # ===== KEYS THAT CAN BE BLOCKED =====
            
            #  SAVE/LOAD KEYS 
            if event.key in [pygame.K_F5, pygame.K_F7, pygame.K_F10]:
                if not self.can_save_load():
                    print(f"🚫 Save/Load operations disabled on screen: {self.game_state.screen}")
                    return True
                
                # Process save/load if allowed
                if event.key == pygame.K_F5:
                    self.save_game(save_slot=99)
                    return True
                elif event.key == pygame.K_F7:
                    print("DEBUG: F7 key detected - opening save screen")
                    self.game_state.save_screen_open = True
                    print(f"DEBUG: save_screen_open set to {self.game_state.save_screen_open}")    
                    return True
                elif event.key == pygame.K_F10:
                    self.game_state.load_screen_open = True
                    return True

            # ===== OVERLAY HOTKEYS - Only work on gameplay screens =====
            # I for Inventory
            if event.key == pygame.K_i:
                if not self.game_state.inventory_open:
                    self.close_all_overlays()
                self.game_state.toggle_inventory()
                print(f"Inventory open: {self.game_state.inventory_open}")
                return True
            
            # Q for quest
            elif event.key == pygame.K_q:
                if not self.game_state.quest_log_open:
                    self.close_all_overlays()
                self.game_state.toggle_quest_log()
                print(f"Quest log open: {self.game_state.quest_log_open}")
                return True
            
            # C for character sheet
            elif event.key == pygame.K_c:
                if not self.game_state.character_sheet_open:
                    self.close_all_overlays()
                self.game_state.toggle_character_sheet()
                print(f"DEBUG: Set character_sheet_open = {self.game_state.character_sheet_open}")
                print(f"DEBUG: Verify game_state.character_sheet_open = {getattr(self.game_state, 'character_sheet_open', 'MISSING')}")
                return True

            # L for character sheet
            elif event.key == pygame.K_l:
                self.close_all_overlays()
                self.game_state.toggle_character_advancement_open()
                print("⭐ Character advancement toggled")
                return True

        return False

    def _update_universal_keys_state(self):
        """
        Updates the state of universal keys based on the current screen.
        Hotkeys (inventory, character sheet, etc.) should be disabled on screens
        that require focused input, like character creation or an active conversation.
        """
        # ⭐ IMPORTANT: Read screen from GameState (Single Data Authority)
        current_screen = self.game_state.screen
        
        # A list of screens where universal keys should be disabled
        screens_to_disable = [
            "game_title",           
            "developer_splash",     
            "main_menu",            
            
            # Character Creation Screens (using ACTUAL names from main.py)
            "stats",                
            "gender",               
            "name",                 
            "portrait_selection",   
            "custom_name",          
            "name_confirm",         
            "gold",                 
            "trinket",              
            "summary",              
            "welcome",              
            
            # Conversation/focused input screens
            "npc_conversation"
        ]
        
        # Check if the current screen is in the disabled list
        is_disabled_screen = current_screen in screens_to_disable
        
        # Update the flag
        self.universal_keys_enabled = not is_disabled_screen
        
        # Provide debug feedback
        if is_disabled_screen:
            print(f"🚫 Universal keys disabled on screen: {current_screen}")
        else:
            print(f"✅ Universal keys enabled on screen: {current_screen}")

    def handle_screen_error(self, error: Exception):
        """
        Professional error recovery system
        """
        self.error_count += 1
        print(f"💥 Screen error in '{self.game_state.screen}': {error}")
        
        # Progressive error recovery
        if self.error_count < 3:
            # Try to continue with current screen
            print("🔧 Attempting to continue...")
        else:
            # Fall back to last known good screen
            print(f"🚨 Falling back to: {self.last_known_good_screen}")
            self.transition_to(self.last_known_good_screen)
        #else:
            # Emergency fallback to splash screen
        #    print("🆘 Emergency fallback to splash screen")
        #    self.transition_to("splash")
        #    self.error_count = 0
    
    def quit_game(self):
        """
        Clean game shutdown with state saving opportunities
        """
        print("👋 Game Controller shutting down...")
        
        # Future: Save game state here
        # self.game_state.save_to_file("autosave.dat")
        
        pygame.quit()
        sys.exit()
    
    def toggle_debug_info(self):
        """
        Toggle debug information display
        """
        self.debug_mode = not self.debug_mode
        print(f"🐛 Debug mode: {'ON' if self.debug_mode else 'OFF'}")
    
    def print_game_state(self):
        """
        Debug function to print current game state
        """
        print(f"\n=== GAME STATE DEBUG ===")
        print(f"Current Screen: {self.game_state.screen}")
        print(f"Previous Screen: {self.previous_screen}")
        print(f"Screen History: {self.screen_history}")
        print(f"Character Name: {getattr(self.game_state, 'character_name', 'None')}")
        print(f"Error Count: {self.error_count}")
        print(f"Frame Count: {self.frame_count}")
        print(f"========================\n")
    
    def screenshot(self):
        """
        Take a screenshot for debugging/development
        """
        filename = f"screenshot_{pygame.time.get_ticks()}.png"
        pygame.image.save(self.screen, filename)
        print(f"📸 Screenshot saved: {filename}")
    
    def close_all_overlays(self):
        """Close all overlay screens for clean single-overlay behavior"""
        self.game_state.inventory_open = False
        self.game_state.quest_log_open = False
        self.game_state.character_sheet_open = False
        self.game_state.help_screen_open = False
        self.game_state.character_advanacement_open = False
        # Clear any selections when closing overlays
        self.game_state.inventory_selected = None
        self.game_state.selected_quest = None
        print("🔄 All overlays closed")
    
    def shutdown(self):
        """Professional shutdown with complete resource cleanup"""
        print("🏰 Terror in Redstone shutting down...")

        # 1. Auto-save current progress (you have this!)
        if hasattr(self, 'save_game'):
            print("💾 Auto-saving progress...")
            self.save_game(save_slot=0)  # Auto-save slot

        # 2. Clear active game state
        if hasattr(self.game_state, 'clear_active_portrait'):
            self.game_state.clear_active_portrait()
            print("🖼️ Portrait resources cleared")

        # 3. Close all overlay states cleanly
        self.close_all_overlays()

        # 4. Audio cleanup (if you add sound later)
        try:
            pygame.mixer.quit()
            print("🔊 Audio resources released")
        except:
            pass  # Audio might not be initialized

        # 5. Clean pygame shutdown
        pygame.quit()
        print("🎮 Pygame resources released")
        
        # 6. Final system exit
        print("⚔️ Farewell, brave adventurer!")
        sys.exit()

    def draw_debug_overlay(self):
        """
        Draw debug information overlay
        """
        if not self.debug_mode:
            return
        
        # Calculate FPS
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fps_time > 1000:
            fps = self.frame_count * 1000 // (current_time - self.last_fps_time)
            self.last_fps_time = current_time
            self.frame_count = 0
            self.last_fps = fps
        
        # Draw debug info
        if hasattr(self, 'last_fps'):
            debug_text = [
                f"FPS: {self.last_fps}",
                f"Screen: {self.game_state.screen}",
                f"Errors: {self.error_count}",
                f"F1:Debug F2:State F3:Screenshot"
            ]
            
            y = 10
            for text in debug_text:
                surface = self.fonts['fantasy_tiny'].render(text, True, BRIGHT_GREEN)
                self.screen.blit(surface, (10, y))
                y += 20

    def save_game(self, save_slot=1):
        
        """
        Save complete game state to JSON file
        save_slot: 1-3 for manual saves, 0 for auto-save
        """
        try:
            # Collect all game state data
            save_data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'save_slot': save_slot,
                

                # Character data
                'character': self.game_state.character,
                'inventory': self.game_state.inventory,
                
                # Game progression
                'current_screen': self.game_state.screen,
                'screen_history': self.screen_history[-5:],  # Keep last 5 screens
                'previous_screen': self.previous_screen,
                
                # World state
                'party_members': getattr(self.game_state, 'party_members', []),
                'tavern_visits': getattr(self.game_state, 'tavern_visits', 0),
                'locations_discovered': getattr(self.game_state, 'locations_discovered', []),
                
                # Quest and NPC states
                'quest_flags': getattr(self.game_state, 'quest_flags', {}),
                'npc_recruitment_status': getattr(self.game_state, 'npc_recruitment_status', {}),
                'conversations_had': getattr(self.game_state, 'conversations_had', []),
                'mayor_talked': getattr(self.game_state, 'mayor_talked', False),
                'mayor_mentioned': getattr(self.game_state, 'mayor_mentioned', False),
                'pete_attempted_recruitment': getattr(self.game_state, 'pete_attempted_recruitment', False),
                'pete_showing_comedy': getattr(self.game_state, 'pete_showing_comedy', False),
                'meredith_talked': getattr(self.game_state, 'meredith_talked', False),
                'garrick_talked': getattr(self.game_state, 'garrick_talked', False),
                'learned_about_church': getattr(self.game_state, 'learned_about_church', False),
                'learned_about_ruins': getattr(self.game_state, 'learned_about_ruins', False),
                'quest_active': getattr(self.game_state, 'quest_active', False),
                'just_got_quest': getattr(self.game_state, 'just_got_quest', False),
                'quest_system': getattr(self.game_state, 'quest_manager', None).get_quest_data_for_save() if hasattr(self.game_state, 'quest_manager') else {},
                'showing_meredith_response':getattr(self.game_state, 'showing_meredith_response', False),
                'showing_garrick_response':getattr(self.game_state, 'showing_garrick_response', False),

                # Dice game state
                'dice_game': getattr(self.game_state, 'dice_game', {}),
            
                # Shopping cart state
                'shopping_cart': getattr(self.game_state, 'shopping_cart', {}),
                
                # Gambling and economy
                'house_money': getattr(self.game_state, 'house_money', 50),
                'gambling_wins': getattr(self.game_state, 'gambling_wins', 0),
                'gambling_losses': getattr(self.game_state, 'gambling_losses', 0),
                
                # Equipment state
                'equipped_weapon': getattr(self.game_state, 'equipped_weapon', None),
                'equipped_armor': getattr(self.game_state, 'equipped_armor', None),
                'equipped_shield': getattr(self.game_state, 'equipped_shield', None),
            }
            
            # Create saves directory if it doesn't exist
            #os.makedirs('saves', exist_ok=True)
            
            # Determine save file name
            if save_slot == 0:
                filename = 'saves/autosave.json'
                save_type = "Auto-save"
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
                save_type = "Quick save"
            else:
                filename = f'saves/save_slot_{save_slot}.json'
                save_type = f"Manual save (Slot {save_slot})"
            
            # Write save file
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"💾 {save_type} completed: {filename}")
            print(f"   🎭 Character: {self.game_state.character.get('name', 'Unknown')}")
            print(f"   💰 Gold: {self.game_state.character.get('gold', 0)}")
        
            # Update GameController state tracking
            self.last_save_time = datetime.now()
            self.error_count = 0  # Reset error count on successful save
            
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            self.error_count += 1
            return False

    def load_game(self, save_slot=1):
        """
        Load game state from JSON file and restore game to saved state
        save_slot: 1-3 for manual saves, 0 for auto-save
        """
        try:
            # Determine save file name
            if save_slot == 0:
                filename = 'saves/autosave.json'
                save_type = "Auto-save"
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
                save_type = 'Quick Save'
            else:
                filename = f'saves/save_slot_{save_slot}.json'
                save_type = f"Save slot {save_slot}"
            
            # Check if save file exists
            if not os.path.exists(filename):
                print(f"❌ No save file found: {filename}")
                return False
            
            # Load save data
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            print(f"📁 Loading {save_type}...")
            print(f"   Saved: {save_data.get('timestamp', 'Unknown time')}")
            print(f"   Version: {save_data.get('version', 'Unknown')}")
            
             # Restore character data (GameState is the authority!)
            if 'character' in save_data:
                self.game_state.character = save_data['character']
                print(f"   🎭 Character: {self.game_state.character.get('name', 'Unknown')}")
            
            if 'inventory' in save_data:
                self.game_state.inventory = save_data['inventory']
                print(f"   💰 Gold: {self.game_state.character.get('gold', 0)}")
            
           # Restore game progression
            target_screen = save_data.get('current_screen', 'game_title')
            if target_screen in self.screens:
                self.game_state.screen = target_screen
                self.previous_screen = save_data.get('previous_screen')
                self.screen_history = save_data.get('screen_history', [])
                self.game_state.screen = target_screen
            else:
                print(f"⚠️ Saved screen '{target_screen}' not available, staying on current screen")
            
            # Restore world state
            self.game_state.party_members = save_data.get('party_members', [])
            self.game_state.tavern_visits = save_data.get('tavern_visits', 0)
            self.game_state.locations_discovered = save_data.get('locations_discovered', [])
            
            # Restore quest and NPC states
            self.game_state.quest_flags = save_data.get('quest_flags', {})
            self.game_state.npc_recruitment_status = save_data.get('npc_recruitment_status', {})
            self.game_state.conversations_had = save_data.get('conversations_had', [])
            self.game_state.mayor_talked = save_data.get('mayor_talked', False)
            self.game_state.meredith_talked = save_data.get('meredith_talked', False)
            self.game_state.garrick_talked = save_data.get('garrick_talked', False)  
            self.game_state.learned_about_church = save_data.get('learned_about_church', False)
            self.game_state.learned_about_ruins = save_data.get('learned_about_ruins', False)
            self.game_state.quest_active = save_data.get('quest_active', False)
            self.game_state.mayor_mentioned = save_data.get('mayor_mentioned', False)
            self.game_state.pete_attempted_recruitment = save_data.get('pete_attempted_recruitment', False)
            self.game_state.pete_showing_comedy = save_data.get('pete_showing_comedy', False)
            self.game_state.showing_meredith_response = save_data.get('showing_meredith_response', False)
            self.game_state.showing_garrick_response = save_data.get('showing_garrick_response', False)

            quest_system_data = save_data.get('quest_system', {})
            if quest_system_data and hasattr(self.game_state, 'quest_manager'):
                self.game_state.quest_manager.load_from_save_data(quest_system_data)

            # Restore dice game state
            self.game_state.dice_game = save_data.get('dice_game', {})
            # Restore shopping cart
            self.game_state.shopping_cart = save_data.get('shopping_cart', {}),
            # Restore gambling and economy
            self.game_state.house_money = save_data.get('house_money', 50)
            self.game_state.gambling_wins = save_data.get('gambling_wins', 0)
            self.game_state.gambling_losses = save_data.get('gambling_losses', 0)
            
            # Restore equipment state
            self.game_state.equipped_weapon = save_data.get('equipped_weapon')
            self.game_state.equipped_armor = save_data.get('equipped_armor')
            self.game_state.equipped_shield = save_data.get('equipped_shield')
             
            # Restore shopping cart (with safety check)
            shopping_cart_data = save_data.get('shopping_cart', {})
            if isinstance(shopping_cart_data, dict):
                self.game_state.shopping_cart = shopping_cart_data
            else:
                # Safety: Reset corrupted shopping cart data
                print("⚠️ Shopping cart data corrupted, resetting to empty cart")
                self.game_state.shopping_cart = {}

            # Also ensure dice game state is properly restored
            dice_game_data = save_data.get('dice_game', {})
            if isinstance(dice_game_data, dict):
                self.game_state.dice_game = dice_game_data
            else:
                # Safety: Reset dice game to defaults
                print("⚠️ Dice game data corrupted, resetting to defaults")
                self.game_state.dice_game = {
                    'house_money': 500,
                    'game_active': True,
                    'win_streak': 0,
                    'loss_streak': 0,
                    'last_roll': [],
                    'current_bet': 0
                }


            print(f"✅ Game loaded successfully from {save_type}")
            print(f"   Character: {self.game_state.character.get('name', 'Unknown')}")
            print(f"   Current screen: {self.game_state.screen}")
            
            #Activate character portrait after loading
            self.game_state.activate_character_portrait()

            # After loading all the flags, populate quest system if mayor was already talked to
            if self.game_state.mayor_talked and self.game_state.quest_active:
                # Ensure mayor is mentioned so button appears
                self.game_state.mayor_mentioned = True

                    # For future quest items:
                    # Re-populate any quest log entries that should exist
                    # (You might need to call a method to rebuild active quests here)
            
            print("✅ Game state restored successfully!")

            # Update GameController state
            self.last_load_time = datetime.now()
            self.error_count = 0  # Reset error count on successful load
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Save file corrupted: {e}")
            return False
        except Exception as e:
            print(f"❌ Load failed: {e}")
            self.error_count += 1
            return False

    def get_save_info(self, save_slot=1):
        """
        Get information about a save file without loading it
        Returns dict with save info or None if no save exists
        """
        try:
            if save_slot == 0:
                filename = 'saves/autosave.json'
                save_type = "Auto-save"
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
                save_type = "Quick save"
            else:
                filename = f'saves/save_slot_{save_slot}.json'
                save_type = f"Save_slot {save_slot}"

           
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            return {
                'character_name': save_data.get('character', {}).get('name', 'Unknown'),
                'timestamp': save_data.get('timestamp', 'Unknown'),
                'current_screen': save_data.get('current_screen', 'Unknown'),
                'party_size': len(save_data.get('party_members', [])) + 1,
                'gold': save_data.get('character', {}).get('gold', 0),
                'version': save_data.get('version', 'Unknown')
            }
            
        except Exception as e:
            print(f"❌ Error reading save info: {e}")
            return None

    def auto_save(self):
        """
        Perform automatic save (shorthand for save_game(0))
        """
        return self.save_game(save_slot=0)

    def delete_save(self, save_slot):
        """
        Delete a save file
        """
        try:
            if save_slot == 0:
                filename = 'saves/autosave.json'
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
            else:
                filename = f'saves/save_slot_{save_slot}.json'
            
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🗑️ Deleted save slot {save_slot}")
                return True
            else:
                print(f"❌ Save slot {save_slot} does not exist")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting save: {e}")
            return False

    def can_save_load(self) -> bool:
            """
            Determine if save/load operations are allowed on current screen
            Returns False for transient/temporary screens where saving would cause issues
            """
            # UNIFIED: Use same screen names as hotkey blocking system
            restricted_screens = {
            'game_title',           # Title screen 
            'developer_splash',     # Company splash screen
            'main_menu',            # Main menu
            
            # Character Creation Screens  
            'stats', 
            'gender', 
            'name', 
            'portrait_selection',
            'custom_name',
            'name_confirm', 
            'gold', 
            'trinket', 
            'summary', 
            'welcome',
            
            # Gambling screens (from original logic)
            'dice_bets',        # Dice betting screen
            'dice_rolling',     # Dice rolling animation
            'dice_results',     # Dice results display
            'dice_rules',       # Dice rules explanation
            
            # Shopping screens (from original logic)
            'merchant_shop'     # Shop
            }

            # Check if the current screen is in the disabled list
            is_disabled_screen = self.game_state.screen in restricted_screens
            
            # Update the flag
            self.universal_keys_enabled = not is_disabled_screen
            
            # Provide debug feedback
            if is_disabled_screen:
                print(f"🚫 Universal keys disabled on screen: {self.game_state.screen}")
            else:
                print(f"✅ Universal keys enabled on screen: {self.game_state.screen}")
            
            print(f"🔧 DEBUG: universal_keys_enabled = {self.universal_keys_enabled}")

            # Check if current screen is restricted
            if self.game_state.screen in restricted_screens:
                print(f"🚫 Save/Load disabled on screen: {self.game_state.screen}")
                return False
            
            # Check if any overlay screens are open that should block save/load
            if hasattr(self.game_state, 'save_screen_open') and self.game_state.save_screen_open:
                return False
            
            if hasattr(self.game_state, 'load_screen_open') and self.game_state.load_screen_open:
                return False
            
            return True
            
    def get_inventory_engine(self):
        """Get the inventory engine instance from DataManager"""
        if self.data_manager:
            return self.data_manager.get_manager('inventory')
        return None

    def get_commerce_engine(self):
        """Get the commerce engine instance from DataManager"""  
        if self.data_manager:
            return self.data_manager.get_manager('commerce')
        return None
    
    def get_dialogue_engine(self):
        """Get the dialogue engine instance through DataManager"""
        if self.data_manager:
            return self.data_manager.get_dialogue_engine()
        return None
    
    def get_data_manager(self):
        """
        Safe accessor for data manager
        Returns None if not initialized
        """
        return getattr(self, 'data_manager', None)
    
    def reload_data_systems(self) -> bool:
        """
        Reload all data systems (useful for development)
        """
        if hasattr(self, 'data_manager') and self.data_manager:
            return self.data_manager.reload_all_systems()
        else:
           # If the data manager doesn't exist, initialize it properly
            print("⚠️ Data manager not found. Initializing all systems instead of reloading.")
            return initialize_game_data(self.game_state)


class ScreenRegistry:
    """
    Helper class for organizing screen registration
    Makes it easy to register all screens in one place
    """
    
    @staticmethod
    def register_all_screens(controller: GameController):
        """
        Register all game screens with the controller
        This is where we'll add each screen as we create them
        """
        
        # Import screen modules (we'll add these as we create them)
        try:
            from screens.character_creation import (
                draw_stats_screen, draw_gender_screen,
                draw_name_screen, draw_custom_name_screen, draw_name_confirm_screen,
                draw_gold_screen, draw_trinket_screen, draw_summary_screen,
                draw_welcome_screen, draw_portrait_selection_screen
            )
            print("🔍 Attempting to import character creation screens...")
            print("✅ Character creation screens imported successfully!")
            
            # Register character creation screens  
            controller.register_screen("stats", draw_stats_screen)
            controller.register_screen("gender", draw_gender_screen)
            controller.register_screen("name", draw_name_screen)
            controller.register_screen("portrait_selection", draw_portrait_selection_screen)
            controller.register_screen("custom_name", draw_custom_name_screen)
            controller.register_screen("name_confirm", draw_name_confirm_screen)
            controller.register_screen("gold", draw_gold_screen)
            controller.register_screen("trinket", draw_trinket_screen)
            controller.register_screen("summary", draw_summary_screen)
            controller.register_screen("welcome", draw_welcome_screen)
            
            print("✅ Character creation screens registered!")

        except ImportError as e:
            print(f"❌ IMPORT ERROR: {e}")
            print(f"⚠️ Character creation screens not available: {e}")
        
         # Register title/menu screens
        try:
            from screens.title_menu import draw_title_screen, draw_company_splash_screen, draw_main_menu
            controller.register_screen("game_title", draw_title_screen)           # Initial title
            controller.register_screen("developer_splash", draw_company_splash_screen)  # Company screen
            controller.register_screen("main_menu", draw_main_menu)               # Main menu
            print("✅ Title/menu screens registered!")
        except ImportError as e:
            print(f"❌ IMPORT ERROR: {e}")
            print(f"⚠️ Title/menu screens not available: {e}")

        # Register character advancement screen
        try:
            from screens.character_advancement import draw_character_advancement
            controller.register_screen("character_advancement", draw_character_advancement)
            print("✅ Character advancement screen registered!")
        except ImportError as e:
            print(f"⚠️ Character advancement screen not available: {e}")

        # Register tavern screens
        try:
            from screens.tavern import draw_tavern_main_screen, draw_npc_selection_screen, draw_npc_conversation_screen
            controller.register_screen("tavern_main", draw_tavern_main_screen)
            controller.register_screen("tavern_npcs", draw_npc_selection_screen)
            controller.register_screen("tavern_conversation", draw_npc_conversation_screen)
            controller.register_screen("bartender", draw_tavern_main_screen)  # If bartender uses same screen
            print("✅ Tavern screens registered!")
        except ImportError as e:
            print(f"⚠️ Tavern screens not available: {e}")

        # Register Broken Blade
        try:
            from screens.broken_blade import draw_broken_blade_main_screen 
            controller.register_screen("broken_blade_main", draw_broken_blade_main_screen)
            print("✅ Broken Blade screens registered!")
        except ImportError as e:
            print(f"⚠️ Broken Blade screens not available: {e}")
        
        # Register gambling screens  
        try:
            from screens.gambling_dice import draw_dice_bets_screen, draw_dice_rolling_screen, draw_dice_results_screen, draw_dice_rules_screen
            #controller.register_screen("dice_bet", draw_dice_bet_screen)
            controller.register_screen("dice_bets", draw_dice_bets_screen)  # Alternative name
            controller.register_screen("dice_rolling", draw_dice_rolling_screen)
            controller.register_screen("dice_results", draw_dice_results_screen)
            controller.register_screen("dice_rules", draw_dice_rules_screen)
            print("✅ Gambling screens registered!")
        except ImportError as e:
            print(f"⚠️ Gambling screens not available: {e}")
        
        # Register shopping screen
        try:
            from screens.shopping import draw_merchant_screen
            controller.register_screen("merchant_shop", draw_merchant_screen)
            print("✅ Shopping screen registered!")
        except ImportError as e:
            print(f"⚠️ Shopping screen not available: {e}")

        # Register save/load screens
        try:
            from screens.load_game import draw_load_game_screen
            from screens.save_game import draw_save_game_screen
            controller.register_screen("load_screen", draw_load_game_screen)
            controller.register_screen("save_screen", draw_save_game_screen)
            print("✅ Save/Load screens registered!")
        except ImportError as e:
            print(f"⚠️ Save/Load screens not available: {e}")

        from ui.generic_dialogue_handler import register_npc_dialogue_screen
        register_npc_dialogue_screen(controller.screen_manager, 'garrick')
        register_npc_dialogue_screen(controller.screen_manager, 'meredith')

        # Future screens will be registered here
        # controller.register_screen("general_store", general_store_screen)
        # controller.register_screen("combat", combat_screen)
        # controller.register_screen("world_map", world_map_screen)
        
        print("✅ Screen registration complete!")


# Professional configuration system
class GameConfig:
    """
    Centralized configuration management
    Easy tweaking of game balance and behavior
    """
    
    # Display settings
    ENABLE_DEBUG_MODE = False
    ESCAPE_EXITS_GAME = True
    ENABLE_UNIVERSAL_KEYS = True
    
    # Game balance settings
    DICE_ANIMATION_SPEED = 0.1  # seconds per dice roll animation frame
    STARTING_GOLD_MULTIPLIER = 10  # 3d6 * 10
    TAVERN_ROOM_COST = 2  # Gold per night
    
    # UI settings
    BUTTON_HOVER_ENABLED = True
    SCREEN_TRANSITION_SPEED = 0.2
    AUTO_SAVE_INTERVAL = 300  # seconds
    
    # Development settings
    SHOW_FPS = False
    ENABLE_SCREENSHOTS = True
    LOG_SCREEN_TRANSITIONS = True
    
    @classmethod
    def apply_to_controller(cls, controller: GameController):
        """
        Apply configuration settings to game controller
        """
        controller.debug_mode = cls.ENABLE_DEBUG_MODE
        controller.escape_exits_game = cls.ESCAPE_EXITS_GAME
        controller.universal_keys_enabled = cls.ENABLE_UNIVERSAL_KEYS
        
        print("⚙️ Game configuration applied to controller")


if __name__ == "__main__":
    print("🎮 Game Controller Infrastructure")
    print("This module provides professional game state management")
    print("Import and use with: from core.game_controller import GameController")



