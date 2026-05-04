# CASEDOCK-FE-CASECREATE-API-01 — Case create intake gate real API integration

## Exact Closure Slice

Replace the static intake material gate values in `frontend/src/modules/cases/pages/CaseCreate.vue` with real intake document gate API data, preserving the existing minimal UI layout and showing loading, error, and empty states.

## Explicit Non-Closure

No case create payload behavior change. No upload implementation. No final filing behavior. No backend code. No shared API contract changes. No route/menu/store changes. No layout redesign.

## Remaining Follow-Up Task IDs

- `CASEDOCK-FE-CASEDETAIL-API-01`
- `CASEDOCK-FE-DOCIMPACT-API-01`
- `CASEDOCK-FE-BATCHFILING-API-01`
- `CASEDOCK-QA-REALAPI-E2E-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. This task owns one Vue page file only. |
| prereq_dependency_density | Medium. Depends on `CASEDOCK-BE-INTAKE-GATE-API-01` and `CASEDOCK-FE-GATE-API-CONTRACT-01`. |
| be_fe_coupling | High. The visible gate rows and conclusion must come from backend `GET /cases/document-gate/intake-preview`. |
| evidence_cost | Medium. Requires frontend lint, typecheck, build, browser smoke where available, and task evidence gate. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/frontend/CASEDOCK-FE-CASECREATE-API-01.md`
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `artifacts/CASEDOCK-FE-CASECREATE-API-01/**`

## Verification Commands

- `npm --prefix frontend run lint`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run build`
- browser smoke for `/cases/new` when the local app can run
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/frontend/CASEDOCK-FE-CASECREATE-API-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-CASECREATE-API-01`
- `./scripts/task_validate.sh CASEDOCK-FE-CASECREATE-API-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-CASECREATE-API-01/`

## Done Definition

- The existing intake gate visual block renders backend API checks, missing items, material counts, conclusion, and suggested actions.
- Loading, error, and no-data states are visible and written in Simplified Chinese.
- No hardcoded gate conclusion or material requirement rows remain in this page.
- Frontend lint, typecheck, build, and task gate pass with evidence.
