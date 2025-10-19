# screens/redstone_town.py
"""
Redstone Town Navigation - Using shared NavigationRenderer utility
"""

import pygame
from ui.base_location_navigation import NavigationRenderer, calculate_required_direction
from utils.constants import *
from utils.graphics import draw_border, draw_centered_text
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from utils.narrative_schema import narrative_schema
from data.maps.redstone_town_map import BUILDING_ENTRANCES
from utils.world_npc_spawner import get_world_npc_spawner

# Import town map data
try:
    from data.maps.redstone_town_map import *

    print(f"DEBUG: Imported spawn point = ({TOWN_SPAWN_X}, {TOWN_SPAWN_Y})")
except ImportError:
    # Fallback data
    print("DEBUG: Using fallback spawn")
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
            'location_id': 'redstone_town', 
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_building_info': get_building_at_entrance,
                'get_tile_color': get_tile_color
            }
        }
        
        self.renderer = NavigationRenderer(config)
        self.current_building = None
        self.showing_temp_message = False
        self.temp_message_text = ""
        self.temp_message_timer = 0

        self.current_npc = None
        self.npc_required_direction = None
        self.can_interact_npc = False

        # Use shared graphics manager (singleton)
        self.graphics_manager = get_tile_graphics_manager()
        # After all your imports, before the class definition:
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
        # Initialize position FIRST before using it
        self.update_player_position(game_state)
        
        # Handle movement using shared renderer
        new_x, new_y = self.renderer.handle_movement(
            keys, game_state.town_player_x, game_state.town_player_y
        )
        
        # Update position if moved
        if new_x != game_state.town_player_x or new_y != game_state.town_player_y:
            game_state.town_player_x = new_x
            game_state.town_player_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Check for building interactions with direction validation
        building_at_entrance = get_building_at_entrance(
            game_state.town_player_x, 
            game_state.town_player_y
        )
        
        # Calculate if player is facing the correct direction
        self.can_interact = False
        self.required_direction = None
        
        if building_at_entrance:
            
            # Find which building this entrance belongs to
            for building_id, building_data in BUILDING_ENTRANCES.items():
                entrance_tiles = building_data['entrance_tiles']
                if (game_state.town_player_x, game_state.town_player_y) in entrance_tiles:
                    # Found the building - get its position
                    building_pos = building_data['building_pos']
                    
                    # Calculate required direction
                    self.required_direction = calculate_required_direction(
                        game_state.town_player_x,
                        game_state.town_player_y,
                        building_pos
                    )
                    
                    # Check if player is facing the correct direction (or if direction check disabled)
                    skip_direction = building_at_entrance.get('skip_direction_check', False)
                    if skip_direction or self.renderer.player_direction == self.required_direction:
                        self.current_building = building_at_entrance
                        self.can_interact = True
                    else:
                        self.current_building = None
                        self.can_interact = False
                    break
        else:
            self.current_building = None

        # Check for NPC interactions with direction validation
        npc_info, npc_required_dir, can_interact_npc = self.renderer.check_npc_interaction(
            game_state.town_player_x,
            game_state.town_player_y,
            self.renderer.player_direction,
            'redstone_town',
            game_state
        )
        
        self.current_npc = npc_info if can_interact_npc else None
        self.npc_required_direction = npc_required_dir
        self.can_interact_npc = can_interact_npc
        
        # Handle building entry OR NPC dialogue (only if facing correct direction)
        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]):
            if self.current_building and self.can_interact:
                interaction_type = self.current_building.get('interaction_type')
                
                print(f"DEBUG: RT: hit return to go somewhere")
                
                if interaction_type == 'npc_dialogue':
                    print(f"DEBUG: RT: NPC Dialogue")
                    npc_id = self.current_building.get('npc_id')
                    
                    if npc_id and controller:
                        # Use current location (redstone_town), not narrative schema
                        location = 'redstone_town'
                        target_screen = f"{location}_{npc_id}"  # ✅ Constructs 'redstone_town_mayor'
                    
                        # CHECK: Is the target dialogue screen implemented?
                        if hasattr(controller, 'screen_manager') and target_screen in controller.screen_manager.render_functions:
                            # Screen exists, proceed with NPC dialogue
                            controller.event_manager.emit("NPC_CLICKED", {
                                'npc_id': npc_id,
                                'location': location
                            })
                        else:
                            # NPC dialogue screen not implemented yet
                            self.showing_temp_message = True
                            self.temp_message_timer = pygame.time.get_ticks()
                            
                            # Contextual messages based on NPC
                            if npc_id == 'mayor':
                                self.temp_message_text = "The mayor is in an important meeting and cannot be disturbed."
                            else:
                                self.temp_message_text = "They seem too busy to talk right now."
                
                elif interaction_type == 'screen_transition':
                    print(f"DEBUG: RT: Screen Transition")
                    screen = self.current_building.get('screen')
                    
                    if screen and controller:
                        # CHECK: Is this screen actually implemented?
                        if hasattr(controller, 'screen_manager') and screen in controller.screen_manager.render_functions:
                            # Screen exists, proceed with transition
                            controller.event_manager.emit("SCREEN_CHANGE", {
                                'target_screen': screen,
                                'source': 'town_navigation'
                            })
                        else:
                            # Screen not implemented yet - show contextual message
                            self.showing_temp_message = True
                            self.temp_message_timer = pygame.time.get_ticks()
                            
                            # Contextual messages based on screen type
                            if screen == 'world_map':
                                self.temp_message_text = "The town gates are sealed. The guards won't let anyone leave right now."
                            else:
                                self.temp_message_text = "Sorry, it's closed."
                elif interaction_type == 'combat':
                    print(f"DEBUG: RT: Combat Trigger")
                    combat_encounter = self.current_building.get('combat_encounter')
                    combat_context = self.current_building.get('combat_context', {})
                    
                    if combat_encounter and controller:
                        # Store combat data in game state (BaseLocation pattern)
                        print(f"🗡️ Starting combat: {combat_encounter}")
                        game_state.previous_screen = game_state.screen
                        game_state.current_combat_encounter = combat_encounter
                        if combat_context:
                            game_state.combat_context = combat_context
                        
                        # Navigate to combat screen
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            'target_screen': 'combat',
                            'source': 'town_navigation'
                        })
                    else:
                        # Fallback if combat data missing
                        self.showing_temp_message = True
                        self.temp_message_timer = pygame.time.get_ticks()
                        self.temp_message_text = "The area is too dangerous to enter right now."

                else:
                    # Default closed message
                    print(f"DEBUG: RT: Sorry it is closed message!")
                    self.showing_temp_message = True
                    self.temp_message_text = "Sorry, it is closed."
                    self.temp_message_timer = pygame.time.get_ticks()
            
            elif self.current_npc and self.can_interact_npc:
                # NPC dialogue trigger
                npc_id = self.current_npc['dialogue_id']
                if controller:
                    # Construct screen name for checking: location_npcid pattern
                    location = 'redstone_town'
                    screen_name = f"{location}_{npc_id}"
                    
                    # Check if dialogue screen exists
                    if hasattr(controller, 'screen_manager') and screen_name in controller.screen_manager.render_functions:
                        # Dialogue exists - proceed
                        # IMPORTANT: Pass BASE location, not full screen name!
                        controller.event_manager.emit("NPC_CLICKED", {
                            'npc_id': npc_id,
                            'location': location  # Just 'redstone_town', not 'redstone_town_henrik'
                        })
                        
                        # Mark as talked
                        
                        get_world_npc_spawner().mark_npc_talked(npc_id, game_state)
                    else:
                        # NPC dialogue not implemented yet - use placeholder from data
                        self.showing_temp_message = True
                        self.temp_message_timer = pygame.time.get_ticks()
                        
                        # Get message from NPC data (data-driven!)
                        self.temp_message_text = self.current_npc.get(
                            'general_response',
                            f"{self.current_npc.get('display_name', 'NPC')} doesn't seem interested in talking."
                        )
        
    def render(self, surface, fonts, game_state):
        """Render town navigation screen"""
        surface.fill(BLACK)
                
        # Draw party status panel
        draw_party_status_panel(surface, game_state, fonts)
        
        # Draw map area border
        draw_border(surface, 0, LAYOUT_IMAGE_Y, 
                   self.renderer.display_width, self.renderer.display_height)
        
        # Create map surface and draw using shared renderer
        map_surface = surface.subsurface(6, LAYOUT_IMAGE_Y + 6,
                                        self.renderer.display_width - 12, 
                                        self.renderer.display_height - 12)
        
        # Draw the map (tiles and buildings)
        self.renderer.draw_map(map_surface, fonts, game_state.town_player_x, game_state.town_player_y, surface)
        
        # Draw NPCs (above tiles, below player)
        self.renderer.draw_npcs(map_surface, 'redstone_town', game_state)

        # Draw player (always on top)
        self.renderer.draw_player(map_surface, game_state.town_player_x, game_state.town_player_y)
        
        # Draw enhanced debug info with entrance information
        building_for_debug = self.current_building if self.can_interact else None
        self.renderer.draw_debug_with_entrance_info(
            surface, fonts, 
            game_state.town_player_x, game_state.town_player_y,
            building_for_debug, self.required_direction
        )

        # Draw interaction prompts
        if self.showing_temp_message:
            still_showing = self.renderer.draw_temp_message(
                surface, fonts, self.temp_message_text, self.temp_message_timer
            )
            if not still_showing:
                self.showing_temp_message = False
        else:
            # Show building or NPC interaction prompt
            if self.can_interact and self.current_building:
                building_name = self.current_building.get('name')
                self.renderer.draw_interaction_prompt(surface, fonts, building_name, True)
            elif self.can_interact_npc and self.current_npc:
                npc_name = self.current_npc.get('display_name')
                prompt_text = f"Talk to {npc_name}"
                self.renderer.draw_interaction_prompt(surface, fonts, prompt_text, True)
            else:
                self.renderer.draw_interaction_prompt(surface, fonts, None, False)
        
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