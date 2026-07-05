# Terror in Redstone — Copy-Paste Task Prompts
# Apr 30, 2026 | Baseline Completion Sprint
#
# HOW TO USE:
#   VS Code edits  → copy the block, paste into the Claude extension chat panel
#   Claude Code    → copy the block, paste as your first message in a new session
#   Claude.ai      → planning and narrative writing sessions
#   Each block is self-contained — no other context needed.
#
# LEGEND:
#   [VS CODE]     = Simple edit, use Claude extension in VS Code
#   [CLAUDE CODE] = Multi-file or logic fix, use Claude Code terminal
#   [CLAUDE.AI]   = Planning, narrative writing, or design discussion
#   [PLAN FIRST]  = Read the planning note before coding
#
# PRIORITY ORDER:
#   Section A — Progression (blockers — do first, these unlock playtesting)
#   Section B — Level & Class System
#   Section C — Quest & Item Cleanup
#   Section D — Remaining UX / Polish from Feb run-through
#   Section E — Cavia Narrative Content
#   Section F — Graphics Pass
#   Section G — Audio (do last)
#
# STATUS KEY:
#   <blank>                    = Not started
#   <IN PROGRESS>              = Active work
#   <COMPLETED>                = Done and verified
#   <COMPLETED — DEVIATION: …> = Done but diverged from plan; note explains what changed
#
# ─────────────────────────────────────────────────────────────────────────────
# POST-SESSION PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# After every [CLAUDE CODE] session:
#   1. Mark each finished task <COMPLETED> (or <COMPLETED — DEVIATION: note>)
#   2. If you deviated, update any future tasks whose context is now wrong
#   3. If you hit a blocker, mark the task <IN PROGRESS> and add a note
#
# After finishing a full section, run the Section Review prompt below before
# starting the next section. Deviations compound — catch them early.
#
# ─────────────────────────────────────────────────────────────────────────────
# COPY-PASTE PROMPTS FOR POST-SESSION WORK
# ─────────────────────────────────────────────────────────────────────────────
#
# ── TASK MARK-UP (paste into Claude Code at end of session) ──────────────────
# ```
# I just finished a work session on Terror in Redstone.
# Here is the current state of my task list from docs/Redstone_CopyPaste_Prompts_Apr30.md:
#
# [PASTE THE RELEVANT TASK BLOCKS HERE — completed and any in-progress ones]
#
# For each completed task: confirm the status marker is correct.
# For any deviation noted: check whether any future task in this document
# depends on the original approach and update its context block if so.
# Show me only the lines that need to change.
# ```
#
# ── SECTION REVIEW (paste into Claude.ai after finishing a full section) ──────
# ```
# I'm working through docs/Redstone_CopyPaste_Prompts_Apr30.md for my Python/Pygame
# CRPG Terror in Redstone. I just completed Section [X].
#
# Here is what changed from the plan during that section:
# [PASTE YOUR DEVIATION NOTES HERE]
#
# Here are the remaining sections I haven't started yet:
# [PASTE REMAINING SECTION HEADERS + TASK TITLES]
#
# Question: Do any of the remaining tasks need their context or approach updated
# based on what changed? List only the ones that need edits, and show the
# exact text to change.
# ```
#
# ── FULL PLAN SYNC (paste into Claude Code if things have drifted significantly) 
# ```
# I need a consistency check on my sprint plan for Terror in Redstone.
# Plan doc: docs/Redstone_CopyPaste_Prompts_Apr30.md
# ADR log:  docs/decisions.md
#
# Please read both files and tell me:
# 1. Any task whose approach contradicts a decision recorded in decisions.md
# 2. Any task marked <COMPLETED> that may have been partially undone by a later task
# 3. Any task whose key files no longer exist or have been renamed
#
# Report as a short bullet list. Do not rewrite the tasks — just flag the issues.
# ```
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════
# SECTION A — PROGRESSION BLOCKERS
# Must be done before playtesting can verify the full game loop.
# ═══════════════════════════════════════════════════════════════

## A-01 [CLAUDE CODE] — Collapse XP requirements to 3-level curve  ⚠️ BLOCKER
<Completed>

```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: The game is designed as a tight 4-6 hour experience with a
3-level progression cap (Level 1 → 2 → 3). However, the XP curve in
narrative_schema.json still uses the old 5-level curve:
  [0, 300, 900, 2700, 6500]

TARGET XP CURVE:
  Level 1: 0 XP (start)
  Level 2: 300 XP (end of Act I — recruit party + rat basement)
  Level 3: 1000 XP (mid Act II — 2-3 location completions)

TASK:
1. Open data/narrative_schema.json
2. Find the "level_progression" section inside "xp_balance"
3. Change "requirements" from [0, 300, 900, 2700, 6500]
   to [0, 300, 1000]
4. Update the "comment" field to reflect the new 3-level design
5. Verify that game_logic/character_engine.py reads this field
   correctly — find where _level_requirements is set (around line 37)
   and confirm it uses the "requirements" array, not a hardcode

Do NOT change the combat_progression arrays in character_classes.json
yet — that is a separate task (B-01).

Read both files first and show me the exact changes before saving.
```

---

## A-02 [CLAUDE CODE] — Wire combat XP rewards to floating indicator  ⚠️ BLOCKER
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: Combat victory correctly emits XP_AWARDED events via
game_logic/combat_engine.py (_award_rewards method, ~line 2986).
Character_engine handles XP_AWARDED and awards XP + shows a floating
notification. Gold is also awarded but shows NO floating indicator —
only an add to game_state.character['gold'].

VERIFICATION NEEDED:
1. Confirm the full chain works end-to-end:
   - combat_engine._award_rewards() emits XP_AWARDED ✓ (confirmed in code)
   - character_engine._handle_xp_award() receives it and updates XP
   - The floating notification (ui/notifications.py) fires for XP
   
2. Add a floating "+N gold" indicator on gold award, matching the XP 
   notification style. Gold is awarded in _award_rewards() around the
   "gold = rewards.get('gold', 0)" block.

3. Verify with the tavern_basement_rats encounter:
   data/combat/encounters/tavern_basement_rats.json shows:
     rewards: { xp: 50, gold: 25 }
   After combat victory, player should see "+50 XP" and "+25 Gold"
   floating indicators.

KEY FILES:
- game_logic/combat_engine.py  (~line 2986, _award_rewards)
- game_logic/character_engine.py  (_handle_xp_award method)
- ui/notifications.py  (floating indicator system)

Read all three files. Trace the XP flow first. If XP notifications
already work, only add the gold indicator. Show me what you find
before making changes.
```

---

## A-03 [CLAUDE CODE] — Verify level-up triggers after combat XP  ⚠️ BLOCKER

<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: After fixing the XP curve to 3 levels (task A-01), we need
to confirm that level-up actually fires at the right thresholds during
normal gameplay, not just in theory.

TASK:
1. Trace the full level-up sequence:
   a. character_engine._handle_xp_award() awards XP
   b. It calls can_level_up() to check threshold
   c. If yes, it should either auto-level or prompt the player
   
   Read character_engine.py around can_level_up() and level_up()
   (approximately lines 1098–1202) — does level-up happen automatically
   or does it require a player action?

2. If level-up requires player action, verify there is a visible
   prompt or notification telling the player they can level up.
   The yellow portrait border task (Feb26 doc, C-18) addresses this
   visually — confirm it is implemented.

3. Verify level_up() actually updates the character's:
   - Level field
   - Max HP (using hit_die from character_classes.json)
   - Attack bonus (from combat_progression array)
   If any of these are not updated, note which ones are missing.

4. Test checklist to walk through manually (do NOT automate):
   - Start new game as Fighter
   - Complete rat basement (50 XP)
   - Recruit 3 party members (should give ~225 XP total from
     recruitment_bonus + discovery_base in xp_balance)
   - Verify total ~375 XP → level 2 triggers

Read character_engine.py first. Report what you find.
Do not make code changes without showing me the gap first.
```


## A-04 [CLAUDE CODE] — Calibrate all XP award values  ⚠️ BLOCKER

<Completed-Deviated>
Post-game Level 4: set character level to 4 on boss victory as a
cosmetic capstone reward. Not a gameplay level — no class data needed.

