# PokeTogether

Ein 2D-Pokémon-Klon mit Online-Funktionalität, entwickelt mit Python und Pygame.

## Projektübersicht

Dieses Projekt ist eine Rekreation des klassischen Pokémon Rot-Spiels mit zusätzlichen Online-Funktionen. Es verwendet:

- **Python** mit **Pygame** für den Client
- **FastAPI/Flask** für das Backend
- **WebSockets** für Echtzeit-Kommunikation

## Einrichtung der Entwicklungsumgebung

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python-Paketmanager)

### Installation

1. Klone das Repository:
   ```
   git clone https://github.com/yourusername/PokeTogether.git
   cd PokeTogether
   ```

2. Führe das Setup-Skript aus:
   ```
   python setup_dev_environment.py
   ```

3. Aktiviere die virtuelle Umgebung:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

## MCP-Tools

Dieses Projekt verwendet Model Context Protocol (MCP) Tools, um die Entwicklung zu erleichtern. Die folgenden MCP-Server sind konfiguriert:

### PokeTogether-Helper

Ein allgemeiner MCP-Server für das Projekt.

### GameDev-Tools

Ein spezieller MCP-Server für die Spieleentwicklung mit folgenden Tools:

- `create_project_structure`: Erstellt die grundlegende Projektstruktur
- `generate_tilemap`: Generiert eine einfache Tilemap für das Spiel
- `create_sprite_sheet`: Erstellt ein Sprite-Sheet aus einzelnen Sprite-Dateien
- `setup_pygame`: Richtet Pygame für das Projekt ein

### AssetManager

Ein MCP-Server für die Verwaltung von Spiel-Assets.

## Projektstruktur

```
PokeTogether/
├── assets/
│   ├── sprites/
│   ├── maps/
│   └── audio/
├── src/
│   ├── game/
│   │   ├── core/
│   │   ├── entities/
│   │   ├── maps/
│   │   ├── ui/
│   │   ├── battle/
│   │   ├── items/
│   │   └── pokemon/
│   └── main.py
├── docs/
├── .cursor/
│   └── mcp.json
├── gamedev_mcp_server/
├── setup_dev_environment.py
└── README.md
```

## Entwicklung

1. Starte das Spiel:
   ```
   python src/main.py
   ```

2. Verwende die MCP-Tools für die Entwicklung:
   ```
   # Beispiel: Erstelle die Projektstruktur
   python -m gamedev_mcp_server create_project_structure
   ```

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die LICENSE-Datei für Details.
