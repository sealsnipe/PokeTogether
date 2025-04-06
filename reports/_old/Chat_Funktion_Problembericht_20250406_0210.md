# Problembericht: Chat-Funktion im Multiplayer-Modus

## Übersicht

In diesem Bericht dokumentiere ich die Analyse für die Implementierung einer Chat-Funktion im Multiplayer-Modus des PokeTogether-Spiels. Die Chat-Funktion soll es Spielern ermöglichen, während des Spiels miteinander zu kommunizieren.

## Anforderungen

Die Chat-Funktion soll folgende Anforderungen erfüllen:

1. **Benutzeroberfläche**: Eine einfache Chat-Oberfläche, die während des Spiels angezeigt werden kann
2. **Nachrichteneingabe**: Möglichkeit, Textnachrichten einzugeben
3. **Nachrichtenversand**: Versenden der Nachrichten an andere Spieler
4. **Nachrichtenanzeige**: Anzeigen der empfangenen Nachrichten
5. **Tastatur- und Controller-Unterstützung**: Bedienung sowohl mit Tastatur als auch mit Controller

## Analyse des bestehenden Codes

### Netzwerk-Kommunikation

Die Analyse des bestehenden Codes zeigt, dass bereits grundlegende Mechanismen für die Netzwerk-Kommunikation vorhanden sind:

1. **Client-Klasse**: Die `GameClient`-Klasse enthält bereits eine `send_chat_message`-Methode:
   ```python
   def send_chat_message(self, message: str):
       """Send a chat message to the server

       Args:
           message: Chat message to send
       """
       if not self.connected:
           self.logger.warning("Not connected to a server")
           return

       data = {
           "type": "chat_message",
           "message": message
       }

       # Schedule the send coroutine in the client thread
       if self.event_loop and self.event_loop.is_running():
           asyncio.run_coroutine_threadsafe(self._send_message_async(data), self.event_loop)
   ```

2. **Server-Klasse**: Die `GameServer`-Klasse enthält bereits Code zum Verarbeiten von Chat-Nachrichten:
   ```python
   elif message_type == "chat_message":
       # Handle chat messages
       chat_data = {
           "type": "chat_message",
           "client_id": client_id,
           "player_name": self.players.get(client_id, {}).get("name", "Unknown"),
           "message": data.get("message", "")
       }

       # Broadcast chat message to all clients
       await self.broadcast(chat_data)
   ```

3. **Multiplayer-Manager**: Die `MultiplayerManager`-Klasse hat bereits einen Callback für Chat-Nachrichten:
   ```python
   self.on_chat_message = None
   ```

### UI-Komponenten

Für die Benutzeroberfläche gibt es bereits verschiedene UI-Komponenten, die als Grundlage für die Chat-Oberfläche dienen können:

1. **Input-Dialog**: Es gibt bereits einen Input-Dialog im `GameStateManager`:
   ```python
   def setup_input_dialog(self, title: str, default_text: str, callback: Callable[[str], None]) -> None:
       """Richtet einen Eingabedialog ein und wechselt zum INPUT_DIALOG-State

       Args:
           title: Der Titel des Dialogs
           default_text: Der Standardtext im Eingabefeld
           callback: Die Funktion, die aufgerufen wird, wenn der Dialog bestätigt wird
       """
       self.logger.info(f"Setting up input dialog: {title}")
       self.input_dialog_title = title
       self.input_dialog_text = default_text
       self.input_dialog_callback = callback

       # Zum INPUT_DIALOG-State wechseln
       self.change_state(GameState.INPUT_DIALOG)
   ```

2. **Render-Manager**: Der `RenderManager` kann bereits Input-Dialoge rendern:
   ```python
   def render_input_dialog(self) -> None:
       """Rendert den Eingabedialog"""
       # Dialog-Hintergrund
       dialog_width = 400
       dialog_height = 150
       dialog_x = (self.screen.get_width() - dialog_width) // 2
       dialog_y = (self.screen.get_height() - dialog_height) // 2
       dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
       
       # Hintergrund mit Rahmen
       self.render_rect(dialog_rect, (50, 50, 50), True)
       self.render_rect(dialog_rect, (200, 200, 200), False, 2)
       
       # Titel
       title_font = pygame.font.SysFont(None, 30)
       self.render_text(
           self.state_manager.input_dialog_title,
           (dialog_x + 20, dialog_y + 20),
           (255, 255, 255),
           title_font
       )
       
       # Eingabefeld
       input_rect = pygame.Rect(dialog_x + 20, dialog_y + 60, dialog_width - 40, 40)
       self.render_rect(input_rect, (30, 30, 30), True)
       self.render_rect(input_rect, (150, 150, 150), False, 1)
       
       # Eingabetext
       input_font = pygame.font.SysFont(None, 28)
       self.render_text(
           self.state_manager.input_dialog_text,
           (dialog_x + 25, dialog_y + 70),
           (255, 255, 255),
           input_font
       )
   ```

