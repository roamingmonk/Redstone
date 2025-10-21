# screens/title_menu.py
"""
Title Screen and Main Menu - Professional RPG start experience
"""

import pygame
from utils.constants import (WHITE, BLACK, YELLOW, DARK_GRAY, CYAN, GRAY, BROWN)
from utils.graphics import draw_border, draw_button, draw_centered_text
from utils.animation import SpriteAnimation

# Drawing functions (duplicated here to avoid import issues)
def draw_text_with_shadow(surface, text, font, x, y, text_color=WHITE, shadow_color=DARK_GRAY, shadow_offset=3):
    """Draw text with a shadow effect"""
    shadow_surface = font.render(text, True, shadow_color)
    surface.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, (x, y))
    return text_surface.get_rect(x=x, y=y)

def draw_title_screen(surface, game_state, fonts, images=None):
    """Draw the game splash screen"""
    surface.fill(BLACK)

    if not hasattr(game_state, 'title_animations'):
        game_state.title_animations = {
            'campfire': SpriteAnimation(
                'assets/images/sprites/fire/campfire_animation.png', 
                10, (64, 64), 300
            ),
            'torch_left': SpriteAnimation(
                'assets/images/sprites/fire/torch_animation.png', 
                4,  # Adjust to your torch frame count
                (32, 32),  # Typical torch size - adjust if different
                350  # Slightly different timing for natural feel
            ),
            'torch_right': SpriteAnimation(
                'assets/images/sprites/fire/torch_animation.png', 
                4,  # Same frame count
                (32, 32),  # Same size
                280  # Different timing for organic atmosphere
            )
        }
    
    # Update animations
    for animation in game_state.title_animations.values():
        animation.update()

    # Create large title font for dramatic effect
    try:
        title_font_large = pygame.font.SysFont('timesnewroman', 68, bold=True, italic=True)
    except:
        title_font_large = fonts.get('title', pygame.font.Font(None, 68))
    
    # Calculate proper centering for titles
    title_y = 220
    
    # Draw title with shadows
    draw_text_with_shadow(surface, "TERROR IN", title_font_large, 
                         (1024 - title_font_large.size("TERROR IN")[0]) // 2, 
                         title_y, WHITE, DARK_GRAY, 4)
    
    draw_text_with_shadow(surface, "REDSTONE", title_font_large, 
                         (1024 - title_font_large.size("REDSTONE")[0]) // 2, 
                         title_y + 80, YELLOW, BROWN, 4)
    

    # Subtitle
    subtitle_y = title_y + 180
    draw_centered_text(surface, "A Classic RPG Adventure", 
                      fonts.get('tnr_normal', fonts['normal']), 
                      subtitle_y, CYAN)
    
    # Instructions
    instruction_y = 768 - 80
    draw_centered_text(surface, "Press ENTER to Start (or click anywhere)", 
                      fonts.get('tnr_normal', fonts['normal']), 
                      instruction_y, WHITE)
    
    # Decorative borders
    pygame.draw.rect(surface, WHITE, (100, 150, 1024-200, 400), 3)
    pygame.draw.rect(surface, GRAY, (105, 155, 1024-210, 390), 1)

    # Draw torches flanking the title
    torch_left_x = 200  # Left side of border area
    torch_left_y = 250  # Near title level
    game_state.title_animations['torch_left'].draw(surface, torch_left_x, torch_left_y)

    torch_right_x = 1024 - 180 - 32  # Right side, accounting for torch width
    torch_right_y = 250  # Same height as left torch
    game_state.title_animations['torch_right'].draw(surface, torch_right_x, torch_right_y)

def draw_company_splash_screen(surface, game_state, fonts, images=None):
    """
    Draw the company/developer splash screen - simple and clean
    """
    surface.fill(BLACK)    
            
    # Initialize star animations if not already done
    if not hasattr(game_state, 'menu_stars'):
        game_state.menu_stars = {
            'star_1': SpriteAnimation(
                'assets/images/sprites/landscape/star_twinkle_1.png',
                13, (32, 32), 100  # 13 frames, 32x32 size, 100ms per frame
            ),
            'star_2': SpriteAnimation(
                'assets/images/sprites/landscape/star_twinkle_1.png',
                13, (32, 32), 120  # Slightly different timing
            ),
            'star_3': SpriteAnimation(
                'assets/images/sprites/landscape/star_twinkle_1.png',
                13, (32, 32), 80  # Even faster twinkle
            )
        }
    
    # Update star animations
    for animation in game_state.menu_stars.values():
        animation.update()

    if not hasattr(game_state, 'title_animations'):
            game_state.title_animations = {
                'campfire': SpriteAnimation(
                    'assets/images/sprites/fire/campfire_animation.png', 
                    10, (64, 64), 300
                )
            }
    
    # Update animations
    for animation in game_state.title_animations.values():
        animation.update()

    # Simple company presentation
    company_y = 300
    
    draw_centered_text(surface, "A Game by", 
                      fonts.get('fantasy_medium', fonts['normal']), 
                      company_y, WHITE)
    
    # Your name/company name
    name_y = company_y + 50
    draw_centered_text(surface, "Roaming Monk Games", 
                       fonts.get('fantasy_large', fonts['header']),
                    name_y, YELLOW)
        
    # Year
    year_y = name_y + 80
    draw_centered_text(surface, "2025", 
                      fonts.get('fantasy_small', fonts['normal']), 
                      year_y, WHITE)
    
    # Continue instruction (smaller, less prominent)
    continue_y = 600
    draw_centered_text(surface, "Press enter or click mouse to continue...", 
                      fonts.get('fantasy_small', fonts['normal']), 
                      continue_y, (128, 128, 128))  # Gray text    
    

    # Draw twinkling stars
    star_positions = [
        (120, 58),   # Top left
        (810, 60),   # Top right
        (500, 25),   # Top center
        (200, 400),   
        (905, 490)
    ]
    
    for i, (star_x, star_y) in enumerate(star_positions):
        if i < len(game_state.menu_stars):
            star_key = f'star_{i+1}'
            game_state.menu_stars[star_key].draw(surface, star_x, star_y)



    campfire_x = (1024 - 64)  //2 
    campfire_y = 500
    game_state.title_animations['campfire'].draw(surface, campfire_x, campfire_y)

