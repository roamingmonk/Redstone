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
# Status: Partly superceedd by ADR 101
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

# ADR-075:  Character Sheet update, add XP, level
# Date: Sep 18, 2025
**Context.** Added uo to include level, XP and progress bar to character sheet.
when next level is reached, a button appears to LEVEL UP!
Functionality for the button is still needed to be added.

## ADR-076: Character Advancement System Implementation
**Status:** Accepted  
**Date:** Sep 19, 2025  
**Context:** Need functional level-up system with player choices, data-driven progression, and proper UI integration
**Decision:** Implement 4-tab character overlay with JSON-driven level progression and functional advancement interface
**Implementation:**
- **4-Tab Character Overlay:** Player/Party/Abilities/Advance tabs using BaseTabbedOverlay framework
- **Data-Driven Progression:** Level advancement data stored in enhanced character_classes.json with features, descriptions, and ability score choices
- **Functional Level-Up Interface:** ADVANCE button triggers existing CharacterEngine.level_up() method with player feedback
- **Player Feedback System:** Recent advancement display shows level gained, HP increase, and new abilities
- **JSON Integration:** Direct JSON reading bypasses CharacterEngine data structure differences
**Technical Features:**
- Level progression requirements from narrative_schema.json (300/900/2700/6500 XP)
- Class-specific features: Fighter gains Combat Surge(L2), Extra Attack(L3), Shield Focus(L4), Terror Resistance(L5)
- HP calculation using class hit die + CON modifier with proper dice rolling
- Results display shows: new level, HP gained, total HP, abilities gained
**Files Modified:** character_overlay.py, character_classes.json
**Benefits:** Professional advancement system ready for all 4 classes, player agency in level-up process, clean separation of data and logic

# ADR-077: Character Advancement System with JSON-Driven Progression
**Status:** Accepted  
**Date:** Sep 19, 2025  
**Context:** Need complete level-up system with ability descriptions, XP persistence, and data-driven progression
**Decision:** Replace hardcoded CharacterEngine class data with JSON-based system and implement 4-tab character overlay with functional advancement interface
**Implementation:**
- **Data Consolidation:** Eliminated hardcoded _get_class_data() method, replaced with _load_class_data_from_json() reading from character_classes.json
- **XP Persistence:** Fixed cumulative XP system - characters retain full XP totals after leveling, save/load preserves experience field
- **4-Tab Character Interface:** Player/Party/Abilities/Advance tabs with ability descriptions from feature_descriptions JSON section
- **Level-Up Integration:** ADVANCE button triggers existing CharacterEngine.level_up() with player feedback showing gained features
- **D&D 5e HP System:** Maintained proper dice rolling (1d[hit_die] + CON modifier) with debug output for transparency
**Technical Benefits:**
- Single source of truth: character_classes.json drives all class progression
- Ability descriptions displayed inline with features gained
- Clean separation: UI detects advancement, engines handle business logic, JSON stores configuration
- Cumulative XP system matches modern RPG expectations
**Files Modified:** character_overlay.py, character_engine.py, character_classes.json, save_manager.py, game_state.py
**Result:** Professional character advancement system with data-driven progression, persistent XP, and clear player feedback

# ADR-078: Complete Character System Implementation
**Status:** Accepted  
**Date:** Sep 19, 2025  
**Context:** Implemented comprehensive level-up system with JSON-driven progression, XP persistence, and party advancement
**Decision:** Replace hardcoded character progression with data-driven system using 4-tab character overlay and functional advancement interface
**Implementation:**
- **Data Architecture:** Eliminated hardcoded _get_class_data() method, replaced with _load_class_data_from_json() reading from character_classes.json with feature_descriptions section
- **XP System:** Fixed cumulative XP persistence - characters retain full XP totals after leveling, save_manager preserves experience field, party members receive XP alongside player
- **4-Tab Character Interface:** Player/Party/Abilities/Advance tabs with dynamic level display and ability descriptions from JSON
- **Party Advancement:** NPCs level up simultaneously with player, party tab shows real-time level updates from game_state.party_member_data
- **Level-Up Flow:** ADVANCE button triggers CharacterEngine.level_up() with player feedback, party member advancement, and cumulative XP preservation
- **D&D 5e Mechanics:** Maintained proper dice rolling (1d[hit_die] + CON modifier) with debug output and minimum 1 HP rule
**Technical Benefits:**
- Single source of truth: character_classes.json drives all class progression and ability descriptions
- Clean separation: UI detects advancement, CharacterEngine handles business logic, JSON stores configuration
- Dynamic party display: Party tab reads actual character data instead of hardcoded values
- Professional advancement feedback: Players see HP gained, abilities acquired, and XP progression
**Files Modified:** character_overlay.py, character_engine.py, character_classes.json, save_manager.py, game_state.py
**Result:** Complete character advancement system with data-driven progression, persistent XP, party advancement, and clear player feedback ready for ability score choices at level 3

# ADR-079:  equipment structure cleanup
**Date:** Sep 19, 2025  
- gamestate, character engine, inventory engine, character creation, inventory overlay, constants, items and character classes.jsons
- data standarization using item ids and internal connection. linked character creation to items, to inventory in a single method.  Json->character engine->gamestate->UI display

# ADR-080: Character Ability Progression System Fix
# Status: Accepted
# Date: Sep 20, 2025
**Context:** Level-up system failed to assign class abilities due to JSON structure mismatch - code expected class_data['abilities'] but JSON used class_data['level_progression'][level]['features']
Decision: Fix ability assignment logic to properly read from JSON structure and implement unified modifier calculation system
Implementation:
Fixed level-up ability parsing: level_data.get('features', []) instead of incorrect class_data['features']
Added calculate_all_modifiers() method to CharacterEngine for unified stat/ability processing
Verified ability accumulation works correctly across levels (Combat Surge at L2, Extra Attack at L3, etc.)
Result: Character abilities now properly assigned during level-up, modifier system functional for future combat/social/exploration mechanics integration
Files Modified: character_engine.py

# ADR-081 Sharted Tiel Graphic system
# Status: Accepted
# Date: Sep 20, 2025
**Context:** Town navigation system used basic colored rectangles without scalable graphics architecture. Multiple future tile-based systems (other towns, world map, dungeons) would require graphics capabilities with consistent loading and fallback behavior.
**Decision:** Implement shared tile graphics utility using singleton pattern with professional fallback system, enabling graphics upgrades while maintaining functionality with zero art assets.
**Implementation:**
Created shared graphics utility: utils/tile_graphics.py with singleton TileGraphicsManager class supporting all tile-based systems
Universal architecture: 23 tile types and 4-directional player sprites loaded and cached for use across all future tile systems
Enhanced visual presentation: Clean tile borders, consistent color scheme, professional grid layout with maintained 60 FPS performance
**Technical Approach:**
Professional API: Clean interface for tiles (get_tile_image()), player sprites (get_player_sprite(direction)), and extensibility (add_custom_tile())
Future-ready structure: Asset organization supports terrain, buildings, decorations, characters, and world map graphics
**Consequences:**
Immediate functionality: System works perfectly with colored fallback tiles, no graphics creation required for deployment
Scalable architecture: Future towns, world map, and dungeon systems automatically inherit graphics capabilities and loaded assets
Memory efficiency: Single instance loads and caches all graphics, preventing duplication across multiple tile-based screens
Development flexibility: Graphics can be added incrementally - each file immediately improves visual quality without code changes
Professional foundation: Industry-standard graphics management ready for commercial-quality tile graphics and sprite animations
**Files Created:** utils/tile_graphics.py
**Files Modified:** screens/redstone_town_navigation.py (uses shared manager), constants.py (tile paths)

# ADR-082 save and quit button add to save screen
# Status: Accepted
# Date: Sep 20, 2025
- added save and quit button the F7 save screen
- event driven and used same quit event system 

# ADR-083 itemManager API unification
# Status: Accepted
# Date: Sep 21, 2025
**Context** The item system used competing lookups and mixed ID/name storage, causing icon-load failures and sellable-item logic errors across the codebase.
**Problem** Multiple ItemManager methods (e.g., get_item_by_id, get_item_by_name, get_item_icon_by_name) and mixed ID/name inventory formats led CharacterEngine, CommerceEngine, and UI overlays to disagree, producing “No items to sell” despite valid inventory.
**Decision** Adopt a unified ID-only ItemManager API as the single source of truth by keeping get_item_by_id(item_id) and get_item_icon(item_id), adding get_display_name(item_id), and removing get_item_by_name() and get_item_icon_by_name().
**Data Storage** Standardization Store all equipment and purchases as lowercase_underscore IDs in CharacterEngine and CommerceEngine, use IDs internally throughout shopping/inventory flows, and convert to display names only at render time.
**Implementation** Refactor ItemManager to a single-lookup pattern, update CharacterEngine to persist IDs, adjust CommerceEngine to append IDs, change inventory_overlay.py and shopping_overlay.py to call get_item_icon(item_id), and unify sellable-items logic to operate on IDs.
**Results** Sellable items display with correct quantities and prices; all inventory uses consistent lowercase_underscore IDs; the API surface is simpler to maintain; and new items require only JSON updates.
**Files Modified** game_logic/item_manager.py, game_logic/character_engine.py, game_logic/commerce_engine.py, screens/inventory_overlay.py, and screens/shopping_overlay.py.
**Validation** Character creation persists equipment as IDs, purchased items appear with correct pricing for selling, inventory displays human-readable names derived from IDs, and shopping/sell carts function end-to-end.

