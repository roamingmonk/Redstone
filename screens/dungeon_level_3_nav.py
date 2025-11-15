"""
Dungeon Level 3 Navigation - The Convergence
Third level where front door and mine tunnel routes meet
Transition from ancient ruins to active cult territory
"""

import pygame
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, RED, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.dungeon_level_3_map import (
    DUNGEON_L3_WIDTH,
    DUNGEON_L3_HEIGHT,
    DUNGEON_L3_SPAWN_X,
    DUNGEON_L3_SPAWN_Y,
    get_tile_type,
    is_walkable,
    get_tile_color,
    get_transition_at_entrance,
    get_searchable_at_position,
    get_combat_trigger
)

class DungeonLevel3Nav:
    """Navigation screen for Dungeon Level 3 - Convergence Zone"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        config = {
            'map_width': DUNGEON_L3_WIDTH,
            'map_height': DUNGEON_L3_HEIGHT,
            'location_id': 'dungeon_level_3',
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
        # Check for spawn override (from transitions)
        if hasattr(game_state, 'dungeon_l3_spawn_override_x'):
            game_state.dungeon_l3_x = game_state.dungeon_l3_spawn_override_x
            game_state.dungeon_l3_y = game_state.dungeon_l3_spawn_override_y
            delattr(game_state, 'dungeon_l3_spawn_override_x')
            delattr(game_state, 'dungeon_l3_spawn_override_y')
            print(f"✅ Level 3 spawn override: ({game_state.dungeon_l3_x}, {game_state.dungeon_l3_y})")
        elif not hasattr(game_state, 'dungeon_l3_x'):
            # Check if player came via mine tunnel (future feature)
            if getattr(game_state, 'using_mine_tunnel_entrance', False):
                # Spawn at mine entrance (left side)
                game_state.dungeon_l3_x = 2
                game_state.dungeon_l3_y = 10
                print(f"🏛️ Entered Dungeon Level 3 via MINE TUNNEL at (2, 10)")
            else:
                # Spawn at stairs from Level 2 (top, front door route)
                game_state.dungeon_l3_x = DUNGEON_L3_SPAWN_X
                game_state.dungeon_l3_y = DUNGEON_L3_SPAWN_Y
                print(f"🏛️ Entered Dungeon Level 3 via FRONT DOOR at ({DUNGEON_L3_SPAWN_X}, {DUNGEON_L3_SPAWN_Y})")
        
        self.renderer.update_camera(game_state.dungeon_l3_x, game_state.dungeon_l3_y)
        
        self.renderer.update_camera(
            game_state.dungeon_l3_x, 
            game_state.dungeon_l3_y
        )
    
    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)
        
        # Handle movement
        old_x = game_state.dungeon_l3_x
        old_y = game_state.dungeon_l3_y
        
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
                if completion_flag:
                    if completion_flag and getattr(game_state, completion_flag, False):
                        # Already cleared, allow movement
                        game_state.dungeon_l3_x = new_x
                        game_state.dungeon_l3_y = new_y
                        self.renderer.update_camera(new_x, new_y)
                        return
                
                # Trigger combat
                encounter_id = combat_trigger.get('encounter_id')
                if controller and hasattr(controller, 'event_manager'):
                    controller.event_manager.emit("INITIATE_COMBAT", {
                        "encounter_id": encounter_id,
                        "return_screen": "dungeon_level_3_nav",
                        "completion_flag": completion_flag
                    })
                return  # Don't move yet, combat will handle it
            
            # PRIORITY 2: Update position if no combat
            game_state.dungeon_l3_x = new_x
            game_state.dungeon_l3_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Update transition cooldown
        self.renderer.update_transition_cooldown(dt)

        # Check for ENTER key interactions
        if (self.renderer.check_enter_just_pressed(keys) and 
            not self.showing_message and 
            self.renderer.can_interact()):
            
            player_x = game_state.dungeon_l3_x
            player_y = game_state.dungeon_l3_y

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
                        'source_screen': 'dungeon_level_3_nav'
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
                        setattr(game_state, return_screen_attr, 'dungeon_level_3_nav')
                        game_state.pending_search_flag = flag_set

                        controller.event_manager.emit("SCREEN_CHANGE", {
                            "target_screen": examine_dialogue,
                            "source_screen": 'dungeon_level_3_nav'
                        })
                return
        
        # Update message timer
        if self.showing_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.showing_message = False
    
    
    
    def show_message(self, text):
        """Display temporary message"""
        self.message_text = text
        self.showing_message = True
        self.message_timer = 2.5  # 2.5 seconds
    
    def render(self, surface, fonts, images, game_state):
        """Render the dungeon level 3 navigation screen"""
        surface.fill(BLACK)
        
        # Render the map using shared renderer
        player_x = game_state.dungeon_l3_x
        player_y = game_state.dungeon_l3_y
        
        self.renderer.draw_map(surface, fonts, player_x, player_y)
        self.renderer.draw_player(surface, player_x, player_y)
        
        # Party status panel
        draw_party_status_panel(surface, game_state, fonts)
        
        # Location title
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        title_text = "DUNGEON - LEVEL 3: THE CONVERGENCE"
        draw_centered_text(surface, title_text, title_font, 20, YELLOW)
        
        # Subtitle (cult presence warning)
        subtitle_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
        subtitle_text = "Signs of cult activity ahead..."
        draw_centered_text(surface, subtitle_text, subtitle_font, 45, RED)
        
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
            pygame.draw.rect(surface, YELLOW, bg_rect, 2)
            
            surface.blit(msg_surface, msg_rect)
        
        return {}


# Global instance
_dungeon_level_3_instance = None

def draw_dungeon_level_3_nav(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _dungeon_level_3_instance

    if _dungeon_level_3_instance is None:
        _dungeon_level_3_instance = DungeonLevel3Nav()

    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _dungeon_level_3_instance.update(dt, keys, game_state, controller)

    return _dungeon_level_3_instance.render(surface, fonts, images, game_state)