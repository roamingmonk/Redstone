# Tiled Map Workflow - Complete Guide
## Creating and Updating Maps with Aseprite + Tiled

---

## INITIAL SETUP (First Time Only)

### Prerequisites
- Aseprite installed
- Tiled Map Editor installed
- Map location folder: `\Redstone\assets\images\tiles\tilesets\`

---

## PHASE 1: CREATE TILESET IN ASEPRITE

### Step 1: Design Tiles
1. Create new file in Aseprite: 32×32 pixels
2. Use Tilemap → New Tileset
3. Tile dimensions: 32×32
4. Add tiles one at a time:
   - Click "New Tile"
   - Draw tile
   - Repeat for all tiles
5. **IMPORTANT:** Note the order! Tiles are numbered left-to-right, top-to-bottom

### Step 2: Export Sprite Sheet
1. **File → Export Sprite Sheet**
2. **Sprite Tab:**
   - Source: **"Tileset"**
3. **Layout Tab:**
   - Sheet Type: By Rows
   - Columns: 7 (or your preferred width)
4. **Output Tab:**
   - File: `location_name.png` (e.g., `refugee_camp.png`)
   - JSON Data: NOT needed (we use grid slicing)
5. **Export** to: `\Redstone\assets\images\tiles\tilesets\location_name.png`
6. **Write down tile order:** 1=trees, 2=grass, 3=dirt, etc.

---

## PHASE 2: BUILD MAP IN TILED

### Step 3: Create New Map
1. **File → New → New Map**
2. **Settings:**
   - Orientation: **Orthogonal**
   - Tile layer format: **CSV** (simplest)
   - Tile size: **32 × 32 pixels**
   - Map size: Your choice (e.g., 20×20, 40×30)
   - Fixed size: ✓ (checked)

### Step 4: Import Tileset
1. **Map → New Tileset**
2. **Type:** Based on Tileset Image
3. **Source:** Browse to your PNG (e.g., `refugee_camp.png`)
4. **Name:** Match your map name (e.g., `refugee_camp`)
5. **Tile width:** 32
6. **Tile height:** 32
7. **Margin:** 0
8. **Spacing:** 0
9. **Click OK**

### Step 5: Paint Map
1. Select tiles from tileset panel (right side)
2. Use Stamp Brush (B) to paint
3. Use Fill Tool (F) for large areas
4. Zoom with mouse wheel
5. Pan with middle mouse button
6. Paint your entire map visually

### Step 6: Export Map
1. **File → Export As**
2. **Format:** JSON map files (*.json)
3. **Filename:** `location_name_map.tmj` (e.g., `refugee_camp_map.tmj`)
4. **Save to:** `\Redstone\assets\images\tiles\tilesets\`
5. **.tmj extension is correct** - don't change it!

---

## PHASE 3: CREATE PYTHON MAPPING (First Time Only)

### Step 7: Create Tile Mapping File

**Create:** `\Redstone\data\maps\location_name_tiles.py`

**Template:**
```python
# data/maps/location_name_tiles.py

LOCATION_NAME_TILE_MAP = {
    0: None,  # Empty tile
    1: 'first_tile_name',   # Match your Aseprite order!
    2: 'second_tile_name',
    3: 'third_tile_name',
    # ... continue for all tiles
}

LOCATION_NAME_WALKABLE = [
    'grass',
    'dirt',
    'path',
    # ... list all walkable tile names
]
```

**Count tiles carefully:**
- Open your PNG in image viewer
- Count left-to-right, top-to-bottom
- First tile = 1, second = 2, etc.
- **Tile order MUST match PNG layout!**

---

## PHASE 4: INTEGRATE WITH GAME (First Time Only)

### Step 8: Update Navigation Screen

**In your navigation file** (e.g., `screens/refugee_camp_main_nav.py`):

**Add to imports:**
```python
from utils.tiled_loader import (
    load_tiled_map_with_names,
    get_tile_type,
    is_walkable_tile
)
from utils.constants import TILESETS_PATH
from data.maps.location_name_tiles import (
    LOCATION_NAME_TILE_MAP,
    LOCATION_NAME_WALKABLE
)
```

**In __init__ method, BEFORE creating config:**
```python
# Load tileset and Tiled map
from utils.tile_graphics import get_tile_graphics_manager

graphics_mgr = get_tile_graphics_manager()
graphics_mgr.load_tileset_from_grid(
    'location_name',           # Your PNG name
    LOCATION_NAME_TILE_MAP,    # Your tile mapping
    tile_size=32,              # Source tile size
    columns=7                  # Tiles per row in PNG
)

