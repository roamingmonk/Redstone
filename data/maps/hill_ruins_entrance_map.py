"""
Hill Ruins Entrance Map Data
20x20 tile grid for windswept hilltop ruins exploration
"""

from utils.constants import (
    # Colors
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    # Buttons
    BUTTON_SIZES, SCREEN_WIDTH
)

HILL_RUINS_ENT_WIDTH = 20
HILL_RUINS_ENT_HEIGHT = 20
HILL_RUINS_ENT_SPAWN_X = 10
HILL_RUINS_ENT_SPAWN_Y = 18  # Enter from bottom (arriving from regional map)

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Map boundary/impassable terrain
    '.': 'ground',        # Walkable grass/dirt
    'g': 'grass',         # Grass (walkable)
    'r': 'rubble',        # Rubble pile (searchable)
    'w': 'wall_remains',  # Crumbled wall sections (not walkable)
    'c': 'carved_stone',  # Carved standing stones (searchable)
    'D': 'ruins_door',    # Door to ground level interior
    'E': 'exit_path',     # Path back to regional map
    '~': 'combat_zone',   # Random combat trigger (walkable but dangerous)
    't': 'tree',          # Trees/vegetation (not walkable)
}

WALKABLE_TILES = {'ground', 'grass', 'rubble', 'carved_stone', 'ruins_door', 
                  'exit_path', 'combat_zone'}

# ASCII map layout - 20x20 grid
HILL_RUINS_ENT_MAP = [
    "####################",  # Row 0
    "#gggggggggggggggggg#",  # Row 1
    "#ggwwwww......gggg.#",  # Row 2 - Crumbled walls
    "#gg.................#",  # Row 3
    "#gg...rrrr.........g#",  # Row 4 - Rubble pile (searchable)
    "#gg...rrrr.........g#",  # Row 5
    "#gg................g#",  # Row 6
    "#ggwwwwwwww.....ggg#",  # Row 7 - Wall remains
    "#gg...~....D.......g#",  # Row 8 - Door entrance, combat trigger
    "#gg................g#",  # Row 9
    "#ggcc..............g#",  # Row 10 - Carved stones (lore/searchable)
    "#ggcc..............g#",  # Row 11
    "#gg................g#",  # Row 12
    "#gg~...............g#",  # Row 13 - Combat trigger
    "#gg................g#",  # Row 14
    "#gg................g#",  # Row 15
    "#gggggggg..........g#",  # Row 16
    "#ggggggggg..E.....gg#",  # Row 17 - Exit
    "#gggggggggg.......gg#",  # Row 18 - spawn point
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < HILL_RUINS_ENT_HEIGHT and 0 <= x < HILL_RUINS_ENT_WIDTH:
        char = HILL_RUINS_ENT_MAP[y][x]
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
        'ground': (120, 100, 70),          # Brown/tan earth
        'grass': (85, 107, 47),            # Olive/dark green grass
        'rubble': (150, 130, 100),         # Tan rubble (HIGHLIGHT for searchable)
        'wall_remains': (100, 100, 100),   # Gray crumbled walls
        'carved_stone': (180, 160, 140),   # Light tan carved stones (HIGHLIGHT)
        'ruins_door': (101, 67, 33),       # Dark brown door
        'exit_path': (110, 90, 60),        # Slightly darker path
        'combat_zone': (125, 105, 75),     # Slightly different ground (subtle)
        'tree': (34, 80, 34),              # Dark green trees
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions (navigation between areas/screens)
AREA_TRANSITIONS = {
    'ruins_entrance': {
        'entrance_tiles': [(11, 7), (12, 7), (11, 8), (12, 8)],  # Standing near door
        'building_pos': [(11, 8)],    # Door tile position
        'info': {
            'name': 'Ruined Structure Entrance',
            'interaction_type': 'navigation',
            'target_screen': 'hill_ruins_ground_level_nav',  # Interior map screen
            'action': 'Enter the Ruins',
            'requirements': {}  # No special requirements to enter
        }
    },
    'return_to_region': {
        'entrance_tiles': [(12, 17), (12, 18)],  # Bottom spawn area
        'building_pos': [(12, 17)],
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
    'ancient_rubble': {
        'search_tiles': [(6, 4), (7, 4), (8, 4), (9, 4), 
                        (6, 5), (7, 5), (8, 5), (9, 5)],  # Around rubble
        'object_pos': [(6, 4), (7, 4), (8, 4), (9, 4)],  # Rubble tiles
        'info': {
            'name': 'Ancient Rubble',
            'interaction_type': 'searchable',
            'description': 'Broken stones with faded rune carvings.',
            'examine_dialogue': 'hill_ruins_rubble',
            'loot_table': None,
            'flag_set': 'hill_ruins_rubble_searched',
            'requirements': {},
            'one_time': True
        }
    },
    'carved_stones': {
        'search_tiles': [(4, 10), (5, 10), (4, 11), (5, 11)],  # Around stones
        'object_pos': [(4, 10), (5, 10), (4, 11), (5, 11)],  # Stone tiles
        'info': {
            'name': 'Carved Standing Stones',
            'interaction_type': 'searchable',
            'description': 'Ancient carved stones depicting a great battle.',
            'examine_dialogue': 'hill_ruins_carved_stones',
            'loot_table': None,
            'flag_set': 'hill_ruins_carved_searched',
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
    (6, 8): {  # Combat zone tile
        'encounter_id': 'hill_ruins_bandits',
        'trigger_type': 'step_on',
        'repeatable': True,  # Can re-encounter
        'chance': 0.3,  # 30% chance when stepping on tile
        'flag_check': None,
        'flag_set': None  # Doesn't set flag (repeatable)
    },
    (4, 13): {  # Another combat tile
        'encounter_id': 'hill_ruins_statue',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.35,  # 35% chance
        'flag_check': None,
        'flag_set': None
    }
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

# NPCs in this area (optional)
LOCATION_NPCS = {}  # No NPCs in entrance for now

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS