# AI‑EOS PROMPT — FE-2-14
## Title
Fees: Drafts list + create + detail scaffold

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
Implement fee drafts list, create page, and draft detail scaffold.
- Routes: `/fees/drafts`, `/fees/drafts/new`, `/fees/drafts/:id`
- Draft create links to case/client/currency (use minimal inputs; do not guess unknown lookups).
- Detail shows meta header and an empty items section placeholder.

## API Endpoints (use shared axios client only)
- `GET /fees/drafts?page=1&page_size=20`
- `POST /fees/drafts`
- `GET /fees/drafts/{id}`
- `PUT /fees/drafts/{id}`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- Draft detail should follow reference-like meta header + tabs/sections.
- In Focus Mode (optional), meta stays readable and content centers.

## File Allowlist (ONLY modify/add these)
- `src/api/fees.ts (update)`
- `src/api/fees.types.ts (update)`
- `src/modules/fees/pages/FeeDraftList.vue (new)`
- `src/modules/fees/pages/FeeDraftCreate.vue (new)`
- `src/modules/fees/pages/FeeDraftDetail.vue (new)`
- `src/router/index.ts (update)`
- `src/styles/layout.css (optional)`
- Evidence Log:
  - `task/frontend/FE-2/FE-2-14_evidence.md` (add)

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
Write `task/frontend/FE-2/FE-2-14_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
Provide manual UI smoke steps for the implemented slice (including expected status codes).

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
