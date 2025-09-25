# data/maps/redstone_town_map.py
"""
Redstone Town Map Data
Professional tile-based town layout for Terror in Redstone

Map Legend:
# = Wall/Impassable
. = Street/Walkable  
T = Tavern (The Broken Blade)
B = General Store (Bernard's)
M = Mayor's Office
S = Town Square/Fountain
G = Gate (exit to world map)
H = House (decorative)
A = Alley/Back street
E = Empty lot
"""

# === TOWN MAP CONSTANTS ===
TOWN_WIDTH = 16
TOWN_HEIGHT = 12
TILE_SIZE = 64

# Player starting position (exits tavern)
TOWN_SPAWN_X = 3  # Just outside tavern door
TOWN_SPAWN_Y = 5

# === TILE TYPE DEFINITIONS ===
TILE_TYPES = {
    '#': 'wall',         # Impassable walls
    '.': 'street',       # Walkable cobblestone
    'T': 'tavern',       # The Broken Blade
    'B': 'general_store', # Bernard's shop
    'M': 'mayor_office',  # Mayor's office
    'S': 'town_square',   # Town square fountain
    'G': 'gate',         # Town gates
    'H': 'house',        # Residential buildings
    'A': 'alley',        # Back streets
    'E': 'empty_lot'     # Empty areas
}

# === WALKABLE TILES ===
WALKABLE_TILES = {
    'street', 'town_square', 'alley', 'empty_lot'
}

# === BUILDING INTERACTION TILES ===
BUILDING_TILES = {
    'tavern': {
        'name': 'The Broken Blade Tavern',
        'screen': 'broken_blade_tavern',
        'action': 'Enter tavern'
    },
    'general_store': {
        'name': "Bernard's General Store", 
        'screen': 'general_store',
        'action': 'Enter store'
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
BUILDING_ENTRANCES = {
    'tavern': {
        'building_pos': (3, 5),
        'entrance_tiles': [(4, 5)],
        'info': {
            'name': 'The Broken Blade Tavern',
            'screen': 'broken_blade_main',
            'action': 'Enter tavern'
        }
    },
    'general_store': {
        'building_pos': (12, 5),
        'entrance_tiles': [(11, 5)],
        'info': {
            'name': "Bernard's General Store",
            'screen': 'general_store',
            'action': 'Enter store'
        }
    },
    'mayor_office': {
        'building_pos': (7, 8),
        'entrance_tiles': [(7, 9), (6, 8)],
        'info': {
            'name': "Mayor's Office",
            'screen': 'mayor_office',
            'action': 'Enter office'
        }
    },
     'gate': {
        'building_pos': [(7, 0), (7,11)],
        'entrance_tiles': [(7, 1), (7,10)],
        'info': {
            'name': "Town Gate",
            'screen': 'world_map',
            'action': 'Exit to world map'
        }    
    }
}

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
    'street': (80, 60, 40),         # Brown cobblestone  
    'tavern': (139, 69, 19),        # Brown tavern
    'general_store': (160, 82, 45), # Lighter brown store
    'mayor_office': (120, 80, 60),  # Tan civic building
    'town_square': (100, 149, 237), # Blue fountain
    'gate': (160, 160, 160),        # Light gray gate
    'house': (139, 69, 19),         # Brown houses
    'alley': (60, 45, 30),          # Darker street
    'empty_lot': (0, 100, 0)        # Green grass
}

# === TOWN LAYOUT (16x12 grid) ===
TOWN_MAP = [
    "#######G########",  # Row 0 - Northern wall and Gate
    "#..............#",  # Row 1 - Street
    "#......SSS.....#",  # Row 2 - Town square (top)
    "#..H...SSS..H..#",  # Row 3 - Town square (middle)
    "#......SSS.....#",  # Row 4 - Town square (bottom)
    "#..T...E....B..#",  # Row 5 - Main street (Tavern, empty, Bernard's)
    "#..............#",  # Row 6 - Street
    "#......AAA.....#",  # Row 7 - Back alley
    "#..H...M....H..#",  # Row 8 - Mayor's office row
    "#..............#",  # Row 9 - Street
    "#..............#",  # Row A - Street
    "#######G########"   # Row B - Southern wall and Gate
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