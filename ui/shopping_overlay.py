"""
Terror in Redstone - Generic Shopping System
Reusable merchant screen for all shops in the game
"""

import pygame
from utils.tabbed_overlay_utils import BaseTabbedOverlay, TabDefinition
from collections import Counter
from utils.graphics import draw_centered_text
from utils.constants import (CORNFLOWER_BLUE, BLACK, WHITE, CYAN, RED, WARNING_RED, SOFT_YELLOW,
                             DARK_GRAY, DARKEST_GRAY, BRIGHT_GREEN, DARK_BROWN, OVERLAY_STATUS_BAR_HEIGHT)
from game_logic.item_manager import item_manager, get_rarity_level

# trying to fix get_cart_total pull 
from game_logic.commerce_engine import get_commerce_engine


# ==========================================
# TABBED SHOPPING OVERLAY CLASS (NEW)
# ==========================================

class ShoppingOverlay(BaseTabbedOverlay):
    """
    Tabbed shopping interface using BaseTabbedOverlay framework
    
    Tabs:
    - BUY (B): Purchase from merchant stock
    - SELL (S): Sell items to merchant
    - INFO (I): View merchant details
    """
    
    def __init__(self, screen_manager=None):
        super().__init__("merchant_shop", "MERCHANT", screen_manager)
        
        self.status_bar_height = 55 

        # Add 3 tabs - using keys B, S, I for tab switching
        self.add_tab("buy", "BUY")
        self.add_tab("sell", "SELL")
        self.add_tab("info", "INFO")
        
        # Tab-specific pagination state
        self.buy_page = 0
        self.sell_page = 0
        self.items_per_page = 7
        #self.info_page = 0

        # Hover Tracking
        self.hovered_item_id = None 

        # Track current merchant to detect changes
        self.current_merchant_id = None

        # Click tracking
        self.merchant_item_rects = []
        self.sell_item_rects = []
        self.button_rects = {}

        # Sell cart tracking (separate from buy cart)
        self.sell_cart = {}  # {item_name: quantity}
        self.sell_cart_total = 0
    
    def on_overlay_opened(self, game_state):
        """Reset state when opening shopping overlay"""
        super().on_overlay_opened(game_state)
        # Always start on BUY tab
        self.switch_to_tab(0)
        # Clear any hovered item from previous session
        self.hovered_item_id = None
        print("🛒 Shopping overlay opened - reset to BUY tab")
    
    def render_tab_content(self, surface, active_tab, game_state, fonts, images):
        """
        REQUIRED: Render content for the active tab
        Called by BaseTabbedOverlay.render()
        """
        tab_id = active_tab.tab_id
        content_rect = self.get_content_area_rect()
        
        # Detect merchant change and reset to BUY tab
        merchant_data = getattr(game_state, 'current_merchant_data', None)
        if merchant_data:
            merchant_id = merchant_data.get('merchant_id')
            if merchant_id != self.current_merchant_id:
                # New merchant detected - reset to BUY tab
                self.current_merchant_id = merchant_id
                self.switch_to_tab(0)  # Switch to BUY tab
                self.hovered_item_id = None  # Clear hover
                print(f"🛒 New merchant detected: {merchant_id} - reset to BUY tab")
        
        try:
            if tab_id == "buy":
                self._render_buy_tab(surface, content_rect, game_state, fonts, images)
            elif tab_id == "sell":
                self._render_sell_tab(surface, content_rect, game_state, fonts, images)
            elif tab_id == "info":
                self._render_info_tab(surface, content_rect, game_state, fonts, images)
        except Exception as e:
            print(f"⚠️ Error rendering {tab_id} tab: {e}")
            draw_centered_text(surface, f"Error: {e}", fonts['normal'], 
                             content_rect.centery, WHITE)
    
    def _render_buy_tab(self, surface, content_rect, game_state, fonts, images):
        """ BUY tab - Show merchant stock with purchase options
        Reuses existing shopping logic with pagination  """
        
        # Clear any stale hover state at start of rendering
        self.hovered_item_id = None

        merchant_data = getattr(game_state, 'current_merchant_data', None)

        if not merchant_data:
            draw_centered_text(surface, "No merchant data available", 
                             fonts['normal'], content_rect.centery, WHITE)
            return
        
        commerce = get_commerce_engine()
        merchant_id = merchant_data.get('merchant_id')
        
        # Title
        title_y = content_rect.y + 20
        draw_centered_text(surface, f"{merchant_data['merchant_name']}'s Stock",
                          fonts.get('fantasy_medium', fonts['normal']), title_y, SOFT_YELLOW)
        
        # Table headers (adjusted for smaller content area)
        header_y = title_y + 35
        header_font = fonts.get('fantasy_small', fonts['normal'])
        
        # Column positions (adjusted for content_rect)
        icon_x = content_rect.x + 20
        desc_x = content_rect.x + 100
        cost_x = content_rect.x + 420
        stock_x = content_rect.x + 520
        cart_x = content_rect.x + 620
        
        # Draw headers
        header_surface = header_font.render("Item", True, CYAN)
        surface.blit(header_surface, (icon_x, header_y))
        
        header_surface = header_font.render("Description", True, CYAN)
        surface.blit(header_surface, (desc_x, header_y))
        
        header_surface = header_font.render("Cost", True, CYAN)
        surface.blit(header_surface, (cost_x, header_y))
        
        header_surface = header_font.render("Stock", True, CYAN)
        surface.blit(header_surface, (stock_x, header_y))
        
        header_surface = header_font.render("Cart", True, CYAN)
        surface.blit(header_surface, (cart_x, header_y))
        
        # Draw merchant items with pagination
        items = merchant_data.get('items', [])
        total_items = len(items)
        
        # Pagination calculations
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        if self.buy_page >= total_pages:
            self.buy_page = total_pages - 1
        
        start_idx = self.buy_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = items[start_idx:end_idx]
        
        # Draw items
        self.merchant_item_rects = []
        item_font = fonts.get('fantasy_tiny', fonts['small'])
        item_y = header_y + 30
        line_height = 32
        
        # Reset hovered item at start of rendering
        self.hovered_item_id = None
        
        for i, item in enumerate(page_items):
            current_y = item_y + i * line_height
            
            # Create clickable rect and check hover
            item_rect = pygame.Rect(icon_x - 5, current_y - 5,
                                   cart_x - icon_x + 100, line_height)
            
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = item_rect.collidepoint(mouse_pos)
            
            if is_hovered:
                SELECTION_COLOR = (100, 149, 237)
                pygame.draw.rect(surface, SELECTION_COLOR, item_rect)
                # Store hovered item ID for status bar
                self.hovered_item_id = item['item_id']
            
            # Store for click detection (with original index)
            self.merchant_item_rects.append((item_rect, start_idx + i))
            
            # Draw item details
            item_id = item['item_id']
            
            # Icon
            icon = game_state.item_manager.get_item_icon(item_id)
            surface.blit(icon, (icon_x + 5, current_y - 5))
            
            # Description
            desc_surface = item_font.render(item['name'], True, WHITE)
            surface.blit(desc_surface, (desc_x, current_y))
            
            # Cost
            cost_surface = item_font.render(str(item['cost']), True, WHITE)
            surface.blit(cost_surface, (cost_x + 10, current_y))
            
            # Stock
            stock_info = commerce.get_stock_status(item_id, merchant_id)
            stock_surface = item_font.render(str(stock_info['available']), True, WHITE)
            surface.blit(stock_surface, (stock_x + 20, current_y))
            
            # Cart quantity
            cart_qty = game_state.shopping_cart.get(item_id, 0)
            if cart_qty > 0:
                cart_surface = item_font.render(str(cart_qty), True, BRIGHT_GREEN)
                surface.blit(cart_surface, (cart_x + 20, current_y))
        
        # Calculate positioning - status bar goes right after items
        status_bar_y = item_y + (self.items_per_page * line_height) + 10
        
        # Render status bar if item is hovered
        if self.hovered_item_id:
            try:
                full_desc = game_state.item_manager.get_item_full_description(self.hovered_item_id)
                self._render_status_bar(surface, fonts, full_desc, status_bar_y)
            except Exception as e:
                print(f"⚠️ Error rendering status bar: {e}")
        
        # Gold and cart summary (below status bar)
        
        gold_y = status_bar_y + OVERLAY_STATUS_BAR_HEIGHT + 15
        
        player_gold = game_state.character.get('gold', 0)
        cart_total = commerce.get_cart_total(merchant_id)
        
        gold_summary = f"Your Gold: {player_gold} gp  --  Cart Total: {cart_total} gp"
        gold_font = fonts.get('fantasy_small', fonts['normal'])  # Smaller font
        gold_surface = gold_font.render(gold_summary, True, BRIGHT_GREEN)
        # Center the text
        gold_x = content_rect.x + (content_rect.width - gold_surface.get_width()) // 2
        surface.blit(gold_surface, (gold_x, gold_y))
        
        # Action buttons (below gold summary)
        button_y = gold_y + 30
        button_width = 100
        button_spacing = 20
        
        total_width = 3 * button_width + 2 * button_spacing
        start_x = content_rect.x + (content_rect.width - total_width) // 2
        
        can_afford = commerce.can_afford_cart(merchant_id)
        has_items = cart_total > 0
        
        self.button_rects['buy'] = draw_button(
            surface, start_x, button_y, button_width, 40,
            "BUY", fonts.get('fantasy_small', fonts['normal']),
            enabled=can_afford)
        
        self.button_rects['reset'] = draw_button(
            surface, start_x + button_width + button_spacing, button_y,
            button_width, 40, "RESET",
            fonts.get('fantasy_small', fonts['normal']),
            enabled=has_items)
        
        self.button_rects['close'] = draw_button(
            surface, start_x + 2 * (button_width + button_spacing), button_y,
            button_width, 40, "CLOSE",
            fonts.get('fantasy_small', fonts['normal']))
        
        # Pagination text - bottom right corner
        if total_pages > 1:
            page_text = f"Page {self.buy_page + 1} of {total_pages}"
            page_font = fonts.get('fantasy_small', fonts['normal'])
            page_surface = page_font.render(page_text, True, SOFT_YELLOW)
            page_x = content_rect.right - page_surface.get_width() - 10  # Right-aligned
            page_y = button_y + 10  # Aligned with buttons
            surface.blit(page_surface, (page_x, page_y))

    def _render_sell_tab(self, surface, content_rect, game_state, fonts, images):
        """SELL tab - player inventory with buyback pricing"""
        
        # Clear any stale hover state at start of rendering
        self.hovered_item_id = None
        
        merchant_data = getattr(game_state, 'current_merchant_data', None)
        if not merchant_data:
            return
        
        merchant_id = merchant_data.get('merchant_id')
        
        # Get merchant config for sell multiplier
        merchant_config = game_state.item_manager.merchant_data.get('merchants', {}).get(merchant_id, {})
        sell_multiplier = merchant_config.get('sell_multiplier', 0.4)
        stock_categories = merchant_config.get('stock_categories', [])

        # Use buy_categories (what merchant BUYS), not stock_categories (what they SELL)
        buy_categories = merchant_config.get('buy_categories', stock_categories)
        
        # Title
        title_y = content_rect.y + 20
        draw_centered_text(surface, f"Sell Items to {merchant_data['merchant_name']}",
                        fonts.get('fantasy_medium', fonts['normal']), title_y, SOFT_YELLOW)
        
        # Table headers
        header_y = title_y + 35
        header_font = fonts.get('fantasy_small', fonts['normal'])
        
        icon_x = content_rect.x + 20
        desc_x = content_rect.x + 100
        value_x = content_rect.x + 400
        sell_price_x = content_rect.x + 500
        qty_x = content_rect.x + 600
        cart_x = content_rect.x + 700

        
        # Draw headers
        header_surface = header_font.render("Item", True, CYAN)
        surface.blit(header_surface, (icon_x, header_y))
        
        header_surface = header_font.render("Description", True, CYAN)
        surface.blit(header_surface, (desc_x, header_y))
        
        header_surface = header_font.render("Value", True, CYAN)
        surface.blit(header_surface, (value_x, header_y))
        
        header_surface = header_font.render("Sell For", True, CYAN)
        surface.blit(header_surface, (sell_price_x, header_y))
        
        header_surface = header_font.render("Qty", True, CYAN)
        surface.blit(header_surface, (qty_x, header_y))

        header_surface = header_font.render("Cart", True, CYAN)
        surface.blit(header_surface, (cart_x, header_y))
        
        # Get sellable items from player inventory
        sellable_items = self._get_sellable_items(game_state, merchant_id, buy_categories, sell_multiplier)

        # Draw items
        self.sell_item_rects = []
        item_font = fonts.get('fantasy_tiny', fonts['small'])
        item_y = header_y + 30
        line_height = 32
        
        # Add pagination calculations (after getting sellable_items)
        total_items = len(sellable_items)

        # Pagination calculations
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        if self.sell_page >= total_pages:
            self.sell_page = total_pages - 1

        start_idx = self.sell_page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, total_items)
        page_items = sellable_items[start_idx:end_idx]

        # Reset hovered item at start of rendering
        if not hasattr(self, 'hovered_item_id'):
            self.hovered_item_id = None
        
        # Update the item loop
        for i, item_data in enumerate(page_items):
            current_y = item_y + i * line_height
            
            # Create clickable rect
            item_rect = pygame.Rect(icon_x - 5, current_y - 5,
                                qty_x - icon_x + 100, line_height)
            
            # Hover highlight
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = item_rect.collidepoint(mouse_pos)
            
            if is_hovered:
                pygame.draw.rect(surface, CORNFLOWER_BLUE, item_rect)
                # Store hovered item ID for status bar
                self.hovered_item_id = item_data['item_id']
            
            # Store for click detection (with original index)
            self.sell_item_rects.append((item_rect, start_idx + i))
            
            # Draw item details
            item_name = item_data['name']
            
            # Get icon directly from ItemManager  
            item_id = item_data['item_id']  # Use the ID field from merchant data
            icon = game_state.item_manager.get_item_icon(item_id)
            
            surface.blit(icon, (icon_x + 5, current_y - 5))
            
            # Description
            desc_surface = item_font.render(item_name, True, WHITE)
            surface.blit(desc_surface, (desc_x, current_y))
            
            # Original value
            value_surface = item_font.render(str(item_data['base_cost']), True, WHITE)
            surface.blit(value_surface, (value_x + 10, current_y))
            
            # Sell price
            sell_surface = item_font.render(str(item_data['sell_price']), True, BRIGHT_GREEN)
            surface.blit(sell_surface, (sell_price_x + 10, current_y))
            
            # Quantity
            qty_surface = item_font.render(str(item_data['quantity']), True, WHITE)
            surface.blit(qty_surface, (qty_x + 20, current_y))

            #Cart Qty    
            item_id = item_data.get('item_id', item_name)
            cart_qty = self.sell_cart.get(item_id, 0)
            if cart_qty > 0:
                cart_surface = item_font.render(str(cart_qty), True, BRIGHT_GREEN)
                surface.blit(cart_surface, (cart_x + 20, current_y))

        # Handle "no items" case
        if not sellable_items:
            no_items_y = content_rect.centery
            draw_centered_text(surface, f"No items to sell to {merchant_data['merchant_name']}",
                            fonts['normal'], no_items_y, WHITE)
            return  # Exit early if no items
        
        # Calculate positioning - status bar goes right after items
        status_bar_y = item_y + (self.items_per_page * line_height) + 10
        
        # Render status bar if item is hovered
        if self.hovered_item_id:
            try:
                full_desc = game_state.item_manager.get_item_full_description(self.hovered_item_id)
                self._render_status_bar(surface, fonts, full_desc, status_bar_y)
            except Exception as e:
                print(f"⚠️ Error rendering status bar: {e}")
        
        # Gold and sell cart summary (below status bar)
        from utils.constants import OVERLAY_STATUS_BAR_HEIGHT
        gold_y = status_bar_y + OVERLAY_STATUS_BAR_HEIGHT + 15
        
        player_gold = game_state.character.get('gold', 0)
        
        # Calculate sell cart total
        self.sell_cart_total = sum(
            item_data['sell_price'] * qty 
            for item_data, qty in [(self._get_item_data_by_name(item_name, sellable_items), qty) 
                                for item_name, qty in self.sell_cart.items()]
            if item_data
        )
        
        sell_summary = f"Your Gold: {player_gold} gp  --  Sell Total: +{self.sell_cart_total} gp"
        gold_font = fonts.get('fantasy_small', fonts['normal'])  # Smaller font
        gold_surface = gold_font.render(sell_summary, True, BRIGHT_GREEN)
        # Center the text
        gold_x = content_rect.x + (content_rect.width - gold_surface.get_width()) // 2
        surface.blit(gold_surface, (gold_x, gold_y))
        
        # Action buttons (below gold summary)
        button_y = gold_y + 30
        button_width = 100
        button_spacing = 20
        
        total_width = 3 * button_width + 2 * button_spacing
        start_x = content_rect.x + (content_rect.width - total_width) // 2
        
        has_items = len(self.sell_cart) > 0
        
        self.button_rects['sell'] = draw_button(
            surface, start_x, button_y, button_width, 40,
            "SELL", fonts.get('fantasy_small', fonts['normal']),
            enabled=has_items)
        
        self.button_rects['clear'] = draw_button(
            surface, start_x + button_width + button_spacing, button_y,
            button_width, 40, "CLEAR",
            fonts.get('fantasy_small', fonts['normal']),
            enabled=has_items)
        
        self.button_rects['close'] = draw_button(
            surface, start_x + 2 * (button_width + button_spacing), button_y,
            button_width, 40, "CLOSE",
            fonts.get('fantasy_small', fonts['normal']))
        
        # Pagination text - bottom right corner
        if total_pages > 1:
            page_text = f"Page {self.sell_page + 1} of {total_pages}"
            page_font = fonts.get('fantasy_small', fonts['normal'])
            page_surface = page_font.render(page_text, True, SOFT_YELLOW)
            page_x = content_rect.right - page_surface.get_width() - 10  # Right-aligned
            page_y = button_y + 10  # Aligned with buttons
            surface.blit(page_surface, (page_x, page_y))

    def _get_item_data_by_name(self, item_name, sellable_items):
        """Helper to find item data by name"""
        return next((item for item in sellable_items if item['name'] == item_name), None)
    
    def _render_info_tab(self, surface, content_rect, game_state, fonts, images):
        """
        INFO tab - Merchant details and lore
        """
        merchant_data = getattr(game_state, 'current_merchant_data', None)
        if not merchant_data:
            return
        
        # Title - Merchant Name
        title_y = content_rect.y + 20
        draw_centered_text(surface, merchant_data['merchant_name'],
                          fonts.get('fantasy_medium', fonts['normal']), title_y, SOFT_YELLOW)
        
        # Greeting
        greeting_y = content_rect.y + 70
        greeting = merchant_data.get('greeting', 'Welcome!')
        draw_centered_text(surface, f'"{greeting}"',
                          fonts['normal'], greeting_y, WHITE)
        
        # Merchant details
        info_y = content_rect.y + 120
        
        merchant_id = merchant_data.get('merchant_id')
        merchant_config = game_state.item_manager.merchant_data.get('merchants', {}).get(merchant_id, {})
        
        # Greeting
        greeting = merchant_config.get('greeting', [])
        if greeting:
            draw_centered_text(surface, f"' {' '.join(greeting)}",
                              fonts['small'], info_y, WHITE)

        # Stock categories
        categories = merchant_config.get('stock_categories', [])
        if categories:
            draw_centered_text(surface, f"Specializes in: {', '.join(categories)}",
                              fonts['small'], info_y, DARK_GRAY)
        
        # Buy/sell rates
        sell_mult = merchant_config.get('sell_multiplier', 0.4)
        rate_y = info_y + 40
        draw_centered_text(surface, f"Buys items at {int(sell_mult * 100)}% of value",
                          fonts['small'], rate_y, DARK_GRAY)
        
        # Location info (future enhancement)
        location_y = rate_y + 40
        draw_centered_text(surface, "More merchant lore coming soon!",
                          fonts['small'], location_y, DARKEST_GRAY)  
        
    
    def handle_keyboard_input(self, key: int) -> bool:
        """Handle keyboard input - ESC closes the overlay"""
        if key == pygame.K_ESCAPE:
            self._handle_close()
            return True
        return super().handle_keyboard_input(key)

    def on_tab_changed(self, old_index: int, new_index: int):
        """Clear hovered item when switching tabs"""
        self.hovered_item_id = None
        print(f"🛒 Tab changed: Cleared hover state")
    
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks on the shopping overlay"""
        print(f"🛒 DEBUG: ShoppingOverlay.handle_mouse_click called with {mouse_pos}")
        
        # Let parent handle tab clicks first
        if super().handle_mouse_click(mouse_pos):
            print("✅ DEBUG: Tab click handled by parent")
            return True
        
        # Handle button clicks in BUY tab
        if self.active_tab_index == 0:  # BUY tab
            print("🛒 DEBUG: In BUY tab, checking buttons")
            for button_name, button_rect in self.button_rects.items():
                if button_rect and button_rect.collidepoint(mouse_pos):
                    print(f"🎯 DEBUG: Button {button_name} clicked!")
                    if button_name == 'buy':
                        if hasattr(self, 'screen_manager') and self.screen_manager:
                            self.screen_manager.event_manager.emit("COMMERCE_PURCHASE", {})
                    elif button_name == 'reset':
                        if hasattr(self, 'screen_manager') and self.screen_manager:
                            self.screen_manager.event_manager.emit("COMMERCE_RESET_CART", {})
                    elif button_name == 'close':
                        self._handle_close()
                    return True
            
            # Handle item clicks
            for item_rect, item_index in self.merchant_item_rects:
                if item_rect.collidepoint(mouse_pos):
                    print(f"🎯 DEBUG: Item {item_index} clicked!")
                    self._handle_item_click(item_index)
                    return True
                
        # Handle SELL tab clicks (COMBINED - remove the duplicate!)
        elif self.active_tab_index == 1:  # SELL tab
            print("🛒 DEBUG: In SELL tab")
            
            # FIRST: Check buttons
            print("🛒 DEBUG: Checking buttons")
            for button_name, button_rect in self.button_rects.items():
                if button_rect and button_rect.collidepoint(mouse_pos):
                    print(f"🎯 DEBUG: SELL Button {button_name} clicked!")
                    if button_name == 'sell':
                        self._process_sell_cart()
                        return True
                    elif button_name == 'clear':
                        self.sell_cart.clear()
                        print("🛒 Sell cart cleared")
                        return True
                    elif button_name == 'close':
                        self._handle_close()
                        return True
            
            # SECOND: Check item clicks
            print("🛒 DEBUG: In SELL tab, checking sell items")
            print(f"🛒 DEBUG: Checking {len(self.sell_item_rects)} sell item rects")
            for item_rect, item_index in self.sell_item_rects:
                if item_rect.collidepoint(mouse_pos):
                    print(f"🎯 DEBUG: Sell item {item_index} clicked!")
                    self._handle_sell_item_click(item_index)
                    return True
        
        print("❌ DEBUG: No click handled")
        return False

    def _handle_item_click(self, item_index):
        """Handle clicking on an item"""
        if hasattr(self, 'screen_manager') and self.screen_manager:
            game_state = self.screen_manager._current_game_controller.game_state
            merchant_data = getattr(game_state, 'current_merchant_data', None)
            
            if merchant_data:
                items = merchant_data.get('items', [])
                if 0 <= item_index < len(items):
                    clicked_item = items[item_index]
                    item_id = clicked_item.get('item_id')
                    merchant_id = merchant_data.get('merchant_id')
                    
                    # Add to cart via commerce engine
                    from game_logic.commerce_engine import get_commerce_engine
                    commerce = get_commerce_engine()
                    
                    # Check stock first
                    stock_status = commerce.get_stock_status(item_id, merchant_id)
                    if stock_status['remaining'] <= 0:
                        print(f"⚠️ {clicked_item.get('name', item_id)} is out of stock!")
                        return
                    
                    commerce.add_to_cart(item_id, merchant_id)
                    print(f"🛒 Added {clicked_item.get('name')} to cart")

    def _handle_sell_item_click(self, item_index):
        """Handle clicking on an item to add to sell cart"""
        print(f"🔍 DEBUG: Current sell_cart contents: {self.sell_cart}") 
        game_state = self.screen_manager._current_game_controller.game_state
        merchant_data = getattr(game_state, 'current_merchant_data', None)
        
        if merchant_data:
            merchant_id = merchant_data.get('merchant_id')
            merchant_config = game_state.item_manager.merchant_data.get('merchants', {}).get(merchant_id, {})
            sell_multiplier = merchant_config.get('sell_multiplier', 0.4)
            buy_categories = merchant_config.get('buy_categories', merchant_config.get('stock_categories', []))
            
            sellable_items = self._get_sellable_items(game_state, merchant_id, buy_categories, sell_multiplier)
            
            if 0 <= item_index < len(sellable_items):
                item_data = sellable_items[item_index]
                item_id = item_data['item_id']      # ← USE ITEM_ID
                item_name = item_data['name']        # ← Keep for display
                
                # Add to sell cart (max = owned quantity)
                max_qty = item_data['quantity']
                current_in_cart = self.sell_cart.get(item_id, 0)  # ← Use item_id as key
                
                if current_in_cart < max_qty:
                    self.sell_cart[item_id] = current_in_cart + 1  # ← Store by item_id
                    print(f"🛒 Added {item_name} (ID: {item_id}) to sell cart ({self.sell_cart[item_id]}/{max_qty})")
                else:
                    print(f"⚠️ Already have all {item_name} in sell cart")

    def _get_sellable_items(self, game_state, merchant_id, buy_categories, sell_multiplier):
        """Get items from player inventory that this merchant will buy"""     
        sellable = []
        
        # Get all player inventory items
        
        all_items = []
        for category in ['weapons', 'armor', 'items', 'consumables']:
            items_in_category = game_state.inventory.get(category, [])
            all_items.extend(items_in_category)
        #print(f"DEBUG: Total items found: {all_items}")
        
        # Count quantities
        item_counts = Counter(all_items)
        
        # Check each unique item
        for item_name, qty in item_counts.items():
            
            # If sell cart stores display names, convert to ID first
            # OR ensure sell cart stores IDs consistently
            item_def = game_state.item_manager.get_item_by_id(item_name)
            if not item_def:
                # Fallback: try treating it as a name (temporary)
                continue
            item_category = item_def.get('category', 'items')
            # RESTRICTION: Check if merchant buys this category
            if item_category not in buy_categories:
                continue  # Skip items this merchant won't buy
            # RESTRICTION: Skip quest items
            if item_def.get('quest_item', False):
                continue
            # RESTRICTION: Skip excluded subcategories (e.g., trinkets)
            merchant_config = game_state.item_manager.merchant_data.get('merchants', {}).get(merchant_id, {})
            excluded_buy_subcats = set(merchant_config.get('exclude_buy_subcategories', []))
            item_subcat = item_def.get('subcategory', '')
            if item_subcat and item_subcat in excluded_buy_subcats:
                continue
            # RESTRICTION: Block special and only_one rarity items from being sold
            item_rarity = item_def.get('rarity', 'common')
            if get_rarity_level(item_rarity) >= 999:  # Special or only_one
                print(f"🚫 Cannot sell special item: {item_def.get('name')} (rarity: {item_rarity})")
                continue

            base_cost = item_def.get('base_cost', item_def.get('cost', 1))
            sell_price = max(1, int(base_cost * sell_multiplier))
            
            sellable.append({
                'name': item_def.get('name', item_name),
                'item_id': item_def.get('id', item_name.lower().replace(' ', '_')),
                'base_cost': base_cost,
                'sell_price': sell_price,
                'quantity': qty,
                'category': item_category
            })
        
        return sellable

    def _process_sell_cart(self):
        """Process the sell cart - actually sell the items"""
        if not self.sell_cart:
            return
        
        game_state = self.screen_manager._current_game_controller.game_state
        merchant_data = getattr(game_state, 'current_merchant_data', None)
        if not merchant_data:
            return
        merchant_id = merchant_data.get('merchant_id')
        merchant_config = game_state.item_manager.merchant_data.get('merchants', {}).get(merchant_id, {})
        sell_multiplier = merchant_config.get('sell_multiplier', 0.4)
        buy_categories = merchant_config.get('buy_categories', [])
        
        total_gold = 0
        items_sold = 0
        print(f"DEBUG: sell_cart contents: {self.sell_cart}")
        print(f"DEBUG: sell_cart items: {list(self.sell_cart.items())}")
        
        # Initialize merchant stock tracking if needed
        if not hasattr(game_state, 'merchant_stocks'):
            game_state.merchant_stocks = {}
        if merchant_id not in game_state.merchant_stocks:
            game_state.merchant_stocks[merchant_id] = {}
        
        # Initialize player-sold tracking if needed
        if not hasattr(game_state, 'merchant_player_sold'):
            game_state.merchant_player_sold = {}
        if merchant_id not in game_state.merchant_player_sold:
            game_state.merchant_player_sold[merchant_id] = {}
        
        # Process each item in sell cart
        for item_id, qty in self.sell_cart.items():
            # Get item definition for base cost
            print(f"DEBUG: Processing sell cart item: '{item_id}' qty: {qty}")
            item_def = game_state.item_manager.get_item_by_id(item_id)
            if not item_def:
                print(f"DEBUG: Could not find item by ID '{item_id}' in sell cart")
                continue
            
            base_cost = item_def.get('base_cost', item_def.get('cost', 1))
            item_category = item_def.get('category', 'items')
            
            # Calculate total value first, THEN convert to int
            total_item_value = base_cost * qty * sell_multiplier
            item_gold = max(1, int(total_item_value))  # Minimum 1 gold for any sale
            
            # Remove from inventory (use item's category directly)
            removed_count = 0
            inventory_items = game_state.inventory.get(item_category, [])
            
            for _ in range(qty):
                if item_id in inventory_items:
                    inventory_items.remove(item_id)
                    removed_count += 1
                    items_sold += 1
            
            print(f"✅ Removed {removed_count} x '{item_id}' from inventory")
            
            # NEW: Add sold items to merchant's stock
            current_merchant_stock = game_state.merchant_stocks[merchant_id].get(item_id, 0)
            game_state.merchant_stocks[merchant_id][item_id] = current_merchant_stock + qty
            
            # Track as player-sold item (for refresh logic)
            current_player_sold = game_state.merchant_player_sold[merchant_id].get(item_id, 0)
            game_state.merchant_player_sold[merchant_id][item_id] = current_player_sold + qty
            
            print(f"✅ Added {qty} x '{item_id}' to {merchant_id}'s inventory")
            print(f"   Merchant now has {game_state.merchant_stocks[merchant_id][item_id]} {item_id}")
            
            total_gold += item_gold
            print(f"💰 Sold {qty} {item_id} for {item_gold} gold (base: {base_cost}, multiplier: {sell_multiplier})")
        
        # Add gold to player
        game_state.character['gold'] += total_gold
        
        # Update statistics (safely check if keys exist)
        if hasattr(game_state, 'player_statistics'):
            stats = game_state.player_statistics
            stats['items_sold'] = stats.get('items_sold', 0) + items_sold
            stats['gold_earned_trading'] = stats.get('gold_earned_trading', 0) + total_gold
        
        # Clear sell cart
        self.sell_cart.clear()

        print(f"💰 Total: Sold {items_sold} items for {total_gold} gold")

        # Refresh merchant data so BUY tab shows newly sold items
        from game_logic.commerce_engine import get_commerce_engine
        commerce = get_commerce_engine()
        if commerce:
            updated_merchant_data = commerce.get_merchant_inventory(merchant_id)
            if updated_merchant_data:
                # Update the cached merchant data in game_state
                game_state.current_merchant_data = updated_merchant_data
                print(f"🔄 Refreshed merchant data after sell - {len(updated_merchant_data.get('items', []))} items now in stock")

    def _handle_close(self):
        """Handle closing the overlay"""
        if hasattr(self, 'screen_manager') and self.screen_manager:
            game_state = self.screen_manager._current_game_controller.game_state
            return_dialogue = getattr(game_state, 'shopping_return_dialogue', 'broken_blade_garrick')
            
            self.screen_manager.event_manager.emit("SCREEN_CHANGE", {
                'target_screen': return_dialogue,
                'source_screen': "merchant_shop"
            })

    def previous_page(self) -> bool:
        """Navigate to previous page based on active tab"""
        if self.active_tab_index == 0:  # BUY tab
            if self.buy_page > 0:
                self.buy_page -= 1
                return True
        elif self.active_tab_index == 1:  # SELL tab
            if self.sell_page > 0:
                self.sell_page -= 1
                return True
        # Add more tabs as needed
        return False

    def next_page(self) -> bool:
        """Navigate to next page based on active tab"""
        if self.active_tab_index == 0:  # BUY tab
            self.buy_page += 1
            return True
        elif self.active_tab_index == 1:  # SELL tab
            self.sell_page += 1
            return True
        # Add more tabs as needed
        return False

###  Keep for fallback, Need to be moved to utils/graphics.py ###
def draw_border(surface, x, y, width, height):
    """Draw a chunky retro border"""
    pygame.draw.rect(surface, WHITE, (x, y, width, height), 3)
    pygame.draw.rect(surface, DARK_GRAY, (x+3, y+3, width-6, height-6), 2)
###  Keep for fallback, Need to be moved to utils/graphics.py ###
def draw_button(surface, x, y, width, height, text, font, pressed=False, selected=False, enabled=True):
    """Draw a retro-style button"""
    if not enabled:
        color = DARKEST_GRAY
        border_color = DARKEST_GRAY
        text_color = (60, 60, 60)
    elif selected:
        color = SOFT_YELLOW
        border_color = WHITE
        text_color = BLACK
    else:
        color = DARKEST_GRAY if pressed else DARK_GRAY
        border_color = DARKEST_GRAY if pressed else WHITE
        text_color = DARK_BROWN
    
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    surface.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height) if enabled else None

# ==========================================
# COMPATIBILITY LAYER (ADD AT THE VERY END)
# ==========================================

# Global instance management
shopping_overlay_instance = None

def get_shopping_overlay():
    """Get the global shopping overlay instance"""
    global shopping_overlay_instance
    if shopping_overlay_instance is None:
        shopping_overlay_instance = ShoppingOverlay()
    return shopping_overlay_instance

def draw_shopping_overlay(surface, game_state, fonts, images=None):
    """
    REQUIRED: Compatibility function for ScreenManager
    MUST match this exact signature
    """
    overlay = get_shopping_overlay()
    
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

def handle_shopping_click(mouse_pos, result):
    """
    REQUIRED: Compatibility function for mouse handling
    MUST match this exact signature
    """
    overlay = get_shopping_overlay()
    return overlay.handle_mouse_click(mouse_pos)

def handle_shopping_keyboard_input(key, game_state):
    """
    REQUIRED: Compatibility function for keyboard handling
    MUST match this exact signature
    """
    if game_state.screen == "merchant_shop":
        overlay = get_shopping_overlay()
        return overlay.handle_keyboard_input(key)
    return False
