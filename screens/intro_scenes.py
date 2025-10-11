# screens/intro_scenes.py
"""
Terror in Redstone - Intro Sequence System
Professional narrative scene management using hybrid cinematic approach
Follows established architectural patterns with full-screen cinematic layout
"""

import pygame
import json
import os
from utils.constants import (
    BLACK, WHITE, YELLOW, BROWN, DARK_GRAY, wrap_text,
    # Intro-specific constants
    INTRO_TITLE_Y, INTRO_TITLE_DECORATION_OFFSET, INTRO_CONTENT_START_Y,
    INTRO_CONTENT_LINE_SPACING, INTRO_CONTENT_PARAGRAPH_SPACING, INTRO_CONTENT_MAX_WIDTH,
    INTRO_BUTTON_Y, INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT, INTRO_BUTTON_SPACING,
    INTRO_OVERLAY_ALPHA, INTRO_MOUNTAIN_HEIGHT_RATIO, INTRO_TOWN_Y_OFFSET,
    INTRO_SKY_DUSK, INTRO_SKY_NIGHT, INTRO_MOUNTAIN_SILHOUETTE, 
    INTRO_BUILDING_SILHOUETTE, INTRO_WARM_LIGHT, INTRO_DISTANT_LIGHT
)
from utils.graphics import draw_button, draw_centered_text

# Global variable to cache loaded intro data
_intro_data = None

