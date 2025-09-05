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

```
## ADR-XXX: <Short title>
- **Status:** Proposed | Accepted | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Context:** …
- **Decision:** …
- **Consequences:** …
```

