#!/usr/bin/env python
"""
Player Manager - Zentrale Verwaltung aller Spieler im Multiplayer-Modus
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List

class PlayerManager:
    """Zentrale Verwaltung aller Spieler im Multiplayer-Modus"""

    def __init__(self):
        """Initialisiere den Player Manager"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("[PLAYER_MANAGER] Initializing Player Manager")
        
        # Dictionary mit allen Spielern (client_id -> player_data)
        self.players: Dict[str, Dict[str, Any]] = {}
        
        # Spawn-Positionen für neue Spieler
        self.spawn_positions = [
            {"x": 460, "y": 448},  # Spieler 1 (Rot)
            {"x": 560, "y": 448},  # Spieler 2 (Blau)
            {"x": 460, "y": 548},  # Spieler 3 (Grün)
            {"x": 560, "y": 548}   # Spieler 4 (Gelb)
        ]
        
        # Farben für die Spieler
        self.player_colors = ["Red", "Blue", "Green", "Yellow"]

    def add_player(self, client_id: str) -> Dict[str, Any]:
        """Fügt einen neuen Spieler hinzu
        
        Args:
            client_id: Client-ID des Spielers
            
        Returns:
            Dict[str, Any]: Spielerdaten des neuen Spielers
        """
        # Bestimme die Spawn-Position basierend auf der Anzahl der verbundenen Spieler
        spawn_index = len(self.players) % len(self.spawn_positions)
        spawn_position = self.spawn_positions[spawn_index]
        character_type = self.player_colors[spawn_index]
        
        # Erstelle die Spielerdaten
        player_data = {
            "x": spawn_position["x"],
            "y": spawn_position["y"],
            "spawn_index": spawn_index,
            "character_type": character_type,
            "name": f"Player {spawn_index + 1}",
            "direction": "down",
            "moving": False,
            "current_frame": 0,
            "emote": None,
            "emote_timer": 0,
            "assigned_time": time.time(),
            "last_update": time.time(),
            "player_id": client_id
        }
        
        # Füge den Spieler zum Dictionary hinzu
        self.players[client_id] = player_data
        
        self.logger.info(f"[PLAYER_MANAGER] ADDED PLAYER: client_id={client_id}, position=({spawn_position['x']}, {spawn_position['y']}), spawn_index={spawn_index}, character_type={character_type}")
        
        return player_data
    
    def remove_player(self, client_id: str) -> None:
        """Entfernt einen Spieler
        
        Args:
            client_id: Client-ID des Spielers
        """
        if client_id in self.players:
            self.logger.info(f"[PLAYER_MANAGER] REMOVING PLAYER: client_id={client_id}")
            del self.players[client_id]
        else:
            self.logger.warning(f"[PLAYER_MANAGER] PLAYER NOT FOUND: client_id={client_id}")
    
    def update_player(self, client_id: str, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aktualisiert die Daten eines Spielers
        
        Args:
            client_id: Client-ID des Spielers
            player_data: Neue Spielerdaten
            
        Returns:
            Dict[str, Any]: Aktualisierte Spielerdaten
        """
        if client_id not in self.players:
            self.logger.warning(f"[PLAYER_MANAGER] PLAYER NOT FOUND, ADDING NEW PLAYER: client_id={client_id}")
            return self.add_player(client_id)
        
        # Extrahiere die Positionsdaten
        try:
            x = float(player_data.get("x", self.players[client_id]["x"]))
            y = float(player_data.get("y", self.players[client_id]["y"]))
        except (ValueError, TypeError):
            self.logger.error(f"[PLAYER_MANAGER] INVALID COORDINATES: client_id={client_id}, x={player_data.get('x')}, y={player_data.get('y')}")
            x = self.players[client_id]["x"]
            y = self.players[client_id]["y"]
        
        # Extrahiere alle anderen Metadaten
        existing_data = self.players[client_id]
        direction = player_data.get("direction", existing_data.get("direction", "down"))
        moving = player_data.get("moving", existing_data.get("moving", False))
        current_frame = player_data.get("current_frame", existing_data.get("current_frame", 0))
        emote = player_data.get("emote", existing_data.get("emote", None))
        emote_timer = player_data.get("emote_timer", existing_data.get("emote_timer", 0))
        
        # Aktualisiere die Spielerdaten
        self.players[client_id].update({
            "x": x,
            "y": y,
            "direction": direction,
            "moving": moving,
            "current_frame": current_frame,
            "emote": emote,
            "emote_timer": emote_timer,
            "last_update": time.time()
        })
        
        self.logger.info(f"[PLAYER_MANAGER] UPDATED PLAYER: client_id={client_id}, position=({x}, {y}), direction={direction}, moving={moving}")
        
        return self.players[client_id]
    
    def get_player(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Gibt die Daten eines Spielers zurück
        
        Args:
            client_id: Client-ID des Spielers
            
        Returns:
            Optional[Dict[str, Any]]: Spielerdaten oder None, wenn der Spieler nicht gefunden wurde
        """
        if client_id in self.players:
            return self.players[client_id]
        else:
            self.logger.warning(f"[PLAYER_MANAGER] PLAYER NOT FOUND: client_id={client_id}")
            return None
    
    def get_all_players(self) -> Dict[str, Dict[str, Any]]:
        """Gibt die Daten aller Spieler zurück
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mit allen Spielerdaten
        """
        return self.players
    
    def get_player_count(self) -> int:
        """Gibt die Anzahl der Spieler zurück
        
        Returns:
            int: Anzahl der Spieler
        """
        return len(self.players)
    
    def get_player_positions(self) -> Dict[str, Dict[str, Any]]:
        """Gibt die Positionen aller Spieler zurück
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mit allen Spielerpositionen
        """
        positions = {}
        for client_id, player_data in self.players.items():
            positions[client_id] = {
                "x": player_data["x"],
                "y": player_data["y"],
                "spawn_index": player_data.get("spawn_index", -1),
                "character_type": player_data.get("character_type", "Red"),
                "name": player_data.get("name", f"Player"),
                "direction": player_data.get("direction", "down"),
                "moving": player_data.get("moving", False),
                "current_frame": player_data.get("current_frame", 0),
                "emote": player_data.get("emote", None),
                "emote_timer": player_data.get("emote_timer", 0),
                "last_update": player_data.get("last_update", time.time()),
                "player_id": player_data.get("player_id", client_id)
            }
        
        return positions
    
    def to_json(self) -> str:
        """Konvertiert alle Spielerdaten in einen JSON-String
        
        Returns:
            str: JSON-String mit allen Spielerdaten
        """
        return json.dumps(self.players)
