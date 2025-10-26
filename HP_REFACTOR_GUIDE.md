# HP Variable Refactoring Guide

## Overview
This refactor standardizes HP variable naming across player and NPCs to eliminate recurring bugs.

**Current Problem:**
- Player uses: `hit_points` (max) + `current_hp` (current)
- NPCs use: `max_hit_points` (max) + `current_hp` (current)

**Solution:**
- Both use: `max_hp` (max) + `current_hp` (current)

---

## File Changes

### 1. game_state.py

**Lines 51-56:** Change player character initialization
```python
# OLD:
            # Progression tracking
            'level': 1,
            'experience': 0,
            'hit_points': 10,   #Max hip points
            'current_hp': 10,   #Current hip points
            'max_hp'
            'abilities': [],

# NEW:
            # Progression tracking
            'level': 1,
            'experience': 0,
            'max_hp': 10,       # Maximum hit points
            'current_hp': 10,   # Current hit points
            'abilities': [],
```

**Lines 257-262:** Change NPC initialization
```python
# OLD:
            'level': npc_template.get('level', 1),
            'experience': 0,  # Start at 0 XP
            'hp': npc_hp,  # Use 'hp' to match NPC JSON format
            'hit_points': npc_hp,  # Also store as hit_points for compatibility
            'current_hp': npc_hp,  # Initialize current HP to max! ← CRITICAL FIX
            'max_hit_points': npc_hp,
            'ac': npc_ac,  # Store AC from NPC JSON

# NEW:
            'level': npc_template.get('level', 1),
            'experience': 0,  # Start at 0 XP
            'max_hp': npc_hp,  # Maximum hit points (standardized)
            'current_hp': npc_hp,  # Current hit points (initialize to max)
            'ac': npc_ac,  # Store AC from NPC JSON
```

**Line 359:** Change get_character_summary
```python
# OLD:
            'hit_points': self.character.get('hit_points', 10),

# NEW:
            'max_hp': self.character.get('max_hp', 10),
```

---

### 2. data/templates/player_template.json

**Lines 28-34:** Flatten hit_points structure
```json
// OLD:
  "progression": {
    "level": 1,
    "experience": 0,
    "hit_points": {
      "current": 10,
      "maximum": 10
    }
  },

// NEW:
  "progression": {
    "level": 1,
    "experience": 0,
    "max_hp": 10,
    "current_hp": 10
  },
```

---

### 3. data/player/current_character.json

**Lines 28-34:** Same change as player_template.json
```json
// OLD:
  "progression": {
    "level": 1,
    "experience": 0,
    "hit_points": {
      "current": 11,
      "maximum": 11
    }
  },

// NEW:
  "progression": {
    "level": 1,
    "experience": 0,
    "max_hp": 11,
    "current_hp": 11
  },
```

---

### 4. game_logic/player_managers.py

**Lines 81-84:** Update player creation
```python
# OLD:
            # Hit points and derived stats
            hit_points = character_data.get('hit_points', 10)
            player_template['progression']['hit_points']['current'] = hit_points
            player_template['progression']['hit_points']['maximum'] = hit_points

# NEW:
            # Hit points and derived stats
            hit_points = character_data.get('max_hp', 10)
            player_template['progression']['max_hp'] = hit_points
            player_template['progression']['current_hp'] = hit_points
```

**Lines 210-216:** Update get_player_data_for_combat
```python
# OLD:
            'name': self.get_player_name(),
            'class': self.player_data.get('class', 'fighter'),
            'stats': self.get_player_stats(),
            'equipment': self.get_player_equipment(),
            'hit_points': self.player_data.get('progression', {}).get('hit_points', {}),
            'is_player': True
        }

# NEW:
            'name': self.get_player_name(),
            'class': self.player_data.get('class', 'fighter'),
            'stats': self.get_player_stats(),
            'equipment': self.get_player_equipment(),
            'max_hp': self.player_data.get('progression', {}).get('max_hp', 10),
            'current_hp': self.player_data.get('progression', {}).get('current_hp', 10),
            'is_player': True
        }
```

