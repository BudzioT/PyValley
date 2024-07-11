from os.path import join as path_join

import pygame
from pytmx.util_pygame import load_pygame

from src.player import Player
from src.ui import UI
from src.groups import CameraGroup
from src.sprites import Sprite, Water, Flower, Tree, InteractiveSprite
from src.utilities import utilities
from src.settings import settings
from src.transition import Transition
from src.soil import Soil
from src.weather import Rain


class Level:
    """Level - the main part of the game"""
    def __init__(self):
        """Initialize the level"""
        # Get the game's display
        self.surface = pygame.display.get_surface()

        # Group of all sprites
        self.sprites = CameraGroup()
        # Interactive sprites
        self.interactive_sprites = pygame.sprite.Group()
        # Sprites that have collisions
        self.collision_sprites = pygame.sprite.Group()

        # Tree sprites
        self.tree_sprites = pygame.sprite.Group()

        # Soil layer
        self.soil = Soil(self.sprites)

        # Set up the level
        self._initialize()

        # Day-skip transition
        self.transition = Transition(self._reset_day, self.player)

        # Rain weather
        self.rain = Rain(self.sprites)
        # Rain flag
        self.rain_active = True

        # Game's user's interface
        self.ui = UI(self.player)

    def run(self, delta_time):
        """Run the level"""
        # Update the surface
        self._update_surface()

        # Update elements positions
        self._update_positions(delta_time)

    def _update_surface(self):
        """Update the level's surface, draw the elements"""
        # Fill the surface with a color
        self.surface.fill("gray")

        # Draw all the sprites
        self.sprites.custom_draw(self.player)

        # Draw the user's interface
        self.ui.display()

    def _update_positions(self, delta_time):
        """Update positions of level's elements"""
        # Update all sprites
        self.sprites.update(delta_time)

        # If it's raining, update the rain weather
        if self.rain_active:
            self.rain.update()

        # If player sleeps, run the day skip transition
        if self.player.sleep:
            self.transition.display()

    def _obtain_item(self, item):
        """Obtain one more of the given item"""
        self.player.items[item] += 1

    def _reset_day(self):
        """Reset everything that happens in a one-day cycle"""
        # Destroy apples from every tree on the map
        for tree in self.tree_sprites.sprites():
            # Destroy apples
            tree.destroy_apples()
            # Create new ones
            tree.create_apples()

        # Remove water from the soil
        self.soil.remove_water()

    def _initialize(self):
        """Initialize and set up the entire level"""
        # Create ground
        Sprite((0, 0), utilities.load("../graphics/world/ground.png"), self.sprites, settings.DEPTHS["ground"])

        # Load tmx map data
        map_data = load_pygame(path_join(settings.BASE_PATH, "../data/map.tmx"))

        # BUILD A HOUSE
        # Go through each layer of bottom of the house
        for layer in ["HouseFloor", "HouseFurnitureBottom"]:
            # Check where are these layers placed
            for pos_x, pos_y, surface in map_data.get_layer_by_name(layer).tiles():
                # Place them in the game
                Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface, self.sprites,
                       settings.DEPTHS["house_bottom"])
        # Go through each top layer of house
        for layer in ["HouseWalls", "HouseFurnitureTop"]:
            # Check placement of layers
            for pos_x, pos_y, surface in map_data.get_layer_by_name(layer).tiles():
                # Place the objects
                Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface, self.sprites)

        # Build fences
        for pos_x, pos_y, surface in map_data.get_layer_by_name("Fence").tiles():
            # Place the fences
            Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface,
                   [self.sprites, self.collision_sprites])

        # Get the frames of water animation
        water_frames = utilities.load_folder("../graphics/water")
        # Place water
        for pos_x, pos_y, surface in map_data.get_layer_by_name("Water").tiles():
            Water((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), water_frames,
                  [self.sprites, self.collision_sprites])

        # Create trees
        for tree in map_data.get_layer_by_name("Trees"):
            Tree((tree.x, tree.y), tree.image,
                 [self.sprites, self.tree_sprites, self.collision_sprites], tree.name, self._obtain_item)

        # Create flowers
        for flower in map_data.get_layer_by_name("Decoration"):
            Flower((flower.x, flower.y), flower.image, [self.sprites, self.collision_sprites])

        # Place the invisible collision sprites
        for pos_x, pos_y, surface in map_data.get_layer_by_name("Collision").tiles():
            Sprite((pos_x * settings.TILE_SIZE, pos_y * settings.TILE_SIZE), surface, self.collision_sprites)

        # Create the player related tiles
        for player in map_data.get_layer_by_name("Player"):
            # If it's his starting position, create him
            if player.name == "Start":
                self.player = Player((player.x, player.y), self.sprites, self.collision_sprites,
                                     self.tree_sprites, self.interactive_sprites, self.soil)
            # If it's a bed, create an interactive sprite, to change cycle of time
            if player.name == "Bed":
                InteractiveSprite((player.x, player.y), (player.width, player.height),
                                  self.interactive_sprites, player.name)
