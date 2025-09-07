
import json
import os
from datetime import datetime

class SaveManager:
    """
    Handles all save/load operations for Terror in Redstone
    Extracted from GameController to follow Single Responsibility Principle
    """
    def __init__(self, game_state, character_engine=None, event_manager=None):
        self.game_state = game_state
        self.character_engine = character_engine
        self.event_manager = event_manager
        
        # Register for save info events
        if event_manager:
            event_manager.register("SAVE_INFO_REQUESTED", self.handle_save_info_request)
            print("📡 SaveManager registered for SAVE_INFO_REQUESTED events")
        else:
            print("❌ SaveManager: No event_manager provided - event registration skipped!")  
        
        print("💾 SaveManager initialized - Professional save/load system ready!")
        
    def save_game(self, save_slot=1):
        
        """
        Save complete game state to JSON file
        save_slot: 1-3 for manual saves, 0 for auto-save
        """
        try:
            # Collect all game state data
            save_data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'save_slot': save_slot,

                # Character data
                'character': self.game_state.character,
                'inventory': self.game_state.inventory,
                
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
                'quest_system': getattr(self.game_state, 'quest_manager', None).get_quest_data_for_save() if hasattr(self.game_state, 'quest_manager') else {},
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
            
            print(f"💾 {save_type} completed: {filename}")
            print(f"   🎭 Character: {self.game_state.character.get('name', 'Unknown')}")
            print(f"   💰 Gold: {self.game_state.character.get('gold', 0)}")
        
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
            target_screen = save_data.get('current_screen', 'game_title')
            if target_screen in self.screens:
                self.game_state.screen = target_screen
                self.previous_screen = save_data.get('previous_screen')
                self.screen_history = save_data.get('screen_history', [])
                self.game_state.screen = target_screen
            else:
                print(f"⚠️ Saved screen '{target_screen}' not available, staying on current screen")
            
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
            
            
            #Activate character portrait after loading
            
            if self.char_engine:
                self.character_engine.activate_character_portrait(self.game_state)

            # After loading all the flags, populate quest system if mayor was already talked to
            if self.game_state.mayor_talked and self.game_state.quest_active:
                # Ensure mayor is mentioned so button appears
                self.game_state.mayor_mentioned = True

                    # For future quest items:
                    # Re-populate any quest log entries that should exist
                    # (You might need to call a method to rebuild active quests here)
            
            print("✅ Game state restored successfully!")

            # Update GameController state
            self.last_load_time = datetime.now()
            self.error_count = 0  # Reset error count on successful load
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Save file corrupted: {e}")
            return False
        except Exception as e:
            print(f"❌ Load failed: {e}")
            self.error_count += 1
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
            print(f"DEBUG: SM: Successfully loaded save data for slot {save_slot}")
            print(f"DEBUG: SM: Character name: {save_data.get('character', {}).get('name', 'NOT FOUND')}")
            
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

    def auto_save(self):
        """
        Perform automatic save (shorthand for save_game(0))
        """
        return self.save_game(save_slot=0)

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
        # UNIFIED: Use same screen names as hotkey blocking system
        restricted_screens = {
        'game_title',           # Title screen 
        'developer_splash',     # Company splash screen
        'main_menu',            # Main menu
        
        # Character Creation Screens  
        'stats', 
        'gender', 
        'name', 
        'portrait_selection',
        'custom_name',
        'name_confirm', 
        'gold', 
        'trinket', 
        'summary', 
        'welcome',
        
        # Gambling screens (from original logic)
        'dice_bets',        # Dice betting screen
        'dice_rolling',     # Dice rolling animation
        'dice_results',     # Dice results display
        'dice_rules',       # Dice rules explanation
        
        # Shopping screens (from original logic)
        'merchant_shop'     # Shop
        }

        # Check if the current screen is in the disabled list
        is_disabled_screen = self.game_state.screen in restricted_screens
        
        # Update the flag
        self.universal_keys_enabled = not is_disabled_screen
        
        # Provide debug feedback
        if is_disabled_screen:
            print(f"🚫 Universal keys disabled on screen: {self.game_state.screen}")
        else:
            print(f"✅ Universal keys enabled on screen: {self.game_state.screen}")
        
        print(f"🔧 DEBUG: universal_keys_enabled = {self.universal_keys_enabled}")

        # Check if current screen is restricted
        if self.game_state.screen in restricted_screens:
            print(f"🚫 Save/Load disabled on screen: {self.game_state.screen}")
            return False
        
        # Check if any overlay screens are open that should block save/load
        if hasattr(self.game_state, 'save_screen_open') and self.game_state.save_screen_open:
            return False
        
        if hasattr(self.game_state, 'load_screen_open') and self.game_state.load_screen_open:
            return False
        
        return True
