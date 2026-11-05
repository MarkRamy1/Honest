# Architecture Audit: Honest AI Shopping & Forensic Research Platform

**Audit Date:** October 2026  
**Auditor:** Principal Software & Migration Architect  
**Project Workspace:** `d:/laravel/Honest`  
**Current State:** Laravel 12 (PHP 8.2) + Blade/Vanilla JS + Manifest V3 Chrome Extension + MySQL/SQLite  
**Target Architecture:** Python (FastAPI) + React (TypeScript + Vite) + PostgreSQL (SQLAlchemy 2.x + Alembic) + AI Agent (OpenAI Agents / Structured Tool-Calling Framework) + Preserved Manifest V3 Extension  

---

## 1. Executive Summary

Honest 4.0 is an AI-powered shopping research and forensic audit platform designed to protect consumers from deceptive e-commerce marketing, fake reviews, misleading studio lighting, and substandard replica materials across online retailers (Amazon, Noon, Shein, AliExpress, etc.).

The system currently consists of:
1. **Laravel Backend (`app/`, `routes/`, `database/`):** REST API providing AI search, visual reality analysis, intent classification, scoring engine, user authentication, catalog search, and community review storage.
2. **Web Frontend (`resources/views/welcome.blade.php`, `preview.blade.php`):** A ChatGPT-inspired dark-mode SPA built with vanilla JavaScript, featuring real-time conversational search, interactive tier comparisons (Original vs. High Copy vs. Budget Copy), dual currency ($ USD and ~EGP), user authentication modals, and settings.
3. **Chrome Extension (`extension/` and root duplicate):** Manifest V3 extension containing `background.js` (service worker), `content.js` (Shadow DOM injection on shopping sites with split-slider visual forensics and AI chat), and `style.css`.
4. **Documentation & Benchmarks:** Architecture audit, migration plan, security audit, and test scripts.

---

## 2. Existing Codebase Inventory

### 2.1 Directory Structure
```text
d:/laravel/Honest/
├── app/
│   ├── Http/Controllers/
│   │   ├── AuthController.php          # User registration, login, logout, me (session/token)
│   │   ├── CatalogController.php       # Product search and store reputation endpoints
│   │   ├── Controller.php              # Base Laravel controller
│   │   ├── HonestApiController.php     # Core API: health, vlm audit, reality gen, agent ask/search
│   │   ├── ReviewController.php        # Community reviews, review submission, upvotes
│   │   └── WebController.php           # Landing page, demo preview, zip download
│   ├── Models/
│   │   ├── Review.php                  # Review model with user_id, ratings, price_paid, upvotes
│   │   ├── StoreReputation.php         # Verified stores with trust scores and honesty ratings
│   │   ├── User.php                    # Standard Laravel user model with hashed passwords
│   │   └── VerifiedProduct.php         # Product catalog with real vs fake material specs
│   ├── Providers/
│   │   └── AppServiceProvider.php
│   └── Services/
│       ├── HonestAuditService.php      # Main coordinator for visual audits, Gemini calls, fallback heuristics
│       ├── IntentParserService.php     # Regex/NLP parser for queries, budgets, categories, use-cases
│       ├── ProductSearchService.php    # Multi-tier candidate discovery, ranking, avoidance
│       ├── ReviewSentimentService.php  # Buyer consensus, durability, flaw analysis
│       └── ScoringEngineService.php    # 4-component Value-for-Money (VFM) scoring algorithm
├── bootstrap/                          # Laravel 12 application bootstrap
├── config/                             # App, auth, database, cors, services config
├── database/
│   ├── migrations/
│   │   ├── 0001_01_01_000000_create_users_table.php
│   │   ├── 0001_01_01_000001_create_cache_table.php
│   │   ├── 0001_01_01_000002_create_jobs_table.php
│   │   ├── 2026_10_14_162448_create_personal_access_tokens_table.php
│   │   └── 2026_10_14_200000_create_reviews_and_catalog_tables.php
│   └── seeders/
│       └── DatabaseSeeder.php          # Realistic seed data for 6 verified products, reviews, stores
├── extension/                          # Browser extension package
│   ├── background.js                   # Service worker bridging extension messages to backend API
│   ├── content.js                      # Shadow DOM UI on shopping sites (split slider, audit, ask)
│   ├── manifest.json                   # Manifest V3 specification
│   └── style.css                       # Encapsulated styles for floating badge and modal
├── resources/
│   ├── css/app.css
│   ├── js/app.js, bootstrap.js
│   └── views/
│       ├── preview.blade.php           # Standalone testing stage with simulated product pages
│       └── welcome.blade.php           # Full ChatGPT-style web app (HTML + CSS + ~1000 lines JS)
├── routes/
│   ├── api.php                         # All REST API endpoints
│   ├── console.php
│   └── web.php                         # Web routes (/, /preview, /extension/download, /embed)
├── scratch/                            # Standalone test scripts (Node.js and PHP)
└── tests/                              # Standard starter feature/unit test stubs
```

