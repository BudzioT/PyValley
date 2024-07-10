import pygame

from src.player import Player
from src.ui import UI
from src.groups import CameraGroup
from src.sprites import Sprite
from src.utilities import utilities
from src.settings import settings


class Level:
    """Level - the main part of the game"""
    def __init__(self):
        """Initialize the level"""
        # Get the game's display
        self.surface = pygame.display.get_surface()

        # Group of all sprites
        self.sprites = CameraGroup()

        # Set up the level
        self._initialize()

        # Game's user's interface
        self.ui = UI(self.player)

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
        self.sprites.custom_draw()

        # Draw the user's interface
        self.ui.display()

    def _update_positions(self, delta_time):
        """Update positions of level's elements"""
        # Update all sprites
        self.sprites.update(delta_time)

    def _initialize(self):
        """Initialize and set up the entire level"""
        # Create the player
        self.player = Player((640, 360), self.sprites)

        # Create ground
        Sprite((0, 0), utilities.load("../graphics/world/ground.png"), self.sprites, settings.DEPTHS["ground"])
