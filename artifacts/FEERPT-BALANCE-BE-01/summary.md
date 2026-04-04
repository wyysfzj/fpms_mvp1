# Summary

## Commands
- `python3 -m ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_fee_report.py`
- `cd backend && pytest -q tests/test_fee_report.py`

## Results
- Extended `GET /fees/drafts` summary with:
  - `billed_amount`
  - `received_amount`
  - `unpaid_balance_amount`
  - `partially_received_bill_count`
- Implemented bill-lineage aggregation from `Bill / BillItem` limited to AR bills with `draft_id` lineage.
- Confirmed partially received bills count only when `0 < balance < amount`.
- Confirmed hand-made bill rows without `draft_id` are excluded from the balance summary slice.

## Notes
- This task does not render any FE UI.
- Trend reporting and per-fee-type billed/received breakdown remain deferred.
