# constants.py 

import pygame
import os

# === SCREEN SETTINGS ===
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# === COLORS (VGA Palette) ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)     
PURPLE = (128, 0, 128)

#GREENS
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
BRIGHT_GREEN = GREEN

#BROWNS
DARK_BROWN = (139, 69, 19)
BROWN = (170, 85, 0)
OLIVE_BROWN = (128, 128, 0)
RECESSED_BROWN = (120, 100, 80)
LIGHT_BROWN = (180, 160, 140)

#BLUES
BLUE = (0, 0, 255)
BRIGHT_BLUE = (0, 191, 255)
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 128)
DARK_CYAN = (0, 128, 128)
CORNFLOWER_BLUE = (100, 149, 237) 

#REDS
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
BRIGHT_RED = (255, 100, 100)
DARK_RED = (128, 0, 0)
RUST_RED = (160, 60, 50)
DARK_COPPER = (184, 115, 51)

# Gray scale refinement (fixing naming confusion)
VERY_DARK_GRAY = (60, 60, 60)       #Disabled Text
DARKEST_GRAY = (85, 85, 85)         # Button backgrounds (pressed state)
GRAY = (128, 128, 128)              # Medium gray for borders
DARK_GRAY = (170, 170, 170)         # Button backgrounds (normal state)  
LIGHTEST_GRAY = (200, 200, 200)     # Text input borders (inactive)

# === CHARACTER CREATION UI COLORS ===
# Softer, more readable versions for UI text
TITLE_GREEN = (85, 255, 85)      # Softer green for titles (less harsh than pure green)
SOFT_YELLOW = (255, 255, 85)     # Warmer yellow for subtitles
WARNING_RED = (170, 0, 0)        # Muted red for warnings (not alarming)

# === BUTTON COLOR SCHEMES ===
# Standard button colors (used by most screens)
BUTTON_NORMAL_BG = GRAY
BUTTON_NORMAL_BORDER = WHITE
BUTTON_NORMAL_TEXT = WHITE   #ORG DARK_BROWN

BUTTON_SELECTED_BG = YELLOW
BUTTON_SELECTED_BORDER = WHITE
BUTTON_SELECTED_TEXT = BLACK

BUTTON_DISABLED_BG = DARK_GRAY
BUTTON_DISABLED_BORDER = DARK_GRAY
BUTTON_DISABLED_TEXT = VERY_DARK_GRAY

# === IMAGE LOADING CONFIGURATION ===
# Standardized image dimensions (makes resizing consistent)
IMAGE_STANDARD_WIDTH = 1024
IMAGE_STANDARD_HEIGHT = 510
IMAGE_CHARACTER_TABLE_WIDTH = 1024
IMAGE_CHARACTER_TABLE_MAX_HEIGHT = 300
ICON_SIZE = 32  # Item icon standard size

# Party display constants
PARTY_PANEL_WIDTH = 138
PARTY_PANEL_X = 1024 - PARTY_PANEL_WIDTH
PORTRAIT_SIZE = 110
PORTRAIT_SPACING = 10
FRAME_THICKNESS = 3

# === DIALOGUE SYSTEM CONSTANTS ===
DIALOGUE_PORTRAIT_SIZE = 200
DIALOGUE_PORTRAIT_X = 50
DIALOGUE_PORTRAIT_Y = 100

DIALOGUE_AREA_X = 270
DIALOGUE_AREA_Y = 100
DIALOGUE_AREA_WIDTH = 700
DIALOGUE_AREA_HEIGHT = 400
DIALOGUE_AREA_PADDING = 20

DIALOGUE_TITLE_Y = 120
DIALOGUE_TEXT_START_Y = 160
DIALOGUE_TEXT_LINE_HEIGHT = 25
DIALOGUE_OPTIONS_START_Y_OFFSET = 40
DIALOGUE_OPTION_HEIGHT = 30
DIALOGUE_OPTION_PADDING = 5

DIALOGUE_BUTTON_Y = 520
DIALOGUE_BUTTON_WIDTH = 120
DIALOGUE_BUTTON_HEIGHT = 35
DIALOGUE_BUTTON_SPACING = 140