## ADR-084: DiceGameEngine Architecture Implementation
- **Status:** Accepted
- **Date:** Sep 21, 2025
- **Context:** Dice game logic scattered across GameState methods violating Single Data Authority principle
- **Decision:** Extract dice game business logic into dedicated DiceGameEngine following established engine patterns
- **Implementation:** Created dice_game_engine.py, moved stats to character['gambling_stats'], added event handlers
- **Consequences:** Clean separation of concerns, proper statistics tracking, event-driven architecture compliance
- **Files Modified:** dice_game_engine.py, game_controller.py, screen_manager.py, screen_handlers.py, gambling_dice.py, game_state.py

## ADR-085: Added simple animation on title screen
**Status:** Accepted
**Date:** Sep 22, 2025
**Context:** Added animated pixel art sprites to title screen for professional atmosphere.
**Decision:** Implement reusable SpriteAnimation class with timing control and transparency support.
**Implementation:** Created utils/animation.py with frame extraction, timing updates, and drawing methods.
**Integration:** Added 64x64 campfire animation to title screen with proper alpha channel handling.
**Architecture:** Animation states stored in game_state for persistence across screen refreshes.
**Benefits:** Scalable system ready for tavern torches, spell effects, and character animations.
**Files:** utils/animation.py, constants.py, title_menu.py, assets/images/sprites/fire/campfire_animation.png.
**Result:** Professional animated title screen foundation for all future game animations.

## ADR-086: Combat system setup
# Date: September 24, 2025
**Decision:** Integrate combat system following established engine/UI separation pattern
**Context** Need to add combat encounters to Terror in Redstone while maintaining architectural consistency with existing BaseLocation and DialogueEngine patterns.
**Decision** Implement two-layer combat system: CombatEngine (business logic) + CombatSystem (UI presentation) with JSON-driven encounter configuration.
**Implementation** 
**CombatEngine:** Loads encounters from JSON, processes combat logic, manages state
** CombatSystem:** Generic UI renderer, delegates all logic to CombatEngine
**Integration:** ScreenManager registration, InputHandler clickable registration, EventManager action routing
**Configuration:** JSON encounter files in data/combat/encounters/ directory
**Consequences:** Positive: Maintains architectural consistency, enables JSON-only encounter creation, clean separation of concerns, follows established patterns
Negative: Requires dual-file structure for combat features
Risk Mitigation: Extensive logging and error handling implemented
**Technical Details**
Fixed draw_button() parameter mismatch, implemented InputHandler registration via register_combat_clickables(), integrated with existing event system for 

## ADR-087: Town Navigation System
# Date: September 25, 2025
**Decision:** Implement tile-based town navigation with directional building entrance system
**Context**  Players needed ability to navigate between buildings and explore town environment for proper RPG progression and world-building.
**Decision** Implement directional entrance system where buildings have designated entry tiles rather than walkable building tiles or adjacent-tile entry.
**Implementation** Created data-driven map system with 16x12 tile layout, entrance point definitions per building, visual interaction prompts, and graceful fallback handling for unimplemented buildings.
**Consequences** Positive: Realistic building interaction, clear visual feedback, professional RPG navigation feel, complete architecture validation of Screen/Event/Input managers
**Negative:** Requires coordinate precision for entrance positioning
**Risk Mitigation:** Debug utilities and systematic entrance coordinate validation implemented
**Technical Details**  Town map data defines building positions and entrance tiles separately, interaction detection uses entrance-point lookup, temporary message system provides user feedback for closed buildings.
**Validation** Complete navigation loop functional: town exploration → building detection → entrance prompts → tavern entry → return to town → unimplemented building fallback handling.

## ADR-088: Shared Navigation Renderer
# Date: September 25, 2025
**Status:** Accepted
**Context:** Town navigation worked but created code duplication concerns for future locations.
**Decision:** Implemented NavigationRenderer utility class in ui/base_location_navigation.py with location-specific wrappers.
**Implementation:** Extracted camera, movement, rendering, collision, and debug logic to shared utility; town navigation reduced to configuration + location-specific behavior.
**Consequences:** New locations require ~50 lines vs 300+ lines; shared movement/rendering logic; automatic debug info on all navigation screens.
**Files:** Created ui/base_location_navigation.py, refactored screens/redstone_town_navigation.py

# ADR-088A: Direct NPC Dialogue Integration from Town Navigation
# Status: Implemented  
# Date: Sep 26, 2025
**Context:** Adding new merchant NPCs required hardcoded elif chains in town navigation and separate screen creation.
**Decision:** Implement data-driven building interactions with direct dialogue integration using narrative schema location lookup and standardized event routing.
**Implementation:**
- Town map BUILDING_ENTRANCES defines interaction_type (npc_dialogue vs screen_transition)
- NPC_CLICKED events use narrative_schema.get_npc_location() for proper screen routing
- Automatic dialogue screen registration from JSON files ({location}_{npc} pattern)
- Shopping integration via dialogue effects (open_shop) with post_shopping states
- Screen naming convention: location screen name must match location_id for proper return navigation
**Result:** Adding new merchant NPCs requires only JSON configuration - no code changes. Eliminates elif proliferation and enables unlimited NPC scaling through pure content creation. Complete dialogue-to-shopping-to-navigation flow working seamlessly.
**Files Modified:** redstone_town_navigation.py (now redstone_town.py) screen_manager.py, narrative_schema.py, redstone_town_map.py
**Architecture Validation:** Direct town navigation → NPC dialogue → shopping → return navigation working end-to-end

# ADR-088 B:  Merchant Category Filtering & Shopping Pagination System
# Status: Complete
# Date: Sep 26, 2025
**Context:** Merchant inventory showed only hardcoded include_ids items instead of category-based filtering. Shopping interface couldn't handle large inventories (42+ items) requiring pagination across BUY/SELL tabs.
**Decision:** Fix category filtering logic in ItemManager and implement multi-tab pagination with keyboard navigation for shopping interface scalability.
**Implementation:**
- Removed duplicate inventory logic from ScreenManager, delegated to ItemManager.get_merchant_inventory()
- Category filtering now works properly for merchants using stock_categories instead of include_ids
- Added pagination state per tab (buy_page, sell_page) with UP/DOWN + P/N keyboard navigation
- Extended BaseTabbedOverlay with previous_page()/next_page() methods for reusable pagination
- Shopping tabs independently paginate with "Page X of Y" display
**Root Cause:** ScreenManager had hardcoded include_ids-only filtering that bypassed ItemManager's category system.
**Result:** Merchants display full category-based inventory (weapons, armor, consumables, items). Shopping interface scales to unlimited items with professional pagination. Architecture supports future tabbed interfaces requiring pagination.
**Files Modified:** screen_manager.py, item_manager.py, base_tabbed_overlay.py, shopping_overlay.py

# ADR-089: consolidated draw_centered_text 
# Status: Complete
# Date: Sep 26, 2025
- def draw_centered_text method was found across numerous files. moved all to link to graphics.py - def draw_centered_text
- Removing duplication saves code and easier imports

# ADR-090: RPG Combat Statistics Integration
# Status: Accepted
# Date: September 26, 2025
**Context:** Character overlay displayed basic stats but lacked professional RPG combat information (AC, attacks per round, weapon damage with modifiers).
Decision: Implement StatsCalculator utility with complete JSON-driven combat stat system integrating D&D-style calculations into existing character display.
**Implementation:** Enhanced items.json with combat_stats (damage_dice, armor_class, weapon_properties) for all 40+ items
Added character_classes.json combat progression (base_attack_bonus, attacks_per_round arrays)
Created StatsCalculator utility calculating AC, attack bonuses, damage with ability modifiers
Integrated calculations into character overlay preserving existing layout
**Result:** Character sheet now displays professional combat statistics (AC: 15, Attacks: 2, Weapon: 1d8+2) with industry-standard calculations. System handles finesse weapons, armor types, level progression, and item bonuses through pure JSON configuration.
**Files:** utils/stats_calculator.py, enhanced data/items.json, enhanced data/player/character_classes.json, modified character_overlay.py

# ADR-091: Added debug overlay
# Status: Accepted
# Date: September 27, 2025
- Updated debug Manager to include the green F1 overlay.
- can now add key info for troubleshooting.

# ADR-092: Setup for quest refactor
# Status: Accepted
# Date: September 27, 2025
-modified the jsons dialogue to setup for all json support.
- next step is to remove all hardcoded quest flags.

# ADR-093: Quest System Restructuring & Pagination Implementation
# Status: Implemented
# Date: September 27, 2025
**Context:** Main story quest cluttered with 12 objectives including granular detailed intelligence gathering. Quest overlay lacked pagination for multiple quests. 
Decision: Split main story into focused core progression and separate intelligence gathering quest. Implement pagination system for quest overlay using existing BaseTabbedOverlay patterns.
Implementation: Moved detailed intel objectives from main_story to new intelligence_gathering quest, Added quest pagination with UP/DOWN + P/N navigation (5 quests per page), Fixed text wrapping using existing wrap_text utility from constants.py, Added quest triggers for intelligence gathering with individual XP rewards
Updated dialogue_state_mapping to support post-intelligence gathering states
**Technical Details:**
Individual quest triggers require "dialogue_flag" field (unlike grouped recruitment triggers)
Quest pagination follows shopping overlay pattern with per-tab page tracking
Text rendering optimized with smaller fonts and professional wrap_text function
**Result:** Clean 9-objective main story quest, separate 3-objective intelligence quest, scalable quest UI with pagination, proper XP rewards for both discovery types. Quest system now handles unlimited quest growth through pagination.
**Files Modified:** narrative_schema.json, quest_overlay.py, dialogue files
Architecture: Maintains schema-driven quest design while improving UX and separating concerns between core story progression and optional detailed investigation.

