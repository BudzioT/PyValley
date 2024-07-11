from os.path import join as path_join

import pygame

from src.settings import settings


class Menu:
    """Interactive menu class"""
    def __init__(self, player, activate_menu):
        """Initialize the menu"""
        # Get game's display
        self.surface = pygame.display.get_surface()
        # Store the reference to the player
        self.player = player

        # Grab the font, set its size to 30
        self.font = pygame.font.Font(path_join(settings.BASE_PATH, "../font/LycheeSoda.ttf"), 30)

        # Get the function to activate menu
        self.activate_menu = activate_menu

        # Starting height
        self.height = 0
        # Menu style variables
        self.width = 400
        self.margin = 10
        self.padding = 8

        # Menu entries, items (got from player's items and seeds)
        self.entries = list(self.player.items.keys()) + list(self.player.current_seeds.keys())

        # Count of items that player can sell
        self.sell_count = len(self.player.items) - 1

        # Further initialize the menu
        self._initialize()

    def update(self):
        """Update the shop menu"""
        # Handle input
        self._handle_input()

        # Show the menu
        self._display()

    def _handle_input(self):
        """Check and handle menu's input"""
        # Get keys that are pressed
        keys = pygame.key.get_pressed()

        # If user pressed escape, close the menu
        if keys[pygame.K_ESCAPE]:
            self.activate_menu()

    def _display(self):
        """Display the menu"""
        # Show the menu surface
        # self.surface.blit(pygame.Surface((1000, 1000)), (0, 0))

        # Check every text surface and blit it
        for index, text_surface in enumerate(self.text_surfaces):
            self.surface.blit(text_surface, (100, index * 50))

        # Display the player's money
        self._display_money()

    def _display_money(self):
        """Display current player's amount of money"""
        # Create a text surface with dollar sign before the amount of money
        text_surface = self.font.render(f"${self.player.money}", False, "black")
        # Create surface rectangle, place it in the correct place
        text_rect = text_surface.get_rect(midbottom=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2))

        # Draw a background rounded  rectangle
        pygame.draw.rect(self.surface, "white", text_rect.inflate(10, 10), 0, 5)

        # Blit the money text
        self.surface.blit(text_surface, text_rect)

    def _display_entry(self, text_surface, amount, top):
        """Display given entry in the menu"""
        # Create the background rectangle with given top position and set padding
        bg_rect = pygame.Rect(self.rect.left, top, self.width, text_surface.get_height() + (self.padding * 2))

    def _initialize(self):
        """Initialize components of the menu"""
        # Prepare list for text surfaces
        self.text_surfaces = []

        # Go through each item in the entries
        for item in self.entries:
            # Render the item's name text surface
            text_surface = self.font.render(item, False, "black")
            # Append it to the list
            self.text_surfaces.append(text_surface)

            # Increase the menu's height (with padding)
            self.height += text_surface.get_height() + (self.padding * 2)

        # Add all the margin between the surfaces to the height too
        self.height += self.margin * (len(self.text_surfaces) - 1)

        # Set the top place of the menu (center the menu in the screen)
        self.top = settings.SCREEN_HEIGHT / 2 - self.height / 2

        # Main rectangle of the window
        self.rect = pygame.Rect(settings.SCREEN_WIDTH / 2 - self.width / 2, self.top, self.width, self.height)
