# Act II Mayor & Discovery System Implementation Plan
## Terror in Redstone - Comprehensive Developer Guide

**Document Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Ready for Implementation  
**Estimated Time:** 5 sessions (8-10 hours total)

---

## 📋 EXECUTIVE SUMMARY

This document outlines the complete implementation plan for transitioning the game from Act I (tavern-based) to Act II (exploration phase), including:
- Mayor location transition from tavern to office
- Discovery-based location unlocking system
- Multiple NPC information sources with redundancy
- Dynamic mayor dialogue based on player progress
- Proper gate-keeping to prevent premature exploration

---

## 🎯 DESIGN DECISIONS (APPROVED)

### Decision 1: Discovery System
**Pattern:** Gated Discovery (Option B)
- Mayor gives general information about locations
- NPCs provide specific information that "discovers" locations
- Prevents premature exploration, rewards thorough investigation
- Mirrors classic CRPG design (Ultima, Baldur's Gate)

### Decision 2: Mayor Movement Timing
**Trigger:** After first town departure (Option B)
- Mayor stays in tavern (patron_selection) during Act I
- Moves to office (redstone_town) after `act_two_started = true`
- Narrative logic: Coordinating response from central location

### Decision 3: Progress Dialogue Complexity
**Level:** Medium (expandable to Complex)
- Mayor acknowledges each major location completion
- Specific dialogue for: Swamp, Ruins, Refugee Camp, Mine
- Can expand with more granular reactions later
- Only 4 areas maximum keeps this manageable

### Decision 4: Dialogue File Structure
**Pattern:** Separate Files (Option B)
- `patron_selection_mayor.json` - Act I quest-giving
- `redstone_town_mayor.json` - Act II progress tracking
- Clean separation of concerns
- Location-based routing via narrative schema

### Decision 5: Backup NPC Information Sources
**Redundancy Pattern:** Primary + Backup sources
- **PRIMARY:** Meredith (swamp), Garrick (ruins), Pete (refugee)
- **BACKUP:** Cassia (swamp), Bernard (ruins), Jenna (refugee)
- Prevents player from getting stuck
- Rewards thorough NPC interaction

---

## 🗂️ NARRATIVE FLAGS REFERENCE

### Discovery Flags (Unlock locations in exploration hub)
```
swamp_church_discovered
hill_ruins_discovered
refugee_camp_discovered
red_hollow_mine_discovered
```

### Completion Flags (Track location completion)
```
swamp_church_complete
hill_ruins_complete
refugee_camp_complete
red_hollow_mine_complete
```

### Act Progression Flags
```
quest_active              # Mayor quest accepted
act_two_started           # Player left town for first time
act_three_ready           # All required locations complete
```

### NPC Information Flags (Primary)
```
meredith_gave_swamp_info
garrick_gave_ruins_info
pete_gave_refugee_info
henrik_gave_mine_info
```

### NPC Information Flags (Backup)
```
bernard_gave_ruins_info
cassia_gave_swamp_info
jenna_gave_refugee_info
```

### Mayor Dialogue Flags
```
mayor_gave_swamp_info
mayor_gave_ruins_info
mayor_gave_refugee_info
mayor_acknowledged_swamp_complete
mayor_acknowledged_ruins_complete
mayor_acknowledged_refugee_complete
mayor_acknowledged_mine_complete
```

---

## 📁 FILE STRUCTURE

```
data/
├── narrative_schema.json                    # UPDATE - Add new flags
├── dialogues/
│   ├── patron_selection_mayor.json          # UPDATE - Remove premature discoveries
│   ├── redstone_town_mayor.json             # NEW - Act II office dialogue
│   ├── broken_blade_meredith.json           # UPDATE - Add swamp discovery
│   ├── broken_blade_garrick.json            # UPDATE - Add ruins discovery
│   ├── broken_blade_pete.json               # UPDATE - Add refugee discovery
│   ├── broken_blade_bernard.json            # UPDATE - Add ruins backup
│   ├── violet_mortar_cassia.json            # UPDATE - Add swamp backup
│   └── [jenna_location]_jenna.json          # UPDATE - Add refugee backup
└── maps/
    └── redstone_town_map.py                 # UPDATE - South gate conditions

game_logic/
└── dialogue_engine.py                       # UPDATE - Mayor location routing

screens/
└── act_two_transition.py                    # VERIFY - Ensure sets act_two_started flag
```

---

## 🔧 PHASE 1: NARRATIVE SCHEMA UPDATES

**File:** `data/narrative_schema.json`

### Task 1.1: Add Discovery Flags
Add to the locations section:
```json
"locations": {
  "swamp_church": {
    "system_id": "swamp_church",
    "name": "The Church in the Swamp",
    "discovery_flag": "swamp_church_discovered",
    "completion_flag": "swamp_church_complete",
    "description": "A fog-shrouded church deep in the marshlands where cult activity has been reported."
  },
  "hill_ruins": {
    "system_id": "hill_ruins",
    "name": "The Ruins on the Hill",
    "discovery_flag": "hill_ruins_discovered",
    "completion_flag": "hill_ruins_complete",
    "description": "Ancient watchtower overlooking the valley, glowing with strange lights at night."
  },
  "refugee_camp": {
    "system_id": "refugee_camp",
    "name": "The Refugee Camp",
    "discovery_flag": "refugee_camp_discovered",
    "completion_flag": "refugee_camp_complete",
    "description": "Makeshift settlement outside town where displaced miners seek shelter."
  },
  "red_hollow_mine": {
    "system_id": "red_hollow_mine",
    "name": "Red Hollow Mine",
    "discovery_flag": "red_hollow_mine_discovered",
    "completion_flag": "red_hollow_mine_complete",
    "description": "Abandoned mine shaft sealed by fearful workers, now home to unknown dangers."
  }
}
```

### Task 1.2: Update Mayor Schema
```json
"mayor": {
  "system_id": "mayor",
  "full_name": "Mayor Aldwin Goldenbottom",
  "dialogue_file": "patron_selection_mayor",
  "act_two_dialogue_file": "redstone_town_mayor",
  "conversation_flag": "mayor_talked",
  "location": "broken_blade",
  "act_two_location": "redstone_town",
  "role": "authority",
  "species": "human",
  "story_flags": {
    "gave_main_quest": "quest_active",
    "mentioned_family": "mayor_mentioned_family",
    "gave_swamp_location": "mayor_gave_swamp_info",
    "gave_ruins_location": "mayor_gave_ruins_info",
    "gave_refugee_location": "mayor_gave_refugee_info",
    "acknowledged_swamp": "mayor_acknowledged_swamp_complete",
    "acknowledged_ruins": "mayor_acknowledged_ruins_complete",
    "acknowledged_refugee": "mayor_acknowledged_refugee_complete",
    "acknowledged_mine": "mayor_acknowledged_mine_complete",
    "main_quest_completed": "main_quest_completed",
    "main_quest_reported": "reported_main_quest",
    "main_quest_paid": "mayor_paid_main_quest",
    "expressed_tremor_urgency": "mayor_worried_tremors",
    "requested_ore_investigation": "mayor_wants_ore_info",
    "ore_samples_examined": "mayor_examined_ore_samples"
  }
}
```

### Task 1.3: Add NPC Info Flags to Other NPCs
Add to Meredith, Garrick, Pete, Bernard, Cassia, Jenna schemas:
```json
"meredith": {
  "story_flags": {
    // ... existing flags ...
    "gave_swamp_location": "meredith_gave_swamp_info"
  }
}
```

**Testing Criteria:**
- [ ] All new flags initialize to false in GameState
- [ ] Save/load preserves all discovery flags
- [ ] No crashes when accessing narrative schema

---

## 🔧 PHASE 2: MAYOR DIALOGUE UPDATES

### Task 2.1: Update patron_selection_mayor.json (Act I Version)

**File:** `data/dialogues/patron_selection_mayor.json`

**Changes Required:**

**A) Modify quest_given state:**
```json
"quest_given": {
  "introduction": [
    "Three hotspots keep coming up: the Refugee Camp,",
    "the Hill Ruins, and the old Swamp Church.",
    "Talk to the tavern folk - they know the area better than I do.",
    "Meredith, Garrick, and Pete might have useful information."
  ],
  "options": [
    { 
      "id": "lead_swamp", 
      "text": "What do you know about the Swamp Church?", 
      "next_state": "brief_swamp" 
    },
    { 
      "id": "lead_ruins", 
      "text": "What about the Hill Ruins?",  
      "next_state": "brief_ruins" 
    },
    { 
      "id": "lead_refugees", 
      "text": "Tell me about the Refugee Camp.", 
      "next_state": "brief_refugees" 
    },
    { 
      "id": "done", 
      "text": "I'll start investigating.", 
      "next_state": "exit" 
    }
  ]
}
```

