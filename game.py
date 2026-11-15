'''
Haven Hackathon
Theme: Bounce Back

Date: 11/15/2026
Author: Tamil Kumar, Srihaas Yeluri

This module is the main game file. Handles rendering and functionality.
'''
# Importing stuff

import math
import random

import pygame
import pygame.gfxdraw

import upgrades
from entities import Enemy, Laser, Player
from settings import *
from ui import Ui

# Loads the best score

def load_best():
    try:
        with open(BEST_FILE) as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0

# Saves the best score

def save_best(value):
    try:
        with open(BEST_FILE, "w") as f:
            f.write(str(value))
    except OSError:
        pass

# Loads the sound

def load_sound(path, volume):
    try:
        sound = pygame.mixer.Sound(path)
    except pygame.error:
        return None
    sound.set_volume(volume)
    return sound

# Plays the music

def play_music():
    try:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

# Creates the game display

class Game:

    # Initializes the game display variables
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.ui = Ui()
        self.best = load_best()
        self.level_up_sound = load_sound(LEVEL_UP_FILE, 1)
        self.shoot_sound = load_sound(SHOOT_FILE, 0.5)
        self.hit_sound = load_sound(HIT_FILE, 0.7)
        self.state = "menu"
        self.reset()
        play_music()

    # Resets the game

    def reset(self):
        self.player = Player()
        self.score = self.progress = self.pending = 0
        self.level = 1
        self.levels = dict.fromkeys(upgrades.UPGRADES, 0)
        self.enemies = []
        self.lasers = []
        self.choices = []
        self.spawn_clock = self.laser_clock = 0.0
        self.slow_timer = self.slow_cooldown = 0.0
        self.time_alive = self.over_time = 0.0
        self.speed_mult = 1.0
        self.player_ramp = 1.0
        self.wave_clock = self.wave_flash = 0.0
        self.spawn_enemy()

    # Points needed to get the next level

    def needed(self):
        return 100 + UPGRADE_POINTS * (self.level - 1)

    # Randomizes the location of enemies

    def edge_point(self):
        m = ENEMY_RADIUS + 6
        for _ in range(20):
            x, y = random.uniform(m, WIDTH - m), random.uniform(m, HEIGHT - m)
            if random.random() < 0.5:
                x = random.choice((m, WIDTH - m))
            else:
                y = random.choice((m, HEIGHT - m))
            if self.player.pos.distance_to((x, y)) > 260:
                break
        return x, y

    # Spawns the enemy

    def spawn_enemy(self):
        self.enemies.append(Enemy(self.edge_point()))

    # Adds the score

    def add_score(self, amount):
        self.score += amount
        self.progress += amount
        leveled = False
        while self.progress >= self.needed():
            self.progress -= self.needed()
            self.level += 1
            self.pending += 1
            leveled = True
        if leveled and self.level_up_sound:
            self.level_up_sound.play()

    # Gives the upgrade options

    def open_upgrades(self):
        self.choices = upgrades.roll(self.levels)
        if not self.choices:
            self.pending = 0
        self.state = "upgrade" if self.choices else "play"

    # Applies the upgrades to the player

    def apply_stats(self):
        player = self.player
        player.speed = PLAYER_SPEED * self.player_ramp * (1 + 0.1 * self.levels["speed"])
        player.heat_time = HEAT_TIME + self.levels["heat"]
        player.recovery = HIT_INVULN + 0.5 * self.levels["recovery"]
        player.shield_level = self.levels["shield"]

    # Handles shockwave upgrade functionality

    def shockwave(self):
        radius = upgrades.wave_radius(self.levels["wave"])
        for enemy in self.enemies:
            offset = enemy.pos - self.player.pos
            if enemy.warmup <= 0 and 0 < offset.length() < radius:
                enemy.vel = offset.normalize()
                enemy.bouncing = True
        self.wave_flash = 0.3
        if self.hit_sound:
            self.hit_sound.play()

    # Handles the picking the upgrade function

    def pick(self, index):
        if index >= len(self.choices):
            return
        key = self.choices[index]
        self.levels[key] += 1
        if key == "life":
            self.player.lives += 1
        self.apply_stats()
        self.pending -= 1
        if self.pending > 0:
            self.open_upgrades()
        else:
            self.state = "play"

    # Fires the lasers

    def fire_lasers(self):
        if self.shoot_sound:
            self.shoot_sound.play()
        count = self.levels["laser"]
        for center, size in self.player.shield_arcs():
            spread = size * math.tau * 0.7
            for i in range(count):
                a = center if count == 1 else center - spread / 2 + spread * i / (count - 1)
                d = pygame.Vector2(math.cos(a), math.sin(a))
                self.lasers.append(Laser(self.player.pos + d * (SHIELD_RADIUS + 6), d))

    # Updates the game

    def update(self, dt):
        self.time_alive += dt
        self.player.update(dt, pygame.key.get_pressed(), pygame.mouse.get_pos())
        if self.player.heat >= 1 and self.player.hurt():
            self.player.heat = 0.0
        self.slow_timer = max(0.0, self.slow_timer - dt)
        self.slow_cooldown = max(0.0, self.slow_cooldown - dt)

        self.spawn_clock += dt
        if self.spawn_clock >= SPAWN_INTERVAL:
            self.spawn_clock -= SPAWN_INTERVAL
            if len(self.enemies) < MAX_ENEMIES:
                self.spawn_enemy()
            else:
                self.speed_mult *= SPEED_STEP
                self.player_ramp = min(PLAYER_MAX_RAMP, self.player_ramp * PLAYER_SPEED_STEP)
                self.apply_stats()

        if self.levels["laser"]:
            self.laser_clock += dt
            if self.laser_clock >= LASER_INTERVAL:
                self.laser_clock -= LASER_INTERVAL
                self.fire_lasers()

        self.wave_flash = max(0.0, self.wave_flash - dt)
        if self.levels["wave"]:
            self.wave_clock += dt
            if self.wave_clock >= SHOCKWAVE_INTERVAL:
                self.wave_clock -= SHOCKWAVE_INTERVAL
                self.shockwave()

        speed = ENEMY_BASE_SPEED * self.speed_mult * (0.5 if self.slow_timer > 0 else 1)
        steps = max(1, math.ceil(speed * dt / 6))
        for enemy in self.enemies:
            if enemy.warmup > 0:
                enemy.warmup -= dt
                continue
            for _ in range(steps):
                if self.step_enemy(enemy, speed, dt / steps):
                    break

        for laser in self.lasers:
            laser.update(dt)
            for enemy in self.enemies:
                if enemy.warmup <= 0 and laser.hits(enemy.pos, ENEMY_RADIUS + 2):
                    laser.alive = False
                    self.add_score(POINTS)
                    enemy.reset(self.edge_point())
                    break
        self.lasers = [laser for laser in self.lasers if laser.alive]

        if self.player.lives <= 0:
            self.state = "over"
            if self.score > self.best:
                self.best = self.score
                save_best(self.best)
        elif self.pending > 0:
            self.open_upgrades()

    # Handles the movement of the enemy

    def step_enemy(self, enemy, speed, dt):
        player = self.player
        if enemy.move(player.pos, speed, dt) and enemy.bouncing:
            enemy.bouncing = False
            self.add_score(POINTS)

        offset = enemy.pos - player.pos
        dist = offset.length()
        if dist == 0:
            return False
        normal = offset / dist
        reach = SHIELD_RADIUS + SHIELD_WIDTH / 2 + ENEMY_RADIUS
        angle = math.atan2(offset.y, offset.x)
        if dist < reach and enemy.vel.dot(normal) < 0 and player.on_shield(angle, ENEMY_RADIUS / SHIELD_RADIUS):
            enemy.vel = enemy.vel.reflect(normal)
            enemy.pos = player.pos + normal * (reach + 1)
            enemy.bouncing = True
            if self.hit_sound:
                self.hit_sound.play()
        elif dist < PLAYER_RADIUS + ENEMY_RADIUS and player.hurt():
            enemy.reset(self.edge_point())
            return True
        return False

    # Handles key and mouse input

    def handle(self, event):
        clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        key = event.key if event.type == pygame.KEYDOWN else None

        if self.state == "menu" and (clicked or key in (pygame.K_RETURN, pygame.K_SPACE)):
            self.state = "play"
        elif self.state == "play":
            if key in (pygame.K_ESCAPE, pygame.K_p):
                self.state = "paused"
                if pygame.mixer.get_init():
                    pygame.mixer.music.pause()
            elif key == pygame.K_SPACE and self.levels["slow"] and self.slow_cooldown <= 0:
                self.slow_timer = float(self.levels["slow"])
                self.slow_cooldown = SLOW_COOLDOWN
        elif self.state == "paused" and (clicked or key in (pygame.K_ESCAPE, pygame.K_p)):
            self.state = "play"
            if pygame.mixer.get_init():
                pygame.mixer.music.unpause()
        elif self.state == "upgrade":
            if key in (pygame.K_1, pygame.K_2, pygame.K_3):
                self.pick(key - pygame.K_1)
            elif clicked:
                for i, rect in enumerate(self.ui.card_rects(len(self.choices))):
                    if rect.collidepoint(event.pos):
                        self.pick(i)
                        break
        elif self.state == "over" and self.over_time > 0.6 and (clicked or key in (pygame.K_r, pygame.K_RETURN)):
            self.reset()
            self.state = "play"

    # Draws the screen window

    def draw(self):
        surf = self.screen
        surf.blit(self.ui.background, (0, 0))
        if self.state == "menu":
            lines = [
                "WASD / Arrow keys to move",
                "Mouse to aim your shield",
                "Knock enemies into the walls for points",
                "Don't stay in the red edge zone or you'll overheat",
                "Space uses Slow once you unlock it",
            ]
            if self.best:
                lines.append(f"Best {self.best}")
            self.ui.draw_screen(surf, TITLE, lines, "Click to start", shade=False)
            pygame.display.flip()
            return

        step = 1000 // FPS
        alpha = (pygame.time.get_ticks() % step + self.time_alive * 1000 % step) / step
        for enemy in self.enemies:
            enemy.draw(surf, self.slow_timer > 0, alpha)
        for laser in self.lasers:
            laser.draw(surf)
        self.player.draw(surf, alpha)
        if self.wave_flash > 0:
            radius = round(upgrades.wave_radius(self.levels["wave"]) * (1 - self.wave_flash / 0.3))
            pygame.gfxdraw.aacircle(surf, round(self.player.pos.x), round(self.player.pos.y), radius, SHIELD_COLOR)
        self.ui.draw_hud(surf, self)

        if self.state == "upgrade":
            self.ui.draw_upgrades(surf, self)
        elif self.state == "paused":
            self.ui.draw_screen(surf, "Paused", [], "Esc to resume")
        elif self.state == "over":
            mins, secs = divmod(int(self.time_alive), 60)
            lines = [f"Score {self.score}", f"Best {self.best}", f"Level {self.level}   Time {mins}:{secs:02d}"]
            prompt = "Click or press R to play again" if self.over_time > 0.6 else None
            self.ui.draw_screen(surf, "Game Over", lines, prompt)
        pygame.display.flip()

    # Runs the game

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000, 1 / 30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                self.handle(event)
            if self.state == "play":
                self.update(dt)
            elif self.state == "over":
                self.over_time += dt
            self.draw()
