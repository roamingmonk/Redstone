# Terror in Redstone — Claude Code Handoff Document

**Prepared:** June 12, 2026
**Prepared by:** Claude (Cowork analysis session) — read-only audit, no code was changed
**Repo:** `/Users/dennis/Development/Redstone` (branch `main`, HEAD `69b1e19`)
**Objective:** Deliver a complete, functioning, polished game. Ship-it path: finish the remaining sprint work in dependency order; defer structural refactoring to a post-release pass.

---

## 0. How to Use This Document

Work through the phases **in order**. Each phase lists objective, files, concrete steps, and acceptance criteria. Do not skip ahead: Phase 1 confirms the baseline that every later phase assumes, and audio (Phase 7) is intentionally last per the project's own sprint plan.

**For Dennis:** every phase in §4 begins with a ready-to-use `COPY-PASTE PROMPT` block. Start a fresh Claude Code session in `/Users/dennis/Development/Redstone`, paste the block for the current phase, and let it run. One phase per session keeps context clean. Where a phase references a sprint task (F-01, G-01, etc.), the prompt instructs Claude Code to open the full task text in `docs/Redstone_CopyPaste_Prompts_Apr30.md` — those prompts are not duplicated here on purpose, so there is a single source of truth.

**Model choice:** each prompt block below names a recommended model. The rule behind it: **Sonnet is the default** — these phases are deliberately well-specified (exact files, known gaps, acceptance criteria), which is exactly what Sonnet is good and economical at. **Opus is reserved for unpredictable debugging** (Session 6, and optionally late Session 8), where unknown bugs can span dialogue + flags + combat at once. You can switch mid-session with `/model` — the escalation signal is Sonnet repeatedly failing to fix the same symptom. If Opus isn't available on your plan or is burning limits, running everything on Sonnet is fine.

Authoritative companion documents inside the repo:

- `docs/Redstone_CopyPaste_Prompts_Apr30.md` — the active sprint plan. Tasks F-01, F-02, G-01–G-04, I-05, I-06 contain full self-contained prompts; this handoff tells you when to execute them and supplies corrections where the sprint doc is stale.
- `docs/project_context.md` — architecture orientation (mostly accurate; status section is from Oct 2025 and outdated).
- `docs/decisions.md` — ADR log. Consult before changing any architectural pattern.
- `docs/Dialogue_issues_-_what_to_review_-Nov_5.md` — **read before touching any dialogue file.** Documents four recurring bug classes and the conventions that prevent them.
- `docs/Asset_Generation_HuggingFace.md` — FLUX image-generation workflow (note: its claim that the engine loads `{npc_id}_idle.png` sprite sheets from `assets/images/sprites/npcs/` is **aspirational, not implemented** — see §5.3).

**Prime directives for every session:**

1. After completing a task from the sprint doc, update its status marker in `docs/Redstone_CopyPaste_Prompts_Apr30.md` (use `<COMPLETED>` or `<COMPLETED — DEVIATION: …>`). **Also append a session log entry to §8 (Session Log) at the bottom of this document** — status, deviations, blockers, commits — using the template there. Do not edit the phase plans themselves; the log is where reality gets recorded.
2. One commit per task, conventional-commit style (matches existing history, e.g. `feat(assets): …`, `fix(quest): …`).
3. Never rename existing narrative flags — save-file compatibility depends on them.
4. Dialogue JSON files must follow `{location}_{npcname}.json` where the NPC name segment contains **no underscores** (the screen manager parses with `rsplit('_', 1)`).
5. Every flag referenced in `dialogue_state_mapping` conditions must be registered in that NPC's `story_flags` in `data/narrative_schema.json`, or condition evaluation silently fails.
6. `SCREEN_CHANGE` events use `target_screen` / `source_screen` keys (never `target`), emitted on the active event manager.

---

## 1. Project Snapshot (verified June 12, 2026)

