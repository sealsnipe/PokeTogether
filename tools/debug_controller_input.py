#!/usr/bin/env python
"""
Debug Controller Input - Testet die Controller-Eingaben
"""

import pygame
import sys
import os
import logging

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.game.core.controller_constants import *

def main():
    """Hauptfunktion"""
    # Pygame initialisieren
    pygame.init()
    
    # Bildschirm erstellen
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Controller Input Test")
    
    # Font initialisieren
    font = pygame.font.SysFont(None, 24)
    
    # Controller initialisieren
    pygame.joystick.init()
    controllers = []
    
    for i in range(pygame.joystick.get_count()):
        controller = pygame.joystick.Joystick(i)
        controller.init()
        controllers.append(controller)
        print(f"Controller gefunden: {controller.get_name()}")
    
    if not controllers:
        print("Kein Controller gefunden!")
        return
    
    # Hauptschleife
    running = True
    while running:
        # Events verarbeiten
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Bildschirm leeren
        screen.fill((0, 0, 0))
        
        # Controller-Status anzeigen
        y = 10
        for i, controller in enumerate(controllers):
            # Controller-Name
            text = font.render(f"Controller {i}: {controller.get_name()}", True, (255, 255, 255))
            screen.blit(text, (10, y))
            y += 30
            
            # Buttons
            text = font.render("Buttons:", True, (255, 255, 255))
            screen.blit(text, (10, y))
            y += 20
            
            button_names = {
                BUTTON_A: "A",
                BUTTON_B: "B",
                BUTTON_X: "X",
                BUTTON_Y: "Y",
                BUTTON_BACK: "Back",
                BUTTON_START: "Start",
                BUTTON_LEFTSTICK: "Left Stick",
                BUTTON_RIGHTSTICK: "Right Stick",
                BUTTON_LEFTSHOULDER: "LB",
                BUTTON_RIGHTSHOULDER: "RB",
                BUTTON_DPAD_UP: "D-Pad Up",
                BUTTON_DPAD_DOWN: "D-Pad Down",
                BUTTON_DPAD_LEFT: "D-Pad Left",
                BUTTON_DPAD_RIGHT: "D-Pad Right",
                BUTTON_GUIDE: "Guide"
            }
            
            for button_id, button_name in button_names.items():
                try:
                    button_state = controller.get_button(button_id)
                    color = (0, 255, 0) if button_state else (255, 0, 0)
                    text = font.render(f"{button_name}: {button_state}", True, color)
                    screen.blit(text, (10, y))
                    y += 20
                except pygame.error:
                    pass
            
            # Achsen
            text = font.render("Achsen:", True, (255, 255, 255))
            screen.blit(text, (10, y))
            y += 20
            
            axis_names = {
                AXIS_LEFTX: "Left X",
                AXIS_LEFTY: "Left Y",
                AXIS_RIGHTX: "Right X",
                AXIS_RIGHTY: "Right Y",
                AXIS_TRIGGERLEFT: "Left Trigger",
                AXIS_TRIGGERRIGHT: "Right Trigger"
            }
            
            for axis_id, axis_name in axis_names.items():
                try:
                    axis_value = controller.get_axis(axis_id)
                    color = (0, 255, 0) if abs(axis_value) > 0.5 else (255, 255, 255)
                    text = font.render(f"{axis_name}: {axis_value:.2f}", True, color)
                    screen.blit(text, (10, y))
                    y += 20
                except pygame.error:
                    pass
            
            # Hats
            text = font.render("Hats:", True, (255, 255, 255))
            screen.blit(text, (10, y))
            y += 20
            
            for hat_id in range(controller.get_numhats()):
                hat_value = controller.get_hat(hat_id)
                text = font.render(f"Hat {hat_id}: {hat_value}", True, (255, 255, 255))
                screen.blit(text, (10, y))
                y += 20
        
        # Bildschirm aktualisieren
        pygame.display.flip()
        
        # Framerate begrenzen
        pygame.time.delay(50)
    
    pygame.quit()

if __name__ == "__main__":
    main()
