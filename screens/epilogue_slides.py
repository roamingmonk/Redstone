# # screens/epilogue_slides.py
# """
# Terror in Redstone - Epilogue Sequence System
# Professional narrative conclusion with conditional story variations
# Mirrors intro_scenes.py architecture for consistency
# """

# import pygame
# import json
# import os
# from utils.constants import (
#     BLACK, YELLOW, WHITE, wrap_text,
#     # Reuse intro constants for consistency
#     INTRO_TITLE_Y, INTRO_TITLE_DECORATION_OFFSET, INTRO_CONTENT_START_Y,
#     INTRO_CONTENT_LINE_SPACING, INTRO_CONTENT_PARAGRAPH_SPACING, INTRO_CONTENT_MAX_WIDTH,
#     INTRO_BUTTON_Y, INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT, INTRO_BUTTON_SPACING,
#     INTRO_OVERLAY_ALPHA, INTRO_MOUNTAIN_HEIGHT_RATIO, INTRO_TOWN_Y_OFFSET,
#     INTRO_SKY_DUSK, INTRO_SKY_NIGHT, INTRO_MOUNTAIN_SILHOUETTE, 
#     INTRO_BUILDING_SILHOUETTE, INTRO_WARM_LIGHT, INTRO_DISTANT_LIGHT
# )
# from utils.graphics import draw_button, draw_centered_text

# # Global variable to cache loaded epilogue data
# _epilogue_data = None

# def load_epilogue_sequence_data():
#     """Load epilogue sequence data from JSON file"""
#     global _epilogue_data
    
#     if _epilogue_data is not None:
#         return _epilogue_data
    
#     try:
#         epilogue_file_path = os.path.join("data", "narrative", "epilogue_sequence.json")
        
#         if not os.path.exists(epilogue_file_path):
#             print(f"⚠️ Epilogue sequence file not found: {epilogue_file_path}")
#             return get_fallback_epilogue_data()
        
#         with open(epilogue_file_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#             _epilogue_data = data["epilogue_sequence"]
#             print(f"✅ Loaded epilogue sequence: {len(_epilogue_data['slides'])} slides")
#             return _epilogue_data
            
#     except Exception as e:
#         print(f"❌ Error loading epilogue sequence: {e}")
#         return get_fallback_epilogue_data()

# def get_fallback_epilogue_data():
#     """Fallback epilogue data if JSON file fails to load"""
#     return {
#         "title": "Terror in Redstone - Epilogue",
#         "slides": [
#             {
#                 "id": "epilogue_victory",
#                 "title": "VICTORY",
#                 "content": [
#                     "The Shadow Blight has been sealed.",
#                     "",
#                     "Redstone is saved.",
#                     "",
#                     "But the cost of victory varies with each hero's choices..."
#                 ],
#                 "next_slide": "epilogue_end",
#                 "background_style": "dawn_sky"
#             },
#             {
#                 "id": "epilogue_end",
#                 "title": "THE END",
#                 "content": [
#                     "Thank you for playing Terror in Redstone!",
#                     "",
#                     "Your adventure has concluded."
#                 ],
#                 "next_slide": "credits",
#                 "background_style": "town_square"
#             }
#         ],
#         "ui_config": {
#             "continue_button_text": "CONTINUE",
#             "skip_button_text": "SKIP TO CREDITS",
#             "title_color": "YELLOW",
#             "text_color": "WHITE", 
#             "background_color": "BLACK"
#         }
#     }

# class EpilogueSequenceManager:
#     """
#     Manages epilogue slide sequence with conditional content resolution
#     Handles navigation between slides and transition to credits
#     """
    
#     def __init__(self, event_manager, game_state):
#         self.event_manager = event_manager
#         self.game_state = game_state
#         self.current_slide_index = 0
#         self.epilogue_data = load_epilogue_sequence_data()
#         self.epilogue_started = False
#         self.register_events()
    
#     def register_events(self):
#         """Register events for epilogue sequence navigation"""
#         self.event_manager.register("EPILOGUE_START", self.handle_epilogue_start)
#         self.event_manager.register("EPILOGUE_NEXT", self.handle_next_slide)
#         self.event_manager.register("EPILOGUE_SKIP", self.handle_skip_epilogue)
        
#     def handle_epilogue_start(self, event_data):
#         """Handle the start of epilogue sequence"""
#         if not self.epilogue_started:
#             self.epilogue_started = True
#             print("🎬 Starting epilogue sequence...")
            
#             # Start first slide
#             self.current_slide_index = 0
#             first_slide_id = self.epilogue_data["slides"][0]["id"]
#             self.event_manager.emit("SCREEN_CHANGE", {"target": first_slide_id})
        
#     def handle_next_slide(self, event_data):
#         """Handle advancing to next slide in sequence"""
#         slides = self.epilogue_data["slides"]
        
