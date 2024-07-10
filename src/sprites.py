import random

import pygame

from src.settings import settings
from src.utilities import utilities
from src.timer import Timer


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
    def __init__(self, pos, surface, group, name, obtain_item):
        """Prepare the tree"""
        super().__init__(pos, surface, group)

        # Apple surface and position
        self.apple_surface = utilities.load("../graphics/fruit/apple.png")
        self.apple_pos = settings.APPLE_POS[name]

        # Tree's health and alive flag
        self.health = 5
        self.alive = True

        # Get stump's image name depending on the tree size
        stump_name = "small" if name == "Small" else "large"
        # Tree stump surface
        self.stump = utilities.load(f"../graphics/stumps/{stump_name}.png")

        # Sprite group of apples of this tree
        self.apple_sprites = pygame.sprite.Group()
        # Create them
        self._create_apples()

        # Allow player to obtain items
        self.obtain_item = obtain_item

        # Time of invincibility
        self.dodge_time = Timer(200)

    def update(self, delta_time):
        """Update the tree"""
        # Check and handle tree's death if it's still alive
        if self.alive:
            self._check_destroy()

    def handle_damage(self):
        """Handle tree getting damaged"""
        # Decrease the health
        self.health -= 1

        # If there are any apples, try to remove a random one
        if len(self.apple_sprites.sprites()) > 0:
            # Choose a random apple
            apple = random.choice(self.apple_sprites.sprites())

            # Generate a particle
            Particle(apple.rect.topleft, apple.image, self.groups()[0], settings.DEPTHS["fruit"])

            # Destroy the apple
            apple.kill()

    def _create_apples(self):
        """Create apples on the tree"""
        # Go through each apple position possible
        for pos in self.apple_pos:
            # Generate the apple randomly
            if random.randint(0, 11) < 2:
                Sprite((pos[0] + self.rect.left, pos[1] + self.rect.top),
                       self.apple_surface, [self.groups()[0], self.apple_sprites], settings.DEPTHS["fruit"])

    def _check_destroy(self):
        """Check if tree is destroyed, handle it"""
        if self.health <= 0:
            # Set the alive flag to false
            self.alive = False

            # Create a particle
            Particle(self.rect.topleft, self.image, self.groups()[0], self.pos_z)

            # Replace the tree's image with a stump one, get its rect and hitboxes
            self.image = self.stump
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)


class Particle(Sprite):
    """Class representing a single particle type mask"""
    def __init__(self, pos, surface, group, pos_z, duration=150):
        """Initialize the particle mask"""
        super().__init__(pos, surface, group, pos_z)

        # Particle alive timer
        self.timer = Timer(duration)

        # White mask created from the image surface
        self.image = pygame.mask.from_surface(self.image).to_surface()
        # Set the color key, to get rid of the black part of mask
        self.image.set_colorkey("black")

        # Start the alive timer
        self.timer.start()

    def update(self, delta_time):
        """Update the particle mask"""
        # Update timer
        self.timer.update()

        # If the particle duration ended, destroy the particle mask
        if not self.timer.active:
            self.kill()
