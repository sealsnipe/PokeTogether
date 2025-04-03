#!/usr/bin/env python
"""
Tests for the Tilemap class
"""

import unittest
import pygame
import sys
import os
import tempfile
import json

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.game.maps.tilemap import Tilemap

class TestTilemap(unittest.TestCase):
    """Test cases for the Tilemap class"""
    
    def setUp(self):
        """Set up the test case"""
        pygame.init()
        self.tilemap = Tilemap(10, 8, 32)
        
    def tearDown(self):
        """Clean up after the test case"""
        pygame.quit()
        
    def test_init(self):
        """Test tilemap initialization"""
        self.assertEqual(self.tilemap.width, 10)
        self.assertEqual(self.tilemap.height, 8)
        self.assertEqual(self.tilemap.tile_size, 32)
        self.assertIsNone(self.tilemap.tileset)
        
        # Check layers
        self.assertEqual(len(self.tilemap.ground_layer), 8)
        self.assertEqual(len(self.tilemap.ground_layer[0]), 10)
        self.assertEqual(len(self.tilemap.object_layer), 8)
        self.assertEqual(len(self.tilemap.object_layer[0]), 10)
        self.assertEqual(len(self.tilemap.collision_layer), 8)
        self.assertEqual(len(self.tilemap.collision_layer[0]), 10)
        
        # Check that all tiles are initialized to 0 or False
        for y in range(8):
            for x in range(10):
                self.assertEqual(self.tilemap.ground_layer[y][x], 0)
                self.assertEqual(self.tilemap.object_layer[y][x], 0)
                self.assertFalse(self.tilemap.collision_layer[y][x])
                
    def test_set_get_tile(self):
        """Test setting and getting tiles"""
        # Set some tiles
        self.tilemap.set_tile("ground", 3, 4, 5)
        self.tilemap.set_tile("object", 2, 1, 7)
        self.tilemap.set_tile("collision", 5, 6, 1)
        
        # Get the tiles
        self.assertEqual(self.tilemap.get_tile("ground", 3, 4), 5)
        self.assertEqual(self.tilemap.get_tile("object", 2, 1), 7)
        self.assertEqual(self.tilemap.get_tile("collision", 5, 6), 1)
        
        # Check that other tiles are still 0 or False
        self.assertEqual(self.tilemap.get_tile("ground", 0, 0), 0)
        self.assertEqual(self.tilemap.get_tile("object", 0, 0), 0)
        self.assertEqual(self.tilemap.get_tile("collision", 0, 0), 0)
        
        # Test out of bounds
        self.tilemap.set_tile("ground", 20, 20, 5)  # Should not crash
        self.assertEqual(self.tilemap.get_tile("ground", 20, 20), 0)  # Should return 0
        
    def test_is_collision(self):
        """Test collision detection"""
        # Set some collision tiles
        self.tilemap.set_tile("collision", 2, 3, 1)
        self.tilemap.set_tile("collision", 5, 6, 1)
        
        # Check collision
        self.assertTrue(self.tilemap.is_collision(2 * 32 + 10, 3 * 32 + 10))
        self.assertTrue(self.tilemap.is_collision(5 * 32 + 10, 6 * 32 + 10))
        
        # Check no collision
        self.assertFalse(self.tilemap.is_collision(0, 0))
        self.assertFalse(self.tilemap.is_collision(1 * 32, 1 * 32))
        
        # Check out of bounds (should be collision)
        self.assertTrue(self.tilemap.is_collision(-10, -10))
        self.assertTrue(self.tilemap.is_collision(11 * 32, 9 * 32))
        
    def test_save_load(self):
        """Test saving and loading the map"""
        # Set some tiles
        self.tilemap.set_tile("ground", 3, 4, 5)
        self.tilemap.set_tile("object", 2, 1, 7)
        self.tilemap.set_tile("collision", 5, 6, 1)
        
        # Set some properties
        self.tilemap.properties = {
            "name": "Test Map",
            "music": "test_music.mp3"
        }
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_path = temp_file.name
            
        try:
            # Save the map
            self.tilemap.save_to_file(temp_path)
            
            # Create a new tilemap
            new_tilemap = Tilemap()
            
            # Load the map
            new_tilemap.load_from_file(temp_path)
            
            # Check that the map was loaded correctly
            self.assertEqual(new_tilemap.width, 10)
            self.assertEqual(new_tilemap.height, 8)
            self.assertEqual(new_tilemap.tile_size, 32)
            
            # Check that the tiles were loaded correctly
            self.assertEqual(new_tilemap.get_tile("ground", 3, 4), 5)
            self.assertEqual(new_tilemap.get_tile("object", 2, 1), 7)
            self.assertEqual(new_tilemap.get_tile("collision", 5, 6), 1)
            
            # Check that the properties were loaded correctly
            self.assertEqual(new_tilemap.properties["name"], "Test Map")
            self.assertEqual(new_tilemap.properties["music"], "test_music.mp3")
        finally:
            # Clean up
            os.unlink(temp_path)

if __name__ == "__main__":
    unittest.main()
