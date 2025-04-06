#!/usr/bin/env python
"""
Einfacher Test für die Spielerposition-Synchronisierung im Multiplayer-Modus
"""

import os
import sys
import time
import json
import logging
import argparse
import subprocess
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

def take_screenshot(instance_name, timestamp):
    """Erstellt einen Screenshot des Spiels"""
    screenshot_file = f"test_screenshots/{instance_name}_{timestamp}.png"
    
    try:
        # Führe das Spiel mit dem Screenshot-Parameter aus
        subprocess.run(
            [sys.executable, "src/main_refactored.py", "--screenshot", "--output", screenshot_file],
            check=True
        )
        logger.info(f"Screenshot erstellt: {screenshot_file}")
        return screenshot_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Fehler beim Erstellen des Screenshots: {e}")
        return None

def move_player(direction, duration=0.5):
    """Bewegt den Spieler in die angegebene Richtung"""
    try:
        # Führe das Spiel mit dem Input-Parameter aus
        subprocess.run(
            [sys.executable, "src/main_refactored.py", "--input", direction, "--duration", str(duration)],
            check=True
        )
        logger.info(f"Spieler in Richtung {direction} bewegt")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Fehler beim Bewegen des Spielers: {e}")
        return False

def extract_player_positions(log_file):
    """Extrahiert die Spielerpositionen aus der Log-Datei"""
    positions = {
        "own_player": {},
        "other_players": []
    }
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                # Eigene Spielerposition
                if "[DATENFLUSS] PLAYER DATA COLLECTED" in line:
                    try:
                        # Extrahiere die Spielerdaten
                        data_start = line.find("{")
                        data_end = line.rfind("}") + 1
                        data_str = line[data_start:data_end]
                        player_data = json.loads(data_str)
                        
                        positions["own_player"] = {
                            "name": player_data.get("name", "Unknown"),
                            "x": player_data.get("x", 0),
                            "y": player_data.get("y", 0),
                            "direction": player_data.get("direction", "down")
                        }
                    except Exception as e:
                        logger.error(f"Fehler beim Extrahieren der eigenen Spielerdaten: {e}")
                
                # Andere Spielerpositionen
                elif "[DATENFLUSS] RENDERING PLAYER" in line and "data=" in line:
                    try:
                        # Extrahiere die Spielerdaten
                        data_start = line.find("data=") + 5
                        data_str = line[data_start:]
                        player_data = json.loads(data_str)
                        
                        other_player = {
                            "name": player_data.get("name", "Unknown"),
                            "x": player_data.get("x", 0),
                            "y": player_data.get("y", 0),
                            "direction": player_data.get("direction", "down")
                        }
                        
                        # Prüfe, ob der Spieler bereits in der Liste ist
                        player_exists = False
                        for i, player in enumerate(positions["other_players"]):
                            if player["name"] == other_player["name"]:
                                # Aktualisiere die Position
                                positions["other_players"][i] = other_player
                                player_exists = True
                                break
                        
                        if not player_exists:
                            positions["other_players"].append(other_player)
                    except Exception as e:
                        logger.error(f"Fehler beim Extrahieren der anderen Spielerdaten: {e}")
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Log-Datei: {e}")
    
    return positions

