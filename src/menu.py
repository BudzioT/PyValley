from os.path import join as path_join

import pygame

from src.settings import settings


class Menu:
    """Interactive menu class"""
    def __init__(self, plater, activate_menu):
        """Initialize the menu"""
        # Get game's display
        self.surface = pygame.display.get_surface()

        # Store the reference to the player
        self.player = player

        # Grab the font, set its size to 30
        self.font = pygame.font.Font(path_join(settings.BASE_PATH, "../font/LycheeSoda.ttf"), 30)