# NPC Selection Button Layout Constants
NPC_BUTTON_HEIGHT = 40
NPC_BUTTON_SPACING = 15
NPC_BUTTONS_PER_ROW = 6
NPC_BUTTON_WIDTH = 130

# Dialogue colors
DIALOGUE_BG_COLOR = (20, 20, 20)
DIALOGUE_BORDER_COLOR = WHITE
DIALOGUE_TEXT_COLOR = WHITE
DIALOGUE_TITLE_COLOR = (0, 255, 0)
DIALOGUE_OPTION_COLOR = (0, 255, 0)
DIALOGUE_OPTION_HOVER_COLOR = (255, 255, 0)
DIALOGUE_OPTION_BG_HOVER = (40, 40, 40)

# === PROFESSIONAL ASSET PATH STRUCTURE ===

# Base paths
ASSETS_PATH = "assets"
IMAGES_PATH = os.path.join(ASSETS_PATH, "images")
FONTS_PATH = os.path.join(ASSETS_PATH, "fonts")

# Background image paths (organized by type)
BACKGROUNDS_PATH = os.path.join(IMAGES_PATH, "backgrounds")
UI_BACKGROUNDS_PATH = os.path.join(BACKGROUNDS_PATH, "ui")
LOCATION_BACKGROUNDS_PATH = os.path.join(BACKGROUNDS_PATH, "locations")
SHOP_BACKGROUNDS_PATH = os.path.join(BACKGROUNDS_PATH, "shops")

# Icon paths (organized by category)
ICONS_PATH = os.path.join(IMAGES_PATH, "icons")
ITEM_ICONS_PATH = os.path.join(ICONS_PATH, "items")
UI_ICONS_PATH = os.path.join(ICONS_PATH, "ui")
CHARACTER_ICONS_PATH = os.path.join(ICONS_PATH, "characters")

# Portrait paths (for party status system)
NPC_PORTRAITS_PATH = os.path.join(CHARACTER_ICONS_PATH, "npc_portraits")
PLAYER_PORTRAITS_PATH = os.path.join(CHARACTER_ICONS_PATH, "player_portraits")
MALE_PORTRAITS_PATH = os.path.join(PLAYER_PORTRAITS_PATH, "male")
FEMALE_PORTRAITS_PATH = os.path.join(PLAYER_PORTRAITS_PATH, "female")

# Sprite paths (ready for combat system)
SPRITES_PATH = os.path.join(IMAGES_PATH, "sprites")
PLAYER_SPRITES_PATH = os.path.join(SPRITES_PATH, "player")
ENEMY_SPRITES_PATH = os.path.join(SPRITES_PATH, "enemies")
EFFECTS_SPRITES_PATH = os.path.join(SPRITES_PATH, "effects")
LANDSCAPE_SPRITES_PATH = os.path.join(SPRITES_PATH, "landscape")
COMBAT_OBSTACLES_PATH = os.path.join(SPRITES_PATH, "items")
COMBAT_WALLS_PATH = os.path.join(SPRITES_PATH, "walls")

# Specific file paths (updated to new structure)
TABLE_IMAGE = os.path.join(UI_BACKGROUNDS_PATH, "character_creation_table.jpg")
WELCOME_IMAGE = os.path.join(LOCATION_BACKGROUNDS_PATH, "town_welcome.jpg")
TAVERN_IMAGE = os.path.join(LOCATION_BACKGROUNDS_PATH, "tavern_interior.jpg")

# Future location images (ready when you create them)
SWAMP_CHURCH_IMAGE = os.path.join(LOCATION_BACKGROUNDS_PATH, "swamp_church_exterior.jpg")
HILL_RUINS_IMAGE = os.path.join(LOCATION_BACKGROUNDS_PATH, "hill_ruins_entrance.jpg")
REFUGEE_CAMP_IMAGE = os.path.join(LOCATION_BACKGROUNDS_PATH, "refugee_camp_overview.jpg")
MAYOR_OFFICE_IMAGE = os.path.join(LOCATION_BACKGROUNDS_PATH, "mayor_office.jpg")

