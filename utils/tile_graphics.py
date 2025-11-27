# utils/tile_graphics.py
"""
Shared Tile Graphics Manager Utility
Professional reusable graphics system for all tile-based screens

This utility can be used by:
- Redstone town navigation
- Other town navigation screens  
- World map exploration
- Dungeon/location exploration
- Any tile-based system
"""

import pygame
import os
import json
from utils.constants import (BLACK, RED, WHITE,
                             TILES_PATH, REGIONMAP_TILES_PATH, PLAYER_SPRITES_PATH)

class TileGraphicsManager:
    """
    Professional shared tile graphics manager
    Singleton pattern ensures one instance shared across all tile systems
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - ensures single instance across all tile systems"""
        if cls._instance is None:
            cls._instance = super(TileGraphicsManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, tile_size=64):
        # Only initialize once (singleton pattern)
        if TileGraphicsManager._initialized:
            return
            
        self.tile_size = tile_size
        self.tile_images = {}
        self.character_sprites = {}
        self.region_tiles = {}
        self.terrain_names = {} 
        
        # Load graphics with fallback system
        self.load_tile_graphics()
        self.load_character_sprites()
        self.load_region_map_tiles()
        
        TileGraphicsManager._initialized = True
        print("🎨 Shared tile graphics manager initialized (singleton)")
    
    def load_tileset(self, tileset_name, tile_size=None):
        """
        Load a tileset from Aseprite JSON export
        
        Args:
            tileset_name: Name of the tileset (e.g., 'refugee_camp')
            tile_size: Optional override for tile size (defaults to self.tile_size if not specified)
        
        This is ADDITIVE - doesn't replace existing tiles, just adds new ones.
        """
        import json
        from utils.constants import TILESETS_PATH
        
        # Use default tile size if not specified
        if tile_size is None:
            tile_size = self.tile_size
        
        # Build file paths
        json_path = os.path.join(TILESETS_PATH, f"{tileset_name}.json")
        png_path = os.path.join(TILESETS_PATH, f"{tileset_name}.png")
        
        # Check if files exist
        if not os.path.exists(png_path):
            print(f"⚠️ Tileset image not found: {tileset_name}.png")
            print(f"   Will use fallback colors for tiles")
            return False
        
        print(f"📦 Loading tileset: {tileset_name}")
        
        try:
            # Load the sprite sheet image
            sprite_sheet = pygame.image.load(png_path)
            
            # If JSON exists, use it for tile definitions
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    tileset_data = json.load(f)
                
                loaded_count = 0
                
                # Aseprite "JSON Hash" format has frames dictionary
                if 'frames' in tileset_data:
                    frames = tileset_data['frames']
                    
                    for tile_name, tile_info in frames.items():
                        # Extract tile from sprite sheet
                        frame_data = tile_info['frame']
                        x = frame_data['x']
                        y = frame_data['y']
                        w = frame_data['w']
                        h = frame_data['h']
                        
                        # Extract the tile
                        tile_surface = sprite_sheet.subsurface((x, y, w, h))
                        
                        # Scale to desired size
                        scaled_tile = pygame.transform.scale(tile_surface, (tile_size, tile_size))
                        
                        # Clean up the name (remove .png extension if present)
                        clean_name = tile_name.replace('.png', '').replace('.ase', '')
                        
                        # Store in tile_images (same as manual tiles)
                        self.tile_images[clean_name] = scaled_tile
                        loaded_count += 1
                
                print(f"   ✅ Loaded {loaded_count} tiles from {tileset_name}")
                return True
            
            else:
                # No JSON - just load the single PNG as-is
                # This is for simple single-image tilesets
                print(f"   ℹ️ No JSON found, loading {tileset_name}.png as single tile")
                scaled_tile = pygame.transform.scale(sprite_sheet, (tile_size, tile_size))
                self.tile_images[tileset_name] = scaled_tile
                print(f"   ✅ Loaded single tile: {tileset_name}")
                return True
                
        except Exception as e:
            print(f"   ⚠️ Error loading tileset: {e}")
            return False
    
    def load_multiple_tilesets(self, tileset_names, tile_size=None):
        """
        Load multiple tilesets at once
        
        Args:
            tileset_names: List of tileset names ['refugee_camp', 'swamp_church', ...]
            tile_size: Optional tile size override
        """
        success_count = 0
        
        for tileset_name in tileset_names:
            if self.load_tileset(tileset_name, tile_size):
                success_count += 1
        
        print(f"📊 Tilesets loaded: {success_count}/{len(tileset_names)}")
        return success_count == len(tileset_names)
    
    def preload_location_tileset(self, location_id):
        """
        Convenience method to load a tileset for a specific location
        
        Args:
            location_id: Location identifier (e.g., 'refugee_camp_main_nav')
        
        Returns tileset name that was loaded, or None if failed
        """
        # Map location IDs to tileset names
        location_to_tileset = {
            'refugee_camp_main_nav': 'refugee_camp',
            'swamp_church_exterior_nav': 'swamp_church',
            'swamp_church_interior_nav': 'swamp_church',
            'hill_ruins_entrance_nav': 'hill_ruins',
            'red_hollow_mine_pre_entrance_nav': 'red_hollow_mine',
        }
        
        tileset_name = location_to_tileset.get(location_id)
        
        if tileset_name:
            if self.load_tileset(tileset_name):
                return tileset_name
        else:
            print(f"ℹ️ No tileset defined for location: {location_id}")
        
        return None
    
    
    def load_tileset_from_grid(self, tileset_name, tile_map, tile_size=32, columns=8):
        """
        Load tileset by slicing a grid-based sprite sheet
        Uses tile_map to assign names to grid positions
        
        Args:
            tileset_name: Name of PNG file (e.g., 'refugee_camp')
            tile_map: Dict mapping indices to names (e.g., REFUGEE_CAMP_TILE_MAP)
            tile_size: Size of each tile in pixels (default 32)
            columns: Number of tiles per row in sprite sheet (default 8)
        """
        from utils.constants import TILESETS_PATH
        
        png_path = os.path.join(TILESETS_PATH, f"{tileset_name}.png")
        
        if not os.path.exists(png_path):
            print(f"⚠️ Tileset not found: {tileset_name}.png")
            return False
        
        print(f"📦 Loading tileset from grid: {tileset_name}")
        
        try:
            sprite_sheet = pygame.image.load(png_path)
            loaded_count = 0
            
            # Slice the sprite sheet into individual tiles
            for index, tile_name in tile_map.items():
                if index == 0 or tile_name is None:
                    continue  # Skip empty tile
                
                # Calculate position in grid (Tiled uses 1-based indexing)
                tile_index = index - 1  # Convert to 0-based for math
                col = tile_index % columns
                row = tile_index // columns
                
                x = col * tile_size
                y = row * tile_size
                
                ## Extract tile from sprite sheet
                try:
                    tile_surface = sprite_sheet.subsurface((x, y, tile_size, tile_size))
                    
                    # Scale tile to 64×64 for display (2× scale for chunky pixels)
                    scaled_tile = pygame.transform.scale(tile_surface, (64, 64))
                    
                    # Store the scaled version
                    self.tile_images[tile_name] = scaled_tile
                    loaded_count += 1
                except ValueError:
                    # Tile position out of bounds
                    print(f"   ⚠️ Tile {index} ({tile_name}) at ({x},{y}) out of bounds")
            
            print(f"   ✅ Loaded {loaded_count} tiles from grid ({columns} columns)")
            return True
            
        except Exception as e:
            print(f"   ⚠️ Error loading grid tileset: {e}")
            return False
    
    def load_tile_graphics(self):
        """Load all tile graphics for any tile-based system"""
        
        # UNIVERSAL tile graphic definitions
        tile_image_map = {
            # Terrain tiles (used by all locations)
            'street': 'terrain/cobblestone_street.png',
            'alley': 'terrain/dirt_alley.png', 
            'empty_lot': 'terrain/grass_square.png',
            'grass': 'terrain/grass_square.png',
            'dirt': 'terrain/dirt_alley.png',
            'stone_floor': 'terrain/stone_floor.png',
            'town_road': 'terrain/town_road.png',
            
            # Building tiles (reusable across towns)
            'wall': 'buildings/stone_wall.png',
            'wall_north': 'buildings/wall_north.png',
            'wall_south': 'buildings/wall_south.png',
            'wall_east': 'buildings/wall_east.png',
            'wall_west': 'buildings/wall_west.png',
            'wall_corner_nw': 'buildings/wall_corner_nw.png',
            'wall_corner_ne': 'buildings/wall_corner_ne.png',
            'wall_corner_sw': 'buildings/wall_corner_sw.png',
            'wall_corner_se': 'buildings/wall_corner_se.png',
            
            #building exteriors
            'tavern': 'buildings/tavern_exterior.png',
            'general_store': 'buildings/general_store_exterior.png',
            'mayor_office': 'buildings/civic_building.png',
            'house': 'buildings/house_exterior.png',
            'church_nw': 'buildings/church_nw.png',
            'church_sw': 'buildings/church_sw.png',
            'church_ne': 'buildings/church_ne.png',
            'church_se': 'buildings/church_se.png',
            'inn': 'buildings/inn_exterior.png',
            'shop': 'buildings/shop_exterior.png',
           

            # Decoration tiles (universal)
            'town_square_fountain': 'decorations/town_fountain.png',
            'gate_north': 'decorations/gate_north.png',
            'gate_south': 'decorations/gate_south.png',
            'well': 'decorations/water_well.png',
            'tree': 'decorations/tree.png',
            'rock': 'decorations/rock.png',
            
        }
        
        # Load with professional fallback system
        for tile_type, image_path in tile_image_map.items():
            full_path = os.path.join(TILES_PATH, image_path)
            
            try:
                if os.path.exists(full_path):
                    # Load actual graphic
                    image = pygame.image.load(full_path)
                    scaled_image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                    self.tile_images[tile_type] = scaled_image
                    print(f"✅ Tile graphic loaded: {tile_type}")
                else:
                    # Create professional colored fallback
                    self.tile_images[tile_type] = self.create_tile_fallback(tile_type)
                    print(f"🎨 Using colored fallback: {tile_type}")
                    
            except Exception as e:
                print(f"⚠️ Error loading {tile_type}: {e}")
                self.tile_images[tile_type] = self.create_tile_fallback(tile_type)
    
    def load_character_sprites(self):
        """Load character sprites for all tile systems (supports both static and animated sprite sheets)"""

        
        # Player sprites (universal)
        player_sprites = {
            'down': 'player_down.png',
            'up': 'player_up.png', 
            'left': 'player_left.png',
            'right': 'player_right.png'
        }
        
        self.character_sprites['player'] = {}
        self.player_animations = {}  # Store animation data for sprite sheets
        
        # Configuration for sprite sheet animations
        PLAYER_SPRITE_SIZE = 32  # Each frame is 32x32
        PLAYER_FRAME_COUNT = 4   # Number of frames per direction (adjust as needed)
        PLAYER_FRAME_SPEED = 150  # Milliseconds per frame
        
        for direction, sprite_path in player_sprites.items():
            full_path = os.path.join(PLAYER_SPRITES_PATH, sprite_path)
            
            try:
                if os.path.exists(full_path):
                    sprite_image = pygame.image.load(full_path)
                    image_width = sprite_image.get_width()
                    image_height = sprite_image.get_height()
                    
                    # Detect if this is a sprite sheet (width > height)
                    if image_width > PLAYER_SPRITE_SIZE:
                        # Sprite sheet detected - extract frames
                        frame_count = image_width // PLAYER_SPRITE_SIZE
                        frames = []
                        
                        for i in range(frame_count):
                            frame_rect = pygame.Rect(i * PLAYER_SPRITE_SIZE, 0, PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE)
                            frame = sprite_image.subsurface(frame_rect)
                            
                            # Preserve alpha channel
                            if sprite_image.get_flags() & pygame.SRCALPHA:
                                frame = frame.convert_alpha()
                            else:
                                frame = frame.convert()
                            
                            frames.append(frame)
                        
                        # Store animation data
                        self.player_animations[direction] = {
                            'frames': frames,
                            'frame_count': frame_count,
                            'current_frame': 0,
                            'last_update': pygame.time.get_ticks(),
                            'frame_speed': PLAYER_FRAME_SPEED
                        }
                        
                        # Set default sprite to first frame
                        self.character_sprites['player'][direction] = frames[0]
                        print(f"✅ Player sprite sheet loaded: {direction} ({frame_count} frames)")
                        
                    else:
                        # Single static sprite
                        scaled_sprite = pygame.transform.scale(sprite_image, (PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE))
                        self.character_sprites['player'][direction] = scaled_sprite
                        print(f"✅ Player sprite loaded: {direction} (static)")
                        
                else:
                    self.character_sprites['player'][direction] = self.create_player_fallback(direction)
                    print(f"🔴 Using red arrow for player: {direction}")
                    
            except Exception as e:
                print(f"⚠️ Error loading player sprite {direction}: {e}")
                self.character_sprites['player'][direction] = self.create_player_fallback(direction)
        
        # NPC sprites (for future use)
        npc_types = ['guard', 'merchant', 'citizen', 'noble', 'henrik']
        self.character_sprites['npcs'] = {}
        
        for npc_type in npc_types:
            try:
                npc_path = os.path.join(TILES_PATH, f'characters/npcs/{npc_type}.png')
                if os.path.exists(npc_path):
                    npc_sprite = pygame.image.load(npc_path)
                    scaled_npc = pygame.transform.scale(npc_sprite, (32, 32))
                    self.character_sprites['npcs'][npc_type] = scaled_npc
                    print(f"✅ NPC sprite loaded: {npc_type}")
                else:
                    self.character_sprites['npcs'][npc_type] = self.create_npc_fallback(npc_type)
                    print(f"🟡 Using colored fallback for NPC: {npc_type}")
            except Exception as e:
                print(f"⚠️ Error loading NPC sprite {npc_type}: {e}")
                self.character_sprites['npcs'][npc_type] = self.create_npc_fallback(npc_type)

    def update_player_animation(self, direction, is_moving=False):
        """
        Update player animation for the given direction
        
        Args:
            direction: Player's current facing direction ('up', 'down', 'left', 'right')
            is_moving: Whether the player is currently moving (advances frames) or idle (shows first frame)
        """
        if direction not in self.player_animations:
            return  # No animation data for this direction (using static sprite)
        
        anim_data = self.player_animations[direction]
        current_time = pygame.time.get_ticks()
        
        if is_moving:
            # Advance animation frames if enough time has passed
            if current_time - anim_data['last_update'] > anim_data['frame_speed']:
                anim_data['current_frame'] = (anim_data['current_frame'] + 1) % anim_data['frame_count']
                anim_data['last_update'] = current_time
                
                # Update the displayed sprite
                self.character_sprites['player'][direction] = anim_data['frames'][anim_data['current_frame']]
        else:
            # Player is idle - reset to first frame (idle pose)
            anim_data['current_frame'] = 0
            anim_data['last_update'] = current_time
            self.character_sprites['player'][direction] = anim_data['frames'][0]

    
    def load_region_map_tiles(self):
        """
        Load 16x16 region map tiles and scale for display
        Loads both BASE tiles and TRANSITION tiles
        """
        
        DISPLAY_SIZE = 32  # Scale 16x16 source to 32x32 display
        
        # Define terrain code to filename mapping (BASE TILES)
        terrain_files = {
            'H': 'hills.png',
            'F': 'forest.png',
            'M': 'mountains.png',
            '-': 'plains.png',
            'R': 'river.png',
            ':': 'swamp.png',
        }
        
        # Terrain name mapping (for transition filenames)
        self.terrain_names = {
            'H': 'hills',
            'F': 'forest',
            'M': 'mountains',
            '-': 'plains',
            'R': 'river',
            ':': 'swamp',
        }
        
        # Color fallbacks
        fallback_colors = {
            'H': (139, 115, 85),
            'F': (34, 139, 34),
            'M': (105, 105, 105),
            '-': (210, 180, 140),
            'R': (70, 130, 180),
            ':': (85, 107, 47),
        }
        
        loaded_count = 0
        fallback_count = 0
        
        print("🗺️ Loading region map tiles (16x16 → 32x32):")
        
        # Load BASE tiles
        for terrain_code, filename in terrain_files.items():
            file_path = os.path.join(REGIONMAP_TILES_PATH, filename)
            
            try:
                if os.path.exists(file_path):
                    image = pygame.image.load(file_path)
                    scaled_image = pygame.transform.scale(image, (DISPLAY_SIZE, DISPLAY_SIZE))
                    self.region_tiles[terrain_code] = scaled_image
                    loaded_count += 1
                    print(f"   ✅ {terrain_code}: {filename}")
                else:
                    fallback = self._create_region_fallback(terrain_code, fallback_colors, DISPLAY_SIZE)
                    self.region_tiles[terrain_code] = fallback
                    fallback_count += 1
                    print(f"   🎨 {terrain_code}: Fallback")
            except Exception as e:
                print(f"   ⚠️ Error loading {filename}: {e}")
                fallback = self._create_region_fallback(terrain_code, fallback_colors, DISPLAY_SIZE)
                self.region_tiles[terrain_code] = fallback
                fallback_count += 1
        
        print(f"   📊 Base tiles: {loaded_count} loaded, {fallback_count} fallbacks")
        
        # Load TRANSITION tiles (scan directory)
        self._load_transition_tiles(REGIONMAP_TILES_PATH, DISPLAY_SIZE)

    def _load_transition_tiles(self, tiles_path, display_size):
        """
        Scan directory for transition tiles and load them
        Transition naming: {terrain}_{directions}_{neighbor}.png
        File name should follow this orer: 
            ['n', 'e', 's', 'w']  # North=0, East=1, South=2, West=3
            Example: forest_n_e_hills.png
        """
        import glob
        
        transition_count = 0
        
        # Get all PNG files in the directory
        all_files = glob.glob(os.path.join(tiles_path, "*.png"))
        
        # Filter for transition files (contain underscore and direction letters)
        for filepath in all_files:
            filename = os.path.basename(filepath)
            
            # Skip base tiles
            if filename in ['hills.png', 'forest.png', 'mountains.png', 
                        'plains.png', 'river.png', 'swamp.png']:
                continue
            
            # This is a transition tile - load it with its full filename as key
            try:
                image = pygame.image.load(filepath)
                scaled_image = pygame.transform.scale(image, (display_size, display_size))
                
                # Store with filename (without .png) as key
                tile_key = filename.replace('.png', '')
                self.region_tiles[tile_key] = scaled_image
                transition_count += 1
                
            except Exception as e:
                print(f"   ⚠️ Error loading transition {filename}: {e}")
        
        print(f"   🔀 Transition tiles: {transition_count} loaded")

    def _create_region_fallback(self, terrain_code, color_map, display_size):
        """Create fallback tile at display size"""
        surface = pygame.Surface((display_size, display_size))
        color = color_map.get(terrain_code, (128, 128, 128))
        surface.fill(color)
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, display_size, display_size), 1)
        return surface

    def get_region_tile(self, terrain_code, neighbors=None):
        """
        Get region map tile with auto-tiling support
        
        Args:
            terrain_code: Current tile terrain ('H', 'F', etc.)
            neighbors: Dict with 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw' keys
                    Each value is the terrain code in that direction
        
        Returns:
            pygame.Surface: 32x32 tile image
        """
        # If no neighbors provided, return base tile
        if neighbors is None:
            return self.region_tiles.get(terrain_code, self._create_region_fallback(
                terrain_code, 
                {'H': (139, 115, 85), 'F': (34, 139, 34), 'M': (105, 105, 105),
                '-': (210, 180, 140), 'R': (70, 130, 180), ':': (85, 107, 47)},
                32
            ))
        
        # Try to find a matching transition tile
        transition_tile = self._find_transition_tile(terrain_code, neighbors)
        if transition_tile is not None:
            return transition_tile
        
        # Fall back to base tile
        return self.region_tiles.get(terrain_code, self._create_region_fallback(
            terrain_code,
            {'H': (139, 115, 85), 'F': (34, 139, 34), 'M': (105, 105, 105),
            '-': (210, 180, 140), 'R': (70, 130, 180), ':': (85, 107, 47)},
            32
        ))

    def _find_transition_tile(self, terrain_code, neighbors):
        """
        Find the best matching transition tile based on neighbors
        
        Naming convention: {terrain}_{directions}_{neighbor_terrain}.png
        Example: forest_n_e_hills.png (forest with hills to north and east)
        """
        # Get terrain name
        terrain_name = self.terrain_names.get(terrain_code, 'unknown')
        
        # Find which neighbors are DIFFERENT terrain
        different_neighbors = {}
        for direction, neighbor_terrain in neighbors.items():
            if neighbor_terrain and neighbor_terrain != terrain_code:
                different_neighbors[direction] = neighbor_terrain
        
        # If no different neighbors, use base tile
        if not different_neighbors:
            return None
        
        # Group neighbors by terrain type
        neighbor_groups = {}
        for direction, neighbor_terrain in different_neighbors.items():
            if neighbor_terrain not in neighbor_groups:
                neighbor_groups[neighbor_terrain] = []
            neighbor_groups[neighbor_terrain].append(direction)
        
        # Try to find transition for the most common neighbor type
        # (In case of mixed neighbors, prioritize the one with most contacts)
        for neighbor_terrain, directions in sorted(neighbor_groups.items(), 
                                                key=lambda x: len(x[1]), 
                                                reverse=True):
            neighbor_name = self.terrain_names.get(neighbor_terrain, 'unknown')
            
            # Build direction string (sorted for consistency)
            # Cardinal directions only first (n, e, s, w)
            cardinal_dirs = [d for d in directions if d in ['n', 'e', 's', 'w']]
            
            if cardinal_dirs:
                direction_string = '_'.join(sorted(cardinal_dirs, 
                                                key=lambda x: ['n', 'e', 's', 'w'].index(x)))
                
                # Try to find this specific transition
                tile_key = f"{terrain_name}_{direction_string}_{neighbor_name}"
                
                if tile_key in self.region_tiles:
                    return self.region_tiles[tile_key]
                
                # Try individual directions if multi-direction not found
                for single_dir in cardinal_dirs:
                    tile_key = f"{terrain_name}_{single_dir}_{neighbor_name}"
                    if tile_key in self.region_tiles:
                        return self.region_tiles[tile_key]
        
        # No matching transition found
        return None

    def create_tile_fallback(self, tile_type, custom_color=None):
        """
        Create colored fallback tiles with universal color mapping
        
        Args:
            tile_type: Type of tile to create
            custom_color: Optional RGB tuple to override default color
        """
        
        # If custom color provided by map, use it (data-driven approach)
        if custom_color:
            surface = pygame.Surface((self.tile_size, self.tile_size))
            surface.fill(custom_color)
            pygame.draw.rect(surface, BLACK, (0, 0, self.tile_size, self.tile_size), 1)
            return surface
        
        # Otherwise use universal fallback colors
        fallback_colors = {
            # Terrain
            'street': (80, 60, 40),
            'alley': (60, 45, 30), 
            'empty_lot': (0, 100, 0),
            'grass': (0, 100, 0),
            'dirt': (101, 67, 33),
            'stone_floor': (128, 128, 128),
            
            # Buildings
            'wall': (100, 100, 100),
            'tavern': (160, 82, 45),
            'general_store': (160, 82, 45),
            'mayor_office': (120, 80, 60),
            'house': (139, 69, 19),
            'inn': (150, 75, 25),
            'shop': (155, 85, 50),
            'potion_shop': (138, 43, 226),
            'church': (245, 245, 220),
            
            # Decorations
            'town_square': (100, 149, 237),
            'gate': (160, 160, 160),
            'well': (70, 130, 180),
            'tree': (34, 139, 34),
            'rock': (105, 105, 105),
            
            # World map
            'world_grass': (0, 128, 0),
            'world_forest': (0, 100, 0),
            'world_mountain': (139, 137, 137),
            'world_water': (0, 0, 255),
            'world_road': (160, 140, 120)
        }
        
        surface = pygame.Surface((self.tile_size, self.tile_size))
        color = fallback_colors.get(tile_type, (128, 128, 128))  # Gray default
        surface.fill(color)
        
        # Add subtle border for definition
        pygame.draw.rect(surface, BLACK, (0, 0, self.tile_size, self.tile_size), 1)
        
        return surface
    
    def create_player_fallback(self, direction='down'):
        """Create red directional arrow fallback for player"""
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Arrow components based on direction
        if direction == 'up':
            # Triangle pointing up
            triangle = [(16, 6), (10, 16), (22, 16)]
            # Tail (rectangle below triangle)
            tail_rect = pygame.Rect(13, 16, 6, 10)
        elif direction == 'down':
            # Triangle pointing down
            triangle = [(16, 26), (10, 16), (22, 16)]
            # Tail (rectangle above triangle)
            tail_rect = pygame.Rect(13, 6, 6, 10)
        elif direction == 'left':
            # Triangle pointing left
            triangle = [(6, 16), (16, 10), (16, 22)]
            # Tail (rectangle to right of triangle)
            tail_rect = pygame.Rect(16, 13, 10, 6)
        else:  # 'right'
            # Triangle pointing right
            triangle = [(26, 16), (16, 10), (16, 22)]
            # Tail (rectangle to left of triangle)
            tail_rect = pygame.Rect(6, 13, 10, 6)
        
        # Draw tail (filled red rectangle)
        pygame.draw.rect(surface, RED, tail_rect)
        
        # Draw triangle (filled red)
        pygame.draw.polygon(surface, RED, triangle)
        
        return surface
    
    def create_npc_fallback(self, npc_type):
        """Create colored fallback for NPCs"""
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        npc_colors = {
            'guard': (255, 165, 0),      # Orange
            'merchant': (128, 0, 128),   # Purple
            'citizen': (100, 100, 255),  # Blue
            'noble': (255, 215, 0),        #Gold
            'henrik': (139, 90, 43)        # Brown
        }
        
        color = npc_colors.get(npc_type, (255, 255, 0))  # Yellow default
        pygame.draw.circle(surface, color, (16, 16), 10)
        pygame.draw.circle(surface, WHITE, (16, 16), 10, 2)
        return surface
    
    # ========================================
    # PUBLIC API - Used by all tile systems
    # ========================================
    
    def get_tile_image(self, tile_type, custom_color=None):
        """
        Get tile image (graphic or colored fallback)
        
        Args:
            tile_type: Type of tile to get
            custom_color: Optional RGB tuple to override default fallback color
        """
        # If we have a loaded image, use it
        if tile_type in self.tile_images:
            return self.tile_images[tile_type]
        
        # Create fallback with custom color if provided
        return self.create_tile_fallback(tile_type, custom_color)


    
    def get_player_sprite(self, direction='down'):
        """Get player sprite facing specified direction"""
        if 'player' in self.character_sprites and direction in self.character_sprites['player']:
            return self.character_sprites['player'][direction]
        return self.create_player_fallback(direction)
    
    def get_npc_sprite(self, npc_type):
        """Get NPC sprite"""
        if 'npcs' in self.character_sprites and npc_type in self.character_sprites['npcs']:
            return self.character_sprites['npcs'][npc_type]
        return self.create_npc_fallback(npc_type)
    
    def add_custom_tile(self, tile_type, image_path):
        """Add custom tile for specific locations"""
        try:
            if os.path.exists(image_path):
                image = pygame.image.load(image_path)
                scaled_image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                self.tile_images[tile_type] = scaled_image
                print(f"✅ Custom tile added: {tile_type}")
                return True
        except Exception as e:
            print(f"⚠️ Error adding custom tile {tile_type}: {e}")
        return False
    
    def get_graphics_stats(self):
        """Get statistics for debugging"""
        return {
            'total_tiles': len(self.tile_images),
            'player_sprites': len(self.character_sprites.get('player', {})),
            'npc_sprites': len(self.character_sprites.get('npcs', {})),
            'region_tiles': len(self.region_tiles),  # NEW
            'tile_size': self.tile_size
        }

# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

# Global instance accessor
_graphics_manager = None

def get_tile_graphics_manager():
    """Get the shared tile graphics manager instance"""
    global _graphics_manager
    if _graphics_manager is None:
        _graphics_manager = TileGraphicsManager()
    return _graphics_manager

def load_tile_image(tile_type):
    """Convenience function to get any tile image"""
    manager = get_tile_graphics_manager()
    return manager.get_tile_image(tile_type)

def load_player_sprite(direction='down'):
    """Convenience function to get player sprite"""
    manager = get_tile_graphics_manager()
    return manager.get_player_sprite(direction)