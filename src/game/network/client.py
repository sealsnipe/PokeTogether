#!/usr/bin/env python
"""
Client-Modul - Implementiert die Client-Seite für Multiplayer
"""

import asyncio
import json
import logging
import threading
import time
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

        # Register default message handlers
        self.register_handler("welcome", self._handle_welcome)
        self.register_handler("player_update", self._handle_player_update)
        self.register_handler("player_disconnected", self._handle_player_disconnected)
        self.register_handler("chat_message", self._handle_chat_message)

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

    def connect(self, host: str, port: int = 8765):
        """Connect to a game server

        Args:
            host: Server host address
            port: Server port

        Returns:
            bool: True if connection was initiated successfully, False otherwise
        """
        self.logger.info(f"=== CLIENT.CONNECT CALLED: {host}:{port} ===")
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

        message = {
            "type": "player_update",
            "player_data": player_data
        }

        # Schedule the send coroutine in the client thread
        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_message(message), self.event_loop)

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
            asyncio.run_coroutine_threadsafe(self._send_message(data), self.event_loop)

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
        uri = f"ws://{host}:{port}"

        # Teste zuerst, ob der Server auf dem Port erreichbar ist
        self.logger.debug(f"Testing server connection to {host}:{port}...")
        connection_test_result = self._test_server_connection(host, port)
        self.logger.debug(f"Server connection test result: {connection_test_result}")

        try:
            self.running = True

            # Verbindungstimeout setzen
            try:
                self.logger.info(f"=== ATTEMPTING TO CONNECT TO {uri} WITH 5 SECOND TIMEOUT ===")
                # Versuche, eine Verbindung mit Timeout herzustellen
                websocket = await asyncio.wait_for(
                    websockets.connect(uri),
                    timeout=5.0  # 5 Sekunden Timeout
                )

                self.websocket = websocket
                self.connected = True
                self.logger.info(f"=== SUCCESSFULLY CONNECTED TO SERVER AT {uri} ===")

                # Listen for messages from the server
                while self.running:
                    try:
                        message = await websocket.recv()
                        self.logger.info(f"Received message: {message[:100]}..." if len(message) > 100 else f"Received message: {message}")
                        await self._process_message(message)
                    except websockets.exceptions.ConnectionClosed:
                        self.logger.info("Connection to server closed")
                        break
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")

            except asyncio.TimeoutError:
                self.logger.error(f"Connection timeout when connecting to {uri}")
                return
            except websockets.exceptions.InvalidStatusCode as e:
                self.logger.error(f"Invalid status code when connecting to {uri}: {e}")
                return
            except ConnectionRefusedError:
                self.logger.error(f"Connection refused when connecting to {uri}")
                return
            except Exception as e:
                self.logger.error(f"Unexpected error when connecting to {uri}: {e}")
                return
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
            await self.websocket.send(message)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    async def _process_message(self, message: str):
        """Process a message from the server

        Args:
            message: Message from the server
        """
        try:
            data = json.loads(message)
            message_type = data.get("type", "")

            # Call the appropriate handler for this message type
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](data)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")

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

    async def _handle_player_update(self, data: Dict[str, Any]):
        """Handle player update message from the server

        Args:
            data: Player update message data
        """
        client_id = data.get("client_id")
        player_data = data.get("player_data", {})

        if client_id:
            self.players[client_id] = player_data
            self.logger.debug(f"Updated player data for {player_data.get('name', 'Unknown')}")

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

    def send_message(self, message_type: str, message_data: Dict[str, Any]):
        """Send a message to the server

        Args:
            message_type: Type of the message
            message_data: Message data
        """
        if not self.connected or not self.websocket:
            self.logger.warning(f"Cannot send message: not connected to server")
            return

        # Erstelle die Nachricht
        message = {
            "type": message_type,
            "data": message_data
        }

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