#         if self.current_slide_index < len(slides) - 1:
#             self.current_slide_index += 1
#             next_slide_id = slides[self.current_slide_index]["id"]
#             print(f"🎬 Advancing to epilogue slide: {next_slide_id}")
#             self.event_manager.emit("SCREEN_CHANGE", {"target": next_slide_id})
#         else:
#             # End of epilogue sequence - go to credits
#             self.complete_epilogue_sequence()
    
#     def handle_skip_epilogue(self, event_data):
#         """Handle skipping epilogue sequence entirely"""
#         print("⏭️ Skipping epilogue sequence")
#         self.complete_epilogue_sequence()
    
#     def complete_epilogue_sequence(self):
#         """Complete epilogue and transition to credits"""
#         print("✨ Epilogue sequence complete - transitioning to credits")
        
#         # Get the final slide's next_slide target
#         slides = self.epilogue_data["slides"]
#         if slides:
#             final_slide = slides[-1]
#             target = final_slide.get("next_slide", "credits")
#             self.event_manager.emit("SCREEN_CHANGE", {"target": target})
#         else:
#             self.event_manager.emit("SCREEN_CHANGE", {"target": "credits"})
    
#     def get_current_slide_data(self):
#         """Get data for currently active epilogue slide with conditional content resolved"""
#         slides = self.epilogue_data["slides"]
#         if 0 <= self.current_slide_index < len(slides):
#             slide_data = slides[self.current_slide_index]
#             # Resolve conditional content based on game state
#             return self.resolve_conditional_content(slide_data)
#         return None
    
#     def resolve_conditional_content(self, slide_data):
#         """
#         Check game state conditions and return appropriate content variant
#         This is where we customize slides based on player choices!
#         """
#         # If no variations, return slide as-is
#         if "variations" not in slide_data:
#             return slide_data
        
#         # Check each variation's condition
#         for variant in slide_data["variations"]:
#             condition = variant.get("condition")
#             if self.check_condition(condition):
#                 # Found matching condition - merge with base slide
#                 resolved_slide = slide_data.copy()
#                 resolved_slide["content"] = variant["content"]
#                 if "title" in variant:
#                     resolved_slide["title"] = variant["title"]
#                 return resolved_slide
        
#         # No matching condition - return base slide with default content
#         return slide_data
    
#     def check_condition(self, condition_string):
#         """
#         Evaluate condition against game state
        
#         Examples:
#           "mayor_family_status == 'all_saved'"
#           "marcus_outcome == 'fled'"
#           "has_item:portal_seal_fragment"
#           "player_species == 'Cavia'"
#         """
#         if not condition_string or condition_string == "default":
#             return True  # Default condition always matches
        
#         try:
#             # Check for item possession
#             if condition_string.startswith("has_item:"):
#                 item_id = condition_string.split(":")[1]
#                 return self.player_has_item(item_id)
            
#             # Check for flag existence
#             elif condition_string.startswith("has_flag:"):
#                 flag_name = condition_string.split(":")[1]
#                 return getattr(self.game_state, flag_name, False)
            
#             # Evaluate complex condition (be careful with eval!)
#             else:
#                 # Build safe namespace for evaluation
#                 safe_globals = {"__builtins__": {}}
#                 safe_locals = {"game_state": self.game_state}
#                 return eval(condition_string, safe_globals, safe_locals)
                
#         except Exception as e:
#             print(f"⚠️ Condition evaluation error: {condition_string} - {e}")
#             return False
    
#     def player_has_item(self, item_id):
#         """Check if player has a specific item"""
#         if not self.game_state or not hasattr(self.game_state, 'inventory'):
#             return False
        
#         # Check inventory for item
#         for item in self.game_state.inventory:
#             if item.get('id') == item_id:
#                 return True
#         return False
    
#     def reset_sequence(self):
#         """Reset epilogue sequence to beginning"""
#         self.current_slide_index = 0
#         self.epilogue_started = False

# def draw_epilogue_background(surface, style):
#     """
#     Create atmospheric backgrounds for epilogue slides
#     Reuses intro background styles + adds new epilogue-specific ones
#     """
#     width, height = surface.get_size()
#     mountain_height = int(height * INTRO_MOUNTAIN_HEIGHT_RATIO)
    
#     if style == "dawn_sky":
#         # Hopeful dawn gradient (brighter than intro)
#         for y in range(height):
#             intensity = 1 - (y / height)
#             # Warm golden dawn colors
#             sky_color = (
#                 int(30 + intensity * 120),   # Red
#                 int(20 + intensity * 100),   # Green
#                 int(50 + intensity * 80)     # Blue
#             )
#             pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
#         # Sun rising on horizon
#         sun_x, sun_y = width - 200, mountain_height - 50
#         pygame.draw.circle(surface, (255, 220, 100), (sun_x, sun_y), 40)
#         pygame.draw.circle(surface, (255, 200, 50), (sun_x, sun_y), 35)
        
