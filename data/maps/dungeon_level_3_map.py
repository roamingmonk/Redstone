"""
Dungeon Level 3 - The Convergence
20x20 tile grid - Where front door and mine tunnel routes meet
ZONE 3: Transition from ancient ruins to active cult territory
Enemies: Mixed undead + first cultists appearing
Environmental: Both ancient decay and fresh cult alterations
"""

from utils.constants import (
    FIRE_BRICK_RED, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
    CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
    BUTTON_SIZES, SCREEN_WIDTH
)

DUNGEON_L3_WIDTH = 20
DUNGEON_L3_HEIGHT = 20

# Starting position (entering from Level 2 - at top stairs)
DUNGEON_L3_SPAWN_X = 6
DUNGEON_L3_SPAWN_Y = 1

# Spawn points for different entry methods
DUNGEON_L3_SPAWN_POINTS = {
    'from_level_2': (6, 1),         # Top of map, at stairs up 'U'
    'from_level_4': (11, 18),       # Bottom of map, at stairs down 'S'
    'from_mine_tunnel': (1, 10),    # Left side entrance 'M' (future mine route)
    'default': (6, 1)
}

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',           # Stone walls (impassable)
    '.': 'floor',          # Stone floor (walkable)
    'P': 'pillar',         # Stone pillar (not walkable, cover)
    'D': 'door',           # Wooden door (walkable)
    'S': 'stairs_down',    # Stairs to Level 4
    'U': 'stairs_up',      # Stairs back to Level 2
    'M': 'mine_entrance',  # Mine tunnel entrance (from Red Hollow)
    '~': 'combat_zone',    # Combat encounter trigger
    'C': 'chest',          # Loot chest (searchable)
    'A': 'altar',          # Cult altar (searchable, ominous)
    '+': 'rubble',         # Debris (walkable)
    'B': 'brazier',        # Lit brazier (cult presence, searchable)
    'R': 'ritual_circle',  # Blood ritual circle (searchable, lore)
}

WALKABLE_TILES = {'floor', 'door', 'stairs_down', 'stairs_up', 'mine_entrance',
                  'combat_zone', 'chest', 'altar', 'rubble', 'brazier', 'ritual_circle'}

# ASCII map layout - 20x20 grid
# Legend:
#  U = Stairs up to Level 2 (front door route)
#  M = Mine tunnel entrance (mine route - future)
#  ~ = Combat encounter
#  C = Chest
#  A = Cult altar (disturbing)
#  B = Brazier (cult presence)
#  R = Ritual circle (lore)
#  S = Stairs down to Level 4
#  P = Pillar
#  # = Wall
#  . = Floor

