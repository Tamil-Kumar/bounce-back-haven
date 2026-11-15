'''
Haven Hackathon
Theme: Bounce Back

Date: 11/15/2026
Author: Tamil Kumar, Srihaas Yeluri

This module handles the upgrade system of the game.
'''

import random

from settings import HEAT_TIME, HIT_INVULN, SHIELD_SIZES, SHOCKWAVE_INTERVAL

# Define upgrades and levels

UPGRADES = {
    "life": ("Extra Life", 3),
    "slow": ("Slower Enemies", 5),
    "shield": ("Bigger Shield", 5),
    "laser": ("Lasers", 5),
    "speed": ("Faster Feet", 5),
    "heat": ("Heat Resistance", 5),
    "recovery": ("Recovery", 5),
    "wave": ("Shockwave", 5),
}

# Get wave radius for shockwave based on level

def wave_radius(level):
    return 100 + 30 * level

# Creates descriptions for upgrades

def describe(key, level):
    if key == "shield":
        return "Two shields, 25% each." if level == 5 else f"Shield covers {int(SHIELD_SIZES[level] * 100)}%."
    return {
        "life": "Gain 1 extra life.",
        "slow": f"Press Space to slow enemies by 50% for {level}s.",
        "laser": f"Shoot {level} laser{'s' if level > 1 else ''} every 5s.",
        "speed": f"Move {level * 10}% faster.",
        "heat": f"Take {HEAT_TIME + level:g}s to overheat at the walls.",
        "recovery": f"{HIT_INVULN + level * 0.5:g}s of safety after getting hit.",
        "wave": f"Knock back enemies within {wave_radius(level)}px every {SHOCKWAVE_INTERVAL:g}s.",
    }[key]

# Handles the randomness of the upgrades

def roll(levels):
    available = [key for key, (_, cap) in UPGRADES.items() if levels[key] < cap]
    return random.sample(available, min(3, len(available)))
