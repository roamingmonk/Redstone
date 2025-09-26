## Repository Structure (generated 2025-09-26 09:07)
```text
Folder PATH listing for volume OS
Volume serial number is 86A5-907E
C:.
|   game_state.py
|   input_handler.py
|   main.py
|   README.md
|   
+---.vscode
|       settings.json
|       
+---assets
|   +---fonts
|   |       MedievalSharp-Regular.ttf
|   |       
|   \---images
|       |   Designer (2).jpg
|       |   Designer (3).jpg
|       |   tavern-gambling.jpg
|       |   
|       +---backgrounds
|       |   +---locations
|       |   |       patron_selection.jpg
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
|       |   |   |       bernard_portrait.jpg
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
|       |   |       broken_compass.jpg
|       |   |       carved_bone_dice.jpg
|       |   |       Carved_bone_dice.PNG
|       |   |       chainmail.PNG
|       |   |       crystal_pendant.jpg
|       |   |       empty_small_leather_pouch_that_jingles.jpg
|       |   |       feathered_dream_catcher.png
|       |   |       glass_vial_with_swirling_mist.png
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
|       |   |       polished_obsidian_shard.jpg
|       |   |       pressed_flower.jpg
|       |   |       quarterstaff.png
|       |   |       rapier.png
|       |   |       shield.PNG
|       |   |       shield_plus_1.PNG
|       |   |       small_brass_key.jpg
|       |   |       small_bronze_mirror.jpg
|       |   |       smooth_river_stone_with_runes.jpg
|       |   |       splint_armor.png
|       |   |       star_map_fragment.jpg
|       |   |       strong_ale.png
|       |   |       tarnished_silver_locket.jpg
|       |   |       thieves_tools.png
|       |   |       tinderbox.png
|       |   |       torch.PNG
|       |   |       trail_rations.PNG
|       |   |       twisted_driftwood_wand.jpg
|       |   |       wooden_dice.jpg
|       |   |       wooden_dice.png
|       |   |       wooden_doll_with_button_eyes.jpg
|       |   |       
|       |   \---ui
|       +---sprites
|       |   +---effects
|       |   +---enemies
|       |   +---fire
|       |   |       campfire_animation.png
|       |   |       torch_animation.png
|       |   |       
|       |   \---player
|       \---tiles
|           |       stone_wall.png
|           |       
|           +---characters
|           |   \---player
|           +---decorations
|           \---terrain
|                   cobblestone_street.png
|                   
+---core
|   |   game_controller.py
|   |   __init__.py
|   |   
|           
+---data
|   |   items.json
|   |   merchants.json
|   |   narrative_schema.json
|   |   __init__.py
|   |   
|   +---dialogues
|   |       broken_blade_garrick.json
|   |       broken_blade_meredith.json
|   |       patron_selection_elara.json
|   |       patron_selection_gareth.json
|   |       patron_selection_lyra.json
|   |       patron_selection_mayor.json
|   |       patron_selection_pete.json
|   |       patron_selection_thorman.json
|   |       redstone_town_bernard.json
|   |       redstone_town_jenna.json
|   |       
|   +---locations
|   |       broken_blade.json
|   |       patron_selection.json
|   |       __init__.py
|   |       
|   +---maps
|   |   |   redstone_town_map.py
|   |   |   
|   |           
|   +---narrative
|   |       intro_sequence.json
|   |       
|   +---npcs
|   |       aldwin_goldenbottem.json
|   |       bernard_mugsworth.json
|   |       elara.json
|   |       gareth.json
|   |       garrick_ironbrew.json
|   |       lyra.json
|   |       meredith_whisperwind.json
|   |       pete_stumblefoot.json
|   |       thorman.json
|   |       
|   +---player
|   |       character_classes.json
|   |       character_classesd.py
|   |       character_names.json
|   |       current_character.json
|   |       low_stats_comments.json
|   |       trinkets.json
|   |       
|   +---templates
|   |       player_template.json
|   |       
|           
+---docs
|       decisions.md
|       project_context copy.md
|       project_context.md
|       Repository_Structure.md
|       
+---game_logic
|   |   character_engine.py
|   |   combat_engine.py
|   |   commerce_engine.py
|   |   data_manager.py
|   |   dialogue_engine.py
|   |   dice_game_engine.py
|   |   event_manager.py
|   |   inventory_engine.py
|   |   item_manager.py
|   |   npc_manager.py
|   |   player_manager.py
|   |   quest_engine.py
|   |   save_manager.py
|   |   
|           
+---saves
|       autosave.json
|       quicksave.json
|       save_slot_1.json
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
|   |   redstone_town.py
|   |   save_game.py
|   |   title_menu.py
|   |   __init__.py
|   |   
|           
+---scripts
|       generate_repo_structure.ps1
|       
+---ui
|   |   base_location.py
|   |   base_location_navigation.py
|   |   combat_system.py
|   |   generic_dialogue_handler.py
|   |   screen_handlers.py
|   |   screen_manager.py
|   |   shopping_overlay.py
|   |   __init__.py
|   |   
|           
+---utils
|   |   animation.py
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
|   |   tile_graphics.py
|   |   xp_manager.py
|   |   __init__.py
|   |   
|           
        
```
