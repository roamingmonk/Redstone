# ui/combat_system.py
"""
CombatSystem - Step 1: Basic UI Presentation Layer
Generic, JSON-driven UI system - NO business logic
Delegates all logic to CombatEngine
"""

import pygame
from typing import Dict, Any, Optional
from utils.constants import *
from utils.graphics import draw_button, draw_centered_text

class CombatEncounter:
    """
    Generic Combat UI System - Step 1: Basic Integration
    
    Handles combat screen presentation and user interaction.
    Delegates ALL business logic to CombatEngine.
    Follows BaseLocation architecture pattern.
    """
    
    def __init__(self, encounter_id: str):
        """
        Initialize combat encounter UI
        
        Args:
            encounter_id: Identifier for this encounter
        """
        self.encounter_id = encounter_id
        self.screen_name = "combat"
        
        print(f"🎮 CombatEncounter UI created for: {encounter_id}")
    
    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, 
              controller=None) -> Dict[str, Any]:
        """
        Main rendering function - follows BaseLocation pattern
        
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
        return self._render_combat_interface(surface, combat_data, fonts, controller)
    
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
        
        if action_type == "TEST_VICTORY":
            # Delegate to CombatEngine for business logic
            event_manager.emit("COMBAT_TEST_VICTORY", {})
            return None
            
        elif action_type == "TEST_DEFEAT":
            # Delegate to CombatEngine for business logic
            event_manager.emit("COMBAT_TEST_DEFEAT", {})
            return None
            
        elif action_type == "COMBAT_BACK":
            # Return to previous screen
            return "broken_blade_main"
        
        return None
    
    # ==========================================
    # RENDERING METHODS
    # ==========================================
    
    def _render_combat_interface(self, surface: pygame.Surface, combat_data: Dict, 
                                fonts: Dict, controller) -> Dict[str, Any]:
        """Render main combat interface"""
        
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        text_font = fonts.get('fantasy_medium', fonts['normal'])
        
        # Title
        draw_centered_text(surface, "COMBAT SYSTEM", title_font, 80, BRIGHT_GREEN)
        draw_centered_text(surface, "(Step 1: Integration Test)", text_font, 110, GRAY)
        
        # Encounter information
        encounter_name = combat_data.get("encounter_name", "Unknown Encounter")
        draw_centered_text(surface, f"Encounter: {encounter_name}", text_font, 160, YELLOW)
        
        # Combat state
        combat_state = combat_data.get("state", "unknown")
        state_color = self._get_state_color(combat_state)
        draw_centered_text(surface, f"Status: {combat_state.title()}", text_font, 190, state_color)
        
        # Combat log
        self._render_combat_log(surface, combat_data, fonts)
        
        # Action buttons
        return self._render_action_buttons(surface, combat_data, fonts)
    
    def _render_combat_log(self, surface: pygame.Surface, combat_data: Dict, fonts: Dict):
        """Render combat log messages"""
        log_font = fonts.get('fantasy_small', fonts['normal'])
        
        draw_centered_text(surface, "Combat Log:", log_font, 250, CYAN)
        
        combat_log = combat_data.get("combat_log", [])
        for i, message in enumerate(combat_log[-4:]):  # Show last 4 messages
            y_pos = 280 + (i * 25)
            draw_centered_text(surface, str(message), log_font, y_pos, WHITE)
    
    def _render_action_buttons(self, surface: pygame.Surface, combat_data: Dict, 
                              fonts: Dict) -> Dict[str, Any]:
        """Render action buttons and return clickable areas"""
        
        clickable_areas = {}
        button_font = fonts.get('fantasy_medium', fonts['normal'])
        
        # Test buttons (Step 1 only)
        if combat_data.get("can_test_victory", False):
            victory_rect = pygame.Rect(250, 400, 150, 50)
            draw_button(surface, 250, 400, 150, 50, "TEST VICTORY", button_font)
            clickable_areas["test_victory"] = victory_rect
        
        if combat_data.get("can_test_defeat", False):
            defeat_rect = pygame.Rect(450, 400, 150, 50)
            draw_button(surface, 450, 400, 150, 50, "TEST DEFEAT", button_font)
            clickable_areas["test_defeat"] = defeat_rect
        
        # Back button (always available)
        back_rect = pygame.Rect(412, 500, 200, 50)
        draw_button(surface, 412, 500, 200, 50, "BACK TO TAVERN", button_font)
        clickable_areas["back_button"] = back_rect
        
        return clickable_areas
    
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
        draw_button(surface, 412, 400, 200, 50, "BACK TO TAVERN", text_font)
        
        return {"back_button": back_rect}
    
    def _render_data_error(self, surface: pygame.Surface, fonts: Dict, error_msg: str) -> Dict[str, Any]:
        """Render error when combat data unavailable"""
        surface.fill(BLACK)
        
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        text_font = fonts.get('fantasy_medium', fonts['normal'])
        
        draw_centered_text(surface, "COMBAT DATA ERROR", title_font, 250, RED)
        draw_centered_text(surface, error_msg[:40], text_font, 300, WHITE)
        
        # Back button
        back_rect = pygame.Rect(412, 400, 200, 50)
        draw_button(surface, 412, 400, 200, 50, "BACK TO TAVERN", text_font)
        
        return {"back_button": back_rect}
    
    def _get_state_color(self, state: str):
        """Get color for combat state display"""
        state_colors = {
            "not_started": GRAY,
            "active": GREEN,
            "victory": BRIGHT_GREEN,
            "defeat": RED
        }
        return state_colors.get(state, WHITE)

# ==========================================
# SCREENMANAGER INTEGRATION
# ==========================================

def draw_combat_screen(surface: pygame.Surface, game_state, fonts: Dict, images: Dict, controller=None):
    """
    ScreenManager integration function - Step 1
    
    Creates CombatEncounter and delegates rendering
    Follows established screen function pattern
    """
    
    # Create combat encounter UI (Step 1: hardcoded encounter)
    encounter_id = "tavern_basement_rats"  # TODO: Get from game state or parameter
    combat_encounter = CombatEncounter(encounter_id)
    
    # Delegate to combat encounter render method
    clickable_areas = combat_encounter.render(surface, game_state, fonts, images, controller)
    # 🔧 ADD THIS SECTION - Register clickables with InputHandler
    if controller and hasattr(controller, 'input_handler') and controller.input_handler:
        input_handler = controller.input_handler
        if hasattr(input_handler, 'register_combat_clickables'):
            input_handler.register_combat_clickables("combat", clickable_areas)
            print(f"🎮 Registered {len(clickable_areas)} combat clickables")
        else:
            print("⚠️ InputHandler missing register_combat_clickables method")
    else:
        print("⚠️ No InputHandler available for combat registration")
    
    return clickable_areas

# ==========================================
# EVENT HANDLERS
# ==========================================

def register_combat_system_events(event_manager, game_controller):
    """Register CombatSystem event handlers"""
    
    def handle_test_victory(event_data):
        """Handle test victory button"""
        combat_engine = getattr(game_controller, 'combat_engine', None)
        if combat_engine:
            combat_engine.end_combat("victory")
            game_controller.game_state.screen = "broken_blade_main"
    
    def handle_test_defeat(event_data):
        """Handle test defeat button"""
        combat_engine = getattr(game_controller, 'combat_engine', None)
        if combat_engine:
            combat_engine.end_combat("defeat")
            game_controller.game_state.screen = "broken_blade_main"
    
    def handle_combat_back(event_data):
        """Handle back to tavern button"""
        game_controller.game_state.screen = "broken_blade_main"
    
    # Register event handlers
    event_manager.register("COMBAT_TEST_VICTORY", handle_test_victory)
    event_manager.register("COMBAT_TEST_DEFEAT", handle_test_defeat)
    event_manager.register("COMBAT_BACK", handle_combat_back)
    
    print("🎮 CombatSystem events registered")

# ==========================================
# INTEGRATION SETUP
# ==========================================

def setup_combat_system_integration(screen_manager, event_manager, game_controller):
    """
    Complete CombatSystem integration setup - Modified for your architecture
    """
    
    # Register combat screen render function
    screen_manager.register_render_function("combat", draw_combat_screen)
    
    # Register event handlers
    register_combat_system_events(event_manager, game_controller)
    
    # Register screen lifecycle hooks (following your pattern)
    def combat_enter_hook(game_state):
        """Called when entering combat screen"""
        print("🎯 Entering combat screen")
        # Register clickables when entering combat screen
        if hasattr(game_controller, 'input_handler'):
            # This will be called after render, need to set up callback
            pass
    
    def combat_exit_hook(game_state):
        """Called when leaving combat screen"""
        print("🎯 Exiting combat screen")
    
    screen_manager.register_enter_hook("combat", combat_enter_hook)
    screen_manager.register_exit_hook("combat", combat_exit_hook)
    
    # Set up custom clickable handling for combat screen
    original_render_screen = getattr(screen_manager, 'render_screen', None)
    
    def enhanced_render_screen(screen_name, surface, game_state, fonts, images, controller):
        """Enhanced render that handles combat clickables"""
        
        # Call original render method
        if screen_name in screen_manager.render_functions:
            render_func = screen_manager.render_functions[screen_name]
            result = render_func(surface, game_state, fonts, images, controller)
            
            # Handle combat screen clickables specially
            if screen_name == "combat" and isinstance(result, dict):
                input_handler = getattr(controller, 'input_handler', None)
                if input_handler and hasattr(input_handler, 'register_combat_clickables'):
                    input_handler.register_combat_clickables(screen_name, result)
            
            return result
        
        return None
    
    # Store the enhanced render method
    screen_manager.enhanced_render_screen = enhanced_render_screen
    
    print("✅ CombatSystem integration complete")
