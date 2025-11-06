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
