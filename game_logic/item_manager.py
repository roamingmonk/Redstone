import json
import os
import pygame
from utils.constants import GRAY, WHITE

class ItemLoader:
    """Professional item management system for RPG games
    
    Handles loading item data from JSON files and managing item icons.
    Follows industry-standard separation of data and logic.
    """
    
    def __init__(self):
        print("DEBUG: ItemLoader initializing...")
        self.items_data = {}
        self.merchant_data = {}
        self.item_icons = {}
        self.load_items()
        self.load_merchant_data()
        self.load_item_icons()
        print("DEBUG: ItemLoader initialization complete")

        # Initialize NPC manager
        from game_logic.npc_manager import npc_manager
        print("DEBUG: NPC system initialized")


    def load_items(self):
        """Load all item definitions from JSON data file"""
        try:
            items_file = os.path.join('data', 'items.json')
            with open(items_file, 'r') as f:
                self.items_data = json.load(f)
            
            print(f"✅ Loaded items_data keys: {self.items_data.keys()}")  # DEBUG
            
            # Debug the merchant items specifically
            merchant_items = self.items_data.get('merchant_items', [])
            print(f"✅ Found {len(merchant_items)} merchant items")  # DEBUG
            
            for item in merchant_items:
                print(f"✅ Item loaded: id={item.get('id')}, name={item.get('name')}, base_cost={item.get('base_cost')}")  # DEBUG
                
        except FileNotFoundError:
            print("❌ Error: data/items.json not found!")
            self.items_data = {"merchant_items": [], "equipment_items": []}
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing items.json: {e}")
            self.items_data = {"merchant_items": [], "equipment_items": []}
    
    def load_item_icons(self):
        """Load all item icons with fallback to placeholder"""
        items_dir = os.path.join('assets', 'images', 'items')
        
        for item in self.get_all_items():
            icon_name = item.get('icon_file', f"{item['id']}.png")
            icon_path = os.path.join(items_dir, icon_name)

            # Try to load the actual icon
            if os.path.exists(icon_path):
                try:
                    icon = pygame.image.load(icon_path)
                    self.item_icons[item['id']] = pygame.transform.scale(icon, (32, 32))
                except pygame.error:
                    self.item_icons[item['id']] = self.create_placeholder_icon()
            else:
                self.item_icons[item['id']] = self.create_placeholder_icon()
    
    def create_placeholder_icon(self):
        """Create a placeholder icon for missing item images"""
        icon = pygame.Surface((32, 32))
        icon.fill(GRAY)
        pygame.draw.rect(icon, WHITE, (0, 0, 32, 32), 2)
        
        # Draw an "X" in the center
        pygame.draw.line(icon, WHITE, (8, 8), (24, 24), 2)
        pygame.draw.line(icon, WHITE, (24, 8), (8, 24), 2)
        
        return icon
    
    def get_merchant_items(self):
        """Get all items available for purchase from merchants"""
        return self.items_data.get('merchant_items', [])
    
    def get_equipment_items(self):
        """Get all equipment items (weapons, armor, etc.)"""
        return self.items_data.get('equipment_items', [])
    
    def get_all_items(self):
        """Get all items from all categories"""
        all_items = []
        all_items.extend(self.get_merchant_items())
        all_items.extend(self.get_equipment_items())
        return all_items
    
    def get_item_by_id(self, item_id):
        """Get a specific item by its ID"""
        #print(f"DEBUG: Looking for item_id '{item_id}'")  # DEBUG
        for item in self.get_all_items():
         #   print(f"DEBUG: Checking item with id '{item.get('id', 'NO_ID')}', base_cost: {item.get('base_cost', 'MISSING')}")  # DEBUG
            if item['id'] == item_id:
                #print(f"DEBUG: FOUND MATCH! Returning item: {item}")  # DEBUG
                return item
        #print(f"DEBUG: NO MATCH FOUND for '{item_id}'")  # DEBUG
        return None
        
    def get_item_by_name(self, item_name):
        """Get a specific item by its display name"""
        for item in self.get_all_items():
            if item['name'] == item_name:
                return item
        return None
    
    def get_item_icon(self, item_id):
        """Get the icon surface for a specific item"""
        return self.item_icons.get(item_id, self.create_placeholder_icon())

    def get_item_price(self, item_id, merchant_modifier=1.0):
        """Calculate final price with merchant modifier"""
        #print(f"DEBUG: get_item_price called with item_id='{item_id}', modifier={merchant_modifier}")
        item = self.get_item_by_id(item_id)
        #print(f"DEBUG: get_item_by_id returned: {item}")
        if item:
            # Handle both 'base_cost' and 'cost' field names
            base_price = item.get('base_cost') or item.get('cost') or 0
        #    print(f"DEBUG: base_price extracted: {base_price} (type: {type(base_price)})")
            final_price = int(base_price * merchant_modifier)
        #    print(f"DEBUG: final calculated price: {final_price}")
            return final_price
        #print("DEBUG: item was None, returning 0")
        return 0

    def get_merchant_pricing(self, merchant_type="standard"):
        """Get pricing modifier for different merchant types"""
        modifiers = {
            "standard": 1.0,      # Tavern, city merchants
            "remote": 1.3,        # Remote village traders  
            "specialty": 1.2,     # Weapon/armor specialists
            "black_market": 0.8,  # Shady dealers (cheaper but risky)
            "emergency": 2.0      # Disaster/siege pricing
        }
        return modifiers.get(merchant_type, 1.0)
    def load_merchant_data(self):
        """Load merchant configurations from JSON"""
        try:
            merchant_file = os.path.join('data', 'merchants.json')
            with open(merchant_file, 'r') as f:
                self.merchant_data = json.load(f)
            merchants = self.merchant_data.get('merchants', {})
            print(f"DEBUG: Found merchants: {list(merchants.keys())}")
            print(f"✅ Loaded {len(merchants)} merchant configurations")
        except FileNotFoundError:
            print("❌ Error: data/merchants.json not found!")
            self.merchant_data = {"merchants": {}}
        except json.JSONDecodeError as e:
            self.merchant_data = {"merchants": {}}

    def get_merchant_inventory(self, merchant_id):
        """Get inventory for a specific merchant"""
        #print(f"DEBUG: Looking for merchant_id: '{merchant_id}'")
        #print(f"DEBUG: Available merchants: {list(self.merchant_data.get('merchants', {}).keys())}")
        
        merchant = self.merchant_data.get('merchants', {}).get(merchant_id)
        #print(f"DEBUG: Found merchant data: {merchant}")
        
        if not merchant:
            #print(f"DEBUG: Merchant '{merchant_id}' not found!")
            return None
        
        formatted_items = []
        for item_id in merchant['stock_items']:
            item = self.get_item_by_id(item_id)
            if item:
                final_cost = self.get_item_price(item_id, merchant['price_modifier'])
                formatted_items.append({
                    'name': item['name'],
                    'cost': final_cost,
                    'type': item['category'],
                    'description': item['description'],
                    'item_id': item['id']
                })
        
        return {
            'merchant_name': merchant['name'],
            'greeting': merchant['greeting'],
            'items': formatted_items
        }
    

# Global item manager instance
item_manager = ItemLoader()