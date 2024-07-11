import random
from os.path import join as path_join

import pygame
from pytmx.util_pygame import load_pygame

from src.utilities import utilities
from src.settings import settings


class Soil:
    """Class that represents soil path"""

    def __init__(self, sprites):
        """Initialize the soil"""
        # Get all the game's visible sprites
        self.sprites = sprites
        # Soil sprites
        self.soil_sprites = pygame.sprite.Group()
        # Watered soil sprites
        self.watered_soil_sprites = pygame.sprite.Group()

        # Get all the surfaces
        self.surfaces = utilities.load_folder_dict("../graphics/soil/")
        self.water_surfaces = utilities.load_folder("../graphics/soil_water")

        # Create the grid
        self._create_grid()
        # Create farmable rectangles based off the grid
        self._create_farmable_rects()

    def _create_grid(self):
        """Create a grid of soil"""
        # Get map's surface to get the size
        map_surface = utilities.load("../graphics/world/ground.png")
        # Dimensions of the map in tiles
        width = map_surface.get_width() // settings.TILE_SIZE
        height = map_surface.get_height() // settings.TILE_SIZE

        # Create the map grid list (list of rows with empty list of columns)
        self.grid = [[[] for column in range(width)] for row in range(height)]

        # Set which grid tiles are farmable by going through the map
        for pos_x, pos_y, surface in (load_pygame(path_join(settings.BASE_PATH,
                                      "../data/map.tmx")).get_layer_by_name("Farmable").tiles()):
            # Set the tile as farmable, by appending 'x' to indicate that
            self.grid[pos_y][pos_x].append('x')

    def _create_farmable_rects(self):
        """Create a list of farmable tile rectangles"""
        # Prepare the list
        self.farmable_rects = []

        # Go through each row in the grid
        for row_index, row in enumerate(self.grid):
            # Check every column
            for column_index, cell in enumerate(row):
                # If the cell is farmable, append it
                if 'x' in cell:
                    # Calculate its position in pixels
                    pos_x = column_index * settings.TILE_SIZE
                    pos_y = row_index * settings.TILE_SIZE
                    # Create a rectangle with that position
                    rect = pygame.Rect(pos_x, pos_y, settings.TILE_SIZE, settings.TILE_SIZE)

                    # Append it to the list
                    self.farmable_rects.append(rect)

    def handle_hit(self, point):
        """Handle farmable tile getting hit"""
        # Go through each farmable rectangle, check if it collides with given point
        for rect in self.farmable_rects:
            if rect.collidepoint(point):
                # Calculate the position in tiles
                pos_x = rect.x // settings.TILE_SIZE
                pos_y = rect.y // settings.TILE_SIZE

                # Check if the hit point is still farmable
                if 'x' in self.grid[pos_y][pos_x]:
                    # Change the tile into hit one
                    self.grid[pos_y][pos_x].append("H")
                    # Create soil tile in place
                    self._create_soil_tiles()

    def _create_soil_tiles(self):
        """Create soil tiles in places where the player hit with a hoe"""
        # Clean the current soil sprites
        self.soil_sprites.empty()

        # Check every row and column in the grid
        for row_index, row in enumerate(self.grid):
            for column_index, cell in enumerate(row):
                # If cell was hit
                if 'H' in cell:
                    soil_type = self._get_soil_type(row_index, row, column_index)
                    
                    # Calculate position in pixels
                    pos_x = column_index * settings.TILE_SIZE
                    pos_y = row_index * settings.TILE_SIZE
                    # Create the soil tile
                    SoilTile((pos_x, pos_y), self.surfaces[soil_type],
                             [self.sprites, self.soil_sprites])

    def water(self, target):
        """Water the soil in the given position"""
        # Go through each of the soil tiles, check which one is the target
        for soil in self.soil_sprites.sprites():
            if soil.rect.collidepoint(target):
                # Get the position in tiles
                pos_x = soil.rect.x // settings.TILE_SIZE
                pos_y = soil.rect.y // settings.TILE_SIZE
                # Mark the soil as watered
                self.grid[pos_y][pos_x].append("W")

                # Get position from the soil
                pos = soil.rect.topleft
                # Set a random surface
                surface = random.choice(self.water_surfaces)

                # Create the soil water tile
                SoilWaterTile(pos, surface, )

    def _get_soil_type(self, row_index, row, column_index):
        """Get the type of soil to place depending on the near hit farmable tiles"""
        # Get the near hit tiles
        top = 'H' in self.grid[row_index - 1][column_index]
        bottom = 'H' in self.grid[row_index + 1][column_index]
        left = 'H' in row[column_index - 1]
        right = 'H' in row[column_index + 1]

        # Current soil type
        soil_type = 'o'

        # If all sides are hit, place the all type of soil
        if all((top, bottom, left, right)):
            soil_type = 'x'

        # Check vertical types
        # If there is hit tile at top, draw the bottom type
        elif not any((bottom, left, right)) and top:
            soil_type = 'b'
        # Only bottom - top type
        elif not any((top, left, right)) and bottom:
            soil_type = 't'
        # Top and bottom type
        elif not any((left, right)) and all((top, bottom)):
            soil_type = 'tb'

        # Check horizontal tiles
        # If there is only tile on left, set the right type
        elif not any((top, bottom, right)) and left:
            soil_type = 'r'
        # Only right - left type
        elif not any((top, bottom, left)) and right:
            soil_type = 'l'
        # Left and right
        elif not any((top, bottom)) and any((left, right)):
            soil_type = 'lr'

        # Check corners
        # Left and bottom - top right corner type
        elif not any((top, right)) and any((left, bottom)):
            soil_type = 'tr'
        # Right and bottom - top left
        elif not any((top, left)) and any((right, bottom)):
            soil_type = 'tl'
        # Left and top - bottom right
        elif not any((bottom, right)) and any((left, top)):
            soil_type = 'br'
        # Right and top - bottom left
        elif not any((bottom, left)) and any((right, top)):
            soil_type = 'bl'

        # Check T-shapes
        # All besides left - top bottom right type
        elif not left and any((top, bottom, right)):
            soil_type = "tbr"
        # All besides right - top bottom left
        elif not right and any((top, bottom, left)):
            soil_type = "tbl"
        # All besides top - left right top
        elif not top and any((bottom, left, right)):
            soil_type = "lrt"
        # All besides bottom - left right bottom type
        elif not bottom and any((top, left, right)):
            soil_type = "lrb"

        # Return the soil type
        return soil_type


class SoilTile(pygame.sprite.Sprite):
    """A single soil tile"""
    def __init__(self, pos, surface, group):
        """Initialize the soil tile"""
        super().__init__(group)

        # Get the image and its rectangle, place it in the correct position
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)

        # Set the depth position as soil value
        self.pos_z = settings.DEPTHS["soil"]


class SoilWaterTile(pygame.sprite.Sprite):
    """Tile of soil that has been watered"""
    def __init__(self, pos, surface, group):
        """Initialize the watered soil"""
        super().__init__(group)

        # Set the image and its rectangle, place it correctly
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)

        # Set the depth position
        self.pos_z = settings.DEPTHS["soil_water"]
