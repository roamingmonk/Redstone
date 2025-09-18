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

# ADR-040: Broken Blade Main Screen Button Registration & Overlay Rendering Fix
**IMPLEMENTED** - September 7, 2025
## Context
The Broken Blade main screen buttons (TALK TO BARTENDER, TALK TO SERVER) were non-functional due to missing event-driven button registration. Additionally, overlay screens (I/Q/C/H hotkeys) were toggling state correctly but not rendering visually.
## Problem Analysis
1. **Missing Enter Hook:** `broken_blade_main` screen lacked enter hook for clickable registration
2. **No Event Listeners:** `NPC_CLICKED` events had 0 listeners registered
3. **Commented Overlay Rendering:** Overlay state management worked, but visual rendering was disabled in `_render_overlays` method
## Decision
Applied proven overlay modernization template using event-driven architecture:
### Button Registration Fix
- Added `enter_hook` to `broken_blade_main` registration
- Created `register_broken_blade_main_clickables()` method in ScreenManager
- Registered `NPC_CLICKED` event handler: `_handle_npc_clicked()` in ScreenManager
- Used ScreenManager for NPC dialogue screen registration (avoiding GameController dependency)
### Overlay Rendering Fix
- Completed `_handle_overlay_toggle()` method for all overlay types (inventory, quest_log, character_sheet, help)
- Uncommented and completed `_render_overlays()` method with all overlay drawing calls
- Maintained separation: ScreenManager handles overlay state, overlays render on top of main screens
- still a lot of work left on functionality of these screens but they are now visible
## ADR-041: BaseTabbedOverlay System Foundation Implementation - 
**Status:** Accepted - 
**Date:** Sep 8, 2025 - 
**Context:** ScreenManager contained 20+ specialized overlay registration methods (`register_help_screen_clickables()`, `register_inventory_screen_clickables()`, etc.) causing code bloat and maintenance overhead. Adding new overlays required extensive ScreenManager modifications. - 
**Decision:** Implement professional tabbed overlay architecture using `BaseTabbedOverlay` base class with reusable tab management, keyboard navigation, and standardized lifecycle hooks. - 
**Implementation:** - Created `utils/tabbed_overlay_utils.py` with `BaseTabbedOverlay` foundation class - Implemented tab navigation via mouse clicks, number keys (1-9), and arrow keys - Added overlay management ensuring only one overlay active at a time - Converted help screen as proof of concept maintaining exact visual compatibility - Eliminated `register_help_screen_clickables()` method from ScreenManager - 
**Technical Features:** - Consistent header/footer rendering across all overlays - Professional tab button styling with active/inactive states - Keyboard shortcut indicators (number badges on tabs) - Standardized content area management with proper spacing - Error handling and graceful fallbacks - 
**Consequences:** - **Positive:** Foundation established for 60-70% reduction in ScreenManager overlay methods. Framework ready for rapid overlay development. Help screen conversion proves concept works without breaking existing functionality. - 
**Future Impact:** Remaining overlays (inventory, quest log, character sheet) can now be converted using established pattern. Adding new overlays becomes configuration rather than coding. - 
**Code Quality:** Professional separation of concerns - base class handles framework, subclasses handle content. - 
**Files Created:** `utils/tabbed_overlay_utils.py`, `screens/help_overlay.py` - **Files Modified:** `ui/screen_manager.py` (import change), `screens/help_screen.py` (replaced) - constants.py - new data added.
**Next Phase:** Session 2 - Convert character sheet overlay using established pattern


## ADR-042: Character Overlay Tabbed System Implementation
- **Status:** Accepted
- **Date:** Sep 8, 2025  
- **Context:** ScreenManager character sheet used basic registration method with no tabbed functionality. Session 2 of overlay refactoring roadmap targeted character sheet conversion to prove multi-tab concept.
- **Decision:** Convert character sheet to 2-tab overlay (Player Stats | Party Members) using established BaseTabbedOverlay pattern from Session 1.
- **Implementation:**
  - Created `screens/character_overlay.py` with CharacterOverlay class extending BaseTabbedOverlay
  - Player Stats tab: Preserved all existing character sheet functionality (stats, equipment, portrait, gold)
  - Party Members tab: New functionality displaying recruited NPCs with portraits and basic info
  - Added keyboard input routing in InputHandler for overlay tab navigation
  - Implemented mouse click routing for tab selection
  - Created centralized screen restriction system using constants for maintainability
- **Technical Features:**
  - Full keyboard navigation: 1/2 keys for direct tab access, arrow keys for navigation
  - Mouse tab clicking with visual feedback and hover states
  - Portrait integration using existing party_display.py system
  - Selective overlay restrictions: main menu allows load screen, blocks others
  - Professional error handling and debug output
- **Consequences:**
  - **Positive:** Multi-tab overlay concept proven successful. Character sheet maintains exact functionality while gaining tabbed interface. Foundation established for party management system. Screen restriction architecture centralized and maintainable.
  - **Architecture:** Eliminated register_character_sheet_screen_clickables() method. Professional separation of Player vs Party information. Template confirmed for remaining overlay conversions.
  - **User Experience:** Seamless tab navigation, preserved character data display, foundation for party member management
- **Files Created:** `screens/character_overlay.py`
- **Files Modified:** `ui/screen_manager.py` (import changes), `input_handler.py` (overlay routing), `utils/constants.py` (screen restrictions)
- **Next Phase:** Session 3 - Quest Log overlay conversion (2 tabs: Active Quests | Completed Quests)


