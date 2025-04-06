#!/usr/bin/env python
"""
RenderManager - Verwaltet das Rendern der verschiedenen Spielzustände
"""

import logging
import pygame
from typing import Dict, Callable, Any, Optional, Tuple
from game.core.game_state_manager import GameState, GameStateManager


class RenderManager:
    """Verwaltet das Rendern der verschiedenen Spielzustände"""

    def __init__(self, screen: pygame.Surface, state_manager: GameStateManager):
        """Initialisiert den RenderManager

        Args:
            screen: Die Pygame-Surface, auf der gerendert werden soll
            state_manager: Der GameStateManager, der die Spielzustände verwaltet
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing RenderManager")

        self.screen = screen
        self.state_manager = state_manager
        
        # Render-Funktionen für die verschiedenen Spielzustände
        self.render_functions: Dict[GameState, Callable] = {}
        
        # Debug-Informationen
        self.show_debug_info = True
        self.debug_font = pygame.font.SysFont(None, 24)
        
        # FPS-Anzeige
        self.show_fps = True
        self.fps_font = pygame.font.SysFont(None, 24)
        self.current_fps = 0

    def register_render_function(self, state: GameState, render_func: Callable) -> None:
        """Registriert eine Render-Funktion für einen bestimmten Spielzustand

        Args:
            state: Der Spielzustand, für den die Render-Funktion registriert werden soll
            render_func: Die Render-Funktion, die aufgerufen werden soll
        """
        self.render_functions[state] = render_func

    def render(self) -> None:
        """Rendert den aktuellen Spielzustand"""
        # Bildschirm leeren
        self.screen.fill((0, 0, 0))
        
        # Aktuellen Spielzustand rendern
        current_state = self.state_manager.current_state
        if current_state in self.render_functions:
            self.render_functions[current_state]()
        else:
            self.logger.warning(f"No render function registered for state {current_state}")
        
        # Debug-Informationen rendern
        if self.show_debug_info:
            self._render_debug_info()
        
        # FPS-Anzeige rendern
        if self.show_fps:
            self._render_fps()
        
        # Bildschirm aktualisieren
        pygame.display.flip()

    def _render_debug_info(self) -> None:
        """Rendert Debug-Informationen"""
        # Aktuelle Spielzustand anzeigen
        state_text = self.debug_font.render(
            f"State: {self.state_manager.current_state.name}", 
            True, 
            (255, 255, 255)
        )
        self.screen.blit(state_text, (10, 70))

    def _render_fps(self) -> None:
        """Rendert die FPS-Anzeige"""
        fps_text = self.fps_font.render(
            f"FPS: {self.current_fps:.1f}", 
            True, 
            (255, 255, 255)
        )
        self.screen.blit(fps_text, (10, 10))

    def update_fps(self, fps: float) -> None:
        """Aktualisiert die FPS-Anzeige

        Args:
            fps: Die aktuellen FPS
        """
        self.current_fps = fps

    def render_text(self, text: str, position: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 255), 
                   font: Optional[pygame.font.Font] = None) -> None:
        """Rendert Text auf dem Bildschirm

        Args:
            text: Der zu rendernde Text
            position: Die Position des Texts (x, y)
            color: Die Farbe des Texts (r, g, b)
            font: Die zu verwendende Schriftart (falls None, wird die Debug-Schriftart verwendet)
        """
        if font is None:
            font = self.debug_font
        
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def render_rect(self, rect: pygame.Rect, color: Tuple[int, int, int], 
                   filled: bool = True, width: int = 1) -> None:
        """Rendert ein Rechteck auf dem Bildschirm

        Args:
            rect: Das zu rendernde Rechteck
            color: Die Farbe des Rechtecks (r, g, b)
            filled: Ob das Rechteck gefüllt sein soll
            width: Die Breite des Rahmens (nur relevant, wenn filled=False)
        """
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, width)

    def render_input_dialog(self) -> None:
        """Rendert den Eingabedialog"""
        # Dialog-Hintergrund
        dialog_width = 400
        dialog_height = 150
        dialog_x = (self.screen.get_width() - dialog_width) // 2
        dialog_y = (self.screen.get_height() - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        # Hintergrund mit Rahmen
        self.render_rect(dialog_rect, (50, 50, 50), True)
        self.render_rect(dialog_rect, (200, 200, 200), False, 2)
        
        # Titel
        title_font = pygame.font.SysFont(None, 30)
        self.render_text(
            self.state_manager.input_dialog_title,
            (dialog_x + 20, dialog_y + 20),
            (255, 255, 255),
            title_font
        )
        
        # Eingabefeld
        input_rect = pygame.Rect(dialog_x + 20, dialog_y + 60, dialog_width - 40, 40)
        self.render_rect(input_rect, (30, 30, 30), True)
        self.render_rect(input_rect, (150, 150, 150), False, 1)
        
        # Eingabetext
        input_font = pygame.font.SysFont(None, 28)
        self.render_text(
            self.state_manager.input_dialog_text,
            (dialog_x + 25, dialog_y + 70),
            (255, 255, 255),
            input_font
        )
        
        # Hinweis
        hint_font = pygame.font.SysFont(None, 20)
        self.render_text(
            "Drücke Enter zum Bestätigen, Escape zum Abbrechen",
            (dialog_x + 20, dialog_y + 120),
            (200, 200, 200),
            hint_font
        )
