"""
Terror in Redstone - Graphics Utilities
Contains all drawing functions for UI elements, borders, buttons, etc.
"""

import pygame
from .constants import (
     WHITE, GRAY, DARK_GRAY, DARK_BROWN, DARK_GREEN, BLACK,BRIGHT_GREEN, YELLOW,
     BORDER_THICKNESS, BUTTON_SELECTED_BG, BUTTON_SELECTED_BORDER, BUTTON_SELECTED_TEXT,
     BUTTON_NORMAL_TEXT, BUTTON_NORMAL_BG, BUTTON_NORMAL_BORDER
     )

def draw_text_with_shadow(surface, text, font, x, y, text_color=WHITE, shadow_color=DARK_GRAY, shadow_offset=3):
    """
    Draw text with a shadow effect for that classic retro look
    
    Args:
        surface: pygame surface to draw on
        text: text string to render
        font: pygame font object
        x, y: position coordinates
        text_color: color of the main text
        shadow_color: color of the shadow
        shadow_offset: pixel offset for shadow
    
    Returns:
        pygame.Rect: rectangle of the rendered text
    """
    # Draw shadow first
    shadow_surface = font.render(text, True, shadow_color)
    surface.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
    
    # Draw main text on top
    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, (x, y))
    
    return text_surface.get_rect(x=x, y=y)

def draw_border(surface, x, y, width, height):
    """
    Draw a chunky retro border with that classic 1980s adventure game look
    
    Args:
        surface: pygame surface to draw on
        x, y: top-left corner position
        width, height: border dimensions
    """
    # Outer white border (thick)
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 3)
    # Inner gray border (thin)
    pygame.draw.rect(surface, GRAY, (x+3, y+3, width-6, height-6), 2)

def calculate_best_font_for_button(text, max_width, fonts_to_try):
    """
    Calculate the best font size that fits in the button
    
    Args:
        text: text string to fit
        max_width: maximum width available
        fonts_to_try: list of font objects to try (largest to smallest)
    
    Returns:
        pygame.Font: best fitting font object
    """
    for font in fonts_to_try:
        text_surface = font.render(text, True, DARK_BROWN)
        if text_surface.get_width() <= max_width - 10:  # 10px padding
            return font
    return fonts_to_try[-1]  # Return smallest font if none fit

def draw_combat_button(surface, x, y, width, height, text, font, button_state="normal"):
    """
    Draw combat-specific buttons with proper visual states
    
    Args:
        surface: Pygame surface to draw on
        x, y: Button position
        width, height: Button dimensions
        text: Button text
        font: Font to use
        button_state: "normal", "active", "disabled"
    """
    # Define colors based on state
    if button_state == "active":
        # Active mode selected - Yellow border to stand out
        bg_color = DARK_GREEN
        text_color = BRIGHT_GREEN
        border_color = YELLOW  # ⭐ Changed from BRIGHT_GREEN
        border_width = 3  # Thicker border for visibility
    elif button_state == "disabled":
        # Disabled - All gray
        bg_color = DARK_GRAY
        text_color = GRAY
        border_color = GRAY
        border_width = 1
    else:  # normal (available but not selected)
        # Normal - Green button, gray border, green text
        bg_color = DARK_GREEN
        text_color = BRIGHT_GREEN
        border_color = DARK_GREEN
        border_width = 1
    
    # Draw button background
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, button_rect)
    pygame.draw.rect(surface, border_color, button_rect, border_width)
    
    # Draw button text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=button_rect.center)
    surface.blit(text_surface, text_rect)
    
    return

