"""
Chat-UI-Modul - Enthält die Benutzeroberfläche für den Chat im Multiplayer-Modus
"""

import pygame
import logging
from typing import List, Tuple, Optional, Callable


class ChatUI:
    """Handles the chat UI in multiplayer mode"""

    def __init__(self, screen: pygame.Surface):
        """Initialize the chat UI

        Args:
            screen: Pygame surface to render on
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing chat UI")

        self.screen = screen
        self.visible = False
        self.active = False  # True when input is active
        self.chat_history: List[Tuple[str, str]] = []  # List of (player_name, message) tuples
        self.input_text = ""
        self.scroll_position = 0
        self.max_messages = 10  # Maximum number of messages to display at once
        self.message_timeout = 5.0  # Seconds to display messages when not active
        self.last_message_time = 0.0  # Time when the last message was received

        # UI dimensions
        self.chat_width = 400
        self.chat_height = 200
        self.input_height = 30
        self.padding = 10
        self.chat_x = self.padding
        self.chat_y = self.screen.get_height() - self.chat_height - self.padding

        # Colors
        self.background_color = (0, 0, 0, 180)  # Semi-transparent black
        self.border_color = (200, 200, 200)
        self.text_color = (255, 255, 255)
        self.input_background_color = (50, 50, 50)
        self.input_border_color = (150, 150, 150)
        self.player_name_colors = {
            "": (200, 200, 200),  # Default color for system messages
            "Player": (100, 255, 100),  # Default color for the local player
        }

        # Fonts
        self.message_font = pygame.font.SysFont(None, 20)
        self.input_font = pygame.font.SysFont(None, 20)

        # Callbacks
        self.on_send_message: Optional[Callable[[str], None]] = None

    def add_message(self, player_name: str, message: str) -> None:
        """Add a message to the chat history

        Args:
            player_name: Name of the player who sent the message
            message: Message content
        """
        self.logger.info(f"Adding chat message: {player_name}: {message}")
        self.chat_history.append((player_name, message))
        self.last_message_time = pygame.time.get_ticks() / 1000.0
        self.scroll_to_bottom()

    def clear_history(self) -> None:
        """Clear the chat history"""
        self.logger.info("Clearing chat history")
        self.chat_history.clear()
        self.scroll_position = 0

    def show(self) -> None:
        """Show the chat UI"""
        self.logger.info("Showing chat UI")
        self.visible = True

    def hide(self) -> None:
        """Hide the chat UI"""
        self.logger.info("Hiding chat UI")
        self.visible = False
        self.active = False
        self.input_text = ""

    def toggle(self) -> None:
        """Toggle the chat UI visibility"""
        if self.visible and self.active:
            self.hide()
        else:
            self.show()
            self.activate()

    def activate(self) -> None:
        """Activate the chat input"""
        self.logger.info("Activating chat input")
        self.active = True
        self.input_text = ""

    def deactivate(self) -> None:
        """Deactivate the chat input"""
        self.logger.info("Deactivating chat input")
        self.active = False
        self.input_text = ""

    def scroll_up(self) -> None:
        """Scroll up in the chat history"""
        if self.scroll_position > 0:
            self.scroll_position -= 1
            self.logger.debug(f"Scrolling up to position {self.scroll_position}")

    def scroll_down(self) -> None:
        """Scroll down in the chat history"""
        if self.scroll_position < max(0, len(self.chat_history) - self.max_messages):
            self.scroll_position += 1
            self.logger.debug(f"Scrolling down to position {self.scroll_position}")

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the chat history"""
        self.scroll_position = max(0, len(self.chat_history) - self.max_messages)
        self.logger.debug(f"Scrolling to bottom (position {self.scroll_position})")

    def handle_key_event(self, event: pygame.event.Event) -> bool:
        """Handle a key event

        Args:
            event: Pygame event to handle

        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Send message
                if self.input_text.strip() and self.on_send_message:
                    self.logger.info(f"Sending chat message: {self.input_text}")
                    self.on_send_message(self.input_text)
                    self.input_text = ""
                self.deactivate()
                return True
            elif event.key == pygame.K_ESCAPE:
                # Cancel input
                self.logger.info("Canceling chat input")
                self.deactivate()
                return True
            elif event.key == pygame.K_BACKSPACE:
                # Delete last character
                self.input_text = self.input_text[:-1]
                self.logger.debug(f"Backspace pressed, input text now: {self.input_text}")
                return True
            elif event.unicode and event.unicode.isprintable():
                # Add character
                self.input_text += event.unicode
                self.logger.debug(f"Character added: {event.unicode}, input text now: {self.input_text}")
                return True
            elif event.key == pygame.K_UP:
                # Scroll up
                self.scroll_up()
                return True
            elif event.key == pygame.K_DOWN:
                # Scroll down
                self.scroll_down()
                return True

        return False

    def handle_controller_input(self, button: str) -> bool:
        """Handle a controller button press

        Args:
            button: Button that was pressed

        Returns:
            bool: True if the input was handled, False otherwise
        """
        if not self.active:
            return False

        if button == "a":
            # Send message
            if self.input_text.strip() and self.on_send_message:
                self.logger.info(f"Sending chat message: {self.input_text}")
                self.on_send_message(self.input_text)
                self.input_text = ""
            self.deactivate()
            return True
        elif button == "b":
            # Cancel input
            self.logger.info("Canceling chat input")
            self.deactivate()
            return True
        elif button == "up":
            # Scroll up
            self.scroll_up()
            return True
        elif button == "down":
            # Scroll down
            self.scroll_down()
            return True

        return False

    def update(self, dt: float) -> None:
        """Update the chat UI

        Args:
            dt: Time since last update in seconds
        """
        # Auto-hide chat if not active and no recent messages
        current_time = pygame.time.get_ticks() / 1000.0
        if (self.visible and not self.active and 
                current_time - self.last_message_time > self.message_timeout):
            self.visible = False
            self.logger.debug("Auto-hiding chat UI due to inactivity")

    def render(self) -> None:
        """Render the chat UI"""
        if not self.visible and not self.chat_history:
            return

        # Determine if we should show the full chat UI or just recent messages
        show_full_ui = self.visible

        if show_full_ui:
            # Draw chat background
            chat_surface = pygame.Surface((self.chat_width, self.chat_height), pygame.SRCALPHA)
            chat_surface.fill(self.background_color)
            self.screen.blit(chat_surface, (self.chat_x, self.chat_y))
            
            # Draw chat border
            pygame.draw.rect(self.screen, self.border_color, 
                            pygame.Rect(self.chat_x, self.chat_y, self.chat_width, self.chat_height), 
                            1)

            # Draw input background if active
            if self.active:
                input_rect = pygame.Rect(
                    self.chat_x, 
                    self.chat_y + self.chat_height - self.input_height - self.padding,
                    self.chat_width - 2 * self.padding,
                    self.input_height
                )
                pygame.draw.rect(self.screen, self.input_background_color, input_rect)
                pygame.draw.rect(self.screen, self.input_border_color, input_rect, 1)

                # Draw input text
                input_text_surface = self.input_font.render(self.input_text, True, self.text_color)
                self.screen.blit(
                    input_text_surface, 
                    (input_rect.x + 5, input_rect.y + (input_rect.height - input_text_surface.get_height()) // 2)
                )

            # Calculate visible message range
            start_idx = max(0, min(self.scroll_position, len(self.chat_history) - self.max_messages))
            end_idx = min(start_idx + self.max_messages, len(self.chat_history))
            visible_messages = self.chat_history[start_idx:end_idx]

            # Draw messages
            message_y = self.chat_y + self.padding
            if self.active:
                max_message_height = self.chat_height - 2 * self.padding - self.input_height - self.padding
            else:
                max_message_height = self.chat_height - 2 * self.padding

            for player_name, message in visible_messages:
                # Determine player name color
                if player_name in self.player_name_colors:
                    name_color = self.player_name_colors[player_name]
                else:
                    # Generate a color based on the player name
                    name_hash = sum(ord(c) for c in player_name)
                    r = (name_hash * 123) % 128 + 128  # 128-255
                    g = (name_hash * 456) % 128 + 128  # 128-255
                    b = (name_hash * 789) % 128 + 128  # 128-255
                    name_color = (r, g, b)
                    self.player_name_colors[player_name] = name_color

                # Render player name
                if player_name:
                    name_text = f"{player_name}: "
                    name_surface = self.message_font.render(name_text, True, name_color)
                    name_width = name_surface.get_width()
                    self.screen.blit(name_surface, (self.chat_x + self.padding, message_y))
                else:
                    name_width = 0

                # Render message
                message_surface = self.message_font.render(message, True, self.text_color)
                self.screen.blit(
                    message_surface, 
                    (self.chat_x + self.padding + name_width, message_y)
                )

                # Update message position
                message_y += message_surface.get_height() + 2

                # Check if we've reached the maximum height
                if message_y - self.chat_y > max_message_height:
                    break
        else:
            # Just show recent messages without the full UI
            # Only show messages that are within the timeout period
            current_time = pygame.time.get_ticks() / 1000.0
            recent_messages = []
            
            for player_name, message in reversed(self.chat_history):
                if current_time - self.last_message_time <= self.message_timeout:
                    recent_messages.insert(0, (player_name, message))
                    if len(recent_messages) >= 3:  # Show at most 3 recent messages
                        break
                else:
                    break
            
            if recent_messages:
                # Draw a small semi-transparent background
                message_height = self.message_font.get_height() + 2
                bg_height = len(recent_messages) * message_height + self.padding * 2
                bg_surface = pygame.Surface((self.chat_width, bg_height), pygame.SRCALPHA)
                bg_surface.fill((0, 0, 0, 120))  # More transparent than the full UI
                self.screen.blit(bg_surface, (self.chat_x, self.screen.get_height() - bg_height - self.padding))
                
                # Draw messages
                message_y = self.screen.get_height() - bg_height - self.padding + self.padding
                
                for player_name, message in recent_messages:
                    # Determine player name color
                    if player_name in self.player_name_colors:
                        name_color = self.player_name_colors[player_name]
                    else:
                        # Generate a color based on the player name
                        name_hash = sum(ord(c) for c in player_name)
                        r = (name_hash * 123) % 128 + 128  # 128-255
                        g = (name_hash * 456) % 128 + 128  # 128-255
                        b = (name_hash * 789) % 128 + 128  # 128-255
                        name_color = (r, g, b)
                        self.player_name_colors[player_name] = name_color

                    # Render player name
                    if player_name:
                        name_text = f"{player_name}: "
                        name_surface = self.message_font.render(name_text, True, name_color)
                        name_width = name_surface.get_width()
                        self.screen.blit(name_surface, (self.chat_x + self.padding, message_y))
                    else:
                        name_width = 0

                    # Render message
                    message_surface = self.message_font.render(message, True, self.text_color)
                    self.screen.blit(
                        message_surface, 
                        (self.chat_x + self.padding + name_width, message_y)
                    )

                    # Update message position
                    message_y += message_surface.get_height() + 2
