# Application Security Plan & Hardening Architecture

**Version:** 1.0.0  
**Target:** Honest AI Shopping Research Platform (FastAPI + React + PostgreSQL + Extension)  

---

## 1. Threat Modeling & Scope

The Honest AI platform processes user search queries, product URLs, external retailer listings, consumer reviews, and AI model prompts. The threat model encompasses five primary vectors:
1. **Authentication & Session Hijacking:** Brute-force attacks against user credentials, insecure token handling, or credential reuse.
2. **Untrusted External Content & Prompt Injection:** External page contents, user-submitted reviews, or retailer product descriptions attempting to manipulate agent decision-making.
3. **Server-Side Request Forgery (SSRF):** Exploitation of image fetching or store URL verification to probe private network addresses.
4. **Browser Extension Privilege Escalation:** Malicious websites attempting to send unauthorized messages to the extension's service worker or abuse permissions.
5. **Data & Secret Leakage:** Accidental exposure of LLM API keys, database credentials, or detailed internal stack traces in HTTP responses or client code.

---

## 2. Authentication & Credential Security

### 2.1 Password Hashing Compatibility
- **Existing Scheme:** Laravel 12 uses `bcrypt` with cost factor 12 (`BCRYPT_ROUNDS=12`).
- **Python Implementation:** Python `passlib` with `bcrypt` backend (`passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")`).
- **Compatibility Guarantee:** Passwords created in Laravel can be verified directly in Python without forcing an immediate password reset. When users log in, the password hash is verified against the bcrypt standard.

### 2.2 Token & Session Architecture
- Stateless JWT tokens (HMAC-SHA256) issued upon `/api/auth/login` or `/api/auth/register`.
- Tokens contain standard claims: `sub` (User ID), `email`, `iat` (Issued At), `exp` (Expiration, default 7 days).
- Tokens transmitted via `Authorization: Bearer <token>` header or HttpOnly secure cookies.
- FastAPI dependency injection (`get_current_user` and `get_optional_user`) validates signature and checks database record existence.

### 2.3 User Data Isolation & Ownership
- Community reviews are publicly readable, but modifications or deletions require verified ownership (`review.user_id == current_user.id`).
- Private search histories (when opted-in for persistence) are strictly scoped to the authenticated user ID (`where user_id = current_user.id`).
- Chat sessions remain in client-side `localStorage` by default, guaranteeing zero server-side exposure of user conversation logs.

---

## 3. API Security & Transport Defense

### 3.1 CORS (Cross-Origin Resource Sharing)
- Explicitly restricted to authorized origins:
  - Frontend development server: `http://localhost:5173`, `http://127.0.0.1:5173`
  - Production web origins: Configured via `CORS_ORIGINS` in `.env`
  - Browser extension: Extension origin or matching host permissions in Manifest V3
- Disallow wildcard `*` with credentials enabled.

### 3.2 Rate Limiting
- Rate limits applied via middleware on critical routes:
  - `/api/auth/login` & `/api/auth/register`: 10 requests / minute per IP to prevent brute-forcing.
  - `/api/agent/ask`, `/api/agent/deep-search`: 30 requests / minute per IP / user to prevent AI budget depletion and denial-of-service.
  - `/api/vlm/audit`: 20 requests / minute.

### 3.3 Safe Error Responses
- In production (`APP_ENV=production`), generic user-facing error messages are returned with an error code and timestamp.
- Detailed Python tracebacks and internal database exceptions are never exposed to clients.
- Structured logging masks sensitive keys (`authorization`, `api_key`, `password`, `token`).

---

## 4. AI Agent & Tool Execution Safeguards

### 4.1 Untrusted Input & Prompt Injection Defenses
- Treat all retrieved web content, retailer descriptions, and user reviews as untrusted input.
- External descriptions are sanitized and fed into prompt templates within isolated structural boundaries (`<untrusted_content>...</untrusted_content>`).
- System instructions enforce:
  1. The agent never executes arbitrary system commands, shell scripts, or raw SQL queries.
  2. The agent never conducts financial transactions, automatic checkout, or payment approvals.
  3. External text cannot override system instructions or alter tool parameters.

### 4.2 SSRF (Server-Side Request Forgery) Protection
- When fetching external product pages or image URLs:
  - Restrict URL schemes to `http` and `https`.
  - Block internal/private IP ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254` AWS metadata).
  - Enforce request timeouts (maximum 8 seconds per external fetch).
  - Limit response payload sizes to prevent memory exhaustion (maximum 5MB).

---

## 5. Browser Extension Security

### 5.1 Principle of Least Privilege
- Manifest permissions are strictly limited to `activeTab` and `storage`.
- Host permissions are limited to explicit retailers (`amazon.com`, `amazon.eg`, `noon.com`, `shein.com`, `aliexpress.com`, `localhost`).
- No broad `<all_urls>` permission.

### 5.2 Message Sender Validation
- Service worker (`background.js`) validates that incoming runtime messages originate from the extension's own content scripts or options page.
- Arbitrary web pages cannot directly invoke background actions.
- Content script executes inside an isolated world and renders UI inside a **Shadow DOM** with closed style encapsulation.

---

## 6. Secret Management & Compliance

1. Real secrets (e.g., `GEMINI_API_KEY`, `POSTGRES_PASSWORD`, `SECRET_KEY`) reside exclusively in local uncommitted `.env` files.
2. A clean `.env.example` file is maintained with placeholder values and descriptive documentation.
3. Git commits are screened to ensure no production keys or confidential tokens are committed.
