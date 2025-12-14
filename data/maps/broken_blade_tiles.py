# data/maps/broken_blade_tiles.py
"""
Broken Blade Tile Definitions
Maps Tiled tile indices to tile names

IMPORTANT: Order must match your Aseprite tileset!
Open broken_blade.png and count left-to-right, top-to-bottom
Tiled uses 1-based indexing (0 = empty, 1 = first tile)
"""

# Tile index to name mapping
BROKEN_BLADE_TILE_MAP = {
    0: None,  # Empty tile (always include)
    
    # Walls and borders (Layer 3)
    1: 'wall_nw_corner',
    2: 'wall_n',
    3: 'wall_n_2',
    4: 'wall_n_3',
    5: 'wall_n_4',
    6: 'wall_n_5',
    7: 'wall_n_6',
    8: 'wall_ne_corner',
    9: 'wall_ne_corner_2',
    11: 'wall_ne_corner_3',

    
    # More furniture/items
    12: 'chair_back',
    13: 'chair_front',

    27: 'chair_right',
    28: 'chair_left',
    30: 'item_30',
    31: 'wall_w',
    34: 'table_nw',
    35: 'table_n',
    36: 'table_ne',
    41: 'wall_e',
    46: 'wall_w_2',
    49: 'table_sw',
    50: 'table_s',
    51: 'table_se',
    56: 'wall_e_2',
    
    # Bottom walls
    61: 'wall_sw_corner',
    62: 'wall_s',
    63: 'wall_s_2',
    64: 'wall_s_3',
    65: 'wall_s_4',
    66: 'wall_s_5',
    67: 'wall_s_6',
    68: 'wall_s_7',
    69: 'wall_s_8',
    
    # Floor tiles (Layer 1)
    74: 'floor_1',
    75: 'floor_2',
    89: 'floor_3',
    90: 'floor_4',
    
    # Rugs (Layer 2)
    96: 'rug_nw',
    97: 'rug_n',
    98: 'rug_n_2',
    99: 'rug_ne',
    111: 'rug_w',
    112: 'rug_center',
    113: 'rug_center_2',
    114: 'rug_e',
    121: 'rug_nw_2',
    122: 'rug_n_3',
    123: 'rug_ne_2',
    126: 'rug_sw',
    127: 'rug_s',
    128: 'rug_s_2',
    129: 'rug_se',
    136: 'rug_w_2',
    137: 'rug_center_3',
    138: 'rug_e_2',
    141: 'rug_sw_2',
    142: 'rug_s_3',
    143: 'rug_s_4',
    144: 'rug_se_2',
    
    # Bar/furniture (Layer 3)
    100: 'bar_item_1',
    104: 'bar_item_2',
    115: 'bar_item_3',
    117: 'floor_special',
    119: 'bar_item_4',
    130: 'bar_item_5',
    134: 'bar_item_6',
    135: 'item_135',
    145: 'bar_start',
    146: 'bar_counter',
    147: 'bar_counter_2',
    148: 'bar_counter_3',
    149: 'bar_end',
    155: 'item_155',
    156: 'item_156',
    170: 'item_170',
    171: 'item_171',
    
    # Floor variant (Layer 1)
    159: 'floor_dark',
    
    # Details (Layer 4)
    160: 'detail_1',
    161: 'detail_2',
    162: 'detail_3',
    163: 'detail_4',
    164: 'detail_5',
    174: 'detail_6',
    176: 'detail_7',
    178: 'detail_8',
    179: 'detail_9',
}

# Define which tiles are walkable
BROKEN_BLADE_WALKABLE = [
    # Floor tiles
    'floor_1',
    'floor_2',
    'floor_3',
    'floor_4',
    'floor_dark',
    'floor_special',
    
    # Rugs (walkable)
    'rug_nw', 'rug_n', 'rug_n_2', 'rug_ne',
    'rug_w', 'rug_center', 'rug_center_2', 'rug_e',
    'rug_nw_2', 'rug_n_3', 'rug_ne_2',
    'rug_sw', 'rug_s', 'rug_s_2', 'rug_se',
    'rug_w_2', 'rug_center_3', 'rug_e_2',
    'rug_sw_2', 'rug_s_3', 'rug_s_4', 'rug_se_2',
    
    # Chairs (if walkable)
    'chair_front','chair_back','chair_right', 'chair_left'
    
    # Add other walkable tiles as needed
]
