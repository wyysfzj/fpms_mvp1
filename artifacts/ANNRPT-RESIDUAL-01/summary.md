# Summary

## Commands
- `test -f docs/superpowers/specs/2026-04-05-annuity-report-residual-design.md`
- `test -f docs/superpowers/plans/2026-04-05-annuity-report-residual.md`
- `test -f tasks/postenhancement/backend/ANNRPT-RESIDUAL-01.md`
- `rg -n 'T_AnnuityTask|T_GovPayment|T_CaseReceipt|ANNRPT-AMOUNT-SPEC-01|success-rate' docs/superpowers/specs/2026-04-05-annuity-report-residual-design.md`

## Results
- Froze `RPT-ANN` residual capability map after the first-round annuity-task report slice.
- Separated the current implemented task-summary slice from spec-level annuity payable / paid / received reporting.
- Identified grouped amount reporting and monitoring success-rate semantics as the remaining residual buckets.
- Recommended `ANNRPT-AMOUNT-SPEC-01` as the next prerequisite slice.

## Notes
- This wave does not implement any annuity-report product behavior.
- `PayList` and `GovPayment` operational pages are not treated as automatic proof of `RPT-ANN` closure.
