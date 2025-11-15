"""
Dungeon Level 2 Navigation - Ancient Lower Ruins
Second level of the cult's sanctum - deeper and more dangerous
"""

import pygame
import random
import json
import os
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, RED, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT, LOCATION_DATA_PATH
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.dungeon_level_2_map import (
    DUNGEON_L2_WIDTH,
    DUNGEON_L2_HEIGHT,
    DUNGEON_L2_SPAWN_X,
    DUNGEON_L2_SPAWN_Y,
    get_tile_type,
    is_walkable,
    get_tile_color,
    get_transition_at_entrance,
    get_searchable_at_position,
    get_combat_trigger,
    get_environmental_hazard
)

class DungeonLevel2Nav:
    """Navigation screen for Dungeon Level 2"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        config = {
            'map_width': DUNGEON_L2_WIDTH,
            'map_height': DUNGEON_L2_HEIGHT,
            'location_id': 'dungeon_level_2',
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
        if not hasattr(game_state, 'dungeon_l2_x'):
            game_state.dungeon_l2_x = DUNGEON_L2_SPAWN_X
            game_state.dungeon_l2_y = DUNGEON_L2_SPAWN_Y
            print(f"🏛️ Entered Dungeon Level 2 at ({DUNGEON_L2_SPAWN_X}, {DUNGEON_L2_SPAWN_Y})")
        
        self.renderer.update_camera(
            game_state.dungeon_l2_x, 
            game_state.dungeon_l2_y
        )
    
    def handle_environmental_hazard(self, hazard_data, game_state, controller):
        """Handle environmental hazard triggers (weak floors, etc.)"""
        hazard_type = hazard_data.get('hazard_type')
        damage = hazard_data.get('damage', '1d6')
        message = hazard_data.get('message', 'Environmental hazard!')
        
        # Show message
        self.show_temp_message(message)
        
        # Apply damage to party (simplified - could be more sophisticated)
        # For now, just log it
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
        
        # Check for loot trigger (from dialogue setting trigger_loot_check flag)
        print(f"🔍 DEBUG: Checking for loot trigger...")  # ADD THIS
        if hasattr(game_state, 'trigger_loot_check'):
            print(f"🔍 DEBUG: trigger_loot_check exists: {game_state.trigger_loot_check}")  # ADD THIS
        
        if hasattr(game_state, 'trigger_loot_check') and game_state.trigger_loot_check:
            loot_table_id = game_state.trigger_loot_check
            print(f"🎁 DEBUG: Triggering loot check for: {loot_table_id}")  # ADD THIS
            game_state.trigger_loot_check = None
            self._trigger_loot_check(loot_table_id, game_state, controller)
            return
    
        # Handle movement
        old_x = game_state.dungeon_l2_x
        old_y = game_state.dungeon_l2_y
        
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)
        
        # Check if player moved to new tile
        if new_x != old_x or new_y != old_y:
            
            # PRIORITY 1: Check for combat trigger on new tile
            combat_trigger = self.renderer.check_combat_trigger(new_x, new_y)
            
            if combat_trigger:
                print(f"⚔️ Combat triggered at ({new_x}, {new_y})")
                print(f"   Encounter: {combat_trigger.get('encounter_id')}")
                
                # Check if already completed
                completion_flag = combat_trigger.get('completion_flag')
                if completion_flag and getattr(game_state, completion_flag, False):
                    # Already cleared, allow movement
                    game_state.dungeon_l2_x = new_x
                    game_state.dungeon_l2_y = new_y
                    self.renderer.update_camera(new_x, new_y)
                    return
                
                # Check if this is a trap encounter (applies damage first)
                trap_damage = combat_trigger.get('trap_damage')
                if trap_damage:
                    self.show_temp_message(f"TRAP! You take {trap_damage} damage!")
                    print(f"   💥 Trap triggered! Damage: {trap_damage}")
                
                # Trigger combat
                encounter_id = combat_trigger.get('encounter_id')
                if controller and hasattr(controller, 'event_manager'):
                    controller.event_manager.emit("INITIATE_COMBAT", {
                        "encounter_id": encounter_id,
                        "return_screen": "dungeon_level_2_nav",
                        "completion_flag": completion_flag,
                        "trap_damage": trap_damage if trap_damage else None
                    })
                return  # Don't move yet, combat will handle it
            
            # PRIORITY 2: Check for environmental hazards
            hazard = get_environmental_hazard(new_x, new_y)
            if hazard:
                # Check if already triggered this session
                hazard_flag = f"hazard_{new_x}_{new_y}_triggered"
                if not getattr(game_state, hazard_flag, False):
                    # Trigger hazard
                    self.handle_environmental_hazard(hazard, game_state, controller)
                    setattr(game_state, hazard_flag, True)
            
            # PRIORITY 3: Update position if no combat
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
                    
                    # Handle level-specific spawn points if needed
                    # (Level 2 doesn't need spawn overrides currently)
                    
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
                        # Extract npc_id from dialogue name (e.g., "dungeon_level_2_chest" -> "chest")
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
    
   
    
    def show_temp_message(self, text):
        self.showing_message = True
        self.message_text = text
        self.message_timer = 3000  # milliseconds, matches Level 1
    
    def _trigger_loot_check(self, loot_table_id, game_state, controller):
        """Trigger loot check using hill ruins loot tables"""
        print(f"💰 DEBUG: _trigger_loot_check called with: {loot_table_id}")


        location_file = os.path.join(LOCATION_DATA_PATH, "hill_ruins.json")
        print(f"💰 DEBUG: Looking for loot file at: {location_file}")
        
        if not os.path.exists(location_file):
            print(f"❌ DEBUG: Loot file NOT found!")
            return

        print(f"💰 DEBUG: Loading loot file...")
        with open(location_file, 'r') as f:
            location_full_data = json.load(f)
            location_data = location_full_data.get('hill_ruins', location_full_data)

        loot_tables = location_data.get('loot_tables', {})
        loot_table = loot_tables.get(loot_table_id)
        
        print(f"💰 DEBUG: Found loot table: {loot_table is not None}")

        if not loot_table:
            print(f"❌ DEBUG: Loot table '{loot_table_id}' not found in file!")
            return

        print(f"💰 DEBUG: Processing loot items...")
        items_dict = {}
        for item_config in loot_table.get('items', []):
            item_id = item_config.get('item_id')
            quantity = item_config.get('quantity', 1)
            chance = item_config.get('chance', 1.0)

            if random.random() <= chance:
                items_dict[item_id] = items_dict.get(item_id, 0) + quantity

        print(f"💰 DEBUG: Items rolled: {items_dict}")
        
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

        print(f"💰 DEBUG: Final items list: {items_list}")

        if not items_list:
            print(f"💰 DEBUG: No items found, showing message")
            self.show_temp_message("You found nothing of value.")
            if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
                setattr(game_state, game_state.pending_search_flag, True)
                game_state.pending_search_flag = None
            return

        print(f"💰 DEBUG: Creating loot data and opening overlay...")
        loot_data = {'total_gold': 0, 'items': items_list}
        game_state.combat_loot_data = loot_data
        game_state.pre_combat_location = 'dungeon_level_2_nav'

        if hasattr(game_state, 'pending_search_flag') and game_state.pending_search_flag:
            game_state.search_loot_flag = game_state.pending_search_flag
            game_state.pending_search_flag = None

        print(f"💰 DEBUG: About to call overlay_state.open_overlay('combat_loot')")
        game_state.overlay_state.open_overlay("combat_loot")
        print(f"✅ DEBUG: Overlay opened!")

    def render(self, surface, fonts, images, game_state):
        """Render the dungeon level 2 navigation screen"""
        surface.fill(BLACK)
        
        # Render the map using shared renderer
        player_x = game_state.dungeon_l2_x
        player_y = game_state.dungeon_l2_y
        
        self.renderer.draw_map(surface, fonts, player_x, player_y)
        self.renderer.draw_player(surface, player_x, player_y)
        
        # Party status panel
        draw_party_status_panel(surface, game_state, fonts)
        
        # Location title
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        title_text = "DUNGEON - LEVEL 2: ANCIENT LOWER RUINS"
        draw_centered_text(surface, title_text, title_font, 20, YELLOW)
        
        # Interaction prompts
        prompt_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
        
        # Show interaction prompts based on player position
        player_x = game_state.dungeon_l2_x
        player_y = game_state.dungeon_l2_y
        
        transition_info = self.renderer.check_valid_entrance(player_x, player_y, self.renderer.player_direction)
        if transition_info and transition_info[0]:
            action_text = f"[ENTER] {transition_info[0].get('action', 'Use stairs')}"
            prompt_surface = prompt_font.render(action_text, True, YELLOW)
            surface.blit(prompt_surface, (20, 700))
        
        searchable_info = self.renderer.check_searchable_object(player_x, player_y)
        if searchable_info:
            name = searchable_info.get('name', 'Object')
            action_text = f"[ENTER] Examine {name}"
            prompt_surface = prompt_font.render(action_text, True, YELLOW)
            surface.blit(prompt_surface, (20, 720))
        
        # Show temporary messages
        if self.showing_message:
            msg_surface = prompt_font.render(self.message_text, True, WHITE)
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
        
        return {}


# Global instance
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