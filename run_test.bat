@echo off
echo PokeTogether Test Runner
echo ======================
echo.

REM Überprüfe, ob ein Testtyp angegeben wurde
if "%1"=="" (
    echo Bitte gib einen Testtyp an: main_menu, options_menu, player_movement oder ingame_menu
    echo Beispiel: run_test.bat main_menu
    exit /b 1
)

REM Kopiere die Testdatei in das input_instructions-Verzeichnis
echo Kopiere Testdatei %1...
copy test_documentation\test_json\%1_test.json input_instructions\current_test.json

REM Starte das Spiel minimiert
echo Starte das Spiel minimiert...
python src/main.py --minimized

echo.
echo Test abgeschlossen. Überprüfe die Screenshots im screenshots-Verzeichnis.
echo.
