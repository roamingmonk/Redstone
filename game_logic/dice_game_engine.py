# game_logic/dice_game_engine.py
"""
Dice Game Engine - Pure Single Data Authority Pattern
GameState = THE authoritative data source
DiceGameEngine = Pure business logic processor
"""

import random
import pygame
from typing import Dict, List, Tuple, Optional, Any

class DiceGameEngine:
    """
    Centralized dice game management following Single Data Authority pattern
    
    This engine handles ALL dice game business logic:
    - Dice rolling mechanics and combinations
    - Payout calculations and house money management
    - Gambling statistics tracking
    - Game state validation and rules enforcement
    
    GameState remains THE single source of truth for all data.
    """
    
    def __init__(self, game_state_ref):
        self.game_state = game_state_ref
        self.event_manager = None
        print("🎲 DiceGameEngine initialized with Single Data Authority pattern")
        
        # Initialize gambling stats in character data if not present
        self._ensure_gambling_stats_initialized()
    
    def set_event_manager(self, event_manager):
        """Set event manager reference and register dice game events"""
        self.event_manager = event_manager
        self.register_dice_events()
    
    def register_dice_events(self):
        """Register dice game event handlers"""
        if self.event_manager:
            self.event_manager.register("DICE_BET_PLACED", self._handle_dice_bet_placed)
            self.event_manager.register("DICE_SKIP_ANIMATION", self._handle_dice_skip_animation)
            print("🎲 DiceGameEngine registered for dice game events")
    
    def _ensure_gambling_stats_initialized(self):
        """Initialize gambling statistics in character data if not present"""
        if 'gambling_stats' not in self.game_state.character:
            self.game_state.character['gambling_stats'] = {
                'house_money': random.randint(400, 700),
                'game_active': True,
                'win_streak': 0,
                'loss_streak': 0,
                'total_winnings': 0,
                'total_losses': 0,
                'games_played': 0,
                'last_roll': [],
                'current_bet': 0,
                'last_result': {}
            }
            print("🎲 Initialized gambling statistics in character data")
    
    # ==========================================
    # EVENT HANDLERS
    # ==========================================
    
    def _handle_dice_bet_placed(self, event_data):
        """Handle when player places a bet on dice game"""
        bet_amount = event_data.get('bet_amount', 5)
        
        # Validate bet can be afforded
        if not self.can_afford_bet(bet_amount):
            print(f"⚠️ Player can't afford bet of {bet_amount} gold")
            return
        
        # Store the bet amount
        self.game_state.character['gambling_stats']['current_bet'] = bet_amount
        
        # Roll the dice
        dice_result = self.roll_redstone_dice()
        
        # Calculate payout
        payout, combination, description, game_continues = self.calculate_dice_payout(bet_amount, dice_result)
        
        # Store results for display
        self.game_state.character['gambling_stats']['last_result'] = {
            'combination': combination,
            'payout': payout,
            'description': description,
            'game_continues': game_continues
        }
        
        # Update statistics
        self._update_gambling_statistics(bet_amount, payout)
        
        print(f"🎲 Dice bet placed: {bet_amount}gp, result: {combination}, payout: {payout}")
        
        # Transition to rolling screen
        if self.event_manager:
            self.event_manager.emit("SCREEN_CHANGE", {
                "target_screen": "dice_rolling",
                "source_screen": "dice_bets"
            })
    
    def _handle_dice_skip_animation(self, event_data):
        """Handle skipping dice rolling animation"""
        self.game_state.character['gambling_stats']['animation_skipped'] = True
        print("🎲 Dice animation skipped")
    
    # ==========================================
    # DICE GAME BUSINESS LOGIC
    # ==========================================
    
    def roll_redstone_dice(self):
        """Roll 3 dice for Redstone Dice game"""
        dice = [random.randint(1, 6) for _ in range(3)]
        gambling_stats = self.game_state.character['gambling_stats']
        gambling_stats['last_roll'] = dice
        gambling_stats['rolling'] = True
        gambling_stats['roll_start_time'] = pygame.time.get_ticks()
        gambling_stats['animation_skipped'] = False  # Reset animation skip flag
        return dice
    
    def analyze_dice_result(self, dice):
        """
        Analyze dice roll and return combination type and multiplier
        
        Args:
            dice: list of 3 dice values
            
        Returns:
            tuple: (combination_name, multiplier, description)
        """
        dice_sorted = sorted(dice)
        dice_total = sum(dice)
        
        # Check for triple 6s (special case - shuts down casino)
        if dice == [6, 6, 6]:
            return ("Triple Sixes", 20, "INCREDIBLE! Triple sixes! The casino shuts down!")
        
        # Check for any triple
        if dice_sorted[0] == dice_sorted[1] == dice_sorted[2]:
            return ("Triple", 8, f"Amazing! Triple {dice_sorted[0]}s!")
        
        # Check for straights (no wraparound)
        straights = [(1,2,3), (2,3,4), (3,4,5), (4,5,6)]
        if tuple(dice_sorted) in straights:
            return ("Straight", 4, f"Excellent! Straight {dice_sorted[0]}-{dice_sorted[1]}-{dice_sorted[2]}!")
        
        # Check for any pair
        if dice_sorted[0] == dice_sorted[1] or dice_sorted[1] == dice_sorted[2]:
            # We have a pair
            if dice_sorted[0] == dice_sorted[1]:
                pair_value = dice_sorted[0]
            else:
                pair_value = dice_sorted[1]
            
            return ("Pair", 1.5, f"Good! Pair of {pair_value}s!")
        
        # Check for total 15+
        if dice_total >= 15:
            return ("High Total", 1.5, f"Nice roll! Total of {dice_total}!")
        
        # House wins
        return ("House Wins", 0, f"Total {dice_total} - House takes your bet!")
    
    def calculate_dice_payout(self, bet_amount, dice):
        """
        Calculate payout for dice roll, considering house money limitations
        
        Args:
            bet_amount: amount player bet
            dice: list of 3 dice values
            
        Returns:
            tuple: (payout_amount, combination_name, description, game_continues)
        """
        combination, multiplier, description = self.analyze_dice_result(dice)
        gambling_stats = self.game_state.character['gambling_stats']
        
        if multiplier == 0:
            # House wins - player loses bet
            self.game_state.character['gold'] -= bet_amount
            gambling_stats['house_money'] += bet_amount
            gambling_stats['loss_streak'] += 1
            gambling_stats['win_streak'] = 0
            return 0, combination, description, True
        
        # Player wins - calculate payout
        gross_winnings = int(bet_amount * multiplier)
        net_winnings = gross_winnings - bet_amount  # Subtract original bet
        
        # Check house money limitation
        if net_winnings > gambling_stats['house_money']:
            net_winnings = gambling_stats['house_money']
            description += f" (House limited payout to {net_winnings} gold!)"
        
        # Apply winnings
        self.game_state.character['gold'] += net_winnings
        gambling_stats['house_money'] -= net_winnings
        gambling_stats['win_streak'] += 1
        gambling_stats['loss_streak'] = 0
        
        # Check for game-ending conditions
        game_continues = True
        if combination == "Triple Sixes":
            gambling_stats['game_active'] = False
            game_continues = False
            description += " The casino closes in awe!"
        elif gambling_stats['house_money'] <= 0:
            gambling_stats['game_active'] = False
            game_continues = False
            description += " You've broken the house!"
        
        return net_winnings, combination, description, game_continues
    
    def get_dice_flavor_text(self, won, combination):
        """Get random flavor text for dice results"""
        if not won:
            messages = [
                "The dice gods frown upon you!",
                "Better luck next time, adventurer!",
                "Fortune is a fickle mistress!",
                "The house always has an edge!",
                "Roll again when courage returns!"
            ]
        elif combination == "Triple Sixes":
            messages = [
                "LEGENDARY! The stuff of tavern songs!",
                "By the gods! What a roll!",
                "Even old-timers are speechless!",
                "This will be remembered for ages!"
            ]
        elif combination == "Triple":
            messages = [
                "Masterful! A roll for the ages!",
                "Incredible! Lightning in a bottle!",
                "Even veterans are impressed!"
            ]
        elif combination == "Straight":
            messages = [
                "Skillful! A perfect sequence!",
                "Impressive! The dice align in your favor!",
                "Excellent technique, adventurer!",
                "The gods smile upon your fortune!"
            ]
        else:
            messages = [
                "Lady Luck graces you this day!",
                "A fine roll, worthy adventurer!",
                "Your courage pays off!",
                "Fortune favors the brave!"
            ]
        
        return random.choice(messages)
    
    def can_afford_bet(self, bet_amount):
        """Check if player can afford a bet"""
        return self.game_state.character.get('gold', 0) >= bet_amount
    
    def reset_dice_game(self):
        """Reset dice game for new session"""
        gambling_stats = self.game_state.character['gambling_stats']
        gambling_stats['house_money'] = random.randint(400, 700)
        gambling_stats['game_active'] = True
        gambling_stats['win_streak'] = 0
        gambling_stats['loss_streak'] = 0
    
    def _update_gambling_statistics(self, bet_amount, payout):
        """Update gambling statistics in character data"""
        gambling_stats = self.game_state.character['gambling_stats']
        gambling_stats['games_played'] += 1
        
        # Track player statistics
        self.game_state.player_statistics['dice_games_played'] += 1
        winnings = payout if payout > 0 else -bet_amount
        self.game_state.player_statistics['dice_total_winnings'] += winnings
        
        if payout > 0:
            gambling_stats['total_winnings'] += payout
            
             # Update longest win streak
            current_win_streak = gambling_stats.get('win_streak', 0)
            if current_win_streak > self.game_state.player_statistics['longest_win_streak']:
                self.game_state.player_statistics['longest_win_streak'] = current_win_streak
            
            # Track highest gold won in a single game 
            
            if payout > self.game_state.player_statistics['highest_winning_roll']:
                self.game_state.player_statistics['highest_winning_roll'] = payout

            # Update longest win streak if current streak is higher
            current_win_streak = gambling_stats.get('win_streak', 0)
            if current_win_streak > self.game_state.player_statistics['longest_win_streak']:
                self.game_state.player_statistics['longest_win_streak'] = current_win_streak
        else:
            gambling_stats['total_losses'] += bet_amount
            
            # Update longest losing streak if current streak is higher
            current_loss_streak = gambling_stats.get('loss_streak', 0)
            if current_loss_streak > self.game_state.player_statistics['longest_losing_streak']:
                self.game_state.player_statistics['longest_losing_streak'] = current_loss_streak
    
    # ==========================================
    # LEGACY COMPATIBILITY METHODS
    # ==========================================
    
    def get_dice_game_state(self):
        """Get current dice game state (for backward compatibility)"""
        return self.game_state.character.get('gambling_stats', {})

