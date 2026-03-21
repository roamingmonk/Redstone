# Terror in Redstone — Copy-Paste Task Prompts
# Feb 26, 2026 | Act I / Broken Blade Run-Through Issues
#
# HOW TO USE:
#   VS Code edits  → copy the block, paste into the Claude extension chat panel
#   Claude Code    → copy the block, paste as your first message in a new session
#   Each block is self-contained — no other context needed.
#
# LEGEND:
#   [VS CODE]     = Simple edit, use Claude extension in VS Code
#   [CLAUDE CODE] = Multi-file or logic fix, use Claude Code terminal
#   [PLAN FIRST]  = Read the planning note before coding
#
# ORDER: Work top to bottom. Do all [VS CODE] items first (fast wins),
#        then tackle [CLAUDE CODE] items.
# ─────────────────────────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════
# SECTION A — CRITICAL BUGS
# ═══════════════════════════════════════════════════════════════

## A-01 [CLAUDE CODE] — Mayor "Not Now" re-entry bug  ⚠️ CRITICAL
```
<COMPLETED>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: When the player is inside the Broken Blade Tavern and talks to the 
Mayor for the first time, if they choose "Not now" and then walk back to 
the Mayor to talk again, they get the message "*The office is empty. The 
Mayor must be at the Broken Blade Tavern.*" — which makes no sense 
because we ARE in the tavern.

That "office is empty" message belongs in redstone_town.py (when the 
player tries to visit the mayor's office in town during Act I). It should 
NOT appear inside the tavern itself.

EXPECTED: Returning to the Mayor in the tavern after "Not now" should 
re-open his normal intro dialogue so the player can accept the quest.

KEY FILES TO CHECK:
- data/dialogues/broken_blade_mayor.json  (the dialogue state machine)
- screens/broken_blade_nav.py             (the tavern navigation screen)
- data/narrative/narrative_schema.json    (for flag names)

APPROACH:
1. Read broken_blade_mayor.json and find the state that triggers 
   "office is empty"
2. That state should only be reachable from redstone_town.py, not from 
   broken_blade_nav.py — add a flag condition or separate entry point
3. When returning to mayor in tavern (quest not yet accepted), the 
   dialogue should return to the intro/offer state
4. Do NOT change the redstone_town mayor behaviour — only fix the 
   tavern re-entry path

Please read the files first, show me what you find, then propose the fix 
before making any changes.
```

---

## A-02 [CLAUDE CODE] — Quest log stuck on "Meet the Mayor" after Not Now  ⚠️ CRITICAL
```
<Completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: After the player selects "Not now" in the Mayor's first dialogue 
in the Broken Blade Tavern, the quest log overlay still shows the 
objective "Meet with the Mayor to get the quests." The player cannot 
complete this because the mayor re-entry is also broken (see A-01), 
but even after that fix, the quest objective should remain open until 
the player actually accepts the quest.

The problem is likely that talking to the mayor at all sets 
mayor_talked = true, which may be advancing the quest objective 
prematurely — even when the player chose "Not now."

KEY FILES TO CHECK:
- data/dialogues/broken_blade_mayor.json  (check what flags "not now" sets)
- data/narrative/narrative_schema.json    (check mayor quest objective flags)
- screens/quest_overlay.py or equivalent  (how quest objectives are shown)

APPROACH:
1. Find the "not now" dialogue option and confirm exactly which flags 
   it sets (or incorrectly sets)
2. The quest objective "Meet the Mayor" should only clear when the 
   player actually accepts the quest (quest_active = true)
3. "Not now" should set NO progress flags — it is a pure deferral
4. Verify the fix doesn't break the quest flow when the player does 
   accept the quest

   Consider how this impacts the narrative_schema file and ensure it still works as intended.

Please read the relevant files first, show me the current flag logic, 
then propose minimal changes.
```

---