**Lines 227-234:** Update sync_with_game_state
```python
# OLD:
        # Update game_state.character with JSON data
        game_state.character.update({
            'name': self.player_data.get('name'),
            'gender': self.player_data.get('player_data', {}).get('gender'),
            'trinket': self.player_data.get('player_data', {}).get('trinket'),
            'hit_points': self.player_data.get('progression', {}).get('hit_points', {}).get('maximum', 10),
            'gold': self.player_data.get('inventory', {}).get('gold', 0),
            **self.player_data.get('stats', {})
        })

# NEW:
        # Update game_state.character with JSON data
        game_state.character.update({
            'name': self.player_data.get('name'),
            'gender': self.player_data.get('player_data', {}).get('gender'),
            'trinket': self.player_data.get('player_data', {}).get('trinket'),
            'max_hp': self.player_data.get('progression', {}).get('max_hp', 10),
            'current_hp': self.player_data.get('progression', {}).get('current_hp', 10),
            'gold': self.player_data.get('inventory', {}).get('gold', 0),
            **self.player_data.get('stats', {})
        })
```

**Lines 359-368:** Update update_hit_points method
```python
# OLD:
    def update_hit_points(self, current_hp, max_hp=None):
        """Update player hit points and save immediately"""
        if self.player_data:
            self.player_data['progression']['hit_points']['current'] = current_hp
            if max_hp is not None:
                self.player_data['progression']['hit_points']['maximum'] = max_hp
            self.save_player()
            print(f"❤️ Hit points updated: {current_hp}")
            return True
        return False

# NEW:
    def update_hit_points(self, current_hp, max_hp=None):
        """Update player hit points and save immediately"""
        if self.player_data:
            self.player_data['progression']['current_hp'] = current_hp
            if max_hp is not None:
                self.player_data['progression']['max_hp'] = max_hp
            self.save_player()
            print(f"❤️ Hit points updated: {current_hp}")
            return True
        return False
```

---

### 5. game_logic/character_engine.py

**Lines 874-876:** Update calculate_hp
```python
# OLD:
        # Update GameState directly (Single Data Authority)
        self.game_state.character['hit_points'] = hit_points #max hit points
        self.game_state.character['current_hp'] = hit_points

# NEW:
        # Update GameState directly (Single Data Authority)
        self.game_state.character['max_hp'] = hit_points  # Maximum hit points
        self.game_state.character['current_hp'] = hit_points  # Current hit points
```

**Lines 1170-1175:** Update level_up_player
```python
# OLD:
        # Increase max HP
        current_max = self.game_state.character.get('hit_points', 10)
        self.game_state.character['hit_points'] = current_max + hp_gain

         # Level ups fully restore health to the new maximum
        self.game_state.character['current_hp'] = self.game_state.character['hit_points']

# NEW:
        # Increase max HP
        current_max = self.game_state.character.get('max_hp', 10)
        self.game_state.character['max_hp'] = current_max + hp_gain

         # Level ups fully restore health to the new maximum
        self.game_state.character['current_hp'] = self.game_state.character['max_hp']
```

**Line 1185:** Update level_up_player return value
```python
# OLD:
            'new_total_hp': self.game_state.character['hit_points'],

# NEW:
            'new_total_hp': self.game_state.character['max_hp'],
```

**Lines 1357-1361:** Update _award_party_member_xp
```python
# OLD:
        if member_id not in self.game_state.party_xp:
            self.game_state.party_xp[member_id] = {
                'experience': 0,
                'level': 1,
                'hit_points': self._get_party_member_starting_hp(member_id)
            }

# NEW:
        if member_id not in self.game_state.party_xp:
            self.game_state.party_xp[member_id] = {
                'experience': 0,
                'level': 1,
                'max_hp': self._get_party_member_starting_hp(member_id)
            }
```

