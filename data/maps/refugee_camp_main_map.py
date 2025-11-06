"""
Refugee Camp Main Area Map Data
20x20 tile grid for explorable refugee camp
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW, DARK_GREEN, PURPLE, PURPLE_BLUE,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

REFUGEE_CAMP_WIDTH = 20
REFUGEE_CAMP_HEIGHT = 20
REFUGEE_CAMP_SPAWN_X = 10
REFUGEE_CAMP_SPAWN_Y = 18  # Enter from bottom (arriving from regional map)

# Tile type definitions
TILE_TYPES = {
    '#': 'hedge_wall',    # Map boundary
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

WALKABLE_TILES = {'ground', 'grass', 'path', 'exit_path'}

# ASCII map layout - 20x20 grid
REFUGEE_CAMP_MAP = [
    "TTTTTTTTTTTTTTTTTTTT",  # Row 0 - Trees
    "TTTggggggggggggTTTTT",  # Row 1 - 
    "TTggTggg...gggttggTT",  # Row 2 - 
    "T#gg.ggTg.ggggggggTT",  # Row 3
    "##gT......t......gTT",  # Row 4 - Tents
    "#gggg.....t..t.t.gTT",  # Row 5 - Tents
    "##ggg.g......t.t.ggT",  # Row 6 - Tents
    "##gTgggss........ggT",  # Row 7 - Supplies (searchable)
    "##gggggss..L...ggggT",  # Row 8 - Campfire
    "##gggg.....f.....ggT",  # Row 9 - Leader
    "##ggg......f.....gTT",  # Row 10  
    "##gggg.tt..R...ttgTT",  # Row 11 - Tents, Refugees
    "##ttgg...........gTT",  # Row 12 - Campfire
    "##ttgg.tt......tggTT",  # Row 13 - Tents
    "##gggg...g......ggTT",  # Row 14
    "##ggg..ttgg....gggTT",  # Row 15 - More tents
    "##ggg..ttgg....gggTT",  # Row 16 - Even more tents
    "###ggggggg.....gggTT",  # Row 17
    "####ggggggg...gggTTT",  # Row 18 - Spawn
    "##########ppEpp#TTTT"   # Row 19 - Path / exit
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
        'hedge_wall': DARK_GREEN,        # Dark gray boundary
        'ground': (100, 130, 70),          # Green grass
        'grass': (85, 120, 60),            # Grass
        'tent': (210, 180, 140),           # Tan canvas
        'fire': (255, 140, 0),             # Orange fire
        'supplies': (139, 90, 43),         # Brown crates (HIGHLIGHT)
        'path': (120, 100, 70),            # Brown dirt path
        'tree': (34, 80, 34),              # Dark green
        'leader': PURPLE,          # Slightly different grass (subtle)(100, 140, 80)
        'refugees': PURPLE_BLUE,         # Slightly different grass (subtle)(95, 135, 75)
        'exit_path': (110, 90, 60),        # Path color
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions (navigation between areas/screens) - (column, row)
AREA_TRANSITIONS = {
    'return_to_region': {
        'entrance_tiles': [(10, 19), (11, 19), (12, 19), (13, 19), (14, 19)],
        'building_pos': [(11, 18)],
        'info': {
            'name': 'Leave Camp',
            'interaction_type': 'navigation',
            'target_screen': 'exploration_hub',
            'action': 'Return to Region Map',
            'requirements': {
                #'flags_any_false': ['agreed_to_defend_camp']  # Can only leave if NOT agreed to defend
            },
            'blocked_message': 'You agreed to help defend the camp. Speak with Marta when you\'re ready to rest.'
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
        'search_tiles': [(11, 7), (12, 8), (10,8)],  # Just around leader position
        'object_pos': [(11, 8)],
        'info': {
            'name': 'Camp Leader',
            'interaction_type': 'searchable',
            'description': 'Marta stands near the central campfire.',
            'examine_dialogue': 'refugee_camp_marta',
            'loot_table': None,
            'flag_set': None,
            'requirements': {},
            'one_time': False
        }
    },
    'refugees': {
        'search_tiles': [(10, 11), (12, 11), (11,12)],  # Different tiles for refugees
        'object_pos': [(11, 11)],
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
        'search_tiles': [(9, 7), (8, 6), (9, 8), (8, 9), (7,6), (7,9)],
        'object_pos': [(7, 7), (8, 7), (8,7), (8,8)],
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
        'search_tiles': [(10, 9), (10, 10), (12,9), (12, 10)],  # Different tiles, away from NPCs
        'object_pos': [(11, 9), (11, 10)],
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