#     elif style == "town_square":
#         # Daytime town square (more hopeful)
#         # Blue sky gradient
#         for y in range(mountain_height):
#             intensity = 1 - (y / mountain_height)
#             sky_color = (
#                 int(100 + intensity * 50),
#                 int(150 + intensity * 80),
#                 int(200 + intensity * 55)
#             )
#             pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
#         # Town buildings (same as intro but with day lighting)
#         building_heights = [50, 70, 40, 90, 60, 50, 80, 65, 45, 75]
#         building_width = width // len(building_heights)
#         town_y = mountain_height + INTRO_TOWN_Y_OFFSET
        
#         for i, building_height in enumerate(building_heights):
#             x = i * building_width
#             building_rect = pygame.Rect(x, town_y - building_height, building_width - 2, building_height)
#             # Lighter building color for daytime
#             pygame.draw.rect(surface, (80, 70, 60), building_rect)
#             pygame.draw.rect(surface, (60, 50, 40), building_rect, 2)
            
#     elif style == "violet_mortar_shop":
#         # Purple-tinted background for Cassia's shop
#         for y in range(height):
#             intensity = 1 - (y / height)
#             sky_color = (
#                 int(60 + intensity * 60),    # Red
#                 int(40 + intensity * 40),    # Green
#                 int(80 + intensity * 100)    # Blue (purple tint)
#             )
#             pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
#         # Simple shop silhouette
#         shop_x, shop_y = width // 2 - 100, mountain_height + 80
#         pygame.draw.rect(surface, (100, 60, 120), (shop_x, shop_y, 200, 100))
        
#     elif style == "marsh_sunset":
#         # Swamp healing - orange/pink sunset
#         for y in range(height):
#             intensity = 1 - (y / height)
#             sky_color = (
#                 int(100 + intensity * 120),  # Warm orange
#                 int(50 + intensity * 80),
#                 int(80 + intensity * 50)
#             )
#             pygame.draw.line(surface, sky_color, (0, y), (width, y))
            
#     elif style == "ancient_scroll":
#         # Mysterious parchment background for sequel hook
#         for y in range(height):
#             intensity = 1 - (y / height)
#             # Aged parchment color
#             sky_color = (
#                 int(180 + intensity * 40),
#                 int(160 + intensity * 40),
#                 int(120 + intensity * 30)
#             )
#             pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
#         # Ancient runes around border
#         rune_color = (80, 60, 40)
#         for x in range(0, width, 100):
#             pygame.draw.circle(surface, rune_color, (x, 50), 3)
#             pygame.draw.circle(surface, rune_color, (x, height - 50), 3)
            
#     else:
#         # Default: reuse road_dusk from intro
#         for y in range(mountain_height):
#             intensity = 1 - (y / mountain_height)
#             sky_color = tuple(int(c * intensity * 1.8) for c in INTRO_SKY_DUSK)
#             pygame.draw.line(surface, sky_color, (0, y), (width, y))

# def draw_epilogue_slide_generic(surface, game_state, fonts, images, slide_id, epilogue_manager):
#     """
#     Cinematic epilogue slide renderer using established architectural patterns
#     Full-screen layout with conditional content based on game state
#     """
#     # Get current slide data from manager (already has conditions resolved!)
#     slide_data = epilogue_manager.get_current_slide_data()
    
#     if not slide_data:
#         print(f"❌ Error: Slide data not found for {slide_id}")
#         return None
    
#     # Get UI configuration
#     ui_config = epilogue_manager.epilogue_data.get("ui_config", {})
    
#     # Clear screen and draw atmospheric background
#     surface.fill(BLACK)
#     background_style = slide_data.get("background_style", "dawn_sky")
#     draw_epilogue_background(surface, background_style)
    
#     # Semi-transparent overlay for text readability
#     overlay = pygame.Surface((1024, 768))
#     overlay.set_alpha(INTRO_OVERLAY_ALPHA)
#     overlay.fill(BLACK)
#     surface.blit(overlay, (0, 0))
    
#     # Slide title
#     title_font = fonts.get('fantasy_large', fonts['header'])
#     draw_centered_text(surface, slide_data["title"], title_font, INTRO_TITLE_Y, YELLOW)
    
#     # Decorative line
#     decoration_y = INTRO_TITLE_Y + INTRO_TITLE_DECORATION_OFFSET
#     draw_centered_text(surface, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 
#                     fonts.get('fantasy_medium', fonts['normal']), 
#                     decoration_y, YELLOW)
    
#     # Content text
#     content_font = fonts.get('fantasy_medium', fonts['normal'])
#     current_y = INTRO_CONTENT_START_Y
    
#     for paragraph in slide_data["content"]:
#         # Wrap text
#         wrapped_lines = wrap_text(paragraph, content_font, INTRO_CONTENT_MAX_WIDTH)
        