**Lines 1523-1543:** Update _level_up_party_member
```python
# OLD:
        # Get OLD max HP (not current HP!)
        old_max_hp = member_data.get('hit_points', member_data.get('hp', 10))

        # Calculate NEW max HP
        new_max_hp = old_max_hp + hp_gain

        # Update all HP fields to new maximum
        member_data['hit_points'] = new_max_hp
        member_data['hp'] = new_max_hp
        member_data['max_hit_points'] = new_max_hp

        # Full heal on level up (same as player)
        member_data['current_hp'] = new_max_hp

        print(f"🎊 {member_id.title()} leveled up! Now level {new_level}, gained {hp_gain} HP to Max HP {new_max_hp}")

        return {
            'member_id': member_id,
            'new_level': new_level,
            'hp_gain': hp_gain,
            'new_total_hp': member_data['hit_points']
        }

# NEW:
        # Get OLD max HP (not current HP!)
        old_max_hp = member_data.get('max_hp', 10)

        # Calculate NEW max HP
        new_max_hp = old_max_hp + hp_gain

        # Update max HP
        member_data['max_hp'] = new_max_hp

        # Full heal on level up (same as player)
        member_data['current_hp'] = new_max_hp

        print(f"🎊 {member_id.title()} leveled up! Now level {new_level}, gained {hp_gain} HP to Max HP {new_max_hp}")

        return {
            'member_id': member_id,
            'new_level': new_level,
            'hp_gain': hp_gain,
            'new_total_hp': member_data['max_hp']
        }
```

**Lines 1603-1604:** Update validate_character_data
```python
# OLD:
        required_fields = ['name', 'class', 'strength', 'dexterity', 'constitution',
                          'intelligence', 'wisdom', 'charisma', 'hit_points', 'gold']

# NEW:
        required_fields = ['name', 'class', 'strength', 'dexterity', 'constitution',
                          'intelligence', 'wisdom', 'charisma', 'max_hp', 'gold']
```

**Lines 1705-1706:** Update finalize_character_creation
```python
# OLD:
        # Calculate class-specific starting stats
        if 'hit_points' not in self.game_state.character:
            self.calculate_hp()

# NEW:
        # Calculate class-specific starting stats
        if 'max_hp' not in self.game_state.character:
            self.calculate_hp()
```

---

### 6. game_logic/combat_engine.py

**Line 230:** Update start_combat autosave
```python
# OLD:
                    max_hp = self.game_state.character.get("hit_points", 10)

# NEW:
                    max_hp = self.game_state.character.get("max_hp", 10)
```

**Line 263:** Update start_combat HP initialization
```python
# OLD:
                max_hp = self.game_state.character.get('hit_points', 10)

# NEW:
                max_hp = self.game_state.character.get('max_hp', 10)
```

**Lines 801-803:** Update _build_party_list
```python
# OLD:
            'current_hp': self.game_state.character.get('current_hp',
                                                        self.game_state.character.get('hit_points', 20)),
            'max_hp': self.game_state.character.get('hit_points', 20),

# NEW:
            'current_hp': self.game_state.character.get('current_hp',
                                                        self.game_state.character.get('max_hp', 20)),
            'max_hp': self.game_state.character.get('max_hp', 20),
```

**Lines 816-817:** Update _build_party_list for NPCs
```python
# OLD:
            # Read HP from member data (initialized in game_state)
            max_hp = member_data.get('hp', member_data.get('hit_points', 20))
            current_hp = member_data.get('current_hp', max_hp)

# NEW:
            # Read HP from member data (initialized in game_state)
            max_hp = member_data.get('max_hp', 20)
            current_hp = member_data.get('current_hp', max_hp)
```

