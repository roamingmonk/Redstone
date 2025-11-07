"""
Red Hollow Mine Pre-Entrance Map Data
15x15 tile grid for sealed mine entrance area
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

MINE_PRE_WIDTH = 15
MINE_PRE_HEIGHT = 15
MINE_PRE_SPAWN_X = 7
MINE_PRE_SPAWN_Y = 13  # Enter from bottom

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Map boundary
    '.': 'ground',        # Walkable rocky ground
    'r': 'rock',          # Rock formations (not walkable)
    'R': 'rubble',        # Rubble piles (not walkable)
    'W': 'warning_sign',  # Henrik's warning signs (searchable)
    'E': 'equipment',     # Abandoned equipment (searchable/loot)
    'S': 'seal',          # Henrik's seal (searchable)
    'M': 'mine_entrance', # Sealed entrance (transition to Level 1)
    't': 'tree',          # Sparse trees
    'b': 'barrier',       # Henrik's wooden barriers (not walkable but examinable with seal)
}

WALKABLE_TILES = {'ground', 'warning_sign', 'equipment', 'seal'}

# ASCII map layout - 15x15 grid
MINE_PRE_MAP = [
    "rrr#########rrr",  # Row 0
    "rr....rrr..rrrr",  # Row 1
    "r..r..rrr..r..r",  # Row 2
    "#.rrr.bbb.rrr.r",  # Row 3 - Henrik's barriers
    "#.rrr.bMb.rrr.r",  # Row 4 - S = seal (examinable)
    "#..rr.bSb.rr..#",  # Row 5 - M = mine entrance (transition)
    "#...r.b.b.r...#",  # Row 6
    "#.....r.......#",  # Row 7
    "#..W..rrr...W.#",  # Row 8 - W = warning signs
    "#.............#",  # Row 9
    "#.E.........E.#",  # Row 10 - E = equipment (loot)
    "#.t.........t.#",  # Row 11
    "rr.R.......R..#",  # Row 12 - R = rubble
    "rrr...........#",  # Row 13 - spawn point
    "rrrrrrr.....###"   # Row 14
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < MINE_PRE_HEIGHT and 0 <= x < MINE_PRE_WIDTH:
        char = MINE_PRE_MAP[y][x]
        return TILE_TYPES.get(char, 'wall')
    return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_tile_color(x, y):
    """Get color for tile rendering"""
    tile_type = get_tile_type(x, y)
    TILE_COLORS = {
        'wall': (60, 60, 60),            # Dark gray boundary
        'ground': (101, 67, 33),         # Brown rocky earth
        'rock': (105, 105, 105),         # Gray rocks
        'rubble': (90, 90, 90),          # Dark gray rubble
        'warning_sign': (200, 180, 50),  # Yellow warning (HIGHLIGHT)
        'equipment': (180, 160, 120),    # Tan equipment (HIGHLIGHT)
        'seal': (150, 100, 50),          # Brown seal
        'mine_entrance': (40, 40, 40),   # Dark entrance
        'tree': (34, 139, 34),           # Green
        'barrier': (139, 90, 43),        # Brown wooden barrier
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'mine_entrance': {
        'entrance_tiles': [(7, 5)],  # In front of entrance
        'building_pos': [(7, 4)],    # Mine entrance tile
        'info': {
            'name': 'Mine Entrance',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_1_nav',
            'action': 'Enter the Mine',
            'requirements': {}
        }
    },
    'return_to_region': {
        'entrance_tiles': [(7, 13), (7, 14), (8,14), (9,14), (10,14), (11,14)],  # Bottom spawn area
        'building_pos': [(7, 14)],
        'info': {
            'name': 'Leave Area',
            'interaction_type': 'navigation',
            'target_screen': 'exploration_hub',
            'action': 'Return to Region Map',
            'requirements': {}
        }
    }
}

def get_transition_info(player_x, player_y):
    """Check if player is at area transition point"""
    for transition_id, transition_data in AREA_TRANSITIONS.items():
        if (player_x, player_y) in transition_data['entrance_tiles']:
            return transition_data['info']
    return None

# Searchable objects
SEARCHABLE_OBJECTS = {
    'warning_signs': {
        'search_tiles': [(3, 8), (11, 8)],  # Warning sign tiles
        'object_pos': [(3, 8), (11, 8)],
        'info': {
            'name': 'Warning Signs',
            'interaction_type': 'searchable',
            'description': 'Weathered wooden signs with dire warnings.',
            'examine_dialogue': 'mine_warning_signs',
            'loot_table': None,
            'flag_set': 'examined_mine_warnings',
            'requirements': {},
            'one_time': True
        }
    },
    'henrik_seal': {
        'search_tiles': [(7,6)],  # In front of seal
        'object_pos': [(7, 5)],
        'info': {
            'name': "Henrik's Seal",
            'interaction_type': 'searchable',
            'description': 'Heavy wooden beams and chains sealing the entrance.',
            'examine_dialogue': 'mine_henrik_seal',
            'loot_table': None,
            'flag_set': 'examined_henrik_seal',
            'requirements': {},
            'one_time': True
        }
    },
    'abandoned_equipment': {
        'search_tiles': [(2, 10), (12, 10)],  # Equipment piles
        'object_pos': [(2, 10), (12, 10)],
        'info': {
            'name': 'Abandoned Equipment',
            'interaction_type': 'searchable',
            'description': 'Old mining tools and supplies left behind.',
            'examine_dialogue': 'mine_equipment',
            'loot_table': 'mine_equipment_loot',
            'flag_set': 'searched_mine_equipment',
            'requirements': {},
            'one_time': True
        }
    }
}

def get_searchable_at_position(player_x, player_y):
    """Check if player is standing at a searchable object"""
    for search_id, search_data in SEARCHABLE_OBJECTS.items():
        if (player_x, player_y) in search_data['search_tiles']:
            return search_data['info']
    return None

# No combat triggers in pre-entrance (warning area)
COMBAT_TRIGGERS = {}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

LOCATION_NPCS = {}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS