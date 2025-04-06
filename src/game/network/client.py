#!/usr/bin/env python
"""
Client-Modul - Implementiert die Client-Seite für Multiplayer
"""

import asyncio
import json
import logging
import threading
import time
import random
from typing import Dict, List, Any, Optional, Callable
import websockets

class GameClient:
    """Game client for connecting to a multiplayer session"""

    def __init__(self):
        """Initialize the game client"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== INITIALIZING GAME CLIENT ===")
        self.websocket = None
        self.client_id = None
        self.connected = False
        self.running = False
        self.players = {}
        self.message_handlers = {}
        self.event_loop = None
        self.client_thread = None
        self.events = []  # Liste für Client-Events

        # Netzwerk-Simulation
        self.latency_simulation = 0  # Latenz in Millisekunden
        self.jitter_simulation = 0  # Jitter in Millisekunden

        # Register default message handlers
        self.register_handler("welcome", self._handle_welcome)
        self.register_handler("player_update", self._handle_player_update)
        self.register_handler("player_disconnected", self._handle_player_disconnected)
        self.register_handler("chat_message", self._handle_chat_message)
        self.register_handler("connection_acknowledged", self._handle_connection_acknowledged)
        self.register_handler("new_client_connected", self._handle_new_client_connected)

        self.logger.debug("Game client initialized with:")
        self.logger.debug(f"- connected: {self.connected}")
        self.logger.debug(f"- client_id: {self.client_id}")

    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler

        Args:
            message_type: Type of message to handle
            handler: Function to call when message is received
        """
        self.message_handlers[message_type] = handler

    def set_network_simulation(self, latency: int = 0, jitter: int = 0) -> None:
        """Set network simulation parameters

        Args:
            latency: Latency in milliseconds (default: 0)
            jitter: Jitter in milliseconds (default: 0)
        """
        self.latency_simulation = latency
        self.jitter_simulation = jitter
        self.logger.info(f"=== NETWORK SIMULATION SET: LATENCY={latency}ms, JITTER={jitter}ms ===")

    def connect(self, host: str, port: int = 8765):
        """Connect to a game server

        Args:
            host: Server host address
            port: Server port

        Returns:
            bool: True if connection was initiated successfully, False otherwise
        """
        self.logger.info(f"=== CLIENT.CONNECT CALLED: {host}:{port} ===")

        # Log network simulation settings
        if self.latency_simulation > 0 or self.jitter_simulation > 0:
            self.logger.info(f"=== NETWORK SIMULATION ACTIVE: LATENCY={self.latency_simulation}ms, JITTER={self.jitter_simulation}ms ===")

        if self.connected:
            self.logger.warning("Already connected to a server")
            return False

        self.logger.info(f"Connecting to server at {host}:{port}")

        try:
            # Create a new event loop for the client thread
            self.event_loop = asyncio.new_event_loop()
            self.logger.debug("Created new event loop for client thread")

            # Start the client in a separate thread
            self.client_thread = threading.Thread(
                target=self._run_client_loop,
                args=(self.event_loop, host, port),
                daemon=True
            )
            self.logger.debug("Created client thread")
            self.client_thread.start()
            self.logger.debug("Started client thread")

            # Warte kurz, um zu sehen, ob die Verbindung hergestellt wird
            time.sleep(0.5)
            self.logger.info(f"Connection status after thread start: {self.connected}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating client thread: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def disconnect(self):
        """Disconnect from the server"""
        if not self.connected:
            return

        self.logger.info("Disconnecting from server")
        self.running = False

        # Schedule the disconnect coroutine in the client thread
        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(self._disconnect(), self.event_loop)

        # Wait for the client thread to finish
        if self.client_thread and self.client_thread.is_alive():
            self.client_thread.join(timeout=2.0)

        self.client_id = None
        self.connected = False
        self.players = {}

    def send_player_update(self, player_data: Dict[str, Any]):
        """Send player update to the server

        Args:
            player_data: Player data to send
        """
        if not self.connected:
            self.logger.warning("Not connected to a server")
            return

        # Für player_update verwenden wir eine spezielle Struktur
        message = {
            "type": "player_update",
            **player_data  # Entpacke die Spielerdaten direkt in die Nachricht
        }

        # Schedule the send coroutine in the client thread
        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_message_async(message), self.event_loop)

    def send_chat_message(self, message: str):
        """Send a chat message to the server

        Args:
            message: Chat message to send
        """
        if not self.connected:
            self.logger.warning("Not connected to a server")
            return

        data = {
            "type": "chat_message",
            "message": message
        }

        # Schedule the send coroutine in the client thread
        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_message_async(data), self.event_loop)

    def _run_client_loop(self, loop, host: str, port: int):
        """Run the client event loop in a separate thread

        Args:
            loop: Event loop to run
            host: Server host address
            port: Server port
        """
        self.logger.info(f"=== RUNNING CLIENT LOOP FOR {host}:{port} ===")
        asyncio.set_event_loop(loop)

        try:
            self.logger.debug(f"Connecting to server at {host}:{port} and listening for messages...")
            loop.run_until_complete(self._connect_and_listen(host, port))
        except Exception as e:
            self.logger.error(f"=== ERROR IN CLIENT LOOP: {e} ===")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            self.logger.debug("Closing client event loop")
            loop.close()

    async def _connect_and_listen(self, host: str, port: int):
        """Connect to the server and listen for messages

        Args:
            host: Server host address
            port: Server port
        """
        self.logger.info(f"=== CONNECTING AND LISTENING TO {host}:{port} ===")
        # Verwende die Standard-URI ohne Pfad
        uri = f"ws://{host}:{port}"
        self.logger.info(f"WebSocket client URI: {uri}")

        # Teste zuerst, ob der Server auf dem Port erreichbar ist
        self.logger.debug(f"Testing server connection to {host}:{port}...")
        connection_test_result = self._test_server_connection(host, port)
        self.logger.debug(f"Server connection test result: {connection_test_result}")

        try:
            self.running = True

            # Verbindungstimeout setzen
            try:
                self.logger.info(f"=== ATTEMPTING TO CONNECT TO {uri} WITH 10 SECOND TIMEOUT ===")
                # Versuche, eine Verbindung mit erhöhtem Timeout herzustellen
                self.logger.debug(f"[DATENFLUSS] WebSocket connection attempt to {uri}")
                websocket = await asyncio.wait_for(
                    websockets.connect(uri),
                    timeout=10.0  # 10 Sekunden Timeout
                )

                self.websocket = websocket
                self.connected = True
                self.logger.info(f"=== SUCCESSFULLY CONNECTED TO SERVER AT {uri} ===")
                self.logger.info(f"[DATENFLUSS] WebSocket connection established successfully")
                # Add a clear marker for automated testing
                print("SUCCESSFULLY CONNECTED TO MULTIPLAYER SESSION")

                # Debug-Ausgabe für den Verbindungsstatus
                print(f"[CONNECTION_STATUS] CONNECTED TO SERVER: {self.connected}")

                # Sende eine Bestätigung an den Server
                await self._send_message_async({
                    "type": "connection_confirmation",
                    "client_info": {
                        "hostname": self._get_hostname(),
                        "ip": self._get_local_ip()
                    }
                })

                # Listen for messages from the server
                self.logger.info(f"[DATENFLUSS] STARTING MESSAGE LISTENER LOOP")
                while self.running:
                    try:
                        self.logger.debug(f"[DATENFLUSS] WAITING FOR MESSAGE FROM SERVER")
                        message = await websocket.recv()
                        self.logger.info(f"[DATENFLUSS] RECEIVED MESSAGE FROM SERVER: {message[:100]}..." if len(message) > 100 else f"[DATENFLUSS] RECEIVED MESSAGE FROM SERVER: {message}")
                        await self._process_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.info("[DATENFLUSS] CONNECTION TO SERVER CLOSED")
                        break
                    except Exception as e:
                        self.logger.error(f"[DATENFLUSS] ERROR PROCESSING MESSAGE: {e}")
                        import traceback
                        self.logger.error(f"[DATENFLUSS] TRACEBACK: {traceback.format_exc()}")

            except asyncio.TimeoutError:
                self.logger.error(f"[DATENFLUSS] CONNECTION TIMEOUT: Could not connect to {uri} within 10 seconds")
                print(f"[CONNECTION_ERROR] TIMEOUT: Could not connect to server within 10 seconds")
                return False
            except websockets.exceptions.InvalidStatusCode as e:
                self.logger.error(f"[DATENFLUSS] INVALID STATUS CODE: {e} when connecting to {uri}")
                print(f"[CONNECTION_ERROR] INVALID STATUS: {str(e)}")
                return False
            except ConnectionRefusedError:
                self.logger.error(f"[DATENFLUSS] CONNECTION REFUSED: Server at {uri} refused connection")
                print(f"[CONNECTION_ERROR] REFUSED: Server refused connection")
                return False
            except Exception as e:
                self.logger.error(f"[DATENFLUSS] UNEXPECTED ERROR: {e} when connecting to {uri}")
                print(f"[CONNECTION_ERROR] FAILED: {str(e)}")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to server: {e}")
        finally:
            self.connected = False
            self.websocket = None
            self.logger.info("Disconnected from server")

    def _test_server_connection(self, host, port):
        """Testet, ob der Server auf dem angegebenen Port erreichbar ist

        Args:
            host: Hostname oder IP-Adresse
            port: Port

        Returns:
            bool: True, wenn der Server erreichbar ist, False sonst
        """
        self.logger.info(f"=== TESTING SERVER CONNECTION: {host}:{port} ===")
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)  # Längerer Timeout
            self.logger.debug(f"Attempting to connect to {host}:{port}...")
            result = s.connect_ex((host, port))
            s.close()

            if result == 0:
                self.logger.info(f"Server is reachable at {host}:{port}")
                # Versuche auch, die lokale IP zu ermitteln
                self._print_local_ip_addresses()
                return True
            else:
                self.logger.error(f"Server is NOT reachable at {host}:{port}, error code: {result}")
                # Versuche auch, die lokale IP zu ermitteln
                self._print_local_ip_addresses()
                return False
        except Exception as e:
            self.logger.error(f"Error testing server connection: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _get_hostname(self) -> str:
        """Gibt den Hostnamen des Clients zurück

        Returns:
            str: Hostname
        """
        try:
            import socket
            return socket.gethostname()
        except Exception as e:
            self.logger.error(f"Error getting hostname: {e}")
            return "unknown"

    def _get_local_ip(self) -> str:
        """Gibt die lokale IP-Adresse des Clients zurück

        Returns:
            str: Lokale IP-Adresse
        """
        try:
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception as e:
            self.logger.error(f"Error getting local IP: {e}")
            return "0.0.0.0"

    def _print_local_ip_addresses(self):
        """Gibt alle lokalen IP-Adressen aus"""
        try:
            import socket
            hostname = socket.gethostname()
            self.logger.info(f"Client hostname: {hostname}")

            # Alle IP-Adressen des Hosts ausgeben
            ip_addresses = socket.getaddrinfo(hostname, None)
            self.logger.info("Client available IP addresses:")
            for ip in ip_addresses:
                if ip[0] == socket.AF_INET:  # Nur IPv4-Adressen
                    self.logger.info(f"  - {ip[4][0]}")
        except Exception as e:
            self.logger.error(f"Error getting IP addresses: {e}")

    async def _disconnect(self):
        """Disconnect from the server"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def _send_message(self, data: Dict[str, Any]):
        """Send a message to the server

        Args:
            data: Message data to send
        """
        if not self.websocket:
            return

        try:
            message = json.dumps(data)

            # Latenz-Simulation anwenden, wenn aktiviert
            if self.latency_simulation > 0 or self.jitter_simulation > 0:
                # Berechne die tatsächliche Verzögerung (Latenz + zufälliger Jitter)
                delay = self.latency_simulation / 1000.0  # Umrechnung in Sekunden

                if self.jitter_simulation > 0:
                    # Zufälligen Jitter zwischen -jitter und +jitter hinzufügen
                    jitter = random.uniform(-self.jitter_simulation, self.jitter_simulation) / 1000.0
                    delay += jitter

                # Stelle sicher, dass die Verzögerung nicht negativ ist
                delay = max(0, delay)

                self.logger.debug(f"Simulating network delay: {delay:.3f}s")
                await asyncio.sleep(delay)

            # Nachricht senden
            await self.websocket.send(message)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    async def _process_message(self, message: str):
        """Process a message from the server

        Args:
            message: Message from the server
        """
        try:
            # Latenz-Simulation anwenden, wenn aktiviert (für eingehende Nachrichten)
            if self.latency_simulation > 0 or self.jitter_simulation > 0:
                # Berechne die tatsächliche Verzögerung (Latenz + zufälliger Jitter)
                delay = self.latency_simulation / 1000.0  # Umrechnung in Sekunden

                if self.jitter_simulation > 0:
                    # Zufälligen Jitter zwischen -jitter und +jitter hinzufügen
                    jitter = random.uniform(-self.jitter_simulation, self.jitter_simulation) / 1000.0
                    delay += jitter

                # Stelle sicher, dass die Verzögerung nicht negativ ist
                delay = max(0, delay)

                self.logger.debug(f"Simulating network delay for incoming message: {delay:.3f}s")
                await asyncio.sleep(delay)

            data = json.loads(message)
            message_type = data.get("type", "")

            self.logger.info(f"[DATENFLUSS] PROCESSING MESSAGE: type={message_type}, data={message[:100]}..." if len(message) > 100 else f"[DATENFLUSS] PROCESSING MESSAGE: type={message_type}, data={message}")

            # Call the appropriate handler for this message type
            if message_type in self.message_handlers:
                self.logger.info(f"[DATENFLUSS] CALLING HANDLER FOR MESSAGE TYPE: {message_type}")
                await self.message_handlers[message_type](data)
            else:
                self.logger.warning(f"[DATENFLUSS] UNKNOWN MESSAGE TYPE: {message_type}")

        except json.JSONDecodeError:
            self.logger.error("Invalid JSON from server")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    async def _handle_welcome(self, data: Dict[str, Any]):
        """Handle welcome message from the server

        Args:
            data: Welcome message data
        """
        self.client_id = data.get("client_id")
        self.players = data.get("players", {})

        self.logger.info(f"Received welcome message. Client ID: {self.client_id}")
        self.logger.info(f"Current players: {len(self.players)}")

        # Signal to force an immediate player data update
        # This will be picked up by the game loop to send player data
        # even if the player hasn't moved
        self.logger.info(f"[DATENFLUSS] SIGNALING FORCE_PLAYER_DATA_UPDATE AFTER WELCOME MESSAGE")
        # We'll use a custom event to signal this
        self.events.append({"type": "force_player_data_update"})

    async def _handle_player_update(self, data: Dict[str, Any]):
        """Handle player update message from the server

        Args:
            data: Player update message data
        """
        # Vollständige Nachricht loggen
        self.logger.info(f"[DATENFLUSS] CLIENT RECEIVED MESSAGE: {json.dumps(data)}")

        client_id = data.get("client_id")

        # Extrahiere die Spielerdaten direkt aus der Nachricht
        # Entferne die Schlüssel "type" und "client_id", um nur die Spielerdaten zu behalten
        player_data = {k: v for k, v in data.items() if k not in ["type", "client_id"]}

        self.logger.info(f"[DATENFLUSS] CLIENT EXTRACTED PLAYER DATA: {json.dumps(player_data)}")

        if client_id and player_data:
            # Ausführlichere Log-Ausgabe für Spieler-Updates
            self.logger.info(f"[DATENFLUSS] RECEIVED PLAYER UPDATE: Player {player_data.get('name', 'Unknown')} (ID: {client_id}): x={player_data.get('x', '?')}, y={player_data.get('y', '?')}, direction={player_data.get('direction', '?')}")

            # Prüfen, ob es sich um einen neuen Spieler handelt
            is_new_player = client_id not in self.players
            if is_new_player:
                self.logger.info(f"[DATENFLUSS] NEW PLAYER JOINED: {player_data.get('name', 'Unknown')} (ID: {client_id})")

            # Spielerdaten speichern
            self.logger.info(f"[DATENFLUSS] ADDING PLAYER TO PLAYERS LIST: client_id={client_id}, player_data={json.dumps(player_data)}")
            self.players[client_id] = player_data
            self.logger.info(f"[DATENFLUSS] PLAYER ADDED TO PLAYERS LIST: client_id={client_id}")
            self.logger.info(f"[DATENFLUSS] UPDATED PLAYER DATA: {json.dumps(player_data)}")

            # Log-Ausgabe für alle bekannten Spieler
            self.logger.info(f"[DATENFLUSS] CURRENT PLAYERS COUNT: {len(self.players)}")
            self.logger.info(f"[DATENFLUSS] PLAYERS LIST: {json.dumps([{'id': cid, 'name': pdata.get('name', 'Unknown'), 'x': pdata.get('x', '?'), 'y': pdata.get('y', '?')} for cid, pdata in self.players.items()])}")

            # Prüfen, ob der Spieler tatsächlich in der Liste ist
            if client_id in self.players:
                self.logger.info(f"[DATENFLUSS] PLAYER VERIFICATION: client_id={client_id} IS in players list")
            else:
                self.logger.warning(f"[DATENFLUSS] PLAYER VERIFICATION FAILED: client_id={client_id} is NOT in players list")

            # Prüfen, ob der Callback registriert ist
            if hasattr(self, 'on_player_update') and self.on_player_update:
                self.logger.info(f"[DATENFLUSS] CALLING ON_PLAYER_UPDATE CALLBACK: client_id={client_id}, player_data={json.dumps(player_data)}")
                self.on_player_update(client_id, player_data)
            else:
                self.logger.warning(f"[DATENFLUSS] ON_PLAYER_UPDATE CALLBACK NOT REGISTERED")
        else:
            self.logger.warning(f"[DATENFLUSS] INVALID PLAYER UPDATE: client_id={client_id}, player_data={json.dumps(player_data)}")

    async def _handle_player_disconnected(self, data: Dict[str, Any]):
        """Handle player disconnected message from the server

        Args:
            data: Player disconnected message data
        """
        client_id = data.get("client_id")
        player_name = data.get("player_name", "Unknown")

        if client_id in self.players:
            del self.players[client_id]
            self.logger.info(f"Player disconnected: {player_name}")

    async def _handle_chat_message(self, data: Dict[str, Any]):
        """Handle chat message from the server

        Args:
            data: Chat message data
        """
        client_id = data.get("client_id")
        player_name = data.get("player_name", "Unknown")
        message = data.get("message", "")

        self.logger.info(f"Chat message from {player_name}: {message}")

    async def _handle_connection_acknowledged(self, data: Dict[str, Any]):
        """Handle a connection acknowledgement from the server

        Args:
            data: Connection acknowledgement data
        """
        server_time = data.get("server_time")
        message = data.get("message", "")

        # Berechne die Latenz (RTT)
        current_time = time.time()
        latency = current_time - server_time if server_time else None

        self.logger.info(f"Connection acknowledged by server: {message}")
        if latency:
            self.logger.info(f"Estimated latency (RTT): {latency*1000:.2f} ms")

        # Ausgabe für automatisierte Tests
        print(f"[CONNECTION_STATUS] CONNECTION ACKNOWLEDGED BY SERVER")

    def send_message(self, message_type: str, message_data: Dict[str, Any]):
        """Send a message to the server

        Args:
            message_type: Type of the message
            message_data: Message data
        """
        if not self.connected or not self.websocket:
            self.logger.warning(f"Cannot send message: not connected to server")
            return

        # Erstelle die Nachricht mit einheitlicher Struktur
        # Für player_update verwenden wir eine spezielle Struktur
        if message_type == "player_update":
            message = {
                "type": message_type,
                **message_data  # Entpacke die Spielerdaten direkt in die Nachricht
            }
        else:
            # Für andere Nachrichtentypen behalten wir die bisherige Struktur bei
            message = {
                "type": message_type,
                "data": message_data
            }
        self.logger.info(f"[DATENFLUSS] CLIENT SENDING MESSAGE: {json.dumps(message)}")

        # Sende die Nachricht asynchron
        asyncio.run_coroutine_threadsafe(self._send_message_async(message), self.event_loop)

    async def _send_message_async(self, message: Dict[str, Any]):
        """Send a message to the server asynchronously

        Args:
            message: Message to send
        """
        if not self.connected or not self.websocket:
            self.logger.warning(f"Cannot send message: not connected to server")
            return

        try:
            # Konvertiere die Nachricht in JSON
            message_json = json.dumps(message)

            # Sende die Nachricht
            await self.websocket.send(message_json)
            self.logger.debug(f"Message sent: {message_json[:100]}..." if len(message_json) > 100 else f"Message sent: {message_json}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    def get_players(self):
        """Get all players in the session

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of player data by client ID
        """
        return self.players

    def get_events(self):
        """Get and clear all pending events

        Returns:
            List[Dict[str, Any]]: List of events
        """
        events = self.events.copy()
        self.events.clear()
        return events

    async def _handle_new_client_connected(self, data: Dict[str, Any]):
        """Handle new client connected message from the server

        Args:
            data: New client connected message data
        """
        client_id = data.get("client_id")
        self.logger.info(f"New client connected: {client_id}")

        # Signal to force an immediate player data update
        # This will be picked up by the game loop to send player data
        # even if the player hasn't moved
        self.logger.info(f"[DATENFLUSS] SIGNALING FORCE_PLAYER_DATA_UPDATE AFTER NEW CLIENT CONNECTED")
        # We'll use a custom event to signal this
        self.events.append({"type": "force_player_data_update"})
