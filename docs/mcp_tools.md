# PokeTogether MCP-Tools

Dieses Dokument beschreibt die MCP-Tools (Model Context Protocol), die für die Entwicklung des PokeTogether-Projekts verwendet werden.

## Überblick

MCP-Tools sind spezielle Tools, die über das Model Context Protocol mit KI-Modellen kommunizieren können. Sie ermöglichen es, bestimmte Aufgaben zu automatisieren und die Entwicklung zu erleichtern.

## Konfiguration

Die MCP-Tools sind in der Datei `.cursor/mcp.json` konfiguriert:

```json
{
  "mcpServers": {
    "PokeTogether-Helper": {
      "command": "npx",
      "args": ["-y", "mcp-server"],
      "env": {
        "PROJECT_NAME": "PokeTogether",
        "GAME_TYPE": "2D-Pokemon"
      }
    },
    "GameDev-Tools": {
      "command": "python",
      "args": ["-m", "gamedev_mcp_server"]
    },
    "AssetManager": {
      "command": "npx",
      "args": ["-y", "asset-manager-mcp"]
    }
  }
}
```

## Verfügbare MCP-Server

### PokeTogether-Helper

Ein allgemeiner MCP-Server für das Projekt, der grundlegende Funktionen bereitstellt.

### GameDev-Tools

Ein spezieller MCP-Server für die Spieleentwicklung mit folgenden Tools:

- `create_project_structure`: Erstellt die grundlegende Projektstruktur
- `generate_tilemap`: Generiert eine einfache Tilemap für das Spiel
- `create_sprite_sheet`: Erstellt ein Sprite-Sheet aus einzelnen Sprite-Dateien
- `setup_pygame`: Richtet Pygame für das Projekt ein

### AssetManager

Ein MCP-Server für die Verwaltung von Spiel-Assets.

## Verwendung

Die MCP-Tools können über die Cursor-IDE verwendet werden. Sie werden automatisch geladen, wenn die IDE gestartet wird.

### Beispiel: Erstellen der Projektstruktur

```python
# Verwende das GameDev-Tools MCP
python -m gamedev_mcp_server create_project_structure
```

### Beispiel: Generieren einer Tilemap

```python
# Verwende das GameDev-Tools MCP
python -m gamedev_mcp_server generate_tilemap --width 20 --height 15 --tile_size 32
```

## Eigene MCP-Tools erstellen

Du kannst eigene MCP-Tools erstellen, indem du einen MCP-Server implementierst. Hier ist ein Beispiel:

```python
from mcp.server.fastmcp import FastMCP

# Erstelle den MCP-Server
server = FastMCP("My-Custom-Tool")

@server.tool()
def my_custom_function(param1: str, param2: int) -> str:
    """Meine benutzerdefinierte Funktion
    
    Args:
        param1: Erster Parameter
        param2: Zweiter Parameter
        
    Returns:
        str: Ergebnis der Funktion
    """
    # Implementiere die Funktion
    return f"Ergebnis: {param1} {param2}"

if __name__ == "__main__":
    server.run()
```

Dann kannst du den Server in der `.cursor/mcp.json`-Datei konfigurieren:

```json
{
  "mcpServers": {
    "My-Custom-Tool": {
      "command": "python",
      "args": ["-m", "my_custom_tool"]
    }
  }
}
```

## Weitere Informationen

Weitere Informationen zu MCP-Tools findest du in der [offiziellen Dokumentation](https://modelcontextprotocol.io/introduction).
