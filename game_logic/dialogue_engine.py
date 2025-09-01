# game_logic/dialogue_engine.py
"""
Dialogue Engine - Professional Conversation Management System
Following Single Data Authority Pattern established in the project

GameState = THE authoritative data source for all conversation flags
DialogueEngine = Pure business logic for conversation flow and quest triggers
JSON Files = Data-driven conversation content with Baldur's Gate style choices

Key Features:
- Branching dialogue trees with player choice consequences
- Quest event hooks for integration with future QuestEngine
- State-dependent conversations based on game progression
- Professional conversation flow management
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any

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
        """
        Determine current conversation state for NPC based on game progression
        
        Args:
            npc_id: NPC identifier (e.g., 'garrick')
            
        Returns:
            str: Current dialogue state key
        """
        # This method analyzes GameState to determine conversation state
        if npc_id == 'garrick':
            # Garrick's conversation states based on quest progression
            if not self.game_state.garrick_talked:
                return 'first_meeting'
            elif not getattr(self.game_state, 'mayor_talked', False):
                return 'after_first_talk'  
            elif getattr(self.game_state, 'quest_active', False):
                return 'quest_active'
            else:
                return 'post_mayor'
        
        elif npc_id == 'meredith' or npc_id == 'server':
            if not getattr(self.game_state, 'meredith_talked', False):
                return 'first_meeting'
            elif getattr(self.game_state, 'mayor_talked', False):
                return 'post_mayor'
            else:
                return 'return_visits'



        # Default to first meeting for other NPCs
        return 'first_meeting'
    
    def get_conversation_options(self, dialogue_id: str, npc_id: str) -> Dict[str, Any]:
        """
        Get current conversation options for NPC
        
        Args:
            dialogue_id: Dialogue file identifier
            npc_id: NPC identifier
            
        Returns:
            Dict containing conversation data and options
        """
        if dialogue_id not in self.dialogues:
            if not self.load_dialogue_file(dialogue_id):
                return self._get_fallback_dialogue(npc_id)
        
        dialogue_tree = self.dialogues[dialogue_id]
        current_state = self.get_current_dialogue_state(npc_id)
        
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
    
    def process_dialogue_choice(self, dialogue_id: str, npc_id: str, choice_id: str) -> Dict[str, Any]:
        """
        Process player's dialogue choice and return response
        
        Args:
            dialogue_id: Dialogue file identifier  
            npc_id: NPC identifier
            choice_id: Selected choice identifier
            
        Returns:
            Dict containing NPC response and any triggered effects
        """
        if dialogue_id not in self.dialogues:
            return {'response': ["I don't understand."], 'effects': []}
        
        dialogue_tree = self.dialogues[dialogue_id]
        current_state = self.get_current_dialogue_state(npc_id)
        
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
        
        # Process the choice effects
        effects = []
        for effect in selected_choice.get('effects', []):
            effect_result = self._apply_dialogue_effect(effect)
            if effect_result:
                effects.append(effect_result)
        
        return {
            'response': selected_choice.get('response', ["..."]),
            'effects': effects,
            'next_state': selected_choice.get('next_state'),
            'actions_available': selected_choice.get('actions', [])
        }
    
    def _check_option_requirements(self, option: Dict[str, Any]) -> bool:
        """Check if dialogue option requirements are met"""
        requirements = option.get('requirements', [])
        
        for req in requirements:
            if req.startswith('!'):
                # Negative requirement - flag should be False
                flag_name = req[1:]
                if getattr(self.game_state, flag_name, False):
                    return False
            else:
                # Positive requirement - flag should be True
                if not getattr(self.game_state, flag_name, False):
                    return False
        
        return True
    
    def _apply_dialogue_effect(self, effect: Dict[str, Any]) -> Optional[str]:
        """Apply dialogue choice effects to GameState"""
        effect_type = effect.get('type')
        
        if effect_type == 'set_flag':
            flag_name = effect.get('flag')
            value = effect.get('value', True)
            setattr(self.game_state, flag_name, value)
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

def initialize_dialogue_engine(game_state_ref):
    """
    Initialize DialogueEngine following the established DataManager pattern
    
    Args:
        game_state_ref: Reference to GameState (Single Data Authority)
        
    Returns:
        DialogueEngine: Initialized engine instance
    """
    try:
        engine = DialogueEngine(game_state_ref)
        print("✅ DialogueEngine initialized successfully")
        return engine
    except Exception as e:
        print(f"❌ DialogueEngine initialization failed: {e}")
        return None