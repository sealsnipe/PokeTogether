# Bericht: Problem mit der Spieler-Sichtbarkeit im Multiplayer

## Übersicht

In diesem Bericht dokumentiere ich die Untersuchung des Problems mit der Spieler-Sichtbarkeit im Multiplayer-Modus des PokeTogether-Spiels. Das Hauptproblem besteht darin, dass Spieler sich gegenseitig nicht sehen können, obwohl die Netzwerkkommunikation funktioniert.

## Identifizierte Probleme

Nach einer gründlichen Analyse des Codes und der Logs wurden folgende potenzielle Probleme identifiziert:

1. **Leere Spielerdaten**: Die Logs zeigen, dass die Spielerdaten, die zwischen den Clients ausgetauscht werden, leer sind:
   ```
   2025-04-05 22:57:01 - game.network.client - INFO - Received message: {"type": "player_update", "client_id": "816fee1a-4508-4f75-86e7-2ae62bc97893", "player_data": {}}
   ```

2. **Inkonsistente Nachrichtenstruktur**: Die Nachrichtenstruktur zwischen Client und Server stimmt nicht überein. Der Client sendet die Nachricht mit einem `data` Feld, aber der Server erwartet ein `player_data` Feld.

3. **Leere `other_players` Liste**: Die Logs zeigen, dass die `other_players` Liste leer bleibt, obwohl Spielerdaten empfangen werden:
   ```
   2025-04-05 22:57:01 - game.core.game_refactored - INFO - [INFO] Rendering other players. Active: 0 players
   ```

## Detaillierte Analyse

### 1. Nachrichtenstruktur

Die Nachrichtenstruktur zwischen Client und Server ist inkonsistent:

- **Client-Seite**: Der Client sendet die Nachricht mit einem `data` Feld:
  ```python
  message = {
      "type": message_type,
      "data": message_data
  }
  ```

- **Server-Seite**: Der Server erwartet ein `player_data` Feld:
  ```python
  if message_type == "player_update":
      # Update player data
      player_data = data.get("player_data", {})
  ```

### 2. Spielerdaten-Übertragung

Die Spielerdaten werden korrekt vom Client zum Server gesendet, aber die Daten sind leer oder werden nicht korrekt weitergeleitet:

- **Client-Seite**: Der Client sendet die Spielerdaten:
  ```python
  player_data = self.player.to_network_data()
  self.multiplayer_manager.send_player_update(player_data)
  ```

- **Server-Seite**: Der Server leitet die Daten an die anderen Clients weiter:
  ```python
  await self.broadcast({
      "type": "player_update",
      "client_id": client_id,
      "player_data": player_data
  }, exclude={client_id})
  ```

### 3. Spielerdaten-Verarbeitung

Die Spielerdaten werden vom Client empfangen, aber nicht korrekt verarbeitet:

- **Client-Seite**: Der Client empfängt die Spielerdaten:
  ```python
  async def _handle_player_update(self, data: Dict[str, Any]):
      client_id = data.get("client_id")
      player_data = data.get("player_data", {})

      if client_id:
          self.players[client_id] = player_data
  ```

- **Game-Klasse**: Die Game-Klasse verarbeitet die Spielerdaten:
  ```python
  def _on_player_update(self, client_id: str, player_data: dict):
      self.other_players[client_id] = player_data
  ```

## Bisherige Lösungsansätze

### 1. Korrektur der Nachrichtenstruktur

Die Nachrichtenstruktur zwischen Client und Server wurde korrigiert:

```python
# Server-Seite
if message_type == "player_update":
    # Update player data
    player_data = data.get("data", {})
    
    # Log the received data
    self.logger.info(f"Received player update from client {client_id}: {player_data}")
```

### 2. Verbesserte Logs

Die Logs wurden erweitert, um mehr Informationen über den Empfang und die Verarbeitung von Spielerdaten zu erhalten:

```python
# Ausführlichere Log-Ausgabe für Spieler-Updates
self.logger.info(f"[INFO] Received update for Player {player_data.get('name')}: x={player_data.get('x')}, y={player_data.get('y')}, direction={player_data.get('direction')}")

# Prüfen, ob es sich um einen neuen Spieler handelt
is_new_player = client_id not in self.other_players
if is_new_player:
    self.logger.info(f"[INFO] New player joined: {player_data.get('name')} (ID: {client_id})")
```

### 3. Verbesserte Render-Funktion

Die `_render_other_players` Methode wurde verbessert, um andere Spieler korrekt darzustellen:

