"""
Dice rolling utility for Terror in Redstone
Supports standard RPG dice notation: XdY+Z
"""

import random
import re


def roll_dice(dice_string):
    """
    Roll dice from standard notation and return total + details
    
    Args:
        dice_string: Dice notation (e.g., "2d4+2", "1d8", "3d6-1")
        
    Returns:
        tuple: (total, individual_rolls, modifier)
        
    Examples:
        >>> roll_dice("2d4+2")
        (8, [3, 2], 2)  # Rolled 3 and 2, plus 2 modifier = 8 total
    """
    try:
        # Parse dice notation using regex
        # Matches: "2d4+2", "1d8", "3d6-1", etc.
        pattern = r'(\d+)d(\d+)([\+\-]\d+)?'
        match = re.match(pattern, dice_string.strip())
        
        if not match:
            print(f"⚠️ Invalid dice notation: {dice_string}")
            return (0, [], 0)
        
        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        modifier_str = match.group(3) if match.group(3) else "+0"
        modifier = int(modifier_str)
        
        # Roll the dice
        individual_rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        dice_total = sum(individual_rolls)
        final_total = dice_total + modifier
        
        return (final_total, individual_rolls, modifier)
        
    except Exception as e:
        print(f"❌ Error rolling dice '{dice_string}': {e}")
        return (0, [], 0)


def format_roll_result(dice_string, total, rolls, modifier):
    """
    Format dice roll result for console output
    
    Args:
        dice_string: Original dice notation
        total: Final total
        rolls: List of individual die rolls
        modifier: Modifier applied
        
    Returns:
        str: Formatted string for logging
    """
    rolls_str = " + ".join(map(str, rolls))
    
    if modifier > 0:
        return f"{dice_string} = [{rolls_str}] + {modifier} = {total}"
    elif modifier < 0:
        return f"{dice_string} = [{rolls_str}] - {abs(modifier)} = {total}"
    else:
        return f"{dice_string} = [{rolls_str}] = {total}"