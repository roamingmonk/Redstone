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
        if not hasattr(game_state, 'dungeon_l3_x'):
            # Check if player came via mine tunnel (future feature)
            from utils.quest_system import get_quest_manager
            quest_mgr = get_quest_manager()
            
            if quest_mgr and quest_mgr.get_flag('using_mine_tunnel_entrance'):
                # Spawn at mine entrance (left side)
                game_state.dungeon_l3_x = 2
                game_state.dungeon_l3_y = 10
                print(f"🏛️ Entered Dungeon Level 3 via MINE TUNNEL at (2, 10)")
            else:
                # Spawn at stairs from Level 2 (top, front door route)
                game_state.dungeon_l3_x = DUNGEON_L3_SPAWN_X
                game_state.dungeon_l3_y = DUNGEON_L3_SPAWN_Y
                print(f"🏛️ Entered Dungeon Level 3 via FRONT DOOR at ({DUNGEON_L3_SPAWN_X}, {DUNGEON_L3_SPAWN_Y})")
        
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
                    from utils.quest_system import get_quest_manager
                    quest_mgr = get_quest_manager()
                    if quest_mgr and quest_mgr.get_flag(completion_flag):
                        print(f"   ✓ Already cleared, skipping")
                        # Update position and continue
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
        
        # Check for transitions
        self.current_transition = self.renderer.check_valid_entrance(
            game_state.dungeon_l3_x, 
            game_state.dungeon_l3_y
        )
        
        # Check for searchables
        self.current_searchable = self.renderer.check_searchable_interaction(
            game_state.dungeon_l3_x, 
            game_state.dungeon_l3_y
        )
        
        # Update message timer
        if self.showing_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.showing_message = False
    
    def handle_interact(self, game_state, controller):
        """Handle E key interaction"""
        # Check transitions first
        if self.current_transition:
            requirements = self.current_transition.get('requirements', {})
            required_flag = requirements.get('flag')
            
            # Check if stairs/transition requires level completion
            if required_flag:
                from utils.quest_system import get_quest_manager
                quest_mgr = get_quest_manager()
                
                if not quest_mgr or not quest_mgr.get_flag(required_flag):
                    self.show_message("The passage ahead is blocked. Clear all enemies first.")
                    return
            
            # Navigate to target screen
            target = self.current_transition.get('target_screen')
            action = self.current_transition.get('action', '')
            
            # Check for "NOT YET IMPLEMENTED" message
            if 'NOT YET IMPLEMENTED' in action:
                self.show_message("This route is not yet available. Use the front door for now.")
                return
            
            if controller and hasattr(controller, 'event_manager'):
                controller.event_manager.emit("SCREEN_CHANGE", {"target": target})
            return
        
        # Check searchables
        if self.current_searchable:
            interaction_type = self.current_searchable.get('interaction_type')
            
            if interaction_type == 'dialogue':
                # Trigger dialogue (altar, ritual, brazier, etc.)
                dialogue_id = self.current_searchable.get('examine_dialogue')
                if controller and hasattr(controller, 'event_manager'):
                    controller.event_manager.emit("START_DIALOGUE", {
                        "npc_id": dialogue_id,
                        "dialogue_file": dialogue_id
                    })
            
            elif interaction_type == 'loot':
                # Trigger loot (chest)
                loot_table = self.current_searchable.get('loot_table')
                flag = self.current_searchable.get('flag_set')
                
                # Check if already looted
                from utils.quest_system import get_quest_manager
                quest_mgr = get_quest_manager()
                if quest_mgr and quest_mgr.get_flag(flag):
                    self.show_message("Already searched.")
                    return
                
                # Open loot screen
                if controller and hasattr(controller, 'event_manager'):
                    controller.event_manager.emit("OPEN_LOOT", {
                        "loot_table": loot_table,
                        "flag_to_set": flag
                    })
    
    def show_message(self, text):
        """Display temporary message"""
        self.message_text = text
        self.showing_message = True
        self.message_timer = 2.5  # 2.5 seconds
    
    def render(self, surface, game_state, fonts, images):
        """Render the dungeon level 3 navigation screen"""
        surface.fill(BLACK)
        
        # Render the map using shared renderer
        self.renderer.render(
            surface, 
            game_state.dungeon_l3_x, 
            game_state.dungeon_l3_y,
            fonts
        )
        
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
        
        if self.current_transition:
            action_text = f"[E] {self.current_transition.get('action', 'Interact')}"
            prompt_surface = prompt_font.render(action_text, True, YELLOW)
            surface.blit(prompt_surface, (20, 700))
        
        if self.current_searchable:
            name = self.current_searchable.get('name', 'Object')
            action_text = f"[E] Examine {name}"
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