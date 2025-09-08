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

## ADR-022: Gender Screen Input Modernization Complete
- **Status:** Accepted
- **Date:** Sep 5, 2025
- **Context:** Gender screen used legacy manual click handling instead of semantic action system
- **Decision:** Implement semantic actions (SELECT_MALE, SELECT_FEMALE) with CharacterEngine event handling
- **Implementation:**
  - ScreenManager registers gender screen clickables via enter hooks
  - InputHandler routes clicks to EventManager as semantic events
  - CharacterEngine handles gender events and business logic directly
  - Used same pattern as stats screen for consistency
- **Consequences:** 
  - Gender screen now uses professional event-driven architecture
  - Clean separation: UI → Events → Engine → GameState
  - Foundation extended for remaining character creation screens
  - GameController input responsibilities reduced by additional 5%
- **Files Modified:** screen_manager.py, character_engine.py

## ADR-023: NEW_GAME Event Handler Architecture Cleanup
- **Status:** Accepted
- **Date:** Sep 5, 2025
- **Context:** NEW_GAME event handling was temporarily placed in GameController with business logic mixed into coordination layer, violating separation of concerns
- **Decision:** Move NEW_GAME event handling from GameController to CharacterEngine where character creation flow logic properly belongs
- **Implementation:**
  - Added NEW_GAME event registration to `register_character_creation_events()` method
  - Created `_handle_new_game()` method in CharacterEngine to handle character creation flow
  - Removed temporary `handle_new_game()` method from GameController
  - CharacterEngine now owns complete character creation sequence logic
- **Consequences:**
  - Supports GameController as pure coordinator without business logic
  - support Character creation flow decisions centralized in appropriate engine
  - Clean separation: GameController coordinates, CharacterEngine decides flow
  - Need to review and adjust other methods for centralizing all character creation sequence logic
  - Architecture follows Single Responsibility Principle
- **Files Modified:** character_engine.py (added handler), game_controller.py (removed temporary code)

## ADR-024: Navigation Event Handler Architecture Cleanup
- **Status:** Accepted
- **Date:** Sep 5, 2025
- **Context:** START_GAME, CONTINUE, and LOAD_GAME event handlers were temporarily placed in GameController, mixing navigation logic with coordination responsibilities
- **Decision:** Move navigation event handling from GameController to ScreenManager where UI state management belongs
- **Implementation:**
  - Added navigation route map to ScreenManager for configurable screen transitions
  - Created `_handle_direct_navigation()` method for START_GAME/CONTINUE events
  - Created `_handle_load_game()` method for load overlay state management
  - Removed three temporary methods from GameController
  - Fixed event registration timing to occur after ScreenManager initialization
- **Consequences:**
  - ScreenManager owns all navigation and UI state management
  - GameController reduced by three more methods (continuing the diet)
  - Navigation routes centralized and easily configurable
  - Clean separation: GameController coordinates, ScreenManager handles UI flow
  - Foundation established for systematic navigation management
- **Files Modified:** screen_manager.py (added handlers), game_controller.py (removed temporary code)

## ADR-025: Name Selection Screen Input 
**Status:** Accepted
**Date:** Sep 6, 2025
**Context:** Name selection screens used legacy manual click handling and inconsistent text input architecture instead of unified event-driven system
**Decision:** Implement complete semantic action system for all three name screens (selection, custom input, confirmation) with unified InputHandler text processing
**Implementation:**ScreenManager registers all name screen clickables via enter hooks with dynamic positioning, InputHandler processes ALL input through EventManager, CharacterEngine handles complete name selection business logic and navigation, Migrated legacy GameController text input to InputHandler for architectural consistency
JSON-based name data storage in data/player/character_names.json for easy content updates
**Consequences:** All three name screens now use professional event-driven architecture
Unified input processing eliminates dual input pathways, Complete text input migration achieves architectural consistency, JSON name data enables content updates without code changes, Clean UX with text clearing on back navigation
Foundation established for remaining character creation screens
GameController input responsibilities reduced by additional 15%
**Files Modified:** screen_manager.py, character_engine.py, input_handler.py, game_controller.py
**Files Created:** data/player/character_names.json

## ADR-026: clean up Gamestate removed redundant code from ADR 025
gamestate.py removed redundant randomn name genreatione code and hardcoded names
moved to character engine and new json file
data/player/character_names.json

