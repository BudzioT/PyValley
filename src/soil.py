import random
from os.path import join as path_join

import pygame
from pygame.math import Vector2 as Vector
from pytmx.util_pygame import load_pygame

from src.utilities import utilities
from src.settings import settings
from src.timer import Timer


class Soil:
    """Class that represents soil path"""

    def __init__(self, sprites, collision_sprites):
        """Initialize the soil"""
        # Get all the game's visible sprites
        self.sprites = sprites
        # Access the collision sprites
        self.collision_sprites = collision_sprites

        # Soil sprites
        self.soil_sprites = pygame.sprite.Group()
        # Watered soil sprites
        self.watered_soil_sprites = pygame.sprite.Group()
        # Plant sprites
        self.plant_sprites = pygame.sprite.Group()

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

                    # If it's raining, update the tile, to be watered
                    if self.rain_active:
                        self.water_all()

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

    def plant(self, seed, target):
        """Plant the specified seed at the target position"""
        # Search for a soil that is the target
        for soil in self.soil_sprites.sprites():
            if soil.rect.collidepoint(target):
                # Get the soil's position in tiles
                pos_x = soil.rect.x // settings.TILE_SIZE
                pos_y = soil.rect.y // settings.TILE_SIZE

                # If there isn't any plant at this tile, plant it
                if 'P' not in self.grid[pos_y][pos_x]:
                    # Append the plant flag to the soil
                    self.grid[pos_y][pos_x].append('P')
                    # Create a plant
                    Plant(seed, [self.sprites, self.plant_sprites, self.collision_sprites], soil,
                          self._watered, self._remove_plant)

    def update_plants(self):
        """Update plant stages"""
        for plant in self.plant_sprites:
            plant.grow()

    def check_plants(self, player_hitbox):
        """Check if plants are fine"""
        # Check every plant
        for plant in self.plant_sprites.sprites():
            # Update it
            plant.check(player_hitbox)

    def _remove_plant(self, pos):
        """Remove plant from specified position"""
        # Calculate tile position
        pos_x = pos[0] // settings.TILE_SIZE
        pos_y = pos[1] // settings.TILE_SIZE
        # Get soil at the calculated position
        soil = self.grid[pos_y][pos_x]

        # Remove the plant from the soil
        soil.remove('P')

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
                SoilWaterTile(pos, surface, [self.sprites, self.watered_soil_sprites])

    def water_all(self):
        """Water all the soil tiles"""
        # Go through each soil tile
        for row_index, row in enumerate(self.grid):
            for column_index, cell in enumerate(row):
                # If the soil is hit and isn't watered already, water it
                if 'H' in cell and 'W' not in cell:
                    # Set the watered flag
                    cell.append('W')
                    # Create the soil water tile
                    SoilWaterTile((column_index * settings.TILE_SIZE, row_index * settings.TILE_SIZE),
                                  random.choice(self.water_surfaces),
                                  [self.sprites, self.watered_soil_sprites])

    def remove_water(self):
        """Remove the water from soil tiles"""
        # Go through each of soil sprite and destroy it
        for water_sprite in self.watered_soil_sprites.sprites():
            water_sprite.kill()

        # Check the grid
        for row in self.grid:
            for cell in row:
                # If there is a watered tile, remove the water flag
                if 'W' in cell:
                    cell.remove('W')

    def _watered(self, pos):
        """Return if the soil from the given position is watered"""
        # Calculate position in tiles
        pos_x = pos[0] // settings.TILE_SIZE
        pos_y = pos[1] // settings.TILE_SIZE
        # Get soil at this position
        soil = self.grid[pos_y][pos_x]

        # Return if the soil has a watered flag
        return 'W' in soil

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


class Plant(pygame.sprite.Sprite):
    """Plant that can be planted on the soil"""
    def __init__(self, plant_type, group, soil, watered, remove_plant):
        """Initialize the plant"""
        super().__init__(group)

        # Save the plant type
        self.plant_type = plant_type
        # Save the soil that plant's on
        self.soil = soil

        # Harvestable flag
        self.harvestable = False

        # Depth position of it
        self.pos_z = settings.DEPTHS["plant"]

        # Import animation frames based off the type
        self.frames = utilities.load_folder(f"../graphics/fruit/{plant_type}")

        # Plant's growth stage
        self.stage = 0
        # Maximum stage (depending on the amount of frames)
        self.max_stage = len(self.frames) - 1
        # Its growth speed
        self.growth_speed = settings.GROW_SPEED[plant_type]

        # Plants position offset
        self.offset_y = -15 if plant_type == "corn" else - 7
        # Current plant's image
        self.image = self.frames[self.stage]
        # Get the rectangle the plant
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + Vector(0, self.offset_y))

        # Health of a plant depending on the type
        self.health = 1 if plant_type == "corn" else 2

        # Check if the soil is watered function
        self.watered = watered
        # Remove plant function
        self.remove_plant = remove_plant

        self.damage_cooldown = Timer(1000)

    def grow(self):
        """Grow the plant if conditions are true"""
        # Check if plant soil was watered
        if self.watered(self.rect.center):
            # If plant isn't yet ready for harvest
            if not self.harvestable:
                # Increase the stage of growth
                self.stage += self.growth_speed

                # If plant started to grow, change its depth
                if int(self.stage) > 0:
                    self.pos_z = settings.DEPTHS["main"]
                    # Set its hitboxes
                    self.hitbox = self.rect.copy().inflate(-25, -self.rect.height * 0.4)

                # If plant is already fully grown, don't grow it anymore
                if self.stage >= self.max_stage:
                    self.stage = self.max_stage
                    # Indicate that the plant is ready to harvest
                    self.harvestable = True

                # If there are still frames left
                if int(self.stage) <= len(self.frames) - 1:
                    # Try to get a new image depending on the stage, and update the rectangle
                    self.image = self.frames[int(self.stage)]
                    self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + Vector(0, self.offset_y))

    def check(self, player_hitbox):
        """Update the plant"""
        # If there isn't active cooldown
        if not self.damage_cooldown.active and not hasattr(self, "hitbox"):
            # Check if player stepped on non-grown plant
            if player_hitbox.hitbox.colliderect(self.rect):
                # Damage the plant
                self.health -= 1
                # Start the damage cooldown
                self.damage_cooldown.start()

                # If plant was stepped on too much, kill it
                if self.health == 0:
                    self.remove_plant(self.rect.center)
                    self.kill()
