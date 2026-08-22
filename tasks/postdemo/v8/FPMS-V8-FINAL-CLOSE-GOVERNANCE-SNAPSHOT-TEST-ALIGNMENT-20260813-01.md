# FPMS V8 Final-Close Governance Snapshot Test Alignment

Status: `IMPLEMENTATION`
Risk: `PROTECTED`

## Observable outcome

Keep adopted Row281 and Row282 governance contracts bound to their exact Git adoption snapshots
instead of mutable current ledger/test inventory. Refresh only the independently reviewed current
whole-file hashes for the Row282 and Row283 task appendices. The missing Final report remains the
sole expected Row283 RED.

## RED and closure

The current last-failed tranche has four pre-Row283 metadata failures: Row281 dynamically includes
four later V8 tests; Row281 and Row282 contracts compare adopted ledger state to later row changes;
and two current task whole-file hashes predate reviewed appendices. Pin historical assertions to
exact reachable adoption commits and retain exact current-byte pins for appendix checks.

## Non-closure

No product/API/UI/schema/migration/seed/catalog/ledger/matrix/report/story/Row283 adoption change;
no result rewriting, test skip/xfail, broad rerun or release claim. The Final report remains absent.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-GOVERNANCE-SNAPSHOT-TEST-ALIGNMENT-20260813-01.md`
- `backend/tests/test_v8_inherited_regression_matrix_contract.py`
- `backend/tests/test_v8_row282_external_path_ownership_adoption.py`
- `backend/tests/test_v8_input_activation_decoupling_contract.py`

## Verification

Run the three exact contracts plus the expected-RED Final-report node separately; scoped Ruff,
format-check and exact diff-check. Independent High review requires P0/P1/P2 `0/0/0`.

## Current verification result

The three corrected governance contracts complete `11 passed` with two pre-existing warnings.
Scoped Ruff and exact diff-check pass; unrelated formatter churn was restored. The exact Final
report node still fails only with the expected missing `docs/product/v8/final-close-report.json`,
preserving Row283 RED and avoiding any premature release claim.
