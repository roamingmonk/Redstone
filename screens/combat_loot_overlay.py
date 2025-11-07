# screens/combat_loot_overlay.py
"""
Combat Loot Overlay - Post-combat loot selection screen
Built using BaseTabbedOverlay for proper integration
"""

import pygame
from utils.tabbed_overlay_utils import BaseTabbedOverlay
from utils.constants import (WHITE, GREEN, YELLOW, BLACK, GRAY, BLUE, RED, CORNFLOWER_BLUE,
                             DARK_GRAY, BUTTON_NORMAL_BG, BUTTON_NORMAL_BORDER,BUTTON_NORMAL_TEXT)
from utils.graphics import draw_text

class CombatLootOverlay(BaseTabbedOverlay):
    """
    Combat loot selection overlay
    Simple single-tab overlay for collecting loot after victory
    """
    
    def __init__(self, screen_manager=None):
        super().__init__("combat_loot", "VICTORY - COLLECT LOOT", screen_manager)
        
        # Single tab - loot collection
        self.add_tab("loot", "LOOT", hotkey=pygame.K_1)
        
        # Loot selection state
        self.selected_items = set()  # Set of item_ids to take
        self.hovered_item = None
        self.gold_collected = False
        
        print("💰 CombatLootOverlay initialized")
    
    def render_tab_content(self, surface, active_tab, game_state, fonts, images):
        """Render the loot selection content"""
        
        # Get loot data from game_state
        loot_data = getattr(game_state, 'combat_loot_data', {'total_gold': 0, 'items': []})
        total_gold = loot_data.get('total_gold', 0)
        items = loot_data.get('items', [])
        
        # Get content area
        content_rect = self.get_content_area_rect()
        content_x = content_rect.x + 20
        content_y = content_rect.y + 20
        
        # Gold section - Auto-collected
        gold_font = fonts.get('normal', fonts['normal'])
        
        # Auto-collect gold on first render
        if not self.gold_collected and total_gold > 0:
            self._collect_gold(game_state)
        
        gold_text = gold_font.render(f"Gold Collected: {total_gold}", True, GREEN)
        surface.blit(gold_text, (content_x, content_y))
        
        # Items section
        items_y = content_y + 60
        items_label = gold_font.render("Items Found:", True, WHITE)
        surface.blit(items_label, (content_x, items_y))
        
        # Item list with checkboxes
        item_y = items_y + 40
        self.item_rects = []
        
        if not items:
            no_items_font = fonts.get('small', fonts['normal'])
            no_items_text = no_items_font.render("No items found", True, GRAY)
            surface.blit(no_items_text, (content_x + 20, item_y))
        else:
            for item_data in items:
                item_id = item_data['item_id']
                item_name = item_data['name']
                quantity = item_data['quantity']
                
                # Item row background
                row_rect = pygame.Rect(content_x, item_y, content_rect.width - 40, 35)
                
                # Highlight if hovered
                if self.hovered_item == item_id:
                    pygame.draw.rect(surface, CORNFLOWER_BLUE, row_rect)
                
                # Checkbox
                checkbox_rect = pygame.Rect(content_x + 10, item_y + 8, 20, 20)
                pygame.draw.rect(surface, WHITE, checkbox_rect, 2)
                
                # Checkmark if selected
                if item_id in self.selected_items:
                    pygame.draw.line(surface, GREEN,
                                   (checkbox_rect.left + 3, checkbox_rect.centery),
                                   (checkbox_rect.centerx, checkbox_rect.bottom - 5), 3)
                    pygame.draw.line(surface, GREEN,
                                   (checkbox_rect.centerx, checkbox_rect.bottom - 5),
                                   (checkbox_rect.right - 3, checkbox_rect.top + 3), 3)
                
                # Item name with quantity
                display_text = f"{item_name} (x{quantity})" if quantity > 1 else item_name
                item_text = gold_font.render(display_text, True, WHITE)
                surface.blit(item_text, (content_x + 40, item_y + 8))
                
                # Store rect for click detection
                self.item_rects.append((row_rect, item_id, item_data))
                
                item_y += 40
        
        # Bottom buttons
        button_y = content_rect.bottom - 60
        button_font = fonts.get('small', fonts['normal'])
        
        # Take Selected
        self.take_button = pygame.Rect(content_x, button_y, 150, 40)
        pygame.draw.rect(surface, BUTTON_NORMAL_BG, self.take_button)
        pygame.draw.rect(surface, WHITE, self.take_button, 2)
        take_text = button_font.render("Take Selected", True, WHITE)
        surface.blit(take_text, take_text.get_rect(center=self.take_button.center))
        
        # Take All
        self.take_all_button = pygame.Rect(content_x + 170, button_y, 150, 40)
        pygame.draw.rect(surface, BUTTON_NORMAL_BG, self.take_all_button)
        pygame.draw.rect(surface, WHITE, self.take_all_button, 2)
        take_all_text = button_font.render("Take All", True, WHITE)
        surface.blit(take_all_text, take_all_text.get_rect(center=self.take_all_button.center))
        
        # Leave All
        self.leave_button = pygame.Rect(content_x + 340, button_y, 150, 40)
        pygame.draw.rect(surface, BUTTON_NORMAL_BG, self.leave_button)
        pygame.draw.rect(surface, WHITE, self.leave_button, 2)
        leave_text = button_font.render("Leave All", True, WHITE)
        surface.blit(leave_text, leave_text.get_rect(center=self.leave_button.center))
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks on loot overlay"""
        # Check parent class for tab clicks first
        if super().handle_mouse_click(mouse_pos):
            return True
        
        game_state = self.screen_manager._current_game_state if self.screen_manager else None
        if not game_state:
            return False
        
        # Item checkboxes
        if hasattr(self, 'item_rects'):
            for row_rect, item_id, item_data in self.item_rects:
                if row_rect.collidepoint(mouse_pos):
                    # Toggle selection
                    if item_id in self.selected_items:
                        self.selected_items.remove(item_id)
                    else:
                        self.selected_items.add(item_id)
                    return True
        
        # Bottom buttons
        if hasattr(self, 'take_button') and self.take_button.collidepoint(mouse_pos):
            self._take_selected_items(game_state)
            return True
        
        if hasattr(self, 'take_all_button') and self.take_all_button.collidepoint(mouse_pos):
            self._take_all_items(game_state)
            return True
        
        if hasattr(self, 'leave_button') and self.leave_button.collidepoint(mouse_pos):
            self._leave_all_items(game_state)
            return True
        
        return False
    
    def _collect_gold(self, game_state):
        """Collect gold"""
        loot_data = getattr(game_state, 'combat_loot_data', {})
        total_gold = loot_data.get('total_gold', 0)
        
        if total_gold > 0:
            game_state.character['gold'] += total_gold
            self.gold_collected = True
            
            if hasattr(game_state, 'player_statistics'):
                current = game_state.player_statistics.get('total_gold_earned', 0)
                game_state.player_statistics['total_gold_earned'] = current + total_gold
            
            print(f"💰 Collected {total_gold} gold!")
    
    def _take_selected_items(self, game_state):
        """Take selected items"""
        loot_data = getattr(game_state, 'combat_loot_data', {})
        items = loot_data.get('items', [])
        
        inventory_engine = None
        if hasattr(self, 'screen_manager') and self.screen_manager:
            if hasattr(self.screen_manager, '_current_game_controller'):
                game_controller = self.screen_manager._current_game_controller
                if game_controller and hasattr(game_controller, 'inventory_engine'):
                    inventory_engine = game_controller.inventory_engine
        
        for item_data in items:
            item_id = item_data['item_id']
            if item_id in self.selected_items:
                quantity = item_data['quantity']
                if inventory_engine:
                    inventory_engine.add_item(item_id, quantity)
                    print(f"📦 Added {quantity}x {item_data['name']}")
        
        self._close_loot_screen(game_state)
    
    def _take_all_items(self, game_state):
        """Take all items"""
        loot_data = getattr(game_state, 'combat_loot_data', {})
        items = loot_data.get('items', [])
        
        inventory_engine = None
        
        if hasattr(self, 'screen_manager') and self.screen_manager:
            if hasattr(self.screen_manager, '_current_game_controller'):
                game_controller = self.screen_manager._current_game_controller
                if game_controller and hasattr(game_controller, 'inventory_engine'):
                    inventory_engine = game_controller.inventory_engine
        
        for item_data in items:
            if inventory_engine:
                inventory_engine.add_item(item_data['item_id'], item_data['quantity'])
                print(f"📦 Added {item_data['quantity']}x {item_data['name']}")
            else:
                print(f"❌ No inventory_engine to add item!")
        
        self._close_loot_screen(game_state)
    
    def _leave_all_items(self, game_state):
        """Leave all items"""
        print("🚪 Left loot behind")
        self._close_loot_screen(game_state)
    
    def _close_loot_screen(self, game_state):
        """Close loot screen"""
        if hasattr(game_state, 'overlay_state'):
            game_state.overlay_state.close_overlay()
        
        # Set search loot flag if this was a search (not combat)
        if hasattr(game_state, 'search_loot_flag') and game_state.search_loot_flag:
            setattr(game_state, game_state.search_loot_flag, True)
            print(f"🚩 Set search flag: {game_state.search_loot_flag}")
            game_state.search_loot_flag = None
        
        # CRITICAL: Clean up combat state so next combat starts fresh
        if self.screen_manager and hasattr(self.screen_manager, '_current_game_controller'):
            game_controller = self.screen_manager._current_game_controller
            if game_controller and hasattr(game_controller, 'combat_engine'):
                game_controller.combat_engine.cleanup_combat()
                print("🧹 Combat state cleaned up after loot collection")

        # Clear game state combat flags
        if hasattr(game_state, 'current_combat_encounter'):
            game_state.current_combat_encounter = None
        if hasattr(game_state, 'combat_context'):
            game_state.combat_context = None

        game_state.combat_loot_data = None
        self.selected_items.clear()
        self.hovered_item = None
        self.gold_collected = False
        
        game_state.in_combat = False
        
        if hasattr(game_state, 'pre_combat_location'):
            return_location = game_state.pre_combat_location
            game_state.pre_combat_location = None
            
            # Use screen_manager's event manager, not game_state's
            if self.screen_manager and hasattr(self.screen_manager, 'event_manager'):
                self.screen_manager.event_manager.emit("SCREEN_CHANGE", {
                    'target_screen': return_location,
                    'source_screen': 'combat_loot'
                })
                print(f"🎯 Loot overlay navigating to: {return_location}")
            else:
                print("❌ No event manager available for navigation!")
        else:
            # Fallback if no pre_combat_location set
            if self.screen_manager and hasattr(self.screen_manager, 'event_manager'):
                self.screen_manager.event_manager.emit("SCREEN_CHANGE", {
                    'target_screen': 'broken_blade',
                    'source_screen': 'combat_loot'
                })


# ========================================
# COMPATIBILITY LAYER FOR SCREEN MANAGER
# ========================================

combat_loot_overlay_instance = None

def get_combat_loot_overlay():
    """Get the global combat loot overlay instance"""
    global combat_loot_overlay_instance
    if combat_loot_overlay_instance is None:
        combat_loot_overlay_instance = CombatLootOverlay()
    return combat_loot_overlay_instance

def draw_combat_loot_screen(surface, game_state, fonts, images=None):
    """
    REQUIRED: Compatibility function for ScreenManager
    """
    overlay = get_combat_loot_overlay()
    
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