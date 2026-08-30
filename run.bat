@echo off
:: STORM GAMES INFO Launcher
:: This script runs the application with hidden console window

cd /d "%~dp0"

:: Check if Python exists
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python 3.10 or higher.
    pause
    exit /b 1
)

:: Run the application with pythonw to hide console
start "" pythonw stormgamesinfo.py

exit