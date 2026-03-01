# AI‑EOS PROMPT — FE-2-04
## Title
Cases: Detail + Edit (reference-aligned case header + tabs + 2-column layout)

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
Implement Case detail view and Case edit flow.
- Route: `/cases/:id`
- Fetch case detail and render:
  - meta header card (case_no in mono, client, filing/app date)
  - status tag
  - tabs scaffold (Overview/Claims/Official Docs/Fees/Billing/Tasks placeholders ok)
  - Work Mode: 2-column layout (main panel + side panel)
  - Focus Mode: single-column reading flow (when `body.mode-immersive`)
- Provide an edit action (button to `/cases/:id/edit` or inline edit) to update case fields.

## API Endpoints (use shared axios client only)
- `GET /cases/{id}`
- `PUT /cases/{id}`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- Must align visually to `case_detail.html`:
  - header height 60px, page padding 30px (in Work Mode)
  - case header card layout and tag styling
  - tabs underline in Work Mode; underline removed in Focus Mode
  - content grid 2fr/1fr in Work Mode, single column in Focus Mode
  - side panel hidden in Focus Mode
- No inline styles in Vue templates; create CSS classes under layout.css and use tokens.

## File Allowlist (ONLY modify/add these)
- `src/api/cases.ts (update)`
- `src/api/cases.types.ts (update)`
- `src/modules/cases/pages/CaseDetail.vue (new)`
- `src/modules/cases/pages/CaseEdit.vue (new) OR reuse a CaseForm component`
- `src/router/index.ts (update: add /cases/:id and edit routes; set meta.supportsFocusMode on claims/doc tabs route if split)`
- `src/styles/layout.css (update: case header/tabs/content grid classes using tokens)`
- Evidence Log:
  - `tasks/frontend/FE-2/FE-2-04_evidence.md` (add)

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
Write `task/frontend/FE-2/FE-2-04_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
1) Navigate to `/cases/:id` and verify loading then content.
2) Toggle immersive mode (if FE‑1‑04 exists) and confirm:
   - sidebar/header collapse
   - content becomes single column with larger readable typography
   - side panel is hidden
3) Edit case fields and save (expect 200); verify detail refresh.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
