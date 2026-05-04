# CASEDOCK-BE-INTAKE-GATE-API-01 — Case intake document gate API

## Exact Closure Slice

Add one permission-protected GET endpoint for case intake document gate preview that returns material requirements, matched source documents, missing items, material roles, gate conclusion, hard-block status, afterfill audit requirement, and suggested actions from query inputs and optional existing document ids.

## Explicit Non-Closure

No case creation mutation change. No document upload implementation. No batch filing behavior. No case detail gate endpoint. No document impact preview endpoint. No frontend code. No database schema or migration.

## Remaining Follow-Up Task IDs

- `CASEDOCK-FE-GATE-API-CONTRACT-01`
- `CASEDOCK-FE-CASECREATE-API-01`

None of those follow-up tasks may be implemented here.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. This task serially owns `backend/app/modules/cases/api.py` and `backend/app/modules/cases/schemas.py`. |
| prereq_dependency_density | High. Depends on `CASEDOCK-BE-GATE-RULES-01` service behavior. |
| be_fe_coupling | High. The response contract will be consumed by the frontend case create integration task. |
| evidence_cost | Medium. Requires targeted API pytest, task-scoped Ruff, and task gate artifacts. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/backend/CASEDOCK-BE-INTAKE-GATE-API-01.md`
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/schemas.py`
- `backend/tests/test_case_intake_document_gate_api.py`
- `artifacts/CASEDOCK-BE-INTAKE-GATE-API-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/backend/CASEDOCK-BE-INTAKE-GATE-API-01.md`
- `cd backend && pytest tests/test_case_intake_document_gate_api.py -q`
- `cd backend && ruff check --fix app/modules/cases/api.py app/modules/cases/schemas.py tests/test_case_intake_document_gate_api.py`
- `cd backend && ruff format app/modules/cases/api.py app/modules/cases/schemas.py tests/test_case_intake_document_gate_api.py`
- `cd backend && ruff check app/modules/cases/api.py app/modules/cases/schemas.py tests/test_case_intake_document_gate_api.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-BE-INTAKE-GATE-API-01`
- `./scripts/task_validate.sh CASEDOCK-BE-INTAKE-GATE-API-01`

## Evidence Path

- `artifacts/CASEDOCK-BE-INTAKE-GATE-API-01/`
