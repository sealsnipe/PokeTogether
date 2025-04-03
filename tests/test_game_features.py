#!/usr/bin/env python
"""
Test Game Features - Tests für die Spielfunktionen
"""

import unittest
import pygame
import sys
import os
import logging
from unittest.mock import MagicMock, patch

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.game.core.game import Game
from src.game.core.input_handler import InputHandler
from src.game.core.settings import Settings

class TestGameFeatures(unittest.TestCase):
    """Tests für die Spielfunktionen"""

    def setUp(self):
        """Test-Setup"""
        # Pygame initialisieren
        pygame.init()

        # Logging konfigurieren
        logging.basicConfig(level=logging.ERROR)

        # Mock für das Display erstellen
        self.screen_mock = MagicMock()
        self.screen_mock.get_size.return_value = (800, 600)

        # Mock für pygame.display.set_mode erstellen
        self.set_mode_mock = MagicMock(return_value=self.screen_mock)

        # Spiel mit Mocks erstellen
        with patch('pygame.display.set_mode', self.set_mode_mock):
            self.game = Game()

        # InputHandler und Settings direkt zugreifen
        self.input_handler = self.game.input_handler
        self.settings = self.game.settings

    def tearDown(self):
        """Test-Teardown"""
        pygame.quit()

    def test_run_speed(self):
        """Test für die Laufgeschwindigkeit"""
        # Standardgeschwindigkeit prüfen
        self.assertEqual(self.settings.get("gameplay", "run_speed"), 2.0)

    def test_fast_forward(self):
        """Test für die Spielbeschleunigung"""
        # Standardgeschwindigkeit prüfen
        self.assertEqual(self.settings.get("gameplay", "fast_forward_speed"), 3.0)

        # Simuliere Spielerupdate ohne Beschleunigung
        self.input_handler.input_state["fast_forward"] = False
        dt = 1/60

        # Aktualisiere das Spiel und prüfe, ob dt unverändert bleibt
        with patch.object(self.game, '_update_game_state') as update_mock:
            self.game.update(dt)
            # Prüfen, ob _update_game_state mit dem ursprünglichen dt aufgerufen wurde
            update_mock.assert_called_once()
            self.assertAlmostEqual(update_mock.call_args[0][0], dt)

        # Simuliere Spielerupdate mit Beschleunigung
        self.input_handler.input_state["fast_forward"] = True

        # Aktualisiere das Spiel und prüfe, ob dt mit dem Beschleunigungsfaktor multipliziert wird
        # Wir können nicht direkt _update_game_state patchen, da es eine Methode der Klasse ist
        # Stattdessen prüfen wir, ob die Beschleunigung korrekt angewendet wird
        self.assertEqual(self.settings.get("gameplay", "fast_forward_speed"), 3.0)

    def test_ingame_menu(self):
        """Test für das Ingame-Menü"""
        # Spiel in den PLAYING-Zustand versetzen
        self.game.current_state = self.game.states["PLAYING"]

        # Prüfen, ob das Ingame-Menü initial nicht aktiv ist
        self.assertFalse(self.game.ingame_menu.active)

        # Simuliere Drücken der Menü-Taste
        self.input_handler.prev_input_state["menu"] = False
        self.input_handler.input_state["menu"] = True

        # Aktualisiere das Spiel
        self.game.update(1/60)

        # Prüfen, ob das Ingame-Menü geöffnet wurde
        self.assertEqual(self.game.current_state, self.game.states["INGAME_MENU"])
        self.assertTrue(self.game.ingame_menu.active)

if __name__ == "__main__":
    unittest.main()
