"""
Terror in Redstone - Game State Management
Contains the GameState class and all character data management
"""

import random
import pygame
from utils.quest_system import integrate_quest_system 
#from game_logic.item_manager import item_manager
from game_logic.data_manager import get_data_manager
from game_logic.character_engine import get_character_engine

class GameState:
    """
    Manages all game state including character data, current screen, and game flow
    """
    
    def __init__(self):
        # Screen management
        self.screen = "game_title"

        # Access the single, shared ItemLoader instance through the DataManager
        self.data_manager = get_data_manager()
        self.item_manager = self.data_manager.item_manager

        # Character data
        self.character = {
            # Core identity
            'name': '',
            'class': 'fighter',
            'gender': '',
            'trinket': '',
            
            # Core stats (set during character creation)
            'strength': 0,
            'dexterity': 0, 
            'constitution': 0,
            'intelligence': 0,
            'wisdom': 0,
            'charisma': 0,
            
            # Progression tracking
            'level': 1,
            'experience': 0,
            'hit_points': 10,
            'abilities': [],  # ← THE KEY ADDITION!
            
            # Resources
            'gold': 0
        }
        self.temp_stats = {}
        
        # Inventory system
        self.inventory = {
            'weapons': [],
            'armor': [], 
            'items': [],
            'consumables': []
        }

        # Name generation system
        self.used_names = set()
        self.current_names = []
        self.selected_name = ""
        
        # UI state
        self.stats_rolled = False
        self.custom_name_text = ""
        self.custom_name_active = False
        
        # Tavern state
        self.party_members = []
        self.party_member_data = []  # List of full NPC character objects 
        self._party_lookup = {}  # Quick lookup: npc_id -> character data 
        self.current_npc = None
        self.tavern_visits = 0
        
        # Equipment system (game mechanics)
        self.equipped_weapon = None
        self.equipped_armor = None  
        self.equipped_shield = None
        
        # Inventory UI state (game mechanics)
        self.inventory_selected = None
        self.inventory_tab = "weapons"
        self.inventory_open = False
        self.inventory_page = {"weapons": 0, "armor": 0, "items": 0, "consumables": 0}
        self.inventory_selected = None   # Currently selected item name

        # Shopping cart for current merchant session
        self.shopping_cart = {}  # {'item_name': quantity}
        
        #Tracking remaining stock per merchant
        self.merchant_stocks = {}
        
        # Save/load system state (game mechanics)
        self.load_screen_open = False
        self.load_selected_slot = None
        self.load_status_message = "Select a save file to load or delete"
        self.save_screen_open = False
        self.save_selected_slot = None
        self.save_status_message = "Select a slot to save your game"

        #Redstone Town location position
        self.town_player_x = 3  # Town spawn position
        self.town_player_y = 5  # Outside tavern door

        # Ensure XP fields exist
        self.character.setdefault('experience', 0)
        self.character.setdefault('level', 1)

        # Gambling state for Redstone Dice
        self.gambling_state = {
            'last_player_dice': [0, 0],
            'last_house_dice': [0, 0],
            'last_result': None,
            'animation_phase': 'waiting',  # 'rolling', 'showing', 'waiting'
            'roll_start_time': 0
        }

        # Quest and overlay UI state (game mechanics)
        self.quest_log_open = False
        self.character_sheet_open = False
        self.help_screen_open = False
        
        # *** Initialize all narrative schema flags ***
        try:
            from utils.narrative_schema import narrative_schema
            all_flags = narrative_schema.get_all_flags()
            
            # Filter out None values and duplicates
            valid_flags = []
            for flag in all_flags:
                if flag and flag not in valid_flags:
                    valid_flags.append(flag)
            
            # Initialize each flag to False if it doesn't already exist
            for flag_name in valid_flags:
                if not hasattr(self, flag_name):
                    setattr(self, flag_name, False)
            
            print(f"🏗️ Initialized {len(valid_flags)} narrative schema flags")
            
            # Debug: Show some key flags that were initialized
            key_flags = ['mayor_talked', 'quest_active', 'gareth_recruited']
            for flag in key_flags:
                if flag in valid_flags:
                    print(f"   ✓ {flag}: {getattr(self, flag)}")
                    
        except ImportError:
            print("⚠️ Narrative schema not available during GameState init")
            # Fallback initialization of critical flags for backward compatibility
            critical_flags = [
                'mayor_talked', 'garrick_talked', 'meredith_talked', 'pete_talked',
                'gareth_talked', 'elara_talked', 'thorman_talked', 'lyra_talked',
                'quest_active', 'gareth_recruited', 'elara_recruited', 
                'thorman_recruited', 'lyra_recruited',
                'learned_about_swamp_church', 'learned_about_ruins', 'learned_about_refugees',
                'main_quest_completed', 'reported_main_quest'
            ]
            
            for flag_name in critical_flags:
                if not hasattr(self, flag_name):
                    setattr(self, flag_name, False)
                    
            print(f"🏗️ Fallback: Initialized {len(critical_flags)} critical flags")

        except Exception as e:
            print(f"❌ Error initializing narrative flags: {e}")
            # Continue with basic initialization
        
    # Add computed property for recruitment tracking
    @property
    def recruited_count(self):
        """Calculate number of recruited NPCs using narrative schema"""
        from utils.narrative_schema import narrative_schema
        recruitment_flags = narrative_schema.schema.get("recruitment_system", {}).get("recruitment_flags", [])
        return sum(1 for flag in recruitment_flags if getattr(self, flag, False))
    
    @property
    def max_party_size(self):
        """Get maximum party size from narrative schema"""
        from utils.narrative_schema import narrative_schema
        return narrative_schema.schema.get("recruitment_system", {}).get("max_party_size", 4)
    
    @property
    def can_recruit_more(self):
        """Check if more party members can be recruited"""
        return self.recruited_count < (self.max_party_size - 1)  # -1 for player character

    def add_party_member_data(self, npc_id):
        """Add full character data for recruited NPC (called by dialogue system)"""
        import json
        import os
        
        # Skip if already exists
        if npc_id in self._party_lookup:
            return True
            
        # Only add if NPC is actually recruited (check flag)
        recruited_flag = f"{npc_id}_recruited"
        if not getattr(self, recruited_flag, False):
            print(f"⚠️ {npc_id} not recruited - skipping character data")
            return False
        
        # Load character template from JSON
        npc_json_path = os.path.join("data", "npcs", f"{npc_id}.json")
        try:
            with open(npc_json_path, 'r') as f:
                npc_template = json.load(f)
        except FileNotFoundError:
            print(f"❌ NPC JSON not found: {npc_json_path}")
            return False
        
        # Create character data object
        character_data = {
            'id': npc_id,
            'name': npc_template.get('name', npc_id.title()),
            'class': npc_template.get('class', 'Fighter'),
            'level': npc_template.get('level', 1),
            'experience': 0,  # Start at 0 XP
            'hit_points': npc_template.get('hp', 20),
            'max_hit_points': npc_template.get('hp', 20),
            'stats': npc_template.get('stats', {}).copy(),
            'equipment': npc_template.get('equipment', {}).copy(),
            'effects': []
        }
        
        # Add to collections
        self.party_member_data.append(character_data)
        self._party_lookup[npc_id] = character_data
        
        print(f"✅ Added character data for {character_data['name']}")
        return True

    def get_party_member_data(self, npc_id):
        """Get full character data for party member"""
        return self._party_lookup.get(npc_id)

    def sync_party_member_data(self):
        """Sync party_member_data with recruitment flags (called by dialogue system)"""
        # Get current recruited NPCs from flags
        from utils.narrative_schema import narrative_schema
        recruitment_flags = narrative_schema.schema.get("recruitment_system", {}).get("recruitment_flags", [])
        
        should_have_data = []
        for flag in recruitment_flags:
            if getattr(self, flag, False):
                npc_id = flag.replace('_recruited', '')
                should_have_data.append(npc_id)
        
        # Add missing character data
        for npc_id in should_have_data:
            if npc_id not in self._party_lookup:
                self.add_party_member_data(npc_id)
        
        # Remove character data for un-recruited NPCs
        current_data_ids = list(self._party_lookup.keys())
        for npc_id in current_data_ids:
            if npc_id not in should_have_data:
                # Remove from collections
                char_data = self._party_lookup.pop(npc_id)
                self.party_member_data.remove(char_data)
                print(f"➖ Removed character data for {npc_id}")

    def set_selected_portrait(self, gender, portrait_index):
        """Store portrait selection using actual filename"""
        # Get the actual filename from the available portraits
        if hasattr(self, 'available_portraits') and portrait_index in self.available_portraits:
            selected_file = self.available_portraits[portrait_index]
            if selected_file:
                self.character['selected_portrait_file'] = selected_file
                self.character['selected_portrait_gender'] = gender
                print(f"Portrait selection stored: {selected_file}")
            else:
                print(f"Warning: No valid portrait file for index {portrait_index}")
        else:
            print(f"Warning: Portrait index {portrait_index} not found in available portraits")

    def get_portrait_selection(self):
        """Retrieve stored portrait filename"""
        filename = self.character.get('selected_portrait_file', None)
        gender = self.character.get('selected_portrait_gender', self.character.get('gender', 'male'))
        return filename, gender

    def get_character_summary(self):
        """
        Get a formatted summary of the character for display
        
        Returns:
            dict: Character data ready for display
        """
        return {
            'name': self.character.get('name', 'Unknown'),
            'gender': self.character.get('gender', 'Unknown').title(),
            'strength': self.character.get('strength', 10),
            'dexterity': self.character.get('dexterity', 10),
            'constitution': self.character.get('constitution', 10),
            'intelligence': self.character.get('intelligence', 10),
            'wisdom': self.character.get('wisdom', 10),
            'charisma': self.character.get('charisma', 10),
            'hit_points': self.character.get('hit_points', 10),
            'gold': self.character.get('gold', 0),
            'trinket': self.character.get('trinket', 'None')
        }
    
    #TODO Tavern Main is not active now.  This needs to be reviewed/removed. Basic tavern methods
    def enter_tavern(self):
        """Called when player enters the tavern"""
        self.screen = "tavern_main"
        self.tavern_visits += 1
    
    def recruit_npc(self, npc_name):
        """Add an NPC to the party"""
        if npc_name not in self.party_members:
            self.party_members.append(npc_name)
            if hasattr(self, 'quest_manager'):
                self.quest_manager.update_from_game_state()
            return True
        return False
    
    def get_party_size(self):
        """Get current party size (player + NPCs)"""
        return 1 + len(self.party_members)  # 1 for player character
    
    def is_party_full(self):
        """Check if party is at maximum size (4 members)"""
        return self.get_party_size() >= 4

    def can_afford_bet(self, bet_amount):
        """Check if player can afford a bet - GameState Authority"""
        return self.character.get('gold', 0) >= bet_amount
    
    def discover_location(self, location_name):
        """Mark a location as discovered through NPC conversation"""
        if location_name == "hill_ruins":
            self.hill_ruins_known = True
            print("New location discovered: Hill Ruins")
        elif location_name == "swamp_church":
            self.swamp_church_known = True
            print("New location discovered: Swamp Church")
        elif location_name == "refugee_camp":
            self.refugee_camp_known = True
            print("New location discovered: Refugee Camp")

    def mention_mayor(self):
        """Called when an NPC mentions the Mayor, making him available"""
        if not self.mayor_mentioned:
            self.mayor_mentioned = True
            print("You should seek out the Mayor to learn more about these troubles...")    

