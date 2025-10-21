# utils/party_display.py
import pygame
import os
from utils.constants import (
    WHITE, BRIGHT_GREEN, GRAY, SOFT_YELLOW, RED,
    NPC_PORTRAITS_PATH, PLAYER_PORTRAITS_PATH,
    PARTY_PANEL_WIDTH, PARTY_PANEL_X,  
    PORTRAIT_SIZE, PORTRAIT_SPACING,   
    FRAME_THICKNESS, MALE_PORTRAITS_PATH          
)
from utils.graphics import draw_centered_text

# # Party display constants
# PARTY_PANEL_WIDTH = 138
# PARTY_PANEL_X = 1024 - PARTY_PANEL_WIDTH
# PORTRAIT_SIZE = 110
# PORTRAIT_SPACING = 10
# FRAME_THICKNESS = 3

def draw_party_status_panel(surface, game_state, fonts):
    """
    Draw party status panel on right side of screen
    Used for main game party displays
    """
        
    # Draw panel background
    panel_rect = pygame.Rect(PARTY_PANEL_X, 10, PARTY_PANEL_WIDTH, 500)
    pygame.draw.rect(surface, (20, 15, 10), panel_rect)  # Dark brown background
    pygame.draw.rect(surface, WHITE, panel_rect, 2)  # White border
    
    # Panel title
    title_y = 15
       
    # Track portrait rectangles for click detection
    portrait_rects = {}

    # Draw portraits
    start_y = 25
    portrait_x = PARTY_PANEL_X + 15

    # Player portrait (always first)
    draw_party_portrait(surface, portrait_x, start_y, 
                       "player", game_state, fonts, is_player=True)
    portrait_rects['player'] = pygame.Rect(portrait_x, start_y, PORTRAIT_SIZE, PORTRAIT_SIZE)
    
    # NPC portraits
    for i, npc_name in enumerate(game_state.party_members):
        if i >= 3:  # Maximum 3 NPCs
            break
        portrait_y = start_y + (i + 1) * (PORTRAIT_SIZE + PORTRAIT_SPACING)
        draw_party_portrait(surface, portrait_x, portrait_y, 
                           npc_name, game_state, fonts, is_player=False)
        portrait_rects[f'npc_{i}'] = pygame.Rect(portrait_x, portrait_y, PORTRAIT_SIZE, PORTRAIT_SIZE)
    # Empty slots
    total_members = 1 + len(game_state.party_members)  # Player + NPCs
    for i in range(total_members, 4):  # Show up to 4 total
        portrait_y = start_y + i * (PORTRAIT_SIZE + PORTRAIT_SPACING)
        draw_empty_portrait_slot(surface, PARTY_PANEL_X + 15, portrait_y)

    return portrait_rects