# Shop images (ready for expansion)
GENERAL_STORE_IMAGE = os.path.join(SHOP_BACKGROUNDS_PATH, "general_store.jpg")
GAMBLING_DEN_IMAGE = os.path.join(SHOP_BACKGROUNDS_PATH, "gambling_den.jpg")
ARMORER_SHOP_IMAGE = os.path.join(SHOP_BACKGROUNDS_PATH, "armorer_shop.jpg")

# Navigation Tile images:
TILES_PATH = os.path.join(IMAGES_PATH, "tiles")
TERRAIN_TILES_PATH = os.path.join(TILES_PATH, "terrain") 
BUILDING_TILES_PATH = os.path.join(TILES_PATH, "buildings")
DECORATIONS_TILES_PATH = os.path.join(TILES_PATH, "decorations")
ANIMATED_TILES_PATH = os.path.join(TILES_PATH, "animated")
COMBAT_FLOORS_PATH = os.path.join(TILES_PATH, "terrain")

# Sprite sizes for combat
COMBAT_TILE_SIZE = 48
COMBAT_OBSTACLE_SIZE = 32
COMBAT_FLOOR_TILE_SIZE = 16

# === FONT LOADING SYSTEM ===

# Font Configuration - CHANGE THESE TO SWAP FONTS!
GAME_FONT_FILE = "MedievalSharp-Regular.ttf"  # ← Change this to swap fonts!
GAME_FONT_NAME = "MedievalSharp"  # ← Update this for the console message

# Font size constants (industry standard: define sizes once)
FONT_SIZE_LARGE = 32
FONT_SIZE_MEDIUM = 26
FONT_SIZE_SMALL = 22
FONT_SIZE_TINY = 18
FONT_SIZE_MICRO = 16

# Font size list (for utilities)
FONT_SIZES = {
    'large': FONT_SIZE_LARGE,
    'medium': FONT_SIZE_MEDIUM,
    'small': FONT_SIZE_SMALL,
    'tiny': FONT_SIZE_TINY,
    'micro': FONT_SIZE_MICRO
}

def _create_font(font_path, size, use_system_fallback=True):
    """
    Helper function to create a single font with fallback
    
    Args:
        font_path: Path to the .ttf file (or None for system font)
        size: Font size in pixels
        use_system_fallback: If True, fall back to pygame default font
    
    Returns:
        pygame.font.Font object
    """
    try:
        if font_path and os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        elif use_system_fallback:
            return pygame.font.Font(None, size)
        else:
            raise FileNotFoundError(f"Font file not found: {font_path}")
    except Exception as e:
        if use_system_fallback:
            print(f"   Warning: Using system font fallback for size {size}")
            return pygame.font.Font(None, size)
        raise

def load_fonts():
    """
    Load all game fonts with fallback support
    Returns a dictionary of font objects
    
    To change fonts: Modify GAME_FONT_FILE constant above!
    """
    fonts = {}
    
    # Build full path to font file
    font_path = os.path.join(FONTS_PATH, GAME_FONT_FILE)
    
    # Check if custom font exists
    font_loaded = False
    if os.path.exists(font_path):
        try:
            # Load all font sizes using helper function
            fonts['fantasy_large'] = _create_font(font_path, FONT_SIZE_LARGE, use_system_fallback=False)
            fonts['fantasy_medium'] = _create_font(font_path, FONT_SIZE_MEDIUM, use_system_fallback=False)
            fonts['fantasy_small'] = _create_font(font_path, FONT_SIZE_SMALL, use_system_fallback=False)
            fonts['fantasy_tiny'] = _create_font(font_path, FONT_SIZE_TINY, use_system_fallback=False)
            fonts['fantasy_micro'] = _create_font(font_path, FONT_SIZE_MICRO, use_system_fallback=False)
            fonts['help_text'] = fonts['fantasy_micro']  
            
            print(f"✓ {GAME_FONT_NAME} font loaded successfully!")
            font_loaded = True
            
        except FileNotFoundError as e:
            print(f"✗ Font file not found: {GAME_FONT_FILE}")
            print(f"   Expected location: {font_path}")
        except Exception as e:
            print(f"✗ Error loading font: {e}")
    else:
        print(f"✗ Font file not found: {GAME_FONT_FILE}")
        print(f"   Expected location: {font_path}")
    
    # Fallback to system fonts if custom font failed
    if not font_loaded:
        print("   Loading system font fallbacks...")
        fonts['fantasy_large'] = _create_font(None, FONT_SIZE_LARGE)
        fonts['fantasy_medium'] = _create_font(None, FONT_SIZE_MEDIUM)
        fonts['fantasy_small'] = _create_font(None, FONT_SIZE_SMALL)
        fonts['fantasy_tiny'] = _create_font(None, FONT_SIZE_TINY)
        fonts['fantasy_micro'] = _create_font(None, FONT_SIZE_MICRO)
        fonts['help_text'] = fonts['fantasy_micro']
    
    # Standard font aliases (for backwards compatibility)
    fonts['header'] = fonts['fantasy_large']
    fonts['normal'] = fonts['fantasy_medium']
    fonts['small'] = fonts['fantasy_small']
    fonts['tiny'] = fonts['fantasy_tiny']
    
    return fonts

