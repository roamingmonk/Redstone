# game_logic/character_engine.py
"""
Character Management Engine - Pure Single Data Authority Pattern
GameState = THE authoritative data source
CharacterEngine = Pure business logic processor
"""

import random
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from utils.narrative_schema import narrative_schema

class CharacterEngine:
    """
    Centralized character management following Single Data Authority pattern
    
    This engine handles ALL character-related business logic:
    - Stat rolling with reroll-ones mechanism
    - Hit point calculation
    - Character class management (fighter, future classes)
    - Level progression system
    - Stat validation and modification
    
    GameState remains THE single source of truth for all data.
    """
    
    def __init__(self, game_state_ref):
        self.game_state = game_state_ref
        self.event_manager = None
        #print("🏗️ CharacterEngine initialized with Single Data Authority pattern")

        # cache just once
        xp_cfg = (getattr(narrative_schema, "schema", {}) or {}).get("xp_balance", {}) or {}
        self._level_requirements = (xp_cfg.get("level_progression", {}) or {}).get(
            "requirements", [0, 300, 900, 2700, 6500]
        )

    # ==========================================
    # CHARACTER CREATION OPERATIONS
    # ==========================================
    def _handle_new_game(self, event_data):
        """Handle starting character creation flow"""
        print("🎮 CharacterEngine: Starting character creation")
        self.activate_character_portrait(self.game_state)
        
        # Emit navigation to first character creation screen
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'stats'})
    
    def set_event_manager(self, event_manager):
        """Set event manager reference and register for XP events"""
        self.event_manager = event_manager
        
        # Register for XP award events
        if event_manager:
            event_manager.register("XP_AWARDED", self._handle_xp_award)
            event_manager.register("QUEST_COMPLETED", self._handle_quest_xp)
            print("📡 CharacterEngine registered for XP events")

    def roll_stats(self, reroll_ones=True):
        """
        Roll character stats with optional reroll-ones mechanism
        Updates GameState character stats directly
        
        Args:
            reroll_ones: If True, reroll any 1s rolled on dice
            
        Returns:
            dict: The rolled stats
        """
        stats = {}
        stat_names = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        
        for stat in stat_names:
            # Roll 3d6 for each stat
            rolls = []
            for _ in range(3):
                roll = random.randint(1, 6)
                # Reroll 1s if enabled (your proven mechanic)
                if reroll_ones and roll == 1:
                    roll = random.randint(1, 6)
                rolls.append(roll)
            
            stats[stat] = sum(rolls)
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character.update(stats)
        
        print(f"🎲 Character stats rolled: {stats}")
        return stats

    def _handle_reroll_stats(self, event_data):
        """Event wrapper for roll_stats - just adds logging"""
        print("🎲 CharacterEngine: REROLL_STATS event received")
        self.roll_stats(reroll_ones=True)  # Use existing method!
        self.game_state.stats_rolled = True

    def _handle_keep_stats(self, event_data):
        """Handle KEEP_STATS - finalize and navigate"""
        print("✅ CharacterEngine: KEEP_STATS event received")
        # Emit navigation event
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'gender'})

    def register_character_creation_events(self, event_manager):
        """Register this engine for all character creation events"""
        self.event_manager = event_manager
        
        # Game flow events
        event_manager.register('NEW_GAME', self._handle_new_game)
        
        # Stat events 
        event_manager.register('REROLL_STATS', self._handle_reroll_stats)
        event_manager.register('KEEP_STATS', self.handle_keep_stats)
        # In register_character_creation_events():
        event_manager.register('REROLL_FROM_CONFIRM', self.handle_reroll_from_confirm)
        event_manager.register('PROCEED_WITH_LOW_STATS', self.handle_proceed_with_low_stats)
        event_manager.register('ADVANCE_FROM_SNARKY', self.handle_advance_from_snarky)
        
        # Gender events 
        event_manager.register('SELECT_MALE', self._handle_select_male)
        event_manager.register('SELECT_FEMALE', self._handle_select_female)
        
        # Name selection events
        event_manager.register('SELECT_NAME_1', self._handle_select_name)
        event_manager.register('SELECT_NAME_2', self._handle_select_name)
        event_manager.register('SELECT_NAME_3', self._handle_select_name)
        event_manager.register('REROLL_NAMES', self._handle_reroll_names)
        event_manager.register('CUSTOM_NAME', self._handle_custom_name)
        
        # Custom name events
        event_manager.register('CONFIRM_CUSTOM_NAME', self._handle_confirm_custom_name)
        event_manager.register('BACK_TO_NAME', self._handle_back_to_name)
        event_manager.register('ACTIVATE_TEXT_INPUT', self._handle_activate_text_input)

        # Text input events
        event_manager.register('TEXT_INPUT', self._handle_text_input)
        event_manager.register('TEXT_BACKSPACE', self._handle_text_backspace)

        # Name confirm events
        event_manager.register('ACCEPT_NAME', self._handle_accept_name)
        event_manager.register('BACK_TO_NAME_SELECTION', self._handle_back_to_name_selection)

        # Portrait selection events
        event_manager.register('SELECT_PORTRAIT_1', self._handle_select_portrait)
        event_manager.register('SELECT_PORTRAIT_2', self._handle_select_portrait)
        event_manager.register('SELECT_PORTRAIT_3', self._handle_select_portrait)
        event_manager.register('SELECT_PORTRAIT_4', self._handle_select_portrait)
        event_manager.register('SELECT_PORTRAIT_5', self._handle_select_portrait)
        event_manager.register('CONFIRM_PORTRAIT', self._handle_confirm_portrait)
        event_manager.register('BACK_FROM_PORTRAIT', self._handle_back_from_portrait)

        #Gold selection events
        event_manager.register("GOLD_BUTTON_CLICK", self.handle_gold_button_click)

        # Trinket screen events
        event_manager.register('TRINKET_BUTTON_CLICK', self.handle_trinket_button_click)

        # Summary screen events
        event_manager.register('START_GAME', self.handle_start_game)

        print("🎯 CharacterEngine registered for all character creation events")

    def register_quest_events(self, event_manager):
        """Register for quest completion events - matches character creation pattern"""
        self.event_manager = event_manager  # Store reference
        
        event_manager.register("QUEST_COMPLETED", self._handle_quest_completion)
        event_manager.register("INFORMATION_DISCOVERED", self._handle_information_discovery)
        print("🎯 CharacterEngine registered for quest events")

    def handle_advance_from_snarky(self, event_data):
        """Handle click to advance from snarky comment"""
        self.game_state.temp_data = {}  # Clear temp data
        self.event_manager.emit("SCREEN_CHANGE", {"target": "gender"})

    def _handle_select_male(self, event_data):
        """Handle SELECT_MALE - set gender and navigate to name selection"""
        print("🚹 CharacterEngine: SELECT_MALE event received")
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['gender'] = 'male'
        
        # Generate name options using our new method
        self.generate_name_options('male')
        
        # Emit navigation event to name selection screen (CORRECTED!)
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'name'})

    def _handle_select_female(self, event_data):
        """Handle SELECT_FEMALE - set gender and navigate to name selection"""
        print("🚺 CharacterEngine: SELECT_FEMALE event received")
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['gender'] = 'female'
        
        # Generate name options using our new method
        self.generate_name_options('female')
        
        # Emit navigation event to name selection screen (CORRECTED!)
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'name'})

    def _handle_reroll_names(self, event_data):
        """Handle rerolling name options"""
        print("🎲 CharacterEngine: REROLL_NAMES event received")
        
        gender = self.game_state.character.get('gender', 'male')
        self.generate_name_options(gender)
        # Stay on same screen - just regenerate the names

    def _handle_select_name(self, event_data):
        """Handle name selection from generated options"""
        print("✨ CharacterEngine: Name selection event received")
        
        # Extract which name was selected (SELECT_NAME_1 -> index 0, etc.)
        event_type = event_data.get('action', 'SELECT_NAME_1')
        name_index = int(event_type.split('_')[-1]) - 1
        
        current_names = getattr(self.game_state, 'current_names', [])
        if 0 <= name_index < len(current_names):
            selected_name = current_names[name_index]
            self.game_state.selected_name = selected_name
            self.game_state.character['name'] = selected_name
            print(f"✅ Selected name #{name_index + 1}: {selected_name}")
            
            # FIXED: Navigate to name confirmation screen
            if self.event_manager:
                self.event_manager.emit('SCREEN_CHANGE', {'target': 'name_confirm'})
        else:
            print(f"❌ Invalid name selection index {name_index}")

    def _handle_custom_name(self, event_data):
        """Handle custom name entry request"""
        print("✏️ CharacterEngine: Custom name requested")
        
        # Navigate to custom name entry screen
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'custom_name'})

    def _handle_text_input(self, event_data):
        """Handle TEXT_INPUT - add character to custom name"""
        character = event_data.get('character', '')
        
        if not hasattr(self.game_state, 'custom_name_text'):
            self.game_state.custom_name_text = ''
        
        if character and len(self.game_state.custom_name_text) < 30:
            self.game_state.custom_name_text += character
            print(f"📝 CharacterEngine: Added '{character}' to name: '{self.game_state.custom_name_text}'")

    def _handle_text_backspace(self, event_data):
        """Handle TEXT_BACKSPACE - remove character from custom name"""
        if hasattr(self.game_state, 'custom_name_text') and self.game_state.custom_name_text:
            self.game_state.custom_name_text = self.game_state.custom_name_text[:-1]
            print(f"📝 CharacterEngine: Backspace - name now: '{self.game_state.custom_name_text}'")

    def _handle_confirm_custom_name(self, event_data):
        """Handle CONFIRM_CUSTOM_NAME - validate and proceed"""
        print("✅ CharacterEngine: CONFIRM_CUSTOM_NAME event received")
        
        text = getattr(self.game_state, 'custom_name_text', '').strip()
        if text:
            self.game_state.selected_name = text
            self.game_state.character['name'] = text
            self.game_state.custom_name_active = False  # Disable text input mode
            print(f"✅ Custom name confirmed: {text}")
            
            # Navigate to name confirmation
            if self.event_manager:
                self.event_manager.emit('SCREEN_CHANGE', {'target': 'name_confirm'})
        else:
            print("❌ No custom name text to confirm")

    def _handle_back_to_name(self, event_data):
        """Handle BACK_TO_NAME - return to name selection and clear custom text"""
        print("⬅️ CharacterEngine: BACK_TO_NAME event received")
        
        # Clear custom name text for fresh start
        if hasattr(self.game_state, 'custom_name_text'):
            self.game_state.custom_name_text = ""
        
        # Disable text input mode
        if hasattr(self.game_state, 'custom_name_active'):
            self.game_state.custom_name_active = False
        
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'name'})

    def _handle_activate_text_input(self, event_data):
        """Handle ACTIVATE_TEXT_INPUT - enable custom name input"""
        print("📝 CharacterEngine: ACTIVATE_TEXT_INPUT event received")
        
        # Activate text input mode
        self.game_state.custom_name_active = True
        if not hasattr(self.game_state, 'custom_name_text'):
            self.game_state.custom_name_text = ""

    def _handle_accept_name(self, event_data):
        """Handle ACCEPT_NAME - finalize name and proceed to portrait selection"""
        print("🎉 CharacterEngine: ACCEPT_NAME event received")
        
        if hasattr(self.game_state, 'selected_name'):
            self.game_state.character['name'] = self.game_state.selected_name
            print(f"🎉 Final name accepted: {self.game_state.selected_name}")
            
            # Navigate to portrait selection
            if self.event_manager:
                self.event_manager.emit('SCREEN_CHANGE', {'target': 'portrait_selection'})
        else:
            print("❌ No selected name to accept")

    def _handle_back_to_name_selection(self, event_data):
        """Handle BACK_TO_NAME_SELECTION - return to name selection from confirmation"""
        print("⬅️ CharacterEngine: BACK_TO_NAME_SELECTION event received")
        
        # Clear custom name text for fresh start (same as back from custom name screen)
        if hasattr(self.game_state, 'custom_name_text'):
            self.game_state.custom_name_text = ""
        
        # Disable text input mode
        if hasattr(self.game_state, 'custom_name_active'):
            self.game_state.custom_name_active = False
        
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'name'})

    def _handle_select_portrait(self, event_data):
        """Handle portrait selection from grid"""
        print("🖼️ CharacterEngine: Portrait selection event received")
        
        # Extract portrait index from action (SELECT_PORTRAIT_1 -> index 0, etc.)
        action = event_data.get('action', '')
        if action.startswith('SELECT_PORTRAIT_'):
            # Convert 1-5 to 0-4 for internal indexing
            portrait_index = int(action.split('_')[-1]) - 1
            
            # Get current gender
            gender = self.game_state.character.get('gender', 'male')
            
            # Store the selected portrait index for UI highlighting (0-4)
            self.game_state.selected_portrait_index = portrait_index
            
            # Use existing GameState method (Single Data Authority)
            self.game_state.set_selected_portrait(gender, portrait_index)
            
            print(f"🎭 Portrait {portrait_index + 1} selected for {gender} (internal index: {portrait_index})")

    def _handle_confirm_portrait(self, event_data):
        """Handle CONFIRM_PORTRAIT - finalize selection and navigate to gold screen"""
        print("✅ CharacterEngine: CONFIRM_PORTRAIT event received")
        
        if hasattr(self.game_state, 'selected_portrait_index') and self.game_state.selected_portrait_index is not None:
            print(f"🎉 Portrait selection confirmed: {self.game_state.selected_portrait_index + 1}")
            
            # Copy selected portrait to active location
            self.ensure_active_portrait(self.game_state)

            # Navigate to next step (gold screen)
            if self.event_manager:
                self.event_manager.emit('SCREEN_CHANGE', {'target': 'gold'})
        else:
            print("⚠️ No portrait selected to confirm")

    def _handle_back_from_portrait(self, event_data):
        """Handle BACK_FROM_PORTRAIT - return to name confirmation screen"""
        print("⬅️ CharacterEngine: BACK_FROM_PORTRAIT event received")
        
        # Clear portrait selection
        if hasattr(self.game_state, 'selected_portrait_index'):
            self.game_state.selected_portrait_index = None
        
        # Navigate back to name confirmation
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'name_confirm'})

    def handle_reroll_from_confirm(self, event_data):
        """Handle reroll from low stats confirmation"""
        print("🎲 Player chose to reroll low stats")
        self.event_manager.emit("SCREEN_CHANGE", {"target": "stats"})

    def handle_proceed_with_low_stats(self, event_data):
        """Handle proceeding with low stats - show class-specific snarky comment"""
        import json
        import os
        import random
        
        # Get current character class
        character_class = self.game_state.character.get('class', 'fighter').lower()
        
        # Load class-specific snarky comments from JSON
        comments_file = os.path.join("data", "player", "low_stats_comments.json")
        try:
            with open(comments_file, 'r') as f:
                comments_data = json.load(f)
            
            # Get class-specific comments
            class_comments = comments_data["low_stats_comments"].get(character_class, 
                                        comments_data["low_stats_comments"]["fighter"])
            
            # Get random comment for this class
            proceed_messages = class_comments["proceed_messages"]
            selected_comment = random.choice(proceed_messages)
            
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            # Fallback comment
            selected_comment = {
                "title": "WELL, ALRIGHT THEN...",
                "main_text": "You're brave, I'll give you that!",
                "sub_text": "Good luck in combat with those stats."
            }
        
        print(f"{character_class.title()} with low primary abilities: {selected_comment['main_text']}")
        
        # Store the selected comment and switch to display mode
        self.game_state.temp_data["showing_snarky_comment"] = True
        self.game_state.temp_data["snarky_comment"] = selected_comment
        
        # Dynamically register full-screen clickable for snarky comment
        if hasattr(self, 'event_manager') and self.event_manager:
            # Clear existing clickables and register full-screen click
            from input_handler import InputHandler
            import pygame
            
            # Get reference to input handler (assuming it's accessible)
            # This is a bit of a hack - we need to access the input handler
            # You might need to pass the input handler reference to CharacterEngine
            
            # For now, emit an event to register the full-screen clickable
            self.event_manager.emit("REGISTER_FULL_SCREEN_CLICK", {
                "screen": "stats_confirm_low", 
                "event_type": "ADVANCE_FROM_SNARKY"
            })
            
    def ensure_active_portrait(self, game_state):
        """Ensure active portrait file exists, recreate if missing"""
        import os
        import shutil
        
        # Get portrait data from game_state instead
        selected_portrait = getattr(self.game_state, 'selected_portrait_index', None)
        gender = self.game_state.character.get('gender', 'male')

        if selected_portrait is not None:
            filename = f"player_{gender}_{selected_portrait + 1:02d}.jpg"
        else:
            filename = None
                
        if not filename:
            print("No portrait file specified in save data")
            return False
        
        # Build source path
        if gender == 'male':
            from utils.constants import MALE_PORTRAITS_PATH
            source_dir = MALE_PORTRAITS_PATH
        else:
            from utils.constants import FEMALE_PORTRAITS_PATH
            source_dir = FEMALE_PORTRAITS_PATH
        
        source_path = os.path.join(source_dir, filename)
        
        # Build active path
        active_dir = os.path.join(os.path.dirname(source_dir), "active")
        os.makedirs(active_dir, exist_ok=True)
        active_path = os.path.join(active_dir, "player.jpg")
        
        # Copy if source exists
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, active_path)
                print(f"Active portrait updated: {filename}")
                return True
            except Exception as e:
                print(f"Error updating active portrait: {e}")
                return False
        else:
            print(f"Warning: Source portrait not found: {filename}")
        return False

    def activate_character_portrait(self, game_state):
        """Ensure correct portrait is active for current character"""
        if hasattr(self, 'character') and 'selected_portrait_gender' in self.character:
            # Character has portrait selection data - ensure active portrait matches
            self.ensure_active_portrait(game_state)
        else:
            # No portrait selection data - clear any existing active portrait
            self.clear_active_portrait(game_state)

    def clear_active_portrait(self, game_state):
        """Remove active portrait file"""
        import os
        try:
            from utils.constants import MALE_PORTRAITS_PATH
            active_dir = os.path.join(os.path.dirname(MALE_PORTRAITS_PATH), "active")
            active_path = os.path.join(active_dir, "player.jpg")
            
            if os.path.exists(active_path):
                os.remove(active_path)
                print("Active portrait cleared")
        except Exception as e:
            print(f"Error clearing active portrait: {e}")

    def finalize_character(self, game_state):
        """
        Complete character creation by calculating final stats
        """
        self.character['hit_points'] = self.calculate_hp()
    
        # Add starting trinket to inventory
        if 'trinket' in self.character:
            self.inventory['items'].append(self.character['trinket'])

    def handle_gold_button_click(self, event_data):
        """Handle gold button click - either roll gold or continue to trinket screen"""
        
        # Check if gold already exists
        if 'gold' in self.game_state.character:
            # Gold already rolled, advance to trinket screen
            print("Gold confirmed, advancing to trinket screen")
            print(f"DEBUG: Current character data: {self.game_state.character}")
            self.event_manager.emit("SCREEN_CHANGE", {"target": "trinket"})
        else:
            # Use the sophisticated JSON-based class system
            self.roll_starting_gold()  # Updates GameState directly
            print(f"DEBUG: Character data after gold roll: {self.game_state.character}")
            # Stay on gold screen so button changes to "CONTINUE"

    def handle_trinket_button_click(self, event_data):
        """Handle trinket button click - either roll trinket or continue to summary screen"""
        
        # Check if trinket already exists
        if 'trinket' in self.game_state.character:
            # Trinket already rolled, advance to summary screen
            print("✨ Trinket confirmed, advancing to summary screen")
            print(f"🔍 DEBUG: Current character data: {self.game_state.character}")
            self.event_manager.emit("SCREEN_CHANGE", {"target": "summary"})
        else:
            # Roll for trinket using the updated JSON-based method
            trinket = self.roll_trinket()
            print(f"🔍 DEBUG: Character data after trinket roll: {self.game_state.character}")
            # Stay on trinket screen so button changes to "CONTINUE"

    def handle_start_game(self, event_data):
        """
        Handle START GAME button click from summary screen
        Finalize character and transition to intro sequence with auto-save
        """
        print("🎮 START GAME button clicked - finalizing character")
        
        # Use existing finalize_character_creation method
        self.finalize_character_creation()
        
        # Trigger intro sequence start (which handles auto-save)
        print("🎬 Triggering intro sequence with auto-save...")
        self.event_manager.emit("INTRO_START", {})

    def handle_keep_stats(self, event_data):
        """Handle keeping stats - check for low primary abilities first"""
       # print(f"DEBUG: CE: Starting KEEP_STATS check")
        
        # Get primary abilities for current class
        primary_abilities = self._get_primary_abilities()
        print(f"DEBUG: CE: Primary abilities: {primary_abilities}")

        # Check if any primary abilities are below 10
        low_primaries = []
        for ability in primary_abilities:
            current_value = self.game_state.character.get(ability, 10)
            print(f"DEBUG: {ability} = {current_value}")
            if current_value < 12:
                low_primaries.append(ability.title())
        
        print(f"DEBUG: Low primaries found: {low_primaries}")
        
        # Calculate HP immediately when stats are finalized
        hp = self.calculate_hp()
        print(f"💚 HP calculated with stats: {hp}")

        if low_primaries:
           
            # Store the low abilities and trigger confirmation screen
            self.game_state.temp_data = {"low_primaries": low_primaries}
            print(f"DEBUG: CE: About to emit SCREEN_CHANGE to stats_confirm_low")
            self.event_manager.emit("SCREEN_CHANGE", {"target": "stats_confirm_low"})
        else:
            print(f"DEBUG: CE: No low primaries, proceeding to gender")
            # Stats are good, proceed normally
            print("✅ Primary abilities are adequate, proceeding to gender")
            self.event_manager.emit("SCREEN_CHANGE", {"target": "gender"})

    def _get_primary_abilities(self):
        """Get primary abilities from JSON for current class"""
        import json
        import os
        
        class_file = os.path.join("data", "player", "character_classes.json")
        try:
            with open(class_file, 'r') as f:
                class_data = json.load(f)
            current_class = self.game_state.character.get('class', 'fighter')
            return class_data["character_classes"][current_class]["primary_abilities"]
        except:
            return ["strength", "constitution"]  # fallback

    def load_name_data(self):
        """Load character names from JSON file"""
        try:
            import json
            import os
            
            # Get the data file path
            data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'player', 'character_names.json')
            
            with open(data_path, 'r') as f:
                self.name_data = json.load(f)
            
            print("📚 Character names loaded from JSON")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load character names: {e}")
            # Fallback to hardcoded names
            self.name_data = {
                "male_names": {
                    "first": ["Garlen", "Theron", "Bjorn", "Marcus", "Aldric"],
                    "last": ["Sliverblade", "Ironwill", "Stormhammer", "Battleborn", "Steelhand"]
                },
                "female_names": {
                    "first": ["Kala", "Gina", "Sera", "Thessa", "Mira"],
                    "last": ["Stormborn", "Brightblade", "Ironheart", "Battlewise", "Steelstrike"]
                }
            }
            return False
    
    def generate_name_options(self, gender):
        """
        Generate 3 random name combinations for the specified gender
        Moved from GameState to CharacterEngine for proper separation of concerns
        
        Args:
            gender: 'male' or 'female'
            
        Returns:
            list: 3 unique name combinations
        """
        import random
        
        # Load names if not already loaded
        if not hasattr(self, 'name_data'):
            self.load_name_data()
        
        gender_key = f"{gender}_names"
        if gender_key not in self.name_data:
            print(f"❌ No name data for gender: {gender}")
            return ["Hero One", "Hero Two", "Hero Three"]
        
        first_names = self.name_data[gender_key]["first"]
        last_names = self.name_data[gender_key]["last"]
        
        names = []
        used_names = getattr(self.game_state, 'used_names', set())
        
        # For males, always include Garlen Sliverblade as option 1 if not used
        if gender == 'male' and "Garlen Sliverblade" not in used_names:
            names.append("Garlen Sliverblade")
            used_names.add("Garlen Sliverblade")
        
        # Generate random combinations for remaining slots
        attempts = 0
        while len(names) < 3 and attempts < 50:  # Prevent infinite loop
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            
            if full_name not in used_names:
                names.append(full_name)
                used_names.add(full_name)
            attempts += 1
        
        # Fill remaining slots if needed (fallback safety)
        while len(names) < 3:
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            names.append(full_name)
        
        # Store used names and current options in GameState
        self.game_state.used_names = used_names
        self.game_state.current_names = names
        
        print(f"🎭 Generated {len(names)} {gender} names: {names}")
        return names

    def calculate_hp(self, constitution_score=None, character_class=None):
        """
        Calculate hit points based on constitution score and class
        
        Args:
            constitution_score: Optional override, uses GameState if not provided
            character_class: Optional override, uses GameState if not provided
            
        Returns:
            int: Calculated hit points
        """
        if constitution_score is None:
            constitution_score = self.game_state.character.get('constitution', 10)
        
        if character_class is None:
            character_class = self.game_state.character.get('class', 'fighter')
        
        # Get class-specific hit die
        class_data = self._get_class_data(character_class)
        hit_die = class_data.get('hit_die', 10) if class_data else 10
        
        # Calculate constitution modifier
        constitution_modifier = (constitution_score - 10) // 2
        
        # HP = max hit die + constitution modifier (level 1)
        hit_points = hit_die + constitution_modifier
        
        # Minimum 1 HP (safety check)
        hit_points = max(1, hit_points)
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['hit_points'] = hit_points
        
        return hit_points
    
    def roll_starting_gold(self, character_class=None):
        """
        Roll starting gold based on character class using JSON data
        
        Args:
            character_class: Optional override, uses GameState if not provided
            
        Returns:
            int: Starting gold amount
        """
        import json
        import os
        import random
        
        # Load class data from JSON file
        class_file = os.path.join("data", "player", "character_classes.json")
        try:
            with open(class_file, 'r') as f:
                class_data = json.load(f)
        except FileNotFoundError:
            print("⚠️ Character class data file not found, using fallback")
            # Fallback for missing JSON file
            return self._fallback_gold_roll(character_class)
        
        # Determine character class
        if character_class is None:
            character_class = self.game_state.character.get('class', 'fighter')
        
        # Get class-specific gold configuration
        classes = class_data.get("character_classes", {})
        class_info = classes.get(character_class.lower(), classes.get('fighter', {}))
        
        if not class_info:
            print(f"⚠️ Class '{character_class}' not found, using fighter defaults")
            class_info = classes.get('fighter', {})
        
        # Extract gold rolling parameters
        gold_config = class_info.get("starting_gold", {
            "dice": 5, "sides": 6, "multiplier": 10, "description": "5d6 × 10 gold pieces"
        })
        
        dice_count = gold_config.get("dice", 5)
        die_sides = gold_config.get("sides", 6)
        multiplier = gold_config.get("multiplier", 10)
        description = gold_config.get("description", f"{dice_count}d{die_sides} × {multiplier}")
        
        # Roll the dice
        individual_rolls = []
        for _ in range(dice_count):
            roll = random.randint(1, die_sides)
            individual_rolls.append(roll)
        
        dice_total = sum(individual_rolls)
        starting_gold = dice_total * multiplier
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['gold'] = starting_gold
        
        # Enhanced logging for debugging and player feedback
        roll_details = " + ".join(map(str, individual_rolls))
        print(f"🏛️ {class_info.get('name', character_class.title())} Starting Gold:")
        print(f"💰 Formula: {description}")
        print(f"🎲 Rolled: [{roll_details}] = {dice_total}")
        print(f"💰 Total: {dice_total} × {multiplier} = {starting_gold} gold pieces")
        
        return starting_gold

    def _fallback_gold_roll(self, character_class=None):
        """
        Fallback gold rolling when JSON file is unavailable
        
        Args:
            character_class: Character class (ignored in fallback)
            
        Returns:
            int: Starting gold amount using default fighter formula
        """
        import random
        
        # Default to fighter formula: 5d6 × 10
        dice_total = sum(random.randint(1, 6) for _ in range(5))
        starting_gold = dice_total * 10
        
        self.game_state.character['gold'] = starting_gold
        
        print(f"💰 Fallback Gold Roll: 5d6 × 10 = {starting_gold} gold pieces")
        return starting_gold

    def apply_class_stat_adjustments(self, character_class=None):
        """
        Apply class-specific stat adjustments from JSON data
        
        Args:
            character_class: Optional override, uses GameState if not provided
            
        Returns:
            dict: Applied adjustments
        """
        import json
        import os
        
        # Load class data from JSON file
        class_file = os.path.join("data", "player", "character_classes.json")
        try:
            with open(class_file, 'r') as f:
                class_data = json.load(f)
        except FileNotFoundError:
            print("⚠️ Character class data file not found, no stat adjustments applied")
            return {}
        
        # Determine character class
        if character_class is None:
            character_class = self.game_state.character.get('class', 'fighter')
        
        # Get class-specific stat adjustments
        classes = class_data.get("character_classes", {})
        class_info = classes.get(character_class.lower(), {})
        stat_adjustments = class_info.get("stat_adjustments", {})
        
        applied_adjustments = {}
        
        # Apply each stat adjustment
        for stat, adjustment in stat_adjustments.items():
            if stat in self.game_state.character:
                old_value = self.game_state.character[stat]
                new_value = old_value + adjustment
                # Cap at 18 (D&D maximum for starting characters)
                new_value = min(new_value, 18)
                self.game_state.character[stat] = new_value
                applied_adjustments[stat] = adjustment
                print(f"📈 {stat.title()}: {old_value} + {adjustment} = {new_value}")
        
        if applied_adjustments:
            print(f"⚡ {class_info.get('name', character_class.title())} class bonuses applied!")
        
        return applied_adjustments
    
    def roll_trinket(self):
        """
        Roll for a mysterious starting trinket
        Classic D&D-style random trinket table loaded from JSON
        
        Returns:
            str: Description of the rolled trinket
        """
        import json
        import os
        import random
        
        # Load trinket data from JSON file
        trinket_file = os.path.join("data", "player", "trinkets.json")
        try:
            with open(trinket_file, 'r') as f:
                trinket_data = json.load(f)
            trinket_table = trinket_data["trinket_table"]
        except FileNotFoundError:
            print("⚠️ Trinket data file not found, using fallback")
            # Fallback trinket table if JSON file missing
            trinket_table = [
                "A small brass key with no lock in sight",
                "Smooth river stone with ancient runes carved deep",
                "Tiny glass vial filled with swirling purple mist"
            ]
        
        trinket = random.choice(trinket_table)
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['trinket'] = trinket
        
        print(f"✨ Rolled trinket: {trinket}")
        return trinket
    
    def set_character_class(self, character_class='fighter'):
        """
        Set character class with full framework support
        
        Args:
            character_class: Class name ('fighter', 'wizard', 'rogue', 'cleric')
        """
        class_data = self._get_class_data(character_class)
        
        if not class_data:
            print(f"⚠️ Invalid class {character_class}, defaulting to fighter")
            character_class = 'fighter'
            class_data = self._get_class_data('fighter')
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['class'] = character_class
        self.game_state.character['class_data'] = class_data
        
        print(f"⚔️ Character class set to: {character_class}")
        return character_class
    
    #TODO is this redundant?  review and see if this is conflicting with character_class JSON or
    # if other json data.  Is anything reading this data?
    def _get_class_data(self, character_class):
        """
        Get class-specific data for character creation and progression
        
        Returns:
            dict: Class data including equipment, abilities, progression
        """
        class_definitions = {
            'fighter': {
                'name': 'Fighter',
                'description': 'A master of martial combat, skilled with various weapons and armor',
                'hit_die': 10,  # d10 for HP per level
                'primary_stats': ['strength', 'constitution'],
                'starting_equipment': {
                    'weapon': 'Longsword',
                    'armor': 'Leather Armor', 
                    'shield': 'Shield',
                    'items': ['Hemp Rope']
                },
                'starting_gold': {'base': 5, 'multiplier': 5},  # 5d6 * 5 gold
                'abilities': {
                    'level_1': ['Combat Training', 'Weapon Mastery'],
                    'level_2': ['Action Surge'],
                    'level_3': ['Second Wind'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['Extra Attack']
                }
            },
            'wizard': {
                'name': 'Wizard',
                'description': 'A scholarly magic-user capable of manipulating arcane forces',
                'hit_die': 6,  # d6 for HP per level
                'primary_stats': ['intelligence', 'wisdom'],
                'starting_equipment': {
                    'weapon': 'Quarterstaff',
                    'armor': 'Robes',
                    'shield': None,
                    'items': ['Spellbook', 'Component Pouch']
                },
                'starting_gold': {'base': 3, 'multiplier': 10},  # 3d6 * 10 gold
                'abilities': {
                    'level_1': ['Spellcasting', 'Arcane Recovery'],
                    'level_2': ['School of Magic'],
                    'level_3': ['Cantrip Mastery'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['3rd Level Spells']
                },
                'spells_known': {
                    'level_1': ['Magic Missile', 'Shield', 'Detect Magic'],
                    'cantrips': ['Light', 'Mage Hand', 'Prestidigitation']
                }
            },
            'rogue': {
                'name': 'Rogue',
                'description': 'A scoundrel who uses stealth and trickery to overcome obstacles',
                'hit_die': 8,  # d8 for HP per level
                'primary_stats': ['dexterity', 'intelligence'],
                'starting_equipment': {
                    'weapon': 'Shortsword',
                    'armor': 'Leather Armor',
                    'shield': None,
                    'items': ['Thieves Tools', 'Daggers (2)']
                },
                'starting_gold': {'base': 4, 'multiplier': 4},  # 4d6 * 4 gold
                'abilities': {
                    'level_1': ['Sneak Attack', 'Thieves Cant'],
                    'level_2': ['Cunning Action'],
                    'level_3': ['Roguish Archetype'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['Uncanny Dodge']
                }
            },
            'cleric': {
                'name': 'Cleric',
                'description': 'A priestly champion who wields divine magic in service of a higher power',
                'hit_die': 8,  # d8 for HP per level
                'primary_stats': ['wisdom', 'constitution'],
                'starting_equipment': {
                    'weapon': 'Mace',
                    'armor': 'Scale Mail',
                    'shield': 'Shield',
                    'items': ['Holy Symbol', 'Prayer Book']
                },
                'starting_gold': {'base': 5, 'multiplier': 4},  # 5d6 * 4 gold
                'abilities': {
                    'level_1': ['Divine Magic', 'Turn Undead'],
                    'level_2': ['Channel Divinity'],
                    'level_3': ['Divine Domain'],
                    'level_4': ['Ability Score Improvement'],
                    'level_5': ['3rd Level Spells']
                },
                'spells_known': {
                    'level_1': ['Cure Wounds', 'Bless', 'Detect Evil'],
                    'cantrips': ['Sacred Flame', 'Light', 'Thaumaturgy']
                }
            }
        }
        
        return class_definitions.get(character_class.lower())
    
    # ==========================================
    # CHARACTER PROGRESSION OPERATIONS
    # ==========================================
    
    def get_level_requirements(self):
        return list(self._level_requirements)

    def can_level_up(self):
        """
        Check if character has enough experience to level up
        
        Returns:
            bool: True if character can level up
        """
        current_level = self.game_state.character.get('level', 1)
        current_xp = self.game_state.character.get('experience', 0)
        
        # Get XP requirements from narrative schema
        #from utils.narrative_schema import narrative_schema
        xp_requirements = narrative_schema.schema.get('xp_balance', {}).get('level_progression', {}).get('requirements', [0, 300, 900, 2700, 6500])
        
        # Convert list to dict for compatibility
        xp_req_dict = {}
        for level, xp in enumerate(xp_requirements, 1):
            if level <= len(xp_requirements):
                xp_req_dict[level] = xp
        xp_requirements = xp_req_dict
        
        next_level = current_level + 1
        if next_level <= 5 and current_xp >= xp_requirements.get(next_level, 999999):
            return True
        
        return False
    
    def level_up(self):
        """
        Perform level up operation with class-specific progression
        Increases level, recalculates HP, grants improvements
        
        Returns:
            dict: Level up results (new level, hp gain, abilities gained, etc.)
        """
        if not self.can_level_up():
            print("❌ Character cannot level up yet")
            return None
        
        current_level = self.game_state.character.get('level', 1)
        new_level = current_level + 1
        character_class = self.game_state.character.get('class', 'fighter')
        
        # Get class-specific data
        class_data = self._get_class_data(character_class)
        hit_die = class_data.get('hit_die', 10) if class_data else 10
        
        # Roll for HP gain (class hit die + con modifier per level)
        constitution_modifier = (self.game_state.character.get('constitution', 10) - 10) // 2
        hp_gain = random.randint(1, hit_die) + constitution_modifier
        hp_gain = max(1, hp_gain)  # Minimum 1 HP per level
        
        # Get new abilities for this level
        new_abilities = []
        if class_data and 'abilities' in class_data:
            level_key = f'level_{new_level}'
            new_abilities = class_data['abilities'].get(level_key, [])
        
        # Update character stats in GameState (Single Data Authority)
        self.game_state.character['level'] = new_level
        current_hp = self.game_state.character.get('hit_points', 10)
        self.game_state.character['hit_points'] = current_hp + hp_gain
        
        # Track abilities gained
        if 'abilities' not in self.game_state.character:
            self.game_state.character['abilities'] = []
        self.game_state.character['abilities'].extend(new_abilities)
        
        level_up_results = {
            'new_level': new_level,
            'hp_gain': hp_gain,
            'new_total_hp': self.game_state.character['hit_points'],
            'abilities_gained': new_abilities,
            'class': character_class
        }
        
        print(f"🎊 LEVEL UP! Now level {new_level} {character_class.title()}, gained {hp_gain} HP")
        if new_abilities:
            print(f"📚 New abilities: {', '.join(new_abilities)}")
        
        return level_up_results
    
    def award_experience(self, xp_amount, reason=""):
        """
        Award experience points to character based on different sources
        
        Args:
            xp_amount: Amount of XP to award
            reason: Optional description of why XP was awarded
        """
        current_xp = self.game_state.character.get('experience', 0)
        new_xp = current_xp + xp_amount
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['experience'] = new_xp
        
        print(f"⭐ Awarded {xp_amount} XP! {reason}")
        print(f"   Total XP: {new_xp}")
        
        # Check for level up opportunity
        if self.can_level_up():
            print("🎊 Ready to level up!")
        
        return new_xp
    
    def award_combat_xp(self, enemy_level=1, enemy_count=1):
        """Award XP for combat victories"""
        base_xp = enemy_level * 100
        total_xp = base_xp * enemy_count
        return self.award_experience(total_xp, f"defeated {enemy_count} enemies")
    
    #TODO  does this need t be removed or updated since we have a calculated XP
    # ENHANCED VERSION - More precise than legacy, less specific than quest_engine
    def award_quest_xp(self, quest_type="normal", custom_amount=None):
        """Award XP for quest completion with flexible options"""
        if custom_amount:
            return self.award_experience(custom_amount, f"Quest: custom")
    
        # Fallback XP values for generic quest types
        xp_values = {
            'easy': 100, 
            'normal': 200, 
            'hard': 400, 
            'epic': 800,
            'main_story': 1000
        }
        xp = xp_values.get(quest_type, 200)
        return self.award_experience(xp, f"Quest: {quest_type}")
    
    def award_skill_xp(self, skill_success=True):
        """Award XP for successful skill achievements"""
        if skill_success:
            return self.award_experience(50, "successful skill achievement")
        return 0
    
    def award_gambling_streak_xp(self, streak_length):
        """Award XP for gambling streaks of 3 or more"""
        if streak_length >= 3:
            xp = min(100, streak_length * 20)  # Cap at 100 XP
            return self.award_experience(xp, f"gambling streak of {streak_length}")
        return 0
    
    def register_quest_events(self, event_manager):
        """Register for quest completion events - follows character creation pattern"""
        self.event_manager = event_manager
        
        # Quest completion events
        event_manager.register("QUEST_COMPLETED", self._handle_quest_completion)
        event_manager.register("INFORMATION_DISCOVERED", self._handle_information_discovery)
        
        print("🎯 CharacterEngine registered for quest events")
    
    def _handle_quest_completion(self, event_data):
        """Handle quest completion XP awards"""
        quest_id = event_data.get("quest_id")
        quest_title = event_data.get("quest_title", "Unknown Quest")
        xp_reward = event_data.get("xp_reward", 0)
        completion_type = event_data.get("completion_type", "quest")
        
        print(f"🏆 Quest completed: {quest_title}")
        
        # Award XP to all party members
        affected_members = self.award_party_xp(xp_reward, f"Quest: {quest_title}")
        
        # Check for level ups
        level_up_members = self.check_party_level_ups()
        
        # If anyone leveled up, trigger character sheet notification
        if level_up_members:
            self.event_manager.emit("LEVEL_UP_AVAILABLE", {
                "characters": level_up_members,
                "source": quest_id
            })
            print(f"🎊 Level up available for: {', '.join(level_up_members)}")
    
    def _handle_information_discovery(self, event_data):
        """Handle information discovery XP awards"""
        info_type = event_data.get("info_type")
        xp_reward = event_data.get("xp_reward", 0)
        
        # Award discovery XP to all party members
        self.award_party_xp(xp_reward, f"Discovery: {info_type}")

    # ==========================================
    # PARTY XP TRACKING METHODS
    # ==========================================
    
    def award_party_xp(self, xp_amount, reason=""):
        """Award XP to all current party members"""
        affected_members = []
        
        # Check if we're in combat state
        if getattr(self.game_state, 'in_combat', False):
            # Store for later processing
            if 'pending_xp' not in self.game_state.__dict__:
                self.game_state.pending_xp = []
            self.game_state.pending_xp.append({'amount': xp_amount, 'reason': reason})
            print(f"⏳ XP deferred (combat): {xp_amount} - {reason}")
            return []
        
        # Award to player character
        old_xp = self.game_state.character.get('experience', 0)
        self.award_experience(xp_amount, reason)
        affected_members.append("player")
        
        # Award to all party members
        for member_id in self.game_state.party_members:
            self.award_party_member_xp(member_id, xp_amount, reason)
            affected_members.append(member_id)
        
        print(f"⭐ Party XP awarded: {xp_amount} to {len(affected_members)} members - {reason}")
        return affected_members
    
    def award_party_member_xp(self, member_id, xp_amount, reason=""):
        """Award XP to specific party member"""
        # Initialize party XP tracking if needed
        if 'party_xp' not in self.game_state.__dict__:
            self.game_state.party_xp = {}
        
        if member_id not in self.game_state.party_xp:
            self.game_state.party_xp[member_id] = {
                'experience': 0, 
                'level': 1,
                'hit_points': self._get_party_member_starting_hp(member_id)
            }
        
        # Award XP
        current_xp = self.game_state.party_xp[member_id]['experience']
        new_xp = current_xp + xp_amount
        self.game_state.party_xp[member_id]['experience'] = new_xp
        
        print(f"⭐ {member_id.title()} gained {xp_amount} XP! (Total: {new_xp}) - {reason}")
    
    def _get_party_member_starting_hp(self, member_id):
        """Get starting HP for party member based on their class"""
        # This would normally come from NPC data files
        hp_values = {
            "gareth": 15,    # Fighter
            "elara": 8,      # Wizard  
            "thorman": 12,   # Cleric
            "lyra": 10       # Rogue
        }
        return hp_values.get(member_id, 10)
    
    def check_party_level_ups(self):
        """Check which party members can level up"""
        level_up_candidates = []
        
        # Check player character
        if self.can_level_up():
            level_up_candidates.append("player")
        
        # Check party members
        for member_id in self.game_state.party_members:
            if self.can_party_member_level_up(member_id):
                level_up_candidates.append(member_id)
        
        return level_up_candidates
    
    def can_party_member_level_up(self, member_id):
        """Check if party member has enough XP to level up"""
        if 'party_xp' not in self.game_state.__dict__:
            return False
        
        if member_id not in self.game_state.party_xp:
            return False
        
        member_data = self.game_state.party_xp[member_id]
        current_level = member_data.get('level', 1)
        current_xp = member_data.get('experience', 0)
        
        #TODO   Don;t we need to update this hardcoded xp requirements as well??
        # Use same XP table as player
        xp_requirements = {1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500}
        
        next_level = current_level + 1
        if next_level <= 5 and current_xp >= xp_requirements.get(next_level, 999999):
            return True
        
        return False
    
    def level_up_party_member(self, member_id):
        """Level up a specific party member"""
        if not self.can_party_member_level_up(member_id):
            print(f"❌ {member_id} cannot level up yet")
            return None
        
        member_data = self.game_state.party_xp[member_id]
        current_level = member_data.get('level', 1)
        new_level = current_level + 1
        
        # Get class-specific HP gain (simplified)
        hp_gain_by_class = {
            "gareth": 8,     # Fighter - d10 average
            "elara": 4,      # Wizard - d6 average  
            "thorman": 6,    # Cleric - d8 average
            "lyra": 5        # Rogue - d6+1 average
        }
        
        hp_gain = hp_gain_by_class.get(member_id, 5)
        
        # Update party member stats
        member_data['level'] = new_level
        current_hp = member_data.get('hit_points', 10)
        member_data['hit_points'] = current_hp + hp_gain
        
        print(f"🎊 {member_id.title()} leveled up! Now level {new_level}, gained {hp_gain} HP")
        
        return {
            'member_id': member_id,
            'new_level': new_level,
            'hp_gain': hp_gain,
            'new_total_hp': member_data['hit_points']
        }
    
    def get_party_member_info(self, member_id):
        """Get complete info for a party member"""
        if 'party_xp' not in self.game_state.__dict__:
            return None
        
        if member_id not in self.game_state.party_xp:
            return None
        
        member_data = self.game_state.party_xp[member_id]
        

        #TODO   Don;t we need to update this hardcoded xp requirements as well??
        # Calculate XP to next level
        current_level = member_data.get('level', 1)
        current_xp = member_data.get('experience', 0)
        xp_requirements = {1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500}
        
        next_level_xp = xp_requirements.get(current_level + 1, 999999)
        xp_to_next = max(0, next_level_xp - current_xp)
        
        return {
            'id': member_id,
            'level': current_level,
            'experience': current_xp,
            'hit_points': member_data.get('hit_points', 10),
            'xp_to_next_level': xp_to_next,
            'can_level_up': self.can_party_member_level_up(member_id)
        }

    # ==========================================
    # CHARACTER VALIDATION & UTILITY
    # ==========================================
    
    def validate_character(self):
        """
        Validate character data integrity
        Ensures all required fields exist with valid values
        
        Returns:
            bool: True if character data is valid
        """
        required_fields = ['name', 'class', 'strength', 'dexterity', 'constitution', 
                          'intelligence', 'wisdom', 'charisma', 'hit_points', 'gold']
        
        for field in required_fields:
            if field not in self.game_state.character:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Validate stat ranges (3-18 for standard D&D)
        stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        for stat in stats:
            value = self.game_state.character.get(stat, 0)
            if not (3 <= value <= 18):
                print(f"❌ Invalid {stat} value: {value} (must be 3-18)")
                return False
        
        print("✅ Character data validated successfully")
        return True
    
    def get_character_summary(self):
        """
        Get formatted character summary for display
        
        Returns:
            dict: Character summary data
        """
        char = self.game_state.character
        
        summary = {
            'name': char.get('name', 'Unknown'),
            'class': char.get('class', 'fighter').title(),
            'level': char.get('level', 1),
            'hit_points': char.get('hit_points', 10),
            'experience': char.get('experience', 0),
            'stats': {
                'Strength': char.get('strength', 10),
                'Dexterity': char.get('dexterity', 10),
                'Constitution': char.get('constitution', 10),
                'Intelligence': char.get('intelligence', 10),
                'Wisdom': char.get('wisdom', 10),
                'Charisma': char.get('charisma', 10)
            },
            'equipment': {
                'weapon': char.get('equipped_weapon', 'Longsword'),
                'armor': char.get('equipped_armor', 'Leather Armor'),
                'shield': char.get('equipped_shield', 'Shield')
            }
        }
        
        return summary

    def _handle_xp_award(self, event_data):
        """Handle XP_AWARDED events from quest/combat/discovery systems"""
        xp_amount = event_data.get('amount', 0)
        reason = event_data.get('reason', 'Unknown')
        
        if xp_amount > 0:
            self.award_party_experience(xp_amount, reason)

    def _handle_quest_xp(self, event_data):
        """Handle QUEST_COMPLETED events with appropriate XP rewards"""
        quest_id = event_data.get('quest_id', '')
        xp_amount = event_data.get('amount', 300)
        reason = f"completed quest: {quest_id}"
        
        self.award_party_experience(xp_amount, reason)

    def award_party_experience(self, xp_amount, reason=""):
        """Award experience to all party members using GameState data"""
        # Award to player (existing logic)
        current_player_xp = self.game_state.character.get('experience', 0)
        self.game_state.character['experience'] = current_player_xp + xp_amount
        
        # Award to all party members
        level_up_candidates = []
        for party_member in self.game_state.party_member_data:
            old_xp = party_member.get('experience', 0)
            new_xp = old_xp + xp_amount
            party_member['experience'] = new_xp
                       
            # Check for level-up opportunity
            if self._can_npc_level_up(party_member):
                level_up_candidates.append(party_member['name'])
        
        print(f"⭐ Awarded {xp_amount} XP to entire party! {reason}")
        if level_up_candidates:
            print(f"🎊 Ready to level up: {', '.join(level_up_candidates)}")
        
        # Check if player can level up too
        if self.can_level_up():
            print("🎊 Player ready to level up!")

    def _can_npc_level_up(self, npc_data):
        """Check if NPC can level up using same XP table as player"""
        current_level = npc_data.get('level', 1)
        current_xp = npc_data.get('experience', 0)
        
        # Get XP requirements from narrative schema
        #from utils.narrative_schema import narrative_schema   
        xp_requirements = narrative_schema.schema.get('xp_balance', {}).get('level_progression', {}).get('requirements', [0, 300, 900, 2700, 6500])
        
        # Convert to dict format
        xp_req_dict = {i+1: xp for i, xp in enumerate(xp_requirements)}
        xp_requirements = xp_req_dict
        
        next_level = current_level + 1
        return (next_level <= 5 and 
                current_xp >= xp_requirements.get(next_level, 999999))

    def finalize_character_creation(self):
        """
        Complete character creation process with class-specific setup
        Performs final calculations and validations
        """
        character_class = self.game_state.character.get('class', 'fighter')
        
        # Calculate class-specific starting stats
        if 'hit_points' not in self.game_state.character:
            self.calculate_hp()
        
        # Set starting level and XP
        self.game_state.character['level'] = 1
        self.game_state.character['experience'] = 0
        
        # Roll starting gold based on class
        if 'gold' not in self.game_state.character:
            self.roll_starting_gold()
        
        # Set up starting equipment based on class
        class_data = self._get_class_data(character_class)
        if class_data and 'starting_equipment' in class_data:
            starting_equipment = class_data['starting_equipment']
            
            # Add weapons to inventory
            if starting_equipment.get('weapon'):
                if 'weapons' not in self.game_state.inventory:
                    self.game_state.inventory['weapons'] = []
                weapon = starting_equipment['weapon']
                self.game_state.inventory['weapons'].append(weapon)
                self.game_state.character['equipped_weapon'] = weapon
            
            # Add armor to inventory
            if starting_equipment.get('armor'):
                if 'armor' not in self.game_state.inventory:
                    self.game_state.inventory['armor'] = []
                armor = starting_equipment['armor']
                self.game_state.inventory['armor'].append(armor)
                self.game_state.character['equipped_armor'] = armor
            
            # Add shield if applicable
            if starting_equipment.get('shield'):
                shield = starting_equipment['shield']
                self.game_state.inventory['armor'].append(shield)
                self.game_state.character['equipped_shield'] = shield
            
            # Add class-specific items
            class_items = starting_equipment.get('items', [])
            if 'items' not in self.game_state.inventory:
                self.game_state.inventory['items'] = []
            self.game_state.inventory['items'].extend(class_items)
        
        # Add trinket to inventory if it exists
        trinket = self.game_state.character.get('trinket')
        if trinket and trinket != 'None':
            if 'items' not in self.game_state.inventory:
                self.game_state.inventory['items'] = []
            self.game_state.inventory['items'].append(trinket)
        
        # Set up class-specific abilities
        if class_data and 'abilities' in class_data:
            level_1_abilities = class_data['abilities'].get('level_1', [])
            self.game_state.character['abilities'] = level_1_abilities.copy()
        
        # Set up spells for casters
        if class_data and 'spells_known' in class_data:
            self.game_state.character['spells'] = class_data['spells_known'].copy()
        
        # Validate the completed character
        is_valid = self.validate_character()
        
        if is_valid:
            print("✅ Character creation finalized successfully!")
            char_name = self.game_state.character.get('name', 'Unknown Hero')
            char_class = self.game_state.character.get('class', 'fighter').title()
            print(f"🎭 Welcome to Redstone, {char_name} the {char_class}!")
        else:
            print("❌ Character creation validation failed!")
        
        return is_valid
    
# ==========================================
# GLOBAL CHARACTER ENGINE MANAGEMENT
# ==========================================

# Global character engine instance (initialized by DataManager)
character_engine = None

def get_character_engine():
    """
    Get the global character engine instance
    Will be initialized by DataManager integration
    """
    return character_engine

def initialize_character_engine(game_state_ref, event_manager=None):
    """
    Initialize the global character engine with event management
    """
    global character_engine
    character_engine = CharacterEngine(game_state_ref)
    
    # Register for stat events if event manager provided
    if event_manager:
        character_engine.register_character_creation_events(event_manager)
        print("📝 CharacterEngine registered for character creation events")
        character_engine.register_quest_events(event_manager)
        print("🎯 CharacterEngine registered for quest events")
        character_engine.set_event_manager(event_manager)
    else:
        print("⚠️ No EventManager provided to CharacterEngine")
    
    print("🔧 Initialized CharacterEngine")
    return character_engine

# Development and testing utilities
if __name__ == "__main__":
    print("🧪 CharacterEngine Development Test")
    print("=" * 50)
    
    print("CharacterEngine follows Single Data Authority pattern:")
    print("- GameState = THE authoritative data source")
    print("- CharacterEngine = Pure business logic processor")
    print("- No data storage in engine itself")
    print("- All operations modify GameState directly")
    print("- Supports character creation AND progression (levels 1-5)")
    
    print("\n✅ CharacterEngine module loaded successfully!")