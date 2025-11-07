"""
Red Hollow Mine - Level 3 Navigation
Deep chamber with ritual site and secret tunnel discovery
"""

import pygame
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, CYAN, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.red_hollow_mine_level_3_map import (
    MINE_L3_WIDTH,
    MINE_L3_HEIGHT,
    MINE_L3_SPAWN_X,
    MINE_L3_SPAWN_Y,
    MINE_L3_SPAWN_POINTS,
    get_tile_type,
    is_walkable,
    get_tile_color,
    get_transition_info,
    get_searchable_at_position,
    get_combat_trigger
)
from data.maps.red_hollow_mine_pre_entrance_map import MINE_PRE_SPAWN_POINTS 
from data.maps.red_hollow_mine_level_2_map import MINE_L2_SPAWN_POINTS

class RedHollowMineLevel3Nav:
    """Navigation screen for mine level 3 deep chamber"""

    def __init__(self):
        config = {
            'map_width': MINE_L3_WIDTH,
            'map_height': MINE_L3_HEIGHT,
            'location_id': 'red_hollow_mine_level_3',
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_tile_color': get_tile_color,
                'get_building_info': get_transition_info,
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
        if hasattr(game_state, 'mine_l3_spawn_override_x'):
            game_state.mine_l3_x = game_state.mine_l3_spawn_override_x
            game_state.mine_l3_y = game_state.mine_l3_spawn_override_y
            delattr(game_state, 'mine_l3_spawn_override_x')
            delattr(game_state, 'mine_l3_spawn_override_y')
            print(f"✅ Level 3 spawn override: ({game_state.mine_l3_x}, {game_state.mine_l3_y})")
        elif not hasattr(game_state, 'mine_l3_x'):
            game_state.mine_l3_x = MINE_L3_SPAWN_X
            game_state.mine_l3_y = MINE_L3_SPAWN_Y

        self.renderer.update_camera(game_state.mine_l3_x, game_state.mine_l3_y)

    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)

        # Check for loot trigger
        if hasattr(game_state, 'trigger_loot_check') and game_state.trigger_loot_check:
            loot_table_id = game_state.trigger_loot_check
            game_state.trigger_loot_check = None
            self._trigger_loot_check(loot_table_id, game_state, controller)
            return

        # Handle movement
        old_x = game_state.mine_l3_x
        old_y = game_state.mine_l3_y
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)

        if new_x != old_x or new_y != old_y:
            # No combat triggers on level 3 (exploration focus)
            game_state.mine_l3_x = new_x
            game_state.mine_l3_y = new_y
            self.renderer.update_camera(new_x, new_y)

        # Check for ENTER key interactions
        if keys[pygame.K_RETURN] and not self.showing_message:
            player_x = game_state.mine_l3_x
            player_y = game_state.mine_l3_y

            # Priority 1: Area transitions (ladder, shaft)
            transition_info = self.renderer.check_valid_entrance(player_x, player_y, 
                                                                self.renderer.player_direction)
            if transition_info and transition_info[0]:
                transition_data = transition_info[0]
                
                # Check if both critical discoveries are complete
                examined_ritual = getattr(game_state, 'examined_ritual_chamber', False)
                searched_ore = getattr(game_state, 'searched_deep_ore_chamber', False)
                
                can_transition = False
                blocked_message = ""
                
                if examined_ritual and searched_ore:
                    # Both complete - allow exit and mark mine as complete
                    can_transition = True
                    if not getattr(game_state, 'red_hollow_mine_complete', False):
                        game_state.red_hollow_mine_complete = True
                        print("✅ Red Hollow Mine fully explored!")
                elif not examined_ritual and not searched_ore:
                    # Neither searched - general message
                    blocked_message = "You should investigate this chamber more thoroughly. The ritual site and ore deposits await."
                elif not examined_ritual:
                    # Missing ritual chamber
                    blocked_message = "You should investigate the ancient ritual site before leaving. The symbols and implements hold important clues."
                elif not searched_ore:
                    # Missing ore deposits
                    blocked_message = "You should collect samples from the massive ore deposits before leaving. They're crucial evidence."
                
                if can_transition and controller:
                    target = transition_data['target_screen']
                    
                    # Set spawn position for destination level using named spawn points
                    if target == 'red_hollow_mine_pre_entrance_nav':
                        spawn_point = MINE_PRE_SPAWN_POINTS['from_shaft_level_3']
                        game_state.mine_pre_spawn_override_x = spawn_point[0]
                        game_state.mine_pre_spawn_override_y = spawn_point[1]
                        print("🚁 Taking shaft to surface")
                    elif target == 'red_hollow_mine_level_2_nav':
                        spawn_point = MINE_L2_SPAWN_POINTS['from_level_3']
                        game_state.mine_l2_spawn_override_x = spawn_point[0]
                        game_state.mine_l2_spawn_override_y = spawn_point[1]
                    
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        'target_screen': target,
                        'source_screen': 'red_hollow_mine_level_3_nav'
                    })
                elif not can_transition:
                    self.show_temp_message(blocked_message)
                return

            # Priority 2: Searchables
            searchable_info = self.renderer.check_searchable_object(player_x, player_y)
            if searchable_info:
                flag_set = searchable_info.get('flag_set')
                if flag_set and getattr(game_state, flag_set, False):
                    self.show_temp_message("You've already examined this.")
                else:
                    examine_dialogue = searchable_info.get('examine_dialogue')
                    if examine_dialogue and controller:
                        npc_id = examine_dialogue.split('_')[-1]
                        return_screen_attr = f'{npc_id}_return_screen'
                        setattr(game_state, return_screen_attr, 'red_hollow_mine_level_3_nav')
                        game_state.pending_search_flag = flag_set

                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": examine_dialogue,
                            "source_screen": 'red_hollow_mine_level_3_nav'
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
        """Trigger loot check using mine loot tables"""
        import json
        import os
        from utils.constants import LOCATION_DATA_PATH

        location_file = os.path.join(LOCATION_DATA_PATH, "red_hollow_mine.json")
        if not os.path.exists(location_file):
            return

        with open(location_file, 'r') as f:
            location_full_data = json.load(f)
            location_data = location_full_data.get('red_hollow_mine', location_full_data)

        loot_tables = location_data.get('loot_tables', {})
        loot_table = loot_tables.get(loot_table_id)

        if not loot_table:
            return

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
            self.show_temp_message("You found nothing of value.")
            if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
                setattr(game_state, game_state.pending_search_flag, True)
                game_state.pending_search_flag = None
            return

        loot_data = {'total_gold': 0, 'items': items_list}
        game_state.combat_loot_data = loot_data
        game_state.pre_combat_location = 'red_hollow_mine_level_3_nav'

        if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
            game_state.search_loot_flag = game_state.pending_search_flag
            game_state.pending_search_flag = None

        game_state.overlay_state.open_overlay("combat_loot")

    def render(self, surface, fonts, images, game_state):
        """Render the navigation screen"""
        surface.fill(BLACK)

        player_x = game_state.mine_l3_x
        player_y = game_state.mine_l3_y

        self.renderer.draw_map(surface, fonts, player_x, player_y)
        self.renderer.draw_player(surface, player_x, player_y)
        draw_party_status_panel(surface, game_state, fonts)

        title_text = "RED HOLLOW MINE - DEEP CHAMBER"
        draw_centered_text(surface, title_text, fonts['fantasy_medium'], 20, CYAN, 880)

        draw_border(surface, 5, LAYOUT_DIALOG_Y, 876, LAYOUT_DIALOG_HEIGHT)

        transition = self.renderer.check_valid_entrance(player_x, player_y, self.renderer.player_direction)
        if transition and transition[0]:
            prompt = f"Press ENTER to {transition[0]['action']}"
            draw_centered_text(surface, prompt, fonts['fantasy_small'], LAYOUT_DIALOG_Y + 15, YELLOW, 880)

        searchable = self.renderer.check_searchable_object(player_x, player_y)
        if searchable:
            flag_set = searchable.get('flag_set')
            if flag_set and getattr(game_state, flag_set, False):
                prompt = f"{searchable['name']} (already examined)"
                draw_centered_text(surface, prompt, fonts['fantasy_small'], LAYOUT_DIALOG_Y + 15, WHITE, 880)
            else:
                prompt = f"Press ENTER to examine {searchable['name']}"
                draw_centered_text(surface, prompt, fonts['fantasy_small'], LAYOUT_DIALOG_Y + 15, YELLOW, 880)

        if self.showing_message:
            draw_centered_text(surface, self.message_text, fonts['fantasy_medium'], LAYOUT_DIALOG_Y + 50, WHITE, 880)


# ScreenManager registration function
_mine_level_3_instance = None

def draw_red_hollow_mine_level_3_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _mine_level_3_instance

    if _mine_level_3_instance is None:
        _mine_level_3_instance = RedHollowMineLevel3Nav()

    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _mine_level_3_instance.update(dt, keys, game_state, controller)

    return _mine_level_3_instance.render(surface, fonts, images, game_state)