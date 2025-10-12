# ui/base_tabbed_overlay.py
"""
Terror in Redstone - Base Tabbed Overlay System
Professional foundation for all tabbed overlays (inventory, quest log, character sheet, help)

DESIGN PHILOSOPHY:
- Single base class handles all tab management
- Subclasses only implement content rendering
- Keyboard + mouse navigation built-in
- Consistent appearance across all overlays
- Professional lifecycle management
"""

import pygame
from typing import List, Dict, Any, Optional, Tuple
from utils.overlay_utils import *
from utils.constants import SPACING, DARK_GRAY
from utils.graphics import draw_centered_text

# ========================================
# STANDARD OVERLAY BUTTON ACTIONS
# ========================================

OVERLAY_BUTTON_ACTIONS = {
    'inventory': {
        'equip': 'INVENTORY_EQUIP_ITEM',
        'unequip': 'INVENTORY_UNEQUIP_ITEM', 
        'consume': 'INVENTORY_CONSUME_ITEM',
        'discard': 'INVENTORY_DISCARD_ITEM'
    }
    # Future overlays add their patterns here
}

class TabDefinition:
    """Defines a single tab in a tabbed overlay"""
    def __init__(self, tab_id: str, display_name: str, hotkey: Optional[int] = None):
        self.tab_id = tab_id
        self.display_name = display_name
        self.hotkey = hotkey  # pygame key constant (e.g., pygame.K_1)

