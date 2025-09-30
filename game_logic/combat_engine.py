# game_logic/combat_engine.py
"""
Combat Engine - Turn-based tactical combat business logic
Follows existing game_logic pattern for core game systems
"""

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
    
    def __init__(self, event_manager, game_state):
        """Initialize with existing game systems"""
        self.event_manager = event_manager
        self.game_state = game_state
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
        self.player_position = None
        self.player_has_moved = False
        self.player_has_acted = False
        self.player_attacks_used = 0 

        #Register combat events (following SaveManager pattern)
        if event_manager:
            from ui.combat_system import register_combat_system_events
            register_combat_system_events(event_manager, self)
            print("Combat events registered with EventManager")
    
        print("CombatEngine initialized")
    
    def _get_movement_range(self) -> int:
        """Get current actor's movement range from stats"""
        # TODO: Eventually read from game_state.character['movement_range']
        return 3  # Base movement for now

    def start_encounter(self, encounter_id: str, combat_context: Dict = None) -> bool:
        """
        Load encounter data and initialize combat state
        Args:encounter_id: ID of encounter to load
            combat_context: Location-specific context from calling screen
        Returns: bool: True if combat started successfully
        """
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
            
            # Initialize player position
            player_positions = self.combat_data.get("player_positions", [])
            if player_positions:
                self.player_position = player_positions[0]  # Use first position for now
            else:
                print(f"❌ No player starting positions defined")
                return False
            
            # Set up turn order (simple: player first, then enemies)
            self._initialize_turn_order()
            
            # Initialize combat phase
            self.current_phase = CombatPhase.PLAYER_TURN
            self.current_actor_index = 0
            
            # Reset turn flags
            self.player_has_moved = False
            self.player_has_acted = False
            
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
            "player_position": self.player_position,
            "current_actor": current_actor,
            "combat_phase": self.current_phase.value,
            "turn_number": self.combat_data.get("turn_number", 0),
            "combat_log": self.combat_log[-10:],  # Last 10 messages
            "player_actions": self._get_available_player_actions(),
            "player_state": {  # ADD THIS BLOCK
                "has_moved": self.player_has_moved,
                "has_acted": self.player_has_acted,
                "attacks_used": self.player_attacks_used,
                "attacks_per_round": self._get_attacks_per_round(),
                "has_attack_targets": len(self.get_attack_targets(self.player_position, 1)) > 0,
                "current_hp": self.game_state.character.get("current_hp", 10),
                "max_hp": self.game_state.character.get("hit_points", 10)
            },
            "current_action_mode": self.current_action_mode, 
            "highlighted_tiles": self._get_highlighted_tiles()
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
        
        Args:
            actor_position: Attacker's [x, y] position
            attack_range: Attack range in tiles
            
        Returns:
            List of target dictionaries with position and target info
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
        
        # TODO: For enemy attacks, check player position
        
        return targets
    
    def execute_player_move(self, target_position: List[int]) -> bool:
        """ Execute player movement to target position
        Args: target_position: Destination [x, y] position
        Returns:bool: True if move was successful
        """
        if self.current_phase != CombatPhase.PLAYER_TURN:
            self._add_to_combat_log("Not player's turn!")
            return False
        
        if self.player_has_moved:
            self._add_to_combat_log("Already moved this turn!")
            return False
        
        # Validate movement
        movement_range = self._get_movement_range()  # uses helper
        valid_moves = self.get_valid_moves(self.player_position, movement_range)
        
        if target_position not in valid_moves:
            self._add_to_combat_log("Invalid movement target!")
            return False
        
        # Execute movement
        old_pos = self.player_position.copy()
        self.player_position = target_position
        self.player_has_moved = True
        
        # Clear action mode after successful move
        self.current_action_mode = None  

        self._add_to_combat_log(f"Player moves to ({target_position[0]}, {target_position[1]})")
        
        # Emit movement event for UI
        self.event_manager.emit("COMBAT_UNIT_MOVED", {
            "unit_type": "player",
            "old_position": old_pos,
            "new_position": target_position
        })
        
        return True
    
    def execute_player_attack(self, target_position: List[int]) -> bool:
        """
        Execute player attack on target position
        Args: target_position: Target [x, y] position
        Returns:bool: True if attack was executed
        """
        if self.current_phase != CombatPhase.PLAYER_TURN:
            self._add_to_combat_log("Not player's turn!")
            return False
        
         # Check attacks remaining
        attacks_per_round = self._get_attacks_per_round()
        if self.player_attacks_used >= attacks_per_round:
            self._add_to_combat_log("No attacks remaining!")
            return False

        if self.player_has_acted:
            self._add_to_combat_log("Already acted this turn!")
            return False
        
        # Find target at position
        target_enemy = None
        enemy_instances = self.combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            if enemy.get("position") == target_position and enemy.get("current_hp", 0) > 0:
                target_enemy = enemy
                break
        
        if not target_enemy:
            self._add_to_combat_log("No valid target at that position!")
            return False
        
        # Validate range
        attack_targets = self.get_attack_targets(self.player_position)
        valid_target = any(t["position"] == target_position for t in attack_targets)
        
        if not valid_target:
            self._add_to_combat_log("Target out of range!")
            return False
        
        # Execute attack
        success = self._resolve_attack(
            attacker_type="player",
            attacker_data=self.game_state.character,
            target_data=target_enemy
        )
        
        # Increment attack counter regardless of hit/miss
        self.player_attacks_used += 1  # ← MOVE THIS HERE

        # Check if all attacks used
        attacks_per_round = self._get_attacks_per_round()
        if self.player_attacks_used >= attacks_per_round:
            self.player_has_acted = True
            self.current_action_mode = None
            self._add_to_combat_log("All attacks used")

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
    
    def _get_attacks_per_round(self) -> int:
        """Get number of attacks player gets per round"""
        # TODO: Eventually read from character progression/class features
        attacks, _ = self.stats_calculator.calculate_attacks_per_round(self.game_state)
        return attacks

    def end_player_turn(self):
        """End the player's turn and advance to next actor"""
        if self.current_phase != CombatPhase.PLAYER_TURN:
            return
        
        self._add_to_combat_log("Player ends turn")
        
        # Reset turn flags
        self.player_has_moved = False
        self.player_has_acted = False
        
        # Advance to next actor (enemies)
        self._advance_turn()
    
    def _initialize_turn_order(self):
        """Set up turn order for combat"""
        # Simple turn order: Player first, then all enemies
        self.turn_order = ["player"]
        
        enemy_instances = self.combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            if enemy.get("current_hp", 0) > 0:
                self.turn_order.append(enemy.get("instance_id"))
        
        print(f"🎯 Turn order: {self.turn_order}")
    
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
        current_actor = self.turn_order[self.current_actor_index]
        if current_actor == "player":
            self.current_phase = CombatPhase.PLAYER_TURN
            self.player_attacks_used = 0  # Reset attack counter
            self._add_to_combat_log("Player's turn")
        else:
            self.current_phase = CombatPhase.ENEMY_TURN
            self._execute_enemy_turn(current_actor)
    
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
        
        # Check if player is in attack range
        attack_targets = self._get_enemy_attack_targets(enemy_pos)
        if attack_targets:
            # Attack player
            self._add_to_combat_log(f"{enemy_name} attacks!")
            self._resolve_attack(
                attacker_type="enemy",
                attacker_data=enemy,
                target_data=self.game_state.character
            )
        else:
            # Move toward player
            movement_speed = enemy.get("movement", {}).get("speed", 3)
            new_position = self._find_best_move_toward_target(enemy_pos, self.player_position, movement_speed)
            
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
        player_x, player_y = self.player_position
        
        # Check if player is in melee range (distance 1)
        distance = abs(enemy_x - player_x) + abs(enemy_y - player_y)
        if distance <= 1:
            targets.append({
                "position": self.player_position,
                "target_type": "player",
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
        
        # Flag display names for combat log
        flag_display_names = { 
            "completed_basement_combat": "Basement Cleared, go see Garrick",
        }
        
        for flag, value in quest_flags.items():
            setattr(self.game_state, flag, value)  # Direct attribute
            display_name = flag_display_names.get(flag, flag)
            self._add_to_combat_log(f"Quest Updated: {display_name}")
            print(f"✅ Quest flag set: {flag} = {value}")
        
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
        
        # Emit defeat event
        self.event_manager.emit("COMBAT_DEFEAT", {
            "encounter_id": self.combat_data.get("encounter", {}).get("encounter_id")
        })
    
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
            movement_range = self._get_movement_range()  # ← Use helper
            highlighted_tiles = self.get_valid_moves(self.player_position, movement_range)
            # print(f"✅ Movement mode: calculated {len(highlighted_tiles)} valid tiles")
            # print(f"   Player position: {self.player_position}")
            # print(f"   Sample tiles: {highlighted_tiles[:5]}")


        # Attack mode - show valid attack targets
        elif self.current_action_mode == "attack":
            attack_range = 1  # Melee range for now
            attack_targets = self.get_attack_targets(self.player_position, attack_range)
            #print(f"🎯 Attack mode: found {len(attack_targets)} targets")
            #print(f"   Attack targets: {attack_targets}")
            # Extract just the positions from the target dictionaries
            highlighted_tiles = [target["position"] for target in attack_targets]
            #print(f"   Highlighted tile positions: {highlighted_tiles}")
        
        return highlighted_tiles
    
    def _add_to_combat_log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
        #print(f"🎯 {message}")  # Also print to console for debugging

def initialize_combat_engine(game_state, event_manager):
    """
    Initialize CombatEngine following established engine pattern
    
    Args:
        game_state: GameState instance
        event_manager: EventManager instance
        
    Returns:
        CombatEngine: Initialized combat engine
    """
    return CombatEngine(event_manager, game_state)