## ADR-027 Portrait Selection Screen Modernization Complete
Status: Accepted
**Date:** Sep 6, 2025
**Context:** Portrait selection screen used legacy hardcoded mouse handling instead of event-driven semantic action system, with business logic scattered between GameState and GameController
Decision: Complete modernization using established semantic action pattern with architectural cleanup and proper dependency injection
**Implementation:**  CharacterEngine Events: Added SELECT_PORTRAIT_1-5, CONFIRM_PORTRAIT, BACK_FROM_PORTRAIT with proper business logic handling
ScreenManager Integration: Dynamic clickable registration using enter hooks with exact coordinate mapping from draw function
InputHandler Integration: All portrait clicks converted to semantic events through EventManager
Architectural Refactoring: Moved portrait business logic methods (ensure_active_portrait, activate_character_portrait, clear_active_portrait, finalize_character) from GameState to CharacterEngine
**Dependency Injection:** Updated SaveManager constructor to receive CharacterEngine instance instead of using imports
**UI Enhancement:** Dynamic character name display ("Choose [Name]'s appearance") positioned above portrait grid
**Consequences:**
Portrait selection now uses professional event-driven architecture matching other modernized screens
Clean separation: UI rendering, semantic events, business logic, and data storage properly divided
Eliminated hardcoded mouse coordinate detection in favor of calculated clickable regions
SaveManager follows proper dependency injection pattern rather than tight coupling through imports
Foundation established for Gold and Trinket screen modernization using identical pattern
GameController portrait responsibilities eliminated, continuing thin coordinator pattern
**Technical Achievements:**
5-portrait horizontal grid with yellow selection highlighting
Portrait file discovery system (player_male_01.jpg to player_male_05.jpg format)
Proper navigation flow: portrait selection → confirmation → gold screen
Complete removal of legacy portrait methods from GameState
Professional shutdown process updated to use CharacterEngine methods
**Files Modified:**
character_engine.py - Added portrait event handlers and business logic methods
screen_manager.py - Added portrait clickable registration with enter hooks
screens/character_creation.py - Enhanced draw function with dynamic character name
save_manager.py - Updated constructor for proper dependency injection
game_controller.py - Updated SaveManager instantiation and shutdown process
game_state.py - Removed portrait business logic methods (cleanup)

## ADR-028: Added Gold screen and ignore empty clicks
- input handler, character classes (for future), character engine, screen manager
- got gold screen working, applied fix for empty clicks to avoid program shutdown

## ADR-029: added trinket screen to refactor

- character engine, screen manager, trinkets.json
- trinket screen works and pulls from trinket json file no longer hardcoded.

## ADR-030: updated to add character class JSON

- updated gold calcualation so it refers to character class json .
-   can be used for future expansion and HP calculations.

## ADR-031: update display to highlight primary attritbutes
- character creation.py
- adds more data for the stats screen for players to know what to focus on for their attributes.  allows for expansion to using json when allowing player to pick class

## ADR-032: Low Stats Warning System with Class-Specific Comments 
**Status: Accepted**
**Date: Sep 6, 2025**
Decision: Implement comprehensive low stats detection with class-aware JSON-driven snarky comment system
**Implementation:**JSON-based class information display on stats screen with primary ability highlighting
Class-specific snarky comment system loaded from low_stats_comments.json
Two-phase confirmation flow: Warning → Class-specific comment → Manual advance
Dynamic clickable registration for different screen states
**Technical Achievements:**JSON-driven character class system in character_classes.json with hit dice, primary abilities, and class data
Enhanced stats screen with Fighter class display and primary ability highlighting (green + asterisk)
Educational UX warning players about combat effectiveness while respecting choice
Class-specific humor system expandable for future class selection screen
**Files Modified:**
character_creation.py - Enhanced stats screen with JSON class display and confirmation screen
character_engine.py - Added low stats detection, class-specific comment loading, and dynamic registration
screen_manager.py - Added confirmation screen registration and dynamic clickable management
Files Created: character_classes.json, low_stats_comments.json

