import random

import pygame

from src.settings import settings
from src.utilities import utilities


class Sprite(pygame.sprite.Sprite):
    """Regular sprite"""
    def __init__(self, pos, surface, group, pos_z=settings.DEPTHS["main"]):
        """Initialize the sprite"""
        super().__init__(group)

        # Set the image
        self.image = surface
        # Get its rectangle, place it in the given position
        self.rect = self.image.get_rect(topleft=pos)
        # Hitboxes (make them a lot smaller vertically, because player should be able to go behind the sprite)
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

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

        # Get flower's hitboxes
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Tree(Sprite):
    """A tree class"""
    def __init__(self, pos, surface, group, name):
        """Prepare the tree"""
        super().__init__(pos, surface, group)

        # Apple surface and position
        self.apple_surface = utilities.load("../graphics/fruit/apple.png")
        self.apple_pos = settings.APPLE_POS[name]

        # Sprite group of apples of this tree
        self.apple_sprites = pygame.sprite.Group()
        # Create them
        self._create_apples()

    def _create_apples(self):
        """Create apples on the tree"""
        # Go through each apple position possible
        for pos in self.apple_pos:
            # Generate the apple randomly
            if random.randint(0, 11) < 2:
                Sprite((pos[0] + self.rect.left, pos[1] + self.rect.top),
                       self.apple_surface, [self.groups()[0], self.apple_sprites], settings.DEPTHS["fruit"])

