# Phase 11.5: Location Navigation System Conversion
## Converting Act II Locations from Static Buttons to Scrollable Tile Navigation

**Document Version:** 2.0 (UPDATED WITH CLARIFICATIONS)  
**Date:** November 1, 2025  
**Status:** Ready for Implementation  
**Goal:** Implement HYBRID system - scrollable exploration maps for investigation areas, button-based screens for climactic encounters

---

## 🎯 EXECUTIVE SUMMARY - UPDATED

**Current State:** Act II locations use static ActionHubLocation screens with button-based interactions defined in JSON.

**Target State - HYBRID APPROACH:**
- **Exploration Areas** (exterior, interior): Scrollable 20x20 tile maps with tile-based interactions
- **Encounter Areas** (crypt, boss rooms): KEEP as ActionHub button screens for focused tactical choices
- **Best of Both Worlds:** Immersive exploration + focused dramatic moments

**Design Philosophy:** 
- Walk around freely to discover and investigate (like Ultima, Eye of the Beholder)
- Important story encounters stay menu-driven for clarity and dramatic pacing
- Random encounters add danger to exploration
- Searchables reward thorough investigation

---

## ✅ DESIGN CLARIFICATIONS (Nov 1, 2025)

### Map Design
- ✅ **Grid Size:** 20x20 tiles per area
- ✅ **Layout Format:** ASCII string arrays (easy to design and edit)
- ✅ **Visual Style:** Colored tile rendering via TileGraphicsManager

### Searchable Objects
- ✅ **Visual Cue:** Highlighted tiles or distinct colors for searchables
- ✅ **Interaction:** Walk to tile + press ENTER to search/examine
- ✅ **Perception System:** Affects loot quantity/quality, NOT availability of key quest items
- ✅ **One-Time Searches:** Each searchable location can only be searched once (flag-based)
- ✅ **Dialogue Integration:** Examining objects can trigger dialogue screens with descriptions

### Combat Triggers
- ✅ **Random Encounters:** Step-on-tile automatic triggers, REPEATABLE (can re-encounter)
- ✅ **Story Encounters:** One-time only, often initiated via button/dialogue choice
- ✅ **Implementation:** 
  - Random: No flag check, can trigger multiple times
  - Story: Flag check prevents re-trigger after completion

### Swamp Church Specific Design
- ✅ **Exterior:** Scrollable 20x20 map
  - Examine ancient symbols tile (triggers dialogue)
  - Random skeleton/ghost encounters (repeatable, step-on-tile)
  - Entrance to interior
- ✅ **Interior:** Scrollable 20x20 map
  - Search pews tile (loot check)
  - Examine altar tile (triggers dialogue)
  - Entrance to crypt
- ✅ **Crypt:** KEEP as ActionHub button screen (existing design)
  - Button: Search the Crypt (loot check)
  - Button: Investigate Ritual Site (dialogue)
  - Button: Confront Cultists (initiates combat)
  - This preserves dramatic pacing for climactic encounter

---

## 📊 CURRENT ARCHITECTURE ANALYSIS

### What Currently Exists

**1. Town Navigation System** (WORKING MODEL TO COPY)
- **File:** `screens/redstone_town.py`
- **Map Data:** `data/maps/redstone_town_map.py`
- **Utility:** `ui/base_location_navigation.py` (NavigationRenderer)
- **Features:**
  - 16x12 scrollable tile grid with camera system
  - ASCII string-based map layout
  - Building entrance tiles (walk to + press ENTER)
  - NPC interaction tiles (walk to + face + press ENTER)
  - Colored tile rendering
  - Turn-then-move mechanics
  - Debug info display

**2. ActionHubLocation System** (CURRENT ACT II - PARTIALLY KEEP)
- **File:** `ui/base_location.py` (ActionHubLocation class)
- **Data:** `data/locations/swamp_church.json` (example)
- **Features:**
  - Static screen with title and description
  - Button-based actions (navigate, dialogue, loot_check, combat)
  - Flag-based requirements for conditional actions
  - JSON-driven configuration
- **Status:** KEEP for crypt/boss rooms, REPLACE for exploration areas

**3. Regional Map** (EXPLORATION HUB)
- **File:** `screens/exploration_hub.py` (planned)
- **Type:** Clickable tile-based world map showing discovered locations
- **Purpose:** Hub for selecting which location to visit
- **Status:** Stays as-is, just update navigation targets

---

## 🗺️ NEW SYSTEM DESIGN - HYBRID APPROACH

### Hierarchical Navigation Structure - UPDATED

```
REGIONAL MAP (Exploration Hub - clickable icons)
    ↓ Click Church Icon
CHURCH EXTERIOR MAP (20x20 scrollable tiles) ← NEW NAVIGATION SCREEN
    │ - Walk around, examine symbols tile
    │ - Random skeleton encounters (repeatable)
    ↓ Walk to door + ENTER
CHURCH INTERIOR MAP (20x20 scrollable tiles) ← NEW NAVIGATION SCREEN
    │ - Walk around, search pews tile, examine altar tile
    ↓ Walk to stairs + ENTER  
CHURCH CRYPT (ActionHub button screen) ← EXISTING SCREEN (KEEP)
    │ - Button: Search Crypt
    │ - Button: Investigate Ritual
    │ - Button: Confront Cultists → COMBAT
    ↓ Return button
Back to INTERIOR or REGIONAL MAP
```

