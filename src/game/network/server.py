#!/usr/bin/env python
"""
Server-Modul - Implementiert den Host-Modus für Multiplayer
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Set
import websockets
from websockets.server import WebSocketServerProtocol

class GameServer:
    """Game server for hosting multiplayer sessions"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        """Initialize the game server

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        self.logger = logging.getLogger(__name__)
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.players: Dict[str, Dict[str, Any]] = {}
        self.server = None
        self.running = False

    async def start(self):
        """Start the game server"""
        self.logger.info(f"Starting game server on {self.host}:{self.port}")
        self.running = True

        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            self.logger.info("Game server started successfully")

            # Lokale IP-Adressen ausgeben
            self._print_local_ip_addresses()

            return True
        except Exception as e:
            self.logger.error(f"Failed to start game server: {e}")
            self.running = False
            return False

    def _print_local_ip_addresses(self):
        """Gibt alle lokalen IP-Adressen aus"""
        try:
            import socket
            hostname = socket.gethostname()
            self.logger.info(f"Hostname: {hostname}")

            # Alle IP-Adressen des Hosts ausgeben
            ip_addresses = socket.getaddrinfo(hostname, None)
            self.logger.info("Available IP addresses:")
            for ip in ip_addresses:
                if ip[0] == socket.AF_INET:  # Nur IPv4-Adressen
                    self.logger.info(f"  - {ip[4][0]}")
        except Exception as e:
            self.logger.error(f"Error getting IP addresses: {e}")

    async def stop(self):
        """Stop the game server"""
        if self.server:
            self.logger.info("Stopping game server")
            self.running = False
            self.server.close()
            await self.server.wait_closed()
            self.logger.info("Game server stopped")

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a client connection

        Args:
            websocket: WebSocket connection
            path: Connection path
        """
        # Generate a unique client ID
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket

        self.logger.info(f"New client connected: {client_id}")

        try:
            # Send welcome message with client ID
            await websocket.send(json.dumps({
                "type": "welcome",
                "client_id": client_id,
                "players": self.players
            }))

            # Handle messages from this client
            async for message in websocket:
                await self.process_message(client_id, message)

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Remove client and player data when they disconnect
            if client_id in self.clients:
                del self.clients[client_id]

            if client_id in self.players:
                player_data = self.players[client_id]
                del self.players[client_id]

                # Notify other clients about the disconnection
                await self.broadcast({
                    "type": "player_disconnected",
                    "client_id": client_id,
                    "player_name": player_data.get("name", "Unknown")
                }, exclude={client_id})

    async def process_message(self, client_id: str, message: str):
        """Process a message from a client

        Args:
            client_id: Client ID
            message: Message from the client
        """
        try:
            data = json.loads(message)
            message_type = data.get("type", "")

            if message_type == "player_update":
                # Update player data
                player_data = data.get("player_data", {})

                # Store or update player data
                if client_id not in self.players:
                    self.logger.info(f"New player joined: {player_data.get('name', 'Unknown')}")

                self.players[client_id] = player_data

                # Broadcast player update to all other clients
                await self.broadcast({
                    "type": "player_update",
                    "client_id": client_id,
                    "player_data": player_data
                }, exclude={client_id})

            elif message_type == "chat_message":
                # Handle chat messages
                chat_data = {
                    "type": "chat_message",
                    "client_id": client_id,
                    "player_name": self.players.get(client_id, {}).get("name", "Unknown"),
                    "message": data.get("message", "")
                }

                # Broadcast chat message to all clients
                await self.broadcast(chat_data)

            else:
                self.logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON from client {client_id}")
        except Exception as e:
            self.logger.error(f"Error processing message from client {client_id}: {e}")

    async def broadcast(self, data: Dict[str, Any], exclude: Optional[Set[str]] = None):
        """Broadcast data to all connected clients

        Args:
            data: Data to broadcast
            exclude: Set of client IDs to exclude from broadcast
        """
        if exclude is None:
            exclude = set()

        message = json.dumps(data)

        for client_id, websocket in self.clients.items():
            if client_id not in exclude:
                try:
                    await websocket.send(message)
                except Exception as e:
                    self.logger.error(f"Error broadcasting to client {client_id}: {e}")
