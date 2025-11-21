# data/maps/broken_blade_map.py
"""
Broken Blade Tavern Interior Map
20x20 tile layout for navigation-based tavern exploration
"""

# === MAP CONSTANTS ===
BROKEN_BLADE_WIDTH = 20
BROKEN_BLADE_HEIGHT = 20
TILE_SIZE = 64

# Player spawn position (entering from town)
TAVERN_SPAWN_X = 10
TAVERN_SPAWN_Y = 18

# === TILE TYPE DEFINITIONS ===
TILE_TYPES = {
    '#': 'wall',           # Walls (impassable)
    '.': 'floor',          # Walkable floor
    'B': 'bar_counter',    # Bar counter (not walkable)
    'T': 'table',          # Tables (walkable)
    'C': 'chair',          # Chairs (walkable)
    'D': 'door',           # Exit door
    'S': 'stairs',         # Basement stairs
    'G': 'gamble_area',    # Dice game area
    'M': 'mayor_table',    # Mayor's table (walkable)
    '@': 'spawn_point',    # Entry spawn
}

WALKABLE_TILES = {'floor', 'table', 'chair', 'gamble_area', 'mayor_table', 'spawn_point', 'door'}

# === ASCII MAP LAYOUT ===
BROKEN_BLADE_MAP = [
    "####################",  # Row 0
    "#S.................#",  # Row 1 - Stairs upper left
    "#..................#",  # Row 2
    "#...BBBBBBBBB......#",  # Row 3 - Bar starts
    "#...B.......B......#",  # Row 4 - Bar with back area (Garrick here)
    "#...B.......B......#",  # Row 5
    "#...BBBBBBBBB......#",  # Row 6 - Bar closes
    "#..TTT......TTT...M#",  # Row 7 - First set of recruit tables + Mayor
    "#..CCC......CCC...M#",  # Row 8
    "#..................#",  # Row 9
    "#......GGG.........#",  # Row 10 - Dice game area
    "#......GGG.........#",  # Row 11
    "#..............TTT.#",  # Row 12
    "#..............CCC.#",  # Row 13
    "#..................#",  # Row 14
    "#..TTT....TTT......#",  # Row 15
    "#..CCC....CCC......#",  # Row 16 - Second set of tables
    "#..................#",  # Row 17
    "#.........@........#",  # Row 18 - Entry/exit (two door tiles)
    "##########DD########",  # Row 19
]

