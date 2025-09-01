"""
Terror in Redstone - Quest Log System
Classic RPG quest tracking with two-column layout
"""

import pygame

from utils.overlay_utils import (
    draw_popup_background, draw_chunky_border, 
    draw_button, WHITE, BLACK, BRIGHT_GREEN, BROWN, DARK_GRAY, SELECTION_COLOR
)

def draw_quest_log_screen(surface, game_state, fonts, images=None):
    """Draw the classic RPG quest log screen"""
    
    # Check required data
    if not hasattr(game_state, 'character'):
        print("ERROR: game_state has no character")
        return None
    
    # Fill screen with brown background
    draw_popup_background(surface)
    
    # Get character name for title
    character_name = game_state.character.get('name', 'Adventurer')
    
    # Draw title
    title_y = 25
    title_font = fonts.get('fantasy_large', fonts['header'])
    title_text = title_font.render(f"{character_name}'s Quests", True, BRIGHT_GREEN)
    title_x = (1024 - title_text.get_width()) // 2
    surface.blit(title_text, (title_x, title_y))
    
    # Draw main content border
    content_x = 50
    content_y = 120
    content_width = 924  # 1024 - 100 (50px margin each side)
    content_height = 500
    
    draw_chunky_border(surface, content_x, content_y, content_width, content_height)
    
    # Calculate layout areas
    quest_list_x = content_x + 20
    quest_list_y = content_y + 20
    quest_list_width = 350  # Left column for quest list
    quest_list_height = content_height - 40
    
    # Divider line
    divider_x = quest_list_x + quest_list_width + 10
    divider_y = quest_list_y
    divider_height = quest_list_height
    
    # Quest details area  
    details_x = divider_x + 20
    details_y = quest_list_y
    details_width = content_width - (details_x - content_x) - 20
    details_height = quest_list_height
    
    # Draw quest list background
    pygame.draw.rect(surface, DARK_GRAY, 
                    (quest_list_x, quest_list_y, quest_list_width, quest_list_height))
    pygame.draw.rect(surface, WHITE, 
                    (quest_list_x, quest_list_y, quest_list_width, quest_list_height), 2)
    
    # Draw divider line
    pygame.draw.line(surface, WHITE, 
                    (divider_x, divider_y), (divider_x, divider_y + divider_height), 3)
    
    # Draw quest details background
    pygame.draw.rect(surface, DARK_GRAY, 
                    (details_x, details_y, details_width, details_height))
    pygame.draw.rect(surface, WHITE, 
                    (details_x, details_y, details_width, details_height), 2)
    
    # Get quest data from game state
    quests = get_available_quests(game_state)
    selected_quest = getattr(game_state, 'selected_quest', None)
    
    # Draw quest list
    quest_rects = []
    row_height = 40
    start_y = quest_list_y + 10
    
    # Headers
    font = fonts.get('fantasy_small', fonts['normal'])
    small_font = fonts.get('normal', font)
    
    # Draw "Quest Title" and "Status" headers
    header_y = start_y
    header_text = font.render("Quest Title", True, WHITE)
    surface.blit(header_text, (quest_list_x + 10, header_y))

    status_text = font.render("Status", True, WHITE)
    surface.blit(status_text, (quest_list_x + 260, header_y))
    
    # Draw header separator line
    header_line_y = header_y + 25
    pygame.draw.line(surface, WHITE, 
                    (quest_list_x + 10, header_line_y), 
                    (quest_list_x + quest_list_width - 10, header_line_y), 2)
    
    # Draw quest rows
    current_y = header_line_y + 10
    
    for quest in quests:
        quest_rect = pygame.Rect(quest_list_x + 5, current_y - 5, 
                               quest_list_width - 10, row_height)
        quest_rects.append(quest_rect)
        
        # Highlight selected quest
        if selected_quest == quest['id']:
            pygame.draw.rect(surface, SELECTION_COLOR, quest_rect)
        
        # Draw quest status indicator
        status_x = quest_list_x + 15
        status_y = current_y + 10
        
        if quest['completed']:
            # Draw checkmark for completed quests
            pygame.draw.circle(surface, BRIGHT_GREEN, (status_x, status_y), 8)
            # Simple checkmark using lines
            pygame.draw.line(surface, WHITE, (status_x - 3, status_y), (status_x, status_y + 3), 2)
            pygame.draw.line(surface, WHITE, (status_x, status_y + 3), (status_x + 4, status_y - 2), 2)
        else:
            # Draw open circle for active quests
            pygame.draw.circle(surface, WHITE, (status_x, status_y), 8, 2)
        
        # Draw quest title (truncated if needed)
        title_x = quest_list_x + 40
        max_title_width = 220  # Leave room for status text
        title_text = quest['title']
        
        # Truncate title if too long
        title_surface = small_font.render(title_text, True, WHITE)
        if title_surface.get_width() > max_title_width:
            # Gradually shorten until it fits
            while title_surface.get_width() > max_title_width and len(title_text) > 10:
                title_text = title_text[:-4] + "..."
                title_surface = small_font.render(title_text, True, WHITE)
        
        surface.blit(title_surface, (title_x, current_y + 5))
        
        # Draw status text
        status_text = "Complete" if quest['completed'] else "Open"
        status_surface = small_font.render(status_text, True, WHITE)
        status_text_x = quest_list_x + 260
        surface.blit(status_surface, (status_text_x, current_y + 5))
        
        current_y += row_height
    
    # Draw quest details
    if selected_quest:
        quest_data = next((q for q in quests if q['id'] == selected_quest), None)
        if quest_data:
            draw_quest_details(surface, quest_data, details_x, details_y, 
                             details_width, details_height, fonts)
    else:
        # Show prompt to select a quest
        prompt_y = details_y + details_height // 2
        prompt_text = fonts.get('normal', font).render("Select a quest to view details", True, WHITE)
        text_x = details_x + (details_width - prompt_text.get_width()) // 2
        surface.blit(prompt_text, (text_x, prompt_y))
    
    # Draw return button
    button_y = content_y + content_height + 20
    return_rect = draw_button(surface, 512 - 60, button_y, 120, 40, 
                             "Return", fonts.get('fantasy_small', fonts['normal']))

    # Draw close instruction
    close_y = button_y + 50
    close_font = fonts.get('help_text', fonts['small'])
    close_text = "Press Q again to close"
    
    # Center the close instruction
    close_surface = close_font.render(close_text, True, WHITE)
    close_x = (1024 - close_surface.get_width()) // 2
    surface.blit(close_surface, (close_x, close_y))


    return quest_rects, return_rect

