from os.path import join as path_join

import pygame
from pygame.math import Vector2 as Vector

from src.utilities import utilities
from src.settings import settings
from src.timer import Timer


class Player(pygame.sprite.Sprite):
    """Player of the game"""
    def __init__(self, pos, group, collision_sprites, tree_sprites, interactive_sprites, soil, activate_shop):
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
        # Player's hitboxes
        self.hitbox = self.rect.copy().inflate((-125, -70))

        # Player's speed
        self.speed = 200

        # Player's direction
        self.direction = Vector()
        # Set his position
        self.pos = Vector(self.rect.center)
        # Depth position of the player
        self.pos_z = settings.DEPTHS["main"]

        # List of sprites that player can collide with
        self.collision_sprites = collision_sprites
        # Sprites that player can interact with
        self.interactive_sprites = interactive_sprites
        # Get the trees
        self.tree_sprites = tree_sprites

        # Sleep flag
        self.sleep = False

        # List of available tools
        self.tools = ["axe", "hoe", "water"]
        # List of available seeds
        self.seeds = ["corn", "tomato"]

        # Current tool's index
        self.tool_index = 0
        # Seed one
        self.seed_index = 0

        # Current player's tool
        self.tool = self.tools[self.tool_index]
        # Current seed
        self.seed = self.seeds[self.seed_index]

        # Player's items
        self.items = {
            "wood": 0,
            "corn": 0,
            "tomato": 0,
            "apple": 0
        }

        # Player's current seeds
        self.current_seeds = {
            "corn": 5,
            "tomato": 4
        }

        # His money
        self.money = 10

        # Timers
        self.timers = {
            "tool": Timer(500, self._use_tool),
            "switch_tool": Timer(400),
            "seed": Timer(500, self._use_seed),
            "switch_seed": Timer(400)
        }

        # The soil ground
        self.soil = soil

        # Function to activate the shop
        self.activate_shop = activate_shop

        # Watering sound
        self.water_sound = pygame.mixer.Sound(path_join(settings.BASE_PATH, "../audio/water.mp3"))
        # Lower down the volume
        self.water_sound.set_volume(0.1)

        # Player's health
        self.health = 3

    def update(self, delta_time):
        """Update the player"""
        # Update timers
        self._update_timers()

        # Handle input
        self._handle_input()

        # Let the player move
        self._move(delta_time)

        # Update the target position of player's tool usage
        self._update_tool_target()

        # Set the player's state
        self._set_state()
        # Animate him
        self._animate(delta_time)

    def _handle_input(self):
        """Check and handle the player's input"""
        # Get the keys pressed
        keys = pygame.key.get_pressed()

        # If player isn't using a tool and isn't sleeping, allow for input
        if not self.timers["tool"].active and not self.sleep:
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

            # Use a seed on L, C or F
            if keys[pygame.K_l] or keys[pygame.K_c] or keys[pygame.K_f]:
                # Turn on the seed timer
                self.timers["seed"].start()
                # Stop the movement
                self.direction = Vector()

            # When user's pressing SPACE or K or X, use a tool
            if keys[pygame.K_SPACE] or keys[pygame.K_k] or keys[pygame.K_x]:
                # Activate the tool timer
                self.timers["tool"].start()

                # Stop the movement
                self.direction = Vector()
                # Reset the animation frame
                self.frame = 0

            # If the switch tool cooldown passed, allow switching tools
            if not self.timers["switch_tool"].active:
                # Change the tool forwards with E button
                if keys[pygame.K_e]:
                    self._change_tool(1)
                    # Activate the timer
                    self.timers["switch_tool"].start()

                # Change the tool backwards with Q button
                if keys[pygame.K_q]:
                    self._change_tool(-1)
                    # Start the switch cooldown
                    self.timers["switch_tool"].start()

            # If there isn't seed changing cooldown active, allow switching seeds
            if not self.timers["switch_seed"].active:
                # Change the seed with Left CTRL button
                if keys[pygame.K_LCTRL]:
                    self._change_seed(1)
                    # Start the seed switch cooldown
                    self.timers["switch_seed"].start()

            # If player presses RETURN (ENTER), try to go into interaction
            if keys[pygame.K_RETURN]:
                collided_sprites = pygame.sprite.spritecollide(self, self.interactive_sprites, False)
                # If there are any collisions, check with what sprite name
                if collided_sprites:
                    # If this is a trader, interact in trade
                    if collided_sprites[0].name == "Trader":
                        self.activate_shop()
                    # Otherwise it's a bed, run the new cycle
                    else:
                        # Go into left idle state, for nice look
                        self.state = "left_idle"
                        # Set player's sleep flag
                        self.sleep = True

                # If there isn't a Trader nearby, try to eat
                else:
                    # If player has at least two apples
                    if self.items["apple"] > 1:
                        # If player doesn't have already max health, eat them
                        if self.health < 3:
                            # Decrease the count of apples
                            self.items["apple"] -= 2

                            # Increase the health
                            self.health += 1

                    # Otherwise if player has a tomato, eat it
                    elif self.items["tomato"] > 0:
                        # Check if he doesn't have max health yet
                        if self.health < 3:
                            # Decrease the tomato count
                            self.items["tomato"] -= 1

                            # Increase his health
                            self.health += 1

    def _move(self, delta_time):
        """Move the player in given direction"""
        # If length of the vector is higher than 0, meaning player moves
        if self.direction.magnitude() > 0:
            # Normalize player's direction, to prevent speed up when moving in two directions at once
            self.direction = self.direction.normalize()

        # Set a new horizontal position
        self.pos.x += self.direction.x * self.speed * delta_time
        # Move the hitbox with the position
        self.hitbox.centerx = round(self.pos.x)
        # Update player's horizontal rectangle position
        self.rect.centerx = self.hitbox.centerx

        # Check horizontal collisions
        self._collisions("horizontal")

        # Move the player vertically
        self.pos.y += self.direction.y * self.speed * delta_time
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery

        # Check horizontal collisions
        self._collisions("vertical")

    def _update_timers(self):
        """Update all the player's timers"""
        # Go through all the timers and update them
        for timer in self.timers.values():
            timer.update()

    def _set_state(self):
        """Set the player's state"""
        # If player isn't moving (his direction's vector length is equal to 0)
        if self.direction.magnitude() == 0:
            # Set the state to current direction idle one
            self.state = self.state.split('_')[0] + "_idle"

        # If tool is being use (the tool timer's active)
        if self.timers["tool"].active:
            # Set the state to the given tool usage
            self.state = self.state.split('_')[0] + '_' + self.tool

    def _collisions(self, direction):
        """Check and handle collisions"""
        # Go through each collide-able sprite
        for sprite in self.collision_sprites.sprites():
            # If it has a hitbox, check for collisions
            if hasattr(sprite, "hitbox"):
                # If it collides with player, handle it
                if sprite.hitbox.colliderect(self.hitbox):
                    # Handle horizontal collisions
                    if direction == "horizontal":
                        # If player move's to the right, hug him to the left side of sprite
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        # Otherwise if he moves to the left, hug him to the right side
                        elif self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right

                        # Update the hitboxes and position
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    # If there are vertical collisions
                    elif direction == "vertical":
                        # Handle top collisions
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        # Handle bottom collisions
                        elif self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top

                        # Update the position and hitboxes
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def _update_tool_target(self):
        """Get the target position which the tool is used on"""
        self.target = self.rect.center + settings.TOOL_OFFSETS[self.state.split('_')[0]]

    def _use_tool(self):
        """Use a selected tool"""
        # If the currently used tool is an axe
        if self.tool == "axe":
            # Search through the tree sprites
            for tree in self.tree_sprites.sprites():
                # If player's tool collides with it, damage it
                if tree.rect.collidepoint(self.target):
                    tree.handle_damage()

        # If player is using a hoe, hit the soil if possible
        elif self.tool == "hoe":
            self.soil.handle_hit(self.target)

        # Otherwise, if player uses watering can, water the soil
        elif self.tool == "water":
            # Water the target if possible
            self.soil.water(self.target)

            # Play the watering sound
            self.water_sound.play()

    def _use_seed(self):
        """Use currently selected seed"""
        # if there is any seed left of the selected type
        if self.current_seeds[self.seed] > 0:
            # Plant it
            self.soil.plant(self.seed, self.target)

            # Decrease the current amount of it
            self.current_seeds[self.seed] -= 1

    def _change_tool(self, amount):
        """Change the tool index by the given amount"""
        # Change the tool index
        self.tool_index += amount

        # Make sure it's not too high, if it is, go back to index 0
        if self.tool_index >= len(self.tools):
            self.tool_index = 0
        # Also make sure it's not too low, if so, change it to the maximum index
        if self.tool_index < 0:
            self.tool_index = len(self.tools) - 1

        # Switch the tool
        self.tool = self.tools[self.tool_index]

    def _change_seed(self, amount):
        """Change the current seed by the given amount"""
        # Set the index
        self.seed_index += amount

        # Loop it around if needed
        if self.seed_index >= len(self.seeds):
            self.seed_index = 0

        # Switch the seed
        self.seed = self.seeds[self.seed_index]

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
