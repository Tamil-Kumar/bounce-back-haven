'''
Haven Hackathon
Theme: Bounce Back

Date: 11/15/2026
Author: Tamil Kumar, Srihaas Yeluri

This module handles the entity creation and movement in the game.
'''

import math

import pygame
import pygame.gfxdraw

from settings import *
from ui import bar, soft_circle

# Loads and resizes character

def load_character():
    image = pygame.image.load(CHARACTER_FILE).convert_alpha()
    image = image.subsurface(image.get_bounding_rect())
    scale = max(1, PLAYER_RADIUS * 2 // max(image.get_size()))
    return pygame.transform.scale_by(image, scale)

# Creates player class

class Player:

    # Initializes variables

    def __init__(self):
        self.image = load_character()
        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.last_pos = self.pos.copy()
        self.aim = 0.0
        self.lives = BASE_LIVES
        self.invuln = 0.0
        self.heat = 0.0
        self.shield_level = 0
        self.speed = PLAYER_SPEED
        self.heat_time = HEAT_TIME
        self.recovery = HIT_INVULN

    # Update conditions for the player

    def update(self, dt, keys, mouse):
        self.last_pos = self.pos.copy()
        move = pygame.Vector2(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT]),
            (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP]),
        )
        if move.length_squared():
            self.pos += move.normalize() * self.speed * dt
        self.pos.x = max(PLAYER_RADIUS, min(WIDTH - PLAYER_RADIUS, self.pos.x))
        self.pos.y = max(PLAYER_RADIUS, min(HEIGHT - PLAYER_RADIUS, self.pos.y))
        if mouse != self.pos:
            self.aim = math.atan2(mouse[1] - self.pos.y, mouse[0] - self.pos.x)

        self.invuln = max(0.0, self.invuln - dt)

        # Hot zone mechanic

        safe = HOT_ZONE < self.pos.x < WIDTH - HOT_ZONE and HOT_ZONE < self.pos.y < HEIGHT - HOT_ZONE
        if safe:
            self.heat = max(0.0, self.heat - dt / COOL_TIME)
        else:
            self.heat = min(1.0, self.heat + dt / self.heat_time)

    # Damage mechanic

    def hurt(self):
        if self.invuln > 0:
            return False
        self.lives -= 1
        self.invuln = self.recovery
        return True

    # Returns shield drawing info

    def shield_arcs(self):
        if self.shield_level >= 5:
            return [(self.aim, 0.25), (self.aim + math.pi, 0.25)]
        return [(self.aim, SHIELD_SIZES[self.shield_level])]

    # Calculate shield angles

    def on_shield(self, angle, margin):
        for center, size in self.shield_arcs():
            diff = (angle - center + math.pi) % math.tau - math.pi
            if abs(diff) <= size * math.pi + margin:
                return True
        return False

    # Draws player and shield

    def draw(self, surf, alpha):

        # Player

        pos = self.last_pos + (self.pos - self.last_pos) * alpha
        if self.invuln <= 0 or int(self.invuln * 10) % 2 == 0: # Blinking player mechanic
            image = self.image
            if self.heat > 0: # Hot zone dimming mechanic
                image = image.copy()
                image.fill(pygame.Color(255, 255, 255).lerp(HOT_COLOR, self.heat), special_flags=pygame.BLEND_RGB_MULT)
            surf.blit(image, image.get_rect(center=(round(pos.x), round(pos.y))))

        # Shield

        inner, outer = SHIELD_RADIUS - SHIELD_WIDTH / 2, SHIELD_RADIUS + SHIELD_WIDTH / 2 # Shield points
        for center, size in self.shield_arcs(): # Draw shield points
            angles = [center + size * math.pi * (i / 12 - 1) for i in range(25)]
            points = [pos + pygame.Vector2(outer, 0).rotate_rad(a) for a in angles]
            points += [pos + pygame.Vector2(inner, 0).rotate_rad(a) for a in reversed(angles)]
            pygame.gfxdraw.filled_polygon(surf, points, SHIELD_COLOR)
            pygame.gfxdraw.aapolygon(surf, points, SHIELD_COLOR)

        # Hot zone bar

        if self.heat > 0:
            side = -1 if self.pos.y > 80 else 1
            rect = pygame.Rect(0, 0, 40, 5)
            rect.center = (self.pos.x, self.pos.y + side * (SHIELD_RADIUS + 14))
            bar(surf, rect, self.heat, HOT_COLOR)

# Creates enemy class

class Enemy:

    # Initializes the enemy position

    def __init__(self, pos):
        self.reset(pos)

    # Resets the enemy

    def reset(self, pos):
        self.pos = pygame.Vector2(pos)
        self.last_pos = self.pos.copy()
        self.vel = pygame.Vector2()
        self.bouncing = False
        self.warmup = WARMUP

    # Moves the enemies and check if its 

    def move(self, target, speed, dt):
        self.last_pos = self.pos.copy()
        if not self.bouncing and target != self.pos:
            desired = (target - self.pos).normalize() * speed
            self.vel = self.vel.lerp(desired, min(1.0, TURN_RATE * dt)) if self.vel.length_squared() else desired
        if self.vel.length_squared():
            self.vel.scale_to_length(speed)
        self.pos += self.vel * dt

        # Checks if the enemy has hit the player
        
        hit = False
        for i, size in enumerate((WIDTH, HEIGHT)):
            if self.pos[i] < ENEMY_RADIUS:
                self.pos[i], self.vel[i], hit = ENEMY_RADIUS, abs(self.vel[i]), True
            elif self.pos[i] > size - ENEMY_RADIUS:
                self.pos[i], self.vel[i], hit = size - ENEMY_RADIUS, -abs(self.vel[i]), True
        return hit

    # Draws the enemies

    def draw(self, surf, slowed, alpha):
        if self.warmup > 0:
            radius = round(ENEMY_RADIUS + 12 * self.warmup / WARMUP)
            pygame.gfxdraw.aacircle(surf, round(self.pos.x), round(self.pos.y), radius, ENEMY_COLOR)
            return
        color = SLOW_COLOR if slowed else BOUNCE_COLOR if self.bouncing else ENEMY_COLOR
        soft_circle(surf, color, self.last_pos + (self.pos - self.last_pos) * alpha, ENEMY_RADIUS)

# Creates a laser class

class Laser:

    # Initializes variables for the laser

    def __init__(self, pos, direction):
        self.pos = pygame.Vector2(pos)
        self.dir = pygame.Vector2(direction)
        self.alive = True

    # Updates the location of the laser

    def update(self, dt):
        self.pos += self.dir * LASER_SPEED * dt
        if not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT):
            self.alive = False

    # Checks if laser is hitting enemy

    def hits(self, point, radius):
        tail = self.pos - self.dir * LASER_LENGTH
        t = max(0.0, min(1.0, (point - tail).dot(self.dir) / LASER_LENGTH))
        return point.distance_to(tail + self.dir * LASER_LENGTH * t) < radius
    
    # Draws the laser

    def draw(self, surf):
        pygame.draw.line(surf, LASER_COLOR, self.pos - self.dir * LASER_LENGTH, self.pos, 2)
