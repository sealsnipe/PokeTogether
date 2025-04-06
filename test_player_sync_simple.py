#!/usr/bin/env python
"""
Einfacher Test für die Spielerposition-Synchronisierung
"""

import subprocess
import time
import logging
import os
import sys
import json

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_player_sync.log')
    ]
)

logger = logging.getLogger(__name__)

def start_server():
    """Startet den Server"""
    logger.info("Server wird gestartet...")
    server_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--server", "--port", "8765"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(2)  # Warte, bis der Server gestartet ist
    return server_process

def start_client(config_file):
    """Startet einen Client mit der angegebenen Konfiguration"""
    logger.info(f"Client mit Konfiguration {config_file} wird gestartet...")
    client_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--config", config_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(3)  # Warte, bis der Client gestartet ist
    return client_process

def check_server_logs():
    """Überprüft die Server-Logs auf Spielerpositionen"""
    logger.info("Überprüfe Server-Logs auf Spielerpositionen...")
    
    try:
        with open("game.log", "r") as f:
            log_lines = f.readlines()
        
        # Suche nach Spielerpositionen in den Logs
        position_logs = [line for line in log_lines if "[SPIELERSYNC]" in line and "POSITION" in line]
        
        if position_logs:
            logger.info(f"Gefundene Positionslogs: {len(position_logs)}")
            for i, log in enumerate(position_logs[-10:]):  # Zeige die letzten 10 Logs
                logger.info(f"Log {i+1}: {log.strip()}")
            return True
        else:
            logger.warning("Keine Positionslogs gefunden!")
            return False
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen der Logs: {e}")
        return False

def main():
    """Hauptfunktion"""
    logger.info("=== STARTE SPIELERPOSITION-SYNCHRONISIERUNGSTEST ===")
    
    # Server starten
    server_process = start_server()
    logger.info("Warte 2 Sekunden, bis der Server vollständig gestartet ist...")
    time.sleep(2)
    
    # Clients starten
    client1_process = start_client("config_player1.json")
    logger.info("Warte 3 Sekunden, bis Client 1 verbunden ist...")
    time.sleep(3)
    
    client2_process = start_client("config_player2.json")
    logger.info("Warte 3 Sekunden, bis Client 2 verbunden ist...")
    time.sleep(3)
    
    # Warte, bis die Spieler synchronisiert sind
    logger.info("Warte 5 Sekunden auf Synchronisierung...")
    time.sleep(5)
    
    # Überprüfe die Logs
    success = check_server_logs()
    
    # Prozesse beenden
    logger.info("Beende Prozesse...")
    for process in [client1_process, client2_process, server_process]:
        try:
            process.terminate()
            process.wait(timeout=2)
        except Exception as e:
            logger.error(f"Fehler beim Beenden eines Prozesses: {e}")
    
    if success:
        logger.info("=== TEST ERFOLGREICH ABGESCHLOSSEN ===")
    else:
        logger.error("=== TEST FEHLGESCHLAGEN ===")

if __name__ == "__main__":
    main()
