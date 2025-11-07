"""
Red Hollow Mine Level 2 Map Data
20x20 tile grid for deeper mine shafts with branching paths
Contains Meredith's ring in mining carts
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

MINE_L2_WIDTH = 20
MINE_L2_HEIGHT = 20
MINE_L2_SPAWN_X = 10
MINE_L2_SPAWN_Y = 1  # Enter from top (descending from Level 1)

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Mine walls/rock
    '.': 'ground',        # Walkable tunnel floor
    'r': 'rock',          # Rock formations
    'o': 'ore_vein',      # Ore traces (visual only)
    'K': 'combat_zone',   # Kobold warrior zone (walkable but dangerous)
    'C': 'mining_cart',   # Mining carts (searchable - RING HERE!)
    'U': 'stairs_up',     # Return to Level 1
    'D': 'stairs_down',   # Descend to Level 3 (main path)
    'B': 'side_passage',  # Side passage to Level 2B (dead end branch)
    'p': 'pillar',        # Support pillar
    'w': 'warning',       # Unstable area warning (examinable)
}

WALKABLE_TILES = {'ground', 'combat_zone', 'mining_cart', 'stairs_up', 'stairs_down', 'side_passage', 'warning', 'ore_vein'}

# ASCII map layout - 20x20 grid
MINE_L2_MAP = [
    "####################",  # Row 0
    "#.........U........#",  # Row 1 - U = stairs up to Level 1
    "#p.................#",  # Row 2
    "#...rrr.....rrr....#",  # Row 3
    "#..roor....roor....#",  # Row 4 - Ore traces
    "#...rrr.....rrr...p#",  # Row 5
    "#..................#",  # Row 6
    "#.....K...K........#",  # Row 7 - K = combat zones (40% kobold warriors)
    "#..p...............#",  # Row 8
    "#.......CCC........#",  # Row 9 - C = mining carts (RING LOCATION!)
    "#.......CCC........#",  # Row 10
    "#..................#",  # Row 11
    "#....K........K...w#",  # Row 12 - w = warning sign for side passage
    "#p................B#",  # Row 13 - B = side passage to Level 2B
    "#.................B#",  # Row 14 - B = side passage continues
    "#..................#",  # Row 15
    "#....rrr...rrr.....#",  # Row 16
    "#...roor..roor....p#",  # Row 17 - More ore traces
    "#.........D........#",  # Row 18 - D = stairs down to Level 3
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < MINE_L2_HEIGHT and 0 <= x < MINE_L2_WIDTH:
        char = MINE_L2_MAP[y][x]
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
        'wall': (50, 40, 30),            # Darker brown rock (deeper)
        'ground': (70, 60, 50),          # Darker tunnel floor
        'rock': (80, 70, 60),            # Rock formations
        'ore_vein': (80, 150, 200),      # Faint ore glow
        'combat_zone': (75, 65, 55),     # Slightly darker ground
        'mining_cart': (150, 140, 120),  # Tan/brown carts (HIGHLIGHT)
        'stairs_up': (110, 90, 70),      # Lighter stairs
        'stairs_down': (90, 70, 50),     # Darker stairs
        'side_passage': (60, 50, 40),    # Dark passage entrance
        'pillar': (60, 50, 40),          # Dark wooden pillar
        'warning': (200, 180, 50),       # Yellow warning sign
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions - BRANCHING PATHS!
AREA_TRANSITIONS = {
    'return_to_level_1': {
        'entrance_tiles': [(10, 1), (9, 1), (11, 1)],  # Stairs up area
        'building_pos': [(10, 1)],
        'info': {
            'name': 'Return to Level 1',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_1_nav',
            'action': 'Ascend to Level 1',
            'requirements': {}
        }
    },
    'descend_to_level_3': {
        'entrance_tiles': [(10, 18), (9, 18), (11, 18)],  # Stairs down - main path
        'building_pos': [(10, 18)],
        'info': {
            'name': 'Deep Mine Shafts',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_3_nav',
            'action': 'Descend to Level 3',
            'requirements': {}
        }
    },
    'side_passage_to_2b': {
        'entrance_tiles': [(18, 13), (18, 14)],  # Side passage - dead end branch
        'building_pos': [(18, 13), (18, 14)],
        'info': {
            'name': 'Collapsed Side Passage',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_2b_nav',
            'action': 'Enter Unstable Passage',
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
    'mining_carts': {
        'search_tiles': [(7, 9), (8, 9), (9, 9), (7, 10), (8, 10), (9, 10)],  # Cart area
        'object_pos': [(8, 9), (8, 10)],
        'info': {
            'name': 'Mining Carts',
            'interaction_type': 'searchable',
            'description': 'Old mining carts filled with coal and debris.',
            'examine_dialogue': 'mine_carts',
            'loot_table': 'mine_carts_loot',  # Contains Meredith's ring!
            'flag_set': 'searched_mining_carts',
            'requirements': {},
            'one_time': True
        }
    },
    'unstable_warning': {
        'search_tiles': [(18, 12), (17, 12)],  # Warning sign
        'object_pos': [(18, 12)],
        'info': {
            'name': 'Unstable Area Warning',
            'interaction_type': 'searchable',
            'description': 'A crudely painted warning about cave-ins.',
            'examine_dialogue': 'mine_unstable_tunnels',
            'loot_table': None,
            'flag_set': 'examined_unstable_warning',
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

# Combat triggers - Kobold warriors (40% chance) - tougher encounters
COMBAT_TRIGGERS = {
    (6, 7): {
        'encounter_id': 'mine_kobold_warriors',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.40,
        'flag_check': 'cleared_kobold_mine',
        'flag_set': None
    },
    (10, 7): {
        'encounter_id': 'mine_kobold_warriors',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.40,
        'flag_check': 'cleared_kobold_mine',
        'flag_set': None
    },
    (5, 12): {
        'encounter_id': 'mine_kobold_warriors',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.40,
        'flag_check': 'cleared_kobold_mine',
        'flag_set': None
    },
    (14, 12): {
        'encounter_id': 'mine_kobold_warriors',
        'trigger_type': 'step_on',
        'repeatable': 'cleared_kobold_mine',
        'chance': 0.40,
        'flag_check': None,
        'flag_set': None
    }
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

LOCATION_NPCS = {}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS