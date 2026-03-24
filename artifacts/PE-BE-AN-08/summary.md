# PE-BE-AN-08

Status: PASS

Scope:
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_annuity_e2e.py`

Changes:
- added a focused annuity-chain slice to normalize `currency` input in draft generation
- `generate_fee_drafts_from_annuity_tasks` now normalizes currency to uppercase with fallback `CNY`
- normalized currency is used consistently for fee-rate lookup, draft storage, and success payload output

Failing proof first:
- added `test_annuity_generate_drafts_normalizes_currency_case`
- before fix, request with `"currency": "cny"` failed expectation (`currency` returned as `cny`)

Validation:
- `ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_annuity_e2e.py`
- `cd backend && pytest -q tests/test_annuity_e2e.py -k 'annuity_generate_drafts_normalizes_currency_case or annuity_generate_drafts_pay_list_gov_payment_chain'`

Notes:
- no schema/migration changes
- no Batch 4 spillover
- no document generation behavior added
- this is one gateable closure slice only
