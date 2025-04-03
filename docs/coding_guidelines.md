# PokeTogether Codierungsrichtlinien

Dieses Dokument beschreibt die Codierungsrichtlinien für das PokeTogether-Projekt.

## Grundprinzipien

### Clean Code

- **DRY (Don't Repeat Yourself)**: Vermeide Wiederholungen im Code. Extrahiere wiederholten Code in Funktionen oder Klassen.
- **KISS (Keep It Simple, Stupid)**: Halte den Code so einfach wie möglich. Komplexität sollte nur eingeführt werden, wenn sie notwendig ist.
- **SRP (Single Responsibility Principle)**: Jede Funktion oder Klasse sollte nur eine Verantwortung haben.

### Modularisierung

- **Eine Funktion pro Datei**: Jede Funktion oder Klasse sollte in einer eigenen Datei liegen.
- **Klare Verzeichnisstruktur**: Die Verzeichnisstruktur sollte die logische Struktur des Projekts widerspiegeln.

## Formatierung

- **PEP 8**: Folge den PEP 8-Richtlinien für Python-Code.
- **Einrückung**: Verwende 4 Leerzeichen für die Einrückung.
- **Zeilenlänge**: Beschränke die Zeilenlänge auf 79 Zeichen.
- **Leerzeilen**: Verwende Leerzeilen, um den Code zu strukturieren.

## Benennung

- **Variablen und Funktionen**: Verwende `snake_case` für Variablen und Funktionen.
- **Klassen**: Verwende `PascalCase` für Klassen.
- **Konstanten**: Verwende `UPPER_CASE` für Konstanten.
- **Private Attribute**: Verwende einen führenden Unterstrich für private Attribute (`_private_var`).

## Dokumentation

- **Docstrings**: Jede Datei, Klasse und Funktion sollte mit Docstrings dokumentiert werden.
- **Kommentare**: Verwende Kommentare, um komplexe Teile des Codes zu erklären.
- **Typ-Annotationen**: Verwende Typ-Annotationen, um die Typen von Parametern und Rückgabewerten anzugeben.

## Logging

- **Logger pro Modul**: Jedes Modul sollte seinen eigenen Logger haben.
- **Log-Level**: Verwende die richtigen Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- **Aussagekräftige Meldungen**: Log-Meldungen sollten aussagekräftig sein und relevante Informationen enthalten.

## Fehlerbehandlung

- **Exceptions**: Fange nur die Exceptions, die du behandeln kannst.
- **Spezifische Exceptions**: Fange spezifische Exceptions statt allgemeiner Exceptions.
- **Logging**: Logge Exceptions mit Stacktrace.

## Tests

- **Testabdeckung**: Jede Funktion oder Klasse sollte getestet werden.
- **Teststruktur**: Tests sollten die Struktur des Quellcodes widerspiegeln.
- **Testbenennung**: Testnamen sollten beschreiben, was getestet wird.

## Git-Workflow

- **Branches**: Verwende Feature-Branches für neue Funktionen.
- **Commit-Nachrichten**: Schreibe aussagekräftige Commit-Nachrichten.
- **Pull Requests**: Verwende Pull Requests für Code-Reviews.

## Import-Regeln

- **Absolute Imports**: Verwende absolute Imports (z.B. `from src.game.core.game import Game`).
- **Spezifische Imports**: Importiere nur das, was du wirklich brauchst.
- **Import-Reihenfolge**: Organisiere Imports in der Reihenfolge: Standardbibliotheken, Drittanbieterbibliotheken, eigene Module.

## Beispiel

```python
#!/usr/bin/env python
"""
Example module - Demonstrates coding guidelines
"""

import logging
from typing import List, Dict, Any

class ExampleClass:
    """Example class demonstrating coding guidelines"""
    
    def __init__(self, name: str):
        """Initialize the example class
        
        Args:
            name: Name of the example
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Creating example '{name}'")
        
        self.name = name
        self._private_var = 0
        
    def example_method(self, value: int) -> str:
        """Example method demonstrating coding guidelines
        
        Args:
            value: Example value
            
        Returns:
            str: Result of the method
        """
        self.logger.debug(f"Called example_method with value {value}")
        
        try:
            result = f"{self.name}: {value + self._private_var}"
            return result
        except Exception as e:
            self.logger.error(f"Error in example_method: {e}", exc_info=True)
            raise
```
