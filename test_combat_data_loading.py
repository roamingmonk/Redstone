# Test script to verify your superior JSON architecture
# Add this to main.py temporarily or run as separate test

def test_combat_data_loading():
    """Test that your enhanced combat JSON files load correctly"""
    print("🧪 Testing Enhanced Combat Data Loading...")
    
    from utils.combat_loader import get_combat_loader
    
    loader = get_combat_loader()
    
    # Test enemy loading
    print("\n--- Testing Enemy Loading ---")
    giant_rat = loader.load_enemy("giant_rat")
    if giant_rat:
        print(f"✅ Enemy loaded: {giant_rat['name']}")
        print(f"   HP: {giant_rat['stats']['hp']}/{giant_rat['stats']['max_hp']}")
        print(f"   AC: {giant_rat['stats']['ac']}")
        print(f"   STR: {giant_rat['stats']['strength']}, DEX: {giant_rat['stats']['dexterity']}")
        print(f"   Attacks: {len(giant_rat['attacks'])}")
        print(f"   Movement Speed: {giant_rat['movement']['speed']}")
        print(f"   XP Value: {giant_rat['loot']['xp_value']}")
    else:
        print("❌ Failed to load Giant Rat")
    
    # Test encounter loading
    print("\n--- Testing Encounter Loading ---")
    basement = loader.load_encounter("tavern_basement_rats")
    if basement:
        print(f"✅ Basement encounter loaded: {basement['name']}")
        print(f"   Battlefield: {basement['battlefield_id']}")
        print(f"   Enemies: {len(basement['enemies'])}")
        print(f"   Player positions: {len(basement['player_party']['starting_positions'])}")
        print(f"   Victory condition: {basement['victory_conditions']['victory_type']}")
        print(f"   Rewards: {basement['rewards']['xp']} XP, {basement['rewards']['gold']} gold")
    else:
        print("❌ Failed to load Basement encounter")
    
    # Test battlefield loading
    print("\n--- Testing Battlefield Loading ---")
    cellar = loader.load_battlefield("small_cellar")
    if cellar:
        print(f"✅ Cellar battlefield loaded: {cellar['name']}")
        print(f"   Size: {cellar['dimensions']['width']}x{cellar['dimensions']['height']}")
        print(f"   Walls: {len(cellar['terrain']['walls'])} segments")
        print(f"   Obstacles: {len(cellar['terrain']['obstacles'])}")
        print(f"   Player spawn points: {len(cellar['spawn_zones']['player_start'])}")
        print(f"   Enemy spawn points: {len(cellar['spawn_zones']['enemy_spawns'])}")
    else:
        print("❌ Failed to load Cellar battlefield")
    
    # Test complete combat instance creation
    print("\n--- Testing Combat Instance Creation ---")
    combat_instance = loader.create_combat_instance("tavern_basement_rats")
    if combat_instance:
        print(f"✅ Combat instance created successfully!")
        print(f"   Encounter: {combat_instance['encounter']['name']}")
        print(f"   Battlefield: {combat_instance['battlefield']['name']}")
        print(f"   Enemy instances: {len(combat_instance['enemy_instances'])}")
        
        # Show enemy instance details
        for i, enemy in enumerate(combat_instance['enemy_instances']):
            print(f"   Enemy {i+1}: {enemy['name']} at {enemy['position']}")
            print(f"             ID: {enemy['instance_id']}, HP: {enemy['current_hp']}")
            print(f"             Facing: {enemy['facing']}, AI: {enemy['ai_behavior']}")
    else:
        print("❌ Failed to create combat instance")
    
    # Test listing available content
    print("\n--- Available Content ---")
    enemies = loader.get_available_enemies()
    encounters = loader.get_available_encounters()  
    battlefields = loader.get_available_battlefields()
    print(f"Available enemies: {enemies}")
    print(f"Available encounters: {encounters}")
    print(f"Available battlefields: {battlefields}")
    
    print("\n🎯 Enhanced combat data loading test complete!")

# Call this function to test your JSON architecture
if __name__ == "__main__":
    test_combat_data_loading()