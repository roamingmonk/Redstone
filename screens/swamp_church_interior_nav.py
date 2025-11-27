import pygame
import random
import json
from ui.base_location_navigation import NavigationRenderer
from data.maps.swamp_church_interior_map import (
    SWAMP_CHURCH_INT_WIDTH,
    SWAMP_CHURCH_INT_HEIGHT,
    SWAMP_CHURCH_INT_SPAWN_X,
    SWAMP_CHURCH_INT_SPAWN_Y,
    get_tile_type,
    is_walkable,
    get_tile_color,
    get_transition_at_entrance,
    get_searchable_at_position
)
from utils.constants import WHITE, YELLOW, BLACK, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT
from utils.graphics import draw_border, draw_centered_text
from utils.party_display import draw_party_status_panel
from game_logic.item_manager import item_manager

LAYOUT_MAP_Y = 60
LAYOUT_MAP_HEIGHT = 500

_swamp_church_interior_nav_instance = None

class SwampChurchInteriorNav:
    def __init__(self):
        config = {
            'player_sprite_size': 64,
            'map_width': SWAMP_CHURCH_INT_WIDTH,
            'map_height': SWAMP_CHURCH_INT_HEIGHT,
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_tile_color': get_tile_color,
                'get_building_info': get_transition_at_entrance,
                'get_searchable_info': get_searchable_at_position
            }
        }
        self.renderer = NavigationRenderer(config)
        self.showing_message = False
        self.message_text = ""


    def show_temp_message(self, message, duration=3000):  
        """Display a temporary message"""
        self.showing_message = True
        self.message_text = message
        self.message_timer = duration   # 3 sec
        
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
        old_x = game_state.swamp_church_int_x
        old_y = game_state.swamp_church_int_y
        
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)
        
        # Update position if moved (no combat triggers in interior)
        if new_x != old_x or new_y != old_y:
            game_state.swamp_church_int_x = new_x
            game_state.swamp_church_int_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Update transition cooldown
        self.renderer.update_transition_cooldown(dt)

        # Check for ENTER key interactions (debounced, with cooldown)
        if (self.renderer.check_enter_just_pressed(keys) and 
            not self.showing_message and 
            self.renderer.can_interact()):
            
            player_x = game_state.swamp_church_int_x
            player_y = game_state.swamp_church_int_y
            
            # Priority 1: Area transitions (doors, exits)
            transition_info = self.renderer.check_valid_entrance(player_x, player_y, 
                                                                self.renderer.player_direction)
            if transition_info and transition_info[0]:
                transition_data = transition_info[0]
                
                # CHECK IF PLAYER NEEDS TO READ CULT DOCUMENTS BEFORE LEAVING
                can_transition = True
                blocked_message = "You cannot leave yet."
                
                # If exiting to exterior and documents are available but not read
                if transition_data.get('target_screen') == 'swamp_church_exterior_nav':
                    found_docs = getattr(game_state, 'found_cult_documents', False)
                    read_docs = getattr(game_state, 'read_cult_documents', False)
                    
                    if found_docs and not read_docs:
                        # Documents are available (after combat) but player hasn't read them
                        can_transition = False
                        blocked_message = "You should examine the cult documents before leaving. They may contain crucial information."
                
                # Navigate or show blocked message
                if can_transition:
                    if controller:
                        target = transition_data['target_screen']
                        self.renderer.start_transition_cooldown()
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            'target_screen': target,
                            'source_screen': 'swamp_church_interior_nav'
                        })
                else:
                    # Show blocked message
                    self.show_temp_message(blocked_message)
                
                return
            
            # Priority 2: Searchable objects
            searchable_info = self.renderer.check_searchable_object(player_x, player_y)
            if searchable_info:
                flag_set = searchable_info.get('flag_set')
                if flag_set and getattr(game_state, flag_set, False):
                    self.show_temp_message("You've already searched here.")
                else:
                    # ===== CHECK REQUIREMENTS BEFORE INTERACTION =====
                    requirements = searchable_info.get('requirements', {})
                    can_interact = True
                    
                    # Check if all required flags are met
                    for flag_name, required_value in requirements.items():
                        current_value = getattr(game_state, flag_name, False)
                        if current_value != required_value:
                            # Requirement not met - silently skip
                            can_interact = False
                            break
                    
                    # Only proceed if requirements are met (or no requirements)
                    if can_interact:
                        examine_dialogue = searchable_info.get('examine_dialogue')
                        if examine_dialogue and controller:
                            npc_id = examine_dialogue.split('_')[-1]
                            return_screen_attr = f'{npc_id}_return_screen'
                            setattr(game_state, return_screen_attr, 'swamp_church_interior_nav')
                            game_state.pending_search_flag = flag_set
                            
                            controller.event_manager.emit("SCREEN_CHANGE", {
                                "target_screen": examine_dialogue,
                                "source_screen": 'swamp_church_interior_nav'
                            })
                    # ===== END REQUIREMENTS CHECK =====
                return
        
        # Update temp message timer
        if self.showing_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.showing_message = False
    
    def update_player_position(self, game_state):
        """Initialize or restore player position"""
        if not hasattr(game_state, 'swamp_church_int_x'):
            game_state.swamp_church_int_x = SWAMP_CHURCH_INT_SPAWN_X
            game_state.swamp_church_int_y = SWAMP_CHURCH_INT_SPAWN_Y
        
        self.renderer.update_camera(
            game_state.swamp_church_int_x, 
            game_state.swamp_church_int_y
        )

    def _trigger_loot_check(self, loot_table_id, game_state, controller):
        """Roll for items from loot table and open combat_loot overlay."""

        
        # Load loot table
        with open('data/locations/swamp_church.json', 'r') as f:
            location_data = json.load(f)
        
        # Access the nested structure: file -> "swamp_church" -> "loot_tables" -> table_id
        swamp_church_data = location_data.get('swamp_church', {})
        loot_table = swamp_church_data.get('loot_tables', {}).get(loot_table_id, {})
        
        print(f"🎲 DEBUG: Loading loot table '{loot_table_id}': {loot_table}")
        
        # Roll for items
        items_dict = {}
        for item_config in loot_table.get('items', []):
            item_id = item_config.get('item_id')
            quantity = item_config.get('quantity', 1)
            chance = item_config.get('chance', 1.0)
            
            if random.random() <= chance:
                if item_id in items_dict:
                    items_dict[item_id] += quantity
                else:
                    items_dict[item_id] = quantity
        
        print(f"🎁 DEBUG: Rolled items: {items_dict}")
        
        # Convert to combat_loot overlay format with full item data
        items_list = []
        for item_id, quantity in items_dict.items():
            display_name = item_manager.get_display_name(item_id)
            items_list.append({
                'item_id': item_id,
                'quantity': quantity,
                'name': display_name
            })
        
        print(f"📦 DEBUG: Final items list: {items_list}")
        
        # Set combat loot data and open overlay
        game_state.combat_loot_data = {
            'total_gold': 0,
            'items': items_list
        }
        game_state.pre_combat_location = 'swamp_church_interior_nav'

        # Store the search flag to set when overlay closes
        if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
            game_state.search_loot_flag = game_state.pending_search_flag
            game_state.pending_search_flag = None

        game_state.overlay_state.open_overlay("combat_loot")
        
    def handle_input(self, event, game_state, controller):
        """Handle keyboard input for movement and interactions."""
        if event.type != pygame.KEYDOWN:
            return
        
        # Handle movement with arrow keys
        moved = False
        if event.key == pygame.K_UP:
            moved = self.renderer.move_player(0, -1)
        elif event.key == pygame.K_DOWN:
            moved = self.renderer.move_player(0, 1)
        elif event.key == pygame.K_LEFT:
            moved = self.renderer.move_player(-1, 0)
        elif event.key == pygame.K_RIGHT:
            moved = self.renderer.move_player(1, 0)
        
        # Check for area transitions after movement
        if moved:
            transition_info = self.renderer.check_building_entrance(
                self.renderer.player_x,
                self.renderer.player_y
            )
            if transition_info:
                target = transition_info.get('target')
                if target:
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        "target_screen": target,
                        "source_screen": "swamp_church_interior_nav"
                    })
                    return
        
        # Handle Enter key for examining searchable objects
        if event.key == pygame.K_RETURN:
            searchable = self.renderer.check_searchable_object(
                self.renderer.player_x,
                self.renderer.player_y
            )
            
            if searchable:
                examine_dialogue = searchable.get('examine_dialogue')
                flag_set = searchable.get('flag_set')
                
                # Check if already examined/searched
                if flag_set and getattr(game_state, flag_set, False):
                    return  # Already searched, do nothing
                
                if examine_dialogue:
                    # Set return screen for dialogue
                    npc_id = examine_dialogue.split('_')[-1]
                    setattr(game_state, f'{npc_id}_return_screen', 'swamp_church_interior_nav')
                    
                    # Transition to dialogue
                    controller.event_manager.emit("SCREEN_CHANGE", {
                        "target_screen": examine_dialogue,
                        "source_screen": "swamp_church_interior_nav"
                    })
    
    def render(self, surface, fonts, images, game_state):
        """Render the interior navigation screen"""
        surface.fill(BLACK)
        
        # Get player position for rendering
        player_x = game_state.swamp_church_int_x
        player_y = game_state.swamp_church_int_y
        
        # Draw map tiles
        self.renderer.draw_map(surface, fonts, player_x, player_y)
        
        # Draw player sprite
        self.renderer.draw_player(surface, player_x, player_y)
        
        # Draw NPCs (if any)
        # TODO: NPC rendering when needed
        
        # Draw party status panel (right side)
        draw_party_status_panel(surface, game_state, fonts)
        
        # Draw location title at top
        title_text = "CHURCH IN THE SWAMP - INTERIOR"
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
            # Check requirements first
            requirements = searchable.get('requirements', {})
            requirements_met = True
            
            for flag_name, required_value in requirements.items():
                current_value = getattr(game_state, flag_name, False)
                if current_value != required_value:
                    requirements_met = False
                    break
            
            # Only show prompt if requirements are met
            if requirements_met:
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

def draw_swamp_church_interior_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _swamp_church_interior_nav_instance
    
    if _swamp_church_interior_nav_instance is None:
        _swamp_church_interior_nav_instance = SwampChurchInteriorNav()
    
    # Handle input
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _swamp_church_interior_nav_instance.update(dt, keys, game_state, controller)
    
    # Render
    return _swamp_church_interior_nav_instance.render(surface, fonts, images, game_state)