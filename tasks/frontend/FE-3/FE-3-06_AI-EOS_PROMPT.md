# AI‑EOS PROMPT — FE-3-06
## Title
Polish: Focus Mode sweep for long-form pages (Case/Document) + route opt-in audit

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
Audit and fix Focus Mode behavior across long-form pages.
Minimum targets:
- Case detail long-form tab (Claims or similar)
- Document detail (if it includes long content/notes)
Ensure:
- Routes that benefit from Focus Mode set `meta.supportsFocusMode = true`
- In immersive mode (`body.mode-immersive`): sidebar/header collapse, content becomes single-column, reading typography applies (`--font-read`), and any side-panel is hidden.
Fix CSS/class usage to match the reference; do not change tokens.

## Must‑Include Requirements
- Immersive mode content padding should match reference (paper-like layout).
- Side panels/timeline equivalents must be hidden in immersive mode.
## Non‑Goals (hard constraints)
- Do NOT add heavy dependencies.
- Do NOT modify the tokens variable block (must stay exactly per `fpms.css`).
- Do NOT introduce inline styles or hardcoded colors/spacing in templates.
- Do NOT implement new business features beyond this task’s scope.

## File Allowlist (ONLY modify/add these)
- `src/router/index.ts (update: meta.supportsFocusMode where needed)`
- `src/modules/cases/pages/CaseDetail.vue (update)`
- `src/modules/documents/pages/DocumentDetail.vue (update)`
- `src/styles/layout.css (update: immersive rules/classes; token-driven)`
- `task/frontend/FE-3/FE-3-06_evidence.md (new)`
- Evidence Log:
  - `task/frontend/FE-3/FE-3-06_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist. Do not proceed.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-3/FE-3-06_evidence.md` including:
- Commands executed + key outputs
- Manual verification steps + results
- Any mismatches and how you handled them (STOP vs in-scope fix)

## Manual Smoke Steps (minimum)
1) Open Case detail long-form tab; toggle immersive mode.
2) Confirm single-column reading layout (centered, max-width feel) and typography changes.
3) Confirm side panel is hidden.
4) Repeat for Document detail.
5) Refresh and confirm mode persistence still works.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
