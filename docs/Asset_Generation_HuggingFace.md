# Terror in Redstone — AI Asset Generation Guide
# Hugging Face / FLUX.1-schnell Pixel Art Workflow

---

## Setup

- **Script:** `/Users/dennis/Documents/Claude/AI-Context-System/generate_image.py`
- **Venv:** `/Users/dennis/Documents/Claude/AI-Context-System/.venv/bin/python3.12`
- **Model:** FLUX.1-schnell (free tier)
- **API token:** stored in `/Users/dennis/Documents/Claude/AI-Context-System/.env`

> **IMPORTANT:** Must be run in Terminal — Claude Code's sandbox blocks outbound
> network calls. Claude drafts the prompt and command; you paste it in Terminal.

---

## Base Command

```bash
/Users/dennis/Documents/Claude/AI-Context-System/.venv/bin/python3.12 \
  /Users/dennis/Documents/Claude/AI-Context-System/generate_image.py \
  "YOUR PROMPT HERE" \
  "output_filename.png" \
  "/path/to/save/location"
```

---

## Save Locations

| Asset Type        | Save Path                                                        |
|-------------------|------------------------------------------------------------------|
| NPC portraits     | `assets/images/icons/characters/npc_portraits/`                 |
| Object icons      | `assets/images/icons/characters/`                               |
| Terrain tiles     | `assets/images/tiles/terrain/`                                  |
| Backgrounds       | `assets/images/backgrounds/locations/`                          |
| NPC world sprites | `assets/images/sprites/npcs/`                                   |

---

## Prompt Building Blocks

### Pixelation (always include one of these)

**Standard pixelation:**
```
coarse pixel art large pixel blocks 16-color palette chunky dithering black background
```

**Heavy pixelation (use when more pixelation is needed):**
```
extremely pixelated very large visible pixel blocks heavy dithering limited 8-color palette
no smooth gradients no anti-aliasing blocky retro SNES style black background
```

### NPC Portraits
```
front-facing bust shot, 16-bit RPG NPC portrait, [pixelation block]
```

- Human NPCs: add `ordinary human, no horns no pointed ears no fantasy features`
- Avoid `dark fantasy` + `dark hair` + `scar` combinations — FLUX defaults to tiefling/demon
- Use occupation/personality as anchor: `tired innkeeper`, `weathered old miner`, `gaunt scholar`
- Distinguish faces explicitly: `round soft face`, `square jaw`, `sharp angular cheekbones`

### Object Icons
```
front-facing object view, no characters, [pixelation block]
```

- Avoid altar/shrine/temple words if you don't want arches — use `flat stone slab` instead
- Describe geometry directly for simple shapes: `horizontal rectangular stone slab`
- Add `nothing above it, empty black space above and behind` to suppress background structures

### NPC World Sprites (Tavern / Map Overlays)

```
pixel art, front-facing character, full body, [character description],
coarse pixel art large pixel blocks 16-color palette chunky dithering black background,
no text no border no ui elements
```

**IMPORTANT — Output Size Limitation:**
`generate_image.py` sends a plain JSON `{"inputs": prompt}` with no dimension
parameters. FLUX.1-schnell returns its default resolution (~1024x1024). You
**cannot** generate a correctly-sized sprite sheet directly.

**Workflow for NPC sprites:**
1. Generate a full-body reference image using the prompt below (saves at ~1024x1024)
2. Open the reference in Aseprite
3. Create a new 128x32 canvas (4 frames × 32px) or 64x32 (2 frames × 32px)
4. Hand-pixel/trace the character from the reference at the correct dimensions
5. Export as PNG sprite sheet to `assets/images/sprites/npcs/{npc_id}_idle.png`

**Sprite sheet format expected by the engine:**
- Frames arranged horizontally, each frame 32x32 px
- 4 idle frames = 128x32 px total
- 2 idle frames = 64x32 px total
- Transparent background (PNG with alpha)
- Filename: `{npc_id}_idle.png`

---

## Wiring Assets Into the Game

### NPC Portraits
Portraits are resolved automatically by `utils/npc_display.py`:
- Filename must be `{npc_id}_portrait.jpg`
- Saved to `assets/images/icons/characters/npc_portraits/`
- The `npc_id` comes from the dialogue JSON or the screen that launches dialogue
- No code change needed if the filename matches

### NPC World Sprites
NPC sprites are loaded by `utils/tile_graphics.py` and drawn in each location nav
screen (e.g. `screens/broken_blade_nav.py`).

