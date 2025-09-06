# decisions.md

## ADR-001: Single Data Authority
- **Status:** Accepted
- **Date:** Sep 1, 2025
- **Context:** Conflicts across GameState, InventoryEngine, CommerceEngine【164†source】
- **Decision:** GameState is the only data authority. Engines are stateless processors.
- **Consequences:** Centralized state, consistent save/load, simpler integrity checks.

## ADR-002: Event System Foundation
- **Status:** Accepted
- **Date:** Sep 1, 2025
- **Context:** `game_controller.py` was a 1000+ line God Object【152†source】
- **Decision:** Introduce EventManager as the global bus【150†source】
- **Consequences:** Systems decoupled; controller shrinks toward ~200 LOC.

## ADR-003: JSON-Driven Dialogue
- **Status:** Accepted
- **Date:** Sep 3, 2025
- **Context:** NPC-specific hardcoding in tavern screens【152†source】
- **Decision:** All dialogue lives in JSON, parsed by DialogueEngine【151†source】【160†source】
- **Consequences:** New NPC = new JSON only; AAA branching validated.

## ADR-004: Screen Management Abstraction
- **Status:** Proposed
- **Date:** Sep 3, 2025
- **Context:** Controller still owns screen transitions【162†source】
- **Decision:** Introduce ScreenManager with register/transition/push/pop API.
- **Consequences:** Clean lifecycle; controller free of screen logic.

## ADR-005: Input Handling Abstraction
- **Status:** Proposed
- **Date:** Sep 3, 2025
- **Context:** Hardcoded click handling in controller【162†source】
- **Decision:** Create InputHandler to register clickables and emit events.
- **Consequences:** Rebind-friendly; decoupled input; initial refactor touches all screens.

## ADR-006: Content-Driven Expansion
- **Status:** Proposed
- **Date:** Sep 3, 2025
- **Context:** Adding NPCs/locations still requires code edits【152†source】【163†source】
- **Decision:** All content defined in `content_config.json` + data files.
- **Consequences:** New NPC/location = JSON only; ContentLoader builds runtime state.

## ADR-007: Event Trace Logging
- **Status:** Proposed
- **Date:** Sep 3, 2025
- **Context:** Debugging event-driven systems can be opaque.
- **Decision:** Add structured event trace toggle; logs written per session.
- **Consequences:** Better bug tracking; small performance hit.

## ADR-008: Engine Test Coverage
- **Status:** Proposed
- **Date:** Sep 3, 2025
- **Context:** Engines like Inventory and Dialogue are business-critical【149†source】
- **Decision:** Add pytest unit tests for engine logic before UI wiring.
- **Consequences:** Safer refactors; higher upfront cost.

---

**ADR-009:** Patron screen add

**Status:** Accepted
-**Date:** Sep 3, 2025
-Context: dialogue updates and additions to NPC patrons still neeeded.
-Decision: added new Patron selection screen, added only gareth dialogue
-Consequences: expanded dialogue scope

**ADR-010:** Garreth dialogue updates to ensure functionality
-Sep 4 2025-
-Dialogue Engine, generic_dialogue Handler - to enhance functionality
-smooth working of gareth dialogue on patron selection screen
also created a JSON file creation guide document to aid in future dialogue creations. in redston doc folder.

**ADR-011:** got shop system visible, but still hardcoded and non-functiona;
-Sep 4, 2025
- Game_Controller.py  shopping.py  geeting the screen to work
- verifies the visibility of the screen

**ADR-012:** input handling integration - phase 1
**Sep 4, 2025**
- created input handler.py, game_controller.py
- extracted universal keyboard from GC to IH.  program can start and use overlays.  first step in major refactoring.

## ADR-013: Semantic Input System - Phase 1 Complete
- **Status:** Accepted
- **Date:** Sep 5, 2025
- **Context:** InputHandler had keyboard extraction but still needed mouse click integration for complete input abstraction
- **Decision:** Implement semantic action system where screens register named actions (START_GAME, CONTINUE, NEW_GAME) instead of hardcoded pixel coordinates. InputHandler routes clicks to EventManager as semantic events.
- **Consequences:** 
  - Title screen navigation now fully event-driven
  - Click coordinates preserved as metadata for analytics
  - Screen logic decoupled from input handling
  - Foundation established for extracting all remaining screen mouse handlers
  - GameController input responsibilities reduced by additional 15%

## ADR-014: EventManager Instance Management
- **Status:** Accepted  
- **Date:** Sep 5, 2025
- **Context:** Duplicate `initialize_event_manager()` calls creating separate instances, breaking event routing
- **Decision:** Single EventManager instance shared across all systems - initialized once in GameController, passed to all subsystems
- **Consequences:** All event registration and emission now uses same instance, enabling proper event-driven architecture

## ADR-015: Complete ScreenManager Architecture Implementation
- **Status:** Accepted
- **Date:** Sep 5, 2025
- **Context:** GameController contained massive draw_current_screen() method with screen rendering logic scattered throughout
- **Decision:** Implement full ScreenManager with event-driven navigation and screen lifecycle management
- **Implementation:** 
  - ScreenManager handles all screen rendering via registered render functions
  - Event-driven navigation through EventManager hub
  - InputHandler delegates unknown clicks to ScreenManager
  - Individual screens auto-register their own click handlers
