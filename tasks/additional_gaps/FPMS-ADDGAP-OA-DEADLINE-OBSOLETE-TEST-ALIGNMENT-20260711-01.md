# FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 27 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the five allowlisted obsolete OA deadline tests and fixtures with the approved structured deadline contracts: executable OA creation uses a confirmed explicit due, missing or unconfirmed due fails closed, and raw-date-only legacy data remains non-executable. Preserve each test's original non-deadline coverage while removing stale expectations that executable OA tasks may use template-day fallback or raw `OfficialDueDate` alone.

## Explicit Non-Closure

Do not modify product code, seed code, migrations, schemas, services, APIs, manifests, specs, or plans. Do not delete coverage or weaken the approved Task 24/Task 27 confirmed-explicit-due and fail-closed behavior. Do not add new product behavior or absorb Task 27 acceptance or Task 47 final-close work.

## Dependencies

- `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01` (`PASS`)
- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01` acceptance
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_b_official_due_date_task_generation.py`
- `backend/tests/test_document_wizard_batch_create.py`
- `backend/tests/test_task_generation.py`
- `backend/tests/test_task_template.py`
- `backend/tests/test_addgap_document_deadline_read_projection.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other source, test, task, manifest, specification, plan, shared ownership file, or artifact family is authorized.

## Runtime Contracts

- Permission: unchanged; test-fixture alignment only.
- Status codes/errors: preserve approved Task 24/Task 27 semantics (`201` only with valid confirmed explicit due; missing/unconfirmed executable OA due returns `409`; payload shape and cross-field errors remain `422`/`400` as specified).
- Response envelope: unchanged.
- SQLite: serialize every pytest invocation through `/tmp/fpms_addgap_sqlite_test.lock`; tests use existing SQLite-safe fixtures.
- Simplified Chinese UI: N/A.

## Verification Commands

- Serialized targeted tests for exactly the five allowlisted test files:

  ```bash
  while ! mkdir /tmp/fpms_addgap_sqlite_test.lock 2>/dev/null; do sleep 1; done
  trap 'rmdir /tmp/fpms_addgap_sqlite_test.lock' EXIT INT TERM
  cd backend
  .venv/bin/pytest -q \
    tests/test_b_official_due_date_task_generation.py \
    tests/test_document_wizard_batch_create.py \
    tests/test_task_generation.py \
    tests/test_task_template.py \
    tests/test_addgap_document_deadline_read_projection.py
  ```

- Scoped Ruff:

  ```bash
  cd backend && \
    .venv/bin/ruff check --fix \
      tests/test_b_official_due_date_task_generation.py \
      tests/test_document_wizard_batch_create.py \
      tests/test_task_generation.py \
      tests/test_task_template.py \
      tests/test_addgap_document_deadline_read_projection.py && \
    .venv/bin/ruff format \
      tests/test_b_official_due_date_task_generation.py \
      tests/test_document_wizard_batch_create.py \
      tests/test_task_generation.py \
      tests/test_task_template.py \
      tests/test_addgap_document_deadline_read_projection.py && \
    .venv/bin/ruff check \
      tests/test_b_official_due_date_task_generation.py \
      tests/test_document_wizard_batch_create.py \
      tests/test_task_generation.py \
      tests/test_task_template.py \
      tests/test_addgap_document_deadline_read_projection.py
  ```

- Scope:

  ```bash
  git diff --check -- \
    backend/tests/test_b_official_due_date_task_generation.py \
    backend/tests/test_document_wizard_batch_create.py \
    backend/tests/test_task_generation.py \
    backend/tests/test_task_template.py \
    backend/tests/test_addgap_document_deadline_read_projection.py \
    tasks/additional_gaps/FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01.md
  ```

- Evidence and task gate:

  ```bash
  ./scripts/evidence_run.sh FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01 <step> <command...>
  ./scripts/task_validate.sh FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01
  ```

## Evidence Path

- `artifacts/FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Execution and Close-Audit Contract

This task is supplemental to the frozen 47-entry program manifest and must not be inserted into or otherwise modify that manifest, its approved specification, or its plan. It must pass its own evidence and task gate before Task 27 acceptance, and Task 47 must record this supplemental task ID, evidence, gate result, and closure decision in the final close audit.

## Done Definition

All five allowlisted test files preserve their original coverage while using confirmed structured OA deadlines or asserting fail-closed legacy/unconfirmed behavior as appropriate; the exact serialized targeted suite passes; scoped Ruff and scope checks pass; required dirty-baseline and completion evidence exists; the individual task gate passes; the exact closure slice is complete; and the explicit non-closure boundary is respected. Only then may this supplemental task be reported `PASS` and used to unblock Task 27 acceptance and Task 47 final close.