```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: The XP level thresholds are being cut to [0, 300, 1000] for a
3-level cap (task A-01). However the XP awards themselves are badly
miscalibrated from testing — they will blow past those thresholds far
too quickly. This task recalibrates every XP source so the pacing
matches the narrative arc.

---
TARGET PACING:
  Level 2 (300 XP) — end of Act I
    Player has: accepted mayor quest, cleared rat basement,
    recruited all 3 party members.
  Level 3 (1000 XP) — mid Act II
    Player has: completed 2-3 of the 4 Act II locations
    (Hill Ruins, Mine, Swamp, Refugee Camp).
  The dungeon (Act III) should be entered at Level 3.

---
PROBLEMS FOUND (read the code to verify these before changing):

1. RECRUITMENT XP IS INCONSISTENT AND INFLATED
   In data/narrative_schema.json → quest_triggers → party_recruitment_triggers:
   - gareth_recruited uses "recruitment_bonus" (20 XP) ← correct
   - elara_recruited uses "quest_multipliers.secondary" (150 XP) ← test value
   - thorman_recruited uses "quest_multipliers.secondary" (150 XP) ← test value
   - lyra_recruited uses "quest_multipliers.secondary" (150 XP) ← test value
   All 4 recruits should give the same amount. Target: 30 XP each.

2. QUEST COMPLETION MULTIPLIERS ARE INFLATED
   In data/narrative_schema.json → xp_balance → quest_multipliers:
   - main_story: 20.0  →  base(50) × 20 = 1000 XP for one flag ← test value
   - secondary: 3.0    →  base(50) × 3  = 150 XP per secondary quest
   - investigation: 3.0 → same
   - side_task: 3.0    →  same
   These multipliers apply every time a trigger fires using that key.
   The multipliers need to drop significantly.

3. DISCOVERY XP FIRES TOO MANY TIMES
   "discovery_base" (50 XP) is used for many triggers — learning about
   each location, each detail about a location, each minor NPC fact.
   This stacks up invisibly. Target: 10-15 XP per discovery.

4. TWO HARDCODED VALUES IN TRIGGERS:
   - casper_redemption_complete: xp=200  (a single side quest giving 200 XP)
   - meredith_ring_direct_return: xp=100
   These are hardcoded integers in the trigger, not using the multiplier
   system. They need to be reduced to fit the budget.

---
PROPOSED RECALIBRATED VALUES:
(Read the code to verify these make sense before applying)

xp_balance in narrative_schema.json:
  discovery_base: 10      (was 50 — fires very frequently)
  recruitment_bonus: 30   (was 20 — used for each recruit, target 30 each)
  base_quest_xp: 25       (was 50 — the base that multipliers multiply)
  quest_multipliers:
    main_story: 4.0       (was 20.0 — main story flag = 100 XP, not 1000)
    secondary: 3.0        (was 3.0 — keep, but base is lower: 25×3=75 XP)
    investigation: 4.0    (was 3.0 — location completion deserves more: 100 XP)
    side_task: 2.0        (was 3.0 — small tasks: 25×2=50 XP)

Hardcoded trigger values:
  casper_redemption_complete: 75  (was 200)
  meredith_ring_direct_return: 50 (was 100)

Recruitment triggers — all 4 recruits:
  Change elara, thorman, lyra from "quest_multipliers.secondary"
  to "recruitment_bonus" (same as gareth) so all 4 give 30 XP each.

---
WHAT THIS PRODUCES (verify the math after implementing):

ACT I expected total ~300 XP:
  Mayor quest accepted:        1 × main_story trigger = 100 XP
  Rat combat victory:          encounter reward = 50 XP (unchanged)
  Report rat quest:            side_task = 25×2 = 50 XP
  3 location hints learned:    3 × discovery = 30 XP
  3 recruits:                  3 × 30 = 90 XP (4th optional)
  party_building complete:     secondary = 25×3 = 75 XP
  intelligence_gathering hints: 3 × discovery = 30 XP
  ≈ 425 XP (slightly above 300, adjust discovery down to 8 if needed)

ACT II per location (target 150-200 XP per location cleared):
  Arrive at location:          discovery = 10 XP
  Location-specific dialogue:  2-3 discoveries = 20-30 XP
  Combat encounters:           per encounter = 50-100 XP (unchanged)
  Location complete:           investigation = 25×4 = 100 XP
  Total per location ≈ 180-240 XP over 2-3 locations → hits 1000

---
TASK:
1. Read data/narrative_schema.json — confirm all the values above
   match what you actually find (don't trust this briefing blindly)

2. Read game_logic/quest_engine.py — confirm how _award_quest_completion_xp
   applies the multiplier, and how party_recruitment_triggers XP is read

3. Read utils/xp_manager.py — understand how base × mult is computed
   to verify the proposed numbers will resolve correctly

4. Apply the recalibrated values to narrative_schema.json

5. Create a COMMENT BLOCK at the top of the xp_balance section in
   narrative_schema.json documenting the design intent:
   // XP PACING DESIGN
   // Level 2 target: ~300 XP (end of Act I)
   // Level 3 target: ~1000 XP (mid Act II, after 2-3 locations)
   // Adjust discovery_base and multipliers during playtesting.

6. Do NOT touch encounter JSON xp rewards (combat XP) in this task —
   those are calibrated separately and are already reasonable.

---
PLAYTESTING GUIDANCE (include this as a comment in the JSON):
After implementing, the most common tuning levers are:
  - discovery_base: lower if player hits L2 before meeting the mayor
  - investigation multiplier: raise if Act II locations feel unrewarding
  - secondary multiplier: raise if side quests feel ignored

Show me all the current values first. Show me the proposed changes
as a diff before saving anything.
```
# ─────────────────────────────────────────────────────────────────────────────
# POST-SESSION A UPDATE — Apr 30, 2026
# ─────────────────────────────────────────────────────────────────────────────
# Section A follow-up: three stale level-cap issues identified in code review
# and resolved in commit 1387df9.
#
# FIXED — character_overlay.py (P1 — crash)
#   XP bar guard changed from `< 5` to `<= len(xp_requirements) - 1`.
#   At post-game level 4, the Stats tab now shows "Champion of Redstone"
#   instead of trying to index xp_requirements[3] (IndexError).
#   Advance tab guard updated identically — no level-up button shown at L4.
#
# FIXED — character_engine.py (P2 — defensive cleanup)
#   can_level_up() and _can_npc_level_up() now use len(self._level_requirements)
#   instead of hardcoded <= 5. Stale fallback list updated to [0, 300, 1000].
#
# FIXED — character_classes.json (P3 — data cleanup)
#   level_4 / level_5 stripped from wizard, rogue, cleric.
#   Fighter level_4 kept as cosmetic-only entry:
#     title: "Champion of Redstone", no mechanical features.
#   Fighter level_5 removed.
#
# NET RESULT: character sheet is safe to open after boss victory.
#   Runtime progression still caps at level 3 (schema-driven).
#   Level 4 is purely cosmetic — set by combat_engine on boss kill.
# ─────────────────────────────────────────────────────────────────────────────

---

# ═══════════════════════════════════════════════════════════════
# SECTION B — LEVEL & CLASS ABILITY SYSTEM
# ═══════════════════════════════════════════════════════════════

## B-01 [CLAUDE CODE] — Verify Fighter level-up and trim to 3 levels  ⚠️ FIGHTER ONLY
<Completed>

```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

SCOPE NOTE: Terror in Redstone ships with Fighter as the only playable
class. Wizard, Rogue, and Cleric data exists in character_classes.json
but these are reserved for a future sequel. Do NOT touch non-Fighter
class data or add multi-class functionality. The 3-level cap is final
for this game.

CONTEXT: ADR-076 through ADR-080 document that the level-up system was
implemented with JSON-driven class features. This task verifies the
Fighter path specifically works end-to-end and trims any dead 5-level
data that could cause index errors.

TASK:
1. Open data/player/character_classes.json — find the fighter section
2. Verify combat_progression arrays have sensible values at indices 0,1,2
   (level 1, 2, 3). If arrays have 5 entries, trim to 3 entries for
   Fighter only:
     "base_attack_bonus": [0, 1, 2]   (was [0,1,2,3,4])
     "attacks_per_round": [1, 1, 2]   (was [1,1,2,2,2])
     "proficiency_bonus": [2, 2, 2]   (was [2,2,2,2,3])

3. Verify Fighter's level_progression has level_2 and level_3 entries
   with features defined. Remove level_4 and level_5 if present.

4. Read character_engine.py level_up() method — confirm it reads
   features from level_progression[level] in the JSON and returns them
   in the results dict (ADR-080 says this was fixed, verify it works).

5. Read character_overlay.py Advance tab — confirm it displays the
   features returned from level_up().

6. Do NOT modify wizard, rogue, or cleric data.

Report what you find at each step before making any changes.
```

---

## B-02 [CLAUDE CODE] — Verify Fighter ability features display correctly  ⚠️ FIGHTER ONLY
<Completed>
<Claude Code launched the game and tested this itself.  very cool.>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

SCOPE NOTE: Fighter is the only playable class. Do not implement or
verify ability systems for Wizard, Rogue, or Cleric.

CONTEXT: ADR-080 fixed ability parsing in level_up() to read
features from level_progression[level]['features']. This task
confirms the Fighter experience is complete and correct.

Fighter ability milestones (verify these in character_classes.json):
  Level 2: Combat Surge (bonus action recharge mechanic)
  Level 3: Extra Attack (attacks_per_round increases to 2)

