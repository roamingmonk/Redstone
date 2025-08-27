# constants.py 

import pygame
import os

# === SCREEN SETTINGS ===
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# === COLORS (VGA Palette) ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BRIGHT_GREEN = (0, 255, 0)
BRIGHT_RED = (255, 100, 100)
GRAY = (128, 128, 128)
DARK_GRAY = (169, 169, 169)
DARK_BROWN = (139, 69, 19)
BROWN = (170, 85, 0)

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

# === FONT LOADING SYSTEM ===

def load_fonts():
    """
    Load all game fonts with fallback support
    Returns a dictionary of font objects
    """
    fonts = {}
    
    # Try to load MedievalSharp font
    try:
        font_path = os.path.join(FONTS_PATH, "MedievalSharp-Regular.ttf")
        
        # Different sizes for different UI elements
        fonts['fantasy_large'] = pygame.font.Font(font_path, 32)
        fonts['fantasy_medium'] = pygame.font.Font(font_path, 28)
        fonts['fantasy_small'] = pygame.font.Font(font_path, 24)
        fonts['fantasy_tiny'] = pygame.font.Font(font_path, 20)
        fonts['fantasy_micro'] = pygame.font.Font(font_path, 16)
        
        # Standard fonts for different purposes
        fonts['header'] = fonts['fantasy_large']
        fonts['normal'] = fonts['fantasy_medium']
        fonts['small'] = fonts['fantasy_small']
        fonts['tiny'] = fonts['fantasy_tiny']
        
        # Help text font
        fonts['help_text'] = pygame.font.Font(font_path, 16)
        
        print("✓ MedievalSharp font loaded successfully!")
        
    except:
        # Fallback to default fonts if MedievalSharp not found
        print("✗ MedievalSharp font not found, using default fonts")
        fonts['fantasy_large'] = pygame.font.Font(None, 32)
        fonts['fantasy_medium'] = pygame.font.Font(None, 28)
        fonts['fantasy_small'] = pygame.font.Font(None, 24)
        fonts['fantasy_tiny'] = pygame.font.Font(None, 20)
        fonts['fantasy_micro'] = pygame.font.Font(None, 16)
        fonts['help_text'] = pygame.font.Font(None, 16)
        
        # Standard font aliases
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
        try:
            font_path = os.path.join(FONTS_PATH, "MedievalSharp-Regular.ttf")
            return pygame.font.Font(font_path, new_size)
        except:
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

# === PROFESSIONAL IMAGE LOADING SYSTEM ===

