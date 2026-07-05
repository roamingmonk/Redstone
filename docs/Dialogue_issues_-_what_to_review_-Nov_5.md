**Summary: What Caused the Dialogue Issues**

**Issue #1: Combat Return Navigation**

**Problem**: Combat returned to refugee_camp_nighttime_defense instead
of nav screen\
**Cause**: base_location.py wasn\'t setting pre_combat_location for
action_hub combats\
**Solution**: Added special case for refugee_camp_brigand_raid to return
to main nav\
**Lesson**: Different combat trigger systems (random encounters vs
action buttons) need consistent return location handling

**Issue #2: Loot Overlay Navigation**

**Problem**: COMBAT_BACK handler triggered instead of loot overlay\'s
navigation\
**Cause**: Loot overlay used wrong event data format (target instead
of target_screen) and wrong event manager
(game_state.event_manager vs screen_manager.event_manager)\
**Solution**: Fixed event format and used correct event manager
reference\
**Lesson**: SCREEN_CHANGE events have a specific format - always
use target_screen and source_screen, and ensure you\'re using the active
event manager

**Issue #3: NPC ID Mismatch**

**Problem**: Dialogue showed first_meeting instead
of post_combat_thanks\
**Cause**: Screen manager parses dialogue files
as location_npc using rsplit(\'\_\', 1). File
named refugee_camp_leader.json was parsed as location=refugee_camp,
npc=leader, but narrative_schema had entry for refugee_camp_leader\
**Solution**: Renamed to refugee_camp_marta.json → parsed as npc=marta,
added marta entries to narrative_schema\
**Lesson**: **NPC dialogue files should follow
pattern: {location}\_{short_npc_name}.json** where short_npc_name has NO
underscores
(like broken_blade_garrick, redstone_town_henrik, refugee_camp_marta)

**Issue #4: Missing Flag in Context**

**Problem**: All dialogue conditions evaluated to False even when flags
were true in save file\
**Cause**: refugee_combat_rewarded wasn\'t registered in
narrative_schema\'s NPC story_flags, so it wasn\'t included in dialogue
engine\'s context dictionary\
**Solution**: Added \"combat_rewarded\": \"refugee_combat_rewarded\" to
marta\'s story_flags\
**Lesson**: **ALL flags used in dialogue_state_mapping conditions MUST
be registered** in either the NPC\'s story_flags or the global flag
registry, otherwise they\'ll be missing from context and cause condition
evaluation to fail

**Issue #5: Schema Key Mismatch (not a file-naming problem this time)**

**Problem**: Refugee camp\'s "Displaced Refugees" dialogue always showed
first_meeting\'s 3 options, forever, no matter how many times you talked to
them or which flags were set\
**Cause**: `refugee_camp_refugees.json` was named correctly (parses fine as
location=refugee_camp, npc=refugees per the rsplit rule), but
`narrative_schema.json` registered this NPC\'s entries in **both** the
`npcs` dict and `dialogue_state_mapping` dict under the key
`"refugee_camp_refugees"` (the full dialogue-file id) instead of the bare
`npc_id` `"refugees"` that `get_current_dialogue_state()` and
`get_npc_conversation_flag()` actually look up by. The lookup silently
returned `{}`, so the code always fell back to `first_meeting`, AND
`get_npc_conversation_flag()` missed the registered `"conversation_flag"`
and silently invented a phantom flag (`refugees_talked`) that nothing else
read\
**Solution**: Renamed both schema keys to `"refugees"` (the `dialogue_file`
field inside the entry, which holds the real filename, was left alone)\
**Lesson**: **The dialogue filename convention and the narrative_schema.json
dict keys are two independent things that both have to match npc_id.**
Getting the filename right (Issue #3) does not guarantee the schema keys
are right too - check both. Compare an NPC that works (e.g. `"marta"`,
keyed by her bare id in both dicts) against a new entry before assuming the
schema is correct.

**Issue #6: One Shared "Talked" Flag Gating Multiple Independent Topics**

**Problem**: Refugees offered 3 topics on first visit (cult info, mayor\'s
family, comfort). Picking any ONE of them permanently removed all 3 on every
future visit - the design intent was to let the player work through all
three across separate visits\
**Cause**: All three options\' effects set the same single flag
(`refugee_group_talked`), and the state mapping\'s `return_visits` condition
gated on that same flag. The first option picked flipped the flag, and the
schema had no way to distinguish "talked once" from "exhausted every topic"\
**Solution**: Gave each topic its own completion flag (existing
`learned_cult_rituals_from_refugees` / `confirmed_mayors_family_taken` plus a
new `comforted_refugees`), added a `requirements` block to each
`first_meeting` option so an already-answered topic drops out of the option
list, and rewrote `return_visits`\'s condition to require all *applicable*
topics done (a topic gated behind another flag, like `quest_active`, doesn\'t
count against exhaustion if it was never actually offered)\
**Lesson**: **If a dialogue state has multiple options meant to be visited
independently across separate sessions, each option needs its own tracking
flag.** A single shared "talked" flag can only distinguish "never talked" from
"talked at all" - it cannot represent "some but not all topics covered."

**How to Avoid These Issues in the Future**

**1. Dialogue File Naming Convention**

✅ **DO**: {location}\_{simple_npc_name}.json

-   Examples: broken_blade_garrick.json, refugee_camp_marta.json

-   NPC name should be short and have NO underscores

❌ **DON\'T**: refugee_camp_leader.json (will parse as npc=\"leader\")
❌ **DON\'T**: refugee_camp_camp_leader.json (too many underscores)

**2. Narrative Schema Flag Registration**

When adding new dialogue states that reference flags:

1.  Add the NPC to npcs section with all story_flags

2.  Add the NPC to dialogue_state_mapping section

3.  **Ensure EVERY flag used in conditions is in story_flags**

4.  Test with debug output to verify flags are in context

**3. Combat Return Navigation**

For action_hub combats, always set both:

game_state.previous_screen = game_state.screen \# For COMBAT_BACK

game_state.pre_combat_location = self.get_screen_name() \# For loot
overlay

**4. Event Format Consistency**

Always use proper SCREEN_CHANGE format:

event_manager.emit(\"SCREEN_CHANGE\", {

\'target_screen\': target, \# NOT \'target\'!

\'source_screen\': current \# Always include source

})

**5. Debug Early**

When dialogue doesn\'t work:

1.  Check STATE-EVAL ORDER (shows condition checking order)

2.  Check context flags (shows what flags are available)

3.  Check individual condition evaluation (shows why each fails)

4.  Verify npc_id matches narrative_schema key
