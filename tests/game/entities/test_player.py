#!/usr/bin/env python
"""
Tests for the Player class
"""

import unittest
import pygame
import sys
import os

# Add the src directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.game.entities.player import Player

class TestPlayer(unittest.TestCase):
    """Test cases for the Player class"""

    def setUp(self):
        """Set up the test case"""
        pygame.init()
        self.player = Player(100, 100, "TestPlayer")

    def tearDown(self):
        """Clean up after the test case"""
        pygame.quit()

    def test_init(self):
        """Test player initialization"""
        self.assertEqual(self.player.name, "TestPlayer")
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.direction, "down")
        self.assertEqual(self.player.speed, 3)
        self.assertEqual(len(self.player.pokemon_team), 0)
        self.assertEqual(len(self.player.items), 0)

    def test_move(self):
        """Test player movement"""
        # Move right
        self.player.move(1, 0)
        self.assertEqual(self.player.x, 103)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.direction, "right")
        self.assertTrue(self.player.moving)

        # Move left
        self.player.move(-1, 0)
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.direction, "left")
        self.assertTrue(self.player.moving)

        # Move down
        self.player.move(0, 1)
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 103)
        self.assertEqual(self.player.direction, "down")
        self.assertTrue(self.player.moving)

        # Move up
        self.player.move(0, -1)
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.direction, "up")
        self.assertTrue(self.player.moving)

        # Stop moving
        self.player.move(0, 0)
        self.assertFalse(self.player.moving)

    def test_update(self):
        """Test player update"""
        # Start moving
        self.player.move(1, 0)
        self.assertTrue(self.player.moving)

        # Update with a time delta
        self.player.update(0.1)
        self.assertEqual(self.player.animation_timer, 0.1)
        self.assertEqual(self.player.current_frame, 0)

        # Update again to trigger frame change
        self.player.update(0.2)
        self.assertAlmostEqual(self.player.animation_timer, 0.1, places=5)  # Reset to 0 and added 0.1
        self.assertEqual(self.player.current_frame, 1)

        # Stop moving and update
        self.player.move(0, 0)
        self.assertFalse(self.player.moving)
        self.player.update(0.1)
        self.assertEqual(self.player.current_frame, 0)

    def test_add_pokemon(self):
        """Test adding Pokemon to the player's team"""
        # Create a mock Pokemon class
        class MockPokemon:
            def __init__(self, name):
                self.name = name

        # Add Pokemon to the team
        pokemon1 = MockPokemon("Pikachu")
        pokemon2 = MockPokemon("Charmander")

        self.assertTrue(self.player.add_pokemon(pokemon1))
        self.assertEqual(len(self.player.pokemon_team), 1)
        self.assertEqual(self.player.pokemon_team[0].name, "Pikachu")

        self.assertTrue(self.player.add_pokemon(pokemon2))
        self.assertEqual(len(self.player.pokemon_team), 2)
        self.assertEqual(self.player.pokemon_team[1].name, "Charmander")

        # Fill the team
        for i in range(4):
            self.player.add_pokemon(MockPokemon(f"Pokemon{i}"))

        # Try to add one more (should fail)
        pokemon7 = MockPokemon("Bulbasaur")
        self.assertFalse(self.player.add_pokemon(pokemon7))
        self.assertEqual(len(self.player.pokemon_team), 6)

    def test_items(self):
        """Test player items"""
        # Add items
        self.player.add_item("Potion", 3)
        self.assertEqual(self.player.items["Potion"], 3)

        self.player.add_item("Pokeball", 5)
        self.assertEqual(self.player.items["Pokeball"], 5)

        # Add more of an existing item
        self.player.add_item("Potion", 2)
        self.assertEqual(self.player.items["Potion"], 5)

        # Use items
        self.assertTrue(self.player.use_item("Potion"))
        self.assertEqual(self.player.items["Potion"], 4)

        # Use all of an item
        self.assertTrue(self.player.use_item("Potion"))
        self.assertTrue(self.player.use_item("Potion"))
        self.assertTrue(self.player.use_item("Potion"))
        self.assertTrue(self.player.use_item("Potion"))
        self.assertFalse("Potion" in self.player.items)

        # Try to use an item that doesn't exist
        self.assertFalse(self.player.use_item("Potion"))
        self.assertFalse(self.player.use_item("Revive"))

if __name__ == "__main__":
    unittest.main()
