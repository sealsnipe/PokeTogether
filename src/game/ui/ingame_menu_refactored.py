#!/usr/bin/env python
"""
IngameMenu class - Handles the in-game menu (refactored version)
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any, Callable, Optional
from game.core.input_manager import InputManager, InputAction
from game.core.game_state_manager import GameState


class IngameMenuRefactored:
    """Handles the in-game menu (refactored version)"""

    def __init__(self, game):
        """Initialize the in-game menu

        Args:
            game: Game instance
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing in-game menu (refactored)")

        self.game = game
        self.screen = game.screen
        self.input_manager = game.input_manager
        self.state_manager = game.state_manager

        # Menu state
        self.selected_option = 0
        self.visible = False

        # Menu options
        self.options = [
            "Resume",
            "Save Game",
            "Load Game",
            "Options",
            "Main Menu",
            "Exit"
        ]

        # Fonts
        self.title_font = pygame.font.SysFont(None, 72)
        self.option_font = pygame.font.SysFont(None, 48)

        # Colors
        self.title_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)

    def show(self) -> None:
        """Show the in-game menu"""
        self.logger.info("Showing in-game menu")
        self.visible = True
        self.selected_option = 0

    def hide(self) -> None:
        """Hide the in-game menu"""
        self.logger.info("Hiding in-game menu")
        self.visible = False

    def update(self) -> None:
        """Update the in-game menu"""
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
            if selected == "Resume":
                self._resume()
            elif selected == "Save Game":
                self._save_game()
            elif selected == "Load Game":
                self._load_game()
            elif selected == "Options":
                self._show_options()
            elif selected == "Main Menu":
                self._return_to_main_menu()
            elif selected == "Exit":
                self._exit_game()
        elif self.input_manager.was_pressed(InputAction.CANCEL) or self.input_manager.was_pressed(InputAction.MENU):
            self._resume()

    def render(self, screen: Optional[pygame.Surface] = None) -> None:
        """Render the in-game menu

        Args:
            screen: Pygame surface to render on (optional, uses self.screen if None)
        """
        if not self.visible:
            return

        if screen is None:
            screen = self.screen

        # Darken the background
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Render title
        title_text = self.title_font.render("Pause", True, self.title_color)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_text, title_rect)

        # Render options
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.option_color
            option_text = self.option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(screen.get_width() // 2, 200 + i * 50))
            screen.blit(option_text, option_rect)

    def _resume(self) -> None:
        """Resume the game"""
        self.logger.info("Resuming game")
        self.hide()
        self.state_manager.change_state(GameState.PLAYING)

    def _save_game(self) -> None:
        """Save the game"""
        self.logger.info("Saving game")
        # TODO: Implement game saving

    def _load_game(self) -> None:
        """Load a saved game"""
        self.logger.info("Loading game")
        # TODO: Implement game loading

    def _show_options(self) -> None:
        """Show the options menu"""
        self.logger.info("Showing options menu")
        self.hide()
        self.state_manager.change_state(GameState.OPTIONS)

    def _return_to_main_menu(self) -> None:
        """Return to the main menu"""
        self.logger.info("Returning to main menu")
        self.hide()
        self.state_manager.change_state(GameState.MAIN_MENU)

    def _exit_game(self) -> None:
        """Exit the game"""
        self.logger.info("Exiting game")
        self.game.quit()
