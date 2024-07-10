import pygame

from src.player import Player


class Level:
    """Level - the main part of the game"""
    def __init__(self):
        """Initialize the level"""
        # Get the game's display
        self.surface = pygame.display.get_surface()

        # Group of all sprites
        self.sprites = pygame.sprite.Group()

        # Set up the level
        self._initialize()

    def run(self, delta_time):
        """Run the level"""
        # Update the surface
        self._update_surface()

        # Update elements positions
        self._update_positions(delta_time)

    def _update_surface(self):
        """Update the level's surface, draw the elements"""
        # Fill the surface with a color
        self.surface.fill("gray")

        # Draw all the sprites
        self.sprites.draw(self.surface)

    def _update_positions(self, delta_time):
        """Update positions of level's elements"""
        # Update all sprites
        self.sprites.update(delta_time)

    def _initialize(self):
        """Initialize and set up the entire level"""
        self.player = Player((640, 360), self.sprites)
