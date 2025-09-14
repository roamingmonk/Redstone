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
    
    def __init__(self, game_state):
        """Initialize DialogueEngine with GameState authority"""
        self.game_state = game_state
        self.dialogues = {}  # Loaded dialogue trees
        self.quest_event_hooks = []  # Future QuestEngine integration
        self.event_manager = None 

        print("🗣️ DialogueEngine initialized with GameState authority")
    
    def load_dialogue_file(self, dialogue_id: str) -> bool:
        """
        Load dialogue tree from JSON file
        
        Args:
            dialogue_id: Name of dialogue file (e.g., 'tavern_garrick')
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            file_path = os.path.join('data', 'dialogues', f'{dialogue_id}.json')
            
            if not os.path.exists(file_path):
                print(f"⚠️ Dialogue file not found: {file_path}")
                return False
                
            with open(file_path, 'r') as f:
                dialogue_data = json.load(f)
                
            self.dialogues[dialogue_id] = dialogue_data
            print(f"✅ Loaded dialogue tree: {dialogue_id}")
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
            print(f"DEBUG: DE: GCDS: Using stored dialogue state: {stored_state}")
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
        print("DE: STATE-EVAL ORDER:", list(npc_states.keys()))
        for state_name, condition in npc_states.items():
            if self._evaluate_condition(condition, context):
                print("DE: MATCH ->", state_name)
                return state_name
        
        return 'first_meeting'

    def _evaluate_condition(self, condition: str, context: dict) -> bool:
        """Evaluate dialogue state condition string"""
        try:
            # Replace operators
            condition = condition.replace('!', 'not ').replace('&&', ' and ').replace('||', ' or ')
            
            # Safely evaluate
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            print(f"DEBUG: Condition evaluation failed: {condition}, error: {e}")
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

    def get_conversation_options(self, dialogue_id: str, npc_id: str, forced_state: str = None) -> Dict[str, Any]:
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
        current_state = forced_state or self.get_current_dialogue_state(npc_id)
        
        if current_state in dialogue_tree.get('states', {}):
            state_data = dialogue_tree['states'][current_state]
            
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
            
            # Get choice_id from conversation data
            conversation_data = self.get_conversation_options(dialogue_file_id, npc_id)
            options = conversation_data.get('options', [])

            if choice_index < len(options):
                choice_id = options[choice_index]['id']
                print(f"🎭 DEBUG: Selected option ID: {choice_id}")
                
                # Determine state BEFORE setting flags for consistency
                current_state = self.get_current_dialogue_state(npc_id)
                print(f"🎭 DEBUG: Using state: {current_state} for choice processing")
                
                # NARRATIVE SCHEMA INTEGRATION - Set conversation flag AFTER state determination
                conv_flag = narrative_schema.get_npc_conversation_flag(npc_id)
                setattr(self.game_state, conv_flag, True)
                print(f"✅ Set conversation flag: {conv_flag} = True")

                # Call existing business logic method with explicit state
                result = self.process_dialogue_choice(dialogue_file_id, npc_id, choice_id, current_state)
                print(f"🎭 DEBUG: Choice processing result: {result}")
                if result:
                    # Handle conversation ending through event system
                    if result.get('conversation_ended'):
                        print(f"🎭 DEBUG: Conversation ended, emitting navigation event")
                        self.event_manager.emit("DIALOGUE_ENDED", {
                            'npc_id': npc_id,
                            'return_to': result.get('return_to', 'location')
                        })
                        return result
                    elif result.get('new_conversation'):
                        new_conv = result['new_conversation']
                        setattr(self.game_state, f'{npc_id}_conversation_data', new_conv)
                        print(f"🎭 DEBUG: Engine result ready for UI handler")
                        return result
                    else:
                        # Fallback for old response format
                        response_lines = result.get('response', [])
                        setattr(self.game_state, f'{npc_id}_dialogue_response', response_lines)
                        setattr(self.game_state, f'showing_{npc_id}_response', True)
                        print(f"🎭 DEBUG: Response stored, registering dialogue state handler")
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
                            location_id = getattr(self.game_state, f'{npc_id}_current_location', None)
                            if location_id:
                                target_screen = f'{location_id}_main'

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
        print(f"🔧 DEBUG PROCESS: Called with forced_state={forced_state}")
        print(f"DEBUG: DE: Processing choice {choice_id} for {npc_id}")

        # Clear temporary action choices when a choice is made
        temp_choices_attr = f'{npc_id}_dialogue_response_actions'
        if hasattr(self.game_state, temp_choices_attr):
            setattr(self.game_state, temp_choices_attr, None)
            print(f"DEBUG: DE: Cleared temporary action choices for {npc_id}")

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
                        print(f"DEBUG: DE: Action choice triggered state transition: {npc_id} -> {target_state}")
                        
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
            current_state = forced_state or self.get_current_dialogue_state(npc_id)
            print(f"🔧 DEBUG PROCESS: DE: Using current_state={current_state}")
            print(f"DEBUG: DE: Current state = {current_state}")

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
            
            print(f"DEBUG: DE: Selected choice = {selected_choice}")

            # Process the choice effects
            #effects = []
            #for effect in selected_choice.get('effects', []):
            #    effect_result = self._apply_dialogue_effect(effect)
            #    if effect_result:
            #        effects.append(effect_result)

            # Process effects immediately when choice is selected
            effects_processed = []
            for effect in selected_choice.get('effects', []):
                effect_result = self._apply_dialogue_effect(effect)
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
                print(f"🧹 DE: PDC: Cleared dialogue state and conversation data for {npc_id}")
                
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
                print(f"DE: STATE UPDATE CHECK: {npc_id} should be {next_state}, actually is {actual_state}")
    
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
    
    def _apply_dialogue_effect(self, effect: Dict[str, Any]) -> Optional[str]:
        """Apply dialogue choice effects to GameState with robust error handling"""
        
        # Add defensive checks at the start
        if not effect or not isinstance(effect, dict):
            print(f"WARNING: Invalid effect data: {effect}")
            return None
            
        effect_type = effect.get('type')
        if not effect_type:
            print(f"WARNING: Effect missing type: {effect}")
            return None
        
        if effect_type == 'set_flag':
            flag_name = effect.get('flag')
            # ADD THIS CHECK:
            if not flag_name:
                print(f"WARNING: set_flag effect missing flag name: {effect}")
                return None
                
            value = effect.get('value', True)
            setattr(self.game_state, flag_name, value)
            print(f"✅ Set flag: {flag_name} = {value}")
            
            # SYNC PARTY MEMBERS LIST when recruitment flags change
            if flag_name.endswith('_recruited'):
                self._sync_party_members_list()
            
            return f"Set {flag_name} = {value}"
            
        elif effect_type == 'quest_trigger':
            # Quest event hook for future QuestEngine integration
            quest_event = {
                'type': 'quest_trigger',
                'quest_id': effect.get('quest_id'),
                'trigger_type': effect.get('trigger_type', 'start'),
                'data': effect.get('data', {})
            }
            self._emit_quest_event(quest_event)
            return f"Quest trigger: {effect.get('quest_id')}"
            
        elif effect_type == 'add_location':
            location = effect.get('location')
            if location and location not in self.game_state.locations_discovered:
                self.game_state.locations_discovered.append(location)
                return f"Discovered location: {location}"
        
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
            
            # Add other requirement types here as needed
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


def initialize_dialogue_engine(game_state_ref, event_manager_ref):
    """
    Initialize DialogueEngine following the established DataManager pattern
    
    Args:
        game_state_ref: Reference to GameState (Single Data Authority)
        event_manager_ref: Reference to EventManager for event handler registration
        
    Returns:
        DialogueEngine: Initialized engine instance
    """
    try:
        engine = DialogueEngine(game_state_ref)
        engine.register_event_handlers(event_manager_ref)  # ADD THIS LINE
        print("✅ DialogueEngine initialized successfully")
        return engine
    except Exception as e:
        print(f"❌ DialogueEngine initialization failed: {e}")
        return None