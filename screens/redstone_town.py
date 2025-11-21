# screens/redstone_town.py
"""
Redstone Town Navigation - Using shared NavigationRenderer utility
"""

import pygame
from ui.base_location_navigation import NavigationRenderer, calculate_required_direction
from utils.constants import (BLACK, WHITE,
                             LAYOUT_IMAGE_Y, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT)
from utils.graphics import draw_border, draw_centered_text
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from utils.narrative_schema import narrative_schema
from data.maps.redstone_town_map import BUILDING_ENTRANCES
from utils.world_npc_spawner import get_world_npc_spawner

# Import town map data
try:
    from data.maps.redstone_town_map import *

    print(f"DEBUG: Imported spawn point = ({TOWN_SPAWN_X}, {TOWN_SPAWN_Y})")
except ImportError:
    # Fallback data
    print("DEBUG: Using fallback spawn")
    TOWN_WIDTH, TOWN_HEIGHT = 16, 12
    TOWN_SPAWN_X, TOWN_SPAWN_Y = 8, 6
    def get_tile_type(x, y): return 'street'
    def is_walkable(x, y): return True
    def get_building_info(x, y): return None

class RedstoneTownNavigation:
    def __init__(self):
        # Configure the shared renderer
        config = {
            'map_width': TOWN_WIDTH,
            'map_height': TOWN_HEIGHT,
            'location_id': 'redstone_town', 
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_building_info': get_building_at_entrance,
                'get_tile_color': get_tile_color
            }
        }
        
        self.renderer = NavigationRenderer(config)
        self.current_building = None
        self.showing_temp_message = False
        self.temp_message_text = ""
        self.temp_message_timer = 0

        self.current_npc = None
        self.npc_required_direction = None
        self.can_interact_npc = False

        self.can_interact = False  # For building interactions
        self.required_direction = None  # For building direction checking

        # Use shared graphics manager (singleton)
        self.graphics_manager = get_tile_graphics_manager()
        # After all your imports, before the class definition:
        print("Town navigation initialized with shared renderer")
    
    def update_player_position(self, game_state):
                
        """Initialize player position if needed"""
        if not hasattr(game_state, 'town_player_x'):
            game_state.town_player_x = TOWN_SPAWN_X
            game_state.town_player_y = TOWN_SPAWN_Y
            print(f"Player spawned at ({TOWN_SPAWN_X}, {TOWN_SPAWN_Y})")
        
        self.renderer.update_camera(game_state.town_player_x, game_state.town_player_y)
    
    def _start_next_victory_dialogue(self, game_state, controller):
            """Start the next NPC in the victory dialogue sequence"""
            
            if not hasattr(game_state, 'victory_npc_sequence'):
                print("⚠️ No victory sequence defined")
                return False
            
            if game_state.victory_npc_index >= len(game_state.victory_npc_sequence):
                print("✅ Victory dialogue sequence complete - all NPCs done")
                # All NPCs done - transition to epilogue slides (or just end for now)
                self._transition_to_epilogue_slides(game_state, controller)
                return False
            
            current_npc = game_state.victory_npc_sequence[game_state.victory_npc_index]
            print(f"🗣️ Starting victory dialogue #{game_state.victory_npc_index + 1} with: {current_npc}")
            
            # Set the dialogue state based on outcome
            self._set_victory_dialogue_state(game_state, current_npc)
            
            # Set return handler
            game_state.victory_dialogue_return_screen = 'redstone_town'
            
            # Emit dialogue screen change
            dialogue_file = f'redstone_town_{current_npc}'
            controller.event_manager.emit("SCREEN_CHANGE", {
                "target_screen": dialogue_file,
                "source_screen": 'redstone_town',
                "is_victory_sequence": True
            })
            
            # Increment for next time
            game_state.victory_npc_index += 1
            
            return True

    def check_victory_celebration_trigger(self, game_state, controller):
        """Check if we should auto-trigger victory celebration dialogues"""
        
        # Only trigger if flag is set and not already started
        if not getattr(game_state, 'trigger_victory_celebration', False):
            return False
            
        if getattr(game_state, 'victory_celebration_started', False):
            return False
        
        print("🎊 VICTORY CELEBRATION AUTO-TRIGGER")
        
        # Mark as started
        game_state.victory_celebration_started = True
        game_state.trigger_victory_celebration = False
        
        # Set up the NPC dialogue sequence
        game_state.victory_npc_sequence = []
        game_state.victory_npc_index = 0
        
        # Build sequence: Mayor -> Cassia -> Henrik (if quest done)
        # MAIN NPCS (branching dialogues)
        game_state.victory_npc_sequence.append('mayor')  # Always required
        
        if getattr(game_state, 'cassia_talked', False):
            game_state.victory_npc_sequence.append('cassia')
        
        # Casper & Meredith: Couple dialogue OR Meredith solo
        if getattr(game_state, 'casper_redemption_complete', False):
            # Casper returned ring - use couple dialogue
            game_state.victory_npc_sequence.append('casper_and_meredith_epilogue')
        elif getattr(game_state, 'meredith_talked', False):
            # Player talked to Meredith - simple dialogue
            game_state.victory_npc_sequence.append('meredith')
        
        if getattr(game_state, 'reported_shaft_to_henrik', False):
            game_state.victory_npc_sequence.append('henrik')
        
        # SUPPORTING NPCS (simple dialogues)
        if getattr(game_state, 'garrick_talked', False):
            game_state.victory_npc_sequence.append('garrick')
        
        if getattr(game_state, 'bernard_talked', False):
            game_state.victory_npc_sequence.append('bernard')
        
        if getattr(game_state, 'jenna_talked', False):
            game_state.victory_npc_sequence.append('jenna')
        
        if getattr(game_state, 'pete_talked', False):
            game_state.victory_npc_sequence.append('pete')
        
        if getattr(game_state, 'refugee_leader_talked', False):
            game_state.victory_npc_sequence.append('marta')
        
        print(f"📜 Victory NPC sequence: {game_state.victory_npc_sequence}")
        
        # Trigger first NPC dialogue (Mayor)
        self._start_next_victory_dialogue(game_state, controller)
        
        return True

    def _set_victory_dialogue_state(self, game_state, npc_id):
        """Set the correct dialogue state for victory conversations"""
        
        if npc_id == 'mayor':
            # Check mayor family status - use ARRIVAL states
            family_status = getattr(game_state, 'mayor_family_status', 'none')
            
            if family_status == 'all_saved':
                game_state.mayor_dialogue_state = 'victory_family_saved_arrival'
            elif family_status == 'partial':
                game_state.mayor_dialogue_state = 'victory_family_partial_arrival'
            else:
                game_state.mayor_dialogue_state = 'victory_family_lost_arrival'
            
            print(f"📋 Mayor dialogue state: {game_state.mayor_dialogue_state}")
        
        elif npc_id == 'cassia':
            # Check Marcus outcome - use ARRIVAL states
            if getattr(game_state, 'marcus_redeemed', False):
                game_state.cassia_dialogue_state = 'victory_marcus_redeemed_arrival'
            elif getattr(game_state, 'marcus_died_in_battle', False):
                game_state.cassia_dialogue_state = 'victory_marcus_died_arrival'
            else:
                game_state.cassia_dialogue_state = 'victory_marcus_died_arrival'
            
            print(f"📋 Cassia dialogue state: {game_state.cassia_dialogue_state}")
        
        elif npc_id == 'casper_and_meredith_epilogue':
            # Let narrative schema handle the state selection
            # It will pick "first_meeting" if they haven't talked yet
            # This allows full branching dialogue exploration
            print(f"📋 Casper & Meredith dialogue: Using narrative schema state selection")
        
        elif npc_id == 'meredith':
            # Meredith solo dialogue (player returned ring directly)
            game_state.meredith_dialogue_state = 'victory_ring_returned'
            print(f"📋 Meredith dialogue state: {game_state.meredith_dialogue_state}")
        
        elif npc_id == 'henrik':
            game_state.henrik_dialogue_state = 'victory_mine_route_arrival'
            print(f"📋 Henrik dialogue state: {game_state.henrik_dialogue_state}")
        
        elif npc_id == 'garrick':
            # Check if basement quest was completed for special dialogue
            if getattr(game_state, 'reported_basement_victory', False):
                game_state.garrick_dialogue_state = 'victory_with_basement'
            else:
                game_state.garrick_dialogue_state = 'victory_simple'
            print(f"📋 Garrick dialogue state: {game_state.garrick_dialogue_state}")
        
        elif npc_id == 'bernard':
            game_state.bernard_dialogue_state = 'victory_simple'
            print(f"📋 Bernard dialogue state: {game_state.bernard_dialogue_state}")
        
        elif npc_id == 'jenna':
            game_state.jenna_dialogue_state = 'victory_simple'
            print(f"📋 Jenna dialogue state: {game_state.jenna_dialogue_state}")
        
        elif npc_id == 'pete':
            game_state.pete_dialogue_state = 'victory_simple'
            print(f"📋 Pete dialogue state: {game_state.pete_dialogue_state}")
        
        elif npc_id == 'marta':
            game_state.marta_dialogue_state = 'victory_arrival'
            print(f"📋 Marta dialogue state: {game_state.marta_dialogue_state}")

    def _set_victory_dialogue_state(self, game_state, npc_id):
        """Set the correct dialogue state for victory conversations"""
        
        if npc_id == 'mayor':
            # Check mayor family status - use ARRIVAL states
            family_status = getattr(game_state, 'mayor_family_status', 'none')
            
            if family_status == 'all_saved':
                game_state.mayor_dialogue_state = 'victory_family_saved_arrival'
            elif family_status == 'partial':
                game_state.mayor_dialogue_state = 'victory_family_partial_arrival'
            else:
                game_state.mayor_dialogue_state = 'victory_family_lost_arrival'
            
            print(f"📋 Mayor dialogue state: {game_state.mayor_dialogue_state}")
        
        elif npc_id == 'cassia':
            # Check Marcus outcome - use ARRIVAL states
            if getattr(game_state, 'marcus_redeemed', False):
                game_state.cassia_dialogue_state = 'victory_marcus_redeemed_arrival'
            elif getattr(game_state, 'marcus_died_in_battle', False):
                game_state.cassia_dialogue_state = 'victory_marcus_died_arrival'
            else:
                game_state.cassia_dialogue_state = 'victory_marcus_died_arrival'
            
            print(f"📋 Cassia dialogue state: {game_state.cassia_dialogue_state}")
        
        elif npc_id == 'casper_and_meredith_epilogue':
            # Let narrative schema handle the state selection
            # It will pick "first_meeting" if they haven't talked yet
            # This allows full branching dialogue exploration
            print(f"📋 Casper & Meredith dialogue: Using narrative schema state selection")
        
        elif npc_id == 'meredith':
            # Meredith solo dialogue (player returned ring directly)
            game_state.meredith_dialogue_state = 'victory_ring_returned'
            print(f"📋 Meredith dialogue state: {game_state.meredith_dialogue_state}")
        
        elif npc_id == 'henrik':
            game_state.henrik_dialogue_state = 'victory_mine_route_arrival'
            print(f"📋 Henrik dialogue state: {game_state.henrik_dialogue_state}")
        
        elif npc_id == 'garrick':
            # Check if basement quest was completed for special dialogue
            if getattr(game_state, 'reported_basement_victory', False):
                game_state.garrick_dialogue_state = 'victory_with_basement'
            else:
                game_state.garrick_dialogue_state = 'victory_simple'
            print(f"📋 Garrick dialogue state: {game_state.garrick_dialogue_state}")
        
        elif npc_id == 'bernard':
            game_state.bernard_dialogue_state = 'victory_simple'
            print(f"📋 Bernard dialogue state: {game_state.bernard_dialogue_state}")
        
        elif npc_id == 'jenna':
            game_state.jenna_dialogue_state = 'victory_simple'
            print(f"📋 Jenna dialogue state: {game_state.jenna_dialogue_state}")
        
        elif npc_id == 'pete':
            game_state.pete_dialogue_state = 'victory_simple'
            print(f"📋 Pete dialogue state: {game_state.pete_dialogue_state}")
        
        elif npc_id == 'marta':
            game_state.marta_dialogue_state = 'victory_arrival'
            print(f"📋 Marta dialogue state: {game_state.marta_dialogue_state}")

    def _transition_to_epilogue_slides(self, game_state, controller):
        """Transition to epilogue cinematic slides"""
        print("🎬 Transitioning to epilogue slides")
        
        # Mark celebration complete
        game_state.victory_celebration_complete = True
        
        # Transition to first epilogue slide
        controller.event_manager.emit("SCREEN_CHANGE", {
            "target_screen": 'epilogue_slide_1',
            "source_screen": 'redstone_town'
        })
        
        print("✨ Victory celebration sequence finished!")
        print(f"📊 NPCs dialogued: {game_state.victory_npc_sequence}")

    def complete_epilogue_sequence(self):
        """Complete epilogue and transition to credits"""
        print("✨ Epilogue sequence complete - transitioning to credits")
        
        # Get the final slide's next_slide target
        slides = self.epilogue_data["slides"]
        if slides:
            final_slide = slides[-1]
            target = final_slide.get("next_slide", "credits")
            self.event_manager.emit("SCREEN_CHANGE", {"target": target})
        else:
            self.event_manager.emit("SCREEN_CHANGE", {"target": "credits"})

    def check_victory_dialogue_return(self, game_state, controller):
        """Check if we just returned from a victory dialogue and should continue sequence"""
        
        # Only process if we're in a victory sequence
        if not getattr(game_state, 'victory_celebration_started', False):
            return False
        
        if getattr(game_state, 'victory_celebration_complete', False):
            return False
        
        # Check if we just returned from dialogue
        just_completed = getattr(game_state, 'just_completed_victory_dialogue', False)
        
        if just_completed:
            print(f"✅ Returned from victory dialogue, continuing sequence")
            
            # Clear the flag FIRST to prevent re-triggering
            setattr(game_state, 'just_completed_victory_dialogue', False)
            
            # Small delay before next dialogue
            import pygame
            pygame.time.wait(500)
            
            # Start next dialogue in sequence
            result = self._start_next_victory_dialogue(game_state, controller)
            
            if not result:
                print("✨ Victory celebration sequence complete!")
                game_state.victory_celebration_complete = True
            
            return True
        
        return False

    def update(self, dt, keys, game_state, controller=None):
        """Update town navigation state"""
        # Initialize position FIRST before using it
        self.update_player_position(game_state)

        # DEBUG: Check flags
        if getattr(game_state, 'victory_celebration_started', False):
            print(f"🔍 DEBUG: victory_celebration_started=True, index={getattr(game_state, 'victory_npc_index', 'NOT SET')}, just_completed={getattr(game_state, 'just_completed_victory_dialogue', False)}")
        

        # CHECK FOR VICTORY CELEBRATION AUTO-TRIGGER (NEW)
        if controller and self.check_victory_celebration_trigger(game_state, controller):
            return  # Dialogue is starting, don't process other input
        
        # CHECK FOR VICTORY DIALOGUE CONTINUATION (AFTER RETURN FROM DIALOGUE)
        if controller and self.check_victory_dialogue_return(game_state, controller):
            return  # Next dialogue is starting
        
        # Handle movement using shared renderer
        new_x, new_y = self.renderer.handle_movement(
            keys, game_state.town_player_x, game_state.town_player_y
        )
        
        # Update position if moved
        if new_x != game_state.town_player_x or new_y != game_state.town_player_y:
            game_state.town_player_x = new_x
            game_state.town_player_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Check for building interactions with direction validation
        building_at_entrance = get_building_at_entrance(
            game_state.town_player_x, 
            game_state.town_player_y
        )
        
        # Calculate if player is facing the correct direction
        self.can_interact = False
        self.required_direction = None
        
        if building_at_entrance:
            
            # Find which building this entrance belongs to
            for building_id, building_data in BUILDING_ENTRANCES.items():
                entrance_tiles = building_data['entrance_tiles']
                if (game_state.town_player_x, game_state.town_player_y) in entrance_tiles:
                    # Found the building - get its position
                    building_pos = building_data['building_pos']
                    
                    # Calculate required direction
                    self.required_direction = calculate_required_direction(
                        game_state.town_player_x,
                        game_state.town_player_y,
                        building_pos
                    )
                    
                    # Check if player is facing the correct direction (or if direction check disabled)
                    skip_direction = building_at_entrance.get('skip_direction_check', False)
                    if skip_direction or self.renderer.player_direction == self.required_direction:
                        self.current_building = building_at_entrance
                        self.can_interact = True
                    else:
                        self.current_building = None
                        self.can_interact = False
                    break
        else:
            self.current_building = None

        # Check for NPC interactions with direction validation
        npc_info, npc_required_dir, can_interact_npc = self.renderer.check_npc_interaction(
            game_state.town_player_x,
            game_state.town_player_y,
            self.renderer.player_direction,
            'redstone_town',
            game_state
        )
        
        self.current_npc = npc_info if can_interact_npc else None
        self.npc_required_direction = npc_required_dir
        self.can_interact_npc = can_interact_npc
        
        # Handle building entry OR NPC dialogue (only if facing correct direction)
        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]):
            if self.current_building and self.can_interact:
                interaction_type = self.current_building.get('interaction_type')
                
                print(f"DEBUG: RT: hit return to go somewhere")
                
                if interaction_type == 'npc_dialogue':
                    print(f"DEBUG: RT: NPC Dialogue")
                    
                    # STEP 1: Check requirements before allowing interaction
                    requirements = self.current_building.get('requirements')
                    if requirements:
                        required_flags = requirements.get('flags', [])
                        requirements_met = True

                        # Check if ALL required flags are True
                        for flag_name in required_flags:
                            flag_value = getattr(game_state, flag_name, False)
                            print(f"DEBUG: RT: Checking NPC requirement '{flag_name}' = {flag_value}")
                            if not flag_value:
                                requirements_met = False
                                break

                        # If requirements not met, block interaction and show message
                        if not requirements_met:
                            self.showing_temp_message = True
                            self.temp_message_timer = pygame.time.get_ticks()
                            self.temp_message_text = requirements.get('message', "They are not available right now.")
                            print(f"DEBUG: RT: NPC requirements not met - blocking interaction")
                            return  # Exit early, don't load dialogue

                    # STEP 2: Proceed with NPC dialogue
                    npc_id = self.current_building.get('npc_id')
                    
                    if npc_id and controller:
                        # Use current location (redstone_town), not narrative schema
                        location = 'redstone_town'
                        target_screen = f"{location}_{npc_id}"  # ✅ Constructs 'redstone_town_mayor'
                    
                        # CHECK: Is the target dialogue screen implemented?
                        if hasattr(controller, 'screen_manager') and target_screen in controller.screen_manager.render_functions:
                            # Screen exists, proceed with NPC dialogue
                            controller.event_manager.emit("NPC_CLICKED", {
                                'npc_id': npc_id,
                                'location': location
                            })
                        else:
                            # NPC dialogue screen not implemented yet
                            self.showing_temp_message = True
                            self.temp_message_timer = pygame.time.get_ticks()
                            
                            # Contextual messages based on NPC
                            if npc_id == 'mayor':
                                self.temp_message_text = "The mayor is in an important meeting and cannot be disturbed."
                            else:
                                self.temp_message_text = "They seem too busy to talk right now."
                elif interaction_type == 'conditional_transition':
                    print(f"DEBUG: RT: Conditional Transition")

                    # STEP 1: Check requirements before allowing transition
                    requirements = self.current_building.get('requirements')
                    if requirements:
                        required_flags = requirements.get('flags', [])
                        requirements_met = True

                        # Check if ALL required flags are True
                        for flag_name in required_flags:
                            flag_value = getattr(game_state, flag_name, False)
                            print(f"DEBUG: RT: Checking requirement '{flag_name}' = {flag_value}")
                            if not flag_value:
                                requirements_met = False
                                break

                        # If requirements not met, block transition and show message
                        if not requirements_met:
                            self.showing_temp_message = True
                            self.temp_message_timer = pygame.time.get_ticks()
                            self.temp_message_text = requirements.get('message', "You cannot proceed yet.")
                            print(f"DEBUG: RT: Requirements not met - blocking transition")
                            return  # Exit early, don't proceed with transition
                        else:
                            print(f"DEBUG: RT: Requirements met - proceeding with transition")

                    # STEP 2: Get the flag to check and the target screens
                    flag_check = self.current_building.get('flag_check')
                    if_true_screen = self.current_building.get('if_true_screen')
                    if_false_screen = self.current_building.get('if_false_screen')

                    if flag_check and if_true_screen and if_false_screen and controller:
                        # Check if flag is set on game_state
                        flag_value = getattr(game_state, flag_check, False)

                        # Route based on flag value
                        target_screen = if_true_screen if flag_value else if_false_screen

                        print(f"DEBUG: RT: Flag '{flag_check}' = {flag_value}, routing to '{target_screen}'")

                        # CHECK: Is the target screen implemented?
                        if hasattr(controller, 'screen_manager') and target_screen in controller.screen_manager.render_functions:
                            controller.event_manager.emit("SCREEN_CHANGE", {
                                'target_screen': target_screen,
                                'source': 'town_navigation'
                            })
                        else:
                            # Screen not implemented
                            self.showing_temp_message = True
                            self.temp_message_timer = pygame.time.get_ticks()
                            self.temp_message_text = "The path ahead is not yet clear..."
                    else:
                        # Missing required configuration
                        self.showing_temp_message = True
                        self.temp_message_timer = pygame.time.get_ticks()
                        self.temp_message_text = "Sorry, it's closed."


                elif interaction_type == 'screen_transition':
                    print(f"DEBUG: RT: Screen Transition")
                    screen = self.current_building.get('screen')
                    
                    if screen and controller:
                        # CHECK: Is this screen actually implemented?
                        if hasattr(controller, 'screen_manager') and screen in controller.screen_manager.render_functions:
                            # Screen exists, proceed with transition
                            controller.event_manager.emit("SCREEN_CHANGE", {
                                'target_screen': screen,
                                'source': 'town_navigation'
                            })
                        else:
                            # Screen not implemented yet - show contextual message
                            self.showing_temp_message = True
                            self.temp_message_timer = pygame.time.get_ticks()
                            
                            # Contextual messages based on screen type
                            if screen == 'world_map':
                                self.temp_message_text = "The town gates are sealed. The guards won't let anyone leave right now."
                            elif screen == 'act_two_start':  
                                if not game_state.mayor_talked or not game_state.quest_active:
                                    self.temp_message_text = "You should speak with the Mayor before venturing beyond the walls."
                                else:
                                    # This shouldn't happen since screen is registered, but just in case
                                    self.temp_message_text = "The investigation begins..."
                            else:
                                self.temp_message_text = "Sorry, it's closed."
                elif interaction_type == 'combat':
                    print(f"DEBUG: RT: Combat Trigger")
                    combat_encounter = self.current_building.get('combat_encounter')
                    combat_context = self.current_building.get('combat_context', {})
                    
                    if combat_encounter and controller:
                        # Store combat data in game state (BaseLocation pattern)
                        print(f"🗡️ Starting combat: {combat_encounter}")
                        game_state.previous_screen = game_state.screen
                        game_state.current_combat_encounter = combat_encounter
                        if combat_context:
                            game_state.combat_context = combat_context
                        
                        # Navigate to combat screen
                        controller.event_manager.emit("SCREEN_CHANGE", {
                            'target_screen': 'combat',
                            'source': 'town_navigation'
                        })
                    else:
                        # Fallback if combat data missing
                        self.showing_temp_message = True
                        self.temp_message_timer = pygame.time.get_ticks()
                        self.temp_message_text = "The area is too dangerous to enter right now."

                else:
                    # Default closed message
                    print(f"DEBUG: RT: Sorry it is closed message!")
                    self.showing_temp_message = True
                    self.temp_message_text = "Sorry, it is closed."
                    self.temp_message_timer = pygame.time.get_ticks()
            
            elif self.current_npc and self.can_interact_npc:
                # NPC dialogue trigger
                npc_id = self.current_npc['dialogue_id']
                if controller:
                    # Construct screen name for checking: location_npcid pattern
                    location = 'redstone_town'
                    screen_name = f"{location}_{npc_id}"
                    
                    # Check if dialogue screen exists
                    if hasattr(controller, 'screen_manager') and screen_name in controller.screen_manager.render_functions:
                        # Dialogue exists - proceed
                        # IMPORTANT: Pass BASE location, not full screen name!
                        controller.event_manager.emit("NPC_CLICKED", {
                            'npc_id': npc_id,
                            'location': location  # Just 'redstone_town', not 'redstone_town_henrik'
                        })
                        
                        # Mark as talked
                        
                        get_world_npc_spawner().mark_npc_talked(npc_id, game_state)
                    else:
                        # NPC dialogue not implemented yet - use placeholder from data
                        self.showing_temp_message = True
                        self.temp_message_timer = pygame.time.get_ticks()
                        
                        # Get message from NPC data (data-driven!)
                        self.temp_message_text = self.current_npc.get(
                            'general_response',
                            f"{self.current_npc.get('display_name', 'NPC')} doesn't seem interested in talking."
                        )
        
    def render(self, surface, fonts, game_state):
        """Render town navigation screen"""
        surface.fill(BLACK)
                
        # Draw party status panel
        draw_party_status_panel(surface, game_state, fonts)
        
        # Draw map area border
        draw_border(surface, 0, LAYOUT_IMAGE_Y, 
                   self.renderer.display_width, self.renderer.display_height)
        
        # Create map surface and draw using shared renderer
        map_surface = surface.subsurface(6, LAYOUT_IMAGE_Y + 6,
                                        self.renderer.display_width - 12, 
                                        self.renderer.display_height - 12)
        
        # Draw the map (tiles and buildings)
        self.renderer.draw_map(map_surface, fonts, game_state.town_player_x, game_state.town_player_y, surface)
        
        # Draw NPCs (above tiles, below player)
        self.renderer.draw_npcs(map_surface, 'redstone_town', game_state)

        # Draw player (always on top)
        self.renderer.draw_player(map_surface, game_state.town_player_x, game_state.town_player_y)
        
        # Draw enhanced debug info with entrance information
        building_for_debug = self.current_building if self.can_interact else None
        self.renderer.draw_debug_with_entrance_info(
            surface, fonts, 
            game_state.town_player_x, game_state.town_player_y,
            building_for_debug, self.required_direction
        )

        # Draw interaction prompts
        if self.showing_temp_message:
            still_showing = self.renderer.draw_temp_message(
                surface, fonts, self.temp_message_text, self.temp_message_timer
            )
            if not still_showing:
                self.showing_temp_message = False
        else:
            # Show building or NPC interaction prompt
            if self.can_interact and self.current_building:
                building_name = self.current_building.get('name')
                self.renderer.draw_interaction_prompt(surface, fonts, building_name, True)
            elif self.can_interact_npc and self.current_npc:
                npc_name = self.current_npc.get('display_name')
                prompt_text = f"Talk to {npc_name}"
                self.renderer.draw_interaction_prompt(surface, fonts, prompt_text, True)
            else:
                self.renderer.draw_interaction_prompt(surface, fonts, None, False)
        
        # Instructions
        #=== DIALOG ZONE (FULL SCREEN WIDTH) ===
        dialog_y = LAYOUT_DIALOG_Y
        dialog_height = LAYOUT_DIALOG_HEIGHT
        dialog_margin = 0

        # Use full 1024 width for dialog box
        draw_border(surface, dialog_margin, dialog_y, 1024 - (dialog_margin * 2), dialog_height) 
        
        instructions = [
            "Use ARROW KEYS or WASD to move around town",
            "Press ENTER near buildings to enter them",
        ]
        text_y = dialog_y + 20
        for instruction in instructions:
            draw_centered_text(surface, instruction, fonts.get('fantasy_small', fonts['normal']),
                             text_y, WHITE)
            text_y += 25
        
        return {}

# Integration function for ScreenManager
_town_navigation_instance = None

def render_town_navigation(surface, game_state, fonts, images, controller=None):
    """ScreenManager integration function"""
    global _town_navigation_instance
    
    if _town_navigation_instance is None:
        _town_navigation_instance = RedstoneTownNavigation()
    
    # Handle input
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _town_navigation_instance.update(dt, keys, game_state, controller)
    
    # Render
    return _town_navigation_instance.render(surface, fonts, game_state)