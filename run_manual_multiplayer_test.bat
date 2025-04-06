@echo off
echo PokeTogether Manueller Multiplayer-Test
echo ==========================
echo.
echo Dieser Test startet zwei Instanzen des Spiels:
echo 1. Eine Host-Instanz
echo 2. Eine Client-Instanz
echo.
echo Bitte stelle sicher, dass du genug Arbeitsspeicher hast, um zwei Spielinstanzen gleichzeitig auszuführen.
set /p confirm=Möchtest du fortfahren? (j/n):

if /i not "%confirm%"=="j" (
    echo Test abgebrochen.
    exit /b
)

echo.
echo Starte Host-Instanz...
start "PokeTogether Host" python src/main.py

echo.
echo Host-Instanz gestartet. Warte 5 Sekunden...
timeout /t 5 /nobreak > nul

echo.
echo Starte Client-Instanz...
start "PokeTogether Client" python src/main.py

echo.
echo Beide Instanzen laufen jetzt. Du kannst sie manuell steuern.
echo.
echo In der Host-Instanz:
echo 1. Wähle "Host Game" im Hauptmenü
echo 2. Warte, bis die Multiplayer-Session gestartet ist
echo.
echo In der Client-Instanz:
echo 1. Wähle "Join Game" im Hauptmenü
echo 2. Gib "localhost" als IP-Adresse ein
echo 3. Bestätige mit Enter
echo.
echo Drücke eine beliebige Taste, um die Tests zu beenden...
pause > nul

echo.
echo Beende die Tests...
taskkill /fi "WINDOWTITLE eq PokeTogether Host*" > nul
taskkill /fi "WINDOWTITLE eq PokeTogether Client*" > nul

echo.
echo Tests beendet.