def draw_party_portrait(surface, x, y, character_name, game_state, fonts, is_player=False):
    """Draw individual party member portrait with HP bar"""
    
    # Try to load portrait
    portrait = load_portrait(character_name, is_player)
    
    if portrait:
        # Scale portrait to fit
        portrait = pygame.transform.scale(portrait, (PORTRAIT_SIZE, PORTRAIT_SIZE))
        surface.blit(portrait, (x, y))
    else:
        # Fallback colored rectangle
        color = get_character_color(character_name, is_player)
        pygame.draw.rect(surface, color, (x, y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    
    # Draw frame
    pygame.draw.rect(surface, WHITE, (x, y, PORTRAIT_SIZE, PORTRAIT_SIZE), FRAME_THICKNESS)
    
    # Draw HP bar below portrait
    _draw_hp_bar_under_portrait(surface, x, y, character_name, game_state, is_player)

def _draw_hp_bar_under_portrait(surface, portrait_x, portrait_y, character_name, game_state, is_player):
    """Draw color-coded HP bar at bottom of portrait (inside the frame)"""
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
    
    # Calculate HP percentage for color determination
    hp_percent = (current_hp / max_hp * 100) if max_hp > 0 else 0
    
    # Color-code based on HP percentage (matching character sheet)
    if hp_percent > 66:
        hp_color = BRIGHT_GREEN
    elif hp_percent > 33:
        hp_color = SOFT_YELLOW
    else:
        hp_color = RED
    
    # HP bar dimensions - INSIDE portrait at bottom
    bar_width = PORTRAIT_SIZE - 8  # Leave 4px margin on each side
    bar_height = 5
    bar_x = portrait_x + 4  # 4px from left edge
    bar_y = portrait_y + PORTRAIT_SIZE - bar_height - 4  # 4px from bottom
    
    # Black background for contrast
    pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    
    # Background (dark gray = missing HP) - slightly transparent
    pygame.draw.rect(surface, (40, 40, 40), (bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2))
    
    # Foreground (color-coded current HP)
    if max_hp > 0:
        hp_fraction = current_hp / max_hp
        filled_width = int((bar_width - 2) * hp_fraction)
        pygame.draw.rect(surface, hp_color, (bar_x + 1, bar_y + 1, filled_width, bar_height - 2))
    
    # White border for definition
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

def draw_empty_portrait_slot(surface, x, y):
    """Draw empty portrait slot"""
    # Gray background
    pygame.draw.rect(surface, GRAY, (x, y, PORTRAIT_SIZE, PORTRAIT_SIZE))
    
    # Dashed border effect
    for dash in range(0, PORTRAIT_SIZE, 8):
        pygame.draw.rect(surface, WHITE, (x + dash, y, 4, 2))
        pygame.draw.rect(surface, WHITE, (x + dash, y + PORTRAIT_SIZE - 2, 4, 2))
        pygame.draw.rect(surface, WHITE, (x, y + dash, 2, 4))
        pygame.draw.rect(surface, WHITE, (x + PORTRAIT_SIZE - 2, y + dash, 2, 4))

def load_portrait(character_name, is_player=False):
    """Load character portrait from file with recovery system"""
    try:
        if is_player:
            # Use same path logic as game_state.py for consistency
            active_dir = os.path.join(os.path.dirname(MALE_PORTRAITS_PATH), "active")
            active_path = os.path.join(active_dir, "player.jpg")
            
            if os.path.exists(active_path):
                return pygame.image.load(active_path)
            else:
                # Active portrait missing - this should trigger recovery in game_state
                print(f"Warning: Active player portrait missing at {active_path}")
                return None
        else:
            # Load NPC portrait
            filename = f"{character_name}_portrait.jpg"
            filepath = os.path.join(NPC_PORTRAITS_PATH, filename)
            return pygame.image.load(filepath)
    except Exception as e:
        print(f"Error loading portrait: {e}")
        return None

def get_character_color(character_name, is_player=False):
    """Get fallback color for character"""
    if is_player:
        return BRIGHT_GREEN
    
    colors = {
        'gareth': (139, 69, 19),    # Brown - Fighter
        'elara': (72, 61, 139),     # Blue - Mage
        'thorman': (184, 134, 11),   # Gold - Cleric  
        'lyra': (47, 79, 47),       # Dark Green - Thief
    }
    return colors.get(character_name, GRAY)

def draw_compact_party_panel(surface, game_state, panel_x, panel_y, 
                             portrait_size=60, selected_member=None):
    """
    Draw compact 4-portrait vertical party panel (reusable for any overlay)
    
    Args:
        surface: pygame surface to draw on
        game_state: game state reference
        panel_x: X position for panel
        panel_y: Y position for panel
        portrait_size: size of each portrait (default 60x60)
        selected_member: ID of selected party member for highlighting
        
    Returns:
        dict: {member_id: pygame.Rect} for click detection
    """
    portrait_spacing = 5
    portrait_rects = {}
    
    # Build party list (player + up to 3 NPCs)
    party_list = ['player'] + list(game_state.party_members)[:3]
    
    for i in range(4):
        portrait_y = panel_y + (i * (portrait_size + portrait_spacing))
        
        if i < len(party_list):
            member_id = party_list[i]
            is_player = (member_id == 'player')
            
            # Draw portrait
            portrait = load_portrait(member_id, is_player)
            
            if portrait:
                # Scale to specified size
                portrait = pygame.transform.scale(portrait, (portrait_size, portrait_size))
                surface.blit(portrait, (panel_x, portrait_y))
            else:
                # Fallback color
                color = get_character_color(member_id, is_player)
                pygame.draw.rect(surface, color, (panel_x, portrait_y, portrait_size, portrait_size))
            
            # Draw HP bar inside portrait
            _draw_compact_hp_bar(surface, panel_x, portrait_y, portrait_size, 
                               member_id, game_state, is_player)
            
            # Selection highlight (yellow border if selected)
            if selected_member == member_id:
                pygame.draw.rect(surface, (255, 255, 0), 
                               (panel_x - 2, portrait_y - 2, portrait_size + 4, portrait_size + 4), 3)
            else:
                # Normal white border
                pygame.draw.rect(surface, WHITE, (panel_x, portrait_y, portrait_size, portrait_size), 2)
            
            # Store clickable rect
            portrait_rects[member_id] = pygame.Rect(panel_x, portrait_y, portrait_size, portrait_size)
        else:
            # Empty slot (grayed out)
            pygame.draw.rect(surface, GRAY, (panel_x, portrait_y, portrait_size, portrait_size))
            pygame.draw.rect(surface, WHITE, (panel_x, portrait_y, portrait_size, portrait_size), 2)
    
    return portrait_rects


def _draw_compact_hp_bar(surface, portrait_x, portrait_y, portrait_size, 
                        member_id, game_state, is_player):
    """Draw HP bar inside compact portrait"""
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
    
    # Calculate HP percentage
    hp_percent = (current_hp / max_hp * 100) if max_hp > 0 else 0
    
    # Color-code (matching character sheet)
    if hp_percent > 66:
        hp_color = BRIGHT_GREEN
    elif hp_percent > 33:
        hp_color = (255, 223, 0)  # SOFT_YELLOW
    else:
        hp_color = (255, 0, 0)  # RED
    
    # Bar dimensions (inside portrait)
    bar_width = portrait_size - 8
    bar_height = 4
    bar_x = portrait_x + 4
    bar_y = portrait_y + portrait_size - bar_height - 4
    
    # Black background
    pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    
    # Dark gray background
    pygame.draw.rect(surface, (40, 40, 40), (bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2))
    
    # Color-coded HP
    if max_hp > 0:
        hp_fraction = current_hp / max_hp
        filled_width = int((bar_width - 2) * hp_fraction)
        pygame.draw.rect(surface, hp_color, (bar_x + 1, bar_y + 1, filled_width, bar_height - 2))
    
    # White border
    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)