#!/usr/bin/env python
"""
OptionsMenu class - Handles the options menu
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any, Callable
from game.core.settings import Settings
from game.core.input_handler import InputHandler

class OptionsMenu:
    """Handles the options menu"""

    def __init__(self, screen: pygame.Surface, settings: Settings, input_handler: InputHandler):
        """Initialize the options menu

        Args:
            screen: Pygame surface to render on
            settings: Game settings
            input_handler: Input handler
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing options menu")

        self.screen = screen
        self.settings = settings
        self.input_handler = input_handler

        # Menu state
        self.active = False
        self.current_menu = "main"  # main, video, audio, gameplay
        self.current_option = 0

        # Menu options
        self.menus = {
            "main": [
                {"text": "Video", "action": lambda: self._change_menu("video")},
                {"text": "Audio", "action": lambda: self._change_menu("audio")},
                {"text": "Gameplay", "action": lambda: self._change_menu("gameplay")},
                {"text": "Controls", "action": lambda: self._change_menu("controls")},
                {"text": "Back", "action": self._exit_menu}
            ],
            "video": [
                {"text": "Fullscreen", "action": self._toggle_fullscreen, "get_value": lambda: "On" if self.settings.get("video", "fullscreen") else "Off"},
                {"text": "Resolution", "action": self._cycle_resolution, "get_value": lambda: f"{self.settings.get('video', 'resolution')[0]}x{self.settings.get('video', 'resolution')[1]}"},
                {"text": "VSync", "action": self._toggle_vsync, "get_value": lambda: "On" if self.settings.get("video", "vsync") else "Off"},
                {"text": "FPS Limit", "action": self._cycle_fps_limit, "get_value": lambda: str(self.settings.get("video", "fps_limit"))},
                {"text": "Back", "action": lambda: self._change_menu("main")}
            ],
            "audio": [
                {"text": "Master Volume", "action": self._cycle_master_volume, "get_value": lambda: f"{int(self.settings.get('audio', 'master_volume') * 100)}%"},
                {"text": "Music Volume", "action": self._cycle_music_volume, "get_value": lambda: f"{int(self.settings.get('audio', 'music_volume') * 100)}%"},
                {"text": "SFX Volume", "action": self._cycle_sfx_volume, "get_value": lambda: f"{int(self.settings.get('audio', 'sfx_volume') * 100)}%"},
                {"text": "Mute", "action": self._toggle_mute, "get_value": lambda: "On" if self.settings.get("audio", "mute") else "Off"},
                {"text": "Back", "action": lambda: self._change_menu("main")}
            ],
            "gameplay": [
                {"text": "Text Speed", "action": self._cycle_text_speed, "get_value": lambda: self.settings.get("gameplay", "text_speed").capitalize()},
                {"text": "Battle Animations", "action": self._toggle_battle_animations, "get_value": lambda: "On" if self.settings.get("gameplay", "battle_animations") else "Off"},
                {"text": "Battle Style", "action": self._cycle_battle_style, "get_value": lambda: self.settings.get("gameplay", "battle_style").capitalize()},
                {"text": "Difficulty", "action": self._cycle_difficulty, "get_value": lambda: self.settings.get("gameplay", "difficulty").capitalize()},
                {"text": "Run Speed", "action": self._cycle_run_speed, "get_value": lambda: f"{int(self.settings.get('gameplay', 'run_speed') * 100)}%"},
                {"text": "Fast Forward Speed", "action": self._cycle_fast_forward_speed, "get_value": lambda: f"{int(self.settings.get('gameplay', 'fast_forward_speed') * 100)}%"},
                {"text": "Back", "action": lambda: self._change_menu("main")}
            ],
            "controls": [
                {"text": "Keyboard", "action": self._toggle_keyboard, "get_value": lambda: "Enabled" if self.settings.get("controls", "keyboard_enabled") else "Disabled"},
                {"text": "Controller", "action": self._toggle_controller, "get_value": lambda: "Enabled" if self.settings.get("controls", "controller_enabled") else "Disabled"},
                {"text": "Controller ID", "action": self._cycle_controller_id, "get_value": lambda: str(self.settings.get("controls", "controller_id"))},
                {"text": "Back", "action": lambda: self._change_menu("main")}
            ]
        }

        # Fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.option_font = pygame.font.SysFont(None, 36)
        self.value_font = pygame.font.SysFont(None, 30)

        # Colors
        self.title_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)
        self.value_color = (150, 150, 255)

    def show(self):
        """Show the options menu"""
        self.active = True
        self.current_menu = "main"
        self.current_option = 0
        self.logger.info("Options menu opened")

    def hide(self):
        """Hide the options menu"""
        self.active = False
        self.logger.info("Options menu closed")

        # Callback für das Schließen des Menüs
        if hasattr(self, "on_close") and self.on_close:
            self.on_close()

    def update(self):
        """Update the options menu"""
        if not self.active:
            return

        # Handle input
        if self.input_handler.was_pressed("up"):
            self.current_option = (self.current_option - 1) % len(self.menus[self.current_menu])
        elif self.input_handler.was_pressed("down"):
            self.current_option = (self.current_option + 1) % len(self.menus[self.current_menu])
        elif self.input_handler.was_pressed("action"):
            # Execute the action for the current option
            self.logger.info(f"Executing action for option: {self.menus[self.current_menu][self.current_option]['text']}")
            self.menus[self.current_menu][self.current_option]["action"]()
        elif self.input_handler.was_pressed("cancel"):
            # Go back to the previous menu or exit
            self.logger.info("Cancel pressed, going back")
            if self.current_menu == "main":
                self.hide()
            else:
                self._change_menu("main")

    def render(self):
        """Render the options menu"""
        if not self.active:
            return

        # Draw background
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Draw title
        title_text = self.title_font.render(f"{self.current_menu.capitalize()} Options", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(title_text, title_rect)

        # Draw options
        for i, option in enumerate(self.menus[self.current_menu]):
            # Option text
            color = self.selected_color if i == self.current_option else self.option_color
            option_text = self.option_font.render(option["text"], True, color)
            option_rect = option_text.get_rect(midleft=(self.screen.get_width() // 4, 150 + i * 50))
            self.screen.blit(option_text, option_rect)

            # Option value (if available)
            if "get_value" in option:
                value_text = self.value_font.render(option["get_value"](), True, self.value_color)
                value_rect = value_text.get_rect(midright=(self.screen.get_width() * 3 // 4, 150 + i * 50))
                self.screen.blit(value_text, value_rect)

    def _change_menu(self, menu: str):
        """Change the current menu

        Args:
            menu: Menu name
        """
        self.current_menu = menu
        self.current_option = 0
        self.logger.info(f"Changed to {menu} menu")

    def _exit_menu(self):
        """Exit the menu"""
        self.hide()
        self.settings.save()
        self.logger.info("Settings saved")

    # Video settings
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        fullscreen = self.settings.toggle_fullscreen()
        self.logger.info(f"Fullscreen set to {fullscreen}")

        # Callback für Auflösungsänderung aufrufen, falls vorhanden
        if hasattr(self, "on_resolution_changed") and self.on_resolution_changed:
            self.on_resolution_changed()

    def _cycle_resolution(self):
        """Cycle through available resolutions"""
        resolutions = self.settings.get_available_resolutions()
        current_resolution = self.settings.get_resolution()
        current_index = resolutions.index(current_resolution)
        next_index = (current_index + 1) % len(resolutions)
        next_resolution = resolutions[next_index]

        # Direkt die Auflösung in den Einstellungen setzen
        self.settings.settings["video"]["resolution"] = next_resolution
        self.logger.info(f"Resolution directly set to {next_resolution[0]}x{next_resolution[1]}")

        # Callback für Auflösungsänderung aufrufen, falls vorhanden
        if hasattr(self, "on_resolution_changed") and self.on_resolution_changed:
            self.on_resolution_changed()

    def _toggle_vsync(self):
        """Toggle VSync"""
        vsync = not self.settings.get("video", "vsync")
        self.settings.set("video", "vsync", vsync)

    def _cycle_fps_limit(self):
        """Cycle through FPS limits"""
        fps_limits = [30, 60, 120, 144, 240, 0]  # 0 means unlimited
        current_fps = self.settings.get("video", "fps_limit")
        current_index = fps_limits.index(current_fps) if current_fps in fps_limits else 1
        next_index = (current_index + 1) % len(fps_limits)
        self.settings.set("video", "fps_limit", fps_limits[next_index])

    # Audio settings
    def _cycle_master_volume(self):
        """Cycle through master volume levels"""
        volume = self.settings.get("audio", "master_volume")
        volume = round((volume + 0.1) * 10) / 10  # Increment by 0.1 and round to nearest 0.1
        if volume > 1.0:
            volume = 0.0
        self.settings.set("audio", "master_volume", volume)

    def _cycle_music_volume(self):
        """Cycle through music volume levels"""
        volume = self.settings.get("audio", "music_volume")
        volume = round((volume + 0.1) * 10) / 10  # Increment by 0.1 and round to nearest 0.1
        if volume > 1.0:
            volume = 0.0
        self.settings.set("audio", "music_volume", volume)

    def _cycle_sfx_volume(self):
        """Cycle through SFX volume levels"""
        volume = self.settings.get("audio", "sfx_volume")
        volume = round((volume + 0.1) * 10) / 10  # Increment by 0.1 and round to nearest 0.1
        if volume > 1.0:
            volume = 0.0
        self.settings.set("audio", "sfx_volume", volume)

    def _toggle_mute(self):
        """Toggle mute"""
        mute = not self.settings.get("audio", "mute")
        self.settings.set("audio", "mute", mute)

    # Gameplay settings
    def _cycle_text_speed(self):
        """Cycle through text speeds"""
        speeds = ["slow", "normal", "fast"]
        current_speed = self.settings.get("gameplay", "text_speed")
        current_index = speeds.index(current_speed)
        next_index = (current_index + 1) % len(speeds)
        self.settings.set("gameplay", "text_speed", speeds[next_index])

    def _toggle_battle_animations(self):
        """Toggle battle animations"""
        animations = not self.settings.get("gameplay", "battle_animations")
        self.settings.set("gameplay", "battle_animations", animations)

    def _cycle_battle_style(self):
        """Cycle through battle styles"""
        styles = ["shift", "set"]
        current_style = self.settings.get("gameplay", "battle_style")
        current_index = styles.index(current_style)
        next_index = (current_index + 1) % len(styles)
        self.settings.set("gameplay", "battle_style", styles[next_index])

    def _cycle_difficulty(self):
        """Cycle through difficulty levels"""
        difficulties = ["easy", "normal", "hard"]
        current_difficulty = self.settings.get("gameplay", "difficulty")
        current_index = difficulties.index(current_difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.settings.set("gameplay", "difficulty", difficulties[next_index])

    def _cycle_run_speed(self):
        """Cycle through run speed levels"""
        speeds = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
        current_speed = self.settings.get("gameplay", "run_speed")
        # Finde den nächsten Wert in der Liste
        next_speed = speeds[0]
        for speed in speeds:
            if speed > current_speed:
                next_speed = speed
                break
        else:
            # Wenn wir hier sind, war der aktuelle Wert größer als alle Werte in der Liste
            # oder gleich dem letzten Wert, also gehen wir zurück zum ersten Wert
            next_speed = speeds[0]
        self.settings.set("gameplay", "run_speed", next_speed)
        self.logger.info(f"Run speed set to {next_speed}")

    def _cycle_fast_forward_speed(self):
        """Cycle through fast forward speed levels"""
        speeds = [1.5, 2.0, 3.0, 5.0, 10.0]
        current_speed = self.settings.get("gameplay", "fast_forward_speed")
        # Finde den nächsten Wert in der Liste
        next_speed = speeds[0]
        for speed in speeds:
            if speed > current_speed:
                next_speed = speed
                break
        else:
            # Wenn wir hier sind, war der aktuelle Wert größer als alle Werte in der Liste
            # oder gleich dem letzten Wert, also gehen wir zurück zum ersten Wert
            next_speed = speeds[0]
        self.settings.set("gameplay", "fast_forward_speed", next_speed)
        self.logger.info(f"Fast forward speed set to {next_speed}")

    # Controls settings
    def _toggle_keyboard(self):
        """Toggle keyboard input"""
        keyboard = not self.settings.get("controls", "keyboard_enabled")
        self.settings.set("controls", "keyboard_enabled", keyboard)

    def _toggle_controller(self):
        """Toggle controller input"""
        controller = not self.settings.get("controls", "controller_enabled")
        self.settings.set("controls", "controller_enabled", controller)

    def _cycle_controller_id(self):
        """Cycle through controller IDs"""
        controller_id = self.settings.get("controls", "controller_id")
        controller_id = (controller_id + 1) % 4  # Assume max 4 controllers
        self.settings.set("controls", "controller_id", controller_id)
