#!/usr/bin/env python
"""
Game class - Main game loop and state management
"""

import pygame
import sys
import logging
import os
from game.core.input_handler import InputHandler
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

    def __init__(self):
        """Initialize the game"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing game")

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
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
        events = pygame.event.get()

        # Wenn wir im Input-Dialog sind, Events direkt dort verarbeiten
        if self.current_state == self.states["INPUT_DIALOG"]:
            self._handle_input_dialog_events(events)
            return

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

        # Input-Handler aktualisieren
        self.input_handler.handle_events(events)
        self.input_handler.update()

    def _handle_input_dialog_events(self, events):
        """Verarbeitet Events speziell für den Input-Dialog

        Args:
            events: Liste der pygame-Events
        """
        # Input-Handler aktualisieren (für Controller-Eingaben)
        self.input_handler.handle_events(events)
        self.input_handler.update()

        # Tastatureingaben verarbeiten
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Enter-Taste: Dialog bestätigen
                    self.logger.info("Enter key pressed, confirming dialog")
                    if self.input_dialog_callback:
                        self.input_dialog_callback(self.input_dialog_text)
                    self.current_state = self.previous_state
                    self.input_dialog_active = False
                elif event.key == pygame.K_ESCAPE:
                    # Escape-Taste: Dialog abbrechen
                    self.logger.info("Escape key pressed, canceling dialog")
                    self.current_state = self.previous_state
                    self.input_dialog_active = False
                elif event.key == pygame.K_BACKSPACE:
                    # Backspace-Taste: Zeichen löschen
                    self.input_dialog_text = self.input_dialog_text[:-1]
                    self.logger.info(f"Backspace pressed, text now: {self.input_dialog_text}")
                elif event.unicode and event.unicode.isprintable():
                    # Zeichen hinzufügen (nur druckbare Zeichen)
                    self.input_dialog_text += event.unicode
                    self.logger.info(f"Character added: {event.unicode}, text now: {self.input_dialog_text}")

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
        # Multiplayer aktivieren und als Host starten
        self.multiplayer_active = True
        self.other_players = {}
        self.start_hosting()
        self.current_state = self.states["PLAYING"]

    def _join_game(self):
        """Join a multiplayer game"""
        self.logger.info("Joining a multiplayer game")
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

        self.logger.info(f"Fast forward pressed: {fast_forward_pressed}")

        if fast_forward_pressed:
            fast_forward_speed = self.settings.get("gameplay", "fast_forward_speed")
            dt *= fast_forward_speed
            self.logger.info(f"Game speed increased to {fast_forward_speed}x")

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

        self.load_resources()

        # FPS-Zähler
        fps_font = pygame.font.SysFont(None, 24)

        while self.running:
            # Zeit messen
            dt = self.clock.tick(60) / 1000.0

            # Events verarbeiten
            self.handle_events()

            # Spielzustand aktualisieren
            self.update(dt)

            # Rendern
            self.render()

            # FPS anzeigen
            fps = self.clock.get_fps()
            fps_text = fps_font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
            self.screen.blit(fps_text, (10, 570))

            # Bildschirm aktualisieren
            pygame.display.flip()

        # Multiplayer-Session beenden, falls aktiv
        if self.multiplayer_active:
            self.stop_multiplayer()

        self.logger.info("Game loop ended")
        pygame.quit()

    # Multiplayer-Methoden
    def start_hosting(self):
        """Startet eine Multiplayer-Session als Host"""
        if self.multiplayer_active:
            self.logger.warning("Multiplayer already active")
            return

        self.logger.info("Starting multiplayer session as host")
        self.multiplayer_manager.start_hosting()
        self.multiplayer_active = True

        # Spielerdaten an den Server senden
        self._send_player_data()

    def join_session(self, host: str, port: int = 8765):
        """Verbindet mit einer Multiplayer-Session

        Args:
            host: Host-Adresse
            port: Host-Port
        """
        if self.multiplayer_active:
            self.logger.warning("Multiplayer already active")
            return

        self.logger.info(f"Joining multiplayer session at {host}:{port}")
        self.multiplayer_manager.connect_to_session(host, port)
        self.multiplayer_active = True

        # Spielzustand auf PLAYING setzen
        self.current_state = self.states["PLAYING"]

        # Spielerdaten an den Server senden
        self._send_player_data()

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
            return

        # Spielerdaten sammeln
        player_data = {
            "name": self.player.name,
            "x": self.player.x,
            "y": self.player.y,
            "direction": self.player.direction,
            "moving": self.player.moving
        }

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
        self.logger.info("Showing join dialog")

        # Einfachen Dialog zur Eingabe der IP-Adresse erstellen
        self.input_dialog_active = True
        self.input_dialog_text = "localhost"
        self.input_dialog_title = "IP-Adresse eingeben:"
        self.input_dialog_callback = self._join_with_ip

        # Wechsle in den Dialog-Zustand
        self.previous_state = self.current_state
        self.current_state = self.states["INPUT_DIALOG"]

    def _join_with_ip(self, ip_address):
        """Verbindet mit der angegebenen IP-Adresse

        Args:
            ip_address: IP-Adresse des Hosts
        """
        self.logger.info(f"Joining session at {ip_address}")
        port = 8765

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

        if self.input_handler.was_pressed("a"):
            # A-Taste: Dialog bestätigen
            self.logger.info("A button pressed, confirming dialog")
            if self.input_dialog_callback:
                self.input_dialog_callback(self.input_dialog_text)
            self.current_state = self.previous_state
            self.input_dialog_active = False

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

            # Kamera-Offset anwenden
            offset = self.camera.get_offset()
            screen_x = x + offset[0]
            screen_y = y + offset[1]

            # Prüfen, ob der Spieler im sichtbaren Bereich ist
            if (0 <= screen_x <= self.screen.get_width() and
                0 <= screen_y <= self.screen.get_height()):

                # Einfache Darstellung als farbiger Kreis
                pygame.draw.circle(self.screen, (0, 0, 255), (int(screen_x), int(screen_y)), 16)

                # Spielername anzeigen
                name_text = font.render(name, True, (255, 255, 255))
                self.screen.blit(name_text, (int(screen_x) - name_text.get_width() // 2, int(screen_y) - 30))
