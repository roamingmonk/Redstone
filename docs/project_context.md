# Terror in Redstone - Project Context

## 1) Project Snapshot
- **Name:** Terror in Redstone
- **One-liner:** Professional-grade 2D RPG framework evolved from monolithic Pygame prototype to event-driven architecture
- **Primary language / runtime:** Python 3.11+
- **Main framework/libs:** Pygame (rendering & input), JSON (data), custom EventManager
- **Dev environment:** VS Code + Git (repo private by default)
- **Current Status:** Production-ready character creation, tavern system, and overlay infrastructure

## 2) Purpose & Goals
- **Motivation:** Transform working prototype into professional, extensible RPG framework ready for rapid content expansion
- **Player-facing:** Tavern-centered narrative, branching dialogue, inventory/party management, quest tracking
- **Dev-facing:** New content (NPCs, locations, quests) created with JSON only; minimal code changes required
- **Success criteria:**
  - ✅ **Event-driven coordination via EventManager** (Complete - Sep 2025)
  - ✅ **Dialogue system fully JSON-driven** with 3+ conversation states and branching (Complete)
  - ✅ **Professional patron NPC system** with event-driven architecture (Complete)
  - ✅ **Engines are stateless**, using GameState as Single Data Authority (Complete)
  - ✅ **Character creation modernization** with semantic action architecture (Complete - Sep 2025)
  - ✅ **Save/Load system modernization** with event-driven overlay management (Complete - Sep 2025)
  - 🎯 **ScreenManager refactoring** from 1000+ lines to modular overlay architecture (In Progress)

## 3) Current Development Phase
**Active Focus:** Screen Architecture Refactoring (Phase 1 of 3)
- **Immediate Goal:** Replace bloated ScreenManager with professional tabbed overlay system
- **Timeline:** 8-10 sessions across 3 phases
- **Expected Outcome:** 60-70% code reduction in screen management with standardized patterns

### Non-Goals (current milestone)
- Multiplayer networking
- Combat engine (planned for future phases)
- World navigation system (planned for future phases)

## 4) Constraints & Assumptions
- **OS:** Windows, macOS, Linux
- **Input:** Keyboard/mouse (controller support deferred)
- **Resolution policy:** Pixel-art scaling, fixed logical sizes for UI buttons (200px width standard)
- **Services:** Local-only, no network or backend dependencies

## 5) Architecture Overview

### 5.1 Core Layers (Established Architecture)
- **Data Authority:** `game_state.py` as single source of truth, plus external JSONs under `/data`
- **Engines:** Pure business logic (`inventory_engine.py`, `dialogue_engine.py`, `character_engine.py`, `save_manager.py`)
- **Presentation:** Screens and UI components, pure rendering only
- **Coordination:** `game_controller.py` orchestrates, `event_manager.py` routes events
- **Input Management:** `input_handler.py` provides semantic action abstraction

### 5.2 Component Responsibility Boundaries (Professional Standards)
**Clear Separation of Concerns:**
- **Engines:** Domain/business logic only (Character, Inventory, Commerce, Dialogue, SaveManager)
- **ScreenManager:** Navigation flow and UI state management 
- **GameController:** Pure coordination without business logic (50% reduction achieved)
- **InputHandler:** Semantic action system replacing hardcoded click handling

**Event Routing Patterns:**
- **Domain Events → Engines:** Business logic processing
- **UI Events → ScreenManager:** Navigation and display state
- **Cross-cutting → EventManager:** Centralized event hub

