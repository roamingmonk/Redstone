# utils/debug_manager.py
"""
Debug Manager - Professional Debug Infrastructure
Handles all debugging functionality, keeping GameController lean
"""
import pygame
from utils.world_npc_spawner import get_world_npc_spawner
from screens.redstone_town import _town_navigation_instance
from utils.narrative_schema import narrative_schema

class DebugManager:
    """
    Professional debug system for Terror in Redstone
    Centralizes all debugging functionality and coordinates with other systems
    """
    
    def __init__(self, game_state, event_manager):
        self.game_state = game_state
        self.event_manager = event_manager
        self.debug_mode = False
        self.combat_engine = None
        
        # Register for debug events
        self.event_manager.register("DEBUG_TOGGLE", self.handle_debug_toggle)
        self.event_manager.register("DEBUG_PERFORMANCE", self.handle_quest_debug)
        self.event_manager.register("DEBUG_SAVE_STATE", self.handle_save_debug)
        self.event_manager.register("NPC_DEBUG", self.handle_npc_debug)
        self.event_manager.register("COMBAT_DEBUG", self.handle_combat_debug)  
        self.event_manager.register("BUFF_DEBUG", self.handle_buff_debug)

        self.event_manager.register("TIME_ADVANCED", self.handle_time_advanced)
        self.event_manager.register("PARTY_RESTED", self.handle_party_rested)

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
    
    def handle_combat_debug(self, data):
        """Handle F6 - Show combat unit positions and AI state"""
        print("⚔️ F6 - Combat Debug Requested")
        
        # Check if we have a combat engine reference
        if not self.combat_engine:
            print("⚠️ Combat engine not available!")
            return
        
        # Check if combat is actually active
        if not hasattr(self.combat_engine, 'combat_data') or not self.combat_engine.combat_data:
            print("⚠️ Not currently in combat!")
            return
        
        self._debug_combat_positions(self.combat_engine)
    
    def handle_buff_debug(self, data):
        """Handle F9 - Show resistance/buff debug info"""
        print("🛡️ F9 - Resistance/Buff Debug Requested")
        
        # Check if in combat vs out of combat
        if self.combat_engine and hasattr(self.combat_engine, 'combat_data') and self.combat_engine.combat_data:
            self._debug_combat_resistances()
        else:
            self._debug_out_of_combat_status()
    
    def _debug_combat_resistances(self):
        """Show resistance/buff info during combat"""
        print("\n" + "="*60)
        print("🛡️ COMBAT RESISTANCE & BUFF DEBUG")
        print("="*60)
        
        # Get combat data
        combat_data = self.combat_engine.get_combat_data_for_ui()
        
        # Player and party resistances
        print("👥 PARTY STATUS:")
        character_states = combat_data.get("character_states", {})
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            char_data = char_state.get('character_data', {})
            name = char_state.get('name', char_id)
            hp = char_data.get('current_hp', '?')
            max_hp = char_data.get('max_hp', '?')
            
            print(f"\n  🏹 {name} [{char_id}] - HP: {hp}/{max_hp}")
            
            # Show resistances (from equipment/buffs)
            resistances = char_data.get('resistances', {})
            immunities = char_data.get('immunities', [])
            vulnerabilities = char_data.get('vulnerabilities', [])
            
            if resistances or immunities or vulnerabilities:
                if resistances:
                    print(f"    🛡️ Resistances: {resistances}")
                if immunities:
                    print(f"    ⚫ Immunities: {immunities}")
                if vulnerabilities:
                    print(f"    🔴 Vulnerabilities: {vulnerabilities}")
            else:
                print("    ⚪ No special resistances")
            
            # Show active buffs (AC bonuses, etc.)
            # TODO: This will be expanded when buff system is implemented
            
        # Enemy resistances
        print("\n👹 ENEMY STATUS:")
        enemy_instances = combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            if enemy.get("current_hp", 0) <= 0:
                continue
            
            name = enemy.get("name", "Enemy")
            hp = enemy.get("current_hp", 0)
            max_hp = enemy.get("stats", {}).get("hp", 1)
            instance_id = enemy.get("instance_id", "???")
            
            print(f"\n  💀 {name} [{instance_id[:4]}] - HP: {hp}/{max_hp}")
            
            # Show enemy resistances from JSON
            resistances = enemy.get("resistances", {})
            immunities = enemy.get("immunities", [])
            vulnerabilities = enemy.get("vulnerabilities", [])
            
            if resistances or immunities or vulnerabilities:
                if resistances:
                    print(f"    🛡️ Resistances: {resistances}")
                if immunities:
                    print(f"    ⚫ Immunities: {immunities}")
                if vulnerabilities:
                    print(f"    🔴 Vulnerabilities: {vulnerabilities}")
            else:
                print("    ⚪ No special resistances")
        
        print("="*60 + "\n")
    
    def _debug_out_of_combat_status(self):
        """Show status info when not in combat"""
        print("\n" + "="*50)
        print("🛡️ OUT-OF-COMBAT STATUS DEBUG")
        print("="*50)
        
        # Player status
        if hasattr(self.game_state, 'character'):
            char = self.game_state.character
            name = char.get('name', 'Player')
            hp = char.get('hp', char.get('current_hp', '?'))
            max_hp = char.get('hit_points', char.get('max_hp', '?'))
            
            print(f"🏹 {name} (Player) - HP: {hp}/{max_hp}")
            
            # TODO: Show equipment-based resistances
            # This would require checking equipped armor/trinkets
            print("    📝 Equipment resistances: [Not yet implemented]")
            
            # Show spell slots
            spell_slots = char.get('spell_slots', {})
            if spell_slots:
                print(f"    🔮 Spell Slots: {spell_slots}")
            
            # Show class abilities
            char_class = char.get('character_class', 'Unknown')
            level = char.get('level', 1)
            print(f"    ⚔️ Class: {char_class} (Level {level})")
        
        # Party member status
        if hasattr(self.game_state, 'party_members') and self.game_state.party_members:
            print(f"\n👥 PARTY MEMBERS:")
            for member_id in self.game_state.party_members:
                member_data = self.game_state.get_party_member_data(member_id)
                if member_data:
                    name = member_data.get('name', member_id)
                    hp = member_data.get('current_hp', '?')
                    max_hp = member_data.get('max_hit_points', member_data.get('hp', '?'))
                    char_class = member_data.get('character_class', 'Unknown')
                    level = member_data.get('level', 1)
                    
                    print(f"  🗡️ {name} - HP: {hp}/{max_hp} - {char_class} (Level {level})")
                    print("      📝 Equipment resistances: [Not yet implemented]")
        else:
            print(f"\n👥 PARTY MEMBERS: None recruited")
        
        print("="*50 + "\n")

    def _debug_combat_positions(self, combat_engine):
        """Display all combat unit positions with validation"""
        print("\n" + "="*60)
        print("⚔️ COMBAT POSITION DEBUG")
        print("="*60)
        
        # Get battlefield dimensions
        combat_data = combat_engine.get_combat_data_for_ui()
        battlefield = combat_data.get("battlefield", {})
        dimensions = battlefield.get("dimensions", {})
        width = dimensions.get("width", 12)
        height = dimensions.get("height", 8)
        
        print(f"📐 Battlefield: {width}x{height}")
        print(f"   Valid X: 0-{width-1}, Valid Y: 0-{height-1}")
        
        # Check party positions
        print(f"\n👥 PARTY POSITIONS:")
        character_states = combat_data.get("character_states", {})
        for char_id, char_state in character_states.items():
            if not char_state.get('is_alive', True):
                continue
            
            pos = char_state.get('position', [0, 0])
            name = char_state.get('name', char_id)
            hp = char_state.get('character_data', {}).get('current_hp', '?')
            max_hp = char_state.get('character_data', {}).get('max_hp', '?')
            
            # Validate position
            x, y = pos
            valid = (0 <= x < width) and (0 <= y < height)
            status = "✅" if valid else "❌ OUT OF BOUNDS!"
            
            # Check if on wall
            on_wall = combat_engine.movement_system._is_wall_tile(x, y, battlefield)
            if on_wall:
                status += " 🧱 ON WALL!"
            
            # Check if on obstacle
            on_obstacle = combat_engine.movement_system._is_obstacle_tile(x, y, battlefield)
            if on_obstacle:
                status += " 📦 ON OBSTACLE!"
            
            print(f"   {name} [{char_id}]: {pos} - HP: {hp}/{max_hp} {status}")
        
        # Check enemy positions
        print(f"\n👹 ENEMY POSITIONS:")
        enemy_instances = combat_data.get("enemy_instances", [])
        for enemy in enemy_instances:
            pos = enemy.get("position", [0, 0])
            name = enemy.get("name", "Enemy")
            hp = enemy.get("current_hp", 0)
            max_hp = enemy.get("stats", {}).get("hp", 1)
            instance_id = enemy.get("instance_id", "???")
            
            if hp <= 0:
                print(f"   {name} [{instance_id}]: DEAD (was at {pos})")
                continue
            
            # Validate position
            x, y = pos
            valid = (0 <= x < width) and (0 <= y < height)
            status = "✅" if valid else "❌ OUT OF BOUNDS!"
            
            # Check if on wall
            on_wall = combat_engine.movement_system._is_wall_tile(x, y, battlefield)
            if on_wall:
                status += " 🧱 ON WALL!"
            
            # Check if on obstacle
            on_obstacle = combat_engine.movement_system._is_obstacle_tile(x, y, battlefield)
            if on_obstacle:
                status += " 📦 ON OBSTACLE!"
            
            # Get AI behavior
            behavior = enemy.get("encounter_behavior") or enemy.get("behavior", {}).get("tactics", "unknown")
            
            # Calculate valid moves
            movement_range = enemy.get("movement", {}).get("speed", 3)
            valid_moves = combat_engine.movement_system.get_valid_moves(pos, movement_range, can_phase=False, is_player=False)
            
            print(f"   {name} [{instance_id[:4]}]: {pos} - HP: {hp}/{max_hp}")
            print(f"      Status: {status}")
            print(f"      AI: {behavior}")
            print(f"      Valid moves: {len(valid_moves)} tiles")
            if len(valid_moves) == 0:
                print(f"      ⚠️ TRAPPED! Cannot move!")
            elif len(valid_moves) < 3:
                print(f"      ⚠️ Limited movement: {valid_moves}")
        
        print("="*60 + "\n")

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
    
    def handle_npc_debug(self, data):
        """Handle F4 - Cycle time/day for NPC testing"""
        print("⏰ F4 - NPC Condition Debug")
        
        # Cycle through days
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_index = days.index(getattr(self.game_state, 'current_day', 'monday'))
        self.game_state.current_day = days[(current_index + 1) % len(days)]
        
        print(f"📅 Day changed to: {self.game_state.current_day.upper()}")
        print(f"🕐 Time of day: {self.game_state.time_of_day}")
        
        # Show NPC spawn info
        self._debug_npc_spawning()
       
        # """Handle F4 - Reset Kobold Mine Quest Objectives"""
        # print("🔧 F4 - Resetting Kobold Mine Quest Objectives...")
        # if hasattr(self.game_state, 'quest_manager'):
        #     quest = self.game_state.quest_manager.quests.get('kobold_mine_investigation')
        #     if quest:
        #         print("\n📋 BEFORE RESET:")
        #         for obj in quest.objectives:
        #             status = "✅" if obj.completed else "❌"
        #             print(f"  {status} {obj.id}: completed = {obj.completed}")
                
        #         # Reset the objectives
        #         for obj in quest.objectives:
        #             if obj.id in ['recover_ring', 'clear_kobolds']:
        #                 obj.completed = False
        #                 print(f"  ⚠️ Reset objective: {obj.id}")
                
        #         print("\n📋 AFTER RESET:")
        #         for obj in quest.objectives:
        #             status = "✅" if obj.completed else "❌"
        #             print(f"  {status} {obj.id}: completed = {obj.completed}")
                
        #         # Force update
        #         self.game_state.quest_manager.update_from_game_state()
        #         print("\n✅ Objectives reset - check Quest Log!")
        # else:
        #     print("⚠️ Quest manager not found!")


    
    def _debug_npc_spawning(self):
        """Debug NPC spawn conditions"""
        
        
        print("\n👥 NPC SPAWN CONDITIONS:")
        npc_mgr = get_world_npc_spawner()
        
        # Check Redstone Town NPCs
        if 'redstone_town' in npc_mgr.location_npcs:
            npcs = npc_mgr.location_npcs['redstone_town']
            active = npc_mgr.get_active_npcs('redstone_town', self.game_state)
            
            print(f"Total NPCs defined: {len(npcs)}")
            print(f"Currently spawned: {len(active)}")
            
            for npc_id, npc_data in npcs.items():
                is_active = any(n['id'] == npc_id for n in active)
                status = "✅ SPAWNED" if is_active else "❌ HIDDEN"
                conditions = npc_data.get('conditions', None)
                
                print(f"  {status} {npc_data['display_name']} ({npc_id})")
                if conditions:
                    print(f"      Conditions: {conditions}")
        print()
    
    def render_debug_overlay(self, surface, fonts):
        
        """Render on-screen debug overlay - F1 toggle"""
        if not self.debug_mode:
            return
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
        #pygame.draw.rect(surface, (0, 255, 0), 
        #                (x_pos, y_pos, overlay_width, overlay_height), 2)
        
        # Draw debug info
        self._draw_debug_lines(surface, debug_font, x_pos + 15, y_pos + 15)
    
    def _draw_debug_lines(self, surface, font, start_x, start_y):
        """Draw all debug information lines"""
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
        
        # Time and NPC info (if in town)
        if self.game_state.screen == 'redstone_town':
            lines.append(f"Day: {getattr(self.game_state, 'current_day', 'N/A').capitalize()}")
            lines.append(f"Time: {getattr(self.game_state, 'time_of_day', 'N/A').capitalize()}")
            
            # Show NPC count
            try:
                npc_mgr = get_world_npc_spawner()
                active_npcs = npc_mgr.get_active_npcs('redstone_town', self.game_state)
                lines.append(f"NPCs: {len(active_npcs)} spawned")
            except:
                pass

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
            'Refugee Camp': getattr(self.game_state, 'learned_about_refugees', False),
            'Detail Refugee': getattr(self.game_state, 'refugee_detailed_intel', False)
        }
        completed_investigations = [name for name, completed in investigations.items() if completed]
        lines.append(f"Discovered: {', '.join(completed_investigations) if completed_investigations else 'none'}")
        lines.append(f"Progress: {len(completed_investigations)}/3")
        
        # # This after the Investigation Sites section:
        # lines.append("")  # Blank line
        # lines.append("=== QUEST OBJECTIVES DEBUG ===")
        # if hasattr(self.game_state, 'quest_manager'):
        #     quest_manager = self.game_state.quest_manager
        #     for quest_id, quest in quest_manager.quests.items():
        #         if quest.status == "active":
        #             lines.append(f"{quest_id}:")
        #             for obj in quest.objectives:
        #                 status = "✅" if obj.completed else "❌"
        #                 lines.append(f"  {status} {obj.id}: {obj.description}")
        # else:
        #     lines.append("No quest manager found")

        lines.append("")
        lines.append("=== DEBUG KEYS ===")
        lines.append("[F1] Toggle Overlay")
        lines.append("[F2] Quest Debug")
        lines.append("[F3] Save Debug")
        lines.append("[F4] Cycle Day (NPC Test)")
        lines.append("[F6] Combat Positions")

        return lines
    
        
    
    def _get_navigation_debug(self):
        """Get navigation-specific debug info"""
        lines = []
        
        # Try to get current building info from navigation instance
        try:
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
        print(f"refugee_camp_details_known: {getattr(self.game_state, 'refugee_camp_details_known', False)}")
        print(f"refugee_detailed_intel: {getattr(self.game_state, 'refugee_detailed_intel', False)}")
        print(f"hill_ruins_details_known: {getattr(self.game_state, 'hill_ruins_details_known', False)}")
        print(f"swamp_church_details_known: {getattr(self.game_state, 'swamp_church_details_known', False)}")


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

        print(f"\n ⛏️ KOBOLD MINE QUEST:")
        print(f"Quest Given (Meredith): {getattr(self.game_state, 'meredith_gave_ring_quest', False)}")
        print(f"Quest Given (Henrik): {getattr(self.game_state, 'henrik_gave_shaft_quest', False)}")
        print(f"Meredith Mentioned Mine: {getattr(self.game_state, 'meredith_mentioned_old_mine', False)}")
        print(f"Henrik Mentioned Shaft: {getattr(self.game_state, 'henrik_mentioned_old_shaft', False)}")
        print(f"Cleared Kobolds: {getattr(self.game_state, 'cleared_kobold_mine', False)}")
        print(f"Ring Returned: {getattr(self.game_state, 'returned_meredith_ring', False)}")
        print(f"Ore Samples Found: {getattr(self.game_state, 'retrieved_ore_samples', False)}")
        print(f"Reported to Henrik: {getattr(self.game_state, 'reported_shaft_to_henrik', False)}")

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
    
    # ==================================================================
    # TEMPORARY REST/TIME HANDLERS - Move to TimeManager/RestManager later
    # TODO
    # ==================================================================
    
    def handle_time_advanced(self, data):
        """
        TEMPORARY: Handle TIME_ADVANCED event from dialogue/rest systems
        TODO: Move to dedicated TimeManager when implemented
        """
        hours = data.get('hours', 8)
        source = data.get('source', 'unknown')
        
        print(f"⏰ TIME_ADVANCED: {hours} hours from {source}")
        
        # Overnight rest advances to next day
        if hours >= 8:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            current_day = getattr(self.game_state, 'current_day', 'monday')
            
            try:
                current_index = days.index(current_day)
                self.game_state.current_day = days[(current_index + 1) % len(days)]
            except ValueError:
                self.game_state.current_day = 'monday'
            
            # Set time to morning after overnight rest
            self.game_state.time_of_day = 'day'
            
            print(f"💤 Day advanced → {self.game_state.current_day.upper()}, morning")
        else:
            # Future: handle partial day advancement
            print(f"⏳ Advanced {hours} hours (partial day not yet implemented)")
    
    def handle_party_rested(self, data):
        """
        TEMPORARY: Handle PARTY_RESTED event - heal party to full
        TODO: Move to dedicated RestManager/PartyManager when implemented
        """
        source = data.get('source', 'unknown')
        print(f"💤 PARTY_RESTED from {source}")
        
        # Heal all party members to full HP
        if hasattr(self.game_state, 'party_members'):
            for member_id in self.game_state.party_members:
                member_data = self.game_state.get_party_member_data(member_id)
                if member_data:
                    # Party members use: current_hp and max_hit_points
                    max_hp = member_data.get('max_hit_points', member_data.get('hp', 20))
                    member_data['current_hp'] = max_hp
                    print(f"  ❤️ {member_id} healed to {max_hp} HP")
        
        # Also heal player (uses hp and max_hp)
        if hasattr(self.game_state, 'character'):
            max_hp = self.game_state.character.get('hit_points', 20)
            self.game_state.character['current_hp'] = max_hp
            print(f"  ❤️ Player healed to {max_hp} HP")
        
        # Auto-save after resting
        if hasattr(self, 'event_manager') and hasattr(self.game_state, 'game_controller'):
            # Call save directly instead of emitting event
            controller = self.game_state.game_controller
            if hasattr(controller, 'save_manager'):
                success = controller.save_manager.save_game(0)
                if success:
                    print("💾 Auto-saved after rest (slot 0)")
                else:
                    print("⚠️ Auto-save failed after rest")