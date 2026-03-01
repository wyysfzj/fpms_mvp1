# AI‑EOS PROMPT — FE-3-05
## Title
Polish: Unify 422 form validation mapping helper + apply to key forms

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
Create a small helper to map backend 422 validation errors into Element Plus field errors.
Then apply it to at least THREE key forms (e.g., Client create/edit, Case create/edit, Task create).
Ensure non-field errors still show in ApiErrorBanner.
Do not change backend contracts; only map existing `error.details` structure.

## Must‑Include Requirements
- Handle both common shapes: details as dict of field->messages, or list of errors; fallback gracefully.
- Field errors must render next to fields (Element Plus form item).
## Non‑Goals (hard constraints)
- Do NOT add heavy dependencies.
- Do NOT modify the tokens variable block (must stay exactly per `fpms.css`).
- Do NOT introduce inline styles or hardcoded colors/spacing in templates.
- Do NOT implement new business features beyond this task’s scope.

## File Allowlist (ONLY modify/add these)
- `src/utils/validation.ts (new)`
- `src/modules/clients/pages/* (update: form pages)`
- `src/modules/cases/pages/* (update: create/edit pages)`
- `src/modules/tasks/pages/* (update: create page)`
- `src/components/state/* (optional: if you add a small FieldErrors helper)`
- `task/frontend/FE-3/FE-3-05_evidence.md (new)`
- Evidence Log:
  - `task/frontend/FE-3/FE-3-05_evidence.md` (add)

If you believe additional files are required, STOP and propose a smallest atomic fix task with its own allowlist. Do not proceed.

## Quality Gates (mandatory)
Run:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

## Evidence Log (mandatory)
Write `task/frontend/FE-3/FE-3-05_evidence.md` including:
- Commands executed + key outputs
- Manual verification steps + results
- Any mismatches and how you handled them (STOP vs in-scope fix)

## Manual Smoke Steps (minimum)
1) For each updated form, submit invalid payload to trigger 422.
2) Verify field-level errors render.
3) Verify requestId is visible on any banner/toast when present.
4) Verify successful submit still works.

## Output in final response (no extra suggestions)
- Bullet summary of changes
- Commands run
- Evidence log path
