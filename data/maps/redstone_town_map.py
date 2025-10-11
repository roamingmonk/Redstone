# data/maps/redstone_town_map.py
"""
Redstone Town Map Data
Professional tile-based town layout for Terror in Redstone

Map Legend:
# = Wall/Impassable
. = Street/Walkable  
T = Tavern (The Broken Blade)
B = General Store (Bernard's)
P = Potion Shop
M = Mayor's Office
S = Town Square/Fountain
C = Church
G = Gate (exit to world map)
H = House (decorative)
A = Alley/Back street
E = Empty lot
R = Main road (to/from town)
g = Ground/grass (outside walls)
"""

# === TOWN MAP CONSTANTS ===
TOWN_WIDTH = 18
TOWN_HEIGHT = 14
TILE_SIZE = 64

# Player starting position (exits tavern)
TOWN_SPAWN_X = 7  # Just outside tavern door
TOWN_SPAWN_Y = 7

# === TILE TYPE DEFINITIONS ===
TILE_TYPES = {
    '#': 'wall',          # Impassable walls
    '=': 'wall_north',    # North wall
    '+': 'wall_south',    # South wall
    '[': 'wall_west',     # West wall
    ']': 'wall_east',     # East wall
    ';': 'wall_corner_nw',# Northwest corner
    ':': 'wall_corner_sw',# Southwest corner
    '/': 'wall_corner_ne',# Northeast corner
    ',': 'wall_corner_se',# Southeast corner
    '.': 'street',        # Walkable cobblestone
    'T': 'tavern',        # The Broken Blade
    'B': 'general_store', # Bernard's shop
    'P': 'potion_shop',   # Potion shop
    'M': 'mayor_office',  # Mayor's office
    'C': 'church',        # Town church
    'S': 'town_square',   # Town square fountain
    'G': 'gate_north',    # Town gates north
    't': 'gate_south',    # Town gates south
    'H': 'house',         # Residential buildings
    'A': 'alley',         # Back streets
    'E': 'empty_lot',     # Empty areas
    'R': 'main_road',     # Main road to/from town
    'g': 'ground_grass',   # Ground/grass outside walls (lowercase g)
}

# === WALKABLE TILES ===
WALKABLE_TILES = {
    'street', 'town_square', 'alley', 'empty_lot', 'main_road', 'ground_grass'
}

# === BUILDING INTERACTION TILES ===
BUILDING_TILES = {
    'tavern': {
        'name': 'The Broken Blade Tavern',
        'screen': 'broken_blade',
        'action': 'Enter tavern'
    },
    'general_store': {
        'name': "Bernard's General Store", 
        'screen': 'general_store',
        'action': 'Enter store'
    },
    'potion_shop': {
        'name': "Potion Shop",
        'screen': 'potion_shop',
        'action': 'Enter potion shop'
    },
    'church': {
        'name': "Redstone Church",
        'screen': 'redstone_church',
        'action': 'Enter church'
    },
    'mayor_office': {
        'name': "Mayor's Office",
        'screen': 'mayor_office', 
        'action': 'Enter office'
    },
    'gate': {
        'name': 'Town Gate',
        'screen': 'world_map',
        'action': 'Exit to world map'
    }
}

