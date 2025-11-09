# Flag Analysis & Path Forward
## Based on save_slot_2.json Analysis

**Date:** November 9, 2025

---

## 🔍 CURRENT STATE ANALYSIS

### Discovery Flags (CURRENTLY IN USE)
From `exploration_flags` section:
```json
"learned_about_swamp_church": true
"learned_about_ruins": true  
"learned_about_refugees": true
```

From `narrative_flags` section:
```json
"discovered_old_mine_shaft": true
```

**FINDING:** Discovery flags are **already working** and use the `learned_about_*` pattern (except mine which uses `discovered_old_mine_shaft`)

---

### Completion Flags (MIXED STATUS)

**Flags that EXIST and work:**
```json
"swamp_church_complete": true (in exploration_flags)
"red_hollow_mine_complete": true (in narrative_flags)
```

**Flags that DON'T EXIST in save (need to be added):**
- `hill_ruins_complete` - Missing
- `refugee_camp_complete` - Missing

**NOTE:** The save shows swamp and mine as complete, but player has NOT completed ruins or refugee camp yet, so we can't verify if those flags exist.

---

### Mayor Acknowledgment Flags (DEFINED BUT UNUSED)

From `narrative_flags`:
```json
"mayor_acknowledged_swamp_complete": false
"mayor_acknowledged_ruins_complete": false
"mayor_acknowledged_refugee_complete": false
"mayor_acknowledged_mine_complete": false
```

**FINDING:** These flags exist in the save but are all `false` - they're ready to use but the dialogue to set them isn't implemented yet. This is EXACTLY what our plan needs to add!

---

### NPC Information Flags (ALL WORKING)

From `narrative_flags`:
```json
"meredith_gave_swamp_info": true
"garrick_gave_ruins_info": true
"pete_gave_refugee_info": true
"henrik_gave_shaft_quest": true
```

**FINDING:** Primary NPC discovery system is already implemented and working!

---

### Mayor Location Flags

From `narrative_flags`:
```json
"mayor_talked": true
"quest_active": true
"mayor_gave_swamp_info": true
"mayor_gave_ruins_info": true
"mayor_gave_refugee_info": true
```

**MISSING FLAG:** `act_two_started` - This flag doesn't exist yet and needs to be added to trigger mayor movement to office.

---

## 🚨 CRITICAL FINDINGS

### Issue #1: Flag Duplication
Some flags appear in BOTH `narrative_flags` AND `exploration_flags`:
```
narrative_flags["learned_about_swamp_church"]: true
exploration_flags["learned_about_swamp_church"]: true

narrative_flags["learned_about_ruins"]: true  
exploration_flags["learned_about_ruins"]: true

narrative_flags["learned_about_refugees"]: true
exploration_flags["learned_about_refugees"]: true
```

**This is the "legacy flags from development iterations" issue the user mentioned.**

**IMPACT:** Not breaking anything currently, but creates confusion. System is checking both places.

**RECOMMENDATION:** Leave as-is for now (both systems working). Can consolidate later in a cleanup phase.

---

### Issue #2: Inconsistent Mine Naming
- Discovery flag: `discovered_old_mine_shaft`
- Completion flag: `red_hollow_mine_complete`

**Pattern inconsistency** but working.

**RECOMMENDATION:** Keep as-is to avoid breaking existing saves.

---