### 5.3 File Structure (Current - Production Ready)
```
Terror in Redstone/
├── main.py                     # Clean entry point with application lifecycle
├── game_state.py              # Single data authority with comprehensive state
├── core/
│   ├── game_controller.py     # Thin coordinator (reduced from 1000+ to ~400 lines)
│   ├── event_manager.py       # Professional event hub
│   ├── input_handler.py       # Semantic action system
│   └── save_manager.py        # Complete save/load business logic
├── game_logic/                # Professional engine architecture
│   ├── quest_engine.py        # ✅ NEW: Event-driven quest management with XP integration
│   ├── character_engine.py    # ✅ ENHANCED: Party XP tracking and quest event handling
│   ├── inventory_engine.py    # Pure business logic for item management
│   ├── commerce_engine.py     # Shopping and merchant logic
│   ├── dialogue_engine.py     # JSON-driven conversation system
│   └── data_manager.py        # Centralized data loading coordination
├── screens/                   # Event-driven screen modules
│   ├── character_creation.py  # Fully modernized with semantic actions
│   ├── title_menu.py         # Professional title and menu system
│   ├── tavern.py             # Complete tavern with NPC recruitment
│   ├── quest_overlay.py      # ✅ NEW: Professional 2-tab quest interface
│   ├── inventory.py          # Professional overlay (refactoring target)
│   ├── quest_log.py          # Legacy quest display (being replaced)
│   ├── character_sheet.py    # Character display overlay (refactoring target)
│   ├── help_screen.py        # Help system overlay (refactoring target)
│   ├── save_game.py          # Modernized save overlay
│   ├── load_game.py          # Modernized load overlay
│   └── shopping.py           # Professional merchant system
├── ui/
│   ├── screen_manager.py     # Screen lifecycle and overlay management (refactoring target)
│   ├── tabbed_overlay_utils.py # ✅ Professional overlay base classes
│   ├── generic_dialogue_handler.py  # Universal NPC conversation system
│   └── screen_handlers.py    # Click handling registration
├── utils/
│   ├── quest_system.py       # ✅ ENHANCED: Core quest logic with 5-quest structure
│   ├── constants.py          # Game constants and configuration
│   ├── graphics.py           # Reusable drawing utilities
│   └── overlay_utils.py      # Shared overlay functionality
├── data/
│   ├── dialogues/            # JSON-driven conversation trees with quest triggers
│   │   ├── tavern_garrick.json # ✅ ENHANCED: Quest triggers and rat basement unlock
│   │   └── tavern_[patron].json
│   ├── player/
│   │   ├── character_names.json    # Dynamic name generation
│   │   └── character_classes.json  # Class definitions and mechanics
│   └── npcs/                 # NPC data definitions
└── assets/
    ├── fonts/                # MedievalSharp with fallback protection
    └── images/               # Standardized artwork pipeline
```

### 5.4 Event-Driven Architecture (Established Patterns)
**Professional Screen Registration:**
```python
screen_manager.register_render_function("stats", draw_stats_screen,
    enter_hook=lambda _: self.register_stats_screen_clickables())
```
- Screens self-register clickable regions on entry
- ScreenManager stays generic (no hardcoded screen names)
- Follows Open/Closed Principle for extensibility

**Semantic Action System:**
```python
# Instead of hardcoded coordinates
input_handler.register_semantic_action("START_GAME", start_button_rect)
# Routes to
event_manager.emit("START_GAME", {"source": "main_menu"})
```
**Quest System Event Flow:**
```python
# Quest Completion → XP Distribution → Level Up Detection
quest_engine.emit("QUEST_COMPLETED", {"xp_reward": 200})
character_engine.handle_quest_completion(event_data)
character_engine.emit("LEVEL_UP_AVAILABLE", {"characters": ["player", "gareth"]})
```


### 5.5 Current Event Flow
```mermaid
flowchart TD
  A[main.py] --> B[GameController]
  B --> C[EventManager]
  C --> D[QuestEngine]
  C --> E[CharacterEngine] 
  C --> F[DialogueEngine]
  C --> G[InventoryEngine]
  C --> H[CommerceEngine]
  C --> I[SaveManager]
  D & E & F & G & H & I --> J[GameState]
  B --> K[ScreenManager]
  B --> L[InputHandler]
  K --> M[Screens/UI]
  L --> C
  M --> L
```

## 6) Data & Content Management
- **Dialogue:** Comprehensive JSON system with quest triggers, information discovery XP, and dynamic unlocks
- **Quests:** 5-quest structure (1 primary: Terror in Redstone, 4 secondary: Party Building + 3 Locations)
- **NPCs:** Standardized JSON schema with dialogue integration and recruitment mechanics
- **Character Classes:** JSON-driven progression with XP tables and ability unlocks
- **Save System:** Professional file management with quest state persistence and party XP tracking
- **Items:** Structured item data with categories, icons, and equipment mechanics

## 7) Recent Major Achievements (Sep 2025)

### Architecture Modernization Complete
- **Character Creation System:** Full modernization with semantic action architecture across 8 screens
- **Save/Load Systems:** Event-driven overlay management with proper business logic separation  
- **Input System:** Professional semantic action system replacing hardcoded click handling
- **Event Architecture:** Comprehensive EventManager hub with proper component decoupling

### Quest System Integration Complete
- **Professional Quest Engine:** Event-driven quest management with XP integration and party tracking
- **Character Progression:** Party XP distribution, level-up detection, exponential progression (levels 1-5)
- **Quest Structure:** Primary quest (main story) + Secondary quests (locations, party building, special unlocks)
- **Dynamic Content:** Rat basement quest unlocks when party assembled, information discovery XP

### Code Quality Improvements
- **GameController Reduction:** 1000+ lines → ~400 lines (60% reduction achieved)
- **Dependency Injection:** Professional 3-phase initialization following game engine patterns
- **Separation of Concerns:** Clean boundaries between engines, presentation, and coordination
- **Error Handling:** Comprehensive safety nets and graceful degradation

