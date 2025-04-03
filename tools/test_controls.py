#!/usr/bin/env python
"""
Test Controls - Ein Testprogramm für die Steuerung
"""

import pygame
import sys
import logging
import logging.config
import time
import os

# Füge das Projektverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.game.core.input_handler import InputHandler
from src.game.entities.player import Player

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
    logger.info("Starte Steuerungstest")
    
    # Pygame initialisieren
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("PokeTogether - Steuerungstest")
    clock = pygame.time.Clock()
    
    # Input-Handler initialisieren
    input_handler = InputHandler()
    
    # Spieler initialisieren
    player = Player(400, 300, "Tester")
    
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
        
        # Bewegung basierend auf Input
        movement = input_handler.get_movement()
        
        # Eingaben loggen
        input_state = {}
        for action in input_handler.input_state:
            if input_handler.is_pressed(action):
                input_state[action] = True
        
        if input_state:
            logger.info(f"Eingaben: {input_state}, Bewegung: {movement}")
        
        # Alte Position speichern
        old_x, old_y = player.x, player.y
        
        # Spieler bewegen
        player.move(movement[0], movement[1])
        
        # Positionsänderung loggen
        if old_x != player.x or old_y != player.y:
            logger.info(f"Position: ({old_x}, {old_y}) -> ({player.x}, {player.y}), Änderung: ({player.x - old_x}, {player.y - old_y})")
        
        # Spieler aktualisieren
        player.update(dt)
        
        # Bildschirm löschen
        screen.fill((100, 200, 100))
        
        # Spieler rendern (einfaches Rechteck)
        pygame.draw.rect(screen, (255, 0, 0), (player.x, player.y, 32, 32))
        
        # Informationen anzeigen
        pos_text = font.render(f"Position: ({player.x}, {player.y})", True, (255, 255, 255))
        screen.blit(pos_text, (10, 10))
        
        dir_text = font.render(f"Richtung: {player.direction}", True, (255, 255, 255))
        screen.blit(dir_text, (10, 40))
        
        input_text = font.render(f"Eingaben: {input_state}", True, (255, 255, 255))
        screen.blit(input_text, (10, 70))
        
        movement_text = font.render(f"Bewegung: {movement}", True, (255, 255, 255))
        screen.blit(movement_text, (10, 100))
        
        # Verbleibende Zeit anzeigen
        remaining_time = int(test_duration - (time.time() - start_time))
        time_text = font.render(f"Verbleibende Zeit: {remaining_time} Sekunden", True, (255, 255, 255))
        screen.blit(time_text, (10, 130))
        
        # Steuerungshinweise anzeigen
        hint1_text = font.render("Steuerung: Pfeiltasten / WASD / Controller", True, (255, 255, 255))
        screen.blit(hint1_text, (10, 500))
        
        hint2_text = font.render("ESC zum Beenden", True, (255, 255, 255))
        screen.blit(hint2_text, (10, 530))
        
        # Bildschirm aktualisieren
        pygame.display.flip()
    
    # Aufräumen
    pygame.quit()
    logger.info("Steuerungstest beendet")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
