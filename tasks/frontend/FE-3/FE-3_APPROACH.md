# Phase FE‑3: Integration & Polish — Approach (AI‑EOS)

## Purpose
FE‑3 turns completed FE‑2 feature pages into a shippable MVP by:
- Proving end‑to‑end operational workflows (UI smoke flows aligned to backend curl guides)
- Eliminating UI/UX inconsistencies (loading/empty/error/pagination/form errors)
- Ensuring Focus Mode/Work Mode dual‑mode behaves exactly like the reference
- MVP‑level accessibility + interaction polish

## UI Style: Non‑Negotiable Source of Truth
- Visual/interaction reference: `reference/case_detail.html`
- Tokens spec: `fpms.css` (the `src/styles/variables.css` token block must match exactly)

Hard rules:
- No inline styles / magic numbers in templates.
- Colors/sizes/spacing must come from tokens + classes.
- Long‑form pages must support Focus Mode (`body.mode-immersive`) and remain readable.

## Execution Model (A/B/C)
### Track A — E2E Smoke Flows (write + run)
Create a single smoke flows document and actually run the flows in UI. This reveals real integration gaps.

### Track B — Consistency Kit (shared components)
Create a small set of shared components/helpers, then apply them in small batches to avoid large risky refactors.

### Track C — Focus Mode + A11y polish
Sweep long‑form pages for immersive behavior and fix keyboard/focus/aria issues.

## Task Breakdown (7 atomic tasks)
1) FE‑3‑01: Write & run UI smoke flows (docs + evidence)
2) FE‑3‑02: Build shared “State Kit” (Loading/Empty/Error/Pagination) + demo on 1 page
3) FE‑3‑03: Apply State Kit to core list pages (Clients/Cases/Tasks)
4) FE‑3‑04: Apply State Kit to remaining list pages (Documents/Fees/Billing/System)
5) FE‑3‑05: Unify 422 form error mapping helper + apply to key forms
6) FE‑3‑06: Focus Mode sweep (Case/Document long‑form pages) + route opt‑in checks
7) FE‑3‑07: MVP A11y & micro‑UX sweep (dialogs, dropdown actions, reduced motion)

## Evidence (mandatory per task)
- `npm run lint`
- `npm run typecheck`
- `npm run build`
- Evidence log: `task/frontend/FE-3/<task_id>_evidence.md`
- Include manual smoke steps and expected outcomes.

## Stop Conditions
If any flow cannot be completed because of:
- endpoint mismatch
- required identifiers not obtainable
- CORS/blob download blocked
STOP and produce a smallest atomic fix task instead of guessing.
