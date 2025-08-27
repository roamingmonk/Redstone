"""
Terror in Redstone - Location Manager (Simple Version)
Professional location data management system for RPG locations.
"""

import json
import os

class LocationManager:
    """Simple location management system - loads and manages location data from JSON files."""
    
    def __init__(self, data_directory="data/locations"):
        """Initialize the location manager."""
        self.data_directory = data_directory
        self.locations = {}
        self.load_all_locations()
    
    def load_all_locations(self):
        """Load all location files from the data directory."""
        if not os.path.exists(self.data_directory):
            print("Warning: Location data directory not found:", self.data_directory)
            return
        
        # Load all JSON files in the locations directory
        for filename in os.listdir(self.data_directory):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_directory, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        location_data = json.load(file)
                        # Extract locations and store by their internal ID (like NPCManager does)
                        for location_key, location_info in location_data.items():
                            location_id = location_info.get('id')
                            if location_id:
                                self.locations[location_id] = location_info
                                print(f"✅ Location registered with ID: {location_id}")
                            else:
                                print(f"❌ Location missing 'id' field in {filename}")
                        print("✅ Loaded location data:", filename)
                except Exception as e:
                    print("❌ Failed to load location file", filename, ":", e)
    
    def get_location_data(self, location_id):
        """Get complete location data by ID."""
        return self.locations.get(location_id)
    
    def get_area_data(self, location_id, area_id):
        """Get specific area data within a location."""
        location = self.get_location_data(location_id)
        if location and 'areas' in location:
            return location['areas'].get(area_id)
        return None
    
    def get_description(self, location_id, area_id, description_type="atmosphere"):
        """Get location description text."""
        area_data = self.get_area_data(location_id, area_id)
        if area_data and 'description' in area_data:
            description = area_data['description'].get(description_type, "")
            if description:
                return description
        
        return "[Description not found: " + location_id + "." + area_id + "." + description_type + "]"
    
    def get_display_name(self, location_id, area_id):
        """Get the display name for a location area."""
        area_data = self.get_area_data(location_id, area_id)
        if area_data:
            return area_data['display_name']
        return 'Unknown Location'
    
    def get_available_actions(self, location_id, area_id):
        """Get list of available actions in a location area."""
        area_data = self.get_area_data(location_id, area_id)
        if area_data:
            return area_data.get('available_actions', [])
        return []
    
    def get_npcs_present(self, location_id, area_id):
        """Get list of NPCs present in a location area."""
        area_data = self.get_area_data(location_id, area_id)
        if area_data:
            return area_data.get('npcs_present', [])
        return []
    
    def get_location_property(self, location_id, area_id, property_name, default=None):
        """Get a specific property value from a location area."""
        area_data = self.get_area_data(location_id, area_id)
        if area_data and 'properties' in area_data:
            return area_data['properties'].get(property_name, default)
        return default
    
    def has_shop(self, location_id, area_id):
        """Check if a location area has shopping functionality."""
        return self.get_location_property(location_id, area_id, 'has_shop', False)
    
    def get_merchant_type(self, location_id, area_id):
        """Get the merchant type for a location area."""
        return self.get_location_property(location_id, area_id, 'merchant_type')
    
    def list_all_locations(self):
        """Get list of all loaded location IDs."""
        return list(self.locations.keys())
    
    def list_location_areas(self, location_id):
        """Get list of all areas within a location."""
        location = self.get_location_data(location_id)
        if location and 'areas' in location:
            return list(location['areas'].keys())
        return []
    
    def debug_location_info(self, location_id):
        """Get debug information about a location."""
        location = self.get_location_data(location_id)
        if not location:
            return "Location '" + location_id + "' not found!"
        
        info = ["Location: " + location.get('name', location_id)]
        info.append("Type: " + location.get('type', 'unknown'))
        
        if 'areas' in location:
            info.append("Areas (" + str(len(location['areas'])) + "):")
            for area_id, area_data in location['areas'].items():
                info.append("  - " + area_id + ": " + area_data.get('name', 'Unnamed'))
        
        return "\n".join(info)

# Global instance for easy access
location_manager = LocationManager()

def get_location_manager():
    """Get the global location manager instance."""
    return location_manager