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

# class QuestManager:
#     """Central quest management system for the entire game"""
#     def __init__(self, game_state):
#         self.game_state = game_state
#         self.quests = {}
#         self.active_quest_ids = set()
#         self._initialize_game_quests()
        
#     def _initialize_game_quests(self):
#         """Initialize quests from narrative schema"""
#         from utils.narrative_schema import narrative_schema
        
#         quest_mappings = narrative_schema.schema.get("quest_mappings", {})
        
#         for quest_id, quest_data in quest_mappings.items():
#             # Create quest from schema
#             quest_type = quest_data.get("type", "secondary")
            
#             # Get quest metadata (we'll need to add this to schema)
#             title = self._get_quest_title(quest_id)
#             description = self._get_quest_description(quest_id)
            
#             quest = Quest(quest_id, title, description)
            
#             # Add objectives from schema
#             objectives = quest_data.get("objectives", {})
#             for obj_id, required_flags in objectives.items():
#                 obj_description = self._get_objective_description(obj_id)
#                 quest.add_objective(obj_id, obj_description)
            
#             self.quests[quest_id] = quest
            
#             # Auto-activate primary quests
#             if quest_type == "primary":
#                 self.activate_quest(quest_id)
        
#         print(f"📋 Schema-driven quest system initialized with {len(self.quests)} quests")
        
#     def activate_quest(self, quest_id):
#         """Activate a quest and make it trackable"""
#         if quest_id in self.quests:
#             self.quests[quest_id].status = "active"
#             self.active_quest_ids.add(quest_id)
#             return True
#         return False
        
#     def complete_objective(self, quest_id, objective_id):
#         """Complete a specific objective"""
#         if quest_id in self.quests:
#             return self.quests[quest_id].complete_objective(objective_id)
#         return False
        
#     def update_from_game_state(self):
#         """Update quest progress based on narrative schema"""
#         from utils.narrative_schema import narrative_schema
        
#         quest_mappings = narrative_schema.schema.get("quest_mappings", {})
        
#         for quest_id, quest_data in quest_mappings.items():
#             quest = self.quests.get(quest_id)
#             if not quest:
#                 continue
                
#             # Handle quest activation
#             activation_flag = quest_data.get("activation_flag")
#             if activation_flag and getattr(self.game_state, activation_flag, False):
#                 if quest.status == "inactive":
#                     self.activate_quest(quest_id)
            
#             # Update objectives
#             objectives = quest_data.get("objectives", {})
#             for obj_id, required_flags in objectives.items():
#                 if isinstance(required_flags, list):
#                     # Check if all required flags are true
#                     all_flags_true = all(getattr(self.game_state, flag, False) for flag in required_flags)
#                     if all_flags_true:
#                         self.complete_objective(quest_id, obj_id)

#     def get_active_quests(self):
#         """Return list of active quests for display"""
#         active_quests = []
#         for quest_id in self.active_quest_ids:
#             if quest_id in self.quests:
#                 quest = self.quests[quest_id]
#                 if quest.status == "active":
#                     active_quests.append(quest)
#         return active_quests
        
#     def get_quest_data_for_save(self):
#         """Return quest data in format suitable for save files"""
#         save_data = {}
#         for quest_id, quest in self.quests.items():
#             quest_save = {
#                 'status': quest.status,
#                 'objectives': [
#                     {'id': obj.id, 'completed': obj.completed} 
#                     for obj in quest.objectives
#                 ]
#             }
#             save_data[quest_id] = quest_save
#         return save_data
        
#     def load_from_save_data(self, save_data):
#         """Restore quest state from save file"""
#         for quest_id, quest_save in save_data.items():
#             if quest_id in self.quests:
#                 quest = self.quests[quest_id]
#                 quest.status = quest_save.get('status', 'inactive')
                
#                 # Restore objective completion status
#                 saved_objectives = {obj['id']: obj['completed'] 
#                                   for obj in quest_save.get('objectives', [])}
                
