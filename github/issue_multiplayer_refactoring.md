# Multiplayer-Refactoring

## Beschreibung

Die Multiplayer-Funktionalität wurde aus der `Game`-Klasse in eine separate Klasse `GameMultiplayer` extrahiert, um die Wartbarkeit und Erweiterbarkeit des Codes zu verbessern. Außerdem wurden Testfunktionen implementiert, um die Multiplayer-Funktionalität besser testen zu können.

## Änderungen

- Extraktion der Multiplayer-Funktionalität in eine separate Klasse `GameMultiplayer`
- Anpassung der `Game`-Klasse, um die neue `GameMultiplayer`-Klasse zu verwenden
- Implementierung von Testfunktionen (Screenshot, Eingabesimulation)
- Verbesserung des Servers
- Implementierung von Testskripten für die Multiplayer-Funktionalität

## Testergebnisse

Die Tests zeigen, dass die grundlegende Multiplayer-Funktionalität funktioniert, aber es gibt noch Verbesserungspotenzial bei der Synchronisierung der Spielerpositionen.

## Screenshots

Die Screenshots der Tests befinden sich im Verzeichnis `test_screenshots`.

## Nächste Schritte

- Verbesserung der Spielerposition-Synchronisierung
- Implementierung weiterer Multiplayer-Funktionen (z.B. Spieler-Interaktionen)
- Verbesserung der Testabdeckung
- Optimierung der Netzwerkleistung
