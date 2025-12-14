#!/usr/bin/env python3
"""
Terror in Redstone - Dialogue Tester
Console tool for testing NPC and object dialogue flows with flag manipulation
"""

import json
import os
from pathlib import Path

class DialogueTester:
    def __init__(self, dialogue_dir="data/dialogues", schema_path="data/narrative_schema.json"):
        self.dialogue_dir = Path(dialogue_dir)
        self.schema_path = Path(schema_path)
        self.current_dialogue = None
        self.current_state = None
        self.flags = {}
        self.narrative_schema = {}
        self.is_object = False
        self.npc_id = None
        
        # Load narrative schema if available
        if self.schema_path.exists():
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    self.narrative_schema = json.load(f)
                print(f"✓ Loaded narrative_schema.json")
            except Exception as e:
                print(f"⚠ Could not load narrative schema: {e}")
        else:
            print(f"Note: Narrative schema not found at {schema_path} (optional)")
    
    def list_npcs(self):
        """List all available NPC dialogue files"""
        if not self.dialogue_dir.exists():
            print(f"\nERROR: Dialogue directory not found!")
            print(f"  Looking for: {self.dialogue_dir.absolute()}")
            print(f"  Current working directory: {Path.cwd()}")
            return []
        
        if not self.dialogue_dir.is_dir():
            print(f"\nERROR: Path is not a directory!")
            print(f"  You entered: {self.dialogue_dir}")
            print(f"  Tip: Enter the FOLDER path, not a file path")
            return []
        
        npc_files = sorted([f.stem for f in self.dialogue_dir.glob("*.json")])
        
        if not npc_files:
            print(f"\nWARNING: No .json files found in {self.dialogue_dir.absolute()}")
        
        return npc_files
        
    
    def load_dialogue(self, npc_name):
        """Load dialogue JSON and discover all flags"""
        file_path = self.dialogue_dir / f"{npc_name}.json"
        
        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_dialogue = json.load(f)
            
            self.npc_id = npc_name
            self.is_object = self.current_dialogue.get("is_object", False)
            
            print(f"\n{'='*60}")
            print(f"Loaded: {npc_name}.json")
            print(f"Type: {'OBJECT' if self.is_object else 'NPC'}")
            
            # Discover all flags used in this dialogue
            discovered_flags = self._discover_flags()
            
            # Initialize all flags to False
            self.flags = {flag: False for flag in discovered_flags}
            
            print(f"Discovered {len(self.flags)} flags:")
            for flag in sorted(self.flags.keys()):
                print(f"  - {flag}")
            
            # Set starting state
            # For NPCs, check narrative schema for initial state
            # For objects, use initial_state field from JSON
            if self.is_object:
                self.current_state = self.current_dialogue.get("initial_state", "examine")
            else:
                self.current_state = self._get_initial_npc_state()
            
            print(f"Initial state: {self.current_state}")
            
            return True
            
        except Exception as e:
            print(f"ERROR loading dialogue: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_initial_npc_state(self):
        """Get initial NPC state from narrative schema or default to first_meeting"""
        if not self.narrative_schema:
            return "first_meeting"
        
        # Check dialogue_state_mapping in narrative schema
        dialogue_states = self.narrative_schema.get('dialogue_state_mapping', {})
        npc_states = dialogue_states.get(self.npc_id, {})
        
        if not npc_states:
            return "first_meeting"
        
        # The first state in the mapping order is the initial state
        # (assuming flags are all False at start)
        for state_name, condition in npc_states.items():
            # Check if this is the "first meeting" condition (usually something like "!npc_talked")
            if self._evaluate_simple_condition(condition):
                return state_name
        
        return "first_meeting"
    
    def _evaluate_simple_condition(self, condition):
        """Simple condition evaluator for initial state check"""
        if not condition:
            return True
        
        # For initial state, assume all flags are False
        # So "!flag" would be True, "flag" would be False
        condition = condition.replace('&&', ' and ').replace('||', ' or ')
        
        tokens = condition.split()
        for i, token in enumerate(tokens):
            if token.startswith("!"):
                tokens[i] = "True"  # !flag is True when flag is False
            elif token not in ["and", "or", "(", ")"]:
                tokens[i] = "False"  # flag is False at start
        
        try:
            return eval(" ".join(tokens))
        except:
            return False
    
    def _discover_flags(self):
        """Scan dialogue for all flag references in requirements and effects"""
        flags = set()
        
        if "states" not in self.current_dialogue:
            return flags
        
        for state_id, state_data in self.current_dialogue["states"].items():
            # Check requirements in options
            if "options" in state_data:
                for option in state_data["options"]:
                    # Requirements
                    requirements = option.get("requirements", {})
                    
                    # Nested flags: {"flags": {"flag_name": true/false}}
                    if "flags" in requirements:
                        for flag_name in requirements["flags"].keys():
                            flags.add(flag_name)
                    
                    # Single flag: {"flag": "flag_name"}
                    if "flag" in requirements:
                        flags.add(requirements["flag"])
                    
                    # Not flag: {"not_flag": "flag_name"}
                    if "not_flag" in requirements:
                        flags.add(requirements["not_flag"])
                    
                    # Any flag: {"any_flag": ["flag1", "flag2"]}
                    if "any_flag" in requirements:
                        for flag_name in requirements["any_flag"]:
                            flags.add(flag_name)
                    
                    # Effects
                    for effect in option.get("effects", []):
                        if isinstance(effect, dict):
                            # set_flag effect
                            if effect.get("type") == "set_flag":
                                flag_name = effect.get("flag")
                                if flag_name:
                                    flags.add(flag_name)
        
        return flags
    
    def display_state(self):
        """Display current dialogue state with flag states and options"""
        if not self.current_dialogue or not self.current_state:
            print("No dialogue loaded!")
            return
        
        states = self.current_dialogue.get("states", {})
        state_data = states.get(self.current_state)
        
        if not state_data:
            print(f"ERROR: State '{self.current_state}' not found!")
            return
        
        # Header
        print(f"\n{'='*60}")
        print(f"CURRENT STATE: {self.current_state}")
        print(f"{'='*60}")
        
        # NPC/Object dialogue text (introduction array)
        introduction = state_data.get("introduction", [])
        if introduction:
            print()
            for line in introduction:
                print(f"  {line}")
            print()
        
        # Display flag states
        self._display_flags()
        
        # Display options
        options = state_data.get("options", [])
        
        if not options:
            print("\n[END OF CONVERSATION]")
            return
        
        print(f"\n{'─'*60}")
        print("OPTIONS:")
        print(f"{'─'*60}")
        
        for idx, option in enumerate(options, 1):
            option_text = option.get("text", "[No text]")
            next_state = option.get("next_state", "exit")
            requirements = option.get("requirements", {})
            effects = option.get("effects", [])
            
            # Check if requirements are met
            req_met, missing = self._check_requirements(requirements)
            status = "✓" if req_met else "✗"
            
            print(f"\n[{idx}] {status} \"{option_text}\"")
            print(f"    → Next: {next_state}")
            
            # Show requirements
            if requirements:
                req_display = self._format_requirements(requirements)
                print(f"    Requirements: {req_display}")
                if not req_met:
                    print(f"    ❌ BLOCKED - Missing: {missing}")
            
            # Show effects
            if effects:
                effects_display = self._format_effects(effects)
                print(f"    Effects: {effects_display}")
                
                # Show narrative schema mapping if available (for NPCs)
                if not self.is_object:
                    self._show_schema_mapping(effects)
    
    def _format_requirements(self, requirements):
        """Format requirements dict into readable string"""
        parts = []
        
        if "flags" in requirements:
            for flag, value in requirements["flags"].items():
                parts.append(f"{flag}={value}")
        
        if "flag" in requirements:
            parts.append(f"{requirements['flag']}=True")
        
        if "not_flag" in requirements:
            parts.append(f"{requirements['not_flag']}=False")
        
        if "any_flag" in requirements:
            flags = ", ".join(requirements["any_flag"])
            parts.append(f"any_of({flags})")
        
        if "race" in requirements:
            parts.append(f"race={requirements['race']}")
        
        if "item" in requirements:
            item_id = requirements["item"]
            qty = requirements.get("quantity", 1)
            qty_text = f"{qty}x " if qty > 1 else ""
            parts.append(f"has {qty_text}{item_id}")
        
        if "not_item" in requirements:
            parts.append(f"!has {requirements['not_item']}")
        
        return ", ".join(parts) if parts else "None"
    
    def _format_effects(self, effects):
        """Format effects array into readable string"""
        parts = []
        
        for effect in effects:
            if not isinstance(effect, dict):
                continue
            
            effect_type = effect.get("type", "unknown")
            
            if effect_type == "set_flag":
                flag = effect.get("flag")
                value = effect.get("value", True)
                parts.append(f"set {flag}={value}")
            
            elif effect_type == "add_item":
                item_id = effect.get("item_id")
                qty = effect.get("quantity", 1)
                parts.append(f"give {qty}x {item_id}")
            
            elif effect_type == "remove_item":
                item_id = effect.get("item_id")
                qty = effect.get("quantity", 1)
                parts.append(f"take {qty}x {item_id}")
            
            elif effect_type in ["add_gold", "award_gold"]:
                amount = effect.get("amount", 0)
                parts.append(f"give {amount} gold")
            
            elif effect_type == "spend_gold":
                amount = effect.get("amount", 0)
                parts.append(f"spend {amount} gold")
            
            elif effect_type == "open_shop":
                merchant = effect.get("merchant_id", "shop")
                parts.append(f"open shop: {merchant}")
            
            elif effect_type == "start_combat":
                encounter = effect.get("encounter_id", "?")
                parts.append(f"START COMBAT: {encounter}")
            
            else:
                parts.append(effect_type)
        
        return ", ".join(parts) if parts else "None"
    
    def _show_schema_mapping(self, effects):
        """Show narrative schema XP/flag mappings if available"""
        if not self.narrative_schema:
            return
        
        # Look for set_flag effects and check schema
        for effect in effects:
            if effect.get("type") == "set_flag":
                flag_name = effect.get("flag")
                
                # Check if this flag triggers XP in schema
                # This is simplified - actual schema structure may vary
                # You can enhance this based on your actual schema structure
                pass
    
    def _check_requirements(self, requirements):
        """Check if requirements are met, return (met, missing_description)"""
        if not requirements:
            return True, []
        
        missing = []
        
        # Check nested flags: {"flags": {"flag_name": true/false}}
        if "flags" in requirements:
            for flag_name, required_value in requirements["flags"].items():
                current_value = self.flags.get(flag_name, False)
                if current_value != required_value:
                    missing.append(f"{flag_name}={required_value}")
        
        # Check single flag: {"flag": "flag_name"} - must be True
        if "flag" in requirements:
            flag_name = requirements["flag"]
            if not self.flags.get(flag_name, False):
                missing.append(f"{flag_name}=True")
        
        # Check not_flag: {"not_flag": "flag_name"} - must be False
        if "not_flag" in requirements:
            flag_name = requirements["not_flag"]
            if self.flags.get(flag_name, False):
                missing.append(f"{flag_name}=False")
        
        # Check any_flag: {"any_flag": ["flag1", "flag2"]} - at least one must be True
        if "any_flag" in requirements:
            flag_list = requirements["any_flag"]
            if not any(self.flags.get(flag, False) for flag in flag_list):
                missing.append(f"any_of({', '.join(flag_list)})")
        
        # Race and item checks - we can't really test these without full game state
        # But we'll note them in the missing list if present
        if "race" in requirements:
            # In real game, would check player race
            # For testing, just note it's required
            pass  # We'll assume race checks pass for testing
        
        if "item" in requirements:
            # In real game, would check inventory
            pass  # We'll assume item checks pass for testing
        
        if "not_item" in requirements:
            pass  # We'll assume not_item checks pass for testing
        
        return len(missing) == 0, missing
    
    def _display_flags(self):
        """Display current flag states"""
        print("\n" + "─"*60)
        print("FLAG STATES:")
        print("─"*60)
        
        if not self.flags:
            print("  [No flags discovered]")
            return
        
        # Display in columns
        flag_list = sorted(self.flags.items())
        for flag, value in flag_list:
            status = "☑" if value else "☐"
            print(f"  {status} {flag} = {value}")
    
    def select_option(self, choice):
        """Select an option and move to next state"""
        states = self.current_dialogue.get("states", {})
        state_data = states.get(self.current_state)
        
        if not state_data:
            return False
        
        options = state_data.get("options", [])
        
        if choice < 1 or choice > len(options):
            print("Invalid choice!")
            return False
        
        option = options[choice - 1]
        
        # Check requirements
        requirements = option.get("requirements", {})
        req_met, missing = self._check_requirements(requirements)
        
        if not req_met:
            print(f"\n❌ Cannot select - Requirements not met: {missing}")
            return False
        
        # Apply effects
        effects = option.get("effects", [])
        if effects:
            print(f"\n🔧 Applying effects:")
            for effect in effects:
                self._apply_effect(effect)
        
        # Move to next state
        next_state = option.get("next_state", "exit")
        
        if next_state == "exit":
            print("\n[CONVERSATION ENDED]")
            self.current_state = None
            return False
        
        self.current_state = next_state
        return True
    
    def _apply_effect(self, effect):
        """Apply a dialogue effect (mainly flag changes for testing)"""
        if not isinstance(effect, dict):
            return
        
        effect_type = effect.get("type")
        
        if effect_type == "set_flag":
            flag_name = effect.get("flag")
            value = effect.get("value", True)
            if flag_name and flag_name in self.flags:
                self.flags[flag_name] = value
                print(f"   Set {flag_name} = {value}")
        
        elif effect_type in ["add_item", "remove_item", "add_gold", "spend_gold", "open_shop", "start_combat"]:
            print(f"   {effect_type}: (game effect, not simulated in tester)")
        
        else:
            print(f"   {effect_type}: (unknown effect type)")
    
    def toggle_flags_menu(self):
        """Display menu to toggle individual flags"""
        while True:
            print(f"\n{'='*60}")
            print("FLAG TOGGLE MENU")
            print(f"{'='*60}")
            
            flag_list = sorted(self.flags.items())
            for idx, (flag, value) in enumerate(flag_list, 1):
                status = "☑" if value else "☐"
                print(f"[{idx}] {status} {flag} = {value}")
            
            print(f"\n[a] Toggle ALL ON")
            print(f"[o] Toggle ALL OFF")
            print(f"[b] Back to dialogue")
            
            choice = input("\nSelect flag number (or command): ").strip().lower()
            
            if choice == 'b':
                # Auto-refresh display when exiting flag menu
                print("\n✓ Flags updated - returning to dialogue...")
                print("💡 TIP: Options with ✓ are now available, ✗ are blocked by requirements")
                break
            elif choice == 'a':
                for flag in self.flags:
                    self.flags[flag] = True
                print("✓ All flags set to TRUE")
            elif choice == 'o':
                for flag in self.flags:
                    self.flags[flag] = False
                print("✓ All flags set to FALSE")
            elif choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(flag_list):
                    flag = flag_list[idx - 1][0]
                    self.flags[flag] = not self.flags[flag]
                    status = self.flags[flag]
                    print(f"✓ Toggled {flag} = {status}")
                else:
                    print("Invalid selection!")
    
    def recalculate_state(self):
        """Recalculate which state we should be in based on current flags (for NPCs with narrative schema)"""
        if self.is_object:
            print("⚠ Objects don't use state recalculation - they follow manual state transitions")
            return
        
        if not self.narrative_schema:
            print("⚠ No narrative schema loaded - can't recalculate state")
            return
        
        # Get dialogue state mapping for this NPC
        dialogue_states = self.narrative_schema.get('dialogue_state_mapping', {})
        npc_states = dialogue_states.get(self.npc_id, {})
        
        if not npc_states:
            print(f"⚠ No state mapping found for {self.npc_id} in narrative schema")
            return
        
        old_state = self.current_state
        
        # Evaluate conditions to find matching state
        for state_name, condition in npc_states.items():
            if self._evaluate_condition(condition):
                self.current_state = state_name
                if self.current_state != old_state:
                    print(f"✓ State changed: {old_state} → {self.current_state}")
                else:
                    print(f"✓ State remains: {self.current_state}")
                return
        
        print(f"⚠ No matching state found - staying in {old_state}")
    
    def list_all_states(self):
        """Show all states available in the dialogue file"""
        if not self.current_dialogue:
            print("No dialogue loaded!")
            return
        
        states = self.current_dialogue.get("states", {})
        print(f"\n{'='*60}")
        print(f"ALL STATES IN {self.npc_id}")
        print(f"{'='*60}")
        
        for state_name in states.keys():
            current_marker = " ← CURRENT" if state_name == self.current_state else ""
            print(f"  • {state_name}{current_marker}")
        
        print(f"\n💡 TIP: Different states have different options!")
        print(f"   Use dialogue choices to navigate between states,")
        print(f"   or use [s] to recalculate state based on flags.")
    
    def jump_to_state(self):
        """Manually jump to a state for testing purposes"""
        if not self.current_dialogue:
            print("No dialogue loaded!")
            return
        
        states = self.current_dialogue.get("states", {})
        state_list = list(states.keys())
        
        print(f"\n{'='*60}")
        print("JUMP TO STATE (Testing Only)")
        print(f"{'='*60}")
        
        for idx, state_name in enumerate(state_list, 1):
            current_marker = " ← CURRENT" if state_name == self.current_state else ""
            print(f"[{idx}] {state_name}{current_marker}")
        
        print(f"\n[b] Back")
        
        choice = input("\nSelect state number: ").strip()
        
        if choice.lower() == 'b':
            return
        
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(state_list):
                old_state = self.current_state
                self.current_state = state_list[idx - 1]
                print(f"✓ Jumped from {old_state} → {self.current_state}")
            else:
                print("Invalid selection!")
    
    def _evaluate_condition(self, condition):
        """Evaluate narrative schema condition string against current flags"""
        if not condition:
            return True
        
        # Replace operators
        condition = condition.replace('&&', ' and ').replace('||', ' or ')
        
        # Build context with current flag values
        context = {}
        for flag_name, flag_value in self.flags.items():
            context[flag_name] = flag_value
        
        # Parse tokens
        tokens = condition.split()
        for i, token in enumerate(tokens):
            if token.startswith("!"):
                # Negation
                flag_name = token[1:]
                flag_value = context.get(flag_name, False)
                tokens[i] = str(not flag_value)
            elif token not in ["and", "or", "(", ")"]:
                # Flag reference
                flag_value = context.get(token, False)
                tokens[i] = str(flag_value)
        
        try:
            result = eval(" ".join(tokens))
            return result
        except Exception as e:
            print(f"⚠ Error evaluating condition '{condition}': {e}")
            return False
    
    def reset(self):
        """Reset to initial state and clear flags"""
        if self.current_dialogue:
            if self.is_object:
                self.current_state = self.current_dialogue.get("initial_state", "examine")
            else:
                self.current_state = self._get_initial_npc_state()
            
            for flag in self.flags:
                self.flags[flag] = False
            print("\n✓ Reset to initial state, all flags cleared")

def main():
    """Main loop for dialogue tester"""
    print("="*60)
    print("TERROR IN REDSTONE - DIALOGUE TESTER")
    print("="*60)
    print("\nTip: Enter FOLDER paths, not file paths!")
    print("Example: data/dialogues (NOT data/dialogues/somefile.json)\n")
    
    # Get dialogue directory from user
    dialogue_dir = input("Enter dialogue directory path (default: data/dialogues): ").strip()
    if not dialogue_dir:
        dialogue_dir = "data/dialogues"
    
    schema_path = input("Enter narrative_schema.json path (default: data/narrative_schema.json): ").strip()
    if not schema_path:
        schema_path = "data/narrative_schema.json"
    
    tester = DialogueTester(dialogue_dir, schema_path)
    
    # List NPCs
    npcs = tester.list_npcs()
    
    if not npcs:
        print("No NPC dialogue files found!")
        return
    
    print("\nAvailable NPCs:")
    for idx, npc in enumerate(npcs, 1):
        print(f"  {idx}. {npc}")
    
    # Select NPC
    while True:
        choice = input("\nSelect NPC number (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            return
        
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(npcs):
                npc = npcs[idx - 1]
                if tester.load_dialogue(npc):
                    break
        
        print("Invalid selection!")
    
    # Main dialogue loop
    while True:
        tester.display_state()
        
        if not tester.current_state:
            # Conversation ended
            choice = input("\n[r] Reset | [q] Quit: ").strip().lower()
            if choice == 'r':
                tester.reset()
            else:
                break
            continue
        
        print(f"\n{'─'*60}")
        print("Commands:")
        print("  [1-9] Select option")
        print("  [f] Toggle flags")
        print("  [s] Recalculate state (checks narrative schema with current flags)")
        print("  [v] View all states")
        print("  [j] Jump to state (testing only)")
        print("  [r] Reset")
        print("  [q] Quit")
        choice = input("> ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'f':
            tester.toggle_flags_menu()
            # Auto-refresh display after flag changes
            continue
        elif choice == 's':
            tester.recalculate_state()
        elif choice == 'v':
            tester.list_all_states()
        elif choice == 'j':
            tester.jump_to_state()
        elif choice == 'r':
            tester.reset()
        elif choice.isdigit():
            tester.select_option(int(choice))

if __name__ == "__main__":
    main()