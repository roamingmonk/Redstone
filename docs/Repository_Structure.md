## Repository Structure (generated 2025-10-12 14:37)
```text
Folder PATH listing for volume OS
Volume serial number is 86A5-907E
C:.
|   game_state.py
|   input_handler.py
|   main.py
|   README.md
|   test_combat_data_loading.py
|   
+---.vscode
|       settings.json
|       
+---assets
|   +---borders
|   |       gold_frame_64_ugly.png
|   |       
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
|       |   |   |       henrik_portrait.jpg
|       |   |   |       jenna_portrait.jpg
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
|       |   |       |       player_female_06.jpg
|       |   |       |       
|       |   |       \---male
|       |   |               player_male_01.jpg
|       |   |               player_male_02.jpg
|       |   |               player_male_03.jpg
|       |   |               player_male_04.jpg
|       |   |               player_male_05.jpg
|       |   |               player_male_06.jpg
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
|       |   |       shortbow.png
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
|       |   +---items
|       |   |       barrel.png
|       |   |       
|       |   +---landscape
|       |   |       star_twinkle_1.png
|       |   |       
|       |   \---player
|       \---tiles
|           |       stone_wall.png
|           |       wall_corner_ne.png
|           |       wall_corner_nw.png
|           |       wall_corner_se.png
|           |       wall_corner_sw.png
|           |       wall_east.png
|           |       wall_north.png
|           |       wall_south.png
|           |       wall_west.png
|           |       
|           +---characters
|           |   \---player
|           +---decorations
|           |       gate_north.png
|           |       gate_south.png
|           |       
|           \---terrain
|                   cobblestone_street.png
|                   cobblestone_street_16x16.png
|                   stone_floor_16x16.png
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
|   +---combat
|   |   +---battlefields
|   |   |       small_cellar.json
|   |   |       
|   |   +---encounters
|   |   |       tavern_basement_rats.json
|   |   |       
|   |   \---enemies
|   |           giant_rat.json
|   |           ogre_archer.json
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
|   |       redstone_town_henrik.json
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
|   |       death_quotes.json
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
|   |       species.json
|   |       
|   +---templates
|   |       player_template.json
|   |       
|           
+---docs
|       adding_npc_dialogue.md
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
|       save_slot_2.json
|       save_slot_3.json
|       save_slot_4.json
|       save_slot_5.json
|       
+---screens
|   |   character_creation.py
|   |   character_overlay.py
|   |   gambling_dice.py
|   |   help_overlay.py
|   |   intro_scenes.py
|   |   inventory_overlay.py
|   |   load_game.py
|   |   quest_overlay.py
|   |   redstone_town.py
|   |   redstone_town_navigation.py.OLD
|   |   save_game.py
|   |   statistics_overlay.py
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
|   |   death_overlay.py
|   |   generic_dialogue_handler.py
|   |   notifications.py
|   |   screen_handlers.py
|   |   screen_manager.py
|   |   shopping_overlay.py
|   |   __init__.py
|   |   
|           
+---utils
|   |   animation.py
|   |   combat_loader.py
|   |   combat_sprite_manager.py
|   |   constants.py
|   |   debug_manager.py
|   |   dialogue_ui_utils.py
|   |   graphics.py
|   |   location_loader.py
|   |   narrative_schema.py
|   |   npc_display.py
|   |   npc_manager.py
|   |   overlay_utils.py
|   |   party_display.py
|   |   quest_system.py
|   |   stats_calculator.py
|   |   tabbed_overlay_utils.py
|   |   tile_graphics.py
|   |   xp_manager.py
|   |   __init__.py
|   |   
|           
        
```
