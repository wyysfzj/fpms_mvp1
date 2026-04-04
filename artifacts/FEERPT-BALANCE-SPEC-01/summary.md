# Summary

## Commands
- `test -f docs/superpowers/specs/2026-04-04-fee-report-balance-semantics-design.md`
- `test -f docs/superpowers/plans/2026-04-04-fee-report-balance-semantics.md`
- `test -f tasks/postenhancement/backend/FEERPT-BALANCE-SPEC-01.md`
- `rg -n 'Bill\.balance|Bill\.amount - Bill\.balance|CaseReceipt|T_Offset|FEERPT-BALANCE-01' docs/superpowers/specs/2026-04-04-fee-report-balance-semantics-design.md`

## Results
- Froze `RPT-FEE` billed / received / unpaid semantics.
- Set `T_Bill / T_BillItem` as billed authority and `Bill.balance` as unpaid authority.
- Set `Bill.amount - Bill.balance` as the primary received metric and kept `T_CaseReceipt` as a derived cross-check carrier.
- Confirmed the next implementation slice can proceed without schema change.

## Notes
- This wave does not implement any fee-report product behavior.
- Hand-made bill rows without `draft_id` lineage remain explicitly deferred.
