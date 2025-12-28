"""
Dungeon Level 2 - Ancient Lower Ruins
18x18 tile grid - Deeper into the ancient structure

Visual tilemap is loaded from dungeon_level_2_tiles.tmj
This file contains game logic: spawn points, transitions, searchables, combat triggers
"""

from utils.constants import (
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    BUTTON_SIZES, SCREEN_WIDTH
)

# Map dimensions (must match TMJ file)
DUNGEON_L2_WIDTH = 18
DUNGEON_L2_HEIGHT = 18

# Spawn points for different entry methods
DUNGEON_L2_SPAWN_POINTS = {
    'from_level_1': (9, 1),         # Top center, at stairs up (Details layer tile 40)
    'from_level_3': (9, 16),        # Bottom center, at stairs down (Details layer tile 39)
    'default': (9, 1)
}

# Legacy support
DUNGEON_L2_SPAWN_X = DUNGEON_L2_SPAWN_POINTS['default'][0]
DUNGEON_L2_SPAWN_Y = DUNGEON_L2_SPAWN_POINTS['default'][1]

# === AREA TRANSITIONS ===
# These define where players can move between areas
AREA_TRANSITIONS = {
    'stairs_to_level_3': {
        'entrance_tiles': [(9, 16), (8, 16), (10, 16), (9,15)],  # Around stairs down
        'building_pos': [(9, 16)],
        'info': {
            'name': 'Descending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_3_nav',
            'action': 'Descend to Level 3',
            'requirements': {}
        }
    },
    'stairs_to_level_1': {
        'entrance_tiles': [(9, 1), (9, 2), (10, 1)],  # Around stairs up
        'building_pos': [(9, 1)],
        'info': {
            'name': 'Ascending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_1_nav',
            'action': 'Return to Level 1',
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

# === SEARCHABLE OBJECTS ===
# These are objects players can examine and interact with
SEARCHABLE_OBJECTS = {
    'treasure_chest': {
        'search_tiles': [(4, 12), (6, 12), (3, 13), (3, 14)],  
        'object_pos': [(5, 12)],
        'info': {
            'name': 'Ancient Treasure Chest',
            'interaction_type': 'searchable',
            'description': 'A reinforced chest half-buried in rubble.',
            'examine_dialogue': 'dungeon_level_2_chest',
            'loot_table': 'dungeon_level_2_chest_loot',
            'flag_set': 'dungeon_level_2_chest_looted',
            'requirements': {},
            'one_time': True
        }
    },
    'bone_pile': {
        'search_tiles': [(5, 12)],  # Debris position (Details layer tile 32)
        'object_pos': [(5, 12)],
        'info': {
            'name': 'Ancient Bone Pile',
            'interaction_type': 'dialogue',
            'description': 'Skeletal remains scattered across the floor.',
            'examine_dialogue': 'dungeon_level_2_bones',
            'loot_table': None,
            'flag_set': 'dungeon_level_2_bones_examined',
            'requirements': {},
            'one_time': True
        }
    }
}

def get_searchable_at_position(player_x, player_y):
    """Check if player is near searchable object"""
    for obj_id, obj_data in SEARCHABLE_OBJECTS.items():
        if (player_x, player_y) in obj_data['search_tiles']:
            return obj_data['info']
    return None

# === COMBAT TRIGGERS ===
# These are tiles that trigger combat when stepped on
# Positions should correspond to open floor areas in the tilemap
COMBAT_ENCOUNTERS = {
    'skeleton_archers': {
        'trigger_tiles': [(5, 4), (6, 4)],  # Upper area
        'encounter_id': 'dungeon_l2_skeleton_archers',
        'one_time': True,
        'completion_flag': 'dungeon_l2_encounter_1_complete',
        'repeatable': False,
        'chance': 1.0
    },
    'animated_armor_patrol': {
        'trigger_tiles': [(10, 9), (11, 9), (12, 9)],  # Middle-right area near altar structure
        'encounter_id': 'dungeon_l2_animated_patrol',
        'one_time': True,
        'completion_flag': 'dungeon_l2_encounter_2_complete',
        'repeatable': False,
        'chance': 1.0
    },
    'trap_ambush': {
        'trigger_tiles': [(3, 14), (4, 14)],  # Lower area
        'encounter_id': 'dungeon_l2_trap_ambush',
        'one_time': True,
        'completion_flag': 'dungeon_l2_encounter_3_complete',
        'repeatable': False,
        'chance': 1.0,
        'trap_damage': '2d6'
    }
}

def get_combat_trigger(x, y):
    """Check if position triggers combat encounter"""
    for encounter_id, encounter_data in COMBAT_ENCOUNTERS.items():
        if (x, y) in encounter_data['trigger_tiles']:
            return encounter_data
    return None

# === ENVIRONMENTAL HAZARDS ===
# These are special tiles that cause environmental damage
ENVIRONMENTAL_HAZARDS = {
    'weak_floor_1': {
        'hazard_tiles': [(11, 6)],  # Right side, mid-upper area
        'hazard_type': 'collapsing_floor',
        'damage': '1d6',
        'message': 'The floor cracks beneath you! You fall through partially before catching yourself.'
    }
}

def get_environmental_hazard(x, y):
    """Check if position has environmental hazard"""
    for hazard_id, hazard_data in ENVIRONMENTAL_HAZARDS.items():
        if (x, y) in hazard_data['hazard_tiles']:
            return hazard_data
    return None


# === LEGACY TILE FUNCTIONS ===
# These are kept for backwards compatibility but are not actively used
# Visual rendering comes from dungeon_level_2_tiles.tmj

# Tile type definitions (legacy)
TILE_TYPES = {
    '#': 'wall',
    '.': 'floor',
    'P': 'pillar',
    'D': 'door',
    'S': 'stairs_down',
    'U': 'stairs_up',
    '~': 'combat_zone',
    'C': 'chest',
    'T': 'trap',
    '+': 'rubble',
    'W': 'weak_floor',
    'B': 'bones',
}

WALKABLE_TILES = {'floor', 'door', 'stairs_down', 'stairs_up', 'combat_zone', 
                  'chest', 'trap', 'rubble', 'weak_floor', 'bones'}

# ASCII map layout (legacy - visual comes from TMJ now)
DUNGEON_L2_MAP = [
    "###################",  # Row 0
    "#........U........#",  # Row 1 - Stairs up (spawn)
    "#.................#",  # Row 2
    "#..PP.........PP..#",  # Row 3 - Pillars
    "#....~............#",  # Row 4 - ENCOUNTER 1
    "#.................#",  # Row 5
    "#..........W......#",  # Row 6 - Weak floor hazard
    "#.....C...........#",  # Row 7 - Chest
    "#..PP.........PP..#",  # Row 8
    "#.................#",  # Row 9
    "#......~..........#",  # Row 10 - ENCOUNTER 2
    "#.................#",  # Row 11
    "#.....B...........#",  # Row 12 - Bone pile
    "#.................#",  # Row 13
    "#..T..............#",  # Row 14 - Trap + encounter
    "#.................#",  # Row 15
    "#........S........#",  # Row 16 - Stairs down
    "###################"   # Row 17
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
        if 0 <= y < DUNGEON_L2_HEIGHT and 0 <= x < DUNGEON_L2_WIDTH:
            char = DUNGEON_L2_MAP[y][x]
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
        'wall': (35, 35, 40),
        'floor': (75, 70, 65),
        'pillar': (55, 50, 45),
        'door': (85, 65, 45),
        'stairs_down': (95, 85, 75),
        'stairs_up': (95, 85, 75),
        'combat_zone': (80, 70, 65),
        'chest': (140, 110, 40),
        'trap': (100, 50, 50),
        'rubble': (65, 60, 55),
        'weak_floor': (85, 75, 70),
        'bones': (120, 115, 110),
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))
