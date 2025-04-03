#!/usr/bin/env python
"""
IngameMenu class - Handles the ingame menu
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any, Callable
from game.core.settings import Settings
from game.core.input_handler import InputHandler

class IngameMenu:
    """Handles the ingame menu"""

    def __init__(self, screen: pygame.Surface, settings: Settings, input_handler: InputHandler):
        """Initialize the ingame menu

        Args:
            screen: Pygame surface to render on
            settings: Game settings
            input_handler: Input handler
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ingame menu")

        self.screen = screen
        self.settings = settings
        self.input_handler = input_handler

        # Menu state
        self.active = False
        self.current_menu = "main"  # main, pokemon, bag, player, save, options, exit
        self.current_option = 0

        # Menu options
        self.menus = {
            "main": [
                {"text": "POKEMON", "action": lambda: self._change_menu("pokemon")},
                {"text": "BAG", "action": lambda: self._change_menu("bag")},
                {"text": "PLAYER", "action": lambda: self._change_menu("player")},
                {"text": "SAVE", "action": self._save_game},
                {"text": "OPTIONS", "action": self._show_options},
                {"text": "EXIT", "action": self._exit_menu}
            ],
            "pokemon": [
                {"text": "Back", "action": lambda: self._change_menu("main")}
            ],
            "bag": [
                {"text": "Back", "action": lambda: self._change_menu("main")}
            ],
            "player": [
                {"text": "Back", "action": lambda: self._change_menu("main")}
            ]
        }

        # Fonts
        self.title_font = pygame.font.SysFont(None, 36)
        self.option_font = pygame.font.SysFont(None, 30)

        # Colors
        self.title_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)
        self.background_color = (40, 40, 80)
        self.border_color = (255, 255, 255)

        # Callbacks
        self.on_show_options = None
        self.on_save_game = None

    def show(self):
        """Show the ingame menu"""
        self.active = True
        self.current_menu = "main"
        self.current_option = 0
        self.logger.info("Ingame menu opened")

    def hide(self):
        """Hide the ingame menu"""
        self.active = False
        self.logger.info("Ingame menu closed")

        # Eingaben zurücksetzen, um Probleme zu vermeiden
        self.input_handler.reset()

    def update(self):
        """Update the ingame menu"""
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
        elif self.input_handler.was_pressed("cancel") or self.input_handler.was_pressed("menu"):
            # Go back to the previous menu or exit
            self.logger.info("Cancel or menu pressed, going back")
            if self.current_menu == "main":
                self.hide()
            else:
                self._change_menu("main")

    def render(self):
        """Render the ingame menu"""
        if not self.active:
            return

        # Draw background overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Draw menu background
        menu_width = 250
        menu_height = 300
        menu_x = self.screen.get_width() - menu_width - 20
        menu_y = 20

        # Draw menu background with border
        pygame.draw.rect(self.screen, self.border_color, (menu_x-2, menu_y-2, menu_width+4, menu_height+4))
        pygame.draw.rect(self.screen, self.background_color, (menu_x, menu_y, menu_width, menu_height))

        # Draw title
        title_text = self.title_font.render("MENU", True, self.title_color)
        title_rect = title_text.get_rect(midtop=(menu_x + menu_width // 2, menu_y + 10))
        self.screen.blit(title_text, title_rect)

        # Draw options
        for i, option in enumerate(self.menus[self.current_menu]):
            color = self.selected_color if i == self.current_option else self.option_color
            option_text = self.option_font.render(option["text"], True, color)
            option_rect = option_text.get_rect(midleft=(menu_x + 20, menu_y + 60 + i * 40))
            self.screen.blit(option_text, option_rect)

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

    def _save_game(self):
        """Save the game"""
        self.logger.info("Saving game")
        if self.on_save_game:
            self.on_save_game()

    def _show_options(self):
        """Show options menu"""
        self.logger.info("Showing options menu")
        if self.on_show_options:
            self.on_show_options()
            self.hide()  # Hide ingame menu while options are shown
