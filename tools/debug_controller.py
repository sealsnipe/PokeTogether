#!/usr/bin/env python
"""
Debug Controller - Ein Programm zum Debuggen der Controller-Eingaben
"""

import pygame
import sys
import os
import time

def main():
    """Hauptfunktion"""
    print("Controller-Debug")
    print("Drücke Tasten auf dem Controller, um sie zu testen")
    print("Drücke ESC, um zu beenden")
    
    # Pygame initialisieren
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Controller-Debug")
    clock = pygame.time.Clock()
    
    # Controller initialisieren
    pygame.joystick.init()
    controllers = []
    
    for i in range(pygame.joystick.get_count()):
        controller = pygame.joystick.Joystick(i)
        controller.init()
        controllers.append(controller)
        print(f"Controller gefunden: {controller.get_name()}")
    
    if not controllers:
        print("Kein Controller gefunden")
        return 1
    
    # Font für Text
    font = pygame.font.SysFont(None, 24)
    
    # Hauptschleife
    running = True
    while running:
        # Zeit messen
        dt = clock.tick(60) / 1000.0
        
        # Events verarbeiten
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"Controller {event.joy}, Button {event.button} gedrückt")
            elif event.type == pygame.JOYBUTTONUP:
                print(f"Controller {event.joy}, Button {event.button} losgelassen")
            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.5:
                    print(f"Controller {event.joy}, Achse {event.axis}: {event.value:.2f}")
            elif event.type == pygame.JOYHATMOTION:
                if event.value != (0, 0):
                    print(f"Controller {event.joy}, Hat {event.hat}: {event.value}")
        
        # Bildschirm löschen
        screen.fill((0, 0, 0))
        
        # Controller-Informationen anzeigen
        y_pos = 10
        for i, controller in enumerate(controllers):
            # Controller-Name
            controller_name = font.render(f"Controller {i}: {controller.get_name()}", True, (255, 255, 255))
            screen.blit(controller_name, (10, y_pos))
            y_pos += 30
            
            # Buttons anzeigen
            for j in range(controller.get_numbuttons()):
                button_state = controller.get_button(j)
                color = (0, 255, 0) if button_state else (255, 0, 0)
                button_text = font.render(f"Button {j}: {button_state}", True, color)
                screen.blit(button_text, (10, y_pos))
                y_pos += 20
            
            # Achsen anzeigen
            for j in range(controller.get_numaxes()):
                axis_value = controller.get_axis(j)
                color = (0, 255, 0) if abs(axis_value) > 0.5 else (255, 255, 255)
                axis_text = font.render(f"Achse {j}: {axis_value:.2f}", True, color)
                screen.blit(axis_text, (200, 10 + j * 20))
            
            # Hats anzeigen
            for j in range(controller.get_numhats()):
                hat_value = controller.get_hat(j)
                color = (0, 255, 0) if hat_value != (0, 0) else (255, 255, 255)
                hat_text = font.render(f"Hat {j}: {hat_value}", True, color)
                screen.blit(hat_text, (400, 10 + j * 20))
        
        # Bildschirm aktualisieren
        pygame.display.flip()
    
    # Aufräumen
    pygame.quit()
    print("Debug beendet")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