### Tile Interaction Types - COMPLETE SPEC

**Type 1: AREA TRANSITION TILES** (Like building entrances)
- **Purpose:** Navigate between areas/screens
- **Interaction:** Walk to tile + press ENTER
- **Visual:** Distinct tile type (door, stairs, gate)
- **Example:** Church door entrance
- **Data Structure:**
```python
AREA_TRANSITIONS = {
    'church_door': {
        'entrance_tiles': [(10, 5), (11, 5)],  # Where player stands
        'building_pos': [(10, 4), (11, 4)],    # Door tiles themselves
        'info': {
            'name': 'Church Entrance',
            'interaction_type': 'navigation',
            'target_screen': 'swamp_church_interior_nav',  # Screen to load
            'action': 'Enter Church',
            'requirements': {}  # Optional flag checks
        }
    }
}
```

**Type 2: NPC INTERACTION TILES** (Already implemented)
- **Purpose:** Talk to NPCs in the area
- **Interaction:** Walk to NPC + face them + press ENTER
- **Visual:** NPC sprite on tile
- **Example:** Mysterious hooded figure in swamp
- **Data Structure:**
```python
LOCATION_NPCS = {
    'mysterious_figure': {
        'sprite_type': 'hooded_figure',
        'default_position': (5, 5),
        'interaction_tiles': [(5, 6), (4, 5), (6, 5), (5, 4)],
        'display_name': 'Mysterious Figure',
        'dialogue_id': 'swamp_mysterious_figure',
        'conditions': None  # Optional spawn conditions
    }
}
```

**Type 3: SEARCHABLE/EXAMINABLE TILES** (NEW - PRIMARY ADDITION)
- **Purpose:** Investigate objects, find loot, discover lore
- **Interaction:** Walk to tile + press ENTER
- **Visual:** Highlighted tile or distinct color (e.g., darker/lighter shade)
- **Example:** Ancient symbols, altar, pews, graves
- **One-Time:** Flag prevents re-searching
- **Perception:** Can affect loot quantity but key items always found
- **Data Structure:**
```python
SEARCHABLE_OBJECTS = {
    'ancient_symbols': {
        'search_tiles': [(8, 3), (9, 3), (10, 3)],  # Where player can stand
        'object_pos': [(9, 2)],  # Object tile itself (for visual highlight)
        'info': {
            'name': 'Ancient Symbols',
            'interaction_type': 'searchable',
            'description': 'Strange symbols carved into stone.',
            
            # OPTION A: Trigger dialogue (for lore/descriptions)
            'examine_dialogue': 'swamp_symbols_examine',  # Dialogue screen ID
            
            # OPTION B: Give loot (for items)
            'loot_table': 'swamp_exterior_symbols',  # Loot pool ID
            
            # Both options can be used together!
            
            'flag_set': 'examined_swamp_symbols',  # Prevents re-examination
            'requirements': {},  # Optional: requires flag to be searchable
            'one_time': True
        }
    },
    'church_pews': {
        'search_tiles': [(7, 8), (8, 8), (9, 8), (10, 8)],
        'object_pos': [(7, 7), (8, 7), (9, 7), (10, 7)],  # Pew tiles
        'info': {
            'name': 'Church Pews',
            'interaction_type': 'searchable',
            'description': 'Overturned pews, scattered hymnals.',
            'loot_table': 'swamp_church_pews',  # Items hidden under pews
            'flag_set': 'searched_church_pews',
            'requirements': {},
            'one_time': True
        }
    }
}
```

**Type 4: COMBAT TRIGGER TILES** (NEW - RANDOM ENCOUNTERS)
- **Purpose:** Initiate combat encounters during exploration
- **Interaction:** Step on tile (automatic)
- **Visual:** Can be hidden (surprise) or obvious (warning)
- **Repeatable:** Random encounters can re-trigger, story encounters one-time only
- **Example:** Skeleton ambush in swamp exterior
- **Data Structure:**
```python
COMBAT_TRIGGERS = {
    (5, 8): {  # Tile coordinates
        'encounter_id': 'skeleton_ambush',
        'trigger_type': 'step_on',  # Automatic when player moves onto tile
        'repeatable': True,  # Random encounter - can happen multiple times
        'chance': 0.30,  # 30% chance to trigger each time stepped on
        'flag_check': None,  # No flag requirement
        'flag_set': None  # Doesn't set a flag (repeatable)
    },
    (12, 15): {  # Different tile
        'encounter_id': 'ghost_encounter',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.25,  # 25% chance
        'flag_check': None,
        'flag_set': None
    }
}

# For story encounters (one-time), use flag_set:
# (3, 3): {
#     'encounter_id': 'boss_ambush',
#     'trigger_type': 'step_on',
#     'repeatable': False,
#     'chance': 1.0,  # Always triggers first time
#     'flag_check': None,
#     'flag_set': 'boss_ambush_defeated'  # Prevents re-trigger
# }
```

---

## 🔧 TECHNICAL IMPLEMENTATION ROADMAP

### Phase 11.5A: Extend NavigationRenderer (Infrastructure)
**Duration:** 1-2 hours  
**Goal:** Add searchable object and combat trigger support to shared navigation utility

#### Tasks

