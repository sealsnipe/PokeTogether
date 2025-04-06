#!/usr/bin/env python
"""
Camera class - Handles the game camera
"""

import pygame
import logging
from typing import Tuple, Any

class Camera:
    """Camera class for following the player and rendering the map"""

    def __init__(self, width: int, height: int, map_width: int, map_height: int, zoom_factor: float = 1.2):
        """Initialize the camera

        Args:
            width: Width of the camera view in pixels
            height: Height of the camera view in pixels
            map_width: Width of the map in pixels
            map_height: Height of the map in pixels
            zoom_factor: Zoom factor (> 1.0 means zoomed out, < 1.0 means zoomed in)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Creating camera with size {width}x{height}, map size {map_width}x{map_height}, zoom {zoom_factor}")

        # Zoom-Faktor anwenden (1.2 = 20% herausgezoomt)
        self.zoom_factor = zoom_factor

        # Effektive Kameragröße (vergrößert durch Zoom-Faktor)
        self.width = int(width * zoom_factor)
        self.height = int(height * zoom_factor)

        # Tatsächliche Bildschirmgröße
        self.screen_width = width
        self.screen_height = height

        self.map_width = map_width
        self.map_height = map_height
        self.x = 0
        self.y = 0

    def update(self, target_x: int, target_y: int):
        """Update the camera position to follow a target

        Args:
            target_x: Target x position
            target_y: Target y position
        """
        # Center the camera on the target
        self.x = target_x - self.width // 2
        self.y = target_y - self.height // 2

        # Keep the camera within the map bounds
        self.x = max(0, min(self.x, self.map_width - self.width))
        self.y = max(0, min(self.y, self.map_height - self.height))

    def apply(self, x: int, y: int) -> Tuple[int, int]:
        """Apply the camera offset to a position

        Args:
            x: X position
            y: Y position

        Returns:
            Tuple[int, int]: Position with camera offset applied
        """
        # Berechne die Position relativ zur Kamera
        rel_x = x - self.x
        rel_y = y - self.y

        # Skaliere die Position basierend auf dem Zoom-Faktor
        # und zentriere sie auf dem Bildschirm
        scaled_x = int(rel_x / self.zoom_factor) + (self.screen_width - int(self.width / self.zoom_factor)) // 2
        scaled_y = int(rel_y / self.zoom_factor) + (self.screen_height - int(self.height / self.zoom_factor)) // 2

        # Ausführliche Debug-Ausgabe für die Kamera-Transformation
        self.logger.info(f"[CAMERA] TRANSFORM: world=({x}, {y}), camera=({self.x}, {self.y}), rel=({rel_x}, {rel_y}), screen=({scaled_x}, {scaled_y})")
        self.logger.info(f"[CAMERA] DETAILS: zoom={self.zoom_factor}, screen_size=({self.screen_width}, {self.screen_height}), camera_size=({self.width}, {self.height})")

        return scaled_x, scaled_y

    def get_offset(self) -> Tuple[int, int]:
        """Get the camera offset

        Returns:
            Tuple[int, int]: Camera offset (x, y)
        """
        return self.x, self.y
