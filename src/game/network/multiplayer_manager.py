#!/usr/bin/env python
"""
Multiplayer-Manager - Verwaltet die Multiplayer-Funktionalität im Spiel
"""

import asyncio
import json
import logging
import threading
import socket
import time
from typing import Dict, List, Any, Optional, Callable

from game.network.server import GameServer
from game.network.client import GameClient

class MultiplayerManager:
    """Manager for multiplayer functionality"""

    def __init__(self):
        """Initialize the multiplayer manager"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== INITIALIZING MULTIPLAYER MANAGER ===")
        self.server = GameServer()
        self.client = GameClient()
        self.is_host = False
        self.server_thread = None
        self.server_loop = None
        self.local_player_data = {}
        self.on_player_update = None
        self.on_player_disconnected = None
        self.on_chat_message = None
        self.on_welcome = None
        self.on_positions_update = None

        # Jitter-Pufferung
        self.jitter_buffer = {}  # Dict von client_id -> Liste von Nachrichten
        self.last_processed_time = {}  # Dict von client_id -> Zeitpunkt der letzten Verarbeitung
        self.jitter_buffer_size = None  # Wird später aus der Konfiguration geladen
        self.jitter_buffer_delay = None  # Wird später aus der Konfiguration geladen

        # Register custom message handlers
        self.client.register_handler("player_update", self._handle_player_update)
        self.client.register_handler("player_disconnected", self._handle_player_disconnected)
        self.client.register_handler("chat_message", self._handle_chat_message)

        self.logger.debug("Multiplayer manager initialized with:")
        self.logger.debug(f"- is_host: {self.is_host}")
        self.logger.debug(f"- client connected: {self.client.connected}")

    def start_hosting(self, port: int = 8765):
        """Start hosting a multiplayer session

        Args:
            port: Port to listen on

        Returns:
            bool: True if hosting was started successfully, False otherwise
        """
        self.logger.info("=== START_HOSTING CALLED ===")
        if self.is_host:
            self.logger.warning("Already hosting a session")
            return False

        if self.client.connected:
            self.logger.warning("Already connected to a session")
            return False

        self.logger.info(f"Starting to host a multiplayer session on port {port}")

        try:
            # Create a new event loop for the server thread
            self.server_loop = asyncio.new_event_loop()
            self.logger.debug("Created new event loop for server thread")

            # Start the server in a separate thread
            self.server_thread = threading.Thread(
                target=self._run_server_loop,
                args=(self.server_loop, port),
                daemon=True
            )
            self.logger.debug("Created server thread")
            self.server_thread.start()
            self.logger.debug("Started server thread")

            # Längere Pause, um dem Server Zeit zum Starten zu geben
            self.logger.debug("Waiting for server to start...")
            time.sleep(1.0)
            self.logger.debug("Wait complete")

            # Connect to our own server
            self.logger.debug("Connecting to own server...")
            success = self.connect_to_session("localhost", port)
            if success:
                self.is_host = True
                self.logger.info("Successfully started hosting multiplayer session")
                self.logger.info(f"Host status: is_host={self.is_host}, client_connected={self.client.connected}")
                return True
            else:
                self.logger.error("Failed to connect to own server")
                return False
        except Exception as e:
            self.logger.error(f"Error starting to host multiplayer session: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def stop_hosting(self):
        """Stop hosting the multiplayer session"""
        if not self.is_host:
            return

        self.logger.info("Stopping multiplayer session")

        # Disconnect from the server
        self.disconnect_from_session()

        # Stop the server
        if self.server_loop and self.server_loop.is_running():
            asyncio.run_coroutine_threadsafe(self.server.stop(), self.server_loop)

        # Wait for the server thread to finish
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)

        self.is_host = False

    def set_network_simulation(self, latency: int = 0, jitter: int = 0) -> None:
        """Set network simulation parameters

        Args:
            latency: Latency in milliseconds (default: 0)
            jitter: Jitter in milliseconds (default: 0)
        """
        self.logger.info(f"=== SETTING NETWORK SIMULATION: LATENCY={latency}ms, JITTER={jitter}ms ===")
        self.client.set_network_simulation(latency, jitter)

    def connect_to_session(self, host: str, port: int = 8765, latency: int = 0, jitter: int = 0, config = None):
        """Connect to a multiplayer session

        Args:
            host: Host address
            port: Host port
            latency: Latency simulation in milliseconds (default: 0)
            jitter: Jitter simulation in milliseconds (default: 0)
            config: Configuration object

        Returns:
            bool: True if connection was initiated successfully, False otherwise
        """
        self.logger.info(f"=== CONNECT_TO_SESSION CALLED: {host}:{port} ===")
        if self.client.connected:
            self.logger.warning("Already connected to a session")
            return False

        # Lade die Jitter-Pufferung-Konfiguration, wenn verfügbar
        if config:
            self.jitter_buffer_size = config.get_jitter_buffer_size()
            self.jitter_buffer_delay = config.get_jitter_buffer_delay()
            self.logger.info(f"Loaded jitter buffer configuration: size={self.jitter_buffer_size}, delay={self.jitter_buffer_delay}s")
        else:
            # Standardwerte verwenden
            self.jitter_buffer_size = 3
            self.jitter_buffer_delay = 0.05
            self.logger.info(f"Using default jitter buffer configuration: size={self.jitter_buffer_size}, delay={self.jitter_buffer_delay}s")

        # Netzwerk-Simulation konfigurieren, wenn angegeben
        if latency > 0 or jitter > 0:
            self.set_network_simulation(latency, jitter)

        self.logger.info(f"Connecting to multiplayer session at {host}:{port}")
        try:
            success = self.client.connect(host, port)
            self.logger.info(f"Connection attempt result: {success}")
            self.logger.info(f"Client connected status: {self.client.connected}")
            return success
        except Exception as e:
            self.logger.error(f"Error connecting to session: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def disconnect_from_session(self):
        """Disconnect from the current session"""
        if not self.client.connected:
            return

        self.logger.info("Disconnecting from multiplayer session")
        self.client.disconnect()

    def update_player(self, player_data: Dict[str, Any]):
        """Update local player data and send to server

        Args:
            player_data: Player data to update
        """
        self.local_player_data = player_data

        if self.client.connected:
            self.client.send_player_update(player_data)

    def send_chat_message(self, message: str):
        """Send a chat message

        Args:
            message: Message to send
        """
        if self.client.connected:
            self.client.send_chat_message(message)

    def get_players(self) -> Dict[str, Dict[str, Any]]:
        """Get all players in the session

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of player data by client ID
        """
        return self.client.players

    def is_connected(self) -> bool:
        """Check if connected to a session

        Returns:
            bool: True if connected to a session
        """
        return self.client.connected

    def get_local_ip(self) -> str:
        """Get the local IP address

        Returns:
            str: Local IP address
        """
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't need to be reachable
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def set_player_update_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Set callback for player updates

        Args:
            callback: Function to call when a player is updated
        """
        self.on_player_update = callback

    def set_player_disconnected_callback(self, callback: Callable[[str, str], None]):
        """Set callback for player disconnections

        Args:
            callback: Function to call when a player disconnects
        """
        self.on_player_disconnected = callback

    def set_chat_message_callback(self, callback: Callable[[str, str], None]):
        """Set callback for chat messages

        Args:
            callback: Function to call when a chat message is received
        """
        self.on_chat_message = callback

    def _run_server_loop(self, loop, port: int):
        """Run the server event loop in a separate thread

        Args:
            loop: Event loop to run
            port: Port to listen on
        """
        self.logger.info(f"=== RUNNING SERVER LOOP ON PORT {port} ===")
        asyncio.set_event_loop(loop)

        try:
            # Start the server
            self.logger.debug("Starting server in event loop...")
            success = loop.run_until_complete(self.server.start())

            if not success:
                self.logger.error("Failed to start server, not running event loop")
                return

            self.logger.info("=== SERVER STARTED SUCCESSFULLY, RUNNING EVENT LOOP ===")

            # Teste, ob der Server auf dem Port erreichbar ist
            self._test_server_connection("localhost", port)

            # Keep the loop running
            self.logger.debug("Running event loop forever...")
            loop.run_forever()
        except Exception as e:
            self.logger.error(f"=== ERROR IN SERVER LOOP: {e} ===")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            self.logger.debug("Closing event loop")
            loop.close()

    def _test_server_connection(self, host, port):
        """Testet, ob der Server auf dem angegebenen Port erreichbar ist

        Args:
            host: Hostname oder IP-Adresse
            port: Port
        """
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((host, port))
            s.close()

            if result == 0:
                self.logger.info(f"Server is reachable at {host}:{port}")
            else:
                self.logger.error(f"Server is NOT reachable at {host}:{port}, error code: {result}")

            # Versuche auch, die externe IP zu ermitteln
            self._get_external_ip()
        except Exception as e:
            self.logger.error(f"Error testing server connection: {e}")

    def _get_external_ip(self):
        """Versucht, die externe IP-Adresse zu ermitteln"""
        try:
            import urllib.request
            import json

            # Verschiedene Dienste zur IP-Ermittlung
            services = [
                "https://api.ipify.org?format=json",
                "https://ipinfo.io/json"
            ]

            for service in services:
                try:
                    response = urllib.request.urlopen(service, timeout=2)
                    data = json.loads(response.read().decode())

                    if "ip" in data:
                        self.logger.info(f"External IP address: {data['ip']}")
                        break
                except:
                    continue
        except Exception as e:
            self.logger.error(f"Error getting external IP: {e}")

    async def _handle_player_update(self, data: Dict[str, Any]):
        """Handle player update message with jitter buffering

        Args:
            data: Player update message data
        """
        # Vollständige Nachricht loggen
        self.logger.info(f"[DATENFLUSS] MULTIPLAYER_MANAGER RECEIVED MESSAGE: {json.dumps(data)}")

        client_id = data.get("client_id")
        timestamp = data.get("timestamp", time.time())

        # Jitter-Pufferung: Füge die Nachricht zum Puffer hinzu
        if client_id not in self.jitter_buffer:
            self.jitter_buffer[client_id] = []
            self.last_processed_time[client_id] = 0

        # Füge die Nachricht zum Puffer hinzu
        self.jitter_buffer[client_id].append((timestamp, data))
        self.logger.debug(f"[JITTER] Added message to buffer for client {client_id}. Buffer size: {len(self.jitter_buffer[client_id])}")

        # Sortiere den Puffer nach Zeitstempel
        self.jitter_buffer[client_id].sort(key=lambda x: x[0])

        # Begrenze die Puffergröße
        if len(self.jitter_buffer[client_id]) > self.jitter_buffer_size:
            # Entferne die älteste Nachricht, wenn der Puffer voll ist
            self.jitter_buffer[client_id].pop(0)
            self.logger.debug(f"[JITTER] Removed oldest message from buffer for client {client_id}")

        # Prüfe, ob es Zeit ist, eine Nachricht zu verarbeiten
        current_time = time.time()
        time_since_last_processed = current_time - self.last_processed_time[client_id]

        if time_since_last_processed >= self.jitter_buffer_delay and self.jitter_buffer[client_id]:
            # Verarbeite die älteste Nachricht im Puffer
            _, buffered_data = self.jitter_buffer[client_id].pop(0)
            self.last_processed_time[client_id] = current_time

            # Extrahiere die Spielerdaten direkt aus der Nachricht
            # Entferne die Schlüssel "type" und "client_id", um nur die Spielerdaten zu behalten
            player_data = {k: v for k, v in buffered_data.items() if k not in ["type", "client_id"]}

            self.logger.info(f"[DATENFLUSS] MULTIPLAYER_MANAGER EXTRACTED PLAYER DATA: {json.dumps(player_data)}")
            self.logger.debug(f"[JITTER] Processing message from buffer for client {client_id}. Remaining buffer size: {len(self.jitter_buffer[client_id])}")

            # Call the callback if registered
            if self.on_player_update:
                self.logger.info(f"[DATENFLUSS] CALLING ON_PLAYER_UPDATE CALLBACK: client_id={client_id}, player_data={json.dumps(player_data)}")
                try:
                    self.logger.info(f"[DATENFLUSS] CALLBACK TYPE: {type(self.on_player_update).__name__}")
                    self.on_player_update(client_id, player_data)
                    self.logger.info(f"[DATENFLUSS] ON_PLAYER_UPDATE CALLBACK CALLED SUCCESSFULLY")
                except Exception as e:
                    self.logger.error(f"[DATENFLUSS] ERROR CALLING ON_PLAYER_UPDATE CALLBACK: {e}")
                    import traceback
                    self.logger.error(f"[DATENFLUSS] TRACEBACK: {traceback.format_exc()}")
            else:
                self.logger.warning(f"[DATENFLUSS] ON_PLAYER_UPDATE CALLBACK NOT REGISTERED")

    async def _handle_player_disconnected(self, data: Dict[str, Any]):
        """Handle player disconnected message

        Args:
            data: Player disconnected message data
        """
        client_id = data.get("client_id")
        player_name = data.get("player_name", "Unknown")

        # Call the callback if registered
        if self.on_player_disconnected:
            self.on_player_disconnected(client_id, player_name)

    async def _handle_chat_message(self, data: Dict[str, Any]):
        """Handle chat message

        Args:
            data: Chat message data
        """
        client_id = data.get("client_id")
        player_name = data.get("player_name", "Unknown")
        message = data.get("message", "")

        self.logger.info(f"[DATENFLUSS] RECEIVED CHAT MESSAGE: {player_name}: {message}")

        # Call the callback if registered
        if self.on_chat_message:
            self.logger.info(f"[DATENFLUSS] CALLING ON_CHAT_MESSAGE CALLBACK: {player_name}: {message}")
            try:
                self.logger.info(f"[DATENFLUSS] CALLBACK TYPE: {type(self.on_chat_message).__name__}")
                self.on_chat_message(player_name, message)
                self.logger.info(f"[DATENFLUSS] ON_CHAT_MESSAGE CALLBACK CALLED SUCCESSFULLY")
            except Exception as e:
                self.logger.error(f"[DATENFLUSS] ERROR CALLING ON_CHAT_MESSAGE CALLBACK: {e}")
                import traceback
                self.logger.error(f"[DATENFLUSS] TRACEBACK: {traceback.format_exc()}")
        else:
            self.logger.warning(f"[DATENFLUSS] ON_CHAT_MESSAGE CALLBACK NOT REGISTERED")

    def send_player_update(self, player_data):
        """Send player data to the server

        Args:
            player_data: Player data to send
        """
        self.logger.info(f"[DATENFLUSS] SENDING PLAYER UPDATE: {json.dumps(player_data)}")

        # Speichere die lokalen Spielerdaten
        self.local_player_data = player_data

        # Sende die Daten an den Server
        if self.client.connected:
            # Füge Zeitstempel hinzu
            player_data_with_timestamp = player_data.copy()
            player_data_with_timestamp["timestamp"] = time.time()

            # Wir senden die Spielerdaten direkt ohne zusätzliche Verschachtelung
            self.logger.info(f"[DATENFLUSS] SENDING MESSAGE TO SERVER: {json.dumps(player_data_with_timestamp)}")

            self.client.send_message("player_update", player_data_with_timestamp)
            self.logger.debug(f"Player update sent with timestamp: {player_data_with_timestamp['timestamp']}")
        else:
            self.logger.warning("Cannot send player update: not connected to server")