| Item | Verified fact |
|---|---|
| Stack | Python 3.11+ target, Pygame (runs clean on Python 3.10 / pygame 2.6.1 in a Linux sandbox) |
| Size | ~51,300 lines of Python (excluding venvs/worktrees), 171 JSON content files, 73 dialogue files |
| Boot test | `python main.py` initializes all systems, loads 12/12 backgrounds, registers all screens, reaches title screen, shuts down cleanly (exit 0) |
| Architecture | Event-driven; `GameState` single data authority; stateless engines in `game_logic/`; JSON-first content; BaseLocation auto-registration (17 nav screens use it) |
| Story content | Acts I, II, III + epilogue structurally complete: town, tavern, 4 Act II locations (Hill Ruins, Red Hollow Mine, Swamp Church, Refugee Camp), 5-level dungeon, boss (Taborex), victory screen, epilogue slides, credits |
| Flags | 266 narrative flags initialized at startup; startup validator (H-02) reports clean |
| Progression | 3-level XP curve implemented and calibrated (sprint A-01–A-04 complete; A-04 deviation: cosmetic Level 4 awarded on boss victory) |
| Audio | **Nothing exists.** No `audio_manager.py`, no audio assets, no `data/audio/` dir. `pygame.mixer.quit()` in shutdown is the only reference |
| Tests | No automated tests. Manual testing via F-key debug overlays (F1–F8) and `scripts/dialogue_tester.py` |
| Dependencies | No `requirements.txt` / `pyproject.toml`. Only third-party dep observed: `pygame` |

### Sprint scoreboard (`docs/Redstone_CopyPaste_Prompts_Apr30.md`)

**Done (verified against git history):** A-01–A-04, B-01, B-02, C-01–C-04, D-01–D-08, E-01–E-03, F-03, H-01–H-08, I-01–I-04, J-01, J-02.

**Remaining — this is the work queue:**

| Task | What | Phase below |
|---|---|---|
| F-01 | Wire combat tileset fields in battlefield JSONs + missing wall/floor art | Phase 3 |
| F-02 | Portrait rendering consistency across screens | Phase 4 |
| I-05 | Combat exit button should require an exit tile | Phase 5 |
| I-06 | Opportunity attacks (design decision needed — optional) | Phase 5 |
| G-01–G-04 | Entire audio system (manager, assets, music wiring, SFX) | Phase 7 |

**Stale markers to fix in the sprint doc (Phase 0):** C-03 carries both a deviation note and a completed marker — confirm formatting; D-08 has a stray `]rewards` line above its status; Section E's `<Completed>` sits on the section header rather than E-01 itself.

---

## 2. Architecture Map (what lives where)

```
main.py                     # bootstrap only (136 lines) — contains a TEST BLOCK to remove (§6, Phase 8)
game_state.py               # GameState: single source of truth (415 lines)
input_handler.py            # global input routing (1,095 lines)
core/game_controller.py     # coordinator + ScreenRegistry (660 lines)
game_logic/                 # 16 stateless engines
  combat_engine.py          #   4,449 lines — god module, works; do NOT refactor pre-release
  character_engine.py       #   1,967 lines
  combat_ai.py              #   1,723 lines
  dialogue_engine.py        #   1,495 lines
  save_manager.py, quest_engine.py, inventory_engine.py, movement_system.py, …
screens/                    # 36 screens; 17 nav screens subclass BaseLocation
ui/                         # screen_manager.py (2,064), combat_system.py (1,656), base_location.py (997), …
utils/                      # 24 modules: narrative_schema, flags (FLAGS constants), combat_sprite_manager,
                            #   tile_graphics, combat_loader, constants, debug_manager, …
data/                       # JSON content: narrative_schema.json (master), dialogues/ (73),
                            #   locations/ (6), combat/{enemies,encounters,battlefields}, npcs/, player/, maps/
scripts/                    # flag_audit.py + report, dialogue_tester.py, repo-structure generators
assets/images/              # 45 MB: backgrounds, icons, portraits, tiles, sprites
saves/                      # 5 slots + quicksave + autosave (currently tracked in git — fix in Phase 0)
Redstone.app                # macOS launcher (Session 1, Phase 1) — opens Terminal, runs venv/bin/python main.py.
                            #   Compiled AppleScript app (osacompile), not a shell-script executable — a raw shell
                            #   script as CFBundleExecutable triggers a bogus Rosetta prompt on Apple Silicon even
                            #   though nothing here is Intel code. Icon: assets/images/redstone_icon.png → .icns.
```

### Conventions and gotchas (learned from the project's own bug history)

- **Dialogue file naming:** `{location}_{npc}.json`, NPC segment has no underscores. `refugee_camp_leader.json` broke because it parsed as npc=`leader`; it was renamed `refugee_camp_marta.json`.
- **Combat return navigation:** action-hub combats must set both `game_state.previous_screen` and `game_state.pre_combat_location`.
- **Flag context:** dialogue conditions only see flags registered in the NPC's `story_flags` or the global registry.
- **Flag duplication:** some flags exist in both `narrative_flags` and `exploration_flags` (legacy, non-breaking). Do not consolidate pre-release.
- **Singletons:** `CombatSpriteManager`, `DataManager`, `narrative_schema` are module-level singletons; import their accessor functions, don't instantiate.
- **FLAGS constants:** Python code references flags via `utils/flags.py` (`FLAGS.MAYOR_TALKED`); JSON uses raw strings (validated at startup).