## ADR-033: Summary Screen Modernization Complete
**Status:** Accepted  
**Date:** Sep 7, 2025  
**Context:** Summary screen used legacy hardcoded display and lacked semantic action integration for START GAME button, with HP calculation timing issues and missing character portrait integration
**Decision:** Complete modernization using established event-driven architecture with JSON-based HP calculation and professional portrait display system
**Implementation:**
- **CharacterEngine Events:** Added handle_start_game() method with proper character finalization and validation
- **HP Calculation Integration:** Moved HP calculation to handle_keep_stats() for immediate availability throughout character creation
- **Portrait System Integration:** Added ensure_active_portrait() call during portrait confirmation to copy selected portrait to active folder
- **ScreenManager Integration:** Added register_summary_screen_clickables() with enter hooks for START GAME button registration
- **Professional Portrait Display:** Integrated character portrait on right side of summary screen using active portrait system
- **Graceful Error Handling:** Added fallback portrait selection for robust error recovery
**Technical Achievements:**
- JSON-based HP calculation using Fighter d10 + CON modifier from character_classes.json
- Portrait file copying architecture ensures consistent loading across all game screens
- Complete character data display: stats, class, HP, gold, equipment, trinket, and portrait
- Event-driven START GAME navigation with character validation and finalization
**Consequences:**
- Summary screen now follows professional semantic action pattern matching other modernized screens
- Character HP displays immediately upon entering summary (no more "Calculating..." placeholder)
- Selected character portrait appears correctly on summary screen via active portrait system
- Foundation established for START GAME transition to welcome screen with fully validated character
- Complete separation: UI rendering, event handling, business logic, and data storage properly divided
**Files Modified:** character_engine.py, screen_manager.py, character_creation.py

## ADR-034: Cinematic Intro Sequence Implementation
**Status: Accepted**
**Date: Sep 7, 2025**
**Context:** Required three narrative intro scenes between character creation and tavern entry to enhance story immersion.
Decision: Implement JSON-driven cinematic intro sequence system using established architectural patterns with atmospheric pygame backgrounds.
**Implementation:** Data Structure: data/narrative/intro_sequence.json with three-scene narrative
Visual System: Pygame-generated atmospheric backgrounds using new intro constants
Integration: Character name insertion, event-driven navigation (INTRO_START/NEXT/SKIP)
Auto-Save: Checkpoint after intro completion (slot 0) with correct screen state
**Technical Changes:**
Created screens/intro_scenes.py with IntroSequenceManager and scene renderers
Added intro layout constants to utils/constants.py
Updated CharacterEngine START_GAME to trigger intro sequence
Integrated with ScreenManager using enter hooks for clickable registration
**Consequences:**
Establishes reusable narrative architecture for future Acts
Character creation flows through story introduction before main game, Auto-save ensures proper resume point at tavern entrance
Foundation for JSON-driven content expansion
Files Modified: character_engine.py, screen_manager.py, game_controller.py, character_creation.py, constants.py
**Files Created:** intro_scenes.py, narrative/intro_sequence.json

## ADR-035: Bulletproof Initialization System Architecture
**Status: Accepted**
**Date: Sep 7, 2025**
**Context:** GameController had dual initialization anti-pattern - SaveManager created twice, causing fragile timing issues and architectural problems.
**Decision:** Implement 3-phase initialization with dependency injection following professional game engine patterns.
**Implementation:**
Phase 1: Infrastructure (EventManager, GameState, ScreenManager)
Phase 2: Core Dependencies (SaveManager, DataManager with proper injection)
Phase 3: System Integration (event handlers, cross-connections)

**Consequences:**
GameController: 800 lines → 400 lines (50% reduction)
Eliminates dual initialization bugs - each system created exactly once
Professional architecture following Unity/Unreal patterns
Foundation for load screen fix (architecture now supports proper event-driven SaveManager)
Future-proof - new systems follow established dependency injection patterns

**Files Modified:** game_controller.py (complete rewrite), save_manager.py, data_manager.py, main.py, event_manager.py

## ADR-036: Load Screen Event-Driven Architecture Modernization Complete
**Status: Accepted**
**Date: Sep 7, 2025**
**Context:** Load screen used legacy dual-path architecture with broken async events and GameController overlay management, violating separation of concerns established in bulletproof initialization.
**Decision:** Modernize load screen to follow character creation event-driven patterns with ScreenManager overlay ownership and SaveManager business logic.
**Implementation:** Moved overlay management from GameController to ScreenManager via OVERLAY_TOGGLE events
Fixed save data display - SaveManager.populate_save_slot_cache() now properly called
Implemented semantic actions - LOAD_SLOT_SELECTED, LOAD_GAME_CONFIRM, DELETE_SAVE_CONFIRM
Hybrid clickable registration - buttons always registered, state validation in SaveManager
Event-driven architecture - InputHandler → EventManager → SaveManager flow
**Technical Changes:**
GameController: Removed handle_overlay_toggle method, reduced coordination role
ScreenManager: Added overlay lifecycle management and clickable registration
SaveManager: Added load screen event handlers with state validation
InputHandler: Updated to use registered clickables instead of manual handlers
load_game.py: Modernized to use SaveManager data instead of broken async events
**Consequences:**
Load screen displays save data correctly - character names, locations, timestamps
All buttons functional - load, delete, cancel operations working
Professional event flow - follows established character creation patterns
GameController diet continues - overlay responsibilities moved to appropriate systems
Template established for modernizing remaining overlays (inventory, quest log, character sheet, help)
**Files Modified:** game_controller.py, screen_manager.py, save_manager.py, input_handler.py, load_game.py, event_manager.py
Next Phase: Apply identical pattern to save_game.py and remaining overlay systems using established template.

