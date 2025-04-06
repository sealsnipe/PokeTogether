#!/usr/bin/env python
"""
PokeTogether - Main Game Entry Point (refactored version)
"""

import logging
import logging.config
import sys
import os
import time
import argparse
from typing import Optional

# Füge den src-Ordner zum Pfad hinzu, damit die Module gefunden werden
src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importiere die Module
from game.core.game_refactored import Game
from game.core.config import Config


def setup_logging(config: Optional[Config] = None) -> logging.Logger:
    """Richtet das Logging-System ein

    Args:
        config: Konfigurationsobjekt (optional)

    Returns:
        Logger: Der Logger für das Hauptmodul
    """
    # Logging-Konfiguration aus Datei laden, falls vorhanden
    if os.path.exists('logging.conf'):
        logging.config.fileConfig('logging.conf')
    else:
        # Standard-Logging-Konfiguration
        log_file = "game.log"

        # Wenn eine Konfiguration vorhanden ist, verwende den instanzspezifischen Logs-Ordner
        if config:
            logs_dir = config.get_logs_dir()
            os.makedirs(logs_dir, exist_ok=True)
            log_file = os.path.join(logs_dir, "game.log")

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
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
    parser.add_argument("--config", default="config.json", help="Pfad zur Konfigurationsdatei")
    parser.add_argument("--screenshots", action="store_true", help="Screenshots während des Spiels aktivieren")
    parser.add_argument("--screenshot", action="store_true", help="Einen Screenshot erstellen und beenden")
    parser.add_argument("--output", help="Pfad für den Screenshot")
    parser.add_argument("--input", help="Eingabe simulieren (up, down, left, right, a, b, x, y, start, select)")
    parser.add_argument("--duration", type=float, default=0.5, help="Dauer der simulierten Eingabe in Sekunden")

    # Test-Optionen
    parser.add_argument("--test", help="Automatischen Test ausführen (movement, action, menu, comprehensive)")
    parser.add_argument("--test-file", help="Pfad zur Testdatei")

    # Multiplayer-Optionen
    parser.add_argument("--host", action="store_true", help="Spiel als Host starten")
    parser.add_argument("--join", help="Mit einem Host verbinden (IP-Adresse)")
    parser.add_argument("--port", type=int, default=8765, help="Port für Multiplayer-Verbindung")
    parser.add_argument("--server", action="store_true", help="Nur den Server starten (ohne Client)")

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


def start_server(config: Config, port: int) -> None:
    """Startet den Multiplayer-Server

    Args:
        config: Konfigurationsobjekt
        port: Port, auf dem der Server lauschen soll
    """
    from game.network.multiplayer_manager import MultiplayerManager

    logger = logging.getLogger(__name__)
    logger.info(f"Starting server on port {port}")

    # Server starten
    multiplayer_manager = MultiplayerManager()
    success = multiplayer_manager.start_hosting(port)

    if success:
        logger.info("Server started successfully. Press Ctrl+C to stop.")
        try:
            # Server läuft im Hintergrund, warte auf Benutzerabbruch
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
    else:
        logger.error("Failed to start server")

def main() -> int:
    """Main entry point for the game

    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    # Kommandozeilenargumente parsen
    args = parse_arguments()

    # Konfiguration laden
    config = Config(args.config)

    # Logging einrichten
    logger = setup_logging(config)
    logger.info(f"Starting PokeTogether with config: {args.config}")

    # Testanweisungen generieren, falls gewünscht
    if args.test:
        generate_test_instructions(args.test)

    # Wenn nur der Server gestartet werden soll
    if args.server:
        try:
            start_server(config, args.port)
            return 0
        except Exception as e:
            logger.error(f"Error running server: {e}", exc_info=True)
            return 1

    try:
        # Spiel starten
        game = Game(config=config, minimized=args.minimized)

        # Screenshots aktivieren, falls gewünscht
        if args.screenshots:
            logger.info("Screenshots enabled")
            game.enable_screenshots()

        # Screenshot erstellen und beenden, falls gewünscht
        if args.screenshot:
            logger.info("Taking screenshot and exiting")
            game.enable_screenshots()
            game.start_new_game()
            output_path = args.output if args.output else f"screenshot_{int(time.time())}.png"
            game.take_screenshot(output_path)
            return 0

        # Eingabe simulieren, falls gewünscht
        if args.input:
            logger.info(f"Simulating input: {args.input} for {args.duration} seconds")
            game.start_new_game()
            game.simulate_input(args.input, args.duration)
            return 0

        # Multiplayer-Optionen verarbeiten
        if args.host:
            logger.info("Starting game as host")
            game.start_new_game(as_host=True)
        elif args.join:
            # Wenn eine IP-Adresse angegeben wurde, verwende diese, ansonsten die aus der Konfiguration
            host = args.join
            port = args.port if args.port else config.get_server_port()
            logger.info(f"Joining game at {host}:{port}")
            game.join_session(host, port)
        elif not args.screenshot and not args.input:
            # Normaler Spielstart, wenn keine anderen Optionen angegeben wurden
            game.start_new_game()

        # Hauptspielschleife starten
        game.run()
    except Exception as e:
        logger.error(f"Error running game: {e}", exc_info=True)
        return 1

    logger.info("Game closed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
