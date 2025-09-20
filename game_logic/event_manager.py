# game_logic/event_manager.py
"""
Event Manager - Professional Game Communication System
Replaces direct method calls with clean event-driven architecture

This is the foundation that enables:
- Loose coupling between game systems
- Easy addition of new features without code changes
- Professional debugging and logging
- Future-proofing for complex RPG systems

Event Types We'll Implement:
- NPC_CLICKED: When player clicks an NPC
- ITEM_PURCHASED: When shopping transaction completes
- SCREEN_CHANGE: When transitioning between screens
- DIALOGUE_CHOICE: When player selects dialogue option
- SAVE_REQUESTED: When game needs to be saved
"""

from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
import traceback

class EventManager:
    """
    Professional event management system for Terror in Redstone
    
    Handles all inter-system communication using event-driven architecture.
    This replaces direct method calls with clean message passing.
    """
    
    def __init__(self):
        """Initialize the event management system"""
        # Dictionary of event_type -> list of callback functions
        self.listeners: Dict[str, List[Callable]] = defaultdict(list)
        
        # Event history for debugging (last 50 events)
        self.event_history: List[Dict[str, Any]] = []
        self.max_history = 50
        
        # Enable/disable event logging for development
        self.debug_logging = True
        
        # Service registry
        self.services = {}  

        print("🎯 EventManager initialized - Professional event system ready!")
    
    def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Emit an event to all registered listeners
        
        Args:
            event_type: Type of event (e.g., 'NPC_CLICKED', 'ITEM_PURCHASED')
            data: Optional data dictionary to pass to event handlers
            
        Returns:
            bool: True if event was processed successfully
        """
        if data is None:
            data = {}
            
        # Add event to history for debugging
        event_record = {
            'type': event_type,
            'data': data.copy(),
            'listeners_called': len(self.listeners[event_type])
        }
        
        self.event_history.append(event_record)
        
        # Keep history size manageable
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        #if self.debug_logging:
        #    print(f"📡 EVENT EM: {event_type} | Data: {data} | Listeners: {len(self.listeners[event_type])}")
        
        # In event_manager.py emit method, add:
        if event_type == "DIALOGUE_ENDED":
            print(f"🔍 DEBUG: DIALOGUE_ENDED emitted with data: {data}")  # Use 'data' not 'event_data'
            #print(f"🔍 DEBUG: Listeners for DIALOGUE_ENDED: {len(self.listeners.get('DIALOGUE_ENDED', []))}")
        # Call all registered listeners for this event type
        success = True
        for callback in self.listeners[event_type]:
            try:
                callback(data)
            except Exception as e:
                print(f"❌ EM Error in event listener for {event_type}: {e}")
                print(f"   EM Callback: {callback}")
                traceback.print_exc()
                success = False
        
        return success
    
    def register(self, event_type: str, callback: Callable) -> bool:
        """
        Register a callback function to listen for specific event type
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
            
        Returns:
            bool: True if registration successful
        """
        try:
            self.listeners[event_type].append(callback)
            
            if self.debug_logging:
                print(f"🔗 REGISTERED: {callback.__name__} for event '{event_type}'")
            
            return True
            
        except Exception as e:
            print(f"❌ EM Failed to register event listener: {e}")
            return False
    
    def unregister(self, event_type: str, callback: Callable) -> bool:
        """
        Remove a callback function from event listeners
        
        Args:
            event_type: Type of event to stop listening for
            callback: Function to remove from listeners
            
        Returns:
            bool: True if removal successful
        """
        try:
            if callback in self.listeners[event_type]:
                self.listeners[event_type].remove(callback)
                
                if self.debug_logging:
                    print(f"🔓 EM UNREGISTERED: {callback.__name__} from event '{event_type}'")
                
                return True
            else:
                print(f"⚠️ EM Callback not found in listeners for {event_type}")
                return False
                
        except Exception as e:
            print(f"❌ EM Failed to unregister event listener: {e}")
            return False

    def register_service(self, service_name: str, service_instance):
        """Register a service for access by other components"""
        self.services[service_name] = service_instance
        print(f"📋 Service registered: {service_name}")

    def get_service(self, service_name: str):
        """Get a registered service"""
        return self.services.get(service_name)


    def get_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent event history for debugging
        
        Args:
            limit: Number of recent events to return
            
        Returns:
            List of recent event records
        """
        return self.event_history[-limit:]
    
    def clear_all_listeners(self) -> None:
        """Clear all event listeners (useful for cleanup/testing)"""
        self.listeners.clear()
        print("🧹 All event listeners cleared")
    
    def get_listener_count(self, event_type: str) -> int:
        """Get number of listeners for specific event type"""
        return len(self.listeners[event_type])
    
    def get_all_event_types(self) -> List[str]:
        """Get list of all registered event types"""
        return list(self.listeners.keys())
    
    def enable_debug_logging(self, enabled: bool = True) -> None:
        """Enable or disable debug logging for events"""
        self.debug_logging = enabled
        status = "enabled" if enabled else "disabled"
        print(f"📊 EM Event debug logging {status}")


