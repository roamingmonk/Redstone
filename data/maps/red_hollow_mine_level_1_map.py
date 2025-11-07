"""
Red Hollow Mine Level 1 Map Data
20x20 tile grid for upper mine tunnels with kobold infestation
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

MINE_L1_WIDTH = 20
MINE_L1_HEIGHT = 20
MINE_L1_SPAWN_X = 10
MINE_L1_SPAWN_Y = 1  # Enter from top (descending from pre-entrance)

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Mine walls/rock
    '.': 'ground',        # Walkable tunnel floor
    'r': 'rock',          # Rock formations
    'O': 'ore_vein',      # Glowing Aethel Ore (searchable)
    'K': 'combat_zone',   # Kobold encounter zone (walkable but dangerous)
    'N': 'nest',          # Kobold nest area (searchable)
    'U': 'stairs_up',     # Return to pre-entrance
    'D': 'stairs_down',   # Descend to Level 2
    'c': 'cart',          # Mining cart (decoration)
    'p': 'pillar',        # Support pillar
}

WALKABLE_TILES = {'ground', 'combat_zone', 'ore_vein', 'nest', 'stairs_up', 'stairs_down', 'cart'}

# ASCII map layout - 20x20 grid
MINE_L1_MAP = [
    "####################",  # Row 0
    "#.........U........#",  # Row 1 - U = stairs up to pre-entrance
    "#p.................#",  # Row 2
    "#...rrr.....rrr....#",  # Row 3
    "#..rOOr....rOOr....#",  # Row 4 - O = ore veins (searchable)
    "#...rrr.....rrr...p#",  # Row 5
    "#..................#",  # Row 6
    "#.....K...K........#",  # Row 7 - K = combat zones (35% kobold scouts)
    "#..p...............#",  # Row 8
    "#.......NNN........#",  # Row 9 - N = kobold nest (searchable)
    "#.......NNN.....c..#",  # Row 10
    "#..................#",  # Row 11
    "#....K........K....#",  # Row 12 - More combat zones
    "#p.................#",  # Row 13
    "#........c.........#",  # Row 14
    "#..................#",  # Row 15
    "#....rrr...rrr.....#",  # Row 16
    "#...rOOr..rOOr....p#",  # Row 17 - More ore veins
    "#.........D........#",  # Row 18 - D = stairs down to Level 2
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < MINE_L1_HEIGHT and 0 <= x < MINE_L1_WIDTH:
        char = MINE_L1_MAP[y][x]
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
        'wall': (60, 50, 40),            # Dark brown rock
        'ground': (80, 70, 60),          # Gray-brown tunnel floor
        'rock': (90, 80, 70),            # Lighter rock
        'ore_vein': (100, 200, 255),     # Glowing cyan ore (HIGHLIGHT)
        'combat_zone': (85, 75, 65),     # Slightly darker ground
        'nest': (110, 90, 70),           # Brown nest material
        'stairs_up': (120, 100, 80),     # Lighter stairs
        'stairs_down': (100, 80, 60),    # Darker stairs
        'cart': (100, 100, 100),         # Gray metal cart
        'pillar': (70, 60, 50),          # Dark wooden pillar
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'return_to_pre_entrance': {
        'entrance_tiles': [(10, 1), (9, 1), (11, 1)],  # Stairs up area
        'building_pos': [(10, 1)],
        'info': {
            'name': 'Return to Entrance',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_pre_entrance_nav',
            'action': 'Ascend to Pre-Entrance',
            'requirements': {}
        }
    },
    'descend_to_level_2': {
        'entrance_tiles': [(10, 18), (9, 18), (11, 18)],  # Stairs down area
        'building_pos': [(10, 18)],
        'info': {
            'name': 'Deeper Mine Shafts',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_2_nav',
            'action': 'Descend to Level 2',
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
    'aethel_ore_deposits_north': {
        'search_tiles': [(5, 4), (6, 4), (14, 4), (15, 4)],  # North ore veins
        'object_pos': [(5, 4), (6, 4), (14, 4), (15, 4)],
        'info': {
            'name': 'Glowing Ore Deposits',
            'interaction_type': 'searchable',
            'description': 'Strange glowing ore veins pulse with otherworldly light.',
            'examine_dialogue': 'mine_aethel_ore',
            'loot_table': 'mine_ore_deposits_loot',
            'flag_set': 'saw_aethel_ore',
            'requirements': {},
            'one_time': True
        }
    },
    'aethel_ore_deposits_south': {
        'search_tiles': [(5, 17), (6, 17), (14, 17), (15, 17)],  # South ore veins
        'object_pos': [(5, 17), (6, 17), (14, 17), (15, 17)],
        'info': {
            'name': 'Glowing Ore Deposits',
            'interaction_type': 'searchable',
            'description': 'More glowing ore veins embedded in the rock.',
            'examine_dialogue': 'mine_ore_deposits',
            'loot_table': 'mine_ore_deposits_loot',
            'flag_set': 'searched_level_1_ore',
            'requirements': {},
            'one_time': True
        }
    },
    'kobold_nest': {
        'search_tiles': [(7, 9), (8, 9), (9, 9), (7, 10), (8, 10), (9, 10)],  # Nest area
        'object_pos': [(8, 9), (8, 10)],
        'info': {
            'name': 'Kobold Nest',
            'interaction_type': 'searchable',
            'description': 'A crude nest made of rags, bones, and stolen items.',
            'examine_dialogue': 'mine_kobold_supplies',
            'loot_table': 'mine_kobold_supplies_loot',
            'flag_set': 'searched_kobold_nest',
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

# Combat triggers - Kobold scouts (35% chance)
COMBAT_TRIGGERS = {
    (6, 7): {
        'encounter_id': 'mine_kobold_scouts',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.35,
        'flag_check': 'cleared_kobold_mine',
        'flag_set': None
    },
    (10, 7): {
        'encounter_id': 'mine_kobold_scouts',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.35,
        'flag_check': 'cleared_kobold_mine',
        'flag_set': None
    },
    (5, 12): {
        'encounter_id': 'mine_kobold_scouts',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.35,
        'flag_check': 'cleared_kobold_mine',
        'flag_set': None
    },
    (14, 12): {
        'encounter_id': 'mine_kobold_scouts',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.35,
        'flag_check': 'cleared_kobold_mine',
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