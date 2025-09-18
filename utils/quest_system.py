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
        # Special case for party_building: complete when party_ready is done
        if self.id == "party_building":
            party_ready_obj = next((obj for obj in self.objectives if obj.id == "party_ready"), None)
            if party_ready_obj and party_ready_obj.completed:
                self.status = "completed"
                return
        
        # Default: all objectives must be complete
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
        """Set up all quests for Terror in Redstone with enhanced quest structure"""
        
        # PRIMARY QUEST: Main storyline
        main_quest = Quest("main_story", "Terror in Redstone", 
                          "Investigate the mysterious disappearances plaguing Redstone")
        
        main_quest.add_objective("talk_to_npcs", "Gather information from tavern patrons")
        main_quest.add_objective("meet_mayor", "Speak with Mayor Aldwin about the crisis")
        main_quest.add_objective("recruit_party", "Recruit at least one companion")
        main_quest.add_objective("discover_locations", "Learn about all three investigation sites")
        main_quest.add_objective("investigate_locations", "Investigate the three key locations")
        main_quest.add_objective("solve_mystery", "Uncover the truth behind the disappearances")
        
        self.quests["main_story"] = main_quest
        
        # SECONDARY QUEST: Party Building  
        recruitment_quest = Quest("party_building", "Assemble Your Party",
                                "Build a capable adventuring party for dangerous missions")
        recruitment_quest.add_objective("recruit_warrior", "Recruit a warrior (Gareth)")
        recruitment_quest.add_objective("recruit_mage", "Recruit a mage (Elara)")  
        recruitment_quest.add_objective("recruit_cleric", "Recruit a cleric (Thorman)")
        recruitment_quest.add_objective("recruit_rogue", "Recruit a rogue (Lyra)")
        recruitment_quest.add_objective("party_ready", "Assemble a full party (3 members)")
        
        self.quests["party_building"] = recruitment_quest
        
        # SECONDARY QUEST: Location Investigations
        hill_ruins_quest = Quest("investigate_hill_ruins", "Investigate the Hill Ruins",
                               "Explore the ancient mining ruins north of town")
        hill_ruins_quest.add_objective("learn_location", "Learn about the Hill Ruins from Garrick")
        hill_ruins_quest.add_objective("travel_to_ruins", "Travel to the Hill Ruins")
        hill_ruins_quest.add_objective("explore_ruins", "Search the ruins for clues")
        hill_ruins_quest.add_objective("find_evidence", "Discover what happened here")
        
        self.quests["investigate_hill_ruins"] = hill_ruins_quest
        
        swamp_church_quest = Quest("explore_swamp_church", "Explore the Swamp Church", 
                                 "Investigate the old shrine in the wetlands")
        swamp_church_quest.add_objective("learn_location", "Learn about the Swamp Church from Meredith")
        swamp_church_quest.add_objective("travel_to_church", "Travel to the Swamp Church")
        swamp_church_quest.add_objective("explore_church", "Search the church for clues")
        swamp_church_quest.add_objective("find_evidence", "Discover what happened here")
        
        self.quests["explore_swamp_church"] = swamp_church_quest
        
        refugee_camp_quest = Quest("find_refugee_camp", "Find the Refugee Camp",
                                 "Locate and investigate the refugee settlement")
        refugee_camp_quest.add_objective("learn_location", "Learn about the refugees from the Mayor")
        refugee_camp_quest.add_objective("travel_to_camp", "Travel to the Refugee Camp")
        refugee_camp_quest.add_objective("talk_to_refugees", "Speak with the refugee leaders")
        refugee_camp_quest.add_objective("gather_information", "Learn what the refugees witnessed")
        
        self.quests["find_refugee_camp"] = refugee_camp_quest
        
        # SECONDARY QUEST: Rat Basement Combat (Garrick's side quest)
        rat_quest = Quest("basement_rat_combat", "Clear the Basement", 
                         "Help Garrick eliminate the rats infesting his tavern basement")
        rat_quest.add_objective("accept_challenge", "Accept Garrick's basement clearing job")
        rat_quest.add_objective("clear_basement", "Defeat all rats in the basement")
        rat_quest.add_objective("report_victory", "Report success to Garrick")
        rat_quest.add_objective("collect_payment", "Collect payment from Garrick")
        
        self.quests["basement_rat_combat"] = rat_quest
        
        print("🎯 Enhanced quest system initialized with 6 quests")
        print("📋 Primary: Terror in Redstone (main story)")
        print("📋 Secondary: Party Building, Hill Ruins, Swamp Church, Refugee Camp, Rat Basement")
        
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
        # Main story quest progress
        main_quest = self.quests.get("main_story")
        if main_quest:
            # Information gathering phase
            if (getattr(self.game_state, 'meredith_talked', False) and 
                getattr(self.game_state, 'garrick_talked', False)):
                self.complete_objective("main_story", "talk_to_npcs")
                
            # Mayor meeting
            if getattr(self.game_state, 'mayor_talked', False):
                self.complete_objective("main_story", "meet_mayor")
                
            # Party recruitment - USE RECRUITMENT FLAGS, not party_members list
            recruitment_count = self.game_state.recruited_count if hasattr(self.game_state, 'recruited_count') else 0
            if recruitment_count >= 1:
                self.complete_objective("main_story", "recruit_party")
            
            # Location discovery progress
            locations_discovered = 0
            if getattr(self.game_state, 'learned_about_swamp_church', False):
                locations_discovered += 1
            if getattr(self.game_state, 'learned_about_ruins', False):
                locations_discovered += 1
            if getattr(self.game_state, 'learned_about_refugees', False):
                locations_discovered += 1
            
            if locations_discovered >= 3:
                self.complete_objective("main_story", "discover_locations")
                
            # Location exploration (when implemented)
            if getattr(self.game_state, 'hill_ruins_completed', False):
                self.complete_objective("main_story", "explore_ruins")
                
        # Party building quest - FIX: Use individual recruitment flags
        party_quest = self.quests.get("party_building")
        if party_quest:
            # Activate party building quest after meeting mayor
            if getattr(self.game_state, 'mayor_talked', False) and party_quest.status == "inactive":
                self.activate_quest("party_building")
                print("🎯 Activated party_building quest")
                
            # Track specific recruitment types using FLAGS, not party_members
            if getattr(self.game_state, 'gareth_recruited', False):
                self.complete_objective("party_building", "recruit_warrior")
            if getattr(self.game_state, 'elara_recruited', False):
                self.complete_objective("party_building", "recruit_mage")
            if getattr(self.game_state, 'thorman_recruited', False):
                self.complete_objective("party_building", "recruit_cleric")
            if getattr(self.game_state, 'lyra_recruited', False):
                self.complete_objective("party_building", "recruit_rogue")
    
            # Complete party building when we have 3 recruits (full party)
            if recruitment_count >= 3:
                print(f"🎯 Completing party_ready objective (recruited_count: {recruitment_count})")
                party_quest = self.quests.get("party_building")
                if party_quest:
                    print(f"📋 Party quest objectives: {[obj.id for obj in party_quest.objectives]}")
                result = self.complete_objective("party_building", "party_ready")
                print(f"📝 Complete objective result: {result}")


        # Rat basement quest progression
        rat_quest = self.quests.get("basement_rat_combat")
        if rat_quest and getattr(self.game_state, 'garrick_offered_basement', False):
            # Activate quest when offered
            if rat_quest.status == "inactive":
                self.activate_quest("basement_rat_combat")
            
            # Update objectives based on current flags
            if getattr(self.game_state, 'accepted_basement_quest', False):
                self.complete_objective("basement_rat_combat", "accept_challenge")
            if getattr(self.game_state, 'completed_basement_combat', False):
                self.complete_objective("basement_rat_combat", "clear_basement")
            if getattr(self.game_state, 'reported_basement_victory', False):
                self.complete_objective("basement_rat_combat", "report_victory")
            if getattr(self.game_state, 'garrick_paid', False):
                self.complete_objective("basement_rat_combat", "collect_payment")

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

