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

# Import core data managers that do not depend on the game engines
from game_logic.item_manager import ItemLoader
from game_logic.npc_manager import NPCManager
from game_logic.location_manager import LocationManager
from game_logic.character_engine import initialize_character_engine
from game_logic.inventory_engine import initialize_inventory_engine
from game_logic.commerce_engine import initialize_commerce_engine
from game_logic.dialogue_engine import initialize_dialogue_engine


# Global data manager instance (Singleton pattern)
data_manager = None


class DataManager:
    """
    Master data loading coordinator for Terror in Redstone
    """
    
    def __init__(self):
        self.initialized = False
        self.load_start_time = None
        self.load_errors = []
        self.system_health = {
            'items': False,
            'npcs': False,
            'inventory_engine': False,
            'commerce_engine': False,
            'character_engine': False
        }
        
        # Data manager instances
        self.item_manager = ItemLoader()
        self.npc_manager = NPCManager()
        self.location_manager = LocationManager()

        # Game engine instances (Session 5+)
        self.inventory_engine = None
        self.commerce_engine = None
        self.character_engine = None
        
        print("🏗️ DataManager initialized - Ready to coordinate all data loading")
    
    def load_all_data(self):
        """
        The NEW single point of truth for all data loading.
        This method orchestrates all data loading and initialization.
        """
        self.load_start_time = datetime.now()  
        print("🔄 DataManager: Starting data loading...")

    # Load Item and NPC data first
    # Check if data is already loaded to avoid duplication
        if hasattr(self.item_manager, 'items_data') and self.item_manager.items_data:
            print("ℹ️  Items already loaded, skipping reload...")
        else:
           self.item_manager.load_data()
        if hasattr(self.npc_manager, 'npcs_data') and self.npc_manager.npcs_data:
            print("ℹ️  NPCs already loaded, skipping reload...")
        else:
            self.npc_manager.load_data()

        self.system_health['items'] = True
        self.system_health['npcs'] = True
        print("✅ Basic systems initialized successfully!")

    def initialize_all_engines(self, game_state_ref):
            """
            Initializes and links all game engines after data is loaded.
            """
            
            print("🔧 DataManager: Initializing game engines with GameState reference...")
            
            try: 
                # Centralized initialization for ALL engines
                self.character_engine = initialize_character_engine(game_state_ref)
                self.inventory_engine = initialize_inventory_engine(
                    game_state_ref, self.item_manager
                )
                self.commerce_engine = initialize_commerce_engine(
                    game_state_ref, self.item_manager
                )
                self.dialogue_engine = initialize_dialogue_engine(game_state_ref)
                self.system_health['character_engine'] = True
                self.system_health['inventory_engine'] = True
                self.system_health['commerce_engine'] = True
                self.system_health['dialogue_engine'] = True
                self.initialized = True
                print("✅ Engine initialization complete")
                return True
                
            except Exception as e:
                print(f"❌ Engine initialization failed: {e}")
                self.load_errors.append(f"Engine initialization: {e}")
                return False

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status report
        Useful for debugging and system monitoring
        """
        print("🔍 DEBUG: get_system_status() called")
        try:
            print(f"🔍 DEBUG: self.initialized = {getattr(self, 'initialized', 'MISSING')}")
            print(f"🔍 DEBUG: self.load_start_time = {getattr(self, 'load_start_time', 'MISSING')}")
            print(f"🔍 DEBUG: self.system_health = {getattr(self, 'system_health', 'MISSING')}")
            print(f"🔍 DEBUG: self.load_errors = {getattr(self, 'load_errors', 'MISSING')}")
            
            # Try each calculation separately
            systems_healthy = sum(self.system_health.values()) if hasattr(self, 'system_health') else 0
            total_systems = len(self.system_health) if hasattr(self, 'system_health') else 0
            
            print(f"🔍 DEBUG: systems_healthy = {systems_healthy}, total_systems = {total_systems}")
            
            #if self.load_start_time is None:
            #    load_time_calc = None
            #    print("🔍 DEBUG: load_start_time is None")
            #else:
            #    load_time_calc = (datetime.now() - self.load_start_time).total_seconds()

            result = {
                'initialized': self.initialized,
                'load_time': None,  #load_time_calc,
                'systems_healthy': sum(self.system_health.values()),
                'total_systems': len(self.system_health),
                'health_details': self.system_health.copy(),
                'error_count': len(self.load_errors),
                'errors': self.load_errors.copy()
            }
        
            print(f"🔍 DEBUG: Returning result = {result}")
            return result


        except Exception as e:
            print(f"❌ ERROR in get_system_status(): {e}")
            import traceback
            traceback.print_exc()
            return None  # This will help us see the actual error



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
               
        return validation_passed
    
    def reload_all_systems(self) -> bool:
        """
        Reloads all game data systems by re-initializing them.
        """
        print("🔄 DataManager: Reloading all systems...")
        self.initialized = False
        self.load_errors = []
        return initialize_game_data(self.game_state)

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status report
        Useful for debugging and system monitoring
        """
        load_time = None
        if self.load_start_time:
            load_time = (datetime.now() - self.load_start_time).total_seconds()
            
        return {
            'initialized': self.initialized,
            'load_time': load_time,
            'systems_healthy': sum(self.system_health.values()),
            'total_systems': len(self.system_health),
            'health_details': self.system_health.copy(),
            'error_count': len(self.load_errors),
            'errors': self.load_errors.copy()
        }
    
    def get_manager(self, manager_type: str):
        """
        Get specific manager instance by type
        Safe accessor with proper error handling
        """
        manager_map = {
            'items': self.item_manager,
            'npcs': self.npc_manager, 
            'locations': self.location_manager,
            'inventory': self.inventory_engine,
            'commerce': self.commerce_engine,
            'dialogue': self.dialogue_engine,
            'character': self.character_engine
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
    Get the global data manager instance.
    """
    global data_manager
    if data_manager is None:
        data_manager = DataManager()
    return data_manager

def initialize_game_data(game_state_ref, data_manager) -> bool:
    """
    The new convenience function to trigger all initialization.
    It takes the DataManager and GameState as arguments.
    """
    try:
        data_manager.load_all_data()
        data_manager.initialize_all_engines(game_state_ref)
        data_manager.initialized = True
        return True
    except Exception as e:
        print(f"❌ FATAL: Error during data initialization: {e}")
        return False
    
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
    pass