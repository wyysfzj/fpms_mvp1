# AI‑EOS PROMPT — FE-2-05
## Title
Cases: Limited Edit (POST /cases/{id}/limited-edit) with 403 UX

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
Implement the limited edit action for Cases.
- Provide a UI entry (button on CaseDetail or separate route) that calls limited-edit endpoint.
- If 403 occurs, ensure PermissionDenied UX shows required_perm if present.
- On success, refresh the Case detail.

## API Endpoints (use shared axios client only)
- `POST /cases/{id}/limited-edit`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- Limited edit UI should be a small dialog/drawer, token-aligned.
- Do not hide the entry purely based on guessed permissions; rely on backend 403.

## File Allowlist (ONLY modify/add these)
- `src/api/cases.ts (update)`
- `src/modules/cases/pages/CaseDetail.vue (update: add limited edit entry)`
- `src/modules/cases/components/LimitedEditDialog.vue (new) OR inline minimal dialog in CaseDetail`
- `src/styles/layout.css (optional)`
- Evidence Log:
  - `task/frontend/FE-2/FE-2-05_evidence.md` (add)

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
Write `tasks/frontend/FE-2/FE-2-05_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
1) From CaseDetail, invoke limited edit.
2) If allowed: submit changes (expect 200) and verify detail updated.
3) If forbidden: expect navigation to /forbidden with required_perm/requestId (or equivalent global 403 UX).

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
