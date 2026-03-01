# AI‑EOS PROMPT — FE-2-20
## Title
Billing: Payments + Offsets + Reverse (minimal reliable UX)

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
Implement payments list/create and offsets create/reverse (as supported by backend).
- Routes: `/billing/payments`, `/billing/payments/new` (optional)
- Provide an offset creation UI that uses only fields that backend actually provides/accepts.
- If required identifiers are not obtainable from existing endpoints, STOP and propose smallest backend/query fix.

## API Endpoints (use shared axios client only)
- `GET /payments?page=1&page_size=20`
- `POST /payments`
- `POST /offsets`
- `POST /offsets/{id}/reverse`

## Non‑Goals (hard constraints)
- Do NOT introduce heavy dependencies.
- Do NOT modify tokens/variables beyond what FE‑1 established.
- Do NOT add inline styles; use classes + tokens.

## UI Requirements (strict)
- Keep workflows minimal and auditable: show IDs in mono font; show balances.
- Do not invent fields; rely on backend payload shapes.

## File Allowlist (ONLY modify/add these)
- `src/api/billing.ts (update)`
- `src/api/billing.types.ts (update)`
- `src/modules/billing/pages/PaymentList.vue (new)`
- `src/modules/billing/pages/PaymentCreate.vue (new OR integrate as dialog)`
- `src/modules/billing/pages/OffsetCreate.vue (new OR dialog within BillDetail)`
- `src/router/index.ts (update)`
- `src/styles/layout.css (optional)`
- Evidence Log:
  - `task/frontend/FE-2/FE-2-20_evidence.md` (add)

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
Write `task/frontend/FE-2/FE-2-20_evidence.md` including:
- Commands executed + key outputs
- Manual smoke steps + expected results
- Any API assumptions verified (or the exact mismatch if you had to STOP)

## Manual Smoke Steps (minimum)
Provide manual UI smoke steps for the implemented slice (including expected status codes).

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
