# NEW FILE: utils/debug_manager.py
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
        print(f"Vistory Reported to Garrick: {getattr(self.game_state, 'reported_basement_victory', False)}")
        print(f"Garrick Paid player: {getattr(self.game_state, 'garrick_paid', False)}")
        print(f"Acknowled Payment: {getattr(self.game_state, 'post_payment_acknowledged', False)}")

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