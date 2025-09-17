# screens/redstone_town_navigation.py
"""
Redstone Town Navigation - Tile-Based Movement System
Professional implementation integrating with Terror in Redstone architecture

This screen handles tile-based movement around the town, building interactions,
and transitions to your existing dialogue/shopping systems.
"""

import pygame
import sys
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text
from utils.party_display import draw_party_status_panel, PARTY_PANEL_WIDTH

# Import our town map data
try:
    from data.maps.redstone_town_map import *
except ImportError:
    print("⚠️ Town map data not found - create data/maps/redstone_town_map.py")
    # Fallback minimal data
    TOWN_WIDTH, TOWN_HEIGHT = 16, 12
    TOWN_SPAWN_X, TOWN_SPAWN_Y = 8, 6
    TILE_SIZE = 64
    WALKABLE_TILES = {'street'}
    def get_tile_type(x, y): return 'street'
    def is_walkable(x, y): return True
    def get_building_info(x, y): return None
    def get_tile_color(x, y): return (80, 60, 40)

class RedstoneTownNavigation:
    """
    Town exploration with scrolling camera system
    
    INTEGRATION POINTS:
    - Uses existing GameState for player position
    - Integrates with ScreenManager for building transitions
    - Works with InputHandler for movement keys
    - Maintains party status display consistency
    """
    
    def __init__(self):
        # Calculate display area (accounting for party panel)
        self.display_width = SCREEN_WIDTH - PARTY_PANEL_WIDTH - 10
        self.display_height = LAYOUT_IMAGE_HEIGHT
        
        # Camera system
        self.camera_x = 0
        self.camera_y = 0
        
        # Movement timing (prevents key repeat madness)
        self.move_timer = 0
        self.move_delay = 200  # 200ms between moves
        self.can_move = True
        
        # Current building interaction
        self.current_building = None
        
        print("🏘️ Town exploration system initialized")
    
    def update_player_position(self, game_state):
        """Initialize or update player position in town"""
        if not hasattr(game_state, 'town_player_x'):
            # First time in town - set spawn position
            game_state.town_player_x = TOWN_SPAWN_X
            game_state.town_player_y = TOWN_SPAWN_Y
            print(f"🚶 Player spawned in town at ({TOWN_SPAWN_X}, {TOWN_SPAWN_Y})")
        
        self.update_camera(game_state.town_player_x, game_state.town_player_y)
    
    def update_camera(self, player_x, player_y):
        """Center camera on player with bounds checking"""
        # Calculate player pixel position
        player_pixel_x = player_x * TILE_SIZE
        player_pixel_y = player_y * TILE_SIZE
        
        # Calculate display area for centering
        visible_width = self.display_width
        visible_height = self.display_height
        
        # Center camera on player
        self.camera_x = player_pixel_x - visible_width // 2
        self.camera_y = player_pixel_y - visible_height // 2
        
        # Keep camera within map bounds
        max_camera_x = (TOWN_WIDTH * TILE_SIZE) - visible_width
        max_camera_y = (TOWN_HEIGHT * TILE_SIZE) - visible_height
        
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))
    
    def handle_movement_input(self, keys, game_state, dt):
        """Handle player movement with timing"""
        if not self.can_move:
            # Update move timer
            self.move_timer += dt
            if self.move_timer >= self.move_delay:
                self.can_move = True
                self.move_timer = 0
            return
        
        # Check for movement input
        new_x = game_state.town_player_x
        new_y = game_state.town_player_y
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= 1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += 1
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= 1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += 1
        
        # Try to move if position changed
        if new_x != game_state.town_player_x or new_y != game_state.town_player_y:
            if is_walkable(new_x, new_y):
                game_state.town_player_x = new_x
                game_state.town_player_y = new_y
                self.update_camera(new_x, new_y)
                self.can_move = False  # Start move delay
                
                # Check for building interaction
                self.current_building = get_building_info(new_x, new_y)
                if self.current_building:
                    print(f"🏢 Near building: {self.current_building['name']}")
    
    def handle_interaction_input(self, keys, game_state, controller):
        """Handle building entry and interaction"""
        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]) and self.current_building:
            building_screen = self.current_building['screen']
            print(f"🚪 Entering {self.current_building['name']} -> {building_screen}")
            
            # Transition to building screen using existing system
            if controller:
                controller.event_manager.emit("SCREEN_CHANGE", {
                    'target_screen': building_screen,
                    'source': 'town_exploration'
                })
    
    def draw_town_map(self, surface):
        """Draw visible portion of town map"""
        # Calculate visible tile range
        start_tile_x = max(0, self.camera_x // TILE_SIZE)
        start_tile_y = max(0, self.camera_y // TILE_SIZE)
        end_tile_x = min(TOWN_WIDTH, (self.camera_x + self.display_width) // TILE_SIZE + 1)
        end_tile_y = min(TOWN_HEIGHT, (self.camera_y + self.display_height) // TILE_SIZE + 1)
        
        # Draw visible tiles
        for map_y in range(start_tile_y, end_tile_y):
            for map_x in range(start_tile_x, end_tile_x):
                # Get tile color
                tile_color = get_tile_color(map_x, map_y)
                
                # Calculate screen position
                screen_x = (map_x * TILE_SIZE) - self.camera_x
                screen_y = (map_y * TILE_SIZE) - self.camera_y
                
                # Draw tile
                pygame.draw.rect(surface, tile_color, 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                
                # Draw tile border for grid effect
                pygame.draw.rect(surface, BLACK, 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)
    
    def draw_player(self, surface, game_state):
        """Draw player character on map"""
        # Calculate player screen position
        player_screen_x = (game_state.town_player_x * TILE_SIZE) - self.camera_x
        player_screen_y = (game_state.town_player_y * TILE_SIZE) - self.camera_y
        
        # Draw player as red circle (classic RPG style)
        center_x = player_screen_x + TILE_SIZE // 2
        center_y = player_screen_y + TILE_SIZE // 2
        pygame.draw.circle(surface, RED, (center_x, center_y), TILE_SIZE // 3)
        
        # Draw player border
        pygame.draw.circle(surface, WHITE, (center_x, center_y), TILE_SIZE // 3, 2)
    
    def draw_interaction_prompt(self, surface, fonts):
        """Draw building interaction prompt"""
        if self.current_building:
            action_text = f"Press ENTER to {self.current_building['action']}"
            
            # Position prompt at bottom of display area
            prompt_y = LAYOUT_IMAGE_Y + LAYOUT_IMAGE_HEIGHT - 40
            
            # Create prompt background
            prompt_font = fonts.get('fantasy_small', fonts['normal'])
            text_surface = prompt_font.render(action_text, True, YELLOW)
            text_width = text_surface.get_width()
            
            # Center horizontally in display area
            prompt_x = (self.display_width - text_width) // 2
            
            # Background box
            bg_rect = pygame.Rect(prompt_x - 10, prompt_y - 5, text_width + 20, 30)
            pygame.draw.rect(surface, BLACK, bg_rect)
            pygame.draw.rect(surface, WHITE, bg_rect, 2)
            
            # Draw text
            surface.blit(text_surface, (prompt_x, prompt_y))
    
    def render(self, surface, game_state, fonts, images, controller=None):
        """Main render function - integrates with ScreenManager"""
        surface.fill(BLACK)
        
        # Update player position and camera
        self.update_player_position(game_state)
        
        # === PARTY STATUS PANEL (RIGHT SIDE) ===
        draw_party_status_panel(surface, game_state, fonts)
        
        # === TOWN MAP AREA (LEFT SIDE) ===
        map_area_rect = pygame.Rect(0, LAYOUT_IMAGE_Y, self.display_width, self.display_height)
        
        # Draw border around map area
        draw_border(surface, 0, LAYOUT_IMAGE_Y, self.display_width, self.display_height)
        
        # Create subsurface for map rendering (prevents drawing outside bounds)
        map_surface = surface.subsurface(6, LAYOUT_IMAGE_Y + 6, 
                                        self.display_width - 12, self.display_height - 12)
        
        # Draw town map
        self.draw_town_map(map_surface)
        
        # Draw player
        self.draw_player(map_surface, game_state)
        
        # === UI ELEMENTS ===
        # Title
        title_font = fonts.get('fantasy_large', fonts['header'])
        draw_centered_text(surface, "REDSTONE TOWN", title_font, 
                          LAYOUT_IMAGE_Y - 30, YELLOW, screen_width=self.display_width)
        
        # Player position debug info
        pos_text = f"Position: ({game_state.town_player_x}, {game_state.town_player_y})"
        debug_font = fonts.get('fantasy_tiny', fonts['small'])
        pos_surface = debug_font.render(pos_text, True, WHITE)
        surface.blit(pos_surface, (10, LAYOUT_IMAGE_Y + self.display_height + 10))
        
        # Interaction prompt
        self.draw_interaction_prompt(surface, fonts)
        
        # === INSTRUCTION PANEL ===
        instruction_y = LAYOUT_DIALOG_Y
        draw_border(surface, 20, instruction_y, SCREEN_WIDTH - 40, LAYOUT_DIALOG_HEIGHT)
        
        instructions = [
            "Use ARROW KEYS or WASD to move around town",
            "Press ENTER near buildings to enter them",
            "ESC to access game menu"
        ]
        
        text_y = instruction_y + 20
        for instruction in instructions:
            draw_centered_text(surface, instruction, fonts.get('fantasy_small', fonts['normal']),
                             text_y, WHITE)
            text_y += 25
        
        return {}  # No clickable areas for now
    
    def update(self, dt, keys, game_state, controller=None):
        """Update game state - called by main game loop"""
        # Handle movement
        self.handle_movement_input(keys, game_state, dt)
        
        # Handle interactions
        self.handle_interaction_input(keys, game_state, controller)

# === INTEGRATION FUNCTION FOR SCREEN_MANAGER ===
def render_town_navigation(surface, game_state, fonts, images, controller=None):
    """
    Function for ScreenManager integration
    
    USAGE: Register this with your ScreenManager like:
    screen_manager.register_render_function("redstone_town_navigation", render_town_navigation)
    """
    global _town_navigation_instance
    
    # Create singleton instance
    if '_town_navigation_instance' not in globals():
        _town_navigation_instance = RedstoneTownNavigation()
    
    # Handle input if keys are available
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16  # Approximate 60 FPS
        _town_navigation_instance.update(dt, keys, game_state, controller)
    
    # Render the screen
    return _town_navigation_instance.render(surface, game_state, fonts, images, controller)