###### New Quest system methods ############
    def get_completed_quests(self):
        """Return list of completed quests for display"""
        completed_quests = []
        for quest in self.quests.values():
            if quest.status == "completed":
                completed_quests.append(quest)
        return completed_quests
    
    def is_quest_complete(self, quest_id):
        """Check if a specific quest is completed"""
        quest = self.quests.get(quest_id)
        return quest.status == "completed" if quest else False
    
    def get_quest_progress(self, quest_id):
        """Get progress for a specific quest"""
        quest = self.quests.get(quest_id)
        if quest:
            completed, total = quest.get_progress()
            return {
                'completed_objectives': completed,
                'total_objectives': total,
                'progress_percent': int((completed / total) * 100) if total > 0 else 0
            }
        return None
    
    def add_dynamic_quest(self, quest_id, title, description):
        """Add a quest dynamically (for special unlocks like rat basement)"""
        if quest_id not in self.quests:
            new_quest = Quest(quest_id, title, description)
            self.quests[quest_id] = new_quest
            print(f"➕ Dynamic quest added: {title}")
            return new_quest
        return None

###### New Quest system methods ############

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
       #let QuestEngine notice transitions to 'completed'
        if getattr(game_state, "quest_engine", None):
            game_state.quest_engine.scan_for_completions()

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
            'progress': "COMPLETE" if quest.status == "completed" else f"{completed}/{total}",
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