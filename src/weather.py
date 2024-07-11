import random

import pygame
from pygame.math import Vector2 as Vector

from src.utilities import utilities
from src.sprites import Sprite
from src.timer import Timer
from src.settings import settings


class Rain:
    """The rain weather class"""
    def __init__(self, sprites):
        """Prepare the rain"""
        # Save the sprites group
        self.sprites = sprites

        # Get the ground map to grab its size
        map_ground = utilities.load("../graphics/world/ground.png")
        # Get its size
        self.map_width = map_ground.width
        self.map_height = map_ground.height

        # Load surfaces
        self.puddle_surfaces = utilities.load_folder("../graphics/rain/floor")
        self.drops_surfaces = utilities.load_folder("../graphics/rain/drops")

    def update(self):
        """Update the rain weather"""
        # Create some puddles
        self._create_puddles()
        # Make some rain drops
        self._create_drops()

    def _create_drops(self):
        """Create rain drops"""
        # Get a random drop position within the map
        pos = (random.randint(0, self.map_width), random.randint(0, self.map_height))
        # Choose a random surface
        surface = random.choice(self.drops_surfaces)

        # Create the rain drop
        RainDrop(pos, surface, self.sprites, settings.DEPTHS["rain_drops"], True)

    def _create_puddles(self):
        """Create puddles when its raining"""
        # Random position within the map
        pos = (random.randint(0, self.map_width), random.randint(0, self.map_height))
        # Random puddle surface
        surface = random.choice(self.puddle_surfaces)

        # Create the puddle (as not moving rain drop)
        RainDrop(pos, surface, self.sprites, settings.DEPTHS["rain_floor"], False)


class RainDrop(Sprite):
    """A single rain drop"""
    def __init__(self, pos, surface, group, pos_z, move):
        """Create the raindrop"""
        # Initialize the parent Sprite
        super().__init__(pos, surface, group, pos_z)

        # Duration of the rain drop
        self.duration = random.randint(350, 550)

        # Move flag
        self.move = move
        # If the drop is moving, set its movement parameters
        if self.move:
            self.speed = random.randint(220, 270)
            self.pos = Vector(self.rect.topleft)
            self.direction = Vector(-2, 4)

        # Lifetime timer
        self.timer = Timer(self.duration)
        # Start it
        self.timer.start()

    def update(self, delta_time):
        """Update the rain drop's position and lifetime"""
        # Update the timer
        self.timer.update()

        # If the drop is moving, change its position
        if self.move:
            self.pos += self.direction * self.speed * delta_time
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        # If the drop's lifetime ended, destroy it
        if not self.timer.active:
            self.kill()
