#!/usr/bin/env python
"""
Tilemap class - Represents a game map
"""

import pygame
import logging
import json
from typing import List, Dict, Tuple, Any, Optional

class Tilemap:
    """Tilemap class representing a game map"""
    
    def __init__(self, width: int = 20, height: int = 15, tile_size: int = 32):
        """Initialize the tilemap
        
        Args:
            width: Width of the map in tiles
            height: Height of the map in tiles
            tile_size: Size of each tile in pixels
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Creating tilemap with size {width}x{height}, tile size {tile_size}px")
        
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tileset = None
        self.tileset_width = 0
        self.tileset_height = 0
        
        # Layers
        self.ground_layer = [[0 for _ in range(width)] for _ in range(height)]
        self.object_layer = [[0 for _ in range(width)] for _ in range(height)]
        self.collision_layer = [[False for _ in range(width)] for _ in range(height)]
        
        # Map properties
        self.properties = {}
        
    def load_tileset(self, tileset_path: str, tile_width: int, tile_height: int):
        """Load the tileset image
        
        Args:
            tileset_path: Path to the tileset image
            tile_width: Width of each tile in the tileset
            tile_height: Height of each tile in the tileset
        """
        self.logger.info(f"Loading tileset from {tileset_path}")
        try:
            self.tileset = pygame.image.load(tileset_path).convert_alpha()
            self.tileset_width = self.tileset.get_width() // tile_width
            self.tileset_height = self.tileset.get_height() // tile_height
            self.logger.info(f"Tileset loaded successfully, {self.tileset_width}x{self.tileset_height} tiles")
        except pygame.error as e:
            self.logger.error(f"Error loading tileset: {e}")
            self.tileset = None
            
    def load_from_file(self, file_path: str):
        """Load the map from a JSON file
        
        Args:
            file_path: Path to the JSON file
        """
        self.logger.info(f"Loading map from {file_path}")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            self.width = data.get('width', self.width)
            self.height = data.get('height', self.height)
            self.tile_size = data.get('tileSize', self.tile_size)
            self.ground_layer = data.get('groundLayer', self.ground_layer)
            self.object_layer = data.get('objectLayer', self.object_layer)
            self.collision_layer = data.get('collisionLayer', self.collision_layer)
            self.properties = data.get('properties', {})
            
            self.logger.info(f"Map loaded successfully, size {self.width}x{self.height}")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Error loading map: {e}")
            
    def save_to_file(self, file_path: str):
        """Save the map to a JSON file
        
        Args:
            file_path: Path to the JSON file
        """
        self.logger.info(f"Saving map to {file_path}")
        data = {
            'width': self.width,
            'height': self.height,
            'tileSize': self.tile_size,
            'groundLayer': self.ground_layer,
            'objectLayer': self.object_layer,
            'collisionLayer': self.collision_layer,
            'properties': self.properties
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Map saved successfully to {file_path}")
        except IOError as e:
            self.logger.error(f"Error saving map: {e}")
            
    def set_tile(self, layer: str, x: int, y: int, tile_id: int):
        """Set a tile in the specified layer
        
        Args:
            layer: Layer name ('ground', 'object', 'collision')
            x: X coordinate
            y: Y coordinate
            tile_id: Tile ID to set
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            self.logger.warning(f"Attempted to set tile outside map bounds: ({x}, {y})")
            return
            
        if layer == 'ground':
            self.ground_layer[y][x] = tile_id
        elif layer == 'object':
            self.object_layer[y][x] = tile_id
        elif layer == 'collision':
            self.collision_layer[y][x] = bool(tile_id)
        else:
            self.logger.warning(f"Unknown layer: {layer}")
            
    def get_tile(self, layer: str, x: int, y: int) -> int:
        """Get a tile from the specified layer
        
        Args:
            layer: Layer name ('ground', 'object', 'collision')
            x: X coordinate
            y: Y coordinate
            
        Returns:
            int: Tile ID at the specified position
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            self.logger.warning(f"Attempted to get tile outside map bounds: ({x}, {y})")
            return 0
            
        if layer == 'ground':
            return self.ground_layer[y][x]
        elif layer == 'object':
            return self.object_layer[y][x]
        elif layer == 'collision':
            return 1 if self.collision_layer[y][x] else 0
        else:
            self.logger.warning(f"Unknown layer: {layer}")
            return 0
            
    def is_collision(self, x: int, y: int) -> bool:
        """Check if there is a collision at the specified position
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if there is a collision, False otherwise
        """
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return True  # Collision with map boundaries
            
        return self.collision_layer[tile_y][tile_x]
        
    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the map
        
        Args:
            screen: Pygame surface to render on
            camera_offset: Camera offset (x, y)
        """
        if not self.tileset:
            self.logger.warning("Attempted to render map without a tileset")
            return
            
        # Calculate visible area
        start_x = max(0, camera_offset[0] // self.tile_size)
        end_x = min(self.width, (camera_offset[0] + screen.get_width()) // self.tile_size + 1)
        start_y = max(0, camera_offset[1] // self.tile_size)
        end_y = min(self.height, (camera_offset[1] + screen.get_height()) // self.tile_size + 1)
        
        # Render ground layer
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.ground_layer[y][x]
                if tile_id > 0:
                    self._render_tile(screen, tile_id, x, y, camera_offset)
                    
        # Render object layer
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.object_layer[y][x]
                if tile_id > 0:
                    self._render_tile(screen, tile_id, x, y, camera_offset)
                    
    def _render_tile(self, screen: pygame.Surface, tile_id: int, x: int, y: int, camera_offset: Tuple[int, int]):
        """Render a single tile
        
        Args:
            screen: Pygame surface to render on
            tile_id: Tile ID to render
            x: X coordinate in tiles
            y: Y coordinate in tiles
            camera_offset: Camera offset (x, y)
        """
        # Calculate the position of the tile in the tileset
        tile_x = (tile_id - 1) % self.tileset_width
        tile_y = (tile_id - 1) // self.tileset_width
        
        # Calculate the position on the screen
        screen_x = x * self.tile_size - camera_offset[0]
        screen_y = y * self.tile_size - camera_offset[1]
        
        # Draw the tile
        screen.blit(
            self.tileset,
            (screen_x, screen_y),
            (tile_x * self.tile_size, tile_y * self.tile_size, self.tile_size, self.tile_size)
        )
