# utils/npc_manager.py
"""
NPC Manager - Singleton utility for NPC spawning, state, and interactions
Follows TileGraphicsManager pattern for consistency
"""

import pygame
from utils.constants import *

class NPCManager:
    """Manages NPC spawning, state, and interaction across all locations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - ensures single instance"""
        if cls._instance is None:
            cls._instance = super(NPCManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once (singleton pattern)
        if NPCManager._initialized:
            return
        
        # Cache for loaded NPC definitions per location
        self.location_npcs = {}
        
        # Sprite cache (reuses TileGraphicsManager for actual sprites)
        from utils.tile_graphics import get_tile_graphics_manager
        self.graphics = get_tile_graphics_manager()
        
        NPCManager._initialized = True
        print("👥 NPC Manager initialized (singleton)")
    
    def load_location_npcs(self, location_id):
        """
        Load NPC definitions for a location
        
        Args:
            location_id: 'redstone_town', 'swamp_church', etc.
        
        Returns:
            Dict of NPC definitions
        """
        # Skip if already cached
        if location_id in self.location_npcs:
            return self.location_npcs[location_id]
        
        # Import location-specific NPC data
        try:
            if location_id == 'redstone_town':
                from data.maps.redstone_town_map import get_location_npcs
                npcs = get_location_npcs()
                self.location_npcs[location_id] = npcs
                print(f"✅ Loaded {len(npcs)} NPCs for {location_id}")
                return npcs
            # Add more locations here as needed
        except (ImportError, AttributeError) as e:
            print(f"⚠️ No NPCs defined for {location_id}: {e}")
            self.location_npcs[location_id] = {}
            return {}
    
    def get_active_npcs(self, location_id, game_state):
        """
        Get list of NPCs that should currently appear at this location
        
        Args:
            location_id: Location identifier
            game_state: Current game state (for conditions, overrides)
        
        Returns:
            List of dicts with NPC data including calculated position
        """
        # Load NPC definitions for location
        npc_definitions = self.load_location_npcs(location_id)
        
        active_npcs = []
        
        for npc_id, npc_data in npc_definitions.items():
            # Check spawn conditions
            if self.check_spawn_conditions(npc_data.get('conditions'), game_state):
                # Copy NPC data and add ID
                npc = npc_data.copy()
                npc['id'] = npc_id
                
                # Check for position override
                if hasattr(game_state, 'npc_position_overrides'):
                    key = f"{location_id}_{npc_id}"
                    if key in game_state.npc_position_overrides:
                        npc['current_position'] = game_state.npc_position_overrides[key]
                    else:
                        npc['current_position'] = npc['default_position']
                else:
                    npc['current_position'] = npc['default_position']
                
                active_npcs.append(npc)
        
        return active_npcs
    
    def get_npc_at_position(self, x, y, location_id, game_state):
        """
        Check if there's an interactable NPC at given position
        
        Args:
            x, y: Player position
            location_id: Current location
            game_state: Game state
        
        Returns:
            NPC dict if found, None otherwise
        """
        active_npcs = self.get_active_npcs(location_id, game_state)
        
        for npc in active_npcs:
            if (x, y) in npc.get('interaction_tiles', []):
                return npc
        
        return None
    
    def check_spawn_conditions(self, conditions, game_state):
        """
        Evaluate whether NPC should spawn based on conditions
        
        Args:
            conditions: Dict or None
        
        Returns:
            Boolean - should NPC appear
        """
        if conditions is None:
            return True
        
        # Check quest conditions using existing quest_manager
        if 'quest_active' in conditions:
            quest_id = conditions['quest_active']
            if hasattr(game_state, 'quest_manager'):
                quest = game_state.quest_manager.quests.get(quest_id)
                if not quest or quest.status != "active":
                    return False
            else:
                return False
        
        if 'quest_complete' in conditions:
            quest_id = conditions['quest_complete']
            if hasattr(game_state, 'quest_manager'):
                quest = game_state.quest_manager.quests.get(quest_id)
                if not quest or quest.status != "completed":
                    return False
            else:
                return False
        
        if 'not_quest_complete' in conditions:
            quest_id = conditions['not_quest_complete']
            if hasattr(game_state, 'quest_manager'):
                quest = game_state.quest_manager.quests.get(quest_id)
                if quest and quest.status == "completed":
                    return False
            # If quest doesn't exist, condition passes
        
        # Check time conditions
        if 'time_of_day' in conditions:
            required_time = conditions['time_of_day']
            current_time = getattr(game_state, 'time_of_day', 'day')
            if isinstance(required_time, list):
                if current_time not in required_time:
                    return False
            else:
                if current_time != required_time:
                    return False
        
        if 'day_of_week' in conditions:
            required_days = conditions['day_of_week']
            current_day = getattr(game_state, 'current_day', 'monday')
            if isinstance(required_days, list):
                if current_day not in required_days:
                    return False
            else:
                if current_day != required_days:
                    return False
        
        # All conditions passed
        return True
    
    def update_npc_position(self, npc_id, location_id, new_x, new_y, game_state):
        """Update NPC position (for movement or scripted events)"""
        if not hasattr(game_state, 'npc_position_overrides'):
            game_state.npc_position_overrides = {}
        
        key = f"{location_id}_{npc_id}"
        game_state.npc_position_overrides[key] = (new_x, new_y)
    
    def mark_npc_talked(self, npc_id, game_state):
        """Mark that player has talked to this NPC today"""
        if not hasattr(game_state, 'npcs_talked_today'):
            game_state.npcs_talked_today = set()
        
        game_state.npcs_talked_today.add(npc_id)
    
    def get_npc_sprite(self, sprite_type, direction='down'):
        """
        Get sprite for NPC rendering
        
        Args:
            sprite_type: 'henrik', 'guard', 'merchant', 'noble', etc.
            direction: 'up', 'down', 'left', 'right'
        
        Returns:
            pygame.Surface (32x32)
        """
        return self.graphics.get_npc_sprite(sprite_type)
    
    def get_npc_stats(self):
        """Debug statistics"""
        return {
            'locations_loaded': len(self.location_npcs),
            'total_npc_definitions': sum(len(npcs) for npcs in self.location_npcs.values())
        }

# Singleton accessor
_npc_manager = None

def get_npc_manager():
    """Get the shared NPC manager instance"""
    global _npc_manager
    if _npc_manager is None:
        _npc_manager = NPCManager()
    return _npc_manager