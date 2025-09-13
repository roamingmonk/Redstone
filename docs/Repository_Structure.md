## Repository Structure (generated 2025-09-13 12:40)
```text
Folder PATH listing for volume OS
Volume serial number is 86A5-907E
C:.
|   .gitmessage.txt
|   Design_LatestUpdate.docx
|   game_state.py
|   input_handler.py
|   main.py
|   README.md
|   
+---assets
|   +---fonts
|   |       MedievalSharp-Regular.ttf
|   |       
|   \---images
|       |   a-medieval-fantasy-tavern-gambling-corner-in-classic-1980s-tsr-dandd-art-style-reminiscent-of-larry-.jpg
|       |   Designer (2).jpg
|       |   Designer (3).jpg
|       |   
|       +---backgrounds
|       |   +---locations
|       |   |       tavern_interior.jpg
|       |   |       town_welcome.jpg
|       |   |       
|       |   +---shops
|       |   \---ui
|       |           character_creation_table.jpg
|       |           
|       +---icons
|       |   +---characters
|       |   |   +---npc_portraits
|       |   |   |       elara_portrait.jpg
|       |   |   |       gareth_portrait.jpg
|       |   |   |       garrick_portrait.jpg
|       |   |   |       garrick_portrait.png
|       |   |   |       lyra_portrait.jpg
|       |   |   |       mayor_portrait.jpg
|       |   |   |       mayor_portrait_happy.jpg
|       |   |   |       meredith_portrait.jpg
|       |   |   |       pete_portrait.jpg
|       |   |   |       thorman_portrait.jpg
|       |   |   |       
|       |   |   \---player_portraits
|       |   |       +---active
|       |   |       +---female
|       |   |       |       player_female_01.jpg
|       |   |       |       player_female_02.jpg
|       |   |       |       player_female_03.jpg
|       |   |       |       player_female_04.jpg
|       |   |       |       player_female_05.jpg
|       |   |       |       
|       |   |       \---male
|       |   |               player_male_01.jpg
|       |   |               player_male_02.jpg
|       |   |               player_male_03.jpg
|       |   |               player_male_04.jpg
|       |   |               player_male_05.jpg
|       |   |               
|       |   +---Items
|       |   |       axe.PNG
|       |   |       battleaxe.png
|       |   |       bedroll.PNG
|       |   |       Carved_bone_dice.PNG
|       |   |       chainmail.PNG
|       |   |       Crystal_pendant.jpg
|       |   |       feathered_dream_catcher.jpg
|       |   |       Glass_vial_with_swirling_mist.jpg
|       |   |       healing_potion.PNG
|       |   |       hemp_rope.PNG
|       |   |       holy_symbol.png
|       |   |       iron_ring_with_strange_symbols.jpg
|       |   |       leather_armor.PNG
|       |   |       leather_pouch_with_dried_herbs.jpg
|       |   |       light_crossbow.png
|       |   |       longsword.PNG
|       |   |       mace.png
|       |   |       plate_armor.PNG
|       |   |       Polished_obsidian_shard.jpg
|       |   |       quarterstaff.png
|       |   |       rapier.png
|       |   |       Shield.PNG
|       |   |       shield_plus_1.PNG
|       |   |       small_bronze_mirror.jpg
|       |   |       smooth_river_stone_with_runes.jpg
|       |   |       splint_armor.png
|       |   |       strong_ale.png
|       |   |       tarnished_silver_locket.jpg
|       |   |       thieves_tools.png
|       |   |       torch.PNG
|       |   |       trail_rations.PNG
|       |   |       twisted_driftwood_wand.jpg
|       |   |       wooden_doll_with_button_eyes.jpg
|       |   |       
|       |   \---ui
|       \---sprites
|           +---effects
|           +---enemies
|           \---player
+---core
|   |   game_controller.py
|   |   __init__.py
|   |   
|   \---__pycache__
|           game_controller.cpython-312.pyc
|           __init__.cpython-312.pyc
|           
+---data
|   |   items.json
|   |   merchants.json
|   |   narrative_schema.json
|   |   __init__.py
|   |   
|   +---dialogues
|   |       broken_blade_elara.json
|   |       broken_blade_gareth.json
|   |       broken_blade_garrick.json
|   |       broken_blade_mayor.json
|   |       broken_blade_meredith.json
|   |       
|   +---locations
|   |       broken_blade.json
|   |       patron_selection.json
|   |       __init__.py
|   |       
|   +---narrative
|   |       intro_sequence.json
|   |       
|   +---npcs
|   |       aldwin_goldenbottem.json
|   |       bernard_mugsworth.json
|   |       elara_moonwhisper.json
|   |       gareth_ironwill.json
|   |       garrick_ironbrew.json
|   |       lyra_quickfingers.json
|   |       meredith_whisperwind.json
|   |       pete_stumblefoot.json
|   |       thorman_stormhammer.json
|   |       
|   +---player
|   |       character_classes.py
|   |       character_names.json
|   |       current_character.json
|   |       low_stats_comments.json
|   |       trinkets.json
|   |       
|   \---templates
|           player_template.json
|           
+---docs
|       decisions.md
|       project_context.md
|       
+---game_logic
|   |   character_engine.py
|   |   commerce_engine.py
|   |   data_manager.py
|   |   dialogue_engine.py
|   |   event_manager.py
|   |   inventory_engine.py
|   |   item_manager.py
|   |   npc_manager.py
|   |   player_manager.py
|   |   quest_engine.py
|   |   save_manager.py
|   |   
|   \---__pycache__
|           character_engine.cpython-312.pyc
|           commerce_engine.cpython-312.pyc
|           data_manager.cpython-312.pyc
|           dialogue_engine.cpython-312.pyc
|           event_manager.cpython-312.pyc
|           inventory_engine.cpython-312.pyc
|           item_manager.cpython-312.pyc
|           npc_manager.cpython-312.pyc
|           quest_engine.cpython-312.pyc
|           save_manager.cpython-312.pyc
|           
+---saves
|       autosave.json
|       quicksave.json
|       save_slot_1.json
|       save_slot_2.json
|       save_slot_3.json
|       
+---screens
|   |   character_advancement.py
|   |   character_creation.py
|   |   character_overlay.py
|   |   gambling_dice.py
|   |   help_overlay.py
|   |   intro_scenes.py
|   |   inventory_overlay.py
|   |   load_game.py
|   |   quest_overlay.py
|   |   save_game.py
|   |   shopping.py
|   |   title_menu.py
|   |   __init__.py
|   |   
|   \---__pycache__
|           character_advancement.cpython-312.pyc
|           character_creation.cpython-312.pyc
|           character_overlay.cpython-312.pyc
|           gambling_dice.cpython-312.pyc
|           help_overlay.cpython-312.pyc
|           intro_scenes.cpython-312.pyc
|           inventory_overlay.cpython-312.pyc
|           load_game.cpython-312.pyc
|           quest_overlay.cpython-312.pyc
|           save_game.cpython-312.pyc
|           title_menu.cpython-312.pyc
|           __init__.cpython-312.pyc
|           
+---ui
|   |   base_location.py
|   |   generic_dialogue_handler.py
|   |   screen_handlers.py
|   |   screen_manager.py
|   |   __init__.py
|   |   
|   \---__pycache__
|           base_location.cpython-312.pyc
|           generic_dialogue_handler.cpython-312.pyc
|           screen_handlers.cpython-312.pyc
|           screen_manager.cpython-312.pyc
|           __init__.cpython-312.pyc
|           
+---utils
|   |   constants.py
|   |   debug_manager.py
|   |   dialogue_ui_utils.py
|   |   graphics.py
|   |   location_loader.py
|   |   narrative_schema.py
|   |   npc_display.py
|   |   overlay_utils.py
|   |   party_display.py
|   |   quest_system.py
|   |   tabbed_overlay_utils.py
|   |   __init__.py
|   |   
|   \---__pycache__
|           constants.cpython-312.pyc
|           debug_manager.cpython-312.pyc
|           dialogue_ui_utils.cpython-312.pyc
|           graphics.cpython-312.pyc
|           location_loader.cpython-312.pyc
|           narrative_schema.cpython-312.pyc
|           npc_display.cpython-312.pyc
|           overlay_utils.cpython-312.pyc
|           party_display.cpython-312.pyc
|           quest_system.cpython-312.pyc
|           tabbed_overlay_utils.cpython-312.pyc
|           __init__.cpython-312.pyc
|           
\---__pycache__
        game_state.cpython-312.pyc
        input_handler.cpython-312.pyc
        
```

