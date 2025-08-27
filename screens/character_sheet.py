"""
Terror in Redstone - Character Sheet Screen
Classic RPG character statistics display
"""

import pygame

from utils.overlay_utils import (
    draw_popup_background, draw_chunky_border, 
    draw_button, WHITE, BLACK, BRIGHT_GREEN, BROWN, DARK_GRAY, CYAN
)

def draw_character_sheet_screen(surface, game_state, fonts, images=None):
    """Draw the character sheet screen with stats, equipment, and conditions"""
    
    # Check required data
    if not hasattr(game_state, 'character'):
        print("ERROR: game_state has no character")
        return None
    
    # Fill screen with brown background
    draw_popup_background(surface)
    
    # Get character data
    character = game_state.character
    character_name = character.get('name', 'Adventurer')
    
    # Draw title
    title_y = 25
    title_font = fonts.get('fantasy_large', fonts['header'])
    title_text = title_font.render("Character Summary", True, BRIGHT_GREEN)
    title_x = (1024 - title_text.get_width()) // 2
    surface.blit(title_text, (title_x, title_y))
    
    # Draw main content border
    content_x = 50
    content_y = 120
    content_width = 924
    content_height = 500
    
    draw_chunky_border(surface, content_x, content_y, content_width, content_height)
    
    # Fill content area
    pygame.draw.rect(surface, DARK_GRAY, 
                    (content_x + 6, content_y + 6, content_width - 12, content_height - 12))
    
    # Layout areas
    left_section_x = content_x + 20
    left_section_y = content_y + 20
    left_section_width = 300
    
    center_section_x = left_section_x + left_section_width + 20
    center_section_y = content_y + 20
    center_section_width = 200
    
    right_section_x = center_section_x + center_section_width + 20
    right_section_y = content_y + 20
    
    # Fonts
    header_font = fonts.get('fantasy_medium', fonts['normal'])
    normal_font = fonts.get('fantasy_small', fonts['normal'])
    small_font = fonts.get('normal', normal_font)
    
    # LEFT SECTION: Character Info
    current_y = left_section_y
    
    # Name
    name_text = header_font.render(f"Name: {character_name}", True, CYAN)
    surface.blit(name_text, (left_section_x, current_y))
    current_y += 30
    
    # Gender
    gender = character.get('gender', 'Unknown').title()
    gender_text = normal_font.render(f"Gender: {gender}", True, WHITE)
    surface.blit(gender_text, (left_section_x, current_y))
    current_y += 25
    
    # Class (placeholder for future)
    class_text = normal_font.render("Class: Fighter", True, WHITE)
    surface.blit(class_text, (left_section_x, current_y))
    current_y += 35
    
    # Hit Points
    hit_points = calculate_hit_points(character)
    hp_label = normal_font.render("Hit Points:", True, WHITE)
    surface.blit(hp_label, (left_section_x, current_y))
    
    hp_value = header_font.render(str(hit_points), True, BRIGHT_GREEN)
    surface.blit(hp_value, (left_section_x + 120, current_y - 3))
    current_y += 35
    
    # Armor Class
    base_ac, total_ac = calculate_armor_class(game_state)
    ac_label = normal_font.render("AC:", True, WHITE)
    surface.blit(ac_label, (left_section_x, current_y))
    
    if base_ac == total_ac:
        ac_value = header_font.render(str(total_ac), True, BRIGHT_GREEN)
    else:
        ac_value = header_font.render(f"{total_ac} ({base_ac})", True, BRIGHT_GREEN)
    surface.blit(ac_value, (left_section_x + 120, current_y - 3))
    current_y += 50
    
    # Equipment Section
    eq_header = header_font.render("Equipped Items", True, CYAN)
    surface.blit(eq_header, (left_section_x, current_y))
    current_y += 32
    
    # Weapon
    weapon_name = game_state.equipped_weapon or "None"
    weapon_damage = get_weapon_damage(weapon_name)
    
    weapon_label = normal_font.render("Weapon:", True, WHITE)
    surface.blit(weapon_label, (left_section_x, current_y))
    
    weapon_text = normal_font.render(f"{weapon_name} {weapon_damage}", True, WHITE)
    surface.blit(weapon_text, (left_section_x + 100, current_y))
    current_y += 32
    
    # Armor
    armor_name = game_state.equipped_armor or "None"
    armor_ac = get_armor_ac(armor_name)
    
    armor_label = normal_font.render("Armor:", True, WHITE)
    surface.blit(armor_label, (left_section_x, current_y))
    
    armor_text = normal_font.render(f"{armor_name} {armor_ac}", True, WHITE)
    surface.blit(armor_text, (left_section_x + 100, current_y))
    current_y += 32
    
    # Shield
    shield_name = game_state.equipped_shield or "None"
    shield_ac = get_shield_ac(shield_name)
    
    shield_label = normal_font.render("Shield:", True, WHITE)
    surface.blit(shield_label, (left_section_x, current_y))
    
    shield_text = normal_font.render(f"{shield_name} {shield_ac}", True, WHITE)
    surface.blit(shield_text, (left_section_x + 100, current_y))
    current_y += 50
    
    # Gold
    gold_amount = game_state.get_current_gold()
    
    gold_label = normal_font.render("Gold:", True, WHITE)
    surface.blit(gold_label, (left_section_x, current_y))
    
    gold_value = header_font.render(str(gold_amount), True, BRIGHT_GREEN)
    surface.blit(gold_value, (left_section_x + 120, current_y - 3))
      
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
    
    # RIGHT SECTION: Character Portrait Placeholder
    portrait_x = right_section_x
    portrait_y = right_section_y + 250
    portrait_size = 150
    
    pygame.draw.rect(surface, (60, 80, 120), 
                    (portrait_x, portrait_y, portrait_size, portrait_size))
    pygame.draw.rect(surface, WHITE, 
                    (portrait_x, portrait_y, portrait_size, portrait_size), 2)
    
    # Load the active player portrait using same logic as party_display.py
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
            print(f"Warning: Active player portrait missing at {active_path}")
            
    except Exception as e:
        print(f"Error loading player portrait for character sheet: {e}")
        # Fallback: bright green square for player
        pygame.draw.rect(surface, BRIGHT_GREEN, 
                        (portrait_x, portrait_y, portrait_size, portrait_size))
    
    # Draw white border around portrait
    pygame.draw.rect(surface, WHITE, 
                    (portrait_x, portrait_y, portrait_size, portrait_size), 2)

   # Conditions Section (bottom)
    conditions_y = content_y + content_height - 60
    conditions_header = normal_font.render("Conditions:", True, WHITE)
    surface.blit(conditions_header, (left_section_x, conditions_y))
    
    # For now, just show "None" - future expansion for status effects
    conditions_text = small_font.render("None", True, WHITE)
    surface.blit(conditions_text, (left_section_x + 160, conditions_y + 5))
    
    # Draw return button
    button_y = content_y + content_height + 20
    return_rect = draw_button(surface, 512 - 60, button_y, 120, 40, 
                             "Return", fonts.get('fantasy_small', fonts['normal']))
    
    # Draw close instruction
    close_y = button_y + 50
    close_font = fonts.get('help_text', fonts['small'])
    close_text = "Press C again to close"
    
    # Center the close instruction
    close_surface = close_font.render(close_text, True, WHITE)
    close_x = (1024 - close_surface.get_width()) // 2
    surface.blit(close_surface, (close_x, close_y))

    return return_rect

