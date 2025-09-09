"""
Terror in Redstone - Quest Engine
Professional quest management system with event-driven architecture
Integrates quest_system.py with event-driven XP and progression
"""

from utils.quest_system import QuestManager, integrate_quest_system

def initialize_quest_engine(game_state, event_manager):
    """
    Initialize Quest Engine following established engine pattern
    
    Args:
        game_state: Reference to game state (Single Data Authority)
        event_manager: Event manager for quest completion notifications
        
    Returns:
        QuestEngine: Initialized quest engine instance
    """
    try:
        # Use existing quest system integration
        integrate_quest_system(game_state)
        
        # Create quest engine wrapper
        quest_engine = QuestEngine(game_state, event_manager)
        
        print("✅ QuestEngine initialized successfully")
        return quest_engine
        
    except Exception as e:
        print(f"❌ QuestEngine initialization failed: {e}")
        return None

class QuestEngine:
    """
    Professional Quest Engine with event-driven architecture
    Wraps the existing QuestManager with modern event integration
    """
    
    def __init__(self, game_state, event_manager):
        self.game_state = game_state
        self.event_manager = event_manager
        
        # Get the quest manager created by integrate_quest_system
        self.quest_manager = game_state.quest_manager
        
        # Register for dialogue events
        self.event_manager.register("DIALOGUE_QUEST_TRIGGER", self._handle_dialogue_quest_trigger)
        self.event_manager.register("PARTY_MEMBER_RECRUITED", self._handle_party_recruitment)
        self.event_manager.register("LOCATION_DISCOVERED", self._handle_location_discovery)
        
        print("🎯 QuestEngine event handlers registered")
    
    # ==========================================
    # EVENT HANDLERS - Connect to game systems
    # ==========================================
    
    def _handle_dialogue_quest_trigger(self, event_data):
        """Handle quest triggers from dialogue system"""
        quest_id = event_data.get('quest_id')
        trigger_type = event_data.get('trigger_type', 'activate')
        
        if trigger_type == 'activate':
            success = self.quest_manager.activate_quest(quest_id)
            if success:
                print(f"🎯 Quest activated: {quest_id}")
        elif trigger_type == 'complete_objective':
            objective_id = event_data.get('objective_id')
            success = self.quest_manager.complete_objective(quest_id, objective_id)
            if success:
                print(f"✅ Objective completed: {quest_id}.{objective_id}")
                self._check_quest_completion(quest_id)
    
    def _handle_party_recruitment(self, event_data):
        """Handle party member recruitment for quest progression"""
        member_id = event_data.get('member_id')
        
        # Update quest progress based on recruitment
        if member_id == "gareth":
            self.quest_manager.complete_objective("party_building", "recruit_warrior")
        elif member_id == "elara":
            self.quest_manager.complete_objective("party_building", "recruit_mage")
        elif member_id == "thorman":
            self.quest_manager.complete_objective("party_building", "recruit_cleric")
        elif member_id == "lyra":
            self.quest_manager.complete_objective("party_building", "recruit_rogue")
        
        # Check if party building quest is complete
        self._check_quest_completion("party_building")
        
        # Check if enough party members for main story
        if len(self.game_state.party_members) >= 1:
            self.quest_manager.complete_objective("main_story", "recruit_party")
            self._check_quest_completion("main_story")
    
    def _handle_location_discovery(self, event_data):
        """Handle location discovery for quest progression"""
        location = event_data.get('location')
        
        if location == "hill_ruins":
            self.quest_manager.complete_objective("main_story", "explore_ruins")
        elif location == "swamp_church":
            self.quest_manager.complete_objective("main_story", "explore_church")
        elif location == "refugee_camp":
            self.quest_manager.complete_objective("main_story", "explore_camp")
        
        self._check_quest_completion("main_story")
    
    # ==========================================
    # QUEST COMPLETION & XP INTEGRATION
    # ==========================================
    
    def _check_quest_completion(self, quest_id):
        """Check if quest is complete and award XP"""
        quest = self.quest_manager.quests.get(quest_id)
        if not quest:
            return
        
        # Check if all objectives are complete
        if quest.status == "completed":
            print(f"🎊 Quest completed: {quest.title}")
            self._award_quest_completion_xp(quest_id, quest.title)
    
    def _award_quest_completion_xp(self, quest_id, quest_title):
        """Award XP for quest completion via event system"""
        # Define XP rewards for different quest types
        xp_rewards = {
            "main_story": 1000,              # Main story milestone
            "party_building": 300,           # Party assembly
            "clear_tavern_basement": 200,    # Rat basement quest
            "investigate_hill_ruins": 400,   # Location investigation
            "explore_swamp_church": 400,     # Location investigation
            "find_refugee_camp": 400         # Location investigation
        }
        
        xp_reward = xp_rewards.get(quest_id, 150)  # Default XP
        
        # Emit quest completion event for CharacterEngine to handle
        self.event_manager.emit("QUEST_COMPLETED", {
            "quest_id": quest_id,
            "quest_title": quest_title,
            "xp_reward": xp_reward,
            "completion_type": self._get_quest_type(quest_id)
        })
        
        print(f"🏆 Quest XP awarded: {xp_reward} for {quest_title}")
    
    def _get_quest_type(self, quest_id):
        """Determine quest type for XP categorization"""
        if quest_id == "main_story":
            return "main_quest"
        elif quest_id in ["investigate_hill_ruins", "explore_swamp_church", "find_refugee_camp"]:
            return "location_quest"
        else:
            return "side_quest"
    
    # ==========================================
    # QUEST MANAGEMENT INTERFACE
    # ==========================================
    
    def get_active_quests(self):
        """Get all active quests for UI display"""
        return self.quest_manager.get_active_quests()
    
    def get_completed_quests(self):
        """Get all completed quests for UI display"""
        completed = []
        for quest in self.quest_manager.quests.values():
            if quest.status == "completed":
                completed.append(quest)
        return completed
    
    def get_quest_by_id(self, quest_id):
        """Get specific quest by ID"""
        return self.quest_manager.quests.get(quest_id)
    
    def activate_quest(self, quest_id):
        """Manually activate a quest"""
        return self.quest_manager.activate_quest(quest_id)
    
    def complete_objective(self, quest_id, objective_id):
        """Manually complete an objective"""
        success = self.quest_manager.complete_objective(quest_id, objective_id)
        if success:
            self._check_quest_completion(quest_id)
        return success
    
    # ==========================================
    # SPECIAL QUEST INTEGRATION
    # ==========================================
    
    def unlock_rat_basement_quest(self):
        """
        Unlock the tavern basement rat quest after party is assembled
        Called when party size >= 2 and player talks to Garrick
        """
        if len(self.game_state.party_members) >= 1:  # At least one party member
            # Add the rat basement quest dynamically
            from utils.quest_system import Quest
            
            if "clear_tavern_basement" not in self.quest_manager.quests:
                rat_quest = Quest("clear_tavern_basement", "Clear the Tavern Basement", 
                                "Help Garrick deal with a giant rat infestation in the basement")
                rat_quest.add_objective("enter_basement", "Enter the tavern basement")
                rat_quest.add_objective("defeat_rats", "Defeat the giant rats")
                rat_quest.add_objective("report_success", "Report success to Garrick")
                
                self.quest_manager.quests["clear_tavern_basement"] = rat_quest
                self.quest_manager.activate_quest("clear_tavern_basement")
                
                print("🐀 Rat basement quest unlocked!")
                return True
        
        return False
    
    def trigger_information_discovery(self, info_type):
        """
        Award XP for information discovery
        Called when NPCs reveal important information
        """
        discovery_xp = {
            "hill_ruins_location": 50,
            "swamp_church_location": 50,
            "refugee_camp_location": 50,
            "mayor_family_info": 25,
            "disappearance_pattern": 25
        }
        
        xp_amount = discovery_xp.get(info_type, 10)
        
        # Award discovery XP via event system
        self.event_manager.emit("INFORMATION_DISCOVERED", {
            "info_type": info_type,
            "xp_reward": xp_amount
        })
        
        print(f"🔍 Information discovered: {info_type} (+{xp_amount} XP)")
    
    # ==========================================
    # SAVE/LOAD INTEGRATION
    # ==========================================
    
    def get_save_data(self):
        """Get quest data for save files"""
        return self.quest_manager.get_quest_data_for_save()
    
    def load_save_data(self, save_data):
        """Restore quest state from save files"""
        return self.quest_manager.load_from_save_data(save_data)