```python
def _render_other_players(self) -> None:
    """Rendert die anderen Spieler im Multiplayer-Modus"""
    # Prüfen, ob überhaupt andere Spieler vorhanden sind
    if not self.other_players:
        self.logger.debug("No other players to render")
        return
        
    # Temporärer Font für Spielernamen
    font = pygame.font.SysFont(None, 18)
    
    for player_id, player_data in self.other_players.items():
        # Spielerdaten extrahieren
        x = player_data.get("x", 0)
        y = player_data.get("y", 0)
        name = player_data.get("name", "Player")
        character_type = player_data.get("character_type", "Red")
        direction = player_data.get("direction", "down")
        
        # Kamera-Offset anwenden
        offset = self.camera.get_offset()
        screen_x = int(x - offset[0])
        screen_y = int(y - offset[1])
        
        # Debug-Ausgabe für das Rendering
        self.logger.debug(f"[DEBUG] Rendering Player {name} (ID: {player_id}): x={x}, y={y}, screen_x={screen_x}, screen_y={screen_y}")

        # Prüfen, ob der Spieler im sichtbaren Bereich ist
        if (0 <= screen_x <= self.screen.get_width() and
            0 <= screen_y <= self.screen.get_height()):
            
            # Farbe basierend auf dem Charaktertyp wählen
            color = (0, 0, 255)  # Standard: Blau
            if character_type == "Blue":
                color = (0, 0, 200)  # Dunkelblau
            elif character_type == "Red":
                color = (200, 0, 0)  # Dunkelrot
            elif character_type == "Green":
                color = (0, 200, 0)  # Dunkelgrün
            elif character_type == "Yellow":
                color = (200, 200, 0)  # Gelb
            
            # Spieler als farbiges Rechteck darstellen
            player_rect = pygame.Rect(screen_x - 16, screen_y - 16, 32, 32)
            pygame.draw.rect(self.screen, color, player_rect)
            
            # Spielername anzeigen
            name_text = font.render(name, True, (255, 255, 255))
            self.screen.blit(name_text, (screen_x - name_text.get_width() // 2, screen_y - 30))
            
            # Richtungspfeil anzeigen
            arrow_color = (255, 255, 0)  # Gelb
            arrow_length = 20
            arrow_start = (player_rect.centerx, player_rect.centery)
            arrow_end = arrow_start
            
            if direction == "up":
                arrow_end = (arrow_start[0], arrow_start[1] - arrow_length)
            elif direction == "down":
                arrow_end = (arrow_start[0], arrow_start[1] + arrow_length)
            elif direction == "left":
                arrow_end = (arrow_start[0] - arrow_length, arrow_start[1])
            elif direction == "right":
                arrow_end = (arrow_start[0] + arrow_length, arrow_start[1])
                
            pygame.draw.line(self.screen, arrow_color, arrow_start, arrow_end, 2)
```

### 4. Ausschluss eigener Spielerdaten aus der `other_players` Liste

Die eigenen Spielerdaten werden nun nicht mehr in die `other_players` Liste aufgenommen:

```python
# Prüfen, ob es sich um die eigenen Daten handelt
is_own_player = player_data.get("player_id") == self.player.player_id
if is_own_player:
    self.logger.info(f"[INFO] Received update for own player. Not adding to other_players list.")
    
    # Server-Reconciliation anwenden, wenn es sich um die eigenen Daten handelt
    if self.config.get_reconciliation():
        self.logger.debug(f"Applying server reconciliation for own player data")
        self.player.apply_server_update(player_data, reconciliation=True)
    return

# Spielerdaten speichern (nur für andere Spieler)
self.other_players[client_id] = player_data
```

## Nächste Schritte

Trotz der bisherigen Lösungsansätze bleibt das Problem bestehen. Die nächsten Schritte könnten sein:

1. **Überprüfung der Spielerdaten-Übertragung**: Sicherstellen, dass die Spielerdaten korrekt vom Client zum Server und zurück zu den anderen Clients übertragen werden.
2. **Überprüfung der Spielerdaten-Verarbeitung**: Sicherstellen, dass die Spielerdaten korrekt von den Clients verarbeitet werden.
3. **Überprüfung der Render-Funktion**: Sicherstellen, dass die Render-Funktion korrekt implementiert ist und die Spielerdaten korrekt darstellt.
4. **Implementierung eines Debug-Modus**: Implementierung eines Debug-Modus, der detaillierte Informationen über die Spielerdaten und die Render-Funktion anzeigt.

## Fazit

Das Problem mit der Spieler-Sichtbarkeit im Multiplayer-Modus ist noch nicht gelöst. Die bisherigen Lösungsansätze haben das Problem nicht behoben. Eine weitere Untersuchung ist erforderlich, um das Problem zu identifizieren und zu beheben.
