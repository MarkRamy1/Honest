# Start Honest AI 4.0 Platform (FastAPI Backend + React Vite Frontend)
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Launching Honest AI 4.0 (Backend + Frontend)..." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

# Ensure Node is accessible if in standard Program Files
if (-not (Get-Command npm -ErrorAction SilentlyContinue) -and (Test-Path "C:\Program Files\nodejs")) {
    $env:PATH = "C:\Program Files\nodejs;$env:PATH"
}

# 1. Launch FastAPI Backend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd '$PSScriptRoot\backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

# 2. Launch React Vite Frontend in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "`$env:PATH = 'C:\Program Files\nodejs;' + `$env:PATH; cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "Backend running at:  http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend running at: http://localhost:5173" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
