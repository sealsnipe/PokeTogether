#!/usr/bin/env python
"""
Visueller Test für die Spielerposition-Synchronisierung
"""

import subprocess
import time
import logging
import os
import sys
import json
import pygame
import pyautogui

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_player_sync_visual.log')
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

def start_client(config_file, window_title=None):
    """Startet einen Client mit der angegebenen Konfiguration"""
    logger.info(f"Client mit Konfiguration {config_file} wird gestartet...")
    
    # Wenn ein Fenstertitel angegeben ist, füge ihn als Umgebungsvariable hinzu
    env = os.environ.copy()
    if window_title:
        env["PYGAME_WINDOW_TITLE"] = window_title
    
    client_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--config", config_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    time.sleep(3)  # Warte, bis der Client gestartet ist
    return client_process

def take_screenshot(window_title, filename):
    """Macht einen Screenshot des Spielfensters"""
    logger.info(f"Mache Screenshot von Fenster '{window_title}'...")
    
    try:
        # Suche nach dem Fenster mit dem angegebenen Titel
        windows = pyautogui.getWindowsWithTitle(window_title)
        if not windows:
            logger.warning(f"Fenster mit Titel '{window_title}' nicht gefunden!")
            return False
        
        window = windows[0]
        window.activate()
        time.sleep(0.5)  # Warte, bis das Fenster aktiviert ist
        
        # Mache einen Screenshot des Fensters
        screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
        screenshot.save(filename)
        logger.info(f"Screenshot gespeichert als {filename}")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Screenshots: {e}")
        return False

def simulate_movement(window_title, keys, duration=1.0):
    """Simuliert Tastatureingaben zur Bewegung des Spielers"""
    logger.info(f"Simuliere Bewegung in Fenster '{window_title}' mit Tasten {keys}...")
    
    try:
        # Suche nach dem Fenster mit dem angegebenen Titel
        windows = pyautogui.getWindowsWithTitle(window_title)
        if not windows:
            logger.warning(f"Fenster mit Titel '{window_title}' nicht gefunden!")
            return False
        
        window = windows[0]
        window.activate()
        time.sleep(0.5)  # Warte, bis das Fenster aktiviert ist
        
        # Drücke die angegebenen Tasten
        for key in keys:
            pyautogui.keyDown(key)
        
        # Warte für die angegebene Dauer
        time.sleep(duration)
        
        # Lasse die Tasten los
        for key in keys:
            pyautogui.keyUp(key)
        
        logger.info(f"Bewegung in Fenster '{window_title}' abgeschlossen")
        return True
    except Exception as e:
        logger.error(f"Fehler bei der Simulation der Bewegung: {e}")
        return False

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
    logger.info("=== STARTE VISUELLEN SPIELERPOSITION-SYNCHRONISIERUNGSTEST ===")
    
    # Erstelle Screenshot-Verzeichnis, falls es nicht existiert
    os.makedirs("test_screenshots", exist_ok=True)
    
    # Server starten
    server_process = start_server()
    logger.info("Warte 2 Sekunden, bis der Server vollständig gestartet ist...")
    time.sleep(2)
    
    # Clients starten
    client1_process = start_client("config_player1.json", "PokeTogether - Player 1")
    logger.info("Warte 3 Sekunden, bis Client 1 verbunden ist...")
    time.sleep(3)
    
    client2_process = start_client("config_player2.json", "PokeTogether - Player 2")
    logger.info("Warte 3 Sekunden, bis Client 2 verbunden ist...")
    time.sleep(3)
    
    # Warte, bis die Spieler synchronisiert sind
    logger.info("Warte 5 Sekunden auf Synchronisierung...")
    time.sleep(5)
    
    # Mache Screenshots vor der Bewegung
    logger.info("Mache Screenshots vor der Bewegung...")
    take_screenshot("PokeTogether - Player 1", "test_screenshots/player1_before.png")
    take_screenshot("PokeTogether - Player 2", "test_screenshots/player2_before.png")
    
    # Simuliere Bewegung für Spieler 1
    logger.info("Simuliere Bewegung für Spieler 1...")
    simulate_movement("PokeTogether - Player 1", ['down'], 2.0)
    
    # Warte auf Synchronisierung
    logger.info("Warte 3 Sekunden auf Synchronisierung nach Bewegung...")
    time.sleep(3)
    
    # Mache Screenshots nach der Bewegung
    logger.info("Mache Screenshots nach der Bewegung...")
    take_screenshot("PokeTogether - Player 1", "test_screenshots/player1_after.png")
    take_screenshot("PokeTogether - Player 2", "test_screenshots/player2_after.png")
    
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
        logger.info("Bitte überprüfe die Screenshots im Verzeichnis 'test_screenshots':")
        logger.info("- player1_before.png und player2_before.png: Spielerpositionen vor der Bewegung")
        logger.info("- player1_after.png und player2_after.png: Spielerpositionen nach der Bewegung")
    else:
        logger.error("=== TEST FEHLGESCHLAGEN ===")

if __name__ == "__main__":
    main()
