# game_logic/commerce_engine.py
"""
Professional Commerce Engine - Single Data Authority Pattern
Handles all shopping and merchant business logic separated from UI presentation

This follows the new architecture pattern:
- GameState is the SINGLE source of truth for all data
- CommerceEngine provides ONLY business logic
- NO data storage in the engine itself
- All data operations go through GameState reference
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
#from game_logic.commerce_engine import initialize_commerce_engine, get_commerce_engine



class CommerceEngine:
    """
    Professional commerce management system for Terror in Redstone
    
    Handles all shopping operations with clean separation from GameState data.
    Operates as pure business logic processor - no data storage.
    """

    
    def __init__(self, game_state_ref, item_manager_ref):
        """
        Initialize commerce engine with references to data sources
        
        Args:
            game_state_ref: Reference to the GameState instance (THE data authority)
            item_manager_ref: Reference to ItemManager for item templates
        """
        self.game_state = game_state_ref  # THE single source of truth
        self.item_manager = item_manager_ref
        
        print("🛒 CommerceEngine initialized - Ready for professional shopping!")
        print("   📋 Data Authority: GameState")
        print("   🏪 Item Source: ItemManager")
    
    # ==========================================
    # SHOPPING CART OPERATIONS
    # ==========================================
    
    def add_to_cart(self, item_name: str, merchant_id: str = 'garrick_barkeep') -> bool:
        """
        Add item to shopping cart with stock validation
        
        Args:
            item_name: Name of item to add
            merchant_id: Which merchant we're buying from
            
        Returns:
            bool: True if added successfully, False if cannot add
        """
        try:
            # Check if item exists and is available from this merchant
            if not self._is_item_available(item_name, merchant_id):
                print(f"❌ Item '{item_name}' not available from {merchant_id}")
                return False
            
            # Check stock limits
            current_in_cart = self.game_state.shopping_cart.get(item_name, 0)
            stock_limit = self._get_stock_limit(item_name, merchant_id)
            
            if current_in_cart >= stock_limit:
                print(f"❌ Cannot add more {item_name} - stock limit {stock_limit} reached")
                return False
            
            # Add to GameState's shopping cart (the authoritative data)
            if item_name in self.game_state.shopping_cart:
                self.game_state.shopping_cart[item_name] += 1
            else:
                self.game_state.shopping_cart[item_name] = 1
            
            print(f"✅ Added {item_name} to cart! ({current_in_cart + 1}/{stock_limit})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding to cart: {e}")
            return False
    
    def remove_from_cart(self, item_name: str) -> bool:
        """
        Remove one quantity of item from shopping cart
        
        Args:
            item_name: Name of item to remove
            
        Returns:
            bool: True if removed successfully
        """
        try:
            if item_name in self.game_state.shopping_cart and self.game_state.shopping_cart[item_name] > 0:
                self.game_state.shopping_cart[item_name] -= 1
                if self.game_state.shopping_cart[item_name] == 0:
                    del self.game_state.shopping_cart[item_name]
                print(f"✅ Removed {item_name} from cart")
                return True
            else:
                print(f"❌ {item_name} not in cart or already at zero")
                return False
                
        except Exception as e:
            print(f"❌ Error removing from cart: {e}")
            return False
    
    def clear_cart(self) -> None:
        """Clear the entire shopping cart"""
        self.game_state.shopping_cart = {}
        print("🛒 Shopping cart cleared")
    
    def get_cart_total(self, merchant_id: str = 'garrick_barkeep') -> int:
        """
        Calculate total cost of items in cart
        
        Args:
            merchant_id: Which merchant's pricing to use
            
        Returns:
            int: Total cost in gold
        """
        total = 0
        merchant_data = self._get_merchant_data(merchant_id)
        
        if not merchant_data:
            return 0
        
        for item_name, quantity in self.game_state.shopping_cart.items():
            item_cost = self._get_item_cost(item_name, merchant_data)
            total += item_cost * quantity
        
        return total
    
    def get_cart_summary(self) -> List[Dict]:
        """
        Get detailed shopping cart summary for UI display
        
        Returns:
            List of dicts with item details and quantities
        """
        summary = []
        for item_name, quantity in self.game_state.shopping_cart.items():
            item_info = self._get_item_info(item_name)
            if item_info:
                summary.append({
                    'name': item_name,
                    'quantity': quantity,
                    'unit_cost': item_info.get('cost', 0),
                    'total_cost': item_info.get('cost', 0) * quantity,
                    'description': item_info.get('description', '')
                })
        return summary
    
    # ==========================================
    # TRANSACTION PROCESSING
    # ==========================================
    
    def process_purchase(self, merchant_id: str = 'garrick_barkeep') -> Tuple[bool, str]:
        """
        Process the entire shopping cart as one transaction
        
        Args:
            merchant_id: Which merchant to buy from
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate cart is not empty
            if not self.game_state.shopping_cart:
                return False, "Shopping cart is empty!"
            
            # Calculate total cost
            total_cost = self.get_cart_total(merchant_id)
            current_gold = self.game_state.character.get('gold', 0)
            
            # Check affordability
            if total_cost > current_gold:
                return False, f"Not enough gold! Need {total_cost}, have {current_gold}"
            
            # Process each item in cart
            success_count = 0
            merchant_data = self._get_merchant_data(merchant_id)
            
            for item_name, quantity in self.game_state.shopping_cart.items():
                # Find item details for categorization
                item_info = self._find_item_in_merchant_data(item_name, merchant_data)
                if item_info:
                    # Add items to inventory (using GameState's inventory)
                    category = self._determine_inventory_category(item_info['type'])
                    for _ in range(quantity):
                        self.game_state.inventory[category].append(item_name)
                    success_count += quantity
            
            # Deduct gold (modify GameState directly - it's the authority)
            self.game_state.character['gold'] -= total_cost
            
            # Clear cart after successful purchase
            self.clear_cart()
            
            return True, f"Purchase complete! Bought {success_count} items for {total_cost} gold."
            
        except Exception as e:
            print(f"❌ Transaction error: {e}")
            return False, f"Transaction failed: {str(e)}"
    
    def can_afford_cart(self, merchant_id: str = 'garrick_barkeep') -> bool:
        """
        Check if player can afford current cart contents
        
        Args:
            merchant_id: Which merchant's pricing to use
            
        Returns:
            bool: True if affordable
        """
        total_cost = self.get_cart_total(merchant_id)
        current_gold = self.game_state.character.get('gold', 0)
        return total_cost <= current_gold
    
    # ==========================================
    # MERCHANT SYSTEM INTEGRATION
    # ==========================================
    
    def get_merchant_inventory(self, merchant_id: str) -> Optional[Dict]:
        """
        Get complete merchant inventory for display
        
        Args:
            merchant_id: Merchant identifier
            
        Returns:
            Dict with merchant data or None if not found
        """
        if not self.item_manager:
            print("❌ No ItemManager available")
            return None
        
        return self.item_manager.get_merchant_inventory(merchant_id)
    
    def get_stock_status(self, item_name: str, merchant_id: str = 'garrick_barkeep') -> Dict:
        """
        Get stock information for an item
        
        Args:
            item_name: Item to check
            merchant_id: Merchant to check with
            
        Returns:
            Dict with stock info: {available: int, in_cart: int, remaining: int}
        """
        stock_limit = self._get_stock_limit(item_name, merchant_id)
        in_cart = self.game_state.shopping_cart.get(item_name, 0)
        
        return {
            'available': stock_limit,
            'in_cart': in_cart,
            'remaining': stock_limit - in_cart
        }
    
    # ==========================================
    # PRIVATE HELPER METHODS
    # ==========================================
    
    def _get_merchant_data(self, merchant_id: str) -> Optional[Dict]:
        """Get merchant data from ItemManager"""
        if self.item_manager:
            return self.item_manager.get_merchant_inventory(merchant_id)
        return None
    
    def _is_item_available(self, item_name: str, merchant_id: str) -> bool:
        """Check if item is available from merchant"""
        merchant_data = self._get_merchant_data(merchant_id)
        if not merchant_data:
            return False
        
        for item in merchant_data.get('items', []):
            if item['name'] == item_name:
                return True
        return False
    
    def _get_stock_limit(self, item_name: str, merchant_id: str) -> int:
        """Get stock limit for item (currently hardcoded to 5)"""
        # TODO: Move to merchant data files when implementing dynamic stock
        return 5
    
    def _get_item_cost(self, item_name: str, merchant_data: Dict) -> int:
        """Get cost of item from merchant data"""
        for item in merchant_data.get('items', []):
            if item['name'] == item_name:
                return item.get('cost', 0)
        return 0
    
    def _get_item_info(self, item_name: str) -> Optional[Dict]:
        """Get item information for cart summary"""
        if not self.item_manager:
            return None
        
        # Try to find in merchant items
        merchant_data = self._get_merchant_data('garrick_barkeep')  # Default merchant
        if merchant_data:
            return self._find_item_in_merchant_data(item_name, merchant_data)
        return None
    
    def _find_item_in_merchant_data(self, item_name: str, merchant_data: Dict) -> Optional[Dict]:
        """Find specific item in merchant data"""
        for item in merchant_data.get('items', []):
            if item['name'] == item_name:
                return item
        return None
    
    def _determine_inventory_category(self, item_type: str) -> str:
        """Determine which inventory category an item belongs in"""
        type_mapping = {
            'weapons': 'weapons',
            'armor': 'armor',
            'consumables': 'consumables',
            'items': 'items'
        }
        return type_mapping.get(item_type, 'items')


