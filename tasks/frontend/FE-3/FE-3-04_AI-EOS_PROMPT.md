# AI‑EOS PROMPT — FE-3-04
## Title
Polish: Apply State Kit to remaining list pages (Documents/Fees/Billing/System)

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
Apply the State Kit components to remaining list pages:
- Documents list
- Fee rates list and/or fee drafts list
- Bills list and/or payments list
- System templates/params/letterheads lists
If any module lacks a list page, apply to the closest equivalent.
Keep changes minimal and consistent.

## Must‑Include Requirements
- All updated pages must show consistent requestId on error.
- Pagination controls must match backend page/page_size semantics.
## Non‑Goals (hard constraints)
- Do NOT add heavy dependencies.
- Do NOT modify the tokens variable block (must stay exactly per `fpms.css`).
- Do NOT introduce inline styles or hardcoded colors/spacing in templates.
- Do NOT implement new business features beyond this task’s scope.

## File Allowlist (ONLY modify/add these)
- `src/modules/documents/pages/DocumentList.vue (update)`
- `src/modules/fees/pages/* (update: whichever list pages exist)`
- `src/modules/billing/pages/* (update: whichever list pages exist)`
- `src/modules/system/pages/* (update: whichever list pages exist)`
- `src/styles/layout.css (optional: minimal adjustments)`
- `task/frontend/FE-3/FE-3-04_evidence.md (new)`
- Evidence Log:
  - `task/frontend/FE-3/FE-3-04_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist. Do not proceed.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-3/FE-3-04_evidence.md` including:
- Commands executed + key outputs
- Manual verification steps + results
- Any mismatches and how you handled them (STOP vs in-scope fix)

## Manual Smoke Steps (minimum)
Provide manual smoke steps relevant to this task and include expected results + requestId visibility where applicable.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
