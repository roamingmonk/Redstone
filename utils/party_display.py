# utils/party_display.py
import pygame
import os
from utils.constants import (
    WHITE, YELLOW, BRIGHT_GREEN, RED, BLACK, GRAY,
    NPC_PORTRAITS_PATH, PLAYER_PORTRAITS_PATH
)
from utils.graphics import draw_centered_text

# Party display constants
PARTY_PANEL_WIDTH = 138
PARTY_PANEL_X = 1024 - PARTY_PANEL_WIDTH
PORTRAIT_SIZE = 110
PORTRAIT_SPACING = 10
FRAME_THICKNESS = 3

def draw_party_status_panel(surface, game_state, fonts):
    """
    Draw party status panel on right side of screen
    """
        
    # Draw panel background
    panel_rect = pygame.Rect(PARTY_PANEL_X, 10, PARTY_PANEL_WIDTH, 500)
    pygame.draw.rect(surface, (20, 15, 10), panel_rect)  # Dark brown background
    pygame.draw.rect(surface, WHITE, panel_rect, 2)  # White border
    
    # Panel title
    title_y = 15
    
        
    # Draw portraits
    start_y = 25

    # Player portrait (always first)
    draw_party_portrait(surface, PARTY_PANEL_X + 15, start_y, 
                       "player", game_state, fonts, is_player=True)
    
    # NPC portraits
    for i, npc_name in enumerate(game_state.party_members):
        if i >= 3:  # Maximum 3 NPCs
            break
        portrait_y = start_y + (i + 1) * (PORTRAIT_SIZE + PORTRAIT_SPACING)
        draw_party_portrait(surface, PARTY_PANEL_X + 15, portrait_y, 
                           npc_name, game_state, fonts, is_player=False)
    
    # Empty slots
    total_members = 1 + len(game_state.party_members)  # Player + NPCs
    for i in range(total_members, 4):  # Show up to 4 total
        portrait_y = start_y + i * (PORTRAIT_SIZE + PORTRAIT_SPACING)
        draw_empty_portrait_slot(surface, PARTY_PANEL_X + 15, portrait_y)

def draw_party_portrait(surface, x, y, character_name, game_state, fonts, is_player=False):
    """Draw individual party member portrait"""
    
    # Try to load portrait
    portrait = load_portrait(character_name, is_player)
    
    if portrait:
        # Scale portrait to fit
        portrait = pygame.transform.scale(portrait, (PORTRAIT_SIZE, PORTRAIT_SIZE))
        surface.blit(portrait, (x, y))
    else:
        # Fallback colored rectangle
        color = get_character_color(character_name, is_player)
        pygame.draw.rect(surface, color, (x, y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    
    # Draw frame
    pygame.draw.rect(surface, WHITE, (x, y, PORTRAIT_SIZE, PORTRAIT_SIZE), FRAME_THICKNESS)
    

def draw_empty_portrait_slot(surface, x, y):
    """Draw empty portrait slot"""
    # Gray background
    pygame.draw.rect(surface, GRAY, (x, y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    
    # Dashed border effect
    for dash in range(0, PORTRAIT_SIZE, 8):
        pygame.draw.rect(surface, WHITE, (x + dash, y, 4, 2))
        pygame.draw.rect(surface, WHITE, (x + dash, y + PORTRAIT_SIZE - 2, 4, 2))
        pygame.draw.rect(surface, WHITE, (x, y + dash, 2, 4))
        pygame.draw.rect(surface, WHITE, (x + PORTRAIT_SIZE - 2, y + dash, 2, 4))

def load_portrait(character_name, is_player=False):
    """Load character portrait from file with recovery system"""
    try:
        if is_player:
            # Use same path logic as game_state.py for consistency
            from utils.constants import MALE_PORTRAITS_PATH
            active_dir = os.path.join(os.path.dirname(MALE_PORTRAITS_PATH), "active")
            active_path = os.path.join(active_dir, "player.jpg")
            
            if os.path.exists(active_path):
                return pygame.image.load(active_path)
            else:
                # Active portrait missing - this should trigger recovery in game_state
                print(f"Warning: Active player portrait missing at {active_path}")
                return None
        else:
            # Load NPC portrait
            filename = f"{character_name}_portrait.jpg"
            filepath = os.path.join(NPC_PORTRAITS_PATH, filename)
            return pygame.image.load(filepath)
    except Exception as e:
        print(f"Error loading portrait: {e}")
        return None

def get_character_color(character_name, is_player=False):
    """Get fallback color for character"""
    if is_player:
        return BRIGHT_GREEN
    
    colors = {
        'gareth': (139, 69, 19),    # Brown - Fighter
        'elara': (72, 61, 139),     # Blue - Mage
        'thorman': (184, 134, 11),   # Gold - Cleric  
        'lyra': (47, 79, 47),       # Dark Green - Thief
    }
    return colors.get(character_name, GRAY)