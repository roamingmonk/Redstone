"""
Dungeon Level 5 - Portal Chamber
The deepest level. Site of the portal and final confrontation.
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
    "############.###########",
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

# Searchable objects (FIXED to match Level 4 pattern)
# Searchable objects (FIXED to match Level 4 pattern)
SEARCHABLE_OBJECTS = {
    'marcus_confrontation': {
        'search_tiles': [(8, 7), (9, 7), (10, 7), (11, 7), (12, 7)],
        'object_pos': [(10, 7)],
        'info': {
            'name': 'Marcus Nightshade',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_5_marcus',
            'flag_set': 'marcus_encountered_level_5',
            'one_time': False  # Can re-examine if needed
        }
    },
    'ritual_circle': {
        'search_tiles': [(11, 13), (12, 13), (13, 13), (11, 14), (12, 14), (13, 14)],
        'object_pos': [(12, 13)],
        'info': {
            'name': 'Ancient Ritual Circle',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_5_ritual_circle',
            'flag_set': 'dungeon_l5_ritual_examined',
            'one_time': True
        }
    },
    'portal': {
        'search_tiles': [(10, 18), (11, 18), (12, 18), (10, 19), (11, 19), (12, 19)],
        'object_pos': [(11, 18)],
        'info': {
            'name': 'Portal',
            'interaction_type': 'dialogue',
            'examine_dialogue': 'dungeon_level_5_portal',
            'flag_set': 'dungeon_l5_portal_examined',
            'one_time': True,
            'requires_flag': 'marcus_confrontation_complete'
        }
    }
}

# Auto-triggered dialogues (trigger on movement, no ENTER required)
AUTO_DIALOGUE_TRIGGERS = {
    'marcus_confrontation': {
        'trigger_tiles': [(8, 7), (9, 7), (10, 7), (11, 7), (12, 7)],
        'dialogue_id': 'dungeon_level_5_marcus',
        'npc_id': 'marcus',
        'flag_check': 'marcus_encountered_level_5',
        'one_time': True
    }
}

def get_searchable_at_position(x, y):
    """Check if player is near searchable object"""
    for obj_id, obj_data in SEARCHABLE_OBJECTS.items():
        if (x, y) in obj_data['search_tiles']:
            # Check requirements if present
            info = obj_data['info']
            if 'requires_flag' in info:
                # Return info with requirement marker
                return info
            return info
    return None

def get_searchable_at_position(x, y):
    """Check if player is near searchable object"""
    for obj_id, obj_data in SEARCHABLE_OBJECTS.items():
        if (x, y) in obj_data['search_tiles']:
            # Check requirements if present
            info = obj_data['info']
            if 'requires_flag' in info:
                # Return info with requirement marker
                return info
            return info
    return None

def get_auto_dialogue_trigger(x, y):
    """Get auto-dialogue trigger at position."""
    for trigger_id, trigger_data in AUTO_DIALOGUE_TRIGGERS.items():
        trigger_tiles = trigger_data.get('trigger_tiles', [])
        if (x, y) in trigger_tiles:
            return trigger_data
    return None

# Combat encounters (FIXED - Marcus REMOVED, only final boss remains)
COMBAT_ENCOUNTERS = {
    'final_boss': {
        'trigger_tiles': [(10, 18), (11, 18), (12, 18), (10, 19), (11, 19), (12, 19)],
        'encounter_id': 'dungeon_l5_final_boss',
        'one_time': True,
        'completion_flag': 'final_boss_defeated',
        'repeatable': False,
        'chance': 1.0,
        'requires_flag': 'marcus_confrontation_complete'
    }
}

def get_combat_trigger(x, y):
    """Check if position triggers combat encounter"""
    for encounter_id, encounter_data in COMBAT_ENCOUNTERS.items():
        if (x, y) in encounter_data['trigger_tiles']:
            return encounter_data
    return None

# Area transitions (FIXED to match Level 4 nested structure)
AREA_TRANSITIONS = {
    'stairs_to_level_4': {
        'entrance_tiles': [(12, 1), (11, 1), (13, 1)],
        'building_pos': [(12, 1)],
        'info': {
            'name': 'Ascending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_4_nav',
            'action': 'Return to Level 4',
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
    if 0 <= y < len(DUNGEON_L5_MAP) and 0 <= x < len(DUNGEON_L5_MAP[y]):
        return DUNGEON_L5_MAP[y][x]
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