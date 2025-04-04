#!/usr/bin/env python
"""
Player class - Represents the player character
"""

import pygame
import logging
from typing import Tuple

class Player:
    """Player class representing the main character"""

    def __init__(self, x: int = 0, y: int = 0, name: str = "Red"):
        """Initialize the player

        Args:
            x: Initial x position
            y: Initial y position
            name: Player name
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Creating player '{name}' at position ({x}, {y})")

        self.name = name
        self.x = x
        self.y = y
        self.direction = "down"  # down, up, left, right
        self.speed = 3
        self.sprite_sheet = None
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.moving = False
        self.pokemon_team = []
        self.items = {}

    def load_sprites(self, sprite_sheet_path: str):
        """Load player sprites

        Args:
            sprite_sheet_path: Path to the sprite sheet image
        """
        self.logger.info(f"Loading player sprites from {sprite_sheet_path}")
        try:
            self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            self.logger.info("Player sprites loaded successfully")
        except pygame.error as e:
            self.logger.error(f"Error loading player sprites: {e}")
            # Fallback to a simple rectangle
            self.sprite_sheet = None

    def move(self, dx: int, dy: int, speed_multiplier: float = 1.0):
        """Move the player

        Args:
            dx: Change in x position
            dy: Change in y position
            speed_multiplier: Multiplier for the player's speed (default: 1.0)
        """
        # Debug-Logging für Bewegungseingaben
        if dx != 0 or dy != 0:
            self.logger.debug(f"Bewegungseingabe: dx={dx}, dy={dy}, speed_multiplier={speed_multiplier}")

        # Richtung basierend auf Bewegung setzen
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        # Position aktualisieren
        old_x, old_y = self.x, self.y
        self.x += dx * self.speed * speed_multiplier
        self.y += dy * self.speed * speed_multiplier

        # Bewegungsstatus aktualisieren
        self.moving = dx != 0 or dy != 0

        # Debug-Logging für tatsächliche Bewegung
        if old_x != self.x or old_y != self.y:
            self.logger.debug(f"Bewegung: ({old_x}, {old_y}) -> ({self.x}, {self.y})")

    def update(self, dt: float):
        """Update the player

        Args:
            dt: Time delta since last update
        """
        # Update animation
        if self.moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = self.animation_timer - self.animation_speed
                self.current_frame = (self.current_frame + 1) % 4
        else:
            self.current_frame = 0

    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the player

        Args:
            screen: Pygame surface to render on
            camera_offset: Camera offset (x, y)
        """
        x = self.x - camera_offset[0]
        y = self.y - camera_offset[1]

        if self.sprite_sheet:
            # Calculate the position in the sprite sheet based on direction and frame
            direction_idx = {"down": 0, "left": 1, "right": 2, "up": 3}
            sprite_x = self.current_frame * 32
            sprite_y = direction_idx[self.direction] * 32

            # Draw the sprite
            screen.blit(self.sprite_sheet, (x, y), (sprite_x, sprite_y, 32, 32))
        else:
            # Fallback: draw a simple rectangle
            pygame.draw.rect(screen, (255, 0, 0), (x, y, 32, 32))

    def add_pokemon(self, pokemon):
        """Add a Pokemon to the player's team

        Args:
            pokemon: Pokemon object to add

        Returns:
            bool: True if the Pokemon was added, False if the team is full
        """
        if len(self.pokemon_team) < 6:
            self.pokemon_team.append(pokemon)
            self.logger.info(f"Added {pokemon.name} to {self.name}'s team")
            return True
        else:
            self.logger.info(f"Could not add {pokemon.name} to {self.name}'s team - team is full")
            return False

    def add_item(self, item_name: str, quantity: int = 1):
        """Add an item to the player's inventory

        Args:
            item_name: Name of the item
            quantity: Quantity to add
        """
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity

        self.logger.info(f"Added {quantity} {item_name} to {self.name}'s inventory")

    def use_item(self, item_name: str) -> bool:
        """Use an item from the player's inventory

        Args:
            item_name: Name of the item to use

        Returns:
            bool: True if the item was used, False if the player doesn't have the item
        """
        if item_name in self.items and self.items[item_name] > 0:
            self.items[item_name] -= 1
            if self.items[item_name] == 0:
                del self.items[item_name]

            self.logger.info(f"{self.name} used {item_name}")
            return True
        else:
            self.logger.info(f"{self.name} tried to use {item_name} but doesn't have any")
            return False
