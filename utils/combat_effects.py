# utils/combat_effects.py
"""
Combat Effects System - Universal effect resolution for all combat actions
Handles damage, healing, buffs, debuffs, and status changes

Philosophy: ANY combat action (spell, attack, ability, item) is just an "effect"
that modifies HP or status. This system provides the single source of truth.
"""

from utils.dice_roller import roll_dice
from typing import Dict, List, Optional
import random

class EffectType:
    """Effect type constants"""
    DAMAGE = "damage"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"
    STATUS = "status"


class TargetType:
    """Valid target types"""
    PLAYER = "player"
    PARTY_MEMBER = "party_member"
    ENEMY = "enemy"
    ALL = "all"


class CombatEffectResolver:
    """
    Universal effect resolution system
    Processes all combat effects through unified pipeline
    
    Responsibilities:
    - Calculate effect magnitude (dice + modifiers)
    - Apply HP changes to correct game state location
    - Return standardized result data
    - Maintain single source of truth for HP modifications
    """
    
    def __init__(self, game_state, event_manager=None):
        """
        Initialize with game state reference
        
        Args:
            game_state: Main game state object
            event_manager: Optional event manager for notifications
        """
        self.game_state = game_state
        self.event_manager = event_manager
    
    # ==================== MAIN RESOLUTION PIPELINE ====================
    
    def resolve_effect(self, effect_definition: Dict, targets: List[Dict], 
                    source_data: Dict = None) -> List[Dict]:
        """
        Universal effect resolver - handles ANY combat effect
        
        Args:
            effect_definition: Effect parameters (dice, modifiers, type)
            targets: List of target dicts with 'type' and 'id'
            source_data: Source character data (for level/stat modifiers)
            
        Returns:
            List of result dicts with applied effects
        """
        print(f"🔍 FULL EFFECT DEFINITION: {effect_definition}")
        results = []
        
        # Calculate magnitude ONCE for all targets (AOE spells roll once!)
        magnitude = self._calculate_effect_magnitude(
            effect_definition, 
            source_data
        )

        effect_type = effect_definition.get('effect_type', EffectType.DAMAGE)
        damage_type = effect_definition.get('elemental_type', 'physical')
        print(f"\n🎯 EFFECT RESOLVER DEBUG:")
        print(f"   Effect Type: {effect_type}")
        print(f"   Damage Type: {damage_type}")
        print(f"   Base Magnitude: {magnitude}")
        
        # Apply same magnitude to all targets
        for target in targets:
            # Check if this is a buff effect
            if effect_type == 'buff':
                result = self._apply_buff_to_target(target, effect_definition)
                results.append(result)
                continue  # Skip damage/healing logic
            
            # Apply damage multiplier from saving throws FIRST
            working_magnitude = magnitude
            damage_multiplier = target.get('damage_multiplier', 1.0)
            if damage_multiplier != 1.0:
                working_magnitude = int(magnitude * damage_multiplier)
                print(f"⚖️ Save multiplier {damage_multiplier}: {magnitude} -> {working_magnitude}")
            
            # Apply resistances to magnitude
            final_magnitude = self._apply_resistances_to_magnitude(
                working_magnitude, target, effect_definition
            )

            if effect_type == 'damage':
                self._debug_resistance_check(target, damage_type, magnitude, final_magnitude)
    
            
            # Your existing _apply_to_target call (unchanged)
            result = self._apply_to_target(
                target,
                final_magnitude,  # Resistance-modified magnitude
                effect_definition.get('effect_type', EffectType.DAMAGE)
            )
            
            if result:
                # Add original damage for resistance logging
                if effect_type == 'damage':
                    result['original_damage'] = magnitude
                results.append(result)
        
        return results
    
    def _apply_buff_to_target(self, target: Dict, effect_def: Dict) -> Dict:
        """
        Apply buff effects to a target
        
        Args:
            target: Target dict with 'type', 'id', 'data', and optional other fields
            effect_def: Buff definition with 'buff_effects', 'duration', 'spell_name'
            
        Returns:
            Result dict with buff application info
        """
        target_type = target['type']
        target_id = target['id']
        
        # Get target character data DIRECTLY from target (it's already there!)
        char_data = target.get('data', {})
        
        if not char_data:
            return {
                'target_id': target_id,
                'target_name': target.get('name', 'Unknown'),
                'effect_type': 'buff',
                'success': False,
                'message': 'Target data not found',
                'magnitude': 0,
                'new_hp': target.get('current_hp', 0),
                'max_hp': char_data.get('hit_points', 0),
                'is_alive': True
            }
        
        # Buffs only apply to allies (player/party members)
        if target_type not in ['player', 'party_member']:
            return {
                'target_id': target_id,
                'target_name': target.get('name', 'Unknown'),
                'effect_type': 'buff',
                'success': False,
                'message': 'Cannot buff enemies',
                'magnitude': 0,
                'new_hp': target.get('current_hp', 0),
                'max_hp': char_data.get('hit_points', 0),
                'is_alive': True
            }
        
        # Initialize active_buffs if not exists
        if 'active_buffs' not in char_data:
            char_data['active_buffs'] = []
        
        # Create buff data
        buff_data = {
            'spell_name': effect_def.get('spell_name', 'Unknown Buff'),
            'duration': effect_def.get('duration', 'combat'),
            'effects': effect_def.get('buff_effects', {}),
            'applied_at': 'combat'  # Could track turn number
        }
        
        # Add to active buffs (avoid duplicates)
        spell_name = buff_data['spell_name']
        existing_buff = next(
            (b for b in char_data['active_buffs'] if b.get('spell_name') == spell_name),
            None
        )
        
        if existing_buff:
            # Refresh duration
            existing_buff['applied_at'] = 'combat'
            message = f"{spell_name} refreshed"
        else:
            char_data['active_buffs'].append(buff_data)
            message = f"{spell_name} applied"
        
        return {
            'target_id': target_id,
            'target_name': char_data.get('name', target.get('name', 'Unknown')),
            'effect_type': 'buff',
            'success': True,
            'buff_name': spell_name,
            'message': message,
            'magnitude': 0,  # Buffs don't have magnitude
            'new_hp': char_data.get('current_hp', target.get('current_hp', 0)),
            'max_hp': char_data.get('hit_points', 0),
            'is_alive': True,
            'target_type': target_type
        }

    # ==================== MAGNITUDE CALCULATION ====================

    def _apply_resistances_to_magnitude(self, base_magnitude: int, target: Dict, 
                                    effect_definition: Dict) -> int:
        """
        Apply damage resistances to magnitude before HP modification
        
        Args:
            base_magnitude: Original effect magnitude  
            target: Target data
            effect_definition: Effect parameters including damage_type
            
        Returns:
            Modified magnitude after resistance calculations
        """
        effect_type = effect_definition.get('effect_type', 'damage')
        
        # Only apply resistances to damage effects
        if effect_type != 'damage':
            return base_magnitude
        
        damage_type = effect_definition.get('elemental_type', 'physical')
        resistance_multiplier = self._get_resistance_multiplier(target, damage_type)
        
        final_magnitude = int(base_magnitude * resistance_multiplier)
        
        # Ensure minimum 1 damage unless completely immune
        if resistance_multiplier > 0 and final_magnitude < 1:
            final_magnitude = 1
        
        return final_magnitude

    def _calculate_effect_magnitude(self, effect_def: Dict, source_data: Dict = None) -> int:
        """
        Calculate effect magnitude from dice notation and modifiers
        
        Supports:
        - Simple dice: "2d4+2"
        - Level scaling: "1d8" with scales_with_level=True
        - Stat modifiers: add_stat_modifier="wisdom"
        
        Args:
            effect_def: Effect definition with dice and modifiers
            source_data: Source character data for modifiers
            
        Returns:
            Final magnitude (minimum 1)
        """
        dice_formula = effect_def.get('dice', '1d8')
        
        # Roll base amount
        total, rolls, modifier = roll_dice(dice_formula)
        # DEBUG: Show base roll
        print(f"🎲 Rolling {dice_formula}: {rolls} = {total}")
        
        # Apply level scaling
        if effect_def.get('scales_with_level') and source_data:
            level = source_data.get('level', 1)
            # Parse dice to get base count
            if 'd' in dice_formula:
                base_dice_str = dice_formula.split('d')[0]
                base_dice = int(base_dice_str)
                
                die_size_str = dice_formula.split('d')[1].split('+')[0].split('-')[0]
                die_size = int(die_size_str)
                
                # Add dice per level ABOVE 1 (level 1 = base, level 2 = base+1, level 3 = base+2)
                extra_dice = level - 1  # ← FIXED: Just add 1 die per level
                extra_roll = sum(random.randint(1, die_size) for _ in range(extra_dice))
                total += extra_roll
            
                if extra_dice > 0:
                    print(f"🎲 Level scaling (level {level}): +{extra_dice}d{die_size} = +{extra_roll} (total: {total})")
        
        # Apply stat modifier
        if effect_def.get('add_stat_modifier') and source_data:
            stat_name = effect_def['add_stat_modifier']
            stat_value = source_data.get('stats', {}).get(stat_name, 10)
            stat_mod = (stat_value - 10) // 2
            total += stat_mod
            print(f"🎲 {stat_name.upper()} modifier ({stat_value}): {stat_mod:+d} = {total}")
        
        # Apply add_level_bonus (for abilities like Second Wind)
        if effect_def.get('add_level_bonus') and source_data:
            level = source_data.get('level', 1)
            total += level
        print(f"🎲 Final magnitude: {total}")
        return max(1, total)  # Minimum 1
    
    # ==================== TARGET-SPECIFIC APPLICATION ====================
    
    def _apply_to_target(self, target: Dict, magnitude: int, 
                        effect_type: str) -> Optional[Dict]:
        """
        Apply effect to specific target based on type
        
        Args:
            target: Target dict with type and id
            magnitude: Effect magnitude to apply
            effect_type: 'damage', 'healing', etc.
            
        Returns:
            Result dict or None if target invalid
        """
        target_type = target.get('type')
        target_id = target.get('id')
        
        if target_type == TargetType.PLAYER:
            return self._modify_player_hp(magnitude, effect_type)
        
        elif target_type == TargetType.PARTY_MEMBER:
            return self._modify_party_member_hp(target_id, magnitude, effect_type)
        
        elif target_type == TargetType.ENEMY:
            enemy_data = target.get('data')
            return self._modify_enemy_hp(enemy_data, magnitude, effect_type)
        
        return None
    
    # ==================== HP MODIFICATION  ====================
    
    def _modify_player_hp(self, magnitude: int, effect_type: str) -> Dict:
        """
        Modify player HP - SINGLE SOURCE OF TRUTH for player HP changes
        
        Args:
            magnitude: Amount to change HP by
            effect_type: 'healing' or 'damage'
            
        Returns:
            Result dict with old/new HP and status
        """
        current_hp = self.game_state.character.get('current_hp', 10)
        max_hp = self.game_state.character.get('max_hp', 10)
        name = self.game_state.character.get('name', 'Player')
        
        if effect_type == EffectType.HEALING:
            new_hp = min(current_hp + magnitude, max_hp)
        else:  # DAMAGE
            new_hp = max(0, current_hp - magnitude)
        
        actual_change = abs(new_hp - current_hp)
        
        # Update game state - THE ONLY PLACE PLAYER HP IS MODIFIED
        self.game_state.character['current_hp'] = new_hp
        
        # Check for unconsciousness
        is_alive = new_hp > 0
        
        return {
            'target_id': 'player',
            'target_name': name,
            'target_type': 'player',
            'effect_type': effect_type,
            'magnitude': actual_change,
            'old_hp': current_hp,
            'new_hp': new_hp,
            'max_hp': max_hp,
            'is_alive': is_alive
        }
    
    def _modify_party_member_hp(self, char_id: str, magnitude: int, 
                                effect_type: str) -> Optional[Dict]:
        """
        Modify party member HP - SINGLE SOURCE OF TRUTH for party HP changes
        
        Args:
            char_id: Party member ID ('gareth', 'elara', etc.)
            magnitude: Amount to change HP by
            effect_type: 'healing' or 'damage'
            
        Returns:
            Result dict or None if member not found
        """
        # Find party member in game state
        target_member = None
        for member in self.game_state.party_member_data:
            if member.get('id') == char_id:
                target_member = member
                break
        
        if not target_member:
            return None
        
        current_hp = target_member.get('current_hp', 10)
        max_hp = target_member.get('max_hp', 10)
        name = target_member.get('name', char_id)
        
        if effect_type == EffectType.HEALING:
            new_hp = min(current_hp + magnitude, max_hp)
        else:  # DAMAGE
            new_hp = max(0, current_hp - magnitude)
        
        actual_change = abs(new_hp - current_hp)
        
        # Update game state - THE ONLY PLACE PARTY MEMBER HP IS MODIFIED
        target_member['current_hp'] = new_hp
        
        is_alive = new_hp > 0
        
        return {
            'target_id': char_id,
            'target_name': name,
            'target_type': 'party_member',
            'effect_type': effect_type,
            'magnitude': actual_change,
            'old_hp': current_hp,
            'new_hp': new_hp,
            'max_hp': max_hp,
            'is_alive': is_alive
        }
    
    def _modify_enemy_hp(self, enemy: Dict, magnitude: int, 
                        effect_type: str) -> Dict:
        """
        Modify enemy HP - SINGLE SOURCE OF TRUTH for enemy HP changes
        
        Args:
            enemy: Enemy instance dict from combat_data
            magnitude: Amount to change HP by
            effect_type: 'healing' or 'damage'
            
        Returns:
            Result dict with old/new HP and status
        """
        current_hp = enemy.get('current_hp', 0)
        max_hp = enemy.get('max_hp')
        if max_hp is None:
            max_hp = enemy.get('stats', {}).get('max_hp', 10)

        name = enemy.get('name', 'Enemy')
        instance_id = enemy.get('instance_id', 'enemy')
        
        if effect_type == EffectType.HEALING:
            new_hp = min(current_hp + magnitude, max_hp)
        else:  # DAMAGE
            new_hp = max(0, current_hp - magnitude)
        
        actual_change = abs(new_hp - current_hp)
        
        # Update enemy data - THE ONLY PLACE ENEMY HP IS MODIFIED
        enemy['current_hp'] = new_hp
        
        is_alive = new_hp > 0
        
        return {
            'target_id': instance_id,
            'target_name': name,
            'target_type': 'enemy',
            'effect_type': effect_type,
            'magnitude': magnitude,
            'old_hp': current_hp,
            'new_hp': new_hp,
            'max_hp': max_hp,
            'is_alive': is_alive
        }

    # ==================== Modifications  ====================
    def _get_resistance_multiplier(self, target: Dict, damage_type: str) -> float:
        """
        Get damage resistance multiplier for target
        
        Returns: 0.0=immune, 0.5=resistant, 1.0=normal, 2.0=vulnerable
        """
        target_data = target.get('data', target)
        
        # Check immunities first
        immunities = target_data.get('immunities', [])
        if damage_type in immunities:
            return 0.0
        
        # Check resistances
        resistances = target_data.get('resistances', {})
        if damage_type in resistances:
            return resistances[damage_type]
        
        # Check vulnerabilities  
        vulnerabilities = target_data.get('vulnerabilities', {})
        if damage_type in vulnerabilities:
            return vulnerabilities[damage_type]
        
        # Normal damage
        return 1.0

    def _debug_resistance_check(self, target: Dict, damage_type: str, base_magnitude: int, final_magnitude: int):
        """Debug resistance calculations"""
        target_data = target.get('data', target)
        target_name = target_data.get('name', 'Unknown')
        
        print(f"\n🛡️ RESISTANCE DEBUG:")
        print(f"   Target: {target_name}")
        print(f"   Damage Type: {damage_type}")
        print(f"   Base Damage: {base_magnitude}")
        print(f"   Final Damage: {final_magnitude}")
        print(f"   Resistances: {target_data.get('resistances', 'None')}")
        print(f"   Immunities: {target_data.get('immunities', 'None')}")
        print(f"   Vulnerabilities: {target_data.get('vulnerabilities', 'None')}")

# ==================== GLOBAL SINGLETON ====================

_effect_resolver = None

def get_effect_resolver(game_state, event_manager=None):
    """
    Get or create the global effect resolver singleton
    
    Args:
        game_state: Main game state object
        event_manager: Optional event manager
        
    Returns:
        CombatEffectResolver instance
    """
    global _effect_resolver
    if _effect_resolver is None:
        _effect_resolver = CombatEffectResolver(game_state, event_manager)
    return _effect_resolver