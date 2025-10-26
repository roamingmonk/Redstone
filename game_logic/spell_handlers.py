# game_logic/spell_handlers.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import random  

class SpellHandler(ABC):
    """Base class for spell type handlers"""
    
    def __init__(self):
        self.movement_system = None  # Will be injected by CombatEngine

    @abstractmethod
    def calculate_affected_tiles(self, spell_data: dict, caster_pos: List[int], 
                                 target_pos: List[int], battlefield: dict) -> List[List[int]]:
        """Calculate which tiles are affected by this spell"""
        pass
    
    @abstractmethod
    def setup_animation(self, spell_data: dict, caster_pos: List[int], 
                       affected_tiles: List[List[int]]) -> Dict[str, Any]:
        """Set up animation data for this spell type"""
        pass
    
    @abstractmethod
    def get_valid_targets(self, spell_data: dict, caster_pos: List[int], 
                         battlefield: dict, characters: dict, enemies: list) -> List[List[int]]:
        """Get valid target positions for this spell"""
        pass


class SingleTargetSpellHandler(SpellHandler):
    """Handles single-target spells (Magic Dart, Cure Wounds, Inflict Wounds)"""
    
    def calculate_affected_tiles(self, spell_data, caster_pos, target_pos, battlefield):
        return [target_pos]
    
    def setup_animation(self, spell_data, caster_pos, affected_tiles):
        animation_id = spell_data.get('animation', 'projectile')
        elemental_type = spell_data.get('elemental_type', 'force')
        
        return {
            'type': animation_id,
            'start_pos': caster_pos,
            'end_pos': affected_tiles[0] if affected_tiles else caster_pos,
            'elemental_type': elemental_type
        }
    
    def create_particles(self, spell_data: dict, affected_tiles: List[List[int]]) -> list:
        """Create trail particles for projectiles"""
        import random
        
        # No particles for now, or add trail particles if desired
        return []

    def get_valid_targets(self, spell_data: dict, caster_pos: List[int], 
                     battlefield: dict, characters: dict, enemies: list) -> List[List[int]]:
        """Get valid single-target positions within range"""
        spell_range = spell_data.get('range', 1)
        target_type = spell_data.get('target_type', 'enemy')
        
        # # DEBUG: Show what we're searching for
        # print(f"🔍 get_valid_targets DEBUG:")
        # print(f"   Spell: {spell_data.get('name', 'Unknown')}")
        # print(f"   Range: {spell_range}")
        # print(f"   Target type: {target_type}")
        # print(f"   Caster pos: {caster_pos}")
        # print(f"   Available characters: {len(characters)}")
        #for char_id, char_state in characters.items():
            #print(f"      - {char_id}: {char_state.get('name')} at {char_state.get('position')} (alive: {char_state.get('is_alive', True)})")
        
        valid_targets = []
        
        # Check all positions within range
        for dx in range(-spell_range, spell_range + 1):
            for dy in range(-spell_range, spell_range + 1):
                target_pos = [caster_pos[0] + dx, caster_pos[1] + dy]
                
                # Check manhattan distance
                distance = abs(dx) + abs(dy)
                if distance > spell_range:
                    continue
                
                # Allow self-targeting for ally spells (like Cure Wounds)
                if distance == 0 and target_type != "ally":
                    continue  # Skip self for non-ally spells
                
                # Check if position has valid target based on target_type
                if target_type == "ally":
                    # Check party members (including self)
                    for char_id, char_state in characters.items():
                        if char_state['position'] == target_pos and char_state.get('is_alive', True):
                            
                            valid_targets.append(target_pos)
                            break
                elif target_type == "enemy":
                    # Check enemies
                    for enemy in enemies:
                        if enemy['position'] == target_pos and enemy.get('current_hp', 0) > 0:
                            valid_targets.append(target_pos)
                            break
        
        #print(f"   📋 Final valid targets: {valid_targets}")
        return valid_targets