---

## 3. Analysis of Existing Features & Implementation Reality

| Feature | Existing Implementation | Verification Status | Implementation Reality & Observations |
| :--- | :--- | :--- | :--- |
| **Health Check (`GET /api/health`)** | `HonestApiController::health` | **Verified Working** | Returns JSON status, version 4.0.0, capabilities list, timestamp. |
| **User Authentication (`/api/auth/*`)** | `AuthController.php` | **Verified Working** | Registration, login, logout, me. Uses Laravel session/cookie authentication. Password hashing via bcrypt (`BCRYPT_ROUNDS=12`). |
| **Catalog Search (`GET /api/catalog/search`)** | `CatalogController::search` | **Verified Working** | Queries `VerifiedProduct` table with `like %q%` filtering across name, brand, category. |
| **Store Reputation (`GET /api/catalog/stores`)** | `CatalogController::stores` | **Verified Working** | Returns ordered list of stores by `trust_score`. |
| **Community Reviews (`/api/reviews`)** | `ReviewController.php` | **Verified Working** | Paginated review listings, stats (avg rating, material accuracy), review creation with validation, upvotes. |
| **Intent Parsing** | `IntentParserService.php` | **Verified Working** | Classifies greeting, capability, gratitude, recommendation, product_audit; extracts budget ($ and EGP), category, use-cases. |
| **Value-for-Money Scoring** | `ScoringEngineService.php` | **Verified Working** | 4-part formula: 35% Quality & Specs, 30% Price Competitiveness, 25% Buyer Experience, 10% Brand & Warranty. Produces letter grades (A+ to D) and badges. |
| **Review Sentiment Synthesis** | `ReviewSentimentService.php` | **Verified Working** | Heuristic domain profiles for Audio, Laptops, Sneakers, Luxury Watches, and General Goods with durability metrics and flaws. |
| **Candidate Search & 3-Tier Classification** | `ProductSearchService.php` | **Verified Working** | Generates Top Value Pick, Premium Pick, Budget Pick, and What to Avoid for categories. |
| **Shopper Q&A (`POST /api/agent/ask`)** | `HonestAuditService::answerQuestion` | **Verified Working** | Combines intent parser, benchmark catalogs, Gemini API (when configured) or heuristic fallback to return 3-tier price matrix, material authenticity verdict, and buying links. |
| **Visual Forensics (`POST /api/vlm/audit`)** | `HonestAuditService::auditProduct` | **Partial / Heuristic** | Calls Gemini 1.5 Flash if `GEMINI_API_KEY` is present; falls back to deterministic heuristic audit if missing or on error. |
| **Reality Generation (`POST /api/vlm/generate-reality`)** | `HonestAuditService::generateReality` | **Heuristic / Mocked** | Returns prompt template and static Unsplash image URLs rather than live FLUX inference server. |
| **Social Search (`POST /api/agent/search`)** | `HonestAuditService::searchSocial` | **Heuristic / Mocked** | Returns synthetic TikTok unboxings with captions, Reddit threads, and Facebook posts. No live TikTok/Reddit scraping adapter. |
| **Browser Extension** | `extension/*` | **Verified Working** | Connects to `http://localhost:8000` through `background.js`. Injects into supported sites and `localhost`. |
| **Web Frontend** | `welcome.blade.php` | **Verified Working** | Pure browser-side state using `localStorage` for chat threads, custom Gemini key support, modal popups for auth/reviews, responsive sidebar. |

