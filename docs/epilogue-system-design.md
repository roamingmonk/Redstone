# Terror in Redstone - Epilogue System Design
## Complete Post-Victory Flow

**Version:** 2.0  
**Date:** November 17, 2025  
**Purpose:** Design comprehensive ending system matching intro/Act transition quality

**Key Design Decisions:**
- Victory screen: New screen (not overlay) with detailed stats and auto-save
- Town celebration: Reuse town_map renderer as static background (no new art!)
- Dialogue files: State-based approach using existing files (no new dialogue files!)
- Level-ups: Shown AFTER epilogue sequence, not on victory screen
- Current scope: Mayor's family rescue only (villager system for future expansion)

---

## EXISTING CINEMATIC SYSTEM (Your Foundation)

### You Already Have This Working!

**Files:**
- `screens/intro_scenes.py` - JSON-driven cinematic sequences
- `data/narrative/intro_sequence.json` - 3-scene intro narrative
- `screens/act_two_transition.py` - Act transition cinematics
- `screens/redstone_town.py` - Town map renderer with NPC sprite system

**Pattern:**
1. Load JSON with scene data
2. Atmospheric pygame-generated backgrounds (OR reuse existing renderers!)
3. Text wrapping and centering
4. Continue/Skip buttons
5. Auto-save checkpoints
6. Navigate to next screen

**This Same System Can Do Epilogues!**

---

## COMPLETE POST-VICTORY FLOW

### Phase 1: Boss Defeated
**Current Location:** Dungeon Level 5 (Portal Chamber)

