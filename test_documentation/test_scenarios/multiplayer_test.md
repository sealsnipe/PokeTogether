# Multiplayer-Test

Dieser Test überprüft die Multiplayer-Funktionalität des Spiels auf einer einzelnen Maschine, indem zwei Spielinstanzen gestartet werden: eine als Host und eine als Client.

## Zu testende Funktionen

1. Starten einer Multiplayer-Session als Host
2. Verbinden mit einer Multiplayer-Session als Client
3. Synchronisation der Spielerpositionen zwischen Host und Client
4. Interaktion zwischen Spielern
5. Beenden der Multiplayer-Session

## Testaufbau

Für diesen Test benötigen wir zwei separate Instanzen des Spiels:
1. **Host-Instanz**: Startet eine Multiplayer-Session und fungiert als Server
2. **Client-Instanz**: Verbindet sich mit der Host-Instanz

## Testschritte

### Teil 1: Host-Instanz starten und Multiplayer-Session hosten

1. **Spiel starten**
   - Starte das Spiel und warte, bis das Hauptmenü angezeigt wird

2. **Host-Option auswählen**
   - Navigiere zur Option "Host Game" im Hauptmenü
   - Drücke die Taste "action" (Enter/Space/Z)
   - Überprüfe, ob die Multiplayer-Session gestartet wird
   - Notiere die IP-Adresse und den Port (standardmäßig 8765)

3. **Warten auf Client-Verbindung**
   - Warte, bis die Client-Instanz verbunden ist

### Teil 2: Client-Instanz starten und mit Host verbinden

1. **Zweite Spielinstanz starten**
   - Starte eine zweite Instanz des Spiels und warte, bis das Hauptmenü angezeigt wird

2. **Join-Option auswählen**
   - Navigiere zur Option "Join Game" im Hauptmenü
   - Drücke die Taste "action" (Enter/Space/Z)
   - Gib die IP-Adresse und den Port der Host-Instanz ein
   - Drücke die Taste "action", um die Verbindung herzustellen
   - Überprüfe, ob die Verbindung erfolgreich hergestellt wird

### Teil 3: Spieler-Interaktion testen

1. **Bewegung des Host-Spielers**
   - In der Host-Instanz, bewege den Spieler in verschiedene Richtungen
   - Überprüfe, ob die Bewegung in der Client-Instanz sichtbar ist

2. **Bewegung des Client-Spielers**
   - In der Client-Instanz, bewege den Spieler in verschiedene Richtungen
   - Überprüfe, ob die Bewegung in der Host-Instanz sichtbar ist

3. **Chat-Nachrichten (falls implementiert)**
   - Sende eine Chat-Nachricht von der Host-Instanz
   - Überprüfe, ob die Nachricht in der Client-Instanz angezeigt wird
   - Sende eine Chat-Nachricht von der Client-Instanz
   - Überprüfe, ob die Nachricht in der Host-Instanz angezeigt wird

### Teil 4: Multiplayer-Session beenden

1. **Client-Verbindung trennen**
   - In der Client-Instanz, öffne das Ingame-Menü
   - Navigiere zur Option "MULTIPLAYER"
   - Wähle "Disconnect" oder drücke die Taste "cancel"
   - Überprüfe, ob die Verbindung getrennt wird

2. **Host-Session beenden**
   - In der Host-Instanz, öffne das Ingame-Menü
   - Navigiere zur Option "MULTIPLAYER"
   - Wähle "Stop Hosting" oder drücke die Taste "cancel"
   - Überprüfe, ob die Session beendet wird

## Automatisierter Test

Da dieser Test zwei separate Spielinstanzen erfordert, ist eine vollständige Automatisierung komplex. Wir können jedoch Teilschritte automatisieren:

### Host-Instanz-Test (host_test.json)

```json
[
  {"type": "wait", "duration": 2.0},
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 5.0},
  
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "up"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "right"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "right"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "left"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "left"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "menu"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "menu"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 2.0}
]
```

### Client-Instanz-Test (client_test.json)

```json
[
  {"type": "wait", "duration": 2.0},
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 5.0},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 5.0},
  
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "up"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "right"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "right"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "left"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "left"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "menu"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "menu"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 2.0}
]
```

## Ausführung des Tests

Um diesen Test auszuführen, müssen zwei separate Spielinstanzen gestartet werden:

1. Starte die Host-Instanz mit dem Host-Test:
   ```
   .\run_test.bat multiplayer_host
   ```

2. Warte, bis die Host-Instanz die Multiplayer-Session gestartet hat

3. Starte die Client-Instanz mit dem Client-Test:
   ```
   .\run_test.bat multiplayer_client
   ```

## Erwartete Ergebnisse

1. Die Host-Instanz sollte erfolgreich eine Multiplayer-Session starten
2. Die Client-Instanz sollte sich erfolgreich mit der Host-Instanz verbinden
3. Die Bewegungen des Host-Spielers sollten in der Client-Instanz sichtbar sein
4. Die Bewegungen des Client-Spielers sollten in der Host-Instanz sichtbar sein
5. Die Multiplayer-Session sollte erfolgreich beendet werden können

## Analyse der Screenshots

Nach der Durchführung des Tests sollten die Screenshots in beiden Instanzen analysiert werden, um zu überprüfen, ob die erwarteten Ergebnisse eingetreten sind:

1. Überprüfe, ob die Host-Instanz erfolgreich eine Multiplayer-Session gestartet hat
2. Überprüfe, ob die Client-Instanz sich erfolgreich mit der Host-Instanz verbunden hat
3. Überprüfe, ob die Bewegungen des Host-Spielers in der Client-Instanz sichtbar sind
4. Überprüfe, ob die Bewegungen des Client-Spielers in der Host-Instanz sichtbar sind
5. Überprüfe, ob die Multiplayer-Session erfolgreich beendet wurde
