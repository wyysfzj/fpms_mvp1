# CASEDOCK-FE-CASECREATE-01 — Case create intake material gate UI

## Exact Closure Slice

Add a static, mock-aligned “收案文件与材料核验” section to the existing case create page so users can see intake files, material checklist status, gate conclusion, and non-submission warning before creating a case.

## Explicit Non-Closure

No backend/API/schema changes. No changes to case create request payload or save behavior. No upload implementation. No route/menu changes. No batch filing or document create UI changes.

## Remaining Follow-Up Task IDs

None

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. Single existing Vue page only. |
| prereq_dependency_density | Low. Depends only on completed static mock page. |
| be_fe_coupling | Low. UI-only static section. |
| evidence_cost | Medium. Requires frontend checks and visual smoke. |

chosen_runbook: `P0-frontend-heavy-story`

## Allowed Files

- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `artifacts/CASEDOCK-FE-CASECREATE-01/**`

## Verification Commands

- `cd frontend && npm run lint`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run build`
- Playwright or browser smoke showing `/cases/new` loads and the “收案文件与材料核验” section is visible.
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-CASECREATE-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-CASECREATE-01/`
