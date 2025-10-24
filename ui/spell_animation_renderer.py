# ui/spell_animation_renderer.py

import pygame
import time
import random

class SpellAnimationRenderer:
    """Centralized spell animation rendering"""
    
    def __init__(self, sprite_manager):
        self.sprite_manager = sprite_manager
        self._renderers = {
            'lightning_line': self._render_line_animation,
            'fire_line': self._render_line_animation,
            'fire_area': self._render_area_burst,
            'fire_projectile': self._render_projectile,
            'force_projectile': self._render_projectile,
            # Add more as needed
        }
    
    def render(self, surface, animation_data, grid_offset, tile_size, 
               elapsed_time, current_tile, animation_alpha, particles):
        """Main render dispatch"""
        anim_type = animation_data.get('type', 'projectile')
        renderer = self._renderers.get(anim_type, self._render_default)
        
        # Pass context to renderer
        context = {
            'surface': surface,
            'grid_offset': grid_offset,
            'tile_size': tile_size,
            'elapsed': elapsed_time,
            'current_tile': current_tile,
            'alpha': animation_alpha,
            'particles': particles
        }
        
        renderer(animation_data, context)
    
    def _render_line_animation(self, anim_data, context):
        """Render line spells (lightning bolt, burning hands)"""
        surface = context['surface']
        grid_offset = context['grid_offset']
        tile_size = context['tile_size']
        alpha = context['alpha']
        current_tile = context['current_tile']
        
        # Get animation tiles
        animation_tiles = anim_data.get('tiles', [])
        if len(animation_tiles) == 0:
            return
        
        caster_pos = anim_data.get('caster_pos')
        anim_type = anim_data.get('type')  # 'lightning_bolt' or 'burning_hands'
        
        # Calculate direction for rotation
        first_tile = animation_tiles[0]
        dx = first_tile[0] - caster_pos[0]
        dy = first_tile[1] - caster_pos[1]
        
        # Normalize direction
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        
        # Determine which image and rotation to use
        is_diagonal = (dx != 0 and dy != 0)
        
        # Determine sprite prefix based on animation type
        if anim_type in ['burning_hands', 'fire_line']:
            sprite_prefix = 'burning_hands'
        else:
            sprite_prefix = 'lightning'
        
        if is_diagonal:
            sprite_key = f'{sprite_prefix}_diag'
            base_image = self.sprite_manager.get_effect_sprite(sprite_key)
            # NE=0°, SE=90°, SW=180°, NW=270°
            if dx > 0 and dy < 0:  # NE
                angle = 0
            elif dx > 0 and dy > 0:  # SE
                angle = 90
            elif dx < 0 and dy > 0:  # SW
                angle = 180
            else:  # NW
                angle = 270
        else:
            sprite_key = f'{sprite_prefix}_h_v'
            base_image = self.sprite_manager.get_effect_sprite(sprite_key)
            # N=0°, E=90°, S=180°, W=270°
            if dy < 0:  # North
                angle = 0
            elif dx > 0:  # East
                angle = 90
            elif dy > 0:  # South
                angle = 180
            else:  # West
                angle = 270
        
        if base_image:
            # Rotate the image
            rotated = pygame.transform.rotate(base_image, angle)
            
            # Draw on all tiles up to current animation point
            tiles_to_show = current_tile + 1
            for i in range(min(tiles_to_show, len(animation_tiles))):
                tile_pos = animation_tiles[i]
                screen_x = grid_offset[0] + (tile_pos[0] * tile_size)
                screen_y = grid_offset[1] + (tile_pos[1] * tile_size)
                
                # Apply alpha fade
                rotated.set_alpha(alpha)
                
                # Center sprite on tile
                sprite_rect = rotated.get_rect()
                sprite_rect.center = (
                    screen_x + tile_size // 2,
                    screen_y + tile_size // 2
                )
                
                surface.blit(rotated, sprite_rect)
        
        # Render particles
        self._render_particles(context['particles'], context)
    
    def _render_area_burst(self, anim_data, context):
        """Render area spells (fireball)"""
        surface = context['surface']
        grid_offset = context['grid_offset']
        tile_size = context['tile_size']
        
        # Get fireball frames
        fireball_frames = self.sprite_manager.get_effect_sprite('fireball_frames')
        
        if fireball_frames and len(fireball_frames) > 0:
            tile_data = anim_data.get('tile_data', [])
            elapsed = context['elapsed']
            
            # Render each tile with its own animation state
            for tile_info in tile_data:
                tile_pos = tile_info['position']
                start_delay = tile_info['start_delay']
                frame_offset = tile_info['frame_offset']
                
                # Check if this tile should be visible yet (expansion effect)
                if elapsed < start_delay:
                    continue  # Tile hasn't ignited yet
                
                # Calculate which frame to show (0.1 seconds per frame, looping)
                tile_elapsed = elapsed - start_delay
                frame_time = 0.1  # Each frame shows for 0.1 seconds
                frame_index = (int(tile_elapsed / frame_time) + frame_offset) % 10
                
                # Get the frame
                frame = fireball_frames[frame_index]
                
                # Calculate screen position
                screen_x = grid_offset[0] + (tile_pos[0] * tile_size)
                screen_y = grid_offset[1] + (tile_pos[1] * tile_size)
                
                # Center the frame on the tile
                frame_rect = frame.get_rect()
                frame_rect.center = (screen_x + tile_size // 2, screen_y + tile_size // 2)
                
                surface.blit(frame, frame_rect)
        
        # Render particles (fireball also has particles)
        self._render_particles(context['particles'], context)
    
    def _render_particles(self, particles, context):
        """Render impact particles"""
        if not particles:
            return
        
        surface = context['surface']
        grid_offset = context['grid_offset']
        tile_size = context['tile_size']
        
        for particle in particles:
            # Convert grid position to screen position
            screen_x = grid_offset[0] + (particle['x'] * tile_size) + tile_size // 2
            screen_y = grid_offset[1] + (particle['y'] * tile_size) + tile_size // 2
            
            # Particle size based on life (starts at 5, shrinks to 1)
            size = int(2 + (3 * particle['life']))
            
            # Particle alpha based on life
            alpha = int(255 * particle['life'])
            
            # Create particle surface with alpha
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = particle['color'] + (alpha,)
            pygame.draw.circle(particle_surf, color_with_alpha, (size, size), size)
            
            surface.blit(particle_surf, (int(screen_x - size), int(screen_y - size)))

    def _render_projectile(self, anim_data, context):
        """Render projectile spells (firebolt, magic dart, etc.)"""
        surface = context['surface']
        grid_offset = context['grid_offset']
        tile_size = context['tile_size']
        elapsed = context['elapsed']
        alpha = context.get('alpha', 255)
        
        start_pos = anim_data.get('start_pos')
        end_pos = anim_data.get('end_pos')
        animation_type = anim_data.get('type', 'fire_projectile')
        
        if not start_pos or not end_pos:
            return
        
        # Map animation type to sprite prefix
        sprite_prefix_map = {
            'fire_projectile': 'firebolt',
            'force_projectile': 'force',
            'cold_projectile': 'ice',
            'acid_projectile': 'acid'
        }

        sprite_prefix = sprite_prefix_map.get(animation_type, 'firebolt')

        # Calculate projectile travel duration (0.5 seconds)
        travel_duration = 0.5
        progress = min(elapsed / travel_duration, 1.0)
        
        # Lerp from start to end
        current_x = start_pos[0] + (end_pos[0] - start_pos[0]) * progress
        current_y = start_pos[1] + (end_pos[1] - start_pos[1]) * progress
        
        # Convert to screen coordinates
        screen_x = grid_offset[0] + (current_x * tile_size) + (tile_size // 2)
        screen_y = grid_offset[1] + (current_y * tile_size) + (tile_size // 2)
        
        # Calculate direction for rotation
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Normalize direction
        if dx != 0:
            dx = dx / abs(dx)
        if dy != 0:
            dy = dy / abs(dy)
        
        # Determine which sprite to use
        is_diagonal = (dx != 0 and dy != 0)
        
        if is_diagonal:
            sprite_key = f'{sprite_prefix}_diag'
            base_image = self.sprite_manager.get_effect_sprite(sprite_key)
            # NE=0°, SE=90°, SW=180°, NW=270°
            if dx > 0 and dy < 0:  # NE
                angle = 0
            elif dx > 0 and dy > 0:  # SE
                angle = 90
            elif dx < 0 and dy > 0:  # SW
                angle = 180
            else:  # NW
                angle = 270
        else:
            sprite_key = f'{sprite_prefix}_h_v'
            base_image = self.sprite_manager.get_effect_sprite(sprite_key)
            # N=0°, E=90°, S=180°, W=270°
            if dy < 0:  # North
                angle = 0
            elif dx > 0:  # East
                angle = 90
            elif dy > 0:  # South
                angle = 180
            else:  # West
                angle = 270
        
        # Render the projectile
        if base_image:
            rotated = pygame.transform.rotate(base_image, angle)
            rotated.set_alpha(alpha)
            
            sprite_rect = rotated.get_rect()
            sprite_rect.center = (int(screen_x), int(screen_y))
            
            surface.blit(rotated, sprite_rect)
            print(f"🔥 Rendering {sprite_key} at ({int(screen_x)}, {int(screen_y)})")  # DEBUG
        else:
            # Fallback: draw a colored circle
            print(f"⚠️ Sprite '{sprite_key}' not found, using fallback")  # DEBUG
            fallback_colors = {
                'firebolt': (255, 100, 0),
                'fire': (255, 100, 0),
                'force': (150, 100, 255),
                'ice': (100, 200, 255),
                'acid': (100, 255, 100)
            }
            color = fallback_colors.get(sprite_prefix, (255, 255, 255))
            pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), 8)
        
        # Render trail particles
        self._render_particles(context.get('particles', []), context)

    def _render_default(self, anim_data, context):
        """Fallback renderer - simple flash effect"""
        surface = context['surface']
        grid_offset = context['grid_offset']
        tile_size = context['tile_size']
        alpha = context.get('alpha', 255)
        
        # Get target tiles
        tiles = anim_data.get('tiles', [])
        
        # Draw a simple white flash on each affected tile
        for tile_pos in tiles:
            screen_x = grid_offset[0] + (tile_pos[0] * tile_size)
            screen_y = grid_offset[1] + (tile_pos[1] * tile_size)
            
            # Create semi-transparent white square
            flash_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, min(alpha, 150)))  # White with fade
            surface.blit(flash_surf, (screen_x, screen_y))
        
        # Also render particles if they exist
        self._render_particles(context.get('particles', []), context)