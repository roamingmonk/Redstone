# screens/act_two_transition.py
"""
Terror in Redstone - Act II Transition System
Single cinematic scene marking the transition from tavern to exploration
Follows intro_scenes.py architecture for consistency
"""

import pygame
import json
import os
from utils.constants import (
    BLACK, YELLOW, BROWN, DARK_GRAY, wrap_text,
    # Intro-specific constants (reused for Act II)
    INTRO_TITLE_Y, INTRO_TITLE_DECORATION_OFFSET, INTRO_CONTENT_START_Y,
    INTRO_CONTENT_LINE_SPACING, INTRO_CONTENT_PARAGRAPH_SPACING, INTRO_CONTENT_MAX_WIDTH,
    INTRO_BUTTON_Y, INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT, INTRO_BUTTON_SPACING,
    INTRO_OVERLAY_ALPHA, INTRO_MOUNTAIN_HEIGHT_RATIO, BUTTON_SIZES,
    INTRO_SKY_DUSK, INTRO_SKY_NIGHT, INTRO_MOUNTAIN_SILHOUETTE
)
from utils.graphics import draw_button, draw_centered_text

# Global variable to cache loaded Act II data
_act_two_data = None

def load_act_two_data():
    """Load Act II transition data from JSON file"""
    global _act_two_data
    
    if _act_two_data is not None:
        return _act_two_data
    
    try:
        act_two_file_path = os.path.join("data", "narrative", "act_two.json")
        
        if not os.path.exists(act_two_file_path):
            print(f"⚠️ Act II data file not found: {act_two_file_path}")
            return get_fallback_act_two_data()
        
        with open(act_two_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _act_two_data = data["act_two_transition"]
            print(f"✅ Loaded Act II transition data")
            return _act_two_data
            
    except Exception as e:
        print(f"❌ Error loading Act II data: {e}")
        return get_fallback_act_two_data()

def get_fallback_act_two_data():
    """Fallback Act II data if JSON file fails to load"""
    return {
        "title": "ACT TWO: THE INVESTIGATION BEGINS",
        "scenes": [
            {
                "id": "act_two_start",
                "title": "The Investigation Begins",
                "content": [
                    "FALLBACK!!! With your companions assembled and the Mayor's urgent plea echoing in your mind, you prepare to venture beyond Redstone's walls.",
                    "Three locations demand investigation: the fog-shrouded church in the southern swamps, the ancient ruins overlooking the valley, and the refugee camp where displaced miners seek shelter.",
                    "Somewhere in these troubled lands lies the answer to Redstone's darkness. The tremors grow stronger. Time is running short."
                ],
                "next_scene": "exploration_hub",
                "background_style": "town_overlook"
            }
        ],
        "ui_config": {
            "continue_button_text": "BEGIN EXPLORATION",
            "title_color": "YELLOW",
            "text_color": "WHITE"
        }
    }

class ActTwoTransitionManager:
    """
    Manages Act II transition display and navigation
    Single scene that sets act_two_started flag and transitions to exploration hub
    """
    
    def __init__(self, event_manager, game_state):
        self.event_manager = event_manager
        self.game_state = game_state
        self.act_two_data = load_act_two_data()
        self.register_events()
    
    def register_events(self):
        """Register events for Act II transition navigation"""
        self.event_manager.register("ACT_TWO_START", self.handle_act_two_start)
        self.event_manager.register("ACT_TWO_CONTINUE", self.handle_continue)
        
    def handle_act_two_start(self, event_data):
        """Handle the start of Act II transition"""
        print("🎬 Starting Act II transition...")
        
        # Set Act II started flag
        if self.game_state:
            self.game_state.act_two_started = True
            print("✅ Act II flag set")
        
        # Navigate to Act II screen
        self.event_manager.emit("SCREEN_CHANGE", {"target": "act_two_start"})
        
    def handle_continue(self, event_data):
        """Handle continuing from Act II transition to exploration hub"""
        print("🎬 Transitioning to exploration hub...")
        
        scenes = self.act_two_data.get("scenes", [])
        if scenes:
            target = scenes[0].get("next_scene", "exploration_hub")
            self.event_manager.emit("SCREEN_CHANGE", {"target": target})
        else:
            self.event_manager.emit("SCREEN_CHANGE", {"target": "exploration_hub"})
    
    def get_scene_data(self):
        """Get Act II scene data"""
        scenes = self.act_two_data.get("scenes", [])
        if scenes:
            return scenes[0]
        return None

def draw_atmospheric_background(surface, style):
    """
    Create atmospheric backgrounds using pygame primitives
    Reused from intro_scenes.py for consistency
    """
    width, height = surface.get_size()
    mountain_height = int(height * INTRO_MOUNTAIN_HEIGHT_RATIO)
    
    if style == "town_overlook":
        # Evening sky with warm tones
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            # Warm evening colors (orange to dark blue)
            r = int(70 * intensity + 10)
            g = int(50 * intensity + 10)
            b = int(90 * intensity + 30)
            sky_color = (r, g, b)
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Mountain silhouette
        for y in range(mountain_height, height):
            pygame.draw.line(surface, INTRO_MOUNTAIN_SILHOUETTE, (0, y), (width, y))
    
    elif style == "road_dusk":
        # Fallback to dusk sky
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            sky_color = tuple(int(c * intensity * 1.8) for c in INTRO_SKY_DUSK)
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        for y in range(mountain_height, height):
            pygame.draw.line(surface, INTRO_MOUNTAIN_SILHOUETTE, (0, y), (width, y))

def draw_act_two_transition_generic(surface, game_state, fonts, images, scene_id):
    """
    Generic Act II transition scene renderer
    Follows intro_scenes.py pattern for consistency
    """
    # Get Act II data
    act_two_data = load_act_two_data()
    
    if not act_two_data:
        print("❌ No Act II data available")
        return {}
    
    # Get scene data
    scenes = act_two_data.get("scenes", [])
    scene_data = None
    for scene in scenes:
        if scene["id"] == scene_id:
            scene_data = scene
            break
    
    if not scene_data:
        print(f"❌ Scene {scene_id} not found")
        return {}
    
    # UI configuration
    ui_config = act_two_data.get("ui_config", {})
    
    # Clear screen and draw atmospheric background
    surface.fill(BLACK)
    background_style = scene_data.get("background_style", "town_overlook")
    draw_atmospheric_background(surface, background_style)
    
    # Semi-transparent overlay for text readability
    overlay = pygame.Surface((1024, 768))
    overlay.set_alpha(INTRO_OVERLAY_ALPHA)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Scene title
    title_font = fonts.get('fantasy_large', fonts['header'])
    draw_centered_text(surface, scene_data["title"], title_font, INTRO_TITLE_Y, YELLOW)
    
    # Decorative line
    decoration_y = INTRO_TITLE_Y + INTRO_TITLE_DECORATION_OFFSET
    draw_centered_text(surface, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 
                      fonts.get('fantasy_medium', fonts['normal']), 
                      decoration_y, YELLOW)
    
    # Content text
    content_font = fonts.get('fantasy_medium', fonts['normal'])
    current_y = INTRO_CONTENT_START_Y
    
    from utils.constants import WHITE
    
    for paragraph in scene_data["content"]:
        # Wrap text
        wrapped_lines = wrap_text(paragraph, content_font, INTRO_CONTENT_MAX_WIDTH)
        
        for line_surface in wrapped_lines:
            # Center each line
            line_rect = line_surface.get_rect(center=(512, current_y))
            surface.blit(line_surface, line_rect)
            current_y += INTRO_CONTENT_LINE_SPACING
        
        # Add paragraph spacing
        current_y += INTRO_CONTENT_PARAGRAPH_SPACING
    
    # Continue button
    button_width, button_height = BUTTON_SIZES['large']  # (220, 70)
    button_x = (1024 - button_width) // 2
    button_y = 650  # Position near bottom

    continue_text = ui_config.get("continue_button_text", "CONTINUE")
    continue_button = draw_button(surface, button_x, button_y, 
                                button_width, button_height,
                                continue_text, fonts.get('fantasy_small', fonts['header']))
    
    # Return button coordinates for registration
    return {
        "continue_button": continue_button,
        "scene_data": scene_data
    }

def draw_act_two_start(surface, game_state, fonts, images):
    """Draw the Act II transition scene"""
    return draw_act_two_transition_generic(surface, game_state, fonts, images, "act_two_start")

def register_act_two_buttons(screen_manager):
    """Register clickable areas with screen manager"""
    # Get current screen's clickable areas
    clickable_areas = screen_manager.current_clickables
    
    if "continue_button" in clickable_areas:
        def on_continue_click():
            screen_manager.event_manager.emit("ACT_TWO_CONTINUE", {})
        
        screen_manager.register_clickable(
            "act_two_continue_button",
            clickable_areas["continue_button"],
            on_continue_click
        )

# Global manager instance
_act_two_manager = None

def get_act_two_manager(event_manager, game_state):
    """Get or create Act II manager singleton"""
    global _act_two_manager
    if _act_two_manager is None:
        _act_two_manager = ActTwoTransitionManager(event_manager, game_state)
    return _act_two_manager