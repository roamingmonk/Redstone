# screens/character_overlay.py
"""
Terror in Redstone - Character Overlay System
Session 2 - Professional tabbed character information display

ARCHITECTURE CONVERSION:
- Follows Session 1 help overlay pattern exactly
- Converts single character sheet into 2-tab professional overlay
- Player Stats tab: Existing character sheet functionality preserved
- Party Members tab: Framework ready with basic NPC display
- Maintains exact visual compatibility for user experience
"""

import json
import os
import pygame
from utils.tabbed_overlay_utils import BaseTabbedOverlay
from utils.overlay_utils import *
from utils.graphics import draw_text
from utils.constants import *
from utils.party_display import load_portrait, get_character_color
from game_logic.character_engine import CharacterEngine
from utils.narrative_schema import narrative_schema
from utils.stats_calculator import get_stats_calculator


class CharacterOverlay(BaseTabbedOverlay):
    """
    Character information overlay - 2-tab implementation
    
    SESSION 2 GOALS:
    - Prove BaseTabbedOverlay works with multiple tabs
    - Preserve all existing character sheet functionality
    - Create foundation for party management system
    - Maintain exact same user experience
    """
    
    def __init__(self, screen_manager=None):
        super().__init__("character_key", "CHARACTER INFO", screen_manager)
        
        # Add two tabs following roadmap specification
        self.add_tab("player_stats", "Player", pygame.K_1)
        self.add_tab("party_members", "Party", pygame.K_2)
        self.add_tab("abilities", "Abilities", pygame.K_3)
        self.add_tab("advancement", "Advance", pygame.K_4)
        
        print("🎯 Character overlay initialized with 2 tabs")
    
    def render_tab_content(self, surface: pygame.Surface, active_tab, game_state, fonts, images):
        """
        Render tab-specific content based on active tab
        
        DESIGN PRINCIPLE: 
        Each tab handles its own content rendering while framework manages tabs
        """
        
        content_rect = self.get_content_area_rect()
        
        if active_tab.tab_id == "player_stats":
            self._render_player_stats_tab(surface, content_rect, game_state, fonts, images)
        elif active_tab.tab_id == "party_members":
            self._render_party_members_tab(surface, content_rect, game_state, fonts, images)
        elif active_tab.tab_id == "abilities":
            self._render_abilities_tab(surface, content_rect, game_state, fonts, images)
        elif active_tab.tab_id == "advancement":
            self._render_advancement_tab(surface, content_rect, game_state, fonts, images)
        else:
            # Fallback - should never happen
            draw_text(surface, f"Unknown tab: {active_tab.tab_id}", 
                     fonts.get('fantasy_medium', fonts['normal']), 
                     content_rect.centerx, content_rect.centery, WHITE)
    
    def _render_player_stats_tab(self, surface: pygame.Surface, content_rect: pygame.Rect, 
                                game_state, fonts, images):
        """
        Render player statistics - COPIED from character_sheet.py with minimal changes
        
        COMPATIBILITY GOAL: Zero visual difference from original character sheet
        """
        # Check required data (same as original)
        if not hasattr(game_state, 'character'):
            error_font = fonts.get('fantasy_medium', fonts['normal'])
            draw_text(surface, "ERROR: No character data", error_font,
                     content_rect.centerx, content_rect.centery, WHITE)
            return
        
        # Get character data
        character = game_state.character
        character_name = character.get('name', 'Adventurer')
        
        # Layout areas (adjusted for content rect instead of full screen)
        left_section_x = content_rect.x + 20
        left_section_y = content_rect.y + 20
        left_section_width = 300
        
        center_section_x = left_section_x + left_section_width + 20
        center_section_y = content_rect.y + 20
        center_section_width = 200
        
        right_section_x = center_section_x + center_section_width + 20
        right_section_y = content_rect.y + 20
        
        # Fonts (same as original)
        header_font = fonts.get('fantasy_medium', fonts['normal'])
        normal_font = fonts.get('fantasy_small', fonts['normal'])
        small_font = fonts.get('normal', normal_font)
        
        # LEFT SECTION: Character Info
        current_y = left_section_y
        
        # Name
        name_text = header_font.render(f"Name: {character_name}", True, CYAN)
        surface.blit(name_text, (left_section_x, current_y))
        current_y += 32
        
        # Level (prominent display)
        current_level = character.get('level', 1)
        level_text = header_font.render(f"Level: {current_level}", True, CYAN)
        surface.blit(level_text, (left_section_x, current_y))
        current_y += 32
        
        # XP Progress Bar (ASCII Style)
        current_xp = character.get('experience', 0)
        from utils.narrative_schema import narrative_schema
        xp_requirements = narrative_schema.schema.get('xp_balance', {}).get('level_progression', {}).get('requirements', [0, 300, 900, 2700, 6500])
        
        if current_level < 5:  # Max level is 5
            next_level_xp = xp_requirements[current_level] if current_level < len(xp_requirements) else xp_requirements[-1]
            current_level_xp = xp_requirements[current_level - 1] if current_level > 1 else 0
            
            xp_progress = current_xp - current_level_xp
            xp_needed_total = next_level_xp - current_level_xp
            
            if current_xp >= next_level_xp:
                # Ready to level up - text and button on same line
                xp_text = normal_font.render("XP Needed: [LEVEL UP READY!]", True, BRIGHT_GREEN)
                surface.blit(xp_text, (left_section_x, current_y))
                
                # Level UP! button - positioned right of the text
                text_width = xp_text.get_width()
                level_up_button = pygame.Rect(left_section_x + text_width + 20, current_y - 5, 100, 30)
                pygame.draw.rect(surface, BRIGHT_GREEN, level_up_button)
                pygame.draw.rect(surface, WHITE, level_up_button, 2)
                button_text = normal_font.render("Level UP!", True, BLACK)
                text_rect = button_text.get_rect(center=level_up_button.center)
                surface.blit(button_text, text_rect)
                current_y += 40
            else:
                # ASCII Progress Bar
                bar_length = 10  # Number of characters in bar
                filled_chars = int((xp_progress / xp_needed_total) * bar_length) if xp_needed_total > 0 else 0
                empty_chars = bar_length - filled_chars
                
                progress_bar = "#" * filled_chars + "-" * empty_chars
                remaining_xp = next_level_xp - current_xp
                
                xp_text = normal_font.render(f"XP : ({current_xp:,}/{next_level_xp:,}) [{progress_bar}]", True, WHITE)
                surface.blit(xp_text, (left_section_x, current_y))
                current_y += 35
        else:
            # Max level reached
            xp_text = normal_font.render("XP Needed: [MAX LEVEL]", True, YELLOW)
            surface.blit(xp_text, (left_section_x, current_y))
            current_y += 35
        
        # Hit Points  
        hp_text = normal_font.render(f"Hit Points: {character.get('hit_points', 10)}", True, WHITE)
        surface.blit(hp_text, (left_section_x, current_y))
        current_y += 50
        
        # Equipment Section
        equipment_header = header_font.render("Equipment", True, CYAN)
        surface.blit(equipment_header, (left_section_x, current_y))
        current_y += 30
        
        # Weapon
        weapon_name = getattr(game_state, 'equipped_weapon', 'None')
        weapon_label = normal_font.render("Weapon:", True, WHITE)
        surface.blit(weapon_label, (left_section_x, current_y))
        
        if weapon_name and weapon_name != 'None':
            from utils.stats_calculator import get_stats_calculator
            calculator = get_stats_calculator()
            weapon_damage, _ = calculator.calculate_weapon_damage(game_state)
            weapon_display = f"{weapon_name.replace('_', ' ').title()} ({weapon_damage})"
        else:
            weapon_display = "None"
        weapon_text = normal_font.render(weapon_display, True, WHITE)
        surface.blit(weapon_text, (left_section_x + 100, current_y))
        current_y += 32
        
        # Armor
        armor_name = getattr(game_state, 'equipped_armor', 'None')
        armor_label = normal_font.render("Armor:", True, WHITE)
        surface.blit(armor_label, (left_section_x, current_y))

        armor_display = armor_name.replace('_', ' ').title() if armor_name and armor_name != 'None' else "None"
        armor_text = normal_font.render(armor_display, True, WHITE)
        surface.blit(armor_text, (left_section_x + 100, current_y))
        current_y += 32

        # Shield
        shield_name = getattr(game_state, 'equipped_shield', 'None')
        shield_label = normal_font.render("Shield:", True, WHITE)
        surface.blit(shield_label, (left_section_x, current_y))

        shield_display = shield_name.replace('_', ' ').title() if shield_name and shield_name != 'None' else "None"
        shield_text = normal_font.render(shield_display, True, WHITE)
        surface.blit(shield_text, (left_section_x + 100, current_y))
        current_y += 50
        # Gold
        gold_amount = character.get('gold', 0)
        
        gold_label = normal_font.render("Gold:", True, WHITE)
        surface.blit(gold_label, (left_section_x, current_y))
        
        gold_value = header_font.render(str(gold_amount), True, BRIGHT_GREEN)
        surface.blit(gold_value, (left_section_x + 120, current_y - 3))
        
        # Combat Stats (add after gold, before RIGHT SECTION)
        current_y += 25
        combat_header = header_font.render("Combat Stats", True, CYAN)
        surface.blit(combat_header, (left_section_x, current_y+10))
        current_y += 30

        ac, _ = calculator.calculate_armor_class(game_state)
        attacks, _ = calculator.calculate_attacks_per_round(game_state)

        ac_text = normal_font.render(f"AC: {ac}", True, WHITE)
        surface.blit(ac_text, (left_section_x, current_y+10))
        current_y += 25

        attacks_text = normal_font.render(f"Attacks: {attacks}", True, WHITE)
        surface.blit(attacks_text, (left_section_x, current_y+10))

        # RIGHT SECTION: Attributes
        attr_x = right_section_x
        attr_y = right_section_y
        
        attr_header = header_font.render("Attributes", True, CYAN)
        surface.blit(attr_header, (attr_x, attr_y))
        attr_y += 30
        
        # Draw attributes in a neat column
        attributes = [
            ("STR", character.get('strength', 10)),
            ("DEX", character.get('dexterity', 10)),
            ("CON", character.get('constitution', 10)),
            ("INT", character.get('intelligence', 10)),
            ("WIS", character.get('wisdom', 10)),
            ("CHA", character.get('charisma', 10))
        ]
        
        for attr_name, attr_value in attributes:
            attr_label = normal_font.render(f"{attr_name}:", True, WHITE)
            surface.blit(attr_label, (attr_x, attr_y))
            
            attr_val = header_font.render(str(attr_value), True, BRIGHT_GREEN)
            surface.blit(attr_val, (attr_x + 60, attr_y - 3))
            attr_y += 25
        
        # RIGHT SECTION: Character Portrait (same as character_sheet.py)
        portrait_x = right_section_x
        portrait_y = right_section_y + 250
        portrait_size = 150
        
        # Load the active player portrait using same logic as character_sheet.py
        try:
            from utils.constants import MALE_PORTRAITS_PATH
            import os
            
            active_dir = os.path.join(os.path.dirname(MALE_PORTRAITS_PATH), "active")
            active_path = os.path.join(active_dir, "player.jpg")
            
            if os.path.exists(active_path):
                player_portrait = pygame.image.load(active_path)
                player_portrait = pygame.transform.scale(player_portrait, (portrait_size, portrait_size))
                surface.blit(player_portrait, (portrait_x, portrait_y))
            else:
                # Fallback: bright green square for player
                pygame.draw.rect(surface, BRIGHT_GREEN, 
                                (portrait_x, portrait_y, portrait_size, portrait_size))
                
        except Exception as e:
            print(f"Error loading player portrait for character overlay: {e}")
            # Fallback: bright green square for player
            pygame.draw.rect(surface, BRIGHT_GREEN, 
                            (portrait_x, portrait_y, portrait_size, portrait_size))
        
        # Draw white border around portrait
        pygame.draw.rect(surface, WHITE, 
                        (portrait_x, portrait_y, portrait_size, portrait_size), 2)
        

    def _render_abilities_tab(self, surface: pygame.Surface, content_rect: pygame.Rect, 
                         game_state, fonts, images):
        """
        Render abilities tab - spells and special abilities
        """
        if not hasattr(game_state, 'character'):
            error_font = fonts.get('fantasy_medium', fonts['normal'])
            draw_text(surface, "ERROR: No character data", error_font,
                    content_rect.centerx, content_rect.centery, WHITE)
            return
        
        character = game_state.character
        character_class = character.get('class', 'fighter')
        level = character.get('level', 1)
        
        # Fonts
        header_font = fonts.get('fantasy_medium', fonts['normal'])
        normal_font = fonts.get('fantasy_small', fonts['normal'])
        
        current_y = content_rect.y + 20
        
        # Header
        draw_text(surface, "ABILITIES & FEATURES", header_font, 
                content_rect.x + 20, current_y, CYAN)
        current_y += 40
        
        # Show gained abilities from level progression
        abilities_gained = character.get('abilities', [])
        if abilities_gained:
            draw_text(surface, "Class Features:", normal_font, 
                    content_rect.x + 40, current_y, YELLOW)
            current_y += 25
            
            for ability in abilities_gained:
                draw_text(surface, f"• {ability}", normal_font, 
                        content_rect.x + 60, current_y, WHITE)
                current_y += 20
                
                # Show description
                description = self._get_ability_description(ability, character_class)
                if description:
                    draw_text(surface, f"  {description}", normal_font, 
                            content_rect.x + 80, current_y, GRAY)
                    current_y += 20
    
                current_y += 5  # Extra spacing between abilities
        
        # Show spells if spellcaster
        if character_class in ['wizard', 'cleric']:
            draw_text(surface, "Spellcasting:", normal_font, 
                    content_rect.x + 40, current_y, YELLOW)
            current_y += 25
            
            # This is placeholder for now - we'll enhance this later
            draw_text(surface, "• Spell system coming soon", normal_font, 
                    content_rect.x + 60, current_y, WHITE)
            current_y += 20
        
        # Show basic info
        if not abilities_gained and character_class not in ['wizard', 'cleric']:
            draw_text(surface, "No special abilities yet", normal_font, 
                    content_rect.x + 40, current_y, WHITE)

    def _render_advancement_tab(self, surface: pygame.Surface, content_rect: pygame.Rect, 
                           game_state, fonts, images):
        """
        Render advancement tab - level up interface
        """
        # Get fonts
        header_font = fonts.get('fantasy_medium', fonts['normal'])
        normal_font = fonts.get('fantasy_small', fonts['normal'])
        
        # Check if character exists
        if not hasattr(game_state, 'character'):
            draw_text(surface, "ERROR: No character data", header_font,
                    content_rect.centerx, content_rect.centery, WHITE)
            return
        
        character = game_state.character
        current_level = character.get('level', 1)
        current_xp = character.get('experience', 0)
        
        # Use your existing XP detection logic
        
        xp_requirements = narrative_schema.schema.get('xp_balance', {}).get('level_progression', {}).get('requirements', [0, 300, 900, 2700, 6500])
        #xp_requirements = self.character_engine.get_level_requirements()

        # Check if ready to level up
        can_level_up = False
        if current_level < 5:
            next_level_xp = xp_requirements[current_level] if current_level < len(xp_requirements) else xp_requirements[-1]
            if current_xp >= next_level_xp:
                can_level_up = True
        
        # Render header
        draw_text(surface, "CHARACTER ADVANCEMENT", header_font, 
                content_rect.x + 20, content_rect.y + 20, CYAN)
        
        current_y = content_rect.y + 60
        
        if can_level_up:
            draw_text(surface, "LEVEL UP AVAILABLE!", normal_font, 
                    content_rect.x + 40, current_y, BRIGHT_GREEN)
            current_y += 40
        
            # Show what will be gained
            next_level = current_level + 1
            character_class = character.get('class', 'fighter')
            
            draw_text(surface, f"Advancing to Level {next_level}:", normal_font, 
                    content_rect.x + 40, current_y, YELLOW)
            current_y += 30
            
            class_file = os.path.join("data", "player", "character_classes.json")
            try:
                with open(class_file, 'r') as f:
                    json_data = json.load(f)
                class_data = json_data["character_classes"].get(character_class, {})
                
                hit_die = class_data.get('hit_die', 8)
                draw_text(surface, f"• Hit Points: +1d{hit_die} + CON modifier", normal_font, 
                          content_rect.x + 60, current_y, WHITE)
            except:
                draw_text(surface, f"• Hit Points: +1d8 + CON modifier", normal_font, 
                          content_rect.x + 60, current_y, WHITE)
            current_y += 25
            
            # Show features gained from JSON
            if 'level_progression' in class_data:
                level_key = f"level_{next_level}"
                level_data = class_data['level_progression'].get(level_key, {})
                
                features = level_data.get('features', [])
                description = level_data.get('description', '')
                
                # Show features
                for feature in features:
                    draw_text(surface, f"• {feature}", normal_font, 
                              content_rect.x + 60, current_y, WHITE)
                    current_y += 25
                
                # Show description if available
                if description:
                    current_y += 10
                    draw_text(surface, description, normal_font, 
                              content_rect.x + 60, current_y, YELLOW)
                    current_y += 35  # Extra space before button
                
                # Add Level Up button
                button_rect = pygame.Rect(content_rect.x + 60, current_y, 120, 35)
                pygame.draw.rect(surface, BRIGHT_GREEN, button_rect)
                pygame.draw.rect(surface, WHITE, button_rect, 2)
                
                button_font = fonts.get('fantasy_small', fonts['normal'])
                button_text = button_font.render("ADVANCE!", True, BLACK)
                text_rect = button_text.get_rect(center=button_rect.center)
                surface.blit(button_text, text_rect)
                
                # Store button rect for click detection (we'll add click handling next)
                self.level_up_button_rect = button_rect
        
        else:
            draw_text(surface, "No advancement available", normal_font, 
                    content_rect.x + 40, current_y, WHITE)
            current_y += 30
            
            # Show recent level-up results if available
            if hasattr(self, 'level_up_results') and self.level_up_results:
                current_y += 20
                draw_text(surface, "RECENT ADVANCEMENT:", header_font, 
                        content_rect.x + 40, current_y, BRIGHT_GREEN)
                current_y += 30
                
                results = self.level_up_results
                draw_text(surface, f"Advanced to Level {results['new_level']} {results['class'].title()}!", normal_font, 
                        content_rect.x + 60, current_y, YELLOW)
                current_y += 25
                
                draw_text(surface, f"Gained {results['hp_gain']} Hit Points (Total: {results['new_total_hp']})", normal_font, 
                        content_rect.x + 60, current_y, WHITE)
                current_y += 25
                
                if results['abilities_gained']:
                    for ability in results['abilities_gained']:
                        draw_text(surface, f"New Ability: {ability}", normal_font, 
                                content_rect.x + 60, current_y, CYAN)
                        current_y += 25
    
    def _render_party_members_tab(self, surface: pygame.Surface, content_rect: pygame.Rect, 
                                 game_state, fonts, images):
        """
        Render party members information - NEW functionality for Session 2
        
        APPROACH: Left-justified portraits with NPC data on the right (as suggested)
        """
        current_y = content_rect.y + 20
        
        # Check if we have party members
        party_members = getattr(game_state, 'party_members', [])
        
        if not party_members:
            # No party members recruited yet
            no_party_font = fonts.get('fantasy_medium', fonts['normal'])
            draw_text(surface, "No party members recruited yet", no_party_font,
                    content_rect.centerx, content_rect.centery - 40, WHITE)
            
            instruction_font = fonts.get('fantasy_small', fonts['normal'])
            # Split the long text into two lines
            line1 = "Visit the Broken Blade tavern"
            line2 = "to recruit companions"
            
            draw_text(surface, line1, instruction_font,
                    content_rect.centerx, content_rect.centery, GRAY)
            draw_text(surface, line2, instruction_font,
                    content_rect.centerx, content_rect.centery + 20, GRAY)
            return
        
        # Fonts
        header_font = fonts.get('fantasy_medium', fonts['normal'])
        normal_font = fonts.get('fantasy_small', fonts['normal'])
        
        # Portrait and info layout constants
        portrait_size = 100
        portrait_spacing = 120  # Space between portraits vertically
        info_x_offset = 120     # Distance from portrait to info text
        
        for i, npc_id in enumerate(party_members):
            # Calculate positions
            portrait_x = content_rect.x + 20
            portrait_y = current_y + (i * portrait_spacing)
            
            # Stop if we're running out of space
            if portrait_y + portrait_size > content_rect.y + content_rect.height - 20:
                break
            
            # Draw NPC portrait (using party_display system)
            npc_portrait = load_portrait(npc_id, is_player=False)
            
            if npc_portrait:
                # Scale portrait to fit
                npc_portrait = pygame.transform.scale(npc_portrait, (portrait_size, portrait_size))
                surface.blit(npc_portrait, (portrait_x, portrait_y))
            else:
                # Fallback colored rectangle
                color = get_character_color(npc_id, is_player=False)
                pygame.draw.rect(surface, color, (portrait_x, portrait_y, portrait_size, portrait_size))
            
            # Draw portrait border
            pygame.draw.rect(surface, WHITE, (portrait_x, portrait_y, portrait_size, portrait_size), 2)
            
            # Draw NPC information to the right of portrait
            info_x = portrait_x + info_x_offset
            info_y = portrait_y
            
            # Get NPC data (with fallbacks)
            npc_info = game_state.get_party_member_data(npc_id)
            if not npc_info:
                npc_info = {'name': npc_id.title(), 'class': 'Adventurer', 'level': 1}
            
            # NPC Name
            name_text = header_font.render(npc_info['name'], True, CYAN)
            surface.blit(name_text, (info_x, info_y))
            info_y += 25
            
            # NPC Class
            class_text = normal_font.render(f"Class: {npc_info['class']}", True, WHITE)
            surface.blit(class_text, (info_x, info_y))
            info_y += 20
            
            # NPC Level
            level_text = normal_font.render(f"Level: {npc_info['level']}", True, WHITE)
            surface.blit(level_text, (info_x, info_y))
            info_y += 20
            
            # Status
            status_text = normal_font.render("Status: Ready", True, BRIGHT_GREEN)
            surface.blit(status_text, (info_x, info_y))
        
        # Party summary at bottom
        summary_y = content_rect.y + content_rect.height - 40
        party_size = 1 + len(party_members)  # Player + NPCs
        summary_text = normal_font.render(f"Total Party Size: {party_size}/4", True, YELLOW)
        surface.blit(summary_text, (content_rect.x + 20, summary_y))
        