**Immediate Actions:**
1. Portal collapse sequence (automatic)
2. Rescue captives (Mayor's family freed)
3. Set outcome flags based on battle

**Flags Set (Phase 1 Scope):**
- `boss_defeated = True`
- `mayor_family_rescued = True/False` (Currently implemented)
- `mayor_family_status = "all_saved"/"partial"/"none"` (Phase 1)
- `marcus_outcome = "fled"/"killed"/"ally"`
- `portal_sealed = True`

**Future Enhancement Flags:**
- `villagers_rescued_count = X` (For future multi-location rescue system)
- `church_captives_saved = X`
- `mine_workers_saved = X`

---

### Phase 2: Victory Screen with Statistics
**Screen:** `screens/victory_screen.py` (NEW - full screen, not overlay)

**Purpose:** Detailed victory statistics and immediate rewards

**Technical Decision:** New screen (not overlay) for clean state separation from combat

**Display Content:**
```
================================================================
                                          
             VICTORY!                     
     The Shadow Blight is Sealed          
                                          
================================================================
                                          
  EXPERIENCE EARNED:                      
    Base Victory Bonus: 1000 XP           
    Mayor's Family Rescued: +500 XP       
    Portal Sealed: +250 XP                
    ---------------------------------             
    TOTAL EARNED: 1750 XP                 
                                          
  SPECIAL REWARDS:                        
    * Portal Seal Fragment                
    * Marcus's Research Notes             
                                          
  MISSION SUMMARY:                        
    Time Played: 4h 23m                   
    Party Survivors: 4/4                  
    Mayor's Family: All Rescued (check)         
                                          
  Game auto-saved.                        
                                          
  [Continue to Redstone]                  
                                          
================================================================
```

**Bonus Calculation Logic:**
```python
def calculate_victory_bonuses(game_state):
    """Calculate all XP bonuses based on player achievements"""
    bonuses = {
        'base_victory': 1000,  # Always awarded
        'mayor_family': 0,
        'portal_sealed': 250,
        'special_items': []
    }
    
    # Mayor's family bonus (Phase 1 implementation)
    if hasattr(game_state, 'mayor_family_status'):
        if game_state.mayor_family_status == 'all_saved':
            bonuses['mayor_family'] = 500
        elif game_state.mayor_family_status == 'partial':
            bonuses['mayor_family'] = 300
        # 'none' = 0 XP
    
    # Future: Add more conditional bonuses here
    # if game_state.locations_explored == 4:
    #     bonuses['thorough_investigation'] = 250
    
    return bonuses
```

**Key Features:**
- Auto-save before continuing (once only)
- Clear stat breakdown
- Special item notifications
- Mission summary
- NO level-up notifications (shown later in post-game)
- Clean separation from combat state

**Navigation:**
- **Continue button** -> Phase 3 (Town Celebration)

---

### Phase 3: Return to Redstone - Static Town Square Celebration
**Screen:** `screens/victory_celebration.py` (NEW)

**Visual:** Reuse town_map renderer as static background with NPCs in celebration positions

**Purpose:** Immediate story resolution with key characters in familiar location

**CRITICAL DESIGN DECISION:**  
This screen **reuses the existing RedstoneTownRenderer** from `screens/redstone_town.py` to show the town square as a **static background**. No new art required!

**Technical Implementation:**
```python
class VictoryCelebrationScreen:
    """Town celebration using static town map rendering"""
    
    def __init__(self):
        # Import existing town renderer
        from screens.redstone_town import RedstoneTownRenderer
        self.town_renderer = RedstoneTownRenderer()
        
        # Define fixed NPC positions for celebration
        self.celebration_npcs = {
            'mayor': (8, 7),      # Center of town square
            'cassia': (7, 7),     # Left of mayor
            'henrik': (9, 7),     # Right of mayor (if quest completed)
            'garrick': (8, 8),    # Behind
            'bernard': (7, 8),    # Behind left
        }
        
        # Sequence of dialogues to auto-play
        self.dialogue_sequence = self.build_dialogue_sequence(game_state)
        self.current_dialogue_index = 0
        
    def build_dialogue_sequence(self, game_state):
        """Build NPC dialogue sequence based on game state"""
        sequence = ['mayor']  # Mayor always first
        sequence.append('cassia')  # Cassia always second
        
        # Henrik only if his quest was completed
        if getattr(game_state, 'henrik_mine_quest_complete', False):
            sequence.append('henrik')
        
        return sequence
        
    def render(self, surface, fonts, game_state):
        surface.fill(BLACK)
        
        # Draw town square as static background
        self.draw_static_town_square(surface)
        
        # Draw NPCs in celebration positions (static sprites)
        self.draw_celebration_npcs(surface, game_state)
        
        # Highlight current NPC being addressed
        self.highlight_current_npc(surface)
        
        # Run dialogue for current NPC
        current_npc = self.dialogue_sequence[self.current_dialogue_index]
        self.run_npc_dialogue(surface, fonts, game_state, current_npc)
        
    def draw_static_town_square(self, surface):
        """Render town square tiles as static background"""
        # Center on town square coordinates (8, 7)
        center_x, center_y = 8, 7
        
        # Use existing renderer but in "static" mode (no player movement)
        # This renders the town tiles and buildings
        self.town_renderer.draw_map_static(surface, center_x, center_y)
        
    def draw_celebration_npcs(self, surface, game_state):
        """Draw NPCs in fixed celebration positions"""
        for npc_id, (tile_x, tile_y) in self.celebration_npcs.items():
            # Skip Henrik if quest not completed
            if npc_id == 'henrik' and not getattr(game_state, 'henrik_mine_quest_complete', False):
                continue
                
            # Draw NPC sprite at fixed position
            self.town_renderer.draw_npc_sprite(surface, npc_id, tile_x, tile_y)
            
    def highlight_current_npc(self, surface):
        """Highlight the NPC currently being addressed"""
        current_npc = self.dialogue_sequence[self.current_dialogue_index]
        tile_x, tile_y = self.celebration_npcs[current_npc]
        
        # Draw subtle highlight circle or glow around current NPC
        self.draw_npc_highlight(surface, tile_x, tile_y)
```

**Dialogue Flow:**

**IMPORTANT: No new dialogue files created!**  
Instead, add **new victory states** to existing dialogue files:

#### 3A: Mayor Resolution (FIRST)
**File:** `data/dialogues/redstone_town_mayor.json` (EXISTING - add new states)

**New States to Add:**
```json
{
  "metadata": {
    "display_name": "Mayor Aldwin Goldenbottom",
    "is_object": false
  },
  "initial_state": "first_meeting",
  "states": {
    "first_meeting": { ... existing ... },
    "quest_given": { ... existing ... },
    
    "victory_family_saved": {
      "introduction": [
        "*The Mayor embraces his family, tears streaming*",
        "",
        "You did it. You brought them back.",
        "",
        "*He turns to you, his voice thick with emotion*",
        "",
        "Words cannot express my gratitude. Redstone owes you everything.",
        "",
        "*He presses a pouch of gold and a ring into your hands*",
        "",
        "Take these. You've earned far more than I can ever repay."
      ],
      "effects": [
        {"type": "award_xp", "amount": 500},
        {"type": "award_gold", "amount": 1000},
        {"type": "add_item", "item_id": "mayors_gratitude_ring"}
      ],
      "choices": [
        {
          "text": "[Accept the reward]",
          "next_state": "CONVERSATION_END"
        }
      ]
    },
    
    "victory_family_partial": {
      "introduction": [
        "*The Mayor's joy is tempered by profound loss*",
        "",
        "You saved those you could. I am grateful for that.",
        "",
        "But the empty chairs at my table... they will haunt me forever.",
        "",
        "*He steadies himself, forcing composure*",
        "",
        "Take this. You earned it, even if the cost was high."
      ],
      "effects": [
        {"type": "award_xp", "amount": 300},
        {"type": "award_gold", "amount": 750}
      ],
      "choices": [
        {
          "text": "[Accept the reward]",
          "next_state": "CONVERSATION_END"
        }
      ]
    },
    
    "victory_family_lost": {
      "introduction": [
        "*The Mayor stands alone, hollow-eyed*",
        "",
        "They're gone. All of them.",
        "",
        "*His voice cracks*",
        "",
        "You sealed the portal. You saved the town. But my family...",
        "",
        "*He cannot continue*"
      ],
      "effects": [
        {"type": "award_xp", "amount": 100}
      ],
      "choices": [
        {
          "text": "[Leave him to his grief]",
          "next_state": "CONVERSATION_END"
        }
      ]
    }
  }
}
```

**How to Trigger Correct State:**
```python
# In VictoryCelebrationScreen, before starting mayor dialogue:
if game_state.mayor_family_status == 'all_saved':
    game_state.mayor_dialogue_state = "victory_family_saved"
elif game_state.mayor_family_status == 'partial':
    game_state.mayor_dialogue_state = "victory_family_partial"
else:
    game_state.mayor_dialogue_state = "victory_family_lost"
```

#### 3B: Cassia Resolution (SECOND)
**File:** `data/dialogues/redstone_town_cassia.json` (EXISTING - add new states)

**New States to Add:**
```json
{
  "states": {
    "... existing states ...",
    
    "victory_marcus_fled": {
      "introduction": [
        "*Cassia looks toward the horizon, a sad smile on her face*",
        "",
        "He's gone. Fled after the battle, I'm told.",
        "",
        "Part of me hoped he would stay. That we could find a way forward.",
        "",
        "*She turns to you*",
        "",
        "But perhaps distance is what he needs. Time to heal, to remember who he was.",
        "",
        "Thank you for giving him that chance."
      ],
      "effects": [
        {"type": "award_xp", "amount": 200},
        {"type": "set_flag", "flag": "cassia_shop_discount", "value": true}
      ],
      "choices": [
        {"text": "[Offer condolences]", "next_state": "CONVERSATION_END"}
      ]
    },
    
    "victory_marcus_killed": {
      "introduction": [
        "*Cassia's eyes are red from crying*",
        "",
        "He's dead. The Shadow Blight finally took him completely.",
        "",
        "*She wipes her eyes*",
        "",
        "I held a private memorial. For the man he once was, not the monster he became.",
        "",
        "Thank you for... ending his torment. It was a kindness, in the end."
      ],
      "effects": [
        {"type": "award_xp", "amount": 300},
        {"type": "set_flag", "flag": "cassia_shop_discount", "value": true}
      ],
      "choices": [
        {"text": "[Offer condolences]", "next_state": "CONVERSATION_END"}
      ]
    },
    
    "victory_marcus_redeemed": {
      "introduction": [
        "*Cassia's face lights up with hope*",
        "",
        "You saw it, didn't you? In the final moment, he fought WITH you.",
        "",
        "The Marcus I loved was still there. Buried, but not gone.",
        "",
        "*Tears stream down her face*",
        "",
        "He gave his life to weaken the portal. A final act of redemption.",
        "",
        "That's how I'll remember him. Not as a cultist, but as a hero."
      ],
      "effects": [
        {"type": "award_xp", "amount": 500},
        {"type": "add_item", "item_id": "cassias_pendant"},
        {"type": "set_flag", "flag": "cassia_shop_discount", "value": true}
      ],
      "choices": [
        {"text": "[Console her]", "next_state": "CONVERSATION_END"}
      ]
    }
  }
}
```

#### 3C: Henrik Resolution (THIRD - Conditional)
**File:** `data/dialogues/redstone_town_henrik.json` (EXISTING - add new state)

**Only appears if:** `henrik_mine_quest_complete == True`

```json
{
  "states": {
    "... existing states ...",
    
    "victory_mine_route": {
      "introduction": [
        "*Henrik grins widely, slapping you on the back*",
        "",
        "You used the mine route! Smart thinking!",
        "",
        "And those ore samples you brought back from the deeper levels...",
        "",
        "*His eyes gleam*",
        "",
        "Pure Aethel ore! With the cult gone, I can safely reopen the mine.",
        "",
        "Here - your share of the first finds. Consider it an investment!"
      ],
      "effects": [
        {"type": "award_gold", "amount": 500},
        {"type": "add_item", "item_id": "aethel_ore_sample"}
      ],
      "choices": [
        {"text": "[Accept the reward]", "next_state": "CONVERSATION_END"}
      ]
    }
  }
}
```

**Auto-Play Sequence:**
1. Mayor dialogue loads and plays automatically
2. When player clicks "[Continue]" -> Mayor dialogue ends
3. Next NPC (Cassia) dialogue loads automatically
4. When player clicks "[Continue]" -> Cassia dialogue ends
5. If Henrik quest completed -> Henrik dialogue loads
6. When final NPC dialogue ends -> Navigate to Phase 4

**Navigation:**
- After last dialogue -> Phase 4 (Epilogue Slides)

---

### Phase 4: Epilogue Cinematic Slides
**Screen:** `screens/epilogue_slides.py` (NEW - copy intro_scenes.py pattern)
**Data:** `data/narrative/epilogue_sequence.json` (NEW)

**System:** Reuse intro_scenes.py architecture!

**Implementation:**
```python
# Copy intro_scenes.py structure exactly
class EpilogueSequenceManager:
    def __init__(self, event_manager, game_state):
        self.epilogue_data = self.load_epilogue_data()
        self.game_state = game_state
        self.current_slide = 0
        
    def get_current_slide(self):
        """Get current slide with conditional content resolved"""
        slide_data = self.epilogue_data["slides"][self.current_slide]
        return self.resolve_conditional_content(slide_data)
        
    def resolve_conditional_content(self, slide):
        """Check conditions and return appropriate content variant"""
        if "variations" in slide:
            for variant in slide["variations"]:
                condition = variant.get("condition")
                if self.check_condition(condition):
                    return variant["content"]
        
        # Fallback to default content
        return slide.get("content", [])
    
    def check_condition(self, condition_string):
        """Evaluate condition against game state"""
        # Examples:
        # "mayor_family_status == 'all_saved'"
        # "marcus_outcome == 'fled'"
        # "has_item:portal_seal_fragment"
        
        if condition_string.startswith("has_item:"):
            item_id = condition_string.split(":")[1]
            return self.game_state.player_has_item(item_id)
        else:
            # Evaluate flag condition
            return eval(condition_string, {"game_state": self.game_state})
```

#### Slide Structure (7 Slides)

**Slide 1: Victory Declaration**
```json
{
  "id": "victory_declaration",
  "title": "VICTORY",
  "background_style": "dawn_sky",
  "content": [
    "The cult of Redstone has been vanquished.",
    "",
    "The Shadow Blight, sealed once more.",
    "",
    "The darkness that plagued the Crimson Reach has lifted.",
    "",
    "But the cost of victory varies with each hero's choices..."
  ]
}
```

**Slide 2: Mayor's Family (CONDITIONAL)**
```json
{
  "id": "mayors_family",
  "title": "THE MAYOR'S FAMILY",
  "background_style": "town_square",
  "variations": [
    {
      "condition": "game_state.mayor_family_status == 'all_saved'",
      "content": [
        "Mayor Aldwin Goldenbottom's family returned safely.",
        "",
        "His son will carry forward the family legacy of service to Redstone."
      ]
    },
    {
      "condition": "game_state.mayor_family_status == 'partial'",
      "content": [
        "Not all of the Mayor's family survived their captivity.",
        "",
        "Aldwin carries the weight of that loss, but continues to lead."
      ]
    },
    {
      "condition": "game_state.mayor_family_status == 'none'",
      "content": [
        "The Mayor's family perished before they could be rescued.",
        "",
        "Grief-stricken, Aldwin will soon resign his post.",
        "",
        "Redstone mourns the loss."
      ]
    }
  ]
}
```

**Slide 3: Villager Rescue (SIMPLIFIED FOR PHASE 1)**
```json
{
  "id": "rescued_captives",
  "title": "THE CAPTIVES",
  "background_style": "redstone_streets",
  "variations": [
    {
      "condition": "game_state.mayor_family_status == 'all_saved'",
      "content": [
        "All of the cult's captives were freed from the dungeon.",
        "",
        "They return to their families, forever changed by their ordeal.",
        "",
        "The town celebrates their heroes' thorough victory."
      ]
    },
    {
      "condition": "game_state.mayor_family_status == 'partial'",
      "content": [
        "Some captives were rescued from the cult's prison.",
        "",
        "Others were not so fortunate.",
        "",
        "The survivors carry scars that may never fully heal."
      ]
    },
    {
      "condition": "game_state.mayor_family_status == 'none'",
      "content": [
        "The heroes arrived too late to save the captives.",
        "",
        "Redstone mourns its lost children.",
        "",
        "But at least the Shadow Blight will claim no more victims."
      ]
    }
  ]
}
```

**NOTE FOR FUTURE ENHANCEMENT:**
```json
// When multi-location villager rescue is implemented:
{
  "id": "rescued_captives_detailed",
  "title": "THE RESCUED",
  "content_template": [
    "[X] villagers were rescued from across the investigation sites:",
    "",
    "Swamp Church: [Y] cultists freed",
    "Hill Ruins: [Z] prisoners liberated", 
    "Red Hollow Mine: [W] workers saved",
    "",
    "Each owes their life to the heroes' thorough investigation."
  ]
}
```

**Slide 4: Marcus Resolution (CONDITIONAL)**
```json
{
  "id": "marcus_fate",
  "title": "THE CORRUPTED SCHOLAR",
  "background_style": "violet_mortar_shop",
  "variations": [
    {
      "condition": "game_state.marcus_outcome == 'fled'",
      "content": [
        "Marcus Nightshade disappeared after the battle.",
        "",
        "Some say Cassia still receives letters from a distant land.",
        "",
        "Perhaps, in time, he will find redemption."
      ]
    },
    {
      "condition": "game_state.marcus_outcome == 'killed'",
      "content": [
        "Marcus Nightshade fell in the final battle.",
        "",
        "Cassia held a private memorial for the man he once was.",
        "",
        "The Shadow Blight takes everything, even those we love."
      ]
    },
    {
      "condition": "game_state.marcus_outcome == 'ally'",
      "content": [
        "Marcus Nightshade fought alongside the heroes at the end.",
        "",
        "His sacrifice weakened the Blight's hold on the portal.",
        "",
        "Cassia remembers him not as a monster,",
        "but as her beloved husband who found his way back."
      ]
    }
  ]
}
```

**Slide 5: Investigation Results (SIMPLIFIED)**
```json
{
  "id": "investigation_results",
  "title": "THE INVESTIGATION",
  "background_style": "marsh_sunset",
  "content": [
    "The heroes' investigation uncovered the cult's secrets:",
    "",
    "Ancient texts revealed the Shadow Blight's true nature.",
    "",
    "Evidence gathered across the Crimson Reach",
    "proved invaluable in the final confrontation.",
    "",
    "Knowledge, as much as courage, won the day."
  ]
}
```

**Slide 6: Cavia Variant (CONDITIONAL)**
```json
{
  "id": "cavia_recognition",
  "title": "THE CAVIA HERO",
  "background_style": "redstone_streets",
  "variations": [
    {
      "condition": "game_state.player_species == 'Cavia'",
      "content": [
        "For the first time in Redstone's history,",
        "a Cavia stood as the town's champion.",
        "",
        "Their bravery shattered old prejudices.",
        "",
        "Perhaps this marks a new era of understanding",
        "between Cavia and the other peoples of the realm."
      ]
    },
    {
      "condition": "default",
      "content": [
        "The heroes' victory will be remembered for generations.",
        "",
        "Songs will be sung of their courage.",
        "",
        "Redstone stands safe, thanks to their sacrifice."
      ]
    }
  ]
}
```

**Slide 7: The Future (Hook Slide with Item Integration)**
```json
{
  "id": "mysteries_remain",
  "title": "MYSTERIES REMAIN",
  "background_style": "ancient_scroll",
  "content_conditional": [
    {
      "priority": 1,
      "condition": "has_item:portal_seal_fragment",
      "text": "The Portal Seal Fragment you recovered pulses with dormant energy.",
      "text2": "What other sealed portals exist beyond Redstone's borders?"
    },
    {
      "priority": 2,
      "condition": "has_item:marcus_research_notes",
      "text": "Marcus's research mentions 'three great seals' protecting the realm.",
      "text2": "Redstone was only the first. Where are the others?"
    },
    {
      "priority": 3,
      "condition": "has_item:aethel_ore_sample",
      "text": "The rare Aethel ore responds to magical energy in strange ways.",
      "text2": "What powerful artifacts could be forged from such material?"
    },
    {
      "priority": 4,
      "condition": "explored:hill_ruins_deep",
      "text": "The ancient inscriptions speak of an empire that fell long ago.",
      "text2": "What cataclysm destroyed them? Could it happen again?"
    }
  ],
  "default_content": [
    "But greater shadows stir beyond the Crimson Reach...",
    "",
    "Darker secrets wait to be uncovered.",
    "",
    "And heroes will be needed once more."
  ],
  "footer": "The adventure continues in... [SEQUEL TITLE TBD]"
}
```

**Hook Slide Logic:**
```python
def resolve_hook_content(self, slide_data, game_state):
    """Select most relevant sequel hook based on player discoveries"""
    hooks = slide_data["content_conditional"]
    
    # Sort by priority
    applicable_hooks = []
    for hook in hooks:
        if self.check_condition(hook["condition"]):
            applicable_hooks.append(hook)
    
    if applicable_hooks:
        # Show top 1-2 hooks
        selected = applicable_hooks[:2]
        content = []
        for hook in selected:
            content.append(hook["text"])
            content.append(hook["text2"])
            content.append("")
    else:
        # Fallback generic hook
        content = slide_data["default_content"]
    
    # Always add footer
    content.append("")
    content.append(slide_data["footer"])
    
    return content
```

**Navigation:**
- After last slide -> Phase 5 (Credits)

---

### Phase 5: Scrolling Credits
**Screen:** `screens/credits.py` (NEW)
**Data:** `data/narrative/credits_data.json` (NEW - JSON-driven!)

**JSON Structure:**
```json
{
  "credits": [
    {
      "section": "Created By",
      "entries": ["Dennis [Your Last Name]"],
      "spacing": 3
    },
    {
      "section": "Special Thanks",
      "entries": [
        "Coffee",
        "Late nights debugging",
        "The patient community"
      ],
      "spacing": 2
    },
    {
      "section": "Built With",
      "entries": [
        "Python 3.x",
        "Pygame",
        "Stubborn determination"
      ],
      "spacing": 4
    },
    {
      "section": "Inspired By",
      "entries": [
        "SSI Gold Box Games (1988-1992)",
        "Ultima Series",
        "Wizardry",
        "The Golden Age of CRPGs"
      ],
      "spacing": 2
    },
    {
      "section": "Thank You",
      "entries": [
        "For playing Terror in Redstone!",
        "",
        "Your adventure is just beginning..."
      ],
      "spacing": 5
    }
  ],
  "scroll_speed": 1.0,
  "final_message": "Press ESC to continue",
  "final_message_pause": 3.0
}
```

**Implementation:**
```python
class CreditsScreen:
    """JSON-driven scrolling credits"""
    
    def __init__(self):
        self.credits_data = self.load_credits_json()
        self.scroll_position = 768  # Start below screen
        self.scroll_speed = self.credits_data["scroll_speed"]
        self.credits_lines = self.build_credits_lines()
        
    def build_credits_lines(self):
        """Convert JSON data to renderable lines"""
        lines = []
        for section in self.credits_data["credits"]:
            # Section header
            lines.append({
                "text": section["section"],
                "style": "header",
                "color": (200, 200, 255)
            })
            lines.append({"text": "", "style": "blank"})
            
            # Section entries
            for entry in section["entries"]:
                lines.append({
                    "text": entry,
                    "style": "normal",
                    "color": (220, 220, 220)
                })
            
            # Spacing
            for _ in range(section["spacing"]):
                lines.append({"text": "", "style": "blank"})
        
        return lines
    
    def update(self, dt):
        """Scroll credits upward"""
        self.scroll_position -= self.scroll_speed
        
        # Check if finished
        total_height = len(self.credits_lines) * 30
        if self.scroll_position < -total_height:
            self.show_final_message()
    
    def handle_input(self, event):
        """Allow ESC to skip"""
        if event.key == pygame.K_ESCAPE:
            self.skip_to_postgame()
```

**Key Features:**
- JSON-driven (easy to update)
- Auto-scroll with configurable speed
- ESC to skip at any time
- Fade to black at end
- Music integration

**Navigation:**
- After credits complete (or ESC pressed) -> Phase 6 (Post-Game Menu)

---

### Phase 6: Post-Game Menu and Continue Exploring
**Screen:** `screens/post_game_menu.py` (NEW)

**Purpose:** Special menu after game completion

**Display:**
```
================================================================
        TERROR IN REDSTONE                  
            Game Complete!
                                            
  [Continue Exploring] (star icon)                   
  [View Statistics]                                
  [New Game]                                
  [Load Game]                               
  [Exit Game]                               
                                            
  Current Save: Post-Game - Level 6          
  Play Time: 4h 23m
                                            
================================================================
```

**Post-Game Features:**

#### 6A: Unique Auto-Save
```python
def save_postgame_state(game_state):
    """Create special post-game save file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"postgame_autosave_{timestamp}.sav"
    
    # Mark as completed game
    game_state.game_completed = True
    game_state.completion_date = datetime.now()
    game_state.epilogue_viewed = True
    
    # Save with special marker
    save_game(game_state, filename, is_postgame=True)
    
    return filename
```

**Save File Indicators:**
- Normal saves: "ACT II - Level 5"
- Post-game saves: "(star) Post-Game - Level 6"

#### 6B: Statistics Screen
```
================================================================
              GAME STATISTICS
================================================================
                                          
  MAIN QUEST: Complete (check)                   
  ACT II INVESTIGATION: 4/4 Locations Explored           
  MAYOR'S FAMILY: All Rescued (check)
                                          
  SIDE QUESTS:                          
    Henrik's Mine: Complete               
    [Future quests here]               
                                          
  PARTY STATUS:                            
    Level: 6                            
    Total XP: 12,450
    Gold: 2,340
                                          
  PLAYTIME: 4h 23m                    
                                          
  SPECIAL ACHIEVEMENTS:
    (star) Portal Sealed
    (star) All Captives Rescued
    (star) Scholar's Redemption (if applicable)
                                          
  [Continue]  [Return to Menu]     
                                          
================================================================
```

#### 6C: Continue Exploring Features

**Post-Victory Town State:**
```python
class PostGameTownState:
    """Town state after victory"""
    
    def __init__(self, game_state):
        # Set all NPCs to post-victory dialogue states
        self.set_postgame_npc_states(game_state)
        
        # Disable certain areas
        game_state.dungeon_accessible = False  # Portal sealed
        game_state.world_map_accessible = True  # Can still explore
        
        # Enable post-game content
        game_state.postgame_quests_available = True
        
    def set_postgame_npc_states(self, game_state):
        """Set all NPCs to show post-victory dialogue"""
        game_state.mayor_dialogue_state = "post_victory"
        game_state.cassia_dialogue_state = "post_victory"
        game_state.henrik_dialogue_state = "post_victory"
        game_state.garrick_dialogue_state = "post_victory"
        # etc.
```

**Post-Game NPC Dialogue (Add to existing files):**
```json
// In redstone_town_mayor.json
{
  "states": {
    "post_victory": {
      "introduction": [
        "*The Mayor looks healthier than he has in weeks*",
        "",
        "Life is slowly returning to normal in Redstone.",
        "",
        "Thanks to you, we have a future to look forward to.",
        "",
        "Is there something I can help you with?"
      ],
      "choices": [
        {"text": "[Ask about the town's recovery]", "next_state": "recovery_details"},
        {"text": "[Farewell]", "next_state": "CONVERSATION_END"}
      ]
    }
  }
}
```

**Available Activities:**
- Talk to all NPCs (new "post_victory" dialogue states)
- Shop at merchants (buy potions, upgrade equipment)
- Complete side quests (future: add optional post-game quests)
- Explore town freely
- View statistics anytime
- Return to main menu when done

**Restrictions:**
- Cannot re-enter dungeon (portal sealed)
- Cannot trigger main quest again
- No random encounters in town (peaceful)

**Graceful Exit:**
- Can save at any time
- Return to main menu
- Start New Game
- Load different save

---

## FILE STRUCTURE

```
screens/
├── victory_screen.py                (NEW - detailed stat screen)
├── victory_celebration.py           (NEW - static town square with NPC dialogues)
├── epilogue_slides.py               (NEW - copy intro_scenes.py)
├── credits.py                       (NEW - JSON-driven scroll)
└── post_game_menu.py                (NEW - post-completion menu)

data/narrative/
├── epilogue_sequence.json           (NEW - 7 conditional slides)
└── credits_data.json                (NEW - JSON credits)

data/dialogues/
├── redstone_town_mayor.json         (MODIFY - add victory states)
├── redstone_town_cassia.json        (MODIFY - add victory states)
└── redstone_town_henrik.json        (MODIFY - add victory state)

// NO NEW DIALOGUE FILES NEEDED!
```

---

## VISUAL DESIGN

### Victory Screen Background
- Black background with gold/white text borders
- Clean stat layout (similar to character creation)
- Prominent "VICTORY!" header

### Town Celebration Background
- Reuse `RedstoneTownRenderer` from `screens/redstone_town.py`
- Static view centered on town square (tiles 7-9, 6-8)
- NPCs rendered in fixed celebration positions
- Current NPC highlighted with subtle glow

### Epilogue Slide Backgrounds
**Reuse intro_scenes.py atmospheric backgrounds:**
- `dawn_sky` - hopeful, new beginning
- `town_square` - community gathering  
- `redstone_streets` - daily life restored
- `violet_mortar_shop` - Cassia's shop
- `marsh_sunset` - swamp healing
- `ancient_scroll` - mysterious map

### Credits Background
- Black screen with centered text (classic)
- OR slow pan across town square (future)

---

## AUDIO

### Music Tracks Needed:
1. **Victory Fanfare** (30 seconds) - Phase 2 victory screen
2. **Town Celebration** (looping) - Phase 3 NPC dialogues
3. **Bittersweet Epilogue** (3-4 minutes) - Phase 4 slides
4. **Credits Theme** (2-3 minutes) - Phase 5 credits roll
5. **Post-Game Ambient** (looping) - Phase 6 town exploration

### Sound Effects:
- Portal collapse rumble (Phase 1)
- Crowd cheering (Phase 3 start)
- Page turn (Phase 4 slide transitions)
- Pen scratch (Phase 5 credits roll)

---

## PLAYER OPTIONS AT EACH STAGE

### After Boss (Phase 1):
- **None** - Automatic progression to victory screen

### Victory Screen (Phase 2):
- **[Continue to Town]** - Proceed to Phase 3

### Town Celebration (Phase 3):
- **[Continue]** - Advance through NPC dialogue sequence
- Auto-advances to next NPC after each dialogue ends

### Epilogue Slides (Phase 4):
- **Click / Space / Enter** - Next slide
- **ESC** - Skip to credits (confirmation prompt?)

### Credits (Phase 5):
- **Wait** - Auto-scroll to end
- **ESC** - Skip to post-game menu

### Post-Game Menu (Phase 6):
- **Continue Exploring** - Return to Redstone town (post-victory state)
- **View Statistics** - Show completion stats
- **New Game** - Start fresh playthrough
- **Load Game** - Load different save
- **Exit** - Quit to desktop

---

## IMPLEMENTATION CHECKLIST

### Pre-Implementation:
- [ ] Review intro_scenes.py architecture
- [ ] Review redstone_town.py renderer for static rendering
- [ ] List all outcome flags currently implemented
- [ ] Write epilogue slide text
- [ ] Write credits JSON

### Session A: Victory Screen (2-3 hours)
- [ ] Create victory_screen.py
- [ ] Implement bonus calculation logic
- [ ] Design victory panel layout
- [ ] Add auto-save functionality
- [ ] Test with different outcomes
- [ ] Register in ScreenManager

### Session B: Town Celebration (3-4 hours)
- [ ] Create victory_celebration.py
- [ ] Import RedstoneTownRenderer
- [ ] Implement static town square rendering
- [ ] Add NPC celebration positioning
- [ ] Implement auto-play dialogue sequence
- [ ] Add mayor victory states to redstone_town_mayor.json
- [ ] Add cassia victory states to redstone_town_cassia.json
- [ ] Add henrik victory state to redstone_town_henrik.json
- [ ] Test dialogue flow
- [ ] Verify rewards given correctly

### Session C: Epilogue Slides (3-4 hours)
- [ ] Copy intro_scenes.py -> epilogue_slides.py
- [ ] Create epilogue_sequence.json (7 slides)
- [ ] Implement conditional content resolution
- [ ] Add Cavia variant detection
- [ ] Implement hook slide item checking
- [ ] Test all slide variations
- [ ] Verify smooth transitions
- [ ] Register in ScreenManager

### Session D: Credits (2-3 hours)
- [ ] Create credits.py with scroll system
- [ ] Create credits_data.json
- [ ] Implement JSON loading
- [ ] Implement auto-scroll
- [ ] Add ESC skip functionality
- [ ] Add music integration
- [ ] Test complete roll
- [ ] Verify navigation to post-game

### Session E: Post-Game State (2-3 hours)
- [ ] Create post_game_menu.py
- [ ] Implement statistics screen
- [ ] Add post_victory NPC dialogue states
- [ ] Implement unique post-game save system
- [ ] Test continue exploring
- [ ] Verify town NPCs work correctly
- [ ] Test save file persistence
- [ ] Ensure no quest restart bugs

### Polish:
- [ ] Add music for all phases
- [ ] Add sound effects
- [ ] Test complete victory->credits->postgame flow
- [ ] Playtest with different outcome combinations
- [ ] Test auto-save/load cycle
- [ ] Fix any bugs
- [ ] Performance testing (maintain 60 FPS)

---

## QUICK START RECOMMENDATION

**Recommended Implementation Order:**

1. **Start with Session A** (Victory Screen) - Establishes immediate post-boss flow
2. **Then Session C** (Epilogue Slides) - Reuses intro_scenes.py pattern (easiest)
3. **Then Session B** (Town Celebration) - Most complex (reusing town renderer)
4. **Then Session D** (Credits) - Straightforward scroll system
5. **Finally Session E** (Post-Game) - Polish and optional content

**Why this order:**
- Victory screen is critical path and simplest
- Epilogue slides reuse existing pattern (quick win)
- Town celebration is complex but happens early in flow
- Credits are simple once other pieces work
- Post-game is optional polish that can come last

---

## ADR RECOMMENDATION

After completing epilogue system:

```
ADR-XXX: Complete Epilogue System Implementation
Status: Accepted
Date: [Date]

Context: Game needed professional ending sequence matching quality 
of intro cinematics and act transitions while minimizing new art assets.

Decision: Implemented 4-phase epilogue system reusing existing visual assets:
1. Victory screen with detailed statistics and auto-save
2. Town celebration using static town_map renderer (no new art!)
3. Cinematic epilogue slides with 7 conditional variations
4. JSON-driven scrolling credits with sequel hooks
5. Post-game menu with continue exploring option

Implementation:
- Victory screen: New full screen with stat breakdown
- Town celebration: Reused RedstoneTownRenderer in static mode
- Dialogue: State-based approach (no new dialogue files)
- Slides: Copied intro_scenes.py architecture
- Credits: JSON-driven for easy updates
- Post-game: New dialogue states in existing files

Technical Decisions:
- New screen (not overlay) for victory (clean state separation)
- Static rendering of town_map (reuses existing assets)
- State-based dialogue system (no new files, cleaner architecture)
- Item-based sequel hooks (rewards thorough exploration)

Consequences:
+ Professional ending experience
+ No new art assets required (reuses town renderer!)
+ Multiple playthroughs rewarded (conditional content)
+ Sequel hook established through items
+ Easy to update credits (JSON)
+ Post-game exploration available
- Additional 10-15 hours development time
- Mayor's family only rescuable entity (Phase 1 scope)
- Future: Expand to multi-location villager rescue

Files Created: 
- screens/victory_screen.py
- screens/victory_celebration.py
- screens/epilogue_slides.py
- screens/credits.py
- screens/post_game_menu.py
- data/narrative/epilogue_sequence.json
- data/narrative/credits_data.json

Files Modified:
- data/dialogues/redstone_town_mayor.json (added victory states)
- data/dialogues/redstone_town_cassia.json (added victory states)
- data/dialogues/redstone_town_henrik.json (added victory state)
- ui/screen_manager.py (registered new screens)
```

---

## SUCCESS METRICS

**Player Experience:**
- [ ] Feels emotionally satisfying
- [ ] Rewards player choices with different outcomes
- [ ] Professional presentation quality
- [ ] Clear sequel hook through discovered items
- [ ] Encourages replay to see variations

**Technical Quality:**
- [ ] No crashes during epilogue sequence
- [ ] All conditional variations display correctly
- [ ] Smooth transitions throughout
- [ ] Auto-saves work correctly
- [ ] Post-game saves preserve state
- [ ] Performance maintained (60 FPS throughout)
- [ ] Town renderer works in static mode

**Content Completeness (Phase 1):**
- [ ] Mayor's family rescue outcomes working
- [ ] Marcus fate variations displaying
- [ ] Cavia variant recognition working
- [ ] Hook slide item checking functional
- [ ] All post-victory NPC dialogues working

**Future Enhancement Readiness:**
- [ ] System designed to add more rescuable villagers
- [ ] Credits JSON easy to update
- [ ] Post-game quests can be added to dialogue states
- [ ] Additional epilogue slides can be inserted

---

## NOTES FOR FUTURE DEVELOPERS

### Current Limitations (Phase 1 Scope):
1. **Only mayor's family rescuable** - Future: Add church captives, mine workers, etc.
2. **Simple investigation slide** - Future: Show detailed location-by-location results
3. **Limited post-game content** - Future: Add optional post-game quests

### Expansion Points:
1. **Villager Rescue System** - Add rescue opportunities at each Act II location
2. **Investigation Details** - Track discoveries per location for detailed epilogue
3. **Post-Game Quests** - Add optional cleanup quests to post-victory dialogue states
4. **Pixel Art Slides** - Replace atmospheric backgrounds with 1024x510 illustrations
5. **Music** - Commission custom tracks for each epilogue phase

### Key Design Patterns:
- **Reuse existing systems** - Don't rebuild what works (town renderer, dialogue engine)
- **JSON-driven content** - Easy to update without code changes (credits, slides)
- **State-based dialogue** - Cleaner than creating new files for every state
- **Conditional content** - Check game state to show appropriate variations

---

**READY TO BUILD THIS?**

Implementation can start with any session, but **Session A (Victory Screen)** is recommended first since it's the critical path and simplest to implement. After that, **Session C (Epilogue Slides)** provides the biggest visual impact while reusing familiar patterns.
