import pygame

from utilities import utilities


class Soil:
    """Class that represents soil path"""
    def __init__(self, sprites):
        """Initialize the soil"""
        # Get all the game's visible sprites
        self.sprites = sprites
        # Soil sprites
        self.soil_sprites = pygame.sprite.Group()

        # Get the surface
        self.surface = utilities.load("../graphics/soil/o.png")
