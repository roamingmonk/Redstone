# utils/combat_sprite_manager.py
"""
Combat Sprite Manager - Singleton utility for combat graphics
Follows TileGraphicsManager pattern for consistency
"""

import pygame
import os
from utils.constants import (COMBAT_WALLS_PATH, COMBAT_OBSTACLES_PATH,COMBAT_FLOORS_PATH,
                             EFFECTS_SPRITES_PATH,
                             COMBAT_FLOOR_TILE_SIZE, COMBAT_TILE_SIZE,
                             DARK_GRAY, BROWN, WHITE)

class CombatSpriteManager:
    """
    Manages all combat-related sprites: obstacles, floors, effects
    Singleton pattern ensures one instance shared across combat encounters
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern - ensures single instance"""
        if cls._instance is None:
            cls._instance = super(CombatSpriteManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once (singleton pattern)
        if CombatSpriteManager._initialized:
            return
        
        self.obstacle_sprites = {}  # 32x32 obstacles
        self.floor_tiles = {}       # 16x16 tileable floors
        self.effect_sprites = {}    # spell effects, damage indicators
        self.wall_tilesets = {}     # Cache of loaded tilesets
        self.effect_sprites = {}

        # Load all combat graphics
        self.load_obstacle_sprites()
        self.load_floor_tiles()
        self.load_spell_effects()
        # Wall tiles loaded on-demand per battlefield!
        
        CombatSpriteManager._initialized = True
        print("⚔️ Combat Sprite Manager initialized (singleton)")
    
    def load_wall_tileset(self, tileset_name: str):
        """Load a complete wall tileset on-demand"""
        # Check cache first
        if tileset_name in self.wall_tilesets:
            print(f"✅ Wall tileset '{tileset_name}' already cached")
            return
        
        print(f"📦 Loading wall tileset: {tileset_name}")
        
        # Wall tile definitions
        wall_types = [
            'wall_north', 'wall_south', 'wall_east', 'wall_west',
            'corner_nw', 'corner_ne', 'corner_sw', 'corner_se'
        ]
        
        tileset = {}
        
        for wall_type in wall_types:
            # Filename: {tileset}_{wall_type}.png
            filename = f"{tileset_name}_{wall_type}.png"
            filepath = os.path.join(COMBAT_WALLS_PATH, filename)
            
            try:
                if os.path.exists(filepath):
                    tile = pygame.image.load(filepath)
                    tileset[wall_type] = tile
                    print(f"  ✅ {filename}")
                else:
                    tileset[wall_type] = self._create_wall_fallback()
                    print(f"  🎨 Fallback: {filename}")
            except Exception as e:
                print(f"  ⚠️ Error loading {filename}: {e}")
                tileset[wall_type] = self._create_wall_fallback()
        
        # Cache the complete tileset
        self.wall_tilesets[tileset_name] = tileset
        print(f"✅ Wall tileset '{tileset_name}' loaded")
    
    def get_wall_tile(self, tileset_name: str, wall_type: str):
        """Get wall tile from specified tileset"""
        # Load tileset if not cached
        if tileset_name not in self.wall_tilesets:
            self.load_wall_tileset(tileset_name)
        
        tileset = self.wall_tilesets.get(tileset_name, {})
        return tileset.get(wall_type, self._create_wall_fallback())

    def load_obstacle_sprites(self):
        """Load 32x32 obstacle sprites (barrels, crates, etc.)"""
        small_obstacles = {
            'barrel': 'barrel.png',
            'crate': 'crate.png',
            'chest': 'chest.png',
        }

        # Large 48x48 obstacles (fill entire tile)
        large_obstacles = {
            'support_beam': 'support_beam.png',
            'pillar': 'pillar.png',
            'statue': 'statue.png'
        }
        
        # Load small obstacles at 32x32
        for obstacle_type, filename in small_obstacles.items():
            filepath = os.path.join(COMBAT_OBSTACLES_PATH, filename)
            self._load_obstacle(obstacle_type, filepath, 32)
        
        # Load large obstacles at 48x48
        for obstacle_type, filename in large_obstacles.items():
            filepath = os.path.join(COMBAT_OBSTACLES_PATH, filename)
            self._load_obstacle(obstacle_type, filepath, 48)
    
    def _load_obstacle(self, obstacle_type, filepath, size):
        """Helper to load obstacle at specified size"""
        try:
            if os.path.exists(filepath):
                sprite = pygame.image.load(filepath)
                scaled = pygame.transform.scale(sprite, (size, size))
                self.obstacle_sprites[obstacle_type] = scaled
                print(f"✅ Combat obstacle loaded: {obstacle_type} ({size}x{size})")
            else:
                self.obstacle_sprites[obstacle_type] = self._create_obstacle_fallback(obstacle_type, size)
                print(f"🎨 Using fallback for: {obstacle_type} ({size}x{size})")
        except Exception as e:
            print(f"⚠️ Error loading {obstacle_type}: {e}")
            self.obstacle_sprites[obstacle_type] = self._create_obstacle_fallback(obstacle_type, size)

    def load_floor_tiles(self):
        """Load 16x16 tileable floor textures"""
        floor_map = {
            'cobblestone_street_16x16': 'cobblestone_street_16x16.png',
            'stone_floor_16x16': 'stone_floor_16x16.png',
            'dirt_floor_16x16': 'dirt_floor_16x16.png'
        }
        
        for floor_type, filename in floor_map.items():
            filepath = os.path.join(COMBAT_FLOORS_PATH, filename)
            
            try:
                if os.path.exists(filepath):
                    tile = pygame.image.load(filepath)
                    # Keep at 16x16 - will be tiled when rendering
                    self.floor_tiles[floor_type] = tile
                    print(f"✅ Combat floor loaded: {floor_type}")
                else:
                    self.floor_tiles[floor_type] = self._create_floor_fallback()
                    print(f"🎨 Using fallback floor: {floor_type}")
            except Exception as e:
                print(f"⚠️ Error loading {floor_type}: {e}")
                self.floor_tiles[floor_type] = self._create_floor_fallback()
    
    def load_spell_effects(self):
        """Load spell effect sprites (lightning bolts, fireballs, etc.)"""
        
        effects_path = os.path.join('assets', 'images', 'sprites', 'effects')
        
        # Load Force projectile sprites
        try:
            # Horizontal/Vertical firebolt
            force_h_v_path = os.path.join(effects_path, 'force_h_v.png')
            if os.path.exists(force_h_v_path):
                sprite = pygame.image.load(force_h_v_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['force_h_v'] = sprite
                print("💜 Loaded force_h_v.png")
            
            # Diagonal force
            force_diag_path = os.path.join(effects_path, 'force_diag.png')
            if os.path.exists(force_diag_path):
                sprite = pygame.image.load(force_diag_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['force_diag'] = sprite
                print("💜 Loaded force_diag.png")
        except Exception as e:
            print(f"⚠️ Error loading force sprites: {e}")

        # Load Firebolt projectile sprites
        try:
            # Horizontal/Vertical firebolt
            firebolt_h_v_path = os.path.join(effects_path, 'firebolt_h_v.png')
            if os.path.exists(firebolt_h_v_path):
                sprite = pygame.image.load(firebolt_h_v_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['firebolt_h_v'] = sprite
                print("🔥 Loaded firebolt_h_v.png")
            
            # Diagonal firebolt
            firebolt_diag_path = os.path.join(effects_path, 'firebolt_diag.png')
            if os.path.exists(firebolt_diag_path):
                sprite = pygame.image.load(firebolt_diag_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['firebolt_diag'] = sprite
                print("🔥 Loaded firebolt_diag.png")
        except Exception as e:
            print(f"⚠️ Error loading firebolt sprites: {e}")
            
        # Load Ice Knife projectile sprites
        try:
            # Horizontal/Vertical ice
            ice_h_v_path = os.path.join(effects_path, 'ice_h_v.png')
            if os.path.exists(ice_h_v_path):
                sprite = pygame.image.load(ice_h_v_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['ice_h_v'] = sprite
                print("❄️ Loaded ice_h_v.png")

            # Diagonal ice
            ice_diag_path = os.path.join(effects_path, 'ice_diag.png')
            if os.path.exists(ice_diag_path):
                sprite = pygame.image.load(ice_diag_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['ice_diag'] = sprite
                print("❄️ Loaded ice_diag.png")
        except Exception as e:
            print(f"⚠️ Error loading ice sprites: {e}")

         # Load necrotic projectile sprites
        try:
            # Horizontal/Vertical ice
            necrotic_h_v_path = os.path.join(effects_path, 'necrotic_h_v.png')
            if os.path.exists(necrotic_h_v_path):
                sprite = pygame.image.load(necrotic_h_v_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['necrotic_h_v'] = sprite
                print(" Loaded necrotic_h_v.png")

            # Diagonal ice
            necrotic_diag_path = os.path.join(effects_path, 'necrotic_diag.png')
            if os.path.exists(ice_diag_path):
                sprite = pygame.image.load(necrotic_diag_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['necrotic_diag'] = sprite
                print(" Loaded necrotic_diag.png")
        except Exception as e:
            print(f"⚠️ Error loading necrotic sprites: {e}")


        # Load Arrow projectile sprites (for bows/crossbows)
        try:
            # Horizontal/Vertical arrow
            arrow_h_v_path = os.path.join(effects_path, 'arrow_h_v.png')
            if os.path.exists(arrow_h_v_path):
                sprite = pygame.image.load(arrow_h_v_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['arrow_h_v'] = sprite
                print("🏹 Loaded arrow_h_v.png")
            
            # Diagonal arrow
            arrow_diag_path = os.path.join(effects_path, 'arrow_diag.png')
            if os.path.exists(arrow_diag_path):
                sprite = pygame.image.load(arrow_diag_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['arrow_diag'] = sprite
                print("🏹 Loaded arrow_diag.png")
        except Exception as e:
            print(f"⚠️ Error loading arrow sprites: {e}")

        # Load Bullet projectile sprites (for slings)
        try:
            # Horizontal/Vertical bullet
            bullet_h_v_path = os.path.join(effects_path, 'bullet_h_v.png')
            if os.path.exists(bullet_h_v_path):
                sprite = pygame.image.load(bullet_h_v_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['bullet_h_v'] = sprite
                print("🪨 Loaded bullet_h_v.png")
            
            # Diagonal bullet
            bullet_diag_path = os.path.join(effects_path, 'bullet_diag.png')
            if os.path.exists(bullet_diag_path):
                sprite = pygame.image.load(bullet_diag_path).convert_alpha()
                sprite = pygame.transform.scale(sprite, (48, 48))
                self.effect_sprites['bullet_diag'] = sprite
                print("🪨 Loaded bullet_diag.png")
        except Exception as e:
            print(f"⚠️ Error loading bullet sprites: {e}")

        # Load Impact sprites (for projectile hit effects)
        impact_sprites = {
            'firebolt_impact': 'firebolt_impact.png',
            'force_impact': 'force_impact.png',
            'ice_impact': 'ice_impact.png'
        }

        for sprite_key, filename in impact_sprites.items():
            filepath = os.path.join(effects_path, filename)
            try:
                if os.path.exists(filepath):
                    sprite = pygame.image.load(filepath).convert_alpha()
                    # Keep impact sprites at their original size for now
                    self.effect_sprites[sprite_key] = sprite
                    print(f"💥 Impact sprite loaded: {sprite_key}")
                else:
                    print(f"⚠️ Missing impact sprite: {filename}")
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")
        
        # Lightning Bolt images
        lightning_files = {
            'lightning_h_v': 'lightning_bolt_h_v.png',
            'lightning_diag': 'lightning_bolt_diag.png'
        }
        
        for effect_key, filename in lightning_files.items():
            filepath = os.path.join(EFFECTS_SPRITES_PATH, filename)
            
            try:
                if os.path.exists(filepath):
                    sprite = pygame.image.load(filepath).convert_alpha()
                    self.effect_sprites[effect_key] = sprite
                    print(f"⚡ Spell effect loaded: {effect_key}")
                else:
                    self.effect_sprites[effect_key] = self._create_effect_fallback()
                    print(f"⚠️ Missing effect sprite: {filename}, using fallback")
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")
                self.effect_sprites[effect_key] = self._create_effect_fallback()
        
        # 🔥 burning_hands images (same pattern as lightning)
        burning_hands_files = {
            'burning_hands_h_v': 'burning_hands_h_v.png',
            'burning_hands_diag': 'burning_hands_diag.png'
        }
        
        for effect_key, filename in burning_hands_files.items():
            filepath = os.path.join(EFFECTS_SPRITES_PATH, filename)
            
            try:
                if os.path.exists(filepath):
                    sprite = pygame.image.load(filepath).convert_alpha()
                    self.effect_sprites[effect_key] = sprite
                    print(f"🔥 Spell effect loaded: {effect_key}")
                else:
                    self.effect_sprites[effect_key] = self._create_effect_fallback()
                    print(f"⚠️ Missing effect sprite: {filename}, using fallback")
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")
                self.effect_sprites[effect_key] = self._create_effect_fallback()

        # 🔥 Fireball Animation Frames
        fireball_sheet_path = os.path.join(EFFECTS_SPRITES_PATH, 'fireball_burn.png')
        
        try:
            if os.path.exists(fireball_sheet_path):
                sprite_sheet = pygame.image.load(fireball_sheet_path).convert_alpha()
                
                # Extract 10 frames (48x48 each) from horizontal sprite sheet
                fireball_frames = []
                frame_width = 48
                frame_height = 48
                
                for i in range(10):
                    # Extract each frame from the sprite sheet
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sprite_sheet, (0, 0), (i * frame_width, 0, frame_width, frame_height))
                    fireball_frames.append(frame)
                
                self.effect_sprites['fireball_frames'] = fireball_frames
                print(f"🔥 Fireball animation loaded: 10 frames")
            else:
                print(f"⚠️ Missing fireball sprite sheet, using fallback")
                self.effect_sprites['fireball_frames'] = [self._create_effect_fallback() for _ in range(10)]
        except Exception as e:
            print(f"⚠️ Error loading fireball animation: {e}")
            self.effect_sprites['fireball_frames'] = [self._create_effect_fallback() for _ in range(10)]
    
    def _create_effect_fallback(self):
        """Create placeholder for missing spell effect"""
        surface = pygame.Surface((COMBAT_TILE_SIZE, COMBAT_TILE_SIZE), pygame.SRCALPHA)
        # Draw a simple lightning bolt placeholder
        pygame.draw.line(surface, (100, 200, 255), (24, 0), (24, 48), 3)
        pygame.draw.line(surface, (200, 230, 255), (24, 0), (24, 48), 1)
        return surface

    def get_effect_sprite(self, effect_type):
        """Get spell effect sprite by type"""
        return self.effect_sprites.get(effect_type, self._create_effect_fallback())
    
    def _create_obstacle_fallback(self, obstacle_type, size=32):
        """Create placeholder for missing obstacle sprite"""
        surface = pygame.Surface((size, size))
        surface.fill(BROWN)
        pygame.draw.rect(surface, WHITE, (0, 0, size, size), 2)
        return surface
    
    def _create_floor_fallback(self):
        """Create placeholder for missing floor tile"""
        surface = pygame.Surface((COMBAT_FLOOR_TILE_SIZE, COMBAT_FLOOR_TILE_SIZE))
        surface.fill((50, 50, 50))  # Dark gray
        return surface
    
    def _create_wall_fallback(self):
        """Create placeholder for missing wall tile"""
        surface = pygame.Surface((COMBAT_TILE_SIZE, COMBAT_TILE_SIZE))
        surface.fill(DARK_GRAY)
        pygame.draw.rect(surface, WHITE, (0, 0, COMBAT_TILE_SIZE, COMBAT_TILE_SIZE), 2)
        return surface

    # === PUBLIC API ===
    
    def get_obstacle_sprite(self, obstacle_type):
        """Get obstacle sprite by type"""
        return self.obstacle_sprites.get(obstacle_type, self._create_obstacle_fallback(obstacle_type))
    
    def get_floor_tile(self, floor_type):
        """Get floor tile by type"""
        return self.floor_tiles.get(floor_type, self._create_floor_fallback())

# ========================================
# CONVENIENCE FUNCTION
# ========================================

_combat_sprite_manager = None

def get_combat_sprite_manager():
    """Get the shared combat sprite manager instance"""
    global _combat_sprite_manager
    if _combat_sprite_manager is None:
        _combat_sprite_manager = CombatSpriteManager()
    return _combat_sprite_manager