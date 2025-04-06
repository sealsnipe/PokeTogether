#!/usr/bin/env python
"""
Debug-Test für die verbesserte Multiplayer-Synchronisierung
"""

import subprocess
import time
import logging
import os
import sys
import psutil

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_multiplayer_sync_debug.log')
    ]
)

logger = logging.getLogger(__name__)

def check_process_output(process, name, timeout=0.5):
    """Überprüft die Ausgabe eines Prozesses"""
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        if stdout:
            logger.info(f"{name} STDOUT: {stdout}")
        if stderr:
            logger.error(f"{name} STDERR: {stderr}")
        return True
    except subprocess.TimeoutExpired:
        # Prozess läuft noch, das ist gut
        return False

def main():
    """Hauptfunktion"""
    logger.info("=== STARTE DEBUG-TEST FÜR VERBESSERTE MULTIPLAYER-SYNCHRONISIERUNG ===")
    
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
    logger.info(f"Server-Prozess gestartet mit PID: {server_process.pid}")
    
    # Überprüfe, ob der Server-Prozess läuft
    time.sleep(1)
    if server_process.poll() is not None:
        logger.error(f"Server-Prozess wurde beendet mit Rückgabecode: {server_process.returncode}")
        check_process_output(server_process, "Server", timeout=0.1)
        return
    
    logger.info("Warte 2 Sekunden, bis der Server vollständig gestartet ist...")
    time.sleep(2)
    
    # Umgebungsvariablen für die Fenstertitel
    env1 = os.environ.copy()
    env1["PYGAME_WINDOW_TITLE"] = "PokeTogether - Player 1"
    
    # Clients starten
    logger.info("Client 1 wird gestartet...")
    client1_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--config", "config_player1.json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env1
    )
    logger.info(f"Client 1 Prozess gestartet mit PID: {client1_process.pid}")
    
    # Überprüfe, ob der Client 1 Prozess läuft
    time.sleep(1)
    if client1_process.poll() is not None:
        logger.error(f"Client 1 Prozess wurde beendet mit Rückgabecode: {client1_process.returncode}")
        check_process_output(client1_process, "Client 1", timeout=0.1)
        # Beende den Server-Prozess
        server_process.terminate()
        return
    
    logger.info("Warte 3 Sekunden, bis Client 1 verbunden ist...")
    time.sleep(3)
    
    # Umgebungsvariablen für die Fenstertitel
    env2 = os.environ.copy()
    env2["PYGAME_WINDOW_TITLE"] = "PokeTogether - Player 2"
    
    logger.info("Client 2 wird gestartet...")
    client2_process = subprocess.Popen(
        ["python", "src/main_refactored.py", "--config", "config_player2.json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env2
    )
    logger.info(f"Client 2 Prozess gestartet mit PID: {client2_process.pid}")
    
    # Überprüfe, ob der Client 2 Prozess läuft
    time.sleep(1)
    if client2_process.poll() is not None:
        logger.error(f"Client 2 Prozess wurde beendet mit Rückgabecode: {client2_process.returncode}")
        check_process_output(client2_process, "Client 2", timeout=0.1)
        # Beende die anderen Prozesse
        client1_process.terminate()
        server_process.terminate()
        return
    
    logger.info("Warte 3 Sekunden, bis Client 2 verbunden ist...")
    time.sleep(3)
    
    # Überprüfe, ob alle Prozesse noch laufen
    all_running = True
    for process, name in [(server_process, "Server"), (client1_process, "Client 1"), (client2_process, "Client 2")]:
        if process.poll() is not None:
            logger.error(f"{name} Prozess wurde beendet mit Rückgabecode: {process.returncode}")
            check_process_output(process, name, timeout=0.1)
            all_running = False
    
    if not all_running:
        logger.error("Nicht alle Prozesse laufen noch. Beende Test...")
        # Beende alle Prozesse
        for process in [client1_process, client2_process, server_process]:
            try:
                process.terminate()
            except:
                pass
        return
    
    # Liste alle laufenden Python-Prozesse auf
    logger.info("Laufende Python-Prozesse:")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                logger.info(f"PID: {proc.info['pid']}, Name: {proc.info['name']}, Cmdline: {' '.join(proc.info['cmdline'])}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Warte auf Benutzereingabe
    logger.info("=== TEST LÄUFT ===")
    logger.info("Bitte überprüfe, ob die Spieler korrekt angezeigt werden.")
    logger.info("Drücke Enter, um den Test zu beenden...")
    input()
    
    # Prozesse beenden
    logger.info("Beende Prozesse...")
    for process, name in [(server_process, "Server"), (client1_process, "Client 1"), (client2_process, "Client 2")]:
        try:
            logger.info(f"Beende {name} Prozess (PID: {process.pid})...")
            process.terminate()
            process.wait(timeout=2)
            logger.info(f"{name} Prozess beendet.")
        except Exception as e:
            logger.error(f"Fehler beim Beenden des {name} Prozesses: {e}")
    
    logger.info("=== TEST BEENDET ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unerwarteter Fehler im Hauptprogramm: {e}")
