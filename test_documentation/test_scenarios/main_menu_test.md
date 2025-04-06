# Hauptmenü-Test

Dieser Test überprüft die Navigation und Funktionalität des Hauptmenüs.

## Zu testende Funktionen

1. Navigation zwischen den Menüoptionen
2. Auswahl von Optionen
3. Öffnen des Optionsmenüs
4. Zurückkehren zum Hauptmenü

## Testschritte

1. **Spiel starten**
   - Das Hauptmenü sollte angezeigt werden
   - Die erste Option "New Game" sollte ausgewählt sein

2. **Navigation nach unten**
   - Drücke die Taste "down" mehrmals
   - Überprüfe, ob die Auswahl durch alle Optionen rotiert:
     - New Game → Host Game → Join Game → Continue → Options → Exit → New Game

3. **Navigation nach oben**
   - Drücke die Taste "up" mehrmals
   - Überprüfe, ob die Auswahl durch alle Optionen in umgekehrter Reihenfolge rotiert:
     - New Game → Exit → Options → Continue → Join Game → Host Game → New Game

4. **Optionsmenü öffnen**
   - Navigiere zur Option "Options"
   - Drücke die Taste "action" (Enter/Space/Z)
   - Überprüfe, ob das Optionsmenü geöffnet wird

5. **Zurück zum Hauptmenü**
   - Drücke die Taste "cancel" (Escape/Backspace/X) im Optionsmenü
   - Überprüfe, ob das Hauptmenü wieder angezeigt wird

## Testanweisungen (JSON)

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
  
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "up"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "up"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 2.0},
  
  {"type": "key_press", "key": "cancel"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "cancel"},
  {"type": "wait", "duration": 2.0}
]
```

## Erwartete Ergebnisse

1. Das Hauptmenü sollte korrekt angezeigt werden
2. Die Auswahl sollte zwischen den Optionen wechseln, wenn die Tasten "up" und "down" gedrückt werden
3. Das Optionsmenü sollte geöffnet werden, wenn die Option "Options" ausgewählt und die Taste "action" gedrückt wird
4. Das Hauptmenü sollte wieder angezeigt werden, wenn die Taste "cancel" im Optionsmenü gedrückt wird

## Analyse der Screenshots

Nach der Durchführung des Tests sollten die Screenshots analysiert werden, um zu überprüfen, ob die erwarteten Ergebnisse eingetreten sind:

1. Überprüfe, ob die Auswahl im Hauptmenü korrekt hervorgehoben wird
2. Überprüfe, ob das Optionsmenü korrekt angezeigt wird
3. Überprüfe, ob das Hauptmenü nach dem Schließen des Optionsmenüs wieder korrekt angezeigt wird
