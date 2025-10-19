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
from game_logic.combat_ai import get_combat_ai
from game_logic.movement_system import get_movement_system
from game_logic.movement_system import MovementSystem

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
    
    def __init__(self, event_manager, game_state, save_manager=None, item_manager=None):
        """Initialize with existing game systems"""
        self.event_manager = event_manager
        self.game_state = game_state
        self.save_manager = save_manager
        self.combat_loader = get_combat_loader()
        self.stats_calculator = get_stats_calculator()
        self.combat_ai = get_combat_ai()
        self.spell_data = self._load_spell_data()
        
        # Initialize movement system
        self.movement_system = get_movement_system(self)
        self.movement_system = MovementSystem(self)
        print("✅ Movement system initialized")

        # Current combat state
        self.combat_data = None
        self.current_phase = CombatPhase.SETUP
        self.turn_order = []
        self.current_actor_index = 0
        self.combat_log = []
        self.current_action_mode = None  # Track current UI interaction mode
        self.item_manager = item_manager
        self.defeated_enemies_loot_data = []
        self.character_states = {}  # Dict of character_id -> state
        self.active_character_id = None  # Currently acting character
        self.inspected_unit = None  # Unit currently being inspected by player

        #Register combat events (following SaveManager pattern)
        if event_manager:
            from ui.combat_system import register_combat_system_events
            register_combat_system_events(event_manager, self)

            event_manager.register("DEATH_ACTION_LOAD_GAME", self._handle_death_load_game)
            event_manager.register("DEATH_ACTION_RESTART_COMBAT", self._handle_death_restart_combat)
            event_manager.register("DEATH_ACTION_RETURN_TO_TITLE", self._handle_death_return_to_title)
            print("💀 Death overlay events registered in CombatEngine")
        
        print("CombatEngine initialized")
    
    def _reset_action_mode_for_active(self):
        """Safe default when a new actor becomes active."""
        # pick your default; movement is usually nicest for UX
        self.current_action_mode = "movement"
        # Start idle; buttons set an explicit mode
        self.current_action_mode = None

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
                
                # Initialize spell slots from character data
                spell_slots_max = self._get_max_spell_slots(member)
                spells_known = self._get_character_spells(member)
                
                self.character_states[character_id] = {
                    'id': character_id, 
                    'name': member['name'],
                    'position': position,
                    'has_moved': False,
                    'attacks_used': 0,
                    'is_alive': True,
                    'dexterity': member.get('stats', {}).get('dexterity', 10),
                    'character_data': member,  # Store full character data
                    'spell_slots_max': spell_slots_max,
                    'spell_slots_remaining': spell_slots_max,
                    'spells_known': spells_known,
                    'spells_cast_this_turn': 0
                }
            
            print(f"✅ Initialized {len(party_members)} party members")
            
            # DEBUG: Print spell data for all characters
            for char_id, char_state in self.character_states.items():
                print(f"🔮 {char_state.get('name')}: spell_slots={char_state.get('spell_slots_max')}/{char_state.get('spell_slots_remaining')}, spells_known={char_state.get('spells_known')}")


            # Set up turn order (simple: player first, then enemies)
            self._initialize_turn_order()
            
            # Initialize combat phase
            self.current_phase = CombatPhase.PLAYER_TURN
            self.current_actor_index = 0
            
           # Set the first active character and add initiative message
            if self.turn_order:
                first_actor_id = self.turn_order[0]
                
                # If first actor is a player character, set as active
                if first_actor_id in self.character_states:
                    self.active_character_id = first_actor_id
                    self._reset_action_mode_for_active() 
                    char_state = self.character_states[first_actor_id]
                    char_state['has_moved'] = False
                    char_state['attacks_used'] = 0
                    char_name = char_state['name']
                    print(f"🎯 First turn: {char_name}")
                    self._add_to_combat_log(f"{char_name} has initiative!")
                # If first actor is an enemy, execute their turn immediately
                else:
                    # Find enemy name
                    enemy_name = "Enemy"
                    enemy_instances = self.combat_data.get("enemy_instances", [])
                    for enemy in enemy_instances:
                        if enemy.get("instance_id") == first_actor_id:
                            enemy_name = enemy.get("name", "Enemy")
                            break
                    
                    print(f"🎯 First turn: {enemy_name}")
                    self._add_to_combat_log(f"{enemy_name} has initiative and attacks first!")
                    self.current_phase = CombatPhase.ENEMY_TURN
                    self._execute_enemy_turn(first_actor_id)
                    # Enemy turn will handle advancing via _advance_turn() internally
            
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

    def validate_movement(self, entity, target_x, target_y):
        return self.movement_system.validate_move(entity, target_x, target_y)

    def _load_spell_data(self) -> dict:
        """Load spell definitions from JSON"""
        try:
            spell_file = os.path.join('data', 'spells.json')
            with open(spell_file, 'r') as f:
                spells = json.load(f)
            print(f"✨ Loaded {len(spells)} spell definitions")
            return spells
        except FileNotFoundError:
            print("⚠️ spells.json not found - spell system disabled")
            return {}
        except Exception as e:
            print(f"❌ Error loading spells: {e}")
            return {}    
        
    def move_entity(self, entity, target_x, target_y):
        return self.movement_system.move_entity(entity, target_x, target_y)
    
    def _execute_enemy_move(self, enemy: Dict, target_position: List[int]) -> bool:
        """
        Execute enemy movement to target position with animation
        
        Args:
            enemy: Enemy instance dict
            target_position: [x, y] position to move to
            
        Returns:
            bool: True if move was successful
        """
        enemy_pos = enemy.get("position", [0, 0])
        enemy_name = enemy.get("name", "Enemy")
        movement_range = enemy.get("movement", {}).get("speed", 3)
        enemy_id = enemy.get("instance_id", "")
        
        # Check for incorporeal ability
        can_phase = enemy.get("movement", {}).get("movement_type") == "incorporeal"
        print(f"DEBUG: Enemy move - {enemy_name} ({enemy_id}) from {enemy_pos} to {target_position}, can_phase={can_phase}")

        # OCCUPATION CHECK: Prevent ending turn on occupied tiles
        # Check if target is occupied by ANYONE (players or other enemies)
        target_x, target_y = target_position
        
        # Check for players at target
        for char_id, char_state in self.character_states.items():
            if char_state.get('is_alive', True) and char_state.get('position') == target_position:
                print(f"   ⚠️ BLOCKED: {enemy_name} cannot move to {target_position} - player there")
                self._add_to_combat_log(f"{enemy_name} cannot reach desired position - tile occupied")
                return False
        
        # Check for other enemies at target (don't check self)
        enemy_instances = self.combat_data.get("enemy_instances", [])
        for other_enemy in enemy_instances:
            if other_enemy.get("current_hp", 0) <= 0:
                continue
            
            other_id = other_enemy.get("instance_id")
            if other_id == enemy_id:
                continue  # Don't block ourselves
            
            # Check both current position and intended position
            if other_enemy.get("position") == target_position or other_enemy.get("intended_position") == target_position:
                print(f"   ⚠️ BLOCKED: {enemy_name} cannot move to {target_position} - another enemy there")
                self._add_to_combat_log(f"{enemy_name} cannot reach desired position - tile occupied")
                return False

        # PATHFINDING: Different strategies for incorporeal vs regular enemies
        if can_phase:
            # Incorporeal: Create direct path (can phase through obstacles)
            path = [enemy_pos]  # Start with current position
            
            # Calculate step directions
            dx = 1 if target_position[0] > enemy_pos[0] else -1 if target_position[0] < enemy_pos[0] else 0
            dy = 1 if target_position[1] > enemy_pos[1] else -1 if target_position[1] < enemy_pos[1] else 0
            
            # Generate path step-by-step
            current = enemy_pos.copy()
            while current != target_position:
                # Move diagonally when possible (faster visual)
                if current[0] != target_position[0] and current[1] != target_position[1]:
                    current[0] += dx
                    current[1] += dy
                # Otherwise move in required direction
                elif current[0] != target_position[0]:
                    current[0] += dx
                elif current[1] != target_position[1]:
                    current[1] += dy
                
                # Add waypoint
                path.append(current.copy())
        else:
            # Regular enemies: Use standard pathfinding (respects obstacles)
            path = self.movement_system.find_path(
                enemy_pos, 
                target_position, 
                can_phase
            )
        
        print(f"DEBUG: Path for {enemy_name}: {path}")
        
        # Validate path exists and is within movement range
        if not path or len(path) - 1 > movement_range:
            self._add_to_combat_log(f"{enemy_name} cannot reach desired position")
            return False
        
        # Start movement animation
        success = self.movement_system.start_entity_movement(
            enemy_id,
            enemy_pos,
            path
        )
        
        if success:
            # Update intended position (actual position updated by movement system during animation)
            enemy["intended_position"] = target_position
            
            # Log movement
            self._add_to_combat_log(f"{enemy_name} moves toward {target_position}")
            
            # Emit movement event for UI
            self.event_manager.emit("COMBAT_UNIT_MOVED", {
                "unit_type": "enemy",
                "old_position": enemy_pos,
                "new_position": target_position,
                "animated": True
            })
            
            return True
        
        return False

    def execute_enemy_turn(self, enemy_id: str):
        """Public method that redirects to the internal _execute_enemy_turn method"""
        return self._execute_enemy_turn(enemy_id)

    def _execute_enemy_turn(self, enemy_id: str):
        """Execute AI turn for enemy using CombatAI decision system"""
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
        
        # Calculate valid moves for this enemy using MovementSystem
        can_phase = enemy.get("movement", {}).get("movement_type") == "incorporeal"
        movement_range = self.movement_system.get_movement_range(enemy)
        valid_moves = self.movement_system.get_valid_moves(
            enemy.get("position", [0, 0]), 
            movement_range, 
            can_phase, 
            is_player=False
        )

        # AI plans ENTIRE turn (move + attack) in ONE call
        combat_state = {
            'character_states': self.character_states,
            'enemy_instances': enemy_instances,
            'battlefield': self.combat_data.get("battlefield", {}),
            'valid_moves': valid_moves,
            'movement_system': self.movement_system,
            'combat_engine': self
        }
        
        # Get complete turn plan from AI
        turn_plan = self.combat_ai.calculate_enemy_turn(enemy, combat_state)

        print(f"\n⚙️ EXECUTING TURN: {enemy_name}")
        
        # Execute movement (if planned)
        if turn_plan.get('move'):
            print(f"   🚶 Executing move to {turn_plan['move']}")
            self._execute_enemy_move(enemy, turn_plan['move'])
        
        # Execute attack (if planned)
        if turn_plan.get('attack'):
            attack_data = turn_plan['attack']
            self._execute_enemy_attack(
                enemy,
                attack_data['target_id'],
                attack_data.get('attack_index', 0)
            )
        
        # Log if no actions taken
        if not turn_plan.get('move') and not turn_plan.get('attack'):
            reason = turn_plan.get('reason', 'no action')
            self._add_to_combat_log(f"{enemy_name} waits ({reason})")
            print(f"   ⏸️ No actions taken: {reason}")
        
        # Advance to next turn
        self._advance_turn()

    def _execute_enemy_attack(self, enemy: Dict, target_char_id: str, attack_index: int = 0) -> bool:
        """
        Execute enemy attack on target character
        
        Args:
            enemy: Enemy instance dict
            target_char_id: Character ID to attack
            attack_index: Which attack from attacks array to use (default 0)
            
        Returns:
            bool: True if attack hit
        """
        enemy_name = enemy.get("name", "Enemy")
        target_char_state = self.character_states.get(target_char_id)
        
        if not target_char_state:
            self._add_to_combat_log(f"{enemy_name} attack failed - no target")
            return False
        
        target_name = target_char_state.get('name', 'Player')
        
        # Get the specific attack
        attacks = enemy.get("attacks", [])
        if not attacks or attack_index >= len(attacks):
            self._add_to_combat_log(f"{enemy_name} has no valid attack!")
            return False
        
        selected_attack = attacks[attack_index]
        attack_name = selected_attack.get("name", "Attack")
        attack_type = selected_attack.get("attack_type", "melee")
        
        self._add_to_combat_log(f"{enemy_name} attacks {target_name} with {attack_name}!")
        
        # For ranged attacks, check line of sight
        if attack_type == "ranged":
            enemy_pos = enemy.get("position", [0, 0])
            target_pos = target_char_state.get('position', [0, 0])
            
            if not self._has_line_of_sight(enemy_pos[0], enemy_pos[1], target_pos[0], target_pos[1]):
                self._add_to_combat_log("No line of sight!")
                return False
        
        # Resolve using the specific weapon attack
        success = self._resolve_attack_with_weapon(
            attacker_type="enemy",
            attacker_data=enemy,
            target_data=target_char_state['character_data'],
            weapon_attack=selected_attack
        )
        
        if success:
            # Check if character was defeated
            if not target_char_state.get('is_alive', True):
                self._add_to_combat_log(f"{target_name} has fallen!")
                
                # Check defeat conditions
                if self._check_victory_conditions():
                    self._handle_combat_defeat()
        
        return success
    
    def _has_ranged_weapon_equipped(self, char_state: Dict) -> bool:
        """Check if character has ranged weapon equipped by checking item data"""
        char_data = char_state.get('character_data', {})
        #print(f"🔍 DEBUG char_data keys: {char_data.keys()}")
        #print(f"🔍 DEBUG char_data: {char_data}")  
        
        equipment = char_data.get('equipment', {})
        #print(f"🔍 DEBUG equipment: {equipment}")
        
        weapon_id = equipment.get('weapon', '')
        
        #print(f"🏹 DEBUG: Checking ranged weapon for {char_state.get('id', 'unknown')}")
        #print(f"   Weapon ID: {weapon_id}")

        if not weapon_id:
            print(f"   ❌ No weapon equipped")
            return False
        
        # For player character, check item manager
        char_id = char_state.get('id')
        if char_id == 'player' and hasattr(self, 'item_manager'):
            weapon_data = self.item_manager.get_item_by_id(weapon_id.lower())
            if weapon_data:
                combat_stats = weapon_data.get('combat_stats', {})
                #is_ranged = combat_stats.get('range') == 'ranged'
                #print(f"   Player weapon data found: range={combat_stats.get('range')}, is_ranged={is_ranged}")
                # Check the range field from JSON
                return combat_stats.get('range') == 'ranged'
        
        # For NPCs, also check item data if available
        if hasattr(self, 'item_manager'):
            weapon_data = self.item_manager.get_item_by_id(weapon_id.lower())
            if weapon_data:
                combat_stats = weapon_data.get('combat_stats', {})
                is_ranged = combat_stats.get('range') == 'ranged'
                #print(f"   NPC weapon data found: range={combat_stats.get('range')}, is_ranged={is_ranged}")
                return combat_stats.get('range') == 'ranged'
            else:
                print(f"   ❌ Weapon '{weapon_id}' not found in item_manager")
        
        # Fallback: if no item manager, assume not ranged
        print(f"   ❌ No item_manager available")
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
            'max_hp': self.game_state.character.get('hit_points', 20),
            'equipment': {
                'weapon': self.game_state.character.get('equipped_weapon'),
                'armor': self.game_state.character.get('equipped_armor'),
                'shield': self.game_state.character.get('equipped_shield')
        }
    }

        party.append(player_char)
        
        # Add recruited party members
        for member_data in self.game_state.party_member_data:
            # Read HP from member data (initialized in game_state)
            max_hp = member_data.get('hp', member_data.get('hit_points', 20))
            current_hp = member_data.get('current_hp', max_hp)
            
            party_member = {
                'id': member_data['id'],
                'name': member_data['name'],
                'class': member_data['class'],
                'level': member_data['level'],
                'stats': member_data.get('stats', {}),
                'equipment': member_data.get('equipment', {}),  
                'current_hp': current_hp,
                'max_hp': max_hp,
                'ac': member_data.get('ac', 10),  
                'spells': member_data.get('spells', {})  
            }
            party.append(party_member)
        
        return party
    
    def get_unit_at_position(self, grid_pos: List[int]) -> Optional[Dict]:
        """
        Get unit data at specified grid position for inspection
        Returns dict with name, type (enemy/ally), current_hp, max_hp
        Returns None if no unit at position
        """
        if not self.combat_data:
            return None
        
        x, y = grid_pos
        
        # Check party members first
        for char_id, char_state in self.character_states.items():
            if not char_state.get('is_alive', True):
                continue
                
            pos = char_state.get('position', [])
            if pos == [x, y]:
                # Found a party member
                char_data = char_state.get('character_data', {})
                
                # Get HP from correct source
                if char_id == 'player':
                    current_hp = self.game_state.character.get('current_hp', 10)
                    max_hp = self.game_state.character.get('hit_points', 10)
                else:
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('max_hp', 10)
                
                return {
                    'name': char_state.get('name', 'Unknown'),
                    'type': 'ally',
                    'current_hp': current_hp,
                    'max_hp': max_hp,
                    'char_id': char_id
                }
        
        # Check enemies
        enemy_instances = self.combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            pos = enemy.get("position", [])
            if pos == [x, y]:
                # Found an enemy
                stats = enemy.get('stats', {})
                return {
                    'name': enemy.get('name', 'Enemy'),
                    'type': 'enemy',
                    'current_hp': enemy.get('current_hp', 0),
                    'max_hp': stats.get('hp', 1),
                    'instance_id': enemy.get('instance_id', 'unknown')
                }
        
        # No unit at this position
        return None

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
        
        # 1) Build the payload
        data = {
            "combat_active": True,
            "encounter": self.combat_data.get("encounter", {}),
            "battlefield": self.combat_data.get("battlefield", {}),
            "enemy_instances": self.combat_data.get("enemy_instances", []),
            "character_states": self.character_states,
            "active_character_id": self.active_character_id,
            "current_actor": current_actor,
            "combat_phase": self.current_phase.value,
            "turn_number": self.combat_data.get("turn_number", 0),
            "combat_log": self.combat_log[-20:],  # Last 20 messages
            "player_actions": self._get_available_player_actions(),
            "player_state": self._get_active_character_state(),
            "current_action_mode": self.current_action_mode, 
            "highlighted_tiles": self._get_highlighted_tiles()
        }

        # 2) Add cover-aware targets only for ranged mode (opt-in)
        try:
            if self.current_phase == CombatPhase.PLAYER_TURN and self.current_action_mode == "ranged_attack":
                char_state = self.character_states.get(self.active_character_id)
                if char_state:
                    # Reuse your weapon-range logic (same as in _get_highlighted_tiles)
                    weapon_range = 8
                    weapon_id = (char_state.get('character_data', {})
                                            .get('equipment', {})
                                            .get('weapon'))
                    if isinstance(weapon_id, str) and hasattr(self, 'item_manager'):
                        wd = self.item_manager.get_item_by_id(weapon_id.lower())
                        if wd:
                            weapon_range = (wd.get('combat_stats', {}) or {}).get('range_grid', weapon_range)

                    targets = self.get_attack_targets(
                        actor_position=char_state['position'],
                        attack_range=weapon_range,
                        requires_los=True,
                        include_cover=True,              # ← NEW param (see part B)
                    )
                    data["highlighted_targets"] = targets  # each has {"position", ..., "cover"}
        except Exception as e:
            # Keep UI resilient; fall back to classic highlights if anything hiccups
            print(f"[get_combat_data_for_ui] cover enrich failed: {e}")

        return data

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
        melee_targets = self.get_attack_targets(char_position, 1, requires_los=False)
        ranged_targets = self.get_attack_targets(char_position, 8, requires_los=True)   
        
        has_ranged_weapon = self._has_ranged_weapon_equipped(char_state)
        #print(f"🎯 DEBUG player_state for {char_state.get('name', 'unknown')}:")
        #print(f"   has_ranged_weapon: {has_ranged_weapon}")
        #print(f"   ranged_targets: {len(ranged_targets)}")
        #print(f"   attacks_used: {char_state.get('attacks_used', 0)}")

        return {
            "has_moved": char_state.get('has_moved', False),
            "has_acted": char_state.get('has_acted', False),
            "attacks_used": char_state.get('attacks_used', 0),
            "attacks_per_round": self._get_attacks_per_round(char_data),
            "has_attack_targets": len(melee_targets) > 0,
            "has_ranged_weapon": self._has_ranged_weapon_equipped(char_state),
            "has_ranged_targets": len(ranged_targets) > 0,
            "current_hp": char_data.get('current_hp', 10),
            "max_hp": char_data.get('max_hp', 10)
        }

    def set_action_mode(self, mode: str):
        """Set the current action mode and calculate valid actions"""
        
        # 🔥 CHECK SPELL LIMIT BEFORE ENTERING SPELL MODE!
        if mode == "spell":
            if not self.active_character_id:
                print("❌ No active character for spell mode")
                return
            
            char_state = self.character_states.get(self.active_character_id)
            if not char_state:
                print("❌ Character state not found")
                return
            
            # Check if already cast a spell this turn
            spells_cast = char_state.get('spells_cast_this_turn', 0)
            if spells_cast >= 1:
                self._add_to_combat_log("Already cast a spell this turn!")
                print("❌ Cannot enter spell mode - already cast this turn")
                return  # Don't enter spell mode!
            
            # Check if has spell slots
            spell_slots = char_state.get('spell_slots_remaining', 0)
            if spell_slots <= 0:
                self._add_to_combat_log("No spell slots remaining!")
                print("❌ Cannot enter spell mode - no spell slots")
                return  # Don't enter spell mode!
        
        print(f"Action mode set to: {mode}")
        self.current_action_mode = mode
        
        # Clear any existing highlighted tiles
        self.combat_data["highlighted_tiles"] = []
        
        # Calculate valid action tiles based on mode
        if mode == "movement":
            # Get active character
            if not self.active_character_id:
                return
                
            char_state = self.character_states.get(self.active_character_id)
            if not char_state:
                return
                
            position = char_state.get('position')
            if not position:
                return
            
            # Check if character can phase through obstacles
            can_phase = False
            for ability in char_state.get('abilities', []):
                if ability.get('id') == 'incorporeal':
                    can_phase = True
                    break
            
            # Get movement range
            movement_range = self.movement_system.get_movement_range(char_state) if char_state else 5
            
            # Calculate valid moves
            is_player = True  # Player characters can move through allies
            
            # Use movement system
            valid_moves = self.movement_system.get_valid_moves(
                position, movement_range, can_phase, is_player
            )
                
            print(f"Calculated {len(valid_moves)} valid movement tiles")
            
            # Store in combat data for rendering
            self.combat_data["highlighted_tiles"] = valid_moves
        
        elif mode == "attack":
            # Your existing attack highlighting code
            if self.active_character_id:
                char_state = self.character_states.get(self.active_character_id)
                if char_state:
                    char_position = char_state['position']
                    attack_targets = self.get_attack_targets(char_position, attack_range=1, requires_los=False)
                    
                    # Extract just the positions for highlighting
                    target_positions = [t["position"] for t in attack_targets]
                    self.combat_data["highlighted_tiles"] = target_positions
                    print(f"Calculated {len(target_positions)} valid attack targets")
            
        elif mode == "ranged_attack":
            # Your existing ranged attack highlighting code
            if self.active_character_id:
                char_state = self.character_states.get(self.active_character_id)
                if char_state:
                    char_position = char_state['position']
                    
                    # Check if character has a ranged weapon
                    if not self._has_ranged_weapon_equipped(char_state):
                        print("❌ No ranged weapon equipped")
                        self.current_action_mode = None
                        return
                    
                    # Get ranged attack targets with LOS and cover info
                    ranged_targets = self.get_attack_targets(
                        char_position, 
                        attack_range=8, 
                        requires_los=True,
                        include_cover=True
                    )
                    
                    # Store targets with cover data for UI
                    self.combat_data["highlighted_targets"] = ranged_targets
                    
                    # Also store positions for backward compatibility
                    target_positions = [t["position"] for t in ranged_targets]
                    self.combat_data["highlighted_tiles"] = target_positions
                    
                    print(f"Calculated {len(target_positions)} valid ranged targets")
        
        elif mode == "spell":
            # Spell mode - just entered, waiting for spell selection
            print("🪄 Entered spell casting mode")

        elif mode == "spell_targeting":
            # Player selected a spell, now show valid targets
            print("🎯 Entered spell targeting mode")
            
            if not hasattr(self, 'selected_spell_id'):
                print("❌ No spell selected!")
                return
            
            # Get the selected spell data
            spell_data = self.spell_data.get(self.selected_spell_id)
            if not spell_data:
                print(f"❌ Spell not found: {self.selected_spell_id}")
                return
            
            # Get valid targets based on spell range and type
            valid_targets = self._get_spell_targets(self.selected_spell_id)
            self.combat_data["highlighted_tiles"] = valid_targets
            
            print(f"✨ Targeting {spell_data['name']} - {len(valid_targets)} valid targets")
            self._add_to_combat_log(f"Select target for {spell_data['name']}")


    def _can_use_ranged_attack(self) -> bool:
        """Check if active character can use ranged attacks"""
        if not self.active_character_id:
            return False
        
        char_state = self.character_states.get(self.active_character_id)
        if not char_state:
            return False
        
        # Check attacks remaining
        if char_state.get('attacks_used', 0) >= self._get_attacks_per_round(char_state.get('character_data')):
            self._add_to_combat_log("All attacks used this turn!")
            return False
        
        # Use the proper ranged weapon check that validates against items.json
        if not self._has_ranged_weapon_equipped(char_state):
            char_name = char_state.get('name', 'Character')
            self._add_to_combat_log(f"{char_name} has no ranged weapon equipped!")
            return False
        
        # Check for valid targets
        char_pos = char_state['position']
        ranged_targets = self.get_attack_targets(char_pos, 8, requires_los=True)
        
        if not ranged_targets:
            self._add_to_combat_log("No valid ranged targets!")
            return False
        
        return True

    def get_attack_targets(self, actor_position: List[int], attack_range: int = 1,
                       requires_los: bool = False, include_cover: bool = False) -> List[Dict]:
        """
        Find valid attack targets within range.
        If include_cover=True, attach 'cover' to each target and suppress full cover when LOS is required.
        """
        targets = []
        start_x, start_y = actor_position

        if self.current_phase == CombatPhase.PLAYER_TURN:
            enemy_instances = self.combat_data.get("enemy_instances", [])
            pool = [
                e for e in enemy_instances
                if e.get("current_hp", 0) > 0
            ]
            for enemy in pool:
                pos_t = enemy.get("position", [0, 0])
                ex, ey = pos_t
                dist = abs(start_x - ex) + abs(start_y - ey)
                if 0 < dist <= attack_range:
                    if requires_los:
                        # coarse LOS first (fast)
                        has_los = self._has_line_of_sight(start_x, start_y, ex, ey)
                        if not has_los:
                            continue
                    cover_level = "none"
                    if include_cover:
                        cover_info = self._compute_cover([start_x, start_y], pos_t)
                        cover_level = cover_info["level"]
                        if requires_los and cover_level == "full":
                            # fully blocked rays → not targetable
                            continue
                    elif requires_los:
                        # when not computing cover but LOS is required, keep the basic LOS decision already made
                        pass

                    # melee (requires_los=False) already constrained by dist==1 in your call site
                    targets.append({
                        "position": pos_t,
                        "target_type": "enemy",
                        "target_id": enemy.get("instance_id"),
                        "target_name": enemy.get("name", "Enemy"),
                        "distance": dist,
                        "cover": cover_level
                    })
        else:
            # Enemy turn: scan party members
            for char_id, char_state in self.character_states.items():
                if not char_state.get('is_alive', True):
                    continue
                pos_t = char_state['position']
                tx, ty = pos_t
                dist = abs(start_x - tx) + abs(start_y - ty)
                if 0 < dist <= attack_range:
                    if requires_los:
                        if not self._has_line_of_sight(start_x, start_y, tx, ty):
                            continue
                    cover_level = "none"
                    if include_cover:
                        cover_info = self._compute_cover([start_x, start_y], pos_t)
                        cover_level = cover_info["level"]
                        if requires_los and cover_level == "full":
                            continue
                    targets.append({
                        "position": pos_t,
                        "target_type": "player",
                        "target_id": char_id,
                        "target_name": char_state['name'],
                        "distance": dist,
                        "cover": cover_level
                    })
        return targets

    def _has_line_of_sight(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Check if there's a clear line of sight between two positions
        Uses Bresenham's line algorithm
        
        Args:
            x1, y1: Starting position
            x2, y2: Ending position
            
        Returns:
            bool: True if line of sight exists
        """
        # Use Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        x, y = x1, y1
        
        x_inc = 1 if x2 > x1 else -1
        y_inc = 1 if y2 > y1 else -1
        
        if dx > dy:
            # More horizontal than vertical
            error = dx / 2
            while x != x2:
                x += x_inc
                error -= dy
                if error < 0:
                    y += y_inc
                    error += dx
                
                # Don't check the final destination square
                if x == x2 and y == y2:
                    break
                    
                # Check for blocking terrain or characters
                if self._is_tile_blocked_for_los(x, y):
                    return False
        else:
            # More vertical than horizontal
            error = dy / 2
            while y != y2:
                y += y_inc
                error -= dx
                if error < 0:
                    x += x_inc
                    error += dy
                
                # Don't check the final destination square
                if x == x2 and y == y2:
                    break
                    
                # Check for blocking terrain or characters
                if self._is_tile_blocked_for_los(x, y):
                    return False
        
        return True

    def _tile_center_f(self, p: list[int]) -> tuple[float, float]:
        return (p[0] + 0.5, p[1] + 0.5)

    def _line_cells_supercover_f(self, a: tuple[float, float], b: tuple[float, float]) -> list[list[int]]:
        """
        Float supercover Bresenham: returns all grid cells a→b touches (inclusive), mapped to int [x,y].
        """
        x0, y0 = a
        x1, y1 = b
        xi0, yi0 = int(x0), int(y0)
        xi1, yi1 = int(x1), int(y1)   

        cells: list[list[int]] = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0

        # generous cap to prevent runaway; worst case is width+height steps
        step_cap = 2 + abs(xi1 - xi0) + abs(yi1 - yi0)
        for _ in range(step_cap):
            ci, cj = int(x), int(y)
            if not cells or cells[-1] != [ci, cj]:
                cells.append([ci, cj])
            if ci == xi1 and cj == yi1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        return cells

    def _is_cover_blocker(self, gx: int, gy: int) -> bool:
        """
        Treat only walls/columns as cover. Ignore creatures and floor.
        If your map has a tile property or layer name for pillars, use that here.
        Fallback: keep using your LOS blocker but subtract unit cells.
        """
        # Example if you have a tile-layer lookup (preferred):
        if hasattr(self, "_is_world_tile_solid"):
            return self._is_world_tile_solid(gx, gy)  # walls/columns only

        # Fallback: LOS blocker minus units
        if self._is_tile_blocked_for_los(gx, gy):
            # Check if any character/enemy occupies this cell; if so, don't count as cover
            for st in self.character_states.values():
                if st.get("position") == [gx, gy]:
                    return False
            for e in self.combat_data.get("enemy_instances", []):
                if e.get("position") == [gx, gy] and e.get("current_hp", 0) > 0:
                    return False
            return True
        return False

    def _compute_cover(self, origin: list[int], target: list[int], *, creatures_grant_cover: bool = False) -> dict:
        """
        Return {'level': 'none'|'half'|'three_quarters'|'full', 'blocked_rays': int}
        Uses true sub-tile rays: center + 4 corners of the *target tile*.
        """
        # 0) Adjacent targets never get cover (clean, obvious UX)
        if abs(origin[0] - target[0]) + abs(origin[1] - target[1]) <= 1:
            return {"level": "none", "blocked_rays": 0}
        
        # 1) Shooter/target points in float tile space
        sx, sy = origin[0] + 0.5, origin[1] + 0.5
        cx, cy = target[0], target[1]

        # Nudge corners inward so we don't skim exact tile borders
        eps = 0.20       # adjust to 0.2 if still get false half-cover or lower if miss legit cover
        samples = [
            (cx + 0.5, cy + 0.5),             # center
            (cx + eps, cy + eps),             # TL
            (cx + 1 - eps, cy + eps),         # TR
            (cx + eps, cy + 1 - eps),         # BL
            (cx + 1 - eps, cy + 1 - eps),     # BR
        ]

        def ray_kind(to_pt) -> str:
            cells = self._line_cells_supercover_f((sx, sy), to_pt)
            # ignore origin & final target tile
            for i in range(1, len(cells) - 1):
                gx, gy = cells[i]

                # Corner-touch tolerance: skip a lone diagonal graze
                px, py = cells[i - 1]; nx, ny = cells[i + 1]
                if (abs(px - gx) == 1 and abs(py - gy) == 1 and
                    abs(nx - gx) == 1 and abs(ny - gy) == 1):
                    continue

                # Classify blocker type
                if self._is_terrain_blocker(gx, gy):
                    return "terrain"                   # hard blocker
                soft = self._tile_soft_cover(gx, gy)
                if soft:
                    return "soft_" + soft              # 'soft_half' / 'soft_three_quarters' / 'soft_full'
                if creatures_grant_cover and self._cell_has_creature(gx, gy):
                    return "creature"                  # creature grants cover (not hard LOS)
            return "clear"

        terrain_hits = 0
        soft_half_hits = 0
        soft_3q_hits = 0
        creature_hits = 0

        for pt in samples:
            k = ray_kind(pt)
            if k == "terrain":
                terrain_hits += 1
            elif k == "soft_half":
                soft_half_hits += 1
            elif k == "soft_three_quarters":
                soft_3q_hits += 1
            elif k == "creature":
                creature_hits += 1

        # Decide cover tier
        # Hard terrain decides the top tiers.
        if terrain_hits >= 5:
            level = "full"
        elif terrain_hits >= 3:
            level = "three_quarters"
        elif terrain_hits >= 1:
            level = "half"
        else:
            # No hard terrain rays → aggregate soft & creatures
            if soft_3q_hits >= 2:
                level = "three_quarters"
            elif soft_3q_hits >= 1 or soft_half_hits >= 1 or creature_hits >= 1:
                level = "half"
            else:
                level = "none"

        # Optional debug:
        # print(f"[COVER] shooter={origin} target={target} terr={terrain_hits} soft½={soft_half_hits} soft¾={soft_3q_hits} cre={creature_hits} -> {level}")

        return {
            "level": level,
            "blocked_rays": terrain_hits + soft_half_hits + soft_3q_hits + creature_hits,
            "terrain_rays": terrain_hits,
            "soft_half_rays": soft_half_hits,
            "soft_three_quarters_rays": soft_3q_hits,
            "creature_rays": creature_hits,
        }
    
    def _get_cover_ac_bonus(self, cover_level: str) -> int:
        """
        Convert cover level to AC bonus (D&D 5E rules)
        
        Args:
            cover_level: 'none', 'half', 'three_quarters', or 'full'
            
        Returns:
            int: AC bonus from cover
        """
        cover_bonuses = {
            'none': 0,
            'half': 2,
            'three_quarters': 5,
            'full': 99  # Effectively untargetable
        }
        return cover_bonuses.get(cover_level, 0)

    def _is_obstacle(self, cell):
        x, y = cell
        return self._is_tile_blocked_for_los(x, y)

    def _get_obstacle_at(self, x: int, y: int) -> dict | None:
        bf = self.combat_data.get("battlefield", {})
        terrain = bf.get("terrain", {})
        for ob in terrain.get("obstacles", []):
            if ob.get("position") == [x, y]:
                return ob
        return None

    def _is_terrain_blocker(self, x: int, y: int) -> bool:
        """Hard LOS blocker: only things with blocks_sight=True (and walls, if you have them)."""
        ob = self._get_obstacle_at(x, y)
        if ob and ob.get("blocks_sight", False):
            return True
        # If your LOS also considers outer walls, keep your existing wall check here:
        # return self._is_tile_blocked_for_los(x, y)
        return False

    def _tile_soft_cover(self, x: int, y: int) -> str | None:
        """Soft terrain cover (doesn't block LOS): 'half' | 'three_quarters' | 'full' or None."""
        ob = self._get_obstacle_at(x, y)
        if not ob:
            return None
        
        # Support both string-based "provides_cover" and integer "cover_value"
        tag = ob.get("provides_cover")
        if tag in ("half", "three_quarters", "full"):
            return tag
        
        # Convert cover_value integer to cover string
        cover_value = ob.get("cover_value", 0)
        if cover_value == 1:
            return "half"
        elif cover_value == 2:
            return "three_quarters"
        elif cover_value >= 3:
            return "full"
        
        return None

    def _cell_has_creature(self, x: int, y: int) -> bool:
        for st in self.character_states.values():
            if st.get('is_alive', True) and st.get('position') == [x, y]:
                return True
        for e in self.combat_data.get("enemy_instances", []):
            if e.get("current_hp", 0) > 0 and e.get("position") == [x, y]:
                return True
        return False

    def _is_tile_blocked_for_los(self, x: int, y: int) -> bool:
        """Hard LOS blocker: walls, sight-blocking terrain, and (optionally) creatures."""
        battlefield = self.combat_data.get("battlefield", {})

        # Walls - use MovementSystem for terrain checking
        if self.movement_system._is_wall_tile(x, y, battlefield):
            return True

        # NEW: terrain that explicitly blocks sight (pillars/support beams, etc.)
        terrain = battlefield.get('terrain', {})
        for ob in terrain.get('obstacles', []):
            if ob.get('position') == [x, y] and ob.get('blocks_sight', False):
                return True

        # Creatures (leave as-is if you want creatures to block LOS; otherwise see note below)
        for char_state in self.character_states.values():
            if char_state.get('is_alive', True) and char_state.get('position') == [x, y]:
                return True
        for enemy in self.combat_data.get("enemy_instances", []):
            if enemy.get("current_hp", 0) > 0 and enemy.get("position") == [x, y]:
                return True

        return False

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
        
        # Check if target is the same as current position
        if char_state['position'] == target_position:
            self._add_to_combat_log("Already at that position!")
            print(f"DEBUG: Attempted to move to same position")
            return False
        
        if char_state.get('has_moved', False):
            self._add_to_combat_log("Already moved this turn!")
            return False
        
        # Validate movement
        movement_range = self.movement_system.get_movement_range(char_state)
     
        # Check for incorporeal ability
        can_phase = False
        for ability in char_state.get('abilities', []):
            if ability.get('id') == 'incorporeal':
                can_phase = True
                break
        
        # Find path to destination using movement system
        path = self.movement_system.find_path(
            char_state['position'], 
            target_position, 
            can_phase,
            is_player=True
        )
        
        if not path or len(path) - 1 > movement_range:
            self._add_to_combat_log("Invalid movement target!")
            return False
        
        # Add debugging for the path:
        print(f"DEBUG: Path calculated: {path}")

        # Start movement animation
        success = self.movement_system.start_entity_movement(
            self.active_character_id,
            char_state['position'],
            path
        )
        
        if not success:
            return False
        
        # Mark character as moved, but don't update position yet
        # Position will be updated by the movement system during animation
        char_state['has_moved'] = True
        char_state['intended_position'] = target_position
        
        # Clear action mode after successful move initiation
        self.current_action_mode = None
        
        char_name = char_state['name']
        self._add_to_combat_log(f"{char_name} moves toward [{target_position[0]}, {target_position[1]}]")
        
        # Emit movement event for UI (will be visual only until animation completes)
        self.event_manager.emit("COMBAT_UNIT_MOVED", {
            "unit_type": "player",
            "old_position": char_state['position'],
            "new_position": target_position,
            "animated": True  # Flag to indicate this is an animated move
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
                
                # 🔥 CHECK IF PLAYER DIED FIRST (defeat takes priority!)
                if self.current_phase == CombatPhase.DEFEAT:
                    return True  # Player already dead, don't check victory
                
                # Check victory conditions
                if self._check_victory_conditions():
                    self._handle_combat_victory()
                    return True

        return success

    def execute_player_ranged_attack(self, target_position: List[int]) -> bool:
        """Execute active character ranged attack on target enemy"""
        if self.current_phase != CombatPhase.PLAYER_TURN:
            return False
        
        if not self.active_character_id:
            return False
        
        char_state = self.character_states[self.active_character_id]
        
        # Check attacks remaining
        if char_state.get('attacks_used', 0) >= self._get_attacks_per_round(char_state.get('character_data')):
            self._add_to_combat_log("All attacks used this turn!")
            return False  # ← Validation at execution time
            
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
        
        # Get weapon data and range
        char_data = char_state.get('character_data', {})
        equipment = char_data.get('equipment', {})
        weapon_id = equipment.get('weapon', '')
        
        weapon_range = 8
        damage_string = "1d6"
        
        if weapon_id:
            if self.active_character_id == 'player' and hasattr(self, 'item_manager'):
                weapon_data = self.item_manager.get_item_by_id(weapon_id.lower())
                if weapon_data:
                    combat_stats = weapon_data.get('combat_stats', {})
                    weapon_range = combat_stats.get('range_grid', 8)
                    damage_string = combat_stats.get('damage_dice', '1d6')
        
        # Validate range and LOS
        char_pos = char_state['position']
        distance = abs(char_pos[0] - target_position[0]) + abs(char_pos[1] - target_position[1])
        
        if distance > weapon_range:
            self._add_to_combat_log("Target out of range!")
            return False
        
        if not self._has_line_of_sight(char_pos[0], char_pos[1], target_position[0], target_position[1]):
            self._add_to_combat_log("No line of sight!")
            return False
        
        # Execute attack
        char_name = char_state['name']
        self._add_to_combat_log(f"{char_name} shoots at {target_enemy['name']}!")
        
        # Calculate attack bonus
        if self.active_character_id == 'player':
            attack_bonus = self.stats_calculator.calculate_attack_bonus(self.game_state)[0]
            damage_string = self.stats_calculator.calculate_weapon_damage(self.game_state)[0]
        else:
            # NPC ranged attack - use DEX modifier
            char_dex = char_data.get('stats', {}).get('dexterity', 10)
            dex_mod = (char_dex - 10) // 2
            attack_bonus = dex_mod + 2  # +2 proficiency
        
        # Roll attack
        attack_roll = random.randint(1, 20)
        # Track critical hits/misses for player
        if self.active_character_id == 'player':
            if attack_roll == 20:
                self.game_state.player_statistics['critical_hits'] += 1
            elif attack_roll == 1:
                self.game_state.player_statistics['critical_misses'] += 1
        
        target_ac = target_enemy.get("stats", {}).get("ac", 10)
        total_attack = attack_roll + attack_bonus
        
        # Cover bump (+2 half, +5 three-quarters); full cover never reaches here (filtered)
        cover_level = self._compute_cover(char_pos, target_position)["level"]
        cover_bonus = 0
        if cover_level == "half":
            cover_bonus = 2
            target_ac += 2
        elif cover_level == "three_quarters":
            cover_bonus = 5
            target_ac += 5
        
        # Log cover bonus for player awareness
        if cover_bonus > 0:
            self._add_to_combat_log(f"Target has {cover_level.replace('_',' ')} cover (+{cover_bonus} AC)")

        self._add_to_combat_log(f"Attack roll: {attack_roll} + {attack_bonus} = {total_attack} vs AC {target_ac}")
        
        if total_attack >= target_ac:
            # Hit!
            damage = self._roll_damage(damage_string)
            self._add_to_combat_log(f"Hit! {damage} damage")
            
            current_hp = target_enemy.get("current_hp", 0)
            new_hp = max(0, current_hp - damage)
            target_enemy["current_hp"] = new_hp
            self._add_to_combat_log(f"{target_enemy['name']}: {new_hp}/{target_enemy.get('stats', {}).get('hp', 0)} HP")
            
            if new_hp <= 0:
                self._add_to_combat_log(f"{target_enemy['name']} defeated!")
                
                # DEBUG: What ID does the killer have?
                print(f"🔍 KILL DEBUG:")
                print(f"   active_character_id: '{self.active_character_id}'")
                print(f"   Type: {type(self.active_character_id)}")
                print(f"   character_states.keys(): {list(self.character_states.keys())}")
                
                                
                # Track enemy defeats by name (for "most defeated" stat)
                enemy_name = target_enemy.get('name', 'Unknown')
                enemy_defeats = self.game_state.player_statistics.get('enemy_defeats', {})
                enemy_defeats[enemy_name] = enemy_defeats.get(enemy_name, 0) + 1
                self.game_state.player_statistics['enemy_defeats'] = enemy_defeats
                
                 # Track kill statistics
                if self.active_character_id == 'player':
                    # Main player got the kill
                    self.game_state.player_statistics['player_kills'] += 1
                    weapon = self.game_state.character.get('equipped_weapon', 'fists')
                    weapon_kills = self.game_state.player_statistics['weapon_kills']
                    weapon_kills[weapon] = weapon_kills.get(weapon, 0) + 1
                elif self.active_character_id in self.character_states:
                    # Party member got the kill
                    self.game_state.player_statistics['party_kills'] += 1
                    member_kills = self.game_state.player_statistics['party_member_kills']
                    member_kills[self.active_character_id] = member_kills.get(self.active_character_id, 0) + 1

                # 🔥 CHECK IF PLAYER DIED FIRST (defeat takes priority!)
                if self.current_phase == CombatPhase.DEFEAT:
                    return True  # Player already dead, don't check victory
                
                if self._check_victory_conditions():
                    self._handle_combat_victory()
                    return True
        else:
            self._add_to_combat_log("Miss!")
        
        # Increment attack counter
        char_state['attacks_used'] += 1
        
        attacks_per_round = self._get_attacks_per_round(char_data)
        if char_state['attacks_used'] >= attacks_per_round:
            char_state['has_acted'] = True
            self._add_to_combat_log(f"{char_name}: All attacks used")
        
        return True

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
        """Advance to next actor in turn order, skipping dead/unconscious characters"""
        max_iterations = len(self.turn_order) + 1  # Safety limit to prevent infinite loops
        iterations = 0
        
        while iterations < max_iterations:
            self.current_actor_index += 1
            iterations += 1
            
            # If we've gone through all actors, start new round
            if self.current_actor_index >= len(self.turn_order):
                self.current_actor_index = 0
                turn_number = self.combat_data.get("turn_number", 0) + 1
                self.combat_data["turn_number"] = turn_number
                self._add_to_combat_log(f"--- Turn {turn_number} ---")
            
            # Get current actor
            current_actor_id = self.turn_order[self.current_actor_index]
            
            # Check if this actor is still alive/conscious
            is_alive = False
            
            # Check if it's a party member
            if current_actor_id in self.character_states:
                char_state = self.character_states[current_actor_id]
                is_alive = char_state.get('is_alive', True)
                
                if is_alive:
                    # Party member's turn
                    self.current_phase = CombatPhase.PLAYER_TURN
                    self.active_character_id = current_actor_id
                    self._reset_action_mode_for_active()
                    
                    # Reset action flags for this character
                    char_state['has_moved'] = False
                    char_state['attacks_used'] = 0
                    char_state['spells_cast_this_turn'] = 0 
                    
                    char_name = char_state['name']
                    self._add_to_combat_log(f"{char_name}'s turn")
                    return  # Found a living actor, exit loop
                else:
                    # CRITICAL FIX: Log and continue if character is dead/unconscious
                    char_name = char_state.get('name', 'Character')
                    self._add_to_combat_log(f"{char_name} is unconscious - skipping turn")
                    # Don't return - continue looping to find next living actor
            else:
                # Check if it's a living enemy
                enemy_instances = self.combat_data.get("enemy_instances", [])
                for enemy in enemy_instances:
                    if enemy.get("instance_id") == current_actor_id:
                        if enemy.get("current_hp", 0) > 0:
                            is_alive = True
                            self.current_phase = CombatPhase.ENEMY_TURN
                            self._execute_enemy_turn(current_actor_id)
                            return  # Found a living actor, exit loop
                        else:
                            # CRITICAL FIX: Log and continue if enemy is dead
                            enemy_name = enemy.get('name', 'Enemy')
                            self._add_to_combat_log(f"{enemy_name} is defeated - skipping turn")
                        break
            
            # If we get here, actor was dead/unconscious, loop continues to next actor
        
        # If we exhausted all actors and none are alive, combat should end
        print("⚠️ WARNING: All actors in turn order are unconscious/dead!")
        # Consider ending combat or triggering special defeat condition here
        
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
                base_ac = target_data.get("stats", {}).get("ac", 10)
                
                # Check for cover bonus (ranged attacks only)
                cover_bonus = 0
                if self.current_action_mode == "ranged_attack":
                    attacker_pos = self.character_states[self.active_character_id]["position"]
                    defender_pos = target_data.get("position", [0, 0])
                    
                    # Use existing 5-ray cover computation system
                    cover_data = self._compute_cover(attacker_pos, defender_pos, creatures_grant_cover=False)
                    cover_level = cover_data.get("level", "none")
                    cover_bonus = self._get_cover_ac_bonus(cover_level)
                    
                    if cover_level != "none":
                        self._add_to_combat_log(f"Target has {cover_level} cover! (+{cover_bonus} AC)")
                    
                    # Full cover = can't target (should be blocked by UI, but safety check)
                    if cover_level == "full":
                        self._add_to_combat_log("Target has full cover - cannot attack!")
                        return False
                
                target_ac = base_ac + cover_bonus
                
            else:
                # Enemy attacking player/party
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
                
                # Get target AC - check if it's a party member or player
                target_char_id = None
                for char_id, char_state in self.character_states.items():
                    if char_state.get('character_data') == target_data:
                        target_char_id = char_id
                        break
                
                # Use party member AC or player AC
                if target_char_id and target_char_id != 'player':
                    base_ac = target_data.get('ac', 10)
                else:
                    base_ac = self.stats_calculator.calculate_armor_class(self.game_state)[0]
                
                # Check for cover bonus (ranged attacks only)
                cover_bonus = 0
                enemy_attack_type = attacker_data.get("attacks", [{}])[0].get("attack_type", "melee")
                if enemy_attack_type == "ranged":
                    attacker_pos = attacker_data.get("position", [0, 0])
                    
                    # Get defender position from character_states
                    defender_char_state = self.character_states.get(target_char_id, {})
                    defender_pos = defender_char_state.get("position", [0, 0])
                    
                    # Use existing 5-ray cover computation system
                    cover_data = self._compute_cover(attacker_pos, defender_pos, creatures_grant_cover=False)
                    cover_level = cover_data.get("level", "none")
                    cover_bonus = self._get_cover_ac_bonus(cover_level)
                    
                    if cover_level != "none":
                        self._add_to_combat_log(f"Target has {cover_level} cover! (+{cover_bonus} AC)")
                    
                    # Full cover = enemy can't target (AI should avoid this)
                    if cover_level == "full":
                        self._add_to_combat_log("Target has full cover - attack blocked!")
                        return False
                
                target_ac = base_ac + cover_bonus
            
            # Roll attack (d20 + bonus vs AC)
            attack_roll = random.randint(1, 20)
            total_attack = attack_roll + attack_bonus
            # Track critical hits/misses for player attacks
            if attacker_type == "player":
                if attack_roll == 20:
                    current_crits = self.game_state.player_statistics.get('critical_hits', 0)
                    self.game_state.player_statistics['critical_hits'] = current_crits + 1
                elif attack_roll == 1:
                    current_crit_miss = self.game_state.player_statistics.get('critical_misses', 0)
                    self.game_state.player_statistics['critical_misses'] = current_crit_miss + 1

            self._add_to_combat_log(f"{attacker_name} attacks {target_name}")
            self._add_to_combat_log(f"Attack roll: {attack_roll} + {attack_bonus} = {total_attack} vs AC {target_ac}")
            
            # Check if attack hits
            if total_attack >= target_ac:
                # Hit! Roll damage
                if attacker_type == "player": self.game_state.player_statistics['hits'] += 1 
                damage = self._roll_damage(damage_string)
                
                # Track biggest hit and total damage for player
                if attacker_type == "player":
                    # Safe access with .get() for backward compatibility with old saves
                    current_biggest = self.game_state.player_statistics.get('biggest_hit', 0)
                    if damage > current_biggest:
                        self.game_state.player_statistics['biggest_hit'] = damage
                    
                    # Track cumulative damage dealt
                    total_damage = self.game_state.player_statistics.get('total_damage_dealt', 0)
                    self.game_state.player_statistics['total_damage_dealt'] = total_damage + damage
                
                self._add_to_combat_log(f"Hit! {damage} damage")
                
                # Apply damage based on attacker type
                if attacker_type == "player":
                    # Player hitting enemy
                    current_hp = target_data.get("current_hp", 0)
                    new_hp = max(0, current_hp - damage)
                    target_data["current_hp"] = new_hp
                    self._add_to_combat_log(f"{target_name}: {new_hp}/{target_data.get('stats', {}).get('hp', 0)} HP")
                    
                    # Track kills when enemy defeated
                    if new_hp <= 0:
                        self._add_to_combat_log(f"{target_name} defeated!")
                        
                        # Award XP immediately to killer only
                        xp_value = target_data.get('loot', {}).get('xp_value', 0)
                        if xp_value > 0 and self.active_character_id:
                            killer_name = self.character_states[self.active_character_id]['character_data'].get('name', 'Unknown')
                            
                            # Award XP to specific character who got the kill
                            if self.event_manager:
                                self.event_manager.emit("XP_AWARDED", {
                                    'amount': xp_value,
                                    'reason': f"defeated {target_name}",
                                    'recipient': self.active_character_id  # Only the killer
                                })
                            self._add_to_combat_log(f"{killer_name} gained {xp_value} XP!")
                        
                        # Store defeated enemy data for loot calculation
                        self.defeated_enemies_loot_data.append({
                            'name': target_name,
                            'loot': target_data.get('loot', {})
                        })
                        
                        # Track enemy defeats by name (for "most defeated" stat)
                        enemy_name = target_data.get('name', 'Unknown')
                        enemy_defeats = self.game_state.player_statistics.get('enemy_defeats', {})
                        enemy_defeats[enemy_name] = enemy_defeats.get(enemy_name, 0) + 1
                        self.game_state.player_statistics['enemy_defeats'] = enemy_defeats
                        
                        # Track kill statistics
                        if self.active_character_id == 'player':
                            # Main player got the kill
                            self.game_state.player_statistics['player_kills'] += 1
                            weapon = self.game_state.character.get('equipped_weapon', 'fists')
                            weapon_kills = self.game_state.player_statistics.get('weapon_kills', {})
                            weapon_kills[weapon] = weapon_kills.get(weapon, 0) + 1
                            self.game_state.player_statistics['weapon_kills'] = weapon_kills
                        elif self.active_character_id in self.character_states:
                            # Party member got the kill
                            self.game_state.player_statistics['party_kills'] += 1
                            member_kills = self.game_state.player_statistics.get('party_member_kills', {})
                            member_kills[self.active_character_id] = member_kills.get(self.active_character_id, 0) + 1
                            self.game_state.player_statistics['party_member_kills'] = member_kills
                else:
                    # Enemy hitting party member

                    # Find the correct character state to damage
                    target_char_id = None
                    for char_id, char_state in self.character_states.items():
                        if char_state.get('character_data') == target_data:
                            target_char_id = char_id
                            break
                    
                    if target_char_id:
                        char_state = self.character_states[target_char_id]
                        
                        # Check if targeting main player or party member
                        if target_char_id == 'player':
                            # Damage main player character
                            current_hp = self.game_state.character.get("current_hp", 0)
                            new_hp = max(0, current_hp - damage)
                            self.game_state.character["current_hp"] = new_hp
                            
                            # Show current/max HP in combat log
                            max_hp = self.game_state.character.get("hit_points", 0)
                            self._add_to_combat_log(f"{target_name}: {new_hp}/{max_hp} HP")
                            
                            # Check if player defeated - INSTANT DEATH!
                            if new_hp <= 0:
                                char_state['is_alive'] = False
                                self._add_to_combat_log(f"{target_name} has fallen!")
                                # Player death triggers immediate defeat
                                self._handle_combat_defeat()
                        else:
                            # Damage party member (NPC)
                            for member in self.game_state.party_member_data:
                                if member['id'] == target_char_id:
                                    current_hp = member.get("current_hp", member.get('hp', 0))
                                    new_hp = max(0, current_hp - damage)
                                    member["current_hp"] = new_hp
                                    
                                    # Also update character_data in combat state
                                    target_data["current_hp"] = new_hp
                                    
                                    # Show current/max HP in combat log
                                    max_hp = member.get('hp', member.get('hit_points', 0))
                                    self._add_to_combat_log(f"{target_name}: {new_hp}/{max_hp} HP")
                                    
                                    # Check if character defeated (knocked out, not dead!)
                                    if new_hp <= 0:
                                        char_state['is_alive'] = False
                                        char_state['is_conscious'] = False
                                        self._add_to_combat_log(f"{target_name} is knocked unconscious!")

                                        # Track party member knockouts
                                        self.game_state.player_statistics['party_knockouts'] += 1
                                        
                                        # Check if ALL party members are knocked out (defeat)
                                        all_unconscious = all(
                                            not cs.get('is_alive', True) 
                                            for cs in self.character_states.values()
                                        )
                                        if all_unconscious:
                                            self._handle_combat_defeat()
                                    break
                
                return True
            else:
                # Miss
                self._add_to_combat_log("Miss!")
                if attacker_type == "player": self.game_state.player_statistics['misses'] += 1
                return False
                
        except Exception as e:
            print(f"❌ Error resolving attack: {e}")
            import traceback
            traceback.print_exc()
            self._add_to_combat_log("Attack failed!")
            return False
    
    def _resolve_attack_with_weapon(self, attacker_type: str, attacker_data: Dict, target_data: Dict, weapon_attack: Dict) -> bool:
        """
        Resolve attack using specific weapon data (for enemies with multiple attacks)
        
        Args:
            attacker_type: "player" or "enemy"
            attacker_data: Attacker's data
            target_data: Target's data
            weapon_attack: Specific weapon attack dict with damage_dice, attack_bonus, etc.
            
        Returns:
            bool: True if attack hit
        """
        try:
            attacker_name = attacker_data.get("name", "Enemy")
            target_name = target_data.get("name", "Target")
            
            # Use weapon-specific attack bonus and damage
            attack_bonus = weapon_attack.get("attack_bonus", 0)
            damage_string = weapon_attack.get("damage_dice", "1d4")
            
            # Get target AC
            target_char_id = None
            for char_id, char_state in self.character_states.items():
                if char_state.get('character_data') == target_data:
                    target_char_id = char_id
                    break
            
            if target_char_id and target_char_id != 'player':
                base_ac = target_data.get('ac', 10)
            else:
                base_ac = self.stats_calculator.calculate_armor_class(self.game_state)[0]
            
            # Check for cover bonus (ranged attacks only)
            cover_bonus = 0
            if weapon_attack.get("attack_type") == "ranged":
                attacker_pos = attacker_data.get("position", [0, 0])
                
                # Get defender position from character_states
                defender_char_state = self.character_states.get(target_char_id, {})
                defender_pos = defender_char_state.get("position", [0, 0])
                
                # Use existing 5-ray cover computation system
                cover_data = self._compute_cover(attacker_pos, defender_pos, creatures_grant_cover=False)
                cover_level = cover_data.get("level", "none")
                cover_bonus = self._get_cover_ac_bonus(cover_level)
                
                if cover_level != "none":
                    self._add_to_combat_log(f"Target has {cover_level} cover! (+{cover_bonus} AC)")
                
                # Full cover = can't attack
                if cover_level == "full":
                    self._add_to_combat_log("Target has full cover - attack blocked!")
                    return False
            
            target_ac = base_ac + cover_bonus
            
            # Roll attack
            attack_roll = random.randint(1, 20)
            total_attack = attack_roll + attack_bonus
            
            self._add_to_combat_log(f"{attacker_name} attacks {target_name}")
            self._add_to_combat_log(f"Attack roll: {attack_roll} + {attack_bonus} = {total_attack} vs AC {target_ac}")
            
            if total_attack >= target_ac:
                # Hit! Roll damage
                damage = self._roll_damage(damage_string)
                self._add_to_combat_log(f"Hit! {damage} damage")
                
                # Apply damage (same logic as _resolve_attack)
                if target_char_id == 'player':
                        # Damage main player
                        current_hp = self.game_state.character.get("current_hp", 0)
                        new_hp = max(0, current_hp - damage)
                        self.game_state.character["current_hp"] = new_hp
                        
                        max_hp = self.game_state.character.get("hit_points", 0)
                        self._add_to_combat_log(f"{target_name}: {new_hp}/{max_hp} HP")
                        
                        # Check if player defeated - INSTANT DEATH!
                        if new_hp <= 0:
                            char_state = self.character_states.get(target_char_id)
                            if char_state:
                                char_state['is_alive'] = False
                            self._add_to_combat_log(f"{target_name} has fallen!")
                            # Player death triggers immediate defeat
                            self._handle_combat_defeat()
                else:
                    # Damage party member
                    for member in self.game_state.party_member_data:
                        if member['id'] == target_char_id:
                            current_hp = member.get("current_hp", member.get('hp', 0))
                            new_hp = max(0, current_hp - damage)
                            member["current_hp"] = new_hp
                            target_data["current_hp"] = new_hp
                            
                            max_hp = member.get('hp', member.get('hit_points', 0))
                            self._add_to_combat_log(f"{target_name}: {new_hp}/{max_hp} HP")
                            
                            if new_hp <= 0:
                                char_state = self.character_states.get(target_char_id)
                                if char_state:
                                    char_state['is_alive'] = False
                                    char_state['is_conscious'] = False
                                    self._add_to_combat_log(f"{target_name} is knocked unconscious!")
                                
                                all_unconscious = all(
                                    not cs.get('is_alive', True) 
                                    for cs in self.character_states.values()
                                )
                                if all_unconscious:
                                    self._handle_combat_defeat()
                            break
                
                return True
            else:
                self._add_to_combat_log("Miss!")
                return False
                
        except Exception as e:
            print(f"❌ Error resolving weapon attack: {e}")
            import traceback
            traceback.print_exc()
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
    
    def _is_tile_occupied(self, x: int, y: int) -> bool:
            """Check if a tile is occupied by any unit (party member or enemy)"""
            position = [x, y]
            
            # Check party member positions
            for char_id, char_state in self.character_states.items():
                if char_state.get('is_alive', True):
                    if char_state['position'] == position:
                        return True
            
            # Check enemy positions - Allowing dead bodies to be passable...
            enemy_instances = self.combat_data.get("enemy_instances", [])
            for enemy in enemy_instances:
                if enemy.get("current_hp", 0) > 0:  # Only living enemies block
                    if enemy.get("position") == position:
                        return True
            #IF want to block movement on corpses, use the below and remove the above.
            # for enemy in enemy_instances:
            #     if enemy.get("position") == position:
            #         return True  # Both corpses and living enemies block

            return False
    
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
        
        # Stabilize unconscious party members at 1 HP
        for char_id, char_state in self.character_states.items():
            if char_id == 'player':
                continue  # Player can't be unconscious in victory (they'd be dead)
            
            if not char_state.get('is_alive', True):
                # This NPC was knocked unconscious - restore to 1 HP
                char_name = char_state.get('name', 'Party member')
                
                # Update in party_member_data (persistent game state)
                for member in self.game_state.party_member_data:
                    if member['id'] == char_id:
                        member['current_hp'] = 1
                        # Also restore in combat state
                        char_data = char_state.get('character_data', {})
                        char_data['current_hp'] = 1
                        # Mark as alive again
                        char_state['is_alive'] = True
                        char_state['is_conscious'] = True
                        
                        self._add_to_combat_log(f"{char_name} stabilized at 1 HP")
                        print(f"💚 {char_name} restored to 1 HP after victory")
                        break

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
        
        # Calculate total loot from defeated enemies + encounter bonuses
        loot_data = self._calculate_combat_loot(rewards)
        
        # Store loot data
        self.game_state.combat_loot_data = loot_data
        
        # Clear defeated enemies list now that loot is calculated
        self.defeated_enemies_loot_data = []
        print(f"🧹 Cleared defeated enemies loot data after calculation")
        
        # Open loot overlay via overlay system
        if not hasattr(self.game_state, 'overlay_state'):
            from ui.screen_manager import OverlayState
            self.game_state.overlay_state = OverlayState()
        
        self.game_state.overlay_state.open_overlay("combat_loot")
        print(f"💰 Combat loot overlay opened: {loot_data['total_gold']} gold, {len(loot_data['items'])} item types")
    
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

        # 🔥 CLOSE LOOT OVERLAY FIRST (if open)
        if hasattr(self.game_state, 'overlay_state'):
            if self.game_state.overlay_state.get_active_overlay() == "combat_loot":
                self.game_state.overlay_state.close_overlay()
                print("💰 Closed loot overlay before death screen")

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
        # Award XP through event system for proper tracking
        xp = rewards.get("xp", 0)
        if xp > 0:
            encounter_id = self.combat_data.get("encounter", {}).get("encounter_id", "combat")
            
            # Emit XP_AWARDED event - character_engine will handle tracking
            if self.event_manager:
                self.event_manager.emit("XP_AWARDED", {
                    'amount': xp,
                    'reason': f"defeated enemies in {encounter_id}",
                    'recipient': 'party'
                })
            
            self._add_to_combat_log(f"Gained {xp} XP!")
        
        # Award gold
        gold = rewards.get("gold", 0)
        if gold > 0:
            self.game_state.character['gold'] += gold
            
            # Track in statistics (with safety check)
            if not hasattr(self.game_state, 'player_statistics'):
                self.game_state.player_statistics = {}
            if 'total_gold_earned' not in self.game_state.player_statistics:
                self.game_state.player_statistics['total_gold_earned'] = 0
            
            self.game_state.player_statistics['total_gold_earned'] += gold
            self._add_to_combat_log(f"Gained {gold} gold!")
        
        # TODO: Award items from rewards["items"]
    
    def _calculate_combat_loot(self, encounter_rewards: Dict) -> Dict:
        """
        Calculate total loot from all defeated enemies plus encounter bonuses
        
        Returns dict with:
            'total_gold': int
            'items': [{'item_id': str, 'quantity': int, 'name': str}, ...]
        """
        import random
        
        total_gold = 0
        items_dict = {}  # item_id -> quantity
        
        # 1) Roll gold and items from each defeated enemy
        for enemy_loot_data in self.defeated_enemies_loot_data:
            loot = enemy_loot_data.get('loot', {})
            
            # Roll gold from enemy's gold_range
            gold_range = loot.get('gold_range', [0, 0])
            if len(gold_range) == 2:
                enemy_gold = random.randint(gold_range[0], gold_range[1])
                total_gold += enemy_gold
            
            # Roll for item drops
            item_drops = loot.get('item_drops', [])
            for drop_entry in item_drops:
                item_id = drop_entry.get('item_id')
                drop_chance = drop_entry.get('drop_chance', 0.0)
                quantity_range = drop_entry.get('quantity_range', [1, 1])
                
                # Roll for drop
                if random.random() <= drop_chance:
                    # Roll quantity
                    if len(quantity_range) == 2:
                        quantity = random.randint(quantity_range[0], quantity_range[1])
                    else:
                        quantity = 1
                    
                    # Add to items dict (stacking)
                    items_dict[item_id] = items_dict.get(item_id, 0) + quantity
        
        # 2) Add encounter bonus gold
        encounter_gold = encounter_rewards.get('gold', 0)
        total_gold += encounter_gold
        
        # 3) Add encounter bonus items (guaranteed drops)
        encounter_items = encounter_rewards.get('items', [])
        for item_id in encounter_items:
            items_dict[item_id] = items_dict.get(item_id, 0) + 1
        
        # 4) Convert items_dict to list format with names
        items_list = []
        for item_id, quantity in items_dict.items():
            # Get display name from ItemManager
            if self.item_manager:
                display_name = self.item_manager.get_display_name(item_id)
            else:
                display_name = item_id.replace('_', ' ').title()
            
            items_list.append({
                'item_id': item_id,
                'quantity': quantity,
                'name': display_name
            })
        
        return {
            'total_gold': total_gold,
            'items': items_list
        }

    def _get_current_actor_name(self) -> str:
        """Get display name of current actor"""
        if self.current_phase == CombatPhase.SETUP:
            return "Setup"
        elif self.current_phase == CombatPhase.PLAYER_TURN:
            # Get active party member name
            if self.active_character_id and self.active_character_id in self.character_states:
                return self.character_states[self.active_character_id]['name']
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
    
    #from typing import List

    def _get_highlighted_tiles(self) -> List[List[int]]:
        """Return grid positions to highlight based on current action mode."""
        tiles: List[List[int]] = []

        if self.current_phase != CombatPhase.PLAYER_TURN or not self.active_character_id:
            return tiles

        char_state = self.character_states.get(self.active_character_id)
        if not char_state:
            return tiles

        pos = char_state['position']
        mode = self.current_action_mode

        # MOVEMENT
        if mode == "movement":
            movement_range = self.movement_system.get_movement_range(char_state)
            # Check for incorporeal ability
            can_phase = False
            abilities = char_state.get('character_data', {}).get('abilities', [])
            for ability in abilities:
                if ability.get('id') == 'incorporeal':
                    can_phase = True
                    break
            return self.movement_system.get_valid_moves(pos, movement_range, can_phase, is_player=True)

        # MELEE
        if mode == "attack":
            targets = self.get_attack_targets(pos, attack_range=1, requires_los=False)
            return [t["position"] for t in targets]

        # RANGED ATTACK (infinite ammo, but only if weapon is actually ranged)
        if mode == "ranged_attack":
            weapon_id = (char_state.get('character_data', {})
                                .get('equipment', {})
                                .get('weapon'))

            weapon_data = None
            if isinstance(weapon_id, str) and hasattr(self, 'item_manager'):
                weapon_data = self.item_manager.get_item_by_id(weapon_id.lower())

            # Must be ranged; otherwise no highlights
            is_ranged = False
            weapon_range = 0  # force empty unless confirmed ranged
            if weapon_data:
                cs = weapon_data.get('combat_stats', {}) or {}
                # treat as ranged if explicitly marked or has >1 tile reach
                is_ranged = (cs.get('range') == 'ranged') or (cs.get('range_grid', 0) > 1)
                if is_ranged:
                    weapon_range = cs.get('range_grid', 8)

            if not is_ranged:
                return []  # fighter w/no bow -> no cyan tiles

            targets = self.get_attack_targets(
                pos, attack_range=weapon_range, requires_los=True
            )
            return [t["position"] for t in targets]

        return tiles

    def get_line_cells(self, start: List[int], end: List[int]) -> List[List[int]]:
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        cells: List[List[int]] = []
        while True:
            cells.append([x0, y0])
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return cells

    def get_ranged_preview(self, origin: List[int], target: List[int]) -> dict:
        """
        Returns a dict the UI can use to draw a dotted line:
        {
            "cells": [[x,y], ...],          # line cells origin→target inclusive
            "blocked_at": idx_or_None,      # first index in cells that is blocked
            "in_range": True/False,         # distance check using same metric as attacks
            "has_los": True/False
        }
        """
        line = self.get_line_cells(origin, target)
        blocked_idx = None
        for i, cell in enumerate(line[1:-1], start=1):  # ignore origin & target for blockers
            if self._is_obstacle(cell):                 # use your existing map/LOS blocker test
                blocked_idx = i
                break

        # Reuse your attack distance rule (or call the same internal function)
        in_range = self._distance_rule(origin, target)  # Manhattan/Chebyshev/etc.
        has_los = blocked_idx is None

        return {
            "cells": line,
            "blocked_at": blocked_idx,
            "in_range": in_range,
            "has_los": has_los
        }

    def _add_to_combat_log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
        #print(f"🎯 {message}")  # Also print to console for debugging
    
    #++++++++++++++ SPELL METHODS +++++++++++++++++++++++++++++++++++++++++
    def _get_max_spell_slots(self, character_data: dict) -> int:
        """Get maximum spell slots for character based on class and level"""
        char_class = character_data.get('class', '').lower()
        level = character_data.get('level', 1)
        
        # Spellcasting classes get slots
        if char_class in ['wizard', 'cleric']:
            # Simple progression: 2 slots at level 1, +1 per level
            return 2 + (level - 1)
        
        # Non-casters have no slots
        return 0

    def _get_character_spells(self, character_data: dict) -> list:
        """Get list of spell IDs this character knows"""
        # DEBUG - get name first
        char_name = character_data.get('name', 'Unknown')
        
        # Check for spells in character data
        spells_data = character_data.get('spells', {})
        
        # DEBUG
        print(f"🔍 _get_character_spells for {char_name}:")
        print(f"   spells_data type: {type(spells_data)}")
        print(f"   spells_data: {spells_data}")
        
        # Handle different spell data formats
        if isinstance(spells_data, dict):
            # Format: {"spells_known": ["cure_wounds", "bless"]}
            spells_known = spells_data.get('spells_known', [])
        elif isinstance(spells_data, list):
            # Format: ["cure_wounds", "bless"]
            spells_known = spells_data
        else:
            spells_known = []
        
        print(f"   After parsing - spells_known: {spells_known}")
        
        # Convert spell names to lowercase IDs
        spell_ids = []
        for spell in spells_known:
            # Convert "Cure Wounds" to "cure_wounds"
            spell_id = spell.lower().replace(' ', '_')
            # Only add if we have definition for it
            if spell_id in self.spell_data:
                spell_ids.append(spell_id)
                print(f"   ✅ Added spell: {spell_id}")
            else:
                print(f"   ❌ Spell not in spell_data: {spell_id}")
        
        print(f"   Final spell_ids: {spell_ids}")
        return spell_ids

    def get_available_spells(self, character_id: str) -> list:
        """
        Get list of spells character can currently cast
        Returns list of dicts with spell info
        """
        if character_id not in self.character_states:
            return []
        
        char_state = self.character_states[character_id]
        
        # Check if character has spell slots remaining
        if char_state.get('spell_slots_remaining', 0) <= 0:
            return []
        
        # Get spells known
        spells_known = char_state.get('spells_known', [])
        
        # Build list of castable spells with full data
        available_spells = []
        for spell_id in spells_known:
            if spell_id in self.spell_data:
                spell_info = self.spell_data[spell_id].copy()
                available_spells.append(spell_info)
        
        return available_spells
    
    def _get_spell_targets(self, spell_id: str) -> list:
        """Get valid target positions for a spell"""
        if not self.active_character_id:
            return []
        
        char_state = self.character_states.get(self.active_character_id)
        if not char_state:
            return []
        
        spell_data = self.spell_data.get(spell_id)
        if not spell_data:
            return []
        
        caster_pos = char_state['position']
        spell_range = spell_data.get('range', 1)
        target_type = spell_data.get('target_type', 'any')
        
        valid_targets = []
        
        # Check all positions within range
        for dx in range(-spell_range, spell_range + 1):
            for dy in range(-spell_range, spell_range + 1):
                target_pos = [caster_pos[0] + dx, caster_pos[1] + dy]
                
                # Allow caster position for ally-targeted spells (like healing)
                if target_pos == caster_pos:
                    if target_type != "ally":
                        continue  # Only skip self for non-ally spells
                
                # Check manhattan distance
                distance = abs(dx) + abs(dy)
                if distance > spell_range:
                    continue
                
                # Check if position has valid target
                if target_type == "ally":
                    # Only target party members
                    for char_id, state in self.character_states.items():
                        if state['position'] == target_pos and state.get('is_alive', True):
                            valid_targets.append(target_pos)
                            break
                elif target_type == "enemy":
                    # Only target enemies
                    for enemy in self.combat_data.get("enemy_instances", []):
                        if enemy['position'] == target_pos and enemy.get('current_hp', 0) > 0:
                            valid_targets.append(target_pos)
                            break
                else:  # "all" or "any"
                    # Target any position (for AOE spells)
                    valid_targets.append(target_pos)
        
        return valid_targets
    
    def execute_spell_cast(self, target_position: List[int]) -> bool:
        """Execute spell casting on target position"""
        if self.current_phase != CombatPhase.PLAYER_TURN:
            return False
        
        if not self.active_character_id or not hasattr(self, 'selected_spell_id'):
            return False
        
        char_state = self.character_states[self.active_character_id]
        
        # 🔥 CHECK IF ALREADY CAST A SPELL THIS TURN
        spells_cast = char_state.get('spells_cast_this_turn', 0)
        if spells_cast >= 1:
            self._add_to_combat_log("Already cast a spell this turn!")
            print("❌ Already cast a spell this turn")
            return False
        
        spell_id = self.selected_spell_id
        spell_data = self.spell_data.get(spell_id)
        
        if not spell_data:
            return False
        
        # Validate target is in valid targets
        valid_targets = self._get_spell_targets(spell_id)
        if target_position not in valid_targets:
            self._add_to_combat_log("Invalid target!")
            return False
        
        # Get affected area (for AOE spells like Fireball)
        affected_positions = self._get_spell_affected_area(spell_data, target_position)
        
        # Cast the spell
        self._execute_spell_effect(spell_data, affected_positions, char_state)
        
       # Consume spell slot
        char_state['spell_slots_remaining'] -= 1
        char_state['spells_cast_this_turn'] += 1  # ← ADD THIS
        print(f"🔮 Spell slots: {char_state['spell_slots_remaining']}/{char_state['spell_slots_max']}")
        print(f"🔮 Spells cast this turn: {char_state['spells_cast_this_turn']}")
                
        # Clear spell selection and mode
        self.selected_spell_id = None
        self.set_action_mode(None)
        
        # Mark action used
        char_state['has_acted'] = True
        
        return True
    
    def _get_spell_affected_area(self, spell_data: dict, target_position: List[int]) -> List[List[int]]:
        """Get all positions affected by spell (for AOE)"""
        area_type = spell_data.get('area_type', 'single')
        area_size = spell_data.get('area_size', 1)
        
        affected = []
        
        if area_type == "single":
            # Single target only
            affected.append(target_position)
        
        elif area_type == "area":
            # Square area (e.g., 3x3 for Fireball)
            half_size = area_size // 2
            for dx in range(-half_size, half_size + 1):
                for dy in range(-half_size, half_size + 1):
                    pos = [target_position[0] + dx, target_position[1] + dy]
                    affected.append(pos)
        
        elif area_type == "line":
            # Line from caster toward target (like Lightning Bolt)
            char_state = self.character_states[self.active_character_id]
            caster_pos = char_state['position']
            
            # Calculate direction
            dx = 1 if target_position[0] > caster_pos[0] else -1 if target_position[0] < caster_pos[0] else 0
            dy = 1 if target_position[1] > caster_pos[1] else -1 if target_position[1] < caster_pos[1] else 0
            
            # Create line
            current = caster_pos.copy()
            for _ in range(area_size):
                current = [current[0] + dx, current[1] + dy]
                affected.append(current.copy())
        
        return affected

    def _execute_spell_effect(self, spell_data: dict, affected_positions: List[List[int]], caster_state: dict):
        """Apply spell effects to all affected positions"""
        spell_name = spell_data.get('name', 'Spell')
        damage_type = spell_data.get('damage_type', 'damage')
        caster_name = caster_state.get('name', 'Caster')
        caster_level = caster_state.get('character_data', {}).get('level', 1)
        
        # Roll damage/healing
        damage_amount = self._roll_spell_damage(spell_data, caster_state, caster_level)
        
        self._add_to_combat_log(f"{caster_name} casts {spell_name}!")
        
        # Apply to all affected positions
        for pos in affected_positions:
            # Check party members
            for char_id, char_state in self.character_states.items():
                if char_state['position'] == pos and char_state.get('is_alive', True):
                    self._apply_spell_to_character(char_state, damage_amount, damage_type, spell_name)
            
            # Check enemies
            for enemy in self.combat_data.get("enemy_instances", []):
                if enemy['position'] == pos and enemy.get('current_hp', 0) > 0:
                    self._apply_spell_to_enemy(enemy, damage_amount, damage_type, spell_name)

    def _roll_spell_damage(self, spell_data: dict, caster_state: dict, caster_level: int) -> int:
        """Roll spell damage/healing amount"""
        damage_dice = spell_data.get('damage_dice', '1d8')
        scales_with_level = spell_data.get('scales_with_level', False)
        add_stat_modifier = spell_data.get('add_stat_modifier')
        
        print(f"🎲 DEBUG: damage_dice={damage_dice}, scales={scales_with_level}, caster_level={caster_level}")
        
        # Parse dice notation (e.g., "1d8" or "3d6")
        if 'd' in damage_dice:
            num_dice, die_size = damage_dice.split('d')
            num_dice = int(num_dice)
            die_size = int(die_size)
            
            # Scale with level if specified
            if scales_with_level:
                num_dice = num_dice * caster_level
            
            print(f"🎲 DEBUG: Rolling {num_dice}d{die_size}")
            
            # Roll the dice
            total = sum(random.randint(1, die_size) for _ in range(num_dice))
            print(f"🎲 DEBUG: Rolled {total}")
        else:
            total = int(damage_dice)
        
        # Add stat modifier if specified
        if add_stat_modifier:
            char_data = caster_state.get('character_data', {})
            stats = char_data.get('stats', {})
            stat_value = stats.get(add_stat_modifier, 10)
            modifier = (stat_value - 10) // 2
            print(f"🎲 DEBUG: Adding {add_stat_modifier} modifier: stat={stat_value}, mod={modifier}")
            total += modifier
        
        print(f"🎲 DEBUG: Final total: {total}")
        return max(1, total)  # Minimum 1

    def _apply_spell_to_character(self, char_state: dict, amount: int, damage_type: str, spell_name: str):
        """Apply spell effect to a party member"""
        
        char_name = char_state.get('name', 'Character')
        char_data = char_state.get('character_data', {})
        
        # Get the ID from char_data
        char_id = char_data.get('id')
        
        print(f"💊 DEBUG: Applying {amount} {damage_type} to {char_name} (id: {char_id})")

        if damage_type == "healing":
            # 🔥 GET OLD_HP AND MAX_HP FROM LIVE GAME_STATE, NOT SNAPSHOT!
            if char_id == 'player':
                # Player character - read from game_state.character
                old_hp = self.game_state.character.get('current_hp', 0)
                max_hp = self.game_state.character.get('hit_points', 10)
            else:
                # Party member - find in live game_state.party_member_data
                old_hp = 0
                max_hp = 10
                for member in self.game_state.party_member_data:
                    if member.get('id') == char_id:
                        old_hp = member.get('current_hp', 0)
                        max_hp = member.get('hp', member.get('hit_points', 10))
                        break
            
            print(f"💊 DEBUG: LIVE old_hp={old_hp}, max_hp={max_hp}")
            
            # Calculate healing
            new_hp = min(old_hp + amount, max_hp)
            actual_healing = new_hp - old_hp
            
            print(f"💊 DEBUG: new_hp={new_hp}, actual_healing={actual_healing}")
            
            # 🎯 APPLY TO CORRECT CHARACTER IN GAME_STATE
            if char_id == 'player':
                # Update main player
                self.game_state.character["current_hp"] = new_hp
                max_hp_display = self.game_state.character.get("hit_points", max_hp)
                self._add_to_combat_log(f"{char_name}: {new_hp}/{max_hp_display} HP")
                
            else:
                # Update party member - loop through list to find them
                for member in self.game_state.party_member_data:
                    if member.get('id') == char_id:
                        member["current_hp"] = new_hp
                        
                        max_hp_display = member.get('hp', member.get('hit_points', max_hp))
                        self._add_to_combat_log(f"{char_name}: {new_hp}/{max_hp_display} HP")
                        break
            
            # Also update the snapshot in char_state for UI consistency
            char_data["current_hp"] = new_hp
            
            self._add_to_combat_log(f"{char_name} healed for {actual_healing} HP!")
            
        else:
            # 🔥 DAMAGE - ALSO READ FROM LIVE GAME_STATE!
            if char_id == 'player':
                # Player character - read from game_state.character
                old_hp = self.game_state.character.get('current_hp', 0)
                max_hp = self.game_state.character.get('hit_points', 0)
            else:
                # Party member - find in live game_state.party_member_data
                old_hp = 0
                max_hp = 0
                for member in self.game_state.party_member_data:
                    if member.get('id') == char_id:
                        old_hp = member.get('current_hp', 0)
                        max_hp = member.get('hp', member.get('hit_points', 0))
                        break
            
            print(f"💊 DEBUG: LIVE Damage - old_hp={old_hp}")
            
            # Calculate damage
            new_hp = max(0, old_hp - amount)
            
            print(f"💊 DEBUG: new_hp={new_hp}")
            
            # 🎯 APPLY TO CORRECT CHARACTER IN GAME_STATE
            if char_id == 'player':
                # Damage main player
                self.game_state.character["current_hp"] = new_hp
                max_hp_display = self.game_state.character.get("hit_points", 0)
                self._add_to_combat_log(f"{char_name}: {new_hp}/{max_hp_display} HP")
                
                # Check if player defeated - INSTANT DEATH!
                if new_hp <= 0:
                    char_state['is_alive'] = False
                    self._add_to_combat_log(f"{char_name} has fallen!")
                    self._handle_combat_defeat()
                    
            else:
                # Damage party member
                for member in self.game_state.party_member_data:
                    if member.get('id') == char_id:
                        member["current_hp"] = new_hp
                        
                        max_hp_display = member.get('hp', member.get('hit_points', 0))
                        self._add_to_combat_log(f"{char_name}: {new_hp}/{max_hp_display} HP")
                        
                        if new_hp <= 0:
                            char_state['is_alive'] = False
                            char_state['is_conscious'] = False
                            self._add_to_combat_log(f"{char_name} is knocked unconscious!")
                            
                            # Check if whole party wiped
                            all_unconscious = all(
                                not cs.get('is_alive', True) 
                                for cs in self.character_states.values()
                            )
                            if all_unconscious:
                                self._handle_combat_defeat()
                        break
            
            # Also update the snapshot in char_state for UI consistency
            char_data["current_hp"] = new_hp
            
            self._add_to_combat_log(f"{char_name} takes {amount} damage!")

    def _apply_spell_to_enemy(self, enemy: dict, amount: int, damage_type: str, spell_name: str):
        """Apply spell effect to an enemy"""
        enemy_name = enemy.get('name', 'Enemy')
        
        if damage_type == "healing":
            # Heal enemy (rare but possible)
            old_hp = enemy.get('current_hp', 0)
            max_hp = enemy.get('max_hp', 10)
            new_hp = min(old_hp + amount, max_hp)
            enemy['current_hp'] = new_hp
            actual_healing = new_hp - old_hp
            
            self._add_to_combat_log(f"{enemy_name} healed for {actual_healing} HP!")
        else:
            # Damage enemy
            old_hp = enemy.get('current_hp', 0)
            new_hp = max(0, old_hp - amount)
            enemy['current_hp'] = new_hp
            
            self._add_to_combat_log(f"{enemy_name} takes {amount} damage!")
            
            if new_hp <= 0:
                self._add_to_combat_log(f"{enemy_name} is defeated!")
                # Check victory
                if self._check_victory_conditions():
                    self._handle_combat_victory()

def initialize_combat_engine(game_state, event_manager, save_manager=None, item_manager=None):
    """
    Initialize CombatEngine following established engine pattern
    
    Args:
        game_state: GameState instance
        event_manager: EventManager instance
        
    Returns:
        CombatEngine: Initialized combat engine
    """
    return CombatEngine(event_manager, game_state, save_manager, item_manager)