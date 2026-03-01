# AI‑EOS PROMPT — FE-2-02
## Title
Clients: Create + Edit + Deactivate (forms + 422 mapping)

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
Implement client create/edit pages and deactivate action.
- Routes: `/clients/new`, `/clients/:id/edit`
- Form uses Element Plus `el-form` with grouped sections.
- On save success: navigate back to `/clients` and show success feedback.
- Deactivate: confirmation modal from edit page or list row action.

## API Endpoints (use shared axios client only)
- `POST /clients`
- `GET /clients/{id}`
- `PUT /clients/{id}`
- `PUT /clients/{id}/deactivate`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- Form pattern: card sections, clear labels, compact spacing.
- Use tokens for spacing/border; avoid inline styles.
- Deactivate action must be visually “danger” but still token-aligned (use Element Plus danger styles mapped to tokens).

## File Allowlist (ONLY modify/add these)
- `src/api/clients.ts (update)`
- `src/api/clients.types.ts (update)`
- `src/modules/clients/pages/ClientForm.vue (new)`
- `src/modules/clients/pages/ClientEdit.vue OR reuse ClientForm.vue (new/update)`
- `src/router/index.ts (update: add routes)`
- `src/styles/layout.css (optional)`
- Evidence Log:
  - `task/frontend/FE-2/FE-2-02_evidence.md` (add)

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
Write `task/frontend/FE-2/FE-2-02_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
1) Create a new client via `/clients/new` (expect 201).
2) Trigger a 422 by submitting invalid data; verify field-level errors render.
3) Edit an existing client via `/clients/:id/edit` (expect 200).
4) Deactivate the client and confirm list reflects status change (expect 200).

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
