#!/usr/bin/env python
"""
SimpleMap class - A simple map implementation for testing
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any, Optional

class SimpleMap:
    """A simple map implementation for testing"""

    def __init__(self, width: int = 20, height: int = 18, tile_size: int = 16):
        """Initialize the simple map

        Args:
            width: Width of the map in tiles
            height: Height of the map in tiles
            tile_size: Size of each tile in pixels
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Creating simple map with size {width}x{height}, tile size {tile_size}px")

        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.pixel_width = width * tile_size
        self.pixel_height = height * tile_size

        # Create a simple map with grass and paths
        self.ground_layer = self._create_ground_layer()
        self.object_layer = self._create_object_layer()
        self.collision_layer = self._create_collision_layer()

        # Create simple tiles
        self.tiles = {
            'grass': (0, 200, 0),
            'path': (200, 200, 100),
            'water': (0, 0, 200),
            'house': (200, 0, 0),
            'tree': (0, 100, 0),
            'player': (255, 255, 0)
        }

    def _create_ground_layer(self) -> List[List[str]]:
        """Create a simple ground layer

        Returns:
            List[List[str]]: The ground layer
        """
        # Create a map filled with grass
        layer = [['grass' for _ in range(self.width)] for _ in range(self.height)]

        # Add a path
        for x in range(5, 15):
            layer[10][x] = 'path'

        for y in range(5, 15):
            layer[y][10] = 'path'

        # Add water
        for x in range(2, 5):
            for y in range(2, 5):
                layer[y][x] = 'water'

        return layer

    def _create_object_layer(self) -> List[List[str]]:
        """Create a simple object layer

        Returns:
            List[List[str]]: The object layer
        """
        # Create an empty object layer
        layer = [['' for _ in range(self.width)] for _ in range(self.height)]

        # Add houses
        layer[5][5] = 'house'
        layer[5][15] = 'house'
        layer[15][10] = 'house'

        # Add trees
        for x in range(0, self.width, 5):
            layer[0][x] = 'tree'
            layer[self.height - 1][x] = 'tree'

        for y in range(0, self.height, 5):
            layer[y][0] = 'tree'
            layer[y][self.width - 1] = 'tree'

        return layer

    def _create_collision_layer(self) -> List[List[bool]]:
        """Create a simple collision layer

        Returns:
            List[List[bool]]: The collision layer
        """
        # Create a collision layer based on the object layer
        layer = [[False for _ in range(self.width)] for _ in range(self.height)]

        # Add collisions for houses and trees
        for y in range(self.height):
            for x in range(self.width):
                if self.object_layer[y][x] in ['house', 'tree']:
                    layer[y][x] = True

        # Add collisions for water
        for y in range(self.height):
            for x in range(self.width):
                if self.ground_layer[y][x] == 'water':
                    layer[y][x] = True

        # Add collisions for map boundaries
        for x in range(self.width):
            layer[0][x] = True
            layer[self.height - 1][x] = True

        for y in range(self.height):
            layer[y][0] = True
            layer[y][self.width - 1] = True

        return layer

    def is_collision(self, x: int, y: int) -> bool:
        """Check if there is a collision at the specified position

        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels

        Returns:
            bool: True if there is a collision, False otherwise
        """
        # Convert pixel coordinates to tile coordinates
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)

        # Check if the coordinates are within the map bounds
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return True  # Collision with map boundaries

        # Check collision layer
        return self.collision_layer[tile_y][tile_x]

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the map

        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset (x, y)
        """
        # Calculate visible area
        start_x = max(0, camera_offset[0] // self.tile_size)
        end_x = min(self.width, (camera_offset[0] + surface.get_width()) // self.tile_size + 1)
        start_y = max(0, camera_offset[1] // self.tile_size)
        end_y = min(self.height, (camera_offset[1] + surface.get_height()) // self.tile_size + 1)

        # Render ground layer
        for y in range(int(start_y), int(end_y)):
            for x in range(int(start_x), int(end_x)):
                tile_type = self.ground_layer[y][x]
                if tile_type:
                    color = self.tiles.get(tile_type, (0, 0, 0))
                    rect = pygame.Rect(
                        x * self.tile_size - camera_offset[0],
                        y * self.tile_size - camera_offset[1],
                        self.tile_size,
                        self.tile_size
                    )
                    pygame.draw.rect(surface, color, rect)

        # Render object layer
        for y in range(int(start_y), int(end_y)):
            for x in range(int(start_x), int(end_x)):
                tile_type = self.object_layer[y][x]
                if tile_type:
                    color = self.tiles.get(tile_type, (0, 0, 0))
                    rect = pygame.Rect(
                        x * self.tile_size - camera_offset[0],
                        y * self.tile_size - camera_offset[1],
                        self.tile_size,
                        self.tile_size
                    )
                    pygame.draw.rect(surface, color, rect)

        # Debug: Render collision layer
        for y in range(int(start_y), int(end_y)):
            for x in range(int(start_x), int(end_x)):
                if self.collision_layer[y][x]:
                    rect = pygame.Rect(
                        x * self.tile_size - camera_offset[0],
                        y * self.tile_size - camera_offset[1],
                        self.tile_size,
                        self.tile_size
                    )
                    pygame.draw.rect(surface, (255, 0, 0, 128), rect, 1)
