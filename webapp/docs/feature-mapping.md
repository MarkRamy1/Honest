# Feature Mapping: Laravel 12 to Python FastAPI + React

This document maps all existing Laravel components to their new Python/FastAPI backend, React frontend, and SQLAlchemy database implementation.

---

## 1. API Route & Controller Mapping

| Laravel Route | Laravel Controller & Action | New FastAPI Route | New Python Module & Function | Request/Response Compatibility |
| :--- | :--- | :--- | :--- | :--- |
| `GET /api/health` | `HonestApiController@health` | `GET /api/health` | `backend/app/api/routes/health.py::get_health` | 100% Identical JSON schema |
| `POST /api/vlm/audit` | `HonestApiController@audit` | `POST /api/vlm/audit` | `backend/app/api/routes/vlm.py::audit_product` | Accepts both camelCase and snake_case |
| `POST /api/vlm/generate-reality` | `HonestApiController@generateReality` | `POST /api/vlm/generate-reality` | `backend/app/api/routes/vlm.py::generate_reality` | 100% Identical JSON schema |
| `GET /api/models` / `GET /api/agent/models` | `HonestApiController@models` | `GET /api/agent/models` & `GET /api/models` | `backend/app/api/routes/agent.py::get_models` | 100% Identical JSON schema |
| `POST /api/agent/search` | `HonestApiController@search` | `POST /api/agent/search` | `backend/app/api/routes/agent.py::search_social` | 100% Identical JSON schema |
| `POST /api/agent/ask` | `HonestApiController@ask` | `POST /api/agent/ask` | `backend/app/api/routes/agent.py::ask_agent` | Returns 3-tier price matrix & material verdict |
| `POST /api/agent/deep-search` | `HonestApiController@deepSearch` | `POST /api/agent/deep-search` | `backend/app/api/routes/agent.py::deep_search` | Identical format with dual currency ($/EGP) |
| `POST /api/agent/alternatives` | `HonestApiController@alternatives` | `POST /api/agent/alternatives` | `backend/app/api/routes/agent.py::get_alternatives` | 100% Identical JSON schema |
| `POST /api/agent/recommend` | `HonestApiController@recommend` | `POST /api/agent/recommend` | `backend/app/api/routes/agent.py::recommend_products` | 100% Identical JSON schema |
| `POST /api/agent/compare-in-cart` | `HonestApiController@compareInCart` | `POST /api/agent/compare-in-cart` | `backend/app/api/routes/agent.py::compare_in_cart` | 100% Identical JSON schema |
| `GET /api/reviews` | `ReviewController@index` | `GET /api/reviews` | `backend/app/api/routes/reviews.py::get_reviews` | Paginated reviews with aggregate stats |
| `POST /api/reviews` | `ReviewController@store` | `POST /api/reviews` | `backend/app/api/routes/reviews.py::create_review` | Validated via Pydantic schema |
| `POST /api/reviews/{id}/upvote` | `ReviewController@upvote` | `POST /api/reviews/{id}/upvote` | `backend/app/api/routes/reviews.py::upvote_review` | Increments upvotes |
| `GET /api/catalog/search` | `CatalogController@search` | `GET /api/catalog/search` | `backend/app/api/routes/catalog.py::search_catalog` | Searches verified products |
| `GET /api/catalog/stores` | `CatalogController@stores` | `GET /api/catalog/stores` | `backend/app/api/routes/catalog.py::get_stores` | Returns store reputation list |
| `POST /api/auth/register` | `AuthController@register` | `POST /api/auth/register` | `backend/app/api/routes/auth.py::register` | Creates user, returns JWT & user object |
| `POST /api/auth/login` | `AuthController@login` | `POST /api/auth/login` | `backend/app/api/routes/auth.py::login` | Verifies bcrypt password, returns JWT |
| `POST /api/auth/logout` | `AuthController@logout` | `POST /api/auth/logout` | `backend/app/api/routes/auth.py::logout` | Revokes session / clears auth cookie |
| `GET /api/auth/me` | `AuthController@me` | `GET /api/auth/me` | `backend/app/api/routes/auth.py::get_current_user` | Dependency injection via `get_current_user` |
| `GET /embed` | `HonestApiController@embed` | `GET /embed` | `backend/app/api/routes/embed.py::embed_player` | Returns HTML video player relay |
| `GET /preview` | `WebController@preview` | Handled by React Frontend (`/preview`) or static test stage | `frontend/src/pages/PreviewPage.tsx` | Interactive product card stage |
| `GET /extension/download` | `WebController@downloadExtension` | `GET /extension/download` | `backend/app/api/routes/extension.py::download_extension` | Serves zipped extension archive |

