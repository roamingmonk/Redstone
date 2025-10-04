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
from utils.overlay_utils import OverlayState
from utils.narrative_schema import narrative_schema

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
            'hit_points': 10,   #Max hip points
            'current_hp': 10,   #Current hip points
            'max_hp'
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
        
        # Overlay state management (unified system)
        self.overlay_state = OverlayState()

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
        
        # Inventory UI state (game mechanics)
        self.inventory_selected = None
        self.inventory_tab = "weapons"
        self.inventory_page = {"weapons": 0, "armor": 0, "items": 0, "consumables": 0}
        self.inventory_selected = None   # Currently selected item name

        # Shopping cart for current merchant session
        self.shopping_cart = {}  # {'item_name': quantity}
        
        #Tracking remaining stock per merchant
        self.merchant_stocks = {}
        
        # Save/load system state (game mechanics)
        self.load_selected_slot = None
        self.load_status_message = "Select a save file to load or delete"
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

        # *** Initialize all narrative schema flags ***
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

        # Combat state tracking
        self.in_combat = False
        self.combat_data = {
            "encounter_id": None,
            "battlefield": None,
            "current_turn": 0,
            "phase": "movement",  # "movement", "action", "resolution"
            "player_position": {"x": 0, "y": 0},
            "enemy_positions": {},
            "defeated_enemies": [],
            "combat_log": []
        }
                
        
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
        npc_hp = npc_template.get('hp', 20)  # Read HP from NPC JSON
        npc_ac = npc_template.get('ac', 10)  # Read AC from NPC JSON

        character_data = {
            'id': npc_id,
            'name': npc_template.get('name', npc_id.title()),
            'class': npc_template.get('class', 'Fighter'),
            'level': npc_template.get('level', 1),
            'experience': 0,  # Start at 0 XP
            'hp': npc_hp,  # Use 'hp' to match NPC JSON format
            'hit_points': npc_hp,  # Also store as hit_points for compatibility
            'current_hp': npc_hp,  # Initialize current HP to max! ← CRITICAL FIX
            'max_hit_points': npc_hp,
            'ac': npc_ac,  # Store AC from NPC JSON
            'stats': npc_template.get('stats', {}).copy(),
            'equipment': npc_template.get('equipment', {}).copy(),
            'effects': []
}
        
        # Add to collections
        self.party_member_data.append(character_data)
        self._party_lookup[npc_id] = character_data
        
        print(f"✅ Added character data for {character_data['name']}")
        return True

    def start_combat(self, encounter_id: str):
        """Initialize combat state for new encounter"""
        self.in_combat = True
        self.combat_data["encounter_id"] = encounter_id
        self.combat_data["combat_log"] = [f"Combat begins: {encounter_id}"]

    def end_combat(self, victory: bool):
        """Clean up combat state and return to exploration"""
        self.in_combat = False
        self.combat_data = {
            "encounter_id": None,
            "battlefield": None,
            "current_turn": 0,
            "phase": "movement",
            "player_position": {"x": 0, "y": 0},
            "enemy_positions": {},
            "defeated_enemies": [],
            "combat_log": []
        }

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
        
        #from game_logic.item_manager import item_manager  
        from game_logic.data_manager import get_data_manager
        item_manager = self.item_manager

        merchant_inventory = item_manager.get_merchant_inventory('garrick_barkeep')
        
        merchant_inventory = None

        # Fallback if merchant data not found
        if merchant_inventory is None:

            return {
                'merchant_name': 'Garrick the Barkeep',
                'greeting': "What can I get for you? I keep basic adventuring gear in stock:",
                'items': []
            }
    
        return merchant_inventory

    def get_items_by_category(self, category):
        """Get all items in a specific category"""
        return self.inventory.get(category, [])

    def is_item_equipped(self, item_name):
        """Check if an item is currently equipped"""
        return (item_name == self.character.get('equipped_weapon') or 
                item_name == self.character.get('equipped_armor') or 
                item_name == self.character.get('equipped_shield'))


    