class BaseTabbedOverlay:
    """
    Professional base class for all tabbed overlays
    
    RESPONSIBILITIES:
    - Tab bar rendering and navigation
    - Keyboard shortcuts (1-9 keys, left/right arrows)
    - Mouse click handling for tabs
    - Standard header/footer layout
    - Content area management
    - Overlay lifecycle (open/close)
    
    SUBCLASS RESPONSIBILITIES:
    - Define tabs in constructor
    - Implement render_tab_content() method
    - Handle tab-specific actions
    """
    
    def __init__(self, overlay_id: str, title: str, screen_manager=None):
        self.overlay_id = overlay_id
        self.title = title
        self.screen_manager = screen_manager
        
        # Tab management
        self.tabs: List[TabDefinition] = []
        self.active_tab_index = 0
        
        # Self-register with input system if available
        self._register_with_input_handler()

        # Layout constants
        self.popup_width = 1024
        self.popup_height = 600
        self.header_height = 60
        self.tab_bar_height = 40
        self.footer_height = 50
        self.margin = 20
        
        # Tab bar layout
        self.tab_button_height = 35
        self.tab_button_spacing = 5
        
        # Content area dimensions (calculated)
        self.content_y = self.header_height + self.tab_bar_height
        self.content_height = self.popup_height - self.content_y - self.footer_height
        self.content_rect = None  # Set during rendering
        
        # State tracking
        self.is_open = False
        self.clickable_tabs = []  # List of (rect, tab_index) for mouse handling
        
    def add_tab(self, tab_id: str, display_name: str, hotkey: Optional[int] = None):
        """Add a tab to this overlay"""
        tab = TabDefinition(tab_id, display_name, hotkey)
        self.tabs.append(tab)
        
    def get_active_tab(self) -> Optional[TabDefinition]:
        """Get the currently active tab"""
        if 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]
        return None
    
    def switch_to_tab(self, tab_index: int) -> bool:
        """Switch to tab by index, returns True if successful"""
        if 0 <= tab_index < len(self.tabs):
            old_index = self.active_tab_index
            self.active_tab_index = tab_index
            
            # Call hook for subclasses
            self.on_tab_changed(old_index, tab_index)
            return True
        return False
    
    def switch_to_tab_by_id(self, tab_id: str) -> bool:
        """Switch to tab by ID, returns True if successful"""
        for i, tab in enumerate(self.tabs):
            if tab.tab_id == tab_id:
                return self.switch_to_tab(i)
        return False
    
    def previous_page(self) -> bool:
        """Override in subclasses that support pagination"""
        return False

    def next_page(self) -> bool:
        """Override in subclasses that support pagination"""
        return False

    def handle_keyboard_input(self, key: int) -> bool:
        """
        Handle keyboard input for tab navigation
        
        Returns True if key was handled, False otherwise
        """
        # Number keys (1-9) for direct tab selection
        if pygame.K_1 <= key <= pygame.K_9:
            tab_index = key - pygame.K_1  # Convert to 0-based index
            return self.switch_to_tab(tab_index)
        
        # Arrow keys for tab navigation
        elif key == pygame.K_LEFT:
            # Previous tab (wrapping)
            new_index = (self.active_tab_index - 1) % len(self.tabs)
            return self.switch_to_tab(new_index)
            
        elif key == pygame.K_RIGHT:
            # Next tab (wrapping)
            new_index = (self.active_tab_index + 1) % len(self.tabs)
            return self.switch_to_tab(new_index)
        
            # Add page navigation
        elif key in (pygame.K_UP, key == pygame.K_p, pygame.K_PAGEUP):
            return self.previous_page()
            
        elif key in (pygame.K_DOWN, key == pygame.K_n, pygame.K_PAGEDOWN):
            return self.next_page()
    
        # Check for tab-specific hotkeys
        else:
            for i, tab in enumerate(self.tabs):
                if tab.hotkey == key:
                    return self.switch_to_tab(i)
        
        return False
    
    def handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """
        Handle mouse clicks on tab buttons
        
        Returns True if click was handled, False otherwise
        """
        for rect, tab_index in self.clickable_tabs:
            if rect.collidepoint(mouse_pos):
                return self.switch_to_tab(tab_index)
        return False
    
    def register_standard_buttons(self, button_rects, overlay_type):
        """Auto-register overlay buttons with InputHandler using standard events"""
        print(f"🔍 Registering buttons: {list(button_rects.keys())}")
        
        if (self.screen_manager and 
            hasattr(self.screen_manager, 'input_handler') and 
            overlay_type in OVERLAY_BUTTON_ACTIONS):
            
            actions = OVERLAY_BUTTON_ACTIONS[overlay_type]
            print(f"🔍 Available actions: {list(actions.keys())}")
            
            for button_name, button_rect in button_rects.items():
                if button_name in actions and button_rect:
                    event_type = actions[button_name]
                    print(f"🔘 Registering {button_name} -> {event_type}")
                    # Register with InputHandler as clickable
                    self.screen_manager.input_handler.register_clickable(
                        screen_name=f"{self.overlay_id}_buttons",
                        rect=button_rect,
                        event_type=event_type,
                        event_data={'button': button_name, 'overlay_type': overlay_type}
                    )
        
    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict) -> List[Tuple[pygame.Rect, int]]:
        """
        Render the complete tabbed overlay
        
        Returns list of clickable tab rectangles for mouse handling
        """
        
        # Get ItemManager if we don't have one
        if not hasattr(self, 'item_manager') or self.item_manager is None:
            if hasattr(self, 'screen_manager') and self.screen_manager:
                if hasattr(self.screen_manager, '_current_game_controller'):
                    controller = self.screen_manager._current_game_controller
                    if hasattr(controller, 'data_manager'):
                        self.item_manager = controller.data_manager.item_manager
                        print("🔧 InventoryOverlay: ItemManager accessed successfully")
        
        # Existing popup background pattern
        #draw_popup_background(surface)

        # Grey background like the original help screen
        overlay = pygame.Surface((1024, 768))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        surface.blit(overlay, (0, 0))


        # Calculate popup area (matching your inventory/quest log pattern)
        popup_x = 50
        popup_y = 120
        popup_width = 924  # 924(1024 - 100) (50px margin each side)
        popup_height = 550

        # Store popup rect for subclass use
        self.popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)
        
       # Draw main content border (matching your existing pattern)
        draw_chunky_border(surface, popup_x, popup_y, popup_width, popup_height)

        # Calculate content area - use constants for consistency

        content_x = popup_x + SPACING['margin']  # 20px margin
        content_y = popup_y + 60  # Space for title and tab area  
        content_width = popup_width - (2 * SPACING['margin'])  # 40px total margin
        content_height = popup_height - 95  # Space for title, tab, and footer

        self.content_rect = pygame.Rect(content_x, content_y, content_width, content_height)
        
        # Render components directly on main surface
        self._render_header(surface, fonts, popup_x, popup_y, popup_width)
        clickable_tabs = self._render_tab_bar(surface, fonts, popup_x, popup_y, popup_width)
        self._render_content_area(surface, game_state, fonts, images)
        self._render_footer(surface, fonts, popup_x, popup_y + popup_height, popup_width)

        # Convert clickable rects to screen coordinates (already correct since we draw on main surface)
        self.clickable_tabs = clickable_tabs
        return clickable_tabs
    
    def _render_header(self, surface: pygame.Surface, fonts: Dict, popup_x: int, popup_y: int, popup_width: int):
        """Render the overlay title header"""
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
        draw_centered_text(surface, self.title, title_font, popup_y + 30, BRIGHT_GREEN, popup_width + 100) #added 100 to make 1024 so centers header
    
    def _render_tab_bar(self, surface: pygame.Surface, fonts: Dict, popup_x: int, popup_y: int, popup_width: int) -> List[Tuple[pygame.Rect, int]]:
        """
        Render the tab buttons
        
        Returns list of (rect, tab_index) for click handling
        """
        if not self.tabs:
            return []
        
        clickable_rects = []
        tab_font = fonts.get('medium', fonts['normal'])

       # Tab positioning using popup coordinates
        tab_width = 200
        tab_spacing = 25
        tab_y = popup_y - 30  # Tabs above the main border
        tab_height = 35

        # Left-justify the tab over the content area
        from utils.constants import SPACING
        content_area_x = popup_x + SPACING['margin']
        tab_start_x = content_area_x  # Left-align instead of center

        # Render each tab using popup positioning
        for i, tab in enumerate(self.tabs):
            x = tab_start_x + i * (tab_width + tab_spacing)
            
            # Draw tab button using your existing function
            is_active = (i == self.active_tab_index)
            tab_rect = draw_tab_button(surface, x, tab_y, tab_width, tab_height, 
                                    tab.display_name, tab_font, active=is_active)
            
            # Store clickable area
            clickable_rects.append((tab_rect, i))
            
            # Add number indicator for keyboard shortcuts
            if i < 9:  # Only show numbers 1-9
                number_text = f"{i + 1}"
                number_surface = fonts.get('fantasy_small', fonts.get('small', fonts['normal'])).render(
                    number_text, True, DARK_GRAY)
                number_rect = number_surface.get_rect()
                number_rect.topright = (x + tab_width - 5, tab_y + 2)  # Use the correct variable names
                surface.blit(number_surface, number_rect)
        
        return clickable_rects
    
    def _render_content_area(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict):
        """
        Render the content area - delegates to subclass
        """
        # Draw content background
        pygame.draw.rect(surface, DARK_BROWN, self.content_rect)
        pygame.draw.rect(surface, WHITE, self.content_rect, 2)
        
        # Get active tab
        active_tab = self.get_active_tab()
        if active_tab:
            # Call subclass implementation
            self.render_tab_content(surface, active_tab, game_state, fonts, images)
        else:
            # No tabs or invalid state - show error message
            error_text = "No content available"
            error_font = fonts.get('medium', fonts['default'])
            draw_centered_text(surface, error_text, error_font, 
                             self.content_rect.centery, WHITE, self.popup_width)
    
    def _render_footer(self, surface: pygame.Surface, fonts: Dict, popup_x: int, popup_y: int, popup_width: int):
        """Render footer with instructions"""
        #footer_font = fonts.get('fantasy_small', fonts.get('small', fonts['normal']))
        footer_font = fonts.get('help_text', fonts['small'])
        
        # Build instruction text based on available tabs
        instructions = []
        if len(self.tabs) > 1:
            instructions.append("N/P: Page up/down")
            instructions.append("1-9: Select Tab")
            #instructions.append("← →: Navigate")  # arrows do not render
        instructions.append("ESC: Close")
        
        instruction_text = " | ".join(instructions)
        draw_centered_text(surface, instruction_text, footer_font, popup_y - 20, GRAY, popup_width + 100)

    def _register_with_input_handler(self):
        """Register this overlay with the InputHandler for automatic input routing"""
        try:
            if (self.screen_manager and 
                hasattr(self.screen_manager, 'input_handler') and 
                self.screen_manager.input_handler):
                
                # Generate state flag from overlay_id
                state_flag = f"{self.overlay_id}_open" if not self.overlay_id.endswith('_open') else self.overlay_id
                
                # Handle special cases for naming consistency
                if self.overlay_id == "quest":
                    state_flag = "quest_log_open"
                elif self.overlay_id == "character":
                    state_flag = "character_sheet_open"
                elif self.overlay_id == "help":
                    state_flag = "help_screen_open"
                
                success = self.screen_manager.input_handler.register_overlay(self, state_flag)
                if success:
                    print(f"✅ Self-registered overlay: {self.overlay_id} -> {state_flag}")
                else:
                    print(f"⚠️ Failed to self-register overlay: {self.overlay_id}")
                    
        except Exception as e:
            print(f"⚠️ Overlay self-registration error for {self.overlay_id}: {e}")
            print("   Overlay will function but input routing may not work")

    def _unregister_from_input_handler(self):
        """Unregister this overlay from InputHandler"""
        try:
            if (self.screen_manager and 
                hasattr(self.screen_manager, 'input_handler') and 
                self.screen_manager.input_handler):
                
                # Use same state flag logic as registration
                state_flag = f"{self.overlay_id}_open" if not self.overlay_id.endswith('_open') else self.overlay_id
                if self.overlay_id == "quest":
                    state_flag = "quest_log_open"
                elif self.overlay_id == "character":
                    state_flag = "character_sheet_open"
                elif self.overlay_id == "help":
                    state_flag = "help_screen_open"
                    
                self.screen_manager.input_handler.unregister_overlay(state_flag)
                
        except Exception as e:
            print(f"⚠️ Overlay unregistration error for {self.overlay_id}: {e}")

    # ========================================
    # SUBCLASS HOOKS
    # ========================================
    
    def render_tab_content(self, surface: pygame.Surface, active_tab: TabDefinition, 
                          game_state, fonts: Dict, images: Dict):
        """
        OVERRIDE THIS: Render content for the active tab
        
        Args:
            surface: The popup surface to draw on
            active_tab: The currently active tab definition
            game_state: Current game state
            fonts: Font dictionary
            images: Image dictionary
        """
        # Default implementation - subclasses should override
        placeholder_text = f"Content for {active_tab.display_name}"
        placeholder_font = fonts.get('fantasy_medium', fonts.get('medium', fonts['default']))
        draw_centered_text(surface, placeholder_text, placeholder_font,
                         self.content_rect.centery, WHITE, 1024)
    
    def on_tab_changed(self, old_index: int, new_index: int):
        """
        OVERRIDE THIS: Called when tab changes
        
        Args:
            old_index: Previous tab index
            new_index: New tab index
        """
        pass
    
    def on_overlay_opened(self, game_state):
        """
        OVERRIDE THIS: Called when overlay is opened
        
        Args:
            game_state: Current game state
        """
        self.is_open = True
    
    def on_overlay_closed(self, game_state):
        """
        OVERRIDE THIS: Called when overlay is closed
        
        Args:
            game_state: Current game state
        """
        self.is_open = False
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def get_content_area_rect(self) -> pygame.Rect:
        """Get the content area rectangle for subclass use"""
        return self.content_rect
    
    def get_tab_count(self) -> int:
        """Get the number of tabs"""
        return len(self.tabs)
    
    def get_tab_by_id(self, tab_id: str) -> Optional[TabDefinition]:
        """Get tab definition by ID"""
        for tab in self.tabs:
            if tab.tab_id == tab_id:
                return tab
        return None