---

## 3. Code Quality Findings (for awareness — most are POST-RELEASE)

These were found in the read-only audit. Only the items marked **[pre-release]** belong in the ship-it path; everything else goes to a post-release backlog so it doesn't destabilize a working game.

1. **[pre-release] Test/debug residue in `main.py`:** lines ~40–58 contain a `setup_victory_test()` block marked "REMOVE THIS AFTER TESTING" (currently inert — the call is commented out), and line ~104 sets `controller.debug_mode = True`. Remove/disable for release (Phase 8).
2. **[pre-release] Repo hygiene:** `__pycache__/*.pyc` and `saves/*.json` are git-tracked and constantly dirty; two virtualenvs (`.venv/`, `venv/`) live in the tree; 3 stale worktrees under `.claude/worktrees/` are already marked "prunable" by git (all `claude/*` branches are 0 commits ahead of main — safe to prune); meaningful work is **uncommitted** (new Cavia dialogue JSONs, sprite references, asset doc). Phase 0 fixes all of this.
3. **[pre-release] No `requirements.txt`** — one line (`pygame>=2.5`) plus a pinned Python version note. Phase 0.
4. **Flag audit tool false positives:** `scripts/flag_audit.py` only scans JSON-side flag effects, so it reports flags set in Python (e.g. `act_two_started`, set in `screens/act_two_transition.py:104`) as "read but never set." Likewise `is_cavia` / `can_recruit_more` are computed context values, not stored flags. Treat report sections A and C with suspicion; do not "fix" these. (Post-release: extend the audit script to scan Python attribute assignments.)
5. **God modules (post-release):** `combat_engine.py` (4,449), `screen_manager.py` (2,064), `character_engine.py` (1,967). They work and are heavily interlinked. Splitting them now risks the release; split after shipping (suggested cut lines: combat → turn manager / action resolution / effects / log; screen_manager → registry / transition handling / overlay routing).
6. **159 set-but-never-read flags** (audit section B): intentionally deferred per H-08. Don't delete pre-release; saves reference them.
7. **`print`-based logging everywhere** (~hundreds of emoji debug prints): fine for development; Phase 8 silences the noisy ones on the startup/shutdown path. Post-release: swap to `logging` with levels.
8. **No automated tests:** post-release, add smoke tests around save/load round-trip, dialogue state mapping evaluation, and XP threshold math — the three systems whose regressions have historically eaten the most time.
9. **Duplicate root-level modules:** `game_state.py` and `input_handler.py` live at repo root while the architecture docs describe them under `core/`. Harmless; leave as-is (imports everywhere assume root).
10. **`data/OG_items.json`** appears to be a legacy item library kept deliberately (C-03 deviation note confirms items.json is a "library for future use"). Leave it.

---

## 4. THE SEQUENTIAL PLAN

### Phase 0 — Repo hygiene & baseline commit (~30 min, low risk)

**COPY-PASTE PROMPT (Session 1 — runs Phase 0 and Phase 1 together · model: Sonnet):**

```
I'm working on my Python/Pygame CRPG "Terror in Redstone" in this repo.
Read the handoff document at "Terror in Redstone an Old style RPG Game/CLAUDE_CODE_HANDOFF.md"
in full before doing anything.

Then execute Phase 0 (repo hygiene) exactly as written, with one addition:
move CLAUDE_CODE_HANDOFF.md into docs/ as part of the hygiene commit so all
future sessions find it there.

Rules:
- Show me the proposed .gitignore changes and the full list of files you will
  commit BEFORE committing anything.
- Do not delete any file from disk; "untrack" means git rm --cached only.
- Never rename narrative flags.

When Phase 0 is complete and git status is clean, verify the game still boots
(python main.py to title screen), then walk me through the Phase 1 manual
verification checklist step by step — I will play the game; you tell me what
to check and record the results. If anything in Phase 1 fails, treat it as a
blocker bug: diagnose and fix it before we finish the session.
```

**Objective:** start from a clean, reproducible, fully-committed state.

