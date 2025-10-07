# Terror in Redstone — Project Context

> **Living overview of the project.** This document provides orientation for developers (human or AI) joining the project. For detailed decisions, see `docs/decisions.md`. For implementation specifics, see individual system documentation.

---

## 1. Project Snapshot

**Name:** Terror in Redstone  
**Genre:** Classic 2D RPG with tactical turn-based combat  
**Tech Stack:** Python 3.11+, Pygame  
**Architecture:** Event-driven, JSON-first content system  
**Development Phase:** Core systems complete, combat integration in progress  
**Current Date:** October 2025

**One-Line Pitch:**  
Professional old-school RPG demonstrating modern game architecture with data-driven content creation.

---

## 2. What's Built & Working

### ✅ Core Systems (Production-Ready)
- **Character System:** Creation, advancement, party management (player + 3 NPCs), XP notifications
- **Dialogue System:** JSON-driven conversations with narrative schema state management
- **Commerce:** Merchant interactions, item purchasing, inventory management
- **Quest System:** JSON-driven objectives with pagination, XP rewards, flag-based progression
- **Save/Load:** Complete persistence (5 manual slots + quicksave + autosave) with portrait restoration and screen resume
- **Overlay Framework:** Universal self-registering overlays (Character, Quest, Inventory, Statistics, Help, Save/Load)
- **Tactical Combat:** Multi-party turn-based combat with DEX-based initiative, collision detection, active character highlighting
- **BaseLocation System:** Auto-registration architecture - new areas require only JSON, zero code changes

### 🔨 In Active Development
- **Combat Refinement:** Enemy AI improvements, spell system integration, party member abilities
- **Additional Location Content:** Redstone Town Church, Alley, roaming NPCs using established BaseLocation patterns

### 📋 Planned (Foundation Ready)
- World map tile movement system
- Key region development (Hill Ruins, Swamp Church, Refugee Camp)
- Additional location content (Redstone Town Church, Alley, roaming NPCs, etc.)
- Advanced spell system (mage/cleric abilities)
- Formation strategies and character-specific equipment effects

---

## 3. Architecture Overview

### Core Principles
1. **Single Data Authority:** `GameState` is sole source of truth; engines are stateless processors
2. **Event-Driven:** `EventManager` coordinates all system communication
3. **JSON-First:** New content = JSON file creation, minimal code changes
4. **Separation of Concerns:** Clean layers (data / logic / presentation)

### System Layers

```
┌─────────────────────────────────────────────┐
│  Presentation (screens/, ui/)              │
│  - Rendering and user interaction          │
└─────────────────────────────────────────────┘
                    ↕ Events
┌─────────────────────────────────────────────┐
│  Event Bus (EventManager)                  │
│  - All system coordination                 │
└─────────────────────────────────────────────┘
                    ↕ Events
┌─────────────────────────────────────────────┐
│  Game Logic (game_logic/)                  │
│  - Dialogue, Quest, Combat, Character      │
│  - Stateless processors                    │
└─────────────────────────────────────────────┘
                    ↕ Read/Write
┌─────────────────────────────────────────────┐
│  Game State (game_state.py)                │
│  - Single source of truth                  │
│  - All game data lives here                │
└─────────────────────────────────────────────┘
                    ↕ Loads
┌─────────────────────────────────────────────┐
│  Data Files (data/)                        │
│  - JSON configuration for all content      │
└─────────────────────────────────────────────┘
```

### Key Architectural Patterns
- **BaseLocation:** Data-driven location screens with auto-registration (see `ui/base_location.py`)
- **BaseTabbedOverlay:** Universal overlay system with self-registration
- **Narrative Schema:** Centralized flag definitions preventing mismatches (`data/narrative_schema.json`)
- **Combat Data Loader:** Three-layer JSON system (enemies/encounters/battlefields)
- **XP Notifications:** Floating text system for real-time player feedback (`ui/notifications.py`)

