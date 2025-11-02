"""
Swamp Church Interior Map Data
20x20 tile grid for church interior with pews, altar, and crypt stairs
"""

SWAMP_CHURCH_INT_WIDTH = 20
SWAMP_CHURCH_INT_HEIGHT = 20
SWAMP_CHURCH_INT_SPAWN_X = 10
SWAMP_CHURCH_INT_SPAWN_Y = 18  # Enter from bottom (from exterior)

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Stone walls
    '.': 'floor',         # Walkable stone floor
    'p': 'pew',           # Church pews (searchable)
    'A': 'altar',         # Main altar (searchable)
    'D': 'door',          # Door to exterior
    'S': 'stairs',        # Stairs down to crypt
    'c': 'candle',        # Decorative candles
}

WALKABLE_TILES = {'floor', 'pew', 'altar', 'door', 'stairs'}

# ASCII map layout - 20x20 grid
SWAMP_CHURCH_INT_MAP = [
    "####################",  # Row 0
    "#..................#",  # Row 1
    "#.pppp....pppp.....#",  # Row 2 - Pews
    "#.pppp....pppp.....#",  # Row 3
    "#..................#",  # Row 4
    "#.pppp....pppp.....#",  # Row 5
    "#.pppp....pppp.....#",  # Row 6
    "#..................#",  # Row 7
    "#.pppp....pppp.....#",  # Row 8
    "#.pppp....pppp.....#",  # Row 9
    "#..................#",  # Row 10
    "#........AA........#",  # Row 11 - Altar
    "#........AA........#",  # Row 12
    "#..................#",  # Row 13
    "#........SS........#",  # Row 14 - Stairs to crypt
    "#........SS........#",  # Row 15
    "#..................#",  # Row 16
    "#..................#",  # Row 17
    "#.........D........#",  # Row 18 - Door to exterior
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < SWAMP_CHURCH_INT_HEIGHT and 0 <= x < SWAMP_CHURCH_INT_WIDTH:
        char = SWAMP_CHURCH_INT_MAP[y][x]
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
        'wall': (80, 80, 80),          # Dark gray stone
        'floor': (139, 115, 85),       # Brown stone floor
        'pew': (101, 67, 33),          # Dark brown pews (SEARCHABLE)
        'altar': (200, 200, 200),      # Light gray altar (SEARCHABLE)
        'door': (139, 69, 19),         # Brown door
        'stairs': (60, 60, 60),        # Dark gray stairs
        'candle': (255, 215, 0),       # Gold candles
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'door_to_exterior': {
        'entrance_tiles': [(10, 18)],
        'building_pos': [(10, 18)],
        'info': {
            'name': 'Church Door',
            'interaction_type': 'navigation',
            'target_screen': 'swamp_church_exterior_nav',
            'action': 'Exit Church',
            'requirements': {}
        }
    },
    'stairs_to_crypt': {
        'entrance_tiles': [(9, 14), (10, 14), (9, 15), (10, 15)],
        'building_pos': [(9, 14), (10, 14)],
        'info': {
            'name': 'Crypt Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'swamp_church_crypt',
            'action': 'Descend into Crypt',
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
    'church_pews': {
        'search_tiles': [(2, 2), (3, 2), (4, 2), (5, 2),  # Left pews
                        (2, 3), (3, 3), (4, 3), (5, 3),
                        (2, 5), (3, 5), (4, 5), (5, 5),
                        (2, 6), (3, 6), (4, 6), (5, 6),
                        (2, 8), (3, 8), (4, 8), (5, 8),
                        (2, 9), (3, 9), (4, 9), (5, 9),
                        (10, 2), (11, 2), (12, 2), (13, 2),  # Right pews
                        (10, 3), (11, 3), (12, 3), (13, 3),
                        (10, 5), (11, 5), (12, 5), (13, 5),
                        (10, 6), (11, 6), (12, 6), (13, 6),
                        (10, 8), (11, 8), (12, 8), (13, 8),
                        (10, 9), (11, 9), (12, 9), (13, 9)],
        'object_pos': [],  # Pews themselves
        'info': {
            'name': 'Church Pews',
            'interaction_type': 'searchable',
            'description': 'Overturned pews scattered across the floor.',
            'examine_dialogue': 'swamp_church_pews',  # Need to create this
            'loot_table': None,
            'flag_set': 'searched_church_pews',
            'requirements': {},
            'one_time': True
        }
    },
    'main_altar': {
        'search_tiles': [(8, 11), (9, 11), (10, 11), (11, 11),
                        (8, 12), (9, 12), (10, 12), (11, 12)],
        'object_pos': [(9, 11), (10, 11), (9, 12), (10, 12)],
        'info': {
            'name': 'Desecrated Altar',
            'interaction_type': 'searchable',
            'description': 'The main altar, stained and defiled.',
            'examine_dialogue': 'swamp_church_altar',  # Already exists!
            'loot_table': None,
            'flag_set': 'examined_altar',
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

# No combat triggers in interior (safe area)
COMBAT_TRIGGERS = {}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

# No NPCs in interior
LOCATION_NPCS = {}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS