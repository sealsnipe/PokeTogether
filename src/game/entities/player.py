#!/usr/bin/env python
"""
Player class - Represents the player character
"""

import pygame
import logging
import uuid
import time
from typing import Tuple, Dict, Any, List, Optional

class Player:
    """Player class representing the main character"""

    def __init__(self, x: int = 0, y: int = 0, character_type: str = "Red", name: str = None):
        """Initialize the player

        Args:
            x: Initial x position
            y: Initial y position
            character_type: Type of character (Red, Blue, etc.)
            name: Player name (defaults to character_type if None)
        """
        self.logger = logging.getLogger(__name__)

        # Wenn kein Name angegeben wurde, verwende den Charaktertyp als Namen
        if name is None:
            name = character_type

        self.logger.info(f"Creating player '{name}' of type '{character_type}' at position ({x}, {y})")

        # Netzwerk-relevante Attribute
        self.player_id = str(uuid.uuid4())  # Eindeutige ID für Netzwerkkommunikation
        self.name = name
        self.character_type = character_type
        self.x = x
        self.y = y
        self.direction = "down"  # down, up, left, right

        # Spielmechanik-Attribute
        self.speed = 3
        self.sprite_sheet = None
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        self.moving = False
        self.pokemon_team = []
        self.items = {}

        # Netzwerk-Synchronisierung
        self.last_sent_position = (x, y)
        self.last_sent_direction = self.direction

        # Client-Side Prediction und Server-Reconciliation
        self.input_sequence_number = 0
        self.pending_inputs = []  # Liste der ausstehenden Eingaben
        self.server_position = (x, y)  # Letzte vom Server bestätigte Position
        self.server_direction = self.direction  # Letzte vom Server bestätigte Richtung
        self.last_update_time = time.time()  # Zeitpunkt der letzten Aktualisierung

        # Bewegungsprognose
        self.velocity_x = 0.0  # Geschwindigkeit in X-Richtung
        self.velocity_y = 0.0  # Geschwindigkeit in Y-Richtung
        self.last_position = (x, y)  # Letzte bekannte Position
        self.last_position_time = time.time()  # Zeitpunkt der letzten Positionsaktualisierung

    def load_sprites(self, sprite_sheet_path: str):
        """Load player sprites

        Args:
            sprite_sheet_path: Path to the sprite sheet image
        """
        self.logger.info(f"Loading player sprites from {sprite_sheet_path}")
        try:
            self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            self.logger.info("Player sprites loaded successfully")
        except pygame.error as e:
            self.logger.error(f"Error loading player sprites: {e}")
            # Fallback to a simple rectangle
            self.sprite_sheet = None

    def move(self, dx: int, dy: int, speed_multiplier: float = 1.0, prediction: bool = True) -> Dict[str, Any]:
        """Move the player

        Args:
            dx: Change in x position
            dy: Change in y position
            speed_multiplier: Multiplier for the player's speed (default: 1.0)
            prediction: Whether to use client-side prediction (default: True)

        Returns:
            Dict[str, Any]: Input data for client-side prediction
        """
        # Debug-Logging für Bewegungseingaben
        if dx != 0 or dy != 0:
            self.logger.debug(f"Bewegungseingabe: dx={dx}, dy={dy}, speed_multiplier={speed_multiplier}")

        # Richtung basierend auf Bewegung setzen
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        elif dy > 0:
            self.direction = "down"
        elif dy < 0:
            self.direction = "up"

        # Position aktualisieren
        old_x, old_y = self.x, self.y
        self.x += dx * self.speed * speed_multiplier
        self.y += dy * self.speed * speed_multiplier

        # Bewegungsstatus aktualisieren
        self.moving = dx != 0 or dy != 0

        # Debug-Logging für tatsächliche Bewegung
        if old_x != self.x or old_y != self.y:
            self.logger.debug(f"Bewegung: ({old_x}, {old_y}) -> ({self.x}, {self.y})")

        # Erstelle Eingabedaten für Client-Side Prediction
        input_data = {
            "sequence_number": self.input_sequence_number,
            "dx": dx,
            "dy": dy,
            "speed_multiplier": speed_multiplier,
            "timestamp": time.time()
        }

        # Erhöhe die Sequenznummer
        self.input_sequence_number += 1

        # Füge die Eingabe zur Liste der ausstehenden Eingaben hinzu, wenn Prediction aktiviert ist
        if prediction:
            self.pending_inputs.append(input_data)

        return input_data

    def update(self, dt: float):
        """Update the player

        Args:
            dt: Time delta since last update
        """
        # Update animation
        if self.moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = self.animation_timer - self.animation_speed
                self.current_frame = (self.current_frame + 1) % 4

        # Aktualisiere den Zeitpunkt der letzten Aktualisierung
        self.last_update_time = time.time()

    def interpolate(self, other_player_data: Dict[str, Any], alpha: float = 0.3) -> None:
        """Interpolate player position and direction with movement prediction

        Args:
            other_player_data: Other player data
            alpha: Interpolation factor (0.0 - 1.0, default: 0.3)
        """
        # Extrahiere die Daten des anderen Spielers
        other_x = other_player_data.get("x", self.x)
        other_y = other_player_data.get("y", self.y)
        other_direction = other_player_data.get("direction", self.direction)
        # Verwende Server-Zeitstempel, wenn verfügbar, sonst Client-Zeitstempel, sonst aktuelle Zeit
        other_timestamp = other_player_data.get("server_timestamp",
                                             other_player_data.get("timestamp", time.time()))
        other_moving = other_player_data.get("moving", False)

        self.logger.debug(f"Using timestamp: server_timestamp={other_player_data.get('server_timestamp')}, timestamp={other_player_data.get('timestamp')}, final={other_timestamp}")

        # Berechne die Zeit seit dem letzten Update
        current_time = time.time()
        time_since_update = current_time - other_timestamp

        # Berechne die Geschwindigkeit basierend auf der Positionsänderung
        time_since_last_position = current_time - self.last_position_time
        if time_since_last_position > 0.001:  # Vermeide Division durch Null
            # Berechne die Geschwindigkeit in Einheiten pro Sekunde
            self.velocity_x = (other_x - self.last_position[0]) / time_since_last_position
            self.velocity_y = (other_y - self.last_position[1]) / time_since_last_position

            # Speichere die aktuelle Position und Zeit
            self.last_position = (other_x, other_y)
            self.last_position_time = other_timestamp

            self.logger.debug(f"Velocity: vx={self.velocity_x:.2f}, vy={self.velocity_y:.2f}")

        # Bewegungsprognose: Berechne die vorhergesagte Position basierend auf der Geschwindigkeit
        predicted_x = other_x + self.velocity_x * time_since_update
        predicted_y = other_y + self.velocity_y * time_since_update

        # Begrenze die Vorhersage, um zu starke Abweichungen zu vermeiden
        max_prediction_distance = 50.0  # Maximale Vorhersagedistanz
        prediction_distance = ((predicted_x - other_x) ** 2 + (predicted_y - other_y) ** 2) ** 0.5

        if prediction_distance > max_prediction_distance:
            # Skaliere die Vorhersage auf die maximale Distanz
            scale_factor = max_prediction_distance / prediction_distance
            predicted_x = other_x + (predicted_x - other_x) * scale_factor
            predicted_y = other_y + (predicted_y - other_y) * scale_factor

        # Berechne einen zeitbasierten Interpolationsfaktor
        # Je länger das Update her ist, desto stärker interpolieren wir
        time_factor = min(1.0, time_since_update * 5.0)  # Max 1.0 nach 0.2 Sekunden

        # Kombiniere den festen Alpha-Wert mit dem zeitbasierten Faktor
        effective_alpha = alpha * (1.0 + time_factor)

        # Begrenze den effektiven Alpha-Wert
        effective_alpha = min(0.8, effective_alpha)  # Max 0.8 für Stabilität

        # Wenn der andere Spieler sich bewegt, erhöhen wir den Interpolationsfaktor
        if other_moving:
            effective_alpha = min(0.9, effective_alpha * 1.5)  # Schnellere Interpolation bei Bewegung

        # Interpoliere die Position mit Easing-Funktion (quadratische Interpolation)
        # Dies erzeugt natürlichere Bewegungen als lineare Interpolation
        t = 1.0 - (1.0 - effective_alpha) * (1.0 - effective_alpha)  # Quadratisches Easing

        # Interpoliere zwischen der aktuellen Position und der vorhergesagten Position
        target_x = predicted_x if other_moving else other_x
        target_y = predicted_y if other_moving else other_y

        # Interpoliere die Position
        self.x = self.x + (target_x - self.x) * t
        self.y = self.y + (target_y - self.y) * t

        # Richtung übernehmen (keine Interpolation für Richtung)
        self.direction = other_direction

        # Bewegungsstatus aktualisieren
        self.moving = (abs(target_x - self.x) > 0.1 or abs(target_y - self.y) > 0.1)

        # Debug-Logging
        self.logger.debug(f"Interpolation: time_factor={time_factor:.2f}, effective_alpha={effective_alpha:.2f}, t={t:.2f}, moving={self.moving}")
        if other_moving:
            self.logger.debug(f"Prediction: other=({other_x:.1f}, {other_y:.1f}), predicted=({predicted_x:.1f}, {predicted_y:.1f}), final=({self.x:.1f}, {self.y:.1f})")

    def render(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render the player

        Args:
            screen: Pygame surface to render on
            camera_offset: Camera offset (x, y)
        """
        x = self.x - camera_offset[0]
        y = self.y - camera_offset[1]

        if self.sprite_sheet:
            # Calculate the position in the sprite sheet based on direction and frame
            direction_idx = {"down": 0, "left": 1, "right": 2, "up": 3}
            sprite_x = self.current_frame * 32
            sprite_y = direction_idx[self.direction] * 32

            # Draw the sprite
            screen.blit(self.sprite_sheet, (x, y), (sprite_x, sprite_y, 32, 32))
        else:
            # Fallback: draw a simple rectangle
            pygame.draw.rect(screen, (255, 0, 0), (x, y, 32, 32))

    def add_pokemon(self, pokemon):
        """Add a Pokemon to the player's team

        Args:
            pokemon: Pokemon object to add

        Returns:
            bool: True if the Pokemon was added, False if the team is full
        """
        if len(self.pokemon_team) < 6:
            self.pokemon_team.append(pokemon)
            self.logger.info(f"Added {pokemon.name} to {self.name}'s team")
            return True
        else:
            self.logger.info(f"Could not add {pokemon.name} to {self.name}'s team - team is full")
            return False

    def add_item(self, item_name: str, quantity: int = 1):
        """Add an item to the player's inventory

        Args:
            item_name: Name of the item
            quantity: Quantity to add
        """
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity

        self.logger.info(f"Added {quantity} {item_name} to {self.name}'s inventory")

    def use_item(self, item_name: str) -> bool:
        """Use an item from the player's inventory

        Args:
            item_name: Name of the item to use

        Returns:
            bool: True if the item was used, False if the player doesn't have the item
        """
        if item_name in self.items and self.items[item_name] > 0:
            self.items[item_name] -= 1
            if self.items[item_name] == 0:
                del self.items[item_name]

            self.logger.info(f"{self.name} used {item_name}")
            return True
        else:
            self.logger.info(f"{self.name} tried to use {item_name} but doesn't have any")
            return False

    def to_network_data(self) -> Dict[str, Any]:
        """Serialize player data for network transmission

        Returns:
            Dict[str, Any]: Serialized player data
        """
        # Erstelle ein Logging-Eintrag für die Netzwerkdaten
        self.logger.info(f"[SPIELERSYNC] SERIALIZING PLAYER DATA: player_id={self.player_id}, x={self.x}, y={self.y}, direction={self.direction}")

        return {
            "player_id": self.player_id,
            "name": self.name,
            "character_type": self.character_type,
            "x": self.x,
            "y": self.y,
            "direction": self.direction,
            "moving": self.moving,
            "current_frame": self.current_frame,
            "input_sequence_number": self.input_sequence_number,
            "timestamp": time.time()
        }

    def has_significant_changes(self) -> bool:
        """Check if the player has significant changes that should be sent over the network

        Returns:
            bool: True if there are significant changes, False otherwise
        """
        # Prüfe, ob sich die Position oder Richtung geändert hat
        position_changed = (self.x, self.y) != self.last_sent_position
        direction_changed = self.direction != self.last_sent_direction

        return position_changed or direction_changed

    def update_last_sent_data(self) -> None:
        """Update the last sent data after sending player data over the network"""
        self.last_sent_position = (self.x, self.y)
        self.last_sent_direction = self.direction

    def apply_server_update(self, server_data: Dict[str, Any], reconciliation: bool = True) -> None:
        """Apply server update to the player

        Args:
            server_data: Server data
            reconciliation: Whether to use server reconciliation (default: True)
        """
        # Extrahiere die Daten vom Server
        server_x = server_data.get("x", self.x)
        server_y = server_data.get("y", self.y)
        server_direction = server_data.get("direction", self.direction)
        server_sequence_number = server_data.get("input_sequence_number", 0)

        # Speichere die Server-Position
        self.server_position = (server_x, server_y)
        self.server_direction = server_direction

        # Wenn Reconciliation deaktiviert ist, übernehme einfach die Server-Position
        if not reconciliation:
            self.x = server_x
            self.y = server_y
            self.direction = server_direction
            return

        # Entferne alle bestätigten Eingaben aus der Liste der ausstehenden Eingaben
        self.pending_inputs = [input_data for input_data in self.pending_inputs
                              if input_data["sequence_number"] > server_sequence_number]

        # Wende die Server-Position an
        self.x = server_x
        self.y = server_y
        self.direction = server_direction

        # Wende alle ausstehenden Eingaben erneut an
        for input_data in self.pending_inputs:
            dx = input_data.get("dx", 0)
            dy = input_data.get("dy", 0)
            speed_multiplier = input_data.get("speed_multiplier", 1.0)

            # Bewege den Spieler ohne neue Eingaben zur Liste hinzuzufügen
            self.move(dx, dy, speed_multiplier, prediction=False)

        self.logger.debug(f"Server-Reconciliation: Server-Position=({server_x}, {server_y}), "
                        f"Finale Position=({self.x}, {self.y}), "
                        f"Ausstehende Eingaben={len(self.pending_inputs)}")