### User Experience Enhancements
- **Context-Sensitive Input:** Intelligent hotkey blocking preventing UI conflicts
- **Professional Overlays:** Consistent save/load experience with proper state management
- **Educational Systems:** Class-aware character creation with guidance and warnings
- **Robust Save System:** Complete character data persistence with portraits and metadata

## 8) Active Development: Screen Architecture Refactoring

### Current Challenge
**ScreenManager Bloat:** 1000+ lines with 20+ specialized registration methods
- Multiple `register_*_clickables()` methods for each screen type
- Inconsistent overlay management patterns
- Difficult maintenance and extension

### Solution: Professional Tabbed Overlay System
**3-Phase Refactoring Roadmap:**

**Phase 1: Tabbed Overlay Foundation (Sessions 1-5)**
- Create `BaseTabbedOverlay` class with keyboard navigation
- Convert Help (1 tab), Character (2 tabs), Quest (2 tabs), Inventory (4 tabs)
- **Target:** 75% reduction in overlay registration methods

**Phase 2: Modal Dialog System (Sessions 6-7)**  
- Standardize confirmation and file dialogs
- Separate modal behavior from content overlays
- **Target:** Consistent dialog patterns across system

**Phase 3: Location Screen System (Sessions 8-10)**
- Create `BaseLocation` class for tavern-style interactions
- Data-driven location configuration
- **Target:** Template system for rapid location creation

### Expected Outcomes
- **Code Reduction:** ScreenManager 1000+ lines → ~300-400 lines (60-70% reduction)
- **Maintainability:** Adding overlays becomes configuration, not coding
- **Consistency:** All overlays follow identical interaction patterns
- **Scalability:** Framework ready for rapid content expansion

**Completed Integration:**
- ✅ **QuestEngine:** Event-driven quest management with 5-quest structure
- ✅ **Character XP System:** Party tracking, level progression, quest completion rewards
- ✅ **Event Flow:** Quest completion → XP distribution → level-up detection → character sheet notifications
- ✅ **Quest Overlay Creation:** Professional 2-tab interface (Active | Completed)

**In Progress:**
- 🎯 **ScreenManager Integration:** Replace legacy quest_log.py with quest_overlay.py
- 🎯 **Hardcoded Quest Cleanup:** Remove orphaned quest functions and legacy data structures
- 🎯 **Testing & Validation:** Ensure quest progression works through real gameplay

### Remaining Overlay Refactoring Roadmap

**Phase 2: Quest Overlay Completion (Current Session)**
- Convert quest log to professional 2-tab overlay with real quest data
- Eliminate legacy hardcoded quest functions
- Test complete quest progression workflow

**Phase 3: Character Sheet Enhancement (Next Session)**
- Add level-up notifications and progression indicators
- Implement level-up button for character advancement
- Integrate party member progression display

**Phase 4: Inventory Overlay Conversion (Future Session)**
- Convert inventory to 4-tab overlay (Weapons | Armor | Items | Consumables)
- Preserve all existing functionality with improved organization
- Complete ScreenManager bloat reduction (target: 60-70% code reduction)



## 9) Success Metrics & Current Status

### Technical Excellence (Achieved)
- ✅ **Modular Architecture:** Clean separation across 15+ modules
- ✅ **Event-Driven Design:** Professional EventManager coordination
- ✅ **Code Quality:** Industry-standard patterns and error handling
- ✅ **Performance:** Consistent 60 FPS with efficient rendering
- ✅ **Beginner-Friendly:** Clear structure for learning and modification

### Framework Maturity (In Progress)
**Quest System Integration:** Complete event-driven quest management with character progression
- ✅ **Data-Driven Content:** JSON-based NPCs, dialogue, and character classes
- ✅ **Professional Save System:** Complete state persistence with metadata
- ✅ **Semantic Input:** Universal action system for all user interactions
- 🎯 **Overlay Standardization:** Target of current refactoring phase
- 📋 **Location Templates:** Planned for Phase 3

### Development Velocity (Target)
- 🎯 **New NPCs:** JSON file creation only (no code changes)
- 🎯 **New Locations:** Configuration-based setup
- 🎯 **New Overlays:** Base class extension with minimal custom code
- 🎯 **Content Expansion:** Framework supports rapid iteration

### Quest System Features (Complete)
- ✅ **5-Quest Structure:** 1 primary (Terror in Redstone) + 4 secondary quests
- ✅ **XP Integration:** Quest completion → XP rewards → character progression
- ✅ **Party Tracking:** Individual XP progression for all recruited party members
- ✅ **Dynamic Unlocks:** Rat basement quest appears when party assembled
- ✅ **Information Discovery:** XP rewards for learning locations and secrets from NPCs
- ✅ **Event-Driven:** Complete integration with dialogue, recruitment, and progression systems

---

*This document reflects the current state as of September 2025, with active development focused on completing the screen architecture refactoring initiative. The project has successfully transitioned from prototype to professional framework status, with robust foundations ready for content expansion.*