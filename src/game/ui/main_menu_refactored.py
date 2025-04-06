#!/usr/bin/env python
"""
MainMenu class - Handles the main menu (refactored version)
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any, Callable, Optional
from game.core.input_manager import InputManager, InputAction


class MainMenuRefactored:
    """Handles the main menu (refactored version)"""

    def __init__(self, game):
        """Initialize the main menu

        Args:
            game: Game instance
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing main menu (refactored)")

        self.game = game
        self.screen = game.screen
        self.input_manager = game.input_manager

        # Menu state
        self.selected_option = 0
        self.visible = False

        # Menu options
        self.options = [
            "Host Game",
            "Join Game",
            "Continue",
            "Options",
            "Exit"
        ]

        # Log-Ausgabe für die Menüoptionen
        self.logger.info("[INFO] Hauptmenü initialisiert – Optionen: Host Game, Join Game, Continue, Options, Exit")

        # Fonts
        self.title_font = pygame.font.SysFont(None, 72)
        self.option_font = pygame.font.SysFont(None, 48)

        # Colors
        self.title_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)

    def show(self) -> None:
        """Show the main menu"""
        self.logger.info("Showing main menu")
        self.visible = True
        self.selected_option = 0
        # Debug-Ausgabe
        self.logger.debug(f"Main menu visibility set to: {self.visible}")

    def hide(self) -> None:
        """Hide the main menu"""
        self.logger.info("Hiding main menu")
        self.visible = False

    def update(self) -> None:
        """Update the main menu"""
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
            if selected == "Host Game":
                self._host_game()
            elif selected == "Join Game":
                self._join_game()
            elif selected == "Continue":
                self._continue_game()
            elif selected == "Options":
                self._show_options()
            elif selected == "Exit":
                self._exit_game()

    def render(self, screen: Optional[pygame.Surface] = None) -> None:
        """Render the main menu

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
        title_text = self.title_font.render("PokeTogether", True, self.title_color)
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_text, title_rect)

        # Render options
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.option_color
            option_text = self.option_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(screen.get_width() // 2, 200 + i * 50))
            screen.blit(option_text, option_rect)

    # Die Methode _new_game wurde entfernt, da sie nicht mehr benötigt wird

    def _host_game(self) -> None:
        """Host a multiplayer game"""
        self.logger.info("=== HOST GAME SELECTED ===")
        self.logger.info("[INFO] Starte Spiel als Host (Spieler 1)")
        # Starte das Spiel als Host (Spieler 1)
        self.game.start_new_game(as_host=True)
        self.hide()

    def _join_game(self) -> None:
        """Join a multiplayer game"""
        self.logger.info("=== JOIN GAME SELECTED ===")
        self.logger.info("[INFO] Verbinde automatisch mit lokaler Session (Spieler 2)")
        # Verstecke das Hauptmenü
        self.hide()
        # Verbinde automatisch mit der lokalen Session (localhost)
        self.game.join_session("localhost", 8765)
        self.logger.info("[INFO] Spieler 2 startet bei Position (560, 448)")

    def _continue_game(self) -> None:
        """Continue a saved game"""
        self.logger.info("Continue game selected")
        self.game.continue_game()
        self.hide()

    def _show_options(self) -> None:
        """Show the options menu"""
        self.logger.info("Options selected")
        self.game.show_options_menu()
        self.hide()

    def _exit_game(self) -> None:
        """Exit the game"""
        self.logger.info("Exit selected")
        self.game.quit()
