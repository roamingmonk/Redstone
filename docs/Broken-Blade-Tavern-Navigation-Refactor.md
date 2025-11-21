# Broken Blade Tavern Navigation Refactor
## Implementation Plan v1.0
**Session Goal:** Convert Broken Blade from static ActionHub to scrollable tile-based navigation  
**Estimated Duration:** 6-8 hours (split across 2-3 sessions recommended)  
**Risk Level:** HIGH (core game starting point - requires careful testing)  
**Pattern Source:** Proven navigation architecture from Swamp Church, Hill Ruins, Redstone Town

---

## 📋 TABLE OF CONTENTS
1. [Overview & Goals](#overview--goals)
2. [Current State Analysis](#current-state-analysis)
3. [Architectural Approach](#architectural-approach)
4. [Tavern Layout Design](#tavern-layout-design)
5. [Complete File Manifest](#complete-file-manifest)
6. [Implementation Phases](#implementation-phases)
7. [Testing Strategy](#testing-strategy)
8. [Risk Mitigation](#risk-mitigation)
9. [Rollback Plan](#rollback-plan)

---

## 🎯 OVERVIEW & GOALS

### What We're Building
Convert the Broken Blade tavern from a static button-based ActionHub screen into a scrollable tile-based navigation system where players walk around to interact with NPCs, similar to the Swamp Church and Hill Ruins exploration screens.

### Success Criteria
✅ Player can walk around tavern interior using arrow keys  
✅ NPCs are positioned at fixed locations (bar, tables, corners)  
✅ Player walks to NPC and presses ENTER to initiate dialogue  
✅ Dice game accessible via dedicated tile/area  
✅ Basement accessible via stairs tile (conditional on quest flag)  
✅ Exit tile returns player to Redstone Town  
✅ ALL existing functionality preserved (recruitment, shopping, quests, gambling)  
✅ Recruited NPCs disappear from tavern  
✅ Mayor disappears from tavern in Act II (moves to office)  
✅ Save/load correctly restores player position in tavern  

### Why This Matters
- **Consistency:** All other locations use tile navigation - tavern should too
- **Immersion:** Walking around creates better RPG experience than clicking buttons
- **Scalability:** Easier to add new NPCs or features to tavern in future
- **Learning:** Establishes the pattern for any future interior locations

---

## 🔍 CURRENT STATE ANALYSIS

### Existing Files & Systems

#### 1. ActionHub Configuration
**File:** `data/locations/broken_blade.json`
```json
{
  "broken_blade": {
    "location_id": "broken_blade",
    "name": "The Broken Blade Tavern",
    "type": "action_hub",
    "areas": {
      "main": {
        "type": "action_hub",
        "actions": {
          "talk_patrons": { "type": "navigate", "target": "patron_selection" },
          "gamble": { "type": "navigate", "target": "dice_bets" },
          "bartender": { "type": "dialogue", "npc_id": "garrick" },
          "server": { "type": "dialogue", "npc_id": "meredith" },
          "basement": { "type": "combat", "requirements": {...} },
          "leave": { "type": "navigate", "target": "redstone_town" }
        }
      }
    }
  }
}
```

#### 2. Screen Registration
**File:** `ui/screen_manager.py`
```python
# Current registration (auto-registered as BaseLocation)
self._auto_register_location("broken_blade")
self._auto_register_location("patron_selection")
```

#### 3. NPCs Involved
- **Garrick** (bartender) - dialogue, shopping, basement quest giver
- **Meredith** (server) - dialogue, shopping
- **Mayor** (Act I only) - dialogue, quest giver, moves to office in Act II
- **Gareth** (recruitable warrior) - dialogue, recruitment
- **Elara** (recruitable mage) - dialogue, recruitment
- **Thorman** (recruitable dwarf) - dialogue, recruitment  
- **Lyra** (recruitable rogue) - dialogue, recruitment
- **Pete** (informant) - dialogue, refugee camp information

#### 4. Connected Systems
- **Gambling:** `screens/dice_bets.py` - accessed via "gamble" action
- **Basement Combat:** Triggered by "basement" action with flag requirements
- **Recruitment:** Via patron_selection screen, syncs to `game_state.party_members`
- **Shopping:** Triggered through NPC dialogues (Garrick/Meredith)
- **Town Navigation:** Entry from `redstone_town` map, exit returns there

#### 5. Flag Dependencies
- `accepted_basement_quest` - Shows basement action
- `completed_basement_combat` - Changes basement to cleared state
- `mayor_talked` - Enables recruitment system
- `gareth_recruited`, `elara_recruited`, etc. - Hides recruited NPCs
- `act_two_started` - Mayor no longer in tavern

---

## 🏗️ ARCHITECTURAL APPROACH

### Pattern to Follow
We'll use the **proven navigation pattern** established in:
- `screens/swamp_church_exterior_nav.py`
- `screens/hill_ruins_entrance_nav.py`
- `screens/redstone_town_navigation.py`

### Key Components

#### 1. Navigation Renderer
**Utility:** `ui/base_location_navigation.py`  
**Purpose:** Handles camera, rendering, movement logic  
**Status:** Already exists, proven working

#### 2. Map Data File
**New File:** `data/maps/broken_blade_map.py`  
**Purpose:** Define tavern layout, tile types, NPC positions, interaction points  
**Pattern:** ASCII string-based map like other locations

#### 3. Navigation Screen
**New File:** `screens/broken_blade_nav.py`  
**Purpose:** Main screen handler for tavern navigation  
**Pattern:** Copy/modify from swamp_church_exterior_nav.py

#### 4. NPC Management System
**Enhancement:** Dynamic NPC visibility based on:
- Recruitment status (recruited NPCs don't show)
- Act progression (Mayor disappears in Act II)
- Quest state (conditional NPCs if needed)

### Integration Points

#### Entry Point
**From:** `redstone_town` navigation map  
**Trigger:** Walk to tavern entrance tile, press ENTER  
**Target:** `broken_blade_nav` (new navigation screen)

#### Exit Point  
**From:** Exit tile in tavern map  
**Trigger:** Walk to door tile, press ENTER  
**Target:** `redstone_town` (return to town)

#### NPC Interactions
**Trigger:** Walk adjacent to NPC, press ENTER  
**Action:** Launch dialogue screen (existing system)  
**Return:** Back to tavern navigation screen

#### Gambling Access
**Trigger:** Walk to dice game area tile, press ENTER  
**Target:** `dice_bets` screen (existing system)  
**Return:** Back to tavern navigation screen

#### Basement Access
**Trigger:** Walk to stairs tile, press ENTER (if quest accepted)  
**Target:** `combat` screen with basement encounter  
**Return:** Back to tavern navigation screen (or cleared basement)

---

## 🗺️ TAVERN LAYOUT DESIGN

### Map Specifications
- **Size:** 20x20 tiles (standard for interior navigation)
- **Tile Size:** 64x64 pixels
- **Visible Window:** 13x7 tiles (832x448 pixels)
- **Camera:** Scrolling, player-centered

### ASCII Map Layout

```
BROKEN BLADE TAVERN - 20x20 INTERIOR MAP

Legend:
# = Walls (impassable)
. = Floor (walkable)
B = Bar counter (not walkable, Garrick behind it)
T = Tables (walkable, NPC interaction points)
C = Chairs (walkable)
D = Door (exit to town)
S = Stairs (basement entrance - conditional)
G = Dice game area (gamble trigger)
M = Mayor's table (Act I only)
@ = Player spawn point (entering from town)

####################
#S.................#
#..................#
#...BBBBBBBBB......#
#...B.......B......#
#...B.......B......#
#..................#
#..TTT......TTT...M#
#..CCC......CCC...M#
#..................#
#......GGG.........#
#......GGG.........#
#..................#
#..................#
#..................#
#..................#
#..TTT....TTT..TTT.#
#..CCC....CCC..CCC.#
#........@D........#
####################

NPC Positions:
- Garrick: Behind bar (row 4, col 9)
- Meredith: Near tables (row 8, col 5) - roaming server
- Mayor: Upper right corner table (row 7, col 18) - ACT I ONLY
- Gareth: Upper table left (row 7, col 4)
- Elara: Upper table center (row 7, col 9)
- Thorman: Lower table left (row 16, col 4)
- Lyra: Lower table center (row 16, col 9)
- Pete: Lower table right (row 16, col 14) - refugee camp info
- Dice Game: Center area (row 10-11, col 7-9)
- Basement Stairs: Upper left corner (row 1, col 1) - CONDITIONAL
- Exit Door: South center (row 18, col 9-10)
```

### Tile Type Definitions

```python
TILE_TYPES = {
    '#': 'wall',           # Impassable walls
    '.': 'floor',          # Walkable floor
    'B': 'bar_counter',    # Bar (not walkable, NPC behind)
    'T': 'table',          # Tables (walkable)
    'C': 'chair',          # Chairs (walkable)
    'D': 'door',           # Exit door (transition tile)
    'S': 'stairs',         # Basement stairs (conditional transition)
    'G': 'gamble_area',    # Dice game zone
    'M': 'mayor_table',    # Mayor's special table
    '@': 'spawn_point',    # Player entry point
}

WALKABLE_TILES = {'floor', 'table', 'chair', 'gamble_area', 'mayor_table', 'spawn_point'}
```

### NPC Interaction Tiles

NPCs will have defined interaction zones (tiles where player can stand and press ENTER):

```python
TAVERN_NPCS = {
    'garrick': {
        'sprite_type': 'bartender',
        'position': (9, 3),  # Behind bar
        'interaction_tiles': [(8, 3), (10, 3), (8, 4), (9, 4), (10, 4)],  # In front of bar
        'dialogue_id': 'garrick',
        'conditions': None  # Always present
    },
    'meredith': {
        'sprite_type': 'server',
        'position': (5, 7),  # Near tables
        'interaction_tiles': [(4, 7), (6, 7), (5, 6), (5, 8)],  # Adjacent tiles
        'dialogue_id': 'meredith',
        'conditions': None  # Always present
    },
    'mayor': {
        'sprite_type': 'noble',
        'position': (18, 6),  # Corner table
        'interaction_tiles': [(17, 6), (18, 7)],
        'dialogue_id': 'mayor',
        'conditions': {'act_check': 1}  # Act I only
    },
    'gareth': {
        'sprite_type': 'warrior',
        'position': (4, 6),  # Table
        'interaction_tiles': [(3, 6), (5, 6), (4, 5), (4, 7)],
        'dialogue_id': 'gareth',
        'conditions': {'not_recruited': 'gareth_recruited'}
    },
    'elara': {
        'sprite_type': 'mage',
        'position': (9, 6),  # Table
        'interaction_tiles': [(8, 6), (10, 6), (9, 5), (9, 7)],
        'dialogue_id': 'elara',
        'conditions': {'not_recruited': 'elara_recruited'}
    },
    'thorman': {
        'sprite_type': 'dwarf',
        'position': (4, 9),  # Table
        'interaction_tiles': [(3, 9), (5, 9), (4, 8), (4, 10)],
        'dialogue_id': 'thorman',
        'conditions': {'not_recruited': 'thorman_recruited'}
    },
    'lyra': {
        'sprite_type': 'rogue',
        'position': (9, 9),  # Table
        'interaction_tiles': [(8, 9), (10, 9), (9, 8), (9, 10)],
        'dialogue_id': 'lyra',
        'conditions': {'not_recruited': 'lyra_recruited'}
    }
}
```

### Special Interaction Zones

```python
# Area transitions (navigation between screens)
AREA_TRANSITIONS = {
    'exit_door': {
        'entrance_tiles': [(9, 18), (10, 18)],  # Standing in front of door
        'building_pos': [(9, 18), (10, 18)],
        'info': {
            'name': 'Tavern Exit',
            'interaction_type': 'navigation',
            'target_screen': 'redstone_town',
            'action': 'Leave Tavern',
            'requirements': {}
        }
    },
    'basement_stairs': {
        'entrance_tiles': [(11, 16)],  # Standing at stairs
        'building_pos': [(11, 16)],
        'info': {
            'name': 'Basement Stairs',
            'interaction_type': 'combat',
            'target_screen': 'combat',
            'combat_encounter': 'tavern_basement_rats',
            'action': 'Descend to Basement',
            'requirements': {
                'flags': {
                    'accepted_basement_quest': True,
                    'completed_basement_combat': False
                }
            }
        }
    },
    'basement_cleared': {
        'entrance_tiles': [(11, 16)],
        'building_pos': [(11, 16)],
        'info': {
            'name': 'Basement',
            'interaction_type': 'navigation',
            'target_screen': 'broken_blade_basement_cleared',
            'action': 'Visit Basement',
            'requirements': {
                'flags': {
                    'completed_basement_combat': True
                }
            }
        }
    }
}

# Special interactive areas
SPECIAL_AREAS = {
    'dice_game': {
        'trigger_tiles': [(7, 12), (8, 12), (9, 12), (7, 13), (8, 13), (9, 13)],
        'info': {
            'name': 'Dice Game',
            'interaction_type': 'navigation',
            'target_screen': 'dice_bets',
            'action': 'Play Redstone Dice',
            'requirements': {}
        }
    }
}
```

---

## 📁 COMPLETE FILE MANIFEST

### Files to CREATE

1. **`data/maps/broken_blade_map.py`**
   - Tavern map layout (20x20 ASCII)
   - Tile type definitions
   - NPC positions and interaction zones
   - Area transitions (door, stairs, dice game)
   - Helper functions (get_tile_type, is_walkable, get_npc_at_position, etc.)

2. **`screens/broken_blade_nav.py`**
   - Navigation screen class
   - Render function
   - Update function
   - NPC visibility logic
   - Event handling

### Files to MODIFY

1. **`ui/screen_manager.py`**
   - Replace `_auto_register_location("broken_blade")` with custom registration
   - Register new `broken_blade_nav` screen with proper hooks
   - Keep `patron_selection` registration (deprecate later if needed)

2. **`data/maps/redstone_town_map.py`** (if needed)
   - Verify tavern entrance transition points to `broken_blade_nav`
   - Should already work, but double-check

3. **`game_logic/game_state.py`** (if needed)
   - Add `tavern_position` tracking (x, y coordinates)
   - Should already exist from town navigation, extend pattern

### Files to DEPRECATE (Keep for now, remove later)

1. **`data/locations/broken_blade.json`**
   - Keep for reference during migration
   - May still be used by basement_cleared area
   - Can delete after full migration

2. **`screens/patron_selection.py`** (if exists)
   - May not be needed if NPCs are on main map
   - Keep for now as fallback

### Files UNCHANGED (Reference Only)

1. **`screens/dice_bets.py`** - Gambling system (still called from map)
2. **`data/dialogues/broken_blade_*.json`** - All NPC dialogues
3. **`game_logic/dialogue_engine.py`** - Dialogue system
4. **`ui/base_location_navigation.py`** - Navigation renderer (already exists)

---

## 🚀 IMPLEMENTATION PHASES

### PHASE 0: Preparation & Backup (30 minutes)

#### Step 0.1: Create Feature Branch
```bash
git checkout -b feature/broken-blade-navigation-refactor
git add .
git commit -m "Checkpoint: Before Broken Blade refactor"
```

#### Step 0.2: Document Current Behavior
1. Launch game
2. Play through tavern interactions:
   - Talk to Garrick
   - Talk to Meredith
   - Talk to Mayor
   - Recruit Gareth
   - Play dice game
   - Accept basement quest (if implemented)
3. Take screenshots/notes of current behavior
4. Test save/load in tavern

#### Step 0.3: Identify All Entry Points
Search codebase for references to `"broken_blade"`:
```bash
grep -r "broken_blade" --include="*.py" --include="*.json"
```
Document every place that navigates to the tavern.

---

### PHASE 1: Create Map Data (1-2 hours)

#### Step 1.1: Create `data/maps/broken_blade_map.py`

**Full file contents:**

```python
# data/maps/broken_blade_map.py
"""
Broken Blade Tavern Interior Map
20x20 tile layout for navigation-based tavern exploration
"""

# === MAP CONSTANTS ===
BROKEN_BLADE_WIDTH = 20
BROKEN_BLADE_HEIGHT = 20
TILE_SIZE = 64

# Player spawn position (entering from town)
TAVERN_SPAWN_X = 9
TAVERN_SPAWN_Y = 18

# === TILE TYPE DEFINITIONS ===
TILE_TYPES = {
    '#': 'wall',           # Walls (impassable)
    '.': 'floor',          # Walkable floor
    'B': 'bar_counter',    # Bar counter (not walkable)
    'T': 'table',          # Tables (walkable)
    'C': 'chair',          # Chairs (walkable)
    'D': 'door',           # Exit door
    'S': 'stairs',         # Basement stairs
    'G': 'gamble_area',    # Dice game area
    'M': 'mayor_table',    # Mayor's table
    '@': 'spawn_point',    # Entry spawn
}

WALKABLE_TILES = {'floor', 'table', 'chair', 'gamble_area', 'mayor_table', 'spawn_point'}

# === ASCII MAP LAYOUT ===
BROKEN_BLADE_MAP = [
    "####################",  # Row 0
    "#S.................#",  # Row 1 - Stairs upper left
    "#..................#",  # Row 2
    "#...BBBBBBBBB......#",  # Row 3 - Bar starts
    "#...B.......B......#",  # Row 4 - Bar with back area
    "#...B.......B......#",  # Row 5
    "#..................#",  # Row 6
    "#..TTT......TTT...M#",  # Row 7 - First set of recruit tables + Mayor
    "#..CCC......CCC...M#",  # Row 8
    "#..................#",  # Row 9
    "#......GGG.........#",  # Row 10 - Dice game area
    "#......GGG.........#",  # Row 11
    "#..................#",  # Row 12
    "#..................#",  # Row 13
    "#..................#",  # Row 14
    "#..................#",  # Row 15
    "#..TTT....TTT..TTT.#",  # Row 16 - Second set of tables closer to door
    "#..CCC....CCC..CCC.#",  # Row 17
    "#........@D........#",  # Row 18 - Entry/exit
    "####################",  # Row 19
]

# === TILE HELPER FUNCTIONS ===
def get_tile_type(x, y):
    """Get tile type at coordinates"""
    if 0 <= y < BROKEN_BLADE_HEIGHT and 0 <= x < BROKEN_BLADE_WIDTH:
        char = BROKEN_BLADE_MAP[y][x]
        return TILE_TYPES.get(char, 'wall')
    return 'wall'

def is_walkable(x, y):
    """Check if tile is walkable"""
    tile_type = get_tile_type(x, y)
    return tile_type in WALKABLE_TILES

def get_tile_color(x, y):
    """Get color for tile rendering (placeholder - will use graphics later)"""
    tile_type = get_tile_type(x, y)
    TILE_COLORS = {
        'wall': (40, 20, 10),           # Dark wood walls
        'floor': (101, 67, 33),         # Brown wooden floor
        'bar_counter': (139, 69, 19),   # Saddle brown bar
        'table': (160, 82, 45),         # Sienna tables
        'chair': (139, 90, 43),         # Wood chairs
        'door': (101, 67, 33),          # Floor color (door tile)
        'stairs': (80, 50, 30),         # Darker wood stairs
        'gamble_area': (34, 139, 34),   # Green felt
        'mayor_table': (160, 82, 45),   # Same as table
        'spawn_point': (101, 67, 33),   # Floor color
    }
    return TILE_COLORS.get(tile_type, (128, 128, 128))

# === NPC DEFINITIONS ===
TAVERN_NPCS = {
    'garrick': {
        'sprite_type': 'bartender',
        'position': (9, 4),  # Behind bar
        'interaction_tiles': [(8, 4), (10, 4), (8, 5), (9, 5), (10, 5)],
        'display_name': 'Garrick',
        'dialogue_id': 'garrick',
        'conditions': None  # Always present
    },
    'meredith': {
        'sprite_type': 'server',
        'position': (5, 8),  # Near tables
        'interaction_tiles': [(4, 8), (6, 8), (5, 7), (5, 9)],
        'display_name': 'Meredith',
        'dialogue_id': 'meredith',
        'conditions': None  # Always present
    },
    'mayor': {
        'sprite_type': 'noble',
        'position': (18, 7),  # Upper right corner table
        'interaction_tiles': [(17, 7), (18, 8), (17, 8)],
        'display_name': 'Mayor Thorne',
        'dialogue_id': 'mayor',
        'conditions': {'act_check': 1}  # Act I only
    },
    'gareth': {
        'sprite_type': 'warrior',
        'position': (4, 7),  # Upper left table
        'interaction_tiles': [(3, 7), (5, 7), (4, 6), (4, 8)],
        'display_name': 'Gareth',
        'dialogue_id': 'gareth',
        'conditions': {'not_recruited': 'gareth_recruited'}
    },
    'elara': {
        'sprite_type': 'mage',
        'position': (9, 7),  # Upper center table
        'interaction_tiles': [(8, 7), (10, 7), (9, 6), (9, 8)],
        'display_name': 'Elara',
        'dialogue_id': 'elara',
        'conditions': {'not_recruited': 'elara_recruited'}
    },
    'thorman': {
        'sprite_type': 'dwarf',
        'position': (4, 16),  # Lower left table
        'interaction_tiles': [(3, 16), (5, 16), (4, 15), (4, 17)],
        'display_name': 'Thorman',
        'dialogue_id': 'thorman',
        'conditions': {'not_recruited': 'thorman_recruited'}
    },
    'lyra': {
        'sprite_type': 'rogue',
        'position': (9, 16),  # Lower center table
        'interaction_tiles': [(8, 16), (10, 16), (9, 15), (9, 17)],
        'display_name': 'Lyra',
        'dialogue_id': 'lyra',
        'conditions': {'not_recruited': 'lyra_recruited'}
    },
    'pete': {
        'sprite_type': 'commoner',
        'position': (14, 16),  # Lower right table
        'interaction_tiles': [(13, 16), (15, 16), (14, 15), (14, 17)],
        'display_name': 'Pete',
        'dialogue_id': 'pete',
        'conditions': None  # Always present
    }
}

def get_npc_at_position(x, y):
    """Get NPC at specific position"""
    for npc_id, npc_data in TAVERN_NPCS.items():
        if npc_data['position'] == (x, y):
            return npc_id, npc_data
    return None, None

def get_npc_interaction_at_tile(player_x, player_y):
    """Check if player can interact with NPC from current position"""
    for npc_id, npc_data in TAVERN_NPCS.items():
        if (player_x, player_y) in npc_data['interaction_tiles']:
            return npc_id, npc_data
    return None, None

def get_visible_npcs(game_state):
    """
    Return list of NPCs that should be visible based on game state
    Filters out recruited NPCs and checks act progression
    """
    visible_npcs = {}
    
    for npc_id, npc_data in TAVERN_NPCS.items():
        # Check conditions
        conditions = npc_data.get('conditions')
        
        if conditions is None:
            # No conditions - always visible (Garrick, Meredith, Pete)
            visible_npcs[npc_id] = npc_data
            continue
        
        # Check act progression for Mayor
        if 'act_check' in conditions:
            required_act = conditions['act_check']
            current_act = getattr(game_state, 'current_act', 1)
            if current_act != required_act:
                continue  # Skip this NPC
        
        # Check recruitment status
        if 'not_recruited' in conditions:
            flag_name = conditions['not_recruited']
            if game_state.get_flag(flag_name):
                continue  # Skip recruited NPCs
        
        # NPC passed all checks
        visible_npcs[npc_id] = npc_data
    
    return visible_npcs

# === AREA TRANSITIONS ===
AREA_TRANSITIONS = {
    'exit_door': {
        'entrance_tiles': [(9, 18), (10, 18)],
        'building_pos': [(9, 18), (10, 18)],
        'info': {
            'name': 'Tavern Exit',
            'interaction_type': 'navigation',
            'target_screen': 'redstone_town',
            'action': 'Leave the Broken Blade',
            'requirements': {}
        }
    },
    'basement_stairs': {
        'entrance_tiles': [(1, 1), (2, 1), (1, 2)],  # Upper left corner
        'building_pos': [(1, 1)],
        'info': {
            'name': 'Basement Stairs',
            'interaction_type': 'combat',
            'target_screen': 'combat',
            'combat_encounter': 'tavern_basement_rats',
            'action': 'Descend to Basement',
            'requirements': {
                'flags': {
                    'accepted_basement_quest': True,
                    'completed_basement_combat': False
                }
            }
        }
    },
    'basement_cleared': {
        'entrance_tiles': [(1, 1), (2, 1), (1, 2)],  # Upper left corner
        'building_pos': [(1, 1)],
        'info': {
            'name': 'Basement',
            'interaction_type': 'navigation',
            'target_screen': 'broken_blade.basement_cleared',
            'action': 'Visit Basement',
            'requirements': {
                'flags': {
                    'completed_basement_combat': True
                }
            }
        }
    }
}

def get_transition_at_entrance(player_x, player_y):
    """Check if player is at area transition point"""
    for transition_id, transition_data in AREA_TRANSITIONS.items():
        if (player_x, player_y) in transition_data['entrance_tiles']:
            return transition_data['info']
    return None

def check_transition_requirements(transition_info, game_state):
    """Check if player meets requirements for transition"""
    requirements = transition_info.get('requirements', {})
    
    if not requirements:
        return True  # No requirements
    
    # Check flag requirements
    if 'flags' in requirements:
        for flag_name, required_value in requirements['flags'].items():
            actual_value = game_state.get_flag(flag_name)
            if actual_value != required_value:
                return False
    
    return True

# === SPECIAL INTERACTION AREAS ===
SPECIAL_AREAS = {
    'dice_game': {
        'trigger_tiles': [(7, 10), (8, 10), (9, 10), (7, 11), (8, 11), (9, 11)],
        'info': {
            'name': 'Dice Game Table',
            'interaction_type': 'navigation',
            'target_screen': 'dice_bets',
            'action': 'Play Redstone Dice',
            'requirements': {}
        }
    }
}

def get_special_area_at_tile(player_x, player_y):
    """Check if player is at special interaction area"""
    for area_id, area_data in SPECIAL_AREAS.items():
        if (player_x, player_y) in area_data['trigger_tiles']:
            return area_data['info']
    return None
```

#### Step 1.2: Test Map Data File

Create a simple test script to validate the map:

```python
# test_broken_blade_map.py (temporary test file)
from data.maps.broken_blade_map import *

# Test map dimensions
assert BROKEN_BLADE_WIDTH == 20
assert BROKEN_BLADE_HEIGHT == 20
assert len(BROKEN_BLADE_MAP) == 20
for row in BROKEN_BLADE_MAP:
    assert len(row) == 20

# Test walkability
assert is_walkable(9, 18)  # Spawn point
assert is_walkable(5, 5)   # Open floor
assert not is_walkable(0, 0)  # Wall
assert not is_walkable(9, 3)  # Bar counter

# Test NPC positions
garrick_id, garrick_data = get_npc_at_position(9, 3)
assert garrick_id == 'garrick'

print("✅ All map data tests passed!")
```

Run test: `python test_broken_blade_map.py`

---

### PHASE 2: Create Navigation Screen (2-3 hours)

#### Step 2.1: Create `screens/broken_blade_nav.py`

**Full file contents:**

```python
# screens/broken_blade_nav.py
"""
Broken Blade Tavern Navigation Screen
Scrollable tile-based interior exploration
"""

import pygame
from ui.base_location_navigation import NavigationRenderer
from utils.constants import BLACK, WHITE, YELLOW, CYAN, RED
from utils.graphics import draw_centered_text, draw_border
from utils.party_display import draw_party_status_panel
from data.maps.broken_blade_map import *

class BrokenBladeNav:
    """Navigation screen for Broken Blade tavern interior"""
    
    def __init__(self):
        # Configure NavigationRenderer with map functions
        config = {
            'map_width': BROKEN_BLADE_WIDTH,
            'map_height': BROKEN_BLADE_HEIGHT,
            'location_id': 'broken_blade_tavern',
            'map_functions': {
                'get_tile_type': get_tile_type,
                'is_walkable': is_walkable,
                'get_tile_color': get_tile_color,
                'get_building_info': self._get_interaction_at_tile,
                'get_searchable_info': None,  # No searchables in tavern
                'get_combat_trigger': None,   # No random combat in tavern
                'get_location_npcs': self._get_current_npcs
            },
            'spawn_position': (TAVERN_SPAWN_X, TAVERN_SPAWN_Y)
        }
        
        self.nav_renderer = NavigationRenderer(config)
        self.temp_message = None
        self.temp_message_timer = 0
    
    def _get_current_npcs(self, game_state):
        """Get NPCs that should be visible"""
        return get_visible_npcs(game_state)
    
    def _get_interaction_at_tile(self, player_x, player_y, game_state):
        """
        Check what player can interact with at current position
        Priority: NPCs > Transitions > Special Areas
        """
        # Check for NPC interaction
        npc_id, npc_data = get_npc_interaction_at_tile(player_x, player_y)
        if npc_id:
            # Verify NPC is visible
            visible_npcs = get_visible_npcs(game_state)
            if npc_id in visible_npcs:
                return {
                    'name': npc_data['display_name'],
                    'interaction_type': 'npc',
                    'target_screen': f"broken_blade_{npc_data['dialogue_id']}",
                    'action': f"Talk to {npc_data['display_name']}",
                    'npc_id': npc_id
                }
        
        # Check for area transitions
        transition = get_transition_at_entrance(player_x, player_y)
        if transition:
            # Check requirements
            if check_transition_requirements(transition, game_state):
                return transition
            else:
                # Requirements not met - show why
                if 'basement' in transition.get('name', '').lower():
                    return {
                        'name': 'Locked Basement',
                        'interaction_type': 'blocked',
                        'action': 'The basement is locked',
                        'message': 'Perhaps the bartender knows something...'
                    }
        
        # Check for special areas (dice game)
        special = get_special_area_at_tile(player_x, player_y)
        if special:
            return special
        
        return None
    
    def render(self, screen, game_state, fonts, images):
        """Render tavern navigation screen"""
        screen.fill(BLACK)
        
        # Render the navigation map
        self.nav_renderer.render(screen, game_state, fonts, images)
        
        # Draw party status panel
        draw_party_status_panel(screen, game_state, fonts)
        
        # Draw temp message if active
        if self.temp_message and self.temp_message_timer > 0:
            message_y = 50
            draw_centered_text(
                screen, self.temp_message, 
                512, message_y, 
                fonts.get('medium', fonts.get('default')), 
                YELLOW
            )
        
        # Draw location title
        title_font = fonts.get('large', fonts.get('default'))
        draw_centered_text(
            screen, "THE BROKEN BLADE TAVERN",
            512, 10,
            title_font, YELLOW
        )
        
        # Draw interaction prompt at bottom
        self._draw_interaction_prompt(screen, game_state, fonts)
        
        return {}
    
    def _draw_interaction_prompt(self, screen, game_state, fonts):
        """Draw prompt for what player can interact with"""
        player_x = game_state.player_x
        player_y = game_state.player_y
        
        interaction = self._get_interaction_at_tile(player_x, player_y, game_state)
        
        if interaction:
            prompt_y = 720
            prompt_font = fonts.get('medium', fonts.get('default'))
            
            if interaction.get('interaction_type') == 'blocked':
                # Blocked interaction (locked door, etc.)
                prompt_text = f"🚫 {interaction.get('message', 'Blocked')}"
                draw_centered_text(screen, prompt_text, 512, prompt_y, prompt_font, RED)
            else:
                # Available interaction
                action = interaction.get('action', 'Interact')
                prompt_text = f"Press ENTER: {action}"
                draw_centered_text(screen, prompt_text, 512, prompt_y, prompt_font, CYAN)
        else:
            # Movement instructions
            prompt_y = 720
            prompt_font = fonts.get('small', fonts.get('default'))
            prompt_text = "Arrow Keys: Move | ENTER: Interact | I/Q/C/H: Menus"
            draw_centered_text(screen, prompt_text, 512, prompt_y, prompt_font, WHITE)
    
    def set_temp_message(self, message, duration=2.0):
        """Display temporary message"""
        self.temp_message = message
        self.temp_message_timer = duration

# === SCREEN INTERFACE FUNCTIONS ===

_broken_blade_nav_instance = None

def get_broken_blade_nav_instance():
    """Get or create singleton instance"""
    global _broken_blade_nav_instance
    if _broken_blade_nav_instance is None:
        _broken_blade_nav_instance = BrokenBladeNav()
    return _broken_blade_nav_instance

def draw_broken_blade_nav(screen, game_state, fonts, images):
    """Main render function for screen manager"""
    nav = get_broken_blade_nav_instance()
    return nav.render(screen, game_state, fonts, images)

def update_broken_blade_nav(game_state, dt):
    """Update function for navigation state"""
    nav = get_broken_blade_nav_instance()
    
    # Update temp message timer
    if nav.temp_message_timer > 0:
        nav.temp_message_timer -= dt
        if nav.temp_message_timer <= 0:
            nav.temp_message = None
    
    # Update navigation renderer
    nav.nav_renderer.update(game_state, dt)
```

#### Step 2.2: Test Navigation Screen (Isolated)

Before integrating, test the screen in isolation:

1. Temporarily add registration to screen_manager.py:
```python
from screens.broken_blade_nav import draw_broken_blade_nav, update_broken_blade_nav

# In _register_location_screens():
self.register_render_function(
    "broken_blade_nav_test",
    draw_broken_blade_nav,
    update_hook=update_broken_blade_nav
)
```

2. Temporarily set starting screen:
```python
# In game_state.py initialization:
self.screen = "broken_blade_nav_test"  # TEMPORARY TEST
```

3. Launch game and verify:
   - ✅ Map renders correctly
   - ✅ Player can move with arrow keys
   - ✅ Camera follows player
   - ✅ NPCs appear at correct positions
   - ✅ Interaction prompts show when near NPCs/doors
   - ✅ No crashes

4. Revert temporary changes after testing

---

### PHASE 3: Integration with Screen Manager (1 hour)

#### Step 3.1: Update `ui/screen_manager.py`

**Find the broken_blade registration section:**

```python
# OLD CODE (remove or comment out):
self._auto_register_location("broken_blade")
```

**Replace with:**

```python
# NEW CODE:
from screens.broken_blade_nav import draw_broken_blade_nav, update_broken_blade_nav

# Broken Blade Tavern - Navigation-based interior
self.register_render_function(
    "broken_blade_nav",
    draw_broken_blade_nav,
    update_hook=update_broken_blade_nav
)

# Keep patron_selection for now (may deprecate later)
self._auto_register_location("patron_selection")
```

#### Step 3.2: Update Town Map Transition

**File:** `data/maps/redstone_town_map.py`

Find the tavern building definition and update target:

```python
# OLD:
'tavern': {
    'name': 'The Broken Blade Tavern',
    'screen': 'broken_blade',  # OLD ActionHub
    'action': 'Enter tavern'
}

# NEW:
'tavern': {
    'name': 'The Broken Blade Tavern',
    'screen': 'broken_blade_nav',  # NEW Navigation screen
    'action': 'Enter the Broken Blade'
}
```

#### Step 3.3: Update Game State Tracking

**File:** `game_logic/game_state.py`

Ensure tavern position tracking exists:

```python
# In __init__() method:
self.player_x = 0
self.player_y = 0
self.previous_screen = None
self.tavern_last_position = None  # Store position when leaving tavern
```

**In save/load methods:**

```python
# In to_dict() for save:
'player_x': self.player_x,
'player_y': self.player_y,
'tavern_last_position': self.tavern_last_position,

# In from_dict() for load:
loaded_state.player_x = state_dict.get('player_x', 0)
loaded_state.player_y = state_dict.get('player_y', 0)
loaded_state.tavern_last_position = state_dict.get('tavern_last_position')
```

---

### PHASE 4: NPC Dialogue Integration (1-2 hours)

#### Step 4.1: Update Dialogue Navigation Returns

**File:** `game_logic/dialogue_engine.py`

Ensure dialogue returns to correct screen:

```python
# When dialogue ends, check where to return:
def end_dialogue(self, game_state):
    """End dialogue and return to appropriate screen"""
    # If dialogue was from tavern navigation, return there
    if game_state.previous_screen == 'broken_blade_nav':
        return 'broken_blade_nav'
    # Otherwise use existing logic
    return self._determine_return_screen(game_state)
```

#### Step 4.2: Test Each NPC Dialogue

**Test Checklist:**
1. Launch game, enter tavern navigation
2. Walk to Garrick, press ENTER
   - ✅ Dialogue loads correctly
   - ✅ All dialogue options work
   - ✅ Shopping system accessible
   - ✅ Basement quest trigger works
   - ✅ Returns to tavern navigation when done
3. Repeat for Meredith, Mayor, Pete, each recruitable NPC
4. Verify recruited NPCs disappear after recruitment
5. Verify Mayor disappears in Act II

---

### PHASE 5: Special Systems Integration (1-2 hours)

#### Step 5.1: Dice Game Integration

**Test Flow:**
1. Walk to dice game area (green tiles)
2. Press ENTER
3. Verify dice_bets screen loads
4. Play game
5. Verify return to tavern navigation

**If issues:** Check SPECIAL_AREAS configuration in broken_blade_map.py

#### Step 5.2: Basement Quest Integration

**Test Flow - Quest Not Accepted:**
1. Walk to stairs tile
2. Press ENTER
3. Verify "locked" message shows
4. Talk to Garrick, accept quest
5. Return to stairs
6. Verify combat trigger now works

**Test Flow - Quest Accepted:**
1. Walk to stairs, press ENTER
2. Verify combat loads with basement encounter
3. Win combat
4. Verify return to tavern
5. Walk to stairs again
6. Verify "cleared basement" navigation works

#### Step 5.3: Entry/Exit Flow

**Test Flow:**
1. From Redstone Town, walk to tavern entrance
2. Press ENTER
3. Verify spawn at correct position in tavern (near door)
4. Walk around tavern
5. Walk to exit door tile
6. Press ENTER
7. Verify return to Redstone Town at correct position

---

### PHASE 6: Compatibility & Polish (1 hour)

#### Step 6.1: Save/Load Testing

**Test Checklist:**
1. Enter tavern, walk to specific position
2. Save game (in tavern)
3. Exit game completely
4. Launch game, load save
5. Verify:
   - ✅ Player in correct position in tavern
   - ✅ NPCs visible/hidden based on flags
   - ✅ All interactions still work
   - ✅ Camera positioned correctly

#### Step 6.2: Recruitment Flow Testing

**Full Flow Test:**
1. Start new game
2. Complete intro, enter tavern
3. Talk to Mayor (accept quest)
4. Recruit Gareth
   - ✅ Gareth dialogue works
   - ✅ Recruitment succeeds
   - ✅ Gareth disappears from tavern
   - ✅ Gareth appears in party status
5. Repeat for Elara, Thorman, Lyra
6. Verify max party size enforced

#### Step 6.3: Act Progression Testing

**Test Checklist:**
1. Start new game in Act I
2. Verify Mayor present in tavern
3. Progress to Act II (trigger act_two_started flag)
4. Re-enter tavern
5. Verify:
   - ✅ Mayor no longer in tavern
   - ✅ No crashes or errors
   - ✅ Other NPCs still present

---

### PHASE 7: Deprecation & Cleanup (30 minutes)

#### Step 7.1: Remove Old ActionHub (Optional)

**If everything works:**

1. Keep `data/locations/broken_blade.json` for now (basement_cleared may use it)
2. Remove `patron_selection` auto-registration if no longer needed
3. Add deprecation comment:

```python
# ui/screen_manager.py
# DEPRECATED: Old ActionHub system (replaced by navigation)
# self._auto_register_location("broken_blade")
```

#### Step 7.2: Update Documentation

Create `docs/broken_blade_refactor_notes.md`:

```markdown
# Broken Blade Navigation Refactor - Completed

## Changes Made
- Converted from ActionHub to navigation-based system
- All NPCs now positioned on map
- Walk-to-interact pattern established
- Recruited NPCs correctly disappear
- Mayor Act I/II positioning works

## Breaking Changes
- Screen ID changed from "broken_blade" to "broken_blade_nav"
- Entry point from town now uses new screen
- Direct navigation to "broken_blade" will fail (use "broken_blade_nav")

## Backwards Compatibility
- All dialogues unchanged
- Recruitment system unchanged
- Save files require migration (handled in game_state.py)

## Future Work
- Consider adding graphics to replace colored tiles
- May add more NPCs or ambient patrons
- Could expand tavern to multiple rooms
```

---

## ✅ TESTING STRATEGY

### Regression Test Suite

Run through this checklist after implementation:

#### Core Movement
- [ ] Player spawns at correct position when entering
- [ ] Arrow keys move player in all 4 directions
- [ ] Player cannot walk through walls
- [ ] Player cannot walk through bar counter
- [ ] Player can walk on floor, tables, chairs
- [ ] Camera follows player smoothly

#### NPC Interactions
- [ ] Garrick appears behind bar
- [ ] Can talk to Garrick from front of bar
- [ ] Garrick dialogue loads correctly
- [ ] Shopping system works from Garrick dialogue
- [ ] Basement quest acceptance works
- [ ] Meredith appears near tables
- [ ] Can talk to Meredith
- [ ] Meredith dialogue and shopping work
- [ ] Mayor appears in Act I
- [ ] Mayor dialogue works
- [ ] Mayor quest acceptance works
- [ ] Mayor disappears in Act II
- [ ] Pete appears at lower right table
- [ ] Can talk to Pete
- [ ] Pete dialogue works (refugee camp info)

#### Recruitment System
- [ ] Gareth, Elara, Thorman, Lyra all appear
- [ ] Cannot recruit until mayor quest accepted
- [ ] Can recruit each NPC after quest
- [ ] Recruited NPCs disappear from tavern
- [ ] Recruited NPCs appear in party status
- [ ] Max party size (3) enforced

#### Special Systems
- [ ] Dice game area accessible
- [ ] Dice game loads and works
- [ ] Returns to tavern after gambling
- [ ] Basement locked before quest
- [ ] Basement accessible after quest
- [ ] Basement combat triggers correctly
- [ ] Basement cleared state works

#### Entry/Exit
- [ ] Enter from Redstone Town works
- [ ] Spawn position correct
- [ ] Exit door returns to town
- [ ] Town position restored correctly

#### Save/Load
- [ ] Can save while in tavern
- [ ] Load restores position correctly
- [ ] Load restores NPC visibility
- [ ] Load restores all flags
- [ ] Camera position correct after load

#### Edge Cases
- [ ] No crashes when walking into walls
- [ ] No crashes when spamming ENTER
- [ ] No crashes with recruited party
- [ ] No crashes in Act II
- [ ] Temp messages display correctly
- [ ] Interaction prompts show/hide correctly

---

## 🛡️ RISK MITIGATION

### High-Risk Areas

#### 1. Save File Compatibility
**Risk:** Old saves may break with new system  
**Mitigation:**
- Add migration logic in `game_state.py`:
```python
def migrate_old_save(state_dict):
    """Migrate old save files to new format"""
    # If loading old save with "broken_blade" screen
    if state_dict.get('screen') == 'broken_blade':
        state_dict['screen'] = 'broken_blade_nav'
        state_dict['player_x'] = TAVERN_SPAWN_X
        state_dict['player_y'] = TAVERN_SPAWN_Y
    return state_dict
```

#### 2. NPC Dialogue Returns
**Risk:** Dialogues may not return to correct screen  
**Mitigation:**
- Set `previous_screen` before launching dialogue
- Test return navigation for each NPC
- Add fallback logic in dialogue_engine.py

#### 3. Recruitment Flag Sync
**Risk:** Recruited NPCs may still appear  
**Mitigation:**
- Use `get_visible_npcs()` function consistently
- Test recruitment with save/load
- Add debug logging for NPC visibility

#### 4. Basement Quest Flow
**Risk:** Complex conditional logic may break  
**Mitigation:**
- Test all basement states (locked, combat, cleared)
- Add clear flag requirements in AREA_TRANSITIONS
- Test with fresh game and loaded game

### Medium-Risk Areas

#### 5. Camera Positioning
**Risk:** Camera may not center correctly  
**Mitigation:**
- Use proven NavigationRenderer from other locations
- Test with player at edges of map
- Verify spawn position calculation

#### 6. Act Progression
**Risk:** Mayor visibility logic may fail  
**Mitigation:**
- Add `current_act` tracking in game_state
- Test Act I and Act II separately
- Add debug logging for act checks

### Common Pitfalls

#### Incorrect Screen Names
**Issue:** Typos in screen registration  
**Solution:** Use constants for screen names

#### Missing Previous Screen
**Issue:** Dialogue doesn't know where to return  
**Solution:** Always set `previous_screen` before navigation

#### NPC Position Mismatch
**Issue:** Interaction tiles don't match NPC position  
**Solution:** Verify coordinates in TAVERN_NPCS

#### Flag Name Typos
**Issue:** Recruitment flags misspelled  
**Solution:** Reference existing flag names from narrative_schema.json

---

## 🔙 ROLLBACK PLAN

### If Major Issues Arise

#### Quick Rollback (5 minutes)
```bash
# Revert to previous commit
git checkout main
git branch -D feature/broken-blade-navigation-refactor
```

#### Partial Rollback (30 minutes)
**Keep new files, restore old registration:**

1. Comment out new screen registration in `screen_manager.py`
2. Uncomment old ActionHub registration
3. Update town map to point to old screen
4. Game works as before, new code preserved for fixing

### Fallback Screens

Create temporary bypass if needed:

```python
# In screen_manager.py
def _handle_broken_blade_fallback(self, game_state):
    """Temporary fallback to old system"""
    if game_state.screen == 'broken_blade_nav':
        # Redirect to old system
        game_state.screen = 'broken_blade'
        game_state.area = 'main'
```

---

## 📊 SUCCESS METRICS

### Before Shipping
- [ ] All regression tests pass
- [ ] No crashes in 30-minute playthrough
- [ ] All NPCs interactable
- [ ] Recruitment system fully functional
- [ ] Save/load works correctly
- [ ] Act progression works
- [ ] Performance at 60 FPS

### Code Quality
- [ ] No commented-out code in final version
- [ ] Clear variable names
- [ ] Proper error handling
- [ ] Debug logging removed or disabled
- [ ] Documentation complete

---

## 🎯 POST-IMPLEMENTATION

### Create ADR

**If this works well, create ADR in decisions.md:**

```markdown
# ADR-XXX: Broken Blade Navigation Refactor
**Status:** Accepted
**Date:** [Date]

**Context:** Broken Blade tavern used static ActionHub system while all other locations used tile-based navigation, creating inconsistent player experience.

**Decision:** Converted Broken Blade to scrollable navigation system using proven pattern from Swamp Church and Hill Ruins. NPCs positioned at fixed locations, walk-to-interact model, dynamic visibility based on recruitment/act progression.

**Implementation:**
- Created data/maps/broken_blade_map.py (20x20 interior layout)
- Created screens/broken_blade_nav.py (navigation screen handler)
- Modified ui/screen_manager.py (registration)
- Modified data/maps/redstone_town_map.py (transition update)

**Consequences:**
- Positive: Consistent navigation UX across all locations, easier to add new tavern NPCs, better immersion
- Positive: Established reusable pattern for future interior locations
- Neutral: Slightly longer time to reach NPCs (walk vs click)
- Risk: Save file migration required for existing saves

**Files Modified:** ui/screen_manager.py, data/maps/redstone_town_map.py
**Files Created:** data/maps/broken_blade_map.py, screens/broken_blade_nav.py
```

### OR Create Commit Message

**If no ADR needed:**

```
Converted Broken Blade tavern to tile-based navigation system

- Created 20x20 interior map with NPC positions
- Walk-to-interact model for all tavern NPCs
- Dynamic NPC visibility (recruitment/act progression)
- Maintains all existing functionality (dialogue, gambling, basement)
- Pattern consistent with Swamp Church and Hill Ruins
```

---

## 📞 TROUBLESHOOTING GUIDE

### Issue: NPCs Don't Appear

**Symptoms:** Tavern renders but no NPCs visible

**Diagnosis:**
1. Check `get_visible_npcs()` is being called
2. Verify NPC positions in TAVERN_NPCS (8 NPCs total)
3. Check flag conditions (recruitment status, act progression)

**Fix:**
```python
# Add debug logging in broken_blade_nav.py:
visible_npcs = get_visible_npcs(game_state)
print(f"DEBUG: Visible NPCs: {list(visible_npcs.keys())}")
```

### Issue: Dialogue Doesn't Return to Tavern

**Symptoms:** After talking to NPC, stuck on dialogue screen

**Diagnosis:**
1. Check `previous_screen` is set before dialogue
2. Verify dialogue_engine return logic
3. Check screen name spelling

**Fix:**
```python
# In broken_blade_nav.py, before launching dialogue:
game_state.previous_screen = 'broken_blade_nav'
```

### Issue: Can't Enter Basement

**Symptoms:** Pressing ENTER at stairs does nothing

**Diagnosis:**
1. Check flag: `accepted_basement_quest`
2. Verify AREA_TRANSITIONS requirements
3. Check transition detection logic

**Fix:**
```python
# Add debug logging:
transition = get_transition_at_entrance(player_x, player_y)
if transition:
    print(f"DEBUG: Found transition: {transition}")
    requirements_met = check_transition_requirements(transition, game_state)
    print(f"DEBUG: Requirements met: {requirements_met}")
```

### Issue: Player Spawns in Wrong Position

**Symptoms:** Enter tavern, player in wall or wrong location

**Diagnosis:**
1. Check TAVERN_SPAWN_X, TAVERN_SPAWN_Y constants
2. Verify spawn_position in NavigationRenderer config
3. Check map coordinates

**Fix:**
```python
# Verify spawn point is walkable:
assert is_walkable(TAVERN_SPAWN_X, TAVERN_SPAWN_Y)
```

### Issue: Recruited NPCs Still Visible

**Symptoms:** Gareth still in tavern after recruitment

**Diagnosis:**
1. Check flag is actually set: `gareth_recruited`
2. Verify `get_visible_npcs()` checks flags
3. Check flag name spelling matches

**Fix:**
```python
# Add debug check:
if game_state.get_flag('gareth_recruited'):
    print("DEBUG: Gareth should be hidden")
```

---

## 🎓 LESSONS FOR FUTURE INTERIOR LOCATIONS

### Reusable Pattern Established

When creating new interior locations (Inn, Shop, etc.), follow this template:

1. **Create map file:** `data/maps/[location]_map.py`
2. **Create nav screen:** `screens/[location]_nav.py`
3. **Register in screen_manager:** `register_render_function()`
4. **Update connecting screen:** Point transition to new nav screen
5. **Test thoroughly:** Entry, exit, NPCs, interactions

### Best Practices Learned

- Always use `get_visible_npcs()` for dynamic NPC management
- Set `previous_screen` before any navigation
- Test with save/load at every stage
- Use constants for spawn positions
- Keep WALKABLE_TILES and tile type dicts consistent
- Add requirements checking for conditional areas
- Test Act progression separately

---

## 📋 FINAL CHECKLIST

Before marking this refactor complete:

### Code Quality
- [ ] No console errors or warnings
- [ ] No commented-out debug code
- [ ] All magic numbers replaced with constants
- [ ] Error handling in place
- [ ] Code follows project style

### Testing
- [ ] Full regression test suite passed
- [ ] 30-minute playthrough without issues
- [ ] Save/load tested multiple times
- [ ] All NPCs tested
- [ ] All special systems tested

### Documentation
- [ ] ADR created (or commit message prepared)
- [ ] Troubleshooting notes added
- [ ] Code comments clear
- [ ] README updated if needed

### Integration
- [ ] No conflicts with other systems
- [ ] Backwards compatible (or migration added)
- [ ] Performance acceptable
- [ ] No memory leaks

### User Experience
- [ ] Smooth transitions
- [ ] Clear interaction prompts
- [ ] No confusing navigation
- [ ] Consistent with other locations

---

## 🚀 READY TO IMPLEMENT

This plan provides everything needed for successful implementation:
- ✅ Clear architectural approach
- ✅ Complete file contents
- ✅ Step-by-step phases
- ✅ Testing checkpoints
- ✅ Risk mitigation
- ✅ Troubleshooting guide
- ✅ Rollback plan

**Estimated Total Time:** 6-8 hours across 2-3 sessions

**Recommended Approach:**
- **Session 1:** Phases 0-2 (Prep, Map Data, Nav Screen)
- **Session 2:** Phases 3-5 (Integration, Dialogues, Special Systems)
- **Session 3:** Phases 6-7 (Testing, Polish, Cleanup)

**Good luck, and may your code compile on the first try!** 🎮✨

---

*End of Implementation Plan*