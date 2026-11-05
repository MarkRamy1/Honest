# Honest AI 4.0 — Web Application

This folder contains the complete, standalone **Honest AI 4.0** Web Application (`backend/` + `frontend/`) designed to be run directly on your device.

---

## 🚀 Quick Start (One-Click)

### Option 1: Double-Click Batch File (Recommended for Windows)
Simply double-click:
```text
start_dev.bat
```
This automatically launches both:
1. **Python FastAPI Backend** on `http://127.0.0.1:8000`
2. **React 18 + Vite Frontend** on `http://localhost:5173`

### Option 2: Run via PowerShell
If PowerShell script execution is restricted on your system, run:
```powershell
powershell -ExecutionPolicy Bypass -File .\start_dev.ps1
```

---

## 🌐 URLs
- **Web App Dashboard:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Backend Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🎨 Theme & Language Features
- **Light & Dark Mode:** Toggle easily via the sun/moon button in the top navigation bar.
  - **Light Mode:** High-fidelity Google Stitch aesthetic with soft mint & indigo tints, crisp cards, and deep navy headings.
  - **Dark Mode:** Crafted with the exact same visual hierarchy, deep midnight slate background, subtle glow accents, and readable slate typography.
- **Bilingual (English & Arabic):** Instant toggle with full bidirectional RTL support.

---

## 🛠 Manual Execution

### Backend
```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
To run tests:
```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

### Frontend
```powershell
cd frontend
npm run dev
```
To build for production:
```powershell
cd frontend
cmd.exe /c "npm run build"
```
