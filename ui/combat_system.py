# ui/combat_system.py
"""
Enhanced Combat System UI - Tactical combat interface for your superior JSON architecture
Follows existing ui pattern for screen presentation layers
"""

import pygame
from typing import Dict, Any, Optional, List
from utils.constants import *
from utils.graphics import draw_button, draw_centered_text
from utils.combat_loader import get_combat_loader

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
        
        print(f"🎯 Enhanced CombatEncounter UI created for: {encounter_id}")
    
    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, 
              controller=None) -> Dict[str, Any]:
        """
        Main combat screen rendering - follows BaseLocation pattern
        
        Args:
            surface: Pygame surface to render on
            game_state: GameState instance
            fonts: Font dictionary
            images: Image dictionary  
            controller: GameController with combat_engine
            
        Returns:
            Dict of clickable areas for InputHandler registration
        """
        
        # Get CombatEngine (business logic)
        combat_engine = getattr(controller, 'combat_engine', None) if controller else None
        
        if not combat_engine:
            return self._render_engine_error(surface, fonts)
        
        # Get combat data from engine
        try:
            combat_data = combat_engine.get_combat_data_for_ui()
        except Exception as e:
            return self._render_data_error(surface, fonts, str(e))
        
        # Clear screen
        surface.fill(BLACK)
        
        # Render combat interface
        return self._render_tactical_combat_interface(surface, combat_data, fonts, controller)
    
    def handle_action(self, action_data: Dict[str, Any], game_state, event_manager) -> Optional[str]:
        """
        Handle combat actions - follows BaseLocation pattern
        
        Args:
            action_data: Action information from InputHandler
            game_state: GameState instance
            event_manager: EventManager for emitting events
            
        Returns:
            Optional navigation target
        """
        
        action_type = action_data.get('action', '')
        
        if action_type == "GRID_CLICK":
            # Handle battlefield grid clicks
            grid_pos = action_data.get('grid_position')
            return self._handle_grid_click(grid_pos, game_state, event_manager)
            
        elif action_type == "ACTION_BUTTON":
            # Handle action button clicks (Move, Attack, Spell, etc.)
            button_type = action_data.get('button_type')
            return self._handle_action_button(button_type, game_state, event_manager)
            
        elif action_type == "END_TURN":
            # End current actor's turn
            event_manager.emit("COMBAT_END_TURN", {})
            return None
            
        elif action_type == "COMBAT_BACK":
            # Return to previous screen
            return "broken_blade_main"
        
        return None
    
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
        self._render_battlefield_units(surface, combat_data)
        
        # Render tile overlays (movement, targeting, etc.)
        self._render_tile_overlays(surface, combat_data)
        
        # Render right panel UI
        panel_areas = self._render_combat_ui_panel(surface, fonts, combat_data)
        clickable_areas.update(panel_areas)
        
        return clickable_areas
    
    def _render_combat_header(self, surface: pygame.Surface, encounter: Dict, 
                            combat_data: Dict, fonts: Dict):
        """Render combat title and turn information"""
        
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        text_font = fonts.get('fantasy_medium', fonts['normal'])
        
        # Combat title
        encounter_name = encounter.get('name', 'Combat Encounter')
        draw_centered_text(surface, encounter_name, title_font, 40, BRIGHT_GREEN)
        
        # Current turn indicator
        current_actor = combat_data.get('current_actor', 'Setup Phase')
        turn_text = f"Current: {current_actor}"
        draw_centered_text(surface, turn_text, text_font, 80, YELLOW)
        
        # Combat phase
        phase = combat_data.get('combat_phase', 'setup')
        phase_text = f"Phase: {phase.title()}"
        draw_centered_text(surface, phase_text, text_font, 100, CYAN)
    
    def _render_battlefield_grid(self, surface: pygame.Surface, battlefield: Dict, 
                               combat_data: Dict, fonts: Dict) -> Dict[str, Any]:
        """Render the tactical battlefield grid"""
        
        clickable_areas = {}
        
        if not battlefield:
            return clickable_areas
        
        dimensions = battlefield.get('dimensions', {'width': 12, 'height': 8})
        width = dimensions['width']
        height = dimensions['height']
        
        # Draw grid squares
        for x in range(width):
            for y in range(height):
                screen_x = self.grid_offset_x + (x * self.tile_size)
                screen_y = self.grid_offset_y + (y * self.tile_size)
                
                # Grid square rect
                square_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                
                # Determine square color
                if self._is_wall_tile(x, y, battlefield):
                    color = DARK_GRAY  # Wall
                elif self._is_obstacle_tile(x, y, battlefield):
                    color = BROWN      # Obstacle
                else:
                    color = DARK_BLUE  # Floor
                
                # Draw square
                pygame.draw.rect(surface, color, square_rect)
                pygame.draw.rect(surface, WHITE, square_rect, 1)  # Border
                
                # Register clickable area
                clickable_areas[f"grid_{x}_{y}"] = {
                    "rect": square_rect,
                    "action": "GRID_CLICK",
                    "grid_position": [x, y]
                }
        
        return clickable_areas
    
    def _render_battlefield_units(self, surface: pygame.Surface, combat_data: Dict):
        """Render player and enemy units on the battlefield"""
        
        # Render enemy units
        enemy_instances = combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            self._render_unit_sprite(surface, enemy, enemy_color=RED)
        
        # Render player units (for now, just player character)
        player_positions = combat_data.get("player_positions", [])
        if player_positions:
            # For now, assume player is at first position
            player_pos = player_positions[0]
            player_unit = {
                "position": player_pos,
                "name": "Player",  # TODO: Get from game_state
                "current_hp": 20,  # TODO: Get from game_state
                "instance_id": "player"
            }
            self._render_unit_sprite(surface, player_unit, enemy_color=BLUE)
    
    def _render_unit_sprite(self, surface: pygame.Surface, unit: Dict, enemy_color: tuple):
        """Render a single unit sprite on the grid"""
        
        position = unit.get("position", [0, 0])
        x, y = position
        
        # Calculate screen position
        screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 4)
        screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 4)
        
        # Draw unit circle
        radius = self.tile_size // 3
        pygame.draw.circle(surface, enemy_color, (screen_x + radius, screen_y + radius), radius)
        pygame.draw.circle(surface, WHITE, (screen_x + radius, screen_y + radius), radius, 2)
        
        # Draw unit label
        name = unit.get("name", "Unit")
        if len(name) > 0:
            label = name[0].upper()  # First letter
            font = pygame.font.Font(None, 24)
            text_surface = font.render(label, True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_x + radius, screen_y + radius))
            surface.blit(text_surface, text_rect)
    
    def _render_tile_overlays(self, surface: pygame.Surface, combat_data: Dict):
        """Render movement/targeting overlays on grid tiles"""
        
        # TODO: Render highlighted tiles based on selected action
        # Green for movement range, red for attack targets, orange for spell areas
        for tile_pos in self.highlighted_tiles:
            x, y = tile_pos
            screen_x = self.grid_offset_x + (x * self.tile_size)
            screen_y = self.grid_offset_y + (y * self.tile_size)
            
            # Draw semi-transparent overlay
            overlay_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
            overlay_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            overlay_surface.fill((0, 255, 0, 128))  # Green with alpha
            surface.blit(overlay_surface, overlay_rect)
    
    def _render_combat_ui_panel(self, surface: pygame.Surface, fonts: Dict, 
                              combat_data: Dict) -> Dict[str, Any]:
        """Render right panel with actions, status, and combat log"""
        
        clickable_areas = {}
        panel_x = 750  # Right side of screen
        panel_y = 150
        
        button_font = fonts.get('fantasy_medium', fonts['normal'])
        text_font = fonts.get('fantasy_small', fonts['normal'])
        
        # Current unit status
        current_y = panel_y
        draw_centered_text(surface, "Current Unit:", text_font, current_y, CYAN)
        current_y += 30
        
        # TODO: Show current unit stats (HP, actions remaining, etc.)
        draw_centered_text(surface, "HP: 20/20", text_font, current_y, WHITE)
        current_y += 50
        
        # Action buttons
        action_buttons = ["MOVE", "ATTACK", "SPELL", "END TURN"]
        button_width = 120
        button_height = 40
        
        for i, action in enumerate(action_buttons):
            button_y = current_y + (i * (button_height + 10))
            button_rect = pygame.Rect(panel_x - (button_width // 2), button_y, button_width, button_height)
            
            # Determine button state (active, disabled, etc.)
            button_color = GREEN if action != "SPELL" else GRAY  # Disable spell for now
            text_color = WHITE if action != "SPELL" else DARK_GRAY
            
            draw_button(surface, button_rect.x, button_rect.y, button_width, button_height,
                       action, button_font, bg_color=BLACK, text_color=text_color, border_color=button_color)
            
            if action != "SPELL":  # Don't register disabled buttons
                clickable_areas[f"action_{action.lower()}"] = {
                    "rect": button_rect,
                    "action": "ACTION_BUTTON",
                    "button_type": action.lower()
                }
        
        current_y += len(action_buttons) * (button_height + 10) + 30
        
        # Combat log
        draw_centered_text(surface, "Combat Log:", text_font, current_y, CYAN)
        current_y += 25
        
        # TODO: Show combat log messages
        log_messages = ["Combat begins!", "Waiting for player action..."]
        for message in log_messages[-4:]:  # Show last 4 messages
            draw_centered_text(surface, message[:30], text_font, current_y, WHITE)
            current_y += 20
        
        # Back button
        back_y = 680
        back_rect = pygame.Rect(panel_x - 60, back_y, 120, 40)
        draw_button(surface, back_rect.x, back_rect.y, 120, 40, "BACK", button_font,
                   bg_color=BLACK, text_color=WHITE, border_color=WHITE)
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
    
    # ==========================================
    # ACTION HANDLERS
    # ==========================================
    
    def _handle_grid_click(self, grid_pos: List[int], game_state, event_manager) -> Optional[str]:
        """Handle clicks on battlefield grid"""
        if not grid_pos or len(grid_pos) != 2:
            return None
        
        x, y = grid_pos
        print(f"🎯 Grid clicked: [{x}, {y}]")
        
        # TODO: Handle based on selected action
        if self.selected_action == "move":
            # Validate movement and emit move event
            event_manager.emit("COMBAT_MOVE_UNIT", {"target_position": [x, y]})
        elif self.selected_action == "attack":
            # Validate attack target and emit attack event
            event_manager.emit("COMBAT_ATTACK_TARGET", {"target_position": [x, y]})
        
        return None
    
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
        
        return None
    
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
        draw_button(surface, 412, 400, 200, 50, "BACK TO TAVERN", text_font,
                   bg_color=BLACK, text_color=WHITE, border_color=WHITE)
        
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
        draw_button(surface, 412, 400, 200, 50, "BACK TO TAVERN", text_font,
                   bg_color=BLACK, text_color=WHITE, border_color=WHITE)
        
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
    
    # Delegate to combat encounter render method
    clickable_areas = combat_encounter.render(surface, game_state, fonts, images, controller)
    
    return clickable_areas

# ==========================================
# EVENT HANDLERS
# ==========================================

def register_combat_system_events(event_manager, game_controller):
    """Register enhanced CombatSystem event handlers"""
    
    def handle_move_unit(event_data):
        """Handle unit movement"""
        target_pos = event_data.get("target_position", [0, 0])
        print(f"🎯 Moving unit to: {target_pos}")
        # TODO: Delegate to CombatEngine for validation and execution
    
    def handle_attack_target(event_data):
        """Handle attack actions"""
        target_pos = event_data.get("target_position", [0, 0])
        print(f"🎯 Attacking target at: {target_pos}")
        # TODO: Delegate to CombatEngine for attack resolution
    
    def handle_end_turn(event_data):
        """Handle end turn"""
        print(f"🎯 Ending current turn")
        # TODO: Delegate to CombatEngine for turn advancement
    
    def handle_combat_back(event_data):
        """Handle return to tavern"""
        game_controller.game_state.screen = "broken_blade_main"
    
    # Register event handlers
    event_manager.register("COMBAT_MOVE_UNIT", handle_move_unit)
    event_manager.register("COMBAT_ATTACK_TARGET", handle_attack_target)
    event_manager.register("COMBAT_END_TURN", handle_end_turn)
    event_manager.register("COMBAT_BACK", handle_combat_back)
    
    print("🎯 Enhanced CombatSystem events registered")

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