# Optionsmenü-Test

Dieser Test überprüft die Navigation und Funktionalität des Optionsmenüs.

## Zu testende Funktionen

1. Navigation zwischen den Menüoptionen
2. Wechsel zwischen verschiedenen Untermenüs
3. Ändern von Einstellungen
4. Speichern von Einstellungen
5. Zurückkehren zum Hauptmenü

## Testschritte

1. **Optionsmenü öffnen**
   - Starte das Spiel und warte, bis das Hauptmenü angezeigt wird
   - Navigiere zur Option "Options"
   - Drücke die Taste "action" (Enter/Space/Z)
   - Überprüfe, ob das Optionsmenü geöffnet wird

2. **Navigation im Hauptmenü des Optionsmenüs**
   - Überprüfe, ob die erste Option "Video" ausgewählt ist
   - Drücke die Taste "down" mehrmals
   - Überprüfe, ob die Auswahl durch alle Optionen rotiert:
     - Video → Audio → Gameplay → Controls → Back → Video

3. **Untermenü öffnen**
   - Navigiere zur Option "Video"
   - Drücke die Taste "action"
   - Überprüfe, ob das Video-Untermenü geöffnet wird

4. **Einstellung ändern**
   - Navigiere zur Option "Resolution"
   - Drücke die Taste "action"
   - Überprüfe, ob die Auflösung geändert wird

5. **Zurück zum Hauptmenü des Optionsmenüs**
   - Navigiere zur Option "Back" im Video-Untermenü
   - Drücke die Taste "action"
   - Überprüfe, ob das Hauptmenü des Optionsmenüs wieder angezeigt wird
   - Alternativ: Drücke die Taste "cancel"

6. **Optionsmenü verlassen**
   - Navigiere zur Option "Back" im Hauptmenü des Optionsmenüs
   - Drücke die Taste "action"
   - Überprüfe, ob das Hauptmenü wieder angezeigt wird
   - Alternativ: Drücke die Taste "cancel"

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
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
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
  
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "up"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "up"},
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
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
  {"type": "wait", "duration": 2.0},
  
  {"type": "key_press", "key": "action"},
  {"type": "wait", "duration": 0.5},
  {"type": "key_release", "key": "action"},
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

1. Das Optionsmenü sollte korrekt angezeigt werden
2. Die Auswahl sollte zwischen den Optionen wechseln, wenn die Tasten "up" und "down" gedrückt werden
3. Das Video-Untermenü sollte geöffnet werden, wenn die Option "Video" ausgewählt und die Taste "action" gedrückt wird
4. Die Auflösung sollte geändert werden, wenn die Option "Resolution" ausgewählt und die Taste "action" gedrückt wird
5. Das Hauptmenü des Optionsmenüs sollte wieder angezeigt werden, wenn die Option "Back" im Video-Untermenü ausgewählt und die Taste "action" gedrückt wird oder die Taste "cancel" gedrückt wird
6. Das Hauptmenü sollte wieder angezeigt werden, wenn die Option "Back" im Hauptmenü des Optionsmenüs ausgewählt und die Taste "action" gedrückt wird oder die Taste "cancel" gedrückt wird

## Analyse der Screenshots

Nach der Durchführung des Tests sollten die Screenshots analysiert werden, um zu überprüfen, ob die erwarteten Ergebnisse eingetreten sind:

1. Überprüfe, ob das Optionsmenü korrekt angezeigt wird
2. Überprüfe, ob die Auswahl im Optionsmenü korrekt hervorgehoben wird
3. Überprüfe, ob das Video-Untermenü korrekt angezeigt wird
4. Überprüfe, ob die Auflösung korrekt geändert wird
5. Überprüfe, ob das Hauptmenü des Optionsmenüs nach dem Schließen des Video-Untermenüs wieder korrekt angezeigt wird
6. Überprüfe, ob das Hauptmenü nach dem Schließen des Optionsmenüs wieder korrekt angezeigt wird
