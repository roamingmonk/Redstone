NPC Updates

Updated Steps to Add NPC Dialogue (One Line Each):

Add NPC entry to data/narrative_schema.json with system_id, location, dialogue_file, and story_flags
Add NPC to merchants.json with merchant_id, location, stock configuration (if merchant)
Create dialogue JSON file following {location}_{npc}.json naming pattern with post_shopping states
Add building entry to BUILDING_ENTRANCES in town map with interaction_type and npc_id
Ensure screen naming consistency: location screen must match location_id from narrative schema
Add portrait image as {npc_id}_portrait.jpg in npc_portraits folder (optional)