**1. Add Searchable Object Support**

**File to Modify:** `ui/base_location_navigation.py`

Add new method to NavigationRenderer class:

```python
def check_searchable_object(self, player_x, player_y):
    """
    Check if player is standing at a searchable object tile
    
    Args:
        player_x, player_y: Player's current position
    
    Returns:
        dict or None: Searchable info if present, None otherwise
    """
    get_searchable = self.map_functions.get('get_searchable_info')
    if get_searchable:
        return get_searchable(player_x, player_y)
    return None
```

**2. Add Combat Trigger Support**

Add new method to NavigationRenderer class:

```python
def check_combat_trigger(self, player_x, player_y):
    """
    Check if player stepped on a combat trigger tile
    
    Args:
        player_x, player_y: Player's current position
    
    Returns:
        dict or None: Combat trigger info if present, None otherwise
    """
    get_combat = self.map_functions.get('get_combat_trigger')
    if get_combat:
        return get_combat(player_x, player_y)
    return None
```

**3. Update Config Requirements**

NavigationRenderer config now supports these map_functions:
```python
config = {
    'map_width': 20,
    'map_height': 20,
    'location_id': 'swamp_church_exterior',
    'map_functions': {
        'get_tile_type': get_tile_type,           # Required
        'is_walkable': is_walkable,               # Required
        'get_tile_color': get_tile_color,         # Required
        'get_building_info': get_transition_at_entrance,  # Existing (for transitions)
        'get_searchable_info': get_searchable_at_position,  # NEW
        'get_combat_trigger': get_combat_trigger  # NEW
    }
}
```

