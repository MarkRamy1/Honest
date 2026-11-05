# Honest AI 4.0 — Project Directory

Welcome to **Honest AI 4.0**! The project is divided into two distinct, dedicated folders as requested:

---

## 📁 Project Structure

```text
D:\Honest\
├── extension/          ← [CHROME EXTENSION] Ready to be loaded into Google Chrome
│   ├── manifest.json   ← Manifest V3 specification
│   ├── background.js   ← Background service worker
│   ├── content.js      ← On-page auditor and reality studio modal
│   ├── style.css       ← Extension stylesheet
│   └── README.md       ← Instructions for loading unpacked in Chrome
│
└── webapp/             ← [WEB APPLICATION] Run directly on your device
    ├── backend/        ← FastAPI Python backend (Port 8000)
    │   ├── app/        ← Endpoints, models, services, scoring engine
    │   ├── tests/      ← Pytest automated test suite (39 passing)
    │   └── .venv/      ← Virtual environment
    ├── frontend/       ← React 18 + TypeScript + Vite UI (Port 5173)
    │   ├── src/        ← Google Stitch design system, Light & Dark themes, Arabic i18n
    │   └── dist/       ← Production build
    ├── start_dev.bat   ← One-click runner for Windows (Backend + Frontend)
    ├── start_dev.ps1   ← PowerShell runner (with -ExecutionPolicy Bypass)
    ├── docker-compose.yml
    └── README.md       ← Detailed guide to running the web application
```

---

## ⚡ Quick Start

### 1. Load the Chrome Extension
1. Open Chrome and go to `chrome://extensions`.
2. Toggle on **Developer mode** in the top right.
3. Click **Load unpacked** in the top left.
4. Select the folder: `D:\Honest\extension`.

### 2. Run the Web Application
Simply double-click:
```text
D:\Honest\webapp\start_dev.bat
```
Or in PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File D:\Honest\webapp\start_dev.ps1
```
- Open your browser to: **[http://localhost:5173](http://localhost:5173)**
- Backend API Docs: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
- Toggle between **Light Mode** and **Dark Mode** anytime using the Sun/Moon button in the top navigation bar!
