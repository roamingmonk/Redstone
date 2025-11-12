# screens/act_three_transition.py
"""
Terror in Redstone - Act III Transition System
Single cinematic scene marking the transition from investigation to final assault
Follows act_two_transition.py architecture for consistency
"""

import pygame
import json
import os
from utils.constants import (
    BLACK, RED, YELLOW, BROWN, DARK_GRAY, wrap_text,
    # Intro-specific constants (reused for Act III)
    INTRO_TITLE_Y, INTRO_TITLE_DECORATION_OFFSET, INTRO_CONTENT_START_Y,
    INTRO_CONTENT_LINE_SPACING, INTRO_CONTENT_PARAGRAPH_SPACING, INTRO_CONTENT_MAX_WIDTH,
    INTRO_BUTTON_Y, INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT, INTRO_BUTTON_SPACING,
    INTRO_OVERLAY_ALPHA, INTRO_MOUNTAIN_HEIGHT_RATIO, BUTTON_SIZES,
    INTRO_SKY_DUSK, INTRO_SKY_NIGHT, INTRO_MOUNTAIN_SILHOUETTE
)
from utils.graphics import draw_button, draw_centered_text

# Global variable to cache loaded Act III data
_act_three_data = None

def load_act_three_data():
    """Load Act III transition data from JSON file"""
    global _act_three_data
    
    if _act_three_data is not None:
        return _act_three_data
    
    try:
        act_three_file_path = os.path.join("data", "narrative", "act_three.json")
        
        if not os.path.exists(act_three_file_path):
            print(f"⚠️ Act III data file not found: {act_three_file_path}")
            return get_fallback_act_three_data()
        
        with open(act_three_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _act_three_data = data["act_three_transition"]
            print(f"✅ Loaded Act III transition data")
            return _act_three_data
            
    except Exception as e:
        print(f"❌ Error loading Act III data: {e}")
        return get_fallback_act_three_data()

def get_fallback_act_three_data():
    """Fallback Act III data if JSON file fails to load"""
    return {
        "title": "ACT THREE: THE FINAL ASSAULT",
        "scenes": [
            {
                "id": "act_three_start",
                "title": "The Final Hour",
                "content": [
                    "The investigation is complete. The truth is clear.",
                    "A cult. A portal. Human sacrifices to tear open the barrier between worlds.",
                    "Deep beneath the Hill Ruins, the ritual nears completion.",
                    "This ends now. One way or another.",
                    "Gather your strength. Check your gear. Say your farewells."
                ],
                "next_scene": "redstone_town",
                "background_style": "ominous_sky"
            }
        ],
        "ui_config": {
            "continue_button_text": "FINAL PREPARATIONS",
            "title_color": "RED",
            "text_color": "WHITE"
        }
    }

class ActThreeTransitionManager:
    """
    Manages Act III transition display and navigation
    Single scene that sets act_three_started flag and returns to town for prep
    """
    
    def __init__(self, event_manager, game_state):
        self.event_manager = event_manager
        self.game_state = game_state
        self.act_three_data = load_act_three_data()
        self.register_events()
    
    def register_events(self):
        """Register events for Act III transition navigation"""
        self.event_manager.register("ACT_THREE_START", self.handle_act_three_start)
        self.event_manager.register("ACT_THREE_CONTINUE", self.handle_continue)
        
    def handle_act_three_start(self, event_data):
        """Handle the start of Act III transition"""
        print("🎬 Starting Act III transition...")
        
        # Navigate to Act III screen
        self.event_manager.emit("SCREEN_CHANGE", {"target": "act_three_start"})
        
    def handle_continue(self, event_data):
        """Handle continuing from Act III transition to town prep phase"""
        print("🎬 Transitioning to final preparations...")
        
        # Set flags for act progression
        if self.game_state:
            self.game_state.act_two_complete = True
            self.game_state.act_three_started = True
            self.game_state.act_three_ready = True
            print("✅ Act II complete, Act III started")
        
        scenes = self.act_three_data.get("scenes", [])
        if scenes:
            target = scenes[0].get("next_scene", "redstone_town")
            self.event_manager.emit("SCREEN_CHANGE", {"target": target})
        else:
            self.event_manager.emit("SCREEN_CHANGE", {"target": "redstone_town"})
    
    def get_scene_data(self):
        """Get Act III scene data"""
        scenes = self.act_three_data.get("scenes", [])
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
    
    if style == "ominous_sky":
        # Dark, foreboding sky with red tones
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            # Ominous red-tinted dark sky
            r = int(60 * intensity + 20)
            g = int(10 * intensity + 5)
            b = int(20 * intensity + 10)
            sky_color = (r, g, b)
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Mountain silhouette (darker)
        for y in range(mountain_height, height):
            pygame.draw.line(surface, (10, 10, 15), (0, y), (width, y))
    
    elif style == "town_overlook":
        # Evening sky with warm tones (fallback)
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            r = int(70 * intensity + 10)
            g = int(50 * intensity + 10)
            b = int(90 * intensity + 30)
            sky_color = (r, g, b)
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        for y in range(mountain_height, height):
            pygame.draw.line(surface, INTRO_MOUNTAIN_SILHOUETTE, (0, y), (width, y))

def draw_act_three_transition_generic(surface, game_state, fonts, images, scene_id):
    """
    Generic Act III transition scene renderer
    Follows intro_scenes.py pattern for consistency
    """
    # Get Act III data
    act_three_data = load_act_three_data()
    
    if not act_three_data:
        print("❌ No Act III data available")
        return {}
    
    # Get scene data
    scenes = act_three_data.get("scenes", [])
    scene_data = None
    for scene in scenes:
        if scene["id"] == scene_id:
            scene_data = scene
            break
    
    if not scene_data:
        print(f"❌ Scene {scene_id} not found")
        return {}
    
    # UI configuration
    ui_config = act_three_data.get("ui_config", {})
    
    # Clear screen and draw atmospheric background
    surface.fill(BLACK)
    background_style = scene_data.get("background_style", "ominous_sky")
    draw_atmospheric_background(surface, background_style)
    
    # Semi-transparent overlay for text readability
    overlay = pygame.Surface((1024, 768))
    overlay.set_alpha(INTRO_OVERLAY_ALPHA)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Scene title (RED for Act III)
    title_font = fonts.get('fantasy_large', fonts['header'])
    draw_centered_text(surface, scene_data["title"], title_font, INTRO_TITLE_Y, RED)
    
    # Decorative line (RED for Act III)
    decoration_y = INTRO_TITLE_Y + INTRO_TITLE_DECORATION_OFFSET
    draw_centered_text(surface, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 
                      fonts.get('fantasy_medium', fonts['normal']), 
                      decoration_y, RED)
    
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
    button_y = 690  # Position near bottom

    continue_text = ui_config.get("continue_button_text", "CONTINUE")
    continue_button = draw_button(surface, button_x, button_y, 
                                button_width, button_height,
                                continue_text, fonts.get('fantasy_small', fonts['header']))
    
    # Return button coordinates for registration
    return {
        "continue_button": continue_button,
        "scene_data": scene_data
    }

def draw_act_three_start(surface, game_state, fonts, images):
    """Draw the Act III transition scene"""
    return draw_act_three_transition_generic(surface, game_state, fonts, images, "act_three_start")

def register_act_three_buttons(screen_manager):
    """Register clickable areas with screen manager"""
    # Get current screen's clickable areas
    clickable_areas = screen_manager.current_clickables
    
    if "continue_button" in clickable_areas:
        def on_continue_click():
            screen_manager.event_manager.emit("ACT_THREE_CONTINUE", {})
        
        screen_manager.register_clickable(
            "act_three_continue_button",
            clickable_areas["continue_button"],
            on_continue_click
        )

# Global manager instance
_act_three_manager = None

def get_act_three_manager(event_manager, game_state):
    """Get or create Act III manager singleton"""
    global _act_three_manager
    if _act_three_manager is None:
        _act_three_manager = ActThreeTransitionManager(event_manager, game_state)
    return _act_three_manager