TASK:
1. Start a new game as Fighter. Use the F2 debug overlay to manually
   award XP (or check if there is a debug XP command).
   If no debug XP exists, note that as a gap — manual testing of the
   level-up flow requires either a debug tool or playing through
   the rat basement.

2. Level up to Level 2 via the Advance tab in the character overlay.
   Confirm:
   - "Combat Surge" appears in the abilities gained notification
   - The Abilities tab in the character overlay shows Combat Surge
   - HP increases by 1d10 + CON modifier

3. Level up to Level 3. Confirm:
   - "Extra Attack" appears
   - attacks_per_round in combat reflects 2 attacks
   - Combat Action button shows Extra Attack as available ability

4. If any step fails, read character_engine.py level_up() and
   character_overlay.py Advance tab rendering — report what's wrong
   before fixing.

This is primarily a verification task. Only fix what is broken.
```


# ═══════════════════════════════════════════════════════════════
# SECTION C — QUEST & ITEM CLEANUP
# ═══════════════════════════════════════════════════════════════

## C-01 [CLAUDE CODE] — Quest log: restructure into Main / Side / Completed tabs  ⚠️ HIGH
<COMPLETED — DEVIATION: Scope expanded from simple filter to 3-tab redesign.
  display_in_log filter implemented as planned.
  find_henrik and intelligence_gathering correctly remain hidden (spec list was stale).
  Active/Completed tabs replaced with Main / Side Quests / Completed using
  existing "type" field (primary → Main, secondary/side_task → Side).
  No data model changes needed — type field was already in quest JSON.>

C-01 Bug Fixes (post-test)
Two visual defects caught during live testing:

Title overflow — Long quest titles in the detail panel were rendering past the panel edge. Fixed by word-wrapping the title to fit within panel bounds, with description position adjusting dynamically below it.
Box glyph in quest list — A ✅ emoji prefix on completed objectives rendered as a replacement box because the game font doesn't support it. Removed the prefix; the green circle+checkmark in the list row already indicates completed status.

```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: The quest log currently shows up to 10 quest entries.
The design calls for max 5 visible quests at any time — only quests
with clear player-facing objectives should be visible.

QUESTS TO KEEP VISIBLE (show in quest log):
  main_story       — "Terror in Redstone" (always visible in Act I+)
  party_building   — "Assemble Your Party" (until party full)
  basement_rat_combat — "Clear the Basement" (while active)
  intelligence_gathering — "Local Intelligence" (while active)
  kobold_mine_investigation — "The Sealed Shaft"
  find_henrik      — "Seek Old Henrik"
  casper_redemption — "A Second Chance"
  refugee_defense  — "Aid the Refugees"

QUESTS TO HIDE (internal tracking, not player-facing):
  marcus_last_recipe — internal flag, no player objective
  marcus_journals    — internal flag, no player objective

TASK:
1. Open data/narrative_schema.json
2. Find the quest_definitions section
3. Add a "visible_in_log": false field to marcus_last_recipe and
   marcus_journals quest definitions
4. Open screens/quest_overlay.py (or game_logic/quest_engine.py —
   whichever renders the quest list)
5. Find where quests are iterated for display
6. Add a filter: skip quests where visible_in_log is false

Show me the current quest list rendering code and the narrative_schema
quest definitions before making changes.

Keep in ming options to make the quest system manageable for the use. Should we better use categorization for Main quest, Side Quest, or just Tasks?  IF you see conflicts or a major design gap flag and identify it so it can be explored in another separate session.
```

---

## C-02 [VS CODE] — Remove duplicate encounter file
<COMPLETED — DEVIATION: files were not identical; copy was the incomplete version missing 3 fields. Real file kept, copy deleted.>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Delete the duplicate encounter file:
  data/combat/encounters/refugee_camp_brigand_raid copy.json

This is an exact copy of refugee_camp_brigand_raid.json left from
a file-system copy operation. It should not exist.

1. Confirm it is an exact duplicate (or note any differences)
2. Delete it
3. Confirm no code references "brigand_raid copy" by name
   (grep for "brigand_raid copy" in all .py and .json files)
```

---


## C-03 [VS CODE] — Curate merchant inventories to focused item set
<DEVIATION FROM ORIGINAL: Items are NOT removed from items.json or image assets.
The data model is kept intact as a library for future use. Only merchant
stock lists are trimmed so the shops present a clean, focused selection.>

<COMPLETED — DEVIATION: items.json and image assets untouched. Merchant
inventories curated in merchants.json only. Garrick: ale + healing potion.
Bernard: core weapons/armor/potions only, camping supplies removed.
Cassia: trimmed to 4 core potions, greater_healing_potion promoted to
guaranteed. Items remain in data model for future use.>


```

I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: Rather than deleting items from items.json, we are curating
what each merchant stocks. items.json stays untouched — it is a
library. Only data/merchants.json changes.

TARGET STOCK PER MERCHANT:

GARRICK (tavern keeper — Broken Blade):
guaranteed_items: strong_ale, healing_potion
optional_items: (remove trail_rations, torch, shortbow)
stock_overrides: strong_ale: 20, healing_potion: 3
stock_filter include_ids: ["strong_ale", "healing_potion"]
Remove: trail_rations, bedroll from guaranteed/optional/overrides

BERNARD (general trader — Redstone Town):
guaranteed_items: longsword, leather_armor, healing_potion, shield
optional_items: chain_mail: 0.7, plate_armor: 0.4, dagger: 0.8,
shortbow: 0.6, greater_healing_potion: 0.5
Remove from guaranteed: bedroll, hemp_rope, tinderbox, torch, trail_rations
Remove torch from stock_overrides
stock_filter: add include_ids list with only the weapons/armor/potions above

CASSIA (alchemist — Violet Mortar):
Keep as-is — her stock is already well-curated.
Only remove from stock_filter include_ids:
elixir_of_vigor, potion_of_clarity, alchemist_fire, holy_water
Keep: healing_potion, greater_healing_potion, antidote, restoration_draught
Update guaranteed_items: healing_potion, greater_healing_potion, antidote
Update optional_items to match the shorter include_ids list

Read data/merchants.json first and show me the current stock before
making changes. Do not touch data/items.json or any asset files.



```

---

## C-04 [VS CODE] — Update quest "Next Steps" hint text
<COMPLETED — DEVIATION: All 48 objective_descriptions rewritten as actionable hints, not just the 5 listed in spec. Unicode checkmark glyph in quest_overlay.py also fixed (same class of bug as C-01 emoji fix).>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: Quest objectives should include a "next_steps" hint so
the player always knows what to do. The quest overlay displays
objectives but may not show actionable hints.

TASK:
1. Open data/narrative_schema.json
2. Find the objective_descriptions section (or similar field that
   drives quest log text)
3. For each of the 8 visible quests (see C-01 list), verify there
   is clear "what to do next" language. If missing or vague, update:

   main_story active: "Find and speak to the Mayor in the Broken Blade Tavern."
   main_story after quest_active: "Investigate the three regions: Hill Ruins, Red Hollow Mine, Swamp Church."
   party_building: "Speak to Gareth, Elara, Lyra, and Thorman in the tavern to recruit party members."
   basement_rat_combat: "Descend to Garrick's basement and clear the rat infestation."
   find_henrik: "Ask around Redstone Town for Old Henrik. He lives on the outskirts."

4. Open screens/quest_overlay.py — confirm these strings are rendered
   beneath the objective title (not just the title alone).

Show me the current objective text before editing.
```


# ═══════════════════════════════════════════════════════════════
# SECTION D — REMAINING UX POLISH (from Feb 26 run-through)
# Items not yet completed from the previous prompts doc.
# ═══════════════════════════════════════════════════════════════

## D-01 [CLAUDE CODE] — Controls hint on first entry to Broken Blade  (was B-03)
<Completed- deviated.  instructions stay until user leaves the tavern>

```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: New players don't know the controls when they first enter the
Broken Blade Tavern. Add a temporary controls hint in the dialog/text
zone at the bottom of the screen.

The hint should show:
  "WASD: Move  |  E: Interact  |  B: Back  |  I: Inventory  |  Q: Quests  |  C: Character  |  H: Help"

RULES:
- Show the hint only until the player first presses any movement key
  or E — then dismiss it permanently for that save
- Use a game_state flag: controls_hint_dismissed = False (default)
  Set it to True on first WASD or E keypress
- Display in the dialog border zone at the bottom (same area as
  interaction prompts) — use draw_centered_text() in GRAY or dim WHITE
