"""
Terror in Redstone - Quest Log Overlay
Professional 2-tab quest management system following BaseTabbedOverlay pattern
Integrates with professional quest system for real quest data
"""

import pygame
from utils.tabbed_overlay_utils import BaseTabbedOverlay
from utils.constants import (YELLOW, WHITE, BRIGHT_GREEN, BROWN, DARK_GRAY, CORNFLOWER_BLUE,
                             wrap_text, DARK_BROWN, WALNUT_BROWN)
from utils.graphics import draw_text

class QuestOverlay(BaseTabbedOverlay):
    """3-tab quest log overlay (Main | Side | Completed)"""
    
    def __init__(self, screen_manager=None):
        super().__init__("quest_key", "QUEST LOG", screen_manager)
        
        # Add tabs following the established pattern
        self.add_tab("main_quests", "Main", pygame.K_1)
        self.add_tab("side_quests", "Side", pygame.K_2)
        self.add_tab("completed_quests", "Completed", pygame.K_3)
        
        # Quest selection state
        self.selected_quest = None
        self.quest_rects = []

        #PAGINATION VARIABLES:
        self.main_page = 0
        self.side_page = 0
        self.completed_page = 0
        self.quests_per_page = 7  # Show Number of quests per page
        
        
        print("🗒️ QuestOverlay initialized with 3 tabs")
    
    def render_tab_content(self, surface: pygame.Surface, active_tab, game_state, fonts, images):
        """
        Render tab-specific content based on active tab
        DESIGN PRINCIPLE: 
        Each tab handles its own content rendering while framework manages tabs
        """
        content_rect = self.get_content_area_rect()
        tab_id = active_tab.tab_id if hasattr(active_tab, 'tab_id') else active_tab
        
        try:
            if tab_id == "main_quests":
                self._render_main_quests(surface, content_rect, game_state, fonts)
            elif tab_id == "side_quests":
                self._render_side_quests(surface, content_rect, game_state, fonts)
            elif tab_id == "completed_quests":
                self._render_completed_quests(surface, content_rect, game_state, fonts)
            else:
                self._render_fallback_content(surface, content_rect, fonts, f"Unknown tab: {tab_id}")
                
        except Exception as e:
            print(f"❌ Error rendering quest tab {tab_id}: {e}")
            self._render_fallback_content(surface, content_rect, fonts, "Error loading quest data")
    
    def _render_main_quests(self, surface, content_rect, game_state, fonts):
        """Render main quests tab (type == primary, display_in_log != false, active)"""
        quests = self._get_quests_by_type(game_state, ["primary"])
        if not quests:
            self._render_empty_quest_list(surface, content_rect, fonts, "No active main quests.")
            return
        self._render_quest_content(surface, content_rect, quests, game_state, fonts, "Main Quests")

    def _render_side_quests(self, surface, content_rect, game_state, fonts):
        """Render side quests tab (type secondary/side_task, display_in_log != false, active)"""
        quests = self._get_quests_by_type(game_state, ["secondary", "side_task"])
        if not quests:
            self._render_empty_quest_list(surface, content_rect, fonts, "No active side quests.")
            return
        self._render_quest_content(surface, content_rect, quests, game_state, fonts, "Side Quests")
    
    def _render_completed_quests(self, surface, content_rect, game_state, fonts):
        """Render completed quests tab content"""
        # Get quest data from quest system
        completed_quests = self._get_completed_quests(game_state)
        
        if not completed_quests:
            self._render_empty_quest_list(surface, content_rect, fonts, "No completed quests yet")
            return
        
        # Render quest list and details using existing layout
        self._render_quest_content(surface, content_rect, completed_quests, game_state, fonts, "Completed Quests")
    
    def _get_quests_by_type(self, game_state, types):
        """Get active quests filtered by type list, skipping display_in_log: false entries."""
        if not hasattr(game_state, 'quest_manager'):
            print("⚠️ Quest manager not found in game state")
            return []

        from utils.narrative_schema import narrative_schema
        quest_definitions = narrative_schema.schema.get("quest_definitions", {})

        quest_list = []
        for quest in game_state.quest_manager.get_active_quests():
            quest_def = quest_definitions.get(quest.id, {})
            if not quest_def.get("display_in_log", True):
                continue
            if quest_def.get("type", "secondary") not in types:
                continue
            completed, total = quest.get_progress()
            quest_list.append({
                'id': quest.id,
                'title': quest.title,
                'description': quest.description,
                'completed': False,
                'progress': f"{completed}/{total}",
                'objectives': [
                    {'description': obj.description, 'completed': obj.completed}
                    for obj in quest.objectives if not getattr(obj, 'hidden', False)
                ]
            })
        return quest_list
    
    def _get_completed_quests(self, game_state):
        """Get completed quests AND completed objectives from quest system"""
        if hasattr(game_state, 'quest_manager'):
            quest_manager = game_state.quest_manager
            quest_list = []
            
            # Get fully completed quests
            completed_quests = quest_manager.get_completed_quests()
            for quest in completed_quests:
                completed, total = quest.get_progress()
                quest_data = {
                    'id': quest.id,
                    'title': quest.title,
                    'description': quest.description,
                    'completed': True,
                    'progress': "COMPLETE",
                    'objectives': [
                        {
                            'description': obj.description,
                            'completed': obj.completed
                        }
                        for obj in quest.objectives if not getattr(obj, 'hidden', False)
                    ]
                }
                quest_list.append(quest_data)
            
            # Get completed individual objectives from active quests
            active_quests = quest_manager.get_active_quests()
            for quest in active_quests:
                for obj in quest.objectives:
                    if obj.completed and not getattr(obj, 'hidden', False):
                        # Create a quest-like entry for completed objectives
                        objective_data = {
                            'id': f"{quest.id}.{obj.id}",
                            'title': f"✅ {obj.description}",
                            'description': f"Discovered from: {quest.title}",
                            'completed': True,
                            'progress': "COMPLETE",
                            'objectives': []  # Individual objectives don't have sub-objectives
                        }
                        quest_list.append(objective_data)
            
            return quest_list
        
        print("⚠️ Quest manager not found in game state")
        return []
    
    def _render_quest_content(self, surface, content_rect, quests, game_state, fonts, section_title):
        """Render quest list and details using the classic 2-column layout"""        
       #Refresh quest states
        if hasattr(game_state, 'quest_manager'):
            game_state.quest_manager.update_from_game_state()
        else:
            print(f"❌ No quest_manager found!")
        
        # Calculate layout areas (preserving original quest_log.py layout)
        quest_list_x = content_rect.x + 20
        quest_list_y = content_rect.y + 20
        quest_list_width = 350  # Left column for quest list
        quest_list_height = content_rect.height - 40
        
        # Divider line
        divider_x = quest_list_x + quest_list_width + 10
        divider_y = quest_list_y
        divider_height = quest_list_height
        
        # Quest details area  
        details_x = divider_x + 20
        details_y = quest_list_y
        details_width = content_rect.width - (details_x - content_rect.x) - 20
        details_height = quest_list_height
        
        # Draw quest list background
        pygame.draw.rect(surface, DARK_BROWN, 
                        (quest_list_x, quest_list_y, quest_list_width, quest_list_height))
        pygame.draw.rect(surface, WHITE, 
                        (quest_list_x, quest_list_y, quest_list_width, quest_list_height), 2)
        
        # Draw divider line
        pygame.draw.line(surface, WHITE, 
                        (divider_x, divider_y), (divider_x, divider_y + divider_height), 3)
        
        # Draw quest details background
        pygame.draw.rect(surface, DARK_BROWN, 
                        (details_x, details_y, details_width, details_height))
        pygame.draw.rect(surface, WHITE, 
                        (details_x, details_y, details_width, details_height), 2)
        
        # Draw quest list
        self.quest_rects = []
        row_height = 40
        start_y = quest_list_y + 10
        
        # Headers
        font = fonts.get('fantasy_small', fonts['normal'])
        small_font = fonts.get('small', fonts['normal'])
        
        # Draw "Quest Title" and "Progress" headers
        header_y = start_y
        header_text = font.render("Quest Title", True, WHITE)
        surface.blit(header_text, (quest_list_x + 10, header_y))

        progress_text = font.render("Progress", True, WHITE)
        surface.blit(progress_text, (quest_list_x + 230, header_y))
        
        # Draw header separator line
        header_line_y = header_y + 25
        pygame.draw.line(surface, WHITE, 
                        (quest_list_x + 10, header_line_y), 
                        (quest_list_x + quest_list_width - 10, header_line_y), 2)
        
        # PAGINATION CALCULATIONS:
        total_quests = len(quests)
        active_tab = self.get_active_tab()
        tab_id = active_tab.tab_id if hasattr(active_tab, 'tab_id') else ""
        if tab_id == "main_quests":
            current_page = self.main_page
        elif tab_id == "side_quests":
            current_page = self.side_page
        else:
            current_page = self.completed_page
        total_pages = max(1, (total_quests + self.quests_per_page - 1) // self.quests_per_page)

        # Ensure current page is valid (clamp page numbers)
        if current_page >= total_pages:
            current_page = total_pages - 1
            if tab_id == "main_quests":
                self.main_page = current_page
            elif tab_id == "side_quests":
                self.side_page = current_page
            else:
                self.completed_page = current_page

        # Get quests for current page
        start_idx = current_page * self.quests_per_page
        end_idx = min(start_idx + self.quests_per_page, total_quests)
        page_quests = quests[start_idx:end_idx]
        
        # Draw quest rows
        current_y = header_line_y + 10
        
        for quest in page_quests:
            quest_rect = pygame.Rect(quest_list_x + 5, current_y - 5, 
                                   quest_list_width - 10, row_height)
            self.quest_rects.append((quest_rect, quest['id']))

            # Highlight selected quest
            if self.selected_quest == quest['id']:
                pygame.draw.rect(surface, CORNFLOWER_BLUE, quest_rect)
            
            # Draw quest status indicator
            status_x = quest_list_x + 15
            status_y = current_y + 10
            
            if quest['completed']:
                # Draw checkmark for completed quests
                pygame.draw.circle(surface, BRIGHT_GREEN, (status_x, status_y), 8)
                # Simple checkmark using lines
                pygame.draw.line(surface, WHITE, (status_x - 3, status_y), (status_x, status_y + 3), 2)
                pygame.draw.line(surface, WHITE, (status_x, status_y + 3), (status_x + 4, status_y - 2), 2)
            else:
                # Draw open circle for active quests
                pygame.draw.circle(surface, WHITE, (status_x, status_y), 8, 2)
            
            # Draw quest title (truncated if needed)
            title_x = quest_list_x + 40
            max_title_width = 220  # Leave room for progress text
            title_text = quest['title']
            
            # Truncate title if too long
            title_surface = small_font.render(title_text, True, WHITE)
            if title_surface.get_width() > max_title_width:
                # Gradually shorten until it fits
                while title_surface.get_width() > max_title_width and len(title_text) > 10:
                    title_text = title_text[:-4] + "..."
                    title_surface = small_font.render(title_text, True, WHITE)
            
            surface.blit(title_surface, (title_x, current_y + 5))
            
            # Draw progress text
            progress_text = quest['progress']
            if progress_text == "COMPLETE":
                # Use even smaller font for COMPLETE to match numerical progress
                tiny_font = fonts.get('fantasy_micro', fonts['small'])
                progress_surface = tiny_font.render(progress_text, True, WHITE)
            else:
                progress_surface = small_font.render(progress_text, True, WHITE)
            progress_text_x = quest_list_x + 260
            surface.blit(progress_surface, (progress_text_x, current_y + 5))
            
            current_y += row_height
        
        # PAGE NAVIGATION DISPLAY:
        if total_pages > 1:
            page_y = current_y + 20
            page_text = f"Page {current_page + 1} of {total_pages}"
            
            # Center the page text in the quest list area
            page_font = fonts.get('fantasy_small', fonts['normal'])
            page_surface = page_font.render(page_text, True, YELLOW)
            page_x = quest_list_x + (quest_list_width - page_surface.get_width()) // 2
            surface.blit(page_surface, (page_x, page_y))
            
            # Add navigation hint
            hint_y = page_y + 25
            hint_text = "UP/DOWN or P/N to navigate pages"
            hint_font = fonts.get('fantasy_tiny', fonts['small'])
            hint_surface = hint_font.render(hint_text, True, WHITE)
            hint_x = quest_list_x + (quest_list_width - hint_surface.get_width()) // 2
            surface.blit(hint_surface, (hint_x, hint_y))

        # Draw quest details
        if self.selected_quest:
            quest_data = next((q for q in quests if q['id'] == self.selected_quest), None)
            if quest_data:
                self._draw_quest_details(surface, quest_data, details_x, details_y, 
                                       details_width, details_height, fonts)
        else:
            # Show prompt to select a quest
            prompt_y = details_y + details_height // 2
            prompt_text = fonts.get('normal', font).render("Select a quest to view details", True, WHITE)
            text_x = details_x + (details_width - prompt_text.get_width()) // 2
            surface.blit(prompt_text, (text_x, prompt_y))
    
    def _draw_quest_details(self, surface, quest_data, x, y, width, height, fonts):
        """Draw detailed quest information in the right panel"""
        font = fonts.get('normal', fonts['header'])
        small_font = fonts.get('small', font)
        
        # Quest title
        title_y = y + 20
        title_surface = small_font.render(quest_data['title'], True, BRIGHT_GREEN)
        surface.blit(title_surface, (x + 20, title_y))
        
        # Quest description with word wrapping
        desc_y = title_y + 40
        description = quest_data['description']
        
        # Quest description with professional word wrapping using constants.py utility
        desc_y = title_y + 40
        description = quest_data['description']

        # Use the established wrap_text function from constants.py
        max_width = width - 40  # Leave margins
        wrapped_lines = wrap_text(description, small_font, max_width)

        # Draw wrapped description lines
        line_height = 25
        current_y = desc_y

        for line_surface in wrapped_lines:
            if current_y + line_height > y + height - 100:  # Leave room for objectives
                break
            surface.blit(line_surface, (x + 20, current_y))
            current_y += line_height
        
        # Draw objectives
        if quest_data.get('objectives'):
            current_y += 20
            obj_header = font.render("Objectives:", True, BRIGHT_GREEN)
            surface.blit(obj_header, (x + 20, current_y))
            current_y += 30
            
            for objective in quest_data['objectives']:
                if current_y + 20 > y + height - 20:
                    break
                
                # Draw objective with manual wrapping and proper colors
                status_char = "✓" if objective['completed'] else "○"
                status_color = BRIGHT_GREEN if objective['completed'] else WHITE
                
                # Use smaller font
                tiny_font = fonts.get('fantasy_tiny', fonts.get ('fantasy.micro', fonts['small']))
                obj_text = f"{status_char} {objective['description']}"
                
                # Manual wrapping with color preservation
                words = obj_text.split(' ')
                lines = []
                current_line = ''
                max_obj_width = width - 80
                
                for word in words:
                    test_line = current_line + word + ' ' if current_line else word + ' '
                    if tiny_font.size(test_line)[0] <= max_obj_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line.strip())
                        current_line = word + ' '
                
                if current_line:
                    lines.append(current_line.strip())
                
                # Draw each line with proper color
                for line in lines:
                    if current_y + 20 > y + height - 20:
                        break
                    line_surface = tiny_font.render(line, True, status_color)
                    surface.blit(line_surface, (x + 40, current_y))
                    current_y += 20

    def previous_page(self):
        """Navigate to previous page (called by BaseTabbedOverlay)"""
        active_tab = self.get_active_tab()
        tab_id = active_tab.tab_id if hasattr(active_tab, 'tab_id') else ""
        if tab_id == "main_quests" and self.main_page > 0:
            self.main_page -= 1
        elif tab_id == "side_quests" and self.side_page > 0:
            self.side_page -= 1
        elif tab_id == "completed_quests" and self.completed_page > 0:
            self.completed_page -= 1

    def next_page(self):
        """Navigate to next page (called by BaseTabbedOverlay)"""
        active_tab = self.get_active_tab()
        tab_id = active_tab.tab_id if hasattr(active_tab, 'tab_id') else ""
        if tab_id == "main_quests":
            self.main_page += 1
        elif tab_id == "side_quests":
            self.side_page += 1
        elif tab_id == "completed_quests":
            self.completed_page += 1

    def _render_empty_quest_list(self, surface, content_rect, fonts, message):
        """Render empty quest list message"""
        # Center the message
        text_width = len(message) * 12  # Rough estimate for centering
        text_x = content_rect.x + (content_rect.width - text_width) // 2
        text_y = content_rect.y + (content_rect.height - 30) // 2
        
        draw_text(surface, message, 
                fonts.get('fantasy_medium', fonts.get('normal', pygame.font.Font(None, 24))),
                text_x, text_y, WHITE)
    
    def _render_fallback_content(self, surface, content_rect, fonts, message):
        """Render fallback content when there's an error"""
        # Center the error message
        text_width = len(message) * 12  # Rough estimate for centering
        text_x = content_rect.x + (content_rect.width - text_width) // 2
        text_y = content_rect.y + (content_rect.height - 30) // 2
        
        draw_text(surface, message, 
                fonts.get('fantasy_medium', fonts.get('normal', pygame.font.Font(None, 24))),
                text_x, text_y, WHITE)
    
    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks on quest items and tabs"""
        # FIRST: Check if click was on a tab (let parent handle it)
        if super().handle_mouse_click(mouse_pos):
            return True
        
        # SECOND: Check quest selection (only if not a tab click)
        for quest_rect, quest_id in self.quest_rects:
            if quest_rect.collidepoint(mouse_pos):
                self.selected_quest = quest_id
                print(f"📋 Quest selected: {quest_id}")
                return True
        
        # Clear selection if clicked on empty space
        self.selected_quest = None
        return False

    def handle_quest_overlay_click(mouse_pos, result):
        """
        COMPATIBILITY: Handle clicks on quest overlay
        
        This maintains the exact same interface as your original quest_log.py
        but internally uses the new tabbed overlay system.
        """
        overlay = get_quest_overlay()
        
        # Try to handle tab clicks first  
        if overlay.handle_mouse_click(mouse_pos):
            return None  # Tab click handled
        
        # No clicks handled - equivalent to your original behavior
        return None

    def handle_quest_keyboard_input(key, game_state):
        """NEW: Handle keyboard input for quest overlay"""
        if getattr(game_state, 'quest_log_open', False):
            overlay = get_quest_overlay()
            return overlay.handle_keyboard_input(key)
        return False



# Compatibility function for ScreenManager integration
# ========================================
# COMPATIBILITY LAYER
# ========================================

# Create global instance
quest_overlay_instance = None

def get_quest_overlay():
    """Get the global quest overlay instance"""
    global quest_overlay_instance
    if quest_overlay_instance is None:
        quest_overlay_instance = QuestOverlay()
    return quest_overlay_instance

def draw_quest_overlay(surface, game_state, fonts, images=None):
    """
    Compatibility function for ScreenManager
    """
    
    overlay = get_quest_overlay()
    
    # Register with input handler on first render if not already registered
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

def handle_quest_overlay_click(mouse_pos, result):
    """
    COMPATIBILITY: Handle clicks on quest overlay
    
    This maintains the exact same interface as your original quest_log.py
    but internally uses the new tabbed overlay system.
    """
    overlay = get_quest_overlay()
    return overlay.handle_mouse_click(mouse_pos)

def handle_quest_keyboard_input(key, game_state):
    """NEW: Handle keyboard input for quest overlay - CRITICAL FOR TAB NAVIGATION"""
    if getattr(game_state, 'quest_log_open', False):
        overlay = get_quest_overlay()
        key_name = pygame.key.name(key)
        print(f"🎯 Quest overlay processing key: {key_name}")
        result = overlay.handle_keyboard_input(key)
        if result:
            print(f"✅ Quest overlay handled key: {key_name}")
        else:
            print(f"❌ Quest overlay ignored key: {key_name}")
        return result
    return False