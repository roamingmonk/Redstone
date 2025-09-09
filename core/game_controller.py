# core/game_controller.py
"""
Professional Game Controller with Industry-Standard Initialization
Based on Unreal Engine and Unity initialization patterns
"""

import pygame
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Import managers and engines
from game_logic.event_manager import initialize_event_manager
from game_logic.save_manager import SaveManager
from game_logic.data_manager import get_data_manager
from game_logic.character_engine import initialize_character_engine
from game_logic.inventory_engine import initialize_inventory_engine
from game_logic.commerce_engine import initialize_commerce_engine
from game_logic.dialogue_engine import initialize_dialogue_engine
from game_logic.quest_engine import initialize_quest_engine
from ui.screen_manager import ScreenManager
from input_handler import InputHandler
from screens.intro_scenes import IntroSequenceManager


class InitializationPhase(Enum):
    """Track initialization progress for debugging and validation"""
    NOT_STARTED = "not_started"
    INFRASTRUCTURE = "infrastructure"
    DEPENDENCIES = "dependencies"
    INTEGRATION = "integration"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class SystemDependencies:
    """Define what each system needs to initialize properly"""
    event_manager: bool = False
    data_manager: bool = False
    character_engine: bool = False
    input_handler: bool = False
    screen_manager: bool = False

@dataclass
class InitializationResult:
    """Result of initialization attempt with detailed feedback"""
    success: bool
    phase_reached: InitializationPhase
    systems_created: List[str]
    errors: List[str]
    validation_results: Dict[str, bool]
    total_time: float

