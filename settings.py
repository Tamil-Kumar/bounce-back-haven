'''
Haven Hackathon
Theme: Bounce Back

Date: 11/15/2026
Author: Tamil Kumar, Srihaas Yeluri

This module handles all of the constant variables, colors, and settings for the game.
'''

import os

# Defines all the game/screen variables and the files

WIDTH, HEIGHT = 960, 640
FPS = 60
TITLE = "After Shock"
FONT_NAME = "trebuchetms,verdana,arial"
BEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best.txt")
CHARACTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "character.png")
MUSIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "background.mp3")
LEVEL_UP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "level_up.mp3")
SHOOT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "shoot.mp3")
HIT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio", "hit.mp3")

BG = (15, 15, 20)
HOT_ZONE_FILL = (55, 15, 15)
PLAYER_COLOR = (232, 107, 5)
SHIELD_COLOR = (255, 255, 255)
ENEMY_COLOR = (255, 30, 30)
BOUNCE_COLOR = (255, 150, 0)
SLOW_COLOR = (90, 90, 255)
LASER_COLOR = (0, 255, 70)
HOT_COLOR = (255, 0, 0)
TEXT = (255, 255, 255)
DIM = (160, 160, 170)
CARD = (40, 40, 50)
CARD_HOVER = (60, 60, 75)

HOT_ZONE = 70
HEAT_TIME = 2.0
COOL_TIME = 1.5

PLAYER_RADIUS = 18
PLAYER_SPEED = 270
PLAYER_SPEED_STEP = 1.15
PLAYER_MAX_RAMP = 2.5
BASE_LIVES = 3
HIT_INVULN = 1.5

SHIELD_RADIUS = 32
SHIELD_WIDTH = 6
SHIELD_SIZES = [0.25, 0.30, 0.35, 0.45, 0.50]

ENEMY_RADIUS = 11
ENEMY_BASE_SPEED = 170
TURN_RATE = 4.0
MAX_ENEMIES = 10
SPAWN_INTERVAL = 3.0
SPEED_STEP = 1.3
WARMUP = 0.7

LASER_INTERVAL = 5.0
LASER_SPEED = 900
LASER_LENGTH = 24

SLOW_COOLDOWN = 12.0
SHOCKWAVE_INTERVAL = 8.0
POINTS = 10
UPGRADE_POINTS = 100