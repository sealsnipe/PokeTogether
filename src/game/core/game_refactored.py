#!/usr/bin/env python
"""
Game class - Main game loop and state management (refactored version)
"""

import pygame
import sys
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
from game.ui.main_menu_refactored import MainMenuRefactored
from game.ui.options_menu_refactored import OptionsMenuRefactored
from game.ui.ingame_menu_refactored import IngameMenuRefactored
from game.network.multiplayer_manager import MultiplayerManager


class Game:
    """Main game class (refactored version)"""

    def __init__(self, minimized=False):
        """Initialize the game

        Args:
            minimized: Wenn True, wird das Spiel minimiert gestartet
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game")

        # Minimiert-Flag speichern
        self.minimized = minimized

        # Pygame initialisieren
        pygame.init()

        # Fenster erstellen
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("PokeTogether" + (" (Test Mode)" if minimized else ""))

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
        self.multiplayer_active = False

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

        # Spieler - Starte in der Mitte der Karte
        self.player = Player(self.current_map.pixel_width // 2, self.current_map.pixel_height // 2, "Red")

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

        # Spieler bewegen
        if direction_x != 0 or direction_y != 0:
            self.player.move(direction_x, direction_y, speed_multiplier)

        # Spieler aktualisieren
        self.player.update(dt)

        # Kamera aktualisieren
        self.camera.update(self.player.x, self.player.y)

        # Multiplayer: Spielerdaten senden, wenn aktiv
        if self.multiplayer_active:
            self._send_player_data()

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
        for player_id, player_data in self.other_players.items():
            # Einfache Darstellung anderer Spieler als farbige Rechtecke
            player_rect = pygame.Rect(
                player_data["x"] - self.camera.get_offset()[0],
                player_data["y"] - self.camera.get_offset()[1],
                32, 32
            )
            pygame.draw.rect(self.screen, (0, 0, 255), player_rect)

            # Spielername anzeigen
            font = pygame.font.SysFont(None, 20)
            name_text = font.render(player_data.get("name", "Player"), True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(player_rect.centerx, player_rect.top - 10))
            self.screen.blit(name_text, name_rect)

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
            self.logger.debug("Not sending player data because multiplayer is not active")
            return

        # Spielerdaten sammeln
        player_data = {
            "name": self.player.name,
            "x": self.player.x,
            "y": self.player.y,
            "direction": self.player.direction,
            "moving": self.player.moving
        }

        self.logger.debug(f"Sending player data: {player_data}")

        # Daten an den Server senden
        self.multiplayer_manager.send_player_update(player_data)

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
        success = self.multiplayer_manager.start_hosting()

        if success:
            self.logger.info("=== SUCCESSFULLY STARTED HOSTING MULTIPLAYER SESSION ===")
            self.multiplayer_active = True

            # Spielerdaten an den Server senden
            self._send_player_data()
            return True
        else:
            self.logger.error("=== FAILED TO START HOSTING MULTIPLAYER SESSION ===")
            return False

    def join_session(self, host: str, port: int = 8765) -> bool:
        """Verbindet mit einer Multiplayer-Session

        Args:
            host: Host-Adresse
            port: Host-Port
        """
        if self.multiplayer_active:
            self.logger.warning("=== MULTIPLAYER ALREADY ACTIVE ===")
            return False

        self.logger.info(f"=== JOINING MULTIPLAYER SESSION AT {host}:{port} ===")

        try:
            # Verbindung herstellen
            success = self.multiplayer_manager.connect_to_session(host, port)

            # Prüfen, ob die Verbindung erfolgreich war
            if success:
                self.logger.info("=== SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION ===")
                self.multiplayer_active = True

                # Spielzustand auf PLAYING setzen
                self.state_manager.change_state(GameState.PLAYING)

                # Spielerdaten an den Server senden
                self._send_player_data()
                return True
            else:
                self.logger.error(f"=== FAILED TO CONNECT TO {host}:{port} ===")
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

        try:
            while self.running:
                try:
                    # Zeit messen
                    dt = self.clock.tick(60) / 1000.0

                    # Events verarbeiten
                    self.handle_events()

                    # Automatische Tests ausführen, wenn vorhanden
                    self._process_automated_tests(dt)

                    # Spielzustand aktualisieren
                    self.update(dt)

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
