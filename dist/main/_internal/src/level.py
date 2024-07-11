import random
import sys
from os.path import join as path_join

import pygame
from pytmx.util_pygame import load_pygame

from src.player import Player
from src.ui import UI
from src.groups import CameraGroup
from src.sprites import Sprite, Water, Flower, Tree, InteractiveSprite, Particle
from src.utilities import utilities
from src.settings import settings
from src.transition import Transition
from src.soil import Soil
from src.weather import Rain
from src.sky import Sky
from src.menu import Menu


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
        self.soil = Soil(self.sprites, self.collision_sprites)

        # Set up the level
        self._initialize()

        # Day-skip transition
        self.transition = Transition(self._reset_day, self.player)

        # Rain weather
        self.rain = Rain(self.sprites)

        # Rain flag
        self.rain_active = random.randint(0, 10) > 6
        # Update the soil's flag
        self.soil.rain_active = self.rain_active

        # Game's sky
        self.sky = Sky()

        # Water all the existing tiles if it's raining
        if self.rain_active:
            self.soil.water_all()

        # Shop open flag
        self.shop = False

        # Menu
        self.menu = Menu(self.player, self._activate_shop)

        # Game's user's interface
        self.ui = UI(self.player)

        # Obtaining item sound
        self.obtain_sound = pygame.mixer.Sound(path_join(settings.BASE_PATH, "../audio/success.wav"))
        # Lower its volume
        self.obtain_sound.set_volume(0.2)

        # Background music
        self.music = pygame.mixer.Sound(path_join(settings.BASE_PATH, "../audio/music.mp3"))
        # Set its volume
        self.music.set_volume(0.2)
        # Play it in loops
        self.music.play(-1)

    def run(self, delta_time):
        """Run the level"""
        # Update the surface
        self._update_surface(delta_time)

        # Update elements positions
        self._update_positions(delta_time)

    def _update_surface(self, delta_time):
        """Update the level's surface, draw the elements"""
        # Fill the surface with a color
        self.surface.fill("gray")

        # Draw all the sprites
        self.sprites.custom_draw(self.player)

        # Draw the user's interface
        self.ui.display(delta_time)

    def _update_positions(self, delta_time):
        """Update positions of level's elements"""
        # If shop is open, update and show the menu
        if self.shop:
            self.menu.update()
        # Otherwise update the sprites that aren't active in the menu
        else:
            # Update all sprites
            self.sprites.update(delta_time)

            # Check the plants condition
            self.soil.check_plants(self.player)
            # Check collisions with them
            self._plant_collision()

            # If it's raining, update the rain weather
            if self.rain_active:
                self.rain.update()

            # If player sleeps, run the day skip transition
            if self.player.sleep:
                self.transition.display()

        # Display the daytime sky
        self.sky.display(delta_time)

    def _check_game_over(self):
        """Check and handle game over"""
        # If player doesn't have any health left, exit the game
        if self.player.health <= 0:
            pygame.quit()
            sys.exit()

    def _obtain_item(self, item):
        """Obtain one more of the given item"""
        # Obtain it
        self.player.items[item] += 1

        # Play the sound
        self.obtain_sound.play()

    def _reset_day(self):
        """Reset everything that happens in a one-day cycle"""
        # Update amount of hearts
        self.ui.create_hearts(self.player.health)

        # Destroy apples from every tree on the map
        for tree in self.tree_sprites.sprites():
            # Destroy apples
            tree.destroy_apples()
            # Create new ones
            tree.create_apples()

        # Grow the plants
        self.soil.update_plants()

        # Decrease the player's health
        self.player.health -= 1

        # Check game over
        self._check_game_over()

        # Remove water from the soil
        self.soil.remove_water()

        # Set the weather to raining randomly
        self.rain_active = random.randint(0, 10) > 6
        # Update the soil's raining flag
        self.soil.rain_active = self.rain_active

        # Reset the sky color
        self.sky.start_color = [255, 255, 255]

    def _plant_collision(self):
        """Check and handle collisions with plants"""
        # Check if there are any plants
        if self.soil.plant_sprites:
            # If there are, check every one of them
            for plant in self.soil.plant_sprites.sprites():
                # If it's harvestable and collides with player, remove it
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    # Add plant harvests to the player's items
                    self._obtain_item(plant.plant_type)

                    # Remove it from the soil
                    plant.remove_plant(plant.rect.center)
                    # Destroy the plant
                    plant.kill()

                    # Make a particle
                    Particle(plant.rect.topleft, plant.image, self.sprites, settings.DEPTHS["main"])

    def _activate_shop(self):
        """Activate Trader's shop"""
        # Switch on or off the shop flag
        self.shop = not self.shop

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
                                     self.tree_sprites, self.interactive_sprites, self.soil, self._activate_shop)
            # If it's a bed, create an interactive sprite, to change cycle of time
            if player.name == "Bed":
                InteractiveSprite((player.x, player.y), (player.width, player.height),
                                  self.interactive_sprites, player.name)
            # On condition that it's a trader, place him as an interactive sprite
            if player.name == "Trader":
                InteractiveSprite((player.x, player.y), (player.width, player.height),
                                  self.interactive_sprites, player.name)
