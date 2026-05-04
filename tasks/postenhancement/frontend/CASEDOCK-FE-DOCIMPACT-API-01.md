# CASEDOCK-FE-DOCIMPACT-API-01 — Document create impact preview real API integration

## Exact Closure Slice

Replace static document create impact preview values in `frontend/src/modules/documents/pages/DocumentCreate.vue` with real `POST /documents/impact-preview` API data driven by case, document type, template, direction, date, title, description, and reply source fields.

## Explicit Non-Closure

No document create submit mutation change. No backend code. No shared API contract changes. No layout redesign. No route/menu/store changes. No new dependencies.

## Remaining Follow-Up Task IDs

- `CASEDOCK-FE-BATCHFILING-API-01`
- `CASEDOCK-QA-REALAPI-E2E-01`

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. This task owns one Vue page file only. |
| prereq_dependency_density | Medium. Depends on `CASEDOCK-BE-DOC-IMPACT-API-01` and `CASEDOCK-FE-GATE-API-CONTRACT-01`. |
| be_fe_coupling | High. Preview rows and confirmation/risk state must come from backend document impact preview API. |
| evidence_cost | Medium. Requires frontend lint, typecheck, build, browser smoke where available, and task evidence gate. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/frontend/CASEDOCK-FE-DOCIMPACT-API-01.md`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `artifacts/CASEDOCK-FE-DOCIMPACT-API-01/**`

## Verification Commands

- `npm --prefix frontend run lint`
- `npm --prefix frontend run typecheck`
- `npm --prefix frontend run build`
- browser smoke for document create when the local app can run
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/frontend/CASEDOCK-FE-DOCIMPACT-API-01.md`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-FE-DOCIMPACT-API-01`
- `./scripts/task_validate.sh CASEDOCK-FE-DOCIMPACT-API-01`

## Evidence Path

- `artifacts/CASEDOCK-FE-DOCIMPACT-API-01/`

## Done Definition

- Source file preview reflects selected reply source and current preview API context.
- Impact rows render backend status, deadline, task, fee, and file-status impact groups.
- Confirmation warning and risk alert render backend confirmation/risk data.
- Loading, error, and no-data states are visible and written in Simplified Chinese.
- Frontend lint, typecheck, build, and task gate pass with evidence.