# ==========================================
# GLOBAL EVENT MANAGER INSTANCE
# ==========================================

# Global event manager instance (initialized by GameController)
event_manager: Optional[EventManager] = None

def get_event_manager() -> EventManager:
    """
    Get the global event manager instance
    Will be initialized by GameController during startup
    """
    global event_manager
    if event_manager is None:
        event_manager = EventManager()
    return event_manager

def initialize_event_manager() -> EventManager:
    """
    Initialize the global event manager
    Called by GameController during system startup
    """
    global event_manager
    event_manager = EventManager()
    print("🔧 Initialized global EventManager")
    return event_manager


# ==========================================
# EVENT TYPE CONSTANTS
# ==========================================

class EventTypes:
    """
    Standard event types for Terror in Redstone
    Using constants prevents typos and makes events discoverable
    """
    
    # Screen and Navigation Events
    SCREEN_CHANGE = "screen_change"
    LOCATION_ENTERED = "location_entered"
    LOCATION_EXITED = "location_exited"
    
    # NPC and Dialogue Events  
    NPC_CLICKED = "npc_clicked"
    DIALOGUE_STARTED = "dialogue_started"
    DIALOGUE_CHOICE = "dialogue_choice"
    DIALOGUE_ENDED = "dialogue_ended"
    
    # Commerce and Inventory Events
    ITEM_PURCHASED = "item_purchased"
    ITEM_SOLD = "item_sold"
    SHOPPING_CART_UPDATED = "shopping_cart_updated"
    INVENTORY_CHANGED = "inventory_changed"
    
    # ==========================================
    # SAVE/LOAD SYSTEM EVENTS
    # ==========================================
    
    # Save Screen Events (Semantic Actions)
    SAVE_SLOT_SELECTED = "SAVE_SLOT_SELECTED"         # User clicks a save slot
    SAVE_GAME_CONFIRM = "SAVE_GAME_CONFIRM"           # User clicks SAVE button
    SAVE_AND_QUIT_CONFIRM = "SAVE_AND_QUIT_CONFIRM"   # User clicks SAVE&QUIT button
    SAVE_SCREEN_CANCEL = "SAVE_SCREEN_CANCEL"         # User clicks CANCEL button
        
    # Load Screen Events (Semantic Actions)  
    LOAD_SLOT_SELECTED = "LOAD_SLOT_SELECTED"         # User clicks a load slot
    LOAD_GAME_CONFIRM = "LOAD_GAME_CONFIRM"           # User clicks LOAD button
    DELETE_SAVE_CONFIRM = "DELETE_SAVE_CONFIRM"       # User clicks DELETE button
    LOAD_SCREEN_CANCEL = "LOAD_SCREEN_CANCEL"         # User clicks CANCEL button
    
    # SaveManager Internal Events
    SAVE_INFO_REQUESTED = "SAVE_INFO_REQUESTED"       # Request save slot information
    SAVE_INFO_RESPONSE = "SAVE_INFO_RESPONSE"         # SaveManager responds with save info
    
    # Game State Lifecycle Events (Notifications)
    GAME_SAVED = "GAME_SAVED"                         # Successful save completion
    GAME_LOADED = "GAME_LOADED"                       # Successful load completion
    SAVE_FAILED = "SAVE_FAILED"                       # Save operation failed
    LOAD_FAILED = "LOAD_FAILED"                       # Load operation failed
    SAVE_DELETED = "SAVE_DELETED"                     # Save file successfully deleted
    DELETE_FAILED = "DELETE_FAILED"                   # Delete operation failed
    
    # Universal Overlay Events
    OVERLAY_TOGGLE = "OVERLAY_TOGGLE"                 # Generic overlay toggle
    ESCAPE_PRESSED = "ESCAPE_PRESSED"                 # ESC key pressed

    # Character Events
    CHARACTER_CREATED = "character_created"
    CHARACTER_STATS_CHANGED = "character_stats_changed"
    PARTY_MEMBER_JOINED = "party_member_joined"
    
    # Quest Events (Future)
    QUEST_STARTED = "quest_started"
    QUEST_COMPLETED = "quest_completed"
    QUEST_UPDATED = "quest_updated"
