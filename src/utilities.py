import os
from os.path import join as path_join

import pygame

from src.settings import settings


class Utilities:
    """Class that gives utilities"""
    def __init__(self):
        """Create utilities"""
        # Save the absolute base file path
        self.BASE_PATH = settings.BASE_PATH

    def load_folder(self, path):
        """Load an entire folder from the given path"""
        surfaces = []

        # Go through each entry in the given path (convert path join to string, path walk requires it)
        for folder_path, subfolders, images in os.walk(str(path_join(self.BASE_PATH, path))):
            # Check every image in the found images
            for image in images:
                # Save the path to the specific image
                full_path = path + '/' + image

                # Load the image
                image_surface = pygame.image.load(os.path.join(self.BASE_PATH, full_path))
                # Append it to the list
                surfaces.append(image_surface)
        # Return the loaded images
        return surfaces


# Create an instance of utilities
utilities = Utilities()