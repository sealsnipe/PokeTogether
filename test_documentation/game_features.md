# PokeTogether - Spielfunktionen und Steuerung

Dieses Dokument beschreibt die verschiedenen Funktionen des PokeTogether-Spiels und wie sie gesteuert werden können. Es dient als Grundlage für die Entwicklung von automatisierten Tests.

## Steuerung

### Tastatur

| Aktion | Tasten |
|--------|--------|
| Bewegung | Pfeiltasten, WASD |
| Aktion/Bestätigen | Leertaste, Enter, Z |
| Abbrechen/Zurück | Escape, Backspace, X |
| Menü öffnen/schließen | Tab, M |
| Rennen | Shift |
| Vorspulen | F, Leertaste |

### Controller

| Aktion | Buttons/Achsen |
|--------|----------------|
| Bewegung | Linker Stick, D-Pad |
| Aktion/Bestätigen | A-Taste |
| Abbrechen/Zurück | B-Taste |
| Menü öffnen/schließen | Start-Taste, Back-Taste |
| Sekundäre Aktion | X-Taste |
| Tertiäre Aktion | Y-Taste |
| Rennen | RB-Taste (rechte Schultertaste) |
| Vorspulen | LB-Taste (linke Schultertaste) |
| Kamera steuern | Rechter Stick |

## Spielzustände und Menüs

### Hauptmenü

Das Hauptmenü ist der erste Bildschirm, der beim Starten des Spiels angezeigt wird. Es enthält folgende Optionen:

1. **New Game** - Startet ein neues Spiel
2. **Host Game** - Startet ein Spiel als Host (Multiplayer)
3. **Join Game** - Tritt einem Spiel bei (Multiplayer)
4. **Continue** - Setzt ein gespeichertes Spiel fort
5. **Options** - Öffnet das Optionsmenü
6. **Exit** - Beendet das Spiel

**Navigation:**
- Hoch/Runter: Wechselt zwischen den Optionen
- Aktion/Bestätigen: Wählt die markierte Option aus

### Ingame-Menü

Das Ingame-Menü kann während des Spiels mit der Menü-Taste (Tab/M oder Start-Taste am Controller) geöffnet werden. Es enthält folgende Optionen:

1. **POKEMON** - Zeigt die Pokémon des Spielers an
2. **BAG** - Zeigt den Inventarbeutel an
3. **PLAYER** - Zeigt Informationen über den Spieler an
4. **SAVE** - Speichert das Spiel
5. **OPTIONS** - Öffnet das Optionsmenü
6. **MULTIPLAYER** - Öffnet das Multiplayer-Menü
7. **EXIT** - Schließt das Menü

**Navigation:**
- Hoch/Runter: Wechselt zwischen den Optionen
- Aktion/Bestätigen: Wählt die markierte Option aus
- Abbrechen/Zurück: Schließt das Menü

### Optionsmenü

Das Optionsmenü enthält verschiedene Einstellungsmöglichkeiten für das Spiel:

1. **Video** - Videoeinstellungen
   - Fullscreen: Ein/Aus
   - Resolution: Verschiedene Auflösungen (640x480, 800x600, 1024x768, 1280x720, 1366x768, 1920x1080)
   - VSync: Ein/Aus
   - FPS Limit: Verschiedene Werte

2. **Audio** - Audioeinstellungen
   - Master Volume: 0-100%
   - Music Volume: 0-100%
   - SFX Volume: 0-100%
   - Mute: Ein/Aus

3. **Gameplay** - Spieleinstellungen
   - Text Speed: Verschiedene Geschwindigkeiten
   - Battle Animations: Ein/Aus
   - Battle Style: Verschiedene Stile
   - Difficulty: Verschiedene Schwierigkeitsgrade
   - Run Speed: Verschiedene Geschwindigkeiten
   - Fast Forward Speed: Verschiedene Geschwindigkeiten

4. **Controls** - Steuerungseinstellungen
   - Keyboard Enabled: Ein/Aus
   - Controller Enabled: Ein/Aus
   - Controller ID: Verschiedene Werte

**Navigation:**
- Hoch/Runter: Wechselt zwischen den Optionen
- Aktion/Bestätigen: Wählt die markierte Option aus oder ändert den Wert
- Abbrechen/Zurück: Geht zurück zum vorherigen Menü oder schließt das Optionsmenü

### Spielwelt

In der Spielwelt kann der Spieler seinen Charakter bewegen und mit der Umgebung interagieren.

**Steuerung:**
- Bewegung: Bewegt den Spieler in die entsprechende Richtung
- Aktion/Bestätigen: Interagiert mit Objekten oder NPCs
- Rennen: Erhöht die Bewegungsgeschwindigkeit
- Menü öffnen: Öffnet das Ingame-Menü

## Testszenarien

Basierend auf den oben beschriebenen Funktionen können folgende Testszenarien entwickelt werden:

1. **Hauptmenü-Navigation** - Testet die Navigation im Hauptmenü
2. **Optionsmenü-Navigation** - Testet die Navigation im Optionsmenü
3. **Optionsänderungen** - Testet das Ändern verschiedener Optionen
4. **Spielerbewegung** - Testet die Bewegung des Spielers in der Spielwelt
5. **Ingame-Menü-Navigation** - Testet die Navigation im Ingame-Menü
6. **Speichern und Laden** - Testet das Speichern und Laden des Spiels
7. **Multiplayer-Funktionen** - Testet die Multiplayer-Funktionen des Spiels