# ADR-094: Combat Data Layer Foundation Implementation
# Status: Implemented
# Date: September 28, 2025
**Context:** Game needed tactical combat system with professional data management for enemies, encounters, and battlefields.
**Decision:** Implemented three-layer JSON architecture with coordinate arrays, full D&D stats, and modular encounter composition using CombatDataLoader utility.
**Implementation:**Created utils/combat_loader.py with validation and caching, Established data/combat/ structure: enemies/, encounters/, battlefields/, Used [x,y] coordinate arrays and disambiguated field names (attack_type, movement_type)
Built combat instance creation with unique enemy IDs and state tracking
**Consequences:**
**Positive:** Content creators can build encounters with zero code changes; enemy templates reusable across multiple encounters; professional validation prevents malformed data
**Foundation:** Ready for game_logic/combat_engine.py business logic layer and ui/combat_system.py tactical interface
Files Created: utils/combat_loader.py, data/combat/ structure with giant_rat.json, tavern_basement_rats.json, small_cellar.json
# ADR-095 Combat System Event Integration
# Date: September 28, 2025
# Status: Implemented
**Problem** Combat system UI was generating events but had no listeners - buttons clicked but nothing happened. Multiple event registration systems were conflicting, causing 0 listeners for core combat actions.
Root Causes Identified Event Name Mismatch: UI emitted MOVE/ATTACK/END_TURN but handlers expected COMBAT_MOVE_UNIT/COMBAT_ATTACK_TARGET
BaseLocation System Incomplete: Screen registration used unimplemented BaseLocation architecture
Duplicate Registration: Two separate event registration functions conflicted
**Solution Implemented** Event Handler Integration, Decision: Use single event registration in combat_engine.py init() method
python# Register combat events; Event Name Alignment-Decision: Align event handlers with actual UI emissions; Method Name Resolution
Decision: Use existing CombatEngine methods
**Architecture Benefits** Clean Event Flow: UI → EventManager → CombatEngine business logic
Proper Separation: UI handles presentation, CombatEngine handles game rules
Existing Method Reuse: Leveraged comprehensive CombatEngine methods
**Integration:** Follows established SaveManager event registration pattern
**Future Considerations** Duplicate Listeners: Currently shows "2 listeners" - investigate and resolve
Visual Feedback: Add movement/attack range highlighting
Enemy AI: Implement automatic enemy turns after player END_TURN
Victory Conditions: Wire existing victory detection to screen transitions

# ADR-096 A: HP System Split (Current vs Maximum)
# Date: September 29, 2025
# Status: Implemented (Untested)
**Context:** Combat system requires tracking damage separately from maximum HP; original hit_points field served dual purpose causing conflicts. **Decision:** Added current_hp field to track combat damage while hit_points remains maximum HP; minimal breaking changes by preserving existing field names.
**Files Modified:** game_state.py, character_engine.py, character_overlay.py, combat_system.py, combat_engine.py, save_manager.py
Implementation: current_hp initialized on character creation, synced during level-ups, modified during combat; migration logic added for old saves; display format changed to "X/Y" pattern.
**Consequences:** Combat can now track damage without losing max HP; old saves auto-migrate; HP displays show current/max split; requires actual combat testing to verify damage application works correctly.
Technical Debt Eliminated: Removed dual-purpose hit_points confusion; added proper save migration for backward compatibility.

# ADR-096 B: Combat Movement & Targeting System
# Date: September 29, 2025
# Status: Implemented
**Context:** Combat required visual feedback for valid movement and attack targeting; needed to prevent action mode persistence after actions completed; required single source of truth for movement range calculations.
**Decision:** Implemented colored border overlays (green=movement, red=attack) triggered by action buttons; centralized movement range in _get_movement_range() method; action mode clears after successful move/attack to prevent stale UI state.
Files Modified: combat_engine.py (_get_highlighted_tiles, _get_movement_range, execute_player_move, execute_player_attack), combat_system.py (_render_tile_overlays), game_state.py (combat_data structure)
**Implementation:** MOVE button sets mode, calculates valid tiles, renders green borders; click executes move, clears mode; ATTACK button shows red borders on enemy positions; both use shared tile calculation preventing misalignment.
Technical Debt Addressed: Eliminated dual hardcoded movement range values; prevented green/red overlay persistence bug; established pattern for future action types (spells, items).


# ADR-097: Enemy Multi-Attack System (Deferred)
# Date: September 29, 2025
**Status:** Deferred to Session 7
**Context:** During combat implementation discovered enemy attack design requires clarification: does attacks array represent attack count, attack options, or specific multi-attack sequences?
**Decision:** Defer complex attack logic to Session 7 (Character Abilities & Spell Integration); implement simple system now where array length = number of identical attacks using first attack definition.
**Rationale:** Same session handling player spell choices and action economy should handle enemy attack variety and AI selection logic; premature optimization before basic combat flow complete.
**Current Implementation:** Enemy attacks all use first attack in array; multi-attack = repeat same attack multiple times; no weapon selection or range-based choice.
Future Enhancement (Session 7): Add multiattack definitions, attack selection AI (melee vs ranged), special attack conditions, weapon switching logic.

# ADR-098: Combat Button State Management
# Date: September 29, 2025
# Status: Implemented
**Context:** Action buttons remained active after player exhausted actions; attack button showed even when no enemies in range; needed visual feedback for action availability.
**Decision:** Button states reflect player action state (has_moved, attacks_used) and tactical situation (enemies in range); buttons gray out when unavailable; attack counter increments on hit or miss following D&D rules.
**Files Modified:** combat_engine.py (get_combat_data_for_ui, execute_player_attack, _get_attacks_per_round), combat_system.py (_render_combat_ui_panel button state logic)
**Implementation:** Combat engine returns player_state dict with action flags and attack availability; UI checks both action limits and valid targets; MOVE grays after moving, ATTACK grays when attacks exhausted or no targets in range.
Consequences: Players receive immediate visual feedback on available actions; prevents clicking disabled buttons; supports multi-attack characters properly; attack attempts count regardless of hit/miss result.

# ADR-099 Combat Victory Quest Flag Integration
# Date: September 29, 2025
# Status: Implemented
Context: Combat victory awarded XP/gold but quest flags weren't propagating to game systems; narrative schema and dialogue system check direct attributes on game_state, but combat was setting flags in quest_flags dictionary causing architecture mismatch.
Decision: Set quest flags as direct attributes on game_state using setattr() to match existing dialogue/narrative schema architecture; abandoned quest_flags dictionary pattern in favor of direct attribute access used throughout codebase.
Files Modified: combat_engine.py (_handle_combat_victory method)
Implementation: Victory reads quest_flags from encounter JSON rewards.story_progress.quest_flags, iterates through flags using setattr() to create direct attributes on game_state; added display name lookup for user-friendly combat log messages.
Consequences: Quest flags now propagate correctly to dialogue system, narrative schema, and debug output; Garrick recognizes completed basement combat and pays player; single consistent storage pattern across all game systems; future encounters automatically integrate with quest system.
Technical Debt Eliminated: Removed competing storage locations (quest_flags dict vs direct attributes); unified flag access pattern across dialogue, combat, and debug systems.

# ADR-100: Combat Death System with Autosave and Recovery
# Date: September 30, 2025
# Status: Implemented
**Context:** Combat needed player death handling with save/restore options and visual feedback.
**Decision:** Implemented three-component death system: autosave on combat entry, death overlay with recovery options, and random death quotes for atmosphere.
**Implementation:**
- Autosave (slot 0) created at tavern before combat using `previous_screen` tracking
- Death overlay displays "YOU DIED", character name, random literary quote, and three buttons
- Buttons: Load Game (opens load overlay), Restart Combat (reloads autosave + auto-restarts combat), Return to Title
- Quote system loads from `data/narrative/death_quotes.json` (20 quotes) at moment of death
- Combat state cleanup prevents mid-combat resume on restart
**Files Modified:** 
`combat_engine.py` (autosave, death detection, quote generation, cleanup), 
`screen_manager.py` (death overlay rendering, clickable registration), 
`save_manager.py` (pending_combat_encounter flag persistence)
**Files Created:** 
`ui/death_overlay.py`, 
`data/narrative/death_quotes.json`
**Consequences:** Players can recover from death without losing progress; restart returns to fresh combat at spawn; literary quotes add atmosphere; autosave system prevents frustration.
**Technical Notes:** Quote generated once per death in combat_engine, stored in game_state; overlay renders from stored quote to prevent cycling; high-priority clickables (200) override combat grid clicks.

# ADR-101: Simplify Party Building Quest Completion Logic
# Date: October 1, 2025
# Status: Accepted (Supersedes ADR-071)
**Context:** Party building quest used `party_ready` objective that was removed from narrative schema, causing quest to never complete despite having 3/4 recruits.
**Decision:** Replace `party_ready` check with simple count-based completion: quest completes when any 3+ recruitment objectives are done.
**Implementation:** Modified `Quest._check_quest_completion()` in `quest_system.py` to count completed objectives instead of checking for non-existent `party_ready` flag.**Technical Changes:** Changed from `if party_ready_obj and party_ready_obj.completed` to `if completed_count >= 3` in party_building special case.
**Consequences:** Self-contained logic with no schema changes, no flag triggers, backward compatible with old saves, works with current 3-slot party design.
**Files Modified:** `utils/quest_system.py`
**Reverses:** ADR-071 party_ready objective pattern

