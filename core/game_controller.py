# core/game_controller.py
"""
Professional Game Controller Infrastructure
Centralized management for screen transitions, input handling, and game state
"""

import pygame
import sys
import json
import os
from game_logic.data_manager import get_data_manager, initialize_game_data
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from utils.constants import *

#from utils.graphics import draw_error_screen   will create later

class GameController:
    """
    Master game controller handling screen management, transitions, and universal input
    This is the 'conductor' that orchestrates all game systems
    """
    
    def __init__(self, screen: pygame.Surface, game_state, fonts: Dict, images: Dict):
        self.screen = screen
        self.game_state = game_state
        self.fonts = fonts
        self.images = images
        
        # Screen registry - maps screen names to their functions
        self.screens: Dict[str, Callable] = {}
        
        # Current screen state
        self.current_screen = "game_title"
        self.previous_screen = None
        self.screen_history = []
        
        # Universal input state
        self.universal_keys_enabled = True
        self.escape_exits_game = True
        
        # Error recovery system
        self.last_known_good_screen = "game_title"
        self.error_count = 0
        
        # Debug/development features
        self.debug_mode = False
        self.frame_count = 0
        self.last_fps_time = pygame.time.get_ticks()
        
        # Save/load system state
        self.last_save_time = None
        self.last_load_time = None
        
        data_init_success = self.initialize_data_systems()
        if not data_init_success:
            print("⚠️ GameController: Continuing with limited data functionality")
        print("🎮 Game Controller initialized - Professional infrastructure ready!")

    def register_screen(self, screen_name: str, screen_function: Callable):
        """
        Register a screen function with the controller
        This allows clean separation - screens don't need to know about each other
        """
        self.screens[screen_name] = screen_function
        print(f"📺 Screen registered: {screen_name}")
    
    def transition_to(self, new_screen: str, save_history: bool = True) -> bool:
        """
        Professional screen transition with error handling and history tracking
        Returns True if transition successful, False if failed
        """
        if new_screen not in self.screens:
            print(f"❌ ERROR: Unknown screen '{new_screen}'")
            return False
        
        # Save previous screen for back navigation
        if save_history and self.current_screen:
            self.previous_screen = self.current_screen
            self.screen_history.append(self.current_screen)
            
            # Limit history size to prevent memory bloat
            if len(self.screen_history) > 10:
                self.screen_history.pop(0)
        
        # Update state
        old_screen = self.current_screen
        self.current_screen = new_screen
        self.last_known_good_screen = new_screen
        
        print(f"🔄 Screen transition: {old_screen} → {new_screen}")
        print(f"DEBUG: Transition successful = True")
        return True
    
    def go_back(self) -> bool:
        """
        Navigate back to previous screen (like browser back button)
        """
        if self.previous_screen:
            return self.transition_to(self.previous_screen, save_history=False)
        elif self.screen_history:
            previous = self.screen_history.pop()
            return self.transition_to(previous, save_history=False)
        else:
            print("📍 No previous screen to return to")
            return False
    
    def handle_universal_input(self, event: pygame.event.Event) -> bool:
        """
        Handle universal keyboard shortcuts that work across all screens
        Returns True if event was consumed, False if screen should handle it
        """
        if not self.universal_keys_enabled:
            return False
        
        if event.type == pygame.KEYDOWN:
            # DEBUG: Show what's happening
            print(f"🔍 DEBUG: Controller screen={self.current_screen}, Key pressed={pygame.key.name(event.key)}")

            # ESC key - close overlays first, never exit game
            if event.key == pygame.K_ESCAPE:
                # Check if any overlays are open and close them
                if (self.game_state.help_screen_open or 
                    self.game_state.inventory_open or 
                    self.game_state.quest_log_open or 
                    self.game_state.character_sheet_open or
                    getattr(self.game_state, 'save_screen_open', False) or
                    getattr(self.game_state, 'load_screen_open', False)):
                    
                    self.close_all_overlays()
                    if hasattr(self.game_state, 'save_screen_open'):
                        self.game_state.save_screen_open = False
                    if hasattr(self.game_state, 'load_screen_open'):
                        self.game_state.load_screen_open = False
                    print("🔄 ESC: Closed all overlays")
                    return True
                else:
                    # No overlays open - ESC does nothing (could add main menu logic here later)
                    print("🔄 ESC: No overlays to close")
                    return True
            
            # F1 always works (to toggle debug on/off)
            if event.key == pygame.K_F1:
                self.toggle_debug_info()
                return True

            # Other debug shortcuts (only in debug mode)
            if self.debug_mode:
                if event.key == pygame.K_F2:
                    self.print_game_state()
                    return True
                elif event.key == pygame.K_F3:
                    self.screenshot()
                    return True
                # F4 - Reload data systems (development shortcut)
                elif event.key == pygame.K_F4:
                    print("🔄 F4 pressed - Reloading data systems...")
                    self.reload_data_systems()
                    return True

            # ===== UNIFIED HOTKEY BLOCKING SYSTEM =====
            # Define screens where ALL hotkeys should be blocked (except H for help)
            blocked_hotkey_screens = {
                'game_title',           # Title screen 
                'developer_splash',     # Company splash screen
                'main_menu',            # Main menu
                
                # Character Creation Screens
                'stats', 
                'gender', 
                'name', 
                'portrait_selection', 
                'name_confirm', 
                'gold', 
                'trinket', 
                'summary', 
                'welcome'
            }

            # Special exception: custom_name screen when text input is active
            is_text_input_active = (self.current_screen == 'custom_name' and 
                                  getattr(self.game_state, 'custom_name_active', False))
            
            # Check if current screen should block hotkeys
            is_blocked_screen = self.current_screen in blocked_hotkey_screens
            
            # Override: Never block on text input screen
            if is_text_input_active:
                is_blocked_screen = False

            print(f"🔍 DEBUG: is_blocked_screen={is_blocked_screen}")

            # ===== HELP KEY - ALWAYS WORKS (except during text input) =====
            if event.key == pygame.K_h:
                if not is_text_input_active:  # Don't interfere with typing 'h' in names
                    if not self.game_state.help_screen_open:
                        self.close_all_overlays()
                    self.game_state.toggle_help()
                    print(f"Help screen open: {self.game_state.help_screen_open}")
                    return True

            # ===== DEFINE BLOCKED KEYS LIST =====
            blocked_keys = [
                pygame.K_i, pygame.K_c, pygame.K_q,    # Overlay hotkeys
                pygame.K_m, pygame.K_p,                # Future hotkeys
                pygame.K_F5, pygame.K_F7, pygame.K_F10  # Save/Load keys
            ]
            
            # ===== BLOCKED SCREEN LOGIC - BLOCK EVERYTHING ELSE =====
            if is_blocked_screen and event.key in blocked_keys:
                # Get readable key name for debug message
                key_names = {
                    pygame.K_i: 'I (Inventory)',
                    pygame.K_c: 'C (Character Sheet)', 
                    pygame.K_q: 'Q (Quest Log)',
                    pygame.K_m: 'M (Map)',
                    pygame.K_p: 'P (Party)',
                    pygame.K_F5: 'F5 (Quick Save)',
                    pygame.K_F7: 'F7 (Save Screen)',
                    pygame.K_F10: 'F10 (Load Screen)'
                }
                key_name = key_names.get(event.key, pygame.key.name(event.key))
                print(f"🚫 Hotkey {key_name} blocked on screen: {self.current_screen}")
                return True

            # ===== SAVE/LOAD KEYS - Check can_save_load() first =====
            if event.key in [pygame.K_F5, pygame.K_F7, pygame.K_F10]:
                if not self.can_save_load():
                    print(f"🚫 Save/Load operations disabled on screen: {self.current_screen}")
                    return True
                
                # Process save/load if allowed
                if event.key == pygame.K_F5:
                    self.save_game(save_slot=99)
                    return True
                elif event.key == pygame.K_F7:
                    print("DEBUG: F7 key detected - opening save screen")
                    self.game_state.save_screen_open = True
                    print(f"DEBUG: save_screen_open set to {self.game_state.save_screen_open}")    
                    return True
                elif event.key == pygame.K_F10:
                    self.game_state.load_screen_open = True
                    return True

            # ===== OVERLAY HOTKEYS - Only work on gameplay screens =====
            # I for Inventory
            if event.key == pygame.K_i:
                if not self.game_state.inventory_open:
                    self.close_all_overlays()
                self.game_state.toggle_inventory()
                print(f"Inventory open: {self.game_state.inventory_open}")
                return True
            
            # Q for quest
            elif event.key == pygame.K_q:
                if not self.game_state.quest_log_open:
                    self.close_all_overlays()
                self.game_state.toggle_quest_log()
                print(f"Quest log open: {self.game_state.quest_log_open}")
                return True
            
            # C for character sheet
            elif event.key == pygame.K_c:
                if not self.game_state.character_sheet_open:
                    self.close_all_overlays()
                self.game_state.toggle_character_sheet()
                print(f"Character sheet open: {self.game_state.character_sheet_open}")
                return True

        return False
    
    def run_current_screen(self, events: list) -> Optional[str]:
        """
        Execute the current screen with professional error handling
        Returns next screen name or None to continue current screen
        """
        try:
            self.frame_count += 1
            
            # Get current screen function
            if self.current_screen not in self.screens:
                raise ValueError(f"Screen '{self.current_screen}' not registered")
            
            screen_function = self.screens[self.current_screen]
            
            # Execute screen with error recovery
            result = screen_function(
                self.screen, 
                self.game_state, 
                self.fonts, 
                self.images, 
                events,
                self  # Pass controller reference for advanced features
            )
            
            # Reset error counter on successful execution
            self.error_count = 0
            
            # Handle screen transition requests
            if result and isinstance(result, str):
                if self.transition_to(result):
                    return result
                else:
                    print(f"❌ Failed to transition to '{result}', staying on current screen")
            
            return None
            
        except Exception as e:
            self.handle_screen_error(e)
            return None
    
    def handle_screen_error(self, error: Exception):
        """
        Professional error recovery system
        """
        self.error_count += 1
        print(f"💥 Screen error in '{self.current_screen}': {error}")
        
        # Progressive error recovery
        if self.error_count < 3:
            # Try to continue with current screen
            print("🔧 Attempting to continue...")
        elif self.error_count < 5:
            # Fall back to last known good screen
            print(f"🚨 Falling back to: {self.last_known_good_screen}")
            self.transition_to(self.last_known_good_screen)
        else:
            # Emergency fallback to splash screen
            print("🆘 Emergency fallback to splash screen")
            self.transition_to("splash")
            self.error_count = 0
    
    def quit_game(self):
        """
        Clean game shutdown with state saving opportunities
        """
        print("👋 Game Controller shutting down...")
        
        # Future: Save game state here
        # self.game_state.save_to_file("autosave.dat")
        
        pygame.quit()
        sys.exit()
    
    def toggle_debug_info(self):
        """
        Toggle debug information display
        """
        self.debug_mode = not self.debug_mode
        print(f"🐛 Debug mode: {'ON' if self.debug_mode else 'OFF'}")
    
    def print_game_state(self):
        """
        Debug function to print current game state
        """
        print(f"\n=== GAME STATE DEBUG ===")
        print(f"Current Screen: {self.current_screen}")
        print(f"Previous Screen: {self.previous_screen}")
        print(f"Screen History: {self.screen_history}")
        print(f"Character Name: {getattr(self.game_state, 'character_name', 'None')}")
        print(f"Error Count: {self.error_count}")
        print(f"Frame Count: {self.frame_count}")
        print(f"========================\n")
    
    def screenshot(self):
        """
        Take a screenshot for debugging/development
        """
        filename = f"screenshot_{pygame.time.get_ticks()}.png"
        pygame.image.save(self.screen, filename)
        print(f"📸 Screenshot saved: {filename}")
    
    def close_all_overlays(self):
        """Close all overlay screens for clean single-overlay behavior"""
        self.game_state.inventory_open = False
        self.game_state.quest_log_open = False
        self.game_state.character_sheet_open = False
        self.game_state.help_screen_open = False
        # Clear any selections when closing overlays
        self.game_state.inventory_selected = None
        self.game_state.selected_quest = None
        print("🔄 All overlays closed")
    
    def shutdown(self):
        """Professional shutdown with complete resource cleanup"""
        print("🏰 Terror in Redstone shutting down...")

        # 1. Auto-save current progress (you have this!)
        if hasattr(self, 'save_game'):
            print("💾 Auto-saving progress...")
            self.save_game(save_slot=0)  # Auto-save slot

        # 2. Clear active game state
        if hasattr(self.game_state, 'clear_active_portrait'):
            self.game_state.clear_active_portrait()
            print("🖼️ Portrait resources cleared")

        # 3. Close all overlay states cleanly
        self.close_all_overlays()

        # 4. Audio cleanup (if you add sound later)
        try:
            pygame.mixer.quit()
            print("🔊 Audio resources released")
        except:
            pass  # Audio might not be initialized

        # 5. Clean pygame shutdown
        pygame.quit()
        print("🎮 Pygame resources released")
        
        # 6. Final system exit
        print("⚔️ Farewell, brave adventurer!")
        sys.exit()

    def draw_debug_overlay(self):
        """
        Draw debug information overlay
        """
        if not self.debug_mode:
            return
        
        # Calculate FPS
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fps_time > 1000:
            fps = self.frame_count * 1000 // (current_time - self.last_fps_time)
            self.last_fps_time = current_time
            self.frame_count = 0
            self.last_fps = fps
        
        # Draw debug info
        if hasattr(self, 'last_fps'):
            debug_text = [
                f"FPS: {self.last_fps}",
                f"Screen: {self.current_screen}",
                f"Errors: {self.error_count}",
                f"F1:Debug F2:State F3:Screenshot"
            ]
            
            y = 10
            for text in debug_text:
                surface = self.fonts['fantasy_tiny'].render(text, True, BRIGHT_GREEN)
                self.screen.blit(surface, (10, y))
                y += 20



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
                'current_screen': self.current_screen,
                'screen_history': self.screen_history[-5:],  # Keep last 5 screens
                'previous_screen': self.previous_screen,
                
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
                'server_talked': getattr(self.game_state, 'server_talked', False),
                'bartender_talked': getattr(self.game_state, 'bartender_talked', False),
                'learned_about_church': getattr(self.game_state, 'learned_about_church', False),
                'learned_about_ruins': getattr(self.game_state, 'learned_about_ruins', False),
                'quest_active': getattr(self.game_state, 'quest_active', False),
                'just_got_quest': getattr(self.game_state, 'just_got_quest', False),
                'quest_system': getattr(self.game_state, 'quest_manager', None).get_quest_data_for_save() if hasattr(self.game_state, 'quest_manager') else {},

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
            self.error_count = 0  # Reset error count on successful save
            
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            self.error_count += 1
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
                self.current_screen = target_screen
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
            self.game_state.server_talked = save_data.get('server_talked', False)
            self.game_state.bartender_talked = save_data.get('bartender_talked', False)  
            self.game_state.learned_about_church = save_data.get('learned_about_church', False)
            self.game_state.learned_about_ruins = save_data.get('learned_about_ruins', False)
            self.game_state.quest_active = save_data.get('quest_active', False)
            self.game_state.mayor_mentioned = save_data.get('mayor_mentioned', False)
            self.game_state.pete_attempted_recruitment = save_data.get('pete_attempted_recruitment', False)
            self.game_state.pete_showing_comedy = save_data.get('pete_showing_comedy', False)
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
            print(f"   Current screen: {self.current_screen}")
            
            #Activate character portrait after loading
            self.game_state.activate_character_portrait()

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
            
            # Check if current screen is restricted
            if self.current_screen in restricted_screens:
                print(f"🚫 Save/Load disabled on screen: {self.current_screen}")
                return False
            
            # Check if any overlay screens are open that should block save/load
            if hasattr(self.game_state, 'save_screen_open') and self.game_state.save_screen_open:
                return False
            
            if hasattr(self.game_state, 'load_screen_open') and self.game_state.load_screen_open:
                return False
            
            return True
    def initialize_data_systems(self) -> bool:
        """
        Initialize all game data management systems
        Called during GameController startup - Session 4 integration
        """
        print("🎮 GameController: Initializing data management systems...")
        
        try:
            # Initialize the master data manager
            success = initialize_game_data()
            
            if success:
                # Store reference to data manager for easy access
                self.data_manager = get_data_manager()
                
                # Validate all systems loaded correctly
                if self.data_manager.validate_data_integrity():
                    print("✅ GameController: All data systems operational!")
                    
                    # NEW: Complete engine initialization with GameState reference
                    engine_success = self.data_manager.initialize_engines_with_gamestate(self.game_state)
                    if engine_success:
                        print("✅ GameController: Complete system initialization successful!")
                        print("   🎯 Single Data Authority pattern active - GameState is the source of truth")
                    else:
                        print("⚠️ GameController: Engine initialization had warnings")

                    # Optional: Print system status for debugging
                    status = self.data_manager.get_system_status()
                    print(f"   📊 Systems loaded: {status['systems_healthy']}/{status['total_systems']}")
                    print(f"   ⏱️ Load time: {status['load_time']:.3f}s")
                    
                    return True
                else:
                    print("⚠️ GameController: Data validation warnings - check console output")
                    # Continue anyway - some warnings are acceptable
                    self.data_manager = get_data_manager()
                    return True
            else:
                print("❌ GameController: Critical data system failures!")
                
                # Emergency fallback - still try to run with minimal data
                self.data_manager = get_data_manager()
                fallback_data = self.data_manager.emergency_fallback()
                print("🆘 GameController: Using emergency fallback data")
                
                # Game can still run, but with limited functionality
                return False
                
        except Exception as e:
            print(f"❌ GameController: Data initialization failed: {e}")
            self.error_count += 1
            
            # Try to continue with no data manager
            self.data_manager = None
            return False
        
    def get_inventory_engine(self):
        """Get the inventory engine instance from DataManager"""
        if self.data_manager:
            return self.data_manager.get_manager('inventory')
        return None

    def get_commerce_engine(self):
        """Get the commerce engine instance from DataManager"""  
        if self.data_manager:
            return self.data_manager.get_manager('commerce')
        return None
    
    def get_data_manager(self):
        """
        Safe accessor for data manager
        Returns None if not initialized
        """
        return getattr(self, 'data_manager', None)
    
    def reload_data_systems(self) -> bool:
        """
        Reload all data systems (useful for development)
        """
        if hasattr(self, 'data_manager') and self.data_manager:
            return self.data_manager.reload_all_systems()
        else:
            return self.initialize_data_systems()


