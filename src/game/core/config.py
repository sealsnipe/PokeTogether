#!/usr/bin/env python
"""
Configuration module for the game
Handles loading and saving of configuration files
"""

import json
import os
import logging
import socket
from typing import Dict, Any, Optional

class Config:
    """Configuration handler for the game"""

    def __init__(self, config_file: str = "config.json"):
        """Initialize the configuration

        Args:
            config_file: Path to the configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing configuration from {config_file}")

        self.config_file = config_file

        # Default configuration
        self.default_config = {
            "player": {
                "name": "Player",
                "character": "Red"
            },
            "multiplayer": {
                "server_host": "127.0.0.1",
                "server_port": 8765,
                "update_rate": 20,  # Updates per second
                "interpolation": True,  # Bewegungen interpolieren
                "prediction": True,  # Client-Side-Prediction aktivieren
                "reconciliation": True,  # Server-Reconciliation aktivieren
                "exact_positioning": False,  # Exakte Positionierung ohne Interpolation
                "latency_simulation": 0,  # Künstliche Latenz in Millisekunden (0 = deaktiviert)
                "jitter_simulation": 0,  # Künstliche Jitter in Millisekunden (0 = deaktiviert)
                "jitter_buffer_size": 3,  # Größe des Jitter-Puffers
                "jitter_buffer_delay": 0.05  # Verzögerung des Jitter-Puffers in Sekunden
            },
            "paths": {
                "save_dir": "saves",
                "screenshots_dir": "screenshots",
                "logs_dir": "logs"
            },
            "instance": {
                "id": "default",
                "window_title": "PokeTogether"
            }
        }

        # Current configuration
        self.config = self.default_config.copy()

        # Load configuration from file
        self.load()

    def load(self) -> bool:
        """Load configuration from file

        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        if not os.path.exists(self.config_file):
            self.logger.info(f"Configuration file {self.config_file} not found, using default configuration")
            return False

        try:
            with open(self.config_file, "r") as f:
                loaded_config = json.load(f)

            # Update configuration with loaded values
            self._update_dict(self.config, loaded_config)

            self.logger.info(f"Configuration loaded from {self.config_file}")
            return True
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error loading configuration: {e}")
            return False

    def save(self) -> bool:
        """Save configuration to file

        Returns:
            bool: True if configuration was saved successfully, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)

            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
        except IOError as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False

    def reset(self) -> None:
        """Reset configuration to default values"""
        self.config = self.default_config.copy()
        self.logger.info("Configuration reset to default values")

    def get(self, section: str, key: str) -> Any:
        """Get a configuration value

        Args:
            section: Configuration section
            key: Configuration key

        Returns:
            Any: Configuration value
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        else:
            self.logger.warning(f"Configuration {section}.{key} not found")
            return None

    def set(self, section: str, key: str, value: Any) -> bool:
        """Set a configuration value

        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value

        Returns:
            bool: True if the configuration was set successfully, False otherwise
        """
        if section in self.config and key in self.config[section]:
            self.config[section][key] = value
            self.logger.info(f"Configuration {section}.{key} set to {value}")
            return True
        else:
            self.logger.warning(f"Configuration {section}.{key} not found")
            return False

    def get_player_name(self) -> str:
        """Get the player name

        Returns:
            str: Player name
        """
        return self.config["player"]["name"]

    def get_save_dir(self) -> str:
        """Get the save directory

        Returns:
            str: Save directory path
        """
        # Get the instance-specific save directory
        instance_id = self.config["instance"]["id"]
        base_save_dir = self.config["paths"]["save_dir"]
        return os.path.join(base_save_dir, instance_id)

    def get_screenshots_dir(self) -> str:
        """Get the screenshots directory

        Returns:
            str: Screenshots directory path
        """
        # Get the instance-specific screenshots directory
        instance_id = self.config["instance"]["id"]
        base_screenshots_dir = self.config["paths"]["screenshots_dir"]
        return os.path.join(base_screenshots_dir, instance_id)

    def get_logs_dir(self) -> str:
        """Get the logs directory

        Returns:
            str: Logs directory path
        """
        # Get the instance-specific logs directory
        instance_id = self.config["instance"]["id"]
        base_logs_dir = self.config["paths"]["logs_dir"]
        return os.path.join(base_logs_dir, instance_id)

    def get_window_title(self) -> str:
        """Get the window title

        Returns:
            str: Window title
        """
        return self.config["instance"]["window_title"]

    def get_server_host(self) -> str:
        """Get the server host

        Returns:
            str: Server host
        """
        return self.config["multiplayer"]["server_host"]

    def get_server_port(self) -> int:
        """Get the server port

        Returns:
            int: Server port
        """
        return self.config["multiplayer"]["server_port"]

    def get_update_rate(self) -> int:
        """Get the update rate

        Returns:
            int: Update rate (updates per second)
        """
        return self.config["multiplayer"]["update_rate"]

    def get_interpolation(self) -> bool:
        """Get the interpolation setting

        Returns:
            bool: True if interpolation is enabled, False otherwise
        """
        return self.config["multiplayer"]["interpolation"]

    def get_prediction(self) -> bool:
        """Get the prediction setting

        Returns:
            bool: True if client-side prediction is enabled, False otherwise
        """
        return self.config["multiplayer"].get("prediction", True)

    def get_exact_positioning(self) -> bool:
        """Get the exact positioning setting

        Returns:
            bool: True if exact positioning is enabled, False otherwise
        """
        return self.config["multiplayer"].get("exact_positioning", False)

    def get_jitter_buffer_size(self) -> int:
        """Get the jitter buffer size

        Returns:
            int: Jitter buffer size
        """
        return self.config["multiplayer"].get("jitter_buffer_size", 3)

    def get_jitter_buffer_delay(self) -> float:
        """Get the jitter buffer delay

        Returns:
            float: Jitter buffer delay in seconds
        """
        return self.config["multiplayer"].get("jitter_buffer_delay", 0.05)

    def get_reconciliation(self) -> bool:
        """Get the reconciliation setting

        Returns:
            bool: True if server reconciliation is enabled, False otherwise
        """
        return self.config["multiplayer"]["reconciliation"]

    def get_latency_simulation(self) -> int:
        """Get the latency simulation setting

        Returns:
            int: Latency simulation in milliseconds (0 = disabled)
        """
        return self.config["multiplayer"]["latency_simulation"]

    def get_jitter_simulation(self) -> int:
        """Get the jitter simulation setting

        Returns:
            int: Jitter simulation in milliseconds (0 = disabled)
        """
        return self.config["multiplayer"]["jitter_simulation"]

    def get_local_ip(self) -> str:
        """Get the local IP address

        Returns:
            str: Local IP address
        """
        try:
            # Erstelle einen Socket, der sich mit einem externen Server verbindet
            # Dies ist ein Trick, um die lokale IP-Adresse zu ermitteln
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google DNS-Server
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            self.logger.error(f"Error getting local IP: {e}")
            return "127.0.0.1"

    def _update_dict(self, target: Dict, source: Dict) -> None:
        """Update a dictionary recursively

        Args:
            target: Target dictionary
            source: Source dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            elif key in target:
                target[key] = value