---

## 4. Extension & Web Communication Architecture

### 4.1 Extension Communication Flow
1. User navigates to e-commerce site or localhost demo stage.
2. `content.js` scans page metadata, OpenGraph tags, schema.org JSON-LD, or DOM selectors to extract product title, image, and price.
3. A floating glassmorphic badge is rendered inside a **Shadow DOM** to prevent CSS leakage.
4. When clicked, `content.js` sends messages via `chrome.runtime.sendMessage` to `background.js`:
   - `CHECK_AGENT_HEALTH` -> `GET /api/health`
   - `RUN_VISUAL_AUDIT` -> `POST /api/vlm/audit`
   - `ASK_HONEST_QUESTION` -> `POST /api/agent/ask`
   - `RUN_DEEP_SEARCH` -> `POST /api/agent/deep-search`
   - `COMPARE_IN_CART` -> `POST /api/agent/compare-in-cart`
   - `GET_RECOMMENDATIONS` -> `POST /api/agent/recommend`
5. `background.js` executes `fetch()` requests against `http://localhost:8000` and relays JSON responses back to `content.js`.
6. `content.js` updates the Shadow DOM UI (interactive split slider, scorecard, tier cards).

### 4.2 Web Application Communication Flow
1. `welcome.blade.php` communicates directly via browser `fetch()` to `/api/*` endpoints.
2. Chat history is stored exclusively in client `localStorage` (`honest_chat_threads_v1`), protecting user privacy.
3. User accounts and reviews communicate with `/api/auth/*` and `/api/reviews`.

---

## 5. Identified Technical Debt, Bugs & Inefficiencies

1. **Monolithic Blade Template:** `welcome.blade.php` is nearly 3,000 lines long, combining HTML structure, CSS custom properties, and ~1,000 lines of imperative JavaScript DOM manipulation. Migrating to React components will drastically improve maintainability, reactivity, and type safety.
2. **Duplicate Extension Code:** Identical copies of extension files (`manifest.json`, `background.js`, `content.js`, `style.css`) exist in the project root, in `extension/`, and in `public/extension/`. We will standardize on `extension/` as the single canonical source.
3. **Hardcoded API Base URL in Extension:** `background.js` contains `const AGENT_BASE_URL = 'http://localhost:8000';`. This should support environment-based configuration for development and production.
4. **Mocked/Heuristic Endpoints:** External reality generation and social video scraping currently return hardcoded templates and Unsplash images. The new Python agent architecture needs clean provider-adapter interfaces so live tools or mock adapters can be swapped transparently without breaking downstream callers.
5. **Database Engine Inconsistency:** `.env` specifies `DB_CONNECTION=mysql` with empty credentials, while code comments in `AuthController.php` and `api.php` refer to SQLite. The database needs a clean, unified PostgreSQL schema with SQLAlchemy 2.x and Alembic migrations.

---

## 6. Audit Conclusion & Readiness

The business logic, intent parsing heuristics, scoring formulas, material verification telltales, database seed datasets, and browser extension UI are solid and well-defined.

The project is fully prepared for Phase B: establishing the foundational backend (FastAPI + SQLAlchemy + Alembic), frontend (React + TypeScript + Vite), and extension adapter structures without touching or destroying the existing Laravel application.
