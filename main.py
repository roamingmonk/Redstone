"""
Terror in Redstone - Main Game File (CLEAN ARCHITECTURE)
Pure GameController bootstrap - all logic moved to appropriate modules
"""

import pygame
import sys
import traceback
sys.path.append('.')

# Essential imports for bootstrap only
from game_state import GameState
from utils.constants import load_fonts, load_images, SCREEN_WIDTH, SCREEN_HEIGHT
from core.game_controller import GameController, GameConfig, ScreenRegistry
from game_logic.data_manager import get_data_manager, initialize_game_data

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

def main():
    """Main game loop - Clean Architecture Version"""
    
    # Initialize everything
    screen, clock, fonts, images = initialize_game()
    
    # Initialize game data and state
    data_manager = get_data_manager()
    game_state = GameState()
    
    # Create GameController (Phase 1: Infrastructure only)
    controller = GameController(screen, game_state, fonts, images, data_manager)
    print("GameController created (Phase 1: Infrastructure)")

    # Initialize all systems with bulletproof architecture (Phases 2-4)
    try:
        init_result = controller.initialize_all_systems()

        # Check initialization result
        if not init_result.success:
            print(f"❌ GameController initialization failed!")
            print(f"   Phase reached: {init_result.phase_reached}")
            print(f"   Systems created: {init_result.systems_created}")
            print(f"   Errors: {init_result.errors}")
            print(f"   Total time: {init_result.total_time:.2f}s")
            
            # Log detailed error information
            for error in init_result.errors:
                print(f"   ERROR: {error}")
            
            pygame.quit()
            sys.exit(1)

        # Success! Log initialization details
        print(f"✅ GameController fully initialized!")
        print(f"   Phase: {init_result.phase_reached}")
        print(f"   Systems: {len(init_result.systems_created)}")
        print(f"   Time: {init_result.total_time:.2f}s")
        print(f"   Validations: {sum(init_result.validation_results.values())}/{len(init_result.validation_results)} passed")

        # Log any validation failures (non-fatal)
        failed_validations = [k for k, v in init_result.validation_results.items() if not v]
        if failed_validations:
            print(f"⚠️ Validation warnings: {failed_validations}")

    except Exception as e:
        print(f"❌ Fatal initialization error: {e}")
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

    def handle_quit_event(event_data):
        global running
        print("🎮 QUIT_GAME: Exiting application")
        controller.shutdown()
        running = False

    controller.event_manager.register('QUIT_GAME', handle_quit_event)
    
    # Apply configuration and register all screens
    GameConfig.apply_to_controller(controller)
    ScreenRegistry.register_all_screens(controller)
    
    game_state.screen = "game_title"  # Start with the game title screen

    # Enable debug mode
    controller.debug_mode = True
    
    running = True
    
    print("=== TERROR IN REDSTONE ===")
    print("Clean GameController architecture initialized!")
    print("All input and rendering handled by GameController")
    print("Universal hotkeys: I/Q/C/H/L/F5/F7/F10/ESC")
    print("==========================")
    
    # CLEAN MAIN GAME LOOP - GameController handles everything
    while running:
        # Pass ALL events to controller - single entry point
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
            # Delegate events to InputHandler
            if controller.input_handler:
                controller.input_handler.handle_input(event)
        
        # Controller handles all screen rendering
        controller.run_current_screen()

        # Standard pygame housekeeping
        pygame.display.flip()
        clock.tick(60)
    
    # Clean shutdown handled by controller
    controller.shutdown()

if __name__ == "__main__":
    main()