3. **Input-Handler**: Der `InputHandler` unterstützt bereits Tastatur- und Controller-Eingaben:
   ```python
   # Tastatur-Konfiguration
   self.keyboard_config = {
       # Bewegung
       "up": [pygame.K_UP, pygame.K_w],
       "down": [pygame.K_DOWN, pygame.K_s],
       "left": [pygame.K_LEFT, pygame.K_a],
       "right": [pygame.K_RIGHT, pygame.K_d],

       # Aktionen
       "action": [pygame.K_SPACE, pygame.K_RETURN, pygame.K_z],  # Z-Taste als Alternative
       "cancel": [pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_x],  # X-Taste als Alternative
       "menu": [pygame.K_TAB, pygame.K_m],  # Menü öffnen/schließen

       # Zusätzliche Aktionen
       "run": [pygame.K_LSHIFT, pygame.K_RSHIFT],  # Rennen
       "fast_forward": [pygame.K_f, pygame.K_SPACE]  # Vorspulen mit F oder Leertaste
   }
   ```

## Fehlende Komponenten

Trotz der vorhandenen Grundlagen fehlen noch einige Komponenten für eine vollständige Chat-Funktion:

1. **Chat-UI**: Eine dedizierte UI-Komponente für den Chat, die Nachrichten anzeigt und Eingaben ermöglicht
2. **Chat-Verlauf**: Eine Datenstruktur, um den Chat-Verlauf zu speichern
3. **Chat-Aktivierung**: Eine Möglichkeit, den Chat während des Spiels zu öffnen
4. **Chat-Callback**: Eine Implementierung des `on_chat_message`-Callbacks im `MultiplayerManager`

## Lösungsansatz

Basierend auf der Analyse schlage ich folgenden Lösungsansatz vor:

1. **Chat-UI-Komponente erstellen**:
   - Eine neue Klasse `ChatUI` im `ui`-Modul erstellen
   - Methoden zum Anzeigen und Scrollen durch den Chat-Verlauf implementieren
   - Methoden zum Öffnen und Schließen des Chat-Fensters implementieren

2. **Chat-Verlauf implementieren**:
   - Eine Datenstruktur für den Chat-Verlauf in der `Game`-Klasse hinzufügen
   - Methoden zum Hinzufügen und Abrufen von Nachrichten implementieren

3. **Chat-Aktivierung implementieren**:
   - Einen neuen Tastatur-/Controller-Shortcut für das Öffnen des Chats hinzufügen (z.B. T-Taste oder Y-Button)
   - Den `InputHandler` entsprechend erweitern

4. **Chat-Callback implementieren**:
   - Den `on_chat_message`-Callback im `MultiplayerManager` implementieren
   - Die empfangenen Nachrichten zum Chat-Verlauf hinzufügen

5. **Integration in die Game-Klasse**:
   - Die Chat-UI in die `Game`-Klasse integrieren
   - Die Chat-Funktionalität in den Spielablauf einbinden

## Implementierungsplan

1. **Chat-UI-Komponente erstellen**:
   - Neue Datei `src/game/ui/chat_ui.py` erstellen
   - `ChatUI`-Klasse mit Methoden zum Anzeigen und Interagieren mit dem Chat implementieren

2. **Chat-Verlauf in Game-Klasse hinzufügen**:
   - `chat_history`-Liste in der `Game`-Klasse hinzufügen
   - Methoden zum Hinzufügen und Abrufen von Nachrichten implementieren

3. **Chat-Aktivierung implementieren**:
   - `InputHandler` um Chat-Shortcut erweitern
   - Methode zum Öffnen des Chats in der `Game`-Klasse hinzufügen

4. **Chat-Callback implementieren**:
   - `_on_chat_message`-Methode in der `Game`-Klasse implementieren
   - Callback im `MultiplayerManager` registrieren

5. **Integration in die Game-Klasse**:
   - Chat-UI in der `Game`-Klasse initialisieren
   - Chat-UI in der `render`-Methode der `Game`-Klasse einbinden
   - Chat-Funktionalität in der `update`-Methode der `Game`-Klasse einbinden

## Fazit

Die Implementierung einer Chat-Funktion im Multiplayer-Modus ist mit den vorhandenen Grundlagen gut machbar. Die meisten benötigten Komponenten sind bereits vorhanden oder können leicht erweitert werden. Die Hauptaufgabe besteht darin, eine dedizierte Chat-UI zu erstellen und die vorhandenen Komponenten zu integrieren.
