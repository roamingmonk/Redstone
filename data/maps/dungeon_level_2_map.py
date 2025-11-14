"""
Dungeon Level 2 - Ancient Lower Ruins
18x18 tile grid - Deeper into the ancient structure
ZONE 2: Transition between ancient ruins and cult occupation
Enemies: Skeleton Archers, More Animated Armor, Shadow Wraiths
Environmental Hazards: Collapsing floors, trapped corridors
"""

from utils.constants import (
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    BUTTON_SIZES, SCREEN_WIDTH
)

DUNGEON_L2_WIDTH = 18
DUNGEON_L2_HEIGHT = 18

# Starting position (entering from Level 1 - at top stairs)
DUNGEON_L2_SPAWN_X = 1
DUNGEON_L2_SPAWN_Y = 1

# Spawn points for different entry methods
DUNGEON_L2_SPAWN_POINTS = {
    'from_level_1': (1, 1),         # Top of map, at stairs up 'U'
    'from_level_3': (12, 16),       # Bottom of map, at stairs down 'S'
    'default': (1, 1)
}
# Tile type definitions
TILE_TYPES = {
    '#': 'wall',           # Stone walls (impassable)
    '.': 'floor',          # Stone floor (walkable)
    'P': 'pillar',         # Stone pillar (not walkable, cover in combat)
    'D': 'door',           # Wooden door (walkable)
    'S': 'stairs_down',    # Stairs to Level 3
    'U': 'stairs_up',      # Stairs back to Level 1
    '~': 'combat_zone',    # Combat encounter trigger
    'C': 'chest',          # Loot chest (searchable)
    'T': 'trap',           # Trapped floor (damage + combat trigger)
    '+': 'rubble',         # Debris (walkable, slows movement)
    'W': 'weak_floor',     # Collapsing floor (walkable, environmental hazard)
    'B': 'bones',          # Bone pile (searchable, lore)
}

WALKABLE_TILES = {'floor', 'door', 'stairs_down', 'stairs_up', 'combat_zone', 
                  'chest', 'trap', 'rubble', 'weak_floor', 'bones'}

# ASCII map layout - 18x18 grid
# Legend:
#  U = Stairs up to Level 1
#  ~ = Combat encounter
#  T = Trap (damage + combat)
#  C = Chest
#  W = Weak floor (hazard)
#  B = Bone pile (searchable)
#  S = Stairs down to Level 3
#  P = Pillar
#  # = Wall
#  . = Floor

DUNGEON_L2_MAP = [
    "##################",  # Row 0
    "#........U........#",  # Row 1 - Stairs up (spawn)
    "#.................#",  # Row 2
    "#..PP.........PP..#",  # Row 3 - Pillars
    "#....~............#",  # Row 4 - ENCOUNTER 1: Skeleton archers
    "#.................#",  # Row 5
    "#..........W......#",  # Row 6 - Weak floor hazard
    "#.....C...........#",  # Row 7 - Chest
    "#..PP.........PP..#",  # Row 8
    "#.................#",  # Row 9
    "#......~..........#",  # Row 10 - ENCOUNTER 2: Animated armor patrol
    "#.................#",  # Row 11
    "#.....B...........#",  # Row 12 - Bone pile (lore)
    "#.................#",  # Row 13
    "#..T..............#",  # Row 14 - Trap + encounter
    "#.................#",  # Row 15
    "#........S........#",  # Row 16 - Stairs down
    "##################"   # Row 17
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < DUNGEON_L2_HEIGHT and 0 <= x < DUNGEON_L2_WIDTH:
        char = DUNGEON_L2_MAP[y][x]
        return TILE_TYPES.get(char, 'wall')
    return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_tile_color(x, y):
    """
    Get color for tile rendering
    TODO: Replace with proper tileset graphics
    These are PLACEHOLDER colors for testing
    """
    tile_type = get_tile_type(x, y)
    TILE_COLORS = {
        'wall': (35, 35, 40),           # Darker stone walls
        'floor': (75, 70, 65),          # Gray stone floor
        'pillar': (55, 50, 45),         # Darker stone pillar
        'door': (85, 65, 45),           # Wooden door
        'stairs_down': (95, 85, 75),    # Lighter stone (highlight)
        'stairs_up': (95, 85, 75),      # Lighter stone (highlight)
        'combat_zone': (80, 70, 65),    # Slightly different floor
        'chest': (140, 110, 40),        # Gold/brown chest (highlight)
        'trap': (100, 50, 50),          # Reddish (danger)
        'rubble': (65, 60, 55),         # Darker debris
        'weak_floor': (85, 75, 70),     # Slightly cracked floor
        'bones': (120, 115, 110),       # Pale bones (highlight)
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'stairs_to_level_3': {
        'entrance_tiles': [(9, 16), (8, 16), (10, 16)],  # Around stairs
        'building_pos': [(9, 16)],
        'info': {
            'name': 'Descending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_3_nav',
            'action': 'Descend to Level 3',
            'requirements': {'flag': 'dungeon_level_2_complete'}
        }
    },
    'stairs_to_level_1': {
        'entrance_tiles': [(9, 1), (8, 1), (10, 1)],  # Stairs up
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

# Searchable objects
SEARCHABLE_OBJECTS = {
    'treasure_chest': {
        'search_tiles': [(7, 7), (6, 7), (8, 7)],
        'object_pos': [(7, 7)],
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
        'search_tiles': [(6, 12), (7, 12), (5, 12)],  # Around bones
        'object_pos': [(6, 12)],
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

# Combat encounters
COMBAT_ENCOUNTERS = {
    'skeleton_archers': {
        'trigger_tiles': [(5, 4), (6, 4), (7, 4)],  # Combat zone 1
        'encounter_id': 'dungeon_l2_skeleton_archers',
        'one_time': True,
        'completion_flag': 'dungeon_l2_encounter_1_complete',
        'repeatable': False,
        'chance': 1.0
    },
    'animated_armor_patrol': {
        'trigger_tiles': [(7, 10), (8, 10), (6, 10)],  # Combat zone 2
        'encounter_id': 'dungeon_l2_animated_patrol',
        'one_time': True,
        'completion_flag': 'dungeon_l2_encounter_2_complete',
        'repeatable': False,
        'chance': 1.0
    },
    'trap_ambush': {
        'trigger_tiles': [(3, 14), (4, 14)],  # Trap tile
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

# Environmental hazards (weak floors, etc.)
ENVIRONMENTAL_HAZARDS = {
    'weak_floor_1': {
        'hazard_tiles': [(11, 6)],
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