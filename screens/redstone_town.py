# screens/redstone_town.py
"""
Redstone Town Navigation - Using shared NavigationRenderer utility
"""

import pygame
from ui.base_location_navigation import NavigationRenderer
from utils.constants import *
from utils.graphics import draw_border, draw_centered_text
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from utils.narrative_schema import narrative_schema

# Import town map data
try:
    from data.maps.redstone_town_map import *
except ImportError:
    # Fallback data
    TOWN_WIDTH, TOWN_HEIGHT = 16, 12
    TOWN_SPAWN_X, TOWN_SPAWN_Y = 8, 6
    def get_tile_type(x, y): return 'street'
    def is_walkable(x, y): return True
    def get_building_info(x, y): return None

class RedstoneTownNavigation:
    def __init__(self):
        # Configure the shared renderer
        config = {
            'map_width': TOWN_WIDTH,
            'map_height': TOWN_HEIGHT,
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_building_info': get_building_at_entrance
            }
        }
        
        self.renderer = NavigationRenderer(config)
        self.current_building = None
        self.showing_temp_message = False
        self.temp_message_text = ""
        self.temp_message_timer = 0

        # Use shared graphics manager (singleton)
        self.graphics_manager = get_tile_graphics_manager()

        print("Town navigation initialized with shared renderer")
    
    def update_player_position(self, game_state):
        """Initialize player position if needed"""
        if not hasattr(game_state, 'town_player_x'):
            game_state.town_player_x = TOWN_SPAWN_X
            game_state.town_player_y = TOWN_SPAWN_Y
            print(f"Player spawned at ({TOWN_SPAWN_X}, {TOWN_SPAWN_Y})")
        
        self.renderer.update_camera(game_state.town_player_x, game_state.town_player_y)
    
    def update(self, dt, keys, game_state, controller=None):
        """Update town navigation state"""
        # Handle movement using shared renderer
        new_x, new_y = self.renderer.handle_movement(
            keys, game_state.town_player_x, game_state.town_player_y
        )
        
        # Update position if moved
        if new_x != game_state.town_player_x or new_y != game_state.town_player_y:
            game_state.town_player_x = new_x
            game_state.town_player_y = new_y
            self.renderer.update_camera(new_x, new_y)
            
            # Check for building interaction
            self.current_building = get_building_at_entrance(new_x, new_y)
        
        # Handle building entry
        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]) and self.current_building:
            interaction_type = self.current_building.get('interaction_type')
            
            if interaction_type == 'npc_dialogue':
                npc_id = self.current_building.get('npc_id')
                if npc_id and controller:
                    # Get location from narrative schema
                    location = narrative_schema.get_npc_location(npc_id, 'redstone_town')
                    controller.event_manager.emit("NPC_CLICKED", {
                        'npc_id': npc_id,
                        'location': location
                    })
            
            elif interaction_type == 'screen_transition':
                screen = self.current_building.get('screen')
                if screen and controller:
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        'target_screen': screen,
                        'source': 'town_navigation'
                    })
            
            else:
                # Default closed message
                self.showing_temp_message = True
                self.temp_message_text = "Sorry, it is closed."
    
    def render(self, surface, fonts, game_state):
        """Render town navigation screen"""
        surface.fill(BLACK)
        self.update_player_position(game_state)
        
        # Draw party status panel
        draw_party_status_panel(surface, game_state, fonts)
        
        # Draw map area border
        draw_border(surface, 0, LAYOUT_IMAGE_Y, 
                   self.renderer.display_width, self.renderer.display_height)
        
        # Create map surface and draw using shared renderer
        map_surface = surface.subsurface(6, LAYOUT_IMAGE_Y + 6,
                                        self.renderer.display_width - 12, 
                                        self.renderer.display_height - 12)
        
        self.renderer.draw_map(map_surface, fonts, game_state.town_player_x, game_state.town_player_y, surface)

        # Draw interaction prompts
        if self.showing_temp_message:
            still_showing = self.renderer.draw_temp_message(
                surface, fonts, self.temp_message_text, self.temp_message_timer
            )
            if not still_showing:
                self.showing_temp_message = False
        else:
            building_name = self.current_building.get('name') if self.current_building else None
            self.renderer.draw_interaction_prompt(surface, fonts, building_name)
        
        # Instructions
        #=== DIALOG ZONE (FULL SCREEN WIDTH) ===
        dialog_y = LAYOUT_DIALOG_Y
        dialog_height = LAYOUT_DIALOG_HEIGHT
        dialog_margin = 0

        # Use full 1024 width for dialog box
        draw_border(surface, dialog_margin, dialog_y, 1024 - (dialog_margin * 2), dialog_height) 
        
        instructions = [
            "Use ARROW KEYS or WASD to move around town",
            "Press ENTER near buildings to enter them",
            "Press ESC to return to tavern"
        ]
        text_y = dialog_y + 20
        for instruction in instructions:
            draw_centered_text(surface, instruction, fonts.get('fantasy_small', fonts['normal']),
                             text_y, WHITE)
            text_y += 25
        
        return {}

# Integration function for ScreenManager
_town_navigation_instance = None

def render_town_navigation(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _town_navigation_instance
    
    if _town_navigation_instance is None:
        _town_navigation_instance = RedstoneTownNavigation()
    
    # Handle input
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _town_navigation_instance.update(dt, keys, game_state, controller)
    
    # Render
    return _town_navigation_instance.render(surface, fonts, game_state)