ADR-102 A: Fix Quest Objective Condition Evaluation for List-Wrapped Conditions
# Date: October 1, 2025
# Status: Accepted
**Context:** Quest objective `recruit_party` defined as `["recruited_count >= 1"]` (list) was never completing because code only evaluated conditions when type was string, not list containing condition string.
**Decision:** Enhanced objective checking logic to detect single-item lists containing condition operators (>=, <=, etc.) and evaluate them as conditions rather than flag names.
**Implementation:** Modified `QuestManager.update_from_game_state()` to check if list has one item with ">=" operator, then pass to `_evaluate_condition()` method instead of treating as flag name.
**Technical Changes:** Added conditional branch: `if len(required_flags) == 1 and ">=" in required_flags[0]` before standard flag checking logic.
**Result:** Quest objectives with computed conditions (recruited_count, party_size, etc.) now work correctly whether defined as string or single-item list, maintaining schema consistency.
**Files Modified:** `utils/quest_system.py`

ADR-102 B: Load Screen Clickable Registration Bug Fix
# Status: Accepted
# Date: October 1, 2025
**Context:** 
Quest overlay clicks were failing when many quests were loaded. Investigation revealed load screen clickables were being registered to the current background screen ('broken_blade_main') instead of to 'load_overlay', causing clickable pollution. Each time the load screen opened, it added another set of clickables to the background screen, accumulating 519+ clickables that intercepted overlay clicks.
**Problem:**
- `register_load_screen_clickables()` used `current_screen` variable to register clickables
- Clickables accumulated on background screens and were never cleared
- Quest overlay clicks fell through to background screen load clickables
- Issue only manifested with large quest lists (more clickable overlap)
**Decision:**
Fixed `register_load_screen_clickables()` in `screen_manager.py` to:
1. Use fixed screen key `'load_overlay'` instead of `current_screen`
2. Clear old clickables before registering new ones
3. Applied same fix to `register_save_screen_clickables()`

# ADR-102 C: Font & Image Loading System Refactor
# Status: Accepted
# Date: October 1, 2025
**Context:** 
Font and image loading systems contained duplicate code, magic numbers, and inconsistent error handling. Changing font files or image dimensions required editing code in multiple locations. Missing assets had inconsistent fallback behavior across different asset types.
**Decision:** 
Implemented professional asset loading architecture with centralized configuration, reusable helper functions, and consistent error handling following DRY principles.
**Implementation:**
**Font System Refactor:**
- Added centralized font configuration constants: `GAME_FONT_FILE`, `GAME_FONT_NAME`, and size constants (`FONT_SIZE_LARGE`, `FONT_SIZE_MEDIUM`, etc.)
- Created `_create_font()` helper function for consistent font loading with fallback support
- Refactored `load_fonts()` to eliminate duplicate code between success and fallback paths
- Enhanced error handling with specific exceptions (FileNotFoundError) instead of bare except blocks
- Fixed `get_scaled_font()` to use centralized font configuration
**Image System Refactor:**
- Added image dimension constants: `IMAGE_STANDARD_WIDTH`, `IMAGE_STANDARD_HEIGHT`, `IMAGE_CHARACTER_TABLE_WIDTH`, etc.
- Created `_load_single_image()` helper function for consistent image loading with error handling
- Created `_create_placeholder_image()` helper function for professional missing asset visualization
- Refactored `load_images()` to use helper functions, eliminating 100+ lines of duplicate try/except blocks
- Simplified image definitions to use filenames instead of full paths in dictionaries
**Constants Consolidation:**
- Moved party display constants (`PARTY_PANEL_WIDTH`, `PORTRAIT_SIZE`, etc.) from `party_display.py` to `constants.py`
- Established pattern: configuration data in `constants.py`, behavior logic in feature modules
- Fixed duplicate color definition: `BRIGHT_GREEN` now aliases `GREEN` instead of duplicating value
**Consequences:**
**Positive:**
- Single-point font swapping: Change one constant to swap fonts across entire game
- Single-point dimension control: Change image sizes in one location
- 60% code reduction in asset loading (200+ lines → ~80 lines)
- Consistent professional placeholders for missing assets
- Improved error messages with specific file paths and clear descriptions
- Easy asset pipeline expansion: add new images by adding one dictionary entry
- Follows industry-standard separation of concerns (data vs. logic)
**Technical Benefits:**
- DRY principle applied: one helper function instead of repeated try/except blocks
- Single Responsibility: each helper does one thing well
- Better debugging: specific exceptions provide clear error information
- Maintainability: future developers can understand asset loading at a glance
**Pattern Established:**
- Configuration constants at top of file for easy adjustment
- Helper functions (prefixed with `_`) for reusable operations
- Feature modules import constants but don't duplicate them
- Clear separation: `constants.py` = data, feature modules = behavior
**Files Modified:** 
- `utils/constants.py` (font/image loading refactor, added configuration constants)
- `utils/party_display.py` (removed duplicate constants, added imports from constants.py)
**Related ADRs:** 
This refactor establishes patterns that should be applied to future asset loading systems (audio, animations, etc.)

# ADR-103: Text Wrapping Consolidation & Data-Driven Combat Messages
# Date: October 1, 2025
# Status: Implemented
**Context:** Two duplicate `wrap_text()` implementations existed (constants.py and dialogue_ui_utils.py) with different hardcoded colors and slightly different algorithms; combat quest messages were hardcoded in combat_engine.py preventing data-driven content creation.
**Decision:** Consolidated into single optimized `wrap_text()` in constants.py with flexible color parameter; moved combat quest flag display messages into encounter JSON files for data-driven architecture.
**Implementation:** Merged best practices from both implementations (list-based efficiency + explicit long-word handling); added color parameter defaulting to WHITE; dialogue_ui_utils.py now wraps constants version with DIALOGUE_TEXT_COLOR; encounter JSON quest_flags changed from `"flag": true` to `"flag": {"value": true, "display_message": "text"}` format; combat_engine reads display messages from JSON instead of hardcoded dictionary.
**Files Modified:** constants.py (optimized wrap_text function), dialogue_ui_utils.py (wrapper function), combat_system.py (combat log wrapping), tavern_basement_rats.json (data-driven messages), combat_engine.py (removed hardcoded display names).
**Consequences:** Single source of truth for text wrapping eliminates code duplication; flexible color parameter allows any UI context (combat=WHITE, dialogue=custom); content designers can add encounters with custom quest messages without touching Python; combat log properly wraps long messages; backward compatible with legacy boolean flag format.
**Technical Benefits:** Eliminated duplicate code; optimized algorithm handles edge cases; professional data-driven content pipeline; fully backward compatible; follows established architectural patterns.

# ADR-104: Multi-Party Tactical Combat System
# Date: October 1, 2025
# Status: Implemented
**Context:** Combat system only supported single player character; needed full party (player + recruited NPCs) with initiative-based turn order for tactical depth.
**Decision:** Implemented DEX-based initiative system with character_states dict tracking individual party member positions/actions; interleaved player/enemy turn order; CYAN visual highlighting for active character.
**Implementation:** 
- Replaced single player_position with character_states dict keyed by character_id
- Added _get_active_party_members() loading player + party_member_data from game_state
- Initiative calculation: DEX + d20 roll, sorted descending for turn_order list
- Active character tracked via active_character_id, automatically advanced through turn_order
- Enemy AI updated to target nearest living party member for movement/attacks
- UI renders all party members with CYAN highlight border for active character
- Encounter JSON requires 4 starting_positions for full party placement
**Files Modified:** combat_engine.py (character state tracking, initiative, turn management), combat_system.py (_render_battlefield_units with multi-character support, UI panel shows active character), tavern_basement_rats.json (4 starting positions)
**Consequences:** 
- Positive: Full party combat with proper initiative order; tactical positioning matters; enemies intelligently target nearest threats; clear visual feedback on active character
- Technical: Each party member has independent action tracking; stats_calculator integration ready for party member abilities
- Foundation: Ready for spell system (mages/clerics), ranged attacks (rogues), and class-specific abilities
**Future Enhancements:** Party member spell casting, ranged weapon attacks, formation strategies, character-specific equipment effects in combat

# ADR-105: Multi-Party Combat Bug Fixes & Collision Detection
# Date: October 2, 2025
# Status: Implemented
**Context:** Multi-party combat system (ADR-104) had critical bugs: turn display showed wrong character names, collision detection missing causing unit overlap, initiative messaging not appearing in combat log, enemy turns executing twice causing skipped player turns.
**Decision:** Fixed turn sequence logic, implemented unit collision detection, corrected character name display from active character state rather than generic current_actor.
**Implementation:** 
- Fixed _get_current_actor_name() to read active_character_id instead of always returning main player name
- Removed duplicate _advance_turn() call after first enemy turn preventing double-execution
- Added _is_tile_occupied(x, y) checking both party and enemy positions
- Integrated collision check into get_valid_moves() and _is_tile_walkable()
- Fixed method signature conflicts (tuple vs separate arguments)
- Moved initiative messages after COMBAT_STARTED event emission
- Updated combat header to display active character from character_states dict
**Files Modified:** combat_engine.py (_get_current_actor_name, _is_tile_occupied, get_valid_moves, start_encounter turn logic), combat_system.py (_render_combat_header dynamic character display, _render_combat_ui_panel removed "Active:" prefix)
**Consequences:** 
- Positive: Turn display accurately shows current actor; units cannot overlap; combat flow smooth with proper turn sequencing; collision creates tactical positioning decisions
- Bug fixes: Eliminated turn skipping, double-execution, stale character names from old saves
- User experience: Clear visual feedback on whose turn it is; tactical depth from blocking/positioning
**Remaining issues:** Enemy attack logic needs review (sometimes fails to attack when adjacent); UI polish needed (spacing, enemy turn visual indicators, and more)

