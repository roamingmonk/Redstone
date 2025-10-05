# screens/statistics_overlay.py
"""
Terror in Redstone - Player Statistics Overlay
Tracks and displays player achievements, combat stats, and game metrics

Uses BaseTabbedOverlay for consistent UI experience
"""

import pygame
from utils.tabbed_overlay_utils import BaseTabbedOverlay
from utils.constants import *
from utils.graphics import draw_text
from utils.overlay_utils import (
    draw_popup_background, draw_chunky_border,
    draw_centered_text
)

class StatisticsOverlay(BaseTabbedOverlay):
    """
    Player statistics tracking overlay
    
    Displays comprehensive player stats across three tabs:
    - PLAYER: General achievements and progression
    - COMBAT: Battle statistics and kill tracking
    - OTHER: Miscellaneous metrics
    """
    
    def __init__(self, screen_manager=None):
        super().__init__("statistics_key", "PLAYER STATISTICS", screen_manager)
        
        # Add 3 tabs for different stat categories
        self.add_tab("player", "PLAYER", hotkey=pygame.K_1)
        self.add_tab("combat", "COMBAT", hotkey=pygame.K_2)
        self.add_tab("other", "OTHER", hotkey=pygame.K_3)
    
    def render_tab_content(self, surface, active_tab, game_state, fonts, images):
        """Render content for the active statistics tab"""
        try:
            current_tab = active_tab.tab_id
            
            # Get content area
            content_rect = self.get_content_area_rect()
            content_x = content_rect.x + SPACING['margin']
            content_y = content_rect.y + 20
            
            # Render appropriate tab content
            if current_tab == "player":
                self._render_player_stats(surface, game_state, fonts, content_x, content_y)
            elif current_tab == "combat":
                self._render_combat_stats(surface, game_state, fonts, content_x, content_y)
            elif current_tab == "other":
                self._render_other_stats(surface, game_state, fonts, content_x, content_y)
                
        except Exception as e:
            print(f"⚠️ Error rendering statistics tab: {e}")
            content_rect = self.get_content_area_rect()
            draw_centered_text(surface, f"Statistics Error: {e}",
                             fonts['normal'], content_rect.centery, WHITE, 1024)
    
    def _render_player_stats(self, surface, game_state, fonts, start_x, start_y):
        """Render PLAYER tab statistics in two columns"""
        stats = game_state.player_statistics
        
        # Title
        title_font = fonts.get('fantasy_large', fonts['header'])
        title_y = start_y - 0
        draw_centered_text(surface, "GENERAL STATISTICS", title_font, title_y, BRIGHT_GREEN, 1024)
        
        # Stats display with two columns
        stat_font = fonts.get('fantasy_small', fonts['normal'])
        y_start = start_y + 35
        line_height = 35
        
        # Left column stats
        left_column_x = start_x + 40
        left_stats = [
            f"NPCs Met: {stats['npcs_met']}",
            f"Drinks Consumed: {stats['drinks_consumed']}",
            f"Potions Consumed: {stats['potions_consumed']}",
            f"Items Discarded: {stats['items_discarded']}",
            "",  # Spacer
            f"Total Gold Earned: {stats['total_gold_earned']}",  # NEW
            "",  # Spacer
            f"XP from Combat: {stats['xp_from_combat']}",
            f"XP from Non-Combat: {stats['xp_from_noncombat']}",
            f"Total XP: {stats['xp_from_combat'] + stats['xp_from_noncombat']}"
        ]
        
        # Right column stats
        right_column_x = start_x + 450
        
        # Format winnings for right column
        winnings = stats['dice_total_winnings']
        if winnings > 0:
            winnings_text = f"Dice Winnings: +{winnings} gold"
        elif winnings < 0:
            winnings_text = f"Dice Winnings: {winnings} gold"
        else:
            winnings_text = f"Dice Winnings: 0 gold"
        
        right_stats = [
            f"Dice Games Played: {stats['dice_games_played']}",
            winnings_text,
            f"Longest Win Streak: {stats['longest_win_streak']}",
            f"Longest Losing Streak: {stats['longest_losing_streak']}",
            f"Best Single Win: {stats['highest_winning_roll']} gold"  
        ]
        
        # Render left column
        y_pos = y_start
        for stat_line in left_stats:
            if stat_line:  # Skip empty spacers
                stat_surface = stat_font.render(stat_line, True, WHITE)
                surface.blit(stat_surface, (left_column_x, y_pos))
            y_pos += line_height
        
        # Render right column
        y_pos = y_start
        for stat_line in right_stats:
            if stat_line:
                stat_surface = stat_font.render(stat_line, True, WHITE)
                surface.blit(stat_surface, (right_column_x, y_pos))
            y_pos += line_height
    
    def _render_combat_stats(self, surface, game_state, fonts, start_x, start_y):
        """Render COMBAT tab statistics in two columns"""
        stats = game_state.player_statistics
        title_y = start_y - 0
        # Title
        title_font = fonts.get('fantasy_large', fonts['header'])
        draw_centered_text(surface, "COMBAT STATISTICS", title_font, title_y, BRIGHT_GREEN, 1024)
        
        # Stats display with two columns
        stat_font = fonts.get('fantasy_small', fonts['normal'])
        y_start = start_y + 35
        line_height = 35
        
        # Left column - Kills and weapons
        left_column_x = start_x + 40
        left_stats = [
            f"Player Kills: {stats['player_kills']}",
            f"Party Kills: {stats['party_kills']}",
            f"Total Kills: {stats['player_kills'] + stats['party_kills']}",
            "",  # Spacer
        ]
        
        # Favorite weapon
        weapon_kills = stats.get('weapon_kills', {})
        if weapon_kills:
            favorite_weapon = max(weapon_kills.items(), key=lambda x: x[1])
            weapon_name = favorite_weapon[0].replace('_', ' ').title()
            left_stats.append(f"Favorite Weapon: {weapon_name} ({favorite_weapon[1]} kills)")
        else:
            left_stats.append(f"Favorite Weapon: None yet")
        
        # Party kill leader
        party_kills_dict = stats.get('party_member_kills', {})
        if party_kills_dict:
            kill_leader = max(party_kills_dict.items(), key=lambda x: x[1])
            leader_name = kill_leader[0].replace('_', ' ').title()
            left_stats.append(f"Party Kill Leader: {leader_name} ({kill_leader[1]} kills)")
        else:
            left_stats.append(f"Party Kill Leader: None yet")
        
        # Right column - Hit stats and criticals
        right_column_x = start_x + 450
        right_stats = []
        
        # Hit/Miss statistics
        total_attacks = stats['hits'] + stats['misses']
        if total_attacks > 0:
            hit_percent = (stats['hits'] / total_attacks) * 100
            right_stats.extend([
                f"Hits: {stats['hits']}",
                f"Misses: {stats['misses']}",
                f"Hit Rate: {hit_percent:.1f}%",
                "",  # Spacer
                f"Critical Hits: {stats['critical_hits']}",
                f"Critical Misses: {stats['critical_misses']}",
                "",  # Spacer
                f"Biggest Hit: {stats['biggest_hit']} damage",
                f"Party Knockouts: {stats['party_knockouts']}"
            ])
        else:
            right_stats.extend([
                f"Hits: 0",
                f"Misses: 0",
                f"Hit Rate: No attacks yet",
                "",  # Spacer
                f"Critical Hits: 0",
                f"Critical Misses: 0",
                "",  # Spacer
                f"Biggest Hit: 0 damage",
                f"Party Knockouts: 0"
            ])
        
        # Render left column
        y_pos = y_start
        for stat_line in left_stats:
            if stat_line:  # Skip empty spacers
                stat_surface = stat_font.render(stat_line, True, WHITE)
                surface.blit(stat_surface, (left_column_x, y_pos))
            y_pos += line_height
        
        # Render right column
        y_pos = y_start
        for stat_line in right_stats:
            if stat_line:
                stat_surface = stat_font.render(stat_line, True, WHITE)
                surface.blit(stat_surface, (right_column_x, y_pos))
            y_pos += line_height
    
    def _render_other_stats(self, surface, game_state, fonts, start_x, start_y):
        """Render OTHER tab statistics"""
        stats = game_state.player_statistics
        
        # Title
        title_font = fonts.get('fantasy_large', fonts['header'])
        draw_centered_text(surface, "MISCELLANEOUS", title_font, start_y, BRIGHT_GREEN, 1024)
        
        # Stats display
        stat_font = fonts.get('fantasy_small', fonts['normal'])
        y_pos = start_y + 35
        line_height = 35
        
        # Other stats
        other_stats = [
            f"Times Saved Game: {stats['times_saved']}",
            "",  # Spacer for future stats
        ]
        
        # Render each stat line
        for stat_line in other_stats:
            if stat_line:  # Skip empty spacers
                stat_surface = stat_font.render(stat_line, True, WHITE)
                surface.blit(stat_surface, (start_x + 40, y_pos))
            y_pos += line_height
    
    def on_overlay_opened(self, game_state):
        """Called when statistics overlay opens"""
        super().on_overlay_opened(game_state)
        print("📊 Statistics overlay opened")
    
    def on_overlay_closed(self, game_state):
        """Called when statistics overlay closes"""
        super().on_overlay_closed(game_state)
        print("📊 Statistics overlay closed")

