# utils/dialogue_ui_utils.py
"""
UI utility functions that work with the existing DialogueEngine
PHASE 1: DISABLE DUAL RENDERING - Let generic_dialogue_handler.py take over
"""

import pygame
from utils.constants import (DIALOGUE_BG_COLOR, DIALOGUE_BORDER_COLOR,
                             DIALOGUE_TEXT_COLOR, DIALOGUE_TITLE_COLOR)
from utils.graphics import draw_button
from utils.npc_display import draw_npc_portrait
from utils.constants import wrap_text as constants_wrap_text

print(f"🔍 DUI module path: {__file__}")

def draw_standard_dialogue_screen(surface, npc_name, conversation_data, game_state, fonts, controller=None):
    """
    DISABLED: This function has been replaced by generic_dialogue_handler.py
    
    Leaving the function signature intact to prevent import errors,
    but the actual rendering is now handled by the generic system.
    """
    print(f"⚠️ DEPRECATED: draw_standard_dialogue_screen called for {npc_name} - should use generic_dialogue_handler")
    
    # Return minimal result to prevent crashes
    return {
        "type": "deprecated_dialogue",
        "conversation_data": conversation_data
    }


def draw_standard_response_screen(surface, npc_name, response_lines, game_state, fonts, controller=None):
    """
    DISABLED: This function has been replaced by generic_dialogue_handler.py
    
    Leaving the function signature intact to prevent import errors,
    but the actual rendering is now handled by the generic system.
    """
    print(f"⚠️ DEPRECATED: draw_standard_response_screen called for {npc_name} - should use generic_dialogue_handler")
    
    # Return minimal result to prevent crashes
    return {
        "type": "deprecated_response",
        "action_rects": {}
    }


# ========== UTILITY FUNCTIONS - THESE WILL BE PRESERVED ==========
def wrap_text(text, font, max_width):
    """
    Dialogue-specific text wrapping wrapper
    
    This is a convenience wrapper around constants.wrap_text that
    automatically uses DIALOGUE_TEXT_COLOR for dialogue screens.
    
    For other UI contexts (combat log, etc.), import directly from constants.
    """
    return constants_wrap_text(text, font, max_width, DIALOGUE_TEXT_COLOR)

def format_dialogue_title(npc_name, font):
    """
    Title formatting utility - KEEP THIS
    Standard way to format NPC names for dialogue titles
    """
    display_name = npc_name.replace('_', ' ').title()
    return font.render(display_name.upper(), True, DIALOGUE_TITLE_COLOR)


def create_dialogue_area(surface, x, y, width, height):
    """
    Dialogue area creation utility - KEEP THIS
    Standard dialogue box drawing function
    """
    dialogue_area = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, DIALOGUE_BG_COLOR, dialogue_area)
    pygame.draw.rect(surface, DIALOGUE_BORDER_COLOR, dialogue_area, 2)
    return dialogue_area