'''
Haven Hackathon
Theme: Bounce Back

Date: 11/15/2026
Author: Tamil Kumar, Srihaas Yeluri

This module is the main file that starts and stops pygame. Imports from game.py.
'''

import pygame

from game import Game

# Main game function

def main():
    pygame.init()
    Game().run()
    pygame.quit()


if __name__ == "__main__":
    main()
