# AI‑EOS PROMPT — FE-3-03
## Title
Polish: Apply State Kit to core list pages (Clients/Cases/Tasks)

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
Apply the FE-3-02 State Kit components to the core operational list pages:
- Clients list
- Cases list
- Tasks list
Each page must show consistent loading/empty/error/pagination behavior.
Do not refactor unrelated business logic; keep changes minimal and mechanical.

## Must‑Include Requirements
- All 3 pages must display requestId on error when available.
- No regression in table density; keep reference-like compact spacing.
## Non‑Goals (hard constraints)
- Do NOT add heavy dependencies.
- Do NOT modify the tokens variable block (must stay exactly per `fpms.css`).
- Do NOT introduce inline styles or hardcoded colors/spacing in templates.
- Do NOT implement new business features beyond this task’s scope.

## File Allowlist (ONLY modify/add these)
- `src/modules/clients/pages/ClientList.vue (update)`
- `src/modules/cases/pages/CaseList.vue (update)`
- `src/modules/tasks/pages/TaskList.vue (update)`
- `src/styles/layout.css (optional: minimal adjustments)`
- `task/frontend/FE-3/FE-3-03_evidence.md (new)`
- Evidence Log:
  - `task/frontend/FE-3/FE-3-03_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist. Do not proceed.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-3/FE-3-03_evidence.md` including:
- Commands executed + key outputs
- Manual verification steps + results
- Any mismatches and how you handled them (STOP vs in-scope fix)

## Manual Smoke Steps (minimum)
For each page (Clients/Cases/Tasks):
1) Load page -> see loading then data.
2) Navigate page 1 -> page 2 -> page 1.
3) Verify empty state (if you can filter to no results) or by temporarily using page beyond total.
4) Verify error banner by forcing an API failure (e.g., remove token) shows requestId.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
