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


class Water(Sprite):
    """Water sprite class"""
    def __init__(self, pos, frames, group):
        """Create the water"""
        # Save the frames, set the current one
        self.frames = frames
        self.frame = 0

        # Initialize the parent sprite with the current frame
        super().__init__(pos, self.frames[self.frame], group, settings.DEPTHS["water"])

    def update(self, delta_time):
        """Update water"""
        self._animate(delta_time)

    def _animate(self, delta_time):
        """Animate the water"""
        # Increase the frame
        self.frame += (settings.ANIMATION_SPEED + 1) * delta_time
        # Set current frame as the image
        self.image = self.frames[int(self.frame) % len(self.frames)]


class Flower(Sprite):
    """Single flower"""
    def __init__(self, pos, surface, group):
        """Initialize the flower"""
        super().__init__(pos, surface, group)


class Tree(Sprite):
    """A tree class"""
    def __init__(self, pos, surface, group, name):
        """Prepare the tree"""
        super().__init__(pos, surface, group)
