"""
Dungeon Level 4 Navigation - Cult Sanctum Upper
Active headquarters of the cult with living quarters and evidence of Marcus's leadership
"""

import pygame
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, RED, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.dungeon_level_4_map import (
    DUNGEON_L4_WIDTH,
    DUNGEON_L4_HEIGHT,
    DUNGEON_L4_SPAWN_X,
    DUNGEON_L4_SPAWN_Y,
    DUNGEON_L4_SPAWN_POINTS,
    get_tile_type,
    is_walkable,
    get_tile_color,
    get_transition_at_entrance,
    get_searchable_at_position,
    get_combat_trigger
)

from data.maps.dungeon_level_3_map import DUNGEON_L3_SPAWN_POINTS
from data.maps.dungeon_level_5_map import DUNGEON_L5_SPAWN_POINTS

class DungeonLevel4Nav:
    """Navigation screen for dungeon level 4 - Cult Sanctum Upper"""

    def __init__(self):
        config = {
            'player_sprite_size': 64,
            'map_width': DUNGEON_L4_WIDTH,
            'map_height': DUNGEON_L4_HEIGHT,
            'location_id': 'dungeon_level_4',
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_tile_color': get_tile_color,
                'get_building_info': get_transition_at_entrance,
                'get_searchable_info': get_searchable_at_position,
                'get_combat_trigger': get_combat_trigger
            }
        }

        self.renderer = NavigationRenderer(config)
        self.showing_message = False
        self.message_text = ""
        self.message_timer = 0
        self.graphics_manager = get_tile_graphics_manager()

    def update_player_position(self, game_state):
        """Initialize or restore player position"""
        # Check for spawn override (from transitions)
        if hasattr(game_state, 'dungeon_l4_spawn_override_x'):
            game_state.dungeon_l4_x = game_state.dungeon_l4_spawn_override_x
            game_state.dungeon_l4_y = game_state.dungeon_l4_spawn_override_y
            delattr(game_state, 'dungeon_l4_spawn_override_x')
            delattr(game_state, 'dungeon_l4_spawn_override_y')
            print(f"✅ Level 4 spawn override: ({game_state.dungeon_l4_x}, {game_state.dungeon_l4_y})")
        elif not hasattr(game_state, 'dungeon_l4_x'):
            game_state.dungeon_l4_x = DUNGEON_L4_SPAWN_X
            game_state.dungeon_l4_y = DUNGEON_L4_SPAWN_Y
            print("🏛️ Entered Cult Sanctum Upper - Level 4")

        self.renderer.update_camera(game_state.dungeon_l4_x, game_state.dungeon_l4_y)

    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)

        # Check for loot trigger - MUST BE FIRST
        if hasattr(game_state, 'trigger_loot_check') and game_state.trigger_loot_check:
            loot_table_id = game_state.trigger_loot_check
            print(f"💰 Level 4 Nav: Detected loot trigger: {loot_table_id}")
            game_state.trigger_loot_check = None
            self._trigger_loot_check(loot_table_id, game_state, controller)
            return

        # Handle movement
        old_x = game_state.dungeon_l4_x
        old_y = game_state.dungeon_l4_y
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)

        if new_x != old_x or new_y != old_y:
            # Check for combat trigger
            combat_trigger = self.renderer.check_combat_trigger(new_x, new_y)

            if combat_trigger:
                # Check if already completed
                completion_flag = combat_trigger.get('completion_flag')
                if completion_flag and getattr(game_state, completion_flag, False):
                    # Already cleared, allow movement
                    game_state.dungeon_l4_x = new_x
                    game_state.dungeon_l4_y = new_y
                    self.renderer.update_camera(new_x, new_y)
                    return

                # Trigger combat
                if controller:
                    game_state.previous_screen = 'dungeon_level_4_nav'
                    game_state.pre_combat_location = 'dungeon_level_4_nav'
                    game_state.current_combat_encounter = combat_trigger['encounter_id']
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        "target_screen": "combat",
                        "source_screen": "dungeon_level_4_nav"
                    })
                return

            game_state.dungeon_l4_x = new_x
            game_state.dungeon_l4_y = new_y
            self.renderer.update_camera(new_x, new_y)

        # Update transition cooldown
        self.renderer.update_transition_cooldown(dt)

        # Check for ENTER key interactions
        if (self.renderer.check_enter_just_pressed(keys) and 
            not self.showing_message and 
            self.renderer.can_interact()):
            
            player_x = game_state.dungeon_l4_x
            player_y = game_state.dungeon_l4_y

            # Priority 1: Transitions
            transition_info = self.renderer.check_valid_entrance(player_x, player_y, self.renderer.player_direction)
            if transition_info and transition_info[0]:
                if controller:
                    target = transition_info[0]['target_screen']
                    
                    # Set spawn position for destination level
                    if target == 'dungeon_level_3_nav':
                        spawn_point = DUNGEON_L4_SPAWN_POINTS.get('from_level_3')
                        if spawn_point:
                            game_state.dungeon_l3_spawn_override_x = spawn_point[0]
                            game_state.dungeon_l3_spawn_override_y = spawn_point[1]
                    elif target == 'dungeon_level_5_nav':
                        spawn_point = DUNGEON_L5_SPAWN_POINTS.get('from_level_4')
                        if spawn_point:
                            game_state.dungeon_l5_spawn_override_x = spawn_point[0]
                            game_state.dungeon_l5_spawn_override_y = spawn_point[1]
                    
                    self.renderer.start_transition_cooldown()
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        'target_screen': target,
                        'source_screen': 'dungeon_level_4_nav'
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
                        setattr(game_state, return_screen_attr, 'dungeon_level_4_nav')
                        game_state.pending_search_flag = flag_set

                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": examine_dialogue,
                            "source_screen": 'dungeon_level_4_nav'
                        })
                return

        # Update message timer
        if self.showing_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.showing_message = False

    def show_temp_message(self, text):
        self.showing_message = True
        self.message_text = text
        self.message_timer = 3000

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
        game_state.pre_combat_location = 'dungeon_level_4_nav'

        if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
            game_state.search_loot_flag = game_state.pending_search_flag
            game_state.pending_search_flag = None

        game_state.overlay_state.open_overlay("combat_loot")

    def render(self, surface, fonts, images, game_state):
        """Render the navigation screen"""
        surface.fill(BLACK)

        player_x = game_state.dungeon_l4_x
        player_y = game_state.dungeon_l4_y

        self.renderer.draw_map(surface, fonts, player_x, player_y)
        self.renderer.draw_player(surface, player_x, player_y)
        draw_party_status_panel(surface, game_state, fonts)

        title_text = "DUNGEON - LEVEL 4: CULT SANCTUM"
        draw_centered_text(surface, title_text, fonts['fantasy_medium'], 20, YELLOW, 880)

        # Cult warning subtitle (similar to Level 3)
        subtitle_text = "The heart of the cult's operations..."
        draw_centered_text(surface, subtitle_text, fonts['fantasy_small'], 45, RED, 880)

        # Dialog zone
        dialog_y = LAYOUT_DIALOG_Y
        dialog_height = LAYOUT_DIALOG_HEIGHT
        dialog_margin = 0
        draw_border(surface, dialog_margin, dialog_y, 1024 - (dialog_margin * 2), dialog_height)

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

        if self.showing_message:
            draw_centered_text(surface, self.message_text, fonts['fantasy_medium'], LAYOUT_DIALOG_Y + 50, WHITE, 1024)


# ScreenManager registration function
_dungeon_level_4_instance = None

def draw_dungeon_level_4_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _dungeon_level_4_instance

    if _dungeon_level_4_instance is None:
        _dungeon_level_4_instance = DungeonLevel4Nav()

    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _dungeon_level_4_instance.update(dt, keys, game_state, controller)

    return _dungeon_level_4_instance.render(surface, fonts, images, game_state)