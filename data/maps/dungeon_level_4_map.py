"""
Dungeon Level 4 - Cult Sanctum Upper
The cult's active headquarters. Living quarters, planning rooms, evidence of Marcus's leadership.

Visual tilemap is loaded from dungeon_level_4_tiles.tmj
This file contains game logic: spawn points, transitions, searchables, combat triggers
"""

# Map dimensions (must match TMJ file)
DUNGEON_L4_WIDTH = 22
DUNGEON_L4_HEIGHT = 22

# Named spawn points for different entrances
DUNGEON_L4_SPAWN_POINTS = {
    'from_level_3': (1, 1),         # Stairs up position (TMJ Details tile 40 at (1,1))
    'from_level_5': (19, 20),       # Stairs down position (TMJ Details tile 39 at (19,20))
    'default': (1, 1)
}

# Legacy support
DUNGEON_L4_SPAWN_X = DUNGEON_L4_SPAWN_POINTS['default'][0]
DUNGEON_L4_SPAWN_Y = DUNGEON_L4_SPAWN_POINTS['default'][1]

# === AREA TRANSITIONS ===
AREA_TRANSITIONS = {
    'stairs_to_level_3': {
        'entrance_tiles': [(1, 1), (2, 1), (1, 2)],   # Stairs up area (TMJ tile 40 at (1,1))
        'building_pos': [(1, 1)],
        'info': {
            'name': 'Ascending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_3_nav',
            'action': 'Return to Level 3',
            'requirements': {}
        }
    },
    'stairs_to_level_5': {
        'entrance_tiles': [(19, 20), (18, 20), (20, 20)],  # Stairs down area (TMJ tile 39 at (19,20))
        'building_pos': [(19, 20)],
        'info': {
            'name': 'Descending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_5_nav',
            'action': 'Descend to Portal Chamber',
            'requirements': {}
        }
    }
}

def get_transition_at_entrance(x, y):
    """Check if player is at area transition point"""
    for transition_id, transition_data in AREA_TRANSITIONS.items():
        if 'entrance_tiles' not in transition_data:
            continue
        if (x, y) in transition_data['entrance_tiles']:
            return transition_data.get('info')
    return None

# === SEARCHABLE OBJECTS ===
# Positions based on TMJ tilemap layout - tune locally after testing
# TMJ Details: chest tiles (46,47) at (6,6)/(7,6) and (11,17)/(12,17), debris (32) at (2,19)
SEARCHABLE_OBJECTS = {
    'cult_planning_table': {
        'search_tiles': [(6, 5), (7, 5), (6, 7), (7, 7)],
        'object_pos': [(6, 6), (7, 6)],
        'info': {
            'name': 'Cult Planning Table',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_planning',
            'flag_set': 'dungeon_l4_planning_examined',
            'one_time': True
        }
    },
    'marcus_study': {
        'search_tiles': [(11, 4), (11, 5), (12, 4), (12, 5)],
        'object_pos': [(11, 4)],
        'info': {
            'name': "Marcus's Study",
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_marcus_study',
            'flag_set': 'dungeon_l4_study_examined',
            'one_time': True
        }
    },
    'prison_cells': {
        'search_tiles': [(6, 14)],
        'object_pos': [(6, 14)],
        'info': {
            'name': 'Prison Cells',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_villager_cells',
            'flag_set': 'dungeon_l4_cells_examined',
            'one_time': True
        }
    },
    'cult_shrine': {
        'search_tiles': [(11, 16), (12, 16), (11, 18), (12, 18)],  # TMJ chest tiles (46,47) at (11,17),(12,17)
        'object_pos': [(11,16), (11, 17)],
        'info': {
            'name': 'Cult Shrine',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_shrine',
            'flag_set': 'dungeon_l4_shrine_examined',
            'one_time': True
        }
    },
    'ancient_chest': {
        'search_tiles': [(2, 20), (3, 19), (1, 19), (2, 18)],  # TMJ debris tile (32) at (2,19)
        'object_pos': [(2, 19)],
        'info': {
            'name': 'Ancient Chest',
            'interaction_type': 'searchable',
            'examine_dialogue': 'dungeon_level_4_chest',
            'loot_table': 'dungeon_level_4_chest_loot',
            'flag_set': 'dungeon_l4_chest_opened',
            'one_time': True
        }
    }
}

