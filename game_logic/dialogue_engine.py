# game_logic/dialogue_engine.py
"""
Dialogue Engine - Professional Conversation Management System
Following Single Data Authority Pattern established in the project

GameState = THE authoritative data source for all conversation flags
DialogueEngine = Pure business logic for conversation flow and quest triggers
JSON Files = Data-driven conversation content 

Key Features:
- Branching dialogue trees with player choice consequences
- Quest event hooks for integration with future QuestEngine
- State-dependent conversations based on game progression
- Professional conversation flow management
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from utils.narrative_schema import narrative_schema
from utils.xp_manager import XPManager

class DialogueEngine:
    """
    Professional dialogue management following Single Data Authority pattern
    
    This engine handles ALL conversation-related business logic:
    - Branching dialogue trees with player choices
    - Quest trigger events and flag management
    - State-dependent conversation flow
    - NPC personality and relationship tracking
    
    GameState remains THE single source of truth for all conversation flags.
    DialogueEngine provides pure conversation flow logic.
    """
    
    def __init__(self, game_state, item_manager):
        """Initialize DialogueEngine with GameState authority"""
        self.game_state = game_state
        self.item_manager = item_manager
        self.dialogues = {}  # Loaded dialogue trees
        self.dialogue_metadata = {} # Store object/npc metatdata for UI Rendering
        self.quest_event_hooks = []  # Future QuestEngine integration
        self.event_manager = None 
        self.dialogue_source_screen = None  # Track where dialogue came from
        self.current_dialogue_npc = None


        print("🗣️ DialogueEngine initialized with GameState authority")
    
    def load_dialogue_file(self, dialogue_id: str) -> bool:
        """
        Load dialogue tree from JSON file
        
        Args:
            dialogue_id: Name of dialogue file (e.g., 'tavern_garrick')
            
        Returns:
            bool: True if loaded successfully
        """
        #print(f"🔍 LOAD DEBUG: Attempting to load dialogue file: {dialogue_id}")
        #print(f"🔍 LOAD DEBUG: Current dialogues cache: {list(self.dialogues.keys())}")
    
        try:
            file_path = os.path.join('data', 'dialogues', f'{dialogue_id}.json')
            #print(f"🔍 LOAD DEBUG: File path: {file_path}")
            if not os.path.exists(file_path):
                print(f"⚠️ Dialogue file not found: {file_path}")
                return False
                
            with open(file_path, 'r', encoding="utf-8") as f:
                dialogue_data = json.load(f)
            
            # Extract the inner dialogue tree (skip outer wrapper key)
            # JSON structure: { "dialogue_id": { "npc_name": ..., "states": {...} } }
            # We need to store the inner object, not the wrapper
            dialogue_root = dialogue_data.get(dialogue_id, dialogue_data)
            self.dialogues[dialogue_id] = dialogue_root
            
            #Extract and store metadata for UI rendering
            metadata = {
                'is_object': dialogue_root.get('is_object', False),
                'hide_portrait': dialogue_root.get('hide_portrait', False),
                'display_name': dialogue_root.get('npc_name', dialogue_id.replace('_', ' ').title()),
                'object_icon': dialogue_root.get('object_icon', None)  # Optional custom icon
            }
            
            self.dialogue_metadata[dialogue_id] = metadata
            
            # Debug log for object examinations
            if metadata['is_object']:
                print(f"📦 Loaded object examination: {dialogue_id} (is_object={metadata['is_object']})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading dialogue {dialogue_id}: {e}")
            return False
    
    def get_current_dialogue_state(self, npc_id: str) -> str:
        """Determine current dialogue state for NPC using narrative schema"""
        
        # Check for stored dialogue state first (from recent transitions)
        stored_state_attr = f'{npc_id}_dialogue_state'
        stored_state = getattr(self.game_state, stored_state_attr, None)
        in_progress = getattr(self.game_state, f'{npc_id}_dialogue_in_progress', False)
        
        if in_progress and stored_state:
            return stored_state
        
        # Use narrative schema dialogue state mapping
        dialogue_states = narrative_schema.schema.get('dialogue_state_mapping', {})
        npc_states = dialogue_states.get(npc_id, {})
        if not npc_states:
            return 'first_meeting'
        
       # Create evaluation context with current game state
        context = {}
        for flag_name in narrative_schema.get_all_flags():
            context[flag_name] = getattr(self.game_state, flag_name, False)
        
        #print(f"🔑 Context flags for {npc_id}: refugee_camp_defended={context.get('refugee_camp_defended', 'MISSING')}, refugee_leader_talked={context.get('refugee_leader_talked', 'MISSING')}, refugee_combat_rewarded={context.get('refugee_combat_rewarded', 'MISSING')}")

        if hasattr(self.game_state, 'character'):
            for key, value in self.game_state.character.items():
                # Add any boolean flags from character dict to context
                if isinstance(value, bool) and key.startswith('is_'):
                    context[key] = value

        # Add computed properties to context
        context['recruited_count'] = getattr(self.game_state, 'recruited_count', 0)
        context['can_recruit_more'] = getattr(self.game_state, 'can_recruit_more', True)
        
        # CRITICAL: If dialogue in progress, temporarily override talked flag
        in_progress = getattr(self.game_state, f'{npc_id}_dialogue_in_progress', False)
        talked_flag = narrative_schema.get_npc_conversation_flag(npc_id)

        if in_progress and not getattr(self.game_state, talked_flag, False):
            # Only override if this is truly the first conversation
            context[talked_flag] = False
            #print(f"DEBUG: Dialogue in progress for {npc_id}, overriding {talked_flag} to False")
        
        # Evaluate each state condition
        #print(f"🔍 DE: Evaluating {len(npc_states)} states for npc_id='{npc_id}'")
        #print("DE: STATE-EVAL ORDER:", list(npc_states.keys()))

        # Show key flag values for mayor
        #if npc_id == 'mayor':
            #print(f"  🔑 KEY FLAGS: act_two_started={context.get('act_two_started')}, mayor_talked={context.get('mayor_talked')}")
            #print(f"  🔑 COMPLETIONS: swamp={context.get('swamp_church_complete')}, ruins={context.get('hill_ruins_complete')}, refugee={context.get('refugee_camp_complete')}")
            #print(f"  🔑 ACKNOWLEDGED: swamp={context.get('mayor_acknowledged_swamp_complete')}, ruins={context.get('mayor_acknowledged_ruins_complete')}, refugee={context.get('mayor_acknowledged_refugee_complete')}")


        for state_name, condition in npc_states.items():
            result = self._evaluate_condition(condition, context)
            #print(f"  📊 {state_name}: '{condition}' = {result}")
            if self._evaluate_condition(condition, context):
                #print(f"✅ DE: MATCH -> {state_name}")
                return state_name
        
        print("❌ DE: No match found, defaulting to first_meeting")
        return 'first_meeting'

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        """Evaluate dialogue state condition string"""
        try:
            # Replace operators
            condition = condition.replace('!', 'not ').replace('&&', ' and ').replace('||', ' or ')
            
            # Safely evaluate
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
           # print(f"DEBUG: Condition evaluation failed: {condition}, error: {e}")
            return False

    def _sync_party_members_list(self):
        """Sync party_members list with recruitment flags for UI systems"""
        # Get all recruitment flags from narrative schema
        from utils.narrative_schema import narrative_schema
        recruitment_flags = narrative_schema.schema.get("recruitment_system", {}).get("recruitment_flags", [])
        
        # Build party_members list from active recruitment flags
        party_members = []
        for flag in recruitment_flags:
            if getattr(self.game_state, flag, False):
                # Convert flag name to NPC ID (gareth_recruited -> gareth)
                npc_id = flag.replace('_recruited', '')
                party_members.append(npc_id)
        
        # Update party_members list
        self.game_state.party_members = party_members
        print(f"🔄 Synced party_members: {party_members}")
        
        # Also sync character data
        self.game_state.sync_party_member_data()
        
        #Update quest system when flags change
        if hasattr(self.game_state, 'quest_manager'):
            self.game_state.quest_manager.update_from_game_state()
            print("📋 Quest system updated after flag changes")

    def _check_single_trigger(self, trigger_name, trigger_data, xp_manager):
        """Check a single narrative trigger for XP award"""
        dialogue_flag = trigger_data.get('dialogue_flag')
        xp_reward_key = trigger_data.get('xp_reward')
        event_type = trigger_data.get('event_type')
        
        if not all([dialogue_flag, xp_reward_key, event_type]):
            return
        
        # Check if flag is set and XP not already awarded
        flag_set = getattr(self.game_state, dialogue_flag, False)
        xp_awarded = getattr(self.game_state, f"{dialogue_flag}_xp_awarded", False)
        
        if flag_set and not xp_awarded:
            xp_amount = xp_manager.get_reward(xp_reward_key)
            
            if self.event_manager and xp_amount > 0:
                self.event_manager.emit("XP_AWARDED", {
                    'amount': xp_amount,
                    'reason': f"{event_type.lower()}: {trigger_name}"
                })
            
            setattr(self.game_state, f"{dialogue_flag}_xp_awarded", True)
            print(f"⚡ Event XP awarded: {xp_amount} for {trigger_name}")



    def get_conversation_options(self, dialogue_id: str, npc_id: str, forced_state: str = None) -> Dict[str, Any]:
        #print(f"🔍 GET_OPTIONS DEBUG: Called for {dialogue_id}, {npc_id}")
        #print(f"🔍 GET_OPTIONS DEBUG: dialogue_id in self.dialogues? {dialogue_id in self.dialogues}")
        
        if dialogue_id not in self.dialogues:
            #print(f"🔍 GET_OPTIONS DEBUG: Dialogue not in cache, attempting to load...")
            if not self.load_dialogue_file(dialogue_id):
                #print(f"🔍 GET_OPTIONS DEBUG: Load failed, using fallback")
                return self._get_fallback_dialogue(npc_id)
        #else:
            #print(f"🔍 GET_OPTIONS DEBUG: Using cached dialogue")
    
        
        """
        Get current conversation options for NPC
        
        Args:
            dialogue_id: Dialogue file identifier
            npc_id: NPC identifier
            
        Returns:
            Dict containing conversation data and options
        """
        
        # (near the top of get_conversation_options)
        temp_choices_attr = f'{npc_id}_dialogue_response_actions'
        temp_choices = getattr(self.game_state, temp_choices_attr, None)
        show_actions_flag = getattr(self.game_state, f'{npc_id}_show_action_choices', False)

        if temp_choices and show_actions_flag:
            # Convert action names to choice-like options for UI
            dialogue_data = self.dialogues.get(dialogue_id, {})
            actions_config = dialogue_data.get('actions', {})
            action_options = []
            for action_name in temp_choices:
                action_def = actions_config.get(action_name, {})
                action_options.append({
                    'id': f'action_{action_name}',
                    'text': action_def.get('text', action_name.replace('_', ' ').title()),
                    'description': action_def.get('description', ''),
                    'action_name': action_name,
                    'is_action_choice': True
                })
            return {
                'npc_name': dialogue_data.get('npc_name', npc_id.title()),
                'description': dialogue_data.get('description', ''),
                'introduction': [f"*{dialogue_data.get('npc_name', npc_id.title())} waits for your response*"],
                'options': action_options,
                'current_state': 'action_choices'
            }
        # NOTE: if temp_choices exist but show_actions_flag is False,
        # we fall through to normal state-driven options (exactly what we want after Back).

       
        if dialogue_id not in self.dialogues:
            if not self.load_dialogue_file(dialogue_id):
                return self._get_fallback_dialogue(npc_id)
        
        dialogue_tree = self.dialogues[dialogue_id]
        
        # For object examinations, use initial_state from JSON instead of narrative schema
        if dialogue_tree.get('is_object', False):
            # Objects use initial_state from their JSON (e.g., "examine")
            current_state = forced_state or dialogue_tree.get('initial_state', 'examine')
        else:
            # NPCs use narrative schema state mapping
            current_state = forced_state or self.get_current_dialogue_state(npc_id)

        if current_state in dialogue_tree.get('states', {}):
            state_data = dialogue_tree['states'][current_state]
            
            # After determining current_state, add this:
            #print(f"🎯 DEBUG: get_conversation_options for {npc_id}")
            #print(f"🎯 DEBUG: dialogue_id: {dialogue_id}")
            #print(f"🎯 DEBUG: determined state: {current_state}")
            #print(f"🎯 DEBUG: state_data options: {state_data.get('options', [])}")

            # Filter options based on requirements (if any)
            available_options = []
            for option in state_data.get('options', []):
                if self._check_option_requirements(option):
                    available_options.append(option)
            
            return {
                'npc_name': dialogue_tree.get('npc_name', npc_id.title()),
                'introduction': state_data.get('introduction', []),
                'options': available_options,
                'default_actions': state_data.get('default_actions', [])
            }
        
        return self._get_fallback_dialogue(npc_id)

    def register_event_handlers(self, event_manager):
        """Register dialogue event handlers with EventManager"""
        #STORE the event_manager reference
        self.event_manager = event_manager
        
        event_manager.register("DIALOGUE_CHOICE", self._handle_dialogue_choice)
        event_manager.register("DIALOGUE_ACTION", self._handle_dialogue_action)
        print("🎭 DialogueEngine event handlers registered")

    def _handle_dialogue_choice(self, event_data):
        """Handle DIALOGUE_CHOICE events"""
        print(f"🎭 DEBUG: DialogueEngine received DIALOGUE_CHOICE event: {event_data}")
        
        npc_id = event_data.get('npc_id')
        choice_index = event_data.get('choice_index')
        
        if npc_id and choice_index is not None:
            print(f"🎭 DEBUG: Processing choice {choice_index} for {npc_id}")
            

            # Get stored location - REQUIRED, no hardcoding
            location_id = getattr(self.game_state, f'{npc_id}_current_location', None)
            if not location_id:
                raise ValueError(f"No location set for {npc_id} dialogue session - location must be set before dialogue begins")
            
            dialogue_file_id = f'{location_id}_{npc_id}'
            print(f"🎭 DEBUG: Looking for dialogue file: {dialogue_file_id}")
            
            # Load dialogue if needed
            if dialogue_file_id not in self.dialogues:
                self.load_dialogue_file(dialogue_file_id)
            
            dialogue_tree = self.dialogues.get(dialogue_file_id, {})
            
            # Get metadata first to determine state handling
            metadata = self.get_dialogue_metadata(dialogue_file_id)
            is_object = metadata.get('is_object', False)
            
            #  Determine current state BEFORE getting conversation options
            if is_object:
                stored_state_attr = f'{npc_id}_dialogue_state'
                stored_state = getattr(self.game_state, stored_state_attr, None)
                in_progress = getattr(self.game_state, f'{npc_id}_dialogue_in_progress', False)
                
                if in_progress and stored_state:
                    current_state = stored_state  # Use the stored state for subsequent choices
                    print(f"🎯 DEBUG: Using stored state for object: {current_state}")
                else:
                    current_state = dialogue_tree.get('initial_state', 'examine')
                    print(f"🎯 DEBUG: Using initial state for object: {current_state}")
            else:
                current_state = self.get_current_dialogue_state(npc_id)
                print(f"🎯 DEBUG: Using narrative schema state for NPC: {current_state}")
            
            # NOW get conversation options with the correct state
            conversation_data = self.get_conversation_options(dialogue_file_id, npc_id, forced_state=current_state)
            options = conversation_data.get('options', [])
            
            print(f"🎯 DEBUG: Got {len(options)} options for state '{current_state}'")

            if choice_index < len(options):
                choice_id = options[choice_index]['id']
                print(f"🎭 DEBUG: Selected option ID: {choice_id}")
                
                # NARRATIVE SCHEMA INTEGRATION - Set conversation flag AFTER state determination
                conv_flag = narrative_schema.get_npc_conversation_flag(npc_id)
                setattr(self.game_state, conv_flag, True)
                print(f"✅ Set conversation flag: {conv_flag} = True")

                # Track NPC encounter for statistics
                if npc_id not in self.game_state.npcs_encountered:
                    if not is_object:
                        # This is an actual NPC conversation
                        self.game_state.npcs_encountered.add(npc_id)
                        self.game_state.player_statistics['npcs_met'] += 1
                        print(f"📊 New NPC met: {npc_id} (Total: {self.game_state.player_statistics['npcs_met']})")
                    else:
                        # This is an object examination - track separately
                        if not hasattr(self.game_state, 'objects_examined'):
                            self.game_state.objects_examined = set()
                        
                        if npc_id not in self.game_state.objects_examined:
                            self.game_state.objects_examined.add(npc_id)
                            
                            # Initialize counter if needed
                            if 'objects_examined' not in self.game_state.player_statistics:
                                self.game_state.player_statistics['objects_examined'] = 0
                            
                            self.game_state.player_statistics['objects_examined'] += 1
                            print(f"🔍 Examined object: {npc_id} (Total objects: {self.game_state.player_statistics['objects_examined']})")

                # Call existing business logic method (pass current_state as forced_state for consistency)
                result = self.process_dialogue_choice(dialogue_file_id, npc_id, choice_id, current_state)
                
                #Get metadata for response screen (needs to know if object)
                metadata = self.get_dialogue_metadata(dialogue_file_id)
                
                if result:
                    # Handle conversation ending through event system
                    if result.get('conversation_ended'):
                        # Clear metadata since conversation is ending
                        conversation_attr = f'{npc_id}_conversation_data'
                        setattr(self.game_state, conversation_attr, None)
                        
                        self.event_manager.emit("DIALOGUE_ENDED", {
                            'npc_id': npc_id,
                            'return_to': result.get('return_to', 'location')
                        })
                        return result
                    elif result.get('new_conversation'):
                        new_conv = result['new_conversation']
                        # Inject metadata into new conversation data
                        new_conv['is_object'] = metadata.get('is_object', False)
                        new_conv['object_icon'] = metadata.get('object_icon', None)
                        setattr(self.game_state, f'{npc_id}_conversation_data', new_conv)
                        return result
                    else:
                        # Fallback for old response format
                        response_lines = result.get('response', [])
                        setattr(self.game_state, f'{npc_id}_dialogue_response', response_lines)
                        setattr(self.game_state, f'showing_{npc_id}_response', True)
                        
                        # Store metadata for response screen
                        conversation_attr = f'{npc_id}_conversation_data'
                        conversation_data = {
                            'is_object': metadata.get('is_object', False),
                            'object_icon': metadata.get('object_icon', None),
                            'display_name': metadata.get('display_name', npc_id.title())
                        }
                        setattr(self.game_state, conversation_attr, conversation_data)
                        
                        return result
            else:
                print(f"❌ DEBUG: Invalid choice index {choice_index} for {npc_id} (only {len(options)} options available)")
                return None
        else:
            print(f"❌ DEBUG: Missing npc_id ({npc_id}) or choice_index ({choice_index}) in event data")
            return None
            
    def _handle_dialogue_action(self, event_data):
        """Handle DIALOGUE_ACTION events"""
        npc_id = event_data.get('npc_id')
        action_name = event_data.get('action_name')
        
        if npc_id and action_name:
            print(f"🎭 Processing dialogue action: {npc_id}, {action_name}")
            
            if action_name == 'back':
                # RETURN TO CHOICE LIST (stay in conversation)
                showing_response_attr = f'showing_{npc_id}_response'
                setattr(self.game_state, showing_response_attr, False)

                # Clear response text
                response_attr = f'{npc_id}_dialogue_response'
                setattr(self.game_state, response_attr, [])

                # CRITICAL: clear any leftover response-actions and disable their gate
                temp_choices_attr = f'{npc_id}_dialogue_response_actions'
                setattr(self.game_state, temp_choices_attr, None)
                setattr(self.game_state, f'{npc_id}_show_action_choices', False)

                
                # CRITICAL: Don't exit to screen - stay in dialogue for state transition
                #print(f"DEBUG: Staying in dialogue, state may have changed for {npc_id}")

            # Also add this case for Enter/Continue:
            elif action_name in ['continue', 'goodbye']:
                if action_name == 'continue':
                    # Check if we're in a state transition scenario
                    showing_response_attr = f'showing_{npc_id}_response'
                    response_actions_attr = f'{npc_id}_dialogue_response_actions'
                    
                    # Get the actions that were available from the response
                    response_actions = getattr(self.game_state, response_actions_attr, [])
                    
                    # Clear response state to prepare for new choices
                    setattr(self.game_state, showing_response_attr, False)
                    setattr(self.game_state, f'{npc_id}_dialogue_response', [])
                    
                    # If there are response actions, convert them to choices
                    if response_actions:
                        location_id = getattr(self.game_state, f'{npc_id}_current_location')
                        dialogue_file_id = f'{location_id}_{npc_id}'
                        dialogue_data = self.dialogues.get(dialogue_file_id, {})
                        actions_config = dialogue_data.get('actions', {})
                        
                        # Check if any response actions exist (regardless of type)
                        has_valid_actions = False
                        for action_name in response_actions:
                            action_def = actions_config.get(action_name, {})
                            if action_def:  # Any action with a definition is valid
                                has_valid_actions = True
                                break
                        
                        if has_valid_actions:
                            # Convert response actions to temporary choices for the current state
                            print(f"DEBUG: Converting {len(response_actions)} actions to choices for {npc_id}")
                            
                            # Store the actions as temporary choices to be rendered
                            temp_choices_attr = f'{npc_id}_dialogue_response_actions'
                            setattr(self.game_state, temp_choices_attr, response_actions)
                            
                            print(f"DEBUG: Continue pressed - showing action choices for {npc_id}")
                            return  # Stay in dialogue, let UI render the action choices
                    
                    # If no valid actions, treat as normal continue
                    print(f"DEBUG: No valid actions found, treating as normal continue")
                
                else:  # action_name == 'goodbye'
                    # Actual goodbye - exit dialogue entirely
                    setattr(self.game_state, f'showing_{npc_id}_response', False)
                    setattr(self.game_state, f'{npc_id}_dialogue_response', [])
                    setattr(self.game_state, f'{npc_id}_dialogue_in_progress', False)
                    setattr(self.game_state, f'{npc_id}_dialogue_state', None)
                    setattr(self.game_state, f'{npc_id}_conversation_data', None)

                    # Navigate back to previous screen
                    if self.event_manager:
                        screen_manager_service = self.event_manager.get_service('screen_manager')
                        if screen_manager_service and hasattr(screen_manager_service, 'input_handler'):
                            state_flag = f'showing_{npc_id}_response'
                            screen_manager_service.input_handler.unregister_dialogue_state(state_flag)

                        target_screen = None
                        prev = None
                        current_screen = getattr(self.game_state, 'screen', None)

                        if self.event_manager:
                            sm = self.event_manager.get_service('screen_manager')
                            if sm and hasattr(sm, 'previous_screen'):
                                prev = getattr(sm, 'previous_screen', None)

                        dialogue_screen_name = f"{getattr(self.game_state, f'{npc_id}_current_location', '')}_{npc_id}"
                        if prev and prev != current_screen and prev != dialogue_screen_name:
                            target_screen = prev

                        if not target_screen:
                            # Strategy 1: Use stored return screen (set when dialogue started)
                            return_screen_attr = f'{npc_id}_return_screen'
                            stored_return = getattr(self.game_state, return_screen_attr, None)
                            
                            if stored_return:
                                target_screen = stored_return
                                print(f"🔙 Using stored return screen: {target_screen}")
                            else:
                                # Strategy 2: Try ScreenManager's previous_screen
                                if self.event_manager:
                                    sm = self.event_manager.get_service('screen_manager')
                                    if sm and hasattr(sm, 'previous_screen'):
                                        prev = getattr(sm, 'previous_screen', None)
                                        dialogue_screen_name = f"{getattr(self.game_state, f'{npc_id}_current_location', '')}_{npc_id}"
                                        
                                        if prev and prev != dialogue_screen_name:
                                            target_screen = prev
                                
                                # Strategy 3: Fallback to location_id (works for single-area locations)
                                if not target_screen:
                                    location_id = getattr(self.game_state, f'{npc_id}_current_location', None)
                                    if location_id:
                                        target_screen = location_id

                        if target_screen:
                            self.event_manager.emit('SCREEN_CHANGE', {
                                'target_screen': target_screen,
                                'source_screen': f'{npc_id}_dialogue'
                            })

    def process_dialogue_choice(self, dialogue_id: str, npc_id: str, choice_id: str, forced_state: str = None) -> Dict[str, Any]:
        """
        Process player's dialogue choice and return response
        
        Args:
            dialogue_id: Dialogue file identifier  
            npc_id: NPC identifier
            choice_id: Selected choice identifier
            
        Returns:
            Dict containing NPC response and any triggered effects
        """
        # DEBUG: Check what conversation data exists
        stored_conversation_attr = f'{npc_id}_conversation_data'
        stored_data = getattr(self.game_state, stored_conversation_attr, None)
        #print(f"🔍 DEBUG: Stored conversation data for {npc_id}: {stored_data}")
        
        # DEBUG: Check current state vs what UI thinks
        current_state = self.get_current_dialogue_state(npc_id)
        #print(f"🔍 DEBUG: DE: Current calculated state: {current_state}")
        #print(f"🔍 DEBUG: DE: Forced state: {forced_state}")
        #print(f"🔍 DEBUG: DE: Choice ID from UI: {choice_id}")
        
        #print(f"🔧 DEBUG PROCESS: Called with forced_state={forced_state}")
        #print(f"DEBUG: DE: Processing choice {choice_id} for {npc_id}")

        # Clear temporary action choices when a choice is made
        temp_choices_attr = f'{npc_id}_dialogue_response_actions'
        if hasattr(self.game_state, temp_choices_attr):
            setattr(self.game_state, temp_choices_attr, None)
            #print(f"DEBUG: DE: Cleared temporary action choices for {npc_id}")

        try:
            if dialogue_id not in self.dialogues:
                return {'response': ["I don't understand."], 'effects': []}
            
            dialogue_tree = self.dialogues[dialogue_id]
            actions_config = dialogue_tree.get('actions', {})
            
            # Check if this is an action choice (from response actions)
            if choice_id.startswith('action_'):
                action_name = choice_id.replace('action_', '')
                action_def = actions_config.get(action_name, {})
                
                if action_def.get('type') == 'dialogue_branch':
                    target_state = action_def.get('target_state')
                    
                    if target_state:
                        # Set the new dialogue state
                        state_attr = f'{npc_id}_dialogue_state'
                        setattr(self.game_state, state_attr, target_state)
                        #print(f"DEBUG: DE: Action choice triggered state transition: {npc_id} -> {target_state}")
                        
                        # CRITICAL FIX: Clear response state to force dialogue reload
                        setattr(self.game_state, f'showing_{npc_id}_response', False)
                        setattr(self.game_state, f'{npc_id}_dialogue_response', [])
                        
                        # Return minimal response to signal state change
                        return {
                            'response': [],  # Empty response forces dialogue reload
                            'effects': [],
                            'state_changed': True,
                            'target_state': target_state,
                            'reload_dialogue': True
                        }
                
                # Handle actions with custom responses
                if 'response' in action_def:
                    # Process action effects
                    effects = []
                    for effect in action_def.get('effects', []):
                        effect_result = self._apply_dialogue_effect(effect)
                        if effect_result:
                            effects.append(effect_result)
                    
                    return {
                        'response': action_def.get('response', ["I see."]),
                        'effects': effects,
                        'action_complete': True
                    }

                # Fallback for actions without responses
                return {'response': ["I see."], 'effects': []}
            
            # Handle normal dialogue choices
            # For objects, check stored state first before falling back to initial_state
            if dialogue_tree.get('is_object', False):
                # Check if there's an active dialogue session with a stored state
                stored_state_attr = f'{npc_id}_dialogue_state'
                stored_state = getattr(self.game_state, stored_state_attr, None)
                in_progress = getattr(self.game_state, f'{npc_id}_dialogue_in_progress', False)
                
                if in_progress and stored_state and not forced_state:
                    # Mid-dialogue: use the stored state
                    current_state = stored_state
                else:
                    # First interaction OR explicit forced_state
                    current_state = forced_state or dialogue_tree.get('initial_state', 'examine')
            else:
                # NPCs use narrative schema state mapping
                current_state = forced_state or self.get_current_dialogue_state(npc_id)

            if current_state not in dialogue_tree.get('states', {}):
                return {'response': ["I don't understand."], 'effects': []}
            
            state_data = dialogue_tree['states'][current_state]
            
            # Find the selected choice
            selected_choice = None
            for option in state_data.get('options', []):
                if option.get('id') == choice_id:
                    selected_choice = option
                    break
            
            if not selected_choice:
                return {'response': ["I don't understand."], 'effects': []}
            
            #print(f"DEBUG: DE: Selected choice = {selected_choice}")

            # Process effects immediately when choice is selected
            effects_processed = []
            for effect in selected_choice.get('effects', []):
                effect_result = self._apply_dialogue_effect(effect, npc_id)
                
                # If remove_item fails, stop processing remaining effects
                if effect.get('type') == 'remove_item' and effect_result is None:
                    print(f"❌ CRITICAL: remove_item failed, aborting remaining effects")
                    return {
                        'response': ["You don't have the required items."],
                        'effects': effects_processed,
                        'effect_failed': True
                    }
                
                if effect_result:
                    effects_processed.append(effect_result)

            # Handle next state - simplified direct transition
            next_state = selected_choice.get('next_state')

            if next_state == 'exit':
                # End conversation and return to location
                
                # ADD THIS: Clear stored dialogue state so next conversation evaluates fresh
                state_attr = f'{npc_id}_dialogue_state'
                setattr(self.game_state, state_attr, None)
                
                # ALSO clear stored conversation data
                conversation_attr = f'{npc_id}_conversation_data'
                setattr(self.game_state, conversation_attr, None)
                #print(f"🧹 DE: PDC: Cleared dialogue state and conversation data for {npc_id}")
                
                self._clear_conversation_state(npc_id)
                return {
                    'conversation_ended': True,
                    'effects': effects_processed,
                    'return_to': 'location'
                }

            if next_state:
                # Transition to new dialogue state
                state_attr = f'{npc_id}_dialogue_state'
                setattr(self.game_state, state_attr, next_state)
                
                # Add this debug:
                actual_state = getattr(self.game_state, state_attr)
                #print(f"DE: STATE UPDATE CHECK: {npc_id} should be {next_state}, actually is {actual_state}")
    
               # Get new conversation data for the NEW state after transition
                if next_state and next_state != 'exit':
                    new_conversation = self.get_conversation_options(dialogue_id, npc_id, forced_state=next_state)
                else:
                    new_conversation = self.get_conversation_options(dialogue_id, npc_id, forced_state=current_state)
                
                return {
                    'new_conversation': new_conversation,
                    'effects': effects_processed,
                    'state_changed': True
                }

            # No next_state means stay in current conversation
            return {
                'effects': effects_processed,
                'continue_dialogue': True
            }
            
        except Exception as e:
            print(f"DE: ERROR in process_dialogue_choice: {e}")
            import traceback
            traceback.print_exc()
            return {'response': ["Something went wrong."], 'effects': []}
    
    def _apply_dialogue_effect(self, effect: Dict[str, Any], npc_id: str = None) -> Optional[str]:
        """Apply dialogue choice effects to GameState; emit neutral events for QuestEngine."""
        # 0) Defensive checks
        if not effect or not isinstance(effect, dict):
            print(f"WARNING: Invalid effect data: {effect}")
            return None

        effect_type = effect.get('type')
        if not effect_type:
            print(f"WARNING: Effect missing type: {effect}")
            return None

        # 1) set_flag  -------------------------------------------------------------
        if effect_type == 'set_flag':
            flag_name = effect.get('flag')
            if not flag_name:
                print(f"WARNING: set_flag effect missing flag name: {effect}")
                return None

            value = effect.get('value', True)
            setattr(self.game_state, flag_name, value)
            print(f"✅ Set flag: {flag_name} = {value}")

            # (A) Keep party list accurate locally (no XP logic here)
            if flag_name.endswith('_recruited'):
                try:
                    self._sync_party_members_list()
                except Exception as e:
                    print(f"DE: party sync failed after {flag_name}: {e}")

            # (B) Emit neutral events so QuestEngine can react
            if self.event_manager:
                try:
                    self.event_manager.emit("FLAG_CHANGED", {"flag": flag_name, "value": value, "source": "dialogue"})
                    if flag_name.endswith('_recruited') and value:
                        member = flag_name.split("_")[0]
                        self.event_manager.emit("PARTY_MEMBER_RECRUITED", {"member_id": member, "member": member, "source": "dialogue"})
                    print(f"[DBG] EMIT FLAG_CHANGED {flag_name}={value}")
                
                except Exception as e:
                    print(f"DE: event emit failed for {flag_name}: {e}")

            return f"Set {flag_name} = {value}"

        # 2) quest_trigger  --------------------------------------------------------
        elif effect_type == 'quest_trigger':
            # Leave as-is; emit a neutral quest event (no XP calculation here)
            quest_event = {
                'type': 'quest_trigger',
                'quest_id': effect.get('quest_id'),
                'trigger_type': effect.get('trigger_type', 'start'),
                'data': effect.get('data', {})
            }
            self._emit_quest_event(quest_event)
            return f"Quest trigger: {effect.get('quest_id')}"

        # 3) add_location  ---------------------------------------------------------
        elif effect_type == 'add_location':
            location = effect.get('location')
            if location and location not in self.game_state.locations_discovered:
                self.game_state.locations_discovered.append(location)
                # Emit discovery so QuestEngine can advance quests/XP
                if self.event_manager:
                    try:
                        self.event_manager.emit("LOCATION_DISCOVERED", {"location": location, "source": "dialogue"})
                    except Exception as e:
                        print(f"DE: event emit failed for LOCATION_DISCOVERED {location}: {e}")
                return f"Discovered location: {location}"

        # 4) open_shop  ------------------------------------------------------------
        elif effect_type == 'open_shop':
            merchant_id = effect.get('merchant_id')
            if not merchant_id:
                print(f"WARNING: open_shop effect missing merchant_id: {effect}")
                return None

            if self.event_manager:
                self.event_manager.emit('OPEN_SHOPPING', {
                    'merchant_id': merchant_id,
                    'source_location': getattr(self.game_state, f'{npc_id}_current_location', 'broken_blade')
                })
                return f"Opening shop for {merchant_id}"
            return None

        # 5) spend_gold  -----------------------------------------------------------
        elif effect_type == 'spend_gold':
            amount = effect.get('amount', 0)
            if amount > 0:
                current_gold = self.game_state.character.get('gold', 0)
                if current_gold >= amount:
                    self.game_state.character['gold'] = current_gold - amount
                    print(f"💰 Spent {amount} gold (was {current_gold}, now {self.game_state.character['gold']})")
                    return f"Spent {amount} gold"
                else:
                    print(f"⚠️ Not enough gold: have {current_gold}, need {amount}")
                    return None
            return None

        # 6) rest_party  -----------------------------------------------------------
        elif effect_type == 'rest_party':
            # Emit event for future rest system
            if self.event_manager:
                self.event_manager.emit('PARTY_RESTED', {'source': 'inn'})
                return "Party rested"
            return None

        # 7) advance_time  ---------------------------------------------------------
        elif effect_type == 'advance_time':
            hours = effect.get('hours', 8)
            # Emit event for time system
            if self.event_manager:
                self.event_manager.emit('TIME_ADVANCED', {
                    'hours': hours,
                    'source': 'rest'
                })
                return f"Time advanced {hours} hours"
            return None
        
        # 8) navigate  -----------------------------------------------------------
        elif effect_type == 'navigate':
            target = effect.get('target')
            
            if not target:
                print(f"WARNING: navigate effect missing target: {effect}")
                return None
            
            if self.event_manager:
                print(f"🚪 Dialogue triggering navigation to: {target}")
                # Set flag to prevent auto-return to previous screen
                self.game_state.skip_dialogue_return = True
                self.event_manager.emit('SCREEN_CHANGE', {
                    'target_screen': target,
                    'source_screen': 'dialogue'
                })
                return f"Navigating to {target}"
            return None
        
        # 9) check_location_completion  --------------------------------------------
        elif effect_type == 'check_location_completion':
            location_id = effect.get('location_id')
            
            if not location_id:
                print(f"WARNING: check_location_completion effect missing location_id: {effect}")
                return None
            
            try:
                # Use narrative schema to check if location completion requirements met
                from utils.narrative_schema import narrative_schema
                was_completed = narrative_schema.check_location_completion(location_id, self.game_state)
                
                if was_completed:
                    # Get display name for nice logging
                    location_data = narrative_schema.schema.get("locations", {}).get(location_id, {})
                    display_name = location_data.get('display_name', location_id)
                    return f"Completed exploration: {display_name}"
                else:
                    # Not yet complete - that's fine, just return None silently
                    return None
                    
            except Exception as e:
                print(f"ERROR: check_location_completion failed for {location_id}: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        # 10) add_item  -------------------------------------------------------------
        elif effect_type == 'add_item':
            item_id = effect.get('item_id')
            quantity = effect.get('quantity', 1)
            category = effect.get('category')  # Optional, auto-detected if None
            
            if not item_id:
                print(f"❌ ERROR: add_item effect missing item_id: {effect}")
                return None
            
            try:
                # Get inventory engine reference
                from game_logic.inventory_engine import get_inventory_engine
                inv_engine = get_inventory_engine()
                
                if not inv_engine:
                    print(f"❌ ERROR: InventoryEngine not available for add_item")
                    return None
                
                # Verify item exists in items.json before adding
                #from game_logic.item_manager import item_manager
                # DEBUG: Check if item_manager is loaded
                print(f"🔍 DEBUG: Checking for item '{item_id}'")
                print(f"🔍 DEBUG: item_manager.items_data has {len(self.item_manager.items_data.get('merchant_items', []))} merchant items")
                print(f"🔍 DEBUG: First 3 item IDs: {[item['id'] for item in self.item_manager.items_data.get('merchant_items', [])[:3]]}")
                
                item_data = self.item_manager.get_item_by_id(item_id)
                if not item_data:
                    print(f"❌ ERROR: Cannot add unknown item '{item_id}' - not found in items.json")
                    return None
                
                # Add the item
                success = inv_engine.add_item(item_id, quantity, category)
                
                if success:
                    # Get display name for notification
                    item_name = item_data.get('name', item_id)
                    print(f"✅ Dialogue gave player: {quantity}x {item_name} ({item_id})")
                    
                    # Show visual notification (like XP notification)
                    if self.event_manager:
                        qty_text = f"{quantity}x " if quantity > 1 else ""
                        self.event_manager.emit("SHOW_FLOATING_TEXT", {
                            "text": f"Received {qty_text}{item_name}",
                            "color": (100, 200, 255),  # Light blue for items
                            "duration": 2200
                        })
                    
                    return f"Received {item_name}"
                else:
                    print(f"❌ ERROR: Failed to add item '{item_id}' to inventory")
                    return None
                    
            except Exception as e:
                print(f"❌ EXCEPTION in add_item effect: {e}")
                import traceback
                traceback.print_exc()
                return None

        # 11) remove_item  ----------------------------------------------------------
        elif effect_type == 'remove_item':
            item_id = effect.get('item_id')
            quantity = effect.get('quantity', 1)
            
            if not item_id:
                print(f"❌ ERROR: remove_item effect missing item_id: {effect}")
                return None
            
            try:
                # Get inventory engine reference
                from game_logic.inventory_engine import get_inventory_engine
                inv_engine = get_inventory_engine()
                
                if not inv_engine:
                    print(f"❌ ERROR: InventoryEngine not available for remove_item")
                    return None
                
                # Get item data for display purposes
                item_data = self.item_manager.get_item_by_id(item_id)
                item_name = item_data.get('name', item_id) if item_data else item_id
                
                # CRITICAL: Pass item_id (not display name) to inventory_engine
                # Inventory stores items by ID, not by display name
                success = inv_engine.remove_item(item_id, quantity)
                
                if success:
                    print(f"✅ Dialogue took from player: {quantity}x {item_name} ({item_id})")
                    
                    # Show visual notification
                    if self.event_manager:
                        qty_text = f"{quantity}x " if quantity > 1 else ""
                        self.event_manager.emit("SHOW_FLOATING_TEXT", {
                            "text": f"Lost {qty_text}{item_name}",
                            "color": (255, 100, 100),
                            "duration": 2200
                        })
                    
                    return f"Lost {item_name}"
                else:
                    print(f"⚠️ WARNING: Could not remove '{item_name}' ({item_id}) - player doesn't have it")
                    return None
                    
            except Exception as e:
                print(f"❌ EXCEPTION in remove_item effect: {e}")
                import traceback
                traceback.print_exc()
                return None

        # 12) heal_party  ----------------------------------------------------------
        elif effect_type == 'heal_party':
            amount = effect.get('amount', 'full')  # Can be 'full', 'half', or a number
            
            try:
                healed_count = 0
                party_members = []
                
                # Get all party members
                if hasattr(self.game_state, 'character') and self.game_state.character:
                    party_members.append(('Player', self.game_state.character))
                
                # Add recruited companions
                companion_flags = ['gareth_recruited', 'elara_recruited', 'thorman_recruited']
                for flag in companion_flags:
                    if getattr(self.game_state, flag, False):
                        companion_name = flag.split('_')[0].capitalize()
                        companion_data = getattr(self.game_state, f'{companion_name.lower()}_character', None)
                        if companion_data:
                            party_members.append((companion_name, companion_data))
                
                # Heal each party member
                for name, char_data in party_members:
                    if 'hp' in char_data and 'max_hp' in char_data:
                        current_hp = char_data['hp']
                        max_hp = char_data['max_hp']
                        
                        if amount == 'full':
                            char_data['hp'] = max_hp
                            healed_count += 1
                        elif amount == 'half':
                            char_data['hp'] = min(max_hp, current_hp + (max_hp // 2))
                            healed_count += 1
                        elif isinstance(amount, (int, float)):
                            char_data['hp'] = min(max_hp, current_hp + amount)
                            healed_count += 1
                        
                        print(f"❤️ Healed {name}: {current_hp}/{max_hp} → {char_data['hp']}/{max_hp}")
                
                if healed_count > 0:
                    # Show visual notification
                    if self.event_manager:
                        self.event_manager.emit("SHOW_FLOATING_TEXT", {
                            "text": f"Party Healed!",
                            "color": (100, 255, 100),  # Green for healing
                            "duration": 2200
                        })
                    
                    print(f"✅ Healed {healed_count} party member(s)")
                    return f"Party healed ({healed_count} members)"
                else:
                    print(f"⚠️ No party members found to heal")
                    return None
                    
            except Exception as e:
                print(f"❌ EXCEPTION in heal_party effect: {e}")
                import traceback
                traceback.print_exc()
                return None   

        

    def _check_option_requirements(self, option: Dict[str, Any]) -> bool:
        """Check if dialogue option requirements are met"""
        requirements = option.get('requirements', {})
        
        # Check flag requirements
        flag_requirements = requirements.get('flags', {})
        for flag_name, required_value in flag_requirements.items():
            current_value = getattr(self.game_state, flag_name, False)
            if current_value != required_value:
                return False
        
        # Check single flag requirement (e.g., "flag": "some_flag_name")
        if 'flag' in requirements:
            flag_name = requirements['flag']
            if not getattr(self.game_state, flag_name, False):
                return False
        
        # Check not_flag requirement (e.g., "not_flag": "some_flag_name")
        if 'not_flag' in requirements:
            flag_name = requirements['not_flag']
            if getattr(self.game_state, flag_name, False):
                return False
        
        # Check any_flag requirement (list of flags, at least one must be true)
        if 'any_flag' in requirements:
            flag_list = requirements['any_flag']
            if not any(getattr(self.game_state, flag, False) for flag in flag_list):
                return False
        
        # Check item requirement (e.g., "item": "glowcap_mushrooms")
        if 'item' in requirements:
            item_id = requirements['item']
            
            # Get inventory engine reference
            try:
                from game_logic.inventory_engine import get_inventory_engine
                inv_engine = get_inventory_engine()
                
                if not inv_engine:
                    print(f"⚠️ WARNING: InventoryEngine not available for item requirement check")
                    return False
                
                # Get item data to convert ID to name
                item_data = self.item_manager.get_item_by_id(item_id)
                if not item_data:
                    print(f"⚠️ WARNING: Unknown item '{item_id}' in requirements")
                    return False
                
                # Get required quantity (default to 1)
                quantity = requirements.get('quantity', 1)

                # Get the item category from item data
                category = item_data.get('category', 'items')

                # Check if player has the item (using ID, not display name)
                if not inv_engine.has_item(item_id, category):
                    return False

                # Check quantity if more than 1 required
                if quantity > 1:
                    item_count = inv_engine.get_item_count(item_id)
                    if item_count < quantity:
                        return False
                    
            except Exception as e:
                print(f"❌ ERROR checking item requirement: {e}")
                return False
            
        # Check not_item requirement (e.g., "not_item": "glowcap_mushrooms")
        # Shows option only if player does NOT have the item
        if 'not_item' in requirements:
            item_id = requirements['not_item']
            
            try:
                from game_logic.inventory_engine import get_inventory_engine
                inv_engine = get_inventory_engine()
                
                if not inv_engine:
                    # If inventory engine not available, assume player doesn't have it
                    pass
                else:
                    # Get item data
                    item_data = self.item_manager.get_item_by_id(item_id)
                    if item_data:
                        # Get required quantity (default to 1)
                        quantity = requirements.get('quantity', 1)
                        
                        # Get the item category from item data
                        category = item_data.get('category', 'items')
                        
                        # If player HAS the item, hide this option
                        if inv_engine.has_item(item_id, category):
                            # Check quantity if specified
                            if quantity > 1:
                                item_count = inv_engine.get_item_count(item_id)
                                if item_count >= quantity:
                                    return False
                            else:
                                return False
            except Exception as e:
                print(f"❌ ERROR checking not_item requirement: {e}")
                # On error, show the option (fail-safe)

        return True

    def _emit_quest_event(self, event: Dict[str, Any]):
        """Emit quest event for future QuestEngine to handle"""
        # Store event for QuestEngine integration
        self.quest_event_hooks.append(event)
        print(f"🎯 Quest event emitted: {event['type']} - {event.get('quest_id')}")
    
    def _get_fallback_dialogue(self, npc_id: str) -> Dict[str, Any]:
        """Fallback dialogue if file loading fails"""
        return {
            'npc_name': npc_id.title(),
            'introduction': [f"{npc_id.title()} looks at you with interest."],
            'options': [
                {
                    'id': 'generic_goodbye',
                    'text': 'Farewell.',
                    'response': ['Safe travels, friend.'],
                    'effects': []
                }
            ],
            'default_actions': []
        }
    def get_dialogue_metadata(self, dialogue_id: str) -> Dict[str, Any]:
        """
        Get metadata for a dialogue (is it an object? should we hide portrait? custom icon?)
        
        Args:
            dialogue_id: Dialogue file identifier (e.g., 'swamp_church_altar')
            
        Returns:
            Dict containing metadata:
                - is_object (bool): True if examining an object, False if talking to NPC
                - hide_portrait (bool): True to hide portrait/icon
                - display_name (str): Name to display in UI
                - object_icon (str|None): Custom icon filename, or None for default
        """
        # Return cached metadata if available
        if dialogue_id in self.dialogue_metadata:
            return self.dialogue_metadata[dialogue_id]
        
        # Not loaded yet - try loading the file
        if self.load_dialogue_file(dialogue_id):
            return self.dialogue_metadata.get(dialogue_id, self._get_default_metadata(dialogue_id))
        
        # Fallback to default NPC metadata
        return self._get_default_metadata(dialogue_id)

    def _get_default_metadata(self, dialogue_id: str) -> Dict[str, Any]:
        """Default metadata for dialogues without explicit metadata"""
        return {
            'is_object': False,
            'hide_portrait': False,
            'display_name': dialogue_id.replace('_', ' ').title(),
            'object_icon': None
        }


    def register_quest_engine(self, quest_engine):
        """Register QuestEngine for event handling (Session 9 integration)"""
        self.quest_engine = quest_engine
        print("🎯 QuestEngine registered with DialogueEngine")
        
        # Process any queued quest events
        for event in self.quest_event_hooks:
            quest_engine.handle_dialogue_event(event)
        
        self.quest_event_hooks.clear()
   
    def _clear_conversation_state(self, npc_id):
            """Clear conversation state when dialogue ends"""
            state_attr = f'{npc_id}_dialogue_state'
            if hasattr(self.game_state, state_attr):
                delattr(self.game_state, state_attr)
            
            # Clear any stored response data from old system
            response_attrs = [
                f'{npc_id}_dialogue_response',
                f'showing_{npc_id}_response',
                f'{npc_id}_dialogue_response_actions'
            ]
            
            for attr in response_attrs:
                if hasattr(self.game_state, attr):
                    delattr(self.game_state, attr)
                    
            print(f"🧹 Cleared dialogue state for {npc_id}")

    def start_dialogue(self, npc_id: str, source_screen: str = None):
        """Start dialogue and remember where it came from"""
        self.current_dialogue_npc = npc_id
        self.dialogue_source_screen = source_screen or self.game_state.screen
        print(f"🎭 Starting dialogue with {npc_id} from {self.dialogue_source_screen}")
    
    def end_dialogue(self):
        """End dialogue and return to appropriate source"""
        
        if self.dialogue_source_screen:
            target_screen = self.dialogue_source_screen
            print(f"🔙 Returning to tracked source screen: {target_screen}")
        
        # Clear dialogue state
        self.current_dialogue_npc = None
        self.dialogue_source_screen = None
        
        # Navigate back
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {
                'target_screen': target_screen,
                'source_screen': f'dialogue'
            })
            print(f"🔙 Navigation event emitted to: {target_screen}")


def initialize_dialogue_engine(game_state_ref, event_manager_ref, item_manager_ref):
    """
    Initialize DialogueEngine following the established DataManager pattern
    
    Args:
        game_state_ref: Reference to GameState (Single Data Authority)
        event_manager_ref: Reference to EventManager for event handler registration
        
    Returns:
        DialogueEngine: Initialized engine instance
    """
    try:
        engine = DialogueEngine(game_state_ref, item_manager_ref)
        engine.register_event_handlers(event_manager_ref)  # ADD THIS LINE
        print("✅ DialogueEngine initialized successfully")
        return engine
    except Exception as e:
        print(f"❌ DialogueEngine initialization failed: {e}")
        return None