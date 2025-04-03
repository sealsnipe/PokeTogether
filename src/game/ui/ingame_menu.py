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
                {"text": "MULTIPLAYER", "action": lambda: self._change_menu("multiplayer")},
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
            ],
            "multiplayer": [
                {"text": "HOST GAME", "action": self._host_game},
                {"text": "JOIN GAME", "action": self._join_game},
                {"text": "DISCONNECT", "action": self._disconnect},
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
        self.on_host_game = None
        self.on_join_game = None
        self.on_disconnect = None

    def show(self):
        """Show the ingame menu"""
        self.active = True
        self.current_menu = "main"
        self.current_option = 0
        self.logger.info("Ingame menu opened")

    def hide(self):
        """Hide the ingame menu"""
        self.active = False
        self.current_menu = "main"  # Zurück zum Hauptmenü
        self.current_option = 0    # Erste Option auswählen
        self.logger.info("Ingame menu closed")

    def update(self):
        """Update the ingame menu"""
        if not self.active:
            return

        # Handle input
        if self.input_handler.was_pressed("up"):
            self.current_option = (self.current_option - 1) % len(self.menus[self.current_menu])
        elif self.input_handler.was_pressed("down"):
            self.current_option = (self.current_option + 1) % len(self.menus[self.current_menu])
        elif self.input_handler.was_pressed("action") or self._check_controller_action():
            # Execute the action for the current option
            self.logger.info(f"Executing action for option: {self.menus[self.current_menu][self.current_option]['text']}")
            self.menus[self.current_menu][self.current_option]["action"]()
        elif self.input_handler.was_pressed("cancel") or self.input_handler.was_pressed("menu") or self._check_controller_cancel():
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

    def _host_game(self):
        """Host a multiplayer game"""
        self.logger.info("Hosting multiplayer game")
        if self.on_host_game:
            self.on_host_game()

    def _join_game(self):
        """Join a multiplayer game"""
        self.logger.info("Joining multiplayer game")
        if self.on_join_game:
            self.on_join_game()

    def _disconnect(self):
        """Disconnect from multiplayer game"""
        self.logger.info("Disconnecting from multiplayer game")
        if self.on_disconnect:
            self.on_disconnect()

    def _check_controller_action(self):
        """Prüft, ob die A-Taste auf dem Controller gedrückt wurde"""
        # Prüfen, ob ein Controller angeschlossen ist
        if self.input_handler.controllers and len(self.input_handler.controllers) > 0:
            controller = self.input_handler.controllers[0]
            try:
                # A-Taste direkt prüfen
                from game.core.controller_constants import BUTTON_A
                if controller.get_button(BUTTON_A):
                    # Prüfen, ob die Taste im letzten Frame nicht gedrückt war
                    # Dies verhindert, dass die Aktion mehrmals ausgeführt wird
                    if not hasattr(self, "_last_a_button_state") or not self._last_a_button_state:
                        self._last_a_button_state = True
                        return True
                    self._last_a_button_state = True
                else:
                    self._last_a_button_state = False
            except Exception as e:
                self.logger.error(f"Fehler bei der Controller-Prüfung: {e}")
        return False

    def _check_controller_cancel(self):
        """Prüft, ob die B-Taste auf dem Controller gedrückt wurde"""
        # Prüfen, ob ein Controller angeschlossen ist
        if self.input_handler.controllers and len(self.input_handler.controllers) > 0:
            controller = self.input_handler.controllers[0]
            try:
                # B-Taste direkt prüfen
                from game.core.controller_constants import BUTTON_B
                if controller.get_button(BUTTON_B):
                    # Prüfen, ob die Taste im letzten Frame nicht gedrückt war
                    # Dies verhindert, dass die Aktion mehrmals ausgeführt wird
                    if not hasattr(self, "_last_b_button_state") or not self._last_b_button_state:
                        self._last_b_button_state = True
                        return True
                    self._last_b_button_state = True
                else:
                    self._last_b_button_state = False
            except Exception as e:
                self.logger.error(f"Fehler bei der Controller-Prüfung: {e}")
        return False
