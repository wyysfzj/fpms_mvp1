# FPMS V8 Final-Suite Governance Snapshot Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Exact Closure Slice

Align two governance-only contracts after independently reviewed append-only adoption and Row283
pre-report bytes. The remediation adoption contract must prove its historical append at exact
adoption commit `e19d615c84c4c2d2afd10dcc440c4f2683fc2b77` and prove that exact story remains
unchanged in the current ledger even when a later reviewed story is appended. The activation
appendix contract must pin the current whole-file SHA-256 of the amended Row283 task.

## Explicit Non-Closure

No product/test behavior/domain/schema/migration/seed/ledger/report/story/release change; no
skip/xfail/assertion deletion; no arbitrary story order acceptance or dynamic task-hash trust.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FINAL-SUITE-GOVERNANCE-SNAPSHOT-ALIGNMENT-20260813-01.md`
- `backend/tests/test_v8_final_matrix_remediation_adoption.py`
- `backend/tests/test_v8_input_activation_decoupling_contract.py`

## Verification Commands

- `cd backend && .venv/bin/pytest -q tests/test_v8_final_matrix_remediation_adoption.py::test_ledger_adoption_is_append_only_when_materialized tests/test_v8_input_activation_decoupling_contract.py::test_latest_wins_appendix_changes_only_prerequisite_interpretation`
- `cd backend && .venv/bin/ruff check tests/test_v8_final_matrix_remediation_adoption.py tests/test_v8_input_activation_decoupling_contract.py`
- `cd backend && .venv/bin/ruff format --check tests/test_v8_final_matrix_remediation_adoption.py`; the second historical contract has pre-existing whole-file formatter drift outside this one-line hash update and must not be reformatted by this task.
- `git diff --check -- tasks/postdemo/v8/FPMS-V8-FINAL-SUITE-GOVERNANCE-SNAPSHOT-ALIGNMENT-20260813-01.md backend/tests/test_v8_final_matrix_remediation_adoption.py backend/tests/test_v8_input_activation_decoupling_contract.py`

Independent High review requires P0/P1/P2 `0/0/0` before current-byte adoption or Final matrix
resume.

## Remaining Follow-Up Task IDs

- `FPMS-V8-FINAL-CLOSE-20260712-01`

## Evidence Path

- `artifacts/FPMS-V8-FINAL-SUITE-GOVERNANCE-SNAPSHOT-ALIGNMENT-20260813-01/`

## Current Verification Result

The exact two-node RED reproduced both full-suite failures. GREEN passes `2 passed`: the historical
adoption is verified at its exact ledger-only commit and remains an unchanged current prefix; the
Row283 task hash is pinned to its current accepted whole-file bytes. Scoped Ruff, focused-file
format-check and exact diff-check pass. The other historical contract's pre-existing formatter
drift remains untouched and outside the changed hash line. Independent High acceptance remains
required.
