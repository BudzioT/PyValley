import pygame

from src.settings import settings


class Sky:
    """Class representing sky"""
    def __init__(self):
        """Prepare the sky"""
        # Grab the game's surface
        self.surface = pygame.display.get_surface()

        # Create a surface that fills the entire screen
        self.screen_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

        # Start and end colors of the sky animation
        self.start_color = [255, 255, 255]
        self.end_color = (40, 100, 190)

    def display(self, delta_time):
        """Display the sky"""
        # Go through each part of the RGB value of end color
        for part, value in enumerate(self.end_color):
            # If the starting color is still higher than the end one, decrease the starting color
            if self.start_color[part] > value:
                self.start_color[part] -= 2 * delta_time

        # Fill the surface with calculated color
        self.screen_surface.fill(self.start_color)
        # Blit the sky animation
        self.surface.blit(self.screen_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
