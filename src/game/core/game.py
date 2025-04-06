#!/usr/bin/env python
"""
Game class - Main game loop and state management
"""

import pygame
import sys
import logging
import os
import time
from game.core.input_handler import InputHandler
from game.core.input_command_reader import InputCommandReader
from game.entities.player import Player
from game.core.camera import Camera
from game.maps.simple_map import SimpleMap
from game.core.settings import Settings
from game.ui.main_menu import MainMenu
from game.ui.options_menu import OptionsMenu
from game.ui.ingame_menu import IngameMenu
from game.network.multiplayer_manager import MultiplayerManager

class Game:
    """Main game class"""

    def __init__(self, minimized=False):
        """Initialize the game

        Args:
            minimized: Wenn True, wird das Spiel minimiert gestartet
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game")

        # Minimiert-Flag speichern
        self.minimized = minimized

        pygame.init()

        # Normales Fenster erstellen
        self.screen = pygame.display.set_mode((800, 600))

        if minimized:
            self.logger.info("Minimierter Modus aktiviert - Fenster wird minimiert")
            pygame.display.set_caption("PokeTogether (Test Mode)")

            # Fenster minimieren (nur unter Windows)
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
        else:
            pygame.display.set_caption("PokeTogether")

        self.clock = pygame.time.Clock()
        self.running = True

        # Game states
        self.states = {
            "MAIN_MENU": 0,
            "PLAYING": 1,
            "BATTLE": 2,
            "PAUSE": 3,
            "OPTIONS": 4,
            "INGAME_MENU": 5,
            "MULTIPLAYER_MENU": 6,
            "INPUT_DIALOG": 7
        }

        # Input-Dialog-Variablen
        self.input_dialog_active = False
        self.input_dialog_text = ""
        self.input_dialog_title = ""
        self.input_dialog_callback = None
        self.previous_state = None
        self.current_state = self.states["MAIN_MENU"]

        # Multiplayer
        self.multiplayer_manager = MultiplayerManager()
        self.other_players = {}
        self.multiplayer_active = False

        # Game resources
        self.resources = {}

        # Settings
        self.settings = Settings()

        # Input-Handler
        self.input_handler = InputHandler()

        # Input-Command-Reader für autonomes Testen
        self.input_command_reader = InputCommandReader()

        # Karte - Dynamische Größe basierend auf der Bildschirmauflösung
        screen_width, screen_height = self.screen.get_size()
        tile_size = 32  # Größere Tiles für bessere Sichtbarkeit

        # Berechne die Anzahl der Tiles basierend auf der Bildschirmgröße
        # Füge ein paar zusätzliche Tiles hinzu, damit die Karte größer als der Bildschirm ist
        map_width = screen_width // tile_size + 10
        map_height = screen_height // tile_size + 10

        self.current_map = SimpleMap(map_width, map_height, tile_size)

        # Spieler - Starte an einer definierten Position basierend auf der Konfiguration
        player_character = "Red"  # Standard-Charakter
        player_x = self.current_map.pixel_width // 2
        player_y = self.current_map.pixel_height // 2

        # Wenn wir eine Konfiguration haben, verwende die Werte daraus
        if hasattr(self, 'config'):
            player_character = self.config.get("player", "character") or player_character
            # Verwende die instance_id, um unterschiedliche Startpositionen zu bestimmen
            instance_id = self.config.get("instance", "id") or ""

            # Beide Spieler starten an festen, vordefinierten Positionen
            # Diese Positionen müssen auf beiden Clients identisch sein
            if "player1" in instance_id:
                # Spieler 1 startet immer bei (460, 448)
                player_x = 460
                player_y = 448
                self.logger.info(f"[SPIELERSYNC] Player 1 spawning at fixed position: ({player_x}, {player_y})")
            elif "player2" in instance_id:
                # Spieler 2 startet immer bei (560, 448)
                player_x = 560
                player_y = 448
                self.logger.info(f"[SPIELERSYNC] Player 2 spawning at fixed position: ({player_x}, {player_y})")

        self.player = Player(player_x, player_y, player_character)

        # Kamera - Verwende die aktuelle Bildschirmgröße für die Kamera
        # Zoom-Faktor von 1.2 bedeutet 20% herausgezoomt
        self.camera = Camera(screen_width, screen_height, self.current_map.pixel_width, self.current_map.pixel_height, zoom_factor=1.2)

        # Menüs
        self.main_menu = MainMenu(self.screen, self.input_handler)
        self.options_menu = OptionsMenu(self.screen, self.settings, self.input_handler)
        self.ingame_menu = IngameMenu(self.screen, self.settings, self.input_handler)

        # Menü-Callbacks einrichten
        self.main_menu.set_callbacks(
            on_new_game=self._start_new_game,
            on_host_game=self._host_game,
            on_join_game=self._join_game,
            on_continue_game=self._continue_game,
            on_show_options=self._show_options,
            on_exit_game=self._exit_game
        )

        # Optionsmenü-Callbacks einrichten
        self.options_menu.on_close = self._options_closed
        self.options_menu.on_resolution_changed = self._apply_current_resolution

        # Ingame-Menü-Callbacks einrichten
        self.ingame_menu.on_show_options = self._show_options
        self.ingame_menu.on_save_game = self._save_game
        self.ingame_menu.on_host_game = self.start_hosting
        self.ingame_menu.on_join_game = self._show_join_dialog
        self.ingame_menu.on_disconnect = self.stop_multiplayer

        # Multiplayer-Callbacks einrichten
        self.multiplayer_manager.set_player_update_callback(self._on_player_update)
        self.multiplayer_manager.set_player_disconnected_callback(self._on_player_disconnected)
        self.multiplayer_manager.set_chat_message_callback(self._on_chat_message)

        self.logger.info("Game initialized")

    def load_resources(self):
        """Load game resources"""
        self.logger.info("Loading resources")
        # Hier würden Ressourcen geladen werden (Bilder, Sounds, etc.)
        self.logger.info("Resources loaded")

    def handle_events(self):
        """Handle pygame events"""
        try:
            # Pygame-Events abrufen
            events = pygame.event.get()

            # Input-Command-Reader aktualisieren und zusätzliche Events abrufen
            try:
                command_events = self.input_command_reader.update()
                if command_events:
                    self.logger.info(f"Received {len(command_events)} command events from InputCommandReader")
                    # Füge die Kommando-Events zur Event-Liste hinzu
                    events.extend(command_events)
            except Exception as e:
                self.logger.error(f"Error updating input command reader: {e}")

            # Wenn wir im Input-Dialog sind, Events direkt dort verarbeiten
            if self.current_state == self.states["INPUT_DIALOG"]:
                self._handle_input_dialog_events(events)
                return

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
        except Exception as e:
            self.logger.error(f"Error handling events: {e}")
            # Versuche, die Events zu leeren, um weitere Fehler zu vermeiden
            try:
                pygame.event.clear()
            except:
                pass

        # Input-Handler aktualisieren
        try:
            self.input_handler.handle_events(events if 'events' in locals() else [])
            self.input_handler.update()
        except Exception as e:
            self.logger.error(f"Error updating input handler: {e}")

    def _handle_input_dialog_events(self, events):
        """Verarbeitet Events speziell für den Input-Dialog

        Args:
            events: Liste der pygame-Events
        """
        try:
            # Input-Handler aktualisieren (für Controller-Eingaben)
            self.input_handler.handle_events(events)
            self.input_handler.update()

            # Tastatureingaben verarbeiten
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    try:
                        if event.key == pygame.K_RETURN:
                            # Enter-Taste: Dialog bestätigen
                            self.logger.info("Enter key pressed, confirming dialog")
                            if self.input_dialog_callback:
                                self.input_dialog_callback(self.input_dialog_text)
                            self.current_state = self.previous_state
                            self.input_dialog_active = False

                            # Eingabezustände zurücksetzen, um zu verhindern, dass die Enter-Taste
                            # als Aktion erkannt wird
                            self.input_handler.input_state = {}
                            self.input_handler.input_pressed = {}
                            self.input_handler.last_input_state = {}
                        elif event.key == pygame.K_ESCAPE:
                            # Escape-Taste: Dialog abbrechen
                            self.logger.info("Escape key pressed, canceling dialog")
                            self.current_state = self.previous_state
                            self.input_dialog_active = False

                            # Eingabezustände zurücksetzen
                            self.input_handler.input_state = {}
                            self.input_handler.input_pressed = {}
                            self.input_handler.last_input_state = {}
                        elif event.key == pygame.K_BACKSPACE:
                            # Backspace-Taste: Zeichen löschen
                            self.input_dialog_text = self.input_dialog_text[:-1]
                            self.logger.info(f"Backspace pressed, text now: {self.input_dialog_text}")
                        elif event.unicode and event.unicode.isprintable():
                            # Zeichen hinzufügen (nur druckbare Zeichen)
                            self.input_dialog_text += event.unicode
                            self.logger.info(f"Character added: {event.unicode}, text now: {self.input_dialog_text}")
                    except Exception as e:
                        self.logger.error(f"Error processing key event: {e}")
        except Exception as e:
            self.logger.error(f"Error handling input dialog events: {e}")

    def handle_keydown(self, event):
        """Handle keydown events"""
        if event.key == pygame.K_ESCAPE:
            if self.current_state == self.states["PLAYING"]:
                self.current_state = self.states["PAUSE"]
            elif self.current_state == self.states["PAUSE"]:
                self.current_state = self.states["PLAYING"]
            elif self.current_state == self.states["INGAME_MENU"]:
                self.current_state = self.states["PLAYING"]
                self.ingame_menu.hide()
            elif self.current_state == self.states["OPTIONS"]:
                self.current_state = self.states["MAIN_MENU"]
                self.options_menu.hide()
            elif self.current_state == self.states["MAIN_MENU"]:
                self.running = False
        elif event.key == pygame.K_RETURN or event.key == pygame.K_x:  # Enter oder X-Taste
            if self.current_state == self.states["PLAYING"]:
                self.current_state = self.states["INGAME_MENU"]
                self.ingame_menu.show()

    def _start_new_game(self):
        """Start a new single player game"""
        self.logger.info("Starting new single player game")
        # Sicherstellen, dass Multiplayer deaktiviert ist
        self.multiplayer_active = False
        self.other_players = {}
        self.current_state = self.states["PLAYING"]

    def _host_game(self):
        """Host a multiplayer game"""
        self.logger.info("Starting new game as host")
        # Multiplayer-Status zurücksetzen
        self.multiplayer_active = False
        self.other_players = {}

        # Als Host starten
        self.start_hosting()

        # Spielzustand auf PLAYING setzen
        self.current_state = self.states["PLAYING"]

    def _join_game(self):
        """Join a multiplayer game"""
        self.logger.info("=== JOINING A MULTIPLAYER GAME ===")
        # Dialog zur Eingabe der IP-Adresse anzeigen
        self._show_join_dialog()

    def _continue_game(self):
        """Continue a saved game"""
        self.logger.info("Continuing game")
        # Hier würde der Spielstand geladen werden
        self.current_state = self.states["PLAYING"]

    def _show_options(self):
        """Show options menu"""
        self.logger.info("Showing options menu")
        # Speichere den vorherigen Zustand, um später dorthin zurückzukehren
        if self.current_state == self.states["INGAME_MENU"]:
            self._previous_state = self.states["INGAME_MENU"]
            self.ingame_menu.hide()
        self.current_state = self.states["OPTIONS"]
        self.options_menu.show()

    def _save_game(self):
        """Save the game"""
        self.logger.info("Saving game")
        # Hier würde der Spielstand gespeichert werden

    def _exit_game(self):
        """Exit the game"""
        self.logger.info("Exiting game")
        self.running = False

    def _options_closed(self):
        """Called when the options menu is closed"""
        self.logger.info("Options menu closed, returning to previous state")
        # Wir entfernen den Aufruf der reset-Methode, da sie Probleme verursacht

        # Wenn das Optionsmenü aus dem Ingame-Menü geöffnet wurde, zurück zum Ingame-Menü
        if hasattr(self, "_previous_state") and self._previous_state == self.states["INGAME_MENU"]:
            self.current_state = self.states["INGAME_MENU"]
            self.ingame_menu.show()
            delattr(self, "_previous_state")
        else:
            # Ansonsten zurück zum Hauptmenü
            self.current_state = self.states["MAIN_MENU"]

    def _apply_current_resolution(self):
        """Apply the current resolution from settings"""
        current_resolution = self.settings.get_resolution()
        self.logger.info(f"Applying current resolution: {current_resolution}")
        self._apply_resolution(current_resolution[0], current_resolution[1])

    def _apply_resolution(self, width: int, height: int):
        """Apply a new resolution

        Args:
            width: New screen width
            height: New screen height
        """
        self.logger.info(f"Applying resolution {width}x{height}")

        # Setze die neue Bildschirmgröße
        fullscreen = self.settings.get("video", "fullscreen")
        if fullscreen:
            self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))

        # Aktualisiere die Karte und die Kamera
        tile_size = 32
        map_width = width // tile_size + 10
        map_height = height // tile_size + 10

        self.current_map = SimpleMap(map_width, map_height, tile_size)
        self.camera = Camera(width, height, self.current_map.pixel_width, self.current_map.pixel_height, zoom_factor=1.2)

        # Setze den Spieler in die Mitte der Karte
        self.player.x = self.current_map.pixel_width // 2
        self.player.y = self.current_map.pixel_height // 2

    def update(self, dt=1/60):
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

        # Prüfen, ob das Spiel beschleunigt werden soll
        # Direkte Prüfung der LB-Taste für Fast Forward
        fast_forward_pressed = False
        if self.input_handler.controllers and len(self.input_handler.controllers) > 0:
            controller = self.input_handler.controllers[0]
            try:
                from game.core.controller_constants import BUTTON_LEFTSHOULDER
                if controller.get_button(BUTTON_LEFTSHOULDER):
                    fast_forward_pressed = True
                    self.logger.info("LB-Taste direkt erkannt für Vorspulen!")
            except Exception as e:
                self.logger.error(f"Fehler bei der Controller-Prüfung für Vorspulen: {e}")

        # Normale Prüfung für Tastatur
        if not fast_forward_pressed:
            fast_forward_pressed = self.input_handler.is_pressed("fast_forward")

        # Nur loggen, wenn sich der Zustand ändert
        if fast_forward_pressed:
            fast_forward_speed = self.settings.get("gameplay", "fast_forward_speed")
            dt *= fast_forward_speed
            self.logger.debug(f"Game speed increased to {fast_forward_speed}x")

        # Aktualisiere den Spielzustand mit dem angepassten dt
        self._update_game_state(dt)

    def _update_game_state(self, dt):
        """Update the game state based on the current state

        Args:
            dt: Zeitdelta seit dem letzten Update in Sekunden
        """
        if self.current_state == self.states["PLAYING"]:
            # Prüfen, ob das Ingame-Menü geöffnet werden soll
            if self.input_handler.was_pressed("menu"):
                self.current_state = self.states["INGAME_MENU"]
                self.ingame_menu.show()
            else:
                # Direkte Prüfung der RB-Taste für Rennen
                run_pressed = False
                if self.input_handler.controllers and len(self.input_handler.controllers) > 0:
                    controller = self.input_handler.controllers[0]
                    try:
                        from game.core.controller_constants import BUTTON_RIGHTSHOULDER
                        if controller.get_button(BUTTON_RIGHTSHOULDER):
                            run_pressed = True
                            self.logger.info("RB-Taste direkt erkannt für Rennen!")
                    except Exception as e:
                        self.logger.error(f"Fehler bei der Controller-Prüfung für Rennen: {e}")

                # Normale Prüfung für Tastatur
                if not run_pressed:
                    run_pressed = self.input_handler.is_pressed("run")

                self.logger.info(f"Run pressed: {run_pressed}")

                run_speed = self.settings.get("gameplay", "run_speed") if run_pressed else 1.0
                if run_pressed:
                    self.logger.info(f"Player running with speed {run_speed}x")

                # Spielerbewegung basierend auf Input
                movement = self.input_handler.get_movement()

                # Alte Position speichern
                old_x, old_y = self.player.x, self.player.y

                # Spieler bewegen (mit Laufgeschwindigkeit multiplizieren)
                self.player.move(movement[0] * run_speed, movement[1] * run_speed)

                # Kollisionserkennung mit der Karte
                if self.current_map.is_collision(self.player.x, self.player.y):
                    # Bei Kollision zurück zur alten Position
                    self.player.x = old_x
                    self.player.y = old_y

                # Spieler aktualisieren
                self.player.update(dt)

                # Kamera aktualisieren
                self.camera.update(self.player.x, self.player.y)

                # Multiplayer: Spielerdaten senden, wenn aktiv
                if self.multiplayer_active:
                    self._send_player_data()
        elif self.current_state == self.states["BATTLE"]:
            # Update battle
            pass
        elif self.current_state == self.states["MAIN_MENU"]:
            # Hauptmenü aktualisieren
            self.main_menu.update()
        elif self.current_state == self.states["INGAME_MENU"]:
            # Ingame-Menü aktualisieren
            self.ingame_menu.update()

            # Prüfen, ob das Menü geschlossen werden soll
            if not self.ingame_menu.active:
                self.current_state = self.states["PLAYING"]
                # Eingaben zurücksetzen
                self.input_handler.input_state = {}
                self.input_handler.input_pressed = {}
                self.input_handler.last_input_state = {}
        elif self.current_state == self.states["OPTIONS"]:
            # Optionsmenü aktualisieren
            self.options_menu.update()
        elif self.current_state == self.states["INPUT_DIALOG"]:
            # Input-Dialog aktualisieren
            self._update_input_dialog()

    def render(self):
        """Render the game"""
        self.screen.fill((0, 0, 0))

        if self.current_state == self.states["PLAYING"]:
            # Render game objects
            self._render_playing()
        elif self.current_state == self.states["BATTLE"]:
            # Render battle
            self._render_battle()
        elif self.current_state == self.states["MAIN_MENU"]:
            # Render menu
            self._render_main_menu()
        elif self.current_state == self.states["INPUT_DIALOG"]:
            # Render input dialog
            self._render_input_dialog()
        elif self.current_state == self.states["PAUSE"]:
            # Render pause menu
            self._render_pause()
        elif self.current_state == self.states["INGAME_MENU"]:
            # Render ingame menu
            self._render_ingame_menu()
        elif self.current_state == self.states["OPTIONS"]:
            # Render options menu
            self._render_options()

        # Bildschirm wird am Ende der run-Methode aktualisiert

    def _render_playing(self):
        """Render the playing state"""
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

    def _render_battle(self):
        """Render the battle state"""
        # Hier würde der Kampfbildschirm gerendert werden
        font = pygame.font.SysFont(None, 36)
        text = font.render("Battle State", True, (255, 255, 255))
        self.screen.blit(text, (300, 280))

    def _render_main_menu(self):
        """Render the main menu"""
        # Hauptmenü rendern
        self.main_menu.render()

    def _render_options(self):
        """Render the options menu"""
        # Hintergrund mit einem dunklen Blau-Grün füllen
        self.screen.fill((0, 50, 50))

        # Titel rendern
        font = pygame.font.SysFont(None, 48)
        title = font.render("PokeTogether - Optionen", True, (255, 255, 255))
        self.screen.blit(title, (200, 50))

        # Optionsmenü rendern
        self.options_menu.render()

    def _render_ingame_menu(self):
        """Render the ingame menu"""
        # Zuerst das Spiel im Hintergrund rendern
        self._render_playing()

        # Dann das Ingame-Menü darüber rendern
        self.ingame_menu.render()

    def _render_pause(self):
        """Render the pause menu"""
        # Hier würde das Pausemenü gerendert werden
        font = pygame.font.SysFont(None, 36)
        text = font.render("Game Paused", True, (255, 255, 255))
        self.screen.blit(text, (300, 280))

        font = pygame.font.SysFont(None, 24)
        resume = font.render("Press ESC to Resume", True, (255, 255, 255))
        self.screen.blit(resume, (300, 350))

    def run(self):
        """Main game loop"""
        self.logger.info("Starting game loop")

        try:
            self.load_resources()

            # FPS-Zähler
            fps_font = pygame.font.SysFont(None, 24)

            # Automatische Tests laden, wenn vorhanden
            self._load_automated_tests()

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

                    # Rendern
                    self.render()

                    # FPS anzeigen
                    fps = self.clock.get_fps()
                    fps_text = fps_font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
                    self.screen.blit(fps_text, (10, 570))

                    # Automatische Tests-Status anzeigen, wenn aktiv
                    if hasattr(self, 'automated_tests') and self.automated_tests:
                        test_text = fps_font.render(f"Automated Test: {len(self.automated_tests)} actions remaining", True, (255, 255, 0))
                        self.screen.blit(test_text, (10, 545))

                    # Bildschirm aktualisieren
                    pygame.display.flip()

                except Exception as e:
                    self.logger.error(f"Error in game loop: {e}")
                    # Kurze Pause, um CPU-Last zu reduzieren
                    pygame.time.wait(100)
        except Exception as e:
            self.logger.error(f"Critical error in game: {e}")
            # Versuche, das Spiel sauber zu beenden
            pygame.quit()

        # Multiplayer-Session beenden, falls aktiv
        if self.multiplayer_active:
            self.stop_multiplayer()

        self.logger.info("Game loop ended")
        pygame.quit()

    # Methoden für automatische Tests
    def _load_automated_tests(self):
        """Lädt automatische Tests aus einer Datei"""
        try:
            # Prüfe, ob Testdateien im input_instructions-Verzeichnis vorhanden sind
            import os
            import json
            import glob

            # Suche nach JSON-Dateien im input_instructions-Verzeichnis
            test_files = glob.glob("input_instructions/*.json")

            if not test_files:
                self.logger.info("Keine automatischen Tests gefunden")
                self.automated_tests = []
                return

            # Verwende die erste gefundene Datei
            test_file = test_files[0]
            self.logger.info(f"Lade automatische Tests aus {test_file}")

            with open(test_file, 'r') as f:
                self.automated_tests = json.load(f)

            self.logger.info(f"Automatische Tests geladen: {len(self.automated_tests)} Aktionen")

            # Erstelle eine .loaded-Datei, um anzuzeigen, dass die Tests geladen wurden
            with open(f"{test_file}.loaded", 'w') as f:
                f.write(f"Loaded at {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Initialisiere den Timer für die Testausführung
            self.test_timer = 0
            self.current_test_action = None

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der automatischen Tests: {e}")
            self.automated_tests = []

    def _process_automated_tests(self, dt):
        """Führt automatische Tests aus"""
        if not hasattr(self, 'automated_tests') or not self.automated_tests:
            return

        # Aktualisiere den Timer
        if hasattr(self, 'test_timer'):
            self.test_timer -= dt

        # Wenn keine aktuelle Aktion ausgeführt wird oder der Timer abgelaufen ist
        if not hasattr(self, 'current_test_action') or self.current_test_action is None or self.test_timer <= 0:
            # Nächste Aktion ausführen
            if self.automated_tests:
                self.current_test_action = self.automated_tests.pop(0)
                self._execute_test_action(self.current_test_action)
            else:
                self.logger.info("Alle automatischen Tests abgeschlossen")
                self.current_test_action = None

    def _execute_test_action(self, action):
        """Führt eine Testaktion aus"""
        try:
            action_type = action.get("type", "")

            # Spielerposition vor der Aktion speichern
            player_pos_before = (self.player.x, self.player.y) if hasattr(self, 'player') else None

            if action_type == "key_press":
                key = action.get("key")
                if key:
                    # Nur wichtige Tasten loggen, um Redundanz zu vermeiden
                    if key in ["up", "down", "left", "right", "space", "return", "escape", "tab"]:
                        self.logger.info(f"Test: Taste drücken: {key}")
                    else:
                        # Debug-Level für unwichtigere Tasten
                        self.logger.debug(f"Test: Taste drücken: {key}")
                    # Simuliere einen Tastendruck
                    key_code = self._get_key_code(key)
                    if key_code:
                        event = pygame.event.Event(pygame.KEYDOWN, {"key": key_code})
                        pygame.event.post(event)

                    # Setze den Timer auf eine kurze Zeit
                    self.test_timer = 0.1

                    # Screenshot nur bei wichtigen Tasten machen (Bewegungstasten, Aktionstasten)
                    if key in ["up", "down", "left", "right", "space", "return", "escape", "tab"]:
                        self._take_screenshot(f"key_press_{key}")

            elif action_type == "key_release":
                key = action.get("key")
                if key:
                    # Keine Logs beim Loslassen von Tasten auf INFO-Level, um Redundanz zu vermeiden
                    self.logger.debug(f"Test: Taste loslassen: {key}")
                    # Simuliere ein Loslassen der Taste
                    key_code = self._get_key_code(key)
                    if key_code:
                        event = pygame.event.Event(pygame.KEYUP, {"key": key_code})
                        pygame.event.post(event)

                    # Setze den Timer auf eine kurze Zeit
                    self.test_timer = 0.1

                    # Keine Screenshots beim Loslassen von Tasten, um Redundanz zu vermeiden

            elif action_type == "wait":
                duration = float(action.get("duration", 1.0))
                # Nur längere Wartezeiten loggen
                if duration >= 1.0:
                    self.logger.info(f"Test: Warte {duration} Sekunden")
                else:
                    self.logger.debug(f"Test: Warte {duration} Sekunden")
                # Setze den Timer auf die angegebene Dauer
                self.test_timer = duration

            else:
                self.logger.warning(f"Unbekannter Aktionstyp: {action_type}")
                # Setze den Timer auf eine kurze Zeit
                self.test_timer = 0.1

            # Spielerposition nach der Aktion überprüfen
            if hasattr(self, 'player') and player_pos_before:
                player_pos_after = (self.player.x, self.player.y)
                if player_pos_before != player_pos_after:
                    # Bewegungsrichtung bestimmen
                    dx = player_pos_after[0] - player_pos_before[0]
                    dy = player_pos_after[1] - player_pos_before[1]
                    direction = ""
                    if dx > 0:
                        direction = "rechts"
                    elif dx < 0:
                        direction = "links"
                    elif dy > 0:
                        direction = "unten"
                    elif dy < 0:
                        direction = "oben"

                    # Bewegung protokollieren und Screenshot machen
                    self.logger.info(f"Spieler bewegt sich {direction}: von {player_pos_before} nach {player_pos_after}")
                    self._take_screenshot(f"movement_{direction}")

        except Exception as e:
            self.logger.error(f"Fehler bei der Ausführung der Testaktion: {e}")
            # Setze den Timer auf eine kurze Zeit
            self.test_timer = 0.1

    def _take_screenshot(self, action_name):
        """Erstellt einen Screenshot des aktuellen Spielzustands

        Args:
            action_name: Name der Aktion für den Dateinamen
        """
        try:
            # Stelle sicher, dass das Verzeichnis existiert
            import os
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)

            # Bestimme, ob dies eine Host- oder Client-Instanz ist
            instance_type = "single"
            if hasattr(self, 'multiplayer_active') and hasattr(self, 'multiplayer_manager'):
                if self.multiplayer_active and self.multiplayer_manager.is_host:
                    instance_type = "host"
                elif self.multiplayer_active:
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

            if hasattr(self, 'player'):
                info_text.append(f"Player: {self.player.name} at ({self.player.x}, {self.player.y})")

            if hasattr(self, 'multiplayer_active') and hasattr(self, 'multiplayer_manager'):
                if self.multiplayer_active:
                    info_text.append(f"Multiplayer: Active (Host: {self.multiplayer_manager.is_host})")
                    if hasattr(self, 'other_players'):
                        info_text.append(f"Other Players: {len(self.other_players)}")

                        # Informationen über andere Spieler hinzufügen
                        for player_id, player_data in self.other_players.items():
                            info_text.append(f"  - {player_data.get('name', 'Unknown')} at ({player_data.get('x', '?')}, {player_data.get('y', '?')})")
                else:
                    info_text.append("Multiplayer: Inactive")
            else:
                info_text.append("Multiplayer: Not initialized")

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

    def _get_key_code(self, key_name):
        """Konvertiert einen Tastennamen in einen Pygame-Tastencode"""
        key_map = {
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

        return key_map.get(key_name.lower())

    # Multiplayer-Methoden
    def start_hosting(self):
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

    def join_session(self, host: str, port: int = 8765):
        """Verbindet mit einer Multiplayer-Session

        Args:
            host: Host-Adresse
            port: Host-Port
        """
        if self.multiplayer_active:
            self.logger.warning("=== MULTIPLAYER ALREADY ACTIVE ===")
            return

        self.logger.info(f"=== JOINING MULTIPLAYER SESSION AT {host}:{port} ===")

        try:
            # Verbindung herstellen
            self.multiplayer_manager.connect_to_session(host, port)

            # Kurze Pause, um die Verbindung herzustellen
            pygame.time.wait(500)  # 500ms warten

            # Prüfen, ob die Verbindung erfolgreich war
            if self.multiplayer_manager.is_connected():
                self.logger.info("=== SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION ===")
                self.multiplayer_active = True

                # Spielzustand auf PLAYING setzen
                self.current_state = self.states["PLAYING"]

                # Spielerdaten an den Server senden
                self._send_player_data()
            else:
                self.logger.error(f"=== FAILED TO CONNECT TO {host}:{port} ===")
                # Zurück zum Hauptmenü
                self.current_state = self.states["MAIN_MENU"]
        except Exception as e:
            self.logger.error(f"=== ERROR CONNECTING TO MULTIPLAYER SESSION: {e} ===")
            import traceback
            self.logger.error(traceback.format_exc())
            # Zurück zum Hauptmenü
            self.current_state = self.states["MAIN_MENU"]

    def stop_multiplayer(self):
        """Beendet die Multiplayer-Session"""
        if not self.multiplayer_active:
            return

        self.logger.info("Stopping multiplayer session")

        if self.multiplayer_manager.is_host:
            self.multiplayer_manager.stop_hosting()
        else:
            self.multiplayer_manager.disconnect_from_session()

        self.multiplayer_active = False
        self.other_players = {}

    def _send_player_data(self):
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
        self.multiplayer_manager.update_player(player_data)

    def _on_player_update(self, client_id: str, player_data: dict):
        """Callback für Spieler-Updates

        Args:
            client_id: Client-ID des Spielers
            player_data: Spielerdaten
        """
        self.logger.debug(f"Player update: {player_data.get('name')} at ({player_data.get('x')}, {player_data.get('y')})")

        # Spielerdaten speichern
        self.other_players[client_id] = player_data

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

    def _on_chat_message(self, player_name: str, message: str):
        """Callback für Chat-Nachrichten

        Args:
            player_name: Name des Spielers
            message: Chat-Nachricht
        """
        self.logger.info(f"Chat message from {player_name}: {message}")
        # Hier könnte die Nachricht im Spiel angezeigt werden

    def _show_join_dialog(self):
        """Zeigt einen Dialog zum Beitreten einer Multiplayer-Session"""
        self.logger.info("=== SHOWING JOIN DIALOG ===")

        # Einfachen Dialog zur Eingabe der IP-Adresse erstellen
        self.input_dialog_active = True
        self.input_dialog_text = "localhost"
        self.input_dialog_title = "IP-Adresse eingeben:"
        self.input_dialog_callback = self._join_with_ip

        # Wechsle in den Dialog-Zustand
        self.previous_state = self.current_state
        self.current_state = self.states["INPUT_DIALOG"]

        self.logger.info(f"Dialog created with default IP: {self.input_dialog_text}")

    def _join_with_ip(self, ip_address):
        """Verbindet mit der angegebenen IP-Adresse

        Args:
            ip_address: IP-Adresse des Hosts
        """
        self.logger.info(f"=== JOINING SESSION AT {ip_address} ===")
        port = 8765

        # Eingabezustände zurücksetzen, um zu verhindern, dass die Enter-Taste
        # als Aktion erkannt wird
        self.input_handler.input_state = {}
        self.input_handler.input_pressed = {}
        self.input_handler.last_input_state = {}

        # Verbindung herstellen
        self.join_session(ip_address, port)

    def _update_input_dialog(self):
        """Aktualisiert den Input-Dialog"""
        # Controller-Eingaben verarbeiten
        if self.input_handler.was_pressed("b"):
            # B-Taste: Dialog abbrechen
            self.logger.info("B button pressed, canceling dialog")
            self.current_state = self.previous_state
            self.input_dialog_active = False

            # Eingabezustände zurücksetzen
            self.input_handler.input_state = {}
            self.input_handler.input_pressed = {}
            self.input_handler.last_input_state = {}

        if self.input_handler.was_pressed("a"):
            # A-Taste: Dialog bestätigen
            self.logger.info("A button pressed, confirming dialog")
            if self.input_dialog_callback:
                self.input_dialog_callback(self.input_dialog_text)
            self.current_state = self.previous_state
            self.input_dialog_active = False

            # Eingabezustände zurücksetzen
            self.input_handler.input_state = {}
            self.input_handler.input_pressed = {}
            self.input_handler.last_input_state = {}

    def _render_input_dialog(self):
        """Rendert den Input-Dialog"""
        # Hintergrund abdunkeln
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Dialog-Box zeichnen
        dialog_width = 400
        dialog_height = 180
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2

        pygame.draw.rect(self.screen, (50, 50, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (dialog_x, dialog_y, dialog_width, dialog_height), 2)

        # Titel zeichnen
        font_title = pygame.font.SysFont(None, 30)
        title_surface = font_title.render(self.input_dialog_title, True, (255, 255, 255))
        self.screen.blit(title_surface, (dialog_x + 20, dialog_y + 20))

        # Eingabefeld zeichnen
        input_box_width = dialog_width - 40
        input_box_height = 40
        input_box_x = dialog_x + 20
        input_box_y = dialog_y + 60

        pygame.draw.rect(self.screen, (30, 30, 30), (input_box_x, input_box_y, input_box_width, input_box_height))
        pygame.draw.rect(self.screen, (150, 150, 150), (input_box_x, input_box_y, input_box_width, input_box_height), 1)

        # Text zeichnen
        font_input = pygame.font.SysFont(None, 28)
        input_surface = font_input.render(self.input_dialog_text, True, (255, 255, 255))
        self.screen.blit(input_surface, (input_box_x + 10, input_box_y + 10))

        # Blinkenden Cursor zeichnen
        cursor_time = pygame.time.get_ticks() // 500 % 2  # Blinkt alle 500ms
        if cursor_time == 0:
            text_width = font_input.size(self.input_dialog_text)[0]
            cursor_x = input_box_x + 10 + text_width
            cursor_y = input_box_y + 10
            pygame.draw.line(self.screen, (255, 255, 255),
                            (cursor_x, cursor_y),
                            (cursor_x, cursor_y + font_input.get_height()), 2)

        # Hinweise zeichnen
        font_hint = pygame.font.SysFont(None, 20)

        # Tastatur-Hinweise
        keyboard_hint = font_hint.render("Enter: Bestätigen, Escape: Abbrechen", True, (200, 200, 200))
        self.screen.blit(keyboard_hint, (dialog_x + 20, dialog_y + 120))

        # Controller-Hinweise
        controller_hint = font_hint.render("A: Bestätigen, B: Abbrechen", True, (200, 200, 200))
        self.screen.blit(controller_hint, (dialog_x + 20, dialog_y + 145))

    def _render_other_players(self):
        """Rendert andere Spieler im Multiplayer-Modus"""
        if not self.multiplayer_active or not self.other_players:
            return

        # Temporärer Font für Spielernamen
        font = pygame.font.SysFont(None, 18)

        # Alle anderen Spieler rendern
        for client_id, player_data in self.other_players.items():
            # Spielerposition aus den Daten extrahieren
            x = player_data.get("x", 0)
            y = player_data.get("y", 0)
            name = player_data.get("name", "Unknown")
            direction = player_data.get("direction", "down")
            player_id = player_data.get("player_id", "Unknown")

            # Bestimme die Farbe basierend auf der player_id
            # Spieler 1 (460, 448) ist rot, Spieler 2 (560, 448) ist blau
            player_color = (0, 0, 255)  # Standard: Blau

            # Identifiziere den Spieler anhand seiner Startposition
            if 450 <= x <= 470 and 440 <= y <= 460:  # Spieler 1 Bereich
                player_color = (255, 0, 0)  # Rot für Spieler 1
                self.logger.info(f"[SPIELERSYNC] Identified player as Player 1: {player_id}")
            elif 550 <= x <= 570 and 440 <= y <= 460:  # Spieler 2 Bereich
                player_color = (0, 0, 255)  # Blau für Spieler 2
                self.logger.info(f"[SPIELERSYNC] Identified player as Player 2: {player_id}")

            # Kamera-Offset anwenden
            screen_x, screen_y = self.camera.apply(x, y)

            # Prüfen, ob der Spieler im erweiterten sichtbaren Bereich ist (mit Toleranz)
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            # Erweitere den sichtbaren Bereich um 50 Pixel in jede Richtung
            tolerance = 50

            self.logger.info(f"[VISIBILITY] CHECK: player={name}, screen_pos=({screen_x}, {screen_y}), screen_size=({screen_width}, {screen_height}), tolerance={tolerance}")

            if (-tolerance <= screen_x <= screen_width + tolerance and
                -tolerance <= screen_y <= screen_height + tolerance):

                # Einfache Darstellung als farbiger Kreis mit der bestimmten Farbe
                pygame.draw.circle(self.screen, player_color, (int(screen_x), int(screen_y)), 16)

                # Debug-Ausgabe für die Spielerposition
                self.logger.info(f"[DATENFLUSS] RENDERING PLAYER {name} (ID: {client_id}, player_id: {player_id}): x={x}, y={y}, screen_x={screen_x}, screen_y={screen_y}")

                # Spielername anzeigen
                name_text = font.render(name, True, (255, 255, 255))
                self.screen.blit(name_text, (int(screen_x) - name_text.get_width() // 2, int(screen_y) - 30))
