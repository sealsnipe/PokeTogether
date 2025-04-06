#!/usr/bin/env python
"""
InputManager - Verwaltet die Eingaben des Spielers
"""

import logging
import pygame
from typing import Dict, List, Tuple, Callable, Any, Optional
from enum import Enum, auto
from game.core.controller_constants import *


class InputAction(Enum):
    """Enum für die verschiedenen Eingabeaktionen"""
    # Bewegung
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    # Aktionen
    ACTION = auto()
    CANCEL = auto()
    MENU = auto()
    SECONDARY = auto()
    TERTIARY = auto()
    RUN = auto()
    FAST_FORWARD = auto()
    CHAT = auto()  # Chat öffnen/schließen

    # Emotes
    EMOTE_1 = auto()  # Winken
    EMOTE_2 = auto()  # Lächeln
    EMOTE_3 = auto()  # Daumen hoch

    # Schultertasten
    SHOULDER_LEFT = auto()
    SHOULDER_RIGHT = auto()
    TRIGGER_LEFT = auto()
    TRIGGER_RIGHT = auto()

    # Stick-Buttons
    STICK_LEFT = auto()
    STICK_RIGHT = auto()

    # Kamera (rechter Stick)
    CAMERA_UP = auto()
    CAMERA_DOWN = auto()
    CAMERA_LEFT = auto()
    CAMERA_RIGHT = auto()


