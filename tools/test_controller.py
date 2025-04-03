#!/usr/bin/env python
"""
Test Controller - Ein Testprogramm für Controller-Eingaben
"""

import pygame
import sys
import logging
import logging.config
import time
import os
import json

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.game.core.input_handler import InputHandler

def setup_logging():
    """Richtet das Logging-System ein"""
    if os.path.exists('logging.conf'):
        logging.config.fileConfig('logging.conf')
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    return logging.getLogger(__name__)

def main():
    """Hauptfunktion"""
    logger = setup_logging()
    logger.info("Starte Controller-Test")
    
    # Pygame initialisieren
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("PokeTogether - Controller-Test")
    clock = pygame.time.Clock()
    
    # Input-Handler initialisieren
    input_handler = InputHandler()
    
    # Font für Text
    font = pygame.font.SysFont(None, 24)
    
    # Testdauer in Sekunden
    test_duration = 60
    start_time = time.time()
    
    # Hauptschleife
    running = True
    while running and time.time() - start_time < test_duration:
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
        
        # Input-Handler aktualisieren
        input_handler.handle_events(events)
        input_handler.update()
        
        # Controller-Debug-Informationen abrufen
        controller_debug = {}
        if input_handler.controllers:
            controller_debug = input_handler.debug_controller(0)
        
        # Eingaben loggen
        input_state = {}
        for action in input_handler.input_state:
            if input_handler.is_pressed(action):
                input_state[action] = True
        
        if input_state:
            logger.info(f"Eingaben: {input_state}")
            
        # Bewegung basierend auf Input
        movement = input_handler.get_movement()
        if movement[0] != 0 or movement[1] != 0:
            logger.info(f"Bewegung: {movement}")
        
        # Bildschirm löschen
        screen.fill((0, 0, 0))
        
        # Informationen anzeigen
        y_pos = 10
        
        # Controller-Informationen anzeigen
        if input_handler.controllers:
            controller_name = font.render(f"Controller: {controller_debug.get('name', 'Unbekannt')}", True, (255, 255, 255))
            screen.blit(controller_name, (10, y_pos))
            y_pos += 30
            
            # Buttons anzeigen
            buttons = controller_debug.get('buttons', {})
            button_text = font.render(f"Buttons: {json.dumps(buttons)}", True, (255, 255, 255))
            screen.blit(button_text, (10, y_pos))
            y_pos += 30
            
            # Achsen anzeigen
            axes = controller_debug.get('axes', {})
            for axis_name, axis_value in axes.items():
                axis_text = font.render(f"{axis_name}: {axis_value:.2f}", True, (255, 255, 255))
                screen.blit(axis_text, (10, y_pos))
                y_pos += 20
                
            # Hats anzeigen
            hats = controller_debug.get('hats', {})
            hat_text = font.render(f"Hats: {json.dumps(hats)}", True, (255, 255, 255))
            screen.blit(hat_text, (10, y_pos))
            y_pos += 30
        else:
            no_controller = font.render("Kein Controller gefunden", True, (255, 255, 255))
            screen.blit(no_controller, (10, y_pos))
            y_pos += 30
            
        # Eingaben anzeigen
        input_text = font.render(f"Eingaben: {input_state}", True, (255, 255, 255))
        screen.blit(input_text, (10, y_pos))
        y_pos += 30
        
        # Bewegung anzeigen
        movement_text = font.render(f"Bewegung: {movement}", True, (255, 255, 255))
        screen.blit(movement_text, (10, y_pos))
        y_pos += 30
        
        # Verbleibende Zeit anzeigen
        remaining_time = int(test_duration - (time.time() - start_time))
        time_text = font.render(f"Verbleibende Zeit: {remaining_time} Sekunden", True, (255, 255, 255))
        screen.blit(time_text, (10, y_pos))
        y_pos += 30
        
        # Steuerungshinweise anzeigen
        hint1_text = font.render("Drücke Tasten auf dem Controller, um sie zu testen", True, (255, 255, 255))
        screen.blit(hint1_text, (10, 500))
        
        hint2_text = font.render("ESC zum Beenden", True, (255, 255, 255))
        screen.blit(hint2_text, (10, 530))
        
        # Bildschirm aktualisieren
        pygame.display.flip()
    
    # Aufräumen
    pygame.quit()
    logger.info("Controller-Test beendet")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
