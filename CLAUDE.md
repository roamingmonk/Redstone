# CLAUDE.md — Terror in Redstone

> This file provides orientation for AI assistants working on this codebase. It covers architecture, conventions, workflows, and key patterns to follow. For detailed history, see `docs/decisions.md`. For full project overview, see `docs/project_context.md`.

---

## Project Overview

**Name:** Terror in Redstone
**Genre:** Classic 2D RPG with tactical turn-based combat
**Tech Stack:** Python 3.11+, Pygame
**Entry Point:** `python main.py`
**Architecture:** Event-driven, JSON-first content system

**One-Line Pitch:** Professional old-school RPG demonstrating modern game architecture with data-driven content creation.

---

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install pygame
python main.py
```

**No build system, CI/CD, or linting tools are configured.** There is no Makefile, no pytest, no pre-commit hooks. The project runs directly with `python main.py`.

---

## Repository Structure

```
Redstone/
├── main.py                    # Entry point — bootstrap only, no game logic
├── game_state.py              # SINGLE DATA AUTHORITY — all game data lives here
├── input_handler.py           # Input routing — delegates all events to EventManager
│
├── core/
│   └── game_controller.py     # Main coordinator — initializes all subsystems
│
├── game_logic/                # Stateless engines (process data, never store it)
│   ├── event_manager.py       # Message bus — all system communication
│   ├── dialogue_engine.py     # JSON-driven conversation system
│   ├── quest_engine.py        # Objective tracking with pagination
│   ├── combat_engine.py       # Turn-based battle mechanics
│   ├── character_engine.py    # Stats, advancement, party management
│   ├── inventory_engine.py    # Inventory and item management
│   ├── commerce_engine.py     # Merchant interactions
│   ├── save_manager.py        # Save/load (5 manual + quicksave + autosave)
│   ├── combat_ai.py           # Enemy AI decision-making
│   ├── data_manager.py        # Central JSON loading and caching
│   ├── spell_handlers.py      # Spell system management
│   └── movement_system.py     # Navigation and pathfinding
│
├── ui/                        # Presentation layer — rendering only
│   ├── screen_manager.py      # Screen lifecycle and state management
│   ├── base_location.py       # JSON-driven location base class (KEY PATTERN)
│   ├── combat_system.py       # Tactical combat UI rendering
│   ├── shopping_overlay.py    # Merchant UI
│   ├── notifications.py       # Floating XP text system
│   └── generic_dialogue_handler.py
│
├── screens/                   # Individual screen implementations (~47 files)
│   ├── title_menu.py
│   ├── character_creation.py
│   ├── character_overlay.py   # 4-tab character sheet
│   ├── quest_overlay.py
│   ├── inventory_overlay.py
│   ├── *_nav.py               # Location navigation screens
│   └── ...
│
├── utils/                     # Shared helpers
│   ├── constants.py           # Screen dimensions, colors, font configs
│   ├── narrative_schema.py    # Story flag validation (prevents mismatches)
│   ├── combat_loader.py       # Combat data management
│   ├── debug_manager.py       # F-key debug overlays
│   └── tabbed_overlay_utils.py
│
├── data/                      # ALL content as JSON — no hardcoded game data
│   ├── narrative_schema.json  # MASTER flag definitions for all quests/story
│   ├── items.json             # 100+ items with stats
│   ├── spells.json
│   ├── merchants.json
│   ├── dialogues/             # 60+ NPC conversation files
│   ├── locations/             # Location configs (auto-loaded)
│   ├── combat/
│   │   ├── enemies/           # 25+ enemy definitions
│   │   ├── encounters/        # 30+ encounter configs
│   │   └── battlefields/      # 15+ battlefield layouts
│   ├── npcs/                  # NPC definitions
│   ├── maps/                  # Tilemap data
│   ├── narrative/             # Act sequences, epilogue, intro
│   └── player/                # Classes, species, names, templates
│
├── assets/
│   ├── fonts/MedievalSharp-Regular.ttf
│   └── images/               # Backgrounds, sprites, icons, tiles
│
├── docs/                      # Project documentation
│   ├── project_context.md     # Living project overview (read this first)
│   ├── decisions.md           # 120+ Architecture Decision Records (ADRs)
│   └── ...                    # Implementation plans, guides
│
└── scripts/
    ├── dialogue_tester.py     # Console tool for testing NPC dialogue flows
    └── generate_repo_structure.py
```

---

## Core Architecture Principles

These four principles underpin every design decision. Do not violate them:

### 1. Single Data Authority
`game_state.py` (`GameState` class) is the **sole source of truth** for all game data. Game logic engines are **stateless processors** — they read from and write to `GameState` but never store state themselves.

```python
# CORRECT: engines receive and mutate game_state
def process_dialogue(self, game_state, npc_id):
    game_state.current_dialogue = npc_id

