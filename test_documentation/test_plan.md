# Testplan für PokeTogether

Dieser Testplan beschreibt die verschiedenen Tests, die für das PokeTogether-Spiel durchgeführt werden sollen, und wie sie ausgeführt werden.

## Übersicht der Tests

1. **Hauptmenü-Test** - Testet die Navigation und Funktionalität des Hauptmenüs
2. **Optionsmenü-Test** - Testet die Navigation und Funktionalität des Optionsmenüs
3. **Spielerbewegung-Test** - Testet die Bewegung des Spielers in der Spielwelt
4. **Ingame-Menü-Test** - Testet die Navigation und Funktionalität des Ingame-Menüs
5. **Multiplayer-Test** - Testet die Multiplayer-Funktionalität mit zwei Spielinstanzen

## Durchführung der Tests

Die Tests werden mit dem automatisierten Testsystem durchgeführt, das Tastatureingaben simuliert und Screenshots erstellt. Die Tests werden in der folgenden Reihenfolge durchgeführt:

1. **Hauptmenü-Test**
   - Dieser Test überprüft die grundlegende Navigation im Hauptmenü
   - Er sollte als erstes durchgeführt werden, da er die Basis für alle anderen Tests bildet

2. **Optionsmenü-Test**
   - Dieser Test überprüft die Navigation und Funktionalität des Optionsmenüs
   - Er sollte nach dem Hauptmenü-Test durchgeführt werden, da er auf dem Hauptmenü aufbaut

3. **Spielerbewegung-Test**
   - Dieser Test überprüft die Bewegung des Spielers in der Spielwelt
   - Er sollte nach dem Hauptmenü-Test durchgeführt werden, da er ein neues Spiel startet

4. **Ingame-Menü-Test**
   - Dieser Test überprüft die Navigation und Funktionalität des Ingame-Menüs
   - Er sollte nach dem Spielerbewegung-Test durchgeführt werden, da er auf der Spielwelt aufbaut

5. **Multiplayer-Test**
   - Dieser Test überprüft die Multiplayer-Funktionalität mit zwei Spielinstanzen
   - Er sollte nach den anderen Tests durchgeführt werden, da er komplexer ist und zwei Spielinstanzen erfordert

## Ausführung der Tests

### Einzelne Tests

Um einen einzelnen Test auszuführen, verwende den folgenden Befehl:

```
.\run_minimized_test.bat <test_name>
```

Wobei `<test_name>` einer der folgenden Werte sein kann:
- `main_menu` - Führt den Hauptmenü-Test aus
- `options_menu` - Führt den Optionsmenü-Test aus
- `player_movement` - Führt den Spielerbewegung-Test aus
- `ingame_menu` - Führt den Ingame-Menü-Test aus

### Multiplayer-Test

Für den Multiplayer-Test, der zwei Spielinstanzen erfordert, verwende den folgenden Befehl:

```
.\run_multiplayer_test.bat
```

Dieses Skript startet zwei Instanzen des Spiels: eine als Host und eine als Client. Die Tests werden automatisch ausgeführt, und die Ergebnisse können in den Screenshots überprüft werden.

## Analyse der Testergebnisse

Nach der Durchführung eines Tests sollten die Screenshots im Verzeichnis `screenshots` analysiert werden, um zu überprüfen, ob die erwarteten Ergebnisse eingetreten sind. Die Screenshots sind nach Datum und Uhrzeit sortiert und enthalten den Namen der Aktion, die ausgeführt wurde.

Für jeden Test gibt es eine Liste von erwarteten Ergebnissen, die überprüft werden sollten. Diese sind in der Dokumentation des jeweiligen Tests aufgeführt.

## Nächste Schritte

Nach der Durchführung und Analyse der Tests können weitere Tests entwickelt werden, um andere Aspekte des Spiels zu testen, wie z.B.:

1. **Weitere Multiplayer-Funktionen** - Testet zusätzliche Multiplayer-Funktionen des Spiels
2. **Speichern und Laden** - Testet das Speichern und Laden des Spiels
3. **Kampfsystem** - Testet das Kampfsystem des Spiels
4. **Inventarsystem** - Testet das Inventarsystem des Spiels

Diese Tests können nach dem gleichen Muster wie die bestehenden Tests entwickelt werden.