def draw_quest_details(surface, quest_data, x, y, width, height, fonts):
    """Draw detailed quest information in the right panel"""
    
    font = fonts.get('normal', fonts['header'])
    small_font = fonts.get('small', font)
    
    # Quest title
    title_y = y + 20
    title_surface = font.render(quest_data['title'], True, BRIGHT_GREEN)
    surface.blit(title_surface, (x + 20, title_y))
    
    # Quest description with word wrapping
    desc_y = title_y + 40
    description = quest_data['description']
    
    # Simple word wrapping
    words = description.split(' ')
    lines = []
    current_line = ''
    
    for word in words:
        test_line = current_line + word + ' '
        test_surface = small_font.render(test_line, True, WHITE)
        
        if test_surface.get_width() > width - 40:
            if current_line:
                lines.append(current_line.strip())
                current_line = word + ' '
            else:
                lines.append(word)
                current_line = ''
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line.strip())
    
    # Draw description lines
    line_height = 25
    current_y = desc_y
    
    for line in lines:
        if current_y + line_height > y + height - 20:  # Don't overflow
            break
        line_surface = small_font.render(line, True, WHITE)
        surface.blit(line_surface, (x + 20, current_y))
        current_y += line_height

def get_available_quests(game_state):
    """Get list of available quests based on game state"""
    
    quests = []
    
    # Main quest - always available once player has met mayor
    if getattr(game_state, 'met_mayor', False):
        main_quest = {
            'id': 'missing_townspeople',
            'title': 'Find Missing Townspeople',
            'completed': getattr(game_state, 'main_quest_complete', False),
            'description': '''Strange winds have been howling through Redstone's cobbled streets for three nights running, and with each dawn, fewer faces appear at market. Old Henrik the blacksmith, young Sarah the baker's daughter, even Constable Morris - all vanished without so much as a scream in the night. The remaining townfolk whisper of an ancient moving wrong, of footprints that lead to the old mine shaft before moving wrong again. Every candle and every candle flame in the tavern flickers in unison.'''
        }
        quests.append(main_quest)
    
    # Sub-quest: Investigate Refugee Camp (available after talking to garrick)
    if getattr(game_state, 'learned_about_refugees', False):
        refugee_quest = {
            'id': 'investigate_refugee_camp',
            'title': 'Investigate Refugee Camp',
            'completed': getattr(game_state, 'refugee_camp_complete', False),
            'description': '''Garrick, the bartender mentioned a group of refugees who recently arrived from the northern settlements. They've made camp outside town and may have witnessed something unusual during their travels. Speaking with them could provide valuable information about the disappearances.'''
        }
        quests.append(refugee_quest)
    
    # Sub-quest: Explore Swamp Church (available after talking to meredith)
    if getattr(game_state, 'learned_about_church', False):
        church_quest = {
            'id': 'explore_swamp_church',
            'title': 'Explore Swamp Church',
            'completed': getattr(game_state, 'swamp_church_complete', False),
            'description': '''Meredith, the tavern server whispered about an abandoned church deep in the eastern swamps. Local legend speaks of strange lights and unholy chanting emanating from the ruins during the dark hours. This cursed place may hold clues to the supernatural forces at work.'''
        }
        quests.append(church_quest)
    
    # Sub-quest: Search Hill Ruins (available after talking to grizzled warrior)
    if getattr(game_state, 'learned_about_ruins', False):
        ruins_quest = {
            'id': 'search_hill_ruins',
            'title': 'Search Hill Ruins',
            'completed': getattr(game_state, 'hill_ruins_complete', False),
            'description': '''The grizzled warrior spoke of ancient ruins atop the western hills, where old stones bear inscriptions in a forgotten tongue. These ruins predate the town itself and may contain knowledge of ancient evils that once plagued this land. A thorough search could reveal protective wards or banishment rituals.'''
        }
        quests.append(ruins_quest)
    
    return quests