---

## 2. Business Services Mapping

| Laravel Service | New Python Service Module | Core Capabilities & Logic Retained |
| :--- | :--- | :--- |
| `IntentParserService` | `backend/app/services/intent_parser.py` | Detects greetings, capabilities, gratitude, recommendation, and product audit; extracts USD and EGP budgets; classifies 10+ categories; parses use cases; cleans product queries. |
| `ScoringEngineService` | `backend/app/services/scoring_engine.py` | Calculates Value-for-Money (VFM) composite score with 4 weighted criteria; determines letter grades (A+ to D) and consumer badges; generates score summary; in-cart product comparison. |
| `ReviewSentimentService` | `backend/app/services/review_sentiment.py` | Durability scores, 1-year survival longevity metrics, low/medium/high return risks, verified pros, critical flaws, buyer consensus across categories. |
| `ProductSearchService` | `backend/app/services/product_search.py` | Candidate pool matching, 3-tier classification (Top Value Pick, Premium Pick, Budget Pick, What to Avoid), dual currency calculations. |
| `HonestAuditService` | `backend/app/services/honest_audit.py` & `backend/app/agents/orchestrator.py` | Gemini VLM live integration, fallback heuristics, 3-tier price matrix generation, material truth comparisons, dual-currency formatting. |

---

## 3. Database Models & Schema Mapping

| Laravel Model & Table | New SQLAlchemy 2.0 Model | New Table in PostgreSQL | Key Columns & Types |
| :--- | :--- | :--- | :--- |
| `User` (`users`) | `backend/app/models/user.py::User` | `users` | `id` (Integer/BigInt PK), `name` (String), `email` (String Unique), `hashed_password` (String), `created_at`, `updated_at`. |
| `VerifiedProduct` (`verified_products`) | `backend/app/models/product.py::VerifiedProduct` | `verified_products` | `id`, `name`, `brand`, `category`, `original_msrp` (Numeric), `high_copy_avg_price`, `copy_avg_price`, `authentic_materials` (Text), `fake_materials` (Text), `verification_telltales` (JSONB), `recommended_sources` (JSONB), timestamps. |
| `StoreReputation` (`stores_reputation`) | `backend/app/models/store.py::StoreReputation` | `stores_reputation` | `id`, `store_name`, `platform`, `specialty_tier`, `trust_score` (SmallInt), `material_honesty_rating` (Numeric), `verified_url`, `notes`, timestamps. |
| `Review` (`reviews`) | `backend/app/models/review.py::Review` | `reviews` | `id`, `user_id` (FK nullable), `user_name`, `product_name`, `brand`, `category`, `tier`, `rating`, `material_accuracy_rating`, `price_paid`, `store_purchased_from`, `product_url`, `comment`, `is_verified_buyer`, `upvotes`, timestamps. |
| *New:* `SearchSession` | `backend/app/models/search.py::SearchSession` | `search_sessions` | `id` (UUID), `user_id` (FK nullable), `query`, `category`, `budget_usd`, `created_at`. Optional opt-in persistence. |

---

## 4. Frontend Component Mapping