**Lines 857-862:** Update get_character_at_position
```python
# OLD:
                # Get HP from correct source
                if char_id == 'player':
                    current_hp = self.game_state.character.get('current_hp', 10)
                    max_hp = self.game_state.character.get('hit_points', 10)
                else:
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('max_hp', 10)

# NEW:
                # Get HP from correct source
                if char_id == 'player':
                    current_hp = self.game_state.character.get('current_hp', 10)
                    max_hp = self.game_state.character.get('max_hp', 10)
                else:
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('max_hp', 10)
```

**Line 2383:** Update _resolve_spell_damage
```python
# OLD:
                            max_hp = self.game_state.character.get("hit_points", 0)

# NEW:
                            max_hp = self.game_state.character.get("max_hp", 0)
```

**Line 2718:** Update _handle_combat_defeat
```python
# OLD:
                max_hp = self.game_state.character.get("hit_points", 10)

# NEW:
                max_hp = self.game_state.character.get("max_hp", 10)
```

---

### 7. game_logic/combat_ai.py

**Lines 814-819:** Update _select_melee_target
```python
# OLD:
                # Get current HP
                if char_id == 'player':
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('hit_points', char_data.get('max_hp', 10))
                else:
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('max_hp', char_data.get('hit_points', 10))

# NEW:
                # Get current HP
                if char_id == 'player':
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('max_hp', 10)
                else:
                    current_hp = char_data.get('current_hp', 10)
                    max_hp = char_data.get('max_hp', 10)
```

**Lines 1208-1215:** Update _find_weakest_target
```python
# OLD:
            if char_id == 'player':
                # Player character - might need special handling
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('hit_points', char_data.get('max_hp', 10))
            else:
                # Party member
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('max_hp', char_data.get('hit_points', 10))

# NEW:
            if char_id == 'player':
                # Player character - might need special handling
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('max_hp', 10)
            else:
                # Party member
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('max_hp', 10)
```

---

### 8. screens/character_overlay.py

**Lines 200-214:** Update draw_character_overlay
```python
# OLD:
        # Hit Points (current/max format)
        max_hp = character.get('hit_points', 10)
        current_hp = character.get('current_hp', 10)
        HP_label = normal_font.render("Hit Points: ", True, WHITE)
        surface.blit(HP_label, (left_section_x, current_y))
        hp_percent = (current_hp / max_hp *100) if max_hp > 0 else 0

        if hp_percent > 66:
            hp_color = BRIGHT_GREEN
        elif hp_percent > 33:
            hp_color = SOFT_YELLOW
        else:
            hp_color = RED

        max_hp = character.get('hit_points', 10)
        value_surface = normal_font.render(f" {current_hp}/{max_hp}", True, hp_color)
        surface.blit(value_surface, (left_section_x + HP_label.get_width(), current_y))

# NEW:
        # Hit Points (current/max format)
        max_hp = character.get('max_hp', 10)
        current_hp = character.get('current_hp', 10)
        HP_label = normal_font.render("Hit Points: ", True, WHITE)
        surface.blit(HP_label, (left_section_x, current_y))
        hp_percent = (current_hp / max_hp *100) if max_hp > 0 else 0

        if hp_percent > 66:
            hp_color = BRIGHT_GREEN
        elif hp_percent > 33:
            hp_color = SOFT_YELLOW
        else:
            hp_color = RED

        value_surface = normal_font.render(f" {current_hp}/{max_hp}", True, hp_color)
        surface.blit(value_surface, (left_section_x + HP_label.get_width(), current_y))
```

**Lines 636-638:** Update draw_party_member_overlay
```python
# OLD:
            # HP with color coding
            current_hp = npc_info.get('current_hp', npc_info.get('hp', 0))
            max_hp = npc_info.get('hp', npc_info.get('hit_points', 0))
            hp_percent = (current_hp / max_hp * 100) if max_hp > 0 else 0

# NEW:
            # HP with color coding
            current_hp = npc_info.get('current_hp', 0)
            max_hp = npc_info.get('max_hp', 0)
            hp_percent = (current_hp / max_hp * 100) if max_hp > 0 else 0
```

