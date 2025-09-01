import pygame
from utils.constants import LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, SPACING
from utils.party_display import load_portrait
from utils.graphics import draw_border, draw_text_with_shadow

def draw_npc_portrait(surface, character_name):
    """
    Draws a scaled NPC portrait on the left side of the image zone.
    
    Args:
        surface: The Pygame surface to draw on.
        character_name: The name of the character (e.g., 'garrick').
    """
    # Define a standard portrait size for consistency
    PORTRAIT_SIZE = (160,160)

    # Try to load the portrait
    npc_portrait = load_portrait(character_name, is_player=False)

    if npc_portrait:
        # Scale the image to the standard size
        scaled_portrait = pygame.transform.scale(npc_portrait, PORTRAIT_SIZE)
        
        # Calculate the position using layout constants  (X -left +right, Y=  -up and +down)
        portrait_x = SPACING['margin'] - 10
        portrait_y = 100 #LAYOUT_IMAGE_Y + LAYOUT_IMAGE_HEIGHT - PORTRAIT_SIZE[1]# - SPACING['margin']
        portrait_rect = scaled_portrait.get_rect(topleft=(portrait_x, portrait_y))
        

        # Draw the scaled portrait and a border
        surface.blit(scaled_portrait, portrait_rect)
        draw_border(surface, portrait_rect.x, portrait_rect.y, portrait_rect.width, portrait_rect.height)
    
    else:
        # Fallback: Draw a gray rectangle and character name
        portrait_rect = pygame.Rect(
            SPACING['margin'],
            LAYOUT_IMAGE_Y + LAYOUT_IMAGE_HEIGHT - PORTRAIT_SIZE[1] - SPACING['margin'],
            PORTRAIT_SIZE[0],
            PORTRAIT_SIZE[1]
        )
        pygame.draw.rect(surface, (100, 100, 100), portrait_rect)
        draw_text_with_shadow(
            surface, 
            character_name.capitalize(), 
            pygame.font.SysFont('timesnewroman', 24),
            portrait_rect.centerx,
            portrait_rect.centery,
        )