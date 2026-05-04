# CASEDOCK-FE-BATCHFILING-API-01 — Batch filing final material gate real API integration

## Exact Closure Slice

Replace static batch filing final gate columns and execution preview in `frontend/src/modules/cases/pages/CaseBatchFiling.vue` with real backend `final_material_gate` data, and keep hard-block UI aligned with backend submit rejection.

## Explicit Non-Closure

No route/menu change. No backend code. No shared API contract changes. No layout redesign. No new dependencies. No change to the submit endpoint path or payload shape.

## Remaining Follow-Up Task IDs

- `CASEDOCK-QA-REALAPI-E2E-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. This task owns one Vue page file only. |
| prereq_dependency_density | Medium. Depends on `CASEDOCK-BE-BATCH-GATE-QUERY-01`, `CASEDOCK-BE-BATCH-GATE-SUBMIT-01`, and `CASEDOCK-FE-GATE-API-CONTRACT-01`. |
| be_fe_coupling | High. Candidate rows and submit rejection handling must reflect backend final material gate behavior. |
| evidence_cost | Medium. Requires frontend lint, typecheck, build, browser smoke where available, and task evidence gate. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/frontend/CASEDOCK-FE-BATCHFILING-API-01.md`
- `frontend/src/modules/cases/pages/CaseBatchFiling.vue`
- `artifacts/CASEDOCK-FE-BATCHFILING-API-01/**`

## Verification Commands

- `npm --prefix frontend run lint`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run build`
- browser smoke for batch filing when the local app can run
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/frontend/CASEDOCK-FE-BATCHFILING-API-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-BATCHFILING-API-01`
- `./scripts/task_validate.sh CASEDOCK-FE-BATCHFILING-API-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-BATCHFILING-API-01/`

## Done Definition

- Final material count, missing items, conclusion, hard-block status, afterfill audit, and execution preview render backend `final_material_gate` data.
- Hard-block rows are not selectable for submit from the UI.
- Backend submit rejection is surfaced in Simplified Chinese if it still occurs.
- Static afterfill audit and execution preview mock values are removed.
- Frontend lint, typecheck, build, and task gate pass with evidence.
