import json
import os

class NPCManager:
    """Professional NPC management system for RPG games
    
    Handles loading NPC data from JSON files and managing character information.
    Follows industry-standard separation of data and logic.
    """
    
    def __init__(self):
        self.npcs_data = {}
   
    def load_data(self):
        """
        Standard interface method for DataManager compatibility
        Calls the internal load_npcs method
        """
        print("🔄 NPCManager: Loading NPC data...")
        self.load_npcs()
        print(f"✅ NPCManager: Loaded {len(self.npcs_data)} NPCs")

    def load_npcs(self):
        """Load all NPC definitions from JSON data files"""
        npcs_dir = os.path.join('data', 'npcs')
        
        if not os.path.exists(npcs_dir):
            print("❌ Error: data/npcs/ directory not found!")
            return
        
        # Load all JSON files in the npcs directory
        for filename in os.listdir(npcs_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(npcs_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        npc_data = json.load(f)
                    
                    npc_id = npc_data.get('id')
                    if npc_id:
                        self.npcs_data[npc_id] = npc_data
                        print(f"✅ NPC loaded: {npc_data.get('name', npc_id)}")
                    else:
                        print(f"❌ NPC file {filename} missing 'id' field")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing {filename}: {e}")
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        
        print(f"✅ Loaded {len(self.npcs_data)} NPCs from JSON files")
    
    def get_npc(self, npc_id):
        """Get NPC data by ID"""
        return self.npcs_data.get(npc_id)

    def get_npc_name(self, npc_id):
        """Get NPC display name by ID"""
        npc = self.get_npc(npc_id)
        return npc.get('name', 'Unknown') if npc else 'Unknown'

    def get_npc_description(self, npc_id):
        """Get NPC description by ID"""
        npc = self.get_npc(npc_id)
        return npc.get('description', 'A mysterious figure.') if npc else 'A mysterious figure.'
    
    def get_npc_dialogue(self, npc_id, dialogue_type, game_state=None):
        """Get specific dialogue for an NPC"""
        npc = self.get_npc(npc_id)
        if npc and 'dialogue' in npc:
            return npc['dialogue'].get(dialogue_type, [])
        return []
    
    def can_recruit_npc(self, npc_id, game_state):
        """Check if an NPC can be recruited based on requirements"""
        npc = self.get_npc(npc_id)
        if not npc or not npc.get('recruitment', {}).get('available'):
            return False
        
        # Check requirements
        requirements = npc['recruitment'].get('requirements', [])
        for requirement in requirements:
            if requirement == 'mayor_talked' and not getattr(game_state, 'mayor_talked', False):
                return False
            # Add more requirement checks as needed
        
        # Check if already recruited
        if npc_id in getattr(game_state, 'party_members', []):
            return False
            
        # Check party size
        party_size = len(getattr(game_state, 'party_members', []))
        if party_size >= 3:  # Max 3 recruited (4 total with player)
            return False
        
        return True
    
    def get_recruitment_text(self, npc_id):
        """Get recruitment success text for an NPC"""
        npc = self.get_npc(npc_id)
        if npc and 'recruitment' in npc:
            return npc['recruitment'].get('success_text', 'They join your party!')
        return 'They join your party!'

# Global NPC manager instance
npc_manager = NPCManager()