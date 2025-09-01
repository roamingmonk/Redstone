# screens/character_advancement.py
"""
Character Advancement Screen - Level Up Interface
Handles character progression and leveling up
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text

def draw_character_advancement(surface, game_state, fonts, controller=None):
    """
    Draw character advancement/level up screen
    
    Returns:
        dict: UI elements for interaction
    """
    surface.fill(BLACK)
    
    # Use standardized layout
    draw_border(surface, 20, 20, 1024-40, 768-40)
    
    result = {
        'level_up_button': None,
        'close_button': None,
        'xp_display': None,
        'class_abilities': []
    }
    
    # Title
    draw_centered_text(surface, "CHARACTER ADVANCEMENT", 
                      fonts.get('fantasy_large', fonts['header']), 60, BRIGHT_GREEN)
    
    # Get character engine for data
    from game_logic.character_engine import get_character_engine
    engine = get_character_engine()
    
    if not engine:
        draw_centered_text(surface, "Character engine not available", 
                          fonts.get('fantasy_medium', fonts['normal']), 300, RED)
        return result
    
    # Character summary
    char = game_state.character
    char_name = char.get('name', 'Unknown')
    char_class = char.get('class', 'fighter').title()
    current_level = char.get('level', 1)
    current_xp = char.get('experience', 0)
    current_hp = char.get('hit_points', 10)
    
    y_pos = 120
    
    # Character info
    char_info = fonts.get('fantasy_medium', fonts['normal']).render(
        f"{char_name} the {char_class}", True, YELLOW)
    surface.blit(char_info, (80, y_pos))
    y_pos += 35
    
    level_info = fonts.get('fantasy_small', fonts['normal']).render(
        f"Level {current_level}    HP: {current_hp}    XP: {current_xp}", True, WHITE)
    surface.blit(level_info, (80, y_pos))
    y_pos += 50
    
    # XP Requirements table
    xp_table_title = fonts.get('fantasy_medium', fonts['normal']).render(
        "EXPERIENCE REQUIREMENTS", True, CYAN)
    surface.blit(xp_table_title, (80, y_pos))
    y_pos += 30
    
    # XP requirements for levels 1-5
    xp_requirements = {1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500}
    
    for level in range(1, 6):
        required_xp = xp_requirements[level]
        if level == current_level:
            color = BRIGHT_GREEN  # Current level
            marker = "► "
        elif level < current_level:
            color = GRAY  # Completed levels
            marker = "✓ "
        else:
            color = WHITE  # Future levels
            marker = "  "
        
        level_text = fonts.get('fantasy_tiny', fonts['small']).render(
            f"{marker}Level {level}: {required_xp:,} XP", True, color)
        surface.blit(level_text, (100, y_pos))
        y_pos += 22
    
    y_pos += 20
    
    # Current abilities
    abilities_title = fonts.get('fantasy_medium', fonts['normal']).render(
        "CURRENT ABILITIES", True, CYAN)
    surface.blit(abilities_title, (80, y_pos))
    y_pos += 30
    
    current_abilities = char.get('abilities', [])
    if current_abilities:
        for ability in current_abilities[:8]:  # Show max 8 abilities
            ability_text = fonts.get('fantasy_tiny', fonts['small']).render(
                f"• {ability}", True, WHITE)
            surface.blit(ability_text, (100, y_pos))
            y_pos += 20
    else:
        no_abilities_text = fonts.get('fantasy_tiny', fonts['small']).render(
            "No special abilities yet", True, GRAY)
        surface.blit(no_abilities_text, (100, y_pos))
        y_pos += 20
    
    y_pos += 30
    
    # Level up section
    can_level_up = engine.can_level_up()
    
    if can_level_up:
        next_level = current_level + 1
        
        # Level up available!
        level_up_title = fonts.get('fantasy_medium', fonts['normal']).render(
            "🎊 LEVEL UP AVAILABLE! 🎊", True, BRIGHT_GREEN)
        title_rect = level_up_title.get_rect(center=(512, y_pos))
        surface.blit(level_up_title, title_rect)
        y_pos += 40
        
        # Show what player will gain
        preview_text = fonts.get('fantasy_small', fonts['normal']).render(
            f"Ready to advance to Level {next_level}!", True, YELLOW)
        preview_rect = preview_text.get_rect(center=(512, y_pos))
        surface.blit(preview_text, preview_rect)
        y_pos += 30
        
        # Preview new abilities
        class_data = engine._get_class_data(char_class.lower())
        if class_data and 'abilities' in class_data:
            new_abilities = class_data['abilities'].get(f'level_{next_level}', [])
            if new_abilities:
                new_abilities_text = fonts.get('fantasy_tiny', fonts['small']).render(
                    f"New abilities: {', '.join(new_abilities)}", True, CYAN)
                abilities_rect = new_abilities_text.get_rect(center=(512, y_pos))
                surface.blit(new_abilities_text, abilities_rect)
                y_pos += 25
        
        # Level up button
        result['level_up_button'] = draw_button(surface, 400, y_pos + 20, 224, 50, 
                                               "LEVEL UP!", fonts.get('fantasy_medium', fonts['normal']))
    
    else:
        # Show XP needed for next level
        next_level = min(current_level + 1, 5)  # Cap at level 5
        if next_level <= 5:
            xp_needed = xp_requirements[next_level] - current_xp
            
            xp_needed_text = fonts.get('fantasy_small', fonts['normal']).render(
                f"XP needed for Level {next_level}: {xp_needed:,}", True, WHITE)
            xp_rect = xp_needed_text.get_rect(center=(512, y_pos))
            surface.blit(xp_needed_text, xp_rect)
            y_pos += 30
            
            # Progress bar
            progress = current_xp / xp_requirements[next_level]
            bar_width = 400
            bar_height = 20
            bar_x = (1024 - bar_width) // 2
            bar_y = y_pos
            
            # Background bar
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                pygame.draw.rect(surface, BRIGHT_GREEN, (bar_x, bar_y, progress_width, bar_height))
            
            # Border
            pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            
            y_pos += 40
        else:
            max_level_text = fonts.get('fantasy_medium', fonts['normal']).render(
                "Maximum level reached!", True, YELLOW)
            max_rect = max_level_text.get_rect(center=(512, y_pos))
            surface.blit(max_level_text, max_rect)
    
    # Close button
    result['close_button'] = draw_button(surface, 50, 680, 120, 40, 
                                        "CLOSE", fonts.get('fantasy_small', fonts['normal']))
    
    # XP sources info (right side)
    info_x = 600
    info_y = 160
    
    xp_sources_title = fonts.get('fantasy_medium', fonts['normal']).render(
        "EXPERIENCE SOURCES", True, CYAN)
    surface.blit(xp_sources_title, (info_x, info_y))
    info_y += 35
    
    xp_sources = [
        "Combat Victories: 100+ XP",
        "Quest Completion: 150-1000 XP",
        "Skill Achievements: 50 XP",
        "Gambling Streaks (3+): 60-100 XP"
    ]
    
    for source in xp_sources:
        source_text = fonts.get('fantasy_tiny', fonts['small']).render(
            f"• {source}", True, WHITE)
        surface.blit(source_text, (info_x + 20, info_y))
        info_y += 22
    
    info_y += 30
    
    # Class progression info
    class_progression_title = fonts.get('fantasy_medium', fonts['normal']).render(
        f"{char_class.upper()} PROGRESSION", True, CYAN)
    surface.blit(class_progression_title, (info_x, info_y))
    info_y += 35
    
    # Show class-specific progression
    class_data = engine._get_class_data(char_class.lower())
    if class_data and 'abilities' in class_data:
        for level in range(1, 6):
            level_abilities = class_data['abilities'].get(f'level_{level}', [])
            if level_abilities:
                level_color = BRIGHT_GREEN if level == current_level else (GRAY if level < current_level else WHITE)
                level_text = fonts.get('fantasy_tiny', fonts['small']).render(
                    f"Level {level}: {', '.join(level_abilities)}", True, level_color)
                surface.blit(level_text, (info_x + 10, info_y))
                info_y += 18
    
    return result

def handle_character_advancement_click(mouse_pos, result, game_state, controller=None):
    """
    Handle mouse clicks on character advancement screen
    
    Args:
        mouse_pos: Tuple of (x, y) mouse position
        result: UI elements from draw_character_advancement
        game_state: Current game state
        controller: Game controller reference
        
    Returns:
        bool: True if click was handled
    """
    # Handle level up button
    if result.get('level_up_button') and result['level_up_button'].collidepoint(mouse_pos):
        from game_logic.character_engine import get_character_engine
        engine = get_character_engine()
        
        if engine:
            level_up_results = engine.level_up()
            if level_up_results:
                # Show level up results
                char_name = game_state.character.get('name', 'Hero')
                new_level = level_up_results['new_level']
                hp_gain = level_up_results['hp_gain']
                abilities_gained = level_up_results.get('abilities_gained', [])
                
                print(f"🎊 {char_name} reached Level {new_level}!")
                print(f"💚 Gained {hp_gain} hit points!")
                
                if abilities_gained:
                    print(f"📚 New abilities: {', '.join(abilities_gained)}")
                
                # Set flag for potential UI notification
                game_state.level_up_notification = {
                    'new_level': new_level,
                    'hp_gain': hp_gain,
                    'abilities': abilities_gained,
                    'timestamp': pygame.time.get_ticks()
                }
        
        return True
    
    # Handle close button
    if result.get('close_button') and result['close_button'].collidepoint(mouse_pos):
        game_state.character_advancement_open = False
        return True
    
    return False

def handle_character_advancement_keys(event, game_state, controller=None):
    """
    Handle keyboard input for character advancement screen
    
    Args:
        event: Pygame event
        game_state: Current game state
        controller: Game controller reference
        
    Returns:
        bool: True if event was handled
    """
    if event.type == pygame.KEYDOWN:
        # ESC closes advancement screen
        if event.key == pygame.K_ESCAPE:
            game_state.character_advancement_open = False
            return True
        
        # ENTER triggers level up if available
        if event.key == pygame.K_RETURN:
            from game_logic.character_engine import get_character_engine
            engine = get_character_engine()
            
            if engine and engine.can_level_up():
                level_up_results = engine.level_up()
                if level_up_results:
                    print(f"🎊 Leveled up via ENTER key!")
                return True
    
    return False

