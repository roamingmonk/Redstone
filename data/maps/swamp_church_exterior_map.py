"""
Swamp Church Exterior Map Data
20x20 tile grid for foggy swamp church approach
"""

from utils.constants import (
                           #Colors
                           FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
                           CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
                           #Buttons
                           BUTTON_SIZES, SCREEN_WIDTH
)

SWAMP_CHURCH_EXT_WIDTH = 20
SWAMP_CHURCH_EXT_HEIGHT = 20
SWAMP_CHURCH_EXT_SPAWN_X = 10
SWAMP_CHURCH_EXT_SPAWN_Y = 18  # Enter from bottom (arriving from regional map)

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Map boundary walls
    '.': 'ground',        # Walkable muddy ground
    'w': 'water',         # Water pools (not walkable)
    't': 'tree',          # Trees (not walkable)
    's': 'swamp',         # Swamp mud (walkable)
    'g': 'grave',         # Graveyard tiles (walkable)
    'C': 'church_wall',   # Church exterior walls (not walkable)
    'D': 'church_door',   # Church entrance (transition point)
    'S': 'symbols',       # Ancient symbols (searchable/examinable)
    'a': 'altar',         # Outdoor altar (searchable)
    'R': 'random_combat', # Random encounter zone (walkable but dangerous)
    'r': 'church_roof',   # Church roof (not walkable)
}

WALKABLE_TILES = {'ground', 'swamp', 'grave', 'random_combat', 'symbols', 'altar'}

# ASCII map layout - 20x20 grid
SWAMP_CHURCH_EXT_MAP = [
    "####################",  # Row 0
    "#tttt.........tttttt#",  # Row 1 - Trees frame edges
    "#tt..wwww..wwww...tt#",  # Row 2 - Water pools
    "#t.wwssSS..SSssw..tt#",  # Row 3 - SS = symbols (searchable)
    "#..wsssgggggsssw...t#",  # Row 4 - graves  (searchable)
    "#..wssgCCCCgssw....t#",  # Row 5 - Church walls 
    "#...ssgCrrCgsw.....#",  # Row 6 - Church walls and roof
    "#...sggCrrCgg..aaa....#",  # Row 7 - rr = church roof
    "#....ggCDDCgg......#",  # Row 8 - Church Door DD (transition)
    "#.....gggggg.......#",  # Row 9 -  g = graves
    "#......gggg........#",  # Row 10
    "#.......RR.........#",  # Row 11 - RR = random combat zone
    "#.....t.RR.....t...#",  # Row 12
    "#....ttt......ttt..#",  # Row 13
    "#...ttttt....ttttt.#",  # Row 14
    "#..ttttttt..tttttt.#",  # Row 15
    "#.....ttt....ttt...#",  # Row 16
    "#......t......t....#",  # Row 17
    "#..................#",  # Row 18 - spawn point
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < SWAMP_CHURCH_EXT_HEIGHT and 0 <= x < SWAMP_CHURCH_EXT_WIDTH:
        char = SWAMP_CHURCH_EXT_MAP[y][x]
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
        'wall': (60, 60, 60),         # Dark gray boundary
        'ground': (101, 67, 33),      # Brown muddy earth
        'water': (0, 119, 190),       # Blue water
        'tree': (34, 139, 34),        # Forest green
        'swamp': (85, 107, 47),       # Olive/dark green swamp
        'grave': (105, 105, 105),     # Gray tombstones
        'church_wall': (169, 169, 169),  # Light gray stone
        'church_door': (139, 69, 19), # Brown door
        'symbols': (200, 150, 100),   # Tan/beige (HIGHLIGHT for searchable)
        'altar': (180, 180, 180),     # Light gray (HIGHLIGHT for searchable)
        'random_combat': (110, 75, 40),  # Slightly darker ground (subtle)
        'church_roof': (FIRE_BRICK_RED),   # red-brown roof
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions (navigation between areas/screens)
AREA_TRANSITIONS = {
    'church_entrance': {
        'entrance_tiles': [(9, 9), (10, 9)],  # Standing in front of doors
        'building_pos': [(9, 8), (10, 8)],    # Door tiles
        'info': {
            'name': 'Church Entrance',
            'interaction_type': 'navigation',
            'target_screen': 'swamp_church_interior_nav',  # Interior map screen
            'action': 'Enter Church',
            'requirements': {}  # No special requirements to enter
        }
    },
    'return_to_region': {
        'entrance_tiles': [(10, 18), (10, 19)],  # Bottom spawn area
        'building_pos': [(10, 19)],
        'info': {
            'name': 'Leave Area',
            'interaction_type': 'navigation',
            'target_screen': 'exploration_hub',  # Back to regional map
            'action': 'Return to Region Map',
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

# Searchable objects (examine/loot)
SEARCHABLE_OBJECTS = {
    'ancient_symbols': {
        'search_tiles': [(8, 3), (9, 3), (10, 3), (11, 3)],  # Around symbols
        'object_pos': [(9, 3), (10, 3)],  # Symbol tiles
        'info': {
            'name': 'Ancient Symbols',
            'interaction_type': 'searchable',
            'description': 'Strange symbols carved into weathered stone pillars.',
            'examine_dialogue': 'swamp_church_symbols',  # Use existing dialogue
            'loot_table': None,
            'flag_set': 'examined_swamp_symbols',
            'requirements': {},
            'one_time': True
        }
    },
    'disturbed_graves': {
        'search_tiles': [(8, 4), (9, 4), (10, 4), (11, 4)],  # Grave area
        'object_pos': [(9, 4), (10, 4), (11, 4)],  # Grave tiles
        'info': {
            'name': 'Disturbed Graves',
            'interaction_type': 'searchable',
            'description': 'Recently disturbed graves with freshly dug dirt.',
            'examine_dialogue': 'swamp_church_graves',  # New dialogue file
            'loot_table': None,
            'flag_set': 'searched_swamp_graves',
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

# Combat triggers (random encounters)
COMBAT_TRIGGERS = {
    (8, 11): {  # Random combat zone tile
        'encounter_id': 'swamp_skeleton',
        'trigger_type': 'step_on',
        'repeatable': True,  # Can re-encounter
        'chance': 0.3,  # 30% chance when stepping on tile
        'flag_check': None,
        'flag_set': None  # Doesn't set flag (repeatable)
    },
    (9, 11): {  # Another random combat tile
        'encounter_id': 'swamp_skeleton',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.25,
        'flag_check': None,
        'flag_set': None
    },
    (8, 12): {  # Ghost encounter zone
        'encounter_id': 'swamp_ghost',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.35,  # 25% chance
        'flag_check': None,
        'flag_set': None
    },
    (9, 12): {  # Another ghost tile
        'encounter_id': 'swamp_ghost',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.35,
        'flag_check': None,
        'flag_set': None
    }
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

# NPCs in this area (optional)
LOCATION_NPCS = {}  # No NPCs in exterior for now

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS