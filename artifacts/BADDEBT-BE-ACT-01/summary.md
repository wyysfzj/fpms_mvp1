# BADDEBT-BE-ACT-01 Summary

- Task: `BADDEBT-BE-ACT-01`
- Runbook: `P0-prereq-heavy-story`
- Role: `worker`
- Closure slice: add AR bill bad-debt write actions for manual mark and partial-payment transfer only
- Explicit non-closure: recovery writes, restore/reversal, frontend, reporting, legacy lifecycle cleanup

## Modified files

- `backend/app/modules/billing/api.py`
- `backend/app/modules/billing/schemas.py`
- `backend/app/modules/billing/service.py`
- `backend/tests/test_billing_bad_debt_actions.py`

## Verification

- `ruff check backend/app/modules/billing/api.py backend/app/modules/billing/schemas.py backend/app/modules/billing/service.py backend/tests/test_billing_bad_debt_actions.py` passed.
- `cd backend && pytest -q tests/test_billing_bad_debt_actions.py -k 'mark or transfer'` passed (`2 passed`).
- `./scripts/task_validate.sh BADDEBT-BE-ACT-01` passed.

## Result

- Manual mark creates one bad-debt voucher and returns bill detail with bad-debt fields.
- Partial-payment transfer creates one bad-debt voucher for the remaining balance only and returns bill detail with bad-debt fields.
- Repeated calls reuse the same voucher for the same bill.
- Task gate passed after evidence generation.