**B) Update brief_swamp state (REMOVE discovery flags):**
```json
"brief_swamp": {
  "introduction": [
    "There is an old chapel out in the marsh.",
    "Reports of lights and chanting at night.",
    "Meredith serves travelers - she hears all the rumors.",
    "Ask her about it."
  ],
  "options": [
    {
      "id": "noted",
      "text": "I'll ask around.",
      "effects": [
        { "type": "set_flag", "flag": "mayor_gave_swamp_info", "value": true }
      ],
      "next_state": "quest_given"
    }
  ]
}
```

**C) Update brief_ruins state:**
```json
"brief_ruins": {
  "introduction": [
    "Old and crumbling stones up on the nearby hill.",
    "Hunters say people vanish near the old arch.",
    "Garrick knows that area - miners used to explore up there.",
    "Talk to him."
  ],
  "options": [
    {
      "id": "noted",
      "text": "Got it.",
      "effects": [
        { "type": "set_flag", "flag": "mayor_gave_ruins_info", "value": true }
      ],
      "next_state": "quest_given"
    }
  ]
}
```

**D) Update brief_refugees state:**
```json
"brief_refugees": {
  "introduction": [
    "There is a camp by the south road.",
    "Full of frightened people having strange dreams.",
    "Missing campers too.",
    "Pete hangs around the tavern - he might know how to find them."
  ],
  "options": [
    {
      "id": "noted",
      "text": "I'll find Pete.",
      "effects": [
        { "type": "set_flag", "flag": "mayor_gave_refugee_info", "value": true }
      ],
      "next_state": "quest_given"
    }
  ]
}
```

**Testing Criteria:**
- [ ] Mayor no longer sets `*_discovered` flags directly
- [ ] Mayor only sets `mayor_gave_*_info` flags
- [ ] Player receives quest information but can't leave town yet
- [ ] Dialogue directs player to specific NPCs