#         for line_surface in wrapped_lines:
#             # Center each line
#             line_rect = line_surface.get_rect(center=(512, current_y))
#             surface.blit(line_surface, line_rect)
#             current_y += INTRO_CONTENT_LINE_SPACING
        
#         # Add paragraph spacing
#         current_y += INTRO_CONTENT_PARAGRAPH_SPACING
    
#     # Navigation buttons
#     total_button_width = (2 * INTRO_BUTTON_WIDTH) + INTRO_BUTTON_SPACING
#     start_x = (1024 - total_button_width) // 2
    
#     # CONTINUE button
#     continue_text = ui_config.get("continue_button_text", "CONTINUE")
#     continue_button = draw_button(surface, start_x, INTRO_BUTTON_Y, 
#                                 INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
#                                 continue_text, fonts.get('fantasy_medium', fonts['normal']))
    
#     # SKIP button
#     skip_x = start_x + INTRO_BUTTON_WIDTH + INTRO_BUTTON_SPACING
#     skip_text = ui_config.get("skip_button_text", "SKIP TO CREDITS")
#     skip_button = draw_button(surface, skip_x, INTRO_BUTTON_Y, 
#                             INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
#                             skip_text, fonts.get('fantasy_medium', fonts['normal']))
    
#     # Return button coordinates for registration
#     return {
#         "continue_button": continue_button,
#         "skip_button": skip_button,
#         "slide_data": slide_data
#     }

# # Individual slide drawing functions
# def draw_epilogue_slide_1(surface, game_state, fonts, images, epilogue_manager):
#     """Draw the first epilogue slide"""
#     return draw_epilogue_slide_generic(surface, game_state, fonts, images, 
#                                       "epilogue_victory", epilogue_manager)

# def draw_epilogue_slide_2(surface, game_state, fonts, images, epilogue_manager):
#     """Draw the second epilogue slide"""
#     slides = epilogue_manager.epilogue_data["slides"]
#     slide_id = slides[1]["id"] if len(slides) > 1 else "epilogue_slide_2"
#     return draw_epilogue_slide_generic(surface, game_state, fonts, images, 
#                                       slide_id, epilogue_manager)

# def draw_epilogue_slide_3(surface, game_state, fonts, images, epilogue_manager):
#     """Draw the third epilogue slide"""
#     slides = epilogue_manager.epilogue_data["slides"]
#     slide_id = slides[2]["id"] if len(slides) > 2 else "epilogue_slide_3"
#     return draw_epilogue_slide_generic(surface, game_state, fonts, images, 
#                                       slide_id, epilogue_manager)

# # Add more slide functions as needed (4-7)# screens/epilogue_slides.py
"""
Terror in Redstone - Epilogue Sequence System
Professional narrative conclusion with conditional story variations
Mirrors intro_scenes.py architecture for consistency
"""

import pygame
import json
import os
from utils.constants import (
    BLACK, YELLOW, WHITE, wrap_text,
    # Reuse intro constants for consistency
    INTRO_TITLE_Y, INTRO_TITLE_DECORATION_OFFSET, INTRO_CONTENT_START_Y,
    INTRO_CONTENT_LINE_SPACING, INTRO_CONTENT_PARAGRAPH_SPACING, INTRO_CONTENT_MAX_WIDTH,
    INTRO_BUTTON_Y, INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT, INTRO_BUTTON_SPACING,
    INTRO_OVERLAY_ALPHA, INTRO_MOUNTAIN_HEIGHT_RATIO, INTRO_TOWN_Y_OFFSET,
    INTRO_SKY_DUSK, INTRO_SKY_NIGHT, INTRO_MOUNTAIN_SILHOUETTE, 
    INTRO_BUILDING_SILHOUETTE, INTRO_WARM_LIGHT, INTRO_DISTANT_LIGHT
)
from utils.graphics import draw_button, draw_centered_text

# Global variable to cache loaded epilogue data
_epilogue_data = None

