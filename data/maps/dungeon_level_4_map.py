"""
Dungeon Level 4 - Cult Sanctum Upper
The cult's active headquarters. Living quarters, planning rooms, evidence of Marcus's leadership.
"""

# Map dimensions
DUNGEON_L4_WIDTH = 22
DUNGEON_L4_HEIGHT = 22

# Starting position (entering from Level 3 - at top stairs)
DUNGEON_L4_SPAWN_X = 12
DUNGEON_L4_SPAWN_Y = 1

# Spawn points for different entry methods
DUNGEON_L4_SPAWN_POINTS = {
    'from_level_3': (12, 1),        # Top of map, at stairs up 'U'
    'from_level_5': (18, 20),       # Bottom of map, at stairs down 'S'
    'default': (12, 1)
}

# Map Grid
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

# Tile definitions
WALKABLE_TILES = {'.', 'U', 'S', '~', 'C', 'M', 'V', 'A', 'X'}
BLOCKED_TILES = {'#', 'P'}

# Color mapping
TILE_COLORS = {
    '#': (60, 60, 60),      # Dark gray walls
    '.': (40, 30, 25),      # Dark brown floor
    'U': (100, 100, 150),   # Blue stairs up
    'S': (150, 50, 50),     # Red stairs down
    'P': (80, 80, 80),      # Gray pillars
    '~': (80, 40, 40),      # Dark red combat zones
    'C': (100, 80, 60),     # Brown table
    'M': (60, 50, 80),      # Purple study
    'V': (70, 70, 50),      # Yellowish cells
    'A': (90, 50, 90),      # Purple shrine
    'X': (150, 120, 50)     # Golden chest
}

# Searchable objects (FIXED to match Level 2/3 pattern)
SEARCHABLE_OBJECTS = {
    'cult_planning_table': {
        'search_tiles': [(7, 5), (6, 5), (8, 5)],
        'object_pos': [(7, 5)],
        'info': {
            'name': 'Cult Planning Table',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_planning',
            'flag_set': 'dungeon_l4_planning_examined',
            'one_time': True
        }
    },
    'marcus_study': {
        'search_tiles': [(13, 10), (12, 10), (14, 10)],
        'object_pos': [(13, 10)],
        'info': {
            'name': 'Marcus\'s Study',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_marcus_study',
            'flag_set': 'dungeon_l4_study_examined',
            'one_time': True
        }
    },
    'prison_cells': {
        'search_tiles': [(8, 13), (7, 13), (9, 13)],
        'object_pos': [(8, 13)],
        'info': {
            'name': 'Prison Cells',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_villager_cells',
            'flag_set': 'dungeon_l4_cells_examined',
            'one_time': True
        }
    },
    'cult_shrine': {
        'search_tiles': [(11, 17), (10, 17), (12, 17)],
        'object_pos': [(11, 17)],
        'info': {
            'name': 'Cult Shrine',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_4_shrine',
            'flag_set': 'dungeon_l4_shrine_examined',
            'one_time': True
        }
    },
    'ancient_chest': {
        'search_tiles': [(2, 19), (1, 19), (3, 19)],
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

# Combat encounters
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

# Area transitions (FIXED to match Level 2/3 nested structure)
AREA_TRANSITIONS = {
    'stairs_to_level_3': {
        'entrance_tiles': [(12, 1), (11, 1), (13, 1)],
        'building_pos': [(12, 1)],
        'info': {
            'name': 'Ascending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_3_nav',
            'action': 'Return to Level 3',
            'requirements': {}
        }
    },
    'stairs_to_level_5': {
        'entrance_tiles': [(18, 20), (17, 20), (19, 20)],
        'building_pos': [(18, 20)],
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

def get_tile_type(x, y):
    """Get the tile character at coordinates."""
    if 0 <= y < len(DUNGEON_L4_MAP) and 0 <= x < len(DUNGEON_L4_MAP[y]):
        return DUNGEON_L4_MAP[y][x]
    return '#'

def is_walkable(x, y):
    """Check if a tile is walkable."""
    tile = get_tile_type(x, y)
    return tile in WALKABLE_TILES

def get_tile_color(x, y):
    """
    Get color for tile rendering
    These are PLACEHOLDER colors for testing
    """
    tile_char = get_tile_type(x, y)
    return TILE_COLORS.get(tile_char, (50, 50, 50))