def create_test_report(timestamp, client1_positions, client2_positions, screenshots):
    """Erstellt einen Testbericht mit den Spielerpositionen"""
    report_file = f"test_logs/test_report_{timestamp}.txt"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"Testbericht für Spielerposition-Synchronisierung ({timestamp})\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("Screenshots\n")
        f.write("-" * 40 + "\n")
        for name, path in screenshots.items():
            f.write(f"{name}: {path}\n")
        f.write("\n")
        
        f.write("Client 1 Positionen\n")
        f.write("-" * 40 + "\n")
        f.write(f"Eigener Spieler: {client1_positions['own_player'].get('name', 'Unknown')} an Position ({client1_positions['own_player'].get('x', '?')}, {client1_positions['own_player'].get('y', '?')})\n")
        f.write("Andere Spieler:\n")
        for player in client1_positions["other_players"]:
            f.write(f"  {player.get('name', 'Unknown')} an Position ({player.get('x', '?')}, {player.get('y', '?')})\n")
        f.write("\n")
        
        f.write("Client 2 Positionen\n")
        f.write("-" * 40 + "\n")
        f.write(f"Eigener Spieler: {client2_positions['own_player'].get('name', 'Unknown')} an Position ({client2_positions['own_player'].get('x', '?')}, {client2_positions['own_player'].get('y', '?')})\n")
        f.write("Andere Spieler:\n")
        for player in client2_positions["other_players"]:
            f.write(f"  {player.get('name', 'Unknown')} an Position ({player.get('x', '?')}, {player.get('y', '?')})\n")
        f.write("\n")
        
        f.write("Auswertung\n")
        f.write("-" * 40 + "\n")
        
        # Prüfe, ob Client 1 in Client 2 sichtbar ist
        client1_name = client1_positions["own_player"].get("name", "Unknown")
        client1_x = client1_positions["own_player"].get("x", None)
        client1_y = client1_positions["own_player"].get("y", None)
        
        client1_visible_in_client2 = False
        for player in client2_positions["other_players"]:
            if player.get("name", "") == client1_name:
                client1_visible_in_client2 = True
                if player.get("x") == client1_x and player.get("y") == client1_y:
                    f.write(f"✓ Client 1 ({client1_name}) ist korrekt in Client 2 sichtbar an Position ({client1_x}, {client1_y})\n")
                else:
                    f.write(f"✗ Client 1 ({client1_name}) ist in Client 2 sichtbar, aber an falscher Position:\n")
                    f.write(f"  - Client 1 sieht sich selbst an Position ({client1_x}, {client1_y})\n")
                    f.write(f"  - Client 2 sieht Client 1 an Position ({player.get('x')}, {player.get('y')})\n")
                break
        
        if not client1_visible_in_client2:
            f.write(f"✗ Client 1 ({client1_name}) ist nicht in Client 2 sichtbar\n")
        
        # Prüfe, ob Client 2 in Client 1 sichtbar ist
        client2_name = client2_positions["own_player"].get("name", "Unknown")
        client2_x = client2_positions["own_player"].get("x", None)
        client2_y = client2_positions["own_player"].get("y", None)
        
        client2_visible_in_client1 = False
        for player in client1_positions["other_players"]:
            if player.get("name", "") == client2_name:
                client2_visible_in_client1 = True
                if player.get("x") == client2_x and player.get("y") == client2_y:
                    f.write(f"✓ Client 2 ({client2_name}) ist korrekt in Client 1 sichtbar an Position ({client2_x}, {client2_y})\n")
                else:
                    f.write(f"✗ Client 2 ({client2_name}) ist in Client 1 sichtbar, aber an falscher Position:\n")
                    f.write(f"  - Client 2 sieht sich selbst an Position ({client2_x}, {client2_y})\n")
                    f.write(f"  - Client 1 sieht Client 2 an Position ({player.get('x')}, {player.get('y')})\n")
                break
        
        if not client2_visible_in_client1:
            f.write(f"✗ Client 2 ({client2_name}) ist nicht in Client 1 sichtbar\n")
        
        f.write("\n")
        f.write("Zusammenfassung\n")
        f.write("-" * 40 + "\n")
        
        if client1_visible_in_client2 and client2_visible_in_client1:
            if (client1_x == client2_positions["other_players"][0].get("x") and 
                client1_y == client2_positions["other_players"][0].get("y") and
                client2_x == client1_positions["other_players"][0].get("x") and
                client2_y == client1_positions["other_players"][0].get("y")):
                f.write("✓ Test erfolgreich: Die Spielerpositionen werden korrekt synchronisiert\n")
            else:
                f.write("✗ Test fehlgeschlagen: Die Spielerpositionen werden nicht korrekt synchronisiert\n")
        else:
            f.write("✗ Test fehlgeschlagen: Nicht alle Spieler sind für den jeweils anderen Spieler sichtbar\n")
    
    logger.info(f"Testbericht erstellt: {report_file}")
    return report_file

def test_position_sync():
    """Testet die Spielerposition-Synchronisierung im Multiplayer-Modus"""
    # Verzeichnisse erstellen
    ensure_directory_exists("test_logs")
    ensure_directory_exists("test_screenshots")
    
    # Aktuelle Zeit für eindeutige Dateinamen
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Log-Dateien
    client1_log = f"test_logs/client1_{timestamp}.log"
    client2_log = f"test_logs/client2_{timestamp}.log"
    server_log = f"test_logs/server_{timestamp}.log"
    
    # Screenshots
    screenshots = {}
    
    try:
        # Server starten
        logger.info("Server wird gestartet...")
        server_process = subprocess.Popen(
            [sys.executable, "src/game/network/server.py"],
            stdout=open(server_log, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT
        )
        
        # Kurz warten, damit der Server starten kann
        time.sleep(1)
        
        # Client 1 starten (Host)
        logger.info("Client 1 (Host) wird gestartet...")
        client1_process = subprocess.Popen(
            [sys.executable, "src/main_refactored.py", "--host", "--name", "Player1", "--verbose"],
            stdout=open(client1_log, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT
        )
        
        # Kurz warten, damit Client 1 starten kann
        time.sleep(3)
        
        # Client 2 starten
        logger.info("Client 2 wird gestartet...")
        client2_process = subprocess.Popen(
            [sys.executable, "src/main_refactored.py", "--connect", "--name", "Player2", "--verbose"],
            stdout=open(client2_log, "w", encoding="utf-8"),
            stderr=subprocess.STDOUT
        )
        
        # Warten, damit beide Clients verbinden können
        logger.info("Warte auf Verbindung...")
        time.sleep(10)
        
        # Screenshots vor der Bewegung
        logger.info("Erstelle Screenshots vor der Bewegung...")
        screenshots["client1_before"] = take_screenshot("client1_before", timestamp)
        screenshots["client2_before"] = take_screenshot("client2_before", timestamp)
        
        # Spieler 1 bewegen
        logger.info("Bewege Spieler 1...")
        move_player("right", 1.0)
        move_player("down", 1.0)
        
        # Warten, damit die Bewegung synchronisiert werden kann
        logger.info("Warte auf Synchronisierung...")
        time.sleep(2)
        
        # Screenshots nach der Bewegung
        logger.info("Erstelle Screenshots nach der Bewegung...")
        screenshots["client1_after"] = take_screenshot("client1_after", timestamp)
        screenshots["client2_after"] = take_screenshot("client2_after", timestamp)
        
        # Spieler 2 bewegen
        logger.info("Bewege Spieler 2...")
        move_player("left", 1.0)
        move_player("up", 1.0)
        
        # Warten, damit die Bewegung synchronisiert werden kann
        logger.info("Warte auf Synchronisierung...")
        time.sleep(2)
        
        # Screenshots nach der zweiten Bewegung
        logger.info("Erstelle Screenshots nach der zweiten Bewegung...")
        screenshots["client1_after2"] = take_screenshot("client1_after2", timestamp)
        screenshots["client2_after2"] = take_screenshot("client2_after2", timestamp)
        
        # Prozesse beenden
        logger.info("Beende Prozesse...")
        client1_process.terminate()
        client2_process.terminate()
        server_process.terminate()
        
        # Warten, damit die Prozesse beendet werden können
        time.sleep(1)
        
        # Spielerpositionen extrahieren
        logger.info("Extrahiere Spielerpositionen...")
        client1_positions = extract_player_positions(client1_log)
        client2_positions = extract_player_positions(client2_log)
        
        # Testbericht erstellen
        logger.info("Erstelle Testbericht...")
        report_file = create_test_report(timestamp, client1_positions, client2_positions, screenshots)
        
        logger.info("Test abgeschlossen")
        logger.info(f"Testbericht: {report_file}")
        
        # Testbericht anzeigen
        with open(report_file, "r", encoding="utf-8") as f:
            print("\n" + f.read())
        
    except Exception as e:
        logger.error(f"Fehler während des Tests: {e}")
        
        # Prozesse beenden, falls sie noch laufen
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
