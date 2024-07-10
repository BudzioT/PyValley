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

        # Get the plain surface
        self.surface = utilities.load("../graphics/soil/o.png")
        # Get all the surfaces
        self.surfaces = utilities.load_folder_dict("../graphics/soil/")

        print(self.surfaces)

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
                    # Calculate position in pixels
                    pos_x = column_index * settings.TILE_SIZE
                    pos_y = row_index * settings.TILE_SIZE
                    # Create the soil tile
                    SoilTile((pos_x, pos_y), self.surface, [self.sprites, self.soil_sprites])


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
