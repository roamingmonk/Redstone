# data/maps/refugee_camp_tiles.py
"""
Refugee Camp Tile Definitions
Maps Tiled tile indices to tile names

IMPORTANT: Order must match your Aseprite tileset!
Open refugee_camp.png and count left-to-right, top-to-bottom
Tiled uses 1-based indexing (0 = empty, 1 = first tile)
"""

# Tile index to name mapping
REFUGEE_CAMP_TILE_MAP = {
    0: None,  # Empty tile (no tile placed)
    1: 'trees',
    2: 'dirt_n_grass',
    3: 'dirt_w_grass',
    4: 'trees_front',
    5: 'tent_grass_s',
    6: 'tent_dirt_s',
    7: 'dirt_s_grass',
    8: 'dirt_e_grass',
    9: 'hedge',
    10: 'hedge_e_grass',
    11: 'grass',
    12: 'path_grass_vertical',
    13: 'path_dirt_vertical',
    14: 'dirt',
    15: 'dirt_n_e_w_grass',
    16: 'hedge_s_grass',
    17: 'path_intersection_grass',
    18: 'path_intersection_dirt',
    19: 'dirt_n_e_grass',
    20: 'dirt_e_w_grass',
    21: 'hedge_n_grass',
    22: 'path_grass_corner_n_e',
    23: 'path_dirt_corner_n_e',
    24: 'grass_e_dirt',
    25: 'campfire',
    26: 'dirt_path_horizontal',
    27: 'grass_path_horizontal',
    28: 'path_dirt_vertical2',
    29: 'dirt_e_s_grass',
    30: 'dirt_n_w_grass',
    31: 'dirt_s_w_grass',
    32: 'path_dirt_vertical_w',
    33: 'dirt_n_s_w_grass',
    34: 'path_dirt_horizontal_n',
    35: 'dirt_n_e_s_grass',
    36: 'dirt_e_s_w_grass',
    37: 'path_dirt_corner_s_w',
    38: 'path_dirt_corner_n_w',
    39: 'tent_dirt_n',
    40: 'tent_dirt_e'
    
}

# Define which tiles are walkable
REFUGEE_CAMP_WALKABLE = [
    'dirt_n_grass',
    'dirt_w_grass',
    'dirt_s_grass',
    'dirt_e_grass',
    'grass',
    'path_grass_vertical',
    'path_dirt_vertical',
    'dirt',
    'dirt_n_e_w_grass',
    'path_intersection_grass',
    'path_intersection_dirt',
    'dirt_n_e_grass',
    'dirt_e_w_grass',
    'path_grass_corner_n_e',
    'path_dirt_corner_n_e',
    'grass',
    'dirt_path_horizontal',
    'grass_path_horizontal',
    'path_dirt_vertical2',
    'dirt_e_s_grass',
    'dirt_e_w_grass',
    'dirt_n_w_grass',
    'dirt_s_w_grass',
    'path_dirt_vertical_w',
    'dirt_n_s_w_grass',
    'dirt_n_e_s_grass',
    'dirt_e_s_w_grass',
    'path_dirt_corner_s_w',
    'path_dirt_corner_n_w',
    'path_dirt_horizontal_n'
        
]