# ========================================
# COMPATIBILITY LAYER
# ========================================

# Create global instance
statistics_overlay_instance = None

def get_statistics_overlay():
    """Get the global statistics overlay instance"""
    global statistics_overlay_instance
    if statistics_overlay_instance is None:
        statistics_overlay_instance = StatisticsOverlay()
    return statistics_overlay_instance

def draw_statistics_screen(surface, game_state, fonts, images=None):
    """
    REQUIRED: Compatibility function for ScreenManager
    MUST match this exact signature
    """
    overlay = get_statistics_overlay()
    
    # Register with input handler on first render
    if not getattr(overlay, '_input_registered', False):
        try:
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'self' in frame.f_locals:
                screen_manager = frame.f_locals['self']
                if hasattr(screen_manager, 'input_handler'):
                    overlay.screen_manager = screen_manager
                    overlay._register_with_input_handler()
                    overlay._input_registered = True
        except:
            overlay._input_registered = True
    
    overlay.render(surface, game_state, fonts, images)
    return None

def handle_statistics_click(mouse_pos, result):
    """
    REQUIRED: Compatibility function for mouse handling
    MUST match this exact signature
    """
    overlay = get_statistics_overlay()
    return overlay.handle_mouse_click(mouse_pos)

def handle_statistics_keyboard_input(key, game_state):
    """
    REQUIRED: Compatibility function for keyboard handling
    MUST match this exact signature
    """
    overlay = get_statistics_overlay()
    return overlay.handle_keyboard_input(key)