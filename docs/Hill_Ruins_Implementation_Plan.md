# Hill Ruins A - Implementation Plan
## Reusing Swamp Church Pattern (Session 12)

*Following the KISS principle: Keep It Simple, Strategist*

---

# Hill Ruins A - Implementation Plan
## Reusing Swamp Church Pattern (Session 12 - Act II Only)

*Following the KISS principle: Keep It Simple, Strategist*

---

## 🎯 EXECUTIVE SUMMARY

**What We're Building:**  
Hill Ruins Act II reconnaissance - entrance, ground level, and locked dungeon discovery. This is the FIRST of two visits to this location.

**Scope of This Session:**
- ✅ Entrance exploration (scrollable map)
- ✅ Ground level exploration (scrollable map with portal chamber)
- ✅ Locked dungeon stub (ActionHub - examine door only, cannot proceed)
- ❌ Full dungeon (Act III - NOT in this session)
- ❌ Final boss encounter (Act III - future implementation)

**Why Two Stages:**  
Classic gated-dungeon design. Players discover the location and find it locked, creating a quest hook to find the key (refugee camp) or alternative route (mine). Return in Act III with access for the final showdown.

**Template Pattern:**  
Reusing Swamp Church navigation structure - no code refactoring, just copy/modify pattern for new location.

---

## 🔗 CONNECTIONS TO OTHER LOCATIONS

### Refugee Camp Dependency
**Story Link:** Dungeon key was taken from ruins by frightened refugee  
**Implementation:** Refugee Camp quest must set `hill_ruins_dungeon_key_obtained = True`  
**Player Experience:** "I need to find that key... maybe someone at the camp knows?"

### Red Hollow Mine Alternative
**Story Link:** Mine tunnels connect to ruins dungeon, bypassing locked door  
**Implementation:** Mine exploration sets `red_hollow_mine_secret_entrance_found = True`  
**Player Experience:** "Henrik mentioned the mine tunnels go deep... maybe there's another way in?"

### Act III Return Visit
**Story Link:** Return with key OR secret knowledge to access full dungeon  
**Implementation:** Act III checks either flag to enable dungeon access  
**Player Experience:** Either use key at front door, or enter via mine passage

### Mayor's Quest Integration
**Story Link:** Mayor's family imprisoned in dungeon depths  
**Implementation:** Mayor dialogue evolves after Act II exploration, urgency increases  
**Player Experience:** "I found the ruins, but the dungeon is sealed. I must find a way in!"

---

## 🎯 GOAL
Create Hill Ruins location with same hybrid structure as Swamp Church:
- **Entrance** (scrollable exploration map)
- **Ground Level** (scrollable exploration map) 
- **Dungeon** (ActionHub confrontation point)

---

## 📁 FILES TO CREATE (Copy & Modify Pattern)

### 1. Map Data Files
```
data/maps/
├── hill_ruins_entrance_map.py      (Copy from swamp_church_exterior_map.py)
└── hill_ruins_ground_level_map.py  (Copy from swamp_church_interior_map.py)
```

### 2. Navigation Screen Files
```
screens/
├── hill_ruins_entrance_nav.py      (Copy from swamp_church_exterior_nav.py)
└── hill_ruins_ground_level_nav.py  (Copy from swamp_church_interior_nav.py)
```

### 3. Location Configuration
```
data/locations/
└── hill_ruins.json                 (Copy from swamp_church.json structure)
```

### 4. Dialogue Files (for searchables)
```
data/dialogues/
└── hill_ruins_searchables.json     (Copy from swamp_searchables.json)
```

---

## 🎭 TWO-STAGE NARRATIVE DESIGN

### Critical Story Structure
Hill Ruins is visited **TWICE** in the game:

**ACT II - First Visit (Initial Exploration):**
- **Entrance:** Outdoor ruins exploration (scrollable map)
- **Ground Level:** Interior ruins with portal chamber (scrollable map)
- **Dungeon:** LOCKED - ActionHub with "examine locked door" only
  - Discovery: "The key is missing - taken by someone from the camp"
  - Sets flag: `hill_ruins_locked_door_found`
  - Cannot proceed further until key obtained