def load_epilogue_sequence_data():
    """Load epilogue sequence data from JSON file"""
    global _epilogue_data
    
    if _epilogue_data is not None:
        return _epilogue_data
    
    try:
        epilogue_file_path = os.path.join("data", "narrative", "epilogue_sequence.json")
        
        if not os.path.exists(epilogue_file_path):
            print(f"⚠️ Epilogue sequence file not found: {epilogue_file_path}")
            return get_fallback_epilogue_data()
        
        with open(epilogue_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _epilogue_data = data["epilogue_sequence"]
            print(f"✅ Loaded epilogue sequence: {len(_epilogue_data['slides'])} slides")
            return _epilogue_data
            
    except Exception as e:
        print(f"❌ Error loading epilogue sequence: {e}")
        return get_fallback_epilogue_data()

def get_fallback_epilogue_data():
    """Fallback epilogue data if JSON file fails to load"""
    return {
        "title": "Terror in Redstone - Epilogue",
        "slides": [
            {
                "id": "epilogue_victory",
                "title": "VICTORY",
                "content": [
                    "The Shadow Blight has been sealed.",
                    "",
                    "Redstone is saved.",
                    "",
                    "But the cost of victory varies with each hero's choices..."
                ],
                "next_slide": "epilogue_end",
                "background_style": "dawn_sky"
            },
            {
                "id": "epilogue_end",
                "title": "THE END",
                "content": [
                    "Thank you for playing Terror in Redstone!",
                    "",
                    "Your adventure has concluded."
                ],
                "next_slide": "credits",
                "background_style": "town_square"
            }
        ],
        "ui_config": {
            "continue_button_text": "CONTINUE",
            "skip_button_text": "SKIP TO CREDITS",
            "title_color": "YELLOW",
            "text_color": "WHITE", 
            "background_color": "BLACK"
        }
    }

class EpilogueSequenceManager:
    """
    Manages epilogue slide sequence with conditional content resolution
    Handles navigation between slides and transition to credits
    """
    
    def __init__(self, event_manager, game_state):
        self.event_manager = event_manager
        self.game_state = game_state
        self.current_slide_index = 0
        self.epilogue_data = load_epilogue_sequence_data()
        self.epilogue_started = False
        self.register_events()
    
    def register_events(self):
        """Register events for epilogue sequence navigation"""
        self.event_manager.register("EPILOGUE_START", self.handle_epilogue_start)
        self.event_manager.register("EPILOGUE_NEXT", self.handle_next_slide)
        self.event_manager.register("EPILOGUE_SKIP", self.handle_skip_epilogue)
        
    def handle_epilogue_start(self, event_data):
        """Handle the start of epilogue sequence"""
        if not self.epilogue_started:
            self.epilogue_started = True
            print("🎬 Starting epilogue sequence...")
            
            # Start first slide
            self.current_slide_index = 0
            first_slide_id = self.epilogue_data["slides"][0]["id"]
            self.event_manager.emit("SCREEN_CHANGE", {"target": first_slide_id})
        
    def handle_next_slide(self, event_data):
        """Handle advancing to next slide in sequence"""
        slides = self.epilogue_data["slides"]
        
        if self.current_slide_index < len(slides) - 1:
            self.current_slide_index += 1
            next_slide_id = slides[self.current_slide_index]["id"]
            print(f"🎬 Advancing to epilogue slide: {next_slide_id}")
            self.event_manager.emit("SCREEN_CHANGE", {"target": next_slide_id})
        else:
            # End of epilogue sequence - go to credits
            self.complete_epilogue_sequence()
    
    def handle_skip_epilogue(self, event_data):
        """Handle skipping epilogue sequence entirely"""
        print("⏭️ Skipping epilogue sequence")
        self.complete_epilogue_sequence()
    
    def complete_epilogue_sequence(self):
        """Complete epilogue and transition to credits"""
        print("✨ Epilogue sequence complete - transitioning to credits")
        
        # Get the final slide's next_slide target
        slides = self.epilogue_data["slides"]
        if slides:
            final_slide = slides[-1]
            target = final_slide.get("next_slide", "credits")
            self.event_manager.emit("SCREEN_CHANGE", {"target": target})
        else:
            self.event_manager.emit("SCREEN_CHANGE", {"target": "credits"})
    
    def get_current_slide_data(self):
        """Get data for currently active epilogue slide with conditional content resolved"""
        slides = self.epilogue_data["slides"]
        if 0 <= self.current_slide_index < len(slides):
            slide_data = slides[self.current_slide_index]
            # Resolve conditional content based on game state
            return self.resolve_conditional_content(slide_data)
        return None
    
    def resolve_conditional_content(self, slide_data):
        """
        Check game state conditions and return appropriate content variant
        This is where we customize slides based on player choices!
        """
        # If no variations, return slide as-is
        if "variations" not in slide_data:
            return slide_data
        
        # Check each variation's condition
        for variant in slide_data["variations"]:
            condition = variant.get("condition")
            if self.check_condition(condition):
                # Found matching condition - merge with base slide
                resolved_slide = slide_data.copy()
                resolved_slide["content"] = variant["content"]
                if "title" in variant:
                    resolved_slide["title"] = variant["title"]
                return resolved_slide
        
        # No matching condition - return base slide with default content
        return slide_data
    
    def check_condition(self, condition_string):
        """
        Evaluate condition against game state
        
        Examples:
          "mayor_family_status == 'all_saved'"
          "marcus_outcome == 'fled'"
          "has_item:portal_seal_fragment"
          "player_species == 'Cavia'"
        """
        if not condition_string or condition_string == "default":
            return True  # Default condition always matches
        
        try:
            # Check for item possession
            if condition_string.startswith("has_item:"):
                item_id = condition_string.split(":")[1]
                return self.player_has_item(item_id)
            
            # Check for flag existence
            elif condition_string.startswith("has_flag:"):
                flag_name = condition_string.split(":")[1]
                return getattr(self.game_state, flag_name, False)
            
            # Evaluate complex condition (be careful with eval!)
            else:
                # Build safe namespace for evaluation
                safe_globals = {"__builtins__": {}}
                safe_locals = {"game_state": self.game_state}
                return eval(condition_string, safe_globals, safe_locals)
                
        except Exception as e:
            print(f"⚠️ Condition evaluation error: {condition_string} - {e}")
            return False
    
    def player_has_item(self, item_id):
        """Check if player has a specific item"""
        if not self.game_state or not hasattr(self.game_state, 'inventory'):
            return False
        
        # Check inventory for item
        for item in self.game_state.inventory:
            if item.get('id') == item_id:
                return True
        return False
    
    def reset_sequence(self):
        """Reset epilogue sequence to beginning"""
        self.current_slide_index = 0
        self.epilogue_started = False

def draw_epilogue_background(surface, style):
    """
    Create atmospheric backgrounds for epilogue slides
    Reuses intro background styles + adds new epilogue-specific ones
    """
    width, height = surface.get_size()
    mountain_height = int(height * INTRO_MOUNTAIN_HEIGHT_RATIO)
    
    if style == "dawn_sky":
        # Hopeful dawn gradient (brighter than intro)
        for y in range(height):
            intensity = 1 - (y / height)
            # Warm golden dawn colors
            sky_color = (
                int(30 + intensity * 120),   # Red
                int(20 + intensity * 100),   # Green
                int(50 + intensity * 80)     # Blue
            )
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Sun rising on horizon
        sun_x, sun_y = width - 200, mountain_height - 50
        pygame.draw.circle(surface, (255, 220, 100), (sun_x, sun_y), 40)
        pygame.draw.circle(surface, (255, 200, 50), (sun_x, sun_y), 35)
        
    elif style == "town_square":
        # Daytime town square (more hopeful)
        # Blue sky gradient
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            sky_color = (
                int(100 + intensity * 50),
                int(150 + intensity * 80),
                int(200 + intensity * 55)
            )
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Town buildings (same as intro but with day lighting)
        building_heights = [50, 70, 40, 90, 60, 50, 80, 65, 45, 75]
        building_width = width // len(building_heights)
        town_y = mountain_height + INTRO_TOWN_Y_OFFSET
        
        for i, building_height in enumerate(building_heights):
            x = i * building_width
            building_rect = pygame.Rect(x, town_y - building_height, building_width - 2, building_height)
            # Lighter building color for daytime
            pygame.draw.rect(surface, (80, 70, 60), building_rect)
            pygame.draw.rect(surface, (60, 50, 40), building_rect, 2)
            
    elif style == "violet_mortar_shop":
        # Purple-tinted background for Cassia's shop
        for y in range(height):
            intensity = 1 - (y / height)
            sky_color = (
                int(60 + intensity * 60),    # Red
                int(40 + intensity * 40),    # Green
                int(80 + intensity * 100)    # Blue (purple tint)
            )
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Simple shop silhouette
        shop_x, shop_y = width // 2 - 100, mountain_height + 80
        pygame.draw.rect(surface, (100, 60, 120), (shop_x, shop_y, 200, 100))
        
    elif style == "marsh_sunset":
        # Swamp healing - orange/pink sunset
        for y in range(height):
            intensity = 1 - (y / height)
            sky_color = (
                int(100 + intensity * 120),  # Warm orange
                int(50 + intensity * 80),
                int(80 + intensity * 50)
            )
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
            
    elif style == "ancient_scroll":
        # Mysterious parchment background for sequel hook
        for y in range(height):
            intensity = 1 - (y / height)
            # Aged parchment color
            sky_color = (
                int(180 + intensity * 40),
                int(160 + intensity * 40),
                int(120 + intensity * 30)
            )
            pygame.draw.line(surface, sky_color, (0, y), (width, y))
        
        # Ancient runes around border
        rune_color = (80, 60, 40)
        for x in range(0, width, 100):
            pygame.draw.circle(surface, rune_color, (x, 50), 3)
            pygame.draw.circle(surface, rune_color, (x, height - 50), 3)
            
    else:
        # Default: reuse road_dusk from intro
        for y in range(mountain_height):
            intensity = 1 - (y / mountain_height)
            sky_color = tuple(int(c * intensity * 1.8) for c in INTRO_SKY_DUSK)
            pygame.draw.line(surface, sky_color, (0, y), (width, y))

def draw_epilogue_slide_generic(surface, game_state, fonts, images, slide_id, epilogue_manager):
    """
    Cinematic epilogue slide renderer using established architectural patterns
    Full-screen layout with conditional content based on game state
    """
    # Get current slide data from manager (already has conditions resolved!)
    slide_data = epilogue_manager.get_current_slide_data()
    
    if not slide_data:
        print(f"❌ Error: Slide data not found for {slide_id}")
        return None
    
    # Get UI configuration
    ui_config = epilogue_manager.epilogue_data.get("ui_config", {})
    
    # Clear screen and draw atmospheric background
    surface.fill(BLACK)
    background_style = slide_data.get("background_style", "dawn_sky")
    draw_epilogue_background(surface, background_style)
    
    # Semi-transparent overlay for text readability
    overlay = pygame.Surface((1024, 768))
    overlay.set_alpha(INTRO_OVERLAY_ALPHA)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Slide title
    title_font = fonts.get('fantasy_large', fonts['header'])
    draw_centered_text(surface, slide_data["title"], title_font, INTRO_TITLE_Y, YELLOW)
    
    # Decorative line
    decoration_y = INTRO_TITLE_Y + INTRO_TITLE_DECORATION_OFFSET
    draw_centered_text(surface, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 
                    fonts.get('fantasy_medium', fonts['normal']), 
                    decoration_y, YELLOW)
    
    # Content text
    content_font = fonts.get('fantasy_medium', fonts['normal'])
    current_y = INTRO_CONTENT_START_Y
    
    for paragraph in slide_data["content"]:
        # Wrap text
        wrapped_lines = wrap_text(paragraph, content_font, INTRO_CONTENT_MAX_WIDTH)
        
        for line_surface in wrapped_lines:
            # Center each line
            line_rect = line_surface.get_rect(center=(512, current_y))
            surface.blit(line_surface, line_rect)
            current_y += INTRO_CONTENT_LINE_SPACING
        
        # Add paragraph spacing
        current_y += INTRO_CONTENT_PARAGRAPH_SPACING
    
    # Navigation buttons
    total_button_width = (2 * INTRO_BUTTON_WIDTH) + INTRO_BUTTON_SPACING
    start_x = (1024 - total_button_width) // 2
    
    # CONTINUE button
    continue_text = ui_config.get("continue_button_text", "CONTINUE")
    continue_button = draw_button(surface, start_x, INTRO_BUTTON_Y, 
                                INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
                                continue_text, fonts.get('fantasy_medium', fonts['normal']))
    
    # SKIP button
    skip_x = start_x + INTRO_BUTTON_WIDTH + INTRO_BUTTON_SPACING
    skip_text = ui_config.get("skip_button_text", "SKIP TO CREDITS")
    skip_button = draw_button(surface, skip_x, INTRO_BUTTON_Y, 
                            INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
                            skip_text, fonts.get('fantasy_medium', fonts['normal']))
    
    # Return button coordinates for registration
    return {
        "continue_button": continue_button,
        "skip_button": skip_button,
        "slide_data": slide_data
    }

# Individual slide drawing functions (NO manager parameter - matches intro_scenes)
def draw_epilogue_slide_1(surface, game_state, fonts, images):
    """Draw the first epilogue slide"""
    # Create manager instance if needed (like intro does with load_intro_sequence_data)
    epilogue_data = load_epilogue_sequence_data()
    
    # Find the slide
    slide_data = epilogue_data["slides"][0] if epilogue_data["slides"] else None
    if not slide_data:
        print("❌ Error: No epilogue slides found")
        return None
    
    # Resolve conditions and render
    return _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data)

