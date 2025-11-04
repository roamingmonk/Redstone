"""
Refugee Camp Main Area Map Data
20x20 tile grid for explorable refugee camp
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

REFUGEE_CAMP_WIDTH = 20
REFUGEE_CAMP_HEIGHT = 20
REFUGEE_CAMP_SPAWN_X = 10
REFUGEE_CAMP_SPAWN_Y = 18  # Enter from bottom (arriving from regional map)

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Map boundary
    '.': 'ground',        # Walkable grass/dirt
    'g': 'grass',         # Grass (walkable)
    't': 'tent',          # Tent (not walkable)
    'f': 'fire',          # Campfire (not walkable)
    's': 'supplies',      # Supply crates (searchable)
    'p': 'path',          # Dirt path (walkable)
    'T': 'tree',          # Trees (not walkable)
    'L': 'leader',        # Camp leader position (walkable, NPC marker)
    'R': 'refugees',      # Refugee position (walkable, NPC marker)
    'E': 'exit_path',     # Exit back to map
}

WALKABLE_TILES = {'ground', 'grass', 'path', 'leader', 'refugees', 'fire', 'supplies', 'exit_path'}

# ASCII map layout - 20x20 grid
REFUGEE_CAMP_MAP = [
    "####################",  # Row 0
    "#TTggggggggggggTTTT#",  # Row 1 - Trees at edges
    "#Tggttgg...gggttggg#",  # Row 2 - Tents
    "#gggggggg.ggggggggg#",  # Row 3
    "#ggttgg...........g#",  # Row 4 - Tents
    "#ggttgg...........g#",  # Row 5
    "#ggggg............g#",  # Row 6
    "#ggggg.ssg........g#",  # Row 7 - Supplies (searchable)
    "#ggggg.ssg...ttgg.g#",  # Row 8
    "#gggg......ffL....g#",  # Row 9 - Fire & Leader
    "#gggg......ffR....g#",  # Row 10 - Fire & Refugees
    "#ggggg............g#",  # Row 11
    "#gttgg............g#",  # Row 12 - Tents
    "#gttgg............g#",  # Row 13
    "#ggggg............g#",  # Row 14
    "#gggg.ttgg....gggg#",  # Row 15 - More tents
    "#gggg.ttgg....gggg#",  # Row 16
    "#ggggggggg....gggg#",  # Row 17
    "#ggggggggpppppgggg#",  # Row 18 - Path/spawn
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < REFUGEE_CAMP_HEIGHT and 0 <= x < REFUGEE_CAMP_WIDTH:
        char = REFUGEE_CAMP_MAP[y][x]
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
        'wall': (60, 60, 60),              # Dark gray boundary
        'ground': (100, 130, 70),          # Green grass
        'grass': (85, 120, 60),            # Grass
        'tent': (210, 180, 140),           # Tan canvas
        'fire': (255, 140, 0),             # Orange fire
        'supplies': (139, 90, 43),         # Brown crates (HIGHLIGHT)
        'path': (120, 100, 70),            # Brown dirt path
        'tree': (34, 80, 34),              # Dark green
        'leader': (100, 140, 80),          # Slightly different grass (subtle)
        'refugees': (95, 135, 75),         # Slightly different grass (subtle)
        'exit_path': (110, 90, 60),        # Path color
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions (navigation between areas/screens)
AREA_TRANSITIONS = {
    'return_to_region': {
        'entrance_tiles': [(10, 18), (11, 18), (12, 18), (10, 17), (11, 17), (12, 17)],  # Bottom spawn area
        'building_pos': [(11, 18)],
        'info': {
            'name': 'Leave Camp',
            'interaction_type': 'navigation',
            'target_screen': 'exploration_hub',  # Back to regional map
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

# Searchable objects (examine/loot)
SEARCHABLE_OBJECTS = {
    'camp_leader': {
        'search_tiles': [(11, 9), (12, 9)],  # Just around leader position
        'object_pos': [(11, 9)],
        'info': {
            'name': 'Camp Leader',
            'interaction_type': 'searchable',
            'description': 'Marta stands near the central campfire.',
            'examine_dialogue': 'refugee_camp_leader',
            'loot_table': None,
            'flag_set': None,
            'requirements': {},
            'one_time': False
        }
    },
    'refugees': {
        'search_tiles': [(11, 10), (12, 10)],  # Different tiles for refugees
        'object_pos': [(12, 10)],
        'info': {
            'name': 'Displaced Refugees',
            'interaction_type': 'searchable',
            'description': 'Displaced families huddle near the fire.',
            'examine_dialogue': 'refugee_camp_refugees',
            'loot_table': None,
            'flag_set': None,
            'requirements': {},
            'one_time': False
        }
    },
    'supply_crates': {
        'search_tiles': [(7, 7), (8, 7), (7, 8), (8, 8)],
        'object_pos': [(7, 7), (8, 7)],
        'info': {
            'name': 'Supply Crates',
            'interaction_type': 'searchable',
            'description': 'Communal supplies and scattered belongings.',
            'examine_dialogue': 'refugee_camp_supplies',
            'loot_table': None,
            'flag_set': 'searched_refugee_supplies',
            'requirements': {},
            'one_time': True
        }
    },
    'central_campfire': {
        'search_tiles': [(10, 9), (10, 10)],  # Different tiles, away from NPCs
        'object_pos': [(10, 9), (10, 10)],
        'info': {
            'name': 'Central Campfire',
            'interaction_type': 'searchable',
            'description': 'A large campfire providing warmth and light.',
            'examine_dialogue': 'refugee_camp_campfire',
            'loot_table': None,
            'flag_set': 'examined_refugee_campfire',
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

# Combat triggers (random encounters) - None in main camp area
COMBAT_TRIGGERS = {}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

# Alias for compatibility
get_transition_at_entrance = get_transition_info