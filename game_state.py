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
        self.custom_name_text = ""
        self.custom_name_active = False
        
        # Tavern state
        self.party_members = []
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

        # Save/load system state (game mechanics)
        self.load_screen_open = False
        self.load_selected_slot = None
        self.load_status_message = "Select a save file to load or delete"
        self.save_screen_open = False
        self.save_selected_slot = None
        self.save_status_message = "Select a slot to save your game"

        # Gambling state for Redstone Dice
        self.gambling_state = {
            'last_player_dice': [0, 0],
            'last_house_dice': [0, 0],
            'last_result': None,
            'animation_phase': 'waiting',  # 'rolling', 'showing', 'waiting'
            'roll_start_time': 0
        }
        
        # Redstone Dice Game State
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

        # Quest and overlay UI state (game mechanics)
        self.quest_log_open = False
        self.character_sheet_open = False
        self.help_screen_open = False
        
        # *** ADD: Initialize all narrative schema flags ***
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
    


#     def debug_quest_state(self):
#         """Print current quest-relevant flags for debugging - F2 Debug System"""
#         print("\n" + "="*50)
#         print("🔍 QUEST DEBUG STATE (F2)")
#         print("="*50)
        
#         # Core conversation flags
#         print(f"mayor_talked: {getattr(self, 'mayor_talked', False)}")
#         print(f"meredith_talked: {getattr(self, 'meredith_talked', False)}")
#         print(f"garrick_talked: {getattr(self, 'garrick_talked', False)}")
#         print(f"quest_active: {getattr(self, 'quest_active', False)}")
#         print(f"garrick_offered_basement: {getattr(self, 'garrick_offered_basement', False)}")
#         print(f"main_quest_started: {getattr(self, 'main_quest_started', False)}")

#  ###################################################################       
#         core_story_flags = [
#             "main_quest_started",
#             "mayor_talked",
#             "meredith_talked",
#             "meredith_mentioned_mayor",
#             "garrick_talked",
#             "quest_active",
#             "garrick_offered_basement",
#             "completed_basement_combat",
#             "reported_basement_victory",
#         ]
#         self._print_flags("📌 CORE STORY FLAGS", core_story_flags)

#         # Dialogue state (helps spot “stuck in response mode” etc.)
#         print("\n🗣️ DIALOGUE STATE:")
#         for npc in ["meredith", "mayor", "garrick", "gareth"]:
#             in_prog = getattr(self, f"{npc}_dialogue_in_progress", False)
#             showing = getattr(self, f"showing_{npc}_response", False)
#             print(f"  {npc:8s} in_progress={in_prog}  showing_response={showing}")

#         # Sanity checks (the ones that catch your current issue fast)
#         issues = []
#         if getattr(self, "main_quest_started", False) and not getattr(self, "mayor_talked", False):
#             issues.append("main_quest_started=True but mayor_talked=False")

#         if getattr(self, "reported_basement_victory", False) and not getattr(self, "completed_basement_combat", False):
#             issues.append("reported_basement_victory=True without completed_basement_combat=True")

#         # Example guard for Mayor deep-node unlocks; tweak names to your JSON:
#         if getattr(self, "mayor_deep_branch_seen", False) and not getattr(self, "main_quest_started", False):
#             issues.append("Mayor deep branch visible before main_quest_started")

#         print("\n🧪 SANITY CHECKS:")
#         if issues:
#             for i in issues:
#                 print("  - ❌", i)
#         else:
#             print("  - ✅ No issues detected")

# #################################################################
#         # Recruitment flags (narrative schema style)
#         print(f"\n🎯 RECRUITMENT FLAGS:")
#         print(f"gareth_recruited: {getattr(self, 'gareth_recruited', False)}")
#         print(f"elara_recruited: {getattr(self, 'elara_recruited', False)}")
#         print(f"thorman_recruited: {getattr(self, 'thorman_recruited', False)}")
#         print(f"lyra_recruited: {getattr(self, 'lyra_recruited', False)}")
        
#         # Party members list (old system)
#         print(f"\n👥 PARTY MEMBERS LIST:")
#         party_members = getattr(self, 'party_members', [])
#         print(f"party_members: {party_members}")
#         print(f"party count: {len(party_members)}")
        
#         # Recruitment count (computed property)
#         print(f"\n📊 COMPUTED VALUES:")
#         print(f"recruited_count: {self.recruited_count}")
#         print(f"can_recruit_more: {self.can_recruit_more}")
        
#         # Quest manager status
#         if hasattr(self, 'quest_manager'):
#             print(f"\n📋 QUEST MANAGER:")
#             active_quests = self.quest_manager.get_active_quests()
#             print(f"Active quests: {[q.id for q in active_quests]}")
            
#             # Check specific quest objectives
#             party_quest = self.quest_manager.quests.get("party_building")
#             if party_quest:
#                 print(f"Party building quest status: {party_quest.status}")
#                 for obj in party_quest.objectives:
#                     print(f"  - {obj.id}: {obj.completed}")
#         else:
#             print("❌ Quest manager not found!")
        
#         print("="*50 + "\n")

#     def debug_save_state(self):
#         """Print save-relevant data for debugging - F3 Debug System"""
#         print("\n" + "="*50)
#         print("💾 SAVE STATE DEBUG (F3)")
#         print("="*50)
        
#         # Character state
#         print(f"Character name: {getattr(self, 'character', {}).get('name', 'Unknown')}")
#         print(f"Current screen: {getattr(self, 'screen', 'Unknown')}")
#         print(f"Money: {getattr(self, 'money', 0)}")
        
#         # All narrative flags for save
#         from utils.narrative_schema import narrative_schema
#         print(f"\n🚩 ALL NARRATIVE FLAGS:")
#         all_flags = narrative_schema.get_all_flags()
#         for flag in all_flags:
#             value = getattr(self, flag, False)
#             if value:  # Only show flags that are True
#                 print(f"  ✓ {flag}: {value}")
        
#         # Quest save data
#         if hasattr(self, 'quest_manager'):
#             quest_save_data = self.quest_manager.get_quest_data_for_save()
#             print(f"\n📋 QUEST SAVE DATA:")
#             for quest_id, quest_data in quest_save_data.items():
#                 print(f"  {quest_id}: {quest_data['status']}")
        
#         print("="*50 + "\n")