def draw_epilogue_slide_2(surface, game_state, fonts, images):
    """Draw the second epilogue slide"""
    epilogue_data = load_epilogue_sequence_data()
    slide_data = epilogue_data["slides"][1] if len(epilogue_data["slides"]) > 1 else None
    if not slide_data:
        return None
    return _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data)

def draw_epilogue_slide_3(surface, game_state, fonts, images):
    """Draw the third epilogue slide"""
    epilogue_data = load_epilogue_sequence_data()
    slide_data = epilogue_data["slides"][2] if len(epilogue_data["slides"]) > 2 else None
    if not slide_data:
        return None
    return _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data)

def draw_epilogue_slide_4(surface, game_state, fonts, images):
    """Draw the fourth epilogue slide"""
    epilogue_data = load_epilogue_sequence_data()
    slide_data = epilogue_data["slides"][3] if len(epilogue_data["slides"]) > 3 else None
    if not slide_data:
        return None
    return _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data)

def draw_epilogue_slide_5(surface, game_state, fonts, images):
    """Draw the fifth epilogue slide"""
    epilogue_data = load_epilogue_sequence_data()
    slide_data = epilogue_data["slides"][4] if len(epilogue_data["slides"]) > 4 else None
    if not slide_data:
        return None
    return _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data)