def draw_button(surface, x, y, width, height, text, font, selected=False, text_color=None, bg_color=None):
    """
    Draw a retro-style button with authentic 1980s look

    Args:
        surface: pygame surface to draw on
        x, y: button position
        width, height: button dimensions
        text: button text
        font: font object for text
        selected: if True, draw selected/highlighted appearance
        text_color: optional color override for text (uses defaults if None)
        bg_color: optional color override for button background (uses defaults if None)

    Returns:
        pygame.Rect: clickable area of the button
    """
    # Determine colors based on button state
    if selected:
        default_bg_color = BUTTON_SELECTED_BG
        border_color = BUTTON_SELECTED_BORDER
        default_text_color = BUTTON_SELECTED_TEXT
    else:
        default_bg_color = BUTTON_NORMAL_BG
        border_color = BUTTON_NORMAL_BORDER
        default_text_color = BUTTON_NORMAL_TEXT

    # Use overrides if provided, otherwise use defaults
    final_bg_color = bg_color if bg_color is not None else default_bg_color
    final_text_color = text_color if text_color is not None else default_text_color

    # Draw button background
    pygame.draw.rect(surface, final_bg_color, (x, y, width, height))
    # Draw button border
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
    
    # Draw centered text
    text_surface = font.render(text, True, final_text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    surface.blit(text_surface, text_rect)
    
    # Return clickable area
    return pygame.Rect(x, y, width, height)

def draw_centered_text(surface, text, font, y_position, color=WHITE, screen_width=1024):
    """
    Draw text centered horizontally on the screen
    
    Industry standard implementation with consistent parameters and return value.
    This is the ONE TRUE draw_centered_text function - all others should be removed.
    
    Args:
        surface: pygame surface to draw on
        text: text string to render
        font: pygame font object
        y_position: vertical position for the text
        color: text color (default WHITE)
        screen_width: width of screen for centering calculation (default 1024)
    
    Returns:
        pygame.Rect: rectangle of the rendered text for collision detection
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen_width//2, y_position))
    surface.blit(text_surface, text_rect)
    return text_rect



def draw_text(surface, text, font, x_position, y_position, color):
    """
    Draw text centered horizontally on the screen
    
    Args:
        surface: pygame surface to draw on
        text: text string to render
        font: pygame font object
        y_position: vertical position
        color: text color
        screen_width: width of screen for centering calculation
    
    Returns:
        pygame.Rect: rectangle of the rendered text
    """
    text_surface = font.render(text, True, color)
    #text_rect = text_surface.get_rect(center=(screen_width//2, y_position))
    text_rect = text_surface.get_rect()
    #text_rect = text_surface.get_rect(text, True, color)
    
    text_rect.x = x_position   
    text_rect.y = y_position
    surface.blit(text_surface, text_rect)
    
def draw_image_with_border(surface, image, x, y, width, height):
    """
    Draw an image with a matching chunky border
    
    Args:
        surface: pygame surface to draw on
        image: pygame image object (or None for placeholder)
        x, y: position
        width, height: total area including border
    
    Returns:
        tuple: (img_x, img_y, img_width, img_height) - actual image area within border
    """
    # Draw border around entire area
    draw_border(surface, x, y, width, height)
    
    # Calculate image area within border
    img_x = x + BORDER_THICKNESS
    img_y = y + BORDER_THICKNESS
    img_width = width - 2 * BORDER_THICKNESS
    img_height = height - 2 * BORDER_THICKNESS
    
    if image:
        # Scale image to fit within border
        scaled_image = pygame.transform.scale(image, (img_width, img_height))
        surface.blit(scaled_image, (img_x, img_y))
    else:
        # Draw placeholder rectangle
        pygame.draw.rect(surface, (50, 50, 100), (img_x, img_y, img_width, img_height))
    
    return (img_x, img_y, img_width, img_height)

def create_input_box(surface, x, y, width, height, text, font, active=False, placeholder=""):
    """
    Draw a text input box with cursor support
    
    Args:
        surface: pygame surface to draw on
        x, y: position
        width, height: box dimensions
        text: current text in box
        font: font object
        active: if True, draw active state with cursor
        placeholder: placeholder text when empty
    
    Returns:
        pygame.Rect: clickable area of input box
    """
    # Draw input box border
    input_color = WHITE if active else (200, 200, 200)  # LIGHT_GRAY
    pygame.draw.rect(surface, input_color, (x, y, width, height), 2)
    pygame.draw.rect(surface, BLACK, (x + 2, y + 2, width - 4, height - 4))
    
    # Draw text or placeholder
    if text:
        text_surface = font.render(text, True, WHITE)
    elif placeholder:
        text_surface = font.render(placeholder, True, GRAY)
    else:
        text_surface = font.render("", True, WHITE)
    
    text_rect = text_surface.get_rect(centery=y + height // 2, x=x + 10)
    surface.blit(text_surface, text_rect)
    
    # Draw blinking cursor when active
    if active and pygame.time.get_ticks() % 1000 < 500:
        cursor_x = text_rect.right + 5 if text else x + 10
        pygame.draw.line(surface, WHITE, (cursor_x, y + 10), (cursor_x, y + height - 10), 2)
    
    return pygame.Rect(x, y, width, height)