---

## 4. Major Architectural Decisions

For complete ADR history, see `docs/decisions.md`. Key decisions that shape the codebase:

- **ADR-001:** Single Data Authority (GameState pattern)
- **ADR-002:** Event System Foundation (EventManager hub)
- **ADR-015:** ScreenManager Architecture (lifecycle management)
- **ADR-044:** Universal Self-Registering Overlays
- **ADR-046:** BaseLocation Core (JSON-driven locations)
- **ADR-057:** Recruitment System Alignment (party synchronization)
- **ADR-063:** Dialogue System Architecture (state-based conversations)
- **ADR-093:** Quest System Restructuring (pagination, JSON-driven)
- **ADR-094:** Combat Data Layer Foundation (three-file JSON approach)
- **ADR-104:** Multi-Party Tactical Combat (DEX initiative, character states)
- **ADR-112:** BaseLocation Auto-Registration (zero-code area creation)

---

## 5. Current Game Flow

### High-Level Player Journey
```
Title Screen → Character Creation → Intro Sequence → 
Broken Blade Tavern → Mayor Quest → NPC Recruitment → 
[Combat System] → World Exploration → Final Dungeon
```

### Recruitment Flow Example
```
Talk to Mayor → Accept Quest (flag: quest_active) → 
Talk to Recruitable NPCs → Party Formed (max 3 NPCs) → 
Party Synchronized to GameState
```

### Combat Flow (Operational)
```
Combat Trigger → Load Encounter Data → 
Initiative Roll (DEX + d20) → Turn Order Established →
Tactical Grid Display → Multi-Party Turn-Based Actions →
Active Character Highlighted (CYAN) → Enemy AI Responds →
Victory/Defeat Resolution → XP Awards → Return to World
```

---

## 6. File Organization

### Key Directories
```
redstone/
├── core/
│   ├── game_controller.py      # Main game coordinator
│   └── game_state.py            # Single data authority
│
├── game_logic/                  # Stateless game engines
│   ├── dialogue_engine.py       # Conversation processing
│   ├── quest_engine.py          # Objective tracking
│   ├── combat_engine.py         # Battle mechanics
│   ├── character_engine.py      # Stats & advancement
│   └── event_manager.py         # Message bus
│
├── screens/                     # Individual screen modules
│   ├── character_overlay.py     # 4-tab character sheet
│   ├── quest_overlay.py         # Quest tracking
│   ├── statistics_overlay.py    # 3-tab game statistics
│   └── [others]
│
├── ui/                          # Presentation layer
│   ├── screen_manager.py        # Screen lifecycle
│   ├── base_location.py         # JSON-driven locations
│   ├── combat_system.py         # Tactical combat UI
│   └── notifications.py         # Floating XP notifications
│
├── utils/                       # Shared utilities
│   ├── narrative_schema.py      # Story flag coordination
│   ├── combat_loader.py         # Combat data management
│   └── constants.py             # Colors, fonts, dimensions
│
└── data/                        # JSON content
    ├── narrative_schema.json    # Master flag definitions
    ├── dialogues/               # NPC conversations
    ├── locations/               # Location configurations
    ├── combat/                  # Enemies, encounters, battlefields
    └── player/                  # Classes, items, templates
```

---

## 7. Content Creation Workflow

### Adding a New NPC (Dialogue)
1. Create `data/dialogues/location_npcname.json` (see `docs/adding_npc_dialogue.md`)
2. Add NPC to `data/narrative_schema.json` (story flags and mapping)
3. Reference NPC in location JSON (no code changes needed)

### Adding a New Location
1. Create `data/locations/location_name.json` (see BaseLocation architecture doc)
2. Define navigation actions, NPC references, image path
3. Location auto-loads via LocationManager (no code registration needed)