## ADR-043: Professional Quest System Integration Complete
**Status:** Accepted  
**Date:** Sep 8, 2025  
**Context:** Game lacked integrated quest progression system connecting dialogue, party recruitment, XP awards, and character progression. Quest tracking was hardcoded in quest_log.py without connection to game events.  
**Decision:** Implement comprehensive event-driven quest system with professional XP progression and party tracking following established engine architecture patterns.  
**Implementation:**  
- Created `game_logic/quest_engine.py` - Event-driven wrapper around enhanced quest system
- Enhanced `utils/quest_system.py` - 5 quests (1 primary: Terror in Redstone, 4 secondary: Party Building, 3 Location Investigations)  
- Extended CharacterEngine with party XP tracking, quest event handlers, and level-up detection
- Integrated quest completion → XP awards → level progression → character sheet notifications
- Dynamic quest unlocking capability (rat basement quest unlocks when party assembled)
**Technical Architecture:**  
- **Event Flow:** Quest Completion → EventManager → CharacterEngine → XP Distribution → Level Up Detection
- **Party XP System:** All party members gain XP independently with levels 1-5 exponential progression  
- **Quest Structure:** Primary quest (main story) + Secondary quests (locations, party building, special unlocks)
- **Integration Points:** Dialogue triggers, party recruitment events, information discovery XP
**XP System Features:**  
- Exponential progression: Level 1 (0 XP) → Level 5 (6500 XP) capping at appropriate scope
- Party member XP tracking with individual progression and level-up capabilities
- Combat state awareness (XP deferred during combat, processed afterward)
- Quest-specific XP rewards: Main story (1000), Locations (400), Side quests (200), Discovery (50)
**Quest Event Integration:**  
- **QUEST_COMPLETED:** Awards XP to all party members, triggers level-up notifications
- **INFORMATION_DISCOVERED:** Awards discovery XP for learning locations/secrets  
- **PARTY_MEMBER_RECRUITED:** Progresses party building and main story objectives
- **DIALOGUE_QUEST_TRIGGER:** Activates quests and completes objectives from NPC conversations
**Consequences:**  
- **Positive:** Professional RPG progression system ready for content expansion. Quest completion provides meaningful character advancement. Event-driven architecture eliminates hardcoded dependencies.
- **Foundation Established:** Ready for quest overlay conversion, dynamic quest unlocking (rat basement), and future location/combat integration
- **Scalable Design:** Adding new quests becomes configuration rather than coding
**Files Created:** `game_logic/quest_engine.py`  
**Files Enhanced:** `utils/quest_system.py`, `game_logic/character_engine.py`, `core/game_controller.py`  
**Next Phase:** Convert quest_log.py to professional 2-tab overlay using quest system data, eliminate hardcoded quest functions

# ADR-044: Universal Self-Registering Overlay System
**Date:** 2025-09-09  
**Status:** Accepted  
**Supersedes:** Individual overlay management patterns  
## Context
Terror in Redstone initially implemented overlays using individual hardcoded patterns. Each new overlay required modifications to InputHandler, ScreenManager, and GameState with overlay-specific boolean flags. This led to code duplication, maintenance overhead, inconsistent behavior, and input routing conflicts.
## Decision
Implement a **Universal Self-Registering Overlay System** with:
1. **Centralized State Management**: Replace boolean flags with `OverlayState` class enforcing single overlay behavior
2. **Self-Registration**: Overlays automatically register with InputHandler when first rendered
3. **Universal Input Routing**: Dynamic overlay discovery through registry lookup
4. **Standardized Framework**: All overlays extend `BaseTabbedOverlay` with consistent interface
5. **Naming Convention**: Use "_key" suffix for overlay IDs (e.g., "character_key")
## Consequences
### Positive
- **Zero-maintenance expansion**: New overlays require no core system modifications
- **Professional architecture**: Matches industry UI overlay management standards
- **Consistent behavior**: Universal tab navigation and input handling
- **Performance**: Single overlay behavior eliminates state conflicts
### Negative
- **Migration overhead**: Required updating existing overlay implementations
- **Learning curve**: Developers must understand self-registration pattern
- **Debugging complexity**: Dynamic registration can obscure initialization issues
### Neutral
- **Rendering hardcoding**: ScreenManager retains explicit overlay rendering cases (acceptable tradeoff for reliability)
## Implementation Requirements
- All overlays must call `super().handle_mouse_click()` first
- Registration must happen during first render
- Overlay IDs must use "_key" suffix convention
- Graceful degradation when registration fails
## Alternatives Considered
- **Continue individual patterns**: Rejected due to poor scalability
- **Complex dynamic discovery**: Rejected as over-engineered
- **Event-based communication**: Rejected for added complexity
- **Complete dynamic rendering**: Rejected due to debugging difficulty
## References
- Universal Overlay Creation Template
- `utils/overlay_utils.py` (OverlayState class)
- `utils/tabbed_overlay_utils.py` (BaseTabbedOverlay framework)

# ADR-045: Inventory Overlay Action Button System Integration Complete
**Date:** 2025-09-09  
**Status:** Accepted  

## Context
Inventory overlay buttons (EQUIP, UNEQUIP, CONSUME, DISCARD) were rendering correctly but not executing actions. Event pipeline was broken at multiple points: missing event registration, incorrect method calls, and ESC key routing conflicts.

## Problem Analysis
1. **Missing Event Registration**: `initialize_inventory_engine()` lacked EventManager parameter, preventing event handler registration
2. **Method Signature Mismatch**: Event handlers called non-existent methods (`self.equip_item()`) instead of working GameState methods
3. **ESC Key Architecture Conflict**: Universal ESC handler used legacy boolean flags while new overlay system uses centralized `overlay_state`

## Decision
Implement complete event-driven inventory action system with proper architectural integration:

### Technical Implementation
**InventoryEngine Integration:**
- Modified `initialize_inventory_engine(game_state_ref, item_manager_ref, event_manager_ref)` signature
- Added automatic event handler registration during initialization
- Updated GameController to pass EventManager reference during engine creation

**Event Handler Architecture:**
- Simplified event handlers to use existing GameState methods (`equip_item()`, `unequip_item()`, `consume_item()`, `discard_item()`)
- Eliminated dependency on incomplete InventoryEngine business logic methods
- Maintained hybrid approach: UI in overlay, business logic in GameState

**ESC Key System Modernization:**
- Updated `_handle_escape_key()` method to use centralized `overlay_state.close_overlay()`
- Removed legacy boolean flag checking for modern overlays
- Maintained fallback support for legacy overlay types

## Consequences
### Positive
- **Full Functionality**: All inventory actions (equip/unequip/consume/discard) working correctly
- **Professional Architecture**: Proper event-driven communication between overlay and business logic
- **Universal ESC Behavior**: Consistent overlay closing behavior across all overlay types
- **Equipment Persistence**: GameState correctly tracks and persists equipment changes