## A-03 [CLAUDE CODE] — Portrait click doesn't open character overlay in tavern
```
<Completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: Clicking on a character portrait in the party status panel should 
open the character info overlay (same as pressing C). This works on 
other screens but NOT inside the Broken Blade Tavern navigation screen 
(broken_blade_nav.py).

The portrait click handler exists in input_handler.py as 
_handle_portrait_click() — it's just not being triggered from the 
tavern screen.

KEY FILES TO CHECK:
- screens/broken_blade_nav.py   (does it register portrait click regions?)
- input_handler.py              (find _handle_portrait_click and how it's called)
- ui/party_display.py           (how party panel portraits are drawn and return rects)

APPROACH:
1. Find how portrait click rects are registered on screens that DO work
2. Check if broken_blade_nav.py registers them the same way — it probably doesn't
3. Make the tavern screen register portrait click regions using the same 
   pattern as working screens
4. Test: clicking portrait 1 should open character overlay on the Player tab;
   clicking NPC portraits should open on the Party tab

Please read the files first and show me the gap before making changes.
```


# ═══════════════════════════════════════════════════════════════
# SECTION B — HIGH PRIORITY UX
# ═══════════════════════════════════════════════════════════════

## B-01 [VS CODE] — App icon shows Python snake logo, need game icon
```
<completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The application taskbar/dock icon shows the default Python snake 
logo. I need to set a custom game icon.

WHAT TO DO:
1. Find where pygame.display.set_caption() is called in main.py or 
   game_controller.py — the icon call goes right next to it
2. The icon should load from assets/images/ — check if there is already 
   a redstone_icon.png or similar file there
3. If an icon PNG exists, add: pygame.display.set_icon(pygame.image.load('path/to/icon.png'))
4. The icon should be 32x32 or 64x64 pixels PNG with transparency
5. If no icon file exists yet, add the code with a TODO comment 
   noting the asset is needed

Show me the current display setup code first, then add the icon call.
```

---

## B-03 [CLAUDE CODE] — No on-screen controls reminder in tavern
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: New players don't know the controls when they first enter the 
Broken Blade Tavern. Add a temporary controls hint in the dialog/text 
zone at the bottom of the screen.

The hint should show:
  "WASD: Move  |  E: Interact  |  I: Inventory  |  Q: Quests  |  C: Character  |  H: Help"

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
- data/narrative/narrative_schema.json  (add controls_hint_dismissed flag)

Please read broken_blade_nav.py first to understand the dialog zone 
rendering, then implement the hint.
```

---

## B-04 [CLAUDE CODE] — Player can walk onto NPC sprites (no collision)
```
<Completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: In the Broken Blade Tavern, the player character can walk directly 
onto NPC sprites — they share the same tile. NPCs should block movement 
like walls do.

KEY FILES TO CHECK:
- screens/broken_blade_nav.py          (NPC positions, movement handling)  
- ui/base_location_navigation.py       (NavigationRenderer, is_walkable logic)
- data/maps/broken_blade_map.py or .tmj (map/NPC position data)

APPROACH:
1. Read how NavigationRenderer.is_walkable() currently works
2. Find where NPC positions are stored/managed in the tavern screen
3. The fix: before allowing a move to (new_x, new_y), also check if 
   any NPC currently occupies that tile — if so, block the move
4. NPC positions should be checked dynamically (NPCs can move or be 
   recruited and disappear), not hardcoded
5. Do NOT change the NPC interaction system — only block movement 
   onto their tile

Please read the movement and NPC management code first, then propose 
the safest way to add NPC collision.
```

---

## B-05 [PLAN FIRST] — Trinket screen doesn't show buff/debuff details
```
⚠️  READ THIS PLANNING NOTE BEFORE CODING  ⚠️

This task requires understanding how BuffManager works with a partially 
initialized game_state (character creation is not yet complete when 
the trinket is selected).

PLAN FIRST — ask in the Claude.ai chat:
  "I need to show trinket buff details on the character creation 
   trinket selection screen. BuffManager exists in utils/buff_manager.py. 
   The problem is game_state may not be fully initialized yet during 
   character creation. How should I approach this?"

THEN IMPLEMENT with Claude Code once you have the approach confirmed.

KEY FILES:
- screens/character_creation*.py    (trinket selection screen)
- utils/buff_manager.py             (get_trinket_bonuses method)
- data/items.json                   (trinket special_effects data)

