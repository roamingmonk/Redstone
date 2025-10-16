# Terror in Redstone - Known Issues & Future Work

## Combat System

### 🔴 HIGH PRIORITY: Movement Pathfinding

**Discovered:** Session with combat AI implementation  
**Severity:** Medium (affects tactical gameplay)  
**Status:** Documented, scheduled for future session

**Description:**
Movement validation checks destination tiles only, not the path to reach them. Units can "teleport" through walls if the destination is within movement range.

**Example:**
- Skeleton at [11, 3] with speed 3
- Wall obstacle at [8, 4]  
- Skeleton moves to [6, 4] by "jumping" through wall
- Should require pathing around obstacles

**Impact:**
- AI behaviors (rush, stalker, etc.) can take impossible shortcuts
- Players can potentially exploit by blocking paths
- Reduces tactical depth of terrain/obstacles

**Proposed Solution:**
Implement proper pathfinding system (Session TBD):
1. BFS/A* pathfinding to find reachable tiles
2. Step-by-step movement animation showing actual path
3. Flood-fill valid movement highlighting for players
4. Path visualization for debugging (F6 integration)

**Temporary Workaround:**
- Incorporeal movement works as intended (phases through)
- Design encounters without critical wall placements
- Current AI behaviors functional, just with "teleporting"

---

### ✅ WORKING: Enemy AI Behaviors

**Implemented and functional:**
- rush_player ✅
- ranged_preference ✅  
- hit_and_run ✅
- aggressive_rush ✅
- mindless_advance ✅
- flanking ✅
- stalker ✅ (incorporeal and walking variants)

**Note:** All AI logic works correctly, only limited by pathfinding issue above.
```

---

## 📝 **Commit Message:**

Once you've added these comments, here's your commit:
```
Docs: Document pathfinding limitation in movement system

- Added TODO comments in get_valid_moves() about destination-only checking
- Noted issue in _is_tile_walkable() documentation
- Created KNOWN_ISSUES.md to track movement pathfinding work
- Updated developer guide with workaround notes
- Movement validation checks destination walkability, not path reachability
- Scheduled proper BFS/A* pathfinding for future session with animation

All AI behaviors implemented and working (rush, ranged, hit_and_run, 
aggressive_rush, mindless_advance, flanking, stalker). Issue is with 
movement execution, not AI planning. Incorporeal movement works correctly.