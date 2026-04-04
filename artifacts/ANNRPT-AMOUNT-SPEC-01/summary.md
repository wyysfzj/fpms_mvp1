# Summary

## Commands
- `test -f docs/superpowers/specs/2026-04-05-annuity-report-amount-semantics-design.md`
- `test -f docs/superpowers/plans/2026-04-05-annuity-report-amount-semantics.md`
- `test -f tasks/postenhancement/backend/ANNRPT-AMOUNT-SPEC-01.md`
- `rg -n 'payable_amount|official_paid_amount|client_received_amount|GovPayment|CaseReceipt|ANNRPT-AMOUNT-01' docs/superpowers/specs/2026-04-05-annuity-report-amount-semantics-design.md`

## Results
- Froze `RPT-ANN` grouped amount semantics for：
  - `payable_amount`
  - `official_paid_amount`
  - `client_received_amount`
- Set `T_AnnuityTask` as payable authority, `T_GovPayment` as official-paid authority, and `T_CaseReceipt` as client-received authority.
- Froze `client / country / year` grouping lineage through `AnnuityTask -> Case`.
- Confirmed the next implementation slice can proceed without schema change.

## Notes
- This wave does not implement any annuity-report product behavior.
- `success-rate` remains explicitly deferred.
