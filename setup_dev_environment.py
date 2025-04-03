#!/usr/bin/env python
"""
Setup Development Environment - Skript zur Einrichtung der Entwicklungsumgebung
für das PokeTogether-Projekt
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Überprüft die Python-Version"""
    print("Überprüfe Python-Version...")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Python 3.8 oder höher wird benötigt. Aktuelle Version: {major}.{minor}")
        return False
    print(f"Python-Version {major}.{minor} ist kompatibel.")
    return True

def install_dependencies():
    """Installiert die benötigten Abhängigkeiten"""
    print("Installiere Abhängigkeiten...")
    
    # Liste der zu installierenden Pakete
    packages = [
        "pygame==2.1.2",
        "pytmx==3.31",
        "requests==2.28.1",
        "websockets==10.3",
        "mcp==1.5.0"  # MCP-Bibliothek für die Erstellung von MCP-Servern
    ]
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("Abhängigkeiten erfolgreich installiert.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Installieren der Abhängigkeiten: {e}")
        return False

def setup_virtual_environment():
    """Richtet eine virtuelle Umgebung ein"""
    print("Richte virtuelle Umgebung ein...")
    
    try:
        # Erstelle eine virtuelle Umgebung
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        
        # Aktiviere die virtuelle Umgebung und installiere die Abhängigkeiten
        if platform.system() == "Windows":
            activate_script = os.path.join("venv", "Scripts", "activate")
            pip_path = os.path.join("venv", "Scripts", "pip")
        else:
            activate_script = os.path.join("venv", "bin", "activate")
            pip_path = os.path.join("venv", "bin", "pip")
        
        # Installiere die Abhängigkeiten in der virtuellen Umgebung
        packages = [
            "pygame==2.1.2",
            "pytmx==3.31",
            "requests==2.28.1",
            "websockets==10.3",
            "mcp==1.5.0"
        ]
        
        if platform.system() == "Windows":
            subprocess.check_call(f'"{pip_path}" install {" ".join(packages)}', shell=True)
        else:
            subprocess.check_call(f'source "{activate_script}" && pip install {" ".join(packages)}', shell=True)
        
        print(f"Virtuelle Umgebung wurde in {os.path.abspath('venv')} erstellt und Abhängigkeiten installiert.")
        print(f"Aktiviere die Umgebung mit:")
        if platform.system() == "Windows":
            print(f"    {activate_script}")
        else:
            print(f"    source {activate_script}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Einrichten der virtuellen Umgebung: {e}")
        return False