### Issue #3: Missing Completion Flags
Need to add (if they don't already exist in schema):
- `hill_ruins_complete`
- `refugee_camp_complete`

---

## ✅ CORRECTED FLAG REFERENCE

### Discovery Flags (USE THESE)
```
learned_about_swamp_church    # Swamp Church discovered
learned_about_ruins           # Hill Ruins discovered
learned_about_refugees        # Refugee Camp discovered
discovered_old_mine_shaft     # Red Hollow Mine discovered
```

### Completion Flags (USE THESE)
```
swamp_church_complete         # ✓ EXISTS - Swamp complete
hill_ruins_complete           # ⚠️ NEEDS VERIFICATION - Ruins complete
refugee_camp_complete         # ⚠️ NEEDS VERIFICATION - Refugee complete
red_hollow_mine_complete      # ✓ EXISTS - Mine complete
```

### Mayor Acknowledgment Flags (USE THESE - already exist!)
```
mayor_acknowledged_swamp_complete
mayor_acknowledged_ruins_complete
mayor_acknowledged_refugee_complete
mayor_acknowledged_mine_complete
```

### NPC Info Flags (USE THESE - already working!)
```
meredith_gave_swamp_info
garrick_gave_ruins_info
pete_gave_refugee_info
henrik_gave_shaft_quest
```

### Act Transition Flag (NEEDS TO BE ADDED)
```
act_two_started               # ⚠️ NEW - Triggers mayor office move
```

---

## 📋 PATH FORWARD - UPDATED PLAN

### PHASE 1: Minimal Changes to patron_selection_mayor.json

**STATUS:** Almost nothing needs to change!

The current mayor dialogue already:
- ✓ Sets `quest_active`
- ✓ Sets `mayor_gave_swamp_info`, `mayor_gave_ruins_info`, `mayor_gave_refugee_info`
- ✓ Directs player to NPCs

**ONLY CHANGE NEEDED:**
Make sure mayor doesn't set discovery flags directly. Based on project documents, it looks like this is already correct - mayor gives info flags, NPCs set discovery flags.

**ACTION:** Review patron_selection_mayor.json to confirm, no major changes needed.

---

### PHASE 2: Create redstone_town_mayor.json

**STATUS:** New file needed

This will use:
- ✓ Existing completion flags (`*_complete`)
- ✓ Existing acknowledgment flags (`mayor_acknowledged_*_complete`)
- All infrastructure already in place!

**ACTION:** Create new dialogue file using existing flags.

---

### PHASE 3: Verify/Add Missing Completion Flags

**PRIORITY ITEMS:**
1. Verify `hill_ruins_complete` exists in schema
2. Verify `refugee_camp_complete` exists in schema  
3. Verify these flags get set when locations are completed
4. Test that they persist in save files

**LOW PRIORITY:**
- Flag duplication cleanup (not breaking anything)
- Mine naming inconsistency (working as-is)

---

### PHASE 4: Add act_two_started Flag

**NEW FLAG NEEDED:** `act_two_started`

**Where to add:**
1. narrative_schema.json - Define it
2. Act II transition screen - Set it when player first leaves town
3. Mayor routing logic - Check it to determine tavern vs office
4. South Gate - Use it to skip intro on subsequent exits

---

### PHASE 5: Backup NPC Discovery (Optional)

**STATUS:** Primary sources working, backups can be added later

Current working primary sources:
- ✓ Meredith → Swamp
- ✓ Garrick → Ruins
- ✓ Pete → Refugees
- ✓ Henrik → Mine

**Backup sources to add:**
- Bernard → Ruins backup
- Cassia → Swamp backup
- Jenna → Refugee backup

**ACTION:** Lower priority, add in Phase 5

---

## 🎯 RECOMMENDED SESSION ORDER (REVISED)

### SESSION 1: Review & Minimal Mayor Changes (30 min)
1. Review patron_selection_mayor.json
2. Confirm mayor doesn't set discovery flags
3. Test existing Act I flow works

### SESSION 2: Verify Schema Flags (30 min)
1. Check narrative_schema.json for all needed flags
2. Add `act_two_started` flag definition
3. Add `hill_ruins_complete` if missing
4. Add `refugee_camp_complete` if missing

### SESSION 3: Create Office Mayor Dialogue (2 hours)
1. Create redstone_town_mayor.json
2. Use existing completion and acknowledgment flags
3. Implement routing logic based on flags
4. Test state transitions

### SESSION 4: Act II Transition & Mayor Movement (1.5 hours)
1. Verify act_two_start screen sets `act_two_started`
2. Add mayor location routing logic
3. Update South Gate with proper conditions
4. Test Act I → Act II transition

### SESSION 5: Testing & Polish (1 hour)
1. End-to-end testing
2. Verify all flags persist in saves
3. Test completion acknowledgments
4. Bug fixes

### SESSION 6: Backup NPCs (Optional - 1-2 hours)
1. Add Bernard ruins backup
2. Add Cassia swamp backup
3. Add Jenna refugee backup

**TOTAL TIME:** 5-7 hours (down from 9-12!)

---

## 🔧 TECHNICAL NOTES

### Flag Storage Locations
**narrative_flags:** Story progression, NPC interactions, quest status
**exploration_flags:** Location interactions, examinations, discoveries

**OVERLAP:** Some flags appear in both (legacy issue, non-breaking)

### Save Compatibility
All changes maintain backward compatibility:
- New flags initialize to false
- Existing flags remain unchanged
- No flag renames or deletions

### Schema Requirements
Must add to narrative_schema.json:
- `act_two_started` definition
- Verify `hill_ruins_complete` exists
- Verify `refugee_camp_complete` exists

---

## ✅ DECISION SUMMARY

**KEEP EXISTING:**
- `learned_about_*` discovery pattern ✓
- `discovered_old_mine_shaft` (mine discovery) ✓
- `*_complete` completion pattern ✓
- `mayor_acknowledged_*_complete` acknowledgment pattern ✓
- All NPC info flags ✓

**ADD NEW:**
- `act_two_started` flag ✓
- Verify/add `hill_ruins_complete`
- Verify/add `refugee_camp_complete`

**DO NOT CHANGE:**
- Flag names (save compatibility)
- Discovery flag patterns (working)
- NPC info flag patterns (working)

---

**END OF ANALYSIS**

*This analysis is based on actual save file data and reflects the real implementation state of the system.*