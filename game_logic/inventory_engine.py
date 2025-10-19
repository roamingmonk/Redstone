# game_logic/inventory_engine.py
"""
Professional Inventory Engine - REFACTORED Single Data Authority Pattern
Handles all inventory business logic separated from UI presentation

ARCHITECTURE BREAKTHROUGH:
- GameState is the SINGLE source of truth for all data
- InventoryEngine provides ONLY business logic
- NO data storage in the engine itself
- All data operations go through GameState reference
- ZERO PlayerManager dependencies!
"""

import pygame
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from utils.constants import (GREEN)

class InventoryEngine:
    """
    Professional inventory management system for Terror in Redstone
    
    Handles all inventory operations with clean separation from UI.
    Uses pure GameState authority - no competing data sources!
    """
    
    def __init__(self, game_state_ref, item_manager_ref, event_manager_ref=None):
        """
        Initialize inventory engine with GameState authority
        
        Args:
            game_state_ref: Reference to GameState (THE data authority)
            item_manager_ref: Reference to ItemManager for item templates
        """

        print(f"🔍 DEBUG InventoryEngine.__init__ called:")
        print(f"   game_state_ref: {game_state_ref is not None}")
        print(f"   item_manager_ref: {item_manager_ref is not None}")
        print(f"   event_manager_ref: {event_manager_ref}")

        self.game_state = game_state_ref  # THE single source of truth
        self.item_manager = item_manager_ref #used to store the reference
        self.event_manager = event_manager_ref  # Store event manager

        # Equipment slot configuration (expandable design)
        self.equipment_slots = {
            'weapon': {'display_name': 'Weapon', 'category': 'weapons'},
            'armor': {'display_name': 'Armor', 'category': 'armor'},
            'shield': {'display_name': 'Shield', 'category': 'armor'}
        }
        
        print("⚔️ InventoryEngine initialized - Pure GameState Authority Pattern!")
        #print("   📋 Data Authority: GameState")
        print("   🏪 Item Source: ItemManager")
    
        # Register events if event_manager provided
        if event_manager_ref:
            self._register_inventory_events(event_manager_ref)

        # if hasattr(game_state_ref, 'event_manager'):
        #     self._register_inventory_events(game_state_ref.event_manager)

    # ==========================================
    # CORE INVENTORY OPERATIONS
    # ==========================================
    
    def _register_inventory_events(self, event_manager):
        """Self-register inventory events with EventManager"""
        event_manager.register("INVENTORY_EQUIP_ITEM", self.handle_inventory_equip_event)
        event_manager.register("INVENTORY_UNEQUIP_ITEM", self.handle_inventory_unequip_event)
        event_manager.register("INVENTORY_CONSUME_ITEM", self.handle_inventory_consume_event)
        event_manager.register("INVENTORY_DISCARD_ITEM", self.handle_inventory_discard_event)
        print("✅ InventoryEngine self-registered for inventory action events")

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
            
            # Access GameState inventory directly (it's the authority!)
            if not hasattr(self.game_state, 'inventory') or not self.game_state.inventory:
                print("❌ No player inventory found in GameState")
                return False

            # Add to GameState inventory (the authoritative data)
            # category is already normalized by _determine_item_category()
            if category not in self.game_state.inventory:
                self.game_state.inventory[category] = []
            
            # Add items (with stacking support)
            for _ in range(quantity):
                self.game_state.inventory[category].append(item_template['id'])
            
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
            if not hasattr(self.game_state, 'inventory'):
                return False
            
            inventory = self.game_state.inventory
            
            # Find and remove items from all categories
            total_removed = 0
            for category_key in ['weapons', 'armor', 'consumables', 'items']:
                if category_key in inventory:
                    items_in_category = inventory[category_key]
                    
                    while total_removed < quantity and item_name in items_in_category:
                        items_in_category.remove(item_name)
                        total_removed += 1
            
            if total_removed > 0:
                qty_text = f"{total_removed}x " if total_removed > 1 else ""
                print(f"✅ Removed {qty_text}{item_name} from inventory")
                return total_removed == quantity
            else:
                print(f"⚠️ Item not found in inventory: {item_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error removing item {item_name}: {e}")
            return False
    
    def equip_item(self, item_id: str, category: str) -> bool:
        """
        Equip an item with validation and business logic
        
        Args:
            item_id: ID of item to equip
            category: Category of item (weapons, armor, items, consumables)
            
        Returns:
            bool: True if successful
        """
        try:
            # Validate item exists in inventory
            if not self.has_item(item_id, category):
                print(f"⚠️ Cannot equip {item_id} - not in inventory")
                return False
            
            # Handle equipment based on category
            if category == "weapons":
                # Unequip current weapon if any
                current_weapon = self.game_state.character.get('equipped_weapon')
                if current_weapon:
                    print(f"🔄 Unequipping {current_weapon}")
                
                # Equip new weapon
                self.game_state.character['equipped_weapon'] = item_id
                print(f"⚔️ Equipped weapon: {item_id}")
                return True
                
            elif category == "armor":
                # Determine if shield or body armor
                subcategory = self.get_item_subcategory(item_id)
                
                if subcategory == "shield":
                    current_shield = self.game_state.character.get('equipped_shield')
                    if current_shield:
                        print(f"🔄 Unequipping shield {current_shield}")
                    self.game_state.character['equipped_shield'] = item_id
                    print(f"🛡️ Equipped shield: {item_id}")
                else:
                    current_armor = self.game_state.character.get('equipped_armor')
                    if current_armor:
                        print(f"🔄 Unequipping armor {current_armor}")
                    self.game_state.character['equipped_armor'] = item_id
                    print(f"🛡️ Equipped armor: {item_id}")
                return True
            
            elif category == "items":
                # Future: Handle equippable items (rings, amulets, etc.)
                print(f"ℹ️ Item equipment not yet implemented for: {item_id}")
                return False
            
            elif category == "consumables":
                # Future: Handle quick-slot consumables
                print(f"ℹ️ Consumable quick-slots not yet implemented for: {item_id}")
                return False
            
            return False
            
        except Exception as e:
            print(f"❌ Error equipping item: {e}")
            return False
    
    def unequip_item(self, item_id: str) -> bool:
        """
        Unequip an item with validation
        
        Args:
            item_id: ID of item to unequip
            
        Returns:
            bool: True if successful
        """
        try:
            # Check all equipment slots
            if item_id == self.game_state.character.get('equipped_weapon'):
                self.game_state.character['equipped_weapon'] = None
                print(f"⚔️ Unequipped weapon: {item_id}")
                return True
            elif item_id == self.game_state.character.get('equipped_armor'):
                self.game_state.character['equipped_armor'] = None
                print(f"🛡️ Unequipped armor: {item_id}")
                return True
            elif item_id == self.game_state.character.get('equipped_shield'):
                self.game_state.character['equipped_shield'] = None
                print(f"🛡️ Unequipped shield: {item_id}")
                return True
            
            print(f"⚠️ Item {item_id} is not equipped")
            return False
            
        except Exception as e:
            print(f"❌ Error unequipping item: {e}")
            return False
    
    def consume_item(self, item_id: str, target_member_id: str = None) -> dict:
        """
        Consume an item and apply its effects
        
        Args:
            item_id: ID of item to consume
            target_member_id: ID of party member to apply effect to ('player', 'gareth', etc.)
            
        Returns:
            dict: Results including success, effect_type, amount, target
        """
        try:
            # Get item template to check consumable effects
            item_template = self._get_item_template(item_id)
            if not item_template:
                return {'success': False, 'message': 'Unknown item'}
            
            # Check if item exists in inventory
            found_in_category = None
            for category in ['consumables', 'items']:
                if item_id in self.game_state.inventory.get(category, []):
                    found_in_category = category
                    break
            
            if not found_in_category:
                return {'success': False, 'message': 'Item not in inventory'}
            
            # Get consumable effects
            consumable_effects = item_template.get('consumable_effects', {})
            if not consumable_effects:
                return {'success': False, 'message': 'Item is not consumable'}
            
            # Check if target is specified for targeted effects
            if 'healing' in consumable_effects and not target_member_id:
                return {'success': False, 'message': 'Select party member'}
            
            # Apply effects based on type
            result = {'success': True, 'effects': []}
            
            # Handle healing
            if 'healing' in consumable_effects:
                healing_formula = consumable_effects['healing']
                healing_result = self._apply_healing(healing_formula, target_member_id)
                result['effects'].append(healing_result)
            
            # Remove item from inventory
            self.game_state.inventory[found_in_category].remove(item_id)
            
            # Track consumption statistics
            current = self.game_state.player_statistics.get('items_consumed', 0)
            self.game_state.player_statistics['items_consumed'] = current + 1
            
            item_name = item_template.get('name', item_id)
            print(f"🍺 Consumed: {item_name}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error consuming item: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': f'Error: {e}'}
    
    #TODO should we centralize healing ??
    def _apply_healing(self, healing_formula: str, target_member_id: str) -> dict:
        """
        Apply healing to a party member using dice notation
        
        Args:
            healing_formula: Dice notation (e.g., "2d4+2")
            target_member_id: ID of target ('player', 'gareth', etc.)
            
        Returns:
            dict: Healing details
        """
        from utils.dice_roller import roll_dice, format_roll_result
        
        # Roll healing amount
        total, rolls, modifier = roll_dice(healing_formula)
        
        # Get target's current and max HP
        if target_member_id == 'player':
            current_hp = self.game_state.character.get('current_hp', 10)
            max_hp = self.game_state.character.get('hit_points', 10)
            target_name = self.game_state.character.get('name', 'Player')
        else:
            # Find party member
            current_hp = 0
            max_hp = 0
            target_name = target_member_id
            for member in self.game_state.party_member_data:
                if member.get('id') == target_member_id:
                    current_hp = member.get('current_hp', 10)
                    max_hp = member.get('hp', member.get('hit_points', 10))
                    target_name = member.get('name', target_member_id)
                    break
        
        # Calculate actual healing (can't exceed max HP)
        old_hp = current_hp
        new_hp = min(current_hp + total, max_hp)
        actual_healing = new_hp - old_hp
        
        # Apply healing to game state
        if target_member_id == 'player':
            self.game_state.character['current_hp'] = new_hp
        else:
            for member in self.game_state.party_member_data:
                if member.get('id') == target_member_id:
                    member['current_hp'] = new_hp
                    break
        
        # Console output
        roll_str = format_roll_result(healing_formula, total, rolls, modifier)
        print(f"🎲 Healing Roll: {roll_str}")
        print(f"💚 {target_name}: {old_hp}/{max_hp} HP → {new_hp}/{max_hp} HP (+{actual_healing} HP)")
        
        return {
            'type': 'healing',
            'target': target_name,
            'target_id': target_member_id,
            'amount': actual_healing,
            'rolled': total,
            'old_hp': old_hp,
            'new_hp': new_hp,
            'max_hp': max_hp
        }
    
    def discard_item(self, item_id: str) -> bool:
        """  Discard an item permanently with validation
             Args:item_id: ID of item to discard (NOT display name)
        Returns:bool: True if successful, False if protected or not found
        """
        try:
            # PROTECTION: Check if item is a trinket (special narrative item)
            item_def = self._get_item_template(item_id)
            if item_def:
                # Check subcategory for trinket protection
                if item_def.get('subcategory') == 'trinket':
                    print(f"🚫 Cannot discard trinket: {item_def.get('name', item_id)}")
                    return False
            else:
                # If no item def found, it might be a display name - try to find the ID
                print(f"⚠️ WARNING: Received possible display name instead of ID: {item_id}")
                # For now, let it through (but log the warning)
            
            # Unequip if currently equipped
            self.unequip_item(item_id)
            
            # Remove from inventory
            for category in ['weapons', 'armor', 'items', 'consumables']:
                if item_id in self.game_state.inventory.get(category, []):
                    self.game_state.inventory[category].remove(item_id)
                    
                    # Track discard statistics
                    self.game_state.player_statistics['items_discarded'] += 1
                    
                    print(f"🗑️ Discarded: {item_id}")
                    return True
            
            print(f"⚠️ Cannot discard {item_id} - not in inventory")
            return False
            
        except Exception as e:
            print(f"❌ Error discarding item: {e}")
            return False
        
    def _find_item_id_by_name(self, display_name: str) -> Optional[str]:
        """Convert display name to item ID (case-insensitive)"""
        if self.item_manager:
            # Search through all items to find matching name (case-insensitive)
            for item in self.item_manager.get_all_items():
                if item.get('name', '').lower() == display_name.lower():
                    return item.get('id')
        
        # Fallback: if display_name IS already an ID, return it
        return display_name

    def handle_inventory_equip_event(self, event_data):
        """Handle INVENTORY_EQUIP_ITEM event"""
        selected_item_name = getattr(self.game_state, 'inventory_selected', None)
        current_tab = getattr(self.game_state, 'inventory_tab', 'weapons')
        
        if selected_item_name:
            # Convert display name to ID
            item_id = self._find_item_id_by_name(selected_item_name)  # FIXED TYPO
            if not item_id:
                print(f"⚠️ Could not find item ID for: {selected_item_name}")
                return
            
            category_map = {'weapons': 'weapons', 'armor': 'armor', 'items': 'items', 'consumables': 'consumables'}
            category = category_map.get(current_tab, 'weapons')
            
            self.equip_item(item_id, category)

    def handle_inventory_unequip_event(self, event_data):
        """Handle INVENTORY_UNEQUIP_ITEM event"""
        selected_item_name = getattr(self.game_state, 'inventory_selected', None)
        
        if selected_item_name:
            item_id = self._find_item_id_by_name(selected_item_name)
            if item_id:
                self.unequip_item(item_id)
            else:
                print(f"⚠️ Could not find item ID for: {selected_item_name}")

    def handle_inventory_consume_event(self, event_data):
        """Handle INVENTORY_CONSUME_ITEM event with party targeting"""
        try:
            selected_item = self.game_state.inventory_selected
            if not selected_item:
                print("⚠️ No item selected to consume")
                self.game_state.inventory_status_message = "Select an item first"
                self.game_state.inventory_status_time = pygame.time.get_ticks()
                return
            
            # Get selected party member from event data
            selected_party_member = event_data.get('target_member_id')
            
            if not selected_party_member:
                print("⚠️ No party member selected for consumable")
                self.game_state.inventory_status_message = "Select Party Member"
                self.game_state.inventory_status_time = pygame.time.get_ticks()
                return
            
            # Consume item with targeting
            result = self.consume_item(selected_item, selected_party_member)
            
            if result.get('success'):
                # Clear selection after successful consumption
                self.game_state.inventory_selected = None
                
                # Get healing details for floating text
                effects = result.get('effects', [])
                if effects:
                    healing_effect = effects[0]  # First effect
                    target_name = healing_effect.get('target', 'Character')
                    amount = healing_effect.get('amount', 0)
                    
                   # Trigger floating text notification
                    if self.event_manager:
                        print(f"🎯 DEBUG: Emitting SHOW_FLOATING_TEXT event for {target_name} +{amount} HP")
                        self.event_manager.emit("SHOW_FLOATING_TEXT", {
                            'text': f"+{amount} HP",
                            'color': GREEN,  
                            'duration': 2000
                        })
                    
                    print(f"✅ Successfully consumed item on {target_name}")
                else:
                    print(f"✅ Successfully consumed item")
                    
            else:
                # Show error message
                message = result.get('message', 'Cannot consume item')
                self.game_state.inventory_status_message = message
                self.game_state.inventory_status_time = pygame.time.get_ticks()
                print(f"❌ Consumption failed: {message}")
                
        except Exception as e:
            print(f"❌ Error in consume event handler: {e}")
            import traceback
            traceback.print_exc()

    def handle_inventory_discard_event(self, event_data):
        """Handle INVENTORY_DISCARD_ITEM event"""
        selected_item_name = getattr(self.game_state, 'inventory_selected', None)
        if selected_item_name:
            item_id = self._find_item_id_by_name(selected_item_name)
            if item_id:
                # Get item info for message
                item_def = self._get_item_template(item_id)
                display_name = item_def.get('name', selected_item_name) if item_def else selected_item_name
                
                success = self.discard_item(item_id)
                if success:
                    self.game_state.inventory_selected = None
                    self.game_state.inventory_status_message = f"Discarded {display_name}"
                    self.game_state.inventory_status_time = pygame.time.get_ticks()
                else:
                    # Check why it failed
                    if item_def and item_def.get('subcategory') == 'trinket':
                        self.game_state.inventory_status_message = "Cannot discard special trinkets"
                    else:
                        self.game_state.inventory_status_message = "Item not found"
                    self.game_state.inventory_status_time = pygame.time.get_ticks()
        
    # ==========================================
    # INVENTORY QUERIES (PURE READ OPERATIONS)
    # ==========================================
    
    def has_item(self, item_id: str, category: Optional[str] = None) -> bool:
        """Check if player has specific item by ID"""
        try:
            if not hasattr(self.game_state, 'inventory'):
                return False
                
            inventory = self.game_state.inventory
            
            if category:
                # Category should already be normalized ('weapons', 'armor', 'consumables', 'items')
                return category in inventory and item_id in inventory[category]
            
            # Search all categories
            for category_list in inventory.values():
                if isinstance(category_list, list) and item_id in category_list:
                    return True
            
            return False
        except Exception as e:
            print(f"❌ Error checking inventory for {item_id}: {e}")
            return False
    
    def get_item_count(self, item_name: str) -> int:
        """Get total count of specific item across all categories"""
        try:
            if not hasattr(self.game_state, 'inventory'):
                return 0
                
            total_count = 0
            for category_list in self.game_state.inventory.values():
                if isinstance(category_list, list):
                    total_count += category_list.count(item_name)
            
            return total_count
        except Exception:
            return 0
    
    def get_inventory_display_data(self) -> Dict[str, List[Dict]]:
        """
        Get formatted inventory data for UI display
        Returns organized data with item counts
        """
        try:
            if not hasattr(self.game_state, 'inventory'):
                return {}
            
            display_data = {}
            
            for category_key, items_list in self.game_state.inventory.items():
                if not isinstance(items_list, list):
                    continue
                
                # Count items and organize by name
                item_counts = {}
                for item_name in items_list:
                    item_counts[item_name] = item_counts.get(item_name, 0) + 1
                
                # Convert to display format
                display_items = []
                for item_name, count in item_counts.items():
                    display_items.append({
                        'name': item_name,
                        'quantity': count,
                        'category': category_key
                    })
                
                display_data[category_key] = display_items
            
            return display_data
        except Exception as e:
            print(f"❌ Error getting inventory display data: {e}")
            return {}
    
    # ==========================================
    # HELPER METHODS (INTERNAL USE ONLY)
    # ==========================================
    
    def _get_item_template(self, item_id: str) -> Optional[Dict]:
        """Get item template from ItemManager"""
        if self.item_manager and hasattr(self.item_manager, 'get_item_by_id'):
            return self.item_manager.get_item_by_id(item_id)
        return None
    
    def _determine_item_category(self, item_template: Dict) -> str:
        """Determine category from item template with validation"""
        category = item_template.get('category', 'items')
        item_id = item_template.get('id', 'unknown')
        
        # Normalize to lowercase
        category = category.lower()
        
        # Valid categories
        valid_categories = ['weapons', 'armor', 'consumables', 'items']
        
        # Check if already valid (plural form)
        if category in valid_categories:
            return category
        
        # Handle singular forms
        singular_to_plural = {
            'weapon': 'weapons',
            'consumable': 'consumables',
            'item': 'items'
        }
        
        if category in singular_to_plural:
            return singular_to_plural[category]
        
        # Invalid category - log error and fallback
        print(f"⚠️ ITEM DATA ERROR: Item '{item_id}' has invalid category '{category}'")
        print(f"   Valid categories: {valid_categories}")
        print(f"   Defaulting to 'items' category")
        return 'items'
    
    def get_item_subcategory(self, item_id):
        """Get subcategory for an item using ItemManager data"""
        item_data = self.item_manager.get_item_by_id(item_id)
        if item_data:
            return item_data.get('subcategory', 'body_armor')
        return 'body_armor'


# ==========================================
# GLOBAL INVENTORY ENGINE MANAGEMENT
# ==========================================

# Global inventory engine instance (initialized by DataManager)
inventory_engine = None

def get_inventory_engine():
    """
    Get the global inventory engine instance
    Will be initialized by DataManager integration
    """
    return inventory_engine

def initialize_inventory_engine(game_state_ref, item_manager_ref, event_manager_ref=None):
    """
    Initialize the global inventory engine with Single Data Authority pattern
    Called by DataManager during system initialization
    
    Args:
        game_state_ref: Reference to GameState (the data authority)
        item_manager_ref: Reference to ItemManager
        event_manager_ref: Reference to EventManager for event registration
    """
    global inventory_engine
    inventory_engine = InventoryEngine(game_state_ref, item_manager_ref, event_manager_ref)
    
    print("🔧 Initialized InventoryEngine with Single Data Authority pattern")
    
    if event_manager_ref:
        print("✅ InventoryEngine initialized with EventManager")
    else:
        print("⚠️ InventoryEngine initialized without EventManager")
    
    return inventory_engine


# Development and testing utilities
if __name__ == "__main__":
    print("🧪 InventoryEngine Development Test")
    print("=" * 50)
    
    print("InventoryEngine follows Single Data Authority pattern:")
    print("- GameState = THE authoritative data source")
    print("- InventoryEngine = Pure business logic processor")
    print("- No data storage in engine itself")
    print("- All operations modify GameState directly")
    
    print("\n✅ InventoryEngine module loaded successfully!")