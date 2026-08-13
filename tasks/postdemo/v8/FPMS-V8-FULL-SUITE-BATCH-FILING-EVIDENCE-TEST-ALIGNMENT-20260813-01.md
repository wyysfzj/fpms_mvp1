# FPMS V8 Full-Suite Batch Filing Evidence Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align four inherited batch-filing test files with the current reviewed final-evidence prerequisite.
Each positive submit case must own exactly one `FILING_PREP` package whose single present manifest
links one same-case FINAL, APPROVED, current evidence version with exact content hash and distinct
creator/reviewer. Existing lifecycle, date, task, document, idempotency and validation assertions
remain intact.

## Exact RED and closure

The approved predecessor matrix reaches seven failures across the four inherited files below.
Each positive submit creates a Case and filing material titles but no filing package/evidence; the
current resolver correctly returns `404 OFFICIAL_WORK_PACKAGE_NOT_FOUND` before mutation.

This task may only:

- extract the existing authoritative batch-filing evidence builder into a helper accepting an
  already-persisted case ID while retaining the original authoritative test behavior;
- enter `FILING_PREPARATION` through the existing bodyless resolve API, then call that exact
  helper for every positive submit case before the submit request;
- leave invalid submitted-date tests without final evidence so their earlier request validation
  and zero-side-effect assertions remain independently exercised.

## Non-closure

- No product, resolver, lifecycle, document, package, task, schema, migration, shared conftest or
  runtime fixture change.
- No monkeypatch of resolver/finalizer/lifecycle seams in inherited tests, no direct post-submit
  status projection, skip, xfail, assertion deletion or relaxed error.
- No claim over application-fee obligations, annuity lineage or other Final failures/Row283 close.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-BATCH-FILING-EVIDENCE-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_v8_batch_filing_lifecycle_adapter.py`
- `backend/tests/test_case_batch_filing_action.py`
- `backend/tests/test_case_batch_filing_side_effects.py`
- `backend/tests/test_apply_fee_limit_base_source.py`
- `backend/tests/test_apply_fee_limit_task_fields.py`

## Verification and acceptance

Run the exact four inherited files with the authoritative batch-filing lifecycle adapter, scoped
Ruff, format-check and exact diff-check. All tests must pass. Independent High review must approve
P0/P1/P2 `0/0/0` before continuing.

## Current verification result

The exact four inherited files plus the authoritative lifecycle adapter completed `15 passed` in
`7.64s`, with four pre-existing dependency/Pydantic warnings. The first GREEN attempt reached the
current projection gate; the final bytes enter filing preparation through the reviewed resolve API
instead of mutating projection fields. Scoped Ruff, format-check and exact diff-check pass.