#                 for objective in quest.objectives:
#                     if objective.id in saved_objectives:
#                         objective.completed = saved_objectives[objective.id]
                
#                 # Update active quest set
#                 if quest.status == "active":
#                     self.active_quest_ids.add(quest_id)

#     def get_completed_objectives(self):
#             """Get all completed objectives from all quests for display"""
#             completed_objectives = []
            
#             for quest in self.quests.values():
#                 for objective in quest.objectives:
#                     if objective.completed:
#                         completed_obj = {
#                             'id': f"{quest.id}.{objective.id}",
#                             'title': objective.description,
#                             'quest_title': quest.title,
#                             'completed': True,
#                             'quest_type': 'discovery' if 'learn_' in objective.id or 'discover_' in objective.id else 'main'
#                         }
#                         completed_objectives.append(completed_obj)
            
#             return completed_objectives
        
# ###### New Quest system methods ############
#     def get_completed_quests(self):
#         """Return list of completed quests for display"""
#         completed_quests = []
#         for quest in self.quests.values():
#             if quest.status == "completed":
#                 completed_quests.append(quest)
#         return completed_quests
    
#     def is_quest_complete(self, quest_id):
#         """Check if a specific quest is completed"""
#         quest = self.quests.get(quest_id)
#         return quest.status == "completed" if quest else False
    
#     def get_quest_progress(self, quest_id):
#         """Get progress for a specific quest"""
#         quest = self.quests.get(quest_id)
#         if quest:
#             completed, total = quest.get_progress()
#             return {
#                 'completed_objectives': completed,
#                 'total_objectives': total,
#                 'progress_percent': int((completed / total) * 100) if total > 0 else 0
#             }
#         return None
    
#     def add_dynamic_quest(self, quest_id, title, description):
#         """Add a quest dynamically (for special unlocks like rat basement)"""
#         if quest_id not in self.quests:
#             new_quest = Quest(quest_id, title, description)
#             self.quests[quest_id] = new_quest
#             print(f"➕ Dynamic quest added: {title}")
#             return new_quest
#         return None

