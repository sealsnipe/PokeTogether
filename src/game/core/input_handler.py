#!/usr/bin/env python
"""
Input Handler - Verarbeitet Tastatur- und Controller-Eingaben
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any
from game.core.controller_constants import *

class InputHandler:
    """Verarbeitet Tastatur- und Controller-Eingaben"""

    def __init__(self):
        """Initialisiert den Input-Handler"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialisiere Input-Handler")

        # Tastatur-Konfiguration
        self.keyboard_config = {
            # Bewegung
            "up": [pygame.K_UP, pygame.K_w],
            "down": [pygame.K_DOWN, pygame.K_s],
            "left": [pygame.K_LEFT, pygame.K_a],
            "right": [pygame.K_RIGHT, pygame.K_d],

            # Aktionen
            "action": [pygame.K_SPACE, pygame.K_RETURN, pygame.K_z],  # Z-Taste als Alternative
            "cancel": [pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_x],  # X-Taste als Alternative
            "menu": [pygame.K_TAB, pygame.K_m],  # Menü öffnen/schließen

            # Zusätzliche Aktionen
            "run": [pygame.K_LSHIFT, pygame.K_RSHIFT],  # Rennen
            "fast_forward": [pygame.K_f, pygame.K_SPACE]  # Vorspulen mit F oder Leertaste
        }

        # Controller-Konfiguration
        self.controller_config = {
            # Bewegung
            "up": [(0, AXIS_LEFTY, -AXIS_DEADZONE), (0, BUTTON_DPAD_UP, 1)],
            "down": [(0, AXIS_LEFTY, AXIS_DEADZONE), (0, BUTTON_DPAD_DOWN, 1)],
            "left": [(0, AXIS_LEFTX, -AXIS_DEADZONE), (0, BUTTON_DPAD_LEFT, 1)],
            "right": [(0, AXIS_LEFTX, AXIS_DEADZONE), (0, BUTTON_DPAD_RIGHT, 1)],

            # Aktionen
            "action": [(0, BUTTON_A, 1)],  # Hauptaktion (Interaktion, Bestätigen)
            "cancel": [(0, BUTTON_B, 1)],  # Abbrechen, Zurück
            "menu": [(0, BUTTON_START, 1), (0, BUTTON_BACK, 1)],  # Menü öffnen/schließen

            # Zusätzliche Aktionen
            "secondary": [(0, BUTTON_X, 1)],  # Sekundäre Aktion
            "tertiary": [(0, BUTTON_Y, 1)],  # Tertiäre Aktion
            "run": [(0, BUTTON_RIGHTSHOULDER, 1)],  # Rennen mit RB-Taste

            # Schultertasten
            "trigger_left": [(0, AXIS_TRIGGERLEFT, AXIS_DEADZONE)],  # Linker Trigger
            "fast_forward": [(0, BUTTON_LEFTSHOULDER, 1)],  # Vorspulen mit LB-Taste
            "trigger_right": [(0, AXIS_TRIGGERRIGHT, AXIS_DEADZONE)],  # Rechter Trigger

            # Stick-Buttons
            "stick_left": [(0, BUTTON_LEFTSTICK, 1)],  # Linker Stick-Button
            "stick_right": [(0, BUTTON_RIGHTSTICK, 1)],  # Rechter Stick-Button

            # Rechter Stick
            "camera_up": [(0, AXIS_RIGHTY, -AXIS_DEADZONE)],  # Kamera nach oben
            "camera_down": [(0, AXIS_RIGHTY, AXIS_DEADZONE)],  # Kamera nach unten
            "camera_left": [(0, AXIS_RIGHTX, -AXIS_DEADZONE)],  # Kamera nach links
            "camera_right": [(0, AXIS_RIGHTX, AXIS_DEADZONE)]  # Kamera nach rechts
        }

        # Aktueller Zustand der Eingaben
        self.input_state = {
            # Bewegung
            "up": False,
            "down": False,
            "left": False,
            "right": False,

            # Aktionen
            "action": False,
            "cancel": False,
            "menu": False,
            "secondary": False,
            "tertiary": False,
            "run": False,
            "fast_forward": False,

            # Schultertasten
            "shoulder_left": False,
            "shoulder_right": False,
            "trigger_left": False,
            "trigger_right": False,

            # Stick-Buttons
            "stick_left": False,
            "stick_right": False,

            # Kamera (rechter Stick)
            "camera_up": False,
            "camera_down": False,
            "camera_left": False,
            "camera_right": False
        }

        # Vorheriger Zustand der Eingaben (für was_pressed und was_released)
        self.prev_input_state = {k: False for k in self.input_state}

        # Controller-Initialisierung
        self.controllers = []
        self.init_controllers()

    def init_controllers(self):
        """Initialisiert alle verfügbaren Controller"""
        pygame.joystick.init()

        # Alte Controller entfernen
        self.controllers = []

        # Neue Controller hinzufügen
        for i in range(pygame.joystick.get_count()):
            try:
                controller = pygame.joystick.Joystick(i)
                controller.init()
                self.controllers.append(controller)
                self.logger.info(f"Controller gefunden: {controller.get_name()}")
            except pygame.error as e:
                self.logger.error(f"Fehler beim Initialisieren des Controllers {i}: {e}")

        if not self.controllers:
            self.logger.info("Keine Controller gefunden")

    def update(self):
        """Aktualisiert den Zustand der Eingaben"""
        # Vorherigen Zustand speichern
        self.prev_input_state = {k: v for k, v in self.input_state.items()}

        # Zustand zurücksetzen
        for key in self.input_state:
            self.input_state[key] = False

        # Tastatureingaben verarbeiten
        keys = pygame.key.get_pressed()
        for action, key_list in self.keyboard_config.items():
            for key in key_list:
                if keys[key]:
                    self.input_state[action] = True
                    break

        # Controller-Eingaben verarbeiten
        for controller_idx, controller in enumerate(self.controllers):
            # Achsen und Buttons verarbeiten
            for action, input_list in self.controller_config.items():
                for input_config in input_list:
                    if len(input_config) == 3 and input_config[0] == controller_idx:
                        # Prüfen, ob es sich um eine Achse oder einen Button handelt
                        if input_config[1] in [AXIS_LEFTX, AXIS_LEFTY, AXIS_RIGHTX, AXIS_RIGHTY, AXIS_TRIGGERLEFT, AXIS_TRIGGERRIGHT]:  # Achse
                            try:
                                axis_value = controller.get_axis(input_config[1])
                                if (input_config[2] < 0 and axis_value < input_config[2]) or \
                                   (input_config[2] > 0 and axis_value > input_config[2]):
                                    self.input_state[action] = True
                                    break
                            except pygame.error:
                                # Ungültige Achse, ignorieren
                                pass
                        else:  # Knopf
                            try:
                                # Prüfen, ob es sich um einen D-Pad-Button handelt
                                if input_config[1] in [BUTTON_DPAD_UP, BUTTON_DPAD_DOWN, BUTTON_DPAD_LEFT, BUTTON_DPAD_RIGHT]:
                                    # D-Pad-Buttons werden über das Hat-Interface abgefragt
                                    # Diese werden bereits in einem separaten Block behandelt
                                    pass
                                else:
                                    # Normale Buttons (A, B, X, Y, etc.)
                                    button_state = controller.get_button(input_config[1])

                                    # Direkte Zuweisung für bestimmte Tasten
                                    if button_state:
                                        # A-Taste
                                        if input_config[1] == BUTTON_A:
                                            self.logger.info(f"A-Taste gedrückt! (Button {input_config[1]})")
                                            self.input_state["action"] = True
                                        # B-Taste
                                        elif input_config[1] == BUTTON_B:
                                            self.logger.info(f"B-Taste gedrückt! (Button {input_config[1]})")
                                            self.input_state["cancel"] = True
                                        # Start-Taste
                                        elif input_config[1] == BUTTON_START:
                                            self.logger.info(f"Start-Taste gedrückt! (Button {input_config[1]})")
                                            self.input_state["menu"] = True
                                        # LB-Taste
                                        elif input_config[1] == BUTTON_LEFTSHOULDER:
                                            self.logger.info(f"LB-Taste gedrückt! (Button {input_config[1]})")
                                            self.input_state["fast_forward"] = True
                                        # RB-Taste
                                        elif input_config[1] == BUTTON_RIGHTSHOULDER:
                                            self.logger.info(f"RB-Taste gedrückt! (Button {input_config[1]})")
                                            self.input_state["run"] = True
                                        # Normale Verarbeitung für andere Tasten
                                        else:
                                            self.input_state[action] = True
                                            self.logger.info(f"Controller-Button erkannt: {action} (Button {input_config[1]})")
                                    # Normale Verarbeitung für andere Tasten
                                    elif button_state:
                                        self.input_state[action] = True
                                        # Debug-Logging für alle Buttons
                                        self.logger.info(f"Controller-Button erkannt: {action} (Button {input_config[1]})")
                                        break
                            except pygame.error:
                                # Ungültiger Button, ignorieren
                                pass

            # D-Pad (Hat) verarbeiten
            try:
                if controller.get_numhats() > 0:
                    hat_value = controller.get_hat(0)  # Normalerweise hat ein Controller nur ein Hat (D-Pad)

                    # Hat-Werte: (x, y) wobei x: -1 (links), 0 (mittig), 1 (rechts) und y: -1 (unten), 0 (mittig), 1 (oben)
                    if hat_value[0] < 0:  # Links
                        self.input_state["left"] = True
                    elif hat_value[0] > 0:  # Rechts
                        self.input_state["right"] = True

                    if hat_value[1] < 0:  # Unten
                        self.input_state["down"] = True
                    elif hat_value[1] > 0:  # Oben
                        self.input_state["up"] = True
            except pygame.error:
                # Fehler beim Zugriff auf Hat, ignorieren
                pass

    def is_pressed(self, action: str) -> bool:
        """Prüft, ob eine Aktion gerade gedrückt wird

        Args:
            action: Name der Aktion

        Returns:
            bool: True, wenn die Aktion gedrückt wird
        """
        # Direkte Prüfung für bestimmte Aktionen
        if action == "run":
            # Prüfen, ob ein Controller angeschlossen ist
            if self.controllers and len(self.controllers) > 0:
                controller = self.controllers[0]
                try:
                    # RB-Taste direkt prüfen
                    from game.core.controller_constants import BUTTON_RIGHTSHOULDER
                    if controller.get_button(BUTTON_RIGHTSHOULDER):
                        self.logger.info("RB-Taste direkt erkannt für Rennen!")
                        return True
                except Exception as e:
                    self.logger.error(f"Fehler bei der Controller-Prüfung für Rennen: {e}")

        elif action == "fast_forward":
            # Prüfen, ob ein Controller angeschlossen ist
            if self.controllers and len(self.controllers) > 0:
                controller = self.controllers[0]
                try:
                    # LB-Taste direkt prüfen
                    from game.core.controller_constants import BUTTON_LEFTSHOULDER
                    if controller.get_button(BUTTON_LEFTSHOULDER):
                        self.logger.info("LB-Taste direkt erkannt für Vorspulen!")
                        return True
                except Exception as e:
                    self.logger.error(f"Fehler bei der Controller-Prüfung für Vorspulen: {e}")

        # Normale Prüfung für alle anderen Aktionen
        result = self.input_state.get(action, False)
        if result and (action == "run" or action == "fast_forward"):
            self.logger.info(f"Aktion {action} erkannt über input_state!")
        return result

    def was_pressed(self, action: str) -> bool:
        """Prüft, ob eine Aktion in diesem Frame gedrückt wurde

        Args:
            action: Name der Aktion

        Returns:
            bool: True, wenn die Aktion in diesem Frame gedrückt wurde
        """
        # Normale Prüfung für alle Aktionen
        result = self.input_state.get(action, False) and not self.prev_input_state.get(action, False)
        if result:
            self.logger.info(f"Aktion erkannt: {action} (input_state: {self.input_state.get(action)}, prev_input_state: {self.prev_input_state.get(action)})")
        return result

    def was_released(self, action: str) -> bool:
        """Prüft, ob eine Aktion in diesem Frame losgelassen wurde

        Args:
            action: Name der Aktion

        Returns:
            bool: True, wenn die Aktion in diesem Frame losgelassen wurde
        """
        return not self.input_state.get(action, False) and self.prev_input_state.get(action, False)

    def get_movement(self) -> Tuple[int, int]:
        """Gibt die aktuelle Bewegungsrichtung zurück

        Returns:
            Tuple[int, int]: (x, y) Bewegungsvektor, wobei jede Komponente -1, 0 oder 1 ist
        """
        x = 0
        y = 0

        # Nur Bewegungseingaben berücksichtigen (links, rechts, oben, unten)
        # Andere Tasten (A, B, X, Y, etc.) werden nicht für die Bewegung verwendet
        if self.is_pressed("left"):
            x -= 1
        if self.is_pressed("right"):
            x += 1
        if self.is_pressed("up"):
            y -= 1
        if self.is_pressed("down"):
            y += 1

        return (x, y)

    def handle_events(self, events: List[pygame.event.Event]):
        """Verarbeitet pygame-Events

        Args:
            events: Liste von pygame-Events
        """
        for event in events:
            # Controller-Events
            if event.type == pygame.JOYDEVICEADDED:
                self.init_controllers()
            elif event.type == pygame.JOYDEVICEREMOVED:
                self.init_controllers()

    def debug_controller(self, controller_idx: int = 0) -> Dict[str, Any]:
        """Gibt Debug-Informationen über einen Controller zurück

        Args:
            controller_idx: Index des Controllers

        Returns:
            Dict[str, Any]: Debug-Informationen über den Controller
        """
        if controller_idx >= len(self.controllers):
            return {"error": f"Controller mit Index {controller_idx} nicht gefunden"}

        controller = self.controllers[controller_idx]

        # Buttons
        buttons = {}
        try:
            for i in range(controller.get_numbuttons()):
                buttons[f"button_{i}"] = controller.get_button(i)
        except pygame.error:
            buttons["error"] = "Fehler beim Zugriff auf Buttons"

        # Achsen
        axes = {}
        try:
            for i in range(controller.get_numaxes()):
                try:
                    axes[f"axis_{i}"] = controller.get_axis(i)
                except pygame.error:
                    axes[f"axis_{i}"] = "Fehler"
        except pygame.error:
            axes["error"] = "Fehler beim Zugriff auf Achsen"

        # Hats (D-Pad)
        hats = {}
        try:
            for i in range(controller.get_numhats()):
                try:
                    hats[f"hat_{i}"] = controller.get_hat(i)
                except pygame.error:
                    hats[f"hat_{i}"] = "Fehler"
        except pygame.error:
            hats["error"] = "Fehler beim Zugriff auf Hats"

        return {
            "name": controller.get_name(),
            "id": controller.get_id(),
            "buttons": buttons,
            "axes": axes,
            "hats": hats
        }
