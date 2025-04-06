#!/usr/bin/env python
"""
PokeTogether - Main Game Entry Point
"""

import logging
import logging.config
import sys
import os
import argparse

# Füge den src-Ordner zum Pfad hinzu, damit die Module gefunden werden
src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importiere das Game-Modul
from game.core.game import Game

def setup_logging():
    """Richtet das Logging-System ein"""
    if os.path.exists('logging.conf'):
        logging.config.fileConfig('logging.conf')
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    return logging.getLogger(__name__)

def parse_arguments():
    """Kommandozeilenargumente parsen"""
    parser = argparse.ArgumentParser(description="PokeTogether - Ein Pokémon-Spiel")
    parser.add_argument("--minimized", action="store_true", help="Spiel minimiert starten")
    parser.add_argument("--test", help="Automatischen Test ausführen (movement, action, menu, comprehensive)")

    return parser.parse_args()

def main():
    """Main entry point for the game"""
    args = parse_arguments()
    logger = setup_logging()
    logger.info("Starting PokeTogether")

    # Wenn ein Test angegeben wurde, generiere die Testanweisungen
    if args.test:
        try:
            import subprocess
            logger.info(f"Generiere Testanweisungen für: {args.test}")
            subprocess.run(["python", "tools/generate_test_instructions.py", "--test", args.test, "--output", "input_instructions"])
        except Exception as e:
            logger.error(f"Fehler beim Generieren der Testanweisungen: {e}")

    try:
        # Spiel minimiert starten, wenn --minimized angegeben wurde
        game = Game(minimized=args.minimized)
        game.run()
    except Exception as e:
        logger.error(f"Error running game: {e}", exc_info=True)
        return 1

    logger.info("Game closed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
