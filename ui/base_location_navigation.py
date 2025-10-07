# ui/base_location_navigation.py
"""
NavigationRenderer - Shared navigation logic utility
Handles camera, movement, rendering, and input for all tile-based locations
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text
from utils.party_display import draw_party_status_panel, PARTY_PANEL_WIDTH
from utils.tile_graphics import get_tile_graphics_manager
#from utils.constants import RED, YELLOW  

class NavigationRenderer:
    """Utility class for shared tile-based navigation logic"""
    
    def __init__(self, config):
        # Store configuration
        self.config = config
        self.map_functions = config['map_functions']
        self.tile_size = config.get('tile_size', 64)
        self.map_width = config['map_width']
        self.map_height = config['map_height']
        
        # Store color function from map (data-driven colors)
        self.get_tile_color = self.map_functions.get('get_tile_color', None)

        # Display area calculation
        self.display_width = SCREEN_WIDTH - PARTY_PANEL_WIDTH - 10
        self.display_height = LAYOUT_IMAGE_HEIGHT
        
        # Camera and movement state
        self.camera_x = 0
        self.camera_y = 0
        self.move_delay = 150
        self.last_move_time = 0
        self.keys_pressed_last_frame = set()
        self.player_direction = 'down'
        
        # Graphics manager
        self.graphics_manager = get_tile_graphics_manager()
        
    def update_camera(self, player_x, player_y):
        """Center camera on player with bounds checking"""
        player_pixel_x = player_x * self.tile_size
        player_pixel_y = player_y * self.tile_size
        
        self.camera_x = player_pixel_x - self.display_width // 2
        self.camera_y = player_pixel_y - self.display_height // 2
        
        max_camera_x = (self.map_width * self.tile_size) - self.display_width
        max_camera_y = (self.map_height * self.tile_size) - self.display_height
        
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))
    
    def handle_movement(self, keys, player_x, player_y):
        """Handle movement input and return new position"""
        current_time = pygame.time.get_ticks()
        keys_pressed_this_frame = set()
        new_x, new_y = player_x, player_y
        movement_attempted = False
        
        # Check movement keys
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            keys_pressed_this_frame.add('up')
            self.player_direction = 'up'
            new_y -= 1
            movement_attempted = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            keys_pressed_this_frame.add('down')
            self.player_direction = 'down'
            new_y += 1
            movement_attempted = True
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            keys_pressed_this_frame.add('left')
            self.player_direction = 'left'
            new_x -= 1
            movement_attempted = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            keys_pressed_this_frame.add('right')
            self.player_direction = 'right'
            new_x += 1
            movement_attempted = True
        
        # Process movement with timing
        moved = False
        if movement_attempted and (current_time - self.last_move_time >= self.move_delay):
            new_key_pressed = bool(keys_pressed_this_frame - self.keys_pressed_last_frame)
            
            if new_key_pressed or (current_time - self.last_move_time >= self.move_delay * 2):
                if (new_x != player_x or new_y != player_y):
                    if self.map_functions['is_walkable'](new_x, new_y):
                        self.last_move_time = current_time
                        moved = True
                        
        self.keys_pressed_last_frame = keys_pressed_this_frame
        
        if moved:
            return new_x, new_y
        return player_x, player_y
    
    def draw_map(self, surface, fonts, player_x, player_y, main_surface=None):
        """Draw the map tiles"""
        # Calculate visible tile range
        start_tile_x = max(0, self.camera_x // self.tile_size)
        start_tile_y = max(0, self.camera_y // self.tile_size)
        end_tile_x = min(self.map_width, (self.camera_x + self.display_width) // self.tile_size + 1)
        end_tile_y = min(self.map_height, (self.camera_y + self.display_height) // self.tile_size + 1)
        
                # Draw visible tiles
        for map_y in range(start_tile_y, end_tile_y):
            for map_x in range(start_tile_x, end_tile_x):
                tile_type = self.map_functions['get_tile_type'](map_x, map_y)
                screen_x = (map_x * self.tile_size) - self.camera_x
                screen_y = (map_y * self.tile_size) - self.camera_y
                
                # CHANGED: Get tile with map-specific color if available
                if self.get_tile_color:
                    # Map provides its own colors (data-driven approach)
                    custom_color = self.get_tile_color(map_x, map_y)
                    tile_image = self.graphics_manager.get_tile_image(
                        tile_type, 
                        custom_color=custom_color
                    )
                else:
                    # Use default TileGraphicsManager colors
                    tile_image = self.graphics_manager.get_tile_image(tile_type)
                
                surface.blit(tile_image, (screen_x, screen_y))
        
        # Draw player sprite using graphics manager
        player_screen_x = (player_x * self.tile_size) - self.camera_x
        player_screen_y = (player_y * self.tile_size) - self.camera_y

        try:
            # Get player sprite from shared graphics manager
            player_sprite = self.graphics_manager.get_player_sprite(self.player_direction)
            
            # Center 32x32 sprite on 64x64 tile
            sprite_x = player_screen_x + (self.tile_size - 32) // 2
            sprite_y = player_screen_y + (self.tile_size - 32) // 2
            
            # Draw player sprite
            surface.blit(player_sprite, (sprite_x, sprite_y))
            
        except (AttributeError, TypeError):
            # Fallback to red circle if sprite system not available
            center_x = player_screen_x + self.tile_size // 2
            center_y = player_screen_y + self.tile_size // 2
            pygame.draw.circle(surface, (255, 0, 0), (center_x, center_y), 16)

        # Draw debug info automatically
        if main_surface:
            self.draw_debug_info(surface, fonts, player_x, player_y)

    def draw_temp_message(self, surface, fonts, temp_message_text, temp_message_timer):
        """Draw temporary message """
        if pygame.time.get_ticks() - temp_message_timer > 2000:
            return False
        
                
        # Center the message text
        draw_centered_text(surface, temp_message_text, fonts.get('fantasy_medium', fonts['normal']),
                        LAYOUT_DIALOG_Y + 10 + LAYOUT_DIALOG_HEIGHT // 2, RED)
        
        return True

    def draw_interaction_prompt(self, surface, fonts, building_name):
        """Draw message """
        if not building_name:
            return

        # Center the prompt text
        action_text = f"Press ENTER to enter {building_name}"

        prompt_font = fonts.get('fantasy_medium', fonts['normal'])
        text_surface = prompt_font.render(action_text, True, YELLOW)
        text_width = text_surface.get_width()
      
        prompt_y = LAYOUT_DIALOG_Y
        prompt_x = (SCREEN_WIDTH - text_width) // 2
        padding = 15
        bg_rect = pygame.Rect(prompt_x - padding, prompt_y - padding + 30 + LAYOUT_DIALOG_HEIGHT //2,
                            text_width + (padding * 2), text_surface.get_height() + (padding * 2))
        
        pygame.draw.rect(surface, (20, 20, 20), bg_rect)
        pygame.draw.rect(surface, YELLOW, bg_rect, 3)
        surface.blit(text_surface, (prompt_x, prompt_y + 30 + LAYOUT_DIALOG_HEIGHT // 2))


    def draw_debug_info(self, surface, fonts, player_x, player_y):
        """Draw debug information for development"""
        
        try:
            # Get graphics stats
            stats = self.graphics_manager.get_graphics_stats()
            pos_text = f"Position: ({player_x}, {player_y}) Facing: {self.player_direction}"
            graphics_text = f"Graphics: {stats['total_tiles']} tiles, {stats['player_sprites']} player sprites loaded"
        except (AttributeError, KeyError):
            # Fallback if graphics stats not available
            pos_text = f"Position: ({player_x}, {player_y}) Facing: {self.player_direction}"
            graphics_text = "Graphics system: Active with navigation renderer loaded"
        
        debug_font = fonts.get('fantasy_tiny', fonts['small'])
        
        # Draw in top-left corner of screen instead
        surface.blit(debug_font.render(pos_text, True, WHITE), (10, 10))
        surface.blit(debug_font.render(graphics_text, True, WHITE), (10, 30))
