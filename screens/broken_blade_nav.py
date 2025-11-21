# screens/broken_blade_nav.py
"""
Broken Blade Tavern Navigation Screen
Scrollable tile-based interior exploration
"""

import pygame
from ui.base_location_navigation import NavigationRenderer
from utils.constants import (BLACK, WHITE, YELLOW, CYAN, RED, 
                             DARK_BROWN, WARM_GOLD, FIRE_BRICK_RED, 
                             PURPLE_BLUE, AUBURN_BROWN, VERY_DARK_GRAY, 
                             LIGHTEST_GRAY, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT)
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from data.maps.broken_blade_map import *

class BrokenBladeNav:
    """Navigation screen for Broken Blade tavern interior"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        config = {
            'map_width': BROKEN_BLADE_WIDTH,
            'map_height': BROKEN_BLADE_HEIGHT,
            'location_id': 'broken_blade_tavern',
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_tile_color': get_tile_color,
                'get_building_info': self._get_interaction_at_tile,
                'get_searchable_info': None,  # No searchables in tavern
                'get_combat_trigger': None,   # No random combat in tavern
                'get_location_npcs': self._get_current_npcs
            },
            'spawn_position': (TAVERN_SPAWN_X, TAVERN_SPAWN_Y)
        }
        
        self.renderer = NavigationRenderer(config)
        self.temp_message = None
        self.temp_message_timer = 0
        self.just_entered_screen = True
    
    def _get_current_npcs(self, game_state):
        """Get NPCs that should be visible based on game state"""
        return get_visible_npcs(game_state)
    
    def _get_interaction_at_tile(self, player_x, player_y, game_state):
        """
        Check what player can interact with at current position
        Priority: NPCs > Transitions > Special Areas
        """
        # Priority 1: Check for NPC interaction
        npc_id, npc_data = get_npc_interaction_at_tile(player_x, player_y)
        if npc_id:
            # Verify NPC is visible (not recruited, correct act, etc.)
            visible_npcs = get_visible_npcs(game_state)
            if npc_id in visible_npcs:
                return {
                    'name': npc_data['display_name'],
                    'interaction_type': 'npc',
                    'target_screen': npc_data['dialogue_id'],
                    'action': f"Talk to {npc_data['display_name']}",
                    'npc_id': npc_id
                }
        
        # Priority 2: Check for area transitions (exits, basement)
        transition = get_transition_at_entrance(player_x, player_y, game_state)
        if transition:
            return transition
        
        # Priority 3: Check basement if not available yet (locked message)
        if (player_x, player_y) in [(1, 1), (2, 1), (1, 2)]:  # Basement stairs area
            # Check if basement quest not accepted yet
            if not getattr(game_state, 'accepted_basement_quest', False):
                return {
                    'name': 'Locked Basement',
                    'interaction_type': 'blocked',
                    'action': 'The basement door is locked',
                    'message': 'Perhaps the bartender knows something...'
                }
        
        # Priority 4: Check for special areas (dice game)
        special = get_special_area_at_tile(player_x, player_y)
        if special:
            return special
        
        return None
    
    def update_player_position(self, game_state):
        """Initialize or restore player position in tavern"""
        if not hasattr(game_state, 'tavern_x'):
            game_state.tavern_x = TAVERN_SPAWN_X
            game_state.tavern_y = TAVERN_SPAWN_Y
        
        self.renderer.update_camera(game_state.tavern_x, game_state.tavern_y)
    
    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)
        
        # Reset cooldown when first entering screen
        if self.just_entered_screen:
            self.renderer.transition_cooldown = 0
            self.just_entered_screen = False
        
        # Update temp message timer
        if self.temp_message_timer > 0:
            self.temp_message_timer -= dt
            if self.temp_message_timer <= 0:
                self.temp_message = None
        
        # Handle movement
        old_x = game_state.tavern_x
        old_y = game_state.tavern_y
        
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)
        
        # Update position if moved
        if new_x != old_x or new_y != old_y:
            game_state.tavern_x = new_x
            game_state.tavern_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Update transition cooldown
        self.renderer.update_transition_cooldown(dt)
        
        # Check for ENTER key interactions
        if (self.renderer.check_enter_just_pressed(keys) and 
            self.renderer.can_interact()):
            
            player_x = game_state.tavern_x
            player_y = game_state.tavern_y
            
            # Get interaction at current tile
            interaction = self._get_interaction_at_tile(player_x, player_y, game_state)
            
            if interaction:
                interaction_type = interaction.get('interaction_type')
                
                # Handle blocked interactions (locked doors, etc.)
                if interaction_type == 'blocked':
                    message = interaction.get('message', 'Cannot interact')
                    self.show_temp_message(message)
                    return
                
                # Handle NPC dialogue
                if interaction_type == 'npc':
                    if controller:
                        target_screen = interaction['target_screen']
                        npc_id = interaction['npc_id']
                        
                        # Set return screen for dialogue system
                        setattr(game_state, f'{npc_id}_return_screen', 'broken_blade_nav')
                        setattr(game_state, f'{npc_id}_current_location', 'broken_blade_nav')
                        game_state.previous_screen = 'broken_blade_nav'
                        
                        self.renderer.start_transition_cooldown()
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            'target_screen': target_screen,
                            'source_screen': 'broken_blade_nav'
                        })
                    return
                
                # Handle navigation (exits, dice game, basement)
                if interaction_type == 'navigation':
                    if controller:
                        target_screen = interaction['target_screen']
                        game_state.previous_screen = 'broken_blade_nav'
                        self.renderer.start_transition_cooldown()
                        self.just_entered_screen = True 
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            'target_screen': target_screen,
                            'source_screen': 'broken_blade_nav'
                        })
                    return
                
                # Handle combat (basement rats)
                if interaction_type == 'combat':
                    if controller:
                        combat_encounter = interaction.get('combat_encounter')
                        game_state.previous_screen = 'broken_blade_nav'
                        game_state.current_combat_encounter = combat_encounter
                        self.renderer.start_transition_cooldown()
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            'target_screen': 'combat',
                            'source_screen': 'broken_blade_nav'
                        })
                    return
    
    def show_temp_message(self, message, duration=2.0):
        """Display temporary message to player"""
        self.temp_message = message
        self.temp_message_timer = duration
    
    def render(self, screen, game_state, fonts, images):
        """Render tavern navigation screen"""
        screen.fill(BLACK)
        
        # Get player position
        player_x = game_state.tavern_x
        player_y = game_state.tavern_y
        
        # Draw map tiles
        self.renderer.draw_map(screen, fonts, player_x, player_y)
        
        # Draw player sprite
        self.renderer.draw_player(screen, player_x, player_y)
        
        # Draw NPCs
        visible_npcs = get_visible_npcs(game_state)
        for npc_id, npc_data in visible_npcs.items():
            npc_x, npc_y = npc_data['position']
            screen_x = (npc_x * 64) - self.renderer.camera_x
            screen_y = (npc_y * 64) - self.renderer.camera_y
            
            # Only draw if in visible area
            if (-64 <= screen_x <= self.renderer.display_width and
                -64 <= screen_y <= self.renderer.display_height):
                # Draw NPC as colored circle (placeholder)
                npc_color = self._get_npc_color(npc_data['sprite_type'])
                pygame.draw.circle(
                    screen,
                    npc_color,
                    (int(screen_x + 32), int(screen_y + 32)),
                    16
                )
        
        # Draw party status panel
        draw_party_status_panel(screen, game_state, fonts)
        
        # Draw temp message if active
        if self.temp_message and self.temp_message_timer > 0:
            message_y = 50
            draw_centered_text(
                screen, 
                self.temp_message, 
                fonts['fantasy_medium'],
                message_y,
                YELLOW
            )
        
        # Draw location title
        draw_centered_text(
            screen, 
            "THE BROKEN BLADE TAVERN",
            fonts['fantasy_large'],
            20,
            YELLOW
        )
        
        # Draw dialog/interaction area at bottom
        dialog_margin = 0
        draw_border(screen, dialog_margin, LAYOUT_DIALOG_Y, 1024 - (dialog_margin * 2), LAYOUT_DIALOG_HEIGHT)
        
        # Draw interaction prompt at bottom
        self._draw_interaction_prompt(screen, game_state, fonts)
        
        return {}
    
    def _get_npc_color(self, sprite_type):
        """Get color for NPC sprite placeholder using constants"""
        colors = {
            'bartender': DARK_BROWN,       # Brown bartender
            'server': WHITE,               # Server (white apron)
            'noble': WARM_GOLD,            # Gold for nobility (Mayor)
            'warrior': FIRE_BRICK_RED,     # Red warrior
            'mage': PURPLE_BLUE,           # Purple mage
            'dwarf': AUBURN_BROWN,         # Brown dwarf
            'rogue': VERY_DARK_GRAY,       # Dark gray rogue (sneaky)
            'commoner': LIGHTEST_GRAY,     # Light gray commoner
        }
        return colors.get(sprite_type, LIGHTEST_GRAY)  # Default to light gray
    
    def _draw_interaction_prompt(self, screen, game_state, fonts):
        """Draw prompt for what player can interact with"""
        player_x = game_state.tavern_x
        player_y = game_state.tavern_y
        
        interaction = self._get_interaction_at_tile(player_x, player_y, game_state)
        
        prompt_y = LAYOUT_DIALOG_Y + 15  # Position inside the dialog border
        
        if interaction:
            if interaction.get('interaction_type') == 'blocked':
                # Blocked interaction (locked door, etc.)
                prompt_text = f"🚫 {interaction.get('message', 'Blocked')}"
                draw_centered_text(screen, prompt_text, fonts['fantasy_medium'], prompt_y, RED)
            else:
                # Available interaction
                action = interaction.get('action', 'Interact')
                prompt_text = f"Press ENTER: {action}"
                draw_centered_text(screen, prompt_text, fonts['fantasy_medium'], prompt_y, CYAN)
        else:
            # Movement instructions
            prompt_text = "Arrow Keys: Move | ENTER: Interact | I/Q/C/H: Menus"
            draw_centered_text(screen, prompt_text, fonts['fantasy_small'], prompt_y, WHITE)

# === SCREEN INTERFACE FUNCTIONS ===

_broken_blade_nav_instance = None

def draw_broken_blade_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _broken_blade_nav_instance
    
    if _broken_blade_nav_instance is None:
        _broken_blade_nav_instance = BrokenBladeNav()
    
    # Handle input
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16  # Approximate milliseconds per frame (60 FPS)
        _broken_blade_nav_instance.update(dt, keys, game_state, controller)
    
    # Render
    return _broken_blade_nav_instance.render(surface, game_state, fonts, images)