"""
Swamp Church Interior Map Data
20x20 tile grid for church interior with pews, altar, and crypt stairs
"""

from utils.constants import (
                           #Colors
                           FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
                           CYAN, WARNING_RED, TITLE_GREEN, YELLOW, STEEL_BLUE, DARK_BLUE, BLUE,
                           #Buttons
                           BUTTON_SIZES, SCREEN_WIDTH
)

SWAMP_CHURCH_INT_WIDTH = 20
SWAMP_CHURCH_INT_HEIGHT = 20
SWAMP_CHURCH_INT_SPAWN_X = 10
SWAMP_CHURCH_INT_SPAWN_Y = 1  # Enter from top

# Tile type definitions
TILE_TYPES = {
    '#': 'church_wall',   # Stone walls
    '.': 'floor',         # Walkable stone floor
    'p': 'pew',           # Church pews (searchable)
    'A': 'altar',         # Main altar (searchable)
    'D': 'door',          # Door to exterior
    'S': 'stairs',        # Stairs down to crypt
    'c': 'candle',        # Decorative candles
    'W': 'window',        # Church Window
}

WALKABLE_TILES = {'floor', 'pew', 'door', 'stairs'}

# ASCII map layout - 20x20 grid
SWAMP_CHURCH_INT_MAP = [
    "#########DD#########",  # Row 0
    "#c................c#",  # Row 1 - Doors
    "#..................#",  # Row 2 
    "#...ppppp..ppppp...#",  # Row 3
    "W...ppppp..ppppp...W",  # Row 4 - Pews
    "#...ppppp..ppppp...#",  # Row 5
    "#..................#",  # Row 6
    "#...ppppp..ppppp...#",  # Row 7
    "W...ppppp..ppppp...W",  # Row 8
    "#..................#",  # Row 9
    "#...ppppp..ppppp...#",  # Row 10
    "W...ppppp..ppppp...W",  # Row 11 
    "#..................#",  # Row 12
    "#..................#",  # Row 13
    "#........AA........#",  # Row 14 - Altar
    "#....c..AAAA..c....#",  # Row 15
    "#..................#",  # Row 16
    "#SS................#",  # Row 17
    "#SS...............c#",  # Row 18 - Stairs to crypt
    "########WWWW########"   # Row 19
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
        'church_wall': (80, 80, 80),          # Dark gray stone
        'floor': (139, 115, 85),       # Brown stone floor
        'pew': (101, 67, 33),          # Dark brown pews (SEARCHABLE)
        'altar': (200, 200, 200),      # Light gray altar (SEARCHABLE)
        'door': (139, 69, 19),         # Brown door
        'stairs': (60, 60, 60),        # Dark gray stairs
        'candle': (255, 215, 0),       # Gold candles
        'window': (STEEL_BLUE)         # Blue window
    }
    return TILE_COLORS.get(tile_type, (GRAY))

# Area transitions
AREA_TRANSITIONS = {
    'door_to_exterior': {
        'entrance_tiles': [(9, 0), (10,0)],
        'building_pos': [(9, 0), (10, 0)],
        'info': {
            'name': 'Church Door',
            'interaction_type': 'navigation',
            'target_screen': 'swamp_church_exterior_nav',
            'action': 'Exit Church',
            'requirements': {}
        }
    },
    'stairs_to_crypt': {
        'entrance_tiles': [(1, 16), (2, 16), (3, 17), (3, 18)],
        'building_pos': [(1, 17), (2, 17), (1,18), (2,18)],
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
        'search_tiles': [(4, 3), (5, 3), (6, 3), (7, 3), (8, 3),  # Left pews
                        
                        (11, 3), (12, 3), (13, 3), (14,3), (15, 3) # Right pews
                        ],
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
        'search_tiles': [(8, 14), (9, 13), (10, 13), (11, 14),
                        (7, 15), (12, 15), (8, 16), (9, 16), (10,16), (11,16)],
        'object_pos': [(9, 14), (10, 14), (9, 15), (10, 15), (8,15), (11,15)],
        'info': {
            'name': 'Desecrated Altar',
            'interaction_type': 'searchable',
            'description': 'The main altar, stained and defiled.',
            'examine_dialogue': 'swamp_church_altar',  
            'loot_table': None,
            'flag_set': 'examined_altar',
            'requirements': {},
            'one_time': True
        }
   },
    'cult_documents': {
        'search_tiles': [(3, 16), (4, 16), (5, 16),  # Right next to stairs
                        (3, 17), (4, 17), (5, 17),
                        (3, 18), (4, 18), (5, 18),
                        (3, 19), (4, 19), (5, 19)],  # Scattered area
        'object_pos': [(4, 17), (4, 18)],  # Visual sprite (papers on ground)
        'info': {
            'name': 'Cult Documents',
            'interaction_type': 'searchable',
            'description': 'Blood-stained papers scattered on the floor, as if dropped in haste.',
            'examine_dialogue': 'swamp_church_cultdocuments',
            'loot_table': None,
            'flag_set': 'read_cult_documents',
            'requirements': {'found_cult_documents': True},  # Only after combat victory
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