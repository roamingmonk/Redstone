"""
Dungeon Level 2 Navigation - Ancient Lower Ruins
Second level of the cult's sanctum - deeper and more dangerous
"""

import pygame
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import (BLACK, WHITE, YELLOW, RED, LAYOUT_DIALOG_Y, 
                             LAYOUT_DIALOG_HEIGHT, TILESETS_PATH)
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from utils.tiled_loader import (
    load_tiled_map_with_names,
    get_tile_type,
    is_walkable_tile
)

from data.maps.dungeon_tiles import (
    DUNGEON_TILE_MAP,
    DUNGEON_WALKABLE
)
from data.maps.dungeon_level_2_map import (
    DUNGEON_L2_WIDTH,
    DUNGEON_L2_HEIGHT,
    DUNGEON_L2_SPAWN_X,
    DUNGEON_L2_SPAWN_Y,
    DUNGEON_L2_SPAWN_POINTS,
    get_transition_at_entrance,
    get_searchable_at_position,
    get_combat_trigger,
    get_environmental_hazard
)
from data.maps.dungeon_level_1_map import DUNGEON_L1_SPAWN_POINTS
from data.maps.dungeon_level_3_map import DUNGEON_L3_SPAWN_POINTS

class DungeonLevel2Nav:
    """Navigation screen for dungeon level 2"""

    def __init__(self):
        # Load tileset from grid (shared dungeon tileset)
        graphics_mgr = get_tile_graphics_manager()
        graphics_mgr.load_tileset_from_grid(
            'dungeon',                   # PNG filename (without extension)
            DUNGEON_TILE_MAP,            # Tile mapping
            tile_size=32,                # Source tile size in PNG
            columns=8                    # Number of columns in dungeon.png
        )
        
        # Load Tiled map
        try:
            self.tilemap = load_tiled_map_with_names(
                'dungeon_level_2_tiles',  # TMJ filename (without extension)
                'dungeon',
                DUNGEON_TILE_MAP,
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
                            if tile_index in DUNGEON_TILE_MAP:
                                tile_name = DUNGEON_TILE_MAP[tile_index]
                            else:
                                tile_name = None  # Unknown tiles become None
                            named_row.append(tile_name)
                        named_layer.append(named_row)
                    self.tilemap['layers'][layer_name] = named_layer
                print(f"✅ Converted {len(self.tilemap['layers'])} layers to use tile names")
            
            # Store layer names in render order
            self.layer_names = ['Floor', 'Walls', 'Details']

        except FileNotFoundError as e:
            print(f"❌ Tiled map file not found: {e}")
            # Fallback to old system
            self.tilemap = {
                'width': DUNGEON_L2_WIDTH,
                'height': DUNGEON_L2_HEIGHT,
                'tile_grid': None
            }
            self.layer_names = None
        
        config = {
            'tile_size': 64,
            'player_sprite_size': 64,
            'map_width': self.tilemap['width'],
            'map_height': self.tilemap['height'],
            'location_id': 'dungeon_level_2',
            'tilemap': self.tilemap,
            'layer_names': self.layer_names,
            'map_functions': {
                'get_tile_type': lambda x, y: get_tile_type(x, y, self.tilemap.get('tile_grid')),
                'is_walkable': self._is_walkable_multi_layer,
                'get_tile_color': None,  # Using graphics now, not colors
                'get_building_info': get_transition_at_entrance,
                'get_searchable_info': get_searchable_at_position,
                'get_combat_trigger': get_combat_trigger
            },
            'spawn_position': (DUNGEON_L2_SPAWN_X, DUNGEON_L2_SPAWN_Y),
            'spawn_direction': 'down'
        }

        self.renderer = NavigationRenderer(config)
        self.showing_message = False
        self.message_text = ""
        self.message_timer = 0
        self.is_hazard_message = False
        self.graphics_manager = get_tile_graphics_manager()

    def get_tile_from_layer(self, x, y, layer_name):
        """Get tile type from a specific layer"""
        if layer_name in self.tilemap.get('layers', {}):
            layer_grid = self.tilemap['layers'][layer_name]
            return get_tile_type(x, y, layer_grid)
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
            if tile_name not in DUNGEON_WALKABLE:
                return False
        
        # All layers are either empty or walkable
        return True

    def update_player_position(self, game_state):
        """Initialize or restore player position"""
        # Check for spawn override (from transitions)
        if hasattr(game_state, 'dungeon_l2_spawn_override_x'):
            game_state.dungeon_l2_x = game_state.dungeon_l2_spawn_override_x
            game_state.dungeon_l2_y = game_state.dungeon_l2_spawn_override_y
            delattr(game_state, 'dungeon_l2_spawn_override_x')
            delattr(game_state, 'dungeon_l2_spawn_override_y')
            print(f"✅ Level 2 spawn override: ({game_state.dungeon_l2_x}, {game_state.dungeon_l2_y})")
        elif not hasattr(game_state, 'dungeon_l2_x'):
            game_state.dungeon_l2_x = DUNGEON_L2_SPAWN_X
            game_state.dungeon_l2_y = DUNGEON_L2_SPAWN_Y
            print("🏛️ Entered Dungeon Level 2")

        self.renderer.update_camera(game_state.dungeon_l2_x, game_state.dungeon_l2_y)

    def handle_environmental_hazard(self, hazard_data, game_state, controller):
        """Handle environmental hazard triggers (weak floors, etc.)"""
        hazard_type = hazard_data.get('hazard_type')
        damage = hazard_data.get('damage', '1d6')
        message = hazard_data.get('message', 'Environmental hazard!')
        
        # Show message with hazard flag
        self.show_temp_message(message, is_hazard=True)
        
        # Apply damage to party (simplified - could be more sophisticated)
        print(f"⚠️ Environmental hazard: {hazard_type}, damage: {damage}")
        
        # Could trigger event for damage application
        if controller and hasattr(controller, 'event_manager'):
            controller.event_manager.emit("ENVIRONMENTAL_DAMAGE", {
                "damage": damage,
                "type": hazard_type
            })

    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)

        # Check for loot trigger - MUST BE FIRST
        if hasattr(game_state, 'trigger_loot_check') and game_state.trigger_loot_check:
            loot_table_id = game_state.trigger_loot_check
            print(f"💰 Level 2 Nav: Detected loot trigger: {loot_table_id}")
            game_state.trigger_loot_check = None
            self._trigger_loot_check(loot_table_id, game_state, controller)
            return

        # Handle movement
        old_x = game_state.dungeon_l2_x
        old_y = game_state.dungeon_l2_y
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)

        if new_x != old_x or new_y != old_y:
            # PRIORITY 1: Check for combat trigger
            combat_trigger = self.renderer.check_combat_trigger(new_x, new_y)

            if combat_trigger:
                # Check if already completed
                completion_flag = combat_trigger.get('completion_flag')
                if completion_flag and getattr(game_state, completion_flag, False):
                    # Already cleared, allow movement
                    game_state.dungeon_l2_x = new_x
                    game_state.dungeon_l2_y = new_y
                    self.renderer.update_camera(new_x, new_y)
                    return

                # Trigger combat
                if controller:
                    game_state.previous_screen = 'dungeon_level_2_nav'
                    game_state.pre_combat_location = 'dungeon_level_2_nav'
                    game_state.current_combat_encounter = combat_trigger['encounter_id']
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        "target_screen": "combat",
                        "source_screen": "dungeon_level_2_nav"
                    })
                return

            # PRIORITY 2: Check for environmental hazards
            hazard = get_environmental_hazard(new_x, new_y)
            if hazard:
                # Check if already triggered this session
                hazard_flag = f"hazard_{new_x}_{new_y}_triggered"
                if not getattr(game_state, hazard_flag, False):
                    # Trigger hazard
                    self.handle_environmental_hazard(hazard, game_state, controller)
                    setattr(game_state, hazard_flag, True)

            # PRIORITY 3: Update position
            game_state.dungeon_l2_x = new_x
            game_state.dungeon_l2_y = new_y
            self.renderer.update_camera(new_x, new_y)

        # Update transition cooldown
        self.renderer.update_transition_cooldown(dt)

        # Check for ENTER key interactions
        if (self.renderer.check_enter_just_pressed(keys) and 
            not self.showing_message and 
            self.renderer.can_interact()):
            
            player_x = game_state.dungeon_l2_x
            player_y = game_state.dungeon_l2_y

            # Priority 1: Transitions
            transition_info = self.renderer.check_valid_entrance(player_x, player_y, self.renderer.player_direction)
            if transition_info and transition_info[0]:
                if controller:
                    target = transition_info[0]['target_screen']
                    
                    # Set spawn position for destination level
                    if target == 'dungeon_level_1_nav':
                        spawn_point = DUNGEON_L1_SPAWN_POINTS.get('from_level_2')
                        if spawn_point:
                            game_state.dungeon_l1_spawn_override_x = spawn_point[0]
                            game_state.dungeon_l1_spawn_override_y = spawn_point[1]
                    elif target == 'dungeon_level_3_nav':
                        spawn_point = DUNGEON_L3_SPAWN_POINTS.get('from_level_2')
                        if spawn_point:
                            game_state.dungeon_l3_spawn_override_x = spawn_point[0]
                            game_state.dungeon_l3_spawn_override_y = spawn_point[1]
                    
                    self.renderer.start_transition_cooldown()
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        'target_screen': target,
                        'source_screen': 'dungeon_level_2_nav'
                    })
                return

            # Priority 2: Searchables
            searchable_info = self.renderer.check_searchable_object(player_x, player_y)
            if searchable_info:
                flag_set = searchable_info.get('flag_set')
                if flag_set and getattr(game_state, flag_set, False):
                    self.show_temp_message("You've already searched here.")
                else:
                    examine_dialogue = searchable_info.get('examine_dialogue')
                    if examine_dialogue and controller:
                        npc_id = examine_dialogue.split('_')[-1]
                        return_screen_attr = f'{npc_id}_return_screen'
                        setattr(game_state, return_screen_attr, 'dungeon_level_2_nav')
                        game_state.pending_search_flag = flag_set

                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": examine_dialogue,
                            "source_screen": 'dungeon_level_2_nav'
                        })
                return

        # Update message timer
        if self.showing_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.showing_message = False
                self.is_hazard_message = False

    def show_temp_message(self, text, is_hazard=False):
        self.showing_message = True
        self.message_text = text
        self.message_timer = 3000
        self.is_hazard_message = is_hazard

    def _trigger_loot_check(self, loot_table_id, game_state, controller):
        """Trigger loot check using hill ruins loot tables"""
        import json
        import os
        from utils.constants import LOCATION_DATA_PATH

        print(f"💰 _trigger_loot_check called with: {loot_table_id}")

        location_file = os.path.join(LOCATION_DATA_PATH, "hill_ruins.json")
        if not os.path.exists(location_file):
            print(f"❌ Loot file not found: {location_file}")
            return

        with open(location_file, 'r') as f:
            location_full_data = json.load(f)
            location_data = location_full_data.get('hill_ruins', location_full_data)

        loot_tables = location_data.get('loot_tables', {})
        loot_table = loot_tables.get(loot_table_id)

        if not loot_table:
            print(f"❌ Loot table '{loot_table_id}' not found in hill_ruins.json")
            return

        print(f"✅ Found loot table: {loot_table_id}")

        items_dict = {}
        for item_config in loot_table.get('items', []):
            item_id = item_config.get('item_id')
            quantity = item_config.get('quantity', 1)
            chance = item_config.get('chance', 1.0)

            if random.random() <= chance:
                items_dict[item_id] = items_dict.get(item_id, 0) + quantity

        items_list = []
        item_manager = getattr(game_state, 'item_manager', None)

        for item_id, quantity in items_dict.items():
            if item_manager and hasattr(item_manager, 'get_display_name'):
                display_name = item_manager.get_display_name(item_id)
            else:
                display_name = item_id.replace('_', ' ').title()

            items_list.append({
                'item_id': item_id,
                'quantity': quantity,
                'name': display_name
            })

        if not items_list:
            print(f"💰 No items rolled from loot table")
            self.show_temp_message("You found nothing of value.")
            if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
                setattr(game_state, game_state.pending_search_flag, True)
                game_state.pending_search_flag = None
            return

        print(f"💰 Opening loot overlay with {len(items_list)} items")
        loot_data = {'total_gold': 0, 'items': items_list}
        game_state.combat_loot_data = loot_data
        game_state.pre_combat_location = 'dungeon_level_2_nav'

        if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
            game_state.search_loot_flag = game_state.pending_search_flag
            game_state.pending_search_flag = None

        game_state.overlay_state.open_overlay("combat_loot")

    def render(self, surface, fonts, images, game_state):
        """Render the navigation screen"""
        surface.fill(BLACK)

        player_x = game_state.dungeon_l2_x
        player_y = game_state.dungeon_l2_y

        # Draw map tiles (multi-layer)
        self.renderer.draw_map(surface, fonts, player_x, player_y)
        
        # Draw player sprite
        self.renderer.draw_player(surface, player_x, player_y)
        
        # Draw party status panel
        draw_party_status_panel(surface, game_state, fonts)

        # Draw title
        title_text = "DUNGEON - LEVEL 2"
        draw_centered_text(surface, title_text, fonts['fantasy_medium'], 20, YELLOW, 880)

        # Dialog zone
        dialog_y = LAYOUT_DIALOG_Y
        dialog_height = LAYOUT_DIALOG_HEIGHT
        dialog_margin = 0
        draw_border(surface, dialog_margin, dialog_y, 1024 - (dialog_margin * 2), dialog_height)

        # Draw interaction prompts
        transition = self.renderer.check_valid_entrance(player_x, player_y, self.renderer.player_direction)
        if transition and transition[0]:
            prompt = f"Press ENTER to {transition[0]['action']}"
            draw_centered_text(surface, prompt, fonts['fantasy_small'], LAYOUT_DIALOG_Y + 15, YELLOW, 1024)

        searchable = self.renderer.check_searchable_object(player_x, player_y)
        if searchable:
            flag_set = searchable.get('flag_set')
            if flag_set and getattr(game_state, flag_set, False):
                prompt = f"{searchable['name']} (already searched)"
                draw_centered_text(surface, prompt, fonts['fantasy_small'], LAYOUT_DIALOG_Y + 15, WHITE, 1024)
            else:
                prompt = f"Press ENTER to examine {searchable['name']}"
                draw_centered_text(surface, prompt, fonts['fantasy_small'], LAYOUT_DIALOG_Y + 15, YELLOW, 1024)

        # Show messages - different rendering based on type
        if self.showing_message:
            if self.is_hazard_message:
                # HAZARD OVERLAY: Black box with red border at center of screen
                msg_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
                msg_surface = msg_font.render(self.message_text, True, WHITE)
                msg_rect = msg_surface.get_rect(center=(512, 400))
                
                # Draw background box
                padding = 10
                bg_rect = pygame.Rect(
                    msg_rect.x - padding,
                    msg_rect.y - padding,
                    msg_rect.width + padding * 2,
                    msg_rect.height + padding * 2
                )
                pygame.draw.rect(surface, BLACK, bg_rect)
                pygame.draw.rect(surface, RED, bg_rect, 2)
                
                surface.blit(msg_surface, msg_rect)
            else:
                # STANDARD MESSAGE: Dialog zone at bottom
                draw_centered_text(surface, self.message_text, fonts['fantasy_medium'], LAYOUT_DIALOG_Y + 50, WHITE, 1024)


# ScreenManager registration function
_dungeon_level_2_instance = None

def draw_dungeon_level_2_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _dungeon_level_2_instance

    if _dungeon_level_2_instance is None:
        _dungeon_level_2_instance = DungeonLevel2Nav()

    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _dungeon_level_2_instance.update(dt, keys, game_state, controller)

    return _dungeon_level_2_instance.render(surface, fonts, images, game_state)
