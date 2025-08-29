"""
Terror in Redstone - Character Creation Screens
Contains all the character creation screen drawing functions
"""

import pygame
import os
# Import layout constants for new standardized system  
from utils.constants import (LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, 
                           LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                           LAYOUT_BUTTON_Y, LAYOUT_DIALOG_TEXT_Y, LAYOUT_BUTTON_CENTER_Y,
                           MALE_PORTRAITS_PATH, FEMALE_PORTRAITS_PATH
)

# Colors (local copy to avoid import issues)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
DARK_GRAY = (85, 85, 85)
LIGHT_GRAY = (200, 200, 200)
BRIGHT_GREEN = (85, 255, 85)
YELLOW = (255, 255, 85)
CYAN = (0, 255, 255)
RED = (170, 0, 0)
BROWN = (170, 85, 0)

# Drawing functions (duplicated here to avoid import issues)
def draw_text_with_shadow(surface, text, font, x, y, text_color=WHITE, shadow_color=DARK_GRAY, shadow_offset=3):
    """Draw text with a shadow effect"""
    shadow_surface = font.render(text, True, shadow_color)
    surface.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, (x, y))
    return text_surface.get_rect(x=x, y=y)

def draw_border(surface, x, y, width, height):
    """Draw a chunky retro border"""
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 3)
    pygame.draw.rect(surface, GRAY, (x+3, y+3, width-6, height-6), 2)

def draw_button(surface, x, y, width, height, text, font, pressed=False, selected=False):
    """Draw a retro-style button"""
    if selected:
        color = YELLOW
        border_color = WHITE
        text_color = BLACK
    else:
        color = DARK_GRAY if pressed else GRAY
        border_color = DARK_GRAY if pressed else WHITE
        text_color = (101, 67, 33)  # DARK_BROWN
    
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    surface.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height)

def calculate_best_font_for_button(text, max_width, fonts_to_try):
    """Calculate the best font size that fits in the button"""
    for font in fonts_to_try:
        text_surface = font.render(text, True, (101, 67, 33))  # DARK_BROWN
        if text_surface.get_width() <= max_width - 10:  # 10px padding
            return font
    return fonts_to_try[-1]  # Return smallest font if none fit

