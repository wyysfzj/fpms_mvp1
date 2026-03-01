# AI‑EOS PROMPT — FE-3-02
## Title
Polish: Build shared State Kit (Loading/Empty/Error/Pagination) + apply to 1 page

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
Create a minimal shared UI kit for common async states and pagination, token-aligned.
Deliver reusable components:
- `LoadingBlock` (table/page loading)
- `EmptyState` (with optional CTA)
- `ApiErrorBanner` (message + requestId; optional required_perm display)
- `PaginationBar` (page/page_size/total aligned)
Then apply the kit to ONE representative list page (prefer Clients list) as a demo.
All styles must use tokens and match the reference density and spacing.

## Must‑Include Requirements
- Components must not hardcode colors/sizes; rely on CSS variables from `variables.css` and existing mappings.
- Error banner must display requestId when available.
- PaginationBar must be wired to backend pagination shape.
## Non‑Goals (hard constraints)
- Do NOT add heavy dependencies.
- Do NOT modify the tokens variable block (must stay exactly per `fpms.css`).
- Do NOT introduce inline styles or hardcoded colors/spacing in templates.
- Do NOT implement new business features beyond this task’s scope.

## File Allowlist (ONLY modify/add these)
- `src/components/state/* (new)`
- `src/components/errors/* (update if you already have it; keep consistent)`
- `src/styles/layout.css (update: classes only, token-driven)`
- `src/modules/clients/pages/ClientList.vue (update OR whichever page exists as the demo)`
- `task/frontend/FE-3/FE-3-02_evidence.md (new)`
- Evidence Log:
  - `task/frontend/FE-3/FE-3-02_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist. Do not proceed.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-3/FE-3-02_evidence.md` including:
- Commands executed + key outputs
- Manual verification steps + results
- Any mismatches and how you handled them (STOP vs in-scope fix)

## Manual Smoke Steps (minimum)
1) Open the demo list page.
2) Verify loading state appears during fetch.
3) Verify empty state appears when total==0.
4) Simulate an API error (e.g., invalid token) and verify error banner shows message + requestId.
5) Verify pagination interaction updates the list.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