def load_images():
    """
    Professional game studio image loading system with progress tracking
    Organized by asset type for easy maintenance and expansion
    """
    print("🎮 Starting asset loading...")
    images = {}
    
    # Asset loading progress tracking
    total_assets = 14 + 19  # backgrounds + icons (update as you add more)
    loaded_count = 0
    
    def update_progress(asset_name, success=True):
        nonlocal loaded_count
        loaded_count += 1
        progress = (loaded_count / total_assets) * 100
        status = "✓" if success else "✗"
        print(f"  {status} [{progress:5.1f}%] {asset_name}")
    
    def create_placeholder_image(width, height, title_text, subtitle_text="Missing Asset"):
        """Create professional placeholder for missing images"""
        placeholder = pygame.Surface((width, height))
        placeholder.fill((40, 40, 40))  # Dark gray
        pygame.draw.rect(placeholder, WHITE, (0, 0, width, height), 3)
        
        try:
            font_large = pygame.font.Font(None, 48)
            font_small = pygame.font.Font(None, 24)
            
            title_surface = font_large.render(title_text, True, WHITE)
            title_rect = title_surface.get_rect(center=(width//2, height//2 - 20))
            placeholder.blit(title_surface, title_rect)
            
            subtitle_surface = font_small.render(subtitle_text, True, (200, 200, 200))
            subtitle_rect = subtitle_surface.get_rect(center=(width//2, height//2 + 20))
            placeholder.blit(subtitle_surface, subtitle_rect)
        except:
            pass
    
        return placeholder
    
    def create_item_fallback_icon(item_name):
        """Create professional fallback icon for missing item images"""
        icon = pygame.Surface((32, 32))
        icon.fill((60, 60, 60))  # Dark background
        pygame.draw.rect(icon, WHITE, (0, 0, 32, 32), 2)  # White border
        
        # Get first letter of item for icon
        letter = item_name[0].upper() if item_name else "?"
        
        try:
            font = pygame.font.Font(None, 20)
            text = font.render(letter, True, WHITE)
            text_rect = text.get_rect(center=(16, 16))
            icon.blit(text, text_rect)
        except:
            pass
        
        return icon




    # === UI BACKGROUND IMAGES ===
    
    # Character creation table
    try:
        character_table = pygame.image.load(TABLE_IMAGE)
        original_width, original_height = character_table.get_size()
        target_width = 1024
        target_height = min(300, int(target_width * original_height / original_width))
        images['character_table'] = pygame.transform.scale(character_table, (target_width, target_height))
        update_progress("Character table image")
    except:
        images['character_table'] = None
        update_progress("Character table image", False)
    
    # === LOCATION BACKGROUND IMAGES ===
    
    location_images = {
        'welcome': WELCOME_IMAGE,
        'tavern': TAVERN_IMAGE,
        'swamp_church': SWAMP_CHURCH_IMAGE,
        'hill_ruins': HILL_RUINS_IMAGE,
        'refugee_camp': REFUGEE_CAMP_IMAGE,
        'mayor_office': MAYOR_OFFICE_IMAGE
    }
    
    for key, image_path in location_images.items():
        try:
            location_img = pygame.image.load(image_path)
            images[key] = pygame.transform.scale(location_img, (1024, 510))
            update_progress(f"{key.title()} background")
        except Exception as e:
                update_progress(f"{key.title()} background", False)
                images[key] = create_placeholder_image(1024, 510, key.upper().replace('_', ' '), f"Missing: {os.path.basename(image_path)}")
    
    # === SHOP BACKGROUND IMAGES ===
    
    shop_images = {
        'general_store': GENERAL_STORE_IMAGE,
        'gambling_den': GAMBLING_DEN_IMAGE,
        'armorer_shop': ARMORER_SHOP_IMAGE
    }
    
    for key, image_path in shop_images.items():
        try:
            shop_img = pygame.image.load(image_path)
            images[key] = pygame.transform.scale(shop_img, (1024, 510))
            update_progress(f"{key.title()} shop background")
        except:
            images[key] = None
            update_progress(f"{key.title()} shop background", False)
    
    # === ITEM ICONS (32x32 PIXEL ART) ===
    
    images['item_icons'] = {}
    
    # Organized item categories (your excellent structure!)
    item_names = [
        # Consumables
        'Strong Ale', 'Trail Rations',
        # Weapons
        'Longsword',
        # Armor
        'Leather Armor', 'Shield',
        # Items
        'Hemp Rope', 'Torch',
        # Character Creation Trinkets (all 12!)
        'Carved bone dice', 'Crystal pendant', 'Wooden doll with button eyes',
        'Tarnished silver locket', 'Smooth river stone with runes', 'Feathered dream catcher',
        'Iron ring with strange symbols', 'Glass vial with swirling mist', 
        'Leather pouch with dried herbs', 'Small bronze mirror', 
        'Twisted driftwood wand', 'Polished obsidian shard',
        # Potions
        'Healing potion'
    ]

    for item_name in item_names:
        # Convert item name to filename (spaces to underscores, lowercase)
        base_filename = item_name.lower().replace(' ', '_')

        # Try PNG first, then JPG (using new item icons path)
        filepath = None
        for extension in ['.png', '.jpg']:
            test_path = os.path.join(ITEM_ICONS_PATH, base_filename + extension)
            if os.path.exists(test_path):
                filepath = test_path
                break

        if not filepath:
            filepath = os.path.join(ITEM_ICONS_PATH, base_filename + '.png')
        
        try:
            icon = pygame.image.load(filepath)
            images['item_icons'][item_name] = pygame.transform.scale(icon, (32, 32))
            print(f"✓ Item icon loaded: {item_name}")
        except Exception as e:
            print(f"✗ Item icon failed: {item_name}")
            print(f"  Tried: {filepath}")
            print(f"  Error: {e}")
            # Create professional fallback icon
            fallback_icon = create_item_fallback_icon(item_name)
            images['item_icons'][item_name] = fallback_icon
            print(f"✓ Using fallback icon for: {item_name}")
            pygame.draw.rect(fallback_icon, (255, 255, 255), (0, 0, 32, 32), 2)
            font = pygame.font.Font(None, 24)
            text = font.render("X", True, (255, 255, 255))
            text_rect = text.get_rect(center=(16, 16))
            fallback_icon.blit(text, text_rect)
            images['item_icons'][item_name] = fallback_icon
            print(f"✗ Using fallback icon for: {item_name}")
    
    # === FUTURE ASSET CATEGORIES ===
    
    # Initialize empty dictionaries for future expansion
    images['character_portraits'] = {}
    images['enemy_sprites'] = {}
    images['player_sprites'] = {}
    images['spell_effects'] = {}
    images['ui_icons'] = {}
    
    # === ASSET LOADING SUMMARY ===
    total_backgrounds = len([k for k in images.keys() if k not in ['item_icons', 'character_portraits']])
    total_icons = len(images.get('item_icons', {}))
    missing_backgrounds = len([k for k, v in images.items() if v is None and k != 'item_icons'])

    print(f"\n🎮 Asset Loading Summary:")
    print(f"  ✓ Background images: {total_backgrounds - missing_backgrounds}/{total_backgrounds}")
    print(f"  ✓ Item icons: {total_icons} loaded")
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
LAYOUT_BUTTON_Y = LAYOUT_DIALOG_Y + LAYOUT_DIALOG_HEIGHT + 9 - 15 # 693
LAYOUT_BUTTON_HEIGHT = 60

# Helper calculations
LAYOUT_DIALOG_TEXT_Y = LAYOUT_DIALOG_Y + 20  # Perfect text positioning
LAYOUT_BUTTON_CENTER_Y = LAYOUT_BUTTON_Y + 10  # Button positioning

# Help text positioning (below buttons)
LAYOUT_HELP_TEXT_Y = 750  # visible on 768px
LAYOUT_HELP_TEXT_FONT_SIZE = 16  # Tiny font for subtle help

# Multi-button layout system (for screens with many buttons)
LAYOUT_BUTTON_SMALL_HEIGHT = 30  # Smaller buttons for multi-row screens
LAYOUT_BUTTON_ZONE_MULTI = 80    # Taller zone for 2+ rows of buttons
LAYOUT_BUTTON_MULTI_Y = LAYOUT_DIALOG_Y + LAYOUT_DIALOG_HEIGHT + 1  # 762
LAYOUT_BUTTON_MULTI_CENTER_Y = LAYOUT_BUTTON_MULTI_Y + 10  # First row positioning