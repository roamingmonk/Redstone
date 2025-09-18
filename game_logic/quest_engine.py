"""
Terror in Redstone - Quest Engine
Professional quest management system with event-driven architecture
Integrates quest_system.py with event-driven XP and progression
"""

from utils.quest_system import QuestManager, integrate_quest_system
from utils.xp_manager import XPManager
from utils.narrative_schema import narrative_schema

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
        game_state.quest_engine = quest_engine
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
        
        # Track last known status and one-shot XP guards
        self._last_status = {qid: q.status for qid, q in self.quest_manager.quests.items()}
        # If you prefer flags on GameState, you can remove this set and use gs attributes instead
        self._awarded_completion = set()

        # Register for dialogue events
        self.event_manager.register("DIALOGUE_QUEST_TRIGGER", self._handle_dialogue_quest_trigger)
        self.event_manager.register("PARTY_MEMBER_RECRUITED", self._handle_party_recruitment)
        self.event_manager.register("LOCATION_DISCOVERED", self._handle_location_discovery)
        self.event_manager.register("FLAG_CHANGED", self.on_flag_changed)
        print("[DBG] QuestEngine registered FLAG_CHANGED")
        print("🎯 QuestEngine event handlers registered")
    
    # ==========================================
    # EVENT HANDLERS - Connect to game systems
    # ==========================================
    
    def scan_for_completions(self):
            """
            Call after QuestManager.update_from_game_state().
            Detect newly-completed quests and award XP once.
            """
            for qid, quest in self.quest_manager.quests.items():
                prev = self._last_status.get(qid)
                now = quest.status
                if now == "completed" and prev != "completed":
                    # newly completed
                    self._award_quest_completion_xp(qid, quest.title)
                self._last_status[qid] = now

    def on_flag_changed(self, data):
        flag = (data or {}).get("flag")
        val  = (data or {}).get("value")
        print(f"[DBG] on_flag_changed received: {flag}={val}")
        # Evaluate only triggers referencing this flag; fall back to a sweep if none found.
        self._evaluate_quest_triggers(flag_hint=flag)
        #self._evaluate_recruitment_by_flag(flag_hint=flag)
        #TODO Do we need ro remove _evaluate_recruitment_by_flag????
        self._award_recruit_xp_for_flag(flag)

    def _award_recruit_xp_for_flag(self, flag_hint: str | None):
        """Award per-recruit XP when a '*_recruited' flag flips True, using nested schema."""
        if not flag_hint or not flag_hint.endswith("_recruited"):
            return

        from utils.narrative_schema import narrative_schema
        from utils.xp_manager import XPManager

        schema    = getattr(narrative_schema, "schema", {}) or {}
        rec_trigs = schema.get("quest_triggers", {}).get("party_recruitment_triggers", {})
        spec      = rec_trigs.get(flag_hint)
        print(f"[DBG] recruitment lookup for {flag_hint} -> {'FOUND' if isinstance(spec, dict) else 'MISSING'}")

        # Only proceed if the flag is truly True and we have a spec
        if not isinstance(spec, dict) or not getattr(self.game_state, flag_hint, False):
            return

        guard = f"xp_awarded__recruit__{flag_hint}"
        if getattr(self.game_state, guard, False):
            print(f"[DBG] guard blocked duplicate recruit award for {flag_hint}")
            return

        xp       = XPManager(narrative_schema)
        
        
        #mult_key = spec.get("xp_reward", "quest_multipliers.secondary")
        #amount   = xp.get_reward({"base": "base_quest_xp", "mult": mult_key})
        #print(f"[DBG] recruit={flag_hint} mult={mult_key} -> amount={amount}")

        xp_spec = spec.get("xp_reward", "recruitment_bonus")
        
        # Handle all forms:
        # - dict: {"base":"base_quest_xp","mult":"quest_multipliers.recruitment"} -> XPManager handles it
        # - "quest_multipliers.X": multiply base_quest_xp by that multiplier
        # - "recruitment_bonus" or "discovery_base": use the flat value directly
        if isinstance(xp_spec, dict):
            amount = xp.get_reward(xp_spec)
        elif isinstance(xp_spec, str) and xp_spec.startswith("quest_multipliers."):
            amount = xp.get_reward({"base": "base_quest_xp", "mult": xp_spec})
        else:
            amount = xp.get_reward(xp_spec)  # flat key in xp_balance (e.g., "recruitment_bonus")

        if amount > 0 and self.event_manager:
            self.event_manager.emit("XP_AWARDED", {
                "amount": amount,
                "reason": f"recruitment:{flag_hint}",
                "recipient": "party",
            })
            print(f"⭐ Recruitment XP: {amount} for {flag_hint}")

        # Progress linked objective if present (keeps objective updates even if PARTY_MEMBER_RECRUITED is missed)
        if spec.get("quest_objective"):
            self._complete_objective_from_path(spec["quest_objective"])

        setattr(self.game_state, guard, True)



    def _evaluate_quest_triggers(self, flag_hint: str | None = None):
        schema = getattr(narrative_schema, "schema", {}) or {}
        trigs  = schema.get("quest_triggers", {})  # nested root
        print(f"[DBG] quest_triggers count={len(trigs)}")

        if flag_hint:
            candidates = [(tid, spec) for tid, spec in trigs.items()
                        if isinstance(spec, dict) and spec.get("dialogue_flag") == flag_hint]
            print(f"[DBG] candidates for flag '{flag_hint}': {[tid for tid,_ in candidates]}")
            if not candidates and getattr(self.game_state, flag_hint, False):
                print("[DBG] no direct candidates; falling back to full sweep")
                candidates = [(tid, spec) for tid, spec in trigs.items() if isinstance(spec, dict)]
        else:
            candidates = [(tid, spec) for tid, spec in trigs.items() if isinstance(spec, dict)]

        xp = XPManager(narrative_schema)

        for trig_id, spec in candidates:
            dlg_flag = spec.get("dialogue_flag")
            if not dlg_flag or not getattr(self.game_state, dlg_flag, False):
                continue

            guard = f"xp_awarded__trigger__{trig_id}"
            if getattr(self.game_state, guard, False):
                continue

            reward_spec = spec.get("xp_reward", 0)
            amount = xp.get_reward(reward_spec)
            print(f"[DBG] trigger={trig_id} flag={dlg_flag} reward_spec={reward_spec} -> amount={amount}")

            if amount > 0 and self.event_manager:
                self.event_manager.emit("XP_AWARDED", {
                    "amount": amount,
                    "reason": f"{spec.get('event_type','TRIGGER')}:{dlg_flag}",  # neutral by flag
                    "recipient": "party"
                })
                print(f"⭐ Trigger XP: {amount} for {trig_id}")

            if spec.get("quest_objective"):
                self._complete_objective_from_path(spec["quest_objective"])

            # ✅ guard set INSIDE the loop
            setattr(self.game_state, guard, True)
    
        
    def _evaluate_recruitment_by_flag(self, flag_hint: str | None):
        if not flag_hint or not flag_hint.endswith("_recruited"):
            return

        schema   = getattr(narrative_schema, "schema", {}) or {}
        rec_trigs = (schema.get("party_recruitment_triggers") or {})
        spec     = rec_trigs.get(flag_hint)
        print(f"[DBG] recruitment lookup for {flag_hint} -> {'FOUND' if spec else 'MISSING'}")

        if not spec or not getattr(self.game_state, flag_hint, False):
            return

        guard = f"xp_awarded__recruit__{flag_hint}"
        if getattr(self.game_state, guard, False):
            print(f"[DBG] guard blocked duplicate recruit award for {flag_hint}")
            return

        xp = XPManager(narrative_schema)
        mult_key = spec.get("xp_reward", "quest_multipliers.secondary")
        amount   = xp.get_reward({"base": "base_quest_xp", "mult": mult_key})
        print(f"[DBG] recruit={flag_hint} mult={mult_key} -> amount={amount}")

        if amount > 0 and self.event_manager:
            self.event_manager.emit("XP_AWARDED", {
                "amount": amount,
                "reason": f"recruitment:{flag_hint}",
                "recipient": "party",
            })
            print(f"⭐ Recruitment XP: {amount} for {flag_hint}")

        # progress linked objective if provided
        obj_path = spec.get("quest_objective")
        if obj_path:
            self._complete_objective_from_path(obj_path)

        setattr(self.game_state, guard, True)


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
        """Advance party-building objectives when a member is recruited (no XP here)."""
        member_id = (event_data or {}).get('member_id') or (event_data or {}).get('member')
        if not member_id:
            return

        if member_id == "gareth":
            self.quest_manager.complete_objective("party_building", "recruit_warrior")
        elif member_id == "elara":
            self.quest_manager.complete_objective("party_building", "recruit_mage")
        elif member_id == "thorman":
            self.quest_manager.complete_objective("party_building", "recruit_cleric")
        elif member_id == "lyra":
            self.quest_manager.complete_objective("party_building", "recruit_rogue")

        self._check_quest_completion("party_building")

    
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
    
    def _evaluate_quest_triggers(self, flag_hint: str | None = None):

        schema = getattr(narrative_schema, "schema", {}) or {}
        trigs = (schema.get("quest_triggers") or {})

        # --- debug visibility ---
        print(f"[DBG] quest_triggers count={len(trigs)}")
        if flag_hint:
            print(f"[DBG] flag_hint={flag_hint}")

        # Build candidate list filtered by dialogue_flag, or sweep all if none found
        if flag_hint:
            candidates = [(tid, spec) for tid, spec in trigs.items()
                        if spec.get("dialogue_flag") == flag_hint]
            print(f"[DBG] candidates for {flag_hint}: {[tid for tid,_ in candidates]}")
            if not candidates and getattr(self.game_state, flag_hint, False):
                print("[DBG] no direct candidates; falling back to full sweep")
                candidates = list(trigs.items())
        else:
            candidates = list(trigs.items())

        xp = XPManager(narrative_schema)

        for trig_id, spec in candidates:
            dlg_flag = spec.get("dialogue_flag")
            if not dlg_flag or not getattr(self.game_state, dlg_flag, False):
                continue

            guard = f"xp_awarded__trigger__{trig_id}"
            if getattr(self.game_state, guard, False):
                continue

            reward_spec = spec.get("xp_reward", 0)
            amount = xp.get_reward(reward_spec)
            print(f"[DBG] trigger={trig_id} reward_spec={reward_spec} amount={amount}")

            if amount > 0 and self.event_manager:
                self.event_manager.emit("XP_AWARDED", {
                    "amount": amount,
                    "reason": f"{spec.get('event_type','TRIGGER')}:{dlg_flag}",
                    "recipient": "party"
                })
                print(f"⭐ Trigger XP: {amount} for {trig_id}")

            obj_path = spec.get("quest_objective")
            if obj_path:
                self._complete_objective_from_path(obj_path)

            setattr(self.game_state, guard, True)

    def _complete_objective_from_path(self, path: str):
        if not hasattr(self.game_state, "quest_manager"):
            return
        try:
            quest_id, objective_id = path.split(".", 1)
        except ValueError:
            return
        qm = self.game_state.quest_manager
        if hasattr(qm, "complete_objective"):
            qm.complete_objective(quest_id, objective_id)
        elif hasattr(qm, "set_objective_status"):
            qm.set_objective_status(quest_id, objective_id, True)

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
        """Award XP for quest completion via event system (one-shot)."""

        xp_manager = XPManager(narrative_schema)

        # Map quest IDs to XP reward keys (fallback kept sane)
        quest_to_reward_key = {
            "main_story": "quest_multipliers.main_story",
            "party_building": "quest_multipliers.secondary",
            "basement_rat_combat": "quest_multipliers.side_task",
            "investigate_hill_ruins": "quest_multipliers.investigation",
            "explore_swamp_church": "quest_multipliers.investigation",
            "find_refugee_camp": "quest_multipliers.investigation",
        }
        reward_key = quest_to_reward_key.get(quest_id, "quest_multipliers.side_task")

        # One-shot guard (persisted on GameState)
        guard_attr = f"xp_awarded__quest_completed__{quest_id}"
        if getattr(self.game_state, guard_attr, False):
            return

        # Compute base × multiplier (XPManager handles dict spec)
        xp_reward = xp_manager.get_reward({"base": "base_quest_xp", "mult": reward_key})
        if xp_reward <= 0:
            # keep going (event still useful), but log the oddity
            print(f"⚠️ No XP resolved for quest '{quest_id}' via '{reward_key}'")

        setattr(self.game_state, guard_attr, True)

        # Notify systems of the quest completion (your CharacterEngine can react)
        self.event_manager.emit("QUEST_COMPLETED", {
            "quest_id": quest_id,
            "quest_title": quest_title,
            "xp_reward": xp_reward,
            "completion_type": self._get_quest_type(quest_id),
        })

        # Optional: also emit a generic XP event if your pipeline expects it
        # self.event_manager.emit("XP_AWARDED", {
        #     "amount": xp_reward, "reason": f"quest_completed:{quest_id}", "recipient": "party"
        # })

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