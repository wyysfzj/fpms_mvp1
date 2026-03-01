# AI‑EOS PROMPT — FE-3-01
## Title
Integration: UI Smoke Flows doc + run core MVP1 flows

## Context
You are working in the FPMS MVP1 frontend repository (Vue3 + TypeScript + Vite + Pinia + Element Plus).
Phase FE‑2 feature pages are complete. Now execute Phase FE‑3: Integration & Polish.

UI Style (STRICT):
- Reference: `reference/case_detail.html`
- Tokens spec: `fpms.css` (the `src/styles/variables.css` variable block must match EXACTLY)

Backend norms to honor:
- Auth: JWT Bearer
- Errors: `{"error":{"code","message","details"}}`
- Pagination: `{items,page,page_size,total}`
- Common statuses: 401/403/422/409

## Objective
Create a reproducible UI smoke flow document aligned to MVP1 operational backbone and backend curl guides.
Deliver:
1) `docs/frontend_smoke_flows.md` containing at least these flows:
   - Auth/session
   - Clients (list/create/edit/deactivate)
   - Cases (list/create/detail/edit/limited-edit)
   - Tasks (list/create/close/reopen/cancel/today)
   - Documents (list/create/detail/upload/download)
   - Fees (rates/drafts/items/lock)
   - Billing (bills list/detail/create/print; payments/offsets if supported; receipts summary)
   - System/Templates (templates upload; params upsert; letterheads)
2) Actually run the flows in the UI and record results (status codes, requestId when present) in the evidence log.
If any flow cannot be completed due to API mismatch or missing fields, STOP and document the smallest fix task.

## Must‑Include Requirements
- Each flow includes: Preconditions, UI steps, Expected API (endpoints + statuses), Expected UI, Failure modes (401/403/422/409) and where requestId is displayed.
- Use absolute routes/paths and exact button labels to make steps reproducible.
## Non‑Goals (hard constraints)
- Do NOT add heavy dependencies.
- Do NOT modify the tokens variable block (must stay exactly per `fpms.css`).
- Do NOT introduce inline styles or hardcoded colors/spacing in templates.
- Do NOT implement new business features beyond this task’s scope.

## File Allowlist (ONLY modify/add these)
- `docs/frontend_smoke_flows.md (new)`
- `task/frontend/FE-3/FE-3-01_evidence.md (new)`
- Evidence Log:
  - `task/frontend/FE-3/FE-3-01_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist. Do not proceed.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-3/FE-3-01_evidence.md` including:
- Commands executed + key outputs
- Manual verification steps + results
- Any mismatches and how you handled them (STOP vs in-scope fix)

## Manual Smoke Steps (minimum)
Run each documented flow end-to-end in the UI. For each flow, record:
- Success/Failure
- Key API statuses
- requestId (if present)
- Any UI inconsistencies found (loading/empty/error/pagination).

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
