# AI‑EOS PROMPT — FE-2-01
## Title
Clients: List + Pagination (high-density table, token-aligned)

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
Implement the Clients list page with server-side pagination.
- Route: `/clients`
- Fetch paginated data and render a compact `el-table` with row actions (dropdown).
- Include loading, empty, and error states.
- Include a primary CTA to create a client (route link to `/clients/new`).

## API Endpoints (use shared axios client only)
- `GET /clients?page=1&page_size=20`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- Follow List Page Pattern: header + filter area (minimal) + table + pagination.
- Table density should feel like the reference: compact spacing, minimal visual noise.
- Use token-driven colors; active/hover row actions must not introduce non-token colors.

## File Allowlist (ONLY modify/add these)
- `src/api/clients.ts (new)`
- `src/api/clients.types.ts (new)`
- `src/modules/clients/pages/ClientList.vue (new)`
- `src/router/index.ts (update: ensure /clients route)`
- `src/styles/layout.css (optional: only for page-level classes using tokens)`
- Evidence Log:
  - `task/frontend/FE-2/FE-2-01_evidence.md` (add)

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
Write `task/frontend/FE-2/FE-2-01_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
1) Login and navigate to `/clients`.
2) Verify table loads and pagination controls work (page/page_size).
3) Verify empty state appears when total == 0.
4) Verify error state shows message + requestId when API fails.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
