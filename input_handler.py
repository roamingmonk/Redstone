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
        
        # Overlay registry for self-registering overlays
        self.overlay_registry: Dict[str, Any] = {}  # state_flag -> overlay_instance

        # Universal hotkey mappings
        self.universal_hotkeys = {
            pygame.K_i: ("OVERLAY_TOGGLE", {"overlay_id": "inventory_key"}),
            pygame.K_q: ("OVERLAY_TOGGLE", {"overlay_id": "quest_key"}),
            pygame.K_c: ("OVERLAY_TOGGLE", {"overlay_id": "character_key"}),
            pygame.K_h: ("OVERLAY_TOGGLE", {"overlay_id": "help_key"}),
            pygame.K_p: ("OVERLAY_TOGGLE", {"overlay_id": "party_key"}),
            
            # Game controls (corrected)
            pygame.K_F1: ("DEBUG_TOGGLE", {}),
            pygame.K_F2: ("DEBUG_PERFORMANCE", {}),  # New debug key
            pygame.K_F3: ("DEBUG_SAVE_STATE", {}),   # New debug key
            pygame.K_F5: ("SAVE_REQUESTED", {"slot": "quick_save"}),
            pygame.K_F7: ("SAVE_GAME", {}),          # Fixed: Opens save overlay
            pygame.K_F10: ("LOAD_GAME", {}),         # Fixed: Opens load overlay
            
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

    def _handle_location_action_events(self, mouse_pos, current_screen):
        """Handle LOCATION_ACTION events from BaseLocation screens"""
        
        # Check clickable regions for LOCATION_ACTION events
        if current_screen in self.clickable_regions:
            regions = self.clickable_regions[current_screen]
            
            for region in regions:
                if region.rect.collidepoint(mouse_pos) and region.event_type == "LOCATION_ACTION":
                    if self.debug_input:
                        print(f"🎯 BaseLocation action clicked: {region.event_data}")
                    
                    # Emit the LOCATION_ACTION event
                    self.event_manager.emit("LOCATION_ACTION", region.event_data)
                    return True
        
        return False

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
        
        # ADD DEBUG LOGGING HERE:
        #print(f"🖱️ DEBUG: IH: Mouse click detected at {mouse_pos}")
        #print(f"🖱️ DEBUG: IH: Current screen: {current_screen}")
        
        # Record click for debugging
        self.click_history.append({
            'pos': mouse_pos,
            'screen': current_screen,
            'regions_checked': 0
        })
        
        # Keep history manageable
        if len(self.click_history) > self.max_click_history:
            self.click_history.pop(0)
        
        #if self.debug_input:
            #print(f"🖱️ IH:  Mouse click at {mouse_pos} on screen '{current_screen}'")
        
        if self._handle_location_action_events(mouse_pos, current_screen):
            return True

        # Check clickable regions for current screen
        if current_screen in self.clickable_regions:
            regions = self.clickable_regions[current_screen]
            regions_checked = 0
            
            #print(f"🖱️ DEBUG: IH: Found {len(regions)} clickable regions for {current_screen}")

            for region in regions:
                regions_checked += 1
                if region.rect.collidepoint(mouse_pos):
                    #if self.debug_input:
                        
                        #print(f"🎯 DEBUG: IH: HIT! Event: {region.event_type}, Data: {region.event_data}")

                    # Emit the event instead of calling methods directly
                    self.event_manager.emit(region.event_type, region.event_data)
                    #print(f"✅ DEBUG: IH: Event emitted successfully")

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
        
        # Handle dialogue state input
        if self._handle_dialogue_state_input(mouse_pos):
            return True
                
        # Universal overlay input handling 
        if self._handle_registered_overlay_input(mouse_pos):
            return True
        
        if self._handle_overlay_clicks(mouse_pos, current_screen):
            return True       
        
        if hasattr(self, 'screen_manager') and self.screen_manager:
            if self.debug_input:
                print(f"🔄 Delegating to ScreenManager for screen: {current_screen}")
            
            # Try ScreenManager's click handling
            if self.screen_manager.handle_screen_click(current_screen, mouse_pos, self.game_controller):
                return True
        
        # Handle special cases that advance on any click
        if current_screen in ["game_title", "developer_splash"]:
            if self.debug_input:
                print(f"⚡ Auto-advancing from {current_screen}")
            self.event_manager.emit("SCREEN_ADVANCE", {"current_screen": current_screen})
            return True

        # DEFAULT: Ignore empty space clicks (safe for all other screens)
        if self.debug_input:
            print(f"🚫 Ignoring empty space click on {current_screen}")
        return True

    #### Handle dialgoue states  ####
    def register_dialogue_state(self, dialogue_handler, state_flag: str) -> bool:
        """
        Register a dialogue state handler for automatic input routing
        
        Args:
            dialogue_handler: The dialogue handler object (must have handle_mouse_click method)
            state_flag: GameState attribute name (e.g., 'showing_meredith_response')
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Validate handler has required methods
            if not hasattr(dialogue_handler, 'handle_mouse_click'):
                print(f"⚠️ Dialogue state registration failed: {dialogue_handler} missing handle_mouse_click method")
                return False
            
            # Store in a separate registry (not overlay_registry)
            if not hasattr(self, 'dialogue_state_registry'):
                self.dialogue_state_registry = {}
                
            self.dialogue_state_registry[state_flag] = dialogue_handler
            
            if self.debug_input:
                print(f"✅ Dialogue state registered: {state_flag} -> {getattr(dialogue_handler, 'handler_id', 'unknown')}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Dialogue state registration error for {state_flag}: {e}")
            return False

    def unregister_dialogue_state(self, state_flag: str) -> bool:
        """Unregister a dialogue state from input routing"""
        if hasattr(self, 'dialogue_state_registry') and state_flag in self.dialogue_state_registry:
            del self.dialogue_state_registry[state_flag]
            if self.debug_input:
                print(f"🗑️ Dialogue state unregistered: {state_flag}")
            return True
        return False

    def _handle_dialogue_state_input(self, mouse_pos) -> bool:
        """Handle clicks for active dialogue states"""
        if not hasattr(self, 'dialogue_state_registry'):
            return False
            
        game_state = self.game_controller.game_state
        
        # Check each registered dialogue state
        for state_flag, dialogue_handler in self.dialogue_state_registry.items():
            if hasattr(game_state, state_flag) and getattr(game_state, state_flag):
                if self.debug_input:
                    print(f"🎭 Routing click to dialogue state: {state_flag}")
                
                # Route the click to the dialogue handler
                if dialogue_handler.handle_mouse_click(mouse_pos):
                    return True
                    
        return False

    ####    ####


    def _handle_registered_overlay_keyboard_input(self, key) -> bool:
        """Handle keyboard input for all registered overlays"""
        if not hasattr(self, 'game_controller') or not self.game_controller:
            return False
            
        game_state = self.game_controller.game_state
        
        # Check centralized overlay state
        if hasattr(game_state, 'overlay_state') and game_state.overlay_state.has_any_overlay_open():
            active_overlay_id = game_state.overlay_state.get_active_overlay()
            
            # Find the matching overlay instance in registry
            for state_flag, overlay_instance in self.overlay_registry.items():
                if overlay_instance.overlay_id == active_overlay_id:
                    try:
                        if self.debug_input:
                            print(f"⌨️ Routing keyboard to registered overlay: {active_overlay_id}")
                        
                        # Try keyboard input
                        if overlay_instance.handle_keyboard_input(key):
                            if self.debug_input:
                                print(f"✅ Overlay {active_overlay_id} handled keyboard input")
                            return True
                            
                    except Exception as e:
                        print(f"❌ Error in overlay {active_overlay_id} keyboard handling: {e}")
                        break
        
        return False

    def _handle_registered_overlay_input(self, mouse_pos) -> bool:
        """Handle input for all registered overlays"""
        if not hasattr(self, 'game_controller') or not self.game_controller:
            return False
            
        game_state = self.game_controller.game_state
        
        # Check centralized overlay state
        if hasattr(game_state, 'overlay_state') and game_state.overlay_state.has_any_overlay_open():
            active_overlay_id = game_state.overlay_state.get_active_overlay()
            
            # Find the matching overlay instance in registry
            for state_flag, overlay_instance in self.overlay_registry.items():
                if overlay_instance.overlay_id == active_overlay_id:
                    try:
                        if self.debug_input:
                            print(f"🎯 Routing input to registered overlay: {active_overlay_id}")
                        
                        # Try mouse click
                        if overlay_instance.handle_mouse_click(mouse_pos):
                            if self.debug_input:
                                print(f"✅ Overlay {active_overlay_id} handled mouse click")
                            return True
                            
                    except Exception as e:
                        print(f"❌ Error in overlay {active_overlay_id} input handling: {e}")
                        break
        
        return False

    def process_keyboard_input(self, event: pygame.event.Event, 
                              game_state) -> bool:
        #print(f"DEBUG: IH: Keyboard event - key: {pygame.key.name(event.key)}, screen: {game_state.screen}")
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
                print("📝 Text input mode active - processing text input events")
            
            # Handle text input through event system
            if event.key == pygame.K_RETURN:
                self.event_manager.emit("CONFIRM_CUSTOM_NAME", {})
            
                return True
                
            elif event.key == pygame.K_BACKSPACE:
                self.event_manager.emit("TEXT_BACKSPACE", {})
                return True
                
            elif event.unicode.isprintable() and len(getattr(game_state, 'custom_name_text', '')) < 30:
                self.event_manager.emit("TEXT_INPUT", {
                    "character": event.unicode
                })
                return True
            
            # Any other key in text mode is handled but ignored
            return True
        
       
        # PRIORITY 2: Handle universal hotkeys
        if event.type == pygame.KEYDOWN:
            key = event.key
            
            # Special screen-specific keys first
            if key == pygame.K_RETURN:
                if game_state.screen in ["game_title", "developer_splash"]:
                    self.event_manager.emit("SCREEN_ADVANCE", {"current_screen": game_state.screen})
                    return True
            # NEW: Handle BaseLocation keyboard navigation (generic)
            current_screen = game_state.screen

            # Detect BaseLocation screens by common patterns
            is_location_screen = (
                current_screen == 'patron_selection' or
                current_screen.endswith('_main') or
                current_screen.endswith('_selection') or
                current_screen.endswith('_hub')
            )

            # Skip dialogue screens (they have their own keyboard handling)
            is_dialogue_screen = (
                current_screen.endswith('_dialogue') or 
                '_dialogue' in current_screen
            )

            if is_location_screen and not is_dialogue_screen:
                if key in (pygame.K_b, pygame.K_BACKSPACE, pygame.K_ESCAPE):
                    print(f"⌨️ Location screen BACK pressed from {current_screen}")
                    
                    # Parse screen to determine location and area
                    if current_screen == 'patron_selection':
                        location_id = 'patron_selection'
                        area_id = 'main_area'
                    elif '_' in current_screen:
                        screen_parts = current_screen.split('_')
                        location_id = '_'.join(screen_parts[:-1])  # Everything except last part
                        area_id = screen_parts[-1]  # Last part (like "main")
                    else:
                        location_id = current_screen
                        area_id = 'main_area'
                    
                    self.event_manager.emit("LOCATION_ACTION", {
                        'action': 'back',
                        'location_id': location_id,
                        'area_id': area_id,
                        'action_data': {'action_name': 'back'}
                    })
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

        # PRIORITY 3: Handle dialogue keyboard input
        if self._handle_dialogue_keyboard_input(event.key, game_state):
            return True

        #Prioirty 4: Route keyboard input to registered overlays
        if self._handle_registered_overlay_keyboard_input(event.key):
            return True

        return True  # Continue running
    
    def _handle_escape_key(self, game_state) -> bool:
        """
        Handle ESC key - close overlays using centralized overlay state
        
        Returns:
            bool: True if an overlay was closed, False if no overlays open
        """
        # Check if any overlay is open using the centralized system
        if hasattr(game_state, 'overlay_state') and game_state.overlay_state.has_any_overlay_open():
            # Get the active overlay for debug purposes
            active_overlay_id = game_state.overlay_state.get_active_overlay()
            
            # Close the active overlay (no parameters needed)
            game_state.overlay_state.close_overlay()
            
            if self.debug_input:
                print(f"🔙 ESC closed overlay: {active_overlay_id}")
            return True
        
        # Fallback: Check old-style boolean flags for legacy overlays
        legacy_overlay_attrs = [
            'character_advancement_open',
            'save_screen_open', 
            'load_screen_open'
        ]
        
        for attr in legacy_overlay_attrs:
            if hasattr(game_state, attr) and getattr(game_state, attr):
                setattr(game_state, attr, False)
                if self.debug_input:
                    print(f"🔙 ESC closed legacy overlay: {attr}")
                return True
        
        # No overlays were open
        return False

    def _handle_overlay_clicks(self, mouse_pos, current_screen):
        """Handle clicks on active overlays"""
        game_state = self.game_controller.game_state
        
      # Load screen overlay - use registered clickables with correct attributes
        if getattr(game_state, 'load_screen_open', False):
            clickables = self.clickable_regions.get('load_overlay', [])
            
            for clickable in clickables:
                if clickable.rect.collidepoint(mouse_pos):
                    print(f"🎯 Load overlay clickable hit: {clickable.event_type}")
                    self.event_manager.emit(clickable.event_type, clickable.event_data)
                    return True
            
            # If no clickable hit, still consume the click to prevent fall-through
            return True
    
        # Save screen overlay - use registered clickables  
        if getattr(game_state, 'save_screen_open', False):
            clickables = self.clickable_regions.get('save_overlay', [])
            
            for clickable in clickables:
                if clickable.rect.collidepoint(mouse_pos):
                    print(f"💾 Save overlay clickable hit: {clickable.event_type}")
                    self.event_manager.emit(clickable.event_type, clickable.event_data)
                    return True
            
            # If no clickable hit, still consume the click to prevent fall-through
            return True
                
        return False

    def register_overlay(self, overlay_instance, state_flag: str) -> bool:
        """
        Register an overlay for automatic input routing
        
        Args:
            overlay_instance: The overlay object (must have handle_mouse_click method)
            state_flag: GameState attribute name (e.g., 'quest_log_open')
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            # Validate overlay has required methods
            if not hasattr(overlay_instance, 'handle_mouse_click'):
                print(f"⚠️ Overlay registration failed: {overlay_instance} missing handle_mouse_click method")
                return False
                
            if not hasattr(overlay_instance, 'handle_keyboard_input'):
                print(f"⚠️ Overlay registration failed: {overlay_instance} missing handle_keyboard_input method")
                return False
            
            # Register the overlay
            self.overlay_registry[state_flag] = overlay_instance
            
            if self.debug_input:
                print(f"✅ Overlay registered: {state_flag} -> {overlay_instance.overlay_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Overlay registration error for {state_flag}: {e}")
            return False

    def unregister_overlay(self, state_flag: str) -> bool:
        """Unregister an overlay from input routing"""
        if state_flag in self.overlay_registry:
            del self.overlay_registry[state_flag]
            if self.debug_input:
                print(f"🗑️ Overlay unregistered: {state_flag}")
            return True
        return False

    def get_registered_overlays(self) -> Dict[str, str]:
        """Get debug info about registered overlays"""
        return {state_flag: getattr(overlay, 'overlay_id', 'unknown') 
                for state_flag, overlay in self.overlay_registry.items()}

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

    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Main event handler - routes events to appropriate processing methods
        
        Args:
            event: pygame event to process
            
        Returns:
            bool: True if event was handled, False if game should quit
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse clicks
            mouse_pos = pygame.mouse.get_pos()
            # Get current screen from game_controller reference (set by GameController)
            current_screen = getattr(self, 'current_screen', 'unknown')
            if hasattr(self, 'game_controller') and self.game_controller:
                current_screen = getattr(self.game_controller.game_state, 'screen', current_screen)
            return self.process_mouse_click(mouse_pos, current_screen)
            
        elif event.type == pygame.KEYDOWN:
            # Handle keyboard input
            game_state = None
            if hasattr(self, 'game_controller') and self.game_controller:
                game_state = self.game_controller.game_state
            return self.process_keyboard_input(event, game_state)
        
        # Other event types are ignored but considered "handled"
        return True

    def _handle_dialogue_keyboard_input(self, key, game_state) -> bool:
            """Handle keyboard input for dialogue screens"""
            # Detect dialogue-capable screens (legacy "*_dialogue" and new "<location>_<npc>")
            current_screen = game_state.screen

            is_dialogue_screen = (current_screen.endswith('_dialogue') or ('_dialogue' in current_screen))

            # Try to infer NPC for "<location>_<npc>" screens (e.g., "broken_blade_meredith")
            candidate_npc = None
            if '_' in current_screen:
                parts = current_screen.split('_')
                if len(parts) >= 2:
                    candidate_npc = parts[-1]  # "meredith" in "broken_blade_meredith"
                    # Treat as dialogue if game_state carries typical dialogue flags for this NPC
                    if (hasattr(game_state, f'{candidate_npc}_dialogue_in_progress') or
                        hasattr(game_state, f'showing_{candidate_npc}_response') or
                        hasattr(game_state, f'{candidate_npc}_current_location')):
                        is_dialogue_screen = True

            if not is_dialogue_screen:
                return False

            print(f"DEBUG: Dialogue keyboard check - screen: {current_screen}, key: {pygame.key.name(key)}")
            if self.debug_input:
                print(f"⌨️ Dialogue screen detected: {current_screen}")

            # Resolve NPC id (prefer the parsed candidate)
            npc_id = candidate_npc
            if not npc_id:
                return False

                
            showing_response_attr = f'showing_{npc_id}_response'
            is_showing_response = getattr(game_state, showing_response_attr, False)
            
            if is_showing_response:
                # RESPONSE MODE - primary/back/shop via keyboard
                if key in (pygame.K_RETURN, pygame.K_a):
                    if self.debug_input:
                        print(f"⌨️ Response primary pressed for {npc_id} → continue")
                    self.event_manager.emit("DIALOGUE_ACTION", {
                        'npc_id': npc_id,
                        'action_name': 'continue'  # ← Changed from 'goodbye' to 'continue'
                    })
                    return True

                elif key in (pygame.K_b, pygame.K_BACKSPACE):
                    if self.debug_input:
                        print(f"⌨️ Response back pressed for {npc_id} → back")
                    self.event_manager.emit("DIALOGUE_ACTION", {
                        'npc_id': npc_id,
                        'action_name': 'back'
                    })
                    return True

                elif key == pygame.K_s:
                    if self.debug_input:
                        print(f"⌨️ Response shop pressed for {npc_id} → shop")
                    self.event_manager.emit("DIALOGUE_ACTION", {
                        'npc_id': npc_id,
                        'action_name': 'shop'
                    })
                    return True

            else:
                # CHOICE MODE - 1, 2, 3 keys for choices (plus ENTER = first/primary)
                # NEW: Backspace/B exits from the main choice list
                if key in (pygame.K_BACKSPACE, pygame.K_b):
                    if self.debug_input:
                        print(f"⌨️ Choice BACK pressed for {npc_id} -> exit (goodbye)")
                    self.event_manager.emit("DIALOGUE_ACTION", {
                        'npc_id': npc_id,
                        'action_name': 'goodbye'
                    })
                    return True

                choice_keys = {
                    pygame.K_1: 0,
                    pygame.K_2: 1, 
                    pygame.K_3: 2
                }

                # ENTER picks the first option (primary)
                if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if self.debug_input:
                        print(f"⌨️ Choice ENTER pressed for {npc_id} -> option 1")
                    self.event_manager.emit("DIALOGUE_CHOICE", {
                        'npc_id': npc_id,
                        'choice_index': 0
                    })
                    return True
                                        
                if key in choice_keys:
                    choice_index = choice_keys[key]
                    if self.debug_input:
                        print(f"⌨️ Choice {choice_index + 1} pressed for {npc_id}")
                    self.event_manager.emit("DIALOGUE_CHOICE", {
                        'npc_id': npc_id,
                        'choice_index': choice_index
                    })
                    return True

def register_stats_screen_actions(self):
    """Register clickable regions for the stats screen"""
    
    clickable_regions = [
        {
            'action': 'REROLL_STATS',
            'coords': (350, 350, 160, 50),  # Based on your ROLL STATS button
            'description': 'Reroll character statistics'
        }
        # We'll add ACCEPT_STATS once we see what happens after rolling
    ]
    
    self.register_screen_clickables('stats', clickable_regions)
    print("📊 Stats screen clickable regions registered")
# ==========================================
# HELPER FUNCTIONS FOR SCREEN REGISTRATION
# ==========================================

def register_stats_screen_actions(self):
    """Register clickable regions for the stats screen"""
    
    clickable_regions = [
        {
            'action': 'REROLL_STATS',
            'coords': (350, 320, 160, 50),  # ROLL STATS button coordinates
            'description': 'Reroll character statistics'
        },
        {
            'action': 'KEEP_STATS',
            'coords': (550, 320, 160, 50),  # KEEP STATS button coordinates  
            'description': 'Accept current stats and continue to gender selection'
        }
    ]
    
    self.register_screen_clickables('stats', clickable_regions)
    print("📊 Stats screen clickable regions registered")

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