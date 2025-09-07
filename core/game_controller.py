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
from game_logic.save_manager import SaveManager
from screens.intro_scenes import IntroSequenceManager
from ui.screen_manager import ScreenManager
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from utils.constants import *
from input_handler import InputHandler


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
        self.input_handler = None

        # Screen registry - maps screen names to their functions
        self.screens: Dict[str, Callable] = {}
        
        # ADD THIS: Initialize ScreenManager
        from ui.screen_manager import ScreenManager
        self.screen_manager = ScreenManager(
            event_manager=self.event_manager,
            screen=screen,       # Pass screen as named parameter
            fonts=fonts,
            images=images
        )
        print("🖥️ ScreenManager initialized")

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
        self.save_manager = SaveManager(self.game_state)
        self.last_save_time = None
        self.last_load_time = None

    def _update_universal_keys_state(self):
        """Update universal keys state based on current screen"""
        # Simple implementation for now
        if self.game_state.screen in ["custom_name"]:
            self.universal_keys_enabled = False
        else:
            self.universal_keys_enabled = True
    
    def register_screen_clickables(self):
        """TEMPORARY - Register screen clickable regions with InputHandler"""
        if not self.input_handler:
            print("🎯 Screen clickables registration skipped (no InputHandler)")
            return
        
        # Only run InputHandler code if it exists
        self.input_handler.clear_all_clickables()
        
        # Rest of the clickable registration code...
        print("🎯 Screen clickables registered with InputHandler")

    def register_screen(self, screen_name: str, draw_function):
        """Register a screen with its drawing function"""
        self.screens[screen_name] = draw_function
        print(f"📋 Registered screen: {screen_name}")
   
    def initialize_data_systems(self) -> bool:
        """
        Initializes and loads all game data and engines.
        Called during GameController startup
        """
        print("🎮 GameController: Initializing data management systems...")
    
        try:
            print("📊 GameController: Beginning core system initialization...")
            # Step 1: Initialize EventManager first
            self.event_manager = initialize_event_manager()
        
            # Step 2: Initialize InputHandler immediately after EventManager
            self.input_handler = InputHandler(self.event_manager)
            self.input_handler.enable_debug_input(True)
            print("✅ InputHandler initialized early!") 
           
            # Step 3: NOW create ScreenManager with EventManager
            self.screen_manager = ScreenManager(
                event_manager=self.event_manager,
                screen=self.screen,
                fonts=self.fonts,
                images=self.images
            )

            self.screen_manager.input_handler = self.input_handler

            self.screen_manager.transition_to(self.game_state.screen, self.game_state, save_history=False)
            print(f"ScreenManager initialized with starting screen: {self.game_state.screen}")

            self.screen_manager.event_manager = self.event_manager
            
            # Subscribe ScreenManager to navigation events
            self.event_manager.register("SCREEN_CHANGE", self.screen_manager._handle_screen_change_event)
            self.event_manager.register("SCREEN_ADVANCE", self.screen_manager._handle_screen_advance_event)
            print("📺 ScreenManager subscribed to navigation events")
            
            # Connect InputHandler to ScreenManager for delegation
            self.input_handler.screen_manager = self.screen_manager
            self.input_handler.game_controller = self
            print("🔗 InputHandler connected to ScreenManager for click delegation")

            # Step 3: Register InputHandler events
            self.event_manager.register("OVERLAY_TOGGLE", self.handle_overlay_toggle)
            self.event_manager.register("SCREEN_ADVANCE", self.handle_screen_advance)
            self.data_manager.load_all_data()

            # Step : Initialize all engines directly in GameController
            self.character_engine = initialize_character_engine(self.game_state, self.event_manager)
            self.inventory_engine = initialize_inventory_engine(self.game_state, self.data_manager.item_manager)
            self.commerce_engine = initialize_commerce_engine(self.game_state, self.data_manager.item_manager) 
            self.dialogue_engine = initialize_dialogue_engine(self.game_state)
            self.data_manager.dialogue_engine = self.dialogue_engine

            self.save_manager = SaveManager(self.game_state, self.character_engine)
            
            # Initialize IntroSequenceManager with SaveManager reference  
            self.intro_sequence_manager = IntroSequenceManager(self.event_manager, self.save_manager)
            print("🎬 IntroSequenceManager initialized with auto-save support")

            self.setup_event_listeners()
            #Register all screens with ScreenManager AFTER engines are ready
            self.screen_manager.register_all_screen_renders()
            
            
            print("📺 GC: All screens render functions registered ")           
            print(f"🔍 DEBUG: GC: EventManager has {self.event_manager.get_listener_count('START_GAME')} listeners for START_GAME")
            print(f"🔍 DEBUG: GC: All registered events: {list(self.event_manager.listeners.keys())}")
            print(f"🔍 DEBUG: GC: EventManager ID: {id(self.event_manager)}")
            
            # Register semantic action event listeners
        
            print("✅ GC:InputHandler initialized and integrated!")
            print("✅ GC: GameController: All systems initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ GameController: Data initialization failed: {e}")
            self.error_count += 1
            return False
    
    def handle_screen_advance(self, event_data):
        """Handle screen advance events from InputHandler"""
        current_screen = event_data.get("current_screen", self.game_state.screen)
        
        if current_screen == "game_title":
            self.game_state.screen = "developer_splash"
        elif current_screen == "developer_splash":
            self.game_state.screen = "main_menu"
    
    def setup_event_listeners(self):
        """Initialize all event listeners for professional event-driven architecture"""
        print("🎯 GC Setting up event listeners...")
        try:
            # Use the event manager we initialized directly in GameController
            event_manager = self.event_manager  # Direct access, no DataManager needed
            print(f"DEBUG: GC event_manager = {event_manager}")  # Add this line
            event_manager.register("NPC_CLICKED", self.handle_npc_clicked)
  
            print("✅ Event listeners registered successfully!")
        except Exception as e:
            print(f"❌ ERROR in setup_event_listeners: {e}")
            import traceback
            traceback.print_exc()
 
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
        """Handle screen transition events - UNIFIED SYSTEM"""
        target_screen = event_data.get("target_screen")
        source_screen = event_data.get("source_screen")
        
        print(f"🔄 SCREEN_CHANGE: {source_screen} -> {target_screen}")
        
        if target_screen:
            # Check BOTH screen systems for registration
            registered_in_controller = target_screen in self.screens
            registered_in_screen_manager = (hasattr(self, 'screen_manager') and 
                                        target_screen in self.screen_manager.get_registered_screens())
            
            if registered_in_controller or registered_in_screen_manager:
                self.game_state.screen = target_screen
                print(f"✅ Screen transition successful: {target_screen}")
            else:
                print(f"❌ UNREGISTERED SCREEN: {target_screen}")
                print(f"   Controller screens: {list(self.screens.keys())}")
                if hasattr(self, 'screen_manager'):
                    print(f"   ScreenManager screens: {self.screen_manager.get_registered_screens()}")
                print("   This screen needs to be registered!")
                # Stay on current screen instead of crashing
                return
        else:
            print("⚠️ SCREEN_CHANGE event without target_screen")

    def handle_universal_input(self, event) -> bool:
        """Debug version to see what's happening"""
        print(f"DEBUG: handle_universal_input called with event type: {event.type}")
        
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            print(f"DEBUG: Processing key: {key_name} (code: {event.key})")
            
            # Test with a simple key first
            if event.key == pygame.K_SPACE:
                print("DEBUG: SPACE key detected - advancing screen")
                # Try to advance to next screen
                if self.game_state.screen == "game_title":
                    self.game_state.screen = "developer_splash"
                    print("DEBUG: Changed to developer_splash")
                elif self.game_state.screen == "developer_splash":
                    self.game_state.screen = "main_menu"
                    print("DEBUG: Changed to main_menu")
                return True
                
            # Test ESC key
            elif event.key == pygame.K_ESCAPE:
                print("DEBUG: ESC key detected")
                return True
                
            print(f"DEBUG: Key {key_name} not handled")
        
        return True

    def _handle_escape_key(self) -> bool:
        """Handle ESC key - close overlays or advance screens"""
        # Check if any overlays are open
        overlay_attrs = [
            'help_screen_open', 'inventory_open', 'quest_log_open', 
            'character_sheet_open', 'load_screen_open', 'save_screen_open'
        ]
        
        for attr in overlay_attrs:
            if hasattr(self.game_state, attr) and getattr(self.game_state, attr):
                setattr(self.game_state, attr, False)
                print(f"DEBUG: ESC closed overlay: {attr}")
                return True
        
        # No overlays open - handle screen-specific ESC behavior
        print(f"DEBUG: ESC on screen: {self.game_state.screen}")
        return True

    def handle_input(self, event) -> bool:
        """Safe version with better mouse handling"""
        if event.type == pygame.QUIT:
            return False
        
        # Check if InputHandler is initialized
        if not self.input_handler:
            if event.type == pygame.KEYDOWN:
                return self.handle_universal_input(event)
            return True
        
        # Let InputHandler process keyboard input
        if event.type == pygame.KEYDOWN:
            return self.input_handler.process_keyboard_input(event, self.game_state)
        
        # Handle mouse clicks safely
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Try InputHandler mouse processing, but catch errors
            try:
                return self.input_handler.process_mouse_click(event.pos, self.game_state.screen)
            except Exception as e:
                print(f"DEBUG: InputHandler mouse click failed: {e}")
                print(f"DEBUG: Falling back to old mouse handling for {self.game_state.screen}")
                # Fall back to your existing screen-specific mouse handling
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

    def register_screen_clickables(self):
        #####################this should eventually move to screen handler###########
        """Register all screen clickable regions with InputHandler"""
        # This will replace your massive handle_screen_mouse_clicks method
        
        # Clear any existing clickables
        if self.input_handler:
            self.input_handler.clear_all_clickables()
        
        # Title screen - any click advances
        title_rect = pygame.Rect(0, 0, 1024, 768)  # Full screen clickable
        self.input_handler.register_clickable(
            "game_title", title_rect, "SCREEN_CHANGE", 
            {"target_screen": "developer_splash", "source_screen": "game_title"}
        )
        
        # Developer splash - any click advances  
        dev_rect = pygame.Rect(0, 0, 1024, 768)
        self.input_handler.register_clickable(
            "developer_splash", dev_rect, "SCREEN_CHANGE",
            {"target_screen": "main_menu", "source_screen": "developer_splash"}
        )
        
        # Main menu buttons (you'll need to get actual button rects)
        # For now, placeholder rects - we'll replace with real ones from screen drawing
        new_game_rect = pygame.Rect(400, 300, 200, 50)
        self.input_handler.register_clickable(
            "main_menu", new_game_rect, "SCREEN_CHANGE",
            {"target_screen": "stats", "source_screen": "main_menu"}
        )
        
        load_game_rect = pygame.Rect(400, 370, 200, 50)
        self.input_handler.register_clickable(
            "main_menu", load_game_rect, "OVERLAY_TOGGLE", {"overlay_id": "load_game"}
        )
        
        quit_rect = pygame.Rect(400, 440, 200, 50)
        self.input_handler.register_clickable(
            "main_menu", quit_rect, "QUIT_GAME", {}
        )
        
        print("🎯 Screen clickables registered with InputHandler")
    def run_current_screen(self):
        """
        CLEAN VERSION - Delegates to ScreenManager instead of massive if/elif chain
        This replaces the entire 1700+ line draw_current_screen() method
        """
        try:
            # Ensure screen manager is synced with game state
            if self.screen_manager.get_current_screen() != self.game_state.screen:
                # Sync ScreenManager with GameState (Single Data Authority)
                success = self.screen_manager.transition_to(
                    self.game_state.screen, 
                    self.game_state, 
                    save_history=False
                )
                if not success:
                    print(f"⚠️ Failed to sync screen: {self.game_state.screen}")
                    return False
            
            # Render current screen - this replaces the ENTIRE massive method
            success = self.screen_manager.render_current_screen(self.game_state)
            
            if success:
                self.frame_count += 1
            
            return success
            
        except Exception as e:
            print(f"❌ Error in run_current_screen: {e}")
            # ScreenManager handles its own fallback logic
            return False
    def register_screen(self, screen_name: str, screen_function: Callable):
        """
        Register a screen function with the controller
        This allows clean separation - screens don't need to know about each other
        """
        self.screens[screen_name] = screen_function
        print(f"📺 Screen registered: {screen_name}")
    
    def transition_to(self, new_screen: str, save_history: bool = True) -> bool:
        """
        Professional screen transition using ScreenManager
        This replaces manual game_state.screen assignments
        """
        success = self.screen_manager.transition_to(new_screen, self.game_state, save_history)
        
        if success:
            self.last_known_good_screen = new_screen
            # Update universal key state based on new screen
            self._update_universal_keys_state()
        
        return success
    
    def go_back(self) -> bool:
        """
        Navigate back to previous screen using ScreenManager
        """
        return self.screen_manager.go_back(self.game_state)

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
#####
    def handle_overlay_toggle(self, event_data):
        """Handle overlay toggle events from InputHandler"""
        overlay_id = event_data.get("overlay_id")
        
        if overlay_id == "inventory":
            if not self.game_state.inventory_open:
                self.close_all_overlays()
            self.game_state.toggle_inventory()
            
        elif overlay_id == "quest_log":
            if not self.game_state.quest_log_open:
                self.close_all_overlays()
            self.game_state.toggle_quest_log()
            
        elif overlay_id == "character_sheet":
            if not self.game_state.character_sheet_open:
                self.close_all_overlays()
            self.game_state.toggle_character_sheet()
            
        elif overlay_id == "help":
            if not self.game_state.help_screen_open:
                self.close_all_overlays()
            self.game_state.toggle_help()
            
        elif overlay_id == "load_game":
            if not getattr(self.game_state, 'load_screen_open', False):
                self.close_all_overlays()
            self.game_state.load_screen_open = not getattr(self.game_state, 'load_screen_open', False)
        
        print(f"🎛️  Overlay toggled: {overlay_id}")

    def handle_save_requested(self, event_data):
        """Handle save requests from InputHandler"""
        slot = event_data.get("slot", "quick_save")
        
        if slot == "quick_save":
            # Use slot 1 for quick save
            success = self.save_manager.save_game(1)  # Changed from self.save_game
            if success:
                print("💾 Quick save successful!")
            else:
                print("❌ Quick save failed!")
        else:
            # Direct slot save
            success = self.save_manager.save_game(slot)  # Changed from self.save_game

    def handle_screenshot_requested(self, event_data):
        """Handle screenshot requests from InputHandler"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            pygame.image.save(self.screen, filename)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")

    def handle_debug_toggle(self, event_data):
        """Handle debug toggle from InputHandler"""
        self.debug_mode = not self.debug_mode
        print(f"🔧 Debug mode: {'ON' if self.debug_mode else 'OFF'}")

    def handle_screen_advance(self, event_data):
        """Handle screen advance events from InputHandler"""
        current_screen = event_data.get("current_screen")
        
        if current_screen == "game_title":
            self.transition_to("developer_splash")
        elif current_screen == "developer_splash":
            self.transition_to("main_menu")
########
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
        
        pygame.quit()
        sys.exit()
    
    def toggle_debug_info(self):
        """
        Toggle debug information display
        """
        self.debug_mode = not self.debug_mode
        print(f"🐛 Debug mode: {'ON' if self.debug_mode else 'OFF'}")

    def handle_event_screen_change(self, event_data):
            """
            Handle SCREEN_CHANGE events from EventManager/InputHandler
            This integrates ScreenManager with your existing event system
            """
            target_screen = event_data.get("target_screen")
            source_screen = event_data.get("source_screen")
            
            if target_screen:
                print(f"🎯 Event-driven screen change: {source_screen} → {target_screen}")
                success = self.transition_to(target_screen)
                
                if success:
                    # Emit screen changed event for other systems
                    self.event_manager.emit("SCREEN_CHANGED", {
                        "old_screen": source_screen,
                        "new_screen": target_screen
                    })
                
                return success
            return False


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
            self.save_manager.save_game(save_slot=0)  # Auto-save slot

        # 2. Clear active game state
        if hasattr(self.character_engine, 'clear_active_portrait'):
            self.character_engine.clear_active_portrait(self.game_state)
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
        
         # Register title/menu screens
        #try:
        #    from screens.title_menu import draw_title_screen, draw_company_splash_screen, draw_main_menu
        #    controller.register_screen("game_title", draw_title_screen)           # Initial title
        #    controller.register_screen("developer_splash", draw_company_splash_screen)  # Company screen
        #    controller.register_screen("main_menu", draw_main_menu)               # Main menu
        #    print("✅ Title/menu screens registered!")
        #except ImportError as e:
        #    print(f"❌ IMPORT ERROR: {e}")
        #    print(f"⚠️ Title/menu screens not available: {e}")

        # Register character advancement screen
        try:
            from screens.character_advancement import draw_character_advancement
            controller.register_screen("character_advancement", draw_character_advancement)
            print("✅ Character advancement screen registered!")
        except ImportError as e:
            print(f"⚠️ Character advancement screen not available: {e}")

        # Register tavern screens
        #try:
        #    from screens.tavern import draw_tavern_main_screen, draw_npc_selection_screen, draw_npc_conversation_screen
        #    controller.register_screen("tavern_main", draw_tavern_main_screen)
        #    controller.register_screen("tavern_npcs", draw_npc_selection_screen)
        #    controller.register_screen("tavern_conversation", draw_npc_conversation_screen)
        #    controller.register_screen("bartender", draw_tavern_main_screen)  # If bartender uses same screen
        #    print("✅ Tavern screens registered!")
        #except ImportError as e:
        #    print(f"⚠️ Tavern screens not available: {e}")

        # Register Broken Blade
        #try:
        #    from screens.broken_blade import draw_broken_blade_main_screen 
        #    from screens.patron_selection import draw_patron_selection_screen  
        #    controller.register_screen("broken_blade_main", draw_broken_blade_main_screen)
        #    controller.register_screen("patron_selection", draw_patron_selection_screen)
        #    print("✅ Broken Blade screens registered!")
        #except ImportError as e:
        #    print(f"⚠️ Broken Blade screens not available: {e}")
        
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
        
        # Register shopping screens (NEW ARCHITECTURE)
        #try:
        #    from screens.shopping import register_shop_screens
        #    register_shop_screens(controller)
        #    print("✅ Shopping screens registered via shopping module!")
        #except ImportError as e:
        #    print(f"⚠️ Shopping screens not available: {e}")

        # Register save/load screens
        #try:
        #    from screens.load_game import draw_load_game_screen
        #    from screens.save_game import draw_save_game_screen
        #    controller.register_screen("load_screen", draw_load_game_screen)
        #    controller.register_screen("save_screen", draw_save_game_screen)
        #    print("✅ Save/Load screens registered!")
        #except ImportError as e:
        #    print(f"⚠️ Save/Load screens not available: {e}")


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



