# input_handler.py
"""
InputHandler - Professional Input Management System
Replaces GameController's massive click/keyboard handling with clean event-driven system

This is the COMMAND CONTROL CENTER for all user input:
- Mouse clicks get routed to appropriate screen handlers
- Keyboard shortcuts emit events instead of direct method calls
- Clickable regions registered dynamically per screen
- Universal hotkeys work consistently across all screens

NO MORE 500+ line input handling functions!
"""

import pygame
from typing import Dict, List, Tuple, Callable, Optional, Any
from dataclasses import dataclass

@dataclass
class ClickableRegion:
    """Represents a clickable area on screen"""
    rect: pygame.Rect
    event_type: str
    event_data: Dict[str, Any]
    screen_name: str
    priority: int = 0  # Higher priority regions checked first

class InputHandler:
    """
    Professional input routing system for Terror in Redstone
    
    This replaces all the massive input handling code in GameController
    with a clean, event-driven system that's easy to debug and extend.
    """
    
    def __init__(self, event_manager):
        self.event_manager = event_manager
        
        # Clickable regions per screen
        self.clickable_regions: Dict[str, List[ClickableRegion]] = {}
        
        # Universal hotkey mappings
        self.universal_hotkeys = {
            pygame.K_i: ("OVERLAY_TOGGLE", {"overlay_id": "inventory"}),
            pygame.K_q: ("OVERLAY_TOGGLE", {"overlay_id": "quest_log"}),
            pygame.K_c: ("OVERLAY_TOGGLE", {"overlay_id": "character_sheet"}),
            pygame.K_h: ("OVERLAY_TOGGLE", {"overlay_id": "help"}),
            pygame.K_l: ("OVERLAY_TOGGLE", {"overlay_id": "load_game"}),
            pygame.K_F5: ("SAVE_REQUESTED", {"slot": "quick_save"}),
            pygame.K_F7: ("SCREENSHOT_REQUESTED", {}),
            pygame.K_F10: ("DEBUG_TOGGLE", {}),
            pygame.K_ESCAPE: ("ESCAPE_PRESSED", {})
        }
        
        # Text input mode tracking
        self.text_input_active = False
        self.text_input_callback = None
        
        #For the clickable region system
        self.current_interactables = []
        self.background_action = None

        # Debug features
        self.debug_input = False
        self.click_history = []
        self.max_click_history = 20
        
        print("🎮 InputHandler initialized - Professional input routing ready!")

    def set_interactables(self, screen_name: str, interactables_data):
        """
        NEW SEMANTIC APPROACH: Register clickable regions using semantic actions
        
        Args:
            screen_name: Name of the screen
            interactables_data: List of dicts with semantic actions or dict with regions + background
        
        Expected format:
        [
            {'action': 'ROLL_STATS', 'rect': (400, 180, 200, 40), 'payload': {'reroll_count': 3}},
            {'action': 'SELECT_NAME', 'rect': (300, 250, 180, 30), 'payload': {'name_index': 0}}
        ]
        """
        
        #print(f"🔍 IH: InputHandler EventManager ID: {id(self.event_manager)}")
        # Clear existing clickables for this screen
        self.clear_clickables(screen_name)
        
        # Handle both list and dict formats
        if isinstance(interactables_data, dict):
            regions = interactables_data.get('regions', [])
            background_action = interactables_data.get('background_action', None)
        else:
            regions = interactables_data or []
            background_action = None
        
        # Convert semantic actions to ClickableRegion objects
        for region_data in regions:
            action = region_data['action']
            rect_tuple = region_data['rect']  # (x, y, width, height)
            payload = region_data.get('payload', {})
            priority = region_data.get('priority', 0)
            
            # Convert tuple to pygame.Rect
            rect = pygame.Rect(rect_tuple[0], rect_tuple[1], rect_tuple[2], rect_tuple[3])
            
            # Register using your existing method
            self.register_clickable(screen_name, rect, action, payload, priority)
        
        # Handle background clicks if specified
        if background_action:
            # Create a full-screen background clickable (lowest priority)
            background_rect = pygame.Rect(0, 0, 1024, 768)
            self.register_clickable(screen_name, background_rect, background_action, {}, -100)
        
        #if self.debug_input:
        #    print(f"🎯 IH: Semantic registration complete for {screen_name}: {len(regions)} regions")

    def register_clickable(self, screen_name: str, rect: pygame.Rect, 
                          event_type: str, event_data: Dict[str, Any], 
                          priority: int = 0) -> None:
        """
        Register a clickable region for a specific screen
        
        Args:
            screen_name: Which screen this clickable belongs to
            rect: The clickable area (pygame.Rect)
            event_type: What event to emit when clicked
            event_data: Data to include with the event
            priority: Higher numbers get checked first (for overlapping regions)
        """
        if screen_name not in self.clickable_regions:
            self.clickable_regions[screen_name] = []
        
        clickable = ClickableRegion(rect, event_type, event_data, screen_name, priority)
        self.clickable_regions[screen_name].append(clickable)
        
        # Sort by priority (highest first)
        self.clickable_regions[screen_name].sort(key=lambda x: x.priority, reverse=True)
        
        #if self.debug_input:
        #    print(f"🎯 IH: Registered clickable: {screen_name} -> {event_type}")
    
    def clear_clickables(self, screen_name: str) -> None:
        """Clear all clickable regions for a screen"""
        if screen_name in self.clickable_regions:
            del self.clickable_regions[screen_name]
            #if self.debug_input:
                #print(f"🧹 Cleared clickables for screen: {screen_name}")
    
    def clear_all_clickables(self) -> None:
        """Clear all clickable regions (useful for cleanup)"""
        self.clickable_regions.clear()
        print("🧹 All clickable regions cleared")
    
    def process_mouse_click(self, mouse_pos: Tuple[int, int], 
                           current_screen: str) -> bool:
        """
        Process a mouse click and emit appropriate events
        
        Args:
            mouse_pos: (x, y) position of the click
            current_screen: Name of the currently active screen
            
        Returns:
            bool: True if click was handled, False otherwise
        """
        # Record click for debugging
        self.click_history.append({
            'pos': mouse_pos,
            'screen': current_screen,
            'regions_checked': 0
        })
        
        # Keep history manageable
        if len(self.click_history) > self.max_click_history:
            self.click_history.pop(0)
        
        if self.debug_input:
            print(f"🖱️  Mouse click at {mouse_pos} on screen '{current_screen}'")
        
        # Check clickable regions for current screen
        if current_screen in self.clickable_regions:
            regions = self.clickable_regions[current_screen]
            regions_checked = 0
            
            for region in regions:
                regions_checked += 1
                if region.rect.collidepoint(mouse_pos):
                    if self.debug_input:
                        print(f"✅ Click hit: {region.event_type} with data {region.event_data}")
                    
                    # Emit the event instead of calling methods directly
                    self.event_manager.emit(region.event_type, region.event_data)
                    
                    # Update debug info
                    self.click_history[-1]['regions_checked'] = regions_checked
                    self.click_history[-1]['hit'] = True
                    
                    return True
            
            # Update debug info for missed clicks
            self.click_history[-1]['regions_checked'] = regions_checked
            self.click_history[-1]['hit'] = False
            
            if self.debug_input:
                print(f"❌ Click missed all {regions_checked} regions on {current_screen}")
        
        else:
            if self.debug_input:
                print(f"⚠️  No clickable regions registered for screen: {current_screen}")
        if hasattr(self, 'screen_manager') and self.screen_manager:
            if self.debug_input:
                print(f"🔄 Delegating to ScreenManager for screen: {current_screen}")
            
            # Try ScreenManager's click handling
            if self.screen_manager.handle_screen_click(current_screen, mouse_pos, self.game_controller):
                return True
        
        # NEW: Add simple screen advance for basic title screen flow
        if current_screen in ["game_title", "developer_splash"]:
            if self.debug_input:
                print(f"⚡ Auto-advancing from {current_screen}")
            self.event_manager.emit("SCREEN_ADVANCE", {"current_screen": current_screen})
            return True
        
        # If all else fails, return False (was causing program exit)
        if self.debug_input:
            print(f"🚫 No handler found for click on {current_screen}")
        return False  # This should not cause program exit now
    
    def process_keyboard_input(self, event: pygame.event.Event, 
                              game_state) -> bool:
        """
        Process keyboard input and emit appropriate events
        
        Args:
            event: The pygame keyboard event
            game_state: Current game state (for checking text input mode)
            
        Returns:
            bool: True if input was handled, False if game should quit
        """
        # PRIORITY 1: Text input gets absolute priority
        if hasattr(game_state, 'custom_name_active') and game_state.custom_name_active:
            if self.debug_input:
                print("📝 Text input mode active - bypassing universal hotkeys")
            # Emit text input event instead of handling here
            self.event_manager.emit("TEXT_INPUT", {"event": event, "screen": game_state.screen})
            return True
        
        # PRIORITY 2: Handle universal hotkeys
        if event.type == pygame.KEYDOWN:
            key = event.key
            
            # Special screen-specific keys first
            if key == pygame.K_RETURN:
                if game_state.screen in ["game_title", "developer_splash"]:
                    self.event_manager.emit("SCREEN_ADVANCE", {"current_screen": game_state.screen})
                    return True
            
            # Universal hotkeys
            if key in self.universal_hotkeys:
                event_type, event_data = self.universal_hotkeys[key]
                
                if self.debug_input:
                    print(f"⌨️  Universal hotkey: {pygame.key.name(key)} -> {event_type}")
                
                # Special handling for ESC key
                if event_type == "ESCAPE_PRESSED":
                    # Check if any overlays are open first
                    overlay_closed = self._handle_escape_key(game_state)
                    if not overlay_closed:
                        # No overlays open - this means quit game
                        return False
                else:
                    # Emit the event
                    self.event_manager.emit(event_type, event_data)
                
                return True
        
        return True  # Continue running
    
    def _handle_escape_key(self, game_state) -> bool:
        """
        Handle ESC key - close overlays in priority order
        
        Returns:
            bool: True if an overlay was closed, False if no overlays open
        """
        # Priority order for closing overlays
        overlay_attrs = [
            'character_advancement_open',
            'save_screen_open', 
            'load_screen_open',
            'inventory_open',
            'quest_log_open', 
            'character_sheet_open',
            'help_screen_open'
        ]
        
        for attr in overlay_attrs:
            if hasattr(game_state, attr) and getattr(game_state, attr):
                setattr(game_state, attr, False)
                if self.debug_input:
                    print(f"🔙 ESC closed overlay: {attr}")
                return True
        
        # No overlays were open
        return False
    
    def set_text_input_mode(self, active: bool, callback: Optional[Callable] = None) -> None:
        """
        Enable/disable text input mode
        
        Args:
            active: Whether text input is currently active
            callback: Function to call when text input is processed
        """
        self.text_input_active = active
        self.text_input_callback = callback
        
        if self.debug_input:
            status = "enabled" if active else "disabled"
            print(f"📝 Text input mode {status}")
    
    def get_click_debug_info(self) -> List[Dict[str, Any]]:
        """Get recent click history for debugging"""
        return self.click_history
    
    def get_registered_screens(self) -> List[str]:
        """Get list of screens with registered clickables"""
        return list(self.clickable_regions.keys())
    
    def get_clickables_for_screen(self, screen_name: str) -> List[ClickableRegion]:
        """Get all clickable regions for a specific screen"""
        return self.clickable_regions.get(screen_name, [])
    
    def enable_debug_input(self, enabled: bool = True) -> None:
        """Enable or disable debug logging for input"""
        self.debug_input = enabled
        status = "enabled" if enabled else "disabled"
        print(f"🔍 Input debug logging {status}")