class LineSpellHandler(SpellHandler):
    """Handles line spells (Lightning Bolt, Burning Hands)"""
    
    def calculate_affected_tiles(self, spell_data, caster_pos, target_pos, battlefield):
        # Calculate direction
        dx = 1 if target_pos[0] > caster_pos[0] else -1 if target_pos[0] < caster_pos[0] else 0
        dy = 1 if target_pos[1] > caster_pos[1] else -1 if target_pos[1] < caster_pos[1] else 0
        
        area_size = spell_data.get('area_size', 6)
        affected = []
        current = caster_pos.copy()
        
        for step in range(area_size):
            current = [current[0] + dx, current[1] + dy]
            
            # Check bounds and obstacles
            if not self._is_valid_tile(current, battlefield):
                break
            
            affected.append(current.copy())
        
        return affected
    
    def _is_valid_tile(self, pos: List[int], battlefield: dict) -> bool:
        """Check if tile is valid (in bounds, not blocked by walls/obstacles)"""
        dimensions = battlefield.get('dimensions', {'width': 8, 'height': 8})
        width = dimensions['width']
        height = dimensions['height']
        
        # Check bounds
        if not (0 <= pos[0] < width and 0 <= pos[1] < height):
            return False
        
        # Check walls using injected movement_system
        if self.movement_system and self.movement_system._is_wall_tile(pos[0], pos[1], battlefield):
            return False
        
        # Check sight-blocking obstacles
        terrain = battlefield.get('terrain', {})
        for obstacle in terrain.get('obstacles', []):
            if obstacle.get('position') == pos and obstacle.get('blocks_sight', False):
                return False
        
        return True
    
    def setup_animation(self, spell_data, caster_pos, affected_tiles):
        elemental_type = spell_data.get('elemental_type', 'lightning')
        animation_id = spell_data.get('animation', f'{elemental_type}_line')
        
        # Determine particle colors based on element
        particle_colors = self._get_particle_colors(elemental_type)
        
        return {
            'type': animation_id,
            'caster_pos': caster_pos,
            'tiles': affected_tiles,
            'elemental_type': elemental_type,
            'particle_colors': particle_colors
        }
    
    def _get_particle_colors(self, elemental_type):
        """Lookup table for particle colors by element"""
        color_map = {
            'fire': [(255, 150, 0), (255, 100, 0), (255, 200, 50)],
            'lightning': [(255, 255, 255), (200, 230, 255), (100, 200, 255)],
            'cold': [(150, 200, 255), (100, 150, 255), (200, 220, 255)],
            'acid': [(100, 255, 100), (150, 255, 50), (50, 200, 100)]
        }
        return color_map.get(elemental_type, [(255, 255, 255)])
    
    def get_valid_targets(self, spell_data: dict, caster_pos: List[int], 
                         battlefield: dict, characters: dict, enemies: list) -> List[List[int]]:
        """Get valid target positions for line spell (any position in the 8 cardinal/diagonal directions)"""
        spell_range = spell_data.get('area_size', 6)  # Line spells use area_size as max range
        
        valid_targets = []
        
        # For line spells, valid targets are ALL positions along 8 directions
        directions = [
            (0, -1),   # North
            (1, -1),   # Northeast
            (1, 0),    # East
            (1, 1),    # Southeast
            (0, 1),    # South
            (-1, 1),   # Southwest
            (-1, 0),   # West
            (-1, -1)   # Northwest
        ]
        
        dimensions = battlefield.get('dimensions', {'width': 8, 'height': 8})
        width = dimensions['width']
        height = dimensions['height']
        
        for dx, dy in directions:
            # Add ALL positions along this direction up to range
            for distance in range(1, spell_range + 1):
                target_pos = [
                    caster_pos[0] + (dx * distance),
                    caster_pos[1] + (dy * distance)
                ]
                
                # Check if in bounds
                if 0 <= target_pos[0] < width and 0 <= target_pos[1] < height:
                    valid_targets.append(target_pos)
        
        return valid_targets

