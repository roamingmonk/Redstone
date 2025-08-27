# game_logic/player_manager.py
"""
Professional Player Data Management System
Handles player character JSON creation, loading, and management
"""

import json
import os
from datetime import datetime
import shutil

class PlayerManager:
    """
    Professional player character management system
    Handles creation, loading, and persistence of player data in JSON format
    Compatible with existing NPC management architecture
    """
    
    def __init__(self):
        self.player_data = None
        self.template_path = os.path.join('data', 'templates', 'player_template.json')
        self.player_file_path = os.path.join('data', 'player', 'current_character.json')
        
        # Ensure directories exist
        self._ensure_directories()
        
        print("🎭 Player Manager initialized - Ready for character management!")
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            os.path.join('data', 'templates'),
            os.path.join('data', 'player')
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 Created directory: {directory}")
    
    def create_player_from_template(self, character_data, game_state):
        """
        Create player JSON file from template using character creation data
        
        Args:
            character_data (dict): Data from game_state.character
            game_state: Current game state for additional data
            
        Returns:
            bool: True if creation successful, False otherwise
        """
        try:
            # Load template
            if not os.path.exists(self.template_path):
                print(f"❌ Template file not found: {self.template_path}")
                return False
                
            with open(self.template_path, 'r') as f:
                player_template = json.load(f)
            
            # Fill in character creation data
            player_template['name'] = character_data.get('name', 'Unknown Adventurer')
            player_template['stats'] = {
                'strength': character_data.get('strength', 10),
                'dexterity': character_data.get('dexterity', 10),
                'constitution': character_data.get('constitution', 10),
                'intelligence': character_data.get('intelligence', 10),
                'wisdom': character_data.get('wisdom', 10),
                'charisma': character_data.get('charisma', 10)
            }
            
            # Player-specific data
            player_template['player_data']['gender'] = character_data.get('gender', 'male')
            player_template['player_data']['trinket'] = character_data.get('trinket', 'None')
            player_template['player_data']['creation_date'] = datetime.now().isoformat()
            
            # Portrait data (if available)
            if hasattr(game_state, 'selected_portrait'):
                player_template['player_data']['portraits']['selected'] = game_state.selected_portrait
            
            # Hit points and derived stats
            hit_points = character_data.get('hit_points', 10)
            player_template['progression']['hit_points']['current'] = hit_points
            player_template['progression']['hit_points']['maximum'] = hit_points
            
            # Starting inventory
            player_template['inventory']['gold'] = character_data.get('gold', 50)
            
            # Add trinket to items if present
            trinket = character_data.get('trinket')
            if trinket and trinket != 'None':
                player_template['inventory']['items'] = [trinket]
            
            # Dynamic description based on character
            name = character_data.get('name', 'Unknown')
            gender_pronoun = 'his' if character_data.get('gender') == 'male' else 'her'
            player_template['description'] = f"{name} stands ready to prove {gender_pronoun} worth in the dangerous world of Redstone"
            
            # Save the completed player file
            with open(self.player_file_path, 'w') as f:
                json.dump(player_template, f, indent=2)
            
            # Load the created data
            self.player_data = player_template
            
            print(f"✅ Player character created: {player_template['name']}")
            print(f"📄 Saved to: {self.player_file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating player character: {e}")
            return False
    
    def load_player(self):
        """Load existing player character from JSON file"""
        try:
            if not os.path.exists(self.player_file_path):
                print("ℹ️ No existing player character found")
                return None
                
            with open(self.player_file_path, 'r') as f:
                self.player_data = json.load(f)
            
            print(f"✅ Player character loaded: {self.player_data.get('name', 'Unknown')}")
            return self.player_data
            
        except Exception as e:
            print(f"❌ Error loading player character: {e}")
            return None
    
    def get_player(self):
        """Get current player data"""
        return self.player_data
    
    def get_player_name(self):
        """Get player name (compatible with NPC manager interface)"""
        return self.player_data.get('name', 'Unknown') if self.player_data else 'Unknown'
    
    def get_player_description(self):
        """Get player description (compatible with NPC manager interface)"""
        return self.player_data.get('description', 'A brave adventurer') if self.player_data else 'A brave adventurer'
    
    def get_player_stats(self):
        """Get player stats dictionary"""
        if self.player_data:
            return self.player_data.get('stats', {})
        return {}
    
    def get_player_equipment(self):
        """Get player equipment dictionary"""
        if self.player_data:
            return self.player_data.get('equipment', {})
        return {}
    
    def get_player_inventory(self):
        """Get player inventory dictionary"""
        if self.player_data:
            return self.player_data.get('inventory', {})
        return {}
    
    def update_player_gold(self, amount):
        """Update player gold and save to file"""
        if self.player_data:
            self.player_data['inventory']['gold'] = amount
            self.save_player()
    
    def update_player_inventory(self, inventory_data):
        """Update player inventory and save to file"""
        if self.player_data:
            self.player_data['inventory'].update(inventory_data)
            self.save_player()
    
    def save_player(self):
        """Save current player data to JSON file"""
        if self.player_data:
            try:
                with open(self.player_file_path, 'w') as f:
                    json.dump(self.player_data, f, indent=2)
                return True
            except Exception as e:
                print(f"❌ Error saving player data: {e}")
                return False
        return False
    
    def delete_player(self):
        """Delete current player character file"""
        try:
            if os.path.exists(self.player_file_path):
                os.remove(self.player_file_path)
                print("🗑️ Player character deleted")
            self.player_data = None
        except Exception as e:
            print(f"❌ Error deleting player character: {e}")
    
    def player_exists(self):
        """Check if a player character file exists"""
        return os.path.exists(self.player_file_path)
    
    def get_player_for_party_display(self):
        """
        Get player data formatted for party display systems
        Compatible with existing party management code
        """
        if not self.player_data:
            return None
            
        return {
            'id': 'player',
            'name': self.get_player_name(),
            'class': self.player_data.get('class', 'fighter'),
            'stats': self.get_player_stats(),
            'equipment': self.get_player_equipment(),
            'hit_points': self.player_data.get('progression', {}).get('hit_points', {}),
            'is_player': True
        }
    
    def sync_with_game_state(self, game_state):
        """
        Synchronize player JSON with current game_state for backwards compatibility
        This allows existing code to continue working while we transition
        """
        if not self.player_data:
            return
            
        # Update game_state.character with JSON data
        game_state.character.update({
            'name': self.player_data.get('name'),
            'gender': self.player_data.get('player_data', {}).get('gender'),
            'trinket': self.player_data.get('player_data', {}).get('trinket'),
            'hit_points': self.player_data.get('progression', {}).get('hit_points', {}).get('maximum', 10),
            'gold': self.player_data.get('inventory', {}).get('gold', 0),
            **self.player_data.get('stats', {})
        })
        
        # Update game_state.inventory with JSON data
        game_state.inventory = self.player_data.get('inventory', {})
        
        print("🔄 Game state synchronized with player JSON")

    def update_player_gold(self, new_amount):
        """Update player gold and immediately save to file"""
        if self.player_data:
            self.player_data['inventory']['gold'] = new_amount
            self.save_player()
            print(f"💰 Player gold updated: {new_amount}")
            return True
        return False
    
    def add_player_gold(self, amount):
        """Add gold to player's current amount"""
        if self.player_data:
            current_gold = self.player_data['inventory']['gold']
            new_gold = current_gold + amount
            return self.update_player_gold(new_gold)
        return False
    
    def subtract_player_gold(self, amount):
        """Subtract gold from player's current amount"""
        if self.player_data:
            current_gold = self.player_data['inventory']['gold']
            if current_gold >= amount:
                new_gold = current_gold - amount
                return self.update_player_gold(new_gold)
            else:
                print(f"❌ Insufficient gold: {current_gold} < {amount}")
                return False
        return False
    
    def update_player_inventory_item(self, category, items_list):
        """Update a specific inventory category and save immediately"""
        if self.player_data:
            valid_categories = ['items', 'weapons', 'armor', 'consumables']
            if category in valid_categories:
                self.player_data['inventory'][category] = items_list
                self.save_player()
                print(f"📦 Player {category} updated: {len(items_list)} items")
                return True
            else:
                print(f"❌ Invalid inventory category: {category}")
        return False
    
    def add_player_item(self, item_name, category='items'):
        """Add single item to player inventory"""
        if self.player_data:
            if category not in self.player_data['inventory']:
                self.player_data['inventory'][category] = []
            
            self.player_data['inventory'][category].append(item_name)
            self.save_player()
            print(f"➕ Added {item_name} to {category}")
            return True
        return False
    
    def remove_player_item(self, item_name, category='items'):
        """Remove single item from player inventory"""
        if self.player_data:
            if category in self.player_data['inventory']:
                inventory_list = self.player_data['inventory'][category]
                if item_name in inventory_list:
                    inventory_list.remove(item_name)
                    self.save_player()
                    print(f"➖ Removed {item_name} from {category}")
                    return True
                else:
                    print(f"❌ Item not found: {item_name} in {category}")
            else:
                print(f"❌ Category not found: {category}")
        return False
    
    def add_party_member(self, npc_id):
        """Add NPC to party and save immediately"""
        if self.player_data:
            # Initialize party_members if it doesn't exist
            if 'party_members' not in self.player_data:
                self.player_data['party_members'] = []
            
            party_members = self.player_data['party_members']
            if npc_id not in party_members:
                party_members.append(npc_id)
                self.save_player()
                print(f"👥 Added {npc_id} to party")
                return True
            else:
                print(f"❌ {npc_id} already in party")
        return False
    
    def remove_party_member(self, npc_id):
        """Remove NPC from party and save immediately"""
        if self.player_data:
            if 'party_members' in self.player_data:
                party_members = self.player_data['party_members']
                if npc_id in party_members:
                    party_members.remove(npc_id)
                    self.save_player()
                    print(f"👥 Removed {npc_id} from party")
                    return True
                else:
                    print(f"❌ {npc_id} not in party")
            else:
                print("❌ No party members to remove")
        return False
    
    def update_equipment(self, equipment_slot, item_name):
        """Update equipped item and save immediately"""
        if self.player_data:
            valid_slots = ['weapon', 'armor', 'shield']
            if equipment_slot in valid_slots:
                self.player_data['equipment'][equipment_slot] = item_name
                self.save_player()
                print(f"⚔️ Equipped {item_name} as {equipment_slot}")
                return True
            else:
                print(f"❌ Invalid equipment slot: {equipment_slot}")
        return False
    
    def update_hit_points(self, current_hp, max_hp=None):
        """Update player hit points and save immediately"""
        if self.player_data:
            self.player_data['progression']['hit_points']['current'] = current_hp
            if max_hp is not None:
                self.player_data['progression']['hit_points']['maximum'] = max_hp
            self.save_player()
            print(f"❤️ Hit points updated: {current_hp}")
            return True
        return False
    
    def get_player_gold(self):
        """Get current player gold amount"""
        if self.player_data:
            return self.player_data['inventory']['gold']
        return 0
    
    def get_party_members(self):
        """Get current party members list"""
        if self.player_data:
            return self.player_data.get('party_members', [])
        return []
    
    def get_player_inventory_category(self, category):
        """Get items from specific inventory category"""
        if self.player_data:
            return self.player_data['inventory'].get(category, [])
        return []
    
    def can_afford(self, amount):
        """Check if player can afford a purchase"""
        return self.get_player_gold() >= amount

def test_player_updates():
    """Test function to verify real-time updates work"""
    print("Testing player manager updates...")
    
    # Test gold update
    initial_gold = player_manager.get_player_gold()
    print(f"Initial gold: {initial_gold}")
    
    player_manager.subtract_player_gold(10)
    new_gold = player_manager.get_player_gold()
    print(f"After spending 10: {new_gold}")
    
    # Test adding item
    player_manager.add_player_item("Test Item", "items")
    items = player_manager.get_player_inventory_category("items")
    print(f"Items: {items}")

# Global player manager instance
player_manager = PlayerManager()

# Uncomment this line to run the test:
test_player_updates()