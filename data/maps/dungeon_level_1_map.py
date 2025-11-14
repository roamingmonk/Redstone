"""
Dungeon Level 1 - Ancient Upper Ruins
First level of the cult's sanctum beneath Hill Ruins
"""

from utils.constants import BLACK, WHITE, YELLOW, GRAY, DARK_GRAY, FIRE_BRICK_RED, PURPLE_BLUE

DUNGEON_L1_WIDTH = 16
DUNGEON_L1_HEIGHT = 16

# Named spawn points for different entrances
DUNGEON_L1_SPAWN_POINTS = {
    'from_hill_ruins': (1, 1),
    'from_level_2': (11, 14),
    'default': (1, 1)
}

# Legacy support
DUNGEON_L1_SPAWN_X = DUNGEON_L1_SPAWN_POINTS['default'][0]
DUNGEON_L1_SPAWN_Y = DUNGEON_L1_SPAWN_POINTS['default'][1]

# Tile type definitions
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

# ASCII map layout - 16x16 grid
DUNGEON_L1_MAP = [
    "################",
    "#U.............#",         #Stairs up
    "#..............#",
    "#..PP......PP..#",         #pillar
    "#.....~........#",         #combat zone
    "#..............#",
    "#.......A......#",         #Altar
    "#..............#",
    "#.........~....#",
    "#..PP..........#",         #Pillar
    "#..............#",
    "#........X.....#",        # Chest
    "#..............#",
    "#.....~........#",        # combat zone
    "#.........S....#",        # Stairs down
    "################"
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < DUNGEON_L1_HEIGHT and 0 <= x < DUNGEON_L1_WIDTH:
        char = DUNGEON_L1_MAP[y][x]
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
        'wall': (40, 40, 40),
        'floor': (60, 60, 60),
        'stairs_up': (100, 100, 150),
        'stairs_down': (150, 50, 50),
        'pillar': (GRAY),
        'combat_zone': (FIRE_BRICK_RED),
        'altar': (PURPLE_BLUE),
        'chest': (YELLOW)
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'return_to_hill_ruins': {
        'entrance_tiles': [(1, 1), (2, 1)],
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
        'entrance_tiles': [(10, 14), (11, 14)],
        'building_pos': [(11, 14)],
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

# Searchable objects
SEARCHABLE_OBJECTS = {
    'healing_altar': {
        'search_tiles': [(7, 6)],
        'object_pos': [(7, 6)],
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
        'search_tiles': [(9, 11)],
        'object_pos': [(9, 11)],
        'info': {
            'name': 'Ancient Chest',
            'interaction_type': 'searchable',
            'description': 'A locked chest from ancient times',
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

# Combat triggers
COMBAT_TRIGGERS = {
    (6, 4): {
        'encounter_id': 'dungeon_l1_skeleton_patrol',
        'trigger_type': 'step_on',
        'repeatable': False,
        'completion_flag': 'dungeon_l1_encounter_1_complete'
    },
    (10, 8): {
        'encounter_id': 'dungeon_l1_animated_armor',
        'trigger_type': 'step_on',
        'repeatable': False,
        'completion_flag': 'dungeon_l1_encounter_2_complete'
    },
    (6, 13): {
        'encounter_id': 'dungeon_l1_shadow_wraith',
        'trigger_type': 'step_on',
        'repeatable': False,
        'completion_flag': 'dungeon_l1_encounter_3_complete'
    }
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

LOCATION_NPCS = {}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS