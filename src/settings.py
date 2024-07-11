import os

from pygame.math import Vector2 as Vector


class Settings:
    """Settings of the game"""
    def __init__(self):
        """Create the settings"""
        # Screen dimensions
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720

        # Size of one tile
        self.TILE_SIZE = 64

        # Animation speed
        self.ANIMATION_SPEED = 4

        # File's base path
        self.BASE_PATH = os.path.dirname(os.path.abspath(__file__))

        # User's interface icon positions
        self.ICON_POSITIONS = {
            "tool": (40, self.SCREEN_HEIGHT - 15),
            "seed": (90, self.SCREEN_HEIGHT)
        }

        # Depth of layers
        self.DEPTHS = {
            "water": 0,
            "ground": 1,
            "soil": 2,
            "soil_water": 3,
            "rain_floor": 4,
            "house_bottom": 5,
            "plant": 6,
            "main": 7,
            "house_top": 8,
            "fruit": 9,
            "rain_drops": 10
        }

        self.APPLE_POS = {
            "Small": [(18, 17), (30, 37), (12, 50), (30, 45), (20, 30), (30, 10)],
            "Large": [(30, 24), (60, 65), (50, 50), (16, 40), (45, 50), (42, 70)]
        }

        self.TOOL_OFFSETS = {
            "up": Vector(0, -10),
            "down": Vector(0, 50),
            "left": Vector(-50, 40),
            "right": Vector(50, 40)
        }

        self.GROW_SPEED = {
            "corn": 0.8,
            "tomato": 0.6
        }


# Instantiate settings
settings = Settings()
