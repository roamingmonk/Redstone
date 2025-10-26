# utils/combat_loader.py
"""
Combat Data Loader - Utilities for loading and validating combat JSON files
Follows existing utils pattern for data management utilities
"""

import json
import os
import copy
import uuid
from typing import Dict, List, Optional

class CombatDataLoader:
    """Utility class for loading and validating combat configuration files"""
    
    def __init__(self):
        """Initialize with caching for performance"""
        self.enemy_cache = {}
        self.encounter_cache = {}
        self.battlefield_cache = {}
        self.base_path = "data/combat"
        
        print("🗂️ CombatDataLoader initialized")
    
    def load_enemy(self, enemy_id: str) -> Optional[Dict]:
        """
        Load enemy definition from data/combat/enemies/
        
        Args:
            enemy_id: ID of enemy to load (e.g., "giant_rat")
            
        Returns:
            Dict containing enemy data or None if not found
        """
        if enemy_id in self.enemy_cache:
            return self.enemy_cache[enemy_id]
        
        try:
            file_path = os.path.join(self.base_path, "enemies", f"{enemy_id}.json")
            
            if not os.path.exists(file_path):
                print(f"❌ Enemy file not found: {file_path}")
                return None
            
            with open(file_path, 'r') as f:
                enemy_data = json.load(f)
            
            # Validate enemy data
            if self._validate_enemy_data(enemy_data):
                self.enemy_cache[enemy_id] = enemy_data
                print(f"✅ Loaded enemy: {enemy_id}")
                return enemy_data
            else:
                print(f"❌ Invalid enemy data: {enemy_id}")
                return None
                
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"❌ Error loading enemy {enemy_id}: {e}")
            return None
    
    def load_encounter(self, encounter_id: str) -> Optional[Dict]:
        """
        Load encounter configuration from data/combat/encounters/
        
        Args:
            encounter_id: ID of encounter to load (e.g., "basement_rats")
            
        Returns:
            Dict containing encounter data or None if not found
        """
        if encounter_id in self.encounter_cache:
            return self.encounter_cache[encounter_id]
        
        try:
            file_path = os.path.join(self.base_path, "encounters", f"{encounter_id}.json")
            
            if not os.path.exists(file_path):
                print(f"❌ Encounter file not found: {file_path}")
                return None
            
            with open(file_path, 'r') as f:
                encounter_data = json.load(f)
            
            # Validate encounter data
            if self._validate_encounter_data(encounter_data):
                self.encounter_cache[encounter_id] = encounter_data
                print(f"✅ Loaded encounter: {encounter_id}")
                return encounter_data
            else:
                print(f"❌ Invalid encounter data: {encounter_id}")
                return None
                
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"❌ Error loading encounter {encounter_id}: {e}")
            return None
    
    def load_battlefield(self, battlefield_id: str) -> Optional[Dict]:
        """
        Load battlefield layout from data/combat/battlefields/
        
        Args:
            battlefield_id: ID of battlefield to load (e.g., "small_cellar")
            
        Returns:
            Dict containing battlefield data or None if not found
        """
        if battlefield_id in self.battlefield_cache:
            return self.battlefield_cache[battlefield_id]
        
        try:
            file_path = os.path.join(self.base_path, "battlefields", f"{battlefield_id}.json")
            
            if not os.path.exists(file_path):
                print(f"❌ Battlefield file not found: {file_path}")
                return None
            
            with open(file_path, 'r') as f:
                battlefield_data = json.load(f)
            
            # Validate battlefield data
            if self._validate_battlefield_data(battlefield_data):
                self.battlefield_cache[battlefield_id] = battlefield_data
                print(f"✅ Loaded battlefield: {battlefield_id}")
                return battlefield_data
            else:
                print(f"❌ Invalid battlefield data: {battlefield_id}")
                return None
                
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"❌ Error loading battlefield {battlefield_id}: {e}")
            return None
    
    def get_available_enemies(self) -> List[str]:
        """Return list of all available enemy IDs"""
        enemies_path = os.path.join(self.base_path, "enemies")
        if not os.path.exists(enemies_path):
            return []
        
        enemy_files = [f[:-5] for f in os.listdir(enemies_path) if f.endswith('.json')]
        return sorted(enemy_files)
    
    def load_encounter_with_context(self, encounter_id: str, combat_context: Dict = None) -> Optional[Dict]:
        """
        Load encounter and merge with location-specific context
        
        Args:
            encounter_id: ID of base encounter (e.g., "two_giant_rats")
            combat_context: Location-specific text and quest flags
            
        Returns:
            Dict containing encounter merged with context
        """
        base_encounter = self.load_encounter(encounter_id)
        if not base_encounter:
            return None
        
        # Merge context if provided
        if combat_context:
            # Add location-specific victory/defeat text
            if "victory_description" in combat_context:
                base_encounter["victory_description"] = combat_context["victory_description"]
            if "defeat_description" in combat_context:
                base_encounter["defeat_description"] = combat_context["defeat_description"]
            
            # Add location-specific quest flags
            if "victory_quest_flags" in combat_context:
                base_encounter["victory_quest_flags"] = combat_context["victory_quest_flags"]
            if "defeat_consequences" in combat_context:
                base_encounter["defeat_consequences"] = combat_context["defeat_consequences"]
            
            # Add location name for combat log
            if "location_name" in combat_context:
                base_encounter["location_name"] = combat_context["location_name"]

        return base_encounter 
        
    def get_available_encounters(self) -> List[str]:
        """Return list of all available encounter IDs"""
        encounters_path = os.path.join(self.base_path, "encounters")
        if not os.path.exists(encounters_path):
            return []
        
        encounter_files = [f[:-5] for f in os.listdir(encounters_path) if f.endswith('.json')]
        return sorted(encounter_files)

    def get_available_battlefields(self) -> List[str]:
        """Return list of all available battlefield IDs"""
        battlefields_path = os.path.join(self.base_path, "battlefields")
        if not os.path.exists(battlefields_path):
            return []
        
        battlefield_files = [f[:-5] for f in os.listdir(battlefields_path) if f.endswith('.json')]
        return sorted(battlefield_files)

    def create_combat_instance(self, encounter_id: str, combat_context: Dict = None) -> Optional[Dict]:
        """
        Create a complete combat instance by loading encounter and all referenced data
        
        Args:
            encounter_id: ID of encounter template
            combat_context: Location-specific text and quest flags
            
        Returns:
            Dict containing complete combat data with instantiated enemies
        """
        # Load the encounter template
        encounter = self.load_encounter(encounter_id)
        if not encounter:
            return None
        
        # Load the battlefield
        battlefield_id = encounter.get("battlefield_id")
        battlefield = self.load_battlefield(battlefield_id)
        if not battlefield:
            print(f"❌ Failed to load battlefield: {battlefield_id}")
            return None
        
        # Create instances of each enemy
        enemy_instances = []
        for enemy_spawn in encounter.get("enemies", []):
            enemy_id = enemy_spawn["enemy_id"]
            
            # Load the base enemy template
            enemy_template = self.load_enemy(enemy_id)
            if not enemy_template:
                print(f"❌ Failed to load enemy: {enemy_id}")
                continue
            
            # Create instance with spawn data
            enemy_instance = self._create_enemy_instance(enemy_template, enemy_spawn)
            enemy_instances.append(enemy_instance)
        
        # Build complete combat data
        combat_data = {
            "encounter": encounter,
            "battlefield": battlefield,
            "enemy_instances": enemy_instances,
            "player_positions": encounter["player_party"]["starting_positions"],
            "turn_number": 0,
            "current_actor": None,
            "combat_phase": "setup"
        }
        
        # Merge location-specific context
        if combat_context:
            self._merge_combat_context(combat_data, combat_context)
        
        print(f"✅ Created combat instance: {encounter_id} with {len(enemy_instances)} enemies")
        return combat_data

    def _create_enemy_instance(self, enemy_template: Dict, spawn_data: Dict) -> Dict:
        """Create an enemy instance from template with spawn data"""
        enemy = copy.deepcopy(enemy_template)
        
        # Apply spawn position [x, y]
        enemy["position"] = spawn_data["position"]
        enemy["facing"] = spawn_data["facing"]
        
        # OPTIONAL: Encounter can override enemy's default tactics
        # If encounter doesn't specify ai_behavior, use enemy template's behavior.tactics
        if "ai_behavior" in spawn_data:
            enemy["encounter_behavior"] = spawn_data["ai_behavior"]
        else:
            # No override - AI will use enemy template's behavior.tactics
            enemy["encounter_behavior"] = None
        
        # Generate unique instance ID for tracking during combat
        enemy["instance_id"] = str(uuid.uuid4())[:8]
        
       # Initialize combat state
        enemy["current_hp"] = enemy["stats"]["hp"]
        enemy["status_effects"] = []
        enemy["actions_remaining"] = 1
        enemy["has_moved"] = False
        enemy["has_acted"] = False
        
        # Initialize spell slots (simple number for now)
        max_slots = enemy.get("spell_slots", 0)
        enemy["current_spell_slots"] = max_slots
        enemy["max_spell_slots"] = max_slots
        
        return enemy

    def _merge_combat_context(self, combat_data: Dict, combat_context: Dict):
        """Merge location-specific context into combat data"""
        context_fields = [
            "victory_description", "defeat_description", 
            "victory_quest_flags", "defeat_consequences", "location_name"
        ]
        
        for field in context_fields:
            if field in combat_context:
                combat_data[field] = combat_context[field]

    def _validate_enemy_data(self, enemy_data: Dict) -> bool:
        """Validate enemy data has required fields"""
        print(f"🔍 DEBUG: Validating enemy data for: {enemy_data.get('enemy_id', 'unknown')}")
        
        required_fields = ['enemy_id', 'name', 'stats', 'attacks', 'movement', 'loot', 'behavior']
        required_stats = ['hp', 'max_hp', 'ac', 'strength', 'dexterity', 'constitution', 
                        'intelligence', 'wisdom', 'charisma']
        
        # Check top-level fields
        for field in required_fields:
            if field not in enemy_data:
                print(f"❌ Enemy missing required field: {field}")
                return False
            else:
                print(f"✅ Found field: {field}")
        
        # Check stats fields (full D&D ability scores)
        stats = enemy_data.get('stats', {})
        for stat in required_stats:
            if stat not in stats:
                print(f"❌ Enemy missing required stat: {stat}")
                return False
            else:
                print(f"✅ Found stat: {stat}")
        
        # Validate attacks array
        attacks = enemy_data.get('attacks', [])
        if not isinstance(attacks, list):
            print(f"❌ Enemy attacks must be an array")
            return False
        
        for i, attack in enumerate(attacks):
            print(f"🔍 Validating attack {i}: {attack.get('name', 'unnamed')}")
            
            # Check if this is a spell attack (uses spell_id reference)
            attack_type = attack.get('attack_type', '')
            if attack_type == 'spell':
                # Spell attacks only need: name, attack_type, spell_id, spell_cost
                required_attack_fields = ['name', 'attack_type', 'spell_id']
                print(f"   📜 Spell attack - validating spell reference")
            else:
                # Physical attacks need full data
                required_attack_fields = ['name', 'damage_dice', 'attack_bonus', 'attack_type', 'range']
            for field in required_attack_fields:
                if field not in attack:
                    print(f"❌ Attack missing required field: {field}")
                    return False
                else:
                    print(f"✅ Attack has field: {field}")
        
        # Validate movement
        movement = enemy_data.get('movement', {})
        print(f"🔍 Validating movement: {movement}")
        required_movement_fields = ['speed', 'movement_type']
        for field in required_movement_fields:
            if field not in movement:
                print(f"❌ Enemy missing movement field: {field}")
                return False
            else:
                print(f"✅ Movement has field: {field}")
        
        print(f"✅ All validation passed for enemy: {enemy_data.get('enemy_id')}")
        return True
    
    def _validate_encounter_data(self, encounter_data: Dict) -> bool:
        """Validate encounter data has required fields"""
        required_fields = ['encounter_id', 'name', 'battlefield_id', 'enemies', 'player_party', 
                          'victory_conditions', 'defeat_conditions', 'rewards']
        
        for field in required_fields:
            if field not in encounter_data:
                print(f"❌ Encounter missing required field: {field}")
                return False
        
        # Validate enemies array
        enemies = encounter_data.get('enemies', [])
        if not isinstance(enemies, list) or len(enemies) == 0:
            print(f"❌ Encounter must have at least one enemy")
            return False
        
        # Validate each enemy spawn
        for enemy in enemies:
            required_enemy_fields = ['enemy_id', 'position', 'facing']  # ai_behavior is OPTIONAL
            for field in required_enemy_fields:
                if field not in enemy:
                    print(f"❌ Enemy spawn missing required field: {field}")
                    return False
            
            # Validate position format [x, y]
            position = enemy.get('position', [])
            if not isinstance(position, list) or len(position) != 2:
                print(f"❌ Enemy position must be [x, y] array")
                return False
        
        # Validate player party
        player_party = encounter_data.get('player_party', {})
        if 'starting_positions' not in player_party:
            print(f"❌ Player party missing starting_positions")
            return False
        
        # Validate victory conditions
        victory_conditions = encounter_data.get('victory_conditions', {})
        if 'victory_type' not in victory_conditions:
            print(f"❌ Encounter missing victory_type")
            return False

        # Validate defeat conditions  
        defeat_conditions = encounter_data.get('defeat_conditions', {})
        if 'defeat_type' not in defeat_conditions:
            print(f"❌ Encounter missing defeat_type")
            return False

        return True
    
    def _validate_battlefield_data(self, battlefield_data: Dict) -> bool:
        """Validate battlefield data has required fields"""
        required_fields = ['battlefield_id', 'name', 'dimensions', 'terrain', 'spawn_zones']
        
        for field in required_fields:
            if field not in battlefield_data:
                print(f"❌ Battlefield missing required field: {field}")
                return False
        
        # Validate dimensions
        dimensions = battlefield_data.get('dimensions', {})
        if 'width' not in dimensions or 'height' not in dimensions:
            print(f"❌ Battlefield dimensions must have width and height")
            return False
        
        # Validate terrain structure
        terrain = battlefield_data.get('terrain', {})
        if 'walls' not in terrain:
            print(f"❌ Battlefield terrain missing walls definition")
            return False
        
        # Validate spawn zones
        spawn_zones = battlefield_data.get('spawn_zones', {})
        required_zones = ['player_start', 'enemy_spawns']
        for zone in required_zones:
            if zone not in spawn_zones:
                print(f"❌ Battlefield missing spawn zone: {zone}")
                return False
        
        return True

# Global instance for easy access
_combat_loader_instance = None

def get_combat_loader():
    """Get the global combat loader instance"""
    global _combat_loader_instance
    if _combat_loader_instance is None:
        _combat_loader_instance = CombatDataLoader()
    return _combat_loader_instance