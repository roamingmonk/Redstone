"""
Terror in Redstone - Redstone Dice Game Screens
The complete gambling experience with betting, rolling, and results
"""

import pygame
import random

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
DARK_BROWN = (101, 67, 33)
BLUE = (0, 0, 170)

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

def draw_button(surface, x, y, width, height, text, font, pressed=False, selected=False, enabled=True):
    """Draw a retro-style button"""
    if not enabled:
        color = DARK_GRAY
        border_color = DARK_GRAY
        text_color = (60, 60, 60)  # Very dark gray
    elif selected:
        color = YELLOW
        border_color = WHITE
        text_color = BLACK
    else:
        color = DARK_GRAY if pressed else GRAY
        border_color = DARK_GRAY if pressed else WHITE
        text_color = DARK_BROWN
    
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    surface.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height) if enabled else None

def draw_centered_text(surface, text, font, y_position, color=WHITE, screen_width=1024):
    """Draw text centered horizontally on the screen"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen_width//2, y_position))
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_dice(surface, x, y, size, value, rolling=False):
    """Draw a single die with proper retro styling"""
    # Die background - white with black border
    pygame.draw.rect(surface, BROWN, (x, y, size, size))
    pygame.draw.rect(surface, BLACK, (x, y, size, size), 3)
    
    if rolling:
        # Show random dots while rolling
        value = random.randint(1, 6)
    
    # Draw dots based on value
    dot_size = size // 8
    dot_positions = {
        1: [(size//2, size//2)],
        2: [(size//4, size//4), (3*size//4, 3*size//4)],
        3: [(size//4, size//4), (size//2, size//2), (3*size//4, 3*size//4)],
        4: [(size//4, size//4), (3*size//4, size//4), (size//4, 3*size//4), (3*size//4, 3*size//4)],
        5: [(size//4, size//4), (3*size//4, size//4), (size//2, size//2), (size//4, 3*size//4), (3*size//4, 3*size//4)],
        6: [(size//4, size//4), (3*size//4, size//4), (size//4, size//2), (3*size//4, size//2), (size//4, 3*size//4), (3*size//4, 3*size//4)]
    }
    
    for dot_x, dot_y in dot_positions[value]:
        pygame.draw.circle(surface, BLACK, (x + dot_x, y + dot_y), dot_size)

def draw_dice_bet_screen(surface, game_state, fonts, images=None):
    """Draw the betting selection screen"""
    surface.fill(BLACK)
    
    # Same 70/30 layout
    image_y = 20
    image_height = 510
    
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Gambling den atmosphere
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    pygame.draw.rect(surface, (20, 40, 20), (img_x, img_y, img_width, img_height))  # Dark green felt
    
    # Draw large decorative dice in the image area
    dice_size = 80
    dice_y = img_y + img_height//2 - dice_size//2
    draw_dice(surface, img_x + img_width//2 - 120, dice_y, dice_size, 6)
    draw_dice(surface, img_x + img_width//2 - 20, dice_y, dice_size, 1)
    draw_dice(surface, img_x + img_width//2 + 80, dice_y, dice_size, 3)
    
    draw_centered_text(surface, "REDSTONE DICE", fonts.get('fantasy_large', fonts['header']), 
                      image_y + 120, YELLOW)
    draw_centered_text(surface, "Place Your Bet", fonts.get('fantasy_medium', fonts['normal']), 
                      image_y + 380, WHITE)
    
    # Dialog area
    dialog_y = image_y + image_height + 20
    dialog_height = 768 - dialog_y - 20
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # Player status
    text_y = dialog_y + 25
    player_gold = game_state.character.get('gold', 0)
    house_money = game_state.dice_game['house_money']
    
    draw_centered_text(surface, f"Your Gold: {player_gold} gp", 
                      fonts.get('fantasy_medium', fonts['normal']), text_y, BRIGHT_GREEN)
    draw_centered_text(surface, f"House Money: {house_money} gp", 
                      fonts.get('fantasy_small', fonts['normal']), text_y + 30, YELLOW)
    
    # Betting buttons
    button_y = text_y + 70
    button_width = 120
    button_height = 50
    button_spacing = 140
    
    # Calculate starting position to center all buttons
    total_width = 3 * button_width + 2 * button_spacing + 2 * 20  # Include spacing for rules and back
    start_x = (1024 - total_width) // 2
    
    # Check which bets player can afford
    bet_5_button = draw_button(surface, start_x, button_y, button_width, button_height,
                              "BET 5 GP", fonts.get('fantasy_tiny', fonts['small']),
                              enabled=game_state.can_afford_bet(5))
    
    bet_10_button = draw_button(surface, start_x + button_spacing, button_y, button_width, button_height,
                               "BET 10 GP", fonts.get('fantasy_tiny', fonts['small']),
                               enabled=game_state.can_afford_bet(10))
    
    bet_25_button = draw_button(surface, start_x + 2 * button_spacing, button_y, button_width, button_height,
                               "BET 25 GP", fonts.get('fantasy_tiny', fonts['small']),
                               enabled=game_state.can_afford_bet(25))
    
    # Rules and back buttons
    rules_button = draw_button(surface, start_x + 3 * button_spacing + 20, button_y, 100, button_height,
                              "RULES (?)", fonts.get('fantasy_tiny', fonts['small']))
    
    back_button = draw_button(surface, start_x + 3 * button_spacing + 140, button_y, 100, button_height,
                             "BACK", fonts.get('fantasy_tiny', fonts['small']))
    
    # Instructions
    if not game_state.dice_game['game_active']:
        draw_centered_text(surface, "GAME OVER - Casino closed or house is broke!", 
                          fonts.get('fantasy_small', fonts['normal']), button_y + 70, RED)
    elif player_gold < 5:
        draw_centered_text(surface, "Come back when you have more coin, adventurer!", 
                          fonts.get('fantasy_small', fonts['normal']), button_y + 70, RED)
    else:
        draw_centered_text(surface, "Choose your bet amount to roll the dice!", 
                          fonts.get('fantasy_small', fonts['normal']), button_y + 70, WHITE)
    
    return bet_5_button, bet_10_button, bet_25_button, rules_button, back_button

def draw_dice_rolling_screen(surface, game_state, fonts, images=None):
    """Draw the dice rolling animation screen with click-to-skip"""
    surface.fill(BLACK)
    
    # Same 70/30 layout
    image_y = 20
    image_height = 510
    
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Gambling area
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    pygame.draw.rect(surface, (20, 40, 20), (img_x, img_y, img_width, img_height))
    
    # Title
    draw_centered_text(surface, "ROLLING THE DICE...", fonts.get('fantasy_large', fonts['header']), 
                      image_y + 80, YELLOW)
    
    # Check if we're still in rolling animation
    current_time = pygame.time.get_ticks()
    roll_start_time = game_state.dice_game.get('roll_start_time', 0)
    rolling_duration = 2000  # 2 seconds of rolling animation
    
    # Check if animation should be skipped (will be set by click handler)
    animation_skipped = game_state.dice_game.get('animation_skipped', False)
    is_rolling = (current_time - roll_start_time) < rolling_duration and not animation_skipped
    
    # Draw dice - large and centered
    dice_size = 100
    dice_spacing = 140
    total_dice_width = 3 * dice_size + 2 * dice_spacing
    dice_start_x = img_x + (img_width - total_dice_width) // 2
    dice_y = img_y + img_height//2 - dice_size//2
    
    if is_rolling:
        # Show rolling animation
        for i in range(3):
            dice_x = dice_start_x + i * (dice_size + dice_spacing)
            draw_dice(surface, dice_x, dice_y, dice_size, random.randint(1, 6), rolling=True)
        
        # Return a full-screen clickable area for skipping
        return pygame.Rect(0, 0, 1024, 768)  # Full screen clickable
    else:
        # Show final results
        final_dice = game_state.dice_game.get('last_roll', [1, 1, 1])
        for i, value in enumerate(final_dice):
            dice_x = dice_start_x + i * (dice_size + dice_spacing)
            draw_dice(surface, dice_x, dice_y, dice_size, value)
    
    # Dialog area
    dialog_y = image_y + image_height + 20
    dialog_height = 768 - dialog_y - 20
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    text_y = dialog_y + 20
    bet_amount = game_state.dice_game.get('current_bet', 0)
    
    if is_rolling:
        draw_centered_text(surface, f"Rolling dice for {bet_amount} gold...", 
                          fonts.get('fantasy_medium', fonts['normal']), text_y + 30, WHITE)
        draw_centered_text(surface, "Hold your breath, adventurer!", 
                          fonts.get('fantasy_small', fonts['normal']), text_y + 60, CYAN)
        
        # Return the full screen area as clickable during animation
        return pygame.Rect(0, 0, 1024, 768)
    else:
        # Rolling is done - show continue button
        draw_centered_text(surface, f"The dice have settled!", 
                          fonts.get('fantasy_medium', fonts['normal']), text_y + 20, WHITE)
        
        continue_button = draw_button(surface, 450, text_y + 80, 140, 40, "SEE RESULTS", 
                                     fonts.get('fantasy_small', fonts['normal']))
        
        return continue_button

def draw_dice_results_screen(surface, game_state, fonts, images=None):
    """Draw the results and payout screen"""
    surface.fill(BLACK)
    
    # Same 70/30 layout
    image_y = 20
    image_height = 510
    
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Gambling area
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    pygame.draw.rect(surface, (20, 40, 20), (img_x, img_y, img_width, img_height))
    
    # Get results
    last_roll = game_state.dice_game.get('last_roll', [1, 1, 1])
    last_result = game_state.dice_game.get('last_result', {})
    
    combination = last_result.get('combination', 'Unknown')
    payout = last_result.get('payout', 0)
    description = last_result.get('description', 'Something happened!')
    
    # Title
    if payout > 0:
        draw_centered_text(surface, "WINNER!", fonts.get('fantasy_large', fonts['header']), 
                          image_y + 80, BRIGHT_GREEN)
    else:
        draw_centered_text(surface, "HOUSE WINS", fonts.get('fantasy_large', fonts['header']), 
                          image_y + 80, RED)
    
    # Draw final dice
    dice_size = 80
    dice_spacing = 120
    total_dice_width = 3 * dice_size + 2 * dice_spacing
    dice_start_x = img_x + (img_width - total_dice_width) // 2
    dice_y = img_y + 150
    
    for i, value in enumerate(last_roll):
        dice_x = dice_start_x + i * (dice_size + dice_spacing)
        draw_dice(surface, dice_x, dice_y, dice_size, value)
    
    # Show combination
    draw_centered_text(surface, combination, fonts.get('fantasy_medium', fonts['normal']), 
                      image_y + 280, YELLOW)
    
    # Show payout
    if payout > 0:
        draw_centered_text(surface, f"You win {payout} gold!", 
                          fonts.get('fantasy_medium', fonts['normal']), image_y + 320, BRIGHT_GREEN)
    else:
        bet_amount = game_state.dice_game.get('current_bet', 0)
        draw_centered_text(surface, f"You lose {bet_amount} gold!", 
                          fonts.get('fantasy_medium', fonts['normal']), image_y + 320, RED)
    
    # Dialog area
    dialog_y = image_y + image_height + 20
    dialog_height = 768 - dialog_y - 20
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    text_y = dialog_y + 25
    
    # Show current status
    player_gold = game_state.character.get('gold', 0)
    house_money = game_state.dice_game['house_money']
    
    draw_centered_text(surface, f"Your Gold: {player_gold} gp  |  House Money: {house_money} gp", 
                      fonts.get('fantasy_small', fonts['normal']), text_y, WHITE)
    
    # Flavor text
    draw_centered_text(surface, description, fonts.get('fantasy_small', fonts['normal']), 
                      text_y + 25, CYAN)
    
    # Action buttons
    button_y = text_y + 80
    
    if game_state.dice_game['game_active'] and player_gold > 0:
        play_again_button = draw_button(surface, 350, button_y, 140, 40, "PLAY AGAIN", 
                                       fonts.get('fantasy_small', fonts['normal']))
        quit_button = draw_button(surface, 510, button_y, 140, 40, "QUIT GAME", 
                                 fonts.get('fantasy_small', fonts['normal']))
        return play_again_button, quit_button
    else:
        # Game over
        if not game_state.dice_game['game_active']:
            draw_centered_text(surface, "GAME OVER - Casino has closed!", 
                              fonts.get('fantasy_medium', fonts['normal']), button_y - 10, RED)
        else:
            draw_centered_text(surface, "You're out of gold!", 
                              fonts.get('fantasy_medium', fonts['normal']), button_y - 10, RED)
        
        quit_button = draw_button(surface, 450, button_y + 20, 140, 40, "BACK TO TAVERN", 
                                 fonts.get('fantasy_small', fonts['normal']))
        return None, quit_button

def draw_dice_rules_screen(surface, game_state, fonts, images=None):
    """Draw the rules explanation screen"""
    surface.fill(BLACK)
    
    # Full screen for rules
    draw_border(surface, 20, 20, 1024-40, 768-40)
    
    # Title
    draw_centered_text(surface, "REDSTONE DICE RULES", fonts.get('fantasy_large', fonts['header']), 
                      60, YELLOW)
    
    # Rules text
    y_pos = 120
    line_height = 28
    
    rules = [
        "HOW TO PLAY:",
        "• Choose your bet: 5, 10, or 25 gold pieces",
        "• Roll three dice and hope for winning combinations!",
        "",
        "WINNING COMBINATIONS:",
        "• Triple Sixes (6-6-6): 20x payout + CASINO CLOSES!",
        "• Any Triple (1-1-1, 2-2-2, etc.): 8x payout",
        "• Straight (1-2-3, 2-3-4, 3-4-5, 4-5-6): 4x payout",
        "• Any Pair (1-1-X, 2-2-X, etc.): 1.5x payout",
        "• High Total (15 or more): 1.5x payout",
        "• Everything else: House wins your bet",
        "",
        "SPECIAL RULES:",
        "• You can't win more than the house has",
        "• Triple sixes ends the game in victory!",
        "• Straights don't wrap around (6-1-2 is not a straight)",
        "• Need at least 5 gold to play"
    ]
    
    for line in rules:
        if line.startswith("•"):
            color = WHITE
            font = fonts.get('fantasy_small', fonts['normal'])
        elif line == "":
            y_pos += line_height // 2
            continue
        elif line.endswith(":"):
            color = BRIGHT_GREEN
            font = fonts.get('fantasy_medium', fonts['normal'])
        else:
            color = CYAN
            font = fonts.get('fantasy_small', fonts['normal'])
        
        draw_centered_text(surface, line, font, y_pos, color)
        y_pos += line_height
    
    # Back button
    back_button = draw_button(surface, 450, 680, 140, 40, "BACK", 
                             fonts.get('fantasy_small', fonts['normal']))
    
    return back_button