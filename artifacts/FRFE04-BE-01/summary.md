# FRFE04-BE-01 Evidence

Repaired the BE-01 historical pay-list header test so it no longer assumes global PayList cardinality when BE-00 data is present.

Verification:
- `pytest -q tests/test_annuity_e2e.py -k historical_pay_list_create` passed.
- `pytest -q tests/test_annuity_e2e.py -k 'pay_list_from_fee_items or historical_pay_list_create'` passed.
- Ruff allowlist checks passed on `app/modules/annuity/api.py`, `app/modules/annuity/service.py`, and `tests/test_annuity_e2e.py`.

Scope:
- Targeted the created pay list by `id`, `pay_list_no`, and `client_id`.
- Verified audit attribution and zero `GovPayment` rows for the created pay list.
- Preserved non-closure boundary: BE-00 behavior and production service code were not changed.
