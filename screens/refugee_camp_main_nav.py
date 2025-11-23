"""
Refugee Camp Main Area Navigation
Scrollable tile-based exploration screen
"""

import pygame
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT, TILESETS_PATH
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.refugee_camp_main_map import (
    #REFUGEE_CAMP_WIDTH,
    #REFUGEE_CAMP_HEIGHT,
    REFUGEE_CAMP_SPAWN_X,
    REFUGEE_CAMP_SPAWN_Y,
    get_tile_type,
    #is_walkable,
    #get_tile_color,
    get_transition_info,
    get_searchable_at_position,
    get_combat_trigger
)
from utils.tiled_loader import (load_tiled_map_with_names,get_tile_type,is_walkable_tile)
from data.maps.refugee_camp_tiles import (REFUGEE_CAMP_TILE_MAP, REFUGEE_CAMP_WALKABLE)


class RefugeeCampMainNav:
    """Navigation screen for refugee camp main area exploration"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        graphics_mgr = get_tile_graphics_manager()
        graphics_mgr.load_tileset_from_grid ('refugee_camp', REFUGEE_CAMP_TILE_MAP, tile_size=32, columns=7)
        
         # Load Tiled map
        try: 
            self.tilemap = load_tiled_map_with_names('refugee_camp_map','refugee_camp', REFUGEE_CAMP_TILE_MAP,TILESETS_PATH)

            print(f"✅ Tilemap loaded: {self.tilemap['width']}x{self.tilemap['height']}")
        except FileNotFoundError as e:
            print(f"❌ Tiled map file not found: {e}")
            print(f"   Using fallback to old ASCII system")
            # Fallback to old system
            from data.maps.refugee_camp_main_map import REFUGEE_CAMP_WIDTH, REFUGEE_CAMP_HEIGHT
            self.tilemap = {
                'width': REFUGEE_CAMP_WIDTH,
                'height': REFUGEE_CAMP_HEIGHT,
                'tile_grid': None  # Will use old system
            }
        except Exception as e:
            print(f"❌ Error loading Tiled map: {e}")
            # Fallback to old system
            from data.maps.refugee_camp_main_map import REFUGEE_CAMP_WIDTH, REFUGEE_CAMP_HEIGHT
            self.tilemap = {
                'width': REFUGEE_CAMP_WIDTH,
                'height': REFUGEE_CAMP_HEIGHT,
                'tile_grid': None  # Will use old system
            }


        config = {
             'tile_size': 64,
             'map_width': self.tilemap['width'],
             'map_height': self.tilemap['height'],
        #     'location_id': 'refugee_camp_main',
             'map_functions': {
                'get_tile_type': lambda x, y: get_tile_type(x, y, self.tilemap['tile_grid']),
                'is_walkable': lambda x, y: is_walkable_tile(
                    get_tile_type(x, y, self.tilemap['tile_grid']),
                    REFUGEE_CAMP_WALKABLE
                ),
                'get_tile_color': None,  # Using graphics now, not colors
                'get_building_info': get_transition_info,
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
        if not hasattr(game_state, 'refugee_camp_x'):
            game_state.refugee_camp_x = REFUGEE_CAMP_SPAWN_X
            game_state.refugee_camp_y = REFUGEE_CAMP_SPAWN_Y
        
        self.renderer.update_camera(
            game_state.refugee_camp_x, 
            game_state.refugee_camp_y
        )
    
    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)

        # CHECK FOR AUTO-NAVIGATION TO NIGHT DEFENSE
        if hasattr(game_state, 'ready_for_night_defense') and game_state.ready_for_night_defense:
            game_state.ready_for_night_defense = False  # Clear flag
            if controller:
                print(f"🌙 Auto-navigating to night defense...")
                controller.event_manager.emit("SCREEN_CHANGE", {
                    'target_screen': 'refugee_camp_nighttime_defense',
                    'source_screen': 'refugee_camp_main_nav'
                })
                return  # Don't process anything else this frame
        
        # Check if we need to trigger loot check after dialogue
        if hasattr(game_state, 'trigger_loot_check') and game_state.trigger_loot_check:
            loot_table_id = game_state.trigger_loot_check
            game_state.trigger_loot_check = None  # Clear flag
            
            # Trigger loot check using existing system
            self._trigger_loot_check(loot_table_id, game_state, controller)
            return
        
        # Handle movement
        old_x = game_state.refugee_camp_x
        old_y = game_state.refugee_camp_y
        
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)
        
        # Check if player moved to new tile
        if new_x != old_x or new_y != old_y:
            
            # PRIORITY 1: Check for combat trigger on new tile
            combat_trigger = self.renderer.check_combat_trigger(new_x, new_y)
            
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
                    if controller:
                        game_state.previous_screen = 'refugee_camp_main_nav'
                        game_state.current_combat_encounter = combat_trigger['encounter_id']
                        print(f"🎯 Starting combat encounter: {combat_trigger['encounter_id']}")
                        
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": "combat",
                            "source_screen": "refugee_camp_main_nav"
                        })
                    return  # Don't move yet, combat starting
            
            # No combat (or failed chance roll), update position
            game_state.refugee_camp_x = new_x
            game_state.refugee_camp_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Update transition cooldown
        self.renderer.update_transition_cooldown(dt)

        # Check for ENTER key interactions (debounced, with cooldown)
        if (self.renderer.check_enter_just_pressed(keys) and 
            not self.showing_message and 
            self.renderer.can_interact()):
            player_x = game_state.refugee_camp_x
            player_y = game_state.refugee_camp_y
            
            # INTERACTION PRIORITY ORDER:
            
            # Priority 1: Area transitions (doors, exits)
            transition_info = self.renderer.check_valid_entrance(player_x, player_y, 
                                                                self.renderer.player_direction)
            if transition_info and transition_info[0]:
                transition_data = transition_info[0]
                
                # CHECK REQUIREMENTS BEFORE NAVIGATING
                requirements = transition_data.get('requirements', {})
                can_transition = True
                blocked_message = transition_data.get('blocked_message', 'You cannot leave yet.')

                # CUSTOM CHECK: Block leaving in two scenarios
                if transition_data.get('target_screen') == 'exploration_hub':
                    agreed = getattr(game_state, 'agreed_to_defend_camp', False)
                    defended = getattr(game_state, 'refugee_camp_defended', False)
                    rewarded = getattr(game_state, 'refugee_combat_rewarded', False)
                    
                    print(f"🚪 EXIT CHECK: agreed={agreed}, defended={defended}, rewarded={rewarded}")
                    
                    # Scenario 1: Agreed to defend but haven't fought yet
                    if agreed and not defended:
                        can_transition = False
                        blocked_message = "You agreed to help defend the camp. Speak with Marta when you're ready to rest."
                    
                    # Scenario 2: Defended but haven't collected reward yet
                    elif defended and not rewarded:
                        can_transition = False
                        blocked_message = "You should speak with Marta before leaving. She wanted to thank you for defending the camp."          
                
                # Check if any flags must be false
                flags_must_be_false = requirements.get('flags_any_false', [])
                for flag_name in flags_must_be_false:
                    if getattr(game_state, flag_name, False):
                        # Flag is true, blocking transition
                        can_transition = False
                        break
                
                # Check if any flags must be true
                flags_must_be_true = requirements.get('flags_any_true', [])
                if flags_must_be_true:
                    any_true = False
                    for flag_name in flags_must_be_true:
                        if getattr(game_state, flag_name, False):
                            any_true = True
                            break
                    if not any_true:
                        can_transition = False
                
                # Navigate or show blocked message
                if can_transition:
                    if controller:
                        target = transition_data['target_screen']
                        self.renderer.start_transition_cooldown()
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            'target_screen': target,
                            'source_screen': 'refugee_camp_main_nav'
                        })
                else:
                    # Show blocked message
                    self.show_temp_message(blocked_message)
                
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
                        setattr(game_state, return_screen_attr, 'refugee_camp_main_nav')

                        print(f"🔍 DEBUG: Set {return_screen_attr} = {getattr(game_state, return_screen_attr, 'NOT SET')}")

                        # Store flag name for later (set after loot is taken)
                        game_state.pending_search_flag = flag_set
                        
                        # Navigate to dialogue screen
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": examine_dialogue,
                            "source_screen": 'refugee_camp_main_nav'
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
        location_file = os.path.join(LOCATION_DATA_PATH, "refugee_camp.json")
        if not os.path.exists(location_file):
            print(f"❌ Cannot find location file: {location_file}")
            return
        
        with open(location_file, 'r') as f:
            location_full_data = json.load(f)
            location_data = location_full_data.get('refugee_camp', location_full_data)
        
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
        game_state.pre_combat_location = 'refugee_camp_main_nav'
        
        # Store the search flag to set when overlay closes
        if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
            game_state.search_loot_flag = game_state.pending_search_flag
            game_state.pending_search_flag = None
        
        # Open loot overlay
        game_state.overlay_state.open_overlay("combat_loot")
        
        print(f"🔍 Search loot overlay opened: {len(items_list)} item types found")

    def render(self, surface, fonts, images, game_state):
        """Render the navigation screen"""
        surface.fill(BLACK)
        
        # Get player position for rendering
        player_x = game_state.refugee_camp_x
        player_y = game_state.refugee_camp_y
        
        # Draw map tiles
        self.renderer.draw_map(surface, fonts, player_x, player_y)
        
        # Draw player sprite
        self.renderer.draw_player(surface, player_x, player_y)
        
        # Draw party status panel (right side)
        draw_party_status_panel(surface, game_state, fonts)
        
        # Draw location title at top
        title_text = "REFUGEE CAMP - MAIN CLEARING"
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
_refugee_camp_main_nav_instance = None

def draw_refugee_camp_main_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _refugee_camp_main_nav_instance
    
    if _refugee_camp_main_nav_instance is None:
        _refugee_camp_main_nav_instance = RefugeeCampMainNav()
    
    # Handle input
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _refugee_camp_main_nav_instance.update(dt, keys, game_state, controller)
    
    # Render
    return _refugee_camp_main_nav_instance.render(surface, fonts, images, game_state)