#!/usr/bin/env python
"""
OptionsMenu class - Handles the options menu (refactored version)
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any, Callable, Optional
from game.core.input_manager import InputManager, InputAction
from game.core.game_state_manager import GameState


class OptionsMenuRefactored:
    """Handles the options menu (refactored version)"""

    def __init__(self, game):
        """Initialize the options menu

        Args:
            game: Game instance
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing options menu (refactored)")

        self.game = game
        self.screen = game.screen
        self.input_manager = game.input_manager
        self.state_manager = game.state_manager

        # Menu state
        self.selected_option = 0
        self.visible = False

        # Menu options
        self.options = [
            "Sound: On",
            "Music: On",
            "Fullscreen: Off",
            "Controls",
            "Back"
        ]

        # Fonts
        self.title_font = pygame.font.SysFont(None, 72)
        self.option_font = pygame.font.SysFont(None, 48)

        # Colors
        self.title_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)

    def show(self) -> None:
        """Show the options menu"""
        self.logger.info("Showing options menu")
        self.visible = True
        self.selected_option = 0

    def hide(self) -> None:
        """Hide the options menu"""
        self.logger.info("Hiding options menu")
        self.visible = False

    def update(self) -> None:
        """Update the options menu"""
        if not self.visible:
            return

        # Handle input
        if self.input_manager.was_pressed(InputAction.UP):
            self.selected_option = (self.selected_option - 1) % len(self.options)
            self.logger.debug(f"Selected option: {self.options[self.selected_option]}")
        elif self.input_manager.was_pressed(InputAction.DOWN):
            self.selected_option = (self.selected_option + 1) % len(self.options)
            self.logger.debug(f"Selected option: {self.options[self.selected_option]}")
        elif self.input_manager.was_pressed(InputAction.ACTION):
            selected = self.options[self.selected_option]
            self.logger.info(f"{selected} selected")
            
            # Execute the corresponding action
            if selected == "Sound: On":
                self._toggle_sound()
            elif selected == "Music: On":
                self._toggle_music()
            elif selected == "Fullscreen: Off":
                self._toggle_fullscreen()
            elif selected == "Controls":
                self._show_controls()
            elif selected == "Back":
                self._back()
        elif self.input_manager.was_pressed(InputAction.CANCEL):
            self._back()

    def render(self, screen: Optional[pygame.Surface] = None) -> None:
        """Render the options menu

        Args:
            screen: Pygame surface to render on (optional, uses self.screen if None)
        """
        if not self.visible:
            return

        if screen is None:
            screen = self.screen

        # Clear the screen
        screen.fill((0, 0, 0))

        # Render title
        title_text = self.title_font.render("Options", True, self.title_color)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_text, title_rect)

        # Render options
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.option_color
            option_text = self.option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(screen.get_width() // 2, 200 + i * 50))
            screen.blit(option_text, option_rect)

    def _toggle_sound(self) -> None:
        """Toggle sound on/off"""
        self.logger.info("Toggling sound")
        # TODO: Implement sound toggling
        if "Sound: On" in self.options:
            self.options[0] = "Sound: Off"
        else:
            self.options[0] = "Sound: On"

    def _toggle_music(self) -> None:
        """Toggle music on/off"""
        self.logger.info("Toggling music")
        # TODO: Implement music toggling
        if "Music: On" in self.options:
            self.options[1] = "Music: Off"
        else:
            self.options[1] = "Music: On"

    def _toggle_fullscreen(self) -> None:
        """Toggle fullscreen mode"""
        self.logger.info("Toggling fullscreen")
        # TODO: Implement fullscreen toggling
        if "Fullscreen: Off" in self.options:
            self.options[2] = "Fullscreen: On"
            # pygame.display.toggle_fullscreen()
        else:
            self.options[2] = "Fullscreen: Off"
            # pygame.display.toggle_fullscreen()

    def _show_controls(self) -> None:
        """Show the controls menu"""
        self.logger.info("Showing controls menu")
        # TODO: Implement controls menu

    def _back(self) -> None:
        """Go back to the previous menu"""
        self.logger.info("Going back to previous menu")
        self.hide()
        self.state_manager.return_to_previous_state()
