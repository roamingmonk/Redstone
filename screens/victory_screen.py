# screens/victory_screen.py
"""
Terror in Redstone - Victory Screen
Post-boss combat victory screen with detailed statistics and rewards
Follows established architectural patterns from intro_scenes.py
"""

import pygame
from typing import Dict, Any
from utils.constants import (
    BLACK, YELLOW, WHITE, DARK_GRAY, LIGHTEST_GRAY,
    INTRO_TITLE_Y, INTRO_CONTENT_START_Y, INTRO_CONTENT_LINE_SPACING,
    INTRO_BUTTON_Y, INTRO_BUTTON_WIDTH, INTRO_BUTTON_HEIGHT
)
from utils.graphics import draw_button, draw_centered_text


def calculate_victory_bonuses(game_state) -> Dict[str, Any]:
    """
    Calculate all XP bonuses and rewards based on player achievements
    
    Returns dict with:
        - base_victory: int (always 1000)
        - mayor_family: int (0, 300, or 500 based on rescue)
        - portal_sealed: int (250 if portal destroyed)
        - total_xp: int (sum of all bonuses)
        - special_items: list of item names awarded
        - mission_stats: dict of completion stats
    """
    bonuses = {
        'base_victory': 1000,  # Always awarded for defeating the boss
        'mayor_family': 0,
        'portal_sealed': 250,  # Always awarded (portal always seals on boss defeat)
        'special_items': [],
        'mission_stats': {}
    }
    
    # Check mayor's family rescue status (Phase 1 implementation)
    mayor_family_status = getattr(game_state, 'mayor_family_status', 'none')
    
    if mayor_family_status == 'all_saved':
        bonuses['mayor_family'] = 500
        bonuses['mission_stats']['family_status'] = 'All Rescued ✓'
    elif mayor_family_status == 'partial':
        bonuses['mayor_family'] = 300
        bonuses['mission_stats']['family_status'] = 'Partial Rescue'
    else:
        bonuses['mayor_family'] = 0
        bonuses['mission_stats']['family_status'] = 'None Rescued'
    
    # Calculate total XP
    bonuses['total_xp'] = (
        bonuses['base_victory'] + 
        bonuses['mayor_family'] + 
        bonuses['portal_sealed']
    )
    
    # Special items (always awarded for boss victory)
    bonuses['special_items'] = [
        'Portal Seal Fragment',
        "Marcus's Research Notes"
    ]
    
    # Mission completion stats
    party = getattr(game_state, 'party_members', [])
    party_survivors = len([m for m in party if True])  # TODO: Check if alive
    party_total = len(party) + 1  # +1 for player character
    
    bonuses['mission_stats']['party_survivors'] = f"{party_total}/{party_total}"
    
    # TODO: Add time tracking when TimeManager is implemented
    # For now, show placeholder
    bonuses['mission_stats']['time_played'] = "Adventure Complete"
    
    return bonuses


