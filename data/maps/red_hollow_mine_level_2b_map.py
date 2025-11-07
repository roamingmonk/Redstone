"""
Red Hollow Mine Level 2B Map Data
12x12 tile grid for collapsed dead end passage
High risk area with spider ambush and better loot
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

MINE_L2B_WIDTH = 12
MINE_L2B_HEIGHT = 12
MINE_L2B_SPAWN_X = 1
MINE_L2B_SPAWN_Y = 6  # Enter from left side

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Collapsed rock
    '.': 'ground',        # Walkable tunnel floor
    'R': 'rubble',        # Rubble piles (searchable - GOOD LOOT)
    'S': 'spider_zone',   # Spider ambush zone (50% chance)
    'w': 'web',           # Spider webs (not walkable but visual)
    'X': 'collapse',      # Collapsed tunnel (not walkable, examinable)
    'E': 'exit_passage',  # Return to Level 2
}

WALKABLE_TILES = {'ground', 'rubble', 'spider_zone', 'web', 'exit_passage'}

# ASCII map layout - 12x12 grid (small, claustrophobic)
MINE_L2B_MAP = [
    "############",  # Row 0
    "#..........#",  # Row 1
    "#w.........#",  # Row 2 - w = webs
    "#www.......#",  # Row 3
    "#ww..S.....#",  # Row 4 - S = spider ambush zone (50%)
    "#w...SS....#",  # Row 5
    "E...SSSS...#",  # Row 6 - E = exit back to Level 2
    "#....SSS...#",  # Row 7
    "#....SRR..X#",  # Row 8 - R = rubble (loot), X = collapse
    "#....S.R.XX#",  # Row 9
    "#.....S...X#",  # Row 10 - X = collapsed dead end
    "############"   # Row 11
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < MINE_L2B_HEIGHT and 0 <= x < MINE_L2B_WIDTH:
        char = MINE_L2B_MAP[y][x]
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
        'wall': (40, 30, 20),            # Very dark brown (unstable)
        'ground': (60, 50, 40),          # Dark tunnel floor
        'rubble': (130, 120, 100),       # Lighter rubble (HIGHLIGHT - loot!)
        'spider_zone': (65, 55, 45),     # Slightly darker ground
        'web': (220, 220, 220),          # White/gray webbing
        'collapse': (30, 25, 20),        # Very dark collapsed rock
        'exit_passage': (70, 60, 50),    # Passage back
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'return_to_level_2': {
        'entrance_tiles': [(0, 6), (1, 6)],  # Left side exit
        'building_pos': [(0, 6)],
        'info': {
            'name': 'Return to Level 2',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_2_nav',
            'action': 'Return to Main Shafts',
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
    'valuable_rubble': {
        'search_tiles': [(7, 8), (8, 8), (7, 9)],  # Rubble piles
        'object_pos': [(7, 8), (8, 8), (7, 9)],
        'info': {
            'name': 'Rubble Pile',
            'interaction_type': 'searchable',
            'description': 'Collapsed rock and debris. Something glints within...',
            'examine_dialogue': 'mine_rubble',
            'loot_table': 'mine_rubble_loot',  # Better loot (risk/reward)
            'flag_set': 'searched_mine_rubble',
            'requirements': {},
            'one_time': True
        }
    },
    'collapsed_tunnel': {
        'search_tiles': [(9, 8), (10, 8), (10, 9), (10, 10)],  # Collapse area
        'object_pos': [(10, 8), (10, 9)],
        'info': {
            'name': 'Collapsed Tunnel',
            'interaction_type': 'searchable',
            'description': 'A complete cave-in blocks further progress.',
            'examine_dialogue': 'mine_collapse',
            'loot_table': None,
            'flag_set': 'examined_collapse',
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

# Combat triggers - Giant spider ambush (50% chance - HIGH RISK!)
COMBAT_TRIGGERS = {
    (5, 4): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (4, 5): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (5, 5): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (4, 6): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (5, 6): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (6, 6): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (7, 6): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (5, 7): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (6, 7): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (7, 7): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (5, 8): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (5, 9): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None},
    (6, 10): {'encounter_id': 'mine_spider_ambush', 'trigger_type': 'step_on', 'repeatable': True, 'chance': 0.50, 'flag_check': None, 'flag_set': None}
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

LOCATION_NPCS = {}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS