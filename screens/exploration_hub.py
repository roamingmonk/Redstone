"""
Exploration Hub - Interactive Regional Map
Tile-based visualization of Redstone Region with clickable locations
Replaces the list-based exploration hub with an immersive map experience
"""

import pygame
from data.maps.redstone_region import (
    REDSTONE_REGION_TERRAIN, REDSTONE_REGION_LOCATIONS, TERRAIN_COLORS,
    REDSTONE_REGION_TILE_SIZE, REDSTONE_REGION_MAP_X, REDSTONE_REGION_MAP_Y,
    REDSTONE_REGION_GRID_WIDTH, REDSTONE_REGION_GRID_HEIGHT,
    is_location_discovered, is_location_completed
)
from utils.constants import YELLOW, WHITE, BLACK, GRAY, GREEN
from utils.graphics import draw_button, draw_centered_text
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from data.maps.redstone_region import get_terrain_neighbors

class ExplorationHubManager:
    """Manages regional map display and location selection"""
    
    def __init__(self):
        self.hovered_location = None
        self.clickable_areas = {}
    
    def render(self, surface, game_state, fonts, images):
        """Render the regional map with clickable locations"""
        surface.fill(BLACK)
        
        # Party status panel (right side)
        portrait_rects = draw_party_status_panel(surface, game_state, fonts)
        
        # Title
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        title_text = "THE REDSTONE REGION"
        draw_centered_text(surface, title_text, title_font, 40, YELLOW)
        
        # Subtitle
        subtitle_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
        subtitle_text = "Choose your investigation destination"
        draw_centered_text(surface, subtitle_text, subtitle_font, 75, WHITE)
        
        # Render terrain grid
        self._render_terrain(surface)
        
        # Render discovered locations
        self._render_locations(surface, game_state, fonts)
        
        # Render location info panel (if hovered)
        if self.hovered_location:
            self._render_location_info(surface, game_state, fonts)
        
        # Discovery counter
        self._render_discovery_counter(surface, game_state, fonts)
        
        # Return button
        button_font = fonts.get('fantasy_medium', fonts.get('normal', fonts['normal']))
        return_button = draw_button(surface, 412, 680, 250, 50,
                                   "RETURN TO TOWN", button_font)
        
        self.clickable_areas['return'] = return_button
        
        return {
            'button_rects': self.clickable_areas,
            'portrait_rects': portrait_rects
        }
    
    def _render_terrain(self, surface):
        """Draw terrain tiles with auto-tiling transitions"""
        
        
        graphics_mgr = get_tile_graphics_manager()
        
        for y in range(REDSTONE_REGION_GRID_HEIGHT):
            for x in range(REDSTONE_REGION_GRID_WIDTH):
                terrain = REDSTONE_REGION_TERRAIN[y][x]
                
                # Get neighbors for auto-tiling
                neighbors = get_terrain_neighbors(x, y)
                
                # Get tile with transition support
                tile_image = graphics_mgr.get_region_tile(terrain, neighbors)
                
                screen_x = REDSTONE_REGION_MAP_X + (x * REDSTONE_REGION_TILE_SIZE)
                screen_y = REDSTONE_REGION_MAP_Y + (y * REDSTONE_REGION_TILE_SIZE)
                
                # Draw tile
                surface.blit(tile_image, (screen_x, screen_y))
    
    def _render_locations(self, surface, game_state, fonts):
        """Draw location icons for discovered locations"""
        for location_id, location_data in REDSTONE_REGION_LOCATIONS.items():
            if not is_location_discovered(location_data, game_state):
                continue
            
            grid_x, grid_y = location_data['grid_pos']
            screen_x = REDSTONE_REGION_MAP_X + (grid_x * REDSTONE_REGION_TILE_SIZE)
            screen_y = REDSTONE_REGION_MAP_Y + (grid_y * REDSTONE_REGION_TILE_SIZE)
            
            center = (screen_x + REDSTONE_REGION_TILE_SIZE // 2, 
                     screen_y + REDSTONE_REGION_TILE_SIZE // 2)
            
            # Draw icon background circle
            icon_color = location_data.get('icon_color', WHITE)
            pygame.draw.circle(surface, icon_color, center, 14)
            pygame.draw.circle(surface, BLACK, center, 14, 2)
            
            # Highlight if hovered
            if self.hovered_location == location_id:
                pygame.draw.circle(surface, YELLOW, center, 16, 3)
            
            # Draw completion checkmark if completed
            if is_location_completed(location_id, game_state):
                check_font = fonts.get('small', fonts['normal'])
                check_surface = check_font.render('✓', True, GREEN)
                check_rect = check_surface.get_rect(center=(center[0] + 12, center[1] - 12))
                
                # Draw white background circle for checkmark
                pygame.draw.circle(surface, WHITE, check_rect.center, 8)
                pygame.draw.circle(surface, GREEN, check_rect.center, 8, 2)
                surface.blit(check_surface, check_rect)
            
            # Store clickable area (full tile, not just circle)
            click_rect = pygame.Rect(screen_x, screen_y, 
                                    REDSTONE_REGION_TILE_SIZE, 
                                    REDSTONE_REGION_TILE_SIZE)
            self.clickable_areas[location_id] = click_rect
    
    def _render_location_info(self, surface, game_state, fonts):
        """Render info panel for hovered location"""
        location_data = REDSTONE_REGION_LOCATIONS[self.hovered_location]
        
        # Draw info box at bottom
        info_box = pygame.Rect(200, 620, 624, 50)
        pygame.draw.rect(surface, (40, 40, 40), info_box)
        pygame.draw.rect(surface, YELLOW, info_box, 2)
        
        # Location name
        name_font = fonts.get('fantasy_medium', fonts.get('normal', fonts['normal']))
        name_surface = name_font.render(location_data['name'], True, YELLOW)
        name_rect = name_surface.get_rect(center=(512, 635))
        surface.blit(name_surface, name_rect)
        
        # Description
        desc_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
        desc_surface = desc_font.render(location_data['description'], True, WHITE)
        desc_rect = desc_surface.get_rect(center=(512, 655))
        surface.blit(desc_surface, desc_rect)
    
    def _render_discovery_counter(self, surface, game_state, fonts):
        """Render discovery counter showing X of Y locations discovered"""
        discovered_count = 0
        total_count = 0
        
        for location_id, location_data in REDSTONE_REGION_LOCATIONS.items():
            # Skip Redstone town (always visible, not a discovery)
            if location_data.get('discovery_flag') is None:
                continue
            
            total_count += 1
            if is_location_discovered(location_data, game_state):
                discovered_count += 1
        
        counter_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
        counter_text = f"Discovered: {discovered_count} of {total_count} locations"
        counter_surface = counter_font.render(counter_text, True, WHITE)
        counter_rect = counter_surface.get_rect(center=(512, 100))
        surface.blit(counter_surface, counter_rect)
    
    def handle_mouse_move(self, pos):
        """Update hovered location based on mouse position"""
        self.hovered_location = None
        
        for location_id, click_rect in self.clickable_areas.items():
            if location_id == 'return':
                continue
            if click_rect.collidepoint(pos):
                self.hovered_location = location_id
                break
    
    def handle_click(self, pos, game_state, event_manager):
        """Handle location selection"""
        # Check return button
        if 'return' in self.clickable_areas:
            if self.clickable_areas['return'].collidepoint(pos):
                event_manager.emit("SCREEN_CHANGE", {"target_screen": "redstone_town"})
                return True
        
        # Check location clicks
        for location_id, click_rect in self.clickable_areas.items():
            if location_id == 'return':
                continue
            if click_rect.collidepoint(pos):
                location_data = REDSTONE_REGION_LOCATIONS[location_id]
                target = location_data['target']
                print(f"🗺️ Traveling to {location_data['name']} → {target}")
                event_manager.emit("SCREEN_CHANGE", {"target_screen": target})
                return True
        
        return False


# Global manager instance
_hub_manager = None

def get_hub_manager():
    """Get or create hub manager singleton"""
    global _hub_manager
    if _hub_manager is None:
        _hub_manager = ExplorationHubManager()
    return _hub_manager

def draw_exploration_hub(surface, game_state, fonts, images):
    """Main render function for exploration hub (ScreenManager compatibility)"""
    hub_manager = get_hub_manager()
    return hub_manager.render(surface, game_state, fonts, images)

def register_exploration_hub_buttons(screen_manager):
    """Register clickable areas with InputHandler"""
    if not (screen_manager and hasattr(screen_manager, 'input_handler')):
        print(f"⚠️ Cannot register exploration_hub: InputHandler not available")
        return
    
    input_handler = screen_manager.input_handler
    game_state = getattr(screen_manager, '_current_game_state', None)
    
    if not game_state:
        print(f"⚠️ Cannot register exploration_hub: GameState not available")
        return
    
    # Get fonts for rendering
    controller = getattr(screen_manager, '_current_game_controller', None)
    if controller and hasattr(controller, 'fonts'):
        fonts = controller.fonts
    else:
        fonts = {
            'normal': pygame.font.Font(None, 24),
            'fantasy_large': pygame.font.Font(None, 36),
            'fantasy_medium': pygame.font.Font(None, 28),
            'fantasy_small': pygame.font.Font(None, 20)
        }
    
    # Render to temp surface to get button rects
    temp_surface = pygame.Surface((1024, 768))
    hub_manager = get_hub_manager()
    result = hub_manager.render(temp_surface, game_state, fonts, {})
    
    button_rects = result.get('button_rects', {})
    
    if not button_rects:
        print(f"⚠️ No button rects found for exploration_hub")
        return
    
    # Register each button
    registered_count = 0
    for action_id, button_rect in button_rects.items():
        if action_id == 'return':
            event_data = {'action': 'return'}
        else:
            event_data = {'action': 'navigate', 'location_id': action_id}
        
        input_handler.register_clickable(
            screen_name='exploration_hub',
            rect=button_rect,
            event_type='EXPLORATION_HUB_ACTION',
            event_data=event_data
        )
        registered_count += 1
    
    print(f"🗺️ Registered {registered_count} exploration hub buttons")