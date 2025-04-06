#!/usr/bin/env python
"""
Server-Modul - Implementiert den Host-Modus für Multiplayer
"""

# Wenn diese Datei direkt ausgeführt wird, startet der Server

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Set
import websockets
from websockets.server import WebSocketServerProtocol
from game.network.player_manager import PlayerManager

class GameServer:
    """Game server for hosting multiplayer sessions"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        """Initialize the game server

        Args:
            host: Host address to bind to
            port: Port to listen on
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"=== INITIALIZING GAME SERVER ON {host}:{port} ===")
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}

        # Initialisiere den PlayerManager für die zentrale Spielerverwaltung
        self.player_manager = PlayerManager()
        self.logger.info("=== INITIALIZED PLAYER MANAGER ===")

        # Behalte diese Variablen für Abwärtskompatibilität bei
        self.players: Dict[str, Dict[str, Any]] = {}
        self.player_positions: Dict[str, Dict[str, Any]] = {}  # Zentrale Positionsverwaltung

        self.server = None
        self.running = False

        # Feste Startpositionen für Spieler (wird jetzt vom PlayerManager verwaltet)
        self.spawn_positions = [
            {"x": 460.0, "y": 448.0},  # Spieler 1
            {"x": 560.0, "y": 448.0},  # Spieler 2
            # Weitere Positionen können hier hinzugefügt werden
        ]

        self.logger.debug("Game server initialized with:")
        self.logger.debug(f"- host: {self.host}")
        self.logger.debug(f"- port: {self.port}")
        self.logger.debug(f"- running: {self.running}")
        self.logger.debug(f"- spawn_positions: {self.spawn_positions}")

    async def start(self):
        """Start the game server"""
        self.logger.info(f"=== STARTING GAME SERVER ON {self.host}:{self.port} ===")
        self.running = True

        try:
            self.logger.debug(f"Creating WebSocket server on {self.host}:{self.port}...")
            # Starte den WebSocket-Server ohne Pfad-Parameter
            self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
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

    async def handle_client(self, websocket: WebSocketServerProtocol, path=None):
        """Handle a client connection

        Args:
            websocket: WebSocket connection
            path: Connection path (optional, not used)
        """
        # Generate a unique client ID
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket

        self.logger.info(f"=== NEW CLIENT CONNECTED: {client_id} ===")
        self.logger.debug(f"Total clients connected: {len(self.clients)}")
        self.logger.info(f"[DATENFLUSS] CLIENT CONNECTED: ID={client_id}, Path={path}")
        # Add a clear marker for automated testing
        print(f"NEW CLIENT CONNECTED: {client_id}")
        print(f"[CONNECTION_STATUS] CLIENT {client_id} CONNECTED TO SERVER")
        print(f"BROADCASTING TO {len(self.clients)} CLIENTS")

        # Weise dem Spieler eine Position zu
        await self._assign_player_position(client_id)

        try:
            # Send welcome message with client ID
            await websocket.send(json.dumps({
                "type": "welcome",
                "client_id": client_id,
                "players": self.players,
                "position": self.player_positions.get(client_id, {})
            }))

            # Notify all other clients about the new client
            await self.broadcast({
                "type": "new_client_connected",
                "client_id": client_id
            }, exclude=client_id)

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

            # Hole die Spielerdaten vom PlayerManager
            player_data = self.player_manager.get_player(client_id)

            # Entferne den Spieler aus dem PlayerManager
            if player_data:
                self.player_manager.remove_player(client_id)

                # Für Abwärtskompatibilität: Entferne den Spieler auch aus den alten Datenstrukturen
                if client_id in self.players:
                    del self.players[client_id]
                if client_id in self.player_positions:
                    del self.player_positions[client_id]

                # Notify other clients about the disconnection
                await self.broadcast({
                    "type": "player_disconnected",
                    "client_id": client_id,
                    "player_name": player_data.get("name", "Unknown")
                }, exclude={client_id})

    async def _assign_player_position(self, client_id: str):
        """Weist einem Spieler eine Position zu

        Args:
            client_id: Client-ID des Spielers
        """
        # Verwende den PlayerManager, um dem Spieler eine Position zuzuweisen
        player_data = self.player_manager.add_player(client_id)

        # Für Abwärtskompatibilität: Aktualisiere auch die alten Datenstrukturen
        self.player_positions[client_id] = player_data

        self.logger.info(f"[SPIELERSYNC] ASSIGNED POSITION TO PLAYER: client_id={client_id}, position=({player_data['x']}, {player_data['y']}), spawn_index={player_data['spawn_index']}, character_type={player_data['character_type']}")

        # Sende die aktualisierten Positionen an alle Clients
        await self._broadcast_positions()

    async def _broadcast_positions(self):
        """Sendet die aktuellen Positionen aller Spieler an alle Clients"""
        # Hole die aktuellen Spielerpositionen vom PlayerManager
        positions = self.player_manager.get_player_positions()

        # Für Abwärtskompatibilität: Aktualisiere auch die alte Datenstruktur
        self.player_positions = positions

        # Füge einen Zeitstempel hinzu, um die Aktualität der Daten zu kennzeichnen
        message = {
            "type": "positions_update",
            "positions": positions,
            "server_timestamp": time.time()
        }

        # Ausführliche Debug-Ausgabe für die Spielersynchronisierung
        self.logger.info(f"[SPIELERSYNC] BROADCASTING POSITIONS: player_count={len(positions)}")
        self.logger.debug(f"[SPIELERSYNC] POSITIONS DATA: {json.dumps(positions)}")

        # Sende die Nachricht an alle Clients
        await self.broadcast(message)

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
                # Vollständige Nachricht loggen
                self.logger.info(f"[DATENFLUSS] SERVER RECEIVED MESSAGE: {json.dumps(data)}")

                # Extrahiere die Spielerdaten direkt aus der Nachricht
                # Entferne den "type"-Schlüssel, um nur die Spielerdaten zu behalten
                player_data = {k: v for k, v in data.items() if k != "type"}

                # Log the received data
                self.logger.info(f"[DATENFLUSS] SERVER PROCESSED PLAYER DATA: {json.dumps(player_data)}")

                # Prüfen, ob die Spielerdaten leer sind oder nur den Typ enthalten
                if not player_data or len(player_data) <= 1:
                    self.logger.warning(f"[DATENFLUSS] EMPTY PLAYER DATA RECEIVED FROM CLIENT: {client_id}")
                    return

                # Store or update player data
                if client_id not in self.players:
                    self.logger.info(f"New player joined: {player_data.get('name', 'Unknown')}")

                self.players[client_id] = player_data

                # Broadcast player update to all other clients
                # Füge client_id zu den Spielerdaten hinzu und setze den Typ
                # Füge Server-Zeitstempel hinzu
                player_data["server_timestamp"] = time.time()

                # Debug-Ausgabe für die Spielersynchronisierung
                self.logger.info(f"[SPIELERSYNC] SERVER PROCESSING PLAYER UPDATE: client_id={client_id}, player_id={player_data.get('player_id')}, x={player_data.get('x')}, y={player_data.get('y')}")

                # Verwende den PlayerManager, um die Spielerdaten zu aktualisieren
                updated_data = self.player_manager.update_player(client_id, player_data)

                # Für Abwärtskompatibilität: Aktualisiere auch die alte Datenstruktur
                self.player_positions[client_id] = updated_data

                self.logger.info(f"[SPIELERSYNC] UPDATED PLAYER POSITION WITH METADATA: client_id={client_id}, position=({updated_data['x']}, {updated_data['y']}), direction={updated_data['direction']}, moving={updated_data['moving']}, character_type={updated_data['character_type']}")

                # Sende die aktualisierten Positionen an alle Clients
                await self._broadcast_positions()

                broadcast_data = {
                    "type": "player_update",
                    "client_id": client_id,
                    **player_data  # Entpacke die Spielerdaten direkt in die Nachricht
                }
                self.logger.info(f"[DATENFLUSS] SERVER BROADCASTING TO CLIENTS: {json.dumps(broadcast_data)}")
                self.logger.info(f"[SPIELERSYNC] SERVER BROADCASTING PLAYER UPDATE: client_id={client_id}, player_id={player_data.get('player_id')}, x={player_data.get('x')}, y={player_data.get('y')}")
                await self.broadcast(broadcast_data, exclude={client_id})

            elif message_type == "connection_confirmation":
                # Handle connection confirmation
                client_info = data.get("client_info", {})
                self.logger.info(f"Received connection confirmation from client {client_id}")
                self.logger.info(f"Client info: {client_info}")

                # Acknowledge the confirmation
                try:
                    await self.clients[client_id].send(json.dumps({
                        "type": "connection_acknowledged",
                        "server_time": time.time(),
                        "message": "Connection confirmed and acknowledged"
                    }))
                    self.logger.info(f"Sent connection acknowledgement to client {client_id}")
                except Exception as e:
                    self.logger.error(f"Error sending connection acknowledgement to client {client_id}: {e}")

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

    async def broadcast(self, data: Dict[str, Any], exclude: Optional[str] = None):
        """Broadcast data to all connected clients

        Args:
            data: Data to broadcast
            exclude: Client ID to exclude from broadcast, or None to broadcast to all clients
        """
        exclude_set = set()
        if exclude is not None:
            if isinstance(exclude, str):
                exclude_set.add(exclude)
            elif isinstance(exclude, (list, set)):
                exclude_set.update(exclude)

        message = json.dumps(data)
        self.logger.info(f"[DATENFLUSS] BROADCASTING MESSAGE TO CLIENTS: {message[:100]}..." if len(message) > 100 else f"[DATENFLUSS] BROADCASTING MESSAGE TO CLIENTS: {message}")
        self.logger.info(f"[DATENFLUSS] BROADCASTING TO {len(self.clients) - len(exclude_set)} CLIENTS (EXCLUDING {len(exclude_set)} CLIENTS)")

        broadcast_count = 0
        for client_id, websocket in self.clients.items():
            if client_id not in exclude_set:
                try:
                    self.logger.info(f"[DATENFLUSS] SENDING BROADCAST TO CLIENT: {client_id}")
                    await websocket.send(message)
                    self.logger.info(f"[DATENFLUSS] BROADCAST SENT TO CLIENT: {client_id}")
                    broadcast_count += 1
                except Exception as e:
                    self.logger.error(f"[DATENFLUSS] ERROR BROADCASTING TO CLIENT {client_id}: {e}")
                    import traceback
                    self.logger.error(f"[DATENFLUSS] TRACEBACK: {traceback.format_exc()}")

        self.logger.info(f"[DATENFLUSS] BROADCAST COMPLETED: {broadcast_count} CLIENTS RECEIVED THE MESSAGE")


if __name__ == "__main__":
    # Konfiguriere Logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Erstelle und starte den Server
    server = GameServer()

    try:
        # Starte den Server und halte ihn am Laufen
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.start())

        # Warte auf Benutzerabbruch
        print("Server running. Press Ctrl+C to stop.")
        loop.run_forever()
    except KeyboardInterrupt:
        print("Server stopping...")
        loop.run_until_complete(server.stop())
        loop.close()
    except Exception as e:
        print(f"Error: {e}")
