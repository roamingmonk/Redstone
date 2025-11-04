# Refugee Camp & Red Hollow Mine - Act II Implementation Plan
## Session 13 & 14 - Completing Act II Exploration

*Following the KISS principle: Keep It Simple, Strategist*

---

## 🎯 EXECUTIVE SUMMARY

**What We're Building:**  
Two remaining Act II locations using proven Swamp Church / Hill Ruins navigation pattern.

**Locations:**
1. **Refugee Camp** (Session 13) - Main story location with dungeon key discovery
2. **Red Hollow Mine** (Session 14) - Henrik's quest location with 4-level deep exploration

**Why These Matter:**
- **Refugee Camp**: Provides dungeon key for Hill Ruins Act III access (Path A)
- **Red Hollow Mine**: Provides secret tunnel knowledge for Hill Ruins Act III access (Path B), plus ore samples and Meredith's ring

**Template Pattern:**  
Copy/modify Swamp Church and Hill Ruins navigation structure - no new systems, just proven patterns.

**Scope:**
- ✅ Act II reconnaissance and exploration
- ✅ Combat encounters and loot discovery
- ✅ Critical flag setting for Act III access
- ❌ Full secret tunnel traversal (Act III only)

---

## 📍 LOCATION 1: REFUGEE CAMP

### Story Context

**What Is This Place:**  
Makeshift settlement outside Redstone where displaced miners and townspeople have fled. Tents, cooking fires, frightened refugees who've witnessed cult activity.

**Why Players Come Here:**  
- Mayor mentioned refugees might know about his family
- Information about Hill Ruins dungeon access
- **Critical Item:** Dungeon key (taken from ruins by frightened refugee)