GOAL: Below each trinket description, show a list of its mechanical 
effects e.g. "+1 Armor Class", "+1 Charisma". For the Mysterious 
Trinket specifically show "??? Effects unknown — examine to reveal"
```


# ═══════════════════════════════════════════════════════════════
# SECTION C — MEDIUM PRIORITY POLISH
# ═══════════════════════════════════════════════════════════════

## C-01 + C-05 [VS CODE] — Stat roll and name screen text tweaks (bundle)
```
<COMPELTED>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Small text/wording fixes on character creation screens.

Find and make these changes (search for the current text strings):

1. Stat roll screen — find text that says something like 
   "...for your Fighter class" or "for your [class] class"
   → Change to use the player's chosen class dynamically:
     Replace hardcoded "Fighter" with game_state.character.get('class','character').title()
     Result should read: "...for your Mage class" or "...for your Fighter class" etc.

2. Name selection screen — find the instruction text that reads something like:
   "Select a name for your character or create a custom name."
   → Change to: "Choose a name or roll new options."

3. Name selection screen — find the button labelled "New Names" or similar
   → Change label to: "Roll Random Names"

KEY FILES: Search in screens/ for character_creation files.
Show me the current text first, then make the changes.
```

---

## C-02 [CLAUDE CODE] — Stat roll RNG skews low, increase high-roll probability
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The stat rolling during character creation feels like it produces 
too many low numbers. Classic Gold Box RPGs (Pool of Radiance etc.) used 
4d6-drop-lowest which gives a more heroic feel with higher average stats.

CURRENT BEHAVIOUR: Unknown — need to check the code first.

CHANGE TO IMPLEMENT:
If currently using 3d6 (sum of 3 dice): change to 4d6 drop lowest
  → Roll 4 random values 1-6, discard the lowest, sum the remaining 3
  → This shifts average from ~10.5 to ~12.2 — feels noticeably better

If already using 4d6: leave it and report back.

KEY FILES: Search screens/character_creation*.py or 
utils/character_utils.py for the stat rolling function (look for 
random.randint calls in groups).

Show me the current roll code first, then implement the change.
```

---

## C-03 + C-04 [VS CODE] — Name screen button visual distinction
```
<COMPLETE>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: On the name selection screen, the action buttons 
("Roll Random Names" / "Enter Custom Name") look identical to the 
name selection buttons. Action buttons should be visually distinct.

CHANGES:
1. Find the "Roll Random Names" (or current equivalent) button render call
2. Find the "Enter Custom Name" (or current equivalent) button render call  
3. Give these TWO buttons a different color — use YELLOW or WARM_GOLD 
   for the border/text to distinguish them as actions vs selections
4. The name option buttons (the actual names to pick from) stay WHITE/normal

KEY FILES: screens/character_creation*.py — look for the name selection 
screen rendering function.

Show me how the buttons are currently drawn, then make the color change.
```

---

## C-06 [VS CODE] — Add more names to name pool including party member names
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The random name pool on character creation is missing some names.
Add these names to the available pool:

Party member names to add: Gareth, Elara, Thorman, Lyra
Additional fantasy names to add (pick fitting ones or use these):
  Aldric, Seraphine, Brennan, Isolde, Caden, Rowena, Theron, Vesper

KEY FILES: Find the name list — search for an array/list of name strings
in screens/character_creation*.py or a data file like data/names.json

Show me where the name list currently lives, then add the names.
```

---

## C-07 + C-08 [VS CODE] — Intro scene visuals and language rewrite
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The intro/starting scenes use plain generated Python graphics 
(flat colours, no atmosphere) and the text prose feels stiff.

Part 1 — Text rewrite (do this first, it's just JSON):
Open data/narrative/intro_sequence.json
Rewrite the scene text to feel more like classic 1980s RPG storytelling —
atmospheric, direct, evocative. Think Pool of Radiance's intro crawl.
Current text is stiff/functional. New text should feel like an opening 
to an adventure novel. Keep the same story beats, just improve the prose.
Show me the current text first, write new versions, and I'll approve 
before you save.

Part 2 — Visual note (for discussion, not immediate coding):
The intro scenes use Python-generated backgrounds. The title screen 
has better visuals. For now just note a TODO comment in 
screens/intro_scenes.py at the background render function:
  # TODO: Replace with layered artwork similar to title screen
  # Currently using generated gradient/silhouette backgrounds
```