### Task 2.2: Create redstone_town_mayor.json (Act II Version)

**File:** `data/dialogues/redstone_town_mayor.json` (NEW)

**Full State Machine:**

```json
{
  "id": "redstone_town_mayor",
  "npc_name": "Mayor Aldwin Goldenbottom",

  "states": {
    "entry_router": {
      "introduction": [],
      "options": [],
      "routing_logic": {
        "description": "This state uses schema routing to determine which state to show",
        "rules": [
          "IF all_complete -> ready_for_act_three",
          "IF any_acknowledged_but_not_all -> multiple_progress",
          "IF swamp_complete AND NOT acknowledged -> swamp_complete_first_time",
          "IF ruins_complete AND NOT acknowledged -> ruins_complete_first_time",
          "IF refugee_complete AND NOT acknowledged -> refugee_complete_first_time",
          "IF mine_complete AND NOT acknowledged -> mine_complete_first_time",
          "ELSE -> no_progress"
        ]
      }
    },

    "no_progress": {
      "introduction": [
        "*The Mayor looks up from his desk, worry etched on his face.*",
        "Any news? Every hour counts.",
        "The tremors are getting worse.",
        "Investigate the Swamp Church, the Hill Ruins, or the Refugee Camp.",
        "Find my family. Find out what is happening to Redstone."
      ],
      "options": [
        { 
          "id": "where_again", 
          "text": "Remind me where I should look.", 
          "next_state": "location_reminders" 
        },
        {
          "id": "ask_tremors",
          "text": "The tremors are definitely getting worse.",
          "next_state": "tremor_discussion"
        },
        { 
          "id": "bye", 
          "text": "I'm on it.", 
          "next_state": "exit" 
        }
      ]
    },

    "location_reminders": {
      "introduction": [
        "Three locations demand investigation:",
        "The Swamp Church - old chapel in the marsh, reports of lights.",
        "The Hill Ruins - ancient stones where people vanish.",
        "The Refugee Camp - displaced miners with strange dreams.",
        "Start wherever you think best."
      ],
      "options": [
        { "id": "back", "text": "Got it.", "next_state": "no_progress" }
      ]
    },

    "tremor_discussion": {
      "introduction": [
        "*He slams his fist on the desk.*",
        "Started weeks ago. Getting stronger every day.",
        "Miners say it is the old shafts settling.",
        "But the timing... right when people vanish?",
        "I do not believe in coincidences.",
        "Find what is taking our people.",
        "Maybe that will stop the tremors too."
      ],
      "options": [
        { 
          "id": "back", 
          "text": "I'll keep investigating.", 
          "next_state": "no_progress" 
        }
      ]
    },

    "swamp_complete_first_time": {
      "introduction": [
        "*His face pales as you describe what you found.*",
        "A cult? Operating right under our noses?",
        "Kidnapping our people for... for rituals?",
        "*He steadies himself against the desk.*",
        "This is worse than I feared.",
        "Thank you for uncovering this, but we are not done.",
        "Keep investigating. There must be more."
      ],
      "options": [
        {
          "id": "continue",
          "text": "I'll keep searching.",
          "effects": [
            { "type": "set_flag", "flag": "mayor_acknowledged_swamp_complete", "value": true }
          ],
          "next_state": "progress_check"
        }
      ]
    },

    "ruins_complete_first_time": {
      "introduction": [
        "*He listens intently to your report.*",
        "A portal? Some kind of... dimensional gateway?",
        "And it is sealed? Locked?",
        "*He runs his hand through his hair.*",
        "Whatever is beyond that door took my family.",
        "We need to find a way through.",
        "Keep investigating the other locations.",
        "Someone must know how to open it."
      ],
      "options": [
        {
          "id": "continue",
          "text": "I'll find a way.",
          "effects": [
            { "type": "set_flag", "flag": "mayor_acknowledged_ruins_complete", "value": true }
          ],
          "next_state": "progress_check"
        }
      ]
    },

    "refugee_complete_first_time": {
      "introduction": [
        "*He takes the key from you, examining it closely.*",
        "This... this is it. The key to the ruins.",
        "Those poor people were guarding it all along.",
        "*He looks up with grim determination.*",
        "Now we can reach the source of this corruption.",
        "But we must be certain we are ready.",
        "Make sure you have investigated everything.",
        "When you are ready, we end this."
      ],
      "options": [
        {
          "id": "continue",
          "text": "I'll make sure I'm prepared.",
          "effects": [
            { "type": "set_flag", "flag": "mayor_acknowledged_refugee_complete", "value": true }
          ],
          "next_state": "progress_check"
        }
      ]
    },

    "mine_complete_first_time": {
      "introduction": [
        "*He examines the ore samples you recovered.*",
        "This is what Henrik sealed away all those years ago.",
        "Strange energy... unnatural glow...",
        "*He sets them down carefully.*",
        "This ore must be connected to the portal somehow.",
        "Dimensional properties, perhaps.",
        "Thank you for investigating the mine.",
        "Every piece of information helps."
      ],
      "options": [
        {
          "id": "continue",
          "text": "Glad I could help.",
          "effects": [
            { "type": "set_flag", "flag": "mayor_acknowledged_mine_complete", "value": true }
          ],
          "next_state": "progress_check"
        }
      ]
    },

    "progress_check": {
      "introduction": [
        "Keep investigating.",
        "The more we know, the better our chances."
      ],
      "options": [
        { 
          "id": "where_next", 
          "text": "What should I focus on?", 
          "next_state": "location_status" 
        },
        { 
          "id": "bye", 
          "text": "I'm on it.", 
          "next_state": "exit" 
        }
      ]
    },

    "location_status": {
      "introduction": [
        "Let me think about what we know...",
        "*He reviews his notes.*"
      ],
      "options": [
        {
          "id": "check_swamp",
          "text": "What about the Swamp Church?",
          "requirements": {
            "flags": {
              "swamp_church_complete": false
            }
          },
          "next_state": "swamp_still_needed"
        },
        {
          "id": "check_ruins",
          "text": "And the Hill Ruins?",
          "requirements": {
            "flags": {
              "hill_ruins_complete": false
            }
          },
          "next_state": "ruins_still_needed"
        },
        {
          "id": "check_refugee",
          "text": "The Refugee Camp?",
          "requirements": {
            "flags": {
              "refugee_camp_complete": false
            }
          },
          "next_state": "refugee_still_needed"
        },
        {
          "id": "back", 
          "text": "Never mind, I'll figure it out.", 
          "next_state": "progress_check" 
        }
      ]
    },

    "swamp_still_needed": {
      "introduction": [
        "The Swamp Church is still a mystery.",
        "If there is cult activity there, we need to know."
      ],
      "options": [
        { "id": "back", "text": "I'll check it out.", "next_state": "progress_check" }
      ]
    },

    "ruins_still_needed": {
      "introduction": [
        "The Hill Ruins are the key to this whole thing.",
        "That is where the disappearances center.",
        "Whatever is there, we need to face it."
      ],
      "options": [
        { "id": "back", "text": "I'll investigate.", "next_state": "progress_check" }
      ]
    },

    "refugee_still_needed": {
      "introduction": [
        "The Refugee Camp might have survivors.",
        "People who escaped whatever is happening.",
        "They might know something crucial."
      ],
      "options": [
        { "id": "back", "text": "I'll go talk to them.", "next_state": "progress_check" }
      ]
    },

    "multiple_progress": {
      "introduction": [
        "*He looks more hopeful than before.*",
        "You are making real progress.",
        "The picture is becoming clearer.",
        "But we still need to know everything before we act."
      ],
      "options": [
        { 
          "id": "status", 
          "text": "What still needs investigating?", 
          "next_state": "location_status" 
        },
        { 
          "id": "bye", 
          "text": "I'll keep working on it.", 
          "next_state": "exit" 
        }
      ]
    },

    "ready_for_act_three": {
      "introduction": [
        "*He stands, resolve hardening in his eyes.*",
        "You have done it. We know what we face.",
        "A cult. A portal. My family taken beyond.",
        "*He grips your shoulder.*",
        "Now we end this.",
        "When you are ready, take the key to the ruins.",
        "I will gather what forces we have left.",
        "Bring my family home."
      ],
      "options": [
        {
          "id": "ready",
          "text": "I'm ready to finish this.",
          "effects": [
            { "type": "set_flag", "flag": "act_three_ready", "value": true }
          ],
          "next_state": "final_blessing"
        },
        {
          "id": "prepare",
          "text": "Let me prepare first.",
          "next_state": "exit"
        }
      ]
    },

    "final_blessing": {
      "introduction": [
        "*He nods solemnly.*",
        "Go with my blessing.",
        "May the gods watch over you.",
        "Save Redstone."
      ],
      "options": [
        { "id": "depart", "text": "I will.", "next_state": "exit" }
      ]
    }
  }
}
```