### Technical Achievements
- **Event Pipeline Integrity**: Complete InputHandler → EventManager → InventoryEngine → GameState flow
- **Method Signature Consistency**: All overlay methods use correct parameter patterns
- **State Management**: Centralized overlay state management eliminates architectural conflicts

## Files Modified
- `game_logic/inventory_engine.py` - Added event_manager parameter and simplified event handlers
- `core/game_controller.py` - Updated inventory engine initialization call
- `input_handler.py` - Modernized ESC key handling for centralized overlay system
- `screens/inventory_overlay.py` - Fixed close_overlay() method call signature

## Validation Results
- ✅ Equipment changes reflected in both inventory UI and character sheet
- ✅ Item consumption properly decreases quantities and clears selection
- ✅ ESC key closes overlays consistently across inventory and character sheet
- ✅ Event listeners properly registered (console shows "Listeners: 1" instead of "Listeners: 0")
# ADR-045: BaseLocation Architecture Foundation - Session 8 Planning Complete
# Status: Accepted
# Date: Sep 10, 2025
**Context:** Game requires standardized location system to replace individual location screens with unified, JSON-driven architecture. Current approach requires code changes for each new location (inn, general store, hill ruins, refugee camp). Screen manager refactoring roadmap identified Session 8 as foundation for location standardization before continuing with modal dialog sessions 6-7.
Decision: Implement comprehensive BaseLocation architecture with hierarchical class system and unified JSON configuration schema. Replace individual location screens with data-driven system enabling pure JSON workflow for content creation.
**Architecture Design:**
BaseLocation Hierarchy: ActionHubLocation, NPCSelectionLocation, DialogueLocation, ShoppingLocation, CombatLocation
Unified JSON Schema: Single configuration file per location with nested areas support
Multi-Area Locations: Complex locations like Hill Ruins support entrance → ground_level → dungeon_level1 transitions
Action Routing System: Navigate, dialogue, shopping, combat, quest_board, loot_check action types
Shopping Integration: Convert shopping.py to ShoppingLocation inheriting BaseTabbedOverlay for consistency

**Implementation Phases:**
Session 8A: DialogueEngine ScreenManager integration fixes, patron_selection clickable registration
Session 8B: Core BaseLocation infrastructure, JSON schema implementation, area navigation system
Session 8C: Shopping standardization, Broken Blade tavern conversion, complete integration testing
**JSON Configuration Examples:**
Simple Location: General Store with shop/talk/notice_board/leave actions
Complex Location: Hill Ruins with entrance/ground_level/dungeon areas and combat integration
Action Types: Navigate between areas, trigger dialogues, initiate shopping, start combat encounters
**Integration Strategy:**
Backward Compatibility: All existing dialogue, shopping, NPC systems preserved exactly
ScreenManager Integration: BaseLocation instances replace individual screen registration
DialogueEngine Integration: No changes required to existing dialogue JSON files
Shopping Modernization: Inherit BaseTabbedOverlay for Buy/Sell/Info tabs, maintain identical functionality
**Content Creation Workflow:**
New Simple Location: Create JSON configuration file only, zero code changes
New Complex Location: Design area flow, create comprehensive JSON with transitions and encounters
Quest Integration: Dialogue choices trigger combat, location unlocking through action definitions
**Technical Benefits:**
Content Velocity: New locations become pure configuration tasks
Consistency: All locations follow identical interaction patterns
Scalability: Multi-area locations supported with area.location navigation
Maintainability: Centralized location logic with data-driven configuration
Extensibility: Framework ready for combat, quests, world map expansion

**Migration Strategy:**
Phase 1: Core infrastructure and JSON schema
Phase 2: Broken Blade conversion as proof of concept
Phase 3: Gradual migration of remaining locations
Phase 4: Pure BaseLocation workflow for new content

**Success Criteria:**
Zero code changes required for new simple locations
JSON-only workflow for complex multi-area locations
Complete backward compatibility with existing tavern functionality
Performance maintained at 60 FPS during location transitions
Professional architecture ready for rapid content expansion

Next Phase: Session 8A implementation - DialogueEngine modernization and ScreenManager integration fixes
Strategic Impact: This architecture foundation enables rapid story expansion and establishes professional location system ready for Terror in Redstone's complete storyline implementation through pure JSON configuration.

# ADR-046: BaseLocation Architecture Core Implementation Complete
**Status:** Accepted  
**Date:** Sep 10, 2025  
**Context:** Session 8B implementation of BaseLocation architecture to replace hardcoded screen logic with JSON-driven configuration system, enabling rapid location development without code changes.

## Decision
Implemented complete BaseLocation architecture with ActionHubLocation and NPCSelectionLocation classes, JSON configuration system, and event-driven action processing through LOCATION_ACTION events.

## Implementation
**Core Architecture:** Created BaseLocation abstract base class with ActionHubLocation and NPCSelectionLocation subclasses supporting flexible button creation and area navigation
**JSON Configuration:** Implemented location_loader.py with LocationManager for caching and validating location data from broken_blade.json
**Event Integration:** LOCATION_ACTION events route through InputHandler → EventManager → ScreenManager with thin coordination layer translating JSON actions to semantic events
**ScreenManager Integration:** Added _register_base_location_screen method with proper controller resolution for BaseLocation rendering
**Button System:** Dynamic button creation with flexible widths, centered positioning, and automatic LOCATION_ACTION event registration

## Technical Resolution
**Controller Resolution Fix:** Resolved black screen issue by accessing controller through ScreenManager._current_game_controller when not passed as parameter
**Mixed Deployment Support:** BaseLocation system coexists with legacy screens during architectural transition
**JSON-Driven Actions:** Complete action type support (navigate, dialogue, shopping) with extensible framework for combat, quest_board, loot_check

## Consequences
**Positive:** New locations can be added with JSON-only configuration, maintaining architectural consistency and enabling rapid content expansion
**Architecture Validated:** Thin coordination layer successfully translates JSON to events while preserving existing system integration
**Foundation Complete:** Core BaseLocation system ready for Session 8C shopping conversion and additional location types
## Files Modified
- ui/base_location.py (created complete architecture)
- ui/screen_manager.py (added BaseLocation registration)
- input_handler.py (added LOCATION_ACTION processing)
- data/locations/broken_blade.json (functional configuration)
- utils/location_loader.py (JSON loading and validation)
## Status
**Core Implementation:** ✅ Complete and functional
**Next Phase:** Session 8C - Shopping system conversion to ShoppingLocation

