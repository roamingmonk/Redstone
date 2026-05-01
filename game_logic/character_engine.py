# game_logic/character_engine.py
"""
Character Management Engine - Pure Single Data Authority Pattern
GameState = THE authoritative data source
CharacterEngine = Pure business logic processor
"""

import json
import os
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
    
    def __init__(self, game_state_ref, event_manager=None, item_manager_ref=None):
        self.game_state = game_state_ref
        self.event_manager = event_manager
        self.item_manager = item_manager_ref
        #print("🏗️ CharacterEngine initialized with Single Data Authority pattern")

        # cache just once
        xp_cfg = (getattr(narrative_schema, "schema", {}) or {}).get("xp_balance", {}) or {}
        self._level_requirements = (xp_cfg.get("level_progression", {}) or {}).get(
            "requirements", [0, 300, 1000]
            # Redstone 2 sequel: extend to [0, 300, 1000, 2700, 6500] for levels 4-5
        )

    # ==========================================
    # CHARACTER CREATION OPERATIONS
    # ==========================================
    def _handle_new_game(self, event_data):
        """Handle starting character creation flow"""
        print("🎮 CharacterEngine: Starting character creation")
        
        # Initialize character creation with proper setup
        self.initialize_character_creation()
        
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

    def initialize_character_creation(self):
        #########################################
        ######## ADD Class selection Here #######
        #########################################
        """
        Initialize a new character creation session
        Sets up default values and prepares for character creation flow
        """
        print("🎮 Initializing character creation session")
        
        # Set default class (expandable to class selection screen later)
        self.set_character_class('fighter')
        
        # Initialize any other default character creation values
        self.game_state.character['level'] = 1
        self.game_state.character['experience'] = 0
        self.game_state.stats_rolled = False
        
        print("✅ Character creation initialized with default fighter class")

    def roll_stats(self, reroll_ones=True):
        """Roll character stats using 4d6-drop-lowest. Updates GameState directly."""
        stats = {}
        stat_names = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        
        for stat in stat_names:
            # Roll 4d6, drop lowest — average ~12.2 vs 3d6's ~10.5
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.remove(min(rolls))
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

    # def _handle_keep_stats(self, event_data):
    #     """Handle KEEP_STATS - finalize and navigate"""
    #     print("✅ CharacterEngine: KEEP_STATS event received")
    #     # Emit navigation event
    #     if self.event_manager:
    #         self.event_manager.emit('SCREEN_CHANGE', {'target': 'gender'})

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
        event_manager.register('SELECT_PORTRAIT_6', self._handle_select_portrait)
        event_manager.register('CONFIRM_PORTRAIT', self._handle_confirm_portrait)
        event_manager.register('BACK_FROM_PORTRAIT', self._handle_back_from_portrait)
        event_manager.register('CAVIA_WARNING_BACK', self._handle_cavia_warning_back)
        event_manager.register('CAVIA_WARNING_CONFIRM', self._handle_cavia_warning_confirm)

        #Gold selection events
        event_manager.register("GOLD_BUTTON_CLICK", self.handle_gold_button_click)

        # Trinket screen events
        event_manager.register('TRINKET_BUTTON_CLICK', self.handle_trinket_button_click)

        # Summary screen events
        event_manager.register('START_GAME', self.handle_start_game)

        print("🎯 CharacterEngine registered for all character creation events")

    def register_quest_events(self, event_manager):
        """Register for quest completion events - matches character creation pattern"""
        self.event_manager = event_manager  
        
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

    def _handle_cavia_warning_back(self, event_data):
        """Handle going back from Cavia warning - return to portrait selection"""
        print("⬅️ CharacterEngine: Player declined Cavia selection")
        
        # Clear the Cavia flag
        self.game_state.character['is_cavia'] = False
        
        # Clear portrait selection
        if hasattr(self.game_state, 'selected_portrait_index'):
            self.game_state.selected_portrait_index = None
        
        # Return to portrait selection
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'portrait_selection'})
    
    def _handle_cavia_warning_confirm(self, event_data):
        """Handle Cavia warning confirmation - apply species and proceed"""
        print("🐹 Player confirmed Cavia selection!")
        
        # Get current gender for portrait setting (portrait #6 = index 5)
        gender = self.game_state.character.get('gender', 'male')
        portrait_index = 5  # Cavia is always portrait #6
        
        # Set the Cavia portrait
        self.game_state.set_selected_portrait(gender, portrait_index)
        
        # Apply Cavia species modifiers (includes stat caps and abilities)
        self._apply_species_modifiers('cavia')
        
        # Cavia special: Reroll charisma with +5 bonus, keep higher value
        original_charisma = self.game_state.character.get('charisma', 10)
        reroll = random.randint(1, 18) + 5  # Roll 1d18+5
        if reroll >= 18:
            reroll = 18
        
        if reroll > original_charisma:
            self.game_state.character['charisma'] = reroll
            print(f"🎲 Cavia charisma reroll: {original_charisma} → {reroll} (rolled {reroll-5}+5)")
        else:
            print(f"🎲 Cavia charisma reroll: Kept original {original_charisma} (rolled {reroll-5}+5 = {reroll})")
        
        # Copy selected portrait to active location
        self.ensure_active_portrait(self.game_state)
        
        # Proceed to gold screen
        if self.event_manager:
            self.event_manager.emit('SCREEN_CHANGE', {'target': 'gold'})

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
        """Handle SELECT_PORTRAIT - store selection for UI highlighting"""
        action = event_data.get('action', '')
        if action.startswith('SELECT_PORTRAIT_'):
            # Convert 1-6 to 0-5 for internal indexing
            portrait_index = int(action.split('_')[-1]) - 1
            
            # Check if Cavia portrait selected (portrait #6 = index 5)
            is_cavia = (portrait_index == 5)
            
            # Get current gender
            gender = self.game_state.character.get('gender', 'male')
            
            # Store the selected portrait index for UI highlighting (0-5)
            self.game_state.selected_portrait_index = portrait_index
            
            # Store Cavia flag
            self.game_state.character['is_cavia'] = is_cavia
            
            if is_cavia:
                print(f"🐹 CAVIA portrait selected! (Will show warning on Continue)")
                # Store selection but don't apply modifiers yet - wait for Continue
                gender = self.game_state.character.get('gender', 'male')
                self.game_state.set_selected_portrait(gender, portrait_index)
            else:
                # Normal human portrait - use existing GameState method
                self.game_state.set_selected_portrait(gender, portrait_index)
                print(f"🎭 Portrait {portrait_index + 1} selected for {gender} (internal index: {portrait_index})")
                
                # Apply Human species modifiers for portraits 1-5
                self._apply_species_modifiers('human')

    def _handle_confirm_portrait(self, event_data):
        """Handle CONFIRM_PORTRAIT - finalize selection and navigate to gold screen"""
        print("✅ CharacterEngine: CONFIRM_PORTRAIT event received")
        
        if hasattr(self.game_state, 'selected_portrait_index') and self.game_state.selected_portrait_index is not None:
            print(f"🎉 Portrait selection confirmed: {self.game_state.selected_portrait_index + 1}")
            
            # Copy selected portrait to active location
            self.ensure_active_portrait(self.game_state)

            # Check if Cavia was selected - show warning before proceeding
            is_cavia = self.game_state.character.get('is_cavia', False)
            
            if is_cavia:
                print(f"🐹 Cavia confirmed - showing warning screen")
                # Navigate to Cavia warning instead of gold
                if self.event_manager:
                    self.event_manager.emit('SCREEN_CHANGE', {'target': 'cavia_warning'})
            else:
                # Normal flow - apply human modifiers and go to gold screen
                self._apply_species_modifiers('human')
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

    def _apply_species_modifiers(self, species_id):
        """Apply species-specific stat modifiers and abilities"""
        print(f"🧬 Applying species modifiers for: {species_id}")
        
        # Load species data
        species_path = os.path.join('data', 'player', 'species.json')
        
        try:
            with open(species_path, 'r', encoding='utf-8') as f:
                species_data = json.load(f)
            
            species = species_data['species'].get(species_id)
            if not species:
                print(f"⚠️ Species '{species_id}' not found in species.json")
                return
            
            # Store species information in character
            self.game_state.character['species'] = {
                'id': species_id,
                'display_name': species['display_name'],
                'special_abilities': species.get('special_abilities', []),
                'resistances': species.get('resistances', []),
                'dialogue_flags': species.get('dialogue_flags', {})
            }
            
            # Apply stat modifiers (caps) - stats are stored directly in character dict
            stat_modifiers = species.get('stat_modifiers', {})
            
            for stat_name, limits in stat_modifiers.items():
                # Check if stat exists directly in character dict
                if stat_name in self.game_state.character:
                    min_val = limits.get('min', 3)
                    max_val = limits.get('max', 18)
                    
                    current_val = self.game_state.character[stat_name]
                    
                    if current_val > max_val:
                        self.game_state.character[stat_name] = max_val
                        print(f"  📉 {stat_name.capitalize()} capped: {current_val} → {max_val}")
                    elif current_val < min_val:
                        self.game_state.character[stat_name] = min_val
                        print(f"  📈 {stat_name.capitalize()} raised: {current_val} → {min_val}")
            
            # Set dialogue flags for easy access
            for flag, value in species.get('dialogue_flags', {}).items():
                # Set in character dict (where it's already working)
                self.game_state.character[flag] = value
                
                # ALSO set in flags dict if it exists
                if hasattr(self.game_state, 'flags'):
                    self.game_state.flags[flag] = value
                    print(f"  🏳️ Set dialogue flag in flags dict: {flag} = {value}")
                else:
                    print(f"  🏳️ Set dialogue flag in character: {flag} = {value}")
            
            print(f"✅ Species modifiers applied: {species['display_name']}")
            print(f"  Abilities: {len(species.get('special_abilities', []))}")
            print(f"  Resistances: {', '.join(species.get('resistances', [])) if species.get('resistances') else 'None'}")
            
        except Exception as e:
            print(f"❌ Error loading species data: {e}")

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

    def handle_gold_button_click(self, event_data):
        """Handle gold button click - either roll gold or continue to trinket screen"""
    
        # Check if gold already rolled (has meaningful value)
        current_gold = self.game_state.character.get('gold', 0)
        if current_gold > 0:
            # Gold already rolled, advance to trinket screen
            print("Gold confirmed, advancing to trinket screen")
            self.event_manager.emit("SCREEN_CHANGE", {"target": "trinket"})
        else:
            # Roll for gold
            self.roll_starting_gold()
            print(f"DEBUG: Character data after gold roll: {self.game_state.character}")

    def handle_trinket_button_click(self, event_data):
        """Handle trinket button click - either roll trinket or continue to summary screen"""
        
        # Check if trinket already rolled (not empty string)
        current_trinket = self.game_state.character.get('trinket', '')
        if current_trinket and current_trinket != '':
            # Trinket already rolled, finalize character BEFORE showing summary
            print("✨ Trinket confirmed, finalizing character...")
            self.finalize_character_creation()
            print("✅ Character finalized, advancing to summary screen")
            self.event_manager.emit("SCREEN_CHANGE", {"target": "summary"})
        else:
            # Roll for trinket
            trinket = self.roll_trinket()
            #print(f"🔍 DEBUG: Character data after trinket roll: {self.game_state.character}")
            # Stay on trinket screen so button changes to "CONTINUE"

    def handle_start_game(self, event_data):
        """
        Handle START GAME button click from summary screen
        Character already finalized, just start the game
        """
        print("🎮 START GAME button clicked - starting adventure!")
        
        # Character was already finalized when summary screen was shown
        # Just trigger intro sequence start (which handles auto-save)
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
        class_data = self._load_class_data_from_json(character_class)
        hit_die = class_data.get('hit_die', 10)
        
        # Calculate constitution modifier
        constitution_modifier = (constitution_score - 10) // 2
        
        # HP = max hit die + constitution modifier (level 1)
        hit_points = hit_die + constitution_modifier
        
        # Minimum 1 HP (safety check)
        hit_points = max(1, hit_points)
        
        # Update GameState directly (Single Data Authority)
        self.game_state.character['max_hp'] = hit_points # Maximum hit points
        self.game_state.character['current_hp'] = hit_points # Current hit points
        
        return hit_points
    
    def roll_starting_gold(self, character_class=None):
        """
        Roll starting gold based on character class using JSON data
        Args: character_class: Optional override, uses GameState if not provided
        Returns:int: Starting gold amount
        """
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

    def _load_class_data_from_json(self, character_class):
        """
        Load class data from JSON file - replacement for old _get_class_data
        """
        
        try:
            class_file = os.path.join("data", "player", "character_classes.json")
            with open(class_file, 'r') as f:
                json_data = json.load(f)
            
            return json_data["character_classes"].get(character_class, {})
        except Exception as e:
            print(f"Error loading class data for {character_class}: {e}")
            return {}

    #@staticmethod
    def _roll_hit_point_gain(self, hit_die, constitution_score):
        """
        Roll HP gain for level up using hit die + CON modifier
        Args:    hit_die: Class hit die (d6, d8, d10, d12)
                 constitution_score: Character's CON score
        Returns: tuple: (hp_gain, dice_roll, con_modifier)
        """
        constitution_modifier = (constitution_score - 10) // 2
        # CON modifier can't reduce HP gain below 0
        con_bonus = max(0, constitution_modifier)
        
        dice_roll = random.randint(1, hit_die)
        
        # Apply minimum average: (hit_die / 2) + 1, rounded up
        minimum_hp = (hit_die // 2) + 0  # d10=5, d8=4, d6=3, d12=6
        hp_gain = max(minimum_hp, dice_roll + con_bonus)
        
        return hp_gain, dice_roll, con_bonus

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
                # Cap at 18 
                new_value = min(new_value, 18)
                self.game_state.character[stat] = new_value
                applied_adjustments[stat] = adjustment
                print(f"📈 {stat.title()}: {old_value} + {adjustment} = {new_value}")
        
        if applied_adjustments:
            print(f"⚡ {class_info.get('name', character_class.title())} class bonuses applied!")
        
        return applied_adjustments

    def get_available_classes(self):
        """
        Get list of available character classes for future selection screen
        
        Returns:
            list: Available class names
        """
        try:
            class_file = os.path.join("data", "player", "character_classes.json")
            with open(class_file, 'r') as f:
                class_data = json.load(f)
            return list(class_data["character_classes"].keys())
        except Exception as e:
            print(f"❌ Error loading class list: {e}")
            return ['fighter']  # Fallback   

    def set_character_class(self, class_name='fighter'):
        """Set character class with validation"""
        class_data = self._load_class_data_from_json(class_name)
        
        if not class_data:
            print(f"Invalid class {class_name}, defaulting to fighter")
            class_name = 'fighter'
        
        self.game_state.character['class'] = class_name
        
        print(f"⚔️ Character class set to: {class_name}")
        return class_name

    def roll_trinket(self):
        """
        Roll for a mysterious starting trinket using Single Source of Truth pattern
        Trinkets are automatically discovered from items.json (subcategory='trinket')
        No separate trinket table needed - items.json is authoritative
        
        IMPORTANT: Only sets character['trinket'] field - does NOT add to inventory yet
        Inventory addition happens later in finalize_character_creation()
        
        Returns:
            str: Display name of the rolled trinket
        """
        # Verify ItemManager is available (it should be after our initialization fix!)
        if not self.item_manager:
            print("ERROR: ItemManager not available in CharacterEngine - initialization problem!")
            # Emergency fallback
            self.game_state.character['trinket'] = "Small brass key with no lock in sight"
            return self.game_state.character['trinket']
        
        # Query items.json for ALL items with subcategory='trinket'
        all_trinkets = [
            item for item in self.item_manager.items_data.get('merchant_items', [])
            if item.get('subcategory') == 'trinket'
        ]
        
        if not all_trinkets:
            print("ERROR: No trinkets found in items.json! Check data file.")
            # Emergency fallback
            self.game_state.character['trinket'] = "Small brass key with no lock in sight"
            return self.game_state.character['trinket']
        
        # Roll for random trinket 
        selected_trinket = random.choice(all_trinkets)
        trinket_id = selected_trinket.get('id', 'unknown_trinket')  # Get ID, not name
        trinket_name = selected_trinket.get('name', 'Unknown Trinket')  # Get name for display

        # Store ID in character data (inventory uses IDs!)
        self.game_state.character['trinket'] = trinket_id

        print(f"🎲 Rolled trinket: {trinket_name} (id: {trinket_id})")
        return trinket_name  # Return display name for UI
    # ==========================================
    # CHARACTER PROGRESSION OPERATIONS
    # ==========================================
    

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
        max_playable_level = len(self._level_requirements)
        if next_level <= max_playable_level and current_xp >= xp_requirements.get(next_level, 999999):
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
        current_xp = self.game_state.character.get('experience', 0)
        new_level = current_level + 1
        character_class = self.game_state.character.get('class', 'fighter')
     
        xp_requirements = narrative_schema.schema.get('xp_balance', {}).get('level_progression', {}).get('requirements', [0, 300, 900, 2700, 6500])
        print(f"🎊 Level-up! XP remains at {current_xp} (cumulative system)")


        # Get class-specific data
        class_data = self._load_class_data_from_json(character_class)
        hit_die = class_data.get('hit_die', 10) if class_data else 10
        
        constitution_score = self.game_state.character.get('constitution', 10)
        print(f"🔍 DEBUG: About to call _roll_hit_point_gain with hit_die={hit_die}, constitution_score={constitution_score}")
        print(f"🔍 DEBUG: Method exists? {hasattr(self, '_roll_hit_point_gain')}")
        print(f"🔍 DEBUG: Method callable? {callable(getattr(self, '_roll_hit_point_gain', None))}")
        hp_gain, dice_roll, constitution_modifier = self._roll_hit_point_gain(hit_die, constitution_score)
        print(f"DEBUG: HP Roll - 1d{hit_die}({dice_roll}) + CON({constitution_modifier}) = {hp_gain}")

        
        # Get new abilities for this level
        new_abilities = []
        if class_data and 'level_progression' in class_data:
            level_key = f'level_{new_level}'
            level_data = class_data['level_progression'].get(level_key, {})
            new_abilities = level_data.get('features', [])  
        
        # Update character stats in GameState (Single Data Authority)
        self.game_state.character['level'] = new_level
        # Ensure experience field exists and is preserved (don't consume XP)
        self.game_state.character.setdefault('experience', 0)
        
        # Increase max HP
        current_max = self.game_state.character.get('max_hp', 10)
        self.game_state.character['max_hp'] = current_max + hp_gain

         # Level ups fully restore health to the new maximum
        self.game_state.character['current_hp'] = self.game_state.character['max_hp']

        # Track abilities gained
        if 'abilities' not in self.game_state.character:
            self.game_state.character['abilities'] = []
        self.game_state.character['abilities'].extend(new_abilities)
        
        level_up_results = {
            'new_level': new_level,
            'hp_gain': hp_gain,
            'new_total_hp': self.game_state.character['max_hp'],
            'abilities_gained': new_abilities,
            'class': character_class
        }
        
        print(f"🎊 LEVEL UP! Now level {new_level} {character_class.title()}, gained {hp_gain} HP")
        if new_abilities:
            print(f"📚 New abilities: {', '.join(new_abilities)}")
        
        #TODO remove after test.
        # TEST CODE:
        print("🔍 DEBUG: Testing modifier calculation...")
        modifiers = self.calculate_all_modifiers()
        print(f"   Attacks per round: {modifiers['attacks_per_round']}")
        print(f"   Shop price modifier: {modifiers['shop_price_modifier']:.1%}")
        print(f"   Daily abilities: {list(modifiers['daily_abilities'].keys())}")

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
        
        # Track XP statistics by source
        reason_lower = reason.lower()
        if 'combat' in reason_lower or 'defeated' in reason_lower or 'enemy' in reason_lower or 'enemies' in reason_lower:
            self.game_state.player_statistics['xp_from_combat'] += xp_amount
        else:
            self.game_state.player_statistics['xp_from_noncombat'] += xp_amount
        
        print(f"⭐ Awarded {xp_amount} XP! {reason}")
        print(f"   Total XP: {new_xp}")
        
        if xp_amount > 0 and self.event_manager:
            #TODO removed reason text for now, review later for better description
            reason_text = "" #reason.strip() if isinstance(reason, str) else ""  
            message = f"+{xp_amount} XP"
            if reason_text:
                message = f"{message} - {reason_text}"

            try:
                self.event_manager.emit(
                    "SHOW_FLOATING_TEXT",
                    {
                        "text": message,
                        "color": (255, 223, 0),
                        "duration": 2200,
                    },
                )
            except Exception as notification_error:
                print(f"⚠️ Floating text emit failed: {notification_error}")
        
        # Check for level up opportunity
        if self.can_level_up():
            print("🎊 Ready to level up!")
            if self.event_manager:
                self.event_manager.emit("LEVEL_UP_AVAILABLE", {
                    "characters": ["player"],
                    "source": "xp_award"
                })
                self.event_manager.emit("SHOW_FLOATING_TEXT", {
                    "text": "LEVEL UP! Open character sheet.",
                    "color": (50, 255, 50),
                    "duration": 4000,
                })

        return new_xp

    def award_combat_xp(self, enemy_level=1, enemy_count=1):
        """Award XP for combat victories"""
        base_xp = enemy_level * 100
        total_xp = base_xp * enemy_count
        return self.award_experience(total_xp, f"defeated {enemy_count} enemies")
    
    #TODO  does this need to be removed or updated since we have a calculated XP
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
    
    def _handle_quest_completion(self, event_data):
        """Handle quest completion notifications and level-up checks.
        
        NOTE: XP is awarded by QuestEngine before this event is emitted.
        CharacterEngine only needs to check for level-ups.
        """
        quest_id = event_data.get("quest_id")
        quest_title = event_data.get("quest_title", "Unknown Quest")
        # xp_reward is included in event_data but NOT used here (QuestEngine already awarded it)
        
        print(f"🏆 Quest completed: {quest_title}")
        
        # XP already awarded by QuestEngine - just check for level ups
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
                'max_hp': self._get_party_member_starting_hp(member_id)
            }
        
        # Award XP
        current_xp = self.game_state.party_xp[member_id]['experience']
        new_xp = current_xp + xp_amount
        self.game_state.party_xp[member_id]['experience'] = new_xp
        
        print(f"⭐ {member_id.title()} gained {xp_amount} XP! (Total: {new_xp}) - {reason}")
    
    def _award_individual_xp(self, character_id: str, xp_amount: int, reason: str = ""):
        """
        Award XP to a single character (for individual achievements like kills)
        
        Args:
            character_id: 'player' or party member ID
            xp_amount: Amount of XP to award
            reason: Description of why XP was awarded
        """
        if character_id == 'player':
            # Award to main player character
            current_xp = self.game_state.character.get('experience', 0)
            new_xp = current_xp + xp_amount
            self.game_state.character['experience'] = new_xp
            
            # Track XP statistics
            self.game_state.player_statistics['xp_from_combat'] += xp_amount
            
            # Floating notification
            if self.event_manager:
                try:
                    self.event_manager.emit("SHOW_FLOATING_TEXT", {
                        "text": f"+{xp_amount} XP",
                        "color": (255, 223, 0),
                        "duration": 2200,
                    })
                except Exception as e:
                    print(f"⚠️ Floating text failed: {e}")
            
            print(f"⭐ {self.game_state.character.get('name', 'Player')} gained {xp_amount} XP! - {reason}")
            
            # Check for level up
            if self.can_level_up():
                print("🎊 Ready to level up!")
                if self.event_manager:
                    self.event_manager.emit("LEVEL_UP_AVAILABLE", {
                        "characters": ["player"],
                        "source": "xp_award"
                    })
                    self.event_manager.emit("SHOW_FLOATING_TEXT", {
                        "text": "LEVEL UP! Open character sheet.",
                        "color": (50, 255, 50),
                        "duration": 4000,
                    })
        else:
            # Award to specific party member
            self.award_party_member_xp(character_id, xp_amount, reason)
            
            # Check if party member can level up
            level_up_candidates = self.check_party_level_ups()
            if character_id in level_up_candidates:
                print(f"🎊 {character_id.title()} ready to level up!")

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
        member_data = self.game_state.get_party_member_data(member_id)
        if not member_data:
            return False
        current_level = member_data.get('level', 1)
        # current_xp = member_data.get('experience', 0)
        
        # #TODO   Don;t we need to update this hardcoded xp requirements as well??
        # # Use same XP table as player
        # xp_requirements = {1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500}
        current_xp = member_data.get('experience', member_data.get('xp', 0))

        # Mirror the player's XP table pulled from the narrative schema configuration
        xp_requirements = self._level_requirements or [0, 300, 1000]
        
        next_level = current_level + 1
        # if next_level <= 5 and current_xp >= xp_requirements.get(next_level, 999999):
        #     return True
        
        # return False

        if next_level < 1:
            return False

        # Translate the level into a zero-based index for the requirements list
        requirement_index = next_level - 1
        required_xp = None

        if isinstance(xp_requirements, dict):
            required_xp = xp_requirements.get(str(next_level))
            if required_xp is None:
                required_xp = xp_requirements.get(next_level)
            if required_xp is None and xp_requirements:
                required_xp = max(xp_requirements.values())
        else:
            try:
                required_xp = xp_requirements[requirement_index]
            except (IndexError, TypeError):
                required_xp = None

        if required_xp is None:
            # Fall back to a high requirement if the level table is missing entries
            required_xp = 999_999

        return current_xp >= required_xp
    
    def level_up_party_member(self, member_id):
        """Level up a specific party member"""
        member_data = self.game_state.get_party_member_data(member_id)
        if not member_data:
            return False
        current_level = member_data.get('level', 1)
        new_level = current_level + 1
        
        # Ensure the NPC is actually in the active party before leveling
        if member_id not in getattr(self.game_state, 'party_members', []):
            print(f"⚠️ Cannot level {member_id}: not in active party")
            return False

        # Load class data so we can roll HP the same way the player does
        class_name = str(member_data.get('class', '')).lower() or 'fighter'
        class_data = self._load_class_data_from_json(class_name)
        hit_die = class_data.get('hit_die', 10) if class_data else 10

        # Determine constitution modifier from stored stats
        print(f"🔍 DEBUG: member_data keys: {member_data.keys()}")
        print(f"🔍 DEBUG: member_data['constitution']: {member_data.get('constitution')}")
        print(f"🔍 DEBUG: member_data['stats']: {member_data.get('stats')}")

        # Determine constitution modifier from stored stats
        constitution_score = member_data.get('constitution')
        if constitution_score is None:
            constitution_score = member_data.get('stats', {}).get('constitution', 10)

        print(f"🔍 DEBUG: Final constitution_score: {constitution_score}")

        hp_gain, dice_roll, constitution_modifier = self._roll_hit_point_gain(hit_die, constitution_score)
        print(f"DEBUG: NPC HP Roll - 1d{hit_die}({dice_roll}) + CON({constitution_modifier}) = {hp_gain}")

        # Update party member stats
        member_data['level'] = new_level
        
        # Get OLD max HP (not current HP!)
        old_max_hp = member_data.get('max_hp', 10)

        # Calculate NEW max HP
        new_max_hp = old_max_hp + hp_gain

        # Update all HP fields to new maximum
        member_data['max_hp'] = new_max_hp

        # Full heal on level up (same as player)
        member_data['current_hp'] = new_max_hp

        print(f"🎊 {member_id.title()} leveled up! Now level {new_level}, gained {hp_gain} HP to Max HP {new_max_hp}")
        
        return {
            'member_id': member_id,
            'new_level': new_level,
            'hp_gain': hp_gain,
            'new_total_hp': member_data['max_hp']
        }

    def get_trinket_effects(self):
        """Get all active trinket special effects for gameplay bonuses"""
        effects = []
        trinket_name = self.game_state.character.get('trinket')
        
        if trinket_name and self.item_manager:
            # Find trinket in items data by name
            if hasattr(self.item_manager, 'items_data'):
                merchant_items = self.item_manager.items_data.get('merchant_items', [])
                for item in merchant_items:
                    if item.get('name') == trinket_name:
                        special_effect = item.get('special_effect')
                        if special_effect:
                            effects.append(special_effect)
                        break
        
        return effects

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
                          'intelligence', 'wisdom', 'charisma', 'max_hp', 'gold']
        
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

    def _handle_xp_award(self, event_data):
        """Handle XP_AWARDED events from quest/combat/discovery systems"""
        xp_amount = event_data.get('amount', 0)
        reason = event_data.get('reason', 'Unknown')
        recipient = event_data.get('recipient', 'party')  # Default to party
        
        if xp_amount > 0:
            if recipient == 'party':
                # Award to entire party (quests, victory bonuses)
                self.award_party_experience(xp_amount, reason)
            else:
                # Award to specific character (individual kills)
                self._award_individual_xp(recipient, xp_amount, reason)

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
        self.award_experience(xp_amount, reason)
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
        max_playable_level = len(self._level_requirements)
        return (next_level <= max_playable_level and
                current_xp >= xp_requirements.get(next_level, 999999))

    def _get_item_display_name(self, item_id):
        """Convert item ID to display name using ItemManager"""
        if hasattr(self, 'item_manager') and self.item_manager:
            item = self.item_manager.get_item_by_id(item_id)
            if item:
                return item['name']
        return item_id  # Fallback to ID if lookup fails

    def finalize_character_creation(self):
        print("🔧 DEBUG: Starting finalize_character_creation()")
        print(f"DEBUG: Inventory before finalization: {self.game_state.inventory}")
        """
        Complete character creation process with class-specific setup
        Performs final calculations and validations
        """
        character_class = self.game_state.character.get('class', 'fighter')
        
        # Calculate class-specific starting stats
        if 'max_hp' not in self.game_state.character:
            self.calculate_hp()
        
        # Set starting level and XP
        self.game_state.character['level'] = 1
        self.game_state.character['experience'] = 0
        
        # ✅ ADD LEVEL 1 ABILITIES
        class_data = self._load_class_data_from_json(character_class)
        level_1_features = class_data.get('level_1_features', [])
        
        if 'abilities' not in self.game_state.character:
            self.game_state.character['abilities'] = []
        
        self.game_state.character['abilities'].extend(level_1_features)
        print(f"✅ Added Level 1 abilities: {level_1_features}")

        # Roll starting gold based on class
        if 'gold' not in self.game_state.character:
            self.roll_starting_gold()
        
        # Set up starting equipment based on class
        class_data = self._load_class_data_from_json(character_class)
        starting_equipment = class_data.get('starting_equipment', {})
        
        if class_data and 'starting_equipment' in class_data:
            starting_equipment = class_data['starting_equipment']
            
            # Weapons section:
            for weapon_id in starting_equipment.get('weapons', []):
                print(f"🔧 DEBUG: Adding weapon: {weapon_id}")
                if 'weapons' not in self.game_state.inventory:
                    self.game_state.inventory['weapons'] = []
                self.game_state.inventory['weapons'].append(weapon_id)  # Store ID, not name
                # Equip the first weapon
                if not self.game_state.character.get('equipped_weapon'):
                    self.game_state.character['equipped_weapon'] = weapon_id  # Store ID

            # Armor section:
            for armor_id in starting_equipment.get('armor', []):
                print(f"🔧 DEBUG: Adding armor: {armor_id}")
                if 'armor' not in self.game_state.inventory:
                    self.game_state.inventory['armor'] = []
                self.game_state.inventory['armor'].append(armor_id)  # Store ID, not name
                
                # Handle equipping logic
                if armor_id.lower() == 'shield':
                    self.game_state.character['equipped_shield'] = armor_id  # Store ID
                else:
                    self.game_state.character['equipped_armor'] = armor_id  # Store ID
            
            # CAVIA SPECIAL: Replace longsword with shortbow, shield with bracers
            is_cavia = self.game_state.character.get('is_cavia', False)
            if is_cavia:
                print("🐹 Applying Cavia-specific equipment changes...")
                
                # Remove longsword from weapons inventory
                if 'longsword' in self.game_state.inventory.get('weapons', []):
                    self.game_state.inventory['weapons'].remove('longsword')
                    print("  ❌ Removed longsword (too heavy for Cavia)")
                    
                    # Add shortbow instead
                    self.game_state.inventory['weapons'].append('shortbow')
                    print("  ✅ Added shortbow")
                    
                    # Update equipped weapon if longsword was equipped
                    if self.game_state.character.get('equipped_weapon') == 'longsword':
                        self.game_state.character['equipped_weapon'] = 'shortbow'
                        print("  🏹 Equipped shortbow")
                
                # Remove shield from armor inventory
                if 'shield' in self.game_state.inventory.get('armor', []):
                    self.game_state.inventory['armor'].remove('shield')
                    print("  ❌ Removed shield (too heavy for Cavia)")
                    
                    # Add bracers instead
                    self.game_state.inventory['armor'].append('bracers')
                    print("  ✅ Added bracers")
                    
                    # Update equipped shield to bracers as body armor
                    if self.game_state.character.get('equipped_shield') == 'shield':
                        self.game_state.character['equipped_shield'] = None
                        self.game_state.character['equipped_armor'] = 'bracers'
                        print("  🛡️ Equipped bracers as armor")
            
            # Add class-specific items
            for item in starting_equipment.get('items', []):
                if 'items' not in self.game_state.inventory:
                    self.game_state.inventory['items'] = []
                self.game_state.inventory['items'].append(item)
            
            # Add consumables if any
            for consumable in starting_equipment.get('consumables', []):
                if 'consumables' not in self.game_state.inventory:
                    self.game_state.inventory['consumables'] = []
                self.game_state.inventory['consumables'].append(consumable)
        
        # Add trinket to inventory 
        trinket = self.game_state.character.get('trinket')
        if trinket and trinket != 'None':
            if 'items' not in self.game_state.inventory:
                self.game_state.inventory['items'] = []
            
            # CHECK IF TRINKET ALREADY EXISTS IN INVENTORY
            if trinket not in self.game_state.inventory['items']:
                self.game_state.inventory['items'].append(trinket)
                print(f"🔧 DEBUG: Added trinket to inventory: {trinket}")
        
        # Set up spells for casters
        if class_data and 'spells_known' in class_data:
            self.game_state.character['spells'] = class_data['spells_known'].copy()
        
        # Validate the completed character
        is_valid = self.validate_character()
        print(f"DEBUG: Inventory after finalization: {self.game_state.inventory}")
        if is_valid:
            print("✅ Character creation finalized successfully!")
            char_name = self.game_state.character.get('name', 'Unknown Hero')
            char_class = self.game_state.character.get('class', 'fighter').title()
            print(f"DEBUG: Inventory after finalization: {self.game_state.inventory}")
            print(f"🎭 Welcome to Redstone, {char_name} the {char_class}!")
        else:
            print("❌ Character creation validation failed!")
        
        return is_valid
    # ==========================================
    # CONSOLIDATED MODIFIER CALCULATER USED TO 
    # PUSH CHARACTER ABILITIES AND EFFECTS TO 
    # COMBAT AND OTHER ENGINES
    # ========================================== 

    def calculate_all_modifiers(self):
        """
        THE UNIFIED MODIFIER CALCULATOR
        Parses character abilities and stats to return all game modifiers
        
        This is the single source of truth for all character effects.
        Every system (combat, shopping, dialogue, skills) uses this.
        
        Returns:
            dict: Complete modifier object with all game effects
        """
        abilities = self.game_state.character.get('abilities', [])
        base_stats = self.game_state.character
        
        # Start with base modifiers - everything defaults to 0/empty
        modifiers = {
            # Combat modifiers
            'attacks_per_round': 1,
            'ac_bonus': 0,
            'damage_bonus': 0,
            'hit_bonus': 0,
            
            # Social modifiers  
            'shop_price_modifier': 0.0,  # -0.1 = 10% discount
            'dialogue_charisma_bonus': 0,
            'intimidation_bonus': 0,
            
            # Exploration modifiers
            'movement_bonus': 0,
            'trap_detection_bonus': 0,
            'search_bonus': 0,
            
            # Magic modifiers (for future spellcasters)
            'spell_slot_bonus': 0,
            'spell_save_dc_bonus': 0,
            'spell_damage_bonus': 0,
            
            # Saving throw bonuses
            'fear_save_bonus': 0,
            'poison_save_bonus': 0,
            'magic_save_bonus': 0,
            
            # Daily abilities available (use tracking)
            'daily_abilities': {},
            
            # Ability score bonuses from class features
            'ability_score_bonuses': {}
        }
        
        # Parse each ability for its mechanical effects
        for ability in abilities:
            if ability == "Extra Attack":
                modifiers['attacks_per_round'] = 2
                
            elif ability == "Combat Surge":
                modifiers['daily_abilities']['Combat Surge'] = {
                    'uses_remaining': 1,  # TODO: Track daily resets
                    'effect': 'Take an extra action once per day',
                    'type': 'combat_action'
                }
                
            elif ability == "Shield Focus":
                modifiers['daily_abilities']['Shield Focus'] = {
                    'uses_remaining': 1,  # TODO: Track daily resets  
                    'effect': '+1 AC for one entire combat encounter',
                    'type': 'defensive_bonus'
                }
                
            elif ability == "Terror Resistance":
                modifiers['fear_save_bonus'] = 1
                
            # Future abilities can be added here easily:
            # elif ability == "Silver Tongue":  # hypothetical charisma ability
            #     modifiers['shop_price_modifier'] -= 0.1  # 10% discount
            #     modifiers['dialogue_charisma_bonus'] += 2
            #     
            # elif ability == "Weapon Mastery":  # hypothetical combat ability
            #     modifiers['hit_bonus'] += 1
            #     modifiers['damage_bonus'] += 2
        
        # Add base stat modifiers (D&D style ability modifiers)
        strength = base_stats.get('strength', 10)
        dexterity = base_stats.get('dexterity', 10)
        constitution = base_stats.get('constitution', 10)
        intelligence = base_stats.get('intelligence', 10)
        wisdom = base_stats.get('wisdom', 10)
        charisma = base_stats.get('charisma', 10)
        
        # Calculate D&D-style ability modifiers
        str_mod = (strength - 10) // 2
        dex_mod = (dexterity - 10) // 2
        con_mod = (constitution - 10) // 2
        int_mod = (intelligence - 10) // 2
        wis_mod = (wisdom - 10) // 2
        cha_mod = (charisma - 10) // 2
        
        # Apply stat-based modifiers
        modifiers['damage_bonus'] += str_mod  # STR affects melee damage
        modifiers['hit_bonus'] += str_mod     # STR affects melee accuracy
        modifiers['ac_bonus'] += dex_mod      # DEX affects AC (if wearing light armor)
        modifiers['shop_price_modifier'] += (cha_mod * 0.05)  # CHA affects prices (5% per modifier)
        modifiers['dialogue_charisma_bonus'] += cha_mod
        modifiers['search_bonus'] += int_mod   # INT affects finding things
        modifiers['trap_detection_bonus'] += wis_mod  # WIS affects noticing traps
        
        return modifiers
    
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

def initialize_character_engine(game_state_ref, event_manager=None, item_manager_ref=None):
    """
    Initialize the global character engine with event management
    """
    global character_engine
    character_engine = CharacterEngine(game_state_ref, event_manager, item_manager_ref)
    
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