---

## C-09 + C-10 [CLAUDE CODE] — Dialogue option color coding (quest items + exits)
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Improve dialogue readability with two visual conventions:

1. QUEST-CRITICAL options → render in YELLOW
   These are dialogue choices that advance the main quest or give 
   critical information. They need to stand out.

2. EXIT/FAREWELL options → render in GRAY or with "[Goodbye]" prefix
   Choices that end the conversation should be visually distinct so 
   players don't accidentally close dialogue.

APPROACH:
- Check the dialogue JSON format — do options already have a "type" 
  or "category" field? If not, we need to add one.
- Suggested convention: add "style": "quest" or "style": "exit" to 
  dialogue option objects in JSON
- In the dialogue renderer, check this field and apply the colour:
    quest → YELLOW
    exit  → GRAY  
    default → WHITE (unchanged)

KEY FILES:
- ui/dialogue_renderer.py or wherever dialogue options are drawn
- data/dialogues/broken_blade_mayor.json  (test file — update a few 
  options to use new style field as proof of concept)

Read the dialogue render code first. Show me the option rendering 
logic. Then propose the minimal change.
```

---

## C-11 + C-12 [VS CODE] — Meredith dialogue farewell text + hide post-quest options
```
<Complete>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Two fixes in data/dialogues/broken_blade_meredith.json

Fix 1 — Abrupt endings:
Find these dialogue options (or similar) and soften the farewell:
  "Take care"  →  "Take care. Find me if you learn anything."
  "I'll find him"  →  "I'll find him. Goodbye for now, Meredith."
The player shouldn't feel the conversation just cut off.

Fix 2 — Hide post-quest discovery options:
Meredith has options about the swamp/ruins that appear even after 
the player has the quest. These should be hidden once quest_active = true.
Find any options referencing the swamp church or ruins locations and add:
  "requirements": {"flag_not": "quest_active"}
so they disappear once the quest is running.

Review the narrative schema file to ensure this change is properly applied.


Show me the current dialogue states before making changes.
```

---

## C-13 + C-14 [VS CODE] — Mayor and Pete farewell text (quick fixes)
```
<Complete>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Two tiny text fixes in dialogue JSON files.

Fix 1 — data/dialogues/broken_blade_mayor.json:
Find the "Not now" dialogue option text.
Change to: "Not now, goodbye."
(The player needs to know this ends the conversation)

Fix 2 — data/dialogues/broken_blade_pete.json:
Find Pete's closing/exit dialogue line (something like "keep the 
stool warm for me" or similar).
Add a goodbye: change to end with "...keep the stool warm. Goodbye."
or add a separate farewell option.  R
Show me the current text for both before changing.
```

---

## C-15 [CLAUDE CODE] — Garrick INFO tab has wrong/mixed content
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: The INFO tab in Garrick's merchant/shop screen shows mixed up or 
incorrect text. It should show:
  1. A flavour description of Garrick and his shop
  2. A note about the player's charisma affecting prices (if charisma 
     is high enough, show a positive note; if low, neutral)

TASKS:
1. First read the shop overlay code to understand how the INFO tab 
   is currently rendered:
   - ui/shop_overlay.py (or similar shop UI file)
   
2. Read Garrick's dialogue/merchant data to understand what info 
   is available:
   - data/dialogues/broken_blade_garrick.json
   
3. Write the INFO tab content — it should read something like:
   "Garrick runs the only supply shop in the Broken Blade. 
    His prices are fair — or at least, that's what he tells everyone.
    [If charisma >= 14]: Your charming manner seems to have caught 
    his attention. You may find his prices... agreeable.
    [If charisma < 14]: He's not unfriendly, just businesslike."

4. Check if BuffManager is available from the shop context to read 
   effective charisma — if so use it; if not, read game_state.character 
   stats directly.

Show me the current INFO tab rendering code first.
```

---

