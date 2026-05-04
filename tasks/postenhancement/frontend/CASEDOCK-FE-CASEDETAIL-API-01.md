# CASEDOCK-FE-CASEDETAIL-API-01 — Case detail document gate real API integration

## Exact Closure Slice

Replace static case detail document gate and file event status values in `frontend/src/modules/cases/components/CaseDocumentsTab.vue` with real case document gate API data.

## Explicit Non-Closure

No document list endpoint changes. No upload implementation. No backend code. No shared API contract changes. No layout redesign. No route/menu/store changes.

## Remaining Follow-Up Task IDs

- `CASEDOCK-FE-DOCIMPACT-API-01`
- `CASEDOCK-FE-BATCHFILING-API-01`
- `CASEDOCK-QA-REALAPI-E2E-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. This task owns one Vue component file only. |
| prereq_dependency_density | Medium. Depends on `CASEDOCK-BE-CASE-GATE-API-01` and `CASEDOCK-FE-GATE-API-CONTRACT-01`. |
| be_fe_coupling | High. Material checks, missing items, conclusion, suggested actions, and file event status must come from `GET /cases/{case_id}/document-gate`. |
| evidence_cost | Medium. Requires frontend lint, typecheck, build, browser smoke where available, and task evidence gate. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/frontend/CASEDOCK-FE-CASEDETAIL-API-01.md`
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `artifacts/CASEDOCK-FE-CASEDETAIL-API-01/**`

## Verification Commands

- `npm --prefix frontend run lint`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run build`
- browser smoke for a case detail documents tab when the local app can run
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/frontend/CASEDOCK-FE-CASEDETAIL-API-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-CASEDETAIL-API-01`
- `./scripts/task_validate.sh CASEDOCK-FE-CASEDETAIL-API-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-CASEDETAIL-API-01/`

## Done Definition

- The current-node material table renders backend `checks`.
- Status strip and gate conclusion render backend material count, missing count, hard-block, afterfill audit, and suggested actions.
- File event status uses backend `file_events`, not static local tags.
- Loading, error, and no-data states are visible and written in Simplified Chinese.
- Frontend lint, typecheck, build, and task gate pass with evidence.