# Load Tiled map
self.tilemap = load_tiled_map_with_names(
    'location_name_map',       # Your .tmj name (no extension)
    'location_name',
    LOCATION_NAME_TILE_MAP,
    TILESETS_PATH
)
```

**Update config dict:**
```python
config = {
    'tile_size': 64,  # Display size (2× scale from 32×32)
    'map_width': self.tilemap['width'],
    'map_height': self.tilemap['height'],
    'location_id': 'location_name_main_nav',
    'map_functions': {
        'get_tile_type': lambda x, y: get_tile_type(x, y, self.tilemap['tile_grid']),
        'is_walkable': lambda x, y: is_walkable_tile(
            get_tile_type(x, y, self.tilemap['tile_grid']),
            LOCATION_NAME_WALKABLE
        ),
        'get_tile_color': None,
        # ... keep other functions
    }
}
```

---

## UPDATING EXISTING MAPS (Quick Workflow)

### Scenario: Map Already Set Up, Just Need Changes

**Step 1: Edit in Tiled**
1. Open existing `.tmj` file in Tiled
2. Make your changes (add tents, move paths, etc.)
3. **File → Save** (Ctrl+S)

**Step 2: Test**
1. Run game
2. Navigate to location
3. Changes appear immediately!

**That's it!** No Python changes needed if you're using existing tiles.

---

### Scenario: Adding New Tiles to Existing Map

**Step 1: Update Aseprite Tileset**
1. Open tileset in Aseprite
2. Add new tiles (they get next available numbers)
3. Re-export sprite sheet to same filename

**Step 2: Update Tile Mapping**
1. Open `location_name_tiles.py`
2. Add new tiles to `TILE_MAP`:
   ```python
   41: 'new_tent_variant',
   42: 'new_tree_type',
   ```
3. Add to `WALKABLE` list if walkable

**Step 3: Use in Tiled**
1. Map → Refresh Tilesets (or restart Tiled)
2. New tiles appear in tileset panel
3. Paint with new tiles
4. Save

**Step 4: Test**
1. Run game
2. New tiles render correctly!

---

## TROUBLESHOOTING

### Problem: Tiles Show as Colored Blocks
**Solution:** Tile names don't match between mapping file and Tiled
- Check console for "Using fallback for: tile_name"
- Verify tile order in PNG matches TILE_MAP
- Count carefully!

### Problem: Map File Not Found
**Solution:** Check filenames and paths
- File must be in `\Redstone\assets\images\tiles\tilesets\`
- File extension: `.tmj` or `.json`
- Load call uses name WITHOUT extension

### Problem: Wrong Tiles in Wrong Places
**Solution:** Column count mismatch
- Count tiles horizontally in PNG
- Update `columns=` parameter in load call
- Should match PNG width in tiles

### Problem: Tiles Too Big/Small
**Solution:** Display size setting
- Source: 32×32 (in Aseprite)
- Display: 64×64 (in config)
- Check `tile_size` in config dict

---

## FILE CHECKLIST

After creating a new Tiled map, you should have:

```
\Redstone\
├── assets\images\tiles\tilesets\
│   ├── location_name.png              ✓ (from Aseprite)
│   └── location_name_map.tmj          ✓ (from Tiled)
│
├── data\maps\
│   └── location_name_tiles.py         ✓ (manual mapping)
│
└── screens\
    └── location_name_nav.py           ✓ (updated imports/init)
```

---

## QUICK REFERENCE

**Tile Sizes:**
- Aseprite: 32×32 (source)
- Tiled: 32×32 (matching source)
- Game Display: 64×64 (2× scaled)

**Columns:**
- 7 columns = 280px wide sprite sheet
- Adjust based on your tileset size

**File Extensions:**
- Aseprite: `.ase` (source)
- Sprite Sheet: `.png` (exported)
- Tiled Map: `.tmj` (new) or `.json` (old)
- Mapping: `.py` (Python)

---

## TIPS

✅ **Keep it organized:** One folder per location's assets
✅ **Name consistently:** refugee_camp.png, refugee_camp_map.tmj, refugee_camp_tiles.py
✅ **Test incrementally:** Export→Load→Test after each change
✅ **Document tile order:** Comment your TILE_MAP with descriptions
✅ **Use Tiled layers:** Separate ground/decorations/collision for clarity
✅ **Save often:** Both Aseprite (.ase) and Tiled (.tmj) source files

---

## ADVANTAGES

**vs. ASCII Arrays:**
- ✅ Visual editing (see what you build)
- ✅ Unlimited tile variants
- ✅ Faster iteration
- ✅ Industry standard tools

**vs. Hardcoded:**
- ✅ No code changes for map edits
- ✅ Designers can update without programming
- ✅ Easier to visualize layout

---

## WORKFLOW SUMMARY

```
CREATE TILES          DESIGN MAP          MAP TO CODE         PLAY!
    |                     |                    |                 |
Aseprite              Tiled               Python            Test Game
    ↓                     ↓                    ↓                 ↓
32×32 tiles    →    Paint layout   →    Index mapping  →   64×64 display
Export PNG          Export .tmj         Create .py        Auto-loads
```

**Initial setup:** 30-60 minutes per location
**Updates:** 30 seconds (edit in Tiled, save, test)

---

End of workflow guide. Happy mapping! 🗺️