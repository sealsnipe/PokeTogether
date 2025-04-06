#!/usr/bin/env python
"""
GameMultiplayer - Verwaltet die Multiplayer-Funktionalität im Spiel
"""

import logging
import json
import time
from typing import Dict, List, Tuple, Callable, Any, Optional

from game.network.multiplayer_manager import MultiplayerManager
from game.entities.player import Player
from game.core.config import Config


class GameMultiplayer:
    """Verwaltet die Multiplayer-Funktionalität im Spiel"""

    def __init__(self, config: Config):
        """Initialisiert die Multiplayer-Funktionalität

        Args:
            config: Konfigurationsobjekt
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing GameMultiplayer")

        self.config = config
        self.multiplayer_manager = MultiplayerManager()
        self.multiplayer_active = False
        self.other_players = {}
        self.interpolated_players = {}
        self.force_player_data_update = False
        self.last_network_update_time = 0
        self.client_id = None  # Wird vom Server zugewiesen
        self.server_assigned_position = None  # Vom Server zugewiesene Position

        # Callbacks
        self.on_player_update = None
        self.on_player_disconnected = None
        self.on_chat_message = None
        self.on_positions_update = None  # Neuer Callback für Positionsupdates

    def initialize(self, player: Player) -> None:
        """Initialisiert die Multiplayer-Funktionalität

        Args:
            player: Der lokale Spieler
        """
        self.logger.info("Initializing multiplayer functionality")

        # Callbacks registrieren
        self.multiplayer_manager.on_player_update = self._on_player_update
        self.multiplayer_manager.on_player_disconnected = self._on_player_disconnected
        self.multiplayer_manager.on_chat_message = self._on_chat_message

        # Jitter-Puffer-Konfiguration
        self.multiplayer_manager.jitter_buffer_size = self.config.get_jitter_buffer_size()
        self.multiplayer_manager.jitter_buffer_delay = self.config.get_jitter_buffer_delay()

        # Netzwerk-Simulation
        self.multiplayer_manager.client.latency_simulation = self.config.get_latency_simulation()
        self.multiplayer_manager.client.jitter_simulation = self.config.get_jitter_simulation()

    def start_hosting(self, port: int = 8765) -> None:
        """Startet das Hosten einer Multiplayer-Sitzung

        Args:
            port: Port, auf dem der Server laufen soll
        """
        self.logger.info(f"Starting to host multiplayer session on port {port}")
        self.multiplayer_manager.start_hosting(port)
        self.multiplayer_active = True

    def connect_to_server(self, host: str = "localhost", port: int = 8765) -> None:
        """Verbindet mit einem Multiplayer-Server

        Args:
            host: Hostname oder IP-Adresse des Servers
            port: Port des Servers
        """
        self.logger.info(f"Connecting to multiplayer server at {host}:{port}")
        self.multiplayer_manager.connect_to_session(host, port)
        self.multiplayer_active = True

    def disconnect(self) -> None:
        """Trennt die Verbindung zum Multiplayer-Server"""
        self.logger.info("Disconnecting from multiplayer server")
        self.multiplayer_manager.disconnect()
        self.multiplayer_active = False
        self.other_players = {}
        self.interpolated_players = {}

    def update(self, dt: float) -> None:
        """Aktualisiert die Multiplayer-Funktionalität

        Args:
            dt: Zeitdifferenz seit dem letzten Update
        """
        if not self.multiplayer_active:
            return

        # Client-Events verarbeiten
        self._process_client_events()

        # Spielerdaten senden, wenn Update-Intervall erreicht ist
        current_time = time.time()
        update_interval = 1.0 / self.config.get_update_rate()
        time_since_last_update = current_time - self.last_network_update_time

        if self.force_player_data_update or time_since_last_update >= update_interval:
            self.logger.debug(f"[DATENFLUSS] NETWORK UPDATE INTERVAL REACHED: {time_since_last_update:.3f}s >= {update_interval:.3f}s or force_update={self.force_player_data_update}")
            self._send_player_data()
            self.last_network_update_time = current_time
            self.force_player_data_update = False
        else:
            self.logger.debug(f"[DATENFLUSS] NETWORK UPDATE INTERVAL NOT REACHED: {time_since_last_update:.3f}s < {update_interval:.3f}s")

    def _process_client_events(self) -> None:
        """Verarbeitet Client-Events"""
        if not self.multiplayer_active or not self.multiplayer_manager or not self.multiplayer_manager.client:
            return

        # Events vom Client abrufen
        events = self.multiplayer_manager.client.get_events()

        if events:
            self.logger.info(f"[DATENFLUSS] PROCESSING {len(events)} CLIENT EVENTS")

        for event in events:
            event_type = event.get("type")

            if event_type == "force_player_data_update":
                self.logger.info(f"[DATENFLUSS] RECEIVED FORCE_PLAYER_DATA_UPDATE EVENT")
                # Sofortiges Update der Spielerdaten erzwingen
                self.force_player_data_update = True
                # Sofort Spielerdaten senden, ohne auf das nächste Update zu warten
                self._send_player_data()

            elif event_type == "new_client_connected":
                self.logger.info(f"[DATENFLUSS] RECEIVED NEW_CLIENT_CONNECTED EVENT")
                # Sofortiges Update der Spielerdaten erzwingen
                self.force_player_data_update = True
                # Sofort Spielerdaten senden, ohne auf das nächste Update zu warten
                self._send_player_data()

    def _send_player_data(self) -> None:
        """Sendet die Spielerdaten an den Server"""
        if not self.multiplayer_active:
            self.logger.debug("[DATENFLUSS] NOT SENDING PLAYER DATA: Multiplayer is not active")
            return

        # Spielerdaten mit der to_network_data Methode sammeln
        player_data = self.player.to_network_data()

        # Zusätzliche Informationen hinzufügen, um die Synchronisierung zu verbessern
        player_data["instance_id"] = self.config.get_instance_id()  # Eindeutige Instanz-ID
        player_data["force_update"] = self.force_player_data_update  # Flag für erzwungenes Update
        player_data["client_time"] = time.time()  # Aktuelle Client-Zeit

        # Stellen Sie sicher, dass die Koordinaten als Zahlen vorliegen
        try:
            player_data["x"] = float(player_data.get("x", 0))
            player_data["y"] = float(player_data.get("y", 0))
        except (ValueError, TypeError):
            self.logger.error(f"[SPIELERSYNC] INVALID COORDINATES IN PLAYER DATA: player_id={self.player.player_id}, x={player_data.get('x')}, y={player_data.get('y')}")
            player_data["x"] = float(self.player.x)
            player_data["y"] = float(self.player.y)

        # Ausführliche Debug-Ausgabe für die Spielersynchronisierung
        self.logger.info(f"[SPIELERSYNC] SENDING LOCAL PLAYER DATA: player_id={self.player.player_id}, x={player_data['x']}, y={player_data['y']}, direction={self.player.direction}")
        self.logger.info(f"[DEBUG] LOCAL PLAYER POSITION: world=({player_data['x']}, {player_data['y']}), instance_id={player_data['instance_id']}")

        self.logger.info(f"[DATENFLUSS] PLAYER DATA COLLECTED: {json.dumps(player_data)}")

        # Ausführlichere Log-Ausgabe für das Senden von Spielerdaten
        self.logger.info(f"[DATENFLUSS] SENDING PLAYER UPDATE: player_id={player_data.get('player_id')}, x={player_data.get('x')}, y={player_data.get('y')}, direction={player_data.get('direction')}")
        self.logger.debug(f"[DATENFLUSS] FULL PLAYER DATA: {json.dumps(player_data)}")

        # Spielerdaten an den Server senden
        self.multiplayer_manager.send_player_update(player_data)

    def send_chat_message(self, message: str) -> None:
        """Sendet eine Chat-Nachricht an alle Spieler

        Args:
            message: Die zu sendende Nachricht
        """
        if not self.multiplayer_active:
            self.logger.debug("[DATENFLUSS] NOT SENDING CHAT MESSAGE: Multiplayer is not active")
            return

        self.logger.info(f"[DATENFLUSS] SENDING CHAT MESSAGE: {message}")
        self.multiplayer_manager.send_chat_message(message)

    def _on_player_update(self, client_id: str, player_data: dict) -> None:
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

        # Ausführliche Debug-Ausgabe für die Spielersynchronisierung
        self.logger.info(f"[SPIELERSYNC] RECEIVED REMOTE PLAYER UPDATE: client_id={client_id}, x={player_data.get('x')}, y={player_data.get('y')}, direction={player_data.get('direction')}")
        self.logger.info(f"[DEBUG] RECEIVED REMOTE PLAYER POSITION: world=({player_data.get('x')}, {player_data.get('y')}), player_id={player_data.get('player_id')}, instance_id={player_data.get('instance_id')}")

        # Ausführlichere Log-Ausgabe für Spieler-Updates
        self.logger.info(f"[DATENFLUSS] PLAYER UPDATE: Player {player_data.get('name', 'Unknown')}: x={player_data.get('x', '?')}, y={player_data.get('y', '?')}, direction={player_data.get('direction', '?')}")

        # Prüfen, ob es sich um einen neuen Spieler handelt
        is_new_player = client_id not in self.other_players
        if is_new_player:
            self.logger.info(f"[DATENFLUSS] NEW PLAYER JOINED: {player_data.get('name', 'Unknown')} (ID: {client_id})")
            # Bei einem neuen Spieler sofort unsere eigenen Daten senden
            self.force_player_data_update = True
            self._send_player_data()

        # Prüfen, ob ein erzwungenes Update vorliegt
        force_update = player_data.get("force_update", False)
        if force_update:
            self.logger.info(f"[DATENFLUSS] RECEIVED FORCED UPDATE FROM CLIENT: {client_id}")
            # Bei einem erzwungenen Update sofort unsere eigenen Daten senden
            self.force_player_data_update = True
            self._send_player_data()

        # Prüfen, ob die Spielerdaten vollständig sind
        if not player_data.get('x') or not player_data.get('y') or not player_data.get('player_id'):
            self.logger.warning(f"[DATENFLUSS] INCOMPLETE PLAYER DATA: {json.dumps(player_data)}")
            return

        # Prüfen, ob es sich um die eigenen Daten handelt
        own_player_id = self.player.player_id
        received_player_id = player_data.get("player_id")
        self.logger.info(f"[DATENFLUSS] PLAYER ID CHECK: received_player_id={received_player_id}, own_player_id={own_player_id}")

        if received_player_id == own_player_id:
            self.logger.info(f"[DATENFLUSS] IGNORING OWN PLAYER DATA")
            return

        # Spieler zur Liste hinzufügen oder aktualisieren
        self.logger.info(f"[DATENFLUSS] ADDING PLAYER TO OTHER_PLAYERS LIST: client_id={client_id}, player_data={json.dumps(player_data)}")

        # Stellen Sie sicher, dass die player_id in den Spielerdaten enthalten ist
        if "player_id" not in player_data:
            self.logger.warning(f"[SPIELERSYNC] PLAYER_ID MISSING IN PLAYER DATA: client_id={client_id}")
            # Verwenden Sie die client_id als Fallback, wenn keine player_id vorhanden ist
            player_data["player_id"] = client_id

        # Stellen Sie sicher, dass die Koordinaten als Zahlen vorliegen
        try:
            player_data["x"] = float(player_data.get("x", 0))
            player_data["y"] = float(player_data.get("y", 0))
        except (ValueError, TypeError):
            self.logger.error(f"[SPIELERSYNC] INVALID COORDINATES IN PLAYER DATA: client_id={client_id}, x={player_data.get('x')}, y={player_data.get('y')}")
            player_data["x"] = 0.0
            player_data["y"] = 0.0

        # Prüfen, ob die Koordinaten in einem sinnvollen Bereich liegen
        # Wenn die Koordinaten zu weit vom Ursprung entfernt sind, setze sie auf die Standardposition
        if abs(player_data["x"]) > 2000 or abs(player_data["y"]) > 2000:
            self.logger.warning(f"[SPIELERSYNC] COORDINATES OUT OF RANGE: client_id={client_id}, x={player_data['x']}, y={player_data['y']}")
            # Setze auf Standardposition basierend auf der instance_id
            instance_id = player_data.get("instance_id", "")
            if "player1" in instance_id:
                player_data["x"] = 460.0
                player_data["y"] = 448.0
            elif "player2" in instance_id:
                player_data["x"] = 560.0
                player_data["y"] = 448.0

        self.other_players[client_id] = player_data
        self.logger.info(f"[DATENFLUSS] PLAYER ADDED TO OTHER_PLAYERS LIST: client_id={client_id}")
        self.logger.info(f"[SPIELERSYNC] PLAYER ADDED: client_id={client_id}, player_id={player_data.get('player_id')}, x={player_data.get('x')}, y={player_data.get('y')}")

        # Prüfen, ob die Liste korrekt aktualisiert wurde
        self.logger.info(f"[DATENFLUSS] UPDATED OTHER_PLAYERS LIST. Current count: {len(self.other_players)}")

        # Prüfen, ob der Spieler in der Liste ist
        player_list = [{"id": pid, "name": pdata.get("name", "Unknown"), "x": pdata.get("x", 0), "y": pdata.get("y", 0), "player_id": pdata.get("player_id", "Unknown")} for pid, pdata in self.other_players.items()]
        self.logger.info(f"[DATENFLUSS] OTHER_PLAYERS LIST: {json.dumps(player_list)}")

        # Prüfen, ob der Spieler in der Liste ist
        if client_id in self.other_players:
            self.logger.info(f"[DATENFLUSS] PLAYER VERIFICATION: client_id={client_id} IS in other_players list")
        else:
            self.logger.error(f"[DATENFLUSS] PLAYER VERIFICATION FAILED: client_id={client_id} IS NOT in other_players list")

        # Callback aufrufen, wenn vorhanden
        if self.on_player_update:
            self.on_player_update(client_id, player_data)

    def _on_player_disconnected(self, client_id: str) -> None:
        """Callback für Spieler-Disconnects

        Args:
            client_id: Client-ID des Spielers
        """
        self.logger.info(f"[DATENFLUSS] PLAYER DISCONNECTED: client_id={client_id}")

        # Spieler aus der Liste entfernen
        if client_id in self.other_players:
            player_name = self.other_players[client_id].get("name", "Unknown")
            self.logger.info(f"[DATENFLUSS] REMOVING PLAYER FROM OTHER_PLAYERS LIST: client_id={client_id}, player_name={player_name}")
            del self.other_players[client_id]
            self.logger.info(f"[DATENFLUSS] PLAYER REMOVED FROM OTHER_PLAYERS LIST: client_id={client_id}")
        else:
            self.logger.warning(f"[DATENFLUSS] PLAYER NOT FOUND IN OTHER_PLAYERS LIST: client_id={client_id}")

        # Interpolierten Spieler entfernen, wenn vorhanden
        if client_id in self.interpolated_players:
            self.logger.info(f"[DATENFLUSS] REMOVING PLAYER FROM INTERPOLATED_PLAYERS LIST: client_id={client_id}")
            del self.interpolated_players[client_id]
            self.logger.info(f"[DATENFLUSS] PLAYER REMOVED FROM INTERPOLATED_PLAYERS LIST: client_id={client_id}")

        # Callback aufrufen, wenn vorhanden
        if self.on_player_disconnected:
            self.on_player_disconnected(client_id)

    def _on_chat_message(self, client_id: str, player_name: str, message: str) -> None:
        """Callback für Chat-Nachrichten

        Args:
            client_id: Client-ID des Spielers
            player_name: Name des Spielers
            message: Chat-Nachricht
        """
        self.logger.info(f"Chat message from {player_name}: {message}")

        # Callback aufrufen, wenn vorhanden
        if self.on_chat_message:
            self.on_chat_message(client_id, player_name, message)

    def set_player(self, player: Player) -> None:
        """Setzt den lokalen Spieler

        Args:
            player: Der lokale Spieler
        """
        self.player = player

    def update_other_players(self) -> None:
        """Aktualisiert die anderen Spieler (Interpolation oder exakte Positionierung)"""
        if not self.multiplayer_active:
            return

        for player_id, player_data in self.other_players.items():
            # Erstelle einen temporären Spieler für die Interpolation oder exakte Positionierung
            if player_id not in self.interpolated_players:
                temp_player = Player()
                temp_player.x = player_data.get("x", 0)
                temp_player.y = player_data.get("y", 0)
                temp_player.direction = player_data.get("direction", "down")
                temp_player.name = player_data.get("name", "Player")
                temp_player.character_type = player_data.get("character_type", "Red")
                self.interpolated_players[player_id] = temp_player

            # Prüfe, ob exakte Positionierung aktiviert ist
            if self.config.get_exact_positioning():
                # Exakte Positionierung ohne Interpolation
                self.logger.debug(f"Using exact positioning for player {player_id}")
                # Direkte Übernahme der Position ohne Interpolation
                self.interpolated_players[player_id].x = player_data.get("x", self.interpolated_players[player_id].x)
                self.interpolated_players[player_id].y = player_data.get("y", self.interpolated_players[player_id].y)
                self.interpolated_players[player_id].direction = player_data.get("direction", self.interpolated_players[player_id].direction)
                # Setze die Geschwindigkeit auf 0, um Nachschleppen zu vermeiden
                self.interpolated_players[player_id].velocity_x = 0
                self.interpolated_players[player_id].velocity_y = 0
                # Setze den Bewegungsstatus basierend auf den Daten
                self.interpolated_players[player_id].moving = player_data.get("moving", False)
            elif self.config.get_interpolation():
                # Interpoliere die Position des Spielers
                self.logger.debug(f"Using interpolation for player {player_id}")
                self.interpolated_players[player_id].interpolate(player_data)
            else:
                # Fallback: Einfache Positionierung ohne Interpolation
                self.logger.debug(f"Using simple positioning for player {player_id}")
                self.interpolated_players[player_id].x = player_data.get("x", self.interpolated_players[player_id].x)
                self.interpolated_players[player_id].y = player_data.get("y", self.interpolated_players[player_id].y)
                self.interpolated_players[player_id].direction = player_data.get("direction", self.interpolated_players[player_id].direction)

            # Aktualisiere die Spielerdaten mit den interpolierten oder exakten Werten
            self.other_players[player_id]["x"] = self.interpolated_players[player_id].x
            self.other_players[player_id]["y"] = self.interpolated_players[player_id].y

    def get_other_players(self) -> Dict[str, Dict[str, Any]]:
        """Gibt die anderen Spieler zurück

        Returns:
            Dict[str, Dict[str, Any]]: Die anderen Spieler
        """
        return self.other_players

    def get_interpolated_players(self) -> Dict[str, Player]:
        """Gibt die interpolierten Spieler zurück

        Returns:
            Dict[str, Player]: Die interpolierten Spieler
        """
        return self.interpolated_players
