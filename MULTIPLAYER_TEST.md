# PokeTogether Multiplayer-Test

Diese Anleitung erklärt, wie du PokeTogether installierst und den Multiplayer-Modus testest.

## Installation

1. Stelle sicher, dass Python 3.8 oder höher installiert ist
2. Klone das Repository oder lade es als ZIP-Datei herunter
3. Öffne eine Kommandozeile im Projektverzeichnis
4. Installiere die erforderlichen Pakete:
   ```
   pip install -r requirements.txt
   ```

## Spiel starten

Führe das Spiel mit folgendem Befehl aus:
```
python src/main.py
```

Oder doppelklicke auf die Datei `start_game.bat` (nur Windows).

## Multiplayer-Modus testen

### Als Host (Server)

1. Starte das Spiel und wähle "New Game"
2. Drücke Enter/Start, um das Ingame-Menü zu öffnen
3. Wähle "MULTIPLAYER"
4. Wähle "HOST GAME", um eine Multiplayer-Session zu starten
5. Teile deine IP-Adresse mit anderen Spielern (siehe unten)

### Als Client

1. Starte das Spiel und wähle "New Game"
2. Drücke Enter/Start, um das Ingame-Menü zu öffnen
3. Wähle "MULTIPLAYER"
4. Wähle "JOIN GAME", um einer Multiplayer-Session beizutreten
5. Gib die IP-Adresse des Hosts ein (standardmäßig wird "localhost" verwendet)

### IP-Adresse herausfinden (für den Host)

Öffne eine Kommandozeile und gib ein:
- Windows: `ipconfig`
- Mac/Linux: `ifconfig` oder `ip addr`

Suche nach der IPv4-Adresse deines LAN-Adapters (in der Regel beginnt sie mit 192.168.x.x).

## Steuerung

- **Pfeiltasten/D-Pad**: Bewegen
- **Enter/A-Taste**: Bestätigen
- **Escape/B-Taste**: Zurück/Menü schließen
- **Shift/RB-Taste**: Rennen
- **F/Leertaste/LB-Taste**: Vorspulen
- **Enter/Start-Taste**: Ingame-Menü öffnen

## Fehlerbehebung

- **Verbindungsprobleme**: Stelle sicher, dass keine Firewall den Port 8765 blockiert
- **Spiel startet nicht**: Überprüfe, ob alle erforderlichen Pakete installiert sind
- **Steuerung funktioniert nicht**: Überprüfe, ob ein Controller angeschlossen ist