# ADR-047: DialogueEngine Modernization with Auto-Discovery Architecture
# Status: Accepted
# Date: September 11, 2025
**Context:** Dialogue system required modernization from hardcoded NPC functions to professional event-driven architecture supporting zero-code content expansion and location-aware NPCs.
**Decision**
Implemented comprehensive DialogueEngine modernization with systematic auto-discovery registration, EventManager services integration, and location-aware dialogue processing through established event-driven patterns.
**Implementation**  **Auto-Discovery System:** Filesystem-based dialogue registration automatically loads JSON files from data/dialogues/*.json using {location_id}_{npc_id} naming convention
**Services Registry:** Added DialogueEngine to EventManager services hub enabling clean engine access via event_manager.get_service()
**Conditional Parameters:** ScreenManager handles both legacy 4-parameter and new 5-parameter render functions maintaining backward compatibility
Event-Driven Processing: DIALOGUE_CHOICE and DIALOGUE_ACTION events route through InputHandler → EventManager → DialogueEngine
**Technical Achievements**
Zero-Code Workflow: New NPCs require only JSON file creation with no code modifications
Location Context: Dynamic dialogue loading with persistent location state throughout dialogue sessions
**Proper Closure Handling:** Fixed Python closure bugs in nested function registration **Rich Interface:** Portrait loading, choice buttons, and action processing functional
**Consequences**
Positive: Established professional dialogue architecture scalable to entire game with clean separation of concerns and zero-code content expansion workflow
**Foundation Ready:** Shopping system conversion and additional location types can proceed using established patterns
**Technical Debt Resolved:** Eliminated hardcoded NPC dialogue functions and centralized processing logic
Remaining Work
Critical response flow completion for all dialogue actions and proper navigation integration back to location screens needed for Session 8A completion.
**Files Modified:** ui/base_location.py, ui/screen_manager.py, ui/generic_dialogue_handler.py, game_logic/dialogue_engine.py, game_logic/event_manager.py, core/game_controller.py

# ADR-048: BaseLocation Button Coordinate Alignment Fix
# Status: Accepted
# Date: Sep 11, 2025
**Context:** BaseLocation system had coordinate mismatch between button registration and rendering, causing clickable areas to be shifted left from visual buttons.
**Problem:** Registration used dummy fonts while rendering used controller fonts, creating different text measurements and button positioning between the two render() calls.
**Decision:** Modified BaseLocation register_with_input_handler() to use controller.fonts instead of dummy fonts, ensuring identical coordinate calculation.
**Result:** Server button now consistently positioned at x=649, w=114 in both registration and rendering. Click detection working correctly with coordinates properly aligned.
**Files Modified:** ui/base_location.py
**Impact:** Session 8A main screen navigation complete. BaseLocation coordinate system validated for broken_blade_main screen.

# ADR-049: narrative schema integration 

-- core/game_state.py (narrative schema integration), game_logic/dialogue_engine.py (schema flag setting), ui/generic_dialogue_handler.py (response state detection)
- updated gamestate, auto initilize, integrated the narrative schema, confirmed 4 dialogue screens, and coordinated flags for dialogue, quest tracking.  
- Open issues.  need to validate if save/load system is holding the new attributes., initial dialogue screen works for garrick and meredith, but response screens are not working and buttons are not working.  patron selection is not linked and has similar button issues.
# ADR-050:  
working through dialogue handling infrastructure

- including narrative_schema.json from ADR-049, input handler, game_controller, dialogue engine, generic dialogue handler, dialogue ui utils.
- working through options to improve dialogue handling.  set stage for keyboard inputs, added service manger link in game controller.  next session will set keyboard inputs if successful.

# ADR-051: Keyboard-Driven Dialogue (Phase 8A)
# Status: Accepted
# Date: Sep 12, 2025
**Context:** Mouse click regions for dialogue (choice vs. response) required re-registration and frequently desynced with UI, causing “phantom” buttons and missed clicks.
**Decision:** Dialogue screens are keyboard-first.Choice mode: 1, 2, 3 select options. Enter chooses the first option. Response mode: Enter = primary (“Continue/Goodbye”), B/Backspace = Back, S = Shop (when present).
**Implementation:**
input_handler._handle_dialogue_keyboard_input(...) emits DIALOGUE_CHOICE or DIALOGUE_ACTION.
generic_dialogue_handler runs in keyboard mode and skips all clickable registration for dialogue.
dialogue_ui_utils.draw_standard_dialogue_screen(...) renders [1] [2] [3] labels; hover rectangles removed.
dialogue_ui_utils.draw_standard_response_screen(...) renders a hint strip with [Enter]/[B]/[S] (indentation fixed).
Navigation after goodbye/back uses the ScreenManager’s previous screen (baselocation or patron_selection, depending on entry).
**Consequences:**
Eliminates re-registration complexity and UI desync.
Consistent UX across all dialogue screens.
Mouse support can be reintroduced later (optionally) with event-driven updates, but is no longer required.

# ADR-052: Canonical UI Module Pinning (Import Guard)
# Status: Accepted
# Date: Sep 12, 2025
**Context:** Multiple archived copies of the repo existed under archive/, which let Python import a different utils/dialogue_ui_utils.py. This produced odd __file__ paths (“Redsstone”, “diallogue_ui_utils.ppy”, etc.) and hid code changes.
**Decision:** Pin and verify the canonical UI module at startup.
At main.py boot, compute project root and ensure it’s first in sys.path.  Import Redstone.utils.dialogue_ui_utils and immediately log its __file__.
On mismatch (path not under the active project), raise a loud error with a clear fix.
(Optional) print a directory scan of any other dialogue_ui_utils.py found under archive/ for visibility.
**Consequences:**Prevents “wrong file imported” mysteries.
Keeps dev and runtime aligned with the intended code.

## ADR-053: Standardized Dialogue Render Debug Traces
# Status: Accepted
# Date: Sep 12, 2025
**Context:** Needed reliable visibility into which renderer drew the frame.
**Decision:** Add one-line traces:
GDH: draw_generic_dialogue_screen [...] and GDH: draw_generic_response_screen [...]
DUI: draw_standard_dialogue_screen [...] and DUI: draw_standard_response_screen [...] (plus the pinned __file__ on first import)
**Consequences:**Faster diagnosis when output doesn’t match code. Helps catch indentation/branching issues immediately.

# ADR-054: Cleaned up mouse click items since moving to keyboard only for dialogues
GDH, Screeen Manage and dialogue ui utils
removed unnecessary code

# ADR-055: Schema-Aligned Dialogue System (Garrick Complete)
# Status: Accepted
# Date: Sep 12, 2025
**Context** Garrick dialogue had state mismatches with narrative schema and action processing dead ends causing "I see" responses and continue button cycling.
**Decision**Rewrote Garrick JSON to use schema states (first_meeting, after_first_talk, post_mayor) and fixed action response processing in dialogue engine.
**Implementation** dialogue_engine.py: Added action response content handling and fixed continue handler action storage
broken_blade_garrick.json: Complete rewrite with response content for all actions
Key fix: Store actions in normal response handling for continue button access
**Consequences** Positive: Complete dialogue flow with basement quest integration, scalable architecture for other NPCs
Resolved: Action dead ends, continue cycling, schema mismatches
Impact: Template established for remaining NPC dialogue implementations

# ADR-055: Patron Selection & Recruitment Foundation
# Status: Accepted
# Date: Sep 12, 2025
**Context**Patron selection had navigation failures and button layout issues preventing NPC recruitment system implementation.
Decision
Fixed BaseLocation NPCSelectionLocation to use dialogue_file from JSON instead of constructed screen names. Implemented centered button layout using constants.py. Created complete Gareth recruitment dialogue with schema alignment.
**Implementation**
BaseLocation fix: NPCSelectionLocation.handle_action() now uses npc.dialogue_file for navigation
Button constants: Added NPC button sizing constants to utils/constants.py
Gareth dialogue: Complete recruitment flow with gruff veteran personality, follows schema states
Recruitment mechanics: No recruitment until mayor_talked flag set
**Consequences**
Positive: Patron selection navigation working, professional button layout, complete recruitment template established
Outstanding: Location tracking issue causing incorrect return navigation from patron_selection→dialogue→back
Next: Mayor dialogue implementation to activate recruitment system

# ADR-056: BaseLocation Universal Keyboard Navigation
**Status: Accepted**
# Date: Sep 12, 2025
**Context:** Dialogue navigation bug: patron_selection→dialogue→back incorrectly returned to broken_blade_main. BaseLocation screens lacked keyboard back navigation.
**Decision:** Fixed dialogue navigation using NPC context routing. Added universal B/Backspace/ESC keyboard navigation for all BaseLocation screens using pattern-based detection.
**Implementation:**
Modified dialogue_engine.py: Patron NPCs return to patron_selection, tavern staff return to broken_blade_main
Added input_handler.py: Pattern-based screen detection (*_main, *_selection, *_hub) triggers LOCATION_ACTION back events
Eliminated dependency on broken ScreenManager navigation history
**Consequences:** Fixed patron_selection navigation bug. Universal keyboard navigation for all BaseLocation screens without hardcoding. Scales automatically to future location types.
Files Modified: game_logic/dialogue_engine.py, input_handler.py

# ADR-057: Recruitment System Alignment
# Status: Accepted
# Date: Sep 13, 2025
**Context** After speaking to the Mayor, recruitable NPCs (e.g., Gareth) still showed “talk to mayor first.” Root causes: conflicting schema flags, quest vs. recruitment state drift, dialogue actions not applying effects, and missing computed props in condition checks.
**Decision**
Align the recruitment flow around the narrative schema as the single source of truth:
Schema cleanup — Remove/normalize conflicting availability_flag entries.
Party sync — When any *_recruited flag changes, sync game_state.party_members.
Action effects — Process effects declared on dialogue actions (e.g., set quest_active).
Computed props — Expose recruited_count/can_recruit_more to dialogue condition evaluation.
**Consequences**
Recruitment works end-to-end: Mayor → quest activation → recruitment options → party tracking. Party size limits enforced via computed props (max 3 recruits).Cleaner separation of concerns and a repeatable pattern for Elara, Thorman, and Lyra. Save/load persists recruitment progress without drift.
**Implementation Notes**
data/narrative_schema.json: remove/normalize availability references. game_logic/dialogue_engine.py: apply action effects; add computed props to eval context; add _sync_party_members_list().
Dialogue JSONs: confirm quest_active and *_recruited effects where used.
**Affected Files**
data/narrative_schema.json, game_logic/dialogue_engine.py, data/dialogues/,broken_blade_mayor.json, data/dialogues/broken_blade_gareth.json
**Validation**
Mayor sets quest_active. Gareth presents recruitment when expected. *_recruited flags update party_members. Party-size guardrails respected. State survives save/load.
**Result:** Recruitment flow unblocked and standardized; architecture scales cleanly to all four recruitable NPCs.

# ADR-058: Made VSC setup changes
# Sep 13, 2025
hid pycache from view, hid from github, added repository structure file, added script folder and file to build repo folder structure.

# ADR-059: some small cleanup changes
- small clean up files to clean some items up.  tried to fix quest # showin 4 party vs. 3 party.  encountered dialogue issues. reverted.

# ADR-060  Dialogue Engine Direct Flow Architecture
# Date: September 13, 2025
# Status: Implemented
**Decision**Replace complex dialogue response-action system with direct state transition flow driven by narrative schema.
**Problem** The previous dialogue system used intermediate response screens with action buttons, creating: State management conflicts between dialogue engine and UI
Complex action processing logic scattered across multiple methods
Inconsistent flag timing causing "I don't understand" errors
Difficult content authoring requiring code changes for new NPCs

**Solution** New Flow Pattern,  NPC Message + Options → Player Choice → New NPC Message + Options → Repeat, Key Components
**Narrative Schema State Mapping:** Centralized dialogue state determination
Forced State Processing: Consistent state throughout choice processing chain
Direct JSON Transitions: next_state field drives conversation flow
Immediate Effect Processing: Flags updated when choices are selected
**Technical Implementation**
Modified process_dialogue_choice() to accept forced_state parameter
Updated get_conversation_options() to respect forced state
Eliminated response action complexity in favor of direct transitions
Integrated narrative schema evaluation with proper timing
**Consequences** Positive
Simplified Content Creation: New NPCs require only JSON dialogue files
Consistent State Management: Single source of truth for dialogue states
Improved Debugging: Clear state evaluation with comprehensive logging
Professional Architecture: Industry-standard dialogue tree pattern
**Negative**
Migration Required: Existing NPCs need dialogue file updates
Input Handler Adjustment: UI input processing needs minor updates
Learning Curve: Content creators need to understand narrative schema
**Validation** Tested with Garrick NPC dialogue:
State transitions work correctly (first_meeting → knows_about_ruins)
Effect processing functions (learned_about_ruins flag set)
Conversation data updates properly, still has issues to troubleshoot.

# ADR-061 Dialogue Progression & Screen Navigation
# Date: September 13, 2025
# Status: Implemented
**Context:** Completion of Session 8A dialogue system refactoring
**Decision**Implement progressive dialogue states with automated screen navigation for conversation endings.
**Problem**NPCs repeated same dialogue options after significant interactions (conversation loops)
Conversations ending with next_state: exit left players on blank screens instead of returning to originating location
**Solution** Progressive Dialogue: Each significant interaction advances to new states rather than looping, Example: knows_about_ruins → gave_mayor_directions → helpful_conclusion → exit
**Automated Navigation:** DialogueEngine emits DIALOGUE_ENDED events; ScreenManager handles return to originating location using stored {npc_id}_current_location
Technical Implementation
**Validation**Tested Garrick dialogue: first_meeting → knows_about_ruins → gave_mayor_directions → automatic return to broken_blade_main. All transitions work correctly.
**Impact**Completes dialogue system refactoring (ADR-058). Creates professional dialogue system with natural conversation progression and seamless navigation suitable for commercial RPG development.

# ADR-062:  garrick dialgoue
- changed to simple one screen with no response screen.  only slightly better still dialogue use errors.

## ADR-063: Dialogue System Architecture Complete Implementation **Status**: Resolved  
**Date**: September 14, 2025
### Final Resolution Summary
Successfully completed dialogue system architecture redesign, resolving all progression and input handling issues. System now provides professional RPG dialogue functionality with natural conversation flow.
### Final Technical Issues Resolved
**Keyboard Input Mapping Bug**:
- **Issue**: Dialogue choices beyond option 3 were not processed due to hardcoded choice key limitations
- **Root Cause**: Duplicate `choice_keys` dictionary definitions, with second definition overwriting expanded key mapping
- **Resolution**: Removed duplicate dictionary, maintained single expanded mapping supporting keys 1-9
**State Management Integration**:
- **Issue**: Dialogue state evaluation competing between stored states and schema conditions
- **Resolution**: Implemented hybrid approach prioritizing stored states during active conversations, schema evaluation for fresh interactions
**Conversation Exit Handling**:
- **Issue**: Players getting stuck in story-specific dialogue branches after conversation completion
- **Resolution**: Clear both dialogue state and conversation data on exit, enabling contextual state re-evaluation
### Architecture Achievements
**Professional State Management**:
- Hybrid stored/evaluated state system prevents stuck conversations
- Flag-based condition evaluation enables contextual dialogue responses
- Automatic state clearing on conversation exit maintains narrative coherence
**Scalable Input System**:
- Dynamic keyboard handling supports 1-9 dialogue choices
- Consistent input patterns across all dialogue interactions
- Proper exit handling via multiple input methods (Backspace, B key, choice selection)
**Content Creation Framework**:
- Single JSON file creation for new NPCs
- Narrative schema integration for professional state management
- Casual chat pattern prevents social interaction dead-ends
### Outcome Validation
**Functional Requirements Met**:
- ✅ Dialogue progression through conversation trees
- ✅ Natural exit from conversations
- ✅ Contextual dialogue state reset on re-engagement  
- ✅ Multi-choice keyboard input handling
- ✅ Professional conversation flow without stuck states
**Architecture Standards Maintained**:
- ✅ Event-driven communication between systems
- ✅ Single responsibility separation maintained
- ✅ Data-driven content creation approach
- ✅ Professional error handling and recovery
- ✅ Industry-standard dialogue state management
### Development Impact
**Code Quality**: Resolved complex architectural conflicts while maintaining clean separation of concerns
**Maintainability**: Established patterns for future NPC dialogue creation  
**User Experience**: Natural conversation flow prevents player confusion or stuck states
**Scalability**: Framework supports unlimited NPC additions through JSON configuration
### Key Learning
The dialogue system required hybrid architecture combining stored state management for conversation continuity with dynamic evaluation for contextual appropriateness. Pure approaches (only stored states OR only dynamic evaluation) failed to provide professional RPG dialogue experience.
The resolution demonstrates successful integration of multiple architectural patterns to achieve professional game dialogue functionality.

# ADR-064 Streamlines NPC Dialogue Flow + Schema ordering

# Status: Accepted
# Date: 2025-09-14
**Context**
Prior dialogue flow had a transient “response layer” and inconsistent gating semantics. This caused sticky states, phantom next_state hops, and hard-to-debug routing (e.g., casual chat shadowed by broader rules). We refactored around Garrick and validated end-to-end.
**Decision**
Remove response layer — Options now transition directly to another state or to exit.
Gating syntax is canonical
Schema routing is order-sensitive — Put more-specific conditions before broader ones. Example for Garrick:
casual_chat (pre-mayor) before knows_about_ruins.
Post-mayor states ordered: complete → accepted → offered → no_basement.
Flags must be declared — Any flag referenced in dialogue_state_mapping must exist in npcs.<id>.story_flags.

End-of-quest graduation — Add a “report/ack” flag (e.g., reported_basement_victory and optional post_payment_acknowledged) to prevent payout/victory loops and return to an idle state (or casual chat).

**Engine hygiene**
Use stored dialogue state only while a conversation is in progress.,  On goodbye, clear *_dialogue_state, *_conversation_data, and *_dialogue_in_progress.

Load JSON with encoding="utf-8" to avoid curly-quote artifacts.

**Alternatives Considered**
Keep response layer and patch bugs → rejected (extra complexity, more moving parts).
OR routing in schema → rejected; current evaluator supports simple boolean expressions with ordering, which is sufficient.

**Consequences**
Pros: Simpler authoring, predictable routing, fewer edge cases; casual chat works reliably; quests advance with clear flags.
Cons: Authors must define substates for info beats (no free “response” text). Schema order becomes part of the contract.

**How to Author (summary)**
Every option: id, text, next_state: "<state>" | "exit", optional effects, optional requirements.
Don’t use "response" fields.
Define all referenced next_state names.
Declare all flags used in routing under npcs.<id>.story_flags.
In schema, list specific conditions first; broad catch-alls last.

**Migration Notes (applied in Garrick)**
Converted casual-chat gates to requirements.flags.
Added missing flags: accepted_basement_quest, reported_basement_victory, etc.
Reordered Garrick mapping: casual_chat before knows_about_ruins; post-mayor fan-out in specific→broad order., Added one-time post-payment ack to graduate from payout screen., Removed DEV hooks and phantom states; replaced any missing next_state with real states or exit.
Implemented engine fixes: in-progress gating for stored state; full clear on goodbye; UTF-8 JSON load.

**Test Checklist (must pass for each NPC)**
First meeting: info options route to real substates (no self-loops unless intended)., Rumor/info flags unlock gated items via requirements.flags., Pre-mayor: casual_chat wins over broader knowledge states., Post-mayor quest path: offered → accepted → complete → reported/paid → stable idle/casual., No phantom states; no "response" fields remain; exit returns to location cleanly.
**Rollout**
Clone the Garrick pattern to Meredith, Pete, etc.,Validate with the above checklist; keep schema ordering discipline. Remove any temporary DEV flags/options before commit.

# ADR- 065 Unified NPC Dialogue Pattern & Key NPC Implementations
# Status: Accepted
# Date: 2025-09-14
**Context**
Previous dialogue used a “response layer,” caused sticky state bugs, inconsistent gating, and authoring friction. We need predictable routing and fast content creation across core NPCs (Mayor, Garrick, Meredith, Gareth, Elara, Thorman, Pete).
**Decision**
State-only dialogues: remove response layer; each option goes to a state or exit.
Gating: use requirements: { "flags": { ... } } (AND semantics).
Schema ordering: evaluate in insertion order; list specific → broad.
Flags discipline: any flag used in routing must be declared under npcs.<id>.story_flags.
Engine hygiene: only reuse stored state in-session; clear on goodbye; load JSON with UTF-8.
**Consequences** **Pros:** simpler authoring, predictable flows, easy testing. **Cons:** authors must define substates (no freeform responses) and maintain mapping order.

# ADR-066 - Small fixes, patron screen ui, save/load, F5 quick save
-Sep 14, 2025
- updated patron selection json to allow for image upload.  
- updated base location to fix patron selection ui for NPC screen, party portrait grid, button position.  added, back button.
- some gamestates were not working on save/load/  added dynamic narrative schema load to ensure save and load were accurate.
fixed F5 quicksave button. 

# ADR-067: Screen Naming Convention Fix
# Date: September 14, 2025
# Status: Implemented
Decision- Fixed dialogue navigation by implementing conditional screen naming logic in dialogue_engine.py:
All other locations → location_id directly (new standard)
Problem
Patron selection NPCs were failing to return from dialogue due to missing patron_selection_main screen (only patron_selection exists).
Solution
✅ Patron selection dialogue navigation works
✅ Future locations use cleaner naming (no _main suffix)
✅ Fixed main menu QUIT button (controller.shutdown() vs controller.quit_game())
Files Modified
game_logic/dialogue_engine.py - Screen naming logic
main.py - Event handler method call

# ADR-068: Shopping System Integration via Event-Driven Architecture
# Status: Partially Complete
# Date: September 15, 2025
**Decision:** Implement shopping integration using event-driven architecture with OPEN_SHOPPING events triggered by dialogue effects, maintaining clean separation between dialogue, commerce, and UI systems.
Implementation: DialogueEngine processes open_shop effects and emits OPEN_SHOPPING events. ScreenManager handles screen transitions and coordinates merchant data loading from ItemManager. CommerceEngine handles business logic via COMMERCE_* events.
**Result:** Shopping screen successfully renders with proper merchant data. Dialogue → shopping flow functional. Architecture maintains single responsibility principle with proper event routing.
Remaining: Button functionality, overlay conversion, UI polish.


# ADR-069: Shopping System Event-Driven Integration
# Status: Implemented
# Date: September 15, 2025
**Decision:** Implement shopping system using event-driven architecture with dialogue effects triggering OPEN_SHOPPING events, JSON-driven merchant filtering, and proper separation of concerns.
Problem: Legacy shopping.py existed but wasn't integrated. ItemManager methods didn't match expected interfaces. CommerceEngine hardcoded merchant references.
**Solution:**
DialogueEngine processes open_shop effects and emits OPEN_SHOPPING events
ScreenManager loads merchant configuration from JSON and filters items using include_ids
CommerceEngine accesses pre-filtered merchant data from GameState
Shopping screen renders as full screen with proper merchant inventory display
**Implementation:** Created complete event chain from dialogue choice to functional shopping screen. Eliminated hardcoded merchant references. Established JSON-first merchant configuration workflow.
Result: Functional shopping integration displaying filtered inventory (Strong Ale, Torch, Trail Rations) with proper merchant data structure. Foundation established for complete commerce system.
**Technical Debt:** Item interaction, purchase processing, and overlay conversion remain for next phase.
Files Modified: ui/screen_manager.py, game_logic/commerce_engine.py, data/dialogues/broken_blade_garrick.json, data/merchants.json


# ADR-070: Tabbed Shopping System
# Status: Implemented
**Date: December 2024**
**Context:** Single-screen shopping interface couldn't scale to support selling mechanics and became inconsistent with other overlay systems in the game.
**Decision:** Implement tabbed shopping system using BaseTabbedOverlay framework with persistent merchant stock tracking and category-based commerce restrictions.
**Implementation:**
Converted shopping system to three-tab overlay (BUY/SELL/INFO)
Added GameState.merchant_stocks for exploit prevention
Implemented category-based buying restrictions per merchant type
Created cart-based selling system matching purchase UX
**Consequences:**
Positive: Unified overlay experience, prevents infinite buying exploits, enables merchant specialization, provides foundation for commerce expansion
Negative: Increased system complexity, required InputHandler modifications for screen-specific overlay routing
Architecture: Eliminated register_shopping_screen_clickables() and related methods, established pattern for future merchant implementations

# ADR-071: Quest System Completion Logic & UI Enhancement
# Date: Sep 16, 2025
# Status: Accepted
**Context:** Party building quest showed as incomplete despite having full party (3 members). Rat basement quest missing from quest log. Quest UI had text overflow and inconsistent sizing issues.
**Decision:** Implemented smart quest completion logic and professional UI improvements.
**Implementation:**
Added missing rat quest: Created basement_rat_combat quest with 4 objectives matching existing game flags
Fixed party completion: Custom logic completes party building quest when party_ready objective achieved (3+ recruits)
Progress display: "COMPLETE" text for finished quests instead of confusing partial ratios
UI polish: Repositioned progress column, smaller fonts, text wrapping for objectives with color preservation
**Technical Changes:**
Enhanced Quest._check_quest_completion() with quest-specific completion rules
Added quest sync logic in update_from_game_state() for rat quest progression
Updated quest overlay rendering with manual text wrapping and proper color handling
Modified progress display logic in both active and completed quest tabs
**Result:** Professional quest system with intuitive completion logic, clean UI presentation, and proper objective tracking for all quest types.
Files Modified: utils/quest_system.py, quest overlay rendering file

# ADR-072 - Town Navigation Tile System Implementation
# Status: Accepted
# Date: 9/17/2025
**Context:** Game previously limited to tavern interior with no exploration mechanics. Players needed ability to navigate between buildings and explore the town environment to create proper RPG progression and world-building.
**Decision:** Implement professional tile-based navigation system with scrolling camera for Redstone town exploration, using 64x64 tile grid with 13x7 visible window and colored tile graphics as Phase 1 foundation.
Implementation:

**Created data-driven map system:** data/maps/redstone_town_map.py with 16x12 tile layout and building definitions
Added navigation screen: screens/redstone_town_navigation.py with scrolling camera, movement timing, and building interaction system
Integrated with existing architecture: Seamless BaseLocation transitions, ScreenManager registration, and party status panel consistency
Minimal code changes: Only 11 lines modified across 3 existing files (game_state.py, screen_manager.py, constants.py)
Professional fallback system: Colored rectangle tiles provide immediate functionality while graphics system remains ready for Phase 2 upgrade
**Technical Approach:**
Scrolling camera system: 876x510 pixel display area shows portion of larger 1024x768 town map with smooth player-centered camera
Building interaction: Walk-to-building-and-press-ENTER system with visual prompts for entry points (still needs to be validated)
Asset organization: Professional tile graphics structure ready for Phase 2 (graphics), Phase 3 (multi-tile), Phase 4 (animation)
**Consequences:**
Major gameplay expansion: Players can now exit tavern and explore full town environment with proper RPG navigation
Foundation for world exploration: Scalable architecture supports future world map, location discovery, and complex area navigation
Visual progression: Clear upgrade path from colored tiles → graphics → multi-tile buildings → animations maintains development momentum
**Created:** data/maps/redstone_town_map.py, screens/redstone_town_navigation.py
**Enhanced:** game_state.py (player position), screen_manager.py (registration), constants.py (asset paths)

# ADR-073: Conditional Button System Implementation
# Status: Accepted
# Date: September 17, 2025
**Context:** Dynamic quest-gated content needed for basement access after Garrick dialogue trigger
Decision: Implemented flag-based requirements system in ActionHubLocation with JSON configuration support
**Implementation:**
Added evaluate_requirements() method with flag validation logic
Enhanced render method to filter actions based on requirements before button creation
Updated broken_blade.json with basement action requiring accepted_basement_quest: true
Created temporary basement placeholder screen with navigation back to tavern
**Consequences:**
Positive: Zero-code conditional content workflow established; basement button appears only when quest accepted; clean data-driven architecture maintained
Foundation: Pattern ready for all future quest-gated locations, NPCs, and actions via JSON requirements blocks
Files Modified: ui/base_location.py, ui/screen_manager.py, data/locations/broken_blade.json

# ADR-074: Unified XP & Narrative Event Architecture
# Date: Sep 18, 2025
**Context.** XP was awarded in multiple places (DialogueEngine, ad-hoc handlers), schema tables were sometimes nested, and recruitment/completion logic risked duplication and drift.
**Decision.** Centralize all XP logic in QuestEngine, driven by neutral events and schema:
DialogueEngine only sets flags and emits FLAG_CHANGED (and optional PARTY_MEMBER_RECRUITED for objectives/UI).
QuestEngine.on_flag_changed handles two cases:
Dialogue/discovery triggers via _evaluate_quest_triggers.
Per-recruit awards via _award_recruit_xp_for_flag when *_recruited flips.
PARTY_MEMBER_RECRUITED is objective-only (no XP).
Narrative schema is read from schema["quest_triggers"] (supports nested party_recruitment_triggers and quest_completion_triggers).
XPManager.get_reward supports flat keys (e.g., recruitment_bonus), multipliers (quest_multipliers.X × base_quest_xp), and dict form {base, mult, plus}.
One EventManager instance is created in GameController and shared by all systems.
One source of truth for quest completion XP (choose either QuestEngine or the consumer of QUEST_COMPLETED, not both).
**Consequences.**
Deterministic, schema-driven XP; DialogueEngine stays thin.
Per-recruit XP is consistent and guarded (e.g., xp_awarded__recruit__{flag}) to prevent duplicates.
Authors can tune rewards by editing JSON only.
Fewer integration bugs from multiple event buses or duplicated award paths.
Easier debugging: FLAG_CHANGED → QuestEngine evaluators → single XP_AWARDED emit.


```
## ADR-XXX: <Short title>
- **Status:** Proposed | Accepted | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Context:** …
- **Decision:** …
- **Consequences:** …
```

