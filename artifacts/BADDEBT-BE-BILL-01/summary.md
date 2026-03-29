# BADDEBT-BE-BILL-01 Evidence Summary

- Exact closure slice: `GET /bills/{bill_id}` now returns bill bad-debt status/substatus, a bad-debt voucher summary, a recovery list, total recovered amount, and remaining bad-debt amount.
- Non-closure respected: no bad-debt write actions, no frontend changes, no reporting changes, no model or migration changes.
- Verification:
  - `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_detail_api.py` passed.
  - `cd backend && pytest -q tests/test_billing_bad_debt_detail_api.py` passed (`2 passed`).
