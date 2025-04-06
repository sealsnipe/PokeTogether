@echo off
echo PokeTogether Autonomous Testing
echo ==============================
echo.

REM Install required dependencies if not already installed
pip install pygame watchdog

REM Run the automated test
python tools/run_automated_test.py %*

echo.
echo Test completed. Check the test_env/reports directory for analysis reports.
pause