- Do NOT show the hint if controls_hint_dismissed is already True
  (so returning players don't see it again)

KEY FILES:
- screens/broken_blade_nav.py    (add rendering + dismiss logic)
- data/narrative_schema.json     (add controls_hint_dismissed flag)

Please read broken_blade_nav.py first to understand the dialog zone
rendering, then implement the hint.

Make sure to test and verify application.
```

---

## D-02 [CLAUDE CODE] — Stat roll: switch to 4d6-drop-lowest  (was C-02)
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The stat rolling during character creation feels like it produces
too many low numbers. Classic Gold Box RPGs (Pool of Radiance etc.) used
4d6-drop-lowest which gives a more heroic feel with higher average stats.

CHANGE TO IMPLEMENT:
If currently using 3d6 (sum of 3 dice): change to 4d6 drop lowest
  → Roll 4 random values 1-6, discard the lowest, sum the remaining 3
  → This shifts average from ~10.5 to ~12.2 — feels noticeably better

If already using 4d6: leave it and report back.

KEY FILES: Search screens/character_creation*.py or
game_logic/character_engine.py for the stat rolling function
(look for random.randint calls in groups of 3 or 4).

Show me the current roll code first, then implement the change if needed.
```

---

## D-03 [CLAUDE CODE] — Dialogue option color coding  (was C-09/C-10)
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Improve dialogue readability with two visual conventions:

1. QUEST-CRITICAL options → render in YELLOW
   Choices that advance the main quest or give critical information.

2. EXIT/FAREWELL options → render in GRAY
   Choices that end the conversation should be visually distinct.

ARCHITECTURE NOTE (verified May 2026):
Dialogue options are keyboard-only — [1][2][3] numbered choices.
There are NO mouse click regions on dialogue options anywhere in
the codebase. The only mouse handling is in the shopping overlay.

TARGET FILE: ui/generic_dialogue_handler.py
The option rendering loop is at approximately line 204:

    for i, choice in enumerate(options):
        choice_text = f"{i+1}. {choice.get('text', 'No text')}"
        choice_surface = choice_font.render(choice_text, True, DIALOGUE_OPTION_COLOR)
        surface.blit(choice_surface, (200, y_pos))

NOTE: dialogue_ui_utils.py does NOT exist — do not look for it.

APPROACH:
- Add "style": "quest" or "style": "exit" to dialogue option objects
  in the JSON files. This is an optional field — default is normal.
- In the rendering loop above, check choice.get('style') and apply:
    style: "quest" → YELLOW
    style: "exit"  → GRAY
    (no style)     → DIALOGUE_OPTION_COLOR (unchanged default)
- The number prefix "1." stays DIALOGUE_OPTION_COLOR regardless.
  Only the option text portion changes color.

PROOF OF CONCEPT:
After the code works, add style fields to 2-3 options in
data/dialogues/broken_blade_mayor.json as a live test.

Read ui/generic_dialogue_handler.py lines 200-215 first.
Show me the current rendering loop, then propose the minimal change.
Do NOT touch mouse click registration or any click handling.
```

---

## D-04 [CLAUDE CODE] — Yellow portrait border when level-up is ready  (was C-18)
<Completed>

```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: When a character has enough XP to level up but hasn't done so
yet, their portrait in the party status panel should pulse or show a
YELLOW border as a visual indicator.

KEY FILES:
- utils/party_display.py          (draw_party_status_panel function)
- game_logic/character_engine.py  (can_level_up method, ~line 1098)

APPROACH:
1. Read draw_party_status_panel() to see how portraits are currently
   drawn with their borders
2. Read can_level_up() in character_engine — it checks XP vs threshold.
   Determine if it is callable without side effects from the UI layer.
3. In the portrait draw code: if can_level_up() is True for this
   character, use YELLOW for the border rect; otherwise normal color.
4. This should apply to BOTH the player portrait and NPC party portraits.

NOTE: This task depends on A-01 (3-level XP curve) being done first,
otherwise the thresholds being checked are wrong.

Show me the current portrait border drawing code before implementing.
```

---

## D-05 [CLAUDE CODE] — Garrick INFO tab content  (was C-15)
<Complete>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: The INFO tab in Garrick's merchant/shop screen shows mixed up or
incorrect text. It should show:
  1. A flavour description of Garrick and his shop
  2. A note about the player's charisma affecting prices (if charisma
     is high enough, show a positive note; if low, neutral)

TASK:
1. Read ui/shopping_overlay.py — find the INFO tab render section
2. Read data/dialogues/broken_blade_garrick.json for personality tone
3. Write the INFO tab content as:
   "Garrick runs the only supply shop in the Broken Blade.
    His prices are fair — or at least, that's what he tells everyone.
    [If charisma >= 14]: Your charming manner seems to have caught
    his attention. You may find his prices... agreeable.
    [If charisma < 14]: He's not unfriendly, just businesslike."

4. Read charisma from game_state.character directly (not BuffManager —
   keep it simple, the shop context may not have BuffManager available).

Show me the current INFO tab rendering code first.
```

---

## D-06 [VS CODE] — Add more names to character creation name pool  (was C-06)
<Complete>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The random name pool on character creation is missing some names.
Add these names to the available pool:


Additional fantasy names: Royce, Byrd, Wonfel, Grover, Danel, Ergus, Hanko

KEY FILES: Find the name list — search for an array/list of name
strings in screens/character_creation.py or data/player/character_names.json

Show me where the name list currently lives, then add the names.
```

---

## D-07 [CLAUDE.AI] — Intro sequence prose rewrite  (was C-07 Part 1)
<COMPLETED — DEVIATION: Scenes 1-3 updated in intro_sequence.json only.
  Rewrote for atmospheric 1980s RPG tone; improved rhythm and pacing for
  pixelated font readability. No code changes made.>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Rewrite the intro sequence text to feel like classic 1980s RPG
storytelling — atmospheric, direct, evocative. Think Pool of Radiance's
opening crawl or the Ultima IV intro.

The current text in data/narrative/intro_sequence.json is functional
but stiff. Keep the same story beats, just improve the prose quality.

PROCESS:
1. I'll share the current intro_sequence.json content with you
2. You write improved versions of each scene's text
3. I'll review and approve before saving to file

Story context for tone:
  - The town of Redstone is being menaced by cultists and shadow blight
  - The player is a travelling adventurer arriving at the Broken Blade Tavern
  - The mayor is worried and seeking help
  - There are strange tremors and disappearances
  - Mood: mysterious, slightly ominous, but with a classic adventure spirit

[PASTE THE CONTENT OF data/narrative/intro_sequence.json HERE WHEN
BRINGING THIS TO CLAUDE.AI]
```

---

## D-08 [CLAUDE CODE] — Gold floating indicator after non-combat
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: After completing Garrick's rat basement quest and talking
to him for the reward, the player sees an XP floating indicator
but there is NO gold gain indicator shown.

TASK:
1. Find the Garrick post-quest reward dialogue in
   data/dialogues/broken_blade_garrick.json
   Check the effects block — is gold actually awarded? How much?

2. Find how XP floating indicators are triggered from dialogue
   effects — look in game_logic/dialogue_engine.py for how
   "xp_reward" effect type is processed.

3. If gold effects exist but no indicator fires, add a matching
   floating indicator for gold rewards from dialogue effects —
   use the same notification system as XP (ui/notifications.py).

4. If gold is not awarded at all in the dialogue effects, add it
   (Garrick should pay ~50 gold for the rat quest).

Read dialogue_engine.py and the Garrick reward dialogue first.
Show me what you find before making changes.
```


# ═══════════════════════════════════════════════════════════════
# SECTION E — CAVIA NARRATIVE CONTENT
# ═══════════════════════════════════════════════════════════════
## E-01 [CLAUDE.AI] — Write Cavia Act II flavor dialogue  ⚠️ NARRATIVE
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Write 3 Cavia-specific flavor dialogue moments for Act II
locations. These should be humorous but grounded — Cavia are a
rodent-folk race with keen senses and practical wisdom.

MOMENT 1 — Red Hollow Mine entry:
  Context: Cavia player enters the kobold-infested mine.
  Tone: Cavia expertise in burrows, mild disdain for kobold tunnel
  quality. Like a master carpenter looking at shoddy work.
  Trigger: on entering mine (mine_pre_entrance_nav or similar)
  Sample direction: "These kobolds have no respect for structural
  integrity. These tunnels will collapse in a decade."

MOMENT 2 — Hill Ruins portal reaction:
  Context: Cavia player sees the ancient Aethel dimensional portal.
  Tone: Dry humor about size — Cavia are small, the portal is massive.
  Sample direction: "I thought it would be... bigger. It's only
  three times my height."

MOMENT 3 — Swamp Church: finding the cult documents:
  Context: Cavia player reads the cult's ritual notes referencing
  flesh as a binding ingredient.
  Tone: Disgust at the hygiene implications, dark humor.
  Sample direction: "Flesh as a binder? Poor hygiene and worse
  carrot storage..."

For each moment, write:
  - A 2-3 line internal monologue / spoken line for the Cavia player
  - The JSON dialogue state structure to add (I'll implement the code)
  - What flag to check: "race" == "cavia" or "is_cavia" == true

Keep the Cavia voice consistent: practical, slightly prim, never
loses their composure, occasionally sharp.
```

---

## E-02 [CLAUDE CODE] — Implement Cavia Act II flavor dialogue
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: After writing the Cavia flavor dialogue text (task E-01),
this task implements it in the game. Three new conditional
interaction points need to be added.

For each Act II location, add a Cavia-specific reaction that
fires ONCE when the player enters (or examines a specific object):

MINE REACTION:
  Location: screens/red_hollow_mine_pre_entrance_nav.py OR
            data/dialogues/mine_*.json (whichever handles entry flavor)
  Condition: game_state.character.get('race') == 'cavia'
  Trigger: on first entry to Red Hollow Mine (flag: cavia_mine_reaction_shown)

HILL RUINS REACTION:
  Location: screens/hill_ruins_entrance_nav.py OR
            data/dialogues/hill_ruins_portal.json
  Condition: same race check
  Trigger: on approaching the portal (flag: cavia_portal_reaction_shown)

SWAMP CHURCH REACTION:
  Location: data/dialogues/swamp_church_cultdocuments.json
  Condition: same race check
  Trigger: on examining cult documents (flag: cavia_swamp_reaction_shown)

For each: look at how Henrik's Cavia recognition works in
data/dialogues/redstone_town_henrik.json (it uses requirements:
{"race": "cavia"} to gate dialogue options) — use the same pattern.

Read the three location files before implementing. Show me where each
reaction should be inserted.
```

---

## E-03 [CLAUDE CODE] — Aethel Lexicon Cavia discovery scene
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: In Dungeon Level 4, the player can examine the Aethel Lexicon
Fragment (data/dialogues/dungeon_level_4_marcus_study.json or similar).
For Cavia players, Elara should have special dialogue here revealing
that Cavia ancestors were Aethel test subjects — an emotionally resonant
moment.

TASK:
1. Find where the Aethel Lexicon is examined — search for
   "lexicon" in data/dialogues/ and screens/dungeon_level_4_nav.py
2. Check if there is already a Cavia-specific branch in that dialogue
3. If not, add a dialogue option gated by race == 'cavia' that leads
   to Elara's revelation:
   "Your ancestors... they were test subjects for the Aethel
    dimensional experiments. I found the records. I'm so sorry."
   Then give the Cavia player a response option (defiant or resigned).
4. Set a flag: cavia_lexicon_revelation_seen = true

Follow the same pattern as the Taborex Cavia confrontation in
data/dialogues/dungeon_level_5_taborex.json (requirements: race: cavia)

Read the lexicon dialogue file first. Show me the structure before
implementing.
```


# ═══════════════════════════════════════════════════════════════
# SECTION F — GRAPHICS PASS
# Do after baseline and content are complete.
# ═══════════════════════════════════════════════════════════════

## F-01 [CLAUDE CODE] — Verify and populate combat tileset assets per location
<COMPLETED — DEVIATION: all 16 battlefield JSONs already had a `tileset` field set (a prior
pass must have done this); the actual gaps were (1) `swamp_exterior.json` being a byte-for-byte
copy of `small_cellar.json` — wrong battlefield_id/tileset/layout — replaced with a real swamp
layout matching the swamp_ghost/swamp_skeleton encounters, tileset `swamp`, terrain `swamp_floor`;
(2) `ui/combat_system.py::_get_floor_type()`'s floor_tile_map was missing `ritual_floor`,
`dungeon_floor`, `swamp_floor` (mapped to their exact generated art) and `corrupted_floor`/
`dark_stone` (no dedicated art exists — mapped to the nearest available tile, ritual/dungeon
respectively); (3) `combat_sprite_manager.py::load_floor_tiles()`'s floor_map only loaded 3 of 7
needed keys, so even correctly-mapped floors fell back — extended to load all 7. Verified via a
headless render of one encounter per tileset (cellar/mine/ruins/alley/camp/dungeon/dungeon_crypt/
swamp): all resolve real wall + floor art, zero fallback warnings, zero render errors. Full
`main.py` boot also clean. Noted but out of scope: `redstone_town_alley - gaunlet.json` is a
dead duplicate battlefield file never loaded by battlefield_id lookup — left alone.>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: ADR-123 (Oct 12, 2025) implemented a full data-driven combat
tileset system with auto-tiling. The infrastructure is ALREADY BUILT:
  - CombatSpriteManager loads tilesets from a "tileset" field in
    battlefield JSON (e.g., "tileset": "cellar")
  - Auto-tiling checks 8 neighbors to select correct wall tile
  - Floor type read from battlefield JSON "terrain.default" field
  - Asset paths: assets/images/tiles/combat/{tileset}_wall_north.png etc.

The rendering code does NOT need to be written. What's missing is
the asset files and ensuring all battlefield JSONs have the right
tileset fields set.

TASK:
1. Read utils/combat_sprite_manager.py — understand what tileset
   files it expects (naming convention for wall/floor PNGs) and
   what fallback it uses when files are missing.

2. Read data/combat/battlefields/*.json — list which ones have a
   "tileset" field set vs which are missing it.

3. List what tileset PNG assets actually exist in assets/images/tiles/

4. Report the gap: which battlefields are using fallback graphics
   because either the tileset field is missing or the PNG is missing.

5. For battlefields missing a "tileset" field, add the appropriate
   value based on location:
     small_cellar / tavern interiors → "cellar"
     mine tunnels                    → "mine"
     hill ruins / dungeon chambers   → "dungeon"
     swamp church                    → "church"
     outdoor / camp                  → "outdoor"
     portal chamber                  → "dungeon"

6. Do NOT create new PNG art — just map the JSON fields correctly
   so the system uses existing assets where available, and falls
   back gracefully where art doesn't exist yet.

Read combat_sprite_manager.py first to understand the file naming
convention before touching any JSON files.
```

---

## F-02 [CLAUDE CODE] — Portrait rendering consistency across all screens
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Audit portrait rendering across all navigation screens and
confirm portraits load consistently. Some screens may fall back to
placeholder circles instead of actual portrait images.

SCREENS TO CHECK:
  screens/broken_blade_nav.py
  screens/redstone_town.py
  screens/exploration_hub.py
  screens/hill_ruins_entrance_nav.py
  screens/swamp_church_exterior_nav.py
  screens/refugee_camp_main_nav.py

TASK:
1. Find how each screen calls draw_party_status_panel() or renders
   portraits — look for portrait image loading code
2. Identify any screens where portraits fall back to placeholder circles
3. For screens with fallback placeholders, trace why the portrait
   image fails to load (wrong path? wrong key in game_state?)
4. Fix paths or loading logic so all screens show the same portrait

Read utils/party_display.py first to understand the portrait loading
system, then check each screen. Report findings before fixing.
```

---

## F-03 [VS CODE] — NPC portrait images for leader and Taborex
<Complete>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: These portrait assets exist in the project:
  assets/images/icons/characters/npc_portraits/leader_portrait.jpg
  assets/images/icons/characters/npc_portraits/taborex_portrait.jpg

TASK:
1. Search the codebase for where refugee camp leader dialogue
   references a portrait image (check refugee_camp_*.json and
   screens/refugee_camp_main_nav.py)
2. Search where Taborex references a portrait image (check
   dungeon_level_5_nav.py and dungeon_level_5_taborex.json)
3. If either is referencing a placeholder or missing path, update
   the path to point to the correct portrait file above
4. Verify the images are the right format for pygame.image.load()
   (JPGs work but PNGs are preferred — note if conversion is needed)
```


# ═══════════════════════════════════════════════════════════════
# SECTION G — AUDIO (do last)
# All gameplay must be complete and tested before audio work begins.
# ═══════════════════════════════════════════════════════════════

## G-01 [CLAUDE CODE] — Create AudioManager skeleton
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Create a new utils/audio_manager.py with the core AudioManager
class. No audio assets exist yet — this is the infrastructure only,
so it must degrade gracefully when no files are present.

IMPLEMENT:
  class AudioManager:
      def __init__(self):
          # Initialize pygame.mixer safely (catch failures)
          # Set default volumes: music=0.7, sfx=0.8
          # Track currently playing music track
          
      def play_music(self, track_id: str, loop: bool = True, fade_in: int = 500):
          # Load from assets/audio/music/{track_id}.ogg
          # If file missing: print warning, return silently
          # Fade in the track
          
      def stop_music(self, fade_out: int = 500):
          # Fade out current music
          
      def play_sfx(self, sfx_id: str, volume: float = 0.8):
          # Load from assets/audio/sfx/{sfx_id}.ogg
          # If file missing: return silently
          
      def set_music_volume(self, volume: float):  # 0.0 to 1.0
      def set_sfx_volume(self, volume: float):
      def mute_all(self):
      def unmute_all(self):

Also create the directory structure:
  assets/audio/
  assets/audio/music/
  assets/audio/sfx/
  assets/audio/README.md  (with notes on expected files)

The AudioManager should be a singleton accessible via:
  from utils.audio_manager import get_audio_manager

Do NOT wire it into any screens yet — this is infrastructure only.
```

---

## G-02 [CLAUDE.AI] — Audio asset sourcing guide
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Help me identify and source the audio assets needed for the game.

MUSIC NEEDED:
  1. exploration_theme — 3-4 min loop, mysterious/adventurous,
     slightly melancholy. Reference: Pool of Radiance town theme.
  2. combat_theme — 2-3 min loop, intense, tactical, heroic.
     Reference: SSI Gold Box combat music.
  3. title_theme — 1-2 min, atmospheric, builds anticipation.
  4. dungeon_theme — 2-3 min loop, darker, tense.

SFX NEEDED (all short, < 2 seconds):
  ui_click, footstep_stone, footstep_wood, sword_hit, bow_release,
  spell_cast, door_open, door_close, level_transition, item_pickup,
  coin_pickup, damage_grunt, level_up_chime, quest_complete_chime

LICENSING REQUIREMENT: All assets must be royalty-free and usable
in a commercial project without attribution requirements (or with
simple text attribution).

SOURCES TO EVALUATE:
  - OpenGameArt.org (free, various licenses)
  - FreePD.com (CC0 public domain)
  - Incompetech.com (Kevin MacLeod, CC BY)
  - Freesound.org (mixed licenses — check each)

Help me build a sourcing plan:
1. Recommend specific search terms for each asset type
2. Flag which licenses are safe for commercial use
3. Suggest an attribution tracking template
4. Note if any assets could be AI-generated safely (with license notes)
```

---

## G-03 [CLAUDE CODE] — Wire AudioManager to screen transitions
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: AudioManager exists (task G-01 complete) and audio assets
are in place (task G-02 sourcing complete). Now wire music to screens.

MUSIC MAP (screen → track_id):
  title_menu           → title_theme
  character_creation   → title_theme (same)
  intro_scenes         → exploration_theme (fade in gently)
  broken_blade_nav     → exploration_theme
  redstone_town        → exploration_theme
  exploration_hub      → exploration_theme
  hill_ruins_*         → dungeon_theme
  red_hollow_mine_*    → dungeon_theme
  swamp_church_*       → dungeon_theme
  refugee_camp_*       → exploration_theme
  dungeon_level_*      → dungeon_theme
  combat (any)         → combat_theme  (switch on combat start,
                          switch back to previous track on exit)
  victory_screen       → (silence or brief fanfare)
  epilogue_slides      → exploration_theme

TASK:
1. Find where screen transitions happen — ui/screen_manager.py
2. After each transition, call get_audio_manager().play_music(track_id)
   using the map above — only if the new track differs from current
3. For combat: on combat start, save the pre-combat track, switch to
   combat_theme. On combat end, restore the saved track.
4. All calls must be safe if audio files are missing (AudioManager
   already handles this — just call the method).

Read screen_manager.py first and show me the transition points.
```

---

## G-04 [CLAUDE CODE] — Wire SFX to UI events
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: AudioManager exists with play_sfx() method. Wire sound
effects to key game events.

SFX TO WIRE:
  - Any button click          → ui_click
    (find the draw_button / click handler pattern in utils/)
  - Player movement (WASD)    → footstep_stone or footstep_wood
    (only every 2nd step to avoid spam — use a step counter)
  - Combat melee hit          → sword_hit
  - Combat ranged attack      → bow_release
  - Spell cast                → spell_cast
  - Item picked up            → item_pickup
  - Gold gained               → coin_pickup
  - Level up                  → level_up_chime
  - Quest completed           → quest_complete_chime
  - Door / screen transition  → door_open

START WITH: button clicks and level-up chime (easiest, most impactful).
Leave footsteps and combat SFX for a second pass.

Find where buttons are clicked (input_handler.py or screen-specific
click handlers). Show me the button click handling pattern before
implementing.
```


# ═══════════════════════════════════════════════════════════════
# SECTION H — QUEST & DIALOGUE SYSTEM STABILISATION
# ⚠️ HIGH PRIORITY — These are the primary source of runtime bugs.
# Do before Cavia content (Section E) — bugs here will break E too.
# ═══════════════════════════════════════════════════════════════
#
# WHY THIS IS A PRIORITY
# The system has significant structural fragility:
#   - 242 flags SET across 70 dialogue JSON files
#   - Only 138 flags declared in narrative_schema.json npcs section
#   - 235 flags set in dialogue but not declared in schema (per audit)
#   - 129 NPC state conditions in dialogue_state_mapping, referencing
#     100+ unique flag names — many checked but never declared
#   - Quest triggers reference 29 flags that are not in the npcs section
#   - dialogue_state_mapping conditions are string expressions evaluated
#     at runtime — a typo in a flag name silently fails (no error raised)
#
# The risk is not theoretical: a wrong flag name routes the player to
# the wrong dialogue state and they may get stuck, miss a quest trigger,
# or see repeated dialogue. This is hard to catch in manual testing
# because most paths only execute once per playthrough.
#
# BEST PRACTICE APPROACH
# The industry standard for this type of system is:
#   1. Single source of truth for flag names (narrative_schema.json)
#   2. All flags declared before use — undeclared = error at load time
#   3. Automated cross-reference at startup — log warnings for mismatches
#   4. Per-act flag audit — only flags relevant to the current act active
#   5. Clear ownership — each flag has one system that sets it
# ═══════════════════════════════════════════════════════════════

## H-01 [CLAUDE CODE] — Flag audit: build a cross-reference report  ⚠️ DO FIRST
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: The game has a flag-based narrative system where:
  - Flags are SET by dialogue JSON effects ("set_flag" effects)
  - Flags are SET by combat victories (quest_flags in encounter JSON)
  - Flags are READ by dialogue_state_mapping conditions (string expressions)
  - Flags are READ by dialogue option requirements
  - Flags are READ by quest_triggers in narrative_schema.json

The problem is there is no validation layer — a misspelled flag name
silently does nothing (no error). A flag can be checked in a condition
but never set, or set in dialogue but never checked by any system.

TASK: Write a standalone Python audit script at scripts/flag_audit.py
that produces a cross-reference report. Do NOT modify any game files.

The script should:

1. COLLECT all flags SET:
   - Scan data/dialogues/*.json for all "set_flag" effect objects
     (look for: {"type": "set_flag", "flag": "..."} patterns)
   - Scan data/combat/encounters/*.json for quest_flags in rewards
   - Output: {flag_name: [list of files that set it]}

2. COLLECT all flags READ:
   - Scan data/narrative_schema.json dialogue_state_mapping — extract
     all identifier tokens from condition strings (alphanumeric + _)
     that look like flag names (not keywords: and, or, not, true, false,
     numbers, known non-flag tokens like 'mayor_family_status')
   - Scan data/dialogues/*.json for requirements.flags keys
   - Scan data/narrative_schema.json quest_triggers for dialogue_flag values
   - Output: {flag_name: [list of locations that read it]}

3. COLLECT all flags DECLARED:
   - Scan data/narrative_schema.json npcs section for story_flags keys
   - Output: set of declared flag names

4. REPORT (print to console, also write to scripts/flag_audit_report.txt):
   A) Flags READ but NEVER SET — these will silently never trigger
      (conditions that can never become true)
   B) Flags SET but NEVER READ — dead flags (set but nothing uses them)
   C) Flags READ but NOT DECLARED in narrative_schema npcs section
      (these are the most dangerous — no canonical definition)
   D) Summary counts: total flags set, read, declared, orphaned

5. Format the report clearly:
   === FLAGS READ BUT NEVER SET (X flags) ===
   flag_name
     Read in: dialogue_state_mapping (garrick condition)
              data/dialogues/broken_blade_garrick.json (requirements)

Run the script. Share the output. Do not fix anything yet —
this report is the basis for H-02 and H-03.
```

---

## H-02 [CLAUDE CODE] — Add startup flag validation to narrative_schema loader
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: After running the flag audit (H-01), we know which flags are
used without being declared. The safest long-term fix is to add a
validation step that runs at startup and logs warnings for any
flag referenced in dialogue_state_mapping conditions that is not
declared in the narrative_schema npcs section.

This does NOT crash the game — it only logs warnings so we can catch
new problems as they're introduced.

TASK:
1. Find where narrative_schema.json is loaded at startup — look in
   utils/narrative_schema.py or wherever the schema module is imported

2. Add a validate_flags() method or function that:
   - Reads all condition strings from dialogue_state_mapping
   - Extracts flag-like tokens (same logic as H-01 audit script)
   - Checks each against the full set of declared flags
     (from npcs[*].story_flags keys)
   - Logs a WARNING for each undeclared flag found:
     "⚠️ Undeclared flag in dialogue_state_mapping: '{flag}' (NPC: {npc})"
   - Does NOT raise exceptions — just logs

3. Call validate_flags() once at game startup (after schema loads)
   in game_controller.py or main.py

4. Add a second check: for each quest_trigger entry that references
   a dialogue_flag, verify that flag exists in some NPC's story_flags.
   Log a warning if not.

KEY FILES:
- utils/narrative_schema.py  (or wherever schema is loaded)
- core/game_controller.py    (for startup call)

Show me the current schema loading code first. Then implement the
validator as an additive, non-breaking change.
```

---

## H-03 [CLAUDE CODE] — Declare missing flags in narrative_schema npcs section
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: The flag audit (H-01) identified flags that are actively used
in dialogue conditions or quest triggers but not declared in the
narrative_schema.json npcs section. This is the primary source of
silent routing bugs.

This task declares the missing flags — it does NOT change any game
logic, just adds the missing declarations so the validation (H-02)
is clean and future developers have a canonical reference.

PROCESS:
1. Get the flag audit report from H-01 output
   (or re-run scripts/flag_audit.py)

2. For section C of the report (READ but NOT DECLARED):
   - For each flag, determine which NPC "owns" it based on the flag
     name prefix and context (e.g., garrick_* flags → garrick npc entry)
   - Add the flag to the appropriate npcs[npc_id].story_flags section
     with a brief description:
     "garrick_post_victory_complete": "Set after garrick gives post-victory dialogue"

3. For flags that don't clearly belong to one NPC (e.g., act-level flags
   like act_three_complete, mayor_family_status), add them to a top-level
   "game_state_flags" section in the schema if it doesn't exist, or to
   the existing act_progression section.

4. After declaring all flags, re-run scripts/flag_audit.py and confirm
   section C is empty (or near-empty — a few ambiguous tokens from
   condition parsing are acceptable).

5. Commit the result with a clear message: "declare all narrative flags
   in schema for validation coverage"

Show me a sample of the current npcs section structure before editing
so the new entries follow the same format.
```

---

## H-04 [CLAUDE CODE] — Quest trigger audit: verify each trigger fires correctly
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: The quest system has 32 triggers in narrative_schema.json
quest_triggers. Each trigger watches for a dialogue_flag to be set,
then advances a quest objective and optionally awards XP.

The risk is that triggers reference flag names that don't match what
dialogue actually sets (e.g., dialogue sets "reported_victory" but
trigger watches "reported_basement_victory"). Silent mismatch = quest
never advances.

TASK:
1. Read all 32 quest_triggers from data/narrative_schema.json

2. For each trigger, find WHERE the dialogue_flag is actually set:
   - grep data/dialogues/*.json for set_flag effects with that flag name
   - Note: some flags may be set by combat (check encounter JSON rewards)

3. Build a simple table:
   trigger_id | dialogue_flag | set in file | quest_objective | XP spec
   
4. Flag any triggers where:
   A) The dialogue_flag is never set anywhere — dead trigger
   B) The dialogue_flag is set in multiple places — double-fire risk
      (check if one-shot guard exists: xp_awarded__trigger__{id})
   C) The quest_objective path doesn't match any defined objective
      in the quest_definitions section

5. For dead triggers (A): check if the flag was recently renamed
   in dialogue JSON but trigger wasn't updated. Propose the correct
   flag name to match the dialogue.

6. Fix only dead triggers (A) and objective path mismatches (C) —
   these are bugs. Document double-fire risks (B) as known issues
   with the guard system already in place.

Read quest_engine.py _evaluate_quest_triggers() first to understand
how triggers are evaluated before auditing the data.
```

---

## H-05 [CLAUDE CODE] — Dialogue state mapping: order validation and dead-state check
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: The dialogue_state_mapping in narrative_schema.json has 129
NPC state conditions across 23 NPCs. These are evaluated IN ORDER —
the first matching condition wins. ADR-064 documents that "more
specific conditions must come before broader ones." A condition ordering
bug means the wrong state is selected and the player sees the wrong
dialogue.

Additionally, dialogue states are referenced in the mapping that may
not exist in the corresponding dialogue JSON file (dead references).

TASK:
1. For each NPC in dialogue_state_mapping, load their dialogue JSON
   and collect all state names defined there.

2. Cross-reference: for each state name in the mapping, check it
   exists in the dialogue JSON. Report any mapping entry that points
   to a non-existent state — these are guaranteed bugs (the engine
   would look up a state that doesn't exist and fall back to a
   default or error state).

3. For ordering: identify any NPC where a BROAD condition appears
   before a SPECIFIC condition. A broad condition is one with fewer
   flag checks. Example of bad ordering:
     "casual_chat": "garrick_talked"  ← catches everything
     "knows_about_ruins": "garrick_talked && learned_about_ruins"  ← never reached
   Flag these — they mean the specific state is unreachable.

4. Fix ordering issues by moving specific conditions above the broad
   catch-all they are being shadowed by. Follow the pattern from
   ADR-064: specific → broad, within each NPC's mapping block.

5. Fix dead state references by either:
   A) Correcting the state name to match the dialogue JSON
   B) Adding the missing state to the dialogue JSON (only if simple)

Focus on NPCs that are critical to quest progression first:
  mayor, garrick, henrik, cassia, marcus

Read narrative_schema.py's _evaluate_condition() method to confirm
how conditions are evaluated before making changes.
```

---

## H-06 [CLAUDE.AI] — Quest/dialogue system: best practice review
<Completed -diviation:  added H-07 and 8 based on this output>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone built
in Python/Pygame. I want a best practice review of our narrative flag
and quest trigger architecture.

SYSTEM OVERVIEW:
- ~240 flags scattered across 70 dialogue JSON files
- Flags evaluated via string expressions in dialogue_state_mapping
  (e.g., "garrick_talked && !mayor_talked && learned_about_ruins")
- Quest triggers watch for specific flags and advance objectives
- No type system or schema validation at load time
- Flags are set by: dialogue effects, combat victory, Python code

KNOWN PROBLEMS:
1. Flag names are strings — typos fail silently at runtime
2. Condition ordering in dialogue_state_mapping is load-order sensitive
3. Duplicate XP awards were a past bug (fixed by one-shot guards)
4. Flags set in one session may not survive save/load if they're
   set as dynamic game_state attributes (not in save data)

QUESTIONS FOR REVIEW:
1. What is the industry standard approach for flag-based narrative
   systems at this scale (~240 flags, 4-6 hour game)?
2. What is the best way to make flag names "validated" without a
   full type system (e.g., enum approach, const file, schema check)?
3. How should condition ordering be managed — is string evaluation
   order the right pattern, or should conditions be structured data?
4. What is the cleanest way to ensure all flags survive save/load?
5. Are there known Python/Pygame patterns for this that avoid the
   runtime-string-evaluation approach entirely?

Please focus on practical recommendations for a solo developer
finishing a game, not theoretical purity. "Good enough for ship"
is the goal.
```


## H-07 [CLAUDE CODE] — Add FLAGS constants module for Python-side flag references
<completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: H-06 best-practice review recommended adding a FLAGS constants
module so that flag names used in Python engine code are never raw strings.
Currently flags like "garrick_talked", "marcus_confrontation_resolved" etc.
are typed as literals in Python files. A typo fails silently at runtime.
The narrative_schema.json and dialogue JSON files will continue using raw
strings (those are caught by the H-02 startup validator). This task covers
only the Python-side references.

TASK:
1. Grep for all raw flag string literals used in Python files (*.py):
   - set_flag / get_flag / has_flag calls
   - Any direct game_state attribute assignments that correspond to flags
   - quest_engine.py and dialogue_engine.py are the primary suspects
   List every unique flag string found.

2. Create utils/flags.py with a FLAGS class (NOT an enum — plain class
   with string constants). Group by category with comments:
     class FLAGS:
         # NPC conversations
         GARRICK_TALKED = "garrick_talked"
         # Quest progression
         MARCUS_CONFRONTATION_RESOLVED = "marcus_confrontation_resolved"
         # etc.
   Only include flags that appear in Python code — not the full schema list.

3. Replace each raw string literal in Python files with FLAGS.<CONSTANT>.
   Add the import at the top of each file changed.

4. Verify: run the game to startup and confirm no AttributeError or
   import errors. The H-02 validator should still report 0 warnings.

5. Commit: "feat(flags): add FLAGS constants module; replace raw flag
   strings in engine code"

Do NOT touch narrative_schema.json or any dialogue JSON files.
Do NOT add flags that only appear in JSON — those stay as raw strings.


## H-08 [CLAUDE CODE] — Dead flag review: 160 set-but-never-read flags
<completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

CONTEXT: H-01 flag audit found 160 flags that are SET but never READ in
any condition. Most are expected (loot flags, exploration markers, one-shot
XP guards). However H-06 review flagged that some quest progression flags
in this list may represent logic holes — a flag is set to record an event
but nothing ever gates on it, meaning the game never reacts to that event.

The flag audit report is at scripts/flag_audit_report.txt (Section B).

TASK:
1. Read Section B of the audit report (set but never read flags).

2. Categorize each flag into one of these buckets:
   A) EXPECTED DEAD — loot flags (trigger_loot_check, *_loot), one-shot
      XP guards (xp_awarded__*), pure exploration markers (searched_*)
   B) QUEST PROGRESSION — flags whose name suggests they record a story
      event (e.g., marcus_journals_found, understood_marcus_plan,
      taborex_ritual_ended, shadow_blight_noticed). These MIGHT be logic
      holes if no condition ever checks them.
   C) AMBIGUOUS — anything else

3. For each flag in bucket B, check whether any dialogue state or quest
   trigger SHOULD logically gate on it but doesn't. Look at the relevant
   NPC's dialogue_state_mapping and their dialogue JSON file.
   Example: if marcus_journals_found is set but no DSM condition checks it,
   does Marcus have a state for "player found the journals"? If that state
   exists in the dialogue JSON but isn't wired in the DSM, that's a bug.

4. Report findings grouped by quest (main quest / side quests):
   - Confirmed logic holes (flag set, state exists in JSON, DSM not wired)
   - Suspected holes (flag set, no corresponding dialogue state found)
   - Confirmed expected dead (safe to ignore)

5. For any confirmed logic holes: fix the DSM wiring in narrative_schema.json
   to add the missing condition. Do NOT add new dialogue states — only wire
   existing ones that were missed.

6. Commit fixes with: "fix(narrative): wire missing DSM conditions for
   orphaned quest flags"

Focus on main quest flags first: marcus_*, dungeon_level_*, taborex_*,
understood_*, shadow_blight_*. Side quest flags (casper_*, meredith_*,
henrik_*) are lower priority.


# ═══════════════════════════════════════════════════════════════
# SECTION I — CARRIED OVER FROM FEB 26 (not yet completed)
# These were open in the Feb 26 doc and not absorbed into Sections A–H.
# Feb 26 doc can now be archived — work from this file only.
# ═══════════════════════════════════════════════════════════════

## I-01 [VS CODE] — Stat roll: change to 4d6 drop lowest
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The stat rolling during character creation skews low. Change to
4d6 drop-lowest (roll 4 dice 1-6, discard the lowest, sum the rest).
This shifts average from ~10.5 to ~12.2 — feels more heroic.

If already using 4d6: leave it and report back.

KEY FILES: Search screens/character_creation*.py or
utils/character_utils.py for the stat rolling function (look for
random.randint calls in groups).

Show me the current roll code first, then implement the change.
```

---

## I-02 [CLAUDE CODE] — Dialogue option color coding (quest items + exits)
<Completed>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Improve dialogue readability with two visual conventions:
1. QUEST-CRITICAL options → render in YELLOW
2. EXIT/FAREWELL options → render in GRAY

APPROACH:
- Check the dialogue JSON format — do options already have a "type"
  or "category" field? If not, add one.
- Suggested convention: add "style": "quest" or "style": "exit" to
  dialogue option objects in JSON
- In the dialogue renderer, check this field and apply the colour

NOTE (ADR-051): Dialogue uses keyboard-first [1][2][3] numbered
choices rendered in dialogue_ui_utils.py — NOT mouse click regions.
Target the rendering code in dialogue_ui_utils.py, not a separate
renderer file.

KEY FILES:
- ui/dialogue_ui_utils.py             (numbered option rendering)
- data/dialogues/broken_blade_mayor.json  (test file — update a few
  options to use new style field as proof of concept)

Read the option rendering code in dialogue_ui_utils.py first. Show
me the current option draw loop, then propose the minimal change.
```

---

## I-03 [CLAUDE CODE] — Garrick INFO tab has wrong/mixed content
```
<Completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: The INFO tab in Garrick's shop screen shows incorrect content.
It should show:
  1. A flavour description of Garrick and his shop
  2. A note about charisma affecting prices (positive if charisma >= 14,
     neutral otherwise)

TASKS:
1. Read the shop overlay code to understand how the INFO tab is rendered
2. Read data/dialogues/broken_blade_garrick.json for flavour context
3. Write the INFO tab content — something like:
   "Garrick runs the only supply shop in the Broken Blade.
    His prices are fair — or at least, that's what he tells everyone.
    [charisma >= 14]: Your charming manner seems to have caught his
    attention. You may find his prices... agreeable.
    [charisma < 14]: He's not unfriendly, just businesslike."
4. Read effective charisma from game_state.character stats directly
   (avoid BuffManager complexity if the shop context doesn't have it)

Show me the current INFO tab rendering code first.
```

---

## I-04 [PLAN FIRST] — Trinket screen buff/debuff details
<complete>
```
⚠️  READ THIS PLANNING NOTE BEFORE CODING  ⚠️

PLAN FIRST — ask in Claude.ai chat:
  "I need to show trinket buff details on the character creation
   trinket selection screen in my Python/Pygame CRPG Terror in Redstone.
   BuffManager exists in utils/buff_manager.py. The problem is
   game_state may not be fully initialized yet during character creation.
   How should I approach showing mechanical effect text (e.g. '+1 Armor
   Class') without triggering initialization errors?"

THEN IMPLEMENT with Claude Code once you have the approach confirmed.

KEY FILES:
- screens/character_creation*.py    (trinket selection screen)
- utils/buff_manager.py             (get_trinket_bonuses method)
- data/items.json                   (trinket special_effects data)

GOAL: Below each trinket description, show its mechanical effects.
For the Mysterious Trinket: "??? Effects unknown — examine to reveal"
```

---

## I-05 [CLAUDE CODE] — Combat exit button: require exit tile
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The Exit button is currently always visible during combat. It
should only appear when the player character is standing on a
designated exit tile (stairs, door, etc.) — Gold Box RPG style.

APPROACH:
1. Read ui/combat_system.py — find the Exit button render and handler
2. Read the combat battlefield JSON format — understand the data
   structure so we can add exit_tiles to battlefield definitions
3. The change:
   - Remove the always-visible Exit button
   - Each frame: if player is on an exit tile, show "Leave Combat"
     prompt; otherwise show nothing
4. Add appropriate exit tile coordinates to the rat basement
   battlefield JSON as a proof of concept

Read the combat UI and one battlefield JSON first, then propose the
full approach before implementing.
```

---

## I-06 [PLAN FIRST] — Opportunity attacks when moving away from adjacent enemy
```
⚠️  PLANNING SESSION REQUIRED BEFORE CODING  ⚠️

BRING THIS TO CLAUDE.AI AND ASK:
  "I want to add opportunity attacks to Terror in Redstone's combat
   system — when a character moves away from an adjacent enemy, that
   enemy gets one free melee attack. I need to understand the current
   movement resolution code in game_logic/combat_engine.py before
   designing the implementation. Can you help me plan this?"

PROVIDE CONTEXT:
- Paste the move resolution section of combat_engine.py
- The game uses a grid-based tactical system
- Enemies have melee attack stats defined in their JSON

ONLY AFTER planning: implement with Claude Code using the agreed approach.
```

# ═══════════════════════════════════════════════════════════════
# SECTION J — New Items(s) discovered during this fix
#
# ═══════════════════════════════════════════════════════════════

J-01-  Change the villian name to Taborex
<Complete>
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK:

I need to rename the villain character "Taborex" to "Taborex" throughout the entire project. Before making any changes, please do the following:
STEP 1 - AUDIT FIRST:
Search the entire project directory for every occurrence of "taborex" and "Taborex" (case-insensitive) across all file types including .py, .json, .md, and any other files. Present a complete list grouped by file before changing anything.
STEP 2 - CONFIRM THE REPLACEMENT RULES:
Apply these specific replacement rules:

taborex → taborex (lowercase)
Taborex → Taborex (capitalized)
TABOREX → TABOREX (uppercase, if any exist)
taborexs → taborex (possessive, drop the s and handle in display text)
taborex_ → taborex_ (in item IDs and flag names e.g. taborexs_corrupted_tome → taborex_corrupted_tome)
"High Cultist Taborex the Consumed" → "High Cultist Taborex the Consumed"

STEP 3 - WAIT FOR APPROVAL:
Show me the full audit list and the proposed changes. Do not modify any files until I review and confirm.
STEP 4 - MAKE CHANGES:
Only after I approve, make all changes. Report each file modified with a count of replacements made.
STEP 5 - VERIFY:
After changes are complete, do a final search to confirm zero remaining instances of "taborex" in any form exist in the project.
```


J-02

[COMPLETE] Overlay Input Freeze & Quest Keyboard Navigation
Commit: 638cbc2

All 17 nav screens now block pygame.key.get_pressed() when any overlay is open — player cannot move behind an overlay using arrow keys
Quest log auto-selects the first quest on open and on tab switch (detail panel always populated, no mouse click required)
UP/DOWN arrows move a keyboard cursor through the quest list; hitting the edge auto-advances to the next/previous page
LEFT/RIGHT arrows switch tabs; 1-9 select tabs directly
P/N keys still page-scroll as before
Footer and inline hint text updated to reflect new controls,