# Ingame-Menü-Test

Dieser Test überprüft die Navigation und Funktionalität des Ingame-Menüs.

## Zu testende Funktionen

1. Öffnen und Schließen des Ingame-Menüs
2. Navigation zwischen den Menüoptionen
3. Öffnen von Untermenüs
4. Zurückkehren zum Hauptmenü des Ingame-Menüs

## Testschritte

1. **Spiel starten und neues Spiel beginnen**
   - Starte das Spiel und warte, bis das Hauptmenü angezeigt wird
   - Wähle "New Game" und starte ein neues Spiel
   - Warte, bis der Spieler in der Spielwelt erscheint

2. **Ingame-Menü öffnen**
   - Drücke die Taste "menu" (Tab/M)
   - Überprüfe, ob das Ingame-Menü geöffnet wird

3. **Navigation im Ingame-Menü**
   - Überprüfe, ob die erste Option "POKEMON" ausgewählt ist
   - Drücke die Taste "down" mehrmals
   - Überprüfe, ob die Auswahl durch alle Optionen rotiert:
     - POKEMON → BAG → PLAYER → SAVE → OPTIONS → MULTIPLAYER → EXIT → POKEMON

4. **Untermenü öffnen**
   - Navigiere zur Option "OPTIONS"
   - Drücke die Taste "action"
   - Überprüfe, ob das Optionsmenü geöffnet wird

5. **Zurück zum Ingame-Menü**
   - Drücke die Taste "cancel"
   - Überprüfe, ob das Ingame-Menü wieder angezeigt wird

6. **Ingame-Menü schließen**
   - Navigiere zur Option "EXIT"
   - Drücke die Taste "action"
   - Überprüfe, ob das Ingame-Menü geschlossen wird und der Spieler wieder in der Spielwelt ist
   - Alternativ: Drücke die Taste "menu" oder "cancel"

## Testanweisungen (JSON)

```json
[
  {"type": "wait", "duration": 2.0},
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 5.0},
  
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
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 2.0},
  
  {"type": "key_press", "key": "cancel"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "cancel"},
  {"type": "wait", "duration": 1.0},
  
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

## Erwartete Ergebnisse

1. Das Ingame-Menü sollte geöffnet werden, wenn die Taste "menu" gedrückt wird
2. Die Auswahl sollte zwischen den Optionen wechseln, wenn die Tasten "up" und "down" gedrückt werden
3. Das Optionsmenü sollte geöffnet werden, wenn die Option "OPTIONS" ausgewählt und die Taste "action" gedrückt wird
4. Das Ingame-Menü sollte wieder angezeigt werden, wenn die Taste "cancel" im Optionsmenü gedrückt wird
5. Das Ingame-Menü sollte geschlossen werden, wenn die Option "EXIT" ausgewählt und die Taste "action" gedrückt wird oder die Taste "menu" oder "cancel" gedrückt wird

## Analyse der Screenshots

Nach der Durchführung des Tests sollten die Screenshots analysiert werden, um zu überprüfen, ob die erwarteten Ergebnisse eingetreten sind:

1. Überprüfe, ob das Ingame-Menü korrekt angezeigt wird
2. Überprüfe, ob die Auswahl im Ingame-Menü korrekt hervorgehoben wird
3. Überprüfe, ob das Optionsmenü korrekt angezeigt wird
4. Überprüfe, ob das Ingame-Menü nach dem Schließen des Optionsmenüs wieder korrekt angezeigt wird
5. Überprüfe, ob der Spieler wieder in der Spielwelt ist, nachdem das Ingame-Menü geschlossen wurde
