import random

import pygame

from src.utilities import utilities
from src.settings import settings
from src.sprites import AnimatedSprite


class UI:
    """User's interface of the game"""
    def __init__(self, player):
        """Initialize the user's interface"""
        # Get main surface
        self.surface = pygame.display.get_surface()

        # Save reference to the player
        self.player = player

        # Path to the UI images
        path = "../graphics/overlay/"
        # Load the tool surfaces
        self.tool_surfaces = {tool: utilities.load(f"{path}{tool}.png") for tool in player.tools}
        # Load the seed surfaces
        self.seed_surfaces = {seed: utilities.load(f"{path}{seed}.png") for seed in player.seeds}

        # Get the heart frames
        self.heart_frames = utilities.load_folder("../graphics/overlay/heart")
        # Get the width of frames
        self.heart_width = self.heart_frames[0].get_width()
        # Heart padding
        self.heart_padding = 10

        # Group of UI sprites
        self.sprites = pygame.sprite.Group()

        # Create first hearts
        self.create_hearts(self.player.health)

    def display(self, delta_time):
        """Display the UI"""
        # Update hearts
        self.sprites.update(delta_time)

        # Get the current tool surface
        tool_surface = self.tool_surfaces[self.player.tool]
        # Get its rectangle
        tool_rect = tool_surface.get_rect(midbottom=settings.ICON_POSITIONS["tool"])

        # Draw it
        self.surface.blit(tool_surface, tool_rect)

        # Get the current seed surface and its rectangle
        seed_surface = self.seed_surfaces[self.player.seed]
        seed_rect = seed_surface.get_rect(midbottom=settings.ICON_POSITIONS["seed"])

        # Draw the seed icon
        self.surface.blit(seed_surface, seed_rect)

        # Draw the hearts
        self.sprites.draw(self.surface)

    def create_hearts(self, amount):
        """Create heart sprites"""
        # Destroy the old ones
        for heart in self.sprites:
            heart.kill()

        # Create specified amount of hearts
        for heart_num in range(amount):
            # Calculate positions
            pos_x = 10 + heart_num * (self.heart_width + self.heart_padding)
            pos_y = 10

            # Create the heart
            Heart((pos_x, pos_y), self.heart_frames, self.sprites)


class Heart(AnimatedSprite):
    """Heart sprite with animation"""
    def __init__(self, pos, frames, group):
        """Initialize the heart sprite"""
        super().__init__(pos, frames, group)

        # Animation flag
        self.active = False

    def update(self, delta_time):
        """Update the heart"""
        # Animate the heart if active
        if self.active:
            self._animate(delta_time)

        # Otherwise, active it at random times
        else:
            if random.randint(0, 400) == 1:
                self.active = True

    def _animate(self, delta_time):
        """Animate the heart"""
        # Increase the frame
        self.frame += self.animation_speed * delta_time

        # Play the animation until the end
        if self.frame < len(self.frames):
            self.image = self.frames[int(self.frame)]

        # Otherwise deactivate the heart and reset the animation
        else:
            self.active = False
            self.frame = 0