**Get Access - Two Possible Paths:**
- **Path A:** Complete Refugee Camp → find dungeon key → `hill_ruins_dungeon_key_obtained`
- **Path B:** Complete Red Hollow Mine (Henrik's quest) → discover secret entrance → `red_hollow_mine_secret_entrance_found`

**ACT III - Second Visit (Final Dungeon):**
- Return with key OR knowledge of secret entrance
- Dungeon now accessible (full exploration/combat)
- Descend into portal chamber (cult sanctum)
- Final boss encounter
- Rescue Mayor's family

### Implementation Impact
This means we need:
1. **Act II Implementation:** Entrance + Ground Level + Locked Dungeon stub
2. **Act III Implementation:** Full dungeon with boss encounter (Session 14+)
3. **Conditional Logic:** Dungeon only accessible when `hill_ruins_dungeon_key_obtained` OR `red_hollow_mine_secret_entrance_found`

---

## 🗺️ HILL RUINS ENTRANCE MAP DESIGN

### Thematic Differences from Swamp Church
**Swamp Church:** Fog, decay, marshland, ancient symbols  
**Hill Ruins:** Windswept, crumbled stone, overgrown, hilltop view

### Map Features (20x20 grid)
```python
# data/maps/hill_ruins_entrance_map.py

HILL_RUINS_ENT_WIDTH = 20
HILL_RUINS_ENT_HEIGHT = 20

# Map Layout Ideas:
# 'g' = grass/ground
# 'r' = rubble (searchable)
# 'w' = crumbled wall (examine)
# 'c' = carved stone (examine - lore)
# 'D' = door to ground level
# 'E' = exit back to regional map
# '~' = random combat trigger (bandits, animated statues)

HILL_RUINS_ENT_MAP = [
    "####################",
    "#gggggggggggggggggg#",
    "#ggwwwww..gggggggg#",   # Crumbled walls
    "#gg.............gg#",
    "#gg...rrrr......gg#",   # Rubble pile (searchable)
    "#gg...rrrr......gg#",
    "#gg.............gg#",
    "#ggwwwwwwwwwgggg#",
    "#gg...~....D...gg#",   # Door entrance, combat trigger
    "#gg............gg#",
    "#ggcc..........gg#",   # Carved stones (lore)
    "#ggcc..........gg#",
    "#gg............gg#",
    "#gg~...........gg#",   # Combat trigger
    "#gg............gg#",
    "#gg............gg#",
    "#gggggggg......gg#",
    "#ggggggggg..Egggg#",   # Exit
    "####################@",  # @ = spawn point
    "####################"
]

# Searchable definitions
SEARCHABLES = {
    'rubble_pile': {
        'positions': [(6,4), (7,4), (8,4), (9,4), (6,5), (7,5), (8,5), (9,5)],
        'info': {
            'name': 'Ancient Rubble',
            'interaction_type': 'searchable',
            'dialogue_id': 'rubble_examine',
            'one_time_flag': 'hill_ruins_rubble_searched'
        }
    },
    'carved_stones': {
        'positions': [(4,10), (5,10), (4,11), (5,11)],
        'info': {
            'name': 'Carved Stones',
            'interaction_type': 'searchable',
            'dialogue_id': 'carved_stones_examine',
            'one_time_flag': 'hill_ruins_carved_searched'
        }
    }
}

# Area transitions
AREA_TRANSITIONS = {
    'ground_level_door': {
        'entrance_tiles': [(13, 8)],  # D tile
        'building_pos': [(13, 8)],
        'info': {
            'name': 'Enter Ruins',
            'interaction_type': 'navigation',
            'target_screen': 'hill_ruins_ground_level_nav',
            'action': 'Enter the Ruined Structure'
        }
    },
    'return_to_map': {
        'entrance_tiles': [(14, 17)],  # E tile
        'building_pos': [(14, 17)],
        'info': {
            'name': 'Return to Map',
            'interaction_type': 'navigation',
            'target_screen': 'exploration_hub',
            'action': 'Leave Hill Ruins'
        }
    }
}

# Combat triggers (bandits, animated statues)
COMBAT_TRIGGERS = {
    (8, 8): {
        'encounter_id': 'hill_ruins_bandits',
        'chance': 0.15,
        'one_time_flag': 'hill_ruins_entrance_combat_1_cleared'
    },
    (4, 13): {
        'encounter_id': 'hill_ruins_statue',
        'chance': 0.20,
        'one_time_flag': 'hill_ruins_entrance_combat_2_cleared'
    }
}

# Tile type function (copy pattern from swamp)
def get_tile_type(x, y):
    if y < 0 or y >= len(HILL_RUINS_ENT_MAP):
        return 'wall'
    if x < 0 or x >= len(HILL_RUINS_ENT_MAP[y]):
        return 'wall'
    
    char = HILL_RUINS_ENT_MAP[y][x]
    
    if char == '#':
        return 'wall'
    elif char in ['g', '.', '~', 'D', 'E', '@', 'r', 'w', 'c']:
        return 'ground'
    return 'wall'

def is_walkable(x, y):
    return get_tile_type(x, y) == 'ground'

# [Additional functions following swamp church pattern...]
```

---

## 🎮 HILL RUINS ENTRANCE NAV SCREEN

```python
# screens/hill_ruins_entrance_nav.py
# Copy from swamp_church_exterior_nav.py and modify:

"""
Hill Ruins Entrance Navigation
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
from data.maps.hill_ruins_entrance_map import *  # <-- CHANGED

class HillRuinsEntranceNav:  # <-- CHANGED class name
    """Navigation screen for hill ruins entrance exploration"""
    
    def __init__(self):
        config = {
            'map_width': HILL_RUINS_ENT_WIDTH,  # <-- CHANGED
            'map_height': HILL_RUINS_ENT_HEIGHT,  # <-- CHANGED
            'location_id': 'hill_ruins_entrance',  # <-- CHANGED
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
        self.showing_temp_message = False
        self.temp_message_text = ""
        self.temp_message_timer = 0
        self.graphics_manager = get_tile_graphics_manager()
    
    def update_player_position(self, game_state):
        """Initialize player position if needed"""
        if not hasattr(game_state, 'hill_ruins_entrance_x'):  # <-- CHANGED
            game_state.hill_ruins_entrance_x = 10  # <-- Spawn point from map
            game_state.hill_ruins_entrance_y = 18  # <-- CHANGED
        
        self.renderer.update_camera(
            game_state.hill_ruins_entrance_x,  # <-- CHANGED
            game_state.hill_ruins_entrance_y   # <-- CHANGED
        )
    
    # [Rest of update() and render() methods follow same pattern as swamp church]
    # Just change variable names: swamp_church -> hill_ruins_entrance

# Integration function
_hill_ruins_entrance_nav_instance = None  # <-- CHANGED

def draw_hill_ruins_entrance_nav(surface, game_state, fonts, images, controller=None):  # <-- CHANGED
    global _hill_ruins_entrance_nav_instance
    
    if _hill_ruins_entrance_nav_instance is None:
        _hill_ruins_entrance_nav_instance = HillRuinsEntranceNav()  # <-- CHANGED
    
    if hasattr(pygame, 'key') and pygame.get_init():
        keys = pygame.key.get_pressed()
        dt = 16
        _hill_ruins_entrance_nav_instance.update(dt, keys, game_state, controller)
    
    return _hill_ruins_entrance_nav_instance.render(surface, fonts, game_state)

# Similar update hook function
def update_hill_ruins_entrance_nav(dt, keys, game_state, controller):
    # [Same pattern as swamp church update]
    pass
```

---

## 🏰 HILL RUINS GROUND LEVEL (Second Area)

Same pattern as entrance, just change:
- Map to interior ruins layout (collapsed ceiling, portal room, stairs down)
- File names: `hill_ruins_ground_level_map.py` and `hill_ruins_ground_level_nav.py`
- Variable names throughout
- Searchables: portal chamber tiles, ancient mechanisms
- Transition to dungeon ActionHub instead of back to entrance

---

## 📋 HILL RUINS DUNGEON (Act II - LOCKED STUB)

**IMPORTANT:** In Act II, the dungeon is just a locked door encounter. The full dungeon is for Act III!

```json
// data/locations/hill_ruins.json
{
  "hill_ruins": {
    "location_id": "hill_ruins",
    "name": "The Ruins on the Hill",
    "areas": {
      "entrance": {
        // This area is handled by hill_ruins_entrance_nav.py
        // No ActionHub config needed
      },
      "ground_level": {
        // This area is handled by hill_ruins_ground_level_nav.py
        // No ActionHub config needed
      },
      "dungeon_locked": {
        "type": "action_hub",
        "title": "SEALED DUNGEON ENTRANCE",
        "description": "Ancient stone steps descend into darkness. At the bottom, a massive reinforced door bars the way - ancient dwarven construction with intricate locking mechanisms. The lock is empty - the key is missing.",
        "actions": {
          "examine_door": {
            "type": "dialogue",
            "npc_id": "locked_dungeon_door",
            "label": "Examine the Sealed Door"
          },
          "search_entrance": {
            "type": "loot_check",
            "label": "Search the Entrance Chamber",
            "loot_table": "hill_ruins_entrance_search",
            "requirements": {
              "hill_ruins_entrance_searched": false
            }
          },
          "try_force_door": {
            "type": "dialogue",
            "npc_id": "force_door_attempt",
            "label": "Attempt to Force the Door",
            "requirements": {
              "examined_locked_door": true
            }
          },
          "return_upstairs": {
            "type": "navigate",
            "target": "hill_ruins_ground_level_nav",
            "label": "Return to Ground Level"
          }
        }
      }
    }
  }
}
```

### Locked Door Dialogue

```json
// data/dialogues/hill_ruins_locked_door.json
{
  "dialogue_id": "locked_dungeon_door",
  "npc_name": "Sealed Dungeon Door",
  "initial_scene": "examine",
  "scenes": {
    "examine": {
      "text": "The door is massive - reinforced iron banded with dark steel, covered in ancient dwarven runes. The lock mechanism is intricate but intact. You can see a keyhole, but no key. Someone must have taken it... or hidden it.",
      "effects": [
        {"type": "set_flag", "flag": "examined_locked_door", "value": true},
        {"type": "set_flag", "flag": "hill_ruins_locked_door_found", "value": true},
        {"type": "xp_award", "amount": 25, "reason": "Discovered locked dungeon"}
      ],
      "choices": []
    }
  }
}
```

```json
// data/dialogues/force_door_attempt.json
{
  "dialogue_id": "force_door_attempt",
  "npc_name": "Narrator",
  "initial_scene": "attempt",
  "scenes": {
    "attempt": {
      "text": "You examine the door carefully, testing its strength. The construction is masterwork - forcing it would take days with proper tools, or explosive magic that would likely collapse the entire entrance. You'll need the key... or find another way in. Perhaps someone at the refugee camp knows something?",
      "effects": [
        {"type": "set_flag", "flag": "attempted_force_door", "value": true}
      ],
      "choices": []
    }
  }
}
```

**Note:** The full dungeon (Act III) will be implemented in Session 14+ as a separate area or screens.

---

## 📝 STEP-BY-STEP CHECKLIST (ACT II SCOPE)

### Phase 1: Entrance Area (2-3 hours)
- [ ] Copy `swamp_church_exterior_map.py` → `hill_ruins_entrance_map.py`
- [ ] Modify map layout (change terrain, searchables, combat triggers)
- [ ] Update all function names and constants
- [ ] Copy `swamp_church_exterior_nav.py` → `hill_ruins_entrance_nav.py`
- [ ] Update class name, location_id, position variables
- [ ] Create `hill_ruins_searchables.json` with examine dialogues
- [ ] Register screen with ScreenManager
- [ ] Test: Can walk around, examine things, trigger combat, enter building

### Phase 2: Ground Level Area (2-3 hours)
- [ ] Copy entrance files → ground level versions
- [ ] Design interior ruins map layout (include portal chamber hints)
- [ ] Update transitions (stairs down to locked dungeon)
- [ ] Create interior searchables (portal chamber, ancient mechanisms)
- [ ] Add portal chamber dialogue (lore about awakening portal)
- [ ] Register screen with ScreenManager
- [ ] Test: Full navigation flow entrance → ground → locked dungeon

### Phase 3: Locked Dungeon Stub (1 hour)
- [ ] Create `hill_ruins.json` with dungeon_locked area config
- [ ] Create locked door dialogues (`locked_dungeon_door`, `force_door_attempt`)
- [ ] Set up entrance chamber loot table (minor loot only)
- [ ] Add hint dialogue pointing to refugee camp
- [ ] Test: Can examine door, get clue about missing key, return upstairs

### Phase 4: Integration (30-60 min)
- [ ] Update `exploration_hub.py` to add hill ruins click target
- [ ] Add narrative flags to schema: `hill_ruins_locked_door_found`
- [ ] Verify save/load preserves positions in all areas
- [ ] Test complete flow: Regional Map → Entrance → Ground → Locked Door → Back
- [ ] Polish any edge cases or bugs

### Phase 5: Act III Dungeon (Future Session 14+)
**NOT IMPLEMENTED IN SESSION 12 - This is for later!**
- [ ] Full dungeon exploration (portal chamber depths)
- [ ] Boss encounter (Cult Shadow Priest)
- [ ] Mayor's family rescue mechanics
- [ ] Dynamic ending based on Act II completion
- [ ] Alternative entrance from Red Hollow Mine

---

## 🔑 NARRATIVE FLAG STRUCTURE

### Flags Needed for Hill Ruins (Act II)
```python
# Discovery & Exploration
hill_ruins_discovered = False              # Can see on regional map
hill_ruins_entrance_explored = False        # Visited entrance area
hill_ruins_ground_level_explored = False    # Visited ground level
hill_ruins_portal_chamber_seen = False      # Examined portal chamber

# Locked Door
hill_ruins_locked_door_found = False        # Discovered the locked entrance
examined_locked_door = False                # Read door description
attempted_force_door = False                # Tried to force it

# Searchables
hill_ruins_rubble_searched = False
hill_ruins_carved_searched = False
hill_ruins_entrance_searched = False

# Combat
hill_ruins_entrance_combat_1_cleared = False
hill_ruins_entrance_combat_2_cleared = False
hill_ruins_ground_combat_1_cleared = False

# Act II Completion
hill_ruins_act_ii_complete = False         # Explored all accessible areas
```

### Flags for Act III Access (Set elsewhere)
```python
# From Refugee Camp
hill_ruins_dungeon_key_obtained = False    # Got key from refugee camp

# From Red Hollow Mine  
red_hollow_mine_secret_entrance_found = False  # Found alternative route

# Act III Progress
hill_ruins_dungeon_accessible = False      # Computed: has_key OR has_secret
hill_ruins_complete = False                # Defeated final boss
```

---

## 🚪 TWO PATHS TO ACT III DUNGEON

### Path A: The Direct Route (Refugee Camp Key)
1. Complete Hill Ruins Act II (find locked door)
2. Complete Refugee Camp investigation
3. Recover dungeon key from frightened refugee
4. Return to Hill Ruins for Act III
5. Use key to unlock door

**Flag Check:**
```python
if game_state.hill_ruins_dungeon_key_obtained:
    # Show "Unlock Door" action instead of locked message
    enable_dungeon_access()
```

### Path B: The Secret Route (Red Hollow Mine)
1. Accept Henrik's quest (optional)
2. Explore Red Hollow Mine
3. Discover secret tunnel system
4. Find passage connecting mine to ruins dungeon
5. Bypass locked door entirely

**Flag Check:**
```python
if game_state.red_hollow_mine_secret_entrance_found:
    # Show "Enter via Mine Tunnel" action
    # OR teleport directly into dungeon past the locked door
    enable_dungeon_access_alternate()
```

### Implementation Note
Act III dungeon screen checks BOTH flags:
```python
def can_access_dungeon(game_state):
    return (game_state.hill_ruins_dungeon_key_obtained or 
            game_state.red_hollow_mine_secret_entrance_found)
```

---

## 🎯 THEMATIC FLAVOR FOR HILL RUINS

### Act II: Reconnaissance & Discovery
**Atmosphere:** Windswept ancient watchtower ruins on hilltop, commanding view of valley, sense of dormant power awakening

**Entrance Area:**
- Crumbled walls and fallen masonry
- Ancient carved stones with faded runes
- Rubble piles that can be searched
- Hints of recent activity (footprints, disturbed earth)
- Eerie silence broken by wind through broken stones

**Ground Level:**
- Interior of ruined structure
- Portal chamber with humming crystal (can observe but not access)
- Ancient mechanisms still partially functional
- Evidence of cult activity (symbols, recent torches)
- Stairs down... to a locked door

**Locked Dungeon:**
- Massive reinforced door (dwarven construction)
- Empty keyhole - key is missing
- Sense that something important lies beyond
- **Cannot proceed further in Act II**

**Enemies (Act II):** 
- Bandits (entrance - opportunistic looters)
- Animated Stone Statues (ground level - ancient guardians)

**Loot (Act II):** 
- Ancient coins, weathered documents
- Minor healing items
- Lore about the portal-stone
- **No key** (that's at refugee camp)

**Quest Hook:** Strange lights at night, portal awakening, evidence of cult activity

### Act III: The Showdown (Future Implementation)
**Atmosphere:** Full dungeon descent, cult sanctum, active portal ritual

**Revelation:** Portal chamber shows connection to kidnappings, Mayor's family imprisoned as ritual fuel

**Enemies (Act III):**
- Shadow Ghosts, Blight Shadows
- Cult fanatics guarding portal
- Cult Shadow Priest (final boss)
- Waves of summoned shadows

**Objective:** 
- Disrupt ritual
- Rescue Mayor's family
- Defeat cult leader
- Seal or destroy portal

---

## ⚖️ WHY NO OVER-ENGINEERING?

**What we're NOT doing:**
- ❌ Creating generic `BaseLocationNavigationScreen` class
- ❌ Factory pattern for location generation
- ❌ Dynamic file loading systems
- ❌ Abstract template magic

**Why:**
- Each location is ~150 lines, 80% unique
- Copy/modify is FASTER than debugging abstractions
- Code is obvious and easy to understand
- Easier for you (novice) to debug and maintain
- Follows "worse is better" philosophy

**What we ARE doing:**
- ✅ Reusing NavigationRenderer (already does heavy lifting)
- ✅ Following proven pattern (template + modify)
- ✅ Clear file naming conventions
- ✅ Documented "recipe" for adding locations
- ✅ KISS principle in action

---

## 🔍 AFTER COMPLETION

### ADR Decision
**Q:** Do we need an ADR for Hill Ruins Act II implementation?  
**A:** Probably not - we're following established patterns (swamp church template). Unless we discover issues or make architectural changes during implementation.

### Commit Message (if no ADR needed)
```
Implemented Hill Ruins Act II exploration using Swamp Church pattern

- Created entrance and ground level scrollable exploration maps
- Added locked dungeon stub (Act II cannot proceed past locked door)
- Portal chamber discovery and lore integration
- Bandits and animated statue encounters
- Two-stage design: Act II reconnaissance, Act III final dungeon (future)
- Reused NavigationRenderer architecture, no code refactoring needed
- Complete three-area accessible flow with searchables, combat, locked door clue
```

### Note on Act III Implementation
The full dungeon (Act III final boss encounter) will be implemented in a future session after:
1. Refugee Camp (key acquisition path)
2. Red Hollow Mine (secret entrance path)  
3. Act III transition planning

This session focuses ONLY on the reconnaissance phase - entrance, ground level, and locked door discovery.

---

## 🎲 READY TO START?

Once you give the green light, we'll begin with **Phase 1: Hill Ruins Entrance Map**. We'll work step-by-step, testing as we go. No over-engineering, just solid template-based development! 

Sound good, partner?
