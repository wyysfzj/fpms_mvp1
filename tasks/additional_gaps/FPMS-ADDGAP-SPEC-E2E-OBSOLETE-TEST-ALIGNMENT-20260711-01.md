# FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before final full-suite close
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the single `test_spec_alignment_e2e.py` integration suite with approved explicit-deadline and
grant pre-instruction contracts: OA and grant document creation use confirmed official due tuples;
OA still creates the correct task; grant creates its source-lineage task but no generic auto draft;
the existing billing/payment/offset/reversal chain starts from an explicit fee draft. Preserve both
end-to-end workflows and their downstream assertions.

## Explicit Non-Closure

Do not modify product, seed, migration, schema, service, API, manifest, specification, plan, or any
other test. Do not implement client instruction, catalog activation, replacement, UI, or final E2E.
Do not delete or weaken OA lifecycle or financial-chain coverage.

## Dependencies

- `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01` (`PASS`)
- `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01` (`PASS`)
- `FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01` (`PASS`)

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_spec_alignment_e2e.py`
- `tasks/additional_gaps/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other source, test, task, manifest, specification, plan, shared ownership file, or artifact family
is authorized.

## Runtime Contracts

- Permission/status/envelope: unchanged; test-only alignment uses existing public APIs.
- SQLite: every pytest invocation is serialized through `/tmp/fpms_addgap_sqlite_test.lock`.
- Simplified Chinese UI: N/A.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_spec_alignment_e2e.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_spec_alignment_e2e.py && .venv/bin/ruff format tests/test_spec_alignment_e2e.py && .venv/bin/ruff check tests/test_spec_alignment_e2e.py`
- Scope: `git diff --check -- backend/tests/test_spec_alignment_e2e.py tasks/additional_gaps/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Execution and Close-Audit Contract

This task remains outside the frozen 47-entry manifest/spec/plan. Task47 must record its task ID,
evidence, gate, and closure decision before final full-suite acceptance.

## Done Definition

Both E2E tests pass with explicit due/source and no grant auto draft while preserving downstream OA
and financial assertions; scoped Ruff/scope, credential-safe RED/GREEN, independent review, atomic
validation, and task gate pass; exact closure and non-closure are respected. Only then may this task
be `PASS`.
