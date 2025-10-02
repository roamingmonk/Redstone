# game_logic/combat_engine.py
"""
Combat Engine - Turn-based tactical combat business logic
Follows existing game_logic pattern for core game systems
"""

import json
import os
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple
from utils.combat_loader import get_combat_loader
from utils.stats_calculator import get_stats_calculator

class CombatPhase(Enum):
    """Combat phase tracking"""
    SETUP = "setup"
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    RESOLUTION = "resolution"
    VICTORY = "victory"
    DEFEAT = "defeat"

class CombatEngine:
    """
    Core business logic engine for tactical combat system
    
    Responsibilities:
    - Turn management and sequence control
    - Movement validation and pathfinding
    - Attack resolution and damage calculation
    - AI behavior processing
    - Victory condition checking
    """
    
    def __init__(self, event_manager, game_state, save_manager=None):
        """Initialize with existing game systems"""
        self.event_manager = event_manager
        self.game_state = game_state
        self.save_manager = save_manager
        self.combat_loader = get_combat_loader()
        self.stats_calculator = get_stats_calculator()
        
        # Current combat state
        self.combat_data = None
        self.current_phase = CombatPhase.SETUP
        self.turn_order = []
        self.current_actor_index = 0
        self.combat_log = []
        self.current_action_mode = None  # Track current UI interaction mode
        
        # Player combat state
        # self.player_position = None
        # self.player_has_moved = False
        # self.player_has_acted = False
        # self.player_attacks_used = 0 
        self.character_states = {}  # Dict of character_id -> state
        self.active_character_id = None  # Currently acting character


        #Register combat events (following SaveManager pattern)
        if event_manager:
            from ui.combat_system import register_combat_system_events
            register_combat_system_events(event_manager, self)

            event_manager.register("DEATH_ACTION_LOAD_GAME", self._handle_death_load_game)
            event_manager.register("DEATH_ACTION_RESTART_COMBAT", self._handle_death_restart_combat)
            event_manager.register("DEATH_ACTION_RETURN_TO_TITLE", self._handle_death_return_to_title)
            print("💀 Death overlay events registered in CombatEngine")
        
        print("CombatEngine initialized")
    
    def _get_movement_range(self) -> int:
        """Get movement range for active character"""
        if not self.active_character_id:
            return 3  # Default fallback
        
        char_state = self.character_states.get(self.active_character_id)
        if not char_state:
            return 3  # Default fallback
        
        # TODO: Eventually read from character class/equipment
        # For now, all characters have 3 movement
        return 3

    def start_encounter(self, encounter_id: str, combat_context: Dict = None) -> bool:
        """
        Load encounter data and initialize combat state
        Args:encounter_id: ID of encounter to load
            combat_context: Location-specific context from calling screen
        Returns: bool: True if combat started successfully
        """
        # Ensure party member data is synced before combat
        self.game_state.sync_party_member_data()
        print(f"🔄 Synced party data before combat")
       
       # CRITICAL: Clear any existing combat data first
        self.combat_data = None
        self.combat_log = []
        self.player_position = None
        self.player_has_moved = False
        self.player_has_acted = False
        self.player_attacks_used = 0
        self.turn_order = []
        self.current_actor_index = 0



        
        # ========== DYNAMIC AUTOSAVE ==========
        try:
            if self.save_manager:
                print("💾 Creating autosave before combat...")
                 
                # Store current screen (will be 'combat')
                combat_screen = self.game_state.screen
                
                # Get the screen player was on before combat started
                previous_screen = getattr(self.game_state, 'previous_screen', None)
                
                if previous_screen:
                    # Store encounter ID for restart
                    self.game_state.pending_combat_encounter = encounter_id
                    
                    # CRITICAL: Store current HP and restore to max for the save
                    original_hp = self.game_state.character.get("current_hp", 0)
                    max_hp = self.game_state.character.get("hit_points", 10)
                    
                    # Temporarily restore to full HP for the autosave
                    self.game_state.character["current_hp"] = max_hp
                    
                    # Temporarily set screen to pre-combat location
                    self.game_state.screen = previous_screen
                    
                    # Create autosave WITH full HP
                    self.save_manager.save_game(save_slot=0)
                    
                    # Restore original HP and screen
                    self.game_state.character["current_hp"] = original_hp
                    self.game_state.pending_combat_encounter = None
                    self.game_state.screen = combat_screen
                    
                    print(f"✅ Combat autosave created (slot 0) at {previous_screen} with full HP")
                else:
                    print("⚠️ No previous_screen available - skipping autosave")
                    print("   Combat was likely triggered without proper screen transition")
            else:
                print("⚠️ SaveManager not available - skipping autosave")
        except Exception as e:
            print(f"⚠️ Autosave failed: {e}")
            import traceback
            traceback.print_exc()
        # ========== END AUTOSAVE BLOCK ==========
        
        try:
            print(f"🎯 Starting combat encounter: {encounter_id}")
             
            # SAFETY: Ensure current_hp exists before combat
            if 'current_hp' not in self.game_state.character:
                max_hp = self.game_state.character.get('hit_points', 10)
                self.game_state.character['current_hp'] = max_hp
                print(f"⚠️ Initialized missing current_hp to {max_hp}")
                
            # Load complete combat instance
            self.combat_data = self.combat_loader.create_combat_instance(encounter_id, combat_context)
            if not self.combat_data:
                print(f"❌ Failed to load combat encounter: {encounter_id}")
                return False
            
            # Initialize party member positions
            player_positions = self.combat_data.get("player_positions", [])
            if not player_positions or len(player_positions) < 4:
                print(f"⚠️ Encounter needs exactly 4 starting positions")
                return False
            
            # Get active party members from game_state
            party_members = self._get_active_party_members()
            
            # Assign positions to party members (shuffle positions randomly)
            import random
            shuffled_positions = player_positions.copy()
            random.shuffle(shuffled_positions)
            
            for idx, member in enumerate(party_members):
                character_id = member['id']
                position = shuffled_positions[idx] if idx < len(shuffled_positions) else [0, 0]
                
                self.character_states[character_id] = {
                    'name': member['name'],
                    'position': position,
                    'has_moved': False,
                    'attacks_used': 0,
                    'is_alive': True,
                    'dexterity': member.get('stats', {}).get('dexterity', 10),
                    'character_data': member  # Store full character data
                }
            
            print(f"✅ Initialized {len(party_members)} party members")
            
            # Set up turn order (simple: player first, then enemies)
            self._initialize_turn_order()
            
            # Initialize combat phase
            self.current_phase = CombatPhase.PLAYER_TURN
            self.current_actor_index = 0
            
            # Set the first active character
            if self.turn_order:
                first_actor_id = self.turn_order[0]
                if first_actor_id in self.character_states:
                    self.active_character_id = first_actor_id
                    char_state = self.character_states[first_actor_id]
                    char_state['has_moved'] = False
                    char_state['attacks_used'] = 0
                    print(f"🎯 First turn: {char_state['name']}")
            
            # Add initial combat log entry
            encounter_name = self.combat_data["encounter"]["name"]
            self._add_to_combat_log(f"Combat begins: {encounter_name}")
            
            # Emit combat started event
            self.event_manager.emit("COMBAT_STARTED", {
                "encounter_id": encounter_id,
                "encounter_name": encounter_name
            })
            
            print(f"✅ Combat started successfully: {encounter_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting combat: {e}")
            return False
    
    def _get_active_party_members(self):
        """Get all active party members including player character"""
        party = []
        
        # Add player character first
        player_char = {
            'id': 'player',
            'name': self.game_state.character.get('name', 'Hero'),
            'class': self.game_state.character.get('class', 'Fighter'),
            'level': self.game_state.character.get('level', 1),
            'stats': {
                'dexterity': self.game_state.character.get('dexterity', 10),
                'strength': self.game_state.character.get('strength', 10),
                'constitution': self.game_state.character.get('constitution', 10),
            },
            'current_hp': self.game_state.character.get('current_hp', 
                                                        self.game_state.character.get('hit_points', 20)),
            'max_hp': self.game_state.character.get('hit_points', 20)
        }
        party.append(player_char)
        
        # Add recruited party members
        for member_data in self.game_state.party_member_data:
            party_member = {
                'id': member_data['id'],
                'name': member_data['name'],
                'class': member_data['class'],
                'level': member_data['level'],
                'stats': member_data.get('stats', {}),
                'current_hp': member_data.get('current_hp', member_data.get('hit_points', 20)),
                'max_hp': member_data.get('hit_points', 20)
            }
            party.append(party_member)
        
        return party
    
    def get_combat_data_for_ui(self) -> Dict:
        """
        Return all data needed for UI rendering
        Returns:Dict containing complete combat state for UI
        """
        if not self.combat_data:
            return {
                "error": "No combat data available",
                "combat_active": False
            }
        
        current_actor = self._get_current_actor_name()
        
        return {
            "combat_active": True,
            "encounter": self.combat_data.get("encounter", {}),
            "battlefield": self.combat_data.get("battlefield", {}),
            "enemy_instances": self.combat_data.get("enemy_instances", []),
            "character_states": self.character_states,
            "active_character_id": self.active_character_id,
            #"player_position": self.player_position,
            "current_actor": current_actor,
            "combat_phase": self.current_phase.value,
            "turn_number": self.combat_data.get("turn_number", 0),
            "combat_log": self.combat_log[-10:],  # Last 10 messages
            "player_actions": self._get_available_player_actions(),
            "player_state": self._get_active_character_state(),
            "current_action_mode": self.current_action_mode, 
            "highlighted_tiles": self._get_highlighted_tiles()
        }

    def _get_active_character_state(self) -> Dict:
        """Get the active character's state for UI display"""
        if not self.active_character_id:
            # Fallback to default state
            return {
                "has_moved": False,
                "has_acted": False,
                "attacks_used": 0,
                "attacks_per_round": 1,
                "has_attack_targets": False,
                "current_hp": 10,
                "max_hp": 10
            }
        
        char_state = self.character_states.get(self.active_character_id)
        if not char_state:
            return {
                "has_moved": False,
                "has_acted": False,
                "attacks_used": 0,
                "attacks_per_round": 1,
                "has_attack_targets": False,
                "current_hp": 10,
                "max_hp": 10
            }
        
        # Get character data
        char_data = char_state.get('character_data', {})
        char_position = char_state.get('position', [0, 0])
        
        # Check for attack targets
        attack_targets = self.get_attack_targets(char_position, 1)
        
        return {
            "has_moved": char_state.get('has_moved', False),
            "has_acted": char_state.get('has_acted', False),
            "attacks_used": char_state.get('attacks_used', 0),
            "attacks_per_round": self._get_attacks_per_round(char_data),
            "has_attack_targets": len(attack_targets) > 0,
            "current_hp": char_data.get('current_hp', 10),
            "max_hp": char_data.get('max_hp', 10)
        }

    def set_action_mode(self, mode: str):
        """Set current action mode for UI interaction"""
        self.current_action_mode = mode
        print(f"Action mode set to: {mode}")

    def get_valid_moves(self, actor_position: List[int], movement_range: int) -> List[List[int]]:
        """
        Calculate valid movement squares considering obstacles and other units
        
        Args:
            actor_position: Current [x, y] position
            movement_range: Number of tiles actor can move
            
        Returns:
            List of valid [x, y] positions
        """
        valid_moves = []
        start_x, start_y = actor_position
        
        battlefield = self.combat_data.get("battlefield", {})
        dimensions = battlefield.get("dimensions", {"width": 12, "height": 8})
        
        # Check all positions within movement range
        for dx in range(-movement_range, movement_range + 1):
            for dy in range(-movement_range, movement_range + 1):
                # Manhattan distance check
                if abs(dx) + abs(dy) <= movement_range and (dx != 0 or dy != 0):
                    new_x = start_x + dx
                    new_y = start_y + dy
                    
                    # Check bounds
                    if 0 <= new_x < dimensions["width"] and 0 <= new_y < dimensions["height"]:
                        # Check if tile is walkable
                        if self._is_tile_walkable(new_x, new_y):
                            valid_moves.append([new_x, new_y])
        
        return valid_moves
    
    def get_attack_targets(self, actor_position: List[int], attack_range: int = 1) -> List[Dict]:
        """
        Find valid attack targets within range
        Args:actor_position: Attacker's [x, y] position
            attack_range: Attack range in tiles
        Returns:List of target dictionaries with position and target info
        """
        targets = []
        start_x, start_y = actor_position
        
        # For player attacks, check enemy positions
        if self.current_phase == CombatPhase.PLAYER_TURN:
            enemy_instances = self.combat_data.get("enemy_instances", [])
            for enemy in enemy_instances:
                if enemy.get("current_hp", 0) > 0:  # Only living enemies
                    enemy_pos = enemy.get("position", [0, 0])
                    enemy_x, enemy_y = enemy_pos
                    
                    # Check if in range (Manhattan distance)
                    distance = abs(start_x - enemy_x) + abs(start_y - enemy_y)
                    if distance <= attack_range:
                        targets.append({
                            "position": enemy_pos,
                            "target_type": "enemy",
                            "target_id": enemy.get("instance_id"),
                            "target_name": enemy.get("name", "Enemy"),
                            "distance": distance
                        })
        
        # For enemy attacks, check all party member positions
        else:
            for char_id, char_state in self.character_states.items():
                if char_state.get('is_alive', True):
                    char_pos = char_state['position']
                    char_x, char_y = char_pos
                    
                    # Check if in range (Manhattan distance)
                    distance = abs(start_x - char_x) + abs(start_y - char_y)
                    if distance <= attack_range:
                        targets.append({
                            "position": char_pos,
                            "target_type": "player",
                            "target_id": char_id,
                            "target_name": char_state['name'],
                            "distance": distance
                        })
        
        return targets
    
    def execute_player_move(self, target_position: List[int]) -> bool:
        """Execute active character movement to target position"""
        print(f"🔍 DEBUG execute_player_move called")
        print(f"   Phase: {self.current_phase}")
        print(f"   Active character ID: {self.active_character_id}")
        if self.current_phase != CombatPhase.PLAYER_TURN:
            return False
        
        if not self.active_character_id:
            print(f"   ❌ No active character ID!")
            return False
        
        char_state = self.character_states[self.active_character_id]
        print(f"   Character: {char_state.get('name')}")
        print(f"   Current position: {char_state['position']}")
        print(f"   Target position: {target_position}")
        print(f"   Has moved: {char_state['has_moved']}")
        if char_state['has_moved']:
            self._add_to_combat_log("Already moved this turn!")
            return False
        
        # Validate movement
        movement_range = self._get_movement_range()  # uses helper
        valid_moves = self.get_valid_moves(char_state['position'], movement_range)
        
        if target_position not in valid_moves:
            self._add_to_combat_log("Invalid movement target!")
            return False
        
        # Execute move
        old_pos = char_state['position']
        char_state['position'] = target_position
        char_state['has_moved'] = True
        
        char_name = char_state['name']
        
        # Clear action mode after successful move
        self.current_action_mode = None  

        self._add_to_combat_log(f"{char_name} moved to [{target_position[0]}, {target_position[1]}]")
        
        # Emit movement event for UI
        self.event_manager.emit("COMBAT_UNIT_MOVED", {
            "unit_type": "player",
            "old_position": old_pos,
            "new_position": target_position
        })
        
        return True
    
    def execute_player_attack(self, target_position: List[int]) -> bool:
        """Execute active character attack on target enemy"""
        if self.current_phase != CombatPhase.PLAYER_TURN:
            return False
        
        if not self.active_character_id:
            return False
        
        char_state = self.character_states[self.active_character_id]
        
        # Find target enemy
        enemy_instances = self.combat_data.get("enemy_instances", [])
        target_enemy = None
        for enemy in enemy_instances:
            if enemy.get("position") == target_position and enemy.get("current_hp", 0) > 0:
                target_enemy = enemy
                break
        
        if not target_enemy:
            self._add_to_combat_log("No valid target!")
            return False
        
        # Validate range
        attack_targets = self.get_attack_targets(char_state['position'])
        valid_target = any(t["position"] == target_position for t in attack_targets)
        
        if not valid_target:
            self._add_to_combat_log("Target out of range!")
            return False
        
        # Execute attack
        success = self._resolve_attack(
            attacker_type="player",
            attacker_data=char_state['character_data'],
            target_data=target_enemy
        )
        
        # Increment attack counter regardless of hit/miss
        char_state['attacks_used'] += 1

        # Check if all attacks used
        attacks_per_round = self._get_attacks_per_round(char_state['character_data'])
        if char_state['attacks_used'] >= attacks_per_round:
            char_state['has_acted'] = True
            self.current_action_mode = None
            char_name = char_state['name']
            self._add_to_combat_log(f"{char_name}: All attacks used")

        if success:
            # Check if target was defeated
            if target_enemy.get("current_hp", 0) <= 0:
                target_name = target_enemy.get("name", "Enemy")
                self._add_to_combat_log(f"{target_name} defeated!")
                
                # Check victory conditions
                if self._check_victory_conditions():
                    self._handle_combat_victory()
                    return True

        return success
    
    def _get_attacks_per_round(self, character_data=None) -> int:
        """Get number of attacks character gets per round"""
        # If no character data provided or player character, use game_state
        if character_data is None or character_data.get('id') == 'player':
            attacks, _ = self.stats_calculator.calculate_attacks_per_round(self.game_state)
            return attacks
        
        # For party members, simple class-based calculation
        # TODO: Eventually integrate party members with stats_calculator
        char_class = character_data.get('class', 'Fighter').lower()
        level = character_data.get('level', 1)
        
        # Fighters get 2 attacks at level 5+
        if char_class == 'fighter' and level >= 5:
            return 2
        
        # Everyone else gets 1 attack
        return 1

    def end_player_turn(self):
        """End the active character's turn and advance to next actor"""
        if self.current_phase != CombatPhase.PLAYER_TURN:
            return
        
        if not self.active_character_id:
            return
        
        char_state = self.character_states.get(self.active_character_id)
        if char_state:
            char_name = char_state['name']
            self._add_to_combat_log(f"{char_name} ends turn")
        
        # Advance to next actor
        self._advance_turn()
    
    def _initialize_turn_order(self):
        """Set up turn order based on DEX-based initiative"""
        combatants = []
        
        # Add all party members with their DEX
        for char_id, char_state in self.character_states.items():
            combatants.append({
                'id': char_id,
                'name': char_state['name'],
                'dex': char_state['dexterity'],
                'type': 'player'
            })
        
        # Add all enemies with their DEX
        enemy_instances = self.combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            if enemy.get("current_hp", 0) > 0:
                combatants.append({
                    'id': enemy.get("instance_id"),
                    'name': enemy.get("name", "Enemy"),
                    'dex': enemy.get("stats", {}).get("dexterity", 10),
                    'type': 'enemy'
                })
        
        # Sort by DEX (highest first), then by random roll for ties
        import random
        for c in combatants:
            c['initiative'] = c['dex'] + random.randint(1, 20)
        
        combatants.sort(key=lambda x: x['initiative'], reverse=True)
        
        # Build turn order list
        self.turn_order = [c['id'] for c in combatants]
        
        print(f"🎯 Initiative Order:")
        for c in combatants:
            print(f"   {c['name']}: {c['initiative']} (DEX {c['dex']})")
    
    def _advance_turn(self):
        """Advance to next actor in turn order"""
        self.current_actor_index += 1
        
        # If we've gone through all actors, start new round
        if self.current_actor_index >= len(self.turn_order):
            self.current_actor_index = 0
            turn_number = self.combat_data.get("turn_number", 0) + 1
            self.combat_data["turn_number"] = turn_number
            self._add_to_combat_log(f"--- Turn {turn_number} ---")
        