# ADR-106: Fixed enemy attack bug and pulled correct npc hp and ac
# Date: October 2, 2025
# Status: Implemented
**Context:** enemy attacks showed npc was using player hp, ac was also wrong for npc
**Decision:** aligned hp and ac to json file and put in gamestate.  fixed save and load files with npc data
**Implementation:** 
- ✅ Fixed npc using wrong ac an hp
- ✅ Implemented proper NPC HP/AC from JSON files
- ✅ Added party_member_data to save/load system
- ✅ Verified damage persistence across save/load cycles
- ✅ Elara now has proper wizard stats (18 HP, 12 AC)

# ADR-107 Ranged Targeting & Mode Reset
# Status: Accepted.
# Date: 2025-10-02.
**Context:** Ranged attacks existed but highlights and clicks failed due to missing UI wiring and permissive defaults.
**Problem:** Entering ranged mode didn’t highlight valid targets and non-ranged actors inherited ranged mode.
**Decision:** Route grid clicks in ranged_attack to execute_player_ranged_attack, add ranged branch in _get_highlighted_tiles, and reset action mode on actor change.
**Alternatives:** Keep per-mode logic in UI; compute highlights client-side; defer LOS to later—all rejected for duplication and drift risk.
**Consequences:** Single-source targeting (get_attack_targets) governs range/LOS; actors without ranged weapons show no cyan tiles; UX is consistent per turn.
**Implementation:** Add UI branch for "ranged_attack", engine highlight branch using get_attack_targets(..., requires_los=True), guard with has_ranged_weapon, and call _reset_action_mode_for_active() in start_combat() and _advance_turn().
**Verification:** Manual test shows cyan highlights only for ranged actors, valid shots resolve, blocked LOS removes highlights; unit tests cover edge-of-range, blocked LOS, and mode reset.

# ADR-108 Ranged Cover & LOS Refinement
# Accepted
# Date: 2025-10-03
Context: Ranged highlights ignored soft cover and inconsistently treated blockers (pillars vs barrels vs creatures).
Problem: Players could target through sight-blocking terrain or received universal half cover due to coarse sampling and obstacle conflation.
Decision: Centralize cover in CombatEngine using float supercover rays (center+corners), hard blockers from blocks_sight, soft cover from provides_cover, optional creatures-as-cover, and expose highlighted_targets with cover.
Alternatives: Compute cover in UI; rely solely on LOS; tile-adjacent sampling; discard soft cover—rejected for drift, opacity, and poor UX.
Consequences: Solid cyan = no cover; dotted cyan = half/¾ cover; no highlight = full cover; AC is adjusted (+2/+5) during resolution; controller remains logic-free.
Implementation: Add _get_obstacle_at, _is_terrain_blocker, _tile_soft_cover, _cell_has_creature, _line_cells_supercover_f, refactor _compute_cover(origin, target, *, creatures_grant_cover=False), extend get_attack_targets(..., include_cover=True), enrich get_combat_data_for_ui() with highlighted_targets, and apply cover AC bump in execute_player_ranged_attack.
Validation: Visual cases (open/peek/full behind pillar), barrels with provides_cover, optional creatures-as-cover, and unit tests for edge-of-range and corner-graze tolerance.
Risks: Performance on large maps (mitigated by caching); data inconsistency if blocks_sight/provides_cover aren’t set correctly.
Follow-ups: Optional LOS hover line, per-source cover logging, precomputed terrain index, and rules toggle for creatures granting cover.

# ADR-109: Combat System Bug Fixes - Equipment Sync & Death Mechanics
# Status: Accepted
# Date: 2025-10-04
**Context:* Ranged attacks failed for player; NPCs took turns while unconscious; player treated as unconscious instead of dead; equipment stored in multiple conflicting locations.
**Decision:** Unified equipment storage in game_state.character['equipped_*']; fixed player instant-death vs NPC unconscious logic; added unconscious actor skip in turn advancement; stabilize unconscious NPCs to 1 HP on victory; removed duplicate _can_use_ranged_attack() string check; fixed HP roll calculation with CON floor and minimum average; removed erroneous @staticmethod decorator from _roll_hit_point_gain().
**Consequences:** Player ranged attacks functional; equipment persists through save/load/combat; player death triggers defeat overlay; unconscious NPCs skip turns and stabilize at 1 HP post-combat; HP rolls guarantee minimum average with non-negative CON modifier; party members show HP/AC/weapon/status in two-column layout.
**Files Modified:** combat_engine.py, game_state.py, stats_calculator.py, character_overlay.py, save_manager.py, character_engine.py
**Validation:** Player shortbow works in combat; Lyra unconscious at 0 HP restored to 1 HP after victory; player death shows death overlay; turn advancement skips dead actors.

# ADR-110: Unified Overlay State Management System
# Status: Accepted
# Date: 2025-10-04
**Context:** Save/load overlays used separate boolean flags while other overlays used OverlayState, causing dual state tracking and preventing proper overlay exclusivity.
**Decision:** Migrate all overlays (I/Q/C/H/F7/F10) to use centralized OverlayState system exclusively.
**Changes:**game_state.py: Removed toggle methods (toggle_inventory, toggle_quest_log, toggle_character_sheet, toggle_help) and old flag initialization; added OverlayState initialization in init
screen_manager.py: Rewrote _render_overlays() to check OverlayState.get_active_overlay() instead of individual boolean flags; updated _handle_load_game() and _handle_save_game() to use overlay_state.open_overlay(); added register_save_screen_clickables() call after rendering
input_handler.py: Added _get_active_overlay_screen() helper; added overlay clickable priority check in process_mouse_click(); removed legacy boolean flag fallback from _handle_escape_key()
constants.py: Removed ALL_OVERLAY_ATTRIBUTES list; updated MAIN_MENU_ALLOWED_OVERLAYS to use overlay_id 'load_game' instead of flag name
save_manager.py: Updated all event handlers (_handle_load_cancel, _handle_load_confirm, _handle_save_cancel, _handle_save_confirm, _handle_save_and_quit_confirm) to close overlay via overlay_state.close_overlay() instead of setting boolean flags; updated can_save_load() to check overlay_state.has_any_overlay_open()
**Consequences:** Single source of truth for overlay state; automatic enforcement of single-overlay behavior; F7/F10 now properly close other overlays when opened; ESC key works uniformly across all overlays; cleaner architecture with ~50 lines of code removed.

# ADR-110: Eliminated trinkets.json - Single Source of Truth for Trinket System
# Status: Accepted
# Date: October 4, 2025
**Context:** Character creation used separate trinkets.json requiring manual sync with items.json, causing maintenance overhead and potential data inconsistencies.
**Decision:** Query items.json directly for all items with subcategory='trinket' instead of maintaining separate trinket list file.
Implementation: Fixed ItemManager dependency injection in CharacterEngine initialization (game_controller.py, data_manager.py, character_engine.py); modified roll_trinket() to query ItemManager.items_data directly; deleted obsolete data/player/trinkets.json file.
Consequences: Adding new trinkets now requires only updating items.json - no separate sync needed; reduced maintenance overhead; proper dependency injection established for all engines; Single Source of Truth pattern enforced.
Files Modified: game_controller.py, data_manager.py, character_engine.py | Files Deleted: data/player/trinkets.json

# ADR-111: Inventory Business Logic Refactored to InventoryEngine - Professional Architecture Achieved
# Status: Accepted
# Date: October 4, 2025
**Context:** GameState contained inventory business logic (equip/unequip/consume/discard) violating Single Data Authority pattern; InventoryEngine event handlers called GameState methods instead of containing logic themselves.
**Decision:** Move all inventory business logic from GameState into InventoryEngine; GameState retains only data storage and simple getters; InventoryEngine validates operations and includes trinket discard protection.
**Implementation:** Added equip_item(), unequip_item(), consume_item(), discard_item() methods to InventoryEngine with full validation; removed duplicate methods from GameState; fixed _get_inventory_category_key() bug (was adding 's' to already-plural categories); added _find_item_id_by_name() for display name to ID conversion; trinket protection implemented via subcategory check in discard_item().
**Consequences:** Clean architectural separation achieved - UI → EventManager → InventoryEngine → GameState data; trinkets cannot be discarded (blocked with user feedback); proper dependency injection throughout inventory system; future inventory features centralized in single engine; eliminates technical debt from ADR-043.
**Files Modified:** game_logic/inventory_engine.py (added 4 business logic methods, fixed category mapping), game_state.py (removed 4 business logic methods)

# ADR-112: Fixed Button Click Region Mismatch in ActionHubLocation
# Date: Oct 4, 2025
# Status: Resolved
**Context:** Basement button appeared after accepting quest but click regions overlapped with other buttons
**Decision:** Removed duplicate action filtering from register_with_input_handler(); render() method already filters based on requirements
Implementation: Registration now trusts button_rects from render() instead of re-filtering actions with potentially different game_state
Consequence: Click regions perfectly match visual buttons; conditional buttons work correctly; eliminated state synchronization bug
Files Modified: ui/base_location.py (register_with_input_handler method)

# ADR-113: Star Animation and Expanded Save Slots
# Date: October 4, 2025
# Status: Implemented
**Context:**  Main menu needed atmospheric visual effects; players requested more save slots for character experimentation.
**Decision:**  Added twinkling star sprite animations to main menu; expanded manual save slots from 3 to 5.
**Implementation:** Updated TITLE_ANIMATIONS constant with star_twinkle path; added star initialization and rendering to draw_main_menu(); updated slots_to_check lists in save_manager.py, load_game.py, and save_game.py to include slots 4 and 5.
**Technical Details:** Stars use SpriteAnimation class with 13 frames at 32x32 pixels; varied timing (100ms, 120ms, 80ms) for organic effect; positioned at (100,50) and (900,50) for top corners.
**Files Modified:** constants.py, title_menu.py, save_manager.py, load_game.py, save_game.py.
Result: Main menu enhanced with subtle twinkling effect; save system now supports 5 manual slots plus quick save and auto-save.