# === FONT SIZING UTILITIES ===

def get_scaled_font(fonts, base_font_key, scale_factor=1.0):
    """Get a font scaled by a factor"""
    base_font = fonts.get(base_font_key, fonts['normal'])
    if hasattr(base_font, 'get_height'):
        new_size = max(12, int(base_font.get_height() * scale_factor))
        
        # Use the same font configuration as load_fonts()
        font_path = os.path.join(FONTS_PATH, GAME_FONT_FILE)
        
        try:
            if os.path.exists(font_path):
                return pygame.font.Font(font_path, new_size)
        except Exception as e:
            print(f"Warning: Could not scale font, using system fallback: {e}")
        
        # Fallback to system font
        return pygame.font.Font(None, new_size)
    return base_font

def get_fitting_font(fonts, text, max_width, font_sizes=['fantasy_large', 'fantasy_medium', 'fantasy_small', 'fantasy_tiny', 'fantasy_micro']):
    """Get the largest font that fits text within max_width"""
    for font_key in font_sizes:
        font = fonts.get(font_key, fonts['normal'])
        if font.size(text)[0] <= max_width:
            return font
    return fonts.get('fantasy_micro', fonts['small'])

def calculate_button_font(fonts, text, button_width, padding=20):
    """Calculate the best font size for button text"""
    available_width = button_width - padding
    return get_fitting_font(fonts, text, available_width)

def wrap_text(text, font, max_width, color=(255, 255, 255)):
    """
    Word wrapping utility - OPTIMIZED VERSION for ANY UI context
    Combines best practices from multiple implementations:
    - Efficient list-based building
    - Explicit long-word handling
    - Flexible color parameter
    - Safety checks for edge cases
    Args:
        text: String to wrap
        font: pygame.Font object
        max_width: Maximum pixel width before wrapping
        color: Text color tuple (default WHITE for general use)
    Returns:
        List of rendered pygame.Surface objects, one per line
    Usage:
        # Combat log (white text)
        wrapped = wrap_text(message, font, 320, (255, 255, 255))
        # Dialogue (custom color)
        wrapped = wrap_text(text, font, 600, DIALOGUE_TEXT_COLOR)
    """
    if not text:  # Safety check for empty/None text
        return []
    
    words = text.split(' ')
    lines = []
    current_line = []  # Use list for efficient joining
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            # Save current line if it exists
            if current_line:
                lines.append(' '.join(current_line))
            
            # Handle words longer than max_width explicitly
            if font.size(word)[0] > max_width:
                lines.append(word)  # Let it overflow - no other choice
                current_line = []
            else:
                current_line = [word]
    
    # Don't forget the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    # Render all lines at once with specified color
    return [font.render(line, True, color) for line in lines]

# === IMAGE LOADING HELPER FUNCTIONS ===

