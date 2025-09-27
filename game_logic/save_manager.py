
import json
import os
from datetime import datetime
from utils.constants import SAVE_LOAD_RESTRICTED_SCREENS

class SaveManager:
    """
    Handles all save/load operations for Terror in Redstone
    Extracted from GameController to follow Single Responsibility Principle
    """
    def __init__(self, game_state, character_engine=None, event_manager=None, quest_engine=None):
        self.game_state = game_state
        self.character_engine = character_engine
        self.event_manager = event_manager
        self.quest_engine = quest_engine
        
        # Register for save info events
        if event_manager:
            event_manager.register("SAVE_INFO_REQUESTED", self.handle_save_info_request)
            event_manager.register("SAVE_REQUESTED", self._handle_quicksave_request)
            print("📡 SaveManager registered for SAVE_INFO_REQUESTED events")
        else:
            print("❌ SaveManager: No event_manager provided - event registration skipped!")  
        
        # Register load screen events  
        self.register_load_screen_events()

        # Register save screen events
        self.register_save_screen_events()

        print("💾 SaveManager initialized - Professional save/load system ready!")
        
    def save_game(self, save_slot=1):
        
        """
        Save complete game state to JSON file
        save_slot: 1-3 for manual saves, 0 for auto-save
        """
       # Quest system data 
        quest_system_data = {}
        if hasattr(self.game_state, 'quest_manager') and self.game_state.quest_manager:
            quest_system_data = self.game_state.quest_manager.get_quest_data_for_save()
            
        try:
            # Collect all game state data
            save_data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'save_slot': save_slot,

                # Character data
                'character': self.game_state.character,
                'inventory': self.game_state.inventory,
                
                # Quest system data (ADD THIS LINE)
                'quest_system': quest_system_data,

                # Game progression
                'current_screen': self.game_state.screen,
                'screen_history': [],  # Screen history not tracked by SaveManager
                'previous_screen': getattr(self.game_state, 'previous_screen', None),
                
                # World state
                'party_members': getattr(self.game_state, 'party_members', []),
                'tavern_visits': getattr(self.game_state, 'tavern_visits', 0),
                'locations_discovered': getattr(self.game_state, 'locations_discovered', []),
                
                # Quest and NPC states
                'quest_flags': getattr(self.game_state, 'quest_flags', {}),
                'npc_recruitment_status': getattr(self.game_state, 'npc_recruitment_status', {}),
                'conversations_had': getattr(self.game_state, 'conversations_had', []),
                'mayor_talked': getattr(self.game_state, 'mayor_talked', False),
                'mayor_mentioned': getattr(self.game_state, 'mayor_mentioned', False),
                'pete_attempted_recruitment': getattr(self.game_state, 'pete_attempted_recruitment', False),
                'pete_showing_comedy': getattr(self.game_state, 'pete_showing_comedy', False),
                'meredith_talked': getattr(self.game_state, 'meredith_talked', False),
                'garrick_talked': getattr(self.game_state, 'garrick_talked', False),
                'learned_about_church': getattr(self.game_state, 'learned_about_church', False),
                'learned_about_ruins': getattr(self.game_state, 'learned_about_ruins', False),
                'quest_active': getattr(self.game_state, 'quest_active', False),
                'just_got_quest': getattr(self.game_state, 'just_got_quest', False),
                'quest_system': self.game_state.quest_manager.get_quest_data_for_save() if hasattr(self.game_state, 'quest_manager') and self.game_state.quest_manager else {},
                'showing_meredith_response':getattr(self.game_state, 'showing_meredith_response', False),
                'showing_garrick_response':getattr(self.game_state, 'showing_garrick_response', False),

                # Dice game state
                'dice_game': getattr(self.game_state, 'dice_game', {}),
            
                # Shopping cart state
                'shopping_cart': getattr(self.game_state, 'shopping_cart', {}),
                
                # Gambling and economy
                'house_money': getattr(self.game_state, 'house_money', 50),
                'gambling_wins': getattr(self.game_state, 'gambling_wins', 0),
                'gambling_losses': getattr(self.game_state, 'gambling_losses', 0),
                
                # Equipment state
                'equipped_weapon': getattr(self.game_state, 'equipped_weapon', None),
                'equipped_armor': getattr(self.game_state, 'equipped_armor', None),
                'equipped_shield': getattr(self.game_state, 'equipped_shield', None),
            }
            
            # *** Save all narrative schema flags dynamically ***
            narrative_flags = {}
            try:
                from utils.narrative_schema import narrative_schema
                all_flags = narrative_schema.get_all_flags()
                
                # Filter out None values and collect flag states
                for flag_name in all_flags:
                    if flag_name:  # Skip None/empty flags
                        flag_value = getattr(self.game_state, flag_name, False)
                        narrative_flags[flag_name] = bool(flag_value)  # Ensure boolean
                
                print(f"💾 Saving {len(narrative_flags)} narrative flags")
                
                # Debug: Show some key flags being saved
                key_flags = ['mayor_talked', 'quest_active', 'gareth_recruited']
                for flag in key_flags:
                    if flag in narrative_flags:
                        print(f"   💾 {flag}: {narrative_flags[flag]}")
                        
            except ImportError:
                print("⚠️ Narrative schema not available for save - using manual collection")
                # Fallback to manual flag collection for backward compatibility
                manual_flags = [
                    'mayor_talked', 'garrick_talked', 'meredith_talked', 'pete_talked',
                    'gareth_talked', 'elara_talked', 'thorman_talked', 'lyra_talked',
                    'quest_active', 'gareth_recruited', 'elara_recruited', 
                    'thorman_recruited', 'lyra_recruited',
                    'learned_about_swamp_church', 'learned_about_ruins', 'learned_about_refugees',
                    'main_quest_completed', 'reported_main_quest'
                ]
                
                for flag_name in manual_flags:
                    flag_value = getattr(self.game_state, flag_name, False)
                    narrative_flags[flag_name] = bool(flag_value)
            
            except Exception as e:
                print(f"❌ Error collecting narrative flags for save: {e}")
                # Continue with empty narrative_flags - save will still work
            
            # Add narrative flags to save data
            save_data['narrative_flags'] = narrative_flags
            
            # *** Also save computed properties for verification ***
            save_data['computed_data'] = {
                'recruited_count': len(getattr(self.game_state, 'party_members', [])),
                'party_members': getattr(self.game_state, 'party_members', []),
                'can_recruit_more': len(getattr(self.game_state, 'party_members', [])) < 3
            }
            # Ensure XP is saved properly
            if 'experience' not in save_data['character']:
                save_data['character']['experience'] = self.game_state.character.get('experience', 0)

            # Create saves directory if it doesn't exist
            #os.makedirs('saves', exist_ok=True)
            
            # Determine save file name
            if save_slot == 0:
                filename = 'saves/autosave.json'
                save_type = "Auto-save"
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
                save_type = "Quick save"
            else:
                filename = f'saves/save_slot_{save_slot}.json'
                save_type = f"Manual save (Slot {save_slot})"
            
            # Write save file
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            print(f"✅ {save_type} completed successfully")
            print(f"   Character: {self.game_state.character.get('name', 'Unknown')}")
            print(f"   Location: {self.game_state.screen}")
            print(f"   Party size: {len(self.game_state.party_members) + 1}")
            print(f"   Narrative flags: {len(narrative_flags)}")
        
            # Update GameController state tracking
            self.last_save_time = datetime.now()
                        
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            
            return False

    def load_game(self, save_slot=1):
        """
        Load game state from JSON file and restore game to saved state
        save_slot: 1-3 for manual saves, 0 for auto-save
        """
        import os
        import shutil
        import json
        from datetime import datetime

        try:
            # Determine save file name
            if save_slot == 0:
                filename = 'saves/autosave.json'
                save_type = "Auto-save"
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
                save_type = 'Quick Save'
            else:
                filename = f'saves/save_slot_{save_slot}.json'
                save_type = f"Save slot {save_slot}"
            
            # Check if save file exists
            if not os.path.exists(filename):
                print(f"❌ No save file found: {filename}")
                return False
            
            # Load save data
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            print(f"📁 Loading {save_type}...")
            print(f"   Saved: {save_data.get('timestamp', 'Unknown time')}")
            print(f"   Version: {save_data.get('version', 'Unknown')}")
            
                # Restore character data (GameState is the authority!)
            if 'character' in save_data:
                self.game_state.character = save_data['character']
                print(f"   🎭 Character: {self.game_state.character.get('name', 'Unknown')}")
            
            if 'inventory' in save_data:
                self.game_state.inventory = save_data['inventory']
                print(f"   💰 Gold: {self.game_state.character.get('gold', 0)}")
            
            # Restore game progression
            self.game_state.screen = save_data.get('current_screen', 'broken_blade_main')
            
            # Restore world state
            self.game_state.party_members = save_data.get('party_members', [])
            self.game_state.tavern_visits = save_data.get('tavern_visits', 0)
            self.game_state.locations_discovered = save_data.get('locations_discovered', [])
            
            # Restore quest and NPC states
            self.game_state.quest_flags = save_data.get('quest_flags', {})
            self.game_state.npc_recruitment_status = save_data.get('npc_recruitment_status', {})
            self.game_state.conversations_had = save_data.get('conversations_had', [])
            self.game_state.mayor_talked = save_data.get('mayor_talked', False)
            self.game_state.meredith_talked = save_data.get('meredith_talked', False)
            self.game_state.garrick_talked = save_data.get('garrick_talked', False)  
            self.game_state.learned_about_church = save_data.get('learned_about_church', False)
            self.game_state.learned_about_ruins = save_data.get('learned_about_ruins', False)
            self.game_state.quest_active = save_data.get('quest_active', False)
            self.game_state.mayor_mentioned = save_data.get('mayor_mentioned', False)
            self.game_state.pete_attempted_recruitment = save_data.get('pete_attempted_recruitment', False)
            self.game_state.pete_showing_comedy = save_data.get('pete_showing_comedy', False)
            self.game_state.showing_meredith_response = save_data.get('showing_meredith_response', False)
            self.game_state.showing_garrick_response = save_data.get('showing_garrick_response', False)

            # *** Load all narrative schema flags dynamically ***
            narrative_flags = save_data.get('narrative_flags', {})
            
            if narrative_flags:
                print(f"📂 Loading {len(narrative_flags)} narrative flags")
                
                try:
                    from utils.narrative_schema import narrative_schema
                    all_schema_flags = narrative_schema.get_all_flags()
                    
                    # Load all schema-defined flags
                    for flag_name in all_schema_flags:
                        if flag_name:  # Skip None/empty flags
                            flag_value = narrative_flags.get(flag_name, False)
                            setattr(self.game_state, flag_name, bool(flag_value))
                    
                    # Also load any extra flags that were saved but not in current schema
                    # This ensures backward compatibility if schema changes
                    for flag_name, flag_value in narrative_flags.items():
                        if flag_name and not hasattr(self.game_state, flag_name):
                            setattr(self.game_state, flag_name, bool(flag_value))
                            print(f"   📂 Restored legacy flag: {flag_name}")
                    
                    # Debug: Show some key flags that were loaded
                    key_flags = ['mayor_talked', 'quest_active', 'gareth_recruited']
                    for flag in key_flags:
                        if flag in narrative_flags:
                            print(f"   📂 {flag}: {narrative_flags[flag]}")
                            
                except ImportError:
                    print("⚠️ Narrative schema not available for load - using direct restore")
                    # Fallback to direct restoration
                    for flag_name, flag_value in narrative_flags.items():
                        if flag_name:  # Skip None/empty flags
                            setattr(self.game_state, flag_name, bool(flag_value))
                            
            else:
                print("⚠️ No narrative flags found in save data - may be old save format")
            
            # *** ADD: Restore computed data and sync party ***
            computed_data = save_data.get('computed_data', {})
            if computed_data:
                # Restore party_members list (this might override the earlier restore, which is fine)
                saved_party = computed_data.get('party_members', [])
                self.game_state.party_members = saved_party
                print(f"👥 Restored party members: {saved_party}")
                
                # Verify recruitment flags match party_members
                expected_recruited = set(saved_party)
                actual_recruited = set()
                
                for npc in ['gareth', 'elara', 'thorman', 'lyra']:
                    if getattr(self.game_state, f'{npc}_recruited', False):
                        actual_recruited.add(npc)
                
                if expected_recruited != actual_recruited:
                    print(f"⚠️ Party sync mismatch - Expected: {expected_recruited}, Actual: {actual_recruited}")
                    # Force sync party to match flags
                    self._sync_party_with_flags()
            else:
                # No computed_data, party_members already restored above from save_data.get('party_members', [])
                print(f"👥 Restored party members (legacy): {self.game_state.party_members}")


            quest_system_data = save_data.get('quest_system', {})
            if quest_system_data and hasattr(self.game_state, 'quest_manager'):
                self.game_state.quest_manager.load_from_save_data(quest_system_data)

            # Restore dice game state
            self.game_state.dice_game = save_data.get('dice_game', {})
            # Restore shopping cart
            self.game_state.shopping_cart = save_data.get('shopping_cart', {}),
            # Restore gambling and economy
            self.game_state.house_money = save_data.get('house_money', 50)
            self.game_state.gambling_wins = save_data.get('gambling_wins', 0)
            self.game_state.gambling_losses = save_data.get('gambling_losses', 0)
            
            # Restore equipment state
            self.game_state.equipped_weapon = save_data.get('equipped_weapon')
            self.game_state.equipped_armor = save_data.get('equipped_armor')
            self.game_state.equipped_shield = save_data.get('equipped_shield')
                
            # Restore shopping cart (with safety check)
            shopping_cart_data = save_data.get('shopping_cart', {})
            if isinstance(shopping_cart_data, dict):
                self.game_state.shopping_cart = shopping_cart_data
            else:
                # Safety: Reset corrupted shopping cart data
                print("⚠️ Shopping cart data corrupted, resetting to empty cart")
                self.game_state.shopping_cart = {}

            # Also ensure dice game state is properly restored
            dice_game_data = save_data.get('dice_game', {})
            if isinstance(dice_game_data, dict):
                self.game_state.dice_game = dice_game_data
            else:
                # Safety: Reset dice game to defaults
                print("⚠️ Dice game data corrupted, resetting to defaults")
                self.game_state.dice_game = {
                    'house_money': 500,
                    'game_active': True,
                    'win_streak': 0,
                    'loss_streak': 0,
                    'last_roll': [],
                    'current_bet': 0
                }
            print(f"✅ Game loaded successfully from {save_type}")
            print(f"   Character: {self.game_state.character.get('name', 'Unknown')}")
            print(f"   Current screen: {self.game_state.screen}")
            
            
            # Activate character portrait if character engine available  
            if self.character_engine and self.game_state.character.get('name'):
                # Restore portrait data from save file to game_state
                portrait_file = save_data.get('character', {}).get('selected_portrait_file')
                portrait_gender = save_data.get('character', {}).get('selected_portrait_gender')
                
                if portrait_file and portrait_gender:
                    # Manually copy the portrait to active folder
                
                    # Build source path based on save data
                    from utils.constants import MALE_PORTRAITS_PATH, FEMALE_PORTRAITS_PATH
                    if portrait_gender == 'male':
                        source_dir = MALE_PORTRAITS_PATH
                    else:
                        source_dir = FEMALE_PORTRAITS_PATH
                    
                    source_path = os.path.join(source_dir, portrait_file)
                    
                    # Build active path
                    active_dir = os.path.join(os.path.dirname(source_dir), "active")
                    os.makedirs(active_dir, exist_ok=True)
                    active_path = os.path.join(active_dir, "player.jpg")
                    
                    # Copy portrait to active folder
                    if os.path.exists(source_path):
                        try:
                            shutil.copy2(source_path, active_path)
                            print(f"✅ Activated portrait: {portrait_file} for {self.game_state.character['name']}")
                        except Exception as e:
                            print(f"❌ Error activating portrait: {e}")
                    else:
                        print(f"⚠️ Portrait file not found: {source_path}")
                else:
                    print("⚠️ No portrait data in save file")
            else:
                print("⚠️ Character engine not available for portrait activation")
            
            # After loading all the flags, populate quest system if mayor was already talked to
            if self.game_state.mayor_talked and self.game_state.quest_active:
                # Ensure mayor is mentioned so button appears
                self.game_state.mayor_mentioned = True

                    # For future quest items:
                    # Re-populate any quest log entries that should exist
                    # (You might need to call a method to rebuild active quests here)
            
            print(f"✅ {save_type} loaded successfully!")
            print(f"   Character: {self.game_state.character.get('name', 'Unknown')}")
            print(f"   Location: {self.game_state.screen}")
            print(f"   Party size: {len(self.game_state.party_members) + 1}")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Save file corrupted: {e}")
            return False
        except Exception as e:
            print(f"❌ Load failed: {e}")
            
            return False

    def get_save_info(self, save_slot=1):
        """
        Get information about a save file without loading it
        Returns dict with save info or None if no save exists
        """
        try:
            if save_slot == 0:
                filename = 'saves/autosave.json'
                save_type = "Auto-save"
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
                save_type = "Quick save"
            else:
                filename = f'saves/save_slot_{save_slot}.json'
                save_type = f"Save_slot {save_slot}"

            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            #print(f"🔍 DEBUG: SM: get_save_info({save_slot}) found save file, returning data")
            #print(f"🔍 DEBUG: SM: Character name: {save_data.get('character', {}).get('name', 'Unknown')}")
            
            return {
                'character_name': save_data.get('character', {}).get('name', 'Unknown'),
                'timestamp': save_data.get('timestamp', 'Unknown'),
                'current_screen': save_data.get('current_screen', 'Unknown'),
                'party_size': len(save_data.get('party_members', [])) + 1,
                'gold': save_data.get('character', {}).get('gold', 0),
                'version': save_data.get('version', 'Unknown')
            }
            
        except Exception as e:
            print(f"❌ Error reading save info: {e}")
            return None

    def handle_save_info_request(self, event_data):
        """
        Handle SAVE_INFO_REQUESTED events
        Responds with save info via callback function
        """
        save_slot = event_data.get('save_slot', 1)
        callback = event_data.get('callback')
        
        print(f"SaveManager: Processing save info request for slot {save_slot}")
        
        # Get the save info using existing method
        save_info = self.get_save_info(save_slot)
        print(f"SaveManager: get_save_info({save_slot}) returned: {save_info}")
        
        # Call the callback with the result
        if callback:
            callback(save_slot, save_info)
            print(f"SaveManager: Sent save info response for slot {save_slot}")

    def delete_save(self, save_slot):
        """
        Delete a save file
        """
        try:
            if save_slot == 0:
                filename = 'saves/autosave.json'
            elif save_slot == 99:
                filename = 'saves/quicksave.json'
            else:
                filename = f'saves/save_slot_{save_slot}.json'
            
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🗑️ Deleted save slot {save_slot}")
                return True
            else:
                print(f"❌ Save slot {save_slot} does not exist")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting save: {e}")
            return False

    def can_save_load(self) -> bool:
        """
        Determine if save/load operations are allowed on current screen
        Returns False for transient/temporary screens where saving would cause issues
        """
        """Check if current screen allows save/load operations"""
        if self.game_state.screen in SAVE_LOAD_RESTRICTED_SCREENS:
            print(f"🚫 Save/Load disabled on screen: {self.game_state.screen}")
            return False

        # Check if the current screen is in the disabled list
        is_disabled_screen = self.game_state.screen in SAVE_LOAD_RESTRICTED_SCREENS
        
        # Update the flag
        self.universal_keys_enabled = not is_disabled_screen
        
        # Provide debug feedback
        if is_disabled_screen:
            print(f"🚫 Universal keys disabled on screen: {self.game_state.screen}")
        else:
            print(f"✅ Universal keys enabled on screen: {self.game_state.screen}")
        
        print(f"🔧 DEBUG: universal_keys_enabled = {self.universal_keys_enabled}")

        # Check if current screen is restricted
        if self.game_state.screen in SAVE_LOAD_RESTRICTED_SCREENS:
            print(f"🚫 Save/Load disabled on screen: {self.game_state.screen}")
            return False
        
        # Check if any overlay screens are open that should block save/load
        if hasattr(self.game_state, 'save_screen_open') and self.game_state.save_screen_open:
            return False
        
        if hasattr(self.game_state, 'load_screen_open') and self.game_state.load_screen_open:
            return False
        
        return True

    def register_load_screen_events(self):
        """Register event handlers for load screen operations"""
        if self.event_manager:
            # Register the new load screen events
            self.event_manager.register("LOAD_SLOT_SELECTED", self._handle_load_slot_selection)
            self.event_manager.register("LOAD_GAME_CONFIRM", self._handle_load_confirm)
            self.event_manager.register("DELETE_SAVE_CONFIRM", self._handle_delete_confirm)
            self.event_manager.register("LOAD_SCREEN_CANCEL", self._handle_load_cancel)
            self.event_manager.register("SCREEN_REFRESH_REQUESTED", self._handle_screen_refresh)

            print("🔍 SaveManager registered for load screen events")

    def register_save_screen_events(self):
        """Register event handlers for save screen operations"""
        if self.event_manager:
            # Register the new save screen events
            self.event_manager.register("SAVE_SLOT_SELECTED", self._handle_save_slot_selection)
            self.event_manager.register("SAVE_GAME_CONFIRM", self._handle_save_confirm)
            self.event_manager.register("SAVE_AND_QUIT_CONFIRM", self._handle_save_and_quit_confirm)
            self.event_manager.register("SAVE_SCREEN_CANCEL", self._handle_save_cancel)
            self.event_manager.register("SCREEN_REFRESH_REQUESTED", self._handle_screen_refresh)

            print("💾 SaveManager registered for save screen events")

    def _handle_screen_refresh(self, event_data):
        """Handle screen refresh requests - forces overlay re-render"""
        # The next render cycle will pick up the new selection state
        pass

    def populate_save_slot_cache(self):
        """
        Populate save slot cache for load screen display
        Returns list of save slot data for rendering
        """
        #print("🔍 DEBUG: SaveManager.populate_save_slot_cache() called!")
        slots_to_check = [
            (99, "Quick Save"),
            (1, "Slot 1"),
            (2, "Slot 2"), 
            (3, "Slot 3"),
            (0, "Auto-Save")
        ]
        
        save_slots = []
        for slot_num, slot_name in slots_to_check:
            save_info = self.get_save_info(slot_num)  # Use existing method!
            save_slots.append({
                'slot_num': slot_num,
                'slot_name': slot_name,
                'save_info': save_info
            })
        
        #print(f"💾 SaveManager: Populated {len(save_slots)} save slots for display")
        return save_slots
    
    def _handle_load_slot_selection(self, event_data):
        """Handle LOAD_SLOT_SELECTED events"""
        slot_num = event_data.get('slot_num')
        
        if slot_num is not None:
            # Toggle selection
            if (hasattr(self.game_state, 'load_selected_slot') and 
                self.game_state.load_selected_slot == slot_num):
                # Deselect if clicking same slot
                self.game_state.load_selected_slot = None
            else:
                # Select this slot
                self.game_state.load_selected_slot = slot_num
            print(f"📍 SaveManager set load_selected_slot to: {getattr(self.game_state, 'load_selected_slot', 'MISSING')}")
            # Force screen refresh to show selection highlight
            if self.event_manager:
                self.event_manager.emit("SCREEN_REFRESH_REQUESTED", {})

            print(f"🎯 SaveManager: Slot {slot_num} selection toggled")
    
    def _handle_load_confirm(self, event_data):
        """Handle LOAD_GAME_CONFIRM events"""
        if not hasattr(self.game_state, 'load_selected_slot') or self.game_state.load_selected_slot is None:
            print("No slot selected for loading")
            return
        success = self.load_game(self.game_state.load_selected_slot)  # Use existing method!
        if success:
            # Close load screen and emit success event
            self.game_state.load_screen_open = False
            self.game_state.load_selected_slot = None
            if self.event_manager:
                self.event_manager.emit("GAME_LOADED", {
                    'slot_num': self.game_state.load_selected_slot
                })
            print("✅ SaveManager: Game loaded successfully")
        else:
            if self.event_manager:
                self.event_manager.emit("LOAD_FAILED", {})
            print("❌ SaveManager: Load failed")
    
    def _handle_delete_confirm(self, event_data):
        """Handle DELETE_SAVE_CONFIRM events"""
        if not hasattr(self.game_state, 'load_selected_slot') or self.game_state.load_selected_slot is None:
            print("No slot selected for deletion")
            return
        success = self.delete_save(self.game_state.load_selected_slot)  # Use existing method!
        if success:
            self.game_state.load_selected_slot = None
            if self.event_manager:
                self.event_manager.emit("SAVE_DELETED", {})
            print("🗑️ SaveManager: Save deleted successfully")
        else:
            if self.event_manager:
                self.event_manager.emit("DELETE_FAILED", {})
            print("❌ SaveManager: Delete failed")
    
    def _handle_load_cancel(self, event_data):
        """Handle LOAD_SCREEN_CANCEL events"""
        self.game_state.load_screen_open = False
        self.game_state.load_selected_slot = None
        print("❌ SaveManager: Load screen cancelled")

    def _handle_save_slot_selection(self, event_data):
        """Handle SAVE_SLOT_SELECTED events"""
        slot_num = event_data.get('slot_num')
        
        if slot_num is not None:
            # Toggle selection
            if (hasattr(self.game_state, 'save_selected_slot') and 
                self.game_state.save_selected_slot == slot_num):
                # Deselect if clicking same slot
                self.game_state.save_selected_slot = None
            else:
                # Select this slot
                self.game_state.save_selected_slot = slot_num
            print(f"💾 SaveManager set save_selected_slot to: {getattr(self.game_state, 'save_selected_slot', 'MISSING')}")
            # Force screen refresh to show selection highlight
            if self.event_manager:
                self.event_manager.emit("SCREEN_REFRESH_REQUESTED", {})

            print(f"🎯 SaveManager: Save slot {slot_num} selection toggled")

    def _handle_save_confirm(self, event_data):
        """Handle SAVE_GAME_CONFIRM events"""
        if not hasattr(self.game_state, 'save_selected_slot') or self.game_state.save_selected_slot is None:
            print("No slot selected for saving")
            return
        success = self.save_game(self.game_state.save_selected_slot)  # Use existing method!
        if success:
            # Close save screen and emit success event
            self.game_state.save_screen_open = False
            self.game_state.save_selected_slot = None
            if self.event_manager:
                self.event_manager.emit("GAME_SAVED", {
                    'slot_num': self.game_state.save_selected_slot
                })
            print("✅ SaveManager: Game saved successfully")
        else:
            if self.event_manager:
                self.event_manager.emit("SAVE_FAILED", {})
            print("❌ SaveManager: Save failed")

    def _handle_save_cancel(self, event_data):
        """Handle SAVE_SCREEN_CANCEL events"""
        self.game_state.save_screen_open = False
        self.game_state.save_selected_slot = None
        print("❌ SaveManager: Save screen cancelled")

    def _handle_save_and_quit_confirm(self, event_data):
        """Handle SAVE_AND_QUIT_CONFIRM events"""
        if not hasattr(self.game_state, 'save_selected_slot') or self.game_state.save_selected_slot is None:
            print("No slot selected for save and quit")
            return
            
        # First, save the game
        success = self.save_game(self.game_state.save_selected_slot)
        
        if success:
            print("✅ SaveManager: Game saved successfully, initiating shutdown...")
            # Close save screen
            self.game_state.save_screen_open = False
            self.game_state.save_selected_slot = None
            
        if hasattr(self, '_game_controller_ref'):
            self._game_controller_ref.shutdown()
        else:
            # Fallback: emit quit event that main.py will catch
            if self.event_manager:
                self.event_manager.emit("QUIT_GAME", {})

    def _sync_party_with_flags(self):
        """Sync party_members list with recruitment flags after load"""
        recruited = []
        
        for npc in ['gareth', 'elara', 'thorman', 'lyra']:
            if getattr(self.game_state, f'{npc}_recruited', False):
                recruited.append(npc)
        
        self.game_state.party_members = recruited
        print(f"🔄 Synced party_members to match flags: {recruited}")

    def _handle_quicksave_request(self, event_data):
        """Handle SAVE_REQUESTED events from InputHandler (F5 key)"""
        print("⚡ F5 Quicksave requested via InputHandler")
        
        # Check what type of save request this is
        slot_info = event_data.get("slot", "unknown")
        print(f"   Slot info: {slot_info}")
        
        # Check if save is allowed on current screen
        if not self.can_save_load():
            print("🚫 Quicksave blocked on current screen")
            return
        
        # Perform quicksave (slot 99)
        success = self.save_game(save_slot=99)
        
        if success:
            print("✅ F5 Quicksave completed successfully")
        else:
            print("❌ F5 Quicksave failed")