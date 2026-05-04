# CASEDOCK-BE-BATCH-GATE-QUERY-01 — Batch filing final material gate query

## Exact Closure Slice

Extend the existing batch filing candidates query behavior so each candidate includes final material count, missing items, gate conclusion, hard-block status, afterfill audit requirement, and execution preview data.

## Explicit Non-Closure

No batch filing submit mutation change. No route path change. No frontend code. No case intake/detail gate behavior. No document impact preview behavior. No database schema or migration.

## Remaining Follow-Up Task IDs

- `CASEDOCK-BE-BATCH-GATE-SUBMIT-01`
- `CASEDOCK-FE-GATE-API-CONTRACT-01`
- `CASEDOCK-FE-BATCHFILING-API-01`

None of those follow-up tasks may be implemented here.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. This task serially owns `backend/app/modules/cases/service.py` and `backend/app/modules/cases/schemas.py`. |
| prereq_dependency_density | High. Depends on `CASEDOCK-BE-GATE-RULES-01`; submit enforcement depends on this same gate interpretation. |
| be_fe_coupling | High. The enriched candidate fields will be consumed by the frontend batch filing integration task. |
| evidence_cost | Medium. Requires targeted query pytest, task-scoped Ruff, and task gate artifacts. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/backend/CASEDOCK-BE-BATCH-GATE-QUERY-01.md`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/tests/test_case_batch_filing_query.py`
- `backend/tests/test_case_batch_filing_document_gate_query.py`
- `artifacts/CASEDOCK-BE-BATCH-GATE-QUERY-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/backend/CASEDOCK-BE-BATCH-GATE-QUERY-01.md`
- `cd backend && pytest tests/test_case_batch_filing_query.py tests/test_case_batch_filing_document_gate_query.py -q`
- `cd backend && ruff check --fix app/modules/cases/service.py app/modules/cases/schemas.py tests/test_case_batch_filing_query.py tests/test_case_batch_filing_document_gate_query.py`
- `cd backend && ruff format app/modules/cases/service.py app/modules/cases/schemas.py tests/test_case_batch_filing_query.py tests/test_case_batch_filing_document_gate_query.py`
- `cd backend && ruff check app/modules/cases/service.py app/modules/cases/schemas.py tests/test_case_batch_filing_query.py tests/test_case_batch_filing_document_gate_query.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-BE-BATCH-GATE-QUERY-01`
- `./scripts/task_validate.sh CASEDOCK-BE-BATCH-GATE-QUERY-01`

## Evidence Path

- `artifacts/CASEDOCK-BE-BATCH-GATE-QUERY-01/`