### Adding a Combat Encounter
1. Define enemy in `data/combat/enemies/enemy_name.json`
2. Create encounter in `data/combat/encounters/encounter_name.json`
3. Define battlefield in `data/combat/battlefields/battlefield_name.json`
4. Reference encounter from dialogue/location (data-driven trigger)

### Adding a Quest
1. Define quest structure in `data/narrative_schema.json`
2. Set quest triggers (dialogue flags, discovery flags)
3. Quest automatically appears in quest overlay with objectives

---

## 8. Getting Oriented as a New Developer

### If You Want to Understand...

**Overall Architecture:**
- Read this document first (you are here!)
- Review `docs/decisions.md` for key ADRs (ADR-001, -002, -015, -044, -046)
- Examine `game_state.py` to see data structure

**The Dialogue System:**
- Read `docs/NPC Dialogue Creation Sep 14 v2.docx`
- Examine `game_logic/dialogue_engine.py`
- Look at `data/dialogues/broken_blade_garrick.json` as example

**The Combat System:**
- Read `docs/Terror in Redstone - Tactical Combat System V1.0`
- Examine `utils/combat_loader.py` for data management
- Review `game_logic/combat_engine.py` for business logic
- Check `ui/combat_system.py` for presentation

**BaseLocation Pattern:**
- Read `docs/BaseLocation Architecture Implementation Plan`
- Examine `ui/base_location.py` for class hierarchy
- Look at `data/locations/broken_blade.json` as example

**Quest System:**
- Review ADR-093 in `docs/decisions.md`
- Examine `game_logic/quest_engine.py`
- Check `data/narrative_schema.json` for quest definitions

### Common Development Tasks

**Debug Game State:**
- Press F1 (dialogue state), F2 (flags), F3 (quest progress)
- Check console output for event tracing

**Test a Feature:**
- F5 = Quick Save
- F7 = Manual Save Menu
- F10 = Load Game Menu

**Hotkeys (In-Game):**
- I = Inventory Overlay
- Q = Quest Overlay  
- C = Character Overlay
- S = Statistics Overlay
- H = Help Overlay
- B/Backspace/ESC = Back/Close

---

## 9. Development Standards

### Code Quality Expectations
- **Modular:** Clean separation between data/logic/presentation
- **Event-Driven:** Use EventManager, avoid direct coupling
- **JSON-First:** New content should require minimal/no code changes
- **Error Handling:** Graceful fallbacks, never crash
- **Documentation:** ADR for architectural decisions, inline comments for complex logic

### Testing Approach
- Manual testing with F-key debug overlays
- Console logging for event tracing
- Save/load validation for state persistence
- Incremental feature addition with regression testing

---

## 10. Project Status Summary

**Strengths:**
- Professional event-driven architecture established
- JSON-driven content pipeline functional for all major systems
- Core RPG systems complete, stable, and production-ready
- Multi-party tactical combat with initiative system operational
- BaseLocation auto-registration enables zero-code area creation
- Clean separation of concerns throughout
- Excellent foundation for rapid content expansion

**Active Work:**
- Combat refinement (enemy AI, spell integration, party abilities)
- Additional location content using established patterns
- Advanced spell system for mage/cleric classes

**Technical Debt:**
- Code cleanup needed - multiple architectural iterations may have left orphaned code
- Potential duplicate functions across modules requiring consolidation
- Legacy patterns may exist alongside modern implementations
- Full codebase audit recommended to streamline and remove dead code
- Combat system has minor enhancement opportunities (enemy multi-attack, spell variety)
- World map tile movement system planned but not started

**Ready for Content Expansion:**
- Additional NPCs via JSON dialogue files
- New locations/areas via BaseLocation JSON configs (auto-registers)
- New quests via narrative schema definitions
- New combat encounters via three-file JSON system
- Full party combat scenarios with existing framework

---

**Last Updated:** October 6, 2025  
**For Detailed Changes:** See `docs/decisions.md`  
**For Implementation Help:** See system-specific docs in `/docs`