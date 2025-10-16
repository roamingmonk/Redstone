# ui/combat_system.py
"""
Enhanced Combat System UI - Tactical combat interface for your superior JSON architecture
Follows existing ui pattern for screen presentation layers
"""

import pygame
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
    
        # Grid rendering settings
        self.grid_offset_x = 50
        self.grid_offset_y = 120
        self.tile_size = 48
        
        # Combat data loader
        self.combat_loader = get_combat_loader()
        
        #print(f"🎯 Enhanced CombatEncounter UI created for: {encounter_id}")

    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, controller=None) -> Dict[str, Any]:
        """Main combat screen rendering - follows BaseLocation pattern"""
        # Get combat sprite manager (singleton)
        self.sprite_manager = get_combat_sprite_manager()

        try:
            # Get combat data from engine
            combat_data = controller.combat_engine.get_combat_data_for_ui()

            # Cache the tileset for this battlefield
            battlefield = combat_data.get("battlefield", {})
            self.current_tileset = battlefield.get("tileset", "cellar")  # Default to cella

        except Exception as e:
            print(f"❌ Combat data error: {e}")
            return self._render_data_error(surface, fonts, str(e))
        
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
        #print(f"🔍 Total clickable areas to register: {len(clickable_areas)}")
        
        # # Show what we're trying to register
        # for area_id in clickable_areas.keys():
        #     if area_id.startswith("button_"):
        #         print(f"  🔘 Button area: {area_id}")
        
        
        """Register combat clickables with InputHandler using existing infrastructure"""
        
        
        
        try:
            if hasattr(controller, 'screen_manager') and hasattr(controller.screen_manager, 'input_handler'):
                input_handler = controller.screen_manager.input_handler
                
                # Use the existing register_combat_clickables method - it's already perfect!
                input_handler.register_combat_clickables('combat', clickable_areas)
                
            else:
                print("⚠️ Cannot register combat clickables - InputHandler not available")
                
        except Exception as e:
            print(f"❌ Error registering combat clickables: {e}")

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
                if self._is_wall_tile(x, y, battlefield):
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
                if self._is_obstacle_tile(x, y, battlefield):
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
        
        # Render all party members
        character_states = combat_data.get("character_states", {})
        active_character_id = combat_data.get("active_character_id")
        
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue  # Skip dead characters
            
            position = char_state.get('position')
            if position and len(position) == 2:
                x, y = position
                # Shift sprite up in the tile by reducing the offset
                screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
                screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2) - 6  # Move up 6 pixels
                
                # Determine color - CYAN for active character, BLUE for others
                is_active = (char_id == active_character_id)
                char_color = CYAN if is_active else BLUE
                
                # Draw character circle
                pygame.draw.circle(surface, char_color, (screen_x, screen_y), self.tile_size // 3)
                
                # Draw extra highlight border for active character
                if is_active:
                    pygame.draw.circle(surface, CYAN, (screen_x, screen_y), 
                                     self.tile_size // 3 + 2, 3)  # Thicker border
                
                # Character label (first letter of name)
                name = char_state.get('name', 'P')
                label = name[0].upper()
                font = pygame.font.Font(None, 24)
                text_surface = font.render(label, True, WHITE)
                text_rect = text_surface.get_rect(center=(screen_x, screen_y))
                surface.blit(text_surface, text_rect)
                
                # Draw HP bar - read from source of truth!
                char_data = char_state.get('character_data', {})
                
                # For player character, read directly from game_state (source of truth)
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
                
                self._draw_hp_bar(surface, screen_x, screen_y, current_hp, max_hp)
        
        # Render enemy units
        enemy_instances = combat_data.get("enemy_instances", [])
        #print(f"🎨 DEBUG: Rendering {len(enemy_instances)} enemies")
        for enemy in enemy_instances:
            position = enemy.get("position", [])
            
            current_hp = enemy.get("current_hp", 0)
            max_hp = enemy.get("stats", {}).get("hp", 1)
            enemy_name = enemy.get("name", "Enemy")
            
            #print(f"🎨 DEBUG: Enemy: {enemy_name} at {position}, HP: {current_hp}/{max_hp}")  
            
            
            if len(position) == 2:
                x, y = position
                # Shift sprite up in the tile
                screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
                screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2) - 6  # Move up 6 pixels
                
                #print(f"🎨 DEBUG: Rendering at screen coords: ({screen_x}, {screen_y})")

                # Draw enemy as red circle with first letter of name
                pygame.draw.circle(surface, RED, (screen_x, screen_y), self.tile_size // 3)
                
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

        # 2) Movement &  melee paths 
        highlighted_tiles = combat_data.get('highlighted_tiles', [])
        if current_action == "attack":
            border_color = (255, 0, 0); border_width = 3
        elif current_action == "movement":
            border_color = (0, 255, 0); border_width = 3
        else:
            return

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
        
        # Active character status
        current_y = panel_y
        
        # Get active character info
        active_character_id = combat_data.get('active_character_id')
        character_states = combat_data.get('character_states', {})
        
        if active_character_id and active_character_id in character_states:
            char_state = character_states[active_character_id]
            char_name = char_state.get('name', 'Unknown')
            
            # Display active character name
            draw_text(surface, f"Active: {char_name}", text_font, 750, current_y, CYAN)
            current_y += 30
            
            # Show active character HP - read from source of truth!
            char_data = char_state.get('character_data', {})
            
            # For player character, read directly from game_state (source of truth)
            # For NPCs, read from party_member_data
            if active_character_id == 'player':
                current_hp = controller.game_state.character.get('current_hp', 20)
                max_hp = controller.game_state.character.get('hit_points', 20)
            else:
                # NPC - find in party_member_data
                current_hp = char_data.get('current_hp', 20)
                max_hp = char_data.get('max_hp', 20)
                # Update from party_member_data if available
                for member in controller.game_state.party_member_data:
                    if member.get('id') == active_character_id:
                        current_hp = member.get('current_hp', current_hp)
                        max_hp = member.get('hp', member.get('hit_points', max_hp))
                        break
            
            hp_display = f"HP: {current_hp}/{max_hp}"
            draw_text(surface, hp_display, text_font, 750, current_y, WHITE)
            current_y += 30
            
            # Show class
            char_class = char_data.get('class', 'Fighter')
            draw_text(surface, f"Class: {char_class}", text_font, 750, current_y, WHITE)
            current_y += 30
        else:
            # Fallback if no active character
            draw_text(surface, "Current Unit:", text_font, 750, current_y, CYAN)
            current_y += 30
        
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
                
                # Determine button state based on player actions
                if action_id == "move":
                    button_state = "disabled" if has_moved else "active"
                elif action_id == "attack":
                    has_attack_targets = player_state.get('has_attack_targets', False)
                    if attacks_used >= attacks_per_round or not has_attack_targets:
                        button_state = "disabled"
                    else:
                        button_state = "active"
                
                elif action_id == "ranged":  
                    has_ranged_weapon = player_state.get('has_ranged_weapon', False)
                    has_ranged_targets = player_state.get('has_ranged_targets', False)
                    
                    if not has_ranged_weapon or attacks_used >= attacks_per_round or not has_ranged_targets:
                        button_state = "disabled"
                    else:
                        button_state = "active"
                
                elif action_id == "spell":
                    button_state = "disabled"  # Not implemented yet
                elif action_id == "end_turn":
                    button_state = "active"  # Always available
                else:
                    button_state = "active"
                
                draw_combat_button(surface, button_rect.x, button_rect.y, button_width, button_height,
                        action_label, button_font, button_state)

                if action_id not in ["spell"]:  # Register all buttons including ranged
                    clickable_areas[f"button_{action_id}"] = {
                        "rect": button_rect,
                        "action": action_id.upper(),
                        "button_type": action_id
                    }
            except Exception as e:
                print(f"❌ Error rendering button {i}: {e}")
                continue
                
        current_y += len(action_buttons) * (button_height + 10) + 30
        
        # Get combat log from combat_data
        log_messages = combat_data.get('combat_log', ["Combat begins!"])
        
        # Display last 10 messages with text wrapping
        recent_messages = log_messages[-12:]
        log_y = current_y
        log_max_width = 320  # Width of combat log panel area
        
        for message in recent_messages:
            # Wrap long messages to fit in panel using optimized wrap_text
            wrapped_lines = wrap_text(message, text_font, log_max_width, WHITE)
            
            for line_surface in wrapped_lines:
                surface.blit(line_surface, (680, log_y))
                log_y += 18  # Line spacing
        
        # Back button
        back_y = 680
        back_rect = pygame.Rect(panel_x - 60, back_y, 120, 40)
        
        draw_combat_button(surface, back_rect.x, back_rect.y, 120, 40, "BACK", button_font)
        clickable_areas["back_button"] = {
            "rect": back_rect,
            "action": "COMBAT_BACK"
        }
        
        return clickable_areas
    
    # ==========================================
    # BATTLEFIELD HELPER METHODS
    # ==========================================
    
    def _is_wall_tile(self, x: int, y: int, battlefield: Dict) -> bool:
        """Check if tile position is a wall"""
        terrain = battlefield.get('terrain', {})
        walls = terrain.get('walls', [])
        
        # Check if point is on any wall line segment
        for wall in walls:
            if len(wall) == 4:
                x1, y1, x2, y2 = wall
                if self._point_on_line_segment(x, y, x1, y1, x2, y2):
                    return True
        return False
    
    def _is_obstacle_tile(self, x: int, y: int, battlefield: Dict) -> bool:
        """Check if tile position has an obstacle"""
        terrain = battlefield.get('terrain', {})
        obstacles = terrain.get('obstacles', [])
        
        for obstacle in obstacles:
            obs_pos = obstacle.get('position', [])
            if len(obs_pos) == 2 and obs_pos[0] == x and obs_pos[1] == y:
                return True
        return False

    def _point_on_line_segment(self, px: int, py: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if point (px, py) is on line segment from (x1,y1) to (x2,y2)"""
        # For grid-based walls, check if point is exactly on the line
        if x1 == x2:  # Vertical line
            return px == x1 and min(y1, y2) <= py <= max(y1, y2)
        elif y1 == y2:  # Horizontal line
            return py == y1 and min(x1, x2) <= px <= max(x1, x2)
        return False
    
    def _handle_action_button(self, button_type: str, game_state, event_manager) -> Optional[str]:
        """Handle action button clicks"""
        print(f"🎯 Action button clicked: {button_type}")
        
        if button_type == "move":
            self.selected_action = "move"
            # TODO: Highlight valid movement squares
            
        elif button_type == "attack":
            self.selected_action = "attack"
            # TODO: Highlight valid attack targets
            
        elif button_type == "end_turn":
            event_manager.emit("COMBAT_END_TURN", {})
            self.selected_action = None
        
        elif button_type == "ranged":                
            self.selected_action = "ranged_attack"   
        
        return None

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
    
    def handle_attack_action(event_data):
        """Handle ATTACK button click"""  
        print("ATTACK button clicked - switching to attack mode")
        if game_controller: 
            game_controller.set_action_mode("attack")

    def handle_ranged_action(event_data):
        """Handle RANGED button click"""
        print("RANGED button clicked - switching to ranged attack mode")
        if game_controller:
            game_controller.set_action_mode("ranged_attack")

    def handle_move_action(event_data):
        """Handle MOVE button click"""
        print("MOVE button clicked - switching to movement mode")
        if game_controller:
            game_controller.set_action_mode("movement")

    def handle_grid_click(event_data):
        grid_pos = event_data.get('grid_pos', [0, 0])
        print(f"Grid clicked at: {grid_pos}")
        
        if game_controller:
            current_mode = getattr(game_controller, 'current_action_mode', None)
            
            if current_mode == "movement":
                result = game_controller.execute_player_move(grid_pos)
                print(f"Movement result: {result}")
            elif current_mode == "attack":
                result = game_controller.execute_player_attack(grid_pos)
                print(f"Attack result: {result}")
            elif current_mode == "ranged_attack":                     
                result = game_controller.execute_player_ranged_attack(grid_pos)
                print(f"Ranged attack result: {result}")              

    def handle_end_turn_action(event_data):
        """Handle END_TURN button click"""
        print("END_TURN button clicked")
        if game_controller:
            # Call the proper combat engine method
            game_controller.end_player_turn()
            print("Player turn ended via combat engine")
        
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
    
    # Register the actual event names being emitted
    event_manager.register("MOVE", handle_move_action)
    event_manager.register("ATTACK", handle_attack_action)
    event_manager.register("RANGED", handle_ranged_action)
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