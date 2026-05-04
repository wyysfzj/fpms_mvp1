# CASEDOCK-BE-GATE-RULES-01 — Case document material gate service rules

## Exact Closure Slice

Add one deterministic backend service module for Case Document Gate material rules: derive material requirements from a case context, match existing document inputs to those requirements, compute missing items, gate conclusion, hard-block status, afterfill audit requirement, and batch execution preview values.

## Explicit Non-Closure

No FastAPI route. No Pydantic API schema. No frontend code. No batch filing submit mutation. No database query behavior. No database schema or migration. No changes to existing case, document, task, or fee services.

## Remaining Follow-Up Task IDs

- `CASEDOCK-BE-INTAKE-GATE-API-01`
- `CASEDOCK-BE-CASE-GATE-API-01`
- `CASEDOCK-BE-BATCH-GATE-QUERY-01`
- `CASEDOCK-BE-BATCH-GATE-SUBMIT-01`

None of those follow-up tasks may be implemented here.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Low. This task creates one new service module and one new service test file only. |
| prereq_dependency_density | High. Later API and batch submit tasks depend on this service contract. |
| be_fe_coupling | Medium. The service fields are backend-internal for this task, but later API schemas will expose them to frontend integration tasks. |
| evidence_cost | Medium. Requires TDD red/green evidence, task-scoped Ruff, targeted pytest, and task gate artifacts. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/backend/CASEDOCK-BE-GATE-RULES-01.md`
- `backend/app/modules/cases/document_gate_service.py`
- `backend/tests/test_case_document_gate_service.py`
- `artifacts/CASEDOCK-BE-GATE-RULES-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/backend/CASEDOCK-BE-GATE-RULES-01.md`
- `cd backend && pytest tests/test_case_document_gate_service.py -q`
- `ruff check --fix backend/app/modules/cases/document_gate_service.py backend/tests/test_case_document_gate_service.py`
- `ruff format backend/app/modules/cases/document_gate_service.py backend/tests/test_case_document_gate_service.py`
- `ruff check backend/app/modules/cases/document_gate_service.py backend/tests/test_case_document_gate_service.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-BE-GATE-RULES-01`
- `./scripts/task_validate.sh CASEDOCK-BE-GATE-RULES-01`

## Evidence Path

- `artifacts/CASEDOCK-BE-GATE-RULES-01/`
