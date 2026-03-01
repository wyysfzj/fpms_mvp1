# AI‑EOS PROMPT — FE-2-03
## Title
Cases: List + Create (requires client_id)

## Context
Repo: FPMS MVP1 frontend (Vue3 + TS + Vite + Pinia + Element Plus).
Backend:
- Base URL: `http://localhost:8000/api/v1`
- JWT Bearer auth
- Errors: `{ "error": { "code", "message", "details" } }`
- Pagination: `{ items, page, page_size, total }`

UI Style (strict):
- Reference UI: `reference/case_detail.html`
- Tokens spec: `fpms.css` (variables must match FE‑1 implementation)

Assume FE‑0 + FE‑1 are complete.

## Objective
Implement Cases list page and a Case create page.
- Routes: `/cases`, `/cases/new`
- Create requires `client_id` (and other minimal fields per backend).
- List shows case_no, title/name, client, status, and updated/created dates if available.

## API Endpoints (use shared axios client only)
- `GET /cases?page=1&page_size=20`
- `POST /cases`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- List page uses the same density/spacing as Clients list.
- Create page: use token-aligned form sections.
- Client selection: if backend supports client listing, fetch a small page and allow selecting; do not guess unsupported search parameters. If client selection UX cannot be implemented without guessing, STOP and propose smallest fix (e.g., add a backend search param) rather than inventing.

## File Allowlist (ONLY modify/add these)
- `src/api/cases.ts (new)`
- `src/api/cases.types.ts (new)`
- `src/modules/cases/pages/CaseList.vue (new)`
- `src/modules/cases/pages/CaseCreate.vue (new)`
- `src/router/index.ts (update: ensure /cases routes)`
- `src/styles/layout.css (optional)`
- Evidence Log:
  - `task/frontend/FE-2/FE-2-03_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist.

## Implementation Requirements
1) Create typed DTOs for the minimum fields needed for this slice.
2) All requests must go through the shared API client (`src/api/http.ts`).
3) Handle loading/empty/error states.
4) On errors, display `requestId` if available.
5) For forms:
   - Map 422 validation details to field errors (Element Plus form items).
   - Show non-field errors in a banner.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-2/FE-2-03_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
Provide manual UI smoke steps for the implemented slice (including expected status codes).

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