# WRONG: engine stores state
self.current_dialogue = npc_id  # Never do this in an engine
```

### 2. Event-Driven Communication
All system communication flows through `EventManager`. Systems do not call each other directly.

```python
# CORRECT: emit an event
self.event_manager.emit('DIALOGUE_STARTED', {'npc_id': npc_id})

# WRONG: direct cross-system call
self.combat_engine.start_combat(...)  # Don't call engines directly from UI
```

### 3. JSON-First Content
New content (NPCs, quests, locations, enemies, items) is defined in JSON files. Code changes should be minimal or zero for content additions.

### 4. Clean Layer Separation
- **Data Layer:** `data/` JSON files
- **State Layer:** `game_state.py`
- **Logic Layer:** `game_logic/` engines (stateless)
- **Event Bus:** `EventManager`
- **Presentation Layer:** `screens/`, `ui/`

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────┐
│  Presentation (screens/, ui/)               │
│  Rendering and user interaction only        │
└─────────────────────────────────────────────┘
                    ↕ Events only
┌─────────────────────────────────────────────┐
│  Event Bus (EventManager)                   │
│  All inter-system coordination              │
└─────────────────────────────────────────────┘
                    ↕ Events only
┌─────────────────────────────────────────────┐
│  Game Logic (game_logic/)                   │
│  Stateless processors: Dialogue, Quest,     │
│  Combat, Character, Inventory, Commerce     │
└─────────────────────────────────────────────┘
                    ↕ Read/Write
┌─────────────────────────────────────────────┐
│  GameState (game_state.py)                  │
│  Single source of truth for all data        │
└─────────────────────────────────────────────┘
                    ↕ Loads from
┌─────────────────────────────────────────────┐
│  Data Files (data/*.json)                   │
│  All game content defined here              │
└─────────────────────────────────────────────┘
```

---

## Key Patterns

### BaseLocation (Auto-Registration)
The most important pattern for adding new areas. A new location requires only a JSON config — no code registration needed.

```json
// data/locations/my_location.json
{
  "location_id": "my_location",
  "background": "assets/images/backgrounds/my_location.png",
  "navigation_actions": [...],
  "npcs": ["npc_id_1", "npc_id_2"]
}
```

See `ui/base_location.py` and `docs/decisions.md` (ADR-046, ADR-112) for full details.

### BaseTabbedOverlay
Universal framework for multi-tab overlays (Character, Quest, Inventory, Statistics). Self-registering — overlays auto-attach to the overlay system.

### Narrative Schema
`data/narrative_schema.json` is the master definition for all story flags, quests, and NPC mappings. Always define new flags here first. The `utils/narrative_schema.py` module validates flag usage to prevent mismatches.

### Combat Data (Three-File System)
Every combat encounter requires three coordinated JSON files:
- `data/combat/enemies/enemy_name.json` — Enemy stats and behavior
- `data/combat/encounters/encounter_name.json` — Encounter configuration
- `data/combat/battlefields/battlefield_name.json` — Terrain and layout

---

## Content Creation Workflows

### Adding a New NPC with Dialogue
1. Create `data/dialogues/{location}_{npc_name}.json`
2. Add NPC entry to `data/narrative_schema.json` (system_id, location, dialogue_file, story_flags)
3. Add to `data/merchants.json` if the NPC is a merchant
4. Reference NPC in location JSON (`data/locations/{location}.json`)
5. Add portrait: `assets/images/icons/characters/{npc_id}_portrait.jpg` (optional)
6. Ensure screen naming matches `location_id` from narrative schema

### Adding a New Location
1. Create `data/locations/{location_name}.json` with navigation actions and NPC references
2. Location auto-registers via `LocationManager` — **no code changes needed**
3. Add background image to `assets/images/backgrounds/`

### Adding a Combat Encounter
1. `data/combat/enemies/{enemy}.json` — Define the enemy
2. `data/combat/encounters/{encounter}.json` — Define the encounter
3. `data/combat/battlefields/{battlefield}.json` — Define the terrain
4. Trigger the encounter from dialogue/location data (data-driven)

### Adding a Quest
1. Define quest structure in `data/narrative_schema.json`
2. Set triggers (dialogue flags, discovery flags)
3. Quest automatically appears in quest overlay — no code needed

---

## Game Flow

### High-Level Player Journey
```
Title Screen → Character Creation → Intro Sequence →
Broken Blade Tavern → Mayor Quest → NPC Recruitment →
Combat System → World Exploration → Final Dungeon → Victory/Epilogue
```

