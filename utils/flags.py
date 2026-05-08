"""
utils/flags.py — Terror in Redstone flag name constants.

All narrative and engine flags that are referenced by name in Python code
are declared here as class constants.  Use FLAGS.<CONSTANT> instead of a
raw string so that typos are caught at import time (AttributeError) rather
than failing silently at runtime.

JSON files (dialogue JSON, narrative_schema.json) continue to use raw strings
because those are validated at startup by utils/narrative_schema.validate_flags().
This module covers only the Python-side references.

Usage:
    from utils.flags import FLAGS
    setattr(game_state, FLAGS.QUEST_ACTIVE, True)
    if getattr(game_state, FLAGS.GARETH_RECRUITED, False): ...
"""


class FLAGS:
    # ── Act / story progression ───────────────────────────────────────────────
    ACT_ONE_COMPLETE                     = "act_one_complete"
    ACT_TWO_STARTED                      = "act_two_started"
    ACT_TWO_COMPLETE                     = "act_two_complete"
    ACT_THREE_STARTED                    = "act_three_started"
    ACT_THREE_READY                      = "act_three_ready"
    ACT_THREE_COMPLETE                   = "act_three_complete"
    RETURNED_TO_REDSTONE_VICTORIOUS      = "returned_to_redstone_victorious"
    MAIN_QUEST_COMPLETED                 = "main_quest_completed"
    QUEST_ACTIVE                         = "quest_active"

    # ── NPC conversations ─────────────────────────────────────────────────────
    MAYOR_TALKED                         = "mayor_talked"
    MEREDITH_TALKED                      = "meredith_talked"
    GARRICK_TALKED                       = "garrick_talked"
    REFUGEE_LEADER_TALKED                = "refugee_leader_talked"

    # ── Party recruitment ─────────────────────────────────────────────────────
    FIRST_PARTY_MEMBER_RECRUITED         = "first_party_member_recruited"
    GARETH_RECRUITED                     = "gareth_recruited"
    ELARA_RECRUITED                      = "elara_recruited"
    THORMAN_RECRUITED                    = "thorman_recruited"
    LYRA_RECRUITED                       = "lyra_recruited"

    # ── Location discoveries ──────────────────────────────────────────────────
    LEARNED_ABOUT_SWAMP_CHURCH           = "learned_about_swamp_church"
    LEARNED_ABOUT_RUINS                  = "learned_about_ruins"
    LEARNED_ABOUT_REFUGEES               = "learned_about_refugees"

    # ── Location completion ───────────────────────────────────────────────────
    SWAMP_CHURCH_COMPLETE                = "swamp_church_complete"
    HILL_RUINS_COMPLETE                  = "hill_ruins_complete"
    REFUGEE_CAMP_COMPLETE                = "refugee_camp_complete"
    RED_HOLLOW_MINE_COMPLETE             = "red_hollow_mine_complete"

    # ── Hill Ruins completion requirements ────────────────────────────────────
    HILL_RUINS_CARVED_SEARCHED           = "hill_ruins_carved_searched"
    HILL_RUINS_PORTAL_EXAMINED           = "hill_ruins_portal_examined"
    HILL_RUINS_MECHANISMS_SEARCHED       = "hill_ruins_mechanisms_searched"
    HILL_RUINS_LOCKED_DOOR_FOUND         = "hill_ruins_locked_door_found"

    # ── Refugee camp ──────────────────────────────────────────────────────────
    AGREED_TO_DEFEND_CAMP                = "agreed_to_defend_camp"
    REFUGEE_CAMP_DEFENDED                = "refugee_camp_defended"
    REFUGEE_COMBAT_REWARDED              = "refugee_combat_rewarded"
    REFUGEE_CAMP_MAIN_EXPLORED           = "refugee_camp_main_explored"
    REFUGEE_CAMP_BRIGANDS_DEFEATED       = "refugee_camp_brigands_defeated"
    REFUGEE_CAMP_DETAILS_KNOWN           = "refugee_camp_details_known"
    READY_FOR_NIGHT_DEFENSE              = "ready_for_night_defense"

    # ── Intelligence / detailed location info ─────────────────────────────────
    SWAMP_CHURCH_DETAILS_KNOWN           = "swamp_church_details_known"
    HILL_RUINS_DETAILS_KNOWN             = "hill_ruins_details_known"
    REFUGEE_DETAILED_INTEL               = "refugee_detailed_intel"

    # ── Swamp Church story flags ──────────────────────────────────────────────
    FOUND_CULT_DOCUMENTS                 = "found_cult_documents"
    READ_CULT_DOCUMENTS                  = "read_cult_documents"
    LEARNED_SACRIFICE_PLAN               = "learned_sacrifice_plan"

    # ── Red Hollow Mine ───────────────────────────────────────────────────────
    INVESTIGATED_OLD_SHAFT               = "investigated_old_shaft"
    RED_HOLLOW_ORE_FOUND                 = "red_hollow_ore_found"
    RETURNED_ORE_TO_HENRIK               = "returned_ore_to_henrik"
    REPORTED_SHAFT_TO_HENRIK             = "reported_shaft_to_henrik"

    # ── Mayor acknowledgements ────────────────────────────────────────────────
    MAYOR_ACKNOWLEDGED_SWAMP_COMPLETE    = "mayor_acknowledged_swamp_complete"
    MAYOR_ACKNOWLEDGED_RUINS_COMPLETE    = "mayor_acknowledged_ruins_complete"
    MAYOR_ACKNOWLEDGED_REFUGEE_COMPLETE  = "mayor_acknowledged_refugee_complete"
    MAYOR_ACKNOWLEDGED_MINE_COMPLETE     = "mayor_acknowledged_mine_complete"

    # ── Marcus / Cassia post-battle ───────────────────────────────────────────
    MARCUS_REDEEMED                      = "marcus_redeemed"
    MAYOR_POST_VICTORY_COMPLETE          = "mayor_post_victory_complete"
    CASSIA_POST_VICTORY_COMPLETE         = "cassia_post_victory_complete"
    HENRIK_POST_VICTORY_COMPLETE         = "henrik_post_victory_complete"

    # ── Victory celebration ───────────────────────────────────────────────────
    TRIGGER_VICTORY_CELEBRATION          = "trigger_victory_celebration"
    VICTORY_CELEBRATION_STARTED          = "victory_celebration_started"
    VICTORY_CELEBRATION_COMPLETE         = "victory_celebration_complete"

    # ── Boss / combat ─────────────────────────────────────────────────────────
    BOSS_DEFEATED                        = "boss_defeated"
    PORTAL_SEALED                        = "portal_sealed"
    IN_COMBAT                            = "in_combat"

    # ── UI state flags ────────────────────────────────────────────────────────
    CONTROLS_HINT_DISMISSED              = "controls_hint_dismissed"
    INVENTORY_OPEN                       = "inventory_open"
    QUEST_LOG_OPEN                       = "quest_log_open"
    CHARACTER_SHEET_OPEN                 = "character_sheet_open"
    HELP_SCREEN_OPEN                     = "help_screen_open"
    LOAD_SCREEN_OPEN                     = "load_screen_open"
    STATS_ROLLED                         = "stats_rolled"
    CUSTOM_NAME_ACTIVE                   = "custom_name_active"
    DEATH_OVERLAY_ACTIVE                 = "death_overlay_active"
    SKIP_DIALOGUE_RETURN                 = "skip_dialogue_return"

    # ── Legacy / misc ─────────────────────────────────────────────────────────
    # Note: explore_* flags below are debug-only; correct canonical names are
    # explored_swamp_church / explored_hill_ruins / explored_refugee_camp.
    EXPLORE_REFUGEE_CAMP                 = "explore_refugee_camp"
    EXPLORE_HILL_RUINS                   = "explore_hill_ruins"
    EXPLORE_SWAMP_CHURCH                 = "explore_swamp_church"
    MAYOR_MENTIONED                      = "mayor_mentioned"
