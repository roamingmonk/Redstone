"""
Terror in Redstone - Main Game File (CLEAN ARCHITECTURE)
Pure GameController bootstrap - all logic moved to appropriate modules
"""

import pygame
import sys
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
    
    # Create the game controller - this handles EVERYTHING now
    controller = GameController(screen, game_state, fonts, images, data_manager)

    def handle_quit_event(event_data):
        global running
        print("🎮 QUIT_GAME: Exiting application")
        controller.quit_game()
        running = False

    # NEW: Centralize all data loading here!
    controller.initialize_data_systems()

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
            # Controller returns False if we should quit
            if not controller.handle_input(event):
                running = False
                break
        
        # Controller handles all screen rendering
        controller.run_current_screen()
        
        # Draw debug overlay
        controller.draw_debug_overlay()

        # Standard pygame housekeeping
        pygame.display.flip()
        clock.tick(60)
    
    # Clean shutdown handled by controller
    controller.shutdown()

if __name__ == "__main__":
    main()