# AI‑EOS PROMPT — FE‑1‑03
## Title
FE‑1‑03: Global error UX (401/403/422/409) + PermissionDenied/NotFound pages (token-aligned)

## Context
FE‑0 implements normalized API errors and 401 redirect. FE‑1‑03 adds FE‑1 global UX for permission and common failures.
Backend error envelope: `{ "error": { "code", "message", "details" } }`.
We also want requestId (X-Request-ID) displayed when present.

## Objective
1) Add routes/pages:
   - `/forbidden` (PermissionDenied)
   - `/:pathMatch(.*)*` (NotFound)
2) Implement a reusable error presentation component (banner/empty state) that shows:
   - message
   - optional `required_perm` (if provided in details)
   - optional requestId
3) Implement global 403 handling without circular imports:
   - In axios response interceptor, on 403 dispatch:
     `window.dispatchEvent(new CustomEvent('fpms:forbidden', { detail: { requiredPerm, message, requestId } }))`
   - In `main.ts`, listen and route to `/forbidden` (avoid redirect loops).
4) Ensure 422 can be rendered at field-level by pages (provide helper to map details).
5) Ensure 409 is shown as a clear conflict message (toast or banner); keep it consistent.

## Non‑Goals
- Do NOT add new module CRUD pages.
- Do NOT implement full i18n.
- Do NOT add dependencies.

## File Allowlist (ONLY modify/add these)
- `src/views/PermissionDenied.vue` (new)
- `src/views/NotFound.vue` (new)
- `src/components/errors/*` (new; e.g. `ApiErrorBanner.vue`)
- `src/api/http.ts` (update: dispatch fpms:forbidden on 403; no router imports)
- `src/api/errors.ts` (update only if needed)
- `src/router/index.ts` (add routes)
- `src/main.ts` (listen to fpms:forbidden, route push)
- `src/styles/layout.css` (style new pages/components using tokens)
- Evidence Log:
  - `task/frontend/FE-1/FE-1-03_evidence.md` (add)

If additional files seem required, STOP and propose a smallest atomic fix task.

## Implementation Requirements
### A) PermissionDenied page
- Shows:
  - Title: “Permission denied”
  - `required_perm` if available
  - requestId if available
  - CTA: “Back to dashboard” and “Logout”
- Style must use tokens: panel bg, radius, border, typography.

### B) NotFound page
- Simple 404 with button back to dashboard.

### C) 403 global dispatch (no circular imports)
- In `http.ts` response interceptor:
  - Normalize error first
  - If status === 403:
    - Extract `required_perm` from error.details if present
    - Dispatch custom event with detail payload

### D) Listener in `main.ts`
- Listen once on app boot:
  - On event, navigate to `/forbidden`
  - Pass info via query string OR in-memory store (prefer query for simplicity)
  - Avoid loops if already on `/forbidden`

### E) 422 helper (minimal)
- Provide a small helper to map backend `details` into:
  - `field -> message[]`
- Do not over-engineer; just enough for FE‑2 forms.

## Quality Gates
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log
Write `task/frontend/FE-1/FE-1-03_evidence.md`:
- Commands + key outputs
- Manual checks:
  - Trigger 403 (e.g. by visiting restricted endpoint) -> navigates to /forbidden and displays required_perm/requestId if present
  - 404 route shows NotFound
  - 409/422 display behavior (can be simulated by mocking ApiError)

## Output in final response (no extra suggestions)
- Summary
- Commands
- Evidence path