## C-16 [VS CODE] — Add close button to Sell and Info tabs in shop
```
<Completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: The shop overlay has a close button on the Buy tab but NOT on 
the Sell tab or Info tab. All three tabs need a close button.

KEY FILE: ui/shop_overlay.py (or the main shop rendering file)

TASK:
1. Find where the close button is defined and rendered for the Buy tab
2. The Sell and Info tab renders should have the identical close button 
   in the same screen position
3. It should trigger the same close/exit event as the Buy tab button

Show me the current Buy tab close button code, then copy it to the 
other two tab render functions.
```

---

## C-17 [VS CODE] — Garrick post-supply-dialogue farewell + town shop hint
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: In data/dialogues/broken_blade_garrick.json

Fix 1: After the "sell supplies" dialogue flow, the final response 
says "Thanks" or similar — this should be a proper farewell:
Change to something like: "Thanks for the trade. Come back anytime."

Fix 2: Add a line pointing the player toward town shops:
Either in the same state or as a separate dialogue option, Garrick 
should hint: "If you need better gear, the shops in town proper 
will have more to offer than I do here."

This helps players know to explore Redstone Town for equipment.

Show me the current post-supply dialogue states before editing.
```

---

## C-18 [CLAUDE CODE] — Yellow portrait border when level-up is ready
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: When a character has enough XP to level up but hasn't done so 
yet, their portrait in the party status panel should have a YELLOW 
border (instead of the normal white/gray border) as a visual indicator.

KEY FILES:
- ui/party_display.py          (draw_party_status_panel function)
- game_logic/character_engine.py  (how to check if level up is available)

APPROACH:
1. Read draw_party_status_panel() to see how portraits are currently 
   drawn with their borders
2. Read character_engine to find how to check: 
   "does this character have enough XP to level up?"
   (look for level_up_available, can_level_up, or xp >= next_level_xp)
3. In the portrait draw code: if level up is available, use YELLOW 
   for the border rect; otherwise use the normal color
4. This should apply to BOTH the player portrait and NPC party portraits

Show me the current portrait border drawing code first.
```


# ═══════════════════════════════════════════════════════════════
# SECTION D — COMBAT ISSUES
# ═══════════════════════════════════════════════════════════════

## D-01 [VS CODE] — Action button active when player has no action items
```
<Completed>
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: In combat, the "Action" button (for using items like healing 
potions) is always active/clickable even when the player has no 
usable items. It should be visually greyed out and non-clickable 
when empty.

KEY FILE: ui/combat_system.py (find the Action button render)

TASK:
1. Find where the Action button is drawn in the combat UI
2. Add a check: count usable consumable items in game_state.inventory
   (look for 'consumables' key or similar)
3. If count == 0: render button in GRAY with no click handler
4. If count > 0: render normally (current behavior)

The pattern for disabled buttons likely already exists elsewhere in 
the UI — find and follow that pattern.

Show me the current Action button render code first.
```

---

## D-02 [CLAUDE CODE] — Combat exit button always visible; should require exit tile
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Currently an "Exit" button is always visible during combat. 
This breaks immersion — the player should have to move their character 
to a designated exit tile to leave combat (stairs, door, etc.)

This is how classic Gold Box games handled it (Pool of Radiance etc.)

APPROACH:
1. Read ui/combat_system.py to find the Exit button render and handler
2. Read the combat battlefield JSON format to understand the data 
   structure — we need to add exit_tiles to battlefield definitions
3. The change:
   - Remove the always-visible Exit button
   - Each frame, check if player character is on an exit tile
   - If yes: show "Leave Combat" prompt in the action area
   - If no: no exit option shown
4. For the rat basement specifically, add appropriate exit tile 
   coordinates to its battlefield JSON

Read the combat UI and one battlefield JSON file first, then 
propose the full approach before implementing.
```

---

## D-03 [PLAN FIRST] — Opportunity attacks when moving away from adjacent enemy
```
⚠️  PLANNING SESSION REQUIRED BEFORE CODING  ⚠️

This is a significant combat engine change. Do NOT hand straight 
to Claude Code without a planning discussion first.

BRING THIS TO THE CLAUDE.AI CHAT AND ASK:
  "I want to add opportunity attacks to Terror in Redstone's combat 
   system — when a character moves away from an adjacent enemy, that 
   enemy gets one free melee attack. I need to understand the current 
   movement resolution code in game_logic/combat_engine.py before 
   designing the implementation. Can you help me plan this?"

