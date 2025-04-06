# PokeTogether Multiplayer - To-Do Liste

## Aktuelles Ziel: Spieler-Sichtbarkeit im Multiplayer

Problem: Spieler können sich gegenseitig nicht sehen, obwohl die Netzwerkkommunikation funktioniert.

### 1. Netzwerk-Logs prüfen / erweitern

- [x] Logs beim Datenempfang implementieren/verbessern:
  - [x] Deutliche Log-Ausgabe, wenn Client Daten anderer Spieler empfängt (z.B. `[INFO] Received update for Player2: x=..., y=...`)
  - [x] Log-Ausgaben im Netzwerk-Callback (z.B. `_process_message` oder `on_player_update`) hinzufügen

- [x] Logs beim Senden implementieren/verbessern (optional):
  - [x] Log-Ausgabe, wenn Client Daten über sich selbst an den Server schickt (z.B. `[DEBUG] Sending position update: x=..., y=...`)

### 2. Render-Funktion für andere Spieler

- [x] Methode zum Zeichnen aller entfernten Spieler überprüfen/erstellen (z.B. `render_other_players()`)
- [x] Log-Ausgaben in dieser Funktion hinzufügen:
  - [x] `[DEBUG] Rendering Player <ID>: x=..., y=...`
- [x] Verbesserte Darstellung der anderen Spieler implementieren (farbige Rechtecke, Namensschilder, Richtungspfeile)

### 3. Datenstrom verifizieren

- [x] Bei jedem Update der Liste anderer Spieler (z.B. `other_players`) loggen:
  - [x] `[DEBUG] other_players list: [ {id:..., x:..., y:...}, ... ]`
- [x] Sicherstellen, dass diese Liste aktualisiert wird, wenn neue Daten vom Server eintreffen
- [x] Nachrichtenstruktur zwischen Client und Server korrigieren (Verwendung von `player_data` statt `data`)
- [x] WebSocket-Verbindung stabilisieren (einheitlicher Pfad `/multiplayer`)
- [x] Verbesserte Fehlerbehandlung und Logging

### 4. Testablauf

- [x] Manuelle Tests durchführen:
  - [x] Server starten
  - [x] Client1 und Client2 starten (jeweils mit eigenem Save/Config)
  - [x] Player1 erkennbar bewegen (z.B. in Richtung x+100)
  - [x] Prüfen, ob Player2 im Log meldet: `[INFO] Received update for Player1: x=100, y=...` und `[DEBUG] Rendering Player1 at (100, ...)`

- [x] Automatisierte Tests erweitern (falls vorhanden):
  - [x] Nach Rendering-Hinweis in den Logs suchen
  - [x] Prüfen, ob Koordinaten ungleich 0 sind, wenn Player1 sich bewegt hat

### 5. Nachweis des Erfolgs

- [x] In den Logs ist eindeutig zu erkennen, dass:
  - [x] Ein Client Daten für andere Spieler erhält
  - [x] Die Render-Funktion tatsächlich aufgerufen wird
  - [x] Die Koordinaten stimmen
- [ ] Im Spiel ist Player2 von Player1 aus sichtbar (und umgekehrt)

## Zukünftige Schritte (nach Lösung des Sichtbarkeitsproblems)

- [ ] Schritt C: Klarer Game-State-Management
- [ ] Schritt D: Erweiterte Tests & Stresstests
- [ ] Schritt E: Speicherstands-Management
