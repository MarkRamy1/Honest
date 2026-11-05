@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting Honest AI 4.0 Platform (Backend + Frontend)...
echo ========================================================

set "PATH=C:\Program Files\nodejs;%PATH%"

:: 1. Start Python FastAPI Backend on port 8000 in a new window
echo Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Honest Backend (FastAPI)" cmd /k "cd /d ""%~dp0backend"" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

:: 2. Wait 2 seconds
timeout /t 2 /nobreak >nul

:: 3. Start React Vite Frontend on port 5173 in a new window
echo Starting React Vite Frontend on http://localhost:5173 ...
start "Honest Frontend (React + Vite)" cmd /k "cd /d ""%~dp0frontend"" && npm.cmd run dev"

echo.
echo ========================================================
echo Both servers are launching!
echo Web Application: http://localhost:5173
echo API Docs:        http://127.0.0.1:8000/docs
echo ========================================================