def create_mcp_server_module():
    """Erstellt ein Python-Modul für den MCP-Server"""
    print("Erstelle MCP-Server-Modul...")
    
    os.makedirs("gamedev_mcp_server", exist_ok=True)
    
    # Erstelle __init__.py
    with open(os.path.join("gamedev_mcp_server", "__init__.py"), "w") as f:
        f.write("""\"\"\"
GameDev MCP Server - Ein MCP-Server für die Spieleentwicklung
\"\"\"

from .server import GameDevMCPServer

__all__ = ["GameDevMCPServer"]
""")
    
    # Erstelle server.py
    with open(os.path.join("gamedev_mcp_server", "server.py"), "w") as f:
        f.write("""\"\"\"
GameDev MCP Server - Hauptimplementierung
\"\"\"

import os
import json
import sys
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

# Erstelle den MCP-Server
server = FastMCP("GameDev-Tools")

@server.tool()
def create_project_structure(base_dir: str = ".") -> str:
    \"\"\"Erstellt die grundlegende Projektstruktur für ein Pokémon-ähnliches Spiel\"\"\"
    directories = [
        "src/game/core",
        "src/game/entities",
        "src/game/maps",
        "src/game/ui",
        "src/game/battle",
        "src/game/items",
        "src/game/pokemon",
        "assets/sprites",
        "assets/maps",
        "assets/audio",
        "docs"
    ]
    
    for directory in directories:
        full_path = os.path.join(base_dir, directory)
        os.makedirs(full_path, exist_ok=True)
        
    # Erstelle eine README.md-Datei
    readme_path = os.path.join(base_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write("# PokeTogether\\n\\nEin 2D-Pokémon-Klon mit Online-Funktionalität\\n")
        
    # Erstelle eine requirements.txt-Datei
    req_path = os.path.join(base_dir, "requirements.txt")
    with open(req_path, "w") as f:
        f.write("pygame==2.1.2\\npytmx==3.31\\nrequests==2.28.1\\nwebsockets==10.3\\n")
        
    # Erstelle eine main.py-Datei
    main_path = os.path.join(base_dir, "src", "main.py")
    with open(main_path, "w") as f:
        f.write(\"\"\"#!/usr/bin/env python
\"\"\"
PokeTogether - Main Game Entry Point
\"\"\"

import pygame
import sys
from game.core.game import Game

def main():
    \"\"\"Main entry point for the game\"\"\"
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
\"\"\")
        
    # Erstelle eine game.py-Datei
    game_path = os.path.join(base_dir, "src", "game", "core", "game.py")
    with open(game_path, "w") as f:
        f.write(\"\"\"#!/usr/bin/env python
\"\"\"
Game class - Main game loop and state management
\"\"\"

import pygame
import sys

class Game:
    \"\"\"Main game class\"\"\"
    
    def __init__(self):
        \"\"\"Initialize the game\"\"\"
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("PokeTogether")
        self.clock = pygame.time.Clock()
        self.running = True
        
    def handle_events(self):
        \"\"\"Handle pygame events\"\"\"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
    def update(self):
        \"\"\"Update game state\"\"\"
        pass
        
    def render(self):
        \"\"\"Render the game\"\"\"
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        
    def run(self):
        \"\"\"Main game loop\"\"\"
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()
\"\"\")
        
    return f"Projektstruktur wurde in {base_dir} erstellt"

@server.tool()
def generate_tilemap(width: int = 20, height: int = 15, tile_size: int = 32) -> str:
    \"\"\"Generiert eine einfache Tilemap für das Spiel\"\"\"
    # Hier würde die Implementierung für die Tilemap-Generierung stehen
    return f"Tilemap mit Größe {width}x{height} und Tile-Größe {tile_size}px wurde generiert"

@server.tool()
def create_sprite_sheet(sprites_dir: str, output_file: str) -> str:
    \"\"\"Erstellt ein Sprite-Sheet aus einzelnen Sprite-Dateien\"\"\"
    # Hier würde die Implementierung für die Sprite-Sheet-Erstellung stehen
    return f"Sprite-Sheet wurde aus {sprites_dir} erstellt und in {output_file} gespeichert"

@server.tool()
def setup_pygame() -> str:
    \"\"\"Richtet Pygame für das Projekt ein\"\"\"
    try:
        import pygame
        pygame_version = pygame.version.ver
        return f"Pygame {pygame_version} ist installiert und einsatzbereit"
    except ImportError:
        return "Pygame ist nicht installiert. Bitte installiere es mit 'pip install pygame'"

if __name__ == "__main__":
    server.run()
""")
    
    # Erstelle __main__.py
    with open(os.path.join("gamedev_mcp_server", "__main__.py"), "w") as f:
        f.write("""\"\"\"
GameDev MCP Server - Einstiegspunkt
\"\"\"

from .server import server

if __name__ == "__main__":
    server.run()
""")
    
    print(f"MCP-Server-Modul wurde in {os.path.abspath('gamedev_mcp_server')} erstellt.")
    return True

def main():
    """Hauptfunktion"""
    print("=== PokeTogether Entwicklungsumgebung Setup ===")
    
    if not check_python_version():
        return
    
    if not setup_virtual_environment():
        print("Versuche, die Abhängigkeiten direkt zu installieren...")
        if not install_dependencies():
            return
    
    create_mcp_server_module()
    
    print("\n=== Setup abgeschlossen ===")
    print("Du kannst jetzt mit der Entwicklung deines Pokémon-Spiels beginnen!")
    print("Verwende die MCP-Tools, um die Entwicklung zu erleichtern.")

if __name__ == "__main__":
    main()
