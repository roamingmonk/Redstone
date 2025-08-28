# game_logic/data_manager.py
"""
Professional Data Manager 
Master coordinator for all game data loading systems

This follows the "Initialize Once, Use Everywhere" pattern used in AAA games.
All data loading is centralized, coordinated, and error-handled here.
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

class DataManager:
    """
    Master data loading coordinator for Terror in Redstone
    
    Handles initialization and coordination of all data loading systems.
    Provides centralized error handling, data validation, and performance monitoring.
    """
    
    def __init__(self):
        # System state tracking
        self.initialized = False
        self.load_start_time = None
        self.load_errors = []
        self.system_health = {
            'items': False,
            'npcs': False, 
            'locations': False,
            'player_manager': False,
            'inventory_engine': False
        }
        
        # Data manager instances
        self.item_manager = None
        self.npc_manager = None
        self.location_manager = None
        self.player_manager = None

        # Game engine instances (Session 5+)
        self.inventory_engine = None
        
        print("🏗️ DataManager initialized - Ready to coordinate all data loading")
    
    def initialize_all_systems(self) -> bool:
        """
        Initialize all data loading systems with comprehensive error handling
        Returns True if initialization successful, False if critical errors occurred
        """
        self.load_start_time = datetime.now()
        print("🚀 DataManager: Beginning system initialization...")
        
        success_count = 0
        total_systems = 5
        
        # 1. Initialize Item Management System
        success_count += self._initialize_item_system()
        
        # 2. Initialize NPC Management System  
        success_count += self._initialize_npc_system()
        
        # 3. Initialize Location Management System
        success_count += self._initialize_location_system()
        
        # 4. Initialize Player Management System (your custom addition)
        success_count += self._initialize_player_system()

        # 5. Initialize Inventory Engine (Session 5 addition)
        success_count += self._initialize_inventory_engine()
        
        # Calculate initialization results
        load_time = datetime.now() - self.load_start_time
        success_rate = (success_count / total_systems) * 100
        
        print(f"⚡ DataManager initialization complete:")
        print(f"   ✅ Systems loaded: {success_count}/{total_systems} ({success_rate:.1f}%)")
        print(f"   ⏱️ Load time: {load_time.total_seconds():.3f} seconds")
        
        if self.load_errors:
            print(f"   ⚠️ Errors encountered: {len(self.load_errors)}")
            for error in self.load_errors:
                print(f"      - {error}")
        
        # Determine if initialization was successful
        # Require at least 75% of systems to load for success
        self.initialized = success_rate >= 75.0
        
        if self.initialized:
            print("✅ DataManager: All critical systems operational!")
        else:
            print("❌ DataManager: Critical system failures - check data files!")
            
        return self.initialized

    def _initialize_item_system(self) -> int:
        """Initialize item management system. Returns 1 if successful, 0 if failed."""
        try:
            from game_logic.item_manager import ItemLoader
            self.item_manager = ItemLoader()
            self.system_health['items'] = True
            print("   ✅ Item system loaded")
            return 1
        except Exception as e:
            error_msg = f"Item system failed: {e}"
            self.load_errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return 0
    
    def _initialize_npc_system(self) -> int:
        """Initialize NPC management system. Returns 1 if successful, 0 if failed."""
        try:
            from game_logic.npc_manager import NPCManager
            self.npc_manager = NPCManager()
            self.system_health['npcs'] = True
            print("   ✅ NPC system loaded")
            return 1
        except Exception as e:
            error_msg = f"NPC system failed: {e}"
            self.load_errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return 0
    
    def _initialize_location_system(self) -> int:
        """Initialize location management system. Returns 1 if successful, 0 if failed.""" 
        try:
            from game_logic.location_manager import LocationManager
            self.location_manager = LocationManager()
            self.system_health['locations'] = True
            print("   ✅ Location system loaded")
            return 1
        except Exception as e:
            error_msg = f"Location system failed: {e}"
            self.load_errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return 0
    
    def _initialize_player_system(self) -> int:
        """Initialize player management system (your custom addition). Returns 1 if successful, 0 if failed."""
        try:
            from game_logic.player_manager import PlayerManager
            self.player_manager = PlayerManager()
            self.system_health['player_manager'] = True
            print("   ✅ Player management system loaded")
            return 1
        except Exception as e:
            error_msg = f"Player management system failed: {e}"
            self.load_errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return 0

    def _initialize_inventory_engine(self) -> int:
        """Initialize inventory engine system. Returns 1 if successful, 0 if failed."""
        try:
            # Import here to avoid circular import
            from game_logic.inventory_engine import initialize_inventory_engine
            
            # Inventory engine needs both data_manager and player_manager
            if not self.player_manager:
                raise Exception("Player manager required for inventory engine")
            
            self.inventory_engine = initialize_inventory_engine(self, self.player_manager)
            self.system_health['inventory_engine'] = True
            print("   ✅ Inventory engine loaded")
            return 1
        except Exception as e:
            error_msg = f"Inventory engine failed: {e}"
            self.load_errors.append(error_msg)
            print(f"   ❌ {error_msg}")
            return 0

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status report
        Useful for debugging and system monitoring
        """
        return {
            'initialized': self.initialized,
            'load_time': (datetime.now() - self.load_start_time).total_seconds() if self.load_start_time else None,
            'systems_healthy': sum(self.system_health.values()),
            'total_systems': len(self.system_health),
            'health_details': self.system_health.copy(),
            'error_count': len(self.load_errors),
            'errors': self.load_errors.copy()
        }
    
    def validate_data_integrity(self) -> bool:
        """
        Perform data integrity checks across all loaded systems
        Returns True if all critical data is valid
        """
        if not self.initialized:
            print("❌ Cannot validate - DataManager not initialized")
            return False
        
        validation_passed = True
        
        # Validate item system
        if self.item_manager and self.system_health['items']:
            try:
                # Check if merchant items exist
                merchant_items = getattr(self.item_manager, 'items_data', {}).get('merchant_items', [])
                if len(merchant_items) == 0:
                    print("⚠️ Warning: No merchant items loaded")
                    validation_passed = False
                else:
                    print(f"✅ Item validation: {len(merchant_items)} merchant items verified")
            except Exception as e:
                print(f"❌ Item validation failed: {e}")
                validation_passed = False
        
        # Validate NPC system  
        if self.npc_manager and self.system_health['npcs']:
            try:
                npc_count = len(getattr(self.npc_manager, 'npcs_data', {}))
                if npc_count == 0:
                    print("⚠️ Warning: No NPCs loaded")
                    validation_passed = False
                else:
                    print(f"✅ NPC validation: {npc_count} NPCs verified")
            except Exception as e:
                print(f"❌ NPC validation failed: {e}")
                validation_passed = False
        
        # Validate player manager
        if self.player_manager and self.system_health['player_manager']:
            try:
                # Check if player manager can access current_character.json (in data/player/ folder)
                player_file_path = os.path.join('data', 'player', 'current_character.json')
                player_data_exists = os.path.exists(player_file_path)
                print(f"✅ Player manager validation: current_character.json exists = {player_data_exists}")
            except Exception as e:
                print(f"❌ Player manager validation failed: {e}")
                validation_passed = False
        
        return validation_passed
    
    def reload_all_systems(self) -> bool:
        """
        Reload all data systems (useful for development/debugging)
        """
        print("🔄 DataManager: Reloading all systems...")
        
        # Reset state
        self.initialized = False
        self.load_errors.clear()
        for system in self.system_health:
            self.system_health[system] = False
        
        # Reinitialize
        return self.initialize_all_systems()
    
    def get_manager(self, manager_type: str):
        """
        Get specific manager instance by type
        Safe accessor with proper error handling
        """
        manager_map = {
            'items': self.item_manager,
            'npcs': self.npc_manager, 
            'locations': self.location_manager,
            'player': self.player_manager,
            'inventory': self.inventory_engine 
        }
        
        if manager_type not in manager_map:
            print(f"❌ Unknown manager type: {manager_type}")
            return None
        
        manager = manager_map[manager_type]
        if manager is None:
            print(f"❌ Manager '{manager_type}' not initialized")
            return None
        
        return manager
    
    def emergency_fallback(self) -> Dict[str, Any]:
        """
        Provide emergency fallback data if critical systems fail
        Ensures game can still run with minimal functionality
        """
        fallback_data = {
            'items': {
                'merchant_items': [
                    {
                        'id': 'strong_ale',
                        'name': 'Strong Ale',
                        'base_cost': 3,
                        'type': 'consumable',
                        'description': 'Restores health and spirits'
                    },
                    {
                        'id': 'trail_rations', 
                        'name': 'Trail Rations',
                        'base_cost': 5,
                        'type': 'consumable',
                        'description': 'Basic sustenance for travelers'
                    }
                ]
            },
            'npcs': {
                'gareth': {
                    'name': 'Gareth the Warrior',
                    'class': 'Fighter',
                    'level': 3,
                    'description': 'A stalwart warrior seeking adventure'
                }
            }
        }
        
        print("⚠️ DataManager: Using emergency fallback data")
        return fallback_data


# Global data manager instance (Singleton pattern)
# This provides easy access throughout the game
data_manager = None

def get_data_manager() -> DataManager:
    """
    Get the global data manager instance
    Creates one if it doesn't exist (Singleton pattern)
    """
    global data_manager
    if data_manager is None:
        data_manager = DataManager()
    return data_manager

def initialize_game_data() -> bool:
    """
    Convenience function to initialize all game data systems
    Returns True if successful
    """
    dm = get_data_manager()
    return dm.initialize_all_systems()


# Development and testing utilities
if __name__ == "__main__":
    print("🧪 DataManager Development Test")
    print("=" * 50)
    
    # Test initialization
    success = initialize_game_data()
    
    # Print system status
    dm = get_data_manager()
    status = dm.get_system_status()
    
    print(f"\nSystem Status:")
    print(f"Initialized: {status['initialized']}")
    print(f"Systems Healthy: {status['systems_healthy']}/{status['total_systems']}")
    
    if status['errors']:
        print(f"Errors: {status['error_count']}")
        for error in status['errors']:
            print(f"  - {error}")
    
    # Test data validation
    print(f"\nData Validation: {dm.validate_data_integrity()}")
    
    print("\n✅ DataManager test complete!")