class ScreenRegistry:
    """
    Helper class for organizing screen registration
    Makes it easy to register all screens in one place
    """
    
    @staticmethod
    def register_all_screens(controller: GameController):
        """
        Register all game screens with the controller
        This is where we'll add each screen as we create them
        """
        
        # Import screen modules (we'll add these as we create them)
        try:
            from screens.character_creation import (
                draw_stats_screen, draw_gender_screen,
                draw_name_screen, draw_custom_name_screen, draw_name_confirm_screen,
                draw_gold_screen, draw_trinket_screen, draw_summary_screen,
                draw_welcome_screen, draw_portrait_selection_screen
            )
            print("🔍 Attempting to import character creation screens...")
            print("✅ Character creation screens imported successfully!")
            
            # Register character creation screens  
            controller.register_screen("stats", draw_stats_screen)
            controller.register_screen("gender", draw_gender_screen)
            controller.register_screen("name", draw_name_screen)
            controller.register_screen("portrait_selection", draw_portrait_selection_screen)
            controller.register_screen("custom_name", draw_custom_name_screen)
            controller.register_screen("name_confirm", draw_name_confirm_screen)
            controller.register_screen("gold", draw_gold_screen)
            controller.register_screen("trinket", draw_trinket_screen)
            controller.register_screen("summary", draw_summary_screen)
            controller.register_screen("welcome", draw_welcome_screen)
            
            print("✅ Character creation screens registered!")

        except ImportError as e:
            print(f"❌ IMPORT ERROR: {e}")
            print(f"⚠️ Character creation screens not available: {e}")
        
         # Register title/menu screens
        try:
            from screens.title_menu import draw_title_screen, draw_company_splash_screen, draw_main_menu
            controller.register_screen("game_title", draw_title_screen)           # Initial title
            controller.register_screen("developer_splash", draw_company_splash_screen)  # Company screen
            controller.register_screen("main_menu", draw_main_menu)               # Main menu
            print("✅ Title/menu screens registered!")
        except ImportError as e:
            print(f"⚠️ Title/menu screens not available: {e}")

        # Register tavern screens
        try:
            from screens.tavern import draw_tavern_main_screen, draw_npc_selection_screen, draw_npc_conversation_screen
            controller.register_screen("tavern_main", draw_tavern_main_screen)
            controller.register_screen("tavern_npcs", draw_npc_selection_screen)
            controller.register_screen("tavern_conversation", draw_npc_conversation_screen)
            controller.register_screen("bartender", draw_tavern_main_screen)  # If bartender uses same screen
            print("✅ Tavern screens registered!")
        except ImportError as e:
            print(f"⚠️ Tavern screens not available: {e}")

        # Register gambling screens  
        try:
            from screens.gambling_dice import draw_dice_bet_screen, draw_dice_rolling_screen, draw_dice_results_screen, draw_dice_rules_screen
            controller.register_screen("dice_bet", draw_dice_bet_screen)
            controller.register_screen("dice_bets", draw_dice_bet_screen)  # Alternative name
            controller.register_screen("dice_rolling", draw_dice_rolling_screen)
            controller.register_screen("dice_results", draw_dice_results_screen)
            controller.register_screen("dice_rules", draw_dice_rules_screen)
            print("✅ Gambling screens registered!")
        except ImportError as e:
            print(f"⚠️ Gambling screens not available: {e}")
        
        # Register shopping screen
        try:
            from screens.shopping import draw_merchant_screen
            controller.register_screen("merchant_shop", draw_merchant_screen)
            print("✅ Shopping screen registered!")
        except ImportError as e:
            print(f"⚠️ Shopping screen not available: {e}")

        # Future screens will be registered here
        # controller.register_screen("general_store", general_store_screen)
        # controller.register_screen("combat", combat_screen)
        # controller.register_screen("world_map", world_map_screen)
        
        print("✅ Screen registration complete!")


