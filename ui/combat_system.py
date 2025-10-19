# ui/combat_system.py
"""
Enhanced Combat System UI - Tactical combat interface for your superior JSON architecture
Follows existing ui pattern for screen presentation layers
"""

import pygame
import time
from typing import Dict, Any, Optional, List
from utils.constants import *
from utils.graphics import draw_combat_button, draw_centered_text, draw_text
from utils.combat_loader import get_combat_loader
from game_logic.combat_engine import CombatPhase
from utils.combat_sprite_manager import get_combat_sprite_manager

class CombatEncounter:
    """
    Enhanced Combat UI System - Tactical grid interface
    Handles battlefield rendering, unit positioning, and player interaction
    Delegates all business logic to CombatEngine
    """
    
    def __init__(self, encounter_id: str):
        """Initialize combat encounter UI"""
        self.encounter_id = encounter_id
        self.screen_name = "combat"
        
        # Get sprite manager (singleton)
        self.sprite_manager = get_combat_sprite_manager()

        # UI state
        self.selected_action = None
        self.selected_unit = None
        self.highlighted_tiles = []
        self.inspected_unit = None 
    
        # Grid rendering settings
        self.grid_offset_x = 50
        self.grid_offset_y = 120
        self.tile_size = 48
        
        # Combat data loader
        self.combat_loader = get_combat_loader()
        
        #print(f"🎯 Enhanced CombatEncounter UI created for: {encounter_id}")

    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, controller=None) -> Dict[str, Any]:
        """Main combat screen rendering - follows BaseLocation pattern"""
         # Cache controller reference for helper methods
        self.controller = controller
        
        if controller and hasattr(controller, 'combat_engine') and hasattr(controller.combat_engine, 'movement_system'):
            #print("Updating movement animations...")
            controller.combat_engine.movement_system.update_movements()
        
        # Get combat sprite manager (singleton)
        self.sprite_manager = get_combat_sprite_manager()

        try:
            # Get combat data from engine
            combat_data = controller.combat_engine.get_combat_data_for_ui()

            # Cache the tileset for this battlefield
            battlefield = combat_data.get("battlefield", {})
            self.current_tileset = battlefield.get("tileset", "cellar")  # Default to cella

            # 🔥 ADD THIS SECTION HERE - Track mouse hover for spell AOE preview
            mouse_pos = pygame.mouse.get_pos()
            hover_grid_pos = self._screen_to_grid(mouse_pos[0], mouse_pos[1])
            
            # Store hover position in combat engine for spell preview
            if controller and hasattr(controller, 'combat_engine'):
                controller.combat_engine.hover_grid_pos = hover_grid_pos

        except Exception as e:
            print(f"❌ Combat data error: {e}")
            return self._render_data_error(surface, fonts, str(e))
        
        # UPDATE MOVEMENT ANIMATIONS - Add this block right here!
        if controller and hasattr(controller, 'combat_engine') and hasattr(controller.combat_engine, 'movement_system'):
            controller.combat_engine.movement_system.update_movements()
        
        # Clear screen
        surface.fill(BLACK)
        
        # Render combat interface
        clickable_areas = self._render_tactical_combat_interface(surface, combat_data, fonts, controller)
        
        # Register clickables with InputHandler AFTER rendering
        self._register_with_input_handler(clickable_areas, controller)
        
        return clickable_areas

    def handle_action(self, action_data: Dict[str, Any], game_state, event_manager) -> Optional[str]:
        action_type = action_data.get('action', '')
        
        if action_type == "GRID_CLICK":
            payload = action_data.get('payload', {})
            grid_pos = payload.get('grid_pos')
            return self._handle_grid_click(grid_pos, game_state, event_manager)
        
        elif action_type in ["MOVE", "ATTACK", "RANGED", "END_TURN"]:  
            # Handle direct button actions
            return self._handle_action_button(action_type.lower(), game_state, event_manager)

        return None

    def _get_floor_type(self, battlefield: Dict) -> str:
        """Get the floor tile type from battlefield data"""
        terrain = battlefield.get('terrain', {})
        default_floor = terrain.get('default', 'stone_floor')
        
        # Map terrain type to actual floor tile filename
        floor_tile_map = {
            'stone_floor': 'stone_floor_16x16',
            'cobblestone': 'cobblestone_street_16x16',
            'dirt': 'dirt_floor_16x16',
            'grass': 'grass_floor_16x16',
            'wood': 'wood_floor_16x16'
        }
        
        return floor_tile_map.get(default_floor, 'stone_floor_16x16')

    def _register_with_input_handler(self, clickable_areas: Dict, controller):
        """Register combat clickables with InputHandler using existing infrastructure"""
        
        try:
            if hasattr(controller, 'screen_manager') and hasattr(controller.screen_manager, 'input_handler'):
                input_handler = controller.screen_manager.input_handler
                
                # Register clickable areas
                input_handler.register_combat_clickables('combat', clickable_areas)
                
            else:
                print("⚠️ Cannot register combat clickables - InputHandler not available")
                
        except Exception as e:
            print(f"❌ Error registering combat clickables: {e}")
            import traceback
            traceback.print_exc()

    # ==========================================
    # MAIN RENDERING METHODS
    # ==========================================
    
    def _render_tactical_combat_interface(self, surface: pygame.Surface, combat_data: Dict, 
                                        fonts: Dict, controller) -> Dict[str, Any]:
        """Render the main tactical combat interface"""
        
        clickable_areas = {}
        
        # Get combat instance data
        encounter = combat_data.get("encounter", {})
        battlefield = combat_data.get("battlefield", {})
        enemy_instances = combat_data.get("enemy_instances", [])
        
        # Render title and current turn info
        self._render_combat_header(surface, encounter, combat_data, fonts)
        
        # Render tactical battlefield grid
        grid_areas = self._render_battlefield_grid(surface, battlefield, combat_data, fonts)
        clickable_areas.update(grid_areas)
        
        # Render unit sprites on grid
        self._render_battlefield_units(surface, combat_data, controller)
        
        # Render tile overlays (movement, targeting, etc.)
        self._render_tile_overlays(surface, combat_data)
        
        # Render right panel UI
        panel_areas = self._render_combat_ui_panel(surface, fonts, combat_data, controller)
        clickable_areas.update(panel_areas)
        
        return clickable_areas
    
    def _render_combat_header(self, surface: pygame.Surface, encounter: Dict, 
                                combat_data: Dict, fonts: Dict):
        """Render combat title and turn information"""
        
        title_font = fonts.get('fantasy_medium', fonts.get('medium', fonts['normal']))
        text_font = fonts.get('fantasy_small', fonts['normal'])
        
        # Combat title
        encounter_name = encounter.get('name', 'Combat Encounter')
        draw_centered_text(surface, encounter_name, title_font, 40, BRIGHT_GREEN)

        panel_x = 675 
        panel_y = 80

        phase = combat_data.get('combat_phase', 'setup')
        
        # Determine what to display based on phase
        if phase == 'victory':
            turn_text = "Victory"
        elif phase == 'defeat':
            turn_text = "Defeat"
        else:
            # Get active character name from character_states
            active_character_id = combat_data.get('active_character_id')
            character_states = combat_data.get('character_states', {})
            
            if active_character_id and active_character_id in character_states:
                char_state = character_states[active_character_id]
                char_name = char_state.get('name', 'Unknown')
                turn_text = f"Turn: {char_name}"
            else:
                # Fallback during enemy turns
                current_actor = combat_data.get('current_actor', 'Unknown')
                turn_text = f"Turn: {current_actor}"
        
        draw_text(surface, turn_text, text_font, panel_x, panel_y, YELLOW)
        
    def _render_battlefield_grid(self, surface: pygame.Surface, battlefield: Dict, 
                               combat_data: Dict, fonts: Dict) -> Dict[str, Any]:
        """Render the tactical battlefield grid"""
        
        clickable_areas = {}
        
        if not battlefield:
            return clickable_areas
        
        dimensions = battlefield.get('dimensions', {'width': 12, 'height': 8})
        width = dimensions['width']
        height = dimensions['height']
        
        # Get floor type from battlefield data (data-driven!)
        floor_type = self._get_floor_type(battlefield)
        
        # Draw grid squares
        for x in range(width):
            for y in range(height):
                screen_x = self.grid_offset_x + (x * self.tile_size)
                screen_y = self.grid_offset_y + (y * self.tile_size)
                
                # Grid square rect
                square_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                
                # === LAYERED RENDERING ===
                # Layer 1: Floor tile (bottom)
                is_wall = False
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'combat_engine'):
                    is_wall = self.controller.combat_engine.movement_system._is_wall_tile(x, y, battlefield)
                
                if is_wall:
                    # Determine which wall tile to use
                    wall_type = self._get_wall_tile_type(x, y, battlefield)
                    # Get tile from current battlefield's tileset
                    wall_tile = self.sprite_manager.get_wall_tile(self.current_tileset, wall_type)
                    if wall_tile:
                        surface.blit(wall_tile, (screen_x, screen_y))
                    else:
                        pygame.draw.rect(surface, DARK_GRAY, square_rect)
                else:
                    # Draw floor using battlefield's terrain type
                    self._draw_floor_tile(surface, screen_x, screen_y, floor_type)
                
                # Layer 2: Obstacles (middle) - drawn ON TOP of floor
                is_obstacle = False
                if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'combat_engine'):
                    is_obstacle = self.controller.combat_engine.movement_system._is_obstacle_tile(x, y, battlefield)
                
                if is_obstacle:
                    obstacle_type = self._get_obstacle_type(x, y, battlefield)
                    self._draw_obstacle_sprite(surface, screen_x, screen_y, obstacle_type)
                
                # Layer 3: Grid border (overlay)
                pygame.draw.rect(surface, (60, 60 , 60), square_rect, 1)  # Border
                
                # Register clickable area
                clickable_areas[f"grid_{x}_{y}"] = {
                    "rect": square_rect,
                    "action": "GRID_CLICK",
                    "grid_pos": [x, y]
                }
        
        return clickable_areas

    def _screen_to_grid(self, screen_x: int, screen_y: int) -> List[int]:
        """Convert screen coordinates to grid position"""
        grid_x = (screen_x - self.grid_offset_x) // self.tile_size
        grid_y = (screen_y - self.grid_offset_y) // self.tile_size
        
        # Return grid position (even if out of bounds - caller will validate)
        return [grid_x, grid_y]

    def _get_wall_tile_type(self, x: int, y: int, battlefield: Dict) -> str:
        """Determine which wall tile to use based on which wall lines it belongs to"""
        walls = battlefield.get('terrain', {}).get('walls', [])
        
        # Check which wall lines this position is part of
        on_horizontal_wall = False
        on_vertical_wall = False
        is_top = False
        is_bottom = False
        is_left = False
        is_right = False
        
        for wall in walls:
            x1, y1, x2, y2 = wall
            
            # Horizontal wall
            if y1 == y2 and y == y1 and min(x1, x2) <= x <= max(x1, x2):
                on_horizontal_wall = True
                if y == 0 or y < battlefield.get('dimensions', {}).get('height', 8) // 2:
                    is_top = True
                else:
                    is_bottom = True
            
            # Vertical wall
            if x1 == x2 and x == x1 and min(y1, y2) <= y <= max(y1, y2):
                on_vertical_wall = True
                if x == 0 or x < battlefield.get('dimensions', {}).get('width', 12) // 2:
                    is_left = True
                else:
                    is_right = True
        
        # Corners: where horizontal and vertical walls meet
        if on_horizontal_wall and on_vertical_wall:
            if is_top and is_left:
                return 'corner_nw'
            elif is_top and is_right:
                return 'corner_ne'
            elif is_bottom and is_left:
                return 'corner_sw'
            elif is_bottom and is_right:
                return 'corner_se'
        
        # Straight walls
        if on_horizontal_wall:
            return 'wall_north' if is_top else 'wall_south'
        elif on_vertical_wall:
            return 'wall_west' if is_left else 'wall_east'
        
        # Default fallback
        return 'wall_north'

    def _get_obstacle_type(self, x: int, y: int, battlefield: Dict) -> str:
        """Get the type of obstacle at this grid position"""
        obstacles = battlefield.get('terrain', {}).get('obstacles', [])
        
        for obstacle in obstacles:
            obs_pos = obstacle.get('position', [])
            if len(obs_pos) == 2 and obs_pos[0] == x and obs_pos[1] == y:
                return obstacle.get('type', 'barrel')  # Default to barrel
        
        return 'barrel'  # Fallback
    
    def _draw_obstacle_sprite(self, surface: pygame.Surface, screen_x: int, screen_y: int, obstacle_type: str):
        """Draw obstacle sprite (auto-centers 32x32, fills tile for 48x48)"""
        sprite = self.sprite_manager.get_obstacle_sprite(obstacle_type)
        
        if sprite:
            sprite_size = sprite.get_width()  # Get actual sprite size
            
            if sprite_size == 48:
                # Large obstacles fill the entire tile
                surface.blit(sprite, (screen_x, screen_y))
            else:
                # Small obstacles center in tile (32x32 in 48x48)
                sprite_x = screen_x + (self.tile_size - sprite_size) // 2
                sprite_y = screen_y + (self.tile_size - sprite_size) // 2
                surface.blit(sprite, (sprite_x, sprite_y))

    def _draw_floor_tile(self, surface: pygame.Surface, screen_x: int, screen_y: int, floor_type: str = 'cobblestone_street_16x16'):
            """Draw tiled floor texture for this grid square"""
            # Get the 16x16 floor tile from sprite manager
            floor_tile = self.sprite_manager.get_floor_tile(floor_type)
            
            if floor_tile:
                # Tile the 16x16 texture 3x3 times to fill 48x48 grid square
                tile_size = 16
                tiles_per_row = self.tile_size // tile_size  # 48 / 16 = 3
                
                for ty in range(tiles_per_row):
                    for tx in range(tiles_per_row):
                        tile_x = screen_x + (tx * tile_size)
                        tile_y = screen_y + (ty * tile_size)
                        surface.blit(floor_tile, (tile_x, tile_y))
            else:
                # Fallback: draw black square if tile not loaded
                pygame.draw.rect(surface, BLACK, 
                            (screen_x, screen_y, self.tile_size, self.tile_size))

    def _render_battlefield_units(self, surface: pygame.Surface, combat_data: Dict, controller):
        """Render player and enemy units on the battlefield"""
        # Add debug information
        #print(f"DEBUG: Rendering battlefield units")
        if controller and hasattr(controller, 'combat_engine') and hasattr(controller.combat_engine, 'movement_system'):
            active_movements = controller.combat_engine.movement_system.entity_movements
            #print(f"DEBUG: Active movements: {len(active_movements)}")
            #for entity_id, movement in active_movements.items():
                #print(f"DEBUG: Movement for {entity_id}: {movement['moving']}, {movement['start_pos']} → {movement['target_pos']}")
    
        # Update movement animations if movement system exists
        if controller and hasattr(controller, 'combat_engine') and hasattr(controller.combat_engine, 'movement_system'):
            controller.combat_engine.movement_system.update_movements()
        
        # Render all party members
        character_states = combat_data.get("character_states", {})
        active_character_id = combat_data.get("active_character_id")
        
        # First, separate living and dead characters
        living_characters = []
        dead_characters = []

        for char_id, char_state in character_states.items():
            if char_state.get('is_alive', True):
                living_characters.append((char_id, char_state))
            else:
                dead_characters.append((char_id, char_state))

        # Render unconsious characters first (so they appear below)
        for char_id, char_state in dead_characters:
            position = char_state.get('position')
            if not position or len(position) != 2:
                continue
            
            x, y = position
            screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
            screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2) - 6
            
            # Draw body as dark gray circle
            pygame.draw.circle(surface, DARK_GRAY, (screen_x, screen_y), self.tile_size // 3)
            
            # Character label
            name = char_state.get('name', 'P')
            label = name[0].upper()
            font = pygame.font.Font(None, 24)
            text_surface = font.render(f"{label}", True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            surface.blit(text_surface, text_rect)

        # Then render living characters
        for char_id, char_state in living_characters:
            # Your existing code for rendering living characters
            
            # Get base grid position
            position = char_state.get('position')
            if not position or len(position) != 2:
                continue
                
            x, y = position
            
            # Check if character is being animated
            if (controller and hasattr(controller, 'combat_engine') and 
                hasattr(controller.combat_engine, 'movement_system') and
                controller.combat_engine.movement_system.is_entity_moving(char_id)):
                
                # Get movement data
                movement = controller.combat_engine.movement_system.entity_movements[char_id]
                
                if movement['moving']:
                    # Calculate current visual position based on interpolation
                    start = movement['start_pos']
                    target = movement['target_pos']
                    elapsed = time.time() - movement['start_time']
                    progress = min(elapsed * movement['move_speed'], 1.0)
                    
                    # Linear interpolation
                    x = start[0] + (target[0] - start[0]) * progress
                    y = start[1] + (target[1] - start[1]) * progress
            
            # Convert to screen coordinates
            screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
            screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2) - 6  # Move up 6 pixels
            
            # Determine color - CYAN for active character, BLUE for others
            is_active = (char_id == active_character_id)
            char_color = CYAN if is_active else BLUE
            
            # Check for incorporeal movement effect
            opacity = 255  # Full opacity by default
            if (controller and hasattr(controller, 'combat_engine') and 
                hasattr(controller.combat_engine, 'movement_system') and
                char_id in controller.combat_engine.movement_system.entity_movements):
                
                movement = controller.combat_engine.movement_system.entity_movements[char_id]
                if movement.get('is_incorporeal', False) and movement['moving']:
                    # Make slightly transparent during movement
                    opacity = 178  # ~70% opacity
                    
                    # Draw phase effect (subtle glow)
                    glow_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*char_color, 50), 
                                    (self.tile_size//2, self.tile_size//2), 
                                    self.tile_size // 2)
                    surface.blit(glow_surf, 
                            (screen_x - self.tile_size//2, 
                                screen_y - self.tile_size//2))
            
            # Create character surface with transparency
            char_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            
            # Draw character circle with appropriate opacity
            pygame.draw.circle(char_surf, (*char_color, opacity), 
                            (self.tile_size//2, self.tile_size//2), 
                            self.tile_size // 3)
            
            # Draw highlight for active character
            if is_active:
                pygame.draw.circle(char_surf, (*CYAN, opacity), 
                                (self.tile_size//2, self.tile_size//2), 
                                self.tile_size // 3 + 2, 3)
            
            # Apply surface with opacity
            surface.blit(char_surf, (screen_x - self.tile_size//2, screen_y - self.tile_size//2))
            
            # Character label (first letter of name)
            name = char_state.get('name', 'P')
            label = name[0].upper()
            font = pygame.font.Font(None, 24)
            text_surface = font.render(label, True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            surface.blit(text_surface, text_rect)

            # 🔥 GET char_data FIRST (before using it!)
            char_data = char_state.get('character_data', {})

            # Get current HP from the correct source
            if char_id == 'player':
                current_hp = controller.game_state.character.get('current_hp', 10)
                max_hp = controller.game_state.character.get('hit_points', 10)
            else:
                # NPC - read from party_member_data
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('max_hp', 10)
                # Update from party_member_data if available
                for member in controller.game_state.party_member_data:
                    if member.get('id') == char_id:
                        current_hp = member.get('current_hp', current_hp)
                        max_hp = member.get('hp', member.get('hit_points', max_hp))
                        break

            # Draw HP bar (ONLY ONCE!)
            self._draw_hp_bar(surface, screen_x, screen_y, current_hp, max_hp)

            # Draw spell slot dots (only for spellcasters)
            spell_slots_remaining = char_state.get('spell_slots_remaining', 0)
            spell_slots_max = char_state.get('spell_slots_max', 0)
            if spell_slots_max > 0:
                self._draw_spell_slots(surface, screen_x, screen_y, spell_slots_remaining, spell_slots_max)
        
        # Render enemy units - DEAD FIRST, then LIVING (for proper Z-order)
        enemy_instances = combat_data.get("enemy_instances", [])
        
        # Separate dead and living enemies
        dead_enemies = [e for e in enemy_instances if e.get("current_hp", 0) <= 0]
        living_enemies = [e for e in enemy_instances if e.get("current_hp", 0) > 0]
        
        # LAYER 1: Render dead enemies as darkened corpses (bottom layer)
        for enemy in dead_enemies:
            position = enemy.get("position", [])
            if len(position) == 2:
                x, y = position
                screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
                screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2) - 6
                
                # Draw corpse as dark gray circle (instead of red)
                pygame.draw.circle(surface, DARK_GRAY, (screen_x, screen_y), self.tile_size // 3)
                
                # Draw an X over the corpse to show it's dead
                pygame.draw.line(surface, RED, 
                            (screen_x - 8, screen_y - 8), 
                            (screen_x + 8, screen_y + 8), 2)
                pygame.draw.line(surface, RED, 
                            (screen_x - 8, screen_y + 8), 
                            (screen_x + 8, screen_y - 8), 2)
                
                # Enemy label (first letter of name) - so you know WHAT died
                name = enemy.get("name", "E")
                label = name[0].upper()
                font = pygame.font.Font(None, 24)
                text_surface = font.render(f"†{label}", True, WHITE)
                text_rect = text_surface.get_rect(center=(screen_x, screen_y))
                surface.blit(text_surface, text_rect)
        
        # LAYER 2: Render living enemies (top layer - will appear over corpses)
        for enemy in living_enemies:
            # Get enemy ID
            enemy_id = enemy.get("instance_id", "")
            
            # Get base grid position
            position = enemy.get("position", [])
            if not position or len(position) != 2:
                continue
                
            x, y = position
            
            # Check if enemy is being animated
            if (controller and hasattr(controller, 'combat_engine') and 
                hasattr(controller.combat_engine, 'movement_system') and
                controller.combat_engine.movement_system.is_entity_moving(enemy_id)):
                
                # Get movement data
                movement = controller.combat_engine.movement_system.entity_movements[enemy_id]
                
                if movement['moving']:
                    # Calculate current visual position based on interpolation
                    start = movement['start_pos']
                    target = movement['target_pos']
                    elapsed = time.time() - movement['start_time']
                    progress = min(elapsed * movement['move_speed'], 1.0)
                    
                    # Linear interpolation
                    x = start[0] + (target[0] - start[0]) * progress
                    y = start[1] + (target[1] - start[1]) * progress
            
            # Convert to screen coordinates
            screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
            screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2) - 6
            
            # Check for incorporeal movement effect
            opacity = 255  # Full opacity by default
            if (controller and hasattr(controller, 'combat_engine') and 
                hasattr(controller.combat_engine, 'movement_system') and
                enemy_id in controller.combat_engine.movement_system.entity_movements):
                
                movement = controller.combat_engine.movement_system.entity_movements[enemy_id]
                if movement.get('is_incorporeal', False) and movement['moving']:
                    # Make slightly transparent during movement
                    opacity = 178  # ~70% opacity
                    
                    # Draw phase effect (subtle glow)
                    glow_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*RED, 50), 
                                    (self.tile_size//2, self.tile_size//2), 
                                    self.tile_size // 2)
                    surface.blit(glow_surf, 
                            (screen_x - self.tile_size//2, 
                                screen_y - self.tile_size//2))
            
            # Create enemy surface with transparency
            enemy_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            
            # Draw enemy circle with appropriate opacity
            pygame.draw.circle(enemy_surf, (*RED, opacity), 
                            (self.tile_size//2, self.tile_size//2), 
                            self.tile_size // 3)
            
            # Apply surface with opacity
            surface.blit(enemy_surf, (screen_x - self.tile_size//2, screen_y - self.tile_size//2))
            
            # Enemy label (first letter of name)
            name = enemy.get("name", "E")
            label = name[0].upper()
            font = pygame.font.Font(None, 24)
            text_surface = font.render(label, True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            surface.blit(text_surface, text_rect)
            
            # Draw enemy HP bar
            current_hp = enemy.get("current_hp", 0)
            max_hp = enemy.get("stats", {}).get("hp", 1)
            self._draw_hp_bar(surface, screen_x, screen_y, current_hp, max_hp)
    
    def _render_tile_overlays(self, surface: pygame.Surface, combat_data: Dict):
        """Render movement/targeting overlays on grid tiles"""
        """Render movement/targeting overlays on grid tiles (cover-aware in ranged mode)."""

        current_action = combat_data.get('current_action_mode')

        # 1) Cover-aware ranged branch (preferred)
        if current_action == "ranged_attack":
            color = (0, 200, 255); border_width = 3
            targets = combat_data.get("highlighted_targets")

            if targets:  # data path with cover info
                for t in targets:
                    x, y = t["position"]
                    rect = pygame.Rect(
                        self.grid_offset_x + x * self.tile_size,
                        self.grid_offset_y + y * self.tile_size,
                        self.tile_size, self.tile_size
                    )
                    cover = t.get("cover", "none")
                    if cover == "none":
                        pygame.draw.rect(surface, color, rect, border_width)          # solid
                    else:
                        self._draw_dotted_border(surface, rect, color, width=border_width)  # dotted
                # LOS line to hovered tile
                if getattr(self, "_hover_grid", None):
                    origin = combat_data["character_states"][combat_data["active_character_id"]]["position"]
                    preview = self.game_controller.combat_engine.get_ranged_preview(origin, self._hover_grid)
                    cells = preview.get("cells", [])
                    line_color = (0, 200, 255) if preview.get("has_los", False) else (255, 64, 64)
                    self._draw_dotted_los(surface, cells, line_color, width=2, gap=6)
                return

            # 1b) Fallback if engine didn’t provide highlighted_targets
            #     (keeps you from drawing nothing in ranged mode)
            highlighted_tiles = combat_data.get('highlighted_tiles', [])
            if highlighted_tiles:
                for x, y in highlighted_tiles:
                    rect = pygame.Rect(
                        self.grid_offset_x + x * self.tile_size,
                        self.grid_offset_y + y * self.tile_size,
                        self.tile_size, self.tile_size
                    )
                    pygame.draw.rect(surface, color, rect, border_width)              # solid cyan
                return
            # If no targets and no tiles, just fall through and return

        # 2) Movement, melee, and spell targeting paths 
        highlighted_tiles = combat_data.get('highlighted_tiles', [])
        if current_action == "attack":
            border_color = (255, 0, 0); border_width = 3
        elif current_action == "movement":
            border_color = (0, 255, 0); border_width = 3
        elif current_action == "spell_targeting":
            # Check if it's an AOE spell like Fireball
            controller = getattr(self, 'controller', None)
            if controller and hasattr(controller, 'combat_engine'):
                engine = controller.combat_engine
                
                # Get selected spell
                if hasattr(engine, 'selected_spell_id'):
                    spell_data = engine.spell_data.get(engine.selected_spell_id, {})
                    
                    # 🔥 AOE SPELL (Fireball) - Show red 3x3 preview
                    if spell_data.get('area_type') == 'area':
                        area_size = spell_data.get('area_size', 3)
                        hover_pos = getattr(engine, 'hover_grid_pos', None)
                        
                        # 🔥 KEY FIX: Check if hover_pos is valid (not None)
                        if hover_pos is not None:
                            
                            # Get battlefield dimensions
                            battlefield = combat_data.get("battlefield", {})
                            dimensions = battlefield.get("dimensions", {"width": 8, "height": 8})
                            grid_width = dimensions.get("width", 8)
                            grid_height = dimensions.get("height", 8)
                        
                            # Calculate area around hover position
                            half_size = area_size // 2
                            
                            for dx in range(-half_size, half_size + 1):
                                for dy in range(-half_size, half_size + 1):
                                    preview_x = hover_pos[0] + dx
                                    preview_y = hover_pos[1] + dy
                                    
                                    # 🔥 Only draw if within battlefield bounds
                                    if 0 <= preview_x < grid_width and 0 <= preview_y < grid_height:
                                        screen_x = self.grid_offset_x + (preview_x * self.tile_size)
                                        screen_y = self.grid_offset_y + (preview_y * self.tile_size)
                                        
                                        # Semi-transparent red fill
                                        red_surface = pygame.Surface((self.tile_size, self.tile_size))
                                        red_surface.set_alpha(100)  # 40% opacity
                                        red_surface.fill((255, 0, 0))  # Red
                                        surface.blit(red_surface, (screen_x, screen_y))
                                        
                                        # Red border
                                        pygame.draw.rect(surface, (255, 0, 0), 
                                                    (screen_x, screen_y, self.tile_size, self.tile_size), 3)
                        return  # Done with AOE preview
                    
                    # Single-target spell - show cyan highlights on valid targets
                    border_color = (0, 255, 255); border_width = 3
                else:
                    # No spell selected yet - default cyan
                    border_color = (0, 255, 255); border_width = 3
            else:
                border_color = (0, 255, 255); border_width = 3  # Cyan for spell targets
        else:
            return

        # Draw highlighted tiles (for non-AOE or fallback)
        for x, y in highlighted_tiles:
            rect = pygame.Rect(
                self.grid_offset_x + x * self.tile_size,
                self.grid_offset_y + y * self.tile_size,
                self.tile_size, self.tile_size
            )
            pygame.draw.rect(surface, border_color, rect, border_width)
        
    def _render_combat_ui_panel(self, surface: pygame.Surface, fonts: Dict, 
                              combat_data: Dict, controller) -> Dict[str, Any]:
        """Render right panel with actions, status, and combat log"""
        
        clickable_areas = {}
        panel_x = 800  # Right side of screen
        panel_y = 150
        
        button_font = fonts.get('fantasy_small', fonts['normal'])
        text_font = fonts.get('fantasy_micro', fonts['normal'])
        combat_log_font = fonts.get('combat_log', text_font)

        # Get active character info (needed for button states)
        active_character_id = combat_data.get('active_character_id')
        character_states = combat_data.get('character_states', {})
        
        # Start positioning for action buttons (moved up closer to Turn: line)
        current_y = panel_y - 30  # spacing below Turn: line
        
        # Action_buttons = ["MOVE", "ATTACK", "SPELL", "END_TURN"]
        action_buttons = [
            {"id": "move", "label": "Move"},
            {"id": "attack", "label": "Attack"},
            {"id": "ranged", "label": "Ranged"},
            {"id": "spell", "label": "Cast Spell"},
            {"id": "end_turn", "label": "End Turn"}
        ]
        
        button_width = 120
        button_height = 30
        
        # Get active character state for button disabling
        active_char_state = character_states.get(active_character_id, {})
        has_moved = active_char_state.get('has_moved', False)
        attacks_used = active_char_state.get('attacks_used', 0)
        
        # Get attacks per round from combat engine via player_state (temporary)
        player_state = combat_data.get('player_state', {})
        attacks_per_round = player_state.get('attacks_per_round', 1)
        has_attack_targets = player_state.get('has_attack_targets', False)

        for i, action_data in enumerate(action_buttons):
            try:
                action_id = action_data.get("id", "unknown")
                action_label = action_data.get("label", "Unknown")

                button_y = current_y + (i * (button_height + 10))
                button_rect = pygame.Rect(panel_x - (button_width // 2), button_y, button_width, button_height)
                
                # Get current action mode to show which button is active
                current_mode = combat_data.get('current_action_mode', None)
                
                # Determine button state based on player actions AND active mode
                if action_id == "move":
                    if has_moved:
                        button_state = "disabled"
                    elif current_mode == "movement":
                        button_state = "active"  # Yellow border - mode is active
                    else:
                        button_state = "normal"  # Gray border - available but not selected
                        
                elif action_id == "attack":
                    has_attack_targets = player_state.get('has_attack_targets', False)
                    if attacks_used >= attacks_per_round or not has_attack_targets:
                        button_state = "disabled"
                    elif current_mode == "attack":
                        button_state = "active"  # Yellow border - mode is active
                    else:
                        button_state = "normal"  # Gray border - available but not selected
                
                elif action_id == "ranged":  
                    has_ranged_weapon = player_state.get('has_ranged_weapon', False)
                    has_ranged_targets = player_state.get('has_ranged_targets', False)
                    
                    if not has_ranged_weapon or attacks_used >= attacks_per_round or not has_ranged_targets:
                        button_state = "disabled"
                    elif current_mode == "ranged_attack":
                        button_state = "active"  # Yellow border - mode is active
                    else:
                        button_state = "normal"  # Gray border - available but not selected
                
                elif action_id == "spell":
                    # Check spell slots AND if already cast this turn
                    spell_slots_remaining = active_char_state.get('spell_slots_remaining', 0)
                    spells_known = active_char_state.get('spells_known', [])
                    spells_cast = active_char_state.get('spells_cast_this_turn', 0)
                    
                    # Disable if: no slots, no spells, or already cast this turn
                    if spell_slots_remaining <= 0 or len(spells_known) == 0 or spells_cast >= 1:
                        button_state = "disabled"
                    elif current_mode == "spell":
                        button_state = "active"  # Yellow border - spell mode active
                    else:
                        button_state = "normal"  # Gray border - can cast spells
                elif action_id == "end_turn":
                    button_state = "normal"  # Always available (never "active" since it doesn't toggle)
                else:
                    button_state = "normal"
                
                draw_combat_button(surface, button_rect.x, button_rect.y, button_width, button_height,
                        action_label, button_font, button_state)

                # Register all action buttons as clickable
                clickable_areas[f"button_{action_id}"] = {
                    "rect": button_rect,
                    "action": action_id.upper(),
                    "button_type": action_id
                }
            except Exception as e:
                print(f"❌ Error rendering button {i}: {e}")
                continue
                
        # Save the y position after buttons for later use
        post_buttons_y = current_y + len(action_buttons) * (button_height + 10) + 10
        
        # If in spell mode, show available spells TO THE RIGHT of action buttons
        current_mode = combat_data.get('current_action_mode', None)
        spell_list_x = panel_x + 80  # Position to the right of the buttons
        spell_list_y = panel_y - 30  # Start at same height as buttons
        
        if current_mode == "spell" and active_character_id:
            char_state = character_states.get(active_character_id, {})
            
            # Get available spells from combat engine
            if controller and hasattr(controller, 'combat_engine'):
                available_spells = controller.combat_engine.get_available_spells(active_character_id)
                if available_spells:
                    # Draw "SELECT SPELL:" header
                    spell_header_font = fonts.get('fantasy_micro', button_font)
                    spell_header = spell_header_font.render("SELECT SPELL:", True, YELLOW)
                    surface.blit(spell_header, (spell_list_x, spell_list_y))
                    spell_list_y += 25
                    
                    # Draw spell buttons with smaller font
                    spell_button_font = fonts.get('fantasy_micro', text_font)
                    for spell_data in available_spells:
                        spell_id = spell_data.get('id')
                        spell_name = spell_data.get('name')
                        
                        # Truncate long spell names
                        if len(spell_name) > 14:
                            spell_display = spell_name[:12] + ".."
                        else:
                            spell_display = spell_name
                        
                        spell_button_rect = pygame.Rect(spell_list_x, spell_list_y, 120, 22)
                        
                        # Draw spell button
                        draw_combat_button(surface, spell_button_rect.x, spell_button_rect.y, 
                                        120, 22, spell_display, spell_button_font, "normal")
                        
                        # Register as clickable
                        clickable_areas[f"spell_{spell_id}"] = {
                            "rect": spell_button_rect,
                            "action": "SELECT_SPELL",
                            "spell_id": spell_id
                        }
                        
                        spell_list_y += 25
                
        # Use the saved position for elements below buttons
        current_y = post_buttons_y


        # Unit Inspector Panel - FIXED SPACE (always reserve space even if empty)
        inspector_start_y = current_y
        
        # Read from CombatEngine (accessed via GameController)
        inspected_unit = None
        if controller and hasattr(controller, 'combat_engine'):
            inspected_unit = getattr(controller.combat_engine, 'inspected_unit', None)
        
        if inspected_unit:
            # Inspector is active - show unit info
            draw_text(surface, "INSPECTING:", text_font, 680, current_y, YELLOW)
            current_y += 20
            
            unit_name = inspected_unit.get('name', 'Unknown')
            unit_type = inspected_unit.get('type', 'ally')  # 'enemy' or 'ally'
            type_label = "Enemy" if unit_type == 'enemy' else "Ally"
            
            draw_text(surface, f"{unit_name} ({type_label})", combat_log_font, 680, current_y, WHITE)
            current_y += 15
            
            # Calculate status from HP percentage
            current_hp = inspected_unit.get('current_hp', 0)
            max_hp = inspected_unit.get('max_hp', 1)
            hp_percent = (current_hp / max_hp * 100) if max_hp > 0 else 0
            
            if hp_percent == 0:
                status = "Defeated"
                status_color = DARK_GRAY
            elif hp_percent >= 90:
                status = "Healthy"
                status_color = GREEN
            elif hp_percent >= 66:
                status = "Hit"
                status_color = YELLOW
            elif hp_percent >= 21:
                status = "Bloodied"
                status_color = ORANGE
            else:  # 1-20%
                status = "Near Death"
                status_color = RED
            
            draw_text(surface, f"Status: {status}", combat_log_font, 680, current_y, status_color)
            current_y += 20
        else:
            # Inspector empty - still reserve the space (3 lines worth)
            current_y += 55  # Reserve fixed height 

       # Combat Log Header
        draw_text(surface, "COMBAT LOG:", text_font, 680, current_y, YELLOW)
        current_y += 25
        
        # Get combat log from combat_data
        log_messages = combat_data.get('combat_log', ["Combat begins!"])
        
        # Display last 18 messages with text wrapping (expanded for more history)
        recent_messages = log_messages[-16:]
        log_y = current_y
        log_max_width = 320  # Width of combat log panel area
        
        for message in recent_messages:
            # Wrap long messages to fit in panel using optimized wrap_text
            wrapped_lines = wrap_text(message, combat_log_font, log_max_width, WHITE)
            
            for line_surface in wrapped_lines:
                surface.blit(line_surface, (680, log_y))
                log_y += 18  # Line spacing
        
        # Exit button
        exit_y = 710
        exit_rect = pygame.Rect(self.grid_offset_x, exit_y, 80, 40)
        
        draw_combat_button(surface, exit_rect.x, exit_rect.y, 80, 40, "EXIT", button_font)
        clickable_areas["back_button"] = {
            "rect": exit_rect,
            "action": "COMBAT_BACK"
        }
        
        return clickable_areas
    
    # ==========================================
    # BATTLEFIELD HELPER METHODS
    # ==========================================
    
    def _draw_dotted_border(self, surface, rect, color, width=3, gap=4):
        # draw dotted lines on four edges
        def dotted_line(p1, p2):
            dx = p2[0] - p1[0]; dy = p2[1] - p1[1]
            length = max(abs(dx), abs(dy))
            if length <= 0: return
            steps = max(1, int(length // (gap)))
            for i in range(0, steps, 2):  # draw, skip, draw...
                t0 = i / steps
                t1 = min((i + 1) / steps, 1.0)
                q0 = (p1[0] + dx * t0, p1[1] + dy * t0)
                q1 = (p1[0] + dx * t1, p1[1] + dy * t1)
                pygame.draw.line(surface, color, q0, q1, width)

        r = rect
        dotted_line((r.left,  r.top),    (r.right, r.top))
        dotted_line((r.right, r.top),    (r.right, r.bottom))
        dotted_line((r.right, r.bottom), (r.left,  r.bottom))
        dotted_line((r.left,  r.bottom), (r.left,  r.top))

    def _draw_hp_bar(self, surface: pygame.Surface, center_x: int, center_y: int, 
                 current_hp: int, max_hp: int):
        """Draw HP bar below unit sprite with black background for visibility"""
        bar_width = 32
        bar_height = 4
        
        # Position below sprite but closer (only 2 pixels gap)
        bar_x = center_x - (bar_width // 2)
        bar_y = center_y + (self.tile_size // 3) + 2  # Closer to sprite
        
        # Black background for contrast
        pygame.draw.rect(surface, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        
        # Background (dark red = missing HP)
        pygame.draw.rect(surface, (139, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Foreground (green = current HP)
        if max_hp > 0:
            hp_percent = current_hp / max_hp
            green_width = int(bar_width * hp_percent)
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, green_width, bar_height))
        
        # White border
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
    
    def _draw_spell_slots(self, surface: pygame.Surface, center_x: int, center_y: int,
                     slots_remaining: int, slots_max: int):
        """Draw spell slot dots below HP bar"""
        if slots_max <= 0:
            return  # No spell slots to show
        
        dot_size = 4
        dot_spacing = 6
        total_width = (slots_max * dot_size) + ((slots_max - 1) * 2)  # dots + gaps
        
        # Position below HP bar (HP bar ends at center_y + 18, add 6px gap)
        dots_x = center_x - (total_width // 2)
        dots_y = center_y + 24
        
        # Draw each dot
        for i in range(slots_max):
            dot_x = dots_x + (i * dot_spacing)
            
            # CYAN if slot available, GRAY if used
            dot_color = CYAN if i < slots_remaining else GRAY
            
            # Draw dot as small filled circle
            pygame.draw.circle(surface, dot_color, (dot_x, dots_y), dot_size // 2)
    
    
    # ==========================================
    # ERROR HANDLING
    # ==========================================
    
    def _render_engine_error(self, surface: pygame.Surface, fonts: Dict) -> Dict[str, Any]:
        """Render error when CombatEngine not available"""
        surface.fill(BLACK)
        
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        text_font = fonts.get('fantasy_medium', fonts['normal'])
        
        draw_centered_text(surface, "COMBAT ENGINE ERROR", title_font, 250, RED)
        draw_centered_text(surface, "CombatEngine not initialized", text_font, 300, WHITE)
        draw_centered_text(surface, "Check GameController setup", text_font, 330, GRAY)
        
        # Back button
        back_rect = pygame.Rect(412, 400, 200, 50)
        draw_combat_button(surface, 412, 400, 200, 50, "BACK TO TAVERN", text_font)
        
        return {"back_button": {"rect": back_rect, "action": "COMBAT_BACK"}}
    
    def _render_data_error(self, surface: pygame.Surface, fonts: Dict, error_msg: str) -> Dict[str, Any]:
        """Render error when combat data unavailable"""
        surface.fill(BLACK)
        
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        text_font = fonts.get('fantasy_medium', fonts['normal'])
        
        draw_centered_text(surface, "COMBAT DATA ERROR", title_font, 250, RED)
        draw_centered_text(surface, error_msg[:40], text_font, 300, WHITE)
        
        # Back button
        back_rect = pygame.Rect(412, 400, 200, 50)
        draw_combat_button(surface, 412, 400, 200, 50, "BACK TO TAVERN", text_font)
        
        return {"back_button": {"rect": back_rect, "action": "COMBAT_BACK"}}

# ==========================================
# SCREENMANAGER INTEGRATION
# ==========================================

def draw_combat_screen(surface: pygame.Surface, game_state, fonts: Dict, images: Dict, controller=None):
    """
    ScreenManager integration function for enhanced tactical combat
    
    Creates CombatEncounter and delegates rendering
    Follows established screen function pattern
    """
    
    # Create combat encounter UI (get encounter ID from game state or context)
    encounter_id = getattr(game_state, 'current_combat_encounter', 'tavern_basement_rats')
    combat_encounter = CombatEncounter(encounter_id)
    
    # Initialize the encounter in CombatEngine if not already started
    if controller and controller.combat_engine:
        if not controller.combat_engine.combat_data:
            combat_context = getattr(game_state, 'combat_context', None)
            controller.combat_engine.start_encounter(encounter_id, combat_context)
    
    # Delegate to combat encounter render method
    clickable_areas = combat_encounter.render(surface, game_state, fonts, images, controller)
    #print(f"🎯 Combat clickable areas: {list(clickable_areas.keys())}")
    return clickable_areas
# ==========================================
# EVENT HANDLERS
# ==========================================

def register_combat_system_events(event_manager, game_controller):
    """Register combat event handlers that actually work"""
    
    def clear_inspector():
        """Clear the unit inspector when starting an action"""
        if game_controller:
            game_controller.inspected_unit = None

    def handle_attack_action(event_data):
        """Handle ATTACK button click - toggle on/off"""
        if game_controller:
            current_mode = getattr(game_controller, 'current_action_mode', None)
            
            if current_mode == "attack":
                # Already in attack mode - toggle OFF
                print("ATTACK button toggled OFF")
                game_controller.set_action_mode(None)
            else:
                # Not in attack mode - toggle ON
                print("ATTACK button clicked - switching to attack mode")
                game_controller.set_action_mode("attack")
                clear_inspector()  # Clear inspector when starting action

    def handle_ranged_action(event_data):
        """Handle RANGED button click - toggle on/off"""
        if game_controller:
            current_mode = getattr(game_controller, 'current_action_mode', None)
            
            if current_mode == "ranged_attack":
                # Already in ranged mode - toggle OFF
                print("RANGED button toggled OFF")
                game_controller.set_action_mode(None)
            else:
                # Not in ranged mode - toggle ON
                print("RANGED button clicked - switching to ranged attack mode")
                game_controller.set_action_mode("ranged_attack")
                clear_inspector()  # Clear inspector when starting action

    def handle_move_action(event_data):
        """Handle MOVE button click - toggle on/off"""
        if game_controller:
            current_mode = getattr(game_controller, 'current_action_mode', None)
            
            if current_mode == "movement":
                # Already in movement mode - toggle OFF
                print("MOVE button toggled OFF")
                game_controller.set_action_mode(None)
            else:
                # Not in movement mode - toggle ON
                print("MOVE button clicked - switching to movement mode")
                game_controller.set_action_mode("movement")
                clear_inspector()  # Clear inspector when starting action 

    def handle_grid_click(event_data):
        grid_pos = event_data.get('grid_pos', [0, 0])
        print(f"Grid clicked at: {grid_pos}")
        
        if game_controller:
            current_mode = getattr(game_controller, 'current_action_mode', None)
            
            # If in an action mode (movement/attack), execute that action
            if current_mode == "movement":
                result = game_controller.execute_player_move(grid_pos)
                print(f"Movement result: {result}")
            elif current_mode == "attack":
                result = game_controller.execute_player_attack(grid_pos)
                print(f"Attack result: {result}")
            elif current_mode == "ranged_attack":                     
                result = game_controller.execute_player_ranged_attack(grid_pos)
                print(f"Ranged attack result: {result}")
            elif current_mode == "spell_targeting":
                result = game_controller.execute_spell_cast(grid_pos)
                print(f"Spell cast result: {result}")
            else:
                # No action mode active - check if clicking on a unit for inspection
                unit_data = game_controller.get_unit_at_position(grid_pos)
                
                if unit_data:
                    # Store in CombatEngine directly
                    game_controller.inspected_unit = unit_data
                    print(f"👁️ Inspecting: {unit_data.get('name', 'Unknown')}")
                else:
                    # Clear inspector if clicking empty space
                    game_controller.inspected_unit = None   

    def handle_end_turn_action(event_data):
        """Handle END_TURN button click"""
        print("END_TURN button clicked")
        if game_controller:
            # Call the proper combat engine method
            game_controller.end_player_turn()
            print("Player turn ended via combat engine")
    
    def handle_spell_action(event_data):
        """Handle SPELL button click - toggle on/off"""
        if game_controller:
            current_mode = getattr(game_controller, 'current_action_mode', None)
            
            if current_mode == "spell":
                # Already in spell mode - toggle OFF
                print("SPELL button toggled OFF")
                game_controller.set_action_mode(None)
            else:
                # Not in spell mode - toggle ON
                print("SPELL button clicked - switching to spell casting mode")
                game_controller.set_action_mode("spell")
                clear_inspector()  # Clear inspector when starting action
        
    def handle_combat_back(event_data):
        """Handle return to previous screen"""
        print("🔙 COMBAT_BACK EVENT HANDLER CALLED!")
        
        if game_controller:
            # CRITICAL: Clean up combat state so next combat starts fresh
            # NOTE: game_controller here is actually the CombatEngine!
            game_controller.cleanup_combat()  # ← REMOVED .combat_engine
            
            # Clear game state combat flags
            if hasattr(game_controller.game_state, 'current_combat_encounter'):
                game_controller.game_state.current_combat_encounter = None
            if hasattr(game_controller.game_state, 'combat_context'):
                game_controller.game_state.combat_context = None
            
            # Return to previous screen
            if hasattr(game_controller.game_state, 'previous_screen') and game_controller.game_state.previous_screen:
                game_controller.game_state.screen = game_controller.game_state.previous_screen
            else:
                game_controller.game_state.screen = "redstone_town"
            
            print(f"Returning to: {game_controller.game_state.screen}")

    def handle_spell_select(event_data):
        """Handle clicking on a specific spell"""
        print(f"🔍 handle_spell_select called with: {event_data}")  # ADD THIS
        if game_controller:
            spell_id = event_data.get('spell_id')
            print(f"🔍 spell_id extracted: {spell_id}")  # ADD THIS
            if spell_id:
                print(f"✨ Spell selected: {spell_id}")
                # Store selected spell in game controller
                game_controller.selected_spell_id = spell_id
                # Change mode to targeting
                game_controller.set_action_mode("spell_targeting")
                clear_inspector()
    
    # Register the actual event names being emitted
    event_manager.register("MOVE", handle_move_action)
    event_manager.register("ATTACK", handle_attack_action)
    event_manager.register("RANGED", handle_ranged_action)
    event_manager.register("SPELL", handle_spell_action)
    event_manager.register("SELECT_SPELL", handle_spell_select) 
    event_manager.register("END_TURN", handle_end_turn_action)
    event_manager.register("GRID_CLICK", handle_grid_click)
    event_manager.register("COMBAT_BACK", handle_combat_back)
    
    print("🎯 Combat System events registered: MOVE, ATTACK, END_TURN, GRID_CLICK, COMBAT_BACK")

# ==========================================
# INTEGRATION SETUP
# ==========================================

def setup_combat_system_integration(screen_manager, event_manager, game_controller):
    """
    Complete enhanced CombatSystem integration setup
    """
    
    # Register combat screen with ScreenManager
    if hasattr(screen_manager, 'register_screen_function'):
        screen_manager.register_screen_function('combat', draw_combat_screen)
    
    # Register combat events
    register_combat_system_events(event_manager, game_controller)
    
    print("🎯 Enhanced Combat System integration complete")