def draw_victory_screen(surface: pygame.Surface, game_state, fonts: Dict, images: Dict) -> Dict[str, Any]:
    """
    Draw the victory screen with detailed statistics
    
    Returns dict with:
        - continue_button: pygame.Rect for click detection
        - bonus_data: calculated bonuses for reference
    """
    surface.fill(BLACK)
    width, height = surface.get_size()
    
    # Calculate bonuses
    bonuses = calculate_victory_bonuses(game_state)
    
    # Draw decorative border
    border_rect = pygame.Rect(40, 40, width - 80, height - 80)
    pygame.draw.rect(surface, YELLOW, border_rect, 3)
    
    # Title section
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render("VICTORY!", True, YELLOW)
    title_rect = title_text.get_rect(center=(width // 2, 80))
    surface.blit(title_text, title_rect)
    
    subtitle_font = fonts.get('fantasy_medium', fonts['normal'])
    subtitle_text = subtitle_font.render("The Shadow Blight is Sealed", True, WHITE)
    subtitle_rect = subtitle_text.get_rect(center=(width // 2, 120))
    surface.blit(subtitle_text, subtitle_rect)
    
    # Horizontal separator
    pygame.draw.line(surface, YELLOW, (80, 150), (width - 80, 150), 2)
    
    # Content font
    content_font = fonts.get('normal', fonts['normal'])
    small_font = fonts.get('small', fonts['normal'])
    
    # Experience Earned Section
    y_pos = 180
    
    section_title = content_font.render("EXPERIENCE EARNED:", True, YELLOW)
    surface.blit(section_title, (100, y_pos))
    y_pos += 35
    
    # Base victory bonus
    base_text = small_font.render(f"Base Victory Bonus: {bonuses['base_victory']} XP", True, WHITE)
    surface.blit(base_text, (120, y_pos))
    y_pos += 25
    
    # Mayor's family bonus (if any)
    if bonuses['mayor_family'] > 0:
        family_text = small_font.render(
            f"Mayor's Family Rescued: +{bonuses['mayor_family']} XP", 
            True, WHITE
        )
        surface.blit(family_text, (120, y_pos))
        y_pos += 25
    
    # Portal sealed bonus
    portal_text = small_font.render(f"Portal Sealed: +{bonuses['portal_sealed']} XP", True, WHITE)
    surface.blit(portal_text, (120, y_pos))
    y_pos += 25
    
    # Total line
    pygame.draw.line(surface, DARK_GRAY, (120, y_pos), (400, y_pos), 1)
    y_pos += 10
    
    total_text = content_font.render(f"TOTAL EARNED: {bonuses['total_xp']} XP", True, YELLOW)
    surface.blit(total_text, (120, y_pos))
    y_pos += 45
    
    # Special Rewards Section
    rewards_title = content_font.render("SPECIAL REWARDS:", True, YELLOW)
    surface.blit(rewards_title, (100, y_pos))
    y_pos += 35
    
    for item in bonuses['special_items']:
        item_text = small_font.render(f"* {item}", True, WHITE)
        surface.blit(item_text, (120, y_pos))
        y_pos += 25
    
    y_pos += 20
    
    # Mission Summary Section
    summary_title = content_font.render("MISSION SUMMARY:", True, YELLOW)
    surface.blit(summary_title, (100, y_pos))
    y_pos += 35
    
    time_text = small_font.render(
        f"Time Played: {bonuses['mission_stats']['time_played']}", 
        True, WHITE
    )
    surface.blit(time_text, (120, y_pos))
    y_pos += 25
    
    party_text = small_font.render(
        f"Party Survivors: {bonuses['mission_stats']['party_survivors']}", 
        True, WHITE
    )
    surface.blit(party_text, (120, y_pos))
    y_pos += 25
    
    family_status_text = small_font.render(
        f"Mayor's Family: {bonuses['mission_stats']['family_status']}", 
        True, WHITE
    )
    surface.blit(family_status_text, (120, y_pos))
    y_pos += 35
    
    # Auto-save notice
    save_notice = small_font.render("Game auto-saved.", True, LIGHTEST_GRAY)
    save_rect = save_notice.get_rect(center=(width // 2, y_pos))
    surface.blit(save_notice, save_rect)
    
    # Continue button at bottom
    button_y = height - 100
    button_x = (width - INTRO_BUTTON_WIDTH) // 2
    
    continue_button = draw_button(
        surface, 
        button_x, 
        button_y,
        INTRO_BUTTON_WIDTH, 
        INTRO_BUTTON_HEIGHT,
        "Continue to Redstone",
        content_font
    )
    
    # Store clickables in game_state for input handler
    clickables = {
        'continue_button': continue_button,
        'bonus_data': bonuses
    }
    game_state._victory_screen_clickables = clickables

    return clickables


class VictoryScreenManager:
    """
    Manages victory screen state and auto-save
    Follows pattern from IntroSequenceManager
    """
    
    def __init__(self, event_manager, save_manager):
        self.event_manager = event_manager
        self.save_manager = save_manager
        self.victory_shown = False
        self.auto_save_complete = False
        self.bonus_data = None
        
    def show_victory_screen(self, game_state):
        """Initialize victory screen display"""
        print("🏆 Showing victory screen")
        
        # Calculate bonuses
        self.bonus_data = calculate_victory_bonuses(game_state)
        
        # Award XP immediately (using your CharacterEngine's expected format)
        if self.bonus_data and self.event_manager:
            self.event_manager.emit("XP_AWARDED", {
                'amount': self.bonus_data['total_xp'],
                'reason': 'Boss Victory',  # Changed from 'source' to 'reason'
                'recipient': 'party'        # Award to entire party
            })
            print(f"⚡ Awarded {self.bonus_data['total_xp']} XP for boss victory")
        
        # Perform auto-save
        if not self.auto_save_complete and self.save_manager:
            try:
                success = self.save_manager.save_game(0)  # Slot 0 = auto-save
                if success:
                    print("💾 Victory auto-save checkpoint created (slot 0)")
                    self.auto_save_complete = True
                else:
                    print("⚠️ Victory auto-save failed, but continuing")
            except Exception as e:
                print(f"⚠️ Victory auto-save error: {e}, but continuing")
        
        self.victory_shown = True
        
    def handle_continue_button(self):
        """Handle continue button click - transition to town celebration"""
        print("🎉 Transitioning to town celebration")
        
        # TODO: When town celebration screen is implemented, transition there
        # For now, return to town
        self.event_manager.emit("SCREEN_CHANGE", {
            'target': 'redstone_town',
            'source': 'victory_screen'
        })
    
    def reset(self):
        """Reset victory screen state for next playthrough"""
        self.victory_shown = False
        self.auto_save_complete = False
        self.bonus_data = None