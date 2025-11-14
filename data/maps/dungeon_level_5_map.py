"""
Dungeon Level 5 - Portal Chamber
The deepest level. Site of the void portal and final confrontation.
Features Marcus encounter and final boss fight.
"""

# Map dimensions
DUNGEON_L5_WIDTH = 24
DUNGEON_L5_HEIGHT = 24

# Starting position (entering from Level 4 - at top stairs)
DUNGEON_L5_SPAWN_X = 12
DUNGEON_L5_SPAWN_Y = 1

# Spawn points for different entry methods
DUNGEON_L5_SPAWN_POINTS = {
    'from_level_4': (12, 1),        # Top of map, at stairs up 'U'
    'default': (12, 1)
}
# Map Grid - Portal Chamber
DUNGEON_L5_MAP = [
    "########################",
    "############U###########",  # Stairs up to Level 4
    "########################",
    "###..................###",
    "##..PP............PP..##",
    "##....................##",
    "#.....................##",
    "#....M................##",  # Marcus confrontation zone (M)
    "#.....................##",
    "##....................##",
    "##..PP............PP..##",
    "###..................###",
    "###.......RRR........###",  # Ritual circle (R)
    "###......RRRRR.......###",
    "###.......RRR........###",
    "####.................###",
    "####.....PPPPP.......###",
    "####.....P~~~P.......###",  # Portal area - FINAL BOSS
    "####.....P~~~P.......###",
    "####.....PPPPP.......###",
    "#####................###",
    "######..............####",
    "#######............#####",
    "########################"
]

# Tile definitions
WALKABLE_TILES = {'.', 'U', 'M', 'R', '~'}
BLOCKED_TILES = {'#', 'P'}

# Color mapping
TILE_COLORS = {
    '#': (30, 30, 40),      # Very dark walls
    '.': (25, 20, 30),      # Dark purple floor
    'U': (100, 100, 150),   # Blue stairs up
    'P': (50, 50, 60),      # Dark pillars
    'M': (80, 50, 50),      # Red zone - Marcus
    'R': (60, 40, 80),      # Purple ritual circle
    '~': (100, 40, 100)     # Bright purple portal
}

# Searchable objects
SEARCHABLES = {
    (12, 13): {
        'name': 'Ancient Ritual Circle',
        'examine_dialogue': 'dialogue_dungeon_level_5_ritual_circle',
        'flag_set': 'dungeon_l5_ritual_examined'
    },
    (11, 18): {
        'name': 'Void Portal',
        'examine_dialogue': 'dialogue_dungeon_level_5_portal',
        'flag_set': 'dungeon_l5_portal_examined',
        'requires_flag': 'marcus_confrontation_complete'
    }
}

# Combat encounters
COMBAT_TRIGGERS = {
    (8, 7): {
        'encounter_id': 'dungeon_l5_marcus_confrontation',
        'completion_flag': 'marcus_confrontation_complete',
        'one_time': True
    },
    (9, 7): {
        'encounter_id': 'dungeon_l5_marcus_confrontation',
        'completion_flag': 'marcus_confrontation_complete',
        'one_time': True
    },
    (10, 7): {
        'encounter_id': 'dungeon_l5_marcus_confrontation',
        'completion_flag': 'marcus_confrontation_complete',
        'one_time': True
    },
    (11, 7): {
        'encounter_id': 'dungeon_l5_marcus_confrontation',
        'completion_flag': 'marcus_confrontation_complete',
        'one_time': True
    },
    (12, 7): {
        'encounter_id': 'dungeon_l5_marcus_confrontation',
        'completion_flag': 'marcus_confrontation_complete',
        'one_time': True
    },
    (10, 18): {
        'encounter_id': 'dungeon_l5_final_boss',
        'completion_flag': 'final_boss_defeated',
        'one_time': True,
        'requires_flag': 'marcus_confrontation_complete'
    },
    (11, 18): {
        'encounter_id': 'dungeon_l5_final_boss',
        'completion_flag': 'final_boss_defeated',
        'one_time': True,
        'requires_flag': 'marcus_confrontation_complete'
    },
    (12, 18): {
        'encounter_id': 'dungeon_l5_final_boss',
        'completion_flag': 'final_boss_defeated',
        'one_time': True,
        'requires_flag': 'marcus_confrontation_complete'
    },
    (10, 19): {
        'encounter_id': 'dungeon_l5_final_boss',
        'completion_flag': 'final_boss_defeated',
        'one_time': True,
        'requires_flag': 'marcus_confrontation_complete'
    },
    (11, 19): {
        'encounter_id': 'dungeon_l5_final_boss',
        'completion_flag': 'final_boss_defeated',
        'one_time': True,
        'requires_flag': 'marcus_confrontation_complete'
    },
    (12, 19): {
        'encounter_id': 'dungeon_l5_final_boss',
        'completion_flag': 'final_boss_defeated',
        'one_time': True,
        'requires_flag': 'marcus_confrontation_complete'
    }
}

# Transitions
TRANSITIONS = {
    (12, 1): {
        'target_screen': 'dungeon_level_4_nav',
        'action': 'go up stairs to Level 4',
        'direction': 'north'
    }
}

def get_tile_type(x, y):
    """Get the tile character at coordinates."""
    if 0 <= y < len(DUNGEON_L5_MAP) and 0 <= x < len(DUNGEON_L5_MAP[y]):
        return DUNGEON_L5_MAP[y][x]
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
    searchable = SEARCHABLES.get((x, y))
    if searchable:
        # Check if requires a flag
        requires_flag = searchable.get('requires_flag')
        if requires_flag:
            # Return special marker that nav screen needs to check
            return searchable
    return searchable

def get_combat_trigger(x, y):
    """Get combat trigger at position."""
    trigger = COMBAT_TRIGGERS.get((x, y))
    if trigger:
        # Check if requires a flag
        requires_flag = trigger.get('requires_flag')
        if requires_flag:
            # Return special marker that nav screen needs to check
            return trigger
    return trigger