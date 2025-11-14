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

# Searchable objects
SEARCHABLES = {
    (7, 5): {
        'name': 'Cult Planning Table',
        'examine_dialogue': 'dialogue_dungeon_level_4_planning',
        'flag_set': 'dungeon_l4_planning_examined'
    },
    (13, 10): {
        'name': 'Marcus\'s Study',
        'examine_dialogue': 'dialogue_dungeon_level_4_marcus_study',
        'flag_set': 'dungeon_l4_study_examined'
    },
    (8, 13): {
        'name': 'Prison Cells',
        'examine_dialogue': 'dialogue_dungeon_level_4_villager_cells',
        'flag_set': 'dungeon_l4_cells_examined'
    },
    (11, 17): {
        'name': 'Cult Shrine',
        'examine_dialogue': 'dialogue_dungeon_level_4_shrine',
        'flag_set': 'dungeon_l4_shrine_examined'
    },
    (2, 19): {
        'name': 'Ancient Chest',
        'examine_dialogue': 'dialogue_dungeon_level_4_chest',
        'flag_set': 'dungeon_l4_chest_opened'
    }
}

# Combat encounters
COMBAT_TRIGGERS = {
    (2, 7): {
        'encounter_id': 'dungeon_l4_cult_patrol',
        'completion_flag': 'dungeon_l4_encounter_1_complete'
    },
    (3, 7): {
        'encounter_id': 'dungeon_l4_cult_patrol',
        'completion_flag': 'dungeon_l4_encounter_1_complete'
    },
    (2, 8): {
        'encounter_id': 'dungeon_l4_cult_patrol',
        'completion_flag': 'dungeon_l4_encounter_1_complete'
    },
    (3, 8): {
        'encounter_id': 'dungeon_l4_cult_patrol',
        'completion_flag': 'dungeon_l4_encounter_1_complete'
    },
    (18, 15): {
        'encounter_id': 'dungeon_l4_possessed_villagers',
        'completion_flag': 'dungeon_l4_encounter_2_complete'
    },
    (19, 15): {
        'encounter_id': 'dungeon_l4_possessed_villagers',
        'completion_flag': 'dungeon_l4_encounter_2_complete'
    },
    (18, 16): {
        'encounter_id': 'dungeon_l4_possessed_villagers',
        'completion_flag': 'dungeon_l4_encounter_2_complete'
    },
    (19, 16): {
        'encounter_id': 'dungeon_l4_possessed_villagers',
        'completion_flag': 'dungeon_l4_encounter_2_complete'
    },
    (18, 19): {
        'encounter_id': 'dungeon_l4_elite_guards',
        'completion_flag': 'dungeon_l4_encounter_3_complete'
    },
    (19, 19): {
        'encounter_id': 'dungeon_l4_elite_guards',
        'completion_flag': 'dungeon_l4_encounter_3_complete'
    },
    (17, 19): {
        'encounter_id': 'dungeon_l4_elite_guards',
        'completion_flag': 'dungeon_l4_encounter_3_complete'
    }
}

# Transitions
TRANSITIONS = {
    (10, 1): {
        'target_screen': 'dungeon_level_3_nav',
        'action': 'go up stairs to Level 3',
        'direction': 'north'
    },
    (18, 20): {
        'target_screen': 'dungeon_level_5_nav',
        'action': 'descend to Portal Chamber',
        'direction': 'south',
        'requires_flag': 'dungeon_level_4_complete',
        'blocked_message': 'The passage is sealed by dark magic. You must defeat the elite guards first.'
    }
}

def get_tile_type(x, y):
    """Get the tile character at coordinates."""
    if 0 <= y < len(DUNGEON_L4_MAP) and 0 <= x < len(DUNGEON_L4_MAP[y]):
        return DUNGEON_L4_MAP[y][x]
    return '#'

def is_walkable(x, y):
    """Check if a tile is walkable."""
    tile = get_tile_type(x, y)
    return tile in WALKABLE_TILES

def get_tile_color(tile_char):
    """Get the color for a tile character."""
    return TILE_COLORS.get(tile_char, (50, 50, 50))

def get_transition_info(x, y):
    """Get transition info at position."""
    return TRANSITIONS.get((x, y))

def get_searchable_at_position(x, y):
    """Get searchable object at position."""
    return SEARCHABLES.get((x, y))

def get_combat_trigger(x, y):
    """Get combat trigger at position."""
    return COMBAT_TRIGGERS.get((x, y))