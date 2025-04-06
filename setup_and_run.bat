@echo off
echo PokeTogether Setup und Start
echo ===========================
echo.

REM Prüfen, ob Python installiert ist
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python ist nicht installiert. Bitte installiere Python 3.13 von:
    echo https://www.python.org/downloads/
    echo.
    echo Stelle sicher, dass du "Add Python to PATH" während der Installation aktivierst.
    echo.
    echo Drücke eine beliebige Taste, um den Browser zu öffnen...
    pause > nul
    start https://www.python.org/downloads/
    echo Starte dieses Skript erneut, nachdem Python installiert wurde.
    pause
    exit
)

echo Python ist installiert. Installiere notwendige Pakete...
echo.

REM Installiere notwendige Pakete
pip install pygame websockets

echo.
echo Pakete installiert. Starte das Spiel...
echo.

REM Erstelle lokales Verzeichnis für das Spiel
set "LOCAL_DIR=%USERPROFILE%\PokeTogether"
echo Erstelle lokales Verzeichnis: %LOCAL_DIR%

if not exist "%LOCAL_DIR%" mkdir "%LOCAL_DIR%"
if not exist "%LOCAL_DIR%\src" mkdir "%LOCAL_DIR%\src"

REM Kopiere die EXE-Datei ins lokale Verzeichnis
echo Kopiere PokeTogether_debug.exe ins lokale Verzeichnis...
copy "%~dp0PokeTogether_debug.exe" "%LOCAL_DIR%\"

REM Starte die EXE-Datei
echo Starte PokeTogether_debug.exe...
cd /d "%LOCAL_DIR%"
start "" "%LOCAL_DIR%\PokeTogether_debug.exe"

echo.
echo Spiel gestartet. Du kannst dieses Fenster jetzt schließen.
pause
