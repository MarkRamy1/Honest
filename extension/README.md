# Honest AI 4.0 — Chrome Browser Extension

This folder contains the standalone, unpacked Google Chrome extension for **Honest AI 4.0**.

---

## 🚀 How to Install in Google Chrome

1. Open **Google Chrome** on your computer.
2. In the URL address bar, enter:
   ```text
   chrome://extensions
   ```
3. In the top-right corner, turn **ON** the **Developer mode** toggle.
4. In the top-left corner, click **Load unpacked**.
5. In the file picker dialog, select this folder:
   ```text
   D:\Honest\extension
   ```
6. The extension **Honest 4.0 - Generative AI Visual Reality & Multi-Modal Product Auditor** is now installed and active!

---

## 🛒 Supported Shopping Platforms
The extension automatically audits listings on:
- **Amazon** (`amazon.com`, `amazon.eg`)
- **Noon** (`noon.com`)
- **Shein** (`shein.com`)
- **AliExpress** (`aliexpress.com`)
- **Local Dev / Testing** (`localhost`, `127.0.0.1`)

---

## ⚙️ Backend Connection
The extension communicates with the Honest AI backend server at:
```text
http://127.0.0.1:8000
```
Make sure the webapp backend is running (via `start_dev.bat` inside the `webapp` folder) to enable live AI multimodal analysis and image verification.

---

## 📁 Files Included
- `manifest.json`: Manifest V3 extension configuration with host permissions.
- `background.js`: Service worker handling API calls, authentication, and offline caching.
- `content.js`: Injects the Honest AI floating badge, visual reality modal, and material audit card on e-commerce product pages.
- `style.css`: Clean, high-fidelity styles matching the Honest AI design system.
