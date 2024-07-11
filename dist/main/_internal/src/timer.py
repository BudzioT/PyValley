import pygame


class Timer:
    """Timer that calls given function after set amount of time"""
    def __init__(self, duration, func=None):
        """Create the timer"""
        # Timer's duration
        self.duration = duration

        # Function to call
        self.func = func

        # Time that the timer started
        self.start_time = 0
        # Active flag
        self.active = False

    def start(self):
        """Start the timer"""
        # Set the flag
        self.active = True
        # Save the start time
        self.start_time = pygame.time.get_ticks()

    def stop(self):
        """Stop the timer"""
        # Reset the active flag
        self.active = False
        # Set start time back to 0
        self.start_time = 0

    def update(self):
        """Update the timer"""
        # Get the current time
        current_time = pygame.time.get_ticks()

        # If duration from the start time passed
        if current_time - self.start_time >= self.duration:
            # If there was a given function and the timer started, call it
            if self.func and self.start_time != 0:
                self.func()

            # Deactivate the timer
            self.stop()
