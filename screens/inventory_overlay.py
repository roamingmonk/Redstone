"""
Terror in Redstone - Inventory Overlay
Converted to Universal Overlay System using BaseTabbedOverlay
"""

import pygame
from utils.tabbed_overlay_utils import BaseTabbedOverlay
from utils.constants import *
from utils.graphics import draw_centered_text, draw_text
from utils.overlay_utils import (
    draw_popup_background, draw_chunky_border, draw_tab_button,
    draw_item_row, draw_button, SELECTION_COLOR
)

class InventoryOverlay(BaseTabbedOverlay):
    def __init__(self, screen_manager=None, item_manager=None):
        super().__init__("inventory_key", "INVENTORY", screen_manager)
        self.item_manager = item_manager
        # Add 4 tabs for inventory categories
        self.add_tab("weapons", "WEAPONS", hotkey=pygame.K_1)
        self.add_tab("armor", "ARMOR", hotkey=pygame.K_2) 
        self.add_tab("items", "ITEMS", hotkey=pygame.K_3)
        self.add_tab("consumables", "CONSUMABLES", hotkey=pygame.K_4)
        
        # Initialize inventory-specific data
        self.item_rects = []
        self.item_names_in_order = []
        self.button_rects = {}
    
    def render_tab_content(self, surface, active_tab, game_state, fonts, images):
        """REQUIRED: Render content for the active tab"""
        try:
            # Get current tab category
            current_tab = active_tab.tab_id
            
            # Ensure game_state has inventory_tab for compatibility
            if not hasattr(game_state, 'inventory_tab'):
                game_state.inventory_tab = current_tab
            else:
                game_state.inventory_tab = current_tab
                
            # Use existing inventory rendering logic
            self._render_inventory_content(surface, game_state, fonts, images, current_tab)
            
        except Exception as e:
            print(f"⚠️ Error rendering inventory tab content: {e}")
            # Render fallback content
            content_rect = self.get_content_area_rect()
            draw_centered_text(surface, f"Inventory Error: {e}", 
                             fonts['normal'], content_rect.centery, WHITE, 800)
    
    def _render_inventory_content(self, surface, game_state, fonts, images, current_tab):
        """Render the main inventory content using existing logic"""
        # Get character name for title
        character_name = game_state.character.get('name', 'Adventurer')
        
        # Calculate content area using constants
        content_rect = self.get_content_area_rect()
        content_x = content_rect.x + SPACING['margin']
        content_y = content_rect.y + 60  # Leave room for title
        content_width = content_rect.width - (2 * SPACING['margin'])
        content_height = content_rect.height - 140  # Leave room for title and buttons
        
        # Draw title
        title_y = content_rect.y + 30
        draw_centered_text(surface, f"{character_name}'s Inventory", 
                          fonts.get('fantasy_large', fonts['header']), title_y, BRIGHT_GREEN, 800)
        
        # Fill content area with light brown background
        active_tab_color = (180, 160, 140)
        pygame.draw.rect(surface, active_tab_color, 
                        (content_x, content_y, content_width, content_height))
        
        # Draw content border
        draw_chunky_border(surface, content_x, content_y, content_width, content_height)
        
        # Table setup using constants
        table_x = content_x + SPACING['margin']
        table_y = content_y + SPACING['margin']
        table_width = content_width - (2 * SPACING['margin'])
        header_height = 30
        
        # Draw table headers
        self._draw_table_headers(surface, fonts, table_x, table_y, current_tab)
        
        # Display items for current tab
        self._render_item_list(surface, game_state, fonts, images, current_tab, 
                      table_x, table_y + header_height + 10, table_width, 
                      item_manager=self.item_manager)
        
        # Draw action buttons
        self._render_action_buttons(surface, game_state, fonts, current_tab, 
                                   content_x, content_y + content_height + 10, content_width)
    
    def _draw_table_headers(self, surface, fonts, table_x, table_y, current_tab):
        """Draw table column headers"""
        header_font = fonts.get('fantasy_small', fonts['normal'])
        
        # Column positions
        icon_x = table_x + 10
        desc_x = table_x + 80
        qty_x = table_x + 500
        equipped_x = table_x + 600
        
        # Draw headers
        header_surface = header_font.render("Item", True, BLACK)
        surface.blit(header_surface, (icon_x, table_y + 8))
        
        header_surface = header_font.render("Description", True, BLACK)
        surface.blit(header_surface, (desc_x, table_y + 8))
        
        header_surface = header_font.render("Qty", True, BLACK)
        surface.blit(header_surface, (qty_x, table_y + 8))
        
        if current_tab in ["weapons", "armor"]:
            header_surface = header_font.render("Equipped", True, BLACK)
            surface.blit(header_surface, (equipped_x, table_y + 8))
    
    def _render_item_list(self, surface, game_state, fonts, images, current_tab, 
                         table_x, item_y, table_width, item_manager=None):
        """Render the list of items for current category"""
        # Reset item tracking
        self.item_rects = []
        self.item_names_in_order = []
        
        # Get items for current tab
        current_items = game_state.get_items_by_category(current_tab)
        
        if not current_items:
            # Show "No items" message
            no_items_font = fonts.get('fantasy_small', fonts['normal'])
            no_items_surface = no_items_font.render(f"No {current_tab} in inventory", True, BLACK)
            surface.blit(no_items_surface, (table_x + SPACING['margin'], item_y + SPACING['margin']))
            return
        
        # Group items by name and count quantities
        item_counts = {}
        for item in current_items:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        # Store item names in display order for click detection
        self.item_names_in_order = list(item_counts.keys())
        
        # Display items using standard spacing
        item_font = fonts.get('fantasy_small', fonts['normal'])
        row_height = 32  # Slightly larger than line_height for better readability
        
        # Column positions
        icon_x = table_x + 10
        desc_x = table_x + 80
        qty_x = table_x + 500
        equipped_x = table_x + 600
        
        for i, (item_name, quantity) in enumerate(item_counts.items()):
            current_row_y = item_y + i * row_height
            
            # Check if this item is selected
            is_selected = (getattr(game_state, 'inventory_selected', None) == item_name)
            
            # Draw row background (highlighted if selected)
            row_width = table_width - SPACING['margin']
            if is_selected:
                pygame.draw.rect(surface, SELECTION_COLOR, 
                                (table_x + 10, current_row_y - 2, row_width, row_height))
            
            # Store row rectangle for click detection
            item_rect = pygame.Rect(table_x + 10, current_row_y - 2, row_width, row_height)
            self.item_rects.append(item_rect)
            
            # Draw item icon
            icon_x_pos = icon_x + 5
            if item_manager:
                icon = item_manager.get_item_icon(item_name)
                surface.blit(icon, (icon_x_pos, current_row_y - 5))
            else:
                # Fallback: draw "X" if no ItemManager available
                icon_surface = item_font.render("X", True, BLACK)
                surface.blit(icon_surface, (icon_x_pos + 10, current_row_y))
                print(f"❌ No ItemManager available for icon: {item_name}")

                
            # Convert item ID to display name for rendering
            display_name = item_manager.get_display_name(item_name)

            # Draw item details
            desc_surface = item_font.render(display_name, True, BLACK)
            surface.blit(desc_surface, (desc_x, current_row_y))
            
            qty_surface = item_font.render(str(quantity), True, BLACK)
            surface.blit(qty_surface, (qty_x + 10, current_row_y))
            
            if current_tab in ["weapons", "armor"]:
                is_equipped = game_state.is_item_equipped(item_name)
                equipped_text = "x" if is_equipped else ""
                equipped_surface = item_font.render(equipped_text, True, BLACK)
                surface.blit(equipped_surface, (equipped_x + 20, current_row_y))
    
    def _render_action_buttons(self, surface, game_state, fonts, current_tab, 
                              content_x, button_y, content_width):
        """Render action buttons based on current tab"""
        # Reset button tracking
        self.button_rects = {}
        
        # Use constants for button layout
        button_height = BUTTON_SIZES['small'][1]  # 40
        button_spacing = SPACING['button_gap']    # 20
        
        # Different buttons based on current tab
        if current_tab in ["weapons", "armor"]:
            # EQUIP | UNEQUIP | DISCARD | RETURN
            button_width = 100
            total_width = 4 * button_width + 3 * button_spacing
            start_x = content_x + (content_width - total_width) // 2
            
            self.button_rects['equip'] = draw_button(surface, start_x, button_y, button_width, button_height,
                                    "EQUIP", fonts.get('fantasy_small', fonts['normal']))
            
            self.button_rects['unequip'] = draw_button(surface, start_x + button_width + button_spacing, button_y,
                                     button_width, button_height, "UNEQUIP", 
                                     fonts.get('fantasy_small', fonts['normal']))
            
            self.button_rects['discard'] = draw_button(surface, start_x + 2 * (button_width + button_spacing), button_y,
                                     button_width, button_height, "DISCARD", 
                                     fonts.get('fantasy_small', fonts['normal']))
            
            
        elif current_tab == "consumables":
            # CONSUME | DISCARD | RETURN
            button_width = 120
            total_width = 3 * button_width + 2 * button_spacing
            start_x = content_x + (content_width - total_width) // 2
            
            self.button_rects['consume'] = draw_button(surface, start_x, button_y, button_width, button_height,
                                     "CONSUME", fonts.get('fantasy_small', fonts['normal']))
            
            self.button_rects['discard'] = draw_button(surface, start_x + button_width + button_spacing, button_y,
                                     button_width, button_height, "DISCARD", 
                                     fonts.get('fantasy_small', fonts['normal']))
            
            
        else:  # items tab
            # DISCARD | RETURN
            button_width = 120
            total_width = 2 * button_width + button_spacing
            start_x = content_x + (content_width - total_width) // 2
            
            self.button_rects['discard'] = draw_button(surface, start_x, button_y, button_width, button_height,
                                        "DISCARD", fonts.get('fantasy_small', fonts['normal']))
            
        if not getattr(self, '_buttons_registered', False):
            self.register_standard_buttons(self.button_rects, 'inventory')
            self._buttons_registered = True

        # Draw close instruction
        close_y = button_y + button_height + SPACING['margin'] + 20
        close_font = fonts.get('help_text', fonts['small'])
        close_text = "Press I to close"
        
        # Center the close instruction
        close_surface = close_font.render(close_text, True, WHITE)
        close_x = content_x + (content_width - close_surface.get_width()) // 2
        surface.blit(close_surface, (close_x, close_y))
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks - MUST call parent first for tab functionality"""
        # CRITICAL: Check tab clicks first
        if super().handle_mouse_click(mouse_pos):
            return True
        
        # Get game_state using the correct access pattern
        game_state = None
        if hasattr(self, 'screen_manager'):
            if hasattr(self.screen_manager, '_current_game_state'):
                game_state = self.screen_manager._current_game_state
            elif hasattr(self.screen_manager, 'game_state'):
                game_state = self.screen_manager.game_state

        if not game_state:
            print("⚠️ Cannot access game_state from inventory overlay")
            return False
        
        # Handle item selection clicks (THIS WAS MISSING!)
        for i, item_rect in enumerate(self.item_rects):
            if item_rect.collidepoint(mouse_pos):
                if i < len(self.item_names_in_order):
                    selected_item = self.item_names_in_order[i]
                    # Toggle selection
                    if getattr(game_state, 'inventory_selected', None) == selected_item:
                        game_state.inventory_selected = None  # Deselect
                    else:
                        game_state.inventory_selected = selected_item  # Select
                    return True

               # CHECK ACTION BUTTONS (THIS WAS COMPLETELY MISSING!)
        if hasattr(self, 'button_rects'):
            for button_name, button_rect in self.button_rects.items():
                if button_rect and button_rect.collidepoint(mouse_pos):
                    print(f"🎯 Button clicked: {button_name}")
                    
                    # Emit the appropriate event
                    if hasattr(self, 'screen_manager') and hasattr(self.screen_manager, 'input_handler'):
                        event_type = None
                        if button_name == 'equip':
                            event_type = 'INVENTORY_EQUIP_ITEM'
                        elif button_name == 'unequip':
                            event_type = 'INVENTORY_UNEQUIP_ITEM'
                        elif button_name == 'consume':
                            event_type = 'INVENTORY_CONSUME_ITEM'
                        elif button_name == 'discard':
                            event_type = 'INVENTORY_DISCARD_ITEM'
                        
                        if event_type:
                            print(f"🚀 Emitting event: {event_type}")
                            self.screen_manager.input_handler.event_manager.emit(
                                event_type, 
                                {'button': button_name, 'overlay_type': 'inventory'}
                            )
                            return True
        
        return False
    
    def handle_keyboard_input(self, key):
        """Handle keyboard input - add ESC handling"""
        # Let parent handle tab navigation first
        if super().handle_keyboard_input(key):
            return True
        
        # Handle ESC key to close overlay
        if key == pygame.K_ESCAPE:
            if hasattr(self, 'screen_manager') and hasattr(self.screen_manager, '_current_game_state'):
                game_state = self.screen_manager._current_game_state
                if hasattr(game_state, 'overlay_state'):
                    game_state.overlay_state.close_overlay()  # ✅ FIXED - removed parameter
                    print("🔴 ESC pressed - closing inventory overlay")
                    return True

        return False
        
    def on_overlay_opened(self, game_state):
        """Optional: Called when overlay opens"""
        super().on_overlay_opened(game_state)
        # Always start on weapons tab
        self.switch_to_tab("weapons")
        # Clear any previous selection
        game_state.inventory_selected = None
        print("🎒 Inventory overlay opened")
    
    def on_overlay_closed(self, game_state):
        """Optional: Called when overlay closes"""
        super().on_overlay_closed(game_state)
        # Clear selection when closing
        game_state.inventory_selected = None
        print("🎒 Inventory overlay closed")


# Global instance management
inventory_overlay_instance = None

def get_inventory_overlay():
    """Get the global overlay instance"""
    global inventory_overlay_instance
    if inventory_overlay_instance is None:
        inventory_overlay_instance = InventoryOverlay()
    return inventory_overlay_instance

def draw_inventory_screen(surface, game_state, fonts, images=None):
    """
    REQUIRED: Compatibility function for ScreenManager
    MUST match this exact signature
    """
    overlay = get_inventory_overlay()
    
    # Register with input handler on first render
    if not getattr(overlay, '_input_registered', False):
        try:
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'self' in frame.f_locals:
                screen_manager = frame.f_locals['self']
                if hasattr(screen_manager, 'input_handler'):
                    overlay.screen_manager = screen_manager
                    overlay._register_with_input_handler()
                    overlay._input_registered = True
        except:
            overlay._input_registered = True
    
    overlay.render(surface, game_state, fonts, images)
    return None

def handle_inventory_click(mouse_pos, result):
    """
    REQUIRED: Compatibility function for mouse handling
    MUST match this exact signature
    """
    overlay = get_inventory_overlay()
    return overlay.handle_mouse_click(mouse_pos)

def handle_inventory_keyboard_input(key, game_state):
    """
    REQUIRED: Compatibility function for keyboard handling
    MUST match this exact signature
    """
    overlay = get_inventory_overlay()
    return overlay.handle_keyboard_input(key)