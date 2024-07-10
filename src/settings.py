import os


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


# Instantiate settings
settings = Settings()