#TODO this armor class ac needs to be pulled from somewhere else and not hard coded.
    def _get_armor_ac(self, armor_name):
        """Get armor class string for display - copied from character_sheet.py logic"""
        if armor_name == "Leather Armor":
            return "(AC 7)"
        elif armor_name == "Chain Mail":
            return "(AC 5)"
        elif armor_name == "Plate Mail":
            return "(AC 3)"
        else:
            return ""
#TODO this sheild ac needs to be pulled from somewhere else and not hard coded.    
    def _get_shield_ac(self, shield_name):
        """Get shield AC bonus string - copied from character_sheet.py logic"""
        if shield_name in ["Small Shield", "Medium Shield", "Large Shield"]:
            return "(+1 AC)"
        else:
            return ""

    def _get_ability_description(self, ability_name, character_class):
        """Get description for an ability from JSON"""

        try:
            class_file = os.path.join("data", "player", "character_classes.json")
            with open(class_file, 'r') as f:
                json_data = json.load(f)
            
            class_data = json_data["character_classes"].get(character_class, {})
            descriptions = class_data.get("feature_descriptions", {})
            return descriptions.get(ability_name, "")
        except:
            return ""

    def on_overlay_opened(self, game_state):
        """Called when character overlay opens"""
        super().on_overlay_opened(game_state)
        self.game_state = game_state  # Store for button clicks
        print("👤 Character overlay opened - tabbed version!")
    
    def on_overlay_closed(self, game_state):
        """Called when character overlay closes"""
        super().on_overlay_closed(game_state)
        print("👤 Character overlay closed")
    
    def on_tab_changed(self, old_index: int, new_index: int):
        """Called when tab changes - useful for future enhancements"""
        super().on_tab_changed(old_index, new_index)
        active_tab = self.get_active_tab()
        if active_tab:
            print(f"📋 Character overlay: Switched to {active_tab.display_name} tab")

    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks - MUST call parent first for tab functionality"""
        # CRITICAL: Check tab clicks first
        if super().handle_mouse_click(mouse_pos):
            return True
        
        # Handle advancement button click
        if hasattr(self, 'level_up_button_rect') and self.level_up_button_rect.collidepoint(mouse_pos):
            print("ADVANCE button clicked!")
            
            # Get game_state from screen_manager using correct attribute name
            if self.screen_manager and hasattr(self.screen_manager, '_current_game_state'):
                game_state = self.screen_manager._current_game_state
                print("DEBUG: game_state found, creating CharacterEngine")
                
                character_engine = CharacterEngine(game_state)
                
                print(f"DEBUG: Checking can_level_up...")
                if character_engine.can_level_up():
                    print("DEBUG: can_level_up = True, calling level_up()")
                    
                    # DEBUG: Show XP before level-up
                    current_xp_before = game_state.character.get('experience', 0)
                    current_level_before = game_state.character.get('level', 1)
                    print(f"DEBUG: BEFORE level-up - Level: {current_level_before}, XP: {current_xp_before}")
                    
                    results = character_engine.level_up()
                    
                    # DEBUG: Show XP after level-up  
                    current_xp_after = game_state.character.get('experience', 0)
                    current_level_after = game_state.character.get('level', 1)
                    print(f"DEBUG: AFTER level-up - Level: {current_level_after}, XP: {current_xp_after}")
                    
                    if results:
                        print(f"Level up successful: {results}")
                        self.level_up_results = results
                        
                        # DEBUG: Check party XP tracking
                        print(f"DEBUG: Party members: {getattr(game_state, 'party_members', [])}")
                        print(f"DEBUG: Party XP data: {getattr(game_state, 'party_xp', {})}")

                        # ADD THIS NEW CODE HERE:
                        # Check and level up party members
                        party_level_ups = character_engine.check_party_level_ups()
                        print(f"DEBUG: Party level-up candidates: {party_level_ups}")

                        # Level up any party members who can advance
                        for member_id in party_level_ups:
                            if member_id != "player":  # Skip player, already done
                                party_result = character_engine.level_up_party_member(member_id)
                                if party_result:
                                    print(f"Party member {member_id} also leveled up!")
                    else:
                        print("DEBUG: level_up() returned None")
                else:
                    print("DEBUG: can_level_up = False")
            else:
                print("DEBUG: Could not access _current_game_state")
            
            return True
        
        return False
# ========================================
# COMPATIBILITY LAYER
# ========================================

# Create global instance
character_overlay_instance = None

def get_character_overlay():
    """Get the global character overlay instance"""
    global character_overlay_instance
    if character_overlay_instance is None:
        character_overlay_instance = CharacterOverlay()
    return character_overlay_instance

def draw_character_sheet_screen(surface, game_state, fonts, images=None):
    """
    REPLACEMENT for old character_sheet.py - EXACT SAME FUNCTION SIGNATURE
    
    This maintains compatibility with your existing ScreenManager while
    internally using the new BaseTabbedOverlay system.
    
    NO CHANGES needed to your ScreenManager integration!
    """
    
    overlay = get_character_overlay()
    
    # Register with input handler on first render if not already registered
    if not getattr(overlay, '_input_registered', False):
        # Try to find screen_manager from the rendering context
        try:
            # Get screen_manager from the call - it should be available as 'self' in caller
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'self' in frame.f_locals:
                screen_manager = frame.f_locals['self']
                if hasattr(screen_manager, 'input_handler'):
                    overlay.screen_manager = screen_manager
                    overlay._register_with_input_handler()
                    overlay._input_registered = True
        except:
            # If registration fails, mark as attempted to avoid repeated tries
            overlay._input_registered = True
    
    overlay.render(surface, game_state, fonts, images)
    return None

def handle_character_sheet_click(mouse_pos, result):
    """
    COMPATIBILITY: Handle clicks on character sheet
    
    This maintains the exact same interface as your original character_sheet.py
    but internally uses the new tabbed overlay system.
    """
    overlay = get_character_overlay()
    return overlay.handle_mouse_click(mouse_pos)

def handle_character_keyboard_input(key, game_state):
    """NEW: Handle keyboard input for character overlay - CRITICAL FOR TAB NAVIGATION"""
    if getattr(game_state, 'character_sheet_open', False):
        overlay = get_character_overlay()
        key_name = pygame.key.name(key)
        print(f"🎯 Character overlay processing key: {key_name}")
        result = overlay.handle_keyboard_input(key)
        if result:
            print(f"✅ Character overlay handled key: {key_name}")
        else:
            print(f"❌ Character overlay ignored key: {key_name}")
        return result
    return False

