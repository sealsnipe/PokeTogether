@echo off
echo PokeTogether Minimized Test
echo ========================
echo.

REM Überprüfe, ob ein Testtyp angegeben wurde
if "%1"=="" (
    echo Bitte gib einen Testtyp an: movement, action, menu oder comprehensive
    echo Beispiel: run_minimized_test.bat movement
    exit /b 1
)

REM Starte das Spiel minimiert mit dem angegebenen Test
python src/main.py --minimized --test %1

echo.
echo Test abgeschlossen. Überprüfe die Screenshots im screenshots-Verzeichnis.
echo.