### Initialization Order (main.py → game_controller.py)
```
1. pygame.init()
2. load_fonts(), load_images()
3. GameState() — data authority
4. GameController(screen, game_state, fonts, images, data_manager)
5. controller.initialize_all_systems()  — Phases 2–4: all subsystems
6. ScreenRegistry.register_all_screens(controller)
7. game_state.screen = "game_title"
8. Main loop: events → InputHandler → controller.run_current_screen()
```

### Combat Flow
```
Trigger → Load Encounter Data → Initiative Roll (DEX + d20) →
Turn Order → Tactical Grid → Multi-Party Actions →
Active Character Highlighted (CYAN) → Enemy AI → Victory/Defeat →
XP Awards → Return to World
```

---

## Debug Tools (In-Game)

| Key | Action |
|-----|--------|
| F1  | Show dialogue state |
| F2  | Show narrative flags |
| F3  | Show quest progress |
| F4  | Cycle day of week |
| F5  | Quick save |
| F7  | Manual save menu |
| F10 | Load game menu |
| I   | Inventory overlay |
| Q   | Quest overlay |
| C   | Character overlay |
| S / H | Statistics / Help overlay |
| B / Backspace / ESC | Back / close |

Console output shows event traces. All F-key overlays are managed by `utils/debug_manager.py`.

---

## Git Commit Conventions

This project uses **Architecture Decision Records (ADRs)**. The commit template (`.gitmessage.txt`) requires:

```
ADR-XXX: <Short summary (~50 chars)>

- <What files changed and why>
- <Impact: what it fixes, improves, or enables>
- <Optional: link to issue, doc section>
```

- Always reference the relevant ADR number from `docs/decisions.md`
- Keep the first line under ~50 characters
- When making a new architectural decision, add a new ADR entry to `docs/decisions.md`

---

## Testing Approach

There is **no automated test framework** (no pytest, no unittest). Testing is manual:

- F-key debug overlays for live state inspection
- Console logging for event tracing
- Save/load cycle validation
- `scripts/dialogue_tester.py` — console tool for testing NPC dialogue trees and flag states
  ```bash
  python scripts/dialogue_tester.py
  ```
- Incremental feature testing with manual regression checks

---

## Development Standards

### Code Quality
- **Modular:** Enforce clean data/logic/presentation separation — never blur these lines
- **Event-Driven:** Use `EventManager.emit()`, avoid direct cross-module calls
- **JSON-First:** New content belongs in `data/`, not hardcoded in Python
- **Error Handling:** Graceful fallbacks everywhere; the game must never crash
- **ADR-Driven:** Document architectural decisions in `docs/decisions.md` before implementing

### Style Conventions
- No linting tools are configured — follow existing code style in each file
- Docstrings are present in core modules; maintain them where they exist
- Type hints are used inconsistently — don't add them unless the surrounding code uses them
- Keep engines stateless; all mutable state belongs in `GameState`

### What to Avoid
- Adding state to engine classes (`game_logic/`)
- Direct imports between unrelated modules (use events)
- Hardcoding content that belongs in JSON
- Registering new screens/locations in code when auto-registration handles it
- Skipping ADR documentation for architectural decisions

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `main.py` | Bootstrap only — start here to understand init order |
| `game_state.py` | All game state — read this to understand data structure |
| `core/game_controller.py` | System coordinator — subsystem wiring |
| `game_logic/event_manager.py` | Event bus — all inter-system communication |
| `ui/base_location.py` | BaseLocation pattern — template for all areas |
| `utils/constants.py` | Screen size, colors, font configs |
| `utils/narrative_schema.py` | Flag validation utilities |
| `data/narrative_schema.json` | Master quest/flag/NPC registry |
| `docs/decisions.md` | 120+ ADRs — full architectural history |
| `docs/project_context.md` | Living project overview |

---

## Production-Ready Systems

- Character creation and advancement
- JSON-driven dialogue with branching narratives
- Commerce/merchant interactions
- Quest tracking with pagination
- Save/load (5 manual + quicksave + autosave)
- Universal overlay framework (Character, Quest, Inventory, Statistics, Help)
- Multi-party tactical turn-based combat (DEX-based initiative)
- BaseLocation auto-registration (zero-code area creation)
- XP rewards with floating text notifications

## In Active Development

- Combat refinement (enemy AI improvements, spell integration, party abilities)
- Additional location content using BaseLocation patterns
- Act 3 narrative alignment

## Known Technical Debt

- No automated test suite
- No CI/CD pipeline or linting configuration
- Potential orphaned code from architectural iterations — full audit recommended
- World map tile movement system planned but not started
- Type hints used inconsistently

---

*Last updated: 2026-03-02*
*For detailed decisions: `docs/decisions.md`*
*For implementation guides: `docs/`*
