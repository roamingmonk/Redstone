"""
Hill Ruins Ground Level Map Data
20x20 tile grid for interior ruins with portal chamber
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW, STEEL_BLUE, DARK_BLUE, BLUE, PURPLE
)

HILL_RUINS_GL_WIDTH = 20
HILL_RUINS_GL_HEIGHT = 20
HILL_RUINS_GL_SPAWN_X = 10
HILL_RUINS_GL_SPAWN_Y = 18  # Enter from bottom (from entrance)

# Tile type definitions
TILE_TYPES = {
    '#': 'ruins_wall',    # Stone walls
    '.': 'floor',         # Walkable stone floor
    'P': 'portal',        # Portal chamber (searchable)
    'M': 'mechanism',     # Ancient mechanism (searchable)
    'D': 'door',          # Door to exterior
    'S': 'stairs',        # Stairs down to locked dungeon
    'c': 'column',        # Decorative columns (not walkable)
    'r': 'rubble',        # Interior rubble
    '~': 'combat_zone',   # Combat trigger
}

WALKABLE_TILES = {'floor', 'mechanism', 'door', 'stairs', 'rubble', 'combat_zone'}

# ASCII map layout - 20x20 grid
HILL_RUINS_GL_MAP = [
    "####################",  # Row 0
    "#..................#",  # Row 1
    "#...cc......cc.....#",  # Row 2 - Columns
    "#...cc......cc.....#",  # Row 3
    "#..................#",  # Row 4
    "#......rrrr........#",  # Row 5 - Rubble
    "#......rrrr........#",  # Row 6
    "#..................#",  # Row 7
    "#...~..............#",  # Row 8 - Combat zone
    "#..................#",  # Row 9
    "#.....PPPPPP.......#",  # Row 10 - Portal chamber
    "#.....PPPPPP.......#",  # Row 11
    "#.....PPPPPP.......#",  # Row 12
    "#.....PPPPPP.......#",  # Row 13
    "#..................#",  # Row 14
    "#..MM..............#",  # Row 15 - Ancient mechanisms
    "#..MM..............#",  # Row 16
    "#SS................#",  # Row 17 - Stairs to dungeon
    "#SS...............D#",  # Row 18 - Door to exterior
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < HILL_RUINS_GL_HEIGHT and 0 <= x < HILL_RUINS_GL_WIDTH:
        char = HILL_RUINS_GL_MAP[y][x]
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
        'ruins_wall': (80, 80, 80),          # Dark gray stone
        'floor': (120, 100, 80),             # Brown stone floor
        'portal': (138, 43, 226),            # Purple portal glow (SEARCHABLE)
        'mechanism': (192, 192, 192),        # Silver mechanisms (SEARCHABLE)
        'door': (139, 69, 19),               # Brown door
        'stairs': (60, 60, 60),              # Dark gray stairs
        'column': (169, 169, 169),           # Light gray columns
        'rubble': (105, 105, 105),           # Gray rubble
        'combat_zone': (125, 105, 85),       # Slightly different floor
    }
    return TILE_COLORS.get(tile_type, GRAY)

# Area transitions
AREA_TRANSITIONS = {
    'door_to_entrance': {
        'entrance_tiles': [(18, 17), (18, 18)],
        'building_pos': [(18, 18)],
        'info': {
            'name': 'Ruins Door',
            'interaction_type': 'navigation',
            'target_screen': 'hill_ruins_entrance_nav',
            'action': 'Exit to Entrance',
            'requirements': {}
        }
    },
    'stairs_to_dungeon': {
    'entrance_tiles': [(1, 16), (2, 16), (1, 17), (2, 17), (1, 18), (2, 18)],
    'building_pos': [(1, 17), (2, 17), (1, 18), (2, 18)],
    'info': {
        'name': 'Dungeon Stairs',
        'interaction_type': 'navigation',
        'target_screen': 'dungeon_level_1_nav',  
        'action': 'Descend into Dungeon',
        'requirements': {}
    }
}
}

def get_transition_at_entrance(player_x, player_y):
    """Check if player is at area transition point"""
    for transition_id, transition_data in AREA_TRANSITIONS.items():
        if (player_x, player_y) in transition_data['entrance_tiles']:
            return transition_data['info']
    return None

# Searchable objects
SEARCHABLE_OBJECTS = {
    'portal_chamber': {
        'search_tiles': [
            (5, 10), (12, 10), (6, 9), (7, 9), (8, 9), (9, 9),
            (5, 11), (12, 11), (10, 9), (11,9),
            (5, 12), (12, 12), 
            (5, 13), (12, 13), 
            (6, 14), (7, 14), (8, 14), (9, 14), (10,14), (11,14)
        ],
        'object_pos': [(6, 11), (7, 11), (8, 11), (9, 11)],
        'info': {
            'name': 'Portal Chamber',
            'interaction_type': 'searchable',
            'description': 'A large crystalline portal structure humming with energy.',
            'examine_dialogue': 'hill_ruins_portal',
            'loot_table': None,
            'flag_set': 'hill_ruins_portal_examined',
            'requirements': {},
            'one_time': True
        }
    },
    'ancient_mechanisms': {
        'search_tiles': [(4, 15), (3, 15), (4, 16), (3, 16)],
        'object_pos': [(4, 15), (3, 15), (4, 16), (3, 16)],
        'info': {
            'name': 'Ancient Mechanisms',
            'interaction_type': 'searchable',
            'description': 'Complex mechanical devices of unknown purpose.',
            'examine_dialogue': 'hill_ruins_mechanisms',
            'loot_table': None,
            'flag_set': 'hill_ruins_mechanisms_searched',
            'requirements': {},
            'one_time': True
        }
    },
    'ground_level_ancient_rubble': {
        'search_tiles': [(7, 5), (8, 5), (9, 5), (10, 5),    
                       (7, 6), (8, 6), (9, 6), (10, 6)],  # Around rubble
        'object_pos': [(7, 5), (8, 5), (9, 5), (10, 5),    
                       (7, 6), (8, 6), (9, 6), (10, 6)],  # Rubble tiles
        'info': {
            'name': 'Ancient Rubble',
            'interaction_type': 'searchable',
            'description': 'Broken stones with faded rune carvings.',
            'examine_dialogue': 'hill_ruins_ground_level_rubble',
            'loot_table': None,
            'flag_set': 'hill_ruins_ground_level_rubble_searched',
            'requirements': {},
            'one_time': True
        }
    },
}

def get_searchable_at_position(player_x, player_y):
    """Check if player is standing at a searchable object"""
    for search_id, search_data in SEARCHABLE_OBJECTS.items():
        if (player_x, player_y) in search_data['search_tiles']:
            return search_data['info']
    return None

# Combat triggers
COMBAT_TRIGGERS = {
    (4, 8): {
        'encounter_id': 'hill_ruins_statue',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.9,  # 25% chance
        'flag_check': None,
        'flag_set': None
    }
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

# No NPCs in ground level
LOCATION_NPCS = {}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS