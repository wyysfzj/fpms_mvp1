# BADDEBT-BE-REC-01 Summary

- Task: `BADDEBT-BE-REC-01`
- Runbook: `P0-prereq-heavy-story`
- Role: `worker`
- Closure slice: implement bad-debt recovery write action only for existing AR bill bad-debt vouchers
- Explicit non-closure: restore/reversal, mark/transfer, frontend, reporting, legacy bad-debt cleanup

## Modified files

- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/billing/service.py`
- `backend/tests/test_billing_bad_debt_recovery.py`

## Verification

- `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_recovery.py` passed.
- `cd backend && pytest -q tests/test_billing_bad_debt_recovery.py` passed (`2 passed`).

## Result

- Recovery writes create one independent recovery record per call.
- Multiple partial recoveries are supported.
- Total recovery amount cannot exceed the bad-debt voucher amount.
- Bill detail responses now reflect updated bad-debt recovery totals and remaining balance.
