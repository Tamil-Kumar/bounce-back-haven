'''
Haven Hackathon
Theme: Bounce Back

Date: 11/15/2026
Author: Tamil Kumar, Srihaas Yeluri

This module handles the UI layout and components of the game.
'''

import math

import pygame
import pygame.gfxdraw

import upgrades
from settings import *


def soft_circle(surf, color, pos, radius):
    x, y, r = round(pos[0]), round(pos[1]), round(radius)
    pygame.gfxdraw.filled_circle(surf, x, y, r, color)
    pygame.gfxdraw.aacircle(surf, x, y, r, color)


def bar(surf, rect, ratio, color):
    pygame.draw.rect(surf, CARD, rect, border_radius=rect.height // 2)
    if ratio > 0:
        fill = pygame.Rect(rect.x, rect.y, max(rect.height, int(rect.width * ratio)), rect.height)
        pygame.draw.rect(surf, color, fill, border_radius=rect.height // 2)


def wrap(font, text, width):
    lines = [""]
    for word in text.split():
        test = (lines[-1] + " " + word).strip()
        if font.size(test)[0] <= width:
            lines[-1] = test
        else:
            lines.append(word)
    return lines


class Ui:
    def __init__(self):
        self.big = pygame.font.SysFont(FONT_NAME, 52)
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.small = pygame.font.SysFont(FONT_NAME, 17)
        self.background = pygame.Surface((WIDTH, HEIGHT))
        self.background.fill(HOT_ZONE_FILL)
        inner = (HOT_ZONE, HOT_ZONE, WIDTH - HOT_ZONE * 2, HEIGHT - HOT_ZONE * 2)
        pygame.draw.rect(self.background, BG, inner, border_radius=16)
        self.shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.shade.fill((12, 13, 18, 170))

    def text(self, surf, msg, font, color, pos, anchor="midtop"):
        img = font.render(msg, True, color)
        surf.blit(img, img.get_rect(**{anchor: pos}))

    def card_rects(self, count):
        w, h, gap = 250, 140, 24
        x0 = (WIDTH - count * w - (count - 1) * gap) // 2
        return [pygame.Rect(x0 + i * (w + gap), 250, w, h) for i in range(count)]

    def draw_hud(self, surf, game):
        self.text(surf, f"Score {game.score}", self.font, TEXT, (16, 10), "topleft")
        bar(surf, pygame.Rect(16, 44, 180, 6), game.progress / game.needed(), PLAYER_COLOR)
        self.text(surf, f"Lv {game.level}", self.small, DIM, (206, 37), "topleft")
        for i in range(game.player.lives):
            soft_circle(surf, PLAYER_COLOR, (WIDTH - 24 - i * 22, 24), 7)
        if game.levels["slow"]:
            if game.slow_timer > 0:
                msg, color = f"Slow {game.slow_timer:.1f}s", SLOW_COLOR
            elif game.slow_cooldown > 0:
                msg, color = f"Slow in {math.ceil(game.slow_cooldown)}s", DIM
            else:
                msg, color = "Slow ready [Space]", SLOW_COLOR
            self.text(surf, msg, self.small, color, (WIDTH // 2, 14))

    def draw_upgrades(self, surf, game):
        surf.blit(self.shade, (0, 0))
        self.text(surf, "Level Up", self.big, TEXT, (WIDTH // 2, 120))
        self.text(surf, "Click or press 1-3", self.small, DIM, (WIDTH // 2, 186))
        mouse = pygame.mouse.get_pos()
        for key, rect in zip(game.choices, self.card_rects(len(game.choices))):
            pygame.draw.rect(surf, CARD_HOVER if rect.collidepoint(mouse) else CARD, rect, border_radius=12)
            name, cap = upgrades.UPGRADES[key]
            level = game.levels[key] + 1
            self.text(surf, name, self.font, TEXT, (rect.x + 18, rect.y + 16), "topleft")
            self.text(surf, f"Level {level}/{cap}", self.small, PLAYER_COLOR, (rect.x + 18, rect.y + 50), "topleft")
            for i, line in enumerate(wrap(self.small, upgrades.describe(key, level), rect.width - 36)):
                self.text(surf, line, self.small, DIM, (rect.x + 18, rect.y + 82 + i * 22), "topleft")

    def draw_screen(self, surf, title, lines, prompt=None, shade=True):
        if shade:
            surf.blit(self.shade, (0, 0))
        self.text(surf, title, self.big, TEXT, (WIDTH // 2, 140))
        y = 230
        for line in lines:
            self.text(surf, line, self.small, DIM, (WIDTH // 2, y))
            y += 28
        if prompt:
            self.text(surf, prompt, self.font, PLAYER_COLOR, (WIDTH // 2, y + 30))
