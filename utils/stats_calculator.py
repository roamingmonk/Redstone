# utils/stats_calculator.py
"""
StatsCalculator - Industry Standard RPG Combat Statistics Engine
Calculates AC, attacks, damage, and all modifiers from multiple sources
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from utils.buff_manager import get_buff_manager

class StatsCalculator:
    """
    Industry standard RPG statistics calculator
    Combines character stats, equipment, class features, and temporary effects
    """
    
    def __init__(self):
        self.items_data = {}
        self.class_data = {}
        self.load_game_data()
    
        # Initialize buff manager for stat modifications
        # Use a simple wrapper to get ItemManager-compatible interface
        self.buff_manager = None  # Lazy initialization on first use
        
    def load_game_data(self):
        """Load items and class data from JSON files"""
        try:
            # Load items data
            with open(os.path.join('data', 'items.json'), 'r') as f:
                self.items_data = json.load(f)
            
            # Load class data  
            with open(os.path.join('data', 'player', 'character_classes.json'), 'r') as f:
                self.class_data = json.load(f)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Error loading game data: {e}")
            self.items_data = {"merchant_items": []}
            self.class_data = {"character_classes": {}}
    
    def _ensure_buff_manager(self):
        """
        Lazy initialization of buff manager
        Uses self as item manager (StatsCalculator has get_item_by_id method)
        """
        if self.buff_manager is None:
            self.buff_manager = get_buff_manager(self)
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """
        Find item data by ID (required for BuffManager compatibility)
        
        Args:
            item_id: Item identifier
            
        Returns:
            Item data dict or None if not found
        """
        # BuffManager expects this method, just delegate to get_item_by_name
        return self.get_item_by_name(item_id)

    def get_ability_modifier(self, ability_score: int) -> int:
        """Standard ability modifier calculation"""
        return (ability_score - 10) // 2
    
    def calculate_proficiency_bonus(self, level: int) -> int:
        """
        Calculate proficiency bonus based on character level
        
        Standard D&D 5e progression:
        - Levels 1-4:  +2
        - Levels 5-8:  +3
        - Levels 9-12: +4
        - Levels 13-16: +5
        - Levels 17-20: +6
        
        Args:
            level: Character level (1-20)
            
        Returns:
            Proficiency bonus as integer
        """
        if level < 1:
            return 2  # Minimum for safety
        return 2 + ((level - 1) // 4)

    def calculate_save_modifier(self, stats: dict, save_type: str, 
                                    proficiencies: list, level: int) -> int:
            """
            Calculate saving throw modifier for a character
            
            Formula: ability_modifier + proficiency_bonus (if proficient)
            
            Args:
                stats: Dict of ability scores {'strength': 14, 'dexterity': 12, ...}
                save_type: Which save ('strength', 'dexterity', 'constitution', 
                        'intelligence', 'wisdom', 'charisma')
                proficiencies: List of saves this character is proficient in
                level: Character level (for proficiency bonus calculation)
                
            Returns:
                Total saving throw modifier as integer
                
            Example:
                Fighter level 3 with STR 16, proficient in STR saves
                -> (16-10)//2 + 2 = +3 + +2 = +5
            """
            # Get base ability modifier
            ability_score = stats.get(save_type, 10)
            ability_mod = self.get_ability_modifier(ability_score)
            
            # Add proficiency bonus if proficient in this save
            if save_type in proficiencies:
                prof_bonus = self.calculate_proficiency_bonus(level)
                return ability_mod + prof_bonus
            
            # Not proficient - just ability modifier
            return ability_mod

    def calculate_spell_save_dc(self, caster_data: dict) -> int:
            """
            Calculate spell save DC for a caster
            
            Formula: 8 + proficiency_bonus + casting_stat_modifier
            
            Args:
                caster_data: Character data dict with stats, level, and class info
                
            Returns:
                Spell save DC as integer
                
            Example:
                Level 3 Wizard with INT 16 (+3 mod)
                -> 8 + 2 (prof) + 3 (INT) = DC 13
            """
            # Get caster level
            level = caster_data.get('level', 1)
            
            # Get proficiency bonus
            prof_bonus = self.calculate_proficiency_bonus(level)
            
            # Determine casting stat based on class
            char_class = caster_data.get('class', 'fighter').lower()
            
            # Map class to primary casting ability
            casting_stat_map = {
                'wizard': 'intelligence',
                'sorcerer': 'charisma',
                'warlock': 'charisma',
                'cleric': 'wisdom',
                'druid': 'wisdom',
                'ranger': 'wisdom',
                'paladin': 'charisma',
                'bard': 'charisma',
                'fighter': 'intelligence',  # Eldritch Knight subclass
                'rogue': 'intelligence'      # Arcane Trickster subclass
            }
            
            casting_stat = casting_stat_map.get(char_class, 'intelligence')
            
            # Get casting stat modifier
            stats = caster_data.get('stats', {})
            stat_value = stats.get(casting_stat, 10)
            stat_modifier = self.get_ability_modifier(stat_value)
            
            # Calculate DC
            dc = 8 + prof_bonus + stat_modifier
            
            return dc

    def get_item_by_name(self, item_name: str) -> Optional[Dict]:
        """Find item data by name OR ID"""
        if not item_name:
            return None
            
        for item in self.items_data.get('merchant_items', []):
            # Check both display name and ID
            if item['name'] == item_name or item['id'] == item_name:
                return item
        return None
    
    def calculate_armor_class(self, game_state) -> Tuple[int, List[str]]:
        """
        Calculate total Armor Class from all sources
        Returns: (total_ac, breakdown_list)
        """
        base_ac = 10
        breakdown = [f"Base: {base_ac}"]
        total_ac = base_ac
        
        # Get character stats
        dex_score = game_state.character.get('dexterity', 10)
        dex_mod = self.get_ability_modifier(dex_score)
        
        # Check equipped armor
        equipped_armor = game_state.character.get('equipped_armor')
        armor_item = self.get_item_by_name(equipped_armor) if equipped_armor else None
        
        if armor_item and 'combat_stats' in armor_item:
            armor_stats = armor_item['combat_stats']
            armor_ac = armor_stats.get('armor_class', 0)
            armor_type = armor_stats.get('armor_type', 'light')
            dex_modifier_rule = armor_stats.get('dex_modifier', 'full')
            
            # Replace base AC with armor AC (not additive)
            total_ac = armor_ac
            breakdown = [f"{equipped_armor}: {armor_ac}"]
            
            # Apply DEX modifier based on armor type
            if dex_modifier_rule == 'full':
                total_ac += dex_mod
                breakdown.append(f"DEX mod: +{dex_mod}")
            elif dex_modifier_rule == 'max_2':
                dex_bonus = min(dex_mod, 2)
                total_ac += dex_bonus
                breakdown.append(f"DEX mod (max 2): +{dex_bonus}")
            # 'none' = no DEX bonus
        else:
            # No armor - use base AC + full DEX
            total_ac += dex_mod
            breakdown.append(f"DEX mod: +{dex_mod}")
        
        # Check equipped shield
        equipped_shield = game_state.character.get('equipped_shield')
        shield_item = self.get_item_by_name(equipped_shield) if equipped_shield else None
        
        if shield_item and 'combat_stats' in shield_item:
            shield_ac = shield_item['combat_stats'].get('armor_class', 0)
            total_ac += shield_ac
            breakdown.append(f"{equipped_shield}: +{shield_ac}")
        
        # Check for AC bonuses from trinkets and special items
        self._ensure_buff_manager()
        equipment_ac_bonus, equipment_breakdown = self.buff_manager.get_effective_stat(
            'armor_class', 0, game_state
        )
        
        # Add equipment bonuses (excluding base value from breakdown)
        if equipment_ac_bonus > 0:
            total_ac += equipment_ac_bonus
            # Skip the "Base: 0" entry, just add the actual bonuses
            breakdown.extend([b for b in equipment_breakdown if not b.startswith('Base:')])
        
        return total_ac, breakdown
    
    def calculate_attacks_per_round(self, game_state) -> Tuple[int, List[str]]:
        """
        Calculate total attacks per round from class features and items
        Returns: (total_attacks, breakdown_list)
        """
        base_attacks = 1
        breakdown = [f"Base: {base_attacks}"]
        total_attacks = base_attacks
        
        # Get character class and level
        character_class = game_state.character.get('class', 'fighter')
        character_level = game_state.character.get('level', 1)
        
        # Get class attack progression
        class_info = self.class_data.get('character_classes', {}).get(character_class, {})
        combat_progression = class_info.get('combat_progression', {})
        attacks_progression = combat_progression.get('attacks_per_round', [1, 1, 1, 1, 1])
        
        if character_level <= len(attacks_progression):
            class_attacks = attacks_progression[character_level - 1]
            if class_attacks > base_attacks:
                total_attacks = class_attacks
                breakdown = [f"Class (Level {character_level}): {class_attacks}"]
        
        # Check for item bonuses (future expansion)
        # Could add magical weapons that grant extra attacks
        
        return total_attacks, breakdown
    
    def calculate_attack_bonus(self, game_state) -> Tuple[int, List[str]]:
        """
        Calculate total attack bonus from class, stats, and equipment
        Returns: (total_bonus, breakdown_list)
        """
        breakdown = []
        total_bonus = 0
        
        # Get character stats and class info
        character_class = game_state.character.get('class', 'fighter')
        character_level = game_state.character.get('level', 1)
        
        # Base Attack Bonus from class
        class_info = self.class_data.get('character_classes', {}).get(character_class, {})
        combat_progression = class_info.get('combat_progression', {})
        bab_progression = combat_progression.get('base_attack_bonus', [0, 0, 0, 0, 0])
        
        if character_level <= len(bab_progression):
            base_attack_bonus = bab_progression[character_level - 1]
            total_bonus += base_attack_bonus
            breakdown.append(f"Base Attack: +{base_attack_bonus}")
        
        # Ability modifier (depends on weapon)
        equipped_weapon = game_state.character.get('equipped_weapon')
        weapon_item = self.get_item_by_name(equipped_weapon) if equipped_weapon else None
        
        if weapon_item and 'combat_stats' in weapon_item:
            abilities_used = weapon_item['combat_stats'].get('abilities_used', ['strength'])
            
            # For finesse weapons, use the better of STR or DEX
            if 'dexterity' in abilities_used and 'strength' in abilities_used:
                str_mod = self.get_ability_modifier(game_state.character.get('strength', 10))
                dex_mod = self.get_ability_modifier(game_state.character.get('dexterity', 10))
                ability_mod = max(str_mod, dex_mod)
                ability_name = "STR" if str_mod >= dex_mod else "DEX"
            elif 'dexterity' in abilities_used:
                ability_mod = self.get_ability_modifier(game_state.character.get('dexterity', 10))
                ability_name = "DEX"
            else:
                ability_mod = self.get_ability_modifier(game_state.character.get('strength', 10))
                ability_name = "STR"
            
            total_bonus += ability_mod
            if ability_mod >= 0:
                breakdown.append(f"{ability_name} mod: +{ability_mod}")
            else:
                breakdown.append(f"{ability_name} mod: {ability_mod}")  # Will show "-1" not "+-1"
        else:
            # Default to STR for unarmed/basic attacks
            str_mod = self.get_ability_modifier(game_state.character.get('strength', 10))
            total_bonus += str_mod
            if str_mod >= 0:
                breakdown.append(f"STR mod: +{str_mod}")
            else:
                breakdown.append(f"STR mod: {str_mod}")
        
        # Weapon enhancement bonus
        if weapon_item and 'combat_stats' in weapon_item:
            weapon_bonus = weapon_item['combat_stats'].get('attack_bonus', 0)
            if weapon_bonus != 0:
                total_bonus += weapon_bonus
                breakdown.append(f"{equipped_weapon}: +{weapon_bonus}")
        
        return total_bonus, breakdown
    
    def calculate_weapon_damage(self, game_state) -> Tuple[str, List[str]]:
        """
        Calculate weapon damage with modifiers
        Returns: (damage_string, breakdown_list)
        """
        equipped_weapon = game_state.character.get('equipped_weapon')
        weapon_item = self.get_item_by_name(equipped_weapon) if equipped_weapon else None
        
        if not weapon_item or 'combat_stats' not in weapon_item:
            return "1d4", ["Unarmed: 1d4"]
        
        combat_stats = weapon_item['combat_stats']
        base_damage = combat_stats.get('damage_dice', '1d4')
        breakdown = [f"{equipped_weapon}: {base_damage}"]
        
        # Calculate ability modifier
        abilities_used = combat_stats.get('abilities_used', ['strength'])
        
        if 'dexterity' in abilities_used and 'strength' in abilities_used:
            # Finesse weapon - use better modifier
            str_mod = self.get_ability_modifier(game_state.character.get('strength', 10))
            dex_mod = self.get_ability_modifier(game_state.character.get('dexterity', 10))
            ability_mod = max(str_mod, dex_mod)
            ability_name = "STR" if str_mod >= dex_mod else "DEX"
        elif 'dexterity' in abilities_used:
            ability_mod = self.get_ability_modifier(game_state.character.get('dexterity', 10))
            ability_name = "DEX"
        else:
            ability_mod = self.get_ability_modifier(game_state.character.get('strength', 10))
            ability_name = "STR"
        
        # Build damage string
        if ability_mod > 0:
            damage_string = f"{base_damage}+{ability_mod}"
            breakdown.append(f"{ability_name} mod: +{ability_mod}")
        elif ability_mod < 0:
            damage_string = f"{base_damage}{ability_mod}"
            breakdown.append(f"{ability_name} mod: {ability_mod}")
        else:
            damage_string = base_damage
        
        return damage_string, breakdown

# Global instance
stats_calculator = StatsCalculator()

def get_stats_calculator():
    """Get the global stats calculator instance"""
    return stats_calculator