**Testing Criteria:**
- [ ] Office mayor only appears when `act_two_started = true`
- [ ] Routing logic correctly identifies completion states
- [ ] Each location completion triggers unique dialogue
- [ ] Multiple completions show cumulative progress
- [ ] Ready state triggers when all locations complete

---

## 🔧 PHASE 3: PRIMARY NPC DISCOVERY DIALOGUES

### Task 3.1: Update Meredith - Swamp Church Discovery

**File:** `data/dialogues/broken_blade_meredith.json`

**Modify the knows_about_swamp state:**

```json
"knows_about_swamp": {
  "introduction": [
    "There is an old church out in the swamp.",
    "Folks say lights move out there at night.",
    "People who go poking around sometimes do not come back."
  ],
  "options": [
    {
      "id": "mark_map",
      "text": "Can you mark it on my map?",
      "effects": [
        { "type": "set_flag", "flag": "meredith_gave_swamp_info", "value": true },
        { "type": "set_flag", "flag": "swamp_church_discovered", "value": true }
      ],
      "next_state": "marked_swamp"
    },
    {
      "id": "ask_mayor",
      "text": "Should I tell the Mayor about this?",
      "effects": [
        { "type": "set_flag", "flag": "meredith_mentioned_mayor", "value": true }
      ],
      "next_state": "mayor_knows"
    },
    { 
      "id": "bye", 
      "text": "Thanks for the warning.", 
      "next_state": "exit" 
    }
  ]
}
```

**Add new state:**
```json
"marked_swamp": {
  "introduction": [
    "*She sketches directions on a scrap of parchment.*",
    "South road, then west into the marsh.",
    "Follow the old stone markers.",
    "Be careful. The ground is treacherous."
  ],
  "options": [
    { "id": "thanks", "text": "Thank you.", "next_state": "exit" }
  ]
}
```

