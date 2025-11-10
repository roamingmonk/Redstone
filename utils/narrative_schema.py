# utils/narrative_schema.py
"""
Narrative Schema Manager - Single Source of Truth for Story Elements
Professional game development pattern for maintaining consistency across systems
"""

import json
import os
from typing import Dict, List, Optional, Any

class NarrativeSchema:
    """
    Centralizes all narrative identifiers and relationships
    Prevents mismatched flags between DialogueEngine, QuestEngine, and GameState
    """
    
    def __init__(self):
        self.schema = None
        self.load_schema()
    
    def load_schema(self):
        """Load narrative schema from JSON file"""
        schema_path = os.path.join('data', 'narrative_schema.json')
        try:
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)
            print("📜 Narrative schema loaded successfully")
        except FileNotFoundError:
            print(f"⚠️ Narrative schema not found at {schema_path}")
            self.schema = {"npcs": {}, "locations": {}, "quest_triggers": {}}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing narrative schema: {e}")
            self.schema = {"npcs": {}, "locations": {}, "quest_triggers": {}}
    
    # NPC Management
    def get_npc_conversation_flag(self, npc_id: str) -> str:
        """Get the GameState flag name for NPC conversation tracking"""
        npc_data = self.schema.get("npcs", {}).get(npc_id, {})
        return npc_data.get("conversation_flag", f"{npc_id}_talked")
    
    def get_npc_story_flag(self, npc_id: str, story_element: str) -> str:
        """Get specific story flag name for NPC"""
        npc_data = self.schema.get("npcs", {}).get(npc_id, {})
        story_flags = npc_data.get("story_flags", {})
        return story_flags.get(story_element, f"{npc_id}_{story_element}")
    
    def get_npc_dialogue_file(self, npc_id: str) -> str:
        """Get dialogue file identifier for NPC"""
        npc_data = self.schema.get("npcs", {}).get(npc_id, {})
        return npc_data.get("dialogue_file", f"broken_blade_{npc_id}")
    
    def get_npc_location(self, npc_id: str, default: str = None) -> str:
        """Get the location where an NPC is found"""
        npc_data = self.schema.get("npcs", {}).get(npc_id, {})
        return npc_data.get("location", default)

    # Location Management  
    def get_location_discovery_flag(self, location_id: str) -> str:
        """Get GameState flag name for location discovery"""
        location_data = self.schema.get("locations", {}).get(location_id, {})
        return location_data.get("discovery_flag", f"learned_about_{location_id}")
    
    def get_location_quest_id(self, location_id: str) -> str:
        """Get quest ID associated with location"""
        location_data = self.schema.get("locations", {}).get(location_id, {})
        return location_data.get("quest_id", f"explore_{location_id}")
    
    def get_location_display_name(self, location_id: str) -> str:
        """Get user-facing location name"""
        location_data = self.schema.get("locations", {}).get(location_id, {})
        return location_data.get("display_name", location_id.replace("_", " ").title())
    
    
    # Quest System Integration
    def get_quest_trigger_for_flag(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """Find quest trigger associated with a dialogue flag"""
        for trigger_id, trigger_data in self.schema.get("quest_triggers", {}).items():
            if trigger_data.get("dialogue_flag") == flag_name:
                return trigger_data
        return None
    
    def get_quest_objectives_for_flags(self, quest_id: str, flags: List[str]) -> List[str]:
        """Get quest objectives that should complete based on flags"""
        quest_mappings = self.schema.get("quest_mappings", {}).get(quest_id, {})
        objectives = quest_mappings.get("objectives", {})
        
        completed_objectives = []
        for objective_id, required_flags in objectives.items():
            # Check if all required flags are in the provided list
            if all(flag in flags for flag in required_flags if not flag.startswith("!")):
                completed_objectives.append(objective_id)
        
        return completed_objectives
    
    # Dialogue State Management
    def evaluate_dialogue_state(self, npc_id: str, game_state) -> str:
        """Determine dialogue state based on game flags"""
        state_mapping = self.schema.get("dialogue_state_mapping", {}).get(npc_id, {})
        
        for state_name, condition in state_mapping.items():
            if self._evaluate_condition(condition, game_state):
                return state_name
        
        return "first_meeting"  # Default fallback
    
    def _evaluate_condition(self, condition: str, game_state) -> bool:
        """Evaluate boolean condition string against game state"""
        # Simple condition evaluator - can be enhanced for complex logic
        # Handles: "!flag", "flag1 && flag2", basic boolean operations
        
        # Replace schema references with actual values
        condition = condition.replace("&&", " and ").replace("||", " or ")
        
        # Handle negation
        tokens = condition.split()
        for i, token in enumerate(tokens):
            if token.startswith("!"):
                flag_name = token[1:]
                flag_value = getattr(game_state, flag_name, False)
                tokens[i] = str(not flag_value)
            elif token not in ["and", "or", "(", ")"]:
                flag_value = getattr(game_state, token, False)
                tokens[i] = str(flag_value)
        
        try:
            return eval(" ".join(tokens))
        except:
            return False
    
    # Validation and Debugging
    def validate_consistency(self) -> List[str]:
        """Validate schema consistency and return list of issues"""
        issues = []
        
        # Check for duplicate flags
        all_flags = set()
        for npc_data in self.schema.get("npcs", {}).values():
            conv_flag = npc_data.get("conversation_flag")
            if conv_flag in all_flags:
                issues.append(f"Duplicate conversation flag: {conv_flag}")
            all_flags.add(conv_flag)
            
            for flag in npc_data.get("story_flags", {}).values():
                if flag in all_flags:
                    issues.append(f"Duplicate story flag: {flag}")
                all_flags.add(flag)
        
        # Check quest trigger references
        for trigger_data in self.schema.get("quest_triggers", {}).values():
            flag = trigger_data.get("dialogue_flag")
            if flag not in all_flags:
                issues.append(f"Quest trigger references unknown flag: {flag}")
        
        return issues
    
    def get_all_flags(self) -> List[str]:
        """Get complete list of all narrative flags for GameState initialization"""
        flags = []
        
        # NPC conversation flags
        for npc_data in self.schema.get("npcs", {}).values():
            flags.append(npc_data.get("conversation_flag"))
            flags.extend(npc_data.get("story_flags", {}).values())
        
        # Location discovery flags
        for location_data in self.schema.get("locations", {}).values():
            discovery_flag = location_data.get("discovery_flag")
            if discovery_flag:
                flags.append(discovery_flag)
            completion_flag = location_data.get("completion_flag")
            if completion_flag:
                flags.append(completion_flag)
        
        # Act progression flags
        for act_data in self.schema.get("act_progression", {}).values():
            start_flag = act_data.get("start_flag")
            if start_flag:
                flags.append(start_flag)
            completion_flag = act_data.get("completion_flag")
            if completion_flag:
                flags.append(completion_flag)
        
        # Quest trigger flags
        for trigger_data in self.schema.get("quest_triggers", {}).values():
            dialogue_flag = trigger_data.get("dialogue_flag")
            if dialogue_flag:
                flags.append(dialogue_flag)
        
        return flags

# Global instance for easy access
narrative_schema = NarrativeSchema()