# === BUILDING/GATE ENTRANCE DEFINITIONS ===
# Column , Row
BUILDING_ENTRANCES = {
    'tavern': {
        'building_pos': (6, 7),
        'entrance_tiles': [(7, 7), (6, 8)],  # In front and below tavern
        'info': {
            'name': 'The Broken Blade Tavern',
            'interaction_type': 'screen_transition',
            'screen': 'broken_blade',
            'action': 'Enter tavern'
        }
    },
    'general_store': {
        'building_pos': (9, 5),
        'entrance_tiles': [(8, 5), (9, 6)],  # In front and below store
        'info': {
            'name': "Bernard's General Store",
            'interaction_type': 'npc_dialogue',
            'npc_id': 'bernard',
            'action': 'Talk to Bernard'
        }
    },
    'potion_shop': {
        'building_pos': (4, 9),
        'entrance_tiles': [(5, 9)],  #In front 
        'info': {
            'name': "Potion Shop",
            'interaction_type': 'screen_transition',  # Or npc_dialogue
            'screen': 'potion_shop',
            'action': 'Enter potion shop'
        }
    },
    'church': {
        'building_pos': [(11, 7), (10, 7), (11, 8), (10, 8)],  # 2x2 church
        'entrance_tiles': [(9, 8), (9, 7)],  # front of church
        'info': {
            'name': "Redstone Church",
            'interaction_type': 'screen_transition',
            'screen': 'redstone_church',
            'action': 'Enter church'
        }
    },
    'mayor_office': {
        'building_pos': (7, 9),
        'entrance_tiles': [(7, 8), (8, 9)],  # In front and below office
        'info': {
            'name': "Mayor's Office",
            'interaction_type': 'npc_dialogue',
            'npc_id': 'mayor',
            'action': 'Talk to Mayor'
        }
    },
    'north_gate': {
        'building_pos': (8, 1),
        'entrance_tiles': [(8, 2)],  # Tile just south of north gate
        'info': {
            'name': "North Town Gate",
            'interaction_type': 'screen_transition',
            'screen': 'world_map',
            'action': 'Exit to world map (North)'
        }    
    },
    'south_gate': {
        'building_pos': (7, 12),
        'entrance_tiles': [(7, 11)],  # Tile just north of south gate
        'info': {
            'name': "South Town Gate",
            'interaction_type': 'screen_transition',
            'screen': 'world_map',
            'action': 'Exit to world map (South)'
        }    
    }
}

# === NPC SPAWN DEFINITIONS ===
TOWN_NPCS = {
    'henrik': {
        'sprite_type': 'henrik',
        'default_position': (7, 6),  # His vegetable cart location
        'interaction_tiles': [(7, 7), (8,6)],  # Can interact from these tiles
        'display_name': 'Old Henrik',
        'dialogue_id': 'henrik',
        'conditions': None  # Always present
    },
    
    'guard_north': {
        'sprite_type': 'guard',
        'default_position': (8, 2),  # Near north gate
        'interaction_tiles': [(7, 2), (8, 1), (9, 2), (8, 3)],
        'display_name': 'Town Guard',
        'dialogue_id': 'guard_generic',
        'conditions': None,
        'general_response': "The guard nods but says nothing. They're on duty."
    },
    
    'guard_south': {
        'sprite_type': 'guard',
        'default_position': (7, 11),  # Near south gate
        'interaction_tiles': [(6, 11), (7, 10), (8, 11), (7, 12)],
        'display_name': 'Town Guard',
        'dialogue_id': 'guard_generic',
        'conditions': None,
        'general_response': "The guard stands watch, scanning the street for trouble."
    },
    
    'market_merchant': {
        'sprite_type': 'merchant',
        'default_position': (8, 7),  # Town square
        'interaction_tiles': [(8, 6), (9, 7), (8, 8), (7, 7)],
        'display_name': 'Traveling Merchant',
        'dialogue_id': 'merchant_wandering',
        'conditions': {
            'day_of_week': ['tuesday', 'friday']  # Market days only
        },
        'general_response': "The merchant is busy arranging wares and waves you off."
    },
    
    'noble_lady': {
        'sprite_type': 'noble',
        'default_position': (10, 6),  # Near church
        'interaction_tiles': [(9, 6), (10, 5), (11, 6), (10, 7)],
        'display_name': 'Lady Ashworth',
        'dialogue_id': 'noble_lady',
        'conditions': {
            'time_of_day': 'day',
            'day_of_week': ['monday','tuesday', 'saturday', 'sunday'],  # Market days only
            'not_quest_complete': 'church_mystery_solved'
        },
        'general_response': "Lady Ashworth glances at you briefly, then continues her walk."
    },
    
    'beggar': {
        'sprite_type': 'citizen',
        'default_position': (4, 8),  # Near alley
        'interaction_tiles': [(4, 7), (3, 8), (5, 8), (4, 9)],  
        'display_name': 'Poor Beggar',
        'dialogue_id': 'beggar',
        'conditions': None,
        'general_response':"The mumbles something incoherent about the end of the world."
    }
}

