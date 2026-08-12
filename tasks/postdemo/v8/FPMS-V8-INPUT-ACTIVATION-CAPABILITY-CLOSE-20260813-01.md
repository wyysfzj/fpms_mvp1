# FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01

Status: READY / NOT STARTED
Risk: PROTECTED
Task Contract Profile: `TC-QA`
Execution role: QA-only

## Exact Closure Slice

Verify the two input capabilities and their inherited Full/Final evidence may close as
`CAPABILITY_READY + CONFIG_REQUIRED`: absent, invalid, unreviewed, expired, revoked, mismatched,
or `TEST_ONLY` production input yields `409 / NO WRITE`; permissions, audit, lineage, version,
hash, scope, interval, review, replacement, and domain separation remain proven.

## Explicit Non-Closure

No product fix, source input, configuration mutation, lane manifest, catalog/ledger edit, release,
positive decision, waived negative evidence, or assertion that either production input is active.

## Dependencies

- Both exact lane manifests and all their original members independently accepted.
- WB-I1, row 214, WB-I2, WB-I3, rows 215-222, and row 278 accepted in order:
  `WB-I1 -> row 214 -> WB-I2 -> WB-I3 -> rows 215-222 -> row 278`.
- Service-price rows 223-229 independently accepted.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md`
- `docs/product/v8/reviews/V8-INPUT-ACTIVATION-CAPABILITY-CURRENT-ADOPTION.md`
- `backend/tests/test_v8_input_activation_capability_close.py`

## Targeted RED / GREEN

Write a focused QA RED for missing capability evidence; run the named negative slices; materialize
only the QA receipt; rerun GREEN and exact diff checks. `TEST_ONLY` isolation and missing-input
`409 / NO WRITE` are decisive.

## Serialized Ownership

Run after both lanes, serialize any SQLite-writing verification, and do not overlap Full, Final,
ledger, or release owners.

## Evidence Path

- Exact Git commit/range plus focused QA RED/GREEN, decisive negative-path, diff, scope, and
  independent-review results. Do not create a legacy artifact directory.

## Rollback Boundary

Revert only this task's exact commit and owned paths before dependent tasks start. Remove only
the owned QA task update, current-adoption record, and focused capability-close test before Full;
do not reverse any accepted lane task or change configuration. Leave accepted predecessors and production inputs untouched.

## Independent Close

Independent High review binds exact current bytes and decisive logs with zero findings.
`CONFIG_REQUIRED` is acceptable only with verified negative-path evidence. This QA-only close
may establish `CAPABILITY_READY` but never claims production activation.
