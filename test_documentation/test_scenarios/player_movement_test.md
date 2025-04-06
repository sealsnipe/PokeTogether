# Spielerbewegung-Test

Dieser Test überprüft die Bewegung des Spielers in der Spielwelt.

## Zu testende Funktionen

1. Bewegung in alle vier Richtungen (oben, unten, links, rechts)
2. Diagonale Bewegung (Kombination von zwei Richtungen)
3. Rennen (erhöhte Geschwindigkeit)
4. Kollisionserkennung mit Hindernissen

## Testschritte

1. **Spiel starten und neues Spiel beginnen**
   - Starte das Spiel und warte, bis das Hauptmenü angezeigt wird
   - Wähle "New Game" und starte ein neues Spiel
   - Warte, bis der Spieler in der Spielwelt erscheint

2. **Bewegung in alle vier Richtungen**
   - Drücke die Taste "up" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste los und warte kurz
   - Drücke die Taste "right" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste los und warte kurz
   - Drücke die Taste "down" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste los und warte kurz
   - Drücke die Taste "left" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste los und warte kurz

3. **Diagonale Bewegung**
   - Drücke die Tasten "up" und "right" gleichzeitig und halte sie für 2 Sekunden gedrückt
   - Lasse die Tasten los und warte kurz
   - Drücke die Tasten "right" und "down" gleichzeitig und halte sie für 2 Sekunden gedrückt
   - Lasse die Tasten los und warte kurz
   - Drücke die Tasten "down" und "left" gleichzeitig und halte sie für 2 Sekunden gedrückt
   - Lasse die Tasten los und warte kurz
   - Drücke die Tasten "left" und "up" gleichzeitig und halte sie für 2 Sekunden gedrückt
   - Lasse die Tasten los und warte kurz

4. **Rennen**
   - Drücke die Taste "run" (Shift) und halte sie gedrückt
   - Drücke die Taste "up" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste "up" los
   - Drücke die Taste "right" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste "right" los
   - Drücke die Taste "down" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste "down" los
   - Drücke die Taste "left" und halte sie für 2 Sekunden gedrückt
   - Lasse die Taste "left" los
   - Lasse die Taste "run" los

## Testanweisungen (JSON)

```json
[
  {"type": "wait", "duration": 2.0},
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
  
  {"type": "key_press", "key": "up"},
  {"type": "key_press", "key": "right"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "up"},
  {"type": "key_release", "key": "right"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "right"},
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "right"},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "down"},
  {"type": "key_press", "key": "left"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "down"},
  {"type": "key_release", "key": "left"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "left"},
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "left"},
  {"type": "key_release", "key": "up"},
  {"type": "wait", "duration": 1.0},
  
  {"type": "key_press", "key": "run"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "up"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "up"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "right"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "right"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "down"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "down"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_press", "key": "left"},
  {"type": "wait", "duration": 2.0},
  {"type": "key_release", "key": "left"},
  {"type": "wait", "duration": 0.5},
  
  {"type": "key_release", "key": "run"},
  {"type": "wait", "duration": 1.0}
]
```

## Erwartete Ergebnisse

1. Der Spieler sollte sich in die entsprechende Richtung bewegen, wenn die Richtungstasten gedrückt werden
2. Der Spieler sollte sich diagonal bewegen, wenn zwei Richtungstasten gleichzeitig gedrückt werden
3. Der Spieler sollte sich schneller bewegen, wenn die Taste "run" gedrückt wird
4. Der Spieler sollte nicht durch Hindernisse hindurchgehen können (Kollisionserkennung)

## Analyse der Screenshots

Nach der Durchführung des Tests sollten die Screenshots analysiert werden, um zu überprüfen, ob die erwarteten Ergebnisse eingetreten sind:

1. Überprüfe, ob der Spieler sich in die richtige Richtung bewegt
2. Überprüfe, ob der Spieler sich diagonal bewegt, wenn zwei Richtungstasten gleichzeitig gedrückt werden
3. Überprüfe, ob der Spieler sich schneller bewegt, wenn die Taste "run" gedrückt wird
4. Überprüfe, ob der Spieler an Hindernissen stoppt
