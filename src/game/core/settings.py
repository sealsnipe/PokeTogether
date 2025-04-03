#!/usr/bin/env python
"""
Settings class - Handles game settings
"""

import json
import os
import logging
from typing import Dict, Any, List, Tuple

class Settings:
    """Handles game settings"""

    def __init__(self, settings_file: str = "settings.json"):
        """Initialize the settings

        Args:
            settings_file: Path to the settings file
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing settings")

        self.settings_file = settings_file

        # Default settings
        self.default_settings = {
            "video": {
                "fullscreen": False,
                "resolution": (800, 600),
                "available_resolutions": [
                    (640, 480),
                    (800, 600),
                    (1024, 768),
                    (1280, 720),
                    (1366, 768),
                    (1920, 1080)
                ],
                "vsync": True,
                "fps_limit": 60
            },
            "audio": {
                "master_volume": 0.8,
                "music_volume": 0.7,
                "sfx_volume": 0.9,
                "mute": False
            },
            "gameplay": {
                "text_speed": "normal",  # slow, normal, fast
                "battle_animations": True,
                "battle_style": "shift",  # shift, set
                "difficulty": "normal",  # easy, normal, hard
                "run_speed": 2.0,  # Laufgeschwindigkeit (1.0 = normal, 2.0 = doppelt so schnell)
                "fast_forward_speed": 3.0  # Vorspulgeschwindigkeit (1.0 = normal, 3.0 = dreifache Geschwindigkeit)
            },
            "controls": {
                "keyboard_enabled": True,
                "controller_enabled": True,
                "controller_id": 0
            }
        }

        # Current settings
        self.settings = self.default_settings.copy()

        # Load settings from file
        self.load()

    def load(self) -> bool:
        """Load settings from file

        Returns:
            bool: True if settings were loaded successfully, False otherwise
        """
        if not os.path.exists(self.settings_file):
            self.logger.info(f"Settings file {self.settings_file} not found, using default settings")
            return False

        try:
            with open(self.settings_file, "r") as f:
                loaded_settings = json.load(f)

            # Update settings with loaded values
            self._update_dict(self.settings, loaded_settings)

            self.logger.info(f"Settings loaded from {self.settings_file}")
            return True
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Error loading settings: {e}")
            return False

    def save(self) -> bool:
        """Save settings to file

        Returns:
            bool: True if settings were saved successfully, False otherwise
        """
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)

            self.logger.info(f"Settings saved to {self.settings_file}")
            return True
        except IOError as e:
            self.logger.error(f"Error saving settings: {e}")
            return False

    def reset(self):
        """Reset settings to default values"""
        self.settings = self.default_settings.copy()
        self.logger.info("Settings reset to default values")

    def get(self, category: str, setting: str) -> Any:
        """Get a setting value

        Args:
            category: Setting category (video, audio, gameplay, controls)
            setting: Setting name

        Returns:
            Any: Setting value
        """
        if category in self.settings and setting in self.settings[category]:
            return self.settings[category][setting]
        else:
            self.logger.warning(f"Setting {category}.{setting} not found")
            return None

    def set(self, category: str, setting: str, value: Any) -> bool:
        """Set a setting value

        Args:
            category: Setting category (video, audio, gameplay, controls)
            setting: Setting name
            value: Setting value

        Returns:
            bool: True if the setting was set successfully, False otherwise
        """
        if category in self.settings and setting in self.settings[category]:
            self.settings[category][setting] = value
            self.logger.info(f"Setting {category}.{setting} set to {value}")
            return True
        else:
            self.logger.warning(f"Setting {category}.{setting} not found")
            return False

    def get_resolution(self) -> Tuple[int, int]:
        """Get the current resolution

        Returns:
            Tuple[int, int]: Current resolution (width, height)
        """
        return self.settings["video"]["resolution"]

    def set_resolution(self, width: int, height: int) -> bool:
        """Set the resolution

        Args:
            width: Screen width
            height: Screen height

        Returns:
            bool: True if the resolution was set successfully, False otherwise
        """
        resolution = (width, height)
        if resolution in self.settings["video"]["available_resolutions"]:
            self.settings["video"]["resolution"] = resolution
            self.logger.info(f"Resolution set to {width}x{height}")
            return True
        else:
            self.logger.warning(f"Resolution {width}x{height} not available")
            return False

    def toggle_fullscreen(self) -> bool:
        """Toggle fullscreen mode

        Returns:
            bool: New fullscreen state
        """
        self.settings["video"]["fullscreen"] = not self.settings["video"]["fullscreen"]
        self.logger.info(f"Fullscreen set to {self.settings['video']['fullscreen']}")
        return self.settings["video"]["fullscreen"]

    def get_available_resolutions(self) -> List[Tuple[int, int]]:
        """Get available resolutions

        Returns:
            List[Tuple[int, int]]: List of available resolutions
        """
        return self.settings["video"]["available_resolutions"]

    def _update_dict(self, target: Dict, source: Dict):
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
