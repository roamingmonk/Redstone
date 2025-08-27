"""
Terror in Redstone - Tavern Screen
The Broken Blade tavern where NPCs gather and adventures begin
"""

import pygame

from utils.constants import (LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, 
                           LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                           LAYOUT_BUTTON_Y, LAYOUT_DIALOG_TEXT_Y, LAYOUT_BUTTON_CENTER_Y,
                           LAYOUT_BUTTON_SMALL_HEIGHT, LAYOUT_BUTTON_MULTI_CENTER_Y)

from utils.party_display import draw_party_status_panel
from game_logic.npc_manager import npc_manager
from game_logic.location_manager import get_location_manager

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
        text_color = DARK_BROWN
    
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    surface.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height)

def draw_centered_text(surface, text, font, y_position, color=WHITE, screen_width=1024):
    """Draw text centered horizontally on the screen"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen_width//2, y_position))
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_tavern_main_screen(surface, game_state, fonts, images=None):
    """Draw the main tavern scene with NPCs and options"""
    surface.fill(BLACK)
    
    # Get character name for personalization
    character_name = game_state.character.get('name', 'Adventurer')
    
    # Use new standardized 3-zone layout
    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT
    
    # Draw border around image area
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Image fits within the border (accounting for border thickness)
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    if images and images.get('tavern'):
        # Scale image to fit within border
        scaled_image = pygame.transform.scale(images['tavern'], (img_width, img_height))
        surface.blit(scaled_image, (img_x, img_y))
    else:
        # Placeholder with tavern atmosphere
        pygame.draw.rect(surface, (40, 20, 10), (img_x, img_y, img_width, img_height))  # Dark brown
        # Get title from location data (fallback section)
        lm = get_location_manager()
        title = lm.get_display_name('broken_blade', 'main_room')
        draw_centered_text(surface, title, fonts.get('fantasy_large', fonts['header']),
                   image_y + 200, YELLOW)
        
    
    # Dialog area - using new standardized layout
    dialog_y = LAYOUT_DIALOG_Y
    dialog_height = LAYOUT_DIALOG_HEIGHT
    
    # Draw border around dialog area
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # Welcome message and tavern atmosphere
    text_y = LAYOUT_DIALOG_TEXT_Y
    
    # Get location manager and load data from JSON structure
    lm = get_location_manager()
    # DEBUG: Let's see what's actually loaded
    #print("DEBUG: All loaded locations:", lm.list_all_locations())
    #print("DEBUG: Requesting location: 'broken_blade'")
    
    area_data = lm.get_area_data('broken_blade', 'main_room')
    
    # Load atmosphere description from location data
    subtitle = area_data['description']['subtitle']
    atmosphere = area_data['description']['atmosphere']
    
    draw_centered_text(surface, subtitle.format(character_name=character_name) if '{character_name}' in subtitle else subtitle,
                fonts.get('fantasy_medium', fonts['normal']), text_y, BRIGHT_GREEN)

    desc_y = text_y + 40
    
    # Split long text into multiple lines for better display
    words = atmosphere.split()
    line1 = ' '.join(words[:12])  # First ~12 words
    line2 = ' '.join(words[12:])  # Remaining words

    draw_centered_text(surface, line1,
                fonts.get('fantasy_small', fonts['normal']), desc_y, WHITE)
    draw_centered_text(surface, line2,
                fonts.get('fantasy_small', fonts['normal']), desc_y + 20, WHITE)
    
    # Action buttons with custom widths
    button_y = LAYOUT_BUTTON_CENTER_Y
    button_height = 40
    button_spacing = 15

    # Define individual button widths
    patron_width = 170
    gamble_width = 110
    bartender_width = 190
    leave_width = 150

    # Calculate starting position to center all buttons
    total_width = patron_width + gamble_width + bartender_width + leave_width + (3 * button_spacing)
    start_x = (1024 - total_width) // 2

    # Draw buttons with individual widths
    talk_button = draw_button(surface, start_x, button_y, patron_width, button_height, 
                            "TALK TO PATRONS", fonts.get('fantasy_tiny', fonts['small']))

    gamble_x = start_x + patron_width + button_spacing
    gamble_button = draw_button(surface, gamble_x, button_y, gamble_width, button_height, 
                            "GAMBLE", fonts.get('fantasy_tiny', fonts['small']))

    bartender_x = gamble_x + gamble_width + button_spacing
    bartender_button = draw_button(surface, bartender_x, button_y, bartender_width, button_height, 
                                "TALK TO BARTENDER", fonts.get('fantasy_tiny', fonts['small']))

    leave_x = bartender_x + bartender_width + button_spacing
    leave_button = draw_button(surface, leave_x, button_y, leave_width, button_height, 
                            "LEAVE TAVERN", fonts.get('fantasy_tiny', fonts['small']))
    
    # Draw help text for hotkeys using constants
    from utils.constants import LAYOUT_HELP_TEXT_Y
    help_y = LAYOUT_HELP_TEXT_Y
    help_font = fonts.get('help_text', fonts['small'])
    help_text = "Press H for help and shortcuts"
    
    # Center the help text
    help_surface = help_font.render(help_text, True, WHITE)
    help_x = (1024 - help_surface.get_width()) // 2
    surface.blit(help_surface, (help_x, help_y))

  # Draw party status panel (only shows after talking to mayor)
    draw_party_status_panel(surface, game_state, fonts)
      
    return talk_button, gamble_button, bartender_button, leave_button

def draw_npc_selection_screen(surface, game_state, fonts, images=None):
    """Draw the NPC interaction selection screen"""
    surface.fill(BLACK)
    
    # Get location manager
    lm = get_location_manager()

    # Use new standardized 3-zone layout
    from utils.constants import (LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, 
                            LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                            LAYOUT_BUTTON_Y, LAYOUT_DIALOG_TEXT_Y)

    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT
    
    # Draw border around image area
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Placeholder image area
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    pygame.draw.rect(surface, (40, 20, 10), (img_x, img_y, img_width, img_height))
    # Get title from location data - use patron selection context
    lm = get_location_manager()
    title = "TAVERN PATRONS"  # Keep this as is, or we can create a separate field later
    draw_centered_text(surface, title, fonts.get('fantasy_large', fonts['header']), 
                    image_y + 240, YELLOW)
    
    # Dialog area - using new standardized layout
    dialog_y = LAYOUT_DIALOG_Y
    dialog_height = LAYOUT_DIALOG_HEIGHT
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # Define text position
    text_y = LAYOUT_DIALOG_TEXT_Y

    # Load patron selection text from location data 
    area_data = lm.get_area_data('broken_blade', 'main_room')
    
    # Critical error if data missing
    if not area_data or 'description' not in area_data:
        print("CRITICAL ERROR: Tavern location data missing!")
        return  # Exit function gracefully

    patron_data = area_data['description']['patron_selection']
    intro = patron_data['intro']
    prompt = patron_data['prompt']

    draw_centered_text(surface, intro, 
                fonts.get('fantasy_small', fonts['normal']), text_y, WHITE)

    desc_y = text_y + 30
    draw_centered_text(surface, prompt, 
                fonts.get('fantasy_medium', fonts['normal']), desc_y, BRIGHT_GREEN)
    
    # NPC buttons with dynamic sizing - 7 characters
    button_height = LAYOUT_BUTTON_SMALL_HEIGHT  # Use smaller buttons for multi-row
    button_spacing = 15
    row_spacing = 10

   # Calculate dynamic button widths based on text length
    font = fonts.get('fantasy_small', fonts['normal'])
    padding = 20  # Extra space around text

    back_width = font.size("BACK")[0] + padding

    server_width = font.size("SERVER")[0] + padding
    pete_width = font.size("OLD PETE")[0] + padding
    warrior_width = font.size("WARRIOR")[0] + padding
    sage_width = font.size("SAGE")[0] + padding
    dwarf_width = font.size("DWARF")[0] + padding
    figure_width = font.size("ROGUE")[0] + padding
    mayor_width = font.size("MAYOR")[0] + padding

    # Single row: ALL buttons in one row
    single_row_npcs = [server_width, pete_width, warrior_width, sage_width, dwarf_width, figure_width]
    if game_state.mayor_mentioned:
        single_row_npcs.append(mayor_width)
    single_row_npcs.append(back_width)

    row_width = sum(single_row_npcs) + (len(single_row_npcs) - 1) * button_spacing
    row_start_x = (1024 - row_width) // 2
    row_y = LAYOUT_BUTTON_CENTER_Y

    # Draw all buttons in single row
    current_x = row_start_x

    server_button = draw_button(surface, current_x, row_y, server_width, button_height,
                            "SERVER", fonts.get('fantasy_small', fonts['normal']))
    current_x += server_width + button_spacing

    pete_button = draw_button(surface, current_x, row_y, pete_width, button_height,
                            "OLD PETE", fonts.get('fantasy_small', fonts['normal']))
    current_x += pete_width + button_spacing

    warrior_button = draw_button(surface, current_x, row_y, warrior_width, button_height,
                            "WARRIOR", fonts.get('fantasy_small', fonts['normal']))
    current_x += warrior_width + button_spacing

    sage_button = draw_button(surface, current_x, row_y, sage_width, button_height,
                            "SAGE", fonts.get('fantasy_small', fonts['normal']))
    current_x += sage_width + button_spacing

    dwarf_button = draw_button(surface, current_x, row_y, dwarf_width, button_height,
                            "DWARF", fonts.get('fantasy_small', fonts['normal']))
    current_x += dwarf_width + button_spacing

    figure_button = draw_button(surface, current_x, row_y, figure_width, button_height,
                            "ROGUE", fonts.get('fantasy_small', fonts['normal']))
    current_x += figure_width + button_spacing

    mayor_button = None
    if game_state.mayor_mentioned:
        mayor_button = draw_button(surface, current_x, row_y, mayor_width, button_height,
                                "MAYOR", fonts.get('fantasy_small', fonts['normal']))
        current_x += mayor_width + button_spacing

    back_button = draw_button(surface, current_x, row_y, back_width, button_height,
                            "BACK", fonts.get('fantasy_small', fonts['normal']))

    # Draw help text for hotkeys using constants
    from utils.constants import LAYOUT_HELP_TEXT_Y
    help_y = LAYOUT_HELP_TEXT_Y
    help_font = fonts.get('help_text', fonts['small'])
    help_text = "Press H for help and shortcuts"
    
    # Center the help text
    help_surface = help_font.render(help_text, True, WHITE)
    help_x = (1024 - help_surface.get_width()) // 2
    surface.blit(help_surface, (help_x, help_y))
    
    # Draw party status panel (only shows after talking to mayor)
    draw_party_status_panel(surface, game_state, fonts)

    return {
        'server': server_button,
        'pete': pete_button, 
        'gareth': warrior_button,     # Internal name -> button mapping
        'elara': sage_button,
        'thorman': dwarf_button,
        'lyra': figure_button,
        'mayor': mayor_button if game_state.mayor_mentioned else None,
        'back': back_button
    }

def get_npc_display_data(current_npc, game_state):
    """Get NPC data from the manager for display purposes"""
    
    # Get basic NPC info from manager
    name = npc_manager.get_npc_name(current_npc)
    description = npc_manager.get_npc_description(current_npc)
    
    # Determine appropriate dialogue based on game state
    if hasattr(game_state, 'mayor_talked') and game_state.mayor_talked:
        if current_npc == 'pete' and hasattr(game_state, 'pete_showing_comedy') and game_state.pete_showing_comedy:
            dialogue = npc_manager.get_npc_dialogue(current_npc, 'comedy_attempt', game_state)
        elif current_npc == 'pete' and hasattr(game_state, 'pete_attempted_recruitment') and game_state.pete_attempted_recruitment:
            dialogue = npc_manager.get_npc_dialogue(current_npc, 'post_attempt', game_state)
        elif len(game_state.party_members) >= 3 and current_npc in ['gareth', 'elara', 'thorman', 'lyra'] and current_npc not in game_state.party_members:
            dialogue = npc_manager.get_npc_dialogue(current_npc, 'party_full', game_state)
        elif len(game_state.party_members) > 0:
            dialogue = npc_manager.get_npc_dialogue(current_npc, 'post_recruitment', game_state)
        else:
            dialogue = npc_manager.get_npc_dialogue(current_npc, 'post_mayor', game_state)
    else:
        dialogue = npc_manager.get_npc_dialogue(current_npc, 'pre_mayor', game_state)
    
    # Handle special cases for non-recruitable NPCs
    if current_npc in ['mayor', 'server', 'regular']:
            
        if current_npc == 'mayor' and not getattr(game_state, 'mayor_talked', False):
            dialogue = npc_manager.get_npc_dialogue(current_npc, 'initial', game_state)
        else:
            dialogue = npc_manager.get_npc_dialogue(current_npc, 'return_visits', game_state)
    
    return {
        'name': name,
        'description': description,
        'dialogue': dialogue
    }

def handle_recruitment_attempt(current_npc, game_state):
    """Handle NPC recruitment using the manager"""
    
    if npc_manager.can_recruit_npc(current_npc, game_state):
        # Add to party
        game_state.party_members.append(current_npc)
        
        # Get success text
        success_text = npc_manager.get_recruitment_text(current_npc)
        print(success_text)
        
        # Show party status
        print(f"✅ {npc_manager.get_npc_name(current_npc)} joined your party!")
        print(f"Party size: {len(game_state.party_members)}/3")
        
        return True
    else:
        # Get failure reason
        failure_reason = npc_manager.get_recruitment_failure_reason(current_npc, game_state)
        print(f"❌ {failure_reason}")
        return False

def draw_npc_conversation_screen(surface, game_state, fonts, images=None):
    """Draw individual NPC conversation screen"""
    surface.fill(BLACK)
    
    # Get current NPC info
    current_npc = game_state.current_npc
    
    # Get NPC data from manager instead of hardcoded dictionary
    npc_display = get_npc_display_data(current_npc, game_state)
    npc = npc_display  # For backwards compatibility with existing code
    
    # Use new standardized 3-zone layout
    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT
    
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Placeholder for NPC portrait
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness
    
    pygame.draw.rect(surface, (40, 20, 10), (img_x, img_y, img_width, img_height))
    draw_centered_text(surface, npc['name'], fonts.get('fantasy_large', fonts['header']), 
                      image_y + 240, YELLOW)
    
    # Dialog area - using new standardized layout
    dialog_y = LAYOUT_DIALOG_Y
    dialog_height = LAYOUT_DIALOG_HEIGHT
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # NPC description
    text_y = LAYOUT_DIALOG_TEXT_Y
    draw_centered_text(surface, npc['name'], 
                      fonts.get('fantasy_medium', fonts['normal']), text_y, WHITE)
    
    # Smart dialogue selection based on quest state
    dialogue_y = text_y + 30
   
    dialogue_set = npc['dialogue']

    # Display the selected dialogue
    for i, line in enumerate(dialogue_set):
        # Use different color for quest notification lines
        if line.startswith('*(') and line.endswith(')*'):
            color = YELLOW  
        else:
            color = CYAN
    
        draw_centered_text(surface, line, fonts.get('fantasy_small', fonts['normal']), 
                    dialogue_y + i * 18, color)
    
    # Set mayor_talked flag when talking to mayor  
    if current_npc == 'mayor':
        if not game_state.mayor_talked:
            game_state.mayor_talked = True
            game_state.quest_active = True
            game_state.met_mayor = True
            game_state.discover_location('refugee_camp')
            game_state.just_got_quest = True
              
    
    # Trigger location discovery when talking to information NPCs
    if current_npc == 'server' and not game_state.server_talked:
        game_state.server_talked = True
        game_state.learned_about_church = True  
        game_state.discover_location('swamp_church')
        
    elif current_npc == 'bartender' and not game_state.bartender_talked:
        game_state.bartender_talked = True
        game_state.learned_about_ruins = True  
        game_state.discover_location('hill_ruins')
   
    # Action buttons
    button_y = LAYOUT_BUTTON_CENTER_Y
    
    # Only show recruit button for adventurers after talking to Mayor
    # Initialize button variables
    recruit_button = None
    shop_button = None
    back_x = 450  # Default back button position

    if current_npc == 'bartender':
        shop_button = draw_button(surface, 250, button_y, 140, 40, "SHOP", 
                                fonts.get('fantasy_small', fonts['normal']))
        back_x = 150  # More space between buttons

    party_full = len(game_state.party_members) >= 3  # Max 3 recruited (4 total with player)
    
    if current_npc in ['gareth', 'elara', 'thorman', 'lyra'] and game_state.mayor_talked and current_npc not in game_state.party_members and not party_full:
        recruit_button = draw_button(surface, 350, button_y, 160, 40, "RECRUIT", 
                                    fonts.get('fantasy_small', fonts['normal']))
        back_x = 550
    elif current_npc == 'pete' and game_state.mayor_talked and not game_state.pete_showing_comedy and not game_state.pete_attempted_recruitment and not party_full:
        recruit_button = draw_button(surface, 350, button_y, 160, 40, "RECRUIT", 
                                    fonts.get('fantasy_small', fonts['normal']))
        back_x = 550
    
    # Set mayor_talked flag when talking to mayor  
    if current_npc == 'mayor':
        if not game_state.mayor_talked:
            game_state.mayor_talked = True
            game_state.quest_active = True
            game_state.met_mayor = True
            game_state.discover_location('refugee_camp')
        
    
    # Set back_x for all cases
    if current_npc in ['gareth', 'elara', 'thorman', 'lyra', 'pete'] and game_state.mayor_talked:
        # Already set back_x = 550 above
        pass
    else:
        # All other cases: center the back button
        back_x = 450

    back_button = draw_button(surface, back_x, button_y, 160, 40, "BACK", 
                            fonts.get('fantasy_small', fonts['normal']))

    # Draw help text for hotkeys using constants
    from utils.constants import LAYOUT_HELP_TEXT_Y
    help_y = LAYOUT_HELP_TEXT_Y
    help_font = fonts.get('help_text', fonts['small'])
    help_text = "Press H for help and shortcuts"
    
    # Center the help text
    help_surface = help_font.render(help_text, True, WHITE)
    help_x = (1024 - help_surface.get_width()) // 2
    surface.blit(help_surface, (help_x, help_y))
    
    # Draw party status panel (only shows after talking to mayor)
    draw_party_status_panel(surface, game_state, fonts)

    # Return the appropriate button based on NPC type
    if current_npc == 'bartender':
        return shop_button, back_button
    else:
        return recruit_button, back_button

def draw_gambling_selection_screen(surface, game_state, fonts, images=None):
    """Draw the gambling game selection screen"""
    surface.fill(BLACK)

    # Same 70/30 layout
    image_y = 20
    image_height = 510

    draw_border(surface, 0, image_y, 1024, image_height)

    # Placeholder gambling area
    border_thickness = 6
    img_x = border_thickness
    img_y = image_y + border_thickness
    img_width = 1024 - 2 * border_thickness
    img_height = image_height - 2 * border_thickness

    pygame.draw.rect(surface, (20, 40, 20), (img_x, img_y, img_width, img_height))  # Dark green felt
    draw_centered_text(surface, "THE GAMBLING DEN", fonts.get('fantasy_large', fonts['header']), 
                    image_y + 240, YELLOW)

    # Dialog area
    dialog_y = image_y + image_height + 20
    dialog_height = 768 - dialog_y - 20
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)

    # Game selection
    text_y = dialog_y + 35
    character_gold = game_state.character.get('gold', 0)
    draw_centered_text(surface, f"Your Gold: {character_gold} gp", 
                    fonts.get('fantasy_medium', fonts['normal']), text_y, YELLOW)

    desc_y = text_y + 40
    draw_centered_text(surface, "Choose your game of chance:", 
                    fonts.get('fantasy_small', fonts['normal']), desc_y, WHITE)

    # Game selection buttons
    button_y = desc_y + 60

    redstone_button = draw_button(surface, 200, button_y, 200, 40, "REDSTONE DICE", 
                                fonts.get('fantasy_small', fonts['normal']))

    merchant_button = draw_button(surface, 420, button_y, 220, 40, "MERCHANT'S GAMBIT", 
                                fonts.get('fantasy_tiny', fonts['small']))

    back_button = draw_button(surface, 660, button_y, 160, 40, "BACK TO TAVERN", 
                            fonts.get('fantasy_tiny', fonts['small']))

    return redstone_button, merchant_button, back_button
