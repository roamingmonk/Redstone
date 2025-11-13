# Terror in Redstone - Act III Master Implementation Plan

**Document Version:** 1.0  
**Created:** November 12, 2025  
**Status:** Design Complete - Ready for Implementation

---

## Executive Summary

Act III represents the climax of Terror in Redstone, where the player confronts the cult in their underground sanctum. This plan provides complete specifications for implementing the final act, including:

- Two-path dungeon entry system (Mine Tunnel vs. Front Door)
- Five-level dungeon structure with thematic zones
- Chain encounter combat system within existing tactical grid
- Marcus redemption narrative branch
- Dynamic final boss encounter
- Multiple ending variations based on player choices

**Estimated Implementation Time:** 8-12 weeks across multiple development sessions

---

## Table of Contents

1. [Prerequisites & Story State](#prerequisites--story-state)
2. [Phase 1: Town Preparation](#phase-1-town-preparation)
3. [Phase 2: Dungeon Entry Choice](#phase-2-dungeon-entry-choice)
4. [Phase 3: Dungeon Structure](#phase-3-dungeon-structure)
5. [Phase 4: Marcus Confrontation](#phase-4-marcus-confrontation)
6. [Phase 5: Final Boss Battle](#phase-5-final-boss-battle)
7. [Phase 6: Epilogue & Endings](#phase-6-epilogue--endings)
8. [Technical Specifications](#technical-specifications)
9. [Asset Requirements](#asset-requirements)
10. [Testing Checklist](#testing-checklist)

---

## Prerequisites & Story State

### Trigger Conditions
Act III begins when player returns to Redstone after completing Act II investigations.

**Required Flags:**
- `act_three_started = True` (set by Act II completion)
- Player has visited minimum 2 of 4 Act II locations
- `refugee_camp_visited = True` (provides dungeon key for front door path)

**Story Threads to Resolve:**
- Marcus (Cassia's brother) - cult leader
- Mayor's missing family - held captive in dungeon
- Cult's ritual purpose - summon/control ancient entity
- Red Hollow Mine secret tunnel - bypass route

---

## Phase 1: Town Preparation

### Overview
Player returns to Redstone for final preparations. NPCs acknowledge the coming confrontation. Cassia conversation becomes available and is required (but dismissible) before departure.

### Implementation Details

#### 1.1 South Gate Modifications

**File:** `locations/south_gate.py`

**Changes Needed:**
- Add Act III state detection
- Implement soft-blocking dialogue for Cassia requirement
- Unlock new destination: Dungeon Entrance Choice Screen

**Blocking Logic:**
```python
# Pseudo-code structure
if act_three_started and not cassia_discussed_marcus:
    show_message("Cassia seemed troubled when you mentioned Marcus and the cult. 
                  You should speak with her before leaving town.")
    offer_choice([
        "Return to town (recommended)",
        "Leave anyway (dismiss story branch)"
    ])
    if player_chooses_dismiss:
        set_flag('marcus_redemption_dismissed', True)
        set_flag('cassia_discussed_marcus', True)  # Allow departure
```

**New Destination:**
- "Dungeon Approach" - leads to entrance choice screen

#### 1.2 Cassia Dialogue - Marcus Revelation

**File:** `data/narrative/dialogues/cassia_act_three.json`

**New Dialogue State:** `act_three_marcus_warning`

**Trigger Conditions:**
- `act_three_started = True`
- `cassia_discussed_marcus = False`

**Dialogue Flow:**

**Opening:**
"I need to tell you something about Marcus... He's my brother. I thought he died years ago, but now I know the truth. He's leading them - the cult."

**Player Choices:**

**Option A: "I'll try to reason with him."**
- Sets: `cassia_wants_marcus_saved = True`
- Cassia response: "Thank you. He wasn't always like this. Maybe there's still good in him. Please... try."
- Rewards: +1 dialogue skill bonus for Marcus encounter

**Option B: "He's too far gone. I'll do what I must."**
- Sets: `cassia_wants_marcus_saved = False`
- Cassia response: "I understand. Sometimes... sometimes they can't be saved. End this quickly."
- Rewards: +1 combat damage bonus against Marcus

**Option C: "I need time to think about this."**
- Allows player to leave and return
- Dialogue state remains available

**Completion:**
- Sets: `cassia_discussed_marcus = True`
- Unlocks departure via South Gate

#### 1.3 Henrik Dialogue (Optional)

**File:** `data/narrative/dialogues/henrik_act_three.json`

**New Dialogue State:** `henrik_mine_assistance`

**Trigger Conditions:**
- `act_three_started = True`
- `red_hollow_mine_secret_entrance_found = True`

**Purpose:** 
Henrik provides miners' lantern and advice about mine tunnel route.

**Rewards:**
- **Item:** "Miner's Lantern" (provides light in dark mine areas, +2 perception in dungeon)
- **Knowledge:** Warns about cave-ins, suggests supporting pillars

#### 1.4 Bernard/Merchant (Optional)

**Standard merchant functionality - no changes needed.**

Player can purchase final supplies, healing potions, scrolls.

---

## Phase 2: Dungeon Entry Choice

### Overview
Player travels to dungeon location and must choose their approach: Mine Tunnel (recommended, requires prior discovery) or Front Door (harder, always available).

### Implementation Details

#### 2.1 Entrance Choice Screen

**New File:** `locations/dungeon_entrance_choice.py`

**Screen Type:** Menu-based decision point (similar to Act II world map)

**Visual Layout:**
- Background: Hill Ruins exterior (day/dusk lighting)
- Title: "The Cult's Sanctum"
- Two large option buttons

**Option A: Red Hollow Mine Tunnel**

**Availability:** 
```python
if quest_manager.get_flag('red_hollow_mine_secret_entrance_found'):
    enabled = True
else:
    enabled = False
    tooltip = "You haven't discovered the mine's secret tunnel."
```

**Description:**
"Henrik mentioned an old mine tunnel that leads deep underground, bypassing the outer ruins. A shorter path - but you'll need to navigate collapsed passages."

**Mechanical Effects:**
- Start at Dungeon Level 3 (mid-point)
- Skip 5-6 encounters
- Face 3-4 encounters before reaching cult sanctum
- Enters via: `dungeon_mine_entrance.py`

**Option B: Hill Ruins Front Door**

**Availability:** Always available if player has dungeon key

**Requirement Check:**
```python
if item_manager.has_item('dungeon_key'):
    enabled = True
else:
    enabled = False  
    tooltip = "The entrance is sealed. You need a key."
```

**Description:**
"The main entrance to the ancient ruins. The cult entered this way initially, fighting through everything. You'll face the full gauntlet - undead guardians, magical traps, and more."

**Mechanical Effects:**
- Start at Dungeon Level 1 (top)
- Face 8-10 encounters before reaching cult sanctum
- More XP, more loot, significantly harder
- Enters via: `dungeon_front_entrance.py`

**Additional UI Elements:**
- "Return to Town" button (bottom)
- Difficulty indicators (⚔️ symbols: Mine = ⚔️⚔️⚔️, Front = ⚔️⚔️⚔️⚔️⚔️)

#### 2.2 Entry Point Files

**File:** `locations/dungeon_mine_entrance.py`
- First navigation map for mine route
- Dark corridors, cave-in hazards
- Connect to Level 3 convergence point

**File:** `locations/dungeon_front_entrance.py`
- First navigation map for front door route
- Ancient ruins aesthetic
- Connect to Level 1 upper chambers

---

## Phase 3: Dungeon Structure

### Overview
Five-level dungeon with distinct thematic zones. Mine route skips Levels 1-2. Both routes converge at Level 3.

### Zone Breakdown

#### ZONE 1: Ancient Upper Ruins (Levels 1-2)
**Only accessible via Front Door route**

**Theme:** Pre-cult occupation - sealed for centuries

**Why Non-Cult Enemies?**
- These chambers were magically sealed before cult arrived
- Original inhabitants: Undead guardians, constructs, trapped spirits
- Cult uses mine tunnel to bypass this danger
- Serves as "natural defense system" protecting inner sanctum

**Enemy Types:**
1. **Skeleton Warriors** (Common)
   - Ancient tomb guards
   - Weapons: Rusty swords, shields
   - Abilities: Formation tactics, shield wall

2. **Shadow Wraiths** (Uncommon)
   - Trapped souls of original builders
   - Abilities: Phase through walls, life drain, fear aura
   - Weakness: Radiant/holy damage

3. **Animated Armor** (Uncommon)
   - Magical defense constructs
   - Abilities: High armor, counterattack, slow but tough
   - Weakness: Crushing damage, no evasion

4. **Stone Golems** (Rare - Mini-boss)
   - Guardian constructs at key chokepoints
   - Abilities: Earthquake stomp, throw boulders, regenerate
   - Weakness: Lightning, persistent damage

**Environmental Hazards:**
- Pressure plate spike traps
- Magical wards (fire/ice damage)
- Collapsed passages requiring backtracking
- Dark areas (lantern required or perception penalty)

**Level 1 Encounter Chain:**
1. Skeleton patrol (3-4 enemies)
2. Animated armor + skeletons (mixed encounter)
3. Shadow wraith ambush (2 wraiths)
4. Stone golem guarding stairway (mini-boss)

**Level 2 Encounter Chain:**
1. Wraith pack (3 wraiths)
2. Skeleton horde (6-8 skeletons, easy individually)
3. Animated armor room (3 armors, narrow corridor)
4. Stone golem + wraith (boss pair guarding descent)

**Loot Tables:**
- Ancient coins (vendor trash, lore flavor)
- Enchanted weapons (+1 bonuses)
- Dusty spellbooks (learn new spells)
- Protection amulets (found on dead cultist scouts)

#### ZONE 2: Transitional Depths (Level 3)
**Convergence Point - Both routes arrive here**

**Theme:** Where ancient meets cult - mixed occupancy

**Narrative Purpose:**
- Evidence of cult's entry and exploration
- Dead cultists who failed to bypass guardians
- Remaining ancient defenses cult couldn't fully clear
- Signs of recent activity (torches, supplies)

**Enemy Mix:**
1. **Remaining Guardians** (40%)
   - Skeleton captains (tougher variants)
   - Corrupted golems (cult-modified)

2. **Cult Forces** (40%)
   - Cultist acolytes (spellcasters)
   - Cult fanatics (melee fighters)

3. **Cult-Controlled Creatures** (20%)
   - Summoned imps
   - Corrupted wolves/bears

**Encounter Chain:**
1. Cult patrol + skeleton (6 total)
2. Corrupted golem (cult control runes visible)
3. Cultist ambush (spellcasters behind melee line)
4. Mixed force defending passage (4 cultists, 2 guardians)

**Environmental Storytelling:**
- Cult journals describing guardian bypass methods
- Dead cultists with protection amulets (lootable consumables)
- Ritual circles used to control constructs
- Evidence cult lost many people exploring

**Key Discovery:**
"The Warding Chamber" - reveals cult's method:
- Ancient control runes in chamber
- Cult modified runes to command constructs
- Protection ritual details (allows player to use same method)
- **Reward:** "Warding Amulet" schematic (craft consumable that prevents undead aggro)

#### ZONE 3: Cult Sanctum - Upper Level (Level 4)
**Active cult operations**

**Theme:** Fully cult-controlled, living quarters and preparation areas

**Enemy Types:**
1. **Cult Priests** (Common)
   - Mid-level spellcasters
   - Spells: Dark bolt, curse, minor summoning
   - Tactics: Support from rear, heal cultists

2. **Cultist Fanatics** (Common)
   - Melee fighters, unarmored but vicious
   - Abilities: Reckless attack, blood frenzy
   - High damage, low defense

3. **Summoned Lesser Demons** (Uncommon)
   - Imps, quasits
   - Abilities: Flight, ranged attacks, minor spells

4. **Possessed Villagers** (Tragic)
   - Captured townspeople under cult control
   - **Choice:** Kill or knock unconscious (spare option)
   - If spared: Adds to epilogue rescue count

**Encounter Chain:**
1. Guard room (4 fanatics, 2 priests)
2. Summoning chamber (priest + 3 demons in progress)
3. Possessed villager ambush (moral choice encounter)
4. Elite cult guard (2 priests, 4 fanatics, defensive position)

**Environmental Features:**
- Ritual chambers with evidence
- Living quarters with cult notes (lore)
- Torture/interrogation room (grim discovery)
- Supply caches (loot)

**Key Discovery:**
"Prison Cells" - find captives:
- Mayor's family (wife + son if alive based on timing)
- Other villagers
- **Quest Update:** Set rescue flags
- Cannot evacuate until cult defeated

#### ZONE 4: Cult Sanctum - Portal Chamber (Level 5)
**Heart of cult operation**

**Theme:** Final confrontation zone

**This level contains:**
1. Marcus Confrontation (if alive)
2. Final Boss Battle
3. Ritual apparatus
4. Ancient portal/entity

**Layout:**
- Antechamber with approach encounters
- Portal Chamber (main boss arena)
- Secret passage (Marcus escape route)

**Pre-Boss Encounter:**
Elite cult force guarding entrance:
- 3 cult priests
- 4 cult fanatics  
- 2 summoned demons
- **Difficulty:** Hardest regular encounter

### Chain Encounter System

**Implementation:** Within existing tactical combat system

**How It Works:**
1. Player navigates dungeon map (navigation screen)
2. Trigger combat → Load tactical grid → Fight
3. Victory → Return to navigation map at same position
4. Progress forward → Next trigger nearby
5. Repeat for encounter chain

**Benefits:**
- Uses existing combat engine
- Creates "gauntlet" feeling
- Easy to balance and test
- 1-2 weeks implementation vs. 14-20 weeks for full scrollable

**Encounter Spacing:**
- 30-60 seconds of navigation between fights
- Environmental storytelling between encounters
- Healing/rest opportunities at "safe rooms"

### Safe Rooms / Rest Points

**Level 2:** Ancient shrine (full heal, save point)  
**Level 3:** Cult supply cache (limited heal, merchant?)  
**Level 4:** Hidden alcove (full heal, save point)

**Mechanic:**
- One-time use per playthrough
- Player decides when to use
- Strategic resource management

---

## Phase 4: Marcus Confrontation

### Overview
Marcus appears in Portal Chamber before final boss. Player can attempt redemption (if Cassia conversation supports it) or fight immediately.

### Implementation Details

#### 4.1 Encounter Trigger

**Location:** Portal Chamber antechamber (Level 5)

**Trigger:** 
- Player enters chamber
- `cassia_discussed_marcus = True` OR `marcus_redemption_dismissed = True`
- Marcus is alive (not defeated earlier if that's possible)

**Entry:** Marcus appears via dialogue cutscene, not ambush

#### 4.2 Dialogue Exchange

**File:** `data/narrative/dialogues/marcus_confrontation.json`

**Marcus Opening:**
"So Cassia sent you. Or did you come for vengeance? Either way, you're too late. The ritual is almost complete."

**Player Response Branches:**

**Branch A: Redemption Attempt** (Only available if `cassia_wants_marcus_saved = True`)

Player choices for persuasion:
1. "Cassia believes there's still good in you."
   - Skill check: CHA + Persuasion vs DC 16
   
2. "The cult is using you. You're not their leader - you're their tool."
   - Skill check: INT + Insight vs DC 14
   
3. "Your sister mourns you every day. Come home."
   - Automatic success if player found Cassia's locket in earlier content

**Redemption Success:**
- Marcus stands down
- Provides information about final boss weakness
- Joins as temporary ally for final battle (controlled by AI)
- Sets: `marcus_redeemed = True`
- After final boss victory, Marcus uses secret passage to escape
- Cassia reunion in epilogue

**Redemption Failure:**
- Marcus: "You don't understand. You CAN'T understand."
- Proceeds to combat (Branch B)
- If defeated → `marcus_defeated_combat = True`

**Branch B: Combat Immediately**

Player choices to attack:
1. "Cassia will mourn, but I'll end this." (if Cassia conversation happened)
2. "Your cult dies today, starting with you." (aggressive)
3. [ATTACK] (no dialogue)

Proceeds to combat encounter.

#### 4.3 Marcus Combat Encounter

**If Marcus fights:**

**Marcus Stats:**
- Level 8 Cult Ritualist
- HP: 85
- AC: 14 (robes + magic shield)
- High INT, moderate DEX, low STR

**Abilities:**
- **Dark Bolt:** Ranged spell attack, 2d8 necrotic
- **Summon Guardian:** Calls 1d3 lesser demons (once per combat)
- **Cursed Ground:** AOE that damages + slows in 3x3 area
- **Ritual Shield:** Reaction to reduce damage (3/day)
- **Desperate Flight:** At 25% HP, attempts to flee

**Combat Tactics:**
- Stays at range
- Summons demons early as meat shields
- Uses cursed ground to control space
- Flees via secret passage at low HP (player can kill or let escape)

**Escape Mechanic:**
At 25% HP (21 HP):
- Marcus moves toward secret passage door
- Player can pursue and finish him OR let him go
- If killed: `marcus_killed = True`
- If escapes: `marcus_escaped = True`

**Loot (if killed):**
- Ritual Dagger (+2, necrotic damage)
- Cult Leader's Robes (AC bonus, INT boost)
- Key to prison cells (if not found earlier)

#### 4.4 Secret Passage

**Location:** Behind altar in Portal Chamber

**Properties:**
- One-way door (cannot open from Hill Ruins surface)
- Marcus uses this regardless of outcome
- Leads to Hill Ruins exterior
- If player tries to use it: "This passage only opens from below. It's an escape route, not an entrance."

**Narrative Purpose:**
- Explains how Marcus/cultists could navigate safely (bypass Zones 1-2)
- Provides escape for Marcus if redeemed or if he flees
- Cannot be exploited by player

---

## Phase 5: Final Boss Battle

### Overview
Cult leader's final ritual with dynamic difficulty based on Marcus outcome. Boss can summon entities and use lair actions.

### Implementation Details

#### 5.1 Boss Composition

**Primary Boss: Cult Leader (Archon Malachar)**

**Base Stats:**
- Level 10 Dark Ritualist
- HP: 150
- AC: 16 (magical robes, shield spell)
- High INT, WIS, moderate DEX

**Spells & Abilities:**

**Core Attacks:**
- **Void Lance:** Ranged attack, 3d8 + 4 force damage, 60ft range
- **Mass Curse:** AOE debuff, -2 to all saves, 4 turn duration
- **Soul Drain:** Melee touch, 2d10 necrotic, heals Malachar for half damage

**Summoning:**
- **Summon Entity (1/combat):** Calls major demon/aberration (see below)
- **Lesser Summons (unlimited):** 1d4 imps/cultist spirits each turn (action cost)

**Defensive:**
- **Shield (Reaction):** +5 AC vs one attack
- **Counterspell:** Interrupt player spell casting
- **Misty Step (Bonus):** Teleport 30ft, avoid melee

**Lair Actions (Every 2 turns):**
Portal Chamber is active ritual site - environment is hostile:

1. **Rift Tear:** Random 3x3 area takes 2d6 force damage, becomes difficult terrain
2. **Shadow Tendrils:** 3 random party members must make DEX save or be restrained (1 turn)
3. **Dark Surge:** All enemies gain +2 damage and +10 temp HP

#### 5.2 Marcus Factor

**If Marcus was defeated/killed earlier:**

Malachar opens: "Fool! You killed my lieutenant. Now I must draw upon the entity directly!"

**Difficulty Increase:**
- Malachar immediately summons Greater Entity (Phase 2 starts immediately)
- Malachar +25 HP (starts at 175)
- Lair actions every turn instead of every 2 turns

**If Marcus was redeemed:**

Marcus fights ALONGSIDE player as temporary ally.

**Marcus Ally Stats:**
- HP: 65 (injured from earlier if fought)
- Provides magical support
- Casts healing spells on party
- Knows Malachar's tactics, warns player before lair actions
- **Advantage:** Removes one lair action (Marcus counters ritual)

**If Marcus dismissed (didn't engage story):**
- Standard fight (base difficulty)
- No modifications

#### 5.3 Boss Phases

**Phase 1: Malachar Alone (100%-50% HP)**

**Tactics:**
- Ranged spell attacks
- Summons lesser entities for meat shields
- Uses misty step to maintain distance
- Casts mass curse when party clusters

**Phase 2: Summoned Entity (50%-0% HP)**

**At 50% HP trigger:**
"Witness the power beyond the veil! Come forth, devourer of worlds!"

**Malachar summons one of these entities (random or designer choice):**

**Option A: Voidspawn Aberration**
- HP: 75
- Abilities: Tentacle attacks, mind blast (AOE confusion), regeneration

**Option B: Greater Demon**
- HP: 90
- Abilities: Flame aura (passive AOE), multiattack, flight

**Option C: Corrupted Guardian**
- HP: 100  
- Abilities: High AC, bash attack, stunning blow

**Phase 2 Tactics:**
- Malachar focuses on spellcasting support
- Entity engages melee fighters
- Coordinated attacks (entity grabs, Malachar nukes)
- Lair actions continue

**Victory Condition:**
Defeat both Malachar AND summoned entity.

#### 5.4 Combat Arena

**Portal Chamber Layout:**

```
╔═══════════════════════════════════╗
║  [Altar]  [PORTAL]  [Altar]      ║
║                                   ║
║    (Rift)          (Rift)        ║
║                                   ║
║  [Pillar]                [Pillar]║
║                                   ║
║         [Malachar Start]          ║
║                                   ║
║  [Entry]──────────────────────   ║
╚═══════════════════════════════════╝
```

**Tactical Elements:**
- Pillars provide cover from ranged attacks
- Altars are destructible (explosion deals AOE damage)
- Portal is active (visual effect, no mechanical impact during combat)
- Rifts are hazardous terrain (periodic lair actions)

**Size:** 24x20 tactical grid (larger than normal combats)

---

## Phase 6: Epilogue & Endings

### Overview
Victory sequence with outcomes based on player choices throughout campaign. Multiple narrative variations.

### Implementation Details

#### 6.1 Immediate Post-Victory

**Portal Chamber Resolution:**

1. **Portal Stabilization:**
   - Portal begins to collapse
   - Automatic check: INT + Arcana to control collapse
   - Success: Graceful shutdown
   - Failure: Explosive shutdown (minor damage, no real penalty)

2. **Prisoner Rescue:**
   - Rescue flags checked: `mayor_family_rescued`, `villagers_rescued`
   - Escort NPCs back through dungeon (auto-succeed)

3. **Marcus Outcome:**
   - If redeemed: Marcus leaves via secret passage (avoid arrest)
   - If killed: Body found by authorities
   - If escaped earlier: No body, mystery remains

#### 6.2 Return to Redstone

**New Screen:** `locations/epilogue_town_celebration.py`

**Visual:** Town square celebration, NPCs gathered

**Variations Based on Outcomes:**

**Mayor's Family:**
- **Alive:** Mayor publicly thanks you, modest reward (500 gold)
- **Dead:** Somber ceremony, Mayor offers entire treasury (1000 gold + magic item)

**Marcus & Cassia:**
- **Marcus redeemed:** Cassia reunion (off-screen, mentioned), relief and gratitude
- **Marcus killed:** Cassia mourns but understands, bittersweet
- **Marcus escaped:** Cassia holds out hope, ambiguous ending
- **Marcus dismissed:** Cassia never learns truth, remains troubled

**Villagers Saved:**
- Count of rescued NPCs
- Each rescued villager provides small reward (50 gold, items)
- High rescue count: Town wide celebration
- Low rescue count: Muted victory

**Henrik (if mine route used):**
- Thanks for using mine
- Offers partnership for reopening (flavor text)

#### 6.3 Ending Slides

**Format:** Text screens with narration (similar to Fallout)

**Slide Sequence:**

**Slide 1: Victory Announcement**
"The cult of Redstone has been vanquished. The darkness that plagued the valley has lifted."

**Slide 2: Mayor's Family**
- Reunited: "Mayor Elsworth's family returned safely. His son will carry forward the family legacy."
- Partial: "Not all of the Mayor's family survived. He carries the weight of loss."
- Lost: "The Mayor's family perished in captivity. He resigned from office, grief-stricken."

**Slide 3: Rescued Captives**
"XX villagers were rescued from the cult's prison. They return to their families, forever changed by their ordeal."

**Slide 4: Marcus Resolution**
- Redeemed: "Marcus disappeared after the battle. Some say Cassia still receives letters from a distant land."
- Killed: "Marcus fell defending his twisted faith. Cassia holds a private memorial."
- Escaped: "Marcus remains at large. Authorities search, but Cassia hopes he found peace."
- Unknown: "The cult leader's identity was never confirmed. Some questions remain unanswered."

**Slide 5: Party's Legacy**
"Your deeds became legend in the valley. Bards sing of the [party name] who saved Redstone from the encroaching darkness."

**Slide 6: Personal Epilogues**
- Individual party member futures (class-based flavor)
- Example: "Lyra the wizard returned to her studies, her spellbook richer with forbidden knowledge."

**Slide 7: Redstone's Future**
- Optimistic (most choices favorable): "Redstone prospers, the dark times behind them."
- Mixed: "Redstone rebuilds slowly, scars from the cult's influence still visible."
- Dark (many bad outcomes): "Redstone survives, but never fully recovers. Some wounds don't heal."

#### 6.4 Credits & Post-Game

**Credits Screen:**
- Development credits
- Special thanks
- Music/art attribution

**Post-Credits:**
- Option to "Continue Playing" (return to town, post-game state)
- Option to "New Game+" (if implemented)
- Option to "Main Menu"

**Post-Game State (if continue):**
- Merchant unlocks special items (cult loot for sale)
- NPCs have new dialogue reflecting victory
- Dungeon becomes optional "practice" zone
- No new story content (completionist cleanup)

---

## Technical Specifications

### Flag System Requirements

**New Flags to Implement:**

**Act III Progression:**
- `act_three_started` (bool) - Triggers Act III content
- `act_three_entrance_choice` (string) - "mine" or "front_door"
- `dungeon_level_current` (int) - Tracks current dungeon level
- `dungeon_zone_current` (string) - Tracks thematic zone

**Marcus Storyline:**
- `cassia_discussed_marcus` (bool) - Required for departure
- `cassia_wants_marcus_saved` (bool) - Player chose redemption path
- `marcus_redemption_dismissed` (bool) - Player dismissed storyline
- `marcus_redemption_attempted` (bool) - Player tried to redeem
- `marcus_redeemed` (bool) - Success!
- `marcus_defeated_combat` (bool) - Fought and defeated
- `marcus_killed` (bool) - Player killed him vs. let escape
- `marcus_escaped` (bool) - Marcus fled via passage

**Dungeon Progress:**
- `dungeon_level_1_complete` (bool)
- `dungeon_level_2_complete` (bool)
- `dungeon_level_3_complete` (bool)
- `dungeon_level_4_complete` (bool)
- `dungeon_level_5_complete` (bool)
- `safe_room_1_used` (bool) - Level 2 shrine
- `safe_room_2_used` (bool) - Level 3 cache
- `safe_room_3_used` (bool) - Level 4 alcove

**Rescue & Outcomes:**
- `mayor_family_rescued` (bool)
- `mayor_son_alive` (bool)
- `villagers_rescued_count` (int) - Number saved
- `possessed_villagers_spared` (int) - Moral choice tracking

**Final Boss:**
- `malachar_defeated` (bool)
- `entity_defeated` (bool)
- `portal_destroyed` (bool)
- `marcus_ally_in_final_battle` (bool)

### Combat Encounter Definitions

**Create JSON files for each encounter:**

**File Structure:**
```
data/combat/encounters/act_three/
├── level_1_skeleton_patrol.json
├── level_1_animated_armor.json
├── level_1_wraith_ambush.json
├── level_1_stone_golem_boss.json
├── ... (continue for all levels)
├── marcus_confrontation.json
├── final_boss_malachar.json
└── final_boss_entity_options.json
```

**Encounter JSON Schema:**
```json
{
  "encounter_id": "level_1_skeleton_patrol",
  "location": "Dungeon Level 1 - Corridor",
  "difficulty": 3,
  "enemies": [
    {
      "type": "skeleton_warrior",
      "count": 3,
      "level": 4,
      "positions": [[2, 8], [3, 8], [4, 8]]
    },
    {
      "type": "skeleton_archer",
      "count": 1,
      "level": 4,
      "positions": [[3, 10]]
    }
  ],
  "terrain_features": [
    {"type": "pillar", "position": [6, 6], "provides_cover": true},
    {"type": "rubble", "position": [8, 8], "difficult_terrain": true}
  ],
  "loot": {
    "guaranteed": ["ancient_coin"],
    "random": [
      {"item": "rusty_sword", "chance": 0.3},
      {"item": "health_potion", "chance": 0.5}
    ]
  },
  "xp_reward": 250,
  "next_encounter": "level_1_animated_armor"
}
```

### New Location Files Required

**Dungeon Navigation Maps:**
1. `locations/dungeon_mine_entrance.py` - Mine start point
2. `locations/dungeon_front_entrance.py` - Front door start
3. `locations/dungeon_level_1_map_a.py` - Upper ruins section A
4. `locations/dungeon_level_1_map_b.py` - Upper ruins section B
5. `locations/dungeon_level_2_map.py` - Lower ruins
6. `locations/dungeon_level_3_map.py` - Convergence zone
7. `locations/dungeon_level_4_map.py` - Cult sanctum upper
8. `locations/dungeon_level_5_portal_chamber.py` - Final area
9. `locations/epilogue_town_celebration.py` - Victory scene

**Choice/Dialogue Screens:**
1. `locations/dungeon_entrance_choice.py` - Route selection
2. `screens/epilogue_slides.py` - Ending narration

### Chain Encounter System Implementation

**Pseudo-code structure:**

```python
class DungeonNavigationMap(BaseLocation):
    def __init__(self):
        self.encounters = self.load_encounter_chain()
        self.current_encounter_index = 0
        self.encounter_triggers = self.setup_triggers()
    
    def setup_triggers(self):
        # Place invisible trigger zones on map
        # When player enters trigger -> launch combat
        return triggers
    
    def on_trigger_activated(self, trigger_id):
        encounter_data = self.encounters[self.current_encounter_index]
        self.launch_combat(encounter_data)
    
    def on_combat_victory(self):
        self.current_encounter_index += 1
        # Mark trigger as used (don't re-trigger)
        # Return player to map at same position
        if self.all_encounters_complete():
            self.unlock_next_level()
```

**Key Features:**
- Encounters load from JSON definitions
- Triggers placed at strategic map positions
- After combat victory, return to navigation map
- Progress tracking prevents re-triggering
- Final encounter unlocks progression to next level

### Save System Integration

**Add to save file schema:**

```json
{
  "act_three_state": {
    "started": bool,
    "entrance_choice": string,
    "current_dungeon_level": int,
    "encounters_completed": [],
    "marcus_outcome": string,
    "boss_defeated": bool
  },
  "epilogue_variables": {
    "mayor_family_rescued": bool,
    "villagers_rescued": int,
    "ending_variant": string
  }
}
```

---

## Asset Requirements

### Graphics Assets

**Dungeon Tilesets:**
- Ancient ruins tiles (stone, pillars, rubble)
- Mine tunnel tiles (rough hewn, supports, cave-ins)
- Cult sanctum tiles (ritual circles, altars, banners)

**Enemy Sprites:**
- Skeleton warrior (sword/shield)
- Skeleton archer
- Shadow wraith (transparent/ghostly)
- Animated armor (various types)
- Stone golem
- Cult priest (robed)
- Cult fanatic (ragged, aggressive)
- Lesser demon variations
- Marcus (unique sprite)
- Malachar (boss sprite)
- Greater entity (final boss ally)

**UI Elements:**
- Dungeon entrance choice buttons
- Ending slide backgrounds
- Victory celebration screen

**VFX:**
- Portal animation (swirling energy)
- Lair action effects (rift tears, tendrils, surges)
- Spell effects (dark bolt, void lance, etc.)

### Audio Assets

**Music Tracks:**
- Dungeon ambient (per zone)
- Marcus confrontation theme
- Final boss battle theme (epic)
- Victory celebration theme
- Epilogue theme (bittersweet)

**Sound Effects:**
- Dungeon ambience (dripping water, echoes)
- Skeleton clattering
- Wraith wails
- Golem stomps
- Portal hum
- Cult chanting
- Boss abilities (void lance, summon, etc.)

### Dialogue & Text

**JSON Files:**
- `cassia_act_three.json` (~500 words)
- `henrik_mine_assistance.json` (~200 words)
- `marcus_confrontation.json` (~800 words, branching)
- `malachar_boss_taunts.json` (~300 words, combat barks)
- `epilogue_slides_text.json` (~1500 words, variations)

**NPC Reactions:**
- Post-victory dialogue for all Act I/II NPCs (~100 words each)

---

## Testing Checklist

### Functional Testing

**Phase 1: Town Preparation**
- [ ] Act III flag properly triggers new content
- [ ] South Gate blocks departure without Cassia talk (can be dismissed)
- [ ] Cassia dialogue sets correct flags
- [ ] Henrik dialogue provides lantern (if mine discovered)
- [ ] Departure allowed after Cassia conversation OR dismissal

**Phase 2: Entrance Choice**
- [ ] Mine tunnel option only available if discovered
- [ ] Front door option only available with dungeon key
- [ ] Choice screen properly routes to correct start point
- [ ] Return to town button works

**Phase 3: Dungeon Structure**
- [ ] Mine route starts at Level 3
- [ ] Front door route starts at Level 1
- [ ] Encounter triggers fire correctly
- [ ] Combat loads proper encounter data
- [ ] Victory returns to navigation map
- [ ] Chain encounters progress in order
- [ ] Safe rooms work (one-time use, full heal)
- [ ] Level progression gates work
- [ ] Both routes converge at Level 3

**Phase 4: Marcus Confrontation**
- [ ] Marcus appears at correct trigger
- [ ] Redemption path only available if flag set
- [ ] Persuasion checks work correctly
- [ ] Combat stats balanced
- [ ] Marcus flees at 25% HP (can be killed)
- [ ] Outcomes set correct flags
- [ ] Marcus ally in final battle (if redeemed)

**Phase 5: Final Boss**
- [ ] Malachar stats correct
- [ ] Lair actions trigger on schedule
- [ ] Summoning mechanics work
- [ ] Phase 2 triggers at 50% HP
- [ ] Difficulty modifiers apply correctly (Marcus factor)
- [ ] Victory properly detected (both enemies defeated)

**Phase 6: Epilogue**
- [ ] Rescue flags checked correctly
- [ ] Ending slides display proper variations
- [ ] NPC dialogue reflects outcomes
- [ ] Post-game state allows continued play
- [ ] Credits screen accessible

### Balance Testing

**Combat Difficulty:**
- [ ] Level 1-2 encounters (front door): Appropriate for party entering Act III
- [ ] Level 3 encounters: Moderate difficulty, both routes balanced
- [ ] Level 4 encounters: Challenging but fair
- [ ] Marcus fight: Tough but not overwhelming
- [ ] Final boss: Epic difficulty, requires strategy

**Pacing:**
- [ ] Mine route: ~45-60 min from entry to boss
- [ ] Front door route: ~90-120 min from entry to boss
- [ ] Encounter spacing feels appropriate (not overwhelming)
- [ ] Safe rooms positioned well

**Rewards:**
- [ ] Loot progression appropriate for difficulty
- [ ] XP gains scale properly
- [ ] Unique rewards for optional content
- [ ] Boss loot feels epic

### Edge Case Testing

- [ ] Player saves mid-dungeon → Loads correctly
- [ ] Player dies in combat → Respawn works
- [ ] Player backtracks in dungeon → No issues
- [ ] Player tries to exploit safe rooms → One-time limit enforced
- [ ] All flag combinations tested (Marcus outcomes, rescue variations)
- [ ] Post-game state: Dungeon accessible again?

### Narrative Testing

- [ ] All dialogue branches accessible
- [ ] Marcus story makes sense in all variations
- [ ] Epilogue slides match player choices
- [ ] No orphaned flags or dead-end states
- [ ] Cassia's story arc resolves appropriately

---

## Implementation Roadmap

**Recommended Session Breakdown:**

### Session 1: Foundation (4-6 hours)
- Implement South Gate Act III routing
- Create Cassia Act III dialogue
- Create Henrik optional dialogue
- Test departure mechanics
- **ADR Required:** "Act III Entry Requirements"

### Session 2: Entrance Choice (3-4 hours)
- Build dungeon entrance choice screen
- Implement conditional routing
- Create mine entrance and front door entry maps
- Test navigation
- **ADR Required:** "Two-Path Dungeon Design"

### Session 3-4: Dungeon Levels 1-2 (8-10 hours)
- Build navigation maps (Level 1A, 1B, 2)
- Create encounter JSON definitions
- Implement chain encounter triggers
- Test combat flow
- Balance difficulty
- **ADR Required:** "Chain Encounter System"

### Session 5: Dungeon Level 3 (4-6 hours)
- Build convergence navigation map
- Create mixed encounter definitions
- Implement route merging logic
- Environmental storytelling elements
- **ADR Required:** None (covered by previous)

### Session 6-7: Dungeon Levels 4-5 (6-8 hours)
- Build cult sanctum navigation maps
- Create portal chamber map
- Implement prison rescue mechanics
- Possessed villager moral choice
- **ADR Required:** "Moral Choice Combat Mechanics"

### Session 8: Marcus Confrontation (5-7 hours)
- Create Marcus dialogue tree
- Implement redemption mechanics
- Build Marcus combat encounter
- Test all outcome branches
- Secret passage implementation
- **ADR Required:** "Marcus Redemption System"

### Session 9-10: Final Boss (8-10 hours)
- Build Malachar combat encounter
- Implement summoning mechanics
- Create lair action system
- Build portal chamber combat arena
- Balance boss fight difficulty
- Test Marcus ally integration
- **ADR Required:** "Dynamic Boss Difficulty System"

### Session 11: Epilogue (4-6 hours)
- Create ending slide system
- Implement outcome variations
- Build post-victory town scene
- Create post-game state
- **ADR Required:** "Epilogue Branching System"

### Session 12: Polish & Testing (6-8 hours)
- Full playthrough testing (both routes)
- Balance adjustments
- Bug fixes
- Edge case testing
- **Final ADR:** "Act III Complete - Lessons Learned"

**Total Estimated Time:** 60-80 hours across 12 sessions

---

## Design Philosophy Notes

**For Developers Working on Act III:**

### Maintain Authentic CRPG Feel
- Challenge should come from tactics, not cheap tricks
- Give players information to make informed choices
- Reward exploration and experimentation
- Environmental storytelling > exposition dumps

### Respect Player Agency
- Marcus redemption should feel earned, not guaranteed
- Moral choices have weight but no "right" answer
- Multiple paths are legitimately different, not fake choice
- Consequences matter but don't punish "wrong" choices

### Dungeon Design Principles
- Telegraph danger before springing it
- Safe rooms are strategic resources, not freebies
- Loot rewards curiosity and thoroughness
- Environmental hazards teach mechanics before combat uses them

### Balance Philosophy
- Mine route should feel smart, not cheap
- Front door should feel epic, not punishing
- Final boss is tough but fair (information + skill = victory)
- Death teaches lessons, not frustration

### Technical Debt Awareness
- Chain encounters are a compromise (not perfect, but workable)
- Secret passage is narrative device (don't overthink mechanics)
- Flag system must stay maintainable (avoid combinatorial explosion)
- Save compatibility is non-negotiable

---

## Appendix: Quick Reference

### Critical Flags
```
act_three_started
cassia_discussed_marcus
marcus_redeemed / marcus_killed / marcus_escaped
dungeon_level_current
malachar_defeated
```

### Key Files
```
locations/south_gate.py - Act III departure
locations/dungeon_entrance_choice.py - Route selection
data/narrative/dialogues/cassia_act_three.json
data/narrative/dialogues/marcus_confrontation.json
data/combat/encounters/act_three/*.json
screens/epilogue_slides.py
```

### Difficulty Tiers
- Mine Route: Moderate (⚔️⚔️⚔️)
- Front Door: Hard (⚔️⚔️⚔️⚔️⚔️)
- Marcus (if fought): Hard (⚔️⚔️⚔️⚔️)
- Final Boss (base): Very Hard (⚔️⚔️⚔️⚔️⚔️)
- Final Boss (Marcus killed): Epic (⚔️⚔️⚔️⚔️⚔️⚔️)

---

## Closing Notes

This document represents the complete design specification for Act III. Any developer (Claude session or human) picking up this work should:

1. Read this document thoroughly
2. Reference existing Act I/II patterns
3. Maintain architectural consistency
4. Test extensively (both routes!)
5. Update ADRs for major decisions
6. Document deviations from this plan

**Good luck, and may your dice rolls be high! 🎲**

---

**End of Document**