# ADR-114: New Statistics Overlay screen with game stats
# Date: October 5, 2025
# Status: Implemented
**Context:**  New statistics overlay that grabs data across the program for game stats
**Decision:**  player statistics on an overlay to inform the player on game activity
**Implementation:** Added new overlay using 's' key to display 3 tabs of player, combat and other statistics
**Technical Details:** Needed to add several items to various screens. update gamestate --init-- with tracking
**Files Modified:** character_engine.py, combat_engine.py, dialogue_engine.py, dice_game_eninge.py, inventory_engine.py, save_manager.py, screen_manager.py, game_state.py, input_handler.py
New file: statistics_overlay.py
**Result:** cools stats tracking!

# ADR-115: New Statistics Overlay screen with game stats
# Date: October 5, 2025
# Status: Implemented
**Context:**  Needed a way to convey XP gain to player
**Decision:**  Created an onscreen floating text notification so player is aware action triggered xp earn
**Implementation:** added ui/notifications.py to draw the message through the character engine trigger when xp is awarded 
**Files Modified:** character_engine.py, screen_manager.py, game_controller.py
New file: notifications.py
**Result:** cool notification!  Consider using for other info

# ADR-112: BaseLocation Auto-Registration System
# Status: Implemented
# Date: October 5, 2025
**Context:** Adding new areas to location JSON files required manual screen registration in screen_manager.py, violating the zero-code content creation goal of the BaseLocation architecture.
**Decision:** Implement automatic area discovery and registration - LocationManager scans location JSON files for all areas and ScreenManager auto-registers each as a screen on startup.
**Implementation:**Added get_all_area_ids() method to LocationManager (15 lines)
Added _auto_register_location() method to ScreenManager (25 lines)
Replaced manual registration calls with self._auto_register_location("location_id")
**Technical Changes:**
LocationManager parses JSON to extract all area IDs from location data
ScreenManager iterates through areas and calls _register_base_location_screen() for each
Console logging shows auto-registered screens for debugging
**Consequences:**
Positive: Adding new areas to location JSON now requires zero code changes - areas automatically register as screens on game startup
Content Velocity: basement_cleared area added with zero code, only JSON edits
Retroactive: Fully backward compatible - existing broken_blade_main and patron_selection_main continue working
Foundation: Enables pure JSON dungeon creation with multiple explorable areas
**Files Modified:** utils/location_loader.py, ui/screen_manager.py
Example: Adding 5 areas to hill_ruins.json automatically creates 5 navigable screens without touching Python code.

# ADR-116: Map-Driven Spawn Point Architecture
# Date: October 6, 2025
# Status: Implemented
**Context:** Town spawn positions were hardcoded in game_state.py, creating dual maintenance burden and violating data-driven architecture when map files already defined spawn points.
**Decision:** Removed spawn position initialization from GameState. Each map screen handler initializes player position from its own map file constants on first entry using existing `update_player_position()` pattern.
**Implementation:** 
- Deleted initialization from game_state.py 
- Map files define spawn constants
- Screen handlers check `hasattr(game_state, 'map_player_x')` and initialize from map constants if missing
- Position initialization moved from render to update method to prevent attribute access errors
**Consequences:** 
- Positive: Each map controls its own spawn point (single source of truth); adding new maps requires zero game_state.py changes; scales to unlimited maps
- Architecture: Aligns with JSON-first, data-driven philosophy; eliminates hardcoded cross-file dependencies
**Files Modified:** game_state.py (removed lines), redstone_town.py (call order fix)
**Result:** Map spawn points defined once in map files; architecture scales cleanly to world map, dungeons, and future locations without touching GameState.

# ADR-117: Race System Implementation with Cavia Player Option
# Status: Accepted
# Date: October 7, 2025
**Context**:Game narrative includes Cavia (guinea pig) race as optional player character with unique stat restrictions and dialogue options. Needed systematic race system supporting both player characters and NPCs (Thorman=Dwarf, Lyra=Drow).
**Decision:**  Implemented JSON-driven race system with portrait-based selection and stat modifiers.
**Implementation:** Race Data: Created data/player/races.json defining Human, Cavia, Dwarf, Drow with stat modifiers, abilities, and resistances
**Portrait Selection:** Extended to 6 portraits (1-5=Human, 6=Cavia) with warning screen for Cavia
Character Engine: Added _apply_race_modifiers() method applying stat caps directly to character dict (not nested stats object)
GameState Integration: Added race field to character initialization for save/load persistence
Event System: Added CAVIA_WARNING_BACK and CAVIA_WARNING_CONFIRM events
NPC Support: Race stored in individual NPC JSON files (e.g., "race": "dwarf")
**Key Files:** data/player/races.json - Race definitions
game_logic/character_engine.py - _apply_race_modifiers(), Cavia event handlers
screens/character_creation.py - draw_cavia_warning_screen(), 6-portrait grid
ui/screen_manager.py - Cavia warning clickables registration
core/game_state.py - Race field initialization
**Consequences:**Positive: Scalable race system, Cavia stat caps enforced (STR/CON max 10), race persists through save/load, Shadow Blight resistance ready for combat integration
Future Work: Display race on character sheet, implement race-specific dialogue branches, add race ability mechanics to combat system

# ADR-118: Species (Race) Dialogue Flag Integration
# Status: Accepted
# Date: Oct 9, 2025
Context: Cavia race-specific dialogue (is_cavia flag) wasn't accessible to dialogue condition evaluator, causing Henrik's special Cavia introduction to fail with "name 'is_cavia' is not defined" error.
Decision: Modified dialogue engine's context builder to dynamically include all boolean is_* flags from game_state.character dict alongside narrative schema flags.
Implementation: Added loop in get_current_dialogue_state() to scan character dict for is_ prefixed booleans and inject into evaluation context; modified _apply_race_modifiers() to set flags in character dict when set_flag() method unavailable.
Consequences: Race flags now accessible to dialogue conditions without hardcoding; Henrik correctly recognizes Cavia players with unique dialogue; system supports future race-specific dialogue for all races (Dwarf, Drow, Human).
Files Modified: game_logic/dialogue_engine.py (context building), game_logic/character_engine.py (race flag setting)

# ADR-119: Species Dialogue Recognition & Henrik Quest Integration
# Status: Accepted
# Date: Oct 9, 2025
**Context:** Cavia players weren't recognized by Henrik's species-specific dialogue due to is_cavia flags stored in character dict not being accessible to dialogue condition evaluator; portrait selection UX was inconsistent (Cavia immediately jumped to warning screen); missing side quest to direct players to Henrik after Garrick mentions him; critical JSON syntax error prevented entire dialogue_state_mapping section from loading.
**Decision:** Modified dialogue engine's get_current_dialogue_state() to dynamically inject all is_* boolean flags from character dict into evaluation context; standardized portrait selection flow so all portraits (including Cavia) highlight first then advance on Continue button; added "Seek Old Henrik" side quest triggered by garrick_mentioned_henrik flag; fixed missing closing brace in narrative_schema.json between quest_mappings and dialogue_state_mapping.
**Implementation:** Added species flag context builder loop in dialogue_engine.py; moved Cavia warning screen trigger from portrait selection handler to portrait confirm handler; created quest definition, objectives, triggers, and mappings for Henrik quest in narrative_schema.json; corrected JSON structure so dialogue_state_mapping is root-level sibling to quest_mappings.
**Consequences:** Henrik now correctly recognizes Cavia players with unique dialogue; all portrait selections follow consistent UX pattern; players receive clear quest objective to find Henrik in town square after learning about him; dialogue state system fully operational enabling all NPC-specific dialogue paths.
**Files Modified:** game_logic/dialogue_engine.py (context building), game_logic/character_engine.py (portrait flow), data/narrative_schema.json (quest + JSON structure), data/dialogues/broken_blade_garrick.json (quest flag triggers)

# ADR-120: Directional Building Entrance System
# Date: October 10, 2025
# Status: Implemented
**Context:** Town navigation allowed building entry from any direction on entrance tiles, lacking spatial awareness and intentional interaction design.
**Decision:** Implemented directional entrance requirement where players must face toward buildings to interact; visual arrow sprite indicates facing direction; interaction prompts only appear when correctly positioned.
**Implementation:** 
- Created `calculate_required_direction()` helper in base_location_navigation.py using Manhattan distance to find closest building tile from entrance position
- Modified `create_player_fallback()` to generate directional arrow sprites (red filled triangle + tail) for up/down/left/right
- Added `can_interact` flag validation in redstone_town.py checking player_direction against required_direction before allowing ENTER key
- Enhanced debug overlay with color-coded entrance status (green=correct facing, red=wrong direction)
**Consequences:** 
- Building interaction requires intentional positioning and facing, adding tactical element to navigation
- Multiple entrance tiles per building provide flexibility while maintaining directional requirement
- System scales to all future tile-based locations (ruins, swamp church, caves) using shared NavigationRenderer
- Visual arrow placeholder ready for future sprite graphics replacement
**Files Modified:** ui/base_location_navigation.py, utils/tile_graphics.py, screens/redstone_town.py
**Technical Debt Addressed:** Removed duplicate debug rendering; established pattern for directional interactions in all future navigation systems.

