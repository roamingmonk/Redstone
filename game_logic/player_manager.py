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
        if self.player_data:
            self.player_data['inventory']['gold'] = new_amount
            self.save_player()

    def update_player_inventory(self, inventory_changes):
        if self.player_data:
            self.player_data['inventory'].update(inventory_changes)
            self.save_player()

    def add_party_member(self, npc_id):
        if self.player_data:
            party_members = self.player_data.get('party_members', [])
            if npc_id not in party_members:
                party_members.append(npc_id)
                self.player_data['party_members'] = party_members
                self.save_player()

    def update_equipment(self, equipment_slot, item_name):
        if self.player_data:
            self.player_data['equipment'][equipment_slot] = item_name
            self.save_player()

# Global player manager instance
player_manager = PlayerManager()