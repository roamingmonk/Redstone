# utils/debug_manager.py
"""
Debug Manager - Professional Debug Infrastructure
Handles all debugging functionality, keeping GameController lean
"""


class DebugManager:
    """
    Professional debug system for Terror in Redstone
    Centralizes all debugging functionality and coordinates with other systems
    """
    
    def __init__(self, game_state, event_manager):
        self.game_state = game_state
        self.event_manager = event_manager
        self.debug_mode = False
        
        # Register for debug events
        self.event_manager.register("DEBUG_TOGGLE", self.handle_debug_toggle)
        self.event_manager.register("DEBUG_PERFORMANCE", self.handle_quest_debug)
        self.event_manager.register("DEBUG_SAVE_STATE", self.handle_save_debug)
        
        print("🔧 DebugManager initialized - Professional debug system ready!")
    
    def handle_debug_toggle(self, data):
        """Handle F1 - Toggle general debug mode"""
        self.debug_mode = not self.debug_mode
        print(f"🔧 F1 Debug mode: {'ON' if self.debug_mode else 'OFF'}")
        
        # Toggle event manager debug logging
        self.event_manager.enable_debug_logging(self.debug_mode)
        
        # Toggle input handler debug (if available)
        input_handler = self.event_manager.get_service('input_handler')
        if input_handler and hasattr(input_handler, 'enable_debug_input'):
            input_handler.enable_debug_input(self.debug_mode)
    
    def handle_quest_debug(self, data):
        """Handle F2 - Show detailed quest state debug info"""
        print("🔍 F2 - Quest State Debug Requested")
        self._debug_quest_state()
        
        # Force quest system update and show results
        if hasattr(self.game_state, 'quest_manager'):
            print("🔄 Forcing quest system update...")
            self.game_state.quest_manager.update_from_game_state()
            print("✅ Quest system updated")
    
    def handle_save_debug(self, data):
        """Handle F3 - Show save state debug info"""
        print("💾 F3 - Save State Debug Requested")
        self._debug_save_state()
    
    def render_debug_overlay(self, surface, fonts):
        
        """Render on-screen debug overlay - F1 toggle"""
        if not self.debug_mode:
            return
        import pygame

        # Get font - use normal font instead of small
        debug_font = fonts.get('small', None)
        if not debug_font:
            return
        
        # Semi-transparent background
        overlay_width = 320
        overlay_height = 320
        overlay_surface = pygame.Surface((overlay_width, overlay_height))
        overlay_surface.set_alpha(200)
        overlay_surface.fill((0, 0, 0))  # Black background
        
        # Position in top-right corner
        x_pos = surface.get_width() - overlay_width - 0
        y_pos = 10
        
        # Draw background
        surface.blit(overlay_surface, (x_pos, y_pos))
        
        # Draw border
        #import pygame
        #pygame.draw.rect(surface, (0, 255, 0), 
        #                (x_pos, y_pos, overlay_width, overlay_height), 2)
        
        # Draw debug info
        self._draw_debug_lines(surface, debug_font, x_pos + 15, y_pos + 15)
    
    def _draw_debug_lines(self, surface, font, start_x, start_y):
        """Draw all debug information lines"""
        import pygame
        y_offset = 0
        line_height = 25
        
        # Core system info
        debug_lines = self._get_debug_lines()
        
        for line in debug_lines:
            color = (0, 255, 0)  # Green text like you had before
            if line.startswith("ERROR"):
                color = (255, 0, 0)  # Red for errors
            elif line.startswith("WARN"):
                color = (255, 255, 0)  # Yellow for warnings
            
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (start_x, start_y + y_offset))
            y_offset += line_height
    
    def _get_debug_lines(self):
        """Generate all debug information lines"""
        lines = []
        
        # Header
        lines.append("=== DEBUG INFO (F1) ===")
        lines.append("")
        
        # Core system status
        lines.append(f"Screen: {self.game_state.screen}")
        lines.append(f"FPS: {getattr(self.game_state, 'current_fps', 'N/A')}")
        lines.append(f"Errors: {getattr(self.game_state, 'error_count', 0)}")
        
        # Overlay status
        overlays_active = []
        if getattr(self.game_state, 'inventory_open', False):
            overlays_active.append("inventory")
        if getattr(self.game_state, 'quest_log_open', False):
            overlays_active.append("quest")
        if getattr(self.game_state, 'character_sheet_open', False):
            overlays_active.append("character")
        if getattr(self.game_state, 'help_screen_open', False):
            overlays_active.append("help")
            
        lines.append(f"Overlays: {', '.join(overlays_active) if overlays_active else 'none'}")
        #lines.append("")
        
        # Player position (if in town navigation)
        if hasattr(self.game_state, 'town_player_x'):
            lines.append(f"Town Pos: ({self.game_state.town_player_x}, {self.game_state.town_player_y})")
            # Get navigation debug info if available
            nav_info = self._get_navigation_debug()
            lines.extend(nav_info)
        
        lines.append("")
        
        # Key game state flags
        #lines.append("=== KEY FLAGS ===")
        #lines.append(f"Quest Active: {getattr(self.game_state, 'quest_active', False)}")
        #lines.append(f"Mayor Talked: {getattr(self.game_state, 'mayor_talked', False)}")
        #lines.append(f"Party Size: {len(getattr(self.game_state, 'party_members', []))}")
        
        # Recruitment flags
        #recruitment_flags = ['gareth_recruited', 'elara_recruited', 'thorman_recruited', 'lyra_recruited']
        #recruited = [flag for flag in recruitment_flags if getattr(self.game_state, flag, False)]
        #lines.append(f"Recruited: {', '.join(recruited) if recruited else 'none'}")

        lines.append("")  # Blank line
        lines.append("=== INVESTIGATION SITES ===")
        investigations = {
            'Swamp Church': getattr(self.game_state, 'learned_about_swamp_church', False),
            'Hill Ruins': getattr(self.game_state, 'learned_about_ruins', False),
            'Refugee Camp': getattr(self.game_state, 'learned_about_refugees', False)
        }
        completed_investigations = [name for name, completed in investigations.items() if completed]
        lines.append(f"Discovered: {', '.join(completed_investigations) if completed_investigations else 'none'}")
        lines.append(f"Progress: {len(completed_investigations)}/3")
        
        # This after the Investigation Sites section:
        lines.append("")  # Blank line
        lines.append("=== QUEST OBJECTIVES DEBUG ===")
        if hasattr(self.game_state, 'quest_manager'):
            quest_manager = self.game_state.quest_manager
            for quest_id, quest in quest_manager.quests.items():
                if quest.status == "active":
                    lines.append(f"{quest_id}:")
                    for obj in quest.objectives:
                        status = "✅" if obj.completed else "❌"
                        lines.append(f"  {status} {obj.id}: {obj.description}")
        else:
            lines.append("No quest manager found")

        return lines
    
    def _get_navigation_debug(self):
        """Get navigation-specific debug info"""
        lines = []
        
        # Try to get current building info from navigation instance
        try:
            from screens.redstone_town import _town_navigation_instance
            if _town_navigation_instance:
                current_building = _town_navigation_instance.current_building
                if current_building:
                    lines.append(f"Building: {current_building.get('name', 'Unknown')}")
                    lines.append(f"Screen: {current_building.get('screen', 'N/A')}")
                else:
                    lines.append("Building: none")
        except Exception as e:
            lines.append(f"Nav Debug: Error - {str(e)[:20]}")
        
        return lines


    def _debug_quest_state(self):
        """Print current quest-relevant flags for debugging"""
        print("\n" + "="*50)
        print("🔍 QUEST DEBUG STATE (F2)")
        print("="*50)

        # Core conversation flags
        print(f"mayor_talked: {getattr(self.game_state, 'mayor_talked', False)}")
        print(f"meredith_talked: {getattr(self.game_state, 'meredith_talked', False)}")
        print(f"garrick_talked: {getattr(self.game_state, 'garrick_talked', False)}")
        print(f"quest_active: {getattr(self.game_state, 'quest_active', False)}")
        print(f"learned_about_swamp_church: {getattr(self.game_state, 'learned_about_swamp_church', False)}")
        print(f"learned_about_ruins: {getattr(self.game_state, 'learned_about_ruins', False)}")
        print(f"learned_about_refugees: {getattr(self.game_state, 'learned_about_refugees', False)}")

        # Recruitment flags (narrative schema style)
        print(f"\n🎯 RECRUITMENT FLAGS:")
        print(f"gareth_recruited: {getattr(self.game_state, 'gareth_recruited', False)}")
        print(f"elara_recruited: {getattr(self.game_state, 'elara_recruited', False)}")
        print(f"thorman_recruited: {getattr(self.game_state, 'thorman_recruited', False)}")
        print(f"lyra_recruited: {getattr(self.game_state, 'lyra_recruited', False)}")
        
        # Party members list (old system)
        print(f"\n👥 PARTY MEMBERS LIST:")
        party_members = getattr(self.game_state, 'party_members', [])
        print(f"party_members: {party_members}")
        print(f"party count: {len(party_members)}")
        
        # Recruitment count (computed property)
        print(f"\n📊 COMPUTED VALUES:")
        print(f"recruited_count: {self.game_state.recruited_count}")
        print(f"can_recruit_more: {self.game_state.can_recruit_more}")
        
        #Rat Quest status
        print(f"\n🐀 Rat Quest:")
        print(f"Basement Quest Offered: {getattr(self.game_state, 'garrick_offered_basement', False)}")
        print(f"Basement Quest Accepted: {getattr(self.game_state, 'accepted_basement_quest', False)}")
        print(f"Completed Rat Combat: {getattr(self.game_state, 'completed_basement_combat', False)}")
        print(f"Victory Reported to Garrick: {getattr(self.game_state, 'reported_basement_victory', False)}")
        print(f"Garrick Paid player: {getattr(self.game_state, 'garrick_paid', False)}")
        print(f"Acknowledged Payment: {getattr(self.game_state, 'post_payment_acknowledged', False)}")

        # Quest manager status
        if hasattr(self.game_state, 'quest_manager'):
            print(f"\n📋 QUEST MANAGER:")
            active_quests = self.game_state.quest_manager.get_active_quests()
            print(f"Active quests: {[q.id for q in active_quests]}")
            
            # Check specific quest objectives
            party_quest = self.game_state.quest_manager.quests.get("party_building")
            if party_quest:
                print(f"Party building quest status: {party_quest.status}")
                for obj in party_quest.objectives:
                    print(f"  - {obj.id}: {obj.completed}")
        else:
            print("❌ Quest manager not found!")
        
        print("="*50 + "\n")
    
    def _debug_save_state(self):
        """Print save-relevant data for debugging"""
        print("\n" + "="*50)
        print("💾 SAVE STATE DEBUG (F3)")
        print("="*50)
        
        # Character state
        print(f"Character name: {getattr(self.game_state, 'character', {}).get('name', 'Unknown')}")
        print(f"Current screen: {getattr(self.game_state, 'screen', 'Unknown')}")
        print(f"Money: {getattr(self.game_state, 'money', 0)}")
        
        # All narrative flags for save
        try:
            from utils.narrative_schema import narrative_schema
            print(f"\n🚩 ALL NARRATIVE FLAGS:")
            all_flags = narrative_schema.get_all_flags()
            for flag in all_flags:
                value = getattr(self.game_state, flag, False)
                if value:  # Only show flags that are True
                    print(f"  ✓ {flag}: {value}")
        except ImportError:
            print("⚠️ Narrative schema not available")
        
        # Quest save data
        if hasattr(self.game_state, 'quest_manager'):
            quest_save_data = self.game_state.quest_manager.get_quest_data_for_save()
            print(f"\n📋 QUEST SAVE DATA:")
            for quest_id, quest_data in quest_save_data.items():
                print(f"  {quest_id}: {quest_data['status']}")
        
        print("="*50 + "\n")
    
    def force_recruitment_sync(self):
        """Sync party_members list with recruitment flags - for manual debugging"""
        print("🔄 Syncing recruitment systems...")
        
        # Get current recruitment flags
        recruited = []
        if getattr(self.game_state, 'gareth_recruited', False):
            recruited.append('gareth')
        if getattr(self.game_state, 'elara_recruited', False):
            recruited.append('elara')
        if getattr(self.game_state, 'thorman_recruited', False):
            recruited.append('thorman')
        if getattr(self.game_state, 'lyra_recruited', False):
            recruited.append('lyra')
        
        # Update party_members list to match flags
        old_party = getattr(self.game_state, 'party_members', [])
        self.game_state.party_members = recruited
        
        print(f"Updated party_members: {old_party} → {self.game_state.party_members}")
        
        # Force quest update
        if hasattr(self.game_state, 'quest_manager'):
            self.game_state.quest_manager.update_from_game_state()
            print("✅ Quest manager updated")
        
        return len(recruited)