# screens/broken_blade_nav.py
"""
Broken Blade Tavern Navigation Screen
Scrollable tile-based interior exploration
"""

import pygame
from ui.base_location_navigation import NavigationRenderer
from utils.constants import (BLACK, WHITE, YELLOW, CYAN, RED, GRAY,
                             DARK_BROWN, WARM_GOLD, FIRE_BRICK_RED,
                             PURPLE_BLUE, AUBURN_BROWN, VERY_DARK_GRAY,
                             LIGHTEST_GRAY, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                             TILESETS_PATH)
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.broken_blade_map import *

from utils.tiled_loader import (
    load_tiled_map_with_names,
    get_tile_type,
    is_walkable_tile
)

from data.maps.broken_blade_tiles import (
    BROKEN_BLADE_TILE_MAP,
    BROKEN_BLADE_WALKABLE
)
from data.maps.broken_blade_map import (TAVERN_SPAWN_X, TAVERN_SPAWN_Y, get_visible_npcs, 
                                        get_npc_interaction_at_tile, get_transition_at_entrance,
                                        get_special_area_at_tile)

class BrokenBladeNav:
    """Navigation screen for Broken Blade tavern interior"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        # Load tileset from grid
        graphics_mgr = get_tile_graphics_manager()
        graphics_mgr.load_tileset_from_grid(
            'broken_blade',              # PNG filename (without extension)
            BROKEN_BLADE_TILE_MAP,       # Tile mapping
            tile_size=16,                # Source tile size in Aseprite
            columns=15                    # Number of columns in your PNG
        )
        
        # Load Tiled map
        try:
            self.tilemap = load_tiled_map_with_names(
                'broken_blade_map',       # TMJ filename (without extension)
                'broken_blade',
                BROKEN_BLADE_TILE_MAP,
                TILESETS_PATH
            )
            print(f"✅ Tilemap loaded: {self.tilemap['width']}x{self.tilemap['height']}")
            # Convert all layers to use tile names instead of indices
            if 'layers' in self.tilemap:
                for layer_name, layer_grid in self.tilemap['layers'].items():
                    named_layer = []
                    for row in layer_grid:
                        named_row = []
                        for tile_index in row:
                            if tile_index in BROKEN_BLADE_TILE_MAP:
                                tile_name = BROKEN_BLADE_TILE_MAP[tile_index]
                            else:
                                tile_name = None  # Unknown tiles become None
                            named_row.append(tile_name)
                        named_layer.append(named_row)
                    self.tilemap['layers'][layer_name] = named_layer
                print(f"✅ Converted {len(self.tilemap['layers'])} layers to use tile names")
            
            # Store layer names in render order
            self.layer_names = ['Floor', 'Rugs', 'Tile Layer 1', 'Details']

        except FileNotFoundError as e:
            print(f"❌ Tiled map file not found: {e}")
            # Fallback to old ASCII system
            #from data.maps.broken_blade_map import BROKEN_BLADE_WIDTH, BROKEN_BLADE_HEIGHT
            self.tilemap = {
                'width': BROKEN_BLADE_WIDTH,
                'height': BROKEN_BLADE_HEIGHT,
                'tile_grid': None  # Will use old system
            }
            self.layer_names = None
        
        config = {
            'tile_size': 64,
            'player_sprite_size': 64,
            'map_width': self.tilemap['width'],
            'map_height': self.tilemap['height'],
            'location_id': 'broken_blade_tavern',
            'tilemap': self.tilemap,              
            'layer_names': self.layer_names,      
            'map_functions': {
                'get_tile_type': lambda x, y: get_tile_type(x, y, self.tilemap['tile_grid']),
                # 'is_walkable': lambda x, y: is_walkable_tile(
                #     get_tile_type(x, y, self.tilemap['tile_grid']),
                #     BROKEN_BLADE_WALKABLE
                # ),
                'is_walkable': self._is_walkable_multi_layer, 
                'get_tile_color': None,  # Using graphics now, not colors
                'get_building_info': self._get_interaction_at_tile,
                'get_searchable_info': None,
                'get_combat_trigger': None,
                'get_location_npcs': self._get_current_npcs
            },
            'spawn_position': (TAVERN_SPAWN_X, TAVERN_SPAWN_Y),
            'spawn_direction': 'up'
        }
        
        self.renderer = NavigationRenderer(config)
        self.temp_message = None
        self.temp_message_timer = 0
        self.just_entered_screen = True
        self._current_game_state = None  # Stored for NPC collision checks
    
    def get_tile_from_layer(self, x, y, layer_name):
        """Get tile type from a specific layer"""
        if layer_name in self.tilemap.get('layers', {}):
            layer_grid = self.tilemap['layers'][layer_name]
            return get_tile_type(x, y, layer_grid)
        return None

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
    
    def _is_walkable_multi_layer(self, x, y):
        """
        Check if tile is walkable across ALL layers
        A tile is only walkable if ALL layers at that position are either:
        - None (empty)
        - A walkable tile
        """
        if not self.tilemap or not self.layer_names:
            return False
        
        # Check each layer in order
        for layer_name in self.layer_names:
            if layer_name not in self.tilemap.get('layers', {}):
                continue
            
            layer_grid = self.tilemap['layers'][layer_name]
            tile_name = get_tile_type(x, y, layer_grid)
            
            # Skip empty tiles
            if tile_name is None:
                continue
            
            # If tile exists and is NOT walkable, position is blocked
            if tile_name not in BROKEN_BLADE_WALKABLE:
                return False
        
        # Check if a visible NPC occupies this tile
        if self._current_game_state is not None:
            visible_npcs = get_visible_npcs(self._current_game_state)
            for npc_data in visible_npcs.values():
                if npc_data['position'] == (x, y):
                    return False

        # All layers are either empty or walkable, no NPC blocking
        return True

    
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
        
        # Store game_state for NPC collision checks in _is_walkable_multi_layer
        self._current_game_state = game_state

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
                        # Dismiss controls hint when player leaves the tavern
                        game_state.controls_hint_dismissed = True
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
    
    def render(self, screen, game_state, fonts, images, controller=None):
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
        portrait_rects = draw_party_status_panel(screen, game_state, fonts)

        # Register portrait clicks with InputHandler
        if controller and hasattr(controller, 'input_handler'):
            input_handler = controller.input_handler

            if 'player' in portrait_rects:
                input_handler.register_clickable(
                    'broken_blade_nav',
                    portrait_rects['player'],
                    "PORTRAIT_CLICKED",
                    {"target": "player", "tab": 1},
                    priority=150
                )

            for key, rect in portrait_rects.items():
                if key.startswith('npc_'):
                    input_handler.register_clickable(
                        'broken_blade_nav',
                        rect,
                        "PORTRAIT_CLICKED",
                        {"target": "party", "tab": 2},
                        priority=150
                    )
        
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
        
        if interaction:
            if interaction.get('interaction_type') == 'blocked':
                # Blocked interaction - show as temp message style
                prompt_text = f"🚫 {interaction.get('message', 'Blocked')}"
                prompt_font = fonts.get('fantasy_medium', fonts['normal'])
                draw_centered_text(screen, prompt_text, prompt_font, LAYOUT_DIALOG_Y + 15, RED)
            else:
                # Available interaction - use renderer's boxed prompt
                action = interaction.get('action', 'Interact')
                self.renderer.draw_interaction_prompt(screen, fonts, action, True)
        else:
            # No interaction available — show controls hint until dismissed
            if not getattr(game_state, 'controls_hint_dismissed', False):
                hint = "WASD: Move  |  E: Interact  |  B: Back  |  I: Inventory  |  Q: Quests  |  C: Character  |  H: Help"
                hint_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
                draw_centered_text(screen, hint, hint_font, LAYOUT_DIALOG_Y + 18, GRAY)
            else:
                self.renderer.draw_interaction_prompt(screen, fonts, None, False)

# === SCREEN INTERFACE FUNCTIONS ===

_broken_blade_nav_instance = None

def draw_broken_blade_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _broken_blade_nav_instance
    
    # TEMPORARY: Force recreation to pick up code changes
    #_broken_blade_nav_instance = None
    
    if _broken_blade_nav_instance is None:
        _broken_blade_nav_instance = BrokenBladeNav()
    
    # Handle input
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16  # Approximate milliseconds per frame (60 FPS)
        _broken_blade_nav_instance.update(dt, keys, game_state, controller)
    
    # Render
    return _broken_blade_nav_instance.render(surface, game_state, fonts, images, controller)