# Professional configuration system
class GameConfig:
    """
    Centralized configuration management
    Easy tweaking of game balance and behavior
    """
    
    # Display settings
    ENABLE_DEBUG_MODE = False
    ESCAPE_EXITS_GAME = True
    ENABLE_UNIVERSAL_KEYS = True
    
    # Game balance settings
    DICE_ANIMATION_SPEED = 0.1  # seconds per dice roll animation frame
    STARTING_GOLD_MULTIPLIER = 10  # 3d6 * 10
    TAVERN_ROOM_COST = 2  # Gold per night
    
    # UI settings
    BUTTON_HOVER_ENABLED = True
    SCREEN_TRANSITION_SPEED = 0.2
    AUTO_SAVE_INTERVAL = 300  # seconds
    
    # Development settings
    SHOW_FPS = False
    ENABLE_SCREENSHOTS = True
    LOG_SCREEN_TRANSITIONS = True
    
    @classmethod
    def apply_to_controller(cls, controller: GameController):
        """
        Apply configuration settings to game controller
        """
        controller.debug_mode = cls.ENABLE_DEBUG_MODE
        controller.escape_exits_game = cls.ESCAPE_EXITS_GAME
        controller.universal_keys_enabled = cls.ENABLE_UNIVERSAL_KEYS
        
        print("⚙️ Game configuration applied to controller")


if __name__ == "__main__":
    print("🎮 Game Controller Infrastructure")
    print("This module provides professional game state management")
    print("Import and use with: from core.game_controller import GameController")