**Success Criteria:**
- ✅ NavigationRenderer has check_searchable_object() method
- ✅ NavigationRenderer has check_combat_trigger() method
- ✅ Methods return None if map doesn't provide those functions (backward compatible)
- ✅ Town navigation still works (doesn't use new features)

---

### Phase 11.5B: Swamp Church Exterior (First Scrollable Exploration Area)
**Duration:** 2-3 hours  
**Goal:** Create complete exterior navigation screen as template for all future areas

#### Step 1: Create Map Data File

**New File:** `data/maps/swamp_church_exterior_map.py`

```python
"""
Swamp Church Exterior Map Data
20x20 tile grid for foggy swamp church approach
"""

SWAMP_CHURCH_EXT_WIDTH = 20
SWAMP_CHURCH_EXT_HEIGHT = 20
SWAMP_CHURCH_EXT_SPAWN_X = 10
SWAMP_CHURCH_EXT_SPAWN_Y = 18  # Enter from bottom (arriving from regional map)

# Tile type definitions
TILE_TYPES = {
    '#': 'wall',          # Map boundary walls
    '.': 'ground',        # Walkable muddy ground
    'w': 'water',         # Water pools (not walkable)
    't': 'tree',          # Trees (not walkable)
    's': 'swamp',         # Swamp mud (walkable, slower?)
    'g': 'grave',         # Graveyard tiles (walkable)
    'C': 'church_wall',   # Church exterior walls (not walkable)
    'D': 'church_door',   # Church entrance (transition point)
    'S': 'symbols',       # Ancient symbols (searchable/examinable)
    'a': 'altar',         # Outdoor altar (searchable)
    'R': 'random_combat', # Random encounter zone (special tile)
}

WALKABLE_TILES = {'ground', 'swamp', 'grave'}

# ASCII map layout - 20x20 grid
SWAMP_CHURCH_EXT_MAP = [
    "####################",  # Row 0
    "#tttt.........tttttt#",  # Row 1 - Trees frame edges
    "#tt..wwww..wwww...tt#",  # Row 2 - Water pools
    "#t.wwssSS..SSssw..tt#",  # Row 3 - SS = symbols (searchable)
    "#..wsssgggggsssw...t#",  # Row 4 - graves
    "#..wssg####gssw....t#",  # Row 5 - Church walls start
    "#...ssg#CC#gsw.....#",  # Row 6 - CC = church walls
    "#...sgg#DD#gg......#",  # Row 7 - DD = door (transition)
    "#....gg####gg......#",  # Row 8 - Church structure
    "#.....ggaagg.......#",  # Row 9 - aa = altar (searchable)
    "#......gggg........#",  # Row 10
    "#.......RR.........#",  # Row 11 - RR = random combat zone
    "#.....t.RR.....t...#",  # Row 12
    "#....ttt......ttt..#",  # Row 13
    "#...ttttt....ttttt.#",  # Row 14
    "#..ttttttt..tttttt.#",  # Row 15
    "#.....ttt....ttt...#",  # Row 16
    "#......t......t....#",  # Row 17
    "#.................@#",  # Row 18 - @ = spawn point
    "####################"   # Row 19
]

def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < SWAMP_CHURCH_EXT_HEIGHT and 0 <= x < SWAMP_CHURCH_EXT_WIDTH:
        char = SWAMP_CHURCH_EXT_MAP[y][x]
        return TILE_TYPES.get(char, 'wall')
    return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_tile_color(x, y):
    """Get color for tile rendering"""
    tile_type = get_tile_type(x, y)
    TILE_COLORS = {
        'wall': (60, 60, 60),         # Dark gray boundary
        'ground': (101, 67, 33),      # Brown muddy earth
        'water': (0, 119, 190),       # Blue water
        'tree': (34, 139, 34),        # Forest green
        'swamp': (85, 107, 47),       # Olive/dark green swamp
        'grave': (105, 105, 105),     # Gray tombstones
        'church_wall': (169, 169, 169),  # Light gray stone
        'church_door': (139, 69, 19), # Brown door
        'symbols': (200, 150, 100),   # Tan/beige (HIGHLIGHT for searchable)
        'altar': (180, 180, 180),     # Light gray (HIGHLIGHT for searchable)
        'random_combat': (120, 80, 60),  # Slightly darker ground (subtle)
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# Area transitions (navigation between areas/screens)
AREA_TRANSITIONS = {
    'church_entrance': {
        'entrance_tiles': [(9, 7), (10, 7)],  # Standing in front of doors
        'building_pos': [(9, 7), (10, 7)],    # Door tiles
        'info': {
            'name': 'Church Entrance',
            'interaction_type': 'navigation',
            'target_screen': 'swamp_church_interior_nav',  # Interior map screen
            'action': 'Enter Church',
            'requirements': {}  # No special requirements to enter
        }
    },
    'return_to_region': {
        'entrance_tiles': [(10, 18), (10, 19)],  # Bottom spawn area
        'building_pos': [(10, 19)],
        'info': {
            'name': 'Leave Area',
            'interaction_type': 'navigation',
            'target_screen': 'exploration_hub',  # Back to regional map
            'action': 'Return to Region Map',
            'requirements': {}
        }
    }
}

def get_transition_at_entrance(player_x, player_y):
    """Check if player is at area transition point"""
    for transition_id, transition_data in AREA_TRANSITIONS.items():
        if (player_x, player_y) in transition_data['entrance_tiles']:
            return transition_data['info']
    return None

# Searchable objects (examine/loot)
SEARCHABLE_OBJECTS = {
    'ancient_symbols': {
        'search_tiles': [(8, 3), (9, 3), (10, 3), (11, 3)],  # Around symbols
        'object_pos': [(9, 3), (10, 3)],  # Symbol tiles (for highlight detection)
        'info': {
            'name': 'Ancient Symbols',
            'interaction_type': 'searchable',
            'description': 'Strange symbols carved into weathered stone pillars.',
            'examine_dialogue': 'swamp_symbols_examine',  # Triggers dialogue
            'loot_table': None,  # No loot, just lore
            'flag_set': 'examined_swamp_symbols',
            'requirements': {},
            'one_time': True
        }
    },
    'outdoor_altar': {
        'search_tiles': [(9, 9), (10, 9), (9, 10), (10, 10)],  # Around altar
        'object_pos': [(9, 9), (10, 9)],  # Altar tiles
        'info': {
            'name': 'Weathered Altar',
            'interaction_type': 'searchable',
            'description': 'An ancient stone altar, cracked and stained.',
            'examine_dialogue': 'swamp_altar_examine',  # Dialogue with description
            'loot_table': 'swamp_altar_loot',  # Might find something
            'flag_set': 'searched_swamp_altar',
            'requirements': {},
            'one_time': True
        }
    },
    'disturbed_graves': {
        'search_tiles': [(8, 4), (9, 4), (10, 4), (11, 4)],  # Grave area
        'object_pos': [(9, 4), (10, 4), (11, 4)],  # Grave tiles
        'info': {
            'name': 'Disturbed Graves',
            'interaction_type': 'searchable',
            'description': 'Recently disturbed graves. Something has been digging here.',
            'examine_dialogue': 'grave_examination',  # Dialogue
            'loot_table': 'swamp_grave_loot',  # Find items
            'flag_set': 'searched_swamp_graves',
            'requirements': {},
            'one_time': True
        }
    }
}

def get_searchable_at_position(player_x, player_y):
    """Check if player is standing at a searchable object"""
    for search_id, search_data in SEARCHABLE_OBJECTS.items():
        if (player_x, player_y) in search_data['search_tiles']:
            return search_data['info']
    return None

# Combat triggers (random encounters)
COMBAT_TRIGGERS = {
    (8, 11): {  # Random combat zone tile
        'encounter_id': 'swamp_skeleton',
        'trigger_type': 'step_on',
        'repeatable': True,  # Can re-encounter
        'chance': 0.30,  # 30% chance when stepping on tile
        'flag_check': None,
        'flag_set': None  # Doesn't set flag (repeatable)
    },
    (9, 11): {  # Another random combat tile
        'encounter_id': 'swamp_skeleton',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.30,
        'flag_check': None,
        'flag_set': None
    },
    (8, 12): {  # Ghost encounter zone
        'encounter_id': 'swamp_ghost',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.25,  # 25% chance
        'flag_check': None,
        'flag_set': None
    },
    (9, 12): {  # Another ghost tile
        'encounter_id': 'swamp_ghost',
        'trigger_type': 'step_on',
        'repeatable': True,
        'chance': 0.25,
        'flag_check': None,
        'flag_set': None
    }
}

def get_combat_trigger(player_x, player_y):
    """Check if player stepped on combat trigger tile"""
    return COMBAT_TRIGGERS.get((player_x, player_y), None)

# NPCs in this area (optional)
LOCATION_NPCS = {}  # No NPCs in exterior for now

def get_location_npcs():
    """Return NPC definitions for this location"""
    return LOCATION_NPCS
```

#### Step 2: Create Navigation Screen

**New File:** `screens/swamp_church_exterior_nav.py`

```python
"""
Swamp Church Exterior Navigation
Scrollable tile-based exploration screen
"""

import pygame
import random
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, LAYOUT_DIALOG_Y, LAYOUT_DIALOG_HEIGHT
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from utils.tile_graphics import get_tile_graphics_manager
from utils.narrative_schema import narrative_schema
from data.maps.swamp_church_exterior_map import *

class SwampChurchExteriorNav:
    """Navigation screen for swamp church exterior exploration"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        config = {
            'map_width': SWAMP_CHURCH_EXT_WIDTH,
            'map_height': SWAMP_CHURCH_EXT_HEIGHT,
            'location_id': 'swamp_church_exterior',
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_tile_color': get_tile_color,
                'get_building_info': get_transition_at_entrance,
                'get_searchable_info': get_searchable_at_position,
                'get_combat_trigger': get_combat_trigger
            }
        }
        
        self.renderer = NavigationRenderer(config)
        self.current_transition = None
        self.current_searchable = None
        self.showing_message = False
        self.message_text = ""
        self.message_timer = 0
        
        self.graphics_manager = get_tile_graphics_manager()
    
    def update_player_position(self, game_state):
        """Initialize or restore player position"""
        if not hasattr(game_state, 'swamp_church_ext_x'):
            game_state.swamp_church_ext_x = SWAMP_CHURCH_EXT_SPAWN_X
            game_state.swamp_church_ext_y = SWAMP_CHURCH_EXT_SPAWN_Y
        
        self.renderer.update_camera(
            game_state.swamp_church_ext_x, 
            game_state.swamp_church_ext_y
        )
    
    def update(self, dt, keys, game_state, controller=None):
        """Update navigation state and handle interactions"""
        self.update_player_position(game_state)
        
        # Handle movement
        old_x = game_state.swamp_church_ext_x
        old_y = game_state.swamp_church_ext_y
        
        new_x, new_y = self.renderer.handle_movement(keys, old_x, old_y)
        
        # Check if player moved to new tile
        if new_x != old_x or new_y != old_y:
            
            # PRIORITY 1: Check for combat trigger on new tile
            combat_trigger = self.renderer.check_combat_trigger(new_x, new_y)
            if combat_trigger and combat_trigger.get('repeatable'):
                # Random encounter - check chance
                chance = combat_trigger.get('chance', 1.0)
                if random.random() < chance:
                    # Trigger combat!
                    if controller:
                        controller.event_manager.emit_event({
                            'type': 'START_COMBAT',
                            'encounter_id': combat_trigger['encounter_id'],
                            'return_screen': 'swamp_church_exterior_nav'
                        })
                    return  # Don't move yet, combat starting
            
            # No combat (or failed chance roll), update position
            game_state.swamp_church_ext_x = new_x
            game_state.swamp_church_ext_y = new_y
            self.renderer.update_camera(new_x, new_y)
        
        # Check for ENTER key interactions (higher priority when standing still)
        if keys[pygame.K_RETURN] and not self.showing_message:
            player_x = game_state.swamp_church_ext_x
            player_y = game_state.swamp_church_ext_y
            
            # INTERACTION PRIORITY ORDER:
            
            # Priority 1: Area transitions (doors, exits)
            transition_info = self.renderer.check_valid_entrance(player_x, player_y, 
                                                                 self.renderer.player_direction)
            if transition_info and transition_info[0]:
                # Navigate to new area/screen
                if controller:
                    target = transition_info[0]['target_screen']
                    controller.transition_to(target)
                return
            
            # Priority 2: Searchable objects (examine, loot)
            searchable_info = self.renderer.check_searchable_object(player_x, player_y)
            if searchable_info:
                # Check if already searched
                flag_set = searchable_info.get('flag_set')
                if flag_set and narrative_schema.get_flag(game_state, flag_set):
                    self.show_temp_message("You've already searched here.")
                else:
                    # Trigger examination
                    examine_dialogue = searchable_info.get('examine_dialogue')
                    if examine_dialogue and controller:
                        # Start dialogue for this searchable
                        controller.start_dialogue(
                            examine_dialogue,
                            return_screen='swamp_church_exterior_nav'
                        )
                    
                    # Handle loot if any
                    loot_table = searchable_info.get('loot_table')
                    if loot_table:
                        # TODO: Implement loot system
                        # For now, just show message
                        self.show_temp_message("You found items! (Loot system TODO)")
                    
                    # Set flag to prevent re-searching
                    if flag_set:
                        narrative_schema.set_flag(game_state, flag_set, True)
                
                return
            
            # Priority 3: NPCs (if any in this area)
            # TODO: Implement NPC interaction check (like town system)
        
        # Update temp message timer
        if self.showing_message:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.showing_message = False
    
    def show_temp_message(self, text):
        """Display temporary message to player"""
        self.showing_message = True
        self.message_text = text
        self.message_timer = 2000  # 2 seconds
    
    def render(self, surface, fonts, images, game_state):
        """Render the exterior navigation screen"""
        surface.fill(BLACK)
        
        # Get player position for rendering
        player_x = game_state.swamp_church_ext_x
        player_y = game_state.swamp_church_ext_y
        
        # Draw map tiles
        self.renderer.draw_map(surface, fonts, player_x, player_y)
        
        # Draw player sprite
        self.renderer.draw_player(surface, player_x, player_y)
        
        # Draw NPCs (if any)
        # TODO: NPC rendering
        
        # Draw party status panel (right side)
        draw_party_status_panel(surface, game_state, fonts, images)
        
        # Draw location title at top
        title_text = "CHURCH IN THE SWAMP - EXTERIOR"
        draw_centered_text(surface, title_text, fonts['fantasy_medium'], 
                          YELLOW, 440, 20)
        
        # Draw dialog/interaction area at bottom
        dialog_rect = pygame.Rect(5, LAYOUT_DIALOG_Y, 876, LAYOUT_DIALOG_HEIGHT)
        draw_border(surface, dialog_rect, WHITE, 3)
        
        # Draw interaction prompts
        transition = self.renderer.check_valid_entrance(player_x, player_y, 
                                                        self.renderer.player_direction)
        if transition and transition[0]:
            prompt = f"Press ENTER to {transition[0]['action']}"
            draw_centered_text(surface, prompt, fonts['medieval_small'],
                             YELLOW, 440, LAYOUT_DIALOG_Y + 15)
        
        searchable = self.renderer.check_searchable_object(player_x, player_y)
        if searchable:
            # Check if already searched
            flag_set = searchable.get('flag_set')
            if flag_set and narrative_schema.get_flag(game_state, flag_set):
                prompt = f"{searchable['name']} (already searched)"
                draw_centered_text(surface, prompt, fonts['medieval_small'],
                                 WHITE, 440, LAYOUT_DIALOG_Y + 15)
            else:
                prompt = f"Press ENTER to examine {searchable['name']}"
                draw_centered_text(surface, prompt, fonts['medieval_small'],
                                 YELLOW, 440, LAYOUT_DIALOG_Y + 15)
        
        # Show temp message if any
        if self.showing_message:
            draw_centered_text(surface, self.message_text, 
                             fonts['medieval_medium'], WHITE, 440, LAYOUT_DIALOG_Y + 50)
        
        # Draw debug info (optional, can be toggled)
        if hasattr(game_state, 'show_debug') and game_state.show_debug:
            debug_text = f"Pos: ({player_x}, {player_y}) Facing: {self.renderer.player_direction}"
            draw_centered_text(surface, debug_text, fonts['medieval_small'],
                             WHITE, 440, 40)


# ScreenManager registration functions
def draw_swamp_church_exterior_nav(surface, game_state, fonts, images, manager=None):
    """Render function for ScreenManager"""
    if not hasattr(manager, 'swamp_church_exterior_nav_instance'):
        manager.swamp_church_exterior_nav_instance = SwampChurchExteriorNav()
    manager.swamp_church_exterior_nav_instance.render(surface, fonts, images, game_state)

def update_swamp_church_exterior_nav(dt, keys, game_state, controller):
    """Update function for ScreenManager"""
    if hasattr(controller.screen_manager, 'swamp_church_exterior_nav_instance'):
        controller.screen_manager.swamp_church_exterior_nav_instance.update(
            dt, keys, game_state, controller
        )
```

#### Step 3: Create Examine Dialogues

**New File:** `data/dialogues/swamp_searchables.json`

```json
{
  "swamp_symbols_examine": {
    "root": {
      "speaker": "Narrator",
      "text": "The stone pillars are covered in strange symbols - twisted runes that seem to shift when you're not looking directly at them. You recognize some as ancient protective wards, but they've been defaced and corrupted.",
      "choices": [
        {
          "text": "Continue",
          "next": "end",
          "effects": []
        }
      ]
    }
  },
  
  "swamp_altar_examine": {
    "root": {
      "speaker": "Narrator",
      "text": "The weathered stone altar bears signs of recent use. Dark stains mar its surface, and the smell of burnt offerings lingers. Fresh candle wax drips down the sides - someone was here recently.",
      "choices": [
        {
          "text": "Search the altar",
          "next": "search",
          "effects": []
        },
        {
          "text": "Leave it alone",
          "next": "end",
          "effects": []
        }
      ]
    },
    "search": {
      "speaker": "Narrator",
      "text": "Behind the altar, you find a small hidden compartment. Inside is a tarnished silver amulet and a scrap of parchment with hastily scrawled notes.",
      "choices": [
        {
          "text": "Take the items",
          "next": "end",
          "effects": [
            {"type": "give_item", "item_id": "strange_amulet", "quantity": 1},
            {"type": "give_item", "item_id": "cult_note", "quantity": 1}
          ]
        }
      ]
    }
  },
  
  "grave_examination": {
    "root": {
      "speaker": "Narrator",
      "text": "The graves have been recently disturbed - earth scattered, headstones toppled. Whatever dug here was searching for something... or someone.",
      "choices": [
        {
          "text": "Search the disturbed earth",
          "next": "search",
          "effects": []
        },
        {
          "text": "Leave the graves be",
          "next": "end",
          "effects": []
        }
      ]
    },
    "search": {
      "speaker": "Narrator",
      "text": "Sifting through the dirt, you find a few silver coins and a broken holy symbol. More troubling, you see drag marks leading toward the church...",
      "choices": [
        {
          "text": "Take what you found",
          "next": "end",
          "effects": [
            {"type": "give_item", "item_id": "silver_coins", "quantity": 5},
            {"type": "give_item", "item_id": "broken_holy_symbol", "quantity": 1},
            {"type": "set_flag", "flag": "found_grave_drag_marks", "value": true}
          ]
        }
      ]
    }
  }
}
```

#### Step 4: Register with ScreenManager

**File to Modify:** `ui/screen_manager.py`

```python
# Import the new screen
from screens.swamp_church_exterior_nav import (
    draw_swamp_church_exterior_nav,
    update_swamp_church_exterior_nav
)

# In _register_location_screens() or similar method:
self.register_screen(
    'swamp_church_exterior_nav',
    draw_swamp_church_exterior_nav,
    update_hook=update_swamp_church_exterior_nav
)
```

#### Step 5: Update Regional Map

**File to Modify:** `screens/exploration_hub.py` (or wherever regional map clicking is handled)

Change the swamp church click target:

```python
# OLD: Navigate to ActionHub screen
# target = 'swamp_church.exterior'

# NEW: Navigate to scrollable nav screen
target = 'swamp_church_exterior_nav'
```

#### Success Criteria for 11.5B
- ✅ Can walk around church exterior freely
- ✅ Can examine ancient symbols (triggers dialogue)
- ✅ Can examine altar (triggers dialogue + loot)
- ✅ Can search graves (triggers dialogue + loot)
- ✅ Random skeleton/ghost encounters trigger sometimes when stepping on combat tiles
- ✅ Can enter church door (transitions to interior)
- ✅ Can return to regional map
- ✅ All flags set correctly (one-time searches work)
- ✅ Temp messages show for already-searched locations

---

### Phase 11.5C: Swamp Church Interior (Second Exploration Area)
**Duration:** 2-3 hours  
**Goal:** Create interior scrollable map, repeat template pattern

#### Tasks
1. Create `data/maps/swamp_church_interior_map.py`
   - 20x20 layout with church interior design
   - Pew tiles (searchable)
   - Altar tile (searchable)
   - Stairs down tile (transition to crypt)
   - Optional: NPC (cultist guard?)
   
2. Create `screens/swamp_church_interior_nav.py`
   - Copy/modify exterior navigation screen
   - Update map imports and position variables
   - Same interaction handling logic
   
3. Create examine dialogues for interior searchables
   - `church_pews_examine`
   - `church_altar_examine`
   
4. Register interior nav screen with ScreenManager

5. Update exterior door transition to point to interior nav screen

6. Update crypt ActionHub button to return to interior nav screen

#### Interior Map Example (Simplified)

```python
SWAMP_CHURCH_INT_MAP = [
    "####################",
    "###################D",  # D = door back to exterior
    "##.................#",
    "##.pppppppppppppp..#",  # p = pews (searchable)
    "##.pppppppppppppp..#",
    "##.................#",
    "##.pppppppppppppp..#",
    "##.pppppppppppppp..#",
    "##.................#",
    "##.......AA........#",  # AA = altar (searchable)
    "##.......AA........#",
    "##.................#",
    "##.........[.......#",  # [ = stairs down (transition to crypt)
    "##.................#",
    "##.................#",
    "##.................#",
    "##.................#",
    "##.................#",
    "###################@",  # @ = spawn (from exterior)
    "####################"
]
```

#### Success Criteria for 11.5C
- ✅ Can walk around church interior
- ✅ Can search pews (loot check)
- ✅ Can examine altar (dialogue)
- ✅ Can descend to crypt (navigate to crypt ActionHub screen - EXISTING)
- ✅ Can return to exterior
- ✅ Interior feels like continuation of exterior exploration

---

### Phase 11.5D: Connect to Existing Crypt Screen
**Duration:** 30-60 minutes  
**Goal:** Link new scrollable areas to existing ActionHub crypt screen

#### Tasks

1. **Update Interior Stairs Transition**

In `swamp_church_interior_map.py`, stairs transition should navigate to existing crypt ActionHub:

```python
AREA_TRANSITIONS = {
    'stairs_to_crypt': {
        'entrance_tiles': [(10, 12)],  # Stairs tile
        'building_pos': [(10, 12)],
        'info': {
            'name': 'Descend to Crypt',
            'interaction_type': 'navigation',
            'target_screen': 'swamp_church.crypt',  # Existing ActionHub screen
            'action': 'Descend into the Crypt',
            'requirements': {}
        }
    }
}
```

2. **Update Crypt ActionHub Return Button**

In existing `data/locations/swamp_church.json`, update crypt return action:

```json
"crypt": {
  "type": "action_hub",
  "title": "SWAMP CHURCH CRYPT",
  "description": "Ancient stone steps, flickering candles, ritual circle...",
  "actions": {
    "search_crypt": {
      "type": "loot_check",
      "label": "Search the Crypt",
      "loot_table": "swamp_church_crypt"
    },
    "investigate_ritual": {
      "type": "dialogue",
      "label": "Investigate Ritual Site",
      "npc_id": "ritual_site"
    },
    "confront_cultists": {
      "type": "combat",
      "label": "Confront the Cultists",
      "combat_encounter": "swamp_cultists",
      "requires_flag": "investigated_ritual_site"
    },
    "return_upstairs": {
      "type": "navigate",
      "label": "Return Upstairs",
      "target": "swamp_church_interior_nav"  ← CHANGED from "swamp_church.interior"
    }
  }
}
```

#### Success Criteria
- ✅ Complete flow: Regional Map → Exterior Nav → Interior Nav → Crypt ActionHub
- ✅ Return navigation works at every step
- ✅ No broken transitions
- ✅ Hybrid system validated (scrollable exploration + button confrontation)

---

## 📋 COMPLETE SWAMP CHURCH CONVERSION CHECKLIST

### Files to Create
- [ ] `data/maps/swamp_church_exterior_map.py` - Exterior tile map
- [ ] `screens/swamp_church_exterior_nav.py` - Exterior navigation screen
- [ ] `data/maps/swamp_church_interior_map.py` - Interior tile map
- [ ] `screens/swamp_church_interior_nav.py` - Interior navigation screen
- [ ] `data/dialogues/swamp_searchables.json` - Examine dialogues

### Files to Modify
- [ ] `ui/base_location_navigation.py` - Add searchable/combat methods
- [ ] `ui/screen_manager.py` - Register new nav screens
- [ ] `screens/exploration_hub.py` - Update church click target
- [ ] `data/locations/swamp_church.json` - Update crypt return target

### Testing Checklist
- [ ] Exterior exploration works (walk around, examine, combat)
- [ ] Interior exploration works (walk around, search, examine)
- [ ] All transitions work (regional → ext → int → crypt → back)
- [ ] Searchables trigger dialogues correctly
- [ ] Loot system works (when implemented)
- [ ] Combat triggers work (random encounters)
- [ ] One-time searches enforced (flags work)
- [ ] Temp messages show correctly
- [ ] Save/load preserves position in each area
- [ ] No crashes or errors

---

## 🎯 TEMPLATE FOR FUTURE LOCATIONS

Once swamp church is complete, use it as template for:

### Hill Ruins
- **Exterior:** 20x20 map, examine ruins tile, climb up entrance
- **Ground Level:** 20x20 map, portal chamber tile, stairs down
- **Dungeon:** ActionHub (locked door puzzle, boss encounter)

### Refugee Camp
- **Main Camp:** 20x20 map, talk to refugees, search tents, brigands approach
- **Defense:** ActionHub or scrollable combat map? (TBD)

### Red Hollow Mine
- **Entrance:** 20x20 map, examine collapse, kobold encounters, descend
- **Deeper Shafts:** 20x20 map, aethel ore deposits, Meredith's ring, Henrik's lantern

---

## ⚠️ IMPORTANT IMPLEMENTATION NOTES

### SearchableObjects + Loot System Integration
- Searchable info includes `loot_table` ID
- Need to implement actual loot distribution when searched
- Consider perception skill affecting loot quality
- Key quest items always findable (100% chance)

### Combat Trigger + Chance System
- Random encounters use `chance` field (0.0 to 1.0)
- Use `random.random() < chance` to determine if combat triggers
- Repeatable encounters don't set flags
- Story encounters set flags to prevent re-trigger

### Dialogue Integration
- Searchables can trigger dialogue screens
- Use existing dialogue system and JSON format
- Return screen should be the navigation screen (not exploration hub)
- Dialogue effects can give items, set flags, start quests

### Visual Highlights for Searchables
- Searchable tiles use distinct colors in `get_tile_color()`
- Slightly lighter or different hue than surrounding tiles
- Not too obvious (discovery should feel rewarding)
- Consistent color scheme across all locations

### Flag Management
- Each searchable sets a flag when examined (`examined_X` or `searched_X`)
- Check flag before allowing re-search
- Show different prompt for already-searched locations
- Flags persist through save/load

---

## 📝 SUMMARY: HYBRID SYSTEM BENEFITS

**Scrollable Exploration Areas (Exterior/Interior):**
- ✅ Player agency and freedom
- ✅ Discovery feels organic
- ✅ Hidden secrets reward exploration
- ✅ Random encounters add danger
- ✅ Classic dungeon-crawling feel
- ✅ Immersive atmosphere

**Button-Based Encounter Areas (Crypt/Boss Rooms):**
- ✅ Dramatic pacing for climactic moments
- ✅ Clear tactical choices
- ✅ Focused storytelling
- ✅ Less overwhelming for complex encounters
- ✅ Easier to implement complex combat setup
- ✅ Players can prepare mentally for big fight

**Result:** Best of both worlds - exploration when it makes sense, focus when drama requires it!

---

## 🚀 READY FOR IMPLEMENTATION

This Phase 11.5 v2.0 plan provides:
- ✅ Complete clarification of hybrid approach
- ✅ Detailed searchable object system
- ✅ Combat trigger specifications (random vs story)
- ✅ Full code examples for all new systems
- ✅ Step-by-step implementation roadmap
- ✅ Template for future location creation
- ✅ Testing criteria and success metrics

**Next Steps:**
1. Review and approve this plan
2. Create ADR if desired (recommended)
3. Begin Phase 11.5A (extend NavigationRenderer)
4. Proceed through 11.5B, C, D sequentially

**Estimated Total Time:** 6-9 hours for complete swamp church conversion

---

**Document End**

*Time to turn these foggy marshlands into an explorable dungeon! Let's bring that classic RPG feel to Act II! 🏰⚔️👻*
