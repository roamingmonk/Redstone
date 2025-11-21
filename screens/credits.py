# screens/credits.py
"""
Terror in Redstone - Credits Screen
JSON-driven scrolling credits with skip functionality
"""

import pygame
import json
import os
from utils.constants import BLACK, WHITE, YELLOW
from utils.graphics import draw_centered_text

# Global variable to cache loaded credits data
_credits_data = None

def load_credits_data():
    """Load credits data from JSON file"""
    global _credits_data
    
    if _credits_data is not None:
        return _credits_data
    
    try:
        credits_file_path = os.path.join("data", "narrative", "credits_data.json")
        
        if not os.path.exists(credits_file_path):
            print(f"⚠️ Credits file not found: {credits_file_path}")
            return get_fallback_credits_data()
        
        with open(credits_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _credits_data = data["credits"]
            print(f"✅ Loaded credits: {len(_credits_data['sections'])} sections")
            return _credits_data
            
    except Exception as e:
        print(f"❌ Error loading credits: {e}")
        return get_fallback_credits_data()

def get_fallback_credits_data():
    """Fallback credits if JSON fails to load"""
    return {
        "sections": [
            {
                "title": "Terror in Redstone",
                "entries": ["A Classic CRPG Adventure"],
                "spacing": 4
            },
            {
                "title": "Created By",
                "entries": ["[Your Name]"],
                "spacing": 4
            },
            {
                "title": "Thank You",
                "entries": ["For playing!"],
                "spacing": 3
            }
        ],
        "scroll_speed": 1.0,
        "final_message": "Press ESC to continue",
        "final_message_pause": 3.0
    }

class CreditsScreen:
    """
    JSON-driven scrolling credits screen
    Auto-scrolls with ESC to skip functionality
    """
    
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.credits_data = load_credits_data()
        self.scroll_position = 768  # Start below screen
        self.scroll_speed = self.credits_data.get("scroll_speed", 1.0)
        self.credits_lines = self.build_credits_lines()
        self.final_message = self.credits_data.get("final_message", "Press ESC to continue")
        self.final_message_pause = self.credits_data.get("final_message_pause", 3.0)
        self.showing_final_message = False
        self.final_message_timer = 0
        self.credits_complete = False
        
        self.epilogue_manager = None 

    def build_credits_lines(self):
        """Convert JSON data to renderable lines"""
        lines = []
        
        for section in self.credits_data["sections"]:
            # Section title
            lines.append({
                "text": section["title"],
                "style": "title",
                "color": YELLOW  # Make sure this uses YELLOW from constants
            })
            lines.append({"text": "", "style": "blank", "color": WHITE})  # ADD COLOR HERE
            
            # Section entries
            for entry in section["entries"]:
                lines.append({
                    "text": entry,
                    "style": "normal",
                    "color": WHITE
                })
            
            # Spacing
            spacing = section.get("spacing", 2)
            for _ in range(spacing):
                lines.append({"text": "", "style": "blank", "color": WHITE})  # ADD COLOR HERE
        
        return lines
    
    def update(self, dt):
        """Update credits scroll position"""
        if self.credits_complete:
            return
        
        if not self.showing_final_message:
            # Scroll upward
            self.scroll_position -= self.scroll_speed
            
            # Check if all credits have scrolled off screen
            total_height = len(self.credits_lines) * 35
            if self.scroll_position < -total_height:
                self.showing_final_message = True
                self.final_message_timer = 0
        else:
            # Count down final message pause (convert dt from ms to seconds)
            self.final_message_timer += dt / 1000.0
            if self.final_message_timer >= self.final_message_pause:
                self.complete_credits()
    
    def handle_input(self, event):
        """Handle keyboard input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.complete_credits()
    
    def complete_credits(self):
        """Complete credits and transition to post-game menu"""
        if not self.credits_complete:
            print("✨ Credits complete - returning to main menu")
            self.credits_complete = True
            # For now, go back to main menu
            # TODO: Create post_game_menu screen
            self.event_manager.emit("SCREEN_CHANGE", {"target": "main_menu"})
    
    def draw(self, surface, fonts):
        """Draw scrolling credits"""
        surface.fill(BLACK)
        
        if not self.showing_final_message:
            # Draw scrolling credits
            current_y = self.scroll_position
            
            for line_data in self.credits_lines:
                if -50 < current_y < 818:  # Only draw visible lines
                    text = line_data["text"]
                    color = line_data["color"]
                    style = line_data["style"]
                    
                    if style == "title":
                        font = fonts.get('fantasy_large', fonts['header'])
                    else:
                        font = fonts.get('fantasy_medium', fonts['normal'])
                    
                    # Render and center text
                    if text:
                        draw_centered_text(surface, text, font, int(current_y), color)
                
                current_y += 35  # Line spacing
        else:
            # Show final message
            draw_centered_text(surface, self.final_message, 
                             fonts.get('fantasy_large', fonts['header']), 
                             384, YELLOW)

def draw_credits_screen(surface, game_state, fonts, images, credits_screen):
    """Main credits screen draw function"""
    credits_screen.draw(surface, fonts)
    return {"credits_screen": credits_screen}