class AreaSpellHandler(SpellHandler):
    """Handles area-of-effect spells (Fireball, Ice Storm)"""
    
    def calculate_affected_tiles(self, spell_data, caster_pos, target_pos, battlefield):
        area_size = spell_data.get('area_size', 3)
        half_size = area_size // 2
        affected = []
        
        for dx in range(-half_size, half_size + 1):
            for dy in range(-half_size, half_size + 1):
                pos = [target_pos[0] + dx, target_pos[1] + dy]
                affected.append(pos)
        
        return affected
    
    def setup_animation(self, spell_data, caster_pos, affected_tiles):
        animation_id = spell_data.get('animation', 'area_burst')
        
        # Calculate expansion delay based on distance from center
        center_pos = affected_tiles[0] if affected_tiles else caster_pos
        tile_data = []
    
        for tile_pos in affected_tiles:
            # Manhattan distance from center
            distance = abs(tile_pos[0] - center_pos[0]) + abs(tile_pos[1] - center_pos[1])
            
            # Random frame offset (0-9) for staggered animation
            frame_offset = random.randint(0, 9)
            
            tile_data.append({
                'position': tile_pos,
                'distance': distance,  # Add this
                'frame_offset': frame_offset,  # Add this
                'start_delay': distance * 0.08
            })
        
        return {
            'type': animation_id,
            'center_pos': center_pos,
            'tile_data': tile_data,
            'elemental_type': spell_data.get('elemental_type', 'fire')
        }

    def get_valid_targets(self, spell_data: dict, caster_pos: List[int], 
                         battlefield: dict, characters: dict, enemies: list) -> List[List[int]]:
        """Get valid target positions for area spell (any position within range)"""
        spell_range = spell_data.get('range', 7)
        
        valid_targets = []
        
        # For AOE spells, any position within range is valid
        for dx in range(-spell_range, spell_range + 1):
            for dy in range(-spell_range, spell_range + 1):
                target_pos = [caster_pos[0] + dx, caster_pos[1] + dy]
                
                # Check manhattan distance
                distance = abs(dx) + abs(dy)
                if distance > spell_range:
                    continue
                
                # All positions within range are valid for AOE
                valid_targets.append(target_pos)
        
        return valid_targets

class SelfAreaSpellHandler(SpellHandler):
    """Handles self-centered AOE spells (Bless, Mass Heal, etc.)"""
    
    def calculate_affected_tiles(self, spell_data, caster_pos, target_pos, battlefield):
        """Calculate tiles in radius around caster (ignores target_pos)"""
        area_size = spell_data.get('area_size', 6)
        affected = []
        
        # Circle around caster position
        for dx in range(-area_size, area_size + 1):
            for dy in range(-area_size, area_size + 1):
                # Manhattan distance
                distance = abs(dx) + abs(dy)
                if distance <= area_size:
                    pos = [caster_pos[0] + dx, caster_pos[1] + dy]
                    affected.append(pos)
        
        return affected
    
    def setup_animation(self, spell_data, caster_pos, affected_tiles):
        """Setup expanding radial animation from caster"""
        animation_id = spell_data.get('animation', 'area_burst')
        elemental_type = spell_data.get('elemental_type', 'radiant')
        
        tile_data = []
        for tile_pos in affected_tiles:
            distance = abs(tile_pos[0] - caster_pos[0]) + abs(tile_pos[1] - caster_pos[1])
            tile_data.append({
                'position': tile_pos,
                'distance': distance,
                'frame_offset': random.randint(0, 9),
                'start_delay': distance * 0.08
            })
        
        return {
            'type': animation_id,
            'center_pos': caster_pos,  # Animation centers on caster
            'tile_data': tile_data,
            'elemental_type': elemental_type,
            'hit': True
        }
    
    def get_valid_targets(self, spell_data, caster_pos, battlefield, characters, enemies):
        """For self-area spells, only the caster position is valid (click anywhere to cast)"""
        # Return caster position - spell auto-casts on self when selected
        return [caster_pos]

class SpellHandlerRegistry:
    """Registry to lookup spell handler by area_type"""
    
    def __init__(self):
        self._handlers = {
            'single': SingleTargetSpellHandler(),
            'line': LineSpellHandler(),
            'area': AreaSpellHandler(),
            'self_area': SelfAreaSpellHandler()
        }
    
    def get_handler(self, area_type: str) -> SpellHandler:
        """Get handler for given area type"""
        return self._handlers.get(area_type, SingleTargetSpellHandler())
    
    def register_handler(self, area_type: str, handler: SpellHandler):
        """Register custom handler"""
        self._handlers[area_type] = handler