# ADR-121 NPC Layer System Implementation Complete
# Status: Accepted
# Date: October 10, 2025
**Context:** Game had static building-only interactions; needed dynamic NPCs with conditional spawning, proper layering, and directional interaction for immersive town exploration.
**Decision:** Implemented multi-layered NPC system with singleton NPCManager, data-driven NPC definitions in map files, conditional spawning using existing quest_manager, and proper rendering order (tiles → NPCs → player).
**Implementation:**
- Created `utils/npc_manager.py` singleton following TileGraphicsManager pattern for consistent architecture
- Added NPC spawn definitions to `data/maps/redstone_town_map.py` with positions, interaction tiles, spawn conditions, and data-driven placeholder messages
- Migrated Henrik from building entrance system to proper NPC (removed 'V' tile, now fully dynamic NPC entity)
- Implemented `draw_npcs()` and `draw_player()` separation in NavigationRenderer for correct Z-ordering
- Added NPC interaction detection with directional facing requirement in town navigation
- Enhanced movement system with turn-then-move mechanics (classic RPG: first press turns, second moves)
- Integrated conditional spawning using existing quest_manager (no duplicate quest tracking)
- Extended debug_manager with F4 hotkey for time/day cycling and NPC condition debugging
- Added full save/load support with backward compatibility for old saves
**Technical Details:** NPCManager caches definitions per location, checks spawn conditions via quest_manager and time tracking, handles position overrides; 32x32 colored dot placeholders centered on 64x64 tiles; interaction prioritizes buildings over NPCs; game state tracks npc_position_overrides, npcs_talked_today, npc_interaction_flags, time_of_day, current_day.
**Consequences:** 6 NPCs active in Redstone Town (Henrik with dialogue, others with data-driven placeholders); conditional spawning functional (merchant on market days, noble lady daytime pre-quest); foundation ready for NPC schedules, movement, AI pathfinding; turn-then-move improves UX; fully scalable to unlimited NPCs across future locations with zero code changes.
**Files Created:** `utils/npc_manager.py`
**Files Modified:** `data/maps/redstone_town_map.py`, `ui/base_location_navigation.py`, `screens/redstone_town.py`, `game_state.py`, `game_logic/save_manager.py`, `utils/debug_manager.py`, `input_handler.py`

## ADR-121A: update Cavia starting equipment and Charisma
- **Status:** Accepted
- **Date:** Oct 10,2025
- **Context:** Cavia shoudl not be able to use a longsword and shield, need to compensate for lower str and con
- **Decision:** Add shortbow and bracers to the equipment and replace longsword and shield.  reroll chrasima with a +5 modifier, min chr score 10
- **Consequences:**  made changes to character creation and character engine
-**Gaps:**  display on summary screen still shows wrong equipment (pulling from class starting equipment vs. gamestate), charisma reroll calculation wrong, is exceeding 18, needs a modifier.

## ADR-122: revised UI on character sheet
- **Status:** Accepted
- **Date:** Oct 10,2025
- **update**:  revised format on character overlay.py 

# ADR-123: Screen Naming Standardization - Remove "_main" Suffix
# Status: Accepted
# Date: October 10, 2025
**Context:** Screen naming had inconsistent "_main" suffix (broken_blade_main vs patron_selection_main) causing navigation failures and requiring hardcoded exceptions in dialogue system.
**Decision:** Standardized all location screen names to remove "_main" suffix for main areas; locations with single "main" area register as base name only (broken_blade, patron_selection).
**Implementation:** Modified _auto_register_location() to skip "_main" suffix for "main" areas; removed hardcoded exception in _handle_dialogue_ended(); updated all navigation targets across 7 files; added save file migration to fix legacy screen names.
**Consequences:** Consistent naming eliminates navigation errors; JSON navigation targets match registered screen names directly; no more special-case handling needed; save file migration preserves backward compatibility.
Files Modified: ui/screen_manager.py (registration + dialogue), data/narrative/intro_sequence.json, screens/intro_scenes.py, data/locations/broken_blade.json, data/maps/redstone_town_map.py, game_logic/save_manager.py (migration)

# ADR-124: Character Creation Constants Standardization
# Date: October 11, 2025
# Status: Accepted - Pattern for Legacy Screen
**Context:** character_creation.py had duplicate colors, functions, and hardcoded positions from being first screen coded.
**Decision:** Eliminate duplication, use constants.py and utils.graphics imports.
**Changes:**
Removed duplicate colors/functions → import from constants.py and utils.graphics
Updated colors: BRIGHT_GREEN → TITLE_GREEN, YELLOW → SOFT_YELLOW, RED → WARNING_RED
Centered buttons using BUTTON_SIZES, SPACING, SCREEN_WIDTH constants
Removed pressed parameter from draw_button() (unused)
Fixed duplicate BROWN bug → added OLIVE_BROWN
**Pattern for Future Screens:**
Import from constants/graphics - no local duplicates
Use BUTTON_SIZES['medium'] and SPACING['button_gap']
Center formula: (SCREEN_WIDTH - total_width) // 2
**Files:** character_creation.py, utils/graphics.py, constants.py
**Next:** Apply same pattern to gambling_dice.py, title_menu.py, other legacy screens.

# ADR-125: Clickable Party Portraits for Character Sheet Navigation
# Date: October 11, 2025
# Status: Accepted
**Context:** Users need quick access to character information while exploring locations.
**Decision:** Party panel portraits are clickable regions that open character sheet overlay at appropriate tab (player portrait → Player tab, NPC portraits → Party tab).
**Implementation:**party_display.py returns portrait rectangles
base_location.py registers portraits as clickables during render
input_handler.py handles PORTRAIT_CLICKED event, emits OVERLAY_TOGGLE with tab selection
**Benefits:** Intuitive UI following classic CRPG conventions (Pool of Radiance, Ultima), event-driven architecture maintains separation of concerns, no GameController changes needed.

# ADR-125A: A. Fixed Player HP Display and B. Inn rest system
# Date: October 12, 2025
# Status: Implemented
Context: Player character HP displayed incorrectly in combat UI (stuck at max HP) while combat log showed correct damage values.
Problem: Combat UI read from stale character_data copy created at combat start instead of game_state.character source of truth.
Decision: Modified _render_combat_ui_panel and _render_battlefield_units to read player HP directly from game_state.character; NPCs continue reading from party_member_data.
Implementation: Added conditional logic checking char_id == 'player' to fetch current_hp from controller.game_state.character; passed controller parameter down to _render_battlefield_units method.
Files Modified: ui/combat_system.py (_render_combat_ui_panel HP display, _render_battlefield_units signature and HP bar rendering)
Consequences: Player HP displays now sync correctly with actual damage; both status bar under sprite and Active panel show accurate HP values; enemies and NPCs already worked due to different update pattern.

# ADR-125B: Inn Rest System & Jenna Innkeeper Implementation
# Status: Accepted
# Date: October 12, 2025
# Context: Game needed rest/healing mechanics and time progression. Jenna NPC converted from shop clerk to innkeeper at Old Knob Inn.
# Decision: Implemented inn rest system using event-driven architecture with dialogue effects triggering rest, healing, time advancement, and auto-save.
**Implementation:**
Created redstone_town_jenna.json dialogue with pricing (10 gold standard, 5 gold with 14+ charisma)
Added dialogue effects: spend_gold, rest_party, advance_time in DialogueEngine
Temporary handlers in DebugManager: handle_party_rested() heals all to max HP, handle_time_advanced() advances day/time
Fixed gold deduction: uses character['gold'] not game_state.gold
Fixed HP healing: player uses hit_points for max, party uses max_hit_points
Added town position to save/load: town_player_x, town_player_y
Auto-save after rest via direct save_manager.save_game(0) call
Updated dialogue_state_mapping for Jenna: conditional routing based on jenna_gave_discount flag
**Technical Details:** Event chain: dialogue choice → spend_gold → PARTY_RESTED event → heal all → TIME_ADVANCED event → advance day → auto-save. Discount remembered via flag check in state mapping.
Consequences: Players can rest at inn for healing/time progression. System ready for migration to dedicated TimeManager/RestManager. Fully data-driven state routing via existing dialogue_state_mapping system.
Files Modified: data/dialogues/redstone_town_jenna.json, data/narrative_schema.json, game_logic/dialogue_engine.py, utils/debug_manager.py, game_logic/save_manager.py, data/maps/redstone_town_map.py

# ADR-126: Fix Duplicate Quest XP Awards, added Combat Sprite system with layered rendering
# Date: October 12, 2025
# Status: Implemented
**Context:**  Quest completion XP awarded twice: once by QuestEngine, once by CharacterEngine listening to QUEST_COMPLETED event. Also, QuestEngine's _evaluate_quest_triggers fallback sweep re-awarded XP for all previously-set flags whenever ANY new flag changed. Combat grid used solid color rectangles; needed scalable sprite system for floors and obstacles without hardcoding assets in constants.py.
**Decision:** Remove duplicate XP logic from CharacterEngine._handle_quest_completion; remove fallback sweep from QuestEngine._evaluate_quest_triggers that checked ALL flags when no trigger found for specific flag., Created CombatSpriteManager singleton following TileGraphicsManager pattern; implemented data-driven layered rendering (floor → obstacles → grid); floor type read from battlefield JSON terrain.default field.
**Implementation:** CharacterEngine now only checks for level-ups on quest completion, doesn't award XP; QuestEngine only evaluates triggers matching the specific changed flag, no fallback sweep.. utils/combat_sprite_manager.py loads 16x16 tileable floors (tiled 3×3 for 48×48 tiles) and 32×32 obstacle sprites with professional fallbacks; ui/combat_system.py uses manager for all combat graphics; floor mapping system (stone_floor→stone_floor_16x16.png) enables JSON-driven battlefield aesthetics.
**Consequences:** Single source of truth for quest XP (QuestEngine); no ghost XP spam from flag changes; CharacterEngine focuses on level-up notifications only. Zero code changes for new battlefields—just add JSON terrain type and drop PNG in assets; barrels render as pixel art sprites; stone floors tile seamlessly; support_beam shows fallback placeholder until asset created; follows established architectural patterns (singleton, separation of concerns, data-driven design).
**Files Created:** utils/combat_sprite_manager.py
**Files Modified:** game_logic/character_engine.py (_handle_quest_completion), game_logic/quest_engine.py (_evaluate_quest_triggers), ui/combat_system.py (added layered rendering, removed constants.py image dependency)

