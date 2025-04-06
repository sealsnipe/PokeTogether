#!/usr/bin/env python
"""
Test für die Spielerposition-Synchronisierung im Multiplayer-Modus
"""

import os
import sys
import time
import logging
import argparse
import subprocess
import pygame
from datetime import datetime

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"test_logs/position_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory):
    """Stellt sicher, dass das angegebene Verzeichnis existiert"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def take_screenshot(window, filename):
    """Erstellt einen Screenshot des Pygame-Fensters"""
    pygame.image.save(window, filename)
    logger.info(f"Screenshot erstellt: {filename}")

def move_player(process, direction, duration=0.5):
    """Bewegt den Spieler in die angegebene Richtung"""
    key_map = {
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT
    }
    
    if direction not in key_map:
        logger.error(f"Ungültige Richtung: {direction}")
        return
    
    key = key_map[direction]
    
    # Taste drücken
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': key}))
    
    # Warten
    time.sleep(duration)
    
    # Taste loslassen
    pygame.event.post(pygame.event.Event(pygame.KEYUP, {'key': key}))
    
    logger.info(f"Spieler in Richtung {direction} bewegt")

def test_position_sync():
    """Testet die Spielerposition-Synchronisierung im Multiplayer-Modus"""
    # Verzeichnisse erstellen
    ensure_directory_exists("test_logs")
    ensure_directory_exists("test_screenshots")
    
    # Aktuelle Zeit für eindeutige Dateinamen
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Server starten
    logger.info("Server wird gestartet...")
    server_process = subprocess.Popen(
        [sys.executable, "src/game/network/server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Kurz warten, damit der Server starten kann
    time.sleep(1)
    
    # Client 1 starten (Host)
    logger.info("Client 1 (Host) wird gestartet...")
    client1_process = subprocess.Popen(
        [sys.executable, "src/main_refactored.py", "--host", "--name", "Player1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Kurz warten, damit Client 1 starten kann
    time.sleep(3)
    
    # Client 2 starten
    logger.info("Client 2 wird gestartet...")
    client2_process = subprocess.Popen(
        [sys.executable, "src/main_refactored.py", "--connect", "--name", "Player2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Warten, damit beide Clients verbinden können
    logger.info("Warte auf Verbindung...")
    time.sleep(5)
    
    # Pygame initialisieren
    pygame.init()
    
    try:
        # Fenster von Client 1 finden
        client1_window = None
        client2_window = None
        
        for window_id in pygame.display.get_window_size():
            window = pygame.display.set_mode((800, 600), pygame.NOFRAME)
            title = pygame.display.get_caption()[0]
            
            if "Player1" in title:
                client1_window = window
            elif "Player2" in title:
                client2_window = window
        
        if not client1_window or not client2_window:
            logger.error("Konnte nicht beide Client-Fenster finden")
            return
        
        # Screenshots vor der Bewegung
        logger.info("Erstelle Screenshots vor der Bewegung...")
        take_screenshot(client1_window, f"test_screenshots/client1_before_{timestamp}.png")
        take_screenshot(client2_window, f"test_screenshots/client2_before_{timestamp}.png")
        
        # Spieler 1 bewegen
        logger.info("Bewege Spieler 1...")
        move_player(client1_process, "right", 1.0)
        move_player(client1_process, "down", 1.0)
        
        # Warten, damit die Bewegung synchronisiert werden kann
        logger.info("Warte auf Synchronisierung...")
        time.sleep(2)
        
        # Screenshots nach der Bewegung
        logger.info("Erstelle Screenshots nach der Bewegung...")
        take_screenshot(client1_window, f"test_screenshots/client1_after_{timestamp}.png")
        take_screenshot(client2_window, f"test_screenshots/client2_after_{timestamp}.png")
        
        # Spieler 2 bewegen
        logger.info("Bewege Spieler 2...")
        move_player(client2_process, "left", 1.0)
        move_player(client2_process, "up", 1.0)
        
        # Warten, damit die Bewegung synchronisiert werden kann
        logger.info("Warte auf Synchronisierung...")
        time.sleep(2)
        
        # Screenshots nach der zweiten Bewegung
        logger.info("Erstelle Screenshots nach der zweiten Bewegung...")
        take_screenshot(client1_window, f"test_screenshots/client1_after2_{timestamp}.png")
        take_screenshot(client2_window, f"test_screenshots/client2_after2_{timestamp}.png")
        
        logger.info("Test abgeschlossen")
        
    except Exception as e:
        logger.error(f"Fehler während des Tests: {e}")
    finally:
        # Prozesse beenden
        logger.info("Beende Prozesse...")
        client1_process.terminate()
        client2_process.terminate()
        server_process.terminate()
        
        # Pygame beenden
        pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test für die Spielerposition-Synchronisierung im Multiplayer-Modus")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    test_position_sync()
