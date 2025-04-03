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
        self.server = GameServer()
        self.client = GameClient()
        self.is_host = False
        self.server_thread = None
        self.server_loop = None
        self.local_player_data = {}
        self.on_player_update = None
        self.on_player_disconnected = None
        self.on_chat_message = None

        # Register custom message handlers
        self.client.register_handler("player_update", self._handle_player_update)
        self.client.register_handler("player_disconnected", self._handle_player_disconnected)
        self.client.register_handler("chat_message", self._handle_chat_message)

    def start_hosting(self, port: int = 8765):
        """Start hosting a multiplayer session

        Args:
            port: Port to listen on

        Returns:
            bool: True if hosting was started successfully, False otherwise
        """
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

            # Start the server in a separate thread
            self.server_thread = threading.Thread(
                target=self._run_server_loop,
                args=(self.server_loop, port),
                daemon=True
            )
            self.server_thread.start()

            # Kurze Pause, um dem Server Zeit zum Starten zu geben
            time.sleep(0.5)

            # Connect to our own server
            success = self.connect_to_session("localhost", port)
            if success:
                self.is_host = True
                self.logger.info("Successfully started hosting multiplayer session")
                return True
            else:
                self.logger.error("Failed to connect to own server")
                return False
        except Exception as e:
            self.logger.error(f"Error starting to host multiplayer session: {e}")
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

    def connect_to_session(self, host: str, port: int = 8765):
        """Connect to a multiplayer session

        Args:
            host: Host address
            port: Host port

        Returns:
            bool: True if connection was initiated successfully, False otherwise
        """
        if self.client.connected:
            self.logger.warning("Already connected to a session")
            return False

        self.logger.info(f"Connecting to multiplayer session at {host}:{port}")
        try:
            self.client.connect(host, port)
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to session: {e}")
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
        asyncio.set_event_loop(loop)

        try:
            # Start the server
            loop.run_until_complete(self.server.start())

            # Keep the loop running
            loop.run_forever()
        except Exception as e:
            self.logger.error(f"Error in server loop: {e}")
        finally:
            loop.close()

    async def _handle_player_update(self, data: Dict[str, Any]):
        """Handle player update message

        Args:
            data: Player update message data
        """
        client_id = data.get("client_id")
        player_data = data.get("player_data", {})

        # Call the callback if registered
        if self.on_player_update:
            self.on_player_update(client_id, player_data)

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

        # Call the callback if registered
        if self.on_chat_message:
            self.on_chat_message(player_name, message)