---

### 9. screens/character_creation.py

**Line 600:** Update draw_character_summary
```python
# OLD:
    hit_points = game_state.character.get('hit_points', 'Calculating...')

# NEW:
    hit_points = game_state.character.get('max_hp', 'Calculating...')
```

---

### 10. utils/party_display.py

**Lines 86-96:** Update _draw_hp_bar_under_portrait
```python
# OLD:
    # Get HP values
    if is_player:
        current_hp = game_state.character.get('current_hp', 10)
        max_hp = game_state.character.get('hit_points', 10)
    else:
        # Find party member data
        current_hp = 10
        max_hp = 10
        for member in game_state.party_member_data:
            if member.get('id') == character_name:
                current_hp = member.get('current_hp', 10)
                max_hp = member.get('hp', member.get('hit_points', 10))
                break

# NEW:
    # Get HP values
    if is_player:
        current_hp = game_state.character.get('current_hp', 10)
        max_hp = game_state.character.get('max_hp', 10)
    else:
        # Find party member data
        current_hp = 10
        max_hp = 10
        for member in game_state.party_member_data:
            if member.get('id') == character_name:
                current_hp = member.get('current_hp', 10)
                max_hp = member.get('max_hp', 10)
                break
```

**Lines 246-256:** Update _draw_compact_hp_bar
```python
# OLD:
    # Get HP values
    if is_player:
        current_hp = game_state.character.get('current_hp', 10)
        max_hp = game_state.character.get('hit_points', 10)
    else:
        current_hp = 10
        max_hp = 10
        for member in game_state.party_member_data:
            if member.get('id') == member_id:
                current_hp = member.get('current_hp', 10)
                max_hp = member.get('hp', member.get('hit_points', 10))
                break

# NEW:
    # Get HP values
    if is_player:
        current_hp = game_state.character.get('current_hp', 10)
        max_hp = game_state.character.get('max_hp', 10)
    else:
        current_hp = 10
        max_hp = 10
        for member in game_state.party_member_data:
            if member.get('id') == member_id:
                current_hp = member.get('current_hp', 10)
                max_hp = member.get('max_hp', 10)
                break
```

---

### 11. utils/combat_effects.py

**Lines 250-252:** Update apply_hp_change_to_player
```python
# OLD:
        current_hp = self.game_state.character.get('current_hp', 10)
        max_hp = self.game_state.character.get('hit_points', 10)
        name = self.game_state.character.get('name', 'Player')

# NEW:
        current_hp = self.game_state.character.get('current_hp', 10)
        max_hp = self.game_state.character.get('max_hp', 10)
        name = self.game_state.character.get('name', 'Player')
```

**Lines 302-304:** Update apply_hp_change_to_party_member
```python
# OLD:
        current_hp = target_member.get('current_hp', 10)
        max_hp = target_member.get('max_hit_points', target_member.get('hit_points', 10))
        name = target_member.get('name', char_id)

# NEW:
        current_hp = target_member.get('current_hp', 10)
        max_hp = target_member.get('max_hp', 10)
        name = target_member.get('name', char_id)
```

---

### 12. utils/debug_manager.py

**Lines 156-158:** Update debug_party_status
```python
# OLD:
            char = self.game_state.character
            name = char.get('name', 'Player')
            hp = char.get('hp', char.get('current_hp', '?'))
            max_hp = char.get('hit_points', char.get('max_hp', '?'))

# NEW:
            char = self.game_state.character
            name = char.get('name', 'Player')
            hp = char.get('current_hp', '?')
            max_hp = char.get('max_hp', '?')
```