# ADR-123: Data-Driven Combat Tileset System with Auto-Tiling
# Status: Accepted
# Date: October 12, 2025
**Context:** Combat battlefields needed flexible wall/floor graphics supporting different aesthetics (cellar, dungeon, church) and any room shape (rectangular, L-shaped, corridors, complex layouts).
**Decision:** Implemented data-driven tileset system with neighbor-based auto-tiling; each battlefield JSON specifies tileset name and wall line segments; CombatSpriteManager loads 8 wall tiles (N/S/E/W + 4 corners) per tileset on-demand; auto-tiling checks 8 neighbors to select correct tile for any wall position.
**Implementation:** Battlefield JSON contains "tileset": "cellar" field; wall tiles named {tileset}_wall_north.png, {tileset}_corner_nw.png, etc.; floor type maps to 16×16 tileable textures (stone_floor→stone_floor_16x16.png); _get_wall_tile_type() uses pure neighbor checking (works ANY shape); grid lines dimmed to (60,60,60) for dungeon atmosphere.
**Consequences:** Zero code changes for new battlefields—just create 8 wall PNGs with tileset prefix and define walls array in JSON; supports unlimited room shapes (rectangles, L-shapes, corridors, mazes); each location has distinct visual identity; follows industry-standard auto-tiling; fully scalable architecture.
**Files Modified:** utils/combat_sprite_manager.py (tileset loading), ui/combat_system.py (auto-tiling logic), utils/constants.py (COMBAT_WALLS_PATH), data/combat/battlefields/small_cellar.json (tileset field)

# ADR-128 A: Dialogue Item Effects System
# Date: October 13, 2025
# Status: Implemented
**Context:** Henrik's dialogue needed to give player his lantern, but no mechanism existed for dialogue to add/remove inventory items.
**Decision:** Extended DialogueEngine._apply_dialogue_effect() to support add_item and remove_item effects; injected ItemManager reference into DialogueEngine for item validation; added floating text notifications matching XP system.
**Implementation:** Added item_manager parameter to DialogueEngine.__init__() and initialize_dialogue_engine(); created add_item and remove_item effect handlers with validation; effects support item_id, quantity, and optional category; visual feedback via SHOW_FLOATING_TEXT event (blue for received, red for lost).
**Files Modified:** dialogue_engine.py, data_manager.py, game_controller.py, redstone_town_henrik.json
**Result:** Dialogue can now give/take items with visual feedback. Henrik's quest properly awards lantern. Architecture supports future quest rewards and NPC trading.

# ADR-128 B: First-Meeting Recruitment Flow Fix
# Date: October 13, 2025
# Status: Accepted
Context: Recruitable NPCs required two visits if player talked to Mayor first - initial meeting showed generic dialogue, then player had to leave and return to see recruitment options.
Decision: Added first_meeting_post_mayor dialogue state to all four recruits (Gareth, Elara, Thorman, Lyra) that acknowledges Mayor's endorsement and offers immediate recruitment or background exploration.
Implementation:narrative_schema.json: Added first_meeting_post_mayor mapping ordered before first_meeting for all 4 recruits
All recruit dialogue JSONs: Added 3 states each (first_meeting_post_mayor, background_with_recruitment, recruitment_blocked_brief)
Maintains player choice: can recruit immediately, learn background first, or defer decision
Consequences: Seamless single-conversation recruitment flow; better narrative continuity; no forced double-visits; maintains player agency and depth options.
Files Modified: data/narrative_schema.json, data/dialogues/patron_selection_gareth.json, data/dialogues/patron_selection_elara.json, data/dialogues/patron_selection_thorman.json, data/dialogues/patron_selection_lyra.json

# ADR-129: Enemy AI Turn Planning System
# Date: 2025-01-14
# Status: Implemented
**Context:** Enemy AI called twice per turn without strategic planning; enemies couldn't coordinate move+attack like players; behavior logic duplicated across methods.
**Decision:** Refactored CombatAI to plan complete turns (move + attack) in single calculate_enemy_turn() call; behavior methods return {'move': pos, 'attack': {target_id, attack_index}} format; CombatEngine executes both actions sequentially.
**Files Modified:** combat_ai.py (calculate_enemy_turn, _calculate_rush_action, _calculate_ranged_preference_action), combat_engine.py (_execute_enemy_turn), combat_loader.py (_create_enemy_instance, _validate_encounter_data)
**Implementation:** AI evaluates entire tactical situation once, plans optimal move+attack combination; ranged_preference backs away then shoots, rush moves into melee then attacks; encounter ai_behavior optional, defaults to enemy.behavior.tactics.
**Benefits:** Enemies use full action economy matching players; strategic coordination (move to optimal position THEN attack); extensible pattern for future behaviors; single source of truth for turn planning.


# ADR-130: Enemy AI Tactical Improvements - Collision Prevention & LOS Integration
# Date: [Today's Date]
# Status: Implemented
**Context:** Shadow Ghost pathfinding onto player tiles; enemies stacking on same position; ranged enemies attacking without line of sight
**Decision:** Enhanced AI planning with collision detection, proper adjacent positioning for melee, and line-of-sight validation for ranged attacks
**Implementation:**
- Modified _find_direct_path_to_target() to stop adjacent (not on target) for melee attacks
- Added intended_position checks in _execute_enemy_move() for collision prevention
- Integrated CombatEngine._has_line_of_sight() into AI planning via combat_state
- Created _find_closest_player_with_los() for ranged target selection
- Added _handle_no_los_fallback() for intelligent repositioning when LOS blocked
- Updated ranged_preference and hit_and_run behaviors to require LOS for ranged attacks

**Consequences:**
- Positive: Realistic tactical combat with proper positioning and LOS rules; enemies reposition intelligently
- Gameplay: Terrain becomes tactically important; players can use cover; ranged enemies behave believably
- Architecture: Single source of truth for LOS (CombatEngine); AI properly delegates validation

# ADR-131: Combat UI Refinement - Inspector & Toggle Buttons
# Date: OCt 17, 2025
# Status: Implemented
Context: Combat UI needed better unit information display and clearer action mode feedback. Players couldn't inspect enemies without committing to actions.
Decision:Added clickable unit inspector panel (shows name, type, HP status)
Implemented toggle buttons with yellow border for active modes (click again to deselect)
Removed redundant Active/HP/Class display from right panel
Expanded combat log to 18 lines with system font for readability
Moved EXIT button to bottom-left, aligned with grid
Implementation:
combat_engine.py: Added inspected_unit tracking, increased combat_log payload to 20 messages
combat_system.py: Inspector panel with fixed spacing, toggle button handlers, visual state management
graphics.py: Updated draw_combat_button() with normal/active/disabled states (gray/yellow/gray borders)
constants.py: Added combat_log system font for clarity
Consequences:
Players can gather intel on enemies before committing to actions
Clearer visual feedback for which action mode is active
More combat history visible for tactical decisions
Combat log more readable during intense encounters

# ADR-132: Combat Loot Collection System
**Status:** Implemented
**Context:** Players needed rewards after combat victories - gold and items from defeated enemies
**Decision:** Created modal overlay using BaseTabbedOverlay for post-combat loot selection with checkbox UI
**Consequences:** (+) Clean loot collection flow, (+) Reuses established overlay architecture, (-) Minor tech debt: overlay accesses inventory_engine via screen_manager instead of event system
**Alternatives Considered:** Event-driven buttons like inventory overlay (deferred for v2), immediate auto-loot (rejected - removes player choice)

# ADR-133: Start implementation of spell casting system
**Status:** Accepted
**Context:** Add functionality to all for spell casting for npcs
**Decision:** created system in combat files to allow for casting spells. 
**Consequences:** Add spells.json, and updated combat_engine, combat_system, input_manager to link spell system.  partially implemented. Only cure wounds work, but only healing player. 
**Next steps :** Need to fix incomplete implementation,  apply range spell damage spells (fireball), remove technical debt.

# ADR-134: Combat Action System
# Status: Accepted
# Date: October 19, 2025
**Context:** Combat lacked mechanism for class abilities and consumable item usage beyond basic attacks/spells.
**Decision:** Implemented data-driven Action button that reads abilities from character_classes.json and items from inventory, displaying available actions based on usage limits.
**Implementation:** Added Action button to combat UI; enhanced character_classes.json with combat_action metadata; created get_available_actions() and execute_player_action() methods; made Action and Spell mutually exclusive.
**Consequences:** Abilities now add via JSON edits only; healing potions usable in combat; action economy properly enforced (Move + one offensive action per turn).
Files Modified: combat_system.py, combat_engine.py, character_classes.json, input_handler.py



```
## ADR-XXX: <Short title>
- **Status:** Proposed | Accepted | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Context:** …
- **Decision:** …
- **Consequences:** …
```

