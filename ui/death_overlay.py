# ui/death_overlay.py
"""
Death Overlay - Displayed when player character dies in combat
Provides options to load a save, restart combat, or return to title
"""

import pygame
from utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BLACK, WHITE, RED, DARK_RED, GRAY, BRIGHT_GREEN
)
from utils.graphics import draw_text_with_shadow, draw_button
from utils.constants import wrap_text

class DeathOverlay:
    """
    Death screen overlay displayed when player dies in combat
    
    Features:
    - Dramatic "YOU DIED" message
    - Character name and death context
    - Space reserved for future death artwork/animation
    - Three action buttons: Load Game, Restart Combat, Return to Title
    """
    
    def __init__(self):
        """Initialize death overlay"""
        self.active = False
        self.character_name = ""
        self.buttons = {}
        self.current_death_quote = ""
    
    def show(self, character_name: str, death_quote: str = ""):
        """Display the death overlay"""
        self.active = True
        self.character_name = character_name
        self.current_death_quote = death_quote or '"The adventure ends here." - Unknown'
    
    def hide(self):
        """Hide the death overlay"""
        self.active = False
        self.character_name = ""
        self.current_death_quote = ""
        print("💀 Death overlay hidden")

    def render(self, surface: pygame.Surface, fonts: dict) -> dict:
        """ Render the death overlay
        Args:surface: Pygame surface to draw onfonts: Dictionary of loaded fonts
        Returns:Dictionary of clickable button rectangles
        """
        if not self.active:
            return {}
        
        # Semi-transparent dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(230)  # Nearly opaque
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Get fonts
        title_font = fonts.get('fantasy_large', fonts['normal'])
        subtitle_font = fonts.get('fantasy_medium', fonts['normal'])
        normal_font = fonts.get('normal')
        small_font = fonts.get('small')
        
        # ========================================
        # MAIN TITLE: "YOU DIED"
        # ========================================
        title_text = "YOU DIED"
        draw_text_with_shadow(
            surface, 
            title_text, 
            title_font,
            SCREEN_WIDTH // 2 - title_font.size(title_text)[0] // 2,
            100,
            text_color=RED,
            shadow_color=BLACK
        )
        
        # ========================================
        # CHARACTER NAME / DEATH MESSAGE
        # ========================================
        death_message = f"{self.character_name} has fallen in battle..."
        draw_text_with_shadow(
            surface,
            death_message,
            subtitle_font,
            SCREEN_WIDTH // 2 - subtitle_font.size(death_message)[0] // 2,
            180,
            text_color=RED,
            shadow_color=BLACK
        )
 
        # ========================================
        # DEATH QUOTE (MOVED BEFORE ARTWORK)
        # ========================================
        quote_font = fonts.get('small', normal_font)

        # Use the quote that was picked when overlay was shown
        death_quote = self.current_death_quote

        # Wrap quote text to fit width
        max_quote_width = 700
        wrapped_quote = wrap_text(death_quote, quote_font, max_quote_width)

        # Display wrapped quote lines
        quote_y = 220
        for line_surface in wrapped_quote:
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, quote_y))
            surface.blit(line_surface, line_rect)
            quote_y += 25  # Line spacing
     # ========================================
        # ARTWORK SPACE (Reserved for future use)
        # ========================================
        # This space (Y: 220-420) is reserved for:
        # - Death animation sprite sheet
        # - Dramatic skull artwork
        # - Character portrait with "defeated" overlay
        # - Particle effects / fade animations
        
        # ========================================
        # ARTWORK SPACE (Reserved for future use)
        # ========================================
        # Adjusted Y position to be BELOW the quote
        artwork_rect = pygame.Rect(362, 300, 300, 150)
        pygame.draw.rect(surface, GRAY, artwork_rect, 2)  # Border only

        placeholder_text = "(Space for artwork)"
        placeholder_surface = small_font.render(placeholder_text, True, GRAY)
        placeholder_rect = placeholder_surface.get_rect(center=artwork_rect.center)
        surface.blit(placeholder_surface, placeholder_rect)

        # ========================================
        # ACTION BUTTONS
        # ========================================
        button_y = 480
        button_width = 240
        button_height = 50
        button_spacing = 20
        
        # Calculate centered X positions for 3 buttons
        total_width = (button_width * 3) + (button_spacing * 2)
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Button 1: Load Game
        load_x = start_x
        load_button = draw_button(
            surface,
            load_x,
            button_y,
            button_width,
            button_height,
            "Load Game",
            normal_font,
            pressed=False,
            selected=False
        )
        
        # Button 2: Restart Combat (make it selected/highlighted)
        restart_x = load_x + button_width + button_spacing
        restart_button = draw_button(
            surface,
            restart_x,
            button_y,
            button_width,
            button_height,
            "Restart Combat",
            small_font,
            pressed=False,
            selected=False  # Highlight this button
        )
        
        # Button 3: Return to Title
        title_x = restart_x + button_width + button_spacing
        title_button = draw_button(
            surface,
            title_x,
            button_y,
            button_width,
            button_height,
            "Return to Title",
            small_font,
            pressed=False,
            selected=False
        )
        
        # ========================================
        # HELPFUL HINT TEXT
        # ========================================
        hint_text = "Restart Combat will reload your last autosave from before the battle"
        hint_surface = normal_font.render(hint_text, True, GRAY)
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, 560))
        surface.blit(hint_surface, hint_rect)
        
        # Return clickable buttons
        self.buttons = {
            'load_game': load_button,
            'restart_combat': restart_button,
            'return_to_title': title_button
        }
        
        return self.buttons
    
    def handle_click(self, pos: tuple, event_manager) -> bool:
        """
        Handle mouse click on death overlay
        
        Args:
            pos: Mouse (x, y) position
            event_manager: EventManager for emitting actions
            
        Returns:
            True if click was handled
        """
        if not self.active:
            return False
        
        # Check button clicks
        if 'load_game' in self.buttons and self.buttons['load_game'].collidepoint(pos):
            print("🎮 Death Overlay: Load Game clicked")
            event_manager.emit("DEATH_ACTION_LOAD_GAME", {})
            return True
        
        if 'restart_combat' in self.buttons and self.buttons['restart_combat'].collidepoint(pos):
            print("🎮 Death Overlay: Restart Combat clicked")
            event_manager.emit("DEATH_ACTION_RESTART_COMBAT", {})
            return True
        
        if 'return_to_title' in self.buttons and self.buttons['return_to_title'].collidepoint(pos):
            print("🎮 Death Overlay: Return to Title clicked")
            event_manager.emit("DEATH_ACTION_RETURN_TO_TITLE", {})
            return True
        
        return False

# ==========================================
# HELPER FUNCTIONS FOR INTEGRATION
# ==========================================

def create_death_overlay() -> DeathOverlay:
    """Factory function to create death overlay instance"""
    return DeathOverlay()

def handle_player_death(event_manager, character_name: str):
    """
    Convenience function to trigger death overlay
    
    Args:
        event_manager: EventManager instance
        character_name: Name of character who died
    """
    event_manager.emit("SHOW_DEATH_OVERLAY", {
        'character_name': character_name
    })