class QuestManager:
    """Schema-driven quest management system"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.quests = {}
        self.active_quest_ids = set()
        self._initialize_schema_driven_quests()
        
    def _initialize_schema_driven_quests(self):
        """Initialize all quests from narrative schema"""
        from utils.narrative_schema import narrative_schema
        
        # Get quest definitions and mappings from schema
        quest_definitions = narrative_schema.schema.get("quest_definitions", {})
        quest_mappings = narrative_schema.schema.get("quest_mappings", {})
        objective_descriptions = narrative_schema.schema.get("objective_descriptions", {})
        
        # Create quests based on schema
        for quest_id, quest_mapping in quest_mappings.items():
            # Get quest metadata from definitions
            quest_def = quest_definitions.get(quest_id, {})
            title = quest_def.get("title", quest_id.replace("_", " ").title())
            description = quest_def.get("description", f"Quest: {title}")
            quest_type = quest_mapping.get("type", "secondary")
            
            # Create quest object
            quest = Quest(quest_id, title, description)
            
            # Add objectives from mappings
            objectives = quest_mapping.get("objectives", {})
            for obj_id, required_flags in objectives.items():
                obj_description = objective_descriptions.get(obj_id, obj_id.replace("_", " ").title())
                quest.add_objective(obj_id, obj_description)
            
            self.quests[quest_id] = quest
            
            # Auto-activate primary quests
            if quest_type == "primary":
                self.activate_quest(quest_id)
        
        print(f"📋 Schema-driven quest system initialized with {len(self.quests)} quests")
        for quest_id, quest in self.quests.items():
            status = "ACTIVE" if quest.status == "active" else "INACTIVE"
            print(f"  📌 {quest.title} [{status}] - {len(quest.objectives)} objectives")
    
    def activate_quest(self, quest_id):
        """Activate a quest and make it trackable"""
        if quest_id in self.quests:
            self.quests[quest_id].status = "active"
            self.active_quest_ids.add(quest_id)
            print(f"🎯 Quest activated: {self.quests[quest_id].title}")
            return True
        print(f"⚠️ Cannot activate unknown quest: {quest_id}")
        return False
        
    def complete_objective(self, quest_id, objective_id):
        """Complete a specific objective"""
        if quest_id in self.quests:
            result = self.quests[quest_id].complete_objective(objective_id)
            #if result:
                #print(f"✅ Objective completed: {quest_id}.{objective_id}")
            #return result
        return False
    
    def update_from_game_state(self):
        """Update quest progress based on narrative schema"""
        from utils.narrative_schema import narrative_schema
        
        quest_mappings = narrative_schema.schema.get("quest_mappings", {})
        
        for quest_id, quest_data in quest_mappings.items():
            quest = self.quests.get(quest_id)
            if not quest:
                continue
                
            # Handle quest activation based on activation_flag
            activation_flag = quest_data.get("activation_flag")
            if activation_flag and getattr(self.game_state, activation_flag, False):
                if quest.status == "inactive":
                    self.activate_quest(quest_id)
            
            # Update objectives based on flag requirements
            objectives = quest_data.get("objectives", {})
            for obj_id, required_flags in objectives.items():
                if isinstance(required_flags, list):
                    # Check if all required flags are true
                    all_flags_true = all(getattr(self.game_state, flag, False) for flag in required_flags)
                    if all_flags_true:
                        self.complete_objective(quest_id, obj_id)
                elif isinstance(required_flags, str):
                    # Handle complex conditions like "recruited_count >= 1"
                    if self._evaluate_condition(required_flags):
                        self.complete_objective(quest_id, obj_id)
    
    def _evaluate_condition(self, condition):
        """Evaluate complex condition strings like 'recruited_count >= 1'"""
        try:
            # Handle recruitment count condition
            if "recruited_count >= " in condition:
                required_count = int(condition.split(">=")[1].strip())
                current_count = getattr(self.game_state, 'recruited_count', 0)
                return current_count >= required_count
            
            # Handle other dynamic conditions here as needed
            # For now, treat unknown conditions as False
            print(f"⚠️ Unknown condition format: {condition}")
            return False
            
        except Exception as e:
            print(f"⚠️ Error evaluating condition '{condition}': {e}")
            return False
    
    def get_active_quests(self):
        """Return list of active quests for display"""
        active_quests = []
        for quest_id in self.active_quest_ids:
            if quest_id in self.quests:
                quest = self.quests[quest_id]
                if quest.status == "active":
                    active_quests.append(quest)
        return active_quests
    
    def get_completed_quests(self):
        """Return list of completed quests"""
        completed_quests = []
        for quest in self.quests.values():
            if quest.status == "completed":
                completed_quests.append(quest)
        return completed_quests
    
    def get_completed_objectives(self):
        """Get all completed objectives from all quests for display"""
        completed_objectives = []
        
        for quest in self.quests.values():
            for objective in quest.objectives:
                if objective.completed:
                    completed_obj = {
                        'id': f"{quest.id}.{objective.id}",
                        'title': objective.description,
                        'quest_title': quest.title,
                        'completed': True,
                        'quest_type': 'discovery' if 'learn_' in objective.id or 'discover_' in objective.id else 'main'
                    }
                    completed_objectives.append(completed_obj)
        
        return completed_objectives
                
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
                    
    def debug_quest_objectives(self):
        """Debug method to see what objectives exist and their status"""
        print("=== SCHEMA-DRIVEN QUEST OBJECTIVES DEBUG ===")
        for quest_id, quest in self.quests.items():
            print(f"Quest: {quest_id} ({quest.status})")
            for obj in quest.objectives:
                status = "✅" if obj.completed else "❌"
                print(f"  {status} {obj.id}: {obj.description}")
        print("==============================================")

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