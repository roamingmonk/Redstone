# screens/title_menu.py
"""
Title Screen and Main Menu - Professional RPG start experience
"""

import pygame
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text
#from screens.title_menu import draw_title_screen, draw_company_splash_screen, draw_main_menu

BROWN = (170, 85, 0)

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




def draw_company_splash_screen(surface, game_state, fonts, images=None):
    """
    Draw the company/developer splash screen - simple and clean
    """
    surface.fill(BLACK)
    
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
    draw_centered_text(surface, "Press any key to continue...", 
                      fonts.get('fantasy_small', fonts['normal']), 
                      continue_y, (128, 128, 128))  # Gray text    

def draw_main_menu(surface, game_state, fonts, images=None):
    """
    Draw the main menu with New Game, Load Game options
    """
    surface.fill(BLACK)
    
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