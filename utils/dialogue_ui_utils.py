# utils/dialogue_ui_utils.py
"""
UI utility functions that work with the existing DialogueEngine
These functions provide consistent dialogue UI rendering across all NPCs
"""

import pygame
from utils.constants import *
from utils.graphics import draw_button
from utils.npc_display import draw_npc_portrait

def draw_standard_dialogue_screen(surface, npc_name, conversation_data, game_state, fonts, controller=None):
    """
    Standardized dialogue screen that works with DialogueEngine data
    This replaces the individual draw_[npc]_dialogue_screen functions
    """
    surface.fill((0, 0, 0))
    
    # Draw NPC portrait using your existing system
    draw_npc_portrait(surface, npc_name.lower())
        
    # Draw standardized dialogue area
    #dialogue_area = pygame.Rect(DIALOGUE_AREA_X, DIALOGUE_AREA_Y, DIALOGUE_AREA_WIDTH, DIALOGUE_AREA_HEIGHT)
    dialogue_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_area)
    pygame.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_area, 2)
    
    # Title
    title_font = fonts.get('fantasy_large', fonts['normal'])
    title_text = title_font.render(conversation_data['npc_name'].upper(), True, DIALOGUE_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(dialogue_area.centerx, 120)) #DIALOGUE_TITLE_Y))
    surface.blit(title_text, title_rect)
    
    # Introduction text with proper wrapping
    intro_font = fonts.get('fantasy_small', fonts['normal'])
    y_pos = 160 #DIALOGUE_TEXT_START_Y
    x_pos = 190 #DIALOGUE_AREA_X

    for line in conversation_data['introduction']:
        wrapped_lines = wrap_text(line, intro_font, DIALOGUE_AREA_WIDTH - 40)
        for wrapped_surface in wrapped_lines:
            surface.blit(wrapped_surface, (x_pos, y_pos))#DIALOGUE_AREA_X - 70, y_pos))
            y_pos += DIALOGUE_TEXT_LINE_HEIGHT
    
    # Draw dialogue options with hover detection
    mouse_pos = pygame.mouse.get_pos()
    option_rects = []
    y_pos += DIALOGUE_OPTIONS_START_Y_OFFSET
    
    for i, option in enumerate(conversation_data['options']):
        option_text = f"[{i+1}] {option['text']}"
        
        # Calculate dynamic hover rect
        text_surface = intro_font.render(option_text, True, DIALOGUE_OPTION_COLOR)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        option_rect = pygame.Rect(
            x_pos + 25, #DIALOGUE_AREA_X - 45,  # Small left padding
            y_pos - DIALOGUE_OPTION_PADDING,
            text_width + (DIALOGUE_OPTION_PADDING * 2),
            text_height + (DIALOGUE_OPTION_PADDING * 2)
        )
        
        # Hover highlight
        if option_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, DIALOGUE_OPTION_BG_HOVER, option_rect)
            text_surface = intro_font.render(option_text, True, DIALOGUE_OPTION_HOVER_COLOR)
        
        surface.blit(text_surface, (x_pos + 25, y_pos))#(DIALOGUE_AREA_X + 20, y_pos))
        option_rects.append(option_rect)
        y_pos += DIALOGUE_OPTION_HEIGHT
    
    # Draw party status using your existing system
    from utils.party_display import draw_party_status_panel
    draw_party_status_panel(surface, game_state, fonts)
    
    # Standard back button
    back_button = draw_button(surface, 450, 520, 120, 35, "BACK", fonts.get('fantasy_small', fonts['normal']))
    
    return {
        "type": "standard_dialogue",
        "option_rects": option_rects,
        "back_button": back_button,
        "conversation_data": conversation_data
    }


def draw_standard_response_screen(surface, npc_name, response_lines, game_state, fonts, controller=None):
    """
    Standardized response screen that matches the dialogue layout
    Shows NPC's response using the same visual framework as dialogue options
    """
    surface.fill((0, 0, 0))
    
    y_pos = 160 #DIALOGUE_TEXT_START_Y
    x_pos = 190 #DIALOGUE_AREA_X
       
    # Draw NPC portrait using your existing system
    draw_npc_portrait(surface, npc_name.lower())

    # Draw standardized dialogue area (same as main dialogue)
    dialogue_area = pygame.Rect(175, 100, 700, 400)
    pygame.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_area)
    pygame.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_area, 2)
    
    # Title (same styling as dialogue)
    title_font = fonts.get('fantasy_large', fonts['normal'])
    npc_display_name = npc_name.replace('_', ' ').title()
    title_text = title_font.render(npc_display_name.upper(), True, DIALOGUE_TITLE_COLOR)
    title_rect = title_text.get_rect(center=(dialogue_area.centerx, DIALOGUE_TITLE_Y))
    surface.blit(title_text, title_rect)
    
    # Response text with proper wrapping (centered in dialogue area)
    response_font = fonts.get('fantasy_small', fonts['normal'])
    #y_pos = DIALOGUE_TEXT_START_Y
    
    for line in response_lines:
        if line.strip():  # Skip empty lines
            wrapped_lines = wrap_text(line, response_font, DIALOGUE_AREA_WIDTH - 40)
            for wrapped_surface in wrapped_lines:
                # Center each line in the dialogue area
                line_x = x_pos #DIALOGUE_AREA_X + (DIALOGUE_AREA_WIDTH - wrapped_surface.get_width()) // 2
                surface.blit(wrapped_surface, (line_x, y_pos))
                y_pos += DIALOGUE_TEXT_LINE_HEIGHT
            y_pos += 10  # Extra space between paragraphs
    
    # Draw party status using your existing system
    from utils.party_display import draw_party_status_panel
    draw_party_status_panel(surface, game_state, fonts)
    
    # Standardized continue button (same position as back button in dialogues)
    continue_button = draw_button(surface, 450, 520, 120, 35, "CONTINUE", fonts.get('fantasy_small', fonts['normal']))
    
    return {
        "type": "standard_response",
        "continue_button": continue_button
    }