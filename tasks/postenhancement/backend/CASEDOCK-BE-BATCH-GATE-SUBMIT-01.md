# CASEDOCK-BE-BATCH-GATE-SUBMIT-01 — Batch filing hard-block submit enforcement

## Exact Closure Slice

Update the existing batch filing submit service so selected hard-block cases are rejected before any case status, submitted date, document, task, or task-log mutation occurs.

## Explicit Non-Closure

No batch candidate query response changes. No route path change. No frontend code. No case intake/detail gate behavior. No document impact preview behavior. No database schema or migration.

## Remaining Follow-Up Task IDs

- `CASEDOCK-QA-REALAPI-E2E-01`

None of those follow-up tasks may be implemented here.

## Story Shape Classification

| Field | Value |
|---|---|
| shared_file_density | Medium. This task serially owns `backend/app/modules/cases/service.py` and batch filing submit tests. |
| prereq_dependency_density | High. Depends on `CASEDOCK-BE-GATE-RULES-01` and `CASEDOCK-BE-BATCH-GATE-QUERY-01`. |
| be_fe_coupling | Medium. Backend enforcement must align with frontend hard-block UI, but no frontend file is in scope. |
| evidence_cost | Medium. Requires hard-block mutation-safety pytest, existing submit regression tests, task-scoped Ruff, and task gate artifacts. |

chosen_runbook: `P0-prereq-heavy-story`

## Allowed Files

- `tasks/postenhancement/backend/CASEDOCK-BE-BATCH-GATE-SUBMIT-01.md`
- `backend/app/modules/cases/service.py`
- `backend/tests/test_case_batch_filing_action.py`
- `backend/tests/test_case_batch_filing_side_effects.py`
- `backend/tests/test_case_batch_filing_document_gate_submit.py`
- `artifacts/CASEDOCK-BE-BATCH-GATE-SUBMIT-01/**`

## Verification Commands

- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py check-task tasks/postenhancement/backend/CASEDOCK-BE-BATCH-GATE-SUBMIT-01.md`
- `cd backend && pytest tests/test_case_batch_filing_action.py tests/test_case_batch_filing_side_effects.py tests/test_case_batch_filing_document_gate_submit.py -q`
- `cd backend && ruff check --fix app/modules/cases/service.py tests/test_case_batch_filing_action.py tests/test_case_batch_filing_side_effects.py tests/test_case_batch_filing_document_gate_submit.py`
- `cd backend && ruff format app/modules/cases/service.py tests/test_case_batch_filing_action.py tests/test_case_batch_filing_side_effects.py tests/test_case_batch_filing_document_gate_submit.py`
- `cd backend && ruff check app/modules/cases/service.py tests/test_case_batch_filing_action.py tests/test_case_batch_filing_side_effects.py tests/test_case_batch_filing_document_gate_submit.py`
- `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate CASEDOCK-BE-BATCH-GATE-SUBMIT-01`
- `./scripts/task_validate.sh CASEDOCK-BE-BATCH-GATE-SUBMIT-01`

## Evidence Path

- `artifacts/CASEDOCK-BE-BATCH-GATE-SUBMIT-01/`
