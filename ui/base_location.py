# ui/base_location.py
"""
BaseLocation Architecture Foundation
Professional location system for Terror in Redstone

This module provides the core architecture for data-driven location management,
replacing hardcoded screen registrations with JSON configuration.
"""

import pygame
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from utils.constants import *
from utils.graphics import draw_border, draw_button, draw_centered_text
from utils.party_display import draw_party_status_panel, PARTY_PANEL_WIDTH
from utils.constants import wrap_text
from utils.constants import LOCATION_BACKGROUNDS_PATH, BUTTON_SIZES
from utils.graphics import draw_button
from utils.constants import calculate_button_layout, calculate_button_font



class BaseLocation(ABC):
    """
    Abstract base class for all game locations
    
    This class defines the interface that all location types must implement.
    It handles the common functionality like area navigation, action processing,
    and integration with the existing game systems.
    """
    
    def __init__(self, location_data: Dict[str, Any]):
        """
        Initialize a location from JSON configuration data
        
        Args:
            location_data: Dictionary loaded from location JSON file
        """
        self.location_id = location_data.get('location_id', 'unknown')
        self.name = location_data.get('name', 'Unknown Location')
        self.areas = location_data.get('areas', {})
        self.current_area = None
        
        # Validate required data
        if not self.areas:
            raise ValueError(f"Location {self.location_id} has no areas defined")
        
        # Set default area to first area if not specified
        if self.areas:
            self.current_area = list(self.areas.keys())[0]

    def register_with_input_handler(self, screen_manager, screen_name):
        """Register location buttons with InputHandler using LOCATION_ACTION events"""
        
        if not (screen_manager and hasattr(screen_manager, 'input_handler')):
            print(f"⚠️ Cannot register {screen_name}: InputHandler not available")
            return
            
        input_handler = screen_manager.input_handler
        
        # Get current button rects by rendering to temp surface  
        temp_surface = pygame.Surface((1024, 768))
        
        # Get game_state and proper resources for rendering
        game_state = getattr(screen_manager, '_current_game_state', None)
        controller = getattr(screen_manager, '_current_game_controller', None)
        
        # Create minimal fonts and images dictionaries
        dummy_fonts = {
            'normal': pygame.font.Font(None, 24),
            'fantasy_large': pygame.font.Font(None, 36),
            'fantasy_medium': pygame.font.Font(None, 28),
            'fantasy_small': pygame.font.Font(None, 20),
            'fantasy_tiny': pygame.font.Font(None, 16),
            # Add font key aliases that rendering code expects
            'header': pygame.font.Font(None, 36),  # Maps to fantasy_large
            'large': pygame.font.Font(None, 36),   # Maps to fantasy_large  
            'small': pygame.font.Font(None, 20),   # Maps to fantasy_small
            'tiny': pygame.font.Font(None, 16)     # Maps to fantasy_tiny
        }
        dummy_images = {}
        
        try:
            result = self.render(temp_surface, game_state, dummy_fonts, dummy_images, controller)
            button_rects = result.get('button_rects', {})
            
            if not button_rects:
                print(f"⚠️ No button rects found for {screen_name}")
                return
            
            # Get action data from JSON for each button
            area_data = self.get_current_area_data()
            actions = area_data.get('actions', {})


            
            # Register each button with LOCATION_ACTION event
            registered_count = 0
            for action_name, button_rect in button_rects.items():
                
                # Include full action data from JSON in the event
                action_data_from_json = actions.get(action_name, {})
                
                event_data = {
                    'action': action_name,
                    'location_id': self.location_id,
                    'area_id': self.current_area,
                    'action_data': action_data_from_json  # Complete JSON action definition
                }
                
                input_handler.register_clickable(
                    screen_name=screen_name,
                    rect=button_rect,
                    event_type="LOCATION_ACTION",
                    event_data=event_data
                )
                
                registered_count += 1
                print(f"  📋 Registered {action_name}: {action_data_from_json.get('type', 'special')} -> {action_data_from_json.get('target', 'N/A')}")
            
            print(f"🎯 BaseLocation registered {registered_count} buttons for {screen_name}")
            
        except Exception as e:
            print(f"❌ Error registering BaseLocation buttons for {screen_name}: {e}")
            import traceback
            traceback.print_exc()

    def get_current_area_data(self) -> Dict[str, Any]:
        """Get the data for the currently active area"""
        if self.current_area and self.current_area in self.areas:
            return self.areas[self.current_area]
        return {}
    
    def navigate_to_area(self, area_id: str) -> bool:
        """
        Navigate to a different area within this location
        
        Args:
            area_id: The ID of the area to navigate to
            
        Returns:
            True if navigation successful, False otherwise
        """
        if area_id in self.areas:
            self.current_area = area_id
            #print(f"🗺️ Navigated to area: {self.location_id}.{area_id}")
            return True
        else:
            print(f"⚠️ Area not found: {area_id} in location {self.location_id}")
            return False
    
    @abstractmethod
    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, 
               controller=None) -> Dict[str, Any]:
        """
        Render the current area of this location
        
        Args:
            surface: Pygame surface to draw on
            game_state: Current game state
            fonts: Available fonts dictionary
            images: Available images dictionary
            controller: Game controller reference
            
        Returns:
            Dictionary containing clickable areas and metadata
        """
        pass
    
    @abstractmethod
    def handle_action(self, action_data: Dict[str, Any], game_state, 
                     event_manager) -> Optional[str]:
        """
        Process an action triggered by user interaction
        
        Args:
            action_data: Dictionary containing action type and parameters
            game_state: Current game state
            event_manager: Event manager for triggering navigation
            
        Returns:
            Action result string or None
        """
        pass
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions for current area"""
        area_data = self.get_current_area_data()
        actions = area_data.get('actions', {})
        return list(actions.keys())


class ActionHubLocation(BaseLocation):
    """
    Location type for areas with multiple action buttons
    
    Examples: Broken Blade Main, General Store, Inn Lobby
    Provides a menu of activities: Talk, Shop, Gamble, Leave, etc.
    """
    
    def __init__(self, location_data: Dict[str, Any]):
        super().__init__(location_data)
        self.location_type = "action_hub"
    
    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, 
           controller=None) -> Dict[str, Any]:

        """Render action hub with standardized UI including party display"""
        surface.fill(BLACK)
        area_data = self.get_current_area_data()
        
        # === PARTY STATUS PANEL (RIGHT SIDE) ===

        draw_party_status_panel(surface, game_state, fonts)
        
        # === IMAGE ZONE (ADJUSTED FOR PARTY PANEL) ===
        image_y = LAYOUT_IMAGE_Y
        image_height = LAYOUT_IMAGE_HEIGHT
        
        # Adjust image width to accommodate party panel

        image_width = 1024 - PARTY_PANEL_WIDTH - 10  # 10px spacing
        
        draw_border(surface, 0, image_y, image_width, image_height)
        
        # Background image or fallback
        border_thickness = 6
        img_x = border_thickness
        img_y = image_y + border_thickness
        img_width = image_width - 2 * border_thickness
        img_height = image_height - 2 * border_thickness
        
        # Load background image using JSON filename + constants path
        bg_image_key = area_data.get('properties', {}).get('background_image')
        bg_loaded = False

        if bg_image_key:
            try:
                image_path = os.path.join(LOCATION_BACKGROUNDS_PATH, f"{bg_image_key}.jpg")
                
                if os.path.exists(image_path):
                    bg_image = pygame.image.load(image_path)
                    scaled_bg = pygame.transform.scale(bg_image, (img_width, img_height))
                    surface.blit(scaled_bg, (img_x, img_y))
                    bg_loaded = True
            except Exception as e:
                print(f"Warning: Could not load background image '{bg_image_key}': {e}")

        if not bg_loaded:
            # Fallback to colored background
            bg_color = area_data.get('properties', {}).get('background_color', [40, 20, 10])
            pygame.draw.rect(surface, bg_color, (img_x, img_y, img_width, img_height))
        
        # Title overlay on image
        title = area_data.get('title', self.name.upper())
        title_font = fonts.get('fantasy_large', fonts.get('large', fonts['normal']))
       # Only show title if no background image is present
        if not bg_loaded:  # Only show title when there's no background image
            draw_centered_text(surface, title, title_font, image_y + 240, YELLOW, screen_width=image_width)
        
        #=== DIALOG ZONE (FULL SCREEN WIDTH) ===
        dialog_y = LAYOUT_DIALOG_Y
        dialog_height = LAYOUT_DIALOG_HEIGHT
        dialog_margin = 0

        # Use full 1024 width for dialog box
        draw_border(surface, dialog_margin, dialog_y, 1024 - (dialog_margin * 2), dialog_height)
        
        # Description text using graphics.py text wrapping
        description = area_data.get('description', {})
        if isinstance(description, dict):
            subtitle = description.get('subtitle', 'Choose your path...')
            atmosphere = description.get('atmosphere', '')
        else:
            subtitle = str(description)
            atmosphere = ''
        
        text_y = LAYOUT_DIALOG_TEXT_Y
        desc_font = fonts.get('fantasy_medium', fonts['normal'])
        
        # Use graphics.py utilities for consistent text handling

        # Main subtitle - use full screen width
        draw_centered_text(surface, subtitle, desc_font, text_y, WHITE, screen_width=1024)

        # Atmosphere text with proper wrapping - use full screen width
        if atmosphere:
            atmo_font = fonts.get('fantasy_small', fonts['normal'])
            try:
                max_width = 1024 - 80  # Leave margins for full width
                wrapped_lines = wrap_text(atmosphere, atmo_font, max_width)
                
                current_y = text_y + 50
                for line_surface in wrapped_lines:
                    line_rect = line_surface.get_rect(center=(512, current_y))  # Center on full screen (1024/2=512)
                    surface.blit(line_surface, line_rect)
                    current_y += DIALOGUE_TEXT_LINE_HEIGHT # SPACING line_height from constants
            except Exception as e:
                # Fallback: draw atmosphere text without wrapping
                draw_centered_text(surface, atmosphere, atmo_font, text_y + 35, WHITE, screen_width=1024)
        
        # === BUTTON ZONE (STANDARDIZED) ===
        button_y = LAYOUT_BUTTON_Y
        actions = area_data.get('actions', {})

        if actions:            
            # Calculate flexible button widths based on text content
            button_height = BUTTON_SIZES['medium'][1]  # 50px standard height
            button_font = fonts.get('fantasy_small', fonts['normal'])
            button_spacing = 20

            # Calculate individual button widths
            button_configs = []
            total_text_width = 0

            for action_name, action_data in actions.items():
                label = action_data.get('label', action_name.replace('_', ' ').lower())
                text_width = button_font.size(label)[0]
                button_width = max(text_width + 40, 80)  # 40px padding, 80px minimum
                button_configs.append({
                    'action_name': action_name,
                    'label': label,
                    'width': button_width
                })
                total_text_width += button_width

            # Calculate spacing and positioning
            total_button_area = total_text_width + (len(button_configs) - 1) * button_spacing
            start_x = (1024 - total_button_area) // 2

            # Position buttons with flexible widths
            button_rects = {}
            current_x = start_x

            for config in button_configs:
                button_rect = draw_button(surface, current_x, button_y, 
                                        config['width'], button_height, 
                                        config['label'], button_font)
                button_rects[config['action_name']] = button_rect
                current_x += config['width'] + button_spacing

        
        return {
            'button_rects': button_rects,
            'area_id': self.current_area,
            'location_type': self.location_type
        }
    
    def handle_action(self, action_data: Dict[str, Any], game_state, 
                 event_manager) -> Optional[str]:
        """Process action triggered by user interaction"""
        
        action_type = action_data.get('type')
        action_name = action_data.get('action_name')  # For special actions
        
        print(f"🔧 BaseLocation handling action: {action_type or action_name}")
        
        if action_type == 'navigate':
            target = action_data.get('target')
            if target:
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": target,
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "navigate_success"
        
        elif action_type == 'dialogue':
            npc_id = action_data.get('npc_id')
            if npc_id:
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": f"{npc_id}_dialogue",
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "dialogue_success"
        
        elif action_type == 'shopping':
            merchant_id = action_data.get('merchant_id', action_data.get('npc_id'))
            if merchant_id:
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": f"{merchant_id}_shop", 
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "shopping_success"
        
        # Handle special actions (like 'back' buttons)
        elif action_name:
            if action_name == 'back':
                # Navigate back to parent location
                area_data = self.get_current_area_data()
                parent = area_data.get('parent', 'broken_blade_main')
                
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": parent,
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "back_success"
        
        print(f"⚠️ Unhandled action: {action_type or action_name}")
        return None


class NPCSelectionLocation(BaseLocation):
    """
    Location type for selecting from multiple NPCs
    
    Examples: Patron Selection, Market Vendors, Town Square
    Displays list of NPCs to interact with
    """
    
    def __init__(self, location_data: Dict[str, Any]):
        super().__init__(location_data)
        self.location_type = "npc_selection"
    
    def render(self, surface: pygame.Surface, game_state, fonts: Dict, images: Dict, 
               controller=None) -> Dict[str, Any]:
        """Render NPC selection with portraits/names and back button"""
        
        surface.fill(BLACK)
        area_data = self.get_current_area_data()
        
        # Calculate display width (accounting for party panel)

        image_width = 1024 - PARTY_PANEL_WIDTH - 10  # 10px spacing

        # === IMAGE ZONE ===
        image_y = LAYOUT_IMAGE_Y
        image_height = LAYOUT_IMAGE_HEIGHT
        draw_border(surface, 0, image_y, 1024, image_height)
        
        # Background
        border_thickness = 6
        img_x = border_thickness
        img_y = image_y + border_thickness
        img_width = 1024 - 2 * border_thickness
        img_height = image_height - 2 * border_thickness
        
        pygame.draw.rect(surface, (40, 20, 10), (img_x, img_y, img_width, img_height))
        
        # Title
        title = area_data.get('title', 'SELECT CHARACTER')
        title_font = fonts.get('fantasy_large', fonts['header'])
        draw_centered_text(surface, title, title_font, image_y + 240, YELLOW)
        
        # === DIALOG ZONE ===
        dialog_y = LAYOUT_DIALOG_Y
        dialog_height = LAYOUT_DIALOG_HEIGHT
        draw_border(surface, 20, dialog_y, 1024-40, dialog_height)
        
        # Instructions
        description = area_data.get('description', {})
        if isinstance(description, dict):
            prompt = description.get('prompt', 'Choose someone to approach:')
        else:
            prompt = str(description)
        
        text_y = LAYOUT_DIALOG_TEXT_Y
        prompt_font = fonts.get('fantasy_medium', fonts['normal'])
        draw_centered_text(surface, prompt, prompt_font, text_y, WHITE)
        
        # === BUTTON ZONE ===
        button_y = LAYOUT_BUTTON_Y
        npcs = area_data.get('npcs', [])
        
        button_rects = {}
        # button_width now calculated dynamically
        # button_height = 40  # moved to individual sections
        # button_spacing = 15  # moved to individual sections
        
       # NPC buttons with flexible sizing
        if npcs:
            button_font = fonts.get('fantasy_small', fonts['normal'])
            button_height = 40
            button_spacing = 15
            
            # Calculate flexible button widths for NPC names
            button_configs = []
            
            for npc_data in npcs:
                if isinstance(npc_data, dict):
                    npc_name = npc_data.get('name', npc_data.get('id', '').title())
                    npc_id = npc_data.get('id')
                else:
                    npc_name = npc_data.replace('_', ' ').title()
                    npc_id = npc_data
                
                text_width = button_font.size(npc_name)[0]
                button_width = max(text_width + 30, 100)  # 30px padding, 100px minimum
                button_configs.append({
                    'npc_id': npc_id,
                    'name': npc_name,
                    'width': button_width
                })
            
            # Arrange in rows (max 3 per row to accommodate longer names)
            npcs_per_row = 3
            rows_needed = (len(button_configs) + npcs_per_row - 1) // npcs_per_row
            
            for row in range(rows_needed):
                row_configs = button_configs[row * npcs_per_row:(row + 1) * npcs_per_row]
                
                # Calculate total width for this row
                total_row_width = sum(config['width'] for config in row_configs)
                total_spacing = (len(row_configs) - 1) * button_spacing
                row_total_width = total_row_width + total_spacing
                
                # Center the row
                start_x = (image_width - row_total_width) // 2
                current_y = button_y + row * (button_height + 15)
                current_x = start_x
                
                # Draw buttons in this row
                for config in row_configs:
                    button_rect = draw_button(surface, current_x, current_y, 
                                            config['width'], button_height, 
                                            config['name'], button_font)
                    button_rects[config['npc_id']] = button_rect
                    current_x += config['width'] + button_spacing
        
        # Back button
        back_rect = draw_button(surface, 50, button_y + 60, 120, 40, "BACK", fonts['normal'])
        button_rects['back'] = back_rect
        
        return {
            'button_rects': button_rects,
            'area_id': self.current_area,
            'location_type': self.location_type
        }
    
    def handle_action(self, action_data: Dict[str, Any], game_state, 
                 event_manager) -> Optional[str]:
        """Process NPC selection clicks"""
        
        action_type = action_data.get('type')
        action_name = action_data.get('action_name')  # For special actions like 'back'
        
        print(f"🗣️ NPCSelectionLocation handling action: {action_type or action_name}")
        
        # Handle JSON-defined actions first
        if action_type == 'navigate':
            target = action_data.get('target')
            if target:
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": target,
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "navigate_success"
        
        elif action_type == 'dialogue':
            npc_id = action_data.get('npc_id')
            if npc_id:
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": f"{npc_id}_dialogue",
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "dialogue_success"
        
        # Handle special actions (like 'back' button or direct NPC clicks)
        elif action_name:
            if action_name == 'back':
                # Navigate back to parent location
                area_data = self.get_current_area_data()
                parent = area_data.get('parent', 'broken_blade_main')
                
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": parent,
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "back_success"
            
            else:
                # Assume it's an NPC selection (patron click)
                npc_id = action_name
                event_manager.emit("SCREEN_CHANGE", {
                    "target_screen": f"{npc_id}_dialogue",
                    "source_screen": f"{self.location_id}_{self.current_area}"
                })
                return "npc_selected"
        
        # Handle action passed as direct action name (legacy support)
        else:
            action = action_data.get('action')
            if action:
                if action == 'back':
                    area_data = self.get_current_area_data()
                    parent = area_data.get('parent', 'broken_blade_main')
                    
                    event_manager.emit("SCREEN_CHANGE", {
                        "target_screen": parent,
                        "source_screen": f"{self.location_id}_{self.current_area}"
                    })
                    return "back_success"
                
                else:
                    # Assume it's an NPC ID
                    npc_id = action
                    event_manager.emit("SCREEN_CHANGE", {
                        "target_screen": f"{npc_id}_dialogue",
                        "source_screen": f"{self.location_id}_{self.current_area}"
                    })
                    return "npc_selected"
        
        print(f"⚠️ NPCSelectionLocation: Unhandled action: {action_type or action_name or action_data}")
        return None


# Location factory function
def create_location(location_data: Dict[str, Any]) -> BaseLocation:
    """
    Factory function to create appropriate location type from JSON data
    
    Args:
        location_data: Dictionary loaded from location JSON file
        
    Returns:
        BaseLocation subclass instance
    """
    
    # Determine location type from first area or explicit type
    location_type = location_data.get('type')
    
    if not location_type and location_data.get('areas'):
        # Infer type from first area
        first_area = list(location_data['areas'].values())[0]
        location_type = first_area.get('type', 'action_hub')
    
    if location_type == 'action_hub':
        return ActionHubLocation(location_data)
    elif location_type == 'npc_selection':
        return NPCSelectionLocation(location_data)
    else:
        # Default to action hub
        print(f"⚠️ Unknown location type '{location_type}', defaulting to action_hub")
        return ActionHubLocation(location_data)