# Set phase based on current actor
        current_actor_id = self.turn_order[self.current_actor_index]
        
        # Check if current actor is a party member or enemy
        if current_actor_id in self.character_states:
            # Party member's turn
            self.current_phase = CombatPhase.PLAYER_TURN
            self.active_character_id = current_actor_id
            
            # Reset action flags for this character
            char_state = self.character_states[current_actor_id]
            char_state['has_moved'] = False
            char_state['attacks_used'] = 0
            
            char_name = char_state['name']
            self._add_to_combat_log(f"{char_name}'s turn")
        #TODO CHECK is this else statement is correct
        else:
            self.current_phase = CombatPhase.ENEMY_TURN
            self._execute_enemy_turn(current_actor_id)
    
    def _execute_enemy_turn(self, enemy_id: str):
        """Execute AI turn for enemy"""
        # Find enemy instance
        enemy_instances = self.combat_data.get("enemy_instances", [])
        enemy = None
        for e in enemy_instances:
            if e.get("instance_id") == enemy_id and e.get("current_hp", 0) > 0:
                enemy = e
                break
        
        if not enemy:
            # Enemy is dead, skip turn
            self._advance_turn()
            return
        
        enemy_name = enemy.get("name", "Enemy")
        self._add_to_combat_log(f"{enemy_name}'s turn")
        
        # Simple AI: Move toward player and attack if in range
        self._execute_basic_ai(enemy)
        
        # Log enemy turn end
        enemy_name = enemy.get("name", "Enemy") if enemy else "Enemy"
        self._add_to_combat_log(f"{enemy_name} ends turn")

        # End enemy turn
        self._advance_turn()
    
    def _execute_basic_ai(self, enemy: Dict):
        """Execute basic AI behavior for enemy"""
        enemy_pos = enemy.get("position", [0, 0])
        enemy_name = enemy.get("name", "Enemy")
        
        # Check if any party member is in attack range
        attack_targets = self._get_enemy_attack_targets(enemy_pos)
        if attack_targets:
            # Attack closest target
            closest_target = min(attack_targets, key=lambda t: t['distance'])
            target_char_id = closest_target['target_id']
            target_char_state = self.character_states.get(target_char_id)
            
            if target_char_state:
                target_name = target_char_state['name']
                self._add_to_combat_log(f"{enemy_name} attacks {target_name}!")
                
                # Get the actual character data for attack resolution
                target_char_data = target_char_state['character_data']
                
                self._resolve_attack(
                    attacker_type="enemy",
                    attacker_data=enemy,
                    target_data=target_char_data
                )
        else:
            # Find nearest party member to move toward
            nearest_target_pos = self._find_nearest_party_member(enemy_pos)
            
            if nearest_target_pos:
                movement_speed = enemy.get("movement", {}).get("speed", 3)
                new_position = self._find_best_move_toward_target(enemy_pos, nearest_target_pos, movement_speed)
                
                if new_position != enemy_pos:
                    enemy["position"] = new_position
                    self._add_to_combat_log(f"{enemy_name} moves to ({new_position[0]}, {new_position[1]})")
                    
                    # Emit movement event
                    self.event_manager.emit("COMBAT_UNIT_MOVED", {
                        "unit_type": "enemy",
                        "unit_id": enemy.get("instance_id"),
                        "old_position": enemy_pos,
                        "new_position": new_position
                    })
    
    def _find_nearest_party_member(self, enemy_pos: List[int]) -> List[int]:
        """Find the position of the nearest living party member"""
        nearest_pos = None
        nearest_distance = float('inf')
        
        for char_id, char_state in self.character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            char_pos = char_state['position']
            distance = abs(enemy_pos[0] - char_pos[0]) + abs(enemy_pos[1] - char_pos[1])
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_pos = char_pos
        
        return nearest_pos
    
    def _resolve_attack(self, attacker_type: str, attacker_data: Dict, target_data: Dict) -> bool:
        """
        Resolve attack using StatsCalculator integration
        
        Args:
            attacker_type: "player" or "enemy"
            attacker_data: Attacker's data (character or enemy instance)
            target_data: Target's data (character or enemy instance)
            
        Returns:
            bool: True if attack hit
        """
        try:
            if attacker_type == "player":
                # Player attacking enemy
                attacker_name = attacker_data.get("name", "Player")
                target_name = target_data.get("name", "Enemy")
                
                # Use StatsCalculator for player attack
                attack_bonus = self.stats_calculator.calculate_attack_bonus(self.game_state)[0]
                damage_string = self.stats_calculator.calculate_weapon_damage(self.game_state)[0]
                
                # Target AC from enemy stats
                target_ac = target_data.get("stats", {}).get("ac", 10)
                
            else:
                # Enemy attacking player
                attacker_name = attacker_data.get("name", "Enemy")
                target_name = target_data.get("name", "Player")
                
                # Enemy attack from enemy data
                attacks = attacker_data.get("attacks", [])
                if attacks:
                    attack = attacks[0]  # Use first attack
                    attack_bonus = attack.get("attack_bonus", 0)
                    damage_string = attack.get("damage_dice", "1d4")
                else:
                    attack_bonus = 0
                    damage_string = "1d4"
                
                # Player AC from StatsCalculator
                target_ac = self.stats_calculator.calculate_armor_class(self.game_state)[0]
            
            # Roll attack (d20 + bonus vs AC)
            attack_roll = random.randint(1, 20)
            total_attack = attack_roll + attack_bonus
            
            self._add_to_combat_log(f"{attacker_name} attacks {target_name}")
            self._add_to_combat_log(f"Attack roll: {attack_roll} + {attack_bonus} = {total_attack} vs AC {target_ac}")
            
            if total_attack >= target_ac:
                # Hit! Roll damage
                damage = self._roll_damage(damage_string)
                self._add_to_combat_log(f"Hit! {damage} damage")
                
                # Apply damage
                if attacker_type == "player":
                    # Damage enemy
                    current_hp = target_data.get("current_hp", 0)
                    new_hp = max(0, current_hp - damage)
                    target_data["current_hp"] = new_hp
                    self._add_to_combat_log(f"{target_name}: {new_hp}/{target_data.get('stats', {}).get('hp', 0)} HP")
                else:
                    # Damage player
                    current_hp = self.game_state.character.get("current_hp", 0)
                    new_hp = max(0, current_hp - damage)
                    self.game_state.character["current_hp"] = new_hp
                    
                    #Show current/max HP in combat log
                    max_hp = self.game_state.character.get("hit_points", 0)
                    self._add_to_combat_log(f"{target_name}: {new_hp}/{max_hp} HP")
                    
                    # Check if player defeated
                    if new_hp <= 0:
                        self._handle_combat_defeat()
                
                return True
            else:
                # Miss
                self._add_to_combat_log("Miss!")
                return False
                
        except Exception as e:
            print(f"❌ Error resolving attack: {e}")
            self._add_to_combat_log("Attack failed!")
            return False
    
    def _roll_damage(self, damage_string: str) -> int:
        """
        Roll damage from dice notation (e.g., "1d4+1")
        
        Args:
            damage_string: Damage in dice notation
            
        Returns:
            int: Rolled damage amount
        """
        try:
            # Simple parser for "XdY+Z" format
            if '+' in damage_string:
                dice_part, bonus_part = damage_string.split('+')
                bonus = int(bonus_part)
            elif '-' in damage_string:
                dice_part, bonus_part = damage_string.split('-')
                bonus = -int(bonus_part)
            else:
                dice_part = damage_string
                bonus = 0
            
            if 'd' in dice_part:
                num_dice, die_size = dice_part.split('d')
                num_dice = int(num_dice)
                die_size = int(die_size)
                
                total = sum(random.randint(1, die_size) for _ in range(num_dice))
                return max(1, total + bonus)  # Minimum 1 damage
            else:
                return max(1, int(damage_string))
                
        except:
            return 1  # Fallback
    
    def _is_tile_walkable(self, x: int, y: int) -> bool:
        """Check if tile at position is walkable"""
        battlefield = self.combat_data.get("battlefield", {})
        
        # Check walls
        if self._is_wall_tile(x, y, battlefield):
            return False
        
        # Check obstacles
        if self._is_obstacle_tile(x, y, battlefield):
            return False
        
        # Check if another unit occupies this tile
        if self._is_tile_occupied(x, y):
            return False
        
        return True
    
    def _is_wall_tile(self, x: int, y: int, battlefield: Dict) -> bool:
        """Check if tile position is a wall"""
        terrain = battlefield.get('terrain', {})
        walls = terrain.get('walls', [])
        
        for wall in walls:
            if len(wall) == 4:
                x1, y1, x2, y2 = wall
                if self._point_on_line_segment(x, y, x1, y1, x2, y2):
                    return True
        return False
    
    def _is_obstacle_tile(self, x: int, y: int, battlefield: Dict) -> bool:
        """Check if tile position has an obstacle"""
        terrain = battlefield.get('terrain', {})
        obstacles = terrain.get('obstacles', [])
        
        for obstacle in obstacles:
            obs_pos = obstacle.get('position', [])
            if len(obs_pos) == 2 and obs_pos[0] == x and obs_pos[1] == y:
                return True
        return False
    
    def _is_tile_occupied(self, x: int, y: int) -> bool:
        """Check if tile is occupied by a unit"""
        # Check player position
        if self.player_position == [x, y]:
            return True
        
        # Check enemy positions
        enemy_instances = self.combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            if enemy.get("current_hp", 0) > 0 and enemy.get("position") == [x, y]:
                return True
        
        return False
    
    def _point_on_line_segment(self, px: int, py: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if point is on line segment"""
        if x1 == x2:  # Vertical line
            return px == x1 and min(y1, y2) <= py <= max(y1, y2)
        elif y1 == y2:  # Horizontal line
            return py == y1 and min(x1, x2) <= px <= max(x1, x2)
        return False
    
    def _find_best_move_toward_target(self, start_pos: List[int], target_pos: List[int], movement_range: int) -> List[int]:
        """Find best movement toward target within range"""
        start_x, start_y = start_pos
        target_x, target_y = target_pos
        
        best_pos = start_pos
        best_distance = abs(start_x - target_x) + abs(start_y - target_y)
        
        # Check all valid moves
        valid_moves = self.get_valid_moves(start_pos, movement_range)
        for move_pos in valid_moves:
            move_x, move_y = move_pos
            distance = abs(move_x - target_x) + abs(move_y - target_y)
            
            if distance < best_distance:
                best_distance = distance
                best_pos = move_pos
        
        return best_pos
    
    def _get_enemy_attack_targets(self, enemy_pos: List[int]) -> List[Dict]:
        """Get attack targets for enemy at position"""
        targets = []
        enemy_x, enemy_y = enemy_pos
        
        # Check all party members for targets in melee range
        for char_id, char_state in self.character_states.items():
            if not char_state.get('is_alive', True):
                continue  # Skip dead characters
            
            char_pos = char_state['position']
            char_x, char_y = char_pos
            
            # Check if character is in melee range (distance 1)
            distance = abs(enemy_x - char_x) + abs(enemy_y - char_y)
            if distance <= 1:
                targets.append({
                    "position": char_pos,
                    "target_type": "player",
                    "target_id": char_id,
                    "target_name": char_state['name'],
                    "distance": distance
                })
        
        return targets
    
    def _check_victory_conditions(self) -> bool:
        """Check if victory conditions are met"""
        victory_conditions = self.combat_data.get("encounter", {}).get("victory_conditions", {})
        victory_type = victory_conditions.get("victory_type", "defeat_all_enemies")
        
        if victory_type == "defeat_all_enemies":
            # Check if all enemies are defeated
            enemy_instances = self.combat_data.get("enemy_instances", [])
            living_enemies = [e for e in enemy_instances if e.get("current_hp", 0) > 0]
            return len(living_enemies) == 0
        
        # TODO: Add other victory condition types
        return False
    
    def _handle_combat_victory(self):
        """Handle combat victory"""
        self.current_phase = CombatPhase.VICTORY
        self._add_to_combat_log("VICTORY!")
        
        # Award rewards
        rewards = self.combat_data.get("encounter", {}).get("rewards", {})
        self._award_rewards(rewards)
        
        # Set quest flags from rewards.story_progress.quest_flags
        story_progress = rewards.get("story_progress", {})
        quest_flags = story_progress.get("quest_flags", {})
        
        for flag, flag_data in quest_flags.items():
            # Support both new format (dict with value + message) and legacy format (bool)
            if isinstance(flag_data, dict):
                flag_value = flag_data.get("value", True)
                display_message = flag_data.get("display_message", flag)
            else:
                # Legacy support: if just a boolean, use that
                flag_value = flag_data
                display_message = flag.replace("_", " ").title()  # Auto-generate from flag name
            
            setattr(self.game_state, flag, flag_value)  # Set flag on game_state
            self._add_to_combat_log(f"Quest Updated: {display_message}")
            print(f"✅ Quest flag set: {flag} = {flag_value}")
        
        # Emit victory event
        self.event_manager.emit("COMBAT_VICTORY", {
            "encounter_id": self.combat_data.get("encounter", {}).get("encounter_id"),
            "rewards": rewards
        })
    
    def _handle_combat_defeat(self):
        """Handle combat defeat"""
        self.current_phase = CombatPhase.DEFEAT
        self._add_to_combat_log("DEFEAT!")
        
        # Handle defeat consequences
        defeat_consequences = self.combat_data.get("defeat_consequences", {})
        if defeat_consequences:
            hp_loss_pct = defeat_consequences.get("hp_loss_percentage", 0)
            if hp_loss_pct > 0:
                max_hp = self.game_state.character.get("hit_points", 10)  
                new_hp = max(1, int(max_hp * (100 - hp_loss_pct) / 100))
                self.game_state.character["current_hp"] = new_hp
        
            # Generate death quote ONCE here

        try:
            quotes_path = os.path.join('data', 'narrative', 'death_quotes.json')
            print(f"🔍 Looking for death quotes at: {quotes_path}")
            print(f"🔍 File exists: {os.path.exists(quotes_path)}")
            
            if os.path.exists(quotes_path):
                with open(quotes_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    quotes = data.get('death_quotes', [])
                    print(f"🔍 Loaded {len(quotes)} quotes from file")
                    
                    if quotes:
                        quote = random.choice(quotes)
                        self.game_state.death_quote = f'"{quote["text"]}" - {quote["author"]}'
                        print(f"✅ Selected quote: {self.game_state.death_quote[:50]}...")
                    else:
                        print("⚠️ No quotes found in JSON")
                        self.game_state.death_quote = '"Even in defeat, honor remains." - Unknown'
            else:
                print(f"❌ Death quotes file not found at: {quotes_path}")
                self.game_state.death_quote = '"The battle is lost, but the war continues." - Unknown'
                
        except Exception as e:
            print(f"❌ Error loading death quotes: {e}")
            import traceback
            traceback.print_exc()
            self.game_state.death_quote = '"The adventure ends here." - Unknown'

        # Show death overlay
        self.game_state.death_overlay_active = True
        print("💀 Death overlay activated")
        
        # Emit defeat event
        self.event_manager.emit("COMBAT_DEFEAT", {
            "encounter_id": self.combat_data.get("encounter", {}).get("encounter_id")
        })

    def cleanup_combat(self):
        """Clear all combat state data"""
        self.combat_data = None
        self.current_phase = CombatPhase.SETUP
        self.turn_order = []
        self.current_actor_index = 0
        self.combat_log = []
        self.current_action_mode = None
        self.player_position = None
        self.player_has_moved = False
        self.player_has_acted = False
        self.player_attacks_used = 0
        print("🧹 Combat state cleared")

    def _handle_death_load_game(self, event_data):
        """Handle Load Game button from death overlay"""
        print("💀 Death action: Opening load screen")
        
        # Set flag to open load screen
        self.game_state.death_overlay_active = False
        self.game_state.load_screen_open = True

    def _handle_death_restart_combat(self, event_data):
        """Handle Restart Combat button - reload autosave and restart combat"""
        print("💀 Death action: Restarting combat from autosave")
        
        # Clear current combat state FIRST
        self.cleanup_combat()
        
        if self.save_manager:
            # Load autosave (slot 0)
            success = self.save_manager.load_game(save_slot=0)
            
            if success:
                # Check for pending combat encounter from autosave
                encounter_id = getattr(self.game_state, 'pending_combat_encounter', None)
                
                if encounter_id:
                    print(f"🔄 Auto-restarting combat: {encounter_id}")
                    # Start combat immediately with fresh state
                    self.start_encounter(encounter_id)
                    self.game_state.screen = 'combat'  # Force to combat screen
                else:
                    print("⚠️ No pending combat encounter - staying at tavern")
                
                self.game_state.death_overlay_active = False
            else:
                print("❌ Failed to load autosave")
                self.game_state.death_overlay_active = False
        else:
            print("⚠️ SaveManager not available")
            self.game_state.death_overlay_active = False

    def _handle_death_return_to_title(self, event_data):
        """Handle Return to Title button"""
        print("💀 Death action: Returning to title screen")
        
        self.game_state.death_overlay_active = False
        self.event_manager.emit("SCREEN_CHANGE", {'target': 'game_title'})

    def _award_rewards(self, rewards: Dict):
        """Award combat rewards to player"""
        # Award XP
        xp = rewards.get("xp", 0)
        if xp > 0:
            current_xp = self.game_state.character.get("experience", 0)
            self.game_state.character["experience"] = current_xp + xp
            self._add_to_combat_log(f"Gained {xp} XP!")
        
        # Award gold
        gold = rewards.get("gold", 0)
        if gold > 0:
            current_gold = self.game_state.character.get("gold", 0)
            self.game_state.character["gold"] = current_gold + gold
            self._add_to_combat_log(f"Found {gold} gold!")
        
        # TODO: Award items from rewards["items"]
    
    def _get_current_actor_name(self) -> str:
        """Get display name of current actor"""
        if self.current_phase == CombatPhase.SETUP:
            return "Setup"
        elif self.current_phase == CombatPhase.PLAYER_TURN:
            return self.game_state.character.get("name", "Player")
        elif self.current_phase == CombatPhase.ENEMY_TURN:
            current_actor = self.turn_order[self.current_actor_index]
            enemy_instances = self.combat_data.get("enemy_instances", [])
            for enemy in enemy_instances:
                if enemy.get("instance_id") == current_actor:
                    return enemy.get("name", "Enemy")
            return "Enemy"
        else:
            return self.current_phase.value.title()
    
    def _get_available_player_actions(self) -> List[str]:
        """Get list of available player actions"""
        actions = []
        
        if self.current_phase == CombatPhase.PLAYER_TURN:
            if not self.player_has_moved:
                actions.append("move")
            if not self.player_has_acted:
                actions.append("attack")
                # TODO: Add spell actions based on character spells
            actions.append("end_turn")
        
        return actions
    
    def _get_highlighted_tiles(self) -> List[List[int]]:
        """Get tiles to highlight in UI based on current action mode"""
        highlighted_tiles = []
        
        #print(f"🎯 Getting highlighted tiles - Phase: {self.current_phase}, Mode: {self.current_action_mode}")

        # Only highlight during player turn
        if self.current_phase != CombatPhase.PLAYER_TURN:
            #print(f"❌ Not player turn, returning empty")
            return highlighted_tiles
        
        if self.current_action_mode == "movement":
            if not self.active_character_id:
                return highlighted_tiles
            
            char_state = self.character_states.get(self.active_character_id)
            if not char_state:
                return highlighted_tiles
            
            movement_range = self._get_movement_range()
            highlighted_tiles = self.get_valid_moves(char_state['position'], movement_range)


        # Attack mode - show valid attack targets
        elif self.current_action_mode == "attack":
            if not self.active_character_id:
                return highlighted_tiles
            
            char_state = self.character_states.get(self.active_character_id)
            if not char_state:
                return highlighted_tiles
            
            attack_range = 1  # Melee range for now
            attack_targets = self.get_attack_targets(char_state['position'], attack_range)

            # Extract just the positions from the target dictionaries
            highlighted_tiles = [target["position"] for target in attack_targets]
            #print(f"   Highlighted tile positions: {highlighted_tiles}")
        
        return highlighted_tiles
    
    def _add_to_combat_log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
        #print(f"🎯 {message}")  # Also print to console for debugging

def initialize_combat_engine(game_state, event_manager, save_manager=None):
    """
    Initialize CombatEngine following established engine pattern
    
    Args:
        game_state: GameState instance
        event_manager: EventManager instance
        
    Returns:
        CombatEngine: Initialized combat engine
    """
    return CombatEngine(event_manager, game_state, save_manager)