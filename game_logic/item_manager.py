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
        #self.load_items()
        #self.load_merchant_data()
        #self.load_item_icons()
        print("DEBUG: ItemLoader initialization complete (Constructor)")

    def load_data(self):
       #NEW  
        """
        Explicitly loads all data into the ItemLoader
        This method is called by the DataManager
        """
        print("DEBUG: ItemLoader loading data...")
        print("🔄 ItemManager: Loading item data... (CALLED FROM DATA MANAGER)")
        self.load_items()
        print(f"✅ ItemManager: Loaded {len(getattr(self, 'items_data', {}).get('merchant_items', []))} items")
        self.load_merchant_data()
        self.load_item_icons()
        print("DEBUG: ItemLoader initialization complete (load_data)")  

    def _normalize_category(self, raw: str) -> str:
        mapping = {
            'potion': 'consumables',
            'consumables': 'consumables',
            'weapons': 'weapons',
            'armor': 'armor',
            'items': 'items'
        }
        return mapping.get(raw, 'items')

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
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        items_dir = os.path.join('assets', 'images', 'icons','items')
        
        print(f"DEBUG: Looking for icons in: {os.path.abspath(items_dir)}")
        print(f"DEBUG: Directory exists? {os.path.exists(items_dir)}")

        for item in self.get_all_items():
            icon_name = item.get('icon_file', f"{item['id']}.png")
            icon_path = os.path.join(items_dir, icon_name)

            print(f"DEBUG: Trying to load icon for {item['id']}: {icon_path}")
            print(f"DEBUG: File exists? {os.path.exists(icon_path)}")

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
        print(f"DEBUG: Looking for item_id '{item_id}'")  # DEBUG
        for item in self.get_all_items():
            print(f"DEBUG: Checking item with id '{item.get('id', 'NO_ID')}', base_cost: {item.get('base_cost', 'MISSING')}")  # DEBUG
            if item['id'] == item_id:
                print(f"DEBUG: FOUND MATCH! Returning item: {item}")  # DEBUG
                return item
        print(f"DEBUG: NO MATCH FOUND for '{item_id}'")  # DEBUG
        return None
        
    # def get_item_by_name(self, item_name):
    #     """Get a specific item by its display name"""
    #     print(f"DEBUG: IM: get_item_by_name searching for '{item_name}'")
        
    #     for item in self.get_all_items():
    #         item_display_name = item.get('name', '')
    #         print(f"DEBUG: IM: Comparing '{item_name}' vs '{item_display_name}'")
    #         if item['name'] == item_name:
    #             print(f"DEBUG: IM: MATCH FOUND for '{item_name}' -> {item['id']}")
    #             return item
        
    #     print(f"DEBUG: IM: NO MATCH for '{item_name}'")
    #     return None
    
    def get_item_icon(self, item_id):
        """Get the icon surface for a specific item"""
        return self.item_icons.get(item_id, self.create_placeholder_icon())

    # def get_item_icon_by_name(self, item_name):
    #     """Get icon by item name (converts name to ID first)"""
    #     print(f"DEBUG: IM:: get_item_icon_by_name called for '{item_name}', have {len(self.item_icons)} icons loaded")
    #     item = self.get_item_by_name(item_name)
    #     if item:
    #         return self.get_item_icon(item['id'])
    #     return self.create_placeholder_icon()

    def get_display_name(self, item_id):
        """Convert item ID to proper display name"""
        item = self.get_item_by_id(item_id)
        return item['name'] if item else item_id.replace('_', ' ').title()

    def get_item_description(self, item_id):
        """Get item description by ID"""
        item = self.get_item_by_id(item_id)
        return item.get('description', '') if item else ''


    def get_item_price(self, item_id, merchant=None, merchant_modifier: float = 1.0) -> int:
        """
        Calculate final price with optional merchant context.
        Honors per-item price_overrides if present on the merchant.
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return 0

        base = item.get('base_cost') or item.get('cost') or 0

        # Merchant-aware path
        if merchant:
            # Optional: explicit override for a specific item
            overrides = merchant.get('price_overrides', {})
            if item_id in overrides:
                return int(overrides[item_id])

            # Otherwise apply the merchant's modifier (or provided fallback)
            mod = float(merchant.get('price_modifier', merchant_modifier))
            return int(round(base * mod))

        # Fallback: no merchant provided, just apply given modifier
        return int(round(base * merchant_modifier))


    def get_merchant_pricing(self, merchant_type="standard"):
        """Get pricing modifier for different merchant types"""
        modifiers = {
            "standard": 1.0,
            "tavern_keeper": 1.0,   # Garrick’s type
            "remote": 1.3,
            "specialty": 1.2,
            "black_market": 0.8,
            "emergency": 2.0
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
    """
    Materialize a merchant's inventory from declarative config
    """
    merchant = self.merchant_data.get('merchants', {}).get(merchant_id)
    if not merchant:
        print(f"❌ No merchant found for ID: {merchant_id}")
        return None

    # Build candidate item ids from filters
    include_ids = set(merchant.get('stock_filter', {}).get('include_ids', []))
    print(f"🔧 Merchant {merchant_id} include_ids: {include_ids}")
    allowed_cats = set(merchant.get('stock_categories', []))
    max_rarity = merchant.get('stock_filter', {}).get('max_rarity')

    # Collect items - prioritize include_ids over categories
    candidates = []
    seen = set()
    
    for item in self.get_all_items():
        if item['id'] in seen:
            continue
            
        # If include_ids is specified, ONLY use those items
        if include_ids:
            if item['id'] in include_ids:
                candidates.append(item)
                seen.add(item['id'])
                print(f"✅ Included specific item: {item['id']}")
        # Otherwise fall back to category filtering
        elif allowed_cats and item.get('category') in allowed_cats:
            candidates.append(item)
            seen.add(item['id'])
            print(f"✅ Included category item: {item['id']}")

    print(f"🔧 Final filtered items: {[item['id'] for item in candidates]}")

    # Rest of the method for pricing and formatting...
    mtype = merchant.get('merchant_type', 'standard')
    fallback_modifier = self.get_merchant_pricing(mtype)
    default_stock = int(merchant.get('default_stock_quantity', 5))
    stock_over = merchant.get('stock_overrides', {})

    formatted_items = []
    for item in candidates:
        item_id = item['id']
        cat = self._normalize_category(item.get('category', 'items'))
        price = self.get_item_price(item_id, merchant=merchant, merchant_modifier=fallback_modifier)
        formatted_items.append({
            'item_id': item_id,
            'name': item['name'],
            'type': cat,
            'description': item.get('description', ''),
            'cost': price,
            'stock': int(stock_over.get(item_id, default_stock)),
        })

    return {
        'merchant_id': merchant_id,
        'merchant_name': merchant.get('name', merchant_id),
        'greeting': merchant.get('greeting', ''),
        'price_modifier': float(merchant.get('price_modifier', fallback_modifier)),
        'default_stock_quantity': default_stock,
        'items': formatted_items
    }
   

# Global item manager instance
item_manager = ItemLoader()