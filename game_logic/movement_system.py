# game_logic/movement_system.py
"""
Movement System - Pathfinding and animated movement for tactical combat
Handles both pathfinding logic and smooth visual transitions
"""
import time
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import deque

class MovementSystem:
    """
    Unified movement system that handles both pathfinding and animation
    
    Responsibilities:
    - Pathfinding with BFS algorithm
    - Movement validation considering obstacles
    - Smooth animation between grid positions
    - Special movement effects for incorporeal units
    """
    
    def __init__(self, combat_engine):
        """Initialize with reference to combat engine for terrain data"""
        self.combat_engine = combat_engine
        # Dictionary to track entity movement animations
        self.entity_movements = {}
        # Movement animation speed
        self.move_speed = 8.0  # Tiles per second

    def get_movement_range(self, entity_data: Dict) -> int:
        """
        Calculate movement range for an entity
        Central authority for movement speed calculation
        
        Args:
            entity_data: Character state dict or enemy instance dict
            
        Returns:
            Movement range in tiles
        """
        # Check if this is a character (has character_data nested)
        if 'character_data' in entity_data:
            # Characters don't have movement_speed field yet - use default
            # TODO: Add movement_speed to character creation
            # TODO: Check for equipment bonuses, status effects
            return 4  # Default player speed
        
        # Check if this is an enemy (has movement dict)
        elif 'movement' in entity_data:
            movement_dict = entity_data.get('movement', {})
            return movement_dict.get('speed', 3)  # Default enemy speed
        
        # Fallback
        return 3
    
    def can_reach(self, start_pos: List[int], end_pos: List[int], 
                  movement_range: int, can_phase: bool = False, 
                  is_player: bool = False) -> bool:
        """
        Check if entity can reach destination within movement range
        
        Args:
            start_pos: Starting position [x, y]
            end_pos: Destination position [x, y]
            movement_range: Maximum tiles entity can move
            can_phase: Whether entity can move through obstacles
            is_player: Whether this is a player character
            
        Returns:
            True if destination is reachable, False otherwise
        """
        # Quick distance check first
        distance = abs(end_pos[0] - start_pos[0]) + abs(end_pos[1] - start_pos[1])
        if distance > movement_range:
            return False  # Too far even in straight line
        
        # Check if end position is in valid moves
        valid_moves = self.get_valid_moves(start_pos, movement_range, can_phase, is_player)
        return end_pos in valid_moves


    # ========== PATHFINDING METHODS ==========
    
    def get_valid_moves(self, position, movement_range, can_phase=False, is_player=False):
        """Get valid moves for an entity within movement_range"""
        if not position or len(position) != 2:
            return []
        
        # Use BFS to find reachable positions
        valid_moves = []
        visited = {tuple(position)}
        queue = [(position, 0)]  # (position, distance so far)
        
        while queue:
            current, dist = queue.pop(0)
            
            # If we're at movement range, don't explore further
            if dist >= movement_range:
                continue
            
            # Check adjacent positions (4 directions)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = current[0] + dx, current[1] + dy
                next_pos = [next_x, next_y]
                next_pos_tuple = (next_x, next_y)
                
                # Skip if already visited
                if next_pos_tuple in visited:
                    continue
                
                # Check if position is valid
                if not self._is_valid_position(next_x, next_y, can_phase, is_player):
                    continue
                
                # Add to valid moves and visited
                valid_moves.append(next_pos)
                visited.add(next_pos_tuple)
                
                # Continue BFS
                queue.append((next_pos, dist + 1))
        
        return valid_moves
        
    def find_path(self, start_pos: List[int], end_pos: List[int], can_phase: bool = False, is_player: bool = False) -> Optional[List[List[int]]]:
        """
        Find shortest path from start to end position
        Uses Breadth-First Search for pathfinding
        
        Args:
            start_pos: Starting position [x, y]
            end_pos: Destination position [x, y]
            can_phase: Whether entity can move through obstacles
            is_player: Whether this is a player character (allows moving through allies)
            
        Returns:
            List of positions forming the path, or None if no path exists
        """
        # Validate positions
        if not start_pos or not end_pos:
            print("DEBUG: Invalid positions")
            return None

        # Special handling for incorporeal entities
        if can_phase:
            # Incorporeal entities can phase through obstacles - direct path
            path = []
            current_x, current_y = start_pos
            end_x, end_y = end_pos
            
            # Build path step by step toward destination
            while current_x != end_x or current_y != end_y:
                path.append([current_x, current_y])
                
                # Move one step toward destination
                if current_x < end_x:
                    current_x += 1
                elif current_x > end_x:
                    current_x -= 1
                elif current_y < end_y:
                    current_y += 1
                elif current_y > end_y:
                    current_y -= 1
            
            # Add final position
            path.append([end_x, end_y])
            return path

        # Check if start and end are the same
        if start_pos == end_pos:
            print("DEBUG: Start and end are the same position")
            return [start_pos]  # Return just the position

        if not start_pos or not end_pos or len(start_pos) != 2 or len(end_pos) != 2:
            return None
            
        # Convert to tuples for hashability
        start_tuple = tuple(start_pos)
        end_tuple = tuple(end_pos)
        
        # Check if start and end are the same
        if start_tuple == end_tuple:
            return [list(start_tuple)]
            
        # BFS queue: (position, path so far)
        queue = deque([(start_tuple, [start_tuple])])
        visited = {start_tuple}
        
        while queue:
            current_tuple, path = queue.popleft()
            
            # Convert current position back to list for easier use
            current_pos = [current_tuple[0], current_tuple[1]]
            
            # Check adjacent tiles
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = current_pos[0] + dx, current_pos[1] + dy
                next_tuple = (next_x, next_y)
                
                # Skip if already visited
                if next_tuple in visited:
                    continue
                    
                # Skip if not a valid movement position - PASS is_player HERE
                if not self._is_valid_position(next_x, next_y, can_phase, is_player):
                    continue
                    
                # Create new path with this position
                next_path = path + [next_tuple]
                
                # Check if we've reached the destination
                if next_tuple == end_tuple:
                    # Convert path from tuples back to lists
                    return [list(pos) for pos in next_path]
                    
                # Mark as visited and add to queue
                visited.add(next_tuple)
                queue.append((next_tuple, next_path))
        
        # No path found
        return None
    
    def _is_valid_position(self, x: int, y: int, can_phase: bool, is_player: bool = False):
        """Check if a position is valid for movement"""
        # Check battlefield boundaries
        bf = self.combat_engine.combat_data.get("battlefield", {})
        dimensions = bf.get("dimensions", {})
        width = dimensions.get("width", 12)
        height = dimensions.get("height", 8)
        
        if x < 0 or x >= width or y < 0 or y >= height:
            return False
        
        # Determine movement type for terrain checking
        movement_type = "incorporeal" if can_phase else "ground"
        
        # Check terrain using our new methods (no occupation check yet)
        if not can_phase:
            # Check for walls and obstacles using local methods
            if self._is_wall_tile(x, y, bf):
                return False
                    
            if self._is_obstacle_tile(x, y, bf):
                return False
        
        # Check for other entities (still using CombatEngine data)
        position = [x, y]
        
        # For player characters AND PARTY MEMBERS, allow moving through other party members
        if is_player:
            # Only check for enemy units
            enemy_instances = self.combat_engine.combat_data.get("enemy_instances", [])
            for enemy in enemy_instances:
                if enemy.get("current_hp", 0) > 0:  # Only check living enemies
                    if enemy.get("position") == position:
                        return False
            # Allow moving through allies
            return True
        else:
            # For enemies, check all occupied tiles
            for char_id, char_state in self.combat_engine.character_states.items():
                if char_state.get('is_alive', True) and char_state.get('position') == position:
                    return False
                    
            for enemy in self.combat_engine.combat_data.get("enemy_instances", []):
                if enemy.get("current_hp", 0) <= 0:
                    continue
                
                # Check BOTH actual position AND intended position (during animations)
                enemy_pos = enemy.get("position")
                enemy_intended = enemy.get("intended_position")
                
                if enemy_pos == position or enemy_intended == position:
                    return False
        
        return True
    # ========== TERRAIN VALIDATION METHODS ==========
    
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
    
    def _point_on_line_segment(self, px: int, py: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if point is on line segment"""
        if x1 == x2:  # Vertical line
            return px == x1 and min(y1, y2) <= py <= max(y1, y2)
        elif y1 == y2:  # Horizontal line
            return py == y1 and min(x1, x2) <= px <= max(x1, x2)
        return False
    
    def is_tile_walkable(self, x: int, y: int, battlefield: Dict, movement_type: str = "ground", 
                         check_occupation_callback=None) -> bool:
        """
        Check if tile at position is walkable
        
        Args:
            x, y: Tile coordinates
            battlefield: Battlefield data dict
            movement_type: Type of movement (ground, flying, incorporeal)
            check_occupation_callback: Function to check if tile is occupied by units
            
        Returns:
            bool: Whether the tile is walkable for the given movement type
        """
        # Check walls - impassable for all except incorporeal
        if self._is_wall_tile(x, y, battlefield) and movement_type != "incorporeal":
            return False
        
        # Check obstacles - impassable for ground units but not incorporeal
        if self._is_obstacle_tile(x, y, battlefield) and movement_type != "incorporeal":
            return False
        
        # Check if another unit occupies this tile (if callback provided)
        if check_occupation_callback and check_occupation_callback(x, y):
            return False
        
        return True


    # ========== MOVEMENT ANIMATION METHODS ==========
    
    def start_entity_movement(self, entity_id: str, start_pos: List[int], path: List[List[int]]):
        """Begin animated movement for entity"""
        print(f"DEBUG: Starting movement for {entity_id} from {start_pos} with path {path}")
        
        if not path or len(path) < 2:  # Need at least 2 points for a real path
            print(f"DEBUG: Invalid path - too short: {path}")
            return False
            
        # Make sure the target position is different from the start
        target_pos = path[-1]  # Get the last position in the path
        if start_pos == target_pos:
            print(f"DEBUG: Start and target are the same: {start_pos}")
            return False
        
        # Set up movement info
        self.entity_movements[entity_id] = {
            'path': path,
            'current_index': 1,
            'moving': True,
            'start_pos': start_pos,
            'target_pos': path[1] if path else start_pos,  # Make sure this isn't the same as start_pos
            'start_time': time.time(),
            'move_speed': 8.0
        }
        
        # Print movement details
        print(f"DEBUG: Movement set up: {self.entity_movements[entity_id]}")
        
        return True
    
    def update_movements(self):
        """Update all entity movements for this frame"""
        #print(f"DEBUG: Updating movements - {len(self.entity_movements)} active movements")
        
        current_time = time.time()
        entities_completed = []
        
        for entity_id, movement in self.entity_movements.items():
            if not movement['moving']:
                entities_completed.append(entity_id)
                continue
            
            #print(f"DEBUG: Animating movement for {entity_id}")
            
            # Get entity reference
            entity = self._get_entity_by_id(entity_id)
            if not entity:
                print(f"DEBUG: Entity {entity_id} not found!")
                entities_completed.append(entity_id)
                continue
            
            # Calculate progress
            elapsed = current_time - movement['start_time']
            progress = min(elapsed * movement['move_speed'], 1.0)
            #print(f"DEBUG: Movement progress: {progress:.2f}")
            
            # Update visual position
            start = movement['start_pos']
            target = movement['target_pos']
            
            # Calculate interpolated position
            visual_x = start[0] + (target[0] - start[0]) * progress
            visual_y = start[1] + (target[1] - start[1]) * progress
            
            # Update entity's visual properties
            #print(f"DEBUG: Setting visual position to ({visual_x:.2f}, {visual_y:.2f})")
            
            # For character_states
            if entity_id in self.combat_engine.character_states:
                char_state = self.combat_engine.character_states[entity_id]
                char_state['visual_x'] = visual_x
                char_state['visual_y'] = visual_y
            # For enemy instances
            else:
                entity['visual_x'] = visual_x
                entity['visual_y'] = visual_y
            
            # Handle completed segments
            if progress >= 1.0:
                # Update actual position to the target position
                if entity_id in self.combat_engine.character_states:
                    self.combat_engine.character_states[entity_id]['position'] = target
                else:
                    entity['position'] = target
                
                # CRITICAL FIX: Move to next segment of the path
                movement['current_index'] += 1
                
                # Check if we've reached the end of the path
                if movement['current_index'] >= len(movement['path']):
                    #print(f"DEBUG: Movement completed for {entity_id}")
                    entities_completed.append(entity_id)
                    movement['moving'] = False
                else:
                    # Set up for the next segment
                    movement['start_pos'] = target
                    movement['target_pos'] = movement['path'][movement['current_index']]
                    movement['start_time'] = current_time
        
        # Remove completed movements
        for entity_id in entities_completed:
            if entity_id in self.entity_movements:
                del self.entity_movements[entity_id]
        
    def is_entity_moving(self, entity_id: str) -> bool:
        """Check if entity is currently moving"""
        return entity_id in self.entity_movements and self.entity_movements[entity_id]['moving']
    
    def get_all_moving_entities(self) -> List[str]:
        """Get list of all entity IDs currently in motion"""
        return [eid for eid, data in self.entity_movements.items() if data['moving']]
    
    def cancel_entity_movement(self, entity_id: str) -> None:
        """Cancel movement for entity"""
        if entity_id in self.entity_movements:
            del self.entity_movements[entity_id]
    
    # ========== COMBAT ENGINE INTEGRATION ==========
    
    def validate_move(self, entity, target_position: List[int]) -> Tuple[bool, Optional[List[List[int]]]]:
        """
        Validate if an entity can move to target position
        
        Args:
            entity: Entity object to move
            target_position: Target position [x, y]
            
        Returns:
            Tuple of (is_valid, path_to_follow)
        """
        if not entity or not hasattr(entity, 'position'):
            return False, None
            
        # Get entity's current position
        start_pos = entity.position
        
        # Check if entity can phase through walls
        can_phase = False
        if hasattr(entity, 'has_ability') and callable(entity.has_ability):
            can_phase = entity.has_ability("incorporeal")
        
        # Get movement range
        movement_range = 3  # Default
        if hasattr(entity, 'get_stat') and callable(entity.get_stat):
            movement_range = entity.get_stat('speed')
        
        # Check if this is a player character
        is_player_character = hasattr(entity, 'id') and entity.id in self.combat_engine.character_states
            
        # Find path to destination
        path = self.find_path(start_pos, target_position, can_phase, is_player_character)
        
        # Check if path exists and is within movement range
        if path and len(path) - 1 <= movement_range:  # -1 because path includes start
            return True, path
            
        return False, None
    
    def move_entity(self, entity, target_position: List[int]) -> bool:
        """
        Move entity to target position with animation
        
        Args:
            entity: Entity to move
            target_position: Target position [x, y]
            
        Returns:
            True if movement started successfully
        """
        # Validate the move
        valid, path = self.validate_move(entity, target_position)
        
        if not valid or not path:
            return False
            
        # Get entity ID
        entity_id = entity.id if hasattr(entity, 'id') else None
        if not entity_id:
            return False
            
        # Check if entity can phase through walls
        is_incorporeal = False
        if hasattr(entity, 'has_ability') and callable(entity.has_ability):
            is_incorporeal = entity.has_ability("incorporeal")
            
        # Start movement animation
        success = self.start_entity_movement(entity_id, entity.position, path)
        
        if success and is_incorporeal:
            # Mark movement as incorporeal for special effects
            self.entity_movements[entity_id]['is_incorporeal'] = True
            
        if success:
            # Update entity's intended destination
            entity.intended_x = target_position[0]
            entity.intended_y = target_position[1]
            
        return success
    
    # Around line 380 in movement_system.py
    def _get_entity_by_id(self, entity_id: str) -> Any:
        """Find entity by ID in combat engine data"""
        # Check character states first
        if entity_id in self.combat_engine.character_states:
            return self.combat_engine.character_states[entity_id]
                
        # Check enemy instances
        for enemy in self.combat_engine.combat_data.get("enemy_instances", []):
            if enemy.get("instance_id") == entity_id:
                return enemy       
        return None

# Create global instance
_movement_system_instance = None

def get_movement_system(combat_engine=None):
    """Get or create the global movement system instance"""
    global _movement_system_instance
    if _movement_system_instance is None and combat_engine is not None:
        _movement_system_instance = MovementSystem(combat_engine)
    return _movement_system_instance