### Task 3.2: Update Garrick - Hill Ruins Discovery

**File:** `data/dialogues/broken_blade_garrick.json`

**Add ruins discovery path (find existing state or create new):**

```json
"knows_about_ruins": {
  "introduction": [
    "Aye, the old ruins up on the hill.",
    "Used to be a watchtower, centuries back.",
    "Hunters avoid it now. Strange lights at night.",
    "Folks who go up there... some do not come back."
  ],
  "options": [
    {
      "id": "mark_map",
      "text": "Show me where it is.",
      "effects": [
        { "type": "set_flag", "flag": "garrick_gave_ruins_info", "value": true },
        { "type": "set_flag", "flag": "hill_ruins_discovered", "value": true }
      ],
      "next_state": "marked_ruins"
    },
    {
      "id": "more_info",
      "text": "What kind of strange lights?",
      "next_state": "ruins_details"
    },
    { 
      "id": "bye", 
      "text": "Interesting.", 
      "next_state": "exit" 
    }
  ]
}
```

**Add supporting states:**
```json
"marked_ruins": {
  "introduction": [
    "Take the north road out of town.",
    "You will see the hill to the east.",
    "Path is overgrown but still there.",
    "Watch yourself up there."
  ],
  "options": [
    { "id": "thanks", "text": "Thanks for the information.", "next_state": "exit" }
  ]
},

"ruins_details": {
  "introduction": [
    "Purple lights, some say. Green others claim.",
    "Depends on who is drinking and how much.",
    "*He leans in.*",
    "But the tremors... those started around the same time.",
    "Make of that what you will."
  ],
  "options": [
    {
      "id": "mark_map",
      "text": "I should check this out. Show me where.",
      "effects": [
        { "type": "set_flag", "flag": "garrick_gave_ruins_info", "value": true },
        { "type": "set_flag", "flag": "hill_ruins_discovered", "value": true }
      ],
      "next_state": "marked_ruins"
    },
    { "id": "bye", "text": "Thanks for the warning.", "next_state": "exit" }
  ]
}
```

### Task 3.3: Update Pete - Refugee Camp Discovery

**File:** `data/dialogues/broken_blade_pete.json`

**Create refugee camp discovery path:**

```json
"knows_about_refugees": {
  "introduction": [
    "*Pete leans in conspiratorially.*",
    "There is a camp. South of town, off the main road.",
    "Miners who fled the sealed shafts.",
    "They are scared. Real scared.",
    "Talk about nightmares and... and things in the dark."
  ],
  "options": [
    {
      "id": "mark_map",
      "text": "Can you tell me how to find them?",
      "effects": [
        { "type": "set_flag", "flag": "pete_gave_refugee_info", "value": true },
        { "type": "set_flag", "flag": "refugee_camp_discovered", "value": true }
      ],
      "next_state": "marked_refugee"
    },
    {
      "id": "nightmares",
      "text": "What kind of nightmares?",
      "next_state": "nightmare_details"
    },
    { 
      "id": "bye", 
      "text": "That is troubling.", 
      "next_state": "exit" 
    }
  ]
}
```

**Add supporting states:**
```json
"marked_refugee": {
  "introduction": [
    "South road, about a mile out.",
    "Look for cooking fires off to the west.",
    "They are wary of strangers, but...",
    "Tell them Pete sent you. They know me."
  ],
  "options": [
    { "id": "thanks", "text": "Thanks, Pete.", "next_state": "exit" }
  ]
},

"nightmare_details": {
  "introduction": [
    "*He shudders.*",
    "Dark figures. Chanting. Being pulled down...",
    "They wake up screaming.",
    "Some of them... they just vanish from the camp.",
    "In the middle of the night. Gone."
  ],
  "options": [
    {
      "id": "help_them",
      "text": "I need to help them. Show me where.",
      "effects": [
        { "type": "set_flag", "flag": "pete_gave_refugee_info", "value": true },
        { "type": "set_flag", "flag": "refugee_camp_discovered", "value": true }
      ],
      "next_state": "marked_refugee"
    },
    { "id": "bye", "text": "I see.", "next_state": "exit" }
  ]
}
```

**Testing Criteria:**
- [ ] Meredith discovers swamp church
- [ ] Garrick discovers hill ruins
- [ ] Pete discovers refugee camp
- [ ] Each sets both `npc_gave_info` and `location_discovered` flags
- [ ] South Gate becomes accessible after any discovery

---

## 🔧 PHASE 4: BACKUP NPC DISCOVERY DIALOGUES

### Task 4.1: Bernard - Hill Ruins Backup

**File:** `data/dialogues/[bernard_location]_bernard.json`

**Add ruins discovery as alternate conversation path:**

```json
"ruins_conversation": {
  "introduction": [
    "The Hill Ruins? Aye, I know of them.",
    "Sell supplies to hunters who work that area.",
    "Well... used to, anyway.",
    "They stopped going up there a few weeks back.",
    "Said it felt... wrong."
  ],
  "options": [
    {
      "id": "tell_me_more",
      "text": "Wrong how?",
      "next_state": "ruins_wrong"
    },
    {
      "id": "mark_map",
      "text": "Can you point me there?",
      "requirements": {
        "flags": {
          "hill_ruins_discovered": false
        }
      },
      "effects": [
        { "type": "set_flag", "flag": "bernard_gave_ruins_info", "value": true },
        { "type": "set_flag", "flag": "hill_ruins_discovered", "value": true }
      ],
      "next_state": "marked_ruins"
    },
    { "id": "bye", "text": "Interesting.", "next_state": "exit" }
  ]
}
```

