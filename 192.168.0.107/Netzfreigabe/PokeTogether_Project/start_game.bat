@echo off
echo PokeTogether Starter
echo =================
echo.

REM Starte das Spiel
cd /d %~dp0
python src\main.py

echo.
echo Spiel beendet.
pause