- **Consequences:** 
  - GameController reduced by ~300 lines with draw_current_screen() method eliminated
  - Clean separation of concerns established as foundation for further refactoring
  - Adding new screens requires only registration, no GameController changes
  - Professional screen lifecycle management with history and error handling
  - Further cleanup needed to achieve target thin coordinator pattern

## ADR-016: Event-Driven Component Architecture
- **Status:** Accepted  
- **Date:** Sep 5, 2025
- **Context:** Components were tightly coupled with manual wiring in GameController
- **Decision:** EventManager as central hub with components subscribing to relevant events
- **Implementation:**
  - ScreenManager subscribes to SCREEN_CHANGE and SCREEN_ADVANCE events
  - InputHandler delegates failed clicks via events rather than direct calls
  - Screen handlers emit navigation events rather than calling methods directly
- **Consequences:** 
  - GameController begins transition to thin coordinator pattern
  - Components self-organize through event subscription
  - Foundation established for complete architectural cleanup
  - Loose coupling enables easier testing and modification
  
## ADR-017: Complete Application Lifecycle Architecture
- **Status:** Accepted
- **Date:** Sep 5, 2025
- **Context:** Quit button emitted QUIT_GAME events but GameController handled application lifecycle management, violating separation of concerns
- **Decision:** Extract application lifecycle to main.py with event-driven quit handling
- **Implementation:**
  - Main game loop registers for QUIT_GAME events directly
  - GameController.handle_quit_game() method removed
  - GameController.quit_game() retained for system cleanup coordination
  - Clean separation: main.py manages application lifecycle, GameController coordinates shutdown
- **Consequences:** 
  - Application lifecycle management extracted from GameController
  - Quit button works with proper event flow
  - GameController responsibility reduced by removing application state management

## ADR-018: SaveManager Architecture Implementation  
- **Status:** Accepted
- **Date:** Sep 5, 2025
- **Context:** GameController contained 6 save/load methods (save_game, load_game, get_save_info, auto_save, delete_save, can_save_load) violating Single Responsibility Principle
- **Decision:** Extract all save/load operations to dedicated SaveManager class
- **Implementation:**
  - Created game_logic/save_manager.py with SaveManager class
  - Moved all 6 save/load methods from GameController to SaveManager
  - GameController retains event routing (handle_save_requested) but delegates to SaveManager
  - SaveManager handles all file I/O and save data operations
- **Consequences:**
  - GameController reduced by 6 major methods (~200 lines)
  - Clean separation: GameController routes save events, SaveManager handles file operations
  - Foundation established for professional save/load architecture
  - Load screen architecture prepared for SaveManager integration

## ADR-019: InputHandler Overlay Architecture Completion
- **Status:** Accepted  
- **Date:** Sep 5, 2025
- **Context:** Load game overlay rendered but click handling was disconnected, overlays managed in multiple places
- **Decision:** Complete overlay architecture with InputHandler managing both rendering coordination and click handling
- **Implementation:**
  - ScreenManager._render_overlays() handles overlay rendering on top of main screens
  - InputHandler._handle_overlay_clicks() processes overlay button interactions
  - GameController legacy overlay handling removed
  - Clean division: InputHandler (overlay state + clicks), ScreenManager (overlay rendering), GameController (thin coordination)
- **Consequences:**
  - Load game overlay fully functional with proper button handling
  - Overlay architecture follows established separation of concerns
  - Foundation complete for adding additional overlays without GameController changes
  - Professional overlay lifecycle management established
## ADR-020: Load Game Display Bug - DEFERRED
Date: September 5, 2025
**Issue**- Load screen shows "[Empty Slot]" instead of character names despite SaveManager returning correct data.
Investigation
SaveManager works correctly (returns valid character data)
Display rendering logic fails for unknown reason
Multiple debugging attempts unsuccessful
**Decision DEFERRED** - Non-critical cosmetic issue. Reverted code to working state.
**Rationale**  Functionality > cosmetics
Time investment vs. benefit
Maintains development momentum
**Status** Core save system questionable. Visual display bug documented for future UI polish phase.
## ADR-021: Stats Screen Input Modernization Complete
Status: Accepted
**Date: Sep 5, 2025**
**Context:** Stats screen used legacy manual click handling instead of semantic action system
**Decision:** Implement semantic actions (REROLL_STATS, KEEP_STATS) with CharacterEngine event handling
**Implementation:**
ScreenManager registers stats screen clickables on transition
InputHandler routes clicks to EventManager as semantic events
CharacterEngine handles stat events and business logic directly
Fixed event format compatibility between components
**Consequences:**Stats screen now uses professional event-driven architecture
Clean separation: UI → Events → Engine → GameState
Foundation established for remaining character creation screens
GameController input responsibilities reduced by additional 10%
**Files Modified:** screen_manager.py, character_engine.py, game_controller.py, character_creation.py
```
## ADR-XXX: <Short title>
- **Status:** Proposed | Accepted | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Context:** …
- **Decision:** …
- **Consequences:** …
```