### Task 4.2: Cassia - Swamp Church Backup

**File:** `data/dialogues/violet_mortar_cassia.json`

**Add swamp discovery conversation:**

```json
"swamp_conversation": {
  "introduction": [
    "The marsh? I gather herbs there sometimes.",
    "Or... I used to.",
    "*Her expression darkens.*",
    "There is an old church deep in the swamp.",
    "Lately, I hear chanting when I am near it.",
    "And the herbs around it... they are dying."
  ],
  "options": [
    {
      "id": "chanting",
      "text": "What kind of chanting?",
      "next_state": "chanting_details"
    },
    {
      "id": "mark_map",
      "text": "Can you show me where this church is?",
      "requirements": {
        "flags": {
          "swamp_church_discovered": false
        }
      },
      "effects": [
        { "type": "set_flag", "flag": "cassia_gave_swamp_info", "value": true },
        { "type": "set_flag", "flag": "swamp_church_discovered", "value": true }
      ],
      "next_state": "marked_swamp"
    },
    { "id": "bye", "text": "That sounds dangerous.", "next_state": "exit" }
  ]
},

"chanting_details": {
  "introduction": [
    "*She wraps her arms around herself.*",
    "Voices. Multiple voices. In a language I do not know.",
    "It reminds me of... of when Marcus changed.",
    "Before he left.",
    "*She looks away.*",
    "Dangerous people. That is what he got involved with."
  ],
  "options": [
    {
      "id": "help",
      "text": "I'll investigate. Show me where.",
      "requirements": {
        "flags": {
          "swamp_church_discovered": false
        }
      },
      "effects": [
        { "type": "set_flag", "flag": "cassia_gave_swamp_info", "value": true },
        { "type": "set_flag", "flag": "swamp_church_discovered", "value": true }
      ],
      "next_state": "marked_swamp"
    },
    { "id": "sorry", "text": "I'm sorry about Marcus.", "next_state": "marcus_sympathy" }
  ]
}
```

**NOTE:** This creates excellent foreshadowing for Cassia's Act III reveal about Marcus being involved with the cult!

### Task 4.3: Jenna - Refugee Camp Backup

**File:** `data/dialogues/[jenna_location]_jenna.json`

**Add refugee discovery conversation:**

```json
"refugee_conversation": {
  "introduction": [
    "Oh, the poor souls at the camp.",
    "I have tried to send supplies, but...",
    "*She sighs.*",
    "They need more than food and blankets.",
    "They need someone to figure out what is happening to them."
  ],
  "options": [
    {
      "id": "happening",
      "text": "What is happening to them?",
      "next_state": "refugee_problems"
    },
    {
      "id": "mark_map",
      "text": "Where can I find this camp?",
      "requirements": {
        "flags": {
          "refugee_camp_discovered": false
        }
      },
      "effects": [
        { "type": "set_flag", "flag": "jenna_gave_refugee_info", "value": true },
        { "type": "set_flag", "flag": "refugee_camp_discovered", "value": true }
      ],
      "next_state": "marked_refugee"
    },
    { "id": "bye", "text": "I see.", "next_state": "exit" }
  ]
}
```

**Testing Criteria:**
- [ ] Bernard can discover ruins if Garrick path missed
- [ ] Cassia can discover swamp if Meredith path missed
- [ ] Jenna can discover refugee if Pete path missed
- [ ] Backup dialogues have unique flavor and character voice
- [ ] All set same discovery flags as primary sources

---

## 🔧 PHASE 5: MAYOR LOCATION ROUTING & SOUTH GATE

### Task 5.1: Mayor Location Routing Logic

**File:** `game_logic/dialogue_engine.py` or appropriate location handler

**Add routing function:**

```python
def get_mayor_dialogue_context(self, game_state):
    """
    Determines which mayor dialogue file to use based on act progression.
    
    Returns:
        dict: Contains dialogue_file and location information
    """
    if game_state.get_flag('act_two_started'):
        return {
            'dialogue_file': 'redstone_town_mayor',
            'location': 'redstone_town',
            'display_name': "Mayor's Office"
        }
    else:
        return {
            'dialogue_file': 'patron_selection_mayor',
            'location': 'broken_blade',
            'display_name': 'The Broken Blade'
        }
```

**Add to NPC interaction handler:**

```python
def start_npc_dialogue(self, npc_id):
    """Handle NPC dialogue with special routing for Mayor."""
    
    if npc_id == 'mayor':
        context = self.get_mayor_dialogue_context(self.game_state)
        dialogue_file = context['dialogue_file']
    else:
        # Normal NPC lookup
        npc_data = self.narrative_schema.get_npc(npc_id)
        dialogue_file = npc_data.get('dialogue_file')
    
    # Load and start dialogue
    self.load_dialogue(dialogue_file)
    # ... rest of dialogue initialization
```

### Task 5.2: Update South Gate Conditions

**File:** `data/maps/redstone_town_map.py`

**Update south_gate definition:**

