# AI‑EOS PROMPT — FE-3-07
## Title
Polish: MVP A11y + micro-UX sweep (dialogs, dropdowns, reduced motion, aria)

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
Perform an MVP-level accessibility and micro-UX sweep focused on:
1) Dialogs/Drawers: focus enters on open, ESC closes, focus returns on close.
2) Dropdown row actions: keyboard accessible, readable labels.
3) Mode toggle: `aria-pressed`, keyboard accessible.
4) Reduced motion: respect `prefers-reduced-motion` for transitions.
Implement minimal code/CSS changes to address issues found in FE-3-01 smoke flows.
Do not redesign; keep changes targeted and token-driven.

## Must‑Include Requirements
- Do not introduce new dependencies for A11y tooling; use manual checks.
- Ensure focus ring is visible and token-aligned (do not hardcode random colors).
## Non‑Goals (hard constraints)
- Do NOT add heavy dependencies.
- Do NOT modify the tokens variable block (must stay exactly per `fpms.css`).
- Do NOT introduce inline styles or hardcoded colors/spacing in templates.
- Do NOT implement new business features beyond this task’s scope.

## File Allowlist (ONLY modify/add these)
- `src/components/layout/ModeToggle.vue (update)`
- `src/styles/base.css (update: reduced motion rules)`
- `src/styles/layout.css (optional: focus ring / accessibility helpers)`
- `src/modules/*/pages/*.vue (update: only pages where dialog/dropdown issues exist; keep minimal)`
- `task/frontend/FE-3/FE-3-07_evidence.md (new)`
- Evidence Log:
  - `task/frontend/FE-3/FE-3-07_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist. Do not proceed.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-3/FE-3-07_evidence.md` including:
- Commands executed + key outputs
- Manual verification steps + results
- Any mismatches and how you handled them (STOP vs in-scope fix)

## Manual Smoke Steps (minimum)
1) Open/close any dialog used in FE-2 actions (deactivate/lock/cancel/etc) and verify focus behavior.
2) Trigger dropdown actions using keyboard only.
3) Toggle immersive mode using keyboard and confirm `aria-pressed`.
4) Enable reduced motion in OS/browser (or emulate) and confirm animations are reduced.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
