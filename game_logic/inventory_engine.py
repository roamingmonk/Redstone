# game_logic/inventory_engine.py
"""
Professional Inventory Engine - REFACTORED Single Data Authority Pattern
Handles all inventory business logic separated from UI presentation

REFACTORED ARCHITECTURE:
- GameState is the SINGLE source of truth for all data
- InventoryEngine provides ONLY business logic
- NO data storage in the engine itself
- All data operations go through GameState reference
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime

class InventoryEngine:
    """
    Professional inventory management system for Terror in Redstone
    
    Handles all inventory operations with clean separation from UI.
    Integrates with existing ItemManager and PlayerManager systems.
    """
    
    def __init__(self, game_state_ref, item_manager_ref):
        #self.data_manager = data_manager
        #self.player_manager = player_manager
        self.game_state = game_state_ref
        self.item_manager = item_manager_ref
        
        # Equipment slot configuration (expandable design)
        self.equipment_slots = {
            'weapon': {'display_name': 'Weapon', 'category': 'weapons'},
            'armor': {'display_name': 'Armor', 'category': 'armor'},
            'shield': {'display_name': 'Shield', 'category': 'armor'}
        }
        
        print("⚔️ InventoryEngine initialized - Ready for professional inventory management!")
    
    # ==========================================
    # CORE INVENTORY OPERATIONS
    # ==========================================
    
    def add_item(self, item_id: str, quantity: int = 1, category: Optional[str] = None) -> bool:
        """
        Add item(s) to player inventory with automatic categorization
        
        Args:
            item_id: ID of item to add
            quantity: Number of items to add
            category: Optional category override
            
        Returns:
            bool: True if successful, False if failed
        """
        try:
            # Get item template from ItemManager for validation
            item_template = self._get_item_template(item_id)
            if not item_template:
                print(f"❌ Cannot add unknown item: {item_id}")
                return False
            
            # Determine category from item template if not provided
            if not category:
                category = self._determine_item_category(item_template)
            
           # NEW: Access GameState inventory directly (it's the authority)
            if not hasattr(self.game_state, 'inventory') or not self.game_state.inventory:
                print("❌ No player inventory found")
                return False

            # Add to GameState inventory (the authoritative data)
            category_key = self.game_state.inventory[category_key] =[]
            
            if category_key not in self.game_state.inventory:
                self.game_state.inventory[category_key] = []
            
            # Add items (with stacking support)
            for _ in range(quantity):
                self.game_state.inventory[category_key].append(item_template['name'])
            
            # Update player data
            #self.player_manager.update_player_inventory(inventory)
            
            item_name = item_template.get('name', item_id)
            qty_text = f"{quantity}x " if quantity > 1 else ""
            print(f"✅ Added {qty_text}{item_name} to inventory ({category})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding item {item_id}: {e}")
            return False
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Remove item(s) from player inventory
        
        Args:
            item_name: Display name of item to remove
            quantity: Number of items to remove
            
        Returns:
            bool: True if successful, False if not enough items
        """
        try:
            player_data = self.player_manager.get_player()
            if not player_data or 'inventory' not in player_data:
                return False
            
            inventory = player_data['inventory']
            
            # Find and remove items from all categories
            total_removed = 0
            for category_key in ['weapons', 'armor', 'consumables', 'items']:
                if category_key in inventory:
                    items_in_category = inventory[category_key]
                    
                    while total_removed < quantity and item_name in items_in_category:
                        items_in_category.remove(item_name)
                        total_removed += 1
            
            if total_removed > 0:
                self.player_manager.update_player_inventory(inventory)
                qty_text = f"{total_removed}x " if total_removed > 1 else ""
                print(f"✅ Removed {qty_text}{item_name} from inventory")
                return total_removed == quantity
            else:
                print(f"⚠️ Item not found in inventory: {item_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error removing item {item_name}: {e}")
            return False
    
    def discard_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Discard item(s) from inventory (same as remove, but with different messaging)
        """
        if self.remove_item(item_name, quantity):
            qty_text = f"{quantity}x " if quantity > 1 else ""
            print(f"🗑️ Discarded {qty_text}{item_name}")
            return True
        return False
    
    def consume_item(self, item_name: str) -> bool:
        """
        Consume a consumable item (food, potion, etc.)
        
        Args:
            item_name: Name of item to consume
            
        Returns:
            bool: True if consumed successfully
        """
        try:
            # Check if item exists in consumables
            if not self.has_item(item_name, category='consumables'):
                print(f"⚠️ No {item_name} available to consume")
                return False
            
            # Remove item from inventory
            if self.remove_item(item_name, 1):
                print(f"🍺 Consumed {item_name}")
                
                # TODO: Apply item effects (Session 8+)
                # This is where we'll add healing, buffs, etc.
                self._apply_consumable_effects(item_name)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error consuming item {item_name}: {e}")
            return False
    
    # ==========================================
    # EQUIPMENT OPERATIONS
    # ==========================================
    
    def equip_item(self, item_name: str) -> bool:
        """
        Equip an item from inventory to appropriate equipment slot
        
        Args:
            item_name: Name of item to equip
            
        Returns:
            bool: True if equipped successfully
        """
        try:
            # Check if player has the item
            if not self.has_item(item_name):
                print(f"⚠️ {item_name} not found in inventory")
                return False
            
            # Determine what type of equipment this is
            equipment_slot = self._determine_equipment_slot(item_name)
            if not equipment_slot:
                print(f"⚠️ {item_name} cannot be equipped")
                return False
            
            # Get current equipment
            player_data = self.player_manager.get_player()
            if not player_data:
                return False
            
            equipment = player_data.get('equipment', {})
            
            # Unequip current item in that slot (if any)
            current_item = equipment.get(equipment_slot)
            if current_item:
                self._unequip_to_inventory(current_item, equipment_slot)
            
            # Remove new item from inventory
            if self.remove_item(item_name, 1):
                # Equip the new item
                equipment[equipment_slot] = item_name
                self.player_manager.update_equipment(equipment_slot, item_name)
                
                print(f"⚔️ Equipped {item_name} as {equipment_slot}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error equipping item {item_name}: {e}")
            return False
    
    def unequip_item(self, equipment_slot: str) -> bool:
        """
        Unequip an item from equipment slot back to inventory
        
        Args:
            equipment_slot: Slot to unequip ('weapon', 'armor', 'shield')
            
        Returns:
            bool: True if unequipped successfully
        """
        try:
            player_data = self.player_manager.get_player()
            if not player_data:
                return False
            
            equipment = player_data.get('equipment', {})
            current_item = equipment.get(equipment_slot)
            
            if not current_item:
                print(f"⚠️ No item equipped in {equipment_slot} slot")
                return False
            
            # Add item back to inventory
            item_template = self._find_item_by_name(current_item)
            if item_template:
                category = self._determine_item_category(item_template)
                if self.add_item(item_template['id'], 1, category):
                    # Clear equipment slot
                    equipment[equipment_slot] = None
                    self.player_manager.update_equipment(equipment_slot, None)
                    
                    print(f"📦 Unequipped {current_item} from {equipment_slot}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error unequipping {equipment_slot}: {e}")
            return False
    
    # ==========================================
    # INVENTORY QUERY OPERATIONS
    # ==========================================
    
    def get_weapons(self) -> List[str]:
        """Get list of all weapons in inventory"""
        return self._get_items_by_category('weapons')
    
    def get_armor(self) -> List[str]:
        """Get list of all armor in inventory"""
        return self._get_items_by_category('armor')
    
    def get_consumables(self) -> List[str]:
        """Get list of all consumables in inventory"""
        return self._get_items_by_category('consumables')
    
    def get_items(self) -> List[str]:
        """Get list of all miscellaneous items in inventory"""
        return self._get_items_by_category('items')
    
    def get_equipped_gear(self) -> Dict[str, Optional[str]]:
        """
        Get all currently equipped items
        
        Returns:
            Dict mapping slot names to equipped item names
        """
        try:
            player_data = self.player_manager.get_player()
            if not player_data:
                return {}
            
            equipment = player_data.get('equipment', {})
            return {
                'weapon': equipment.get('weapon'),
                'armor': equipment.get('armor'),
                'shield': equipment.get('shield')
            }
            
        except Exception as e:
            print(f"❌ Error getting equipped gear: {e}")
            return {}
    
    def has_item(self, item_name: str, quantity: int = 1, category: Optional[str] = None) -> bool:
        """
        Check if player has specified item(s) in inventory
        
        Args:
            item_name: Name of item to check
            quantity: Minimum quantity required
            category: Optional category to search in
            
        Returns:
            bool: True if player has enough of the item
        """
        try:
            player_data = self.player_manager.get_player()
            if not player_data or 'inventory' not in player_data:
                return False
            
            inventory = player_data['inventory']
            count = 0
            
            # Search in specific category or all categories
            categories_to_search = [category] if category else ['weapons', 'armor', 'consumables', 'items']
            
            for cat in categories_to_search:
                if cat in inventory:
                    count += inventory[cat].count(item_name)
            
            return count >= quantity
            
        except Exception as e:
            print(f"❌ Error checking for item {item_name}: {e}")
            return False
    
    def get_item_count(self, item_name: str) -> int:
        """Get total count of specific item in inventory"""
        try:
            player_data = self.player_manager.get_player()
            if not player_data or 'inventory' not in player_data:
                return 0
            
            inventory = player_data['inventory']
            count = 0
            
            for category_key in ['weapons', 'armor', 'consumables', 'items']:
                if category_key in inventory:
                    count += inventory[category_key].count(item_name)
            
            return count
            
        except Exception as e:
            print(f"❌ Error counting item {item_name}: {e}")
            return 0
    
    def get_inventory_summary(self) -> Dict[str, int]:
        """
        Get summary of inventory contents
        
        Returns:
            Dict with category counts and total items
        """
        try:
            player_data = self.player_manager.get_player()
            if not player_data or 'inventory' not in player_data:
                return {'weapons': 0, 'armor': 0, 'consumables': 0, 'items': 0, 'total': 0}
            
            inventory = player_data['inventory']
            summary = {}
            total = 0
            
            for category in ['weapons', 'armor', 'consumables', 'items']:
                count = len(inventory.get(category, []))
                summary[category] = count
                total += count
            
            summary['total'] = total
            return summary
            
        except Exception as e:
            print(f"❌ Error getting inventory summary: {e}")
            return {'weapons': 0, 'armor': 0, 'consumables': 0, 'items': 0, 'total': 0}
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    def _get_items_by_category(self, category: str) -> List[str]:
        """Get items from specific inventory category"""
        try:
            player_data = self.player_manager.get_player()
            if not player_data or 'inventory' not in player_data:
                return []
            
            inventory = player_data['inventory']
            return inventory.get(category, [])
            
        except Exception as e:
            print(f"❌ Error getting {category}: {e}")
            return []
    
    def _get_item_template(self, item_id: str) -> Optional[Dict]:
        """Get item template from ItemManager"""
        if not self.item_manager:
            return None
        
        # Search merchant items for the item
        merchant_items = getattr(self.item_manager, 'items_data', {}).get('merchant_items', [])
        for item in merchant_items:
            if item.get('id') == item_id:
                return item
        
        return None
    
    def _find_item_by_name(self, item_name: str) -> Optional[Dict]:
        """Find item template by display name"""
        if not self.item_manager:
            return None
        
        merchant_items = getattr(self.item_manager, 'items_data', {}).get('merchant_items', [])
        for item in merchant_items:
            if item.get('name') == item_name:
                return item
        
        return None
    
    def _determine_item_category(self, item_template: Dict) -> str:
        """Determine inventory category from item template"""
        item_type = item_template.get('type', '').lower()
        
        category_mapping = {
            'weapon': 'weapons',
            'armor': 'armor',
            'consumable': 'consumables',
            'food': 'consumables',
            'potion': 'consumables'
        }
        
        return category_mapping.get(item_type, 'items')
    
    def _get_inventory_category_key(self, category: str) -> str:
        """Map category to inventory key"""
        category_mapping = {
            'weapons': 'weapons',
            'armor': 'armor', 
            'consumables': 'consumables',
            'items': 'items'
        }
        return category_mapping.get(category, 'items')
    
    def _determine_equipment_slot(self, item_name: str) -> Optional[str]:
        """Determine what equipment slot an item goes in"""
        item_template = self._find_item_by_name(item_name)
        if not item_template:
            return None
        
        item_type = item_template.get('type', '').lower()
        
        # Map item types to equipment slots
        slot_mapping = {
            'weapon': 'weapon',
            'armor': 'armor',
            'shield': 'shield'
        }
        
        return slot_mapping.get(item_type)
    
    def _unequip_to_inventory(self, item_name: str, equipment_slot: str) -> bool:
        """Move equipped item back to inventory"""
        item_template = self._find_item_by_name(item_name)
        if item_template:
            category = self._determine_item_category(item_template)
            return self.add_item(item_template['id'], 1, category)
        return False
    
    def _apply_consumable_effects(self, item_name: str):
        """
        Apply effects when consuming items
        TODO: Implement in Session 8+ when we add effects system
        """
        # Placeholder for future effects system
        effects_map = {
            'Strong Ale': '(+5 HP, +1 Morale)',
            'Trail Rations': '(+3 HP)',
            'Healing Potion': '(+10 HP)'
        }
        
        effect = effects_map.get(item_name, '(No effect yet)')
        print(f"   💫 Effect: {effect}")
    
    def can_equip_item(self, item_name: str) -> bool:
        """Check if an item can be equipped"""
        return self._determine_equipment_slot(item_name) is not None
    
    def get_available_equipment_actions(self, item_name: str) -> List[str]:
        """
        Get list of possible actions for an item
        Used by UI to determine what buttons to show
        """
        actions = []
        
        if self.has_item(item_name):
            actions.append('discard')
            
            if self.can_equip_item(item_name):
                actions.append('equip')
            
            # Check if it's consumable
            item_template = self._find_item_by_name(item_name)
            if item_template and item_template.get('type', '').lower() in ['consumable', 'food', 'potion']:
                actions.append('consume')
        
        return actions

# Global inventory engine instance (initialized by DataManager)
inventory_engine = None

def get_inventory_engine():
    """
    Get the global inventory engine instance
    Will be initialized by DataManager integration
    """
    return inventory_engine

def initialize_inventory_engine(game_state_ref, item_manager_ref):
    """
    Initialize the global inventory engine - REFACTORED
    Called by DataManager during system initialization
    
    Args:
        game_state_ref: Reference to GameState (the data authority)
        item_manager_ref: Reference to ItemManager
    """
    global inventory_engine
    inventory_engine = InventoryEngine(game_state_ref, item_manager_ref)
    return inventory_engine


# Development and testing utilities
if __name__ == "__main__":
    print("🧪 InventoryEngine Development Test")
    print("=" * 50)
    
    # Note: This would need proper DataManager and PlayerManager instances to run
    print("InventoryEngine requires DataManager and PlayerManager integration")
    print("Run via main game for full functionality testing")
    
    print("\n✅ InventoryEngine module loaded successfully!")