def draw_epilogue_slide_6(surface, game_state, fonts, images):
    """Draw the sixth epilogue slide"""
    epilogue_data = load_epilogue_sequence_data()
    slide_data = epilogue_data["slides"][5] if len(epilogue_data["slides"]) > 5 else None
    if not slide_data:
        return None
    return _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data)

def draw_epilogue_slide_7(surface, game_state, fonts, images):
    """Draw the seventh epilogue slide"""
    epilogue_data = load_epilogue_sequence_data()
    slide_data = epilogue_data["slides"][6] if len(epilogue_data["slides"]) > 6 else None
    if not slide_data:
        return None
    return _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data)

# Helper function to render with condition resolution
def _render_epilogue_slide(surface, game_state, fonts, images, slide_data, epilogue_data):
    """Internal helper to render a slide with conditional content"""
    # Resolve conditional content
    resolved_slide = _resolve_slide_conditions(slide_data, game_state)
    
    # Clear screen and draw background
    surface.fill(BLACK)
    background_style = resolved_slide.get("background_style", "dawn_sky")
    draw_epilogue_background(surface, background_style)
    
    # Semi-transparent overlay
    overlay = pygame.Surface((1024, 768))
    overlay.set_alpha(INTRO_OVERLAY_ALPHA)
    overlay.fill(BLACK)
    surface.blit(overlay, (0, 0))
    
    # Slide title
    title_font = fonts.get('fantasy_large', fonts['header'])
    draw_centered_text(surface, resolved_slide["title"], title_font, INTRO_TITLE_Y, YELLOW)
    
    # Decorative line
    decoration_y = INTRO_TITLE_Y + INTRO_TITLE_DECORATION_OFFSET
    draw_centered_text(surface, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 
                    fonts.get('fantasy_medium', fonts['normal']), 
                    decoration_y, YELLOW)
    
    # Content text
    content_font = fonts.get('fantasy_medium', fonts['normal'])
    current_y = INTRO_CONTENT_START_Y
    
    for paragraph in resolved_slide["content"]:
        wrapped_lines = wrap_text(paragraph, content_font, INTRO_CONTENT_MAX_WIDTH)
        for line_surface in wrapped_lines:
            line_rect = line_surface.get_rect(center=(512, current_y))
            surface.blit(line_surface, line_rect)
            current_y += INTRO_CONTENT_LINE_SPACING
        current_y += INTRO_CONTENT_PARAGRAPH_SPACING
    
    # Get UI config
    ui_config = epilogue_data.get("ui_config", {})
    
    # Navigation buttons
    total_button_width = (2 * INTRO_BUTTON_WIDTH) + INTRO_BUTTON_SPACING
    start_x = (1024 - total_button_width) // 2
    
    # CONTINUE button
    continue_text = ui_config.get("continue_button_text", "CONTINUE")
    continue_button = draw_button(surface, start_x, INTRO_BUTTON_Y, 
                                INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
                                continue_text, fonts.get('fantasy_medium', fonts['normal']))
    
    # SKIP button
    skip_x = start_x + INTRO_BUTTON_WIDTH + INTRO_BUTTON_SPACING
    skip_text = ui_config.get("skip_button_text", "SKIP TO CREDITS")
    skip_button = draw_button(surface, skip_x, INTRO_BUTTON_Y, 
                            INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT,
                            skip_text, fonts.get('fantasy_medium', fonts['normal']))
    
    return {
        "continue_button": continue_button,
        "skip_button": skip_button,
        "slide_data": resolved_slide
    }

