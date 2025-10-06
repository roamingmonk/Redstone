# utils/location_loader.py
"""
Location Configuration Loader
Handles loading and validation of location JSON files
"""

import json
import os
from typing import Dict, Any, Optional, List
from ui.base_location import BaseLocation, create_location


class LocationManager:
    """
    Manages loading and caching of location configurations
    
    This class handles the JSON loading, validation, and caching of location data.
    It integrates with the DataManager system and provides location instances to
    the ScreenManager.
    """
    
    def __init__(self, data_directory: str = "data/locations"):
        """
        Initialize the LocationManager
        
        Args:
            data_directory: Path to directory containing location JSON files
        """
        self.data_directory = data_directory
        self.loaded_locations = {}  # Cache for loaded location data
        self.location_instances = {}  # Cache for BaseLocation instances
        
        # Ensure data directory exists
        if not os.path.exists(data_directory):
            print(f"⚠️ Location data directory not found: {data_directory}")
            print(f"Creating directory: {data_directory}")
            os.makedirs(data_directory, exist_ok=True)
    
    def get_all_area_ids(self, location_id: str) -> List[str]:
        """
        Get list of all area IDs for a location
        
        Args:
            location_id: Location identifier
            
        Returns:
            List of area IDs (e.g., ['main', 'basement_cleared'])
        """
        location_data = self.load_location_data(location_id)
        if not location_data:
            return []
        
        # Get the inner location object
        location_obj = location_data.get(location_id, {})
        areas = location_obj.get('areas', {})
        
        return list(areas.keys())
    
    def load_location_data(self, location_id: str) -> Optional[Dict[str, Any]]:
        """
        Load location data from JSON file
        
        Args:
            location_id: ID of location to load (e.g., 'broken_blade')
            
        Returns:
            Dictionary containing location data or None if not found
        """
        
        # Check cache first
        if location_id in self.loaded_locations:
            return self.loaded_locations[location_id]
        
        # Try to load from file
        filename = f"{location_id}.json"
        filepath = os.path.join(self.data_directory, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️ Location file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Validate basic structure
                if not self._validate_location_data(data, location_id):
                    return None
                
                # Cache the loaded data
                self.loaded_locations[location_id] = data
                print(f"📍 Loaded location data: {location_id}")
                return data
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in {filepath}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading location {location_id}: {e}")
            return None
    
    def _validate_location_data(self, data: Dict[str, Any], location_id: str) -> bool:
        """
        Validate location data structure
        
        Args:
            data: Location data dictionary
            location_id: Expected location ID
            
        Returns:
            True if valid, False otherwise
        """
        
        # Check if data contains the location_id key
        if location_id not in data:
            print(f"❌ Location data missing key '{location_id}'")
            return False
        
        location_data = data[location_id]
        
        # Check required fields
        required_fields = ['location_id', 'name', 'areas']
        for field in required_fields:
            if field not in location_data:
                print(f"❌ Location {location_id} missing required field: {field}")
                return False
        
        # Validate areas
        areas = location_data.get('areas', {})
        if not areas:
            print(f"❌ Location {location_id} has no areas defined")
            return False
        
        # Validate each area
        for area_id, area_data in areas.items():
            if not isinstance(area_data, dict):
                print(f"❌ Area {area_id} in location {location_id} is not a dictionary")
                return False
            
            # Check area has required fields
            if 'type' not in area_data:
                print(f"⚠️ Area {area_id} missing type, defaulting to 'action_hub'")
                area_data['type'] = 'action_hub'
        
        print(f"✅ Location data validated: {location_id}")
        return True
    
    def get_location_instance(self, location_id: str) -> Optional[BaseLocation]:
        """
        Get a BaseLocation instance for the specified location
        
        Args:
            location_id: ID of location to get instance for
            
        Returns:
            BaseLocation instance or None if not found/invalid
        """
        
        # Check instance cache first
        if location_id in self.location_instances:
            return self.location_instances[location_id]
        
        # Load data and create instance
        location_data = self.load_location_data(location_id)
        if not location_data:
            return None
        
        try:
            # Extract the location-specific data
            location_config = location_data[location_id]
            
            # Create BaseLocation instance
            location_instance = create_location(location_config)
            
            # Cache the instance
            self.location_instances[location_id] = location_instance
            print(f"🏗️ Created location instance: {location_id} ({location_instance.location_type})")
            
            return location_instance
            
        except Exception as e:
            print(f"❌ Error creating location instance for {location_id}: {e}")
            return None
    
    def get_area_data(self, location_id: str, area_id: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific area within a location
        
        Args:
            location_id: ID of the location
            area_id: ID of the area within the location
            
        Returns:
            Dictionary containing area data or None if not found
        """
        
        location_data = self.load_location_data(location_id)
        if not location_data:
            return None
        
        location_config = location_data.get(location_id, {})
        areas = location_config.get('areas', {})
        
        return areas.get(area_id)
    
    def list_available_locations(self) -> List[str]:
        """
        Get list of all available location IDs
        
        Returns:
            List of location IDs that have JSON files
        """
        
        if not os.path.exists(self.data_directory):
            return []
        
        locations = []
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.json'):
                location_id = filename[:-5]  # Remove .json extension
                locations.append(location_id)
        
        return sorted(locations)
    
    def reload_location(self, location_id: str) -> bool:
        """
        Force reload of a location (useful for development)
        
        Args:
            location_id: ID of location to reload
            
        Returns:
            True if reload successful, False otherwise
        """
        
        # Clear caches
        if location_id in self.loaded_locations:
            del self.loaded_locations[location_id]
        if location_id in self.location_instances:
            del self.location_instances[location_id]
        
        # Reload
        location_instance = self.get_location_instance(location_id)
        return location_instance is not None


# Global instance for easy access
_location_manager = None

def get_location_manager() -> LocationManager:
    """Get the global LocationManager instance"""
    global _location_manager
    if _location_manager is None:
        _location_manager = LocationManager()
    return _location_manager

def initialize_location_manager(data_directory: str = "data/locations") -> LocationManager:
    """Initialize the global LocationManager with specific directory"""
    global _location_manager
    _location_manager = LocationManager(data_directory)
    return _location_manager