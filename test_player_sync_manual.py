#!/usr/bin/env python
"""
Manueller Test für die Spielerposition-Synchronisierung
"""

import subprocess
import time
import logging
import os
import sys

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_player_sync_manual.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion"""
    logger.info("=== STARTE MANUELLEN SPIELERPOSITION-SYNCHRONISIERUNGSTEST ===")
    
    # Stelle sicher, dass das Screenshots-Verzeichnis existiert
    os.makedirs("test_screenshots", exist_ok=True)
    
    # Server starten
    logger.info("Server wird gestartet...")
    server_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--server", "--port", "8765"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    logger.info("Warte 2 Sekunden, bis der Server vollständig gestartet ist...")
    time.sleep(2)
    
    # Umgebungsvariablen für die Fenstertitel
    env1 = os.environ.copy()
    env1["PYGAME_WINDOW_TITLE"] = "PokeTogether - Player 1"
    
    env2 = os.environ.copy()
    env2["PYGAME_WINDOW_TITLE"] = "PokeTogether - Player 2"
    
    # Clients starten
    logger.info("Client 1 wird gestartet...")
    client1_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--config", "config_player1.json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env1
    )
    logger.info("Warte 3 Sekunden, bis Client 1 verbunden ist...")
    time.sleep(3)
    
    logger.info("Client 2 wird gestartet...")
    client2_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--config", "config_player2.json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env2
    )
    logger.info("Warte 3 Sekunden, bis Client 2 verbunden ist...")
    time.sleep(3)
    
    # Warte auf Benutzereingabe
    logger.info("=== TEST LÄUFT ===")
    logger.info("Bitte überprüfe, ob die Spieler korrekt angezeigt werden.")
    logger.info("Drücke Enter, um den Test zu beenden...")
    input()
    
    # Prozesse beenden
    logger.info("Beende Prozesse...")
    for process in [client1_process, client2_process, server_process]:
        try:
            process.terminate()
            process.wait(timeout=2)
        except Exception as e:
            logger.error(f"Fehler beim Beenden eines Prozesses: {e}")
    
    logger.info("=== TEST BEENDET ===")

if __name__ == "__main__":
    main()