def _create_placeholder_image(width, height, title_text, subtitle_text="Missing Asset"):
    """
    Create professional placeholder for missing images
    
    Args:
        width: Placeholder width in pixels
        height: Placeholder height in pixels
        title_text: Main text (e.g., "TAVERN")
        subtitle_text: Subtitle text (e.g., "Missing: tavern.jpg")
    
    Returns:
        pygame.Surface with placeholder graphics
    """
    placeholder = pygame.Surface((width, height))
    placeholder.fill((40, 40, 40))  # Dark gray background
    pygame.draw.rect(placeholder, WHITE, (0, 0, width, height), 3)  # White border
    
    try:
        font_large = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 24)
        
        # Draw title
        title_surface = font_large.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(width//2, height//2 - 20))
        placeholder.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_surface = font_small.render(subtitle_text, True, (200, 200, 200))
        subtitle_rect = subtitle_surface.get_rect(center=(width//2, height//2 + 20))
        placeholder.blit(subtitle_surface, subtitle_rect)
    except:
        pass  # If font rendering fails, just show blank placeholder
    
    return placeholder


def _load_single_image(filepath, target_size, create_placeholder=True, placeholder_title=""):
    """
    Load and scale a single image with professional error handling
    
    Args:
        filepath: Full path to image file
        target_size: Tuple of (width, height) for scaling
        create_placeholder: If True, generate placeholder on failure
        placeholder_title: Title for placeholder image (e.g., "TAVERN")
    
    Returns:
        pygame.Surface (loaded image or placeholder) or None
    """
    try:
        # Check if file exists first
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image file not found: {filepath}")
        
        # Load and scale the image
        image = pygame.image.load(filepath)
        scaled_image = pygame.transform.scale(image, target_size)
        return scaled_image
    
    except FileNotFoundError as e:
        # File doesn't exist - create placeholder if requested
        if create_placeholder:
            return _create_placeholder_image(
                target_size[0], 
                target_size[1], 
                placeholder_title.upper().replace('_', ' '),
                f"Missing: {os.path.basename(filepath)}"
            )
        return None
    
    except Exception as e:
        # Some other error (corrupt file, etc.)
        print(f"   Error loading image {filepath}: {e}")
        if create_placeholder:
            return _create_placeholder_image(
                target_size[0], 
                target_size[1], 
                placeholder_title.upper().replace('_', ' '),
                "Load Error"
            )
        return None
    
# === PROFESSIONAL IMAGE LOADING SYSTEM ===

def load_images():
    """
    Professional image loading system with progress tracking
    Uses helper functions for consistent error handling
    """
    print("🎮 Starting asset loading...")
    images = {}
    
    # Progress tracking
    total_assets = 12  # Will be calculated dynamically below
    loaded_count = 0
    
    def update_progress(asset_name, success=True):
        """Update and display loading progress"""
        nonlocal loaded_count
        loaded_count += 1
        progress = (loaded_count / total_assets) * 100
        status = "✓" if success else "✗"
        print(f"  {status} [{progress:5.1f}%] {asset_name}")
    
    # === CHARACTER TABLE (Special Case) ===
    # This one has unique dimensions, so handle separately
    try:
        character_table = pygame.image.load(TABLE_IMAGE)
        original_width, original_height = character_table.get_size()
        target_width = IMAGE_CHARACTER_TABLE_WIDTH
        target_height = min(IMAGE_CHARACTER_TABLE_MAX_HEIGHT, 
                          int(target_width * original_height / original_width))
        images['character_table'] = pygame.transform.scale(character_table, 
                                                          (target_width, target_height))
        update_progress("Character table image")
    except:
        images['character_table'] = None
        update_progress("Character table image", False)
    
    # === LOCATION BACKGROUND IMAGES ===
    # Dictionary of location key -> filename
    location_images = {
        'welcome': 'town_welcome.jpg',
        'tavern': 'tavern_interior.jpg',
        'swamp_church': 'swamp_church_exterior.jpg',
        'hill_ruins': 'hill_ruins_entrance.jpg',
        'refugee_camp': 'refugee_camp_overview.jpg',
        'mayor_office': 'mayor_office.jpg',
        'broken_blade_main': 'tavern_interior.jpg',  # Reuses tavern image
        'broken_blade': 'tavern_interior.jpg'  # Reuses tavern image
    }
    
    # Update total assets count
    total_assets = 1 + len(location_images) + 3  # table + locations + shops
    
    # Load all location backgrounds using helper function
    for key, filename in location_images.items():
        filepath = os.path.join(LOCATION_BACKGROUNDS_PATH, filename)
        images[key] = _load_single_image(
            filepath, 
            (IMAGE_STANDARD_WIDTH, IMAGE_STANDARD_HEIGHT),
            create_placeholder=True,
            placeholder_title=key
        )
        update_progress(f"{key.title().replace('_', ' ')} background", 
                       success=(images[key] is not None))
    
    # === SHOP BACKGROUND IMAGES ===
    shop_images = {
        'general_store': 'general_store.jpg',
        'gambling_den': 'gambling_den.jpg',
        'armorer_shop': 'armorer_shop.jpg'
    }
    
    # Load all shop backgrounds using helper function
    for key, filename in shop_images.items():
        filepath = os.path.join(SHOP_BACKGROUNDS_PATH, filename)
        images[key] = _load_single_image(
            filepath,
            (IMAGE_STANDARD_WIDTH, IMAGE_STANDARD_HEIGHT),
            create_placeholder=True,
            placeholder_title=key
        )
        update_progress(f"{key.title().replace('_', ' ')} shop background",
                       success=(images[key] is not None))
    
    # === FUTURE ASSET CATEGORIES ===
    # Initialize empty dictionaries for future expansion
    images['item_icons'] = {}
    images['character_portraits'] = {}
    images['ui_icons'] = {}
    
    # === LOADING SUMMARY ===
    total_backgrounds = len(location_images) + len(shop_images) + 1  # +1 for table
    successful_loads = sum(1 for k, v in images.items() 
                          if v is not None and k not in ['item_icons', 'character_portraits', 
                                                          'enemy_sprites', 'player_sprites',
                                                          'spell_effects', 'ui_icons'])
    
    print(f"\n🎮 Asset Loading Summary:")
    print(f"  ✓ Background images: {successful_loads}/{total_backgrounds}")
    print(f"  ✓ Item icons: {len(images.get('item_icons', {}))} loaded")
    print(f"  📁 Asset pipeline ready for expansion!")
    
    return images

# === BUTTON SIZE STANDARDS ===
BUTTON_SIZES = {
    'large': (220, 70),
    'medium': (160, 50), 
    'small': (120, 40),
    'tiny': (100, 30)
}

# BORDER THICKNESS
BORDER_THICKNESS = 6

# === STANDARD SPACING VALUES ===
SPACING = {
    'margin': 20,
    'border': 30,
    'line_height': 22,
    'button_gap': 20
}

# === STANDARDIZED 3-ZONE LAYOUT SYSTEM ===
LAYOUT_IMAGE_Y = 5
LAYOUT_IMAGE_HEIGHT = 510
LAYOUT_DIALOG_Y = LAYOUT_IMAGE_Y + LAYOUT_IMAGE_HEIGHT + 9  # 524
LAYOUT_DIALOG_HEIGHT = 180
LAYOUT_BUTTON_Y = LAYOUT_DIALOG_Y + LAYOUT_DIALOG_HEIGHT + 7 
LAYOUT_BUTTON_HEIGHT = 60

# Helper calculations
LAYOUT_DIALOG_TEXT_Y = LAYOUT_DIALOG_Y + 20  #
LAYOUT_BUTTON_CENTER_Y = LAYOUT_BUTTON_Y + 10  # Button positioning

# Help text positioning (below buttons)
LAYOUT_HELP_TEXT_Y = 750  # visible on 768px
LAYOUT_HELP_TEXT_FONT_SIZE = 16  # Tiny font for subtle help

# Multi-button layout system (for screens with many buttons)
LAYOUT_BUTTON_SMALL_HEIGHT = 30  # Smaller buttons for multi-row screens
LAYOUT_BUTTON_ZONE_MULTI = 80    # Taller zone for 2+ rows of buttons
LAYOUT_BUTTON_MULTI_Y = LAYOUT_DIALOG_Y + LAYOUT_DIALOG_HEIGHT + 1  # 762
LAYOUT_BUTTON_MULTI_CENTER_Y = LAYOUT_BUTTON_MULTI_Y + 10  # First row positioning


def calculate_button_layout(num_buttons, screen_width=1024, button_width=150, spacing=15):
    """Calculate evenly spaced button positions"""
    total_width = num_buttons * button_width + (num_buttons - 1) * spacing
    start_x = (screen_width - total_width) // 2
    
    positions = []
    current_x = start_x
    for i in range(num_buttons):
        positions.append(current_x)
        current_x += button_width + spacing
    
    return positions, button_width


# === INTRO SEQUENCE LAYOUT CONSTANTS ===
# Full-screen cinematic layout for narrative sequences

INTRO_TITLE_Y = 80
INTRO_TITLE_DECORATION_OFFSET = 50
INTRO_CONTENT_START_Y = 180
INTRO_CONTENT_LINE_SPACING = 25
INTRO_CONTENT_PARAGRAPH_SPACING = 15
INTRO_CONTENT_MAX_WIDTH = 800
INTRO_BUTTON_Y = 600
INTRO_BUTTON_WIDTH = 160
INTRO_BUTTON_HEIGHT = 50
INTRO_BUTTON_SPACING = 80

# Atmospheric background constants
INTRO_OVERLAY_ALPHA = 180  # Semi-transparent overlay for text readability
INTRO_MOUNTAIN_HEIGHT_RATIO = 0.5  # Mountains take up 50% of screen height
INTRO_TOWN_Y_OFFSET = 80  # Town positioned below center
INTRO_BUILDING_WIDTH_RATIO = 0.1  # Building width as ratio of screen width

# Color variations for atmospheric backgrounds (brighter for visibility)
INTRO_SKY_DUSK = (60, 50, 80)  # Much lighter blue-purple
INTRO_SKY_NIGHT = (40, 35, 65)  # Lighter night scenes  
INTRO_MOUNTAIN_SILHOUETTE = (80, 70, 90)  # Much lighter mountains
INTRO_BUILDING_SILHOUETTE = (70, 60, 85)  # Lighter buildings
INTRO_WARM_LIGHT = (255, 200, 120)  # Brighter warm light
INTRO_DISTANT_LIGHT = (255, 255, 180)  # Brighter distant lights

# === ANIMATION SYSTEM CONSTANTS ===
ANIMATION_SPEED = 300  # milliseconds per frame
TITLE_SPRITE_SIZE = (64, 64)  # Your campfire size

# Sprite paths for title screen (update path to match yours)
TITLE_ANIMATIONS = {
    'campfire': 'assets/images/sprites/fire/campfire_animation.png',
    'torch': 'assets/images/sprites/fire/torch_animation.png',  
    'star_twinkle': 'assets/images/sprites/landscape/star_twinkle_1.png' 
}

# Screen exclusion lists - centralized for maintainability
# Overlay exclusion - screens where overlays should not appear
OVERLAY_RESTRICTED_SCREENS = {
    'game_title', 'developer_splash',  # Remove main_menu from here
    'stats', 'gender', 'name', 'portrait_selection', 'custom_name', 
    'name_confirm', 'gold', 'trinket', 'summary', 'welcome',
    'dice_bets', 'dice_rolling', 'dice_results', 'dice_rules', 'merchant_shop'
}

# Save/Load exclusion - screens where save/load operations don't make sense
SAVE_LOAD_RESTRICTED_SCREENS = {
    'game_title', 'developer_splash', 'main_menu',  # Keep main_menu here
    'stats', 'gender', 'name', 'portrait_selection', 'custom_name', 
    'name_confirm', 'gold', 'trinket', 'summary', 'welcome',
    'dice_bets', 'dice_rolling', 'dice_results', 'dice_rules', 'merchant_shop'
}

# Overlay access control - centralized configuration
MAIN_MENU_ALLOWED_OVERLAYS = ['load_game']  

