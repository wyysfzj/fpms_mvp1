# CASEDOCK-BE-DOC-IMPACT-API-01 — Document create impact preview API

## Exact Closure Slice

Add one permission-protected POST endpoint for document create impact preview that returns status impact, deadline impact, task impact, fee impact, file status impact, confirmation requirements, and risk tips from pending document create inputs.

## Explicit Non-Closure

No document creation mutation. No existing document wizard endpoint behavior change. No case document gate endpoint. No batch filing behavior. No frontend code. No database schema or migration.

## Remaining Follow-Up Task IDs

- `CASEDOCK-FE-GATE-API-CONTRACT-01`
- `CASEDOCK-FE-DOCIMPACT-API-01`

None of those follow-up tasks may be implemented here.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. This task serially owns document API, schema, and service files. |
| prereq_dependency_density | Medium. Depends on existing document template fields and existing case/document validation behavior. |
| be_fe_coupling | High. The response contract will be consumed by the frontend document create integration task. |
| evidence_cost | Medium. Requires targeted API pytest, task-scoped Ruff, and task gate artifacts. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/backend/CASEDOCK-BE-DOC-IMPACT-API-01.md`
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_document_impact_preview_api.py`
- `artifacts/CASEDOCK-BE-DOC-IMPACT-API-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/backend/CASEDOCK-BE-DOC-IMPACT-API-01.md`
- `cd backend && pytest tests/test_document_impact_preview_api.py -q`
- `cd backend && ruff check --fix app/modules/documents/api.py app/modules/documents/schemas.py app/modules/documents/service.py tests/test_document_impact_preview_api.py`
- `cd backend && ruff format app/modules/documents/api.py app/modules/documents/schemas.py app/modules/documents/service.py tests/test_document_impact_preview_api.py`
- `cd backend && ruff check app/modules/documents/api.py app/modules/documents/schemas.py app/modules/documents/service.py tests/test_document_impact_preview_api.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-BE-DOC-IMPACT-API-01`
- `./scripts/task_validate.sh CASEDOCK-BE-DOC-IMPACT-API-01`

## Evidence Path

- `artifacts/CASEDOCK-BE-DOC-IMPACT-API-01/`
