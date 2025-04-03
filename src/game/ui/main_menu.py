#!/usr/bin/env python
"""
MainMenu class - Handles the main menu
"""

import pygame
import logging
from typing import Dict, List, Tuple, Any, Callable
from game.core.input_handler import InputHandler

class MainMenu:
    """Handles the main menu"""
    
    def __init__(self, screen: pygame.Surface, input_handler: InputHandler):
        """Initialize the main menu
        
        Args:
            screen: Pygame surface to render on
            input_handler: Input handler
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing main menu")
        
        self.screen = screen
        self.input_handler = input_handler
        
        # Menu state
        self.current_option = 0
        
        # Menu options
        self.options = [
            {"text": "New Game", "action": self._new_game},
            {"text": "Continue", "action": self._continue_game},
            {"text": "Options", "action": self._show_options},
            {"text": "Exit", "action": self._exit_game}
        ]
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 72)
        self.option_font = pygame.font.SysFont(None, 48)
        
        # Colors
        self.title_color = (255, 255, 255)
        self.option_color = (200, 200, 200)
        self.selected_color = (255, 255, 0)
        
        # Callbacks
        self.on_new_game = None
        self.on_continue_game = None
        self.on_show_options = None
        self.on_exit_game = None
        
    def update(self):
        """Update the main menu"""
        # Handle input
        if self.input_handler.was_pressed("up"):
            self.current_option = (self.current_option - 1) % len(self.options)
        elif self.input_handler.was_pressed("down"):
            self.current_option = (self.current_option + 1) % len(self.options)
        elif self.input_handler.was_pressed("action"):
            # Execute the action for the current option
            self.options[self.current_option]["action"]()
                
    def render(self):
        """Render the main menu"""
        # Draw background
        self.screen.fill((0, 0, 100))
        
        # Draw title
        title_text = self.title_font.render("PokeTogether", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw options
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.current_option else self.option_color
            option_text = self.option_font.render(option["text"], True, color)
            option_rect = option_text.get_rect(center=(self.screen.get_width() // 2, 250 + i * 60))
            self.screen.blit(option_text, option_rect)
            
    def set_callbacks(self, on_new_game: Callable = None, on_continue_game: Callable = None, 
                     on_show_options: Callable = None, on_exit_game: Callable = None):
        """Set callbacks for menu actions
        
        Args:
            on_new_game: Callback for new game
            on_continue_game: Callback for continue game
            on_show_options: Callback for show options
            on_exit_game: Callback for exit game
        """
        self.on_new_game = on_new_game
        self.on_continue_game = on_continue_game
        self.on_show_options = on_show_options
        self.on_exit_game = on_exit_game
        
    def _new_game(self):
        """Start a new game"""
        self.logger.info("New game selected")
        if self.on_new_game:
            self.on_new_game()
            
    def _continue_game(self):
        """Continue a saved game"""
        self.logger.info("Continue game selected")
        if self.on_continue_game:
            self.on_continue_game()
            
    def _show_options(self):
        """Show options menu"""
        self.logger.info("Options selected")
        if self.on_show_options:
            self.on_show_options()
            
    def _exit_game(self):
        """Exit the game"""
        self.logger.info("Exit selected")
        if self.on_exit_game:
            self.on_exit_game()
