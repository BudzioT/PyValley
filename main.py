import sys

import pygame

from src.settings import settings
from src.level import Level


class Game:
    """The main game class"""
    def __init__(self):
        """Initialize the entire game"""
        # Prepare pygame
        pygame.init()

        # Get the display surface
        self.surface = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        # Set its caption
        pygame.display.set_caption("PyValley")

        # Get the timer for calculating FPS
        self.timer = pygame.time.Clock()

        # Game's level
        self.level = Level()

    def run(self):
        """Run the game"""
        # Game's loop
        while True:
            # Check and handle events
            self._get_events()

            # Remain 60 FPS
            delta_time = self.timer.tick(60) / 1000

            # Run the level
            self.level.run(delta_time)

            # Update the display surface
            self._update_surface()

    def _get_events(self):
        """Get the input events and handle them"""
        # Check every event
        for event in pygame.event.get():
            # If user wants to quit, let him do it
            if event.type == pygame.QUIT:
                # Free pygame's resources
                pygame.quit()
                # Exit the program
                sys.exit()

    def _update_surface(self):
        """Draw things onto the surface"""
        # Update the display
        pygame.display.update()


# If it's the main file, run it
if __name__ == "__main__":
    # Create and run the game
    game = Game()
    game.run()

# IDEA: ADD HEARTS, NEED TO EAT SURVIVAL MECHANIC
