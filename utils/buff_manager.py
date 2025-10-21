# utils/buff_manager.py
"""
Buff Manager - Persistent stat modification system
Handles equipment bonuses, trinket effects, and special item bonuses

Phase 1: Equipment & Trinkets (CURRENT)
Phase 2: Temporary spell buffs (FUTURE - Shield, Bless, etc.)

Design Principles:
- Single source of truth for stat modifiers
- ONE trinket per character (stored in character['trinket'])
- Special items (Hendrik's Lantern) stack with trinket
- All inventory items checked (not just equipped)
"""

from typing import Tuple, List, Dict, Optional


class BuffManager:
    """
    Manages all persistent stat modifiers from equipment and items
    
    Responsibilities:
    - Calculate equipment bonuses (weapon/armor/shield)
    - Calculate active trinket bonuses (one per character)
    - Calculate special item bonuses (Hendrik's Lantern, etc.)
    - Provide clean API for other systems to query effective stats
    """
    
    def __init__(self, item_manager):
        """
        Initialize with ItemManager for item data lookups
        
        Args:
            item_manager: ItemManager instance for accessing item definitions
        """
        self.item_manager = item_manager
        
        # Stats we support in Phase 1
        self.supported_stats = {
            'armor_class',      # AC bonuses from trinkets/special items
            'initiative',       # Morale bonuses affecting initiative rolls
            'charisma',         # CHA bonuses from items
            'gambling_luck'     # Luck bonuses for dice games
        }
    
    # ==================== MAIN API ====================
    
    def get_effective_stat(self, stat_name: str, base_value: int, 
                          game_state) -> Tuple[int, List[str]]:
        """
        Calculate final stat value with ALL modifiers applied
        
        This is the main API method other systems should call.
        Combines equipment, trinket, and special item bonuses.
        
        Args:
            stat_name: What stat to calculate ('armor_class', 'initiative', etc.)
            base_value: Starting value before any modifiers
            game_state: Game state for inventory/equipment access
            
        Returns:
            (total_value, breakdown_list)
            
        Example:
            >>> buff_manager.get_effective_stat('armor_class', 15, game_state)
            (17, ['Base: 15', 'Jingly Pouch: +1', "Hendrik's Lantern: +1"])
        """
        if stat_name not in self.supported_stats:
            # Stat not supported yet, return base value
            return base_value, [f"Base: {base_value}"]
        
        total = base_value
        breakdown = [f"Base: {base_value}"]
        
        # Get equipment bonuses (weapon/armor/shield combat_stats)
        equip_bonus, equip_breakdown = self.get_equipment_bonuses(stat_name, game_state)
        if equip_bonus > 0:
            total += equip_bonus
            breakdown.extend(equip_breakdown)
        
        # Get trinket bonuses (ONE trinket only)
        trinket_bonus, trinket_breakdown = self.get_trinket_bonuses(stat_name, game_state)
        if trinket_bonus > 0:
            total += trinket_bonus
            breakdown.extend(trinket_breakdown)
        
        # Get special item bonuses (Hendrik's Lantern, etc.)
        special_bonus, special_breakdown = self.get_special_item_bonuses(stat_name, game_state)
        if special_bonus > 0:
            total += special_bonus
            breakdown.extend(special_breakdown)
        
        return total, breakdown
    
    # ==================== EQUIPMENT BONUSES ====================
    
    def get_equipment_bonuses(self, stat_name: str, game_state) -> Tuple[int, List[str]]:
        """
        Get bonuses from equipped weapon/armor/shield
        
        Only checks equipped items, not entire inventory.
        Reads combat_stats from item definitions.
        
        Args:
            stat_name: Stat to check for bonuses
            game_state: Game state for equipment data
            
        Returns:
            (bonus_value, breakdown_list)
        """
        bonus = 0
        breakdown = []
        
        # Equipment slots to check
        equipment_slots = {
            'equipped_weapon': game_state.character.get('equipped_weapon'),
            'equipped_armor': game_state.character.get('equipped_armor'),
            'equipped_shield': game_state.character.get('equipped_shield')
        }
        
        for slot_name, item_id in equipment_slots.items():
            if not item_id:
                continue
            
            # Look up item data
            item_data = self.item_manager.get_item_by_id(item_id)
            if not item_data or 'combat_stats' not in item_data:
                continue
            
            combat_stats = item_data['combat_stats']
            
            # Check for relevant stat bonuses
            if stat_name == 'armor_class':
                # Armor/shield AC is handled by stats_calculator
                # This is for BONUS AC (like magic items)
                # Currently no equipped items give bonus AC beyond base
                pass
            
            # Future: Add weapon/armor special bonuses here
            # (e.g., +1 Longsword, Ring of Protection, etc.)
        
        return bonus, breakdown
    
    # ==================== TRINKET BONUSES ====================
    
    def get_trinket_bonuses(self, stat_name: str, game_state) -> Tuple[int, List[str]]:
        """
        Get bonuses from active trinket (ONE per character)
        
        Trinkets are stored in game_state.character['trinket']
        Only ONE trinket can be active at a time (design rule)
        
        Args:
            stat_name: Stat to check for bonuses
            game_state: Game state for trinket data
            
        Returns:
            (bonus_value, breakdown_list)
        """
        bonus = 0
        breakdown = []
        
        # Get active trinket from character data
        active_trinket = game_state.character.get('trinket')
        
        if not active_trinket or active_trinket == 'None':
            return 0, []
        
        # Look up trinket data by ID
        trinket_data = self.item_manager.get_item_by_id(active_trinket)
        if not trinket_data:
            return 0, []
        
        trinket_name = trinket_data.get('name', active_trinket)
        
        # Check combat_stats first (like Jingly Pouch, Iron Ring)
        if 'combat_stats' in trinket_data:
            combat_stats = trinket_data['combat_stats']
            
            if stat_name == 'armor_class':
                ac_bonus = combat_stats.get('armor_class', 0)
                if ac_bonus > 0:
                    bonus += ac_bonus
                    breakdown.append(f"{trinket_name}: +{ac_bonus}")
        
        # Check special_effects (like Dream Catcher, Misty Vial)
        if 'special_effects' in trinket_data:
            effects = trinket_data['special_effects']
            
            if stat_name == 'armor_class':
                ac_bonus = effects.get('ac_bonus', 0)
                if ac_bonus > 0:
                    bonus += ac_bonus
                    breakdown.append(f"{trinket_name}: +{ac_bonus}")
            
            elif stat_name == 'initiative':
                # Morale bonus applies to initiative
                morale = effects.get('morale_bonus', 0)
                if morale > 0:
                    bonus += morale
                    breakdown.append(f"{trinket_name}: +{morale}")
            
            elif stat_name == 'charisma':
                cha_bonus = effects.get('charisma_bonus', 0)
                if cha_bonus > 0:
                    bonus += cha_bonus
                    breakdown.append(f"{trinket_name}: +{cha_bonus}")
            
            elif stat_name == 'gambling_luck':
                luck = effects.get('gambling_luck', 0)
                if luck > 0:
                    bonus += luck
                    breakdown.append(f"{trinket_name}: +{luck}")
        
        return bonus, breakdown
    
    # ==================== SPECIAL ITEM BONUSES ====================
    
    def get_special_item_bonuses(self, stat_name: str, game_state) -> Tuple[int, List[str]]:
        """
        Get bonuses from special items (Hendrik's Lantern, etc.)
        
        Special items can stack with trinkets (design rule)
        Checks entire inventory for items with special_effects
        Excludes trinkets (handled separately)
        
        Args:
            stat_name: Stat to check for bonuses
            game_state: Game state for inventory data
            
        Returns:
            (bonus_value, breakdown_list)
        """
        bonus = 0
        breakdown = []
        processed_items = set()  # Prevent duplicate processing
        
        # Active trinket (don't double-count)
        active_trinket = game_state.character.get('trinket')
        
        # Scan all inventory categories
        for category in ['items', 'consumables', 'weapons', 'armor']:
            for item_id in game_state.inventory.get(category, []):
                # Skip if already processed
                if item_id in processed_items:
                    continue
                processed_items.add(item_id)
                
                # Skip active trinket (already handled)
                if item_id == active_trinket:
                    continue
                
                # Look up item data
                item_data = self.item_manager.get_item_by_id(item_id)
                if not item_data:
                    continue
                
                # Skip items that are trinkets (only ONE trinket allowed)
                subcategory = item_data.get('subcategory', '')
                if subcategory == 'trinket':
                    continue
                
                # Check for special_effects
                if 'special_effects' not in item_data:
                    continue
                
                effects = item_data['special_effects']
                item_name = item_data.get('name', item_id)
                
                # Check for relevant stat bonuses
                if stat_name == 'armor_class':
                    ac_bonus = effects.get('ac_bonus', 0)
                    if ac_bonus > 0:
                        bonus += ac_bonus
                        breakdown.append(f"{item_name}: +{ac_bonus}")
                
                elif stat_name == 'initiative':
                    morale = effects.get('morale_bonus', 0)
                    if morale > 0:
                        bonus += morale
                        breakdown.append(f"{item_name}: +{morale}")
                
                elif stat_name == 'charisma':
                    cha_bonus = effects.get('charisma_bonus', 0)
                    if cha_bonus > 0:
                        bonus += cha_bonus
                        breakdown.append(f"{item_name}: +{cha_bonus}")
                
                elif stat_name == 'gambling_luck':
                    luck = effects.get('gambling_luck', 0)
                    if luck > 0:
                        bonus += luck
                        breakdown.append(f"{item_name}: +{luck}")
        
        return bonus, breakdown


# ==================== GLOBAL INSTANCE ====================

_buff_manager_instance = None

def get_buff_manager(item_manager=None):
    """
    Get or create global BuffManager instance
    
    Follows same pattern as get_stats_calculator() and get_effect_resolver()
    
    Args:
        item_manager: Required on first call to initialize
        
    Returns:
        BuffManager: Global instance
        
    Raises:
        ValueError: If item_manager not provided on first call
    """
    global _buff_manager_instance
    if _buff_manager_instance is None:
        if item_manager is None:
            raise ValueError("Must provide item_manager on first call to get_buff_manager()")
        _buff_manager_instance = BuffManager(item_manager)
    return _buff_manager_instance