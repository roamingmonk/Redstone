"""
Red Hollow Mine Level 3 Map Data
15x15 tile grid for deepest chamber with ritual site and secret tunnel
CRITICAL: Secret tunnel discovery enables Act III alternate path
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

MINE_L3_WIDTH = 15
MINE_L3_HEIGHT = 15
MINE_L3_SPAWN_X = 7
MINE_L3_SPAWN_Y = 1  # Enter from top (descending from Level 2)


# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Deep chamber walls
    '.': 'ground',        # Walkable chamber floor
    'O': 'ore_crystal',   # Large Aethel Ore deposits (searchable - CRITICAL)
    'r': 'ritual_site',   # Ritual area (examinable for lore)
    'T': 'secret_tunnel', # Secret tunnel entrance (searchable - ACT III FLAG!)
    'U': 'stairs_up',     # Return to Level 2
    'c': 'crystal',       # Glowing crystal formations
    'p': 'pillar',        # Ancient stone pillars
    'S': 'shaft_up',       # Quick shaft to surface
}

WALKABLE_TILES = {'ground', 'ore_crystal', 'ritual_site', 'secret_tunnel', 'stairs_up'}

# ASCII map layout - 15x15 grid
MINE_L3_MAP = [
    "#######U#######",  # Row 0
    "#.............#",  # Row 1 - U = stairs up to Level 2
    "#p...........p#",  # Row 2
    "#.............#",  # Row 3
    "#...ccc.ccc...#",  # Row 4 - c = glowing crystals
    "#..cOOOcOOOc..#",  # Row 5 - O = Aethel Ore deposits (searchable)
    "#..cOOO.OOOc..#",  # Row 6
    "#...cccrccc...#",  # Row 7 - r = ritual site center
    "#p....rrr....p#",  # Row 8 - ritual area
    "#.....rrr.....#",  # Row 9
    "#.............#",  # Row 10
    "#.............#",  # Row 11
    "##SS..TTT.....#",  # Row 12 - T = SECRET TUNNEL (behind ore deposits)
    "#pSS..TTT....p#",  # Row 13 - S = Shaft to the surface
    "###############"   # Row 14
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < MINE_L3_HEIGHT and 0 <= x < MINE_L3_WIDTH:
        char = MINE_L3_MAP[y][x]
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
        'wall': (35, 25, 15),            # Very dark (deepest mine)
        'ground': (55, 45, 35),          # Dark chamber floor
        'ore_crystal': (100, 220, 255),  # Bright glowing ore (HIGHLIGHT)
        'ritual_site': (120, 100, 80),   # Ancient stone (HIGHLIGHT)
        'secret_tunnel': (80, 60, 40),   # Dark passage (CRITICAL HIGHLIGHT)
        'stairs_up': (100, 80, 60),      # Stairs
        'crystal': (150, 200, 255),      # Glowing blue crystals
        'pillar': (90, 80, 70),          # Ancient stone pillars
        'shaft_up': (100, 100, 120),     # Gray shaft
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'return_to_level_2': {
        'entrance_tiles': [(7, 1), (6, 1), (8, 1),(7, 0)],  # Stairs up area
        'building_pos': [(7, 0)],
        'info': {
            'name': 'Return to Level 2',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_2_nav',
            'action': 'Ascend to Level 2',
            'requirements': {}
        }
    },
    'shaft_to_surface': {
        'entrance_tiles': [(2, 11), (3, 11), (4, 12), (4, 13)],
        'building_pos': [(2, 12), (3, 12), (2, 13), (3, 13)],
        'info': {
            'name': 'Shaft to Surface',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_pre_entrance_nav',
            'action': 'Climb shaft to surface (Quick Exit)',
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

# Searchable objects - CRITICAL DISCOVERIES
SEARCHABLE_OBJECTS = {
    'ritual_chamber': {
        'search_tiles': [(7, 7), (6, 8), (7, 8), (8, 8), (6, 9), (7, 9), (8, 9)],  # Ritual area
        'object_pos': [(7, 8)],
        'info': {
            'name': 'Ancient Ritual Site',
            'interaction_type': 'searchable',
            'description': 'Strange symbols and ritual implements surround this area.',
            'examine_dialogue': 'mine_ritual_chamber',
            'loot_table': None,
            'flag_set': 'examined_ritual_chamber',
            'requirements': {},
            'one_time': True
        }
    },
    'deep_ore_deposits': {
        'search_tiles': [(4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6)],  # Ore area
        'object_pos': [(5, 5), (6, 5), (8, 5), (9, 5)],
        'info': {
            'name': 'Aethel Ore Deposits',
            'interaction_type': 'searchable',
            'description': 'Massive crystalline ore formations pulse with energy.',
            'examine_dialogue': 'mine_deep_ore',
            'loot_table': 'mine_deep_ore_loot',
            'flag_set': 'searched_deep_ore_chamber',
            'requirements': {},
            'one_time': True
        }
    },
    'secret_tunnel_entrance': {
        'search_tiles': [(5, 12), (6, 12), (7, 12), (8, 12), (9, 12), (5, 13), (6, 13), (7, 13), (8, 13), (9, 13)],  # Tunnel area
        'object_pos': [(6, 12), (7, 12), (8, 12), (6, 13), (7, 13), (8, 13)],
        'info': {
            'name': 'Hidden Passage',
            'interaction_type': 'searchable',
            'description': 'A dark tunnel carved through the rock, leading toward the hill ruins...',
            'examine_dialogue': 'mine_secret_tunnel',
            'loot_table': None,
            'flag_set': 'red_hollow_mine_secret_entrance_found',  # CRITICAL ACT III FLAG!
            'requirements': {
                'examined_ritual_chamber': True  # Must examine ritual site first
            },
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

# No combat triggers in Level 3 (final chamber, exploration focus)
COMBAT_TRIGGERS = {}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

LOCATION_NPCS = {}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS