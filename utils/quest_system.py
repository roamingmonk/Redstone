# quest_system.py - Professional Quest Management for Terror in Redstone

class QuestObjective:
    """Individual quest objective with completion tracking"""
    def __init__(self, obj_id, description, completed=False):
        self.id = obj_id
        self.description = description
        self.completed = completed
        self.hidden = False  # Some objectives start hidden until prerequisites met

class Quest:
    """Complete quest with multiple objectives and state management"""
    def __init__(self, quest_id, title, description):
        self.id = quest_id
        self.title = title
        self.description = description
        self.status = "inactive"  # inactive, active, completed, failed
        self.objectives = []
        self.prerequisites_met = False
        self.completion_flags = {}  # Custom flags for complex quest logic
        
    def add_objective(self, obj_id, description, completed=False):
        """Add a new objective to this quest"""
        objective = QuestObjective(obj_id, description, completed)
        self.objectives.append(objective)
        return objective
        
    def complete_objective(self, obj_id):
        """Mark specific objective as completed"""
        for obj in self.objectives:
            if obj.id == obj_id:
                obj.completed = True
                self._check_quest_completion()
                return True
        return False
        
    def _check_quest_completion(self):
        """Check if all objectives are complete"""
        if all(obj.completed for obj in self.objectives):
            self.status = "completed"
            
    def get_progress(self):
        """Return (completed_objectives, total_objectives)"""
        completed = sum(1 for obj in self.objectives if obj.completed)
        return (completed, len(self.objectives))

class QuestManager:
    """Central quest management system for the entire game"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.quests = {}
        self.active_quest_ids = set()
        self._initialize_game_quests()
        
    def _initialize_game_quests(self):
        """Set up all quests for Terror in Redstone"""
        
        # Main storyline quest
        main_quest = Quest("main_story", "Terror in Redstone", 
                          "Investigate the mysterious disappearances plaguing Redstone")
        
        main_quest.add_objective("talk_to_npcs", "Gather information from tavern patrons")
        main_quest.add_objective("meet_mayor", "Speak with Mayor Aldwin about the crisis")
        main_quest.add_objective("recruit_party", "Recruit at least one companion")
        main_quest.add_objective("explore_ruins", "Investigate the Hill Ruins")
        main_quest.add_objective("explore_church", "Search the Swamp Church")
        main_quest.add_objective("explore_camp", "Visit the Refugee Camp")
        main_quest.add_objective("solve_mystery", "Uncover the truth behind the disappearances")
        
        self.quests["main_story"] = main_quest
        
        # Side quest examples
        recruitment_quest = Quest("party_building", "Assembling Heroes",
                                "Build a capable adventuring party")
        recruitment_quest.add_objective("recruit_warrior", "Recruit a warrior")
        recruitment_quest.add_objective("recruit_mage", "Recruit a mage")  
        recruitment_quest.add_objective("recruit_cleric", "Recruit a cleric")
        recruitment_quest.add_objective("recruit_rogue", "Recruit a rogue")
        
        self.quests["party_building"] = recruitment_quest
        
    def activate_quest(self, quest_id):
        """Activate a quest and make it trackable"""
        if quest_id in self.quests:
            self.quests[quest_id].status = "active"
            self.active_quest_ids.add(quest_id)
            return True
        return False
        
    def complete_objective(self, quest_id, objective_id):
        """Complete a specific objective"""
        if quest_id in self.quests:
            return self.quests[quest_id].complete_objective(objective_id)
        return False
        
    def update_from_game_state(self):
        """Update quest progress based on current game state flags"""
        
        # Main story progression
        main_quest = self.quests.get("main_story")
        if main_quest:
            # Information gathering phase
            if (self.game_state.meredith_talked and 
                self.game_state.garrick_talked and
                len(self.game_state.party_members) > 0):
                self.complete_objective("main_story", "talk_to_npcs")
                
            # Mayor meeting
            if self.game_state.mayor_talked:
                self.complete_objective("main_story", "meet_mayor")
                
            # Party recruitment
            if len(self.game_state.party_members) >= 1:
                self.complete_objective("main_story", "recruit_party")
                
            # Location exploration (when implemented)
            if getattr(self.game_state, 'hill_ruins_completed', False):
                self.complete_objective("main_story", "explore_ruins")
                
        # Party building quest
        party_quest = self.quests.get("party_building")
        if party_quest and self.game_state.mayor_talked:
            # Activate party building quest after meeting mayor
            if party_quest.status == "inactive":
                self.activate_quest("party_building")
                
            # Track specific recruitment types
            for member in self.game_state.party_members:
                if member == "gareth":
                    self.complete_objective("party_building", "recruit_warrior")
                elif member == "elara":
                    self.complete_objective("party_building", "recruit_mage")
                elif member == "thorman":
                    self.complete_objective("party_building", "recruit_cleric")
                elif member == "lyra":
                    self.complete_objective("party_building", "recruit_rogue")
    
    def get_active_quests(self):
        """Return list of active quests for display"""
        active_quests = []
        for quest_id in self.active_quest_ids:
            if quest_id in self.quests:
                quest = self.quests[quest_id]
                if quest.status == "active":
                    active_quests.append(quest)
        return active_quests
        
    def get_quest_data_for_save(self):
        """Return quest data in format suitable for save files"""
        save_data = {}
        for quest_id, quest in self.quests.items():
            quest_save = {
                'status': quest.status,
                'objectives': [
                    {'id': obj.id, 'completed': obj.completed} 
                    for obj in quest.objectives
                ]
            }
            save_data[quest_id] = quest_save
        return save_data
        
    def load_from_save_data(self, save_data):
        """Restore quest state from save file"""
        for quest_id, quest_save in save_data.items():
            if quest_id in self.quests:
                quest = self.quests[quest_id]
                quest.status = quest_save.get('status', 'inactive')
                
                # Restore objective completion status
                saved_objectives = {obj['id']: obj['completed'] 
                                  for obj in quest_save.get('objectives', [])}
                
                for objective in quest.objectives:
                    if objective.id in saved_objectives:
                        objective.completed = saved_objectives[objective.id]
                
                # Update active quest set
                if quest.status == "active":
                    self.active_quest_ids.add(quest_id)

# Integration with existing GameState class
def integrate_quest_system(game_state):
    """Add quest system to existing GameState"""
    if not hasattr(game_state, 'quest_manager'):
        game_state.quest_manager = QuestManager(game_state)
        
        # Activate main quest at start
        game_state.quest_manager.activate_quest("main_story")
        
        # Update quest progress based on current state
        game_state.quest_manager.update_from_game_state()

# Usage example in main game loop:
def update_quest_system(game_state):
    """Call this periodically to keep quests in sync"""
    if hasattr(game_state, 'quest_manager'):
        game_state.quest_manager.update_from_game_state()

# Quest Log UI Integration
def get_quest_log_data(game_state):
    """Return formatted data for quest log display"""
    if not hasattr(game_state, 'quest_manager'):
        return []
        
    active_quests = game_state.quest_manager.get_active_quests()
    quest_data = []
    
    for quest in active_quests:
        completed, total = quest.get_progress()
        quest_info = {
            'id': quest.id,
            'title': quest.title,
            'description': quest.description,
            'progress': f"{completed}/{total}",
            'objectives': [
                {
                    'description': obj.description,
                    'completed': obj.completed
                }
                for obj in quest.objectives if not obj.hidden
            ]
        }
        quest_data.append(quest_info)
        
    return quest_data