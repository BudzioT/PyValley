import pygame

from src.utilities import utilities
from src.settings import settings


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

    def display(self):
        """Display the UI"""
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
