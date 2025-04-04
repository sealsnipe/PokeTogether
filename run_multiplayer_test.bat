@echo off
echo PokeTogether Multiplayer Test
echo ==========================
echo.

echo Dieser Test startet zwei Instanzen des Spiels:
echo 1. Eine Host-Instanz, die eine Multiplayer-Session hostet
echo 2. Eine Client-Instanz, die sich mit der Host-Instanz verbindet
echo.
echo Bitte stelle sicher, dass du genug Arbeitsspeicher hast, um zwei Spielinstanzen gleichzeitig auszuführen.
echo.

REM Frage den Benutzer, ob er fortfahren möchte
set /p continue=Möchtest du fortfahren? (j/n):
if /i not "%continue%"=="j" (
    echo Test abgebrochen.
    exit /b 0
)

echo.
echo Starte Host-Instanz...
echo.

REM Kopiere die Host-Testdatei in das input_instructions-Verzeichnis
copy test_documentation\test_json\multiplayer_host_test.json input_instructions\current_test.json

REM Starte die Host-Instanz minimiert
start /min "PokeTogether Host" python src/main.py --minimized

echo Host-Instanz gestartet. Warte 10 Sekunden, damit die Host-Instanz die Multiplayer-Session starten kann...
timeout /t 10 /nobreak > nul

echo.
echo Starte Client-Instanz...
echo.

REM Kopiere die Client-Testdatei in das input_instructions-Verzeichnis
copy test_documentation\test_json\multiplayer_client_test.json input_instructions\current_test.json

REM Starte die Client-Instanz minimiert
start /min "PokeTogether Client" python src/main.py --minimized

echo Client-Instanz gestartet.
echo.
echo Beide Instanzen laufen jetzt. Die Tests werden automatisch ausgeführt.
echo Überprüfe die Screenshots im screenshots-Verzeichnis, um die Ergebnisse zu sehen.
echo.
echo Drücke eine beliebige Taste, um die Tests zu beenden...
pause > nul

echo Beende die Tests...
taskkill /FI "WINDOWTITLE eq PokeTogether Host" /F
taskkill /FI "WINDOWTITLE eq PokeTogether Client" /F

echo.
echo Tests beendet. Überprüfe die Screenshots im screenshots-Verzeichnis.
echo.