def draw_centered_text(surface, text, font, y_position, color=WHITE, screen_width=1024):
    """Draw text centered horizontally on the screen"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen_width//2, y_position))
    surface.blit(text_surface, text_rect)
    return text_rect

def create_input_box(surface, x, y, width, height, text, font, active=False, placeholder=""):
    """Draw a text input box with cursor support"""
    input_color = WHITE if active else LIGHT_GRAY
    pygame.draw.rect(surface, input_color, (x, y, width, height), 2)
    pygame.draw.rect(surface, BLACK, (x + 2, y + 2, width - 4, height - 4))
    
    if text:
        text_surface = font.render(text, True, WHITE)
    elif placeholder:
        text_surface = font.render(placeholder, True, GRAY)
    else:
        text_surface = font.render("", True, WHITE)
    
    text_rect = text_surface.get_rect(centery=y + height // 2, x=x + 10)
    surface.blit(text_surface, text_rect)
    
    if active and pygame.time.get_ticks() % 1000 < 500:
        cursor_x = text_rect.right + 5 if text else x + 10
        pygame.draw.line(surface, WHITE, (cursor_x, y + 10), (cursor_x, y + height - 10), 2)
    
    return pygame.Rect(x, y, width, height)

def draw_splash_screen(surface, fonts, images=None):
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

def draw_stats_screen(surface, game_state, fonts, images=None):
    """Draw the stat rolling screen"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, BRIGHT_GREEN)
    draw_centered_text(surface, "ROLL STATS", fonts.get('fantasy_medium', fonts['normal']), 120, YELLOW)
    
    # Stats display
    stats_y = 200
    stats = [
        f"STR: {game_state.temp_stats.get('strength', '--'):2}",
        f"DEX: {game_state.temp_stats.get('dexterity', '--'):2}",
        f"CON: {game_state.temp_stats.get('constitution', '--'):2}",
        f"INT: {game_state.temp_stats.get('intelligence', '--'):2}",
        f"WIS: {game_state.temp_stats.get('wisdom', '--'):2}",
        f"CHA: {game_state.temp_stats.get('charisma', '--'):2}"
    ]
    
    # Center the stats grid
    start_x = 350
    for i, stat in enumerate(stats):
        x = start_x + (i % 3) * 140
        y = stats_y + (i // 3) * 50
        stat_surface = fonts.get('fantasy_medium', fonts['normal']).render(stat, True, BRIGHT_GREEN)
        surface.blit(stat_surface, (x, y))
    
    # Buttons
    button_y = 320
    roll_button = draw_button(surface, 350, button_y, 160, 50, "ROLL STATS", 
                             fonts.get('fantasy_small', fonts['normal']))
    
    keep_button = None
    if game_state.stats_rolled:
        keep_button = draw_button(surface, 550, button_y, 160, 50, "KEEP STATS", 
                                 fonts.get('fantasy_small', fonts['normal']))
    
    # Instructions
    draw_centered_text(surface, "Roll your character's base attributes", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    
    return roll_button, keep_button

def draw_gender_screen(surface, game_state, fonts, images=None):
    """Draw the gender selection screen"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, BRIGHT_GREEN)
    draw_centered_text(surface, "CHOOSE GENDER", fonts.get('fantasy_medium', fonts['normal']), 120, YELLOW)
    
    # Gender buttons
    button_y = 280
    male_button = draw_button(surface, 340, button_y, 160, 70, "MALE", 
                             fonts.get('fantasy_medium', fonts['normal']))
    female_button = draw_button(surface, 560, button_y, 160, 70, "FEMALE", 
                               fonts.get('fantasy_medium', fonts['normal']))
    
    # Instructions
    draw_centered_text(surface, "Select your character's gender", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    
    return male_button, female_button

def draw_name_screen(surface, game_state, fonts, images=None):
    """Draw the name selection screen"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, BRIGHT_GREEN)
    draw_centered_text(surface, "CHOOSE NAME", fonts.get('fantasy_medium', fonts['normal']), 120, YELLOW)
    
    # Name buttons with dynamic sizing
    name_buttons = []
    button_width = 220
    button_height = 50
    button_y = 200
    
    # Calculate starting position to center all three buttons
    total_width = 3 * button_width + 2 * 20  # 20px spacing
    start_x = (1024 - total_width) // 2
    
    for i, name in enumerate(game_state.current_names):
        x = start_x + i * (button_width + 20)
        
        # Calculate best font for this name
        fonts_to_try = [
            fonts.get('fantasy_small', fonts['normal']),
            fonts.get('fantasy_tiny', fonts['small']),
            fonts.get('fantasy_micro', fonts['small'])
        ]
        best_font = calculate_best_font_for_button(name, button_width, fonts_to_try)
        
        button = draw_button(surface, x, button_y, button_width, button_height, name, best_font)
        name_buttons.append(button)
    
    # Action buttons
    action_button_y = 280
    new_names_button = draw_button(surface, 350, action_button_y, 160, 50, "NEW NAMES", 
                                  fonts.get('fantasy_small', fonts['normal']))
    custom_name_button = draw_button(surface, 550, action_button_y, 180, 50, "CUSTOM NAME", 
                                    fonts.get('fantasy_small', fonts['normal']))
    
    # Instructions
    draw_centered_text(surface, "Choose a name for your character", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    
    return name_buttons, new_names_button, custom_name_button

def draw_custom_name_screen(surface, game_state, fonts, images=None):
    """Draw the custom name input screen"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, BRIGHT_GREEN)
    draw_centered_text(surface, "ENTER CUSTOM NAME", fonts.get('fantasy_medium', fonts['normal']), 120, YELLOW)
    
    # Text input box
    input_box_width = 400
    input_box_height = 50
    input_box_x = (1024 - input_box_width) // 2
    input_box_y = 220
    
    input_box_rect = create_input_box(surface, input_box_x, input_box_y, input_box_width, input_box_height,
                                     game_state.custom_name_text, fonts.get('fantasy_medium', fonts['normal']),
                                     game_state.custom_name_active, "Type your name here...")
    
    # Buttons
    button_y = 320
    confirm_button = None
    if game_state.custom_name_text.strip():
        confirm_button = draw_button(surface, 350, button_y, 160, 50, "CONFIRM", 
                                    fonts.get('fantasy_small', fonts['normal']))
    
    back_button = draw_button(surface, 550, button_y, 160, 50, "BACK", 
                             fonts.get('fantasy_small', fonts['normal']))
    
    # Instructions
    draw_centered_text(surface, "Click in the box and type your character's name", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    
    return input_box_rect, confirm_button, back_button

def draw_name_confirm_screen(surface, game_state, fonts, images=None):
    """Draw the name confirmation screen"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, BRIGHT_GREEN)
    draw_centered_text(surface, "CONFIRM NAME", fonts.get('fantasy_medium', fonts['normal']), 120, YELLOW)
    
    # Show selected name
    draw_centered_text(surface, game_state.selected_name, fonts.get('fantasy_large', fonts['header']), 200, CYAN)
    
    # Buttons
    button_y = 280
    confirm_button = draw_button(surface, 350, button_y, 160, 50, "CONFIRM", 
                                fonts.get('fantasy_small', fonts['normal']))
    back_button = draw_button(surface, 550, button_y, 160, 50, "BACK", 
                             fonts.get('fantasy_small', fonts['normal']))
    
    # Instructions
    draw_centered_text(surface, "Is this the name you want for your character?", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    
    return confirm_button, back_button

def draw_gold_screen(surface, game_state, fonts, images=None):
    """Draw the gold rolling screen"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, BRIGHT_GREEN)
    draw_centered_text(surface, "STARTING GOLD", fonts.get('fantasy_medium', fonts['normal']), 120, YELLOW)
    
    # Show gold if rolled
    if 'gold' in game_state.character:
        draw_centered_text(surface, f"{game_state.character['gold']} Gold Pieces", 
                          fonts.get('fantasy_large', fonts['header']), 200, CYAN)
        button_text = "CONTINUE"
    else:
        draw_centered_text(surface, "Roll 3d6 x 5 for your starting gold", 
                          fonts.get('fantasy_medium', fonts['normal']), 200, WHITE)
        button_text = "ROLL GOLD"
    
    # Button
    button_y = 280
    roll_button = draw_button(surface, 450, button_y, 160, 50, button_text, 
                             fonts.get('fantasy_small', fonts['normal']))
    
    # Instructions
    draw_centered_text(surface, "Roll for your starting wealth", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    
    return roll_button

def draw_trinket_screen(surface, game_state, fonts, images=None):
    """Draw the trinket rolling screen"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, BRIGHT_GREEN)
    draw_centered_text(surface, "MYSTERIOUS TRINKET", fonts.get('fantasy_medium', fonts['normal']), 120, YELLOW)
    
    # Show trinket if rolled
    if 'trinket' in game_state.character:
        draw_centered_text(surface, game_state.character['trinket'], 
                          fonts.get('fantasy_medium', fonts['normal']), 200, CYAN)
        button_text = "CONTINUE"
    else:
        draw_centered_text(surface, "Roll for your mysterious trinket", 
                          fonts.get('fantasy_medium', fonts['normal']), 200, WHITE)
        button_text = "ROLL TRINKET"
    
    # Button
    button_y = 280
    roll_button = draw_button(surface, 450, button_y, 160, 50, button_text, 
                             fonts.get('fantasy_small', fonts['normal']))
    
    # Instructions
    draw_centered_text(surface, "Every adventurer carries something special", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    
    return roll_button

def draw_summary_screen(surface, game_state, fonts, images=None):
    """Draw the final character summary screen"""
    surface.fill(BLACK)
    
   # Character summary uses original dynamic layout (needs more space for data)
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))

    # Draw border box above image  
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title
    draw_centered_text(surface, "CHARACTER SUMMARY", fonts.get('fantasy_large', fonts['header']), 55, BRIGHT_GREEN)
    
    # Character info - tighter spacing
    y_pos = 90
    line_height = 28
    
    # Name and Gender
    name_surface = fonts.get('fantasy_medium', fonts['normal']).render(
        f"Name: {game_state.character['name']}", True, YELLOW)
    surface.blit(name_surface, (80, y_pos))
    y_pos += line_height
    
    gender_surface = fonts.get('fantasy_medium', fonts['normal']).render(
        f"Gender: {game_state.character['gender'].title()}", True, YELLOW)
    surface.blit(gender_surface, (80, y_pos))
    y_pos += line_height + 10
    
    # Stats
    stats_title = fonts.get('fantasy_medium', fonts['normal']).render("ATTRIBUTES", True, CYAN)
    surface.blit(stats_title, (80, y_pos))
    y_pos += line_height
    
    stats = [
        f"STR: {game_state.character['strength']:2d}",
        f"DEX: {game_state.character['dexterity']:2d}",
        f"CON: {game_state.character['constitution']:2d}",
        f"INT: {game_state.character['intelligence']:2d}",
        f"WIS: {game_state.character['wisdom']:2d}",
        f"CHA: {game_state.character['charisma']:2d}"
    ]
    
    for i, stat in enumerate(stats):
        x = 80 + (i % 3) * 140
        y = y_pos + (i // 3) * line_height
        stat_surface = fonts.get('fantasy_small', fonts['normal']).render(stat, True, WHITE)
        surface.blit(stat_surface, (x, y))
    
    y_pos += line_height * 2 + 15
    
    # Combat stats
    hp_surface = fonts.get('fantasy_medium', fonts['normal']).render(
        f"Hit Points: {game_state.character['hit_points']}", True, RED)
    surface.blit(hp_surface, (80, y_pos))
    y_pos += line_height
    
    gold_surface = fonts.get('fantasy_medium', fonts['normal']).render(
        f"Starting Gold: {game_state.character['gold']} gp", True, YELLOW)
    surface.blit(gold_surface, (80, y_pos))
    y_pos += line_height + 8
    
    # Equipment
    equipment_title = fonts.get('fantasy_medium', fonts['normal']).render("STARTING EQUIPMENT", True, CYAN)
    surface.blit(equipment_title, (80, y_pos))
    y_pos += line_height
    
    equipment = [
        "Leather Armor (AC 12)",
        "Longsword (1d8 damage)",
        "Shield (+2 AC)",
        game_state.character['trinket']
    ]
    
    for item in equipment:
        item_surface = fonts.get('fantasy_tiny', fonts['small']).render(f"• {item}", True, WHITE)
        surface.blit(item_surface, (80, y_pos))
        y_pos += line_height - 2
      
    # Button positioned with safe margin (original dynamic system)
    button_y = min(y_pos + 25, border_height - 65)
    start_button = draw_button(surface, 600, button_y, 160, 50, "START GAME", 
                              fonts.get('fantasy_small', fonts['normal']))
    
    return start_button

def finalize_character_creation(game_state):
    """
    Complete character creation by generating player JSON file
    This replaces the existing finalize_character() call
    """
    # Calculate final character stats (existing logic)
    game_state.character['hit_points'] = game_state.calculate_hp()
    
    # Add starting trinket to inventory (existing logic)
    if 'trinket' in game_state.character:
        game_state.inventory['items'].append(game_state.character['trinket'])
    
    # NEW: Create player JSON file from character data
    print("✅ Character creation finalized!")
    print(f"   🎭 Name: {game_state.character.get('name', 'Unknown')}")
    print(f"   💰 Gold: {game_state.character.get('gold', 0)}")
    print(f"   ❤️ Hit Points: {game_state.character.get('hit_points', 10)}")
    print(f"   🎒 Starting Items: {len(game_state.inventory.get('items', []))} items")
    
    return True

def draw_welcome_screen(surface, game_state, fonts, images=None):
    """Draw the welcome to Redstone screen"""
    surface.fill(BLACK)
    
    # Get character name
    character_name = game_state.character.get('name', 'Adventurer')
    
    # Use new standardized 3-zone layout
    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT

    # Draw border around image area
    draw_border(surface, 0, image_y, 1024, image_height)

    # Image fits within the border (accounting for border thickness)
    border_thickness = 6  # 3px outer + 3px spacing
    img_x = border_thickness
    img_y = LAYOUT_IMAGE_Y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    if images and images.get('welcome'):
        # Scale image to fit within border
        scaled_image = pygame.transform.scale(images['welcome'], (img_width, img_height))
        surface.blit(scaled_image, (img_x, img_y))
    else:
        # Placeholder
        pygame.draw.rect(surface, (50, 50, 100), (img_x, img_y, img_width, img_height))
        draw_centered_text(surface, "WELCOME TO REDSTONE", fonts.get('fantasy_large', fonts['header']), 
                          LAYOUT_IMAGE_Y + 255, WHITE)
        draw_centered_text(surface, "Generate welcome.jpg at 1024x510 pixels", 
                          fonts.get('tnr_small', fonts['small']), LAYOUT_IMAGE_Y + 290, CYAN)
    
   
    # Draw border around dialog area
    draw_border(surface, 20, LAYOUT_DIALOG_Y, 1024-40, LAYOUT_DIALOG_HEIGHT)
    
    # Welcome message
    text_y = LAYOUT_DIALOG_TEXT_Y
    draw_centered_text(surface, f"Welcome to Redstone,", fonts.get('fantasy_large', fonts['header']), 
                      text_y, BRIGHT_GREEN)
    draw_centered_text(surface, f"{character_name}!", fonts.get('fantasy_large', fonts['header']), 
                      text_y + 30, YELLOW)
    
    # Description text
    desc_y = text_y + 65
    draw_centered_text(surface, "The road to Redstone has been long and treacherous.", 
                      fonts.get('fantasy_small', fonts['normal']), desc_y, WHITE)
    draw_centered_text(surface, "You can smell woodsmoke and hear distant laughter from The Broken Blade tavern.", 
                      fonts.get('fantasy_small', fonts['normal']), desc_y + 22, WHITE)
    
    # Continue button
    # Button positioned with safe margin (original dynamic system)
    button_y = LAYOUT_BUTTON_CENTER_Y
    continue_button = draw_button(surface, 470, button_y, 120, 40, "CONTINUE", 
                                 fonts.get('fantasy_tiny', fonts['small']))
    
    return continue_button

def draw_portrait_selection_screen(surface, game_state, fonts, images=None):
    """Draw portrait selection screen"""
    surface.fill(BLACK)
    
    # Use standardized layout
    from utils.constants import (LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, 
                                LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                                LAYOUT_BUTTON_CENTER_Y)
    
    # Image area with portrait grid
    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT
    
    # Draw border around image area
    from utils.graphics import draw_border
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Dialog area
    dialog_y = LAYOUT_DIALOG_Y
    dialog_height = LAYOUT_DIALOG_HEIGHT
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # Instructions
    from utils.graphics import draw_centered_text
    text_y = dialog_y + 20
    draw_centered_text(surface, "Choose your character's appearance:", 
                      fonts.get('fantasy_medium', fonts['normal']), text_y, WHITE)
    
    desc_y = text_y + 30
    draw_centered_text(surface, "Click a portrait to select, then click CONTINUE", 
                      fonts.get('fantasy_small', fonts['normal']), desc_y, YELLOW)
    
    # Portrait grid (5 portraits, load images or show numbered placeholders)
    portrait_size = 110
    total_width = 5 * portrait_size + 4 * 20  # 5 portraits + 4 gaps of 20px
    start_x = (1024 - total_width) // 2  # Center the row
    portrait_y = image_y + 100  # Position in image area

    portrait_buttons = []
    gender = game_state.character.get('gender', 'male')
    if gender == 'male':
        portrait_dir = MALE_PORTRAITS_PATH
    else:
        portrait_dir = FEMALE_PORTRAITS_PATH

    for i in range(5):
        portrait_x = start_x + i * (portrait_size + 20)
        portrait_rect = pygame.Rect(portrait_x, portrait_y, portrait_size, portrait_size)
        
        # Try to load portrait image
        filename = f"player_{gender}_{i+1:02d}.jpg"
        filepath = os.path.join(portrait_dir, filename)
        
        portrait_loaded = False
        if os.path.exists(filepath):
            try:
                portrait_img = pygame.image.load(filepath)
                portrait_img = pygame.transform.scale(portrait_img, (portrait_size, portrait_size))
                surface.blit(portrait_img, (portrait_x, portrait_y))
                portrait_loaded = True
                # Store the actual filename for this portrait option
                if not hasattr(game_state, 'available_portraits'):
                    game_state.available_portraits = {}
                game_state.available_portraits[i] = filename if portrait_loaded else None
            except:
                pass
        # Store None for failed portraits
        if not hasattr(game_state, 'available_portraits'):
            game_state.available_portraits = {}
        if i not in game_state.available_portraits:
            game_state.available_portraits[i] = None


        # If no portrait loaded, show numbered placeholder
        if not portrait_loaded:
            pygame.draw.rect(surface, (60, 40, 30), portrait_rect)  # Brown background
            number_text = fonts.get('fantasy_large', fonts['header']).render(str(i+1), True, WHITE)
            number_rect = number_text.get_rect(center=portrait_rect.center)
            surface.blit(number_text, number_rect)
        
        # Draw border (highlight if selected)
        if getattr(game_state, 'selected_portrait_index', -1) == i:
            border_color = YELLOW
            border_width = 4
        else:
            border_color = WHITE
            border_width = 2
        
        pygame.draw.rect(surface, border_color, portrait_rect, border_width)
        portrait_buttons.append(portrait_rect)
    
    # Buttons
    from utils.graphics import draw_button
    button_y = LAYOUT_BUTTON_CENTER_Y
    
    back_button = draw_button(surface, 300, button_y, 120, 40, "BACK", 
                             fonts.get('fantasy_small', fonts['normal']))
    continue_button = draw_button(surface, 600, button_y, 120, 40, "CONTINUE", 
                                 fonts.get('fantasy_small', fonts['normal']))
    
    return portrait_buttons, back_button, continue_button
