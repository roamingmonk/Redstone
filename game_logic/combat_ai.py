# game_logic/combat_ai.py
"""
Combat AI Manager - Enemy decision-making and behavior system
Follows existing game_logic pattern for core game systems

Responsibilities:
- Analyze combat state and enemy capabilities
- Decide enemy actions based on behavior JSON data
- Select movement destinations and attack targets
- Handle retreat decisions based on HP thresholds
"""

from typing import Dict, List, Optional, Tuple

class CombatAI:
    """
    AI behavior manager for tactical combat
    
    Separation of concerns:
    - CombatAI DECIDES what enemies should do
    - CombatEngine EXECUTES those decisions
    """
    
    def __init__(self):
        """Initialize AI manager"""
        print("🤖 CombatAI initialized")
    
    def calculate_enemy_turn(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        Main AI decision point - determines what action enemy should take
        
        Args:
            enemy_data: Complete enemy instance data including stats, position, behavior
            combat_state: Current battlefield state (characters, enemies, battlefield layout)
            
        Returns:
            Action dict with structure:
            {
                'action_type': 'move' | 'attack' | 'retreat' | 'wait',
                'target_position': [x, y] if moving,
                'target_id': character_id if attacking,
                'reason': 'debug string explaining decision'
            }
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        enemy_name = enemy_data.get("name", "Enemy")
        behavior = enemy_data.get("behavior", {})
        # DEBUG: Show enemy info
        print(f"\n🤖 AI PLANNING: {enemy_name}")
        print(f"   Position: {enemy_pos}")
        print(f"   HP: {enemy_data.get('current_hp')}/{enemy_data.get('stats', {}).get('max_hp')}")
    
        # Check for retreat first (applies to all behaviors)
        if self._should_retreat(enemy_data, behavior):
            print(f"   ⚠️ LOW HP - Retreating!")
            enemy_pos = enemy_data.get("position", [0, 0])
            movement_range = enemy_data.get("movement", {}).get("speed", 3)
            
            # Find closest player to flee from
            closest_player = self._find_closest_player(enemy_pos, combat_state)
            if not closest_player:
                return {'move': None, 'attack': None, 'reason': 'no players to flee from'}
            
            retreat_pos = self._find_best_retreat_position(
                enemy_pos,
                closest_player['position'],
                movement_range,
                combat_state
            )
            
            # RETURN THE RETREAT ACTION!
            return {
                'move': retreat_pos,
                'attack': None,
                'reason': 'retreating (low HP)'
            }
        
        # Get behavior tactics - ENCOUNTER OVERRIDES ENEMY DEFINITION
        # Priority: encounter spawn > enemy default > fallback
        tactics = (
            enemy_data.get("encounter_behavior") or  # Set during combat setup
            behavior.get("tactics") or               # Enemy definition default
            "rush_player"                             # Fallback
        )
        print(f"   🧠 AI Behavior: {tactics}")
        # Route to appropriate behavior handler
        try:
            if tactics == "rush_player":
                result = self._calculate_rush_action(enemy_data, combat_state)
            elif tactics == "ranged_preference":
                result = self._calculate_ranged_preference_action(enemy_data, combat_state)
            elif tactics == "hit_and_run":
                result = self._calculate_hit_and_run_action(enemy_data, combat_state)
            elif tactics == "spell_preference":
                result = self._calculate_spell_preference_action(enemy_data, combat_state)
            elif tactics == "stalker":
                result = self._calculate_stalker_action(enemy_data, combat_state)
            elif tactics == "aggressive_rush":
                result = self._calculate_aggressive_rush_action(enemy_data, combat_state)
            elif tactics == "mindless_advance":
                result = self._calculate_mindless_advance_action(enemy_data, combat_state)
            elif tactics == "flanking":
                result = self._calculate_flanking_action(enemy_data, combat_state)
            else:
                # Fallback to basic rush
                print(f"⚠️ Unknown tactics '{tactics}' for {enemy_name}, using rush_player")
                result = self._calculate_rush_action(enemy_data, combat_state)
        except Exception as e:
            print(f"   ❌ ERROR in AI calculation: {e}")
            import traceback
            traceback.print_exc()
            result = {'move': None, 'attack': None, 'reason': f'AI error: {e}'}

        # DEBUG: Show the complete plan (NOW THIS EXECUTES!)
        print(f"   📋 PLAN:")
        if result.get('move'):
            print(f"      • Move: {enemy_pos} → {result['move']}")
        else:
            print(f"      • Move: None (staying at {enemy_pos})")

        if result.get('attack'):
            attack_data = result['attack']
            attacks = enemy_data.get("attacks", [])
            weapon_name = "unknown"
            if attack_data.get('attack_index', 0) < len(attacks):
                weapon_name = attacks[attack_data['attack_index']].get('name', 'unknown')
            print(f"      • Attack: {weapon_name} at {attack_data['target_id']}")
        else:
            print(f"      • Attack: None")

        print(f"   💭 Reason: {result.get('reason', 'no reason given')}")

        return result  # <- Return at the END
    # ========================================
    # RETREAT LOGIC
    # ========================================

    def _should_retreat(self, enemy_data: Dict, behavior: Dict) -> bool:
        """Check if enemy should retreat based on HP threshold"""
        retreat_threshold = behavior.get("retreat_threshold", 0)
        
        # Negative or zero threshold means never retreat
        if retreat_threshold <= 0:
            return False
        
        current_hp = enemy_data.get("current_hp", 0)
        return current_hp <= retreat_threshold
    
    def _calculate_retreat_action(self, enemy_data: Dict, combat_state: Dict) -> Optional[Dict]:
        """Calculate retreat movement away from players"""
        enemy_pos = enemy_data.get("position", [0, 0])
        
        # Find closest player to flee from
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        if not closest_player:
            return None
        
        player_pos = closest_player['position']
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        
        # Find position that maximizes distance from player
        best_retreat_pos = self._find_best_retreat_position(
            enemy_pos, 
            player_pos, 
            movement_range,
            combat_state
        )
        
        if best_retreat_pos and best_retreat_pos != enemy_pos:
            return {
                'action_type': 'move',
                'target_position': best_retreat_pos,
                'reason': 'retreating from player (low HP)'
            }
        
        return None
    
    # ========================================
    # BEHAVIOR TACTICS
    # ========================================
    
    def _calculate_rush_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        RUSH_PLAYER: Plan turn for aggressive melee behavior
        Returns: {'move': pos or None, 'attack': data or None}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        if not closest_player:
            return {'move': None, 'attack': None, 'reason': 'no players found'}
        
        distance = closest_player['distance']
        
        # Already adjacent - just attack (no move needed)
        if distance == 1:
            return {
                'move': None,
                'attack': {
                    'target_id': closest_player['id'],
                    'attack_index': 0
                },
                'reason': 'already adjacent - attacking'
            }
        
        # Not adjacent - plan move toward player
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        new_pos = self._find_best_move_toward_target(
            enemy_pos,
            closest_player['position'],
            movement_range,
            combat_state
        )
        
        # Check if move gets us into attack range
        if new_pos != enemy_pos:
            new_distance = self._manhattan_distance(new_pos, closest_player['position'])
            
            if new_distance == 1:
                # Perfect! Move will put us adjacent - attack after move
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': 0
                    },
                    'reason': 'moving into melee then attacking'
                }
            else:
                # Move but can't reach yet
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'moving closer ({distance} -> {new_distance})'
                }
        
        # Can't move closer
        return {'move': None, 'attack': None, 'reason': 'cannot move closer'}
    
    def _calculate_ranged_preference_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        RANGED_PREFERENCE: Plan turn for skirmisher behavior
        Strategy: Stay at range 2-5, shoot, retreat if too close
        Requires line of sight for ranged attacks
        Returns: {'move': pos or None, 'attack': data or None}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        # Find closest player WITH line of sight (ranged attacks require LOS)
        closest_player = self._find_closest_player_with_los(enemy_pos, combat_state)
        if not closest_player:
            # No LOS to any target - try to reposition
            return self._handle_no_los_fallback(enemy_data, combat_state, "ranged_preference")
        
        distance = closest_player['distance']
        
        # Find ranged and melee attacks
        attacks = enemy_data.get("attacks", [])
        ranged_attack = None
        melee_attack = None
        
        for i, attack in enumerate(attacks):
            if attack.get("attack_type") == "ranged":
                ranged_attack = {'index': i, 'data': attack}
            elif attack.get("attack_type") == "melee":
                melee_attack = {'index': i, 'data': attack}
        
        if not ranged_attack:
            # No ranged weapon - fall back to rush
            return self._calculate_rush_action(enemy_data, combat_state)
        
        max_range = ranged_attack['data'].get("range", 5)
        
        # CASE 1: At ideal range (2-5) - shoot without moving
        if 2 <= distance <= max_range:
            return {
                'move': None,
                'attack': {
                    'target_id': closest_player['id'],
                    'attack_index': ranged_attack['index']
                },
                'reason': f'at ideal range ({distance}) - shooting'
            }
        
        # CASE 2: Too close (adjacent) - back away then shoot if possible
        if distance == 1:
            movement_range = enemy_data.get("movement", {}).get("speed", 3)
            retreat_pos = self._find_retreat_position_from_player(
                enemy_pos,
                closest_player['position'],
                combat_state,
                min_distance=2
            )
            
            if retreat_pos and retreat_pos != enemy_pos:
                new_distance = self._manhattan_distance(retreat_pos, closest_player['position'])
                
                # Can we shoot after backing away?
                if 2 <= new_distance <= max_range:
                    return {
                        'move': retreat_pos,
                        'attack': {
                            'target_id': closest_player['id'],
                            'attack_index': ranged_attack['index']
                        },
                        'reason': f'backing to range {new_distance} then shooting'
                    }
                else:
                    return {
                        'move': retreat_pos,
                        'attack': None,
                        'reason': 'backing away from melee'
                    }
            
            # Can't retreat - cornered! Melee as last resort
            if melee_attack:
                return {
                    'move': None,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': melee_attack['index']
                    },
                    'reason': 'cornered - desperate melee'
                }
        
        # CASE 3: Too far - move to ideal range then shoot
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        new_pos = self._find_move_to_range(
            enemy_pos,
            closest_player['position'],
            target_range=3,  # Ideal shooting distance
            movement_range=movement_range,
            combat_state=combat_state
        )
        
        if new_pos and new_pos != enemy_pos:
            new_distance = self._manhattan_distance(new_pos, closest_player['position'])
            
            # Can we shoot after moving?
            if 2 <= new_distance <= max_range:
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': ranged_attack['index']
                    },
                    'reason': f'moving to range {new_distance} then shooting'
                }
            else:
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'moving closer ({distance} -> {new_distance})'
                }
        
        # Fallback
        return {'move': None, 'attack': None, 'reason': 'no valid action'}
    
    def _calculate_spell_preference_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        SPELL_PREFERENCE: Intelligent caster AI
        Strategy: Maintain 4-7 tile casting range, prefer spells, consider friendly fire
        Returns: {'move': pos or None, 'attack': data or None, 'reason': str}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        if not closest_player:
            return {'move': None, 'attack': None, 'reason': 'no players found'}
        
        distance = closest_player['distance']
        behavior = enemy_data.get("behavior", {})
        acceptable_ff = behavior.get("acceptable_friendly_fire", 3)
        
        # Get attacks using our new helper (spell_focused preference)
        attacks = enemy_data.get("attacks", [])
        
        # CASE 1: At ideal casting range (4-7) - evaluate spell opportunities
        if 4 <= distance <= 7:
            attack_idx = self._select_best_attack(
                enemy_data,
                enemy_pos,
                closest_player['position'],
                behavior_type='spell_focused',
                combat_state=combat_state
            )
            
            if attack_idx is not None:
                # Check friendly fire for AOE spells
                selected_attack = attacks[attack_idx]
                
                # For now, simple friendly fire check
                # TODO: In future, calculate actual AOE and count allies
                # For single-target or non-AOE, just use it
                
                return {
                    'move': None,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': attack_idx
                    },
                    'reason': f'at casting range ({distance}) - using {selected_attack.get("name", "spell")}'
                }
        
        # CASE 2: Too close (<4) - back away to ideal range then cast
        if distance < 4:
            movement_range = enemy_data.get("movement", {}).get("speed", 3)
            retreat_pos = self._find_retreat_position_from_player(
                enemy_pos,
                closest_player['position'],
                combat_state,
                min_distance=4
            )
            
            if retreat_pos:
                new_distance = self._manhattan_distance(retreat_pos, closest_player['position'])
                
                # Can we cast after backing away?
                attack_idx = self._select_best_attack(
                    enemy_data,
                    retreat_pos,  # Check from NEW position
                    closest_player['position'],
                    behavior_type='spell_focused',
                    combat_state=combat_state
                )
                
                if attack_idx is not None:
                    return {
                        'move': retreat_pos,
                        'attack': {
                            'target_id': closest_player['id'],
                            'attack_index': attack_idx
                        },
                        'reason': f'backing to range {new_distance} then casting'
                    }
                else:
                    return {
                        'move': retreat_pos,
                        'attack': None,
                        'reason': 'retreating from melee'
                    }
            
            # Can't retreat - cornered! Use whatever attack is available
            attack_idx = self._select_best_attack(
                enemy_data,
                enemy_pos,
                closest_player['position'],
                behavior_type='opportunistic',  # Take anything!
                combat_state=combat_state
            )
            
            if attack_idx is not None:
                return {
                    'move': None,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': attack_idx
                    },
                    'reason': 'cornered - desperate attack'
                }
        
        # CASE 3: Too far (8+) - move to ideal casting range
        if distance > 7:
            movement_range = enemy_data.get("movement", {}).get("speed", 3)
            new_pos = self._find_move_to_range(
                enemy_pos,
                closest_player['position'],
                target_range=5,  # Aim for middle of ideal range
                movement_range=movement_range,
                combat_state=combat_state
            )
            
            new_distance = self._manhattan_distance(new_pos, closest_player['position'])
            
            # Can we cast after moving closer?
            attack_idx = self._select_best_attack(
                enemy_data,
                new_pos,
                closest_player['position'],
                behavior_type='spell_focused',
                combat_state=combat_state
            )
            
            if attack_idx is not None:
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': attack_idx
                    },
                    'reason': f'moving to range {new_distance} then casting'
                }
            else:
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'moving closer ({distance} -> {new_distance})'
                }
        
        # Fallback - no valid action
        return {'move': None, 'attack': None, 'reason': 'no valid spell actions'}

    def _calculate_hit_and_run_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        HIT_AND_RUN: Goblin-style skirmisher
        Strategy: Attack FIRST (bow or scimitar), then retreat to maintain distance
        Uses "Nimble Escape" - can move after attacking
        Requires line of sight for ranged attacks
        Returns: {'move': pos or None, 'attack': data or None}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        # Find closest player WITH line of sight (for ranged attacks)
        closest_player = self._find_closest_player_with_los(enemy_pos, combat_state)
        if not closest_player:
            # No LOS for ranged - try melee or reposition
            # Check if any player is adjacent for melee fallback
            adjacent_players = self._find_adjacent_players(enemy_pos, combat_state)
            if adjacent_players:
                # Can do melee attack instead
                closest_player = adjacent_players[0]
                # Continue with the rest of the method using melee
            else:
                # No melee option either - reposition
                return self._handle_no_los_fallback(enemy_data, combat_state, "hit_and_run")
        
        distance = closest_player['distance']
        player_pos = closest_player['position']
        
        # Find ranged and melee attacks
        attacks = enemy_data.get("attacks", [])
        ranged_attack = None
        melee_attack = None
        
        for i, attack in enumerate(attacks):
            if attack.get("attack_type") == "ranged":
                ranged_attack = {'index': i, 'data': attack}
            elif attack.get("attack_type") == "melee":
                melee_attack = {'index': i, 'data': attack}
        
        movement_range = enemy_data.get("movement", {}).get("speed", 4)
        
        # CASE 1: Player at ranged attack distance (2-6 tiles)
        if ranged_attack and 2 <= distance <= ranged_attack['data'].get("range", 6):
            # Shoot, then consider retreating if too close
            retreat_pos = None
            
            # If player is getting close (2-3 tiles), back away after shooting
            if distance <= 3:
                retreat_pos = self._find_retreat_position_from_player(
                    enemy_pos,
                    player_pos,
                    combat_state,
                    min_distance=4  # Try to get to 4+ tiles away
                )
            
            if retreat_pos and retreat_pos != enemy_pos:
                new_distance = self._manhattan_distance(retreat_pos, player_pos)
                return {
                    'move': retreat_pos,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': ranged_attack['index']
                    },
                    'reason': f'shooting then retreating (range {distance} -> {new_distance})'
                }
            else:
                # Good position, shoot and stay
                return {
                    'move': None,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': ranged_attack['index']
                    },
                    'reason': f'shooting from safe distance ({distance})'
                }
        
        # CASE 2: Player adjacent (melee range)
        if distance == 1:
            if melee_attack:
                # Attack with scimitar, then retreat
                retreat_pos = self._find_retreat_position_from_player(
                    enemy_pos,
                    player_pos,
                    combat_state,
                    min_distance=3  # Get away to ranged distance
                )
                
                if retreat_pos and retreat_pos != enemy_pos:
                    new_distance = self._manhattan_distance(retreat_pos, player_pos)
                    return {
                        'move': retreat_pos,
                        'attack': {
                            'target_id': closest_player['id'],
                            'attack_index': melee_attack['index']
                        },
                        'reason': f'melee strike then retreating (range 1 -> {new_distance})'
                    }
                else:
                    # Can't retreat, just attack
                    return {
                        'move': None,
                        'attack': {
                            'target_id': closest_player['id'],
                            'attack_index': melee_attack['index']
                        },
                        'reason': 'cornered - melee attack only'
                    }
        
        # CASE 3: Player too far (7+ tiles) or too close (range 1 with no melee)
        if ranged_attack:
            # Move to optimal shooting range (3-4 tiles)
            new_pos = self._find_move_to_range(
                enemy_pos,
                player_pos,
                target_range=4,  # Ideal hit-and-run distance
                movement_range=movement_range,
                combat_state=combat_state
            )
            
            if new_pos and new_pos != enemy_pos:
                new_distance = self._manhattan_distance(new_pos, player_pos)
                
                # Can we shoot after moving?
                if 2 <= new_distance <= ranged_attack['data'].get("range", 6):
                    return {
                        'move': new_pos,
                        'attack': {
                            'target_id': closest_player['id'],
                            'attack_index': ranged_attack['index']
                        },
                        'reason': f'repositioning to range {new_distance} then shooting'
                    }
                else:
                    # Just reposition, can't shoot yet
                    return {
                        'move': new_pos,
                        'attack': None,
                        'reason': f'repositioning ({distance} -> {new_distance})'
                    }
        
        # FALLBACK: Cornered goblin - desperate melee attack
        # If we get here, we couldn't retreat or shoot, so try melee as last resort
        if melee_attack and distance <= 1:
            return {
                'move': None,
                'attack': {
                    'target_id': closest_player['id'],
                    'attack_index': melee_attack['index']
                },
                'reason': 'cornered - desperate melee strike!'
            }
        
        # Truly stuck - can't move, can't attack
        return {'move': None, 'attack': None, 'reason': 'cornered and no valid targets'}
    
    def _calculate_stalker_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        STALKER: Relentless single-target pursuit (ghosts/obsessed hunters)
        Strategy:
        - Locks onto ONE target and pursues relentlessly
        - Never switches targets unless current target dies
        - Can move through obstacles if incorporeal (checks movement_type)
        - Ignores tactical considerations - pure obsession
        - Creates horror movie "it's following you" feeling
        Returns: {'move': pos or None, 'attack': data or None}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        enemy_instance_id = enemy_data.get("instance_id", "unknown")
        
        # Check if we have a locked target (stored in enemy data)
        locked_target_id = enemy_data.get("stalker_target")
        character_states = combat_state.get('character_states', {})
        
        # Validate locked target is still alive
        if locked_target_id and locked_target_id in character_states:
            target_state = character_states[locked_target_id]
            if not target_state.get('is_alive', True):
                # Target died - clear lock
                locked_target_id = None
                enemy_data["stalker_target"] = None
        
        # If no locked target, pick the closest player and LOCK ON
        if not locked_target_id:
            closest = self._find_closest_player(enemy_pos, combat_state)
            if not closest:
                return {'move': None, 'attack': None, 'reason': 'no prey detected'}
            
            locked_target_id = closest['id']
            enemy_data["stalker_target"] = locked_target_id
            print(f"   🎯 LOCKED TARGET: {closest['name']}")
        
        # Get locked target info
        target_state = character_states.get(locked_target_id)
        if not target_state:
            return {'move': None, 'attack': None, 'reason': 'target lost'}
        
        target_name = target_state.get('name', 'Target')
        target_pos = target_state.get('position', [0, 0])
        distance = self._manhattan_distance(enemy_pos, target_pos)
        
        # Already adjacent to locked target - ATTACK
        if distance == 1:
            return {
                'move': None,
                'attack': {
                    'target_id': locked_target_id,
                    'attack_index': 0
                },
                'reason': f'relentlessly attacking {target_name}'
            }
        
        # Move toward locked target
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        movement_type = enemy_data.get("movement", {}).get("movement_type", "walking")
        
        # Check if incorporeal (can pass through obstacles)
        can_phase = movement_type in ["flying", "incorporeal", "teleport"]
        
        if can_phase:
            # Incorporeal - move directly toward target, ignoring obstacles
            new_pos = self._find_direct_path_to_target(
                enemy_pos,
                target_pos,
                movement_range,
                combat_state
            )
        else:
            # Corporeal - use normal pathfinding
            new_pos = self._find_best_move_toward_target(
                enemy_pos,
                target_pos,
                movement_range,
                combat_state
            )
        
        if new_pos != enemy_pos:
            new_distance = self._manhattan_distance(new_pos, target_pos)
            
            # Moved into attack range
            if new_distance == 1:
                phase_msg = "(phasing through obstacles)" if can_phase else ""
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': locked_target_id,
                        'attack_index': 0
                    },
                    'reason': f'stalking {target_name} into melee {phase_msg}'
                }
            else:
                phase_msg = "(phasing)" if can_phase else ""
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'relentlessly stalking {target_name} {phase_msg} (distance {distance} → {new_distance})'
                }
        
        # Blocked (shouldn't happen for incorporeal)
        return {'move': None, 'attack': None, 'reason': f'stalking {target_name} blocked'}
    
    def _calculate_aggressive_rush_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        AGGRESSIVE_RUSH: Smart hunter targeting weakest prey
        Strategy: 
        - Identify party member with lowest HP percentage
        - Move aggressively toward that target
        - Attack if adjacent, prioritizing the weakest target
        - Ignores high-HP tanks, focuses on wounded/fragile targets
        Returns: {'move': pos or None, 'attack': data or None}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        # Find the weakest party member (lowest current HP)
        weakest_target = self._find_weakest_player(enemy_pos, combat_state)
        if not weakest_target:
            return {'move': None, 'attack': None, 'reason': 'no valid targets found'}
        
        distance = weakest_target['distance']
        target_name = weakest_target['name']
        target_hp = weakest_target['current_hp']
        target_max_hp = weakest_target['max_hp']
        
        # Already adjacent to weakest target - ATTACK!
        if distance == 1:
            return {
                'move': None,
                'attack': {
                    'target_id': weakest_target['id'],
                    'attack_index': 0
                },
                'reason': f'attacking weakest target: {target_name} ({target_hp}/{target_max_hp} HP)'
            }
        
        # Check if we're adjacent to ANY player (might not be weakest)
        adjacent_players = self._find_adjacent_players(enemy_pos, combat_state)
        if adjacent_players:
            # We're next to someone - find the weakest one
            # Need to look up HP data from character_states
            character_states = combat_state.get('character_states', {})
            
            weakest_adjacent = None
            lowest_adjacent_hp = float('inf')
            
            for adj_player in adjacent_players:
                char_id = adj_player['id']
                char_state = character_states.get(char_id)
                if not char_state:
                    continue
                
                char_data = char_state.get('character_data', {})
                
                # Get current HP
                if char_id == 'player':
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('hit_points', char_data.get('max_hp', 10))
                else:
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('max_hp', char_data.get('hit_points', 10))
                
                # Track weakest adjacent
                if current_hp < lowest_adjacent_hp:
                    lowest_adjacent_hp = current_hp
                    weakest_adjacent = {
                        'id': char_id,
                        'name': char_state.get('name', 'Character'),
                        'current_hp': current_hp,
                        'max_hp': max_hp
                    }
            
            if weakest_adjacent:
                return {
                    'move': None,
                    'attack': {
                        'target_id': weakest_adjacent['id'],
                        'attack_index': 0
                    },
                    'reason': f'attacking nearby: {weakest_adjacent["name"]} ({weakest_adjacent["current_hp"]}/{weakest_adjacent["max_hp"]} HP)'
                }
        
        # Not adjacent - move toward weakest target
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        new_pos = self._find_best_move_toward_target(
            enemy_pos,
            weakest_target['position'],
            movement_range,
            combat_state
        )
        
        if new_pos != enemy_pos:
            new_distance = self._manhattan_distance(new_pos, weakest_target['position'])
            
            # Check if move gets us into attack range
            if new_distance == 1:
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': weakest_target['id'],
                        'attack_index': 0
                    },
                    'reason': f'moving to attack weakest: {target_name} ({target_hp}/{target_max_hp} HP)'
                }
            else:
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'hunting weakest prey: {target_name} ({target_hp}/{target_max_hp} HP) - distance {distance} → {new_distance}'
                }
        
        # Can't move closer
        return {'move': None, 'attack': None, 'reason': f'cannot reach weakest target: {target_name}'}
    
    def _calculate_mindless_advance_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        MINDLESS_ADVANCE: Relentless shambling (zombies/skeletons/constructs)
        Strategy:
        - Move toward nearest player (closest, not smartest)
        - Attack if adjacent
        - NEVER retreats (even at 1 HP - they're mindless!)
        - Ignores all tactical considerations
        - Simple, predictable, terrifying in numbers
        Returns: {'move': pos or None, 'attack': data or None}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        # Find closest player (shortest distance, ignore HP/tactics)
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        if not closest_player:
            return {'move': None, 'attack': None, 'reason': 'no targets detected'}
        
        distance = closest_player['distance']
        target_name = closest_player['name']
        
        # Already adjacent - ATTACK with mindless hunger
        if distance == 1:
            return {
                'move': None,
                'attack': {
                    'target_id': closest_player['id'],
                    'attack_index': 0
                },
                'reason': f'mindless attack on {target_name}'
            }
        
        # Not adjacent - shamble closer
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        new_pos = self._find_best_move_toward_target(
            enemy_pos,
            closest_player['position'],
            movement_range,
            combat_state
        )
        
        if new_pos != enemy_pos:
            new_distance = self._manhattan_distance(new_pos, closest_player['position'])
            
            # Moved into attack range - strike immediately
            if new_distance == 1:
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': 0
                    },
                    'reason': f'shambling into melee with {target_name}'
                }
            else:
                # Still approaching
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'shambling toward {target_name} (distance {distance} → {new_distance})'
                }
        
        # Blocked or trapped
        return {'move': None, 'attack': None, 'reason': 'shambling blocked'}
    
    def _calculate_flanking_action(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        FLANKING: Tactical positioning for coordinated attacks (rogues/thieves)
        Strategy:
        - Prioritize attacking targets already engaged by other enemies
        - Move to gang up on isolated targets
        - Coordinate strikes rather than spreading out
        - Creates dangerous pack hunting behavior
        Returns: {'move': pos or None, 'attack': data or None}
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        enemy_instances = combat_state.get('enemy_instances', [])
        
        # Find all living players
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        if not closest_player:
            return {'move': None, 'attack': None, 'reason': 'no targets found'}
        
        # Check if we're already adjacent to any player
        adjacent_players = self._find_adjacent_players(enemy_pos, combat_state)
        
        if adjacent_players:
            # We're adjacent to someone - find the best target to flank
            best_flank_target = None
            max_flankers = 0
            
            for adj_player in adjacent_players:
                player_pos = adj_player['position']
                
                # Count how many OTHER enemies are adjacent to this player
                flanker_count = 0
                for other_enemy in enemy_instances:
                    if other_enemy.get("current_hp", 0) <= 0:
                        continue  # Skip dead enemies
                    if other_enemy.get("instance_id") == enemy_data.get("instance_id"):
                        continue  # Skip self
                    
                    other_pos = other_enemy.get("position", [0, 0])
                    other_distance = self._manhattan_distance(other_pos, player_pos)
                    
                    if other_distance == 1:
                        flanker_count += 1
                
                # Prefer targets already being flanked
                if flanker_count > max_flankers or best_flank_target is None:
                    max_flankers = flanker_count
                    best_flank_target = adj_player
            
            if best_flank_target:
                flank_status = "flanking with allies" if max_flankers > 0 else "solo attack"
                return {
                    'move': None,
                    'attack': {
                        'target_id': best_flank_target['id'],
                        'attack_index': 0
                    },
                    'reason': f'{flank_status} on {best_flank_target["name"]} ({max_flankers} allies adjacent)'
                }
        
        # Not adjacent - find the best target to flank
        # Prioritize players already being attacked by allies
        character_states = combat_state.get('character_states', {})
        best_target = None
        best_flanker_count = -1
        best_distance = float('inf')
        
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            char_pos = char_state.get('position', [0, 0])
            distance = self._manhattan_distance(enemy_pos, char_pos)
            
            # Count enemies adjacent to this player
            flanker_count = 0
            for other_enemy in enemy_instances:
                if other_enemy.get("current_hp", 0) <= 0:
                    continue
                if other_enemy.get("instance_id") == enemy_data.get("instance_id"):
                    continue
                
                other_pos = other_enemy.get("position", [0, 0])
                other_distance = self._manhattan_distance(other_pos, char_pos)
                
                if other_distance == 1:
                    flanker_count += 1
            
            # Prefer targets being flanked, then closer targets
            if flanker_count > best_flanker_count or (flanker_count == best_flanker_count and distance < best_distance):
                best_flanker_count = flanker_count
                best_distance = distance
                best_target = {
                    'id': char_id,
                    'name': char_state.get('name', 'Character'),
                    'position': char_pos
                }
        
        if not best_target:
            # Fallback to closest
            best_target = {
                'id': closest_player['id'],
                'name': closest_player['name'],
                'position': closest_player['position']
            }
            best_flanker_count = 0
        
        # Move toward best flank target
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        new_pos = self._find_best_move_toward_target(
            enemy_pos,
            best_target['position'],
            movement_range,
            combat_state
        )
        
        if new_pos != enemy_pos:
            new_distance = self._manhattan_distance(new_pos, best_target['position'])
            
            # Moved into attack range - strike!
            if new_distance == 1:
                flank_msg = "joining flank" if best_flanker_count > 0 else "flanking position"
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': best_target['id'],
                        'attack_index': 0
                    },
                    'reason': f'{flank_msg} on {best_target["name"]} ({best_flanker_count} allies nearby)'
                }
            else:
                flank_msg = "coordinating with allies" if best_flanker_count > 0 else "seeking flank position"
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'{flank_msg} on {best_target["name"]} (distance {best_distance} → {new_distance})'
                }
        
        # Can't move closer
        return {'move': None, 'attack': None, 'reason': 'cannot reach flank position'}
    
    # ========================================
    # HELPER METHODS - TACTICAL ANALYSIS
    # ========================================
    
    def _find_closest_player(self, enemy_pos: List[int], combat_state: Dict) -> Optional[Dict]:
        """Find closest living player character"""
        character_states = combat_state.get("character_states", {})
        
        closest = None
        closest_distance = float('inf')
        
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            char_pos = char_state.get('position', [0, 0])
            distance = self._manhattan_distance(enemy_pos, char_pos)
            
            if distance < closest_distance:
                closest_distance = distance
                closest = {
                    'id': char_id,
                    'name': char_state.get('name', 'Player'),
                    'position': char_pos,
                    'distance': distance
                }
        
        return closest

    def _handle_no_los_fallback(self, enemy_data: Dict, combat_state: Dict, behavior_type: str) -> Dict:
        """
        Fallback behavior when ranged enemy has no line of sight to any target
        
        Args:
            enemy_data: Enemy instance
            combat_state: Current combat state
            behavior_type: AI behavior type (for context)
        
        Returns:
            Action dict
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        enemy_name = enemy_data.get("name", "Enemy")
        
        # Strategy: Try to reposition to get LOS
        # Find closest player (ignoring LOS) and try to move toward them
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        
        if not closest_player:
            return {'move': None, 'attack': None, 'reason': 'no targets available'}
        
        # Try to move closer to get LOS
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        new_pos = self._find_best_move_toward_target(
            enemy_pos,
            closest_player['position'],
            movement_range,
            combat_state
        )
        
        if new_pos != enemy_pos:
            return {
                'move': new_pos,
                'attack': None,
                'reason': f'repositioning for LOS on {closest_player["name"]}'
            }
        
        # Can't move - hold position
        return {'move': None, 'attack': None, 'reason': 'no LOS and cannot reposition'}

    def _find_closest_player_with_los(self, enemy_pos: List[int], combat_state: Dict) -> Optional[Dict]:
        """
        Find closest player that has line of sight
        Returns: {'id': str, 'name': str, 'position': [x,y], 'distance': int} or None
        """
        character_states = combat_state.get('character_states', {})
        
        closest_player = None
        closest_distance = float('inf')
        
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            char_pos = char_state.get('position', [0, 0])
            
            # Check LOS first (critical for ranged planning)
            if not self._check_line_of_sight(enemy_pos, char_pos, combat_state):
                continue  # Skip targets without LOS
            
            distance = self._manhattan_distance(enemy_pos, char_pos)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_player = {
                    'id': char_id,
                    'name': char_state.get('name', 'Player'),
                    'position': char_pos,
                    'distance': distance,
                    'current_hp': char_state.get('character_data', {}).get('current_hp', 10),
                    'max_hp': char_state.get('character_data', {}).get('max_hp', 10)
                }
        
        return closest_player

    def _find_weakest_player(self, enemy_pos: List[int], combat_state: Dict) -> Optional[Dict]:
        """
        Find the party member with lowest current HP (wounded prey)
        
        Args:
            enemy_pos: Enemy's current [x, y] position
            combat_state: Current combat state
            
        Returns:
            Dict with player info: {id, name, position, distance, current_hp, max_hp, hp_percent}
            or None if no living players found
        """
        character_states = combat_state.get('character_states', {})
        
        weakest = None
        lowest_hp = float('inf')
        
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            char_pos = char_state.get('position', [0, 0])
            char_data = char_state.get('character_data', {})
            
            # Get current HP
            if char_id == 'player':
                # Player character - might need special handling
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('hit_points', char_data.get('max_hp', 10))
            else:
                # Party member
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('max_hp', char_data.get('hit_points', 10))
            
            # Track the one with lowest CURRENT HP (absolute, not percentage)
            # This makes wounded characters high priority targets
            if current_hp < lowest_hp:
                lowest_hp = current_hp
                distance = self._manhattan_distance(enemy_pos, char_pos)
                
                weakest = {
                    'id': char_id,
                    'name': char_state.get('name', 'Character'),
                    'position': char_pos,
                    'distance': distance,
                    'current_hp': current_hp,
                    'max_hp': max_hp,
                    'hp_percent': (current_hp / max_hp * 100) if max_hp > 0 else 0
                }
        
        return weakest

    def _find_adjacent_players(self, enemy_pos: List[int], combat_state: Dict) -> List[Dict]:
        """Find all players adjacent to enemy (within 1 tile)"""
        adjacent = []
        character_states = combat_state.get("character_states", {})
        enemy_x, enemy_y = enemy_pos
        
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            char_pos = char_state.get('position', [0, 0])
            char_x, char_y = char_pos
            
            # Check if adjacent (Manhattan distance = 1)
            if abs(enemy_x - char_x) + abs(enemy_y - char_y) == 1:
                adjacent.append({
                    'id': char_id,
                    'name': char_state.get('name', 'Player'),
                    'position': char_pos
                })
        
        return adjacent
    
    def _find_best_move_toward_target(self, start_pos: List[int], target_pos: List[int], 
                                    movement_range: int, combat_state: Dict) -> List[int]:
        """
        Find best movement position to get closer to target
        Uses ACTUAL valid moves from CombatEngine
        """
        # Get valid moves calculated by CombatEngine
        valid_moves = combat_state.get('valid_moves', [])
        
        if not valid_moves:
            return start_pos  # Can't move
        
        # Find closest valid move to target
        best_pos = start_pos
        best_distance = self._manhattan_distance(start_pos, target_pos)
        
        for move_pos in valid_moves:
            distance = self._manhattan_distance(move_pos, target_pos)
            if distance < best_distance:
                best_distance = distance
                best_pos = move_pos
        
        return best_pos

    def _find_direct_path_to_target(self, start: List[int], target: List[int], movement_range: int, combat_state: Dict = None) -> List[int]:
        """
        Find direct path toward target using MovementSystem
        Uses centralized pathfinding for consistency
        """
        movement_system = combat_state.get('movement_system')
        if not movement_system:
            raise RuntimeError("MovementSystem not available in combat_state - this should never happen!")
        
        # Use MovementSystem to find actual path
        can_phase = True  # This is for incorporeal movement
        path = movement_system.find_path(start, target, can_phase, is_player=False)
        
        if path and len(path) > 1:
            # For melee attacks, stop ADJACENT (one before target)
            # Path includes start, so path[-1] is target, path[-2] is adjacent
            max_steps = min(movement_range + 1, len(path))
            
            # Stop one tile before target (adjacent for melee)
            destination_index = min(max_steps - 1, len(path) - 2)
            
            # Ensure we move at least one tile forward
            if destination_index < 1:
                destination_index = 1

            print(f"   🔍 Direct path debug:")
            print(f"      Start: {start}, Target: {target}")
            print(f"      Full path: {path}")
            print(f"      Movement range: {movement_range}")
            print(f"      Returning index {destination_index}: {path[destination_index]}")
            
            return path[destination_index]
        
        # No path found, stay put
        return start

    def _find_best_retreat_position(self, enemy_pos: List[int], player_pos: List[int],
                               movement_range: int, combat_state: Dict) -> List[int]:
        """Find position that maximizes distance from player using ACTUAL valid moves"""
        # Get valid moves from engine
        valid_moves = combat_state.get('valid_moves', [])
        
        if not valid_moves:
            return enemy_pos  # Can't move
        
        # Find valid move that's farthest from player
        best_pos = enemy_pos
        best_distance = self._manhattan_distance(enemy_pos, player_pos)
        
        for move_pos in valid_moves:
            distance = self._manhattan_distance(move_pos, player_pos)
            if distance > best_distance:  # Want maximum distance for retreat
                best_distance = distance
                best_pos = move_pos
        
        return best_pos
    
    def _manhattan_distance(self, pos1: List[int], pos2: List[int]) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _check_line_of_sight(self, start_pos: List[int], end_pos: List[int], combat_state: Dict) -> bool:
        """
        Check if there's line of sight between two positions
        Delegates to CombatEngine for authoritative LOS check
        """
        combat_engine = combat_state.get('combat_engine')
        if not combat_engine:
            # Fallback if engine not available (shouldn't happen)
            return True
        
        # Use engine's authoritative LOS check
        return combat_engine._has_line_of_sight(
            start_pos[0], start_pos[1],
            end_pos[0], end_pos[1]
        )

    def _find_retreat_position_from_player(self, enemy_pos: List[int], player_pos: List[int], 
                                       combat_state: Dict, min_distance: int = 2) -> Optional[List[int]]:
        """Find retreat position that maintains at least min_distance from player"""
        # Get valid moves from engine
        valid_moves = combat_state.get('valid_moves', [])
        
        if not valid_moves:
            return None
        
        # Find valid move that meets minimum distance requirement
        best_pos = None
        best_distance = 0
        
        for move_pos in valid_moves:
            distance = self._manhattan_distance(move_pos, player_pos)
            
            # Must meet minimum distance and be farther than current
            if distance >= min_distance and distance > best_distance:
                best_distance = distance
                best_pos = move_pos
        
        return best_pos

    def _find_move_to_range(self, start_pos: List[int], target_pos: List[int],
                       target_range: int, movement_range: int, combat_state: Dict) -> Optional[List[int]]:
        """Find movement position that gets us to target_range distance from target"""
        # Get valid moves from engine
        valid_moves = combat_state.get('valid_moves', [])
        
        if not valid_moves:
            return None
        
        current_distance = self._manhattan_distance(start_pos, target_pos)
        
        # Find move that gets closest to target_range
        best_pos = start_pos
        best_distance_diff = abs(current_distance - target_range)
        
        for move_pos in valid_moves:
            distance = self._manhattan_distance(move_pos, target_pos)
            distance_diff = abs(distance - target_range)
            
            # Prefer positions closer to target_range
            if distance_diff < best_distance_diff:
                best_distance_diff = distance_diff
                best_pos = move_pos
        
        return best_pos if best_pos != start_pos else None
    
    

    def _plan_rush_turn(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        Plan turn for RUSH_PLAYER behavior
        Strategy: Move toward player, attack if in range
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        if not closest_player:
            return {'move': None, 'attack': None, 'reason': 'no players found'}
        
        distance = closest_player['distance']
        
        # If already adjacent, attack (no move)
        if distance == 1:
            return {
                'move': None,
                'attack': {
                    'target_id': closest_player['id'],
                    'attack_index': 0  # Use first attack (melee)
                },
                'reason': 'already adjacent - attacking'
            }
        
        # Not adjacent - move closer then attack if we get in range
        movement_range = enemy_data.get("movement", {}).get("speed", 3)
        new_pos = self._find_best_move_toward_target(
            enemy_pos,
            closest_player['position'],
            movement_range,
            combat_state
        )
        
        # Check if move gets us in range
        new_distance = self._manhattan_distance(new_pos, closest_player['position'])
        
        if new_distance == 1:
            # Move will put us adjacent - attack after move!
            return {
                'move': new_pos,
                'attack': {
                    'target_id': closest_player['id'],
                    'attack_index': 0
                },
                'reason': 'moving into melee range then attacking'
            }
        else:
            # Move but can't reach attack range
            return {
                'move': new_pos,
                'attack': None,
                'reason': f'moving closer (distance {distance} -> {new_distance})'
            }

    def _plan_ranged_preference_turn(self, enemy_data: Dict, combat_state: Dict) -> Dict:
        """
        Plan turn for RANGED_PREFERENCE behavior
        Strategy: Stay at range 2-5, shoot with ranged weapon
        """
        enemy_pos = enemy_data.get("position", [0, 0])
        
        closest_player = self._find_closest_player(enemy_pos, combat_state)
        if not closest_player:
            return {'move': None, 'attack': None, 'reason': 'no players found'}
        
        distance = closest_player['distance']
        
        # Get attacks
        attacks = enemy_data.get("attacks", [])
        ranged_attack = None
        melee_attack = None
        
        for i, attack in enumerate(attacks):
            if attack.get("attack_type") == "ranged":
                ranged_attack = {'index': i, 'data': attack}
            elif attack.get("attack_type") == "melee":
                melee_attack = {'index': i, 'data': attack}
        
        # CASE 1: At ideal range (2-5) - shoot without moving
        if ranged_attack and 2 <= distance <= ranged_attack['data'].get("range", 5):
            return {
                'move': None,
                'attack': {
                    'target_id': closest_player['id'],
                    'attack_index': ranged_attack['index']
                },
                'reason': f'at ideal range ({distance}) - shooting'
            }
        
        # CASE 2: Too close (adjacent) - back away then shoot if possible
        if distance == 1:
            movement_range = enemy_data.get("movement", {}).get("speed", 3)
            retreat_pos = self._find_retreat_position_from_player(
                enemy_pos,
                closest_player['position'],
                combat_state,
                min_distance=2
            )
            
            if retreat_pos:
                new_distance = self._manhattan_distance(retreat_pos, closest_player['position'])
                
                # Can we shoot after backing away?
                if ranged_attack and 2 <= new_distance <= ranged_attack['data'].get("range", 5):
                    return {
                        'move': retreat_pos,
                        'attack': {
                            'target_id': closest_player['id'],
                            'attack_index': ranged_attack['index']
                        },
                        'reason': f'backing away to range {new_distance} then shooting'
                    }
                else:
                    return {
                        'move': retreat_pos,
                        'attack': None,
                        'reason': 'backing away from melee'
                    }
            
            # Can't retreat - cornered! Melee as last resort
            if melee_attack:
                return {
                    'move': None,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': melee_attack['index']
                    },
                    'reason': 'cornered - desperate melee'
                }
        
        # CASE 3: Too far (6+) - move to ideal range (3-4) then shoot if in range
        if ranged_attack:
            movement_range = enemy_data.get("movement", {}).get("speed", 3)
            new_pos = self._find_move_to_range(
                enemy_pos,
                closest_player['position'],
                target_range=3,  # Ideal shooting distance
                movement_range=movement_range,
                combat_state=combat_state
            )
            
            new_distance = self._manhattan_distance(new_pos, closest_player['position'])
            
            # Can we shoot after moving?
            if 2 <= new_distance <= ranged_attack['data'].get("range", 5):
                return {
                    'move': new_pos,
                    'attack': {
                        'target_id': closest_player['id'],
                        'attack_index': ranged_attack['index']
                    },
                    'reason': f'moving to range {new_distance} then shooting'
                }
            else:
                return {
                    'move': new_pos,
                    'attack': None,
                    'reason': f'moving closer (distance {distance} -> {new_distance})'
                }
        
        # No ranged attack - fall back to rush behavior
        return self._plan_rush_turn(enemy_data, combat_state)

    def _select_best_attack(self, enemy_data: Dict, enemy_pos: List[int], 
                           target_pos: List[int], behavior_type: str, 
                           combat_state: Dict) -> Optional[int]:
        """
        Select best attack from enemy's attacks array
        
        Args:
            enemy_data: Enemy instance data
            enemy_pos: Enemy's current position
            target_pos: Target position
            behavior_type: 'opportunistic', 'ranged_only', 'spell_focused', 'melee_only'
            combat_state: Combat state dict
            
        Returns:
            attack_index (int) or None if no valid attack
        """
        attacks = enemy_data.get("attacks", [])
        if not attacks:
            return None
        
        distance = self._manhattan_distance(enemy_pos, target_pos)
        current_spell_slots = enemy_data.get("current_spell_slots", 0)
        
        # DEBUG
        enemy_name = enemy_data.get("name", "Enemy")
        print(f"   🎯 ATTACK SELECTION DEBUG for {enemy_name}:")
        print(f"      Distance to target: {distance}")
        print(f"      Current spell slots: {current_spell_slots}")
        print(f"      Behavior type: {behavior_type}")
        print(f"      Number of attacks: {len(attacks)}")

        # Score each attack option
        attack_scores = []
        
        for idx, attack in enumerate(attacks):
            score = 0
            attack_type = attack.get("attack_type", "melee")
            attack_range = attack.get("range", 1)
            spell_cost = attack.get("spell_cost", 0)
            
            # Get range - for spells, need to look up from spell data
            if attack_type == "spell":
                spell_id = attack.get("spell_id")
                spell_data = combat_state.get('spell_data', {})
                if spell_id and spell_data:
                    spell_info = spell_data.get(spell_id, {})
                    attack_range = spell_info.get("range", 1)
                else:
                    attack_range = attack.get("range", 1)  # Fallback
            else:
                attack_range = attack.get("range", 1)

            # Skip if spell with no slots
            if spell_cost > 0 and current_spell_slots < spell_cost:
                continue
            
            # Check if attack is in range
            if distance > attack_range:
                print(f"      ❌ {attack.get('name')} out of range (need {attack_range}, have {distance})")
                continue
            
            print(f"      ✅ {attack.get('name')} in range! Range={attack_range}, Distance={distance}")
            
            # Check line of sight for spells that require it
            if attack_type == "spell":
                spell_id = attack.get("spell_id")
                spell_data = combat_state.get('spell_data', {})
                if spell_id and spell_data:
                    spell_info = spell_data.get(spell_id, {})
                    requires_los = spell_info.get('requires_line_of_sight', False)
                    
                    if requires_los:
                        # Use existing LOS system (same as ranged attacks!)
                        combat_engine = combat_state.get('combat_engine')
                        if combat_engine:
                            has_los = combat_engine._has_line_of_sight(
                                enemy_pos[0], enemy_pos[1],
                                target_pos[0], target_pos[1]
                            )
                            
                            if not has_los:
                                print(f"      ❌ {attack.get('name')} blocked by walls (no LOS)")
                                continue  # No line of sight, skip
            
            # BASE SCORE: Expected damage (rough estimate)
            damage_dice = attack.get("damage_dice", "1d4")
            # Simple heuristic: count dice (e.g., "3d6" = 3)
            if 'd' in damage_dice:
                num_dice = int(damage_dice.split('d')[0])
                score += num_dice * 5
            
            # BEHAVIOR MODIFIERS
            if behavior_type == "spell_focused":
                if attack_type == "spell":
                    score += 50  # Heavily prefer spells
                elif attack_type == "ranged":
                    score += 10  # Ranged okay
                # Melee gets no bonus
                
            elif behavior_type == "ranged_only":
                if attack_type == "ranged" or attack_type == "spell":
                    score += 30  # Prefer ranged/spells
                else:
                    score -= 50  # Penalize melee heavily
                    
            elif behavior_type == "melee_only":
                if attack_type == "melee":
                    score += 30
                else:
                    score -= 30
                    
            elif behavior_type == "opportunistic":
                # No strong preference, just use what's in range
                score += 10
            
            # RANGE BONUS: Prefer attacks we can use at current distance
            if distance <= attack_range:
                score += 10
            
            # RESOURCE CONSERVATION: Penalize using spell slots if low
            if spell_cost > 0:
                if current_spell_slots <= 1:
                    score -= 25  # Save last slot!
                elif current_spell_slots <= 2:
                    score -= 10  # Getting low
            
            attack_scores.append((idx, score, attack.get("name", "Attack")))
        
        # No valid attacks
        if not attack_scores:
            print(f"      ❌ NO VALID ATTACKS FOUND!")
            return None
        
        # Return highest scoring attack
        attack_scores.sort(key=lambda x: x[1], reverse=True)
        best_idx, best_score, best_name = attack_scores[0]
        
        print(f"      🎯 Selected attack: {best_name} (index {best_idx}, score {best_score})")
        
        return best_idx

# Singleton instance
_combat_ai_instance = None

def get_combat_ai():
    """Get singleton CombatAI instance"""
    global _combat_ai_instance
    if _combat_ai_instance is None:
        _combat_ai_instance = CombatAI()
    return _combat_ai_instance