- Filename must be `{npc_id}_idle.png`
- Save to `assets/images/sprites/npcs/`
- Sprite sheet: frames horizontal, 32x32 px each, transparent PNG
- After saving, update the nav screen to load and draw the sprite instead of the
  colored-circle placeholder (see "Wiring NPC Sprites" in code comments)

### Object Icons
Object icons are mapped in `utils/object_display.py` → `OBJECT_ICON_MAPPING`:

```python
OBJECT_ICON_MAPPING = {
    'altar':          'altar_shrine.png',
    'altar_corrupted':'altar_corrupted.png',
    'book':           'book.png',
    'chest':          'chest.png',
    'chest_angled':   'chest_angled.png',
    'door':           'door.png',
    'symbols':        'symbols.png',
    'ritual':         'ritual.png',
}
```

To add a new object type: generate the image, save to `assets/images/icons/characters/`,
then add a new entry to `OBJECT_ICON_MAPPING`.

---

## Thorman NPC Sprite — Reference Generation

**Step 1 — generate reference image in Terminal:**

```bash
/Users/dennis/Documents/Claude/AI-Context-System/.venv/bin/python3.12 \
  /Users/dennis/Documents/Claude/AI-Context-System/generate_image.py \
  "pixel art, front-facing full body character, dwarf male cleric, bald head with long braided red-orange beard, blue cleric robes with gold trim, thor hammer amulet on chest, stocky short build, blue eyes, stern expression, standing idle pose, coarse pixel art large pixel blocks 16-color palette chunky dithering black background, no text no border no ui elements" \
  "thorman_sprite_reference.png" \
  "/Users/dennis/Development/Redstone/assets/images/sprites/npcs"
```

**Step 2 — in Aseprite:**
- Open `thorman_sprite_reference.png` as reference
- New canvas: 128x32 (4 frames) or 64x32 (2 frames), transparent background
- Trace/redraw Thorman at 32x32 per frame matching his portrait style
- Export sprite sheet to `assets/images/sprites/npcs/thorman_idle.png`

**Step 3 — tell Claude:** "Thorman sprite is ready, wire it up"
- Claude will update `broken_blade_nav.py` to load and draw the sprite instead of the dot

---

## Assets Generated (May 2026)

| File | Type | Notes |
|------|------|-------|
| `npc_portraits/taborex_portrait.jpg` | NPC portrait | High Cultist villain |
| `npc_portraits/leader_portrait.jpg` | NPC portrait | Refugee camp leader (unused — resolves to marta) |
| `npc_portraits/marta_portrait.jpg` | NPC portrait | Camp leader (npc_id: marta) |
| `npc_portraits/marcus_portrait.jpg` | NPC portrait | Corrupted scholar |
| `npc_portraits/jenna_portrait.jpg` | NPC portrait | Innkeeper |
| `npc_portraits/henrik_portrait.jpg` | NPC portrait | Old miner |
| `altar_shrine.png` | Object icon | White marble healing shrine |
| `altar_corrupted.png` | Object icon | Blood-stained stone slab |
| `book.png` | Object icon | Ancient arcane tome |
| `chest.png` | Object icon | Front-facing ancient chest |
| `chest_angled.png` | Object icon | 3/4 angle ancient chest |
| `door.png` | Object icon | Iron-banded dungeon door |
| `symbols.png` | Object icon | Aethel shadow corruption runes |
| `ritual.png` | Object icon | Blood ritual circle with green flames |
| `sprites/npcs/thorman_sprite_reference.png` | NPC sprite reference | Thorman dwarf cleric — trace in Aseprite to 128x32 for final sprite |

---

## Prompt Template for Claude

When asking Claude to generate a new asset, use this as your prompt:

```
I'm working on a Python/Pygame CRPG called Terror in Redstone.

We use Hugging Face (FLUX.1-schnell) to generate pixel art assets.
See docs/Asset_Generation_HuggingFace.md for the full workflow.

ASSET NEEDED: [describe what you need — NPC portrait / object icon / tile]
CHARACTER/OBJECT CONTEXT: [paste relevant dialogue JSON description or scene context]
SAVE AS: [filename.png or filename.jpg]
SAVE TO: [which asset folder]

TASK:
1. Read the character/object description from the dialogue JSON
2. Craft a FLUX prompt using the guidelines in the asset generation doc
3. Provide the Terminal command to run
4. Once I confirm it looks good, wire it into the game (update
   object_display.py or confirm npc_id filename match)
```
