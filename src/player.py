import pygame
from pygame.math import Vector2 as Vector


class Player(pygame.sprite.Sprite):
    """Player of the game"""
    def __init__(self, pos, group):
        """Initialize the player"""
        super().__init__(group)

        # Set his image (temporary a black rectangle)
        self.image = pygame.Surface((32, 64))
        self.image.fill("black")

        # Get his rectangle, center him around given position
        self.rect = self.image.get_rect(center=pos)

        # Player's direction
        self.direction = Vector()

    def update(self, delta_time):
        """Update the player"""
        # Handle input
        self._handle_input()

    def _handle_input(self):
        """Check and handle the player's input"""
        # Get the keys pressed
        keys = pygame.key.get_pressed()
