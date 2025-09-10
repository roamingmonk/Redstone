"""
Terror in Redstone - Inventory Management Screen
Full-screen popup inventory with equipment management
"""

import pygame

from utils.overlay_utils import (
    draw_popup_background, draw_chunky_border, draw_tab_button,
    draw_item_row, draw_centered_text, draw_button, SELECTION_COLOR, WHITE, BLACK, 
    DARK_GRAY, GRAY, BROWN, BRIGHT_GREEN, CYAN
)

def draw_inventory_screen(surface, game_state, fonts, images=None):
    """Draw the complete inventory management screen"""

   
    # Check if we have required data
    if not hasattr(game_state, 'inventory_tab'):
        print("ERROR: game_state has no inventory_tab")
        return None
        
    if not hasattr(game_state, 'character'):
        print("ERROR: game_state has no character")
        return None
    
  
    # Fill screen with brown background
    draw_popup_background(surface)
    
    # Get character name for title
    character_name = game_state.character.get('name', 'Adventurer')
    
    # Draw title
    title_y = 25
    draw_centered_text(surface, f"{character_name}'s Inventory", 
                      fonts.get('fantasy_large', fonts['header']), title_y, BRIGHT_GREEN)
    
    # Draw main content border
    content_x = 50
    content_y = 120
    content_width = 924  # 1024 - 100 (50px margin each side)
    content_height = 550  # Plenty of room for tabs, table, buttons
    
    draw_chunky_border(surface, content_x, content_y, content_width, content_height)
    
    # Draw category tabs
    tab_y = content_y - 30
    tab_height = 40
    tab_width = 200
    tab_spacing = 25
    
    # Calculate starting position to center all 4 tabs
    total_tab_width = 4 * tab_width + 3 * tab_spacing
    tab_start_x = content_x + (content_width - total_tab_width) // 2
    
    current_tab = game_state.inventory_tab
    
    # Draw the 4 category tabs
    weapons_tab = draw_tab_button(surface, tab_start_x, tab_y, tab_width, tab_height,
                                 "WEAPONS", fonts.get('fantasy_small', fonts['normal']),
                                 active=(current_tab == "weapons"))
    
    armor_tab = draw_tab_button(surface, tab_start_x + tab_width + tab_spacing, tab_y, 
                               tab_width, tab_height, "ARMOR", 
                               fonts.get('fantasy_small', fonts['normal']),
                               active=(current_tab == "armor"))
    
    items_tab = draw_tab_button(surface, tab_start_x + 2 * (tab_width + tab_spacing), tab_y,
                               tab_width, tab_height, "ITEMS",
                               fonts.get('fantasy_small', fonts['normal']),
                               active=(current_tab == "items"))
    
    consumables_tab = draw_tab_button(surface, tab_start_x + 3 * (tab_width + tab_spacing), tab_y,
                                     tab_width, tab_height, "CONSUMABLES",
                                     fonts.get('fantasy_tiny', fonts['small']),
                                     active=(current_tab == "consumables"))
    
    # Draw table header
    table_x = content_x + 20
    table_y = tab_y + tab_height + 20
    table_width = content_width - 40
    header_height = 30
    
 

    
    # Fill content area with same color as active tab
    active_tab_color = (180, 160, 140)  # Same light brown as active tab
    pygame.draw.rect(surface, active_tab_color, 
                    (content_x + 4, content_y + 4, content_width - 8, content_height - 8))


  
    
    # Draw the border around it
    draw_chunky_border(surface, content_x, content_y, content_width, content_height)
        
    # Table column headers
    header_font = fonts.get('fantasy_small', fonts['normal'])
    
    # Column positions
    icon_x = table_x + 10
    desc_x = table_x + 80
    qty_x = table_x + 500
    equipped_x = table_x + 600
    
    # Draw headers based on current tab
    header_surface = header_font.render("Item", True, BLACK)
    surface.blit(header_surface, (icon_x, table_y + 8))
    
    header_surface = header_font.render("Description", True, BLACK)
    surface.blit(header_surface, (desc_x, table_y + 8))
    
    header_surface = header_font.render("Qty", True, BLACK)
    surface.blit(header_surface, (qty_x, table_y + 8))
    
    if current_tab in ["weapons", "armor"]:
        header_surface = header_font.render("Equipped", True, BLACK)
        surface.blit(header_surface, (equipped_x, table_y + 8))
    
    # Store item rectangles for click detection
    item_rects = []
    item_names_in_order = []  
    
    # Display items for current tab
    current_items = game_state.get_items_by_category(current_tab)

    # Display items for current tab
    current_items = game_state.get_items_by_category(current_tab)

    
    if current_items:
        item_font = fonts.get('fantasy_small', fonts['normal'])
        item_y = table_y + header_height + 10
        row_height = 32
        
        for i, item_name in enumerate(current_items):
            # Group items by name and count quantities
            item_counts = {}
            for item in current_items:
                item_counts[item] = item_counts.get(item, 0) + 1

            # Store item names in display order for click detection
            item_names_in_order = list(item_counts.keys())


            # Display unique items with quantities
            for i, (item_name, quantity) in enumerate(item_counts.items()):
                current_row_y = item_y + i * row_height
                
                # Check if this item is selected
                is_selected = (game_state.inventory_selected == item_name)
                
                # Draw row background (highlighted if selected)
                row_width = table_width - 20
                if is_selected:
                    pygame.draw.rect(surface, SELECTION_COLOR, 
                                    (table_x + 10, current_row_y - 2, row_width, row_height))
                
                # Store row rectangle for click detection
                item_rect = pygame.Rect(table_x + 10, current_row_y - 2, row_width, row_height)
                item_rects.append(item_rect)
                
                # Draw item icon
                icon_x_pos = icon_x + 5
                if images and 'item_icons' in images and item_name in images['item_icons']:
                    icon = images['item_icons'][item_name]
                    surface.blit(icon, (icon_x_pos, current_row_y - 5))
                else:
                    icon_surface = item_font.render("X", True, BLACK)
                    surface.blit(icon_surface, (icon_x_pos + 10, current_row_y))
                
                # Draw item details
                desc_surface = item_font.render(item_name, True, BLACK)
                surface.blit(desc_surface, (desc_x, current_row_y))
                
                qty_surface = item_font.render(str(quantity), True, BLACK)
                surface.blit(qty_surface, (qty_x + 10, current_row_y))
                
                if current_tab in ["weapons", "armor"]:
                    is_equipped = game_state.is_item_equipped(item_name)
                    equipped_text = "x" if is_equipped else ""
                    equipped_surface = item_font.render(equipped_text, True, BLACK)
                    surface.blit(equipped_surface, (equipped_x + 20, current_row_y))
    
    try:
        # Action buttons at bottom - initialize all to None first
        equip_button = None
        unequip_button = None
        discard_button = None
        return_button = None
        consume_button = None

        button_y = content_y + content_height + 10  
        button_height = 40
        button_spacing = 20
   

        # Different buttons based on current tab
        if current_tab in ["weapons", "armor"]:
            # EQUIP | UNEQUIP | DISCARD | RETURN
            button_width = 100
            total_width = 4 * button_width + 3 * button_spacing
            start_x = content_x + (content_width - total_width) // 2
            
            equip_button = draw_button(surface, start_x, button_y, button_width, button_height,
                                    "EQUIP", fonts.get('fantasy_small', fonts['normal']))
            
            unequip_button = draw_button(surface, start_x + button_width + button_spacing, button_y, 
                                        button_width, button_height, "UNEQUIP", 
                                        fonts.get('fantasy_small', fonts['normal']))
            
            discard_button = draw_button(surface, start_x + 2 * (button_width + button_spacing), button_y,
                                        button_width, button_height, "DISCARD", 
                                        fonts.get('fantasy_small', fonts['normal']))
            
            return_button = draw_button(surface, start_x + 3 * (button_width + button_spacing), button_y,
                                    button_width, button_height, "RETURN", 
                                    fonts.get('fantasy_small', fonts['normal']))

        elif current_tab == "consumables":
            # CONSUME | DISCARD | RETURN
            button_width = 120
            total_width = 3 * button_width + 2 * button_spacing
            start_x = content_x + (content_width - total_width) // 2
            
            consume_button = draw_button(surface, start_x, button_y, button_width, button_height,
                                        "CONSUME", fonts.get('fantasy_small', fonts['normal']))
            
            discard_button = draw_button(surface, start_x + button_width + button_spacing, button_y,
                                        button_width, button_height, "DISCARD", 
                                        fonts.get('fantasy_small', fonts['normal']))
            
            return_button = draw_button(surface, start_x + 2 * (button_width + button_spacing), button_y,
                                    button_width, button_height, "RETURN", 
                                    fonts.get('fantasy_small', fonts['normal']))

        else:  # items tab
            # DISCARD | RETURN
            button_width = 120
            total_width = 2 * button_width + button_spacing
            start_x = content_x + (content_width - total_width) // 2
            
            discard_button = draw_button(surface, start_x, button_y, button_width, button_height,
                                        "DISCARD", fonts.get('fantasy_small', fonts['normal']))
            
            return_button = draw_button(surface, start_x + button_width + button_spacing, button_y,
                                    button_width, button_height, "RETURN", 
                                    fonts.get('fantasy_small', fonts['normal']))

        # Return tab rectangles for click detection
        tab_rects = (weapons_tab, armor_tab, items_tab, consumables_tab)

        # Return button rectangles based on current tab
        if current_tab in ["weapons", "armor"]:
            button_rects = (equip_button, unequip_button, discard_button, return_button)
        elif current_tab == "consumables":
            button_rects = (consume_button, discard_button, return_button, None)
        else:  # items tab
            button_rects = (discard_button, return_button, None, None)

        # Draw close instruction
        close_y = content_y + content_height + 50
        #close_y = button_y + 10
        close_font = fonts.get('help_text', fonts['small'])
        close_text = "Press I to close"
        
        # Center the close instruction
        close_surface = close_font.render(close_text, True, WHITE)
        close_x = (1024 - close_surface.get_width()) // 2
        surface.blit(close_surface, (close_x, close_y))


        return tab_rects, button_rects, item_rects, item_names_in_order
    
    except Exception as e:
            # Return without buttons if there's an error
            tab_rects = (weapons_tab, armor_tab, items_tab, consumables_tab)
            return tab_rects, (None, None, None, None), [], []