def draw_main_menu(surface, game_state, fonts, images=None):
    """
    Draw the main menu with New Game, Load Game options
    """
    surface.fill(BLACK)
    
    # Initialize star animations if not already done
    if not hasattr(game_state, 'menu_stars'):
        
        game_state.menu_stars = {
            'star_1': SpriteAnimation(
                'assets/images/sprites/landscape/star_twinkle_1.png',
                13, (32, 32), 100  # 13 frames, 32x32 size, 100ms per frame
            ),
            'star_2': SpriteAnimation(
                'assets/images/sprites/landscape/star_twinkle_1.png',
                13, (32, 32), 120  # Slightly different timing
            ),
            'star_3': SpriteAnimation(
                'assets/images/sprites/landscape/star_twinkle_1.png',
                13, (32, 32), 80  # Even faster twinkle
            )
        }
    
    # Update star animations
    for animation in game_state.menu_stars.values():
        animation.update()

 # Create large title font for dramatic effect
    try:
        title_font_large = pygame.font.SysFont('timesnewroman', 68, bold=True, italic=True)
    except:
        title_font_large = fonts.get('title', pygame.font.Font(None, 68))

    # Title
    title_y = 100
    
    # Draw title with shadows
    draw_text_with_shadow(surface, "TERROR IN", title_font_large, 
                         (1024 - title_font_large.size("TERROR IN")[0]) // 2, 
                         title_y, WHITE, DARK_GRAY, 4)
    
    draw_text_with_shadow(surface, "REDSTONE", title_font_large, 
                         (1024 - title_font_large.size("REDSTONE")[0]) // 2, 
                         title_y + 80, YELLOW, BROWN, 4)
    
       
    # Menu buttons
    button_y = 300
    button_width = 200
    button_height = 60
    button_spacing = 80
    
    # Center the buttons
    start_x = (1024 - button_width) // 2
    
    new_game_button = draw_button(surface, start_x, button_y, 
                                 button_width, button_height,
                                 "NEW GAME", fonts.get('fantasy_medium', fonts['normal']))
    
    load_game_button = draw_button(surface, start_x, button_y + button_spacing, 
                                  button_width, button_height,
                                  "LOAD GAME", fonts.get('fantasy_medium', fonts['normal']))
    
    quit_button = draw_button(surface, start_x, button_y + (button_spacing * 2), 
                             button_width, button_height,
                             "QUIT", fonts.get('fantasy_medium', fonts['normal']))
    
    # Draw twinkling stars
    star_positions = [
        (100, 50),   # Top left
        (820, 70),   # Top right
        (512, 25),   # Top center
    ]
    
    for i, (star_x, star_y) in enumerate(star_positions):
        if i < len(game_state.menu_stars):
            star_key = f'star_{i+1}'
            game_state.menu_stars[star_key].draw(surface, star_x, star_y)


    return new_game_button, load_game_button, quit_button



def get_game_title_interactables():
    """
    Semantic clickable regions for the game title screen
    Click anywhere to advance to developer splash
    """
    return [
        {
            'action': 'START_GAME',
            'rect': (0, 0, 1024, 768),  # Full screen clickable
            'payload': {'target_screen': 'developer_splash'},
            'priority': 0
        }
    ]

def get_developer_splash_interactables():
    """
    Semantic clickable regions for the developer splash screen
    Click anywhere to advance to main menu
    """
    return [
        {
            'action': 'CONTINUE',
            'rect': (0, 0, 1024, 768),  # Full screen clickable
            'payload': {'target_screen': 'main_menu'},
            'priority': 0
        }
    ]

def get_main_menu_interactables():
    """
    Semantic clickable regions for the main menu
    Returns regions for the three buttons
    """
    # Button layout (matching draw_main_menu)
    button_y = 300
    button_width = 200
    button_height = 60
    button_spacing = 80
    start_x = (1024 - button_width) // 2
    
    return [
        {
            'action': 'NEW_GAME',
            'rect': (start_x, button_y, button_width, button_height),
            'payload': {'target_screen': 'stats'},
            'priority': 1
        },
        {
            'action': 'LOAD_GAME', 
            'rect': (start_x, button_y + button_spacing, button_width, button_height),
            'payload': {'open_load_screen': True},
            'priority': 1
        },
        {
            'action': 'QUIT_GAME',
            'rect': (start_x, button_y + (button_spacing * 2), button_width, button_height),
            'payload': {'quit': True},
            'priority': 1
        }
    ]