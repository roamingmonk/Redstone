"""
Hill Ruins Entrance Navigation
Scrollable tile-based exploration screen
"""

import pygame
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.hill_ruins_entrance_map import (
    HILL_RUINS_ENT_WIDTH,
    HILL_RUINS_ENT_HEIGHT,
    HILL_RUINS_ENT_SPAWN_X,
    HILL_RUINS_ENT_SPAWN_Y,
    get_tile_type,
    is_walkable,
    get_tile_color,
    get_transition_at_entrance,
    get_searchable_at_position,
    get_combat_trigger
)

class HillRuinsEntranceNav:
    """Navigation screen for hill ruins entrance exploration"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        config = {
            'map_width': HILL_RUINS_ENT_WIDTH,
            'map_height': HILL_RUINS_ENT_HEIGHT,
            'location_id': 'hill_ruins_entrance',
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
        self.current_transition = None
        self.current_searchable = None
        self.showing_message = False
        self.message_text = ""
        self.message_timer = 0
        
        self.graphics_manager = get_tile_graphics_manager()
    
    def update_player_position(self, game_state):
        """Initialize or restore player position"""
        if not hasattr(game_state, 'hill_ruins_entrance_x'):
            game_state.hill_ruins_entrance_x = HILL_RUINS_ENT_SPAWN_X
            game_state.hill_ruins_entrance_y = HILL_RUINS_ENT_SPAWN_Y
        
        self.renderer.update_camera(
            game_state.hill_ruins_entrance_x, 
            game_state.hill_ruins_entrance_y
        )
    
    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)
        
        # Check if we need to trigger loot check after dialogue
        if hasattr(game_state, 'trigger_loot_check') and game_state.trigger_loot_check:
            loot_table_id = game_state.trigger_loot_check
            game_state.trigger_loot_check = None  # Clear flag
            
            # Trigger loot check using existing system
            self._trigger_loot_check(loot_table_id, game_state, controller)
            return
        
        # Handle movement
        old_x = game_state.hill_ruins_entrance_x
        old_y = game_state.hill_ruins_entrance_y
        
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)
        
        # Check if player moved to new tile
        if new_x != old_x or new_y != old_y:
            
            # PRIORITY 1: Check for combat trigger on new tile
            combat_trigger = self.renderer.check_combat_trigger(new_x, new_y)
            
            # DEBUG: Show what's happening
            if combat_trigger:
                print(f"🎲 DEBUG: Combat trigger detected at ({new_x}, {new_y})")
                print(f"   Encounter: {combat_trigger.get('encounter_id')}, Chance: {combat_trigger.get('chance')}")
            
            if combat_trigger and combat_trigger.get('repeatable'):
                # Random encounter - check chance
                chance = combat_trigger.get('chance', 1.0)
                roll = random.random()
                print(f"🎲 DEBUG: Rolling for combat - rolled {roll:.2f}, need < {chance}")
                
                if roll < chance:
                    print(f"⚔️ Starting combat with {combat_trigger['encounter_id']}")
                    # Trigger combat using the standard pattern
                    if controller:
                        # Save current screen for return after combat
                        game_state.previous_screen = 'hill_ruins_entrance_nav'
                        # Set combat encounter
                        game_state.current_combat_encounter = combat_trigger['encounter_id']
                        print(f"🎯 Starting combat encounter: {combat_trigger['encounter_id']}")
                        
                        # Navigate to combat screen
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": "combat",
                            "source_screen": "hill_ruins_entrance_nav"
                        })
                    return  # Don't move yet, combat starting
            
            # No combat (or failed chance roll), update position
            game_state.hill_ruins_entrance_x = new_x
            game_state.hill_ruins_entrance_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Check for ENTER key interactions (higher priority when standing still)
        # Update transition cooldown
        self.renderer.update_transition_cooldown(dt)

        # Check for ENTER key interactions (debounced, with cooldown)
        if (self.renderer.check_enter_just_pressed(keys) and 
            not self.showing_message and 
            self.renderer.can_interact()):
            player_x = game_state.hill_ruins_entrance_x
            player_y = game_state.hill_ruins_entrance_y
            
            # INTERACTION PRIORITY ORDER:
            
            # Priority 1: Area transitions (doors, exits)
            transition_info = self.renderer.check_valid_entrance(player_x, player_y, 
                                                                self.renderer.player_direction)
            if transition_info and transition_info[0]:
                # Navigate to new area/screen
                if controller:
                    target = transition_info[0]['target_screen']
                    self.renderer.start_transition_cooldown()
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        'target_screen': target,
                        'source_screen': 'hill_ruins_entrance_nav'
                    })
                return
            
            # Priority 2: Searchable objects (examine, loot)
            searchable_info = self.renderer.check_searchable_object(player_x, player_y)
            if searchable_info:
                # Check if already searched
                flag_set = searchable_info.get('flag_set')
                if flag_set and getattr(game_state, flag_set, False):
                    self.show_temp_message("You've already searched here.")
                else:
                    # Trigger examination dialogue
                    examine_dialogue = searchable_info.get('examine_dialogue')
                    if examine_dialogue and controller:
                        # Extract npc_id from dialogue screen name
                        npc_id = examine_dialogue.split('_')[-1]
                           
                        # Store return screen using dialogue system's expected attribute name
                        return_screen_attr = f'{npc_id}_return_screen'
                        setattr(game_state, return_screen_attr, 'hill_ruins_entrance_nav')

                        # DEBUG: Verify it was set
                        print(f"🔍 DEBUG: Set {return_screen_attr} = {getattr(game_state, return_screen_attr, 'NOT SET')}")

                        # Store flag name for later (set after loot is taken)
                        game_state.pending_search_flag = flag_set
                        
                        # Navigate to dialogue screen
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": examine_dialogue,
                            "source_screen": 'hill_ruins_entrance_nav'
                        })
                
                return
        
        # Update temp message timer
        if self.showing_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.showing_message = False
    
    def show_temp_message(self, text):
        """Display temporary message to player"""
        self.showing_message = True
        self.message_text = text
        self.message_timer = 3000  # 3 seconds
    
    def _trigger_loot_check(self, loot_table_id, game_state, controller):
        """Trigger loot check and open combat loot overlay"""
        import json
        import os
        from utils.constants import LOCATION_DATA_PATH
        
        # Load location data to get loot tables
        location_file = os.path.join(LOCATION_DATA_PATH, "hill_ruins.json")
        if not os.path.exists(location_file):
            print(f"❌ Cannot find location file: {location_file}")
            return
        
        with open(location_file, 'r') as f:
            location_full_data = json.load(f)
            location_data = location_full_data.get('hill_ruins', location_full_data)
        
        # Get loot tables
        loot_tables = location_data.get('loot_tables', {})
        loot_table = loot_tables.get(loot_table_id)
        
        if not loot_table:
            print(f"❌ Loot table '{loot_table_id}' not found")
            return
        
        # Roll for items
        items_dict = {}  # item_id -> quantity
        for item_config in loot_table.get('items', []):
            item_id = item_config.get('item_id')
            quantity = item_config.get('quantity', 1)
            chance = item_config.get('chance', 1.0)
            
            # Roll against chance
            if random.random() <= chance:
                items_dict[item_id] = items_dict.get(item_id, 0) + quantity
                print(f"🎲 Found: {item_id} x{quantity}")

        # Convert to loot overlay format with item names
        items_list = []
        item_manager = getattr(game_state, 'item_manager', None)

        for item_id, quantity in items_dict.items():
            # Get display name from ItemManager
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
            # Set the flag even if nothing found
            if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
                setattr(game_state, game_state.pending_search_flag, True)
                game_state.pending_search_flag = None
            return
        
        # Prepare loot data for overlay
        loot_data = {
            'total_gold': 0,
            'items': items_list
        }
        
        game_state.combat_loot_data = loot_data
        game_state.pre_combat_location = 'hill_ruins_entrance_nav'
        
        # Store the search flag to set when overlay closes
        if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
            game_state.search_loot_flag = game_state.pending_search_flag
            game_state.pending_search_flag = None
        
        # Open loot overlay
        game_state.overlay_state.open_overlay("combat_loot")
        
        print(f"🔍 Search loot overlay opened: {len(items_list)} item types found")

    def render(self, surface, fonts, images, game_state):
        """Render the entrance navigation screen"""
        surface.fill(BLACK)
        
        # Get player position for rendering
        player_x = game_state.hill_ruins_entrance_x
        player_y = game_state.hill_ruins_entrance_y
        
        # Draw map tiles
        self.renderer.draw_map(surface, fonts, player_x, player_y)
        
        # Draw player sprite
        self.renderer.draw_player(surface, player_x, player_y)
        
        # Draw NPCs (if any)
        # TODO: NPC rendering when needed
        
        # Draw party status panel (right side)
        draw_party_status_panel(surface, game_state, fonts)
        
        # Draw location title at top
        title_text = "THE RUINS ON THE HILL - ENTRANCE"
        draw_centered_text(surface, title_text, fonts['fantasy_medium'], 
                          20, YELLOW, 880)
        
        # Draw dialog/interaction area at bottom
        #=== DIALOG ZONE (FULL SCREEN WIDTH) ===
        dialog_y = LAYOUT_DIALOG_Y
        dialog_height = LAYOUT_DIALOG_HEIGHT
        dialog_margin = 0
        draw_border(surface, dialog_margin, dialog_y, 1024 - (dialog_margin * 2), dialog_height) 
        
        # Draw interaction prompts
        transition = self.renderer.check_valid_entrance(player_x, player_y, 
                                                        self.renderer.player_direction)
        if transition and transition[0]:
            prompt = f"Press ENTER to {transition[0]['action']}"
            draw_centered_text(surface, prompt, fonts['fantasy_small'],
                             LAYOUT_DIALOG_Y + 15, YELLOW, 1024)
        
        searchable = self.renderer.check_searchable_object(player_x, player_y)
        if searchable:
            # Check if already searched
            flag_set = searchable.get('flag_set')
            if flag_set and getattr(game_state, flag_set, False):
                prompt = f"{searchable['name']} (already searched)"
                draw_centered_text(surface, prompt, fonts['fantasy_small'],
                                 LAYOUT_DIALOG_Y + 15, WHITE, 1024)
            else:
                prompt = f"Press ENTER to examine {searchable['name']}"
                draw_centered_text(surface, prompt, fonts['fantasy_small'],
                                 LAYOUT_DIALOG_Y + 15, YELLOW, 1024)
        
        # Show temp message if any
        if self.showing_message:
            draw_centered_text(surface, self.message_text, 
                             fonts['fantasy_medium'], LAYOUT_DIALOG_Y + 50, WHITE, 1024)
        
        # Draw debug info (optional, can be toggled)
        if hasattr(game_state, 'show_debug') and game_state.show_debug:
            debug_text = f"Pos: ({player_x}, {player_y}) Facing: {self.renderer.player_direction}"
            draw_centered_text(surface, debug_text, fonts['fantasy_small'],
                             40, WHITE, 1024)


# ScreenManager registration function
_hill_ruins_entrance_nav_instance = None

def draw_hill_ruins_entrance_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _hill_ruins_entrance_nav_instance
    
    if _hill_ruins_entrance_nav_instance is None:
        _hill_ruins_entrance_nav_instance = HillRuinsEntranceNav()
    
    # Handle input
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _hill_ruins_entrance_nav_instance.update(dt, keys, game_state, controller)
    
    # Render
    return _hill_ruins_entrance_nav_instance.render(surface, fonts, images, game_state)