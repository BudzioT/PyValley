import pygame
from pygame.math import Vector2 as Vector

from src.utilities import utilities
from src.settings import settings


class Player(pygame.sprite.Sprite):
    """Player of the game"""
    def __init__(self, pos, group):
        """Initialize the player"""
        super().__init__(group)

        # Get the player's assets
        self._load_assets()

        # Player's state
        self.state = "down_idle"

        # Current frame of animation
        self.frame = 0

        # Set his image to the current frame animation of state he's in
        self.image = self.frames[self.state][self.frame]

        # Get his rectangle, center him around given position
        self.rect = self.image.get_rect(center=pos)

        # Player's speed
        self.speed = 200

        # Player's direction
        self.direction = Vector()
        # Set his position
        self.pos = Vector(self.rect.center)

    def update(self, delta_time):
        """Update the player"""
        # Handle input
        self._handle_input()

        # Let the player move
        self._move(delta_time)

        # Animate him
        self._animate(delta_time)

    def _handle_input(self):
        """Check and handle the player's input"""
        # Get the keys pressed
        keys = pygame.key.get_pressed()

        # If player wants to move left, set his direction to the left
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1
            # Set the player's state to walking left
            self.state = "left"
        # Handle right movement and set the correct state
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1
            self.state = "right"
        # If player isn't pressing any horizontal keys, stay in place horizontally
        else:
            self.direction.x = 0

        # If user's presses up, change his direction to up
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
            # Set his state
            self.state = "up"
        # Handle down movement and state accordingly
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1
            self.state = "down"
        # If there isn't any vertical movement, make the player stay in place vertically
        else:
            self.direction.y = 0

    def _move(self, delta_time):
        """Move the player in given direction"""
        # If length of the vector is higher than 0, meaning player moves
        if self.direction.magnitude() > 0:
            # Normalize player's direction, to prevent speed up when moving in two directions at once
            self.direction = self.direction.normalize()

        # Set a new horizontal position
        self.pos.x += self.direction.x * self.speed * delta_time
        # Update player's horizontal rectangle position
        self.rect.centerx = self.pos.x

        # Move the player vertically
        self.pos.y += self.direction.y * self.speed * delta_time
        self.rect.centery = self.pos.y

    def _animate(self, delta_time):
        """Animate the player"""
        # Increase the current frame
        self.frame += settings.ANIMATION_SPEED * delta_time

        # Make sure the current frame is correct, otherwise set it back to 0
        if self.frame >= len(self.frames[self.state]):
            self.frame = 0

        # Set the new image based off the current frame
        self.image = self.frames[self.state][int(self.frame)]

    def _load_assets(self):
        """Load the player's assets"""
        # Prepare the dictionary with animations
        self.frames = { }
        # Go through each animation type
        for animation_type in ['', "_idle", "_hoe", "_axe", "_water"]:
            # Check and prepare empty list of animations for every direction of it
            for direction in ["up", "down", "left", "right"]:
                self.frames[direction + animation_type] = []

        # Go through all the animations that were prepared
        for animation in self.frames.keys():
            # Get the full path to a file
            full_path = "../graphics/character/" + animation
            # Save the animation frames in animations variable
            self.frames[animation] = utilities.load_folder(full_path)