1. Review the uncommitted changes (`git status`): new Cavia dialogue files (`data/dialogues/mine_cavia_*.json`), `assets/borders/`, `assets/images/sprites/npcs/` (thorman reference images), `assets/images/redstone_icon.png`, `docs/Asset_Generation_HuggingFace.md`, `scripts/flag_audit_report.txt`, `.claude/`. Commit the content and docs; decide whether reference images belong in the repo (recommended: yes, they're small).
2. Add to `.gitignore`: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `saves/*.json`, `.claude/`, `assets/images/icons/characters/player_portraits/active/`. Then `git rm -r --cached` the tracked `__pycache__` dirs and `saves/*.json` (keep the files on disk — the game needs the saves locally).
3. Create `requirements.txt`: `pygame>=2.5`. Note Python 3.11+ in README.
4. Prune stale worktrees: `git worktree prune` (all 3 `.claude/worktrees/*` entries are already marked prunable; verified all `claude/*` branches are 0 commits ahead of main). Delete the merged local branches.
5. Fix the stale status markers in `docs/Redstone_CopyPaste_Prompts_Apr30.md` (see §1).
6. Commit: `chore(repo): hygiene pass — gitignore, requirements, prune worktrees, commit pending content`.

**Acceptance:** `git status` clean; `python main.py` still boots to title.

### Phase 1 — Baseline verification (~30 min)

*(No separate prompt — Phase 1 runs at the end of Session 1; see the Phase 0 prompt above.)*

**Objective:** confirm the critical path works before building on it.

1. Launch, start a new game, complete character creation (test both Human and Cavia, Fighter class), reach the Broken Blade tavern.
2. Talk to the Mayor, accept the quest, trigger the rat-basement combat, win it, confirm: XP floating indicator appears, level-up fires at 300 XP with yellow portrait border, quest log updates.
3. F5 quicksave → F10 load → confirm state restores (screen, party, flags).
4. Log any failure as a blocker bug and fix before proceeding. **Do not start Phase 2 with a broken Act I.**

**Acceptance:** Act I plays start-to-tavern-to-first-combat with XP/level/save all working.

### Phase 2 — Install generated art assets (~30 min)

**COPY-PASTE PROMPT (Session 2 · model: Sonnet):**

```
I'm working on Terror in Redstone. Read docs/CLAUDE_CODE_HANDOFF.md, then
execute Phase 2: install the generated asset pack per
"Terror in Redstone an Old style RPG Game/generated_assets/INSTALL.md".

Rules:
- Do NOT install the player/ folder — the game already has better player art.
- Do not overwrite the existing cellar_* wall tiles.
- After copying, boot the game and paste me the console lines showing the new
  wall/floor/NPC assets loading (they should replace the "fallback" messages).
- Regression check: trigger the rat-basement cellar combat and confirm it
  renders exactly as before.
- Commit as: feat(assets): add procedural combat tilesets, floor tiles, and
  NPC world sprites
```

**Objective:** drop in the asset pack generated alongside this handoff (see §5 manifest). All target paths and filenames match what the engine already loads — **only the floor-tile additions require a code touch, listed in Phase 3.**

1. Copy `generated_assets/walls/*` → `assets/images/sprites/walls/`
2. Copy `generated_assets/terrain/*` → `assets/images/tiles/terrain/`
3. Copy `generated_assets/npcs/*` → `assets/images/tiles/characters/npcs/` (create the dir)
4. Do **not** install `generated_assets/player/*` — the game already has better 9-frame player sheets at `assets/images/sprites/player/`. The generated 4-frame sheets are spare alternates only.
5. Boot the game; console should report wall/floor/sprite loads instead of fallback messages.
6. Commit: `feat(assets): add procedural combat tilesets, floor tiles, NPC and player world sprites`.

**Acceptance:** boot log shows the new assets loading; combat in the cellar still renders correctly (regression check).

### Phase 3 — F-01: Combat tileset wiring (~2 h)

**COPY-PASTE PROMPT (Session 3 · model: Sonnet — discovery work already done in this doc):**

```
I'm working on Terror in Redstone. Read docs/CLAUDE_CODE_HANDOFF.md Phase 3,
then open task F-01 in docs/Redstone_CopyPaste_Prompts_Apr30.md and execute it —
BUT apply the verified corrections listed in the handoff's Phase 3 first
(correct wall-tile path, the two-layer floor mapping in combat_system.py and
combat_sprite_manager.py, and the swamp_exterior.json tileset bug).

Read utils/combat_sprite_manager.py and ui/combat_system.py::_get_floor_type
before editing anything, and show me your gap report (step 4 of F-01) before
making changes.

When done: verify the Phase 3 acceptance criteria, mark F-01 <COMPLETED> (or
<COMPLETED — DEVIATION: …>) in the sprint doc, and commit.
```

**Objective:** every combat encounter renders a location-appropriate backdrop.

Execute sprint task F-01 (full prompt in the sprint doc), with these **verified corrections** to its briefing:

- Wall tiles load from `assets/images/sprites/walls/` (`COMBAT_WALLS_PATH`), **not** `assets/images/tiles/combat/` as the F-01 prompt claims. Naming: `{tileset}_{wall_north|wall_south|wall_east|wall_west|corner_nw|corner_ne|corner_sw|corner_se}.png`, 48×48.
- Floor tiles load from `assets/images/tiles/terrain/` at 16×16; `combat_sprite_manager.load_floor_tiles()` currently hardcodes only two keys (`stone_floor_16x16`, `dirt_floor_16x16`). To use the new floors, extend that `floor_map` dict with the new filenames (grass, cobblestone, swamp, ritual) — a few-line change.
- Battlefield JSONs already reference these tilesets: `cellar` (exists), `dungeon`, `dungeon_crypt`, `underground_tunnel`, `ruins_outdoor`, `urban_alley`, `camp_clearing` (art for all six supplied in the asset pack).
- Known data bug: `data/combat/battlefields/swamp_exterior.json` has `tileset: cellar` / `terrain: stone_floor` — wrong for a swamp. Point it at the new swamp/outdoor assets.
- Floor resolution has **two layers**, and both need edits: (a) `ui/combat_system.py::_get_floor_type()` maps battlefield `terrain.default` → tile key, but only knows `stone_floor`, `cobblestone`, `dirt`, `grass`, `wood`; battlefield values `ritual_floor`, `corrupted_floor`, `dark_stone`, `dungeon_floor` all silently default to stone. (b) `combat_sprite_manager.load_floor_tiles()` only *loads* two keys (`stone_floor_16x16`, `dirt_floor_16x16`), so even mapped keys like `cobblestone_street_16x16` (whose PNG already exists) currently fall back. Extend both maps. Note: for cobblestone the engine expects key/file `cobblestone_street_16x16.png` (already present) — the generated `cobblestone_floor_16x16.png` is a redundant spare.

**Acceptance:** trigger one combat per location (cellar, mine, ruins, alley, camp, dungeon, swamp) — each shows distinct walls/floor, grid remains readable, no fallback warnings in console. Commit per F-01's suggested message.

### Phase 4 — F-02: Portrait rendering consistency (~1–2 h)

**COPY-PASTE PROMPT (Session 4 · model: Sonnet):**

```
I'm working on Terror in Redstone. Read docs/CLAUDE_CODE_HANDOFF.md Phase 4,
then open task F-02 in docs/Redstone_CopyPaste_Prompts_Apr30.md and execute it
as written. Portraits resolve via utils/party_display.py / utils/npc_display.py
using the {npc_id}_portrait.jpg convention.

Also: garrick_portrait exists as both .jpg and .png in
assets/images/icons/characters/npc_portraits/ — determine which one the loader
actually uses and delete the loser.

When done: verify the Phase 4 acceptance criteria, mark F-02 <COMPLETED> in the
sprint doc, and commit.
```

Execute sprint task F-02 as written (portrait sizing/border/fallback consistency across dialogue, party display, character sheet, combat). No corrections needed; `utils/npc_display.py` resolves portraits by `{npc_id}_portrait.jpg` convention. Note `garrick_portrait` exists as both `.jpg` and `.png` — check which one wins and delete the loser.

**Acceptance:** portraits identical in style/size across all screens that show them; missing portraits fall back to `default_portrait.jpg` without errors.

### Phase 5 — Combat UX completion: I-05 and I-06 (~2–3 h)

**COPY-PASTE PROMPT (Session 5 · model: Sonnet):**

```
I'm working on Terror in Redstone. Read docs/CLAUDE_CODE_HANDOFF.md Phase 5,
then open task I-05 in docs/Redstone_CopyPaste_Prompts_Apr30.md and execute it
(combat Exit button must require standing on an exit tile).

Then read task I-06 (opportunity attacks) but do NOT implement it. Instead,
give me a one-paragraph recommendation: implement now, or defer to the sequel?
Consider combat balance at the 3-level cap and implementation risk. I'll decide,
and you record the decision as a short entry in docs/decisions.md.

When done: verify acceptance criteria, update both task markers in the sprint
doc, and commit.
```

1. **I-05 (do):** combat Exit button should only work on an exit tile. Full prompt in sprint doc.
2. **I-06 (decide):** opportunity attacks. This is a `[PLAN FIRST]` task — implement only if combat feels too easy to disengage from during Phase 6 playtesting. A reasonable ship decision is to **defer to the sequel** and note it in `decisions.md`.

**Acceptance:** can't flee combat from arbitrary tiles; decision on I-06 recorded.

### Phase 6 — Full playtest pass #1 (~4–6 h play + fix time)

**COPY-PASTE PROMPT (Session 6 — keep this session open while you play · model: OPUS — live debugging of unknown bugs across systems; this is where the heavier model earns its cost):**

```
I'm working on Terror in Redstone. Read docs/CLAUDE_CODE_HANDOFF.md Phase 6.

I'm about to do a full Human Fighter playthrough (title → epilogue → credits)
following the Run 1 checklist in docs/Revised-Completion-plan.md Week 8.
Your job in this session:
1. Create BUGS.md in the repo root with sections: Critical / High / Medium / Low.
2. As I report issues, log each one with: where it happened, what I expected,
   what actually happened.
3. Fix Critical and High bugs as they come in (crash, progression block, save
   corruption, combat softlock, missing UI, quest/dialogue not firing).
   Medium/Low just get logged.
4. Pay special attention to the historical trouble spots listed in the
   handoff's Phase 6 (Act II ↔ town transitions, mayor acknowledgments,
   combat return navigation, XP pacing vs xp_balance targets).
One commit per bug fix. Ready? Wait for my first report.
```

**Objective:** one complete Human Fighter run, title → epilogue → credits.

- Follow the Run 1 checklist in `docs/Revised-Completion-plan.md` Week 8.
- Triage bugs: fix Critical (crash, progression block, save corruption, combat softlock) and High (UI missing, quest log error, dialogue not firing) immediately; log Medium/Low to a `BUGS.md`.
- Watch specifically: Act II ↔ town transitions and mayor acknowledgment dialogue (the area with the most historical flag bugs), combat return navigation from action-hub fights, XP pacing vs. the targets in narrative_schema's `xp_balance` design comment (L2 ≈ end Act I, L3 ≈ mid Act II).

**Acceptance:** complete run with zero Critical/High bugs outstanding.

### Phase 7 — Audio: G-01 → G-02 → G-03 → G-04 (~4–6 h)

**COPY-PASTE PROMPT (Session 7a — infrastructure + sourcing guide · model: Sonnet):**

```
I'm working on Terror in Redstone. Read docs/CLAUDE_CODE_HANDOFF.md Phase 7,
then execute tasks G-01 and G-02 from docs/Redstone_CopyPaste_Prompts_Apr30.md
in that order.

Hard requirement for G-01: the game must run identically when audio asset
files are absent — every AudioManager call degrades silently.
For G-02: produce the sourcing guide with exact tracks/SFX needed, target
formats (.ogg preferred), and where each license note goes
(data/audio/LICENSES.md). I will download the files myself between sessions.

When done: update both task markers in the sprint doc and commit each task
separately.
```

**COPY-PASTE PROMPT (Session 7b — after you've downloaded the audio files into data/audio/ · model: Sonnet):**

```
I'm working on Terror in Redstone. I've placed the audio files in data/audio/
per the G-02 sourcing guide. Read docs/CLAUDE_CODE_HANDOFF.md Phase 7, then
execute tasks G-03 (music wiring per the music map in the task) and G-04
(SFX wiring) from docs/Redstone_CopyPaste_Prompts_Apr30.md.

Acceptance before committing: music transitions exploration↔combat smoothly;
SFX fire on button/attack/spell/door/gold/damage/level-up; volume controls
work and persist; and the game still runs cleanly with data/audio/ renamed
away (fallback test). Update both task markers and commit each task separately.
```

Audio is last by design ("all gameplay must be complete and tested before audio work begins").

1. **G-01:** create `utils/audio_manager.py` skeleton (full prompt in sprint doc): `play_music(track_id, loop, fade_in)`, `stop_music(fade_out)`, `play_sfx(sfx_id, volume)`, separate music/SFX volume, hard requirement: the game must run identically when asset files are absent.
2. **G-02:** source assets — 2 music loops (exploration, combat) + ~10 SFX. Royalty-free sources per `Revised-Completion-plan.md` Week 7 (incompetech, FreePD, OpenGameArt). Document license per file in `data/audio/LICENSES.md`.
3. **G-03:** wire music to screen transitions (music map in sprint doc prompt).
4. **G-04:** wire SFX (button click, melee/ranged hit, spell, door, gold, damage, level-up).

**Acceptance:** music transitions exploration↔combat smoothly; SFX fire; game fully functional with audio files deleted; volume controls persist.

### Phase 8 — Release prep (~2–3 h)

**COPY-PASTE PROMPT (Session 8 · model: start Sonnet for the cleanup steps; switch to Opus via /model if the Cavia/speedrun playtests surface gnarly bugs):**

```
I'm working on Terror in Redstone. Read docs/CLAUDE_CODE_HANDOFF.md Phase 8
and execute it:
1. Remove the setup_victory_test() block from main.py; set
   controller.debug_mode = False; gate the F1–F4/F8 debug hotkeys behind a
   DEBUG constant in utils/constants.py (keep F5/F7/F10 saves live).
2. Quiet the startup/shutdown console spam (keep error output).
3. Update README.md (real repo URL, requirements, controls) and the status
   section of docs/project_context.md.
4. Show me the final diff before committing.

Then give me the Run 2 (Cavia Wizard) and Run 3 (speedrun) checklists from
docs/Revised-Completion-plan.md Week 8 — I'll play them, and we fix anything
Critical/High that surfaces, same protocol as the Phase 6 session.
When both runs pass and the Success Criteria in Revised-Completion-plan.md
all check out, tag v1.0.0.
```

1. Remove the `setup_victory_test()` block from `main.py`; set `controller.debug_mode = False`; decide whether F1–F8 debug hotkeys ship (recommend: keep F5/F7/F10 saves, disable F1–F4/F8 debug state dumps behind a `DEBUG` constant in `utils/constants.py`).
2. Quiet the startup/shutdown console spam (keep error prints).
3. Playtest pass #2: Cavia Wizard run (verifies E-01–E-03 content: Henrik recognition, three Act II flavor reactions, Aethel Lexicon scene, Cavia epilogue) + a speedrun for progression blockers.
4. Update `README.md` (real repo URL, requirements, controls) and `docs/project_context.md` status section.
5. Tag `v1.0.0`. Optional: itch.io packaging notes in `Revised-Completion-plan.md` contingency section.

**Acceptance:** the Success Criteria list in `docs/Revised-Completion-plan.md` (§"SUCCESS CRITERIA") all pass.

---

## 5. Generated Asset Pack Manifest

Location: `generated_assets/` (delivered alongside this document). All PNG, with alpha where relevant. Style: 16-color-palette procedural pixel art with dithering, tuned to read clearly at game scale. They are deliberately conservative placeholders-plus — good enough to ship, easy to swap for FLUX art later via the same filenames.

### 5.1 Combat wall tilesets → `assets/images/sprites/walls/` (48×48 each, 8 per set)

| Tileset | Theme | Files |
|---|---|---|
| `dungeon` | dark stone block walls | `dungeon_wall_north.png` … `dungeon_corner_se.png` |
| `dungeon_crypt` | pale bone-inlaid stone | `dungeon_crypt_*.png` (8) |
| `underground_tunnel` | rough-hewn mine rock + timber | `underground_tunnel_*.png` (8) |
| `ruins_outdoor` | weathered, moss-eaten masonry | `ruins_outdoor_*.png` (8) |
| `urban_alley` | brick + plaster town walls | `urban_alley_*.png` (8) |
| `camp_clearing` | wooden palisade / brush line | `camp_clearing_*.png` (8) |
| `swamp` | rotting timber + slime stone | `swamp_*.png` (8) — for the swamp_exterior battlefield fix |

### 5.2 Floor tiles → `assets/images/tiles/terrain/` (16×16, tileable)

`dirt_floor_16x16.png` (already expected by code, was missing), `grass_floor_16x16.png`, `cobblestone_floor_16x16.png`, `swamp_floor_16x16.png`, `ritual_floor_16x16.png`, `dungeon_floor_16x16.png`. **Code touch required:** add these keys to `floor_map` in `combat_sprite_manager.load_floor_tiles()` (Phase 3).

### 5.3 NPC world sprites → `assets/images/tiles/characters/npcs/` (32×32, single frame)

`guard.png`, `merchant.png`, `citizen.png`, `noble.png`, `henrik.png` — these five exact names are already loaded by `tile_graphics.load_character_sprites()`; the directory simply didn't exist, so all NPCs render as colored-circle fallbacks today. (The `{npc_id}_idle.png` sprite-sheet system described in `docs/Asset_Generation_HuggingFace.md` is **not implemented** in code — if you want per-NPC animated world sprites, that's new engine work; flag it as a post-release feature.)

### 5.4 Player sprites (SPARE — do not install by default)

`generated_assets/player/player_{down,up,left,right}.png` are 128×32 4-frame sheets. The game **already has** 288×32 9-frame player sheets at `assets/images/sprites/player/` (the loader reads `PLAYER_SPRITES_PATH = assets/images/sprites/player`, auto-detects sheet width, 100 ms/frame). The empty `assets/images/tiles/characters/player/` directory is a red herring — not the load path. Keep the generated sheets only as emergency replacements.

---

## 6. Known Issues & Decisions Already Made (do not relitigate)

- 3-level cap is final for this release; level 4 on boss victory is cosmetic only (A-04 deviation).
- Items library (`items.json`) keeps unused items on purpose; only merchant stock lists are curated (C-03 deviation).
- Flag duplication between `narrative_flags`/`exploration_flags` ships as-is.
- Villain is **Taborex** everywhere (renamed from Vexthar, J-01).
- Trinkets are flavor + minor stat display (I-04 done).
- **F-key bindings kept as-is** (F1–F4 debug, F5 quicksave, F7 save menu, F8 debug XP, F10 load) — not remapped off macOS's system-reserved F-key range. macOS intercepts F1–F3 and F7–F12 system-wide (brightness/Mission Control/media/volume) before the app ever sees the keydown; on a Mac, players must hold **Fn** with those keys, or enable "Use F1, F2, etc. keys as standard function keys" in System Settings → Keyboard. This is an OS-level behavior the app cannot override. Documented in `docs/project_context.md` §8; revisit only if playtesting shows this blocks non-technical players — the fallback is remapping saves/debug off the reserved range or exposing them via on-screen menu buttons (Save/Load already have overlay equivalents; debug keys do not).
- Expansive ideas (world-map tile movement, more spells, formation tactics, per-NPC animated sprites) → Godot sequel wishlist, not this release.

## 7. Suggested Post-Release Backlog (carry into a new doc after v1.0.0)

1. Split `combat_engine.py` into turn management / action resolution / effects / logging modules.
2. Replace print-logging with the `logging` module.
3. Extend `scripts/flag_audit.py` to scan Python-side flag assignments (kills the false positives).
4. Add smoke tests: save/load round-trip, dialogue state-mapping evaluation, XP thresholds.
5. Dead-flag cleanup (audit section B) with a save-migration shim.
6. Consolidate `narrative_flags` / `exploration_flags`.
7. Per-NPC animated world sprites (implement the `{npc_id}_idle.png` loader the asset doc describes).
8. `assets/borders/gold_frame_64_ugly.png` — an unrefined dialogue-box border option, committed as-is in the Phase 0 hygiene pass. Revisit/redesign before using it anywhere.

---

## 8. Session Log (append-only — newest entry at top)

Claude Code: at the end of every session, append an entry here using this template. Keep it under ~10 lines. This log is how the planning agent (Cowork Claude) reassesses status if the plan needs to change — record *why* things deviated, not just what happened.

```
### Session N — Phase X — YYYY-MM-DD
Status: COMPLETE / PARTIAL / BLOCKED
Done: <one line per major item>
Deviations: <what differed from the plan and why — "none" if clean>
Blockers/Open: <anything unresolved, bugs deferred to BUGS.md>
Commits: <hashes + one-word description>
Next: <confirm next phase, or flag if plan needs review>
```

### Session 1 — Phase 0/1 — 2026-07-05
Status: PARTIAL
Done: Phase 0 hygiene pass (gitignore fixes, untracked pycache/saves, requirements.txt, pruned 3 clean worktrees + deleted 6 merged claude/* branches, fixed stale sprint-doc markers, moved this handoff doc into docs/, committed pending Cavia/asset content); verified `python main.py` boots clean (266 flags, validation passed). Pushed to origin/main (199dcad). Built `Redstone.app` macOS launcher (compiled AppleScript app, custom icon from `assets/images/redstone_icon.png`) so the game can run outside VS Code / be pinned to the Dock. Found and fixed a real bug during Phase 1 F-key testing: F5 quicksave had no player-visible confirmation — added a "Game Saved"/"Save Failed" floating-text indicator in `game_logic/save_manager.py::_handle_quicksave_request`, reusing the existing `SHOW_FLOATING_TEXT` system.
Deviations: kept `assets/borders/gold_frame_64_ugly.png` per Dennis's direction rather than dropping it (§7 backlog item 8). Decided to keep F1–F10 bindings as-is rather than remap off macOS's reserved F-key range — see §6 decision log and `docs/project_context.md` §8 for the Fn-key note to players.
Blockers/Open: Phase 1's character-creation → tavern → combat → quicksave/load checklist has not been run yet (session got diverted into launcher setup and F-key/Rosetta troubleshooting first). Resume there next.
Commits: 199dcad chore(repo) hygiene pass (pushed). Quicksave-indicator fix not yet committed.
Next: run the Phase 1 manual verification checklist (character creation, Mayor quest, rat-basement combat, F5/F10 save-load round trip) before moving to Phase 2.
