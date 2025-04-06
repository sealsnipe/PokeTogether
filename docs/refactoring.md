# Refactoring-Dokumentation

## Übersicht

Dieses Dokument beschreibt die Änderungen, die im Rahmen des Refactorings des PokeTogether-Spiels vorgenommen wurden. Das Ziel des Refactorings war es, den Code besser zu strukturieren, Verantwortlichkeiten klarer zu trennen und die Wartbarkeit zu verbessern.

## Neue Struktur

Die neue Struktur besteht aus mehreren spezialisierten Klassen, die jeweils für einen bestimmten Aspekt des Spiels verantwortlich sind:

1. **GameStateManager**: Verwaltet die verschiedenen Spielzustände und Übergänge zwischen ihnen.
2. **RenderManager**: Verwaltet das Rendern der verschiedenen Spielzustände.
3. **InputManager**: Verwaltet die Eingaben des Spielers.
4. **Game**: Koordiniert die anderen Manager und den Hauptspielablauf.

## Detaillierte Änderungen

### 1. GameStateManager

Die `GameStateManager`-Klasse ist für die Verwaltung der verschiedenen Spielzustände verantwortlich. Sie bietet folgende Funktionalitäten:

- Verwaltung des aktuellen und vorherigen Spielzustands
- Wechsel zwischen verschiedenen Spielzuständen
- Speicherung von zustandsspezifischen Daten
- Verwaltung von Callbacks für Zustandsänderungen
- Verwaltung des Eingabedialogs

Die Spielzustände werden als Enum-Werte definiert, was die Lesbarkeit verbessert und Tippfehler verhindert.

### 2. RenderManager

Die `RenderManager`-Klasse ist für das Rendern der verschiedenen Spielzustände verantwortlich. Sie bietet folgende Funktionalitäten:

- Registrierung von Render-Funktionen für verschiedene Spielzustände
- Rendern des aktuellen Spielzustands
- Anzeige von Debug-Informationen
- Anzeige der FPS
- Hilfsfunktionen zum Rendern von Text, Rechtecken und anderen UI-Elementen

### 3. InputManager

Die `InputManager`-Klasse ist eine verbesserte Version der `InputHandler`-Klasse. Sie bietet folgende Funktionalitäten:

- Verwaltung von Tastatur- und Controller-Eingaben
- Registrierung von Callbacks für Eingabeaktionen
- Prüfung, ob eine Aktion gedrückt, gerade gedrückt oder gerade losgelassen wurde
- Zurücksetzen des Eingabezustands

Die Eingabeaktionen werden als Enum-Werte definiert, was die Lesbarkeit verbessert und Tippfehler verhindert.

### 4. Game

Die `Game`-Klasse wurde überarbeitet, um die anderen Manager zu verwenden und den Hauptspielablauf zu koordinieren. Sie bietet folgende Funktionalitäten:

- Initialisierung der Manager und des Spiels
- Verarbeitung von Pygame-Events
- Aktualisierung des Spielzustands
- Rendern des Spiels
- Verwaltung der Multiplayer-Funktionalität
- Verwaltung der automatisierten Tests

## Vorteile der neuen Struktur

Die neue Struktur bietet mehrere Vorteile:

1. **Bessere Trennung der Verantwortlichkeiten**: Jede Klasse ist für einen bestimmten Aspekt des Spiels verantwortlich, was die Wartbarkeit verbessert.
2. **Verbesserte Lesbarkeit**: Der Code ist besser strukturiert und leichter zu verstehen.
3. **Einfachere Erweiterbarkeit**: Neue Funktionalitäten können leichter hinzugefügt werden, ohne den bestehenden Code zu ändern.
4. **Bessere Testbarkeit**: Die einzelnen Komponenten können unabhängig voneinander getestet werden.
5. **Reduzierte Komplexität**: Die einzelnen Klassen sind weniger komplex und leichter zu verstehen.

## Verwendung der neuen Struktur

Um die neue Struktur zu verwenden, müssen folgende Dateien importiert werden:

```python
from game.core.game_state_manager import GameStateManager, GameState
from game.core.render_manager import RenderManager
from game.core.input_manager import InputManager, InputAction
from game.core.game_refactored import Game
```

Die `main_refactored.py`-Datei zeigt, wie die neue Struktur verwendet werden kann.

## Nächste Schritte

Obwohl das Refactoring bereits viele Verbesserungen gebracht hat, gibt es noch weitere Möglichkeiten zur Verbesserung:

1. **Weitere Aufteilung der Game-Klasse**: Die `Game`-Klasse könnte weiter aufgeteilt werden, um die Verantwortlichkeiten noch klarer zu trennen.
2. **Verbesserung der Multiplayer-Funktionalität**: Die Multiplayer-Funktionalität könnte in eine eigene Klasse ausgelagert werden.
3. **Verbesserung der Fehlerbehandlung**: Die Fehlerbehandlung könnte verbessert werden, um robustere Fehlerbehandlung zu gewährleisten.
4. **Verbesserung der Dokumentation**: Die Dokumentation könnte weiter verbessert werden, um die Verwendung der neuen Struktur zu erleichtern.
5. **Verbesserung der Tests**: Es könnten Tests für die einzelnen Komponenten erstellt werden, um die Qualität des Codes zu verbessern.

## Fazit

Das Refactoring hat die Struktur des PokeTogether-Spiels deutlich verbessert. Die neue Struktur ist besser organisiert, leichter zu verstehen und einfacher zu erweitern. Die Trennung der Verantwortlichkeiten erleichtert die Wartung und Erweiterung des Spiels.