**Story Beats:**
1. Initial exploration - talking with refugees
2. Dialogue with key witness (saw Mayor's family taken)
3. Brigand raid occurs (combat trigger)
4. Post-combat: Key discovery hunt begins
5. Find refugee with dungeon key (dialogue + clue)
6. Search for key location (searchable after combat)
7. Obtain key, complete location

### Two-Area Structure

#### **AREA 1: Camp Main (Scrollable Navigation)**
- 20x20 tile map with tents, campfires, refugee NPCs
- Searchable objects: supply crates, abandoned belongings
- NPC dialogues: refugees with information
- Combat trigger: brigand raid (30% chance on certain tiles after first dialogue)
- Transition to: camp interior tent

**Key Interactions:**
- Examine refugee tents (dialogue)
- Talk to camp leader (dialogue)
- Search supply crates (loot check)
- Defend against brigands (combat encounter)
- Enter medical tent (navigation to interior)

#### **AREA 2: Camp Interior - Medical Tent (Scrollable Navigation)**
- 15x15 tile map - interior of large medical tent
- Searchable objects: medical supplies, refugee belongings
- NPC dialogue: frightened refugee with key information
- **Key Discovery Mechanic:** Dialogue provides clue, searchable reveals key location
- Transition back to: camp main

**Key Interactions:**
- Talk to wounded refugees (dialogue)
- Examine medical supplies (searchable)
- Talk to specific refugee about ruins (dialogue - sets `refugee_has_key_info` flag)
- Search refugee's belongings (searchable - requires flag + combat complete) → **OBTAIN KEY**

### Flag Integration

**Discovery & Completion:**
```python
refugee_camp_discovered = False      # Set by Mayor dialogue
refugee_camp_explored = False        # Set on first entry
refugee_camp_main_explored = False   # Set on camp main exploration
refugee_camp_interior_explored = False  # Set on tent interior exploration
refugee_camp_complete = False        # Set when key obtained
```

**Story Progression:**
```python
learned_about_mayors_family = False     # Set by NPC dialogue
refugee_camp_raid_defeated = False      # Set after brigand combat
refugee_has_key_info = False            # Set by specific NPC dialogue
hill_ruins_dungeon_key_obtained = False # Set when key found (CRITICAL for Act III)
```

**Searchables:**
```python
refugee_supply_crates_searched = False
refugee_medical_supplies_searched = False
refugee_belongings_searched = False  # This one has the key
```

### Files to Create

#### Map Data Files
```
data/maps/
├── refugee_camp_main_map.py         (Copy from swamp_church_exterior_map.py)
└── refugee_camp_interior_map.py     (Copy from swamp_church_interior_map.py)
```

#### Navigation Screen Files
```
screens/
├── refugee_camp_main_nav.py         (Copy from swamp_church_exterior_nav.py)
└── refugee_camp_interior_nav.py     (Copy from swamp_church_interior_nav.py)
```

#### Location Configuration
```
data/locations/
└── refugee_camp.json                (Copy from swamp_church.json structure)
```

#### Dialogue Files (Searchables & NPCs)
```
data/dialogues/
├── refugee_camp_leader.json         (Camp leader NPC)
├── refugee_camp_witness.json        (Refugee who saw Mayor's family)
├── refugee_camp_key_holder.json     (Refugee with key info - provides clue)
├── refugee_tents.json               (Examine tents dialogue)
├── refugee_supplies.json            (Supply crate searchable)
├── refugee_medical.json             (Medical supplies searchable)
└── refugee_belongings.json          (Key discovery searchable)
```

#### Combat Files
```
data/combat/enemies/
└── brigand_raider.json              (New enemy type)

data/combat/encounters/
└── refugee_camp_raid.json           (Brigand raid encounter)

data/combat/battlefields/
└── refugee_camp_defense.json        (Combat map for raid)
```

### Combat Encounter: Brigand Raid

**Enemy Types:**
- 3x Brigand Raiders (Medium difficulty)
- 1x Brigand Leader (Harder, better tactics)

**Trigger:**
- 30% chance on specific tiles in camp main after initial dialogues
- One-time encounter (flag: `refugee_camp_raid_defeated`)

**Rewards:**
- 120 XP total
- 50 gold
- Enables key discovery sequence

### Loot Tables

**Camp Main - Supply Crates:**
```json
{
  "refugee_supply_crates": {
    "items": [
      {"item_id": "healing_potion", "quantity": 2, "chance": 0.8},
      {"item_id": "bandages", "quantity": 3, "chance": 1.0}
    ],
    "gold": {"min": 15, "max": 35},
    "xp": 25
  }
}
```

**Camp Interior - Medical Supplies:**
```json
{
  "refugee_medical_supplies": {
    "items": [
      {"item_id": "healing_potion", "quantity": 1, "chance": 0.6},
      {"item_id": "antidote", "quantity": 1, "chance": 0.5}
    ],
    "gold": {"min": 5, "max": 15},
    "xp": 20
  }
}
```

**Camp Interior - Refugee Belongings (KEY LOCATION):**
```json
{
  "refugee_belongings": {
    "items": [
      {"item_id": "hill_ruins_dungeon_key", "quantity": 1, "chance": 1.0, "message": "Hidden among tattered blankets, you find an ancient iron key!"}
    ],
    "gold": {"min": 0, "max": 5},
    "xp": 50,
    "requirements": {
      "refugee_has_key_info": true,
      "refugee_camp_raid_defeated": true
    }
  }
}
```

### Testing Checklist - Refugee Camp
- [ ] Regional map → Refugee camp main transition works
- [ ] Camp main navigation (movement, camera, collision)
- [ ] Tent examination dialogues trigger correctly
- [ ] Camp leader dialogue provides story information
- [ ] Supply crate search works (loot overlay)
- [ ] Brigand raid combat triggers (30% chance)
- [ ] Combat victory sets flag properly
- [ ] Enter medical tent → camp interior transition
- [ ] Camp interior navigation works
- [ ] Wounded refugee dialogues work
- [ ] Medical supplies search works
- [ ] Key holder refugee dialogue sets flag
- [ ] Refugee belongings search only works after requirements met
- [ ] **CRITICAL:** Dungeon key added to inventory
- [ ] **CRITICAL:** `hill_ruins_dungeon_key_obtained` flag set
- [ ] Return to camp main works
- [ ] Return to regional map works
- [ ] All flags persist in save/load

---

## 📍 LOCATION 2: RED HOLLOW MINE

### Story Context

**What Is This Place:**  
Abandoned mine shaft sealed by Henrik years ago after discovering unstable Aethel Ore. Now kobolds have nested in the sealed chambers, and something worse may lurk deeper.

**Why Players Come Here:**  
- Henrik's quest (optional side quest)
- Find Aethel Ore samples for lore/Mayor
- Recover Meredith's ring (intertwined quest)
- **Critical Discovery:** Secret tunnel to Hill Ruins dungeon (Act III alternate access)

**Story Beats:**
1. Pre-entrance area - warning signs, sealed entrance
2. Level 1 - Kobold encounters begin, ore samples visible
3. Level 2 - Deeper shafts, more dangerous enemies
4. Level 2B (Dead End) - Dangerous trap area with better loot
5. Level 3 - Deep chamber with secret tunnel discovery

### Four-Level Structure

#### **AREA 1: Pre-Entrance (Scrollable Navigation)**
- 15x15 tile map with warning signs, sealed entrance, Henrik's barriers
- Searchable objects: Henrik's warning signs, abandoned equipment
- No combat (warning area)
- Transition to: Level 1 entrance

**Key Interactions:**
- Read warning signs (dialogue)
- Examine Henrik's seal (dialogue)
- Search abandoned equipment (loot check)
- Enter mine shaft (navigation to Level 1)

#### **AREA 2: Level 1 - Mine Entrance (Scrollable Navigation)**
- 20x20 tile map with mine tunnels, ore veins, kobold nests
- Searchable objects: ore deposits, kobold supplies
- Combat triggers: Kobold scouts (35% chance on certain tiles)
- Transition to: Level 2 deeper shafts

**Key Interactions:**
- Examine glowing ore (dialogue - sets `saw_aethel_ore` flag)
- Search ore deposits (loot - ore samples)
- Fight kobold scouts (combat encounter)
- Search kobold supplies (loot check)
- Descend to deeper level (navigation to Level 2)

#### **AREA 3: Level 2 - Deeper Shafts (Scrollable Navigation)**
- 20x20 tile map with unstable tunnels, stronger ore presence
- Searchable objects: mining carts, collapsed passages
- Combat triggers: Kobold warriors (40% chance)
- Transitions: Level 2B (side passage) or Level 3 (continue down)

**Key Interactions:**
- Examine unstable tunnels (dialogue)
- Search mining carts (loot - Meredith's ring is here!)
- Fight kobold warriors (combat encounter)
- Discover side passage (navigation to Level 2B)
- Continue descent (navigation to Level 3)

#### **AREA 4: Level 2B - Collapsed Dead End (Scrollable Navigation)**
- 12x12 tile map - dangerous unstable area
- Searchable objects: valuable loot hidden in rubble
- Combat trigger: Giant spider ambush (50% chance - more dangerous)
- **Risk/Reward:** Better loot but harder encounter
- Dead end - must return to Level 2

**Key Interactions:**
- Search rubble (loot - better items)
- Avoid/fight giant spider (combat encounter)
- Examine collapse (dialogue - no way forward)
- Return to Level 2 (navigation back)

#### **AREA 5: Level 3 - Deep Chamber (ActionHub)**
- Deep ritual chamber with Aethel Ore deposits
- **Secret Tunnel Discovery:** Searchable object reveals tunnel to Hill Ruins
- **Critical Flag:** `red_hollow_mine_secret_entrance_found`
- Final ore sample collection
- Return path to surface

**Key Interactions:**
- Examine ritual chamber (dialogue - lore reveal)
- Search ore deposits (loot - more samples)
- **Discover secret tunnel** (searchable - sets critical flag)
- Examine tunnel entrance (dialogue - "Leads to the ruins... but not safe to enter yet")
- Return to surface (navigation chain back up)

### Flag Integration

**Discovery & Completion:**
```python
red_hollow_mine_discovered = False          # Set by Mayor/Henrik
red_hollow_mine_explored = False            # Set on first entry
henrik_gave_shaft_quest = False             # Set by Henrik dialogue
investigated_old_shaft = False              # Set when entering mine
red_hollow_mine_complete = False            # Set when returning to Henrik
```

**Quest Progression:**
```python
cleared_kobold_mine = False                 # Set after defeating kobolds
retrieved_ore_samples = False               # Set when ore samples found
returned_meredith_ring = False              # Set when ring returned to Meredith
reported_shaft_to_henrik = False            # Set when reporting back
mayor_examined_ore_samples = False          # Set if showing samples to Mayor
```

**Critical Act III Flag:**
```python
red_hollow_mine_secret_entrance_found = False  # CRITICAL - Enables Act III alternate path
```

**Area Exploration:**
```python
mine_pre_entrance_explored = False
mine_level_1_explored = False
mine_level_2_explored = False
mine_level_2b_explored = False
mine_level_3_explored = False
saw_aethel_ore = False
```

**Searchables:**
```python
mine_equipment_searched = False             # Pre-entrance
mine_ore_deposits_searched = False          # Level 1
mine_kobold_supplies_searched = False       # Level 1
mine_carts_searched = False                 # Level 2 - contains ring
mine_rubble_searched = False                # Level 2B
mine_deep_ore_searched = False              # Level 3
mine_secret_tunnel_discovered = False       # Level 3 - sets Act III flag
```

### Files to Create

#### Map Data Files
```
data/maps/
├── red_hollow_mine_pre_entrance_map.py     (Copy from hill_ruins_entrance_map.py)
├── red_hollow_mine_level_1_map.py          (Copy from swamp_church_exterior_map.py)
├── red_hollow_mine_level_2_map.py          (Copy from swamp_church_interior_map.py)
├── red_hollow_mine_level_2b_map.py         (Copy from smaller template)
└── red_hollow_mine_level_3_map.py          (Smaller ActionHub-style map)
```

#### Navigation Screen Files
```
screens/
├── red_hollow_mine_pre_entrance_nav.py     (Copy from hill_ruins_entrance_nav.py)
├── red_hollow_mine_level_1_nav.py          (Copy from swamp_church_exterior_nav.py)
├── red_hollow_mine_level_2_nav.py          (Copy from swamp_church_interior_nav.py)
└── red_hollow_mine_level_2b_nav.py         (Copy from similar nav screen)
```

#### Location Configuration
```
data/locations/
└── red_hollow_mine.json                    (Copy from hill_ruins.json structure)
```

#### Dialogue Files (Searchables)
```
data/dialogues/
├── mine_warning_signs.json                 (Pre-entrance warnings)
├── mine_henrik_seal.json                   (Henrik's barrier examination)
├── mine_equipment.json                     (Abandoned equipment)
├── mine_aethel_ore.json                    (Glowing ore examination - LORE)
├── mine_ore_deposits.json                  (Ore sample searchable)
├── mine_kobold_supplies.json               (Kobold nest searchable)
├── mine_unstable_tunnels.json              (Structural warning)
├── mine_carts.json                         (Mining cart search - ring found here)
├── mine_rubble.json                        (Level 2B rubble search)
├── mine_ritual_chamber.json                (Level 3 chamber lore)
├── mine_deep_ore.json                      (Level 3 ore deposits)
└── mine_secret_tunnel.json                 (SECRET TUNNEL discovery - CRITICAL)
```

#### Combat Files
```
data/combat/enemies/
├── kobold_scout.json                       (Weak kobold)
├── kobold_warrior.json                     (Medium kobold)
├── kobold_shaman.json                      (Magic-using kobold)
└── giant_spider.json                       (Level 2B threat)

data/combat/encounters/
├── mine_kobold_scouts.json                 (Level 1 encounter)
├── mine_kobold_warriors.json               (Level 2 encounter)
└── mine_spider_ambush.json                 (Level 2B encounter)

data/combat/battlefields/
├── mine_tunnel.json                        (Standard mine combat map)
└── mine_collapsed_area.json                (Level 2B spider lair)
```

### Combat Encounters

**Kobold Scouts (Level 1):**
- 2-3 Kobold Scouts
- Cowardly - may flee at low HP
- Sling attacks (ranged)
- 70 XP, 20 gold
- 35% trigger chance on tiles

**Kobold Warriors (Level 2):**
- 3-4 Kobold Warriors + 1 Kobold Shaman
- More aggressive, pack tactics
- Shaman uses healing and minor buffs
- 100 XP, 35 gold
- 40% trigger chance on tiles

**Giant Spider (Level 2B):**
- 1 Giant Spider + 2-3 baby spiders
- Web attack (immobilize)
- Poison bite (damage over time)
- Guards better loot
- 90 XP, 25 gold
- 50% trigger chance (high risk area)

### Loot Tables

**Pre-Entrance - Abandoned Equipment:**
```json
{
  "mine_equipment": {
    "items": [
      {"item_id": "rope", "quantity": 1, "chance": 0.7},
      {"item_id": "torch", "quantity": 3, "chance": 1.0}
    ],
    "gold": {"min": 10, "max": 20},
    "xp": 15
  }
}
```

**Level 1 - Ore Deposits:**
```json
{
  "mine_ore_deposits": {
    "items": [
      {"item_id": "aethel_ore_sample", "quantity": 1, "chance": 1.0, "message": "You carefully collect a sample of the glowing ore."}
    ],
    "gold": {"min": 0, "max": 0},
    "xp": 40,
    "sets_flag": "retrieved_ore_samples"
  }
}
```

**Level 1 - Kobold Supplies:**
```json
{
  "mine_kobold_supplies": {
    "items": [
      {"item_id": "healing_potion", "quantity": 1, "chance": 0.5},
      {"item_id": "silver_coins", "quantity": 8, "chance": 0.8}
    ],
    "gold": {"min": 15, "max": 30},
    "xp": 20
  }
}
```

**Level 2 - Mining Carts (RING LOCATION):**
```json
{
  "mine_carts": {
    "items": [
      {"item_id": "merediths_ring", "quantity": 1, "chance": 1.0, "message": "Beneath coal dust, a silver ring glints!"},
      {"item_id": "healing_potion", "quantity": 1, "chance": 0.6}
    ],
    "gold": {"min": 20, "max": 40},
    "xp": 50,
    "sets_flag": "found_merediths_ring"
  }
}
```

**Level 2B - Rubble (Risk/Reward):**
```json
{
  "mine_rubble": {
    "items": [
      {"item_id": "silver_coins", "quantity": 15, "chance": 1.0},
      {"item_id": "healing_potion", "quantity": 2, "chance": 0.8},
      {"item_id": "rare_gem", "quantity": 1, "chance": 0.4}
    ],
    "gold": {"min": 40, "max": 70},
    "xp": 35
  }
}
```

**Level 3 - Deep Ore Deposits:**
```json
{
  "mine_deep_ore": {
    "items": [
      {"item_id": "aethel_ore_sample", "quantity": 2, "chance": 1.0}
    ],
    "gold": {"min": 0, "max": 0},
    "xp": 50,
    "sets_flag": "retrieved_ore_samples"
  }
}
```

**Level 3 - Secret Tunnel Discovery (CRITICAL):**
```json
{
  "mine_secret_tunnel": {
    "items": [],
    "gold": {"min": 0, "max": 0},
    "xp": 75,
    "message": "Behind the ore deposits, you discover a tunnel leading toward the hill ruins!",
    "sets_flag": "red_hollow_mine_secret_entrance_found",
    "dialogue": "The tunnel is dark and unstable. Best not to risk it until you have a reason to reach the ruins from below..."
  }
}
```

### Testing Checklist - Red Hollow Mine
- [ ] Regional map → Mine pre-entrance transition
- [ ] Pre-entrance navigation works
- [ ] Warning signs examination works
- [ ] Henrik's seal examination works
- [ ] Equipment search works
- [ ] Enter mine → Level 1 transition
- [ ] Level 1 navigation works
- [ ] Aethel ore examination (lore reveal)
- [ ] Ore deposits search (samples obtained)
- [ ] Kobold scout combat triggers (35%)
- [ ] Kobold supplies search works
- [ ] Level 1 → Level 2 transition
- [ ] Level 2 navigation works
- [ ] Mining cart search (ring found!)
- [ ] Kobold warrior combat triggers (40%)
- [ ] Level 2 → Level 2B side passage works
- [ ] Level 2B navigation works
- [ ] Rubble search (better loot)
- [ ] Spider ambush triggers (50%)
- [ ] Return to Level 2 from 2B works
- [ ] Level 2 → Level 3 transition
- [ ] Level 3 (ActionHub style) works
- [ ] Ritual chamber examination (lore)
- [ ] Deep ore search (more samples)
- [ ] **CRITICAL:** Secret tunnel discovery
- [ ] **CRITICAL:** `red_hollow_mine_secret_entrance_found` flag set
- [ ] Tunnel examination dialogue (mentions not entering yet)
- [ ] Return path works (L3 → L2 → L1 → Pre → Regional map)
- [ ] All flags persist in save/load
- [ ] Ring can be returned to Meredith
- [ ] Ore samples can be shown to Mayor/Henrik
- [ ] Quest completion with Henrik works

---

## 🎯 ACT III INTEGRATION NOTES

### Hill Ruins Dungeon - Two Access Paths

Once Act III begins and players return to Hill Ruins dungeon:

**Path A: Use Refugee Camp Key**
```python
if game_state.hill_ruins_dungeon_key_obtained:
    # Unlock action appears in hill_ruins.json
    # Player can use key to open door
    # Standard entrance to dungeon
```

**Path B: Use Mine Secret Tunnel**
```python
if game_state.red_hollow_mine_secret_entrance_found:
    # Mine entrance action appears in hill_ruins.json
    # Player can enter via tunnel
    # Bypasses initial dungeon encounters
```

**Hill Ruins ActionHub (dungeon area) Conditional Actions:**

Already implemented in `data/locations/hill_ruins.json`:
```json
{
  "actions": {
    "unlock_door": {
      "type": "navigate",
      "target": "hill_ruins.dungeon_interior",
      "label": "Unlock the Door",
      "requirements": {
        "hill_ruins_dungeon_key_obtained": true
      },
      "hidden_unless_requirements_met": true
    },
    "enter_via_mine": {
      "type": "navigate",
      "target": "hill_ruins.dungeon_interior",
      "label": "Enter via Mine Tunnel",
      "requirements": {
        "red_hollow_mine_secret_entrance_found": true
      },
      "hidden_unless_requirements_met": true
    }
  }
}
```

### Quest Completion Flows

**Refugee Camp Completion:**
1. Explore camp areas
2. Defend against brigand raid
3. Get clue from refugee dialogue
4. Search belongings after combat
5. Obtain dungeon key
6. `refugee_camp_complete` flag set
7. Return to exploration hub

**Mine Completion:**
1. Explore all 5 levels
2. Defeat kobold encounters
3. Collect ore samples
4. Find Meredith's ring
5. Discover secret tunnel
6. Return to surface
7. Report to Henrik → `reported_shaft_to_henrik` flag set
8. Optional: Show ore to Mayor → bonus XP
9. Optional: Return ring to Meredith → quest reward
10. `red_hollow_mine_complete` flag set

---

## 📋 IMPLEMENTATION ORDER

### Session 13: Refugee Camp (3-4 hours)

**Phase 1: Camp Main Navigation (90 min)**
1. Copy/modify map data from swamp_church_exterior
2. Copy/modify navigation screen
3. Create location JSON with loot pools
4. Create searchable dialogues
5. Register with ScreenManager
6. Update regional map navigation target
7. Test navigation and searchables

**Phase 2: Camp Interior Navigation (60 min)**
1. Copy/modify map data for tent interior
2. Copy/modify navigation screen
3. Add interior searchables and dialogues
4. Add key discovery mechanic
5. Test full location flow

**Phase 3: Combat Integration (60 min)**
1. Create brigand enemy definitions
2. Create raid encounter
3. Create defense battlefield
4. Test combat triggers and victory
5. Verify key discovery requirements

**Phase 4: Testing & Polish (30 min)**
1. Full location playthrough
2. Verify all flags set correctly
3. Test save/load persistence
4. Verify key appears in inventory
5. Confirm integration with exploration hub

### Session 14: Red Hollow Mine (4-5 hours)

**Phase 1: Pre-Entrance & Level 1 (90 min)**
1. Copy/modify pre-entrance map and nav
2. Copy/modify Level 1 map and nav
3. Create location JSON structure
4. Create ore examination dialogues
5. Create kobold scout encounter
6. Test navigation and combat

**Phase 2: Level 2 & Level 2B (90 min)**
1. Copy/modify Level 2 map and nav
2. Create Level 2B dead end area
3. Add ring discovery to mining carts
4. Create kobold warrior encounter
5. Create spider encounter for 2B
6. Test branching navigation

**Phase 3: Level 3 & Secret Tunnel (60 min)**
1. Create Level 3 chamber (simpler ActionHub style)
2. Add secret tunnel discovery mechanic
3. Create ritual chamber lore dialogues
4. Test critical flag setting
5. Verify return path navigation

**Phase 4: Quest Integration (45 min)**
1. Test Henrik quest flow
2. Test ore sample collection
3. Test Meredith's ring recovery
4. Test reporting back to Henrik
5. Test optional Mayor ore reveal

**Phase 5: Testing & Polish (45 min)**
1. Full 5-level playthrough
2. Test all combat encounters
3. Verify all flags set correctly
4. Test save/load at each level
5. Verify Act III integration readiness

---

## 🔍 CRITICAL FLAG VERIFICATION

### Must Be Set for Act III

**Refugee Camp:**
- ✅ `hill_ruins_dungeon_key_obtained` - Enables Path A to dungeon

**Red Hollow Mine:**
- ✅ `red_hollow_mine_secret_entrance_found` - Enables Path B to dungeon

**At Least One Must Be True:**
```python
# Player must have either key OR tunnel knowledge to proceed in Act III
can_access_dungeon = (
    game_state.hill_ruins_dungeon_key_obtained or 
    game_state.red_hollow_mine_secret_entrance_found
)
```

### Optional But Recommended Flags

**For Quest Completion:**
- `retrieved_ore_samples` - Henrik quest reward
- `returned_meredith_ring` - Meredith quest reward
- `reported_shaft_to_henrik` - Henrik quest complete
- `learned_about_mayors_family` - Story progression

---

## 🎮 TESTING PROTOCOLS

### Refugee Camp Full Test Sequence
1. Load game → Navigate to exploration hub
2. Select Refugee Camp → camp main loads
3. Walk around, test searchables
4. Trigger brigand raid combat
5. Win combat → verify flag set
6. Talk to refugees → get story info
7. Enter medical tent → interior loads
8. Talk to key refugee → get clue
9. Search belongings → obtain key
10. Verify key in inventory
11. Verify flag `hill_ruins_dungeon_key_obtained = True`
12. Return to exploration hub
13. Save/load → verify persistence

### Red Hollow Mine Full Test Sequence
1. Load game → Navigate to exploration hub
2. Select Red Hollow Mine → pre-entrance loads
3. Examine warnings, search equipment
4. Enter mine → Level 1 loads
5. Examine ore, trigger kobold combat
6. Search ore deposits → get samples
7. Descend to Level 2
8. Search mining carts → get ring
9. Trigger warrior combat
10. Take side passage → Level 2B
11. Search rubble, trigger spider
12. Return to Level 2, continue to Level 3
13. Examine ritual chamber lore
14. Search deep ore deposits
15. **CRITICAL:** Discover secret tunnel
16. Verify flag `red_hollow_mine_secret_entrance_found = True`
17. Return to surface (test navigation chain)
18. Report to Henrik → verify quest complete
19. Save/load → verify persistence

### Integration Test (Both Locations)
1. Complete Refugee Camp → get key
2. Complete Red Hollow Mine → find tunnel
3. Navigate to Hill Ruins dungeon
4. Verify BOTH unlock options appear:
   - "Unlock the Door" (key path)
   - "Enter via Mine Tunnel" (tunnel path)
5. Test that either path works
6. Verify Act III dungeon is accessible

---

## 📊 SUCCESS CRITERIA

### Refugee Camp
- ✅ Two navigable areas functional
- ✅ All dialogues trigger correctly
- ✅ Combat encounter works and sets flags
- ✅ Key discovery mechanic works properly
- ✅ Critical flag `hill_ruins_dungeon_key_obtained` set
- ✅ Location feels complete and polished
- ✅ Save/load preserves all progress

### Red Hollow Mine
- ✅ Five navigable areas functional
- ✅ Progressive difficulty as player descends
- ✅ All combat encounters work properly
- ✅ Ore sample collection works
- ✅ Meredith's ring found and returnable
- ✅ Secret tunnel discovery works
- ✅ Critical flag `red_hollow_mine_secret_entrance_found` set
- ✅ Quest completion with Henrik works
- ✅ Location feels appropriately deep and rewarding
- ✅ Save/load preserves progress at all levels

### Overall Act II Completion
- ✅ All four Act II locations complete:
  - Swamp Church
  - Hill Ruins (Act II reconnaissance)
  - Refugee Camp
  - Red Hollow Mine
- ✅ At least one path to Act III dungeon unlocked
- ✅ All major quests completable
- ✅ Story progression clear and satisfying
- ✅ Players ready to tackle Act III finale

---

## 🎯 ARCHITECTURE NOTES

### Why This Approach Works

**Proven Pattern:**
- Swamp Church established the navigation template
- Hill Ruins validated the copy/modify approach
- Both locations work flawlessly in production

**Minimal Code Changes:**
- No new systems required
- BaseLocation auto-registration handles everything
- Copy/paste/modify is faster than abstraction
- Each location remains independent

**Maintainability:**
- Clear file organization
- Consistent naming conventions
- Self-documenting structure
- Easy for future developers to understand

**Scalability:**
- Pattern works for 2 areas or 5 areas
- Combat integration is plug-and-play
- Searchables and dialogues use same system
- Future locations can use same template

### KISS Principle Applied

**What We're NOT Doing:**
- ❌ Creating generic "ActIILocation" abstract class
- ❌ Over-engineering shared navigation logic
- ❌ Premature optimization for 20+ locations
- ❌ Complex inheritance hierarchies

**What We ARE Doing:**
- ✅ Copy working code
- ✅ Modify for new location
- ✅ Test thoroughly
- ✅ Ship it
- ✅ Refactor later only if needed

---

## 📝 ADR CONSIDERATIONS

**Will We Need an ADR?**

**Probably NOT** - Because:
- Using existing, proven patterns
- No new architectural decisions
- No new systems being created
- Simply applying established templates

**Commit Message Instead:**

For Refugee Camp:
```
Refugee Camp Act II implementation - main camp and interior tent

Complete refugee camp location for Act II with two navigable areas,
brigand raid combat, and dungeon key discovery mechanic. Players
can explore camp, defend against raid, and obtain key through 
dialogue-searchable hunt sequence. Critical flag 
hill_ruins_dungeon_key_obtained enables Act III Path A.

Files Created: 2 map data, 2 nav screens, 7 dialogues, 3 combat files
Integration: Regional map navigation, exploration hub connection
```

For Red Hollow Mine:
```
Red Hollow Mine Act II implementation - 5-level deep mine exploration

Complete Henrik's mine quest with 5 navigable areas (pre-entrance,
levels 1-3, level 2B dead end). Features kobold combat encounters,
ore sample collection, Meredith's ring recovery, and secret tunnel
discovery. Critical flag red_hollow_mine_secret_entrance_found
enables Act III Path B to Hill Ruins dungeon.

Files Created: 5 map data, 4 nav screens, 12 dialogues, 7 combat files
Integration: Henrik quest completion, Meredith quest completion
```

---

## 🎲 FINAL NOTES FOR IMPLEMENTATION

### Before Starting

**Verify Prerequisites:**
- [ ] Swamp Church fully tested and working
- [ ] Hill Ruins fully tested and working
- [ ] Regional map navigation functional
- [ ] BaseLocation auto-registration working
- [ ] Combat system stable
- [ ] Dialogue system stable
- [ ] Loot system stable

### During Implementation

**Best Practices:**
- Copy existing files as templates
- Modify one section at a time
- Test frequently (every 15-30 minutes)
- Use console logging to verify flags
- Save working copies before major changes

### After Completion

**Final Validation:**
- [ ] Both locations playable start to finish
- [ ] All critical flags set properly
- [ ] Act III integration verified
- [ ] Save/load works at all points
- [ ] No console errors or warnings
- [ ] Performance maintained (60 FPS)
- [ ] Code committed with clear messages

---

## 🎬 CONCLUSION

**You've Got This!**

These two locations complete Act II exploration. The pattern is proven, the architecture is solid, and you have working examples to copy from. Take it one location at a time, one area at a time, and test frequently.

**Remember:**
- Copy don't create
- Test don't guess
- Ship don't polish forever
- Trust the pattern

**When in doubt:**
- Look at Swamp Church exterior for navigation examples
- Look at Swamp Church interior for multi-area transitions
- Look at Hill Ruins for ActionHub integration
- Look at existing dialogues for searchable patterns

**The adventure awaits, strategist!** 🎲⚔️

---

*Last Updated: November 3, 2025*  
*Pattern Version: 2.0 (Post Hill Ruins)*  
*Status: Ready for Implementation*
