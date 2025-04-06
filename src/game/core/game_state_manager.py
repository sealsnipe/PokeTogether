#!/usr/bin/env python
"""
GameStateManager - Verwaltet die verschiedenen Spielzustände
"""

import logging
from enum import Enum, auto
from typing import Dict, Any, Callable, Optional


class GameState(Enum):
    """Enum für die verschiedenen Spielzustände"""
    MAIN_MENU = auto()
    PLAYING = auto()
    BATTLE = auto()
    PAUSE = auto()
    OPTIONS = auto()
    INGAME_MENU = auto()
    MULTIPLAYER_MENU = auto()
    INPUT_DIALOG = auto()


class GameStateManager:
    """Verwaltet die verschiedenen Spielzustände und Übergänge zwischen ihnen"""

    def __init__(self, initial_state: GameState = GameState.MAIN_MENU):
        """Initialisiert den GameStateManager

        Args:
            initial_state: Der anfängliche Spielzustand
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing GameStateManager")

        self.current_state = initial_state
        self.previous_state = None

        # State-spezifische Daten
        self.state_data: Dict[GameState, Dict[str, Any]] = {
            state: {} for state in GameState
        }

        # Callbacks für State-Änderungen
        self.on_state_changed: Dict[GameState, Callable] = {}

        # Input-Dialog-Variablen (für INPUT_DIALOG-State)
        self.input_dialog_text = ""
        self.input_dialog_title = ""
        self.input_dialog_callback = None

    def change_state(self, new_state: GameState) -> None:
        """Wechselt zu einem neuen Spielzustand

        Args:
            new_state: Der neue Spielzustand
        """
        if new_state == self.current_state:
            return

        self.logger.info(f"Changing game state from {self.current_state} to {new_state}")
        self.previous_state = self.current_state
        self.current_state = new_state

        # Callback für State-Änderung aufrufen, falls vorhanden
        if new_state in self.on_state_changed and self.on_state_changed[new_state]:
            self.on_state_changed[new_state]()

    def register_state_changed_callback(self, state: GameState, callback: Callable) -> None:
        """Registriert einen Callback für eine State-Änderung

        Args:
            state: Der Spielzustand, für den der Callback registriert werden soll
            callback: Die Funktion, die aufgerufen werden soll
        """
        self.on_state_changed[state] = callback

    def get_state_data(self, state: GameState) -> Dict[str, Any]:
        """Gibt die Daten für einen bestimmten Spielzustand zurück

        Args:
            state: Der Spielzustand, für den die Daten zurückgegeben werden sollen

        Returns:
            Die Daten für den angegebenen Spielzustand
        """
        return self.state_data[state]

    def set_state_data(self, state: GameState, key: str, value: Any) -> None:
        """Setzt ein Datenelement für einen bestimmten Spielzustand

        Args:
            state: Der Spielzustand, für den das Datenelement gesetzt werden soll
            key: Der Schlüssel des Datenelements
            value: Der Wert des Datenelements
        """
        self.state_data[state][key] = value

    def return_to_previous_state(self) -> None:
        """Kehrt zum vorherigen Spielzustand zurück"""
        if self.previous_state:
            self.change_state(self.previous_state)
        else:
            self.logger.warning("No previous state to return to")

    def setup_input_dialog(self, title: str, default_text: str, callback: Callable[[str], None]) -> None:
        """Richtet einen Eingabedialog ein und wechselt zum INPUT_DIALOG-State

        Args:
            title: Der Titel des Dialogs
            default_text: Der Standardtext im Eingabefeld
            callback: Die Funktion, die aufgerufen wird, wenn der Dialog bestätigt wird
        """
        self.logger.info(f"Setting up input dialog: {title}")
        self.input_dialog_title = title
        self.input_dialog_text = default_text
        self.input_dialog_callback = callback

        # Zum INPUT_DIALOG-State wechseln
        self.change_state(GameState.INPUT_DIALOG)

    def confirm_input_dialog(self) -> None:
        """Bestätigt den Eingabedialog und ruft den Callback auf"""
        if self.current_state == GameState.INPUT_DIALOG and self.input_dialog_callback:
            self.logger.info(f"Confirming input dialog with text: {self.input_dialog_text}")
            callback = self.input_dialog_callback
            text = self.input_dialog_text

            # Tastaturwiederholung deaktivieren
            import pygame
            pygame.key.set_repeat()

            # Zurück zum vorherigen State wechseln
            self.return_to_previous_state()

            # Callback aufrufen
            callback(text)
        else:
            self.logger.warning("Cannot confirm input dialog: not in INPUT_DIALOG state or no callback registered")

    def cancel_input_dialog(self) -> None:
        """Bricht den Eingabedialog ab und kehrt zum vorherigen State zurück"""
        if self.current_state == GameState.INPUT_DIALOG:
            self.logger.info("Canceling input dialog")

            # Tastaturwiederholung deaktivieren
            import pygame
            pygame.key.set_repeat()

            self.return_to_previous_state()
        else:
            self.logger.warning("Cannot cancel input dialog: not in INPUT_DIALOG state")

    def add_character_to_input_dialog(self, char: str) -> None:
        """Fügt ein Zeichen zum Eingabedialog hinzu

        Args:
            char: Das hinzuzufügende Zeichen
        """
        if self.current_state == GameState.INPUT_DIALOG:
            self.input_dialog_text += char
            self.logger.info(f"Character added: {char}, text now: {self.input_dialog_text}")
        else:
            self.logger.warning("Cannot add character to input dialog: not in INPUT_DIALOG state")

    def remove_character_from_input_dialog(self) -> None:
        """Entfernt das letzte Zeichen aus dem Eingabedialog"""
        if self.current_state == GameState.INPUT_DIALOG:
            if self.input_dialog_text:
                self.input_dialog_text = self.input_dialog_text[:-1]
                self.logger.info(f"Character removed, text now: {self.input_dialog_text}")
            else:
                self.logger.debug("Cannot remove character: text is already empty")
        else:
            self.logger.warning("Cannot remove character from input dialog: not in INPUT_DIALOG state")
