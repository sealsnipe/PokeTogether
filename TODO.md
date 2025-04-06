# PokeTogether TODO-Liste Überarbeitet

## 1. Multiplayer-Funktionalität
- [ ] Multiplayer-Refactoring abschließen und Verbindungsprobleme beheben
  - [ ] Server-Verbindungsprobleme beheben
  - [ ] Client-Verbindungsprobleme beheben
  - [ ] Automatisierte Tests zum Laufen bringen
- [x] Grundlegende Client-Server-Kommunikation implementieren
- [x] Spieler-Sichtbarkeit im Multiplayer-Modus implementieren
- [x] Bewegungsflüssigkeit im Multiplayer-Modus verbessern
- [x] Chat-Funktion implementieren (weitere Interaktionen folgen später)
- [x] Spielerposition-Synchronisierung verbessern (Issue #2 und #3)
  - [x] Problem beheben: Spieler synchronisieren sich erst bei Bewegung
  - [x] Problem beheben: Positionen sind nicht exakt gleich auf verschiedenen Clients
- [x] Multiplayer-Code refaktorisieren
  - [x] Multiplayer-Funktionalität in separate Klasse extrahieren
  - [x] Testbarkeit verbessern

## 2. Technische Verbesserungen
- [ ] Speichersystem optimieren
- [ ] Ladezeiten verbessern
- [ ] Fehlerbehandlung verbessern
- [ ] Logging-System verbessern
- [x] Automatisierte Tests erweitern
  - [x] Tests für Multiplayer-Funktionalität implementieren
  - [x] Screenshot-Funktion für Tests implementieren
  - [x] Eingabesimulation für Tests implementieren

## 3. UI/UX
- [ ] Hauptmenü verbessern
- [ ] Ingame-Menü verbessern
- [ ] Pokémon-Statusanzeige implementieren
- [ ] Trainer-Karte implementieren
- [ ] Pokédex implementieren

## 4. Spielwelt
- [ ] Karten-Editor implementieren
  - [ ] Tileset-Management (Import, Kategorisierung, Vorschau)
  - [ ] Layer-System (Boden, Objekte, Kollision, Events)
  - [ ] Werkzeuge (Pinsel, Füllen, Auswahl, Kopieren/Einfügen)
  - [ ] Event-Platzierung (Teleporter, NPCs, Items)
  - [ ] Speichern/Laden von Karten im eigenen Format
  - [ ] Exportieren von Karten für das Spiel
- [ ] Kartenmaterial sammeln
  - [ ] Bilder der Routen, Städte, Höhlen aus Pokémon Rot (4. Generation) von pokewiki.de sammeln
  - [ ] Nur hochauflösende, nicht-pixelige Bilder der 4. Generation verwenden
- [ ] Quest-System implementieren
  - [ ] Einfachen Quest-Log entwickeln (aufrufbar mit Y-Taste auf Controller oder entsprechende Taste auf Tastatur)
  - [ ] Tracking von aktiven Quests
  - [ ] Detailansicht für ausgewählte Quests
  - [ ] Eine Beispiel-Quest implementieren
  - [ ] Anmerkung: Belohnungssystem und weitere Quests werden später implementiert

## 5. Gameplay
- [ ] Pokémon-Datenbank implementieren
  - [ ] Research zu Pokémon-Werten und Eigenschaften
  - [ ] 10 Beispiel-Pokémon implementieren
  - [ ] Entscheidung: Datenbank vs. Dateisystem für Pokémon-Daten
- [ ] Kampfsystem implementieren
- [ ] Gras-Mechanik auf Routen implementieren
- [ ] Pokémon-Begegnung und Fang-Mechanik implementieren
- [ ] Inventar-System implementieren
- [ ] Pokémon-Center implementieren
- [ ] Pokémon-Entwicklung implementieren
- [ ] Pokémon-Markt implementieren