PROVIDE CONTEXT:
- combat_engine.py move resolution section (paste the relevant code)
- The game uses a grid-based tactical system
- Enemies have melee attack stats already defined in their JSON

ONLY AFTER planning: implement with Claude Code using the agreed approach.
```

---

## D-04 [CLAUDE CODE] — Gold reward indicator missing after Garrick rat quest
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

BUG: After completing the rat basement quest and talking to Garrick 
for the reward, the player sees an XP gain floating indicator but 
there is NO gold gain indicator shown. The gold may or may not 
actually be added — needs verification either way.

TASKS:
1. First verify: find the Garrick post-quest reward dialogue in 
   data/dialogues/broken_blade_garrick.json
   Check the effects block — is gold actually awarded? How much?

2. Check the XP floating indicator code in combat or dialogue effects 
   — find how "XP gained" floats up on screen

3. Gold awards should show the same floating indicator: "+50 gold" 
   (or whatever the amount is) using the same visual system

4. If gold is not actually being awarded at all, fix that first, 
   then add the indicator

KEY FILES:
- data/dialogues/broken_blade_garrick.json  (reward effects)
- ui/combat_system.py or game_logic/dialogue_engine.py  (reward indicators)

Read the Garrick reward dialogue and the XP indicator code first.
```


# ═══════════════════════════════════════════════════════════════
# SECTION E — LOW PRIORITY (do last)
# ═══════════════════════════════════════════════════════════════

## E-04 [NOTE — Art dependent] — Player walk animation improvement
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

NOTE: The player character in the Broken Blade Tavern currently 
renders as a colored circle placeholder. The animation improvement 
depends on sprite art being created in Aseprite first.

WHEN ART IS READY: 
Find the player sprite rendering in screens/broken_blade_nav.py
Replace the colored circle draw call with a pygame sprite sheet loader
The sprite sheet should have at minimum: 4 directional idle frames

FOR NOW — add a TODO comment to the circle draw code:
  # TODO: Replace with sprite sheet animation when art asset is ready
  # Expected: assets/sprites/player_walk.png (4-direction, 2-frame)

Just add the comment, no other code changes needed yet.
```

---

## E-06 [VS CODE] — Deepen recruit NPC dialogue (Elara, Gareth, Lyra, Thorman)
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: The four recruitable NPCs in the Broken Blade Tavern have very 
simple dialogue that was kept minimal during early development. 
Each needs 2-3 additional dialogue states to give them more personality.

CHARACTERS AND PERSONALITY NOTES:
- Gareth: Veteran fighter, pragmatic, dry humour, seen too much
- Elara: Elven mage, precise, curious about the Aethel lore, slightly 
  aloof but genuinely interested in the party's findings
- Thorman: Dwarven warrior, stubborn, loyal, deeply suspicious of magic
- Lyra: Rogue, quick-witted, street-smart, has personal reasons for 
  wanting to clean up Redstone

FOR EACH CHARACTER add to their dialogue JSON:
  1. A "tell me about yourself" branch with 2-3 lines of backstory
  2. A reaction to being asked about the tremors/strangeness in Redstone
  3. A farewell option that feels in-character

KEY FILES: data/dialogues/broken_blade_[gareth/elara/thorman/lyra].json

Read one character's current dialogue first, then write additions 
for all four. Show me before saving.
```

---

## E-07 [VS CODE — verification only] — Verify tremor story thread consistency
```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

TASK: Garrick and Meredith both reference "tremors" in the Broken 
Blade Tavern. Verify this is narratively consistent with the game lore.

BACKGROUND (from project documents):
The tremors are caused by the Shadow Blight destabilizing the ancient 
Aethel portal beneath Redstone. This is established lore and the 
tremor references by Garrick/Meredith are correct and intentional.

ACTION NEEDED:
1. Open data/dialogues/broken_blade_garrick.json
2. Open data/dialogues/broken_blade_meredith.json  
3. Find the tremor references in each
4. Confirm the language is consistent with Shadow Blight / portal 
   activity (not blaming it on something else entirely)
5. If consistent: no changes needed — mark E-07 as verified
6. If inconsistent: note what needs updating

This is a READ AND VERIFY task, not a code change.
```