# ==========================================
# GLOBAL DICE GAME ENGINE MANAGEMENT
# ==========================================

# Global dice game engine instance (initialized by DataManager)
dice_game_engine = None

def get_dice_game_engine():
    """Get the global dice game engine instance"""
    return dice_game_engine

def initialize_dice_game_engine(game_state_ref, event_manager=None):
    """Initialize the global dice game engine with event management"""
    global dice_game_engine
    dice_game_engine = DiceGameEngine(game_state_ref)
    
    # Register for dice events if event manager provided
    if event_manager:
        dice_game_engine.set_event_manager(event_manager)
    else:
        print("⚠️ No EventManager provided to DiceGameEngine")
    
    print("🎲 Initialized DiceGameEngine")
    return dice_game_engine

# Development and testing utilities
if __name__ == "__main__":
    print("🧪 DiceGameEngine Development Test")
    print("=" * 50)
    
    print("DiceGameEngine follows Single Data Authority pattern:")
    print("- GameState = THE authoritative data source")
    print("- DiceGameEngine = Pure business logic processor")
    print("- No data storage in engine itself")
    print("- All operations modify GameState.character['gambling_stats']")
    print("- Supports complete dice game with statistics tracking")
    
    print("\n✅ DiceGameEngine module loaded successfully!")