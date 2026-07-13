# FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01

Status: PASS
Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Wave: Supplemental prerequisite before Task 38 acceptance
Executor role: Backend Developer / worker

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Align the single obsolete Task33 `seed_dev` expectation in
`test_addgap_notice_oa_acceptance_activation.py` after approved Task38 activation: row009 is now the
seventh executable row with exact grant semantics, while the original six OA/acceptance semantics
and all remaining 53 reference-only rows stay unchanged.

## Explicit Non-Closure

Do not modify product/seed/catalog or any other test/spec/plan/manifest. Do not alter Task38
implementation, activate another row, or weaken Task33 six-row invariants and idempotency coverage.

## Dependencies

- `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01` (`PASS`)
- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01` implementation at `REVIEW`

## Remaining Follow-Up Task IDs

- `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01` acceptance
- `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

## Allowed Files

- `backend/tests/test_addgap_notice_oa_acceptance_activation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

No other file or artifact family is authorized.

## Runtime Contracts

- Test-only alignment; permission/status/envelope unchanged.
- SQLite: every pytest invocation uses `/tmp/fpms_addgap_sqlite_test.lock`.

## Verification Commands

- RED/GREEN: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_oa_acceptance_activation.py tests/test_addgap_notice_grant_activation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_addgap_notice_oa_acceptance_activation.py && .venv/bin/ruff format tests/test_addgap_notice_oa_acceptance_activation.py && .venv/bin/ruff check tests/test_addgap_notice_oa_acceptance_activation.py`
- Scope: `git diff --check -- backend/tests/test_addgap_notice_oa_acceptance_activation.py tasks/additional_gaps/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01.md`

## Evidence Path

- `artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/**`

## Supplemental Close Contract

This task is outside the frozen 47-entry manifest. It must independently pass review/evidence/gate
before Task38 acceptance; Task47 must record its closure.

## Done Definition

The one stale seed_dev expectation is aligned to exact seven-row target state; original six and
remaining 53 semantics remain asserted; target passes with Ruff/scope/secret-safe evidence,
independent review, atomic validation, and task gate. Only then may this task be `PASS`.
