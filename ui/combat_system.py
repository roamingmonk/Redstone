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
        
        #print(f"🎯 Enhanced CombatEncounter UI created for: {encounter_id}")
    
    # def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, 
    #           controller=None) -> Dict[str, Any]:
    #     """
    #     Main combat screen rendering - follows BaseLocation pattern
        
    #     Args:
    #         surface: Pygame surface to render on
    #         game_state: GameState instance
    #         fonts: Font dictionary
    #         images: Image dictionary  
    #         controller: GameController with combat_engine
            
    #     Returns:
    #         Dict of clickable areas for InputHandler registration
    #     """
        
    #     # Get CombatEngine (business logic)
    #     combat_engine = getattr(controller, 'combat_engine', None) if controller else None
        
    #     if not combat_engine:
    #         return self._render_engine_error(surface, fonts)
        
    #     # Get combat data from engine
    #     try:
    #         combat_data = combat_engine.get_combat_data_for_ui()
    #     except Exception as e:
    #         return self._render_data_error(surface, fonts, str(e))
        
    #     # Clear screen
    #     surface.fill(BLACK)
        
    #     # Render combat interface
    #     return self._render_tactical_combat_interface(surface, combat_data, fonts, controller)

    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, controller=None) -> Dict[str, Any]:
        """Main combat screen rendering - follows BaseLocation pattern"""
        
        try:
            # Get combat data from engine
            combat_data = controller.combat_engine.get_combat_data_for_ui()
            
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
        
        elif action_type in ["MOVE", "ATTACK", "END_TURN"]:
            # Handle direct button actions
            return self._handle_action_button(action_type.lower(), game_state, event_manager)

        return None
    
    # def _register_with_input_handler(self):
    #     """Register combat clickables with InputHandler"""
    #     if hasattr(self, 'screen_manager') and hasattr(self.screen_manager, 'input_handler'):
    #         input_handler = self.screen_manager.input_handler
    #         input_handler.clear_clickables('combat')
            
    #         # Get current clickable areas
    #         # You'll need to store these during render
    #         if hasattr(self, 'current_clickable_areas'):
    #             for area_id, area_data in self.current_clickable_areas.items():
    #                 if isinstance(area_data, dict) and 'rect' in area_data:
    #                     input_handler.register_clickable(
    #                         screen_name='combat',
    #                         rect=area_data['rect'],
    #                         event_type='COMBAT_ACTION',
    #                         event_data=area_data
    #                     )
    #         print("Combat clickables registered with InputHandler")

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
        
        title_font = fonts.get('fantasy_medium', fonts.get('medium', fonts['normal']))
        text_font = fonts.get('fantasy_small', fonts['normal'])
        
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
                    color = BLACK  # Floor was DARK_BLUE
                
                # Draw square
                pygame.draw.rect(surface, color, square_rect)
                pygame.draw.rect(surface, WHITE, square_rect, 1)  # Border
                
                # Register clickable area
                clickable_areas[f"grid_{x}_{y}"] = {
                    "rect": square_rect,
                    "action": "GRID_CLICK",
                    "grid_pos": [x, y]
                }
        
        return clickable_areas
    
    def _render_battlefield_units(self, surface: pygame.Surface, combat_data: Dict):
        """Render player and enemy units on the battlefield"""
        
        # Render player unit
        player_position = combat_data.get("player_position")
        if player_position and len(player_position) == 2:
            x, y = player_position
            screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
            screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2)
            
            # Draw player as blue circle with "P" label
            pygame.draw.circle(surface, BLUE, (screen_x, screen_y), self.tile_size // 3)
            
            # Player label
            font = pygame.font.Font(None, 24)
            text_surface = font.render("P", True, WHITE)
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            surface.blit(text_surface, text_rect)
        
        # Render enemy units
        enemy_instances = combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            position = enemy.get("position", [])
            if len(position) == 2:
                x, y = position
                screen_x = self.grid_offset_x + (x * self.tile_size) + (self.tile_size // 2)
                screen_y = self.grid_offset_y + (y * self.tile_size) + (self.tile_size // 2)
                
                # Draw enemy as red circle with first letter of name
                pygame.draw.circle(surface, RED, (screen_x, screen_y), self.tile_size // 3)
                
                # Enemy label (first letter of name)
                name = enemy.get("name", "E")
                label = name[0].upper()
                font = pygame.font.Font(None, 24)
                text_surface = font.render(label, True, WHITE)
                text_rect = text_surface.get_rect(center=(screen_x, screen_y))
                surface.blit(text_surface, text_rect)
    
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
        panel_x = 800  # Right side of screen
        panel_y = 150
        
        button_font = fonts.get('fantasy_small', fonts['normal'])
        text_font = fonts.get('fantasy_micro', fonts['normal'])
        
        # Current unit status
        current_y = panel_y
        draw_text(surface, "Current Unit:", text_font, 750, current_y, CYAN)
        
        current_y += 30

        # TODO: Show current unit stats (HP, actions remaining, etc.)
        draw_text(surface, "HP: 20/20", text_font, 750, current_y, WHITE)
        current_y += 50
        
        # Action buttons
        action_buttons = ["MOVE", "ATTACK", "SPELL", "END_TURN"]
        button_width = 80
        button_height = 30
        
        for i, action in enumerate(action_buttons):
            button_y = current_y + (i * (button_height + 10))
            button_rect = pygame.Rect(panel_x - (button_width // 2), button_y, button_width, button_height)
            
            # Determine button state (active, disabled, etc.)
            if action != "SPELL":
                button_state = "active"
            else:
                button_state = "disabled"  # Disable spell for now

            draw_combat_button(surface, button_rect.x, button_rect.y, button_width, button_height,
                    action, button_font, button_state)
            
            if action != "SPELL":  # Don't register disabled buttons
                button_id = f"button_{action.lower()}"
                clickable_areas[f"button_{action.lower()}"] = {
                    "rect": button_rect,
                    "action": action.upper(),
                    "button_type": action.lower()
                }
                
        current_y += len(action_buttons) * (button_height + 10) + 30
        
        # Combat log
        draw_text(surface, "Combat Log:", text_font, 750, current_y, CYAN)
        current_y += 25
        
        # TODO: Show combat log messages
        log_messages = ["Combat begins!", "Waiting for player action..."]
        for message in log_messages[-4:]:  # Show last 4 messages
            draw_text(surface, message[:30], text_font, 750, current_y, WHITE)
            current_y += 120
        
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
    
    # ==========================================
    # ACTION HANDLERS
    # ==========================================
    
    # def _handle_grid_click(self, grid_pos: List[int], game_state, event_manager) -> Optional[str]:
    #     """Handle clicks on battlefield grid"""
    #     if not grid_pos or len(grid_pos) != 2:
    #         return None
        
    #     x, y = grid_pos
    #     print(f"🎯 Grid clicked: [{x}, {y}]")
        
    #     # TODO: Handle based on selected action
    #     if self.selected_action == "move":
    #         # Validate movement and emit move event
    #         event_manager.emit("COMBAT_MOVE_UNIT", {"target_position": [x, y]})
    #     elif self.selected_action == "attack":
    #         # Validate attack target and emit attack event
    #         event_manager.emit("COMBAT_ATTACK_TARGET", {"target_position": [x, y]})
        
    #     return None
    
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
        if game_controller:  # game_controller is actually the CombatEngine
            game_controller.set_action_mode("attack")

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

    def handle_end_turn_action(event_data):
        """Handle END_TURN button click"""
        print("END_TURN button clicked")
        if game_controller:
            # Import the enum at the top of combat_system.py
            from game_logic.combat_engine import CombatPhase
            game_controller.current_phase = CombatPhase.ENEMY_TURN
            print("Player turn ended, enemy turn begins")
        
    def handle_combat_back(event_data):
        """Handle return to previous screen"""
        print("🔙 COMBAT_BACK EVENT HANDLER CALLED!")
        if hasattr(game_controller.game_state, 'previous_screen') and game_controller.game_state.previous_screen:
            game_controller.game_state.screen = game_controller.game_state.previous_screen
        else:
            game_controller.game_state.screen = "broken_blade_main"
        print(f"Returning to: {game_controller.game_state.screen}")
    
    # Register the actual event names being emitted
    event_manager.register("MOVE", handle_move_action)
    event_manager.register("ATTACK", handle_attack_action)
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