class InputManager:
    """Verwaltet die Eingaben des Spielers"""

    def __init__(self):
        """Initialisiert den InputManager"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing InputManager")

        # Tastatur-Konfiguration
        self.keyboard_config: Dict[InputAction, List[int]] = {
            # Bewegung
            InputAction.UP: [pygame.K_UP, pygame.K_w],
            InputAction.DOWN: [pygame.K_DOWN, pygame.K_s],
            InputAction.LEFT: [pygame.K_LEFT, pygame.K_a],
            InputAction.RIGHT: [pygame.K_RIGHT, pygame.K_d],

            # Aktionen
            InputAction.ACTION: [pygame.K_RETURN, pygame.K_z, pygame.K_SPACE],
            InputAction.CANCEL: [pygame.K_ESCAPE, pygame.K_x, pygame.K_BACKSPACE],
            InputAction.MENU: [pygame.K_ESCAPE, pygame.K_TAB],
            InputAction.SECONDARY: [pygame.K_LSHIFT, pygame.K_RSHIFT],
            InputAction.TERTIARY: [pygame.K_LCTRL, pygame.K_RCTRL],
            InputAction.RUN: [pygame.K_LSHIFT, pygame.K_RSHIFT],
            InputAction.FAST_FORWARD: [pygame.K_f],
            InputAction.CHAT: [pygame.K_t, pygame.K_y],

            # Emotes
            InputAction.EMOTE_1: [pygame.K_1],  # Winken
            InputAction.EMOTE_2: [pygame.K_2],  # Lächeln
            InputAction.EMOTE_3: [pygame.K_3],  # Daumen hoch
        }

        # Controller-Konfiguration
        self.controller_config: Dict[InputAction, List[Tuple[int, int, float]]] = {
            # Bewegung (linker Stick)
            InputAction.UP: [(0, AXIS_LEFTY, -0.5)],
            InputAction.DOWN: [(0, AXIS_LEFTY, 0.5)],
            InputAction.LEFT: [(0, AXIS_LEFTX, -0.5)],
            InputAction.RIGHT: [(0, AXIS_LEFTX, 0.5)],

            # Aktionen
            InputAction.ACTION: [(0, BUTTON_A, 1)],
            InputAction.CANCEL: [(0, BUTTON_B, 1)],
            InputAction.MENU: [(0, BUTTON_START, 1)],
            InputAction.SECONDARY: [(0, BUTTON_X, 1)],
            InputAction.TERTIARY: [(0, BUTTON_Y, 1)],
            InputAction.RUN: [(0, BUTTON_RIGHTSHOULDER, 1)],
            InputAction.FAST_FORWARD: [(0, BUTTON_LEFTSHOULDER, 1)],
            InputAction.CHAT: [(0, BUTTON_BACK, 1)],  # Back/Select-Button für Chat

            # Emotes (D-Pad)
            InputAction.EMOTE_1: [(0, BUTTON_DPAD_UP, 1)],    # Winken
            InputAction.EMOTE_2: [(0, BUTTON_DPAD_RIGHT, 1)], # Lächeln
            InputAction.EMOTE_3: [(0, BUTTON_DPAD_DOWN, 1)],  # Daumen hoch

            # Schultertasten
            InputAction.SHOULDER_LEFT: [(0, BUTTON_LEFTSHOULDER, 1)],
            InputAction.SHOULDER_RIGHT: [(0, BUTTON_RIGHTSHOULDER, 1)],
            InputAction.TRIGGER_LEFT: [(0, AXIS_TRIGGERLEFT, 0.5)],
            InputAction.TRIGGER_RIGHT: [(0, AXIS_TRIGGERRIGHT, 0.5)],

            # Stick-Buttons
            InputAction.STICK_LEFT: [(0, BUTTON_LEFTSTICK, 1)],
            InputAction.STICK_RIGHT: [(0, BUTTON_RIGHTSTICK, 1)],

            # Kamera (rechter Stick)
            InputAction.CAMERA_UP: [(0, AXIS_RIGHTY, -0.5)],
            InputAction.CAMERA_DOWN: [(0, AXIS_RIGHTY, 0.5)],
            InputAction.CAMERA_LEFT: [(0, AXIS_RIGHTX, -0.5)],
            InputAction.CAMERA_RIGHT: [(0, AXIS_RIGHTX, 0.5)],
        }

        # Aktueller Zustand der Eingaben
        self.input_state: Dict[InputAction, bool] = {action: False for action in InputAction}

        # Vorheriger Zustand der Eingaben (für was_pressed und was_released)
        self.prev_input_state: Dict[InputAction, bool] = {action: False for action in InputAction}

        # Controller-Initialisierung
        self.controllers = []
        self.init_controllers()

        # Callbacks für Eingabeaktionen
        self.action_callbacks: Dict[InputAction, List[Callable]] = {action: [] for action in InputAction}

    def init_controllers(self) -> None:
        """Initialisiert die Controller"""
        pygame.joystick.init()

        # Alle angeschlossenen Controller initialisieren
        self.controllers = []
        for i in range(pygame.joystick.get_count()):
            try:
                controller = pygame.joystick.Joystick(i)
                controller.init()
                self.controllers.append(controller)
                self.logger.info(f"Controller {i} initialized: {controller.get_name()}")
            except pygame.error as e:
                self.logger.error(f"Error initializing controller {i}: {e}")

    def update(self) -> None:
        """Aktualisiert den Zustand der Eingaben"""
        # Vorherigen Zustand speichern
        self.prev_input_state = {k: v for k, v in self.input_state.items()}

        # Zustand zurücksetzen
        for action in InputAction:
            self.input_state[action] = False

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
                                if controller.get_button(input_config[1]):
                                    self.input_state[action] = True
                                    break
                            except pygame.error:
                                # Ungültiger Knopf, ignorieren
                                pass

        # Callbacks für gedrückte Aktionen aufrufen
        for action in InputAction:
            if self.was_pressed(action):
                for callback in self.action_callbacks[action]:
                    callback()

    def is_pressed(self, action: InputAction) -> bool:
        """Prüft, ob eine Aktion aktuell gedrückt ist

        Args:
            action: Die zu prüfende Aktion

        Returns:
            bool: True, wenn die Aktion aktuell gedrückt ist
        """
        return self.input_state.get(action, False)

    def was_pressed(self, action: InputAction) -> bool:
        """Prüft, ob eine Aktion in diesem Frame gedrückt wurde

        Args:
            action: Die zu prüfende Aktion

        Returns:
            bool: True, wenn die Aktion in diesem Frame gedrückt wurde
        """
        return self.input_state.get(action, False) and not self.prev_input_state.get(action, False)

    def was_released(self, action: InputAction) -> bool:
        """Prüft, ob eine Aktion in diesem Frame losgelassen wurde

        Args:
            action: Die zu prüfende Aktion

        Returns:
            bool: True, wenn die Aktion in diesem Frame losgelassen wurde
        """
        return not self.input_state.get(action, False) and self.prev_input_state.get(action, False)

    def register_action_callback(self, action: InputAction, callback: Callable) -> None:
        """Registriert einen Callback für eine Eingabeaktion

        Args:
            action: Die Aktion, für die der Callback registriert werden soll
            callback: Die Funktion, die aufgerufen werden soll
        """
        self.action_callbacks[action].append(callback)

    def unregister_action_callback(self, action: InputAction, callback: Callable) -> None:
        """Entfernt einen Callback für eine Eingabeaktion

        Args:
            action: Die Aktion, für die der Callback entfernt werden soll
            callback: Die Funktion, die entfernt werden soll
        """
        if callback in self.action_callbacks[action]:
            self.action_callbacks[action].remove(callback)

    def reset(self) -> None:
        """Setzt den Eingabezustand zurück"""
        for action in InputAction:
            self.input_state[action] = False
            self.prev_input_state[action] = False
