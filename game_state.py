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
        self.screen = "splash"

        # Access the single, shared ItemLoader instance through the DataManager
        self.data_manager = get_data_manager()
        self.item_manager = self.data_manager.item_manager

        # Character data
        self.character = {}
        self.temp_stats = {}
        
        # Inventory system
        self.inventory = {
            'weapons': ['Longsword'],
            'armor': ['Leather Armor', 'Shield'], 
            'items': [],
            'consumables': []
        }

        # Name generation system
        self.used_names = set()
        self.current_names = []
        self.selected_name = ""
        
        # UI state
        self.stats_rolled = False
        self.custom_name_input = False
        self.custom_name_text = ""
        self.custom_name_active = False
        
        # Tavern state
        self.party_members = []
        self.current_npc = None
        self.tavern_visits = 0
        
        # Quest system flags  
        self.mayor_mentioned = False
        self.mayor_talked = False
        self.quest_active = False

        # Location discovery system
        self.hill_ruins_known = False
        self.swamp_church_known = False  
        self.refugee_camp_known = False

        # NPC interaction tracking
        self.garrick_talked = False
        self.meredith_talked = False
        self.drunk_talked = False
        self.pete_attempted_recruitment = False
        self.pete_showing_comedy = False

        # NPC response tracking  (validate this is needed)
        self.showing_garrick_repsponse = False
        self.garrick_dialogue_response = []
        self.showing_meredith_response = False
        self.meredith_dialogue_response = []
        
        integrate_quest_system(self)

        # Shopping cart for current merchant session
        self.shopping_cart = {}  # {'item_name': quantity}
        # Inventory Management System
        self.equipped_weapon = None      # Currently equipped weapon name
        self.equipped_armor = None       # Currently equipped body armor name  
        self.equipped_shield = None      # Currently equipped shield name
        self.inventory_open = False      # Is inventory screen open
        self.inventory_tab = "weapons"   # Current tab: weapons, armor, items, consumables
        self.inventory_page = {"weapons": 0, "armor": 0, "items": 0, "consumables": 0}
        self.inventory_selected = None   # Currently selected item name

        # Quest Log System
        self.quest_log_open = False      # Is quest log screen open
        self.selected_quest = None       # Currently selected quest for details
        
        # Character Sheet
        self.character_sheet_open = False  # Is character sheet screen open
        
        # Help Screen
        self.help_screen_open = False

        # Quest progression flags
        self.met_mayor = False           # Has player talked to mayor
        self.learned_about_refugees = False    # Bartender Garrick mentioned refugee camp
        self.learned_about_church = False      # Server Meredith mentioned swamp church  
        self.learned_about_ruins = False       # Grizzled warrior mentioned hill ruins
        
        # Quest completion flags
        self.main_quest_complete = False
        self.refugee_camp_complete = False
        self.swamp_church_complete = False
        self.hill_ruins_complete = False

        # In GameState.__init__
        self.load_screen_open = False
        self.load_selected_slot = None
        self.load_status_message = "Select a save file to load or delete"

        # Save game screen state
        self.save_screen_open = False
        self.save_selected_slot = None
        self.save_status_message = "Select a slot to save your game"


        # Enhanced Gambling state for Redstone Dice
        self.gambling_state = {
            'last_player_dice': [0, 0],
            'last_house_dice': [0, 0],
            'last_result': None,
            'animation_phase': 'waiting',  # 'rolling', 'showing', 'waiting'
            'roll_start_time': 0
        }
        
        # NEW: Redstone Dice Game State
        self.dice_game = {
            'house_money': random.randint(400, 700),  # House starts with random amount
            'current_bet': 0,
            'last_roll': [0, 0, 0],
            'rolling': False,
            'roll_start_time': 0,
            'last_result': None,
            'last_payout': 0,
            'game_active': True,  # False if house is broke or player hit triple 6s
            'win_streak': 0,
            'loss_streak': 0
        }
        

    def get_random_names(self, gender):
        """
        Generate 3 random names based on gender
        
        Args:
            gender: 'male' or 'female'
            
        Returns:
            list: 3 unique name combinations
        """
        male_first = ["Garlen", "Theron", "Bjorn", "Marcus", "Aldric", "Grim", 
                     "Roderick", "Tormund", "Cedric", "Bronn", "Garrett", "Willem"]
        male_last = ["Sliverblade", "Ironwill", "Stormhammer", "Battleborn", "Steelhand", 
                    "Ironforge", "Valorheart", "Ashblade", "Strongarm", "Warwick", 
                    "Blackstone", "Goldbeard", "Flameheart", "Ironshield"]
        
        female_first = ["Kala", "Gina", "Sera", "Thessa", "Mira", "Brenna",
                       "Cordelia", "Vera", "Dara", "Elara", "Rhea", "Zara"]
        female_last = ["Stormborn", "Brightblade", "Ironheart", "Battlewise", "Steelstrike",
                      "Stormwind", "Ashfall", "Strongwill", "Valorborn", "Moonwhisper",
                      "Starfire", "Swiftarrow", "Nightblade", "Goldweaver"]
        
        names = []
        
        # For males, always include Garlen Sliverblade as an option if not used
        if gender == 'male' and "Garlen Sliverblade" not in self.used_names:
            names.append("Garlen Sliverblade")
            self.used_names.add("Garlen Sliverblade")
        
        # Generate random combinations
        first_names = male_first if gender == 'male' else female_first
        last_names = male_last if gender == 'male' else female_last
        
        attempts = 0
        while len(names) < 3 and attempts < 50:  # Prevent infinite loop
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            if full_name not in self.used_names:
                names.append(full_name)
                self.used_names.add(full_name)
            attempts += 1
        
        # Fill remaining slots if needed (fallback safety)
        while len(names) < 3:
            first = random.choice(first_names)
            last = random.choice(last_names)
            full_name = f"{first} {last}"
            names.append(full_name)
        
        return names
    
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

    def ensure_active_portrait(self):
        """Ensure active portrait file exists, recreate if missing"""
        import os
        import shutil
        
        filename, gender = self.get_portrait_selection()
        
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

    def activate_character_portrait(self):
        """Ensure correct portrait is active for current character"""
        if hasattr(self, 'character') and 'selected_portrait_gender' in self.character:
            # Character has portrait selection data - ensure active portrait matches
            self.ensure_active_portrait()
        else:
            # No portrait selection data - clear any existing active portrait
            self.clear_active_portrait()

    def clear_active_portrait(self):
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

    def finalize_character(self):
        """
        Complete character creation by calculating final stats
        """
        self.character['hit_points'] = self.calculate_hp()
    
        # Add starting trinket to inventory
        if 'trinket' in self.character:
            self.inventory['items'].append(self.character['trinket'])

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
    
    # Basic tavern methods
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
    
    def roll_dice_gambling(self, bet_amount=10):
        """
        Simple gambling mini-game: player vs house dice roll
        Returns: (player_won, player_roll, house_roll, winnings)
        """
        # Check if player has enough gold
        if self.character.get('gold', 0) < bet_amount:
            return False, 0, 0, 0
        
        # Roll dice
        player_roll = random.randint(1, 6) + random.randint(1, 6)  # 2d6
        house_roll = random.randint(1, 6) + random.randint(1, 6)   # 2d6
        
        # Determine winner
        if player_roll > house_roll:
            # Player wins - gets bet back plus winnings
            winnings = bet_amount * 2
            net_gain = winnings - bet_amount
            self.character['gold'] += net_gain
            return True, player_roll, house_roll, winnings
        else:
            # House wins - player loses bet
            self.character['gold'] -= bet_amount
            return False, player_roll, house_roll, 0

    
    def roll_redstone_dice(self):
        """Roll 3 dice for Redstone Dice game"""
        dice = [random.randint(1, 6) for _ in range(3)]
        self.dice_game['last_roll'] = dice
        self.dice_game['rolling'] = True
        self.dice_game['roll_start_time'] = pygame.time.get_ticks()
        return dice
    
    def analyze_dice_result(self, dice):
        """
        Analyze dice roll and return combination type and multiplier
        
        Args:
            dice: list of 3 dice values
            
        Returns:
            tuple: (combination_name, multiplier, description)
        """
        dice_sorted = sorted(dice)
        dice_total = sum(dice)
        
        # Check for triple 6s (special case - shuts down casino)
        if dice == [6, 6, 6]:
            return ("Triple Sixes", 20, "INCREDIBLE! Triple sixes! The casino shuts down!")
        
        # Check for any triple
        if dice_sorted[0] == dice_sorted[1] == dice_sorted[2]:
            return ("Triple", 8, f"Amazing! Triple {dice_sorted[0]}s!")
        
        # Check for straights (no wraparound)
        straights = [(1,2,3), (2,3,4), (3,4,5), (4,5,6)]
        if tuple(dice_sorted) in straights:
            return ("Straight", 4, f"Excellent! Straight {dice_sorted[0]}-{dice_sorted[1]}-{dice_sorted[2]}!")
        
        # Check for any pair
        if dice_sorted[0] == dice_sorted[1] or dice_sorted[1] == dice_sorted[2]:
            # We have a pair
            if dice_sorted[0] == dice_sorted[1]:
                pair_value = dice_sorted[0]
            else:
                pair_value = dice_sorted[1]
            
            return ("Pair", 1.5, f"Good! Pair of {pair_value}s!")
        
        # Check for total 15+
        if dice_total >= 15:
            return ("High Total", 1.5, f"Nice roll! Total of {dice_total}!")
        
        # House wins
        return ("House Wins", 0, f"Total {dice_total} - House takes your bet!")
    
    def calculate_dice_payout(self, bet_amount, dice):
        """
        Calculate payout for dice roll, considering house money limitations
        
        Args:
            bet_amount: amount player bet
            dice: list of 3 dice values
            
        Returns:
            tuple: (payout_amount, combination_name, description, game_continues)
        """
        combination, multiplier, description = self.analyze_dice_result(dice)
        
        if multiplier == 0:
            # House wins - player loses bet
            self.character['gold'] -= bet_amount
            self.dice_game['house_money'] += bet_amount
            self.dice_game['loss_streak'] += 1
            self.dice_game['win_streak'] = 0
            return 0, combination, description, True
        
        # Player wins - calculate payout
        gross_winnings = int(bet_amount * multiplier)
        net_winnings = gross_winnings - bet_amount  # Subtract original bet
        
        # Check house money limitation
        if net_winnings > self.dice_game['house_money']:
            net_winnings = self.dice_game['house_money']
            description += f" (House limited payout to {net_winnings} gold!)"
        
        # Apply winnings
        self.character['gold'] += net_winnings
        self.dice_game['house_money'] -= net_winnings
        self.dice_game['win_streak'] += 1
        self.dice_game['loss_streak'] = 0
        
        # Check for game-ending conditions
        game_continues = True
        if combination == "Triple Sixes":
            self.dice_game['game_active'] = False
            game_continues = False
            description += " The casino closes in awe!"
        elif self.dice_game['house_money'] <= 0:
            self.dice_game['game_active'] = False
            game_continues = False
            description += " You've broken the house!"
        
        return net_winnings, combination, description, game_continues
    
    def get_dice_flavor_text(self, won, combination):
        """Get random flavor text for dice results"""
        if not won:
            messages = [
                "The dice gods frown upon you!",
                "Better luck next time, adventurer!",
                "The house always has an edge...",
                "Fortune favors the bold, but not today!",
                "Even heroes have unlucky streaks!"
            ]
        elif combination == "Triple Sixes":
            messages = [
                "BY THE GODS! TRIPLE SIXES!",
                "LEGENDARY! The stuff of tavern tales!",
                "IMPOSSIBLE! Even the dice-keeper is stunned!",
                "MIRACULOUS! The crowd erupts in cheers!"
            ]
        elif combination == "Triple":
            messages = [
                "The crowd cheers your incredible luck!",
                "Triple! Your reputation grows!",
                "Amazing! The dice favor you greatly!",
                "Extraordinary! Even veterans are impressed!"
            ]
        elif combination == "Straight":
            messages = [
                "Skillful! A perfect sequence!",
                "Impressive! The dice align in your favor!",
                "Excellent technique, adventurer!",
                "The gods smile upon your fortune!"
            ]
        else:
            messages = [
                "Lady Luck graces you this day!",
                "A fine roll, worthy adventurer!",
                "Your courage pays off!",
                "Fortune favors the brave!"
            ]
        
        return random.choice(messages)
    
    def can_afford_bet(self, bet_amount):
        """Check if player can afford a bet - GameState Authority"""
        return self.character.get('gold', 0) >= bet_amount
    
    def reset_dice_game(self):
        """Reset dice game for new session"""
        self.dice_game['house_money'] = random.randint(400, 700)
        self.dice_game['game_active'] = True
        self.dice_game['win_streak'] = 0
        self.dice_game['loss_streak'] = 0
    
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
        
        print("🔍 DEBUG: DataManager or item_manager not available")
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
        """Equip an item (weapon or armor)"""
        if category == "weapons":
            self.equipped_weapon = item_name
        elif category == "armor":
            if item_name == "Shield":
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