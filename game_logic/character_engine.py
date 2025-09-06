# game_logic/character_engine.py
"""
Character Management Engine - Pure Single Data Authority Pattern
GameState = THE authoritative data source
CharacterEngine = Pure business logic processor
"""

import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class CharacterEngine:
    """
    Centralized character management following Single Data Authority pattern
    
    This engine handles ALL character-related business logic:
    - Stat rolling with reroll-ones mechanism
    - Hit point calculation
    - Character class management (fighter, future classes)
    - Level progression system
    - Stat validation and modification
    
    GameState remains THE single source of truth for all data.
    """
    
    def __init__(self, game_state_ref):
        """
        Initialize with GameState reference (Single Data Authority pattern)
        
        Args:
            game_state_ref: Reference to GameState (the data authority)
        """
        self.game_state = game_state_ref
        print("🏗️ CharacterEngine initialized with Single Data Authority pattern")
    
    # ==========================================
    # CHARACTER CREATION OPERATIONS
    # ==========================================
    
    def roll_stats(self, reroll_ones=True):
        """
        Roll character stats with optional reroll-ones mechanism
        Updates GameState character stats directly
        
        Args:
            reroll_ones: If True, reroll any 1s rolled on dice
            
        Returns:
            dict: The rolled stats
        """
        stats = {}
        stat_names = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        
        for stat in stat_names:
            # Roll 3d6 for each stat
            rolls = []
            for _ in range(3):
                roll = random.randint(1, 6)
                # Reroll 1s if enabled (your proven mechanic)
                if reroll_ones and roll == 1:
                    roll = random.randint(1, 6)
                rolls.append(roll)
            
            stats[stat] = sum(rolls)
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character.update(stats)
        
        print(f"🎲 Character stats rolled: {stats}")
        return stats
    # def register_stat_events(self, event_manager):
    #     """Register this engine for stat-related events"""
    #     self.event_manager = event_manager
        
    #     # Wire events directly to existing methods
    #     event_manager.register('REROLL_STATS', self._handle_reroll_stats)
    #     event_manager.register('KEEP_STATS', self._handle_keep_stats)
    #     print("📝 CharacterEngine registered for stat events")

    def _handle_reroll_stats(self, event_data):
        """Event wrapper for roll_stats - just adds logging"""
        print("🎲 CharacterEngine: REROLL_STATS event received")
        self.roll_stats(reroll_ones=True)  # Use existing method!
        self.game_state.stats_rolled = True

    def _handle_keep_stats(self, event_data):
        """Handle KEEP_STATS - finalize and navigate"""
        print("✅ CharacterEngine: KEEP_STATS event received")
        # Emit navigation event
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'gender'})

    def register_character_creation_events(self, event_manager):
        """Register this engine for all character creation events"""
        self.event_manager = event_manager
        
        # Stat events (existing)
        event_manager.register('REROLL_STATS', self._handle_reroll_stats)
        event_manager.register('KEEP_STATS', self._handle_keep_stats)
        
        # Gender events (new)
        event_manager.register('SELECT_MALE', self._handle_select_male)
        event_manager.register('SELECT_FEMALE', self._handle_select_female)
        
        print("🎯 CharacterEngine registered for all character creation events")

    def _handle_select_male(self, event_data):
        """Handle SELECT_MALE - set gender and navigate"""
        print("🚹 CharacterEngine: SELECT_MALE event received")
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['gender'] = 'male'
        
        # Emit navigation event to next screen
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'portrait_selection'})

    def _handle_select_female(self, event_data):
        """Handle SELECT_FEMALE - set gender and navigate"""
        print("🚺 CharacterEngine: SELECT_FEMALE event received")
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['gender'] = 'female'
        
        # Emit navigation event to next screen
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'portrait_selection'})

    def calculate_hp(self, constitution_score=None, character_class=None):
        """
        Calculate hit points based on constitution score and class
        
        Args:
            constitution_score: Optional override, uses GameState if not provided
            character_class: Optional override, uses GameState if not provided
            
        Returns:
            int: Calculated hit points
        """
        if constitution_score is None:
            constitution_score = self.game_state.character.get('constitution', 10)
        
        if character_class is None:
            character_class = self.game_state.character.get('class', 'fighter')
        
        # Get class-specific hit die
        class_data = self._get_class_data(character_class)
        hit_die = class_data.get('hit_die', 10) if class_data else 10
        
        # Calculate constitution modifier
        constitution_modifier = (constitution_score - 10) // 2
        
        # HP = max hit die + constitution modifier (level 1)
        hit_points = hit_die + constitution_modifier
        
        # Minimum 1 HP (safety check)
        hit_points = max(1, hit_points)
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['hit_points'] = hit_points
        
        return hit_points
    
    def roll_starting_gold(self, character_class=None):
        """
        Roll starting gold based on character class
        
        Args:
            character_class: Optional override, uses GameState if not provided
            
        Returns:
            int: Starting gold amount
        """
        if character_class is None:
            character_class = self.game_state.character.get('class', 'fighter')
        
        class_data = self._get_class_data(character_class)
        if class_data and 'starting_gold' in class_data:
            gold_data = class_data['starting_gold']
            base_dice = gold_data.get('base', 5)
            multiplier = gold_data.get('multiplier', 5)
            
            # Roll base dice and multiply
            roll_total = 0
            for _ in range(base_dice):
                roll_total += random.randint(1, 6)
            
            starting_gold = roll_total * multiplier
        else:
            # Fallback: 5d6 * 5 (fighter default)
            roll_total = sum(random.randint(1, 6) for _ in range(5))
            starting_gold = roll_total * 5
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['gold'] = starting_gold
        
        print(f"💰 Starting gold: {starting_gold} gp")
        return starting_gold
    
    def roll_trinket(self):
        """
        Roll for a mysterious starting trinket
        Classic D&D-style random trinket table
        
        Returns:
            str: Description of the rolled trinket
        """
        trinket_table = [
            "A small brass key with no lock in sight",
            "Smooth river stone with ancient runes carved deep",
            "Tiny glass vial filled with swirling purple mist",
            "Silver coin from a kingdom that no longer exists",
            "Wooden dice that always show the same number",
            "Fragment of a star map drawn on worn parchment",
            "Iron ring that grows cold near undead creatures",
            "Pressed flower from your childhood home",
            "Small leather pouch that jingles but appears empty",
            "Broken compass that points toward magic instead of north"
        ]
        
        trinket = random.choice(trinket_table)
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['trinket'] = trinket
        
        print(f"✨ Rolled trinket: {trinket}")
        return trinket
    
    def set_character_class(self, character_class='fighter'):
        """
        Set character class with full framework support
        
        Args:
            character_class: Class name ('fighter', 'wizard', 'rogue', 'cleric')
        """
        class_data = self._get_class_data(character_class)
        
        if not class_data:
            print(f"⚠️ Invalid class {character_class}, defaulting to fighter")
            character_class = 'fighter'
            class_data = self._get_class_data('fighter')
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['class'] = character_class
        self.game_state.character['class_data'] = class_data
        
        print(f"⚔️ Character class set to: {character_class}")
        return character_class
    
    def _get_class_data(self, character_class):
        """
        Get class-specific data for character creation and progression
        
        Returns:
            dict: Class data including equipment, abilities, progression
        """
        class_definitions = {
            'fighter': {
                'name': 'Fighter',
                'description': 'A master of martial combat, skilled with various weapons and armor',
                'hit_die': 10,  # d10 for HP per level
                'primary_stats': ['strength', 'constitution'],
                'starting_equipment': {
                    'weapon': 'Longsword',
                    'armor': 'Leather Armor', 
                    'shield': 'Shield',
                    'items': ['Hemp Rope']
                },
                'starting_gold': {'base': 5, 'multiplier': 5},  # 5d6 * 5 gold
                'abilities': {
                    'level_1': ['Combat Training', 'Weapon Mastery'],
                    'level_2': ['Action Surge'],
                    'level_3': ['Second Wind'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['Extra Attack']
                }
            },
            'wizard': {
                'name': 'Wizard',
                'description': 'A scholarly magic-user capable of manipulating arcane forces',
                'hit_die': 6,  # d6 for HP per level
                'primary_stats': ['intelligence', 'wisdom'],
                'starting_equipment': {
                    'weapon': 'Quarterstaff',
                    'armor': 'Robes',
                    'shield': None,
                    'items': ['Spellbook', 'Component Pouch']
                },
                'starting_gold': {'base': 3, 'multiplier': 10},  # 3d6 * 10 gold
                'abilities': {
                    'level_1': ['Spellcasting', 'Arcane Recovery'],
                    'level_2': ['School of Magic'],
                    'level_3': ['Cantrip Mastery'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['3rd Level Spells']
                },
                'spells_known': {
                    'level_1': ['Magic Missile', 'Shield', 'Detect Magic'],
                    'cantrips': ['Light', 'Mage Hand', 'Prestidigitation']
                }
            },
            'rogue': {
                'name': 'Rogue',
                'description': 'A scoundrel who uses stealth and trickery to overcome obstacles',
                'hit_die': 8,  # d8 for HP per level
                'primary_stats': ['dexterity', 'intelligence'],
                'starting_equipment': {
                    'weapon': 'Shortsword',
                    'armor': 'Leather Armor',
                    'shield': None,
                    'items': ['Thieves Tools', 'Daggers (2)']
                },
                'starting_gold': {'base': 4, 'multiplier': 4},  # 4d6 * 4 gold
                'abilities': {
                    'level_1': ['Sneak Attack', 'Thieves Cant'],
                    'level_2': ['Cunning Action'],
                    'level_3': ['Roguish Archetype'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['Uncanny Dodge']
                }
            },
            'cleric': {
                'name': 'Cleric',
                'description': 'A priestly champion who wields divine magic in service of a higher power',
                'hit_die': 8,  # d8 for HP per level
                'primary_stats': ['wisdom', 'constitution'],
                'starting_equipment': {
                    'weapon': 'Mace',
                    'armor': 'Scale Mail',
                    'shield': 'Shield',
                    'items': ['Holy Symbol', 'Prayer Book']
                },
                'starting_gold': {'base': 5, 'multiplier': 4},  # 5d6 * 4 gold
                'abilities': {
                    'level_1': ['Divine Magic', 'Turn Undead'],
                    'level_2': ['Channel Divinity'],
                    'level_3': ['Divine Domain'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['3rd Level Spells']
                },
                'spells_known': {
                    'level_1': ['Cure Wounds', 'Bless', 'Detect Evil'],
                    'cantrips': ['Sacred Flame', 'Light', 'Thaumaturgy']
                }
            }
        }
        
        return class_definitions.get(character_class.lower())
    
    # ==========================================
    # CHARACTER PROGRESSION OPERATIONS
    # ==========================================
    
    def can_level_up(self):
        """
        Check if character has enough experience to level up
        
        Returns:
            bool: True if character can level up
        """
        current_level = self.game_state.character.get('level', 1)
        current_xp = self.game_state.character.get('experience', 0)
        
        # Simple XP table for levels 1-5
        xp_requirements = {
            1: 0,
            2: 300,
            3: 900,
            4: 2700,
            5: 6500
        }
        
        next_level = current_level + 1
        if next_level <= 5 and current_xp >= xp_requirements.get(next_level, 999999):
            return True
        
        return False
    
    def level_up(self):
        """
        Perform level up operation with class-specific progression
        Increases level, recalculates HP, grants improvements
        
        Returns:
            dict: Level up results (new level, hp gain, abilities gained, etc.)
        """
        if not self.can_level_up():
            print("❌ Character cannot level up yet")
            return None
        
        current_level = self.game_state.character.get('level', 1)
        new_level = current_level + 1
        character_class = self.game_state.character.get('class', 'fighter')
        
        # Get class-specific data
        class_data = self._get_class_data(character_class)
        hit_die = class_data.get('hit_die', 10) if class_data else 10
        
        # Roll for HP gain (class hit die + con modifier per level)
        constitution_modifier = (self.game_state.character.get('constitution', 10) - 10) // 2
        hp_gain = random.randint(1, hit_die) + constitution_modifier
        hp_gain = max(1, hp_gain)  # Minimum 1 HP per level
        
        # Get new abilities for this level
        new_abilities = []
        if class_data and 'abilities' in class_data:
            level_key = f'level_{new_level}'
            new_abilities = class_data['abilities'].get(level_key, [])
        
        # Update character stats in GameState (Single Data Authority)
        self.game_state.character['level'] = new_level
        current_hp = self.game_state.character.get('hit_points', 10)
        self.game_state.character['hit_points'] = current_hp + hp_gain
        
        # Track abilities gained
        if 'abilities' not in self.game_state.character:
            self.game_state.character['abilities'] = []
        self.game_state.character['abilities'].extend(new_abilities)
        
        level_up_results = {
            'new_level': new_level,
            'hp_gain': hp_gain,
            'new_total_hp': self.game_state.character['hit_points'],
            'abilities_gained': new_abilities,
            'class': character_class
        }
        
        print(f"🎊 LEVEL UP! Now level {new_level} {character_class.title()}, gained {hp_gain} HP")
        if new_abilities:
            print(f"📚 New abilities: {', '.join(new_abilities)}")
        
        return level_up_results
    
    def award_experience(self, xp_amount, reason=""):
        """
        Award experience points to character based on different sources
        
        Args:
            xp_amount: Amount of XP to award
            reason: Optional description of why XP was awarded
        """
        current_xp = self.game_state.character.get('experience', 0)
        new_xp = current_xp + xp_amount
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['experience'] = new_xp
        
        print(f"⭐ Awarded {xp_amount} XP! {reason}")
        print(f"   Total XP: {new_xp}")
        
        # Check for level up opportunity
        if self.can_level_up():
            print("🎊 Ready to level up!")
        
        return new_xp
    
    def award_combat_xp(self, enemy_level=1, enemy_count=1):
        """Award XP for combat victories"""
        base_xp = enemy_level * 100
        total_xp = base_xp * enemy_count
        return self.award_experience(total_xp, f"defeated {enemy_count} enemies")
    
    def award_quest_xp(self, quest_difficulty='normal'):
        """Award XP for quest completion"""
        xp_values = {'easy': 150, 'normal': 300, 'hard': 500, 'epic': 1000}
        xp = xp_values.get(quest_difficulty, 300)
        return self.award_experience(xp, f"completed {quest_difficulty} quest")
    
    def award_skill_xp(self, skill_success=True):
        """Award XP for successful skill achievements"""
        if skill_success:
            return self.award_experience(50, "successful skill achievement")
        return 0
    
    def award_gambling_streak_xp(self, streak_length):
        """Award XP for gambling streaks of 3 or more"""
        if streak_length >= 3:
            xp = min(100, streak_length * 20)  # Cap at 100 XP
            return self.award_experience(xp, f"gambling streak of {streak_length}")
        return 0
    
    # ==========================================
    # CHARACTER VALIDATION & UTILITY
    # ==========================================
    
    def validate_character(self):
        """
        Validate character data integrity
        Ensures all required fields exist with valid values
        
        Returns:
            bool: True if character data is valid
        """
        required_fields = ['name', 'class', 'strength', 'dexterity', 'constitution', 
                          'intelligence', 'wisdom', 'charisma', 'hit_points', 'gold']
        
        for field in required_fields:
            if field not in self.game_state.character:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Validate stat ranges (3-18 for standard D&D)
        stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for stat in stats:
            value = self.game_state.character.get(stat, 0)
            if not (3 <= value <= 18):
                print(f"❌ Invalid {stat} value: {value} (must be 3-18)")
                return False
        
        print("✅ Character data validated successfully")
        return True
    
    def get_character_summary(self):
        """
        Get formatted character summary for display
        
        Returns:
            dict: Character summary data
        """
        char = self.game_state.character
        
        summary = {
            'name': char.get('name', 'Unknown'),
            'class': char.get('class', 'fighter').title(),
            'level': char.get('level', 1),
            'hit_points': char.get('hit_points', 10),
            'experience': char.get('experience', 0),
            'stats': {
                'Strength': char.get('strength', 10),
                'Dexterity': char.get('dexterity', 10),
                'Constitution': char.get('constitution', 10),
                'Intelligence': char.get('intelligence', 10),
                'Wisdom': char.get('wisdom', 10),
                'Charisma': char.get('charisma', 10)
            },
            'equipment': {
                'weapon': char.get('equipped_weapon', 'Longsword'),
                'armor': char.get('equipped_armor', 'Leather Armor'),
                'shield': char.get('equipped_shield', 'Shield')
            }
        }
        
        return summary
    
    def finalize_character_creation(self):
        """
        Complete character creation process with class-specific setup
        Performs final calculations and validations
        """
        character_class = self.game_state.character.get('class', 'fighter')
        
        # Calculate class-specific starting stats
        if 'hit_points' not in self.game_state.character:
            self.calculate_hp()
        
        # Set starting level and XP
        self.game_state.character['level'] = 1
        self.game_state.character['experience'] = 0
        
        # Roll starting gold based on class
        if 'gold' not in self.game_state.character:
            self.roll_starting_gold()
        
        # Set up starting equipment based on class
        class_data = self._get_class_data(character_class)
        if class_data and 'starting_equipment' in class_data:
            starting_equipment = class_data['starting_equipment']
            
            # Add weapons to inventory
            if starting_equipment.get('weapon'):
                if 'weapons' not in self.game_state.inventory:
                    self.game_state.inventory['weapons'] = []
                weapon = starting_equipment['weapon']
                self.game_state.inventory['weapons'].append(weapon)
                self.game_state.character['equipped_weapon'] = weapon
            
            # Add armor to inventory
            if starting_equipment.get('armor'):
                if 'armor' not in self.game_state.inventory:
                    self.game_state.inventory['armor'] = []
                armor = starting_equipment['armor']
                self.game_state.inventory['armor'].append(armor)
                self.game_state.character['equipped_armor'] = armor
            
            # Add shield if applicable
            if starting_equipment.get('shield'):
                shield = starting_equipment['shield']
                self.game_state.inventory['armor'].append(shield)
                self.game_state.character['equipped_shield'] = shield
            
            # Add class-specific items
            class_items = starting_equipment.get('items', [])
            if 'items' not in self.game_state.inventory:
                self.game_state.inventory['items'] = []
            self.game_state.inventory['items'].extend(class_items)
        
        # Add trinket to inventory if it exists
        trinket = self.game_state.character.get('trinket')
        if trinket and trinket != 'None':
            if 'items' not in self.game_state.inventory:
                self.game_state.inventory['items'] = []
            self.game_state.inventory['items'].append(trinket)
        
        # Set up class-specific abilities
        if class_data and 'abilities' in class_data:
            level_1_abilities = class_data['abilities'].get('level_1', [])
            self.game_state.character['abilities'] = level_1_abilities.copy()
        
        # Set up spells for casters
        if class_data and 'spells_known' in class_data:
            self.game_state.character['spells'] = class_data['spells_known'].copy()
        
        # Validate the completed character
        is_valid = self.validate_character()
        
        if is_valid:
            print("✅ Character creation finalized successfully!")
            char_name = self.game_state.character.get('name', 'Unknown Hero')
            char_class = self.game_state.character.get('class', 'fighter').title()
            print(f"🎭 Welcome to Redstone, {char_name} the {char_class}!")
        else:
            print("❌ Character creation validation failed!")
        
        return is_valid


# ==========================================
# GLOBAL CHARACTER ENGINE MANAGEMENT
# ==========================================

# Global character engine instance (initialized by DataManager)
character_engine = None

def get_character_engine():
    """
    Get the global character engine instance
    Will be initialized by DataManager integration
    """
    return character_engine

def initialize_character_engine(game_state_ref, event_manager=None):
    """
    Initialize the global character engine with event management
    """
    global character_engine
    character_engine = CharacterEngine(game_state_ref)
    
    # Register for stat events if event manager provided
    if event_manager:
        character_engine.register_character_creation_events(event_manager)
        print("📝 CharacterEngine registered for character creation events")
    else:
        print("⚠️ No EventManager provided to CharacterEngine")
    
    print("🔧 Initialized CharacterEngine")
    return character_engine


# Development and testing utilities
if __name__ == "__main__":
    print("🧪 CharacterEngine Development Test")
    print("=" * 50)
    
    print("CharacterEngine follows Single Data Authority pattern:")
    print("- GameState = THE authoritative data source")
    print("- CharacterEngine = Pure business logic processor")
    print("- No data storage in engine itself")
    print("- All operations modify GameState directly")
    print("- Supports character creation AND progression (levels 1-5)")
    
    print("\n✅ CharacterEngine module loaded successfully!")