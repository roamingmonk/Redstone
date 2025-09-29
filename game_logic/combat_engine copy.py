# game_logic/combat_engine.py
"""
CombatEngine - Step 1: Basic Integration Test
Pure business logic processor - NO UI code
"""

from enum import Enum
from typing import Dict, Any, Optional, List
import random
from utils.combat_loader import CombatLoader
from utils.stats_calculator import get_stats_calculator

class CombatState(Enum):
    """Combat state tracking"""
    NOT_STARTED = "not_started"
    ACTIVE = "active" 
    VICTORY = "victory"
    DEFEAT = "defeat"

class CombatEngine:
    """
    Combat Engine - Step 2: Professional Combat Integration
    
    Handles all combat logic using StatsCalculator for professional RPG calculations.
    Integrates with GameState for character data and equipment.
    """
    
    def __init__(self, event_manager, game_state, data_manager=None):
        """
        Initialize CombatEngine with StatsCalculator integration
        """
        self.event_manager = event_manager
        self.game_state = game_state
        self.data_manager = data_manager
        
        # Initialize systems
        self.combat_loader = CombatLoader()
        self.stats_calculator = get_stats_calculator()
        
        # Combat state
        self.combat_state = CombatState.NOT_STARTED
        self.current_encounter = None
        self.current_battlefield = None
        self.enemies = []
        self.combat_log = []
        
        # Turn management
        self.current_turn = 0
        self.current_character_index = 0
        self.player_has_moved = False
        self.player_has_acted = False
        
        print("⚔️ CombatEngine initialized with StatsCalculator integration")
    
    def start_combat(self, encounter_id: str) -> bool:
        """Start combat with real data and stats calculation"""
        try:
            print(f"🎯 Starting combat: {encounter_id}")
            
            # Load encounter data
            encounter_data = self.combat_loader.get_encounter_with_dependencies(encounter_id)
            if not encounter_data:
                return False
            
            self.current_encounter = encounter_data
            self.current_battlefield = encounter_data.get('battlefield_data')
            
            # Create enemies with calculated stats
            self.enemies = self._create_enemy_instances(encounter_data.get('enemies_data', []))
            
            # Initialize player combat position
            player_positions = encounter_data.get('player_party', {}).get('starting_positions', [[1, 6]])
            self.game_state.character['combat_position'] = player_positions[0]
            
            # Set combat state
            self.combat_state = CombatState.ACTIVE
            self.current_turn = 1
            self.current_character_index = 0  # Player goes first
            self.player_has_moved = False
            self.player_has_acted = False
            
            encounter_name = encounter_data.get('name', encounter_id)
            self.combat_log = [f"Combat begins: {encounter_name}"]
            
            # Add player stats to log
            player_ac, _ = self.stats_calculator.calculate_armor_class(self.game_state)
            player_attacks, _ = self.stats_calculator.calculate_attacks_per_round(self.game_state)
            self.combat_log.append(f"Player AC: {player_ac}, Attacks: {player_attacks}")
            
            self.event_manager.emit("COMBAT_STARTED", {
                "encounter_id": encounter_id,
                "encounter_name": encounter_name,
                "enemy_count": len(self.enemies)
            })
            
            return True
            
        except Exception as e:
            print(f"❌ Combat start failed: {e}")
            return False
    
    def execute_player_attack(self, target_enemy_index: int, attack_type: str = "auto") -> Dict[str, Any]:
        """
        Execute player attack using StatsCalculator for real damage
        
        Args:
            target_enemy_index: Index of enemy to attack
            attack_type: "melee", "ranged", or "auto" (determine by distance)
            
        Returns:
            Attack result dictionary
        """
        if not self._can_player_act():
            return {"success": False, "message": "Player cannot act"}
        
        if target_enemy_index >= len(self.enemies) or not self.enemies[target_enemy_index]['is_alive']:
            return {"success": False, "message": "Invalid target"}
        
        target = self.enemies[target_enemy_index]
        player_pos = self.game_state.character.get('combat_position', [1, 6])
        target_pos = target['position']
        
        # Calculate distance (Manhattan distance)
        distance = abs(player_pos[0] - target_pos[0]) + abs(player_pos[1] - target_pos[1])
        
        # Determine attack type
        if attack_type == "auto":
            attack_type = "melee" if distance <= 1 else "ranged"
        
        # Validate attack type by distance
        if attack_type == "melee" and distance > 1:
            return {"success": False, "message": "Target too far for melee attack"}
        
        # Calculate attack using StatsCalculator
        attack_bonus, attack_breakdown = self.stats_calculator.calculate_attack_bonus(self.game_state)
        damage_string, damage_breakdown = self.stats_calculator.calculate_weapon_damage(self.game_state)
        
        # Roll attack (simplified - d20 + bonus vs target AC)
        attack_roll = random.randint(1, 20)
        total_attack = attack_roll + attack_bonus
        target_ac = target['stats'].get('ac', 10)
        
        hit = total_attack >= target_ac
        
        result = {
            "success": True,
            "attack_type": attack_type,
            "hit": hit,
            "attack_roll": attack_roll,
            "attack_bonus": attack_bonus,
            "total_attack": total_attack,
            "target_ac": target_ac,
            "damage": 0,
            "target_name": target['name']
        }
        
        if hit:
            # Roll damage using the damage string from StatsCalculator
            damage = self._roll_damage_string(damage_string)
            actual_damage = self._apply_damage_to_enemy(target, damage)
            
            result["damage"] = actual_damage
            result["target_hp"] = target['stats']['current_hp']
            result["target_defeated"] = not target['is_alive']
            
            # Log the attack
            self.combat_log.append(
                f"Player {attack_type} attack: {attack_roll}+{attack_bonus}={total_attack} vs AC {target_ac} - HIT!"
            )
            self.combat_log.append(
                f"Damage: {actual_damage} to {target['name']} ({target['stats']['current_hp']}/{target['stats']['hp']} HP)"
            )
            
            if not target['is_alive']:
                self.combat_log.append(f"{target['name']} is defeated!")
                
        else:
            self.combat_log.append(
                f"Player {attack_type} attack: {attack_roll}+{attack_bonus}={total_attack} vs AC {target_ac} - MISS!"
            )
        
        # Mark player as having acted
        self.player_has_acted = True
        
        # Check for victory
        if self._check_victory():
            self._end_combat("victory")
        
        return result
    
    def execute_player_move(self, new_position: List[int]) -> Dict[str, Any]:
        """
        Execute player movement with validation
        
        Args:
            new_position: [x, y] coordinates to move to
            
        Returns:
            Movement result dictionary
        """
        if not self._can_player_move():
            return {"success": False, "message": "Player cannot move"}
        
        current_pos = self.game_state.character.get('combat_position', [1, 6])
        
        # Calculate movement distance (simplified - allow 1 tile movement)
        distance = abs(new_position[0] - current_pos[0]) + abs(new_position[1] - current_pos[1])
        
        if distance > 1:  # Can expand this based on character speed
            return {"success": False, "message": "Move too far"}
        
        # Validate position is within battlefield
        if not self._is_valid_position(new_position):
            return {"success": False, "message": "Invalid position"}
        
        # Check for obstacles (will implement with battlefield data)
        if self._position_blocked(new_position):
            return {"success": False, "message": "Position blocked"}
        
        # Execute move
        old_position = current_pos.copy()
        self.game_state.character['combat_position'] = new_position
        self.player_has_moved = True
        
        self.combat_log.append(f"Player moves from {old_position} to {new_position}")
        
        return {
            "success": True,
            "old_position": old_position,
            "new_position": new_position
        }
    
    def reset_player_turn(self):
        """Reset player turn flags - from demo logic"""
        self.player_has_moved = False
        self.player_has_acted = False

    def next_turn(self):
        """Advance to next turn - from demo logic"""
        self.current_turn += 1
        self.reset_player_turn()
        
        # Process enemy turns
        self._process_enemy_turns()

    def _get_enemy_at_position(self, grid_pos):
        """Check if there's an enemy at the given position"""
        for enemy in self.enemies:
            if enemy['is_alive'] and enemy['position'] == grid_pos:
                return enemy
        return None
    
    def _process_enemy_turns(self):
        """Process AI turns for all living enemies"""
        for enemy in self.enemies:
            if enemy['is_alive']:
                self._process_single_enemy_turn(enemy)

    def _process_single_enemy_turn(self, enemy):
        """Process one enemy's turn - move toward player and attack if adjacent"""
        player_pos = self.game_state.character.get('combat_position', [1, 6])
        enemy_pos = enemy['position']
        
        # Calculate distance to player
        distance = abs(player_pos[0] - enemy_pos[0]) + abs(player_pos[1] - enemy_pos[1])
        
        if distance == 1:
            # Adjacent - attack player
            damage = 3  # Simple damage for now
            self.combat_log.append(f"{enemy['name']} attacks player for {damage} damage!")
            print(f"Enemy {enemy['name']} attacks for {damage} damage")
        else:
            # Move one step toward player
            dx = 1 if player_pos[0] > enemy_pos[0] else -1 if player_pos[0] < enemy_pos[0] else 0
            dy = 1 if player_pos[1] > enemy_pos[1] else -1 if player_pos[1] < enemy_pos[1] else 0
            
            new_pos = [enemy_pos[0] + dx, enemy_pos[1]]
            if self._is_valid_position(new_pos) and not self._position_blocked(new_pos):
                enemy['position'] = new_pos
                self.combat_log.append(f"{enemy['name']} moves closer")
            else:
                new_pos = [enemy_pos[0], enemy_pos[1] + dy]  
                if self._is_valid_position(new_pos) and not self._position_blocked(new_pos):
                    enemy['position'] = new_pos
                    self.combat_log.append(f"{enemy['name']} moves closer")

    def _enemy_attack_player(self, enemy):
        """Enemy attacks the player"""
        # Basic attack logic - you can expand this later
        damage = 3  # Simple fixed damage for now
        self.combat_log.append(f"{enemy['name']} attacks player for {damage} damage!")

    def _move_enemy_toward_player(self, enemy, player_pos):
        """Move enemy one step toward player"""
        # Simple pathfinding - move in the direction that reduces distance
        enemy_pos = enemy['position']
        
        # Determine best move direction
        dx = 1 if player_pos[0] > enemy_pos[0] else -1 if player_pos[0] < enemy_pos[0] else 0
        dy = 1 if player_pos[1] > enemy_pos[1] else -1 if player_pos[1] < enemy_pos[1] else 0
        
        # Try to move (prioritize x-axis movement)
        new_pos = [enemy_pos[0] + dx, enemy_pos[1]]
        if self._is_valid_position(new_pos) and not self._position_blocked(new_pos):
            enemy['position'] = new_pos
            self.combat_log.append(f"{enemy['name']} moves closer")
        else:
            # Try y-axis movement instead
            new_pos = [enemy_pos[0], enemy_pos[1] + dy]
            if self._is_valid_position(new_pos) and not self._position_blocked(new_pos):
                enemy['position'] = new_pos
                self.combat_log.append(f"{enemy['name']} moves closer")







    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    def _roll_damage_string(self, damage_string: str) -> int:
        """
        Roll damage from a string like "1d8+2" or "2d6+4"
        
        Args:
            damage_string: Damage string from StatsCalculator
            
        Returns:
            Total damage rolled
        """
        try:
            # Parse damage string (e.g., "1d8+2")
            if '+' in damage_string:
                dice_part, bonus = damage_string.split('+')
                bonus = int(bonus)
            elif '-' in damage_string:
                dice_part, bonus_str = damage_string.split('-')
                bonus = -int(bonus_str)
            else:
                dice_part = damage_string
                bonus = 0
            
            # Parse dice (e.g., "1d8")
            if 'd' in dice_part:
                num_dice, die_size = dice_part.split('d')
                num_dice = int(num_dice)
                die_size = int(die_size)
                
                # Roll dice
                total = sum(random.randint(1, die_size) for _ in range(num_dice))
                return total + bonus
            else:
                # Just a flat number
                return int(dice_part) + bonus
                
        except (ValueError, IndexError):
            print(f"⚠️ Invalid damage string: {damage_string}")
            return 1  # Minimum damage
    

    
    def _apply_damage_to_enemy(self, enemy: Dict[str, Any], damage: int) -> int:
        """Apply damage to enemy and update status"""
        current_hp = enemy['stats'].get('current_hp', enemy['stats'].get('hp', 1))
        new_hp = max(0, current_hp - damage)
        enemy['stats']['current_hp'] = new_hp
        
        if new_hp <= 0:
            enemy['is_alive'] = False
        
        return damage  # Return actual damage dealt
    
    def _can_player_move(self) -> bool:
        """Check if player can move this turn"""
        return (self.combat_state == CombatState.ACTIVE and 
                self.current_character_index == 0 and 
                not self.player_has_moved)
    
    def _can_player_act(self) -> bool:
        """Check if player can act this turn"""
        return (self.combat_state == CombatState.ACTIVE and 
                self.current_character_index == 0 and 
                not self.player_has_acted)
    
    def _is_valid_position(self, position: List[int]) -> bool:
        """Check if position is within battlefield bounds"""
        if not self.current_battlefield:
            return True  # No battlefield restrictions
        
        dimensions = self.current_battlefield.get('dimensions', {})
        width = dimensions.get('width', 12)
        height = dimensions.get('height', 8)
        
        x, y = position
        return 0 <= x < width and 0 <= y < height
    
    def _position_blocked(self, position: List[int]) -> bool:
        """Check if position is blocked by obstacles or other characters"""
        # Check against enemies
        for enemy in self.enemies:
            if enemy['is_alive'] and enemy['position'] == position:
                return True
        
        # Check against battlefield obstacles (future implementation)
        if self.current_battlefield:
            obstacles = self.current_battlefield.get('terrain', {}).get('obstacles', [])
            for obstacle in obstacles:
                if obstacle.get('position') == position and obstacle.get('blocks_movement', False):
                    return True
        
        return False
    
    def _check_victory(self) -> bool:
        """Check if all enemies are defeated"""
        return all(not enemy['is_alive'] for enemy in self.enemies)
    
    def _check_defeat(self) -> bool:
        """Check if player is defeated (placeholder)"""
        # This would check player HP when we implement player damage
        return False
    
    def _end_combat(self, result: str):
        """End combat and apply rewards"""
        if result == "victory":
            self.combat_state = CombatState.VICTORY
            rewards = self.current_encounter.get('rewards', {})
            xp = rewards.get('xp', 0)
            gold = rewards.get('gold', 0)
            
            # Apply rewards to player
            current_xp = self.game_state.character.get('experience', 0)
            current_gold = self.game_state.character.get('gold', 0)
            
            self.game_state.character['experience'] = current_xp + xp
            self.game_state.character['gold'] = current_gold + gold
            
            self.combat_log.append(f"Victory! Gained {xp} XP and {gold} gold.")
            
        elif result == "defeat":
            self.combat_state = CombatState.DEFEAT
            self.combat_log.append("Defeat!")
    
    def get_combat_data_for_ui(self) -> Dict[str, Any]:
        """
        Get combat data formatted for UI display - Step 2: Real Data
        
        Returns:
            Dictionary with all data needed for UI rendering
        """
        
        if not self.current_encounter:
            return {
                "encounter_name": "No Active Encounter",
                "state": self.combat_state.value,
                "combat_log": ["No combat active"],
                "battlefield": None,
                "enemies": [],
                "player_position": [0, 0]
            }
        
        return {
            "encounter_name": self.current_encounter.get('name', 'Unknown Encounter'),
            "encounter_id": self.current_encounter.get('encounter_id', 'unknown'),
            "state": self.combat_state.value,
            "combat_log": self.combat_log.copy(),
            "battlefield": self.current_battlefield,
            "enemies": [self._format_enemy_for_ui(enemy) for enemy in self.enemies if enemy['is_alive']],
            "all_enemies": self.enemies.copy(),  # Include defeated enemies for UI
            "player_position": self.game_state.character.get('combat_position', [1, 6]),
            "turn_info": self._get_turn_info()
        }
    
    def _format_enemy_for_ui(self, enemy: Dict[str, Any]) -> Dict[str, Any]:
        """Format enemy data for UI display"""
        return {
            'name': enemy['name'],
            'position': enemy['position'],
            'current_hp': enemy['stats'].get('current_hp', 0),
            'max_hp': enemy['stats'].get('hp', 0),
            'is_alive': enemy['is_alive'],
            'facing': enemy['facing']
        }
   
    def _get_turn_info(self) -> Dict[str, Any]:
        """Get current turn information"""
        return {
            'current_phase': 'player_turn',  # Will expand this later
            'actions_remaining': 2,  # Move + Action
            'can_move': True,
            'can_attack': True
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

    def _create_enemy_instances(self, enemies_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create enemy instances from loaded JSON data
        
        Args:
            enemies_data: List of enemy configurations from encounter
            
        Returns:
            List of enemy instances ready for combat
        """
        enemy_instances = []
        
        for enemy_config in enemies_data:
            try:
                # Create enemy instance
                enemy = {
                    'id': enemy_config.get('enemy_id', 'unknown'),
                    'name': enemy_config.get('name', 'Unknown Enemy'),
                    'position': enemy_config.get('position', [0, 0]),
                    'facing': enemy_config.get('facing', 'north'),
                    'stats': enemy_config.get('stats', {}).copy(),
                    'attacks': enemy_config.get('attacks', []),
                    'movement': enemy_config.get('movement', {'speed': 1}),
                    'behavior': enemy_config.get('behavior', {'tactics': 'basic'}),
                    'is_alive': True,
                    'has_moved': False,
                    'has_acted': False
                }
                
                # Ensure enemy has current HP
                if 'hp' in enemy['stats'] and 'current_hp' not in enemy['stats']:
                    enemy['stats']['current_hp'] = enemy['stats']['hp']
                
                enemy_instances.append(enemy)
                print(f"   🐾 Created enemy: {enemy['name']} at {enemy['position']}")
                
            except Exception as e:
                print(f"❌ Error creating enemy instance: {e}")
                continue
        
        return enemy_instances

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