# Terror in Redstone - Act II Exploration System Implementation Plan

**Document Version:** 1.0  
**Date:** October 29, 2025  
**Status:** Approved for Implementation  
**Estimated Sessions:** 9-13 (approximately 10-15 development hours)

---

## 🎯 EXECUTIVE SUMMARY

This document defines the complete implementation plan for Terror in Redstone's Act II exploration system. The approach uses **phased development** starting with a simple list-based location menu (rapid prototyping), then upgrading to an interactive tile-based regional map (visual polish).

### Key Design Principles
- **Content First:** Get locations playable immediately, polish later
- **Migration-Friendly:** Option 2 → Option 1 requires zero location content changes
- **Reuse Architecture:** Leverage existing BaseLocation, ScreenManager, narrative schema patterns
- **Discovery-Driven:** Locations appear only when unlocked through dialogue/quests
- **Combat Integration:** Use existing tactical combat system for all encounters

### Development Philosophy
Following classic 1980s RPG development patterns: prove gameplay mechanics first, add visual flourishes after content validation. This mirrors how games like Pool of Radiance, Ultima IV, and Wizardry were developed.

---

## 📋 SYSTEM OVERVIEW

### Act II Game Flow
```
Broken Blade Tavern
    ↓
Mayor Dialogue (sets discovery flags)
    ↓
ACT TWO Transition Screen (narrative moment)
    ↓
Exploration Hub (location selection)
    ↓
Discovered Locations (swamp church, hill ruins, refugee camp, mine)
    ↓
Location Areas (investigation, dialogue, combat)
    ↓
Return to Hub or Town
```

### Three-Phase Implementation Strategy

**PHASE 1 (Session 9):** Foundation with List-Based Hub  
- ACT TWO transition screen
- Exploration hub using simple button menu
- Discovery flag system integration
- **Deliverable:** Players can navigate to unlocked locations

**PHASE 2 (Sessions 10):** First Complete Location  
- Swamp Church with 3 areas (exterior/interior/crypt)
- Investigation mechanics, loot, combat integration
- **Deliverable:** End-to-end location experience

**PHASE 3 (Session 11):** Visual Map Upgrade  
- Replace list menu with interactive tile-based regional map
- Terrain rendering, location icons, click detection
- **Deliverable:** Polished exploration experience

**PHASE 4 (Sessions 12-13):** Additional Locations  
- Hill Ruins, Refugee Camp, Red Hollow Mine
- **Deliverable:** Complete Act II content

---

## 🗺️ EXPLORATION HUB DESIGNS

### Option 2: List-Based Menu (PHASE 1 - Sessions 9)
```
┌─────────────────────────────────────────────┐
│     THE REDSTONE REGION - ACT TWO          │
├─────────────────────────────────────────────┤
│                                             │
│  ⛪ THE CHURCH IN THE SWAMP                │
│     A fog-shrouded church deep in the       │
│     marshlands. Cult activity reported.     │
│     [TRAVEL THERE]                          │
│                                             │
│  🏔️ THE RUINS ON THE HILL                 │
│     Ancient watchtower overlooking the      │
│     valley. Strange lights at night.        │
│     [TRAVEL THERE]                          │
│                                             │
│  (Other locations appear when discovered)   │
│                                             │
│  [RETURN TO REDSTONE TOWN]                 │
└─────────────────────────────────────────────┘
```

**Implementation:** Pure JSON using existing BaseLocation ActionHubLocation pattern  
**Complexity:** Low - reuses proven architecture  
**Time:** 30 minutes  
**Advantages:** Immediate playability, zero risk, easy testing

### Option 1: Tile-Based Regional Map (PHASE 3 - Session 11)
```
┌─────────────────────────────────────────────┐
│     THE CRIMSON REACH REGION               │
├─────────────────────────────────────────────┤
│  [16x16 tile grid - 32px tiles]            │
│                                             │
│    🏔️ [Hill Ruins] ← clickable icon       │
│         ↑                                   │
│         │                                   │
│    🏘️ REDSTONE ────→ ⛪ [Swamp Church]    │
│         │                                   │
│         ↓                                   │
│    ⛺ [Refugee Camp]                        │
│                                             │
│  Terrain: Hills, Forest, Mountains, Rivers  │
│  Discovered: 2 of 4 locations              │
│  [RETURN TO TOWN]                          │
└─────────────────────────────────────────────┘
```

**Implementation:** Custom tile renderer similar to redstone_town_navigation.py  
**Complexity:** Medium - new rendering system, map data entry  
**Time:** 3-3.5 hours  
**Advantages:** Immersive, geographic context, authentic 80s RPG feel

---

## 🏗️ ARCHITECTURE INTEGRATION

### Existing Systems Leveraged
- **BaseLocation Framework:** All locations use ActionHubLocation pattern
- **Narrative Schema:** Discovery flags defined in narrative_schema.json
- **Combat System:** Existing tactical combat for all encounters
- **ScreenManager:** Standard registration and transition patterns
- **DialogueEngine:** Story progression through NPC conversations

### New Components Required

**Data Files:**
```
data/
├── narrative/
│   └── act_two.json                    # NEW - Act II transition narrative
├── locations/
│   ├── exploration_hub.json            # NEW - Phase 1 list menu config
│   └── swamp_church.json               # NEW - Three-area location
└── maps/
    └── crimson_reach_region.py         # NEW - Phase 3 tile map data
```

**Screen Files:**
```
screens/
├── act_two_transition.py               # NEW - Cinematic Act II screen
├── exploration_hub.py                  # NEW - Phase 1 list, Phase 3 tile map
└── locations/
    └── swamp_church.py                 # NEW - Custom logic if needed (optional)
```

---

## 📅 SESSION-BY-SESSION IMPLEMENTATION PLAN

## SESSION 9A: ACT TWO Transition & Narrative Schema Setup

**Duration:** 45-60 minutes  
**Goal:** Create narrative transition and flag infrastructure

### Tasks

#### 1. Create ACT TWO Transition Screen (30 minutes)
Reuse intro_scenes.py architecture for consistency.

**File:** `screens/act_two_transition.py`
```python
# Copy pattern from intro_scenes.py
# Single scene: "ACT TWO: THE INVESTIGATION BEGINS"
# CONTINUE button → transition to exploration_hub
```

