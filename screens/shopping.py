"""
Terror in Redstone - Generic Shopping System
Reusable merchant screen for all shops in the game
"""

import pygame

from utils.constants import (LAYOUT_IMAGE_Y, LAYOUT_IMAGE_HEIGHT, 
                           LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT,
                           LAYOUT_BUTTON_Y, LAYOUT_DIALOG_TEXT_Y, LAYOUT_BUTTON_CENTER_Y)

from game_logic.item_manager import item_manager  

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
DARK_GRAY = (85, 85, 85)
BRIGHT_GREEN = (85, 255, 85)
YELLOW = (255, 255, 85)
CYAN = (0, 255, 255)
RED = (170, 0, 0)
DARK_BROWN = (101, 67, 33)

def draw_border(surface, x, y, width, height):
    """Draw a chunky retro border"""
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 3)
    pygame.draw.rect(surface, GRAY, (x+3, y+3, width-6, height-6), 2)

def draw_button(surface, x, y, width, height, text, font, pressed=False, selected=False, enabled=True):
    """Draw a retro-style button"""
    if not enabled:
        color = DARK_GRAY
        border_color = DARK_GRAY
        text_color = (60, 60, 60)
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

def draw_merchant_screen(surface, game_state, fonts, merchant_data, images=None):
    """
    Table-style merchant screen matching the mockup design
    """
    surface.fill(BLACK)
    
    # Use standardized layout
    image_y = LAYOUT_IMAGE_Y
    image_height = LAYOUT_IMAGE_HEIGHT
    
    draw_border(surface, 0, image_y, 1024, image_height)
    
    # Main content area
    border_thickness = 6
    content_x = border_thickness
    content_y = image_y + border_thickness
    content_width = 1024 - 2 * border_thickness
    content_height = image_height - 2 * border_thickness
    
    # Brown background for shop atmosphere
    pygame.draw.rect(surface, (60, 40, 20), (content_x, content_y, content_width, content_height))
    
    # === MERCHANT STOCK TABLE ===
    
    # Merchant title
    title_y = content_y + 20
    draw_centered_text(surface, f"{merchant_data['merchant_name']}'s Stock", 
                      fonts.get('fantasy_medium', fonts['normal']), title_y, YELLOW)
    
    # Table headers
    header_y = title_y + 40
    header_font = fonts.get('fantasy_small', fonts['normal'])
    
    # Column positions
    icon_x = content_x + 30
    desc_x = content_x + 140
    cost_x = content_x + 450
    qty_x = content_x + 550
    purchase_x = content_x + 650
    
    # Draw headers
    header_surface = header_font.render("Item", True, CYAN)
    surface.blit(header_surface, (icon_x, header_y))
    
    header_surface = header_font.render("Description", True, CYAN)
    surface.blit(header_surface, (desc_x, header_y))
    
    header_surface = header_font.render("Cost", True, CYAN)
    surface.blit(header_surface, (cost_x, header_y))
    
    header_surface = header_font.render("Qty Avail", True, CYAN)
    surface.blit(header_surface, (qty_x, header_y))

    header_surface = header_font.render("Purchase", True, CYAN)
    surface.blit(header_surface, (purchase_x + 10, header_y))  # Move Purchase header right
    
    # Merchant items
    item_font = fonts.get('fantasy_tiny', fonts['small'])
    item_y = header_y + 30
    line_height = 32
    
    merchant_item_rects = []  # Store clickable areas for items
    
    for i, item in enumerate(merchant_data['items']):
        current_y = item_y + i * line_height
        
        # Icon placeholder (X for now)
        # Draw item icon
        # Draw item icon
        if images and 'item_icons' in images and item['name'] in images['item_icons']:
            icon = images['item_icons'][item['name']]
            surface.blit(icon, (icon_x + 5, current_y - 5))
        else:
            # Fallback to X if no icon system
            icon_surface = item_font.render("X", True, WHITE)
            surface.blit(icon_surface, (icon_x + 10, current_y))
        
        # Description
        desc_surface = item_font.render(item['description'], True, WHITE)
        surface.blit(desc_surface, (desc_x, current_y))
        
        # Cost
        cost_surface = item_font.render(str(item['cost']), True, WHITE)
        surface.blit(cost_surface, (cost_x + 10, current_y))
        
        # Available quantity - each item has limited stock (Hardcoded)
        qty_available = 5
        qty_surface = item_font.render(str(qty_available), True, WHITE)
        surface.blit(qty_surface, (qty_x + 20, current_y))
        
        # Purchase quantity
        purchase_qty = game_state.shopping_cart.get(item['name'], 0)
        purchase_surface = item_font.render(str(purchase_qty), True, BRIGHT_GREEN)
        surface.blit(purchase_surface, (purchase_x + 20, current_y))
        
        # Store clickable area for this item
        item_rect = pygame.Rect(icon_x, current_y, purchase_x + 50 - icon_x, line_height)
        merchant_item_rects.append(item_rect)
    
    # === PLAYER INVENTORY TABLE ===
    
    inventory_y = item_y + len(merchant_data['items']) * line_height + 40
    
    # Player inventory title
    character_name = game_state.character.get('name', 'Adventurer')
    draw_centered_text(surface, f"{character_name}'s Inventory", 
                      fonts.get('fantasy_medium', fonts['normal']), inventory_y, YELLOW)
    
    # Inventory headers
    inv_header_y = inventory_y + 30
    
    header_surface = header_font.render("Item", True, CYAN)
    surface.blit(header_surface, (icon_x, inv_header_y))
    
    header_surface = header_font.render("Description", True, CYAN)
    surface.blit(header_surface, (desc_x, inv_header_y))
    
    header_surface = header_font.render("Qty", True, CYAN)
    surface.blit(header_surface, (qty_x, inv_header_y))
    
    # Display inventory items
    inv_item_y = inv_header_y + 25
    all_items = []
    
    # Combine all inventory categories
    for category in ['weapons', 'armor', 'items', 'consumables']:
        for item in game_state.inventory.get(category, []):
            all_items.append(item)
    
    # Count quantities and display unique items
    item_counts = {}
    for item in all_items:
        item_counts[item] = item_counts.get(item, 0) + 1
    
    for i, (item_name, quantity) in enumerate(item_counts.items()):
        current_y = inv_item_y + i * 32  # Smaller line height for inventory
        
        # Draw item icon
        if images and 'item_icons' in images and item_name in images['item_icons']:
            icon = images['item_icons'][item_name]
            surface.blit(icon, (icon_x + 5, current_y - 5))
        else:
            # Fallback to X if no icon system
            icon_surface = item_font.render("X", True, WHITE)
            surface.blit(icon_surface, (icon_x + 10, current_y))
        
        # Item name as description
        desc_surface = item_font.render(item_name, True, WHITE)
        surface.blit(desc_surface, (desc_x, current_y))
        
        # Quantity
        qty_surface = item_font.render(str(quantity), True, WHITE)
        surface.blit(qty_surface, (qty_x + 20, current_y))
    
    # === DIALOG AREA ===
    
    dialog_y = LAYOUT_DIALOG_Y
    dialog_height = LAYOUT_DIALOG_HEIGHT
    draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
    
    # Player gold and cart total
    text_y = LAYOUT_DIALOG_TEXT_Y
    from game_logic.player_manager import player_manager
    player_gold = player_manager.get_player_gold()
    cart_total = game_state.get_cart_total(merchant_data)
    
    draw_centered_text(surface, f"Your Gold: {player_gold} gp", 
                      fonts.get('fantasy_medium', fonts['normal']), text_y, BRIGHT_GREEN)
    
    draw_centered_text(surface, f"Cart Total: {cart_total} gp", 
                      fonts.get('fantasy_small', fonts['normal']), text_y + 25, YELLOW)
    
    # Instructions
    instructions = "Click items above to add to cart. Use buttons below to complete purchase."
    draw_centered_text(surface, instructions, 
                      fonts.get('fantasy_tiny', fonts['small']), text_y + 50, WHITE)
    
    # === ACTION BUTTONS ===
    
    button_y = LAYOUT_BUTTON_CENTER_Y
    button_height = 40
    button_width = 100
    button_spacing = 20
    
    # Center the three action buttons
    total_width = 3 * button_width + 2 * button_spacing
    start_x = (1024 - total_width) // 2
    
    # Check if player can afford cart
    can_afford_cart = cart_total <= player_gold and cart_total > 0
    has_items_in_cart = cart_total > 0

    buy_button = draw_button(surface, start_x, button_y, button_width, button_height,
                            "BUY", fonts.get('fantasy_small', fonts['normal']),
                            enabled=can_afford_cart)

    reset_button = draw_button(surface, start_x + button_width + button_spacing, button_y, 
                            button_width, button_height, "RESET", 
                            fonts.get('fantasy_small', fonts['normal']),
                            enabled=has_items_in_cart)
        
    back_button = draw_button(surface, start_x + 2 * (button_width + button_spacing), button_y,
                             button_width, button_height, "BACK", 
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
    
    return merchant_item_rects, buy_button, reset_button, back_button