#!/usr/bin/env python
"""
Verbesserter Test für die Spielerposition-Synchronisierung im Multiplayer-Modus
"""

import os
import sys
import time
import json
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
        logging.FileHandler(f"test_logs/position_sync_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory):
    """Stellt sicher, dass das angegebene Verzeichnis existiert"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_test_report(timestamp, positions):
    """Erstellt einen Testbericht mit den Spielerpositionen"""
    report_file = f"test_logs/test_report_{timestamp}.txt"
    
    with open(report_file, "w") as f:
        f.write(f"Testbericht für Spielerposition-Synchronisierung ({timestamp})\n")
        f.write("=" * 80 + "\n\n")
        
        for phase, phase_data in positions.items():
            f.write(f"Phase: {phase}\n")
            f.write("-" * 40 + "\n")
            
            for client, client_data in phase_data.items():
                f.write(f"  {client}:\n")
                
                if "own_player" in client_data:
                    player = client_data["own_player"]
                    f.write(f"    Eigener Spieler: {player['name']} an Position ({player['x']}, {player['y']})\n")
                
                if "other_players" in client_data:
                    f.write(f"    Andere Spieler:\n")
                    for player in client_data["other_players"]:
                        f.write(f"      {player['name']} an Position ({player['x']}, {player['y']})\n")
            
            f.write("\n")
        
        # Auswertung
        f.write("Auswertung\n")
        f.write("-" * 40 + "\n")
        
        # Prüfen, ob die Positionen übereinstimmen
        for phase, phase_data in positions.items():
            if "client1" in phase_data and "client2" in phase_data:
                client1_data = phase_data["client1"]
                client2_data = phase_data["client2"]
                
                if "own_player" in client1_data and "other_players" in client2_data:
                    client1_player = client1_data["own_player"]
                    client2_other_players = client2_data["other_players"]
                    
                    client1_visible_in_client2 = False
                    for player in client2_other_players:
                        if player["name"] == client1_player["name"]:
                            client1_visible_in_client2 = True
                            if player["x"] == client1_player["x"] and player["y"] == client1_player["y"]:
                                f.write(f"✅ Phase {phase}: Client 1 ({client1_player['name']}) ist korrekt in Client 2 sichtbar an Position ({player['x']}, {player['y']})\n")
                            else:
                                f.write(f"❌ Phase {phase}: Client 1 ({client1_player['name']}) ist in Client 2 sichtbar, aber an falscher Position: Client 1 sieht sich selbst an ({client1_player['x']}, {client1_player['y']}), Client 2 sieht Client 1 an ({player['x']}, {player['y']})\n")
                    
                    if not client1_visible_in_client2:
                        f.write(f"❌ Phase {phase}: Client 1 ({client1_player['name']}) ist nicht in Client 2 sichtbar\n")
                
                if "own_player" in client2_data and "other_players" in client1_data:
                    client2_player = client2_data["own_player"]
                    client1_other_players = client1_data["other_players"]
                    
                    client2_visible_in_client1 = False
                    for player in client1_other_players:
                        if player["name"] == client2_player["name"]:
                            client2_visible_in_client1 = True
                            if player["x"] == client2_player["x"] and player["y"] == client2_player["y"]:
                                f.write(f"✅ Phase {phase}: Client 2 ({client2_player['name']}) ist korrekt in Client 1 sichtbar an Position ({player['x']}, {player['y']})\n")
                            else:
                                f.write(f"❌ Phase {phase}: Client 2 ({client2_player['name']}) ist in Client 1 sichtbar, aber an falscher Position: Client 2 sieht sich selbst an ({client2_player['x']}, {client2_player['y']}), Client 1 sieht Client 2 an ({player['x']}, {player['y']})\n")
                    
                    if not client2_visible_in_client1:
                        f.write(f"❌ Phase {phase}: Client 2 ({client2_player['name']}) ist nicht in Client 1 sichtbar\n")
        
        f.write("\n")
        f.write("Zusammenfassung\n")
        f.write("-" * 40 + "\n")
        
        # Gesamtergebnis
        success = True
        for phase, phase_data in positions.items():
            if "client1" in phase_data and "client2" in phase_data:
                client1_data = phase_data["client1"]
                client2_data = phase_data["client2"]
                
                if "own_player" in client1_data and "other_players" in client2_data:
                    client1_player = client1_data["own_player"]
                    client2_other_players = client2_data["other_players"]
                    
                    client1_visible_in_client2 = False
                    for player in client2_other_players:
                        if player["name"] == client1_player["name"]:
                            client1_visible_in_client2 = True
                            if player["x"] != client1_player["x"] or player["y"] != client1_player["y"]:
                                success = False
                    
                    if not client1_visible_in_client2:
                        success = False
                
                if "own_player" in client2_data and "other_players" in client1_data:
                    client2_player = client2_data["own_player"]
                    client1_other_players = client1_data["other_players"]
                    
                    client2_visible_in_client1 = False
                    for player in client1_other_players:
                        if player["name"] == client2_player["name"]:
                            client2_visible_in_client1 = True
                            if player["x"] != client2_player["x"] or player["y"] != client2_player["y"]:
                                success = False
                    
                    if not client2_visible_in_client1:
                        success = False
        
        if success:
            f.write("✅ Test erfolgreich: Die Spielerpositionen werden korrekt synchronisiert\n")
        else:
            f.write("❌ Test fehlgeschlagen: Die Spielerpositionen werden nicht korrekt synchronisiert\n")
    
    logger.info(f"Testbericht erstellt: {report_file}")
    return report_file

def extract_player_positions(log_file):
    """Extrahiert die Spielerpositionen aus der Log-Datei"""
    positions = {}
    
    with open(log_file, "r") as f:
        for line in f:
            if "[DATENFLUSS] RENDERING PLAYER" in line:
                # Beispiel: [DATENFLUSS] RENDERING PLAYER: 247b5950-cb12-4077-b7f7-ac5f34a15a26, data={"name": "Player1", "x": 560, "y": 448, "direction": "down", "character_type": "Red", "player_id": "90271bf9-c2e6-4a4a-9d5f-e5b5c5c5c5c5"}
                try:
                    # Extrahiere die Spielerdaten
                    data_start = line.find("data=") + 5
                    data_str = line[data_start:]
                    player_data = json.loads(data_str)
                    
                    # Extrahiere die Client-ID
                    client_id_start = line.find("PLAYER: ") + 8
                    client_id_end = line.find(", data=")
                    client_id = line[client_id_start:client_id_end]
                    
                    # Füge die Daten zum Dictionary hinzu
                    if client_id not in positions:
                        positions[client_id] = {}
                    
                    positions[client_id] = {
                        "name": player_data.get("name", "Unknown"),
                        "x": player_data.get("x", 0),
                        "y": player_data.get("y", 0),
                        "direction": player_data.get("direction", "down")
                    }
                except Exception as e:
                    logger.error(f"Fehler beim Extrahieren der Spielerdaten: {e}")
    
    return positions

def test_position_sync():
    """Testet die Spielerposition-Synchronisierung im Multiplayer-Modus"""
    # Verzeichnisse erstellen
    ensure_directory_exists("test_logs")
    ensure_directory_exists("test_screenshots")
    
    # Aktuelle Zeit für eindeutige Dateinamen
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Positionen für den Testbericht
    positions = {
        "before": {"client1": {}, "client2": {}},
        "after_client1_move": {"client1": {}, "client2": {}},
        "after_client2_move": {"client1": {}, "client2": {}}
    }
    
    try:
        # Server starten
        logger.info("Server wird gestartet...")
        server_process = subprocess.Popen(
            [sys.executable, "src/game/network/server.py"],
            stdout=open(f"test_logs/server_{timestamp}.log", "w"),
            stderr=subprocess.STDOUT
        )
        
        # Kurz warten, damit der Server starten kann
        time.sleep(1)
        
        # Client 1 starten (Host)
        logger.info("Client 1 (Host) wird gestartet...")
        client1_process = subprocess.Popen(
            [sys.executable, "src/main_refactored.py", "--host", "--name", "Player1", "--verbose"],
            stdout=open(f"test_logs/client1_{timestamp}.log", "w"),
            stderr=subprocess.STDOUT
        )
        
        # Kurz warten, damit Client 1 starten kann
        time.sleep(3)
        
        # Client 2 starten
        logger.info("Client 2 wird gestartet...")
        client2_process = subprocess.Popen(
            [sys.executable, "src/main_refactored.py", "--connect", "--name", "Player2", "--verbose"],
            stdout=open(f"test_logs/client2_{timestamp}.log", "w"),
            stderr=subprocess.STDOUT
        )
        
        # Warten, damit beide Clients verbinden können
        logger.info("Warte auf Verbindung...")
        time.sleep(5)
        
        # Screenshots vor der Bewegung
        logger.info("Erstelle Screenshots vor der Bewegung...")
        subprocess.run([sys.executable, "src/main_refactored.py", "--screenshot", "--output", f"test_screenshots/client1_before_{timestamp}.png"])
        subprocess.run([sys.executable, "src/main_refactored.py", "--screenshot", "--output", f"test_screenshots/client2_before_{timestamp}.png"])
        
        # Extrahiere Spielerpositionen vor der Bewegung
        positions["before"]["client1"] = extract_player_positions(f"test_logs/client1_{timestamp}.log")
        positions["before"]["client2"] = extract_player_positions(f"test_logs/client2_{timestamp}.log")
        
        # Spieler 1 bewegen
        logger.info("Bewege Spieler 1...")
        # Simuliere Tastendruck für Client 1
        subprocess.run([sys.executable, "src/main_refactored.py", "--input", "right", "--duration", "1.0"])
        subprocess.run([sys.executable, "src/main_refactored.py", "--input", "down", "--duration", "1.0"])
        
        # Warten, damit die Bewegung synchronisiert werden kann
        logger.info("Warte auf Synchronisierung...")
        time.sleep(2)
        
        # Screenshots nach der Bewegung
        logger.info("Erstelle Screenshots nach der Bewegung...")
        subprocess.run([sys.executable, "src/main_refactored.py", "--screenshot", "--output", f"test_screenshots/client1_after_{timestamp}.png"])
        subprocess.run([sys.executable, "src/main_refactored.py", "--screenshot", "--output", f"test_screenshots/client2_after_{timestamp}.png"])
        
        # Extrahiere Spielerpositionen nach der Bewegung
        positions["after_client1_move"]["client1"] = extract_player_positions(f"test_logs/client1_{timestamp}.log")
        positions["after_client1_move"]["client2"] = extract_player_positions(f"test_logs/client2_{timestamp}.log")
        
        # Spieler 2 bewegen
        logger.info("Bewege Spieler 2...")
        # Simuliere Tastendruck für Client 2
        subprocess.run([sys.executable, "src/main_refactored.py", "--input", "left", "--duration", "1.0"])
        subprocess.run([sys.executable, "src/main_refactored.py", "--input", "up", "--duration", "1.0"])
        
        # Warten, damit die Bewegung synchronisiert werden kann
        logger.info("Warte auf Synchronisierung...")
        time.sleep(2)
        
        # Screenshots nach der zweiten Bewegung
        logger.info("Erstelle Screenshots nach der zweiten Bewegung...")
        subprocess.run([sys.executable, "src/main_refactored.py", "--screenshot", "--output", f"test_screenshots/client1_after2_{timestamp}.png"])
        subprocess.run([sys.executable, "src/main_refactored.py", "--screenshot", "--output", f"test_screenshots/client2_after2_{timestamp}.png"])
        
        # Extrahiere Spielerpositionen nach der zweiten Bewegung
        positions["after_client2_move"]["client1"] = extract_player_positions(f"test_logs/client1_{timestamp}.log")
        positions["after_client2_move"]["client2"] = extract_player_positions(f"test_logs/client2_{timestamp}.log")
        
        # Erstelle Testbericht
        report_file = create_test_report(timestamp, positions)
        
        logger.info("Test abgeschlossen")
        logger.info(f"Testbericht: {report_file}")
        
    except Exception as e:
        logger.error(f"Fehler während des Tests: {e}")
    finally:
        # Prozesse beenden
        logger.info("Beende Prozesse...")
        if 'client1_process' in locals():
            client1_process.terminate()
        if 'client2_process' in locals():
            client2_process.terminate()
        if 'server_process' in locals():
            server_process.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test für die Spielerposition-Synchronisierung im Multiplayer-Modus")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgabe")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    test_position_sync()
