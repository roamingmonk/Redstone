"""
Terror in Redstone - Character Creation Screens
Contains all the character creation screen drawing functions
"""

import pygame
import json
import os
from game_logic.character_engine import get_character_engine
# Import layout constants for new standardized system  
from utils.constants import (LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, 
                           LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                           LAYOUT_BUTTON_Y, LAYOUT_DIALOG_TEXT_Y, LAYOUT_BUTTON_CENTER_Y,
                           MALE_PORTRAITS_PATH, FEMALE_PORTRAITS_PATH,
                           #Colors
                           WHITE, DARK_GRAY, GRAY, BLACK, SOFT_YELLOW, BROWN,
                           CYAN, WARNING_RED, TITLE_GREEN, YELLOW,
                           #Buttons
                           BUTTON_SIZES, SCREEN_WIDTH
)
from utils.graphics import (draw_centered_text, draw_border, draw_button, 
                            create_input_box, draw_text_with_shadow, 
                            calculate_best_font_for_button)

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

def draw_cavia_warning_screen(surface, game_state, fonts, images=None):
    """Draw warning screen when Cavia portrait selected"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title
    draw_centered_text(surface, "WAIT... IS THAT A GUINEA PIG?!", 
                      fonts.get('fantasy_large', fonts['header']), 100, SOFT_YELLOW)
    
    # Warning text with humor
    text_y = 160
    draw_centered_text(surface, "Uh, just so you know...", 
                      fonts.get('fantasy_medium', fonts['normal']), text_y, WHITE)
    draw_centered_text(surface, "If you select this portrait, your Strength and Constitution", 
                      fonts.get('fantasy_small', fonts['normal']), text_y + 40, WHITE)
    draw_centered_text(surface, "will be capped at 10. You're a guinea pig, not a Human Fighter!", 
                      fonts.get('fantasy_small', fonts['normal']), text_y + 65, WHITE)
    
    draw_centered_text(surface, "On the bright side:", 
                      fonts.get('fantasy_small', fonts['normal']), text_y + 110, TITLE_GREEN)
    draw_centered_text(surface, "• You get unique dialogue options", 
                      fonts.get('fantasy_tiny', fonts['small']), text_y + 135, WHITE)
    draw_centered_text(surface, "• NPCs will be... intrigued", 
                      fonts.get('fantasy_tiny', fonts['small']), text_y + 155, WHITE)
    draw_centered_text(surface, "• You will get a bonus roll on your Charisma attribute, since you are cute and fluffy.", 
                      fonts.get('fantasy_tiny', fonts['small']), text_y + 175, WHITE)
    
    # Buttons
    button_y = text_y + 230
    back_button = draw_button(surface, 280, button_y, 200, 50, "PICK AGAIN", 
                             fonts.get('fantasy_small', fonts['normal']))
    
    confirm_button = draw_button(surface, 520, button_y, 200, 50, "I'M A GUINEA PIG!", 
                                fonts.get('fantasy_small', fonts['normal']))
    
    return back_button, confirm_button

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
                         title_y + 80, SOFT_YELLOW, BROWN, 4)
    
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
    # SELF-REGISTRATION: Register this screen's clickable regions
    # This ensures InputHandler knows about our buttons
    
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    
    # Title and subtitle
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, TITLE_GREEN)
    draw_centered_text(surface, "ROLL STATS", fonts.get('fantasy_medium', fonts['normal']), 120, SOFT_YELLOW)
    
    # Load class information from JSON
    class_file = os.path.join("data", "player", "character_classes.json")
    try:
        with open(class_file, 'r') as f:
            class_data = json.load(f)
        
        # Get current character class (defaults to fighter for now)
        current_class = game_state.character.get('class', 'fighter')
        class_info = class_data["character_classes"].get(current_class, {})
        
        class_name = class_info.get("name", "Fighter")
        primary_abilities = class_info.get("primary_abilities", ["strength", "constitution"])
        
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        # Fallback if JSON file is missing or corrupted
        class_name = "Fighter"
        primary_abilities = ["strength", "constitution"]

    # Display class information
    draw_centered_text(surface, class_name.upper(), fonts.get('fantasy_medium', fonts['normal']), 160, TITLE_GREEN)

    # Format primary abilities for display
    primary_text = "Primary Attributes: " + ", ".join([ability.title() for ability in primary_abilities])
    draw_centered_text(surface, primary_text, fonts.get('fantasy_small', fonts['normal']), 185, SOFT_YELLOW)

    # Stats display
    stats_y = 200
    stats = [
        f"STR: {game_state.character.get('strength', '--'):2}",
        f"DEX: {game_state.character.get('dexterity', '--'):2}",
        f"CON: {game_state.character.get('constitution', '--'):2}",
        f"INT: {game_state.character.get('intelligence', '--'):2}",
        f"WIS: {game_state.character.get('wisdom', '--'):2}",
        f"CHA: {game_state.character.get('charisma', '--'):2}"
    ]
    
    # Store primary abilities for highlighting (use the variables from the JSON loading above)
    primary_stat_prefixes = [ability[:3].lower() for ability in primary_abilities]  # ["str", "con"]

    # Center the stats grid with highlighting
    start_x = 350
    for i, stat in enumerate(stats):
        stat_name = stat.split(':')[0].lower()  # "STR: 15" -> "str"
        
        # Choose color and prefix based on whether it's a primary ability
        if stat_name in primary_stat_prefixes:
            color = TITLE_GREEN  # Highlight primary stats
            display_stat = f"*{stat}"  # Add asterisk
        else:
            color = WHITE
            display_stat = f" {stat}"  # Space for alignment
        
        x = start_x + (i % 3) * 140
        y = stats_y + (i // 3) * 50
        stat_surface = fonts.get('fantasy_medium', fonts['normal']).render(display_stat, True, color)
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
    draw_centered_text(surface, "Roll your character's base attributes for a Fighter", 
                      fonts.get('tnr_small', fonts['small']), 435, WHITE)
    draw_centered_text(surface, "Green stats with * are most important for your class", 
                  fonts.get('tnr_small', fonts['small']), 415, WHITE)
    
    return roll_button, keep_button

def draw_stats_confirm_low_screen(surface, game_state, fonts, images=None):
    """Draw confirmation screen for low primary stats"""
    surface.fill(BLACK)
    
    # Draw character creation table image at bottom
    if images and images.get('character_table'):
        image_height = images['character_table'].get_height()
        surface.blit(images['character_table'], (0, 768 - image_height))
    
    # Draw border box above image
    border_height = 768 - (images['character_table'].get_height() if images and images.get('character_table') else 100) - 40
    draw_border(surface, 30, 30, 1024-60, border_height)
    # Check if we're showing snarky comment or initial warning
    if game_state.temp_data.get("showing_snarky_comment", False):
        # Load snarky comment from temp_data
        comment = game_state.temp_data.get("snarky_comment", {})
        
        title = comment.get("title", "WELL, ALRIGHT THEN...")
        main_text = comment.get("main_text", "You're brave, I'll give you that!")
        sub_text = comment.get("sub_text", "Good luck in combat with those stats.")
        
        # Display snarky comment
        draw_centered_text(surface, title, fonts.get('fantasy_large', fonts['header']), 120, SOFT_YELLOW)
        draw_centered_text(surface, main_text, fonts.get('fantasy_medium', fonts['normal']), 180, WHITE)
        draw_centered_text(surface, sub_text, fonts.get('fantasy_small', fonts['normal']), 220, WHITE)
        draw_centered_text(surface, "Click anywhere to continue...", 
                  fonts.get('fantasy_small', fonts['normal']), 260, TITLE_GREEN)
        
        # No buttons during snarky comment display
        return None, None
    else:
        # Title
        draw_centered_text(surface, "ARE YOU SURE?", fonts.get('fantasy_large', fonts['header']), 120, WARNING_RED)
        
        # Warning message
        low_abilities = game_state.temp_data.get("low_primaries", ["Primary Abilities"])
        abilities_text = ", ".join(low_abilities)
        
        draw_centered_text(surface, f"Your {abilities_text} scores are quite low!", 
                        fonts.get('fantasy_medium', fonts['normal']), 180, SOFT_YELLOW)
        draw_centered_text(surface, "This will make your Fighter less effective in combat.", 
                        fonts.get('fantasy_small', fonts['normal']), 210, WHITE)
        draw_centered_text(surface, "Consider rerolling for better primary abilities.", 
                        fonts.get('fantasy_small', fonts['normal']), 235, WHITE)
        
        # Buttons
        button_y = 280
        reroll_button = draw_button(surface, 300, button_y, 160, 50, "REROLL", 
                                fonts.get('fantasy_small', fonts['normal']))
        
        proceed_button = draw_button(surface, 500, button_y, 160, 50, "PROCEED", 
                                    fonts.get('fantasy_small', fonts['normal']))
        
        return reroll_button, proceed_button

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
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, TITLE_GREEN)
    draw_centered_text(surface, "CHOOSE GENDER", fonts.get('fantasy_medium', fonts['normal']), 120, SOFT_YELLOW)
    
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
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, TITLE_GREEN)
    draw_centered_text(surface, "CHOOSE NAME", fonts.get('fantasy_medium', fonts['normal']), 120, SOFT_YELLOW)
    
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
    draw_centered_text(surface, "Choose a name for your character or click New Name/Custom Name for more options", 
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
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, TITLE_GREEN)
    draw_centered_text(surface, "ENTER CUSTOM NAME", fonts.get('fantasy_medium', fonts['normal']), 120, SOFT_YELLOW)
    
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
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, TITLE_GREEN)
    draw_centered_text(surface, "CONFIRM NAME", fonts.get('fantasy_medium', fonts['normal']), 120, SOFT_YELLOW)
    
    # Show selected name
    draw_centered_text(surface, game_state.selected_name, fonts.get('fantasy_large', fonts['header']), 200, CYAN)
    
    # Buttons - use constants for proper centering
    button_width = BUTTON_SIZES['medium'][0]  # 160
    button_height = BUTTON_SIZES['medium'][1]  # 50
    button_spacing = 40  # Gap between buttons
    button_y = 280

    # Center both buttons as a group
    total_width = (button_width * 2) + button_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2  # 332 (properly centered!)

    confirm_button = draw_button(surface, start_x, button_y, button_width, button_height,
                                "CONFIRM", fonts.get('fantasy_small', fonts['normal']))
    back_button = draw_button(surface, start_x + button_width + button_spacing, button_y,
                            button_width, button_height, "BACK", 
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
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, TITLE_GREEN)
    draw_centered_text(surface, "STARTING GOLD", fonts.get('fantasy_medium', fonts['normal']), 120, SOFT_YELLOW)
    
    # Show gold if rolled
    if game_state.character.get('gold', 0) > 0:
        draw_centered_text(surface, f"{game_state.character['gold']} Gold Pieces",
                          fonts.get('fantasy_large', fonts['header']), 200, CYAN)
        button_text = "Continue"
    else:
        draw_centered_text(surface, "Roll 3d6 x 5 for your starting gold",
                          fonts.get('fantasy_medium', fonts['normal']), 200, WHITE)
        button_text = "Roll"
    
    # Button - centered using constants
    button_width = BUTTON_SIZES['medium'][0]  # 160
    button_height = BUTTON_SIZES['medium'][1]  # 50
    button_y = 280
    button_x = (SCREEN_WIDTH - button_width) // 2  # 432 (perfectly centered!)
    
    roll_button = draw_button(surface, button_x, button_y, button_width, button_height, 
                             button_text, fonts.get('fantasy_small', fonts['normal']))
    
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
    draw_centered_text(surface, "CHARACTER CREATION", fonts.get('fantasy_large', fonts['header']), 80, TITLE_GREEN)
    draw_centered_text(surface, "MYSTERIOUS TRINKET", fonts.get('fantasy_medium', fonts['normal']), 120, SOFT_YELLOW)
    
    # Show trinket if rolled
    if game_state.character.get('trinket', ''):
        # Get the display name from the ID
        trinket_id = game_state.character['trinket']

        # Convert ID to display name using ItemManager
        from game_logic.data_manager import get_data_manager
        data_manager = get_data_manager()
        if data_manager and data_manager.item_manager:
            trinket_display = data_manager.item_manager.get_display_name(trinket_id)
        else:
            # Fallback: capitalize the ID
            trinket_display = trinket_id.replace('_', ' ').title()

        draw_centered_text(surface, trinket_display,
                        fonts.get('fantasy_medium', fonts['normal']), 200, CYAN)
        button_text = "Continue"

    else:
        draw_centered_text(surface, "Roll for your mysterious trinket",
                          fonts.get('fantasy_medium', fonts['normal']), 200, WHITE)
        button_text = "Roll"
    
    # Button - centered using constants
    button_width = BUTTON_SIZES['medium'][0]  # 160
    button_height = BUTTON_SIZES['medium'][1]  # 50
    button_y = 280
    button_x = (SCREEN_WIDTH - button_width) // 2  # 432 (perfectly centered!)
    
    roll_button = draw_button(surface, button_x, button_y, button_width, button_height, 
                             button_text, fonts.get('fantasy_small', fonts['normal']))
    
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
    draw_centered_text(surface, "CHARACTER SUMMARY", fonts.get('fantasy_large', fonts['header']), 55, TITLE_GREEN)
    
    # Character info - tighter spacing
    y_pos = 90
    line_height = 28
    
    # Name - label in white, value in yellow
    font_med = fonts.get('fantasy_medium', fonts['normal'])
    
    label_surface = font_med.render("Name: ", True, WHITE)
    surface.blit(label_surface, (80, y_pos))
    value_surface = font_med.render(game_state.character['name'], True, SOFT_YELLOW)
    surface.blit(value_surface, (80 + label_surface.get_width(), y_pos))
    y_pos += line_height
    
    # Gender - label in white, value in yellow
    label_surface = font_med.render("Gender: ", True, WHITE)
    surface.blit(label_surface, (80, y_pos))
    value_surface = font_med.render(game_state.character['gender'].title(), True, SOFT_YELLOW)
    surface.blit(value_surface, (80 + label_surface.get_width(), y_pos))
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
    
    # Hit Points - label in white, value in Yellow
    label_surface = font_med.render("Hit Points: ", True, WHITE)
    surface.blit(label_surface, (80, y_pos))
    hit_points = game_state.character.get('max_hp', 'Calculating...')
    value_surface = font_med.render(str(hit_points), True, SOFT_YELLOW)
    surface.blit(value_surface, (80 + label_surface.get_width(), y_pos))
    y_pos += line_height
    
    # Starting Gold - label in white, value in yellow
    label_surface = font_med.render("Starting Gold: ", True, WHITE)
    surface.blit(label_surface, (80, y_pos))
    value_surface = font_med.render(f"{game_state.character['gold']} gp", True, SOFT_YELLOW)
    surface.blit(value_surface, (80 + label_surface.get_width(), y_pos))
    y_pos += line_height + 8
    
    # Equipment section
    equipment_title = fonts.get('fantasy_medium', fonts['normal']).render("STARTING EQUIPMENT", True, CYAN)
    surface.blit(equipment_title, (80, y_pos))
    y_pos += line_height
    
    try:
        
        # Load items data for name lookup
        items_file = os.path.join("data", "items.json")
        with open(items_file, 'r') as f:
            items_data = json.load(f)
        
        # Helper function to get item name from ID
        def get_item_name(item_id):
            """Convert item ID to display name"""
            for item in items_data['merchant_items']:
                if item['id'] == item_id:
                    return item['name']
            # If not found in merchant_items, return the ID as-is (trinkets, etc.)
            return item_id.replace('_', ' ').title()  # Format ID as fallback
        
        # Build equipment list from ACTUAL GAME STATE INVENTORY
        equipment = []
        
        # Add weapons from inventory
        for weapon_id in game_state.inventory.get('weapons', []):
            weapon_name = get_item_name(weapon_id)
            equipment.append(weapon_name)
            #print(f"  ✅ Added weapon: {weapon_name} (id: {weapon_id})")
        
        # Add armor from inventory (includes shields and bracers)
        for armor_id in game_state.inventory.get('armor', []):
            armor_name = get_item_name(armor_id)
            equipment.append(armor_name)
            #print(f"  ✅ Added armor: {armor_name} (id: {armor_id})")
        
        # Add items from inventory (includes trinkets)
        for item_id in game_state.inventory.get('items', []):
            item_name = get_item_name(item_id)
            equipment.append(item_name)
            #print(f"  ✅ Added item: {item_name} (id: {item_id})")
        
        # Add consumables from inventory
        for consumable_id in game_state.inventory.get('consumables', []):
            consumable_name = get_item_name(consumable_id)
            equipment.append(consumable_name)
            #print(f"  ✅ Added consumable: {consumable_name} (id: {consumable_id})")

    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"❌ Error loading equipment data: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to basic equipment
        equipment = ["Basic Equipment"]
        trinket = game_state.character.get('trinket')
        if trinket and trinket != 'None':
            equipment.append(trinket)
    
    # Render equipment list
    if equipment:
        for item in equipment:
            item_surface = fonts.get('fantasy_tiny', fonts['small']).render(f"• {item}", True, WHITE)
            surface.blit(item_surface, (80, y_pos))
            y_pos += line_height - 2
    else:
        no_equip_surface = fonts.get('fantasy_tiny', fonts['small']).render("• No equipment", True, WHITE)
        surface.blit(no_equip_surface, (80, y_pos))
        print("⚠️ DEBUG: Equipment list is empty!")

    portrait_x = 650
    portrait_y = 150
    portrait_size = 150
    
    pygame.draw.rect(surface, (60, 80, 120), 
                    (portrait_x, portrait_y, portrait_size, portrait_size))
    pygame.draw.rect(surface, WHITE, 
                    (portrait_x, portrait_y, portrait_size, portrait_size), 2)
    
    # Load the active player portrait using same logic as party_display.py
    try:
        
        active_dir = os.path.join(os.path.dirname(MALE_PORTRAITS_PATH), "active")
        active_path = os.path.join(active_dir, "player.jpg")
        
        if os.path.exists(active_path):
            player_portrait = pygame.image.load(active_path)
            player_portrait = pygame.transform.scale(player_portrait, (portrait_size, portrait_size))
            surface.blit(player_portrait, (portrait_x, portrait_y))
        else:
            # Fallback: bright green square for player
            pygame.draw.rect(surface, TITLE_GREEN, 
                            (portrait_x, portrait_y, portrait_size, portrait_size))
            print(f"Warning: Active player portrait missing at {active_path}")

       # Button aligned below portrait with nice spacing
        button_y = portrait_y + portrait_size + 20  # 20px gap below portrait
        button_x = portrait_x - 5  # Slight left alignment with portrait
        start_button = draw_button(surface, button_x, button_y, 160, 50, "START GAME", 
                                fonts.get('fantasy_small', fonts['normal']))
                    
    except Exception as e:
        print(f"Error loading player portrait for character sheet: {e}")
        # Fallback: bright green square for player
        pygame.draw.rect(surface, TITLE_GREEN, 
                        (portrait_x, portrait_y, portrait_size, portrait_size))
        
    return start_button

def finalize_character_creation(game_state):
    """
    Complete character creation by using CharacterEngine
    """

    
    engine = get_character_engine()
    
    if engine:
        # Set character class (fighter for now, expandable later)
        engine.set_character_class('fighter')
        
        # Call the NEW method instead
        success = engine.finalize_character_creation()  # <-- Changed this line
        
        if success:
            print("✅ Character creation completed via CharacterEngine!")
        return success
    else:
        print("❌ CharacterEngine not available!")
        return False
    
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
                      text_y, TITLE_GREEN)
    draw_centered_text(surface, f"{character_name}!", fonts.get('fantasy_large', fonts['header']), 
                      text_y + 30, SOFT_YELLOW)
    
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
    
    # Image area with portrait grid
    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT
    
    # Draw border around image area

    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Dialog area
    dialog_y = LAYOUT_DIALOG_Y
    dialog_height = LAYOUT_DIALOG_HEIGHT
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # Instructions
    text_y = dialog_y + 20
    # Get character name for dynamic text
    character_name = game_state.character.get('name', 'your character')
    title_y = image_y + 20
    draw_centered_text(surface, f"Choose {character_name}'s appearance:", 
                    fonts.get('fantasy_medium', fonts['normal']), title_y, WHITE)
    
    desc_y = text_y + 30
    draw_centered_text(surface, "Click a portrait to select your character image, then click CONTINUE", 
                      fonts.get('fantasy_small', fonts['normal']), desc_y, SOFT_YELLOW)
    
    # Portrait grid (6 portraits, load images or show numbered placeholders)
    portrait_size = 110
    total_width = 6 * portrait_size + 5 * 20  # 6 portraits + 5 gaps of 20px
    start_x = (1024 - total_width) // 2  # Center the row
    portrait_y = image_y + 120  # Position in image area

    portrait_buttons = []
    gender = game_state.character.get('gender', 'male')
    if gender == 'male':
        portrait_dir = MALE_PORTRAITS_PATH
    else:
        portrait_dir = FEMALE_PORTRAITS_PATH

    for i in range(6):
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
        current_selection = getattr(game_state, 'selected_portrait_index', -1)
        if current_selection == i:
            border_color = YELLOW
            border_width = 4
        else:
            border_color = WHITE
            border_width = 2
        
        pygame.draw.rect(surface, border_color, portrait_rect, border_width)
        portrait_buttons.append(portrait_rect)
    
    # Buttons
    button_y = LAYOUT_BUTTON_CENTER_Y
    
    back_button = draw_button(surface, 300, button_y, 120, 40, "BACK", 
                             fonts.get('fantasy_small', fonts['normal']))
    continue_button = draw_button(surface, 600, button_y, 120, 40, "CONTINUE", 
                                 fonts.get('fantasy_small', fonts['normal']))
    
    return portrait_buttons, back_button, continue_button
