#!/usr/bin/env python
"""
Input Command Reader - Liest Eingabebefehle aus Dateien und verarbeitet sie
"""

import os
import sys
import time
import json
import glob
import logging
import pygame
from typing import Dict, List, Any, Optional

class InputCommandReader:
    """Liest Eingabebefehle aus Dateien und verarbeitet sie"""

    def __init__(self, command_dir="input_commands"):
        """Initialisiert den Input-Command-Reader

        Args:
            command_dir: Verzeichnis, in dem die Befehlsdateien gespeichert werden
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisiere Input-Command-Reader")

        self.command_dir = command_dir
        os.makedirs(self.command_dir, exist_ok=True)

        # Letzter Zeitstempel, zu dem Befehle gelesen wurden
        self.last_check_time = time.time()
        
        # Tastenzuordnungen für die Umwandlung von Tastencodes in Pygame-Konstanten
        self.key_map = {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "w": pygame.K_w,
            "a": pygame.K_a,
            "s": pygame.K_s,
            "d": pygame.K_d,
            "space": pygame.K_SPACE,
            "return": pygame.K_RETURN,
            "enter": pygame.K_RETURN,
            "escape": pygame.K_ESCAPE,
            "esc": pygame.K_ESCAPE,
            "backspace": pygame.K_BACKSPACE,
            "tab": pygame.K_TAB,
            "shift": pygame.K_LSHIFT,
            "lshift": pygame.K_LSHIFT,
            "rshift": pygame.K_RSHIFT,
            "z": pygame.K_z,
            "x": pygame.K_x,
            "c": pygame.K_c,
            "v": pygame.K_v,
            "m": pygame.K_m,
            "f": pygame.K_f
        }

    def update(self) -> List[pygame.event.Event]:
        """Aktualisiert den Reader und gibt eine Liste von Ereignissen zurück

        Returns:
            List[pygame.event.Event]: Liste von Pygame-Ereignissen
        """
        events = []
        
        # Prüfe, ob neue Befehlsdateien vorhanden sind
        command_files = self.get_command_files()
        
        for file_path in command_files:
            try:
                # Lese den Befehl aus der Datei
                with open(file_path, 'r') as f:
                    command_data = json.load(f)
                
                # Verarbeite den Befehl
                event = self.process_command(command_data)
                if event:
                    events.append(event)
                
                # Lösche die Datei nach der Verarbeitung
                os.remove(file_path)
                
                # Erstelle eine .processed-Datei, um anzuzeigen, dass der Befehl verarbeitet wurde
                with open(f"{file_path}.processed", 'w') as f:
                    f.write(f"Processed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Exception as e:
                self.logger.error(f"Fehler beim Verarbeiten der Befehlsdatei {file_path}: {e}")
        
        # Aktualisiere den Zeitstempel
        self.last_check_time = time.time()
        
        return events

    def get_command_files(self) -> List[str]:
        """Gibt eine Liste von Befehlsdateien zurück

        Returns:
            List[str]: Liste von Dateipfaden
        """
        # Suche nach JSON-Dateien im Befehlsverzeichnis
        pattern = os.path.join(self.command_dir, "current_input_*.json")
        files = glob.glob(pattern)
        
        # Sortiere die Dateien nach Erstellungszeit
        files.sort(key=os.path.getctime)
        
        return files

    def process_command(self, command_data: Dict[str, Any]) -> Optional[pygame.event.Event]:
        """Verarbeitet einen Befehl und gibt ein Pygame-Ereignis zurück

        Args:
            command_data: Dictionary mit Befehlsdaten

        Returns:
            Optional[pygame.event.Event]: Pygame-Ereignis oder None, wenn kein Ereignis erzeugt werden konnte
        """
        command_type = command_data.get("type")
        
        if command_type == "key_press":
            key = command_data.get("key")
            key_code = command_data.get("key_code")
            
            # Verwende den key_code aus der Datei oder mappe den Schlüssel
            if key_code is None and key in self.key_map:
                key_code = self.key_map[key]
            
            if key_code is not None:
                self.logger.info(f"Erzeuge KEYDOWN-Ereignis für Taste: {key}")
                return pygame.event.Event(pygame.KEYDOWN, {"key": key_code})
        
        elif command_type == "key_release":
            key = command_data.get("key")
            key_code = command_data.get("key_code")
            
            # Verwende den key_code aus der Datei oder mappe den Schlüssel
            if key_code is None and key in self.key_map:
                key_code = self.key_map[key]
            
            if key_code is not None:
                self.logger.info(f"Erzeuge KEYUP-Ereignis für Taste: {key}")
                return pygame.event.Event(pygame.KEYUP, {"key": key_code})
        
        elif command_type == "button_press":
            button = command_data.get("button")
            button_code = command_data.get("button_code")
            
            if button_code is not None:
                self.logger.info(f"Erzeuge JOYBUTTONDOWN-Ereignis für Button: {button}")
                return pygame.event.Event(pygame.JOYBUTTONDOWN, {"joy": 0, "button": button_code})
        
        elif command_type == "button_release":
            button = command_data.get("button")
            button_code = command_data.get("button_code")
            
            if button_code is not None:
                self.logger.info(f"Erzeuge JOYBUTTONUP-Ereignis für Button: {button}")
                return pygame.event.Event(pygame.JOYBUTTONUP, {"joy": 0, "button": button_code})
        
        return None
