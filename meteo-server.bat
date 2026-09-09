@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Install it from https://www.python.org/downloads/ and try again.
  pause
  exit /b 1
)
start "" http://localhost:8765/
python serve.py site
