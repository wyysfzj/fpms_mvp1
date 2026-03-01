# AI‑EOS PROMPT — FE‑0‑01
## Title
FE‑0‑01: Auth + Session + normalized API client + guarded routes (closed loop)

## Context
Repository is FPMS MVP1 frontend (Vue3 + TS + Pinia + Element Plus + Vite). Backend is stable and must be honored:
- Base URL: `http://localhost:8000/api/v1`
- Auth: JWT Bearer token
- Errors envelope: `{ "error": { "code", "message", "details" } }`
- Pagination: `{ items, page, page_size, total }`
- Common statuses: 401/403/422/409

Assume FE‑0‑00 is complete and `lint/typecheck/build` gates exist and pass.

## Objective (Closed-loop)
Implement a working login + session + API call flow:
1) User can log in via UI, store token in localStorage, and keep session after refresh.
2) All HTTP calls go through a shared axios client:
   - baseURL from `VITE_API_BASE_URL` (must include `/api/v1`)
   - inject `Authorization: Bearer <token>`
   - normalize backend error envelope into a consistent `ApiError`
   - capture `X-Request-ID` header (if present) into `ApiError.requestId`
3) Router guard:
   - unauthenticated access to protected routes redirects to `/login`
   - authenticated user visiting `/login` redirects to `/dashboard`
4) Create/adjust a protected page (Dashboard) that calls a protected endpoint (smoke):
   - `GET /clients?page=1&page_size=1`
   - Show success (total/items) or empty state
5) Provide curl-based verification steps and an Evidence Log.

## Non‑Goals (hard constraints)
- Do NOT implement full layout polish or RBAC navigation (that is FE‑1).
- Do NOT implement CRUD pages (that is FE‑2).
- Do NOT add heavy dependencies.

## File Allowlist (ONLY modify/add these)
- `.env.example` (update; keep as example)
- optional local `.env` (only if required for dev; keep minimal)
- `src/api/http.ts`
- `src/api/types.ts` (add or update)
- `src/api/errors.ts` (add)
- `src/stores/auth.ts` (add)
- `src/router/index.ts`
- `src/modules/auth/pages/Login.vue`
- `src/modules/dashboard/pages/Dashboard.vue`
- `src/main.ts` (only if required for boot-time restore / unauthorized handling)
- Evidence Log output:
  - `task/frontend/FE-0/FE-0-01_evidence.md` (add; create directories if missing)

If you believe additional files are required, STOP and output a *new smallest atomic fix task* with its own allowlist. Do not proceed.

## Implementation Requirements (Detailed)
### A) Environment config
- Update `.env.example` so:
  - `VITE_API_BASE_URL=http://localhost:8000/api/v1`

### B) Shared types
Create `src/api/types.ts` including:
- `ErrorEnvelope` type for `{ error: { code, message, details } }`
- `Pagination<T>` type for `{ items, page, page_size, total }`
- `ApiError` normalized type: `{ status, code, message, details?, requestId? }`

### C) Error normalization
Create `src/api/errors.ts`:
- Function to normalize axios errors:
  - Prefer backend envelope fields when available
  - Fallback to generic message if not in envelope
  - Extract `X-Request-ID` (axios headers are lowercased)
- Ensure the normalized error is safe to display (string message).

### D) Axios client
Update `src/api/http.ts`:
- `baseURL` should equal `import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'`
- Request interceptor:
  - read token from localStorage key `fpms_token`
  - set `Authorization` header
- Response interceptor:
  - on error: normalize with `normalizeApiError`
  - on `401`: remove token from localStorage and trigger a global unauthorized signal
    - IMPORTANT: avoid circular imports between http/auth/router
    - Use a simple event mechanism:
      - `window.dispatchEvent(new CustomEvent('fpms:unauthorized'))`
  - then reject with normalized error

### E) Auth store (Pinia)
Create `src/stores/auth.ts`:
- State:
  - `token: string | null` (hydrate from localStorage at startup)
  - `isAuthenticated: boolean` derived
- Actions:
  - `login(username, password)`:
    - POST `/auth/login`
    - store token in state + localStorage
  - `logout()`:
    - clear state + localStorage
- Keep store independent from router (no router imports). Routing is handled by UI/guards.

### F) Router guards
Update `src/router/index.ts`:
- Ensure there is a usable default route:
  - `/` should redirect to `/dashboard`
- Add `meta.requiresAuth` to routes that need auth (everything under MainLayout).
- Global `beforeEach`:
  - if route requires auth and no token → redirect `/login`
  - if navigating to `/login` and already authenticated → redirect `/dashboard`

### G) Boot-time restore + unauthorized redirect
Update `src/main.ts` (if needed):
- Ensure token is restored (either via auth store initial state or explicit call).
- Listen to `fpms:unauthorized` event:
  - if current route is not `/login`, redirect to `/login`

### H) Login page wiring
Update `Login.vue`:
- Use auth store `login()`
- On success: route push `/dashboard`
- On failure: display error message (and include requestId if present)

### I) Dashboard smoke
Update `Dashboard.vue`:
- On mount, call `GET /clients?page=1&page_size=1`
- Show:
  - loading state
  - success state (e.g., total + first item if exists)
  - error state (message + requestId)
This page is the proof that token injection + protected call works.

## Verification (mandatory)
### 1) CLI gates
- `npm run lint`
- `npm run typecheck`
- `npm run build`

### 2) Curl parity (write in Evidence Log)
Provide commands:
- Login to get token
- Call protected endpoint with Bearer token (clients list)

## Evidence Log (mandatory)
Write `task/frontend/FE-0/FE-0-01_evidence.md` with:
- Commands executed and key outputs
- Curl commands and expected status codes
- Manual smoke steps (UI) and expected behavior

## Output in your final response (no extra suggestions)
- Brief change summary
- Commands you ran
- Where the Evidence Log is located
