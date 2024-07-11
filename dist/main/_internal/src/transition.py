import pygame

from src.settings import settings


class Transition:
    """Transition that indicates time-skip through player's sleep"""
    def __init__(self, reset_day, player):
        """Prepare the transition"""
        # Get game's surface
        self.surface = pygame.display.get_surface()

        # Get player's reference
        self.player = player
        # Save the function to reset day
        self.reset_day = reset_day

        # Create a basic surface that fills the entire screen
        self.image = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        # Transition color in RGB value
        self.color = 255
        # Its speed
        self.speed = -2

    def display(self):
        """Display the transition effect"""
        # Update color based off speed
        self.color += self.speed

        # Make sure the color doesn't get negative
        if self.color <= 0:
            # Change color to 0
            self.color = 0
            # Reverse the speed, so it goes back to more visible colors
            self.speed *= -1
            # Reset the day
            self.reset_day()

        # End the transition and ensure that it doesn't get higher than 255
        if self.color >= 255:
            self.color = 255
            # Wake up the player
            self.player.sleep = False
            # Reset the transition
            self.speed = -2

        # Fill the screen with current color in hex
        self.image.fill((self.color, self.color, self.color))
        # Blit the transition (RGBA MULT makes lighter colors less visible)
        self.surface.blit(self.image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