**Lines 182-185:** Update debug_party_status (party members)
```python
# OLD:
                member_data = self.game_state.get_party_member_data(member_id)
                if member_data:
                    name = member_data.get('name', member_id)
                    hp = member_data.get('current_hp', '?')
                    max_hp = member_data.get('max_hit_points', member_data.get('hp', '?'))
                    char_class = member_data.get('character_class', 'Unknown')
                    level = member_data.get('level', 1)

# NEW:
                member_data = self.game_state.get_party_member_data(member_id)
                if member_data:
                    name = member_data.get('name', member_id)
                    hp = member_data.get('current_hp', '?')
                    max_hp = member_data.get('max_hp', '?')
                    char_class = member_data.get('character_class', 'Unknown')
                    level = member_data.get('level', 1)
```

**Lines 717-728:** Update handle_party_rested
```python
# OLD:
                member_data = self.game_state.get_party_member_data(member_id)
                if member_data:
                    # Party members use: current_hp and max_hit_points
                    max_hp = member_data.get('max_hit_points', member_data.get('hp', 20))
                    member_data['current_hp'] = max_hp
                    print(f"  ❤️ {member_id} healed to {max_hp} HP")

        # Also heal player (uses hit_points for max, current_hp for current)
        if hasattr(self.game_state, 'character'):
            max_hp = self.game_state.character.get('hit_points', 20)
            self.game_state.character['current_hp'] = max_hp
            print(f"  ❤️ Player healed to {max_hp} HP")

# NEW:
                member_data = self.game_state.get_party_member_data(member_id)
                if member_data:
                    # Party members use: current_hp and max_hp (standardized)
                    max_hp = member_data.get('max_hp', 20)
                    member_data['current_hp'] = max_hp
                    print(f"  ❤️ {member_id} healed to {max_hp} HP")

        # Also heal player (uses max_hp for max, current_hp for current)
        if hasattr(self.game_state, 'character'):
            max_hp = self.game_state.character.get('max_hp', 20)
            self.game_state.character['current_hp'] = max_hp
            print(f"  ❤️ Player healed to {max_hp} HP")
```

---

### 13. ui/combat_system.py

**Lines 565-577:** Update _draw_character_portraits
```python
# OLD:
            # Get current HP from the correct source
            if char_id == 'player':
                current_hp = controller.game_state.character.get('current_hp', 10)
                max_hp = controller.game_state.character.get('hit_points', 10)
            else:
                # NPC - read from party_member_data
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('max_hp', 10)
                # Update from party_member_data if available
                for member in controller.game_state.party_member_data:
                    if member.get('id') == char_id:
                        current_hp = member.get('current_hp', current_hp)
                        max_hp = member.get('hp', member.get('hit_points', max_hp))
                        break

# NEW:
            # Get current HP from the correct source
            if char_id == 'player':
                current_hp = controller.game_state.character.get('current_hp', 10)
                max_hp = controller.game_state.character.get('max_hp', 10)
            else:
                # NPC - read from party_member_data
                current_hp = char_data.get('current_hp', 10)
                max_hp = char_data.get('max_hp', 10)
                # Update from party_member_data if available
                for member in controller.game_state.party_member_data:
                    if member.get('id') == char_id:
                        current_hp = member.get('current_hp', current_hp)
                        max_hp = member.get('max_hp', max_hp)
                        break
```

---

## Testing Checklist

After making these changes, test:

1. ✅ Character creation - HP displays correctly
2. ✅ Rest at Old Knob Inn - Player HP recovers to max
3. ✅ Combat - Player and NPC HP displays correctly
4. ✅ Level up - HP increases and displays correctly
5. ✅ Party member recruitment - NPC HP initializes correctly
6. ✅ Save/Load game - HP values persist correctly
7. ✅ Character overlay - HP displays correctly
8. ✅ Combat defeat - HP penalty applies correctly

---

## Summary

**Files changed:** 13
**Total edits:** ~50 locations
**Result:** Consistent `max_hp` + `current_hp` for both player and NPCs