**File:** `data/narrative/act_two.json`
```json
{
  "act_two_transition": {
    "title": "ACT TWO: THE INVESTIGATION BEGINS",
    "scenes": [
      {
        "id": "act_two_start",
        "title": "The Investigation Begins",
        "content": [
          "With your companions assembled and the Mayor's urgent plea echoing in your mind, you prepare to venture beyond Redstone's walls.",
          "Three locations demand investigation: the fog-shrouded church in the southern swamps, the ancient ruins overlooking the valley, and the refugee camp where displaced miners seek shelter.",
          "Somewhere in these troubled lands lies the answer to Redstone's darkness. The tremors grow stronger. Time is running short."
        ],
        "next_scene": "exploration_hub",
        "background_style": "town_overlook"
      }
    ],
    "ui_config": {
      "continue_button_text": "BEGIN EXPLORATION",
      "title_color": "YELLOW",
      "text_color": "WHITE"
    }
  }
}
```

**Integration Points:**
- Register with ScreenManager: `screen_manager.register("act_two_start", ...)`
- Trigger from Mayor dialogue or South Gate exit
- Sets flag: `act_two_started = True`

#### 2. Update Narrative Schema (15 minutes)

**File:** `data/narrative_schema.json`

Add Act II location flags:
```json
{
  "locations": {
    "swamp_church": {
      "system_id": "swamp_church",
      "name": "The Church in the Swamp",
      "discovery_flag": "swamp_church_discovered",
      "completion_flag": "swamp_church_complete",
      "description": "A fog-shrouded church deep in the marshlands where cult activity has been reported."
    },
    "hill_ruins": {
      "system_id": "hill_ruins",
      "name": "The Ruins on the Hill",
      "discovery_flag": "hill_ruins_discovered",
      "completion_flag": "hill_ruins_complete",
      "description": "Ancient watchtower overlooking the valley, glowing with strange lights at night."
    },
    "refugee_camp": {
      "system_id": "refugee_camp",
      "name": "The Refugee Camp",
      "discovery_flag": "refugee_camp_discovered",
      "completion_flag": "refugee_camp_complete",
      "description": "Makeshift settlement outside town where displaced miners seek shelter."
    },
    "red_hollow_mine": {
      "system_id": "red_hollow_mine",
      "name": "Red Hollow Mine",
      "discovery_flag": "red_hollow_mine_discovered",
      "completion_flag": "red_hollow_mine_complete",
      "description": "Abandoned mine shaft sealed by fearful workers, now home to unknown dangers."
    }
  }
}
```

Add Mayor story flags (already defined):
```json
"mayor": {
  "story_flags": {
    "gave_swamp_location": "mayor_gave_swamp_info",
    "gave_ruins_location": "mayor_gave_ruins_info",
    "gave_refugee_location": "mayor_gave_refugee_info"
  }
}
```

### Success Criteria
- ✅ ACT TWO screen displays with atmospheric text
- ✅ CONTINUE button transitions to exploration_hub
- ✅ All Act II flags initialized in GameState
- ✅ No crashes or missing dependencies

---

## SESSION 9B: Exploration Hub - List Menu (Option 2)

**Duration:** 60-90 minutes  
**Goal:** Implement discovery-driven location selection menu

### Tasks

#### 1. Create Exploration Hub JSON (30 minutes)

**File:** `data/locations/exploration_hub.json`
```json
{
  "exploration_hub": {
    "location_id": "exploration_hub",
    "name": "The Redstone Region",
    "areas": {
      "main": {
        "type": "action_hub",
        "title": "THE REDSTONE REGION",
        "description": "Several locations around Redstone demand investigation. Where will you travel?",
        "actions": {
          "swamp_church": {
            "type": "navigate",
            "target": "swamp_church.exterior",
            "label": "⛪ The Church in the Swamp",
            "description": "A fog-shrouded church deep in the marshlands. Cult activity reported.",
            "requirements": {
              "swamp_church_discovered": true
            }
          },
          "hill_ruins": {
            "type": "navigate",
            "target": "hill_ruins.entrance",
            "label": "🏔️ The Ruins on the Hill",
            "description": "Ancient watchtower overlooking the valley. Strange lights at night.",
            "requirements": {
              "hill_ruins_discovered": true
            }
          },
          "refugee_camp": {
            "type": "navigate",
            "target": "refugee_camp.main",
            "label": "⛺ The Refugee Camp",
            "description": "Makeshift settlement where displaced miners seek shelter.",
            "requirements": {
              "refugee_camp_discovered": true
            }
          },
          "red_hollow_mine": {
            "type": "navigate",
            "target": "red_hollow_mine.entrance",
            "label": "⛏️ Red Hollow Mine",
            "description": "Abandoned mine shaft, sealed by fearful workers.",
            "requirements": {
              "red_hollow_mine_discovered": true
            }
          },
          "return_town": {
            "type": "navigate",
            "target": "redstone_town",
            "label": "Return to Redstone"
          }
        }
      }
    }
  }
}
```

**Technical Notes:**
- Uses existing `ActionHubLocation` class (zero new code)
- Leverages conditional button system (ADR-073)
- Buttons with unmet requirements are automatically hidden
- Description field can be displayed as subtitle under button

#### 2. Update Mayor Dialogue (20 minutes)

**File:** `data/dialogues/broken_blade_mayor.json`

Add discovery flag effects to quest acceptance dialogue:
```json
{
  "mayor_quest_accept": {
    "text": "I'm counting on you. Investigate the swamp church, the hill ruins, and the refugee camp. Find my family. Save this town.",
    "effects": [
      {"type": "set_flag", "flag": "quest_active", "value": true},
      {"type": "set_flag", "flag": "mayor_gave_swamp_info", "value": true},
      {"type": "set_flag", "flag": "swamp_church_discovered", "value": true},
      {"type": "set_flag", "flag": "mayor_gave_ruins_info", "value": true},
      {"type": "set_flag", "flag": "hill_ruins_discovered", "value": true},
      {"type": "set_flag", "flag": "mayor_gave_refugee_info", "value": true},
      {"type": "set_flag", "flag": "refugee_camp_discovered", "value": true}
    ],
    "next_scene": "mayor_quest_active",
    "choices": []
  }
}
```

