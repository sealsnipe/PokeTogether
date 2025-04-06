# Problembericht: Multiplayer-Sichtbarkeit

## Übersicht

In diesem Bericht dokumentiere ich die Analyse des Problems mit der Spieler-Sichtbarkeit im Multiplayer-Modus des PokeTogether-Spiels. Das Hauptproblem besteht darin, dass Spieler sich gegenseitig nicht sehen können, obwohl die WebSocket-Verbindung funktioniert und Daten ausgetauscht werden.

## Identifizierte Probleme

Nach einer gründlichen Analyse des Codes wurden folgende Probleme identifiziert:

1. **Fehlende Callback-Registrierung**: In der Game-Klasse (`game_refactored.py`) wurden die Multiplayer-Callbacks nicht registriert. Es fehlte die Methode `_register_multiplayer_callbacks()`, die die Callbacks für Spieler-Updates, Spieler-Disconnects und Chat-Nachrichten registriert.

2. **Inkonsistente Nachrichtenstruktur**: Die Nachrichtenstruktur zwischen Client und Server war inkonsistent. Der Client sendete die Nachricht mit einem `player_data` Feld, das wiederum die eigentlichen Spielerdaten enthielt, was zu einer verschachtelten Struktur führte.

3. **Inkonsistente Methoden zum Senden von Nachrichten**: In der `GameClient` Klasse gab es zwei Methoden zum Senden von Nachrichten: `_send_message` und `_send_message_async`. Die `send_player_update` Methode verwendete `_send_message`, während die `send_message` Methode `_send_message_async` verwendete, was zu Verwirrung führen konnte.

4. **Fehlende Chat-Nachricht-Methode**: In der Game-Klasse fehlte die `_on_chat_message` Methode, die als Callback für Chat-Nachrichten registriert wurde.

## Detaillierte Analyse

### 1. Fehlende Callback-Registrierung

In der Game-Klasse (`game_refactored.py`) wurden die Multiplayer-Callbacks nicht registriert. Es fehlte die Methode `_register_multiplayer_callbacks()`, die die Callbacks für Spieler-Updates, Spieler-Disconnects und Chat-Nachrichten registriert.

```python
# Diese Methode fehlte in der Game-Klasse
def _register_multiplayer_callbacks(self) -> None:
    """Registriert die Multiplayer-Callbacks"""
    self.logger.info("Registering multiplayer callbacks")
    
    # Prüfen, ob die Methoden existieren
    if not hasattr(self.multiplayer_manager, "on_player_update"):
        self.logger.error("multiplayer_manager has no attribute 'on_player_update'")
    if not hasattr(self, "_on_player_update"):
        self.logger.error("Game has no method '_on_player_update'")
        
    # Callbacks registrieren
    self.multiplayer_manager.on_player_update = self._on_player_update
    self.multiplayer_manager.on_player_disconnected = self._on_player_disconnected
    self.multiplayer_manager.on_chat_message = self._on_chat_message
    
    self.logger.info("Multiplayer callbacks registered successfully")
```

Außerdem fehlte der Aufruf dieser Methode in der `__init__` Methode der Game-Klasse:

```python
# UI-Elemente initialisieren
self._init_ui()

# Render-Funktionen registrieren
self._register_render_functions()

# Input-Callbacks registrieren
self._register_input_callbacks()

# State-Callbacks registrieren
self._register_state_callbacks()

# Multiplayer-Callbacks registrieren
self._register_multiplayer_callbacks()  # Diese Zeile fehlte
```

### 2. Inkonsistente Nachrichtenstruktur

Die Nachrichtenstruktur zwischen Client und Server war inkonsistent. Der Client sendete die Nachricht mit einem `player_data` Feld, das wiederum die eigentlichen Spielerdaten enthielt, was zu einer verschachtelten Struktur führte:

```json
{
  "type": "player_update",
  "player_data": {
    "player_id": "...",
    "name": "Player1",
    "x": 608.0,
    "y": 457.0,
    ...
  }
}
```

Anstatt:

```json
{
  "type": "player_update",
  "player_id": "...",
  "name": "Player1",
  "x": 608.0,
  "y": 457.0,
  ...
}
```

### 3. Inkonsistente Methoden zum Senden von Nachrichten

In der `GameClient` Klasse gab es zwei Methoden zum Senden von Nachrichten: `_send_message` und `_send_message_async`. Die `send_player_update` Methode verwendete `_send_message`, während die `send_message` Methode `_send_message_async` verwendete, was zu Verwirrung führen konnte.

```python
# In der send_player_update Methode
asyncio.run_coroutine_threadsafe(self._send_message(message), self.event_loop)

# In der send_message Methode
asyncio.run_coroutine_threadsafe(self._send_message_async(message), self.event_loop)
```

### 4. Fehlende Chat-Nachricht-Methode

In der Game-Klasse fehlte die `_on_chat_message` Methode, die als Callback für Chat-Nachrichten registriert wurde:

```python
# Diese Methode fehlte in der Game-Klasse
def _on_chat_message(self, client_id: str, player_name: str, message: str):
    """Callback für Chat-Nachrichten

    Args:
        client_id: Client-ID des Spielers
        player_name: Name des Spielers
        message: Chat-Nachricht
    """
    self.logger.info(f"Chat message from {player_name}: {message}")
    
    # TODO: Chat-Nachricht anzeigen
```

## Lösungsansatz

Um die identifizierten Probleme zu beheben, werde ich folgende Änderungen vornehmen:

1. **Implementierung der Callback-Registrierung**: Ich werde die Methode `_register_multiplayer_callbacks()` in der Game-Klasse implementieren und sicherstellen, dass sie in der `__init__` Methode aufgerufen wird.

2. **Vereinheitlichung der Nachrichtenstruktur**: Ich werde die Nachrichtenstruktur zwischen Client und Server vereinheitlichen, indem ich die Spielerdaten direkt in die Nachricht entpacke, anstatt sie in einem `player_data` Feld zu verschachteln.

3. **Vereinheitlichung der Methoden zum Senden von Nachrichten**: Ich werde die Methoden zum Senden von Nachrichten vereinheitlichen, indem ich überall `_send_message_async` verwende und die `_send_message` Methode entferne, wenn sie nicht mehr benötigt wird.

4. **Implementierung der Chat-Nachricht-Methode**: Ich werde die `_on_chat_message` Methode in der Game-Klasse implementieren.

## Nächste Schritte

1. Implementierung der Callback-Registrierung
2. Vereinheitlichung der Nachrichtenstruktur
3. Vereinheitlichung der Methoden zum Senden von Nachrichten
4. Implementierung der Chat-Nachricht-Methode
5. Testen der Implementierung
6. Analyse der Testergebnisse und Identifizierung verbleibender Probleme
