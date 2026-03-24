# PE-BE-FE-03

Status: PASS

Scope:
- `backend/app/modules/fees/service.py`
- `backend/tests/test_annuity_e2e.py`

Changes:
- implemented a first Batch 3 fee-calculation slice for `PER_CLAIM`
- added reduction and discount application using existing `calc_params`
- preserved `FIXED` behavior and left other calc modes unchanged for later slices
- added regression coverage proving `PER_CLAIM` amount calculation with reduction and discount

Validation:
- `ruff check backend/app/modules/fees/api.py backend/app/modules/fees/service.py backend/app/modules/fees/schemas.py backend/tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k 'calculate_fee_amount_per_claim_with_reduction_and_discount or annuity_generate_drafts_pay_list_gov_payment_chain'`

Notes:
- no schema change
- no Batch 4 spillover
- no document generation behavior introduced
- this is one gateable calc slice only; other calc modes remain for later Batch 3 tasks
