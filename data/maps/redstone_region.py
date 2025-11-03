"""
Redstone Region Map - Terror in Redstone
16x16 tile grid showing terrain and key locations around Redstone town
This is the local exploration area for Act II investigations

Part of the larger Crimson Reach (28x20 overworld map)
Tiles are 32x32 pixels, total map size 512x512, centered on screen
"""

import pygame
from utils.constants import (
                           #Colors
                           FIRE_BRICK_RED, MOUNTAIN_GRAY, WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
                           CYAN, WARNING_RED, TITLE_GREEN, YELLOW, PURPLE, PURPLE_BLUE, STEEL_BLUE,
                           #Buttons
                           BUTTON_SIZES, SCREEN_WIDTH
)


# Terrain type constants
TERRAIN_HILLS = 'H'
TERRAIN_FOREST = 'F'
TERRAIN_MOUNTAINS = 'M'
TERRAIN_PLAINS = '-'
TERRAIN_RIVER = 'R'
TERRAIN_SWAMP = ':'
TERRAIN_TOWN = 'T'

# Terrain colors for rendering (RGB tuples)
TERRAIN_COLORS = {
    'H': (139, 115, 85),    # Hills - brown/tan
    'F': (34, 139, 34),     # Forest - dark green
    'M': MOUNTAIN_GRAY,     # Mountains - dark gray
    '-': (210, 180, 140),   # Plains - tan/beige
    'R': STEEL_BLUE,        # River - steel blue
    ':': (85, 107, 47),     # Swamp - dark olive green
    'T': (139, 69, 19)      # Town - saddle brown
}

# 16x16 terrain grid - Redstone Region
# Layout: Redstone in center-north, swamp in south, mountains in east, hills throughout
REDSTONE_REGION_TERRAIN = [
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'F', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'F', 'H', 'H', 'H', 'H', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'F', 'F', 'F', 'T', 'F', 'H', 'H', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'F', 'F', 'F', 'F', 'F', 'H', 'H', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'F', 'F', 'F', 'F', 'F', 'H', 'H', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'F', 'F', 'F', 'H', 'H', 'H', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'F', 'F', 'H', ':', ':', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'F', 'F', ':', ':', 'R', 'R', 'M', 'M', 'R', 'R'],
    ['H', '-', '-', 'H', 'H', 'H', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', '-', '-', 'H', 'H', 'F', 'F', ':', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'H', ':', 'F', ':', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'H', ':', 'F', ':', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'H', 'F', 'F', ':', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'F', 'F', 'F', ':', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'F', 'F', 'F', ':', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
]

# Location definitions with grid coordinates (x, y)
REDSTONE_REGION_LOCATIONS = {
    'redstone_town': {
        'name': 'Redstone',
        'grid_pos': (8, 3),  # Center-north of map
        'discovery_flag': None,  # Always visible (home base)
        'icon': '🏘️',
        'icon_color': (255, 215, 0),  # Gold
        'target': 'redstone_town',
        'description': 'The mining town at the heart of the region.'
    },
    'hill_ruins': {
        'name': 'Hill Ruins',
        'grid_pos': (12, 1),  # East, in the mountains
        'discovery_flag': 'learned_about_ruins',
        'icon': '🏔️',
        'icon_color': GRAY,  # Gray
        'target': 'hill_ruins_entrance_nav',
        'description': 'Ancient watchtower overlooking the valley.'
    },
    'swamp_church': {
        'name': 'Swamp Church',
        'grid_pos': (7, 12),  # Southwest, in the swamp
        'discovery_flag': 'learned_about_swamp_church',
        'icon': '⛪',
        'icon_color': PURPLE,
        'target': 'swamp_church_exterior_nav',
        'description': 'Fog-shrouded church deep in the marshlands.'
    },
    'refugee_camp': {
        'name': 'Refugee Camp',
        'grid_pos': (2, 10),  # West, in the plains
        'discovery_flag': 'learned_about_refugees',
        'icon': '⛺',
        'icon_color': (210, 105, 30),  # Chocolate brown
        'target': 'refugee_camp_main',
        'description': 'Makeshift settlement of displaced miners.'
    },
    'red_hollow_mine': {
        'name': 'Red Hollow Mine',
        'grid_pos': (11, 6),  # East, in the mountains
        'discovery_flag': 'discovered_old_mine_shaft',
        'icon': '⛏️',
        'icon_color': FIRE_BRICK_RED,  # Firebrick red
        'target': 'red_hollow_mine_entrance',
        'description': 'Abandoned mine shaft, sealed by fearful workers.'
    }
}

# Map rendering constants
REDSTONE_REGION_TILE_SIZE = 32
REDSTONE_REGION_GRID_WIDTH = 16
REDSTONE_REGION_GRID_HEIGHT = 16
REDSTONE_REGION_MAP_WIDTH = REDSTONE_REGION_GRID_WIDTH * REDSTONE_REGION_TILE_SIZE  # 512
REDSTONE_REGION_MAP_HEIGHT = REDSTONE_REGION_GRID_HEIGHT * REDSTONE_REGION_TILE_SIZE  # 512

# Center map on 1024x768 screen, leaving room for UI
REDSTONE_REGION_MAP_X = (1024 - REDSTONE_REGION_MAP_WIDTH) // 2  # 256
REDSTONE_REGION_MAP_Y = 120  # Leave room for title and party panel at top

def get_terrain_at(x, y):
    """Get terrain type at grid coordinates"""
    if 0 <= y < REDSTONE_REGION_GRID_HEIGHT and 0 <= x < REDSTONE_REGION_GRID_WIDTH:
        return REDSTONE_REGION_TERRAIN[y][x]
    return None

def get_location_at(x, y):
    """Check if there's a location at grid coordinates"""
    for location_id, location_data in REDSTONE_REGION_LOCATIONS.items():
        if location_data['grid_pos'] == (x, y):
            return location_id, location_data
    return None, None

def is_location_discovered(location_data, game_state):
    """Check if location is discovered (always show if no discovery_flag)"""
    discovery_flag = location_data.get('discovery_flag')
    if discovery_flag is None:
        return True  # Always visible (like Redstone town)
    return getattr(game_state, discovery_flag, False)

def is_location_completed(location_id, game_state):
    """Check if location has been completed"""
    # Convert location_id to completion flag name
    # e.g., "swamp_church" → "swamp_church_complete"
    completion_flag = f"{location_id}_complete"
    return getattr(game_state, completion_flag, False)