#TODO  is this needed anymore?? why is it in gamestate?
    def get_garrick_inventory(self):
        """Get Garrick's merchant inventory (now fully data-driven!)"""
        print("🔍 DEBUG: get_garrick_inventory() called")
        #from game_logic.item_manager import item_manager  
        from game_logic.data_manager import get_data_manager
        item_manager = self.item_manager

        #print(f"🔍 DEBUG: item_manager object id: {id(item_manager)}")
        #print(f"🔍 DEBUG: item_manager.merchant_data keys: {list(item_manager.merchant_data.keys())}")
        #print(f"🔍 DEBUG: item_manager.merchant_data contents: {item_manager.merchant_data}")

        
        print(f"🔍 DEBUG: Using DataManager's item_manager")    
        merchant_inventory = item_manager.get_merchant_inventory('garrick_barkeep')
        
        #print("🔍 DEBUG: DataManager or item_manager not available")
        merchant_inventory = None
        print(f"🔍 DEBUG: merchant_inventory result: {merchant_inventory}")

        # Fallback if merchant data not found
        if merchant_inventory is None:
            print("🔍 DEBUG: Using fallback - merchant_inventory is None")
            return {
                'merchant_name': 'Garrick the Barkeep',
                'greeting': "What can I get for you? I keep basic adventuring gear in stock:",
                'items': []
            }
    
        return merchant_inventory

    def toggle_inventory(self):
        """Toggle inventory screen open/closed"""
        self.inventory_open = not self.inventory_open
        if self.inventory_open:
            print(f"🔍 DEBUG: toggle -i- button pressed")
            self.inventory_tab = "weapons"  # Always start with weapons
            self.inventory_selected = None  # Clear selection

    def toggle_quest_log(self):
            """Toggle the quest log screen open/closed"""
            self.quest_log_open = not self.quest_log_open
            print(f"🔍 DEBUG: toggle -q- button pressed")
            if not self.quest_log_open:
                self.selected_quest = None  # Clear selection when closing

    def toggle_help(self):
            """Toggle the help screen open/closed"""
            print(f"🔍 DEBUG: toggle -h- button pressed")
            self.help_screen_open = not self.help_screen_open
        

    def toggle_character_sheet(self):
            """Toggle the character sheet screen open/closed"""
            print(f"🔍 DEBUG: toggle -c- button pressed")
            self.character_sheet_open = not self.character_sheet_open

    def toggle_character_advancement_open(self):
                """Toggle the character sheet screen open/closed"""
                print(f"🔍 DEBUG: toggle -l- button pressed")
                self.character_advancement_open = not self.character_advanacement_open

    def get_items_by_category(self, category):
        """Get all items in a specific category"""
        return self.inventory.get(category, [])

    def is_item_equipped(self, item_name):
        """Check if an item is currently equipped"""
        return (item_name == self.equipped_weapon or 
                item_name == self.equipped_armor or
                item_name == self.equipped_shield)

    def equip_item(self, item_name, category):
        """Equip an item using InventoryEngine for subcategory lookup"""
        if category == "weapons":
            self.equipped_weapon = item_name
        elif category == "armor":
            # Ask InventoryEngine for subcategory (proper architecture)
            if hasattr(self, 'inventory_engine') and self.inventory_engine:
                subcategory = self.inventory_engine.get_item_subcategory(item_name)
            else:
                # Fallback
                subcategory = "shield" if "shield" in item_name.lower() else "body_armor"
            
            if subcategory == "shield":
                self.equipped_shield = item_name
            else:
                self.equipped_armor = item_name

    def unequip_item(self, item_name):
        """Unequip an item"""
        if item_name == self.equipped_weapon:
            self.equipped_weapon = None
        elif item_name == self.equipped_armor:
            self.equipped_armor = None
        elif item_name == self.equipped_shield:
            self.equipped_shield = None

    def consume_item(self, item_name):
        """Consume an item (remove one from inventory)"""
        for category in ['consumables', 'items']:  # Check both categories
            if item_name in self.inventory[category]:
                self.inventory[category].remove(item_name)
                return True
        return False
    
    def discard_item(self, item_name):
        """Remove an item from inventory completely"""
        for category in ['weapons', 'armor', 'items', 'consumables']:
            if item_name in self.inventory[category]:
                # Unequip if currently equipped
                self.unequip_item(item_name)
                # Remove from inventory
                self.inventory[category].remove(item_name)
                return True
        return False
    
