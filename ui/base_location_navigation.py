# ui/base_location_navigation.py
"""
NavigationRenderer - Shared navigation logic utility
Handles camera, movement, rendering, and input for all tile-based locations
"""

import pygame
from utils.constants import (RED, YELLOW, WHITE, GREEN,
                             SCREEN_WIDTH, LAYOUT_IMAGE_HEIGHT, LAYOUT_DIALOG_HEIGHT,
                             LAYOUT_DIALOG_Y)
from utils.graphics import draw_border, draw_button, draw_centered_text
from utils.party_display import draw_party_status_panel, PARTY_PANEL_WIDTH
from utils.tile_graphics import get_tile_graphics_manager
from utils.world_npc_spawner import get_world_npc_spawner

def calculate_required_direction(entrance_x, entrance_y, building_pos):
    """
    Calculate which direction player must face to enter building from entrance tile
    
    Args:
        entrance_x, entrance_y: Player's current position (entrance tile)
        building_pos: Either (x, y) tuple or list of (x, y) tuples for multi-tile buildings
    
    Returns:
        String direction ('up', 'down', 'left', 'right') or None if can't determine
    """
    # Handle both single position and list of positions
    if isinstance(building_pos, tuple):
        building_positions = [building_pos]
    else:
        building_positions = building_pos
    
    # Find closest building tile to entrance
    min_distance = float('inf')
    closest_building_x, closest_building_y = building_positions[0]
    
    for bx, by in building_positions:
        distance = abs(bx - entrance_x) + abs(by - entrance_y)  # Manhattan distance
        if distance < min_distance:
            min_distance = distance
            closest_building_x, closest_building_y = bx, by
    
    # Calculate direction from entrance to building
    dx = closest_building_x - entrance_x
    dy = closest_building_y - entrance_y
    
    # Determine primary direction (prefer horizontal if equal)
    if abs(dx) >= abs(dy):
        return 'right' if dx > 0 else 'left'
    else:
        return 'down' if dy > 0 else 'up'

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

        # Enter key debouncing
        self.enter_pressed_last_frame = False
        self.transition_cooldown = 0
        self.transition_cooldown_duration = 300  # 300ms cooldown after transitions
        
        # Graphics manager
        self.graphics_manager = get_tile_graphics_manager()

        # world npc spawner
        self.npc_manager = get_world_npc_spawner()
        self.location_id = config.get('location_id', 'unknown')

    def check_valid_entrance(self, player_x, player_y, player_direction):
        """
        Check if player is at valid entrance and facing correct direction
        
        Returns:
            tuple: (building_info dict or None, required_direction string or None)
        """
        # Get building info at current position
        building_info = self.map_functions.get('get_building_info', lambda x, y: None)(player_x, player_y)
        
        if not building_info:
            return None, None
        
        # Check if building_info has entrance data with building position
        # This requires the map data to pass building_pos through get_building_at_entrance
        # For now, return building_info and we'll check direction in the calling code
        return building_info, None

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
        """Handle movement input with turn-then-move mechanics and timing"""
        current_time = pygame.time.get_ticks()
        keys_pressed_this_frame = set()
        new_x, new_y = player_x, player_y
        intended_direction = None
        movement_attempted = False
        
        # Determine intended direction from keys
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            keys_pressed_this_frame.add('up')
            intended_direction = 'up'
            movement_attempted = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            keys_pressed_this_frame.add('down')
            intended_direction = 'down'
            movement_attempted = True
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            keys_pressed_this_frame.add('left')
            intended_direction = 'left'
            movement_attempted = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            keys_pressed_this_frame.add('right')
            intended_direction = 'right'
            movement_attempted = True
        
        # Process movement/turning with timing
        moved_or_turned = False
        if movement_attempted and (current_time - self.last_move_time >= self.move_delay):
            new_key_pressed = bool(keys_pressed_this_frame - self.keys_pressed_last_frame)
            
            if new_key_pressed or (current_time - self.last_move_time >= self.move_delay * 2):
                # Check if player needs to turn first
                if self.player_direction != intended_direction:
                    # TURN: Change facing direction without moving
                    self.player_direction = intended_direction
                    self.last_move_time = current_time
                    moved_or_turned = True
                else:
                    # MOVE: Already facing this direction, calculate new position
                    if intended_direction == 'up':
                        new_y = player_y - 1
                    elif intended_direction == 'down':
                        new_y = player_y + 1
                    elif intended_direction == 'left':
                        new_x = player_x - 1
                    elif intended_direction == 'right':
                        new_x = player_x + 1
                    
                    # Validate and execute movement
                    if (new_x != player_x or new_y != player_y):
                        if self.map_functions['is_walkable'](new_x, new_y):
                            self.last_move_time = current_time
                            moved_or_turned = True
                        
        self.keys_pressed_last_frame = keys_pressed_this_frame
        
        if moved_or_turned:
            return new_x, new_y
        return player_x, player_y
    
    def check_enter_just_pressed(self, keys):
        """
        Check if ENTER was just pressed (not held from previous frame)
        
        Returns:
            bool: True if ENTER just pressed, False if held or not pressed
        """
        enter_currently_pressed = keys[pygame.K_RETURN]
        just_pressed = enter_currently_pressed and not self.enter_pressed_last_frame
        
        # Update state for next frame
        self.enter_pressed_last_frame = enter_currently_pressed
        
        return just_pressed

    def update_transition_cooldown(self, dt):
        """
        Update transition cooldown timer
        
        Args:
            dt: Delta time in milliseconds
        """
        if self.transition_cooldown > 0:
            self.transition_cooldown -= dt

    def start_transition_cooldown(self):
        """Start cooldown timer to prevent rapid re-triggering"""
        self.transition_cooldown = self.transition_cooldown_duration

    def can_interact(self):
        """Check if player can interact (not in cooldown)"""
        return self.transition_cooldown <= 0
    
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

    def draw_player(self, surface, player_x, player_y):
        """
        Draw player sprite on map
        
        Args:
            surface: Surface to draw on
            player_x, player_y: Player tile position
        """
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
            # Fallback to red circle if sprite fails
            pygame.draw.circle(
                surface,
                (255, 0, 0),
                (player_screen_x + self.tile_size // 2, player_screen_y + self.tile_size // 2),
                16
            )
    
    def check_npc_interaction(self, player_x, player_y, player_direction, location_id, game_state):
        """
        Check if player can interact with NPC at current position/facing
        
        Returns:
            tuple: (npc_data dict or None, required_direction or None, can_interact bool)
        """
        # Get NPC at player's position
        npc = self.npc_manager.get_npc_at_position(player_x, player_y, location_id, game_state)
        
        if not npc:
            return None, None, False
        
        # Calculate required direction to face NPC
        npc_x, npc_y = npc['current_position']
        
        # Use same direction calculation as buildings
        required_direction = calculate_required_direction(player_x, player_y, (npc_x, npc_y))
        
        # Check if facing correctly
        can_interact = (player_direction == required_direction)
        
        return npc, required_direction, can_interact
    
    def draw_npcs(self, surface, location_id, game_state):
            """
            Draw all active NPCs for current location
            
            Args:
                surface: Surface to draw on
                location_id: Current location identifier
                game_state: Game state for conditions/overrides
            """
            active_npcs = self.npc_manager.get_active_npcs(location_id, game_state)
            
            for npc in active_npcs:
                # Get NPC position (check for overrides)
                npc_x, npc_y = npc['current_position']
                
                # Calculate screen position
                screen_x = (npc_x * self.tile_size) - self.camera_x
                screen_y = (npc_y * self.tile_size) - self.camera_y
                
                # Only draw if in visible area
                if (-self.tile_size <= screen_x <= self.display_width and
                    -self.tile_size <= screen_y <= self.display_height):
                    
                    # Get NPC sprite (dot placeholder for now)
                    sprite = self.npc_manager.get_npc_sprite(npc['sprite_type'])
                    
                    # Center 32x32 sprite on 64x64 tile
                    sprite_x = screen_x + (self.tile_size - 32) // 2
                    sprite_y = screen_y + (self.tile_size - 32) // 2
                    
                    # Draw sprite
                    surface.blit(sprite, (sprite_x, sprite_y))

    def draw_temp_message(self, surface, fonts, temp_message_text, temp_message_timer):
        """Draw temporary message """
        if pygame.time.get_ticks() - temp_message_timer > 2000:
            return False
        
                
        # Center the message text
        draw_centered_text(surface, temp_message_text, fonts.get('fantasy_medium', fonts['normal']),
                        LAYOUT_DIALOG_Y + 10 + LAYOUT_DIALOG_HEIGHT // 2, RED)
        
        return True

    def draw_interaction_prompt(self, surface, fonts, prompt_text, can_interact=True):
        """Draw interaction prompt with smart formatting for NPCs vs buildings"""
        if not prompt_text or not can_interact:
            return

        # Smart formatting: detect if it's already a complete action phrase
        # Actions like "Talk to X", "Leave X", "Play X" don't need "to enter"
        action_verbs = ['Talk to', 'Leave', 'Play', 'Visit', 'Descend', 'Examine']
        needs_enter_prefix = not any(prompt_text.startswith(verb) for verb in action_verbs)
        
        if needs_enter_prefix:
            action_text = f"Press ENTER to enter {prompt_text}"
        else:
            action_text = f"Press ENTER: {prompt_text}"

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


    def check_searchable_object(self, player_x, player_y):
        """
        Check if player is standing at a searchable object tile
        
        Args:
            player_x, player_y: Player's current position
        
        Returns:
            dict or None: Searchable info if present, None otherwise
        """
        get_searchable = self.map_functions.get('get_searchable_info')
        if get_searchable:
            return get_searchable(player_x, player_y)
        return None

    def check_combat_trigger(self, player_x, player_y):
        """
        Check if player stepped on a combat trigger tile
        
        Args:
            player_x, player_y: Player's current position
        
        Returns:
            dict or None: Combat trigger info if present, None otherwise
        """
        get_combat = self.map_functions.get('get_combat_trigger')
        if get_combat:
            return get_combat(player_x, player_y)
        return None

    def draw_debug_info(self, surface, fonts, player_x, player_y, building_info=None, required_direction=None):
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
        
        # Draw in top-left corner of screen
        y_offset = 10
        surface.blit(debug_font.render(pos_text, True, WHITE), (10, y_offset))
        y_offset += 20
        surface.blit(debug_font.render(graphics_text, True, WHITE), (10, y_offset))
        y_offset += 20
        
        # Show entrance information if at a building
        if building_info and required_direction:
            building_name = building_info.get('name', 'Unknown')
            entrance_text = f"At entrance: {building_name} (need: {required_direction})"
            facing_correct = self.player_direction == required_direction
            color = GREEN if facing_correct else RED
            surface.blit(debug_font.render(entrance_text, True, color), (10, y_offset))

    def draw_debug_with_entrance_info(self, surface, fonts, player_x, player_y, building_info, required_direction):
        """Special debug draw that includes entrance information"""
        self.draw_debug_info(surface, fonts, player_x, player_y, building_info, required_direction)