def calculate_hit_points(character):
    """Calculate character hit points based on constitution"""
    constitution = character.get('constitution', 10)
    con_modifier = (constitution - 10) // 2
    base_hp = 8  # Fighter base
    return max(1, base_hp + con_modifier)

def calculate_armor_class(game_state):
    """Calculate base and total armor class"""
    character = game_state.character
    dexterity = character.get('dexterity', 10)
    dex_modifier = (dexterity - 10) // 2
    
    base_ac = 10 + dex_modifier
    total_ac = base_ac
    
    # Add armor bonuses
    if game_state.equipped_armor:
        total_ac += get_armor_ac_bonus(game_state.equipped_armor)
    
    if game_state.equipped_shield:
        total_ac += get_shield_ac_bonus(game_state.equipped_shield)
    
    return base_ac, total_ac

def get_weapon_damage(weapon_name):
    """Get weapon damage string"""
    weapon_damages = {
        'Longsword': '1d8',
        'Shortsword': '1d6',
        'Dagger': '1d4',
        'None': ''
    }
    return weapon_damages.get(weapon_name, '1d6')

def get_armor_ac(armor_name):
    """Get armor AC display string"""
    if armor_name == 'None':
        return ''
    return 'AC:12'  # Simplified for now

def get_armor_ac_bonus(armor_name):
    """Get armor AC bonus value"""
    armor_bonuses = {
        'Leather Armor': 2,  
        'Chain Mail': 4,
        'Plate Armor': 6
    }
    return armor_bonuses.get(armor_name, 0)

def get_shield_ac(shield_name):
    """Get shield AC display string"""
    if shield_name == 'None':
        return ''
    return '+2'

def get_shield_ac_bonus(shield_name):
    """Get shield AC bonus value"""
    if shield_name and shield_name != 'None':
        return 2
    return 0