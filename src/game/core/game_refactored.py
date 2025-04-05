#!/usr/bin/env python
"""
Game class - Main game loop and state management (refactored version)
"""

import pygame
import sys
import json
import logging
import os
import time
from typing import Dict, List, Tuple, Callable, Any, Optional

from game.core.game_state_manager import GameStateManager, GameState
from game.core.render_manager import RenderManager
from game.core.input_manager import InputManager, InputAction
from game.core.input_command_reader import InputCommandReader
from game.entities.player import Player
from game.core.camera import Camera
from game.maps.simple_map import SimpleMap
from game.core.settings import Settings
from game.core.config import Config
from game.ui.main_menu_refactored import MainMenuRefactored
from game.ui.options_menu_refactored import OptionsMenuRefactored
from game.ui.ingame_menu_refactored import IngameMenuRefactored
from game.network.multiplayer_manager import MultiplayerManager


class Game:
    """Main game class (refactored version)"""

    def __init__(self, config: Config = None, minimized: bool = False):
        """Initialize the game

        Args:
            config: Konfigurationsobjekt
            minimized: Wenn True, wird das Spiel minimiert gestartet
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game")

        # Konfiguration speichern oder Standardkonfiguration erstellen
        self.config = config if config else Config()
        self.logger.info(f"Using configuration with player name: {self.config.get_player_name()}")

        # Minimiert-Flag speichern
        self.minimized = minimized

        # Pygame initialisieren
        pygame.init()

        # Fenster erstellen
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(self.config.get_window_title() + (" (Test Mode)" if minimized else ""))

        # Fenster minimieren, wenn gewünscht
        if minimized:
            self._minimize_window()

        # Spiel-Clock
        self.clock = pygame.time.Clock()
        self.running = True

        # Manager initialisieren
        self.state_manager = GameStateManager(GameState.MAIN_MENU)
        self.render_manager = RenderManager(self.screen, self.state_manager)
        self.input_manager = InputManager()

        # Input-Command-Reader für autonomes Testen
        self.input_command_reader = InputCommandReader()

        # Multiplayer
        self.multiplayer_manager = MultiplayerManager()
        self.other_players = {}
        self.interpolated_players = {}  # Für Interpolation
        self.multiplayer_active = False
        self.force_player_data_update = True  # Beim ersten Mal immer senden

        # Screenshots
        self.screenshots_enabled = False
        self.screenshot_interval = 5.0  # Sekunden zwischen automatischen Screenshots
        self.last_screenshot_time = 0.0

        # Game resources
        self.resources = {}

        # Settings
        self.settings = Settings()

        # Karte - Dynamische Größe basierend auf der Bildschirmauflösung
        screen_width, screen_height = self.screen.get_size()
        tile_size = 32  # Größere Tiles für bessere Sichtbarkeit

        # Berechne die Anzahl der Tiles basierend auf der Bildschirmgröße
        # Füge ein paar zusätzliche Tiles hinzu, damit die Karte größer als der Bildschirm ist
        map_width = screen_width // tile_size + 10
        map_height = screen_height // tile_size + 10

        self.current_map = SimpleMap(map_width, map_height, tile_size)

        # Spieler - Starte in der Mitte der Karte mit dem Namen aus der Konfiguration
        player_name = self.config.get_player_name()
        player_character = self.config.get("player", "character")
        self.player = Player(self.current_map.pixel_width // 2, self.current_map.pixel_height // 2, player_character)
        self.player.name = player_name

        # Kamera - Verwende die aktuelle Bildschirmgröße für die Kamera
        # Zoom-Faktor von 1.2 bedeutet 20% herausgezoomt
        self.camera = Camera(screen_width, screen_height, self.current_map.pixel_width, self.current_map.pixel_height, zoom_factor=1.2)

        # UI-Elemente initialisieren
        self._init_ui()

        # Render-Funktionen registrieren
        self._register_render_functions()

        # Input-Callbacks registrieren
        self._register_input_callbacks()

        # State-Callbacks registrieren
        self._register_state_callbacks()

        # Multiplayer-Callbacks registrieren
        self._register_multiplayer_callbacks()

        # Hauptmenü anzeigen
        self.main_menu.show()

    def _minimize_window(self) -> None:
        """Minimiert das Spielfenster (nur unter Windows)"""
        self.logger.info("Minimierter Modus aktiviert - Fenster wird minimiert")

        try:
            import ctypes
            import win32con
            import win32gui

            # Pygame-Fenster-Handle bekommen
            hwnd = pygame.display.get_wm_info()["window"]

            # Fenster minimieren
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

            # Speichere das Fenster-Handle für spätere Verwendung
            self.window_handle = hwnd

            self.logger.info("Fenster erfolgreich minimiert")
        except Exception as e:
            self.logger.error(f"Fehler beim Minimieren des Fensters: {e}")

    def _init_ui(self) -> None:
        """Initialisiert die UI-Elemente"""
        # Hauptmenü
        self.main_menu = MainMenuRefactored(self)

        # Optionsmenü
        self.options_menu = OptionsMenuRefactored(self)

        # Ingame-Menü
        self.ingame_menu = IngameMenuRefactored(self)

    def _register_render_functions(self) -> None:
        """Registriert die Render-Funktionen für die verschiedenen Spielzustände"""
        self.render_manager.register_render_function(GameState.MAIN_MENU, self._render_main_menu)
        self.render_manager.register_render_function(GameState.PLAYING, self._render_playing)
        self.render_manager.register_render_function(GameState.BATTLE, self._render_battle)
        self.render_manager.register_render_function(GameState.PAUSE, self._render_pause)
        self.render_manager.register_render_function(GameState.OPTIONS, self._render_options)
        self.render_manager.register_render_function(GameState.INGAME_MENU, self._render_ingame_menu)
        self.render_manager.register_render_function(GameState.INPUT_DIALOG, self._render_input_dialog)

    def _register_input_callbacks(self) -> None:
        """Registriert die Input-Callbacks"""
        # Menü-Steuerung
        self.input_manager.register_action_callback(InputAction.MENU, self._toggle_menu)

        # Eingabedialog-Steuerung
        self.input_manager.register_action_callback(InputAction.ACTION, self._confirm_dialog)
        self.input_manager.register_action_callback(InputAction.CANCEL, self._cancel_dialog)

    def _register_state_callbacks(self) -> None:
        """Registriert die State-Callbacks"""
        self.state_manager.register_state_changed_callback(GameState.PLAYING, self._on_enter_playing)
        self.state_manager.register_state_changed_callback(GameState.MAIN_MENU, self._on_enter_main_menu)
        self.state_manager.register_state_changed_callback(GameState.INGAME_MENU, self._on_enter_ingame_menu)

    def _register_multiplayer_callbacks(self) -> None:
        """Registriert die Multiplayer-Callbacks"""
        self.logger.info("[DATENFLUSS] REGISTERING MULTIPLAYER CALLBACKS")

        # Prüfen, ob die Methoden existieren
        if not hasattr(self.multiplayer_manager, "on_player_update"):
            self.logger.error("[DATENFLUSS] MULTIPLAYER_MANAGER HAS NO ATTRIBUTE 'on_player_update'")
        else:
            self.logger.info("[DATENFLUSS] MULTIPLAYER_MANAGER HAS ATTRIBUTE 'on_player_update'")

        if not hasattr(self, "_on_player_update"):
            self.logger.error("[DATENFLUSS] GAME HAS NO METHOD '_on_player_update'")
        else:
            self.logger.info("[DATENFLUSS] GAME HAS METHOD '_on_player_update'")

        # Callbacks registrieren
        self.logger.info("[DATENFLUSS] REGISTERING CALLBACK: on_player_update = self._on_player_update")
        self.multiplayer_manager.on_player_update = self._on_player_update
        self.logger.info("[DATENFLUSS] CALLBACK REGISTERED: on_player_update")

        self.logger.info("[DATENFLUSS] REGISTERING CALLBACK: on_player_disconnected = self._on_player_disconnected")
        self.multiplayer_manager.on_player_disconnected = self._on_player_disconnected
        self.logger.info("[DATENFLUSS] CALLBACK REGISTERED: on_player_disconnected")

        self.logger.info("[DATENFLUSS] REGISTERING CALLBACK: on_chat_message = self._on_chat_message")
        self.multiplayer_manager.on_chat_message = self._on_chat_message
        self.logger.info("[DATENFLUSS] CALLBACK REGISTERED: on_chat_message")

        # Prüfen, ob die Callbacks korrekt registriert wurden
        if hasattr(self.multiplayer_manager, "on_player_update") and self.multiplayer_manager.on_player_update == self._on_player_update:
            self.logger.info("[DATENFLUSS] CALLBACK VERIFICATION: on_player_update is correctly registered")
        else:
            self.logger.error("[DATENFLUSS] CALLBACK VERIFICATION FAILED: on_player_update is not correctly registered")

        self.logger.info("[DATENFLUSS] MULTIPLAYER CALLBACKS REGISTERED SUCCESSFULLY")

    def _toggle_menu(self) -> None:
        """Öffnet oder schließt das Menü"""
        if self.state_manager.current_state == GameState.PLAYING:
            self.state_manager.change_state(GameState.INGAME_MENU)
        elif self.state_manager.current_state == GameState.INGAME_MENU:
            self.state_manager.change_state(GameState.PLAYING)

    def _confirm_dialog(self) -> None:
        """Bestätigt den aktuellen Dialog"""
        if self.state_manager.current_state == GameState.INPUT_DIALOG:
            self.state_manager.confirm_input_dialog()

    def _cancel_dialog(self) -> None:
        """Bricht den aktuellen Dialog ab"""
        if self.state_manager.current_state == GameState.INPUT_DIALOG:
            self.state_manager.cancel_input_dialog()

    def _on_enter_playing(self) -> None:
        """Wird aufgerufen, wenn der Spielzustand zu PLAYING wechselt"""
        self.logger.info("Entering PLAYING state")

    def _on_enter_main_menu(self) -> None:
        """Wird aufgerufen, wenn der Spielzustand zu MAIN_MENU wechselt"""
        self.logger.info("Entering MAIN_MENU state")
        self.main_menu.show()

    def _on_enter_ingame_menu(self) -> None:
        """Wird aufgerufen, wenn der Spielzustand zu INGAME_MENU wechselt"""
        self.logger.info("Entering INGAME_MENU state")
        self.ingame_menu.show()

    def handle_events(self) -> None:
        """Verarbeitet Pygame-Events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                # Eingabedialog-Steuerung
                if self.state_manager.current_state == GameState.INPUT_DIALOG:
                    self.logger.debug(f"Keydown event in INPUT_DIALOG state: {event.key}, unicode: {event.unicode}")
                    if event.key == pygame.K_RETURN:
                        self.logger.info("Enter key pressed, confirming dialog")
                        self.state_manager.confirm_input_dialog()
                    elif event.key == pygame.K_ESCAPE:
                        self.logger.info("Escape key pressed, canceling dialog")
                        self.state_manager.cancel_input_dialog()
                    elif event.key == pygame.K_BACKSPACE:
                        self.logger.info("Backspace key pressed")
                        self.state_manager.remove_character_from_input_dialog()
                        self.logger.info(f"Backspace pressed, text now: {self.state_manager.input_dialog_text}")
                    elif event.unicode and event.unicode.isprintable():
                        self.logger.info(f"Character key pressed: {event.unicode}")
                        self.state_manager.add_character_to_input_dialog(event.unicode)
                        self.logger.info(f"Character added: {event.unicode}, text now: {self.state_manager.input_dialog_text}")
                    # Verhindern, dass andere Teile des Spiels die Tastatureingaben verarbeiten
                    continue

    def update(self, dt: float) -> None:
        """Update game state

        Args:
            dt: Zeitdelta seit dem letzten Update in Sekunden
        """
        # Wenn im minimierten Modus, stelle sicher, dass das Fenster minimiert bleibt
        if hasattr(self, 'minimized') and self.minimized and hasattr(self, 'window_handle'):
            try:
                import win32gui
                import win32con
                if win32gui.IsWindowVisible(self.window_handle) and not win32gui.IsIconic(self.window_handle):
                    win32gui.ShowWindow(self.window_handle, win32con.SW_MINIMIZE)
            except Exception:
                pass  # Ignoriere Fehler beim erneuten Minimieren

        # Input-Manager aktualisieren
        self.input_manager.update()

        # Zustandsspezifische Updates
        if self.state_manager.current_state == GameState.PLAYING:
            self._update_playing(dt)
        elif self.state_manager.current_state == GameState.BATTLE:
            self._update_battle(dt)
        elif self.state_manager.current_state == GameState.MAIN_MENU:
            self._update_main_menu(dt)
        elif self.state_manager.current_state == GameState.INGAME_MENU:
            self._update_ingame_menu(dt)

    def _update_playing(self, dt: float) -> None:
        """Aktualisiert den Spielzustand im PLAYING-State

        Args:
            dt: Zeitdelta seit dem letzten Update in Sekunden
        """
        # Prüfen, ob das Ingame-Menü geöffnet werden soll
        if self.input_manager.was_pressed(InputAction.MENU):
            self.state_manager.change_state(GameState.INGAME_MENU)
            return

        # Direkte Prüfung der RB-Taste für Rennen
        run_pressed = False
        if self.input_manager.is_pressed(InputAction.RUN):
            run_pressed = True
            self.logger.debug("Run button pressed")

        # Prüfen, ob das Spiel beschleunigt werden soll
        fast_forward_pressed = self.input_manager.is_pressed(InputAction.FAST_FORWARD)

        # Spielgeschwindigkeit anpassen
        speed_multiplier = 1.0
        if run_pressed:
            speed_multiplier *= 2.0
        if fast_forward_pressed:
            speed_multiplier *= 3.0

        # Bewegungsrichtung bestimmen
        direction_x = 0
        direction_y = 0

        if self.input_manager.is_pressed(InputAction.UP):
            direction_y = -1
        elif self.input_manager.is_pressed(InputAction.DOWN):
            direction_y = 1

        if self.input_manager.is_pressed(InputAction.LEFT):
            direction_x = -1
        elif self.input_manager.is_pressed(InputAction.RIGHT):
            direction_x = 1

        # Spieler bewegen mit Client-Side Prediction
        if direction_x != 0 or direction_y != 0:
            # Verwende Client-Side Prediction, wenn aktiviert
            prediction = self.config.get_prediction()
            input_data = self.player.move(direction_x, direction_y, speed_multiplier, prediction)

            # Wenn im Multiplayer-Modus und eine signifikante Änderung vorliegt, erzwinge ein Update
            if self.multiplayer_active and (direction_x != 0 or direction_y != 0):
                self.force_player_data_update = True

        # Spieler aktualisieren
        self.player.update(dt)

        # Andere Spieler aktualisieren (Interpolation)
        if self.multiplayer_active and self.config.get_interpolation():
            for player_id, player_data in self.other_players.items():
                # Erstelle einen temporären Spieler für die Interpolation
                if player_id not in self.interpolated_players:
                    temp_player = Player()
                    temp_player.x = player_data.get("x", 0)
                    temp_player.y = player_data.get("y", 0)
                    temp_player.direction = player_data.get("direction", "down")
                    temp_player.name = player_data.get("name", "Player")
                    temp_player.character_type = player_data.get("character_type", "Red")
                    self.interpolated_players[player_id] = temp_player

                # Interpoliere die Position des Spielers
                self.interpolated_players[player_id].interpolate(player_data)

                # Aktualisiere die Spielerdaten mit den interpolierten Werten
                self.other_players[player_id]["x"] = self.interpolated_players[player_id].x
                self.other_players[player_id]["y"] = self.interpolated_players[player_id].y

        # Kamera aktualisieren
        self.camera.update(self.player.x, self.player.y)

        # Multiplayer-Aktualisierungen werden jetzt in der Hauptschleife mit Timer durchgeführt

    def _update_battle(self, dt: float) -> None:
        """Aktualisiert den Spielzustand im BATTLE-State

        Args:
            dt: Zeitdelta seit dem letzten Update in Sekunden
        """
        # TODO: Kampfsystem implementieren
        pass

    def _update_main_menu(self, dt: float) -> None:
        """Aktualisiert den Spielzustand im MAIN_MENU-State

        Args:
            dt: Zeitdelta seit dem letzten Update in Sekunden
        """
        self.main_menu.update()

    def _update_ingame_menu(self, dt: float) -> None:
        """Aktualisiert den Spielzustand im INGAME_MENU-State

        Args:
            dt: Zeitdelta seit dem letzten Update in Sekunden
        """
        self.ingame_menu.update()

    def _render_playing(self) -> None:
        """Rendert den Spielzustand im PLAYING-State"""
        # Hintergrund mit schwarzer Farbe füllen
        self.screen.fill((0, 0, 0))

        # Karte rendern
        self.current_map.render(self.screen, self.camera.get_offset())

        # Spieler rendern
        self.player.render(self.screen, self.camera.get_offset())

        # Andere Spieler rendern, wenn Multiplayer aktiv ist
        if self.multiplayer_active:
            self.logger.info(f"[INFO] Rendering other players. Active: {len(self.other_players)} players")
            self._render_other_players()

        # Debug-Informationen
        font = pygame.font.SysFont(None, 24)
        pos_text = font.render(f"Position: ({self.player.x}, {self.player.y})", True, (255, 255, 255))
        self.screen.blit(pos_text, (10, 10))

        dir_text = font.render(f"Richtung: {self.player.direction}", True, (255, 255, 255))
        self.screen.blit(dir_text, (10, 40))

    def _render_battle(self) -> None:
        """Rendert den Spielzustand im BATTLE-State"""
        # TODO: Kampfsystem implementieren
        self.screen.fill((0, 0, 100))

        font = pygame.font.SysFont(None, 36)
        text = font.render("Battle System (Not Implemented)", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, text_rect)

    def _render_main_menu(self) -> None:
        """Rendert den Spielzustand im MAIN_MENU-State"""
        self.main_menu.render(self.screen)

    def _render_pause(self) -> None:
        """Rendert den Spielzustand im PAUSE-State"""
        # Hintergrund abdunkeln
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(None, 36)
        text = font.render("Pause", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, text_rect)

    def _render_options(self) -> None:
        """Rendert den Spielzustand im OPTIONS-State"""
        self.options_menu.render(self.screen)

    def _render_ingame_menu(self) -> None:
        """Rendert den Spielzustand im INGAME_MENU-State"""
        self.ingame_menu.render(self.screen)

    def _render_input_dialog(self) -> None:
        """Rendert den Spielzustand im INPUT_DIALOG-State"""
        # Hintergrund abdunkeln
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Dialog rendern
        self.render_manager.render_input_dialog()

    def _render_other_players(self) -> None:
        """Rendert die anderen Spieler im Multiplayer-Modus"""
        # Prüfen, ob überhaupt andere Spieler vorhanden sind
        self.logger.info(f"[DATENFLUSS] RENDERING OTHER PLAYERS. Count: {len(self.other_players)}")
        self.logger.info(f"[DATENFLUSS] OTHER_PLAYERS CONTENT: {json.dumps(self.other_players)}")

        # Prüfen, ob die other_players Liste korrekt initialisiert wurde
        if not hasattr(self, 'other_players'):
            self.logger.error("[DATENFLUSS] OTHER_PLAYERS LIST NOT INITIALIZED")
            return

        # Prüfen, ob die other_players Liste ein Dictionary ist
        if not isinstance(self.other_players, dict):
            self.logger.error(f"[DATENFLUSS] OTHER_PLAYERS IS NOT A DICTIONARY: {type(self.other_players).__name__}")
            return

        if not self.other_players:
            self.logger.info("[DATENFLUSS] NO OTHER PLAYERS TO RENDER")
            return

        # Temporärer Font für Spielernamen
        font = pygame.font.SysFont(None, 18)

        for player_id, player_data in self.other_players.items():
            # Vollständige Spielerdaten loggen
            self.logger.info(f"[DATENFLUSS] RENDERING PLAYER: {player_id}, data={json.dumps(player_data)}")

            # Spielerdaten extrahieren
            x = player_data.get("x", 0)
            y = player_data.get("y", 0)
            name = player_data.get("name", "Player")
            character_type = player_data.get("character_type", "Red")
            direction = player_data.get("direction", "down")

            # Kamera-Offset anwenden
            offset = self.camera.get_offset()
            screen_x = int(x - offset[0])
            screen_y = int(y - offset[1])

            # Debug-Ausgabe für das Rendering
            self.logger.info(f"[DATENFLUSS] RENDERING PLAYER {name} (ID: {player_id}): x={x}, y={y}, screen_x={screen_x}, screen_y={screen_y}")

            # Prüfen, ob der Spieler im sichtbaren Bereich ist
            if (0 <= screen_x <= self.screen.get_width() and
                0 <= screen_y <= self.screen.get_height()):

                # Farbe basierend auf dem Charaktertyp wählen
                color = (0, 0, 255)  # Standard: Blau
                if character_type == "Blue":
                    color = (0, 0, 200)  # Dunkelblau
                elif character_type == "Red":
                    color = (200, 0, 0)  # Dunkelrot
                elif character_type == "Green":
                    color = (0, 200, 0)  # Dunkelgrün
                elif character_type == "Yellow":
                    color = (200, 200, 0)  # Gelb

                # Spieler als farbiges Rechteck darstellen
                player_rect = pygame.Rect(screen_x - 16, screen_y - 16, 32, 32)
                pygame.draw.rect(self.screen, color, player_rect)

                # Spielername anzeigen
                name_text = font.render(name, True, (255, 255, 255))
                self.screen.blit(name_text, (screen_x - name_text.get_width() // 2, screen_y - 30))

                # Richtungspfeil anzeigen
                arrow_color = (255, 255, 0)  # Gelb
                arrow_length = 20
                arrow_start = (player_rect.centerx, player_rect.centery)
                arrow_end = arrow_start

                if direction == "up":
                    arrow_end = (arrow_start[0], arrow_start[1] - arrow_length)
                elif direction == "down":
                    arrow_end = (arrow_start[0], arrow_start[1] + arrow_length)
                elif direction == "left":
                    arrow_end = (arrow_start[0] - arrow_length, arrow_start[1])
                elif direction == "right":
                    arrow_end = (arrow_start[0] + arrow_length, arrow_start[1])

                pygame.draw.line(self.screen, arrow_color, arrow_start, arrow_end, 2)

                # Debug-Informationen anzeigen
                if self.settings.get("debug", "show_player_info"):
                    debug_font = pygame.font.SysFont(None, 16)
                    debug_text = debug_font.render(
                        f"ID: {player_id[:8]}... Pos: ({x}, {y})",
                        True, (200, 200, 200)
                    )
                    debug_rect = debug_text.get_rect(center=(player_rect.centerx, player_rect.bottom + 15))
                    self.screen.blit(debug_text, debug_rect)

    def enable_screenshots(self) -> None:
        """Aktiviert automatische Screenshots"""
        self.logger.info("Enabling automatic screenshots")
        self.screenshots_enabled = True
        self.last_screenshot_time = time.time()

        # Sofort einen Screenshot machen, um zu bestätigen, dass es funktioniert
        self._take_screenshot("enabled")

    def _take_screenshot(self, action_name: str) -> None:
        """Erstellt einen Screenshot des aktuellen Spielzustands

        Args:
            action_name: Name der Aktion für den Dateinamen
        """
        try:
            # Stelle sicher, dass das Verzeichnis existiert
            screenshot_dir = self.config.get_screenshots_dir()
            os.makedirs(screenshot_dir, exist_ok=True)

            # Bestimme, ob dies eine Host- oder Client-Instanz ist
            instance_type = "single"
            if self.multiplayer_active:
                if self.multiplayer_manager.is_host:
                    instance_type = "host"
                else:
                    instance_type = "client"

            # Erstelle einen eindeutigen Dateinamen mit Instanztyp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{screenshot_dir}/test_{timestamp}_{instance_type}_{action_name}.png"

            # Füge Informationen zum Screenshot hinzu
            # - Spielerposition
            # - Multiplayer-Status
            # - Andere Spieler (falls vorhanden)
            font = pygame.font.SysFont(None, 24)

            # Kopie des Bildschirms erstellen, um Informationen hinzuzufügen
            screen_copy = self.screen.copy()

            # Informationen hinzufügen
            info_text = []
            info_text.append(f"Instance: {instance_type.upper()}")
            info_text.append(f"Player: {self.player.name} at ({self.player.x}, {self.player.y})")
            info_text.append(f"Multiplayer: {self.multiplayer_active}")

            if self.multiplayer_active and self.other_players:
                info_text.append(f"Other players: {len(self.other_players)}")
                for pid, pdata in self.other_players.items():
                    info_text.append(f"  - {pdata.get('name', 'Unknown')} at ({pdata.get('x', '?')}, {pdata.get('y', '?')})")

            # Text rendern und auf den Screenshot zeichnen
            y_offset = 10
            for text in info_text:
                text_surface = font.render(text, True, (255, 255, 255), (0, 0, 0))
                screen_copy.blit(text_surface, (10, y_offset))
                y_offset += 25

            # Screenshot mit Informationen speichern
            pygame.image.save(screen_copy, filename)
            self.logger.info(f"Screenshot erstellt: {filename}")
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Screenshots: {e}")

    def _process_automated_tests(self, dt: float) -> None:
        """Verarbeitet automatisierte Tests

        Args:
            dt: Zeitdelta seit dem letzten Update in Sekunden
        """
        # Verarbeite Eingabekommandos, wenn vorhanden
        if hasattr(self, 'automated_tests') and self.automated_tests:
            self.input_command_reader.process_commands(self.input_manager.input_state)

    def _send_player_data(self) -> None:
        """Sendet die Spielerdaten an den Server"""
        if not self.multiplayer_active:
            self.logger.debug("[DATENFLUSS] NOT SENDING PLAYER DATA: Multiplayer is not active")
            return

        # Prüfen, ob sich relevante Daten geändert haben
        if not self.player.has_significant_changes() and not self.force_player_data_update:
            self.logger.debug("[DATENFLUSS] NOT SENDING PLAYER DATA: No significant changes")
            return

        # Spielerdaten mit der to_network_data Methode sammeln
        player_data = self.player.to_network_data()
        self.logger.info(f"[DATENFLUSS] PLAYER DATA COLLECTED: {json.dumps(player_data)}")

        # Ausführlichere Log-Ausgabe für das Senden von Spielerdaten
        self.logger.info(f"[DATENFLUSS] SENDING PLAYER UPDATE: player_id={player_data.get('player_id')}, x={player_data.get('x')}, y={player_data.get('y')}, direction={player_data.get('direction')}")
        self.logger.debug(f"[DATENFLUSS] FULL PLAYER DATA: {json.dumps(player_data)}")

        # Prüfen, ob die Spielerdaten vollständig sind
        if not player_data.get('x') or not player_data.get('y') or not player_data.get('player_id'):
            self.logger.warning(f"[DATENFLUSS] INCOMPLETE PLAYER DATA: {json.dumps(player_data)}")
            return

        # Prüfen, ob die player_id korrekt gesetzt ist
        if player_data.get('player_id') != self.player.player_id:
            self.logger.warning(f"[DATENFLUSS] PLAYER ID MISMATCH: player_data.player_id={player_data.get('player_id')}, self.player.player_id={self.player.player_id}")

        # Daten an den Server senden
        self.logger.info(f"[DATENFLUSS] SENDING PLAYER DATA TO MULTIPLAYER MANAGER")
        self.multiplayer_manager.send_player_update(player_data)
        self.logger.info(f"[DATENFLUSS] PLAYER DATA SENT TO MULTIPLAYER MANAGER")

        # Aktualisiere die letzten gesendeten Daten
        self.player.update_last_sent_data()
        self.logger.debug(f"[DATENFLUSS] LAST SENT DATA UPDATED: position=({self.player.last_sent_position[0]}, {self.player.last_sent_position[1]}), direction={self.player.last_sent_direction}")

        # Zurücksetzen des Force-Flags
        self.force_player_data_update = False
        self.logger.debug(f"[DATENFLUSS] FORCE_PLAYER_DATA_UPDATE RESET: {self.force_player_data_update}")

    def _on_player_update(self, client_id: str, player_data: dict):
        """Callback für Spieler-Updates

        Args:
            client_id: Client-ID des Spielers
            player_data: Spielerdaten
        """
        # Vollständige Daten loggen
        self.logger.info(f"[DATENFLUSS] GAME RECEIVED PLAYER UPDATE: client_id={client_id}, player_data={json.dumps(player_data)}")

        # Prüfen, ob die Spielerdaten leer sind
        if not player_data:
            self.logger.warning(f"[DATENFLUSS] EMPTY PLAYER DATA RECEIVED FOR CLIENT: {client_id}")
            return

        # Ausführlichere Log-Ausgabe für Spieler-Updates
        self.logger.info(f"[DATENFLUSS] PLAYER UPDATE: Player {player_data.get('name', 'Unknown')}: x={player_data.get('x', '?')}, y={player_data.get('y', '?')}, direction={player_data.get('direction', '?')}")

        # Prüfen, ob es sich um einen neuen Spieler handelt
        is_new_player = client_id not in self.other_players
        if is_new_player:
            self.logger.info(f"[DATENFLUSS] NEW PLAYER JOINED: {player_data.get('name', 'Unknown')} (ID: {client_id})")

        # Prüfen, ob es sich um die eigenen Daten handelt
        own_player_id = self.player.player_id
        received_player_id = player_data.get("player_id")

        self.logger.info(f"[DATENFLUSS] PLAYER ID CHECK: received_player_id={received_player_id}, own_player_id={own_player_id}")

        is_own_player = received_player_id == own_player_id
        if is_own_player:
            self.logger.info(f"[DATENFLUSS] RECEIVED UPDATE FOR OWN PLAYER. Not adding to other_players list.")

            # Server-Reconciliation anwenden, wenn es sich um die eigenen Daten handelt
            if self.config.get_reconciliation():
                self.logger.debug(f"Applying server reconciliation for own player data")
                self.player.apply_server_update(player_data, reconciliation=True)
            return

        # Prüfen, ob die Spielerdaten vollständig sind
        if not player_data.get('x') or not player_data.get('y') or not player_data.get('player_id'):
            self.logger.warning(f"[DATENFLUSS] INCOMPLETE PLAYER DATA: {json.dumps(player_data)}")
            return

        # Spielerdaten speichern (nur für andere Spieler)
        self.logger.info(f"[DATENFLUSS] ADDING PLAYER TO OTHER_PLAYERS LIST: client_id={client_id}, player_data={json.dumps(player_data)}")
        self.other_players[client_id] = player_data
        self.logger.info(f"[DATENFLUSS] PLAYER ADDED TO OTHER_PLAYERS LIST: client_id={client_id}")

        # Log-Ausgabe für alle bekannten Spieler
        self.logger.info(f"[DATENFLUSS] UPDATED OTHER_PLAYERS LIST. Current count: {len(self.other_players)}")
        self.logger.info(f"[DATENFLUSS] OTHER_PLAYERS LIST: {json.dumps([{'id': cid, 'name': data.get('name', 'Unknown'), 'x': data.get('x', '?'), 'y': data.get('y', '?')} for cid, data in self.other_players.items()])}")

        # Prüfen, ob der Spieler tatsächlich in der Liste ist
        if client_id in self.other_players:
            self.logger.info(f"[DATENFLUSS] PLAYER VERIFICATION: client_id={client_id} IS in other_players list")
        else:
            self.logger.warning(f"[DATENFLUSS] PLAYER VERIFICATION FAILED: client_id={client_id} is NOT in other_players list")

        # Erzwinge ein Rendering-Update
        self.force_render_update = True

    def _on_player_disconnected(self, client_id: str, player_name: str):
        """Callback für Spieler-Disconnects

        Args:
            client_id: Client-ID des Spielers
            player_name: Name des Spielers
        """
        self.logger.info(f"Player disconnected: {player_name}")

        # Spieler aus der Liste entfernen
        if client_id in self.other_players:
            del self.other_players[client_id]

    def _on_chat_message(self, client_id: str, player_name: str, message: str):
        """Callback für Chat-Nachrichten

        Args:
            client_id: Client-ID des Spielers
            player_name: Name des Spielers
            message: Chat-Nachricht
        """
        self.logger.info(f"Chat message from {player_name}: {message}")

        # TODO: Chat-Nachricht anzeigen

        # Interpolierten Spieler entfernen, wenn vorhanden
        if client_id in self.interpolated_players:
            del self.interpolated_players[client_id]

    def _on_chat_message(self, player_name: str, message: str):
        """Callback für Chat-Nachrichten

        Args:
            player_name: Name des Spielers
            message: Chat-Nachricht
        """
        self.logger.info(f"Chat message from {player_name}: {message}")

    def start_new_game(self, as_host: bool = False) -> None:
        """Startet ein neues Spiel

        Args:
            as_host: Wenn True, wird das Spiel als Host gestartet
        """
        self.logger.info(f"Starting new game (as_host={as_host})")

        # Multiplayer-Status zurücksetzen
        self.multiplayer_active = False
        self.other_players = {}

        # Als Host starten, wenn gewünscht
        if as_host:
            self.start_hosting()

        # Zum PLAYING-State wechseln
        self.state_manager.change_state(GameState.PLAYING)

    def continue_game(self) -> None:
        """Setzt ein gespeichertes Spiel fort"""
        self.logger.info("Continuing game")
        # TODO: Spielstand laden

        # Zum PLAYING-State wechseln
        self.state_manager.change_state(GameState.PLAYING)

    def show_options_menu(self) -> None:
        """Zeigt das Optionsmenü an"""
        self.logger.info("Showing options menu")
        self.state_manager.change_state(GameState.OPTIONS)

    def join_multiplayer_game(self) -> None:
        """Tritt einem Multiplayer-Spiel bei"""
        self.logger.info("=== JOINING A MULTIPLAYER GAME ===")
        # Dialog zur Eingabe der IP-Adresse anzeigen
        self._show_join_dialog()

    def _show_join_dialog(self) -> None:
        """Zeigt einen Dialog zum Beitreten einer Multiplayer-Session"""
        self.logger.info("=== SHOWING JOIN DIALOG ===")

        # Eingabezustände zurücksetzen, um zu verhindern, dass vorherige Eingaben erkannt werden
        self.input_manager.reset()

        # Warte kurz, um sicherzustellen, dass die Enter-Taste vom vorherigen Menü nicht mehr erkannt wird
        pygame.event.clear()

        # Warte auf ein neues Frame, um sicherzustellen, dass keine Tasten mehr gedrückt sind
        self.clock.tick(60)

        # Dialog einrichten
        self.state_manager.setup_input_dialog(
            "IP-Adresse eingeben:",
            "localhost",
            self._join_with_ip
        )

        self.logger.info(f"Dialog created with default IP: {self.state_manager.input_dialog_text}")

        # Sicherstellen, dass der Fokus auf dem Eingabefeld liegt
        pygame.key.set_repeat(500, 50)  # Tastaturwiederholung aktivieren

        # Warte auf ein weiteres Frame, um sicherzustellen, dass keine Tasten mehr gedrückt sind
        self.clock.tick(60)
        pygame.event.clear()

    def _join_with_ip(self, ip_address: str) -> None:
        """Verbindet mit der angegebenen IP-Adresse

        Args:
            ip_address: IP-Adresse des Hosts
        """
        self.logger.info(f"=== JOINING SESSION AT {ip_address} ===")
        port = 8765

        # Eingabezustände zurücksetzen, um zu verhindern, dass die Enter-Taste
        # als Aktion erkannt wird
        self.input_manager.reset()

        # Verbindung herstellen
        self.join_session(ip_address, port)

    def start_hosting(self) -> bool:
        """Startet eine Multiplayer-Session als Host"""
        if self.multiplayer_active:
            self.logger.warning("=== MULTIPLAYER ALREADY ACTIVE ===")
            return False

        self.logger.info("=== STARTING MULTIPLAYER SESSION AS HOST ===")
        port = self.config.get_server_port()
        success = self.multiplayer_manager.start_hosting(port)

        if success:
            self.logger.info("=== SUCCESSFULLY STARTED HOSTING MULTIPLAYER SESSION ===")
            self.multiplayer_active = True

            # Spielerdaten an den Server senden
            self._send_player_data()
            return True
        else:
            self.logger.error("=== FAILED TO START HOSTING MULTIPLAYER SESSION ===")
            return False

    def join_session(self, host: str = None, port: int = None, latency: int = None, jitter: int = None) -> bool:
        """Verbindet mit einer Multiplayer-Session

        Args:
            host: Host-Adresse (optional, sonst aus Konfiguration)
            port: Host-Port (optional, sonst aus Konfiguration)
            latency: Latenz-Simulation in Millisekunden (optional, sonst aus Konfiguration)
            jitter: Jitter-Simulation in Millisekunden (optional, sonst aus Konfiguration)

        Returns:
            bool: True if the connection attempt was initiated successfully, False otherwise
        """
        if self.multiplayer_active:
            self.logger.warning("=== MULTIPLAYER ALREADY ACTIVE ===")
            return False

        # Verwende die Werte aus der Konfiguration, wenn keine angegeben wurden
        if host is None:
            host = self.config.get_server_host()
        if port is None:
            port = self.config.get_server_port()
        if latency is None:
            latency = self.config.get_latency_simulation()
        if jitter is None:
            jitter = self.config.get_jitter_simulation()

        self.logger.info(f"=== JOINING MULTIPLAYER SESSION AT {host}:{port} ===")
        if latency > 0 or jitter > 0:
            self.logger.info(f"=== NETWORK SIMULATION ACTIVE: LATENCY={latency}ms, JITTER={jitter}ms ===")

        try:
            # Verbindung herstellen
            success = self.multiplayer_manager.connect_to_session(host, port, latency, jitter)

            # Prüfen, ob die Verbindung initiiert wurde (nicht unbedingt schon hergestellt)
            if success:
                # Wir setzen multiplayer_active auf True, aber die tatsächliche Verbindung
                # wird asynchron hergestellt. Die Verbindungsmeldung wird vom Client ausgegeben,
                # wenn die WebSocket-Verbindung tatsächlich hergestellt wurde.
                self.logger.info("=== CONNECTION ATTEMPT INITIATED ===")
                self.multiplayer_active = True

                # Spielzustand auf PLAYING setzen
                self.state_manager.change_state(GameState.PLAYING)

                # Wir versuchen, Spielerdaten zu senden, aber es kann sein, dass die Verbindung
                # noch nicht vollständig hergestellt ist. Der Client wird Warnungen ausgeben,
                # wenn die Verbindung noch nicht hergestellt ist.
                self._send_player_data()
                return True
            else:
                self.logger.error(f"=== FAILED TO INITIATE CONNECTION TO {host}:{port} ===")
                # Zurück zum Hauptmenü
                self.state_manager.change_state(GameState.MAIN_MENU)
                return False
        except Exception as e:
            self.logger.error(f"=== ERROR CONNECTING TO MULTIPLAYER SESSION: {e} ===")
            import traceback
            self.logger.error(traceback.format_exc())
            # Zurück zum Hauptmenü
            self.state_manager.change_state(GameState.MAIN_MENU)
            return False

    def quit(self) -> None:
        """Beendet das Spiel"""
        self.logger.info("Quitting game")
        self.running = False
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        """Startet die Hauptspielschleife"""
        self.logger.info("Starting game loop")

        # FPS-Font
        fps_font = pygame.font.SysFont(None, 24)

        # FPS-Limit aus den Einstellungen holen
        fps_limit = self.settings.get("video", "fps_limit")
        self.logger.info(f"FPS limit set to {fps_limit}")

        # Netzwerk-Update-Timer initialisieren
        last_network_update = 0
        network_update_interval = 1.0 / self.config.get_update_rate()
        self.logger.info(f"Network update interval: {network_update_interval:.3f}s ({self.config.get_update_rate()} updates/s)")

        # Netzwerk-Optimierungen aktivieren
        self.logger.info(f"Network optimizations: interpolation={self.config.get_interpolation()}, "
                       f"prediction={self.config.get_prediction()}, "
                       f"reconciliation={self.config.get_reconciliation()}")

        # Latenz-Simulation aktivieren, wenn konfiguriert
        latency_simulation = self.config.get_latency_simulation()
        jitter_simulation = self.config.get_jitter_simulation()
        if latency_simulation > 0 or jitter_simulation > 0:
            self.logger.info(f"Network simulation: latency={latency_simulation}ms, jitter={jitter_simulation}ms")

        try:
            while self.running:
                try:
                    # Zeit messen
                    dt = self.clock.tick(fps_limit) / 1000.0

                    # Events verarbeiten
                    self.handle_events()

                    # Automatische Tests ausführen, wenn vorhanden
                    self._process_automated_tests(dt)

                    # Spielzustand aktualisieren
                    self.update(dt)

                    # Multiplayer: Spielerdaten senden, wenn aktiv und Update-Intervall erreicht
                    if self.multiplayer_active:
                        last_network_update += dt
                        if last_network_update >= network_update_interval:
                            self.logger.debug(f"[DATENFLUSS] NETWORK UPDATE INTERVAL REACHED: {last_network_update:.3f}s >= {network_update_interval:.3f}s")
                            self._send_player_data()
                            last_network_update = 0
                        else:
                            self.logger.debug(f"[DATENFLUSS] NETWORK UPDATE INTERVAL NOT REACHED: {last_network_update:.3f}s < {network_update_interval:.3f}s")

                    # Screenshots erstellen, wenn aktiviert
                    if self.screenshots_enabled:
                        current_time = time.time()
                        if current_time - self.last_screenshot_time >= self.screenshot_interval:
                            self._take_screenshot(f"auto_{self.state_manager.current_state.name.lower()}")
                            self.last_screenshot_time = current_time

                    # FPS aktualisieren
                    self.render_manager.update_fps(self.clock.get_fps())

                    # Rendern
                    self.render_manager.render()

                except Exception as e:
                    self.logger.error(f"Error in game loop: {e}", exc_info=True)
        except KeyboardInterrupt:
            self.logger.info("Game interrupted by user")
        finally:
            self.quit()
