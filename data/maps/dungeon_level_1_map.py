"""
Dungeon Level 1 - Ancient Upper Ruins
First level of the cult's sanctum beneath Hill Ruins

Visual tilemap is loaded from dungeon_level_1_tiles.tmj
This file contains game logic: spawn points, transitions, searchables, combat triggers
"""

from utils.constants import BLACK, WHITE, YELLOW, GRAY, DARK_GRAY, FIRE_BRICK_RED, PURPLE_BLUE

# Map dimensions (must match TMJ file)
DUNGEON_L1_WIDTH = 16
DUNGEON_L1_HEIGHT = 16

# Named spawn points for different entrances
DUNGEON_L1_SPAWN_POINTS = {
    'from_hill_ruins': (1, 1),      # Stairs up position
    'from_level_2': (10, 14),       # Stairs down position
    'default': (1, 1)
}

# Legacy support
DUNGEON_L1_SPAWN_X = DUNGEON_L1_SPAWN_POINTS['default'][0]
DUNGEON_L1_SPAWN_Y = DUNGEON_L1_SPAWN_POINTS['default'][1]

# === AREA TRANSITIONS ===
# These define where players can move between areas
AREA_TRANSITIONS = {
    'return_to_hill_ruins': {
        'entrance_tiles': [(1, 1), (2, 1)],  # Stairs up area
        'building_pos': [(1, 1)],
        'info': {
            'name': 'Return to Hill Ruins',
            'interaction_type': 'navigation',
            'target_screen': 'hill_ruins_ground_level_nav',
            'action': 'Ascend to Hill Ruins',
            'requirements': {}
        }
    },
    'descend_to_level_2': {
        'entrance_tiles': [(10, 14), (11, 14)],  # Stairs down area
        'building_pos': [(10, 14)],
        'info': {
            'name': 'Descend to Level 2',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_2_nav',
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

# === SEARCHABLE OBJECTS ===
# These are objects players can examine and interact with
SEARCHABLE_OBJECTS = {
    'healing_altar': {
        'search_tiles': [(3, 10), (4, 10), (3, 12), (4, 12)],  # Altar position (visible in Walls layer)
        'object_pos': [(3, 11), (4, 11)],
        'info': {
            'name': 'Ancient Altar',
            'interaction_type': 'searchable',
            'description': 'A stone altar with healing properties',
            'examine_dialogue': 'dungeon_level_1_altar',
            'flag_set': 'dungeon_level_1_altar_used',
            'requirements': {},
            'one_time': False
        }
    },
    'treasure_chest': {
        'search_tiles': [(1, 13), (3, 13),(2,14), (2,12),(3,13),(1,13)],  # Chest position (visible in Details layer)
        'object_pos': [(2, 13)],
        'info': {
            'name': 'Ancient Chest',
            'interaction_type': 'searchable',
            'description': 'A locked chest from ancient times',
            'examine_dialogue': 'dungeon_level_1_chest',
            'loot_table': 'dungeon_level_1_chest_loot',
            'flag_set': 'dungeon_l1_chest_opened',
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

# === COMBAT TRIGGERS ===
# These are tiles that trigger combat when stepped on
# Positions should correspond to open floor areas in the tilemap
COMBAT_TRIGGERS = {
    (6, 4): {  # Combat zone in upper area
        'encounter_id': 'dungeon_l1_skeleton_patrol',
        'trigger_type': 'step_on',
        'repeatable': False,
        'completion_flag': 'dungeon_l1_encounter_1_complete'
    },
    (10, 8): {  # Combat zone in middle area
        'encounter_id': 'dungeon_l1_animated_armor',
        'trigger_type': 'step_on',
        'repeatable': False,
        'completion_flag': 'dungeon_l1_encounter_2_complete'
    },
    (6, 13): {  # Combat zone in lower area
        'encounter_id': 'dungeon_l1_shadow_wraith',
        'trigger_type': 'step_on',
        'repeatable': False,
        'completion_flag': 'dungeon_l1_encounter_3_complete'
    }
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

# === NPC DEFINITIONS ===
LOCATION_NPCS = {}  # No NPCs in this dungeon level

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS


# === LEGACY TILE FUNCTIONS ===
# These are kept for backwards compatibility but are not actively used
# Visual rendering comes from dungeon_level_1_tiles.tmj

# Tile type definitions (legacy)
TILE_TYPES = {
    '#': 'wall',
    '.': 'floor',
    'U': 'stairs_up',
    'S': 'stairs_down',
    'P': 'pillar',
    '~': 'combat_zone',
    'A': 'altar',
    'X': 'chest'
}

WALKABLE_TILES = {'floor', 'stairs_up', 'stairs_down', 'combat_zone', 'altar', 'chest'}

# ASCII map layout (legacy - visual comes from TMJ now)
DUNGEON_L1_MAP = [
    "################",
    "#U.............#",         # Stairs up
    "#..............#",
    "#..PP......PP..#",         # Pillar
    "#.....~........#",         # Combat zone
    "#..............#",
    "#.......A......#",         # Altar
    "#..............#",
    "#.........~....#",
    "#..PP..........#",         # Pillar
    "#..............#",
    "#........X.....#",         # Chest
    "#..............#",
    "#.....~........#",         # Combat zone
    "#.........S....#",         # Stairs down
    "################"
]

def get_tile_type(x, y, tile_grid=None):
    """Get tile type at coordinates (legacy function)"""
    if tile_grid:
        # New system: use provided tile grid
        if 0 <= y < len(tile_grid) and 0 <= x < len(tile_grid[0]):
            return tile_grid[y][x]
        return None
    else:
        # Legacy system: use ASCII map
        if 0 <= y < DUNGEON_L1_HEIGHT and 0 <= x < DUNGEON_L1_WIDTH:
            char = DUNGEON_L1_MAP[y][x]
            return TILE_TYPES.get(char, 'wall')
        return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable (legacy function)"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_tile_color(x, y):
    """Get color for tile rendering (legacy function)"""
    tile_type = get_tile_type(x, y)
    TILE_COLORS = {
        'wall': (40, 40, 40),
        'floor': (60, 60, 60),
        'stairs_up': (100, 100, 150),
        'stairs_down': (150, 50, 50),
        'pillar': GRAY,
        'combat_zone': FIRE_BRICK_RED,
        'altar': PURPLE_BLUE,
        'chest': YELLOW
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))
