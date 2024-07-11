import pygame
from pygame.math import Vector2 as Vector

from src.settings import settings


class CameraGroup(pygame.sprite.Group):
    """Group of sprites that are displayed based off camera position"""
    def __init__(self):
        """Initialize the camera group of sprites"""
        super().__init__()

        # Get game's display surface
        self.surface = pygame.display.get_surface()

        # Camera's offset
        self.offset = Vector()

    def custom_draw(self, player):
        """Draw the sprites with an offset"""
        # Calculate the offset based off player's position
        self.offset.x = player.rect.centerx - settings.SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - settings.SCREEN_HEIGHT / 2

        # Check every depth layer, to draw sprites in order depending on the depth
        for layer in settings.DEPTHS.values():
            # Go through each sprite sorted by the vertical position
            for sprite in sorted(self.sprites(), key=lambda element: element.rect.centery):
                # If sprite is on the current layer, draw it
                if sprite.pos_z == layer:
                    # Get the rectangle of sprite
                    offset_rect = sprite.rect.copy()
                    # Apply offset
                    offset_rect.center -= self.offset

                    # Blit it with the calculated offset
                    self.surface.blit(sprite.image, offset_rect)