class GameController:
    """
    Professional Game Controller with Bulletproof Initialization
    
    Follows the "Initialize Once, Use Everywhere" pattern used in commercial game engines.
    Each system is initialized exactly once with all required dependencies available.
    """
    
    def __init__(self, screen: pygame.Surface, game_state, fonts: Dict, images: Dict, data_manager):
        """
        Phase 1: Infrastructure Only
        Create only systems with zero dependencies
        """
        # Core infrastructure (no dependencies)
        self.screen = screen
        self.game_state = game_state
        self.fonts = fonts
        self.images = images
        self.data_manager = data_manager
        
        # Initialization state tracking
        self.current_phase = InitializationPhase.NOT_STARTED
        self.initialization_start_time = None
        self.systems_created = []
        self.initialization_errors = []
        
        # System registry (will be populated in phases 2-3)
        self.event_manager = None
        self.input_handler = None
        self.screen_manager = None
        self.save_manager = None
        self.character_engine = None
        self.inventory_engine = None
        self.commerce_engine = None
        self.dialogue_engine = None
        self.intro_sequence_manager = None
        
        # Navigation state
        self.previous_screen = None
        self.screen_history = []
        
        # Universal input state
        self.universal_keys_enabled = True
        self.escape_exits_game = True
        
        # Error recovery
        self.last_known_good_screen = "game_title"
        self.error_count = 0
        
        # Debug features
        self.debug_mode = False
        self.frame_count = 0
        self.last_fps_time = pygame.time.get_ticks()
        
        print("🎮 GameController Phase 1 (Infrastructure) complete")
    
    def initialize_all_systems(self) -> InitializationResult:
        """
        Master initialization method following industry dependency injection patterns
        Returns detailed result for debugging and error handling
        """
        self.initialization_start_time = datetime.now()
        self.current_phase = InitializationPhase.NOT_STARTED
        
        try:
            # Phase 2: Core Dependencies
            self._initialize_core_dependencies()
            
            # Phase 3: System Integration  
            self._initialize_system_integration()
            
            # Phase 4: Validation
            validation_results = self._validate_all_systems()
            
            self.current_phase = InitializationPhase.COMPLETE
            total_time = (datetime.now() - self.initialization_start_time).total_seconds()
            
            return InitializationResult(
                success=True,
                phase_reached=InitializationPhase.COMPLETE,
                systems_created=self.systems_created.copy(),
                errors=self.initialization_errors.copy(),
                validation_results=validation_results,
                total_time=total_time
            )
            
        except Exception as e:
            self.current_phase = InitializationPhase.FAILED
            error_msg = f"Initialization failed in phase {self.current_phase}: {e}"
            self.initialization_errors.append(error_msg)
            print(f"❌ {error_msg}")
            
            total_time = (datetime.now() - self.initialization_start_time).total_seconds()
            
            return InitializationResult(
                success=False,
                phase_reached=self.current_phase,
                systems_created=self.systems_created.copy(),
                errors=self.initialization_errors.copy(),
                validation_results={},
                total_time=total_time
            )
    
    def _initialize_core_dependencies(self):
        """
        Phase 2: Initialize systems that other systems depend on
        Order matters here - each system must have its dependencies ready
        """
        self.current_phase = InitializationPhase.DEPENDENCIES
        print("🔧 GameController Phase 2: Core Dependencies")
        
        # Step 1: EventManager (no dependencies)
        self.event_manager = initialize_event_manager()
        self._mark_system_created("event_manager")
        
        # Step 2: InputHandler (requires: EventManager)
        self._validate_dependency("event_manager", self.event_manager)
        self.input_handler = InputHandler(self.event_manager)
        self.input_handler.enable_debug_input(True)
        self._mark_system_created("input_handler")
        
        # Step 3: ScreenManager (requires: EventManager)
        self.screen_manager = ScreenManager(
            event_manager=self.event_manager,
            screen=self.screen,
            fonts=self.fonts,
            images=self.images
        )
        self._mark_system_created("screen_manager")
        
        # Step 4: Load all game data (no engine dependencies)
        self.data_manager.load_all_data()
        self._mark_system_created("data_loaded")
        
        # Step 5: Initialize engines (requires: EventManager, DataManager)
        self._validate_dependency("event_manager", self.event_manager)
        self._validate_dependency("data_manager", self.data_manager)
        
        self.character_engine = initialize_character_engine(self.game_state, self.event_manager)
        self.inventory_engine = initialize_inventory_engine(self.game_state, self.data_manager.item_manager)
        self.commerce_engine = initialize_commerce_engine(self.game_state, self.data_manager.item_manager)
        self.dialogue_engine = initialize_dialogue_engine(self.game_state)
        self.quest_engine = initialize_quest_engine(self.game_state, self.event_manager)

        self._mark_system_created("character_engine")
        self._mark_system_created("inventory_engine")
        self._mark_system_created("commerce_engine")
        self._mark_system_created("dialogue_engine")
        self._mark_system_created("quest_engine")
        
        # Step 6: SaveManager (requires: GameState, CharacterEngine, EventManager)
        self._validate_dependency("character_engine", self.character_engine)
        self._validate_dependency("event_manager", self.event_manager)
        
        self.save_manager = SaveManager(
            game_state=self.game_state,
            character_engine=self.character_engine,
            event_manager=self.event_manager
        )
        self._mark_system_created("save_manager")
        
        # Step 7: IntroSequenceManager (requires: EventManager, SaveManager)
        self._validate_dependency("save_manager", self.save_manager)
        
        self.intro_sequence_manager = IntroSequenceManager(
            self.event_manager, 
            self.save_manager
        )
        self._mark_system_created("intro_sequence_manager")
        
        print("✅ Phase 2 Complete: All core dependencies initialized")
    
    def _initialize_system_integration(self):
        """
        Phase 3: Connect systems together and register event handlers
        All systems exist at this point, so cross-references are safe
        """
        self.current_phase = InitializationPhase.INTEGRATION
        print("🔗 GameController Phase 3: System Integration")
        
        # Connect InputHandler to ScreenManager for delegation
        self.input_handler.screen_manager = self.screen_manager
        self.input_handler.game_controller = self
        
        # Connect ScreenManager to other systems
        self.screen_manager.input_handler = self.input_handler
        self.screen_manager.event_manager = self.event_manager
        self.screen_manager._current_game_controller = self  # Give ScreenManager access to GameController

        # Register screen transition handlers
        self.event_manager.register("SCREEN_CHANGE", self.screen_manager._handle_screen_change_event)
        self.event_manager.register("SCREEN_ADVANCE", self.screen_manager._handle_screen_advance_event)
        
        # Register input event handlers
        
        self.event_manager.register("SCREEN_ADVANCE", self.handle_screen_advance)
        
        # Set up ScreenManager screen registry
        self.screen_manager.register_all_screen_renders()

        # Register ScreenManager overlay events
        self.screen_manager.register_overlay_events()
        
        # Sync ScreenManager with current game state
        self.screen_manager.transition_to(self.game_state.screen, self.game_state, save_history=False)
        
        print("✅ Phase 3 Complete: System integration finished")
    
    def _validate_dependency(self, dependency_name: str, dependency_object: Any):
        """Validate that a required dependency is available"""
        if dependency_object is None:
            raise RuntimeError(f"Required dependency '{dependency_name}' is None")
        print(f"✓ Dependency validated: {dependency_name}")
    
    def _mark_system_created(self, system_name: str):
        """Track system creation for debugging"""
        self.systems_created.append(system_name)
        print(f"✓ System created: {system_name}")
    
    def _validate_all_systems(self) -> Dict[str, bool]:
        """
        Comprehensive system validation
        Ensures all systems are properly initialized and connected
        """
        validation_results = {}
        
        # Core systems validation
        validation_results["event_manager"] = self.event_manager is not None
        validation_results["input_handler"] = self.input_handler is not None
        validation_results["screen_manager"] = self.screen_manager is not None
        validation_results["save_manager"] = self.save_manager is not None
        
        # Engine validation
        validation_results["character_engine"] = self.character_engine is not None
        validation_results["inventory_engine"] = self.inventory_engine is not None
        validation_results["commerce_engine"] = self.commerce_engine is not None
        validation_results["dialogue_engine"] = self.dialogue_engine is not None
        
        # Integration validation
        validation_results["input_screen_connection"] = (
            hasattr(self.input_handler, 'screen_manager') and 
            self.input_handler.screen_manager is not None
        )
        
        validation_results["event_registrations"] = (
            len(self.event_manager.listeners.get("OVERLAY_TOGGLE", [])) > 0 and
            len(self.event_manager.listeners.get("SCREEN_ADVANCE", [])) > 0
        )
        
        # Data loading validation
        validation_results["data_loaded"] = (
            hasattr(self.data_manager, 'item_manager') and
            hasattr(self.data_manager.item_manager, 'items_data') and
            self.data_manager.item_manager.items_data is not None
        )
        
        # Report validation results
        failed_validations = [k for k, v in validation_results.items() if not v]
        if failed_validations:
            print(f"⚠️ Failed validations: {failed_validations}")
        else:
            print("✅ All system validations passed")
        
        return validation_results
    
    def get_initialization_status(self) -> Dict[str, Any]:
        """Get detailed initialization status for debugging"""
        total_time = None
        if self.initialization_start_time:
            total_time = (datetime.now() - self.initialization_start_time).total_seconds()
        
        return {
            "phase": self.current_phase.value,
            "systems_created": len(self.systems_created),
            "systems_list": self.systems_created.copy(),
            "error_count": len(self.initialization_errors),
            "errors": self.initialization_errors.copy(),
            "total_time": total_time,
            "memory_usage": {
                "event_manager": self.event_manager is not None,
                "save_manager": self.save_manager is not None,
                "engines": {
                    "character": self.character_engine is not None,
                    "inventory": self.inventory_engine is not None,
                    "commerce": self.commerce_engine is not None,
                    "dialogue": self.dialogue_engine is not None
                }
            }
        }
    

    
    def handle_screen_advance(self, event_data):
        """Handle screen advance events from InputHandler"""
        current_screen = event_data.get("current_screen", self.game_state.screen)
        
        if current_screen == "game_title":
            self.game_state.screen = "developer_splash"
        elif current_screen == "developer_splash":
            self.game_state.screen = "main_menu"
    
    def close_all_overlays(self):
        """Close all open overlays"""
        self.game_state.inventory_open = False
        self.game_state.quest_log_open = False
        self.game_state.character_sheet_open = False
        self.game_state.help_screen_open = False
        if hasattr(self.game_state, 'load_screen_open'):
            self.game_state.load_screen_open = False
    
    def register_screen(self, screen_name: str, draw_function):
        """
        Register a screen with its drawing function
        Compatibility method for ScreenRegistry
        """
        if hasattr(self, 'screen_manager') and self.screen_manager:
            # Delegate to ScreenManager
            self.screen_manager.register_render_function(screen_name, draw_function)
            print(f"Screen registered via ScreenManager: {screen_name}")
        else:
            print(f"Warning: Cannot register screen {screen_name} - ScreenManager not available")

    
    def run_current_screen(self):
        """
        CLEAN VERSION - Delegates to ScreenManager instead of massive if/elif chain
        This replaces the entire 1700+ line draw_current_screen() method
        """
        try:
            current_screen = self.game_state.screen
            sm_screen = self.screen_manager.get_current_screen()
            
            # Debug logging
            if current_screen != sm_screen:
                print(f"🔄 Screen sync needed: GameState='{current_screen}' vs ScreenManager='{sm_screen}'")
            
            # Ensure screen manager is synced with game state
            if sm_screen != current_screen:
                success = self.screen_manager.transition_to(current_screen, self.game_state, save_history=False)
                if not success:
                    print(f"⚠️ Failed to sync screen: {current_screen}")
                    return False
                print(f"✅ Screen synced to: {current_screen}")
            
            # Render current screen
            success = self.screen_manager.render_current_screen(self.game_state)
            
            if not success:
                print(f"❌ Render failed for screen: {current_screen}")
                # Add more debug info
                registered_screens = list(self.screen_manager.render_functions.keys()) if hasattr(self.screen_manager, 'render_functions') else []
                print(f"📋 Registered screens: {registered_screens}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error in run_current_screen: {e}")
            self.error_count += 1
            return False
        
    def shutdown(self):
        """
        Professional shutdown coordination with complete resource cleanup
        Coordinates autosave, UI cleanup, and system shutdown across all engines
        """
        print("🏰 Terror in Redstone shutting down...")
        
        # Step 1: Auto-save current progress (if in saveable state)
        if hasattr(self, 'save_manager') and self.save_manager:
            try:
                if self.save_manager.can_save_load():
                    print("💾 Auto-saving progress before shutdown...")
                    success = self.save_manager.save_game(save_slot=0)  # Auto-save slot
                    if success:
                        print("✅ Auto-save completed successfully")
                    else:
                        print("⚠️ Auto-save failed, but continuing shutdown")
                else:
                    print("ℹ️ Game not in saveable state - skipping auto-save")
            except Exception as e:
                print(f"⚠️ Auto-save error during shutdown: {e}, continuing...")
        
        # Step 2: Clear active portrait resources
        if hasattr(self, 'character_engine') and self.character_engine:
            try:
                self.character_engine.clear_active_portrait(self.game_state)
                print("🖼️ Portrait resources cleared")
            except Exception as e:
                print(f"⚠️ Portrait cleanup error: {e}, continuing...")
        
        # Step 3: Close all overlay states cleanly
        try:
            self.close_all_overlays()
            print("🗂️ All overlays closed")
        except Exception as e:
            print(f"⚠️ Overlay cleanup error: {e}, continuing...")
        
        # Step 4: Audio cleanup (future-proofing)
        try:
            pygame.mixer.quit()
            print("🔊 Audio resources released")
        except Exception as e:
            # Audio might not be initialized, or pygame.mixer might not exist
            print(f"ℹ️ Audio cleanup skipped: {e}")
        
        # Step 5: Clean pygame shutdown
        try:
            pygame.quit()
            print("🎮 Pygame resources released")
        except Exception as e:
            print(f"⚠️ Pygame cleanup error: {e}, continuing...")
        
        # Step 6: Final system exit
        print("⚔️ Farewell, brave adventurer!")
        import sys
        sys.exit()

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

        # Register character advancement screen
        try:
            from screens.character_advancement import draw_character_advancement
            controller.register_screen("character_advancement", draw_character_advancement)
            print("✅ Character advancement screen registered!")
        except ImportError as e:
            print(f"⚠️ Character advancement screen not available: {e}")

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