# === TILE HELPER FUNCTIONS ===
def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < BROKEN_BLADE_HEIGHT and 0 <= x < BROKEN_BLADE_WIDTH:
        char = BROKEN_BLADE_MAP[y][x]
        return TILE_TYPES.get(char, 'wall')
    return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_tile_color(x, y):
    """Get color for tile rendering (placeholder - will use graphics later)"""
    tile_type = get_tile_type(x, y)
    TILE_COLORS = {
        'wall': (40, 20, 10),           # Dark wood walls
        'floor': (101, 67, 33),         # Brown wooden floor
        'bar_counter': (139, 69, 19),   # Saddle brown bar
        'table': (160, 82, 45),         # Sienna tables
        'chair': (139, 90, 43),         # Wood chairs
        'door': (101, 67, 33),          # Floor color (door tile)
        'stairs': (80, 50, 30),         # Darker wood stairs
        'gamble_area': (34, 139, 34),   # Green felt
        'mayor_table': (160, 82, 45),   # Same as table
        'spawn_point': (101, 67, 33),   # Floor color
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# === NPC DEFINITIONS ===
TAVERN_NPCS = {
    'garrick': {
        'sprite_type': 'bartender',
        'position': (9, 4),  # Behind bar (center of bar back area)
        'interaction_tiles': [(8, 7), (9, 7), (10, 7), (7, 7), (11, 7)],  # Front of bar
        'display_name': 'Garrick',
        'dialogue_id': 'broken_blade_garrick',
        'conditions': None  # Always present
    },
    'meredith': {
        'sprite_type': 'server',
        'position': (5, 8),  # Near upper tables
        'interaction_tiles': [(4, 8), (6, 8), (5, 7), (5, 9)],  # Adjacent tiles
        'display_name': 'Meredith',
        'dialogue_id': 'broken_blade_meredith',
        'conditions': None  # Always present
    },
    'mayor': {
        'sprite_type': 'noble',
        'position': (18, 7),  # Upper right corner table
        'interaction_tiles': [(17, 7), (18, 8), (17, 8)],  # Adjacent tiles
        'display_name': 'Mayor Aldwin',
        'dialogue_id': 'broken_blade_mayor',
        'conditions': {'act_check': 1}  # Act I only
    },
    'gareth': {
        'sprite_type': 'warrior',
        'position': (4, 7),  # Upper left table
        'interaction_tiles': [(3, 7), (5, 7), (4, 6), (4, 8)],  # Adjacent tiles
        'display_name': 'Gareth',
        'dialogue_id': 'broken_blade_gareth',
        'conditions': {'not_recruited': 'gareth_recruited'}
    },
    'elara': {
        'sprite_type': 'mage',
        'position': (10, 7),  # Upper center table
        'interaction_tiles': [(9, 7), (11, 7), (10, 6), (10, 8)],  # Adjacent tiles
        'display_name': 'Elara',
        'dialogue_id': 'broken_blade_elara',
        'conditions': {'not_recruited': 'elara_recruited'}
    },
    'thorman': {
        'sprite_type': 'dwarf',
        'position': (4, 15),  # Lower left table
        'interaction_tiles': [(3, 15), (5, 15), (4, 14), (4, 16)],  # Adjacent tiles
        'display_name': 'Thorman',
        'dialogue_id': 'broken_blade_thorman',
        'conditions': {'not_recruited': 'thorman_recruited'}
    },
    'lyra': {
        'sprite_type': 'rogue',
        'position': (10, 15),  # Lower center table (adjusted from 9 to avoid overlap)
        'interaction_tiles': [(9, 15), (11, 15), (10, 14), (10, 16)],  # Adjacent tiles
        'display_name': 'Lyra',
        'dialogue_id': 'broken_blade_lyra',
        'conditions': {'not_recruited': 'lyra_recruited'}
    },
    'pete': {
        'sprite_type': 'commoner',
        'position': (15, 12),  # Lower right table (adjusted from 14 to fit better)
        'interaction_tiles': [(14, 12), (16, 12), (15, 11), (15, 13)],  # Adjacent tiles
        'display_name': 'Pete',
        'dialogue_id': 'broken_blade_pete',
        'conditions': None  # Always present
    }
}

def get_npc_at_position(x, y):
    """Get NPC at specific position"""
    for npc_id, npc_data in TAVERN_NPCS.items():
        if npc_data['position'] == (x, y):
            return npc_id, npc_data
    return None, None

def get_npc_interaction_at_tile(player_x, player_y):
    """Check if player can interact with NPC from current position"""
    for npc_id, npc_data in TAVERN_NPCS.items():
        if (player_x, player_y) in npc_data['interaction_tiles']:
            return npc_id, npc_data
    return None, None

def get_visible_npcs(game_state):
    """
    Return list of NPCs that should be visible based on game state
    Filters out recruited NPCs and checks act progression
    """
    visible_npcs = {}
    
    for npc_id, npc_data in TAVERN_NPCS.items():
        # Check conditions
        conditions = npc_data.get('conditions')
        
        if conditions is None:
            # No conditions - always visible (Garrick, Meredith, Pete)
            visible_npcs[npc_id] = npc_data
            continue
        
        # Check act progression for Mayor
        if 'act_check' in conditions:
            required_act = conditions['act_check']
            current_act = getattr(game_state, 'current_act', 1)
            if current_act != required_act:
                continue  # Skip this NPC
        
        # Check recruitment status
        if 'not_recruited' in conditions:
            flag_name = conditions['not_recruited']
            if getattr(game_state, flag_name, False): 
                continue  # Skip recruited NPCs
        
        # NPC passed all checks
        visible_npcs[npc_id] = npc_data
    
    return visible_npcs

# === AREA TRANSITIONS ===
AREA_TRANSITIONS = {
    'exit_door': {
        'entrance_tiles': [(9, 19), (10, 19)],  # Standing on door tiles
        'building_pos': [(9, 19), (10, 19)],
        'info': {
            'name': 'Tavern Exit',
            'interaction_type': 'navigation',
            'target_screen': 'redstone_town',
            'action': 'Leave the Broken Blade',
            'requirements': {}
        }
    },
    'basement_stairs': {
        'entrance_tiles': [(1, 1), (2, 1), (1, 2)],  # Upper left corner around stairs
        'building_pos': [(1, 1)],
        'info': {
            'name': 'Basement Stairs',
            'interaction_type': 'combat',
            'target_screen': 'combat',
            'combat_encounter': 'tavern_basement_rats',
            'action': 'Descend to Basement',
            'requirements': {
                'flags': {
                    'accepted_basement_quest': True,
                    'completed_basement_combat': False
                }
            }
        }
    },
    'basement_cleared': {
        'entrance_tiles': [(1, 1), (2, 1), (1, 2)],  # Same tiles as above
        'building_pos': [(1, 1)],
        'info': {
            'name': 'Basement',
            'interaction_type': 'navigation',
            'target_screen': 'broken_blade.basement_cleared',
            'action': 'Visit Basement',
            'requirements': {
                'flags': {
                    'completed_basement_combat': True
                }
            }
        }
    }
}

def get_transition_at_entrance(player_x, player_y, game_state):
    """
    Check if player is at area transition point
    Returns the appropriate transition based on game state flags
    """
    # Check each transition
    for transition_id, transition_data in AREA_TRANSITIONS.items():
        if (player_x, player_y) in transition_data['entrance_tiles']:
            # Check requirements
            requirements = transition_data['info'].get('requirements', {})
            
            # No requirements - always available
            if not requirements:
                return transition_data['info']
            
            # Check flag requirements
            if 'flags' in requirements:
                all_met = True
                for flag_name, required_value in requirements['flags'].items():
                    actual_value = getattr(game_state, flag_name, False)
                    if actual_value != required_value:
                        all_met = False
                        break
                
                if all_met:
                    return transition_data['info']
    
    return None

# === SPECIAL INTERACTION AREAS ===
SPECIAL_AREAS = {
    'dice_game': {
        'trigger_tiles': [(7, 10), (8, 10), (9, 10), (7, 11), (8, 11), (9, 11)],
        'info': {
            'name': 'Dice Game Table',
            'interaction_type': 'navigation',
            'target_screen': 'dice_bets',
            'action': 'Play Redstone Dice',
            'requirements': {}
        }
    }
}

def get_special_area_at_tile(player_x, player_y):
    """Check if player is at special interaction area"""
    for area_id, area_data in SPECIAL_AREAS.items():
        if (player_x, player_y) in area_data['trigger_tiles']:
            return area_data['info']
    return None