## ADR-037: Load Screen Blue Line Display & Duplicate Event Handler Resolution
## Status: Accepted
## Date: Sep 7, 2025
**Context:** Load screen blue line highlighting not working and load functionality failing due to architectural issues in event-driven system.
**Problem Analysis:**
Blue line highlighting failed to appear when selecting save slots
Load functionality crashed with AttributeError exceptions
Root cause: Duplicate event handler registration causing toggle conflicts
Secondary issues: SaveManager retained GameController attribute references
**Investigation Process:**
Initial hypothesis focused on game_state reference mismatches
Comprehensive code analysis revealed dual registration in SaveManager.init() and GameController._initialize_system_integration()
Debug output showed 2 listeners for LOAD_SLOT_SELECTED events
SaveManager's toggle logic: first call sets selection, second call clears it
Additional issues: self.error_count, self.last_load_time, self.screens attribute errors
**Solution Implemented:** Removed duplicate event registration from GameController._initialize_system_integration()
Cleaned SaveManager.load_game() method of GameController dependencies
Implemented direct portrait restoration using save file data instead of character engine, Fixed Python scoping issues with import statements
**Technical Changes:**
GameController: Removed duplicate self.save_manager.register_load_screen_events() call, SaveManager: Removed self.error_count, self.last_load_time, self.screens references
**SaveManager:** Added direct portrait activation using saved portrait_file and portrait_gender data
Portrait System: Bypassed character engine complexity for reliable save/load portrait restoration
**Validation Results:**
Blue line highlighting working correctly
Load functionality completely operational
Portrait restoration working seamlessly
Clean error-free operation with proper debug output
**Consequences:**Load screen fully modernized following event-driven architecture patterns, Template established for remaining overlay modernizations (save, inventory, quest log, character sheet, help)
Separation of concerns properly maintained: InputHandler → EventManager → SaveManager

## ADR-038: Added shutdown and autosave method
-added to gamecontroller based on research and coordiantor responsibilities
- safely closes and autosave according to the save parameters.
## ADR-039: Save Game Overlay Event-Driven Architecture Modernization CompleteStatus: Accepted
## Date: Sep 7, 2025
**Context:** Save game overlay used legacy direct click handling instead of event-driven semantic action system established in load game modernization, violating architectural consistency and separation of concerns.Problem Analysis:
Save overlay opened with F7 but buttons failed to register clicks properly
Legacy handle_save_game_click() function bypassed modern event system
Inconsistent text rendering caused display corruption
Button registration used unreliable dynamic detection instead of fixed positioning
Decision: Modernize save game overlay to match load game event-driven architecture exactly, establishing consistent overlay modernization template.Implementation:
**SaveManager Events:** Added register_save_screen_events() with handlers for SAVE_SLOT_SELECTED, SAVE_GAME_CONFIRM, SAVE_SCREEN_CANCEL
ScreenManager Integration: Added save overlay lifecycle management and fixed-position clickable registration
InputHandler Updates: Added save overlay click handling section matching load overlay pattern
UI Improvements: Filtered save slots to manual saves only (slots 1-3), fixed text rendering to multi-column format
Architecture Cleanup: Removed legacy handle_save_game_click() function, moved all event handlers to SaveManager
**Technical Changes:**
save_manager.py: Added save screen event handlers with proper state validation
screen_manager.py: Added register_save_screen_clickables() with fixed button positioning
input_handler.py: Added save overlay click processing section
save_game.py: Updated text rendering, removed legacy click handler, filtered to manual save slots only
input_handler.py: Fixed F7 hotkey mapping from SCREENSHOT_REQUESTED to SAVE_GAME
**Consequences:** Save overlay fully functional with professional event-driven architecture
Template established for remaining overlay modernizations (inventory, quest log, character sheet, help)
Clean separation: InputHandler → EventManager → SaveManager → ScreenManager
F7 save menu shows only manual slots (1-3), maintaining clean save architecture (F5=quick, F7=manual, auto=system)
**Files Modified:** save_manager.py, screen_manager.py, input_handler.py, save_game.py


```
## ADR-XXX: <Short title>
- **Status:** Proposed | Accepted | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Context:** …
- **Decision:** …
- **Consequences:** …
```

