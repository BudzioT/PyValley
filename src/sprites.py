import pygame

from src.settings import settings


class Sprite(pygame.sprite.Sprite):
    """Regular sprite"""
    def __init__(self, pos, surface, group, pos_z=settings.DEPTHS["main"]):
        """Initialize the sprite"""
        super().__init__(group)

        # Set the image
        self.image = surface
        # Get its rectangle, place it in the given position
        self.rect = self.image.get_rect(topleft=pos)

        # Depth position of the sprite
        self.pos_z = pos_z
