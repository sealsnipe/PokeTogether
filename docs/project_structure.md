# PokeTogether Projektstruktur

Dieses Dokument beschreibt die Struktur des PokeTogether-Projekts und erklärt, wo welche Dateien zu finden sind.

## Überblick

Das Projekt folgt einer modularen Struktur, bei der jede Funktion oder Klasse in einer eigenen Datei liegt. Dies macht den Code übersichtlicher und leichter zu warten.

## Hauptverzeichnisse

- `src/`: Enthält den gesamten Quellcode des Spiels
- `assets/`: Enthält alle Ressourcen wie Bilder, Sounds und Karten
- `tests/`: Enthält alle Testdateien
- `docs/`: Enthält die Dokumentation

## Quellcode-Struktur

Der Quellcode ist in verschiedene Module unterteilt, die jeweils einen bestimmten Aspekt des Spiels abdecken:

### Core-Modul (`src/game/core/`)

Enthält die Kernkomponenten des Spiels:

- `game.py`: Die Hauptspielklasse, die den Spielablauf steuert
- `camera.py`: Die Kameraklasse, die die Ansicht des Spielers verwaltet

### Entities-Modul (`src/game/entities/`)

Enthält alle Spielentitäten:

- `player.py`: Die Spielerklasse, die den Hauptcharakter repräsentiert
- Weitere Entitäten wie NPCs, Gegner, etc.

### Maps-Modul (`src/game/maps/`)

Enthält alles, was mit Karten zu tun hat:

- `tilemap.py`: Die Tilemap-Klasse, die die Spielwelt repräsentiert

### UI-Modul (`src/game/ui/`)

Enthält alle Benutzeroberflächen-Komponenten:

- Menüs, Dialoge, HUD, etc.

### Battle-Modul (`src/game/battle/`)

Enthält alle Kampfmechaniken:

- Kampfsystem, Angriffe, etc.

### Items-Modul (`src/game/items/`)

Enthält alle Items und Item-Funktionen:

- Verschiedene Items wie Tränke, Pokébälle, etc.

### Pokemon-Modul (`src/game/pokemon/`)

Enthält alle Pokémon-Klassen und -Funktionen:

- Pokémon-Klassen, Attacken, etc.

### Utils-Modul (`src/game/utils/`)

Enthält Hilfsfunktionen für das Spiel:

- Allgemeine Hilfsfunktionen, die von verschiedenen Modulen verwendet werden

### Network-Modul (`src/game/network/`)

Enthält alle Netzwerkfunktionen für den Online-Modus:

- Client-Server-Kommunikation, Multiplayer-Funktionen, etc.

## Assets-Struktur

Die Assets sind in verschiedene Kategorien unterteilt:

- `assets/sprites/`: Enthält alle Sprites (Charaktere, Pokémon, etc.)
- `assets/maps/`: Enthält alle Karten
- `assets/audio/`: Enthält alle Sounds und Musik

## Test-Struktur

Die Tests spiegeln die Struktur des Quellcodes wider:

- `tests/game/core/`: Tests für das Core-Modul
- `tests/game/entities/`: Tests für das Entities-Modul
- usw.

## Import-Regeln

Für Imports gelten folgende Regeln:

1. Verwende absolute Imports (z.B. `from src.game.core.game import Game`)
2. Importiere nur das, was du wirklich brauchst
3. Vermeide Wildcard-Imports (`from module import *`)
4. Organisiere Imports in der Reihenfolge: Standardbibliotheken, Drittanbieterbibliotheken, eigene Module

## Logging

Das Projekt verwendet das Python-Logging-System:

1. Jedes Modul hat seinen eigenen Logger (`logging.getLogger(__name__)`)
2. Die Logging-Konfiguration wird zentral in `logging.conf` definiert
3. Log-Level können pro Modul angepasst werden

## Dokumentation

Jede Datei, Klasse und Funktion sollte mit Docstrings dokumentiert werden:

1. Dateien: Kurze Beschreibung des Inhalts
2. Klassen: Beschreibung der Klasse und ihrer Verantwortlichkeiten
3. Funktionen: Beschreibung der Funktion, Parameter und Rückgabewerte
