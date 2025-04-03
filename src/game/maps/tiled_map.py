#!/usr/bin/env python
"""
TiledMap class - Handles maps created with Tiled Map Editor
"""

import pygame
import pytmx
import logging
from typing import Dict, List, Tuple, Any, Optional
import os

class TiledMap:
    """Handles maps created with Tiled Map Editor"""
    
    def __init__(self):
        """Initialize the TiledMap"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating TiledMap")
        
        self.tmx_data = None
        self.width = 0
        self.height = 0
        self.tile_width = 0
        self.tile_height = 0
        self.pixel_width = 0
        self.pixel_height = 0
        self.properties = {}
        self.tilesets = {}
        
    def load(self, filename: str) -> bool:
        """Load a TMX file
        
        Args:
            filename: Path to the TMX file
            
        Returns:
            bool: True if the file was loaded successfully, False otherwise
        """
        self.logger.info(f"Loading TMX file: {filename}")
        
        if not os.path.exists(filename):
            self.logger.error(f"File not found: {filename}")
            return False
        
        try:
            self.tmx_data = pytmx.load_pygame(filename)
            self.width = self.tmx_data.width
            self.height = self.tmx_data.height
            self.tile_width = self.tmx_data.tilewidth
            self.tile_height = self.tmx_data.tileheight
            self.pixel_width = self.width * self.tile_width
            self.pixel_height = self.height * self.tile_height
            
            # Load map properties
            self.properties = dict(self.tmx_data.properties)
            
            # Load tilesets
            for tileset in self.tmx_data.tilesets:
                self.tilesets[tileset.name] = tileset
                
            self.logger.info(f"TMX file loaded successfully: {self.width}x{self.height} tiles, {self.tile_width}x{self.tile_height} pixels per tile")
            return True
        except Exception as e:
            self.logger.error(f"Error loading TMX file: {e}")
            return False
            
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the map
        
        Args:
            surface: Pygame surface to render on
            camera_offset: Camera offset (x, y)
        """
        if not self.tmx_data:
            self.logger.warning("Attempted to render map without loading TMX data")
            return
            
        # Calculate visible area
        start_x = max(0, camera_offset[0] // self.tile_width)
        end_x = min(self.width, (camera_offset[0] + surface.get_width()) // self.tile_width + 2)
        start_y = max(0, camera_offset[1] // self.tile_height)
        end_y = min(self.height, (camera_offset[1] + surface.get_height()) // self.tile_height + 2)
        
        # Render visible tiles for each layer
        for layer in self.tmx_data.visible_layers:
            # Skip object layers
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
                
            for x in range(int(start_x), int(end_x)):
                for y in range(int(start_y), int(end_y)):
                    tile = layer.data[y][x]
                    if tile:
                        # Get the tile image
                        image = self.tmx_data.get_tile_image(x, y, layer.id)
                        if image:
                            # Calculate the position on the screen
                            pos_x = x * self.tile_width - camera_offset[0]
                            pos_y = y * self.tile_height - camera_offset[1]
                            
                            # Draw the tile
                            surface.blit(image, (pos_x, pos_y))
                            
    def render_layer(self, surface: pygame.Surface, layer_name: str, camera_offset: Tuple[int, int] = (0, 0)):
        """Render a specific layer
        
        Args:
            surface: Pygame surface to render on
            layer_name: Name of the layer to render
            camera_offset: Camera offset (x, y)
        """
        if not self.tmx_data:
            self.logger.warning("Attempted to render layer without loading TMX data")
            return
            
        # Find the layer
        layer = None
        for l in self.tmx_data.visible_layers:
            if hasattr(l, 'name') and l.name == layer_name:
                layer = l
                break
                
        if not layer:
            self.logger.warning(f"Layer not found: {layer_name}")
            return
            
        # Skip object layers
        if not isinstance(layer, pytmx.TiledTileLayer):
            return
            
        # Calculate visible area
        start_x = max(0, camera_offset[0] // self.tile_width)
        end_x = min(self.width, (camera_offset[0] + surface.get_width()) // self.tile_width + 2)
        start_y = max(0, camera_offset[1] // self.tile_height)
        end_y = min(self.height, (camera_offset[1] + surface.get_height()) // self.tile_height + 2)
        
        # Render visible tiles
        for x in range(int(start_x), int(end_x)):
            for y in range(int(start_y), int(end_y)):
                tile = layer.data[y][x]
                if tile:
                    # Get the tile image
                    image = self.tmx_data.get_tile_image(x, y, layer.id)
                    if image:
                        # Calculate the position on the screen
                        pos_x = x * self.tile_width - camera_offset[0]
                        pos_y = y * self.tile_height - camera_offset[1]
                        
                        # Draw the tile
                        surface.blit(image, (pos_x, pos_y))
                        
    def is_collision(self, x: int, y: int) -> bool:
        """Check if there is a collision at the specified position
        
        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels
            
        Returns:
            bool: True if there is a collision, False otherwise
        """
        if not self.tmx_data:
            self.logger.warning("Attempted to check collision without loading TMX data")
            return False
            
        # Convert pixel coordinates to tile coordinates
        tile_x = x // self.tile_width
        tile_y = y // self.tile_height
        
        # Check if the coordinates are within the map bounds
        if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
            return True  # Collision with map boundaries
            
        # Check collision layers
        for layer in self.tmx_data.visible_layers:
            # Skip non-tile layers
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
                
            # Check if this is a collision layer
            if hasattr(layer, 'properties') and layer.properties.get('collision', False):
                tile = layer.data[tile_y][tile_x]
                if tile:
                    return True  # Collision with a tile in a collision layer
                    
        # Check object layers for collision objects
        for obj in self.tmx_data.objects:
            if hasattr(obj, 'properties') and obj.properties.get('collision', False):
                # Check if the point is inside the object
                if obj.x <= x < obj.x + obj.width and obj.y <= y < obj.y + obj.height:
                    return True  # Collision with an object
                    
        return False  # No collision
        
    def get_objects(self, layer_name: str = None) -> List[Any]:
        """Get all objects or objects from a specific layer
        
        Args:
            layer_name: Name of the layer to get objects from, or None to get all objects
            
        Returns:
            List[Any]: List of objects
        """
        if not self.tmx_data:
            self.logger.warning("Attempted to get objects without loading TMX data")
            return []
            
        if layer_name:
            # Get objects from a specific layer
            return [obj for obj in self.tmx_data.objects if hasattr(obj, 'parent') and obj.parent.name == layer_name]
        else:
            # Get all objects
            return list(self.tmx_data.objects)
            
    def get_object_by_name(self, name: str) -> Optional[Any]:
        """Get an object by its name
        
        Args:
            name: Name of the object
            
        Returns:
            Optional[Any]: The object, or None if not found
        """
        if not self.tmx_data:
            self.logger.warning("Attempted to get object without loading TMX data")
            return None
            
        for obj in self.tmx_data.objects:
            if hasattr(obj, 'name') and obj.name == name:
                return obj
                
        return None
        
    def get_object_by_id(self, obj_id: int) -> Optional[Any]:
        """Get an object by its ID
        
        Args:
            obj_id: ID of the object
            
        Returns:
            Optional[Any]: The object, or None if not found
        """
        if not self.tmx_data:
            self.logger.warning("Attempted to get object without loading TMX data")
            return None
            
        for obj in self.tmx_data.objects:
            if hasattr(obj, 'id') and obj.id == obj_id:
                return obj
                
        return None
        
    def get_tile_properties(self, x: int, y: int, layer: int) -> Dict[str, Any]:
        """Get the properties of a tile
        
        Args:
            x: X coordinate in tiles
            y: Y coordinate in tiles
            layer: Layer ID
            
        Returns:
            Dict[str, Any]: Tile properties
        """
        if not self.tmx_data:
            self.logger.warning("Attempted to get tile properties without loading TMX data")
            return {}
            
        # Check if the coordinates are within the map bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return {}
            
        # Get the tile
        tile = self.tmx_data.get_tile_properties(x, y, layer)
        if tile:
            return dict(tile)
        else:
            return {}
