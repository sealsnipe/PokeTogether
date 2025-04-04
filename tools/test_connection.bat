@echo off
echo WebSocket-Verbindungstest
echo =======================
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
pip install websockets

echo.
echo Pakete installiert.
echo.

echo Wähle eine Option:
echo 1. Server starten
echo 2. Client starten
echo.

set /p option="Option (1 oder 2): "

if "%option%"=="1" (
    echo.
    echo Server wird gestartet...
    echo.
    python tools/test_server.py
) else if "%option%"=="2" (
    echo.
    echo Client wird gestartet...
    echo.
    python tools/test_client.py
) else (
    echo.
    echo Ungültige Option!
    echo.
)

echo.
echo Test beendet.
pause