```python
'south_gate': {
    'building_pos': (7, 12),
    'entrance_tiles': [(7, 11)],  # Tile just north of south gate
    'info': {
        'name': "South Town Gate",
        'interaction_type': 'conditional_transition',
        
        # Requirements to unlock gate
        'requirements': {
            'flags': ['quest_active'],  # Must have accepted mayor's quest
            'any_of': [  # AND at least ONE location discovered
                'swamp_church_discovered',
                'hill_ruins_discovered', 
                'refugee_camp_discovered',
                'red_hollow_mine_discovered'
            ],
            'failure_message': "The guards at the gate stop you.\n\n'Mayor's orders - no one leaves until we have solid leads. Talk to the folks at the Broken Blade if you need information.'"
        },
        
        # Which screen to show
        'flag_check': 'act_two_started',
        'if_true_screen': 'exploration_hub',      # Already seen Act II intro
        'if_false_screen': 'act_two_start',       # First time - show intro
        'action': 'Begin Investigation'
    }
}
```

**Implementation Notes:**
- If `conditional_transition` doesn't exist, you may need to implement this interaction type
- Alternative: Use two different interaction handlers based on requirements check
- Failure message prevents player from leaving before they have leads

### Task 5.3: Ensure act_two_start Sets Flag

**File:** `screens/act_two_transition.py` (or wherever Act II transition is handled)

**Verify the transition screen sets the flag:**

```python
def on_continue_button():
    """Handle continue button press from Act II intro."""
    # Set the flag so Mayor moves to office
    game_state.set_flag('act_two_started', True)
    
    # Save this progress
    save_manager.save_game(game_state, 'auto_act_two')
    
    # Transition to exploration hub
    screen_manager.transition_to('exploration_hub')
```

**Testing Criteria:**
- [ ] Mayor appears in tavern before `act_two_started`
- [ ] Mayor appears in office after `act_two_started`
- [ ] South Gate blocks player without quest + discovery
- [ ] South Gate shows Act II intro on first exit
- [ ] South Gate goes straight to exploration hub on subsequent exits
- [ ] Flag persists through save/load

---

## 🔧 PHASE 6: MAYOR ROUTING IN NARRATIVE SCHEMA

### Task 6.1: Add Schema Routing Rules

**File:** `data/dialogues/redstone_town_mayor.json`

**Add routing metadata to entry_router state:**

```json
"entry_router": {
  "introduction": [],
  "options": [],
  "schema_routing": {
    "type": "conditional_router",
    "routes": [
      {
        "conditions": {
          "all_of": [
            { "flag": "swamp_church_complete", "value": true },
            { "flag": "hill_ruins_complete", "value": true },
            { "flag": "refugee_camp_complete", "value": true }
          ]
        },
        "target_state": "ready_for_act_three",
        "priority": 1
      },
      {
        "conditions": {
          "any_of": [
            { "flag": "mayor_acknowledged_swamp_complete", "value": true },
            { "flag": "mayor_acknowledged_ruins_complete", "value": true },
            { "flag": "mayor_acknowledged_refugee_complete", "value": true }
          ]
        },
        "target_state": "multiple_progress",
        "priority": 2
      },
      {
        "conditions": {
          "all_of": [
            { "flag": "swamp_church_complete", "value": true },
            { "flag": "mayor_acknowledged_swamp_complete", "value": false }
          ]
        },
        "target_state": "swamp_complete_first_time",
        "priority": 3
      },
      {
        "conditions": {
          "all_of": [
            { "flag": "hill_ruins_complete", "value": true },
            { "flag": "mayor_acknowledged_ruins_complete", "value": false }
          ]
        },
        "target_state": "ruins_complete_first_time",
        "priority": 3
      },
      {
        "conditions": {
          "all_of": [
            { "flag": "refugee_camp_complete", "value": true },
            { "flag": "mayor_acknowledged_refugee_complete", "value": false }
          ]
        },
        "target_state": "refugee_complete_first_time",
        "priority": 3
      },
      {
        "conditions": {
          "all_of": [
            { "flag": "red_hollow_mine_complete", "value": true },
            { "flag": "mayor_acknowledged_mine_complete", "value": false }
          ]
        },
        "target_state": "mine_complete_first_time",
        "priority": 4
      },
      {
        "conditions": {},
        "target_state": "no_progress",
        "priority": 999
      }
    ]
  }
}
```

**NOTE:** This routing structure assumes your DialogueEngine supports schema-based routing. If not, you may need to implement this in the dialogue engine itself.

---

## ✅ TESTING CHECKLIST

### Phase 1 Testing: Schema & Flags
- [ ] All discovery flags initialize to false
- [ ] All completion flags initialize to false  
- [ ] All NPC info flags initialize to false
- [ ] act_two_started flag initializes to false
- [ ] Save/load preserves all flag states
- [ ] No crashes when accessing any flag

### Phase 2 Testing: Mayor Dialogue Changes
- [ ] Mayor in tavern gives quest without discoveries
- [ ] Mayor directs player to specific NPCs
- [ ] Mayor office dialogue loads when act_two_started = true
- [ ] Office dialogue routing works correctly
- [ ] Each completion triggers unique first-time dialogue
- [ ] Acknowledgment flags prevent repeat first-time dialogue
- [ ] Ready state triggers with all completions

