#!/usr/bin/env python
"""
PokeTogether - Main Game Entry Point (refactored version)
"""

import logging
import logging.config
import sys
import os
import argparse
from typing import Dict, Any, Optional

# Füge den src-Ordner zum Pfad hinzu, damit die Module gefunden werden
src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importiere das Game-Modul
from game.core.game_refactored import Game


def setup_logging() -> logging.Logger:
    """Richtet das Logging-System ein

    Returns:
        Logger: Der Logger für das Hauptmodul
    """
    # Logging-Konfiguration aus Datei laden, falls vorhanden
    if os.path.exists('logging.conf'):
        logging.config.fileConfig('logging.conf')
    else:
        # Standard-Logging-Konfiguration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("game.log"),
                logging.StreamHandler()
            ]
        )

    return logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Kommandozeilenargumente parsen

    Returns:
        Namespace: Die geparsten Kommandozeilenargumente
    """
    parser = argparse.ArgumentParser(description="PokeTogether - Ein Pokémon-Spiel")
    
    # Allgemeine Optionen
    parser.add_argument("--minimized", action="store_true", help="Spiel minimiert starten")
    parser.add_argument("--fullscreen", action="store_true", help="Spiel im Vollbildmodus starten")
    parser.add_argument("--resolution", help="Bildschirmauflösung (z.B. 800x600)")
    
    # Test-Optionen
    parser.add_argument("--test", help="Automatischen Test ausführen (movement, action, menu, comprehensive)")
    parser.add_argument("--test-file", help="Pfad zur Testdatei")
    
    # Multiplayer-Optionen
    parser.add_argument("--host", action="store_true", help="Spiel als Host starten")
    parser.add_argument("--join", help="Mit einem Host verbinden (IP-Adresse)")
    parser.add_argument("--port", type=int, default=8765, help="Port für Multiplayer-Verbindung")

    return parser.parse_args()


def generate_test_instructions(test_type: str) -> None:
    """Generiert Testanweisungen für automatische Tests

    Args:
        test_type: Art des Tests (movement, action, menu, comprehensive)
    """
    try:
        import subprocess
        logging.info(f"Generiere Testanweisungen für: {test_type}")
        subprocess.run(["python", "tools/generate_test_instructions.py", "--test", test_type, "--output", "input_instructions"])
    except Exception as e:
        logging.error(f"Fehler beim Generieren der Testanweisungen: {e}")


def main() -> int:
    """Main entry point for the game

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    # Kommandozeilenargumente parsen
    args = parse_arguments()
    
    # Logging einrichten
    logger = setup_logging()
    logger.info("Starting PokeTogether")
    
    # Testanweisungen generieren, falls gewünscht
    if args.test:
        generate_test_instructions(args.test)
    
    try:
        # Spiel starten
        game = Game(minimized=args.minimized)
        
        # Multiplayer-Optionen verarbeiten
        if args.host:
            logger.info("Starting game as host")
            game.start_new_game(as_host=True)
        elif args.join:
            logger.info(f"Joining game at {args.join}:{args.port}")
            game.join_session(args.join, args.port)
        
        # Hauptspielschleife starten
        game.run()
    except Exception as e:
        logger.error(f"Error running game: {e}", exc_info=True)
        return 1
    
    logger.info("Game closed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
