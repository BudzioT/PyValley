import pygame
from pygame.math import Vector2 as Vector


class CameraGroup(pygame.sprite.Group):
    """Group of sprites that are displayed based off camera position"""
    def __init__(self):
        """Initialize the camera group of sprites"""
        super().__init__()

        # Get game's display surface
        self.surface = pygame.display.get_surface()

        # Camera's offset
        self.offset = Vector()

    def custom_draw(self):
        """Draw the sprites with an offset"""
        # Go through each sprite sorted by the depth position
        for sprite in sorted(self.sprites(), key=lambda element: element.pos_z):
            # Blit it
            self.surface.blit(sprite.image, sprite.rect)