def load_intro_sequence_data():
    """Load intro sequence data from JSON file"""
    global _intro_data
    
    if _intro_data is not None:
        return _intro_data
    
    try:
        intro_file_path = os.path.join("data", "narrative", "intro_sequence.json")
        
        if not os.path.exists(intro_file_path):
            print(f"⚠️ Intro sequence file not found: {intro_file_path}")
            return get_fallback_intro_data()
        
        with open(intro_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _intro_data = data["intro_sequence"]
            print(f"✅ Loaded intro sequence: {len(_intro_data['scenes'])} scenes")
            return _intro_data
            
    except Exception as e:
        print(f"❌ Error loading intro sequence: {e}")
        return get_fallback_intro_data()

def get_fallback_intro_data():
    """Fallback intro data if JSON file fails to load"""
    return {
        "title": "Terror in Redstone - Prologue",
        "scenes": [
            {
                "id": "intro_scene_1",
                "title": "The Road to Redstone",
                "content": [
                    "The dusty trail stretches before you as you approach the mining town of Redstone. Tales of strange happenings and missing miners have reached even the distant cities, and local authorities are offering good coin for brave souls willing to investigate the growing darkness."
                ],
                "next_scene": "intro_scene_2",
                "background_style": "road_dusk"
            },
            {
                "id": "intro_scene_2", 
                "title": "Whispers in the Wind",
                "content": [
                    "As you crest the final hill, Redstone comes into view. The town seems quiet - too quiet for a place that should be bustling with mining activity. Smoke rises from only a few chimneys, and you notice several boarded-up buildings. Whatever troubles this place runs deeper than simple bandit raids."
                ],
                "next_scene": "intro_scene_3",
                "background_style": "town_overlook"
            },
            {
                "id": "intro_scene_3",
                "title": "The Broken Blade Beckons", 
                "content": [
                    "You guide your horse down the main street, noting the nervous glances of the few townspeople you see. At the town's center stands The Broken Blade tavern, its warm light a welcome beacon in the growing dusk. Perhaps the locals there will have answers... and maybe you'll find allies for whatever lies ahead."
                ],
                "next_scene": "broken_blade",
                "background_style": "tavern_approach"
            }
        ],
        "ui_config": {
            "continue_button_text": "CONTINUE",
            "skip_button_text": "SKIP INTRO",
            "title_color": "YELLOW",
            "text_color": "WHITE", 
            "background_color": "BLACK"
        }
    }

class IntroSequenceManager:
    """
    Professional scene sequence management with auto-save checkpoint
    Handles navigation between intro scenes and transition to main game
    """
    
    def __init__(self, event_manager, save_manager=None):
        self.event_manager = event_manager
        self.save_manager = save_manager
        self.current_scene_index = 0
        self.intro_data = load_intro_sequence_data()
        self.intro_started = False
        self.register_events()
    
    def register_events(self):
        """Register events for intro sequence navigation"""
        self.event_manager.register("INTRO_START", self.handle_intro_start)
        self.event_manager.register("INTRO_NEXT", self.handle_next_scene)
        self.event_manager.register("INTRO_SKIP", self.handle_skip_intro)
        
    def handle_intro_start(self, event_data):
        """Handle the start of intro sequence"""
        if not self.intro_started:
            self.intro_started = True
            print("🎬 Starting intro sequence...")
            
            # Start first scene (removed auto-save from here)
            self.current_scene_index = 0
            first_scene_id = self.intro_data["scenes"][0]["id"]
            self.event_manager.emit("SCREEN_CHANGE", {"target": first_scene_id})
        
    def handle_next_scene(self, event_data):
        """Handle advancing to next scene in sequence"""
        scenes = self.intro_data["scenes"]
        
        if self.current_scene_index < len(scenes) - 1:
            self.current_scene_index += 1
            next_scene_id = scenes[self.current_scene_index]["id"]
            print(f"🎬 Advancing to intro scene: {next_scene_id}")
            self.event_manager.emit("SCREEN_CHANGE", {"target": next_scene_id})
        else:
            # End of intro sequence - go to main game
            self.complete_intro_sequence()
    
    def handle_skip_intro(self, event_data):
        """Handle skipping intro sequence entirely"""
        print("⏭️ Skipping intro sequence")
        self.complete_intro_sequence()
    
    def complete_intro_sequence(self):
        """Complete intro and transition to main game with auto-save checkpoint"""
        print("✨ Intro sequence complete - transitioning to main game")
        
        # Get the final scene's next_scene target
        scenes = self.intro_data["scenes"]
        if scenes:
            final_scene = scenes[-1]
            target = final_scene.get("next_scene", "broken_blade")
            
            # Transition to main game FIRST
            self.event_manager.emit("SCREEN_CHANGE", {"target": target})
            
            # THEN create auto-save checkpoint after screen transition
            if self.save_manager:
                try:
                    success = self.save_manager.save_game(0)
                    if success:
                        print("💾 Auto-save checkpoint created after intro completion")
                    else:
                        print("⚠️ Auto-save failed, but continuing to game")
                except Exception as e:
                    print(f"⚠️ Auto-save error: {e}, but continuing to game")
        else:
            self.event_manager.emit("SCREEN_CHANGE", {"target": "broken_blade"})
    
    def get_current_scene_data(self):
        """Get data for currently active intro scene"""
        scenes = self.intro_data["scenes"]
        if 0 <= self.current_scene_index < len(scenes):
            return scenes[self.current_scene_index]
        return None
    
    def reset_sequence(self):
        """Reset intro sequence to beginning"""
        self.current_scene_index = 0
        self.intro_started = False

def draw_atmospheric_background(surface, style):
    """
    Create atmospheric backgrounds using pygame primitives and established constants
    Professional cinematic backgrounds without requiring external image files
    """
    width, height = surface.get_size()
    mountain_height = int(height * INTRO_MOUNTAIN_HEIGHT_RATIO)
    
    if style == "road_dusk":
        # Gradient sky from dark blue to black using established color constants
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            sky_color = tuple(int(c * intensity * 1.8) for c in INTRO_SKY_DUSK)
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Mountain silhouettes using constants
        mountain_points = [
            (0, mountain_height), (150, mountain_height - 100), (300, mountain_height - 50),
            (500, mountain_height - 130), (700, mountain_height - 80), (900, mountain_height - 110),
            (width, mountain_height), (width, height), (0, height)
        ]
        pygame.draw.polygon(surface, INTRO_MOUNTAIN_SILHOUETTE, mountain_points)
        
        # Distant town lights using established light colors
        lights = [(200, mountain_height + 60), (250, mountain_height + 45), (190, mountain_height + 70),
                 (280, mountain_height + 55), (230, mountain_height + 80)]
        for light_x, light_y in lights:
            pygame.draw.circle(surface, YELLOW, (light_x, light_y), 2)
            pygame.draw.circle(surface, INTRO_DISTANT_LIGHT, (light_x, light_y), 4, 1)
        
    elif style == "town_overlook":
        # Darker, more ominous gradient using night colors
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            sky_color = tuple(int(c * intensity * 1.2) for c in INTRO_SKY_NIGHT)
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Town silhouette using established building ratios
        building_heights = [40, 60, 35, 80, 50, 45, 70, 55, 40, 65]
        building_width = width // len(building_heights)
        town_y = mountain_height + INTRO_TOWN_Y_OFFSET
        
        for i, building_height in enumerate(building_heights):
            x = i * building_width
            building_rect = pygame.Rect(x, town_y - building_height, building_width - 2, building_height)
            pygame.draw.rect(surface, INTRO_BUILDING_SILHOUETTE, building_rect)
            
            # Occasional lit windows using warm light constant
            if i % 3 == 0:
                window_x = x + building_width // 3
                window_y = town_y - building_height + 10
                pygame.draw.rect(surface, INTRO_WARM_LIGHT, (window_x, window_y, 6, 8))
        
        # Church spire in distance
        spire_x = width - 200
        spire_points = [(spire_x, town_y), (spire_x + 15, town_y - 90), (spire_x + 30, town_y)]
        pygame.draw.polygon(surface, INTRO_MOUNTAIN_SILHOUETTE, spire_points)
        
    elif style == "tavern_approach":
        # Warmer but still moody using dusk colors
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            # Slightly warmer gradient for tavern approach
            sky_color = (
                int(INTRO_SKY_DUSK[0] * intensity * 0.8),
                int(INTRO_SKY_DUSK[1] * intensity * 0.6),
                int(INTRO_SKY_DUSK[2] * intensity * 0.5)
            )
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Tavern building silhouette (larger, more prominent)
        tavern_x = width // 2 - 150
        tavern_y = mountain_height + 50
        
        # Main building using established silhouette color
        pygame.draw.rect(surface, INTRO_BUILDING_SILHOUETTE, (tavern_x, tavern_y, 300, 120))
        
        # Warm light from windows using established warm light
        windows = [(tavern_x + 50, tavern_y + 30), (tavern_x + 150, tavern_y + 30), 
                  (tavern_x + 250, tavern_y + 30)]
        for win_x, win_y in windows:
            pygame.draw.rect(surface, INTRO_WARM_LIGHT, (win_x, win_y, 20, 25))
            # Window glow effect
            pygame.draw.rect(surface, INTRO_DISTANT_LIGHT, (win_x - 2, win_y - 2, 24, 29), 2)
        
        # Door with light spilling out
        door_x = tavern_x + 125
        pygame.draw.rect(surface, (255, 150, 50), (door_x, tavern_y + 70, 15, 50))
        
        # Sign post using brown constant
        pygame.draw.line(surface, BROWN, (tavern_x - 30, tavern_y), (tavern_x - 30, tavern_y + 60), 3)
        pygame.draw.rect(surface, INTRO_BUILDING_SILHOUETTE, (tavern_x - 60, tavern_y + 20, 60, 20))

def draw_intro_scene_generic(surface, game_state, fonts, images, scene_id):
            """
            Cinematic intro scene renderer using established architectural patterns
            Full-screen layout with professional text handling via your utilities
            """
            # Load intro data and find specific scene
            intro_data = load_intro_sequence_data()
            scene_data = None
            
            for scene in intro_data["scenes"]:
                if scene["id"] == scene_id:
                    scene_data = scene
                    break
            
            if not scene_data:
                print(f"❌ Error: Scene data not found for {scene_id}")
                return None
            
            # Get UI configuration
            ui_config = intro_data.get("ui_config", {})
            
            # Clear screen and draw atmospheric background
            surface.fill(BLACK)
            background_style = scene_data.get("background_style", "road_dusk")
            draw_atmospheric_background(surface, background_style)
            
            # Semi-transparent overlay for text readability using established constant
            overlay = pygame.Surface((1024, 768))
            overlay.set_alpha(INTRO_OVERLAY_ALPHA)
            overlay.fill(BLACK)
            surface.blit(overlay, (0, 0))
            
            # Scene title using your established drawing function and constants
            title_font = fonts.get('fantasy_large', fonts['header'])
            draw_centered_text(surface, scene_data["title"], title_font, INTRO_TITLE_Y, YELLOW)
            
            # Decorative line using your patterns and constants
            decoration_y = INTRO_TITLE_Y + INTRO_TITLE_DECORATION_OFFSET
            draw_centered_text(surface, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 
                            fonts.get('fantasy_medium', fonts['normal']), 
                            decoration_y, YELLOW)
            
            # Character name integration using game_state (following your patterns)
            character_name = None
            if game_state and hasattr(game_state, 'character'):
                character_name = game_state.character.get('name', None)
            
            # Content text using your wrap_text utility and established constants
            content_font = fonts.get('fantasy_medium', fonts['normal'])
            current_y = INTRO_CONTENT_START_Y
            
            for paragraph in scene_data["content"]:
                # Insert character name naturally (first paragraph only)
                if character_name and paragraph == scene_data["content"][0]:
                    if paragraph.startswith("You have"):
                        paragraph = f"As {character_name}, you have" + paragraph[8:]
                    elif paragraph.startswith("You "):
                        paragraph = f"As {character_name}, you " + paragraph[4:]
                
                # Use your established wrap_text utility
                wrapped_lines = wrap_text(paragraph, content_font, INTRO_CONTENT_MAX_WIDTH)
                
                for line_surface in wrapped_lines:
                    # Center each line using established screen width
                    line_rect = line_surface.get_rect(center=(512, current_y))
                    surface.blit(line_surface, line_rect)
                    current_y += INTRO_CONTENT_LINE_SPACING
                
                # Add paragraph spacing using established constant
                current_y += INTRO_CONTENT_PARAGRAPH_SPACING
            
            # Navigation buttons using your draw_button function and constants
            total_button_width = (2 * INTRO_BUTTON_WIDTH) + INTRO_BUTTON_SPACING
            start_x = (1024 - total_button_width) // 2
            
            # CONTINUE button
            continue_text = ui_config.get("continue_button_text", "CONTINUE")
            continue_button = draw_button(surface, start_x, INTRO_BUTTON_Y, 
                                        INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
                                        continue_text, fonts.get('fantasy_medium', fonts['normal']))
            
            # SKIP button
            skip_x = start_x + INTRO_BUTTON_WIDTH + INTRO_BUTTON_SPACING
            skip_text = ui_config.get("skip_button_text", "SKIP INTRO")
            skip_button = draw_button(surface, skip_x, INTRO_BUTTON_Y, 
                                    INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
                                    skip_text, fonts.get('fantasy_medium', fonts['normal']))
            
            # Return button coordinates for registration (following your established pattern)
            return {
                "continue_button": continue_button,
                "skip_button": skip_button,
                "scene_data": scene_data
            }

        # Individual scene drawing functions following your established pattern

def draw_intro_scene_1(surface, game_state, fonts, images):
    """Draw the first intro scene"""
    return draw_intro_scene_generic(surface, game_state, fonts, images, "intro_scene_1")

def draw_intro_scene_2(surface, game_state, fonts, images):
    """Draw the second intro scene"""
    return draw_intro_scene_generic(surface, game_state, fonts, images, "intro_scene_2")

def draw_intro_scene_3(surface, game_state, fonts, images):
    """Draw the third intro scene"""
    return draw_intro_scene_generic(surface, game_state, fonts, images, "intro_scene_3")


