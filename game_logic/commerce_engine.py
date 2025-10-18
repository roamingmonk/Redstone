# game_logic/commerce_engine.py

from typing import Dict, List, Tuple, Optional

class CommerceEngine:
    """
    Professional commerce management system for Terror in Redstone
    - GameState = single source of truth
    - ItemManager supplies catalog/merchant views
    - Engine is pure business logic (no internal state)
    """

    def __init__(self, game_state_ref, item_manager_ref):
        self.game_state = game_state_ref
        self.item_manager = item_manager_ref

        # Initialize merchant stocks if needed
        if not hasattr(self.game_state, 'merchant_stocks'):
            self.game_state.merchant_stocks = {}

        print("🛒 CommerceEngine ready (ID-based, stock-aware)")

    # =========================
    # CART OPERATIONS (item_id)
    # =========================
    def add_to_cart(self, item_id: str, merchant_id: str) -> bool:
        try:
            if not self._is_item_available(item_id, merchant_id):
                print(f"❌ Item '{item_id}' not sold by {merchant_id}")
                return False

            current_in_cart = self.game_state.shopping_cart.get(item_id, 0)
            stock_limit = self._get_stock_limit(item_id, merchant_id)

            if current_in_cart >= stock_limit:
                print(f"❌ Stock limit reached for {item_id} ({current_in_cart}/{stock_limit})")
                return False

            self.game_state.shopping_cart[item_id] = current_in_cart + 1
            print(f"✅ Added {item_id} to cart ({current_in_cart + 1}/{stock_limit})")
            return True
        except Exception as e:
            print(f"❌ add_to_cart error: {e}")
            return False

    def remove_from_cart(self, item_id: str) -> bool:
        try:
            qty = self.game_state.shopping_cart.get(item_id, 0)
            if qty > 0:
                if qty == 1:
                    del self.game_state.shopping_cart[item_id]
                else:
                    self.game_state.shopping_cart[item_id] = qty - 1
                print(f"✅ Removed one {item_id} from cart")
                return True
            print(f"❌ {item_id} not in cart or already zero")
            return False
        except Exception as e:
            print(f"❌ remove_from_cart error: {e}")
            return False

    def clear_cart(self) -> None:
        self.game_state.shopping_cart = {}
        print("🛒 Cart cleared")

    def get_cart_total(self, merchant_id: str) -> int:
        total = 0
        merchant_data = self._get_merchant_data(merchant_id)
        if not merchant_data:
            return 0
        for item_id, qty in self.game_state.shopping_cart.items():
            unit = self._get_item_cost(item_id, merchant_data)
            total += unit * qty
        return total

    def get_cart_summary(self, merchant_id: str) -> List[Dict]:
        summary = []
        merchant_data = self._get_merchant_data(merchant_id)
        for item_id, qty in self.game_state.shopping_cart.items():
            unit = self._get_item_cost(item_id, merchant_data) if merchant_data else 0
            item_def = self.item_manager.get_item_by_id(item_id) if self.item_manager else None
            summary.append({
                "item_id": item_id,
                "name": (item_def or {}).get("name", item_id),
                "quantity": qty,
                "unit_cost": unit,
                "total_cost": unit * qty,
                "description": (item_def or {}).get("description", "")
            })
        return summary

    # =====================
    # TRANSACTION PROCESSOR
    # =====================
    def process_purchase(self, merchant_id: str) -> Tuple[bool, str]:
        try:
            if not self.game_state.shopping_cart:
                return False, "Shopping cart is empty."

            merchant_data = self._get_merchant_data(merchant_id)
            if not merchant_data:
                return False, "Merchant not found."

            total_cost = self.get_cart_total(merchant_id)
            current_gold = self.game_state.character.get("gold", 0)
            if total_cost > current_gold:
                return False, f"Not enough gold. Need {total_cost}, have {current_gold}."

            # Validate stock one more time
            for item_id, qty in self.game_state.shopping_cart.items():
                if qty > self._get_stock_limit(item_id, merchant_id):
                    return False, f"{item_id} exceeds available stock."

            # Commit: add items to inventory
            purchased = 0
            for item_id, qty in self.game_state.shopping_cart.items():
                inv_row = self._find_in_merchant_by_id(item_id, merchant_data)
                if not inv_row:
                    continue
                
                item_def = self.item_manager.get_item_by_id(item_id) if self.item_manager else None
                category = self._determine_inventory_category(item_def.get("category", "items") if item_def else "items")
                
                for _ in range(qty):
                    self.game_state.inventory[category].append(item_id)
                purchased += qty

            # Reduce merchant stock PERMANENTLY in game_state
            if merchant_id not in self.game_state.merchant_stocks:
                self._initialize_merchant_stock(merchant_id)

            for item_id, qty in self.game_state.shopping_cart.items():
                current_stock = self.game_state.merchant_stocks[merchant_id].get(item_id, 0)
                self.game_state.merchant_stocks[merchant_id][item_id] = max(0, current_stock - qty)
                print(f"🛒 Reduced {item_id} stock from {current_stock} to {self.game_state.merchant_stocks[merchant_id][item_id]}")

            # Deduct gold, clear cart
            self.game_state.character["gold"] = current_gold - total_cost
            self.clear_cart()
            return True, f"Purchase complete! Bought {purchased} items for {total_cost} gold."
        except Exception as e:
            print(f"❌ process_purchase error: {e}")
            return False, f"Transaction failed: {e}"

    def can_afford_cart(self, merchant_id: str) -> bool:
        return self.get_cart_total(merchant_id) <= self.game_state.character.get("gold", 0)

    # TODO CALL THIS METHOD TO RESET STOCK FOR MERCHANTS, maybe after a 'rest'
    def restock_merchant(self, merchant_id: str):
        """Reset merchant to full stock (call on rest/new day)"""
        self._initialize_merchant_stock(merchant_id)  # Resets to full
        print(f"🔄 {merchant_id} restocked")

    def register_event_handlers(self, event_manager):
        """Register commerce event handlers"""
        event_manager.register("COMMERCE_PURCHASE", self._handle_purchase)
        event_manager.register("COMMERCE_RESET_CART", self._handle_reset_cart)
        event_manager.register("COMMERCE_ADD_TO_CART", self._handle_add_to_cart)
        print("🛒 CommerceEngine event handlers registered")

    def _handle_purchase(self, event_data):
        """Handle purchase requests"""
        merchant_id = getattr(self.game_state, 'current_merchant_id', 'garrick')
        success, message = self.process_purchase(merchant_id)
        print(f"🛒 Purchase result: {message}")

    def _handle_reset_cart(self, event_data):
        """Handle cart reset requests"""
        self.clear_cart()
        print("🛒 Shopping cart cleared")

    def _handle_add_to_cart(self, event_data):
        """Handle add to cart requests"""
        item_id = event_data.get('item_id')
        merchant_id = event_data.get('merchant_id')
        
        print(f"🛒 Adding {item_id} to cart for merchant {merchant_id}")
        
        if item_id and merchant_id:
            success = self.add_to_cart(item_id, merchant_id)
            print(f"🛒 Add to cart result: {success}")
            
            # Trigger screen refresh so Purchase column updates
            if success and hasattr(self, 'event_manager'):
                self.event_manager.emit("SCREEN_REDRAW", {"screen": "merchant_shop"})
        else:
            print("🛒 Missing item_id or merchant_id in add to cart request")


    # =====================
    # MERCHANT INTEGRATION
    # =====================
    def get_merchant_inventory(self, merchant_id: str) -> Optional[Dict]:
        if not self.item_manager:
            print("❌ No ItemManager available")
            return None
        return self.item_manager.get_merchant_inventory(merchant_id)

    def get_stock_status(self, item_id: str, merchant_id: str) -> Dict:
        available = self._get_stock_limit(item_id, merchant_id)
        in_cart = self.game_state.shopping_cart.get(item_id, 0)
        return {"available": available, "in_cart": in_cart, "remaining": max(0, available - in_cart)}

    # ===============
    # PRIVATE HELPERS
    # ===============
    def _get_merchant_data(self, merchant_id: str) -> Optional[Dict]:
        # Get the merchant data that ScreenManager already prepared
        merchant_data = getattr(self.game_state, 'current_merchant_data', None)
        if merchant_data and merchant_data.get('merchant_id') == merchant_id:
            return merchant_data
        return None

    def _is_item_available(self, item_id: str, merchant_id: str) -> bool:
        m = self._get_merchant_data(merchant_id)
        if not m:
            return False
        return any(row.get("item_id") == item_id for row in m.get("items", []))

    def _get_stock_limit(self, item_id: str, merchant_id: str) -> int:
        """Get CURRENT stock from game_state, initialize if needed"""
        # Initialize merchant stock on first access
        if merchant_id not in self.game_state.merchant_stocks:
            self._initialize_merchant_stock(merchant_id)
        
        # Return current stock from game state
        return self.game_state.merchant_stocks[merchant_id].get(item_id, 0)

    def _initialize_merchant_stock(self, merchant_id: str):
        """Set up initial stock levels from merchant data"""
        merchant_data = self._get_merchant_data(merchant_id)
        if not merchant_data:
            return
        
        self.game_state.merchant_stocks[merchant_id] = {}
        for item in merchant_data.get('items', []):
            item_id = item.get('item_id')
            stock = item.get('stock', 5)  # Get from merchant data
            self.game_state.merchant_stocks[merchant_id][item_id] = stock
        
        print(f"🛒 Initialized stock for {merchant_id}: {self.game_state.merchant_stocks[merchant_id]}")

    def _get_item_cost(self, item_id: str, merchant_data: Dict) -> int:
        row = self._find_in_merchant_by_id(item_id, merchant_data)
        return int(row.get("cost", 0)) if row else 0

    def _find_in_merchant_by_id(self, item_id: str, merchant_data: Dict) -> Optional[Dict]:
        for row in merchant_data.get("items", []):
            if row.get("item_id") == item_id:
                return row
        return None

    def _determine_inventory_category(self, item_type: str) -> str:
        # Keep in sync with ItemLoader’s normalization (e.g., "potion" → "consumables")
        print(f"🛒 DEBUG: _determine_inventory_category called with: '{item_type}'") 
        mapping = {
            "weapons": "weapons",
            "armor": "armor",
            "consumables": "consumables",
            "items": "items"
        }

        result = mapping.get(item_type, "items")    
        print(f"🛒 DEBUG: Mapped '{item_type}' to '{result}'")
        return result
            

# ==========================================
# GLOBAL COMMERCE ENGINE MANAGEMENT (unchanged)
# ==========================================
commerce_engine = None

def initialize_commerce_engine(game_state_ref, item_manager_ref):
    global commerce_engine
    commerce_engine = CommerceEngine(game_state_ref, item_manager_ref)
    print("🔧 Initialized CommerceEngine (ID-based, stock-aware)")
    return commerce_engine

def get_commerce_engine():
    return commerce_engine