# ==========================================
# HELPER FUNCTIONS FOR SCREEN REGISTRATION
# ==========================================

def register_simple_click(input_handler, screen_name: str, rect: pygame.Rect, 
                         event_type: str, **event_data) -> None:
    """
    Convenience function for registering simple clickable regions
    
    Args:
        input_handler: The InputHandler instance
        screen_name: Screen this clickable belongs to
        rect: Clickable area
        event_type: Event to emit
        **event_data: Additional data to include with event
    """
    input_handler.register_clickable(screen_name, rect, event_type, event_data)

def register_screen_transition(input_handler, screen_name: str, rect: pygame.Rect, 
                              target_screen: str, priority: int = 0) -> None:
    """
    Convenience function for registering screen transition clicks
    
    Args:
        input_handler: The InputHandler instance
        screen_name: Current screen name
        rect: Clickable area
        target_screen: Screen to transition to
        priority: Click priority (higher = checked first)
    """
    input_handler.register_clickable(
        screen_name, rect, "SCREEN_CHANGE", 
        {"target_screen": target_screen, "source_screen": screen_name},
        priority
    )

def register_npc_click(input_handler, screen_name: str, rect: pygame.Rect, 
                      npc_id: str, location: str, priority: int = 0) -> None:
    """
    Convenience function for registering NPC clicks
    
    Args:
        input_handler: The InputHandler instance
        screen_name: Current screen name
        rect: Clickable NPC area
        npc_id: ID of the NPC
        location: Location where NPC was clicked
        priority: Click priority
    """
    input_handler.register_clickable(
        screen_name, rect, "NPC_CLICKED",
        {"npc_id": npc_id, "location": location},
        priority
    )


if __name__ == "__main__":
    print("🎮 InputHandler - Professional Input Routing System")
    print("This module handles ALL mouse and keyboard input for Terror in Redstone")
    print("Import and use with: from ui.input_handler import InputHandler")