# ==========================================
# GLOBAL COMMERCE ENGINE MANAGEMENT
# ==========================================

# Global commerce engine instance (initialized by DataManager)
commerce_engine = None

def get_commerce_engine():
    """
    Get the global commerce engine instance
    Will be initialized by DataManager integration
    """
    return commerce_engine

def initialize_commerce_engine(game_state_ref, item_manager_ref):
    """
    Initialize the global commerce engine
    Called by DataManager during system initialization
    
    Args:
        game_state_ref: Reference to GameState (the data authority)
        item_manager_ref: Reference to ItemManager
    """
    global commerce_engine
    commerce_engine = CommerceEngine(game_state_ref, item_manager_ref)
    print("🔧 Initialized CommerceEngine with Single Data Authority pattern")
    return commerce_engine

def get_commerce_engine():
    """
    Get the global commerce engine instance
    Will be initialized by DataManager integration
    """
    return commerce_engine


# Development and testing utilities
if __name__ == "__main__":
    print("🧪 CommerceEngine Development Test")
    print("=" * 50)
    
    print("CommerceEngine follows Single Data Authority pattern:")
    print("- GameState = THE authoritative data source")
    print("- CommerceEngine = Pure business logic processor")
    print("- No data storage in engine itself")
    print("- All operations modify GameState directly")
    
    print("\n✅ CommerceEngine module loaded successfully!")