**Alternative Discovery Pattern:** (Progressive reveal)
If you want players to discover locations through different NPCs:
- Mayor reveals: swamp_church + hill_ruins
- Meredith reveals: red_hollow_mine (Henrik's quest)
- Refugee camp revealed: After visiting one location

#### 3. South Gate Integration (20 minutes)

**File:** `data/maps/redstone_town_map.py`

Add South Gate building with trigger to Act II:
```python
'south_gate': {
    'building_pos': [(8, 11)],  # Adjust coordinates as needed
    'entrance_tiles': [(8, 10)],
    'info': {
        'name': 'South Gate',
        'interaction_type': 'navigation',
        'screen': 'act_two_start',  # Triggers Act II transition
        'action': 'Leave Redstone',
        'requirements': {
            'quest_active': True  # Only after accepting Mayor's quest
        }
    }
}
```

#### 4. Screen Registration (10 minutes)

**File:** `ui/screen_manager.py`

Register new screens:
```python
# In _register_location_screens() or appropriate section
self.register_screen("act_two_start", draw_act_two_transition, 
                    enter_hook=register_act_two_buttons)

self.register_screen("exploration_hub", draw_exploration_hub,
                    enter_hook=register_exploration_hub_buttons)
```

### Testing Checklist
- [ ] Mayor dialogue sets all discovery flags correctly
- [ ] South Gate only appears after quest accepted
- [ ] Act II transition screen displays properly
- [ ] Exploration hub shows only discovered locations
- [ ] Undiscovered locations are hidden (not grayed out)
- [ ] Return to Town button works
- [ ] Save/load preserves discovery flags

### Success Criteria
- ✅ Complete flow: Tavern → Mayor → South Gate → Act II → Exploration Hub
- ✅ Conditional location display works (discovered = visible, undiscovered = hidden)
- ✅ Navigation to placeholder locations (will crash gracefully with "not implemented")
- ✅ Foundation ready for Session 10 location content

---

## SESSION 10A: Swamp Church - Area Structure

**Duration:** 90-120 minutes  
**Goal:** Build first complete three-area location with investigation mechanics

### Tasks

#### 1. Create Swamp Church Location JSON (45 minutes)

**File:** `data/locations/swamp_church.json`
```json
{
  "swamp_church": {
    "location_id": "swamp_church",
    "name": "The Church in the Swamp",
    "areas": {
      "exterior": {
        "type": "action_hub",
        "title": "SWAMP CHURCH EXTERIOR",
        "description": "Fog clings to twisted trees surrounding a half-sunken stone church. The air is thick with the smell of decay and something else... incense?",
        "actions": {
          "investigate_entrance": {
            "type": "dialogue",
            "npc_id": "swamp_church_entrance",
            "label": "Examine the Church Entrance"
          },
          "search_grounds": {
            "type": "loot_check",
            "label": "Search the Swamp Grounds",
            "loot_pool": "swamp_exterior_search",
            "requirements": {
              "swamp_exterior_searched": false
            }
          },
          "enter_church": {
            "type": "navigate",
            "target": "swamp_church.interior",
            "label": "Enter the Church"
          },
          "leave": {
            "type": "navigate",
            "target": "exploration_hub",
            "label": "Return to Region Map"
          }
        }
      },
      "interior": {
        "type": "action_hub",
        "title": "SWAMP CHURCH INTERIOR",
        "description": "Pews lie overturned. Unholy symbols are painted on the walls in dried blood. A spiral staircase descends into darkness.",
        "actions": {
          "examine_altar": {
            "type": "dialogue",
            "npc_id": "cult_altar",
            "label": "Examine the Desecrated Altar"
          },
          "read_documents": {
            "type": "dialogue",
            "npc_id": "cult_documents",
            "label": "Read Scattered Cult Documents"
          },
          "search_interior": {
            "type": "loot_check",
            "label": "Search the Church Interior",
            "loot_pool": "swamp_interior_search",
            "requirements": {
              "swamp_interior_searched": false
            }
          },
          "stairs_down": {
            "type": "navigate",
            "target": "swamp_church.crypt",
            "label": "Descend into the Crypt",
            "requirements": {
              "read_cult_documents": true
            }
          },
          "leave": {
            "type": "navigate",
            "target": "swamp_church.exterior",
            "label": "Return to Church Exterior"
          }
        }
      },
      "crypt": {
        "type": "action_hub",
        "title": "SWAMP CHURCH CRYPT",
        "description": "The air grows cold as you descend. Candles flicker around a ritual circle. Cultists turn to face you, weapons drawn.",
        "actions": {
          "fight_cultists": {
            "type": "combat",
            "label": "Face the Cultists",
            "combat_encounter": "swamp_church_crypt_fight",
            "combat_context": {
              "location_name": "Swamp Church Crypt",
              "victory_description": "The cultists fall, but their leader escapes through a hidden passage! You find documents confirming the kidnappings.",
              "defeat_description": "You retreat from the crypt, wounded but alive. The cultists laugh as you flee.",
              "victory_quest_flags": {
                "swamp_church_complete": true,
                "cult_leader_encountered": true,
                "found_cult_documents": true
              }
            },
            "requirements": {
              "swamp_church_complete": false
            }
          },
          "examine_ritual": {
            "type": "dialogue",
            "npc_id": "ritual_circle",
            "label": "Examine the Ritual Circle",
            "requirements": {
              "swamp_church_complete": true
            }
          },
          "leave": {
            "type": "navigate",
            "target": "swamp_church.interior",
            "label": "Return Upstairs"
          }
        }
      }
    }
  }
}
```

#### 2. Create Investigation Dialogue Files (30 minutes)

**File:** `data/dialogues/swamp_church_entrance.json`
```json
{
  "dialogue_id": "swamp_church_entrance",
  "npc_name": "Church Entrance",
  "initial_scene": "first_look",
  "scenes": {
    "first_look": {
      "text": "The church doors hang open, the wood swollen and rotting. Fresh bootprints in the mud lead inside. Someone—or something—has been here recently.",
      "effects": [
        {"type": "set_flag", "flag": "examined_church_entrance", "value": true}
      ],
      "choices": []
    }
  }
}
```

**File:** `data/dialogues/cult_documents.json`
```json
{
  "dialogue_id": "cult_documents",
  "npc_name": "Cult Documents",
  "initial_scene": "read_papers",
  "scenes": {
    "read_papers": {
      "text": "Scattered papers reveal disturbing truths: 'The Aethel Ore failed. Human sacrifices are now required to stabilize the portal. The Mayor's family will serve perfectly—their bloodline is old and strong.'",
      "effects": [
        {"type": "set_flag", "flag": "read_cult_documents", "value": true},
        {"type": "set_flag", "flag": "learned_sacrifice_plan", "value": true},
        {"type": "xp_award", "amount": 50, "reason": "Discovered cult plans"}
      ],
      "choices": []
    }
  }
}
```

**File:** `data/dialogues/cult_altar.json`
```json
{
  "dialogue_id": "cult_altar",
  "npc_name": "Desecrated Altar",
  "initial_scene": "examine",
  "scenes": {
    "examine": {
      "text": "The stone altar is covered in dried blood and strange symbols. A sense of wrongness permeates this place—reality feels thin here, as if something beyond is trying to push through.",
      "effects": [
        {"type": "set_flag", "flag": "examined_altar", "value": true}
      ],
      "choices": []
    }
  }
}
```

#### 3. Create Loot Pools (15 minutes)

**File:** `data/loot/swamp_church_loot.json` (NEW file)
```json
{
  "swamp_exterior_search": {
    "items": [
      {
        "item_id": "glowcap_mushroom",
        "quantity": 3,
        "chance": 1.0,
        "message": "You find several glowing mushrooms growing in the dampest corners."
      }
    ],
    "gold": {
      "min": 0,
      "max": 0
    },
    "xp": 25,
    "search_flag": "swamp_exterior_searched"
  },
  "swamp_interior_search": {
    "items": [
      {
        "item_id": "healing_potion",
        "quantity": 2,
        "chance": 0.8
      }
    ],
    "gold": {
      "min": 10,
      "max": 30
    },
    "xp": 25,
    "search_flag": "swamp_interior_searched"
  }
}
```

**Note:** Glowcap mushrooms are required for Cassia's Phase 1 quest.

### Testing Checklist
- [ ] All three areas accessible via navigation
- [ ] Investigation dialogues trigger and set flags correctly
- [ ] Loot search actions work (items added to inventory)
- [ ] Crypt stairs only appear after reading documents
- [ ] Navigation flow: exterior → interior → crypt → return paths work
- [ ] All story flags persist in save/load

### Success Criteria
- ✅ Complete three-area location with atmosphere and investigation
- ✅ Discovery mechanics work (examine, search, read)
- ✅ Navigation between areas is intuitive
- ✅ Foundation ready for combat integration

---

## SESSION 10B: Swamp Church - Combat Integration

**Duration:** 60-90 minutes  
**Goal:** Add tactical combat encounter to crypt, test full location flow

### Tasks

#### 1. Define Enemy Stats (20 minutes)

**File:** `data/combat/enemies/cultists.json`
```json
{
  "cultist": {
    "name": "Fanatic Cultist",
    "level": 2,
    "max_hp": 18,
    "armor_class": 12,
    "stats": {
      "strength": 10,
      "dexterity": 12,
      "constitution": 12,
      "intelligence": 10,
      "wisdom": 10,
      "charisma": 8
    },
    "attacks": [
      {
        "name": "Dagger",
        "type": "melee",
        "damage_dice": "1d4",
        "damage_bonus": 0,
        "hit_bonus": 2,
        "range": 1
      }
    ],
    "abilities": [
      {
        "name": "Dark Bolt",
        "type": "ranged_spell",
        "damage_dice": "1d6",
        "damage_type": "necrotic",
        "range": 6,
        "uses": 2
      }
    ],
    "ai_behavior": "aggressive",
    "xp_value": 50,
    "loot_table": "cultist_loot"
  },
  "cult_leader_swamp": {
    "name": "Cult Priest",
    "level": 3,
    "max_hp": 28,
    "armor_class": 14,
    "stats": {
      "strength": 10,
      "dexterity": 14,
      "constitution": 14,
      "intelligence": 14,
      "wisdom": 16,
      "charisma": 12
    },
    "attacks": [
      {
        "name": "Staff Strike",
        "type": "melee",
        "damage_dice": "1d6",
        "damage_bonus": 1,
        "hit_bonus": 3,
        "range": 1
      }
    ],
    "abilities": [
      {
        "name": "Dark Bolt",
        "type": "ranged_spell",
        "damage_dice": "2d6",
        "damage_type": "necrotic",
        "range": 6,
        "uses": 4
      },
      {
        "name": "Shadow Shield",
        "type": "buff",
        "effect": "Gain +2 AC for 3 rounds",
        "uses": 2
      }
    ],
    "ai_behavior": "tactical",
    "escape_threshold": 0.25,
    "escape_message": "The cult priest snarls a curse and vanishes in a swirl of shadow!",
    "xp_value": 100,
    "loot_table": "cult_leader_loot"
  }
}
```

#### 2. Define Combat Encounter (15 minutes)

**File:** `data/combat/encounters/swamp_church.json`
```json
{
  "swamp_church_crypt_fight": {
    "name": "Crypt Ambush",
    "description": "Cultists defend their ritual chamber!",
    "enemies": [
      {
        "enemy_id": "cultist",
        "count": 2,
        "positions": [[3, 2], [3, 5]]
      },
      {
        "enemy_id": "cult_leader_swamp",
        "count": 1,
        "positions": [[5, 3]]
      }
    ],
    "map_id": "crypt_chamber",
    "music": "combat_tense",
    "victory_rewards": {
      "xp": 200,
      "gold": 75,
      "items": ["cult_documents_evidence", "healing_potion"]
    }
  }
}
```

#### 3. Define Combat Map (15 minutes)

**File:** `data/combat/maps/crypt_chamber.json`
```json
{
  "crypt_chamber": {
    "name": "Ritual Chamber",
    "width": 10,
    "height": 8,
    "terrain": [
      [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
      [".", ".", "W", ".", ".", ".", "W", ".", ".", "."],
      [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
      ["P", "P", ".", ".", "A", ".", ".", ".", ".", "."],
      ["P", "P", ".", ".", ".", ".", ".", ".", ".", "."],
      [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
      [".", ".", "W", ".", ".", ".", "W", ".", ".", "."],
      [".", ".", ".", ".", ".", ".", ".", ".", ".", "."]
    ],
    "terrain_legend": {
      ".": "floor",
      "W": "wall",
      "P": "player_spawn",
      "A": "altar"
    },
    "special_tiles": {
      "altar": {
        "positions": [[4, 3]],
        "passable": false,
        "provides_cover": true
      }
    }
  }
}
```

#### 4. Integration Testing (20 minutes)

**Test Sequence:**
1. Load game → Navigate to exploration hub
2. Select Swamp Church
3. Progress through exterior → interior → crypt
4. Trigger combat encounter
5. Fight cultists (test AI, abilities, escape mechanics)
6. Verify victory: flags set, XP awarded, items granted
7. Return to exploration hub
8. Verify swamp_church_complete flag is set

### Testing Checklist
- [ ] Combat triggers from crypt action
- [ ] All enemies spawn in correct positions
- [ ] Cultist AI behaves appropriately (attacks, uses Dark Bolt)
- [ ] Cult leader uses abilities and may escape at low HP
- [ ] Victory rewards granted correctly
- [ ] Victory flags set (swamp_church_complete, cult_leader_encountered)
- [ ] Return to hub after combat
- [ ] Save/load preserves completion state

### Success Criteria
- ✅ Full location playable start to finish
- ✅ Combat integrated seamlessly with exploration
- ✅ Victory/defeat handled correctly
- ✅ First Act II location complete and tested

---

## SESSION 11: Visual Map Upgrade (Option 1)

**Duration:** 180-210 minutes  
**Goal:** Replace list-based hub with interactive tile-based regional map

### Overview
This session transforms the exploration hub from a simple menu into an immersive tile-based regional map, matching the aesthetic of the town navigation system while providing geographic context.

### Tasks

#### 1. Create Regional Map Data (60 minutes)

**File:** `data/maps/crimson_reach_region.py`
```python
"""
Crimson Reach Regional Map - Terror in Redstone
16x16 tile grid showing terrain and key locations
Tiles are 32x32 pixels, total map size 512x512, centered on screen
"""

# Terrain type constants
TERRAIN_HILLS = 'H'
TERRAIN_FOREST = 'F'
TERRAIN_MOUNTAINS = 'M'
TERRAIN_PLAINS = '-'
TERRAIN_RIVER = 'R'
TERRAIN_SWAMP = ':'
TERRAIN_TOWN = '*'

# Terrain colors for rendering
TERRAIN_COLORS = {
    'H': (210, 180, 140),   # Hills - tan
    'F': (34, 139, 34),     # Forest - green
    'M': (128, 128, 128),   # Mountains - gray
    '-': (245, 245, 220),   # Plains - beige
    'R': (135, 206, 250),   # River - light blue
    ':': (105, 105, 105),   # Swamp - dark gray
    '*': (255, 215, 0)      # Redstone - gold
}

# 16x16 terrain grid (matches reference map image)
CRIMSON_REACH_TERRAIN = [
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'M', 'H', 'H', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'F', 'F', 'H', 'H', 'H', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'F', 'H', 'H', 'F', 'H', 'H', 'H', 'H', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', '*', 'H', 'M', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'M', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'M', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'H', 'F', 'F', 'H', 'H', 'M', 'M', 'M', 'M', 'M', 'M'],
    ['H', 'H', 'H', 'H', 'H', 'F', 'F', 'F', 'H', ':', ':', 'R', 'M', 'M', 'R', 'R'],
    ['H', 'H', 'H', 'H', 'H', 'F', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'H', 'F', 'F', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'H', 'F', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'H', '-', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'H', 'F', 'F', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'F', 'F', 'F', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R'],
    ['H', 'H', 'H', 'F', 'F', 'F', 'F', ':', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R']
]

# Location definitions with grid coordinates
REGION_LOCATIONS = {
    'redstone_town': {
        'name': 'Redstone',
        'grid_pos': (8, 4),  # Column 8, Row 4
        'discovery_flag': None,  # Always visible
        'icon': '🏘️',
        'icon_color': (255, 215, 0),  # Gold
        'target': 'redstone_town',
        'description': 'The mining town at the heart of the region.'
    },
    'hill_ruins': {
        'name': 'Hill Ruins',
        'grid_pos': (8, 1),
        'discovery_flag': 'hill_ruins_discovered',
        'icon': '🏔️',
        'icon_color': (180, 180, 180),  # Gray
        'target': 'hill_ruins.entrance',
        'description': 'Ancient watchtower overlooking the valley.'
    },
    'old_mine': {
        'name': 'Old Mine',
        'grid_pos': (10, 6),
        'discovery_flag': 'red_hollow_mine_discovered',
        'icon': '⛏️',
        'icon_color': (139, 69, 19),  # Brown
        'target': 'red_hollow_mine.entrance',
        'description': 'Abandoned mine shaft, sealed by fearful workers.'
    },
    'swamp_church': {
        'name': 'Swamp Church',
        'grid_pos': (7, 10),
        'discovery_flag': 'swamp_church_discovered',
        'icon': '⛪',
        'icon_color': (128, 0, 128),  # Purple
        'target': 'swamp_church.exterior',
        'description': 'Fog-shrouded church deep in the marshlands.'
    },
    'refugee_camp': {
        'name': 'Refugee Camp',
        'grid_pos': (5, 12),
        'discovery_flag': 'refugee_camp_discovered',
        'icon': '⛺',
        'icon_color': (165, 42, 42),  # Brown
        'target': 'refugee_camp.main',
        'description': 'Makeshift settlement of displaced miners.'
    }
}

# Map rendering constants
REGION_TILE_SIZE = 32
REGION_GRID_WIDTH = 16
REGION_GRID_HEIGHT = 16
REGION_MAP_WIDTH = REGION_GRID_WIDTH * REGION_TILE_SIZE  # 512
REGION_MAP_HEIGHT = REGION_GRID_HEIGHT * REGION_TILE_SIZE  # 512

# Center map on 1024x768 screen, leaving room for UI
REGION_MAP_X = (1024 - REGION_MAP_WIDTH) // 2  # 256
REGION_MAP_Y = 100  # Leave room for title at top

def get_terrain_at(x, y):
    """Get terrain type at grid coordinates"""
    if 0 <= y < REGION_GRID_HEIGHT and 0 <= x < REGION_GRID_WIDTH:
        return CRIMSON_REACH_TERRAIN[y][x]
    return None

def get_location_at(x, y):
    """Check if there's a location at grid coordinates"""
    for location_id, location_data in REGION_LOCATIONS.items():
        if location_data['grid_pos'] == (x, y):
            return location_id, location_data
    return None, None

def is_location_discovered(location_data, game_state):
    """Check if location is discovered (always show if no flag)"""
    flag = location_data.get('discovery_flag')
    if flag is None:
        return True
    return getattr(game_state, flag, False)
```

#### 2. Create Tile Map Screen (90 minutes)

**File:** `screens/exploration_hub.py`
```python
"""
Exploration Hub - Interactive Regional Map
Tile-based visualization of Crimson Reach region with clickable locations
"""

import pygame
from data.maps.crimson_reach_region import (
    CRIMSON_REACH_TERRAIN, REGION_LOCATIONS, TERRAIN_COLORS,
    REGION_TILE_SIZE, REGION_MAP_X, REGION_MAP_Y,
    REGION_GRID_WIDTH, REGION_GRID_HEIGHT,
    is_location_discovered, get_location_at
)
from utils.constants import YELLOW, WHITE, BLACK, GRAY
from utils.graphics import draw_button, draw_centered_text

class ExplorationHubManager:
    """Manages regional map display and location selection"""
    
    def __init__(self, game_state, event_manager):
        self.game_state = game_state
        self.event_manager = event_manager
        self.hovered_location = None
        self.clickable_areas = {}
    
    def render(self, surface, fonts, images):
        """Render the regional map with clickable locations"""
        surface.fill(BLACK)
        
        # Title
        title_surface = fonts['fantasy_large'].render("THE CRIMSON REACH", True, YELLOW)
        title_rect = title_surface.get_rect(center=(512, 40))
        surface.blit(title_surface, title_rect)
        
        # Render terrain grid
        self._render_terrain(surface)
        
        # Render discovered locations
        self._render_locations(surface, fonts)
        
        # Render location info panel (if hovered)
        if self.hovered_location:
            self._render_location_info(surface, fonts)
        
        # Return button
        return_button = draw_button(surface, 412, 650, 200, 50,
                                   "RETURN TO TOWN", fonts['fantasy_medium'])
        
        self.clickable_areas = {
            'return': return_button
        }
        
        return self.clickable_areas
    
    def _render_terrain(self, surface):
        """Draw terrain tiles"""
        for y in range(REGION_GRID_HEIGHT):
            for x in range(REGION_GRID_WIDTH):
                terrain = CRIMSON_REACH_TERRAIN[y][x]
                color = TERRAIN_COLORS.get(terrain, GRAY)
                
                screen_x = REGION_MAP_X + (x * REGION_TILE_SIZE)
                screen_y = REGION_MAP_Y + (y * REGION_TILE_SIZE)
                
                # Draw tile with subtle border
                pygame.draw.rect(surface, color,
                               (screen_x, screen_y, REGION_TILE_SIZE, REGION_TILE_SIZE))
                pygame.draw.rect(surface, BLACK,
                               (screen_x, screen_y, REGION_TILE_SIZE, REGION_TILE_SIZE), 1)
    
    def _render_locations(self, surface, fonts):
        """Draw location icons for discovered locations"""
        for location_id, location_data in REGION_LOCATIONS.items():
            if not is_location_discovered(location_data, self.game_state):
                continue
            
            grid_x, grid_y = location_data['grid_pos']
            screen_x = REGION_MAP_X + (grid_x * REGION_TILE_SIZE)
            screen_y = REGION_MAP_Y + (grid_y * REGION_TILE_SIZE)
            
            # Draw icon background (circle)
            center = (screen_x + REGION_TILE_SIZE // 2, screen_y + REGION_TILE_SIZE // 2)
            pygame.draw.circle(surface, location_data.get('icon_color', WHITE), center, 12)
            pygame.draw.circle(surface, BLACK, center, 12, 2)
            
            # Draw icon text (emoji or letter)
            icon = location_data.get('icon', '?')
            icon_surface = fonts['normal'].render(icon, True, BLACK)
            icon_rect = icon_surface.get_rect(center=center)
            surface.blit(icon_surface, icon_rect)
            
            # Highlight if hovered
            if self.hovered_location == location_id:
                pygame.draw.circle(surface, YELLOW, center, 14, 3)
            
            # Store clickable area
            click_rect = pygame.Rect(screen_x, screen_y, REGION_TILE_SIZE, REGION_TILE_SIZE)
            self.clickable_areas[location_id] = click_rect
    
    def _render_location_info(self, surface, fonts):
        """Render info panel for hovered location"""
        location_data = REGION_LOCATIONS[self.hovered_location]
        
        # Draw info box at bottom
        info_box = pygame.Rect(256, 620, 512, 80)
        pygame.draw.rect(surface, (40, 40, 40), info_box)
        pygame.draw.rect(surface, YELLOW, info_box, 2)
        
        # Location name
        name_surface = fonts['fantasy_medium'].render(location_data['name'], True, YELLOW)
        name_rect = name_surface.get_rect(center=(512, 640))
        surface.blit(name_surface, name_rect)
        
        # Description
        desc_surface = fonts['small'].render(location_data['description'], True, WHITE)
        desc_rect = desc_surface.get_rect(center=(512, 670))
        surface.blit(desc_surface, desc_rect)
    
    def handle_mouse_move(self, pos):
        """Update hovered location based on mouse position"""
        self.hovered_location = None
        
        for location_id, click_rect in self.clickable_areas.items():
            if location_id == 'return':
                continue
            if click_rect.collidepoint(pos):
                self.hovered_location = location_id
                break
    
    def handle_click(self, pos):
        """Handle location selection"""
        # Check return button
        if 'return' in self.clickable_areas:
            if self.clickable_areas['return'].collidepoint(pos):
                self.event_manager.emit("SCREEN_CHANGE", {"target": "redstone_town"})
                return
        
        # Check location clicks
        for location_id, click_rect in self.clickable_areas.items():
            if location_id == 'return':
                continue
            if click_rect.collidepoint(pos):
                location_data = REGION_LOCATIONS[location_id]
                target = location_data['target']
                self.event_manager.emit("SCREEN_CHANGE", {"target": target})
                return

# Global manager instance
_hub_manager = None

def get_hub_manager(game_state, event_manager):
    """Get or create hub manager singleton"""
    global _hub_manager
    if _hub_manager is None:
        _hub_manager = ExplorationHubManager(game_state, event_manager)
    return _hub_manager

def draw_exploration_hub(surface, game_state, fonts, images):
    """Main render function for exploration hub"""
    hub_manager = get_hub_manager(game_state, None)
    return hub_manager.render(surface, fonts, images)

def register_exploration_hub_buttons(screen_manager):
    """Register clickable areas with screen manager"""
    # Mouse movement handled in game loop
    pass

def handle_exploration_hub_input(event, game_state, event_manager):
    """Handle input events for exploration hub"""
    hub_manager = get_hub_manager(game_state, event_manager)
    
    if event.type == pygame.MOUSEMOTION:
        hub_manager.handle_mouse_move(event.pos)
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        hub_manager.handle_click(event.pos)
```

#### 3. Update Screen Registration (20 minutes)

**File:** `ui/screen_manager.py`

Replace exploration_hub registration:
```python
# OLD (Option 2 - list menu)
# from data.locations.exploration_hub import draw_exploration_hub_list

# NEW (Option 1 - tile map)
from screens.exploration_hub import (
    draw_exploration_hub, 
    register_exploration_hub_buttons,
    handle_exploration_hub_input
)

# In registration method
self.register_screen("exploration_hub", draw_exploration_hub,
                    enter_hook=register_exploration_hub_buttons,
                    input_handler=handle_exploration_hub_input)
```

#### 4. Testing & Polish (30 minutes)

**Test Checklist:**
- [ ] Map renders correctly with all terrain types
- [ ] Discovered locations show icons
- [ ] Undiscovered locations remain hidden
- [ ] Clicking location navigates to target
- [ ] Hover shows location info panel
- [ ] Return button works
- [ ] Map centered properly on screen
- [ ] Performance is smooth (60 FPS)

**Polish Tasks:**
- Add subtle hover animation (icon pulse)
- Add completion indicators (checkmarks on completed locations)
- Add "X of Y locations discovered" counter
- Consider adding terrain legend

### Success Criteria
- ✅ Interactive tile-based regional map functional
- ✅ All discovered locations clickable and navigate correctly
- ✅ Visual upgrade complete without breaking any existing content
- ✅ Professional, immersive exploration experience

---

## SESSIONS 12-13: Additional Locations

**Duration:** 2-3 hours per location  
**Goal:** Complete Act II content with all major locations

### Locations to Implement

#### Hill Ruins (Session 12)
- **Structure:** 3 areas (entrance, ground_level, dungeon)
- **Features:** 
  - Portal-stone chamber discovery
  - Locked dungeon entrance (requires refugee camp key)
  - Animated armor + shadow ghost encounters
- **Rewards:** Portal knowledge, map fragment

#### Refugee Camp (Session 13A)
- **Structure:** 2 areas (main_camp, nighttime_defense)
- **Features:**
  - Social encounters (NPC conversations)
  - Brigand raid defense combat
  - Dungeon key discovery
  - Mayor's family information
- **Rewards:** Dungeon key, faction reputation

#### Red Hollow Mine (Session 13B - Optional)
- **Structure:** 2 areas (entrance, deeper_shafts)
- **Features:**
  - Kobold encounters
  - Aethel Ore discovery
  - Meredith's ring (if quest active)
  - Henrik's lantern (Act III item)
- **Rewards:** Ore samples, quest items

Each location follows the same pattern established with swamp church:
1. Create location JSON with areas
2. Create investigation dialogue files
3. Define combat encounters and enemies
4. Add loot pools and rewards
5. Test navigation and flag progression

---

## 🎯 SUCCESS CRITERIA & TESTING

### Overall System Success Metrics

**Technical Quality:**
- [ ] Zero crashes or game-breaking bugs
- [ ] All locations navigable without issues
- [ ] Save/load preserves all discovery and completion flags
- [ ] Combat integration seamless across all locations
- [ ] Performance maintained at 60 FPS

**Content Quality:**
- [ ] All locations have atmospheric descriptions
- [ ] Investigation mechanics engaging and rewarding
- [ ] Combat encounters balanced and challenging
- [ ] Story progression clear and logical
- [ ] Quest hooks integrated naturally

**User Experience:**
- [ ] Discovery system intuitive (locations unlock naturally)
- [ ] Navigation clear and consistent
- [ ] Visual feedback for completed locations
- [ ] Regional map provides geographic context
- [ ] Return to town always available

### Testing Protocol

**Session-End Testing:**
After each session, perform full regression test:
1. New game → character creation → intro
2. Tavern → Mayor dialogue → verify flags
3. South Gate → Act II transition
4. Exploration hub → verify all discovered locations show
5. Navigate to each location → test all areas
6. Trigger combat encounters → verify victory/defeat
7. Return to hub → verify completion flags
8. Save game → reload → verify persistence
9. Performance check → maintain 60 FPS

**Integration Testing:**
Before starting new session:
1. Load previous session's save
2. Verify all progress preserved
3. Test transitions between systems
4. Check dialogue flag progression
5. Validate combat balance

---

## 📝 ARCHITECTURE DECISION RECORD

### ADR: Act II Exploration System Implementation

**Status:** Accepted  
**Date:** October 29, 2025

**Context:**
Terror in Redstone requires exploration system for Act II investigations. Players need to discover and navigate to multiple locations (swamp church, hill ruins, refugee camp, mine) based on NPC dialogue and quest progression.

**Decision:**
Implement phased exploration system starting with simple list-based location menu (Option 2), upgrading to interactive tile-based regional map (Option 1) after content validation.

**Implementation Approach:**
- Phase 1: List menu using BaseLocation ActionHubLocation pattern
- Phase 2: Content development (swamp church as prototype)
- Phase 3: Visual upgrade to tile-based map
- Phase 4: Additional location content

**Rationale:**
- **Content-first development:** Prove gameplay before polish
- **Risk mitigation:** Validate discovery and navigation systems early
- **Migration-friendly:** Option 2 → Option 1 requires zero location content changes
- **Architectural consistency:** Leverages existing BaseLocation, narrative schema, combat systems
- **Classic RPG approach:** Mirrors 1980s development patterns (functionality before graphics)

**Consequences:**
- Positive: Rapid prototyping, early playability, proven architecture
- Positive: Clear upgrade path maintains development momentum
- Positive: Reuses existing systems reduces bug surface area
- Neutral: Two implementation phases for exploration hub (acceptable tradeoff)
- Risk mitigation: Content development decoupled from visual implementation

**Technical Specifications:**
- Discovery system: Narrative schema flags control location visibility
- Navigation: Standard ScreenManager transitions to location.area targets
- Combat integration: Existing tactical combat system via encounter definitions
- Map rendering: Pygame tile system matching town navigation pattern (32x32 tiles, 16x16 grid)

**Files Modified:**
- New: screens/act_two_transition.py, screens/exploration_hub.py
- New: data/narrative/act_two.json, data/locations/swamp_church.json
- New: data/maps/crimson_reach_region.py
- Enhanced: data/narrative_schema.json (Act II location flags)
- Enhanced: data/dialogues/broken_blade_mayor.json (discovery flags)

**Dependencies:**
- BaseLocation architecture (ADR-046, ADR-112)
- Narrative schema system (ADR-074)
- Tactical combat system (ADR-094, ADR-104)
- Screen manager lifecycle (ADR-015)

---

## 🎲 APPENDIX: QUICK REFERENCE

### File Structure Summary
```
screens/
├── act_two_transition.py           # Cinematic Act II intro
├── exploration_hub.py               # Option 1 tile map OR Option 2 list menu
└── locations/
    └── swamp_church.py              # Custom logic (if needed)

data/
├── narrative/
│   ├── act_two.json                 # Act II transition content
│   └── narrative_schema.json        # Act II discovery flags
├── locations/
│   ├── exploration_hub.json         # Option 2 list menu config
│   └── swamp_church.json            # Three areas + encounters
├── dialogues/
│   ├── broken_blade_mayor.json      # Updated with discovery flags
│   ├── swamp_church_entrance.json   # Investigation dialogues
│   ├── cult_documents.json
│   └── cult_altar.json
├── combat/
│   ├── enemies/cultists.json        # Enemy definitions
│   ├── encounters/swamp_church.json # Encounter configs
│   └── maps/crypt_chamber.json      # Combat map layouts
├── loot/
│   └── swamp_church_loot.json       # Loot pools for searching
└── maps/
    └── crimson_reach_region.py      # Option 1 tile map data
```

### Key Flags Reference
```python
# Location Discovery Flags
swamp_church_discovered = False
hill_ruins_discovered = False
refugee_camp_discovered = False
red_hollow_mine_discovered = False

# Location Completion Flags
swamp_church_complete = False
hill_ruins_complete = False
refugee_camp_complete = False
red_hollow_mine_complete = False

# Story Progression Flags
act_two_started = False
quest_active = False
cult_leader_encountered = False
found_cult_documents = False
learned_sacrifice_plan = False
```

### Navigation Targets
```python
# Act II Flow
"act_two_start" → "exploration_hub"

# Location Targets
"swamp_church.exterior" → "swamp_church.interior" → "swamp_church.crypt"
"hill_ruins.entrance" → "hill_ruins.ground_level" → "hill_ruins.dungeon"
"refugee_camp.main" → "refugee_camp.nighttime_defense"
"red_hollow_mine.entrance" → "red_hollow_mine.deeper_shafts"

# Return Paths
"exploration_hub" ← "redstone_town"
Any location → "exploration_hub"
```

### Session Timeline Summary
```
Session 9A (45-60 min):   ACT TWO screen + narrative schema setup
Session 9B (60-90 min):   Exploration hub (list menu)
Session 10A (90-120 min): Swamp church areas + investigation
Session 10B (60-90 min):  Swamp church combat integration
Session 11 (180-210 min): Visual map upgrade (tile-based)
Session 12 (120-180 min): Hill Ruins implementation
Session 13A (90-120 min): Refugee Camp implementation
Session 13B (60-90 min):  Red Hollow Mine (optional)
```

---

## 🚀 GETTING STARTED

### Starting Session 9A Right Now

**Step 1:** Copy intro_scenes.py architecture
```bash
cp screens/intro_scenes.py screens/act_two_transition.py
# Edit to single scene pattern
```

**Step 2:** Create Act II narrative JSON
```bash
# Create data/narrative/act_two.json
# Use template provided in Session 9A
```

**Step 3:** Update narrative schema
```bash
# Edit data/narrative_schema.json
# Add location discovery flags
```

**Step 4:** Test the transition
```bash
python game.py
# Load save → trigger Act II → verify screen displays
```

### Next Session Preparation

Before Session 9B:
- [ ] Verify Act II transition working
- [ ] Review exploration_hub.json template
- [ ] Plan Mayor dialogue updates
- [ ] Identify South Gate trigger location in town map

---

## 📞 SUPPORT & QUESTIONS

### Common Issues & Solutions

**Issue:** "Location not appearing in exploration hub"
- **Check:** Discovery flag set correctly in dialogue
- **Check:** Flag name matches narrative_schema.json
- **Check:** Requirements block in exploration_hub.json

**Issue:** "Combat doesn't trigger from location"
- **Check:** combat_encounter ID matches encounters JSON
- **Check:** Combat map defined in maps directory
- **Check:** Enemy IDs exist in enemies JSON

**Issue:** "Save/load loses discovery flags"
- **Check:** Flags added to narrative_schema.get_all_flags()
- **Check:** SaveManager loads narrative_flags
- **Check:** GameState initializes schema flags

### Developer Notes

**Migration from Option 2 to Option 1:**
1. Create crimson_reach_region.py map data
2. Implement exploration_hub.py tile renderer
3. Update screen_manager.py registration
4. Test navigation → all locations still work
5. Delete exploration_hub.json (no longer needed)

**Adding New Locations:**
1. Define in narrative_schema.json (flags)
2. Add to REGION_LOCATIONS in crimson_reach_region.py
3. Create data/locations/new_location.json
4. Define combat encounters if needed
5. Test discovery and navigation flow

---

**DOCUMENT END**

This implementation plan is ready for handoff to any developer (including future Claude instances). All sessions are self-contained with clear goals, file specifications, and testing criteria.

**Ready to begin Session 9A?** 🎲
