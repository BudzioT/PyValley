from os.path import join as path_join

import pygame

from src.settings import settings
from src.timer import Timer


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
        # Amounts of entries
        self.amounts = []

        # Count of items that player can sell
        self.sell_count = len(self.player.items) - 1

        # Index of menu
        self.index = 0
        # Select timer
        self.timer = Timer(250)

        # Further initialize the menu
        self._initialize()

    def update(self):
        """Update the shop menu"""
        # Update the timer
        self.timer.update()

        # Handle input
        self._handle_input()

        # Get the amount of entries
        self._update_amount()

        # Show the menu
        self._display()

    def _handle_input(self):
        """Check and handle menu's input"""
        # Get keys that are pressed
        keys = pygame.key.get_pressed()

        # If user pressed escape, close the menu
        if keys[pygame.K_ESCAPE]:
            self.activate_menu()

        # Allow selecting when select cooldown is off
        if not self.timer.active:
            # On up decrease the index (higher index is lower)
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.index -= 1
                # Activate the cooldown
                self.timer.start()

            # On down, decrease the index
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.index += 1
                # Start the timer
                self.timer.start()

            # Don't allow for too low index, make it loop
            if self.index < 0:
                self.index = len(self.entries) - 1
            # Don't allow higher ones too
            if self.index >= len(self.entries):
                self.index = 0

            # If player presses space, try to buy or sell the entry
            if keys[pygame.K_SPACE]:
                # Get the selected entry
                entry = self.entries[self.index]
                # Handle shopping
                self._shop(entry)



    def _display(self):
        """Display the menu"""
        # Check every text surface and blit it
        for index, text_surface in enumerate(self.text_surfaces):
            # Calculate the top position
            top = self.rect.top + index * (text_surface.get_height() + (self.padding * 2) + self.margin)
            # Show the entry
            self._display_entry(text_surface, self.amounts[index], top, self.index == index)

        # Display the player's money
        self._display_money()

    def _display_money(self):
        """Display current player's amount of money"""
        # Create a text surface with dollar sign before the amount of money
        text_surface = self.font.render(f"${self.player.money}", False, "black")
        # Create surface rectangle, place it in the correct place
        text_rect = text_surface.get_rect(midbottom=(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT - 20))

        # Draw a background rounded  rectangle
        pygame.draw.rect(self.surface, "white", text_rect.inflate(10, 10), 0, 5)

        # Blit the money text
        self.surface.blit(text_surface, text_rect)

    def _display_entry(self, text_surface, amount, top, select):
        """Display given entry in the menu"""
        # Create the background rectangle with given top position and set padding
        bg_rect = pygame.Rect(self.rect.left, top, self.width, text_surface.get_height() + (self.padding * 2))

        # Reposition the text rectangle
        text_rect = text_surface.get_rect(midleft=(self.rect.left + 20, bg_rect.centery))

        # Create amount text surface
        amount_surface = self.font.render(str(amount), False, "black")
        # Get its rectangle and set position of it
        amount_rect = amount_surface.get_rect(midright=(self.rect.right - 20, bg_rect.centery))

        # Draw the background rectangle
        pygame.draw.rect(self.surface, "white", bg_rect, 0, 5)
        # Blit the entry text
        self.surface.blit(text_surface, text_rect)
        # Blit the amount text surface
        self.surface.blit(amount_surface, amount_rect)

        # If this entry is selected, draw a border around it
        if select:
            # Draw the border
            pygame.draw.rect(self.surface, "black", bg_rect, 4, 4)

            # If this index is in the buy-zone, try to buy an entry
            if self.index > self.sell_count:
                # Get and position the buy text's rectangle
                buy_rect = self.buy_text.get_rect(midleft=(self.rect.left + 250, bg_rect.centery))
                # Blit the buy text
                self.surface.blit(self.buy_text, buy_rect)
            # Otherwise try to sell an entry
            else:
                # Position the sell text's rectangle
                sell_rect = self.sell_text.get_rect(midleft=(self.rect.left + 250, bg_rect.centery))
                # Draw the sell text
                self.surface.blit(self.sell_text, sell_rect)

    def _update_amount(self):
        """Update amount of every entry"""
        self.amounts = list(self.player.items.values()) + list(self.player.current_seeds.values())

    def _shop(self, entry):
        """Allow player to buy and sell items"""
        # If player is buying
        if self.index > self.sell_count:
            # Get the price of an item
            price = settings.PURCHASE_PRICES[entry]

            # Check if user has enough money, if so, buy the item
            if self.player.money >= price:
                # Add item to the inventory
                self.player.current_seeds[entry] += 1
                # Decrease his amount of money
                self.player.money -= price

        # Otherwise, if player is selling

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

        # Text for buying and selling
        self.buy_text = self.font.render("buy", False, "black")
        self.sell_text = self.font.render("sell", False, "black")
