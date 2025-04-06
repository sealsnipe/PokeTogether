# PokeTogether Testdokumentation

Diese Dokumentation beschreibt die verschiedenen Tests, die für das PokeTogether-Spiel entwickelt wurden, und wie sie verwendet werden.

## Übersicht

Die Testdokumentation besteht aus den folgenden Teilen:

1. **game_features.md** - Eine Übersicht über die Spielfunktionen und deren Steuerung
2. **test_plan.md** - Ein Plan für die Durchführung der Tests
3. **test_scenarios/** - Detaillierte Beschreibungen der einzelnen Testszenarien
4. **test_json/** - JSON-Dateien mit den Testanweisungen für die automatisierte Ausführung

## Testszenarien

Die folgenden Testszenarien wurden entwickelt:

1. **Hauptmenü-Test** - Testet die Navigation und Funktionalität des Hauptmenüs
2. **Optionsmenü-Test** - Testet die Navigation und Funktionalität des Optionsmenüs
3. **Spielerbewegung-Test** - Testet die Bewegung des Spielers in der Spielwelt
4. **Ingame-Menü-Test** - Testet die Navigation und Funktionalität des Ingame-Menüs

## Ausführung der Tests

Um einen Test auszuführen, verwende den folgenden Befehl:

```
.\run_test.bat <test_name>
```

Wobei `<test_name>` einer der folgenden Werte sein kann:
- `main_menu` - Führt den Hauptmenü-Test aus
- `options_menu` - Führt den Optionsmenü-Test aus
- `player_movement` - Führt den Spielerbewegung-Test aus
- `ingame_menu` - Führt den Ingame-Menü-Test aus

Das Skript kopiert die entsprechende JSON-Datei in das `input_instructions`-Verzeichnis und startet das Spiel im minimierten Modus. Das Spiel liest die Testanweisungen und führt sie aus, während es Screenshots erstellt, um die Ergebnisse zu dokumentieren.

## Analyse der Testergebnisse

Nach der Durchführung eines Tests sollten die Screenshots im Verzeichnis `screenshots` analysiert werden, um zu überprüfen, ob die erwarteten Ergebnisse eingetreten sind. Die Screenshots sind nach Datum und Uhrzeit sortiert und enthalten den Namen der Aktion, die ausgeführt wurde.

Für jeden Test gibt es eine Liste von erwarteten Ergebnissen, die überprüft werden sollten. Diese sind in der Dokumentation des jeweiligen Tests aufgeführt.

## Erweiterung der Tests

Um neue Tests zu entwickeln, folge diesen Schritten:

1. Erstelle eine neue Markdown-Datei im Verzeichnis `test_scenarios/` mit einer detaillierten Beschreibung des Tests
2. Erstelle eine neue JSON-Datei im Verzeichnis `test_json/` mit den Testanweisungen
3. Aktualisiere die Datei `test_plan.md`, um den neuen Test zu beschreiben
4. Führe den Test aus und analysiere die Ergebnisse

## Fehlerbehebung

Wenn ein Test nicht wie erwartet funktioniert, überprüfe Folgendes:

1. Stelle sicher, dass die JSON-Datei korrekt formatiert ist
2. Überprüfe, ob die Testanweisungen den richtigen Tasten entsprechen
3. Überprüfe, ob die Wartezeiten ausreichend sind
4. Überprüfe, ob das Spiel korrekt gestartet wurde

Wenn das Problem weiterhin besteht, überprüfe die Logdateien im Verzeichnis `logs/` für weitere Informationen.