| Existing Blade View / DOM Section | New React Component | Responsibilities & State |
| :--- | :--- | :--- |
| `resources/views/welcome.blade.php` | `frontend/src/App.tsx` & `frontend/src/layouts/AppLayout.tsx` | Application shell, theme providers, responsive layout container |
| Left Sidebar (`.sidebar`, `#sidebar`) | `frontend/src/components/Sidebar.tsx` | New Chat button, chat history threads from `localStorage`, tier selector, mobile drawer |
| Quality Tier Pills (`.tier-pills-vertical`) | `frontend/src/components/TierSelector.tsx` | Original vs High Copy vs Budget Copy selection |
| Chat Viewport (`#chat-area`, `#messages-container`) | `frontend/src/components/ChatViewport.tsx` | Scroll container, empty state greeting, message stream |
| Message Bubbles (`.message-row.user`, `.message-row.ai`) | `frontend/src/components/MessageItem.tsx` | User bubble & AI response formatting |
| Material Verdict Card (`.material-verdict-card`) | `frontend/src/components/MaterialVerdictCard.tsx` | Genuine vs replica material comparison, telltales list |
| 3-Tier Pricing Matrix (`.pricing-matrix-container`) | `frontend/src/components/PricingMatrix.tsx` | Original, High-Copy, Budget-Copy pricing cards, dual currency ($/EGP), source buttons |
| In-Cart Real-Time Advisor | `frontend/src/components/InCartAdvisor.tsx` | Scanned product vs top alternative comparison with savings banner |
| Auth Modal (`#modal-auth`) | `frontend/src/components/AuthModal.tsx` | Sign in / register forms, demo credential loader, validation feedback |
| Reviews & Catalog Modal (`#modal-reviews`) | `frontend/src/components/ReviewsModal.tsx` | Live review feed from `/api/reviews`, aggregate stats, new review form |
| Settings Modal (`#modal-settings`) | `frontend/src/components/SettingsModal.tsx` | Custom Gemini API key storage in `localStorage`, purge local chats |
| Topbar & User Menu (`#topbar-user-menu`) | `frontend/src/components/Topbar.tsx` | Language toggle (EN/AR), sign-in button, user profile dropdown |
| Standalone Preview (`preview.blade.php`) | `frontend/src/pages/PreviewPage.tsx` | Demo stage with sample product listings for testing the extension |

---

## 5. Browser Extension Message Mapping

| Extension Message Action (`request.action`) | Existing Laravel Handler | New FastAPI Endpoint | Response Contract |
| :--- | :--- | :--- | :--- |
| `CHECK_AGENT_HEALTH` | `GET /api/health` | `GET /api/health` | `{ status: "online", version: "4.0.0", ... }` |
| `RUN_VISUAL_AUDIT` | `POST /api/vlm/audit` | `POST /api/vlm/audit` | `{ success: true, audit: { ... } }` |
| `GENERATE_REALITY_IMAGE` | `POST /api/vlm/generate-reality` | `POST /api/vlm/generate-reality` | `{ success: true, prompt: ... }` |
| `ASK_HONEST_QUESTION` | `POST /api/agent/ask` | `POST /api/agent/ask` | `{ success: true, answer: ..., material_verdict: ..., price_matrix: ... }` |
| `RUN_DEEP_SEARCH` | `POST /api/agent/deep-search` | `POST /api/agent/deep-search` | `{ success: true, deep_search: ... }` |
| `GET_ALTERNATIVES` | `POST /api/agent/alternatives` | `POST /api/agent/alternatives` | `{ success: true, alternatives: [ ... ] }` |
| `COMPARE_IN_CART` | `POST /api/agent/compare-in-cart` | `POST /api/agent/compare-in-cart` | `{ success: true, comparison: ... }` |
| `GET_RECOMMENDATIONS` | `POST /api/agent/recommend` | `POST /api/agent/recommend` | `{ success: true, recommendation: ... }` |
| `SEARCH_SOCIAL_AGENT` | `POST /api/agent/search` | `POST /api/agent/search` | `{ success: true, discoveredPosts: [ ... ] }` |