## Git-tracked files
```text
.gitignore.txt
Design_LatestUpdate.docx
README.md
__pycache__/game_state.cpython-312.pyc
assets/fonts/MedievalSharp-Regular.ttf
assets/images/Designer (2).jpg
assets/images/Designer (3).jpg
assets/images/a-medieval-fantasy-tavern-gambling-corner-in-classic-1980s-tsr-dandd-art-style-reminiscent-of-larry-.jpg
assets/images/backgrounds/Locations/tavern_interior.jpg
assets/images/backgrounds/Locations/town_welcome.jpg
assets/images/backgrounds/ui/character_creation_table.jpg
assets/images/icons/Items/Carved_bone_dice.PNG
assets/images/icons/Items/Crystal_pendant.jpg
assets/images/icons/Items/Glass_vial_with_swirling_mist.jpg
assets/images/icons/Items/Polished_obsidian_shard.jpg
assets/images/icons/Items/Shield.PNG
assets/images/icons/Items/axe.PNG
assets/images/icons/Items/battleaxe.png
assets/images/icons/Items/bedroll.PNG
assets/images/icons/Items/chainmail.PNG
assets/images/icons/Items/feathered_dream_catcher.jpg
assets/images/icons/Items/healing_potion.PNG
assets/images/icons/Items/hemp_rope.PNG
assets/images/icons/Items/holy_symbol.png
assets/images/icons/Items/iron_ring_with_strange_symbols.jpg
assets/images/icons/Items/leather_armor.PNG
assets/images/icons/Items/leather_pouch_with_dried_herbs.jpg
assets/images/icons/Items/light_crossbow.png
assets/images/icons/Items/longsword.PNG
assets/images/icons/Items/mace.png
assets/images/icons/Items/plate_armor.PNG
assets/images/icons/Items/quarterstaff.png
assets/images/icons/Items/rapier.png
assets/images/icons/Items/shield_plus_1.PNG
assets/images/icons/Items/small_bronze_mirror.jpg
assets/images/icons/Items/smooth_river_stone_with_runes.jpg
assets/images/icons/Items/splint_armor.png
assets/images/icons/Items/strong_ale.png
assets/images/icons/Items/tarnished_silver_locket.jpg
assets/images/icons/Items/thieves_tools.png
assets/images/icons/Items/torch.PNG
assets/images/icons/Items/trail_rations.PNG
assets/images/icons/Items/twisted_driftwood_wand.jpg
assets/images/icons/Items/wooden_doll_with_button_eyes.jpg
assets/images/icons/characters/npc_portraits/elara_portrait.jpg
assets/images/icons/characters/npc_portraits/gareth_portrait.jpg
assets/images/icons/characters/npc_portraits/garrick_portrait.jpg
assets/images/icons/characters/npc_portraits/garrick_portrait.png
assets/images/icons/characters/npc_portraits/lyra_portrait.jpg
assets/images/icons/characters/npc_portraits/mayor_portrait.jpg
assets/images/icons/characters/npc_portraits/mayor_portrait_happy.jpg
assets/images/icons/characters/npc_portraits/meredith_portrait.jpg
assets/images/icons/characters/npc_portraits/pete_portrait.jpg
assets/images/icons/characters/npc_portraits/thorman_portrait.jpg
assets/images/icons/characters/player_portraits/female/player_female_01.jpg
assets/images/icons/characters/player_portraits/female/player_female_02.jpg
assets/images/icons/characters/player_portraits/female/player_female_03.jpg
assets/images/icons/characters/player_portraits/female/player_female_04.jpg
assets/images/icons/characters/player_portraits/female/player_female_05.jpg
assets/images/icons/characters/player_portraits/male/player_male_01.jpg
assets/images/icons/characters/player_portraits/male/player_male_02.jpg
assets/images/icons/characters/player_portraits/male/player_male_03.jpg
assets/images/icons/characters/player_portraits/male/player_male_04.jpg
assets/images/icons/characters/player_portraits/male/player_male_05.jpg
core/__init__.py
core/__pycache__/__init__.cpython-312.pyc
core/__pycache__/game_controller.cpython-312.pyc
core/game_controller.py
data/__init__.py
data/dialogues/broken_blade_gareth.json
data/dialogues/broken_blade_garrick.json
data/dialogues/broken_blade_mayor.json
data/dialogues/broken_blade_meredith.json
data/items.json
data/locations/__init__.py
data/locations/broken_blade.json
data/locations/patron_selection.json
data/merchants.json
data/narrative/intro_sequence.json
data/narrative_schema.json
data/npcs/aldwin_goldenbottem.json
data/npcs/bernard_mugsworth.json
data/npcs/elara_moonwhisper.json
data/npcs/gareth_ironwill.json
data/npcs/garrick_ironbrew.json
data/npcs/lyra_quickfingers.json
data/npcs/meredith_whisperwind.json
data/npcs/pete_stumblefoot.json
data/npcs/thorman_stormhammer.json
data/player/character_classes.py
data/player/character_names.json
data/player/current_character.json
data/player/low_stats_comments.json
data/player/trinkets.json
data/templates/player_template.json
docs/decisions.md
docs/project_context.md
docs/project_context2.md
game_logic/__init__.py
game_logic/__pycache__/__init__.cpython-312.pyc
game_logic/__pycache__/item_manager.cpython-312.pyc
game_logic/__pycache__/location_manager.cpython-312.pyc
game_logic/__pycache__/npc_manager.cpython-312.pyc
game_logic/__pycache__/player_manager.cpython-312.pyc
game_logic/character_engine.py
game_logic/commerce_engine.py
game_logic/data_manager.py
game_logic/dialogue_engine.py
game_logic/event_manager.py
game_logic/inventory_engine.py
game_logic/item_manager.py
game_logic/npc_manager.py
game_logic/player_manager.py
game_logic/quest_engine.py
game_logic/save_manager.py
game_state.py
input_handler.py
main.py
saves/quicksave.json
saves/save_slot_1.json
saves/save_slot_2.json
saves/save_slot_3.json
screens/__init__.py
screens/__pycache__/__init__.cpython-312.pyc
screens/__pycache__/character_creation.cpython-312.pyc
screens/__pycache__/character_sheet.cpython-312.pyc
screens/__pycache__/gambling_dice.cpython-312.pyc
screens/__pycache__/help_screen.cpython-312.pyc
screens/__pycache__/inventory.cpython-312.pyc
screens/__pycache__/load_game.cpython-312.pyc
screens/__pycache__/quest_log.cpython-312.pyc
screens/__pycache__/save_game.cpython-312.pyc
screens/__pycache__/shopping.cpython-312.pyc
screens/__pycache__/tavern.cpython-312.pyc
screens/__pycache__/title_menu.cpython-312.pyc
screens/character_advancement.py
screens/character_creation.py
screens/character_overlay.py
screens/character_sheetOLD.py
screens/gambling_dice.py
screens/help_overlay.py
screens/help_screenOLD.py
screens/intro_scenes.py
screens/inventoryOLD.py
screens/inventory_overlay.py
screens/load_game.py
screens/quest_logOLD.py
screens/quest_overlay.py
screens/save_game.py
screens/shopping.py
screens/title_menu.py
ui/base_location.py
ui/generic_dialogue_handler.py
ui/screen_handlers.py
ui/screen_manager.py
utils/__init__.py
utils/__pycache__/__init__.cpython-312.pyc
utils/__pycache__/constants.cpython-312.pyc
utils/__pycache__/graphics.cpython-312.pyc
utils/__pycache__/overlay_utils.cpython-312.pyc
utils/__pycache__/party_display.cpython-312.pyc
utils/__pycache__/quest_system.cpython-312.pyc
utils/constants.py
utils/debug_manager.py
utils/dialogue_ui_utils.py
utils/graphics.py
utils/location_loader.py
utils/narrative_schema.py
utils/npc_display.py
utils/overlay_utils.py
utils/party_display.py
utils/quest_system.py
utils/tabbed_overlay_utils.py
```