def get_location_npcs():
    """Return NPC definitions for this location"""
    return TOWN_NPCS

def get_building_at_entrance(player_x, player_y):
    """Check if player is standing at a valid building entrance"""
    for building_id, building_data in BUILDING_ENTRANCES.items():
        entrance_tiles = building_data['entrance_tiles']
        if (player_x, player_y) in entrance_tiles:
            return building_data['info']
    return None

# === TILE COLORS (Classic VGA Palette) ===
TILE_COLORS = {
    'wall': (100, 100, 100),        # Gray stone walls
    'wall_north': (100, 100, 100),        
    'wall_south': (100, 100, 100),        
    'wall_east': (100, 100, 100),        
    'wall_west': (100, 100, 100),        
    'street': (80, 60, 40),         # Brown cobblestone  
    'tavern': (160, 82, 45),        # Lighter brown tavern
    'general_store': (160, 82, 45), # Lighter brown store
    'potion_shop': (138, 43, 226),  # Purple potion shop
    'church': (245, 245, 220),      # Beige/cream church
    'mayor_office': (120, 80, 60),  # Tan civic building
    'town_square': (100, 149, 237), # Blue fountain
    'gate_north': (160, 160, 160),        # Light gray gate
    'gate_south': (160, 160, 160),        # Light gray gate
    'house': (139, 69, 19),         # Brown houses
    'alley': (60, 45, 30),          # Darker street
    'empty_lot': (0, 100, 0),       # Green grass
    'main_road': (101, 67, 33),     # Dark brown road
    'ground_grass': (34, 139, 34),   # Forest green grass
}

# === TOWN LAYOUT (18x14 grid) ===
# Corner battlements create fortified town structure
# g = Ground/grass outside walls between corner towers (lowercase)
# R = Main roads leading to north/south gates
# NOTE: Rows 0 and 13 are decorative borders showing ground outside town walls
TOWN_MAP = [
    "####ggggRggggg####",  # Row 0 - Top border: corner towers, grass, north road (R at col 8)
    "#;======G=======/#",  # Row 1 - Top wall with north gate (G at col 8)
    "#[..............]#",  # Row 2 - Street (corner battlements)
    "#[.HH.HH.HHHAHH.]#",  # Row 3 - Houses with alley (corner battlements)
    "g[.HH.HH.HHHAHH.]g",  # Row 4 - Houses with alley + side grass
    "g[.HH.HH.BHHAHH.]g", # Row 5 - Bernard's store (B at col 9) + side grass
    "g[.HH.HSSS......]g",  # Row 6 - Town square (S) begins + side grass
    "g[.HH.TSSSCCH.H.]g",  # Row 7 - Tavern (T at col 5), square, church (C at cols 9-10) + side grass
    "g[.....SSSCCH.H.]g",  # Row 8 - Square/church continue + side grass
    "g[.HP.HM.HHHH.H.]g",  # Row 9 - Potion shop (P at col 3), Mayor (M at col 6) + side grass
    "#[.HH.HH.HHHH.E.]#",  # Row 10 - Houses, empty lot (E at col 14) (corner battlements)
    "#[..............]#",  # Row 11 - Street (corner battlements)
    "#:+++++t++++++++,#",  # Row 12 - Bottom wall with south gate (G at col 7)
    "####gggRgggggg####"   # Row 13 - Bottom border: corner towers, grass, south road (R at col 7)
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < TOWN_HEIGHT and 0 <= x < TOWN_WIDTH:
        char = TOWN_MAP[y][x]
        return TILE_TYPES.get(char, 'wall')
    return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_building_info(x, y):
    """Get building information if tile is a building"""
    tile_type = get_tile_type(x, y)
    return BUILDING_TILES.get(tile_type, None)

def get_tile_color(x, y):
    """Get color for tile at coordinates"""
    tile_type = get_tile_type(x, y)
    return TILE_COLORS.get(tile_type, (128, 128, 128))  # Default gray