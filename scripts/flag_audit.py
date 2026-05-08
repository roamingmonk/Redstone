#!/usr/bin/env python3
"""
flag_audit.py — Terror in Redstone flag cross-reference auditor.

Produces a report of:
  A) Flags READ but NEVER SET   (conditions that can never become true)
  B) Flags SET but NEVER READ   (dead flags — set but nothing uses them)
  C) Flags READ but NOT DECLARED in narrative_schema (npcs, locations,
     act_progression, quest_triggers, ui_flags, game_state_flags)
  D) Summary counts

Usage:
    python3 scripts/flag_audit.py
    (run from the project root, or any directory — paths are resolved relative
     to this script's location)
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR  = Path(__file__).resolve().parent
ROOT        = SCRIPT_DIR.parent
DIALOGUES   = ROOT / "data" / "dialogues"
ENCOUNTERS  = ROOT / "data" / "combat" / "encounters"
SCHEMA_FILE = ROOT / "data" / "narrative_schema.json"
REPORT_FILE = SCRIPT_DIR / "flag_audit_report.txt"

# ---------------------------------------------------------------------------
# Tokens that appear in condition strings but are NOT flags
# (character attributes, comparison values, keywords, etc.)
# ---------------------------------------------------------------------------
NON_FLAG_TOKENS = {
    # Python / condition keywords
    "and", "or", "not", "true", "false", "if", "else", "in",
    "True", "False", "None",
    # Character/game attributes used as expressions (not stored flags)
    "recruited_count",
    "mayor_family_status",
    "is_cavia",        # stored in character dict, not game_state
    "can_recruit_more",# computed at runtime, not a stored flag
    # String literal comparison values
    "all_saved", "partial", "none",
}

# ---------------------------------------------------------------------------
# Helper: recursively walk any JSON value and yield all "set_flag" effects
# ---------------------------------------------------------------------------
def iter_set_flags(obj):
    """Yield (flag_name, value) for every set_flag effect in obj."""
    if isinstance(obj, dict):
        if obj.get("type") == "set_flag" and "flag" in obj:
            yield obj["flag"], obj.get("value", True)
        for v in obj.values():
            yield from iter_set_flags(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_set_flags(item)


# ---------------------------------------------------------------------------
# Helper: recursively walk any JSON value and yield all requirements.flags keys
# and requirements.flag / not_flag / any_flag values
# ---------------------------------------------------------------------------
def iter_requirement_flags(obj):
    """Yield (flag_name, source_description) for every flag checked in requirements."""
    if isinstance(obj, dict):
        if "requirements" in obj:
            req = obj["requirements"]
            if isinstance(req, dict):
                # requirements.flags dict
                for flag_name in req.get("flags", {}).keys():
                    yield flag_name, "requirements.flags"
                # requirements.flag  (single)
                if "flag" in req:
                    yield req["flag"], "requirements.flag"
                # requirements.not_flag
                if "not_flag" in req:
                    yield req["not_flag"], "requirements.not_flag"
                # requirements.any_flag  (list)
                for flag_name in req.get("any_flag", []):
                    yield flag_name, "requirements.any_flag"
        for v in obj.values():
            yield from iter_requirement_flags(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from iter_requirement_flags(item)


# ---------------------------------------------------------------------------
# Helper: extract flag-like tokens from a condition string
# Condition strings look like:
#   "!meredith_talked && mayor_talked && !casper_returned_ring_to_meredith"
#   "act_two_started && mayor_family_status == 'all_saved' && !mayor_post_victory_complete"
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(r"\b([a-z_][a-zA-Z0-9_]*)\b")

def extract_condition_flags(condition_str):
    """Return set of flag-like token names from a condition expression string."""
    if not isinstance(condition_str, str):
        return set()
    # Strip string literals first (e.g. 'all_saved')
    cleaned = re.sub(r"'[^']*'", "", condition_str)
    cleaned = re.sub(r'"[^"]*"', "", cleaned)
    tokens = TOKEN_RE.findall(cleaned)
    result = set()
    for tok in tokens:
        if tok in NON_FLAG_TOKENS:
            continue
        try:
            int(tok)
            continue
        except ValueError:
            pass
        result.add(tok)
    return result


# ===========================================================================
# 1. COLLECT FLAGS SET
# ===========================================================================
# flags_set: flag_name -> list of source strings
flags_set = defaultdict(list)

# 1a. Dialogue JSON set_flag effects
for jfile in sorted(DIALOGUES.glob("*.json")):
    try:
        data = json.loads(jfile.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  WARN: could not parse {jfile.name}: {e}")
        continue
    short = f"dialogues/{jfile.name}"
    for flag, val in iter_set_flags(data):
        flags_set[flag].append(f"{short} (set_flag effect, value={val})")

# 1b. Combat encounter quest_flags (story_progress.quest_flags keys)
for jfile in sorted(ENCOUNTERS.glob("*.json")):
    try:
        data = json.loads(jfile.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  WARN: could not parse {jfile.name}: {e}")
        continue
    short = f"encounters/{jfile.name}"
    qf = data.get("rewards", {}).get("story_progress", {}).get("quest_flags", {})
    for flag_name, flag_data in qf.items():
        if isinstance(flag_data, dict) and flag_data.get("value") is True:
            flags_set[flag_name].append(f"{short} (combat quest_flag)")
        elif isinstance(flag_data, bool) and flag_data:
            flags_set[flag_name].append(f"{short} (combat quest_flag)")


# ===========================================================================
# 2. COLLECT FLAGS READ
# ===========================================================================
# flags_read: flag_name -> list of source strings
flags_read = defaultdict(list)

schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))

# 2a. dialogue_state_mapping condition strings
dsm = schema.get("dialogue_state_mapping", {})
for npc_key, states in dsm.items():
    if npc_key.startswith("_comment"):
        continue
    if not isinstance(states, dict):
        continue
    for state_name, condition in states.items():
        if state_name.startswith("_comment"):
            continue
        if not isinstance(condition, str):
            continue
        for flag in extract_condition_flags(condition):
            flags_read[flag].append(
                f"narrative_schema.dialogue_state_mapping[{npc_key}][{state_name}]"
            )

# 2b. Dialogue JSON requirements.flags / .flag / .not_flag / .any_flag
for jfile in sorted(DIALOGUES.glob("*.json")):
    try:
        data = json.loads(jfile.read_text(encoding="utf-8"))
    except Exception:
        continue
    short = f"dialogues/{jfile.name}"
    for flag, req_type in iter_requirement_flags(data):
        flags_read[flag].append(f"{short} ({req_type})")

# 2c. quest_triggers dialogue_flag values
qt = schema.get("quest_triggers", {})
for trigger_key, trigger_data in qt.items():
    if isinstance(trigger_data, dict):
        df = trigger_data.get("dialogue_flag")
        if df:
            flags_read[df].append(
                f"narrative_schema.quest_triggers[{trigger_key}].dialogue_flag"
            )


# ===========================================================================
# 3. COLLECT FLAGS DECLARED
# ===========================================================================
flags_declared = set()

# 3a. npcs[*] — conversation_flag, story_flags, interaction_flags
for npc_id, npc_data in schema.get("npcs", {}).items():
    cf = npc_data.get("conversation_flag")
    if cf:
        flags_declared.add(cf)
    sf = npc_data.get("story_flags", {})
    if isinstance(sf, dict):
        for val in sf.values():
            if isinstance(val, str):
                flags_declared.add(val)
    for v in npc_data.get("interaction_flags", {}).values():
        if isinstance(v, str):
            flags_declared.add(v)

# 3b. ui_flags keys
for flag_key in schema.get("ui_flags", {}).keys():
    flags_declared.add(flag_key)

# 3c. locations — completion_flag, discovery_flag, explored_flag, story_flags
for loc_data in schema.get("locations", {}).values():
    for key in ("completion_flag", "discovery_flag", "explored_flag"):
        f = loc_data.get(key)
        if f:
            flags_declared.add(f)
    sf = loc_data.get("story_flags", [])
    if isinstance(sf, list):
        flags_declared.update(sf)
    elif isinstance(sf, dict):
        flags_declared.update(v for v in sf.values() if isinstance(v, str))

# 3d. act_progression flags
for act_data in schema.get("act_progression", {}).values():
    for key in ("start_flag", "completion_flag", "act_three_complete_flag",
                "location_completed_flag"):
        f = act_data.get(key)
        if f:
            flags_declared.add(f)

# 3e. quest_triggers dialogue_flags
for trigger_data in schema.get("quest_triggers", {}).values():
    if isinstance(trigger_data, dict):
        df = trigger_data.get("dialogue_flag")
        if df:
            flags_declared.add(df)

# 3f. game_state_flags (skip computed/character-attribute entries)
for flag_key, flag_data in schema.get("game_state_flags", {}).items():
    if isinstance(flag_data, dict) and (flag_data.get("is_computed") or
                                         flag_data.get("is_character_attribute")):
        continue
    flags_declared.add(flag_key)


# ===========================================================================
# 4. BUILD REPORT
# ===========================================================================
all_set   = set(flags_set.keys())
all_read  = set(flags_read.keys())
all_decl  = flags_declared

read_never_set  = sorted(all_read - all_set)
set_never_read  = sorted(all_set - all_read)
read_undeclared = sorted(all_read - all_decl)

lines = []

def h(text):
    lines.append(text)

h("=" * 72)
h("TERROR IN REDSTONE — FLAG AUDIT REPORT")
h("=" * 72)
h("")

# ---------------------------------------------------------------------------
# Section A — READ but NEVER SET
# ---------------------------------------------------------------------------
h(f"=== A) FLAGS READ BUT NEVER SET ({len(read_never_set)} flags) ===")
h("    These conditions can never become true — possible typos or missing")
h("    set_flag effects.")
h("")
if read_never_set:
    for flag in read_never_set:
        h(f"  {flag}")
        sources = flags_read[flag]
        # deduplicate while preserving order
        seen = set()
        for src in sources:
            if src not in seen:
                h(f"    Read in: {src}")
                seen.add(src)
        h("")
else:
    h("  (none)")
    h("")

# ---------------------------------------------------------------------------
# Section B — SET but NEVER READ
# ---------------------------------------------------------------------------
h(f"=== B) FLAGS SET BUT NEVER READ ({len(set_never_read)} flags) ===")
h("    These flags are written but nothing checks them — dead flags or")
h("    features not yet wired up.")
h("")
if set_never_read:
    for flag in set_never_read:
        h(f"  {flag}")
        sources = flags_set[flag]
        seen = set()
        for src in sources:
            if src not in seen:
                h(f"    Set in:  {src}")
                seen.add(src)
        h("")
else:
    h("  (none)")
    h("")

# ---------------------------------------------------------------------------
# Section C — READ but NOT DECLARED
# ---------------------------------------------------------------------------
h(f"=== C) FLAGS READ BUT NOT DECLARED IN SCHEMA ({len(read_undeclared)} flags) ===")
h("    No canonical definition exists. Risky: no schema validation,")
h("    default value assumptions may be wrong.")
h("")
if read_undeclared:
    for flag in read_undeclared:
        h(f"  {flag}")
        sources = flags_read[flag]
        set_info = "  [also SET]" if flag in all_set else "  [NEVER SET either — double orphan]"
        h(f"    {set_info}")
        seen = set()
        for src in sources[:6]:  # cap at 6 to keep report readable
            if src not in seen:
                h(f"    Read in: {src}")
                seen.add(src)
        if len(sources) > 6:
            h(f"    ... and {len(sources)-6} more locations")
        h("")
else:
    h("  (none)")
    h("")

# ---------------------------------------------------------------------------
# Section D — Summary
# ---------------------------------------------------------------------------
h("=== D) SUMMARY ===")
h("")
h(f"  Total unique flags SET:       {len(all_set)}")
h(f"  Total unique flags READ:      {len(all_read)}")
h(f"  Total flags DECLARED:         {len(all_decl)}")
h(f"")
h(f"  A) Read but never set:        {len(read_never_set)}")
h(f"  B) Set but never read:        {len(set_never_read)}")
h(f"  C) Read but not declared:     {len(read_undeclared)}")
h(f"")
h(f"  Flags set AND read (healthy):  {len(all_set & all_read)}")
h(f"  Flags declared but not read:   {len(all_decl - all_read)}")
h("")
h("=" * 72)

report_text = "\n".join(lines)

# ===========================================================================
# 5. OUTPUT
# ===========================================================================
print(report_text)
REPORT_FILE.write_text(report_text, encoding="utf-8")
print(f"\nReport written to: {REPORT_FILE}")
