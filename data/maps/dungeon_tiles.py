# data/maps/dungeon_tiles.py
"""
Dungeon Tileset Definitions
Maps Tiled tile indices to tile names for dungeon.png

IMPORTANT: dungeon.png is 8 columns x 7 rows = 56 tiles (32x32 each)
Tiled uses 1-based indexing (0 = empty, 1 = first tile)
Count left-to-right, top-to-bottom in your dungeon.png file
"""

# Tile index to name mapping
DUNGEON_TILE_MAP = {
    0: None,  # Empty tile
    
    # Row 1 (tiles 1-8): Structural elements
    1: 'structure_top_nw',        # Northwest corner of structure (altar/column)
    2: 'structure_top_n-',          # North edge of structure
    3: 'structure_top_ne',         # Northeast corner of structure
    4: 'wall_1',
    5: 'wall_2',
    6: 'wall_3',
    7: 'wall_4',
    8: 'structure_top_n',
    
    # Row 2 (tiles 9-16): Floor and wall variations
    9: 'structure_top_e',                   # East wall
    10: 'wall_pillar',             # Wall pillar detail
    11: 'structure_top_w',                 # Main floor tile
    12: 'wall_5',
    13: 'wall_6',
    14: 'wall_7',
    15: 'wall_8',
    16: 'structure_top_u',
    
    # Row 3 (tiles 17-24): Floor variations and structures
    17: 'structure_top_sw',
    18: 'structure_top_s',                 # Floor variation (used in walls layer too)
    19: 'structure_top_se',
    20: 'floor_1',                 # Floor with variation
    21: 'floor_2',                # Floor with variation
    22: 'floor_3',                # Floor with variation
    23: 'structure_top_[',
    24: 'structure_top_]',               # End piece of altar/table
    
    # Row 4 (tiles 25-32): Floor variations and objects
    25: 'structure_top_nub_se',
    26: 'structure_top_nub_sw',
    27: 'structure_top__ne',
    28: 'structure_top__nw',
    29: 'structure_top_nub_ne_se',                # Altar/table northwest corner
    30: 'structure_top_=',                 # Altar/table north edge
    31: 'structure_top_nw_sw',
    32: 'chest_1',                # Debris/detail object
    
    # Row 5 (tiles 33-40): Bottom walls and floor
    33: 'structure_top_nub_ne',                 # Southwest wall corner
    34: 'structure_top_nub_nw',                 # Southeast wall corner
    35: 'structure_top_-_se',
    36: 'structure_top_-sw',
    37: 'structure_top_sw_se',
    38: 'structure_top',
    39: 'stairs_down',             # Stairs going down
    40: 'stairs_up',               # Stairs going up
    
    # Row 6 (tiles 41-48): Structure elements
    41: 'structure_top_nub_nw_2',
    42: 'structure_top_nub_ne_2',
    43: 'structure_top_nub_ise',        # Middle section of column/structure
    44: 'structure_top_nub_swi',
    45: 'structure_top_ii',         # Vertical column piece (repeating)
    46: 'altar_left',                # Chest northwest corner
    47: 'altar_right',                # Chest northeast corner
    48: 'structure_top_nub_sw_2',                 # Northwest wall corner
    
    # Row 7 (tiles 49-56): Bottom elements
    49: 'structure_top_se_2',                  # North wall edge
    50: 'structure_top_i_ne',
    51: 'structure_top_nw_i',
    52: 'structure_top_nw_ne',
    53: 'floor_4',                # Floor variation
    54: 'floor_5',                # Floor variation
    55: 'floor_6',
    56: 'floor_7',                # Floor variation
}

# Define which tiles are walkable
DUNGEON_WALKABLE = [
    # All floor tiles are walkable
    'floor_1', 'floor_2', 'floor_3', 'floor_4', 'floor_5', 'floor_6',
    'floor_7',
    
    # Stairs are walkable
    'stairs_up',
    'stairs_down',
    
    # Debris/details/stairs are walkable
    'debris_1',
    
    # Note: Walls, columns, altar, and chest are NOT walkable
]