# ========================================
# INTEGRATION HELPERS
# ========================================

def register_tabbed_overlay_with_screen_manager(screen_manager, overlay_instance, 
                                              state_flag: str, hotkey: int):
    """
    Helper function to register a tabbed overlay with the ScreenManager
    
    Args:
        screen_manager: The ScreenManager instance
        overlay_instance: The BaseTabbedOverlay subclass instance
        state_flag: GameState attribute name (e.g., 'inventory_open')
        hotkey: pygame key constant for opening overlay
    """
    
    def render_overlay(surface, game_state, fonts, images):
        """Render function for ScreenManager"""
        return overlay_instance.render(surface, game_state, fonts, images)
    
    def handle_overlay_input(key, game_state):
        """Input handler for the overlay"""
        if getattr(game_state, state_flag, False):
            return overlay_instance.handle_keyboard_input(key)
        return False
    
    def handle_overlay_click(mouse_pos, game_state):
        """Click handler for the overlay"""
        if getattr(game_state, state_flag, False):
            return overlay_instance.handle_mouse_click(mouse_pos)
        return False
    
    # Register with ScreenManager's overlay system
    overlay_config = {
        'state_flag': state_flag,
        'render_function': render_overlay,
        'input_handler': handle_overlay_input,
        'click_handler': handle_overlay_click,
        'hotkey': hotkey,
        'overlay_instance': overlay_instance
    }
    
    # This would integrate with your existing ScreenManager overlay registry
    # Exact integration depends on your current ScreenManager structure
    print(f"📋 Registered tabbed overlay: {overlay_instance.overlay_id}")
    return overlay_config