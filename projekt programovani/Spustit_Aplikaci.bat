@echo off
cd /d "%~dp0"

REM Spuštění backendu na pozadí (logujeme do backend\backend.log)
if not exist backend mkdir backend
start "AMP-Backend" /B cmd /c ".\.venv\Scripts\python.exe backend\app.py 1>>backend\backend.log 2>&1"

REM Počkej pár sekund než backend nastartuje
timeout /t 4 /nobreak >nul

REM Spuštění desktop aplikace (otevře se okno)
start "" .\.venv\Scripts\pythonw.exe fitness_app\main.py

exit
