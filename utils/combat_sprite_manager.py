# utils/combat_sprite_manager.py
"""
Combat Sprite Manager - Singleton utility for combat graphics
Follows TileGraphicsManager pattern for consistency
"""

import pygame
import os
from utils.constants import *

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
        
        # Load all combat graphics
        self.load_obstacle_sprites()
        self.load_floor_tiles()
        
        CombatSpriteManager._initialized = True
        print("⚔️ Combat Sprite Manager initialized (singleton)")
    
    def load_obstacle_sprites(self):
        """Load 32x32 obstacle sprites (barrels, crates, etc.)"""
        obstacle_map = {
            'barrel': 'barrel.png',
            'crate': 'crate.png',
            'pillar': 'pillar.png',
            'support_beam': 'support_beam.png'
        }
        
        for obstacle_type, filename in obstacle_map.items():
            filepath = os.path.join(COMBAT_OBSTACLES_PATH, filename)
            
            try:
                if os.path.exists(filepath):
                    sprite = pygame.image.load(filepath)
                    scaled = pygame.transform.scale(sprite, (COMBAT_OBSTACLE_SIZE, COMBAT_OBSTACLE_SIZE))
                    self.obstacle_sprites[obstacle_type] = scaled
                    print(f"✅ Combat obstacle loaded: {obstacle_type}")
                else:
                    # Fallback placeholder
                    self.obstacle_sprites[obstacle_type] = self._create_obstacle_fallback(obstacle_type)
                    print(f"🎨 Using fallback for: {obstacle_type}")
            except Exception as e:
                print(f"⚠️ Error loading {obstacle_type}: {e}")
                self.obstacle_sprites[obstacle_type] = self._create_obstacle_fallback(obstacle_type)
    
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
    
    def _create_obstacle_fallback(self, obstacle_type):
        """Create placeholder for missing obstacle sprite"""
        surface = pygame.Surface((COMBAT_OBSTACLE_SIZE, COMBAT_OBSTACLE_SIZE))
        surface.fill(BROWN)
        pygame.draw.rect(surface, WHITE, (0, 0, COMBAT_OBSTACLE_SIZE, COMBAT_OBSTACLE_SIZE), 2)
        return surface
    
    def _create_floor_fallback(self):
        """Create placeholder for missing floor tile"""
        surface = pygame.Surface((COMBAT_FLOOR_TILE_SIZE, COMBAT_FLOOR_TILE_SIZE))
        surface.fill((50, 50, 50))  # Dark gray
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