### Phase 3 Testing: Primary NPC Discovery
- [ ] Meredith can discover swamp church
- [ ] Garrick can discover hill ruins
- [ ] Pete can discover refugee camp
- [ ] Each sets both NPC and location flags
- [ ] Discovery enables South Gate if quest active
- [ ] Multiple NPCs can give same location (no conflicts)

### Phase 4 Testing: Backup NPC Discovery
- [ ] Bernard provides ruins info if Garrick missed
- [ ] Cassia provides swamp info if Meredith missed
- [ ] Jenna provides refugee info if Pete missed
- [ ] Backup sources have unique dialogue flavor
- [ ] Requirements prevent duplicate discovery spam
- [ ] Player can't get "stuck" without location info

### Phase 5 Testing: Gate & Routing
- [ ] South Gate blocks without quest
- [ ] South Gate blocks with quest but no discoveries
- [ ] South Gate allows exit with quest + 1 discovery
- [ ] First exit shows Act II intro screen
- [ ] Subsequent exits go directly to exploration hub
- [ ] act_two_started flag persists correctly
- [ ] Mayor disappears from tavern after act_two_started
- [ ] Mayor appears in office after act_two_started

### End-to-End Testing
- [ ] Complete Act I → accept quest → discover locations → exit town
- [ ] Mayor moves to office → complete one location → return
- [ ] Mayor acknowledges completion → complete more → return
- [ ] Mayor ready state triggers → Act III accessible
- [ ] Save/load at each step preserves all progress
- [ ] Alternate discovery paths work (backup NPCs)

---

## 🚨 KNOWN ISSUES & TROUBLESHOOTING

### Issue: Mayor appears in both locations
**Cause:** Routing logic not checking act_two_started flag  
**Fix:** Verify mayor location routing function and that patron_selection removes mayor from NPC list when flag is true

### Issue: South Gate allows exit without discoveries
**Cause:** Conditional requirements not properly implemented  
**Fix:** Check that `any_of` logic works in interaction handler, may need custom implementation

### Issue: Discovery flags not setting
**Cause:** Dialogue effects not processing correctly  
**Fix:** Verify DialogueEngine.process_effects() handles set_flag effect type

### Issue: Routing shows wrong dialogue state
**Cause:** Priority order incorrect or flag checks wrong  
**Fix:** Review schema_routing priority values, ensure highest priority routes checked first

### Issue: Player can't find backup NPCs
**Cause:** Backup NPCs not visible or dialogue paths hidden  
**Fix:** Ensure backup NPCs have visible dialogue options, not hidden behind requirements

---

## 📊 IMPLEMENTATION ORDER SUMMARY

**SESSION 1: Foundation** (2-3 hours)
1. Update narrative_schema.json with all new flags
2. Update patron_selection_mayor.json (remove discoveries)
3. Test Mayor Act I behavior

**SESSION 2: Mayor Office** (2-3 hours)
1. Create redstone_town_mayor.json with full state machine
2. Implement mayor location routing logic
3. Test Act II transition and mayor movement

**SESSION 3: Primary Discovery** (2 hours)
1. Update Meredith dialogue (swamp)
2. Update Garrick dialogue (ruins)
3. Update/Create Pete dialogue (refugee)
4. Test all three discovery paths

**SESSION 4: Backup Discovery** (2 hours)
1. Add Bernard dialogue (ruins backup)
2. Add Cassia dialogue (swamp backup)
3. Add Jenna dialogue (refugee backup)
4. Test backup discovery redundancy

**SESSION 5: Gate & Polish** (1-2 hours)
1. Update South Gate with requirements
2. Verify act_two_started flag integration
3. End-to-end testing
4. Bug fixes and polish

**TOTAL ESTIMATED TIME:** 9-12 hours

---

## 📝 NOTES FOR FUTURE DEVELOPERS

### Design Philosophy
This system follows classic CRPG design patterns:
- **Redundancy:** Multiple information sources prevent getting stuck
- **Discovery:** Rewards thorough exploration and NPC interaction
- **Progress:** Mayor dialogue reflects player achievements
- **Gating:** Prevents premature exploration while allowing flexibility

### Expansion Points
To add more locations:
1. Add discovery/completion flags to narrative_schema.json
2. Create discovery dialogue path in NPC files
3. Add completion acknowledgment state in redstone_town_mayor.json
4. Update exploration_hub.json with new location button

### Technical Debt
- Schema routing system may need implementation if not present
- Conditional transitions may need custom interaction handler
- Mayor portrait swap (tavern vs office) not addressed in this plan

### Related Systems
- **Exploration Hub:** Needs location buttons with discovery requirements
- **Location Completion:** Each location must set completion flags
- **Quest System:** Should integrate with Mayor progress tracking
- **Act III Trigger:** Depends on act_three_ready flag

---

## 🎯 SUCCESS CRITERIA

Implementation is complete when:
1. ✅ Player cannot leave town without quest + discoveries
2. ✅ Multiple NPCs can provide same location information
3. ✅ Mayor moves from tavern to office after Act II begins
4. ✅ Mayor dialogue reflects specific location completions
5. ✅ All flags persist through save/load
6. ✅ No way for player to get stuck
7. ✅ Smooth transition from Act I to Act II to Act III

---

**END OF IMPLEMENTATION PLAN**

*This document is ready for any developer to pick up and continue implementation. All design decisions are documented, all code snippets are provided, and all testing criteria are defined.*

*Good luck, and may your D20 rolls be high! 🎲*