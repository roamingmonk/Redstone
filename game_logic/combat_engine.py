# game_logic/combat_engine.py
"""
CombatEngine - Step 1: Basic Integration Test
Pure business logic processor - NO UI code
"""

from enum import Enum
from typing import Dict, Any, Optional

class CombatState(Enum):
    """Combat state tracking"""
    NOT_STARTED = "not_started"
    ACTIVE = "active" 
    VICTORY = "victory"
    DEFEAT = "defeat"

class CombatEngine:
    """
    Combat Engine - Step 1: Basic Business Logic
    
    Handles all combat logic and calculations.
    Integrates with GameState for character data.
    NO UI code - pure business logic processor.
    """
    
    def __init__(self, event_manager, game_state, data_manager=None):
        """
        Initialize CombatEngine
        
        Args:
            event_manager: EventManager for combat events
            game_state: GameState (Single Data Authority)
            data_manager: DataManager for future JSON loading
        """
        self.event_manager = event_manager
        self.game_state = game_state
        self.data_manager = data_manager
        
        # Combat state (transient - not saved)
        self.combat_state = CombatState.NOT_STARTED
        self.current_encounter = None
        self.combat_log = []
        
        print("⚔️ CombatEngine (Step 1) initialized")
    
    def start_combat(self, encounter_id: str) -> bool:
        """
        Start combat encounter - Step 1 version
        
        Args:
            encounter_id: Encounter identifier
            
        Returns:
            bool: True if combat started successfully
        """
        try:
            print(f"🎯 CombatEngine starting encounter: {encounter_id}")
            
            # Step 1: Simulate encounter loading
            self.current_encounter = {
                "id": encounter_id,
                "name": self._get_encounter_name(encounter_id)
            }
            
            # Set combat state
            self.combat_state = CombatState.ACTIVE
            self.combat_log = [f"Combat begins: {self.current_encounter['name']}"]
            
            # Emit combat started event
            self.event_manager.emit("COMBAT_STARTED", {
                "encounter_id": encounter_id,
                "encounter_name": self.current_encounter["name"]
            })
            
            print(f"✅ CombatEngine: Combat started successfully")
            return True
            
        except Exception as e:
            print(f"❌ CombatEngine: Combat start failed - {e}")
            return False
    
    def end_combat(self, result: str) -> Dict[str, Any]:
        """
        End combat and process results
        
        Args:
            result: "victory" or "defeat"
            
        Returns:
            dict: Combat results for GameState integration
        """
        print(f"🏁 CombatEngine ending combat with result: {result}")
        
        # Determine rewards based on encounter
        encounter_id = self.current_encounter.get("id") if self.current_encounter else "unknown"
        
        combat_results = {
            "result": result,
            "encounter_id": encounter_id,
            "xp_gained": 0,
            "gold_gained": 0,
            "quest_flags": {}
        }
        
        if result == "victory":
            # Step 1: Simple reward calculation
            combat_results.update({
                "xp_gained": 50,
                "gold_gained": 25,
                "quest_flags": self._get_victory_quest_flags(encounter_id)
            })
            
            # Apply rewards to GameState (Single Data Authority)
            self._apply_rewards_to_gamestate(combat_results)
            
        # Update combat state
        self.combat_state = CombatState.VICTORY if result == "victory" else CombatState.DEFEAT
        self.combat_log.append(f"Combat ended: {result}")
        
        # Emit combat ended event
        self.event_manager.emit("COMBAT_ENDED", combat_results)
        
        print(f"✅ CombatEngine: Combat ended with {combat_results}")
        return combat_results
    
    def get_combat_data_for_ui(self) -> Dict[str, Any]:
        """
        Provide combat data for UI rendering
        
        Returns:
            dict: All data needed by CombatSystem for rendering
        """
        return {
            "state": self.combat_state.value,
            "encounter_id": self.current_encounter.get("id") if self.current_encounter else None,
            "encounter_name": self.current_encounter.get("name") if self.current_encounter else "No Combat",
            "combat_log": self.combat_log.copy(),
            "is_active": self.combat_state == CombatState.ACTIVE,
            "can_test_victory": self.combat_state == CombatState.ACTIVE,
            "can_test_defeat": self.combat_state == CombatState.ACTIVE
        }
    
    # ==========================================
    # PRIVATE HELPER METHODS
    # ==========================================
    
    def _get_encounter_name(self, encounter_id: str) -> str:
        """Get display name for encounter - Step 1 version"""
        encounter_names = {
            "tavern_basement_rats": "Basement Rat Infestation",
            "hill_ruins_entrance": "Hill Ruins Guardian",
            "swamp_church_undead": "Undead at the Swamp Church"
        }
        return encounter_names.get(encounter_id, f"Unknown Encounter ({encounter_id})")
    
    def _get_victory_quest_flags(self, encounter_id: str) -> Dict[str, bool]:
        """Get quest flags to set on victory - Step 1 version"""
        victory_flags = {
            "tavern_basement_rats": {"completed_basement_combat": True},
            "hill_ruins_entrance": {"cleared_hill_ruins_entrance": True},
            "swamp_church_undead": {"defeated_swamp_church_undead": True}
        }
        return victory_flags.get(encounter_id, {})
    
    def _apply_rewards_to_gamestate(self, combat_results: Dict[str, Any]):
        """Apply combat rewards to GameState - Step 1 version"""
        try:
            # Add XP to player
            current_xp = self.game_state.character.get('experience', 0)
            self.game_state.character['experience'] = current_xp + combat_results['xp_gained']
            
            # Add gold to player
            current_gold = self.game_state.character.get('gold', 0)  
            self.game_state.character['gold'] = current_gold + combat_results['gold_gained']
            
            # Set quest flags
            if not hasattr(self.game_state, 'story_flags'):
                self.game_state.story_flags = {}
            
            for flag_name, flag_value in combat_results.get('quest_flags', {}).items():
                self.game_state.story_flags[flag_name] = flag_value
            
            # Add XP to party members (Step 1: simple equal distribution)
            party_xp_gain = combat_results['xp_gained']
            if hasattr(self.game_state, 'party_members') and self.game_state.party_members:
                for member_id in self.game_state.party_members:
                    if hasattr(self.game_state, 'party_xp') and member_id in self.game_state.party_xp:
                        current_member_xp = self.game_state.party_xp[member_id].get('experience', 0)
                        self.game_state.party_xp[member_id]['experience'] = current_member_xp + party_xp_gain
            
            print(f"✅ Applied rewards: {combat_results['xp_gained']} XP, {combat_results['gold_gained']} Gold")
            
        except Exception as e:
            print(f"❌ Error applying rewards to GameState: {e}")

# ==========================================
# INITIALIZATION FUNCTIONS
# ==========================================

def initialize_combat_engine(event_manager, game_state, data_manager=None):
    """
    Factory function to create CombatEngine instance
    Follows established engine initialization pattern
    """
    return CombatEngine(event_manager, game_state, data_manager)

# Global combat engine instance (initialized by GameController)
_combat_engine = None

def get_combat_engine():
    """Get the global CombatEngine instance"""
    return _combat_engine

def set_combat_engine(engine):
    """Set the global CombatEngine instance"""
    global _combat_engine
    _combat_engine = engine