def _resolve_slide_conditions(slide_data, game_state):
    """Resolve conditional content based on game state"""
    if "variations" not in slide_data:
        return slide_data
    
    # Check each variation's condition
    for variant in slide_data["variations"]:
        condition = variant.get("condition")
        if _check_condition(condition, game_state):
            # Found matching condition - merge with base slide
            resolved_slide = slide_data.copy()
            resolved_slide["content"] = variant["content"]
            if "title" in variant:
                resolved_slide["title"] = variant["title"]
            return resolved_slide
    
    # No matching condition - return base slide
    return slide_data

def _check_condition(condition_string, game_state):
    """Evaluate condition against game state"""
    if not condition_string or condition_string == "default":
        return True
    
    try:
        # Check for flag existence
        if condition_string.startswith("has_flag:"):
            flag_name = condition_string.split(":")[1]
            return getattr(game_state, flag_name, False)
        
        # Evaluate complex condition
        else:
            safe_globals = {"__builtins__": {}}
            safe_locals = {"game_state": game_state}
            return eval(condition_string, safe_globals, safe_locals)
            
    except Exception as e:
        print(f"⚠️ Condition evaluation error: {condition_string} - {e}")
        return False
    
def handle_next_slide(self, event_data):
    """Handle advancing to next slide in sequence"""
    slides = self.epilogue_data["slides"]
    
    if self.current_slide_index < len(slides) - 1:
        self.current_slide_index += 1
        # CRITICAL: Use screen number, NOT JSON ID
        next_slide_screen = f"epilogue_slide_{self.current_slide_index + 1}"
        print(f"🎬 Advancing to epilogue slide #{self.current_slide_index + 1}: {next_slide_screen}")
        self.event_manager.emit("SCREEN_CHANGE", {"target": next_slide_screen})
    else:
        # End of epilogue sequence - go to credits
        self.complete_epilogue_sequence()