# AI‑EOS PROMPT — FE-2-22
## Title
System/Templates: Templates list + upload

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
Implement templates management.
- Route: `/system/templates`
- List existing templates.
- Provide upload (multipart) and refresh list on success.

## API Endpoints (use shared axios client only)
- `GET /templates?page=1&page_size=50`
- `POST /templates (multipart/form-data)`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- Use compact list/table; upload control token-aligned; show requestId on failures.

## File Allowlist (ONLY modify/add these)
- `src/api/system.ts (new)`
- `src/api/system.types.ts (new)`
- `src/modules/system/pages/TemplateList.vue (new)`
- `src/modules/system/components/TemplateUpload.vue (new)`
- `src/router/index.ts (update)`
- `src/styles/layout.css (optional)`
- Evidence Log:
  - `task/frontend/FE-2/FE-2-22_evidence.md` (add)

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
Write `task/frontend/FE-2/FE-2-22_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
Provide manual UI smoke steps for the implemented slice (including expected status codes).

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