def get_searchable_at_position(x, y):
    """Check if player is near searchable object"""
    for obj_id, obj_data in SEARCHABLE_OBJECTS.items():
        if (x, y) in obj_data['search_tiles']:
            return obj_data['info']
    return None

# === COMBAT ENCOUNTERS ===
COMBAT_ENCOUNTERS = {
    'cult_patrol': {
        'trigger_tiles': [(2, 7), (3, 7), (2, 8), (3, 8)],
        'encounter_id': 'dungeon_l4_cult_patrol',
        'one_time': True,
        'completion_flag': 'dungeon_l4_encounter_1_complete',
        'repeatable': False,
        'chance': 1.0
    },
    'possessed_villagers': {
        'trigger_tiles': [(18, 15), (19, 15), (18, 16), (19, 16)],
        'encounter_id': 'dungeon_l4_possessed_villagers',
        'one_time': True,
        'completion_flag': 'dungeon_l4_encounter_2_complete',
        'repeatable': False,
        'chance': 1.0
    },
    'elite_guards': {
        'trigger_tiles': [(17, 19), (18, 19), (19, 19)],
        'encounter_id': 'dungeon_l4_elite_guards',
        'one_time': True,
        'completion_flag': 'dungeon_l4_encounter_3_complete',
        'repeatable': False,
        'chance': 1.0
    }
}

def get_combat_trigger(x, y):
    """Check if position triggers combat encounter"""
    for encounter_id, encounter_data in COMBAT_ENCOUNTERS.items():
        if (x, y) in encounter_data['trigger_tiles']:
            return encounter_data
    return None


# === LEGACY TILE FUNCTIONS ===
# Kept for backwards compatibility - visual rendering comes from dungeon_level_4_tiles.tmj

TILE_TYPES = {
    '#': 'wall',
    '.': 'floor',
    'U': 'stairs_up',
    'S': 'stairs_down',
    'P': 'pillar',
    '~': 'combat_zone',
    'C': 'planning_table',
    'M': 'study',
    'V': 'cells',
    'A': 'altar',
    'X': 'chest'
}

WALKABLE_TILES = {'floor', 'stairs_up', 'stairs_down', 'combat_zone', 'planning_table', 'study', 'cells', 'altar', 'chest'}

# ASCII map layout (legacy - visual comes from TMJ now)
DUNGEON_L4_MAP = [
    "######################",
    "#U...................#",  # Stairs up to Level 3
    "#....................#",
    "#...PP..........PP...#",
    "#....................#",
    "#.......C............#",  # Cult planning table (C)
    "#....................#",
    "#~~..................#",  # ENCOUNTER 1 - cult patrol
    "#~~..................#",
    "#....................#",
    "#............M.......#",  # Marcus's study (M)
    "#....................#",
    "#....................#",
    "#.....V..............#",  # Possessed villager cells (V)
    "#....................#",
    "#..................~~#",  # ENCOUNTER 2 - possessed villagers
    "#..................~~#",
    "#..........A.........#",  # Cult shrine (A)
    "#....................#",
    "#.X.............~~...#",  # Chest (X), ENCOUNTER 3 (boss area)
    "#..................S.#",  # Stairs down to Level 5
    "######################"
]

def get_tile_type(x, y, tile_grid=None):
    """Get tile type at coordinates"""
    if tile_grid:
        # New system: use provided tile grid
        if 0 <= y < len(tile_grid) and 0 <= x < len(tile_grid[0]):
            return tile_grid[y][x]
        return None
    else:
        # Legacy system: use ASCII map
        if 0 <= y < DUNGEON_L4_HEIGHT and 0 <= x < DUNGEON_L4_WIDTH:
            char = DUNGEON_L4_MAP[y][x]
            return TILE_TYPES.get(char, 'wall')
        return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable (legacy function)"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_tile_color(x, y):
    """Get color for tile rendering (legacy function)"""
    tile_type = get_tile_type(x, y)
    TILE_COLORS = {
        'wall': (60, 60, 60),
        'floor': (40, 30, 25),
        'stairs_up': (100, 100, 150),
        'stairs_down': (150, 50, 50),
        'pillar': (80, 80, 80),
        'combat_zone': (80, 40, 40),
        'planning_table': (100, 80, 60),
        'study': (60, 50, 80),
        'cells': (70, 70, 50),
        'altar': (90, 50, 90),
        'chest': (150, 120, 50)
    }
    return TILE_COLORS.get(tile_type, (50, 50, 50))
