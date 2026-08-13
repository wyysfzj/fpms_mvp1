# FPMS V8 Full-Suite Case Field Selection Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align two inherited case-field tests reached after the approved case-create input alignment with
the current reviewed fee-reduction contract. A non-zero create uses a supported canonical value
and exact current applicant-scoped approval evidence. A full update that changes the applicant
composition explicitly resubmits the intended canonical fee-reduction selection.

## Exact RED and closure

The fresh exact 58-file predecessor verification completed `252 passed / 30 failed`. Exactly two
failures are this task's input boundary:

- `test_a2_full_fields_mvp_surface_persists_and_exposes_detail` sends unsupported legacy value
  `0.15` and receives `422 VALIDATION_ERROR` instead of reaching its field round-trip assertions;
- `test_update_case_full_persists_case_applicant_applicant_id` changes the applicant composition
  without an explicit fee-reduction selection and receives
  `409 FEE_REDUCTION_EXPLICIT_SELECTION_REQUIRED` before its link assertion.

This task may only:

- change the A2 scenario to current canonical `0.85`, seed one exact current approval for its two
  persisted applicants before create, and assert the same returned value;
- add explicit canonical `fee_reduction="0"` to the successful applicant-composition update;
- preserve all other field, applicant link, unknown applicant, blank normalization, validation,
  search and round-trip assertions byte-for-byte.

## Non-closure

- No product, schema, migration, seed, shared fixture/conftest, fee calculation, lifecycle,
  permission or registry change.
- No skip, xfail, assertion deletion, fallback default, compatibility coercion or adjacent cleanup.
- No claim over the other 28 Final-matrix failures, Row283 report/story/ledger/receipt, production
  activation or release.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-CASE-FIELD-SELECTION-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_case_a2_full_fields_readiness.py`
- `backend/tests/test_case_applicant_masterdata_link_write_path.py`

## Verification and acceptance

Run the two exact inherited files plus the authoritative create/update fee-reduction suites,
scoped Ruff and exact diff-check. All tests must pass. Independent High review must approve
P0/P1/P2 `0/0/0` before any next prerequisite begins.

## Current verification result

The exact two inherited files plus the authoritative create/update fee-reduction suites completed
`59 passed / 19 subtests` in `23.96s`. The only warnings are four pre-existing dependency and
Pydantic deprecations. Scoped Ruff, format-check and exact diff-check pass.
