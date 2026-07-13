# FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 42 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the allowlisted legacy grant state-machine test's actionable fixtures with Task42's confirmed
lineage precondition, and extend its exact state-response shape assertions with
`lineage_status`, `source_document_id`, `deadline_source`, and `deadline_confirmed_at`. Preserve all
existing workflow-state, permission, transition, invalid-action, and case-advance assertions.

## Explicit Non-Closure

Do not modify product code, Task42's target test, worklist tests, spec/plan/manifest, or any unrelated
assertion. Do not weaken exact response shape, change expected workflow states, or add legacy/
superseded gate coverage already owned by Task42.

## Dependencies

- `FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01` acceptance
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_grant_fee_state_machine_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/**`

No other source, test, task, plan, manifest, or artifact family is authorized.

## Runtime Contracts

- Test-only; permission, status-code, envelope, workflow-state, and product behavior remain unchanged.
- Fixtures that exercise ordinary actions must use a real same-case source document and a complete
  confirmed deadline lineage tuple; no production backfill or invented product data is authorized.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_grant_fee_state_machine_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_grant_fee_state_machine_api.py && .venv/bin/ruff format tests/test_grant_fee_state_machine_api.py && .venv/bin/ruff check tests/test_grant_fee_state_machine_api.py`
- Scope: `git diff --check -- backend/tests/test_grant_fee_state_machine_api.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest. It must pass independent review, evidence
validation, and its task gate before Task42 acceptance; Task47 must record its closure.

## Done Definition

Only the state-test fixture helper and exact lineage response assertions change; the full state
test file passes with all prior behavioral assertions preserved; scoped Ruff/scope, independent
review, atomic validation, and task gate pass. Only then may this task be `PASS`.
