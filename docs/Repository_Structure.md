## Repository Structure (generated 2025-11-11 08:51)
```text
Folder PATH listing
Volume serial number is 36E2-184C
E:.
|   game_state.py
|   input_handler.py
|   main.py
|   README.md
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
|       |   |   |   altar.png
|       |   |   |   book.png
|       |   |   |   chest.png
|       |   |   |   default_portrait.aseprite
|       |   |   |   default_portrait.png
|       |   |   |   door.png
|       |   |   |   object_examination.png
|       |   |   |   ritual.png
|       |   |   |   symbols.png
|       |   |   |   
|       |   |   +---npc_portraits
|       |   |   |       bernard_portrait.jpg
|       |   |   |       cassia_portrait.jpg
|       |   |   |       default_portrait.jpg
|       |   |   |       elara_portrait.jpg
|       |   |   |       gareth_portrait.jpg
|       |   |   |       garrick_portrait.jpg
|       |   |   |       garrick_portrait.png
|       |   |   |       henrik_portrait.jpg
|       |   |   |       jenna_portrait.jpg
|       |   |   |       leader_portrait.jpg
|       |   |   |       lyra_portrait.jpg
|       |   |   |       marta_portrait.jpg
|       |   |   |       mayor_portrait.jpg
|       |   |   |       mayor_portrait_happy.jpg
|       |   |   |       meredith_portrait.jpg
|       |   |   |       pete_portrait.jpg
|       |   |   |       swamp_church_altar.aseprite
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
|       |   |       aethel_ore_sample.png
|       |   |       alchemist_fire.png
|       |   |       ancient_coins.png
|       |   |       antidote.png
|       |   |       axe.PNG
|       |   |       battleaxe.png
|       |   |       bedroll.PNG
|       |   |       bone_fragment.png
|       |   |       bracers_armor.png
|       |   |       broken_compass.jpg
|       |   |       broken_compass.png
|       |   |       broken_holy_symbol.png
|       |   |       carved_bone_dice.jpg
|       |   |       Carved_bone_dice.PNG
|       |   |       chainmail.PNG
|       |   |       cheap_cloak.png
|       |   |       coal_ore.png
|       |   |       crude_armor_scraps.png
|       |   |       crude_shortbow.png
|       |   |       crystal_pendant.jpg
|       |   |       cult_documents.png
|       |   |       cult_robes.png
|       |   |       cursed_talisman.png
|       |   |       diseased_fang.png
|       |   |       elixir_of_vigor.png
|       |   |       empty_bottle.png
|       |   |       empty_small_leather_pouch_that_jingles.png
|       |   |       feathered_dream_catcher.png
|       |   |       glass_vial_with_swirling_mist.png
|       |   |       glowcap_mushrooms.png
|       |   |       greater_healing_potion.png
|       |   |       healing_potion.PNG
|       |   |       healing_scroll.png
|       |   |       hemp_rope.PNG
|       |   |       henriks_lantern.PNG
|       |   |       hill_ruins_dungeon_key.png
|       |   |       holy_symbol.png
|       |   |       holy_water.png
|       |   |       iron_ore.png
|       |   |       iron_ring_with_strange_symbols.jpg
|       |   |       leather_armor.PNG
|       |   |       leather_pouch_with_dried_herbs.png
|       |   |       light_crossbow.png
|       |   |       lockpicks.png
|       |   |       longsword.PNG
|       |   |       mace.png
|       |   |       marcus_masterwork_elixir.png
|       |   |       merediths_silver_ring.png
|       |   |       plate_armor.PNG
|       |   |       polished_obsidian_shard.jpg
|       |   |       potion_of_clarity.png
|       |   |       pressed_flower.jpg
|       |   |       pressed_flowers.png
|       |   |       quarterstaff.png
|       |   |       rapier.png
|       |   |       rare_gem.png
|       |   |       rat_pelt.png
|       |   |       rat_tail.png
|       |   |       restoration_draught.png
|       |   |       ritual_dagger.png
|       |   |       rusted_shortsword.png
|       |   |       shadow_essence.png
|       |   |       shield.PNG
|       |   |       shield_plus_1.PNG
|       |   |       shortbow.png
|       |   |       shortsword.png
|       |   |       silver_coins.png
|       |   |       small_brass_key.jpg
|       |   |       small_bronze_mirror.jpg
|       |   |       small_bronze_mirror.png
|       |   |       smooth_river_stone_with_runes.png
|       |   |       spectral_fragment.png
|       |   |       spider_leg.png
|       |   |       spider_silk.png
|       |   |       splint_armor.png
|       |   |       star_map_fragment.jpg
|       |   |       stolen_coin_purse.png
|       |   |       stone_fragment.png
|       |   |       strange_relic.png
|       |   |       strong_ale.png
|       |   |       tarnished_silver_locket.jpg
|       |   |       tarnished_silver_locket.png
|       |   |       thieves_tools.png
|       |   |       tinderbox.png
|       |   |       torch.PNG
|       |   |       trail_rations.PNG
|       |   |       twisted_driftwood_wand.jpg
|       |   |       twisted_driftwood_wand.png
|       |   |       twisted_staff.png
|       |   |       venom_gland.png
|       |   |       wooden_dice.jpg
|       |   |       wooden_dice.png
|       |   |       wooden_doll_with_button_eyes.jpg
|       |   |       
|       |   \---ui
|       +---sprites
|       |   +---effects
|       |   |       acid_diag.png
|       |   |       acid_h_v.png
|       |   |       acid_impact.png
|       |   |       arrow_diag.png
|       |   |       arrow_h_v.png
|       |   |       bullet_diag.png
|       |   |       bullet_h_v.png
|       |   |       burning_hands_diag.png
|       |   |       burning_hands_h_v.png
|       |   |       fireball_burn.png
|       |   |       firebolt_diag.png
|       |   |       firebolt_h_v.png
|       |   |       firebolt_impact.png
|       |   |       force_diag.png
|       |   |       force_h_v.png
|       |   |       force_impact.png
|       |   |       ice_diag.png
|       |   |       ice_h_v.png
|       |   |       ice_impact.png
|       |   |       lightning_bolt_diag.png
|       |   |       lightning_bolt_h_v.png
|       |   |       necrotic_diag.png
|       |   |       necrotic_h_v.png
|       |   |       
|       |   +---enemies
|       |   +---fire
|       |   |       campfire_animation.png
|       |   |       torch_animation.png
|       |   |       
|       |   +---items
|       |   |       barrel.png
|       |   |       pillar.png
|       |   |       support_beam.png
|       |   |       
|       |   +---landscape
|       |   |       star_twinkle_1.png
|       |   |       
|       |   +---player
|       |   \---walls
|       |           cellar_corner_ne.png
|       |           cellar_corner_nw.png
|       |           cellar_corner_se.png
|       |           cellar_corner_sw.png
|       |           cellar_wall_east.png
|       |           cellar_wall_north.png
|       |           cellar_wall_south.png
|       |           cellar_wall_west.png
|       |           
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
|   |   spells.json
|   |   __init__.py
|   |   
|   +---combat
|   |   +---battlefields
|   |   |       crypt_chamber.json
|   |   |       hill_ruins_exterior.json
|   |   |       mine_collapsed_area.json
|   |   |       mine_tunnel.json
|   |   |       redstone_town_alley - gaunlet.json
|   |   |       redstone_town_alley.json
|   |   |       refugee_camp_night.json
|   |   |       small_cellar.json
|   |   |       swamp_exterior.json
|   |   |       
|   |   +---encounters
|   |   |       alley_fight.json
|   |   |       alley_fight3.json
|   |   |       alley_fight_2.json
|   |   |       hill_ruins_bandits.json
|   |   |       hill_ruins_statue.json
|   |   |       mine_kobold_scouts.json
|   |   |       mine_kobold_warriors.json
|   |   |       mine_spider_ambush.json
|   |   |       refugee_camp_brigand_raid copy.json
|   |   |       refugee_camp_brigand_raid.json
|   |   |       swamp_church_cultists.json
|   |   |       swamp_ghost.json
|   |   |       swamp_skeleton.json
|   |   |       tavern_basement_rats.json
|   |   |       
|   |   \---enemies
|   |           animated_statue.json
|   |           baby_spider.json
|   |           bandit_common.json
|   |           bandit_leader.json
|   |           blight_shadow.json
|   |           cultist.json
|   |           cult_leader.json
|   |           cult_priest_swamp.json
|   |           giant_rat.json
|   |           giant_spider.json
|   |           goblin.json
|   |           kobold.json
|   |           kobold_scout.json
|   |           kobold_shaman.json
|   |           kobold_warrior.json
|   |           ogre_archer.json
|   |           shadow_ghost.json
|   |           skeleton.json
|   |           thief_common.json
|   |           
|   +---dialogues
|   |       broken_blade_garrick.json
|   |       broken_blade_meredith.json
|   |       hill_ruins_carved_stones.json
|   |       hill_ruins_forcedoor.json
|   |       hill_ruins_lockeddoor.json
|   |       hill_ruins_marcus.json
|   |       hill_ruins_mechanisms.json
|   |       hill_ruins_mine.json
|   |       hill_ruins_portal.json
|   |       hill_ruins_rubble.json
|   |       hill_ruins_unlockdoor.json
|   |       mine_aethel_ore.json
|   |       mine_carts.json
|   |       mine_collapse.json
|   |       mine_deep_ore.json
|   |       mine_equipment.json
|   |       mine_henrik_seal.json
|   |       mine_kobold_supplies.json
|   |       mine_ore_deposits.json
|   |       mine_ritual_chamber.json
|   |       mine_rubble.json
|   |       mine_secret_tunnel.json
|   |       mine_unstable_tunnels.json
|   |       mine_warning_signs.json
|   |       patron_selection_elara.json
|   |       patron_selection_gareth.json
|   |       patron_selection_lyra.json
|   |       patron_selection_mayor.json
|   |       patron_selection_pete.json
|   |       patron_selection_thorman.json
|   |       redstone_town_beggar.json
|   |       redstone_town_bernard.json
|   |       redstone_town_casperandmeredith.json
|   |       redstone_town_cassia.json
|   |       redstone_town_henrik.json
|   |       redstone_town_jenna.json
|   |       redstone_town_mayor.json
|   |       refugee_camp_campfire.json
|   |       refugee_camp_leader_rest.json
|   |       refugee_camp_marta.json
|   |       refugee_camp_refugees.json
|   |       refugee_camp_supplies.json
|   |       swamp_church_altar.json
|   |       swamp_church_graves.json
|   |       swamp_church_pews.json
|   |       swamp_church_ritual.json
|   |       swamp_church_symbols.json
|   |       
|   +---locations
|   |       broken_blade.json
|   |       exploration_hub.json
|   |       hill_ruins.json
|   |       patron_selection.json
|   |       red_hollow_mine.json
|   |       refugee_camp.json
|   |       swamp_church.json
|   |       __init__.py
|   |       
|   +---maps
|   |   |   hill_ruins_entrance_map.py
|   |   |   hill_ruins_ground_level_map.py
|   |   |   redstone_region.py
|   |   |   redstone_town_map.py
|   |   |   red_hollow_mine_level_1_map.py
|   |   |   red_hollow_mine_level_2b_map.py
|   |   |   red_hollow_mine_level_2_map.py
|   |   |   red_hollow_mine_level_3_map.py
|   |   |   red_hollow_mine_pre_entrance_map.py
|   |   |   refugee_camp_main_map.py
|   |   |   swamp_church_exterior_map.py
|   |   |   swamp_church_interior_map.py
|   |   |   
|   |           
|   +---narrative
|   |       act_two.json
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
|       acti-II-mayor-and-discovery-system-implementation-plan.md
|       Act_II_Exploration_System_Implementation_Plan.md
|       adding_npc_dialogue.md
|       decisions.md
|       Dialogue_issues_-_what_to_review_-Nov_5.md
|       Flag-analysis-and-path-forward.md
|       Hill_Ruins_Implementation_Plan.md
|       Phase_11.5_Location_Navigation_Conversion_Plan_v2.md
|       project_context copy.md
|       project_context.md
|       Refugee_Camp_and_Red_Hollow_Mine_Implementation_Plan.md
|       Repository_Structure.md
|       
+---game_logic
|   |   character_engine.py
|   |   combat_ai.py
|   |   combat_engine.py
|   |   commerce_engine.py
|   |   data_manager.py
|   |   dialogue_engine.py
|   |   dice_game_engine.py
|   |   event_manager.py
|   |   inventory_engine.py
|   |   item_manager.py
|   |   movement_system.py
|   |   npc_data_loader.py
|   |   player_managers.py
|   |   quest_engine.py
|   |   save_manager.py
|   |   spell_handlers.py
|   |   
|           
+---saves
|       autosave.json
|       quicksave.json
|       save_slot_1.json
|       save_slot_2.json
|       save_slot_3.json
|       save_slot_4 copy.json
|       save_slot_4.json
|       save_slot_5.json
|       
+---screens
|   |   act_two_transition.py
|   |   character_creation.py
|   |   character_overlay.py
|   |   combat_loot_overlay.py
|   |   exploration_hub.py
|   |   gambling_dice.py
|   |   help_overlay.py
|   |   hill_ruins_entrance_nav.py
|   |   hill_ruins_ground_level_nav.py
|   |   intro_scenes.py
|   |   inventory_overlay.py
|   |   load_game.py
|   |   quest_overlay.py
|   |   redstone_town.py
|   |   red_hollow_mine_level_1_nav.py
|   |   red_hollow_mine_level_2b_nav.py
|   |   red_hollow_mine_level_2_nav.py
|   |   red_hollow_mine_level_3_nav.py
|   |   red_hollow_mine_pre_entrance_nav.py
|   |   refugee_camp_main_nav.py
|   |   save_game.py
|   |   statistics_overlay.py
|   |   swamp_church_exterior_nav.py
|   |   swamp_church_interior_nav.py
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
|   |   spell_animation_renderer.py
|   |   __init__.py
|   |   
|           
+---utils
|   |   animation.py
|   |   buff_manager.py
|   |   combat_effects.py
|   |   combat_loader.py
|   |   combat_sprite_manager.py
|   |   constants.py
|   |   debug_manager.py
|   |   dialogue_ui_utils.py
|   |   dice_roller.py
|   |   graphics.py
|   |   location_loader.py
|   |   narrative_schema.py
|   |   npc_display.py
|   |   object_display.py
|   |   overlay_utils.py
|   |   party_display.py
|   |   quest_system.py
|   |   stats_calculator.py
|   |   tabbed_overlay_utils.py
|   |   tile_graphics.py
|   |   world_npc_spawner.py
|   |   xp_manager.py
|   |   __init__.py
|   |   
|           
        
```
