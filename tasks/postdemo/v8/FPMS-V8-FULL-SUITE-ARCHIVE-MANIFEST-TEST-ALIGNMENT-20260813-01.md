# FPMS V8 Full-Suite Archive Manifest Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Align the inherited receipt/archive API fixture with the current package-kind manifest contract.
An OA reply package carries `OA_MODIFIED_CLAIMS`; a filing-preparation package carries the required
`FILING_FULL_WORD`. The archive test continues to prove that missing receipt blocks and a complete
explicit override records follow-up facts.

## Exact RED and closure

The fresh predecessor matrix reaches one failure in
`test_archive_api_requires_receipt_unless_override_is_complete`: its helper creates a
`FILING_PREP` package but always labels the only source attachment/manifest
`OA_MODIFIED_CLAIMS`. Current evaluation correctly adds `MANIFEST_MISSING:FILING_FULL_WORD`, a
maintenance blocker that receipt override cannot bypass, and returns 409.

This task may only derive the source file role from the explicit package kind and persist the same
role on its attachment and manifest. All receipt metadata, archive, blocker, override, follow-up
and durable-row assertions remain unchanged.

## Non-closure

- No product, schema, migration, package evaluator, archive policy, evidence, shared fixture or
  conftest change.
- No bypass of manifest maintenance blockers, no skip/xfail/assertion deletion/fallback role.
- No claim over other Final-matrix failures or Row283 close/release.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-SUITE-ARCHIVE-MANIFEST-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_pd_p1_receipt_archive_api.py`

## Verification and acceptance

Run the exact inherited API file with current work-package service, filing full-word gate and
receipt lifecycle authority suites, then scoped Ruff, format-check and diff-check. Independent
High review must approve P0/P1/P2 `0/0/0` before continuing.

## Current verification result

The inherited API plus work-package service, filing full-word gate and receipt lifecycle authority
suites completed `15 passed / 6 subtests` in `6.55s`, with four pre-existing dependency/Pydantic
warnings. Scoped Ruff, format-check and exact diff-check pass.
