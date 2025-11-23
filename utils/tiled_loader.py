# utils/tiled_loader.py
"""
Tiled Map Loader - Professional tilemap loading from Tiled Map Editor
Auto-detects .tmj (new) and .json (old) file extensions
100% backwards compatible with existing ASCII map system

Tiled Map Editor: https://www.mapeditor.org/
"""

import json
import os


def find_tiled_map(map_name, base_path):
    """
    Find a Tiled map file with either .tmj or .json extension
    
    Args:
        map_name: Map name without extension (e.g., 'refugee_camp_map')
        base_path: Directory to search in
    
    Returns:
        Full path to the map file
        
    Raises:
        FileNotFoundError: If neither .tmj nor .json found
    """
    
    # Try .tmj first (newer Tiled versions 1.8+)
    tmj_path = os.path.join(base_path, f'{map_name}.tmj')
    if os.path.exists(tmj_path):
        print(f"📍 Found Tiled map: {map_name}.tmj")
        return tmj_path
    
    # Try .json (older Tiled versions)
    json_path = os.path.join(base_path, f'{map_name}.json')
    if os.path.exists(json_path):
        print(f"📍 Found Tiled map: {map_name}.json")
        return json_path
    
    # Neither found
    raise FileNotFoundError(
        f"❌ Tiled map not found: {map_name}.tmj or {map_name}.json in {base_path}"
    )


def load_tiled_map(map_name, tileset_name, base_path):
    """
    Load a map created in Tiled Map Editor
    Auto-detects .tmj or .json extension
    
    Args:
        map_name: Map name without extension (e.g., 'refugee_camp_map')
        tileset_name: Name of tileset (e.g., 'refugee_camp')
        base_path: Directory containing the map file
    
    Returns:
        dict with:
        - 'width': Map width in tiles
        - 'height': Map height in tiles
        - 'tile_width': Tile width in pixels
        - 'tile_height': Tile height in pixels
        - 'tile_grid': 2D array of tile indices (integers)
        - 'layers': Dict of all layers by name
        - 'tilesets': Tileset information
    """
    
    # Find the map file (auto-detect .tmj or .json)
    tiled_json_path = find_tiled_map(map_name, base_path)
    
    # Load Tiled JSON
    print(f"📦 Loading Tiled map: {map_name}")
    with open(tiled_json_path, 'r') as f:
        tiled_data = json.load(f)
    
    # Extract map properties (handle different Tiled export formats)
    map_width = tiled_data.get('width', 20)
    map_height = tiled_data.get('height', 20)
    tile_width = tiled_data.get('tilewidth', 32)
    tile_height = tiled_data.get('tileheight', 32)
    
    # Alternative format: some Tiled versions nest these differently
    if tile_width == 32 and 'tileSize' in tiled_data:
        tile_width = tiled_data['tileSize'].get('width', 32)
        tile_height = tiled_data['tileSize'].get('height', 32)
    
    print(f"   📐 Map size: {map_width}×{map_height} tiles ({tile_width}×{tile_height} pixels)")
    
    # Extract layers
    layers = {}
    tile_grid = None  # Will be the first/main layer
    
    for layer in tiled_data.get('layers', []):
        if layer.get('type') == 'tilelayer':
            layer_name = layer.get('name', 'Layer')
            layer_data = layer.get('data', [])  # Flat array of tile indices
            
            # Check if data exists
            if not layer_data:
                print(f"   ⚠️ Warning: Layer '{layer_name}' has no tile data, skipping")
                continue
            
            # Convert flat array to 2D grid
            grid = []
            for y in range(map_height):
                row = []
                for x in range(map_width):
                    idx = y * map_width + x
                    if idx < len(layer_data):
                        tile_index = layer_data[idx]
                    else:
                        tile_index = 0  # Empty tile
                    row.append(tile_index)
                grid.append(row)
            
            layers[layer_name] = grid
            
            # Use first layer as main tile_grid
            if tile_grid is None:
                tile_grid = grid
                print(f"   🗺️ Main layer: {layer_name}")
    
    # Check if we got any tile data
    if tile_grid is None:
        print(f"   ⚠️ Warning: No valid tile layers found, creating empty grid")
        tile_grid = [[0 for x in range(map_width)] for y in range(map_height)]
    
    # Extract tileset info
    tilesets = []
    for tileset in tiled_data.get('tilesets', []):
        tilesets.append({
            'firstgid': tileset.get('firstgid', 1),
            'name': tileset.get('name', tileset_name),
            'tilewidth': tileset.get('tilewidth', tile_width),
            'tileheight': tileset.get('tileheight', tile_height),
            'tilecount': tileset.get('tilecount', 0),
            'columns': tileset.get('columns', 0)
        })
    
    return {
        'width': map_width,
        'height': map_height,
        'tile_width': tile_width,
        'tile_height': tile_height,
        'tile_grid': tile_grid,
        'layers': layers,
        'tilesets': tilesets,
        'tileset_name': tileset_name
    }


def load_tiled_map_with_names(map_name, tileset_name, tile_index_map, base_path):
    """
    Load Tiled map and convert tile indices to tile names
    
    Args:
        map_name: Map name without extension (e.g., 'refugee_camp_map')
        tileset_name: Tileset name (e.g., 'refugee_camp')
        tile_index_map: Dict mapping {index: tile_name}
        base_path: Directory containing the map file
    
    Returns:
        dict with 'tile_grid' containing tile NAMES instead of indices
    """
    
    # Load the map (with indices)
    tilemap = load_tiled_map(map_name, tileset_name, base_path)
    
    # Convert indices to names
    named_grid = []
    unknown_indices = set()  # Track unmapped indices
    
    for row in tilemap['tile_grid']:
        named_row = []
        for tile_index in row:
            # Get tile name from index map
            if tile_index in tile_index_map:
                tile_name = tile_index_map[tile_index]
            else:
                # Unknown index - use fallback
                tile_name = f'unknown_{tile_index}'
                unknown_indices.add(tile_index)
            
            named_row.append(tile_name)
        named_grid.append(named_row)
    
    # Warn about unmapped indices
    if unknown_indices:
        print(f"   ⚠️ Warning: {len(unknown_indices)} unmapped tile indices: {sorted(unknown_indices)}")
        print(f"   Add these to your tile_index_map!")
    else:
        print(f"   ✅ All tiles mapped successfully")
    
    # Replace tile_grid with named version
    tilemap['tile_grid'] = named_grid
    
    return tilemap


def get_tile_type(x, y, tile_grid):
    """
    Get tile type at coordinates
    
    Args:
        x, y: Tile coordinates
        tile_grid: 2D array of tile names
    
    Returns:
        Tile name string, or None if out of bounds
    """
    if 0 <= y < len(tile_grid) and 0 <= x < len(tile_grid[0]):
        return tile_grid[y][x]
    return None


def is_walkable_tile(tile_name, walkable_tiles):
    """
    Check if a tile is walkable
    
    Args:
        tile_name: Name of the tile
        walkable_tiles: List of walkable tile names
    
    Returns:
        True if walkable, False otherwise
    """
    if tile_name is None:
        return False
    
    # Direct match
    if tile_name in walkable_tiles:
        return True
    
    # Prefix match (e.g., 'grass_light' matches 'grass')
    for walkable in walkable_tiles:
        if tile_name.startswith(walkable + '_'):
            return True
    
    return False