DUNGEON_L3_MAP = [
    "####################",  # Row 0
    "#..................#",  # Row 1
    "#.....U............#",  # Row 2 - Stairs up (front door spawn)
    "#..................#",  # Row 3
    "#..PP..........PP..#",  # Row 4 - Pillars
    "#..................#",  # Row 5
    "#....~.............#",  # Row 6 - ENCOUNTER 1: Mixed undead + cultist
    "#..................#",  # Row 7
    "#......C...........#",  # Row 8 - Chest
    "#..................#",  # Row 9
    "#M.................#",  # Row 10 - Mine entrance (LEFT SIDE, mine route)
    "#..................#",  # Row 11
    "#..........B.......#",  # Row 12 - Brazier (cult sign)
    "#..................#",  # Row 13
    "#.....~............#",  # Row 14 - ENCOUNTER 2: Cult guards
    "#..................#",  # Row 15
    "#......R...........#",  # Row 16 - Ritual circle (lore)
    "#..A...............#",  # Row 17 - Cult altar
    "#.........S........#",  # Row 18 - Stairs down to Level 4
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < DUNGEON_L3_HEIGHT and 0 <= x < DUNGEON_L3_WIDTH:
        char = DUNGEON_L3_MAP[y][x]
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
        'wall': (30, 30, 35),           # Very dark stone walls
        'floor': (70, 65, 60),          # Dark gray stone floor
        'pillar': (50, 45, 40),         # Dark stone pillar
        'door': (80, 60, 40),           # Wooden door
        'stairs_down': (90, 80, 70),    # Lighter stone (highlight)
        'stairs_up': (90, 80, 70),      # Lighter stone (highlight)
        'mine_entrance': (60, 50, 40),  # Dark tunnel opening
        'combat_zone': (75, 65, 60),    # Slightly different floor
        'chest': (130, 100, 30),        # Gold/brown chest (highlight)
        'altar': (80, 40, 40),          # Dark red altar (ominous)
        'rubble': (60, 55, 50),         # Darker debris
        'brazier': (150, 80, 30),       # Orange fire (highlight)
        'ritual_circle': (100, 30, 30), # Dark red circle (blood)
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions
AREA_TRANSITIONS = {
    'stairs_to_level_4': {
        'entrance_tiles': [(10, 18), (9, 18), (11, 18)],  # Around stairs
        'building_pos': [(10, 18)],
        'info': {
            'name': 'Descending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_4_nav',
            'action': 'Descend to Level 4 - Cult Sanctum',
            'requirements': {}
        }
    },
    'stairs_to_level_2': {
        'entrance_tiles': [(6, 2), (5, 2), (7, 2)],  # Stairs up
        'building_pos': [(6, 2)],
        'info': {
            'name': 'Ascending Stairs',
            'interaction_type': 'navigation',
            'target_screen': 'dungeon_level_2_nav',
            'action': 'Return to Level 2',
            'requirements': {}
        }
    },
    'convergence_chest': {
        'search_tiles': [(7, 8), (8, 8), (6, 8)],  # Around chest
        'object_pos': [(7, 8)],
        'info': {
            'name': 'Heavy Iron Chest',
            'interaction_type': 'dialogue',  # CHANGED from 'loot'
            'description': 'A reinforced chest marked with both ancient and cult symbols.',
            'examine_dialogue': 'dungeon_level_3_chest',  # ADDED
            'loot_table': None,  # CHANGED from the loot table name
            'flag_set': 'dungeon_level_3_chest_looted',
            'requirements': {},
            'one_time': True
        }
    },
    'mine_tunnel_entrance': {
        'entrance_tiles': [(1, 10), (2, 10)],  # Mine tunnel
        'building_pos': [(1, 10)],
        'info': {
            'name': 'Mine Tunnel Passage',
            'interaction_type': 'navigation',
            'target_screen': 'red_hollow_mine_level_3_nav',
            'action': 'Enter Mine Tunnel (Shortcut Route - NOT YET IMPLEMENTED)',
            'requirements': {'flag': 'red_hollow_mine_secret_entrance_found'}
        }
    }
}

def get_transition_at_entrance(player_x, player_y):
    """Check if player is at area transition point"""
    for transition_id, transition_data in AREA_TRANSITIONS.items():
        # Safety check for malformed data
        if 'entrance_tiles' not in transition_data:
            continue
        if (player_x, player_y) in transition_data['entrance_tiles']:
            return transition_data.get('info')
    return None

# Searchable objects
SEARCHABLE_OBJECTS = {
    'convergence_chest': {
        'search_tiles': [(7, 7), (6, 8), (8, 8)],  # Around chest
        'object_pos': [(7, 8)],
        'info': {
            'name': 'Heavy Iron Chest',
            'interaction_type': 'searchable',
            'description': 'A reinforced chest marked with both ancient and cult symbols.',
            'examine_dialogue': 'dungeon_level_3_chest',
            'loot_table': 'dungeon_level_3_chest_loot',
            'flag_set': 'dungeon_level_3_chest_looted',
            'requirements': {},
            'one_time': True
        }
    },
    'cult_altar': {
        'search_tiles': [(2, 17), (5, 17), (3, 16), (4, 16)],  # Around altar
        'object_pos': [(3, 17), (4, 17)],
        'info': {
            'name': 'Defiled Cult Altar',
            'interaction_type': 'dialogue',
            'description': 'A stone altar covered in dried blood and strange symbols.',
            'examine_dialogue': 'dungeon_level_3_altar',
            'loot_table': None,
            'flag_set': 'dungeon_level_3_altar_examined',
            'requirements': {},
            'one_time': True
        }
    },
    'ritual_circle': {
        'search_tiles': [(2, 14), (2, 15), (5, 14), (5, 15), (3, 13), (4, 13)],  # Around circle
        'object_pos': [(3, 14), (4, 14), (3, 15), (4, 15)],
        'info': {
            'name': 'Blood Ritual Circle',
            'interaction_type': 'dialogue',
            'description': 'A freshly drawn ritual circle stained with blood.',
            'examine_dialogue': 'dungeon_level_3_ritual',
            'loot_table': None,
            'flag_set': 'dungeon_level_3_ritual_examined',
            'requirements': {},
            'one_time': True
        }
    },
    'brazier': {
        'search_tiles': [(11, 13), (12, 12), (10, 12)],  # Around brazier
        'object_pos': [(11, 12)],
        'info': {
            'name': 'Burning Brazier',
            'interaction_type': 'dialogue',
            'description': 'A large iron brazier burning with unnatural green flames.',
            'examine_dialogue': 'dungeon_level_3_brazier',
            'loot_table': None,
            'flag_set': 'dungeon_level_3_brazier_examined',
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
    'undead_cultist_mix': {
        'trigger_tiles': [(5, 6), (6, 6), (7, 6)],  # Combat zone 1
        'encounter_id': 'dungeon_l3_mixed_forces',
        'one_time': True,
        'completion_flag': 'dungeon_l3_encounter_1_complete',
        'repeatable': False,
        'chance': 1.0
    },
    'cult_guard_patrol': {
        'trigger_tiles': [(6, 14), (7, 14), (8, 14)],  # Combat zone 2
        'encounter_id': 'dungeon_l3_cult_guards',
        'one_time': True,
        'completion_flag': 'dungeon_l3_encounter_2_complete',
        'repeatable': False,
        'chance': 1.0
    }
}

def get_combat_trigger(x, y):
    """Check if position triggers combat encounter"""
    for encounter_id, encounter_data in COMBAT_ENCOUNTERS.items():
        if (x, y) in encounter_data['trigger_tiles']:
            return encounter_data
    return None