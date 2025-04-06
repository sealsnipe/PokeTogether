@echo off
echo PokeTogether Multiplayer Test
echo ==========================
echo.

echo Dieser Test startet einen Server und zwei Client-Instanzen:
echo 1. Ein Server, der die Multiplayer-Verbindungen verwaltet
echo 2. Client 1 (Player1), der sich mit dem Server verbindet
echo 3. Client 2 (Player2), der sich mit dem Server verbindet
echo.
echo Der Test überprüft automatisch, ob beide Clients erfolgreich eine Verbindung zum Server herstellen können.
echo.

REM Frage den Benutzer, ob er fortfahren möchte
set /p continue=Möchtest du fortfahren? (j/n):
if /i not "%continue%"=="j" (
    echo Test abgebrochen.
    exit /b 0
)

echo.
echo Starte automatisierten Multiplayer-Test...
echo.

REM Starte den automatisierten Test
python test_local_multiplayer.py %*
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% == 0 (
    echo TEST ERFOLGREICH: Beide Clients haben erfolgreich eine Verbindung zum Server hergestellt!
) else (
    echo TEST FEHLGESCHLAGEN: Es gab Probleme bei der Verbindung zum Server. Fehlercode: %EXIT_CODE%
    echo Bitte überprüfe die Testberichte im Verzeichnis test_logs für weitere Details.
)

echo.
echo Drücke eine beliebige Taste, um fortzufahren...
pause > nul
